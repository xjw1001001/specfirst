"""The SDTM to ADaM part of the trace graph (PLAN.md sections 4.1, 4.2 and 7.5).

Nodes: one per ADaM output column (layer L4) and one per SDTM column that a
specification reads (layer L3). Edges: `derives_from`, static, from an ADaM
column to the ADaM or SDTM columns its rule reads, each with the file and
line of the place in the specification where the column is read. Helper
columns, intermediates and row templates are not nodes: an edge goes through
them, and its line is the nearest place on the way that reads the target.

Pilot 7's reviewed claims are taken over as candidate `cites` edges from
ADaM columns to document spans (layer L0). They are judged edges, marked
imported, with no verified quote and no approval (section 4.2).

The graph has no node for a literal. A column whose rule reads no column at
all is recorded in coverage.json as `literal`, with the declared inputs
whose rows it is built on.
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
from specfirst.machine.lineage import Lineage, Read, column_dependencies
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


@dataclass
class _Trace:
    targets: dict[str, tuple[int, str, int]] = field(default_factory=dict)  # id -> depth, site
    inputs: set[str] = field(default_factory=set)
    gaps: set[str] = field(default_factory=set)


def _trace_column(
    plan: SpecPlan, lineage: Lineage, by_element: dict[str, list[Read]], name: str,
    datasets: dict[str, tuple[str, str]],
) -> _Trace:
    """Follow one output column through helpers, intermediates and row templates."""
    outputs = set(lineage.outputs)
    intermediates = {item["id"]: item["dataset"] for item in plan.specification.get(
        "intermediates", [])}
    rows = {row["id"]: row["dataset"] for row in plan.specification.get("rows", [])}
    trace = _Trace()
    if name not in lineage.defined:
        trace.gaps.add("no derivation in the specification")

    def whole(alias: str) -> None:
        alias = intermediates.get(alias, alias)
        if alias in datasets:
            layer, dataset = datasets[alias]
            trace.inputs.add(f"{layer}:{dataset}")

    def target(node: str, depth: int, site: tuple[str, int]) -> None:
        found = (depth, *site)
        if node not in trace.targets or found < trace.targets[node]:
            trace.targets[node] = found

    if not rows:  # without row templates, every row comes from the base dataset
        whole(plan.specification.get("base") or "")

    start = f"spec.{name}"
    seen, queue = {start}, deque([(start, 0)])
    while queue:
        element, depth = queue.popleft()
        if element.startswith("row."):
            whole(rows.get(element[4:], ""))
        for read in by_element.get(element, []):
            site = _site(plan, read.pointer)
            trace.gaps |= {f"unresolved reference {ref} at {site[0]}:{site[1]}"
                           for ref in read.unresolved}
            trace.gaps |= {f"unknown name {ref} at {site[0]}:{site[1]}" for ref in read.unknown}
            for alias in read.whole:
                whole(alias)
            for ref in sorted(read.refs):
                head, _, tail = ref.partition(".")
                if head == "spec" and tail in outputs and tail != name:
                    target(adam_id(plan.name, tail), depth, site)
                elif head in datasets and head not in ("spec", "row", "intermediate"):
                    layer, dataset = datasets[head]
                    target(f"{layer}:{dataset}.{tail}", depth, site)
                elif ref not in seen:
                    seen.add(ref)
                    queue.append((ref, depth + 1))
    return trace


def _reach(edges: list[dict]) -> dict[str, set[str]]:
    """For every node with a derives_from edge: the SDTM columns it reaches."""
    following: dict[str, set[str]] = {}
    for edge in edges:
        if edge["type"] == "derives_from":
            following.setdefault(edge["from"], set()).add(edge["to"])
    reach: dict[str, set[str]] = {}
    for start in following:
        seen, stack, found = {start}, [start], set()
        while stack:
            for nxt in following.get(stack.pop(), ()):
                if nxt.startswith("sdtm:"):
                    found.add(nxt)
                elif nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        reach[start] = found
    return reach


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
            file, line = _site(plan, _definition_place(plan, lineage, name))
            nodes[node] = {
                "id": node, "layer": "L4", "kind": "variable",
                "hash": content_hash(_column_content(plan.specification, name)),
                "source": {"file": file, "line": line},
            }
            if labels.get(name):
                nodes[node]["label"] = labels[name]
            trace = _trace_column(plan, lineage, by_element, name, datasets)
            traces[node] = trace
            for to, (_, file, line) in trace.targets.items():
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
    reach = _reach(ordered_edges)
    columns = []
    for node in sorted(traces):
        trace = traces[node]
        reached = len(reach.get(node, ()))
        terminal = "gap" if trace.gaps else "sdtm" if reached else "literal"
        columns.append({
            "column": node, "terminal": terminal, "sdtm": reached,
            "inputs": sorted(trace.inputs), "gaps": sorted(trace.gaps),
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
        taken, not_documents, not_columns = 0, Counter(), set()
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
            "file": file, "claims": len(claims), "cites_edges": taken,
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
    root: Path, folder: Path, expected: dict[str, list[str]], accepted_gaps: dict[str, str]
) -> tuple[list[str], list[str]]:
    """Check the written graph against the gate of real-1 (PLAN.md section 13.3).

    expected: the output columns of every dataset, taken from the built data.
    accepted_gaps: column ID -> reason, for gaps the kit lists.
    Returns the lines of the report and the problems. Reachability is
    computed here from edges.jsonl, not taken from coverage.json.
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

    reach = _reach(edges)
    recorded = {entry["column"]: entry for entry in coverage.get("columns", [])}
    wanted = {adam_id(dataset, column) for dataset, columns in expected.items()
              for column in columns}
    for extra in sorted(set(recorded) - wanted):
        problems.append(f"{extra}: in coverage.json but not an output column of the built data")
    lines.append(f"{'dataset':9s} {'columns':>7s} {'to SDTM':>7s} {'literal':>7s} {'gaps':>5s}")
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
            reached = len(reach.get(node, ()))
            if entry["gaps"]:
                count["gaps"] += 1
                reason = accepted_gaps.get(node)
                detail = "; ".join(entry["gaps"])
                if reason:
                    lines.append(f"  gap {node}: {detail} (listed: {reason})")
                else:
                    problems.append(f"{node}: gap with no listed reason: {detail}")
            elif reached:
                count["sdtm"] += 1
            elif entry["terminal"] == "literal":
                count["literal"] += 1
            else:
                problems.append(f"{node}: no derives_from path to an SDTM column")
                count["gaps"] += 1
            if reached != entry["sdtm"] or (not entry["gaps"] and entry["terminal"] != (
                    "sdtm" if reached else "literal")):
                problems.append(f"{node}: coverage.json disagrees with edges.jsonl")
        totals.update(count)
        lines.append(f"{dataset:9s} {len(columns):7d} {count['sdtm']:7d} {count['literal']:7d} "
                     f"{count['gaps']:5d}")
    total = sum(len(columns) for columns in expected.values())
    lines.append(f"{'TOTAL':9s} {total:7d} {totals['sdtm']:7d} {totals['literal']:7d} "
                 f"{totals['gaps']:5d}")
    for node in sorted(set(accepted_gaps) - {c for c, e in recorded.items() if e["gaps"]}):
        problems.append(f"{node}: listed as a gap in the kit, but it has none")
    by_layer = Counter(node["layer"] for node in nodes)
    by_type = Counter(edge["type"] for edge in edges)
    imported = sum(1 for edge in edges if edge.get("origin") == "imported")
    lines.append("nodes: " + ", ".join(f"{k} {v}" for k, v in sorted(by_layer.items())))
    lines.append("edges: " + ", ".join(f"{k} {v}" for k, v in sorted(by_type.items()))
                 + f" ({imported} imported, judged, not verified, not approved)")
    literal = [entry for entry in coverage.get("columns", []) if entry["terminal"] == "literal"]
    if literal:
        on = Counter(", ".join(entry["inputs"]) or "no declared input" for entry in literal)
        lines.append("literal columns sit on rows of: "
                     + "; ".join(f"{k} ({v})" for k, v in sorted(on.items())))
    return lines, problems
