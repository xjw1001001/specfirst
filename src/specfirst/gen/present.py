"""Find a logged probe again in the SDTM that was written (PLAN.md section 6.5).

`probes.jsonl` says which probes a dataset carries. A line of a log proves
nothing by itself: for every probe this module has a check that reads the
datasets and says why the probe is not there. The gate asks, for every pair
of alternatives of every applicable decision, for one probe of the twin
that separates the pair and is found in the twin's data.
"""

from __future__ import annotations

import datetime
from collections.abc import Callable

from specfirst.compile import catalog as catalogs
from specfirst.gen import design as designs
from specfirst.gen import probes, sdtm

Date = datetime.date
Tables = dict[str, list[dict]]


def _date(text: object) -> Date | None:
    if not isinstance(text, str) or len(text) < 10:
        return None
    try:
        return Date.fromisoformat(text[:10])
    except ValueError:
        return None


class Data:
    """The datasets of one study, by subject."""

    def __init__(self, tables: Tables):
        self.tables = tables
        self.dm = {row["USUBJID"]: row for row in tables.get("DM", [])}
        self._by_subject: dict[str, dict[str, list[dict]]] = {}
        for name, rows in tables.items():
            if rows and "USUBJID" in rows[0]:
                grouped: dict[str, list[dict]] = {}
                for row in rows:
                    grouped.setdefault(row["USUBJID"], []).append(row)
                self._by_subject[name] = grouped

    def rows(self, domain: str, subject: str) -> list[dict]:
        return self._by_subject.get(domain, {}).get(subject, [])

    def first_dose(self, subject: str) -> Date | None:
        return _date(self.dm[subject]["RFXSTDTC"]) if subject in self.dm else None

    def last_dose(self, subject: str) -> Date | None:
        return _date(self.dm[subject]["RFXENDTC"]) if subject in self.dm else None

    def end_of_study(self, subject: str) -> Date | None:
        dates = [_date(r["DSSTDTC"]) for r in self.rows("DS", subject)
                 if r["DSCAT"] == "DISPOSITION EVENT"]
        return max([d for d in dates if d], default=None)

    def exposure(self, subject: str) -> list[dict]:
        return sorted(self.rows("EX", subject), key=lambda r: r["EXSEQ"])

    def dosed(self, subject: str) -> list[dict]:
        """Exposure records with a dose, as the catalog defines one, and a complete start."""
        return [r for r in self.exposure(subject) if with_dose(r) and _date(r["EXSTDTC"])]

    def event_starts(self, subject: str) -> list[tuple[Date, dict]]:
        """Adverse events with a complete start date, as (date, record)."""
        return [(d, r) for r in self.rows("AE", subject) if (d := _date(r["AESTDTC"]))]

    def vitals(self, subject: str, test: str | None = None) -> list[dict]:
        return [r for r in self.rows("VS", subject) if test is None or r["VSTESTCD"] == test]


def with_dose(row: dict) -> bool:
    """trt.start.source: EXDOSE above zero, or zero with an EXTRT that contains PLACEBO."""
    dose = row["EXDOSE"]
    return dose is not None and (dose > 0 or (dose == 0 and "PLACEBO" in (row["EXTRT"] or "")))


Finder = Callable[[dict, Data, dict], list[str]]


def _each(record: dict, check: Callable[[str], str | None]) -> list[str]:
    """Run a check for every logged subject; a probe without subjects is not there."""
    if not record["subjects"]:
        return ["the log names no subject"]
    return [f"{subject}: {problem}" for subject in record["subjects"]
            if (problem := check(subject)) is not None]


def _arm_label(record: dict, data: Data, design: dict) -> list[str]:
    for name in record["detail"].get("arms", []):
        arm = designs.arm(design, name)
        rows = [r for r in data.dm.values() if r["ARMCD"] == name]
        if rows and arm["description"] != arm["label"] and \
                all(r["ARM"] == arm["description"] for r in rows):
            return []
    return ["no arm in DM whose ARM differs from its short label"]


def _actual_differs(record: dict, data: Data, design: dict) -> list[str]:
    def check(subject: str) -> str | None:
        row = data.dm.get(subject)
        if not row or not row["ARMCD"] or not row["ACTARMCD"] or row["ARMCD"] == row["ACTARMCD"]:
            return "ARMCD and ACTARMCD do not differ"
        actual = designs.arm(design, row["ACTARMCD"])
        name = sdtm.treatment_name(design, actual["studyInterventionId"])
        rows = data.exposure(subject)
        if not rows or any(r["EXTRT"] != name or r["EXDOSE"] != actual["dose"] for r in rows):
            return "the exposure records do not name the treatment of ACTARM"
        return None
    return _each(record, check)


def _first_other(record: dict, data: Data, design: dict) -> list[str]:
    def check(subject: str) -> str | None:
        actual = designs.arm(design, data.dm[subject]["ACTARMCD"])
        name = sdtm.treatment_name(design, actual["studyInterventionId"])
        rows = data.exposure(subject)
        if len(rows) < 2 or rows[0]["EXTRT"] == name:
            return "the first exposure record names the treatment of ACTARM"
        if not any(r["EXTRT"] == name for r in rows[1:]):
            return "no later exposure record names the treatment of ACTARM"
        return None
    return _each(record, check)


def _zero_dose(record: dict, data: Data, design: dict) -> list[str]:
    def check(subject: str) -> str | None:
        zero = [d for r in data.exposure(subject)
                if r["EXDOSE"] == 0 and not with_dose(r) and (d := _date(r["EXSTDTC"]))]
        dosed = [_date(r["EXSTDTC"]) for r in data.dosed(subject)]
        if not zero or not dosed or min(zero) >= min(dosed):
            return "no record of dose zero before the first record with a dose"
        if not any(min(zero) <= d < min(dosed) and (_date(r["AEENDTC"]) or d) < min(dosed)
                   for d, r in data.event_starts(subject)):
            return "no event that starts and ends between the two treatment starts"
        return None
    return _each(record, check)


def _rfxstdtc(record: dict, data: Data, design: dict) -> list[str]:
    def check(subject: str) -> str | None:
        starts = [_date(r["EXSTDTC"]) for r in data.dosed(subject)]
        first = data.first_dose(subject)
        if not starts or first is None or first == min(starts):
            return "RFXSTDTC is the earliest exposure start date"
        low, high = sorted((first, min(starts)))
        if not any(low <= d < high for d, _ in data.event_starts(subject)):
            return "no event that starts between RFXSTDTC and the first exposure record"
        return None
    return _each(record, check)


def _spans_days(record: dict, data: Data, design: dict) -> list[str]:
    for subject in data.dm:
        rows = data.exposure(subject)
        if rows:
            start, end = _date(rows[-1]["EXSTDTC"]), _date(rows[-1]["EXENDTC"])
            if start and end and end > start:
                return []
    return ["no subject whose last exposure record ends after it starts"]


def _no_end_date(record: dict, data: Data, design: dict) -> list[str]:
    """Every subject has no exposure end date and a serious event later than the window
    after the disposition record the log names (gen-2b: the study record; or the treatment
    record, with a study record late enough that the event lies inside the window after
    it; or the treatment record of a subject without a study-level record)."""
    names = design["collection"]["disposition"]["subcategories"]
    window = datetime.timedelta(days=record["detail"]["window_days"])

    def check(subject: str) -> str | None:
        rows = data.exposure(subject)
        if not rows or any(r["EXENDTC"] for r in rows):
            return "an exposure record has an end date, or there is no record"
        if not data.dosed(subject):
            return "no exposure record with a dose and a complete start date"
        own = (record.get("by_subject") or {}).get(subject) or {
            "records": ["study"], "event_after": "study"}
        events = {r["DSSCAT"]: _date(r["DSSTDTC"]) for r in data.rows("DS", subject)
                  if r["DSCAT"] == "DISPOSITION EVENT"}
        wanted = {names[kind] for kind in own["records"]}
        if set(events) != wanted or any(date is None for date in events.values()):
            return (f"disposition events with the subcategories {sorted(events)}, not "
                    f"{sorted(wanted)}")
        end = events[names[own["event_after"]]]
        late = [(d, r) for d, r in data.event_starts(subject) if d > end + window]
        if not late:
            return "no event later than the window after the disposition date"
        if not any(r["AESER"] == "Y" for _, r in late):
            return "the event after the window is not serious"
        if own["event_after"] == "treatment" and "study" in own["records"] and not any(
                d <= events[names["study"]] + window for d, _ in late):
            return "the event lies after the window that follows the study record as well"
        return None
    return _each(record, check)


def _undosed_after_last(record: dict, data: Data, design: dict) -> list[str]:
    days = datetime.timedelta(days=record["detail"]["window_days"])

    def check(subject: str) -> str | None:
        rows = data.exposure(subject)
        dosed = [d for r in rows if with_dose(r) and (d := _date(r["EXENDTC"]))]
        zero = [d for r in rows if r["EXDOSE"] == 0 and not with_dose(r)
                and (d := _date(r["EXENDTC"]))]
        if not dosed or not zero or max(zero) <= max(dosed):
            return "no record of dose zero that ends after the last record with a dose"
        if not any(max(dosed) + days < d <= max(zero) + days
                   for d, _ in data.event_starts(subject)):
            return ("no event later than the window after the last record with a dose and "
                    "within the window after the record of dose zero")
        return None
    return _each(record, check)


def _partial_exposure(record: dict, data: Data, design: dict) -> list[str]:
    def check(subject: str) -> str | None:
        rows = data.exposure(subject)
        if not rows or len(rows[0]["EXSTDTC"]) != 7 or not with_dose(rows[0]):
            return "the first exposure start is not a year and a month"
        complete = [_date(r["EXSTDTC"]) for r in data.dosed(subject)]
        if not complete:
            return "no other exposure record has a complete start date"
        month = _date(rows[0]["EXSTDTC"] + "-01")
        if not any(month <= d < min(complete) and (_date(r["AEENDTC"]) or d) < min(complete)
                   for d, r in data.event_starts(subject)):
            return ("no event between the first day of the month and the first complete "
                    "start date")
        # The efficacy-evaluable set by a baseline value (gen-2b): a value of its test
        # before the first day of the month, a baseline for the completed date.
        test = record["detail"].get("value_before_month")
        if test and not any((d := _date(r["VSDTC"])) and d < month
                            for r in data.vitals(subject, test)):
            return f"no value of {test} before the first day of the month of the first dose"
        return None
    return _each(record, check)


def _partial_not_earliest(record: dict, data: Data, design: dict) -> list[str]:
    def check(subject: str) -> str | None:
        rows = data.exposure(subject)
        if len(rows) < 3 or not _date(rows[0]["EXSTDTC"]) or not _date(rows[-1]["EXENDTC"]):
            return "the first and the last exposure dates are not complete"
        if not any(len(r["EXSTDTC"]) == 7 and len(r["EXENDTC"] or "") == 7 for r in rows[1:-1]):
            return "no record between them has dates of a year and a month"
        return None
    return _each(record, check)


def _reference_start(record: dict, data: Data, design: dict) -> list[str]:
    def check(subject: str) -> str | None:
        start, dose = _date(data.dm[subject]["RFSTDTC"]), data.first_dose(subject)
        if not (start and dose and start < dose):
            return "RFSTDTC is not before the first dose"
        return None if data.event_starts(subject) else \
            "no event with a start date: no study day that the two origins number differently"
    return _each(record, check)


def _without_postbaseline(record: dict, data: Data, design: dict) -> list[str]:
    def check(subject: str) -> str | None:
        test = record["by_subject"][subject]["test"]
        dose = data.first_dose(subject)
        if not data.dm[subject]["ARMCD"] or dose is None:
            return "the subject is not randomized and dosed"
        later = [r for r in data.vitals(subject) if (d := _date(r["VSDTC"])) and d > dose]
        if any(r["VSTESTCD"] == test for r in later):
            return f"a value of {test} after the first dose"
        return None if later else "no later value of another vital sign"
    return _each(record, check)


def _not_randomized(record: dict, data: Data, design: dict) -> list[str]:
    def check(subject: str) -> str | None:
        if data.dm[subject]["ARMCD"]:
            return "ARMCD is present"
        return None if data.dosed(subject) else \
            "no exposure record with a dose and a complete start date"
    return _each(record, check)


def _never_dosed(record: dict, data: Data, design: dict) -> list[str]:
    def check(subject: str) -> str | None:
        if not data.dm[subject]["ARMCD"]:
            return "ARMCD is missing"
        return "an exposure record" if data.exposure(subject) else None
    return _each(record, check)


def _split(data: Data, subject: str, test: str) -> tuple[list[dict], list[dict]]:
    """The values of a test on or before the day of the first dose, and after it."""
    dose = data.first_dose(subject)
    rows = [(r, _date(r["VSDTC"])) for r in data.vitals(subject, test)]
    before = [r for r, d in rows if d and dose and d <= dose]
    after = [r for r, d in rows if d and dose and d > dose]
    return before, after


def _visit_missed(record: dict, data: Data, design: dict) -> list[str]:
    def check(subject: str) -> str | None:
        for test in record["detail"]["tests"]:
            before, after = _split(data, subject, test)
            if not before or not after:
                return f"no baseline value or no later value of {test}"
        attended = {r["VISIT"] for r in data.rows("SV", subject)}
        both = sorted(attended & set(record["detail"]["visits"]))
        if both:
            return f"an SV record of {both[0]}"
        # gen-2b: an event after the first dose, so that planted subjects without events
        # who move the other way between the two rules do not leave the table the same.
        dose = data.first_dose(subject)
        return None if dose and any(d > dose for d, _ in data.event_starts(subject)) else \
            "no adverse event after the first dose"
    return _each(record, check)


def _other_test_only(record: dict, data: Data, design: dict) -> list[str]:
    def check(subject: str) -> str | None:
        test = record["by_subject"][subject]["test_without_baseline"]
        before, after = _split(data, subject, test)
        if before or not after:
            return f"{test} has a baseline value or no later value"
        codes = {r["VSTESTCD"] for r in data.vitals(subject)} - {test}
        if not any(all(_split(data, subject, code)) for code in codes):
            return "no other vital sign with a baseline value and a later value"
        return None
    return _each(record, check)


def _two_dispositions(record: dict, data: Data, design: dict) -> list[str]:
    names = design["collection"]["disposition"]["subcategories"]

    def check(subject: str) -> str | None:
        rows = sorted((r for r in data.rows("DS", subject) if r["DSCAT"] == "DISPOSITION EVENT"),
                      key=lambda r: r["DSSEQ"])
        if len(rows) != 2:
            return f"{len(rows)} disposition event records"
        first, second = rows
        if (first["DSSCAT"], second["DSSCAT"]) != (names["treatment"], names["study"]):
            return "not the end of treatment followed by the end of the study"
        if first["DSDECOD"] == second["DSDECOD"] or first["DSSTDTC"] == second["DSSTDTC"]:
            return "the two records have the same term or the same date"
        return None
    return _each(record, check)


def _partial_ae_in_month(record: dict, data: Data, design: dict) -> list[str]:
    def check(subject: str) -> str | None:
        dose = data.dm[subject]["RFXSTDTC"] or ""
        if len(dose) < 10 or int(dose[8:10]) <= 1:
            return "the first dose is on the first day of the month, or has no complete date"
        # The subject logged without a time of the first dose (gen-2b): none in DM or EX.
        own = (record.get("by_subject") or {}).get(subject) or {}
        if "dose_time" in own and own["dose_time"] is None and (
                len(dose) != 10 or any(len(r["EXSTDTC"] or "") > 10
                                       for r in data.exposure(subject)[:1])):
            return "the first dose has a time, and the log says it has none"
        rows = [r for r in data.rows("AE", subject)
                if r["AESTDTC"] and len(r["AESTDTC"]) == 7 and r["AESTDTC"] == dose[:7]]
        if not rows:
            return "no event start of a year and a month in the month of the first dose"
        # An event that ended before the first dose is not emergent under any alternative.
        if not any(not r["AEENDTC"] or r["AEENDTC"][:10] >= dose[:10] for r in rows):
            return "the event ended before the first dose"
        return None
    return _each(record, check)


def _partial_ae_before_month(record: dict, data: Data, design: dict) -> list[str]:
    def check(subject: str) -> str | None:
        dose = (data.dm[subject]["RFXSTDTC"] or "")[:7]
        rows = [r for r in data.rows("AE", subject)
                if r["AESTDTC"] and len(r["AESTDTC"]) == 7 and r["AESTDTC"] < dose]
        if not rows:
            return "no event start of a year and a month before the month of the first dose"
        return None if any(not r["AEENDTC"] for r in rows) else "the event is not ongoing"
    return _each(record, check)


def _on_first_dose_date(record: dict, data: Data, design: dict) -> list[str]:
    def check(subject: str) -> str | None:
        # The time of the first dose is read from the exposure record by two alternatives
        # of trt.start.source and from DM.RFXSTDTC by the third: it must stand in both.
        dosed = data.dosed(subject)
        texts = [data.dm[subject]["RFXSTDTC"] or "", dosed[0]["EXSTDTC"] if dosed else ""]
        if any("T" not in text or text.split("T")[1] <= "00:00" for text in texts):
            return "the first dose has no time after 00:00 in EX.EXSTDTC or in DM.RFXSTDTC"
        if texts[0][:10] != texts[1][:10]:
            return "DM.RFXSTDTC and the first exposure record are on different days"
        if not any(r["AESTDTC"] == texts[1][:10] for r in data.rows("AE", subject)):
            return "no event that starts on the first dose date without a time"
        return None
    return _each(record, check)


def _timed_before_dose(record: dict, data: Data, design: dict) -> list[str]:
    def check(subject: str) -> str | None:
        # The time of the first dose stands in the exposure record and in DM.RFXSTDTC,
        # as for the event on the first dose date without a time.
        dosed = data.dosed(subject)
        texts = [data.dm[subject]["RFXSTDTC"] or "", dosed[0]["EXSTDTC"] if dosed else ""]
        if any("T" not in text or text.split("T")[1] <= "00:00" for text in texts):
            return "the first dose has no time after 00:00 in EX.EXSTDTC or in DM.RFXSTDTC"
        if texts[0] != texts[1]:
            return "DM.RFXSTDTC and the first exposure record differ"
        if not any(str(r["AESTDTC"])[:11] == texts[1][:11] and str(r["AESTDTC"]) < texts[1]
                   for r in data.rows("AE", subject)):
            return "no event on the first dose date at a collected time before the dose"
        return None
    return _each(record, check)


def _starts(data: Data, subject: str) -> list[Date]:
    return [d for r in data.rows("AE", subject) if (d := _date(r["AESTDTC"]))]


def _after_window(record: dict, data: Data, design: dict) -> list[str]:
    days = record["detail"]["window_days"]

    def check(subject: str) -> str | None:
        last = data.last_dose(subject)
        if last is None:
            return "no date of the last dose"
        offset = record["by_subject"][subject]["days_after_last_dose"]
        return None if last + datetime.timedelta(days=offset) in _starts(data, subject) else \
            f"no event {offset} days after the last dose"
    offsets = sorted(own["days_after_last_dose"] for own in record["by_subject"].values())
    if offsets != [days, days + 1]:
        return [f"the log has subjects for {offsets} days after the last dose, not for "
                f"{days} and {days + 1}"]
    return _each(record, check)


def _each_causality(record: dict, data: Data, design: dict) -> list[str]:
    problems = []
    seen = set()
    for subject, own in record["by_subject"].items():
        dose = data.first_dose(subject)
        rows = [r for r in data.rows("AE", subject) if r["AEREL"] == own["value"]
                and (d := _date(r["AESTDTC"])) and dose and d > dose]
        if rows:
            seen.add(own["value"])
        else:
            problems.append(f"{subject}: no event after the first dose with the causality "
                            f"{own['value']}")
    collected = design["collection"]["adverseEvents"]["causality"]
    problems += [f"no planted event with the causality {value}"
                 for value in collected if value not in seen]
    return problems


def _without_any_postbaseline(record: dict, data: Data, design: dict) -> list[str]:
    def check(subject: str) -> str | None:
        dose = data.first_dose(subject)
        if dose is None or not data.exposure(subject):
            return "the subject is not dosed"
        if any((d := _date(r["VSDTC"])) and d > dose for r in data.vitals(subject)):
            return "a vital sign value after the first dose"
        if any((d := _date(r["SVSTDTC"])) and d > dose for r in data.rows("SV", subject)):
            return "a visit after the first dose"
        return None
    return _each(record, check)


def _treated(data: Data, arm: str) -> list[str]:
    return [subject for subject, row in data.dm.items()
            if row["ACTARMCD"] == arm and row["RFXSTDTC"]]


def _zero_count(record: dict, data: Data, design: dict) -> list[str]:
    arm = record["detail"]["arm"]
    people = [s for s, row in data.dm.items() if arm in (row["ARMCD"], row["ACTARMCD"])]
    if not _treated(data, arm):
        return [f"no treated subject in the arm {arm}"]
    fatal = [s for s in people if any(r["AESDTH"] == "Y" for r in data.rows("AE", s))]
    return [f"{len(fatal)} subjects of the arm {arm} have a fatal event"] if fatal else []


def _rounding_half(record: dict, data: Data, design: dict) -> list[str]:
    """The column of the arm under the decisions the counts were set for (the log names
    them), by the hand calculation: its size and its counts are the logged ones, and the
    counts lie at a rounding half at the logged number of decimals."""
    detail = record["detail"]
    try:
        column = probes.spared_column(data.tables, detail["decisions"], detail["arm"])
    except (RuntimeError, ValueError) as error:   # reference.CannotCalculate is a ValueError
        return [f"the column cannot be calculated: {error}"]
    found = (len(column.members), len(column.with_any_event), len(column.with_serious_event))
    logged = (detail["subjects"], detail["with_any_event"], detail["with_serious_event"])
    if column.label != detail["column"] or found != logged:
        return [f"column {column.label!r}: the data give {found[0]}, {found[1]} and {found[2]} "
                f"subjects, the log says {detail['column']!r} with {logged[0]}, {logged[1]} "
                f"and {logged[2]}"]
    added = set(record["subjects"])
    if len(added) != detail["subjects_added"] or not added <= set(column.members):
        return [f"column {column.label!r}: the log names {len(added)} added subjects, of which "
                f"{len(added - set(column.members))} are not in the column; it counts "
                f"{detail['subjects_added']}"]
    return [f"column {column.label!r}: {count} of {found[0]} subjects is not at a rounding half "
            f"at {detail['decimals']} decimals" for count in found[1:]
            if not probes.is_rounding_half(count, found[0], detail["decimals"])]


def _out_of_dose_order(record: dict, data: Data, design: dict) -> list[str]:
    listed = [arm["name"] for arm in designs.arms(design)]
    return [] if listed != designs.dose_order(design) else \
        ["the protocol lists the arms in ascending order of dose with placebo first"]


def _nothing_to_find(record: dict, data: Data, design: dict) -> list[str]:
    return []


FINDERS: dict[str, Finder] = {
    "output_shape": _nothing_to_find,
    "arms_listed_out_of_dose_order": _out_of_dose_order,
    "arm_label_differs_from_decode": _arm_label,
    "actual_arm_differs_from_planned": _actual_differs,
    "first_exposure_other_treatment": _first_other,
    "zero_dose_record_before_first_dose": _zero_dose,
    "rfxstdtc_differs_from_exposure": _rfxstdtc,
    "last_exposure_record_spans_days": _spans_days,
    "no_exposure_end_date": _no_end_date,
    "undosed_record_after_last_dose": _undosed_after_last,
    "partial_exposure_date": _partial_exposure,
    "partial_exposure_date_not_earliest": _partial_not_earliest,
    "reference_start_before_first_dose": _reference_start,
    "randomized_without_postbaseline_value": _without_postbaseline,
    "dosed_but_not_randomized": _not_randomized,
    "randomized_never_dosed": _never_dosed,
    "postbaseline_value_but_visit_missed": _visit_missed,
    "baseline_value_of_other_test_only": _other_test_only,
    "two_disposition_events": _two_dispositions,
    "partial_ae_start_in_month_of_first_dose": _partial_ae_in_month,
    "partial_ae_start_before_month_of_first_dose": _partial_ae_before_month,
    "ae_on_first_dose_date_without_time": _on_first_dose_date,
    "ae_timed_before_timed_first_dose": _timed_before_dose,
    "ae_starts_after_emergence_window": _after_window,
    "ae_with_each_causality_value": _each_causality,
    "dosed_without_postbaseline_value": _without_any_postbaseline,
    "category_with_zero_count": _zero_count,
    "statistic_at_rounding_half": _rounding_half,
}


def find(record: dict, tables: Tables, design: dict) -> list[str]:
    """Why a logged probe is not in the data. An empty list means it is there."""
    finder = FINDERS.get(record["probe"])
    if finder is None:
        return [f"no check for the probe '{record['probe']}'"]
    try:
        return finder(record, Data(tables), design)
    except (KeyError, TypeError, IndexError) as error:
        return [f"the data cannot be read for this probe: {type(error).__name__}: {error}"]


def planted_for(log: list[dict]) -> str:
    """What the twin's probes were made for (gen-2b): the table's analysis set, grouping,
    decimals and window, the calibrated column, and the recipes that follow them."""
    twin = {record["probe"]: record for record in log if record["data"] == "twin"}
    counts = twin["statistic_at_rounding_half"]["detail"]
    values = counts["decisions"]
    window = values["ae.teae.end"]
    parts = [f"table on the {counts['population']} set, by {counts['grouping']} treatment",
             f"{counts['decimals']} decimals",
             "window " + (f"{window['days']} days" if window["rule"] == "last_dose_plus_days"
                          else "none"),
             f"column {counts['column']!r} of {counts['subjects']} subjects "
             f"({counts['subjects_added']} added), {counts['with_any_event']} with an event, "
             f"{counts['with_serious_event']} with a serious one"]
    if "no_exposure_end_date" in twin:
        record = twin["no_exposure_end_date"]
        own = list((record.get("by_subject") or {}).values())
        parts.append("the subject without an exposure end date "
                     + ("completes its treatment" if record["detail"]["completes_treatment"]
                        else "stops early")
                     + (", with a treatment and a study disposition record"
                        if own and own[0]["records"] == ["treatment", "study"] else "")
                     + (", and a second one without a study-level disposition record"
                        if len(own) > 1 else ""))
    if len((twin.get("partial_ae_start_in_month_of_first_dose") or {}).get("subjects", [])) > 1:
        parts.append("a partial event in the month of a first dose without a time")
    if "ae_with_each_causality_value" in twin:
        parts.append("causality events "
                     + ("serious" if twin["ae_with_each_causality_value"]["detail"]["serious"]
                        else "not serious"))
    return "; ".join(parts)


def coverage(catalog: catalogs.Catalog, design: dict, records: list[dict], tables: Tables,
             which: str = "twin",
             units: tuple[str, ...] = probes.SLICE_UNITS) -> tuple[int, int, list[str]]:
    """Pairs of alternatives asked for, probes checked, and what is missing.

    For every decision of the units that applies to the design, and every
    pair of its alternatives, one probe of the dataset `which` must separate
    the pair, as the catalog says, and must be found in the data. The twin
    must carry every probe that these decisions list. The log is what is
    being checked: which pairs a probe separates is read from the catalog,
    and a line of the log that claims other pairs is a problem.
    """
    own = [r for r in records if r["data"] == which]
    logged = [record["probe"] for record in own]
    problems = [f"probe {probe}: logged {logged.count(probe)} times"
                for probe in sorted(set(logged)) if logged.count(probe) > 1]
    found: dict[str, list[str]] = {}
    claims: dict[str, dict[str, list[list]]] = {}
    for record in own:
        probe = record["probe"]
        if probe not in catalog.probes:
            problems.append(f"probe {probe}: not a probe of the catalog")
            continue
        found[probe] = find(record, tables, design)
        claims[probe] = probes.claimed_pairs(catalog, design, probe)
        if record.get("separates") != claims[probe]:
            problems.append(f"probe {probe}: the log claims other pairs than the catalog gives")
    problems += [f"probe {probe}: {problem}" for probe, issues in sorted(found.items())
                 for problem in issues]
    if which == "twin":
        problems += [f"probe {probe}: the twin does not carry it"
                     for probe in probes.needed(catalog, design, units) if probe not in found]
    pairs = 0
    for entry in probes.slice_entries(catalog, design, units):
        for first, second in probes.pairs_of(entry, design):
            pairs += 1
            claiming = [probe for probe in found
                        if [first, second] in claims[probe].get(entry.id, [])]
            if not claiming:
                problems.append(f"{entry.id}: no probe in the {which} separates {first} "
                                f"from {second}")
            elif not any(not found[probe] for probe in claiming):
                problems.append(f"{entry.id}: {first} and {second}: every probe that should "
                                f"separate them is missing from the data "
                                f"({', '.join(claiming)})")
    return pairs, len(found), problems
