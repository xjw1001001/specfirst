"""The review page and its checks (issue #31, ADR-022), on a review made by hand.

One output with one printed number (a count and its percent in one cell), one analysis
that reads two ADaM columns reaching SDTM, one decision record with a citation, and the
sheet. The page must pass every check, and fail on each planted defect (rule R5): a cell
without a panel, a broken path to SDTM, a decision left off the sheet, a judged edge drawn
as proven, an unseparated decision drawn as proven, a script and a link that leaves the
page.
"""

from __future__ import annotations

import copy

import pytest

from specfirst.machine import build
from specfirst.viewer import check, model, page

CELL = "cell:Out_X/r2/c1"
KEY = "toy/A_SEX"


def review() -> model.Review:
    grid = {"schema": "specfirst/grid@0", "output_id": "Out_X", "titles": ["Table 1"],
            "footnotes": ["N = subjects."],
            "columns": [{"id": "c1", "label": "Arm A"}, {"id": "c2", "label": "p-value"}],
            "rows": [{"id": "r1", "label": "Subjects", "section": "@header", "cells": [
                {"id": "cell:Out_X/r1/c1", "column": "c1", "text": "Arm", "ard": []},
                {"id": "cell:Out_X/r1/c2", "column": "c2", "text": "", "ard": []}]},
                     {"id": "r2", "label": "Female", "cells": [
                         {"id": CELL, "column": "c1", "text": "2 ( 50.0)",
                          "ard": ["ard:A_SEX/n/Arm_A/Sex_F", "ard:A_SEX/pct/Arm_A/Sex_F"]},
                         {"id": "cell:Out_X/r2/c2", "column": "c2", "text": "", "ard": []}]}]}
    cite = model.Citation("doc:sap#9/9.2. Demographics", "9.2. Demographics", True, None,
                          "imported")
    decision = model.DecisionView(
        "demo.sex (mod-demographics)", "demo.sex", "mod-demographics",
        "Sex is ADSL.SEX.", '{"rule": "dm_sex"}', "stated", "document_rule",
        model.HOUSE_DEFAULT, [model.Citation("doc:sap#9.2", "sex", True, None, "record")],
        ["Sex is collected again."], ["ars:A_SEX"], model.NOT_TESTED, "gold/decisions/x.jsonl")
    analysis = model.AnalysisView(
        KEY, "toy", "A_SEX", "Sex by arm", ["Who: the safety set."], ["count: none"],
        ["ars:A_SEX"], decisions=[decision.key], cites=[cite],
        columns=[("adam:ADSL.SEX", ["variable"]), ("adam:ADSL.SAFFL", ["set"])],
        recompute={"analysis": "A_SEX", "event": "toy", "status": "reproduced", "rows": 2,
                   "largest": 0.0},
        script=("scripts/toy/A_SEX.py", "import sys\n"))
    columns = {
        "adam:ADSL.SEX": model.ColumnView("adam:ADSL.SEX", "Sex", "DM.SEX", '{"value": "DM.SEX"}',
                                          "adsl.yaml:9", [decision.key], [], ["sdtm:DM.SEX"],
                                          ["sdtm:DM.SEX"]),
        "adam:ADSL.SAFFL": model.ColumnView("adam:ADSL.SAFFL", "Safety flag", "", "",
                                            "adsl.yaml:30", [], [], ["sdtm:EX.EXDOSE"],
                                            ["sdtm:EX.EXDOSE"]),
    }
    cells = {CELL: model.CellView(CELL, "Out_X", "Female", "Arm A", "2 ( 50.0)", [
        ("ard:A_SEX/n/Arm_A/Sex_F", "n", "2"), ("ard:A_SEX/pct/Arm_A/Sex_F", "pct", "50.0")],
        KEY, [KEY])}
    sheet = [model.SheetLine("record", decision.key, decision.unit, decision.statement,
                             decision.status, decision.klass, decision.mark, decision.citations,
                             decision.p4, 1)]
    return model.Review("toy", ("catalog@2", "open-default@2"),
                        [model.OutputView("Out_X", "toy", grid, [KEY])], {KEY: analysis}, cells,
                        columns, {decision.key: decision}, sheet, [])


def test_the_gate_of_issue_31():
    from specfirst import gates

    names = [check.name for check in gates.GATES["issue-31"]]
    assert names[0] == "environment" and names[-1] == "ASCII"
    for earlier, later in (("P1 determinism", "trace"), ("grids", "review"),
                           ("recompute", "review"), ("review", "planted defects"),
                           ("planted defects", "cache untouched")):
        assert names.index(earlier) < names.index(later)
    assert gates.REVIEW_OUTPUTS == ("Out14-1-1", "Out14-3-1-1", "Out14-3-2-1")
    assert gates.REVIEW_DEFECTS == ("D7-display", "D8-trace", "D13-review")


def test_the_folders_are_those_of_the_build():
    assert (model.GRAPH, model.GRID, model.ARD, model.RESOLVED) == (
        build.GRAPH, build.GRID, build.ARD, build.RESOLVED)


def test_the_page_passes_its_checks_and_is_the_same_twice():
    made = review()
    text = page.html(made)
    assert text == page.html(review())
    assert check.page_problems(text, made) == []
    lines, problems = check.acceptance(made, text, ("Out_X",))
    assert problems == []
    assert lines == ["Out_X: 1 printed numbers; 1 open a panel; 1 reach SDTM; 1 reach a "
                     "citation or a house default", "sheet: 1 record; 1 of 1 records listed"]
    # The calculation stands before the folded grid; the number links to its cell's block,
    # which is in the panel of its analysis.
    assert text.index("The calculation") < text.index("<details><summary>The grid")
    assert f'href="#c-{CELL}"' in text and f'id="c-{CELL}"' in text
    assert text.index('class="panel" id="a-toy/A_SEX"') < text.index(f'id="c-{CELL}"')
    assert "awaiting approval" in text and "house default" in text
    assert "in the study spec's words (the Define-XML comment)" in text


def planted_page(text: str, old: str, new: str) -> str:
    assert old in text, old
    return text.replace(old, new, 1)


@pytest.mark.parametrize(("old", "new", "message"), [
    ("</body>", "<script>fetch('x')</script></body>", "the page has a <script>"),
    ('<a class="number"', '<a onclick="x()" class="number"', "the handler 'onclick'"),
    ('href="#sheet"', 'href="https://example.org/x"', "leaves the page"),
    ('<li class="citation"><span class="kind judged">judged</span>',
     '<li class="citation"><span class="kind executed">judged</span>',
     "is drawn executed, not judged"),
    ("awaiting approval", "approved", "marked awaiting approval or approved by a person"),
    ('href="#sheet"', 'href="#nowhere"', "has no anchor on the page"),
])
def test_a_page_that_loads_runs_or_draws_a_kind_wrongly_is_seen(old, new, message):
    made = review()
    found = check.page_problems(planted_page(page.html(made), old, new), made)
    assert any(message in problem for problem in found), found


def test_an_unseparated_decision_drawn_as_proven_is_seen():
    made = review()
    made.decisions["demo.sex (mod-demographics)"].p4 = model.UNSEPARATED
    made.sheet[0].p4 = model.UNSEPARATED
    text = page.html(made)
    assert check.page_problems(text, made) == []
    found = check.page_problems(text.replace("kind unseparated", "kind static"), made)
    assert any("is unseparated and not drawn so" in problem for problem in found), found


def test_a_cell_without_a_panel_a_broken_path_and_a_decision_off_the_sheet_are_seen():
    made = review()
    text = page.html(made)
    # A cell without a panel: its block is gone from the page.
    _, found = check.acceptance(made, text.replace(f'id="c-{CELL}"', 'id="c-other"'),
                                ("Out_X",))
    assert found == [f"{CELL}: prints '2 ( 50.0)' and opens no panel"]
    # A broken path to SDTM: a column the analysis reads has no node.
    broken = copy.deepcopy(made)
    del broken.columns["adam:ADSL.SAFFL"]
    _, found = check.acceptance(broken, text, ("Out_X",))
    assert found == [f"{CELL}: its panel reaches no SDTM column through every column it reads"]
    # No citation and no house default.
    bare = copy.deepcopy(made)
    bare.analyses[KEY].cites = []
    bare.decisions["demo.sex (mod-demographics)"].citations = []
    bare.decisions["demo.sex (mod-demographics)"].mark = model.CUSTOMIZED
    _, found = check.acceptance(bare, text, ("Out_X",))
    assert found == [f"{CELL}: its panel reaches no citation and no house default"]
    # A decision left off the sheet.
    off = copy.deepcopy(made)
    off.sheet = []
    _, found = check.acceptance(off, text, ("Out_X",))
    assert found == ["the sheet does not list the decision demo.sex (mod-demographics)"]
