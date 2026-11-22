"""catalog@2 and open-default@2: anchors by entry, fixed rules, defaults by design,
attributes (ADR-020, part catalog-2b)."""

from __future__ import annotations

import pytest

from specfirst.compile import attributes, migration
from specfirst.compile import catalog as catalogs
from specfirst.compile import house as houses
from specfirst.compile.standard_form import StandardForm, StandardFormError


@pytest.fixture(scope="module")
def pair(root):
    return houses.load_pair(root, "catalog@2", "open-default@2")


def test_the_house_document_anchors_by_entry_and_parses_back(pair):
    catalog, house = pair
    text = houses.standards_document(catalog, house)
    form = StandardForm(catalog)
    doc, records, cases, fixed = form.parse_full(text)
    assert doc == houses.DOCUMENT_ID
    anchors = {r["anchor"] for r in records}
    assert "trt.start.source" in anchors
    assert "tfl.population/tfl-demographics" in anchors
    assert all("/s" not in anchor for anchor in anchors)
    assert [line["value"]["rule"] for line in cases[("pop.safety.rule", "mod-populations")]] == [
        "randomized_and_dosed", "at_least_one_dose"]
    rules = {f"{e.id}/{r['id']}" for e in catalog.entries.values() for r in e.fixed_rules}
    assert set(fixed) == rules and "ae.teae.start/no_start_date" in rules
    assert "[ae.teae.start/no_start_date] An adverse event without an analysis start date" in text
    assert "Status: frozen on 2026-11-21." in text
    assert "Order of precedence:" in text and "## Change log" in text


def test_a_default_by_design_cites_its_case(pair):
    catalog, house = pair
    for randomized, anchor, rule in ((True, "pop.safety.rule/1", "randomized_and_dosed"),
                                     (False, "pop.safety.rule/2", "at_least_one_dose")):
        features = {name: True for name in catalog.design_features}
        features["design.randomized"] = randomized
        records = {r["id"]: r for r in houses.default_decisions(catalog, house, features)}
        assert records["pop.safety.rule"]["value"] == {"rule": rule}
        assert records["pop.safety.rule"]["citations"][0]["anchor"] == anchor
    assert "pop.safety.rule" not in {r["id"] for r in houses.default_decisions(catalog, house)}


def _document(pair):
    catalog, house = pair
    return StandardForm(catalog), houses.standards_document(catalog, house)


@pytest.mark.parametrize("change, words", [
    (lambda t: t.replace("[ae.teae.start/no_start_date] An adverse event without",
                         "[ae.teae.start/no_start_date] Any adverse event without"),
     "not stated as the catalog states it"),
    (lambda t: t.replace("[pop.safety.rule/1]", "[pop.safety.rule/3]"), "out of order"),
    (lambda t: t.replace("[trt.start.source]", "[trt.end.source]"), "does not name"),
    (lambda t: t.replace("[trt.start.source] The", "[trt.start.source]  The"),
     "line"),
])
def test_a_document_anchored_by_entry_refuses_a_planted_defect(pair, change, words):
    form, text = _document(pair)
    planted = change(text)
    assert planted != text
    with pytest.raises(StandardFormError, match=words):
        form.parse_full(planted)


@pytest.mark.parametrize("change, words", [
    (lambda t: t.replace("[trt.start.source] The", "[1/s1] The"), "the document's anchors are by"),
    (lambda t: t.replace("[ae.teae.start/no_start_date] An adverse event without an analysis "
                         "start date is treatment-emergent.",
                         "An adverse event without an analysis start date is treatment-emergent."),
     "without its anchor"),
])
def test_a_document_refuses_mixed_anchors_and_a_rule_without_its_anchor(pair, change, words):
    form, text = _document(pair)
    planted = change(text)
    assert planted != text
    with pytest.raises(StandardFormError, match=words):
        form.parse_full(planted)


def test_a_fixed_rule_stands_in_the_section_of_its_entry(pair):
    form, text = _document(pair)
    line = ("[ae.teae.start/no_start_date] An adverse event without an analysis start date is "
            "treatment-emergent.")
    moved = text.replace(line + "\n", "").replace(
        "[trt.start.source] ", line + "\n\n[trt.start.source] ", 1)
    with pytest.raises(StandardFormError, match="stands in the section of mod-treatment"):
        form.parse_full(moved)


def test_parse_document_refuses_cases(pair):
    form, text = _document(pair)
    with pytest.raises(StandardFormError, match="read it with parse_full"):
        form.parse_document(text)


def test_a_positional_document_is_as_before(root):
    catalog, house = houses.load_pair(root, "catalog@1", "open-default@1")
    text = houses.standards_document(catalog, house)
    assert text == (house.directory / "STANDARD.md").read_text(encoding="ascii")
    assert "[1/s1]" in text and "Fixed rules" not in text


def test_the_migration_maps_a_removed_alternative_to_a_person(root):
    new = catalogs.load(catalogs.default_dir(root, "catalog@2"))
    record = {"id": "ae.teae.end", "unit": "mod-ae-emergence", "value": {"rule": "end_of_study"}}
    assert migration.migrate(record, new) == (
        None, "removed: ae.teae.end/end_of_study; a person decides")
    kept = {"id": "trt.planned.source", "unit": "mod-treatment", "value": {"rule": "dm_arm"}}
    assert migration.migrate(kept, new) == (kept, "kept")


# -- attributes (#33) -----------------------------------------------------------

# A test parent with a carried flag and a time part.
PARENT = {"columns": [
    {"name": "USUBJID", "type": "str", "label": "Unique Subject Identifier",
     "derivation": "AE.USUBJID"},
    {"name": "SAFFL", "type": "str", "label": "Safety Population Flag",
     "derivation": "ADSL.SAFFL"},
    {"name": "ASTTM", "type": "int", "label": "Analysis Start Time",
     "derivation": {"time_of_day": {"source": "ASTDTM"}}},
    {"name": "_WORK", "type": "str", "label": "Working value", "derivation": "'Y'"},
]}
ADSL = {"columns": [{"name": "SAFFL", "type": "str", "label": "Safety Population Flag",
                     "derivation": "'Y'"}]}


def test_the_parents_carry_the_labels_of_their_sources(pair):
    _, house = pair
    parents = {d: house.read(str(meta["parent"])) for d, meta in house.adam.items()}
    assert attributes.carried_label_problems(parents) == []
    assert attributes.carried_label_problems({"ADAE": PARENT, "ADSL": ADSL}) == []


def test_a_carried_label_that_differs_is_named():
    wrong = {"columns": [dict(PARENT["columns"][1], label="Safety Flag")]}
    found = attributes.carried_label_problems({"ADAE": wrong, "ADSL": ADSL})
    assert found == ["ADAE.SAFFL: carried from ADSL, labelled 'Safety Flag', not 'Safety "
                     "Population Flag' (the label of its source)"]


def test_a_label_only_difference_and_a_time_of_day_are_classified():
    built = attributes.of_spec(PARENT)
    assert set(built) == {"USUBJID", "SAFFL", "ASTTM"}
    reference = {**built,
                 "SAFFL": attributes.Attribute("SAFFL", "str", "Safety Population Flag (Y/N)"),
                 "ASTTM": attributes.Attribute("ASTTM", "time", "Analysis Start Time")}
    found = attributes.compare(built, reference, carried=frozenset({"SAFFL"}))
    assert [(d.name, d.category, d.explained) for d in found] == [
        ("ASTTM", "time", True), ("SAFFL", "label", True)]
    assert "set the label of SAFFL to 'Safety Population Flag (Y/N)'" in found[1].text
    assert attributes.unexplained(found) == []
    # Not carried, the same label difference is unexplained; a text time is a type difference.
    other = {**reference, "ASTTM": attributes.Attribute("ASTTM", "str", "Analysis Start Time")}
    found = attributes.compare(built, other)
    assert [(d.name, d.category) for d in attributes.unexplained(found)] == [
        ("ASTTM", "type"), ("SAFFL", "label")]
