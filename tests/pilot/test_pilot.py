"""The evidence behind ADR-001, on the fetch cache and the assembled pilot kit.

    A1-resolve  the yamaa wheel composes each pilot specification to exactly
                the snapshot Pilot 7 committed, which its own runner made with
                yamaa built from the pinned git revision (E19)
    A2-runner   our runner (kit layout, every input in memory) builds the same
                tables as yamaa's own project run on Pilot 7's layout
    A3-lineage  specfirst.machine.lineage gives the same column dependencies as
                Pilot 7's own code, run from the cache at the pinned commit

These tests need `specfirst fetch` and carry the marker `evidence`, like the
spikes: `make test` leaves them out and `specfirst gate real-1` runs them. A
missing cache skips them, except under SPECFIRST_STRICT=1 (set by the gate),
where it fails: a gate never passes by skipping.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

from specfirst import kit as kits
from specfirst.machine import runner
from specfirst.machine.canonical import json_text
from specfirst.machine.lineage import column_dependencies
from specfirst.paths import cache_dir, repo_root

pytestmark = pytest.mark.evidence

KIT = "cdiscpilot01"
PROJECT = "cdiscpilot01/spec/yamaa/project.yaml"


class Missing(RuntimeError):
    """The fetch cache or the engine is not there."""


@dataclass
class Pilot:
    root: Path
    p7: Path  # Pilot 7 in the fetch cache
    kit: kits.Kit
    dest: Path  # the assembled kit


@pytest.fixture(scope="session")
def pilot(tmp_path_factory) -> Pilot:
    root = repo_root()
    p7 = cache_dir(root) / "p7"
    kit = kits.load_kit(root, KIT)
    return Pilot(root, p7, kit, tmp_path_factory.mktemp("pilot") / KIT)


def assembled(pilot: Pilot) -> None:
    if not (pilot.p7 / ".git").exists():
        raise Missing("not in the fetch cache: p7; run `specfirst fetch`")
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
    problems, revisions = [], set()
    for name in project.names:
        record = runner._relocate(project.spec(name).resolve(), pilot.p7)
        snapshot_file = project_file.parent / "resolved" / Path(record["entry"]).name
        with open(snapshot_file.with_suffix(".inspection.json"), encoding="ascii") as handle:
            snapshot = json.load(handle)
        revisions.add((snapshot["yamaa_version"], snapshot["yamaa_revision"]))
        same = json_text(record) == json_text(snapshot["resolved"])
        print(f"{name:9s} composed specification equals Pilot 7's snapshot: {same}")
        if not same:
            problems.append(f"{name}: the wheel resolves the specification differently")
    for version, revision in sorted(revisions):
        print(f"snapshots were made with yamaa {version} built from git revision {revision}")
        if version != yamaa.__version__:
            problems.append(f"snapshot is of yamaa {version}, installed is {yamaa.__version__}")
    print(f"installed: yamaa {yamaa.__version__} (wheel)")
    return problems


def a2_runner(pilot: Pilot) -> list[str]:
    import yamaa

    plans = runner.run_project(pilot.dest, pilot.kit.project, pilot.kit.sdtm)
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


CASES = {"A1-resolve": a1_resolve, "A2-runner": a2_runner, "A3-lineage": a3_lineage}


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
