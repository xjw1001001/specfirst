"""Planted defects for the checks catalog-2b adds (ADR-020; rule R5).

The house document of open-default@2 states every default by design and
every fixed rule; the catalog's terms name entries; fixed rule IDs are used
once; a parent carries the labels of its sources.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

from specfirst.compile import checks
from specfirst.compile import house as houses
from specfirst.compile.standard_form import StandardForm


@pytest.fixture(scope="module")
def clean(root, tmp_path_factory) -> Path:
    base = tmp_path_factory.mktemp("catalog2") / "root"
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


def problems(work: Path) -> dict[str, list[str]]:
    catalog, house = houses.load_pair(work, "catalog@2", "open-default@2")
    return {"catalog": checks.catalog_problems(catalog, work),
            "house": checks.house_problems(catalog, house, work)}


def test_the_clean_copy_passes(work):
    assert problems(work) == {"catalog": [], "house": []}


@pytest.mark.parametrize("cut, words", [
    (lambda t: t.replace("[ae.teae.start/no_start_date] An adverse event without an analysis "
                         "start date is treatment-emergent.\n", ""),
     "does not state the fixed rule ae.teae.start/no_start_date"),
    (lambda t: t.replace("[pop.safety.rule/2]", "[pop.safety.rule/9]"), "out of order"),
])
def test_a_document_that_drops_a_rule_or_a_case_is_named(work, cut, words):
    catalog, house = houses.load_pair(work, "catalog@2", "open-default@2")
    text = houses.standards_document(catalog, house)
    planted = cut(text)
    assert planted != text
    found = checks._document_cases_and_rules(catalog, house, StandardForm(catalog), planted)
    assert any(words in problem for problem in found), found


def test_a_case_stated_otherwise_is_named(work, monkeypatch):
    catalog, house = houses.load_pair(work, "catalog@2", "open-default@2")
    text = houses.standards_document(catalog, house)
    real = houses.choices

    def swapped(house_, entry_id, unit, per_family):
        found = real(house_, entry_id, unit, per_family)
        return found[::-1] if entry_id == "pop.safety.rule" else found

    monkeypatch.setattr(houses, "choices", swapped)
    found = checks._document_cases_and_rules(catalog, house, StandardForm(catalog), text)
    assert any("states the cases of pop.safety.rule" in problem for problem in found), found


def _catalog_yaml(work: Path) -> Path:
    return work / "standard" / "catalog@2" / "catalog.yaml"


def _entry(work: Path, entry_id: str) -> Path:
    return work / "standard" / "catalog@2" / "entries" / f"{entry_id}.yaml"


DEFECTS = [
    ("a term that names no entry",
     lambda w: change(_catalog_yaml(w), lambda d: d["terms"].__setitem__(
         "end of study", {"entry": "disp.nowhere", "text": "the end"})),
     "catalog", "term 'end of study': a term names an entry"),
    ("a fixed rule ID used twice",
     lambda w: change(_entry(w, "ae.teae.start"), lambda d: d["fixed_rules"].append(
         {"id": "no_start_date", "text": "Another rule."})),
     "catalog", "ae.teae.start: a fixed rule ID is used twice"),
    ("a carried variable labelled by the parent",
     lambda w: change(w / "standard" / "houses" / "open-default@2" / "adam" / "adae.yaml",
                      lambda d: next(c for c in d["columns"] if c["name"] == "AESOC")
                      .__setitem__("label", "Organ Class")),
     "house", "ADAE.AESOC: carried from AE, labelled 'Organ Class'"),
]


@pytest.mark.parametrize("plant, check, words", [pytest.param(*d[1:], id=d[0]) for d in DEFECTS])
def test_a_planted_defect_is_named(work, plant, check, words):
    plant(work)
    found = problems(work)
    assert any(words in problem for problem in found[check]), found[check]
