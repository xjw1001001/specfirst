"""real-5b without R and without the cache: what Tables 14-3.11 and 14-3.13 need.

A CSR page with a column without a count, the header of the row labels and
a section heading on the line of its first row; a note in place of
footnotes; the proof other_build; the extra columns and the block kind
`groups` of layout spec v0 (amendment of real-5b to ADR-003 and ADR-015).
The pages and the events are invented.
"""

from __future__ import annotations

import copy

import pytest
import toy_displays as displays
import toy_results as toy

from specfirst.machine import ars, csr, grid
from specfirst.machine import layout as layouts

# ---- a CSR page of the shape of Table 14-3.13, invented ---------------------------------

CENTRES = (52, 64, 76, 90)


def line(stub: str, label: str, cells=()) -> str:
    text = " " * 4 + stub.ljust(10) + label if stub else " " * 14 + label
    for centre, cell in zip(CENTRES, cells, strict=False):
        if cell is not None:
            text = text.ljust(centre - len(cell) // 2) + cell
    return text


PAGE = "\n".join([
    "Protocol: DEMO" + " " * 60 + "Page 1 of 1",
    "Population: Efficacy",
    " " * 35 + "Table 9-3.13",
    " " * 25 + "Score - Categorical Analysis",
    "",
    line("", "", (None, "Drug", "Drug")),
    line("", "", ("Placebo", "Low", "High", "p-value")),
    line("", "", ("(N=10)", "(N=11)", "(N=12)", "[1]")),
    line("Week 8", "n", ("9", "11", "10", "0.1234")),
    line("", "Better", ("1 ( 11%)", "0", "2 ( 20%)")),
    line("", "Worse", ("8 ( 89%)", "11 (100%)", "8 ( 80%)")),
    "",
    "Note: Invented for a test,",
    "continued on the next line.",
    "Source: nowhere",
])


def test_a_page_with_a_column_without_a_count_is_read():
    page = PAGE.replace(" " * 30 + "(N=10)", "Assessment".ljust(30) + "(N=10)", 1)
    assert page != PAGE
    table = csr.parse(page, "9-3.13")
    assert table["stub"] == "Assessment"
    assert table["columns"] == [{"label": "Placebo", "count": "(N=10)"},
                                {"label": "Drug Low", "count": "(N=11)"},
                                {"label": "Drug High", "count": "(N=12)"},
                                {"label": "p-value [1]", "count": None}]
    assert [(line["label"], line["cells"]) for line in table["lines"]] == [
        ("Week 8", None), ("n", ["9", "11", "10", "0.1234"]),
        ("Better", ["1 ( 11%)", "0", "2 ( 20%)", None]),
        ("Worse", ["8 ( 89%)", "11 (100%)", "8 ( 80%)", None])]
    # A note stands in the place of footnotes.
    assert table["footnotes"] == ["Note: Invented for a test, continued on the next line."]


def test_a_line_of_three_labels_and_a_text_between_counts_are_refused():
    with pytest.raises(csr.CsrError, match="more than two labels"):
        csr.parse(PAGE.replace("Week 8    n", "Week 8  x  n"), "9-3.13")
    with pytest.raises(csr.CsrError, match="between two counts"):
        csr.parse(PAGE.replace("(N=11)", "(N=11)  x", 1), "9-3.13")


# ---- the proof other_build --------------------------------------------------------------

CELL = "cell:Out1/r2/c2"
SHOWN = (grid.Shown("d", "ard:A_PW/M_d/G_2", "X.X", "A_PW"),
         grid.Shown("se", "ard:A_PW/M_se/G_2", "X.XX", "A_PW"))
OURS = {"ard:A_PW/M_d/G_2": -0.59, "ard:A_PW/M_se/G_2": 1.02,
        "ard:A_PW_Avg/M_d/G_2": -0.04, "ard:A_PW_Avg/M_se/G_2": 0.70,
        "ard:A_PW_90/M_d/G_2": -0.04, "ard:A_PW_90/M_se/G_2": 0.70}
VISIT = "custom:eff-mmrm-visit"  # a decision that sets the option `at` (decisions.PARAMETERS)


def pairwise(analysis_id: str, at: str, level: str = "95") -> dict:
    return {"id": analysis_id, "name": analysis_id, "methodId": "M_PW", "dataset": "ADX",
            "variable": "CHG", "programmingCode": {"context": "specfirst method registry",
                                                  "parameters": [
                                                      {"name": "at", "value": [at]},
                                                      {"name": "confidence_level",
                                                       "value": [level]}]}}


ANALYSES = {"A_PW": pairwise("A_PW", "last"), "A_PW_Avg": pairwise("A_PW_Avg", "average"),
            "A_PW_90": pairwise("A_PW_90", "average", "90")}
RECORDS = {VISIT: {"id": VISIT, "binds": ["ars:A_PW"]},
           "custom:shown": {"id": "custom:shown", "binds": ["ars:M_PW"]},
           "custom:other": {"id": "custom:other", "binds": ["ars:A_OTHER"]}}
ENTRY = {"cell": CELL, "csr": "-0.0 (0.70)", "class": "rule_choice",
         "decision": [VISIT, "custom:shown"],
         "proof": {"kind": "other_build", "analyses": {"A_PW": "A_PW_Avg"},
                   "display": "display.pattern.signed"}}


def judged(entry: dict, ours: str = "-0.6 (1.02)", theirs: str = "-0.0 (0.70)",
           shown=SHOWN, template: str = "{d} ({se})", records=RECORDS,
           analyses=ANALYSES) -> csr.Comparison:
    found = csr.Comparison("Out1", "9-3.11", differing={CELL: (ours, theirs)})
    csr.judge(found, [entry], {CELL: (template, shown)}, OURS, records, analyses)
    return found


def test_a_difference_is_proved_by_another_build():
    assert judged(ENTRY).classified == {CELL: "rule_choice"}
    # Another template: a count of 0 without its percent.
    zero = (grid.Shown("n", "ard:A/n", "X", "A"), grid.Shown("pct", "ard:A/pct", "XX%", "A"))
    entry = {"cell": CELL, "csr": "0", "class": "rule_choice", "decision": "custom:d",
             "proof": {"kind": "other_build", "template": "{n}"}}
    found = csr.Comparison("Out1", "9-3.13", differing={CELL: ("0 (0%)", "0")})
    csr.judge(found, [entry], {CELL: ("{n} ({pct})", zero)}, {"ard:A/n": 0, "ard:A/pct": 0.0},
              {"custom:d"})
    assert found.problems == [] and found.classified == {CELL: "rule_choice"}


@pytest.mark.parametrize(("proof", "message"), [
    ({"kind": "other_build", "analyses": {"A_PW": "A_PW_Avg"}},
     "with the other build the cell is '0.0 (0.70)'"),
    ({"kind": "other_build", "analyses": {"A_PW": "A_PW"}, "display": "display.pattern.signed"},
     "with the other build the cell is"),
    ({"kind": "other_build", "analyses": {"A_PW": "A_NONE"}}, "no analysis A_NONE"),
    ({"kind": "other_build", "analyses": {"A_X": "A_PW_Avg"}}, "'analyses' must map analyses"),
    ({"kind": "other_build", "patterns": {"x": "X.X"}}, "'patterns' must give parts"),
    ({"kind": "other_build", "note": "x"}, "other_build takes"),
    ({"kind": "other_build"}, "other_build takes"),
    ({"kind": "other_build", "display": "display.pattern.other"}, "'display' must be a display"),
    # Review of real-5b, F1: the other analysis differs in more than the decision's option;
    # a template that shows no part, or adds text, is no build.
    ({"kind": "other_build", "analyses": {"A_PW": "A_PW_90"},
      "display": "display.pattern.signed"}, "differs from A_PW in more than the options at"),
    ({"kind": "other_build", "template": "-0.0 (0.70)"}, "must show parts of the cell"),
    ({"kind": "other_build", "template": "{n}"}, "must show parts of the cell"),
    ({"kind": "other_build", "template": "-{d} ({se})", "analyses": {"A_PW": "A_PW_Avg"}},
     "add no text"),
    # G1: nor may a pattern carry text: the sign of "-0.0" by a pattern, not by the rule.
    ({"kind": "other_build", "analyses": {"A_PW": "A_PW_Avg"}, "patterns": {"d": "-X.X"}},
     "the other pattern '-X.X' of d changes more than the mask of 'X.X'"),
    ({"kind": "other_build", "patterns": {"d": "-0.0", "se": "X.XX"}},
     "the other pattern of d is no pattern"),
])
def test_an_other_build_that_proves_nothing(proof, message):
    found = judged(dict(ENTRY, proof=proof))
    assert any(message in problem for problem in found.problems), found.problems


def test_an_other_build_proves_a_rule_choice_and_changes_something():
    found = judged(dict(ENTRY, **{"class": "reference_error"}))
    assert any("other_build proves a rule_choice" in p for p in found.problems)
    found = judged(ENTRY, ours="-0.0 (0.70)")
    assert any("the other build changes nothing" in p for p in found.problems)


def test_the_decisions_of_an_entry_bind_the_cell_and_set_what_the_build_changes():
    # A decision that binds neither the cell's analysis nor its method (F1, F3 of real-5a).
    found = judged(dict(ENTRY, decision=[VISIT, "custom:other"]))
    assert any("custom:other binds no analysis of the cell nor its method" in p
               for p in found.problems), found.problems
    # Decisions that set no option of an analysis cannot justify an other analysis.
    found = judged(dict(ENTRY, decision="custom:shown"))
    assert any("set no option of an analysis" in p for p in found.problems), found.problems
    # Without the records and the event an other analysis is not held, so it does not pass.
    found = judged(ENTRY, records={VISIT: {}, "custom:shown": {}}, analyses=None)
    assert any("which the check was not given" in p for p in found.problems), found.problems
    found = judged(dict(ENTRY, decision="custom:none"))
    assert any("no decision record custom:none" in p for p in found.problems)


# ---- extra columns and the block kind `groups` ------------------------------------------

GROUPS = {
    "layout": 0, "output": displays.OUTPUT,
    "columns": {"grouping": "ARM", "extra": [{"id": "pvalue", "label": "p-value"}]},
    "rows": [
        {"kind": "header", "cell": "{N}",
         "parts": {"N": {"analysis": "A_N", "operation": "M_N_n", "pattern": "(N=XX)"}}},
        {"kind": "statistics", "analysis": "A_N", "section": "Sex", "rows": [
            {"label": "n", "cell": "{n}", "parts": {"n": {"operation": "M_N_n", "pattern": "X"}},
             "extra": {"pvalue": {"cell": "{p}", "parts": {
                 "p": {"analysis": "A_AGE_P", "operation": "M_ANOVA_p"}}}}}]},
        {"kind": "groups", "analysis": "A_SEX", "grouping": "SEX", "section": "Sex",
         "indent": 1, "labels": {"Sex_M": "Men"}, "cell": "{n} ({pct})",
         "parts": {"n": {"operation": "M_CAT_n", "pattern": "X"},
                   "pct": {"operation": "M_CAT_pct", "pattern": "XX%"}}},
    ],
}


@pytest.fixture
def toy_event():
    return ars.index(displays.event_data())


def test_a_groups_block_gives_a_row_per_group_and_an_extra_column(root, toy_event):
    spec = layouts.parse(copy.deepcopy(GROUPS))
    assert layouts.problems(spec, toy_event) == []
    rows = toy.run(root, displays.event_data())
    made = grid.build(toy_event, spec, rows)
    assert grid.grid_problems(made, root) == []
    assert [column["label"] for column in made["columns"]][-1] == "p-value"
    # The header has no count in the extra column; the n row has the test's p-value there.
    assert made["rows"][0]["cells"][3] == {"id": f"cell:{displays.OUTPUT}/r1/c4", "column": "c4",
                                           "text": "", "ard": []}
    n_row = made["rows"][1]
    assert n_row["cells"][3]["ard"] == ["ard:A_AGE_P/M_ANOVA_p/*"]
    # One row per group of SEX, in its order, with the layout's label where it has one.
    assert [(row["label"], row["section"], row["indent"]) for row in made["rows"][2:]] == [
        ("Sex_F", "Sex", 1), ("Men", "Sex", 1)]
    for row in made["rows"][2:]:
        assert row["cells"][3]["text"] == "" and row["cells"][3]["ard"] == []
        assert all(cell["ard"] for cell in row["cells"][:3])
    shell = grid.shell(toy_event, spec)
    assert shell["rows"][1]["cells"][3]["text"] == "x.xxxx"
    assert shell["rows"][2]["cells"][0]["text"] == "x (xx%)"


@pytest.mark.parametrize(("change", "message"), [
    (lambda d: d["columns"]["extra"].append({"id": "Arm_A", "label": "x"}),
     "'Arm_A' is the ID of a group of ARM"),
    (lambda d: d["rows"][1]["rows"][0]["extra"]["pvalue"]["parts"]["p"].update(
        analysis="A_AGE"), "compares the column grouping ARM alone"),
    (lambda d: d["rows"][1]["rows"][0]["extra"].update(other=d["rows"][1]["rows"][0]["extra"][
        "pvalue"]), "'other': not an extra column of the layout"),
    (lambda d: d["rows"][2].update(analysis="A_AGE"), "split by the column grouping ARM and"),
    (lambda d: d["rows"][2].update(grouping="SOC"), "with defined groups"),
    (lambda d: d["rows"][2].update(labels={"Sex_X": "x"}), "'Sex_X' is not a group of SEX"),
])
def test_an_extra_column_or_a_groups_block_that_does_not_fit_its_event(toy_event, change,
                                                                         message):
    data = copy.deepcopy(GROUPS)
    change(data)
    found = layouts.problems(layouts.parse(data), toy_event)
    assert any(message in problem for problem in found), found


@pytest.mark.parametrize(("change", "message"), [
    (lambda d: d["columns"]["extra"].append({"id": "pvalue", "label": "x"}), "listed twice"),
    (lambda d: d["columns"]["extra"].append({"id": "p value", "label": "x"}),
     "has an 'id' \\(a name\\) and a 'label'"),
    (lambda d: d["rows"][2].pop("grouping"), "names its 'analysis' and its row 'grouping'"),
    (lambda d: d["rows"][2]["parts"]["n"].update(analysis="A_N"),
     "shows a result of the block's analysis"),
    (lambda d: d["rows"][2].update(rows=[]), "unknown key 'rows'"),
    (lambda d: d["rows"][1]["rows"][0]["extra"]["pvalue"]["parts"]["p"].pop("analysis"),
     "a part of a header names its analysis"),
])
def test_an_extra_column_or_a_groups_block_of_another_form_is_refused(change, message):
    data = copy.deepcopy(GROUPS)
    change(data)
    with pytest.raises(layouts.LayoutError, match=message):
        layouts.parse(data)
