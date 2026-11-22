"""The layout pieces of issue #31 (ADR-022): the extra cells of a groups block, the block
kind `terms` with its nested rows, and the spanner of an extra column; on the toy event of
tests/toy_results.py.

The toy's treatment-emergent records in the safety set (worked out by hand):

    organ class  term     arm A    arm B
    CARD         AF       S1       -
    CARD         MI       -        S5
    SKIN         RASH     S2       S6

Arm A has 4 subjects, arm B 3 and arm C none. Every check is first shown to pass on the
unchanged inputs and then to fail on a planted defect (rule R5).
"""

from __future__ import annotations

import copy
import re

import pytest
import toy_displays as displays
import toy_results as toy

from specfirst.machine import ars, grid, layout, methods


def event_data() -> dict:
    """The toy event with an analysis by organ class and a Fisher test by organ class and
    term besides those it has (A_SOC by arm, organ class and term; A_SOC_P by organ class)."""
    data = displays.event_data()
    data["analyses"] += [
        toy.analysis("A_SOC1", "M_CAT", "ADAE", "USUBJID", [("ARM", True), ("SOC", True)],
                     analysisSetId="SAF", dataSubsetId="TEAE", **toy.percent_of("A_SOC1", "A_N")),
        toy.analysis("A_PT_P", "M_FISHER", "ADAE", "USUBJID",
                     [("ARM", False), ("SOC", True), ("PT", True)], analysisSetId="SAF",
                     dataSubsetId="TEAE_AB"),
    ]
    return data


CELL = {"cell": "{n} {pct}", "parts": {"n": {"operation": "M_CAT_n", "pattern": "XX"},
                                       "pct": {"operation": "M_CAT_pct"}}}
P = {"cell": "{p}", "parts": {"p": {"analysis": "A_SOC_P", "operation": "M_FISHER_p"}}}


def layout_data() -> dict:
    return {
        "layout": 0, "output": displays.OUTPUT,
        "columns": {"grouping": "ARM", "extra": [
            {"id": "p", "label": "A vs. B", "spanner": "Fisher p-values"}]},
        "rows": [
            {"kind": "header", "cell": "{N}",
             "parts": {"N": {"analysis": "A_N", "operation": "M_N_n", "pattern": "(N=XX)"}}},
            {"kind": "groups", "analysis": "A_SEX", "grouping": "SEX", "section": "Sex",
             **copy.deepcopy(CELL),
             "extra": {"p": {"cell": "{p}", "parts": {"p": {"analysis": "A_SEX_P",
                                                            "operation": "M_CHISQ_p"}}}}},
            {"kind": "terms", "analysis": "A_SOC1", "grouping": "SOC", "sort": "alphabetical",
             **copy.deepcopy(CELL), "extra": {"p": copy.deepcopy(P)},
             "nested": {"analysis": "A_SOC", "grouping": "PT", "indent": 1, "extra": {"p": {
                 "cell": "{p}", "parts": {"p": {"analysis": "A_PT_P",
                                                "operation": "M_FISHER_p"}}}}}},
        ],
    }


@pytest.fixture(scope="module")
def event():
    return ars.index(event_data())


@pytest.fixture(scope="module")
def rows(root):
    return toy.run(root, event_data())


def labels(made: dict) -> list[tuple[int, str]]:
    return [(row.get("indent", 0), row["label"]) for row in made["rows"]]


def p_text(rows: dict, key: str) -> str:
    return methods.pattern_text(rows[key]["raw_value"], "X.XXXX")


def test_the_rows_of_a_terms_block_are_the_values_of_the_results(event, rows):
    spec = layout.parse(layout_data())
    assert layout.problems(spec, event) == []
    made = grid.build(event, spec, rows)
    assert labels(made) == [(0, "Subjects, n (%)"), (0, "Sex_F"), (0, "Sex_M"),
                            (0, "CARD"), (1, "AF"), (1, "MI"), (0, "SKIN"), (1, "RASH")]
    texts = {row["label"]: [cell["text"] for cell in row["cells"]] for row in made["rows"]}
    assert texts["CARD"][:3] == ["1 ( 25.0)", "1 ( 33.3)", "0 "]
    assert texts["AF"][:3] == ["1 ( 25.0)", "0 (  0.0)", "0 "]
    assert texts["MI"][:3] == ["0 (  0.0)", "1 ( 33.3)", "0 "]
    assert texts["RASH"][:3] == ["1 ( 25.0)", "1 ( 33.3)", "0 "]
    # The p-values stand in the extra column of every row, from the ARD of the comparison.
    assert texts["CARD"][3] == p_text(rows, "ard:A_SOC_P/M_FISHER_p/*/=CARD")
    assert texts["MI"][3] == p_text(rows, "ard:A_PT_P/M_FISHER_p/*/=CARD/=MI")
    cell = made["rows"][4]["cells"][3]
    assert cell["ard"] == ["ard:A_PT_P/M_FISHER_p/*/=CARD/=AF"]
    # The columns: the spanner of the extra column.
    assert made["columns"][3] == {"id": "c4", "label": "A vs. B", "spanner": "Fisher p-values"}


def test_the_extra_cell_of_a_groups_block_stands_in_its_first_row(event, rows):
    made = grid.build(event, layout.parse(layout_data()), rows)
    first, second = made["rows"][1], made["rows"][2]
    assert first["cells"][3]["text"] == p_text(rows, "ard:A_SEX_P/M_CHISQ_p/*/*")
    assert first["cells"][3]["ard"] == ["ard:A_SEX_P/M_CHISQ_p/*/*"]
    assert (second["cells"][3]["text"], second["cells"][3]["ard"]) == ("", [])


def test_a_comparison_without_a_result_for_a_term_leaves_its_cell_empty(event, rows):
    """A data subset of two arms may have no record of a term: no result, an empty cell."""
    fewer = {key: row for key, row in rows.items()
             if key != "ard:A_PT_P/M_FISHER_p/*/=CARD/=MI"}
    made = grid.build(event, layout.parse(layout_data()), fewer)
    mi = next(row for row in made["rows"] if row["label"] == "MI")
    assert (mi["cells"][3]["text"], mi["cells"][3]["ard"]) == ("", [])
    # A result of the block's own analysis that is missing is an error, as in every block.
    fewer = {key: row for key, row in rows.items() if key != "ard:A_SOC/M_CAT_n/Arm_B/=CARD/=MI"}
    with pytest.raises(grid.GridError, match="not in the ARD"):
        grid.build(event, layout.parse(layout_data()), fewer)


def test_the_shell_of_a_terms_block_has_a_placeholder_row_per_level(event):
    shell = grid.shell(event, layout.parse(layout_data()))
    assert labels(shell)[3:] == [(0, "<Organ class>"), (1, "<Term>")]
    placeholder = shell["rows"][3]["cells"]
    assert [cell["text"] for cell in placeholder] == ["xx ( xx.x)"] * 3 + [""]
    assert all(cell["ard"] == [] for cell in placeholder)
    assert not any(grid.numeric(cell) for row in shell["rows"] for cell in row["cells"])


def change(path, value):
    def apply(data):
        target = data
        for key in path[:-1]:
            target = target[key]
        if value is None:
            del target[path[-1]]
        else:
            target[path[-1]] = value
    return apply


@pytest.mark.parametrize(("planted", "message"), [
    (change(["rows", 2, "sort"], "by_count"), "'sort' must be one of alphabetical"),
    (change(["rows", 2, "nested", "colour"], 1), "nested: unknown key 'colour'"),
    (change(["columns", "extra", 0, "spanner"], 3), "may have a 'spanner'"),
    (change(["rows", 2, "nested"], "A_SOC"), "nested: names its 'analysis'"),
])
def test_a_terms_block_that_is_not_of_the_format_is_refused(planted, message):
    data = layout_data()
    planted(data)
    with pytest.raises(layout.LayoutError, match=message):
        layout.parse(data)


@pytest.mark.parametrize(("planted", "message"), [
    # A row grouping with defined groups is no grouping of a terms block.
    (change(["rows", 2, "grouping"], "SEX"), "'SEX' is not a data-driven grouping"),
    # The block's analysis must be split by the column and the row grouping only.
    (change(["rows", 2, "analysis"], "A_SOC"), "a terms block shows an analysis split by"),
    # The nested analysis is split by both row groupings.
    (change(["rows", 2, "nested", "analysis"], "A_SOC1"), "split by the column grouping and "
                                                          "both row groupings"),
    # The p-value of a row compares the arms, split by the row grouping.
    (change(["rows", 2, "extra", "p", "parts", "p", "analysis"], "A_PT_P"),
     "must have the groupings ARM \\(compared\\), SOC \\(by group\\)"),
    # The p-value of a groups block compares the arms and the row grouping.
    (change(["rows", 1, "extra", "p", "parts", "p", "analysis"], "A_AGE_P"),
     "must have the groupings ARM \\(compared\\), SEX \\(compared\\)"),
    # An extra cell stands in an extra column of the layout.
    (change(["rows", 1, "extra", "q"], {"cell": "{p}", "parts": {"p": {
        "analysis": "A_SEX_P", "operation": "M_CHISQ_p"}}}), "extra 'q': not an extra column"),
])
def test_a_terms_block_that_does_not_fit_its_event_is_refused(event, planted, message):
    data = layout_data()
    planted(data)
    found = layout.problems(layout.parse(data), event)
    assert any(re.search(message, item) for item in found), found
    with pytest.raises(grid.GridError, match="does not fit"):
        grid.plan(event, layout.parse(data), None)
