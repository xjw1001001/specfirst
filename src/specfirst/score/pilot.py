"""The pilot, report only (ADR-005, decision 5): arm S, stage T, on CDISCPILOT01.

The adverse event summary is built from the house standard alone on the
reference ADaM of the pilot, and held against the results that CDISC's ARS
example "Common Safety Displays" embeds for the analyses of its adverse
event summary (output Out14-3-1-1). Nothing is tuned on the pilot (PLAN.md
section 6.1): this module only reports.

The key. The example formats results; the kit's layout of real-3a
(kits/cdiscpilot01/gold/layout/Out14-3-1-1.yaml) says which results share a
cell. The key is that grid with the example's `formattedValue` in every
cell. The data are the two reference datasets the kit pins, read from the
fetch cache after their SHA-256 is checked (rule R3).

The crosswalk. A row of the key and a row of the house table are the same
row when they count the same events. `ROWS` maps each analysis of the
example to the row code of the catalog entry tfl.ae.summary.rows whose
data subset says the same thing; three analyses of the example have no
such code. The key's rows take the house labels through it, so that the
scores of ADR-005, decision 4 compare like with like. This mapping is a
reading of two public definitions and is listed in the report.

What cannot be built. Stage T is given ADaM, so a variable the house
template reads and the reference ADaM does not have cannot be derived. The
analyses that read it are left out, their rows count as rows the candidate
lacks, and the variable is listed with the decision that writes it in the
house standard.

Explaining a difference (section 4.8, `rule_choice`). A cell that differs
is explained by a decision when the table built with another value of that
one decision has the key's text there; every alternative of the seven
table decisions is tried, each with the examples of its slots. An axis is
explained the same way. A cell of the key that arm S does not have is in
one of two states: its row needs a variable that only a decision outside
stage T writes (`open`: named with that decision), or the catalog has no
row for it (`no_row`: a gap of the catalog, which no decision explains).
Anything else is `unexplained`.

Not compared: titles, footnotes and the header of the row labels. The house
layout has no text for the latter; the key's header row takes an empty
label so that the counts under the column headers are compared.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from specfirst import kit as kits
from specfirst.compile import checks, compiler
from specfirst.machine import ars, results
from specfirst.machine import grid as grids
from specfirst.machine import layout as layouts
from specfirst.machine.canonical import sha256_file
from specfirst.paths import cache_dir
from specfirst.score import build
from specfirst.score.candidate import SUBJECT_KEY, Build, Data, Hooks, Key, Machine
from specfirst.score.display0 import Arm

KIT = "cdiscpilot01"
OUTPUT, UNIT, OUR_OUTPUT = "Out14-3-1-1", "tfl-ae-summary", "Out_AESUM"
DATASETS = ("ADSL", "ADAE")
# The analyses of the example's adverse event summary, and the row of the house
# table that counts the same events (None: the catalog has no such row).
ROWS = {
    "An07_01_TEAE_Summ_ByTrt": "ANY",
    "An07_02_RelTEAE_Summ_ByTrt": "RELATED",
    "An07_03_SerTEAE_Summ_ByTrt": "SERIOUS",
    "An07_04_RelSerTEAE_Summ_ByTrt": None,
    "An07_05_TEAELd2Dth_Summ_ByTrt": "FATAL",
    "An07_06_RelTEAELd2Dth_Summ_ByTrt": None,
    "An07_07_TEAELd2DoseMod_Summ_ByTrt": None,
    "An07_08_TEAELd2TrtDsc_Summ_ByTrt": "DISCONTINUATION",
}
Out = Callable[[str], None]


class PilotError(RuntimeError):
    """The pilot cannot be scored: the cache, the kit or the example is not as pinned."""


STATES = ("decision", "open", "no_row", "unexplained")


@dataclass
class Explained:
    cell: build.WrongCell
    state: str = "unexplained"  # one of STATES
    by: list[tuple[Key, dict]] = field(default_factory=list)  # (decision, the value that fits)
    note: str = ""


@dataclass
class Pilot:
    score: build.BuildScore
    key: dict  # the key grid, with the house labels
    ours: dict | None  # the grid of arm S
    missing: list[tuple[str, str, list[str]]]  # (dataset, variable, decisions that write it)
    not_built: list[str]  # row codes left out for a missing variable
    no_row: list[str]  # analyses of the example without a row in the catalog
    cells: list[Explained]
    axes: dict[str, list[tuple[Key, dict]]]  # axis that differs -> what makes it equal
    vector: list[dict]
    reads: list[tuple[str, str, bool]] = field(default_factory=list)  # (dataset, variable, there)


def _pinned(root: Path, kit: kits.Kit, path: str) -> Path:
    entry = next((item for item in kit.files if item.path == path), None)
    if entry is None:
        raise PilotError(f"the kit {kit.id} lists no file {path}")
    origin = cache_dir(root) / entry.source / entry.origin
    if not origin.is_file():
        raise PilotError(f"{entry.source}:{entry.origin} is not in the fetch cache: run "
                         "`specfirst fetch`")
    if sha256_file(origin) != entry.sha256:
        raise PilotError(f"{entry.source}:{entry.origin} does not have the pinned SHA-256")
    return origin


def reference(root: Path) -> tuple[Data, ars.Event, layouts.Layout]:
    """The reference ADaM of the pilot, the ARS example and the kit's layout of its
    adverse event summary."""
    import pyarrow.parquet as pq

    kit = kits.load_kit(root, KIT)
    tables = {name: pq.read_table(_pinned(root, kit, f"{kit.reference}/{name.lower()}.parquet"))
              for name in DATASETS}
    spec = kit.results[0]
    event = ars.index(ars.read(_pinned(root, kit, spec.ars)))
    display = next((item for item in spec.displays if item.output == OUTPUT), None)
    if event.problems or display is None:
        raise PilotError(f"the kit does not build {OUTPUT} from a usable reporting event")
    layout = layouts.read(kits.manifest_path(root, KIT).parent / display.layout)
    return Data(f"{KIT}/reference", adam=tables), event, layout


def arms(data: Data) -> tuple[Arm, ...]:
    """The arms of the pilot, from the reference ADSL: the actual treatment and its
    numeric code, which is the daily dose (0, 54 and 81)."""
    table = data.adam["ADSL"]
    doses = dict(zip(table.column("TRT01A").to_pylist(), table.column("TRT01AN").to_pylist(),
                     strict=True))
    ordered = sorted(doses.items(), key=lambda item: item[1])
    return tuple(Arm(label, float(dose), place) for place, (label, dose)
                 in enumerate(ordered, start=1))


def labels(machine: Machine) -> dict[str, str]:
    """The label of every row code of the house table."""
    compiled = machine.compile(standard_vector(machine))
    if isinstance(compiled, str):
        raise PilotError(f"the house defaults do not compile: {compiled}")
    return {row["analysis"].removeprefix("An_AESUM_"): row["label"]
            for row in compiled.layouts[UNIT]["rows"]}


def key_grid(event: ars.Event, layout: layouts.Layout, names: dict[str, str]) -> dict:
    """The key: the example's formatted values in the cells of the kit's layout, as a
    grid with the house labels and the house output ID."""
    planned = grids.plan(event, layout, None)
    embedded = results.embedded(event)
    rows = []
    for number, row in enumerate(planned.rows, start=1):
        cells = []
        for cell in row.cells:
            lacking = [item.ard for item in cell.shown
                       if item.ard not in embedded or embedded[item.ard].formatted is None]
            if lacking:
                raise PilotError(f"the example formats no value for {lacking[0]}")
            text = grids.cell_text(row.template, cell.shown, {
                (item.ard, item.pattern): embedded[item.ard].formatted for item in cell.shown})
            cells.append({"id": f"cell:{OUR_OUTPUT}/r{number}/{cell.column}",
                          "column": cell.column, "text": text, "ard": grids.cell_rows(cell.shown)})
        analysis = cell.shown[-1].analysis
        record = {"id": f"r{number}", "cells": cells}
        if row.section == layouts.HEADER_SECTION:
            record.update(label="", section=row.section)
        else:
            code = ROWS.get(analysis)
            record["label"] = names[code] if code else row.label
        rows.append(record)
    return {"schema": grids.SCHEMA, "output_id": OUR_OUTPUT, "titles": list(planned.titles),
            "columns": [{"id": column, "label": label} for column, _, label in planned.columns],
            "rows": rows, "footnotes": list(planned.footnotes)}


def standard_vector(machine: Machine) -> list[dict]:
    """Arm S for the one output: every house default; the first alternative of the
    catalog where a decision of another unit has none (the tables read none of
    these); the three other table families left out."""
    found = []
    for record in checks.base_vector(machine.catalog, machine.house):
        kind = machine.catalog.units[record["unit"]].kind
        if kind == "table_family" and record["unit"] != UNIT:
            if record["id"] == "tfl.output.include":
                found.append({**record, "value": {"rule": "not_included"}})
            continue
        found.append(record)
    return found


def lacking(compiled: compiler.Compiled, data: Data) -> list[tuple[str, str]]:
    """The (dataset, variable) pairs the compiled tables read and the data do not have."""
    if compiled.ars is None:
        return []  # no output is included
    event = ars.index(compiled.ars)
    return [(dataset, name) for dataset, names in ars.columns(event, SUBJECT_KEY).items()
            for name in names
            if dataset not in data.adam or name not in data.adam[dataset].column_names]


def without_unbuildable(data: Data) -> Hooks:
    """Leave out the analyses that read a variable the data do not have, and their rows."""
    def plant(compiled: compiler.Compiled) -> None:
        gone = set(lacking(compiled, data))
        if not gone:
            return
        event = ars.index(compiled.ars)
        dropped = {analysis_id for analysis_id in event.analyses
                   if any((dataset, name) in gone
                          for _, dataset, name in ars.reads(event, analysis_id, SUBJECT_KEY))}
        compiled.ars["analyses"] = [a for a in compiled.ars["analyses"] if a["id"] not in dropped]
        compiler.prune_ars(compiled.ars)
        for layout in compiled.layouts.values():
            layout["rows"] = [row for row in layout["rows"] if row["analysis"] not in dropped]

    return Hooks("without-unbuildable", compiled=plant)


def _wrong(score: build.BuildScore) -> list[build.WrongCell]:
    return score.wrong()


def run(machine: Machine) -> Pilot:
    """Score arm S at stage T on the pilot and explain every difference."""
    data, event, layout = reference(machine.root)
    names = labels(machine)
    key = key_grid(event, layout, names)
    design = arms(data)
    hooks = without_unbuildable(data)
    vector = standard_vector(machine)

    def made(records: list[dict]) -> Build:
        return machine.build(records, data, design, hooks)

    def scored(built: Build) -> build.BuildScore:
        return build.score("reference ADaM", {OUR_OUTPUT: key}, built.grids, built.ok,
                           built.failure, built.not_produced)

    base = made(vector)
    score = scored(base)
    compiled = machine.compile(vector)
    missing, reads = [], []
    if not isinstance(compiled, str):
        gone = set(lacking(compiled, data))
        reads = [(dataset, name, (dataset, name) not in gone)
                 for dataset, names in ars.columns(ars.index(compiled.ars), SUBJECT_KEY).items()
                 for name in names]
        for dataset, name in lacking(compiled, data):
            writers = sorted(key[0] for key, bound in compiled.binds.items()
                             if f"adam:{dataset}.{name}" in bound)
            missing.append((dataset, name, writers))
    our_rows = {row["label"] for row in (base.grids.get(OUR_OUTPUT) or {"rows": []})["rows"]}
    not_built = [code for code, label in names.items() if label not in our_rows]
    # Every other value of every table decision, each built once.
    trials: list[tuple[Key, dict, build.BuildScore]] = []
    for record in vector:
        if record["unit"] != UNIT:
            continue
        key_of = (record["id"], record["unit"])
        for value in compiler.other_values(machine.catalog, record["id"], record["value"]):
            other = [{**r, "value": value} if (r["id"], r["unit"]) == key_of else r
                     for r in vector]
            trials.append((key_of, value, scored(made(other))))
    cells = []
    for cell in _wrong(score):
        item = Explained(cell)
        for key_of, value, trial in trials:
            still = {(w.row, w.column) for w in trial.wrong()}
            if trial.produced and (cell.row, cell.column) not in still:
                item.by.append((key_of, value))
        code = next((c for c, label in names.items() if label == cell.row[1]), None)
        if item.by:
            item.state = "decision"
        elif cell.reason == "no_row" and code in not_built:
            item.state = "open"
            item.note = "the row is not built: " + "; ".join(
                f"the reference ADaM has no {d}.{n}, which the house standard writes by "
                f"{', '.join(w) or 'its parent spec'}" for d, n, w in missing)
        elif cell.reason == "no_row":
            item.state = "no_row"
            item.note = "the catalog has no such row (tfl.ae.summary.rows)"
        else:
            item.note = "no other value of one table decision gives the key's text"
        cells.append(item)
    axes: dict[str, list[tuple[Key, dict]]] = {}
    output = score.outputs[0]
    for axis, equal in (("rows", output.rows_equal), ("columns", output.columns_equal)):
        if output.produced and not equal:
            axes[axis] = [(key_of, value) for key_of, value, trial in trials
                          if trial.produced and getattr(trial.outputs[0], f"{axis}_equal")]
    no_row = [analysis for analysis, code in ROWS.items() if code is None]
    return Pilot(score, key, base.grids.get(OUR_OUTPUT), missing, not_built, no_row, cells, axes,
                 vector, reads)


def _fits(by: list[tuple[Key, dict]]) -> str:
    import json

    return "; ".join(f"{key[0]} = {json.dumps(value, sort_keys=True)}" for key, value in by)


def lines(pilot: Pilot) -> list[str]:
    """The report on the pilot as text: the table, the scores, every difference."""
    said = ["pilot CDISCPILOT01, arm S (the house standard alone), stage T (table decisions "
            "on the reference ADaM); report only",
            "key: the results CDISC's ARS example embeds for its adverse event summary "
            f"({OUTPUT}), as the kit's layout places them"]
    theirs = build.table_of(pilot.key)
    ours = build.table_of(pilot.ours) if pilot.ours else None
    explained = {(item.cell.row, item.cell.column): item for item in pilot.cells}
    said.append("  row | column | key | arm S | state")
    for row in theirs.rows:
        for column in theirs.columns:
            want = theirs.cells[(row, column)]["text"]
            got = ours.cells.get((row, column)) if ours else None
            item = explained.get((row, column))
            if item is None:
                state = "equal"
            elif item.state == "decision":
                state = "differs; explained by " + _fits(item.by)
            elif item.state == "unexplained":
                state = "UNEXPLAINED: " + item.note
            else:
                state = item.note
            said.append(f"  {row[1] or '(column header)'} | {column[0]} | {want} | "
                        f"{'-' if got is None else got['text']} | {state}")
    said += ["  " + line for line in pilot.score.lines()]
    for axis, by in pilot.axes.items():
        output = pilot.score.outputs[0]
        extra = output.extra_rows if axis == "rows" else output.extra_columns
        more = (" (arm S has more: " + ", ".join(str(key[-2]) for key in extra) + ")"
                if extra else "")
        lacks = len([row for row in theirs.rows if ours and row not in ours.rows])
        less = f" (the key has {lacks} rows that arm S lacks)" if axis == "rows" and lacks else ""
        said.append(f"  the {axis} are not the key's{more}{less}: "
                    + ("explained by " + _fits(by) if by else
                       "no other value of one table decision makes them equal"))
    count = {state: sum(1 for item in pilot.cells if item.state == state) for state in STATES}
    said.append(f"  cells of the key that differ or are missing: {len(pilot.cells)}. "
                f"{count['decision']} differ and are explained by another value of one table "
                f"decision; {count['open']} are in a row that needs a variable the reference "
                f"ADaM lacks; {count['no_row']} are in rows the catalog does not have; "
                f"{count['unexplained']} unexplained")
    said.append(f"  variables the house template reads: {len(pilot.reads)}; in the reference "
                "ADaM under the same name: "
                + ", ".join(f"{d}.{n}" for d, n, there in pilot.reads if there))
    said.append("  variables the house template reads and the reference ADaM does not have: "
                + ("none" if not pilot.missing else str(len(pilot.missing))))
    for dataset, name, writers in pilot.missing:
        said.append(f"    {dataset}.{name}: the house standard writes it by "
                    f"{', '.join(writers) or 'its parent spec'}; rows not built: "
                    f"{', '.join(pilot.not_built)}")
    said.append("  analyses of the example with no row in the catalog: "
                + (", ".join(pilot.no_row) or "none"))
    said.append("  the crosswalk of rows (example analysis = house row): " + ", ".join(
        f"{analysis} = {code}" for analysis, code in ROWS.items() if code))
    return said
