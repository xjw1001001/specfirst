"""Grid to HTML (PLAN.md sections 7.1 and 7.4): a projection of the grid.

A renderer never computes a number. It writes the texts of the grid into a
page, and `projection_problems` reads the page back and holds every text
against the grid, and where it stands: every row of the table header, body
and footer in its place, with its elements in the order of the columns
(the review of real-3a, F6). The page is one file without scripts, without
anything fetched from elsewhere and without a date, so the same grid gives
the same bytes (rule R4); the check refuses a handler (an attribute `on...`),
a style sheet that is not the renderer's, a `meta` other than the character
set, a comment and text outside the body but the title.

Rows of the section `@header` (specfirst.machine.layout.HEADER_SECTION) are
shown in the table header, under the column labels. The label of the first
of them is the header of the row labels. Blanks in a cell are kept: a
pattern pads with them. A section of the body is shown as a heading line
above its rows, held against the grid like every other text (real-5a); a
row without a section after a section gets an empty separator line.
"""

from __future__ import annotations

import re
from html import escape
from html.parser import HTMLParser
from itertools import groupby

from specfirst.machine.layout import HEADER_SECTION

_STYLE = """
body { font-family: Georgia, serif; margin: 2em; color: #111; }
table.grid { border-collapse: collapse; }
table.grid caption { caption-side: top; text-align: center; padding-bottom: 0.6em; }
table.grid caption div { font-weight: bold; }
table.grid thead tr:first-child th { border-top: 2px solid #111; }
table.grid thead tr:last-child th, table.grid thead tr:last-child td {
  border-bottom: 1px solid #111; }
table.grid tbody tr:last-child th, table.grid tbody tr:last-child td {
  border-bottom: 2px solid #111; }
table.grid th, table.grid td { padding: 0.15em 1.2em; vertical-align: top; }
table.grid th.stub { text-align: left; font-weight: normal; }
table.grid th.column, table.grid th.spanner { text-align: center; font-weight: bold; }
table.grid td { text-align: center; white-space: pre; font-family: "Courier New", monospace; }
table.grid tfoot td { text-align: left; white-space: normal; font-family: Georgia, serif;
  font-size: 0.9em; padding-top: 0.3em; }
""".strip()


def _stub(row: dict | None) -> str:
    if row is None:
        return '<th class="stub"></th>'
    indent = int(row.get("indent", 0))
    style = f' style="padding-left: {1.2 + 1.5 * indent:.1f}em"' if indent else ""
    return f'<th class="stub" scope="row" data-label="{escape(row["id"])}"{style}>' \
           f'{escape(row["label"])}</th>'


def _row(row: dict) -> str:
    cells = "".join(f'<td data-cell="{escape(cell["id"])}">{escape(cell["text"])}</td>'
                    for cell in row["cells"])
    return f'<tr data-row="{escape(row["id"])}">{_stub(row)}{cells}</tr>'


def _sections(body: list[dict]) -> list[tuple[str, object]]:
    """The lines of the body: ("heading", name), ("separator", None) or ("row", row).

    A row whose section differs from the row before it starts that section:
    with a name, a heading line shows the name; without one (a row after a
    section), an empty separator stands before it.
    """
    found: list[tuple[str, object]] = []
    current: str | None = None
    for row in body:
        if row.get("section") != current:
            current = row.get("section")
            found.append(("heading", current) if current is not None else ("separator", None))
        found.append(("row", row))
    return found


def section_headings(grid: dict) -> dict[str, str]:
    """The heading lines a page shows, by their number (data-section): the section's name."""
    body = [row for row in grid["rows"] if row.get("section") != HEADER_SECTION]
    headings = [name for kind, name in _sections(body) if kind == "heading"]
    return {str(number): str(name) for number, name in enumerate(headings, start=1)}


def html(grid: dict) -> str:
    """One page that shows the grid."""
    columns = grid["columns"]
    head = [row for row in grid["rows"] if row.get("section") == HEADER_SECTION]
    body = [row for row in grid["rows"] if row.get("section") != HEADER_SECTION]
    lines = ["<!DOCTYPE html>", '<html lang="en">', "<head>", '<meta charset="utf-8">',
             f"<title>{escape(grid['output_id'])}</title>", f"<style>\n{_STYLE}\n</style>",
             "</head>", "<body>",
             f'<table class="grid" data-output="{escape(grid["output_id"])}">']
    if grid["titles"]:
        lines.append("<caption>" + "".join(f'<div data-title="{number}">{escape(text)}</div>'
                                           for number, text in enumerate(grid["titles"], 1))
                     + "</caption>")
    lines.append("<thead>")
    if any(column.get("spanner") for column in columns):
        spans = "".join(
            f'<th class="spanner" colspan="{len(list(group))}">{escape(name or "")}</th>'
            for name, group in groupby(columns, key=lambda column: column.get("spanner")))
        lines.append(f'<tr><th class="stub"></th>{spans}</tr>')
    labels = "".join(f'<th class="column" scope="col" data-column="{escape(column["id"])}">'
                     f'{escape(column["label"])}</th>' for column in columns)
    lines.append(f'<tr><th class="stub"></th>{labels}</tr>')
    lines += [_row(row) for row in head]
    lines.append("</thead>")
    lines.append("<tbody>")
    headings = 0
    for kind, item in _sections(body):
        if kind == "heading":  # the section's name, above its rows
            headings += 1
            lines.append(f'<tr class="section"><th class="stub" colspan="{len(columns) + 1}" '
                         f'data-section="{headings}">{escape(str(item))}</th></tr>')
        elif kind == "separator":  # the rows after it have no section
            lines.append('<tr class="section"></tr>')
        else:
            lines.append(_row(item))
    lines.append("</tbody>")
    if grid["footnotes"]:
        lines.append("<tfoot>")
        lines += [f'<tr><td colspan="{len(columns) + 1}" data-footnote="{number}">'
                  f'{escape(text)}</td></tr>'
                  for number, text in enumerate(grid["footnotes"], 1)]
        lines.append("</tfoot>")
    lines += ["</table>", "</body>", "</html>"]
    return "\n".join(lines) + "\n"


# What a page fetches or draws from elsewhere: elements, and attributes on any element.
_FETCHING = {"script", "link", "img", "iframe", "frame", "object", "embed", "video", "audio",
             "source", "track", "svg", "image", "use", "base", "form", "input", "picture"}
_FETCHING_ATTRIBUTES = {"src", "href", "srcset", "background", "poster", "xlink:href", "data",
                        "action", "formaction", "lowsrc", "dynsrc", "ping"}
# The one style attribute the renderer writes: the indent of a row label.
_INDENT = re.compile(r"padding-left: \d+\.\dem")


class _Reader(HTMLParser):
    """Collects the texts of a page made by `html`, by what each one is, and where each
    stands: the rows of the table header, body and footer in order, each with the elements
    of its row in order (the review of real-3a, F6)."""

    _KINDS = ("data-cell", "data-label", "data-column", "data-title", "data-footnote",
              "data-section")

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.found: dict[tuple[str, str], str] = {}
        self.outside: list[str] = []  # text in the body that belongs to no element of the grid
        self._open: tuple[str, str] | None = None
        self._depth = 0
        self._in_body = False
        self.external: list[str] = []
        self.unsafe: list[str] = []  # what a page that loads and runs nothing must not hold
        self.rows: list[tuple[str, tuple]] = []  # (thead, tbody or tfoot; its elements in order)
        self.spans: list[tuple[str, str]] = []  # the spanners: (colspan, text)
        self.title = ""
        self.style = ""
        self._part = ""
        self._row: list | None = None
        self._in = ""  # "title", "style", "spanner" or ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        given = dict(attrs)
        if tag == "body":
            self._in_body = True
        if tag in _FETCHING or set(given) & _FETCHING_ATTRIBUTES:
            self.external.append(tag)
        # Handlers, attributes that hide, and any style but the indent of a row label (the
        # review of real-3a, F6; of real-3, F3).
        self.unsafe += [f"the attribute '{name}' of <{tag}>" for name, value in attrs
                        if name.lower().startswith("on") or name.lower() == "hidden"
                        or name.lower() == "style" and not _INDENT.fullmatch(str(value))]
        if tag == "meta" and set(given) != {"charset"}:
            self.unsafe.append("a <meta> other than the character set")
        if tag in ("thead", "tbody", "tfoot"):
            self._part = tag
        elif tag == "tr":
            self._row = []
        elif tag in ("title", "style"):
            self._in = tag
        elif tag == "th" and "spanner" in str(given.get("class") or "").split():
            self.spans.append((str(given.get("colspan")), ""))
            self._in = "spanner"
        if self._row is not None:
            self._row += [(kind, str(given[kind])) for kind in self._KINDS if kind in given]
        for kind in self._KINDS:
            if kind in given:
                self._open, self._depth = (kind, str(given[kind])), 0
                self.found[self._open] = ""
                return
        if self._open:
            self._depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "tr" and self._row is not None:
            self.rows.append((self._part, tuple(self._row)))
            self._row = None
        elif tag in ("thead", "tbody", "tfoot"):
            self._part = ""
        elif tag in ("title", "style", "th"):
            self._in = ""
        if self._open:
            if self._depth == 0:
                self._open = None
            else:
                self._depth -= 1

    def handle_data(self, data: str) -> None:
        if self._in == "title":
            self.title += data
        elif self._in == "style":
            self.style += data
        elif self._in == "spanner":
            self.spans[-1] = (self.spans[-1][0], self.spans[-1][1] + data)
        if self._open:
            self.found[self._open] += data
        elif self._in_body and data.strip() and self._in != "spanner":
            self.outside.append(data.strip())
        elif not self._in_body and data.strip() and self._in not in ("title", "style"):
            self.unsafe.append(f"text outside the body: {data.strip()[:40]!r}")

    def handle_comment(self, data: str) -> None:
        self.unsafe.append("a comment")

    def handle_decl(self, decl: str) -> None:
        if decl != "DOCTYPE html":
            self.unsafe.append(f"the declaration {decl!r}")

    def handle_pi(self, data: str) -> None:
        self.unsafe.append("a processing instruction")


def _layout(grid: dict) -> list[tuple[str, tuple]]:
    """Where `html` places the elements of the grid: the rows of the table header, body and
    footer in order, each with the data attributes of its elements in order."""
    columns = grid["columns"]
    head = [row for row in grid["rows"] if row.get("section") == HEADER_SECTION]
    body = [row for row in grid["rows"] if row.get("section") != HEADER_SECTION]

    def row(record: dict) -> tuple:
        return (("data-label", record["id"]),
                *(("data-cell", cell["id"]) for cell in record["cells"]))

    placed: list[tuple[str, tuple]] = []
    if any(column.get("spanner") for column in columns):
        placed.append(("thead", ()))
    placed.append(("thead", tuple(("data-column", column["id"]) for column in columns)))
    placed += [("thead", row(record)) for record in head]
    headings = 0
    for kind, item in _sections(body):
        if kind == "heading":
            headings += 1
            placed.append(("tbody", (("data-section", str(headings)),)))
        elif kind == "separator":
            placed.append(("tbody", ()))
        else:
            placed.append(("tbody", row(item)))
    placed += [("tfoot", (("data-footnote", str(number)),))
               for number in range(1, len(grid["footnotes"]) + 1)]
    return placed


def _spanners(grid: dict) -> list[tuple[str, str]]:
    return [(str(len(list(group))), name or "") for name, group in
            groupby(grid["columns"], key=lambda column: column.get("spanner"))] \
        if any(column.get("spanner") for column in grid["columns"]) else []


def projection_problems(grid: dict, page: str) -> list[str]:
    """Why a page is not a projection of the grid: every text of the grid, and no other."""
    reader = _Reader()
    reader.feed(page)
    reader.close()
    wanted: dict[tuple[str, str], str] = {}
    for number, text in enumerate(grid["titles"], 1):
        wanted[("data-title", str(number))] = text
    for number, text in enumerate(grid["footnotes"], 1):
        wanted[("data-footnote", str(number))] = text
    for column in grid["columns"]:
        wanted[("data-column", column["id"])] = column["label"]
    for number, name in section_headings(grid).items():
        wanted[("data-section", number)] = name
    for row in grid["rows"]:
        wanted[("data-label", row["id"])] = row["label"]
        for cell in row["cells"]:
            wanted[("data-cell", cell["id"])] = cell["text"]
    problems = [f"{kind[5:]} {key}: the page has {reader.found.get((kind, key))!r}, the grid "
                f"{text!r}" for (kind, key), text in wanted.items()
                if reader.found.get((kind, key)) != text]
    problems += [f"{kind[5:]} {key}: on the page, not in the grid"
                 for kind, key in reader.found if (kind, key) not in wanted]
    problems += [f"text on the page that is not of the grid: {text!r}" for text in reader.outside]
    problems += [f"the page refers to something outside itself: <{tag}>"
                 for tag in reader.external]
    # Where each text stands (the review of real-3a, F6): two cells or two rows exchanged
    # together with their attributes, or the header row in the body, show a value under
    # another column or label.
    wanted_places = _layout(grid)
    if reader.rows != wanted_places:
        place = next((number for number, (ours, theirs) in enumerate(
            zip(reader.rows, wanted_places, strict=False), start=1) if ours != theirs),
            min(len(reader.rows), len(wanted_places)) + 1)
        problems.append(f"the rows of the page are not those of the grid in their places: the "
                        f"first that differs is row {place} of the table")
    if reader.spans != _spanners(grid):
        problems.append(f"the spanners of the page are {reader.spans}, the grid's "
                        f"{_spanners(grid)}")
    if reader.title != grid["output_id"]:
        problems.append(f"the title of the page is {reader.title!r}, not the output's ID")
    if reader.style.strip() != _STYLE:
        problems.append("the style sheet of the page is not the renderer's")
    problems += [f"the page holds {item}" for item in reader.unsafe]
    return problems
