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


def _drafted(root: Path, tmp_path: Path) -> Path:
    """A copy of standard/ in which catalog@2 and open-default@2 are drafts again."""
    copy = tmp_path / "drafted"
    shutil.copytree(root / "standard", copy / "standard")
    path = copy / "standard" / "versions.yaml"
    data = yaml.safe_load(path.read_text(encoding="ascii"))
    for kind, label in (("catalogs", "catalog@2"), ("houses", "open-default@2")):
        data[kind][label]["status"] = "draft"
        del data[kind][label]["tree"]
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="ascii", newline="\n")
    return copy


def test_the_frozen_folders_have_their_trees(root):
    known = versions.load(root)
    for label in ("catalog@1", "open-default@1", "catalog@2", "open-default@2"):
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


def test_version_2_changes_the_defaults_the_owner_took(root):
    """The defaults of open-default@2 are those of open-default@1 but for the eight
    of ADR-020, question 2 (#1, #2, #3, #6, #7, #8, #11, #13) and #22."""
    old = {(r["id"], r["unit"]): r["value"] for r in houses.defaults(*houses.load_pair(root))}
    new = {(r["id"], r["unit"]): r["value"] for r in houses.defaults(
        *houses.load_pair(root, "catalog@2", "open-default@2"))}
    changed = {key for key in set(old) | set(new) if old.get(key) != new.get(key)}
    assert {entry for entry, _ in changed} == {
        "tfl.percent.format", "pop.safety.rule", "ae.teae.end", "bds.baseline.rule",
        "demo.age.groups", "tfl.columns.total", "bds.window.tiebreak", "tfl.quantile.definition"}
    assert new[("ae.teae.end", "mod-ae-emergence")] == {"rule": "last_dose_plus_days", "days": 30}
    assert ("pop.safety.rule", "mod-populations") not in new  # by design: needs the features


def test_draft_versions_may_not_be_named(root, tmp_path):
    drafted = _drafted(root, tmp_path)
    with pytest.raises(versions.VersionError, match="a draft version"):
        versions.require_usable(drafted, ["catalog@2"], "a kit")
    versions.require_usable(drafted, ["catalog@1", "open-default@1"], "a kit")
    versions.require_usable(root, ["catalog@2", "open-default@2"], "a kit")
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


def test_the_pinned_trees_are_those_of_the_tag():
    """The trees of catalog@1 and open-default@1 at the tag catalog@1 (git rev-parse
    catalog@1:standard/catalog and catalog@1:standard/houses/open-default@1); those of
    catalog@2 and open-default@2 at the tag catalog@2 (catalog@2:standard/catalog@2 and
    catalog@2:standard/houses/open-default@2)."""
    assert versions.PINNED == {
        "catalog@1": "a25d42c08d37352131b9320a62c7fa2ce266cb9b",
        "open-default@1": "7ac0f4fc4d76333817b6e3edf21e156afec38ef4",
        "catalog@2": "1a3dcc6575849a57f47257b8daaf5eb30d995be9",
        "open-default@2": "550cb664b4d64a304f9d14bbd995379d16602601"}


def test_scores_are_comparable_only_over_kept_decisions(house2):
    _migration(house2, [
        {"alternative": "ae.teae.end/end_of_study", "change": "removed", "replacement": None,
         "backlog": "i03.end-of-study-removed"},
        {"alternative": "tfl.percent.format/one_decimal_always", "change": "renamed",
         "to": "tfl.percent.format/always", "backlog": "x"}])
    catalog = catalogs.load(catalogs.default_dir(house2, "catalog@2"))
    kept = [{"id": "ae.teae.end", "unit": "mod-ae-emergence", "value": {"rule": "no_end"}},
            {"id": "tfl.percent.format", "unit": "tfl-ae-summary",
             "value": {"rule": "one_decimal_always"}},
            {"id": "custom:eff-x", "unit": "tfl-ae-summary", "value": {"rule": "any"}}]
    assert migration.comparable(kept, catalog) == []
    gone = kept + [{"id": "ae.teae.end", "unit": "mod-ae-emergence",
                    "value": {"rule": "end_of_study"}}]
    assert migration.comparable(gone, catalog) == [
        "ae.teae.end (mod-ae-emergence): removed: ae.teae.end/end_of_study; a person decides"]


def test_a_task_and_a_kit_refuse_a_draft_version(root, tmp_path):
    from specfirst.gen import kits
    from specfirst.harness import task

    with pytest.raises(task.TaskError, match="a draft version"):
        task.kit_catalog(_drafted(root, tmp_path), {
            "catalog": {"name": "specfirst-m1", "version": 2}, "house": "open-default@2"})
    assert task.kit_catalog(root, {"catalog": {"name": "specfirst-m1", "version": 2},
                                   "house": "open-default@2"}) == "catalog@2"
    assert task.kit_catalog(root, {"catalog": {"name": "specfirst-m1", "version": 1},
                                   "house": "open-default@1"}) == "catalog@1"
    copy = tmp_path / "root"
    shutil.copytree(root / "standard", copy / "standard")
    path = copy / "standard" / "versions.yaml"
    data = yaml.safe_load(path.read_text(encoding="ascii"))
    data["catalogs"]["catalog@1"]["status"] = "draft"
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="ascii", newline="\n")
    with pytest.raises(kits.KitError, match="catalog@1', a draft version"):
        kits._generate(copy, "seed-x", tmp_path / "kit", "train", False, print, None, "full")


def test_house_write_refuses_a_frozen_house(root, capsys):
    from specfirst import cli

    before = (root / "standard" / "houses" / "open-default@1" / "STANDARD.md").read_bytes()
    assert cli.main(["house", "--write"]) == 1
    assert "open-default@1 is frozen" in capsys.readouterr().out
    after = (root / "standard" / "houses" / "open-default@1" / "STANDARD.md").read_bytes()
    assert after == before
    assert cli.main(["catalog", "--catalog", "catalog@2", "--house", "open-default@1"]) == 1
    assert "cannot load the catalog and the house" in capsys.readouterr().out


def test_the_backlog_covers_its_issues_and_prints(root):
    assert backlog.problems(root) == []
    lines = backlog.summary(root)
    assert lines[0] == f"==> {backlog.FILE} <=="
    assert any(line.startswith("house, waits:") for line in lines)
    assert not any(line.endswith(", accepted:") for line in lines)  # all done at the freeze
