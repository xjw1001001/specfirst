"""The review page and its checks (issue #31, ADR-022), on a review made by hand.

One output with one printed number (a count and its percent in one cell), one analysis
that reads two ADaM columns reaching SDTM, one decision record with a citation that binds
the analysis and one that binds a column it reads, and the sheet. The page must pass every
check, and fail on each planted defect (rule R5): a cell without a panel, a broken path to
SDTM in the review and in the page, a decision left off the sheet and off the panel, a
judged edge drawn as proven, a citation without its approval words, an unseparated or a
tested decision drawn as proven, a script and a link that leaves the page.
"""

from __future__ import annotations

import copy

import pytest

from specfirst.machine import build
from specfirst.viewer import check, model, page

CELL = "cell:Out_X/r2/c1"
KEY = "toy/A_SEX"
COLUMN_RECORD = "pop.safety.rule (mod-populations)"


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
    # A record of a column the analysis reads: drawn in its panel with the column it binds.
    flag = model.DecisionView(
        COLUMN_RECORD, "pop.safety.rule", "mod-populations",
        "The safety set is every randomized subject who took a dose.",
        '{"rule": "randomized_and_dosed"}', "default", "house_default", model.HOUSE_DEFAULT,
        [model.Citation("doc:house#pop", "The safety set", True, None, "record")], [],
        ["adam:ADSL.SAFFL"], model.NOT_TESTED, "gold/decisions/x.jsonl")
    analysis = model.AnalysisView(
        KEY, "toy", "A_SEX", "Sex by arm", ["Who: the safety set."], ["count: none"],
        ["ars:A_SEX"], decisions=[decision.key],
        column_decisions=[(flag.key, "adam:ADSL.SAFFL", "adam:ADSL.SAFFL")], cites=[cite],
        columns=[("adam:ADSL.SEX", ["variable"]), ("adam:ADSL.SAFFL", ["set"])],
        recompute={"analysis": "A_SEX", "event": "toy", "status": "reproduced", "rows": 2,
                   "largest": 0.0},
        script=("scripts/toy/A_SEX.py", "import sys\n"))
    columns = {
        "adam:ADSL.SEX": model.ColumnView("adam:ADSL.SEX", "Sex", "DM.SEX", '{"value": "DM.SEX"}',
                                          "adsl.yaml:9", [decision.key], [], ["sdtm:DM.SEX"],
                                          ["sdtm:DM.SEX"]),
        "adam:ADSL.SAFFL": model.ColumnView("adam:ADSL.SAFFL", "Safety flag", "", "",
                                            "adsl.yaml:30", [flag.key], [], ["sdtm:EX.EXDOSE"],
                                            ["sdtm:EX.EXDOSE"]),
    }
    cells = {CELL: model.CellView(CELL, "Out_X", "Female", "Arm A", "2 ( 50.0)", [
        ("ard:A_SEX/n/Arm_A/Sex_F", "n", "2"), ("ard:A_SEX/pct/Arm_A/Sex_F", "pct", "50.0")],
        KEY, [KEY])}
    sheet = [model.SheetLine("record", view.key, view.unit, view.statement, view.status,
                             view.klass, view.mark, view.citations, view.p4, 1)
             for view in (decision, flag)]
    return model.Review("toy", ("catalog@2", "open-default@2"),
                        [model.OutputView("Out_X", "toy", grid, [KEY])], {KEY: analysis}, cells,
                        columns, {decision.key: decision, flag.key: flag}, sheet, [])


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


def test_a_kit_binding_is_found_in_the_catalog_by_the_parameters_it_sets(root):
    """The review of issue #31, F6: the sheet marks the binding sas5 by the house."""
    from specfirst.compile import house as houses

    catalog, _ = houses.load_pair(root, "catalog@2", "open-default@2")
    assert model._alternatives_setting(catalog, "quantile_definition", "sas5") == [
        ("tfl.quantile.definition", "tfl-demographics", "sas5")]
    assert model._alternatives_setting(catalog, "quantile_definition", "sas9") == []


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
                     "citation or a house default; 1 draw every decision behind them",
                     "sheet: 2 record; 2 of 2 records listed"]
    # The record of a column it reads stands in section 2 with the column it binds.
    assert text.index("2. The decisions behind it") < text.index(
        f'<li class="decision" data-key="{COLUMN_RECORD}">') < text.index("3. The ADaM columns")
    assert "It binds <code>adam:ADSL.SAFFL</code>, which the analysis reads." in text
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
    # One citation's approval words moved into another: as many words as citations, and
    # one citation without them (the review of issue #31, F3).
    ("; awaiting approval)</li>", ")</li>", "citation 1 is not marked awaiting approval"),
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


def test_a_class_of_a_p4_run_is_drawn_tested_and_never_static():
    made = review()
    made.decisions["demo.sex (mod-demographics)"].p4 = "separated"
    made.sheet[0].p4 = "separated"
    text = page.html(made)
    assert check.page_problems(text, made) == []
    assert '<span class="kind tested">P4: separated</span>' in text
    found = check.page_problems(text.replace("kind tested", "kind static"), made)
    assert any("has the P4 class separated and is drawn otherwise" in p for p in found), found


def test_a_class_of_a_p4_run_holds_only_at_the_value_it_was_found_at(tmp_path):
    # The matrix of `specfirst gen separate` decides a class at its gold value; a record
    # with another value is not tested, and says what the run tried.
    matrix = tmp_path / "matrix.json"
    matrix.write_text('{"decisions": [{"id": "ae.teae.end", "unit": "mod-ae-emergence", '
                      '"class": "unseparated", "value": {"rule": "last_dose_plus_days", '
                      '"days": 30}, "gold": "last_dose_plus_days(days=30)"}]}',
                      encoding="ascii")
    from specfirst.viewer import command

    run = command.read_p4(matrix)[("ae.teae.end", "mod-ae-emergence")]
    assert run == model.P4Run("unseparated", '{"days": 30, "rule": "last_dose_plus_days"}',
                              "last_dose_plus_days(days=30)")
    assert model.p4_of(None, run.value) == (model.NOT_TESTED, "")
    assert model.p4_of(run, model.canonical({"rule": "last_dose_plus_days", "days": 30})) \
        == ("unseparated", "")
    assert model.p4_of(run, model.canonical({"rule": "no_end"})) == (
        model.NOT_TESTED, "the P4 run tried another value, last_dose_plus_days(days=30): "
        "unseparated")
    # The page draws it not tested, with the note, in its panel and on the sheet.
    made = review()
    note = "the P4 run tried another value, last_dose_plus_days(days=30): unseparated"
    made.decisions["demo.sex (mod-demographics)"].p4_note = note
    made.sheet[0].p4_note = note
    text = page.html(made)
    assert check.page_problems(text, made) == []
    assert text.count(f'<span class="kind not-tested">not-tested</span> ({note})') == 2


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
    for view in bare.decisions.values():
        view.citations = []
        view.mark = model.CUSTOMIZED
    _, found = check.acceptance(bare, text, ("Out_X",))
    assert found == [f"{CELL}: its panel reaches no citation and no house default"]
    # An entry of the catalog the kit names that the sheet does not list.
    entries = copy.deepcopy(made)
    entries.catalog_keys = ["demo.sex (mod-demographics)", "demo.bmi.rule (mod-demographics)"]
    _, found = check.acceptance(entries, text, ("Out_X",))
    assert found == ["the sheet does not list the entry demo.bmi.rule (mod-demographics) of "
                     "the catalog"]


def test_what_the_page_does_not_draw_is_seen_though_the_review_holds_it():
    """The review of issue #31, F3: the acceptance reads the page back."""
    made = review()
    text = page.html(made)
    # The page names no SDTM column in the panel.
    no_sdtm = text.replace("Down to SDTM: <code>sdtm:DM.SEX</code>", "Down to SDTM: none")
    _, found = check.acceptance(made, no_sdtm, ("Out_X",))
    assert found == [f"{CELL}: its panel reaches no SDTM column through every column it reads"]
    # The panel draws no citation and no house default.
    bare = text.replace('<li class="citation">', "<li>").replace(
        'class="kind house-default"', 'class="kind study-customized"')
    _, found = check.acceptance(made, bare, ("Out_X",))
    assert found == [f"{CELL}: its panel reaches no citation and no house default"]
    # The record of a column it reads is not drawn in the panel.
    gone = text.replace(f'<li class="decision" data-key="{COLUMN_RECORD}">', "<li>")
    _, found = check.acceptance(made, gone, ("Out_X",))
    assert found == [f"{CELL}: its panel does not draw the decision {COLUMN_RECORD}"]
    # A record left off the sheet of the page.
    row = '<tr class="decision" id="s-demo.sex_(mod-demographics)" data-key="demo.sex ' \
          '(mod-demographics)">'
    _, found = check.acceptance(made, planted_page(text, row, "<tr>"), ("Out_X",))
    assert found == ["the sheet does not list the decision demo.sex (mod-demographics)"]
