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
from specfirst.gen import decisions, gate2, gold, kits, study, verify
from specfirst.gen import design as designs
from specfirst.machine.canonical import read_jsonl, write_json

SEED = "unit-kits"
NUMBER = gate2.PLANTED     # the scenario of the house standard for the columns of the table


@pytest.fixture(scope="module")
def catalog(root):
    return catalogs.load(catalogs.default_dir(root))


@pytest.fixture(scope="module")
def kit(root, tmp_path_factory):
    out = tmp_path_factory.mktemp("kits") / "kit"
    said: list[str] = []
    manifest = kits.generate(root, kits.kit_seed(SEED, NUMBER), out, kits.split_of(NUMBER),
                             with_r=False, say=said.append, number=NUMBER)
    return out, manifest, said


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
    assert any("stated in gold/docs/sap.md and read back by the parser" in line for line in said)
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
    assert any(p.startswith("decision tfl.columns.total") or "does not read back" in p
               for p in found)
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
