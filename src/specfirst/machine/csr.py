"""Reference grids from the tables of a CSR, and P2 for a grid against one.

PLAN.md sections 4.8 and 13.3, ADR-012 (decision 3) and ADR-015. A table of
the clinical study report is a reference: what the study really printed. Its
page is turned into text by poppler's pdftotext with -layout, as evidence
E24 and E25 did, and that text is parsed into a reference grid: the titles,
the column labels with the count under each, and the lines of the body,
each a label with one cell per column (a line without cells is a section
heading). Footnotes are kept as lines of text. Since real-5b a page may have
a column without a count to the right of the counted ones (CSR Table 14-3.13:
"p-value [1]"), a text left of the counts on their line (the header of the
row labels, "Assessment"), and a line with two labels, the section heading
and the row label ("Week 8" and "n"), read as a heading line and a row.

CSR content is CDISC material (rule 4 of section 2.1). A reference grid is
written into an ignored folder of the checkout (build/csr/<kit>/), never
into the fetch cache, whose check fails on any added file, and never into
git. It is parsed again from the pinned PDF on every run of the check.

The comparison (`compare`) holds a built grid against a reference grid:

- the column labels and the counts under them (the cells of the header row);
- the lines of the body in their order: a section heading of the grid (its
  rows' `section`) against a line without cells, a row against a line with
  cells. Labels are compared without their blanks: pdftotext writes the
  label "p-value(Xan High - Xan Low)[1][3]" of one page with a blank before
  "[1]" and that of another without;
- every cell: its text without blanks, against the reference cell the same
  way. Blanks carry no number: a pattern pads with them, pdftotext places
  them, and SAP template 5 writes "xx.x(x.xx)" where the CSR prints
  "-0.5 (0.82)". An empty cell of the grid stands for no text there.

A cell whose text differs is a difference. Section 4.8 asks for exactly one
class and a proof per difference: the `cells` section of the kit's
exceptions file (`load_exceptions`), one entry per cell, checked by `judge`.
Two proof kinds, both for the class `rule_choice` (section 4.8: a build with
the other alternative, in which the cell equals the reference).
`other_pattern`: the cell's own results, shown by other patterns, give the
CSR's text. It is the first real case of a difference of display (ADR-003,
decision 5): SAP template 5 shows the limits of a confidence interval with 2
decimals, the CSR with 1 (ADR-015). `other_build` (real-5b): the cell built
again with any of the results of other analyses of the same event (an
analysis that follows the other alternative of the decision; its ARD rows
are those of the cell with the analysis's ID replaced), other patterns,
another cell template and other options of display.pattern gives the CSR's
text. The titles are compared like labels. The footnotes
are not compared: the layouts state the methods in words of their own, and
the CSR's footnotes are not copied into git.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from specfirst.machine.layout import HEADER_SECTION

FORMAT = 0
_COUNT = re.compile(r"\(N=\s*\d+\)")
_TOKEN = re.compile(r"\S+(?: \S+)*")  # words joined by single blanks
# A footnote, or a note in the place of footnotes (CSR Table 14-3.11).
_FOOTNOTE = re.compile(r"^(\[\d+\]|Note:)")


class CsrError(ValueError):
    """The page cannot be read as a table."""


def page_text(pdf: Path, page: int) -> str:
    """One page of a PDF as text, by poppler's pdftotext with -layout (lesson 3)."""
    if shutil.which("pdftotext") is None:
        raise CsrError("pdftotext is not installed; it comes with poppler")
    done = subprocess.run(["pdftotext", "-layout", "-f", str(page), "-l", str(page), str(pdf),
                           "-"], capture_output=True, text=True, encoding="utf-8",
                          errors="replace")
    if done.returncode != 0:
        raise CsrError(f"pdftotext exited {done.returncode}: {done.stderr.strip()}")
    return done.stdout


def _tokens(line: str) -> list[tuple[int, int, str]]:
    """The texts of a line that stand apart by two blanks or more, with their place."""
    return [(match.start(), match.end(), match.group()) for match in _TOKEN.finditer(line)]


def _nearest(centres: list[float], start: int, end: int) -> int:
    middle = (start + end) / 2
    return min(range(len(centres)), key=lambda number: abs(centres[number] - middle))


def squeeze(text: str) -> str:
    """A text without blanks: how labels, titles and cells are compared."""
    return "".join(text.split())


def parse(text: str, table: str) -> dict:
    """The reference grid of the table `table` ("14-3.01") on a page of text."""
    lines = text.splitlines()
    heading = f"Table {table}"
    at = next((n for n, line in enumerate(lines) if line.strip() == heading), None)
    if at is None:
        raise CsrError(f"the page has no line '{heading}'")
    counts_at = next((n for n in range(at + 1, len(lines)) if _COUNT.search(lines[n])), None)
    if counts_at is None:
        raise CsrError(f"{heading}: no line with the counts of the columns, (N=...)")
    counts = [(match.start(), match.end(), match.group()) for match in
              _COUNT.finditer(lines[counts_at])]
    # The other texts of the line of counts: left of the counts, the header of the row
    # labels; right of them, a column without a count, the text its label ends with.
    first_count, last_count = counts[0][0], counts[-1][1]
    stub, extra = [], []
    for start, end, token in _tokens(lines[counts_at]):
        if _COUNT.fullmatch(token):
            continue
        if end <= first_count:
            stub.append(token)
        elif start >= last_count:
            extra.append((start, end, token))
        else:
            raise CsrError(f"{heading}: the line of counts has {token!r} between two counts")
    centres = [(start + end) / 2 for start, end, _ in counts + extra]
    # The titles: the table's own line and the lines under it, up to the first empty
    # line; the column labels: the lines from there to the counts.
    first_label = next((n for n in range(at + 1, counts_at) if not lines[n].strip()), counts_at)
    titles = [heading] + [" ".join(lines[n].split()) for n in range(at + 1, first_label)]
    labels: list[list[str]] = [[] for _ in centres]
    for n in range(first_label, counts_at):
        for start, end, token in _tokens(lines[n]):
            labels[_nearest(centres, start, end)].append(token)
    for number, (_, _, token) in enumerate(extra, start=len(counts)):
        labels[number].append(token)
    columns = [{"label": " ".join(parts), "count": count}
               for parts, count in zip(labels, [count for _, _, count in counts]
                                       + [None] * len(extra), strict=True)]
    body, footnotes = [], []
    margin = first_count - 4
    for n in range(counts_at + 1, len(lines)):
        line = lines[n]
        if not line.strip():
            continue
        if _FOOTNOTE.match(line.strip()) or line.strip().startswith("Source:") or footnotes:
            if line.strip().startswith("Source:"):
                break
            if _FOOTNOTE.match(line.strip()) or not footnotes:
                footnotes.append(" ".join(line.split()))
            else:
                footnotes[-1] += " " + " ".join(line.split())
            continue
        tokens = _tokens(line)
        cells: list[str | None] = [None] * len(centres)
        named = [token for start, _, token in tokens if start < margin]
        if not named:
            raise CsrError(f"{heading}, line {n + 1}: no row label: {line.strip()!r}")
        if len(named) > 2:
            raise CsrError(f"{heading}, line {n + 1}: more than two labels: {named}")
        if len(named) == 2:  # a section heading on the line of its first row
            body.append({"label": named[0], "cells": None})
        label = named[-1]
        for start, end, token in tokens[len(named):]:
            column = _nearest(centres, start, end)
            if cells[column] is not None:
                raise CsrError(f"{heading}, line {n + 1}: two texts in column {column + 1}")
            cells[column] = token
        # Indentation is not kept: pdftotext places labels a column or two apart.
        body.append({"label": label, "cells": None if all(
            cell is None for cell in cells) else cells})
    if not body:
        raise CsrError(f"{heading}: no line under the column labels")
    population = next((" ".join(line.split()[1:]) for line in lines[:at]
                       if line.strip().startswith("Population:")), None)
    return {"reference": FORMAT, "table": table, "titles": titles, "population": population,
            "stub": " ".join(stub) or None, "columns": columns, "lines": body,
            "footnotes": footnotes}


def read_table(pdf: Path, page: int, table: str) -> dict:
    """The reference grid of a table, parsed from its page of the PDF."""
    grid = parse(page_text(pdf, page), table)
    grid["page"] = page
    return grid


# ---- P2 for a grid against a reference grid --------------------------------------------


@dataclass
class Comparison:
    output: str
    table: str
    cells: int = 0  # cells of the grid compared, the header's included
    printed: int = 0  # of them, cells the reference prints a text in
    equal: int = 0  # cells whose text is the reference's
    differing: dict[str, tuple[str, str]] = field(default_factory=dict)  # cell -> (ours, theirs)
    classified: dict[str, str] = field(default_factory=dict)  # cell -> class, proof holds
    problems: list[str] = field(default_factory=list)

    def lines(self) -> list[str]:
        said = [f"grid {self.output} against CSR Table {self.table}: {self.cells} cells, "
                f"{self.printed} of them printed in the CSR; {self.equal} equal the CSR, "
                f"{len(self.differing)} differ, {len(self.classified)} of them with one class "
                "and a proof that holds"]
        said += [f"  {cell}: ours {ours!r}, CSR {theirs!r}"
                 + (f" ({self.classified[cell]})" if cell in self.classified else "")
                 for cell, (ours, theirs) in sorted(self.differing.items())]
        return said


# ---- the classified differences of cells (section 4.8) ---------------------------------

CLASSES = ("rule_choice", "reference_error", "data_difference")
PROOFS = ("other_pattern", "other_build")
# The keys of an other_build proof besides its kind; at least one is given.
BUILD_KEYS = ("analyses", "patterns", "template", "display")


def load_exceptions(path: Path) -> dict[str, list[dict]]:
    """The `cells` section of a kit's exceptions file: output -> entries.

    An entry: `cell` (its ID), `csr` (the CSR's text of the cell), `class`,
    `decision` (the decision record whose other alternative the CSR follows,
    for a rule_choice) and `proof`. Every problem of the shape is reported.
    """
    import yaml

    with open(path, encoding="ascii") as handle:
        data = yaml.safe_load(handle)
    sets = (data or {}).get("cells") or {}
    if not isinstance(sets, dict):
        raise CsrError(f"{path.name}: 'cells' must map an output to its entries")
    problems = []
    for output, entries in sets.items():
        if not isinstance(entries, list):
            problems.append(f"cells of {output}: expected a list of entries")
            continue
        seen = set()
        for number, entry in enumerate(entries):
            where = f"cells of {output}[{number}]"
            if not isinstance(entry, dict) or set(entry) != {"cell", "csr", "class", "decision",
                                                              "proof"}:
                problems.append(f"{where}: an entry has exactly cell, csr, class, decision and "
                                "proof")
                continue
            if not isinstance(entry["cell"], str) or not entry["cell"].startswith(
                    f"cell:{output}/"):
                problems.append(f"{where}: 'cell' must be the ID of a cell of {output}")
            elif entry["cell"] in seen:
                problems.append(f"{where}: {entry['cell']} is listed twice")
            seen.add(entry["cell"])
            if entry["class"] not in CLASSES:
                problems.append(f"{where}: 'class' must be one of {', '.join(CLASSES)}")
            proof = entry["proof"]
            if not isinstance(proof, dict) or proof.get("kind") not in PROOFS:
                problems.append(f"{where}: 'proof' needs a 'kind' out of {', '.join(PROOFS)}")
    if problems:
        raise CsrError(f"{path.name}: " + "; ".join(problems))
    return {str(output): list(entries) for output, entries in sets.items()}


def judge(found: Comparison, entries: list[dict], planned: dict[str, tuple[str, tuple]],
          ours: dict[str, float | int | None], decisions: set[str]) -> None:
    """Hold every differing cell of a comparison against its one entry; record the classes.

    `planned`: cell ID -> (template, shown parts), from the plan of the grid;
    `ours`: ARD row ID -> raw value; `decisions`: the IDs of the kit's
    decision records. A differing cell without an entry, an entry whose proof
    does not hold, and an entry for a cell that does not differ are problems.
    """
    from specfirst.machine import methods

    by_cell = {entry["cell"]: entry for entry in entries}
    for cell_id in sorted(set(by_cell) - set(found.differing)):
        found.problems.append(f"{cell_id}: an exception for a cell that does not differ from "
                              "the CSR")
    for cell_id, (text, theirs) in sorted(found.differing.items()):
        entry = by_cell.get(cell_id)
        where = f"{cell_id}: ours {text!r}, CSR {theirs!r}"
        if entry is None:
            found.problems.append(f"{where}: a difference with no class")
            continue
        reasons = []
        if squeeze(str(entry["csr"])) != squeeze(theirs):
            reasons.append(f"the entry says the CSR prints {entry['csr']!r}")
        if entry["decision"] not in decisions:
            reasons.append(f"no decision record {entry['decision']}")
        proof = entry["proof"]
        template, shown = planned.get(cell_id, ("", ()))
        if proof["kind"] == "other_pattern":
            patterns = proof.get("patterns")
            names = {item.name for item in shown}
            if entry["class"] != "rule_choice":
                reasons.append("other_pattern proves a rule_choice")
            if not isinstance(patterns, dict) or not patterns or set(patterns) - names:
                reasons.append("'patterns' must give parts of the cell "
                               f"({', '.join(sorted(names))})")
            else:
                try:
                    texts = {item.name: methods.pattern_text(
                        ours.get(item.ard), patterns.get(item.name, item.pattern)) or ""
                        for item in shown}
                    other = template.format(**texts)
                except (methods.MethodError, KeyError, ValueError) as error:
                    reasons.append(f"the other patterns cannot be applied: {error}")
                else:
                    if squeeze(other) != squeeze(theirs):
                        reasons.append(f"with the other patterns the cell is {other!r}")
                    if squeeze(other) == squeeze(text):
                        reasons.append("the other patterns change nothing")
        elif proof["kind"] == "other_build":
            reasons += _other_build(entry, proof, template, shown, ours, text, theirs)
        if reasons:
            found.problems.append(f"{where}: the proof does not hold: " + "; ".join(reasons))
        else:
            found.classified[cell_id] = entry["class"]


def _other_build(entry: dict, proof: dict, template: str, shown: tuple,
                 ours: dict[str, float | int | None], text: str, theirs: str) -> list[str]:
    """Why an other_build proof does not hold; nothing when it does."""
    from specfirst.machine import methods

    reasons = []
    if entry["class"] != "rule_choice":
        reasons.append("other_build proves a rule_choice")
    unknown = set(proof) - {"kind", *BUILD_KEYS}
    if unknown or not set(proof) & set(BUILD_KEYS):
        return reasons + [f"other_build takes {', '.join(BUILD_KEYS)}, at least one"]
    analyses = proof.get("analyses") or {}
    patterns = proof.get("patterns") or {}
    display = proof.get("display") or {}
    names = {item.name for item in shown}
    if not isinstance(analyses, dict) or set(analyses) - {item.analysis for item in shown}:
        reasons.append("'analyses' must map analyses of the cell to other analyses")
    if not isinstance(patterns, dict) or set(patterns) - names:
        reasons.append(f"'patterns' must give parts of the cell ({', '.join(sorted(names))})")
    if not isinstance(display, dict):
        reasons.append("'display' must give options of display.pattern")
    if reasons:
        return reasons
    texts = {}
    for item in shown:
        ard = item.ard
        if item.analysis in analyses:
            head = "ard:" + item.analysis + "/"
            ard = "ard:" + str(analyses[item.analysis]) + "/" + ard[len(head):]
            if ard not in ours:
                return [f"no result {ard} of the other analysis"]
        try:
            texts[item.name] = methods.pattern_text(
                ours.get(ard), patterns.get(item.name, item.pattern), **display) or ""
        except (methods.MethodError, TypeError) as error:
            return [f"the other build cannot be shown: {error}"]
    try:
        other = str(proof.get("template", template)).format(**texts)
    except (KeyError, ValueError, IndexError) as error:
        return [f"the other template cannot be filled: {error}"]
    if squeeze(other) != squeeze(theirs):
        reasons.append(f"with the other build the cell is {other!r}")
    if squeeze(other) == squeeze(text):
        reasons.append("the other build changes nothing")
    return reasons


def _body(grid: dict) -> list[tuple[str, object]]:
    """The lines of a grid's body: ("heading", section) before a new section, ("row", row)."""
    found: list[tuple[str, object]] = []
    current = None
    for row in grid["rows"]:
        if row.get("section") == HEADER_SECTION:
            continue
        if row.get("section") != current:
            current = row.get("section")
            if current is not None:
                found.append(("heading", current))
        found.append(("row", row))
    return found


def compare(grid: dict, reference: dict) -> Comparison:
    """Every cell of a grid against the reference grid of a CSR table (module docstring)."""
    found = Comparison(grid["output_id"], reference["table"])
    columns = [column["label"] for column in grid["columns"]]
    theirs_columns = [column["label"] for column in reference["columns"]]
    if [squeeze(text) for text in columns] != [squeeze(text) for text in theirs_columns]:
        found.problems.append(f"the column labels {columns} are not the CSR's {theirs_columns}")
        return found
    if [squeeze(text) for text in grid["titles"]] != [squeeze(text)
                                                       for text in reference["titles"]]:
        found.problems.append(f"the titles {grid['titles']} are not the CSR's "
                              f"{reference['titles']}")

    def cell(ours: dict, theirs: str | None) -> None:
        found.cells += 1
        if theirs is not None:
            found.printed += 1
        if squeeze(ours["text"]) == squeeze(theirs or ""):
            found.equal += 1
        else:
            found.differing[ours["id"]] = (ours["text"], theirs or "")

    header = [row for row in grid["rows"] if row.get("section") == HEADER_SECTION]
    if len(header) != 1:
        found.problems.append(f"the grid has {len(header)} header rows; the CSR has one line "
                              "of counts under the column labels")
    else:
        for ours, column in zip(header[0]["cells"], reference["columns"], strict=True):
            cell(ours, column["count"])
    ours_lines = _body(grid)
    theirs_lines = reference["lines"]
    if len(ours_lines) != len(theirs_lines):
        found.problems.append(f"the grid has {len(ours_lines)} lines under the header, the CSR "
                              f"{len(theirs_lines)}")
    pairs = zip(ours_lines, theirs_lines, strict=False)  # a difference of length is above
    for number, ((kind, item), line) in enumerate(pairs, start=1):
        where = f"line {number}"
        if kind == "heading":
            if line["cells"] is not None or squeeze(str(item)) != squeeze(line["label"]):
                found.problems.append(f"{where}: the grid has the heading {item!r}, the CSR "
                                      f"{line['label']!r} with cells {line['cells']}")
            continue
        if squeeze(item["label"]) != squeeze(line["label"]):
            found.problems.append(f"{where}: the grid has the row {item['label']!r}, the CSR "
                                  f"{line['label']!r}")
            continue
        if line["cells"] is None:
            found.problems.append(f"{where}: the CSR's {line['label']!r} is a heading, the "
                                  "grid's a row")
            continue
        for ours, theirs in zip(item["cells"], line["cells"], strict=True):
            cell(ours, theirs)
    return found
