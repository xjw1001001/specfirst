"""A mock shell against the example's table shell (the review of real-3a, F1).

CDISC's ARS example keeps a table shell next to some of its outputs: a PDF
that shows the rows, the columns and the mask of every cell, before data
exist. The kit pins it (`shell` of an output in kit.yaml), and the mock
shell of the build (specfirst.machine.grid.shell) is held against its text,
which poppler's pdftotext writes with -layout (lesson 3), as the CSR parser
reads a CSR page (specfirst.machine.csr). Nothing of it is kept in git.

A line of the shell's text is cut where two or more blanks stand. A piece
that is a mask ("XX", "XX ( XX.X)", "(N=XX)", "XX.X, XX.X") is a cell; the
pieces before the first cell are the label. So a line is a row with cells,
a line of the header (every cell is a count of a column, "(N=...)"), or a
text: a title, a column label, a heading, a footnote. A text with `<...>`
in it is a placeholder: "<Visit n>" stands for any visit, and `...` for
rows that repeat.

What the check holds, for every row of the mock shell:

- a row of the table header: its masks, in order, are those of a header
  line of the shell;
- a row of the body with cells: its label and its masks (the cells that are
  not empty, in the order of the columns) are those of a row of the shell,
  and the rows of one run (rows with cells, one after the other) stand in
  the shell in the same order, one after the other;
- a row without cells, and the name of a section: a text of the shell, or
  a placeholder that fits it;

and every row of the shell with cells is the row of some row of the mock
shell, and every heading of the shell in its own words (a text in one
piece, without a placeholder, between the header and the last row with
cells, such as "Number of subjects with at least one event") is a section
or a row without cells of the mock shell. Masks are compared without their
case: the mock shell writes "xx.x", a shell "XX.X".

Which column a cell stands in is held where the shell's rows with the most
cells have one cell per column of the grid: pdftotext keeps the place of a
text on its line, so the middles of their cells say where the columns
stand, and a cell of a row with empty cells belongs to the nearest.

What it does not hold: the titles, the footnotes and the header of the row
labels (a shell writes them with placeholders and in its own words; ADR-003
lists the differences), the labels of the columns (pdftotext breaks them
over lines) and the indent of a row.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from specfirst.machine.layout import HEADER_SECTION

_PIECES = re.compile(r"\S(?:\S| (?! ))*")  # a run of text without two blanks in a row
_MASK = re.compile(r"X+(?:\.X+)?")
_AROUND = set("()[]{} ,;:=N%-+/")  # what may stand around the masks of a cell
_PLACEHOLDER = re.compile(r"<[^<>]*>")


class ShellError(ValueError):
    """The shell cannot be read."""


@dataclass(frozen=True)
class Line:
    number: int  # in the text of the shell, from 1
    label: str  # the text before the first cell, its pieces joined by one blank
    masks: tuple[str, ...]  # the cells, upper case
    pieces: int = 1  # how many pieces the line has: a text in one piece may be a heading
    centres: tuple[float, ...] = ()  # where each cell stands on the line: its middle

    @property
    def header(self) -> bool:
        return bool(self.masks) and all(mask.startswith("(N=") for mask in self.masks)


def is_mask(piece: str) -> bool:
    """A piece of a line that is the mask of a cell: masks of X and what stands around them."""
    rest = _MASK.sub("", piece)
    return rest != piece and set(rest) <= _AROUND and "N" not in rest.replace("(N=", "")


def lines(text: str) -> list[Line]:
    """The lines of a shell's text that hold something, each cut into a label and cells."""
    found = []
    for number, raw in enumerate(text.splitlines(), start=1):
        spans = [(match.group(), match.start(), match.end())
                 for match in _PIECES.finditer(raw)]
        pieces = [piece for piece, _, _ in spans]
        if not pieces:
            continue
        first = next((n for n, piece in enumerate(pieces) if is_mask(piece)), len(pieces))
        found.append(Line(number, " ".join(" ".join(pieces[:first]).split()),
                          tuple(" ".join(piece.split()).upper() for piece in pieces[first:]),
                          len(pieces),
                          tuple((start + end) / 2 for _, start, end in spans[first:])))
    return found


def read(pdf: Path) -> list[Line]:
    """The lines of a shell, from its text as poppler's pdftotext writes it."""
    from specfirst.machine import csr

    try:
        return lines(csr.page_text(pdf, None))
    except csr.CsrError as error:
        raise ShellError(f"{pdf.name}: {error}") from error


def _fits(text: str, line: Line) -> bool:
    """Whether a heading of ours is a text of the shell, or fits its placeholder."""
    wanted = " ".join(text.split())
    if line.masks or not line.label:
        return False
    if _PLACEHOLDER.search(line.label) is None:
        return wanted == line.label
    pattern = ".+".join(re.escape(" ".join(part.split()))
                        for part in _PLACEHOLDER.split(line.label))
    pattern = pattern.replace(re.escape(" "), " ?")
    return re.fullmatch(pattern, wanted) is not None


def _masks(row: dict) -> tuple[str, ...]:
    return tuple(" ".join(cell["text"].split()).upper() for cell in row["cells"] if cell["text"])


@dataclass
class Held:
    rows: int = 0  # rows of the mock shell held against the shell
    lines: int = 0  # rows of the shell with cells
    problems: list[str] | None = None


def compare(shell: dict, found: list[Line]) -> Held:
    """Hold a mock shell (a grid without results) against the lines of a table shell."""
    held = Held(problems=[])
    rows_of_shell = [line for line in found if line.masks and not line.header]
    headers = [line for line in found if line.header]
    texts = [line for line in found if not line.masks]
    used: set[int] = set()
    run: list[int] = []  # the shell lines of the current run of rows with cells
    section = None
    by_number = {line.number: line for line in rows_of_shell}
    # Where the columns stand: the middle of each cell of the shell's rows with the most
    # cells, when they have as many cells as the grid has columns (pdftotext keeps the
    # place of a text on its line). A row with empty cells is then held column by column.
    full = max((len(line.masks) for line in rows_of_shell), default=0)
    centres = [sum(line.centres[i] for line in rows_of_shell if len(line.masks) == full)
               / sum(1 for line in rows_of_shell if len(line.masks) == full)
               for i in range(full)] if full == len(shell["columns"]) else []

    def columns_of(line: Line) -> list[int]:
        return [min(range(len(centres)), key=lambda i: abs(centres[i] - middle))
                for middle in line.centres]
    for row in shell["rows"]:
        masks = _masks(row)
        where = f"row {row['id']} ({row['label']!r})"
        if row.get("section") == HEADER_SECTION:
            held.rows += 1
            if not any(line.masks == masks for line in headers):
                held.problems.append(f"{where}: the header masks {list(masks)} are on no header "
                                     "line of the shell")
            continue
        if row.get("section") != section:
            section = row.get("section")
            if section is not None and not any(_fits(section, line) for line in texts):
                held.problems.append(f"section {section!r}: no text of the shell, and no "
                                     "placeholder, fits it")
        held.rows += 1
        if not masks:
            run = []
            if not any(_fits(row["label"], line) for line in texts):
                held.problems.append(f"{where}: a row without cells that no text of the shell, "
                                     "and no placeholder, fits")
            continue
        label = " ".join(row["label"].split())
        matches = [line.number for line in rows_of_shell
                   if line.label == label and line.masks == masks]
        if not matches:
            held.problems.append(f"{where}: no row of the shell has this label and the masks "
                                 f"{list(masks)}")
            run = []
            continue
        if run:
            following = [number for number in matches if number > run[-1]]
            if not following or [line.number for line in rows_of_shell
                                 if run[-1] < line.number < following[0]]:
                held.problems.append(f"{where}: in the shell it does not follow the row before "
                                     "it")
                run = [matches[0]]
                continue
            run.append(following[0])
        else:
            run = [matches[0]]
        used.update(matches)
        ours = [number for number, cell in enumerate(row["cells"]) if cell["text"]]
        if centres and ours != columns_of(by_number[run[-1]]):
            held.problems.append(f"{where}: its cells stand in the columns "
                                 f"{[number + 1 for number in ours]}; on line {run[-1]} of the "
                                 f"shell in {[n + 1 for n in columns_of(by_number[run[-1]])]}")
    held.lines = len(rows_of_shell)
    held.problems += [f"line {line.number} of the shell ({line.label!r}, {list(line.masks)}): no "
                      "row of the mock shell has it" for line in rows_of_shell
                      if line.number not in used]
    # A heading of the shell in its own words (one piece, no placeholder, between the header
    # and the last row with cells) is a section or a row without cells of the grid too.
    if headers and rows_of_shell:
        ours = {" ".join(name.split()) for row in shell["rows"]
                for name in (row.get("section") or "", row["label"] if not _masks(row) else "")
                if name and row.get("section") != HEADER_SECTION}
        held.problems += [
            f"line {line.number} of the shell ({line.label!r}): a heading no section and no row "
            "of the mock shell shows" for line in texts
            if headers[-1].number < line.number < rows_of_shell[-1].number and line.pieces == 1
            and _PLACEHOLDER.search(line.label) is None
            and any(character.isalnum() for character in line.label)  # not a rule or "..."
            and line.label not in ours]
    return held
