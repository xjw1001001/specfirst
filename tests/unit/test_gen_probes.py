"""Probe recipes: planted in the twin, found again in the SDTM, and missed when undone.

Rule R5 for the check behind the gate: for every probe there is a planted
defect that undoes the probe in the data that were written. The check must
then say that the probe is not there.
"""

from __future__ import annotations

import copy
import datetime

import pytest

from specfirst.compile import catalog as catalogs
from specfirst.gen import design as designs
from specfirst.gen import pgfix, present, probes, sdtm, study

# One design with an efficacy set (every decision of the slice applies), one without.
SEEDS = ("probes-a", "probes-b", "probes-c", "probes-d")
DAY = datetime.timedelta(days=1)


@pytest.fixture(scope="module")
def catalog(root):
    return catalogs.load(catalogs.default_dir(root))


def _study(catalog, seed, which="twin", share=study.VISIBLE_SHARE):
    design = pgfix.sample(seed, study.catalog_label(catalog))
    people, log = study.simulate(design, catalog, seed, which, share)
    return design, people, log, sdtm.build(design, people)


@pytest.fixture(scope="module")
def studies(catalog):
    return {seed: _study(catalog, seed) for seed in SEEDS}


@pytest.fixture(scope="module")
def full(catalog):
    """A twin of a design in which every decision of the slice applies."""
    for number in range(50):
        seed = f"probes-full-{number}"
        design = pgfix.sample(seed, study.catalog_label(catalog))
        if designs.features(design)["design.has_efficacy_set"]:
            return _study(catalog, seed)
    raise AssertionError("no seed gives a design with an efficacy set")


def test_the_twin_carries_every_probe_of_the_slice(catalog, studies):
    for design, _, log, tables in studies.values():
        needed = probes.needed(catalog, design)
        assert [record["probe"] for record in log] == needed
        pairs, checked, problems = present.coverage(catalog, design, log, tables)
        assert problems == [] and checked == len(needed) and pairs >= 30
        assert all(record["data"] == "twin" for record in log)
        assert {record["catalog"] for record in log} == {study.catalog_label(catalog)}


def test_every_probe_of_the_slice_has_a_recipe_and_a_check(catalog):
    for seed in SEEDS:
        design = pgfix.sample(seed, study.catalog_label(catalog))
        for probe in probes.needed(catalog, design):
            kind = catalog.probes[probe]["kind"]
            assert probe in present.FINDERS, probe
            assert probe in probes.RECIPES or kind in probes.WITHOUT_DATA, probe


def test_the_visible_data_carry_a_sampled_part(catalog):
    counts = []
    for seed in SEEDS:
        design, _, twin, _ = _study(catalog, seed)
        _, _, visible, tables = _study(catalog, seed, "visible")
        twin_ids = [r["probe"] for r in twin]
        seen = [r["probe"] for r in visible]
        assert set(seen) < set(twin_ids)
        # What cannot be left out is there; what is logged is in the data.
        fixed = [p for p in twin_ids if p in probes.ALWAYS
                 or catalog.probes[p]["kind"] in probes.WITHOUT_DATA]
        assert set(fixed) <= set(seen)
        for record in visible:
            assert present.find(record, tables, design) == [], record["probe"]
        counts.append((len(seen) - len(fixed), len(twin_ids) - len(fixed)))
    sampled, possible = (sum(column) for column in zip(*counts, strict=True))
    assert 0.25 < sampled / possible < 0.75
    # A share of 0 plants nothing that can be left out; a share of 1 is the twin.
    _, _, none, _ = _study(catalog, SEEDS[0], "visible", share=0.0)
    assert all(r["probe"] in probes.ALWAYS or r["kind"] in probes.WITHOUT_DATA for r in none)


def test_a_planted_subject_never_enters_the_arm_of_the_count_probes(studies):
    for design, _, log, tables in studies.values():
        spared = probes.Parameters.of(design).spared_arm
        planted = {s for r in log for s in r["subjects"]}
        rows = {row["USUBJID"]: row for row in tables["DM"]}
        assert planted
        assert all(rows[s]["ACTARMCD"] != spared for s in planted)
        record = next(r for r in log if r["probe"] == "statistic_at_rounding_half")
        total = record["detail"]["subjects"]
        assert total == designs.arm(design, spared)["plannedNumber"] and total % 16 == 0
        assert record["detail"]["with_serious_event"] * 16 == total
        assert record["detail"]["percent"][1] == 6.25


@pytest.mark.parametrize("count, total, expected", [
    (1, 16, True), (2, 32, True), (5, 16, True), (9, 16, True), (13, 16, True), (3, 48, True),
    (1, 80, True), (3, 16, False), (1, 32, False), (4, 16, False), (1, 20, False),
    (0, 16, False), (1, 0, False),
])
def test_what_counts_as_a_rounding_half(count, total, expected):
    """A percentage that ends in .25: exact in binary, halfway at one decimal, even digit."""
    assert probes.is_rounding_half(count, total) is expected
    if expected:
        percent = 100 * count / total
        assert percent * 4 == int(percent * 4) and round(percent * 10 % 10, 6) in (2.5,)


# -- planted defects: undo each probe in the data ------------------------------


def _row(tables, domain, subject, **where):
    return next(r for r in tables[domain] if r["USUBJID"] == subject
                and all(r[key] == value for key, value in where.items()))


def _rows(tables, domain, subject):
    return [r for r in tables[domain] if r["USUBJID"] == subject]


def _drop(tables, domain, keep):
    tables[domain] = [row for row in tables[domain] if keep(row)]


def _first_dose(tables, subject):
    return datetime.date.fromisoformat(_row(tables, "DM", subject)["RFXSTDTC"][:10])


def _undo_actual(t, r, d):
    row = _row(t, "DM", r["subjects"][0])
    row["ACTARMCD"], row["ACTARM"] = row["ARMCD"], row["ARM"]


def _undo_first_other(t, r, d):
    rows = sorted(_rows(t, "EX", r["subjects"][0]), key=lambda x: x["EXSEQ"])
    rows[0]["EXTRT"] = rows[-1]["EXTRT"]


def _undo_zero_dose(t, r, d):
    for row in _rows(t, "EX", r["subjects"][0]):
        row["EXDOSE"] = row["EXDOSE"] or 5.0


def _undo_rfxstdtc(t, r, d):
    subject = r["subjects"][0]
    _row(t, "DM", subject)["RFXSTDTC"] = min(x["EXSTDTC"] for x in _rows(t, "EX", subject))


def _undo_spans(t, r, d):
    for row in t["EX"]:
        row["EXENDTC"] = row["EXSTDTC"][:10]


def _undo_no_end(t, r, d):
    for row in _rows(t, "EX", r["subjects"][0]):
        row["EXENDTC"] = row["EXSTDTC"][:10]


def _undo_partial_exposure(t, r, d):
    row = min(_rows(t, "EX", r["subjects"][0]), key=lambda x: x["EXSEQ"])
    row["EXSTDTC"] += "-02"


def _undo_partial_middle(t, r, d):
    for row in _rows(t, "EX", r["subjects"][0]):
        if len(row["EXSTDTC"]) == 7:
            row["EXSTDTC"] += "-05"


def _undo_reference(t, r, d):
    row = _row(t, "DM", r["subjects"][0])
    row["RFSTDTC"] = row["RFXSTDTC"][:10]


def _add_vital(t, subject, test, date):
    like = dict(_rows(t, "VS", subject)[-1])
    like.update(VSTESTCD=test, VSDTC=date.isoformat(), VSSEQ=like["VSSEQ"] + 1)
    t["VS"].append(like)


def _undo_without_postbaseline(t, r, d):
    subject = r["subjects"][0]
    _add_vital(t, subject, r["by_subject"][subject]["test"], _first_dose(t, subject) + 10 * DAY)


def _undo_not_randomized(t, r, d):
    row = _row(t, "DM", r["subjects"][0])
    row["ARMCD"] = row["ACTARMCD"]


def _undo_never_dosed(t, r, d):
    like = dict(t["EX"][0])
    like["USUBJID"] = r["subjects"][0]
    t["EX"].append(like)


def _undo_visit_missed(t, r, d):
    like = dict(_rows(t, "SV", r["subjects"][0])[0])
    like["VISIT"] = r["detail"]["visits"][0]
    t["SV"].append(like)


def _undo_other_test(t, r, d):
    subject = r["subjects"][0]
    _add_vital(t, subject, r["by_subject"][subject]["test_without_baseline"],
               _first_dose(t, subject) - 2 * DAY)


def _undo_two_dispositions(t, r, d):
    subject = r["subjects"][0]
    _drop(t, "DS", lambda row: not (row["USUBJID"] == subject
                                    and row["DSSCAT"] == "STUDY TREATMENT"))


def _undo_partial_ae(t, r, d):
    for row in _rows(t, "AE", r["subjects"][0]):
        if len(row["AESTDTC"]) == 7:
            row["AESTDTC"] += "-01"


def _undo_ongoing(t, r, d):
    for row in _rows(t, "AE", r["subjects"][0]):
        row["AEENDTC"] = "2030-01-01"


def _undo_dose_time(t, r, d):
    row = _row(t, "DM", r["subjects"][0])
    row["RFXSTDTC"] = row["RFXSTDTC"][:10]


def _undo_after_window(t, r, d):
    subject = r["subjects"][0]
    last = max(row["AESTDTC"] for row in _rows(t, "AE", subject))
    _drop(t, "AE", lambda row: not (row["USUBJID"] == subject and row["AESTDTC"] == last))


def _undo_events(t, r, d):
    subject = r["subjects"][0]
    _drop(t, "AE", lambda row: row["USUBJID"] != subject)


def _undo_causality(t, r, d):
    scale = d["collection"]["adverseEvents"]["causality"]
    subject = next(s for s, own in r["by_subject"].items() if own["value"] == scale[-1])
    for row in _rows(t, "AE", subject):
        row["AEREL"] = scale[0]


def _undo_without_any(t, r, d):
    subject = r["subjects"][0]
    _add_vital(t, subject, _rows(t, "VS", subject)[0]["VSTESTCD"],
               _first_dose(t, subject) + 20 * DAY)


def _undo_zero_count(t, r, d):
    arm = r["detail"]["arm"]
    members = {row["USUBJID"] for row in t["DM"] if row["ACTARMCD"] == arm}
    next(row for row in t["AE"] if row["USUBJID"] in members)["AESDTH"] = "Y"


def _undo_rounding(t, r, d):
    arm = r["detail"]["arm"]
    members = {row["USUBJID"] for row in t["DM"] if row["ACTARMCD"] == arm}
    serious = {row["USUBJID"] for row in t["AE"] if row["AESER"] == "Y"}
    dose = {row["USUBJID"]: row["RFXSTDTC"][:10] for row in t["DM"] if row["RFXSTDTC"]}
    row = next(row for row in t["AE"] if row["USUBJID"] in members - serious
               and row["AESTDTC"] > dose[row["USUBJID"]])
    row["AESER"] = "Y"


def _undo_arm_label(t, r, d):
    for row in t["DM"]:
        if row["ARMCD"]:
            row["ARM"] = designs.arm(d, row["ARMCD"])["label"]


def _undo_dose_order(t, r, d):
    arms = {arm["name"]: arm for arm in d["studyDesign"]["arms"]}
    d["studyDesign"]["arms"] = [arms[name] for name in designs.dose_order(d)]


UNDO = {
    "arms_listed_out_of_dose_order": _undo_dose_order,
    "arm_label_differs_from_decode": _undo_arm_label,
    "actual_arm_differs_from_planned": _undo_actual,
    "first_exposure_other_treatment": _undo_first_other,
    "zero_dose_record_before_first_dose": _undo_zero_dose,
    "rfxstdtc_differs_from_exposure": _undo_rfxstdtc,
    "last_exposure_record_spans_days": _undo_spans,
    "no_exposure_end_date": _undo_no_end,
    "partial_exposure_date": _undo_partial_exposure,
    "partial_exposure_date_not_earliest": _undo_partial_middle,
    "reference_start_before_first_dose": _undo_reference,
    "randomized_without_postbaseline_value": _undo_without_postbaseline,
    "dosed_but_not_randomized": _undo_not_randomized,
    "randomized_never_dosed": _undo_never_dosed,
    "postbaseline_value_but_visit_missed": _undo_visit_missed,
    "baseline_value_of_other_test_only": _undo_other_test,
    "two_disposition_events": _undo_two_dispositions,
    "partial_ae_start_in_month_of_first_dose": _undo_partial_ae,
    "partial_ae_start_before_month_of_first_dose": _undo_ongoing,
    "ae_on_first_dose_date_without_time": _undo_dose_time,
    "ae_starts_after_emergence_window": _undo_after_window,
    "ae_starts_after_end_of_study": _undo_events,
    "ae_between_window_end_and_end_of_study": _undo_events,
    "ae_with_each_causality_value": _undo_causality,
    "dosed_without_postbaseline_value": _undo_without_any,
    "category_with_zero_count": _undo_zero_count,
    "statistic_at_rounding_half": _undo_rounding,
}


def test_there_is_a_planted_defect_for_every_probe_with_data(catalog, full):
    design, _, log, _ = full
    with_data = [r["probe"] for r in log if r["kind"] != "structural"]
    assert sorted(with_data) == sorted(UNDO)


@pytest.mark.parametrize("probe", sorted(UNDO))
def test_a_probe_that_is_undone_in_the_data_is_missed(catalog, full, probe):
    design, _, log, tables = full
    record = next(r for r in log if r["probe"] == probe)
    assert present.find(record, tables, design) == []
    broken, changed = copy.deepcopy(tables), copy.deepcopy(design)
    UNDO[probe](broken, record, changed)
    problems = present.find(record, broken, changed)
    assert problems, f"the check still finds {probe} after it was undone"
    # The gate check reports it, too: the pairs of the probe lose their only witness,
    # unless another probe separates the same pair.
    _, _, missing = present.coverage(catalog, changed, log, broken)
    assert any(line.startswith(f"probe {probe}:") for line in missing)


def test_a_pair_without_any_probe_is_reported(catalog, full):
    design, _, log, tables = full
    shorter = [r for r in log if r["probe"] != "reference_start_before_first_dose"]
    _, _, problems = present.coverage(catalog, design, shorter, tables)
    assert problems == ["date.studyday.origin: no probe in the twin separates treatment_start "
                        "from dm_rfstdtc"]
    # A probe of the visible data does not count for the twin.
    moved = [dict(r, data="visible") if r["probe"] == "two_disposition_events" else r
             for r in log]
    _, _, problems = present.coverage(catalog, design, moved, tables)
    assert any("disp.status.record" in problem for problem in problems)


def test_a_log_line_alone_proves_nothing(catalog, full):
    """A probe that is logged for a subject who does not show it is not there."""
    design, _, log, tables = full
    record = copy.deepcopy(next(r for r in log if r["probe"] == "randomized_never_dosed"))
    other = next(row["USUBJID"] for row in tables["EX"])
    record["subjects"] = [other]
    assert present.find(record, tables, design) == [f"{other}: an exposure record"]
    record["subjects"] = []
    assert present.find(record, tables, design) == ["the log names no subject"]
    record["subjects"] = ["no-such-subject"]
    assert "cannot be read" in present.find(record, tables, design)[0]
    assert "no check" in present.find({"probe": "unknown_probe"}, tables, design)[0]


def test_the_log_gives_what_a_decision_sampler_needs(catalog, full):
    design, _, log, _ = full
    for record in log:
        assert set(record) >= {"catalog", "generator", "study", "data", "probe", "kind", "where",
                               "domains", "separates", "varies", "stresses", "subjects",
                               "detail", "parameters"}
        assert record["parameters"]["window_days"] == designs.follow_up_days(design)
        for entry_id, pairs in record["separates"].items():
            ids = {a.id for a in catalog.entry(entry_id).alternatives}
            # An entry with one alternative has no pair; its probe varies a slot.
            assert pairs or len(ids) == 1
            assert all(len(pair) == 2 and set(pair) <= ids for pair in pairs)
    window = next(r for r in log if r["probe"] == "ae_starts_after_emergence_window")
    assert window["detail"]["window_days"] == designs.follow_up_days(design)
    assert window["varies"] == {"ae.teae.end": ["days"]}
