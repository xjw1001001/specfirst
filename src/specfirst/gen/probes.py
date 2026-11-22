"""Probe recipes (PLAN.md section 6.5, stage S3).

A probe is a planted subject or record on which two alternatives of one
decision give different results. The recipes are those of the catalog
(standard/catalog@<n>/probes.yaml); this module implements the ones that the
decisions of a list of units need, and can find each one again in the SDTM
that was written.

Where a probe lives:

    planted     one or more extra subjects, made for this probe alone
    base        a property that the base process gives the data anyway
    design      a property of the design, shared by both datasets
    structural  nothing in the data: the outputs differ for any data
    counts      numbers of subjects in one arm, set after everything else

The twin carries every probe. The visible data carry a sampled part of the
planted probes and of the count probes; the other kinds cannot be left out.

Some recipes depend on a value that a decision would state (the length of
the emergence window, the vital sign of a population rule). `Parameters`
takes these values from the design; the log of probes repeats them, so
that the decisions of a kit can be sampled to fit (gen-2).

The count probes hold for the house defaults: columns by actual treatment
(DM.ACTARM) on the safety set. They use one arm, the placebo arm, which no
planted subject has as its actual arm.

What a probe promises, and what it does not. A recipe plants the pattern of
the catalog in SDTM, and where the two alternatives differ in whether an
adverse event is treatment-emergent, an event in the interval where they
disagree. Whether the difference reaches the one output of the slice, the
adverse event summary, depends for most decisions on the values of other
decisions (the analysis set of the table, the rows it shows, an emergence
window): `REACHES` says which, as a condition that `reaches` evaluates on a
decision vector, and every line of the log repeats it. That is a
prediction; gen-2 verifies it by mutation (property P4).
"""

from __future__ import annotations

import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from itertools import combinations

from specfirst.compile import catalog as catalogs
from specfirst.compile import predicate
from specfirst.gen import GENERATOR, subjects
from specfirst.gen import design as designs
from specfirst.gen.rng import Stream
from specfirst.gen.subjects import DAY, Disposition, Dose, Event, Subject, Visit

Date = datetime.date

# The units of the slice "adverse event summary first" (docs/decisions/ADR-005.md).
SLICE_UNITS = ("mod-treatment", "mod-populations", "mod-ae-emergence", "tfl-ae-summary")

# When a difference between two alternatives of a decision reaches the adverse
# event summary (unit tfl-ae-summary). Per entry:
#
#     when    a condition on the decision vector of the study; it holds for every
#             pair of alternatives of the entry
#     pairs   "<alternative>|<alternative>" -> a further condition for that pair
#     note    words for a reader of the log
#
# A condition is one of
#
#     {"always": true}, {"never": true}
#     {"all_of": [...]}, {"any_of": [...]}, {"none_of": [...]}
#     {"decision": <entry>, "is": [<alternative>, ...]}
#         and with it "slot": <name>, "equals": <value>, where the value
#         "parameters.<key>" stands for that key of the `parameters` of the log
#     {"rows": [<code>, ...]}   the table shows at least one of these rows
#
# A decision of a table family is the one of the adverse event summary. A
# decision the vector does not hold has its house default. The conditions are
# predicted from the templates of the catalog and the house standard; gen-2
# verifies them by mutation (`reaches` below evaluates one).
_ROW_ANY = {"rows": ["ANY"]}
_ROW_EVENT = {"rows": ["ANY", "SERIOUS"]}
_BY_ACTUAL = {"all_of": [{"decision": "tfl.population", "is": ["safety"]},
                         {"decision": "pop.safety.grouping", "is": ["actual"]}]}
_READS_PLANNED = {"any_of": [
    {"decision": "tfl.population", "is": ["randomized", "efficacy"]},
    {"decision": "pop.safety.grouping", "is": ["planned"]},
    {"decision": "trt.actual.source", "is": ["same_as_planned"]}]}
# The analysis set of the table holds every randomized subject who was dosed, so a
# planted subject is in it whatever else the probe did to it (an early stop, a missing
# value). The efficacy-evaluable set and a randomized set that asks for a post-baseline
# value leave some planted subjects out.
_ANALYZED = {"any_of": [
    {"decision": "tfl.population", "is": ["safety"]},
    {"all_of": [{"decision": "tfl.population", "is": ["randomized"]},
                {"decision": "pop.randomized.rule", "is": ["all_randomized"]}]}]}
_WINDOW = {"decision": "ae.teae.end", "is": ["last_dose_plus_days"], "slot": "days",
           "equals": "parameters.window_days"}
_TREATMENT_RECORD = {"decision": "disp.status.record",
                     "is": ["disposition_event_by_subcategory"], "slot": "subcategory",
                     "equals": "parameters.treatment_subcategory"}
_STUDY_RECORD = {"decision": "disp.status.record",
                 "is": ["disposition_event_by_subcategory"], "slot": "subcategory",
                 "equals": "parameters.study_subcategory"}
_ONE_EVENT = ("the alternatives differ in one planted event, mild and not serious, of a "
              "subject who is randomized and dosed: the table must show the row ANY, on an "
              "analysis set that holds every such subject")
REACHES: dict[str, dict] = {
    "trt.planned.source": {
        "when": _READS_PLANNED,
        "note": "the table reads planned treatment only then"},
    "trt.actual.source": {
        "when": _BY_ACTUAL,
        "note": "the table reads actual treatment only on the safety set grouped by it"},
    "trt.start.source": {"when": {"all_of": [_ROW_ANY, _ANALYZED]}, "note": _ONE_EVENT},
    "trt.end.source": {
        "when": {"all_of": [_WINDOW, _ROW_EVENT, _ANALYZED]},
        "pairs": {"last_ex_end_date|ds_date_when_ex_missing": {"none_of": [_TREATMENT_RECORD]}},
        "note": "only an emergence window reads the treatment end date, and the planted "
                "events lie parameters.window_days + 2 days after the disposition date and "
                "after the last record with a dose: a window of exactly "
                "parameters.window_days days separates every pair. The subject without an "
                "exposure end date stops early, and it has no treatment record: with the "
                "subcategory of that record as the end-of-study record it has no "
                "disposition date to stand in for the missing end date"},
    "trt.date.imputation": {"when": {"all_of": [_ROW_ANY, _ANALYZED]}, "note": _ONE_EVENT},
    "date.studyday.origin": {
        "when": {"never": True},
        "note": "no row of the adverse event summary reads a study day; ASTDY and AENDY of "
                "ADAE differ"},
    "pop.randomized.rule": {"when": {"decision": "tfl.population", "is": ["randomized"]}},
    "pop.safety.rule": {
        "when": {"all_of": [_BY_ACTUAL, {"decision": "trt.actual.source",
                                          "is": ["dm_actarm", "first_ex_treatment"]}]},
        "note": "the subject who is dosed without being randomized has no planned "
                "treatment: it stands in a column of the table only by actual treatment"},
    "pop.safety.grouping": {
        "when": {"all_of": [{"decision": "tfl.population", "is": ["safety"]},
                            {"none_of": [{"decision": "trt.actual.source",
                                          "is": ["same_as_planned"]}]}]}},
    "pop.efficacy.rule": {"when": {"decision": "tfl.population", "is": ["efficacy"]}},
    "disp.status.record": {
        "when": {"all_of": [_ROW_EVENT, _ANALYZED, {"none_of": [_STUDY_RECORD]}, _WINDOW,
                            {"decision": "trt.end.source", "is": ["ds_date_when_ex_missing"]}]},
        "note": "the last disposition event of the planted subject is its study "
                "participation record: the two alternatives differ for the subcategory "
                "parameters.treatment_subcategory only, and a study whose end-of-study "
                "record is the one with parameters.study_subcategory has no probe"},
    "ae.start.imputation": {
        "when": {"all_of": [_ROW_ANY, _ANALYZED]},
        "pairs": {"first_of_month_not_before_first_dose|first_of_month": {"none_of": [
            {"decision": "ae.teae.start", "is": ["at_or_after_first_dose_time"]}]}},
        "note": _ONE_EVENT + "; an event completed to the first day of the month of the first "
                "dose is before the dose by date and by time alike"},
    "ae.teae.start": {"when": {"all_of": [_ROW_ANY, _ANALYZED]}, "note": _ONE_EVENT},
    "ae.teae.end": {
        "when": {"all_of": [_ROW_EVENT, _ANALYZED]},
        "note": "a window is one of parameters.window_days days; a window that is longer "
                "or shorter may leave the planted events on one side"},
    "ae.related.values": {"when": {"all_of": [{"rows": ["RELATED"]}, _ANALYZED]}},
    "tfl.output.include": {"when": {"always": True}},
    "tfl.population": {"when": {"always": True}},
    "tfl.columns.arms": {
        "when": {"none_of": [{"all_of": [_BY_ACTUAL, {"decision": "trt.actual.source",
                                                       "is": ["first_ex_treatment"]}]}]},
        "note": "by the treatment of the first exposure record the active arms share one "
                "column, and a protocol that lists the placebo arm first then has the "
                "columns of the dose order"},
    "tfl.columns.total": {"when": {"always": True}},
    "tfl.percent.format": {
        "when": {"rows": ["FATAL"]},
        "note": "the zero count is the count of fatal events in one arm"},
    "tfl.rounding.rule": {
        "when": {"all_of": [_ROW_EVENT,
                            {"decision": "tfl.population", "is": ["safety"]},
                            {"decision": "pop.safety.grouping", "is": ["actual"]},
                            {"decision": "trt.actual.source", "is": ["dm_actarm"]}]},
        "note": "the counts of one arm are set for these decisions"},
    "tfl.ae.summary.rows": {"when": {"always": True}},
}
# tfl.ae.summary.rows/standard_rows (catalog@2): the rows of the ARS example, in its order.
_ALL_ROWS = ("ANY", "RELATED", "SERIOUS", "SERIOUS_RELATED", "FATAL", "DISCONTINUATION")


def shown_rows(value: dict | None) -> tuple[str, ...]:
    """The rows of the adverse event summary that a value of tfl.ae.summary.rows shows."""
    if value is None or value.get("rule") == "standard_rows":
        return _ALL_ROWS
    return tuple(value.get("rows") or ())


def holds(condition: dict, values: dict[str, dict], parameters: dict) -> bool:
    """Whether a condition of `REACHES` holds for a decision vector.

    `values` maps an entry to its value, for a table family that of the
    adverse event summary; `parameters` is the record of that name in a
    line of the log of probes.
    """
    if "always" in condition:
        return True
    if "never" in condition:
        return False
    if "all_of" in condition:
        return all(holds(item, values, parameters) for item in condition["all_of"])
    if "any_of" in condition:
        return any(holds(item, values, parameters) for item in condition["any_of"])
    if "none_of" in condition:
        return not any(holds(item, values, parameters) for item in condition["none_of"])
    if "rows" in condition:
        return bool(set(condition["rows"]) & set(shown_rows(values.get("tfl.ae.summary.rows"))))
    if "decision" in condition:
        value = values.get(condition["decision"])
        if value is None or value.get("rule") not in condition["is"]:
            return False
        if "slot" not in condition:
            return True
        wanted = condition["equals"]
        if isinstance(wanted, str) and wanted.startswith("parameters."):
            wanted = parameters[wanted.split(".", 1)[1]]
        return value.get(condition["slot"]) == wanted
    raise ValueError(f"not a condition of REACHES: {condition}")


def reaches(entry_id: str, first: str, second: str, values: dict[str, dict],
            parameters: dict, table: dict[str, dict] | None = None) -> bool:
    """Whether a difference between two alternatives of a decision reaches the output.

    `table` is `REACHES`, or the field `reaches` of a line of the log.
    """
    reach = (REACHES if table is None else table)[entry_id]
    if not holds(reach["when"], values, parameters):
        return False
    for pair, condition in (reach.get("pairs") or {}).items():
        if set(pair.split("|")) == {first, second} and not holds(condition, values, parameters):
            return False
    return True


@dataclass
class Parameters:
    """Values of decision slots that the recipes are built around."""

    window_days: int            # ae.teae.end: days after the treatment end date
    tests: tuple[str, ...]      # pop.randomized.rule, pop.efficacy.rule: vital sign tests
    visits: tuple[str, ...]     # pop.efficacy.rule: every planned visit after day 1
    spared_arm: str             # the arm of the count probes
    treatment_subcategory: str = ""   # disp.status.record: DSSCAT of the treatment record
    study_subcategory: str = ""       # and of the study participation record

    @classmethod
    def of(cls, design: dict) -> Parameters:
        codes = [t["testCode"] for t in designs.vital_signs(design)
                 if len(t["encounterIds"]) > 1]
        preferred = [c for c in ("SYSBP", "WEIGHT") if c in codes] or codes
        later = [e["label"] for e in designs.encounters(design) if e["plannedDay"] > 1]
        names = design["collection"]["disposition"]["subcategories"]
        return cls(window_days=designs.follow_up_days(design), tests=tuple(preferred[:2]),
                   visits=tuple(later), spared_arm=designs.dose_order(design)[0],
                   treatment_subcategory=names["treatment"], study_subcategory=names["study"])

    def as_record(self) -> dict:
        return {"window_days": self.window_days, "tests": list(self.tests),
                "visits": list(self.visits), "spared_arm": self.spared_arm,
                "treatment_subcategory": self.treatment_subcategory,
                "study_subcategory": self.study_subcategory}


@dataclass
class Planted:
    probe: str
    where: str                        # planted | base | design | structural | counts
    keys: list[str] = field(default_factory=list)   # subject keys, for planted probes
    detail: dict = field(default_factory=dict)
    per_key: dict[str, dict] = field(default_factory=dict)   # what differs between subjects


@dataclass
class Planter:
    """What a recipe works with: the study so far and a way to add a subject."""

    ctx: subjects.Context
    people: list[Subject]
    rng: Stream
    parameters: Parameters
    span: int = 0

    def __post_init__(self) -> None:
        self.span = max((subjects.enrolment_end(self.people) - self.ctx.start).days, 30)
        order = designs.dose_order(self.ctx.design)
        self.others = [a for a in order if a != self.parameters.spared_arm]
        self.active = [a for a in order if not designs.is_placebo(self.ctx.design, a)]
        # The planned and the actual arm of the subject who is dosed off plan. Drawn here,
        # whether or not that probe is planted, because another recipe depends on it.
        if len(self.others) >= 2:
            planned, actual = self.rng.child("switch").sample(self.others, 2)
        else:
            planned, actual = self.parameters.spared_arm, self.others[0]
        self.switch = (planned, actual)

    def arm(self, probe: str, number: int = 1) -> str:
        """An arm for a planted subject: never the arm of the count probes."""
        return self.rng.child(probe, number, "arm").choice(self.others)

    def fresh(self, probe: str, number: int = 1, *, arm: str | None = None,
              need: Callable[[Date], bool] = lambda date: True, **forced: object) -> Subject:
        """A new subject without adverse events who completes the study, unless forced."""
        stream = self.rng.child(probe, number)
        first = self.ctx.start
        for _ in range(500):
            first = self.ctx.start + (30 + stream.between(0, self.span)) * DAY
            if need(first):
                break
        else:
            raise RuntimeError(f"probe {probe}: no first dose date fits")
        options = {"events": False, "complete": True, **forced}
        if "stop_day" in options:
            options.pop("complete")
        subject = subjects.simulate(self.ctx, stream, f"probe-{probe}-{number}", first,
                                    arm=arm or self.arm(probe, number), first_dose=first,
                                    **options)
        subject.probes.append(probe)
        self.people.append(subject)
        return subject

    def event(self, subject: Subject, start: Date, end: Date | None = None,
              **changes: object) -> Event:
        """A mild, unrelated event; ongoing when it has no end.

        No action is taken with a treatment that is not being given: before
        the first dose and after the last one the action is NOT APPLICABLE,
        as in the base process.
        """
        outcome = "RECOVERED/RESOLVED" if end else "NOT RECOVERED/NOT RESOLVED"
        last = subject.last_dose or subject.end_of_study
        on_treatment = subject.first_dose is not None and \
            subject.first_dose <= start <= (last or start)
        event = Event(term="Headache", start=start, end=end, severity="MILD", serious=False,
                      causality=self.ctx.scale[0],
                      action="DOSE NOT CHANGED" if on_treatment else "NOT APPLICABLE",
                      outcome=outcome)
        for name, value in changes.items():
            setattr(event, name, value)
        subject.events.append(event)
        return event


def split_first(subject: Subject, days: int = 3) -> tuple[Dose, Dose]:
    """Cut the first exposure record after `days` days; return both parts."""
    first = min(subject.doses, key=lambda d: d.start)
    cut = first.start + (days - 1) * DAY
    if first.end is None or first.end <= cut:
        raise RuntimeError("the first exposure record is too short to cut")
    rest = Dose(treatment=first.treatment, dose=first.dose, start=cut + DAY, end=first.end)
    first.end = cut
    subject.doses.append(rest)
    subject.doses.sort(key=lambda d: d.start)
    return first, rest


def split_last(subject: Subject, days: int = 3) -> tuple[Dose, Dose]:
    """Cut the last exposure record `days` days before its end; return both parts."""
    last = max(subject.doses, key=lambda d: d.start)
    if last.end is None or (last.end - last.start).days <= days:
        raise RuntimeError("the last exposure record is too short to cut")
    cut = last.end - days * DAY
    rest = Dose(treatment=last.treatment, dose=last.dose, start=cut + DAY, end=last.end)
    last.end = cut
    subject.doses.append(rest)
    subject.doses.sort(key=lambda d: d.start)
    return last, rest


def delay_end(subject: Subject, date: Date) -> None:
    """Move the end of the study, and the follow-up visit if there is one, to a later date."""
    old = subject.end_of_study
    for visit in subject.visits:
        if visit.date == old and visit.planned_day is not None and visit.planned_day > 1:
            visit.date = date
    for vital in subject.vitals:
        if vital.date == old:
            vital.date = date
    for item in subject.dispositions:
        if item.category == "DISPOSITION EVENT" and item.date == old:
            item.date = date
    subject.end_of_study = date


# -- planting ------------------------------------------------------------------


def _arm_label(p: Planter) -> Planted | None:
    arms = [a["name"] for a in designs.arms(p.ctx.design) if a["description"] != a["label"]]
    return Planted("arm_label_differs_from_decode", "design", detail={"arms": arms}) \
        if arms else None


def _actual_differs(p: Planter) -> Planted:
    probe = "actual_arm_differs_from_planned"
    planned, actual = p.switch
    subject = p.fresh(probe, arm=planned)
    subject.actual_arm = actual
    treatment, dose = p.ctx.treatment_of(actual)
    for record in subject.doses:
        record.treatment, record.dose = treatment, dose
    return Planted(probe, "planted", [subject.key], {"planned": planned, "actual": actual})


def _first_other(p: Planter) -> Planted:
    probe = "first_exposure_other_treatment"
    subject = p.fresh(probe, arm=p.rng.child(probe, "arm").choice(p.active))
    first, _ = split_first(subject)
    placebo = next(i["name"] for i in p.ctx.design["studyDesign"]["studyInterventions"]
                   if i["role"] == designs.PLACEBO_ROLE)
    first.treatment, first.dose = placebo, 0.0
    return Planted(probe, "planted", [subject.key], {"first_treatment": "PLACEBO"})


def _zero_dose(p: Planter) -> Planted:
    probe = "zero_dose_record_before_first_dose"
    subject = p.fresh(probe, arm=p.rng.child(probe, "arm").choice(p.active))
    first, rest = split_first(subject)
    # SDTM takes the first exposure record as the start of treatment (RFXSTDTC),
    # whatever its dose; which record starts treatment in analysis is a decision.
    first.dose = 0.0
    # An event during the days of dose zero, over before the first dose above zero:
    # emergent when treatment starts with the first record, not when it starts with a dose.
    p.event(subject, first.start + DAY, rest.start - DAY)
    return Planted(probe, "planted", [subject.key],
                   {"zero_dose_days": 3, "event_on_study_day": 2})


def _rfxstdtc(p: Planter) -> Planted:
    probe = "rfxstdtc_differs_from_exposure"
    subject = p.fresh(probe)
    earlier = subject.first_dose - DAY
    subject.first_exposure_text = earlier.isoformat()
    # An event that starts on the date of DM.RFXSTDTC, the day before the first exposure
    # record: emergent when that date starts treatment, not when the record does.
    p.event(subject, earlier, subject.first_dose + 2 * DAY)
    return Planted(probe, "planted", [subject.key],
                   {"days_earlier": 1, "event_on": earlier.isoformat()})


def _spans_days(p: Planter) -> Planted | None:
    count = sum(1 for s in p.people if s.doses
                and (last := max(s.doses, key=lambda d: d.start)).end is not None
                and last.end > last.start)
    return Planted("last_exposure_record_spans_days", "base", detail={"subjects": count}) \
        if count else None


def _no_end_date(p: Planter) -> Planted:
    probe = "no_exposure_end_date"
    stop = p.rng.child(probe, "stop").between(5, 10)
    subject = p.fresh(probe, stop_day=stop, reason="LOST TO FOLLOW-UP")
    for record in subject.doses:
        record.end = None
    subject.last_dose = None
    # An event later than the emergence window after the disposition date: emergent
    # while the subject has no treatment end date, not once the disposition date is one.
    # The event is serious, and the only serious event of a planted subject: where
    # another planted subject changes the other way in the same arm, the count of
    # subjects with any event stays the same; the count of subjects with a serious
    # event does not.
    days = p.parameters.window_days
    p.event(subject, subject.end_of_study + (days + 2) * DAY, None, serious=True,
            severity="MODERATE")
    return Planted(probe, "planted", [subject.key],
                   {"window_days": days, "event_days_after_disposition": days + 2,
                    "event_serious": True})


def _undosed_after_last(p: Planter) -> Planted:
    probe = "undosed_record_after_last_dose"
    subject = p.fresh(probe, arm=p.rng.child(probe, "arm").choice(p.active))
    last, rest = split_last(subject)
    # A record of dose zero, not placebo: no dose, as trt.start.source defines one.
    rest.dose = 0.0
    subject.last_dose = last.end
    # An event later than the window after the last record with a dose and within the
    # window after the record of dose zero: emergent when every record ends treatment.
    days = p.parameters.window_days
    start = last.end + (days + 2) * DAY
    delay_end(subject, max(subject.end_of_study, start + 3 * DAY))
    p.event(subject, start, start + 2 * DAY)
    return Planted(probe, "planted", [subject.key],
                   {"zero_dose_days": 3, "window_days": days,
                    "event_days_after_last_dose": days + 2})


def _partial_exposure(p: Planter) -> Planted:
    probe = "partial_exposure_date"
    subject = p.fresh(probe, need=lambda date: 4 <= date.day <= 24)
    first, rest = split_first(subject)
    month = first.start.isoformat()[:7]
    first.start_text, first.start_time = month, None
    subject.first_exposure_text = month
    subject.reference_start = subject.first_dose
    # An event between the first day of the month and the first complete start date, over
    # before that date: emergent when the partial date is completed, not when it is left out.
    p.event(subject, first.start + DAY, rest.start - DAY)
    return Planted(probe, "planted", [subject.key],
                   {"collected": month, "event_on": (first.start + DAY).isoformat()})


def _partial_not_earliest(p: Planter) -> Planted:
    probe = "partial_exposure_date_not_earliest"
    subject = p.fresh(probe, need=lambda date: date.day <= 12)
    _, rest = split_first(subject, days=4)
    cut = rest.start + 3 * DAY
    if rest.end is None or rest.end <= cut:
        raise RuntimeError("the exposure of the probe subject is too short")
    last = Dose(treatment=rest.treatment, dose=rest.dose, start=cut + DAY, end=rest.end)
    rest.end = cut
    rest.start_text = rest.start.isoformat()[:7]
    rest.end_text = rest.end.isoformat()[:7]
    subject.doses.append(last)
    subject.doses.sort(key=lambda d: d.start)
    return Planted(probe, "planted", [subject.key], {"collected": rest.start_text})


def _reference_start(p: Planter) -> Planted:
    probe = "reference_start_before_first_dose"
    subject = p.fresh(probe)
    days = p.rng.child(probe, "days").between(1, 3)
    subject.reference_start = subject.first_dose - days * DAY
    subject.randomized_on = subject.reference_start
    for item in subject.dispositions:
        if item.decod == "RANDOMIZED":
            item.date = subject.reference_start
    # An event, so that a study day exists that the two origins number differently.
    start = subject.first_dose + 3 * DAY
    p.event(subject, start, start + 2 * DAY)
    return Planted(probe, "planted", [subject.key], {"days_before": days})


def _without_postbaseline(p: Planter) -> Planted:
    probe = "randomized_without_postbaseline_value"
    keys: list[str] = []
    tests: dict[str, dict] = {}
    for number, test in enumerate(p.parameters.tests, start=1):
        subject = p.fresh(probe, number)
        subject.vitals = [v for v in subject.vitals
                          if not (v.code == test and v.date > subject.first_dose)]
        keys.append(subject.key)
        tests[subject.key] = {"test": test}
    return Planted(probe, "planted", keys, per_key=tests)


def _not_randomized(p: Planter) -> Planted:
    probe = "dosed_but_not_randomized"
    subject = p.fresh(probe, state="not_assigned",
                      arm=p.rng.child(probe, "arm").choice(p.active))
    return Planted(probe, "planted", [subject.key], {"actual": subject.actual_arm})


def _never_dosed(p: Planter) -> Planted:
    probe = "randomized_never_dosed"
    # Planned for the planned arm of the subject who is dosed off plan. Three planted
    # subjects move between the safety set and the randomized set (this one, the one
    # dosed off plan, the one dosed without being randomized); with arms drawn freely
    # they can leave every column with the same count in both sets.
    subject = p.fresh(probe, dosed=False, arm=p.switch[0])
    return Planted(probe, "planted", [subject.key], {"planned": subject.planned_arm})


def _visit_missed(p: Planter) -> Planted:
    probe = "postbaseline_value_but_visit_missed"
    subject = p.fresh(probe, stop_day=9, reason="WITHDRAWAL BY SUBJECT")
    visit = Visit(number=2.1, name="UNSCHEDULED 2.1", planned_day=None,
                  date=subject.first_dose + 5 * DAY)
    subject.visits.append(visit)
    subject.vitals += subjects.measure(p.rng.child(probe, "vitals"), p.ctx, subject, visit)
    return Planted(probe, "planted", [subject.key],
                   {"tests": list(p.parameters.tests), "visits": list(p.parameters.visits)})


def _other_test_only(p: Planter) -> Planted:
    probe = "baseline_value_of_other_test_only"
    keys: list[str] = []
    tests: dict[str, dict] = {}
    for number, test in enumerate(p.parameters.tests, start=1):
        subject = p.fresh(probe, number)
        subject.vitals = [v for v in subject.vitals
                          if not (v.code == test and v.date <= subject.first_dose)]
        keys.append(subject.key)
        tests[subject.key] = {"test_without_baseline": test}
    return Planted(probe, "planted", keys, per_key=tests)


def _two_dispositions(p: Planter) -> Planted:
    probe = "two_disposition_events"
    stop = p.rng.child(probe, "stop").between(12, 20)
    subject = p.fresh(probe, stop_day=stop, reason="PHYSICIAN DECISION")
    names = p.ctx.design["collection"]["disposition"]["subcategories"]
    subject.dispositions = [d for d in subject.dispositions if d.category != "DISPOSITION EVENT"]
    subject.dispositions += [
        Disposition("DISPOSITION EVENT", "PHYSICIAN DECISION", subject.last_dose,
                    names["treatment"]),
        Disposition("DISPOSITION EVENT", "COMPLETED", subject.end_of_study, names["study"]),
    ]
    return Planted(probe, "planted", [subject.key], {"subcategories": [names["treatment"],
                                                                         names["study"]]})


def _partial_ae_in_month(p: Planter) -> Planted:
    probe = "partial_ae_start_in_month_of_first_dose"
    subject = p.fresh(probe, need=lambda date: 5 <= date.day <= 20)
    start = subject.first_dose + 2 * DAY
    p.event(subject, start, start + 4 * DAY, start_text=start.isoformat()[:7])
    return Planted(probe, "planted", [subject.key], {"collected": start.isoformat()[:7]})


def _partial_ae_before_month(p: Planter) -> Planted:
    probe = "partial_ae_start_before_month_of_first_dose"
    subject = p.fresh(probe, need=lambda date: date.day <= 3)
    start = subject.consent
    if start.isoformat()[:7] >= subject.first_dose.isoformat()[:7]:
        raise RuntimeError("the screening of the probe subject is in the month of the dose")
    p.event(subject, start, None, start_text=start.isoformat()[:7])
    return Planted(probe, "planted", [subject.key], {"collected": start.isoformat()[:7]})


def _on_first_dose_date(p: Planter) -> Planted:
    probe = "ae_on_first_dose_date_without_time"
    subject = p.fresh(probe)
    p.event(subject, subject.first_dose, subject.first_dose + 3 * DAY)
    return Planted(probe, "planted", [subject.key], {"dose_time": subject.first_dose_time})


def _timed_before_dose(p: Planter) -> Planted:
    probe = "ae_timed_before_timed_first_dose"
    subject = p.fresh(probe)
    # The first dose is given between 08:00 and 11:45 (specfirst.gen.subjects): the
    # event starts two hours earlier on that day, with its time collected.
    hour, minute = (int(part) for part in subject.first_dose_time.split(":"))
    before = f"{hour - 2:02d}:{minute:02d}"
    p.event(subject, subject.first_dose, subject.first_dose + 3 * DAY,
            start_text=f"{subject.first_dose.isoformat()}T{before}")
    return Planted(probe, "planted", [subject.key],
                   {"dose_time": subject.first_dose_time, "event_time": before})


def _after_window(p: Planter) -> Planted:
    probe = "ae_starts_after_emergence_window"
    days = p.parameters.window_days
    keys: list[str] = []
    after: dict[str, dict] = {}
    # Two subjects, so that the table counts each event: one event on the last day of
    # the window, one on the day after it.
    for number, offset in enumerate((days, days + 1), start=1):
        subject = p.fresh(probe, number)
        delay_end(subject, subject.last_dose + (days + 3) * DAY)
        p.event(subject, subject.last_dose + offset * DAY, None)
        keys.append(subject.key)
        after[subject.key] = {"days_after_last_dose": offset}
    return Planted(probe, "planted", keys, {"window_days": days}, after)


def _each_causality(p: Planter) -> Planted:
    probe = "ae_with_each_causality_value"
    keys: list[str] = []
    values: dict[str, dict] = {}
    for number, value in enumerate(p.ctx.scale, start=1):
        subject = p.fresh(probe, number, arm=p.others[(number - 1) % len(p.others)])
        start = subject.first_dose + 5 * DAY
        p.event(subject, start, start + 2 * DAY, causality=value)
        keys.append(subject.key)
        values[subject.key] = {"value": value}
    return Planted(probe, "planted", keys, {"values": list(p.ctx.scale)}, values)


def _without_any_postbaseline(p: Planter) -> Planted:
    probe = "dosed_without_postbaseline_value"
    stop = p.rng.child(probe, "stop").between(3, 5)
    subject = p.fresh(probe, stop_day=stop, reason="WITHDRAWAL BY SUBJECT")
    return Planted(probe, "planted", [subject.key])


def _treated(p: Planter, arm: str) -> list[Subject]:
    return [s for s in p.people if s.actual_arm == arm and s.first_dose is not None]


def _emergent(subject: Subject) -> list[Event]:
    """Events of a base subject that start on or after the day of the first dose."""
    return [e for e in subject.events if e.start >= subject.first_dose]


def _zero_count(p: Planter) -> Planted | None:
    arm = p.parameters.spared_arm
    people = [s for s in p.people if arm in (s.planned_arm, s.actual_arm)]
    if any(e.fatal for s in people for e in s.events):
        raise RuntimeError("a subject of the spared arm has a fatal event")
    return Planted("category_with_zero_count", "counts", detail={
        "arm": arm, "category": "fatal adverse event", "count": 0,
        "assumes": {"tfl.ae.summary.rows": "shows FATAL"}})


def is_rounding_half(count: int, total: int) -> bool:
    """Whether 100 * count / total ends in .25: halfway at one decimal, even digit before.

    Only quarters are exact in binary floating point; a value such as 3.15
    is not, and would not sit exactly on the half.
    """
    return total > 0 and (400 * count) % total == 0 and ((400 * count) // total) % 4 == 1


def _rounding_half(p: Planter) -> Planted:
    probe = "statistic_at_rounding_half"
    arm = p.parameters.spared_arm
    people = _treated(p, arm)
    total = len(people)
    if total % 16 != 0:
        raise RuntimeError(f"arm {arm} has {total} treated subjects, not a multiple of 16")
    unit = total // 16
    rng = p.rng.child(probe)

    # Serious events: exactly one subject in sixteen.
    serious = [s for s in people if any(e.serious for e in _emergent(s))]
    for subject in rng.child("less-serious").shuffled(serious)[unit:]:
        for event in subject.events:
            event.serious = False
    lacking = unit - min(len(serious), unit)
    plain = [s for s in people if _emergent(s) and not any(e.serious for e in s.events)]
    for subject in rng.child("more-serious").shuffled(plain)[:lacking]:
        _emergent(subject)[0].serious = True
    lacking -= min(lacking, len(plain))
    quiet = [s for s in people if not _emergent(s) and (s.last_dose - s.first_dose).days >= 3]
    for subject in rng.child("new-serious").shuffled(quiet)[:lacking]:
        p.event(subject, subject.first_dose + 2 * DAY, subject.first_dose + 4 * DAY,
                serious=True, severity="SEVERE")

    # Any event: 5, 9 or 13 subjects in sixteen, whichever is nearest.
    having = [s for s in people if _emergent(s)]
    target = min((5 * unit, 9 * unit, 13 * unit), key=lambda t: (abs(t - len(having)), t))
    removable = [s for s in having
                 if not any(e.serious or e.action == "DRUG WITHDRAWN" for e in s.events)]
    for subject in rng.child("fewer").shuffled(removable)[:max(len(having) - target, 0)]:
        subject.events = [e for e in subject.events if e.start <= subject.first_dose]
    quiet = [s for s in people if not _emergent(s) and (s.last_dose - s.first_dose).days >= 3]
    for subject in rng.child("more").shuffled(quiet)[:max(target - len(having), 0)]:
        p.event(subject, subject.first_dose + 2 * DAY, subject.first_dose + 4 * DAY)
    having = [s for s in people if _emergent(s)]
    serious = [s for s in people if any(e.serious for e in _emergent(s))]
    if not is_rounding_half(len(serious), total) or not is_rounding_half(len(having), total):
        raise RuntimeError(f"arm {arm}: {len(having)} and {len(serious)} of {total} subjects "
                           "do not give a percentage at a rounding half")
    return Planted(probe, "counts", detail={
        "arm": arm, "subjects": total, "with_any_event": len(having),
        "with_serious_event": len(serious),
        "percent": [100.0 * len(having) / total, 100.0 * len(serious) / total],
        "assumes": {"tfl.population": "safety", "pop.safety.grouping": "actual",
                    "trt.actual.source": "dm_actarm",
                    "tfl.ae.summary.rows": "shows ANY or SERIOUS"}})


# probe ID -> recipe; a planted or count probe can be left out of the visible data.
RECIPES: dict[str, Callable[[Planter], Planted | None]] = {
    "arm_label_differs_from_decode": _arm_label,
    "actual_arm_differs_from_planned": _actual_differs,
    "first_exposure_other_treatment": _first_other,
    "zero_dose_record_before_first_dose": _zero_dose,
    "rfxstdtc_differs_from_exposure": _rfxstdtc,
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
    # After every planted subject exists:
    "last_exposure_record_spans_days": _spans_days,
    "category_with_zero_count": _zero_count,
    "statistic_at_rounding_half": _rounding_half,
}
# Probes that cannot be left out of a dataset: they are in the design or in the base process.
ALWAYS = ("arm_label_differs_from_decode", "last_exposure_record_spans_days")
# Probes with nothing in the data, by their kind in the catalog.
WITHOUT_DATA = ("structural", "design")


def slice_entries(catalog: catalogs.Catalog, design: dict,
                  units: tuple[str, ...] = SLICE_UNITS) -> list[catalogs.Entry]:
    """The entries of the units that apply to the design."""
    features = designs.features(design)
    return [entry for entry in catalog.entries.values()
            if set(entry.units) & set(units)
            and predicate.evaluate(predicate.parse(entry.applies_when), features)]


def needed(catalog: catalogs.Catalog, design: dict,
           units: tuple[str, ...] = SLICE_UNITS) -> list[str]:
    """The probes that the applicable decisions of the units list, in catalog order."""
    wanted = {probe for entry in slice_entries(catalog, design, units) for probe in entry.probes}
    return [probe for probe in catalog.probes if probe in wanted]


def chosen(catalog: catalogs.Catalog, design: dict, rng: Stream, share: float,
           units: tuple[str, ...] = SLICE_UNITS) -> list[str]:
    """The probes of one dataset: all of them for a share of 1, else a sampled part."""
    picked = []
    for probe in needed(catalog, design, units):
        kind = catalog.probes[probe].get("kind")
        if kind in WITHOUT_DATA or probe in ALWAYS:
            picked.append(probe)
        elif probe not in RECIPES:
            raise KeyError(f"no recipe for the probe '{probe}'")
        elif share >= 1.0 or rng.child("sample", probe).chance(share):
            picked.append(probe)
    return picked


def spared_arm(design: dict, picked: list[str]) -> str | None:
    """The arm in which the base process lets nobody die, when a chosen probe asks for it."""
    return Parameters.of(design).spared_arm if "category_with_zero_count" in picked else None


def plant(ctx: subjects.Context, catalog: catalogs.Catalog, people: list[Subject], rng: Stream,
          picked: list[str]) -> list[Planted]:
    """Plant the chosen probes into the subjects of one dataset, in the order of RECIPES."""
    planter = Planter(ctx, people, rng, Parameters.of(ctx.design))
    planted = []
    for probe in picked:
        kind = catalog.probes[probe].get("kind")
        if kind in WITHOUT_DATA:
            planted.append(Planted(probe, str(kind)))
    for probe, recipe in RECIPES.items():
        if probe in picked:
            result = recipe(planter)
            if result is not None:
                planted.append(result)
    return planted


def alternatives_of(entry: catalogs.Entry, design: dict) -> list[str]:
    """The alternatives of a decision that a study of this design can choose.

    The catalog says per entry when a decision applies, not per alternative.
    One alternative of the slice needs more than its entry does: a table on
    the efficacy-evaluable set needs a design that has such a set.
    """
    ids = [alternative.id for alternative in entry.alternatives]
    if entry.id == "tfl.population" and not designs.features(design)["design.has_efficacy_set"]:
        ids.remove("efficacy")
    return ids


def pairs_of(entry: catalogs.Entry, design: dict) -> list[tuple[str, str]]:
    """Every pair of alternatives of a decision that a probe has to separate."""
    return list(combinations(alternatives_of(entry, design), 2))


def claimed_pairs(catalog: catalogs.Catalog, design: dict, probe: str) -> dict[str, list[list]]:
    """What the catalog says a probe separates: entry -> pairs, for the pairs of this design."""
    claims = {}
    for entry_id, claimed in (catalog.probes[probe].get("separates") or {}).items():
        entry = catalog.entry(entry_id)
        possible = pairs_of(entry, design)
        if claimed == "all":
            pairs = possible
        else:
            wanted = [frozenset(pair) for pair in claimed or []]
            pairs = [pair for pair in possible if frozenset(pair) in wanted]
        claims[entry_id] = [list(pair) for pair in pairs]
    return claims


def log(design: dict, catalog: catalogs.Catalog, which: str, planted: list[Planted],
        people: list[Subject]) -> list[dict]:
    """The lines of probes.jsonl for one dataset. Subjects must carry their identifiers."""
    by_key = {subject.key: subject.usubjid for subject in people}
    parameters = Parameters.of(design).as_record()
    order = list(catalog.probes)
    records = []
    for item in sorted(planted, key=lambda p: order.index(p.probe)):
        recipe = catalog.probes[item.probe]
        separates = claimed_pairs(catalog, design, item.probe)
        served = [*separates, *(recipe.get("varies") or {}), *(recipe.get("stresses") or [])]
        records.append({
            "catalog": f"{catalog.name} {catalog.version}",
            "generator": GENERATOR,
            "study": designs.study_id(design),
            "data": which,
            "probe": item.probe,
            "kind": recipe.get("kind"),
            "where": item.where,
            "domains": list(recipe.get("domains") or []),
            "separates": separates,
            "varies": dict(recipe.get("varies") or {}),
            "stresses": list(recipe.get("stresses") or []),
            "reaches": {entry_id: REACHES[entry_id] for entry_id in dict.fromkeys(served)
                        if entry_id in REACHES},
            "subjects": sorted(by_key[key] for key in item.keys),
            "by_subject": {by_key[key]: value for key, value in sorted(item.per_key.items())},
            "detail": item.detail,
            "parameters": parameters,
        })
    return records
