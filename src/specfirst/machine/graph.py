"""The SDTM to ADaM part of the trace graph (PLAN.md sections 4.1, 4.2 and 7.5).

Nodes: one per ADaM output column (layer L4) and one per SDTM column that a
specification reads (layer L3). Edges: `derives_from`, static, from an ADaM
column to the ADaM or SDTM columns its rule reads. Helper columns, lookups
(yamaa's intermediates) and row templates are not nodes: an edge goes
through them.

What an edge means, and what it does not (ADR-001, item 6):

- It says what a column's rule reads, not which rows contributed. A value
  the rule computes with and a column that only selects or orders rows (the
  filter of a row template, the key, filter and order of a lookup) both
  give an edge, and the edge does not say which it is. coverage.json says
  per column whether the rule itself reads a column (`value`).
- There is one edge per pair of columns. Its file and line are those of one
  place that reads the target: a rule before a row template or the
  declaration of a lookup, then the nearest on the way, then the lowest file
  and line. A column taken through a lookup is cited where the rule names
  it. A join key is cited at the rule that causes the join; the key itself
  is named in the specification's `input`.
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
from collections import Counter, deque
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
    # target ID -> (0 for a rule, 1 for a row template or a lookup declaration; depth; file; line)
    targets: dict[str, tuple[int, int, str, int]] = field(default_factory=dict)
    inputs: set[str] = field(default_factory=set)
    gaps: set[str] = field(default_factory=set)
    through: set[str] = field(default_factory=set)
    value: bool = False  # the rule itself reads a column, apart from its row templates


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
        targets: dict[str, tuple[int, int, str, int]] = {}

        def target(node: str, found: tuple[int, int, str, int]) -> None:
            if node not in targets or found < targets[node]:
                targets[node] = found

        start = f"spec.{name}"
        seen = {start}
        queue: deque[tuple[str, int, tuple[str, int] | None]] = deque([(start, 0, None)])
        while queue:
            element, depth, named_at = queue.popleft()
            if element.startswith("row."):
                whole(rows.get(element[4:], ""))
            context = 1 if element.startswith(("row.", "intermediate.")) else 0
            for read in by_element.get(element, []):
                site = _site(plan, read.pointer)
                trace.gaps.update(f"unresolved reference {ref} at {site[0]}:{site[1]}"
                                  for ref in read.unresolved)
                trace.gaps.update(f"unknown name {ref} at {site[0]}:{site[1]}"
                                  for ref in read.unknown)
                for alias in read.whole:
                    whole(alias)
                taken = named_at if named_at and passes_on(element, read) else site
                for ref in sorted(read.refs):
                    head, _, tail = ref.partition(".")
                    if head == "row" and not with_rows:
                        continue
                    if head == "spec" and tail in outputs and tail != name:
                        target(adam_id(plan.name, tail), (context, depth, *site))
                    elif head in datasets and head not in ("spec", "row", "intermediate"):
                        layer, dataset = datasets[head]
                        target(f"{layer}:{dataset}.{tail}", (context, depth, *taken))
                    elif ref not in seen:
                        seen.add(ref)
                        queue.append((ref, depth + 1, site))
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
    lines.append("and that reach SDTM only through the filter of a row template.")
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
