"""Build a decision vector on a dataset: what the scorer compares (PLAN.md section 9).

"A run submits decision records. The scorer compares them with gold, then
builds them on the visible data and on the twin and compares the results."
This module is that build: decisions in, compiled specs, ADaM datasets,
results, grids and the trace out, as one `Build`. Gold is built the same
way from the gold decisions, so two builds differ only where the decisions
do (rule R4).

    compile   specfirst.compile.compiler: yamaa specs, an ARS file, layouts
    ADaM      the yamaa runner of the machine, in memory, in a new folder
              under the system's temporary folder (yamaa refuses to save on
              a Windows drive under WSL, and nothing is saved here)
    groups    a treatment grouping of the house standard is data-driven;
              its groups are listed from the ADaM data, in the order the
              layout asks for (specfirst.gen.gold.resolve_groupings)
    results   the Python result engine: the gold ARD is its ARD
    grids     specfirst.gen.display, from the compiled layout and the ARD
    trace     derives_from from the resolved specs (specfirst.machine.graph);
              for every cell the results and analyses behind it

From the groups on, these are the functions that build the gold of a
generated kit (docs/decisions/ADR-007.md): on the data of a kit the gold
decisions give the files of the kit, byte for byte in the grid
(`specfirst.score.kit.gold_problems` holds that for every kit it scores).

The order of the treatment columns needs the arms of the protocol, which no
decision carries (ADR-007, decision 2). A build is given them as the
generator gives them: code, dose, and every text that can name the arm in
a treatment column, in the order of the protocol.

Two stages (ADR-005, decision 2). The chain builds ADaM from SDTM. Stage T
is given ADaM datasets and builds the tables only; the ADaM specs are
compiled and not run.

Scope. A slice scores the decisions of some units. `vector` puts a
candidate's records of those units on the gold records of every other
unit; a decision of the scope that the candidate leaves out takes the house
default, and one without a default stays out (ADR-005, decision 3).

A build that fails keeps the rule that failed (section 9.2, validity). A
planted defect is a hook: a function that changes what one step hands to
the next (`Hooks`).
"""

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from specfirst import kit as kits
from specfirst.compile import catalog as catalogs
from specfirst.compile import compiler
from specfirst.compile import house as houses
from specfirst.gen import display
from specfirst.gen import gold as kitgold
from specfirst.machine import ard, ars, graph, grid, lineage, results, runner
from specfirst.machine import registry as registries

Key = tuple[str, str]
Arms = list[dict]  # of the protocol, in its order: code, dose, names (specfirst.gen.gold.arms_of)
SUBJECT_KEY = "USUBJID"
# Where a build lays out its files, relative to its folder.
SPEC, HOUSE, SDTM = "spec", "house", "sdtm"
PROJECT = f"{SPEC}/adam/project.yaml"


@dataclass(frozen=True)
class Data:
    """One dataset of a study, as tables: SDTM for the chain, or ADaM as given (stage T)."""

    name: str  # for example `hand01/visible`: part of what identifies a build
    sdtm: dict | None = None  # file stem (dm, ae, ...) -> Arrow table
    adam: dict | None = None  # dataset (ADSL, ADAE, ...) -> Arrow table


@dataclass(frozen=True)
class Hooks:
    """A planted defect: changes to what one step of a build hands to the next.

    compiled(Compiled)   change the ARS file, a layout or a spec file
    adam(tables)         change the ADaM tables; returns the tables
    ard(rows)            change the ARD rows; returns the rows
    """

    name: str
    compiled: Callable | None = None
    adam: Callable | None = None
    ard: Callable | None = None


@dataclass(frozen=True)
class CellPath:
    """What stands behind one cell: the results it shows, and the analyses they are
    computed from (the numerator's and the denominator's)."""

    ard: tuple[str, ...]
    analyses: tuple[str, ...]


def cell_paths(event: ars.Event, made: dict, rows: dict[str, dict]) -> dict[str, CellPath]:
    """For every cell of a grid: its ARD rows, and the analyses behind them."""
    found = {}
    for row in made["rows"]:
        for cell in row["cells"]:
            analyses: list[str] = []
            for key in cell["ard"]:
                analysis = event.analyses[rows[key]["analysis_id"]]
                analyses += [analysis["id"], *graph.referenced_analyses(
                    event, analysis, rows[key]["operation_id"])]
            found[cell["id"]] = CellPath(tuple(cell["ard"]), tuple(dict.fromkeys(analyses)))
    return found


@dataclass
class Build:
    """What one decision vector builds on one dataset."""

    data: str
    records: list[dict]  # id, unit, value: the vector that was compiled
    failure: str | None = None  # the rule that stopped the build, if any
    files: dict[str, str] = field(default_factory=dict)  # the compiled files
    ars: dict | None = None  # the compiled ARS file: its groupings as the decisions wrote them
    layouts: dict[str, dict] = field(default_factory=dict)  # unit -> compiled layout
    adam: dict = field(default_factory=dict)  # dataset -> Arrow table
    ard: dict[str, dict] = field(default_factory=dict)  # ARD rows by ID
    # (grouping, group) -> the name and the condition of the group in the reporting
    # event that was run, where the groups of a data-driven grouping are listed.
    groups: dict[tuple[str, str], dict] = field(default_factory=dict)
    grids: dict[str, dict] = field(default_factory=dict)  # output ID -> grid
    not_produced: dict[str, str] = field(default_factory=dict)  # output ID -> why
    paths: dict[str, CellPath] = field(default_factory=dict)  # cell ID -> what is behind it
    edges: list[dict] = field(default_factory=list)  # derives_from, between ADaM and SDTM columns
    through: dict[str, list[str]] = field(default_factory=dict)  # ADaM column -> working columns
    outputs: dict[str, str] = field(default_factory=dict)  # output ID -> unit

    @property
    def ok(self) -> bool:
        return self.failure is None

    def value(self, key: Key) -> object:
        return next((r["value"] for r in self.records if (r["id"], r["unit"]) == key), None)


def vector(catalog: catalogs.Catalog, house: houses.House, gold: list[dict],
           candidate: list[dict], units: tuple[str, ...]) -> list[dict]:
    """The decision vector that stands for a candidate, in catalog order.

    Inside the units of the scope: the candidate's value, else the house
    default, else nothing. Outside: the gold value. A record without a
    value (asked, in conflict, not applicable) gives no value. A decision
    that the study does not make (gold has no record of it: the catalog
    entry does not apply to its design) takes no default either; only a
    record of the candidate puts it into the vector.
    """
    given = {(r.get("id"), r.get("unit")): r for r in reversed(candidate)}
    known = {(r.get("id"), r.get("unit")): r for r in gold}
    found = []
    for key in catalog.keys():
        if key[1] in units:
            if key in given:
                value = given[key].get("value")
            elif key in known:
                value = houses.default_value(catalog, house, *key)
            else:
                value = None
        else:
            value = known[key].get("value") if key in known else None
        if value is not None:
            found.append({"id": key[0], "unit": key[1], "value": value})
    return found


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode()).hexdigest()


def element_changes(one: compiler.Compiled | None, two: compiler.Compiled | None) -> set[str]:
    """The spec elements that two compiles do not have in common with the same content.

    `ars:<id>` for an element of the ARS file; `layout:<unit>/<part>` for a
    part of a layout; `adam:<DATASET>.<name>` for a column, and
    `adam:<DATASET>.@<id>` for a lookup or a row template, that a fragment
    writes. This is the `decides` edge of section 4.2 for one pair of
    values: proven by compiling both.
    """
    found: set[str] = set()
    empty = compiler.Compiled()
    one, two = one or empty, two or empty
    for name in compiler.ARS_LISTS:
        ours = {e["id"]: e for e in (one.ars or {}).get(name, [])}
        theirs = {e["id"]: e for e in (two.ars or {}).get(name, [])}
        found |= {f"ars:{key}" for key in set(ours) | set(theirs)
                  if ours.get(key) != theirs.get(key)}
    for unit in set(one.layouts) | set(two.layouts):
        ours, theirs = one.layouts.get(unit) or {}, two.layouts.get(unit) or {}
        found |= {f"layout:{unit}/{part}" for part in set(ours) | set(theirs)
                  if ours.get(part, _ABSENT) != theirs.get(part, _ABSENT)}
    for path in set(one.files) | set(two.files):
        parts = path.split("/")
        if parts[:2] != ["adam", "fragments"] or one.files.get(path) == two.files.get(path):
            continue
        dataset = parts[2].upper()
        ours = yaml.safe_load(one.files[path]) if path in one.files else {}
        theirs = yaml.safe_load(two.files[path]) if path in two.files else {}
        for part, name_key, mark in (("columns", "name", ""), ("intermediates", "id", "@"),
                                     ("rows", "id", "@")):
            a = {item[name_key]: item for item in ours.get(part) or []}
            b = {item[name_key]: item for item in theirs.get(part) or []}
            found |= {f"adam:{dataset}.{mark}{key}" for key in set(a) | set(b)
                      if a.get(key) != b.get(key)}
    return found


_ABSENT = object()


def passes_through(plans: list, tables: dict) -> dict[str, list[str]]:
    """For every ADaM output column: the working columns, lookups and row templates
    of its specification that its rule passes through, as fragments name them.

    A decision's fragment may write a working column (`_TEEND`) that an
    output column reads; the column of the dataset is then decided by that
    decision too. Another output column on the way ends the walk: it is a
    node of the graph with an edge of its own.
    """
    produced = {plan.name: set(plan.columns) for plan in plans}
    found: dict[str, list[str]] = {}
    for plan in plans:
        columns_of: dict[str, set[str]] = {}
        for source in plan.inputs:
            if source.layer == "adam":
                columns_of[source.alias] = produced[source.dataset]
            else:
                columns_of[source.alias] = set(tables[source.dataset.lower()].column_names)
        reads = lineage.column_dependencies(plan.specification, columns_of).edges()
        outputs = set(plan.columns)
        for name in plan.columns:
            seen, stack, passed = {f"spec.{name}"}, [f"spec.{name}"], set()
            while stack:
                for ref in reads.get(stack.pop(), []):
                    head, _, tail = ref.partition(".")
                    if ref in seen or head in columns_of:
                        continue
                    if head == "spec" and tail in outputs:
                        continue
                    seen.add(ref)
                    stack.append(ref)
                    if head == "spec":
                        passed.add(tail)
                    elif head in ("intermediate", "row"):
                        passed.add("@" + tail)
            found[graph.adam_id(plan.name, name)] = sorted(passed)
    return found


class Machine:
    """The standard of a checkout and the builds made with it, each made once.

    `datasets` limits a build to these ADaM datasets of the house standard.
    A kit of the slice builds ADSL and ADAE (ADR-007, decision 8): its
    decisions do not hold those of ADVS, which the full house would ask for.
    """

    def __init__(self, root: Path, datasets: tuple[str, ...] | None = None):
        self.root = root
        self.catalog = catalogs.load(catalogs.default_dir(root))
        self.house = houses.load(houses.default_dir(root))
        self.built = self.house if datasets is None else kitgold.house_view(self.house, datasets)
        self.registry = registries.load(root)
        self._compiled: dict[str, compiler.Compiled | str] = {}
        self._builds: dict[str, Build] = {}
        self.builds_made = 0

    # ---- compile ------------------------------------------------------------------

    def compile(self, records: list[dict]) -> compiler.Compiled | str:
        """The compiled files of a decision vector, or the reason it does not compile."""
        key = _digest(records)
        if key not in self._compiled:
            try:
                self._compiled[key] = compiler.compile_decisions(
                    self.catalog, self.built, records, f"../../{HOUSE}",
                    sdtm_dir=f"../../{SDTM}", adam_dir="../../adam")
            except compiler.CompileError as error:
                self._compiled[key] = "compile: " + "; ".join(error.problems)
        return self._compiled[key]

    def changes(self, records: list[dict], key: Key, value: object) -> set[str]:
        """The spec elements that change when one decision of a vector takes another value."""
        other = [r for r in records if (r["id"], r["unit"]) != key]
        if value is not None:
            other.append({"id": key[0], "unit": key[1], "value": value})
        one, two = self.compile(records), self.compile(other)
        return element_changes(None if isinstance(one, str) else one,
                               None if isinstance(two, str) else two)

    # ---- build --------------------------------------------------------------------

    def build(self, records: list[dict], data: Data, arms: Arms,
              hooks: Hooks | None = None) -> Build:
        """Build a decision vector on a dataset. The same vector, data and hooks are
        built once."""
        key = _digest([records, data.name, hooks.name if hooks else None])
        if key not in self._builds:
            self.builds_made += 1
            self._builds[key] = self._build(records, data, arms, hooks)
        return self._builds[key]

    def _build(self, records: list[dict], data: Data, arms: Arms,
               hooks: Hooks | None) -> Build:
        built = Build(data.name, [dict(r) for r in records])
        compiled = self.compile(records)
        if isinstance(compiled, str):
            built.failure = compiled
            return built
        if hooks and hooks.compiled:
            compiled = _copy(compiled)
            hooks.compiled(compiled)
        built.files, built.ars, built.layouts = dict(compiled.files), compiled.ars, dict(
            compiled.layouts)
        try:
            if data.adam is not None:
                built.adam = dict(data.adam)
            else:
                self._adam(built, compiled, data)
            if hooks and hooks.adam:
                built.adam = hooks.adam(dict(built.adam))
            self._tables(built, arms, hooks)
        except (runner.RunnerError, graph.GraphError) as error:
            built.failure = f"ADaM: {error}"
        except (ars.ArsError, ard.EngineError, results.ResultsError,
                registries.RegistryError, kitgold.GoldError) as error:
            built.failure = f"results: {error}"
        return built

    def _adam(self, built: Build, compiled: compiler.Compiled, data: Data) -> None:
        import pyarrow.parquet as pq

        if not compiled.datasets:
            return
        work = Path(tempfile.mkdtemp(prefix="specfirst-score-"))
        try:
            shutil.copytree(self.house.directory / "adam", work / HOUSE / "adam")
            for stem, table in (data.sdtm or {}).items():
                (work / SDTM).mkdir(parents=True, exist_ok=True)
                pq.write_table(table, work / SDTM / f"{stem}.parquet")
            for relative, text in built.files.items():
                path = work / SPEC / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="ascii", newline="\n")
            project = {"yamaa": compiler.YAMAA_VERSION, "type": "project",
                       "adam": {"specs": [f"{name.lower()}.yaml" for name in compiled.datasets]}}
            (work / PROJECT).write_text(compiler.canonical_yaml(project), encoding="ascii",
                                        newline="\n")
            plans = runner.run_project(work, PROJECT, SDTM)
            kit = kits.Kit(id="score", title="a build of the scorer", tier="A", engines={},
                           sources={}, project=PROJECT, sdtm=SDTM, reference="", claims=None,
                           documents=(), files=(), trace_gaps={})
            trace = graph.build_graph(kit, work, plans)
            built.adam = {plan.name: plan.table for plan in plans}
            built.edges = [edge for edge in trace.edges if edge["type"] == "derives_from"]
            built.through = passes_through(plans, data.sdtm or {})
        finally:
            shutil.rmtree(work, ignore_errors=True)

    def _tables(self, built: Build, arms: Arms, hooks: Hooks | None) -> None:
        if built.ars is None:
            return  # no output is included
        event = ars.index(built.ars)
        if event.problems:
            raise ars.ArsError("; ".join(event.problems[:5]))
        tables = {}
        for dataset, names in ars.columns(event, SUBJECT_KEY).items():
            table = built.adam.get(dataset)
            if table is None:
                raise ard.EngineError(f"the tables read {dataset}, which was not built")
            missing = sorted(set(names) - set(table.column_names))
            if missing:
                raise ard.EngineError(f"dataset {dataset} has no column {', '.join(missing)}")
            tables[dataset] = ard.table_from_arrow(dataset, table.select(names))
        # From here on, as the gold of a generated kit is built (specfirst.gen.gold.show).
        listed = kitgold.resolve_groupings(built.ars, tables, built.layouts, arms)
        event, _, rows = kitgold.python_results(self.root, listed, tables)
        built.groups = {
            (grouping["id"], group["id"]): {"name": group.get("name"),
                                            "condition": group.get("condition")}
            for grouping in listed.get("analysisGroupings") or []
            for group in grouping.get("groups") or []}
        if hooks and hooks.ard:
            rows = hooks.ard([dict(row) for row in rows])
        built.ard = results.by_id(rows)
        for unit, layout in sorted(built.layouts.items()):
            output = str((layout.get("output") or {}).get("id"))
            built.outputs[output] = unit
            try:
                made = display.build(event, layout, built.ard)
            except display.DisplayError as error:
                built.not_produced[output] = f"display: {error}"
                continue
            problems = grid.grid_problems(made, self.root)
            if problems:
                built.not_produced[output] = "grid: " + "; ".join(problems[:3])
                continue
            built.grids[output] = made
            built.paths.update(cell_paths(event, made, built.ard))


def _copy(compiled: compiler.Compiled) -> compiler.Compiled:
    """A compile that a hook may change without changing the one that is kept."""
    return compiler.Compiled(
        files=dict(compiled.files), binds=dict(compiled.binds),
        layout_binds=dict(compiled.layout_binds), datasets=list(compiled.datasets),
        adam_columns=dict(compiled.adam_columns), families=list(compiled.families),
        ars=json.loads(json.dumps(compiled.ars)), layouts=json.loads(json.dumps(compiled.layouts)))
