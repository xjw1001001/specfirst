"""The `specfirst` command.

base-0 provides doctor, fetch, status and gate. real-1 adds kit, build and
check. The other commands of PLAN.md section 12 (compile, preview, rebuild,
gen, score, run, ask) arrive with the work packages that build them.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

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

    p_kit = commands.add_parser("kit", help="assemble a kit from the fetch cache, or pin its files")
    p_kit.add_argument("action", choices=("assemble", "lock"))
    p_kit.add_argument("kit", help="kit ID, for example cdiscpilot01")

    p_build = commands.add_parser(
        "build", help="build a kit's resolved specs, ADaM datasets and graph"
    )
    p_build.add_argument("kit", help="kit ID")
    p_build.add_argument(
        "--into", type=Path, help="assemble and build here, not in build/kits/<kit>"
    )

    p_check = commands.add_parser(
        "check", help="compare a build with the reference (P2) and check its trace"
    )
    p_check.add_argument("kit", help="kit ID")
    p_check.add_argument("--build", type=Path, help="the build to check; default build/kits/<kit>")
    p_check.add_argument(
        "--twice", action="store_true", help="first build twice and compare the hashes (P1)"
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
    if args.command == "kit":
        from specfirst import kit

        if args.action == "assemble":
            return kit.run_assemble(root, args.kit)
        changed = kit.lock(root, args.kit)
        print(f"kit {args.kit}: SHA-256 rewritten from the fetch cache; {len(changed)} changed")
        return 0
    if args.command == "build":
        from specfirst.machine import build

        return build.build(root, args.kit, into=args.into)
    if args.command == "check":
        from specfirst.machine import build

        return build.check(root, args.kit, folder=args.build, twice=args.twice)
    raise AssertionError(args.command)
