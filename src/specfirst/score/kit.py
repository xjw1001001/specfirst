"""A generated kit as a case of the scorer, and a set of kits scored (PLAN.md sections
8 and 9; docs/decisions/ADR-005.md, part read-1a; docs/decisions/ADR-007.md).

A kit of gen-2a is a folder outside every checkout (docs/state/gen.md, "A
kit: what the folder holds"). The scorer reads from it:

    gold/decisions.jsonl        the gold decision records, with `identifiable`
    gold/docs/sap.md            the stated decisions in standard form; with
    inputs/house/STANDARD.md    the documents a citation may name
    gold/design.yaml            the arms of the protocol (ADR-007, decision 2)
    inputs/data/sdtm, twin/data/sdtm        the two datasets
    gold/grid, gold/ard, gold/data/adam     and the same below twin/gold:
                                the gold the kit was written with
    gold/identifiability.json   the matrix of the twin

Gold is not read from the files: the scorer builds the gold decisions on
each dataset with the functions that built the kit, and compares the
candidate with that build. `gold_problems` holds the build against the
files. If they differ, the kit or the scorer is wrong, and no score counts.

The matrix. A decision that the matrix marks `unseparated` cannot be scored
by the table of the twin: its values are compared (section 9.3; ADR-007,
"The owner's answer on decision 6"). A planted wrong value of such a
decision is `silent` (specfirst.score.defects). The scorer finds that by
building; `matrix_problems` holds what it finds against the matrix of the
kit, pair by pair. A planted value that the matrix does not hold as a pair
(a slot of the gold alternative, as a window one day longer) is not held
against it.

The sweep. The matrix of a kit is a list of planted defects that the kit
itself vouches for: every decision of the slice, read as each other value
the matrix holds, with the claim whether the twin shows it and in how many
cells. `sweep` scores each of them as a candidate of its own (the gold
decisions through the parser, one value changed) and asks of the scorer:

- the reading score has exactly that decision wrong;
- the build score of the twin falls exactly when the matrix says
  `separated`, and where the two axes of the twin are the gold axes, in as
  many cells as the matrix counts;
- every wrong cell and every axis that is not the gold axis, on either
  dataset, has an owner, the changed decision, at the layer where that
  decision acts (`OWNING_LAYER`);
- a value that shows nowhere is reported as silent.

With one wrong decision an owner has no other decision to name, and the
candidate with that decision at its gold value is gold: "confirmed" cannot
fail there. So the sweep goes on to pairs: a module decision and a table
decision of the kit's own matrix, both wrong at once. What each does alone
is known from the first pass, cell by cell, and the owner of every wrong
cell of the pair is held against it: the one decision that changes the
cell alone; both, where each changes it; never a claim that failed.

The files of a kit are held against the hashes of its manifest before
anything is read (rule R3): a decision record whose class or
`identifiable` was changed would be scored in another way, and the gold
check does not see that.

A set. `score_set` scores the kits of a folder: the gold check, the parser
control in both stages, the standard alone in both stages (reported: it
decides nothing), the planted defects of section 9.5 and the sweep. It
passes when on every kit the gold check and the control hold, no planted
defect fails and the sweep has no problem, and when every defect that
applies to the slice is detected and attributed on at least one kit.
"""

from __future__ import annotations

import copy
import dataclasses
import json
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from specfirst.compile import house as houses
from specfirst.compile.catalog import Catalog
from specfirst.gen import decisions, probes, verify
from specfirst.gen import design as designs
from specfirst.gen import gold as kitgold
from specfirst.gen import kits as genkits
from specfirst.machine.canonical import read_jsonl
from specfirst.score import attribute, build, defects, report, scorer
from specfirst.score.candidate import Data, Key, Machine
from specfirst.score.reading import Documents, same_value

Out = Callable[[str], None]
DATASETS = tuple(kitgold.PLACES)  # visible, twin


class KitError(RuntimeError):
    """The folder is not a kit the scorer can read."""


@dataclass(frozen=True)
class Kit:
    """What the scorer reads of a kit folder."""

    folder: Path
    manifest: dict
    design: dict
    records: list[dict]  # gold/decisions.jsonl
    matrix: dict  # gold/identifiability.json
    parameters: dict  # the slot values the probes of the study are built around
    documents: Documents
    data: dict[str, Data]  # visible, twin -> the SDTM tables
    grids: dict[str, dict]  # dataset -> output ID -> the gold grid as written
    ard: dict[str, dict[str, dict]]  # dataset -> the gold ARD rows by ID, as written
    adam: dict[str, dict]  # dataset -> ADaM dataset -> the gold table as written

    @property
    def id(self) -> str:
        return str(self.manifest["id"])

    @property
    def units(self) -> tuple[str, ...]:
        return tuple(self.manifest["units"])


def load(folder: Path) -> Kit:
    """Read a kit folder. Raises `KitError`."""
    import pyarrow.parquet as pq

    try:
        manifest = genkits.read_manifest(folder)
        if manifest.get("kit") != genkits.FORMAT or manifest.get("slice") != genkits.SLICE:
            raise ValueError(f"kit format {manifest.get('kit')!r}, slice "
                             f"{manifest.get('slice')!r}; the scorer reads format "
                             f"{genkits.FORMAT} of the slice {genkits.SLICE}")
        drift = genkits.hash_differences(manifest.get("files") or {}, genkits.all_files(folder))
        if drift:
            raise ValueError(f"{len(drift)} files are not the files of {genkits.MANIFEST}, "
                             f"for example {drift[0]}")
        records = genkits.read_decisions(folder)
        design = designs.load(folder / "gold" / "design.yaml")
        with open(folder / genkits.IDENTIFIABILITY, encoding="ascii") as handle:
            matrix = json.load(handle)
        documents = Documents({
            decisions.DOCUMENT: (folder / genkits.DOCUMENT).read_text(encoding="ascii"),
            houses.DOCUMENT_ID: (folder / kitgold.HOUSE / "STANDARD.md").read_text(
                encoding="ascii")})
        data, grids, ard, adam = {}, {}, {}, {}
        for which, (sdtm, place) in kitgold.PLACES.items():
            data[which] = Data(f"{manifest['id']}/{which}", sdtm={
                path.stem: pq.read_table(path)
                for path in sorted((folder / sdtm).glob("*.parquet"))})
            grids[which] = {}
            for path in sorted((folder / place / kitgold.GRID).glob("*.json")):
                if not path.name.endswith(".shell.json"):
                    with open(path, encoding="ascii") as handle:
                        grids[which][path.name[:-len(".json")]] = json.load(handle)
            ard[which] = {row["id"]: row for row in read_jsonl(
                folder / place / kitgold.ARD / f"{kitgold.EVENT}.jsonl")}
            adam[which] = {path.stem.upper(): pq.read_table(path) for path in sorted(
                (folder / place / kitgold.ADAM).glob("*.parquet"))}
    except (OSError, ValueError, KeyError) as error:
        raise KitError(f"{folder}: not a kit of the slice: {error!r}") from error
    if not all(data[which].sdtm and grids[which] for which in DATASETS):
        raise KitError(f"{folder}: a dataset of the kit has no SDTM or no gold grid")
    return Kit(folder, manifest, design, records, matrix,
               probes.Parameters.of(design).as_record(), documents, data, grids, ard, adam)


def machine_of(root: Path, kit: Kit | None = None) -> Machine:
    """A machine that builds the ADaM datasets a kit of the slice builds."""
    datasets = tuple(kit.manifest["datasets"]) if kit else kitgold.SLICE_DATASETS
    return Machine(root, datasets=datasets)


def options(kit: Kit, catalog: Catalog, key: Key) -> list[dict]:
    """The values the matrix of the kit changes a decision between: the gold value
    first (specfirst.gen.verify.options). Empty for a decision the kit does not make."""
    values = decisions.as_values(kit.records)
    if key[0] not in values or key[0] not in catalog.entries:
        return []
    return verify.options(catalog.entry(key[0]), kit.design, kit.parameters, values)


def case(kit: Kit, catalog: Catalog, stage: str = "C") -> scorer.Case:
    """The kit as a case. Stage C scores the units of the slice from SDTM; stage T
    the table decisions alone, on the ADaM of gold (ADR-005, decision 2)."""
    units = kit.units if stage == "C" else tuple(
        unit for unit in kit.units if catalog.units[unit].kind == "table_family")
    return scorer.Case(
        id=kit.id, units=units, gold=kit.records,
        arms=lambda records: kitgold.arms_of(kit.design, decisions.as_values(records)),
        data=dict(kit.data), documents=kit.documents, stage=stage,
        standard_form=decisions.DOCUMENT,
        variants=lambda key: options(kit, catalog, key)[1:])


# ---- the gold of the kit, built again ----------------------------------------------------


def gold_problems(machine: Machine, kit: Kit) -> list[str]:
    """Why the scorer's build of the gold decisions is not the gold the kit was
    written with: the grid as a whole (IDs, texts, the ARD rows of every cell),
    every result, every value of every ADaM column."""
    problems = []
    for which in DATASETS:
        try:
            _, gold = scorer.staged(machine, case(kit, machine.catalog), which)
        except scorer.ScoreError as error:
            problems.append(str(error))
            continue
        for output in sorted(set(kit.grids[which]) | set(gold.grids)):
            ours, theirs = gold.grids.get(output), kit.grids[which].get(output)
            if ours == theirs:
                continue
            found = verify.differences(verify.table_view(ours), verify.table_view(theirs),
                                       ("the scorer's build", "the kit"))
            problems += [f"{which}, {output}: {line}" for line in found[:5]] or [
                f"{which}, {output}: the same texts, and the grids differ in an ID, a title, "
                "a footnote or the ARD rows of a cell"]
        differing = build.ard_differences(kit.ard[which], gold.ard)
        problems += [f"{which}: result {key}: {state} in the scorer's build"
                     for key, state in list(differing.items())[:5]]
        columns = {**build.adam_differences(kit.adam[which], gold.adam),
                   **build.adam_differences(gold.adam, kit.adam[which])}
        problems += [f"{which}: {column}: {count} records differ"
                     for column, count in list(sorted(columns.items()))[:5]]
    return problems


# ---- the matrix of the kit ---------------------------------------------------------------


def separated_in_matrix(kit: Kit, catalog: Catalog, key: Key, value: dict) -> bool | None:
    """Whether the matrix of the kit says that the twin separates the gold value of a
    decision from another value. None: the matrix holds no such pair."""
    item = next((d for d in kit.matrix["decisions"] if (d["id"], d["unit"]) == key), None)
    choices = options(kit, catalog, key)
    match = next((choice for choice in choices[1:] if same_value(choice, value)), None)
    if item is None or match is None:
        return None
    label = verify.label(match, choices)
    pair = next((p for p in item["pairs"] if p["gold"] and p["second"] == label), None)
    return None if pair is None else bool(pair["separated"])


def matrix_problems(kit: Kit, catalog: Catalog,
                    outcomes: list[defects.Outcome]) -> tuple[list[str], dict[str, str]]:
    """Where the scorer's builds of the planted decisions and the matrix of the kit
    disagree about the twin; and per defect what the matrix says of its pair."""
    problems, said = [], {}
    for outcome in outcomes:
        planted = outcome.planted
        if planted is None or planted.decision is None or planted.value is None \
                or outcome.result is None or outcome.defect.dimension:
            continue
        expected = separated_in_matrix(kit, catalog, planted.decision, planted.value)
        shows = not outcome.result.builds["twin"].perfect
        if expected is None:
            said[outcome.defect.id] = "the matrix holds no such pair"
            continue
        said[outcome.defect.id] = ("the matrix: separated on the twin" if expected
                                   else "the matrix: unseparated on the twin")
        if expected != shows:
            problems.append(
                f"{outcome.defect.id}, {planted.decision[0]}: the matrix of the kit says the "
                f"twin {'separates' if expected else 'does not separate'} this value from "
                f"gold; the scorer's builds on the twin {'differ' if shows else 'are the same'}")
    return problems, said


# The layer at which a wrong value of a decision owns its cells: what the decision
# sets. A module decision writes ADaM columns (L4). Five decisions set elements of
# the ARS file: which output, which analysis set, which rows, the total column, and
# the treatment variable the table groups by (L5). Three set parts of the layout
# only (L7). gold/spec/compile.json of a kit lists the same per decision (`binds`,
# `layout`); tests/unit/test_score_kit.py holds this table against it.
OWNING_LAYER = {
    **dict.fromkeys(("trt.planned.source", "trt.actual.source", "trt.start.source",
                     "trt.end.source", "trt.date.imputation", "date.studyday.origin",
                     "pop.randomized.rule", "pop.safety.rule", "pop.efficacy.rule",
                     "disp.status.record", "ae.start.imputation", "ae.teae.start",
                     "ae.teae.end", "ae.related.values"), "L4"),
    **dict.fromkeys(("pop.safety.grouping", "tfl.output.include", "tfl.population",
                     "tfl.columns.total", "tfl.ae.summary.rows"), "L5"),
    **dict.fromkeys(("tfl.columns.arms", "tfl.percent.format", "tfl.rounding.rule"), "L7"),
}
# How many pairs of two wrong decisions a kit is swept with: so many module
# decisions that its twin separates, each with so many table decisions.
PAIR_MODULES, PAIR_TABLES = 4, 3


@dataclass
class Sweep:
    """Every other value of every decision in the matrix of a kit, scored alone; and
    pairs of a module decision with a table decision, both wrong."""

    values: int = 0
    decisions: int = 0
    shown: int = 0  # the twin shows it, as the matrix says
    visible_only: int = 0  # the visible data show it and the twin does not
    silent: int = 0  # no dataset shows it, as the matrix says of the twin
    cells: int = 0  # wrong cells and axes, each with the changed decision as its owner
    counted: int = 0  # values whose wrong cells on the twin are held against the matrix
    layers: dict[str, set[str]] = field(default_factory=dict)  # decision -> owning layers
    pairs: int = 0
    pair_cells: int = 0  # wrong cells and axes of the pairs
    one_cause: int = 0  # owned by the one decision that changes it alone
    both_causes: int = 0  # each decision changes it alone: owned by both
    together: int = 0  # wrong only with both wrong: owned by one of them
    problems: list[str] = field(default_factory=list)


def _where(owner) -> str:
    return getattr(owner, "cell", None) or f"axis {getattr(owner, 'axis', '')}"


def _other_axes(score: build.BuildScore) -> list[tuple[str, str]]:
    """The axes of the produced outputs that are not the gold axes: (output, axis)."""
    return [(output.output, axis) for output in score.outputs if output.produced
            for axis, equal in (("rows", output.rows_equal), ("columns", output.columns_equal))
            if not equal]


def _marks(result: scorer.Result) -> dict[str, set]:
    """Per dataset, what is wrong: the wrong cells as (row, column), the axes as
    (output, axis)."""
    return {which: {(cell.row, cell.column) for cell in score.wrong()} | set(_other_axes(score))
            for which, score in result.builds.items()}


def _owner_marks(result: scorer.Result, which: str) -> dict:
    found = {(owner.row, owner.column): owner for owner in result.owners[which]}
    found.update({(axis.output, axis.axis): axis for axis in result.axes[which]})
    return found


def sweep(machine: Machine, kit: Kit) -> Sweep:
    """Score every pair of the matrix of the kit as a candidate with one wrong decision,
    then pairs of two wrong decisions."""
    catalog = machine.catalog
    on = case(kit, catalog)
    records, documents = scorer.control_records(machine, on)
    found = Sweep()
    alone: dict[Key, tuple[dict, dict[str, set]]] = {}  # separated on the twin: value, marks

    def scored(changes: dict[Key, dict]) -> scorer.Result:
        candidate = [{**r, "value": changes[(r["id"], r["unit"])]}
                     if (r["id"], r["unit"]) in changes else r for r in records]
        return scorer.run(machine, on, candidate, arm="sweep", documents=documents)

    for item in kit.matrix["decisions"]:
        key = (item["id"], item["unit"])
        choices = options(kit, catalog, key)
        found.decisions += 1
        for value in choices[1:]:
            label = verify.label(value, choices)
            name = f"{key[0]} = {label}"
            pair = next((p for p in item["pairs"] if p["gold"] and p["second"] == label), None)
            if pair is None:
                found.problems.append(f"{name}: the matrix holds no pair of gold with it")
                continue
            found.values += 1
            result = scored({key: value})
            wrong = [score.key for score in result.reading.wrong()]
            if wrong != [key]:
                found.problems.append(f"{name}: the reading score has wrong by value: "
                                      f"{', '.join(k[0] for k in wrong) or 'nothing'}")
            score = result.builds["twin"]
            twin = not score.perfect
            if twin != bool(pair["separated"]):
                found.problems.append(
                    f"{name}: the matrix says the twin "
                    f"{'separates' if pair['separated'] else 'does not separate'} it; the "
                    f"scorer's builds on the twin {'differ' if twin else 'are the same'}")
            elif not _other_axes(score) and score.produced == score.in_gold:
                # The matrix counts the cells of two grids by their place on the page;
                # with the gold axes that is the count by row and column.
                found.counted += 1
                if len(score.wrong()) != pair["cells"]:
                    found.problems.append(f"{name}: the matrix counts {pair['cells']} changed "
                                          f"cells on the twin, the scorer {len(score.wrong())}")
            owned = 0
            for which, marks in _marks(result).items():
                owners = _owner_marks(result, which)
                if set(owners) != marks or len(result.owners[which]) + len(
                        result.axes[which]) != len(marks):
                    found.problems.append(
                        f"{name}: {which}: {len(marks)} wrong cells and axes have "
                        f"{len(result.owners[which]) + len(result.axes[which])} owners")
                for owner in owners.values():
                    if owner.decisions != (key,):
                        names = ", ".join(k[0] for k in owner.decisions) or "no decision"
                        found.problems.append(f"{name}: {which}, {_where(owner)}: owned by "
                                              f"{names} at layer {owner.layer}")
                    elif owner.note == attribute.UNNAMED:
                        found.problems.append(
                            f"{name}: {which}, {_where(owner)}: the decision owns it by "
                            "running alone: no element that differs on the path is decided "
                            "by it")
                    elif owner.layer != OWNING_LAYER.get(key[0]):
                        found.problems.append(
                            f"{name}: {which}, {_where(owner)}: owned at layer {owner.layer}; "
                            f"the decision acts at {OWNING_LAYER.get(key[0])}")
                    found.layers.setdefault(key[0], set()).add(owner.layer)
                owned += len(owners)
            found.cells += owned
            if twin:
                found.shown += 1
                if key not in alone:
                    alone[key] = (value, _marks(result))
            elif owned:
                found.visible_only += 1
            else:
                found.silent += 1
                if key not in result.silent:
                    found.problems.append(f"{name}: shown by no cell, and not reported as "
                                          "silent")

    modules = [key for key in alone if catalog.units[key[1]].kind != "table_family"]
    tables = [key for key in alone if catalog.units[key[1]].kind == "table_family"]
    for first in modules[:PAIR_MODULES]:
        for second in tables[:PAIR_TABLES]:
            found.pairs += 1
            name = f"{first[0]} with {second[0]}"
            result = scored({first: alone[first][0], second: alone[second][0]})
            if sorted(score.key for score in result.reading.wrong()) != sorted([first, second]):
                found.problems.append(f"{name}: the reading score does not have these two, "
                                      "and only these, wrong by value")
            for which, marks in _marks(result).items():
                owners = _owner_marks(result, which)
                if set(owners) != marks:
                    found.problems.append(f"{name}: {which}: {len(marks)} wrong cells and "
                                          f"axes have {len(owners)} owners")
                for mark, owner in owners.items():
                    found.pair_cells += 1
                    by_first = mark in alone[first][1][which]
                    by_second = mark in alone[second][1][which]
                    if by_first and by_second:
                        wanted, kind = [{first, second}], "both_causes"
                    elif by_first or by_second:
                        wanted, kind = [{first if by_first else second}], "one_cause"
                    else:
                        wanted, kind = [{first}, {second}], "together"
                    if owner.confirmed is not True or set(owner.decisions) not in wanted \
                            or owner.note == attribute.UNNAMED:
                        names = ", ".join(k[0] for k in owner.decisions) or "no decision"
                        found.problems.append(
                            f"{name}: {which}, {_where(owner)}: owned by {names} at layer "
                            f"{owner.layer}, confirmed {owner.confirmed}; alone, it is wrong "
                            f"under {first[0] if by_first else ''}"
                            f"{' and ' if by_first and by_second else ''}"
                            f"{second[0] if by_second else ''}"
                            f"{'neither' if not (by_first or by_second) else ''}")
                    else:
                        setattr(found, kind, getattr(found, kind) + 1)
    return found


# ---- one kit -----------------------------------------------------------------------------


@dataclass
class KitScore:
    kit: Kit
    gold: list[str] = field(default_factory=list)  # gold_problems
    control: dict[str, scorer.Result] = field(default_factory=dict)  # stage -> arm C
    standard: dict[str, scorer.Result] = field(default_factory=dict)  # stage -> arm S
    outcomes: list[defects.Outcome] = field(default_factory=list)
    matrix: list[str] = field(default_factory=list)  # matrix_problems
    sweep: Sweep = field(default_factory=Sweep)

    @property
    def control_holds(self) -> bool:
        return bool(self.control) and all(result.perfect for result in self.control.values())

    @property
    def failed(self) -> list[defects.Outcome]:
        return [outcome for outcome in self.outcomes if outcome.state == "failed"]

    @property
    def passed(self) -> bool:
        return (not self.gold and self.control_holds and not self.failed and not self.matrix
                and not self.sweep.problems)


def build_line(result: scorer.Result) -> str:
    """The build scores of a result in one line per dataset, each with its denominators."""
    said = []
    for name, score in result.builds.items():
        cells = score.denominators()
        text = (f"{name}: produced {score.produced} of {score.in_gold}; cells correct "
                f"{score.correct} of {cells['shared_rows']}, {cells['produced']} and "
                f"{cells['all']}; strict {score.strict} of {score.in_gold}; lenient "
                f"{score.lenient} of {score.in_gold}")
        if not score.valid:
            text += f" (not valid: {str(score.failure)[:90]})"
        said.append(text)
    return "; ".join(said)


def reading_line(result: scorer.Result) -> str:
    read = result.reading
    marks = "; ".join(f"{name} {right} of {scored}" for name in ("value", "status", "quote",
                                                                 "span")
                      for right, scored in [read.total(name)])
    return f"{len(read.decisions)} decisions: {marks}"


def _cells(grids: dict[str, dict]) -> int:
    return sum(len(row["cells"]) for made in grids.values() for row in made["rows"])


def _owned(result: scorer.Result) -> str:
    """Per dataset: how many wrong cells and axes each layer and decision owns; a
    claim that failed when it was run is counted apart."""
    found = []
    for name in result.builds:
        counts: dict[tuple[str, str], int] = {}
        for owner in [*result.owners[name], *result.axes[name]]:
            names = ", ".join(k[0] for k in owner.decisions) or "no decision"
            layer = owner.layer if owner.confirmed is not False else "no owner found: " \
                + owner.layer
            counts[(layer, names)] = counts.get((layer, names), 0) + 1
        if counts:
            found.append(f"{name} owned by " + " and ".join(
                f"{layer} ({names}): {count}" for (layer, names), count in sorted(
                    counts.items())))
    return "; ".join(found)


def score_kit(machine: Machine, kit: Kit, out: Out, name: str = "") -> KitScore:
    """Score one kit: the gold check, arm C and arm S in both stages, the planted defects."""
    found = KitScore(kit)
    catalog = machine.catalog
    props = kit.manifest["properties"]
    out(f"kit {kit.id}{' (' + name + ')' if name else ''}, {kit.manifest['split']}: "
        f"{kit.manifest['study']['arms']} arms; {props['visible']['subjects']} subjects in the "
        f"visible data, {props['twin']['subjects']} in the twin; "
        f"{sum(1 for r in kit.records if r['unit'] in kit.units)} decisions of the slice, "
        f"{sum(1 for r in kit.records if r['unit'] in kit.units and r['status'] == 'stated')} "
        "stated")
    found.gold = gold_problems(machine, kit)
    if found.gold:
        for problem in found.gold:
            out(f"  problem: {problem}")
        out("  the scorer's build of the gold decisions is NOT the gold of the kit: nothing "
            "is scored")
        return found
    summary = kit.matrix["summary"]
    apart = [*summary["unseparated_not_read"], *summary["unseparated_read"]]
    out(f"  unseparated on the twin by the matrix of the kit, compared by value only: "
        f"{len(apart)}: {', '.join(apart) or 'none'}"
        + (f" (read by the table: {', '.join(summary['unseparated_read'])})"
           if summary["unseparated_read"] else ""))
    out("  gold: built again from the gold decisions, it is the gold of the kit on both "
        "datasets: " + "; ".join(
            f"{which} {_cells(kit.grids[which])} cells, {len(kit.ard[which])} results, "
            f"{sum(len(t.column_names) for t in kit.adam[which].values())} ADaM columns"
            for which in DATASETS))
    for stage in scorer.STAGES:
        on = case(kit, catalog, stage)
        result = found.control[stage] = scorer.control(machine, on)
        out(f"  arm C, stage {stage}: {reading_line(result)}; {build_line(result)}: "
            f"{'100%' if result.perfect else 'NOT 100%'}")
        if not result.perfect:
            for line in report.lines(result):
                out("    " + line)
    if not found.control_holds:
        out("  the control does not score 100%: no planted defect counts")
        return found
    for stage in scorer.STAGES:
        result = found.standard[stage] = scorer.standard_alone(machine, case(kit, catalog, stage))
        wrong = [item.key[0] for item in result.reading.wrong()]
        owned = _owned(result) if stage == "T" else ""
        out(f"  arm S, stage {stage}: {len(wrong)} of {len(result.reading.decisions)} decisions "
            f"to change ({', '.join(wrong) or 'none'}); {build_line(result)}"
            + (f"; {owned}" if owned else ""))
    on = case(kit, catalog)
    records, documents = scorer.control_records(machine, on)
    for defect in defects.DEFECTS:
        if defect.layer is not None:
            found.outcomes.append(defects.run_one(machine, on, defect, records, documents))
    found.matrix, said = matrix_problems(kit, catalog, found.outcomes)
    for outcome in found.outcomes:
        defect = outcome.defect
        head = f"  {defect.id} ({defect.layer}): {outcome.state}"
        if outcome.planted is None:
            out(f"{head}: {outcome.reason}")
            continue
        shows = "; ".join(f"{where} {what}" for where, what in outcome.shows.items())
        owned = _owned(outcome.result)
        out(f"{head}: {outcome.planted.what}. {shows}"
            + (f"; {owned}" if owned else "")
            + (f"; {said[defect.id]}" if defect.id in said else ""))
        for problem in outcome.problems:
            out(f"    problem: {problem}")
    for problem in found.matrix:
        out(f"  problem: {problem}")
    swept = found.sweep = sweep(machine, kit)
    out(f"  sweep of the matrix: {swept.values} other values of {swept.decisions} decisions, "
        f"each as the one wrong decision of a candidate: {swept.shown} shown on the twin and "
        f"{swept.silent} silent, as the matrix says; {swept.visible_only} shown on the visible "
        f"data only; {swept.cells} wrong cells and axes, each owned by the changed decision "
        f"at its layer; the cells of the twin counted against the matrix for {swept.counted} "
        "values")
    out(f"  sweep of pairs: {swept.pairs} candidates with a module decision and a table "
        f"decision wrong at once: {swept.pair_cells} wrong cells and axes; {swept.one_cause} "
        f"owned by the one decision that changes them alone, {swept.both_causes} by both "
        f"where each does, {swept.together} by one of the two where neither does alone; "
        f"{len(swept.problems)} problems in both sweeps")
    for problem in swept.problems:
        out(f"    problem: {problem}")
    return found


# ---- the checks of this module, on planted defects (rule R5) ------------------------------


def _without_statement(text: str, anchor: str) -> str:
    """A standard-form document without the paragraph of one anchor."""
    lines, kept, skipping = text.split("\n"), [], False
    for line in lines:
        if line.startswith(f"[{anchor}] "):
            skipping = True
        elif skipping and not line.strip():
            skipping = False
            continue
        if not skipping:
            kept.append(line)
    return "\n".join(kept)


def planted(machine: Machine, kit: Kit, scored: KitScore, out: Out) -> bool:
    """The three checks of a kit fail on what they are for.

    A gold grid with one other text; a document that lacks one statement;
    a matrix that says the opposite of one planted pair.
    """
    catalog = machine.catalog
    seen = True
    # 1. The gold check: one cell of the twin's grid file says something else.
    grids = copy.deepcopy(kit.grids)
    cell = next(iter(grids["twin"].values()))["rows"][0]["cells"][0]
    cell["text"] = cell["text"] + "9"
    found = gold_problems(machine, dataclasses.replace(kit, grids=grids))
    ok = any("twin" in problem and cell["text"] in problem for problem in found)
    out(f"  planted in the gold of the kit: the first cell of the twin's grid reads "
        f"{cell['text']!r}: the gold check fails: {'yes' if ok else 'NO'}")
    seen &= ok
    # 2. The control: the document lacks the statement of one stated decision of the slice.
    stated = next(r for r in kit.records if r["unit"] in kit.units and r["status"] == "stated")
    anchor = stated["citations"][0]["anchor"]
    text = _without_statement(kit.documents.texts[decisions.DOCUMENT], anchor)
    other = dataclasses.replace(kit, documents=Documents(
        {**kit.documents.texts, decisions.DOCUMENT: text}))
    try:
        result = scorer.control(machine, case(other, catalog))
        wrong = [item.key[0] for item in result.reading.wrong()]
        ok = not result.perfect and stated["id"] in wrong
        said = (f"the control is {'not ' if not result.perfect else ''}100%; wrong by value: "
                f"{', '.join(wrong) or 'none'}")
    except Exception as error:  # a parser that refuses the document has seen it too
        ok, said = True, f"the document is refused: {type(error).__name__}: {error}"
    out(f"  planted in the document: the statement [{anchor}] of {stated['id']} is taken out: "
        f"{said}: the control fails: {'yes' if ok else 'NO'}")
    seen &= ok
    # 3. The matrix: it says the opposite of one planted pair.
    target = next((o for o in scored.outcomes if o.planted is not None
                   and o.planted.decision is not None and o.planted.value is not None
                   and not o.defect.dimension and separated_in_matrix(
                       kit, catalog, o.planted.decision, o.planted.value) is not None), None)
    if target is None:
        out("  planted in the matrix: no planted decision of this kit is a pair of its matrix")
        return False
    matrix = copy.deepcopy(kit.matrix)
    choices = options(kit, catalog, target.planted.decision)
    label = verify.label(next(c for c in choices[1:] if same_value(c, target.planted.value)),
                         choices)
    for item in matrix["decisions"]:
        if (item["id"], item["unit"]) == target.planted.decision:
            for pair in item["pairs"]:
                if pair["gold"] and pair["second"] == label:
                    pair["separated"] = not pair["separated"]
    found, _ = matrix_problems(dataclasses.replace(kit, matrix=matrix), catalog, scored.outcomes)
    ok = any(target.defect.id in problem for problem in found)
    out(f"  planted in the matrix: the pair of {target.planted.decision[0]} with {label} says "
        f"the opposite: the comparison with the matrix fails: {'yes' if ok else 'NO'}")
    return seen and ok


# ---- a set of kits -----------------------------------------------------------------------


def folders(folder: Path) -> list[Path]:
    """The kit folders of a set, in their order."""
    return sorted(path.parent for path in folder.glob(f"*/{genkits.MANIFEST}"))


def score_set(root: Path, folder: Path, out: Out = print) -> bool:
    """Score every kit of a folder, and decide the gate of read-1a on them."""
    found = folders(folder)
    if not found:
        out(f"{folder}: no kit")
        return False
    machine = machine_of(root)
    scores = []
    for path in found:
        try:
            kit = load(path)
        except KitError as error:
            out(f"problem: {error}")
            return False
        scores.append(score_kit(machine, kit, out, path.name))
    out("")
    out("the checks on planted defects, on the first kit that passes:")
    first = next((score for score in scores if score.passed), None)
    checks = planted(machine, first.kit, first, out) if first else False
    if first is None:
        out("  no kit passes: nothing to plant in")
    out("")
    applies = [defect for defect in defects.DEFECTS if defect.layer is not None]
    out(f"planted defects on {len(scores)} kits: per defect, the kits by outcome")
    everywhere = True
    for defect in applies:
        states: dict[str, list[str]] = {}
        for score in scores:
            outcome = next((o for o in score.outcomes if o.defect.id == defect.id), None)
            states.setdefault(outcome.state if outcome else "not scored", []).append(
                score.kit.id)
        shown = len(states.get("passed", []))
        everywhere &= shown > 0
        out(f"  {defect.id} ({defect.layer}): detected and attributed on {shown} kits; "
            + "; ".join(f"{state} on {len(kits)}" for state, kits in sorted(states.items())
                        if state != "passed"))
    gold = sum(1 for score in scores if not score.gold)
    control = sum(1 for score in scores if score.control_holds)
    failed = [(score.kit.id, outcome.defect.id) for score in scores for outcome in score.failed]
    matrix = [problem for score in scores for problem in score.matrix]
    swept = [score.sweep for score in scores]
    layers: dict[str, set[str]] = {}
    for one in swept:
        for name, where in one.layers.items():
            layers.setdefault(name, set()).update(where)
    out(f"sweep of the matrices: {sum(one.values for one in swept)} other values, each as the "
        f"one wrong decision of a candidate: {sum(one.shown for one in swept)} shown on the "
        f"twin, {sum(one.visible_only for one in swept)} on the visible data only, "
        f"{sum(one.silent for one in swept)} silent; {sum(one.cells for one in swept)} wrong "
        "cells and axes owned by the changed decision at its layer; the cells of the twin "
        f"counted against the matrix for {sum(one.counted for one in swept)} values")
    out(f"sweep of pairs: {sum(one.pairs for one in swept)} candidates with two wrong "
        f"decisions: {sum(one.pair_cells for one in swept)} wrong cells and axes; "
        f"{sum(one.one_cause for one in swept)} owned by the one decision that changes them "
        f"alone, {sum(one.both_causes for one in swept)} by both, "
        f"{sum(one.together for one in swept)} by one of the two where neither does alone")
    out(f"problems of the sweeps: {sum(len(one.problems) for one in swept)}")
    out("  the layer at which each decision owns its cells: " + "; ".join(
        f"{name} {', '.join(sorted(where))}" for name, where in sorted(layers.items())))
    out(f"gold built again is the gold of the kit: {gold} of {len(scores)} kits")
    out(f"parser control 100% in both stages: {control} of {len(scores)} kits")
    out(f"planted defects that failed: {len(failed)}"
        + ("" if not failed else ": " + ", ".join(f"{d} on {k}" for k, d in failed)))
    out(f"disagreements with the matrices of the kits: {len(matrix)}")
    out(f"every defect that applies is detected and attributed on at least one kit: "
        f"{'yes' if everywhere else 'NO'}")
    out(f"the checks fail on their planted defects: {'yes' if checks else 'NO'}")
    passed = (gold == control == len(scores) and not failed and not matrix and everywhere
              and checks and not any(one.problems for one in swept))
    out(f"kits: {'PASS' if passed else 'FAIL'}")
    return passed
