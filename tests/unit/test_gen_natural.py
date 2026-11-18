"""The natural form (specfirst.gen.natural) and the documents of a kit (specfirst.gen.documents).

The slot check and the read-back check are tested on planted defects first (rule R5): a
changed number, a lost variable name, two values exchanged, a text that is no paragraph,
a read-back that picked another alternative. The loop is run with the test in the place
of the rewriter and the verifier, up to the fallback to the phrasing template.
"""

from __future__ import annotations

import json

import pytest

from specfirst.compile import catalog as catalogs
from specfirst.compile import house as houses
from specfirst.compile.standard_form import StandardForm
from specfirst.gen import decisions, documents, natural, pgfix, probes, study
from specfirst.gen import design as designs
from specfirst.gen.rng import Stream


@pytest.fixture(scope="module")
def catalog(root):
    return catalogs.load(catalogs.default_dir(root))


@pytest.fixture(scope="module")
def house(root):
    return houses.load(houses.default_dir(root))


@pytest.fixture(scope="module")
def design(catalog):
    for number in range(200):
        found = pgfix.sample(f"natural-{number}", study.catalog_label(catalog))
        if designs.features(found)["design.has_efficacy_set"] and len(designs.arms(found)) >= 3:
            return found
    raise AssertionError("no design with three arms and an efficacy-evaluable set")


def _render(catalog, entry_id, value, unit=None):
    entry = catalog.entries[entry_id]
    unit = unit or ("tfl-ae-summary" if entry.per_family else entry.units[0])
    return StandardForm(catalog).render(entry_id, unit, value), unit


def test_the_tokens_of_a_statement(catalog):
    assert natural.tokens(catalog, "ae.teae.end", "mod-ae-emergence",
                          {"rule": "last_dose_plus_days", "days": 14}) == ["14", "days"]
    assert natural.tokens(catalog, "demo.age.groups", "mod-demographics",
                          {"rule": "lt65_65to80_gt80"}) == ["65", "65", "80", "80", "years"]
    assert natural.tokens(catalog, "trt.planned.source", "mod-treatment", {
        "rule": "dm_armcd_map", "map": [{"code": "PBO", "label": "Placebo"},
                                        {"code": "KRD5", "label": "Low Dose"}]}) == [
        "PBO", "Placebo", "KRD5", "Low Dose", "DM.ARMCD"]
    # Groups keep their order; groups may stand in any order.
    assert natural.token_groups(catalog, "date.studyday.origin", "mod-treatment",
                                {"rule": "dm_rfstdtc"}) == [["1"], ["DM.RFSTDTC"]]
    assert natural.tokens(catalog, "tfl.population", "tfl-ae-summary",
                          {"rule": "safety"}) == ["adverse event summary table"]
    assert natural.tokens(catalog, "ae.related.values", "mod-ae-emergence", {
        "rule": "stated_list", "values": ["POSSIBLE", "PROBABLE"]}) == ["POSSIBLE", "PROBABLE"]
    assert natural.tokens(catalog, "trt.end.source", "mod-treatment",
                          {"rule": "last_ex_end_date"}) == []


def test_the_slot_check_fails_on_planted_defects(catalog):
    wanted = natural.token_groups(catalog, "trt.planned.source", "mod-treatment", {
        "rule": "dm_armcd_map", "map": [{"code": "PBO", "label": "Placebo"},
                                        {"code": "KRD5", "label": "Low Dose"}]})
    good = ("Planned treatment will be decoded from the planned arm code (DM.ARMCD): PBO "
            "stands for Placebo and KRD5 for Low Dose.")
    assert natural.slot_problems(good, wanted) == []
    assert natural.slot_problems(good.replace("DM.ARMCD", "the arm code"), wanted) == [
        "'DM.ARMCD' is not in the paragraph"]
    assert sorted(natural.slot_problems(good.replace("DM.ARMCD", "DM.ARMCDX"), wanted)) == [
        "'ARMCDX' is not in the statement", "'DM.ARMCD' is not in the paragraph"]
    swapped = good.replace("Placebo", "@").replace("Low Dose", "Placebo").replace("@", "Low Dose")
    found = natural.slot_problems(swapped, wanted)
    assert found and all("is out of the order of the statement" in item for item in found)
    days = natural.token_groups(catalog, "ae.teae.end", "mod-ae-emergence",
                          {"rule": "last_dose_plus_days", "days": 14})
    period = "The treatment-emergent period will close 14 days after the treatment end date."
    assert natural.slot_problems(period, days) == []
    for changed in ("15 days", "140 days", "14.5 days", "1 4 days"):
        assert natural.slot_problems(period.replace("14 days", changed), days), changed
    assert natural.slot_problems(period.replace("days", "weeks"), days) == [
        "'days' is not in the paragraph"]
    ages = natural.token_groups(catalog, "demo.age.groups", "mod-demographics",
                          {"rule": "lt65_65to80_gt80"})
    text = "Age groups will be below 65, 65 to 80, and above 80 years."
    assert natural.slot_problems(text, ages) == []
    assert natural.slot_problems(text.replace("above 80", "above 85"), ages) == [
        "the number 85 is not in the statement",
        "'80' stands 1 times in the paragraph, the statement has it 2 times"]
    # What is no paragraph of a document.
    assert natural.slot_problems(period + "\nMore.", days) == ["the paragraph is not one line"]
    assert natural.slot_problems("[3/p1] " + period, days)[0] == "the paragraph holds an anchor"
    assert natural.slot_problems("# " + period, days) == [
        "the paragraph starts with a blank or a Markdown mark"]
    assert natural.slot_problems(period.replace("will", "wi" + chr(0x2019) + "ll"), days) == [
        "the paragraph is not ASCII"]
    assert natural.slot_problems("", days) == ["the paragraph is empty"]


def test_every_phrasing_template_of_the_slice_keeps_its_slots(catalog, house, design):
    """The fallback of section 6.6 must pass the slot check of its statement."""
    parameters = probes.Parameters.of(design).as_record()
    seen = 0
    for entry in decisions.entries(catalog, design):
        for value in decisions.variants(entry, design, parameters):
            for name, choices in decisions.slot_values(entry.id, value["rule"], design,
                                                       parameters).items():
                for choice in choices:
                    one = {**value, name: choice}
                    _, unit = _render(catalog, entry.id, one)
                    for family in ("plain", "formal", "brief"):
                        text = natural.phrasing(catalog, entry.id, unit, one, family)
                        wanted = natural.token_groups(catalog, entry.id, unit, one)
                        assert natural.slot_problems(text, wanted) == [], (family, text)
                        seen += 1
            if not decisions.slot_values(entry.id, value["rule"], design, parameters):
                _, unit = _render(catalog, entry.id, value)
                text = natural.phrasing(catalog, entry.id, unit, value)
                assert natural.slot_problems(text, natural.token_groups(
                    catalog, entry.id, unit, value)) == [], text
                seen += 1
    assert seen >= 50


def _wanted(catalog, entry_id, value):
    statement, unit = _render(catalog, entry_id, value)
    key = natural.key_of(statement)
    return {key: {"key": key, "entry": entry_id, "unit": unit, "value": value,
                  "statement": statement, "document": "sap"}}


def test_the_loop_accepts_what_reads_back_and_falls_back_after_three_failures(catalog,
                                                                               tmp_path):
    store = natural.Store.load(tmp_path)
    value = {"rule": "last_dose_plus_days", "days": 14}
    wanted = _wanted(catalog, "ae.teae.end", value)
    key = next(iter(wanted))
    request = natural.rewrite_request(catalog, store, wanted, [])
    assert [item["key"] for item in request["paragraphs"]] == [key]
    # Attempt 1: a changed number. The slot check refuses it; it is never read back.
    lines = natural.propose(catalog, store, wanted, {"paragraphs": [
        {"key": key, "text": "Treatment emergence ends 15 days after the treatment end date."}]},
        "call-1")
    assert "SLOTS" in lines[0] and natural.readback_request(catalog, store)["items"] == []
    # Attempt 2 keeps the slots; the verifier reads it as another alternative.
    text = "Emergence will stop 14 days after the treatment end date."
    natural.propose(catalog, store, wanted, {"paragraphs": [{"key": key, "text": text}]},
                    "call-2")
    request = natural.readback_request(catalog, store)
    assert len(request["items"]) == 1
    item = request["items"][0]
    # The verifier sees the paragraph, the question and the alternatives: no statement, no
    # value, and an ID that says nothing.
    assert set(item) == {"item", "paragraph", "question", "alternatives"}
    assert item["paragraph"] == text and wanted[key]["statement"] not in json.dumps(request)
    assert natural.NONE not in {alt["id"] for alt in item["alternatives"]}
    natural.readback(catalog, store, {"items": [{"item": item["item"], "pick": "end_of_study"}]},
                     "call-3")
    assert not store.paragraphs[key]["accepted"] and store.failed(store.paragraphs[key]) == 2
    # Attempt 3 fails the slot check too: three failures, the phrasing template follows.
    lines = natural.propose(catalog, store, wanted, {"paragraphs": [{"key": key, "text": "x"}]},
                            "call-4")
    attempts = store.paragraphs[key]["attempts"]
    assert len(attempts) == 4 and attempts[3]["by"] == "template" and attempts[3]["slots"] == []
    assert attempts[3]["text"] == natural.phrasing(catalog, "ae.teae.end", "mod-ae-emergence",
                                                   value)
    assert natural.rewrite_request(catalog, store, wanted, [])["paragraphs"] == []
    request = natural.readback_request(catalog, store)
    natural.readback(catalog, store, {"items": [{"item": request["items"][0]["item"],
                                                 "pick": "last_dose_plus_days"}]}, "call-5")
    assert store.paragraphs[key]["accepted"] == 4
    assert store.accepted(wanted[key]["statement"])["by"] == "template"
    # The store is saved and read back as it was; a call is logged once.
    store.add_call({"call": "call-5", "role": "read-back"})
    with pytest.raises(natural.NaturalError):
        store.add_call({"call": "call-5", "role": "read-back"})
    store.save()
    again = natural.Store.load(tmp_path)
    assert again.paragraphs == store.paragraphs and again.calls == store.calls


def test_a_paragraph_passes_only_with_its_own_read_back(catalog, tmp_path):
    store = natural.Store.load(tmp_path)
    value = {"rule": "half_even"}
    wanted = _wanted(catalog, "tfl.rounding.rule", value)
    key = next(iter(wanted))
    text = "Numbers displayed in the adverse event summary table will be rounded half to even."
    natural.propose(catalog, store, wanted, {"paragraphs": [{"key": key, "text": text}]}, "w")
    item = natural.readback_request(catalog, store)["items"][0]["item"]
    natural.readback(catalog, store, {"items": [{"item": item, "pick": "half_even"}]}, "r")
    record = {"id": "tfl.rounding.rule", "unit": "tfl-ae-summary", "value": value,
              "statement": wanted[key]["statement"]}
    assert natural.paragraph_problems(catalog, store, record, text) == []
    # The planted bad rewrite: one word changed after the read-back.
    changed = text.replace("half to even", "half to odd")
    assert natural.paragraph_problems(catalog, store, record, changed) == [
        "read-back: no read-back of this text in the store"]
    # The read-back of another alternative.
    other = {**record, "value": {"rule": "half_away_from_zero"}}
    assert natural.paragraph_problems(catalog, store, other, text)[-1].startswith(
        "read-back: read back as half_even")


@pytest.mark.parametrize("tier", documents.TIERS)
def test_the_documents_of_each_tier(catalog, house, design, tier, tmp_path):
    parameters = probes.Parameters.of(design).as_record()
    values = decisions.sample(catalog, house, design, parameters, Stream("documents", tier))
    listed = decisions.vector(catalog, house, design, values)
    store = natural.Store.load(tmp_path / "empty-store")
    records, written = documents.write(catalog, house, design, listed, tier,
                                       decisions.SLICE_UNITS, Stream("tier", tier),
                                       tmp_path / "kit", store)
    state = {(r["id"], r["unit"]): r["status"] for r in records}
    defaults = {(r["id"], r["unit"]) for r in houses.default_decisions(catalog, house)}
    none_default = {key for key in state if key not in defaults and key[1] in
                    decisions.SLICE_UNITS}
    assert {key[0] for key in none_default} == {"ae.related.values", "pop.efficacy.rule"}
    if tier == "full":
        assert set(state.values()) == {"stated"}
    elif tier == "standard":
        assert "asked" not in state.values() and "default" in state.values()
    else:
        assert {key for key, status in state.items() if status == "asked"} == none_default
    assert written["tier"] == tier and written["paragraphs"]["missing"] == written["stated"]
    oracle = documents.read_oracle(tmp_path / "kit")
    assert {(a["decision"], a["unit"]) for a in oracle["answers"]} == {
        key for key, status in state.items() if status == "asked"}
    # The standard form reads back to the stated decisions, each in the document of its home.
    form = StandardForm(catalog)
    texts = documents.read_texts(tmp_path / "kit")
    parsed = {}
    for doc in ("protocol", "sap"):
        name, items = form.parse_document(texts[documents.standard_id(doc)])
        assert name == f"{doc}-standard"
        parsed.update({(i["id"], i["unit"]): doc for i in items})
    assert parsed == {(r["id"], r["unit"]): documents.home_of(r["id"])[0] for r in records
                      if r["status"] == "stated"}
    # Every paragraph of the natural form has its own anchor; every stated decision cites
    # its paragraph, whose text it quotes; an asked decision is in no document.
    for doc in ("protocol", "sap"):
        anchored = documents.paragraphs(texts[doc])
        lines = [line for line in texts[doc].split("\n") if line.startswith("[")]
        assert len(lines) == len(anchored) >= 3
        assert f"Document ID: {doc}" in texts[doc]
    for record in records:
        if record["status"] == "stated":
            natural_cite = record["citations"][1]
            assert documents.paragraphs(texts[natural_cite["doc"]])[
                natural_cite["anchor"]] == natural_cite["quote"]
        if record["status"] == "asked":
            assert record["statement"] not in " ".join(texts.values())
    # The arms of the protocol, in its order, stand in the natural protocol.
    order = [texts["protocol"].index(f"- Arm {arm['name']} ") for arm in designs.arms(design)]
    assert order == sorted(order)


def test_the_tier_of_a_kit(catalog):
    assert documents.TIER_PLAN.count("ask") == 2 and len(documents.TIER_PLAN) == 10
    assert [documents.tier_of("s", n) for n in (4, 7, 14)] == ["ask", "ask", "ask"]
    assert {documents.tier_of(f"seed-{n}", None) for n in range(20)} == {"full", "standard"}
    with pytest.raises(ValueError, match="a tier is one of"):
        documents.statuses(catalog, None, [], "other", ())


def test_the_gate_gen_3a_has_the_checks_of_the_plan():
    """PLAN.md section 13.5, gen-3, for the slice: the parser, the slot and read-back
    checks, a planted bad rewrite, the visible probes. Drift first."""
    from specfirst import gates

    names = [check.name for check in gates.GATES["gen-3a"]]
    assert names[0] == "environment" and names[-1] == "ASCII"
    for needed in ("unit tests", "kits", "parser", "slots", "read-back", "bad rewrite", "tiers",
                   "anchors", "visible probes", "summary"):
        assert needed in names
    # The kits are written by the check "kits" and removed by the check "summary".
    assert names.index("kits") < names.index("parser") < names.index("summary")
    assert names.index("summary") == max(names.index(name) for name in (
        "parser", "slots", "read-back", "bad rewrite", "tiers", "anchors", "visible probes",
        "summary"))


def test_the_slot_check_keeps_case_and_refuses_what_the_statement_lacks(catalog):
    """Review of gen-3a, finding D5: rewrites that change the meaning and passed the first
    slot check. Values keep their case, and the paragraph may hold no number and no word
    in capitals that the statement lacks."""
    def groups(entry_id, value, unit=None):
        _, unit = _render(catalog, entry_id, value, unit)
        return natural.token_groups(catalog, entry_id, unit, value)

    related = groups("ae.related.values", {"rule": "stated_list", "values": ["RELATED"]})
    base = "An adverse event will be regarded as related to study treatment when its causality "
    assert natural.slot_problems(base + "is one of RELATED.", related) == []
    assert natural.slot_problems(base + "is one of PROBABLY RELATED.", related) == [
        "'PROBABLY' is not in the statement"]
    two = groups("ae.related.values", {"rule": "stated_list",
                                       "values": ["PROBABLY RELATED", "RELATED"]})
    assert natural.slot_problems(base + "is PROBABLY RELATED, NOT RELATED.", two) == [
        "'NOT' is not in the statement"]
    cased = groups("ae.related.values", {"rule": "stated_list",
                                         "values": ["POSSIBLE", "PROBABLE"]})
    assert natural.slot_problems(base + "is one of POSSIBLE, PROBABLE.", cased) == []
    assert natural.slot_problems(base + "is one of possible, probable.", cased) == [
        "'POSSIBLE' is not in the paragraph", "'PROBABLE' is not in the paragraph"]
    rows = groups("tfl.ae.summary.rows", {"rule": "stated_rows",
                                          "rows": ["FATAL", "SERIOUS", "RELATED", "ANY"]})
    table = "The adverse event summary table will show the rows "
    assert natural.slot_problems(table + "FATAL, SERIOUS, RELATED, ANY, in this order.",
                                 rows) == []
    assert natural.slot_problems(table + "FATAL, SERIOUS, RELATED, in this order, without "
                                 "any other row.", rows) == ["'ANY' is not in the paragraph"]
    window = groups("ae.teae.end", {"rule": "last_dose_plus_days", "days": 30})
    assert natural.slot_problems("Emergence will end 30 days after the treatment end date plus "
                                 "2 days.", window) == ["the number 2 is not in the statement"]
    # A word in capitals of the template text is a token of its own.
    pooled = groups("demo.race.pooling", {"rule": "pooled_below_count", "count": 5})
    assert ["OTHER"] in pooled
    assert natural.slot_problems("A race category with fewer than 5 subjects will be pooled "
                                 "into the category Other.", pooled) == [
        "'OTHER' is not in the paragraph"]


def test_a_read_back_that_cannot_tell_agreement_from_abstention_does_not_count(catalog,
                                                                               tmp_path):
    """Review of gen-3a, finding D3 (lesson 57): `tfl.columns.total` has an alternative
    `none`; a pick `none` under a call that told the verifier to answer `none` for "none of
    them" does not count, and the paragraph is read again."""
    store = natural.Store.load(tmp_path)
    value = {"rule": "none"}
    wanted = _wanted(catalog, "tfl.columns.total", value)
    key = next(iter(wanted))
    text = "The adverse event summary table will not include a total column."
    natural.propose(catalog, store, wanted, {"paragraphs": [{"key": key, "text": text}]}, "w")
    item = natural.readback_request(catalog, store)["items"][0]["item"]
    store.add_call({"call": "old", "role": "read-back", "abstention": "none"})
    natural.readback(catalog, store, {"items": [{"item": item, "pick": "none"}]}, "old")
    record = {"id": "tfl.columns.total", "unit": "tfl-ae-summary", "value": value,
              "statement": wanted[key]["statement"]}
    assert natural.paragraph_problems(catalog, store, record, text) == [
        "read-back: the only read-back of this text cannot tell agreement from abstention"]
    request = natural.readback_request(catalog, store)
    assert [one["item"] for one in request["items"]] == [item]
    assert natural.NONE in request["rules"][0]
    store.add_call({"call": "new", "role": "read-back", "abstention": natural.NONE})
    natural.readback(catalog, store, {"items": [{"item": item, "pick": "none"}]}, "new")
    attempt = store.paragraphs[key]["attempts"][0]
    assert attempt["readback"]["by"] == "old" and attempt["again"][0]["by"] == "new"
    assert natural.paragraph_problems(catalog, store, record, text) == []
    assert natural.readback_request(catalog, store)["items"] == []


def test_the_sap_names_the_protocol_where_it_sends_a_reader_to_the_house(catalog, house,
                                                                          design):
    """Review of gen-3a, finding D4: the protocol states decisions too; the SAP may not
    send a reader to the house standard for them."""
    for tier in documents.TIERS:
        intro = documents.sap_paragraphs(design, tier, house)["intro"][0]
        assert "this plan and the protocol" in intro.lower() or \
            "neither this plan nor the protocol" in intro, intro


def test_a_gate_refuses_another_store(root, monkeypatch):
    """Review of gen-3a, finding D6: a gate writes and judges kits from the store of the
    repository only."""
    from specfirst import gates

    lines: list[str] = []
    monkeypatch.setenv("SPECFIRST_REWRITES", "/elsewhere")
    check = gates.Check("demo", "nothing", lambda ctx: True)
    assert gates.run_gate(root, "demo", (check,), echo=lines.append) == 1
    assert any("SPECFIRST_REWRITES is set" in line for line in lines)


def test_the_store_in_a_checkout_takes_no_secret_statement(root, tmp_path):
    """Review of gen-3a, finding D7: the statements of dev, test and sealed kits are secret
    (section 8); only the kits of the gate seed, whose seed is in the repository, and train
    kits may go into the store of the repository."""
    import yaml

    from specfirst.gen import command, gate2, kits
    from specfirst.gen.rng import seed_sha256

    def kit(name, split, seed):
        folder = tmp_path / name
        folder.mkdir()
        (folder / kits.MANIFEST).write_text(yaml.safe_dump(
            {"split": split, "seed_sha256": seed_sha256(seed)}), encoding="ascii")
        return folder

    folders = [kit("dev-secret", "dev", "a secret seed/kit-5"),
               kit("train-secret", "train", "a secret seed/kit-1"),
               kit("dev-gate", "dev", kits.kit_seed(gate2.SEED, 5))]
    assert command._secret_kits(root, natural.STORE, folders) == ["dev-secret"]
    outside = tmp_path / "store-outside"
    outside.mkdir()
    assert command._secret_kits(root, outside, folders) == []
