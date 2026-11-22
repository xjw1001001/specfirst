"""What the review page shows, read from a build of a kit (issue #31, ADR-022).

`load` reads a built kit (build/kits/<kit>: the grids, the ARD, the graph,
the resolved specifications, the ARS files), the kit's decision records,
the catalog and house the kit names, the recomputation of issue #29
(build/recompute/<kit>) and, if given, a P4 matrix (`specfirst gen
separate`). It computes nothing of the study: every number on the page is a
value of the ARD, as the grid shows it.

What a panel says, and where it comes from:

- the analysis in sentences: the ARS analysis as `specfirst.recompute.reading`
  reads it for the scripts of issue #29 (its set, subset, groupings, method,
  operations, and each option with where its value comes from);
- the decisions: the kit's records that bind the analysis or one of its
  elements (rule: `binds`), each with its statement, value, status, class,
  citations (a quote is checked against the text of its document by script),
  the alternatives of its catalog entry it does not take, the mark `house
  default` (its value is the house's default for its unit) or `study
  customized`, and its P4 class or `not tested`;
- the ADaM columns: the `reads` edges of the analysis with their roles
  (coverage.json), each column with the records that bind it, its label, the
  study spec's own comment (the Define-XML comment of the resolved
  specification) labelled as such, its rule with the file and line of the
  graph node, its candidate citations (Pilot 7's claims) and the columns it
  derives from, down to SDTM;
- the recomputation: the line of build/recompute/<kit>/run/report.json and
  the text of the script.
"""

from __future__ import annotations

import json
import re
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path

from specfirst import kit as kits
from specfirst.machine import ars
from specfirst.machine import decisions as decision_records
from specfirst.machine.canonical import read_jsonl
from specfirst.paths import build_dir
from specfirst.recompute import reading
from specfirst.recompute.common import where_words

# The folders of a build (specfirst.machine.build; a unit test holds them equal).
GRAPH, GRID, ARD, RESOLVED = "gold/graph", "gold/grid", "gold/ard", "gold/resolved"
REGISTRY = "standard/methods/registry.json"
# The kinds of an edge or a claim as the page draws them, never merged (PLAN.md 4.2).
EXECUTED, STATIC, JUDGED = "executed", "static", "judged"
UNSEPARATED, NOT_TESTED = "unseparated", "not tested"
HOUSE_DEFAULT, CUSTOMIZED = "house default", "study customized"


class ReviewError(RuntimeError):
    """The review cannot be made: the build or one of its files is missing."""


@dataclass(frozen=True)
class Citation:
    """A citation as the page draws it: always judged, approved or awaiting approval."""

    target: str  # the span: doc:<document>#<anchor>
    text: str  # the quote, or the label of a page reference
    verified: bool  # a script found the text at the document
    approved_by: str | None
    origin: str  # imported (another project's), built, or record (a decision record)
    checkable: bool = True  # False: the source is no document of the kit (the owner's answers)


@dataclass
class ColumnView:
    id: str  # adam:<DATASET>.<COLUMN> or sdtm:<DOMAIN>.<COLUMN>
    label: str = ""
    comment: str = ""  # the study spec's own comment (Define-XML)
    rule: str = ""  # the rule of the resolved specification, as JSON
    source: str = ""  # file:line of the graph node
    decisions: list[str] = field(default_factory=list)  # record keys
    cites: list[Citation] = field(default_factory=list)
    derives: list[str] = field(default_factory=list)  # the columns it derives from
    sdtm: list[str] = field(default_factory=list)  # every SDTM column it reaches
    terminal: str = ""  # coverage.json: sdtm, literal or gap; "" for an SDTM column


@dataclass
class DecisionView:
    key: str  # <id> (<unit>)
    id: str
    unit: str
    statement: str
    value: str  # canonical JSON
    status: str
    klass: str
    mark: str  # HOUSE_DEFAULT or CUSTOMIZED
    citations: list[Citation]
    alternatives: list[str]  # the statements of the alternatives it does not take
    binds: list[str]
    p4: str  # the class of the P4 matrix, or NOT_TESTED
    source: str  # the decisions file
    house_sources: list[str] = field(default_factory=list)  # of the house's default, if taken


@dataclass
class AnalysisView:
    key: str  # <event>/<analysis>
    event: str
    id: str
    name: str
    sentences: list[str]
    options: list[str]
    elements: list[str]  # ars:<id> of the analysis, its set, subset, groupings, method
    decisions: list[str] = field(default_factory=list)
    cites: list[Citation] = field(default_factory=list)
    columns: list[tuple[str, list[str]]] = field(default_factory=list)  # (column, roles)
    recompute: dict | None = None
    script: tuple[str, str] | None = None  # (bundle path, text)


@dataclass
class CellView:
    id: str
    output: str
    row: str
    column: str
    text: str
    results: list[tuple[str, str, str]]  # (ARD row ID, operation, raw value)
    analysis: str  # the key of the analysis of its first ARD row
    analyses: list[str]  # every analysis it is computed from (with denominators)


@dataclass
class OutputView:
    id: str
    event: str
    grid: dict
    analyses: list[str]  # keys, in the order of the grid


@dataclass
class SheetLine:
    kind: str  # record, catalog entry, kit binding, layout
    key: str
    unit: str
    text: str
    status: str
    klass: str
    mark: str
    citations: list[Citation]
    p4: str
    cells: int


@dataclass
class Review:
    kit: str
    standard: tuple[str, str] | None  # (catalog, house) the kit names
    outputs: list[OutputView]
    analyses: dict[str, AnalysisView]
    cells: dict[str, CellView]
    columns: dict[str, ColumnView]
    decisions: dict[str, DecisionView]
    sheet: list[SheetLine]
    problems: list[str]
    catalog_keys: list[str] = field(default_factory=list)  # every <entry> (<unit>) of the catalog


def _json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(", ", ": "))


def record_files(kit: kits.Kit) -> list[str]:
    """The decision files the kit names, in order."""
    return list(kit.decisions)


def _closure(start: str, following: dict[tuple[str, str], list[str]]) -> set[str]:
    seen, queue = {start}, deque([start])
    while queue:
        for target in following.get(("derives_from", queue.popleft()), []):
            if target not in seen:
                seen.add(target)
                queue.append(target)
    return seen - {start}


def _citation(edge: dict, nodes: dict[str, dict]) -> Citation:
    """A `cites` edge. Its text is the label of its span (a page reference's), or empty: a
    claim of Pilot 7 names a section and carries no quote to check."""
    node = nodes.get(edge["to"], {})
    return Citation(edge["to"], str(node.get("label") or ""),
                    bool(edge.get("quote_verified")), edge.get("approved_by"),
                    str(edge.get("origin") or "built"))


def _sentences(event: reading.Event, analysis_id: str,
               raw: dict) -> tuple[list[str], list[str], list[str]]:
    """The analysis in sentences, its options, and the ARS elements it is made of."""
    try:
        a = event.analysis(analysis_id)
    except reading.NotCovered as error:
        elements = [raw.get(name) for name in ("analysisSetId", "dataSubsetId", "methodId")]
        elements += [entry.get("groupingId") for entry in raw.get("orderedGroupings") or []]
        return ([f"{raw.get('name') or analysis_id}: the ARS analysis; its parts cannot be "
                 f"read into sentences here ({error})."], [],
                ["ars:" + analysis_id, *("ars:" + str(e) for e in elements if e)])
    said = [f"Who: the subjects of the analysis set {a.set_id} ({a.set_name}): "
            f"{where_words(a.set_where)}."]
    records = f"Which records: the {a.dataset} records of those subjects"
    if a.subset_id:
        records += (f", in the data subset {a.subset_id} ({a.subset_name}): "
                    f"{where_words(a.subset_where)}")
    said.append(records + f"; the analysis variable {a.dataset}.{a.variable}.")
    groups = []
    for g in a.groupings:
        if g.data_driven:
            text = (f"{g.id} ({g.name}): one group per value of {g.dataset}.{g.variable} "
                    "that occurs")
        else:
            text = (f"{g.id} ({g.name}): the groups defined on {g.dataset}.{g.variable}: "
                    + ", ".join(f"{group.name} ({where_words(group.where)})"
                                for group in g.groups))
        groups.append(text + ("" if g.by_group else ", compared"))
    said.append("Which groups: " + ("; ".join(groups) if groups else "none") + ".")
    statistic = []
    for op in a.operations:
        part = f"{op.name} ({op.method}, operation {op.operation})"
        if op.denominator:
            part += f", over the result {op.denominator[1]} of {op.denominator[0]}"
        statistic.append(part)
    said.append(f"Which statistic: the method {a.method_id}: " + "; ".join(statistic) + ".")
    options = []
    for method, chosen in sorted(a.options.items()):
        for option, value in sorted(chosen.items()):
            where = a.option_sources.get(method, {}).get(option, "the registry default")
            options.append(f"{method}: {option} = {_json(value)} ({where})")
    elements = ["ars:" + analysis_id, "ars:" + a.set_id, "ars:" + a.method_id]
    elements += ["ars:" + str(a.subset_id)] if a.subset_id else []
    elements += ["ars:" + g.id for g in a.groupings]
    return said, options, elements


def load(root: Path, kit_id: str, folder: Path | None = None, recompute: Path | None = None,
         p4: dict[tuple[str, str], str] | None = None) -> Review:
    """The review of a built kit. `p4`: (decision ID, unit) -> class, from a P4 matrix."""
    kit = kits.load_kit(root, kit_id)
    folder = folder or build_dir(root) / "kits" / kit_id
    recompute = recompute or build_dir(root) / "recompute" / kit_id
    if not (folder / GRAPH / "edges.jsonl").is_file():
        raise ReviewError(f"{folder}: no graph; build the kit first (specfirst build {kit_id})")
    problems: list[str] = []
    nodes = {node["id"]: node for node in read_jsonl(folder / GRAPH / "nodes.jsonl")}
    edges = read_jsonl(folder / GRAPH / "edges.jsonl")
    coverage = json.loads((folder / GRAPH / "coverage.json").read_text(encoding="ascii"))
    following: dict[tuple[str, str], list[str]] = {}
    by_from: dict[tuple[str, str], list[dict]] = {}
    for edge in edges:
        following.setdefault((edge["type"], edge["from"]), []).append(edge["to"])
        by_from.setdefault((edge["type"], edge["from"]), []).append(edge)
    registry = json.loads((root / REGISTRY).read_text(encoding="ascii"))["methods"]
    quotes = decision_records.kit_quotes(root, kit, folder)

    # The decision records, by key.
    records: list[tuple[dict, str]] = []
    for name in record_files(kit):
        path = folder / name if (folder / name).is_file() else root / "kits" / kit_id / name
        records += [(record, name) for record in read_jsonl(path)]
    standard = kit.standard
    catalog = house = None
    if standard:
        from specfirst.compile import house as houses

        catalog, house = houses.load_pair(root, standard[0], standard[1])
    features = None  # the design features of the study: no kit states them yet
    decisions: dict[str, DecisionView] = {}
    for record, source in records:
        key = f"{record['id']} ({record['unit']})"
        decisions[key] = _decision(record, source, catalog, house, quotes,
                                   (p4 or {}).get((record["id"], record["unit"]), NOT_TESTED))
    bound: dict[str, list[str]] = {}
    for key, view in decisions.items():
        for element in view.binds:
            bound.setdefault(element, []).append(key)

    # The recomputation of issue #29.
    report: dict[tuple[str, str], dict] = {}
    scripts: dict[tuple[str, str], tuple[str, str]] = {}
    if (recompute / "run" / "report.json").is_file():
        made = json.loads((recompute / "run" / "report.json").read_text(encoding="ascii"))
        report = {(item["event"], item["analysis"]): item for item in made["analyses"]}
        plan = json.loads((recompute / "bundle" / "plan.json").read_text(encoding="ascii"))
        for item in plan["analyses"]:
            if item.get("file") and (recompute / "bundle" / item["file"]).is_file():
                scripts[(item["event"], item["analysis"])] = (
                    item["file"], (recompute / "bundle" / item["file"]).read_text(
                        encoding="ascii"))
    else:
        problems.append(f"no recomputation of {kit_id} (build/recompute/{kit_id}); run "
                        f"specfirst recompute {kit_id}")

    # The ADaM and SDTM columns of the graph.
    resolved: dict[str, dict] = {}
    for path in sorted((folder / RESOLVED).glob("*.json")):
        made = json.loads(path.read_text(encoding="utf-8"))
        for entry in made.get("entries") or []:
            spec = entry.get("specification") or {}
            domain = str(spec.get("domain") or path.stem).upper()
            for column in spec.get("columns") or []:
                resolved[f"adam:{domain}.{column.get('name')}"] = column
    terminals = {entry["column"]: ("gap" if entry.get("gaps") else str(entry.get("terminal")))
                 for entry in coverage.get("columns", [])}
    columns: dict[str, ColumnView] = {}
    for node_id, node in nodes.items():
        if node.get("layer") not in ("L3", "L4"):
            continue
        spec = resolved.get(node_id, {})
        comment = ((spec.get("submission") or {}).get("comment") or {})
        view = ColumnView(
            node_id, label=str(spec.get("label") or ""),
            comment=str(comment.get("text") or "") if isinstance(comment, dict) else str(comment),
            rule=_json(spec["derivation"]) if spec.get("derivation") else "",
            source=f"{node['source']['file']}:{node['source']['line']}",
            decisions=sorted(bound.get(node_id, [])),
            cites=[_citation(edge, nodes) for edge in by_from.get(("cites", node_id), [])],
            derives=sorted(following.get(("derives_from", node_id), [])))
        view.sdtm = sorted(c for c in _closure(node_id, following) if c.startswith("sdtm:"))
        view.terminal = terminals.get(node_id, "")
        columns[node_id] = view

    # The analyses and the cells of every built grid.
    outputs: list[OutputView] = []
    analyses: dict[str, AnalysisView] = {}
    cells: dict[str, CellView] = {}
    read = coverage.get("analyses", {})
    for spec in kit.results:
        data = json.loads((folder / spec.ars).read_text(encoding="utf-8"))
        event = ars.index(data)
        reader = reading.Event(data, spec.id, registry, spec.binding)
        rows = {row["id"]: row for row in read_jsonl(folder / ARD / f"{spec.id}.jsonl")}
        for display in spec.displays:
            grid = json.loads((folder / GRID / f"{display.output}.json").read_text(
                encoding="ascii"))
            labels = {column["id"]: column["label"] for column in grid["columns"]}
            order: list[str] = []
            for row in grid["rows"]:
                for cell in row["cells"]:
                    if not cell["ard"]:
                        continue
                    found, behind = [], []
                    for key in cell["ard"]:
                        result = rows.get(key)
                        if result is None:
                            problems.append(f"{cell['id']}: {key} is not in the ARD")
                            continue
                        found.append((key, result["operation_id"], _json(result["raw_value"])))
                        behind += [f"{spec.id}/{target[len('ars:'):]}"
                                   for target in following.get(("computes", key), [])]
                    if not found:
                        continue
                    first = f"{spec.id}/{rows[found[0][0]]['analysis_id']}"
                    behind = sorted(set(behind), key=lambda k: (k != first, k))
                    cells[cell["id"]] = CellView(
                        cell["id"], display.output,
                        " / ".join(t for t in (row.get("section"), row["label"]) if t),
                        labels.get(cell["column"], cell["column"]), cell["text"], found, first,
                        behind)
                    order += [key for key in behind if key not in order]
            outputs.append(OutputView(display.output, spec.id, grid, order))
            for key in order:
                if key in analyses:
                    continue
                name = key.partition("/")[2]
                raw = event.analyses[name]
                said, options, elements = _sentences(reader, name, raw)
                view = AnalysisView(key, spec.id, name, str(raw.get("name") or name), said,
                                    options, elements)
                view.decisions = sorted({k for element in elements
                                         for k in bound.get(element, [])})
                view.cites = [_citation(edge, nodes)
                              for edge in by_from.get(("cites", "ars:" + name), [])]
                view.columns = [(item["column"], item["roles"])
                                for item in read.get("ars:" + name, {}).get("reads", [])]
                view.recompute = report.get((spec.id, name))
                view.script = scripts.get((spec.id, name))
                analyses[key] = view
    sheet = _sheet(decisions, analyses, cells, kit, catalog, house, features)
    keys = [f"{entry} ({unit})" for entry, unit in catalog.keys()] if catalog is not None else []
    return Review(kit.id, standard, outputs, analyses, cells, columns, decisions, sheet,
                  problems, keys)


def _decision(record: dict, source: str, catalog, house, quotes: decision_records.Quotes,
              p4: str) -> DecisionView:
    """A decision record as the page shows it: mark, alternatives, checked quotes."""
    entry = None
    if catalog is not None and not str(record["id"]).startswith("custom:"):
        try:
            entry = catalog.entry(record["id"])
        except KeyError:
            entry = None
    mark, alternatives, sources = CUSTOMIZED, [], []
    value = record.get("value") or {}
    if entry is not None:
        # A default by design is one value per case: the record takes the house's default
        # when its value is that of one of them (the case is the study's design).
        if any(_json(default) == _json(value) for default in decision_records.house_values(
                catalog, house, entry.id, record["unit"])):
            mark = HOUSE_DEFAULT
            sources = decision_records.house_sources(catalog, house, entry.id, record["unit"],
                                                     value)
        phrase = catalog.units[record["unit"]].phrase if record["unit"] in catalog.units else ""
        # A slot of an alternative not taken has no value: it is shown as <name>.
        alternatives = [re.sub(r"\{(\w+)\}", r"<\1>", alternative.statement.replace(
                            "{output}", phrase or "the output"))
                        for alternative in entry.alternatives
                        if alternative.id != value.get("rule")]
    citations = [Citation(f"doc:{c.get('doc')}#{c.get('anchor')}", str(c.get("quote") or ""),
                          quotes.found(str(c.get("doc")), str(c.get("quote") or "")),
                          c.get("approved_by"), "record", quotes.knows(str(c.get("doc"))))
                 for c in record.get("citations") or []]
    return DecisionView(
        f"{record['id']} ({record['unit']})", record["id"], record["unit"],
        str(record.get("statement") or ""), _json(value), str(record.get("status") or ""),
        str(record.get("class") or ""), mark, citations, alternatives,
        sorted(record.get("binds") or []), p4, source, sources)


def _sheet(decisions, analyses, cells, kit, catalog, house, features) -> list[SheetLine]:
    """Every study-level decision: the records, the catalog entries the records do not
    take, the kit's bindings and the layout settings."""
    reached: dict[str, set[str]] = {}
    for cell in cells.values():
        for key in cell.analyses:
            for decision in analyses[key].decisions if key in analyses else []:
                reached.setdefault(decision, set()).add(cell.id)
    lines = [SheetLine("record", key, view.unit, view.statement, view.status, view.klass,
                       view.mark, view.citations, view.p4, len(reached.get(key, ())))
             for key, view in decisions.items()]
    if catalog is not None:
        from specfirst.compile import predicate

        taken = {(view.id, view.unit) for view in decisions.values()}
        for entry_id, unit in catalog.keys():
            if (entry_id, unit) in taken:
                continue
            entry = catalog.entry(entry_id)
            if features is not None and not predicate.evaluate(
                    predicate.parse(entry.applies_when), features):
                continue
            default = decision_records.house_values(catalog, house, entry_id, unit)
            lines.append(SheetLine(
                "catalog entry", f"{entry_id} ({unit})", unit, entry.question, "no record",
                "", HOUSE_DEFAULT if default else "no house default", [], NOT_TESTED, 0))
    for spec in kit.results:
        for method, options in sorted(((spec.binding or {}).get("options") or {}).items()):
            for option, value in sorted(options.items()):
                lines.append(SheetLine("kit binding", f"{spec.id}: {method}.{option}", spec.id,
                                       f"{method}: {option} = {_json(value)}", "stated", "",
                                       CUSTOMIZED, [], NOT_TESTED, 0))
        for display in spec.displays:
            lines.append(SheetLine("layout", f"{display.output}: {display.layout}", spec.id,
                                   f"the layout of {display.output}, a file of the kit", "stated",
                                   "", CUSTOMIZED, [], NOT_TESTED, sum(
                                       1 for cell in cells.values()
                                       if cell.output == display.output)))
    return lines
