"""The trace graph: built from hand-made plans, then checked with planted defects (rule R5)."""

from __future__ import annotations

import json

import pytest

from specfirst import kit as kits
from specfirst.machine import graph
from specfirst.machine.canonical import read_jsonl, write_json, write_jsonl
from specfirst.machine.runner import InputSource, SpecPlan

pa = pytest.importorskip("pyarrow")
pq = pytest.importorskip("pyarrow.parquet")

SHA = "c" * 64


def make_kit(tmp_path, gaps=None) -> kits.Kit:
    for name, columns in (("dm", ["USUBJID", "AGE", "ARM"]), ("vs", ["USUBJID", "VSSTRESN"])):
        path = tmp_path / "inputs/data/sdtm" / f"{name}.parquet"
        path.parent.mkdir(parents=True, exist_ok=True)
        pq.write_table(pa.table({column: pa.array([], pa.string()) for column in columns}), path)
    (tmp_path / "inputs/data/sdtm/define.xml").write_text(
        '<ODM>\n<ItemDef OID="DM.USUBJID"/>\n<ItemDef OID="DM.AGE"/>\n</ODM>\n', encoding="ascii"
    )
    files = [
        {"path": path, "source": "s", "from": path, "sha256": SHA}
        for path in ("inputs/data/sdtm/dm.parquet", "inputs/data/sdtm/vs.parquet",
                     "inputs/data/sdtm/define.xml", "gold/spec/project.yaml",
                     "gold/reference/adam/adsl.parquet")
    ]
    return kits.parse_kit({
        "kit": 0, "id": "demo", "title": "Demo", "tier": "A",
        "pins": {"engines": {"yamaa": "0"}, "sources": {"s": "d" * 40}},
        "build": {"project": "gold/spec/project.yaml", "sdtm": "inputs/data/sdtm",
                  "reference": "gold/reference/adam"},
        "documents": [{"id": "define-sdtm", "file": "inputs/data/sdtm/define.xml"}],
        "trace_gaps": gaps or {},
        "files": files,
    })


def plan(columns, outputs, origins=None, base="DM") -> SpecPlan:
    return SpecPlan(
        name="ADSL", entry="gold/spec/adsl.yaml", record={},
        specification={
            "base": base,
            "input": {"DM": {"path": "dm.parquet"}, "VS": {"path": "vs.parquet"}},
            "output": {"columns": outputs},
            "columns": columns,
        },
        origins=origins or {},
        inputs=(InputSource("DM", "sdtm", "DM", "inputs/data/sdtm/dm.parquet"),
                InputSource("VS", "sdtm", "VS", "inputs/data/sdtm/vs.parquet")),
    )


COLUMNS = [
    {"name": "USUBJID", "label": "Subject", "derivation": {"value": "DM.USUBJID"}},
    {"name": "AGE_N", "derivation": {"value": "DM.AGE"}},
    {"name": "AGEGR1", "derivation": {"value": {"case": [
        {"when": "AGE_N < 65", "then": "'<65'"}, {"otherwise": "'>=65'"}]}}},
    {"name": "AGEGR1N", "derivation": {"value": {"case": [
        {"when": "AGEGR1 = '<65'", "then": 1}, {"otherwise": 2}]}}},
    {"name": "STUDYID", "derivation": {"value": "'DEMO'"}},
    {"name": "HT", "derivation": {"value": "VS.VSSTRESN"}},
]
OUTPUTS = ["USUBJID", "AGEGR1", "AGEGR1N", "STUDYID", "HT"]
ORIGINS = {
    "": {"declaring_source": None, "source_kind": "composed"},
    "/columns/0/derivation": {"declaring_source": "gold/spec/adsl.yaml", "line": 12,
                              "source_kind": "authored"},
    "/columns/1": {"declaring_source": "gold/spec/parent.yaml", "line": 40,
                   "source_kind": "authored"},
    "/columns/2/derivation": {"declaring_source": "gold/spec/adsl.yaml", "line": 30,
                              "source_kind": "authored"},
}


def edge(result: graph.Graph, start: str, end: str) -> dict | None:
    return next((e for e in result.edges if (e["from"], e["to"]) == (start, end)), None)


def test_nodes_edges_and_sources(tmp_path):
    result = graph.build_graph(make_kit(tmp_path), tmp_path, [plan(COLUMNS, OUTPUTS, ORIGINS)])
    ids = [node["id"] for node in result.nodes]
    assert ids == sorted(ids)
    assert ids == [
        "adam:ADSL.AGEGR1", "adam:ADSL.AGEGR1N", "adam:ADSL.HT", "adam:ADSL.STUDYID",
        "adam:ADSL.USUBJID", "sdtm:DM.AGE", "sdtm:DM.USUBJID", "sdtm:VS.VSSTRESN",
    ]  # the helper AGE_N is not a node; DM.ARM is not read, so it is not a node
    nodes = {node["id"]: node for node in result.nodes}
    assert nodes["adam:ADSL.USUBJID"]["source"] == {"file": "gold/spec/adsl.yaml", "line": 12}
    assert nodes["adam:ADSL.USUBJID"]["label"] == "Subject"
    assert nodes["adam:ADSL.USUBJID"]["layer"] == "L4"
    # An SDTM column is defined in the Define-XML; without an entry there, in its data file.
    assert nodes["sdtm:DM.AGE"]["source"] == {"file": "inputs/data/sdtm/define.xml", "line": 3}
    assert nodes["sdtm:VS.VSSTRESN"]["source"] == {"file": "inputs/data/sdtm/vs.parquet",
                                                   "line": 1}
    # Through the helper: the edge names the line where DM.AGE is read.
    through = edge(result, "adam:ADSL.AGEGR1", "sdtm:DM.AGE")
    assert through == {"type": "derives_from", "from": "adam:ADSL.AGEGR1", "to": "sdtm:DM.AGE",
                       "proof": "static", "origin": "built",
                       "source": {"file": "gold/spec/parent.yaml", "line": 40}}
    # From one output column to another: the edge stops there.
    assert edge(result, "adam:ADSL.AGEGR1N", "adam:ADSL.AGEGR1") is not None
    assert edge(result, "adam:ADSL.AGEGR1N", "sdtm:DM.AGE") is None
    # No origin for that place: the specification file, line 1.
    assert edge(result, "adam:ADSL.HT", "sdtm:VS.VSSTRESN")["source"] == {
        "file": "gold/spec/adsl.yaml", "line": 1}


def test_coverage_reaches_sdtm_through_other_columns(tmp_path):
    result = graph.build_graph(make_kit(tmp_path), tmp_path, [plan(COLUMNS, OUTPUTS, ORIGINS)])
    coverage = {entry["column"]: entry for entry in result.coverage["columns"]}
    assert coverage["adam:ADSL.AGEGR1N"] == {
        "column": "adam:ADSL.AGEGR1N", "terminal": "sdtm", "sdtm": 1, "value": True,
        "inputs": ["sdtm:DM"], "gaps": []}
    assert coverage["adam:ADSL.STUDYID"]["terminal"] == "literal"
    assert coverage["adam:ADSL.STUDYID"]["value"] is False
    assert coverage["adam:ADSL.STUDYID"]["inputs"] == ["sdtm:DM"]  # rows of the base dataset


def hashes(tmp_path, kit, columns) -> dict[str, str]:
    result = graph.build_graph(kit, tmp_path, [plan(columns, OUTPUTS, ORIGINS)])
    return {node["id"]: node["hash"] for node in result.nodes}


def test_a_changed_rule_changes_the_hash_of_its_node_only(tmp_path):
    kit = make_kit(tmp_path)
    before = hashes(tmp_path, kit, COLUMNS)
    changed = [dict(column) for column in COLUMNS]
    changed[2] = {"name": "AGEGR1", "derivation": {"value": {"case": [
        {"when": "AGE_N < 70", "then": "'<70'"}, {"otherwise": "'>=70'"}]}}}
    after = hashes(tmp_path, kit, changed)
    assert {key for key in before if before[key] != after[key]} == {"adam:ADSL.AGEGR1"}


def test_a_changed_helper_changes_the_hash_of_the_column_that_reads_it(tmp_path):
    # The same edges and the same own rule, but another rule behind it.
    kit = make_kit(tmp_path)
    before = hashes(tmp_path, kit, COLUMNS)
    changed = [dict(column) for column in COLUMNS]
    changed[1] = {"name": "AGE_N", "derivation": {"value": "DM.AGE + 10"}}
    after = hashes(tmp_path, kit, changed)
    assert {key for key in before if before[key] != after[key]} == {"adam:ADSL.AGEGR1"}


ROW_ORIGINS = {
    "/rows/0": {"declaring_source": "gold/spec/adsl.yaml", "line": 90, "source_kind": "authored"},
    "/intermediates/0": {"declaring_source": "gold/spec/adsl.yaml", "line": 50,
                         "source_kind": "authored"},
    "/columns/0/derivation": {"declaring_source": "gold/spec/adsl.yaml", "line": 60,
                              "source_kind": "authored"},
    "/columns/2/derivation": {"declaring_source": "gold/spec/adsl.yaml", "line": 70,
                              "source_kind": "authored"},
}


def with_rows() -> SpecPlan:
    """A specification with a row template that filters, and a lookup."""
    result = plan(
        [
            {"name": "USUBJID", "derivation": {"value": "DM.USUBJID"}},
            {"name": "FLAG", "derivation": {"value": "'Y'"}},
            {"name": "HT", "derivation": {"value": "BASE.VSSTRESN"}},
        ],
        ["USUBJID", "FLAG", "HT"],
        ROW_ORIGINS,
    )
    result.specification["rows"] = [
        {"id": "treated", "dataset": "DM", "filter": "DM.ARM <> 'Screen Failure'",
         "derivations": {}}]
    result.specification["intermediates"] = [
        {"id": "BASE", "dataset": "VS", "key": ["USUBJID"], "keep": "first"}]
    return result


def test_value_and_context_dependencies(tmp_path):
    result = graph.build_graph(make_kit(tmp_path), tmp_path, [with_rows()])
    coverage = {entry["column"]: entry for entry in result.coverage["columns"]}
    # FLAG is a literal on filtered rows: it reaches SDTM, but not by its own rule.
    assert coverage["adam:ADSL.FLAG"]["terminal"] == "sdtm"
    assert coverage["adam:ADSL.FLAG"]["value"] is False
    assert coverage["adam:ADSL.HT"]["value"] is True
    # A column taken through a lookup is cited where the rule names it (line 70),
    # not at the declaration of the lookup (line 50).
    assert edge(result, "adam:ADSL.HT", "sdtm:VS.VSSTRESN")["source"]["line"] == 70
    # The key of the lookup is read at its declaration, the row filter at the row template.
    assert edge(result, "adam:ADSL.HT", "sdtm:VS.USUBJID")["source"]["line"] == 50
    assert edge(result, "adam:ADSL.HT", "sdtm:DM.ARM")["source"]["line"] == 90
    # A rule is preferred to a row template or a lookup as the place of an edge.
    assert edge(result, "adam:ADSL.USUBJID", "sdtm:DM.USUBJID")["source"]["line"] == 60


def test_a_gap_is_passed_on_to_the_columns_that_read_it(tmp_path, root):
    """Review of real-1, finding F2: AGEGR1N reads only AGEGR1, which has a gap."""
    kit = make_kit(tmp_path)
    result = graph.build_graph(kit, tmp_path, [plan(bad(2, "AGE_TYPO < 65"), OUTPUTS, ORIGINS)])
    coverage = {entry["column"]: entry for entry in result.coverage["columns"]}
    assert coverage["adam:ADSL.AGEGR1"]["terminal"] == "gap"
    assert coverage["adam:ADSL.AGEGR1N"]["terminal"] == "gap"
    assert coverage["adam:ADSL.AGEGR1N"]["gaps"] == ["reads adam:ADSL.AGEGR1, which has a gap"]
    assert coverage["adam:ADSL.USUBJID"]["terminal"] == "sdtm"
    graph.write_graph(tmp_path / "graph", result)
    expected = {"ADSL": OUTPUTS}
    # Listing the gap of AGEGR1 alone is not enough.
    _, problems = graph.check_graph(root, tmp_path / "graph", expected,
                                    {"adam:ADSL.AGEGR1": "known"})
    assert len(problems) == 1 and problems[0].startswith(
        "adam:ADSL.AGEGR1N: gap with no listed reason")
    lines, problems = graph.check_graph(
        root, tmp_path / "graph", expected,
        {"adam:ADSL.AGEGR1": "known", "adam:ADSL.AGEGR1N": "behind AGEGR1"})
    assert problems == [] and "ADSL            5       2       0       1     2" in lines
    # A coverage file that calls the reading column complete does not pass either.
    with open(tmp_path / "graph" / "coverage.json", encoding="ascii") as handle:
        recorded = json.load(handle)
    for entry in recorded["columns"]:
        if entry["column"] == "adam:ADSL.AGEGR1N":
            entry.update(terminal="literal", gaps=[])
    write_json(tmp_path / "graph" / "coverage.json", recorded)
    _, problems = graph.check_graph(root, tmp_path / "graph", expected,
                                    {"adam:ADSL.AGEGR1": "known"})
    assert problems == ["adam:ADSL.AGEGR1N: recorded as complete, but it reads "
                        "adam:ADSL.AGEGR1, which has a gap"]


def bad(index: int, value) -> list[dict]:
    columns = [dict(column) for column in COLUMNS]
    columns[index] = {"name": columns[index]["name"], "derivation": {"value": value}}
    return columns


@pytest.mark.parametrize(
    ("columns", "reason"),
    [
        (bad(5, "VS.NO_SUCH_COLUMN"), "unresolved reference VS.NO_SUCH_COLUMN"),
        (bad(5, "HEIGTH_RAW * 2"), "unknown name HEIGTH_RAW"),
        ([*COLUMNS[:5], {"name": "HT"}], "no derivation in the specification"),
    ],
)
def test_planted_gap_is_recorded_and_fails_the_check(tmp_path, root, columns, reason):
    kit = make_kit(tmp_path)
    result = graph.build_graph(kit, tmp_path, [plan(columns, OUTPUTS, ORIGINS)])
    entry = next(e for e in result.coverage["columns"] if e["column"] == "adam:ADSL.HT")
    assert entry["terminal"] == "gap" and reason in entry["gaps"][0]
    graph.write_graph(tmp_path / "graph", result)
    lines, problems = graph.check_graph(root, tmp_path / "graph", {"ADSL": OUTPUTS}, {})
    assert len(problems) == 1 and "gap with no listed reason" in problems[0]
    # A gap the kit lists with its reason passes, and is printed.
    lines, problems = graph.check_graph(
        root, tmp_path / "graph", {"ADSL": OUTPUTS}, {"adam:ADSL.HT": "not built yet"}
    )
    assert problems == [] and any("listed: not built yet" in line for line in lines)


@pytest.fixture
def written(tmp_path):
    result = graph.build_graph(make_kit(tmp_path), tmp_path, [plan(COLUMNS, OUTPUTS, ORIGINS)])
    graph.write_graph(tmp_path / "graph", result)
    return tmp_path / "graph"


def test_complete_graph_passes(written, root):
    sdtm = {"DM": {"USUBJID", "AGE", "ARM"}, "VS": {"USUBJID", "VSSTRESN"}}
    lines, problems = graph.check_graph(root, written, {"ADSL": OUTPUTS}, {}, sdtm)
    assert problems == []
    assert "dataset   columns to SDTM by rows literal  gaps" in lines
    assert "ADSL            5       4       0       1     0" in lines
    assert "nodes: L3 3, L4 5" in lines
    assert "literal columns sit on rows of: sdtm:DM (1)" in lines
    assert "cites edges: 0 imported, 0 with a verified quote, 0 approved by a person" in lines


def test_an_sdtm_node_must_be_a_column_of_the_kit(written, root):
    """Review of real-1, finding F6: a node and an edge for a column that does not exist."""
    rewrite(written, "nodes.jsonl", lambda nodes: [*nodes, {
        "id": "sdtm:ZZ.NOSUCH", "layer": "L3", "hash": "0" * 64,
        "source": {"file": "inputs/data/sdtm/zz.parquet", "line": 1}}])
    sdtm = {"DM": {"USUBJID", "AGE", "ARM"}, "VS": {"USUBJID", "VSSTRESN"}}
    _, problems = graph.check_graph(root, written, {"ADSL": OUTPUTS}, {}, sdtm)
    assert problems == ["node sdtm:ZZ.NOSUCH: not a column of the kit's SDTM data"]
    _, problems = graph.check_graph(root, written, {"ADSL": OUTPUTS}, {}, {"DM": {"AGE"}})
    assert "node sdtm:DM.USUBJID: not a column of the kit's SDTM data" in problems


def test_the_cites_line_counts_what_the_edges_say(written, root):
    """Review of real-1, finding F6: the words after the count were fixed text."""
    def add(edges):
        return sorted([*edges, {
            "type": "cites", "from": "adam:ADSL.HT", "to": "doc:sap#p1", "proof": "judged",
            "origin": "imported", "quote_verified": True, "approved_by": "nobody"}],
            key=lambda e: (e["type"], e["from"], e["to"]))

    rewrite(written, "edges.jsonl", add)
    rewrite(written, "nodes.jsonl", lambda nodes: sorted([*nodes, {
        "id": "doc:sap#p1", "layer": "L0", "hash": "0" * 64,
        "source": {"file": "inputs/docs/sap.pdf", "line": 1}}], key=lambda n: n["id"]))
    lines, problems = graph.check_graph(root, written, {"ADSL": OUTPUTS}, {})
    assert problems == []
    assert "cites edges: 1 imported, 1 with a verified quote, 1 approved by a person" in lines


def rewrite(folder, name, change):
    records = read_jsonl(folder / name)
    write_jsonl(folder / name, change(records))


def test_a_listed_gap_that_is_no_gap_fails(written, root):
    _, problems = graph.check_graph(root, written, {"ADSL": OUTPUTS}, {"adam:ADSL.HT": "old"})
    assert problems == ["adam:ADSL.HT: listed as a gap in the kit, but it has none"]


def test_an_output_column_without_a_node_fails(written, root):
    _, problems = graph.check_graph(root, written, {"ADSL": [*OUTPUTS, "NEWCOL"]}, {})
    assert problems == ["adam:ADSL.NEWCOL: an output column with no node or no coverage entry"]


# The next two tests change one of the two files, so they show that the check
# compares the files. They are not the case of a reference the analysis
# missed, which leaves both files agreeing (review of real-1, finding F4):
# tests/pilot A4-unread tests that case against the engine.
def test_a_removed_edge_fails(written, root):
    rewrite(written, "edges.jsonl", lambda edges: [e for e in edges if e["from"] != "adam:ADSL.HT"])
    _, problems = graph.check_graph(root, written, {"ADSL": OUTPUTS}, {})
    assert "adam:ADSL.HT: no derives_from path to an SDTM column" in problems
    assert "adam:ADSL.HT: coverage.json disagrees with edges.jsonl" in problems


def test_a_column_wrongly_recorded_as_literal_fails(written, root):
    with open(written / "coverage.json", encoding="ascii") as handle:
        coverage = json.load(handle)
    for entry in coverage["columns"]:
        if entry["column"] == "adam:ADSL.HT":
            entry.update(terminal="literal", sdtm=0)
    write_json(written / "coverage.json", coverage)
    _, problems = graph.check_graph(root, written, {"ADSL": OUTPUTS}, {})
    assert problems == ["adam:ADSL.HT: coverage.json disagrees with edges.jsonl"]


def test_schema_order_and_dangling_edges_are_checked(written, root):
    def spoil(edges):
        edges[0]["proof"] = "judged"  # only cites may be judged
        edges.append({"type": "derives_from", "from": "adam:ADSL.HT", "to": "sdtm:XX.NONE",
                      "proof": "static"})
        return list(reversed(edges))

    rewrite(written, "edges.jsonl", spoil)
    _, problems = graph.check_graph(root, written, {"ADSL": OUTPUTS}, {})
    text = "\n".join(problems)
    assert "is not one of ['executed', 'static']" in text
    assert "sdtm:XX.NONE is not a node" in text
    assert "edges.jsonl is not sorted" in text


def test_claims_become_imported_judged_cites_edges(tmp_path):
    claims = {"dataset": "ADSL", "claims": [
        {"variable": "AGEGR1", "citations": [
            {"document": "the/define.xml", "section": "DM.AGE", "quote": "q"},
            {"document": "the/define.xml", "section": "page 4", "quote": "q"},
            {"document": "the/define.xml", "section": "page 4", "quote": "again"},
            {"document": "a/program.sas", "section": "L1", "quote": "q"}]},
        {"variable": "AGE_N", "citations": [{"document": "the/define.xml", "section": "x"}]},
    ]}
    path = tmp_path / "gold/claims/adsl-claims.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(claims, indent=2) + "\n", encoding="ascii")
    data = {
        "kit": 0, "id": "demo", "title": "Demo", "tier": "A",
        "pins": {"engines": {"yamaa": "0"}, "sources": {"s": "d" * 40}},
        "build": {"project": "gold/spec/project.yaml", "sdtm": "inputs/data/sdtm",
                  "reference": "gold/reference/adam", "claims": "gold/claims"},
        "documents": [{"id": "define-sdtm", "file": "inputs/data/sdtm/define.xml",
                       "cited_as": ["the/define.xml"]}],
        "files": [{"path": p, "source": "s", "from": p, "sha256": SHA} for p in (
            "inputs/data/sdtm/dm.parquet", "inputs/data/sdtm/define.xml",
            "gold/spec/project.yaml", "gold/reference/adam/adsl.parquet",
            "gold/claims/adsl-claims.json")],
    }
    make_kit(tmp_path)
    result = graph.build_graph(kits.parse_kit(data), tmp_path, [plan(COLUMNS, OUTPUTS, ORIGINS)])
    cites = [e for e in result.edges if e["type"] == "cites"]
    assert [(e["from"], e["to"]) for e in cites] == [
        ("adam:ADSL.AGEGR1", "doc:define-sdtm#DM.AGE"),
        ("adam:ADSL.AGEGR1", "doc:define-sdtm#page%204"),
    ]
    assert all(e["proof"] == "judged" and e["origin"] == "imported"
               and e["quote_verified"] is False and e["approved_by"] is None for e in cites)
    assert cites[0]["source"] == {"file": "gold/claims/adsl-claims.json", "line": 5}
    nodes = {n["id"]: n for n in result.nodes}
    assert nodes["doc:define-sdtm#DM.AGE"]["layer"] == "L0"
    assert nodes["doc:define-sdtm#DM.AGE"]["source"] == {
        "file": "inputs/data/sdtm/define.xml", "line": 3}  # the ItemDef of that name
    assert nodes["doc:define-sdtm#page%204"]["source"]["line"] == 1
    # Three citations of the kit's document; two of them name the same span.
    assert result.coverage["claims"]["ADSL"] == {
        "file": "gold/claims/adsl-claims.json", "claims": 2,
        "citations_of_kit_documents": 3, "cites_edges": 2,
        "citations_not_to_kit_documents": {"a/program.sas": 1},
        "variables_not_output_columns": ["AGE_N"],
    }


def test_claims_for_another_dataset_are_refused(tmp_path):
    path = tmp_path / "gold/claims/adsl-claims.json"
    path.parent.mkdir(parents=True)
    path.write_text('{"dataset": "ADAE", "claims": []}\n', encoding="ascii")
    kit = make_kit(tmp_path)
    data_kit = kits.Kit(**{**kit.__dict__, "claims": "gold/claims", "files": (
        *kit.files, kits.KitFile("gold/claims/adsl-claims.json", "s", "x", SHA))})
    with pytest.raises(graph.GraphError, match="claims are for dataset 'ADAE'"):
        graph.build_graph(data_kit, tmp_path, [plan(COLUMNS, OUTPUTS, ORIGINS)])
