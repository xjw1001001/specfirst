"""The pilot's decision records of the demographics and AE tables (issue #31, ADR-022) and the
rules of the decisions check that hold them: a record of the catalog the kit names fits its
entry (unit, value, statement, house default), a stated record cites a quote, and every
quote stands in its document. Each rule fails on a planted defect first (rule R5).

The records are held for their form, their binds and their quotes, not by result: whether
the reference build does what a value says is std-2's check (PLAN.md section 13.4).
"""

from __future__ import annotations

import copy
import json
from collections import Counter

import pytest
import toy_results as toy

from specfirst import kit as kits
from specfirst.compile import house as houses
from specfirst.machine import ars, decisions, registry

SAFETY = "kits/cdiscpilot01/gold/decisions/safety.jsonl"


@pytest.fixture(scope="module")
def pair(root):
    return houses.load_pair(root, "catalog@2", "open-default@2")


@pytest.fixture(scope="module")
def records(root):
    with open(root / SAFETY, encoding="ascii") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def test_the_records_of_the_two_tables_fit_the_catalog_the_kit_names(root, pair, records):
    kit = kits.load_kit(root, "cdiscpilot01")
    assert kit.standard == ("catalog@2", "open-default@2") and SAFETY.split("cdiscpilot01/")[
        1] in kit.decisions
    catalog_records = [r for r in records if not r["id"].startswith("custom:")]
    assert [p for r in catalog_records for p in decisions.catalog_problems(r, *pair)] == []
    units = {r["unit"] for r in records}
    assert units == {"mod-treatment", "mod-populations", "mod-demographics", "mod-ae-emergence",
                     "tfl-demographics", "tfl-ae-summary", "tfl-ae-soc-pt"}
    assert len({(r["id"], r["unit"]) for r in records}) == len(records) == 49
    # The SAP's mock tables (section 13.2) count as what it states, their masks included
    # (ADR-022, decision 7).
    assert Counter(r["status"] for r in records) == {"stated": 18, "default": 12,
                                                      "conflict": 17, "asked": 2}
    # Every custom record is one the catalog has no alternative or no unit for.
    assert sorted(r["id"] for r in records if r["id"].startswith("custom:")) == [
        "custom:demog-age-display", "custom:demog-baseline-visits", "custom:demog-decimals",
        "custom:socpt-fisher", "custom:socpt-pvalue-format"]
    # A conflict keeps the build's value and cites the document that says otherwise.
    assert all(r["citations"] and "class" not in r for r in records
               if r["status"] == "conflict")


def test_a_default_cites_the_house_standard_by_its_statement(root, records):
    """A record with the status default cites the statement of open-default@2's STANDARD.md
    that sets the default, by its anchor, as house.default_decisions writes it."""
    quotes = decisions.Quotes({"house": houses.default_dir(root, "open-default@2")
                               / "STANDARD.md"})
    defaults = [r for r in records if r["status"] == "default"]
    assert defaults and all(r["class"] == "house_default" for r in defaults)
    for record in defaults:
        assert [c["doc"] for c in record["citations"]] == ["house"]
        assert record["citations"][0]["quote"] == record["statement"]
        assert quotes.found("house", record["statement"]), record["id"]
    assert not quotes.found("house", "Safety analyses group subjects by planned treatment.")


def test_the_records_are_what_the_generator_writes(root, records):
    """Every line of the file is canonical JSON: the order of its keys is the writer's."""
    text = (root / SAFETY).read_text(encoding="ascii")
    assert text == "".join(json.dumps(r) + "\n" for r in records)


@pytest.mark.parametrize(("change", "message"), [
    (lambda r: r.update(unit="tfl-demographics"), "is not one of the entry's"),
    (lambda r: r.update(value={"rule": "every_record"}), "its value is not an alternative"),
    (lambda r: r.update(statement="Safety is everyone."), "is not the one the catalog renders"),
    (lambda r: r.update(status="default"), "the value is not the house's default"),
    (lambda r: r.update(id="pop.nobody.rule"), "no entry of catalog@2"),
])
def test_a_record_that_does_not_fit_its_entry_is_refused(pair, records, change, message):
    record = copy.deepcopy(next(r for r in records if r["id"] == "trt.actual.source"))
    assert decisions.catalog_problems(record, *pair) == []
    change(record)
    found = decisions.catalog_problems(record, *pair)
    assert any(message in problem for problem in found), found


def test_a_default_by_design_is_the_house_default_of_one_of_its_cases(pair, records):
    """pop.safety.rule: the house's default depends on the design; a value of one case is
    the house default, another value is not."""
    record = copy.deepcopy(next(r for r in records if r["id"] == "pop.safety.rule"))
    values = decisions.house_values(*pair, "pop.safety.rule", "mod-populations")
    assert {"rule": "randomized_and_dosed"} in values and len(values) > 1
    record["status"] = "default"
    assert decisions.catalog_problems(record, *pair) == []


def problems_of(root, records, tmp_path, standard=None, columns=None):
    (tmp_path / "doc.txt").write_text("The safety population holds every dosed subject.",
                                      encoding="ascii")
    event = ars.index(toy.event_data())
    known = registry.load(root)
    quotes = decisions.Quotes({"doc": tmp_path / "doc.txt"})
    found = decisions.problems(root, records, [(event, ars.bind(event, known))], known, None,
                               standard, columns, quotes)[1]
    return [problem for problem in found if "no record, and the reporting event" not in problem]


def test_quotes_citations_and_binds_are_held(root, pair, tmp_path):
    record = {"id": "custom:toy-safety", "unit": "mod-populations", "value": {"rule": "dosed"},
              "status": "stated", "class": "document_rule", "statement": "Dosed subjects.",
              "citations": [{"doc": "doc", "anchor": "1", "quote": "every  dosed\nsubject"}],
              "binds": ["ars:SAF", "adam:ADSL.SAFFL"]}
    assert problems_of(root, [record], tmp_path, columns={"adam:ADSL.SAFFL"}) == []
    planted = {
        "the quote 'every treated subject' does not stand": dict(record, citations=[
            {"doc": "doc", "anchor": "1", "quote": "every treated subject"}]),
        "stated, and it cites nothing": dict(record, citations=[]),
        "cites other, which is neither a document of the kit": dict(record, citations=[
            {"doc": "other", "anchor": "1", "quote": "every dosed subject"}]),
        "binds adam:ADSL.SAFFL, which no reporting event": record,  # the column is not built
    }
    for message, given in planted.items():
        columns = None if message.startswith("binds") else {"adam:ADSL.SAFFL"}
        found = problems_of(root, [given], tmp_path, columns=columns)
        assert any(message in problem for problem in found), (message, found)
    # A source that is no document of the kit (the owner's answers) is counted, not checked.
    answers = dict(record, citations=[{"doc": "answers", "anchor": "2026-11-20",
                                       "quote": "anything"}])
    assert problems_of(root, [answers], tmp_path, columns={"adam:ADSL.SAFFL"}) == []
    event = ars.index(toy.event_data())
    known = registry.load(root)
    lines, _ = decisions.problems(root, [answers], [(event, ars.bind(event, known))], known,
                                  None, None, {"adam:ADSL.SAFFL"},
                                  decisions.Quotes({"doc": tmp_path / "doc.txt"}))
    assert "not checked by script: answers 1" in lines[-1]
    # A catalog ID needs the standard of the kit.
    catalog = dict(record, id="pop.safety.rule")
    found = problems_of(root, [catalog], tmp_path, columns={"adam:ADSL.SAFFL"})
    assert any("has a custom ID" in problem for problem in found)
    found = problems_of(root, [catalog], tmp_path, pair, {"adam:ADSL.SAFFL"})
    assert any("its value is not an alternative" in problem for problem in found)
