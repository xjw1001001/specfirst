"""The grid of a compiled house layout (layout draft 0), for the outputs of a generated study.

Why this module exists. The compiler writes one layout file per table family
from the templates of the house standard. Those templates are "layout draft
0", written by std-1 before a grid builder read them. The grid builder of
real-3a (`specfirst.machine.grid`) reads layout spec v0 (ADR-003), a format
of its own that has no total column, no rule for the order of the columns,
one rounding rule and no rule for a count of zero. Four decisions of the
catalog decide exactly these. Until the house templates are aligned with a
layout format that carries them (std-2 and the rest of real-3), this module
builds the grid of a draft 0 layout directly (docs/decisions/ADR-007.md).

It builds what the machine's builder builds: a grid of schema version 0
whose every cell has its text and the IDs of the ARD rows behind it, a row
with the section `@header` for the counts under the column headers (ADR-003,
decision 4), and a mock shell with masks in place of numbers. It computes
no number. A text is a result of the ARD shown by `display.pattern` of the
method registry, with the rounding rule the layout names.

What a draft 0 layout of the kind `count_percent` gives, and how it is shown:

    columns.grouping        one column per group, in the order of the groups
                            (`resolve_groupings` of specfirst.gen.gold lists
                            the groups of a data-driven grouping in the order
                            the layout asks for)
    columns.total           one more column, the last: the one group of its
                            grouping
    columns.header_count    the analysis whose count stands under each column
                            header, as "(N=XX)"
    rows[].analysis         a row: the count and the percent of the analysis
    rows[].total_analysis   the same for the total column
    formats.rounding        half_away_from_zero or half_even
    formats.percent         decimals, and zero_count: count_only shows a count
                            of zero alone, count_and_percent with its percent

A cell is "{n} {pct}": the count by the pattern "XX", the percent by
"(XXX.X)" (as many X after the point as `decimals`), for example
"12 ( 37.5)". A percent that does not exist (a column without subjects) is
left out.
"""

from __future__ import annotations

from urllib.parse import quote

from specfirst.machine import ars, grid, methods

HEADER_PATTERN = "(N=XX)"
COUNT_PATTERN = "XX"
HEADER_SECTION = "@header"
ZERO_COUNT = ("count_only", "count_and_percent")


class DisplayError(ValueError):
    """The layout cannot be shown."""


def percent_pattern(decimals: int) -> str:
    return "(XXX." + "X" * decimals + ")" if decimals else "(XXX)"


def _operations(event: ars.Event, analysis: dict) -> tuple[str, str | None]:
    """The count and the percent operation of the method of an analysis.

    The percent is the operation that refers to others (its numerator and
    denominator); the count is the one that does not.
    """
    method = event.methods[analysis["methodId"]]
    counts = [op["id"] for op in method["operations"]
              if not op.get("referencedOperationRelationships")]
    percents = [op["id"] for op in method["operations"]
                if op.get("referencedOperationRelationships")]
    if len(counts) != 1 or len(percents) > 1:
        raise DisplayError(f"analysis '{analysis['id']}': a count needs a method with one count "
                           "and at most one percent")
    return counts[0], percents[0] if percents else None


def _groups(event: ars.Event, grouping_id: str) -> list[dict]:
    grouping = event.groupings.get(grouping_id)
    if grouping is None:
        raise DisplayError(f"the grouping '{grouping_id}' is not in the reporting event")
    if grouping.get("dataDriven"):
        raise DisplayError(f"the grouping '{grouping_id}' is data-driven: its groups must be "
                           "listed before a grid is built (specfirst.gen.gold)")
    return [group for _, group in sorted(enumerate(grouping["groups"]),
                                         key=lambda item: (item[1].get("order", 0), item[0]))]


def columns(event: ars.Event, layout: dict) -> list[dict]:
    """The columns of a layout: id, label, and where its results are (grouping and group)."""
    axis = layout["columns"]
    found = [{"grouping": axis["grouping"], "group": group["id"],
              "label": str(group.get("name") or ""), "total": False}
             for group in _groups(event, axis["grouping"])]
    total = axis.get("total")
    if total:
        groups = _groups(event, total["grouping"])
        if len(groups) != 1:
            raise DisplayError(f"the total grouping '{total['grouping']}' must have one group")
        found.append({"grouping": total["grouping"], "group": groups[0]["id"],
                      "label": str(total.get("label") or groups[0].get("name") or ""),
                      "total": True})
    for number, column in enumerate(found, start=1):
        column["id"] = f"c{number}"
    return found


def _ard(event: ars.Event, analysis_id: str | None, operation: str, column: dict) -> str:
    analysis = event.analyses.get(analysis_id or "")
    if analysis is None:
        raise DisplayError(f"the analysis '{analysis_id}' is not in the reporting event")
    used = [entry["groupingId"] for entry in event.groupings_of(analysis)]
    if used != [column["grouping"]]:
        raise DisplayError(f"analysis '{analysis_id}' is grouped by {used}, its column by "
                           f"{column['grouping']}")
    return grid.ard_id(event, analysis, operation, {column["grouping"]: ("id", column["group"])})


def build(event: ars.Event, layout: dict, rows: dict[str, dict] | None) -> dict:
    """The grid of a layout from the ARD rows by ID; the mock shell when `rows` is None."""
    formats = layout.get("formats") or {}
    rounding = formats.get("rounding", "half_away_from_zero")
    percent = formats.get("percent") or {}
    decimals, zero = percent.get("decimals", 1), percent.get("zero_count", "count_and_percent")
    if zero not in ZERO_COUNT or rounding not in methods.ROUNDING_RULES:
        raise DisplayError(f"the layout names the rounding '{rounding}' and the zero count "
                           f"'{zero}'; known are {', '.join(methods.ROUNDING_RULES)} and "
                           f"{', '.join(ZERO_COUNT)}")
    output = layout["output"]["id"]
    if output not in ars.outputs(event):
        raise DisplayError(f"the output '{output}' is not in the reporting event")
    axis = layout["columns"]
    found = columns(event, layout)
    mock = rows is None

    def value(key: str) -> float | int | None:
        if key not in rows:
            raise DisplayError(f"{key}: the layout shows it, the ARD does not have it")
        return rows[key]["raw_value"]

    def shown(key: str, pattern: str) -> str | None:
        return methods.pattern_text(None if mock else value(key), pattern, mock=mock,
                                    rounding=rounding)

    def cell(number: int, column: dict, text: str, keys: list[str]) -> dict:
        return {"id": f"cell:{quote(output, safe='')}/r{number}/{column['id']}",
                "column": column["id"], "text": text, "ard": keys}

    made = []
    header = []
    for column in found:
        name = (axis["total"] if column["total"] else axis)["header_count"]
        key = _ard(event, name, _operations(event, event.analyses[name])[0], column)
        header.append(cell(1, column, shown(key, HEADER_PATTERN) or "", [key]))
    made.append({"id": "r1", "label": "", "section": HEADER_SECTION, "cells": header})
    for number, row in enumerate(layout["rows"], start=2):
        if row.get("kind") != "count_percent":
            raise DisplayError(f"row '{row.get('label')}': this builder shows rows of the kind "
                               f"count_percent, not '{row.get('kind')}'")
        cells = []
        for column in found:
            name = row["total_analysis"] if column["total"] else row["analysis"]
            count_op, percent_op = _operations(event, event.analyses[name])
            count_key = _ard(event, name, count_op, column)
            keys, text = [count_key], shown(count_key, COUNT_PATTERN) or ""
            if percent_op is not None:
                percent_key = _ard(event, name, percent_op, column)
                alone = not mock and value(count_key) == 0 and zero == "count_only"
                part = None if alone else shown(percent_key, percent_pattern(decimals))
                if part is not None:
                    keys.append(percent_key)
                    text = f"{text} {part}"
            cells.append(cell(number, column, text, keys))
        made.append({"id": f"r{number}", "label": str(row["label"]), "cells": cells})
    sections = ars.display_sections(event, output)
    titles = sections.get("Title") or [str(layout["output"].get("title") or "")]
    return {"schema": grid.SCHEMA, "output_id": output, "titles": list(titles),
            "columns": [{"id": column["id"], "label": column["label"]} for column in found],
            "rows": made,
            "footnotes": [*sections.get("Abbreviation", []), *sections.get("Footnote", [])]}


def texts(made: dict) -> dict[tuple[str, str], str]:
    """(row label, column label) -> text of a grid; the header row has the label ''."""
    labels = {column["id"]: column["label"] for column in made["columns"]}
    return {(row["label"], labels[cell["column"]]): cell["text"]
            for row in made["rows"] for cell in row["cells"]}
