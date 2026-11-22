"""The hand calculation of the adverse event summary (specfirst.gen.reference).

The reference is what a build of a generated study is held against (P2), so
it is tested on a study small enough to be counted on paper: five subjects,
written out below, with the expected table of every case worked out by hand
from the statements of the catalog. Nothing of the machine takes part.
"""

from __future__ import annotations

import datetime
from fractions import Fraction

import pytest

from specfirst.gen import reference
from specfirst.gen.reference import Arm

Date = datetime.date

# P1  placebo, dosed from 2024-03-10 08:00 to 2024-04-20; a mild event on the day of the
#     first dose, collected without a time
# L1  low dose, dosed from 2024-03-12 to 2024-04-30; a related event collected as
#     "2024-03", a serious event 41 days after the last dose (2024-06-10), and an event
#     that ended before the first dose
# L2  randomized to low dose and never dosed; one event
# N1  dosed with the low dose without being randomized; the exposure record has no end
#     date; a fatal event on 2024-03-25
# H1  randomized to high dose, dosed with the low dose: first three days a record with
#     dose 0, then the low dose from 2024-03-18; an event on 2024-03-16
DM = [
    {"USUBJID": "P1", "ARMCD": "PBO", "ARM": "Placebo", "ACTARM": "Placebo",
     "RFXSTDTC": "2024-03-10T08:00"},
    {"USUBJID": "L1", "ARMCD": "LOW", "ARM": "Drug 10 mg", "ACTARM": "Drug 10 mg",
     "RFXSTDTC": "2024-03-12"},
    {"USUBJID": "L2", "ARMCD": "LOW", "ARM": "Drug 10 mg", "ACTARM": None, "RFXSTDTC": None},
    {"USUBJID": "N1", "ARMCD": None, "ARM": None, "ACTARM": "Drug 10 mg",
     "RFXSTDTC": "2024-03-20"},
    {"USUBJID": "H1", "ARMCD": "HIGH", "ARM": "Drug 20 mg", "ACTARM": "Drug 10 mg",
     "RFXSTDTC": "2024-03-15"},
]
EX = [
    {"USUBJID": "P1", "EXSEQ": 1, "EXTRT": "PLACEBO", "EXDOSE": 0.0,
     "EXSTDTC": "2024-03-10T08:00", "EXENDTC": "2024-04-20"},
    {"USUBJID": "L1", "EXSEQ": 1, "EXTRT": "DRUG", "EXDOSE": 10.0, "EXSTDTC": "2024-03-12",
     "EXENDTC": "2024-04-30"},
    {"USUBJID": "N1", "EXSEQ": 1, "EXTRT": "DRUG", "EXDOSE": 10.0, "EXSTDTC": "2024-03-20",
     "EXENDTC": None},
    {"USUBJID": "H1", "EXSEQ": 1, "EXTRT": "DRUG", "EXDOSE": 0.0, "EXSTDTC": "2024-03-15",
     "EXENDTC": "2024-03-17"},
    {"USUBJID": "H1", "EXSEQ": 2, "EXTRT": "DRUG", "EXDOSE": 10.0, "EXSTDTC": "2024-03-18",
     "EXENDTC": "2024-04-25"},
]


def _event(subject, seq, start, end=None, serious="N", related="NONE", action="DOSE NOT CHANGED",
           death="N"):
    return {"USUBJID": subject, "AESEQ": seq, "AESTDTC": start, "AEENDTC": end, "AESER": serious,
            "AEREL": related, "AEACN": action, "AESDTH": death}


AE = [
    _event("P1", 1, "2024-03-10", "2024-03-12"),
    _event("L1", 1, "2024-03-01", "2024-03-05"),
    _event("L1", 2, "2024-03", None, related="POSSIBLE"),
    _event("L1", 3, "2024-06-10", None, serious="Y"),
    _event("L2", 1, "2024-03-14", None),
    _event("N1", 1, "2024-03-25", "2024-03-27", serious="Y", death="Y", action="DRUG WITHDRAWN"),
    _event("H1", 1, "2024-03-16", "2024-03-16"),
]
DS = [
    {"USUBJID": "P1", "DSSEQ": 1, "DSCAT": "DISPOSITION EVENT", "DSSCAT": "STUDY PARTICIPATION",
     "DSSTDTC": "2024-05-04"},
    {"USUBJID": "L1", "DSSEQ": 1, "DSCAT": "PROTOCOL MILESTONE", "DSSCAT": None,
     "DSSTDTC": "2024-03-12"},
    {"USUBJID": "L1", "DSSEQ": 2, "DSCAT": "DISPOSITION EVENT", "DSSCAT": "STUDY TREATMENT",
     "DSSTDTC": "2024-04-30"},
    {"USUBJID": "L1", "DSSEQ": 3, "DSCAT": "DISPOSITION EVENT", "DSSCAT": "STUDY PARTICIPATION",
     "DSSTDTC": "2024-05-14"},
    {"USUBJID": "N1", "DSSEQ": 1, "DSCAT": "DISPOSITION EVENT", "DSSCAT": "STUDY PARTICIPATION",
     "DSSTDTC": "2024-03-27"},
    {"USUBJID": "H1", "DSSEQ": 1, "DSCAT": "DISPOSITION EVENT", "DSSCAT": "STUDY PARTICIPATION",
     "DSSTDTC": "2024-05-09"},
]


def _vital(subject, date, test="SYSBP", value=120.0):
    return {"USUBJID": subject, "VSTESTCD": test, "VSSTRESN": value, "VSDTC": date}


VS = [
    _vital("P1", "2024-03-10"), _vital("P1", "2024-03-24"),
    _vital("L1", "2024-03-12"), _vital("L1", "2024-03-12", "WEIGHT"),
    _vital("L1", "2024-03-26", "WEIGHT"),
    _vital("N1", "2024-03-19"), _vital("N1", "2024-03-24"),
    _vital("H1", "2024-03-14"), _vital("H1", "2024-03-29", value=None),
]
SV = [{"USUBJID": "P1", "VISIT": "WEEK 2"}, {"USUBJID": "L1", "VISIT": "WEEK 2"},
      {"USUBJID": "H1", "VISIT": "BASELINE"}]
TABLES = {"DM": DM, "EX": EX, "AE": AE, "DS": DS, "VS": VS, "SV": SV}
# The protocol lists the arms as high, low, placebo.
ARMS = [Arm("HIGH", 20.0, ("Drug 20 mg", "DRUG", "High")),
        Arm("LOW", 10.0, ("Drug 10 mg", "DRUG", "Low")),
        Arm("PBO", 0.0, ("Placebo", "PLACEBO"))]
# The house defaults of open-default@1, the vector the cases below were worked out for.
# Every value is an alternative of catalog@2 as well (tfl.percent.format with its slot);
# open-default@2 takes four others (`HOUSE_2`).
HOUSE = {
    "trt.planned.source": {"rule": "dm_arm"}, "trt.actual.source": {"rule": "dm_actarm"},
    "trt.start.source": {"rule": "first_ex_with_dose"},
    "trt.end.source": {"rule": "last_ex_end_date"},
    "trt.date.imputation": {"rule": "not_completed"},
    "pop.randomized.rule": {"rule": "all_randomized"},
    "pop.safety.rule": {"rule": "at_least_one_dose"}, "pop.safety.grouping": {"rule": "actual"},
    "disp.status.record": {"rule": "disposition_event"},
    "ae.start.imputation": {"rule": "first_of_month_not_before_first_dose"},
    "ae.teae.start": {"rule": "on_or_after_first_dose_date"}, "ae.teae.end": {"rule": "no_end"},
    "ae.related.values": {"rule": "stated_list", "values": ["POSSIBLE", "PROBABLE"]},
    "tfl.output.include": {"rule": "included"}, "tfl.population": {"rule": "safety"},
    "tfl.columns.arms": {"rule": "ascending_dose_placebo_first"},
    "tfl.columns.total": {"rule": "all_arms"},
    "tfl.percent.format": {"rule": "one_decimal_zero_blank", "decimals": 1},
    "tfl.rounding.rule": {"rule": "half_away_from_zero"},
    "tfl.ae.summary.rows": {"rule": "standard_rows"},
}
# The defaults of open-default@2 for a randomized design (ADR-020, question 2).
HOUSE_2 = {
    **HOUSE,
    "pop.safety.rule": {"rule": "randomized_and_dosed"},
    "ae.teae.end": {"rule": "last_dose_plus_days", "days": 30},
    "tfl.columns.total": {"rule": "none"},
    "tfl.percent.format": {"rule": "one_decimal_always", "decimals": 1},
}


def _table(**changed):
    values = {**HOUSE, **{name.replace("__", "."): value for name, value in changed.items()}}
    return reference.table(TABLES, values, ARMS)


def _row(found, label):
    return dict(zip(found.columns, dict(found.rows)[label], strict=True))


def test_the_house_defaults_on_five_subjects():
    """Safety set by actual treatment: P1 in Placebo; L1, N1 and H1 in Drug 10 mg."""
    found = _table()
    assert found.columns == ["Placebo", "Drug 10 mg", "Total"]
    assert found.header == ["(N=1)", "(N=3)", "(N=4)"]
    assert [label for label, _ in found.rows] == [reference.ROW_LABELS[code]
                                                  for code in reference.STANDARD_ROWS]
    # P1: the event starts on the day of the first dose. L1: the event before the dose is
    # over; the partial one is completed to the day of the first dose; the late one has no
    # end of emergence against it. N1 and H1: one emergent event each (H1's treatment
    # starts with the first record that has a dose, 2024-03-18, and its event is over by
    # then: not emergent).
    assert _row(found, "Any adverse event") == {
        "Placebo": "1 (100.0)", "Drug 10 mg": "2 ( 66.7)", "Total": "3 ( 75.0)"}
    assert _row(found, "Related adverse event") == {
        "Placebo": "0", "Drug 10 mg": "1 ( 33.3)", "Total": "1 ( 25.0)"}
    assert _row(found, "Serious adverse event") == {
        "Placebo": "0", "Drug 10 mg": "2 ( 66.7)", "Total": "2 ( 50.0)"}
    assert _row(found, "Adverse event leading to discontinuation of study treatment") == {
        "Placebo": "0", "Drug 10 mg": "1 ( 33.3)", "Total": "1 ( 25.0)"}
    assert _row(found, "Fatal adverse event")["Drug 10 mg"] == "1 ( 33.3)"
    # N1's serious event is not related: no serious related event.
    assert _row(found, "Serious related adverse event") == {
        "Placebo": "0", "Drug 10 mg": "0", "Total": "0"}
    assert found.counts["N"] == {"Placebo": 1, "Drug 10 mg": 3, "Total": 4}


def test_the_house_defaults_of_open_default_2():
    """Safety set of the randomized subjects who were dosed: P1 in Placebo; L1 and H1 in
    Drug 10 mg (N1 was not randomized). The window of 30 days leaves out L1's serious
    event on day 41; no total column; a count of zero with its percentage."""
    found = reference.table(TABLES, HOUSE_2, ARMS)
    assert found.columns == ["Placebo", "Drug 10 mg"]
    assert found.header == ["(N=1)", "(N=2)"]
    zero = "0 (  0.0)"
    assert dict(found.rows) == {
        "Any adverse event": ["1 (100.0)", "1 ( 50.0)"],
        "Related adverse event": [zero, "1 ( 50.0)"],
        "Serious adverse event": [zero, zero],
        "Serious related adverse event": [zero, zero],
        "Fatal adverse event": [zero, zero],
        "Adverse event leading to discontinuation of study treatment": [zero, zero],
    }
    assert [label for label, _ in found.rows] == [
        "Any adverse event", "Related adverse event", "Serious adverse event",
        "Serious related adverse event", "Fatal adverse event",
        "Adverse event leading to discontinuation of study treatment"]


def test_the_treatment_decisions():
    # By the first exposure record: every arm has the name of its treatment.
    found = _table(trt__actual__source={"rule": "first_ex_treatment"})
    assert found.columns == ["PLACEBO", "DRUG", "Total"] and found.header[1] == "(N=3)"
    # Actual as planned: H1 moves to its planned arm, N1 has no planned treatment.
    found = _table(trt__actual__source={"rule": "same_as_planned"})
    assert found.columns == ["Placebo", "Drug 10 mg", "Drug 20 mg", "Total"]
    assert found.header == ["(N=1)", "(N=1)", "(N=1)", "(N=3)"]
    # A decoded arm code is read only where the table shows planned treatment.
    decoded = {"rule": "dm_armcd_map", "map": [{"code": "PBO", "label": "Placebo"},
                                               {"code": "LOW", "label": "Low"},
                                               {"code": "HIGH", "label": "High"}]}
    assert _table(trt__planned__source=decoded).columns == ["Placebo", "Drug 10 mg", "Total"]
    found = _table(trt__planned__source=decoded, pop__safety__grouping={"rule": "planned"})
    assert found.columns == ["Placebo", "Low", "High", "Total"]
    # The treatment starts with any exposure record: H1's event on 2024-03-16 is emergent.
    found = _table(trt__start__source={"rule": "first_ex_record"})
    assert _row(found, "Any adverse event")["Drug 10 mg"] == "3 (100.0)"
    found = _table(trt__start__source={"rule": "dm_rfxstdtc"})
    assert _row(found, "Any adverse event")["Drug 10 mg"] == "3 (100.0)"


def test_the_end_of_emergence():
    # 30 days after the last dose: L1's event on day 41 is out; N1 has no treatment end
    # date, so no end.
    window = {"rule": "last_dose_plus_days", "days": 30}
    found = _table(ae__teae__end=window)
    assert _row(found, "Serious adverse event")["Drug 10 mg"] == "1 ( 33.3)"
    assert _row(found, "Any adverse event")["Drug 10 mg"] == "2 ( 66.7)"
    assert _row(_table(ae__teae__end={"rule": "last_dose_plus_days", "days": 41}),
                "Serious adverse event")["Drug 10 mg"] == "2 ( 66.7)"
    # catalog@2 has no end of emergence at the end of the study (#3).
    with pytest.raises(reference.CannotCalculate, match="ae.teae.end"):
        _table(ae__teae__end={"rule": "end_of_study"})
    # With the treatment record as the end-of-study record only L1 has an end at all.
    treatment = {"rule": "disposition_event_by_subcategory", "subcategory": "STUDY TREATMENT"}
    people = {p.usubjid: p for p in reference.people(
        TABLES, {**HOUSE, "disp.status.record": treatment})}
    assert people["L1"].end_of_study == Date(2024, 4, 30) and people["P1"].end_of_study is None
    # The disposition date as the treatment end date where no exposure record has one: N1's
    # event on 2024-03-25 is before 2024-03-27, so nothing changes at 30 days; at 0 days
    # nothing either, and the subject now has an end.
    by_ds = {"rule": "ds_date_when_ex_missing"}
    people = {p.usubjid: p for p in reference.people(TABLES, {**HOUSE, "trt.end.source": by_ds})}
    assert people["N1"].end == Date(2024, 3, 27) and people["L1"].end == Date(2024, 4, 30)
    assert {p.usubjid: p.end for p in reference.people(TABLES, HOUSE)}["N1"] is None
    start = {"rule": "last_ex_start_date"}
    assert {p.usubjid: p.end for p in reference.people(
        TABLES, {**HOUSE, "trt.end.source": start})}["H1"] == Date(2024, 3, 18)
    # The latest end of any exposure record (#24): a record of dose 0 after H1's last dose,
    # to 2024-04-30, ends treatment; by the records with a dose it ends on 2024-04-25.
    tables = {**TABLES, "EX": [*EX, {"USUBJID": "H1", "EXSEQ": 3, "EXTRT": "DRUG",
                                     "EXDOSE": 0.0, "EXSTDTC": "2024-04-26",
                                     "EXENDTC": "2024-04-30"}]}
    ends = {p.usubjid: p.end for p in reference.people(
        tables, {**HOUSE, "trt.end.source": {"rule": "last_ex_record_end"}})}
    assert ends["H1"] == Date(2024, 4, 30) and ends["N1"] is None
    assert {p.usubjid: p.end for p in reference.people(tables, HOUSE)}["H1"] == Date(2024, 4, 25)


def test_the_start_of_emergence_and_partial_dates():
    # By the time of the first dose: P1's event has no time and counts from 00:00, before
    # the dose at 08:00.
    by_time = {"rule": "at_or_after_first_dose_time"}
    found = _table(ae__teae__start=by_time)
    assert _row(found, "Any adverse event")["Placebo"] == "0"
    # By date and time where both were collected (#5): P1's event has no time, so its date
    # counts, and it is emergent; collected at 07:30, before the dose at 08:00, it is not.
    collected = {"rule": "by_time_when_collected"}
    assert _row(_table(ae__teae__start=collected), "Any adverse event")["Placebo"] == \
        "1 (100.0)"
    timed = {**TABLES, "AE": [{**AE[0], "AESTDTC": "2024-03-10T07:30"}, *AE[1:]]}
    found = reference.table(timed, {**HOUSE, "ae.teae.start": collected}, ARMS)
    assert _row(found, "Any adverse event")["Placebo"] == "0"
    found = reference.table(timed, HOUSE, ARMS)
    assert _row(found, "Any adverse event")["Placebo"] == "1 (100.0)"
    late = {**TABLES, "AE": [{**AE[0], "AESTDTC": "2024-03-10T08:00"}, *AE[1:]]}
    found = reference.table(late, {**HOUSE, "ae.teae.start": collected}, ARMS)
    assert _row(found, "Any adverse event")["Placebo"] == "1 (100.0)"
    # L1's partial start "2024-03": to the day of the first dose (emergent), to the first of
    # the month (before the dose, and the event has not ended: not emergent), or not
    # completed (no analysis start date: emergent).
    assert reference.analysis_start("2024-03", Date(2024, 3, 12),
                                    "first_of_month_not_before_first_dose") == Date(2024, 3, 12)
    assert reference.analysis_start("2024-03", Date(2024, 3, 12), "first_of_month") == Date(
        2024, 3, 1)
    assert reference.analysis_start("2024-03", Date(2024, 3, 12), "not_completed") is None
    # A partial date in an earlier month keeps the first day of its own month.
    assert reference.analysis_start("2024-02", Date(2024, 3, 12),
                                    "first_of_month_not_before_first_dose") == Date(2024, 2, 1)
    assert reference.analysis_start("2024", Date(2024, 3, 12), "first_of_month") is None
    assert reference.analysis_start("2024---15", Date(2024, 3, 12), "first_of_month") is None
    found = _table(ae__start__imputation={"rule": "first_of_month"})
    assert _row(found, "Related adverse event")["Drug 10 mg"] == "0"
    found = _table(ae__start__imputation={"rule": "not_completed"})
    assert _row(found, "Related adverse event")["Drug 10 mg"] == "1 ( 33.3)"
    # Partial exposure dates: left out, or completed to the first of the month.
    assert reference.full_date("2024-03") is None and reference.known_month("2024-03") == Date(
        2024, 3, 1)
    assert reference.known_month("2024---15") is None and reference.full_date("2024---15") is None
    tables = {**TABLES, "EX": [{**EX[0], "EXSTDTC": "2024-03"}, *EX[1:]]}
    people = {p.usubjid: p for p in reference.people(tables, HOUSE)}
    assert people["P1"].start is None and not people["P1"].in_safety
    completed = {**HOUSE, "trt.date.imputation": {"rule": "first_day_of_month"}}
    people = {p.usubjid: p for p in reference.people(tables, completed)}
    assert people["P1"].start == Date(2024, 3, 1) and people["P1"].in_safety


def test_the_analysis_sets():
    people = {p.usubjid: p for p in reference.people(TABLES, HOUSE)}
    assert {s for s, p in people.items() if p.randomized} == {"P1", "L1", "L2", "H1"}
    assert {s for s, p in people.items() if p.in_safety} == {"P1", "L1", "N1", "H1"}
    # The randomized subject of catalog@2 (#10): with a disposition record RANDOMIZED in
    # the study, the record decides, whatever the planned arm code.
    randomized = [{"USUBJID": s, "DSSEQ": 9, "DSCAT": "PROTOCOL MILESTONE", "DSSCAT": None,
                   "DSDECOD": "RANDOMIZED", "DSSTDTC": "2024-03-01"} for s in ("P1", "N1")]
    tables = {**TABLES, "DS": [*DS, *randomized]}
    people = {p.usubjid: p for p in reference.people(tables, HOUSE)}
    assert {s for s, p in people.items() if p.randomized} == {"P1", "N1"}
    # The randomized set, by planned treatment: L2 is in it, N1 is not.
    found = _table(tfl__population={"rule": "randomized"})
    assert found.columns == ["Placebo", "Drug 10 mg", "Drug 20 mg", "Total"]
    assert found.header == ["(N=1)", "(N=2)", "(N=1)", "(N=4)"]
    # L2 was never dosed: its event is not emergent.
    assert _row(found, "Any adverse event")["Drug 10 mg"] == "1 ( 50.0)"
    # With a post-baseline value of SYSBP: P1 only (H1's later result is missing, L1 has
    # none after its first dose, L2 has no first dose).
    rule = {"rule": "randomized_with_postbaseline", "test": "SYSBP"}
    found = _table(tfl__population={"rule": "randomized"}, pop__randomized__rule=rule)
    assert found.columns == ["Placebo", "Total"] and found.header == ["(N=1)", "(N=1)"]
    rule = {"rule": "randomized_and_dosed"}
    assert _table(pop__safety__rule=rule).header == ["(N=1)", "(N=2)", "(N=3)"]
    # The efficacy-evaluable set: a baseline and a post-baseline value of the test, or a
    # visit. H1 has a baseline value before its first dose with a dose and no later result.
    efficacy = {"rule": "efficacy"}
    by_value = {"rule": "baseline_and_postbaseline", "test": "SYSBP"}
    found = _table(tfl__population=efficacy, pop__efficacy__rule=by_value)
    assert found.columns == ["Placebo", "Total"] and found.header[0] == "(N=1)"
    by_weight = {"rule": "baseline_and_postbaseline", "test": "WEIGHT"}
    assert _table(tfl__population=efficacy, pop__efficacy__rule=by_weight).columns == [
        "Drug 10 mg", "Total"]
    by_visit = {"rule": "attended_visit", "visit": "WEEK 2"}
    found = _table(tfl__population=efficacy, pop__efficacy__rule=by_visit)
    assert found.header == ["(N=1)", "(N=1)", "(N=2)"]
    with pytest.raises(reference.CannotCalculate, match="tfl.population"):
        _table(tfl__population=efficacy)


def test_the_table_decisions():
    protocol = {"rule": "protocol_order"}
    assert _table(tfl__columns__arms=protocol).columns == ["Drug 10 mg", "Placebo", "Total"]
    found = _table(tfl__population={"rule": "randomized"}, tfl__columns__arms=protocol)
    assert found.columns == ["Drug 20 mg", "Drug 10 mg", "Placebo", "Total"]
    assert _table(tfl__columns__total={"rule": "none"}).columns == ["Placebo", "Drug 10 mg"]
    found = _table(tfl__columns__total={"rule": "active_arms", "control": "Placebo"})
    assert found.header == ["(N=1)", "(N=3)", "(N=3)"]
    # A control that no column has pools every arm.
    found = _table(tfl__columns__total={"rule": "active_arms", "control": "PLACEBO"})
    assert found.header[-1] == "(N=4)"
    always = {"rule": "one_decimal_always", "decimals": 1}
    assert _row(_table(tfl__percent__format=always), "Related adverse event")[
        "Placebo"] == "0 (  0.0)"
    # The number of decimals (#1): the mask "XXX" of a whole number is not padded.
    for decimals, text, zero in ((0, "1 (33)", "0 (0)"), (2, "1 ( 33.33)", "0 (  0.00)")):
        found = _table(tfl__percent__format={"rule": "one_decimal_always", "decimals": decimals})
        assert _row(found, "Related adverse event")["Drug 10 mg"] == text
        assert _row(found, "Related adverse event")["Placebo"] == zero
    # The rows of catalog@2 (#13): a related serious and fatal event, a dose interrupted.
    tables = {**TABLES, "AE": [{**AE[0], "AEACN": "DRUG INTERRUPTED"}, *AE[1:5],
                               {**AE[5], "AEREL": "PROBABLE"}, *AE[6:]]}
    rows = {"rule": "stated_rows",
            "rows": ["SERIOUS_RELATED", "FATAL_RELATED", "DOSE_MODIFIED", "ANY"]}
    found = reference.table(tables, {**HOUSE, "tfl.ae.summary.rows": rows}, ARMS)
    assert dict(found.rows) == {
        "Serious related adverse event": ["0", "1 ( 33.3)", "1 ( 25.0)"],
        "Fatal related adverse event": ["0", "1 ( 33.3)", "1 ( 25.0)"],
        "Adverse event leading to dose modification": ["1 (100.0)", "0", "1 ( 25.0)"],
        "Any adverse event": ["1 (100.0)", "2 ( 66.7)", "3 ( 75.0)"]}
    rows = {"rule": "stated_rows", "rows": ["FATAL", "ANY"]}
    assert [label for label, _ in _table(tfl__ae__summary__rows=rows).rows] == [
        "Fatal adverse event", "Any adverse event"]
    assert _table(tfl__output__include={"rule": "not_included"}) is None
    assert reference.as_record(None) == {"included": False}
    assert reference.as_record(_table())["header"] == ["(N=1)", "(N=3)", "(N=4)"]


def test_rounding_is_done_on_exact_fractions():
    assert reference.rounded(Fraction(25, 4), 1, "half_away_from_zero") == "6.3"
    assert reference.rounded(Fraction(25, 4), 1, "half_even") == "6.2"
    assert reference.rounded(Fraction(75, 4), 1, "half_even") == "18.8"
    assert reference.rounded(Fraction(200, 3), 1, "half_even") == "66.7"
    assert reference.rounded(Fraction(1, 2), 0, "half_even") == "0"
    assert reference.rounded(Fraction(3, 2), 0, "half_even") == "2"
    assert reference.rounded(Fraction(1, 2), 0, "half_away_from_zero") == "1"
    assert reference.rounded(Fraction(100), 1, "half_even") == "100.0"
    assert reference.rounded(Fraction(1, 20), 1, "half_even") == "0.0"
    assert reference.rounded(Fraction(3, 20), 1, "half_even") == "0.2"
    with pytest.raises(reference.CannotCalculate):
        reference.rounded(Fraction(1, 2), 0, "half_down")
    # Sixteen subjects, one with an event: the percentage at a half that the probes plant.
    values = {**HOUSE, "tfl.rounding.rule": {"rule": "half_even"}}
    assert reference.cell_text(1, 16, HOUSE) == "1 (  6.3)"
    assert reference.cell_text(1, 16, values) == "1 (  6.2)"
    assert reference.cell_text(0, 16, HOUSE) == "0" and reference.cell_text(3, 0, HOUSE) == "3"
    assert reference.header_text(16) == "(N=16)"


def test_column_order_by_the_arms_of_the_protocol():
    labels = ["Drug 10 mg", "Drug 20 mg", "Placebo", "Something else"]
    assert reference.column_order(labels, ARMS, "ascending_dose_placebo_first") == [
        "Placebo", "Drug 10 mg", "Drug 20 mg", "Something else"]
    assert reference.column_order(labels, ARMS, "protocol_order") == [
        "Drug 20 mg", "Drug 10 mg", "Placebo", "Something else"]
    # A label that names two arms stands where the first of them stands.
    assert reference.column_order(["PLACEBO", "DRUG"], ARMS, "protocol_order") == [
        "DRUG", "PLACEBO"]
    with pytest.raises(reference.CannotCalculate):
        reference.column_order(labels, ARMS, "alphabetical")
