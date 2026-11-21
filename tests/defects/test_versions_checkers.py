"""Planted defects for the checks of the versions of the standard (ADR-020; rule R5).

Each test copies the standard, shows that the copy is clean, plants one
defect and expects the check to name it: frozen, migration, backlog,
defaults and templates (the gates catalog-2a and catalog-2b).
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

from specfirst.compile import backlog, checks, migration, versions
from specfirst.compile import catalog as catalogs
from specfirst.compile import house as houses


@pytest.fixture(scope="module")
def clean(root, tmp_path_factory) -> Path:
    base = tmp_path_factory.mktemp("versions") / "root"
    shutil.copytree(root / "standard", base / "standard")
    return base


@pytest.fixture
def work(clean, tmp_path) -> Path:
    copy = tmp_path / "root"
    shutil.copytree(clean, copy)
    return copy


def change(path: Path, plant) -> None:
    data = yaml.safe_load(path.read_text(encoding="ascii"))
    plant(data)
    path.write_text(yaml.safe_dump(data, sort_keys=False, width=10_000), encoding="ascii",
                    newline="\n")


def all_problems(work: Path) -> dict[str, list[str]]:
    old = catalogs.load(catalogs.default_dir(work, "catalog@1"))
    catalog, house = houses.load_pair(work, "catalog@2", "open-default@2")
    return {
        "frozen": versions.frozen_problems(work),
        "migration": migration.problems(old, catalog, backlog.accepted_for(
            backlog.load(work), "catalog@2")),
        "backlog": backlog.problems(work),
        "defaults": checks.defaults_problems(catalog, house, work),
        "templates": checks.template_directive_problems(catalog, house),
    }


def test_the_clean_copy_passes(work):
    assert all_problems(work) == {name: [] for name in (
        "frozen", "migration", "backlog", "defaults", "templates")}


def _entry(work: Path, entry_id: str, label: str = "catalog@2") -> Path:
    return work / "standard" / label / "entries" / f"{entry_id}.yaml"


def _defaults(work: Path) -> Path:
    return work / "standard" / "houses" / "open-default@2" / "defaults.yaml"


def _one_byte(work: Path) -> None:
    path = _entry(work, "ae.teae.end", "catalog@1")
    data = bytearray(path.read_bytes())
    data[data.index(b"When")] = ord("w")
    path.write_bytes(bytes(data))


def _added_file(work: Path) -> None:
    (work / "standard" / "houses" / "open-default@1" / "NOTES.md").write_text(
        "a note\n", encoding="ascii")


def _folder_and_line(work: Path) -> None:
    """One byte of catalog@1 changed, and versions.yaml given the new tree (review F1)."""
    from specfirst.compile import versions

    _one_byte(work)
    tree = versions.tree_hash(work / "standard" / "catalog@1")
    change(work / "standard" / "versions.yaml",
           lambda data: data["catalogs"]["catalog@1"].__setitem__("tree", tree))


def _copied_folder(work: Path) -> None:
    """catalog@2 copied as catalog@3 and listed: its files still say version 2 (F2)."""
    shutil.copytree(work / "standard" / "catalog@2", work / "standard" / "catalog@3")
    change(work / "standard" / "versions.yaml", lambda data: data["catalogs"].__setitem__(
        "catalog@3", {"status": "draft", "date": "2026-11-21", "by": "a plant"}))


def _pinned_made_draft(work: Path) -> None:
    """catalog@1 called a draft and changed: the pin holds it, whatever the default (G1)."""
    _one_byte(work)
    change(work / "standard" / "versions.yaml",
           lambda data: data["catalogs"]["catalog@1"].__setitem__("status", "draft"))


def _fn_mapping(work: Path) -> None:
    def plant(data):
        data["alternatives"]["no_end"]["adam"]["ADAE"]["columns"][0]["derivation"] = {
            "$fn": {"name": "cut_labels"}, "args": []}
    change(work / "standard" / "catalog@2" / "templates" / "ae.teae.end.yaml", plant)


def _kit_names_draft(work: Path) -> None:
    change(work / "standard" / "versions.yaml",
           lambda data: data["catalogs"]["catalog@2"].__setitem__("status", "draft"))
    kit = work / "kits" / "k1"
    kit.mkdir(parents=True)
    (kit / "kit.yaml").write_text(
        "kit: 1\ncatalog: {name: specfirst-m1, version: 2}\nhouse: open-default@2\n",
        encoding="ascii")


def _definition(work: Path) -> None:
    def plant(data):
        data["alternatives"][0]["definition"] = "The arm as the sponsor last recorded it."
    change(_entry(work, "trt.planned.source"), plant)


def _line(entry: dict):
    return lambda work: change(work / "standard" / "catalog@2" / migration.FILE,
                               lambda data: data.__setitem__("changes", [entry]))


def _record(plant):
    return lambda work: change(work / backlog.FILE, lambda data: plant(data["records"]))


def _item(entry_id: str, value):
    return lambda work: change(_defaults(work),
                               lambda data: data["defaults"].__setitem__(entry_id, value))


def _template(work: Path) -> None:
    def plant(data):
        data["alternatives"]["no_end"]["adam"]["ADAE"]["columns"][0]["derivation"] = {
            "$if": {"get": "never", "eq": 1}, "then": {"$fn": "no_such_helper", "args": []}}
    change(work / "standard" / "catalog@2" / "templates" / "ae.teae.end.yaml", plant)


DEFECTS = [
    ("one byte changed in a file of catalog@1", _one_byte, "frozen",
     "catalog@1: the folder standard/catalog@1 has the tree"),
    ("a file added to open-default@1", _added_file, "frozen",
     "open-default@1: the folder standard/houses/open-default@1 has the tree"),
    ("a kit that names a draft version", _kit_names_draft, "frozen",
     "kits/k1/kit.yaml (catalog): names 'catalog@2', a draft version"),
    ("a frozen folder changed with its line of versions.yaml", _folder_and_line, "frozen",
     "catalog@1: standard/versions.yaml records the tree"),
    ("a folder whose files are another version", _copied_folder, "frozen",
     "catalog@3: its catalog.yaml says version 2, not catalog@3"),
    ("a house that versions.yaml pairs with another catalog",
     lambda w: change(w / "standard" / "versions.yaml", lambda data: data["houses"][
         "open-default@2"].__setitem__("catalog", "catalog@1")),
     "frozen", "open-default@2: its house.yaml needs catalog@2, standard/versions.yaml says "
     "catalog@1"),
    ("a pinned version made a draft and changed", _pinned_made_draft, "frozen",
     "catalog@1: the folder standard/catalog@1 has the tree"),
    ("a pinned version made a draft", lambda w: change(
        w / "standard" / "versions.yaml",
        lambda data: data["catalogs"]["catalog@1"].__setitem__("status", "draft")),
     "frozen", "catalog@1: pinned as frozen, and standard/versions.yaml calls it draft"),
    ("a folder that versions.yaml does not list",
     lambda w: shutil.copytree(w / "standard" / "catalog@2", w / "standard" / "catalog@3"),
     "frozen", "catalog@3: a folder that standard/versions.yaml does not list"),
    ("a definition changed without a line", _definition, "migration",
     "trt.planned.source/dm_arm: changed in meaning in catalog@2, and migration.yaml has "
     "no line for it"),
    ("a line for an alternative that did not change",
     _line({"alternative": "trt.planned.source/dm_arm", "change": "changed",
            "backlog": "i03.window-default"}),
     "migration", "change 1: trt.planned.source/dm_arm does not change in meaning"),
    ("a line with no accepted record",
     _line({"alternative": "trt.planned.source/dm_arm", "change": "changed",
            "backlog": "i99.nothing"}),
     "migration", "names the backlog record 'i99.nothing', which is not accepted"),
    ("a record with an unknown status",
     _record(lambda records: records[0].__setitem__("status", "maybe")), "backlog",
     "i01.zero-shown: the status 'maybe' is not one of"),
    ("an issue without a record",
     _record(lambda records: records[:] and [records.remove(r) for r in list(records)
                                             if r["issue"] == 33]),
     "backlog", "issue #33: no record in standard/BACKLOG.yaml"),
    ("a record accepted for a frozen version",
     _record(lambda records: records[0].__setitem__("status", "accepted")), "backlog",
     "i01.zero-shown: accepted for open-default@2, which is frozen"),
    ("an entry without an item", lambda w: change(
        _defaults(w), lambda data: data["defaults"].pop("ae.teae.end")),
     "defaults", "defaults.yaml: ae.teae.end: no item"),
    ("a default that is not an alternative", _item("ae.teae.end", {"rule": "sometimes"}),
     "defaults", "ae.teae.end: entry ae.teae.end has no alternative 'sometimes'"),
    ("a default for a unit the entry does not have",
     lambda w: change(_defaults(w), lambda data: data["defaults"]["tfl.percent.format"][
         "units"].__setitem__("tfl-vitals-by-visit", {"rule": "one_decimal_always"})),
     "defaults", "tfl.percent.format: the unit tfl-vitals-by-visit does not answer this entry"),
    ("an entry per table family without an item",
     lambda w: change(_defaults(w), lambda data: data["defaults"].pop("tfl.population")),
     "defaults", "tfl.population (tfl-demographics): no item"),
    ("a case that names an unknown feature", _item("ae.teae.end", {"cases": [
        {"when": "design.on_mars", "rule": "no_end"}, {"rule": "no_end"}]}),
     "defaults", "`when` names the unknown feature 'design.on_mars'"),
    ("a last case with `when`", _item("ae.teae.end", {"cases": [
        {"when": "design.randomized", "rule": "no_end"},
        {"when": "design.always", "rule": "no_end"}]}),
     "defaults", "every case but the last has `when`"),
    ("an unknown helper in a branch no example reaches", _template, "templates",
     "unknown helper 'no_such_helper'"),
    ("a mapping as the name of a helper", _fn_mapping, "templates",
     "unknown helper '{'name'"),
]


@pytest.mark.parametrize("plant, check, words", [pytest.param(*d[1:], id=d[0]) for d in DEFECTS])
def test_a_planted_defect_is_named(work, plant, check, words):
    plant(work)
    found = all_problems(work)
    assert any(words in problem for problem in found[check]), found[check]
