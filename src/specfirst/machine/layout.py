"""Layout spec v0 (PLAN.md section 7.4, ADR-003): what a display needs and ARS does not hold.

A layout belongs to one output of an ARS reporting event. It names the
column axis, the row axis and, for every cell, the results it shows and
the pattern each result is shown by. It holds rules, no numbers (rule R6).

    layout: 0
    output: <ARS output ID>
    titles: [text, ...]       optional; default: the Title section of the output's display
    footnotes: [text, ...]    optional; default: its Abbreviation and Footnote sections
    missing: ""               optional; the text of a result that has no value
    columns:
      grouping: <ARS grouping ID>    one column per group
      values: [text, ...]            a data-driven grouping only: its values, in
                                     the order of the columns; default: the values
                                     the results have, sorted
      labels: {<group>: text}        optional; default: the name of a defined
                                     group, the value of a data-driven one
      extra:                         optional (amendment of real-5b): columns after
        - {id: <name>, label: text}  those of the groups, which are no group; their
                                     cells are empty unless a row fills them; an
                                     extra column may have a `spanner` (issue #31),
                                     a header over it and its neighbours with the
                                     same spanner
      within:                        optional (real-3): one column per group and
        - {id: <name>, label: text}  item, in this order: the item's label is the
                                     column's, the group's label its spanner. A
                                     layout with `within` has header and by_groups
                                     blocks only, and no extra column
    rows:                     blocks, from the top
      - kind: header          one row, shown in the table header under the column labels
        label: text           optional; default: the Rowlabel Header section of the display
        cell: "{N}"
        parts:
          N: {analysis: <analysis ID>, operation: <operation ID>, pattern: "(N=XX)"}
      - kind: analyses        one row per listed analysis
        section: text         optional; a name the rows of the block share
        indent: 0             optional
        cell: "{n} {pct}"
        parts:
          n: {operation: <operation ID>}
          pct: {operation: <operation ID>, pattern: "( XX.X)"}
        analyses:
          - <analysis ID>                    label: the analysis's label, else its name
          - {id: <analysis ID>, label: text}

      - kind: statistics      one row per statistic of one analysis (ADR-003, amendment
                              of real-5a)
        analysis: <analysis ID>
        section: text         optional
        indent: 0             optional; the indent of every row that gives none
        columns: [<group>, ...]   optional; the groups of the column grouping whose
                              columns show results. The cells of the other columns are
                              empty. Default: every column.
        rows:
          - label: text
            indent: 1         optional
            cell: "{mean} ({sd})"
            parts:
              mean: {operation: <operation ID>, pattern: "X.X"}
              sd: {operation: <operation ID>, pattern: "X.XX"}
            extra:            optional: the cells of extra columns in this row
              <name>: {cell: "{p}", parts: {p: {analysis: <ID>, operation: <ID>}}}

      - kind: groups          one row per group of a row grouping (amendment of real-5b)
        analysis: <analysis ID>   its groupings: the column grouping and the row
                              grouping, both with results by group
        grouping: <ARS grouping ID>   the row grouping, with defined groups
        section: text         optional
        indent: 0             optional
        labels: {<group>: text}   optional; default: the name of the group
        cell: "{n} ({pct})"
        parts:
          n: {operation: <operation ID>, pattern: "XX"}
        extra:                optional (issue #31): the cells of extra columns in the
          <name>: {cell: "{p}", parts: {p: {analysis: <ID>, operation: <ID>}}}
                              first row of the block; the analysis compares the
                              column grouping and the row grouping (a test of the
                              table of the two)

      - kind: terms           one row per value of a data-driven row grouping (issue #31)
        analysis: <analysis ID>   split by the column grouping and the row grouping
        grouping: <ARS grouping ID>   the row grouping, data-driven: its rows are the
                              values the results have
        sort: alphabetical    the order of the rows; v0 knows this one
        section: text         optional
        indent: 0             optional
        cell: "{n} {pct}"
        parts: {...}          as in a groups block
        extra:                optional: the cells of extra columns in every row; the
          <name>: {cell, parts}   analysis compares the column grouping and is split
                              by the row grouping; a value it has no result for has
                              an empty cell there
        nested:               optional: under each row, one row per value of a second
          analysis: <ID>      data-driven grouping that occurs with it; the analysis is
          grouping: <ID>      split by the column grouping, the row grouping and this
          indent: 1           one, and its rows take the cell and parts of the block
          extra: {...}        as above, split by both row groupings

      - kind: by_groups       the statistic rows of one or more analyses for every pair of
                              groups of two row groupings (real-3: the vital signs by
                              parameter and visit)
        by: [<ID>, <ID>]      two row groupings with defined groups: a group of the first
                              is the section of its rows, a group of the second a row
                              without cells above them
        labels: {<group>: text}   optional; default: the name of the group
        indent: 1             optional: the indent of the statistic rows
        analyses:             each split by the column grouping and the two row groupings,
          - analysis: <ID>    all of one method
            column: <name>    with columns.within: the item whose column it fills
            heading: "{group}"    without columns.within: the row above its rows;
                              {group} is the group of the second grouping
            skip: [<group>, ...]  optional: the groups of the row groupings it has no
                              rows for (its data subset leaves them without records; the
                              reference holds this, as every result it formats is shown)
        rows:                 the statistic rows, as in a statistics block; their parts
          - label: text       name operations of the analyses' method
            cell: "{n}"
            parts: {n: {operation: <ID>}}

A cell template is text with `{name}` where the part of that name goes. A
part is one result: an ARS operation of the row's analysis (in a header
block the part names its analysis). Its pattern is a pattern of the
registry's display.pattern; when the layout gives none, the `resultPattern`
of the ARS operation is taken, and a part with neither is an error.

A part of an analyses block that names an analysis shows a result the
row's results are computed from (the denominator of a percent, "{n}/{N}");
the result of another row is refused. An analysis stands in one block of the
body of a layout; the count under the column headers may stand in the body
again (the review of real-3a, F3).

In a header block and an analyses block, an analysis has the column
grouping as its only grouping, with results by group. In a statistics block
it may also compare the column grouping (results by group false, as a test
does): its one result per operation is then shown in the one column its
`columns` lists. Columns that compare two arms are statistics blocks of
this kind: a comparison of each arm with a reference arm stands in the
columns of the arms that are compared (`columns`), and the reference's
column stays empty.

A terms block (issue #31) is the table by organ class and term: its rows are
known only from the results, so a mock shell shows one placeholder row per
level, `<name of the grouping>`, whose cells show masks and name no ARD row.

A by_groups block (real-3) is a table of observed values and changes by
parameter and visit. With `columns.within` (the horizontal layout) every
group of the column grouping has one column per analysis, and a pair of row
groups has one row without cells and the statistic rows, whose cells show
each analysis in its column; a column of an analysis that skips the pair is
empty. Without it (the vertical layout) each analysis that does not skip
the pair has its own row without cells, its `heading`, and its statistic
rows. The count under the column headers stands in the first column of
each group when the layout has `within`.

An extra column (real-5b) holds what belongs to no group, such as the
p-value of a test that compares all the groups (CSR Table 14-3.13). A row
of a statistics block fills it with a part of another analysis that
compares the column grouping, with its own cell template. A groups block
has one row per group of a row grouping, in the grouping's order, for an
analysis split by both groupings. The blocks the other table families need
(a total column, a threshold) are added later, as kinds of this list.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from string import Formatter

import yaml

from specfirst.machine import ars, methods

FORMAT = 0
KINDS = ("header", "analyses", "statistics", "groups", "terms", "by_groups")
# The orders of the rows of a terms block (issue #31): by value, A to Z.
SORTS = ("alphabetical",)
# The section of a grid row that is shown in the table header (ADR-003, decision 4).
HEADER_SECTION = "@header"
_KEYS = {"layout", "output", "titles", "footnotes", "missing", "columns", "rows"}
_COLUMN_KEYS = {"grouping", "values", "labels", "extra", "within"}
_BLOCK_KEYS = {"header": {"kind", "label", "cell", "parts"},
               "analyses": {"kind", "section", "indent", "cell", "parts", "analyses"},
               "statistics": {"kind", "analysis", "section", "indent", "columns", "rows"},
               "groups": {"kind", "analysis", "grouping", "section", "indent", "labels", "cell",
                          "parts", "extra"},
               "terms": {"kind", "analysis", "grouping", "sort", "section", "indent", "cell",
                         "parts", "extra", "nested"},
               "by_groups": {"kind", "by", "labels", "indent", "analyses", "rows"}}
_NESTED_KEYS = {"analysis", "grouping", "indent", "extra"}
_SHOWN_KEYS = {"analysis", "column", "heading", "skip"}
_ROW_KEYS = {"label", "indent", "cell", "parts", "extra"}
_PART_KEYS = {"analysis", "operation", "pattern"}


class LayoutError(ValueError):
    """The layout cannot be used."""


@dataclass(frozen=True)
class Part:
    name: str
    operation: str
    analysis: str | None  # None: the analysis of the row
    pattern: str | None  # None: the resultPattern of the ARS operation


@dataclass(frozen=True)
class ExtraCell:
    """The cell of an extra column in a row: its column, template and parts."""

    column: str
    cell: str
    parts: tuple[Part, ...]


@dataclass(frozen=True)
class StatisticRow:
    """One row of a statistics block: its label, its cell template and its parts."""

    label: str
    cell: str
    parts: tuple[Part, ...]
    indent: int
    extra: tuple[ExtraCell, ...] = ()


@dataclass(frozen=True)
class Nested:
    """The rows of a second data-driven grouping under each row of a terms block."""

    analysis: str
    grouping: str
    indent: int
    extra: tuple[ExtraCell, ...] = ()


@dataclass(frozen=True)
class Shown:
    """An analysis of a by_groups block: its column (with `within`), the text of the row
    above its rows (without), and the groups it has no rows for (real-3)."""

    analysis: str
    column: str | None = None
    heading: str = "{group}"
    skip: tuple[str, ...] = ()


@dataclass(frozen=True)
class Block:
    kind: str
    cell: str  # the template; "" in a statistics block, whose rows have their own
    parts: tuple[Part, ...]  # in the order the template names them
    label: str | None = None  # header
    section: str | None = None  # analyses, statistics
    indent: int = 0
    analyses: tuple[tuple[str, str | None], ...] = ()  # (analysis ID, label or None)
    analysis: str | None = None  # statistics
    statistics: tuple[StatisticRow, ...] = ()  # statistics
    columns: tuple[str, ...] | None = None  # statistics: the groups whose columns show results
    grouping: str | None = None  # groups, terms: the row grouping
    labels: tuple[tuple[str, str], ...] = ()  # groups: row labels by group
    extra: tuple[ExtraCell, ...] = ()  # groups: the first row's; terms: every row's
    sort: str | None = None  # terms
    nested: Nested | None = None  # terms
    by: tuple[str, ...] = ()  # by_groups: the two row groupings
    shown: tuple[Shown, ...] = ()  # by_groups: its analyses


@dataclass(frozen=True)
class Layout:
    output: str
    grouping: str
    blocks: tuple[Block, ...]
    values: tuple[str, ...] | None = None
    labels: tuple[tuple[str, str], ...] = ()
    titles: tuple[str, ...] | None = None
    footnotes: tuple[str, ...] | None = None
    missing: str = ""
    extra: tuple[tuple[str, str], ...] = ()  # extra columns: (name, label)
    spanners: tuple[tuple[str, str], ...] = ()  # extra columns: (name, spanner), issue #31
    within: tuple[tuple[str, str], ...] = ()  # columns per group: (name, label), real-3


def template_names(template: str) -> list[str]:
    """The part names of a cell template, in the order they stand in it."""
    try:
        fields = list(Formatter().parse(template))
    except ValueError as error:
        raise LayoutError(f"cell template {template!r}: {error}") from error
    names = []
    for _, name, spec, conversion in fields:
        if name is None:
            continue
        if not name.isidentifier() or spec or conversion:
            raise LayoutError(f"cell template {template!r}: write a part as {{name}}")
        names.append(name)
    return names


def _texts(value: object, where: str, problems: list[str]) -> tuple[str, ...] | None:
    if value is None:
        return None
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        problems.append(f"{where}: must be a list of texts")
        return None
    return tuple(value)


def _indent(value: object, where: str, problems: list[str]) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        problems.append(f"{where}: 'indent' must be a whole number from 0")
        return 0
    return value


def _statistics(data: dict, where: str, problems: list[str]) -> Block | None:
    """A statistics block: one row per statistic of one analysis."""
    analysis, section = data.get("analysis"), data.get("section")
    if not isinstance(analysis, str) or not analysis:
        problems.append(f"{where}: a statistics block names its 'analysis'")
        return None
    if section is not None and not isinstance(section, str):
        problems.append(f"{where}: 'section' must be text")
    if section == HEADER_SECTION:
        problems.append(f"{where}: the section name {HEADER_SECTION} is that of a header block")
    indent = _indent(data.get("indent", 0), where, problems)
    columns = _texts(data.get("columns"), f"{where}: columns", problems)
    if columns is not None and (not columns or len(set(columns)) != len(columns)):
        problems.append(f"{where}: 'columns' lists each group once, at least one")
    listed = data.get("rows")
    if not isinstance(listed, list) or not listed:
        problems.append(f"{where}: a statistics block lists its 'rows'")
        return None
    rows = []
    for number, item in enumerate(listed):
        at = f"{where}, rows[{number}]"
        if not isinstance(item, dict) or not isinstance(item.get("label"), str):
            problems.append(f"{at}: a row has a 'label', a 'cell' and its 'parts'")
            continue
        problems += [f"{at}: unknown key '{key}'" for key in sorted(set(item) - _ROW_KEYS)]
        parts = _parts(item.get("cell"), item.get("parts"), "statistics", at, problems)
        if parts is None:
            continue
        if any(part.analysis not in (None, analysis) for part in parts):
            problems.append(f"{at}: a part of a statistics block shows a result of the "
                            "block's analysis")
        rows.append(StatisticRow(item["label"], item["cell"], parts,
                                 _indent(item.get("indent", indent), at, problems),
                                 _extra_cells(item.get("extra"), at, problems)))
    return Block("statistics", "", (), section=section, indent=indent, analysis=analysis,
                 statistics=tuple(rows), columns=columns)


def _extra_cells(given: object, at: str, problems: list[str]) -> tuple[ExtraCell, ...]:
    """The cells of extra columns: each its template and parts, every part naming its analysis."""
    extra = []
    given = given or {}
    if not isinstance(given, dict):
        problems.append(f"{at}: 'extra' maps an extra column to its cell")
        given = {}
    for column, cell in given.items():
        here = f"{at}, extra '{column}'"
        if not isinstance(cell, dict) or set(cell) != {"cell", "parts"}:
            problems.append(f"{here}: needs a 'cell' template and its 'parts'")
            continue
        cell_parts = _parts(cell["cell"], cell["parts"], "header", here, problems)
        if cell_parts is not None:
            extra.append(ExtraCell(str(column), cell["cell"], cell_parts))
    return tuple(extra)


def _parts(template: object, given: object, kind: str, where: str,
           problems: list[str]) -> tuple[Part, ...] | None:
    """The parts of a cell template, in the order the template names them."""
    if not isinstance(template, str) or not isinstance(given, dict) or not given:
        problems.append(f"{where}: needs a 'cell' template and its 'parts'")
        return None
    try:
        names = template_names(template)
    except LayoutError as error:
        problems.append(f"{where}: {error}")
        return None
    if sorted(names) != sorted(given) or len(set(names)) != len(names):
        problems.append(f"{where}: the template names {', '.join(names) or 'no part'}, the "
                        f"parts are {', '.join(sorted(map(str, given)))}; each part stands "
                        "once in the template")
        return None
    parts = []
    for name in names:
        part = given[name]
        if not isinstance(part, dict) or set(part) - _PART_KEYS or not isinstance(
                part.get("operation"), str):
            problems.append(f"{where}, part '{name}': needs an 'operation', and may have an "
                            "'analysis' and a 'pattern'")
            continue
        for key in ("analysis", "pattern"):
            if part.get(key) is not None and not isinstance(part[key], str):
                problems.append(f"{where}, part '{name}': '{key}' must be text")
        if kind == "header" and not part.get("analysis"):
            problems.append(f"{where}, part '{name}': a part of a header names its analysis")
        if part.get("pattern") is not None:
            try:
                methods.pattern_mask(part["pattern"])
            except methods.MethodError as error:
                problems.append(f"{where}, part '{name}': {error}")
        parts.append(Part(name, part["operation"], part.get("analysis"), part.get("pattern")))
    return tuple(parts)


def _groups(data: dict, where: str, problems: list[str]) -> Block | None:
    """A groups block: one row per group of a row grouping (amendment of real-5b)."""
    analysis, grouping, section = data.get("analysis"), data.get("grouping"), data.get("section")
    if not isinstance(analysis, str) or not analysis or not isinstance(grouping, str):
        problems.append(f"{where}: a groups block names its 'analysis' and its row 'grouping'")
        return None
    if section is not None and not isinstance(section, str):
        problems.append(f"{where}: 'section' must be text")
    if section == HEADER_SECTION:
        problems.append(f"{where}: the section name {HEADER_SECTION} is that of a header block")
    labels = data.get("labels") or {}
    if not isinstance(labels, dict) or not all(
            isinstance(key, str) and isinstance(text, str) for key, text in labels.items()):
        problems.append(f"{where}: 'labels' must map a group to its text")
        labels = {}
    parts = _parts(data.get("cell"), data.get("parts"), "groups", where, problems)
    if parts is None:
        return None
    if any(part.analysis not in (None, analysis) for part in parts):
        problems.append(f"{where}: a part of a groups block shows a result of the block's "
                        "analysis")
    return Block("groups", data["cell"], parts, section=section,
                 indent=_indent(data.get("indent", 0), where, problems), analysis=analysis,
                 grouping=grouping, labels=tuple(sorted(labels.items())),
                 extra=_extra_cells(data.get("extra"), where, problems))


def _terms(data: dict, where: str, problems: list[str]) -> Block | None:
    """A terms block: one row per value of a data-driven row grouping (issue #31)."""
    analysis, grouping, section = data.get("analysis"), data.get("grouping"), data.get("section")
    if not isinstance(analysis, str) or not analysis or not isinstance(grouping, str):
        problems.append(f"{where}: a terms block names its 'analysis' and its row 'grouping'")
        return None
    if section is not None and not isinstance(section, str):
        problems.append(f"{where}: 'section' must be text")
    if section == HEADER_SECTION:
        problems.append(f"{where}: the section name {HEADER_SECTION} is that of a header block")
    sort = data.get("sort")
    if sort not in SORTS:
        problems.append(f"{where}: 'sort' must be one of {', '.join(SORTS)}")
    parts = _parts(data.get("cell"), data.get("parts"), "groups", where, problems)
    if parts is None:
        return None
    if any(part.analysis not in (None, analysis) for part in parts):
        problems.append(f"{where}: a part of a terms block shows a result of the block's "
                        "analysis")
    nested = None
    given = data.get("nested")
    if given is not None:
        at = f"{where}, nested"
        if (not isinstance(given, dict) or not isinstance(given.get("analysis"), str)
                or not isinstance(given.get("grouping"), str)):
            problems.append(f"{at}: names its 'analysis' and its 'grouping'")
        else:
            problems += [f"{at}: unknown key '{key}'" for key in sorted(set(given) - _NESTED_KEYS)]
            nested = Nested(given["analysis"], given["grouping"],
                            _indent(given.get("indent", 1), at, problems),
                            _extra_cells(given.get("extra"), at, problems))
    return Block("terms", data["cell"], parts, section=section,
                 indent=_indent(data.get("indent", 0), where, problems), analysis=analysis,
                 grouping=grouping, extra=_extra_cells(data.get("extra"), where, problems),
                 sort=sort, nested=nested)


def _by_groups(data: dict, where: str, problems: list[str]) -> Block | None:
    """A by_groups block: statistic rows for every pair of groups of two row groupings (real-3)."""
    by = _texts(data.get("by"), f"{where}: by", problems)
    if by is None or len(by) != 2 or by[0] == by[1]:
        problems.append(f"{where}: a by_groups block names two row groupings in 'by'")
        return None
    labels = data.get("labels") or {}
    if not isinstance(labels, dict) or not all(
            isinstance(key, str) and isinstance(text, str) for key, text in labels.items()):
        problems.append(f"{where}: 'labels' must map a group to its text")
        labels = {}
    indent = _indent(data.get("indent", 1), where, problems)
    shown = []
    for number, item in enumerate(data.get("analyses") or []):
        at = f"{where}, analyses[{number}]"
        if not isinstance(item, dict) or not isinstance(item.get("analysis"), str) or set(
                item) - _SHOWN_KEYS:
            problems.append(f"{at}: names its 'analysis', and may give its 'column', its "
                            "'heading' and the groups it skips ('skip')")
            continue
        column, heading = item.get("column"), item.get("heading", "{group}")
        skip = _texts(item.get("skip"), f"{at}: skip", problems) or ()
        if column is not None and not isinstance(column, str):
            problems.append(f"{at}: 'column' must be the name of an item of columns.within")
        if not isinstance(heading, str):
            problems.append(f"{at}: 'heading' must be text")
            heading = "{group}"
        else:
            try:
                if set(template_names(heading)) - {"group"}:
                    problems.append(f"{at}: a heading names no part but {{group}}")
            except LayoutError as error:
                problems.append(f"{at}: {error}")
        shown.append(Shown(item["analysis"], column, heading, tuple(skip)))
    if not shown:
        problems.append(f"{where}: a by_groups block lists its 'analyses'")
    names = [item.analysis for item in shown]
    problems += [f"{where}: the analysis '{name}' is listed twice"
                 for name in sorted({name for name in names if names.count(name) > 1})]
    listed = data.get("rows")
    if not isinstance(listed, list) or not listed:
        problems.append(f"{where}: a by_groups block lists its statistic 'rows'")
        return None
    rows = []
    for number, item in enumerate(listed):
        at = f"{where}, rows[{number}]"
        if not isinstance(item, dict) or not isinstance(item.get("label"), str):
            problems.append(f"{at}: a row has a 'label', a 'cell' and its 'parts'")
            continue
        problems += [f"{at}: unknown key '{key}'"
                     for key in sorted(set(item) - (_ROW_KEYS - {"extra"}))]
        parts = _parts(item.get("cell"), item.get("parts"), "by_groups", at, problems)
        if parts is None:
            continue
        if any(part.analysis is not None for part in parts):
            problems.append(f"{at}: a part of a by_groups block names an operation of the "
                            "block's analyses, no analysis")
        rows.append(StatisticRow(item["label"], item["cell"], parts,
                                 _indent(item.get("indent", indent), at, problems)))
    return Block("by_groups", "", (), indent=indent, statistics=tuple(rows),
                 labels=tuple(sorted(labels.items())), by=tuple(by), shown=tuple(shown))


def _block(data: object, where: str, problems: list[str]) -> Block | None:
    if not isinstance(data, dict) or data.get("kind") not in KINDS:
        problems.append(f"{where}: needs a 'kind' out of {', '.join(KINDS)}")
        return None
    kind = data["kind"]
    problems += [f"{where}: unknown key '{key}'" for key in sorted(set(data) - _BLOCK_KEYS[kind])]
    if kind == "statistics":
        return _statistics(data, where, problems)
    if kind == "groups":
        return _groups(data, where, problems)
    if kind == "terms":
        return _terms(data, where, problems)
    if kind == "by_groups":
        return _by_groups(data, where, problems)
    template = data.get("cell")
    parts = _parts(template, data.get("parts"), kind, where, problems)
    if parts is None:
        return None
    label, section, indent = data.get("label"), data.get("section"), data.get("indent", 0)
    for key, value in (("label", label), ("section", section)):
        if value is not None and not isinstance(value, str):
            problems.append(f"{where}: '{key}' must be text")
    if section == HEADER_SECTION:
        problems.append(f"{where}: the section name {HEADER_SECTION} is that of a header block")
    if isinstance(indent, bool) or not isinstance(indent, int) or indent < 0:
        problems.append(f"{where}: 'indent' must be a whole number from 0")
        indent = 0
    analyses: list[tuple[str, str | None]] = []
    if kind == "analyses":
        listed = data.get("analyses")
        if not isinstance(listed, list) or not listed:
            problems.append(f"{where}: lists no analysis")
            listed = []
        for item in listed:
            if isinstance(item, str):
                analyses.append((item, None))
            elif (isinstance(item, dict) and set(item) <= {"id", "label"}
                  and isinstance(item.get("id"), str)
                  and isinstance(item.get("label"), str | None)):
                analyses.append((item["id"], item.get("label")))
            else:
                problems.append(f"{where}: an analysis is its ID, or its 'id' with a 'label'")
        repeated = sorted({name for name, _ in analyses
                           if sum(1 for other, _ in analyses if other == name) > 1})
        problems += [f"{where}: the analysis '{name}' is listed twice" for name in repeated]
    return Block(kind, template, tuple(parts), label, section, indent, tuple(analyses))


def parse(data: object, where: str = "layout") -> Layout:
    """Read a layout. Every problem of its form is reported at once."""
    if not isinstance(data, dict) or data.get("layout") != FORMAT:
        raise LayoutError(f"{where}: expected `layout: {FORMAT}`")
    problems = [f"unknown key '{key}'" for key in sorted(set(data) - _KEYS)]
    output = data.get("output")
    if not isinstance(output, str) or not output:
        problems.append("'output' must name the ARS output")
    columns = data.get("columns")
    if not isinstance(columns, dict) or not isinstance(columns.get("grouping"), str):
        problems.append("'columns' must name its 'grouping'")
        columns = {}
    problems += [f"columns: unknown key '{key}'" for key in sorted(set(columns) - _COLUMN_KEYS)]
    values = _texts(columns.get("values"), "columns.values", problems)
    if values is not None and len(set(values)) != len(values):
        problems.append("columns.values: a value is listed twice")
    labels = columns.get("labels") or {}
    if not isinstance(labels, dict) or not all(
            isinstance(key, str) and isinstance(text, str) for key, text in labels.items()):
        problems.append("columns.labels: must map a group to its text")
        labels = {}
    extra, spanners = [], []
    for number, item in enumerate(columns.get("extra") or []):
        if (not isinstance(item, dict) or not {"id", "label"} <= set(item) <= {
                "id", "label", "spanner"}
                or not isinstance(item["id"], str) or not item["id"].isidentifier()
                or not isinstance(item["label"], str)
                or not isinstance(item.get("spanner", ""), str)):
            problems.append(f"columns.extra[{number}]: an extra column has an 'id' (a name) "
                            "and a 'label', and may have a 'spanner'")
            continue
        extra.append((item["id"], item["label"]))
        if item.get("spanner"):
            spanners.append((item["id"], item["spanner"]))
    if len({name for name, _ in extra}) != len(extra):
        problems.append("columns.extra: an id is listed twice")
    within = []
    for number, item in enumerate(columns.get("within") or []):
        if (not isinstance(item, dict) or set(item) != {"id", "label"}
                or not isinstance(item["id"], str) or not item["id"].isidentifier()
                or not isinstance(item["label"], str)):
            problems.append(f"columns.within[{number}]: an item has an 'id' (a name) and a "
                            "'label'")
            continue
        within.append((item["id"], item["label"]))
    if len({name for name, _ in within}) != len(within):
        problems.append("columns.within: an id is listed twice")
    if within and extra:
        problems.append("columns: a layout with 'within' has no extra column")
    missing = data.get("missing", "")
    if not isinstance(missing, str):
        problems.append("'missing' must be text")
        missing = ""
    rows = data.get("rows")
    if not isinstance(rows, list) or not rows:
        problems.append("'rows' must list at least one block")
        rows = []
    blocks = [_block(item, f"rows[{number}]", problems) for number, item in enumerate(rows)]
    if within:
        problems += [f"rows[{number}]: a layout with columns.within has header and by_groups "
                     "blocks only" for number, block in enumerate(blocks)
                     if block is not None and block.kind not in ("header", "by_groups")]
    for number, block in enumerate(blocks):
        if block is None or block.kind != "by_groups":
            continue
        columns_of = [item.column for item in block.shown]
        if within and sorted(columns_of, key=str) != sorted(name for name, _ in within):
            problems.append(f"rows[{number}]: with columns.within every item is the 'column' of "
                            "one analysis of the block")
        if not within and any(name is not None for name in columns_of):
            problems.append(f"rows[{number}]: an analysis names a 'column', and the layout has no "
                            "columns.within")
    titles = _texts(data.get("titles"), "titles", problems)
    footnotes = _texts(data.get("footnotes"), "footnotes", problems)
    if problems:
        raise LayoutError(f"{where}: " + "; ".join(problems))
    return Layout(output=output, grouping=columns["grouping"],
                  blocks=tuple(block for block in blocks if block is not None), values=values,
                  labels=tuple(sorted(labels.items())), titles=titles, footnotes=footnotes,
                  missing=missing, extra=tuple(extra), spanners=tuple(spanners),
                  within=tuple(within))


def read(path: Path) -> Layout:
    """Read a layout file: YAML, or JSON, which is YAML too."""
    try:
        with open(path, encoding="ascii") as handle:
            data = yaml.safe_load(handle)
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as error:
        raise LayoutError(f"{path.name}: {error}") from error
    return parse(data, path.name)


def pattern_of(event: ars.Event, part: Part) -> str | None:
    """The pattern a part is shown by: the layout's, else that of the ARS operation."""
    if part.pattern is not None:
        return part.pattern
    return event.operations.get(part.operation, ("", {}))[1].get("resultPattern")


def analysis_label(event: ars.Event, analysis_id: str, label: str | None) -> str:
    analysis = event.analyses[analysis_id]
    return label if label is not None else str(analysis.get("label") or analysis.get("name") or "")


def problems(layout: Layout, event: ars.Event) -> list[str]:
    """Why a layout does not fit its reporting event."""
    found = []
    if layout.output not in ars.outputs(event):
        found.append(f"the output '{layout.output}' is not in the reporting event")
    grouping = event.groupings.get(layout.grouping)
    if grouping is None:
        return [*found, f"the column grouping '{layout.grouping}' is not in the reporting event"]
    driven = bool(grouping.get("dataDriven"))
    if layout.values is not None and not driven:
        found.append("columns.values is for a data-driven grouping; this one lists its groups")
    known = None if driven else {group["id"] for group in grouping["groups"]}
    if known is not None:
        found += [f"columns.labels: '{key}' is not a group of {layout.grouping}"
                  for key, _ in layout.labels if key not in known]
        found += [f"columns.extra: '{name}' is the ID of a group of {layout.grouping}"
                  for name, _ in layout.extra if name in known]
    for number, block in enumerate(layout.blocks):
        where = f"rows[{number}]"
        if block.kind == "statistics":
            found += _statistics_problems(layout, event, block, where, known)
            continue
        if block.kind == "groups":
            found += _groups_problems(layout, event, block, where)
            continue
        if block.kind == "terms":
            found += _terms_problems(layout, event, block, where)
            continue
        if block.kind == "by_groups":
            found += _by_groups_problems(layout, event, block, where)
            continue
        rows = block.analyses or ((None, None),)
        for analysis_id, _ in rows:
            for part in block.parts:
                name = part.analysis or analysis_id
                at = f"{where}, part '{part.name}'"
                analysis = event.analyses.get(name)
                if analysis is None:
                    found.append(f"{at}: the analysis '{name}' is not in the reporting event")
                    continue
                if (block.kind == "analyses" and name != analysis_id
                        and analysis_id in event.analyses
                        and name not in _referenced(event.analyses[analysis_id])):
                    # The review of real-3a, F3: the percent of one row in another row.
                    found.append(f"{at}: the row of '{analysis_id}' shows a result of '{name}', "
                                 "which none of its results is computed from")
                at += f", analysis '{name}'"
                if event.operations.get(part.operation, (None,))[0] != analysis.get("methodId"):
                    found.append(f"{at}: '{part.operation}' is not an operation of its method")
                    continue
                groupings = [(entry["groupingId"], bool(entry.get("resultsByGroup")))
                             for entry in event.groupings_of(analysis)]
                if groupings != [(layout.grouping, True)]:
                    found.append(f"{at}: layout v0 shows an analysis whose only grouping is "
                                 f"the column grouping {layout.grouping}, with results by group")
                pattern = pattern_of(event, part)
                if pattern is None:
                    found.append(f"{at}: neither the layout nor the ARS operation gives a "
                                 "pattern")
                    continue
                try:
                    methods.pattern_mask(pattern)
                except methods.MethodError as error:
                    found.append(f"{at}: {error}")
    found += _repeated_problems(layout)
    return sorted(set(found))


def _referenced(analysis: dict) -> set[str]:
    """The analyses whose results the operations of an analysis are computed from (rule I15)."""
    return {str(reference.get("analysisId"))
            for reference in analysis.get("referencedAnalysisOperations") or []}


def block_analyses(block: Block) -> set[str]:
    """The analyses a block stands for: those of its rows, of a header's parts and of its
    extra cells. A part of a body row that names the analysis of a denominator (a cell
    "{n}/{N}") is not counted: it shows a result its row is computed from."""
    found = {name for name, _ in block.analyses}
    found |= {block.analysis} if block.analysis else set()
    found |= {block.nested.analysis} if block.nested else set()
    found |= {item.analysis for item in block.shown}
    found |= {part.analysis for part in block.parts if block.kind == "header" and part.analysis}
    cells = [*block.extra, *(block.nested.extra if block.nested else ()),
             *(cell for row in block.statistics for cell in row.extra)]
    found |= {part.analysis for cell in cells for part in cell.parts if part.analysis}
    return found


def _repeated_problems(layout: Layout) -> list[str]:
    """An analysis stands in one block of the body of a layout (the review of real-3a, F3:
    the same rows twice would show its results twice, and the comparison would not see it).
    The count under a column header may be shown again in the body ("n")."""
    seen: dict[str, int] = {}
    found = []
    for number, block in enumerate(layout.blocks):
        if block.kind == "header":
            continue
        for name in sorted(block_analyses(block)):
            if name in seen and seen[name] != number:
                found.append(f"rows[{number}]: the analysis '{name}' stands in rows[{seen[name]}] "
                             "already; an analysis stands in one block")
            seen.setdefault(name, number)
    return found


def _part_problems(event: ars.Event, analysis: dict, part: Part, at: str) -> list[str]:
    """Why a part cannot show a result of the analysis: its operation, its pattern."""
    if event.operations.get(part.operation, (None,))[0] != analysis.get("methodId"):
        return [f"{at}: '{part.operation}' is not an operation of its method"]
    pattern = pattern_of(event, part)
    if pattern is None:
        return [f"{at}: neither the layout nor the ARS operation gives a pattern"]
    try:
        methods.pattern_mask(pattern)
    except methods.MethodError as error:
        return [f"{at}: {error}"]
    return []


def _statistics_problems(layout: Layout, event: ars.Event, block: Block, where: str,
                         known: set[str] | None) -> list[str]:
    """Why a statistics block does not fit its reporting event."""
    analysis = event.analyses.get(block.analysis or "")
    if analysis is None:
        return [f"{where}: the analysis '{block.analysis}' is not in the reporting event"]
    at = f"{where}, analysis '{block.analysis}'"
    found = []
    groupings = [(entry["groupingId"], bool(entry.get("resultsByGroup")))
                 for entry in event.groupings_of(analysis)]
    if groupings not in ([(layout.grouping, True)], [(layout.grouping, False)]):
        found.append(f"{at}: a statistics block shows an analysis whose only grouping is the "
                     f"column grouping {layout.grouping}, by group or compared")
    elif not groupings[0][1] and (block.columns is None or len(block.columns) != 1):
        found.append(f"{at}: the analysis compares the column grouping, so its one result per "
                     "operation stands in one column: 'columns' lists one group")
    allowed = known if known is not None else (
        set(layout.values) if layout.values is not None else None)
    if block.columns is not None and allowed is not None:
        found += [f"{at}: columns: '{key}' is not a group of {layout.grouping}"
                  for key in block.columns if key not in allowed]
    extra = {name for name, _ in layout.extra}
    for row in block.statistics:
        for part in row.parts:
            found += _part_problems(event, analysis, part,
                                    f"{at}, row '{row.label}', part '{part.name}'")
        for cell in row.extra:
            here = f"{at}, row '{row.label}', extra '{cell.column}'"
            if cell.column not in extra:
                found.append(f"{here}: not an extra column of the layout")
            for part in cell.parts:
                other = event.analyses.get(part.analysis or "")
                if other is None:
                    found.append(f"{here}, part '{part.name}': the analysis '{part.analysis}' "
                                 "is not in the reporting event")
                    continue
                compared = [(entry["groupingId"], bool(entry.get("resultsByGroup")))
                            for entry in event.groupings_of(other)]
                if compared != [(layout.grouping, False)]:
                    found.append(f"{here}, part '{part.name}': an extra cell shows an analysis "
                                 f"that compares the column grouping {layout.grouping} alone")
                found += _part_problems(event, other, part, f"{here}, part '{part.name}'")
    return found


def _groups_problems(layout: Layout, event: ars.Event, block: Block, where: str) -> list[str]:
    """Why a groups block does not fit its reporting event."""
    analysis = event.analyses.get(block.analysis or "")
    if analysis is None:
        return [f"{where}: the analysis '{block.analysis}' is not in the reporting event"]
    at = f"{where}, analysis '{block.analysis}'"
    found = []
    rows = event.groupings.get(block.grouping or "")
    if rows is None or rows.get("dataDriven"):
        return [f"{at}: the row grouping '{block.grouping}' is not a grouping of the event with "
                "defined groups"]
    groupings = sorted((entry["groupingId"], bool(entry.get("resultsByGroup")))
                       for entry in event.groupings_of(analysis))
    if groupings != sorted([(layout.grouping, True), (block.grouping, True)]):
        found.append(f"{at}: a groups block shows an analysis split by the column grouping "
                     f"{layout.grouping} and the row grouping {block.grouping}, nothing else")
    known = {group["id"] for group in rows["groups"]}
    found += [f"{at}: labels: '{key}' is not a group of {block.grouping}"
              for key, _ in block.labels if key not in known]
    for part in block.parts:
        found += _part_problems(event, analysis, part, f"{at}, part '{part.name}'")
    found += _extra_problems(layout, event, block.extra, at, [
        (layout.grouping, False), (block.grouping or "", False)])
    return found


def _extra_problems(layout: Layout, event: ars.Event, cells: tuple[ExtraCell, ...], at: str,
                    groupings: list[tuple[str, bool]]) -> list[str]:
    """Why the extra cells of a block do not fit: their columns, and the groupings of their
    analyses, which must be `groupings` (in any order)."""
    found = []
    extra = {name for name, _ in layout.extra}
    for cell in cells:
        here = f"{at}, extra '{cell.column}'"
        if cell.column not in extra:
            found.append(f"{here}: not an extra column of the layout")
        for part in cell.parts:
            other = event.analyses.get(part.analysis or "")
            if other is None:
                found.append(f"{here}, part '{part.name}': the analysis '{part.analysis}' is "
                             "not in the reporting event")
                continue
            has = sorted((entry["groupingId"], bool(entry.get("resultsByGroup")))
                         for entry in event.groupings_of(other))
            if has != sorted(groupings):
                found.append(f"{here}, part '{part.name}': the analysis '{part.analysis}' must "
                             "have the groupings " + ", ".join(
                                 f"{name} ({'by group' if split else 'compared'})"
                                 for name, split in groupings))
            found += _part_problems(event, other, part, f"{here}, part '{part.name}'")
    return found


def _by_groups_problems(layout: Layout, event: ars.Event, block: Block,
                        where: str) -> list[str]:
    """Why a by_groups block does not fit its reporting event (real-3)."""
    found = []
    groups: set[str] = set()
    for name in block.by:
        grouping = event.groupings.get(name)
        if grouping is None or grouping.get("dataDriven") or name == layout.grouping:
            found.append(f"{where}: the row grouping '{name}' is not a grouping of the event "
                         "with defined groups other than the column grouping")
            continue
        groups |= {group["id"] for group in grouping["groups"]}
    if found:
        return found
    found += [f"{where}: labels: '{key}' is not a group of {' or '.join(block.by)}"
              for key, _ in block.labels if key not in groups]
    wanted = sorted([(layout.grouping, True), *((name, True) for name in block.by)])
    methods_of = set()
    for item in block.shown:
        at = f"{where}, analysis '{item.analysis}'"
        analysis = event.analyses.get(item.analysis)
        if analysis is None:
            found.append(f"{at}: not in the reporting event")
            continue
        methods_of.add(analysis.get("methodId"))
        has = sorted((entry["groupingId"], bool(entry.get("resultsByGroup")))
                     for entry in event.groupings_of(analysis))
        if has != wanted:
            found.append(f"{at}: a by_groups block shows an analysis split by the column "
                         f"grouping {layout.grouping} and the row groupings "
                         f"{', '.join(block.by)}, nothing else")
        found += [f"{at}: skip: '{key}' is not a group of {' or '.join(block.by)}"
                  for key in item.skip if key not in groups]
        for row in block.statistics:
            for part in row.parts:
                found += _part_problems(event, analysis, part,
                                        f"{at}, row '{row.label}', part '{part.name}'")
    if len(methods_of) > 1:
        found.append(f"{where}: its analyses have the methods {', '.join(sorted(methods_of))}; "
                     "the rows name the operations of one")
    return found


def _terms_problems(layout: Layout, event: ars.Event, block: Block, where: str) -> list[str]:
    """Why a terms block does not fit its reporting event (issue #31)."""
    analysis = event.analyses.get(block.analysis or "")
    if analysis is None:
        return [f"{where}: the analysis '{block.analysis}' is not in the reporting event"]
    at = f"{where}, analysis '{block.analysis}'"
    found = []
    levels = [block.grouping or ""] + ([block.nested.grouping] if block.nested else [])
    for name in levels:
        grouping = event.groupings.get(name)
        if grouping is None or not grouping.get("dataDriven"):
            found.append(f"{at}: the row grouping '{name}' is not a data-driven grouping of "
                         "the event")
    if found:
        return found
    wanted = [(layout.grouping, True), (block.grouping, True)]
    has = sorted((entry["groupingId"], bool(entry.get("resultsByGroup")))
                 for entry in event.groupings_of(analysis))
    if has != sorted(wanted):
        found.append(f"{at}: a terms block shows an analysis split by the column grouping "
                     f"{layout.grouping} and the row grouping {block.grouping}, nothing else")
    for part in block.parts:
        found += _part_problems(event, analysis, part, f"{at}, part '{part.name}'")
    found += _extra_problems(layout, event, block.extra, at,
                             [(layout.grouping, False), (block.grouping or "", True)])
    if block.nested is None:
        return found
    inner = event.analyses.get(block.nested.analysis)
    here = f"{where}, nested analysis '{block.nested.analysis}'"
    if inner is None:
        return [*found, f"{here}: not in the reporting event"]
    if inner.get("methodId") != analysis.get("methodId"):
        found.append(f"{here}: its rows take the parts of the block, so it has the block's "
                     "method")
    has = sorted((entry["groupingId"], bool(entry.get("resultsByGroup")))
                 for entry in event.groupings_of(inner))
    if has != sorted([*wanted, (block.nested.grouping, True)]):
        found.append(f"{here}: split by the column grouping and both row groupings, nothing "
                     "else")
    found += _extra_problems(layout, event, block.nested.extra, here, [
        (layout.grouping, False), (block.grouping or "", True), (block.nested.grouping, True)])
    return found
