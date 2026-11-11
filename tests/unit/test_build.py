"""Runner, build and the three checks, end to end on the made-up study of tests/toy_kit.py."""

from __future__ import annotations

import os

import pytest
import toy_kit

from specfirst import kit as kits
from specfirst.machine import build, compare, runner
from specfirst.machine.canonical import read_jsonl

pytest.importorskip("yamaa")
pa = pytest.importorskip("pyarrow")


@pytest.fixture
def make(tmp_path, root, monkeypatch):
    monkeypatch.delenv("SPECFIRST_CACHE", raising=False)
    monkeypatch.delenv("SPECFIRST_ROOT", raising=False)

    def factory(**options):
        return toy_kit.make(tmp_path, root, **options)

    return factory


def run(function, *args, **kwargs):
    lines: list[str] = []
    result = function(*args, out=lines.append, **kwargs)
    return result, "\n".join(lines)


def test_runner_builds_the_datasets_in_run_order(make):
    toy = make()
    kit = kits.load_kit(toy, "toy")
    dest = kits.assembled_dir(toy, "toy")
    assert kits.assemble(toy, kit) == []
    plans = runner.run_project(dest, kit.project, kit.sdtm)
    assert [plan.name for plan in plans] == ["ADSL", "ADAE"]
    assert plans[0].entry == "gold/spec/adsl.yaml"
    assert plans[0].inputs == (
        runner.InputSource("DM", "sdtm", "DM", "inputs/data/sdtm/dm.parquet"),)
    # ADAE reads the ADSL of this run, not a file.
    assert plans[1].inputs == (
        runner.InputSource("ADSL", "adam", "ADSL", None),
        runner.InputSource("AE", "sdtm", "AE", "inputs/data/sdtm/ae.parquet"),
    )
    expected = toy_kit.tables()
    for plan in plans:
        reference = expected[f"data/adam/{plan.name.lower()}.parquet"]
        assert compare.compare_tables(plan.name, reference, plan.table).equal
    # Every path of the resolution is relative to the kit: no absolute path is written.
    assert str(dest) not in str(plans[0].record)
    assert plans[0].origins["/columns/1/derivation"]["declaring_source"] == "gold/spec/adsl.yaml"
    # Nothing was written next to the specifications or the inputs.
    assert not (dest / "gold/data").exists() and not (dest / "gold/spec/data").exists()


def test_relocating_a_resolution_asks_the_file_system_once_per_file(tmp_path, monkeypatch):
    # Lesson 10: a resolution names a few files in many thousands of origins, and on a
    # Windows drive under WSL each path resolution is a slow call.
    from pathlib import Path

    spec = str(tmp_path / "gold" / "spec" / "adsl.yaml")
    record = {
        "entry": spec, "project": None,
        "entries": [{
            "entry": spec, "layers": [spec], "resources": [],
            "origins": {f"/columns/{i}": {"declaring_source": spec, "line": i + 1,
                                          "source_kind": "authored"} for i in range(500)},
        }],
    }
    calls: list[Path] = []
    resolve = Path.resolve
    monkeypatch.setattr(Path, "resolve", lambda self, *a, **k: calls.append(self) or resolve(
        self, *a, **k))
    result = runner._relocate(record, tmp_path)
    assert result["entries"][0]["origins"]["/columns/499"]["declaring_source"] == (
        "gold/spec/adsl.yaml")
    assert len(calls) <= 3  # the kit folder and the one file, not once per origin
    assert record["entry"] == spec  # the engine's record is not changed


def test_resolve_reads_no_data(make):
    toy = make()
    kit = kits.load_kit(toy, "toy")
    dest = kits.assembled_dir(toy, "toy")
    assert kits.assemble(toy, kit) == []
    (dest / "inputs/data/sdtm/dm.parquet").write_bytes(b"not a parquet file")
    plans = runner.resolve_project(dest, kit.project, kit.sdtm)
    assert [plan.table for plan in plans] == [None, None]
    assert plans[0].columns == ["STUDYID", "USUBJID", "AGE", "AGEGR1", "SAFFL", "TRTSDT"]


def test_build_then_all_checks_pass(make):
    toy = make()
    code, text = run(build.build, toy, "toy")
    assert code == 0, text
    assert "built ADSL           3 rows x   6 columns from DM" in text
    folder = kits.assembled_dir(toy, "toy")
    manifest = build.read_manifest(folder)
    assert manifest["datasets"] == ["ADSL", "ADAE"]
    assert sorted(manifest["files"]) == [
        "gold/data/adam/adae.parquet", "gold/data/adam/adsl.parquet",
        "gold/graph/coverage.json", "gold/graph/edges.jsonl", "gold/graph/nodes.jsonl",
        "gold/resolved/adae.json", "gold/resolved/adsl.json",
    ]
    assert build.manifest_problems(folder) == []

    passed, text = run(build.reproduction, toy, "toy")
    assert passed, text
    assert "TOTAL cells=33 mismatched=0" in text
    assert "large_string -> string in 7 columns" in text
    assert "P2 reproduction: 2 of 2 datasets equal their reference" in text

    passed, text = run(build.trace, toy, "toy")
    assert passed, text
    assert "ADSL            6       5       0       1     0" in text
    assert "ADAE            5       5       0       0     0" in text
    assert ("claims ADSL        2 claims,   1 citations of kit documents ->   1 cites edges "
            "(one per column and span); 1 citations of programs or other files, not imported; "
            "1 variables that are not output columns") in text

    assert run(build.check, toy, "toy")[0] == 0


def test_graph_of_the_toy_study(make):
    toy = make()
    assert run(build.build, toy, "toy")[0] == 0
    folder = kits.assembled_dir(toy, "toy") / "gold/graph"
    edges = {(e["from"], e["to"]): e for e in read_jsonl(folder / "edges.jsonl")}
    nodes = {n["id"]: n for n in read_jsonl(folder / "nodes.jsonl")}
    lines = toy_kit.ADSL.splitlines()
    helper = [i for i, line in enumerate(lines, start=1) if line == "    derivation: DM.AGE"][1]
    # AGEGR1 reads DM.AGE through the helper column AGE_N: the edge names the helper's line.
    assert edges[("adam:ADSL.AGEGR1", "sdtm:DM.AGE")]["source"] == {
        "file": "gold/spec/adsl.yaml", "line": helper}
    assert ("adam:ADSL.AGE_N", "sdtm:DM.AGE") not in edges and "adam:ADSL.AGE_N" not in nodes
    # ADAE.AGE comes from ADSL.AGE, found by the key USUBJID.
    assert ("adam:ADAE.AGE", "adam:ADSL.AGE") in edges
    assert ("adam:ADAE.AGE", "adam:ADSL.USUBJID") in edges
    assert ("adam:ADAE.AGE", "sdtm:DM.AGE") not in edges
    assert nodes["sdtm:DM.AGE"]["source"] == {"file": "inputs/data/sdtm/define.xml", "line": 4}
    assert nodes["sdtm:DM.RFSTDTC"]["source"] == {"file": "inputs/data/sdtm/dm.parquet", "line": 1}
    cites = edges[("adam:ADSL.AGEGR1", "doc:sap#section%201")]
    assert (cites["type"], cites["proof"], cites["origin"]) == ("cites", "judged", "imported")
    assert not any(node.startswith("adam:ADSL.NOTBUILT") for node in nodes)


def test_two_builds_have_the_same_hashes(make):
    toy = make()
    passed, text = run(build.determinism, toy, "toy")
    assert passed, text
    assert "P1 determinism: 7 of 7 files have the same SHA-256 in both builds" in text
    first = build.read_manifest(toy / "build/p1/toy/first")
    assert first == build.read_manifest(toy / "build/p1/toy/second")
    # Each build assembled the kit in its own folder: the two share no path of the kit.
    for folder in ("first", "second"):
        assert (toy / "build/p1/toy" / folder / "inputs/data/sdtm/dm.parquet").is_file()
    assert not kits.assembled_dir(toy, "toy").exists()


def test_p1_fails_when_a_built_file_depends_on_its_folder(make, tmp_path, monkeypatch):
    """Review of real-1, finding F3: the paths of a resolution left absolute.

    The defect is planted in the build processes themselves, through a
    sitecustomize module that only they import.
    """
    toy = make()
    hook = tmp_path / "hook"
    hook.mkdir()
    (hook / "sitecustomize.py").write_text(
        "import specfirst.machine.runner as runner\n"
        "runner._relocate = lambda record, kit_dir: record\n",
        encoding="ascii",
    )
    paths = [str(hook), *filter(None, [os.environ.get("PYTHONPATH")])]
    monkeypatch.setenv("PYTHONPATH", os.pathsep.join(paths))
    passed, text = run(build.determinism, toy, "toy")
    assert not passed, text
    assert "P1: gold/resolved/adsl.json: the two builds differ" in text
    assert "P1: gold/graph/nodes.jsonl: the two builds differ" in text
    assert "same      " in text  # the datasets themselves do not depend on the folder


def test_compare_builds_sees_planted_differences():
    first = {"kit": "toy", "kit_manifest_sha256": "1", "engines": {"yamaa": "1"},
             "datasets": ["ADSL"], "files": {"a.parquet": "aa", "b.json": "bb"}}
    lines, problems = build.compare_builds(first, first)
    assert problems == [] and len(lines) == 2
    assert all(line.startswith("same") for line in lines)
    changed = {**first, "files": {"a.parquet": "aa", "b.json": "cc"}}
    assert build.compare_builds(first, changed)[1] == ["b.json: the two builds differ"]
    fewer = {**first, "files": {"a.parquet": "aa"}}
    assert build.compare_builds(first, fewer)[1] == ["b.json: the two builds differ"]
    assert build.compare_builds(fewer, first)[1] == ["b.json: the two builds differ"]
    other = {**first, "engines": {"yamaa": "2"}}
    assert "engines" in build.compare_builds(first, other)[1][0]
    assert "lists no file" in build.compare_builds({**first, "files": {}}, {**first, "files": {}}
                                                   )[1][0]


def test_a_reference_with_another_value_fails_p2(make):
    toy = make(reference_age=71.0)
    assert run(build.build, toy, "toy")[0] == 0
    passed, text = run(build.reproduction, toy, "toy")
    assert not passed
    assert "mismatched=     1" in text and "AGE:1" in text
    assert "P2: ADSL: differs from the reference" in text
    assert "P2 reproduction: 1 of 2 datasets equal their reference" in text
    assert run(build.check, toy, "toy")[0] == 1


def test_a_build_changed_after_it_was_built_is_refused(make):
    toy = make()
    assert run(build.build, toy, "toy")[0] == 0
    edges = kits.assembled_dir(toy, "toy") / "gold/graph/edges.jsonl"
    edges.write_bytes(edges.read_bytes().replace(b'"to":"sdtm:DM.AGE"', b'"to":"sdtm:DM.ARM"'))
    for check in (build.trace, build.reproduction):
        passed, text = run(check, toy, "toy")
        assert not passed and "gold/graph/edges.jsonl: changed since the build" in text


def test_a_dataset_without_a_reference_fails_p2(make):
    layout = {k: v for k, v in toy_kit.LAYOUT.items() if k != "gold/reference/adam/adae.parquet"}
    toy = make(layout=layout)
    assert run(build.build, toy, "toy")[0] == 0
    passed, text = run(build.reproduction, toy, "toy")
    assert not passed and "the kit has references for ['ADSL']" in text


def test_another_engine_version_than_the_pinned_one_is_refused(make):
    toy = make(engine_version="0.0.1")
    code, text = run(build.build, toy, "toy")
    assert code == 1 and "the kit pins yamaa 0.0.1" in text
    assert not (kits.assembled_dir(toy, "toy") / "gold/data").exists()


def test_a_specification_the_engine_refuses_fails_the_build(make):
    # AGEGR1 reads the helper AGE_N before it is declared.
    head, helper, rest = toy_kit.ADSL.partition(
        "  - name: AGE_N\n    type: float\n    label: Age, helper\n    derivation: DM.AGE\n")
    assert helper
    toy = make(adsl=head + rest + helper)
    code, text = run(build.build, toy, "toy")
    assert code == 1 and "ADSL" in text and "AGE_N" in text


def test_an_input_that_is_not_in_the_kit_fails_the_build(make):
    layout = {k: v for k, v in toy_kit.LAYOUT.items() if k != "inputs/data/sdtm/ae.parquet"}
    toy = make(layout=layout)
    code, text = run(build.build, toy, "toy")
    assert code == 1
    assert "ADAE: input AE" in text and "nor a file in inputs/data/sdtm" in text


def test_a_changed_cache_fails_the_build_before_anything_runs(make):
    toy = make()
    (toy / "third_party/cache/toy/data/sdtm/dm.parquet").write_bytes(b"other data")
    code, text = run(build.build, toy, "toy")
    assert code == 1 and "does not have the pinned SHA-256" in text
