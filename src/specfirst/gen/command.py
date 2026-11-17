"""`specfirst gen`: sample a design, generate a study, check a study.

    specfirst gen design --seed S --out design.yaml
    specfirst gen study --design design.yaml --seed S --out DIR
    specfirst gen check DIR

A seed is a text. `--seed-file` reads it from a file instead of the command
line; such a file must lie outside the checkout, because the seeds of dev,
test and sealed kits are secrets (PLAN.md sections 6.7 and 8). The gate
seeds are development seeds and are in `specfirst.gen.gate`.
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
    """The seed text: from the command line, or from a file outside the checkout."""
    if (seed is None) == (seed_file is None):
        raise SeedError("give exactly one of --seed and --seed-file")
    if seed is not None:
        return seed
    path = Path(seed_file).expanduser().resolve()
    if path == root.resolve() or root.resolve() in path.parents:
        raise SeedError(f"{path} is inside the checkout; a seed file stays outside the "
                        "repository (PLAN.md section 6.7)")
    text = path.read_text(encoding="ascii").strip()
    if not text:
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
    for sub in (p_design, p_study):
        sub.add_argument("--seed", help="the seed, as text")
        sub.add_argument("--seed-file", help="a file outside the checkout that holds the seed")
    p_check = actions.add_parser(
        "check", help="check a study: its files, its probes, and its SDTM with CDISC CORE")
    p_check.add_argument("folder", help="a study folder")
    p_check.add_argument("--no-core", action="store_true", help="skip CDISC CORE")
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
            _, unexplained = gate.classify(report, gate.load_explained(), tables, log, which)
            unexplained = gate.report_problems(root, report) + unexplained
            print(f"{which}: CDISC CORE {report.engine}, {len(report.findings)} findings, "
                  f"{len(unexplained)} unexplained")
            problems += [f"{which}: CORE: {line}" for line in unexplained]
    for problem in problems:
        print(problem)
    print("study: " + ("ok" if not problems else "FAILED"))
    return 0 if not problems else 1


def main(root: Path, argv: Sequence[str]) -> int:
    args = _parser().parse_args(list(argv))
    if args.action == "check":
        return _check(root, Path(args.folder), not args.no_core)
    try:
        seed = read_seed(root, args.seed, args.seed_file)
    except (SeedError, OSError) as error:
        print(f"cannot read the seed: {error}")
        return 2
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
