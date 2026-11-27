"""The Python result engine on the made-up study of tests/toy_results.py.

The expected values are worked out by hand from the tables there. The
last tests run the R engine on the same inputs (skipped where R is not
installed) and plant inputs the engine must refuse.
"""

from __future__ import annotations

import math

import numpy as np
import pytest
import toy_results as toy

from specfirst import schemas
from specfirst.machine import ard, ars, methods, registry, rengine, results

pa = pytest.importorskip("pyarrow")

HASH_OF_NO_OPTIONS = "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a"


@pytest.fixture(scope="module")
def rows(root):
    return toy.run(root)


def value(rows, key):
    return rows[f"ard:{key}"]["raw_value"]


def test_every_row_fits_the_schema_and_the_rows_are_sorted(root, rows):
    assert len(rows) == 67
    assert list(rows) == sorted(rows)
    validator = schemas.validator("ard", root=root)
    for row in rows.values():
        assert list(validator.iter_errors(row)) == [], row
    assert results.ard_problems(list(rows.values()), root) == []
    row = rows["ard:A_SEX/M_CAT_pct/Arm_B/Sex_F"]
    assert row == {
        "id": "ard:A_SEX/M_CAT_pct/Arm_B/Sex_F", "analysis_id": "A_SEX",
        "operation_id": "M_CAT_pct", "group1_groupingId": "ARM", "group1_groupId": "Arm_B",
        "group2_groupingId": "SEX", "group2_groupId": "Sex_F", "method_id": "percent.subjects",
        "method_options_hash": HASH_OF_NO_OPTIONS, "raw_value": 100 / 3,
    }


def test_counts_and_percents_with_a_referenced_denominator(rows):
    # Rule I8: a group that is defined gives results, with or without records.
    assert [value(rows, f"A_N/M_N_n/Arm_{arm}") for arm in "ABC"] == [4, 3, 0]
    assert [value(rows, f"A_SEX/M_CAT_n/Arm_A/Sex_{sex}") for sex in "FM"] == [2, 2]
    assert [value(rows, f"A_SEX/M_CAT_n/Arm_B/Sex_{sex}") for sex in "FM"] == [1, 2]
    assert value(rows, "A_SEX/M_CAT_pct/Arm_A/Sex_F") == 50.0
    assert value(rows, "A_SEX/M_CAT_pct/Arm_B/Sex_M") == pytest.approx(200 / 3, rel=1e-15)
    # percent.subjects, statement 4: a denominator of 0 gives a missing result.
    assert value(rows, "A_SEX/M_CAT_n/Arm_C/Sex_F") == 0
    assert value(rows, "A_SEX/M_CAT_pct/Arm_C/Sex_F") is None
    assert isinstance(value(rows, "A_N/M_N_n/Arm_A"), int)


def test_subjects_are_counted_once_and_only_in_the_set_and_the_subset(rows):
    # S1 has two records of one event; S6's other event has no flag; S8 is not in the set.
    assert [value(rows, f"A_TEAE/M_CAT_n/Arm_{arm}") for arm in "ABC"] == [2, 2, 0]
    assert value(rows, "A_TEAE/M_CAT_pct/Arm_A") == 50.0
    assert value(rows, "A_TEAE/M_CAT_pct/Arm_B") == pytest.approx(200 / 3, rel=1e-15)


def test_data_driven_groups_are_the_combinations_that_occur(rows):
    cells = sorted(key.split("/", 3)[3] for key in rows
                   if key.startswith("ard:A_SOC/M_CAT_n/Arm_A"))
    # Rule I9: no (CARD, RASH), which no record has; GI has no flagged record.
    assert cells == ["=CARD/=AF", "=CARD/=MI", "=SKIN/=RASH"]
    assert value(rows, "A_SOC/M_CAT_n/Arm_A/=CARD/=AF") == 1
    assert value(rows, "A_SOC/M_CAT_n/Arm_A/=CARD/=MI") == 0
    assert value(rows, "A_SOC/M_CAT_pct/Arm_B/=SKIN/=RASH") == pytest.approx(100 / 3, rel=1e-15)
    row = rows["ard:A_SOC/M_CAT_n/Arm_B/=CARD/=MI"]
    assert (row["group2_groupingId"], row["group2_groupValue"]) == ("SOC", "CARD")
    assert "group2_groupId" not in row and row["group3_groupValue"] == "MI"


def test_continuous_summary_leaves_missing_values_out(rows):
    def stats(arm):
        return {name: value(rows, f"A_AGE/M_CONT_{name}/Arm_{arm}")
                for name in ("n", "mean", "sd", "median", "q1", "q3", "min", "max")}

    assert stats("A") == {"n": 3, "mean": 62.0, "sd": pytest.approx(math.sqrt(57), rel=1e-15),
                          "median": 61.0, "q1": 55.0, "q3": 70.0, "min": 55.0, "max": 70.0}
    assert stats("B") == {"n": 3, "mean": 72.0, "sd": 8.0, "median": 72.0, "q1": 64.0,
                          "q3": 80.0, "min": 64.0, "max": 80.0}
    assert stats("C") == {"n": 0, "mean": None, "sd": None, "median": None, "q1": None,
                          "q3": None, "min": None, "max": None}


def test_the_tests_get_their_tables_from_the_compared_groupings(rows):
    # Rule I12c: one compared grouping, the values per group.
    row = rows["ard:A_AGE_P/M_ANOVA_p/*"]
    assert row["raw_value"] == methods.anova_oneway_p([[61, 70, 55], [64, 72, 80]])
    assert row["group1_groupingId"] == "ARM" and "group1_groupId" not in row
    assert row["method_id"] == "test.anova.oneway"
    # Rule I12a: two compared groupings, subjects by arm and sex; arm C has none.
    assert value(rows, "A_SEX_P/M_CHISQ_p/*/*") == methods.chisq_p([[2, 2], [1, 2]])
    # Rules I12b and I13: subjects with an event against the rest of the population.
    assert value(rows, "A_SOC_P/M_FISHER_p/*/=CARD") == methods.fisher_exact_p([[1, 3], [1, 2]])
    assert value(rows, "A_SOC_P/M_FISHER_p/*/=SKIN") == methods.fisher_exact_p([[1, 3], [1, 2]])


def test_the_population_is_the_set_within_the_subject_part_of_the_subset(root):
    """Rule I13: "arms A and B" in the data subset is what limits the population."""
    data = toy.event_data()
    subset = next(s for s in data["dataSubsets"] if s["id"] == "TEAE_AB")
    # Only arm B: one group is left, and a test on one group has no result.
    subset["compoundExpression"]["whereClauses"][1] = toy.condition("ADSL", "ARM", "EQ", "B")
    rows = toy.run(root, data)
    assert rows["ard:A_SOC_P/M_FISHER_p/*/=CARD"]["raw_value"] is None
    # A subject with an event outside the safety set does not enter the table: S8.
    data = toy.event_data()
    data["analysisSets"][0]["condition"]["value"] = ["N"]  # now only S8 is in the set
    rows = toy.run(root, data)
    assert [rows[f"ard:A_N/M_N_n/Arm_{arm}"]["raw_value"] for arm in "ABC"] == [0, 1, 0]
    assert rows["ard:A_SOC_P/M_FISHER_p/*/=CARD"]["raw_value"] is None  # one arm, one subject
    # The test needs an analysis set, and counts subjects.
    data = toy.event_data()
    del next(a for a in data["analyses"] if a["id"] == "A_SOC_P")["analysisSetId"]
    with pytest.raises(ard.EngineError, match="needs an analysis set"):
        toy.run(root, data)
    data = toy.event_data()
    next(a for a in data["analyses"] if a["id"] == "A_SOC_P")["variable"] = "AEDECOD"
    with pytest.raises(ard.EngineError, match="analysis variable must be USUBJID"):
        toy.run(root, data)


def test_a_method_option_changes_the_values_and_the_hash(root, rows):
    other = toy.run(root, binding={"options": {"summary.continuous": {"quantile_definition":
                                                                    "r7"}}})
    key = "ard:A_AGE/M_CONT_q1/Arm_A"
    assert (rows[key]["raw_value"], other[key]["raw_value"]) == (55.0, 58.0)
    assert rows[key]["method_options_hash"] != other[key]["method_options_hash"]
    assert rows[key]["method_options_hash"] == registry.load(root).options_hash(
        "summary.continuous")
    # The rows of other methods keep their hash.
    assert other["ard:A_N/M_N_n/Arm_A"] == rows["ard:A_N/M_N_n/Arm_A"]
    # An analysis can state the option itself; it wins over what the caller gives.
    data = toy.event_data()
    next(a for a in data["analyses"] if a["id"] == "A_AGE")["programmingCode"] = {
        "context": ars.REGISTRY_CONTEXT,
        "parameters": [{"name": "quantile_definition", "value": ["r7"]}]}
    stated = toy.run(root, data)
    assert stated[key] == other[key]


def test_conditions_and_missing_values():
    """Rule I3, on one column: text, numbers, and what a missing value does."""
    text = np.array(["A", "B", "", "2020-01-10"], dtype=object)
    assert ard.compare(text, "text", "EQ", ["A"]).tolist() == [True, False, False, False]
    assert ard.compare(text, "text", "NE", ["A"]).tolist() == [False, True, True, True]
    assert ard.compare(text, "text", "IN", ["A", "B"]).tolist() == [True, True, False, False]
    assert ard.compare(text, "text", "NOTIN", ["A", "B"]).tolist() == [False, False, True, True]
    assert ard.compare(text, "text", "EQ", [""]).tolist() == [False, False, True, False]
    # An ordered comparison with a missing value is false, in both directions.
    assert ard.compare(text, "text", "GE", ["B"]).tolist() == [False, True, False, False]
    assert ard.compare(text, "text", "LT", ["B"]).tolist() == [True, False, False, True]
    numbers = np.array([1.0, 2.5, np.nan])
    assert ard.compare(numbers, "number", "EQ", ["1"]).tolist() == [True, False, False]
    assert ard.compare(numbers, "number", "NE", ["1"]).tolist() == [False, True, True]
    assert ard.compare(numbers, "number", "IN", ["1", "2.5"]).tolist() == [True, True, False]
    assert ard.compare(numbers, "number", "NOTIN", ["1"]).tolist() == [False, True, True]
    assert ard.compare(numbers, "number", "GT", ["1"]).tolist() == [False, True, False]
    assert ard.compare(numbers, "number", "LE", ["2.5"]).tolist() == [True, True, False]
    with pytest.raises(ard.EngineError, match="number column is compared"):
        ard.compare(numbers, "number", "EQ", ["high"])


def test_a_condition_on_another_dataset_goes_by_subject(root):
    """Rule I4, with a compound expression: OR, and NOT."""
    data = toy.event_data()
    data["dataSubsets"].append({"id": "ANY", "name": "has a skin event, or is not female",
                                "compoundExpression": {"logicalOperator": "OR", "whereClauses": [
                                    toy.condition("ADAE", "AESOC", "EQ", "SKIN"),
                                    {"compoundExpression": {"logicalOperator": "NOT",
                                                            "whereClauses": [toy.condition(
                                                                "ADSL", "SEX", "EQ", "F")]}}]}})
    data["analyses"].append(toy.analysis("A_ANY", "M_N", "ADSL", "USUBJID", [("ARM", True)],
                                         analysisSetId="SAF", dataSubsetId="ANY"))
    rows = toy.run(root, data)
    # Arm A: S1 and S2 have a skin event (S1's is not treatment-emergent, which this
    # subset does not ask), S3 and S4 are male. Arm B: S6 and S7; S5 is female, no skin event.
    assert [rows[f"ard:A_ANY/M_N_n/Arm_{arm}"]["raw_value"] for arm in "AB"] == [4, 2]


def test_group_values_are_encoded_in_the_row_id(root):
    adae = dict(toy.ADAE, AESOC=["CARD / heart", *toy.ADAE["AESOC"][1:]])
    rows = toy.run(root, given=toy.tables(adae=adae))
    key = "ard:A_SOC/M_CAT_n/Arm_A/=CARD%20%2F%20heart/=AF"
    assert rows[key]["group2_groupValue"] == "CARD / heart" and rows[key]["raw_value"] == 1
    assert all(" " not in row_id for row_id in rows)


def test_numbers_and_dates_as_group_values():
    table = ard.table_from_arrow("X", pa.table({
        "N": pa.array([8, 8, 2, None], pa.int64()),
        "F": [1.5, 1.5, None, 0.1],
        "D": pa.array([None, 18263, 18264, 18264], pa.date32()),
        "B": [True, None, False, True],
    }))
    assert table.kinds == {"N": "number", "F": "number", "D": "text", "B": "text"}
    assert table.columns["D"].tolist() == ["", "2020-01-02", "2020-01-03", "2020-01-03"]
    assert table.columns["B"].tolist() == ["true", "", "false", "true"]
    assert math.isnan(table.columns["N"][3]) and math.isnan(table.columns["F"][2])
    assert [ard._number_text(v) for v in (8.0, 1.5, 0.1, -3.0)] == ["8", "1.5", "0.1", "-3"]


@pytest.mark.parametrize("value", [math.inf, -math.inf])
def test_a_number_that_is_not_finite_is_no_group_value(root, value):
    """The last sentence of rule I9 in the Python engine too (the review of real-3a, F8):
    the R engine refused it, the Python engine wrote the row `.../=inf`."""
    with pytest.raises(ard.EngineError, match="not finite"):
        ard._number_text(value)
    # A number column that only a data-driven grouping reads.
    adsl = dict(toy.ADSL, SCORE=[1.0, value, 2.0, 2.0, 1.0, 1.0, 2.0, 1.0])
    data = toy.event_data()
    data["analysisGroupings"].append(
        {"id": "BYSCORE", "name": "Score", "groupingDataset": "ADSL",
         "groupingVariable": "SCORE", "dataDriven": True})
    data["analyses"].append(toy.analysis("A_BYSCORE", "M_N", "ADSL", "USUBJID",
                                         [("BYSCORE", True)]))
    with pytest.raises(ard.EngineError, match="ADSL.SCORE: the number .* is not finite"):
        toy.run(root, data, given=toy.tables(adsl=adsl))


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda d: d["methods"][3].pop("description"), "is not bound to the method registry"),
        (lambda d: d["analyses"][2].update(variable="SEX"), "holds text; this method needs"),
        (lambda d: d["analyses"][0].update(dataset="ADXX"), "dataset ADXX was not handed"),
        (lambda d: d["analyses"][0].update(variable="NOSUCH"), "has no column NOSUCH"),
        (lambda d: d["analyses"][1]["referencedAnalysisOperations"].pop(),
         "does not say which analysis gives the DENOMINATOR"),
        (lambda d: d["analyses"][1]["referencedAnalysisOperations"][1].update(analysisId="A_SEX"),
         "0 results of A_SEX.M_N_n fit the cell as DENOMINATOR"),
        (lambda d: d["analyses"][3]["orderedGroupings"].append(
            {"order": 2, "groupingId": "SEX", "resultsByGroup": False}),
         "analysis of variance compares one grouping, found 2"),
        (lambda d: d["analyses"][4]["orderedGroupings"].clear(),
         "compares one or two groupings, found 0"),
        (lambda d: d["analyses"][0].update(methodId="M_NONE"), "method 'M_NONE' is not defined"),
    ],
)
def test_inputs_the_engine_refuses(root, change, message):
    data = toy.event_data()
    change(data)
    with pytest.raises((ard.EngineError, ars.ArsError), match=message):
        event = ars.index(data)
        known = registry.load(root)
        tables = toy.tables()
        ard.run(event, known, ars.bind(event, known), tables)


def test_a_subject_with_two_values_of_a_grouping_variable_is_refused(root):
    data = toy.event_data()
    # Group the events by a variable of ADAE read through another dataset: SEX from ADSL
    # is fine, but a grouping read from ADAE into ADSL has several records per subject.
    data["analysisGroupings"].append({
        "id": "SOC_OF_SUBJECT", "name": "x", "groupingDataset": "ADAE",
        "groupingVariable": "AESOC", "dataDriven": True})
    data["analyses"].append(toy.analysis("A_BAD", "M_N", "ADSL", "USUBJID",
                                         [("SOC_OF_SUBJECT", True)], analysisSetId="SAF"))
    with pytest.raises(ard.EngineError, match="has two values of ADAE.AESOC"):
        toy.run(root, data)


def test_analyses_that_reference_each_other_in_a_circle_are_refused(root):
    data = toy.event_data()
    # The denominator of A_SEX is A_TEAE, and that of A_TEAE is A_SEX, through M_CAT_n.
    data["methods"][1]["operations"][1]["referencedOperationRelationships"][1][
        "operationId"] = "M_CAT_n"
    data["analyses"][1]["referencedAnalysisOperations"][1]["analysisId"] = "A_TEAE"
    data["analyses"][5]["referencedAnalysisOperations"][1]["analysisId"] = "A_SEX"
    with pytest.raises(ard.EngineError, match="reference each other in a circle"):
        toy.run(root, data)


def test_the_r_engine_gives_the_same_rows(root, rows, tmp_path):
    if not rengine.available():
        pytest.skip("Rscript is not installed")
    event = ars.index(toy.event_data())
    known = registry.load(root)
    path = tmp_path / "event.json"
    path.write_text(__import__("json").dumps(event.data), encoding="ascii")
    tables = toy.tables()
    found, meta, said = rengine.run(root, tmp_path / "work", path, registry.json_path(root),
                                    ars.bind(event, known), tables, "USUBJID")
    assert "R engine: 8 analyses, 67 rows" in said
    assert rengine.data_problems(meta, tables) == []
    assert results.ard_problems(found, root) == []
    lines, problems = results.agreement(rows, results.by_id(found))
    assert problems == [], problems
    assert "67 results in both, 0 disagree" in lines[0]
    # With another option in the R engine alone, the two are seen to disagree.
    other, _, _ = rengine.run(
        root, tmp_path / "work2", path, registry.json_path(root),
        ars.bind(event, known, {"options": {"summary.continuous": {"quantile_definition": "r7"}}}),
        tables, "USUBJID")
    _, problems = results.agreement(rows, results.by_id(other))
    assert any("A_AGE/M_CONT_q1/Arm_A" in problem for problem in problems)
