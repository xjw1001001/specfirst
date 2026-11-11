"""The `specfirst` command.

base-0 provides doctor, fetch, status and gate. The other commands of
PLAN.md section 12 (compile, build, check, preview, rebuild, gen, score,
run, ask, kit) arrive with the work packages that build them.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from specfirst import __version__, doctor, fetch, gates, status
from specfirst.paths import repo_root


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="specfirst", description=__doc__.splitlines()[0])
    parser.add_argument("--version", action="version", version=f"specfirst {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("doctor", help="compare the environment with the lock files")

    p_fetch = commands.add_parser(
        "fetch", help="clone the pinned sources into the ignored cache and verify them"
    )
    p_fetch.add_argument("--only", nargs="+", metavar="NAME", help="only these sources")
    p_fetch.add_argument("--verify", action="store_true", help="verify the cache, download nothing")

    commands.add_parser("status", help="print the handover file of every track")

    p_gate = commands.add_parser("gate", help="run the gate of a work package")
    p_gate.add_argument("wp", help="work package, for example base-0")
    p_gate.add_argument(
        "--clean", action="store_true", help="fail when the tree has uncommitted changes"
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = repo_root()
    if args.command == "doctor":
        return doctor.run(root)
    if args.command == "fetch":
        return fetch.run(root, only=args.only, verify_only=args.verify)
    if args.command == "status":
        return status.run(root)
    if args.command == "gate":
        return gates.run_gate(root, args.wp, require_clean=args.clean)
    raise AssertionError(args.command)
