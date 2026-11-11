"""P2 for ADaM: the built dataset equals the reference, cell by cell.

PLAN.md section 4.6: numeric tolerance 1e-10. A cell is one row of one
column of the reference. The count follows evidence/compare_adam.py (E1), so
the total for the pilot is the same 9,119,605, with three holes of the spike
closed: a NaN against a number is a mismatch, a column the reference does not
have fails the comparison, and so does a different column order.

Values are compared by logical kind (number, text, date, ...). Two storage
types of one kind, such as Arrow's string and large_string, hold the same
values and are not a difference; they are listed. A column whose kind
differs, such as text against number, mismatches in every cell that is not
missing on both sides.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pyarrow as pa

TOLERANCE = 1e-10


@dataclass
class Comparison:
    name: str
    rows: int  # of the reference
    columns: int  # of the reference
    mismatched: int = 0
    problems: list[str] = field(default_factory=list)  # structure: rows, columns
    by_column: dict[str, int] = field(default_factory=dict)  # column -> mismatched cells
    # Columns of one logical kind in two storage types: column, reference, built.
    storage: list[tuple[str, str, str]] = field(default_factory=list)

    @property
    def cells(self) -> int:
        return self.rows * self.columns

    @property
    def equal(self) -> bool:
        return self.mismatched == 0 and not self.problems

    def line(self) -> str:
        detail = " ".join(f"{name}:{count}" for name, count in list(self.by_column.items())[:8])
        text = (f"{self.name:9s} rows={self.rows:6d} cols={self.columns:3d} cells={self.cells:8d} "
                f"mismatched={self.mismatched:6d} storage_type_diffs={len(self.storage)}")
        return " ".join(part for part in (text, "; ".join(self.problems), detail) if part)


def kind(data_type: pa.DataType) -> str:
    import pyarrow as pa

    types = pa.types
    if types.is_dictionary(data_type):
        return kind(data_type.value_type)
    if types.is_boolean(data_type):
        return "boolean"
    if types.is_integer(data_type) or types.is_floating(data_type) or types.is_decimal(data_type):
        return "number"
    if types.is_string(data_type) or types.is_large_string(data_type):
        return "text"
    if types.is_date(data_type):
        return "date"
    if types.is_timestamp(data_type):
        return "timestamp"
    if types.is_time(data_type):
        return "time"
    if types.is_null(data_type):
        return "null"
    return str(data_type)


def _column_mismatches(reference: pa.ChunkedArray, built: pa.ChunkedArray, tolerance: float) -> int:
    import numpy as np
    import pyarrow as pa
    import pyarrow.compute as pc

    left, right = reference.combine_chunks(), built.combine_chunks()
    if pa.types.is_dictionary(left.type):
        left = left.dictionary_decode()
    if pa.types.is_dictionary(right.type):
        right = right.dictionary_decode()
    left_null = np.asarray(left.is_null())
    right_null = np.asarray(right.is_null())
    both = ~left_null & ~right_null
    mismatched = left_null != right_null
    kinds = kind(left.type), kind(right.type)
    if "null" in kinds:
        return int(mismatched.sum())
    if kinds[0] != kinds[1]:
        return int((mismatched | both).sum())
    if kinds[0] == "number":
        if pa.types.is_integer(left.type) and pa.types.is_integer(right.type):
            a = left.fill_null(0).to_numpy(zero_copy_only=False)
            b = right.fill_null(0).to_numpy(zero_copy_only=False)
            differ = a != b
        else:
            a = pc.cast(left, pa.float64()).fill_null(0.0).to_numpy(zero_copy_only=False)
            b = pc.cast(right, pa.float64()).fill_null(0.0).to_numpy(zero_copy_only=False)
            a_nan, b_nan = np.isnan(a), np.isnan(b)
            with np.errstate(invalid="ignore"):
                differ = np.abs(a - b) > tolerance
            differ = np.where(a_nan | b_nan, a_nan != b_nan, differ)  # NaN equals only NaN
            differ = np.where(np.isinf(a) | np.isinf(b), a != b, differ)
        return int((mismatched | (both & differ)).sum())
    if kinds[0] == "text":
        left, right = pc.cast(left, pa.large_string()), pc.cast(right, pa.large_string())
    elif left.type != right.type:
        if kinds[0] == "date":
            target = pa.date64()
        elif kinds[0] == "timestamp":
            target = pa.timestamp("ns", tz=left.type.tz)
        elif kinds[0] == "time":
            target = pa.time64("ns")
        else:
            return int((mismatched | both).sum())
        left, right = pc.cast(left, target), pc.cast(right, target)
    differ = np.asarray(pc.fill_null(pc.not_equal(left, right), False))
    return int((mismatched | (both & differ)).sum())


def compare_tables(
    name: str, reference: pa.Table, built: pa.Table, tolerance: float = TOLERANCE
) -> Comparison:
    result = Comparison(name, reference.num_rows, reference.num_columns)
    expected, found = reference.schema.names, built.schema.names
    if expected != found:
        missing = [column for column in expected if column not in found]
        extra = [column for column in found if column not in expected]
        if missing or extra:
            result.problems.append(f"columns differ: missing={missing} extra={extra}")
        else:
            result.problems.append("columns are in another order")
    if reference.num_rows != built.num_rows:
        result.problems.append(f"rows: reference={reference.num_rows} built={built.num_rows}")
        result.mismatched = result.cells
        return result
    for column in expected:
        if column not in found:
            count = reference.num_rows
        else:
            left, right = reference.schema.field(column).type, built.schema.field(column).type
            if left != right and kind(left) == kind(right):
                result.storage.append((column, str(left), str(right)))
            count = _column_mismatches(reference.column(column), built.column(column), tolerance)
        if count:
            result.by_column[column] = count
        result.mismatched += count
    return result


def total_line(results: list[Comparison]) -> str:
    cells = sum(result.cells for result in results)
    mismatched = sum(result.mismatched for result in results)
    return f"TOTAL cells={cells} mismatched={mismatched}"


def storage_summary(results: list[Comparison]) -> dict[str, int]:
    """How many columns differ in storage type only, by 'reference -> built'."""
    pairs = Counter(
        f"{left} -> {right}" for result in results for _, left, right in result.storage
    )
    return dict(sorted(pairs.items()))
