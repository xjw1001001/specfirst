"""Slots, statements and standard-form documents (PLAN.md sections 4.4 and 6.6)."""

from __future__ import annotations

import pytest

from specfirst import schemas
from specfirst.compile import catalog as catalog_module
from specfirst.compile import checks
from specfirst.compile import house as house_module
from specfirst.compile.slots import (
    SlotError,
    check_value,
    parse_value,
    render_value,
    slot_from_spec,
)
from specfirst.compile.standard_form import StandardForm, StandardFormError, decision_record

# The std-1 tests hold the frozen pair of version 1 (ADR-020: loadable by label).
V1 = ("catalog@1", "open-default@1")


@pytest.fixture(scope="module")
def catalog(root):
    return catalog_module.load(catalog_module.default_dir(root, V1[0]))


@pytest.fixture(scope="module")
def form(catalog):
    return StandardForm(catalog)


def slot(kind: str, **more):
    return slot_from_spec("x", {"type": kind, "examples": [], **more})


@pytest.mark.parametrize("kind, value, text", [
    ("int", 30, "30"),
    ("int", -1, "-1"),
    ("number", 5, "5"),
    ("number", 2.5, "2.5"),
    ("text", "Week 24, day 1; (pre-dose).", '"Week 24, day 1; (pre-dose)."'),
    ("name", "DM.ARM", "DM.ARM"),
    ("list[int]", [18, 65], "18, 65"),
    ("list[text]", ["POSSIBLE", "PROBABLE"], '"POSSIBLE", "PROBABLE"'),
    ("list[name]", ["AGE", "SEX"], "AGE, SEX"),
])
def test_a_value_has_one_text_and_reads_back(kind, value, text):
    assert render_value(slot(kind), value) == text
    assert parse_value(slot(kind), text) == (value, len(text))


def test_records_read_back():
    windows = slot_from_spec("windows", {
        "type": "records",
        "fields": {"visit": "text", "low": "int", "high": "int"},
        "item": "{visit} from day {low} to day {high}",
        "examples": [],
    })
    value = [{"visit": "Week 2; early", "low": 8, "high": 21},
             {"visit": "W4", "low": 22, "high": 42}]
    text = render_value(windows, value)
    assert text == '"Week 2; early" from day 8 to day 21; "W4" from day 22 to day 42'
    assert parse_value(windows, text) == (value, len(text))


@pytest.mark.parametrize("kind, value", [
    ("int", True), ("int", 1.0), ("int", "1"),
    ("number", 5.0),            # a whole number is written as an integer
    ("number", float("nan")), ("number", 1e-9),
    ("text", 'say "x"'), ("text", " padded"), ("text", ""), ("text", "caf" + chr(233)),
    ("name", "dm.arm"), ("name", "A B"),
    ("list[int]", []), ("list[int]", [1, 1]), ("list[text]", "ab"),
])
def test_values_outside_the_canonical_form_are_refused(kind, value):
    with pytest.raises(SlotError):
        check_value(slot(kind), value)


@pytest.mark.parametrize("kind, text", [
    ("int", "030"), ("int", "+3"), ("int", "-0"), ("number", "2.50"), ("number", "1e3"),
    ("text", "Week 2"), ("text", '"open'), ("name", "arm"),
])
def test_texts_outside_the_canonical_form_are_refused(kind, text):
    try:
        value, end = parse_value(slot(kind), text)
    except SlotError:
        return
    assert end != len(text) or render_value(slot(kind), value) != text


def test_limits_and_choices_are_enforced():
    with pytest.raises(SlotError):
        check_value(slot("int", min=0), -1)
    with pytest.raises(SlotError):
        check_value(slot("list[name]", choices=["AGE", "SEX"]), ["AGE", "RACE"])


def test_every_alternative_round_trips_exactly(catalog):
    problems, tried = checks.roundtrip_problems(catalog)
    assert problems == []
    alternatives = sum(len(e.alternatives) * len(e.units) for e in catalog.entries.values())
    assert tried >= alternatives >= 100


def test_the_example_of_the_plan(form):
    value = {"rule": "last_dose_plus_days", "days": 30}
    statement = form.render("ae.teae.end", "mod-ae-emergence", value)
    assert statement == "Treatment emergence ends 30 days after the treatment end date."
    assert form.parse(statement) == ("ae.teae.end", "mod-ae-emergence", value)


def test_a_table_family_statement_names_its_output(form):
    value = {"rule": "active_arms", "control": "Placebo"}
    statement = form.render("tfl.columns.total", "tfl-ae-summary", value)
    assert statement == ('A total column of the adverse event summary table pools the '
                         'treatment arms other than "Placebo".')
    assert form.parse(statement) == ("tfl.columns.total", "tfl-ae-summary", value)
    other = form.render("tfl.columns.total", "tfl-vitals-by-visit", value)
    assert form.parse(other)[1] == "tfl-vitals-by-visit"


@pytest.mark.parametrize("statement", [
    "Treatment emergence ends 30 days after the treatment end date",       # no full stop
    "Treatment emergence ends 030 days after the treatment end date.",     # not canonical
    "Treatment emergence ends thirty days after the treatment end date.",  # not a number
    "treatment emergence ends 30 days after the treatment end date.",
    "Treatment emergence ends 30 days after the last dose.",               # another sentence
    "The analysis set of the listing of deaths is the safety set.",        # unknown output
])
def test_a_text_that_is_not_a_statement_is_refused(form, statement):
    with pytest.raises(StandardFormError):
        form.parse(statement)


@pytest.mark.parametrize("entry_id, unit, value", [
    ("ae.teae.end", "mod-ae-emergence", {"rule": "next_week"}),
    ("ae.teae.end", "mod-ae-emergence", {"rule": "last_dose_plus_days"}),          # slot missing
    ("ae.teae.end", "mod-ae-emergence", {"rule": "no_end", "days": 3}),            # slot too many
    ("ae.teae.end", "mod-ae-emergence", {"rule": "last_dose_plus_days", "days": -1}),
    ("ae.teae.end", "mod-treatment", {"rule": "no_end"}),                          # wrong unit
    ("ae.unknown", "mod-ae-emergence", {"rule": "no_end"}),
])
def test_a_value_that_fits_no_alternative_is_not_rendered(form, entry_id, unit, value):
    with pytest.raises(StandardFormError):
        form.render(entry_id, unit, value)


def test_document_round_trip_and_decision_records(root, catalog, form):
    house = house_module.load(house_module.default_dir(root, V1[1]))
    records = checks.base_vector(catalog, house)
    text = form.render_document("sap", "Statistical analysis plan", records)
    doc, parsed = form.parse_document(text)
    assert doc == "sap"
    assert [(r["id"], r["unit"], r["value"]) for r in parsed] == \
        [(r["id"], r["unit"], r["value"]) for r in form.order(records)]
    anchors = [r["anchor"] for r in parsed]
    assert len(set(anchors)) == len(anchors) and anchors[0] == "1/s1"
    for item in parsed:
        record = decision_record(item, doc, "stated", "document_rule")
        assert schemas.problems("decision-record", record, root=root) == []
        assert record["citations"] == [{"doc": "sap", "anchor": item["anchor"],
                                        "quote": item["statement"]}]
    assert form.render_document("sap", "Statistical analysis plan", records) == text


def test_document_defects_are_refused(catalog, form):
    records = [{"id": "ae.teae.end", "unit": "mod-ae-emergence", "value": {"rule": "no_end"}}]
    text = form.render_document("sap", "SAP", records)
    assert "[1/s1] Treatment emergence has no end date." in text
    with pytest.raises(StandardFormError, match="stated twice"):
        form.parse_document(text + "\n[1/s2] Treatment emergence ends at the end-of-study date.\n")
    with pytest.raises(StandardFormError, match="no template"):
        form.parse_document(text.replace("no end date", "no end"))
    with pytest.raises(StandardFormError, match="belongs to unit"):
        form.parse_document(text + "\n[1/s2] Study day 1 is the treatment start date.\n")
    with pytest.raises(StandardFormError, match="Document"):
        form.parse_document(text.replace("Document: sap", "Doc sap"))
    with pytest.raises(StandardFormError, match="two decisions"):
        form.render_document("sap", "SAP", records + records)


@pytest.mark.parametrize("damage", [
    lambda line: " " + line,              # indented
    lambda line: "- " + line,             # a list item
    lambda line: "**" + line + "**",      # emphasized
    lambda line: line.replace("] ", "]"),  # no space after the anchor
])
def test_a_statement_line_is_never_dropped_in_silence(form, damage):
    """Section 6.6: a parser recovers every decision. A damaged line is an error, not a gap."""
    records = [{"id": "ae.teae.end", "unit": "mod-ae-emergence", "value": {"rule": "no_end"}},
               {"id": "ae.teae.start", "unit": "mod-ae-emergence",
                "value": {"rule": "on_or_after_first_dose_date"}}]
    text = form.render_document("sap", "SAP", records)
    line = "[1/s2] Treatment emergence has no end date."
    assert line in text and len(form.parse_document(text)[1]) == 2
    with pytest.raises(StandardFormError, match="not an anchored statement"):
        form.parse_document(text.replace(line, damage(line)))


def test_a_document_names_its_catalog_and_itself_once(catalog, form):
    records = [{"id": "ae.teae.end", "unit": "mod-ae-emergence", "value": {"rule": "no_end"}}]
    text = form.render_document("sap", "SAP", records)
    named = f"Catalog: {catalog.name} {catalog.version}"
    assert named in text
    with pytest.raises(StandardFormError, match="written for the catalog"):
        form.parse_document(text.replace(named, f"Catalog: {catalog.name} 99"))
    with pytest.raises(StandardFormError, match="no 'Catalog:"):
        form.parse_document(text.replace(named + "\n", ""))
    with pytest.raises(StandardFormError, match="second 'Document:' line"):
        form.parse_document(text + "\nDocument: protocol\n")


@pytest.mark.parametrize("entry_id, value, problem", [
    ("bds.window.table", {"rule": "protocol_windows", "windows": [
        {"visit": "Week 2", "target": 15, "low": 22, "high": 8}]}, "is above"),
    ("bds.window.table", {"rule": "protocol_windows", "windows": [
        {"visit": "Week 2", "target": 30, "low": 8, "high": 21}]}, "is outside"),
    ("bds.window.table", {"rule": "protocol_windows", "windows": [
        {"visit": "Week 2", "target": 15, "low": 8, "high": 21},
        {"visit": "Week 4", "target": 21, "low": 20, "high": 42}]}, "overlap"),
    ("bds.window.table", {"rule": "protocol_windows", "windows": [
        {"visit": "Week 2", "target": 15, "low": 8, "high": 21},
        {"visit": "Week 2", "target": 29, "low": 22, "high": 42}]}, "repeats a value"),
    ("bds.window.table", {"rule": "midpoint_windows", "visits": [
        {"visit": "Week 4", "target": 29}, {"visit": "Week 2", "target": 15}]}, "must ascend"),
    ("bds.window.table", {"rule": "midpoint_windows", "visits": [
        {"visit": "Day 1", "target": 1}]}, "is below"),
    ("trt.planned.source", {"rule": "dm_armcd_map", "map": [
        {"code": "A", "label": "Drug"}, {"code": "A", "label": "Placebo"}]}, "repeats a value"),
    ("demo.age.groups", {"rule": "stated_cuts", "cuts": [65, 18]}, "must ascend"),
])
def test_a_table_that_contradicts_itself_is_not_a_decision(catalog, form, entry_id, value,
                                                           problem):
    unit = catalog.entry(entry_id).units[0]
    with pytest.raises(StandardFormError, match=problem):
        form.render(entry_id, unit, value)


@pytest.mark.parametrize("damaged", [
    "Treatment emergence has no end date.",            # the anchor is gone
    "(1/s2) Treatment emergence has no end date.",     # the anchor is in round brackets
    "* Treatment emergence has no end date.",
])
def test_a_statement_without_its_anchor_is_an_error(form, damaged):
    records = [{"id": "ae.teae.end", "unit": "mod-ae-emergence", "value": {"rule": "no_end"}},
               {"id": "ae.teae.start", "unit": "mod-ae-emergence",
                "value": {"rule": "on_or_after_first_dose_date"}}]
    text = form.render_document("sap", "SAP", records)
    line = "[1/s2] Treatment emergence has no end date."
    assert line in text
    with pytest.raises(StandardFormError, match="without its anchor"):
        form.parse_document(text.replace(line, damaged))
