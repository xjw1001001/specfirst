"""The `specfirst` command.

base-0 provides doctor, fetch, status and gate. real-1 adds kit, build and
check. std-1 adds catalog, house, compile, render and parse. real-2 adds
methods, and the results to build and check. The other commands of PLAN.md
section 12 (preview, rebuild, gen, score, run, ask) arrive with the work
packages that build them.
"""

from __future__ import annotations

import argparse
import json
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

    p_methods = commands.add_parser(
        "methods", help="list the method registry and check standard/methods/registry.json"
    )
    p_methods.add_argument(
        "--write", action="store_true", help="rewrite registry.json from the YAML entries"
    )

    p_check = commands.add_parser(
        "check", help="compare a build with its references (P2), check its trace and its results"
    )
    p_check.add_argument("kit", help="kit ID")
    p_check.add_argument("--build", type=Path, help="the build to check; default build/kits/<kit>")
    p_check.add_argument(
        "--twice", action="store_true", help="first build twice and compare the hashes (P1)"
    )

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

    p_house = commands.add_parser("house", help="check the house standard")
    p_house.add_argument("--write", action="store_true",
                         help="render STANDARD.md from the catalog and house.yaml")

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

    p_render = commands.add_parser(
        "render", help="render decision records as a standard-form document"
    )
    p_render.add_argument("--decisions", required=True, help="decisions.jsonl")
    p_render.add_argument("--doc", required=True, help="document ID, for example sap")
    p_render.add_argument("--title", default="Standard form")
    p_render.add_argument("--out", required=True, help="the Markdown file to write")

    p_parse = commands.add_parser(
        "parse", help="read a standard-form document back into decision records"
    )
    p_parse.add_argument("document", help="a standard-form Markdown file")
    p_parse.add_argument("--out", required=True, help="decisions.jsonl to write")
    return parser


def _read_jsonl(path: str) -> list[dict]:
    with open(path, encoding="ascii") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _catalog(root: Path, args: argparse.Namespace) -> int:
    from specfirst.compile import catalog, gate, house, overview

    if args.overview:
        text = overview.render(catalog.load(catalog.default_dir(root)),
                               house.load(house.default_dir(root)))
        Path(args.overview).write_text(text, encoding="ascii", newline="\n")
        print(f"wrote {args.overview}")
        return 0
    selected = [check for flag, check in (
        (args.sources, gate.sources_check), (args.roundtrip, gate.roundtrip_check),
        (args.yamaa, gate.yamaa_check), (args.run, gate.run_check),
        (args.tables, gate.tables_check)) if flag]
    passed = [check(root, print) for check in (selected or [gate.catalog_check])]
    return 0 if all(passed) else 1


def _house(root: Path, args: argparse.Namespace) -> int:
    from specfirst.compile import catalog, gate, house

    if args.write:
        known = house.load(house.default_dir(root))
        text = house.standards_document(catalog.load(catalog.default_dir(root)), known)
        path = known.directory / str(known.raw["document"])
        path.write_text(text, encoding="ascii", newline="\n")
        print(f"wrote {path}")
    return 0 if gate.house_check(root, print) else 1


def _compile(root: Path, args: argparse.Namespace) -> int:
    from specfirst.compile import catalog, compiler, house

    known = catalog.load(catalog.default_dir(root))
    standard = house.load(house.default_dir(root))
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

    form = standard_form.StandardForm(catalog.load(catalog.default_dir(root)))
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

    form = standard_form.StandardForm(catalog.load(catalog.default_dir(root)))
    text = Path(args.document).read_text(encoding="ascii")
    try:
        doc, parsed = form.parse_document(text)
    except standard_form.StandardFormError as error:
        print(f"cannot parse: {error}")
        return 1
    status_class = ("default", "house_default") if doc == DOCUMENT_ID else \
        ("stated", "document_rule")
    with open(args.out, "w", encoding="ascii", newline="\n") as handle:
        for item in parsed:
            record = standard_form.decision_record(item, doc, *status_class)
            handle.write(json.dumps(record, sort_keys=True) + "\n")
    print(f"parsed {len(parsed)} decisions of the document '{doc}' into {args.out}")
    return 0


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
    if args.command == "methods":
        from specfirst.machine import registry

        return registry.run(root, write=args.write)
    if args.command == "build":
        from specfirst.machine import build

        return build.build(root, args.kit, into=args.into)
    if args.command == "check":
        from specfirst.machine import build

        return build.check(root, args.kit, folder=args.build, twice=args.twice)
    handlers = {"catalog": _catalog, "house": _house, "compile": _compile,
                "render": _render, "parse": _parse}
    return handlers[args.command](root, args)
