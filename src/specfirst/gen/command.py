"""`specfirst gen`: sample a design, generate a study, check a study; write and verify kits.

    specfirst gen design --seed S --out design.yaml
    specfirst gen study --design design.yaml --seed S --out DIR
    specfirst gen check DIR
    specfirst gen kit --seed S --out DIR [--split train] [--number N]
    specfirst gen kits --seed S --count N --out DIR [--first K]
    specfirst gen verify DIR [--no-mutation]
    specfirst gen natural requests|propose|readback-requests|readback|status ...

`gen kit` writes one kit of the slice "adverse event summary first" (data,
decisions, gold on the visible data and on the twin) when it has the
properties P1 to P4. `gen kits` writes the kits K to K + N - 1 of the set of
a seed, in folders kit-001, kit-002, ...; the number of a kit gives its
split and its scenario. `gen verify` decides the properties of a written
kit again from its files. `gen natural` is the loop of the natural form
(PLAN.md section 6.6, docs/decisions/ADR-009.md): it writes the request a
rewriter or a verifier gets, and stores and checks what they write back.

A seed is a text. `--seed-file` reads it from a file instead of the command
line; such a file must lie outside every checkout, because the seeds of dev,
test and sealed kits are secrets (PLAN.md sections 6.7 and 8). The seed is
then the whole content of the file, a line end included, so that
`seed_sha256` of the manifest is what `sha256sum` says of the seed file.
The gate seeds are development seeds and are in `specfirst.gen.gate`.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from specfirst.compile import catalog as catalogs
from specfirst.gen import design as designs
from specfirst.gen import pgfix, present, sdtm, study

ARCHETYPES = {pgfix.ARCHETYPE: pgfix.sample}


class SeedError(ValueError):
    """The seed cannot be taken as given."""


def read_seed(root: Path, seed: str | None, seed_file: str | None) -> str:
    """The seed text: from the command line, or the content of a file outside every checkout.

    The content is taken byte for byte: the SHA-256 that a manifest gives
    for the seed is the SHA-256 of the seed file (PLAN.md section 6.7).
    """
    if (seed is None) == (seed_file is None):
        raise SeedError("give exactly one of --seed and --seed-file")
    if seed is not None:
        return seed
    path = Path(seed_file).expanduser().resolve()
    inside = [root.resolve()] if root.resolve() in (path, *path.parents) else []
    # Another worktree or clone is a checkout as well: its mark is an entry `.git`.
    inside += [folder for folder in path.parents if (folder / ".git").exists()]
    if inside:
        raise SeedError(f"{path} is inside the checkout {inside[0]}; a seed file stays outside "
                        "every repository (PLAN.md section 6.7)")
    try:
        text = path.read_bytes().decode("ascii")
    except UnicodeDecodeError as error:
        raise SeedError(f"{path} is not ASCII text") from error
    if not text.strip():
        raise SeedError(f"{path} is empty")
    return text


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="specfirst gen", description=__doc__.splitlines()[0])
    actions = parser.add_subparsers(dest="action", required=True)
    p_design = actions.add_parser("design", help="sample a design of an archetype")
    p_design.add_argument("--archetype", default=pgfix.ARCHETYPE, choices=sorted(ARCHETYPES))
    p_design.add_argument("--out", required=True, help="the design.yaml to write")
    p_study = actions.add_parser("study", help="generate visible data, twin and probes.jsonl")
    p_study.add_argument("--design", required=True, help="a design.yaml")
    p_study.add_argument("--out", required=True, help="the study folder to write")
    p_study.add_argument("--domains", nargs="+", metavar="DOMAIN",
                         help=f"limit the SDTM to these domains; default: "
                              f"{' '.join(sdtm.SLICE_DOMAINS)}")
    p_kit = actions.add_parser("kit", help="write one kit: data, decisions, gold, twin")
    p_kit.add_argument("--out", required=True, help="the kit folder to write; must be empty")
    p_kit.add_argument("--split", default="train", choices=("train", "dev", "test", "sealed"))
    p_kit.add_argument("--number", type=int,
                       help="the number of the kit in a set: it gives the scenario")
    p_kit.add_argument("--documents", choices=("full", "standard", "ask"),
                       help="the tier of the documents; default: by --number, or the seed")
    p_kits = actions.add_parser("kits", help="write kits of the set of a seed")
    p_kits.add_argument("--out", required=True, help="the folder of the set")
    p_kits.add_argument("--count", type=int, required=True, help="how many kits")
    p_kits.add_argument("--first", type=int, default=1, help="the number of the first kit")
    for sub in (p_design, p_study, p_kit, p_kits):
        sub.add_argument("--seed", help="the seed, as text")
        sub.add_argument("--seed-file", help="a file outside the checkout that holds the seed")
    p_verify = actions.add_parser("verify", help="decide the properties of a written kit again")
    p_verify.add_argument("folder", help="a kit folder")
    p_verify.add_argument("--no-mutation", action="store_true",
                          help="skip the mutation of P4 (the slow part)")
    p_check = actions.add_parser(
        "check", help="check a study: its files, its probes, and its SDTM with CDISC CORE")
    p_check.add_argument("folder", help="a study folder")
    p_check.add_argument("--no-core", action="store_true", help="skip CDISC CORE")
    p_natural = actions.add_parser(
        "natural", help="the loop of the natural form: requests, proposals, read-back")
    p_natural.add_argument("step", choices=("requests", "propose", "readback-requests",
                                            "readback", "status"))
    p_natural.add_argument("file", nargs="?", help="propose, readback: the file a subagent "
                           "wrote")
    p_natural.add_argument("--kits", help="a folder of kits (kit-*) or one kit: the statements "
                           "their natural documents state")
    p_natural.add_argument("--out", help="requests, readback-requests: the request to write")
    p_natural.add_argument("--call", help="propose, readback: the ID of the model call")
    p_natural.add_argument("--request", help="the request the call answered (its hash is "
                           "logged)")
    p_natural.add_argument("--tokens", type=int, help="tokens of the call, as reported")
    p_natural.add_argument("--tool-uses", type=int, help="tool uses of the call, as reported")
    p_natural.add_argument("--seconds", type=int, help="time of the call, as reported")
    return parser


def _check(root: Path, folder: Path, with_core: bool) -> int:
    from specfirst.gen import gate

    catalog = catalogs.load(catalogs.default_dir(root))
    design = designs.load(folder / "gold" / "design.yaml")
    manifest = study.read_manifest(folder)
    problems = gate.hash_differences(manifest["files"], study.file_hashes(folder))
    print(f"{len(manifest['files'])} files against the hashes of study.json: "
          f"{len(problems)} differ")
    log = study.read_probes(folder)
    for which in study.PLACES:
        tables = study.read_tables(folder, which)
        pairs, checked, missing = present.coverage(catalog, design, log, tables, which)
        if which == "visible":  # the visible data carry a sampled part: only what is logged
            missing = [line for line in missing if line.startswith("probe ")]
        print(f"{which}: {checked} probes logged, {pairs} pairs of alternatives, "
              f"{len(missing)} problems")
        problems += [f"{which}: {line}" for line in missing]
        if with_core:
            report = gate.run_core(root, folder, which)
            _, findings = gate.classify(report, gate.load_explained(), tables, log, which)
            unexplained = gate.report_problems(root, report, tables) + [
                gate.describe(f) for f in findings]
            print(f"{which}: CDISC CORE {report.engine}, {len(report.findings)} findings, "
                  f"{len(unexplained)} unexplained")
            problems += [f"{which}: CORE: {line}" for line in unexplained]
    for problem in problems:
        print(problem)
    print("study: " + ("ok" if not problems else "FAILED"))
    return 0 if not problems else 1


def _kits(root: Path, args: argparse.Namespace, seed: str) -> int:
    from specfirst.gen import kits

    out = Path(args.out)
    try:
        if args.action == "kit":
            manifest = kits.generate_checked(root, seed, out, args.split, say=print,
                                             number=args.number, tier=args.documents)
            summary = manifest["properties"]["identifiability"]
            print(f"kit {manifest['id']} ({manifest['split']}): {len(manifest['files'])} files "
                  f"in {out}; P1: two builds have the same bytes; P2 to P4 hold; "
                  f"{len(summary['separated'])} of {summary['decisions']} decisions separated "
                  "on the twin")
        else:
            kits.generate_set(root, seed, args.count, out, first=args.first)
    except kits.KitError as error:
        print(f"cannot write the kit: {error}")
        return 1
    return 0


def main(root: Path, argv: Sequence[str]) -> int:
    args = _parser().parse_args(list(argv))
    if args.action == "check":
        return _check(root, Path(args.folder), not args.no_core)
    if args.action == "natural":
        return _natural(root, args)
    if args.action == "verify":
        from specfirst.gen import kits

        problems = kits.check(root, Path(args.folder), print, mutation=not args.no_mutation)
        for problem in problems:
            print(problem)
        print("kit: " + ("ok" if not problems else "FAILED"))
        return 0 if not problems else 1
    try:
        seed = read_seed(root, args.seed, args.seed_file)
    except (SeedError, OSError) as error:
        print(f"cannot read the seed: {error}")
        return 2
    if args.action in ("kit", "kits"):
        return _kits(root, args, seed)
    catalog = catalogs.load(catalogs.default_dir(root))
    if args.action == "design":
        design = ARCHETYPES[args.archetype](seed, study.catalog_label(catalog))
        Path(args.out).write_text(designs.dump(design), encoding="ascii", newline="\n")
        print(f"design of the archetype {args.archetype}: study {designs.study_id(design)}, "
              f"{len(designs.arms(design))} arms, written to {args.out}")
        return 0
    try:
        design = designs.load(Path(args.design))
        domains = tuple(args.domains) if args.domains else sdtm.SLICE_DOMAINS
        unknown = sorted(set(domains) - set(sdtm.DOMAINS))
        if unknown:
            raise study.StudyError(f"unknown domains: {', '.join(unknown)}")
        manifest = study.generate(root, design, seed, Path(args.out), domains)
    except (designs.DesignError, study.StudyError) as error:
        print(f"cannot generate: {error}")
        return 1
    counts = manifest["counts"]
    print(f"study {manifest['study']} for the catalog {study.catalog_label(catalog)}: "
          f"{counts['visible']['subjects']} subjects in the visible data, "
          f"{counts['twin']['subjects']} in the twin, {len(manifest['files'])} files in "
          f"{args.out}")
    return 0


def _kit_folders(folder: Path) -> list[Path]:
    if (folder / "kit.yaml").is_file():
        return [folder]
    return sorted(path for path in folder.glob("kit-*") if (path / "kit.yaml").is_file())


def _natural(root: Path, args: argparse.Namespace) -> int:
    """`specfirst gen natural`: one step of the loop of section 6.6 (ADR-009, decision 6)."""
    import hashlib
    import json

    from specfirst.gen import documents, kits, natural

    catalog = catalogs.load(catalogs.default_dir(root))
    store = natural.Store.load()
    wanted: dict[str, dict] = {}
    if args.kits:
        folders = _kit_folders(Path(args.kits))
        if not folders:
            print(f"no kit in {args.kits}")
            return 2
        wanted = natural.statements_of([kits.read_decisions(folder) for folder in folders])
    if args.step in ("requests", "propose") and not wanted:
        print("give --kits: the statements come from the decisions of kits")
        return 2
    if args.step in ("requests", "readback-requests"):
        if not args.out:
            print("give --out")
            return 2
        request = (natural.rewrite_request(catalog, store, wanted, documents.filler_wanted())
                   if args.step == "requests" else natural.readback_request(catalog, store))
        Path(args.out).write_text(json.dumps(request, indent=1, ensure_ascii=True) + "\n",
                                  encoding="ascii", newline="\n")
        counts = {name: len(request.get(name) or [])
                  for name in ("paragraphs", "items", "filler")}
        print(f"{args.out}: " + ", ".join(f"{count} {name}" for name, count in counts.items()
                                          if count or name == "filler"))
        return 0
    if args.step in ("propose", "readback"):
        if not args.file or not args.call:
            print("give the file the subagent wrote and --call")
            return 2
        raw = Path(args.file).read_bytes()
        answer = json.loads(raw.decode("ascii"))
        if args.step == "propose":
            lines = natural.propose(catalog, store, wanted, answer, args.call)
            items = len(answer.get("paragraphs") or []) + len(answer.get("filler") or [])
        else:
            lines = natural.readback(catalog, store, answer, args.call)
            items = len(answer.get("items") or []) + len(answer.get("filler") or [])
        store.add_call({
            "call": args.call, "role": "rewrite" if args.step == "propose" else "read-back",
            "model": natural.MODEL, "items": items, "tokens": args.tokens,
            "tool_uses": args.tool_uses, "seconds": args.seconds,
            "request_sha256": hashlib.sha256(Path(args.request).read_bytes()).hexdigest()
            if args.request else None,
            "answer_sha256": hashlib.sha256(raw).hexdigest()})
        store.save()
        for line in lines:
            print(line)
    records = list(store.paragraphs.values())
    accepted = [r for r in records if r.get("accepted")]
    template = [r for r in accepted if r["attempts"][r["accepted"] - 1]["by"] == "template"]
    open_ = [r for r in records if not r.get("accepted")]
    print(f"store {store.folder}: {len(records)} statements, {len(accepted)} accepted "
          f"({len(template)} by the phrasing template), {len(open_)} open; "
          f"{len(store.accepted_filler())} of {len(store.filler)} filler paragraphs accepted; "
          f"{len(store.calls)} calls, {sum(c.get('tokens') or 0 for c in store.calls)} tokens")
    if wanted:
        missing = sorted(key for key in wanted if store.accepted(wanted[key]["statement"]) is None)
        print(f"the kits state {len(wanted)} statements; without an accepted text: "
              f"{len(missing)}")
    return 0
