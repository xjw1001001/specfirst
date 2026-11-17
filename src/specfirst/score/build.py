"""The build score (PLAN.md section 9.2; ADR-005, decision 4): the effect of a reading.

The scorer builds the candidate's decisions on a dataset and compares what
they give with what the gold decisions give on the same dataset: once on the
visible data, once on the twin. This module compares two such builds. It
builds nothing itself (`specfirst.score.candidate` does).

For the outputs of a kit, each score with its denominator named:

    produced    outputs built, of the outputs in gold
    cells       gold cells that the candidate shows with the same text, of
                (a) the gold cells of the rows that gold and the candidate
                    both have, in the outputs produced;
                (b) all gold cells of the outputs produced;
                (c) all gold cells: an output that was not produced counts
                    as wrong
    strict      outputs whose two axes equal those of gold and whose every
                cell is equal, of the outputs in gold
    lenient     outputs in which every gold cell is present and equal;
                more rows or columns are allowed; of the outputs in gold

What a row and a column are. A reader of a table tells its rows apart by
section and label and its columns by their header. So a row of gold and a
row of the candidate are the same row when they have the same section and
the same label (the n-th such row, when a label repeats), and a column is
its header text. Position does not count: a candidate that leaves out the
second row still has the third. Order counts for `strict` only.

The header row of a grid (section `@header`: the counts under the column
headers) is a row like any other: its cells are printed numbers.

For the layers below the grid (section 9.2, "values"), `adam_differences`
and `ard_differences` say which ADaM columns and which results differ;
attribution walks them (`specfirst.score.attribute`).
"""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field

RowKey = tuple[str, str, int]  # (section, label, n-th row of that section and label)
ColumnKey = tuple[str, int]  # (header text, n-th column of that text)
# The relative tolerance of two of our own values (rule R11; specfirst.machine.results).
RELATIVE = 1e-9
# The columns that say which records of two builds of one dataset belong together.
RECORD_KEYS = ("USUBJID", "PARAMCD", "AESEQ", "VSSEQ", "DTYPE")


def _numbered(names: list) -> list[tuple]:
    seen: Counter = Counter()
    found = []
    for name in names:
        seen[name] += 1
        found.append((*name, seen[name]) if isinstance(name, tuple) else (name, seen[name]))
    return found


@dataclass(frozen=True)
class Table:
    """A grid as its two axes and its cells."""

    rows: tuple[RowKey, ...]
    columns: tuple[ColumnKey, ...]
    cells: dict[tuple[RowKey, ColumnKey], dict]  # the cell of the grid: id, text, ard


def table_of(grid: dict) -> Table:
    """The axes and the cells of a grid (standard/schemas/grid.schema.json)."""
    columns = _numbered([column.get("label", "") for column in grid["columns"]])
    by_id = {column["id"]: key for column, key in zip(grid["columns"], columns, strict=True)}
    rows = _numbered([(str(row.get("section") or ""), str(row.get("label") or ""))
                      for row in grid["rows"]])
    cells = {}
    for row, key in zip(grid["rows"], rows, strict=True):
        for cell in row["cells"]:
            cells[(key, by_id[cell["column"]])] = cell
    return Table(tuple(rows), tuple(columns), cells)


@dataclass(frozen=True)
class WrongCell:
    """A gold cell the candidate does not show with the same text."""

    output: str
    row: RowKey
    column: ColumnKey
    cell: str  # the ID of the gold cell
    gold: str
    candidate: str | None  # None: the candidate has no such cell
    reason: str  # differs | no_row | no_column | not_produced


@dataclass
class OutputScore:
    output: str
    produced: bool
    why_not: str | None = None  # the failing rule, when the output was not produced
    gold_cells: int = 0
    shared_row_cells: int = 0  # gold cells of the rows both have
    correct: int = 0
    rows_equal: bool = False
    columns_equal: bool = False
    wrong: list[WrongCell] = field(default_factory=list)
    extra_rows: list[RowKey] = field(default_factory=list)
    extra_columns: list[ColumnKey] = field(default_factory=list)

    @property
    def lenient(self) -> bool:
        return self.produced and self.correct == self.gold_cells

    @property
    def strict(self) -> bool:
        return self.lenient and self.rows_equal and self.columns_equal


def compare_output(output: str, gold: dict, candidate: dict | None,
                   why_not: str | None = None) -> OutputScore:
    """Compare the grid of one output with the gold grid of the same output."""
    ours = table_of(gold)
    if candidate is None:
        found = OutputScore(output, False, why_not or "the candidate did not build it",
                            gold_cells=len(ours.cells))
        found.wrong = [WrongCell(output, row, column, cell["id"], cell["text"], None,
                                 "not_produced") for (row, column), cell in ours.cells.items()]
        return found
    theirs = table_of(candidate)
    found = OutputScore(output, True, gold_cells=len(ours.cells),
                        rows_equal=ours.rows == theirs.rows,
                        columns_equal=ours.columns == theirs.columns)
    their_rows, their_columns = set(theirs.rows), set(theirs.columns)
    for (row, column), cell in ours.cells.items():
        if row in their_rows:
            found.shared_row_cells += 1
        other = theirs.cells.get((row, column))
        if other is not None and other["text"] == cell["text"]:
            found.correct += 1
            continue
        reason = ("no_row" if row not in their_rows else
                  "no_column" if column not in their_columns else "differs")
        found.wrong.append(WrongCell(output, row, column, cell["id"], cell["text"],
                                     None if other is None else other["text"], reason))
    found.extra_rows = [row for row in theirs.rows if row not in set(ours.rows)]
    found.extra_columns = [column for column in theirs.columns if column not in set(ours.columns)]
    return found


@dataclass
class BuildScore:
    """The build score of one candidate on one dataset (the visible data, or the twin)."""

    dataset: str
    valid: bool  # the decisions compile and build (section 9.2, validity)
    failure: str | None
    outputs: list[OutputScore]
    extra_outputs: list[str] = field(default_factory=list)  # built, and not in gold

    @property
    def in_gold(self) -> int:
        return len(self.outputs)

    @property
    def produced(self) -> int:
        return sum(1 for output in self.outputs if output.produced)

    @property
    def correct(self) -> int:
        return sum(output.correct for output in self.outputs)

    def denominators(self) -> dict[str, int]:
        """The three denominators of `cells correct` (ADR-005, decision 4)."""
        made = [output for output in self.outputs if output.produced]
        return {
            "shared_rows": sum(output.shared_row_cells for output in made),
            "produced": sum(output.gold_cells for output in made),
            "all": sum(output.gold_cells for output in self.outputs),
        }

    @property
    def strict(self) -> int:
        return sum(1 for output in self.outputs if output.strict)

    @property
    def lenient(self) -> int:
        return sum(1 for output in self.outputs if output.lenient)

    def wrong(self) -> list[WrongCell]:
        return [cell for output in self.outputs for cell in output.wrong]

    @property
    def perfect(self) -> bool:
        return self.valid and not self.extra_outputs and self.strict == self.in_gold

    def lines(self) -> list[str]:
        """The four scores, each with its denominator named."""
        cells = self.denominators()
        said = [
            f"{self.dataset}: valid: {'yes' if self.valid else 'no (' + str(self.failure) + ')'}",
            f"{self.dataset}: produced: {self.produced} of {self.in_gold} outputs in gold",
            f"{self.dataset}: cells correct: {self.correct} of {cells['shared_rows']} gold cells "
            "of the rows that gold and the candidate both have",
            f"{self.dataset}: cells correct: {self.correct} of {cells['produced']} gold cells of "
            "the outputs produced",
            f"{self.dataset}: cells correct: {self.correct} of {cells['all']} gold cells (an "
            "output that was not produced counts as wrong)",
            f"{self.dataset}: whole output, strict: {self.strict} of {self.in_gold} outputs in "
            "gold (both axes equal and every cell equal)",
            f"{self.dataset}: whole output, lenient: {self.lenient} of {self.in_gold} outputs in "
            "gold (every gold cell present and equal)",
        ]
        if self.extra_outputs:
            said.append(f"{self.dataset}: outputs built that gold does not have: "
                        + ", ".join(self.extra_outputs))
        return said


def score(dataset: str, gold: dict[str, dict], candidate: dict[str, dict], valid: bool = True,
          failure: str | None = None, not_produced: dict[str, str] | None = None) -> BuildScore:
    """Compare the grids of a candidate build with the gold grids, by output ID.

    `not_produced` gives, for an output the candidate did not build, the
    rule that failed.
    """
    reasons = not_produced or {}
    outputs = [compare_output(name, grid, candidate.get(name), reasons.get(name) or failure)
               for name, grid in sorted(gold.items())]
    return BuildScore(dataset, valid, failure, outputs,
                      extra_outputs=sorted(set(candidate) - set(gold)))


# ---- the layers below the grid --------------------------------------------------------


def same_number(one: object, two: object) -> bool:
    """Two values of one column or result are the same."""
    if one is None or two is None:
        return one is two
    if isinstance(one, float) or isinstance(two, float):
        try:
            a, b = float(one), float(two)
        except (TypeError, ValueError):
            return False
        if math.isnan(a) or math.isnan(b):
            return math.isnan(a) and math.isnan(b)
        return abs(a - b) <= RELATIVE * max(abs(a), abs(b))
    return one == two


def _records(table, keys: list[str]) -> dict[tuple, dict] | None:
    """The records of an Arrow table by key; None when the key is not one."""
    rows = table.to_pylist()
    found = {tuple(row[key] for key in keys): row for row in rows}
    return found if len(found) == len(rows) else None


def adam_differences(gold: dict, candidate: dict) -> dict[str, int]:
    """The ADaM columns of gold whose values the candidate does not have, each with
    the number of records that differ.

    `gold` and `candidate` map a dataset name to its Arrow table. A column
    is named `adam:<DATASET>.<COLUMN>`. Records are matched by the record
    keys both tables have; a dataset or a column the candidate lacks
    differs in every record, and so does every column when the two tables
    do not hold the same records.
    """
    found: dict[str, int] = {}
    for name, table in sorted(gold.items()):
        other = candidate.get(name)
        every = max(table.num_rows, 1)
        if other is None:
            found.update({f"adam:{name}.{column}": every for column in table.column_names})
            continue
        keys = [key for key in RECORD_KEYS
                if key in table.column_names and key in other.column_names]
        ours, theirs = _records(table, keys), _records(other, keys)
        if ours is None or theirs is None or set(ours) != set(theirs):
            found.update({f"adam:{name}.{column}": every for column in table.column_names})
            continue
        for column in table.column_names:
            if column not in other.column_names:
                found[f"adam:{name}.{column}"] = every
                continue
            differing = sum(1 for key, row in ours.items()
                            if not same_number(row[column], theirs[key][column]))
            if differing:
                found[f"adam:{name}.{column}"] = differing
    return found


def ard_differences(gold: dict[str, dict], candidate: dict[str, dict]) -> dict[str, str]:
    """The results that gold and the candidate do not have in common with the same value.

    Both map the ID of an ARD row to the row. Returns, per ID, `absent` (in
    gold only), `extra` (in the candidate only) or `differs`.
    """
    found = {}
    for key, row in sorted(gold.items()):
        if key not in candidate:
            found[key] = "absent"
        elif not same_number(row.get("raw_value"), candidate[key].get("raw_value")):
            found[key] = "differs"
    found.update({key: "extra" for key in sorted(candidate) if key not in gold})
    return found
