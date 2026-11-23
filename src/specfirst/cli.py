"""The `specfirst` command.

base-0 provides doctor, fetch, status and gate. real-1 adds kit, build and
check. std-1 adds catalog, house, compile, render and parse. real-2 adds
methods, and the results to build and check. real-3a adds the grids, their
mock shells and pages, and the trace of their cells. gen-1a adds gen, and
gen-2a its actions kit, kits and verify; issue #30 the action separate.
read-1a adds score. read-2a adds run (the reader harness) and ask (the
oracle). Issue #29 adds recompute (one standalone recomputation script per
analysis, ADR-021). Issue #31 adds view (the review page of a built kit,
ADR-022). The other commands of PLAN.md
section 12 (preview, rebuild) arrive with the work packages that build them.
"""

from __future__ import annotations

import argparse
import json
import sys
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
        "build", help="build a kit's resolved specs, ADaM datasets, results, grids and graph"
    )
    p_build.add_argument("kit", help="kit ID")
    p_build.add_argument(
        "--into", type=Path, help="assemble and build here, not in build/kits/<kit>"
    )

    p_methods = commands.add_parser(
        "methods", help="list the method registry and check standard/methods/registry.json"
    )
    p_methods.add_argument(
        "--write", action="store_true", help="rewrite registry.json from the YAML entries"
    )

    p_check = commands.add_parser(
        "check", help="compare a build with its references (P2): ADaM, trace, results, grids"
    )
    p_check.add_argument("kit", help="kit ID")
    p_check.add_argument("--build", type=Path, help="the build to check; default build/kits/<kit>")
    p_check.add_argument(
        "--twice", action="store_true", help="first build twice and compare the hashes (P1)"
    )

    p_recompute = commands.add_parser(
        "recompute", help="write one standalone recomputation script per analysis of a built "
                          "kit, run them sealed and compare with the ARD (issue #29)")
    p_recompute.add_argument("kit", help="kit ID")
    p_recompute.add_argument("--build", type=Path,
                             help="the build to recompute; default build/kits/<kit>")
    p_recompute.add_argument("--export", type=Path, metavar="DIR",
                             help="also copy the bundle to DIR/recompute-<kit>")

    p_view = commands.add_parser(
        "view", help="write the review page of a built kit: the calculation first, a panel "
                     "per number, the study decision sheet (issue #31)")
    p_view.add_argument("kit", help="kit ID")
    p_view.add_argument("--build", type=Path, help="the build; default build/kits/<kit>")
    p_view.add_argument("--p4", type=Path, metavar="FILE",
                        help="a P4 matrix (specfirst gen separate) for the classes of decisions")

    p_catalog = commands.add_parser("catalog", help="check the decision catalog")
    p_catalog.add_argument("--sources", action="store_true",
                           help="check the cited public sources on the fetch cache")
    p_catalog.add_argument("--roundtrip", action="store_true",
                           help="check decisions to statements to decisions")
    p_catalog.add_argument("--yamaa", action="store_true",
                           help="compile every alternative and run yamaa check")
    p_catalog.add_argument("--run", action="store_true",
                           help="compile every alternative and build ADaM on the tiny study")
    p_catalog.add_argument("--tables", action="store_true",
                           help="compile every alternative and check ARS files and layouts")
    p_catalog.add_argument("--overview", metavar="FILE",
                           help="write one readable page of the whole catalog and stop")
    _pair_arguments(p_catalog)

    p_house = commands.add_parser("house", help="check the house standard")
    p_house.add_argument("--write", action="store_true",
                         help="render STANDARD.md from the catalog and the house")
    _pair_arguments(p_house)

    p_compile = commands.add_parser(
        "compile", help="compile decision records into yamaa, ARS and layout files"
    )
    p_compile.add_argument("--decisions", required=True, help="decisions.jsonl")
    p_compile.add_argument("--out", required=True, help="output folder")
    p_compile.add_argument("--defaults", action="store_true",
                           help="take the house default for every decision the file leaves out")
    p_compile.add_argument("--sdtm", default="../sdtm",
                           help="where the ADaM specs read SDTM, relative to <out>/adam")
    p_compile.add_argument("--adam", default=".",
                           help="where the ADaM specs write ADaM, relative to <out>/adam")
    _pair_arguments(p_compile)

    p_render = commands.add_parser(
        "render", help="render decision records as a standard-form document"
    )
    p_render.add_argument("--decisions", required=True, help="decisions.jsonl")
    p_render.add_argument("--doc", required=True, help="document ID, for example sap")
    p_render.add_argument("--title", default="Standard form")
    p_render.add_argument("--out", required=True, help="the Markdown file to write")
    _pair_arguments(p_render, house=False)

    p_parse = commands.add_parser(
        "parse", help="read a standard-form document back into decision records"
    )
    p_parse.add_argument("document", help="a standard-form Markdown file")
    p_parse.add_argument("--out", required=True, help="decisions.jsonl to write")
    _pair_arguments(p_parse, house=False)

    p_gen = commands.add_parser(
        "gen", add_help=False,
        help="generate a study or a kit: `gen design|study|check|kit|kits|verify|separate` "
             "(see `gen --help`)")
    p_gen.add_argument("rest", nargs=argparse.REMAINDER)

    p_score = commands.add_parser(
        "score", add_help=False,
        help="score decisions: `score hand`, `score defects`, `score pilot` (see `score --help`)")
    p_score.add_argument("rest", nargs=argparse.REMAINDER)

    p_run = commands.add_parser(
        "run", add_help=False,
        help="the reader harness: `run task|arm|probe|check|score|skills|validate` "
             "(see `run --help`)")
    p_run.add_argument("rest", nargs=argparse.REMAINDER)

    p_ask = commands.add_parser(
        "ask", add_help=False,
        help='ask about one decision: `ask "<question>" --decision ID --run RUN --task TASK`')
    p_ask.add_argument("rest", nargs=argparse.REMAINDER)
    return parser


def _pair_arguments(parser: argparse.ArgumentParser, house: bool = True) -> None:
    """--catalog and --house: the version labels to load (ADR-020)."""
    from specfirst.compile import versions

    parser.add_argument("--catalog", metavar="LABEL",
                        help="the catalog version, catalog@<n>; default "
                             f"{versions.DEFAULT_CATALOG}")
    if house:
        parser.add_argument("--house", metavar="LABEL",
                            help=f"the house version, <house>@<n>; default "
                                 f"{versions.DEFAULT_HOUSE}")


def _pair(root: Path, args: argparse.Namespace):
    """The catalog and the house the arguments name; a house that does not fit is refused."""
    from specfirst.compile import house

    return house.load_pair(root, getattr(args, "catalog", None), getattr(args, "house", None))


def _read_jsonl(path: str) -> list[dict]:
    with open(path, encoding="ascii") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _catalog(root: Path, args: argparse.Namespace) -> int:
    from specfirst.compile import gate, overview

    pair = (args.catalog, args.house)
    if args.overview:
        text = overview.render(*_pair(root, args))
        Path(args.overview).write_text(text, encoding="ascii", newline="\n")
        print(f"wrote {args.overview}")
        return 0
    selected = [check for flag, check in (
        (args.sources, gate.sources_check), (args.roundtrip, gate.roundtrip_check),
        (args.yamaa, gate.yamaa_check), (args.run, gate.run_check),
        (args.tables, gate.tables_check)) if flag]
    passed = [check(root, print, pair) for check in (selected or [gate.catalog_check])]
    return 0 if all(passed) else 1


def _house(root: Path, args: argparse.Namespace) -> int:
    from specfirst.compile import gate, house, versions

    pair = (args.catalog, args.house)
    if args.write:
        known, standard = _pair(root, args)
        listed = versions.load(root).get(standard.label)
        if listed is None or listed.status == "frozen":
            print(f"{standard.label} is frozen or not listed in {versions.VERSIONS}: its "
                  "STANDARD.md is not written (ADR-020)")
            return 1
        text = house.standards_document(known, standard)
        path = standard.directory / str(standard.raw["document"])
        path.write_text(text, encoding="ascii", newline="\n")
        print(f"wrote {path}")
    return 0 if gate.house_check(root, print, pair) else 1


def _compile(root: Path, args: argparse.Namespace) -> int:
    from specfirst.compile import compiler, house

    known, standard = _pair(root, args)
    records = _read_jsonl(args.decisions)
    if args.defaults:
        have = {(record.get("id"), record.get("unit")) for record in records}
        records += [r for r in house.defaults(known, standard)
                    if (r["id"], r["unit"]) not in have]
    out = Path(args.out).resolve()
    reference = compiler.relative_reference(standard.directory, out / "adam")
    try:
        compiled = compiler.compile_decisions(known, standard, records, reference,
                                              sdtm_dir=args.sdtm, adam_dir=args.adam)
    except compiler.CompileError as error:
        for problem in error.problems:
            print(f"cannot compile: {problem}")
        return 1
    compiler.bind_tables(known, standard, records, compiled, reference,
                         sdtm_dir=args.sdtm, adam_dir=args.adam)
    compiled.write(out)
    print(f"compiled {len(records)} decisions into {len(compiled.files) + 1} files in {out}")
    return 0


def _render(root: Path, args: argparse.Namespace) -> int:
    from specfirst.compile import catalog, standard_form

    form = standard_form.StandardForm(catalog.load(catalog.default_dir(root, args.catalog)))
    records = [record for record in _read_jsonl(args.decisions) if record.get("value")]
    try:
        text = form.render_document(args.doc, args.title, records)
    except standard_form.StandardFormError as error:
        print(f"cannot render: {error}")
        return 1
    Path(args.out).write_text(text, encoding="ascii", newline="\n")
    print(f"rendered {len(records)} decisions into {args.out}")
    return 0


def _parse(root: Path, args: argparse.Namespace) -> int:
    from specfirst.compile import catalog, standard_form
    from specfirst.compile.house import DOCUMENT_ID

    form = standard_form.StandardForm(catalog.load(catalog.default_dir(root, args.catalog)))
    text = Path(args.document).read_text(encoding="ascii")
    try:
        doc, parsed, cases, _ = form.parse_full(text)
    except standard_form.StandardFormError as error:
        print(f"cannot parse: {error}")
        return 1
    if cases:
        print(f"left out: {len(cases)} decisions by design (they need the design's features)")
    status_class = ("default", "house_default") if doc == DOCUMENT_ID else \
        ("stated", "document_rule")
    with open(args.out, "w", encoding="ascii", newline="\n") as handle:
        for item in parsed:
            record = standard_form.decision_record(item, doc, *status_class)
            handle.write(json.dumps(record, sort_keys=True) + "\n")
    print(f"parsed {len(parsed)} decisions of the document '{doc}' into {args.out}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    given = list(sys.argv[1:] if argv is None else argv)
    if given and given[0] in ("run", "ask"):
        # The rest goes to the harness as it is: the REMAINDER of a subparser drops a
        # rest that starts with an option (`ask --run RUN "<question>"`).
        from specfirst.harness import command as harness_command

        if given[0] == "ask":
            return harness_command.ask_main(repo_root(), given[1:])
        return harness_command.main(repo_root(), given[1:])
    args = build_parser().parse_args(given)
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
    if args.command == "methods":
        from specfirst.machine import registry

        return registry.run(root, write=args.write)
    if args.command == "build":
        from specfirst.machine import build

        return build.build(root, args.kit, into=args.into)
    if args.command == "check":
        from specfirst.machine import build

        return build.check(root, args.kit, folder=args.build, twice=args.twice)
    if args.command == "recompute":
        from specfirst.recompute import run as recompute

        return recompute.main(root, args.kit, args.build, args.export)
    if args.command == "view":
        from specfirst.viewer import command as view

        return view.main(root, args.kit, args.build, args.p4)
    if args.command == "gen":
        from specfirst.gen import command

        return command.main(root, args.rest)
    if args.command == "score":
        from specfirst.score import command as score_command

        return score_command.main(root, args.rest)
    handlers = {"catalog": _catalog, "house": _house, "compile": _compile,
                "render": _render, "parse": _parse}
    from specfirst.compile.catalog import CatalogError
    from specfirst.compile.house import HouseError
    from specfirst.compile.versions import VersionError

    try:
        return handlers[args.command](root, args)
    except (CatalogError, HouseError, VersionError) as error:
        print(f"cannot load the catalog and the house: {error}")
        return 1
