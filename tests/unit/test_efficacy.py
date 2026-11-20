"""real-5a (ADR-012, ADR-015): what the efficacy tables add, without R and without the cache.

The reference grid of a CSR page and the comparison of a grid with it, on a
page invented here (no CSR text is in git, rule 4); the block kind
`statistics` of layout spec v0; the options of the model-based methods of the
registry; the model terms an analysis reads; the Python engine, which leaves a
model-based analysis to R; the gold ARD; and the check of the decision records.
"""

from __future__ import annotations

import copy

import pytest
import toy_displays as displays
import toy_results as toy
import yaml

from specfirst.machine import ard, ars, build, csr, decisions, grid, registry
from specfirst.machine import layout as layouts

# ---- a page of a CSR, invented ---------------------------------------------------------

CENTRES = (40, 60, 80)


def line(label: str, cells=(), indent: int = 4) -> str:
    text = " " * indent + label
    for centre, cell in zip(CENTRES, cells, strict=False):
        if cell is not None:
            text = text.ljust(centre - len(cell) // 2) + cell
    return text


PAGE = "\n".join([
    "Protocol: DEMO" + " " * 60 + "Page 1 of 1",
    "Population: Efficacy",
    " " * 35 + "Table 9-1.01",
    " " * 20 + "Score - Change from Baseline to Week 4",
    "",
    line("", (None, "Drug", "Drug"), 0),
    line("", ("Placebo", "Low", "High"), 0),
    line("", ("(N=10)", "(N=11)", "(N=12)"), 0),
    line("Baseline"),
    line("n", ("10", "11", "12"), 6),
    line("Mean (SD)", ("5.1 (1.20)", "5.3 (1.10)", "4.9 (1.30)"), 6),
    "",
    line("p-value(Dose Response) [1]", (None, None, "0.123"), 6),
    line("p-value(Drug - Placebo)[1]", (None, "0.456", "0.789"), 6),
    line("Diff (SE)", (None, "-0.5 (0.40)", "-1.0 (0.41)"), 7),
    "",
    "[1] Invented for a test,",
    "continued on the next line.",
    "Source: nowhere",
])


def test_a_page_is_read_as_a_reference_grid():
    table = csr.parse(PAGE, "9-1.01")
    assert table["titles"] == ["Table 9-1.01", "Score - Change from Baseline to Week 4"]
    assert table["population"] == "Efficacy"
    assert table["columns"] == [{"label": "Placebo", "count": "(N=10)"},
                                {"label": "Drug Low", "count": "(N=11)"},
                                {"label": "Drug High", "count": "(N=12)"}]
    assert [(line["label"], line["cells"]) for line in table["lines"]] == [
        ("Baseline", None), ("n", ["10", "11", "12"]),
        ("Mean (SD)", ["5.1 (1.20)", "5.3 (1.10)", "4.9 (1.30)"]),
        ("p-value(Dose Response) [1]", [None, None, "0.123"]),
        ("p-value(Drug - Placebo)[1]", [None, "0.456", "0.789"]),
        ("Diff (SE)", [None, "-0.5 (0.40)", "-1.0 (0.41)"])]
    assert table["footnotes"] == ["[1] Invented for a test, continued on the next line."]


@pytest.mark.parametrize(("change", "message"), [
    (lambda page: page.replace("Table 9-1.01", "Table 9-1.02"), "no line 'Table 9-1.01'"),
    (lambda page: page.replace("(N=", "(M="), "no line with the counts"),
    (lambda page: page.replace("    Baseline", line("", ("7",)), 1), "no row label"),
    (lambda page: page.replace("5.1 (1.20)", "5.1   1.20"), "two texts in column 1"),
])
def test_a_page_that_is_not_such_a_table_is_refused(change, message):
    with pytest.raises(csr.CsrError, match=message):
        csr.parse(change(PAGE), "9-1.01")


def made_grid() -> dict:
    """The grid that shows the invented table; blanks where a pattern pads."""
    def cells(number: int, texts) -> list[dict]:
        return [{"id": f"cell:Out1/r{number}/c{k}", "column": f"c{k}", "text": text,
                 "ard": [f"ard:x/{number}/{k}"] if text else []}
                for k, text in enumerate(texts, start=1)]
    rows = [("", "@header", ("(N=10)", "(N=11)", "(N=12)")),
            ("n", "Baseline", ("10", "11", "12")),
            ("Mean (SD)", "Baseline", (" 5.1 (1.20)", "5.3 (1.10)", "4.9 ( 1.30)")),
            ("p-value(Dose Response) [1]", None, ("", "", "0.123")),
            ("p-value(Drug - Placebo) [1]", None, ("", "0.456", "0.789")),
            ("Diff (SE)", None, ("", "-0.50 (0.40)", "-1.0 (0.41)"))]
    made = []
    for number, (label, section, texts) in enumerate(rows, start=1):
        row = {"id": f"r{number}", "label": label, "cells": cells(number, texts)}
        if section:
            row["section"] = section
        made.append(row)
    return {"schema": grid.SCHEMA, "output_id": "Out1",
            "titles": ["Table 9-1.01", "Score - Change from Baseline to Week 4"],
            "columns": [{"id": "c1", "label": "Placebo"}, {"id": "c2", "label": "Drug Low"},
                        {"id": "c3", "label": "Drug  High"}],
            "rows": made, "footnotes": []}


DIFF = "cell:Out1/r6/c2"
SHOWN = (grid.Shown("d", "ard:x/d", "X.XX", "A"), grid.Shown("se", "ard:x/se", "X.XX", "A"))
PLANNED = {DIFF: ("{d} ({se})", SHOWN)}
OURS = {"ard:x/d": -0.4987, "ard:x/se": 0.4012}
ENTRY = {"cell": DIFF, "csr": "-0.5 (0.40)", "class": "rule_choice", "decision": "custom:d",
         "proof": {"kind": "other_pattern", "patterns": {"d": "X.X"}}}


def test_every_cell_is_compared_without_its_blanks():
    compared = csr.compare(made_grid(), csr.parse(PAGE, "9-1.01"))
    assert compared.problems == []
    # 3 counts and 5 rows of 3 cells; the CSR prints 3 + 6 + 1 + 2 + 2 of them.
    assert (compared.cells, compared.printed, compared.equal) == (18, 14, 17)
    assert compared.differing == {DIFF: ("-0.50 (0.40)", "-0.5 (0.40)")}


def test_a_difference_is_classified_by_its_one_proof():
    table = csr.parse(PAGE, "9-1.01")
    compared = csr.compare(made_grid(), table)
    csr.judge(compared, [ENTRY], PLANNED, OURS, {"custom:d"})
    assert compared.problems == [] and compared.classified == {DIFF: "rule_choice"}
    for entries, message in (
        ([], "a difference with no class"),
        ([dict(ENTRY, proof={"kind": "other_pattern", "patterns": {"d": "X.XX"}})],
         "the other patterns change nothing"),
        ([dict(ENTRY, proof={"kind": "other_pattern", "patterns": {"d": "X.XXX"}})],
         "with the other patterns the cell is '-0.499 (0.40)'"),
        ([dict(ENTRY, proof={"kind": "other_pattern", "patterns": {"x": "X.X"}})],
         "'patterns' must give parts of the cell"),
        # Review of real-5b, G1: a pattern changes the mask only, so it carries no CSR text.
        ([dict(ENTRY, proof={"kind": "other_pattern", "patterns": {"d": "X.X", "se": "X.40"}})],
         "the other pattern 'X.40' of se changes more than the mask of 'X.XX'"),
        ([dict(ENTRY, proof={"kind": "other_pattern", "patterns": {"d": "-0.5"}})],
         "the other pattern of d is no pattern"),
        ([dict(ENTRY, **{"class": "reference_error"})], "other_pattern proves a rule_choice"),
        ([dict(ENTRY, decision="custom:other")], "no decision record custom:other"),
        ([dict(ENTRY, csr="-0.6 (0.40)")], "the entry says the CSR prints"),
        ([ENTRY, dict(ENTRY, cell="cell:Out1/r2/c1")], "a cell that does not differ"),
    ):
        compared = csr.compare(made_grid(), table)
        csr.judge(compared, entries, PLANNED, OURS, {"custom:d"})
        assert any(message in problem for problem in compared.problems), (message, compared)


@pytest.mark.parametrize(("change", "message"), [
    (lambda g: g["rows"][1].update(label="N"), "the grid has the row 'N'"),
    (lambda g: g["rows"][1].update(section="Week 4"), "the grid has the heading 'Week 4'"),
    (lambda g: g["rows"].pop(), "the grid has 5 lines under the header, the CSR 6"),
    (lambda g: g["columns"].reverse(), "the column labels"),
    (lambda g: g["titles"].pop(), "the titles"),
    (lambda g: g["rows"].pop(0), "the grid has 0 header rows"),
])
def test_a_grid_of_another_shape_is_seen(change, message):
    made = made_grid()
    change(made)
    compared = csr.compare(made, csr.parse(PAGE, "9-1.01"))
    assert any(message in problem for problem in compared.problems), compared.problems


def test_the_cells_section_of_an_exceptions_file(tmp_path):
    path = tmp_path / "exceptions.yaml"
    path.write_text(yaml.safe_dump({"exceptions": 0, "results": {}, "cells": {"Out1": [ENTRY]}}),
                    encoding="ascii")
    assert csr.load_exceptions(path) == {"Out1": [ENTRY]}
    for cells, message in (
        ({"Out1": [dict(ENTRY, note="x")]}, "exactly cell, csr, class, decision and proof"),
        ({"Out1": [ENTRY, ENTRY]}, "listed twice"),
        ({"Out2": [ENTRY]}, "must be the ID of a cell of Out2"),
        ({"Out1": [dict(ENTRY, **{"class": "other"})]}, "'class' must be one of"),
        ({"Out1": [dict(ENTRY, proof={"kind": "alternative"})]}, "needs a 'kind' out of"),
    ):
        path.write_text(yaml.safe_dump({"exceptions": 0, "cells": cells}), encoding="ascii")
        with pytest.raises(csr.CsrError, match=message):
            csr.load_exceptions(path)


# ---- the block kind `statistics` -------------------------------------------------------

STATISTICS = {
    "layout": 0, "output": displays.OUTPUT, "columns": {"grouping": "ARM"},
    "rows": [
        {"kind": "header", "cell": "{N}",
         "parts": {"N": {"analysis": "A_N", "operation": "M_N_n", "pattern": "(N=XX)"}}},
        {"kind": "statistics", "analysis": "A_AGE", "section": "Age", "indent": 1, "rows": [
            {"label": "n", "cell": "{n}", "parts": {"n": {"operation": "M_CONT_n",
                                                         "pattern": "X"}}},
            {"label": "Mean (SD)", "cell": "{m} ({s})",
             "parts": {"m": {"operation": "M_CONT_mean", "pattern": "X.X"},
                       "s": {"operation": "M_CONT_sd", "pattern": "X.XX"}}}]},
        {"kind": "statistics", "analysis": "A_AGE_P", "columns": ["Arm_B"], "rows": [
            {"label": "p-value", "indent": 2, "cell": "{p}",
             "parts": {"p": {"operation": "M_ANOVA_p"}}}]},
    ],
}


@pytest.fixture
def toy_event():
    return ars.index(displays.event_data())


def test_a_statistics_block_gives_a_row_per_statistic(root, toy_event):
    spec = layouts.parse(copy.deepcopy(STATISTICS))
    assert layouts.problems(spec, toy_event) == []
    rows = toy.run(root, displays.event_data())
    made = grid.build(toy_event, spec, rows)
    assert grid.grid_problems(made, root) == []
    # Ages of the safety set: arm A 61, 70, 55 and one missing; arm B 64, 72, 80; arm C none.
    assert [(row["label"], row.get("section"), row.get("indent", 0),
             [cell["text"] for cell in row["cells"]]) for row in made["rows"][1:3]] == [
        ("n", "Age", 1, ["3", "3", "0"]),
        ("Mean (SD)", "Age", 1, ["62.0 (7.55)", "72.0 (8.00)", " ()"])]
    p_row = made["rows"][3]
    assert (p_row["label"], p_row.get("section"), p_row["indent"]) == ("p-value", None, 2)
    # The test compares the arms: its one result stands in the one column the block lists.
    assert [cell["ard"] for cell in p_row["cells"]] == [[], ["ard:A_AGE_P/M_ANOVA_p/*"], []]
    assert [cell["text"] for cell in p_row["cells"]][::2] == ["", ""]
    assert p_row["cells"][1]["text"] == methods_text(rows["ard:A_AGE_P/M_ANOVA_p/*"])
    shell = grid.shell(toy_event, spec)
    assert [cell["text"] for cell in shell["rows"][3]["cells"]] == ["", "x.xxxx", ""]


def methods_text(row: dict) -> str:
    from specfirst.machine import methods

    return methods.pattern_text(row["raw_value"], "X.XXXX")


@pytest.mark.parametrize(("change", "message"), [
    (lambda d: d["rows"][2].pop("columns"), "'columns' lists one group"),
    (lambda d: d["rows"][2].update(columns=["Arm_A", "Arm_B"]), "'columns' lists one group"),
    (lambda d: d["rows"][1].update(columns=["Arm_Z"]), "'Arm_Z' is not a group of ARM"),
    (lambda d: d["rows"][1].update(analysis="A_SEX"), "only grouping is the column grouping"),
    (lambda d: d["rows"][1]["rows"][0]["parts"]["n"].update(operation="M_CAT_n"),
     "'M_CAT_n' is not an operation of its method"),
])
def test_a_statistics_block_that_does_not_fit_its_event(toy_event, change, message):
    data = copy.deepcopy(STATISTICS)
    change(data)
    found = layouts.problems(layouts.parse(data), toy_event)
    assert any(message in problem for problem in found), found


@pytest.mark.parametrize(("change", "message"), [
    (lambda d: d["rows"][1].pop("analysis"), "names its 'analysis'"),
    (lambda d: d["rows"][1].update(rows=[]), "lists its 'rows'"),
    (lambda d: d["rows"][1].update(analyses=["A_AGE"]), "unknown key 'analyses'"),
    (lambda d: d["rows"][1]["rows"][0].update(note="x"), "unknown key 'note'"),
    (lambda d: d["rows"][1]["rows"][0]["parts"]["n"].update(analysis="A_N"),
     "shows a result of the block's analysis"),
    (lambda d: d["rows"][1].update(columns=["Arm_A", "Arm_A"]), "lists each group once"),
    (lambda d: d["rows"][1].update(section="@header"), "that of a header block"),
])
def test_a_statistics_block_of_another_form_is_refused(change, message):
    data = copy.deepcopy(STATISTICS)
    change(data)
    with pytest.raises(layouts.LayoutError, match=message):
        layouts.parse(data)


# ---- the model-based methods: registry, ARS, engines -----------------------------------

PAIRWISE = {"id": "M_PW", "name": "Pairwise", "description": "Method registry: "
            "model.ancova.pairwise", "operations": [
                toy.operation("M_PW_d", "Difference of LS means", 1),
                toy.operation("M_PW_se", "Standard error", 2),
                toy.operation("M_PW_l", "Lower confidence limit", 3),
                toy.operation("M_PW_u", "Upper confidence limit", 4),
                toy.operation("M_PW_p", "P-value", 5)]}


def with_model(*parameters: dict) -> dict:
    data = toy.event_data()
    data["methods"].append(copy.deepcopy(PAIRWISE))
    data["analyses"].append(toy.analysis(
        "A_AGE_PW", "M_PW", "ADSL", "AGE", [("ARM", True)], analysisSetId="SAF",
        programmingCode={"context": "specfirst method registry", "parameters": list(
            parameters or ({"name": "factors", "value": ["SEX"]},
                           {"name": "reference", "value": ["Arm_A"]}))}))
    return data


def test_the_terms_of_a_model_are_read_and_bound(root):
    event = ars.index(with_model())
    assert ("model", "ADSL", "SEX") in ars.reads(event, "A_AGE_PW", "USUBJID")
    assert "SEX" in ars.columns(event, "USUBJID")["ADSL"]
    bound = ars.bind(event, registry.load(root))
    assert bound.options["A_AGE_PW"] == {"model.ancova.pairwise": {
        "confidence_level": 95, "covariates": [], "df": "residual", "factors": ["SEX"],
        "reference": "Arm_A"}}
    with pytest.raises(ars.ArsError, match="must name a group"):
        ars.bind(ars.index(with_model({"name": "factors", "value": ["SEX"]})), registry.load(root))
    with pytest.raises(ars.ArsError, match="with one value"):
        ars.bind(ars.index(with_model({"name": "reference", "value": ["Arm_A"]},
                                      {"name": "df", "value": ["residual", "asymptotic"]})),
                 registry.load(root))


def test_the_python_engine_leaves_a_model_based_analysis_to_r(root):
    with_it = toy.run(root, with_model())
    without = toy.run(root)
    assert with_it == without
    engine = toy.engine(root, with_model())
    assert engine.r_only("A_AGE_PW") and not engine.r_only("A_AGE")


def test_the_gold_ard_takes_the_r_engine_rows_of_model_based_methods(root):
    known = registry.load(root)
    python = [{"id": "ard:a", "method_id": "summary.continuous"}]
    r = [{"id": "ard:a", "method_id": "summary.continuous"},
         {"id": "ard:0", "method_id": "model.ancova.pairwise"}]
    assert build.gold_rows(python, r, known) == [r[1], python[0]]
    assert build.gold_rows(python, python, known) is python
    with pytest.raises(ard.EngineError, match="model-based method"):
        build.gold_rows(r, r, known)


def model_entry(root, **changes) -> dict:
    with open(root / "standard/methods/model.ancova.pairwise.yaml", encoding="ascii") as handle:
        data = yaml.safe_load(handle)
    data.update(changes)
    return data


@pytest.mark.parametrize(("changes", "message"), [
    ({"implementations": ["python", "r"]}, "implemented in R only"),
    ({"kind": "test"}, "only a model-based method takes columns"),
    ({"options": {"reference": {"takes": "group", "default": "Arm_A"}}}, "has no default"),
    ({"options": {"factors": {"takes": "columns", "default": ["X"]}}},
     "a list of columns has the default"),
    ({"options": {"factors": {"takes": "rows", "default": []}}}, "'takes' must be one of"),
])
def test_an_entry_of_a_model_based_method_that_is_not_valid(root, changes, message):
    with pytest.raises(registry.RegistryError, match=message):
        registry.parse_method(model_entry(root, **changes), "entry")


def test_the_options_of_a_model_are_resolved(root):
    known = registry.load(root)
    resolved = known.options("model.ancova.pairwise", {"reference": "Grp", "factors": ["SITE"]})
    assert resolved == {"confidence_level": 95, "covariates": [], "df": "residual",
                        "factors": ["SITE"], "reference": "Grp"}
    for given, message in (({}, "must name a group"),
                           ({"reference": "G", "factors": ["A", "A"]}, "distinct column"),
                           ({"reference": "G", "factors": ["1X"]}, "distinct column"),
                           ({"reference": "G", "factors": "SITE"}, "distinct column")):
        with pytest.raises(registry.RegistryError, match=message):
            known.options("model.ancova.pairwise", given)


# ---- the decision records against the reporting event ----------------------------------

TERMS = {"id": "custom:eff-model-terms", "unit": "tfl-efficacy-ancova",
         "value": {"rule": "terms", "factors": ["SEX"], "covariates": []},
         "status": "stated", "class": "study_input", "statement": "The model has SEX.",
         "binds": ["ars:A_AGE_PW"]}


def decision_problems(root, *records: dict) -> list[str]:
    event = ars.index(with_model())
    known = registry.load(root)
    _, found = decisions.problems(root, list(records), [(event, ars.bind(event, known))], known)
    return [problem for problem in found if "no record, and the reporting event" not in problem]


def test_a_decision_is_held_against_the_parameters_of_the_analyses_it_binds(root):
    assert decision_problems(root, TERMS) == []
    for record, message in (
        (dict(TERMS, value={"rule": "terms", "factors": ["ARM"], "covariates": []}),
         "has factors = ['SEX'], the decision factors = ['ARM']"),
        (dict(TERMS, binds=["ars:A_NONE"]), "binds ars:A_NONE, which no reporting event"),
        (dict(TERMS, binds=["ars:A_AGE"]), "no analysis it binds has the option factors"),
        (dict(TERMS, id="pop.efficacy.rule"), "has a custom ID"),
        (dict(TERMS, unit="efficacy"), "unit"),
        (dict(TERMS, **{"class": "document_rule"}), "citations"),
    ):
        found = decision_problems(root, record)
        assert any(message in problem for problem in found), (message, found)
    assert any("two records" in problem for problem in decision_problems(root, TERMS, TERMS))
