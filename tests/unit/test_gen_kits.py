"""A kit of a generated study, written and checked again (specfirst.gen.kits, verify, gate2).

One kit is written once for the module, without the R engine (the gate runs
both engines; a test that needs R is skipped where R is not installed). The
checks that decide the gate gen-2a are then tested on it with planted
defects (rule R5).
"""

from __future__ import annotations

import json
import shutil

import pytest
import yaml

from specfirst import cli, gates
from specfirst.compile import catalog as catalogs
from specfirst.compile import house as houses
from specfirst.gen import decisions, documents, gate2, gold, kits, natural, study, verify
from specfirst.gen import design as designs
from specfirst.machine.canonical import read_jsonl, write_json

SEED = "unit-kits"
NUMBER = gate2.PLANTED     # the scenario of the house standard for the columns of the table


@pytest.fixture(scope="module")
def catalog(root):
    return catalogs.load(catalogs.default_dir(root))


def fill_store(root, folder, store_dir):
    """A store of model text for the statements of a kit, written by the test in the
    place of the rewriter and the verifier: the phrasing template of each statement, read
    back as its alternative, and one neutral paragraph per filler heading."""
    catalog = catalogs.load(catalogs.default_dir(root))
    store = natural.Store.load(store_dir)
    for key, item in natural.statements_of([kits.read_decisions(folder)]).items():
        text = natural.phrasing(catalog, item["entry"], item["unit"], item["value"])
        store.paragraphs[key] = {
            "key": key, "entry": item["entry"], "unit": item["unit"], "value": item["value"],
            "statement": item["statement"], "accepted": 1,
            "attempts": [{"n": 1, "by": "unit-test", "text": text, "slots": [],
                          "readback": {"pick": item["value"]["rule"], "agrees": True,
                                       "by": "unit-test"}}]}
    for item in documents.filler_wanted():
        store.filler[item["key"]] = {
            **item, "text": f"This section is about {item['heading'].lower()}.",
            "by": "unit-test", "problems": [], "readback": {"states": [], "by": "unit-test"}}
    store.save()


@pytest.fixture(scope="module")
def kit(root, tmp_path_factory):
    """The kit of the module, written twice: once to learn its statements, once with a
    store that holds them (the statements of this seed are not in the store of the
    repository)."""
    base = tmp_path_factory.mktemp("kits")
    store_dir = base / "store"
    store_dir.mkdir(parents=True)
    with pytest.MonkeyPatch.context() as patch:
        patch.setenv("SPECFIRST_REWRITES", str(store_dir))
        first = base / "first"
        kits.generate(root, kits.kit_seed(SEED, NUMBER), first, kits.split_of(NUMBER),
                      with_r=False, number=NUMBER)
        fill_store(root, first, store_dir)
        out = base / "kit"
        said: list[str] = []
        manifest = kits.generate(root, kits.kit_seed(SEED, NUMBER), out, kits.split_of(NUMBER),
                                 with_r=False, say=said.append, number=NUMBER)
        yield out, manifest, said


def test_the_gate_has_the_checks_of_the_plan():
    """PLAN.md section 13.5: 10 kits pass P1 to P4; every applicable decision is separated
    on the twin; the engines agree. Drift first."""
    names = [check.name for check in gates.GATES["gen-2a"]]
    assert names[0] == "environment"
    for needed in ("unit tests", "registry", "method vectors", "pilot tests", "kits",
                   "separation", "engines", "splits", "ASCII"):
        assert needed in names
    # The kits are written by the check "kits" and removed by the check "splits".
    assert names.index("kits") < names.index("separation") < names.index("engines") \
        < names.index("splits")
    assert gate2.COUNT == 10 and gate2.MAX_WORKERS <= 4


def test_a_kit_holds_what_the_manifest_says(root, kit):
    out, manifest, _ = kit
    assert manifest == kits.read_manifest(out)
    assert manifest["kit"] == kits.FORMAT and manifest["tier"] == "A"
    assert manifest["split"] == kits.split_of(NUMBER) and manifest["slice"] == "ae-summary-first"
    assert manifest["id"] == manifest["study"]["id"].lower()
    assert manifest["decisions"]["scenario"] == NUMBER
    assert manifest["decisions"]["given"] == {
        "tfl.population": "safety", "pop.safety.grouping": "actual",
        "trt.actual.source": "dm_actarm"}
    assert manifest["files"] == kits.all_files(out)
    names = set(manifest["files"])
    for needed in ("study.json", "gold/design.yaml", "gold/probes.jsonl", "gold/decisions.jsonl",
                   "gold/docs/sap.md", "gold/spec/compile.json", "gold/spec/adam/adsl.yaml",
                   "gold/spec/adam/adae.yaml", "gold/spec/adam/project.yaml",
                   "gold/spec/ars/reporting-event.json", "gold/spec/layout/tfl-ae-summary.json",
                   "gold/resolved/adsl.json", "gold/data/adam/adsl.parquet",
                   "gold/data/adam/adae.parquet", "gold/ars/reporting-event.json",
                   "gold/ard/reporting-event.jsonl", "gold/grid/Out_AESUM.json",
                   "gold/grid/Out_AESUM.shell.json", "gold/out/Out_AESUM.html",
                   "gold/graph/nodes.jsonl", "gold/graph/edges.jsonl", "gold/graph/coverage.json",
                   "gold/reference/tfl-ae-summary.json", "gold/identifiability.json",
                   "inputs/data/sdtm/dm.parquet", "inputs/data/sdtm/define.xml",
                   "inputs/house/house.yaml", "inputs/house/STANDARD.md",
                   "inputs/house/adam/adsl.yaml", "twin/data/sdtm/ae.parquet",
                   "twin/gold/data/adam/adae.parquet", "twin/gold/grid/Out_AESUM.json",
                   "twin/gold/graph/edges.jsonl", "twin/gold/reference/tfl-ae-summary.json"):
        assert needed in names, needed
    # A kit of the slice builds the two datasets its output reads, and no working folder
    # is left behind.
    assert not [name for name in names if name.startswith("work/") or (
        "advs" in name and not name.startswith("inputs/house/"))]
    assert manifest["datasets"] == ["ADSL", "ADAE"]
    # Nothing in the kit names the folder it was built in, the seed, or a clock.
    everything = b"".join((out / name).read_bytes() for name in names) + (
        out / kits.MANIFEST).read_bytes()
    assert kits.kit_seed(SEED, NUMBER).encode() not in everything
    assert str(out).encode() not in everything and str(root).encode() not in everything
    # The compiled specs name the house standard of the kit, not that of the checkout.
    spec = yaml.safe_load((out / "gold/spec/adam/adsl.yaml").read_text(encoding="ascii"))
    assert spec["parent"] == "../../../inputs/house/adam/adsl.yaml"
    for name in ("house.yaml", "STANDARD.md", "adam/adae.yaml", "ars/ae-summary.yaml"):
        assert (out / gold.HOUSE / name).read_bytes() == (
            houses.default_dir(root) / name).read_bytes()


def test_the_properties_of_the_kit(root, kit, catalog):
    out, manifest, _ = kit
    summary = manifest["properties"]["identifiability"]
    for which in ("visible", "twin"):
        found = manifest["properties"][which]
        assert found["cells"] == found["cells_equal_to_the_reference"] >= 8
        assert found["engines_agree"] is None        # this kit was written without R
    assert summary["applicable_and_unseparated"] == []
    assert "date.studyday.origin" in summary["unseparated_not_read"]
    # The scenario is the one the calibrated counts of the probes are made for.
    assert {"tfl.rounding.rule", "tfl.percent.format", "pop.safety.rule", "trt.actual.source",
            "ae.teae.start", "ae.teae.end"} <= set(summary["separated"])
    assert summary["pairs_claimed"] <= summary["pairs_separated"] <= summary["pairs"]
    records = kits.read_decisions(out)
    states = {r["id"]: r.get("identifiable") for r in records}
    assert states["date.studyday.origin"] == "unseparated"
    assert states["ae.teae.end"] == "separated" and states["demo.age.groups"] is None
    binds = {r["id"]: r["binds"] for r in records if r["unit"] != "tfl-demographics"}
    assert "adam:ADAE._TEEND" in binds["ae.teae.end"]
    assert not [b for found in binds.values() for b in found if b.startswith("layout:")]
    with open(out / kits.IDENTIFIABILITY, encoding="ascii") as handle:
        matrix = json.load(handle)
    item = next(i for i in matrix["decisions"] if i["id"] == "date.studyday.origin")
    assert (item["read"], item["applicable"], item["identifiable"]) == (
        False, False, "unseparated") and item["reason"] == verify.NOT_READ
    item = next(i for i in matrix["decisions"] if i["id"] == "ae.teae.end")
    assert item["read"] and item["applicable"] and len(item["pairs"]) == 3
    assert all(pair["separated"] for pair in item["pairs"])
    # The check of a written kit decides everything again from the files, the mutation
    # included, and finds nothing. This kit has no results of the R engine, which the
    # check reports unless it is told not to ask for them.
    said: list[str] = []
    assert kits.check(root, out, said.append, engines=False) == []
    assert any(" decisions recovered by the parser with the house standard and the oracle"
               in line and "natural paragraphs pass the slot and read-back checks" in line
               for line in said)
    assert any("P4 " in line and "0 applicable and unseparated" in line for line in said)
    assert kits.check(root, out, mutation=False) == [
        "visible: the kit has no results of the R engine",
        "twin: the kit has no results of the R engine"]


def test_two_builds_of_a_kit_are_the_same_bytes(root, kit, tmp_path):
    out, manifest, _ = kit
    again = kits.generate(root, kits.kit_seed(SEED, NUMBER), tmp_path / "again",
                          kits.split_of(NUMBER), with_r=False, number=NUMBER)
    assert kits.hash_differences(kits.kit_hashes(out), kits.kit_hashes(tmp_path / "again")) == []
    assert again == manifest
    other = kits.generate(root, kits.kit_seed(SEED, NUMBER + 10), tmp_path / "other",
                          kits.split_of(NUMBER), with_r=False, number=NUMBER)
    assert other["id"] != manifest["id"] and other["decisions"]["given"] == manifest[
        "decisions"]["given"]
    with pytest.raises(kits.KitError, match="is not empty"):
        kits.generate(root, "x", tmp_path / "other", with_r=False)
    with pytest.raises(kits.KitError, match="a split is one of"):
        kits.generate(root, "x", tmp_path / "new", split="exam", with_r=False)
    assert kits.hash_differences({"a": "1", "b": "2"}, {"a": "1", "b": "3", "c": "4"}) == [
        "c: only in one build", "b: the hashes differ"]


def test_planted_defects_of_the_gate_are_seen(root, kit, catalog):
    out, _, _ = kit
    said: list[str] = []
    assert gate2.planted_p2(said.append, out) is True
    assert gate2.planted_p3(root, said.append, out, catalog) is True
    assert gate2.planted_separation(root, said.append, out) is True
    planted = [line for line in said if line.startswith("planted defect:")]
    assert len(planted) >= 9, said
    assert any("date.studyday.origin" in line for line in planted)
    assert any("ae.teae.start is unseparated" in line for line in planted)


def test_planted_defects_of_the_splits_and_of_the_matrix_are_seen(root, kit):
    """Review finding G4: a kit that holds its seed, has another split than its place
    gives or names another seed; and a matrix that calls an unseparated decision
    separated, with the hashes written again."""
    out, _, _ = kit
    assert gate2.split_problems(out, NUMBER, SEED) == []
    # The same kit at another place of the set: another seed, and here another split.
    found = gate2.split_problems(out, NUMBER + 1, SEED)
    assert any("seed_sha256" in problem for problem in found)
    assert any("the plan gives" in problem for problem in found)
    said: list[str] = []
    assert gate2.planted_splits(said.append, out, SEED, NUMBER) is True
    assert gate2.planted_matrix(root, said.append, out, engines=False) is True
    planted = [line for line in said if line.startswith("planted defect:")]
    assert len(planted) == 4, said
    assert "inputs/docs/sap.md holds the seed" in planted[0]
    assert "date.studyday.origin" in planted[3] and "a new mutation 3" in planted[3]
    # A kit that is not sound itself is no ground for a planted defect.
    assert gate2.planted_splits(said.append, out, SEED, NUMBER + 1) is False


def test_a_kit_that_cannot_be_written_leaves_nothing(root, tmp_path, monkeypatch):
    """Review finding G7: a kit that fails a property is not written, folder included."""
    monkeypatch.setattr(kits, "_attempt",
                        lambda *args, **options: ({}, ["twin: P2: a planted difference"], []))
    with pytest.raises(kits.KitError, match="1 defects: twin: P2: a planted difference"):
        kits.generate(root, kits.kit_seed(SEED, NUMBER), tmp_path / "failed", with_r=False,
                      number=NUMBER)
    assert not (tmp_path / "failed").exists()


def test_a_changed_kit_fails_its_check(root, kit, tmp_path):
    out, _, _ = kit
    copy_of = tmp_path / "kit"
    shutil.copytree(out, copy_of)

    def problems():
        return kits.check(root, copy_of, mutation=False, engines=False)

    def refresh():
        """Write the hashes again, as someone would who changes a kit on purpose."""
        manifest = kits.read_manifest(copy_of)
        manifest["files"] = kits.all_files(copy_of)
        (copy_of / kits.MANIFEST).write_text(yaml.safe_dump(manifest, sort_keys=False),
                                             encoding="ascii", newline="\n")

    assert problems() == []
    # A file that changed after the manifest was written.
    path = copy_of / "gold" / "grid" / "Out_AESUM.json"
    made = json.loads(path.read_text(encoding="ascii"))
    made["rows"][1]["cells"][0]["text"] = "99 ( 99.9)"
    write_json(path, made)
    assert problems() == ["file gold/grid/Out_AESUM.json: the hashes differ"]
    # With the hashes written again, the content is judged: the grid is not the reference.
    refresh()
    found = problems()
    assert len(found) == 1 and found[0].startswith("visible: P2: row '")
    # A decision changed in the records only: the document no longer states it, and the
    # grids are not the hand calculation of that vector.
    shutil.rmtree(copy_of)
    shutil.copytree(out, copy_of)
    records = read_jsonl(copy_of / gold.DECISIONS)
    for record in records:
        if record["id"] == "tfl.columns.total":
            other = "none" if record["value"]["rule"] != "none" else "all_arms"
            record["value"] = {"rule": other}
    gold.write_decisions(copy_of, records)
    refresh()
    found = problems()
    assert any(p.startswith("documents, parser: ") and "tfl.columns.total" in p for p in found)
    assert any(p.startswith("twin: P2: columns") for p in found)
    # A kit of another generator or catalog version is not judged at all.
    shutil.rmtree(copy_of)
    shutil.copytree(out, copy_of)
    manifest = kits.read_manifest(copy_of)
    manifest["generator"] = "gen-0"
    (copy_of / kits.MANIFEST).write_text(yaml.safe_dump(manifest, sort_keys=False),
                                         encoding="ascii", newline="\n")
    assert problems()[0].startswith("kit.yaml: 'generator' is 'gen-0'")


def test_the_command_line_writes_and_verifies_a_kit(root, kit, tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("SPECFIRST_ROOT", str(root))
    out, manifest, _ = kit
    # The kit of this module has no results of the R engine: the command says so.
    assert cli.main(["gen", "verify", str(out), "--no-mutation"]) == 1
    printed = capsys.readouterr().out
    assert "the kit has no results of the R engine" in printed and "kit: FAILED" in printed
    assert f"kit {manifest['id']} ({manifest['split']})" in printed
    assert "P2 " in printed and "equal the hand calculation" in printed
    assert cli.main(["gen", "verify", str(tmp_path)]) == 1
    assert "no usable kit.yaml" in capsys.readouterr().out
    assert cli.main(["gen", "kit", "--out", str(tmp_path / "k")]) == 2     # no seed
    design = designs.load(out / "gold" / "design.yaml")
    values = decisions.as_values(kits.read_decisions(out))
    assert not kits.held_out(design, values)
    assert study.read_manifest(out)["study"] == manifest["study"]["id"]
