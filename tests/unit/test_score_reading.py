"""The reading score (PLAN.md section 9.1): every dimension, planted (rule R5).

Each test changes one thing in a candidate that is otherwise the gold
records, and asks that exactly the dimension it belongs to falls.
"""

from __future__ import annotations

import copy

from specfirst.score.reading import Documents, ask_keys, score, unmapped_keys

UNITS = ("mod-x", "tfl-y")
DOCUMENTS = Documents({
    "sap": "# Plan\n\nDocument: sap\n\n## 1 Things (mod-x)\n\n"
           "[1/s1] The window is 30 days long.\n\n"
           "[1/s2] The list of values is\n\"A\", \"B\".\n\n"
           "Some text that no anchor holds: the window is 31 days long.\n",
    "house": "[1/s1] The set is the safety set.\n\nMeaning: every dosed subject.\n",
})


def record(entry, unit, value, status, kind, cite=None, **more):
    made = {"id": entry, "unit": unit, "value": value, "status": status, "class": kind, **more}
    if cite:
        made["citations"] = [{"doc": cite[0], "anchor": cite[1], "quote": cite[2]}]
    return made


GOLD = [
    record("a.window", "mod-x", {"rule": "days", "days": 30}, "stated", "document_rule",
           ("sap", "1/s1", "The window is 30 days long.")),
    record("a.list", "mod-x", {"rule": "stated", "values": ["A", "B"]}, "stated",
           "document_rule", ("sap", "1/s2", "The list of values is \"A\", \"B\".")),
    record("a.set", "tfl-y", {"rule": "safety"}, "default", "house_default",
           ("house", "1/s1", "The set is the safety set.")),
    record("a.ask", "mod-x", {"rule": "cut", "at": 65}, "asked", "study_input"),
    record("a.quirk", "mod-x", {"rule": "odd"}, "stated", "gold_quirk"),
    record("a.nogold", "mod-x", {"rule": "lost"}, "stated", "no_gold"),
    record("b.other", "mod-z", {"rule": "one"}, "default", "house_default",
           ("house", "1/s1", "The set is the safety set.")),
]
DEFAULTS = {("a.set", "tfl-y"): GOLD[2]}
ASKED = {("a.ask", "mod-x")}


def scored(candidate, **more):
    more.setdefault("asked", ASKED)
    return score(GOLD, candidate, DEFAULTS, UNITS, DOCUMENTS, **more)


def changed(entry, **fields):
    records = copy.deepcopy(GOLD)
    for item in records:
        if item["id"] == entry:
            item.update(fields)
    return records


def marks(result, entry):
    return next(item for item in result.decisions if item.key[0] == entry).marks()


def test_the_gold_records_score_100_percent():
    result = scored(GOLD)
    assert result.perfect
    assert [item.key[0] for item in result.decisions] == [
        "a.window", "a.list", "a.set", "a.ask", "a.quirk", "a.nogold"]
    assert result.total("value") == (4, 4)
    assert result.total("quote") == (3, 3) and result.total("span") == (3, 3)
    assert result.outside == [("b.other", "mod-z")]


def test_another_value_fails_value_only():
    result = scored(changed("a.window", value={"rule": "days", "days": 31}))
    assert marks(result, "a.window") == {"value": False, "status": True, "quote": True,
                                         "span": True}
    assert [item.key[0] for item in result.wrong()] == ["a.window"]
    assert not result.perfect


def test_a_slot_is_compared_exactly():
    assert marks(scored(changed("a.list", value={"rule": "stated", "values": ["B", "A"]})),
                 "a.list")["value"] is False
    assert marks(scored(changed("a.list", value={"rule": "stated", "values": ["A"]})),
                 "a.list")["value"] is False
    assert marks(scored(changed("a.window", value={"rule": "days", "days": 30.0})),
                 "a.window")["value"] is True


def test_another_status_fails_status_only():
    result = scored(changed("a.window", status="default"))
    assert marks(result, "a.window") == {"value": True, "status": False, "quote": True,
                                         "span": True}


def test_a_decision_left_out_takes_the_house_default():
    result = scored([r for r in GOLD if r["id"] != "a.set"])
    item = next(item for item in result.decisions if item.key[0] == "a.set")
    assert item.source == "default" and item.status == "default"
    assert item.marks() == {"value": True, "status": True, "quote": True, "span": True}
    assert result.perfect


def test_a_decision_left_out_without_a_default_stays_open():
    result = scored([r for r in GOLD if r["id"] != "a.window"])
    item = next(item for item in result.decisions if item.key[0] == "a.window")
    assert item.source == "open" and item.status is None
    assert item.marks() == {"value": False, "status": False, "quote": False, "span": False}


def test_a_study_input_counts_as_a_question_asked_not_as_a_guess():
    guessed = scored(GOLD, asked=set())
    item = next(item for item in guessed.decisions if item.key[0] == "a.ask")
    assert item.value is False and "guess" in item.notes[0]
    assert (guessed.asks.given, guessed.asks.gold, guessed.asks.hits) == (0, 1, 0)
    assert guessed.asks.recall == 0 and guessed.asks.precision is None
    assert marks(scored(GOLD), "a.ask")["value"] is True


def test_asking_for_what_is_stated_costs_precision():
    result = scored(GOLD, asked={*ASKED, ("a.window", "mod-x")})
    assert (result.asks.given, result.asks.gold, result.asks.hits) == (2, 1, 1)
    assert result.asks.precision == 0.5 and result.asks.recall == 1
    assert not result.perfect


def test_a_quirk_and_a_decision_without_gold_are_counted_and_never_scored():
    result = scored(changed("a.quirk", value={"rule": "anything"}))
    assert marks(result, "a.quirk") == {"value": None, "status": None, "quote": None,
                                        "span": None}
    assert marks(result, "a.nogold")["value"] is None
    assert result.perfect
    by_class = {row["class"]: row for row in result.counts("class")}
    assert by_class["gold_quirk"]["decisions"] == 1 and by_class["gold_quirk"]["scored"] == 0
    assert by_class["document_rule"]["value_of"] == 2


def test_a_quote_that_is_not_in_the_document():
    cite = [{"doc": "sap", "anchor": "1/s1", "quote": "The window is 30 days long, about."}]
    result = scored(changed("a.window", citations=cite))
    assert marks(result, "a.window") == {"value": True, "status": True, "quote": False,
                                         "span": False}


def test_a_citation_that_points_at_the_wrong_span():
    cite = [{"doc": "sap", "anchor": "1/s2", "quote": "The window is 30 days long."}]
    result = scored(changed("a.window", citations=cite))
    assert marks(result, "a.window") == {"value": True, "status": True, "quote": True,
                                         "span": False}


def test_a_quote_from_elsewhere_in_the_document_under_the_gold_anchor():
    cite = [{"doc": "sap", "anchor": "1/s1", "quote": "the window is 31 days long."}]
    result = scored(changed("a.window", citations=cite))
    assert marks(result, "a.window")["quote"] is True
    assert marks(result, "a.window")["span"] is False


def test_a_span_runs_to_the_next_empty_line_and_blanks_do_not_count():
    assert DOCUMENTS.span("sap", "1/s2") == 'The list of values is "A", "B".'
    assert DOCUMENTS.in_span("sap", "1/s2", 'values   is\n"A"')
    assert DOCUMENTS.span("house", "1/s1") == "The set is the safety set."
    assert DOCUMENTS.span("sap", "9/s9") is None and DOCUMENTS.span("none", "1/s1") is None
    assert not DOCUMENTS.has("sap", "  ")


def test_no_citation_fails_quote_and_span():
    records = changed("a.window")
    del records[0]["citations"]
    assert marks(scored(records), "a.window") == {"value": True, "status": True,
                                                  "quote": False, "span": False}


def test_gold_without_a_citation_gives_no_span_to_score():
    gold = copy.deepcopy(GOLD)
    del gold[0]["citations"]
    result = score(gold, GOLD, DEFAULTS, UNITS, DOCUMENTS, ASKED)
    assert marks(result, "a.window") == {"value": True, "status": True, "quote": True,
                                         "span": None}


def test_unmapped_is_scored_by_document_and_anchor():
    result = scored(GOLD, unmapped={("sap", "4/p2"), ("sap", "5/p1")},
                    gold_unmapped={("sap", "4/p2")})
    assert (result.unmapped.given, result.unmapped.gold, result.unmapped.hits) == (2, 1, 1)
    assert result.unmapped.precision == 0.5 and not result.perfect
    assert scored(GOLD, unmapped={("sap", "4/p2")}, gold_unmapped={("sap", "4/p2")}).perfect


def test_two_records_for_one_decision_and_a_record_gold_does_not_have():
    result = scored([*GOLD, changed("a.window", value={"rule": "days", "days": 1})[0],
                     record("c.new", "mod-x", {"rule": "x"}, "stated", "document_rule")])
    assert marks(result, "a.window")["value"] is True  # the first record is taken
    assert len(result.problems) == 1 and "more than one record" in result.problems[0]
    assert result.unknown == [("c.new", "mod-x")]
    assert not result.perfect


def test_counts_by_unit_name_their_denominators():
    result = scored(changed("a.window", value={"rule": "days", "days": 31}))
    by_unit = {row["unit"]: row for row in result.counts("unit")}
    assert (by_unit["mod-x"]["value"], by_unit["mod-x"]["value_of"]) == (2, 3)
    assert (by_unit["tfl-y"]["value"], by_unit["tfl-y"]["value_of"]) == (1, 1)
    assert by_unit["mod-x"]["decisions"] == 5 and by_unit["mod-x"]["scored"] == 3
    both = result.counts("both")
    assert {(row["class"], row["unit"]) for row in both} >= {("document_rule", "mod-x"),
                                                             ("house_default", "tfl-y")}


def test_an_unseparated_decision_is_still_compared_by_value():
    gold = copy.deepcopy(GOLD)
    gold[0]["identifiable"] = "unseparated"
    result = score(gold, changed("a.window", value={"rule": "days", "days": 31}), DEFAULTS,
                   UNITS, DOCUMENTS, ASKED)
    item = result.decisions[0]
    assert item.identifiable == "unseparated" and item.value is False


def test_the_files_of_a_run_are_read_into_keys():
    units = {"a.ask": ("mod-x",), "t.pop": ("tfl-y", "tfl-z")}
    assert ask_keys([{"decision": "a.ask", "question": "?"}, {"decision": "t.pop"},
                     {"decision": "t.pop", "unit": "tfl-z"}, {"question": "?"}], units) == {
        ("a.ask", "mod-x"), ("t.pop", "tfl-z")}
    assert unmapped_keys([{"doc": "sap", "anchor": "4/p2", "text": "x"}, {"doc": "sap"}]) == {
        ("sap", "4/p2")}
