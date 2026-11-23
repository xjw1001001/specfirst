"""The trace from the cells of a grid to SDTM columns (PLAN.md sections 4.2 and 4.6, P3).

The graph below the ADaM columns is made by hand: five ADaM columns of the
made-up study, each derived from one SDTM column. The cells, the ARD rows
and the analyses are those of tests/toy_displays.py. The check must pass on
them and fail on every planted gap (rule R5).
"""

from __future__ import annotations

import copy
import json

import pytest
import toy_displays as displays
import toy_results as toy

from specfirst import schemas
from specfirst.machine import ars, graph, grid, layout
from specfirst.machine.canonical import content_hash, read_jsonl, write_json, write_jsonl

ADAM = {"ADSL.USUBJID": "DM.USUBJID", "ADSL.ARM": "DM.ARM", "ADSL.SAFFL": "EX.EXDOSE",
        "ADAE.USUBJID": "AE.USUBJID", "ADAE.TRTEMFL": "AE.AESTDTC"}


def below(columns: dict[str, str] | None = None, gaps: dict[str, list[str]] | None = None):
    """A graph of ADaM columns, each derived from one SDTM column."""
    columns = ADAM if columns is None else columns
    nodes, edges, coverage = [], [], []
    for adam, sdtm in sorted(columns.items()):
        for name, layer in ((f"adam:{adam}", "L4"), (f"sdtm:{sdtm}", "L3")):
            nodes.append({"id": name, "layer": layer, "kind": "variable",
                          "hash": content_hash(name), "source": {"file": "spec.yaml", "line": 1}})
        edges.append({"type": "derives_from", "from": f"adam:{adam}", "to": f"sdtm:{sdtm}",
                      "proof": "static", "origin": "built",
                      "source": {"file": "spec.yaml", "line": 1}})
        found = (gaps or {}).get(adam, [])
        coverage.append({"column": f"adam:{adam}", "terminal": "gap" if found else "sdtm",
                         "sdtm": 1, "value": True, "inputs": [], "gaps": found})
    return graph.Graph(nodes=sorted(nodes, key=lambda n: n["id"]), edges=edges,
                       coverage={"columns": coverage, "claims": {}})


@pytest.fixture(scope="module")
def built(root, tmp_path_factory):
    """The made-up output: its event file, its ARD rows in file order, and its grid."""
    folder = tmp_path_factory.mktemp("cells")
    data = displays.event_data()
    (folder / "event.json").write_text(json.dumps(data, indent=1), encoding="ascii")
    event = ars.index(data)
    rows = toy.run(root, data)
    made = grid.build(event, layout.parse(displays.layout_data()), rows)
    return folder, event, list(rows.values()), made


def display(built, made=None) -> graph.Display:
    folder, event, rows, value = built
    return graph.Display(grid=made or value, grid_file="gold/grid/Out_AE.json", event=event,
                         ars_file="event.json", ard_file="gold/ard/toy.jsonl", rows=rows,
                         subject_key="USUBJID")


def traced(built, tmp_path, lower=None, made=None):
    """The graph with the cells added, written; and what the check says of it."""
    folder, _, _, value = built
    result = lower or below()
    graph.add_displays(result, folder, [display(built, made)])
    graph.write_graph(tmp_path, result)
    return result, graph.check_cells(tmp_path, {displays.OUTPUT: made or value})


@pytest.mark.parametrize(("left_out", "message"), [
    # One reads edge that the analysis of the denominator (A_N) covers.
    (("reads", "ars:A_TEAE", "adam:ADSL.SAFFL"), "ars:A_TEAE: its reads edges are"),
    # The computes edge of one percent to the analysis of its denominator.
    (("computes", "ard:A_TEAE/M_CAT_pct/Arm_B", "ars:A_N"),
     "ard:A_TEAE/M_CAT_pct/Arm_B: its computes edges go to ['ars:A_TEAE']"),
])
def test_every_edge_is_held_against_the_ars_file(built, tmp_path, left_out, message):
    """The review of real-3a, F4: with the events, a single edge left out is seen; without
    them, the walk still finds a complete path, as it did."""
    folder, event, _, made = built
    result = below()
    graph.add_displays(result, folder, [display(built)])
    events = {displays.OUTPUT: (event, "USUBJID")}
    graph.write_graph(tmp_path, result)
    assert graph.check_cells(tmp_path, {displays.OUTPUT: made}, events)[1] == []
    result.edges = [edge for edge in result.edges
                    if (edge["type"], edge["from"], edge["to"]) != left_out]
    graph.write_graph(tmp_path, result)
    assert graph.check_cells(tmp_path, {displays.OUTPUT: made})[1] == []
    problems = graph.check_cells(tmp_path, {displays.OUTPUT: made}, events)[1]
    assert any(message in problem for problem in problems), problems
    # The reads coverage.json records are held against the edges too.
    result = below()
    graph.add_displays(result, folder, [display(built)])
    entry = result.coverage["analyses"]["ars:A_TEAE"]
    entry["reads"] = entry["reads"][:1]
    graph.write_graph(tmp_path, result)
    assert any("ars:A_TEAE: coverage.json records the reads" in problem for problem in
               graph.check_cells(tmp_path, {displays.OUTPUT: made}, events)[1])


def test_cells_reach_sdtm_columns_through_results_analyses_and_adam_columns(root, built,
                                                                           tmp_path):
    result, (lines, problems) = traced(built, tmp_path)
    assert problems == []
    assert lines == [
        "grid Out_AE: 9 cells, 9 print a number; 9 of the 9 cells with results have a complete "
        "path to SDTM columns",
        "  through 15 ARD rows, 3 analyses, 5 ADaM columns, to 5 SDTM columns"]
    for part, records in (("node", result.nodes), ("edge", result.edges)):
        validator = schemas.validator("graph", part, root)
        assert all(list(validator.iter_errors(record)) == [] for record in records)
    assert result.nodes == sorted(result.nodes, key=lambda n: n["id"])
    assert result.edges == sorted(result.edges, key=lambda e: (e["type"], e["from"], e["to"]))
    by_type: dict[str, list] = {}
    for edge in result.edges:
        by_type.setdefault(edge["type"], []).append((edge["from"], edge["to"]))
    # A percent is computed from its own analysis and from that of its denominator.
    assert (len(by_type["shows"]), len(by_type["computes"]), len(by_type["reads"])) == (15, 21, 12)
    assert ("ard:A_TEAE/M_CAT_pct/Arm_B", "ars:A_N") in by_type["computes"]
    assert ("ard:A_TEAE/M_CAT_n/Arm_B", "ars:A_N") not in by_type["computes"]
    assert sorted(to for start, to in by_type["reads"] if start == "ars:A_TEAE") == [
        "adam:ADAE.TRTEMFL", "adam:ADAE.USUBJID", "adam:ADSL.ARM", "adam:ADSL.SAFFL",
        "adam:ADSL.USUBJID"]
    nodes = {node["id"]: node for node in result.nodes}
    assert nodes["cell:Out_AE/r3/c2"] == {
        "id": "cell:Out_AE/r3/c2", "layer": "L7", "kind": "cell", "label": "2 ( 66.7)",
        "hash": content_hash({"text": "2 ( 66.7)", "ard": ["ard:A_TEAE/M_CAT_n/Arm_B",
                                                          "ard:A_TEAE/M_CAT_pct/Arm_B"]}),
        "source": {"file": "gold/grid/Out_AE.json", "line": 1}}
    # A result is at its line of the ARD file, an analysis at the line of its ID.
    row = nodes["ard:A_TEAE/M_CAT_n/Arm_B"]
    assert row["layer"] == "L6" and row["source"]["file"] == "gold/ard/toy.jsonl"
    assert [r["id"] for r in built[2]][row["source"]["line"] - 1] == row["id"]
    analysis = nodes["ars:A_TEAE"]
    text = (built[0] / "event.json").read_text("ascii").splitlines()
    assert text[analysis["source"]["line"] - 1].strip() == '"id": "A_TEAE",'
    assert analysis["layer"] == "L5" and analysis["label"] == "A_TEAE"
    assert result.coverage["displays"][displays.OUTPUT] == {
        "grid": "gold/grid/Out_AE.json", "cells": 9, "numeric": 9, "complete": 9, "results": 15,
        "analyses": ["A_AE", "A_N", "A_TEAE"], "sdtm": 5, "gaps": []}
    assert result.coverage["analyses"]["ars:A_N"] == {"not_built": [], "reads": [
        {"column": "adam:ADSL.ARM", "roles": ["grouping"]},
        {"column": "adam:ADSL.SAFFL", "roles": ["set"]},
        {"column": "adam:ADSL.USUBJID", "roles": ["key", "variable"]}]}


def test_the_analyses_a_result_is_computed_from(built):
    event = built[1]
    assert graph.referenced_analyses(event, event.analyses["A_TEAE"], "M_CAT_pct") == [
        "A_N", "A_TEAE"]
    assert graph.referenced_analyses(event, event.analyses["A_TEAE"], "M_CAT_n") == []
    assert graph.ars_id("An 1/x") == "ars:An%201%2Fx"


def rewrite(folder, name, keep):
    write_jsonl(folder / name, [record for record in read_jsonl(folder / name) if keep(record)])


@pytest.mark.parametrize(
    ("name", "keep", "message", "cells"),
    [
        ("edges.jsonl", lambda e: (e["type"], e["to"]) != ("shows", "ard:A_TEAE/M_CAT_n/Arm_B"),
         "cell:Out_AE/r3/c2: its shows edges are not the ARD rows of the cell", 1),
        ("edges.jsonl", lambda e: (e["type"], e["from"]) != (
            "computes", "ard:A_TEAE/M_CAT_n/Arm_B"),
         "cell:Out_AE/r3/c2: ard:A_TEAE/M_CAT_n/Arm_B has no computes edge", 1),
        ("edges.jsonl", lambda e: (e["type"], e["from"], e["to"]) != (
            "computes", "ard:A_TEAE/M_CAT_pct/Arm_B", "ars:A_TEAE"),
         "cell:Out_AE/r3/c2: ard:A_TEAE/M_CAT_pct/Arm_B has no computes edge to its own "
         "analysis", 1),
        ("edges.jsonl", lambda e: (e["type"], e["from"]) != ("reads", "ars:A_AE"),
         "cell:Out_AE/r2/c1: ars:A_AE has no node or no reads edge", 3),
        ("nodes.jsonl", lambda n: n["id"] != "ard:A_N/M_N_n/Arm_C",
         "cell:Out_AE/r1/c3: ard:A_N/M_N_n/Arm_C has no node", 1),
        ("nodes.jsonl", lambda n: n["id"] != "ars:A_N",
         "cell:Out_AE/r1/c1: ars:A_N has no node or no reads edge", 9),
        ("nodes.jsonl", lambda n: n["id"] != "cell:Out_AE/r1/c1",
         "cell:Out_AE/r1/c1: the cell has no node", 1),
        ("nodes.jsonl", lambda n: n["id"] != "sdtm:DM.ARM",
         "cell:Out_AE/r1/c1: sdtm:DM.ARM is not a node", 9),
        ("edges.jsonl", lambda e: e["type"] != "derives_from",
         "cell:Out_AE/r1/c1: ars:A_N reaches no SDTM column", 9),
    ],
)
def test_a_planted_gap_in_the_graph_files_fails_the_check(built, tmp_path, name, keep, message,
                                                          cells):
    _, (_, problems) = traced(built, tmp_path)
    assert problems == []
    rewrite(tmp_path, name, keep)
    lines, problems = graph.check_cells(tmp_path, {displays.OUTPUT: built[3]})
    assert message in problems, problems
    assert f"{9 - cells} of the 9 cells with results have a complete path" in lines[0]
    assert "grid Out_AE: coverage.json disagrees with the graph files" in problems


def test_a_gap_of_an_adam_column_is_a_gap_of_every_cell_behind_it(built, tmp_path):
    lower = below(gaps={"ADAE.TRTEMFL": ["unresolved reference x"]})
    result, (lines, problems) = traced(built, tmp_path, lower)
    assert problems == [f"cell:Out_AE/r3/c{n}: adam:ADAE.TRTEMFL has a gap" for n in (1, 2, 3)]
    assert "6 of the 9 cells with results have a complete path" in lines[0]
    entry = result.coverage["displays"][displays.OUTPUT]
    assert entry["complete"] == 6 and entry["gaps"] == problems


def test_a_column_that_no_specification_builds_is_a_gap(built, tmp_path):
    lower = below({key: value for key, value in ADAM.items() if key != "ADAE.TRTEMFL"})
    result, (_, problems) = traced(built, tmp_path, lower)
    assert problems == [f"cell:Out_AE/r3/c{n}: ars:A_TEAE reads adam:ADAE.TRTEMFL, which the "
                        "kit does not build" for n in (1, 2, 3)]
    assert result.coverage["analyses"]["ars:A_TEAE"]["not_built"] == ["adam:ADAE.TRTEMFL"]
    assert not any(edge["to"] == "adam:ADAE.TRTEMFL" for edge in result.edges)


def test_a_printed_number_without_a_result_behind_it_fails(built, tmp_path):
    made = copy.deepcopy(built[3])
    made["rows"][1]["cells"][0].update(text="5 (12.5)", ard=[])
    _, (lines, problems) = traced(built, tmp_path, made=made)
    assert problems == ["cell:Out_AE/r2/c1: prints '5 (12.5)' and shows no ARD row"]
    assert "8 of the 8 cells with results" in lines[0]
    # A cell without a number and without a result is no problem: a label, a blank.
    made["rows"][1]["cells"][0]["text"] = "-"
    assert traced(built, tmp_path, made=made)[1][1] == []


def test_a_result_that_is_not_in_the_ard_file_is_a_gap(built, tmp_path):
    folder, event, rows, made = built
    fewer = [row for row in rows if row["id"] != "ard:A_TEAE/M_CAT_n/Arm_B"]
    result = below()
    graph.add_displays(result, folder, [graph.Display(
        grid=made, grid_file="gold/grid/Out_AE.json", event=event, ars_file="event.json",
        ard_file="gold/ard/toy.jsonl", rows=fewer, subject_key="USUBJID")])
    graph.write_graph(tmp_path, result)
    assert result.coverage["displays"][displays.OUTPUT]["gaps"] == [
        "cell:Out_AE/r3/c2 shows ard:A_TEAE/M_CAT_n/Arm_B, which is not in gold/ard/toy.jsonl"]
    _, problems = graph.check_cells(tmp_path, {displays.OUTPUT: made})
    assert "cell:Out_AE/r3/c2: ard:A_TEAE/M_CAT_n/Arm_B has no node" in problems


def test_coverage_and_the_grids_of_the_build_must_agree(built, tmp_path):
    traced(built, tmp_path)
    with open(tmp_path / "coverage.json", encoding="ascii") as handle:
        coverage = json.load(handle)
    assert graph.check_cells(tmp_path, {})[1] == [
        "grid Out_AE: in coverage.json, but not a grid of the build"]
    coverage["displays"][displays.OUTPUT]["complete"] = 8
    write_json(tmp_path / "coverage.json", coverage)
    assert graph.check_cells(tmp_path, {displays.OUTPUT: built[3]})[1] == [
        "grid Out_AE: coverage.json disagrees with the graph files"]
    del coverage["displays"][displays.OUTPUT]
    write_json(tmp_path / "coverage.json", coverage)
    assert graph.check_cells(tmp_path, {displays.OUTPUT: built[3]})[1] == [
        "grid Out_AE: coverage.json has no entry for it"]
