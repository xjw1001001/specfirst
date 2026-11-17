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

A cell template is text with `{name}` where the part of that name goes. A
part is one result: an ARS operation of the row's analysis (in a header
block the part names its analysis). Its pattern is a pattern of the
registry's display.pattern; when the layout gives none, the `resultPattern`
of the ARS operation is taken, and a part with neither is an error.

Version 0 has these two kinds of block. In both, an analysis has the
column grouping as its only grouping. The blocks the other table families
need (one row per group of a row grouping, statistics below each other,
columns that compare groups) are added by the rest of real-3, as kinds of
this list.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from string import Formatter

import yaml

from specfirst.machine import ars, methods

FORMAT = 0
KINDS = ("header", "analyses")
# The section of a grid row that is shown in the table header (ADR-003, decision 4).
HEADER_SECTION = "@header"
_KEYS = {"layout", "output", "titles", "footnotes", "missing", "columns", "rows"}
_COLUMN_KEYS = {"grouping", "values", "labels"}
_BLOCK_KEYS = {"header": {"kind", "label", "cell", "parts"},
               "analyses": {"kind", "section", "indent", "cell", "parts", "analyses"}}
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
class Block:
    kind: str
    cell: str  # the template
    parts: tuple[Part, ...]  # in the order the template names them
    label: str | None = None  # header
    section: str | None = None  # analyses
    indent: int = 0
    analyses: tuple[tuple[str, str | None], ...] = ()  # (analysis ID, label or None)


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


def _block(data: object, where: str, problems: list[str]) -> Block | None:
    if not isinstance(data, dict) or data.get("kind") not in KINDS:
        problems.append(f"{where}: needs a 'kind' out of {', '.join(KINDS)}")
        return None
    kind = data["kind"]
    problems += [f"{where}: unknown key '{key}'" for key in sorted(set(data) - _BLOCK_KEYS[kind])]
    template, given = data.get("cell"), data.get("parts")
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
    missing = data.get("missing", "")
    if not isinstance(missing, str):
        problems.append("'missing' must be text")
        missing = ""
    rows = data.get("rows")
    if not isinstance(rows, list) or not rows:
        problems.append("'rows' must list at least one block")
        rows = []
    blocks = [_block(item, f"rows[{number}]", problems) for number, item in enumerate(rows)]
    titles = _texts(data.get("titles"), "titles", problems)
    footnotes = _texts(data.get("footnotes"), "footnotes", problems)
    if problems:
        raise LayoutError(f"{where}: " + "; ".join(problems))
    return Layout(output=output, grouping=columns["grouping"],
                  blocks=tuple(block for block in blocks if block is not None), values=values,
                  labels=tuple(sorted(labels.items())), titles=titles, footnotes=footnotes,
                  missing=missing)


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
    for number, block in enumerate(layout.blocks):
        where = f"rows[{number}]"
        rows = block.analyses or ((None, None),)
        for analysis_id, _ in rows:
            for part in block.parts:
                name = part.analysis or analysis_id
                at = f"{where}, part '{part.name}'"
                analysis = event.analyses.get(name)
                if analysis is None:
                    found.append(f"{at}: the analysis '{name}' is not in the reporting event")
                    continue
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
    return sorted(set(found))
