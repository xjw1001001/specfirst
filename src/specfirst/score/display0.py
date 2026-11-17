"""The grid of a compiled table of counts and percents, from layout draft 0.

A stand-in, for the scorer's own builds only. The compiler writes layout
draft 0 (ADR-004, decision 6), and the grid builder of the machine reads
layout version 0 (ADR-003), which has no total column, no rule for a count
of zero and one rounding rule. Three of the seven decisions of the unit
`tfl-ae-summary` say exactly these things, and the house default has a
total column. Until the builder that gen-2a puts on `main` is used here
(docs/state/read.md), this module shows a compiled layout of the kind
`count_percent` as a grid of schema version 0, so that the scorer can be
run on hand-made studies and on the pilot. It is not the gold builder of
any kit.

What it does that layout version 0 cannot say:

- A total column: a second grouping with one group, shown as the last
  column (decision tfl.columns.total).
- A count of zero without its percent (tfl.percent.format).
- Rounding half to even (tfl.rounding.rule).
- An arm that has subjects and no record of an analysis: the data-driven
  grouping gives it no ARD row (rule I9; review of real-3a, finding F2).
  Its count is zero, and the cell then names no ARD row.

The order of the arm columns (tfl.columns.arms) needs the arms of the
design: `Arm` has the dose and the place in the protocol's list. A value of
the treatment variable that is no arm of the design stands after the arms,
by its text.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal, localcontext
from urllib.parse import quote

from specfirst.machine import ars, methods
from specfirst.machine.grid import SCHEMA, ard_id
from specfirst.machine.layout import HEADER_SECTION

COUNT_PATTERN = "XX"
HEADER_PATTERN = "(N=XX)"
ROUNDINGS = ("half_away_from_zero", "half_even")
ORDERS = ("ascending_dose_placebo_first", "protocol_order")
ZERO_COUNTS = ("count_only", "count_and_percent")


class DisplayError(ValueError):
    """The layout cannot be shown by this stand-in."""


@dataclass(frozen=True)
class Arm:
    """An arm of the design: what the order of the treatment columns needs."""

    label: str  # the value of the treatment variable
    dose: float  # 0 for placebo
    position: int  # in the order in which the protocol lists the arms


@dataclass(frozen=True)
class CellPath:
    """What stands behind one cell: the results it shows when they exist, and the
    analyses they are computed from (the numerator's and the denominator's)."""

    ard: tuple[str, ...]
    analyses: tuple[str, ...]


def number_text(value: float | int | None, pattern: str, rounding: str) -> str | None:
    """A number under a result pattern, by the rounding rule of the decision."""
    if rounding == "half_away_from_zero" or value is None:
        return methods.pattern_text(value, pattern)
    before, mask, after = methods.pattern_mask(pattern)
    decimals = len(mask.partition(".")[2])
    exact = Decimal(repr(value)) if isinstance(value, float) else Decimal(value)
    with localcontext() as context:
        context.prec = 400
        rounded = exact.quantize(Decimal(1).scaleb(-decimals), rounding=ROUND_HALF_EVEN)
    if rounded == 0:
        rounded = abs(rounded)
    text = format(rounded, "f")
    sign = "-" if text.startswith("-") else ""
    digits = text.removeprefix("-")
    if "." in mask:
        digits = digits.rjust(len(mask))
    return before + sign + digits + after


def _operations(event: ars.Event, analysis_id: str) -> list[str]:
    """The operations of the method of an analysis, in their order."""
    analysis = event.analyses.get(analysis_id)
    if analysis is None:
        raise DisplayError(f"the layout names the analysis '{analysis_id}', which is not in "
                           "the reporting event")
    found = sorted(((operation.get("order", 0), operation_id)
                    for operation_id, (method_id, operation) in event.operations.items()
                    if method_id == analysis["methodId"]))
    return [operation_id for _, operation_id in found]


def arm_order(values: list[str], arms: tuple[Arm, ...], rule: str) -> list[str]:
    """The values of the treatment variable in the order of the columns."""
    if rule not in ORDERS:
        raise DisplayError(f"unknown column order '{rule}'")
    known = {arm.label: arm for arm in arms}
    key = (lambda arm: (arm.dose, arm.position)) if rule == ORDERS[0] else (
        lambda arm: (arm.position,))
    first = sorted((value for value in values if value in known), key=lambda v: key(known[v]))
    return first + sorted(value for value in values if value not in known)


def grid(event: ars.Event, layout: dict, rows: dict[str, dict],
         arms: tuple[Arm, ...]) -> tuple[dict, dict[str, CellPath]]:
    """The grid of one compiled output, and what stands behind each of its cells.

    `layout` is a compiled layout draft 0 whose rows are all of the kind
    `count_percent`; `rows` are the ARD rows by ID.
    """
    try:
        output = layout["output"]["id"]
        columns, formats = layout["columns"], layout["formats"]
        rounding = formats["rounding"]
        percent = formats["percent"]
        zero_count, decimals = percent["zero_count"], int(percent["decimals"])
        grouping, total = columns["grouping"], columns.get("total")
        header = columns["header_count"]
        body = layout["rows"]
    except (KeyError, TypeError) as error:
        raise DisplayError(f"not a layout draft 0 of counts and percents: {error!r}") from None
    if rounding not in ROUNDINGS or zero_count not in ZERO_COUNTS:
        raise DisplayError(f"unknown format: rounding '{rounding}', zero count '{zero_count}'")
    if any(row.get("kind") != "count_percent" for row in body):
        raise DisplayError("this stand-in shows rows of the kind count_percent only")
    if grouping not in event.groupings:
        raise DisplayError(f"the column grouping '{grouping}' is not in the reporting event")
    percent_pattern = "( XX" + ("." + "X" * decimals if decimals else "") + ")"
    header_analysis = event.analyses.get(header)
    if header_analysis is None:
        raise DisplayError(f"the header count '{header}' is not in the reporting event")
    values = sorted({row["group1_groupValue"] for row in rows.values()
                     if row["analysis_id"] == header and row.get("group1_groupValue")})
    # (label, grouping of the column, group, header analysis; None: the row's own analysis)
    shown: list[tuple[str, str, tuple[str, str], str, bool]] = [
        (value, grouping, ("value", value), header, False)
        for value in arm_order(values, arms, columns["order"])]
    if total:
        groups = (event.groupings.get(total["grouping"]) or {}).get("groups") or []
        if len(groups) != 1:
            raise DisplayError(f"the total grouping '{total['grouping']}' must have one group")
        shown.append((str(total["label"]), total["grouping"], ("id", groups[0]["id"]),
                      total["header_count"], True))
    if not shown:
        raise DisplayError("no subject is in the analysis set: the table has no column")

    paths: dict[str, CellPath] = {}

    def value_of(analysis_id: str, operation: str, column_grouping: str,
                 group: tuple[str, str]) -> tuple[str, float | int | None, bool]:
        key = ard_id(event, event.analyses[analysis_id], operation, {column_grouping: group})
        if key in rows:
            return key, rows[key]["raw_value"], True
        return key, None, False

    def cell(row_number: int, column_number: int, text: str, keys: list[tuple[str, bool]],
             analyses: list[str]) -> dict:
        cell_id = f"cell:{quote(output, safe='')}/r{row_number}/c{column_number}"
        paths[cell_id] = CellPath(tuple(key for key, _ in keys), tuple(dict.fromkeys(analyses)))
        return {"id": cell_id, "column": f"c{column_number}", "text": text,
                "ard": [key for key, present in keys if present]}

    made = []
    cells = []
    for number, (_, column_grouping, group, count_analysis, _) in enumerate(shown, start=1):
        operation = _operations(event, count_analysis)[0]
        key, value, present = value_of(count_analysis, operation, column_grouping, group)
        text = number_text(0 if value is None else value, HEADER_PATTERN, rounding)
        cells.append(cell(1, number, text, [(key, present)], [count_analysis]))
    made.append({"id": "r1", "label": "", "section": HEADER_SECTION, "cells": cells})
    for row_number, row in enumerate(body, start=2):
        cells = []
        for number, (_, column_grouping, group, count_analysis, is_total) in enumerate(
                shown, start=1):
            analysis_id = row["total_analysis"] if is_total else row["analysis"]
            operations = _operations(event, analysis_id)
            if len(operations) != 2:
                raise DisplayError(f"'{analysis_id}': a row of counts and percents needs a "
                                   "method with two operations")
            n_key, n, n_present = value_of(analysis_id, operations[0], column_grouping, group)
            p_key, pct, p_present = value_of(analysis_id, operations[1], column_grouping, group)
            n = 0 if n is None else n
            text = number_text(n, COUNT_PATTERN, rounding)
            if n != 0 or zero_count == "count_and_percent":
                text += " " + number_text(0.0 if pct is None else pct, percent_pattern, rounding)
            cells.append(cell(row_number, number, text, [(n_key, n_present), (p_key, p_present)],
                              [analysis_id, count_analysis]))
        made.append({"id": f"r{row_number}", "label": str(row["label"]), "cells": cells})
    built = {"schema": SCHEMA, "output_id": output, "titles": [str(layout["output"]["title"])],
             "columns": [{"id": f"c{number}", "label": label}
                         for number, (label, *_) in enumerate(shown, start=1)],
             "rows": made, "footnotes": []}
    return built, paths
