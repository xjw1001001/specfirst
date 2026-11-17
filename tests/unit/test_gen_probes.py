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
    # The house default reads the time of the first dose from the exposure record.
    row = min(_rows(t, "EX", r["subjects"][0]), key=lambda x: x["EXSEQ"])
    row["EXSTDTC"] = row["EXSTDTC"][:10]


def _undo_after_window(t, r, d):
    # The subject whose event starts the day after the window loses it.
    subject = max(r["by_subject"], key=lambda s: r["by_subject"][s]["days_after_last_dose"])
    _drop(t, "AE", lambda row: row["USUBJID"] != subject)


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
    assert problems == [
        "probe reference_start_before_first_dose: the twin does not carry it",
        "date.studyday.origin: no probe in the twin separates treatment_start from dm_rfstdtc"]
    # A probe of the visible data does not count for the twin.
    moved = [dict(r, data="visible") if r["probe"] == "two_disposition_events" else r
             for r in log]
    _, _, problems = present.coverage(catalog, design, moved, tables)
    assert any("disp.status.record" in problem for problem in problems)


def test_the_twin_must_carry_every_probe_even_one_that_separates_no_pair(catalog, full):
    """Review finding F11: a probe that only varies a slot was free to be missing."""
    design, _, log, tables = full
    for probe in ("ae_with_each_causality_value", "baseline_value_of_other_test_only",
                  "partial_exposure_date_not_earliest"):
        shorter = [r for r in log if r["probe"] != probe]
        _, checked, problems = present.coverage(catalog, design, shorter, tables)
        assert problems == [f"probe {probe}: the twin does not carry it"]
        assert checked == len(log) - 1
    # The visible data carry a sampled part: there a missing probe is no problem by itself.
    visible = [dict(r, data="visible") for r in log if r["probe"] != "two_disposition_events"]
    _, _, problems = present.coverage(catalog, design, visible, tables, "visible")
    assert not any("does not carry" in line for line in problems)


def test_which_pairs_a_probe_separates_comes_from_the_catalog(catalog, full):
    """Review finding F10: the log is what is checked, so its own claims do not count."""
    design, _, log, tables = full
    moved = []
    for record in log:
        record = copy.deepcopy(record)
        if record["probe"] == "two_disposition_events":
            continue
        if record["probe"] == "output_shape":  # a probe whose check finds nothing to miss
            record["separates"]["disp.status.record"] = [
                ["disposition_event", "disposition_event_by_subcategory"]]
        moved.append(record)
    _, _, problems = present.coverage(catalog, design, moved, tables)
    assert "probe output_shape: the log claims other pairs than the catalog gives" in problems
    assert any(line.startswith("disp.status.record: no probe in the twin separates")
               for line in problems)
    twice = [*log, log[0]]
    assert any("logged 2 times" in line for line in
               present.coverage(catalog, design, twice, tables)[2])
    unknown = [*log, dict(log[0], probe="no_such_probe")]
    assert "probe no_such_probe: not a probe of the catalog" in present.coverage(
        catalog, design, unknown, tables)[2]


def test_a_design_without_an_efficacy_set_has_no_pair_with_that_set(catalog, studies):
    """Review finding F7: a table on the efficacy-evaluable set cannot be built there."""
    entry = catalog.entry("tfl.population")
    for design, _, log, _ in studies.values():
        has_set = designs.features(design)["design.has_efficacy_set"]
        pairs = probes.pairs_of(entry, design)
        assert (("safety", "efficacy") in pairs) is has_set
        assert ("safety", "randomized") in pairs
        record = next(r for r in log if r["probe"] == "dosed_without_postbaseline_value")
        claimed = record["separates"]["tfl.population"]
        assert claimed == ([["safety", "efficacy"], ["randomized", "efficacy"]] if has_set
                           else [])


def _counts(tables, flag, arm_variable):
    """Subjects per arm of an analysis set, as the header of a table counts them."""
    counts: dict[str, int] = {}
    dosed = {row["USUBJID"] for row in tables["EX"]}
    for row in tables["DM"]:
        inside = row["USUBJID"] in dosed if flag == "safety" else bool(row["ARMCD"])
        if inside and row[arm_variable]:
            counts[row[arm_variable]] = counts.get(row[arm_variable], 0) + 1
    return counts


def test_the_safety_set_and_the_randomized_set_never_count_the_same(catalog):
    """Review finding F3: three planted subjects cancelled in one twin in four.

    The table on the safety set counts by actual arm, the table on the
    randomized set by planned arm. With the arms of the planted subjects
    drawn freely the two tables had the same count in every column in 18 of
    150 twins. Here: 60 designs with three or four arms.
    """
    checked = 0
    for number in range(400):
        seed = f"cancel-{number}"
        design = pgfix.sample(seed, study.catalog_label(catalog))
        if len(designs.arms(design)) < 3:
            continue
        people, _ = study.simulate(design, catalog, seed, "twin")
        tables = sdtm.build(design, people, ("DM", "EX"))
        assert _counts(tables, "safety", "ACTARMCD") != _counts(tables, "randomized", "ARMCD"), \
            seed
        checked += 1
        if checked == 60:
            break
    assert checked == 60


def test_a_log_line_says_when_its_difference_reaches_the_output(catalog, full):
    """Review findings F5, F8 and F22: what a probe separates may need other decisions."""
    design, _, log, _ = full
    assert set(probes.REACHES) == {e.id for e in probes.slice_entries(catalog, design)}
    for record in log:
        served = [*record["separates"], *record["varies"], *record["stresses"]]
        assert set(record["reaches"]) == set(served) & set(probes.REACHES)
        for entry_id, reach in record["reaches"].items():
            assert reach == probes.REACHES[entry_id] and "when" in reach
    by_probe = {r["probe"]: r for r in log}
    half = by_probe["statistic_at_rounding_half"]["detail"]["assumes"]
    assert half["trt.actual.source"] == "dm_actarm" and "tfl.ae.summary.rows" in half
    assert "FATAL" in by_probe["category_with_zero_count"]["detail"]["assumes"][
        "tfl.ae.summary.rows"]
    parameters = log[0]["parameters"]
    assert parameters["treatment_subcategory"] == "STUDY TREATMENT"
    assert parameters["study_subcategory"] == "STUDY PARTICIPATION"


def _reach(entry_id, first, second, parameters, **changed):
    """`probes.reaches` for the house defaults with some decisions changed."""
    values = {"tfl.population": {"rule": "safety"}, "pop.safety.grouping": {"rule": "actual"},
              "trt.actual.source": {"rule": "dm_actarm"}, "ae.teae.end": {"rule": "no_end"},
              "ae.teae.start": {"rule": "on_or_after_first_dose_date"},
              "trt.end.source": {"rule": "last_ex_end_date"},
              "disp.status.record": {"rule": "disposition_event"},
              "tfl.ae.summary.rows": {"rule": "standard_rows"}}
    values.update({name.replace("__", "."): value for name, value in changed.items()})
    return probes.reaches(entry_id, first, second, values, parameters)


def test_reaches_is_evaluated_on_a_decision_vector(catalog, full):
    """Review finding F22: the rows, the length of the window, and two interplays."""
    design, _, log, _ = full
    parameters = log[0]["parameters"]
    days = parameters["window_days"]
    window = {"rule": "last_dose_plus_days", "days": days}
    rows = {"rule": "stated_rows", "rows": ["RELATED", "FATAL"]}
    # At the house defaults: what the report of gen-1a says.
    assert _reach("trt.start.source", "first_ex_with_dose", "first_ex_record", parameters)
    assert not _reach("date.studyday.origin", "treatment_start", "dm_rfstdtc", parameters)
    assert not _reach("pop.randomized.rule", "all_randomized", "randomized_with_postbaseline",
                      parameters)
    assert _reach("pop.randomized.rule", "all_randomized", "randomized_with_postbaseline",
                  parameters, tfl__population={"rule": "randomized"})
    # A decision that acts through one mild event needs the row ANY.
    for entry_id, pair in (("trt.start.source", ("first_ex_with_dose", "dm_rfxstdtc")),
                           ("trt.date.imputation", ("not_completed", "first_day_of_month")),
                           ("ae.start.imputation", ("first_of_month", "not_completed")),
                           ("ae.teae.start", ("on_or_after_first_dose_date",
                                              "at_or_after_first_dose_time"))):
        assert _reach(entry_id, *pair, parameters)
        assert not _reach(entry_id, *pair, parameters, tfl__ae__summary__rows=rows)
    assert _reach("ae.related.values", "stated_list", "stated_list", parameters,
                  tfl__ae__summary__rows=rows)
    # The treatment end date is read by a window of exactly the planted length.
    pair = ("last_ex_end_date", "ds_date_when_ex_missing")
    assert not _reach("trt.end.source", *pair, parameters)
    assert _reach("trt.end.source", *pair, parameters, ae__teae__end=window)
    for other in (days + 2, days - 1):
        assert not _reach("trt.end.source", *pair, parameters,
                          ae__teae__end={"rule": "last_dose_plus_days", "days": other})
    # The two interplays.
    pair = ("first_of_month_not_before_first_dose", "first_of_month")
    by_time = {"rule": "at_or_after_first_dose_time"}
    assert _reach("ae.start.imputation", *pair, parameters)
    assert _reach("ae.start.imputation", *reversed(pair), parameters)
    assert not _reach("ae.start.imputation", *pair, parameters, ae__teae__start=by_time)
    assert _reach("ae.start.imputation", "first_of_month", "not_completed", parameters,
                  ae__teae__start=by_time)
    treatment = {"rule": "disposition_event_by_subcategory",
                 "subcategory": parameters["treatment_subcategory"]}
    study = {**treatment, "subcategory": parameters["study_subcategory"]}
    assert _reach("ae.teae.end", "no_end", "end_of_study", parameters)
    assert not _reach("ae.teae.end", "no_end", "end_of_study", parameters,
                      disp__status__record=treatment)
    assert _reach("ae.teae.end", "no_end", "end_of_study", parameters,
                  disp__status__record=study)
    assert _reach("ae.teae.end", "no_end", "last_dose_plus_days", parameters,
                  disp__status__record=treatment)
    # The table reads actual treatment on the safety set grouped by it, planned otherwise.
    planned = {"rule": "planned"}
    pair = ("dm_actarm", "first_ex_treatment")
    assert _reach("trt.actual.source", *pair, parameters)
    assert not _reach("trt.actual.source", *pair, parameters, pop__safety__grouping=planned)
    assert not _reach("trt.planned.source", "dm_arm", "dm_armcd_map", parameters)
    assert _reach("trt.planned.source", "dm_arm", "dm_armcd_map", parameters,
                  pop__safety__grouping=planned)
    # A line of the log carries the same table: a reader of the log needs no code.
    record = next(r for r in log if "ae.teae.end" in r["reaches"])
    values = {"ae.teae.end": {"rule": "no_end"}, "disp.status.record": treatment}
    assert probes.reaches("ae.teae.end", "no_end", "end_of_study", values, parameters,
                          record["reaches"]) is False
    with pytest.raises(ValueError, match="not a condition"):
        probes.holds({"sometimes": True}, {}, parameters)


# What an alternative needs besides the pattern (review finding F9): each case changes the
# twin so that the pattern is still there and the two alternatives no longer differ.
def _f9_dose_time_in_dm_only(t, r, d):
    row = _row(t, "DM", r["subjects"][0])
    row["RFXSTDTC"] = row["RFXSTDTC"][:10]


def _f9_no_dose(t, r, d):
    for row in _rows(t, "EX", r["subjects"][0]):
        row["EXDOSE"] = 0.0


def _f9_placebo_on_day_one(t, r, d):
    rows = sorted(_rows(t, "EX", r["subjects"][0]), key=lambda x: x["EXSEQ"])
    like = dict(rows[0])
    like.update(EXTRT="PLACEBO", EXDOSE=0.0, EXSEQ=rows[-1]["EXSEQ"] + 1)
    t["EX"].append(like)


def _f9_event_over_before_the_dose(t, r, d):
    subject = r["subjects"][0]
    for row in _rows(t, "AE", subject):
        row["AEENDTC"] = _row(t, "DM", subject)["RFXSTDTC"][:8] + "01"


def _f9_no_event(t, r, d):
    _drop(t, "AE", lambda row: row["USUBJID"] != r["subjects"][0])


def _f9_late_event_not_serious(t, r, d):
    for row in _rows(t, "AE", r["subjects"][0]):
        row["AESER"] = "N"


def _f9_one_more_serious_on_day_one(t, r, d):
    arm = r["detail"]["arm"]
    members = [row for row in t["DM"] if row["ACTARMCD"] == arm and row["RFXSTDTC"]]
    serious = {row["USUBJID"] for row in t["AE"] if row["AESER"] == "Y"}
    dm = next(row for row in members if row["USUBJID"] not in serious)
    like = dict(t["AE"][0])
    like.update(USUBJID=dm["USUBJID"], AESEQ=99, AESER="Y", AESTDTC=dm["RFXSTDTC"][:10],
                AEENDTC=None)
    t["AE"].append(like)


F9 = [
    ("ae_on_first_dose_date_without_time", _f9_dose_time_in_dm_only),
    ("no_exposure_end_date", _f9_no_dose),
    ("dosed_but_not_randomized", _f9_no_dose),
    ("zero_dose_record_before_first_dose", _f9_placebo_on_day_one),
    ("partial_ae_start_in_month_of_first_dose", _f9_event_over_before_the_dose),
    ("zero_dose_record_before_first_dose", _f9_no_event),
    ("rfxstdtc_differs_from_exposure", _f9_no_event),
    ("partial_exposure_date", _f9_no_event),
    ("no_exposure_end_date", _f9_no_event),
    ("no_exposure_end_date", _f9_late_event_not_serious),
    ("reference_start_before_first_dose", _f9_no_event),
    ("statistic_at_rounding_half", _f9_one_more_serious_on_day_one),
]


@pytest.mark.parametrize("probe, change", F9, ids=[f"{p}-{c.__name__[4:]}" for p, c in F9])
def test_a_pattern_that_no_longer_separates_is_missed(catalog, full, probe, change):
    design, _, log, tables = full
    record = next(r for r in log if r["probe"] == probe)
    assert present.find(record, tables, design) == []
    broken = copy.deepcopy(tables)
    change(broken, record, design)
    assert present.find(record, broken, design), f"{probe} is still found"


def test_no_other_planted_subject_has_a_serious_event(catalog, studies):
    """The subject without an exposure end date changes a count that no other probe does."""
    for design, people, log, _ in studies.values():
        serious = sorted({probe for s in people if s.probes and any(e.serious for e in s.events)
                          for probe in s.probes})
        assert serious == ["no_exposure_end_date"]
        record = next(r for r in log if r["probe"] == "no_exposure_end_date")
        assert record["detail"]["event_serious"] is True
        # Never in the arm whose counts are calibrated for the rounding probe.
        spared = probes.Parameters.of(design).spared_arm
        assert all(s.actual_arm != spared for s in people if s.probes and s.events)


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
