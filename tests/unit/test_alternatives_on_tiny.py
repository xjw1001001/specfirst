"""Alternatives on data: a changed decision changes the values its statement speaks of.

Each case changes one or two decisions of the base vector, builds the tiny
study of `specfirst.compile.tiny` with yamaa and compares one value with
what the statement of the alternative says. The gate check "yamaa run"
shows that every alternative runs; these cases show, for the alternatives
the tiny study can tell apart, that it runs to the right value.
"""

from __future__ import annotations

import pyarrow.parquet as pq
import pytest

from specfirst.compile import catalog as catalog_module
from specfirst.compile import checks, tiny
from specfirst.compile import house as house_module
from specfirst.compile.compiler import compile_decisions, relative_reference

# The std-1 tests hold the frozen pair of version 1 (ADR-020: loadable by label).
V1 = ("catalog@1", "open-default@1")

WINDOWS = [{"visit": "Week 2", "target": 15, "low": 8, "high": 21},
           {"visit": "Week 4", "target": 29, "low": 22, "high": 42}]
VISITS = [{"visit": "Week 2", "target": 15}, {"visit": "Week 4", "target": 29}]

# (what the case shows, decisions changed, dataset, key of the row, column, expected value)
CASES = [
    ("the base: the first alternative of trt.start.source",
     {}, "ADSL", ("S1",), "TRTSDT", "2024-03-10"),
    ("a record with a partial start date does not void the start date",
     {}, "ADSL", ("S1",), "SAFFL", "Y"),
    ("a record with a partial end date does not void the end date",
     {}, "ADSL", ("S1",), "TRTEDT", "2024-04-20"),
    ("a partial start date completed with the first day of its month is the earliest",
     {"trt.date.imputation": {"rule": "first_day_of_month"}}, "ADSL", ("S1",), "TRTSDT",
     "2024-03-01"),
    ("a partial end date completed with the first day of its month is the latest",
     {"trt.date.imputation": {"rule": "first_day_of_month"}}, "ADSL", ("S1",), "TRTEDT",
     "2024-05-01"),
    ("the disposition date ends treatment when no dosed record has an end date: not here",
     {"trt.end.source": {"rule": "ds_date_when_ex_missing"}}, "ADSL", ("S1",), "TRTEDT",
     "2024-04-20"),
    ("dosed without being randomized: in the safety set by default",
     {}, "ADSL", ("S4",), "SAFFL", "Y"),
    ("dosed without being randomized: not in the safety set of randomized and dosed",
     {"pop.safety.rule": {"rule": "randomized_and_dosed"}}, "ADSL", ("S4",), "SAFFL", "N"),
    ("no exposure end date: no treatment end date by default",
     {}, "ADSL", ("S4",), "TRTEDT", None),
    ("no exposure end date: the disposition date ends treatment",
     {"trt.end.source": {"rule": "ds_date_when_ex_missing"}}, "ADSL", ("S4",), "TRTEDT",
     "2024-04-15"),
    ("the disposition date gives no treatment end to a subject who was never dosed",
     {"trt.end.source": {"rule": "ds_date_when_ex_missing"}}, "ADSL", ("S3",), "TRTEDT", None),
    ("an event that starts on the end-of-study date is still treatment-emergent",
     {"ae.teae.end": {"rule": "end_of_study"}}, "ADAE", ("S2", 2), "TRTEMFL", "Y"),
    ("an event that starts the day after the end-of-study date is not",
     {"ae.teae.end": {"rule": "end_of_study"}}, "ADAE", ("S2", 3), "TRTEMFL", None),
    ("two records one day from the target: the earlier one is analyzed",
     {"bds.window.table": {"rule": "protocol_windows", "windows": WINDOWS}},
     "ADVS", ("S1", "SYSBP", 11, ""), "ANL01FL", "Y"),
    ("two records one day from the target: the later one is not, by default",
     {"bds.window.table": {"rule": "protocol_windows", "windows": WINDOWS}},
     "ADVS", ("S1", "SYSBP", 6, ""), "ANL01FL", None),
    ("two records one day from the target: the later one, when the tie goes to the later",
     {"bds.window.table": {"rule": "protocol_windows", "windows": WINDOWS},
      "bds.window.tiebreak": {"rule": "closest_then_later"}},
     "ADVS", ("S1", "SYSBP", 6, ""), "ANL01FL", "Y"),
    ("DM.RFXSTDTC gives the treatment start date",
     {"trt.start.source": {"rule": "dm_rfxstdtc"}}, "ADSL", ("S2",), "TRTSDT", "2024-03-12"),
    ("the latest exposure start date ends treatment",
     {"trt.end.source": {"rule": "last_ex_start_date"}}, "ADSL", ("S1",), "TRTEDT", "2024-04-01"),
    ("planned treatment decoded from the arm code",
     {"trt.planned.source": {"rule": "dm_armcd_map", "map": [
         {"code": "LOW", "label": "Drug 10 mg"}, {"code": "PBO", "label": "Placebo"}]}},
     "ADSL", ("S1",), "TRT01P", "Drug 10 mg"),
    ("actual treatment from the first exposure record",
     {"trt.actual.source": {"rule": "first_ex_treatment"}}, "ADSL", ("S2",), "TRT01A", "PLACEBO"),
    ("study day 1 is the reference start date, two days before the first dose",
     {"date.studyday.origin": {"rule": "dm_rfstdtc"}}, "ADAE", ("S1", 2), "ASTDY", 3),
    ("two age groups: 65 is in the upper one",
     {"demo.age.groups": {"rule": "lt65_ge65"}}, "ADSL", ("S1",), "AGEGR1", ">=65"),
    ("stated cuts: an age equal to a cut starts the group",
     {"demo.age.groups": {"rule": "stated_cuts", "cuts": [65, 81]}},
     "ADSL", ("S3",), "AGEGR1", ">=81"),
    ("stated cuts: 80 is below the cut at 81",
     {"demo.age.groups": {"rule": "stated_cuts", "cuts": [65, 81]}},
     "ADSL", ("S2",), "AGEGR1", "65-<81"),
    ("a race with one subject is pooled when fewer than two are",
     {"demo.race.pooling": {"rule": "pooled_below_count", "count": 2}},
     "ADSL", ("S2",), "RACEGR1", "OTHER"),
    ("a race with two subjects is not pooled when fewer than two are",
     {"demo.race.pooling": {"rule": "pooled_below_count", "count": 2}},
     "ADSL", ("S1",), "RACEGR1", "WHITE"),
    ("baseline weight at the screening visit",
     {"demo.baseline.record": {"rule": "at_visit", "visit": "SCREENING"}},
     "ADSL", ("S1",), "WEIGHTBL", 70.0),
    ("efficacy-evaluable by an attended visit: attended",
     {"pop.efficacy.rule": {"rule": "attended_visit", "visit": "WEEK 4"}},
     "ADSL", ("S1",), "EFFFL", "Y"),
    ("efficacy-evaluable by an attended visit: not attended",
     {"pop.efficacy.rule": {"rule": "attended_visit", "visit": "WEEK 4"}},
     "ADSL", ("S2",), "EFFFL", "N"),
    ("randomized set with a post-baseline value: the undosed subject has none",
     {"pop.randomized.rule": {"rule": "randomized_with_postbaseline", "test": "SYSBP"}},
     "ADSL", ("S3",), "ITTFL", "N"),
    ("no disposition event of the named subcategory: the subject is ongoing",
     {"disp.status.record": {"rule": "disposition_event_by_subcategory",
                             "subcategory": "STUDY TREATMENT"}},
     "ADSL", ("S1",), "EOSSTT", "ONGOING"),
    ("first day of the month, before the first dose: not treatment-emergent",
     {"ae.start.imputation": {"rule": "first_of_month"}}, "ADAE", ("S2", 1), "TRTEMFL", None),
    ("first day of the month: the date itself",
     {"ae.start.imputation": {"rule": "first_of_month"}}, "ADAE", ("S2", 1), "ASTDT",
     "2024-03-01"),
    ("a partial date that is not completed has no start date and is treatment-emergent",
     {"ae.start.imputation": {"rule": "not_completed"}}, "ADAE", ("S2", 1), "TRTEMFL", "Y"),
    ("a start without a time on the first dose date is before a dose at 08:00",
     {"ae.teae.start": {"rule": "at_or_after_first_dose_time"}}, "ADAE", ("S1", 2), "TRTEMFL",
     None),
    ("the same start when the first dose has no time either: emergent",
     {"ae.teae.start": {"rule": "at_or_after_first_dose_time"},
      "ae.start.imputation": {"rule": "first_of_month_not_before_first_dose"}},
     "ADAE", ("S2", 1), "TRTEMFL", "Y"),
    ("35 days after the last dose is outside a window of 30 days",
     {"ae.teae.end": {"rule": "last_dose_plus_days", "days": 30}}, "ADAE", ("S1", 3), "TRTEMFL",
     None),
    ("35 days after the last dose is inside a window of 35 days",
     {"ae.teae.end": {"rule": "last_dose_plus_days", "days": 35}}, "ADAE", ("S1", 3), "TRTEMFL",
     "Y"),
    ("an event after the end-of-study date is not treatment-emergent",
     {"ae.teae.end": {"rule": "end_of_study"}}, "ADAE", ("S1", 3), "TRTEMFL", None),
    ("a causality outside the stated list is not related",
     {"ae.related.values": {"rule": "stated_list", "values": ["PROBABLE"]}},
     "ADAE", ("S1", 1), "RELGR1", "NOT RELATED"),
    ("on or before the treatment start date: the value after the dose is baseline",
     {"bds.baseline.rule": {"rule": "last_on_or_before_first_dose_date"}},
     "ADVS", ("S1", "SYSBP", 3, ""), "ABLFL", "Y"),
    ("baseline at a scheduled visit",
     {"bds.baseline.rule": {"rule": "scheduled_baseline_visit", "visit": "SCREENING"}},
     "ADVS", ("S1", "SYSBP", 1, ""), "ABLFL", "Y"),
    ("unscheduled records excluded: no baseline from an unscheduled visit",
     {"bds.unscheduled.use": {"rule": "excluded"}}, "ADVS", ("S2", "SYSBP", 1, ""), "ABLFL",
     None),
    ("protocol windows: day 17 of an unscheduled visit falls into Week 2",
     {"bds.window.table": {"rule": "protocol_windows", "windows": WINDOWS}},
     "ADVS", ("S1", "SYSBP", 5, ""), "AVISIT", "Week 2"),
    ("protocol windows: day 47 is in no window",
     {"bds.window.table": {"rule": "protocol_windows", "windows": WINDOWS}},
     "ADVS", ("S1", "SYSBP", 7, ""), "AVISIT", None),
    ("midpoint windows: day 47 belongs to the last visit",
     {"bds.window.table": {"rule": "midpoint_windows", "visits": VISITS}},
     "ADVS", ("S1", "SYSBP", 7, ""), "AVISIT", "Week 4"),
    ("closest to target: day 15 beats day 17 in Week 2",
     {"bds.window.table": {"rule": "protocol_windows", "windows": WINDOWS}},
     "ADVS", ("S1", "SYSBP", 4, ""), "ANL01FL", "Y"),
    ("the last record of the window is analyzed",
     {"bds.window.table": {"rule": "protocol_windows", "windows": WINDOWS},
      "bds.window.tiebreak": {"rule": "last_record"}},
     "ADVS", ("S1", "SYSBP", 5, ""), "ANL01FL", "Y"),
    ("midpoint windows: day 30 is closer to the Week 4 target than day 47",
     {"bds.window.table": {"rule": "midpoint_windows", "visits": VISITS},
      "bds.window.tiebreak": {"rule": "closest_then_later"}},
     "ADVS", ("S1", "SYSBP", 6, ""), "ANL01FL", "Y"),
]

KEYS = {"ADSL": ["USUBJID"], "ADAE": ["USUBJID", "AESEQ"],
        "ADVS": ["USUBJID", "PARAMCD", "VSSEQ", "DTYPE"]}


@pytest.fixture(scope="module")
def standard(root):
    catalog = catalog_module.load(catalog_module.default_dir(root, V1[0]))
    house = house_module.load(house_module.default_dir(root, V1[1]))
    return catalog, house, checks.base_vector(catalog, house)


@pytest.fixture(scope="module")
def build(standard, tmp_path_factory):
    """Compile and run a changed base vector once; return the rows of a dataset by key."""
    catalog, house, base = standard
    built: dict[str, dict] = {}

    def run(changes: dict) -> dict:
        label = repr(sorted(changes.items()))
        if label not in built:
            folder = tmp_path_factory.mktemp("tiny")
            tiny.write(folder / "sdtm")
            records = [{**r, "value": changes[r["id"]]} if r["id"] in changes else r
                       for r in base]
            compiled = compile_decisions(
                catalog, house, records,
                relative_reference(house.directory, folder / "spec" / "adam"),
                sdtm_dir="../../sdtm", adam_dir="../../adam")
            compiled.write(folder / "spec")
            (folder / "adam").mkdir()
            rows = {}
            for dataset in compiled.datasets:
                spec = folder / "spec" / "adam" / f"{dataset.lower()}.yaml"
                assert checks.yamaa_run(spec) == []
                table = pq.read_table(folder / "adam" / f"{dataset.lower()}.parquet")
                rows[dataset] = {tuple(row[k] for k in KEYS[dataset]): row
                                 for row in table.to_pylist()}
            built[label] = rows
        return built[label]

    return run


@pytest.mark.parametrize("what, changes, dataset, key, column, expected", CASES,
                         ids=[case[0] for case in CASES])
def test_alternative_gives_the_value_of_its_statement(build, what, changes, dataset, key,
                                                      column, expected):
    row = build(changes)[dataset][key]
    value = row[column]
    if expected is not None and not isinstance(expected, int | float):
        value = None if value is None else str(value)
    assert value == expected, what


def test_no_end_of_treatment_record_without_the_decision(build):
    with_record = build({})["ADVS"]
    without = build({"bds.eot.record": {"rule": "none"}})["ADVS"]
    assert [key for key in with_record if key[3] == "LOV"] == \
        [("S1", "SYSBP", 6, "LOV"), ("S2", "SYSBP", 2, "LOV")]
    assert [key for key in without if key[3] == "LOV"] == []
    assert len(without) == len(with_record) - 2
