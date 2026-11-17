"""`specfirst score ...`: the scorer from the command line (PLAN.md sections 9 and 12).

    specfirst score hand [--stage C|T] [--arm S|C | --decisions FILE
                         [--questions FILE] [--unmapped FILE]]
    specfirst score defects
    specfirst score pilot

`hand` scores on the hand-made study HAND01 (specfirst.score.hand): an arm
that needs no reader, or the decision records of a file. `defects` plants
the defects of section 9.5 that apply to the slice. `pilot` is the report
on CDISCPILOT01 of ADR-005, decision 5; it needs the fetch cache.

Scoring the kits of gen-2a is added when they are on `main`
(docs/state/read.md).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from specfirst.score import defects, hand, pilot, report, scorer
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
    p_hand.add_argument("--stage", choices=scorer.STAGES, default="C",
                        help="C: the chain from SDTM; T: table decisions on the gold ADaM")
    p_hand.add_argument("--arm", choices=("S", "C"),
                        help="S: the house standard alone; C: the parser control")
    p_hand.add_argument("--decisions", help="decisions.jsonl of a candidate")
    p_hand.add_argument("--questions", help="questions.jsonl of the candidate")
    p_hand.add_argument("--unmapped", help="unmapped.jsonl of the candidate")
    commands.add_parser("defects", help="plant the defects of section 9.5 on HAND01")
    commands.add_parser("pilot", help="arm S on the reference ADaM of CDISCPILOT01 (report only)")
    return parser


def main(root: Path, argv: list[str]) -> int:
    args = build_parser().parse_args(argv)
    machine = Machine(root)
    if args.what == "defects":
        passed, _ = defects.suite(machine, hand.case(machine.catalog, machine.house))
        return 0 if passed else 1
    if args.what == "pilot":
        try:
            found = pilot.run(machine)
        except pilot.PilotError as error:
            print(f"pilot: {error}")
            return 1
        print("\n".join(pilot.lines(found)))
        return 0
    case = hand.case(machine.catalog, machine.house, args.stage)
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
