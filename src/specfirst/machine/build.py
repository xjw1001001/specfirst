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
from specfirst.machine import (
    ard,
    ars,
    compare,
    csr,
    graph,
    grid,
    methods,
    render,
    rengine,
    results,
    runner,
)
from specfirst.machine import layout as layouts
from specfirst.machine import registry as registries
from specfirst.machine.canonical import read_jsonl, sha256_file, write_json, write_parquet
from specfirst.paths import build_dir

Out = Callable[[str], None]
# What a build writes, relative to the folder it builds into.
RESOLVED, ADAM, GRAPH, MANIFEST = "gold/resolved", "gold/data/adam", "gold/graph", "gold/build.json"
# The results of real-2: the ARD of each engine and the ARS file with regenerated results.
ARD, ARS_OUT = "gold/ard", "gold/ars"
# The displays of real-3: per output <id>.json, the grid, and <id>.shell.json, its mock
# shell; and the pages that show them, <id>.html and <id>.shell.html.
GRID, PAGES = "gold/grid", "gold/out"
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
    for stale in (RESOLVED, ADAM, GRAPH, ARD, ARS_OUT, GRID, PAGES, WORK, MANIFEST):
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
    record = {
        "kit": kit.id,
        "kit_manifest_sha256": sha256_file(kits.manifest_path(root, kit.id)),
        "engines": {runner.ENGINE: installed, "pyarrow": pyarrow.__version__},
        "datasets": [plan.name for plan in plans],
    }
    if kit.results:
        displays: list[graph.Display] = []
        try:
            written += build_results(root, kit, into, record, out, displays)
        except (ars.ArsError, ard.EngineError, rengine.REngineError, results.ResultsError,
                registries.RegistryError, methods.MethodError, layouts.LayoutError,
                grid.GridError) as error:
            # A method that refuses its input (a Fisher table too large to sum) ends the
            # build like any other input that cannot be run.
            out(f"build {kit_id}: FAIL ({error})")
            return 1
        # The trace from the cells of the grids to the ADaM columns (real-3).
        graph.add_displays(trace, dest, displays)
    written += graph.write_graph(into / GRAPH, trace)
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


def build_displays(root: Path, into: Path, spec: kits.ResultSet, event: ars.Event,
                   rows: list[dict], displays: list[graph.Display], out: Out) -> list[Path]:
    """Build the grid, the mock shell and their pages for every output the kit lists.

    The grid is built from the rows of the Python engine: the gold ARD.
    """
    written: list[Path] = []
    by_id = results.by_id(rows)
    for display in spec.displays:
        layout = layouts.read(into / display.layout)
        if layout.output != display.output:
            raise layouts.LayoutError(f"{display.layout} is the layout of the output "
                                      f"'{layout.output}', the kit lists it for "
                                      f"'{display.output}'")
        made = {"": grid.build(event, layout, by_id), ".shell": grid.shell(event, layout)}
        for kind, value in made.items():
            problems = grid.grid_problems(value, root)
            if problems:
                raise grid.GridError(f"the grid of {display.output} is not valid: "
                                     + "; ".join(problems[:5]))
            path = into / GRID / f"{display.output}{kind}.json"
            write_json(path, value)
            page = into / PAGES / f"{display.output}{kind}.html"
            page.parent.mkdir(parents=True, exist_ok=True)
            page.write_bytes(render.html(value).encode("utf-8"))
            written += [path, page]
        displays.append(graph.Display(
            grid=made[""], grid_file=f"{GRID}/{display.output}.json", event=event,
            ars_file=spec.ars, ard_file=f"{ARD}/{spec.id}.jsonl", rows=rows,
            subject_key=spec.subject_key))
        cells = sum(len(row["cells"]) for row in made[""]["rows"])
        out(f"display {display.output}: {len(made['']['rows'])} rows x "
            f"{len(made['']['columns'])} columns, {cells} cells; its mock shell; a page for each")
    return written


def gold_rows(python: list[dict], r: list[dict], registry: registries.Registry) -> list[dict]:
    """The gold ARD: the Python engine's rows and the R engine's rows of the methods only R
    implements, the model-based ones (section 7.3, ADR-015), sorted by their ID."""
    r_only = results.r_only_methods(registry)
    if any(row["method_id"] in r_only for row in python):
        raise ard.EngineError("the Python engine gave a result of a model-based method")
    modelled = [row for row in r if row["method_id"] in r_only]
    return sorted([*python, *modelled], key=lambda row: row["id"]) if modelled else python


def build_results(root: Path, kit: kits.Kit, into: Path, record: dict, out: Out,
                  displays: list[graph.Display] | None = None) -> list[Path]:
    """Run both engines on every result set of the kit; write the two ARDs and the gold ARS.

    With `displays`, also build the grids of the outputs the kit lists, and
    add what the trace needs of each to that list.
    """
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
        # Model-based methods are R only (section 7.3, ADR-015): their rows of the gold
        # ARD are the R engine's.
        merged = gold_rows(rows, other, inputs.registry)
        if len(merged) != len(rows):
            out(f"results {spec.id}: {len(merged) - len(rows)} results of model-based methods "
                f"(R only) join the gold ARD, which has {len(merged)} rows")
            rows = merged
            results.write_ard(into / ARD / f"{spec.id}.jsonl", rows, root)
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
        if displays is not None:
            written += build_displays(root, into, spec, inputs.event, rows, displays, out)
    return written


def proof_evidence(root: Path, folder: Path, spec: kits.ResultSet) -> results.Evidence:
    """What a proof may ask for: our results under another value of a method option,
    and, from the Python engine on the built data, the values of a cell and the
    groups a test compares. Each is made when it is first asked for."""
    made: dict[tuple, results.Rows] = {}
    engines: list[ard.Engine] = []

    def build_with(method_id: str, option: str, value: object) -> results.Rows:
        key = (method_id, option, value)
        if key not in made:
            given = json.loads(json.dumps(spec.binding))
            given.setdefault("options", {}).setdefault(method_id, {})[option] = value
            inputs = result_inputs(root, folder, spec, given)
            made[key] = results.by_id(ard.run(inputs.event, inputs.registry, inputs.binding,
                                              inputs.tables, spec.subject_key))
        return made[key]

    def engine() -> ard.Engine:
        if not engines:
            inputs = result_inputs(root, folder, spec)
            engines.append(ard.Engine(inputs.event, inputs.registry, inputs.binding,
                                      inputs.tables, spec.subject_key))
        return engines[0]

    return results.Evidence(build_with, lambda key: engine().cell_values(key),
                            lambda analysis_id: engine().compared_groups(analysis_id))


def judge(label: str, event: ars.Event, registry: registries.Registry, rows: results.Rows,
          entries: list[dict], evidence: results.Evidence | results.Alternative,
          out: Out) -> tuple[bool, results.Comparison]:
    """P2 for the results of one engine: reproduced, or a difference with one class and a proof."""
    comparison = results.compare_reference(event, rows)
    lines, problems = results.check_exceptions(comparison, entries, rows, registry, evidence)
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
            evidence = proof_evidence(root, folder, spec)
            comparisons = {}
            for engine, lines in rows.items():
                problems += [f"{engine} ARD: {p}" for p in results.ard_problems(lines, root)]
                ok, comparison = judge(
                    f"results {spec.id}, {engine} engine", inputs.event, inputs.registry,
                    results.by_id(lines), listed.get(spec.id, []), evidence, out)
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
            # Rule R11 holds for the methods both engines implement. The results of a
            # model-based method are the R engine's in both files (ADR-015).
            r_only = results.r_only_methods(inputs.registry)
            both = {name: {key: row for key, row in results.by_id(found).items()
                           if row["method_id"] not in r_only} for name, found in rows.items()}
            modelled = {name: {key: row for key, row in results.by_id(found).items()
                               if row["method_id"] in r_only} for name, found in rows.items()}
            lines, disagreements = results.agreement(both["Python"], both["R"])
            # Only R stamps these rows: their options hash is held against the registry's.
            stamps = [
                f"{key}: the R engine stamps the options hash {row['method_options_hash']}, "
                "the registry gives another"
                for key, row in sorted(modelled["R"].items())
                if row["method_options_hash"] != inputs.registry.options_hash(
                    row["method_id"],
                    inputs.binding.options[row["analysis_id"]][row["method_id"]])]
            problems += stamps
            if modelled["Python"] != modelled["R"]:
                problems.append("the gold ARD does not hold the R engine's results of the "
                                "model-based methods as the R engine gave them")
            elif modelled["R"] and not stamps:
                out(f"results {spec.id}: {len(modelled['R'])} results of model-based methods "
                    "(R only, section 7.3): the gold ARD holds them as the R engine gave them, "
                    "each stamped with the registry's hash of its options")
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


def _read_json(path: Path) -> object:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def display_problems(root: Path, event: ars.Event, layout: layouts.Layout, made: object,
                     shell: object, pages: dict[str, str], rows: results.Rows,
                     other_rows: results.Rows,
                     classes: dict[str, str]) -> tuple[grid.DisplayComparison, list[str]]:
    """What is wrong with the built display of one output: `display_checks` has the list.

    `pages` holds the page of the grid under "" and that of the mock shell
    under ".shell". `rows` are the gold ARD, `other_rows` those of the second
    engine. `classes` gives the class of every result whose difference from
    the reference is explained.
    """
    problems = [f"grid: {p}" for p in grid.grid_problems(made, root)]
    problems += [f"shell: {p}" for p in grid.grid_problems(shell, root)]
    if problems:
        return grid.DisplayComparison(layout.output), problems
    compared = grid.compare_reference(event, layout, made, rows, classes)
    problems += compared.problems
    try:
        if grid.build(event, layout, other_rows) != made:
            problems.append("the rows of the second engine give another grid: a value at "
                            "the edge of a rounding, or a result one engine lacks")
        if grid.shell(event, layout) != shell:
            problems.append("the mock shell is not what the layout gives")
    except grid.GridError as error:
        problems.append(str(error))
    problems += [f"{cell['id']}: the mock shell shows a number: {cell['text']!r}"
                 for row in shell["rows"] for cell in row["cells"] if grid.numeric(cell)]
    for kind, value in (("", made), (".shell", shell)):
        problems += [f"page {layout.output}{kind}.html: {p}"
                     for p in render.projection_problems(value, pages[kind])]
    return compared, problems


def csr_reference_dir(root: Path, kit_id: str) -> Path:
    """Where the reference grids parsed from a CSR are written: an ignored folder of the
    checkout, never the fetch cache and never git (rule 4; ADR-015)."""
    return build_dir(root) / "csr" / kit_id


def csr_comparison(root: Path, kit: kits.Kit, folder: Path, display: kits.Display,
                   event: ars.Event, layout: layouts.Layout, made: dict, rows: results.Rows,
                   entries: list[dict]) -> csr.Comparison:
    """P2 for a grid whose reference is a CSR table: parse the page again, compare every
    cell, and hold each difference against its one entry (specfirst.machine.csr)."""
    reference = display.reference
    table = csr.read_table(folder / reference.file, reference.page, reference.table)
    write_json(csr_reference_dir(root, kit.id) / f"{reference.table}.json", table)
    decisions: dict[str, dict] = {}
    if kit.decisions:
        decisions = {record["id"]: record for record in read_jsonl(folder / kit.decisions)}
    return csr_against(made, table, event, layout, rows, entries, decisions)


def csr_against(made: dict, table: dict, event: ars.Event, layout: layouts.Layout,
                rows: results.Rows, entries: list[dict],
                decisions: set[str] | dict[str, dict]) -> csr.Comparison:
    """A grid against a parsed CSR table, each difference held against its entry.

    `decisions`: the kit's decision records by ID (or their IDs alone, which
    holds neither what a record binds nor an other analysis of a proof)."""
    compared = csr.compare(made, table)
    planned = grid.plan(event, layout, rows)
    cells = {f"cell:{made['output_id']}/r{number}/{cell.column}":
             (grid.template_of(row, cell), cell.shown)
             for number, row in enumerate(planned.rows, start=1) for cell in row.cells}
    csr.judge(compared, entries, cells, {key: row["raw_value"] for key, row in rows.items()},
              decisions, event.analyses)
    return compared


def display_checks(root: Path, kit_id: str, folder: Path | None = None,
                   out: Out = print) -> tuple[bool, list[dict]]:
    """P2 for grid text, on a build. Returns whether all holds, and the counts per output.

    For every output the kit lists: the grid fits its schema and is what the
    layout and the ARD give; every cell text is the reference's formatted
    value, or its difference has one class (specfirst.machine.grid); the rows
    of the R engine give the same grid; the mock shell is what the layout
    gives without results and shows no number; each page is a projection of
    its grid.
    """
    found = _built(root, kit_id, folder, out)
    if found is None:
        return False, []
    kit, folder = found
    passed, counts = True, []
    try:
        listed = results.load_exceptions(folder / kit.exceptions) if kit.exceptions else {}
        cell_entries = csr.load_exceptions(folder / kit.exceptions) if kit.exceptions else {}
        outputs = {display.output for spec in kit.results for display in spec.displays
                   if display.reference is not None}
        for output in sorted(set(cell_entries) - outputs):
            out(f"grids: the exceptions name cells of {output}, which has no CSR reference")
            passed = False
        for spec in kit.results:
            if not spec.displays:
                continue
            inputs = result_inputs(root, folder, spec)
            rows = {name: results.by_id(read_jsonl(folder / ARD / f"{spec.id}{suffix}.jsonl"))
                    for name, suffix in (("Python", ""), ("R", ".r"))}
            comparison = results.compare_reference(inputs.event, rows["Python"])
            explained, _ = results.judge_entries(
                comparison, listed.get(spec.id, []), rows["Python"], inputs.registry,
                proof_evidence(root, folder, spec))
            classes = {key: entry["class"] for key, entry in explained.items()}
            for display in spec.displays:
                layout = layouts.read(folder / display.layout)
                made = _read_json(folder / GRID / f"{display.output}.json")
                shell = _read_json(folder / GRID / f"{display.output}.shell.json")
                pages = {kind: (folder / PAGES / f"{display.output}{kind}.html").read_text(
                    encoding="utf-8") for kind in ("", ".shell")}
                compared, problems = display_problems(
                    root, inputs.event, layout, made, shell, pages, rows["Python"], rows["R"],
                    classes)
                if display.reference is not None:
                    # The reference is a CSR table: the event embeds no formatted value.
                    against = csr_comparison(root, kit, folder, display, inputs.event, layout,
                                             made, rows["Python"],
                                             cell_entries.get(display.output, []))
                    problems += against.problems
                    for line in against.lines():
                        out(line)
                    out(f"grid {display.output}: the R engine's rows give the same grid; the "
                        f"mock shell and the two pages hold; {len(problems)} problems"
                        if not problems else f"grid {display.output}: {len(problems)} problems")
                    for problem in problems[:UNEXPLAINED_SHOWN]:
                        out(f"  grid {display.output}: {problem}")
                    passed &= not problems
                    counts.append({
                        "set": spec.id, "output": display.output, "reference": "csr",
                        "cells": against.cells, "printed": against.printed,
                        "equal": against.equal, "differing": len(against.differing),
                        "classified": len(against.classified),
                        "classes": dict(Counter(against.classified.values())),
                        "problems": len(problems)})
                    continue
                for line in compared.lines():
                    out(line)
                for problem in problems[:UNEXPLAINED_SHOWN]:
                    out(f"  grid {display.output}: {problem}")
                if len(problems) > UNEXPLAINED_SHOWN:
                    out(f"  grid {display.output}: and {len(problems) - UNEXPLAINED_SHOWN} more")
                out(f"grid {display.output}: the R engine's rows give the same grid; the mock "
                    f"shell and the two pages hold; {len(problems)} problems"
                    if not problems else f"grid {display.output}: {len(problems)} problems")
                passed &= not problems
                counts.append({
                    "set": spec.id, "output": display.output, "reference": "ars",
                    "cells": compared.cells,
                    "results": compared.results, "equal": compared.equal,
                    "differing": len(compared.differing),
                    "classified": sum(compared.classified.values()),
                    "no_reference": len(compared.no_reference), "problems": len(problems),
                })
    except (ars.ArsError, ard.EngineError, results.ResultsError, registries.RegistryError,
            layouts.LayoutError, csr.CsrError, grid.GridError, OSError, ValueError) as error:
        out(f"grids: {error}")
        passed = False
    out(f"grids: {len(counts)} outputs, {'pass' if passed else 'FAIL'}")
    return passed, counts


def decision_checks(root: Path, kit_id: str, folder: Path | None = None,
                    out: Out = print) -> bool:
    """The kit's decision records against its reporting events (specfirst.machine.decisions)."""
    from specfirst.machine import decisions

    found = _built(root, kit_id, folder, out)
    if found is None:
        return False
    kit, folder = found
    if not kit.decisions:
        out("decisions: the kit names no decision records")
        return True
    try:
        records = decisions.load(folder / kit.decisions)
        events, engines = [], []
        registry = None
        for spec in kit.results:
            inputs = result_inputs(root, folder, spec)
            events.append((inputs.event, inputs.binding))
            engines.append(ard.Engine(inputs.event, inputs.registry, inputs.binding,
                                      inputs.tables, spec.subject_key))
            registry = inputs.registry
        lines, problems = decisions.problems(root, records, events, registry, engines)
    except (ars.ArsError, registries.RegistryError, OSError, ValueError) as error:
        out(f"decisions: {error}")
        return False
    for line in lines:
        out(line)
    # A record in conflict has no class (section 4.5): it is counted by its status.
    by_class = Counter(str(record.get("class") or f"no class ({record.get('status')})")
                       for record in records)
    by_status = Counter(str(record.get("status")) for record in records)
    out("decisions: by class: " + ", ".join(f"{count} {name}"
                                           for name, count in sorted(by_class.items()))
        + "; by status: " + ", ".join(f"{count} {name}"
                                      for name, count in sorted(by_status.items())))
    for problem in problems:
        out(f"decisions: {problem}")
    out(f"decisions: {'pass' if not problems else 'FAIL'}")
    return not problems


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
    # From the cells of the grids to SDTM columns (real-3).
    grids = {display.output: _read_json(folder / GRID / f"{display.output}.json")
             for spec in kit.results for display in spec.displays}
    if grids:
        lines, behind = graph.check_cells(folder / GRAPH, grids)
        for line in lines:
            out(line)
        problems += behind
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
    passed.append(display_checks(root, kit_id, folder, out)[0])
    return 0 if all(passed) else 1
