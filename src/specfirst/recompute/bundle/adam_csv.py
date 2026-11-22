"""Write CSV copies of ADaM datasets for the R recomputation scripts (issue #29, ADR-021).

    python adam_csv.py <folder of the ADaM as Parquet> <target folder> <dataset> ...

Standalone: pyarrow and the standard library only. The R library of the
project reads no Parquet, so the R scripts read these copies. A number is
written as the shortest text that reads back as the same number (Python's
repr), a date or time in ISO 8601, a missing value as the empty text.
"""

from __future__ import annotations

import csv
import datetime
import sys
from pathlib import Path

import pyarrow.parquet as pq


def text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return "" if value != value else repr(value)
    if isinstance(value, datetime.date | datetime.time):
        return value.isoformat()
    return str(value)


def write(source: Path, target: Path, names: list[str]) -> None:
    target.mkdir(parents=True, exist_ok=True)
    for name in names:
        table = pq.read_table(source / f"{name}.parquet")
        columns = [column.to_pylist() for column in table.columns]
        with open(target / f"{name}.csv", "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(table.column_names)
            for row in zip(*columns, strict=True):
                writer.writerow([text(value) for value in row])


if __name__ == "__main__":
    write(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3:])
