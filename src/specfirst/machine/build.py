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
import time
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from specfirst import kit as kits
from specfirst.machine import ard, ars, compare, graph, rengine, results, runner
from specfirst.machine import registry as registries
from specfirst.machine.canonical import read_jsonl, sha256_file, write_json, write_parquet
from specfirst.paths import build_dir

Out = Callable[[str], None]
# What a build writes, relative to the folder it builds into.
RESOLVED, ADAM, GRAPH, MANIFEST = "gold/resolved", "gold/data/adam", "gold/graph", "gold/build.json"
# The results of real-2: the ARD of each engine and the ARS file with regenerated results.
ARD, ARS_OUT = "gold/ard", "gold/ars"
# Working files of a build (what is handed to the R engine); not part of what was built.
WORK = "work"
# How many unexplained differences a check prints one by one.
UNEXPLAINED_SHOWN = 30


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
    for stale in (RESOLVED, ADAM, GRAPH, ARD, ARS_OUT, WORK, MANIFEST):
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
    record = {
        "kit": kit.id,
        "kit_manifest_sha256": sha256_file(kits.manifest_path(root, kit.id)),
        "engines": {runner.ENGINE: installed, "pyarrow": pyarrow.__version__},
        "datasets": [plan.name for plan in plans],
    }
    if kit.results:
        try:
            written += build_results(root, kit, into, record, out)
        except (ars.ArsError, ard.EngineError, rengine.REngineError, results.ResultsError,
                registries.RegistryError) as error:
            out(f"build {kit_id}: FAIL ({error})")
            return 1
    files = {path.relative_to(into).as_posix(): sha256_file(path) for path in sorted(written)}
    write_json(into / MANIFEST, {**record, "files": files})
    out(f"build {kit_id}: {len(plans)} datasets, {len(trace.nodes)} nodes, "
        f"{len(trace.edges)} edges, {len(files)} files in {into}")
    return 0


@dataclass
class ResultInputs:
    """What both engines read for one result set of a kit."""

    spec: kits.ResultSet
    event: ars.Event
    registry: registries.Registry
    binding: ars.Binding
    tables: dict[str, ard.Table]


def result_inputs(root: Path, folder: Path, spec: kits.ResultSet,
                  binding: dict | None = None) -> ResultInputs:
    """Read the reporting event, the registry and the built ADaM data of a result set.

    The reporting event must fit the schema generated from the ARS model
    when the kit pins one. The data are the ADaM datasets this build made,
    not the reference and not the fetch cache.
    """
    data = ars.read(folder / spec.ars)
    if spec.schema:
        problems = ars.schema_problems(data, ars.read(folder / spec.schema))
        if problems:
            raise ars.ArsError(f"{spec.ars} does not fit the ARS schema: "
                               + "; ".join(problems[:5]))
    event = ars.index(data)
    if event.problems:
        raise ars.ArsError(f"{spec.ars}: " + "; ".join(event.problems[:5]))
    registry = registries.load(root)
    stale = registries.json_problems(root)
    if stale:
        raise registries.RegistryError("; ".join(stale))
    bound = ars.bind(event, registry, spec.binding if binding is None else binding)
    tables = ard.load_tables(folder / ADAM, ars.columns(event, spec.subject_key))
    return ResultInputs(spec, event, registry, bound, tables)


def build_results(root: Path, kit: kits.Kit, into: Path, record: dict, out: Out) -> list[Path]:
    """Run both engines on every result set of the kit; write the two ARDs and the gold ARS."""
    written: list[Path] = []
    record["registry_sha256"] = sha256_file(registries.json_path(root))
    for spec in kit.results:
        started = time.monotonic()
        inputs = result_inputs(root, into, spec)
        read = time.monotonic()
        rows = ard.run(inputs.event, inputs.registry, inputs.binding, inputs.tables,
                       spec.subject_key)
        done = time.monotonic()
        results.write_ard(into / ARD / f"{spec.id}.jsonl", rows, root)
        out(f"results {spec.id}: Python engine, {len(inputs.event.analyses)} analyses, "
            f"{len(rows)} rows in {done - read:.1f} s (reading the files: {read - started:.1f} s)")
        other, meta, _ = rengine.run(
            root, into / WORK / spec.id, into / spec.ars, registries.json_path(root),
            inputs.binding, inputs.tables, spec.subject_key)
        problems = rengine.data_problems(meta, inputs.tables)
        if problems:
            raise rengine.REngineError("; ".join(problems))
        results.write_ard(into / ARD / f"{spec.id}.r.jsonl", other, root)
        out(f"results {spec.id}: R engine {meta.get('r')}, {len(other)} rows in "
            f"{meta.get('seconds')} s; it read the same values of {len(meta['columns'])} columns")
        record["engines"]["R"] = meta.get("r")
        gold = results.with_results(inputs.event, rows)
        if spec.schema:
            problems = ars.schema_problems(gold, ars.read(into / spec.schema))
            if problems:
                raise ars.ArsError(f"the ARS file with our results does not fit the ARS "
                                   f"schema: {'; '.join(problems[:5])}")
        write_json(into / ARS_OUT / f"{spec.id}.json", gold)
        written += [into / ARD / f"{spec.id}.jsonl", into / ARD / f"{spec.id}.r.jsonl",
                    into / ARS_OUT / f"{spec.id}.json"]
    return written


def alternatives(root: Path, folder: Path, spec: kits.ResultSet) -> results.Alternative:
    """Our results under another value of a method option: what a proof may ask for."""
    made: dict[tuple, results.Rows] = {}

    def build_with(method_id: str, option: str, value: object) -> results.Rows:
        key = (method_id, option, value)
        if key not in made:
            given = json.loads(json.dumps(spec.binding))
            given.setdefault("options", {}).setdefault(method_id, {})[option] = value
            inputs = result_inputs(root, folder, spec, given)
            made[key] = results.by_id(ard.run(inputs.event, inputs.registry, inputs.binding,
                                              inputs.tables, spec.subject_key))
        return made[key]

    return build_with


def judge(label: str, event: ars.Event, registry: registries.Registry, rows: results.Rows,
          entries: list[dict], alternative: results.Alternative,
          out: Out) -> tuple[bool, results.Comparison]:
    """P2 for the results of one engine: reproduced, or a difference with one class and a proof."""
    comparison = results.compare_reference(event, rows)
    lines, problems = results.check_exceptions(comparison, entries, rows, registry, alternative)
    out(f"{label}: {comparison.total} embedded results, {comparison.reproduced} reproduced as "
        f"printed, {len(comparison.differing)} with another value, {len(comparison.absent)} "
        "without a result of ours")
    out(f"  reproduced as printed, but not at the precision of the result pattern: "
        f"{len(comparison.coarse)} (each needs a class, like the others)")
    for key, (printed, value) in sorted(comparison.coarse.items())[:UNEXPLAINED_SHOWN]:
        out(f"    {key}: embedded {printed}, ours {value!r}")
    if comparison.edge:
        out(f"  equal only at the edge of the allowance: {len(comparison.edge)}")
        for key, printed, value in comparison.edge[:UNEXPLAINED_SHOWN]:
            out(f"    {key}: embedded {printed}, ours {value!r}")
    for line in lines:
        out(line)
    for problem in problems[:UNEXPLAINED_SHOWN]:
        out(f"  unexplained: {problem}")
    if len(problems) > UNEXPLAINED_SHOWN:
        out(f"  unexplained: and {len(problems) - UNEXPLAINED_SHOWN} more")
    if problems:  # where to look: by analysis, and whether groups look exchanged
        by_analysis = Counter(problem[len("ard:"):].split("/")[0] for problem in problems
                              if problem.startswith("ard:"))
        out("  unexplained differences by analysis: "
            + ", ".join(f"{name} {count}" for name, count in sorted(by_analysis.items())))
        for grouping, count in sorted(results.exchanged(event, comparison, rows).items()):
            out(f"  {count} of the {len(comparison.differing)} other values are our value of "
                f"another group of {grouping}")
    out(f"{label}: {len(problems)} unexplained")
    return not problems, comparison


def result_checks(root: Path, kit_id: str, folder: Path | None = None,
                  out: Out = print) -> tuple[bool, list[dict]]:
    """P2 for results and rule R11, on a build. Returns whether all hold, and the counts.

    For every result set of the kit: the ARS files fit the ARS schema; each
    engine reproduces the results the reference embeds or the difference is
    classified with a proof that holds; and the two engines agree.
    """
    found = _built(root, kit_id, folder, out)
    if found is None:
        return False, []
    kit, folder = found
    if not kit.results:
        out("results: the kit names no ARS file")
        return True, []
    passed, counts = True, []
    try:
        listed = results.load_exceptions(folder / kit.exceptions) if kit.exceptions else {}
        stray = sorted(set(listed) - {spec.id for spec in kit.results})
        if stray:
            raise results.ResultsError(f"exceptions for {', '.join(stray)}: no such result set")
        for spec in kit.results:
            inputs = result_inputs(root, folder, spec)
            gold = ars.read(folder / ARS_OUT / f"{spec.id}.json")
            problems = ars.schema_problems(gold, ars.read(folder / spec.schema)) if spec.schema \
                else []
            if spec.schema:
                out(f"ARS schema ({spec.schema}): {spec.ars} fits; {ARS_OUT}/{spec.id}.json "
                    f"{'fits' if not problems else 'does not fit'}")
            rows = {
                "Python": read_jsonl(folder / ARD / f"{spec.id}.jsonl"),
                "R": read_jsonl(folder / ARD / f"{spec.id}.r.jsonl"),
            }
            alternative = alternatives(root, folder, spec)
            comparisons = {}
            for engine, lines in rows.items():
                problems += [f"{engine} ARD: {p}" for p in results.ard_problems(lines, root)]
                ok, comparison = judge(
                    f"results {spec.id}, {engine} engine", inputs.event, inputs.registry,
                    results.by_id(lines), listed.get(spec.id, []), alternative, out)
                passed &= ok
                comparisons[engine] = comparison
                counts.append({
                    "set": spec.id, "engine": engine, "total": comparison.total,
                    "reproduced": comparison.reproduced,
                    "not_reproduced": len(comparison.open), "explained": ok,
                })
            extra = comparisons["Python"].extra
            if extra:
                out(f"results {spec.id}: {sum(extra.values())} results of ours that the "
                    "reference does not list: "
                    + ", ".join(f"{name} {count}" for name, count in sorted(extra.items())))
            carried = {key: item.printed
                       for key, item in results.embedded(ars.index(gold)).items()}
            ours = {row["id"]: results.raw_text(row["raw_value"]) or "" for row in rows["Python"]}
            if carried != ours:
                problems.append(f"{ARS_OUT}/{spec.id}.json does not carry the results of the ARD")
            else:
                out(f"results {spec.id}: {ARS_OUT}/{spec.id}.json carries the {len(ours)} "
                    "results of the Python ARD as raw values")
            lines, disagreements = results.agreement(results.by_id(rows["Python"]),
                                                     results.by_id(rows["R"]))
            for line in lines:
                out(f"results {spec.id}, {line}")
            for problem in [*problems, *disagreements[:20]]:
                out(f"results {spec.id}: {problem}")
            if len(disagreements) > 20:
                out(f"results {spec.id}: and {len(disagreements) - 20} more disagreements")
            passed &= not problems and not disagreements
    except (ars.ArsError, ard.EngineError, results.ResultsError, registries.RegistryError,
            OSError, ValueError) as error:
        out(f"results: {error}")
        passed = False
    out(f"results: {'pass' if passed else 'FAIL'}")
    return passed, counts


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
    for key in ("kit", "kit_manifest_sha256", "engines", "datasets", "registry_sha256"):
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
    """`specfirst check <kit>`: P2, the trace and the results on a build; with twice, P1 first."""
    passed = []
    if twice:
        passed.append(determinism(root, kit_id, out))
        folder = folder or build_dir(root) / "p1" / kit_id / "first"
    passed.append(reproduction(root, kit_id, folder, out))
    passed.append(trace(root, kit_id, folder, out))
    passed.append(result_checks(root, kit_id, folder, out)[0])
    return 0 if all(passed) else 1
