"""`specfirst score ...`: the scorer from the command line (PLAN.md sections 9 and 12).

    specfirst score hand [--stage C|T] [--arm S|C | --decisions FILE
                         [--questions FILE] [--unmapped FILE]]
    specfirst score kit DIR [--stage C|T] [--arm S|C | --decisions FILE
                         [--questions FILE] [--unmapped FILE]]
    specfirst score kits DIR
    specfirst score defects [--kit DIR]
    specfirst score pilot

`hand` scores on the hand-made study HAND01 (specfirst.score.hand): an arm
that needs no reader, or the decision records of a file. `kit` does the
same on a generated kit (a folder that `specfirst gen kit` wrote); with
neither an arm nor a file it runs everything the gate runs on one kit: the
gold of the kit built again, both arms in both stages, the planted defects
and the sweep of its matrix. `kits` does that for every kit of a folder
and decides as the gate does. `defects` plants the defects of section 9.5
that apply to the slice, on HAND01 or on a kit. `pilot` is the report on
CDISCPILOT01 of ADR-005, decision 5; it needs the fetch cache.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from specfirst.score import defects, hand, pilot, report, scorer
from specfirst.score import kit as kits
from specfirst.score.candidate import Machine
from specfirst.score.reading import ask_keys, unmapped_keys


def _jsonl(path: str | None) -> list[dict]:
    if not path:
        return []
    with open(path, encoding="ascii") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="specfirst score", description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="what", required=True)
    p_hand = commands.add_parser("hand", help="score on the hand-made study HAND01")
    p_kit = commands.add_parser("kit", help="score on a generated kit")
    p_kit.add_argument("folder", help="a kit folder")
    for sub in (p_hand, p_kit):
        sub.add_argument("--stage", choices=scorer.STAGES, default="C",
                         help="C: the chain from SDTM; T: table decisions on the gold ADaM")
        sub.add_argument("--arm", choices=("S", "C"),
                         help="S: the house standard alone; C: the parser control")
        sub.add_argument("--decisions", help="decisions.jsonl of a candidate")
        sub.add_argument("--questions", help="questions.jsonl of the candidate")
        sub.add_argument("--unmapped", help="unmapped.jsonl of the candidate")
    p_kits = commands.add_parser("kits", help="score every kit of a folder, as the gate does")
    p_kits.add_argument("folder", help="a folder of kit folders")
    p_defects = commands.add_parser("defects", help="plant the defects of section 9.5")
    p_defects.add_argument("--kit", help="a kit folder; default: the hand-made study HAND01")
    commands.add_parser("pilot", help="arm S on the reference ADaM of CDISCPILOT01 (report only)")
    return parser


def _kit(root: Path, folder: str) -> tuple[Machine, kits.Kit] | None:
    """A kit and its machine; None, with the reason printed, when it cannot be scored."""
    try:
        kit = kits.load(Path(folder))
    except kits.KitError as error:
        print(f"cannot score: {error}")
        return None
    return kits.machine_of(root, kit), kit


def main(root: Path, argv: list[str]) -> int:
    args = build_parser().parse_args(argv)
    if args.what == "kits":
        return 0 if kits.score_set(root, Path(args.folder)) else 1
    if args.what == "pilot":
        try:
            found = pilot.run(Machine(root))
        except pilot.PilotError as error:
            print(f"pilot: {error}")
            return 1
        print("\n".join(pilot.lines(found)))
        return 0
    if args.what == "defects" and not args.kit:
        machine = Machine(root)
        passed, _ = defects.suite(machine, hand.case(machine.catalog, machine.house))
        return 0 if passed else 1
    if args.what == "hand":
        machine = Machine(root)
        case = hand.case(machine.catalog, machine.house, args.stage)
    else:
        loaded = _kit(root, args.kit if args.what == "defects" else args.folder)
        if loaded is None:
            return 1
        machine, kit = loaded
        if args.what == "kit" and not (args.arm or args.decisions):
            return 0 if kits.score_kit(machine, kit, print).passed else 1
        # A score counts only against a gold that the scorer builds as the kit holds it.
        problems = kits.gold_problems(machine, kit)
        if problems:
            print("\n".join(f"problem: {problem}" for problem in problems))
            print("the scorer's build of the gold decisions is not the gold of the kit")
            return 1
        if args.what == "defects":
            _, outcomes = defects.suite(machine, kits.case(kit, machine.catalog))
            return 0 if outcomes and not any(o.state == "failed" for o in outcomes) else 1
        case = kits.case(kit, machine.catalog, args.stage)
    if args.decisions:
        units = {entry.id: entry.units for entry in machine.catalog.entries.values()}
        result = scorer.run(machine, case, _jsonl(args.decisions),
                            asked=ask_keys(_jsonl(args.questions), units),
                            unmapped=unmapped_keys(_jsonl(args.unmapped)))
    elif args.arm == "C":
        result = scorer.control(machine, case)
    else:
        result = scorer.standard_alone(machine, case)
    print("\n".join(report.lines(result)))
    return 0 if result.perfect or args.arm != "C" else 1
