"""The mock shell against a table shell (specfirst.machine.shells; the review of real-3a, F1).

The shell here is made up for the toy output of tests/toy_displays.py, in the form
poppler's pdftotext gives a shell of CDISC's example: cells apart by two or more
blanks, masks in capitals. Each planted defect passed the comparison with the
formatted values (lesson 29) and must fail here.
"""

from __future__ import annotations

import pytest
import toy_displays as displays

from specfirst.machine import ars, grid, layout, shells

HEADING = "Number of subjects with"
SHELL = f"""\
Study - Toy                                                     Page x of y
                               Table 1
                         Toy summary of events

                                   Arm A          Arm B          Arm C
Subjects, n (%)                   (N=XX)         (N=XX)         (N=XX)
                              ______ ______ ______ ______ ______ ______
{HEADING}
  With an adverse event        XX ( XX.X)     XX ( XX.X)     XX ( XX.X)
  Treatment-emergent           XX ( XX.X)     XX ( XX.X)     XX ( XX.X)

Note: made up.
"""


@pytest.fixture(scope="module")
def event():
    return ars.index(displays.event_data())


def held(event, change=None, text=SHELL) -> shells.Held:
    """The toy layout, its rows in the section of the shell's heading, changed by `change`."""
    data = displays.layout_data()
    data["rows"][1]["section"] = HEADING
    if change:
        change(data)
    return shells.compare(grid.shell(event, layout.parse(data)), shells.lines(text))


def test_the_lines_of_a_shell():
    found = shells.lines(SHELL)
    rows = [(line.label, line.masks) for line in found if line.masks]
    assert rows == [("Subjects, n (%)", ("(N=XX)",) * 3),
                    ("With an adverse event", ("XX ( XX.X)",) * 3),
                    ("Treatment-emergent", ("XX ( XX.X)",) * 3)]
    assert [line.header for line in found if line.masks] == [True, False, False]
    assert ("Arm A Arm B Arm C", (), 3) in [(line.label, line.masks, line.pieces)
                                            for line in found]


@pytest.mark.parametrize(("piece", "mask"), [
    ("XX", True), ("(N=XX)", True), ("XX ( XX.X)", True), ("XX.X (XX.XX)", True),
    ("XX.X, XX.X", True), ("XX, XX", True), ("Xanomeline", False), ("Page x of y", False),
    ("NX", False), ("TEAE", False), ("<Visit n>", False)])
def test_what_is_a_mask(piece, mask):
    assert shells.is_mask(piece) is mask


def test_the_mock_shell_is_held_against_the_shell(event):
    found = held(event)
    assert found.problems == [] and (found.rows, found.lines) == (3, 2)


@pytest.mark.parametrize(("change", "message"), [
    # The three cases of the review that passed the comparison with formatted values.
    (lambda d: d["rows"][1].update(cell="{pct} {n}"), "no row of the shell has this label"),
    (lambda d: d["rows"][1].update(cell="{n}/{pct}"), "no row of the shell has this label"),
    (lambda d: d["rows"][0].update(cell="N={N}"), "the header masks"),
    # The mask of the count: the text of a count is the same under XX and XXX.
    (lambda d: d["rows"][1]["parts"]["n"].update(pattern="XXX"),
     "no row of the shell has this label"),
    (lambda d: d["rows"][1].update(analyses=list(reversed(d["rows"][1]["analyses"]))),
     "does not follow the row before it"),
    (lambda d: d["rows"][1]["analyses"].pop(), "no row of the mock shell has it"),
    (lambda d: d["rows"][1]["analyses"].__setitem__(1, {"id": "A_TEAE", "label": "Emergent"}),
     "no row of the shell has this label"),
    (lambda d: d["rows"][1].update(section="Events"), "section 'Events': no text of the shell"),
    # The line above the rows of the shell (the line of the review of real-3a, F1).
    (lambda d: d["rows"][1].pop("section"), "a heading no section and no row"),
])
def test_what_the_shell_does_not_show_is_seen(event, change, message):
    found = held(event, change)
    assert any(message in problem for problem in found.problems), found.problems


def _grid(cells: list[list[str]], labels: list[str]) -> dict:
    """A mock shell made by hand: one row without cells, then rows with the given texts."""
    return {"columns": [{"id": f"c{n}", "label": ""} for n in range(1, 5)], "rows": [
        {"id": "r1", "label": "Baseline",
         "cells": [{"id": f"x/r1/c{n}", "column": f"c{n}", "text": ""} for n in range(1, 5)]},
        *({"id": f"r{n}", "label": label, "cells": [
            {"id": f"x/r{n}/c{m}", "column": f"c{m}", "text": text}
            for m, text in enumerate(texts, start=1)]}
          for n, (label, texts) in enumerate(zip(labels, cells, strict=True), start=2))]}


def test_where_a_cell_stands_in_a_row_with_empty_cells():
    """Observed and change side by side under each arm: at baseline only the observed value.
    A layout that put the observed value under the change shows the same masks in the same
    order; the place of the cells on the line tells them apart."""
    text = """\
                     Observed    Change      Observed    Change
Baseline
  n                     XX                      XX
  Mean                 XX.X                    XX.X
Week 2
  n                     XX          XX          XX          XX
"""
    found = shells.lines(text)
    assert [line.masks for line in found if line.masks][0] == ("XX", "XX")
    right = _grid([["xx", "", "xx", ""], ["xx.x", "", "xx.x", ""]], ["n", "Mean"])
    assert shells.compare(right, found).problems == ["line 6 of the shell ('n', ['XX', 'XX', "
                                                     "'XX', 'XX']): no row of the mock shell "
                                                     "has it"]
    swapped = _grid([["", "xx", "", "xx"], ["", "xx.x", "", "xx.x"]], ["n", "Mean"])
    problems = shells.compare(swapped, found).problems
    assert any("its cells stand in the columns [2, 4]; on line 3 of the shell in [1, 3]"
               in problem for problem in problems), problems


def test_a_section_may_fit_a_placeholder(event):
    placeholder = SHELL.replace(HEADING, "<Category n> (<unit>)")
    assert held(event, lambda d: d["rows"][1].update(section="Events (subjects)"),
                placeholder).problems == []
    assert held(event, lambda d: d["rows"][1].update(section="Events"), placeholder).problems
