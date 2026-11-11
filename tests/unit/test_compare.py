"""P2 for ADaM: the comparison must see every planted difference (rule R5)."""

from __future__ import annotations

import datetime

import pytest

from specfirst.machine.compare import compare_tables, storage_summary, total_line

pa = pytest.importorskip("pyarrow")


def reference():
    return pa.table({
        "ID": pa.array(["a", "b", "c", None], pa.large_string()),
        "N": pa.array([1.0, 2.5, None, float("nan")]),
        "K": pa.array([1.0, 2.0, 3.0, None]),
        "D": pa.array([datetime.date(2020, 1, 1), None, datetime.date(2020, 1, 3), None]),
    })


def built(**changes):
    columns = {
        "ID": pa.array(["a", "b", "c", None]),
        "N": pa.array([1.0, 2.5, None, float("nan")]),
        "K": pa.array([1, 2, 3, None], pa.int64()),
        "D": pa.array([datetime.date(2020, 1, 1), None, datetime.date(2020, 1, 3), None]),
    }
    columns.update(changes)
    return pa.table(columns)


def test_equal_tables_and_storage_types():
    result = compare_tables("X", reference(), built())
    assert result.equal and result.mismatched == 0 and result.cells == 16
    # Same values in another storage type are listed, not counted.
    assert result.storage == [("ID", "large_string", "string"), ("K", "double", "int64")]
    assert storage_summary([result]) == {"double -> int64": 1, "large_string -> string": 1}
    assert total_line([result]) == "TOTAL cells=16 mismatched=0"
    assert result.line().startswith("X         rows=     4 cols=  4 cells=      16 mismatched=")


@pytest.mark.parametrize(
    ("change", "column", "count"),
    [
        ({"N": [1.0, 2.5000001, None, float("nan")]}, "N", 1),  # beyond the tolerance
        ({"N": [1.0, 2.5, 0.0, float("nan")]}, "N", 1),  # a value where the reference has none
        ({"N": [1.0, None, None, float("nan")]}, "N", 1),  # missing where the reference has one
        ({"N": [1.0, 2.5, None, 7.0]}, "N", 1),  # a number against NaN
        ({"N": [float("inf"), 2.5, None, float("nan")]}, "N", 1),
        ({"ID": ["a", "B", "c", None]}, "ID", 1),
        ({"ID": ["a", "b", "c", ""]}, "ID", 1),  # empty text is not missing
        ({"K": [1, 2, 4, None]}, "K", 1),
        ({"D": [datetime.date(2020, 1, 2), None, datetime.date(2020, 1, 3), None]}, "D", 1),
        ({"K": ["1", "2", "3", None]}, "K", 3),  # text against number: another kind
    ],
)
def test_planted_difference_is_counted(change, column, count):
    result = compare_tables("X", reference(), built(**{k: pa.array(v) for k, v in change.items()}))
    assert not result.equal
    assert result.by_column == {column: count}
    assert result.mismatched == count


def test_difference_within_the_tolerance_is_equal():
    close = pa.array([1.0, 2.5 + 1e-11, None, float("nan")])
    assert compare_tables("X", reference(), built(N=close)).equal


def test_large_integers_are_compared_exactly():
    left = pa.table({"K": pa.array([2**60], pa.int64())})
    right = pa.table({"K": pa.array([2**60 + 1], pa.int64())})
    assert compare_tables("X", left, left).equal
    assert compare_tables("X", left, right).mismatched == 1


def test_another_number_of_rows_fails_every_cell():
    result = compare_tables("X", reference(), built().slice(0, 3))
    assert not result.equal and result.mismatched == 16
    assert result.problems == ["rows: reference=4 built=3"]


def test_missing_extra_and_reordered_columns_fail():
    missing = compare_tables("X", reference(), built().drop_columns(["K"]))
    assert not missing.equal and missing.mismatched == 4 and missing.by_column == {"K": 4}
    assert "missing=['K']" in missing.problems[0]

    extra = compare_tables("X", reference(), built().append_column("NEW", pa.array([1, 2, 3, 4])))
    assert extra.mismatched == 0 and not extra.equal  # a hole of the spike, closed
    assert "extra=['NEW']" in extra.problems[0]

    reordered = compare_tables("X", reference(), built().select(["N", "ID", "K", "D"]))
    assert reordered.mismatched == 0 and not reordered.equal
    assert reordered.problems == ["columns are in another order"]


def test_all_missing_column_of_null_type_equals_a_typed_one():
    left = pa.table({"A": pa.array([None, None], pa.string())})
    right = pa.table({"A": pa.array([None, None], pa.null())})
    assert compare_tables("X", left, right).equal
    assert not compare_tables("X", pa.table({"A": ["x", None]}), right).equal
