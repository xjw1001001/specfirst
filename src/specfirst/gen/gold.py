"""Gold from decisions (PLAN.md section 6.4, stage S5): specs, ADaM, results, grid, graph.

`build(decisions, inputs)` of PLAN.md section 7, for a generated study:

    decision records
      -> compile          specfirst.compile: yamaa specs, one ARS file, layout files
      -> run              yamaa through the thin runner of the machine: ADaM
      -> list the groups  a treatment grouping of the house standard is
                          data-driven; the groups of a grouping on ADSL
                          are listed from the ADaM data, in the order the
                          layout asks for
      -> results          both engines of the machine: the ARD
      -> grid             specfirst.gen.display: the compiled layout and the ARD
      -> graph            the trace of the machine, and the `decides` edges

No model is involved. The same code builds the gold of a kit and any other
decision vector on the data of a kit (`Workbench`), which is what the
mutation of property P4 and a scorer need.

A kit of the slice builds the datasets its outputs read: ADSL and ADAE
(`SLICE_DATASETS`). The house standard also has ADVS; no output of the slice
reads it.

Why the groups are listed. The engines of the machine give a data-driven
grouping one group per value that occurs on the records of an analysis (rule
I9 of standard/methods/README.md). An arm in which no subject has a serious
event then has no result for the serious events, not a count of zero, and a
cell that prints 0 would have no ARD row behind it. A grouping with listed
groups gives every group a result (rule I8). So before the engines run, a
data-driven grouping on ADSL, which subdivides the subject population, is
replaced by the list of the values its variable has in the analysis set.
The order of the list is the column order the layout asks for
(tfl.columns.arms), which needs what no decision carries: the arms of the
protocol with their doses (`arms_of`, from the design).

A data-driven grouping on another dataset subdivides its records: the
organ class and the preferred term of ADAE. It stays data-driven, as in
CDISC's example "Common Safety Displays". The engines then give the
combinations of its values that occur on the records of an analysis (rule
I9), each with every listed group (rule I10): arms x the pairs of organ
class and term that occur. Listed, rule I10 would cross every organ class
with every term (issue #27, docs/decisions/ADR-011.md).
"""

from __future__ import annotations

import copy
import dataclasses
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from specfirst.compile import catalog as catalogs
from specfirst.compile import compiler
from specfirst.compile import house as houses
from specfirst.gen import design as designs
from specfirst.gen import display, sdtm
from specfirst.machine import ard, ars, graph, grid, render, rengine, results, runner
from specfirst.machine import registry as registries
from specfirst.machine.canonical import (
    content_hash,
    sha256_file,
    write_json,
    write_jsonl,
    write_parquet,
)
from specfirst.machine.lineage import column_dependencies

SUBJECT_KEY = "USUBJID"
# The subject-level analysis dataset of ADaM: one record per subject. A grouping on it
# subdivides the subject population, and only such a grouping has its groups listed.
SUBJECT_DATASET = "ADSL"
SLICE_DATASETS = ("ADSL", "ADAE")
# Where the parts of a kit are, relative to its folder.
HOUSE = "inputs/house"
SPEC = "gold/spec"
PROJECT = f"{SPEC}/adam/project.yaml"
ARS_FILE = f"{SPEC}/ars/reporting-event.json"
DECISIONS = "gold/decisions.jsonl"
# The two datasets of a kit: where its SDTM is, and where its gold is built.
PLACES = {"visible": ("inputs/data/sdtm", "gold"), "twin": ("twin/data/sdtm", "twin/gold")}
# What a build writes, relative to the place of its gold.
RESOLVED, ADAM, ARS_OUT, ARD, GRID, PAGES, GRAPH = (
    "resolved", "data/adam", "ars", "ard", "grid", "out", "graph")
EVENT = "reporting-event"


class GoldError(RuntimeError):
    """A decision vector cannot be built on these data."""


# ---- the house and the arms ------------------------------------------------------------


def house_view(house: houses.House,
               datasets: tuple[str, ...] = SLICE_DATASETS) -> houses.House:
    """The house standard, limited to the ADaM datasets a kit builds."""
    return dataclasses.replace(
        house, adam={name: meta for name, meta in house.adam.items() if name in datasets})


def copy_house(house: houses.House, kit_dir: Path) -> list[Path]:
    """The house standard as a kit ships it (PLAN.md section 8: inputs/house/)."""
    written = []
    for path in sorted(house.directory.rglob("*")):
        if path.is_file():
            target = kit_dir / HOUSE / path.relative_to(house.directory)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
            written.append(target)
    return written


def arms_of(design: dict, values: dict[str, dict]) -> list[dict]:
    """The arms of the protocol, in its order: code, dose, and every text that can name
    the arm in a treatment column under some decision.

    The names: the description of the arm (DM.ARM and DM.ACTARM), the name
    of its treatment on an exposure record (EX.EXTRT), and the label that a
    decoding of the arm code gives it (trt.planned.source).
    """
    mapped = {pair["code"]: pair["label"]
              for pair in (values.get("trt.planned.source") or {}).get("map") or []}
    found = []
    for arm in designs.arms(design):
        names = [arm["description"], sdtm.treatment_name(design, arm["studyInterventionId"])]
        if arm["name"] in mapped:
            names.append(mapped[arm["name"]])
        found.append({"code": arm["name"], "dose": float(arm["dose"]),
                      "names": sorted(set(names))})
    return found


def order_values(values: list[str], arms: list[dict], rule: str | None) -> list[str]:
    """The values of a treatment grouping in the order of a column rule of the layout.

    A value that names several arms stands where the first of them stands;
    a value that names no arm comes last; equal places go by the value.
    """
    if rule == "protocol_order":
        ranked = list(arms)
    elif rule == "ascending_dose_placebo_first":
        ranked = sorted(arms, key=lambda arm: (arm["dose"], arm["code"]))
    elif rule is None:
        ranked = []
    else:
        raise GoldError(f"unknown column order '{rule}'")

    def place(value: str) -> tuple[int, str]:
        found = [number for number, arm in enumerate(ranked) if value in arm["names"]]
        return (found[0] if found else len(ranked), value)

    return sorted(values, key=place)


# ---- compile ---------------------------------------------------------------------------


def compile_records(catalog: catalogs.Catalog, house: houses.House, records: list[dict],
                    depth: int = 3, bind: bool = False) -> compiler.Compiled:
    """Compile decision records for a kit.

    The specs name the house standard of the kit (`inputs/house`), `depth`
    folders above `adam/`: 3 in a kit (gold/spec/adam). Raises
    `compiler.CompileError`.
    """
    up = "/".join([".."] * depth)
    options = {"sdtm_dir": f"{up}/inputs/data/sdtm", "adam_dir": "../../data/adam"}
    view = house_view(house)
    compiled = compiler.compile_decisions(catalog, view, records, f"{up}/{HOUSE}", **options)
    if bind:
        compiler.bind_tables(catalog, view, records, compiled, f"{up}/{HOUSE}", **options)
    return compiled


def project_text(compiled: compiler.Compiled) -> str:
    """The yamaa project of the compiled ADaM specs, in the order of the house."""
    lines = ["yamaa: '1.0'", "type: project", "adam:", "  specs:"]
    lines += [f"  - {name.lower()}.yaml" for name in compiled.datasets]
    return "\n".join(lines) + "\n"


def write_spec(folder: Path, compiled: compiler.Compiled) -> list[Path]:
    """Write a compile into `<folder>` (gold/spec of a kit), with its yamaa project."""
    files = dict(compiled.files)
    files["compile.json"] = compiler.canonical_json(compiled.manifest())
    files["adam/project.yaml"] = project_text(compiled)
    written = []
    for relative, text in sorted(files.items()):
        path = folder / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="ascii", newline="\n")
        written.append(path)
    return written


# ---- results ---------------------------------------------------------------------------


def engine_tables(plans: list[runner.SpecPlan], event: ars.Event) -> dict[str, ard.Table]:
    """The columns the analyses read, from the datasets a run built, in memory."""
    wanted = ars.columns(event, SUBJECT_KEY)
    built = {plan.name: plan.table for plan in plans}
    tables = {}
    for dataset, names in wanted.items():
        if dataset not in built:
            raise GoldError(f"the tables read {dataset}, which the kit does not build")
        missing = sorted(set(names) - set(built[dataset].schema.names))
        if missing:
            raise GoldError(f"dataset {dataset} has no column {', '.join(missing)}")
        tables[dataset] = ard.table_from_arrow(dataset, built[dataset].select(names))
    return tables


def resolve_groupings(data: dict, tables: dict[str, ard.Table], layouts: dict[str, dict],
                      arms: list[dict]) -> dict:
    """A copy of a reporting event whose data-driven groupings on ADSL list their groups.

    The groups of a grouping are the values of its variable, in its own
    dataset, on the records of the analysis set of the analyses that use it.
    A group has the ID `<grouping>_<n>`, n counting the values in sorted
    order, so that the ID of a result does not depend on the column order;
    its `order` is the place the layout gives its column. A data-driven
    grouping on another dataset (organ class, preferred term) is left as it
    is: its groups are the combinations that occur (rule I9; ADR-011).
    """
    data = copy.deepcopy(data)
    event = ars.index(data)
    if event.problems:
        raise GoldError("the reporting event is not usable: " + "; ".join(event.problems[:5]))
    engine = ard.Engine(event, None, None, tables, SUBJECT_KEY)
    rules = {layout["columns"]["grouping"]: layout["columns"].get("order")
             for layout in layouts.values()}
    for grouping in data.get("analysisGroupings") or []:
        if not grouping.get("dataDriven") or grouping["groupingDataset"] != SUBJECT_DATASET:
            continue
        users = [analysis for analysis in event.analyses.values()
                 if any(entry["groupingId"] == grouping["id"]
                        for entry in analysis.get("orderedGroupings") or [])]
        sets = sorted({analysis.get("analysisSetId") or "" for analysis in users})
        if len(sets) != 1:
            raise GoldError(f"grouping '{grouping['id']}' is used with the analysis sets "
                            f"{sets}; its groups can be listed for one")
        dataset = grouping["groupingDataset"]
        values = engine.group_values(dataset, grouping)
        if sets[0]:
            values = values[engine.where(dataset, event.sets[sets[0]])]
        found = sorted(set(values.tolist()) - {""})
        if not found:
            raise GoldError(f"grouping '{grouping['id']}': no record of {dataset} in the "
                            "analysis set has a value")
        ordered = order_values(found, arms, rules.get(grouping["id"]))
        grouping["dataDriven"] = False
        grouping["groups"] = [
            {"id": f"{grouping['id']}_{number}", "name": value, "level": 1,
             "order": ordered.index(value) + 1,
             "condition": {"dataset": dataset, "variable": grouping["groupingVariable"],
                           "comparator": "EQ", "value": [value]}}
            for number, value in enumerate(found, start=1)]
    return data


def python_results(root: Path, data: dict, tables: dict[str, ard.Table],
                   ) -> tuple[ars.Event, ars.Binding, list[dict]]:
    """Run the Python engine on a reporting event whose groupings list their groups."""
    event = ars.index(data)
    if event.problems:
        raise GoldError("the reporting event is not usable: " + "; ".join(event.problems[:5]))
    registry = registries.load(root)
    binding = ars.bind(event, registry, {})
    return event, binding, ard.run(event, registry, binding, tables, SUBJECT_KEY)


@dataclass
class Shown:
    """One decision vector, built on one dataset: what a comparison needs."""

    compiled: compiler.Compiled
    grids: dict[str, dict] = field(default_factory=dict)   # output ID -> grid
    rows: list[dict] = field(default_factory=list)          # the ARD of the Python engine
    event: ars.Event | None = None
    data: dict | None = None                                 # the reporting event, groups listed
    plans: list[runner.SpecPlan] = field(default_factory=list)


def show(root: Path, compiled: compiler.Compiled, plans: list[runner.SpecPlan],
         arms: list[dict]) -> Shown:
    """From built ADaM to the grids of every output of a compile (Python engine)."""
    found = Shown(compiled, plans=plans)
    if compiled.ars is None:
        return found   # the study plans no output
    unresolved = ars.index(compiled.ars)
    tables = engine_tables(plans, unresolved)
    found.data = resolve_groupings(compiled.ars, tables, compiled.layouts, arms)
    found.event, _, found.rows = python_results(root, found.data, tables)
    by_id = results.by_id(found.rows)
    for layout in compiled.layouts.values():
        made = display.build(found.event, layout, by_id)
        problems = grid.grid_problems(made, root)
        if problems:
            raise GoldError(f"the grid of {layout['output']['id']} is not valid: "
                            + "; ".join(problems[:5]))
        found.grids[layout["output"]["id"]] = made
    return found


# ---- any vector on the data of a kit ---------------------------------------------------


class Workbench:
    """Builds decision vectors on one dataset of a kit, in a scratch folder.

    The scratch folder gets a copy of the house standard and of the SDTM
    data; every distinct set of ADaM specs is written to a folder of its own
    below it and run once. Nothing is written into the kit.
    """

    DEPTH = 5   # v/<n>/gold/spec/adam is five folders below the scratch folder

    def __init__(self, root: Path, catalog: catalogs.Catalog, house: houses.House,
                 kit_dir: Path, which: str, scratch: Path):
        self.root, self.catalog, self.house = root, catalog, house
        self.scratch, self.sdtm = scratch, PLACES[which][0]
        self.runs = 0
        self._adam: dict[str, list[runner.SpecPlan]] = {}
        self._shown: dict[str, Shown] = {}
        copy_house(house, scratch)
        (scratch / self.sdtm).mkdir(parents=True, exist_ok=True)
        for path in sorted((kit_dir / self.sdtm).glob("*.parquet")):
            shutil.copyfile(path, scratch / self.sdtm / path.name)

    def compile(self, records: list[dict]) -> compiler.Compiled:
        return compile_records(self.catalog, self.house, records, depth=self.DEPTH)

    def adam(self, compiled: compiler.Compiled) -> list[runner.SpecPlan]:
        """The ADaM of a compile; a set of specs that was run before is not run again."""
        files = {path: text for path, text in sorted(compiled.files.items())
                 if path.startswith("adam/")}
        key = content_hash(files)
        if key not in self._adam:
            self.runs += 1
            folder = self.scratch / "v" / str(self.runs) / SPEC
            for relative, text in files.items():
                path = folder / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="ascii", newline="\n")
            project = folder / "adam" / "project.yaml"
            project.write_text(project_text(compiled), encoding="ascii", newline="\n")
            try:
                self._adam[key] = runner.run_project(
                    self.scratch, project.relative_to(self.scratch).as_posix(), self.sdtm)
            except runner.RunnerError as error:
                raise GoldError(str(error)) from error
        return self._adam[key]

    def show(self, records: list[dict], arms: list[dict]) -> Shown:
        """Compile and build a vector as far as its grids. Raises `GoldError`."""
        try:
            compiled = self.compile(records)
        except compiler.CompileError as error:
            raise GoldError("cannot compile: " + "; ".join(error.problems)) from error
        key = content_hash({"files": compiled.files, "arms": arms})
        if key not in self._shown:
            plans = self.adam(compiled) if compiled.datasets else []
            try:
                self._shown[key] = show(self.root, compiled, plans, arms)
            except (ars.ArsError, ard.EngineError, display.DisplayError,
                    results.ResultsError) as error:
                raise GoldError(str(error)) from error
        return self._shown[key]


# ---- the gold of a kit -----------------------------------------------------------------


@dataclass(frozen=True)
class _Document:
    id: str
    file: str
    cited_as: tuple[str, ...] = ()


@dataclass(frozen=True)
class _KitView:
    """What the graph builder of the machine reads of a kit."""

    sdtm: str
    documents: tuple[_Document, ...]
    claims: str | None = None
    files: tuple = ()
    trace_gaps: dict = field(default_factory=dict)

    def document(self, cited_as: str) -> _Document | None:
        return None


def upstream(kit_dir: Path, plans: list[runner.SpecPlan], event: ars.Event,
             analyses: set[str]) -> set[str]:
    """Every ADaM column, working columns included, that the named analyses read or
    that a column they read is derived from: `adam:<dataset>.<column>`."""
    import pyarrow.parquet as pq

    produced = {plan.name: plan.columns for plan in plans}
    reads_of: dict[str, dict[str, list[str]]] = {}
    alias_of: dict[str, dict[str, tuple[str, str]]] = {}
    for plan in plans:
        columns_of = {}
        alias_of[plan.name] = {}
        for source in plan.inputs:
            alias_of[plan.name][source.alias] = (source.layer, source.dataset)
            columns_of[source.alias] = set(produced[source.dataset]) if source.layer == "adam" \
                else set(pq.read_schema(kit_dir / source.file).names)
        reads_of[plan.name] = column_dependencies(plan.specification, columns_of).edges()
    start = {(dataset, f"spec.{variable}") for name in analyses
             for _, dataset, variable in ars.reads(event, name, SUBJECT_KEY)
             if dataset in reads_of}
    seen, stack = set(start), list(start)
    while stack:
        dataset, element = stack.pop()
        for ref in reads_of[dataset].get(element, []):
            head, _, tail = ref.partition(".")
            layer, source = alias_of[dataset].get(head, ("", ""))
            if layer == "adam":
                following = (source, f"spec.{tail}")
            elif layer == "sdtm":
                continue
            else:
                following = (dataset, ref)
            if following not in seen:
                seen.add(following)
                stack.append(following)
    return {f"adam:{dataset}.{element[len('spec.'):]}" for dataset, element in seen
            if element.startswith("spec.")}


def decision_id(record: dict, catalog: catalogs.Catalog) -> str:
    """The ID of the graph node of a decision; a table family decision names its unit."""
    entry = catalog.entries.get(record["id"])
    if entry is not None and entry.per_family:
        return f"decision:{record['id']}@{record['unit']}"
    return f"decision:{record['id']}"


def reach(kit_dir: Path, shown: Shown, catalog: catalogs.Catalog,
          records: list[dict]) -> dict[str, dict]:
    """For every decision of a vector: which of the elements it sets the outputs read.

    A decision sets (binds) columns of ADaM specs, elements of the ARS file
    and parts of layout files (compile.json; the binds of ARS elements and
    layout parts are proven by mutation of the compile). The outputs read an
    element when it is on the way of a cell: an analysis a cell shows, its
    analysis set, data subset, groupings and method, the ADaM columns these
    name and every column those are derived from, and every part of the
    layout of a built output. A decision with no such element cannot change
    a cell: the outputs of this study do not read it.
    """
    event = shown.event
    behind: set[str] = set()
    for made in shown.grids.values():
        for row in made["rows"]:
            for cell in row["cells"]:
                for key in cell["ard"]:
                    analysis = event.analyses[key[len("ard:"):].split("/")[0]]
                    operation = next(r["operation_id"] for r in shown.rows if r["id"] == key)
                    behind |= {analysis["id"],
                               *graph.referenced_analyses(event, analysis, operation)}
    elements = set()
    for name in behind:
        analysis = event.analyses[name]
        elements |= {name, analysis.get("analysisSetId"), analysis.get("dataSubsetId"),
                     analysis.get("methodId")}
        elements |= {entry["groupingId"] for entry in analysis.get("orderedGroupings") or []}
    read_ars = {f"ars:{name}" for name in elements if name}
    read_adam = upstream(kit_dir, shown.plans, event, behind) if event is not None else set()
    outputs = {layout["output"]["id"] for layout in shown.compiled.layouts.values()}
    built = {unit for unit, layout in shown.compiled.layouts.items()
             if layout["output"]["id"] in shown.grids and layout["output"]["id"] in outputs}
    found = {}
    for record in records:
        key = (record["id"], record["unit"])
        binds = shown.compiled.binds.get(key, [])
        layout = [part for part in shown.compiled.layout_binds.get(key, [])
                  if part[len("layout:"):].split("/")[0] in built]
        on_the_way = sorted((set(binds) & (read_ars | read_adam)) | set(layout))
        found[decision_id(record, catalog)] = {
            "id": record["id"], "unit": record["unit"], "binds": binds,
            "layout": shown.compiled.layout_binds.get(key, []), "read": on_the_way}
    return found


def add_decisions(trace: graph.Graph, records: list[dict], reached: dict[str, dict],
                  catalog: catalogs.Catalog) -> None:
    """Add the decisions and their `decides` edges to a graph (PLAN.md section 4.2).

    An edge goes to every element a decision sets that has a node: an ADaM
    output column, an analysis a cell shows. A working column, a grouping or
    a layout part has no node in graph schema version 0; coverage.json holds
    the full list of what each decision sets and which of it the outputs
    read.
    """
    nodes = {node["id"]: node for node in trace.nodes}
    edges = {(edge["type"], edge["from"], edge["to"]): edge for edge in trace.edges}
    for line, record in enumerate(records, start=1):
        name = decision_id(record, catalog)
        source = {"file": DECISIONS, "line": line}
        nodes[name] = {"id": name, "layer": "decision", "kind": "decision",
                       "label": str(record.get("statement") or record["id"]),
                       "hash": content_hash({key: record.get(key)
                                             for key in ("id", "unit", "value")}),
                       "source": source}
        for bind in reached[name]["binds"]:
            if bind in nodes:
                edges[("decides", name, bind)] = {
                    "type": "decides", "from": name, "to": bind, "proof": "static",
                    "origin": "built", "source": source}
    trace.nodes = [nodes[key] for key in sorted(nodes)]
    trace.edges = [edges[key] for key in sorted(edges)]
    trace.coverage = {**trace.coverage, "decisions": reached}


def build(root: Path, catalog: catalogs.Catalog, kit_dir: Path, which: str,
          compiled: compiler.Compiled, records: list[dict], arms: list[dict],
          with_r: bool = True) -> tuple[Shown, list[Path], dict]:
    """Build the gold of one dataset of a kit and write it. The kit holds its SDTM, its
    house standard and its compiled specs already.

    Returns what was built, the files written, and a record for the
    manifest (engines, agreement of the two result engines).
    """
    sdtm_dir, place = PLACES[which]
    into = kit_dir / place
    try:
        plans = runner.run_project(kit_dir, PROJECT, sdtm_dir)
    except runner.RunnerError as error:
        raise GoldError(str(error)) from error
    written: list[Path] = []
    for plan in plans:
        stem = plan.name.lower()
        if which == "visible":   # the resolution reads no data: it is the same for the twin
            write_json(into / RESOLVED / f"{stem}.json", plan.record)
            written.append(into / RESOLVED / f"{stem}.json")
        write_parquet(into / ADAM / f"{stem}.parquet", plan.table)
        written.append(into / ADAM / f"{stem}.parquet")
    record: dict = {"datasets": {plan.name: plan.table.num_rows for plan in plans}}
    try:
        shown = show(root, compiled, plans, arms)
    except (ars.ArsError, ard.EngineError, display.DisplayError,
            results.ResultsError) as error:
        raise GoldError(str(error)) from error
    if shown.event is None:
        raise GoldError("the decisions plan no output")
    event_file = into / ARS_OUT / f"{EVENT}.json"
    write_json(event_file, results.with_results(shown.event, shown.rows))
    results.write_ard(into / ARD / f"{EVENT}.jsonl", shown.rows, root)
    written += [event_file, into / ARD / f"{EVENT}.jsonl"]
    record["results"] = len(shown.rows)
    if with_r:
        registry = registries.load(root)
        binding = ars.bind(shown.event, registry, {})
        tables = engine_tables(plans, shown.event)
        other, meta, _ = rengine.run(root, kit_dir / "work" / which, event_file,
                                     registries.json_path(root), binding, tables, SUBJECT_KEY)
        problems = rengine.data_problems(meta, tables)
        if problems:
            raise GoldError("the R engine: " + "; ".join(problems))
        results.write_ard(into / ARD / f"{EVENT}.r.jsonl", other, root)
        written.append(into / ARD / f"{EVENT}.r.jsonl")
        lines, disagreements = results.agreement(results.by_id(shown.rows),
                                                 results.by_id(other))
        record["r"] = meta.get("r")
        record["engines"] = {"agree": not disagreements, "lines": lines,
                             "disagreements": disagreements[:20]}
        shutil.rmtree(kit_dir / "work" / which, ignore_errors=True)
    displays = []
    for output, made in sorted(shown.grids.items()):
        layout = next(layout for layout in compiled.layouts.values()
                      if layout["output"]["id"] == output)
        shell = display.build(shown.event, layout, None)
        for kind, value in (("", made), (".shell", shell)):
            path = into / GRID / f"{output}{kind}.json"
            write_json(path, value)
            page = into / PAGES / f"{output}{kind}.html"
            page.parent.mkdir(parents=True, exist_ok=True)
            page.write_bytes(render.html(value).encode("utf-8"))
            written += [path, page]
        displays.append(graph.Display(
            grid=made, grid_file=f"{place}/{GRID}/{output}.json", event=shown.event,
            ars_file=f"{place}/{ARS_OUT}/{EVENT}.json", ard_file=f"{place}/{ARD}/{EVENT}.jsonl",
            rows=shown.rows, subject_key=SUBJECT_KEY))
    view = _KitView(sdtm=sdtm_dir, documents=(_Document("define-sdtm",
                                                        f"{sdtm_dir}/define.xml"),))
    try:
        trace = graph.build_graph(view, kit_dir, plans)
    except graph.GraphError as error:
        raise GoldError(str(error)) from error
    graph.add_displays(trace, kit_dir, displays)
    reached = reach(kit_dir, shown, catalog, records)
    add_decisions(trace, records, reached, catalog)
    written += graph.write_graph(into / GRAPH, trace)
    record["reach"] = reached
    return shown, written, record


def file_hashes(kit_dir: Path, paths: list[Path]) -> dict[str, str]:
    return {path.relative_to(kit_dir).as_posix(): sha256_file(path) for path in sorted(paths)}


def write_decisions(kit_dir: Path, records: list[dict]) -> Path:
    path = kit_dir / DECISIONS
    write_jsonl(path, records)
    return path
