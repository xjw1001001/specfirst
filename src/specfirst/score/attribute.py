"""Attribution (PLAN.md section 9.4): the layer and the decision that own a wrong cell.

"For each wrong cell, walk the gold graph upstream and compare candidate and
gold artifacts layer by layer. The first element that differs owns the
error." The walk goes from the cell to what it rests on:

    cell -> the results it shows -> their analyses (the numerator's and the
    denominator's) -> the ADaM columns those analyses read, in any role ->
    the ADaM columns these derive from

and the comparison starts at the far end, because a difference there
explains every difference after it:

    L4  an ADaM column on the path has other values in the candidate. The
        owner is the column no other differing column lies upstream of.
    L5  the data are the same, and an analysis on the path is defined in
        another way, or is not there: the analysis itself, its analysis
        set, its data subset, a grouping or its method.
    L6  data and analyses are the same, and a result of the cell has
        another value or is not there. No decision reaches this: the
        results were changed after they were computed.
    L7  the results are the same and the cell is not: the layout.

A build that stopped has no artifacts to compare. Its cells are owned by
the layer `build`, with the rule that failed (section 9.2, validity).

An axis that is not the gold axis (section 9.2, structure) is walked the
same way. The columns of a table are the groups of a grouping: the values
its variable has on the records of the analysis set. So the columns rest on
data as well, on the ADaM columns that the analyses of the output read as a
grouping or as an analysis set, and a treatment label that a decision
writes in another way owns the axis at L4. The rows of the tables of this
slice are listed by the layout and rest on no data.

The decision. Of the decisions in which the candidate differs from gold,
the owners are those that decide the element that differs. That is the
`decides` edge of section 4.2, proven by compiling: a decision decides the
elements that change when the gold vector takes the candidate's value for
it, or the candidate's vector the gold value (`Machine.changes`). For an
ADaM column this includes the working columns its rule passes through.

An attribution is a claim. `confirm` runs it (rule R1): the candidate is
built again with the owning decisions at their gold values, and the claim
holds for a cell when the cell then has the gold text.

Elements of a wrong cell that differ beyond the first are kept in `also`.
One owner per cell is the rule of section 9.4; a second wrong decision
behind the same cell shows when the first is right.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field

from specfirst.machine import ars
from specfirst.score.build import (
    ColumnKey,
    RowKey,
    WrongCell,
    adam_differences,
    ard_differences,
    table_of,
)
from specfirst.score.candidate import SUBJECT_KEY, Build, Key, Machine
from specfirst.score.reading import same_value

LAYERS = {"L4": "analysis data", "L5": "analysis", "L6": "results", "L7": "display",
          "build": "the build stopped"}


@dataclass
class Owner:
    """Who owns one wrong cell."""

    output: str
    cell: str  # the ID of the gold cell
    row: RowKey
    column: ColumnKey
    layer: str  # a key of LAYERS
    element: str | None  # the first element that differs
    decisions: tuple[Key, ...] = ()  # the differing decisions that decide it
    also: tuple[str, ...] = ()  # more elements on the path that differ
    confirmed: bool | None = None  # None: not run
    note: str = ""

    @property
    def unit(self) -> str | None:
        """The owning unit: that of the first owning decision."""
        return self.decisions[0][1] if self.decisions else None


def differing_decisions(gold: Build, candidate: Build) -> list[Key]:
    """The decisions with another value in the candidate's vector, gold's order first."""
    keys = list(dict.fromkeys([(r["id"], r["unit"]) for r in gold.records]
                              + [(r["id"], r["unit"]) for r in candidate.records]))
    return [key for key in keys if not same_value(gold.value(key), candidate.value(key))]


def _reach(edges: list[dict]) -> dict[str, set[str]]:
    following: dict[str, set[str]] = {}
    for edge in edges:
        if edge["type"] == "derives_from":
            following.setdefault(edge["from"], set()).add(edge["to"])
    reach: dict[str, set[str]] = {}
    for start in following:
        seen, stack = {start}, [start]
        while stack:
            for nxt in following.get(stack.pop(), ()):
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        reach[start] = seen - {start}
    return reach


def analysis_parts(event: ars.Event | None, analysis_id: str) -> dict[str, object]:
    """An analysis with everything its definition names, by element ID.

    The analysis without its results, its analysis set, its data subset,
    its groupings and its method. Two reporting events define an analysis
    in the same way when these are equal.
    """
    if event is None or analysis_id not in event.analyses:
        return {}
    analysis = event.analyses[analysis_id]
    parts: dict[str, object] = {
        f"ars:{analysis_id}": {k: v for k, v in analysis.items() if k != "results"}}
    for key, known in (("analysisSetId", event.sets), ("dataSubsetId", event.subsets),
                       ("methodId", event.methods)):
        if analysis.get(key):
            parts[f"ars:{analysis[key]}"] = known.get(analysis[key])
    for entry in event.groupings_of(analysis):
        parts[f"ars:{entry['groupingId']}"] = event.groupings.get(entry["groupingId"])
    return parts


def _index(document: dict | None) -> ars.Event | None:
    return ars.index(document) if document else None


@dataclass
class _Walk:
    """What the walk of every cell of one pair of builds shares."""

    gold: Build
    candidate: Build
    differing: list[Key]
    changes: dict[Key, set[str]]
    adam: dict[str, int]
    ard: dict[str, str]
    reach: dict[str, set[str]]
    gold_event: ars.Event | None
    candidate_event: ars.Event | None
    through: dict[str, set[str]] = field(default_factory=dict)

    def deciders(self, elements: set[str]) -> tuple[Key, ...]:
        return tuple(key for key in self.differing if self.changes[key] & elements)


def _prepare(machine: Machine, gold: Build, candidate: Build) -> _Walk:
    differing = differing_decisions(gold, candidate)
    changes = {key: machine.changes(gold.records, key, candidate.value(key))
               | machine.changes(candidate.records, key, gold.value(key)) for key in differing}
    through: dict[str, set[str]] = {}
    for build in (gold, candidate):
        for column, passed in build.through.items():
            dataset = column.rsplit(".", 1)[0]
            through.setdefault(column, {column}).update(f"{dataset}.{name}" for name in passed)
    return _Walk(gold, candidate, differing, changes,
                 adam_differences(gold.adam, candidate.adam) if candidate.ok else {},
                 ard_differences(gold.ard, candidate.ard) if candidate.ok else {},
                 _reach(gold.edges), _index(gold.ars),
                 _index(candidate.ars) if candidate.ok else None, through)


def _stopped(machine: Machine, walk: _Walk, reason: str, unit: str | None) -> tuple[Key, ...]:
    """The decisions that own a build that stopped, or an output that was not built.

    A build that does not compile: the differing decisions each of which,
    taken at its gold value alone, makes the vector compile. Otherwise the
    differing decisions that change the specs of the output's unit.
    """
    if reason.startswith("compile:"):
        found = []
        for key in walk.differing:
            other = [r for r in walk.candidate.records if (r["id"], r["unit"]) != key]
            value = walk.gold.value(key)
            if value is not None:
                other.append({"id": key[0], "unit": key[1], "value": value})
            if not isinstance(machine.compile(other), str):
                found.append(key)
        return tuple(found)
    return tuple(key for key in walk.differing
                 if any(e.startswith(("ars:", f"layout:{unit}/")) for e in walk.changes[key]))


def _own(walk: _Walk, machine: Machine, wrong: WrongCell) -> Owner:
    made = dict(output=wrong.output, cell=wrong.cell, row=wrong.row, column=wrong.column)
    gold, candidate = walk.gold, walk.candidate
    unit = gold.outputs.get(wrong.output)
    if not candidate.ok:
        return Owner(**made, layer="build", element=candidate.failure,
                     decisions=_stopped(machine, walk, str(candidate.failure), unit))
    if wrong.output in candidate.not_produced:
        reason = candidate.not_produced[wrong.output]
        return Owner(**made, layer="build", element=reason,
                     decisions=_stopped(machine, walk, reason, unit))
    path = gold.paths.get(wrong.cell)
    if path is None or walk.gold_event is None:
        return Owner(**made, layer="L7", element=None, note="the gold cell has no path")
    # L4: the ADaM columns the analyses of the cell read, and what those derive from.
    read = {f"adam:{dataset}.{variable}" for analysis_id in path.analyses
            for _, dataset, variable in ars.reads(walk.gold_event, analysis_id, SUBJECT_KEY)}
    data = _other_data(walk, read)
    if data is not None:
        root, decisions, also = data
        return Owner(**made, layer="L4", element=root, decisions=decisions, also=also)
    # L5: the analyses, with what their definitions name.
    other_parts: list[str] = []
    for analysis_id in path.analyses:
        ours = analysis_parts(walk.gold_event, analysis_id)
        theirs = analysis_parts(walk.candidate_event, analysis_id)
        other_parts += [name for name in ours if ours[name] != theirs.get(name)]
    if other_parts:
        other_parts = list(dict.fromkeys(other_parts))
        return Owner(**made, layer="L5", element=other_parts[0],
                     decisions=walk.deciders(set(other_parts)), also=tuple(other_parts[1:]))
    # L6: the results of the cell.
    other_results = [key for key in path.ard if key in walk.ard]
    if other_results:
        return Owner(**made, layer="L6", element=other_results[0], also=tuple(other_results[1:]),
                     note=f"the result is {walk.ard[other_results[0]]} in the candidate, with "
                          "the same data and the same analysis")
    # L7: the layout.
    ours, theirs = gold.layouts.get(unit) or {}, candidate.layouts.get(unit) or {}
    parts = [f"layout:{unit}/{part}" for part in ours if ours[part] != theirs.get(part)]
    return Owner(**made, layer="L7", element=parts[0] if parts else None,
                 decisions=walk.deciders(set(parts)), also=tuple(parts[1:]),
                 note="" if parts else "the layouts are the same: the text was changed")


def _other_data(walk: _Walk, read: set[str]) -> tuple[str, tuple[Key, ...], tuple[str, ...]] | None:
    """Of the ADaM columns that are read and of those they derive from: the ones with
    other values in the candidate. Returns the first column that no other differing
    column lies upstream of, the differing decisions that decide such columns, and
    the other differing columns; None when the data on the path are the same."""
    on_path = set(read)
    for column in read:
        on_path |= {node for node in walk.reach.get(column, set()) if node.startswith("adam:")}
    other_data = sorted(column for column in on_path if column in walk.adam)
    if not other_data:
        return None
    roots = [column for column in other_data
             if not walk.reach.get(column, set()) & set(other_data)]
    decided: set[str] = set()
    for column in roots:
        decided |= walk.through.get(column, {column})
    return (roots[0], walk.deciders(decided),
            tuple(column for column in other_data if column != roots[0]))


@dataclass
class AxisOwner:
    """Who owns an axis of an output that is not the gold axis (section 9.2, structure)."""

    output: str
    axis: str  # rows | columns
    layer: str
    element: str | None
    decisions: tuple[Key, ...] = ()
    confirmed: bool | None = None

    @property
    def unit(self) -> str | None:
        return self.decisions[0][1] if self.decisions else None


def _own_axis(walk: _Walk, output: str, axis: str) -> AxisOwner:
    """An axis differs when the data give the columns other groups (L4: a treatment
    label written in another way, another subject in the analysis set), when the
    analyses behind the output are defined in another way (L5: a row or a column
    more or less), or when the layout places the same analyses in another way (L7:
    another order, a row or column left out)."""
    gold, candidate = walk.gold, walk.candidate
    unit = gold.outputs.get(output)
    prefix = f"cell:{output}/"
    names = list(dict.fromkeys(
        analysis_id for build in (gold, candidate) for cell, path in build.paths.items()
        if cell.startswith(prefix) for analysis_id in path.analyses))
    if axis == "columns" and walk.gold_event is not None:
        read = {f"adam:{dataset}.{variable}" for analysis_id in names
                if analysis_id in walk.gold_event.analyses
                for role, dataset, variable in ars.reads(walk.gold_event, analysis_id,
                                                         SUBJECT_KEY)
                if role in ("grouping", "set")}
        data = _other_data(walk, read)
        if data is not None:
            return AxisOwner(output, axis, "L4", data[0], data[1])
    parts: list[str] = []
    for analysis_id in names:
        ours = analysis_parts(walk.gold_event, analysis_id)
        theirs = analysis_parts(walk.candidate_event, analysis_id)
        parts += [name for name in {**ours, **theirs} if ours.get(name) != theirs.get(name)]
    if parts:
        parts = list(dict.fromkeys(parts))
        return AxisOwner(output, axis, "L5", parts[0], walk.deciders(set(parts)))
    part = f"layout:{unit}/{axis}"
    ours, theirs = gold.layouts.get(unit) or {}, candidate.layouts.get(unit) or {}
    if ours.get(axis) != theirs.get(axis):
        return AxisOwner(output, axis, "L7", part, walk.deciders({part}))
    return AxisOwner(output, axis, "L7", None)


def attribute(machine: Machine, gold: Build, candidate: Build, wrong: list[WrongCell],
              axes: list[tuple[str, str]] | None = None) -> tuple[list[Owner], list[AxisOwner]]:
    """The owner of every wrong cell of a candidate build, against the gold build
    of the same dataset; and of every axis that is not the gold axis.

    `axes` lists (output, `rows` or `columns`) for the outputs that were
    produced with another axis.
    """
    walk = _prepare(machine, gold, candidate)
    return ([_own(walk, machine, cell) for cell in wrong],
            [_own_axis(walk, output, axis) for output, axis in axes or []])


def confirm(owners: list[Owner], axes: list[AxisOwner], gold: Build, candidate: Build,
            rebuild: Callable[[list[dict]], Build]) -> None:
    """Run every attribution to decisions: build the candidate again with the owning
    decisions at their gold values, and see whether the cell then has the gold
    text, or the axis is then the gold axis.

    `rebuild` builds a decision vector on the dataset of the two builds. An
    owner without a decision is left as it is (`confirmed` stays None).
    """
    again: dict[tuple[Key, ...], Build] = {}

    def built_with(decisions: tuple[Key, ...]) -> Build:
        if decisions not in again:
            records = [r for r in candidate.records if (r["id"], r["unit"]) not in decisions]
            for key in decisions:
                value = gold.value(key)
                if value is not None:
                    records.append({"id": key[0], "unit": key[1], "value": value})
            order = {(r["id"], r["unit"]): n for n, r in enumerate(gold.records)}
            records.sort(key=lambda r: order.get((r["id"], r["unit"]), len(order)))
            again[decisions] = rebuild(records)
        return again[decisions]

    for owner in owners:
        if not owner.decisions:
            continue
        grid = built_with(owner.decisions).grids.get(owner.output)
        if grid is None:
            owner.confirmed = False
            continue
        cell = table_of(grid).cells.get((owner.row, owner.column))
        wanted = table_of(gold.grids[owner.output]).cells[(owner.row, owner.column)]["text"]
        owner.confirmed = cell is not None and cell["text"] == wanted
    for axis in axes:
        if not axis.decisions:
            continue
        grid = built_with(axis.decisions).grids.get(axis.output)
        ours = table_of(gold.grids[axis.output])
        axis.confirmed = grid is not None and (
            table_of(grid).rows == ours.rows if axis.axis == "rows"
            else table_of(grid).columns == ours.columns)


def summary(owners: list[Owner]) -> list[tuple[str, str, str, int, int]]:
    """Wrong cells by layer, owning unit and decision: (layer, unit, decisions, cells,
    of which confirmed)."""
    counts: Counter = Counter()
    confirmed: Counter = Counter()
    for owner in owners:
        name = (owner.layer, owner.unit or "-",
                ", ".join(key[0] for key in owner.decisions) or "-")
        counts[name] += 1
        confirmed[name] += owner.confirmed is True
    return [(*name, count, confirmed[name]) for name, count in sorted(counts.items())]
