"""The reference of a generated study: the adverse event summary, calculated by hand.

Property P2 asks that a build equals its reference (PLAN.md section 4.6). A
real study has a reference: what it delivered. A generated study has none,
so this module is one: it calculates the output of the slice from the SDTM
rows and the decision values, by the words of the catalog entries of the
default pair (`catalog@2`, `open-default@2`, ADR-020), the way a statistician
would check a table with a second program.

It shares no code with the machine: no compiler, no template, no yamaa, no
result engine, no grid builder, no method registry. It reads SDTM as rows
(Dataset-JSON), works with dates and whole numbers, and rounds exact
fractions. Where the two agree, two independent readings of the catalog
agree; where they differ, one of them is wrong, or the catalog can be read
in two ways. `verify` holds every build against it.

What it takes from elsewhere, and says so:

- The text of a cell: `cell_text` and `header_text` follow the display of
  specfirst.gen.display (a count, and a percentage in brackets with the
  decimals of tfl.percent.format, padded to its mask when it has decimals).
- The arms of the protocol, which no decision carries (`Arm`): their order,
  their doses, and the texts that can name each arm in a treatment column.
  The caller makes them with `gold.arms_of`, the function the machine uses,
  so the two share that input. `column_order` is the rule of
  `gold.order_values` written a second time, not a second reading: an arm
  that `arms_of` names wrongly stands last in both.
- The labels of the rows and of the total column (`ROW_LABELS`,
  `TOTAL_LABEL`): copied from the ARS and layout templates of the house
  standard.

Readings where the words of an entry leave a choice are marked READING. A
reading that the machine shares does not show as a difference.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from fractions import Fraction

Date = datetime.date
Tables = dict[str, list[dict]]
Values = dict[str, dict]
DAY = datetime.timedelta(days=1)

ROW_LABELS = {
    "ANY": "Any adverse event",
    "RELATED": "Related adverse event",
    "SERIOUS": "Serious adverse event",
    "SERIOUS_RELATED": "Serious related adverse event",
    "DISCONTINUATION": "Adverse event leading to discontinuation of study treatment",
    "DOSE_MODIFIED": "Adverse event leading to dose modification",
    "FATAL": "Fatal adverse event",
    "FATAL_RELATED": "Fatal related adverse event",
}
# tfl.ae.summary.rows/standard_rows: the rows of the ARS example in its order, without
# its rows of related fatal events and of events leading to dose modification.
STANDARD_ROWS = ("ANY", "RELATED", "SERIOUS", "SERIOUS_RELATED", "FATAL", "DISCONTINUATION")
# AEACN of an event leading to dose modification (tfl.ae.summary.rows, notes).
DOSE_MODIFIED = ("DOSE REDUCED", "DRUG INTERRUPTED")
TOTAL_LABEL = "Total"


class CannotCalculate(ValueError):
    """The decisions cannot be calculated by this reference."""


@dataclass(frozen=True)
class Arm:
    """What the protocol says of one arm; the list of arms is in its order."""

    code: str
    dose: float
    names: tuple[str, ...]   # every text that names the arm in a treatment column


@dataclass
class Person:
    """One subject of DM with what the decisions make of it."""

    usubjid: str
    planned: str | None = None      # TRT01P
    actual: str | None = None       # TRT01A
    start: Date | None = None       # TRTSDT
    start_time: int = 0             # seconds of the day of the first dose; 0 without a time
    end: Date | None = None         # TRTEDT
    end_of_study: Date | None = None
    randomized: bool = False        # RANDFL
    in_randomized: bool = False     # ITTFL
    in_safety: bool = False         # SAFFL
    in_efficacy: bool = False       # EFFFL
    events: list[dict] = field(default_factory=list)   # per event: start, emergent, kinds


@dataclass
class Table:
    """The adverse event summary as texts: what the grid must show."""

    columns: list[str]
    header: list[str]
    rows: list[tuple[str, list[str]]]
    counts: dict = field(default_factory=dict)   # numbers behind the texts, for a report

    def cells(self) -> dict[tuple[str, str], str]:
        """(row label, column label) -> text, the header row under the label ''."""
        found = {("", column): text for column, text in zip(self.columns, self.header,
                                                             strict=True)}
        for label, texts in self.rows:
            found.update({(label, column): text
                          for column, text in zip(self.columns, texts, strict=True)})
        return found


# ---- dates ---------------------------------------------------------------------------


def full_date(text: object) -> Date | None:
    """The date of a text that has a year, a month and a day; None for anything less."""
    if not isinstance(text, str) or len(text) < 10:
        return None
    try:
        return Date.fromisoformat(text[:10])
    except ValueError:
        return None


def known_month(text: object) -> Date | None:
    """The first day of the month of a text that has a year and a month and no day."""
    if not isinstance(text, str) or len(text) != 7 or text[4] != "-":
        return None
    try:
        return Date(int(text[:4]), int(text[5:7]), 1)
    except ValueError:
        return None


def seconds_of(text: object) -> int:
    """The time of day of a date and time, in seconds; 0 when no time was collected."""
    if not isinstance(text, str) or len(text) < 16 or text[10] != "T":
        return 0
    parts = [int(part) for part in text[11:].split(":")[:3]]
    parts += [0] * (3 - len(parts))
    return 3600 * parts[0] + 60 * parts[1] + parts[2]


def _by_subject(rows: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for row in rows:
        grouped.setdefault(row["USUBJID"], []).append(row)
    return grouped


# ---- the modules -----------------------------------------------------------------------


def with_dose(record: dict) -> bool:
    """trt.start.source: EXDOSE above zero, or zero with an EXTRT that contains PLACEBO."""
    dose = record.get("EXDOSE")
    return dose is not None and (dose > 0 or (dose == 0 and "PLACEBO" in (record.get("EXTRT")
                                                                          or "")))


def _usable(text: object, imputation: str) -> tuple[Date, int] | None:
    """An exposure date as trt.date.imputation lets it take part: (date, seconds of the day)."""
    date = full_date(text)
    if date is not None:
        return date, seconds_of(text)
    if imputation == "first_day_of_month":
        month = known_month(text)
        if month is not None:
            return month, 0
    return None


def _treatment_dates(person: Person, dm: dict, exposure: list[dict], values: Values) -> None:
    start, end = values["trt.start.source"]["rule"], values["trt.end.source"]["rule"]
    imputation = values["trt.date.imputation"]["rule"]
    dosed = [record for record in exposure if with_dose(record)]
    if start == "first_ex_with_dose":
        texts = [record["EXSTDTC"] for record in dosed]
    elif start == "first_ex_record":
        texts = [record["EXSTDTC"] for record in exposure]
    elif start == "dm_rfxstdtc":
        texts = [dm.get("RFXSTDTC")]
    else:
        raise CannotCalculate(f"trt.start.source: {start}")
    starts = [found for text in texts if (found := _usable(text, imputation)) is not None]
    if starts:
        person.start, person.start_time = min(starts)
    field_name = {"last_ex_end_date": "EXENDTC", "ds_date_when_ex_missing": "EXENDTC",
                  "last_ex_start_date": "EXSTDTC", "last_ex_record_end": "EXENDTC"}.get(end)
    if field_name is None:
        raise CannotCalculate(f"trt.end.source: {end}")
    # last_ex_record_end: every exposure record takes part, whatever its dose.
    records = exposure if end == "last_ex_record_end" else dosed
    ends = [found[0] for record in records
            if (found := _usable(record[field_name], imputation)) is not None]
    if ends:
        person.end = max(ends)
    elif end == "ds_date_when_ex_missing" and person.start is not None:
        # "or the end-of-study disposition date when no such record has an end date ...
        # taken only for a subject with a treatment start"
        person.end = person.end_of_study


def _end_of_study(disposition: list[dict], value: dict) -> Date | None:
    events = [record for record in disposition if record["DSCAT"] == "DISPOSITION EVENT"]
    if value["rule"] == "disposition_event_by_subcategory":
        events = [record for record in events if record["DSSCAT"] == value["subcategory"]]
    elif value["rule"] != "disposition_event":
        raise CannotCalculate(f"disp.status.record: {value['rule']}")
    if not events:
        return None
    return full_date(max(events, key=lambda record: record["DSSEQ"])["DSSTDTC"])


def _results(vitals: list[dict], test: str) -> list[Date]:
    """The dates of the non-missing results of a vital sign test."""
    return [date for record in vitals
            if record["VSTESTCD"] == test and record["VSSTRESN"] is not None
            and (date := full_date(record["VSDTC"])) is not None]


def _populations(person: Person, dm: dict, disposition: list[dict], vitals: list[dict],
                 visits: list[dict], values: Values, by_disposition: bool) -> None:
    # pop.randomized.rule, fixed rule randomized_subject: a disposition record RANDOMIZED;
    # when no subject of the study has one, the planned arm code.
    if by_disposition:
        person.randomized = any(record.get("DSDECOD") == "RANDOMIZED"
                                for record in disposition)
    else:
        code = dm.get("ARMCD")
        person.randomized = bool(code) and code not in ("SCRNFAIL", "NOTASSGN")
    rule = values["pop.randomized.rule"]
    if rule["rule"] == "all_randomized":
        person.in_randomized = person.randomized
    elif rule["rule"] == "randomized_with_postbaseline":
        after = person.start is not None and any(
            date > person.start for date in _results(vitals, rule["test"]))
        person.in_randomized = person.randomized and after
    else:
        raise CannotCalculate(f"pop.randomized.rule: {rule['rule']}")
    dosed = person.start is not None
    rule = values["pop.safety.rule"]["rule"]
    if rule == "at_least_one_dose":
        person.in_safety = dosed
    elif rule == "randomized_and_dosed":
        person.in_safety = dosed and person.randomized
    else:
        raise CannotCalculate(f"pop.safety.rule: {rule}")
    rule = values.get("pop.efficacy.rule")
    if rule is None:
        person.in_efficacy = False
    elif rule["rule"] == "baseline_and_postbaseline":
        dates = _results(vitals, rule["test"])
        person.in_efficacy = person.in_safety and any(d <= person.start for d in dates) \
            and any(d > person.start for d in dates)
    elif rule["rule"] == "attended_visit":
        person.in_efficacy = person.in_safety and any(
            record["VISIT"] == rule["visit"] for record in visits)
    else:
        raise CannotCalculate(f"pop.efficacy.rule: {rule['rule']}")


def _treatments(person: Person, dm: dict, exposure: list[dict], values: Values) -> None:
    rule = values["trt.planned.source"]
    if rule["rule"] == "dm_arm":
        person.planned = dm.get("ARM") or None
    elif rule["rule"] == "dm_armcd_map":
        labels = {pair["code"]: pair["label"] for pair in rule["map"]}
        person.planned = labels.get(dm.get("ARMCD"))
    else:
        raise CannotCalculate(f"trt.planned.source: {rule['rule']}")
    rule = values["trt.actual.source"]["rule"]
    if rule == "dm_actarm":
        person.actual = dm.get("ACTARM") or None
    elif rule == "first_ex_treatment":
        # READING: "the one with the earliest start date; the lowest EXSEQ breaks a tie".
        # A partial start date is ordered as its text, which puts it before every date
        # of its month.
        first = min(exposure, key=lambda r: (r["EXSTDTC"] or "", r["EXSEQ"]), default=None)
        person.actual = first["EXTRT"] if first else None
    elif rule == "same_as_planned":
        person.actual = person.planned
    else:
        raise CannotCalculate(f"trt.actual.source: {rule}")


def analysis_start(text: object, treatment_start: Date | None, rule: str) -> Date | None:
    """ASTDT of an adverse event (ae.start.imputation)."""
    date = full_date(text)
    if date is not None:
        return date
    month = known_month(text)
    if month is None or rule == "not_completed":
        return None
    if rule == "first_of_month":
        return month
    if rule == "first_of_month_not_before_first_dose":
        # READING: "completed with the first day of that month, or with the treatment
        # start date when it falls in that month": the treatment start date is taken
        # only when it lies in the month of the event. A partial date in an earlier
        # month keeps the first day of its own month.
        if treatment_start is not None and (treatment_start.year, treatment_start.month) == (
                month.year, month.month):
            return treatment_start
        return month
    raise CannotCalculate(f"ae.start.imputation: {rule}")


def _emergent(person: Person, event: dict, start: Date | None, values: Values) -> bool:
    """TRTEMFL of one event (ae.teae.start with its notes, ae.teae.end)."""
    if person.start is None:
        return False
    # READING: "an event that ends before the treatment start date" needs a complete
    # end date; a partial end date is no end. And when an event has no analysis start
    # date and a complete end date before the treatment start, two notes of the entry
    # apply (not emergent because it ended; emergent because the start is missing): the
    # end decides.
    ended = full_date(event.get("AEENDTC"))
    if ended is not None and ended < person.start:
        return False
    if start is None:
        return True
    rule = values["ae.teae.start"]["rule"]
    if rule == "on_or_after_first_dose_date":
        begins = start >= person.start
    elif rule == "at_or_after_first_dose_time":
        # A start without a collected time, a completed one included, counts from 00:00.
        collected = seconds_of(event["AESTDTC"]) if full_date(event["AESTDTC"]) else 0
        begins = (start, collected) >= (person.start, person.start_time)
    elif rule == "by_time_when_collected":
        # On the first dose date an event is not emergent only when both times were
        # collected and it starts before the dose. READING: the time of the first dose
        # counts as collected when it is after 00:00 (nothing precedes 00:00 on its day).
        timed = full_date(event["AESTDTC"]) is not None and str(event["AESTDTC"])[10:11] == "T"
        if start == person.start and timed and person.start_time > 0:
            begins = seconds_of(event["AESTDTC"]) >= person.start_time
        else:
            begins = start >= person.start
    else:
        raise CannotCalculate(f"ae.teae.start: {rule}")
    rule = values["ae.teae.end"]
    if rule["rule"] == "no_end":
        within = True
    elif rule["rule"] == "last_dose_plus_days":
        within = person.end is None or start <= person.end + rule["days"] * DAY
    else:
        raise CannotCalculate(f"ae.teae.end: {rule['rule']}")
    return begins and within


def people(tables: Tables, values: Values) -> list[Person]:
    """Every subject of DM with its treatments, dates, analysis sets and events."""
    exposure, disposition = _by_subject(tables.get("EX", [])), _by_subject(tables.get("DS", []))
    vitals, visits = _by_subject(tables.get("VS", [])), _by_subject(tables.get("SV", []))
    events = _by_subject(tables.get("AE", []))
    related = set((values.get("ae.related.values") or {}).get("values") or ())
    imputation = values["ae.start.imputation"]["rule"]
    by_disposition = any(record.get("DSDECOD") == "RANDOMIZED"
                         for record in tables.get("DS", []))
    found = []
    for dm in tables["DM"]:
        subject = dm["USUBJID"]
        person = Person(subject)
        person.end_of_study = _end_of_study(disposition.get(subject, []),
                                            values["disp.status.record"])
        _treatment_dates(person, dm, exposure.get(subject, []), values)
        _populations(person, dm, disposition.get(subject, []), vitals.get(subject, []),
                     visits.get(subject, []), values, by_disposition)
        _treatments(person, dm, exposure.get(subject, []), values)
        for event in events.get(subject, []):
            start = analysis_start(event["AESTDTC"], person.start, imputation)
            kinds = {"ANY"}
            if event.get("AEREL") in related:
                kinds.add("RELATED")
            if event.get("AESER") == "Y":
                kinds.add("SERIOUS")
            if event.get("AEACN") == "DRUG WITHDRAWN":
                kinds.add("DISCONTINUATION")
            if event.get("AEACN") in DOSE_MODIFIED:
                kinds.add("DOSE_MODIFIED")
            if event.get("AESDTH") == "Y":
                kinds.add("FATAL")
            if "RELATED" in kinds and "SERIOUS" in kinds:
                kinds.add("SERIOUS_RELATED")
            if "RELATED" in kinds and "FATAL" in kinds:
                kinds.add("FATAL_RELATED")
            person.events.append({"seq": event["AESEQ"], "start": start, "kinds": kinds,
                                  "emergent": _emergent(person, event, start, values)})
        found.append(person)
    return found


# ---- the table ---------------------------------------------------------------------------


def rounded(value: Fraction, decimals: int, rule: str) -> str:
    """An exact fraction as text with `decimals` decimals (tfl.rounding.rule)."""
    if rule not in ("half_away_from_zero", "half_even"):
        raise CannotCalculate(f"tfl.rounding.rule: {rule}")
    scaled = value * 10 ** decimals
    whole, rest = divmod(scaled.numerator, scaled.denominator)   # value >= 0 here
    twice = 2 * rest
    if twice > scaled.denominator or (twice == scaled.denominator and (
            rule == "half_away_from_zero" or whole % 2 == 1)):
        whole += 1
    text = str(whole).rjust(decimals + 1, "0")
    return text if decimals == 0 else f"{text[:-decimals]}.{text[-decimals:]}"


def header_text(count: int) -> str:
    return f"(N={count})"


def cell_text(count: int, total: int, values: Values) -> str:
    """A count and its percentage, as the display shows them: "12 ( 37.5)" with one
    decimal, padded to the mask "XXX.X"; "12 (38)" with none, the mask "XXX" is not
    padded (display.pattern)."""
    show = values["tfl.percent.format"]["rule"]
    if show not in ("one_decimal_zero_blank", "one_decimal_always"):
        raise CannotCalculate(f"tfl.percent.format: {show}")
    if total == 0 or (count == 0 and show == "one_decimal_zero_blank"):
        return str(count)
    decimals = values["tfl.percent.format"]["decimals"]
    percent = rounded(Fraction(100 * count, total), decimals,
                      values["tfl.rounding.rule"]["rule"])
    return f"{count} ({percent.rjust(4 + decimals) if decimals else percent})"


def shown_rows(values: Values) -> list[str]:
    rule = values["tfl.ae.summary.rows"]
    if rule["rule"] == "standard_rows":
        return list(STANDARD_ROWS)
    if rule["rule"] == "stated_rows":
        return list(rule["rows"])
    raise CannotCalculate(f"tfl.ae.summary.rows: {rule['rule']}")


def column_order(labels: list[str], arms: list[Arm], rule: str) -> list[str]:
    """The treatment columns in the order of tfl.columns.arms.

    A label that names several arms stands where the first of them stands; a
    label that names none comes last. Equal places are ordered by the label.
    """
    if rule == "protocol_order":
        place = {arm.code: number for number, arm in enumerate(arms)}
    elif rule == "ascending_dose_placebo_first":
        ranked = sorted(arms, key=lambda arm: (arm.dose, arm.code))
        place = {arm.code: number for number, arm in enumerate(ranked)}
    else:
        raise CannotCalculate(f"tfl.columns.arms: {rule}")

    def key(label: str) -> tuple[int, str]:
        places = [place[arm.code] for arm in arms if label in arm.names]
        return (min(places) if places else len(arms), label)

    return sorted(labels, key=key)


def table(tables: Tables, values: Values, arms: list[Arm]) -> Table | None:
    """The adverse event summary of a study under a decision vector; None when it is
    not a planned output."""
    if values["tfl.output.include"]["rule"] == "not_included":
        return None
    population = values["tfl.population"]["rule"]
    flag = {"safety": "in_safety", "randomized": "in_randomized",
            "efficacy": "in_efficacy"}.get(population)
    if flag is None or (population == "efficacy" and values.get("pop.efficacy.rule") is None):
        raise CannotCalculate(f"tfl.population: {population}")
    # pop.safety.grouping: it holds for an output on the safety set; an output on
    # another analysis set groups by planned treatment.
    by_actual = population == "safety" and values["pop.safety.grouping"]["rule"] == "actual"
    members = [(person, person.actual if by_actual else person.planned)
               for person in people(tables, values) if getattr(person, flag)]
    # READING: a subject of the analysis set without a treatment in the grouping stands
    # in no column, the total column included ("pools all treatment arms"); and an arm
    # without a subject in the analysis set has no column. So a subject who is dosed
    # without being randomized is in no table by planned treatment.
    members = [(person, group) for person, group in members if group]
    if not members:
        raise CannotCalculate("no subject of the analysis set has a treatment: the table "
                              "has no treatment column")
    labels = column_order(sorted({group for _, group in members}), arms,
                          values["tfl.columns.arms"]["rule"])
    total = values["tfl.columns.total"]
    if total["rule"] == "all_arms":
        pooled = set(labels)
    elif total["rule"] == "active_arms":
        pooled = set(labels) - {total["control"]}
    elif total["rule"] == "none":
        pooled = None
    else:
        raise CannotCalculate(f"tfl.columns.total: {total['rule']}")
    groups: list[tuple[str, set[str]]] = [(label, {label}) for label in labels]
    if pooled is not None:
        groups.append((TOTAL_LABEL, pooled))
    sizes = [sum(1 for _, group in members if group in pool) for _, pool in groups]
    rows, counts = [], {"N": dict(zip([label for label, _ in groups], sizes, strict=True))}
    for code in shown_rows(values):
        texts, numbers = [], {}
        for (label, pool), size in zip(groups, sizes, strict=True):
            count = sum(1 for person, group in members if group in pool and any(
                event["emergent"] and code in event["kinds"] for event in person.events))
            texts.append(cell_text(count, size, values))
            numbers[label] = count
        rows.append((ROW_LABELS[code], texts))
        counts[code] = numbers
    return Table([label for label, _ in groups], [header_text(size) for size in sizes], rows,
                 counts)


def as_record(found: Table | None) -> dict:
    """A table as plain data, for a file of a kit."""
    if found is None:
        return {"included": False}
    return {"included": True, "columns": found.columns, "header": found.header,
            "rows": [{"label": label, "cells": texts} for label, texts in found.rows],
            "counts": found.counts}
