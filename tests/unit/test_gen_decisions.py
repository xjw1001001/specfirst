"""The decisions of a generated study (specfirst.gen.decisions): variants, sampling, records."""

from __future__ import annotations

import pytest

from specfirst import schemas
from specfirst.compile import catalog as catalogs
from specfirst.compile import house as houses
from specfirst.compile.standard_form import StandardForm
from specfirst.gen import decisions, documents, kits, pgfix, probes, study
from specfirst.gen import design as designs
from specfirst.gen.rng import Stream


@pytest.fixture(scope="module")
def catalog(root):
    return catalogs.load(catalogs.default_dir(root))


@pytest.fixture(scope="module")
def house(root):
    return houses.load(houses.default_dir(root))


def _design(catalog, seed="decisions", efficacy=True, arms=0):
    for number in range(200):
        design = pgfix.sample(f"{seed}-{number}", study.catalog_label(catalog))
        if designs.features(design)["design.has_efficacy_set"] is efficacy and len(
                designs.arms(design)) >= arms and not decisions.held_out_design(design):
            return design
    raise AssertionError("no such design")


def test_every_alternative_of_the_slice_is_a_variant_with_fitting_slots(catalog):
    design = _design(catalog)
    parameters = probes.Parameters.of(design).as_record()
    form = StandardForm(catalog)
    found = decisions.entries(catalog, design)
    assert len(found) == 22 and {e.id for e in found} == set(probes.REACHES)
    for entry in found:
        options = decisions.variants(entry, design, parameters)
        assert [o["rule"] for o in options] == [a.id for a in entry.alternatives]
        unit = decisions.OUTPUT_UNIT if entry.per_family else entry.units[0]
        for option in options:
            form.check_value(entry.id, unit, option)   # raises on a missing or a stray slot
    by_id = {e.id: decisions.variants(e, design, parameters) for e in found}
    # The slots fit the design: the window is the house's (30 days, the probes are built
    # around it), the follow-up length a study may state instead; the tests are measured,
    # the subcategory is that of the treatment record, the map names every arm.
    assert by_id["ae.teae.end"][1] == {"rule": "last_dose_plus_days", "days": 30}
    assert decisions.slot_values("ae.teae.end", "last_dose_plus_days", design, parameters)[
        "days"] == list(dict.fromkeys([30, designs.follow_up_days(design)]))
    assert by_id["pop.randomized.rule"][1]["test"] == parameters["tests"][0]
    assert by_id["disp.status.record"][1]["subcategory"] == "STUDY TREATMENT"
    assert [pair["code"] for pair in by_id["trt.planned.source"][1]["map"]] == [
        arm["name"] for arm in designs.arms(design)]
    assert by_id["ae.related.values"][0]["values"] == decisions.related_values(design)
    # Without an efficacy-evaluable set the entry does not apply and the table cannot use it.
    other = _design(catalog, efficacy=False)
    ids = {e.id: e for e in decisions.entries(catalog, other)}
    assert "pop.efficacy.rule" not in ids and len(ids) == 21
    assert [o["rule"] for o in decisions.variants(ids["tfl.population"], other, parameters)] == [
        "safety", "randomized"]


def test_a_sampled_vector_fits_the_data_and_is_a_function_of_its_stream(catalog, house):
    design = _design(catalog)
    parameters = probes.Parameters.of(design).as_record()
    base = decisions.defaults(catalog, house, design)
    assert "pop.efficacy.rule" not in base and "ae.related.values" not in base
    stated = 0
    seen: dict[str, set[str]] = {}
    for number in range(150):
        values = decisions.sample(catalog, house, design, parameters, Stream("s", number))
        assert values == decisions.sample(catalog, house, design, parameters, Stream("s", number))
        assert not decisions.held_out_combination(values)
        assert values["tfl.output.include"] == {"rule": "included"}
        assert set(values) == {e.id for e in decisions.entries(catalog, design)}
        stated += sum(1 for entry_id, value in values.items() if base.get(entry_id) != value)
        for entry_id, value in values.items():
            seen.setdefault(entry_id, set()).add(value["rule"])
        if values["tfl.columns.total"]["rule"] == "active_arms":
            assert values["tfl.columns.total"]["control"] == decisions.placebo_label(
                design, values)
    # Within the house standard: most decisions are the default, and every alternative of
    # every entry is drawn in some kit.
    assert 5 < stated / 150 < 13
    for entry in decisions.entries(catalog, design):
        if entry.id != "tfl.output.include":
            assert seen[entry.id] == {a.id for a in entry.alternatives}, entry.id
    # gen-2b (ADR-023, decision 6; the owner's choice of 2026-11-23): no combination is
    # refused for the probes; the three that gen-2a refused are drawn.
    drawn = [decisions.sample(catalog, house, design, parameters, Stream("s", number),
                              stated_share=0.9) for number in range(150)]
    assert any(v["disp.status.record"].get("subcategory") == parameters["treatment_subcategory"]
               for v in drawn)
    assert any(v["disp.status.record"].get("subcategory") == parameters["study_subcategory"]
               and v["ae.teae.end"]["rule"] == "last_dose_plus_days"
               and v["trt.end.source"]["rule"] == "ds_date_when_ex_missing" for v in drawn)
    assert any(v["ae.teae.start"]["rule"] == "at_or_after_first_dose_time"
               and v["ae.start.imputation"]["rule"] != "not_completed" for v in drawn)


def test_every_row_list_shows_what_the_probes_of_one_event_need(catalog):
    """The probes of one planted event and of the count of zero are counted by the rows ANY
    and FATAL; every row list a study can state shows both, so no vector is refused for
    them (gen-2b)."""
    design = _design(catalog)
    parameters = probes.Parameters.of(design).as_record()
    for rows in decisions.slot_values("tfl.ae.summary.rows", "stated_rows", design,
                                      parameters)["rows"]:
        assert {"ANY", "FATAL"} <= set(rows)
    assert not hasattr(decisions, "fits")


def test_the_records_of_a_kit_fit_the_schema_and_read_back(root, catalog, house, tmp_path):
    design = _design(catalog)
    parameters = probes.Parameters.of(design).as_record()
    values = decisions.sample(catalog, house, design, parameters, Stream("records"),
                              stated_share=0.6)
    listed = decisions.vector(catalog, house, design, values)
    records, _ = documents.write(catalog, house, design, listed, "standard",
                                 decisions.SLICE_UNITS, Stream("records", "documents"), tmp_path)
    for record in records:
        assert schemas.problems("decision-record", record, root=root) == [], record["id"]
    by_key = {(r["id"], r["unit"]): r for r in records}
    # The slice as sampled; the demographics module at the default; the other outputs out.
    found = decisions.as_values(records)
    assert {entry_id: found[entry_id] for entry_id in values} == values
    assert set(found) - set(values) == {"demo.age.groups", "demo.race.pooling",
                                        "demo.baseline.record", "demo.bmi.rule"}
    for unit in ("tfl-demographics", "tfl-ae-soc-pt", "tfl-vitals-by-visit"):
        assert by_key[("tfl.output.include", unit)]["value"] == {"rule": "not_included"}
        assert by_key[("tfl.output.include", unit)]["status"] == "stated"
    assert by_key[("demo.age.groups", "mod-demographics")]["status"] == "default"
    assert not [r for r in records if r["unit"] == "mod-bds-visits"]
    assert {r["unit"] for r in records if r["unit"].startswith("tfl-") and r["id"]
            != "tfl.output.include"} == {decisions.OUTPUT_UNIT}
    # A default cites the standards document of the house; a stated decision its
    # statement in a standard-form document, then its paragraph in the natural form. The
    # parser reads the standard-form documents back to exactly the stated decisions.
    form = StandardForm(catalog)
    stated = [r for r in records if r["status"] == "stated"]
    parsed = []
    for doc in ("protocol", "sap"):
        name, items = form.parse_document((tmp_path / documents.STANDARD[doc]).read_text())
        assert name == documents.standard_id(doc)
        parsed += items
    assert len(parsed) == len(stated) >= 5
    assert {(p["id"], p["unit"]): p["value"] for p in parsed} == {
        (r["id"], r["unit"]): r["value"] for r in stated}
    for record in records:
        cited = record["citations"][0]
        assert cited["quote"] == record["statement"]
        if record["status"] == "stated":
            home = documents.home_of(record["id"])[0]
            assert [c["doc"] for c in record["citations"]] == [documents.standard_id(home), home]
        else:
            assert cited["doc"] == "house"
        assert (record["status"], record["class"]) in (("stated", "document_rule"),
                                                       ("default", "house_default"))
    assert "pop.efficacy.rule" in {r["id"] for r in stated}     # no house default: stated


def test_scenarios_and_what_an_exam_holds_out(catalog, house):
    assert len(decisions.SCENARIOS) == len(kits.SPLIT_PLAN) == 10
    two_arms = next(pgfix.sample(f"two-{n}", study.catalog_label(catalog)) for n in range(200)
                    if len(designs.arms(pgfix.sample(f"two-{n}", study.catalog_label(
                        catalog)))) == 2)
    with_set = _design(catalog)
    without = _design(catalog, efficacy=False)
    for scenario in decisions.SCENARIOS:
        if scenario.get("feature"):
            assert decisions.scenario_fits(scenario, with_set)
            assert not decisions.scenario_fits(scenario, without)
        if scenario.get("arms"):
            assert not decisions.scenario_fits(scenario, two_arms)
    parameters = probes.Parameters.of(with_set).as_record()
    for number, scenario in enumerate(decisions.SCENARIOS):
        values = decisions.sample(catalog, house, with_set, parameters, Stream("sc", number),
                                  given=scenario["values"])
        assert {k: values[k]["rule"] for k in scenario["values"]} == scenario["values"]
    with pytest.raises(decisions.DecisionError, match="cannot decide"):
        decisions.sample(catalog, house, without, probes.Parameters.of(without).as_record(),
                         Stream("x"), given={"tfl.population": "efficacy"})
    with pytest.raises(decisions.DecisionError, match="a split is one of"):
        decisions.sample(catalog, house, with_set, parameters, Stream("x"), split="exam")
    # The design of a kit: a scenario that needs an efficacy-evaluable set gets one, and no
    # train kit has the allocation ratio that an exam holds out.
    label = study.catalog_label(catalog)
    for number in range(1, 11):
        scenario = decisions.SCENARIOS[kits.scenario_of("any", number)]
        design, _ = kits.sample_design(f"plan-{number}", label, kits.split_of(number), scenario)
        assert decisions.scenario_fits(scenario, design)
        assert not decisions.held_out_design(design)
    assert [kits.split_of(n) for n in range(1, 12)] == [
        "train"] * 4 + ["dev"] * 3 + ["test"] * 3 + ["train"]
    held = [n for n in range(300) if decisions.held_out_design(pgfix.sample(f"h-{n}", label))]
    assert 5 < len(held) < 80      # the variation exists, so holding it out means something
    design, drawn = kits.sample_design(f"h-{held[0]}", label, "train", decisions.SCENARIOS[0])
    assert drawn >= 1 and not decisions.held_out_design(design)
    design, drawn = kits.sample_design(f"h-{held[0]}", label, "sealed", decisions.SCENARIOS[0])
    assert drawn == 0 and decisions.held_out_design(design)
    assert 0 <= kits.scenario_of("a seed", None) < 10
    assert kits.kit_seed("s", 3) == "s/kit-3"
