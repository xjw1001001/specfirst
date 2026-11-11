"""Build a kit's gold from its pinned files, and check what was built.

`build` runs the machine as far as real-1 takes it (PLAN.md section 13.3):
the resolved specifications, the ADaM datasets and the SDTM to ADaM part of
the graph, each written by a canonical serializer, plus build.json with the
SHA-256 of every file written.

The checks are the properties of section 4.6 that apply so far:

    determinism   P1: two builds, each in a new process, give the same hashes
    reproduction  P2: every built dataset equals its reference, cell by cell
    trace         every output column reaches SDTM columns, literals or
                  declared inputs through derives_from
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

from specfirst import kit as kits
from specfirst.machine import compare, graph, runner
from specfirst.machine.canonical import sha256_file, write_json, write_parquet
from specfirst.paths import build_dir

Out = Callable[[str], None]
# What a build writes, relative to the folder it builds into.
RESOLVED, ADAM, GRAPH, MANIFEST = "gold/resolved", "gold/data/adam", "gold/graph", "gold/build.json"


def _assembled(
    root: Path, kit_id: str, folder: Path | None, out: Out
) -> tuple[kits.Kit, Path] | None:
    """The kit, assembled in `folder` (default build/kits/<kit>) from the fetch cache."""
    try:
        kit = kits.load_kit(root, kit_id)
    except kits.KitError as error:
        out(f"kit {kit_id}: {error}")
        return None
    dest = (folder or kits.assembled_dir(root, kit_id)).resolve()
    problems = kits.assemble(root, kit, dest)
    for problem in problems:
        out(f"kit {kit_id}: {problem}")
    return None if problems else (kit, dest)


def build(root: Path, kit_id: str, into: Path | None = None, out: Out = print) -> int:
    """`specfirst build <kit>`: assemble, check the pins, run, write. Returns 0 or 1.

    The kit is assembled in the folder it is built in, so a build stands on
    its own, and two builds in two folders share no path (P1).
    """
    import pyarrow

    found = _assembled(root, kit_id, into, out)
    if found is None:
        out(f"build {kit_id}: FAIL (the kit could not be assembled from the fetch cache)")
        return 1
    kit, dest = found
    into = dest
    wanted, installed = kit.engines.get(runner.ENGINE), runner.engine_version()
    if wanted != installed:
        out(f"build {kit_id}: FAIL (the kit pins {runner.ENGINE} {wanted}, "
            f"{installed} is installed)")
        return 1
    for stale in (RESOLVED, ADAM, GRAPH, MANIFEST):
        target = into / stale
        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists():
            target.unlink()
    try:
        plans = runner.run_project(dest, kit.project, kit.sdtm)
        trace = graph.build_graph(kit, dest, plans)
    except (runner.RunnerError, graph.GraphError) as error:
        out(f"build {kit_id}: FAIL ({error})")
        return 1
    written: list[Path] = []
    for plan in plans:
        stem = plan.name.lower()
        write_json(into / RESOLVED / f"{stem}.json", plan.record)
        write_parquet(into / ADAM / f"{stem}.parquet", plan.table)
        written += [into / RESOLVED / f"{stem}.json", into / ADAM / f"{stem}.parquet"]
        out(f"built {plan.name:9s} {plan.table.num_rows:6d} rows x {plan.table.num_columns:3d} "
            f"columns from {', '.join(source.dataset for source in plan.inputs)}")
    written += graph.write_graph(into / GRAPH, trace)
    files = {path.relative_to(into).as_posix(): sha256_file(path) for path in sorted(written)}
    write_json(into / MANIFEST, {
        "kit": kit.id,
        "kit_manifest_sha256": sha256_file(kits.manifest_path(root, kit.id)),
        "engines": {runner.ENGINE: installed, "pyarrow": pyarrow.__version__},
        "datasets": [plan.name for plan in plans],
        "files": files,
    })
    out(f"build {kit_id}: {len(plans)} datasets, {len(trace.nodes)} nodes, "
        f"{len(trace.edges)} edges, {len(files)} files in {into}")
    return 0


def read_manifest(folder: Path) -> dict:
    with open(folder / MANIFEST, encoding="ascii") as handle:
        return json.load(handle)


def manifest_problems(folder: Path) -> list[str]:
    """Why the files of a build are not the files its build.json describes."""
    try:
        manifest = read_manifest(folder)
    except (OSError, ValueError) as error:
        return [f"no usable {MANIFEST} in {folder}: {error}"]
    problems = []
    for name, digest in sorted(manifest.get("files", {}).items()):
        path = folder / name
        if not path.is_file():
            problems.append(f"{name}: missing")
        elif sha256_file(path) != digest:
            problems.append(f"{name}: changed since the build")
    return problems


def compare_builds(first: dict, second: dict) -> tuple[list[str], list[str]]:
    """Lines of the comparison of two build.json records, and the problems."""
    lines, problems = [], []
    for key in ("kit", "kit_manifest_sha256", "engines", "datasets"):
        if first.get(key) != second.get(key):
            problems.append(f"{key}: {first.get(key)!r} against {second.get(key)!r}")
    one, two = first.get("files", {}), second.get("files", {})
    if not one:
        problems.append("the first build lists no file")
    for name in sorted(set(one) | set(two)):
        same = name in one and name in two and one[name] == two[name]
        lines.append(f"{'same     ' if same else 'DIFFERENT'} {one.get(name, '-' * 64)[:16]} "
                     f"{two.get(name, '-' * 64)[:16]} {name}")
        if not same:
            problems.append(f"{name}: the two builds differ")
    return lines, problems


def determinism(root: Path, kit_id: str, out: Out = print) -> bool:
    """P1: build twice, each in a new process and its own folder, and compare the hashes.

    Each build assembles the kit in its own folder, so the two share no path
    of the kit: a built file that depends on where it was built differs.
    """
    base = build_dir(root) / "p1" / kit_id
    folders = [base / "first", base / "second"]
    for folder in folders:
        if folder.exists():
            shutil.rmtree(folder)
        done = subprocess.run(
            [sys.executable, "-m", "specfirst", "build", kit_id, "--into", str(folder)],
            cwd=root, capture_output=True, text=True,
            env={**os.environ, "SPECFIRST_ROOT": str(root)},
        )
        tail = (done.stdout + done.stderr).strip().splitlines()[-1:]
        out(f"build into {folder.relative_to(root).as_posix()}: exit {done.returncode}"
            + (f" ({tail[0]})" if tail else ""))
        if done.returncode != 0:
            out((done.stdout + done.stderr).rstrip())
            return False
    problems = [p for folder in folders for p in manifest_problems(folder)]
    lines, differences = compare_builds(read_manifest(folders[0]), read_manifest(folders[1]))
    for line in lines:
        out(line)
    problems += differences
    for problem in problems:
        out(f"P1: {problem}")
    out(f"P1 determinism: {len(lines) - len(differences)} of {len(lines)} files have the same "
        "SHA-256 in both builds")
    return not problems


def _built(root: Path, kit_id: str, folder: Path | None, out: Out):
    """The kit and the folder of a build of it, or None when one of them is unusable.

    The pinned files of the folder are checked again (and restored from the
    cache if they changed), then the built files against build.json.
    """
    found = _assembled(root, kit_id, folder, out)
    if found is None:
        return None
    kit, folder = found
    problems = manifest_problems(folder)
    for problem in problems:
        out(f"build in {folder}: {problem}")
    return None if problems else (kit, folder)


def reproduction(root: Path, kit_id: str, folder: Path | None = None, out: Out = print) -> bool:
    """P2: every built ADaM dataset equals the reference dataset of the same name."""
    import pyarrow.parquet as pq

    found = _built(root, kit_id, folder, out)
    if found is None:
        return False
    kit, folder = found
    dest = folder
    datasets = read_manifest(folder)["datasets"]
    references = sorted(
        Path(entry.path).stem.upper() for entry in kit.files
        if entry.path.startswith(kit.reference + "/") and entry.path.endswith(".parquet")
    )
    problems = []
    if sorted(datasets) != references:
        problems.append(f"built {sorted(datasets)}, the kit has references for {references}")
    results = []
    for name in datasets:
        reference = dest / kit.reference / f"{name.lower()}.parquet"
        if not reference.is_file():
            continue
        result = compare.compare_tables(
            name, pq.read_table(reference), pq.read_table(folder / ADAM / f"{name.lower()}.parquet")
        )
        results.append(result)
        out(result.line())
        if not result.equal:
            problems.append(f"{name}: differs from the reference")
    out(compare.total_line(results))
    out(compare.tolerance_line(results))
    for pair, count in compare.storage_summary(results).items():
        out(f"storage type only, same values (reference -> built): {pair} in {count} columns")
    for problem in problems:
        out(f"P2: {problem}")
    equal = sum(1 for result in results if result.equal)
    out(f"P2 reproduction: {equal} of {len(references)} datasets equal their reference "
        f"(numeric tolerance {compare.TOLERANCE:g})")
    return not problems


def trace(root: Path, kit_id: str, folder: Path | None = None, out: Out = print) -> bool:
    """Every output column of the built data has a complete derives_from path."""
    import pyarrow.parquet as pq

    found = _built(root, kit_id, folder, out)
    if found is None:
        return False
    kit, folder = found
    expected = {
        name: pq.read_schema(folder / ADAM / f"{name.lower()}.parquet").names
        for name in read_manifest(folder)["datasets"]
    }
    sdtm = {
        path.stem.upper(): set(pq.read_schema(path).names)
        for path in sorted((folder / kit.sdtm).glob("*.parquet"))
    }
    lines, problems = graph.check_graph(root, folder / GRAPH, expected, kit.trace_gaps, sdtm)
    for line in lines:
        out(line)
    with open(folder / GRAPH / "coverage.json", encoding="ascii") as handle:
        claims = json.load(handle).get("claims", {})
    for name, summary in claims.items():
        skipped = sum(summary["citations_not_to_kit_documents"].values())
        out(f"claims {name:9s} {summary['claims']:3d} claims, "
            f"{summary['citations_of_kit_documents']:3d} citations of kit documents -> "
            f"{summary['cites_edges']:3d} cites edges (one per column and span); "
            f"{skipped} citations of programs or other files, not imported; "
            f"{len(summary['variables_not_output_columns'])} variables that are not output columns")
    for problem in problems:
        out(f"trace: {problem}")
    out(f"trace: {'complete' if not problems else f'{len(problems)} problems'}")
    return not problems


def check(root: Path, kit_id: str, folder: Path | None = None, twice: bool = False,
          out: Out = print) -> int:
    """`specfirst check <kit>`: P2 and the trace on a build; with twice, P1 first."""
    results = []
    if twice:
        results.append(determinism(root, kit_id, out))
        folder = folder or build_dir(root) / "p1" / kit_id / "first"
    results.append(reproduction(root, kit_id, folder, out))
    results.append(trace(root, kit_id, folder, out))
    return 0 if all(results) else 1
