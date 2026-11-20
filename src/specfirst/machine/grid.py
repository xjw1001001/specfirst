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
    used |= {block.analysis for block in layout.blocks if block.kind in ("statistics", "groups")}
    found_columns = _columns(event, layout, rows, used)
    if not found_columns:
        raise GridError(f"the column grouping {layout.grouping} has no group")
    found_columns += [((EXTRA, name), label) for name, label in layout.extra]
    columns = [(f"c{number}", group, label) for number, (group, label)
               in enumerate(found_columns, start=1)]

    def cells(block: layouts.Block, analysis_id: str | None) -> tuple[PlannedCell, ...]:
        made = []
        for column, group, _ in columns:
            if group[0] == EXTRA:
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
                    cell = extra.get(group[1])
                    row_cells.append(PlannedCell(column, () if cell is None else tuple(
                        Shown(part.name, ard_id(event, event.analyses[part.analysis],
                                                part.operation, {}),
                              layouts.pattern_of(event, part), part.analysis)
                        for part in cell.parts), None if cell is None else cell.cell))
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
        for _, group in ordered:
            row_cells = []
            for column, column_group, _ in columns:
                if column_group[0] == EXTRA:
                    row_cells.append(PlannedCell(column, ()))
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

    planned = []
    for block in layout.blocks:
        if block.kind == "statistics":
            planned += statistics(block)
            continue
        if block.kind == "groups":
            planned += by_group(block)
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
    return Plan(layout.output, titles, footnotes, tuple(columns), tuple(planned), layout.missing)


Texts = dict[tuple[str, str], str]  # (ARD row, pattern) -> the text it is shown as


def cell_text(template: str, shown: tuple[Shown, ...], texts: Texts) -> str:
    """A cell template filled with the text of every part; an empty cell shows nothing."""
    if not shown:
        return ""
    return template.format(**{item.name: texts[(item.ard, item.pattern)] for item in shown})


def cell_rows(shown: tuple[Shown, ...]) -> list[str]:
    """The ARD rows of a cell, each once, in the order of its parts."""
    return list(dict.fromkeys(item.ard for item in shown))


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
        raise GridError(f"{len(absent)} results of the layout are not in the ARD, for example "
                        f"{absent[0]}")
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
    return {"schema": SCHEMA, "output_id": planned.output, "titles": list(planned.titles),
            "columns": [{"id": column, "label": label} for column, _, label in planned.columns],
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


def compare_reference(event: ars.Event, layout: layouts.Layout, grid: dict, rows: Rows,
                      explained: dict[str, str]) -> DisplayComparison:
    """Compare every cell text of a grid with the formatted values the event embeds.

    The expected text of a cell is its template filled with the reference's
    `formattedValue` of every result it shows. A cell that differs is
    classified when every part that differs shows a result whose own
    difference from the reference has a class and a proof that holds
    (`explained`: ARD row -> class), the reference's formatted value is its
    own raw value under the same pattern, and all such parts have the same
    class. Any other difference is a difference with no class.

    The grid is also held against the plan: its cells must show the results
    the layout asks for, with the text our display rule gives; every result
    the reference formats for an analysis of the output must be shown by a
    cell; and the rows must show the analyses in the order in which the
    reference lists them.

    What this cannot see: a reference formats results, not cells. Which
    results share a cell, in which order, and with what text between them
    is the layout's, and no formatted value says otherwise.
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
    # A reference formats results, not cells: it cannot say in which order the parts
    # of a cell stand. It does say in which order it lists the analyses of the output.
    ours_in_order = list(dict.fromkeys(item.analysis for row in planned.rows
                                       for cell in row.cells for item in cell.shown
                                       if item.analysis in listed))
    theirs_in_order = [name for name in listed if name in ours_in_order]
    if ours_in_order != theirs_in_order:
        found.problems.append("the rows show the analyses in the order "
                              f"{', '.join(ours_in_order)}; the reference lists them as "
                              f"{', '.join(theirs_in_order)}")
    return found
