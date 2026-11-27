"""The grid builder (PLAN.md section 7.4): a layout and an ARD in, grid.json out.

A grid (standard/schemas/grid.schema.json, version 0) is the canonical
display of one output: every cell has its text and the IDs of the ARD rows
behind it. Renderers project it; scoring and tracing read it. The builder
computes no number: it looks results up in the ARD and shows each one by
its pattern (the registry's display.pattern, which rounds once).

A mock shell is the same grid without an ARD: every result is shown as the
mask of its pattern. Its cells still name the ARD rows they will show.

`plan` is the one place that says which results a cell shows. The builder
fills the plan; `compare_reference` walks the same plan to compare every
cell with the formatted values a reference embeds (P2 for grid text,
section 4.6), so a grid file that was changed after it was built does not
pass as built.

A header row. Schema version 0 gives a column an ID, a label and a
spanner, and no place for a result. A count under a column header ("(N=86)")
is a printed number and needs its ARD row, so it is a cell: of a row with
the section `@header`, which a renderer shows in the table header (ADR-003).
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import quote

from specfirst import schemas
from specfirst.machine import ars, methods, results
from specfirst.machine import layout as layouts

SCHEMA = "specfirst/grid@0"
Rows = results.Rows


class GridError(ValueError):
    """The grid cannot be built from this layout and these results."""


def ard_id(event: ars.Event, analysis: dict, operation_id: str,
           groups: dict[str, results.Group]) -> str:
    """The ID of the ARD row of an analysis and operation in the given groups (rule I14)."""
    parts = [quote(analysis["id"], safe=""), quote(operation_id, safe="")]
    for entry in event.groupings_of(analysis):
        kind, key = groups.get(entry["groupingId"], ("all", None))
        parts.append(quote(key, safe="") if kind == "id"
                     else "=" + quote(key, safe="") if kind == "value" else "*")
    return "ard:" + "/".join(parts)


@dataclass(frozen=True)
class Shown:
    """One result in a cell: the part of the template, its ARD row, its pattern."""

    name: str
    ard: str
    pattern: str
    analysis: str


@dataclass(frozen=True)
class PlannedCell:
    column: str  # c1, c2, ...
    shown: tuple[Shown, ...]
    template: str | None = None  # None: the row's; an extra cell has its own (real-5b)


@dataclass(frozen=True)
class PlannedRow:
    label: str
    template: str
    cells: tuple[PlannedCell, ...]
    section: str | None = None
    indent: int = 0


@dataclass(frozen=True)
class Plan:
    output: str
    titles: tuple[str, ...]
    footnotes: tuple[str, ...]
    columns: tuple[tuple[str, results.Group, str], ...]  # (column ID, group, label)
    rows: tuple[PlannedRow, ...]
    missing: str
    spanners: tuple[tuple[str, str], ...] = ()  # (column ID, spanner), issue #31


EXTRA = "extra"  # the kind of the group of an extra column: it is no group (real-5b)


def template_of(row: PlannedRow, cell: PlannedCell) -> str:
    """The template a cell is filled by: its own, else its row's."""
    return cell.template if cell.template is not None else row.template


def _columns(event: ars.Event, layout: layouts.Layout, rows: Rows | None,
             analyses: set[str]) -> list[tuple[results.Group, str]]:
    """The groups of the column grouping, in order, each with its label."""
    grouping = event.groupings[layout.grouping]
    labels = dict(layout.labels)
    if not grouping.get("dataDriven"):
        ordered = sorted(enumerate(grouping["groups"]),
                         key=lambda item: (item[1].get("order", 0), item[0]))
        return [(("id", group["id"]), labels.get(group["id"], str(group.get("name") or "")))
                for _, group in ordered]
    if layout.values is not None:
        values = list(layout.values)
    elif rows is not None:
        values = sorted({key for row in rows.values() if row["analysis_id"] in analyses
                         for name, (kind, key) in results.row_groups(row).items()
                         if name == layout.grouping and kind == "value"})
    else:
        raise GridError(f"the column grouping {layout.grouping} is data-driven: without "
                        "results, the layout must list its values (columns.values)")
    return [(("value", value), labels.get(value, value)) for value in values]


def plan(event: ars.Event, layout: layouts.Layout, rows: Rows | None = None) -> Plan:
    """Which results every cell of the output shows. `rows` is only read for the
    groups of a data-driven column grouping that the layout does not list."""
    found = layouts.problems(layout, event)
    if found:
        raise GridError("the layout does not fit the reporting event: " + "; ".join(found))
    sections = ars.display_sections(event, layout.output)
    used = {part.analysis or analysis_id for block in layout.blocks
            for analysis_id, _ in (block.analyses or ((None, None),)) for part in block.parts}
    used |= {block.analysis for block in layout.blocks
             if block.kind in ("statistics", "groups", "terms")}
    used |= {item.analysis for block in layout.blocks for item in block.shown}
    found_columns = _columns(event, layout, rows, used)
    if not found_columns:
        raise GridError(f"the column grouping {layout.grouping} has no group")
    within: dict[str, str] = {}  # column ID -> the item of columns.within it is (real-3)
    first: set[str] = set()  # the first column of each group, with `within`
    spanners_of_groups: list[tuple[str, str]] = []
    if layout.within:
        columns = []
        for group, label in found_columns:
            for number, (name, item_label) in enumerate(layout.within):
                column = f"c{len(columns) + 1}"
                columns.append((column, group, item_label))
                within[column] = name
                spanners_of_groups.append((column, label))
                if number == 0:
                    first.add(column)
    else:
        found_columns += [((EXTRA, name), label) for name, label in layout.extra]
        columns = [(f"c{number}", group, label) for number, (group, label)
                   in enumerate(found_columns, start=1)]
    spanned = dict(layout.spanners)
    spanners = tuple(spanners_of_groups) + tuple(
        (column, spanned[group[1]]) for column, group, _ in columns
        if group[0] == EXTRA and group[1] in spanned)

    def extra_cell(column: str, cell: layouts.ExtraCell | None,
                   groups: dict[str, results.Group], optional: bool = False) -> PlannedCell:
        """The cell of an extra column. `optional`: a result the ARD does not have leaves it
        empty (a terms block: a comparison has no result for a value it has no record of)."""
        if cell is None:
            return PlannedCell(column, ())
        shown = tuple(Shown(part.name, ard_id(event, event.analyses[part.analysis],
                                              part.operation, groups),
                            layouts.pattern_of(event, part), part.analysis)
                      for part in cell.parts)
        if optional and (rows is None or any(item.ard not in rows for item in shown)):
            return PlannedCell(column, ())
        return PlannedCell(column, shown, cell.cell)

    def cells(block: layouts.Block, analysis_id: str | None) -> tuple[PlannedCell, ...]:
        made = []
        for column, group, _ in columns:
            if group[0] == EXTRA or (within and column not in first):
                # With columns.within the count of a group stands in its first column.
                made.append(PlannedCell(column, ()))
                continue
            shown = []
            for part in block.parts:
                analysis = event.analyses[part.analysis or analysis_id]
                shown.append(Shown(part.name,
                                   ard_id(event, analysis, part.operation,
                                          {layout.grouping: group}),
                                   layouts.pattern_of(event, part), analysis["id"]))
            made.append(PlannedCell(column, tuple(shown)))
        return tuple(made)

    def statistics(block: layouts.Block) -> list[PlannedRow]:
        """One row per statistic. A compared grouping has one result, in its listed column;
        a column the block does not list has an empty cell."""
        analysis = event.analyses[block.analysis]
        split = bool(event.groupings_of(analysis)[0].get("resultsByGroup"))
        made = []
        for row in block.statistics:
            row_cells = []
            extra = {cell.column: cell for cell in row.extra}
            for column, group, _ in columns:
                if group[0] == EXTRA:
                    row_cells.append(extra_cell(column, extra.get(group[1]), {}))
                    continue
                if block.columns is not None and group[1] not in block.columns:
                    row_cells.append(PlannedCell(column, ()))
                    continue
                groups = {layout.grouping: group} if split else {}
                row_cells.append(PlannedCell(column, tuple(
                    Shown(part.name, ard_id(event, analysis, part.operation, groups),
                          layouts.pattern_of(event, part), analysis["id"])
                    for part in row.parts)))
            made.append(PlannedRow(row.label, row.cell, tuple(row_cells), block.section,
                                   row.indent))
        return made

    def by_group(block: layouts.Block) -> list[PlannedRow]:
        """One row per group of the row grouping, in its order (a groups block)."""
        analysis = event.analyses[block.analysis]
        grouping = event.groupings[block.grouping]
        labels = dict(block.labels)
        ordered = sorted(enumerate(grouping["groups"]),
                         key=lambda item: (item[1].get("order", 0), item[0]))
        made = []
        extra = {cell.column: cell for cell in block.extra}
        for number, (_, group) in enumerate(ordered):
            row_cells = []
            for column, column_group, _ in columns:
                if column_group[0] == EXTRA:
                    # The extra cells of a groups block stand in its first row (issue #31).
                    row_cells.append(extra_cell(column, extra.get(column_group[1])
                                                if number == 0 else None, {}))
                    continue
                groups = {layout.grouping: column_group, block.grouping: ("id", group["id"])}
                row_cells.append(PlannedCell(column, tuple(
                    Shown(part.name, ard_id(event, analysis, part.operation, groups),
                          layouts.pattern_of(event, part), analysis["id"])
                    for part in block.parts)))
            label = labels.get(group["id"], str(group.get("name") or ""))
            made.append(PlannedRow(label, block.cell, tuple(row_cells), block.section,
                                   block.indent))
        return made

    def values_of(analysis_id: str, names: list[str]) -> list[tuple[str, ...]]:
        """The combinations of values of data-driven groupings that the results of an
        analysis have, sorted A to Z level by level (the sort `alphabetical`)."""
        found = set()
        for row in (rows or {}).values():
            if row["analysis_id"] != analysis_id:
                continue
            groups = results.row_groups(row)
            picked = [groups.get(name) for name in names]
            if all(item is not None and item[0] == "value" for item in picked):
                found.add(tuple(str(item[1]) for item in picked))
        return sorted(found)

    def term_row(block: layouts.Block, analysis_id: str, cells_extra: tuple,
                 values: dict[str, results.Group], label: str, indent: int) -> PlannedRow:
        analysis = event.analyses[analysis_id]
        extra = {cell.column: cell for cell in cells_extra}
        row_cells = []
        for column, column_group, _ in columns:
            if column_group[0] == EXTRA:
                row_cells.append(extra_cell(column, extra.get(column_group[1]), dict(values),
                                            optional=True))
                continue
            groups = {layout.grouping: column_group, **values}
            row_cells.append(PlannedCell(column, tuple(
                Shown(part.name, ard_id(event, analysis, part.operation, groups),
                      layouts.pattern_of(event, part), analysis["id"])
                for part in block.parts)))
        return PlannedRow(label, block.cell, tuple(row_cells), block.section, indent)

    def terms(block: layouts.Block) -> list[PlannedRow]:
        """One row per value of a data-driven row grouping, each followed by the rows of the
        values of the nested grouping that occur with it (a terms block, issue #31). A mock
        shell has no results: one placeholder row per level, naming no ARD row."""
        nested = block.nested
        if rows is None:
            made = []
            for name, indent in [(block.grouping, block.indent),
                                 *([(nested.grouping, nested.indent)] if nested else [])]:
                label = f"<{event.groupings[name].get('name') or name}>"
                made.append(PlannedRow(label, block.cell, tuple(
                    PlannedCell(column, () if group[0] == EXTRA else tuple(
                        Shown(part.name, "", layouts.pattern_of(event, part),
                              block.analysis or "") for part in block.parts))
                    for column, group, _ in columns), block.section, indent))
            return made
        outer = [value for (value,) in values_of(block.analysis, [block.grouping])]
        pairs = values_of(nested.analysis, [block.grouping, nested.grouping]) if nested else []
        made = []
        for value in outer:
            made.append(term_row(block, block.analysis, block.extra,
                                 {block.grouping: ("value", value)}, value, block.indent))
            for first, second in pairs:
                if first == value:
                    made.append(term_row(block, nested.analysis, nested.extra, {
                        block.grouping: ("value", value), nested.grouping: ("value", second)},
                        second, nested.indent))
        return made

    def ordered_groups(name: str) -> list[dict]:
        return [group for _, group in sorted(
            enumerate(event.groupings[name]["groups"]),
            key=lambda item: (item[1].get("order", 0), item[0]))]

    def by_groups(block: layouts.Block) -> list[PlannedRow]:
        """The statistic rows of the block's analyses for every pair of row groups (real-3):
        a group of the first grouping is the section, one of the second a row without cells
        above them; with columns.within the analyses stand side by side in their columns,
        without it one after the other, each under its own heading."""
        outer, inner = block.by
        labels = dict(block.labels)
        empty = tuple(PlannedCell(column, ()) for column, _, _ in columns)

        def label(group: dict) -> str:
            return labels.get(group["id"], str(group.get("name") or ""))

        def stat_cells(row: layouts.StatisticRow, groups: dict[str, results.Group],
                       showing: dict[str, layouts.Shown]) -> tuple[PlannedCell, ...]:
            """The cells of a statistic row: in each column, the analysis it shows."""
            made = []
            for column, group, _ in columns:
                item = showing.get(within.get(column, ""))
                if item is None:
                    made.append(PlannedCell(column, ()))
                    continue
                analysis = event.analyses[item.analysis]
                every = {layout.grouping: group, **groups}
                made.append(PlannedCell(column, tuple(
                    Shown(part.name, ard_id(event, analysis, part.operation, every),
                          layouts.pattern_of(event, part), analysis["id"])
                    for part in row.parts)))
            return tuple(made)

        made = []
        for first_group in ordered_groups(outer):
            section = label(first_group)
            for second_group in ordered_groups(inner):
                groups = {outer: ("id", first_group["id"]), inner: ("id", second_group["id"])}
                present = [item for item in block.shown if first_group["id"] not in item.skip
                           and second_group["id"] not in item.skip]
                if not present:
                    continue
                if within:
                    made.append(PlannedRow(label(second_group), "", empty, section))
                    showing = {item.column or "": item for item in present}
                    made += [PlannedRow(row.label, row.cell, stat_cells(row, groups, showing),
                                        section, row.indent) for row in block.statistics]
                    continue
                for item in present:
                    made.append(PlannedRow(item.heading.format(group=label(second_group)), "",
                                           empty, section))
                    made += [PlannedRow(row.label, row.cell,
                                        stat_cells(row, groups, {"": item}), section, row.indent)
                             for row in block.statistics]
        return made

    planned = []
    for block in layout.blocks:
        if block.kind == "statistics":
            planned += statistics(block)
            continue
        if block.kind == "by_groups":
            planned += by_groups(block)
            continue
        if block.kind == "groups":
            planned += by_group(block)
            continue
        if block.kind == "terms":
            planned += terms(block)
            continue
        if block.kind == "header":
            label = block.label if block.label is not None else " ".join(
                sections.get("Rowlabel Header", []))
            planned.append(PlannedRow(label, block.cell, cells(block, None),
                                      layouts.HEADER_SECTION))
            continue
        for analysis_id, label in block.analyses:
            planned.append(PlannedRow(layouts.analysis_label(event, analysis_id, label),
                                      block.cell, cells(block, analysis_id), block.section,
                                      block.indent))
    titles = layout.titles if layout.titles is not None else tuple(sections.get("Title", []))
    footnotes = layout.footnotes if layout.footnotes is not None else tuple(
        [*sections.get("Abbreviation", []), *sections.get("Footnote", [])])
    return Plan(layout.output, titles, footnotes, tuple(columns), tuple(planned), layout.missing,
                spanners)


Texts = dict[tuple[str, str], str]  # (ARD row, pattern) -> the text it is shown as


def cell_text(template: str, shown: tuple[Shown, ...], texts: Texts) -> str:
    """A cell template filled with the text of every part; an empty cell shows nothing."""
    if not shown:
        return ""
    return template.format(**{item.name: texts[(item.ard, item.pattern)] for item in shown})


def cell_rows(shown: tuple[Shown, ...]) -> list[str]:
    """The ARD rows of a cell, each once, in the order of its parts. A placeholder of a
    mock shell (its ARD row is "") names none."""
    return list(dict.fromkeys(item.ard for item in shown if item.ard))


def _our_texts(planned: Plan, rows: Rows | None) -> tuple[Texts, list[str]]:
    """The text of every result of the plan by our display rule; and what is missing."""
    texts: Texts = {}
    absent = []
    for row in planned.rows:
        for cell in row.cells:
            for item in cell.shown:
                key = (item.ard, item.pattern)
                if rows is None:
                    texts[key] = methods.pattern_text(None, item.pattern, mock=True)
                elif item.ard not in rows:
                    absent.append(item.ard)
                else:
                    text = methods.pattern_text(rows[item.ard]["raw_value"], item.pattern)
                    texts[key] = planned.missing if text is None else text
    return texts, sorted(set(absent))


def fill(planned: Plan, rows: Rows | None) -> dict:
    """The grid of a plan. With `rows` None it is the mock shell."""
    texts, absent = _our_texts(planned, rows)
    if absent:
        message = (f"{len(absent)} results of the layout are not in the ARD, for example "
                   f"{absent[0]}")
        values = {"=" + quote(str(group[1]), safe="") for _, group, _ in planned.columns
                  if group[0] == "value"}
        if any(part in values for key in absent for part in key.split("/")):
            # The review of real-3a, F2: no silent zero and no number without its ARD row.
            message += (". The column grouping is data-driven: a group without a record of an "
                        "analysis has no result there (rules I9, I10). List the groups before "
                        "the engines run (defined groups, as specfirst.gen.gold."
                        "resolve_groupings does, ADR-007), and the engine gives the group its "
                        "count of 0 (rule I11)")
        raise GridError(message)
    made = []
    for number, row in enumerate(planned.rows, start=1):
        record: dict[str, object] = {"id": f"r{number}", "label": row.label}
        if row.indent:
            record["indent"] = row.indent
        if row.section is not None:
            record["section"] = row.section
        record["cells"] = [{
            "id": f"cell:{quote(planned.output, safe='')}/r{number}/{cell.column}",
            "column": cell.column, "text": cell_text(template_of(row, cell), cell.shown, texts),
            "ard": cell_rows(cell.shown),
        } for cell in row.cells]
        made.append(record)
    spanners = dict(planned.spanners)
    return {"schema": SCHEMA, "output_id": planned.output, "titles": list(planned.titles),
            "columns": [{"id": column, "label": label,
                         **({"spanner": spanners[column]} if column in spanners else {})}
                        for column, _, label in planned.columns],
            "rows": made, "footnotes": list(planned.footnotes)}


def build(event: ars.Event, layout: layouts.Layout, rows: Rows) -> dict:
    """The grid of an output from its layout and the ARD rows."""
    return fill(plan(event, layout, rows), rows)


def shell(event: ars.Event, layout: layouts.Layout) -> dict:
    """The mock shell of an output: the grid without results, masks in place of numbers."""
    return fill(plan(event, layout, None), None)


def grid_problems(grid: object, root: Path) -> list[str]:
    """Why a value is not a grid: the schema, and what the schema cannot say."""
    found = schemas.problems("grid", grid, root=root)
    if found:
        return found
    columns = [column["id"] for column in grid["columns"]]
    if columns != [f"c{number}" for number in range(1, len(columns) + 1)]:
        found.append("the columns are not numbered c1, c2, ... in order")
    output = quote(grid["output_id"], safe="")
    for number, row in enumerate(grid["rows"], start=1):
        if row["id"] != f"r{number}":
            found.append(f"row {row['id']}: the rows are not numbered r1, r2, ... in order")
        if [cell["column"] for cell in row["cells"]] != columns:
            found.append(f"row {row['id']}: its cells are not one per column, in order")
        found += [f"cell {cell['id']}: its ID is not that of its row and column"
                  for cell in row["cells"]
                  if cell["id"] != f"cell:{output}/{row['id']}/{cell['column']}"]
    return found


def numeric(cell: dict) -> bool:
    """A cell that prints a number: its text holds a digit."""
    return any(character.isdigit() for character in cell["text"])


# ---- P2 for grid text: the formatted values of a reference ---------------------------


@dataclass
class DisplayComparison:
    output: str
    cells: int = 0
    results: int = 0  # results shown, over all cells
    equal: int = 0  # cells whose text is the reference's
    classified: Counter = field(default_factory=Counter)  # class -> cells with a difference
    differing: dict[str, tuple[str, str]] = field(default_factory=dict)  # cell -> (ours, theirs)
    no_reference: list[str] = field(default_factory=list)  # results the reference does not format
    problems: list[str] = field(default_factory=list)
    formats_used: set[str] = field(default_factory=set)  # entries of `formats` that hold
    uncompared: int = 0  # cells with a result the reference does not format (issue #31)
    shell_rows: int = 0  # rows of the mock shell held against the table shell (F1 of real-3a)
    shell_lines: int = 0  # rows of the table shell with cells

    def lines(self) -> list[str]:
        said = [f"grid {self.output}: {self.cells} cells show {self.results} results; "
                f"{self.equal} cells equal the reference's formatted values, "
                f"{len(self.differing)} differ, {sum(self.classified.values())} of them "
                "with one class"]
        said += [f"  {count} cells differ by a result classed {name}"
                 for name, count in sorted(self.classified.items())]
        if self.no_reference:
            said.append(f"  results the reference gives no formatted value for: "
                        f"{len(self.no_reference)} (their cells are not compared)")
        return said


def reference_text(item: results.Embedded, pattern: str) -> str | None:
    """The reference's own raw value, shown by our display rule under the same pattern."""
    if item.printed == "":
        return None
    try:
        return methods.pattern_text(float(item.printed), pattern)
    except (ValueError, methods.MethodError):
        return None


def half_problem(item: results.Embedded, ours: object, pattern: str, cls: str) -> str | None:
    """Why the proof `half_in_floating_error` does not hold; None when it does (real-3).

    What it shows, and no cause beyond it: the reference's raw value, as it is written,
    lies exactly on a half at the decimals of the pattern, and its formatted value is that
    value under the pattern; our value is the same number within the relative 1e-9 of
    rule R11, on the other side of the half, so our display rule rounds it the other way;
    and the other rule, which first rounds the value to 12 significant digits (as the
    reference writes its raw values) and then applies the pattern, gives the reference's
    formatted value from our value. That is the build of the alternative that PLAN.md
    section 4.8 asks of a `rule_choice`, for one result. On the pilot the value is a change
    of 0.05 (such as 36.94 - 36.89) that binary floating point holds as
    0.04999999999999716, in the public reference ADaM as in ours.
    """
    from decimal import Decimal, InvalidOperation

    if cls != "rule_choice":
        return "a value at a half in floating error proves a rule_choice only"
    decimals = len(methods.pattern_mask(pattern)[1].partition(".")[2])
    try:
        exact = Decimal(item.printed)
    except InvalidOperation:
        return f"the reference's raw value {item.printed!r} is no number"
    if not isinstance(ours, float) or not exact.is_finite() or (
            abs(exact.scaleb(decimals)) % 1 != Decimal("0.5")):
        return (f"the reference's raw value {item.printed} is not on a half at {decimals} "
                "decimals")
    if not results.same(float(exact), ours):
        return f"our value {ours!r} is not the reference's {item.printed} within a relative 1e-9"
    if (Decimal(repr(ours)) - exact) * (1 if exact > 0 else -1) >= 0:
        return f"our value {ours!r} is not on the other side of the half {item.printed}"
    if reference_text(item, pattern) != item.formatted:
        return (f"the reference's formatted value {item.formatted!r} is not its raw value "
                f"{item.printed} under the pattern {pattern!r}")
    other = methods.pattern_text(float(f"{ours:.12g}"), pattern)
    if other != item.formatted:
        return (f"our value rounded to 12 significant digits under the pattern is {other!r}, "
                f"not the reference's {item.formatted!r}")
    return None


def compare_reference(event: ars.Event, layout: layouts.Layout, grid: dict, rows: Rows,
                      explained: dict[str, str],
                      formats: dict[str, dict] | None = None) -> DisplayComparison:
    """Compare every cell text of a grid with the formatted values the event embeds.

    The expected text of a cell is its template filled with the reference's
    `formattedValue` of every result it shows. A cell that differs is
    classified when every part that differs shows a result whose own
    difference from the reference has a class and a proof that holds
    (`explained`: ARD row -> class), the reference's formatted value is its
    own raw value under the same pattern, and all such parts have the same
    class. A part may differ by display only (`formats`, issue #31: ARD row ->
    entry of the exceptions file): the reference's raw value under the
    pattern is our text, and its formatted value, the entry's, is not; the
    part then has the entry's class. Any other difference is a difference
    with no class.

    The grid is also held against the plan: its cells must show the results
    the layout asks for, with the text our display rule gives; every result
    the reference formats for an analysis of the output must be shown by a
    cell; no cell shows an analysis the reference does not list for the
    output (when it embeds results; the review of real-3a, F3); and the rows
    must show the analyses in the order in which the reference lists them.

    What this cannot see: formatted values are of results, not of cells.
    Which results share a cell, in which order, and with what text between
    them is held against the example's table shell where the kit pins one
    (specfirst.machine.shells, F1), as are the row labels and the sections;
    two parts with the same mask ("XX.X, XX.X") are told apart only by the
    label of a statistic row, which the layout holds against the labels of
    the ARS operations it shows ("Q1, Q3"; the review of real-3, F2);
    a part of a body row that names another analysis than its row's is
    refused by the layout unless the row's results are computed from it
    (F3). Held against nothing here: the titles, the footnotes and the
    indents, which the layout or the ARS display gives. A cell whose result
    the reference gives no formatted value for is counted as not compared
    and does not fail this comparison (`uncompared`); a gate that asks for
    none says so by its counts (the review of real-3a, F9).
    """
    found = DisplayComparison(layout.output)
    try:
        planned = plan(event, layout, rows)
    except GridError as error:
        found.problems.append(str(error))
        return found
    ours, absent = _our_texts(planned, rows)
    found.problems += [f"{key}: the layout shows it, the ARD does not have it" for key in absent]
    embedded = results.embedded(event)
    by_id = {row["id"]: row for row in grid.get("rows", [])}
    if [column["label"] for column in grid.get("columns", [])] != [
            label for _, _, label in planned.columns]:
        found.problems.append("the columns of the grid are not those of the layout")
    if len(by_id) != len(planned.rows):
        found.problems.append(f"the grid has {len(by_id)} rows, the layout gives "
                              f"{len(planned.rows)}")
    if (grid.get("titles"), grid.get("footnotes")) != (list(planned.titles),
                                                       list(planned.footnotes)):
        found.problems.append("the titles or the footnotes of the grid are not those of the "
                              "layout")
    shown: set[str] = set()
    for number, row in enumerate(planned.rows, start=1):
        record = by_id.get(f"r{number}")
        cells = {cell["column"]: cell for cell in (record or {}).get("cells", [])}
        if record is not None and record["label"] != row.label:
            found.problems.append(f"row r{number}: the label is not that of the layout")
        for cell in row.cells:
            there = cells.get(cell.column)
            where = f"cell r{number}/{cell.column}"
            if there is None:
                found.problems.append(f"{where}: the layout has it, the grid does not")
                continue
            found.cells += 1
            found.results += len(cell.shown)
            wanted = cell_rows(cell.shown)
            shown.update(wanted)
            if there["ard"] != wanted:
                found.problems.append(f"{there['id']}: its ARD rows are not those the layout "
                                      "shows there")
                continue
            if any(key in absent for key in wanted):
                continue  # reported above
            if there["text"] != cell_text(template_of(row, cell), cell.shown, ours):
                found.problems.append(f"{there['id']}: the text {there['text']!r} is not what "
                                      "the layout and the ARD give")
                continue
            without = [key for key in wanted
                       if key not in embedded or embedded[key].formatted is None]
            if without:
                found.no_reference += without
                found.uncompared += 1
                continue
            theirs = cell_text(template_of(row, cell), cell.shown, {
                (item.ard, item.pattern): embedded[item.ard].formatted for item in cell.shown})
            if there["text"] == theirs:
                found.equal += 1
                continue
            found.differing[there["id"]] = (there["text"], theirs)
            classes, reasons = set(), []
            for item in cell.shown:
                text = ours[(item.ard, item.pattern)]
                if text == embedded[item.ard].formatted:
                    continue
                if item.ard in (formats or {}):
                    entry = formats[item.ard]
                    raw = reference_text(embedded[item.ard], item.pattern)
                    half = entry["proof"].get("kind") == "half_in_floating_error"
                    if entry["formatted"] != embedded[item.ard].formatted:
                        reasons.append(f"{item.ard}: the exceptions give the formatted value "
                                       f"{entry['formatted']!r}, the reference has "
                                       f"{embedded[item.ard].formatted!r}")
                    elif half:
                        problem = half_problem(embedded[item.ard], rows[item.ard]["raw_value"],
                                               item.pattern, entry["class"])
                        if problem:
                            reasons.append(f"{item.ard}: {problem}")
                        else:
                            classes.add(entry["class"])
                            found.formats_used.add(item.ard)
                    elif raw != text:
                        reasons.append(f"{item.ard}: the reference's raw value "
                                       f"{embedded[item.ard].printed} under the pattern "
                                       f"{item.pattern!r} is {raw!r}, ours is {text!r}: the "
                                       "values differ, not their display")
                    else:
                        classes.add(entry["class"])
                        found.formats_used.add(item.ard)
                    continue
                if item.ard not in explained:
                    reasons.append(f"{item.ard} is shown as {text!r}, the reference "
                                   f"has {embedded[item.ard].formatted!r}, and the result has "
                                   "no classified difference")
                elif reference_text(embedded[item.ard], item.pattern) != embedded[
                        item.ard].formatted:
                    reasons.append(f"{item.ard}: the reference's formatted value "
                                   f"{embedded[item.ard].formatted!r} is not its raw value "
                                   f"{embedded[item.ard].printed} under the pattern "
                                   f"{item.pattern!r}")
                else:
                    classes.add(explained[item.ard])
            if reasons or len(classes) != 1:
                reasons = reasons or [f"its parts have the classes {', '.join(sorted(classes))}"]
                found.problems.append(f"{there['id']}: text {there['text']!r}, reference "
                                      f"{theirs!r}: a difference with no class: "
                                      + "; ".join(reasons))
            else:
                found.classified[classes.pop()] += 1
    listed = ars.listed_analyses(event, layout.output)
    for key, item in sorted(embedded.items()):
        if item.analysis_id in listed and item.formatted is not None and key not in shown:
            found.problems.append(f"{key}: the reference formats this result of the output "
                                  f"({item.formatted!r}), and no cell shows it")
    if embedded:
        # The review of real-3a, F3: a row of another output. A reference that embeds results
        # lists the analyses of each output; a cell shows those analyses only.
        others = sorted({item.analysis for row in planned.rows for cell in row.cells
                         for item in cell.shown if item.analysis not in listed})
        found.problems += [f"the grid shows results of {name}, which the reference does not list "
                           "for the output" for name in others]
    # The formatted values cannot say in which order the parts of a cell stand (the table
    # shell does, specfirst.machine.shells). The list does say in which order the analyses
    # of the output stand.
    ours_in_order = list(dict.fromkeys(item.analysis for row in planned.rows
                                       for cell in row.cells for item in cell.shown
                                       if item.analysis in listed))
    theirs_in_order = [name for name in listed if name in ours_in_order]
    if ours_in_order != theirs_in_order:
        found.problems.append("the rows show the analyses in the order "
                              f"{', '.join(ours_in_order)}; the reference lists them as "
                              f"{', '.join(theirs_in_order)}")
    return found
