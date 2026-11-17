"""The design model and the sampler of the archetype PG-FIX (PLAN.md section 6.2)."""

from __future__ import annotations

import copy

import pytest

from specfirst.compile import catalog as catalogs
from specfirst.compile import predicate
from specfirst.gen import design as designs
from specfirst.gen import pgfix, probes, study

SEEDS = [f"test-{number}" for number in range(40)]


@pytest.fixture(scope="module")
def catalog(root):
    return catalogs.load(catalogs.default_dir(root))


@pytest.fixture(scope="module")
def sampled(catalog):
    return [pgfix.sample(seed, study.catalog_label(catalog)) for seed in SEEDS]


def test_every_sampled_design_is_usable_and_is_the_preset(sampled):
    for design in sampled:
        assert designs.problems(design) == []
        assert design["archetype"] == "PG-FIX"
        body = design["studyDesign"]
        assert body["model"] == "PARALLEL" and body["randomization"]
        placebo = [a for a in body["arms"] if designs.is_placebo(design, a["name"])]
        assert len(placebo) == 1 and placebo[0]["dose"] == 0
        assert 2 <= len(body["arms"]) <= 4
        assert [e["name"] for e in body["epochs"]] == list(designs.EPOCHS)
        days = [e["plannedDay"] for e in designs.encounters(design)]
        assert days == sorted(days) and 1 in days and 0 not in days
        assert all(e["windowLower"] >= 0 and e["windowUpper"] >= 0
                   for e in designs.encounters(design))


def test_the_sampler_is_a_function_of_the_seed(catalog):
    label = study.catalog_label(catalog)
    assert pgfix.sample("x", label) == pgfix.sample("x", label)
    assert pgfix.sample("x", label) != pgfix.sample("y", label)
    design = pgfix.sample("x", label)
    assert designs.dump(design) == designs.dump(copy.deepcopy(design))
    assert design["catalog"] == label  # named in everything generated


def test_the_sampler_uses_its_ranges(sampled):
    ranges = pgfix.RANGES
    seen = {"arms": set(), "weeks": set(), "follow": set(), "efficacy": set(), "scale": set()}
    for design in sampled:
        body = design["studyDesign"]
        active = len(body["arms"]) - 1
        assert ranges["active_arms"][0] <= active <= ranges["active_arms"][1]
        seen["arms"].add(active)
        weeks = designs.treatment_days(design) // 7
        assert weeks in ranges["treatment_weeks"]
        seen["weeks"].add(weeks)
        assert designs.follow_up_days(design) in ranges["follow_up_days"]
        seen["follow"].add(designs.follow_up_days(design))
        seen["efficacy"].add(designs.features(design)["design.has_efficacy_set"])
        seen["scale"].add(len(design["collection"]["adverseEvents"]["causality"]))
        assert ranges["sites"][0] <= len(design["sites"]) <= ranges["sites"][1]
    assert seen["arms"] == {1, 2, 3} and len(seen["weeks"]) >= 3 and len(seen["follow"]) >= 3
    assert seen["efficacy"] == {True, False} and seen["scale"] == {2, 4, 5}


def test_two_properties_exist_for_the_probes(sampled):
    """Arms out of dose order, and arm sizes that are multiples of 16 (see pgfix)."""
    for design in sampled:
        listed = [arm["name"] for arm in designs.arms(design)]
        assert listed != designs.dose_order(design)
        assert designs.dose_order(design)[0] == "PBO"
        doses = [designs.arm(design, name)["dose"] for name in designs.dose_order(design)]
        assert doses == sorted(doses)
        for arm in designs.arms(design):
            assert arm["plannedNumber"] % 16 == 0
            assert arm["description"] != arm["label"] or arm["name"] == "PBO"
        total = sum(arm["plannedNumber"] for arm in designs.arms(design))
        assert total % design["studyDesign"]["randomization"]["blockSize"] == 0


def test_features_answer_every_predicate_of_the_catalog(catalog, sampled):
    for design in sampled[:5]:
        features = designs.features(design)
        assert set(features) == set(catalog.design_features)
        for entry in catalog.entries.values():
            predicate.evaluate(predicate.parse(entry.applies_when), features)
    entries = {e.id for e in probes.slice_entries(catalog, sampled[0])}
    assert {"trt.start.source", "pop.safety.rule", "ae.teae.end", "tfl.ae.summary.rows",
            "tfl.rounding.rule"} <= entries
    assert "bds.baseline.rule" not in entries and "tfl.demog.rows" not in entries


def test_the_efficacy_decision_applies_only_with_an_efficacy_set(catalog, sampled):
    with_set = next(d for d in sampled if designs.features(d)["design.has_efficacy_set"])
    without = next(d for d in sampled if not designs.features(d)["design.has_efficacy_set"])
    assert "pop.efficacy.rule" in {e.id for e in probes.slice_entries(catalog, with_set)}
    assert "pop.efficacy.rule" not in {e.id for e in probes.slice_entries(catalog, without)}


@pytest.mark.parametrize("change, expected", [
    (lambda d: d.update(design=2), "'design' must be 1"),
    (lambda d: d["studyDesign"]["arms"].append(dict(d["studyDesign"]["arms"][0])),
     "arm names must differ"),
    (lambda d: d["studyDesign"]["arms"][0].update(studyInterventionId="NONE"),
     "unknown intervention"),
    (lambda d: d["studyDesign"]["arms"][0].update(plannedNumber=0), "plannedNumber"),
    (lambda d: d["studyDesign"]["encounters"][2].update(plannedDay=0), "no study day 0"),
    (lambda d: d["studyDesign"]["encounters"][1].update(plannedDay=2), "study day 1"),
    (lambda d: d["studyDesign"]["randomization"].update(allocationRatio=[1]),
     "allocationRatio"),
    (lambda d: d["studyDesign"]["analysisPopulations"].append({"name": "PK"}),
     "unknown analysis population"),
    (lambda d: d.pop("process"), "'process' is missing"),
])
def test_a_planted_defect_in_a_design_is_reported(sampled, change, expected):
    design = copy.deepcopy(sampled[0])
    change(design)
    assert any(expected in problem for problem in designs.problems(design))


def test_a_design_file_round_trips(sampled, tmp_path):
    path = tmp_path / "design.yaml"
    path.write_text(designs.dump(sampled[0]), encoding="ascii", newline="\n")
    assert designs.load(path) == sampled[0]
    path.write_text("design: 1\n", encoding="ascii")
    with pytest.raises(designs.DesignError):
        designs.load(path)
