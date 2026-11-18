"""The checks of `specfirst gate read-1a` (ADR-005, decision 1; PLAN.md section 13.6).

Gate of the part: "The planted defects of section 9.5 that apply to the
slice are each detected and attributed to the right layer. The parser
control scores 100%." The work starts on the pilot and on hand-made
fixtures and finishes on the kits of gen-2a. Each function prints what it
counted, so the gate log is the evidence of the report (rule R8).

    hand_table   the gold decisions of HAND01 build the table worked out by
                 hand, on the visible data and on the twin
    separated    which decisions of the slice HAND01 can show, by mutation
    control      the parser control scores 100% on HAND01, in both stages;
                 and it does not when a statement of the document is changed
    defects      the planted defects on HAND01
    pilot        the report on CDISCPILOT01 runs on the pinned files
                 (report only: its scores decide nothing)
    kits         the kits of the gate of gen-2a, written again from its seed:
                 the gold of each kit built again, the control, the planted
                 defects and the sweep of its matrix (specfirst.score.kit)

A kit is never in the repository (docs/state/gen.md). The check `kits`
writes the ten kits of the development seed of the gate gen-2a into a
folder under the system's temporary folder, each by a process of its own,
four at a time, and removes them when it is done. A kit is a pure function
of the generator, the catalog, the house standard and the seed (property
P1, which the gate gen-2a holds), so these are the kits of that gate.
"""

from __future__ import annotations

import shutil
import tempfile
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from specfirst.compile.standard_form import StandardForm, StandardFormError, decision_record
from specfirst.gen import gate2
from specfirst.gen import kits as genkits
from specfirst.machine.canonical import sha256_file
from specfirst.score import build, defects, hand, pilot, report, scorer
from specfirst.score import kit as kits_scored
from specfirst.score.candidate import Machine

Out = Callable[[str], None]
_MACHINES: dict[str, Machine] = {}


def machine_of(root: Path) -> Machine:
    """One machine per checkout and process: a build made by one check is not made
    again by the next."""
    if str(root) not in _MACHINES:
        _MACHINES[str(root)] = Machine(root)
    return _MACHINES[str(root)]


def hand_table(root: Path, out: Out) -> bool:
    machine = machine_of(root)
    case = hand.case(machine.catalog, machine.house)
    problems = 0
    for which in case.data:
        _, gold = scorer.staged(machine, case, which)
        table = build.table_of(gold.grids[hand.OUTPUT])
        ours = {(row[1], column[0]): cell["text"] for (row, column), cell in table.cells.items()}
        wanted = hand.expected_cells(which)
        out(f"HAND01, {which}: {len(hand.SUBJECTS[which])} subjects, "
            f"{len(hand.EVENTS[which])} adverse events; columns "
            + " | ".join(column[0] for column in table.columns))
        for row in table.rows:
            out(f"  {row[1] or '(column header)':60s} "
                + " | ".join(table.cells[(row, column)]["text"] for column in table.columns))
        differing = sorted(key for key in set(ours) | set(wanted)
                           if ours.get(key) != wanted.get(key))
        for key in differing:
            out(f"  problem: {key[0]} / {key[1]}: built {ours.get(key)!r}, by hand "
                f"{wanted.get(key)!r}")
        problems += len(differing)
        out(f"HAND01, {which}: {len(wanted) - len(differing)} of {len(wanted)} cells are the "
            "cells worked out by hand")
    return problems == 0


def separated(root: Path, out: Out) -> bool:
    """Which decisions HAND01 can show at all: every other value of every decision of
    the slice, alone on gold. The gold records must mark exactly the others as
    `unseparated`."""
    import json

    machine = machine_of(root)
    case = hand.case(machine.catalog, machine.house)
    found = scorer.separation(machine, case)
    silent = []
    out("decision: other value -> cells or axes changed on the visible data / on the twin")
    for key, values in found.items():
        where = [name for name in case.data if any(changed[name] for _, changed in values)]
        if not where:
            silent.append(key[0])
        state = "separated on " + " and ".join(where) if where else "UNSEPARATED"
        out(f"  {key[0]} ({state}): " + "; ".join(
            f"{json.dumps(value, sort_keys=True)} -> {changed['visible']}/{changed['twin']}"
            for value, changed in values))
    marked = [r["id"] for r in case.gold if r.get("identifiable") == "unseparated"]
    out(f"HAND01 separates {len(found) - len(silent)} of {len(found)} decisions of the slice "
        f"on one of its two datasets; unseparated on both: {', '.join(silent)}")
    same = marked == silent
    out(f"the gold records mark the same {len(marked)} as unseparated: "
        + ("yes" if same else "NO: " + ", ".join(marked)))
    return same


def _changed_document(machine: Machine, case: scorer.Case) -> tuple[str, scorer.Result | str]:
    """The control on a document in which one statement says something else."""
    records, documents = scorer.control_records(machine, case)
    text = documents.texts[scorer.CONTROL_DOCUMENT]
    form = StandardForm(machine.catalog)
    line = next(line for line in text.split("\n") if "30 days" in line)
    changed = text.replace(line, line.replace("30 days", "31 days"))
    try:
        doc, parsed = form.parse_document(changed)
    except StandardFormError as error:
        return line, f"the parser refuses the document: {error}"
    stated = [decision_record(item, doc, "stated", "document_rule") for item in parsed]
    have = {(r["id"], r["unit"]) for r in stated}
    rest = [r for r in records if (r["id"], r["unit"]) not in have]
    return line, scorer.run(machine, case, stated + rest, arm="C",
                            documents=type(documents)({**documents.texts, doc: changed}))


def control(root: Path, out: Out) -> bool:
    machine = machine_of(root)
    passed = True
    for stage in scorer.STAGES:
        case = hand.case(machine.catalog, machine.house, stage)
        result = scorer.control(machine, case)
        out(f"parser control on HAND01, stage {stage}: {len(result.reading.decisions)} "
            "decisions; " + "; ".join(
                f"{name} {right} of {scored}" for name in ("value", "status", "quote", "span")
                for right, scored in [result.reading.total(name)]))
        for name, score in result.builds.items():
            cells = score.denominators()
            out(f"  {name}: produced {score.produced} of {score.in_gold}; cells correct "
                f"{score.correct} of {cells['shared_rows']}, {cells['produced']} and "
                f"{cells['all']} (its three denominators); strict {score.strict} of "
                f"{score.in_gold}; lenient {score.lenient} of {score.in_gold}")
        if not result.perfect:
            for line in report.lines(result):
                out("  " + line)
        out(f"parser control on HAND01, stage {stage}: "
            f"{'100%' if result.perfect else 'NOT 100%'}")
        passed &= result.perfect
    # Rule R5: the control must fail on a document that states something else.
    case = hand.case(machine.catalog, machine.house)
    line, found = _changed_document(machine, case)
    out(f"planted in the document: '{line}' with 31 days in place of 30")
    if isinstance(found, str):
        out(f"  {found}")
        seen = True
    else:
        wrong = [item.key[0] for item in found.reading.wrong()]
        seen = not found.perfect and wrong == ["ae.teae.end"]
        out(f"  the control is {'not ' if not found.perfect else ''}100%: wrong by value: "
            f"{', '.join(wrong) or 'none'}; twin: "
            f"{len(found.builds['twin'].wrong())} cells wrong")
    out(f"the control fails on the changed document: {'yes' if seen else 'NO'}")
    return passed and seen


def planted_defects(root: Path, out: Out) -> bool:
    machine = machine_of(root)
    passed, _ = defects.suite(machine, hand.case(machine.catalog, machine.house), out)
    return passed


def arms(root: Path, out: Out) -> bool:
    """Arm S on HAND01, in both stages: printed, and held against what the study is
    built to show."""
    machine = machine_of(root)
    chain = scorer.standard_alone(machine, hand.case(machine.catalog, machine.house))
    table = scorer.standard_alone(machine, hand.case(machine.catalog, machine.house, "T"))
    for result in (chain, table):
        for line in report.lines(result):
            out(line)
    # The study states two decisions. One has no default, so the chain cannot be
    # built from the standard alone; the table decisions are all defaults.
    not_built = all(score.produced == 0 for score in chain.builds.values())
    owners = {key[0] for owners in chain.owners.values() for owner in owners
              for key in owner.decisions}
    out(f"arm S, chain: no output produced: {'yes' if not_built else 'NO'}; owned by "
        f"{', '.join(sorted(owners)) or 'no decision'}")
    out(f"arm S, stage T: every score 100%: {'yes' if table.perfect else 'NO'}")
    return not_built and owners == {"ae.related.values"} and table.perfect


def pilot_report(root: Path, out: Out) -> bool:
    try:
        found = pilot.run(machine_of(root))
    except pilot.PilotError as error:
        out(f"pilot: {error}")
        return False
    for line in pilot.lines(found):
        out(line)
    out("pilot: report only; its scores decide nothing in this gate")
    return True


def write_kits(root: Path, folder: Path, out: Out, seed: str = gate2.SEED,
               count: int = gate2.COUNT) -> bool:
    """Write the kits 1 to `count` of the set of a seed into `folder`, as the gate of
    gen-2a writes its first builds: each by a process of its own, four at a time."""
    def run(number: int) -> str:
        try:
            genkits.generate_apart(root, genkits.kit_seed(seed, number),
                                   folder / f"kit-{number:03d}", genkits.split_of(number),
                                   number=number, hash_seed="1", zone=None)
        except genkits.KitError as error:
            return str(error)
        return ""

    numbers = range(1, count + 1)
    with ThreadPoolExecutor(max_workers=gate2.MAX_WORKERS) as pool:
        failed = list(pool.map(run, numbers))
    for number, problem in zip(numbers, failed, strict=True):
        path = folder / f"kit-{number:03d}"
        if problem:
            out(f"kit {number}: cannot be written: {problem}")
            continue
        manifest = genkits.read_manifest(path)
        out(f"kit {number} of the set of the seed '{seed}': {manifest['id']}, "
            f"{manifest['split']}, generator {manifest['generator']}, {len(manifest['files'])} "
            f"files, kit.yaml {sha256_file(path / genkits.MANIFEST)[:16]}")
    return not any(failed)


def kits(root: Path, out: Out) -> bool:
    folder = Path(tempfile.mkdtemp(prefix="specfirst-read1a-"))
    try:
        if not write_kits(root, folder, out):
            return False
        return kits_scored.score_set(root, folder, out)
    finally:
        shutil.rmtree(folder, ignore_errors=True)
