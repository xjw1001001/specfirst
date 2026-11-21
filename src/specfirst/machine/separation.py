"""P4 on a reference study: one class per decision instead of a failure (issue #30, ADR-019).

PLAN.md section 4.6 states P4: changing any decision to another listed
alternative changes at least one result. A generated study is made so that
it holds: its probes are planted for the decisions, and the gate of gen-2a
asks it of every decision that a kit's log of probes claims
(`specfirst.gen.verify`). A reference is a study that was really delivered,
or any study used as an anchor. Its data were not made for the decisions,
and many of them do not separate. Section 4.7: "Where data cannot separate
two alternatives, the decision is marked `unseparated` and reported. It is
not counted as proven." This module says which kind of "not separated" a
decision of a reference is, so that a person knows what to ask.

What one other value does. A decision is built at its value in the study
(gold) and at every other value tried, all other decisions kept. The two
builds are compared at three layers, and the other value gets the highest
layer at which they differ (`compare`):

    fails     the other value cannot be built on these data, or compiled with
              the other decisions: it cannot give the reference
    outputs   a printed cell, a row label or a column label of an output
              differs, or an output is built in one of the two only
    results   an ARD row differs, and no printed cell does
    adam      an ADaM cell differs, and no ARD row does
    none      the two builds are the same in all three layers

`fails` and `outputs` separate the value from gold: the reference a person
holds is what the outputs print (P2 compares grid text; the reference of a
real study is a printed table or the formatted values of an ARS file).
`results` and `adam` separate it at the level of a dataset only: the
analysis results data or the ADaM datasets differ, the outputs do not.

The class of a decision (`classify`), from every value tried:

    inert                       no value tried changes an element that an
                                output reads (`read`, static: from the compile
                                and the trace, not from the data). Not asked:
                                no data can show it, under these outputs.
    separated                   every value tried separates in the outputs.
    unseparated                 some value tried gives the same build as gold
                                in all three layers: nothing in the study can
                                tell the two apart. Asked first.
    separated_at_dataset_only   no value tried gives the same build, but some
                                give the same outputs: the ADaM datasets or the
                                ARD differ, the outputs that read the decision
                                do not. Asked, with those outputs named.

`no_alternative` is not a class: the decision has no other value to be
changed to, and P4 asks nothing of it.

A decision is `separated` only when every other value separates. One value
that reproduces the outputs is enough to leave the gold value unproven: the
data cannot tell the two apart, whatever the other values do (the same
reading as the matrix of a generated kit, where every pair of the gold value
with another alternative must be separated).

The interval of a numeric parameter (`interval`). For an integer slot of the
gold alternative, the values of the slot next to gold are built one at a
time, all other slots at gold, until a value separates or the scan ends. The
interval is the run of values around gold that give the same outputs as
gold; each end says what stops it: a value that separates (`separated`), the
bound of the slot in the catalog (`slot_minimum`, `slot_maximum`), or the
end of the scan (`scan_limit`: the interval may go on). Every value scanned
is also a value tried: one that gives the same build in all three layers
makes the decision `unseparated`.

The decision record. Its field `identifiable` (decision-record.schema.json)
has two values. A decision is `separated` there only when its class is
`separated`; the three other classes are `unseparated` (section 4.7: not
counted as proven), and `no_alternative` leaves the field empty
(`identifiable`). The class, the values that reproduce and the interval are
in the matrix. A scorer that reads `identifiable` therefore never credits a
decision of another class as shown by the results, and reports it apart.

The review (`review`): the decisions in the order a person should look at
them: `unseparated` first, then `separated_at_dataset_only`, then
`separated`; `inert` and `no_alternative` last, not asked.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass

CLASSES = ("separated", "unseparated", "inert", "separated_at_dataset_only")
NO_ALTERNATIVE = "no_alternative"
# What another value changes, from the most to the least.
LEVELS = ("fails", "outputs", "results", "adam", "none")
SEPARATING = ("fails", "outputs")
BELOW_OUTPUTS = ("results", "adam")
# The order of the review, and whether a person is asked.
REVIEW_ORDER = ("unseparated", "separated_at_dataset_only", "separated", "inert", NO_ALTERNATIVE)
ASKED = ("unseparated", "separated_at_dataset_only")
# What ends an interval on one side.
ENDS = ("separated", "slot_minimum", "slot_maximum", "scan_limit")


@dataclass(frozen=True)
class Comparison:
    """What another value changes against gold, at each layer."""

    level: str  # one of LEVELS
    adam: int = 0  # ADaM cells that differ (a dataset or a column in one build only: all its cells)
    results: int = 0  # ARD rows that differ or are in one build only
    cells: int = 0  # printed cells that differ or are in one build only; an axis counts one
    failure: str = ""  # why the other value cannot be built

    def as_dict(self) -> dict:
        found = {"level": self.level, "adam": self.adam, "results": self.results,
                 "cells": self.cells}
        if self.failure:
            found["failure"] = self.failure
        return found


# ---- comparing two builds ---------------------------------------------------------------


def _canonical(value: object) -> object:
    """A value that compares equal to itself: NaN is the same as NaN."""
    if isinstance(value, float) and math.isnan(value):
        return "NaN"
    return value


def adam_changes(one: dict, two: dict) -> int:
    """The ADaM cells that differ between two sets of tables (dataset -> Arrow table).

    Cells are compared row by row in the order of the tables. A dataset, a
    column or a row that one side has and the other has not counts with all
    its cells.
    """
    count = 0
    for name in sorted(set(one) | set(two)):
        first, second = one.get(name), two.get(name)
        if first is None or second is None:
            table = first if second is None else second
            count += table.num_rows * max(len(table.column_names), 1)
            continue
        names = sorted(set(first.column_names) | set(second.column_names))
        rows = max(first.num_rows, second.num_rows)
        for column in names:
            if column not in first.column_names or column not in second.column_names:
                count += rows
                continue
            a = [_canonical(v) for v in first.column(column).to_pylist()]
            b = [_canonical(v) for v in second.column(column).to_pylist()]
            count += sum(1 for x, y in zip(a, b, strict=False) if x != y) + abs(len(a) - len(b))
    return count


def result_changes(one: dict, two: dict) -> int:
    """The ARD rows (ID -> row) that differ or that one side has and the other has not."""
    def text(row: dict | None) -> str | None:
        return None if row is None else json.dumps(row, sort_keys=True, default=str)

    return sum(1 for key in set(one) | set(two) if text(one.get(key)) != text(two.get(key)))


def printed(grid: dict) -> dict:
    """What a grid prints: titles, column labels, row labels, cell texts, footnotes."""
    return {
        "titles": list(grid.get("titles") or []),
        "columns": [column.get("label") for column in grid.get("columns") or []],
        "rows": [row.get("label") for row in grid.get("rows") or []],
        "cells": {cell["id"]: cell.get("text") for row in grid.get("rows") or []
                  for cell in row.get("cells") or []},
        "footnotes": list(grid.get("footnotes") or []),
    }


def output_changes(one: dict, two: dict) -> int:
    """The printed cells of the outputs (output ID -> grid) that differ, plus one for each
    title, column axis, row axis or footnote list that differs. An output that one side
    builds and the other does not counts with all its cells, and at least one."""
    count = 0
    for output in sorted(set(one) | set(two)):
        if output not in one or output not in two:
            grid = one.get(output) or two.get(output)
            count += max(len(printed(grid)["cells"]), 1)
            continue
        a, b = printed(one[output]), printed(two[output])
        count += sum(1 for key in set(a["cells"]) | set(b["cells"])
                     if a["cells"].get(key) != b["cells"].get(key))
        count += sum(1 for part in ("titles", "columns", "rows", "footnotes") if a[part] != b[part])
    return count


def compare(gold: object, other: object) -> Comparison:
    """What another value changes against gold. Each argument is a build with the
    attributes `failure`, `adam`, `ard` and `grids` (specfirst.score.candidate.Build)."""
    if gold.failure:
        raise ValueError(f"the gold value cannot be built: {gold.failure}")
    if other.failure:
        return Comparison("fails", failure=other.failure)
    adam = adam_changes(gold.adam, other.adam)
    results = result_changes(gold.ard, other.ard)
    cells = output_changes(gold.grids, other.grids)
    if cells:
        level = "outputs"
    elif results:
        level = "results"
    elif adam:
        level = "adam"
    else:
        level = "none"
    return Comparison(level, adam, results, cells)


# ---- the class of a decision ------------------------------------------------------------


def classify(read: bool, levels: list[str]) -> str:
    """The class of a decision from the levels of the values tried (`LEVELS`), and
    whether an output reads an element that one of them changes."""
    unknown = sorted(set(levels) - set(LEVELS))
    if unknown:
        raise ValueError(f"not a level: {', '.join(unknown)}")
    if not levels:
        return NO_ALTERNATIVE
    if not read:
        return "inert"
    if all(level in SEPARATING for level in levels):
        return "separated"
    if "none" in levels:
        return "unseparated"
    return "separated_at_dataset_only"


def identifiable(klass: str) -> str | None:
    """The field `identifiable` of the decision record for a class (decision-record schema:
    `separated` or `unseparated`; empty where nothing is changed)."""
    if klass == NO_ALTERNATIVE:
        return None
    if klass not in CLASSES:
        raise ValueError(f"not a class: {klass}")
    return "separated" if klass == "separated" else "unseparated"


def credited(record: dict) -> bool:
    """Whether results can confirm a decision: only when the machine marked it
    `separated`. A decision of any other class is compared by value only, and reported
    apart (PLAN.md sections 4.7 and 9.3)."""
    return record.get("identifiable") == "separated"


def interval(slot: str, gold: int, levels: dict[int, str], low_limit: int, high_limit: int,
             minimum: float | None, maximum: float | None) -> dict:
    """The interval of an integer slot that gives the same outputs as its gold value.

    `levels` holds the level of every value scanned (gold excluded); the scan
    went from gold down to `low_limit` and up to `high_limit`, and stopped on
    each side at the first value that separates. `minimum` and `maximum` are
    the bounds of the slot in the catalog, when it has them.
    """
    def side(step: int, limit: int, bound: float | None, name: str) -> tuple[int, str]:
        value = gold
        while True:
            following = value + step
            if (following < limit) if step < 0 else (following > limit):
                reached = bound is not None and following * step > bound * step
                return value, (name if reached else "scan_limit")
            level = levels.get(following)
            if level is None:
                raise ValueError(f"{slot} = {following} was not scanned")
            if level in SEPARATING:
                return value, "separated"
            value = following

    low, below = side(-1, low_limit, minimum, "slot_minimum")
    high, above = side(1, high_limit, maximum, "slot_maximum")
    inside = {number: level for number, level in levels.items() if low <= number <= high}
    return {"slot": slot, "gold": gold, "low": low, "high": high, "below": below,
            "above": above,
            "same": sorted(number for number, level in inside.items() if level == "none"),
            "dataset_only": sorted(number for number, level in inside.items()
                                   if level in BELOW_OUTPUTS)}


def problems(item: dict) -> list[str]:
    """What is wrong in the entry of one decision of a matrix: an inert decision whose
    value changes an output (the static reach missed what the output reads), a class
    that its values do not give, an interval that does not hold gold."""
    found = []
    name = f"{item['id']} ({item['unit']})"
    values = item.get("values") or []
    if item["class"] == "inert":
        found += [f"{name}: inert, yet {value['label']} "
                  + ("cannot be built" if value["level"] == "fails" else "changes the outputs")
                  for value in values if value["level"] in SEPARATING]
    expected = classify(bool(item.get("read")), [value["level"] for value in values])
    if expected != item["class"]:
        found.append(f"{name}: the class is {item['class']}; its values give {expected}")
    for span in item.get("intervals") or []:
        if not span["low"] <= span["gold"] <= span["high"]:
            found.append(f"{name}: the interval of {span['slot']} does not hold gold")
    return found


def review(matrix: dict) -> list[dict]:
    """The decisions in the order of the review: unseparated first (section 4.7)."""
    rank = {klass: number for number, klass in enumerate(REVIEW_ORDER)}
    ordered = sorted(matrix["decisions"], key=lambda item: (rank[item["class"]], item["id"],
                                                          item["unit"]))
    found = []
    for item in ordered:
        entry = {"id": item["id"], "unit": item["unit"], "class": item["class"],
                 "asked": item["class"] in ASKED}
        if item["class"] == "unseparated":
            entry["reproduce"] = item.get("reproduce") or []
        if item["class"] == "separated_at_dataset_only":
            entry["outputs"] = item.get("outputs") or []
        if item.get("intervals"):
            entry["intervals"] = [{key: span[key] for key in ("slot", "low", "high", "below",
                                                              "above")}
                                  for span in item["intervals"]]
        found.append(entry)
    return found


def summary(decisions: list[dict]) -> dict:
    """The decisions of a matrix by class, and the values tried by level."""
    found = {"decisions": len(decisions)}
    for klass in (*CLASSES, NO_ALTERNATIVE):
        found[klass] = sorted(f"{item['id']} ({item['unit']})" for item in decisions
                              if item["class"] == klass)
    found["values"] = {level: sum(1 for item in decisions for value in item.get("values") or []
                                  if value["level"] == level) for level in LEVELS}
    return found


def differences(recorded: dict, fresh: dict) -> list[str]:
    """Where a matrix that was written differs from a new mutation: per decision, the
    class, `identifiable`, the level of each value, the values that reproduce, the
    intervals; and decisions that one of the two has and the other has not."""
    found = []
    mine = {(item["id"], item["unit"]): item for item in recorded.get("decisions") or []}
    theirs = {(item["id"], item["unit"]): item for item in fresh.get("decisions") or []}
    for key in sorted(set(mine) | set(theirs)):
        name = f"{key[0]} ({key[1]})"
        if key not in mine or key not in theirs:
            found.append(f"{name}: in the {'new mutation' if key not in mine else 'written'} "
                         "matrix only")
            continue
        a, b = mine[key], theirs[key]
        for part in ("class", "identifiable", "read", "reproduce", "outputs", "intervals"):
            if a.get(part) != b.get(part):
                found.append(f"{name}: {part} is {json.dumps(a.get(part), sort_keys=True)} in "
                             f"the written matrix and {json.dumps(b.get(part), sort_keys=True)} "
                             "in a new mutation")
        levels_a = {value["label"]: value["level"] for value in a.get("values") or []}
        levels_b = {value["label"]: value["level"] for value in b.get("values") or []}
        if levels_a != levels_b:
            found.append(f"{name}: the levels of its values differ: written "
                         f"{json.dumps(levels_a, sort_keys=True)}, new "
                         f"{json.dumps(levels_b, sort_keys=True)}")
    return found
