"""P4 by class on a reference study (issue #30, ADR-019): the classifier, the test study
SEP01 and the planted defects against each class (rule R5).

specfirst.machine.separation decides; specfirst.gen.separate builds; specfirst.gen.sep01
is the study. The matrix of SEP01 is built once per module (about a minute).
"""

from __future__ import annotations

import copy
import math
from types import SimpleNamespace

import pyarrow as pa
import pytest

from specfirst.gen import sep01, separate
from specfirst.machine import separation as sep
from specfirst.score import build as scores
from specfirst.score.candidate import Machine

# ---- the classifier, without builds ------------------------------------------------------


@pytest.mark.parametrize(("read", "levels", "klass"), [
    (True, ["outputs", "fails"], "separated"),
    (True, ["outputs", "none"], "unseparated"),
    (True, ["outputs", "adam", "none"], "unseparated"),
    (True, ["outputs", "adam"], "separated_at_dataset_only"),
    (True, ["results"], "separated_at_dataset_only"),
    (False, ["adam", "none"], "inert"),
    (False, ["outputs"], "inert"),
    (True, [], "no_alternative"),
    (False, [], "no_alternative"),
])
def test_the_class_of_a_decision_follows_from_the_levels_of_its_values(read, levels, klass):
    assert sep.classify(read, levels) == klass


def test_a_level_that_is_not_one_is_refused():
    with pytest.raises(ValueError):
        sep.classify(True, ["outputs", "printed"])


def test_only_separated_is_separated_in_the_decision_record():
    assert sep.identifiable("separated") == "separated"
    for klass in ("unseparated", "inert", "separated_at_dataset_only"):
        assert sep.identifiable(klass) == "unseparated"
    assert sep.identifiable("no_alternative") is None
    assert sep.credited({"identifiable": "separated"})
    assert not sep.credited({"identifiable": "unseparated"})
    assert not sep.credited({})


def _build(failure=None, adam=None, ard=None, grids=None):
    return SimpleNamespace(failure=failure, adam=adam or {}, ard=ard or {}, grids=grids or {})


def _grid(*texts, label="Any adverse event"):
    return {"titles": ["T"], "columns": [{"id": "c1", "label": "A"}],
            "rows": [{"id": "r1", "label": label,
                      "cells": [{"id": f"cell:O/r1/c{n}", "text": text}
                                for n, text in enumerate(texts, start=1)]}],
            "footnotes": []}


def test_two_builds_are_compared_at_three_layers():
    table = pa.table({"USUBJID": ["1", "2"], "X": [1.0, math.nan]})
    other = pa.table({"USUBJID": ["1", "2"], "X": [2.0, math.nan]})
    gold = _build(adam={"ADSL": table}, ard={"a": {"value": 1}}, grids={"O": _grid("1")})
    assert sep.compare(gold, gold) == sep.Comparison("none")
    assert sep.compare(gold, _build(adam={"ADSL": other}, ard={"a": {"value": 1}},
                                    grids={"O": _grid("1")})).level == "adam"
    found = sep.compare(gold, _build(adam={"ADSL": table}, ard={"a": {"value": 2}},
                                     grids={"O": _grid("1")}))
    assert (found.level, found.results, found.cells) == ("results", 1, 0)
    found = sep.compare(gold, _build(adam={"ADSL": other}, ard={"a": {"value": 2}},
                                     grids={"O": _grid("2")}))
    assert (found.level, found.adam, found.results, found.cells) == ("outputs", 1, 1, 1)
    assert sep.compare(gold, _build(adam={"ADSL": table}, ard={"a": {"value": 1}},
                                    grids={"O": _grid("1", label="Other")})).level == "outputs"
    assert sep.compare(gold, _build(adam={"ADSL": table}, ard={"a": {"value": 1}})).cells == 1
    failed = sep.compare(gold, _build(failure="ADaM: no subject"))
    assert (failed.level, failed.failure) == ("fails", "ADaM: no subject")
    with pytest.raises(ValueError):
        sep.compare(_build(failure="compile: no"), gold)


def test_the_interval_says_what_ends_it_on_each_side():
    levels = {34: "outputs", 36: "none", 37: "adam", 38: "none", 39: "fails"}
    span = sep.interval("days", 35, levels, 5, 65, 0, None)
    assert (span["low"], span["high"], span["below"], span["above"]) == (
        35, 38, "separated", "separated")
    assert (span["same"], span["dataset_only"]) == ([36, 38], [37])
    span = sep.interval("days", 1, {0: "none", 2: "none", 3: "none"}, 0, 3, 0, None)
    assert (span["low"], span["below"], span["high"], span["above"]) == (
        0, "slot_minimum", 3, "scan_limit")
    span = sep.interval("n", 5, {4: "none", 6: "outputs"}, 4, 6, 4, 6)
    assert (span["low"], span["below"]) == (4, "slot_minimum")
    with pytest.raises(ValueError):
        sep.interval("days", 35, {34: "outputs"}, 5, 65, 0, None)


def test_the_review_asks_unseparated_decisions_first():
    matrix = {"decisions": [
        {"id": "a", "unit": "u", "class": "inert"},
        {"id": "b", "unit": "u", "class": "separated"},
        {"id": "c", "unit": "u", "class": "separated_at_dataset_only", "outputs": ["O"]},
        {"id": "d", "unit": "u", "class": "unseparated", "reproduce": ["x"]},
    ]}
    found = sep.review(matrix)
    assert [entry["id"] for entry in found] == ["d", "c", "b", "a"]
    assert [entry["asked"] for entry in found] == [True, True, False, False]
    assert found[0]["reproduce"] == ["x"] and found[1]["outputs"] == ["O"]


def test_an_inert_decision_whose_value_changes_an_output_is_a_problem():
    item = {"id": "x", "unit": "u", "class": "inert", "read": False, "intervals": [],
            "values": [{"label": "other", "level": "outputs"}]}
    assert sep.problems(item) == ["x (u): inert, yet other changes the outputs"]
    item["values"] = [{"label": "other", "level": "adam"}]
    assert sep.problems(item) == []
    item["class"] = "separated"
    assert sep.problems(item) == ["x (u): the class is separated; its values give inert"]


# ---- SEP01 -----------------------------------------------------------------------------


@pytest.fixture(scope="module")
def machine(root):
    return Machine(root)


@pytest.fixture(scope="module")
def records(machine):
    return sep01.records(machine.catalog, machine.house)


@pytest.fixture(scope="module")
def mutation(machine, records):
    return separate.Mutation(machine, sep01.data(), sep01.ARMS, records)


@pytest.fixture(scope="module")
def matrix(mutation):
    return mutation.matrix(study="sep01")


def _item(matrix, key):
    return next(item for item in matrix["decisions"] if (item["id"], item["unit"]) == key)


def test_the_gold_decisions_build_the_table_worked_out_by_hand(mutation):
    table = scores.table_of(mutation.gold.grids[sep01.OUTPUT])
    assert {(row[1], column[0]): cell["text"] for (row, column), cell in table.cells.items()} \
        == sep01.expected_cells()


def test_the_study_states_two_decisions_and_takes_the_house_for_the_rest(machine, records):
    stated = {(r["id"], r["unit"]): r["value"] for r in records
              if (r["id"], r["unit"]) in sep01.STATED}
    assert stated == sep01.STATED
    assert {r["value"]["rule"] for r in records if r["id"] == "tfl.output.include"
            and r["unit"] != "tfl-ae-summary"} == {"not_included"}


def test_a_window_that_four_values_reproduce(matrix):
    item = _item(matrix, sep01.WINDOW)
    assert item["class"] == "unseparated" and item["identifiable"] == "unseparated"
    assert item["intervals"] == [sep01.INTERVAL]
    assert item["reproduce"] == [f"last_dose_plus_days(days={days})" for days in (36, 37, 38)]
    levels = {value["label"]: value["level"] for value in item["values"]}
    assert levels["last_dose_plus_days(days=34)"] == "outputs"
    assert levels["last_dose_plus_days(days=39)"] == "outputs"
    assert levels["no_end"] == "outputs"  # catalog@2 has no end at the end of the study


def test_an_inert_rule_changes_adam_and_no_output_reads_it(matrix):
    item = _item(matrix, ("date.studyday.origin", "mod-treatment"))
    assert (item["class"], item["read"], item["outputs"]) == ("inert", False, [])
    assert [(value["level"], value["cells"], value["adam"] > 0) for value in item["values"]] == [
        ("adam", 0, True)]
    assert item["identifiable"] == "unseparated"


def test_a_rule_separated_in_adam_and_not_in_the_table(matrix):
    item = _item(matrix, ("ae.start.imputation", "mod-ae-emergence"))
    assert item["class"] == "separated_at_dataset_only"
    assert item["outputs"] == [sep01.OUTPUT] and item["read"]
    assert {value["level"] for value in item["values"]} == {"adam"}
    assert all(value["adam"] > 0 and value["results"] == 0 and value["cells"] == 0
               for value in item["values"])
    assert item["dataset_only"] == ["first_of_month", "not_completed"]


def test_every_decision_of_the_slice_has_the_class_the_study_states(matrix):
    assert {(item["id"], item["unit"]): item["class"] for item in matrix["decisions"]} \
        == sep01.CLASSES
    assert sep01.check(matrix) == []
    assert matrix["problems"] == []
    assert {klass: len(names) for klass, names in matrix["summary"].items()
            if klass in sep.CLASSES} == {"separated": 7, "unseparated": 9, "inert": 5,
                                         "separated_at_dataset_only": 1}


def test_the_decision_record_takes_separated_only_for_the_separated_class(matrix):
    for item in matrix["decisions"]:
        assert item["identifiable"] == ("separated" if item["class"] == "separated"
                                        else "unseparated")


def test_the_review_lists_the_unseparated_decisions_first(matrix):
    classes = [entry["class"] for entry in matrix["review"]]
    assert classes == sorted(classes, key=sep.REVIEW_ORDER.index)
    assert classes[0] == "unseparated"
    assert all(entry["asked"] == (entry["class"] in sep.ASKED) for entry in matrix["review"])


def test_a_new_mutation_gives_the_matrix_again(mutation, matrix):
    again = mutation.matrix(study="sep01")
    again["summary"]["builds"] = matrix["summary"]["builds"]
    assert sep.differences(matrix, again) == []
    assert again["decisions"] == matrix["decisions"]


@pytest.mark.parametrize(("gold", "span", "expected"), [
    # The events of SEP01 start 7 (H2), 35 (P2) and 39 (L2) days after a last dose: a
    # window of 0 to 6 days gives the table of 3 days. The slot's minimum is 0.
    (3, 30, (0, "slot_minimum", 6, "separated", [0, 1, 2, 4, 5, 6])),
    (3, 2, (1, "scan_limit", 5, "scan_limit", [1, 2, 4, 5])),
    (35, 3, (35, "separated", 38, "scan_limit", [36, 37, 38])),
])
def test_the_scan_stops_at_the_bound_of_the_slot_and_at_its_span(machine, gold, span, expected):
    # Cases of the review of issue #30 (F1): a scan that builds no value at a limit, or that
    # ignores the minimum of the slot, fails here and passed every other test.
    vector = separate.house_vector(machine.catalog, machine.house, {
        **sep01.STATED, sep01.WINDOW: {"rule": "last_dose_plus_days", "days": gold}})
    made = separate.Mutation(machine, sep01.data(), sep01.ARMS, vector, span).matrix(
        study="sep01, scan", keys=[sep01.WINDOW])
    item = _item(made, sep01.WINDOW)
    (span_found,) = item["intervals"]
    assert (span_found["low"], span_found["below"], span_found["high"], span_found["above"],
            span_found["same"]) == expected
    labels = [value["label"] for value in item["values"]]
    assert len(labels) == len(set(labels))
    assert all(value["value"]["days"] >= 0 for value in item["values"] if "days" in value["value"])
    assert made["problems"] == []


# ---- planted defects: each makes the check of one class fail (rule R5) -----------------


@pytest.mark.parametrize("name", ["separated", "unseparated", "separated_at_dataset_only"])
def test_planted_data_make_the_check_of_one_class_fail(machine, records, matrix, name):
    key = sep01.PLANTED_DECISION[name]
    assert _item(matrix, key)["class"] == name
    planted = separate.Mutation(machine, sep01.planted(name), sep01.ARMS, records).matrix(
        study=f"sep01, planted {name}", keys=[key])
    found = sep01.check(planted)
    assert found and all(line.startswith(f"{key[0]} ({key[1]})") for line in found), found
    item = _item(planted, key)
    assert item["class"] != name
    if name == "unseparated":
        # One more event, 36 days after a last dose: every other window now separates.
        assert item["class"] == "separated"
        assert item["intervals"][0]["low"] == item["intervals"][0]["high"] == 35


def test_a_planted_reach_makes_the_check_of_inert_fail(machine, records, matrix):
    keys = [sep01.PLANTED_DECISION["inert"], sep01.WINDOW]
    planted = separate.Mutation(machine, sep01.data(), sep01.ARMS, records,
                                reach_of=lambda build: {}).matrix(study="sep01, planted reach",
                                                                  keys=keys)
    assert [item["class"] for item in planted["decisions"]] == ["inert", "inert"]
    window = f"{sep01.WINDOW[0]} ({sep01.WINDOW[1]})"
    assert planted["problems"] and all(line.startswith(f"{window}: inert, yet ")
                                       for line in planted["problems"])
    assert any(line.startswith(window) for line in sep01.check(planted))


def test_a_planted_matrix_differs_from_a_new_mutation(matrix):
    written = copy.deepcopy(matrix)
    _item(written, sep01.WINDOW)["intervals"][0]["high"] = 40
    _item(written, ("tfl.rounding.rule", "tfl-ae-summary"))["class"] = "separated"
    found = sep.differences(written, matrix)
    assert len(found) == 2
    assert found[0].startswith("ae.teae.end (mod-ae-emergence): intervals")
    assert found[1].startswith("tfl.rounding.rule (tfl-ae-summary): class")


# ---- the pilot's arms --------------------------------------------------------------------


def test_the_arms_of_a_study_come_from_dm_and_ex_in_the_order_of_the_dose():
    # As in the pilot: the screen failures have the code Scrnfail and no exposure, and the
    # high dose is titrated (54 mg, then 81 mg). The first run on the pilot stopped on each.
    dm = pa.table({"USUBJID": ["1", "2", "3", "4"], "ARMCD": ["Hi", "Pbo", "Lo", "Scrnfail"],
                   "ARM": ["High", "Placebo", "Low", "Screen Failure"]})
    ex = pa.table({"USUBJID": ["1", "1", "2", "3"], "EXTRT": ["DRUG", "DRUG", "PLACEBO", "DRUG"],
                   "EXDOSE": [54.0, 81.0, 0.0, 54.0]})
    arms = separate.pilot_arms(SimpleNamespace(sdtm={"dm": dm, "ex": ex}))
    assert arms == [{"code": "Pbo", "dose": 0.0, "names": ["PLACEBO", "Placebo"]},
                    {"code": "Lo", "dose": 54.0, "names": ["Low"]},
                    {"code": "Hi", "dose": 81.0, "names": ["High"]}]
    same = pa.table({"USUBJID": ["1", "2", "3"], "EXTRT": ["DRUG", "PLACEBO", "DRUG"],
                     "EXDOSE": [54.0, 0.0, 54.0]})
    with pytest.raises(separate.SeparationError):
        separate.pilot_arms(SimpleNamespace(sdtm={"dm": dm, "ex": same}))
