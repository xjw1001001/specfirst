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
from itertools import combinations

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

    def vitals(self, subject: str, test: str | None = None) -> list[dict]:
        return [r for r in self.rows("VS", subject) if test is None or r["VSTESTCD"] == test]


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
        rows = data.exposure(subject)
        zero = [r["EXSTDTC"][:10] for r in rows
                if r["EXDOSE"] == 0 and "PLACEBO" not in r["EXTRT"]]
        dosed = [r["EXSTDTC"][:10] for r in rows if r["EXDOSE"] > 0]
        if not zero or not dosed or min(zero) >= min(dosed):
            return "no record of dose zero before the first record with a dose"
        return None
    return _each(record, check)


def _rfxstdtc(record: dict, data: Data, design: dict) -> list[str]:
    def check(subject: str) -> str | None:
        starts = [r["EXSTDTC"][:10] for r in data.exposure(subject)]
        if not starts or (data.dm[subject]["RFXSTDTC"] or "")[:10] == min(starts):
            return "RFXSTDTC is the earliest exposure start date"
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
    def check(subject: str) -> str | None:
        rows = data.exposure(subject)
        if not rows or any(r["EXENDTC"] for r in rows):
            return "an exposure record has an end date, or there is no record"
        if data.end_of_study(subject) is None:
            return "no disposition event with a date"
        return None
    return _each(record, check)


def _partial_exposure(record: dict, data: Data, design: dict) -> list[str]:
    def check(subject: str) -> str | None:
        rows = data.exposure(subject)
        if not rows or len(rows[0]["EXSTDTC"]) != 7:
            return "the first exposure start is not a year and a month"
        if not any(_date(r["EXSTDTC"]) for r in rows[1:]):
            return "no other exposure record has a complete start date"
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
        return None if start and dose and start < dose else "RFSTDTC is not before the first dose"
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
        return None if data.exposure(subject) else "no exposure record"
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
        return f"an SV record of {both[0]}" if both else None
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
        starts = [r["AESTDTC"] for r in data.rows("AE", subject)]
        if not any(len(s) == 7 and s == dose[:7] for s in starts if s):
            return "no event start of a year and a month in the month of the first dose"
        return None if len(dose) >= 10 and int(dose[8:10]) > 1 else \
            "the first dose is on the first day of the month"
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
        dose = data.dm[subject]["RFXSTDTC"] or ""
        if "T" not in dose or dose.split("T")[1] <= "00:00":
            return "the first dose has no time after 00:00"
        if not any(r["AESTDTC"] == dose[:10] for r in data.rows("AE", subject)):
            return "no event that starts on the first dose date without a time"
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
        wanted = {last + datetime.timedelta(days=days), last + datetime.timedelta(days=days + 1)}
        return None if wanted <= set(_starts(data, subject)) else \
            f"no events {days} and {days + 1} days after the last dose"
    return _each(record, check)


def _after_end_of_study(record: dict, data: Data, design: dict) -> list[str]:
    def check(subject: str) -> str | None:
        end = data.end_of_study(subject)
        return None if end and any(d > end for d in _starts(data, subject)) else \
            "no event that starts after the end-of-study date"
    return _each(record, check)


def _between_window_and_end(record: dict, data: Data, design: dict) -> list[str]:
    days = record["detail"]["window_days"]

    def check(subject: str) -> str | None:
        last, end = data.last_dose(subject), data.end_of_study(subject)
        if last is None or end is None:
            return "no date of the last dose or of the end of the study"
        limit = last + datetime.timedelta(days=days)
        return None if any(limit < d < end for d in _starts(data, subject)) else \
            f"no event more than {days} days after the last dose and before the end of the study"
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


def arm_counts(data: Data, arm: str) -> tuple[int, int, int]:
    """Treated subjects of an arm; with an event after the first dose day; with a serious one."""
    people = _treated(data, arm)
    having = serious = 0
    for subject in people:
        dose = data.first_dose(subject)
        rows = [r for r in data.rows("AE", subject)
                if (d := _date(r["AESTDTC"])) and dose and d > dose]
        having += bool(rows)
        serious += any(r["AESER"] == "Y" for r in rows)
    return len(people), having, serious


def _rounding_half(record: dict, data: Data, design: dict) -> list[str]:
    detail = record["detail"]
    total, having, serious = arm_counts(data, detail["arm"])
    logged = (detail["subjects"], detail["with_any_event"], detail["with_serious_event"])
    if (total, having, serious) != logged:
        return [f"arm {detail['arm']}: the data give {total}, {having} and {serious} subjects, "
                f"the log says {logged[0]}, {logged[1]} and {logged[2]}"]
    return [f"arm {detail['arm']}: {count} of {total} subjects is not at a rounding half"
            for count in (having, serious) if not probes.is_rounding_half(count, total)]


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
    "ae_starts_after_emergence_window": _after_window,
    "ae_starts_after_end_of_study": _after_end_of_study,
    "ae_between_window_end_and_end_of_study": _between_window_and_end,
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


def coverage(catalog: catalogs.Catalog, design: dict, records: list[dict], tables: Tables,
             which: str = "twin",
             units: tuple[str, ...] = probes.SLICE_UNITS) -> tuple[int, int, list[str]]:
    """Pairs of alternatives asked for, probes checked, and what is missing.

    For every decision of the units that applies to the design, and every
    pair of its alternatives, one probe of the dataset `which` must claim to
    separate the pair and must be found in the data.
    """
    own = [r for r in records if r["data"] == which]
    found: dict[str, list[str]] = {}
    for record in own:
        found[record["probe"]] = find(record, tables, design)
    problems = [f"probe {probe}: {problem}" for probe, issues in sorted(found.items())
                for problem in issues]
    pairs = 0
    for entry in probes.slice_entries(catalog, design, units):
        ids = [alternative.id for alternative in entry.alternatives]
        for first, second in combinations(ids, 2):
            pairs += 1
            claiming = [r["probe"] for r in own
                        if any(set(pair) == {first, second}
                               for pair in r["separates"].get(entry.id, []))]
            if not claiming:
                problems.append(f"{entry.id}: no probe in the {which} separates {first} "
                                f"from {second}")
            elif not any(not found[probe] for probe in claiming):
                problems.append(f"{entry.id}: {first} and {second}: every probe that should "
                                f"separate them is missing from the data "
                                f"({', '.join(claiming)})")
    return pairs, len(own), problems
