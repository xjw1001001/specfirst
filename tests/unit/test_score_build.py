"""The build score (ADR-005, decision 4): four scores, each with its denominator.

Every test plants one difference in a candidate grid and asks for the
numbers a person would count on the two tables.
"""

from __future__ import annotations

import pyarrow as pa

from specfirst.score.build import (
    adam_differences,
    ard_differences,
    compare_output,
    score,
    table_of,
)

COLUMNS = ["Placebo", "Drug", "Total"]
ROWS = {"": ["(N=2)", "(N=3)", "(N=5)"], "Any event": ["1 ( 50.0)", "2 ( 66.7)", "3 ( 60.0)"],
        "Serious event": ["0", "1 ( 33.3)", "1 ( 20.0)"]}


def grid(rows=None, columns=None, output="Out_A"):
    columns = COLUMNS if columns is None else columns
    rows = ROWS if rows is None else rows
    made = []
    for number, (label, texts) in enumerate(rows.items(), start=1):
        record = {"id": f"r{number}", "label": label.rstrip("#"), "cells": [
            {"id": f"cell:{output}/r{number}/c{n}", "column": f"c{n}", "text": text, "ard": []}
            for n, text in enumerate(texts, start=1)]}
        if label == "":
            record["section"] = "@header"
        made.append(record)
    return {"schema": "specfirst/grid@0", "output_id": output, "titles": [], "footnotes": [],
            "columns": [{"id": f"c{n}", "label": label} for n, label in enumerate(columns, 1)],
            "rows": made}


def numbers(found):
    return (found.produced, found.in_gold, found.correct, found.denominators(), found.strict,
            found.lenient)


def test_the_same_grid_is_right_in_every_score():
    found = score("visible", {"Out_A": grid()}, {"Out_A": grid()})
    assert numbers(found) == (1, 1, 9, {"shared_rows": 9, "produced": 9, "all": 9}, 1, 1)
    assert found.perfect and found.wrong() == []


def test_the_header_row_counts_like_any_row():
    rows = {**ROWS, "": ["(N=2)", "(N=4)", "(N=5)"]}
    found = score("visible", {"Out_A": grid()}, {"Out_A": grid(rows)})
    assert found.correct == 8
    wrong = found.wrong()[0]
    assert (wrong.row, wrong.column, wrong.gold, wrong.candidate, wrong.reason) == (
        ("@header", "", 1), ("Drug", 1), "(N=3)", "(N=4)", "differs")


def test_a_row_the_candidate_lacks_leaves_the_first_denominator():
    rows = {label: texts for label, texts in ROWS.items() if label != "Serious event"}
    found = score("visible", {"Out_A": grid()}, {"Out_A": grid(rows)})
    assert numbers(found) == (1, 1, 6, {"shared_rows": 6, "produced": 9, "all": 9}, 0, 0)
    assert {cell.reason for cell in found.wrong()} == {"no_row"}
    # The row after a missing row is still the same row: position does not count.
    rows = {label: texts for label, texts in ROWS.items() if label != "Any event"}
    assert score("visible", {"Out_A": grid()}, {"Out_A": grid(rows)}).correct == 6


def test_a_missing_column_is_wrong_in_the_rows_both_have():
    rows = {label: texts[:2] for label, texts in ROWS.items()}
    found = score("visible", {"Out_A": grid()}, {"Out_A": grid(rows, COLUMNS[:2])})
    assert numbers(found) == (1, 1, 6, {"shared_rows": 9, "produced": 9, "all": 9}, 0, 0)
    assert {cell.reason for cell in found.wrong()} == {"no_column"}
    assert not found.outputs[0].columns_equal and found.outputs[0].rows_equal


def test_more_rows_and_columns_pass_lenient_and_fail_strict():
    rows = {**{label: [*texts, "x"] for label, texts in ROWS.items()},
            "Fatal event": ["0", "0", "0", "x"]}
    found = score("visible", {"Out_A": grid()}, {"Out_A": grid(rows, [*COLUMNS, "More"])})
    assert numbers(found) == (1, 1, 9, {"shared_rows": 9, "produced": 9, "all": 9}, 0, 1)
    output = found.outputs[0]
    assert output.extra_rows == [("", "Fatal event", 1)]
    assert output.extra_columns == [("More", 1)]
    assert not found.perfect


def test_another_order_of_columns_or_rows_fails_strict_only():
    order = [2, 0, 1]
    rows = {label: [texts[i] for i in order] for label, texts in ROWS.items()}
    found = score("visible", {"Out_A": grid()},
                  {"Out_A": grid(rows, [COLUMNS[i] for i in order])})
    assert numbers(found) == (1, 1, 9, {"shared_rows": 9, "produced": 9, "all": 9}, 0, 1)
    turned = dict(reversed(list(ROWS.items())))
    found = score("visible", {"Out_A": grid()}, {"Out_A": grid(turned)})
    assert (found.correct, found.strict, found.lenient) == (9, 0, 1)
    assert not found.outputs[0].rows_equal and found.outputs[0].columns_equal


def test_an_output_that_was_not_produced_counts_in_the_third_denominator_only():
    gold = {"Out_A": grid(), "Out_B": grid(output="Out_B")}
    found = score("twin", gold, {"Out_A": grid()}, not_produced={"Out_B": "display: no rule"})
    assert numbers(found) == (1, 2, 9, {"shared_rows": 9, "produced": 9, "all": 18}, 1, 1)
    assert found.outputs[1].why_not == "display: no rule"
    assert {cell.reason for cell in found.wrong()} == {"not_produced"}
    nothing = score("twin", gold, {}, valid=False, failure="compile: no value")
    assert numbers(nothing) == (0, 2, 0, {"shared_rows": 0, "produced": 0, "all": 18}, 0, 0)
    assert nothing.outputs[0].why_not == "compile: no value" and not nothing.perfect


def test_an_output_that_gold_does_not_have():
    found = score("visible", {"Out_A": grid()},
                  {"Out_A": grid(), "Out_B": grid(output="Out_B")})
    assert found.extra_outputs == ["Out_B"] and not found.perfect
    assert score("visible", {}, {}).perfect  # gold plans no output, and none is built


def test_rows_with_one_label_are_told_apart_by_their_turn():
    rows = {"": ROWS[""], "n": ["1", "2", "3"], "n#": ["4", "5", "6"]}
    table = table_of(grid(rows))
    assert table.rows == (("@header", "", 1), ("", "n", 1), ("", "n", 2))
    other = {"": ROWS[""], "n": ["1", "2", "3"], "n#": ["4", "5", "7"]}
    found = compare_output("Out_A", grid(rows), grid(other))
    assert found.correct == 8 and found.wrong[0].row == ("", "n", 2)


def test_every_score_is_printed_with_its_denominator():
    rows = {label: texts for label, texts in ROWS.items() if label != "Serious event"}
    text = "\n".join(score("twin", {"Out_A": grid()}, {"Out_A": grid(rows)}).lines())
    for wanted in (
            "twin: produced: 1 of 1 outputs in gold",
            "cells correct: 6 of 6 gold cells of the rows that gold and the candidate both have",
            "cells correct: 6 of 9 gold cells of the outputs produced",
            "cells correct: 6 of 9 gold cells (an output that was not produced counts as wrong)",
            "whole output, strict: 0 of 1 outputs in gold",
            "whole output, lenient: 0 of 1 outputs in gold"):
        assert wanted in text


def adsl(**columns):
    base = {"USUBJID": ["S1", "S2", "S3"], "SAFFL": ["Y", "Y", "N"], "AGE": [60.0, 61.5, None]}
    return pa.table({**base, **columns})


def test_adam_columns_are_compared_record_by_record():
    assert adam_differences({"ADSL": adsl()}, {"ADSL": adsl()}) == {}
    assert adam_differences({"ADSL": adsl()}, {"ADSL": adsl(SAFFL=["Y", "N", "N"])}) == {
        "adam:ADSL.SAFFL": 1}
    # the order of the records does not count, the key does
    turned = pa.table({"USUBJID": ["S3", "S1", "S2"], "SAFFL": ["N", "Y", "Y"],
                       "AGE": [None, 60.0, 61.5]})
    assert adam_differences({"ADSL": adsl()}, {"ADSL": turned}) == {}
    assert adam_differences({"ADSL": adsl()}, {"ADSL": adsl(AGE=[60.0, 61.5, 70.0])}) == {
        "adam:ADSL.AGE": 1}
    assert adam_differences({"ADSL": adsl()},
                            {"ADSL": adsl(AGE=[60.0, 61.5 * (1 + 1e-12), None])}) == {}


def test_a_column_a_dataset_or_a_record_the_candidate_lacks():
    assert adam_differences({"ADSL": adsl()}, {"ADSL": adsl().drop_columns(["AGE"])}) == {
        "adam:ADSL.AGE": 3}
    assert adam_differences({"ADSL": adsl()}, {}) == {
        "adam:ADSL.USUBJID": 3, "adam:ADSL.SAFFL": 3, "adam:ADSL.AGE": 3}
    assert set(adam_differences({"ADSL": adsl()}, {"ADSL": adsl().slice(0, 2)})) == {
        "adam:ADSL.USUBJID", "adam:ADSL.SAFFL", "adam:ADSL.AGE"}
    # a column that only the candidate has is no difference of a gold column
    assert adam_differences({"ADSL": adsl()}, {"ADSL": adsl(NEW=["a", "b", "c"])}) == {}


def test_results_are_compared_by_their_id():
    gold = {"ard:A/n/=P": {"raw_value": 1}, "ard:A/pct/=P": {"raw_value": 50.0},
            "ard:A/n/=D": {"raw_value": 2}}
    other = {"ard:A/n/=P": {"raw_value": 1}, "ard:A/pct/=P": {"raw_value": 33.3},
             "ard:A/n/=X": {"raw_value": 2}}
    assert ard_differences(gold, gold) == {}
    assert ard_differences(gold, other) == {"ard:A/n/=D": "absent", "ard:A/pct/=P": "differs",
                                            "ard:A/n/=X": "extra"}
