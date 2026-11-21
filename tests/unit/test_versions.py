"""The versions of the standard: labels, trees, pairs, defaults by design (ADR-020)."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

from specfirst.compile import backlog, migration, versions
from specfirst.compile import catalog as catalogs
from specfirst.compile import house as houses


def test_the_tree_hash_is_gits_on_a_small_folder(tmp_path, git):
    folder = tmp_path / "f"
    (folder / "a").mkdir(parents=True)
    (folder / "empty").mkdir()
    (folder / "a" / "x.yaml").write_bytes(b"k: 1\n")
    (folder / "a-b").write_bytes(b"hello\n")  # sorts before the folder a: '-' < '/'
    (folder / "b.md").write_bytes(b"")
    # git write-tree of the same files, computed once with git itself
    found = versions.tree_hash(folder)
    assert found == "0bd99570d7ebd979fdf5d3c124dbecb7c0b73944"
    git(folder, "init", "-q", ".")
    git(folder, "add", "-A")
    assert git(folder, "write-tree") == found


def test_the_frozen_folders_have_their_trees(root):
    known = versions.load(root)
    for label in ("catalog@1", "open-default@1"):
        assert known[label].status == "frozen"
        assert versions.tree_hash(versions.folder(root, label)) == known[label].tree
    assert versions.frozen_problems(root) == []


def test_labels_name_folders():
    assert versions.folder(Path("r"), "catalog@2") == Path("r/standard/catalog@2")
    assert versions.folder(Path("r"), "open-default@2") == Path("r/standard/houses/open-default@2")
    for bad in ("catalog", "catalog@0", "catalog@x", "Open@1"):
        with pytest.raises(versions.VersionError):
            versions.folder(Path("r"), bad)
    with pytest.raises(versions.VersionError):
        catalogs.default_dir(Path("r"), "open-default@1")


def test_the_default_pair_is_version_1(root):
    catalog, house = houses.load_pair(root)
    assert (catalog.label, house.label) == ("catalog@1", "open-default@1")
    assert catalog.directory.name == "catalog@1" and catalog.has_defaults


def test_a_house_alone_takes_the_catalog_it_needs(root):
    catalog, house = houses.load_pair(root, house_label="open-default@2")
    assert (catalog.label, house.label) == ("catalog@2", "open-default@2")
    assert not catalog.has_defaults and house.defaults_file is not None


@pytest.mark.parametrize("pair", [("catalog@1", "open-default@2"),
                                  ("catalog@2", "open-default@1")])
def test_a_house_that_does_not_fit_is_refused(root, pair):
    with pytest.raises(houses.HouseError, match="needs catalog@"):
        houses.load_pair(root, *pair)


def test_version_2_has_the_defaults_of_version_1(root):
    old = houses.load_pair(root)
    new = houses.load_pair(root, "catalog@2", "open-default@2")
    assert houses.defaults(*old) == houses.defaults(*new)
    assert houses.without_default(*old) == houses.without_default(*new)


def test_draft_versions_may_not_be_named(root):
    with pytest.raises(versions.VersionError, match="a draft version"):
        versions.require_usable(root, ["catalog@2"], "a kit")
    versions.require_usable(root, ["catalog@1", "open-default@1"], "a kit")
    assert versions.kit_labels({"catalog": {"name": "specfirst-m1", "version": "2"},
                                "house": "open-default@2"}) == [
        ("catalog", "catalog@2"), ("house", "open-default@2")]


@pytest.fixture
def house2(root, tmp_path) -> Path:
    copy = tmp_path / "standard"
    shutil.copytree(root / "standard" / "catalog@2", copy / "catalog@2")
    shutil.copytree(root / "standard" / "houses" / "open-default@2",
                    copy / "houses" / "open-default@2")
    return tmp_path


def _cases(work: Path, entry_id: str, cases: list[dict]) -> None:
    path = work / "standard" / "houses" / "open-default@2" / "defaults.yaml"
    data = yaml.safe_load(path.read_text(encoding="ascii"))
    data["defaults"][entry_id] = {"cases": cases}
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="ascii", newline="\n")


def test_a_default_by_design_needs_the_features(house2):
    _cases(house2, "pop.safety.rule", [
        {"when": "design.randomized", "rule": "randomized_and_dosed"},
        {"rule": "at_least_one_dose"}])
    catalog, house = houses.load_pair(house2, "catalog@2", "open-default@2")
    unit = catalog.entry("pop.safety.rule").units[0]
    assert houses.by_design(catalog, house, "pop.safety.rule", unit)
    assert houses.default_value(catalog, house, "pop.safety.rule", unit,
                                {"design.randomized": True}) == {"rule": "randomized_and_dosed"}
    assert houses.default_value(catalog, house, "pop.safety.rule", unit,
                                {"design.randomized": False}) == {"rule": "at_least_one_dose"}
    with pytest.raises(houses.HouseError, match="depends on the design"):
        houses.default_value(catalog, house, "pop.safety.rule", unit)
    assert "pop.safety.rule" not in {r["id"] for r in houses.defaults(catalog, house)}
    assert ("pop.safety.rule", unit) not in houses.without_default(catalog, house)


def _migration(work: Path, changes: list[dict]) -> None:
    path = work / "standard" / "catalog@2" / migration.FILE
    data = yaml.safe_load(path.read_text(encoding="ascii"))
    data["changes"] = changes
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="ascii", newline="\n")


def test_a_record_maps_through_the_migration_file(house2):
    _migration(house2, [
        {"alternative": "ae.teae.end/end_of_study", "change": "removed", "replacement": None,
         "backlog": "i03.end-of-study-removed"},
        {"alternative": "tfl.percent.format/one_decimal_always", "change": "renamed",
         "to": "tfl.percent.format/always", "backlog": "x"},
        {"alternative": "demo.bmi.rule/derived", "change": "changed", "backlog": "x"}])
    catalog = catalogs.load(catalogs.default_dir(house2, "catalog@2"))

    def record(entry_id, rule, unit="u"):
        return {"id": entry_id, "unit": unit, "value": {"rule": rule}, "status": "stated"}

    kept, how = migration.migrate(record("ae.teae.end", "no_end"), catalog)
    assert how == "kept" and kept["value"] == {"rule": "no_end"}
    renamed, how = migration.migrate(record("tfl.percent.format", "one_decimal_always"), catalog)
    assert renamed["value"] == {"rule": "always"} and how.startswith("renamed")
    for entry_id, rule in (("ae.teae.end", "end_of_study"), ("demo.bmi.rule", "derived")):
        gone, how = migration.migrate(record(entry_id, rule), catalog)
        assert gone is None and "a person decides" in how


def test_the_backlog_covers_its_issues_and_prints(root):
    assert backlog.problems(root) == []
    lines = backlog.summary(root)
    assert lines[0] == f"==> {backlog.FILE} <=="
    assert any(line.startswith("house, accepted:") for line in lines)
