"""Attribution (PLAN.md section 9.4): the layer and the decision that own a wrong cell.

"For each wrong cell, walk the gold graph upstream and compare candidate and
gold artifacts layer by layer. The first element that differs owns the
error." The walk goes from the cell to what it rests on:

    cell -> the results it shows -> their analyses (the numerator's and the
    denominator's) -> the ADaM columns those analyses read, in any role ->
    the ADaM columns these derive from

Does anything above the display reach the cell? Only when a result of the
cell has another value in the candidate or is not there, or when a group a
result belongs to is another group (a treatment label written in another
way). When every result of the cell and every group is the same in both
builds, the difference is the display's, whatever differs further up in
the data: a wrong record of another arm, an analysis defined in another way
that gives the same number.

Where something reaches the cell, each layer with a difference on the path
makes a claim, the far end first, because a difference there explains
every difference after it:

    L4  an ADaM column on the path has other values in the candidate. The
        claim names the column no other differing column lies upstream of.
    L5  an analysis on the path is defined in another way, or is not there:
        the analysis itself, its analysis set, its data subset, a grouping
        or its method.
    L6  a result of the cell has another value or is not there. No decision
        is named: the results were changed after they were computed.
    L7  the layout of the output is another.

A build that stopped has no artifacts to compare. Its cells are claimed by
the layer `build`, with the rule that failed (section 9.2, validity).

The decision. Of the decisions in which the candidate differs from gold, a
claim names those that decide its element. That is the `decides` edge of
section 4.2, proven by compiling: a decision decides the elements that
change when the gold vector takes the candidate's value for it, or the
candidate's vector the gold value (`Machine.changes`). For an ADaM column
this includes the working columns its rule passes through.

A claim is run before it is an owner (rule R1). The candidate is built
again with decisions at their gold values, and decisions own a cell when
the cell then has the gold text. In this order:

    1. one decision that a claim names, alone: the first that gives the
       gold text, the far end first. `confirmed`;
    2. else the fewest of the decisions that the claims name which give
       the gold text together: several differences reach the cell, and no
       one of them is enough. `confirmed`, and the note says so;
    3. else, when the gold decisions themselves give the gold text in this
       build, more decisions than the claims name: the other wrong
       decisions are added until the cell has the gold text, and what is
       not needed is taken out again. This is a wrong decision whose
       difference another wrong decision hides (the treatment variable of
       a table on the safety set, while the table names another set): no
       artifact of the candidate shows it, and with the other decision
       right the cell would still be wrong. `confirmed`, and the note says
       so;
    4. else the first claim that names no decision: a step of the build
       was changed, and no decision explains the cell;
    5. else the first claim, not confirmed: a claim that failed when it was
       run. Read it as "no owner was found", not as an owner.

The owning claim, and with it the layer, is the first claim from the far
end that names one of the owning decisions.

Without a function to build again (`rebuild`), the owner is the first
claim and nothing is confirmed.

An axis that is not the gold axis (section 9.2, structure) is walked and
run the same way. The columns of a table are the groups of a grouping: the
values its variable has on the records of the analysis set. So the columns
rest on data as well, on the ADaM columns that the analyses of the output
read as a grouping or as an analysis set, and a treatment label that a
decision writes in another way owns the axis at L4. The rows of the tables
of this slice are listed by the layout and rest on no data.

Elements of a wrong cell that differ beyond the first of the owning claim
are kept in `also`. One owner per cell is the rule of section 9.4.
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


@dataclass
class _Claim:
    """What one layer says of a wrong cell or axis, before it is run."""

    layer: str
    element: str | None
    decisions: tuple[Key, ...] = ()
    also: tuple[str, ...] = ()
    note: str = ""


def _reaches(walk: _Walk, path) -> bool:
    """Whether something above the display reaches a cell: a result it shows has
    another value in the candidate or is not there, or a group that a result
    belongs to is defined in another way (its name, its condition)."""
    gold, candidate = walk.gold, walk.candidate
    for key in path.ard:
        if key in walk.ard:
            return True
        row = gold.ard.get(key) or {}
        number = 1
        while f"group{number}_groupingId" in row:
            group = (row[f"group{number}_groupingId"], row.get(f"group{number}_groupId"))
            if group[1] is not None and gold.groups.get(group) != candidate.groups.get(group):
                return True
            number += 1
    return False


def _layout_claim(walk: _Walk, unit: str | None, always: bool) -> _Claim | None:
    ours = walk.gold.layouts.get(unit) or {}
    theirs = walk.candidate.layouts.get(unit) or {}
    parts = [f"layout:{unit}/{part}" for part in ours if ours[part] != theirs.get(part)]
    if not parts and not always:
        return None
    return _Claim("L7", parts[0] if parts else None, walk.deciders(set(parts)), tuple(parts[1:]),
                  "" if parts else "the layouts are the same: the text was changed")


def _cell_claims(walk: _Walk, machine: Machine, wrong: WrongCell) -> list[_Claim]:
    """The claims on a wrong cell, the far end first."""
    gold, candidate = walk.gold, walk.candidate
    unit = gold.outputs.get(wrong.output)
    if not candidate.ok:
        return [_Claim("build", candidate.failure,
                       _stopped(machine, walk, str(candidate.failure), unit))]
    if wrong.output in candidate.not_produced:
        reason = candidate.not_produced[wrong.output]
        return [_Claim("build", reason, _stopped(machine, walk, reason, unit))]
    path = gold.paths.get(wrong.cell)
    if path is None or walk.gold_event is None:
        return [_Claim("L7", None, note="the gold cell has no path")]
    claims: list[_Claim] = []
    if _reaches(walk, path):
        # L4: the ADaM columns the analyses of the cell read, and what those derive from.
        read = {f"adam:{dataset}.{variable}" for analysis_id in path.analyses
                for _, dataset, variable in ars.reads(walk.gold_event, analysis_id, SUBJECT_KEY)}
        data = _other_data(walk, read)
        if data is not None:
            claims.append(_Claim("L4", *data))
        # L5: the analyses, with what their definitions name.
        other_parts: list[str] = []
        for analysis_id in path.analyses:
            ours = analysis_parts(walk.gold_event, analysis_id)
            theirs = analysis_parts(walk.candidate_event, analysis_id)
            other_parts += [name for name in ours if ours[name] != theirs.get(name)]
        if other_parts:
            other_parts = list(dict.fromkeys(other_parts))
            claims.append(_Claim("L5", other_parts[0], walk.deciders(set(other_parts)),
                                 tuple(other_parts[1:])))
        # L6: the results of the cell.
        other_results = [key for key in path.ard if key in walk.ard]
        if other_results:
            claims.append(_Claim("L6", other_results[0], (), tuple(other_results[1:]),
                                 f"the result is {walk.ard[other_results[0]]} in the candidate"))
    layout = _layout_claim(walk, unit, always=not claims)
    if layout is not None:
        claims.append(layout)
    return claims


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
    note: str = ""

    @property
    def unit(self) -> str | None:
        return self.decisions[0][1] if self.decisions else None


def _axis_claims(walk: _Walk, output: str, axis: str) -> list[_Claim]:
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
    claims: list[_Claim] = []
    if axis == "columns" and walk.gold_event is not None:
        read = {f"adam:{dataset}.{variable}" for analysis_id in names
                if analysis_id in walk.gold_event.analyses
                for role, dataset, variable in ars.reads(walk.gold_event, analysis_id,
                                                         SUBJECT_KEY)
                if role in ("grouping", "set")}
        data = _other_data(walk, read)
        if data is not None:
            claims.append(_Claim("L4", *data))
    parts: list[str] = []
    for analysis_id in names:
        ours = analysis_parts(walk.gold_event, analysis_id)
        theirs = analysis_parts(walk.candidate_event, analysis_id)
        parts += [name for name in {**ours, **theirs} if ours.get(name) != theirs.get(name)]
    if parts:
        parts = list(dict.fromkeys(parts))
        claims.append(_Claim("L5", parts[0], walk.deciders(set(parts)), tuple(parts[1:])))
    part = f"layout:{unit}/{axis}"
    ours, theirs = gold.layouts.get(unit) or {}, candidate.layouts.get(unit) or {}
    if ours.get(axis) != theirs.get(axis):
        claims.append(_Claim("L7", part, walk.deciders({part})))
    return claims or [_Claim("L7", None)]


class _Runs:
    """The candidate built again with some of its decisions at their gold values."""

    def __init__(self, gold: Build, candidate: Build, rebuild: Callable[[list[dict]], Build]):
        self.gold, self.candidate, self.rebuild = gold, candidate, rebuild
        self._tables: dict[tuple[tuple[Key, ...], str], object] = {}
        self._wanted = {output: table_of(grid) for output, grid in gold.grids.items()}

    def _table(self, decisions: tuple[Key, ...], output: str):
        name = (tuple(sorted(decisions)), output)
        if name not in self._tables:
            chosen = set(decisions)
            records = [r for r in self.candidate.records if (r["id"], r["unit"]) not in chosen]
            for key in decisions:
                value = self.gold.value(key)
                if value is not None:
                    records.append({"id": key[0], "unit": key[1], "value": value})
            order = {(r["id"], r["unit"]): n for n, r in enumerate(self.gold.records)}
            records.sort(key=lambda r: order.get((r["id"], r["unit"]), len(order)))
            grid = self.rebuild(records).grids.get(output)
            self._tables[name] = None if grid is None else table_of(grid)
        return self._tables[name]

    def cell(self, decisions: tuple[Key, ...], wrong: WrongCell) -> bool:
        """With these decisions at gold, the cell has the gold text."""
        table = self._table(decisions, wrong.output)
        found = None if table is None else table.cells.get((wrong.row, wrong.column))
        wanted = self._wanted[wrong.output].cells[(wrong.row, wrong.column)]["text"]
        return found is not None and found["text"] == wanted

    def axis(self, decisions: tuple[Key, ...], output: str, axis: str) -> bool:
        """With these decisions at gold, the axis is the gold axis."""
        table = self._table(decisions, output)
        return table is not None and getattr(table, axis) == getattr(self._wanted[output], axis)


JOINT = "only with all of these decisions at their gold values: more than one difference reaches it"
HIDDEN = ("only with all of these decisions at their gold values: the difference of one is "
          "hidden by another wrong decision and shows in no artifact of the candidate")
REFUTED = "a claim that failed when it was run: the gold value does not give the gold text"
UNNAMED = ("found by running alone: no element that differs on the path is decided by a "
           "decision that differs")


def _widen(named: tuple[Key, ...], differing: list[Key],
           holds: Callable[[tuple[Key, ...]], bool]) -> tuple[Key, ...]:
    """Decisions that give the gold text, from the named ones on: one more wrong
    decision where that is enough; else they are added in their order until the text
    is the gold text. All the wrong decisions together are known to give it."""
    rest = [key for key in differing if key not in named]
    for key in rest:
        if holds((*named, key)):
            return (*named, key)
    chosen = list(named)
    for key in rest:
        chosen.append(key)
        if holds(tuple(chosen)):
            break
    return tuple(chosen)


def _fewest(chosen: tuple[Key, ...],
            holds: Callable[[tuple[Key, ...]], bool]) -> tuple[Key, ...]:
    """Of decisions that give the gold text together: those that are needed. Each is
    taken out, the display's end first, and stays out when the rest still gives it."""
    kept = list(chosen)
    for key in reversed(chosen):
        fewer = tuple(k for k in kept if k != key)
        if fewer and holds(fewer):
            kept = list(fewer)
    return tuple(kept)


def _settle(claims: list[_Claim], differing: list[Key],
            holds: Callable[[tuple[Key, ...]], bool] | None,
            ) -> tuple[_Claim, tuple[Key, ...], bool | None, str]:
    """The claim that owns, the decisions it needs, whether it was confirmed, a note."""
    first = claims[0]
    if holds is None:
        return first, first.decisions, None, first.note
    decided = [claim for claim in claims if claim.decisions]
    named = tuple(dict.fromkeys(key for claim in decided for key in claim.decisions))

    def owning(chosen: tuple[Key, ...]) -> _Claim:
        return next((claim for claim in decided if set(claim.decisions) & set(chosen)),
                    decided[0] if decided else first)

    for key in named:
        if holds((key,)):
            return owning((key,)), (key,), True, ""
    if len(named) > 1 and holds(named):
        chosen = _fewest(named, holds)
        return owning(chosen), chosen, True, JOINT
    if differing and holds(tuple(differing)):
        # Decisions own it, and the claims do not name them all.
        chosen = _fewest(_widen(named, differing, holds), holds)
        return owning(chosen), chosen, True, HIDDEN if decided else UNNAMED
    unnamed = [claim for claim in claims if not claim.decisions]
    if unnamed:
        return unnamed[0], (), None, unnamed[0].note
    return decided[0], decided[0].decisions, False, REFUTED


def attribute(machine: Machine, gold: Build, candidate: Build, wrong: list[WrongCell],
              axes: list[tuple[str, str]] | None = None,
              rebuild: Callable[[list[dict]], Build] | None = None,
              ) -> tuple[list[Owner], list[AxisOwner]]:
    """The owner of every wrong cell of a candidate build, against the gold build
    of the same dataset; and of every axis that is not the gold axis.

    `axes` lists (output, `rows` or `columns`) for the outputs that were
    produced with another axis. `rebuild` builds a decision vector on the
    dataset of the two builds, with whatever was planted in the candidate's
    build: with it every claim is run, and an owner is confirmed or not.
    """
    walk = _prepare(machine, gold, candidate)
    runs = None if rebuild is None else _Runs(gold, candidate, rebuild)
    owners = []
    for cell in wrong:
        claims = _cell_claims(walk, machine, cell)
        holds = None if runs is None else (lambda keys, cell=cell: runs.cell(keys, cell))
        claim, decisions, confirmed, note = _settle(claims, walk.differing, holds)
        others = tuple(c.element for c in claims if c is not claim and c.element)
        owners.append(Owner(cell.output, cell.cell, cell.row, cell.column, claim.layer,
                            claim.element, decisions, (*claim.also, *others), confirmed, note))
    found = []
    for output, axis in axes or []:
        claims = _axis_claims(walk, output, axis)
        holds = None if runs is None else (
            lambda keys, output=output, axis=axis: runs.axis(keys, output, axis))
        claim, decisions, confirmed, note = _settle(claims, walk.differing, holds)
        found.append(AxisOwner(output, axis, claim.layer, claim.element, decisions, confirmed,
                               note))
    return owners, found


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
