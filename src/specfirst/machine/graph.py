"""The SDTM to ADaM part of the trace graph (PLAN.md sections 4.1, 4.2 and 7.5).

Nodes: one per ADaM output column (layer L4) and one per SDTM column that a
specification reads (layer L3). Edges: `derives_from`, static, from an ADaM
column to the ADaM or SDTM columns its rule reads. Helper columns, lookups
(yamaa's intermediates) and row templates are not nodes: an edge goes
through them.

What an edge means, and what it does not (ADR-001, item 6):

- It says what a column's rule reads, not which rows contributed. A value
  the rule computes with and a column that only selects or orders rows (the
  filter of a row template or of the specification, the key, filter and
  order of a lookup) both give an edge, and the edge does not say which it
  is. coverage.json says per column whether the rule itself reads a column
  (`value`); a filter on rows is not part of the rule.
- There is one edge per pair of columns. Its file and line are those of one
  place that reads the target: a rule before a filter on rows or the
  declaration of a lookup, then the nearest on the way, then the lowest file
  and line. A column taken through a lookup is cited where the rule names
  it, whether the lookup reads an input or the dataset itself. A join key
  is cited at the rule that causes the join; the key itself is named in the
  specification's `input`.
- The hash of an ADaM node covers the column's own rule and every helper
  column, lookup and row template the rule passes through.

Pilot 7's reviewed claims are taken over as candidate `cites` edges from
ADaM columns to document spans (layer L0). They are judged edges, marked
imported, with no verified quote and no approval (section 4.2). Several
citations of one span by one column give one edge.

The graph has no node for a literal or for a dataset. A column that reaches
no column is recorded in coverage.json as `literal`, with the declared
inputs whose rows it is built on. A column is complete only if every column
it reaches is: a gap is passed on to the columns that read it.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import quote

from specfirst import schemas
from specfirst.kit import Kit
from specfirst.machine.canonical import content_hash, read_jsonl, write_json, write_jsonl
from specfirst.machine.lineage import Lineage, Read, column_dependencies, pointer
from specfirst.machine.runner import SpecPlan

_ITEM_DEF = re.compile(r'<ItemDef\b[^>]*?\bOID="([^"]+)"')
_VARIABLE_LINE = re.compile(r'^\s*"variable"\s*:\s*("(?:[^"\\]|\\.)*")')
_ANCHOR_SAFE = "!$&'()*+,;=:@/?.-_~"
# Where lineage records what the top-level filter of a specification reads.
_SPEC_FILTER = pointer("filter")


class GraphError(RuntimeError):
    """The graph cannot be built from these inputs."""


@dataclass
class Graph:
    nodes: list[dict] = field(default_factory=list)
    edges: list[dict] = field(default_factory=list)
    coverage: dict = field(default_factory=dict)


def adam_id(dataset: str, column: str) -> str:
    return f"adam:{dataset}.{column}"


def sdtm_id(dataset: str, column: str) -> str:
    return f"sdtm:{dataset}.{column}"


def item_def_lines(path: Path) -> dict[str, int]:
    """The line of each `<ItemDef OID="...">` of a Define-XML file."""
    lines: dict[str, int] = {}
    with open(path, encoding="utf-8", errors="replace") as handle:
        for number, line in enumerate(handle, start=1):
            for match in _ITEM_DEF.finditer(line):
                lines.setdefault(match.group(1), number)
    return lines


def _site(plan: SpecPlan, place: str) -> tuple[str, int]:
    """The file and line where the element at a JSON pointer was written."""
    while True:
        origin = plan.origins.get(place)
        if origin and origin.get("declaring_source") and origin.get("line"):
            if origin.get("source_kind") != "schema_default":
                return origin["declaring_source"], int(origin["line"])
        if not place:
            return plan.entry, 1
        place = place.rsplit("/", 1)[0]


def _definition_place(plan: SpecPlan, lineage: Lineage, name: str) -> str:
    places = [read.pointer for read in lineage.reads if read.element == f"spec.{name}"]
    for wanted in ("/columns/", "/rows/"):
        for place in places:
            if place.startswith(wanted) and place.endswith(("/derivation", f"/{name}")):
                return place
    return places[0] if places else ""


def _column_content(spec: dict, name: str) -> dict:
    column = next((c for c in spec.get("columns", []) if c["name"] == name), None)
    rows = {
        row["id"]: row["derivations"][name]
        for row in spec.get("rows", [])
        if name in row.get("derivations", {})
    }
    return {"column": column, "rows": rows}


def _node_content(spec: dict, name: str, through: set[str]) -> dict:
    """What the hash of an ADaM node covers: the rule and everything it passes through."""
    lookups = {item["id"]: item for item in spec.get("intermediates", [])}
    rows = {row["id"]: row for row in spec.get("rows", [])}
    passed: dict[str, object] = {}
    for element in sorted(through):
        head, _, tail = element.partition(".")
        if head == "spec":
            passed[element] = _column_content(spec, tail)
        elif head == "row":
            passed[element] = {k: v for k, v in rows.get(tail, {}).items() if k != "derivations"}
        elif head == "intermediate":
            passed[element] = lookups.get(tail)
        elif head in lookups:
            passed[f"intermediate.{head}"] = lookups[head]
    return {**_column_content(spec, name), "through": passed}


@dataclass
class _Trace:
    # target ID -> (0 for a rule, 1 for a filter on rows or a lookup declaration; depth; file;
    # line)
    targets: dict[str, tuple[int, int, str, int]] = field(default_factory=dict)
    inputs: set[str] = field(default_factory=set)
    gaps: set[str] = field(default_factory=set)
    through: set[str] = field(default_factory=set)
    # The rule itself reads a column, apart from what only selects rows: its row
    # templates and the filter of the specification.
    value: bool = False


def _trace_column(
    plan: SpecPlan, lineage: Lineage, by_element: dict[str, list[Read]], name: str,
    datasets: dict[str, tuple[str, str]],
) -> _Trace:
    """Follow one output column through helpers, lookups and row templates."""
    spec = plan.specification
    outputs = set(lineage.outputs)
    lookups = {item["id"]: (j, item) for j, item in enumerate(spec.get("intermediates", []))}
    rows = {row["id"]: row["dataset"] for row in spec.get("rows", [])}
    trace = _Trace()
    if name not in lineage.defined:
        trace.gaps.add("no derivation in the specification")

    def whole(alias: str) -> None:
        alias = lookups[alias][1]["dataset"] if alias in lookups else alias
        if alias in datasets:
            layer, dataset = datasets[alias]
            trace.inputs.add(f"{layer}:{dataset}")

    def passes_on(element: str, read: Read) -> bool:
        """A column taken from a lookup as it is: the rule that names it is the place."""
        head, _, tail = element.partition(".")
        if head not in lookups:
            return False
        j, item = lookups[head]
        return tail not in item.get("derivations", {}) and read.pointer == pointer(
            "intermediates", j)

    def walk(with_rows: bool) -> dict[str, tuple[int, int, str, int]]:
        """The columns reached, each with its place: (context, depth, file, line).

        with_rows False leaves out what only selects rows: the row templates
        and the filter of the specification. The walk goes level by level,
        so that of two places at the same distance the lowest file and line
        wins, whichever element is visited first.
        """
        targets: dict[str, tuple[int, int, str, int]] = {}

        def target(node: str, found: tuple[int, int, str, int]) -> None:
            if node not in targets or found < targets[node]:
                targets[node] = found

        start = f"spec.{name}"
        seen = {start}
        # element -> where it was named: (context, file, line), or None for the start
        level: list[tuple[str, tuple[int, str, int] | None]] = [(start, None)]
        depth = 0
        while level:
            found: dict[str, tuple[int, str, int]] = {}
            for element, named_at in level:
                if element.startswith("row."):
                    whole(rows.get(element[4:], ""))
                for read in by_element.get(element, []):
                    on_rows = read.pointer == _SPEC_FILTER
                    if on_rows and not with_rows:
                        continue
                    site = _site(plan, read.pointer)
                    trace.gaps.update(f"unresolved reference {ref} at {site[0]}:{site[1]}"
                                      for ref in read.unresolved)
                    trace.gaps.update(f"unknown name {ref} at {site[0]}:{site[1]}"
                                      for ref in read.unknown)
                    for alias in read.whole:
                        whole(alias)
                    if named_at and passes_on(element, read):
                        place = named_at  # the rule that names the lookup's column
                    else:
                        declared = on_rows or element.startswith(("row.", "intermediate."))
                        place = (1 if declared else 0, *site)
                    for ref in sorted(read.refs):
                        head, _, tail = ref.partition(".")
                        if head == "row" and not with_rows:
                            continue
                        if head == "spec" and tail in outputs and tail != name:
                            target(adam_id(plan.name, tail), (place[0], depth, *place[1:]))
                        elif head in datasets and head not in ("spec", "row", "intermediate"):
                            layer, dataset = datasets[head]
                            target(f"{layer}:{dataset}.{tail}", (place[0], depth, *place[1:]))
                        elif ref not in seen and (ref not in found or place < found[ref]):
                            found[ref] = place
            seen |= set(found)
            level = sorted(found.items())
            depth += 1
        trace.through |= seen - {start}
        return targets

    if not rows:  # without row templates, every row comes from the base dataset
        whole(spec.get("base") or "")
    trace.value = bool(walk(with_rows=False))
    trace.targets = walk(with_rows=True)
    return trace


def _closure(edges: list[dict]) -> dict[str, set[str]]:
    """For every node with a derives_from edge: all nodes it reaches through such edges."""
    following: dict[str, set[str]] = {}
    for edge in edges:
        if edge["type"] == "derives_from":
            following.setdefault(edge["from"], set()).add(edge["to"])
    reach: dict[str, set[str]] = {}
    for start in following:
        seen, stack = {start}, [start]
        while stack:
            for nxt in following.get(stack.pop(), ()):
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        reach[start] = seen - {start}
    return reach


def _sdtm(nodes: set[str]) -> set[str]:
    return {node for node in nodes if node.startswith("sdtm:")}


def build_graph(kit: Kit, kit_dir: Path, plans: list[SpecPlan]) -> Graph:
    """Nodes, edges and coverage from the resolved specifications. Reads no study data rows."""
    import pyarrow.parquet as pq

    produced = {plan.name: plan.columns for plan in plans}
    sdtm_schema: dict[str, object] = {}
    sdtm_file: dict[str, str] = {}
    define = next((doc for doc in kit.documents if doc.file.startswith(kit.sdtm + "/")), None)
    define_lines = item_def_lines(kit_dir / define.file) if define else {}

    nodes: dict[str, dict] = {}
    edges: dict[tuple[str, str, str], dict] = {}
    traces: dict[str, _Trace] = {}
    for plan in plans:
        columns_of: dict[str, set[str]] = {}
        datasets: dict[str, tuple[str, str]] = {}
        for source in plan.inputs:
            datasets[source.alias] = (source.layer, source.dataset)
            if source.layer == "adam":
                columns_of[source.alias] = set(produced[source.dataset])
            else:
                if source.dataset not in sdtm_schema:
                    sdtm_schema[source.dataset] = pq.read_schema(kit_dir / source.file)
                    sdtm_file[source.dataset] = source.file
                columns_of[source.alias] = set(sdtm_schema[source.dataset].names)
        lineage = column_dependencies(plan.specification, columns_of)
        by_element: dict[str, list[Read]] = {}
        for read in lineage.reads:
            by_element.setdefault(read.element, []).append(read)
        labels = {c["name"]: c.get("label") for c in plan.specification.get("columns", [])}
        for name in lineage.outputs:
            node = adam_id(plan.name, name)
            trace = _trace_column(plan, lineage, by_element, name, datasets)
            traces[node] = trace
            file, line = _site(plan, _definition_place(plan, lineage, name))
            nodes[node] = {
                "id": node, "layer": "L4", "kind": "variable",
                "hash": content_hash(_node_content(plan.specification, name, trace.through)),
                "source": {"file": file, "line": line},
            }
            if labels.get(name):
                nodes[node]["label"] = labels[name]
            for to, (_, _, file, line) in trace.targets.items():
                edges[("derives_from", node, to)] = {
                    "type": "derives_from", "from": node, "to": to, "proof": "static",
                    "origin": "built", "source": {"file": file, "line": line},
                }

    for edge in list(edges.values()):
        to = edge["to"]
        if to in nodes:
            continue
        if not to.startswith("sdtm:"):
            traces[edge["from"]].gaps.add(f"reads {to}, which no specification of the kit builds")
            del edges[(edge["type"], edge["from"], to)]
            continue
        dataset, column = to[len("sdtm:"):].split(".", 1)
        kind = sdtm_schema[dataset].field(column).type
        line = define_lines.get(f"{dataset}.{column}")
        nodes[to] = {
            "id": to, "layer": "L3", "kind": "variable",
            "hash": content_hash({"dataset": dataset, "name": column, "type": str(kind)}),
            "source": {"file": define.file, "line": line} if line else
                      {"file": sdtm_file[dataset], "line": 1},
        }

    claims = _import_claims(kit, kit_dir, plans, nodes, edges)
    ordered_edges = [edges[key] for key in sorted(edges)]
    reach = _closure(ordered_edges)
    with_gap = {node for node, trace in traces.items() if trace.gaps}
    columns = []
    for node in sorted(traces):
        trace = traces[node]
        reached = reach.get(node, set())
        # A gap is passed on: a column is complete only if every column it reaches is.
        gaps = sorted(trace.gaps) + [
            f"reads {other}, which has a gap" for other in sorted(reached & with_gap)
        ]
        sdtm = len(_sdtm(reached))
        columns.append({
            "column": node, "terminal": "gap" if gaps else "sdtm" if sdtm else "literal",
            "sdtm": sdtm, "value": trace.value, "inputs": sorted(trace.inputs), "gaps": gaps,
        })
    return Graph(
        nodes=[nodes[key] for key in sorted(nodes)],
        edges=ordered_edges,
        coverage={"columns": columns, "claims": claims},
    )


def _claim_lines(text: str, variables: list[str], where: str) -> list[int]:
    """The line of each claim: the line of its "variable" key, in file order."""
    found = []
    for number, line in enumerate(text.splitlines(), start=1):
        match = _VARIABLE_LINE.match(line)
        if match:
            found.append((json.loads(match.group(1)), number))
    if [name for name, _ in found] != variables:
        raise GraphError(f"{where}: cannot find the line of every claim")
    return [number for _, number in found]


def _import_claims(
    kit: Kit, kit_dir: Path, plans: list[SpecPlan], nodes: dict[str, dict],
    edges: dict[tuple[str, str, str], dict],
) -> dict:
    """Pilot 7's claims as candidate cites edges. Returns what was taken and what was not."""
    summary: dict[str, dict] = {}
    if not kit.claims:
        return summary
    hashes = {entry.path: entry.sha256 for entry in kit.files}
    item_lines = {
        doc.id: item_def_lines(kit_dir / doc.file)
        for doc in kit.documents if doc.file.endswith(".xml")
    }
    for plan in plans:
        file = f"{kit.claims}/{plan.name.lower()}-claims.json"
        if file not in hashes:
            continue
        text = (kit_dir / file).read_text(encoding="utf-8")
        data = json.loads(text)
        if str(data.get("dataset", "")).upper() != plan.name:
            raise GraphError(f"{file}: the claims are for dataset {data.get('dataset')!r}")
        claims = data.get("claims") or []
        lines = _claim_lines(text, [claim.get("variable") for claim in claims], file)
        taken, cited, not_documents, not_columns = 0, 0, Counter(), set()
        for claim, line in zip(claims, lines, strict=True):
            node = adam_id(plan.name, str(claim.get("variable")))
            if node not in nodes:
                not_columns.add(str(claim.get("variable")))
                continue
            for citation in claim.get("citations") or []:
                document = kit.document(str(citation.get("document", "")))
                if document is None:
                    not_documents[str(citation.get("document", ""))] += 1
                    continue
                cited += 1
                section = str(citation.get("section") or "")
                anchor = quote(section, safe=_ANCHOR_SAFE)
                span = f"doc:{document.id}#{anchor}" if anchor else f"doc:{document.id}"
                if span not in nodes:
                    at = item_lines.get(document.id, {}).get(section, 1)
                    nodes[span] = {
                        "id": span, "layer": "L0", "kind": "span",
                        "hash": content_hash({"document": hashes[document.file],
                                              "anchor": anchor}),
                        "source": {"file": document.file, "line": at},
                    }
                key = ("cites", node, span)
                if key not in edges:
                    taken += 1
                    edges[key] = {
                        "type": "cites", "from": node, "to": span, "proof": "judged",
                        "origin": "imported", "quote_verified": False, "approved_by": None,
                        "source": {"file": file, "line": line},
                    }
        summary[plan.name] = {
            "file": file, "claims": len(claims), "citations_of_kit_documents": cited,
            "cites_edges": taken,
            "citations_not_to_kit_documents": dict(sorted(not_documents.items())),
            "variables_not_output_columns": sorted(not_columns),
        }
    return summary


def write_graph(folder: Path, graph: Graph) -> list[Path]:
    paths = [folder / "nodes.jsonl", folder / "edges.jsonl", folder / "coverage.json"]
    write_jsonl(paths[0], graph.nodes)
    write_jsonl(paths[1], graph.edges)
    write_json(paths[2], graph.coverage)
    return paths


def check_graph(
    root: Path, folder: Path, expected: dict[str, list[str]], accepted_gaps: dict[str, str],
    sdtm_columns: dict[str, set[str]] | None = None,
) -> tuple[list[str], list[str]]:
    """Check the written graph against the gate of real-1 (PLAN.md section 13.3).

    expected: the output columns of every dataset, taken from the built data.
    accepted_gaps: column ID -> reason, for gaps the kit lists.
    sdtm_columns: the columns of every SDTM dataset of the kit, if known.
    Returns the lines of the report and the problems.

    What this proves: the files fit the schema and agree with each other,
    every output column has a node, no column has a gap the kit does not
    list, and reachability, computed here from edges.jsonl, is what
    coverage.json records. It cannot see a reference the dependency analysis
    missed: such a column would be recorded as literal in both files. For
    the pilot, tests/pilot compares the analysis with Pilot 7's (A3) and
    with the engine (A4).
    """
    lines: list[str] = []
    problems: list[str] = []
    nodes = read_jsonl(folder / "nodes.jsonl")
    edges = read_jsonl(folder / "edges.jsonl")
    with open(folder / "coverage.json", encoding="ascii") as handle:
        coverage = json.load(handle)
    for part, records in (("node", nodes), ("edge", edges)):
        validator = schemas.validator("graph", part, root)
        for record in records:
            for error in validator.iter_errors(record):
                name = record.get("id") or f"{record.get('from')} -> {record.get('to')}"
                problems.append(f"{part} {name}: {error.message}")
    ids = [node["id"] for node in nodes]
    known = set(ids)
    problems += [f"node {name}: listed {count} times" for name, count in Counter(ids).items()
                 if count > 1]
    for edge in edges:
        problems += [f"edge {edge['type']} {edge['from']} -> {edge['to']}: {end} is not a node"
                     for end in (edge["from"], edge["to"]) if end not in known]
    if nodes != sorted(nodes, key=lambda n: n["id"]):
        problems.append("nodes.jsonl is not sorted by id")
    if edges != sorted(edges, key=lambda e: (e["type"], e["from"], e["to"])):
        problems.append("edges.jsonl is not sorted by type, from, to")
    if sdtm_columns is not None:
        for name in sorted(_sdtm(known)):
            dataset, _, column = name[len("sdtm:"):].partition(".")
            if column not in sdtm_columns.get(dataset, set()):
                problems.append(f"node {name}: not a column of the kit's SDTM data")

    reach = _closure(edges)
    recorded = {entry["column"]: entry for entry in coverage.get("columns", [])}
    with_gap = {column for column, entry in recorded.items() if entry["gaps"]}
    wanted = {adam_id(dataset, column) for dataset, columns in expected.items()
              for column in columns}
    for extra in sorted(set(recorded) - wanted):
        problems.append(f"{extra}: in coverage.json but not an output column of the built data")
    lines.append(f"{'dataset':9s} {'columns':>7s} {'to SDTM':>7s} {'by rows':>7s} "
                 f"{'literal':>7s} {'gaps':>5s}")
    totals = Counter()
    for dataset, columns in expected.items():
        count = Counter()
        for column in columns:
            node = adam_id(dataset, column)
            entry = recorded.get(node)
            if node not in known or entry is None:
                problems.append(f"{node}: an output column with no node or no coverage entry")
                count["gaps"] += 1
                continue
            reached = reach.get(node, set())
            sdtm = len(_sdtm(reached))
            behind = sorted((reached & with_gap) - {node})
            if entry["gaps"]:
                count["gaps"] += 1
                reason = accepted_gaps.get(node)
                detail = "; ".join(entry["gaps"])
                if reason:
                    lines.append(f"  gap {node}: {detail} (listed: {reason})")
                else:
                    problems.append(f"{node}: gap with no listed reason: {detail}")
            elif behind:
                count["gaps"] += 1
                problems.append(f"{node}: recorded as complete, but it reads {behind[0]}, "
                                "which has a gap")
            elif sdtm:
                count["sdtm"] += 1
                count["rows"] += 0 if entry.get("value") else 1
            elif entry["terminal"] == "literal":
                count["literal"] += 1
            else:
                problems.append(f"{node}: no derives_from path to an SDTM column")
                count["gaps"] += 1
            if sdtm != entry["sdtm"] or (not entry["gaps"] and entry["terminal"] != (
                    "sdtm" if sdtm else "literal")):
                problems.append(f"{node}: coverage.json disagrees with edges.jsonl")
        totals.update(count)
        lines.append(f"{dataset:9s} {len(columns):7d} {count['sdtm']:7d} {count['rows']:7d} "
                     f"{count['literal']:7d} {count['gaps']:5d}")
    total = sum(len(columns) for columns in expected.values())
    lines.append(f"{'TOTAL':9s} {total:7d} {totals['sdtm']:7d} {totals['rows']:7d} "
                 f"{totals['literal']:7d} {totals['gaps']:5d}")
    lines.append("to SDTM: reaches SDTM columns through derives_from. by rows: those of them "
                 "whose own rule reads no column")
    lines.append("and that reach SDTM only through a filter on rows (of a row template or of the "
                 "specification).")
    for node in sorted(set(accepted_gaps) - with_gap):
        problems.append(f"{node}: listed as a gap in the kit, but it has none")
    by_layer = Counter(node["layer"] for node in nodes)
    by_type = Counter(edge["type"] for edge in edges)
    cites = [edge for edge in edges if edge["type"] == "cites"]
    lines.append("nodes: " + ", ".join(f"{k} {v}" for k, v in sorted(by_layer.items())))
    lines.append("edges: " + ", ".join(f"{k} {v}" for k, v in sorted(by_type.items())))
    lines.append(
        f"cites edges: {sum(1 for e in cites if e.get('origin') == 'imported')} imported, "
        f"{sum(1 for e in cites if e.get('quote_verified'))} with a verified quote, "
        f"{sum(1 for e in cites if e.get('approved_by'))} approved by a person"
    )
    literal = [entry for entry in coverage.get("columns", []) if entry["terminal"] == "literal"]
    if literal:
        on = Counter(", ".join(entry["inputs"]) or "no declared input" for entry in literal)
        lines.append("literal columns sit on rows of: "
                     + "; ".join(f"{k} ({v})" for k, v in sorted(on.items())))
    return lines, problems


# ---- from cells to ADaM columns (real-3; PLAN.md sections 4.2 and 7.5) -----------------


def ars_id(analysis_id: str) -> str:
    return "ars:" + quote(analysis_id, safe="")


@dataclass(frozen=True)
class Display:
    """One built grid with what it was built from, for the trace."""

    grid: dict
    grid_file: str  # in the build, with forward slashes
    event: object  # the reporting event (specfirst.machine.ars.Event)
    ars_file: str
    ard_file: str
    rows: list[dict]  # the ARD rows of the file, in its order
    subject_key: str


def _id_lines(path: Path, wanted: set[str]) -> dict[str, int]:
    """The line of `"id": "<name>"` for every wanted name, in a JSON file as it is written."""
    lines: dict[str, int] = {}
    pattern = re.compile(r'^\s*"id"\s*:\s*("(?:[^"\\]|\\.)*")')
    with open(path, encoding="utf-8", errors="replace") as handle:
        for number, line in enumerate(handle, start=1):
            match = pattern.match(line)
            if match:
                name = json.loads(match.group(1))
                if name in wanted:
                    lines.setdefault(name, number)
    return lines


def referenced_analyses(event, analysis: dict, operation_id: str) -> list[str]:
    """The analyses whose results an operation of an analysis is computed from.

    A percent names a numerator and a denominator (rule I15); each is a
    result of an analysis, the same one or another.
    """
    operation = event.operations.get(operation_id, ("", {}))[1]
    wanted = {relation.get("id") for relation in
              operation.get("referencedOperationRelationships") or []}
    return sorted({reference["analysisId"]
                   for reference in analysis.get("referencedAnalysisOperations") or []
                   if reference.get("referencedOperationRelationshipId") in wanted})


def add_displays(graph: Graph, kit_dir: Path, displays: list[Display]) -> None:
    """Add the cells of built grids, the ARD rows they show and the analyses behind them.

    Edges: `shows`, cell to ARD row, executed: the grid builder put the row
    into the cell. `computes`, ARD row to analysis, executed: the engine
    stamped the row with its analysis; a row that is computed from results
    of another analysis (the denominator of a percent) has an edge to that
    analysis too. `reads`, analysis to ADaM column, static: what the analysis
    names in the ARS file, in any role (variable, set, subset, grouping,
    key). The roles are in coverage.json: an edge of schema version 0 cannot
    carry one.

    Only what a built grid shows gets a node. An ADaM column that an
    analysis reads and no specification builds has no node; that is a gap
    of every cell behind it, recorded in coverage.json.
    """
    from specfirst.machine import ars as ars_module

    nodes = {node["id"]: node for node in graph.nodes}
    edges = {(edge["type"], edge["from"], edge["to"]): edge for edge in graph.edges}
    reach = _closure(graph.edges)
    gap_columns = {entry["column"] for entry in graph.coverage.get("columns", [])
                   if entry["gaps"]}
    analyses_read: dict[str, dict] = {}
    coverage_displays: dict[str, dict] = {}
    for display in displays:
        event = display.event
        row_at = {row["id"]: (number, row) for number, row in enumerate(display.rows, start=1)}
        shown_analyses: set[str] = set()
        output = display.grid["output_id"]
        gaps: list[str] = []
        cells = numeric = 0
        behind: dict[str, set[str]] = {}  # cell -> analyses behind it
        for row in display.grid["rows"]:
            for cell in row["cells"]:
                cells += 1
                numeric += any(character.isdigit() for character in cell["text"])
                nodes[cell["id"]] = {
                    "id": cell["id"], "layer": "L7", "kind": "cell", "label": cell["text"],
                    "hash": content_hash({"text": cell["text"], "ard": cell["ard"]}),
                    "source": {"file": display.grid_file, "line": 1},
                }
                behind[cell["id"]] = set()
                for key in cell["ard"]:
                    if key not in row_at:
                        gaps.append(f"{cell['id']} shows {key}, which is not in "
                                    f"{display.ard_file}")
                        continue
                    number, result = row_at[key]
                    source = {"file": display.ard_file, "line": number}
                    nodes[key] = {"id": key, "layer": "L6", "kind": "result",
                                  "hash": content_hash(result), "source": source}
                    edges[("shows", cell["id"], key)] = {
                        "type": "shows", "from": cell["id"], "to": key, "proof": "executed",
                        "origin": "built", "source": {"file": display.grid_file, "line": 1}}
                    analysis = event.analyses[result["analysis_id"]]
                    computed_from = {analysis["id"], *referenced_analyses(
                        event, analysis, result["operation_id"])}
                    for name in sorted(computed_from):
                        edges[("computes", key, ars_id(name))] = {
                            "type": "computes", "from": key, "to": ars_id(name),
                            "proof": "executed", "origin": "built", "source": source}
                    shown_analyses |= computed_from
                    behind[cell["id"]] |= computed_from
        lines = _id_lines(kit_dir / display.ars_file, shown_analyses)
        for name in sorted(shown_analyses):
            analysis = event.analyses[name]
            source = {"file": display.ars_file, "line": lines.get(name, 1)}
            node = {"id": ars_id(name), "layer": "L5", "kind": "analysis",
                    "hash": content_hash({k: v for k, v in analysis.items() if k != "results"}),
                    "source": source}
            if analysis.get("name"):
                node["label"] = str(analysis["name"])
            nodes[node["id"]] = node
            reads = ars_module.reads(event, name, display.subject_key)
            roles: dict[str, list[str]] = {}
            for role, dataset, variable in reads:
                roles.setdefault(adam_id(dataset, variable), []).append(role)
            missing = sorted(column for column in roles if column not in nodes)
            analyses_read[ars_id(name)] = {
                "reads": [{"column": column, "roles": sorted(found)}
                          for column, found in sorted(roles.items())],
                "not_built": missing,
            }
            for column in sorted(roles):
                if column in nodes:
                    edges[("reads", ars_id(name), column)] = {
                        "type": "reads", "from": ars_id(name), "to": column, "proof": "static",
                        "origin": "built", "source": source}
        complete = 0
        sdtm: set[str] = set()
        for cell_id in sorted(behind):
            columns: set[str] = set()
            trouble = []
            for name in sorted(behind[cell_id]):
                entry = analyses_read[ars_id(name)]
                trouble += [f"{name} reads {column}, which the kit does not build"
                            for column in entry["not_built"]]
                columns |= {item["column"] for item in entry["reads"]} - set(entry["not_built"])
            reached = set(columns)
            for column in columns:
                reached |= reach.get(column, set())
            trouble += [f"{column} has a gap" for column in sorted(reached & gap_columns)]
            if not behind[cell_id]:
                continue
            if trouble or not _sdtm(reached):
                gaps += [f"{cell_id}: {problem}" for problem in trouble] or [
                    f"{cell_id}: reaches no SDTM column"]
            else:
                complete += 1
                sdtm |= _sdtm(reached)
        coverage_displays[output] = {
            "grid": display.grid_file, "cells": cells, "numeric": numeric,
            "complete": complete, "results": len({key for row in display.grid["rows"]
                                                  for cell in row["cells"] for key in cell["ard"]}),
            "analyses": sorted(shown_analyses), "sdtm": len(sdtm), "gaps": sorted(set(gaps)),
        }
    graph.nodes = [nodes[key] for key in sorted(nodes)]
    graph.edges = [edges[key] for key in sorted(edges)]
    graph.coverage = {**graph.coverage, "analyses": analyses_read, "displays": coverage_displays}


def check_cells(folder: Path, grids: dict[str, dict]) -> tuple[list[str], list[str]]:
    """Every numeric cell of the grids has a complete path to SDTM columns (P3, section 4.6).

    The paths are walked here, from nodes.jsonl and edges.jsonl alone: cell
    -> shows -> ARD rows -> computes -> analyses -> reads -> ADaM columns ->
    derives_from -> SDTM columns. A path is complete when every step has an
    edge, every element on it is a node, the cell's `shows` edges are
    exactly its `ard` list, no ADaM column on it has a gap, and it ends at
    SDTM columns. A cell that prints a digit and shows no ARD row fails.

    This cannot see a result the builder used and did not record, or a
    column the engine reads and the ARS file does not name; tests/defects
    holds both against the builder and the engine (D8).
    """
    lines: list[str] = []
    problems: list[str] = []
    nodes = {node["id"]: node for node in read_jsonl(folder / "nodes.jsonl")}
    edges = read_jsonl(folder / "edges.jsonl")
    with open(folder / "coverage.json", encoding="ascii") as handle:
        coverage = json.load(handle)
    following: dict[tuple[str, str], set[str]] = {}
    for edge in edges:
        following.setdefault((edge["type"], edge["from"]), set()).add(edge["to"])
    reach = _closure(edges)
    with_gap = {entry["column"] for entry in coverage.get("columns", []) if entry["gaps"]}
    recorded = coverage.get("displays", {})
    for output, grid in sorted(grids.items()):
        count = Counter()
        results_seen: set[str] = set()
        analyses_seen: set[str] = set()
        adam_seen: set[str] = set()
        sdtm_seen: set[str] = set()
        for row in grid["rows"]:
            for cell in row["cells"]:
                count["cells"] += 1
                digits = any(character.isdigit() for character in cell["text"])
                count["numeric"] += digits
                if not cell["ard"]:
                    if digits:
                        problems.append(f"{cell['id']}: prints {cell['text']!r} and shows no "
                                        "ARD row")
                    continue
                trouble = []
                if cell["id"] not in nodes:
                    trouble.append("the cell has no node")
                shows = following.get(("shows", cell["id"]), set())
                if shows != set(cell["ard"]):
                    trouble.append("its shows edges are not the ARD rows of the cell")
                reached_sdtm: set[str] = set()
                for key in cell["ard"]:
                    if key not in nodes:
                        trouble.append(f"{key} has no node")
                    analyses = following.get(("computes", key), set())
                    if not analyses:
                        trouble.append(f"{key} has no computes edge")
                    elif "ars:" + key[len("ard:"):].split("/")[0] not in analyses:
                        trouble.append(f"{key} has no computes edge to its own analysis")
                    for analysis in sorted(analyses):
                        columns = following.get(("reads", analysis), set())
                        if analysis not in nodes or not columns:
                            trouble.append(f"{analysis} has no node or no reads edge")
                        not_built = coverage.get("analyses", {}).get(analysis, {}).get(
                            "not_built", [])
                        trouble += [f"{analysis} reads {column}, which the kit does not build"
                                    for column in not_built]
                        reached = set(columns)
                        for column in columns:
                            reached |= reach.get(column, set())
                        trouble += [f"{column} is not a node" for column in sorted(reached)
                                    if column not in nodes]
                        trouble += [f"{column} has a gap" for column in sorted(reached & with_gap)]
                        if not _sdtm(reached):
                            trouble.append(f"{analysis} reaches no SDTM column")
                        analyses_seen.add(analysis)
                        adam_seen |= {column for column in reached if column.startswith("adam:")}
                        reached_sdtm |= _sdtm(reached)
                    results_seen.add(key)
                if trouble:
                    problems += [f"{cell['id']}: {problem}" for problem in sorted(set(trouble))]
                else:
                    count["complete"] += 1
                    sdtm_seen |= reached_sdtm
        with_results = sum(1 for row in grid["rows"] for cell in row["cells"] if cell["ard"])
        lines.append(f"grid {output}: {count['cells']} cells, {count['numeric']} print a number; "
                     f"{count['complete']} of the {with_results} cells with results have a "
                     "complete path to SDTM columns")
        lines.append(f"  through {len(results_seen)} ARD rows, {len(analyses_seen)} analyses, "
                     f"{len(adam_seen)} ADaM columns, to {len(sdtm_seen)} SDTM columns")
        entry = recorded.get(output)
        if entry is None:
            problems.append(f"grid {output}: coverage.json has no entry for it")
        elif (entry["cells"], entry["numeric"], entry["complete"], entry["sdtm"]) != (
                count["cells"], count["numeric"], count["complete"], len(sdtm_seen)):
            problems.append(f"grid {output}: coverage.json disagrees with the graph files")
    for output in sorted(set(recorded) - set(grids)):
        problems.append(f"grid {output}: in coverage.json, but not a grid of the build")
    return lines, problems
