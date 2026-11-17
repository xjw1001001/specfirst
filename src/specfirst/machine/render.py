"""Grid to HTML (PLAN.md sections 7.1 and 7.4): a projection of the grid.

A renderer never computes a number. It writes the texts of the grid into a
page, and `projection_problems` reads the page back and holds every text
against the grid. The page is one file without scripts, without anything
fetched from elsewhere and without a date, so the same grid gives the same
bytes (rule R4).

Rows of the section `@header` (specfirst.machine.layout.HEADER_SECTION) are
shown in the table header, under the column labels. The label of the first
of them is the header of the row labels. Blanks in a cell are kept: a
pattern pads with them.
"""

from __future__ import annotations

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
    section = None
    lines.append("<tbody>")
    for row in body:
        if row.get("section") != section:
            section = row.get("section")
            lines.append(f'<tr class="section" data-section="{escape(section or "")}"></tr>')
        lines.append(_row(row))
    lines.append("</tbody>")
    if grid["footnotes"]:
        lines.append("<tfoot>")
        lines += [f'<tr><td colspan="{len(columns) + 1}" data-footnote="{number}">'
                  f'{escape(text)}</td></tr>'
                  for number, text in enumerate(grid["footnotes"], 1)]
        lines.append("</tfoot>")
    lines += ["</table>", "</body>", "</html>"]
    return "\n".join(lines) + "\n"


class _Reader(HTMLParser):
    """Collects the texts of a page made by `html`, by what each one is."""

    _KINDS = ("data-cell", "data-label", "data-column", "data-title", "data-footnote")

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.found: dict[tuple[str, str], str] = {}
        self.outside: list[str] = []  # text in the body that belongs to no element of the grid
        self._open: tuple[str, str] | None = None
        self._depth = 0
        self._in_body = False
        self.external: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        given = dict(attrs)
        if tag == "body":
            self._in_body = True
        if tag in ("script", "link", "img", "iframe", "object", "embed") or "src" in given \
                or "href" in given:
            self.external.append(tag)
        for kind in self._KINDS:
            if kind in given:
                self._open, self._depth = (kind, str(given[kind])), 0
                self.found[self._open] = ""
                return
        if self._open:
            self._depth += 1

    def handle_endtag(self, tag: str) -> None:
        if self._open:
            if self._depth == 0:
                self._open = None
            else:
                self._depth -= 1

    def handle_data(self, data: str) -> None:
        if self._open:
            self.found[self._open] += data
        elif self._in_body and data.strip():
            self.outside.append(data.strip())


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
    for row in grid["rows"]:
        wanted[("data-label", row["id"])] = row["label"]
        for cell in row["cells"]:
            wanted[("data-cell", cell["id"])] = cell["text"]
    problems = [f"{kind[5:]} {key}: the page has {reader.found.get((kind, key))!r}, the grid "
                f"{text!r}" for (kind, key), text in wanted.items()
                if reader.found.get((kind, key)) != text]
    problems += [f"{kind[5:]} {key}: on the page, not in the grid"
                 for kind, key in reader.found if (kind, key) not in wanted]
    spanners = {column.get("spanner") for column in grid["columns"]} - {None}
    problems += [f"text on the page that is not of the grid: {text!r}"
                 for text in reader.outside if text not in spanners]
    problems += [f"the page refers to something outside itself: <{tag}>"
                 for tag in reader.external]
    return problems
