"""The evidence behind ADR-001, on the fetch cache and the assembled pilot kit.

    A1-resolve  the yamaa wheel composes each pilot specification to exactly
                the snapshot Pilot 7 committed, which its own runner made with
                yamaa built from the git revision Pilot 7 pins (E19)
    A2-runner   our runner (kit layout, every input in memory) builds the same
                tables as yamaa's own project run on Pilot 7's layout
    A3-lineage  specfirst.machine.lineage gives the same column dependencies as
                Pilot 7's own code, run from the cache at the pinned commit
    A4-unread   the graph against the engine: with every SDTM column that has
                no node in the graph changed (rolled by one row; emptied when
                it holds one value; filled when it is all missing), the build
                gives the same ADaM
    A5-adapted  no Python file of ours shares more than a few lines with a
                Python file of a cached source, and no R file of ours with an
                R file of one, unless third_party/SOURCES.md records it as
                adapted code
    A6-engine   the Python result engine runs the 31 analyses of the ARS
                example on the built ADaM in under 10 seconds, reproduces
                3,711 of its 3,735 embedded results (real-2; E2) and gives
                the expected number of rows for every analysis

A4 is the check the trace check cannot make by itself: a reference that the
dependency analysis misses leaves graph files that agree with each other.
A5 is the check a table cannot make: it finds an adaptation nobody recorded.
It compares lines, so it finds code taken over nearly as it was (the
function behind finding F1 of the review shared 3 lines; 2 are allowed),
not code that was rewritten line by line.

These tests need `specfirst fetch` and carry the marker `evidence`, like the
spikes: `make test` leaves them out and `specfirst gate real-1` runs them. A
missing cache skips them, except under SPECFIRST_STRICT=1 (set by the gate),
where it fails: a gate never passes by skipping.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import pytest

from specfirst import kit as kits
from specfirst.machine import graph, runner
from specfirst.machine.canonical import json_text
from specfirst.machine.lineage import column_dependencies
from specfirst.paths import cache_dir, repo_root

pytestmark = pytest.mark.evidence

KIT = "cdiscpilot01"
PROJECT = "cdiscpilot01/spec/yamaa/project.yaml"
ENGINE_PIN = "cdiscpilot01/program/adam/python/requirements.txt"
# A5: the sources whose Python files are compared with ours, and how many
# lines an unrecorded file of ours may share with them (common idioms).
COMPARED_SOURCES = ("p7", "yamaa", "p6", "ars")
SHARED_LINES_ALLOWED = 2
IDIOMS = (".mkdir(",)  # lines every Python program has; they are not counted
ADAPTED_ROW = re.compile(r"^\| `([^`|]+\.(?:py|R))` \| https://github\.com/", re.MULTILINE)


class Missing(RuntimeError):
    """The fetch cache or the engine is not there."""


@dataclass
class Pilot:
    root: Path
    cache: Path
    p7: Path  # Pilot 7 in the fetch cache
    kit: kits.Kit
    dest: Path  # the assembled kit
    plans: list[runner.SpecPlan] | None = None  # the build, made once

    def built(self) -> list[runner.SpecPlan]:
        if self.plans is None:
            self.plans = runner.run_project(self.dest, self.kit.project, self.kit.sdtm)
        return self.plans


@pytest.fixture(scope="session")
def pilot(tmp_path_factory) -> Pilot:
    root = repo_root()
    cache = cache_dir(root)
    kit = kits.load_kit(root, KIT)
    return Pilot(root, cache, cache / "p7", kit, tmp_path_factory.mktemp("pilot") / KIT)


def assembled(pilot: Pilot) -> None:
    for source in sorted(pilot.kit.sources):
        if not (pilot.cache / source / ".git").exists():
            raise Missing(f"not in the fetch cache: {source}; run `specfirst fetch`")
    try:
        import yamaa  # noqa: F401
    except ImportError as error:
        raise Missing(f"yamaa is not installed: {error}") from error
    if not (pilot.dest / "kit.yaml").is_file():
        problems = kits.assemble(pilot.root, pilot.kit, pilot.dest)
        assert problems == [], problems


def a1_resolve(pilot: Pilot) -> list[str]:
    import yamaa

    project_file = pilot.p7 / PROJECT
    project = yamaa.project(str(project_file))
    problems, made_with = [], set()
    for name in project.names:
        record = runner._relocate(project.spec(name).resolve(), pilot.p7)
        snapshot_file = project_file.parent / "resolved" / Path(record["entry"]).name
        with open(snapshot_file.with_suffix(".inspection.json"), encoding="ascii") as handle:
            snapshot = json.load(handle)
        made_with.add((snapshot["yamaa_version"], snapshot["yamaa_revision"]))
        same = json_text(record) == json_text(snapshot["resolved"])
        print(f"{name:9s} composed specification equals Pilot 7's snapshot: {same}")
        if not same:
            problems.append(f"{name}: the wheel resolves the specification differently")
    pin = re.search(r"yamaa\.git@([0-9a-f]{40})", (pilot.p7 / ENGINE_PIN).read_text("ascii"))
    pinned = pin.group(1) if pin else None
    print(f"Pilot 7 pins yamaa at git revision {pinned} ({ENGINE_PIN})")
    for version, revision in sorted(made_with):
        print(f"snapshots were made with yamaa {version} built from git revision {revision}")
        if version != yamaa.__version__:
            problems.append(f"snapshot is of yamaa {version}, installed is {yamaa.__version__}")
        if revision != pinned:
            problems.append(f"snapshot is of revision {revision}, Pilot 7 pins {pinned}")
    print(f"installed: yamaa {yamaa.__version__} (wheel)")
    return problems


def a2_runner(pilot: Pilot) -> list[str]:
    import yamaa

    plans = pilot.built()
    runs = yamaa.project(str(pilot.p7 / PROJECT)).run("adam")
    problems = []
    if runs.status != "succeeded" or list(runs.names) != [plan.name for plan in plans]:
        problems.append(f"yamaa's project run: {runs.status}, {list(runs.names)}")
    for plan in plans:
        theirs = runs[plan.name].output.to_arrow()
        same = theirs.schema.equals(plan.table.schema) and theirs.equals(plan.table)
        print(f"{plan.name:9s} {plan.table.num_rows:6d} rows x {plan.table.num_columns:3d} "
              f"columns: runner equals yamaa's project run: {same}")
        if not same:
            problems.append(f"{plan.name}: the runner and yamaa's project run differ")
    left = sorted(p.name for p in (pilot.p7 / "cdiscpilot01/data/adam").glob("*-yamaa.parquet"))
    if left:
        problems.append(f"the run wrote into the fetch cache: {left}")
    return problems


def a3_lineage(pilot: Pilot) -> list[str]:
    import pyarrow.parquet as pq
    import yaml

    # Importing from the cache must not leave bytecode there: the cache has to
    # stay exactly what was fetched (lesson 13).
    scripts = pilot.p7 / ".github" / "scripts"
    writes_bytecode, sys.dont_write_bytecode = sys.dont_write_bytecode, True
    sys.path.insert(0, str(scripts))
    try:
        from study_dashboard.lineage import build_lineage
    finally:
        sys.path.remove(str(scripts))
        sys.dont_write_bytecode = writes_bytecode
    plans = runner.resolve_project(pilot.dest, pilot.kit.project, pilot.kit.sdtm)
    produced = {plan.name: set(plan.columns) for plan in plans}
    problems = []
    for plan in plans:
        columns = {
            source.alias: produced[source.dataset] if source.layer == "adam"
            else set(pq.read_schema(pilot.dest / source.file).names)
            for source in plan.inputs
        }
        ours = column_dependencies(plan.specification, columns)
        theirs = build_lineage(
            yaml.safe_dump(plan.specification, sort_keys=False), plan.specification,
            {alias: set(names) for alias, names in columns.items()},
        )
        same = ours.edges() == theirs["edges"]
        unresolved = sorted({name for read in ours.reads for name in read.unresolved})
        print(f"{plan.name:9s} {len(theirs['edges']):4d} elements: dependencies equal "
              f"Pilot 7's: {same}; unresolved ours {unresolved} theirs {theirs['unresolved']}")
        if not same:
            problems.append(f"{plan.name}: dependencies differ from Pilot 7's lineage")
        if unresolved != theirs["unresolved"]:
            problems.append(f"{plan.name}: unresolved names differ from Pilot 7's lineage")
    left = sorted(p.relative_to(pilot.p7).as_posix() for p in scripts.rglob("__pycache__"))
    if left:
        problems.append(f"the import wrote into the fetch cache: {left}")
    return problems


def changed_column(column):
    """A column of the same type with other content, and how it was changed.

    A column with more than one value is rolled: the same values, one row
    down. A roll changes nothing in a column that holds one value, so such a
    column is emptied, and a column that is all missing is filled (review of
    real-1, finding N1). Returns (None, reason) when nothing can be done.
    """
    import pyarrow as pa

    types = pa.types
    last = len(column) - 1
    if last < 0:
        return None, "no rows"
    turned = pa.concat_arrays([column.slice(last), column.slice(0, last)])
    if not turned.equals(column):
        return turned, "rolled"
    if column.null_count < len(column):
        return pa.nulls(len(column), column.type), "constant, emptied"
    kind = column.type
    if types.is_string(kind) or types.is_large_string(kind):
        value = "X"
    elif types.is_integer(kind) or types.is_floating(kind):
        value = 1
    elif types.is_boolean(kind):
        value = True
    else:
        return None, f"all missing, of type {kind}"
    return pa.array([value] * len(column), kind), "all missing, filled"


def a4_unread(pilot: Pilot) -> list[str]:
    """Change every SDTM column that has no node, and build again."""
    import pyarrow.parquet as pq

    plans = pilot.built()
    read = {node["id"] for node in graph.build_graph(pilot.kit, pilot.dest, plans).nodes
            if node["layer"] == "L3"}
    rolled = pilot.dest.parent / "rolled"
    if rolled.exists():
        shutil.rmtree(rolled)
    shutil.copytree(pilot.dest / "gold" / "spec", rolled / "gold" / "spec")
    (rolled / pilot.kit.sdtm).mkdir(parents=True)
    how: dict[str, int] = {}
    problems = []
    for path in sorted((pilot.dest / pilot.kit.sdtm).glob("*.parquet")):
        table = pq.read_table(path)
        for index, name in enumerate(table.schema.names):
            node = f"sdtm:{path.stem.upper()}.{name}"
            if node in read:
                continue
            column = table.column(index).combine_chunks()
            other, done = changed_column(column)
            how[done] = how.get(done, 0) + 1
            if other is None:
                problems.append(f"{node}: could not be changed ({done})")
                continue
            assert other.type == column.type and not other.equals(column)
            table = table.set_column(index, table.schema.field(index), other)
        pq.write_table(table, rolled / pilot.kit.sdtm / path.name)
    count = sum(how.values())
    if not count:
        problems.append("no column changed: the test would prove nothing")
    try:
        again = runner.run_project(rolled, pilot.kit.project, pilot.kit.sdtm)
    except runner.RunnerError as error:
        return [*problems, f"the build on the changed data failed: {error}"]
    changed = [plan.name for plan, other in zip(plans, again, strict=True)
               if not other.table.equals(plan.table)]
    detail = ", ".join(f"{number} {done}" for done, number in sorted(how.items()))
    print(f"SDTM columns with a node in the graph: {len(read)}; without one: {count}, every "
          f"one of them changed ({detail})")
    print(f"ADaM datasets that changed: {changed or 'none'}")
    if changed:
        problems.append(f"the build reads an SDTM column that has no node: {changed} changed")
    return problems


def _code_lines(path: Path) -> set[str]:
    """Lines of more than 30 characters, white space removed; no comments, imports, idioms."""
    found = set()
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        text = "".join(line.split())
        if len(text) > 30 and not text.startswith(("#", "import", "from")):
            if not any(idiom in text for idiom in IDIOMS):
                found.add(text)
    return found


def a5_adapted(pilot: Pilot) -> list[str]:
    sources = (pilot.root / "third_party" / "SOURCES.md").read_text(encoding="ascii")
    recorded = set(ADAPTED_ROW.findall(sources))
    theirs: dict[str, str] = {}
    files = 0
    for source in COMPARED_SOURCES:
        for path in sorted((pilot.cache / source).rglob("*.py")):
            if ".git" in path.relative_to(pilot.cache).parts:
                continue
            files += 1
            for line in _code_lines(path):
                theirs.setdefault(line, f"{source}:{path.relative_to(pilot.cache / source)}")
    problems, most = [], 0
    ours = sorted([*(pilot.root / "src").rglob("*.py"), *(pilot.root / "tests").rglob("*.py")])
    for path in ours:
        name = path.relative_to(pilot.root).as_posix()
        shared = sorted(_code_lines(path) & set(theirs))
        if name in recorded:
            print(f"recorded as adapted: {name} shares {len(shared)} lines with cached sources")
        elif len(shared) > SHARED_LINES_ALLOWED:
            problems.append(f"{name}: shares {len(shared)} lines with cached sources, for "
                            f"example with {theirs[shared[0]]}, and is not in SOURCES.md")
        else:
            most = max(most, len(shared))
    print(f"compared {len(ours)} Python files of ours with {files} of "
          f"{', '.join(COMPARED_SOURCES)}; the most lines a file that is not recorded shares: "
          f"{most} (allowed: {SHARED_LINES_ALLOWED})")
    # The same for the R engine, against the R files of every cached source (review of
    # real-2, finding F7: siera, cards and cardx were tried before the engine was written).
    theirs, files, most = {}, 0, 0
    sources = sorted(path.name for path in pilot.cache.iterdir() if (path / ".git").exists())
    for source in sources:
        folder = pilot.cache / source
        for path in sorted([*folder.rglob("*.R"), *folder.rglob("*.r")]):
            if ".git" in path.relative_to(pilot.cache).parts or not path.is_file():
                continue
            files += 1
            for line in _code_lines(path):
                theirs.setdefault(line, f"{source}:{path.relative_to(pilot.cache / source)}")
    ours = sorted((pilot.root / "r").rglob("*.R"))
    for path in ours:
        name = path.relative_to(pilot.root).as_posix()
        shared = sorted(_code_lines(path) & set(theirs))
        if name in recorded:
            print(f"recorded as adapted: {name} shares {len(shared)} lines with cached sources")
        elif len(shared) > SHARED_LINES_ALLOWED:
            problems.append(f"{name}: shares {len(shared)} lines with cached sources, for "
                            f"example with {theirs[shared[0]]}, and is not in SOURCES.md")
        else:
            most = max(most, len(shared))
    print(f"compared {len(ours)} R files of ours with {files} of {len(sources)} cached sources; "
          f"the most lines a file that is not recorded shares: {most} (allowed: "
          f"{SHARED_LINES_ALLOWED})")
    if not ours or not files:
        problems.append("no R file was compared: the test would prove nothing")
    for name in sorted(recorded):
        if not (pilot.root / name).is_file():
            problems.append(f"{name}: recorded in SOURCES.md, but there is no such file")
    return problems


# A6: the results every analysis of the ARS example gives on the pilot data. 504 of
# the 4,238 are not listed by the reference (F6 of the review of real-2): for them
# the agreement of the two engines is the only check, and it cannot see a result
# that both lack. These numbers can: a result lost in the engine changes one.
ROWS_PER_ANALYSIS = {
    "An01_05_SAF_Summ_ByTrt": 3,
    "An03_01_Age_Summ_ByTrt": 24,
    "An03_01_Age_Comp_ByTrt": 1,
    "An03_02_AgeGrp_Summ_ByTrt": 12,
    "An03_02_AgeGrp_Comp_ByTrt": 1,
    "An03_03_Sex_Summ_ByTrt": 12,
    "An03_03_Sex_Comp_ByTrt": 1,
    "An03_04_Ethnic_Summ_ByTrt": 12,
    "An03_04_Ethnic_Comp_ByTrt": 1,
    "An03_05_Race_Summ_ByTrt": 54,
    "An03_05_Race_Comp_ByTrt": 1,
    "An03_06_Height_Summ_ByTrt": 24,
    "An03_06_Height_Comp_ByTrt": 1,
    "An07_01_TEAE_Summ_ByTrt": 6,
    "An07_01_TEAE_Comp_ByTrt_PlacLow": 1,
    "An07_01_TEAE_Comp_ByTrt_PlacHigh": 1,
    "An07_02_RelTEAE_Summ_ByTrt": 6,
    "An07_03_SerTEAE_Summ_ByTrt": 6,
    "An07_04_RelSerTEAE_Summ_ByTrt": 6,
    "An07_05_TEAELd2Dth_Summ_ByTrt": 6,
    "An07_06_RelTEAELd2Dth_Summ_ByTrt": 6,
    "An07_07_TEAELd2DoseMod_Summ_ByTrt": 6,
    "An07_08_TEAELd2TrtDsc_Summ_ByTrt": 6,
    "An07_09_Soc_Summ_ByTrt": 138,
    "An07_09_Soc_Comp_ByTrt_PlacLow": 22,
    "An07_09_Soc_Comp_ByTrt_PlacHigh": 22,
    "An07_10_SocPt_Summ_ByTrt": 1380,
    "An07_10_SocPt_Comp_ByTrt_PlacLow": 180,
    "An07_10_SocPt_Comp_ByTrt_PlacHigh": 187,
    "An08_01_Obs_Summ_ByTrt": 1056,
    "An08_02_ChgBl_Summ_ByTrt": 1056,
}


def a6_engine(pilot: Pilot) -> list[str]:
    """The Python result engine on the pilot: what it reproduces, and how long it takes.

    PLAN.md section 13.3 (real-2): the spike took about 3 minutes; the
    target is under 10 seconds. The time is from reading the ARS file to the
    last row, on the ADaM tables of this build.
    """
    import time

    from specfirst.machine import ard, ars, registry, results

    spec = pilot.kit.results[0]
    built = {plan.name: plan.table for plan in pilot.built()}
    started = time.perf_counter()
    event = ars.index(ars.read(pilot.dest / spec.ars))
    known = registry.load(pilot.root)
    binding = ars.bind(event, known, spec.binding)
    tables = {
        dataset: ard.table_from_arrow(dataset, built[dataset].select(names))
        for dataset, names in ars.columns(event, spec.subject_key).items()
    }
    rows = ard.run(event, known, binding, tables, spec.subject_key)
    seconds = time.perf_counter() - started
    comparison = results.compare_reference(event, results.by_id(rows))
    read = sum(len(names) for names in ars.columns(event, spec.subject_key).values())
    print(f"Python engine: {len(event.analyses)} analyses on {read} columns of "
          f"{', '.join(tables)}: {len(rows)} rows in {seconds:.2f} s (the spike: about 3 "
          "minutes; the target: under 10 seconds)")
    print(f"embedded results: {comparison.total}; reproduced as printed: "
          f"{comparison.reproduced}")
    problems = []
    if seconds >= 10:
        problems.append(f"the Python engine took {seconds:.1f} s; the target is under 10 s")
    if (comparison.total, comparison.reproduced) != (3735, 3711):
        problems.append(f"{comparison.reproduced} of {comparison.total} reproduced; E2 says "
                        "3711 of 3735")
    per_analysis = Counter(row["analysis_id"] for row in rows)
    print(f"rows per analysis: {len(per_analysis)} analyses, {sum(per_analysis.values())} rows; "
          f"expected {len(ROWS_PER_ANALYSIS)} analyses, {sum(ROWS_PER_ANALYSIS.values())} rows")
    for name in sorted(set(per_analysis) | set(ROWS_PER_ANALYSIS)):
        if per_analysis.get(name, 0) != ROWS_PER_ANALYSIS.get(name, 0):
            problems.append(f"{name}: {per_analysis.get(name, 0)} rows, expected "
                            f"{ROWS_PER_ANALYSIS.get(name, 0)}")
    return problems


CASES = {
    "A1-resolve": a1_resolve, "A2-runner": a2_runner, "A3-lineage": a3_lineage,
    "A4-unread": a4_unread, "A5-adapted": a5_adapted, "A6-engine": a6_engine,
}


@pytest.mark.parametrize("case", list(CASES), ids=list(CASES))
def test_pilot(case, pilot):
    try:
        assembled(pilot)
    except Missing as error:
        if os.environ.get("SPECFIRST_STRICT") == "1":
            pytest.fail(str(error))
        pytest.skip(str(error))
    print(f"\n--- {case}")
    problems = CASES[case](pilot)
    assert not problems, "\n".join(problems)
