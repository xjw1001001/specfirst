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

The probes follow the decisions of the study (section 6.4: stage S1 before
S3; gen-2b, docs/decisions/ADR-023.md). The decision vector is drawn
first; the recipes then plant for it:

- the count probes are set for the column of the placebo arm under the
  analysis set, the grouping and the number of decimals of the kit's own
  table, by the hand calculation (`specfirst.gen.reference`), with planted
  subjects of that arm added until the column has a size for which a
  rounding half exists;
- a planted subject that carries the event of a probe lies inside the
  analysis set of the table (the subject without an exposure end date
  completes its treatment when the set asks for a later visit or value; the
  subject with a partial first exposure date has a value of the test before
  the month of its first dose when the set asks for a baseline value);
- the window probes are built around the kit's own emergence window;
- the events of the causality probe are serious when the table shows
  serious related events and not related events.

`Parameters` holds the values the recipes are built around; the log of
probes repeats them. `Parameters.of` gives those of a design, which the
decision sampler uses; `Parameters.of_kit` those of a design and a vector.

What a probe promises, and what it does not. A recipe plants the pattern of
the catalog in SDTM, and where the two alternatives differ in whether an
adverse event is treatment-emergent, an event in the interval where they
disagree. Whether the difference reaches the one output of the slice, the
adverse event summary, can depend on the values of other decisions: an
output that groups by planned treatment does not read actual treatment, an
output without an emergence window does not read the treatment end date.
`REACHES` names only such conditions: where one does not hold, the
alternatives give the same output on any data of the design that follow
SDTMIG v3.4 (kind (a) of finding G1 of the gen-2a review; the note of a row
names what it rests on).
Every other pair of a decision that the output reads must be separated on
the twin; gen-2 verifies that by mutation (property P4), and a kit in which
one is not is not written.
"""

from __future__ import annotations

import datetime
import functools
from collections.abc import Callable
from dataclasses import dataclass, field
from fractions import Fraction
from itertools import combinations

from specfirst.compile import catalog as catalogs
from specfirst.compile import house as houses
from specfirst.compile import predicate
from specfirst.gen import GENERATOR, subjects
from specfirst.gen import design as designs
from specfirst.gen.rng import Stream
from specfirst.gen.subjects import DAY, Disposition, Dose, Event, Subject, Visit

Date = datetime.date

# The units of the slice "adverse event summary first" (docs/decisions/ADR-005.md).
SLICE_UNITS = ("mod-treatment", "mod-populations", "mod-ae-emergence", "tfl-ae-summary")

# When the alternatives of a decision can differ in the adverse event summary (unit
# tfl-ae-summary) at all. Per entry:
#
#     when    a condition on the decision vector of the study; it holds for every
#             pair of alternatives of the entry
#     note    words for a reader of the log
#
# A condition is one of
#
#     {"always": true}, {"never": true}
#     {"all_of": [...]}, {"any_of": [...]}, {"none_of": [...]}
#     {"decision": <entry>, "is": [<alternative>, ...]}
#     {"rows": [<code>, ...]}   the table shows at least one of these rows
#     {"parameter": <key>}      that key of the `parameters` of the log is true
#
# A decision of a table family is the one of the adverse event summary. A
# decision the vector does not hold has its house default.
#
# Only one kind of condition stands here (gen-2b, the owner's answer of 2026-11-17 on
# finding G1 of the gen-2a review): where it does not hold, another decision of the
# kit makes the alternatives give the same output on ANY data. Where the data of a
# kit could separate the alternatives, the probes are planted so that they do; no
# condition here says that a probe does not work under some decisions. A kit whose
# twin leaves a pair unseparated that this table claims is not written, and the gate
# fails on it.
_BY_ACTUAL = {"all_of": [{"decision": "tfl.population", "is": ["safety"]},
                         {"decision": "pop.safety.grouping", "is": ["actual"]}]}
_READS_PLANNED = {"any_of": [
    {"decision": "tfl.population", "is": ["randomized", "efficacy"]},
    {"decision": "pop.safety.grouping", "is": ["planned"]},
    {"decision": "trt.actual.source", "is": ["same_as_planned"]}]}
_WINDOW = {"decision": "ae.teae.end", "is": ["last_dose_plus_days"]}
REACHES: dict[str, dict] = {
    "trt.planned.source": {
        "when": _READS_PLANNED,
        "note": "a table grouped by actual treatment does not read planned treatment"},
    "trt.actual.source": {
        "when": _BY_ACTUAL,
        "note": "only a table on the safety set grouped by actual treatment reads it"},
    "trt.start.source": {"when": {"always": True}},
    "trt.end.source": {
        "when": _WINDOW,
        "note": "only an emergence window reads the treatment end date"},
    "trt.date.imputation": {"when": {"always": True}},
    "date.studyday.origin": {
        "when": {"never": True},
        "note": "no row of the adverse event summary reads a study day; ASTDY and AENDY of "
                "ADAE differ"},
    "pop.randomized.rule": {
        "when": {"decision": "tfl.population", "is": ["randomized"]},
        "note": "only a table on the randomized set reads it"},
    "pop.safety.rule": {
        "when": {"all_of": [_BY_ACTUAL, {"decision": "trt.actual.source",
                                          "is": ["dm_actarm", "first_ex_treatment"]}]},
        "note": "the two rules differ in the subjects dosed without being randomized; "
                "such a subject has no planned arm (in a randomized design the arm is "
                "assigned at randomization: DM.ARMCD empty, ARMNRS NOT ASSIGNED, SDTMIG "
                "v3.4 DM; per recommendation, pending SME review), so it stands in a column "
                "only by actual treatment, and only a table on the safety set reads the rule"},
    "pop.safety.grouping": {
        "when": {"all_of": [{"decision": "tfl.population", "is": ["safety"]},
                            {"none_of": [{"decision": "trt.actual.source",
                                          "is": ["same_as_planned"]}]}]},
        "note": "only a table on the safety set reads it, and with actual treatment the "
                "same as planned the two groupings are one"},
    "pop.efficacy.rule": {
        "when": {"decision": "tfl.population", "is": ["efficacy"]},
        "note": "only a table on the efficacy-evaluable set reads it"},
    "disp.status.record": {
        "when": {"all_of": [_WINDOW, {"decision": "trt.end.source",
                                      "is": ["ds_date_when_ex_missing"]}]},
        "note": "the table reads the end-of-study date only where it stands in for a "
                "missing exposure end date, and only through an emergence window"},
    "ae.start.imputation": {"when": {"always": True}},
    "ae.teae.start": {"when": {"always": True}},
    "ae.teae.end": {"when": {"always": True}},
    "ae.related.values": {
        "when": {"rows": ["RELATED", "SERIOUS_RELATED", "FATAL_RELATED"]},
        "note": "a table without a row of related events does not read the causality"},
    "tfl.output.include": {"when": {"always": True}},
    "tfl.population": {"when": {"always": True}},
    "tfl.columns.arms": {
        "when": {"none_of": [{"all_of": [_BY_ACTUAL,
                                         {"decision": "trt.actual.source",
                                          "is": ["first_ex_treatment"]},
                                         {"parameter": "placebo_first"}]}]},
        "note": "by the treatment of the first exposure record the active arms share one "
                "column, and where the protocol lists the placebo arm first the two orders "
                "of the columns are one"},
    "tfl.columns.total": {"when": {"always": True}},
    "tfl.percent.format": {"when": {"always": True}},
    "tfl.rounding.rule": {"when": {"always": True}},
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
    if "parameter" in condition:
        return bool(parameters.get(condition["parameter"]))
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
    """Whether a difference between two alternatives of a decision can reach the output:
    no other decision of the vector makes them give the same output on any data that keep
    the premise of the row (its note; SDTMIG v3.4 for every row).

    `table` is `REACHES`, or the field `reaches` of a line of the log. The
    condition is the same for every pair of alternatives of the entry; `first`
    and `second` name the pair for the reader of a call.
    """
    reach = (REACHES if table is None else table)[entry_id]
    return holds(reach["when"], values, parameters)


@functools.lru_cache(maxsize=1)
def house_window() -> int | None:
    """The days of the default window of the house of the default pair (ae.teae.end), or
    None when its default has no window. The probes of the window are built around it, so
    that a kit that takes the default tells it apart (open-default@2: 30 days)."""
    catalog, house = houses.load_pair(None)
    value = houses.default_value(catalog, house, "ae.teae.end", "mod-ae-emergence")
    return value.get("days") if value and value.get("rule") == "last_dose_plus_days" else None


@dataclass
class Parameters:
    """Values of decision slots that the recipes are built around."""

    # ae.teae.end: days after the treatment end date. For a design: the house's default
    # window, or the follow-up length when the house has none. For a kit (`of_kit`): the
    # kit's own window, when it has one.
    window_days: int
    tests: tuple[str, ...]      # pop.randomized.rule, pop.efficacy.rule: vital sign tests
    visits: tuple[str, ...]     # pop.efficacy.rule: every planned visit after day 1
    spared_arm: str             # the arm of the count probes
    treatment_subcategory: str = ""   # disp.status.record: DSSCAT of the treatment record
    study_subcategory: str = ""       # and of the study participation record
    follow_up_days: int = 0           # the follow-up length of the design: a stated window
    placebo_first: bool = False       # the protocol lists the placebo arm first

    @classmethod
    def of(cls, design: dict) -> Parameters:
        """The values of a design: what the decision sampler offers (stage S1)."""
        codes = [t["testCode"] for t in designs.vital_signs(design)
                 if len(t["encounterIds"]) > 1]
        preferred = [c for c in ("SYSBP", "WEIGHT") if c in codes] or codes
        later = [e["label"] for e in designs.encounters(design) if e["plannedDay"] > 1]
        names = design["collection"]["disposition"]["subcategories"]
        follow_up = designs.follow_up_days(design)
        listed = [arm["name"] for arm in designs.arms(design)]
        return cls(window_days=house_window() or follow_up, tests=tuple(preferred[:2]),
                   visits=tuple(later), spared_arm=designs.dose_order(design)[0],
                   treatment_subcategory=names["treatment"], study_subcategory=names["study"],
                   follow_up_days=follow_up,
                   placebo_first=listed[0] == designs.dose_order(design)[0])

    @classmethod
    def of_kit(cls, design: dict, values: dict[str, dict]) -> Parameters:
        """The values the probes of a study with this decision vector are built around: the
        window is the vector's own, when it has one (stage S3 after S1)."""
        found = cls.of(design)
        window = values.get("ae.teae.end") or {}
        if window.get("rule") == "last_dose_plus_days":
            found.window_days = window["days"]
        return found

    def as_record(self) -> dict:
        return {"window_days": self.window_days, "tests": list(self.tests),
                "visits": list(self.visits), "spared_arm": self.spared_arm,
                "treatment_subcategory": self.treatment_subcategory,
                "study_subcategory": self.study_subcategory,
                "follow_up_days": self.follow_up_days, "placebo_first": self.placebo_first}


@dataclass
class Planted:
    probe: str
    where: str                        # planted | base | design | structural | counts
    keys: list[str] = field(default_factory=list)   # subject keys, for planted probes
    detail: dict = field(default_factory=dict)
    per_key: dict[str, dict] = field(default_factory=dict)   # what differs between subjects


@dataclass
class Planter:
    """What a recipe works with: the study so far, the decision vector the probes follow,
    and a way to add a subject."""

    ctx: subjects.Context
    people: list[Subject]
    rng: Stream
    parameters: Parameters
    values: dict[str, dict] = field(default_factory=dict)
    span: int = 0

    def later_data_needed(self) -> bool:
        """Whether the analysis set of the table asks for more than a dose: a post-baseline
        value (the randomized set by that rule) or a value or visit after day 1 (the
        efficacy-evaluable set). A subject who stops early may then fall outside it."""
        population = (self.values.get("tfl.population") or {}).get("rule")
        if population == "efficacy":
            return True
        return population == "randomized" and (self.values.get("pop.randomized.rule") or {}) \
            .get("rule") == "randomized_with_postbaseline"

    def __post_init__(self) -> None:
        self.span = max((subjects.enrolment_end(self.people) - self.ctx.start).days, 30)
        order = designs.dose_order(self.ctx.design)
        self.others = [a for a in order if a != self.parameters.spared_arm]
        self.active = [a for a in order if not designs.is_placebo(self.ctx.design, a)]
        # The planned and the actual arm of the subject who is dosed off plan. Drawn here,
        # whether or not that probe is planted, because another recipe depends on it. With
        # one arm besides the arm of the count probes, one of the two is that arm: the one
        # the table does not group by, so that the subject stays out of the counted column
        # (a table by planned treatment counts it by its planned arm).
        if len(self.others) >= 2:
            planned, actual = self.rng.child("switch").sample(self.others, 2)
        elif self.by_actual():
            planned, actual = self.parameters.spared_arm, self.others[0]
        else:
            planned, actual = self.others[0], self.parameters.spared_arm
        self.switch = (planned, actual)

    def by_actual(self) -> bool:
        """Whether the table groups by actual treatment (the safety set grouped by it);
        without a vector, as the house default does."""
        if not self.values:
            return True
        return self.values["tfl.population"]["rule"] == "safety" and \
            self.values["pop.safety.grouping"]["rule"] == "actual"

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
    # The subject carries the event that separates the sources of the treatment end date,
    # so it lies inside the analysis set of the table. One who is lost to follow-up after
    # a few days has no later visit and no post-baseline value; where the set asks for
    # one, the subject completes its treatment and the follow-up instead.
    inside = p.later_data_needed()
    names = p.ctx.design["collection"]["disposition"]["subcategories"]
    record = p.values.get("disp.status.record") or {}
    by_subcategory = record.get("rule") == "disposition_event_by_subcategory"
    days = p.parameters.window_days
    keys: list[str] = []
    per_key: dict[str, dict] = {}

    def without_end(number: int, reason: str) -> Subject:
        if inside:
            subject = p.fresh(probe, number)
        else:
            subject = p.fresh(probe, number, stop_day=stop, reason=reason)
        for dose in subject.doses:
            dose.end = None
        return subject

    # An event later than the emergence window after the disposition date: emergent
    # while the subject has no treatment end date, not once the disposition date is one.
    # The event is serious, and so is that of the second subject below; no other planted
    # subject has a serious event: where another planted subject changes the other way
    # in the same arm, the count of subjects with any event stays the same; the count of
    # subjects with a serious event does not.
    subject = without_end(1, "LOST TO FOLLOW-UP")
    ended = subject.last_dose
    subject.last_dose = None
    if by_subcategory and record.get("subcategory") == names["treatment"]:
        # The end-of-study record of the kit is the treatment record (the limit (b)
        # lifted, gen-2b): the subject has one, on its last dose, and a study record at
        # least two days later; the event lies after the window that follows the
        # treatment record and inside the one that follows the study record, so the
        # record that is taken decides whether it is emergent.
        if subject.end_of_study < ended + 2 * DAY:
            delay_end(subject, ended + 3 * DAY)
        decod = next(d.decod for d in subject.dispositions if d.category == "DISPOSITION EVENT")
        subject.dispositions.append(Disposition("DISPOSITION EVENT", decod, ended,
                                                names["treatment"]))
        after, records = ended, ["treatment", "study"]
    else:
        after, records = subject.end_of_study, ["study"]
    p.event(subject, after + (days + 2) * DAY, None, serious=True, severity="MODERATE")
    keys.append(subject.key)
    per_key[subject.key] = {"records": records, "event_after": records[0]}
    if by_subcategory and record.get("subcategory") == names["study"]:
        # The end-of-study record of the kit is the study participation record (the limit
        # (c) lifted, gen-2b): it is the last disposition event of every subject. A second
        # subject without an exposure end date has stopped its treatment and is still in
        # the study: its one disposition event is the treatment record, and it has no
        # study-level record. The last disposition event gives it a date that stands in
        # for the missing end date; the study record gives none. (Per recommendation,
        # pending SME review: a subject who is still in the study has no study-level
        # disposition record; SDTMIG v3.4, section 6.2 DS.)
        other = without_end(2, "PHYSICIAN DECISION")
        stopped = other.last_dose
        other.last_dose = None
        decod = "COMPLETED" if inside else "PHYSICIAN DECISION"
        other.dispositions = [d for d in other.dispositions if d.category != "DISPOSITION EVENT"]
        other.dispositions.append(Disposition("DISPOSITION EVENT", decod, stopped,
                                              names["treatment"]))
        start = stopped + (days + 2) * DAY
        p.event(other, start, None, serious=True, severity="MODERATE")
        # The last contact: the report of the event.
        other.end_of_study = max(other.end_of_study, start + 3 * DAY)
        keys.append(other.key)
        per_key[other.key] = {"records": ["treatment"], "event_after": "treatment"}
    return Planted(probe, "planted", keys,
                   {"window_days": days, "event_days_after_disposition": days + 2,
                    "event_serious": True, "completes_treatment": inside}, per_key)


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
    # The subject carries the event of the probe, so it lies inside the analysis set of the
    # table when its partial date is completed to the first day of the month. Where the set
    # asks for a value of a test on or before the treatment start (the efficacy-evaluable
    # set by a baseline and a post-baseline value), the first dose falls on the second or
    # third day of a month: the screening visit, at least three days earlier, lies in the
    # month before, and its value of the test is a baseline value for the completed date
    # (gen-2b, finding H3 of its review).
    efficacy = p.values.get("pop.efficacy.rule") or {}
    test = efficacy.get("test") if (p.values.get("tfl.population") or {}).get("rule") == \
        "efficacy" and efficacy.get("rule") == "baseline_and_postbaseline" else None
    low, high = (2, 3) if test else (4, 24)
    subject = p.fresh(probe, need=lambda date: low <= date.day <= high)
    first, rest = split_first(subject)
    month = first.start.isoformat()[:7]
    if test and not any(v.code == test and v.date.isoformat()[:7] < month
                        for v in subject.vitals):
        raise RuntimeError(f"probe {probe}: no value of {test} before the month of the first dose")
    first.start_text, first.start_time = month, None
    subject.first_exposure_text = month
    subject.reference_start = subject.first_dose
    # An event between the first day of the month and the first complete start date, over
    # before that date: emergent when the partial date is completed, not when it is left out.
    p.event(subject, first.start + DAY, rest.start - DAY)
    return Planted(probe, "planted", [subject.key],
                   {"collected": month, "event_on": (first.start + DAY).isoformat(),
                    "value_before_month": test})


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
    # A mild event, emergent under every rule: other planted subjects without events move the
    # other way between the two rules of the efficacy-evaluable set (the one without a
    # baseline value of the test, the one without a later value of it); in one arm they
    # would leave the table the same (gen-2b, a kit of the review of gen-2b).
    start = subject.first_dose + 2 * DAY
    p.event(subject, start, start + 2 * DAY)
    return Planted(probe, "planted", [subject.key],
                   {"tests": list(p.parameters.tests), "visits": list(p.parameters.visits),
                    "event_on": start.isoformat()})


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
    keys: list[str] = []
    per_key: dict[str, dict] = {}
    # Where emergence is by the date and time of the first dose, an event completed to the
    # first day of its month and one completed to the treatment start date (00:00) both
    # start before a first dose with a time. A second subject, whose first dose has no
    # collected time, tells them apart (gen-2b, ADR-023: the limit (a) lifted).
    timeless = (p.values.get("ae.teae.start") or {}).get("rule") == "at_or_after_first_dose_time"
    for number in (1, 2) if timeless else (1,):
        subject = p.fresh(probe, number, need=lambda date: 5 <= date.day <= 20)
        if number == 2:
            subject.first_dose_time = None
            for dose in subject.doses:
                dose.start_time = None
        start = subject.first_dose + 2 * DAY
        p.event(subject, start, start + 4 * DAY, start_text=start.isoformat()[:7])
        keys.append(subject.key)
        per_key[subject.key] = {"collected": start.isoformat()[:7],
                                "dose_time": subject.first_dose_time}
    return Planted(probe, "planted", keys, {"subjects": len(keys)}, per_key)


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
    # The events are counted in a row of related events of the table: a mild one by the
    # row RELATED; where the table shows serious related events and not related events,
    # the events are serious.
    rows = shown_rows(p.values.get("tfl.ae.summary.rows")) if p.values else _ALL_ROWS
    serious = "RELATED" not in rows and "SERIOUS_RELATED" in rows
    for number, value in enumerate(p.ctx.scale, start=1):
        subject = p.fresh(probe, number, arm=p.others[(number - 1) % len(p.others)])
        start = subject.first_dose + 5 * DAY
        if serious:
            p.event(subject, start, start + 2 * DAY, causality=value, serious=True,
                    severity="MODERATE")
        else:
            p.event(subject, start, start + 2 * DAY, causality=value)
        keys.append(subject.key)
        values[subject.key] = {"value": value}
    return Planted(probe, "planted", keys, {"values": list(p.ctx.scale), "serious": serious},
                   values)


def _without_any_postbaseline(p: Planter) -> Planted:
    probe = "dosed_without_postbaseline_value"
    stop = p.rng.child(probe, "stop").between(3, 5)
    subject = p.fresh(probe, stop_day=stop, reason="WITHDRAWAL BY SUBJECT")
    return Planted(probe, "planted", [subject.key])


def _zero_count(p: Planter) -> Planted | None:
    arm = p.parameters.spared_arm
    people = [s for s in p.people if arm in (s.planned_arm, s.actual_arm)]
    if any(e.fatal for s in people for e in s.events):
        raise RuntimeError("a subject of the spared arm has a fatal event")
    return Planted("category_with_zero_count", "counts", detail={
        "arm": arm, "category": "fatal adverse event", "count": 0,
        "assumes": {"tfl.ae.summary.rows": "shows FATAL"}})


def is_rounding_half(count: int, total: int, decimals: int = 1) -> bool:
    """Whether 100 * count / total lies exactly halfway between two values at `decimals`
    decimals, with an even digit before the half: half to even then rounds down and half
    away from zero up.

    The value must also be exact in binary floating point, as the engines compute it:
    its denominator is a power of two (6.25, 12.5, 3.125; not 3.15). At one decimal
    that is a value that ends in .25; the size of the group is then a multiple of 16,
    at no decimals of 8, at two decimals of 32.
    """
    if total <= 0 or count < 0:
        return False
    value = Fraction(100 * count, total)
    if value.denominator & (value.denominator - 1):
        return False
    scaled = value * 10 ** decimals
    twice = 2 * scaled
    return twice.denominator == 1 and twice.numerator % 2 == 1 and \
        (scaled.numerator // scaled.denominator) % 2 == 0


def half_sizes(decimals: int) -> int:
    """The sizes of a group for which a count at a rounding half exists are the multiples
    of this number (`is_rounding_half`)."""
    return 2 ** (decimals + 3)


# The domains the hand calculation reads.
_REFERENCE_DOMAINS = ("DM", "SV", "DS", "EX", "AE", "VS")


@dataclass
class Column:
    """The column of the count probes under a decision vector, by the hand calculation."""

    label: str
    members: list[str]          # USUBJID of every subject of the analysis set in the column
    with_any_event: list[str]   # of them, with a treatment-emergent event
    with_serious_event: list[str]


def spared_column(tables: dict[str, list[dict]], values: dict[str, dict], arm: str) -> Column:
    """The column of the arm `arm` in the adverse event summary of these SDTM rows under
    the vector `values`, as `specfirst.gen.reference` calculates it: who is in it, who has
    a treatment-emergent event, who a serious one. The column is the one in which the
    subjects planned for and dosed with that arm stand (by DM.ARMCD and DM.ACTARMCD)."""
    from specfirst.gen import reference

    people = reference.people(tables, values)
    population = values["tfl.population"]["rule"]
    flag = {"safety": "in_safety", "randomized": "in_randomized",
            "efficacy": "in_efficacy"}[population]
    by_actual = population == "safety" and values["pop.safety.grouping"]["rule"] == "actual"

    def group(person: reference.Person) -> str | None:
        return person.actual if by_actual else person.planned

    dm = {row["USUBJID"]: row for row in tables["DM"]}
    own = [person for person in people
           if dm[person.usubjid]["ARMCD"] == arm and dm[person.usubjid]["ACTARMCD"] == arm]
    labels = sorted({label for person in own if (label := group(person)) is not None})
    if len(labels) != 1:
        raise RuntimeError(f"the subjects of the arm {arm} stand in {len(labels)} columns "
                           f"under these decisions: {labels}")
    members = [person for person in people if getattr(person, flag)
               and group(person) == labels[0]]
    return Column(labels[0], [person.usubjid for person in members],
                  [person.usubjid for person in members
                   if any(event["emergent"] for event in person.events)],
                  [person.usubjid for person in members
                   if any(event["emergent"] and "SERIOUS" in event["kinds"]
                          for event in person.events)])


def _column_now(p: Planter) -> tuple[Column, dict[str, Subject]]:
    """The column of the count probes in the study as it stands, and the subjects by
    USUBJID. The identifiers are given again: a later call numbers the same subjects
    alike."""
    from specfirst.gen import sdtm

    subjects.assign_identifiers(p.ctx.design, p.people)
    tables = sdtm.build(p.ctx.design, p.people, _REFERENCE_DOMAINS)
    return spared_column(tables, p.values, p.parameters.spared_arm), \
        {subject.usubjid: subject for subject in p.people}


def _rounding_half(p: Planter) -> Planted:
    """Counts of the column of the placebo arm at a rounding half, for the kit's own table.

    The column is the one the analysis set, the grouping and the sources of treatment of
    the decision vector give (`spared_column`); the number of decimals is the vector's.
    Subjects of the arm are added, who complete the study without an event, until the
    size of the column is a multiple of `half_sizes`. Then the subjects with a serious
    event and with any event are made a count at a rounding half: the smallest for
    serious events, the nearest one for any event. Only subjects of the base process and
    the added subjects are changed; an event added starts two days after the first dose,
    which every rule of emergence counts.
    """
    probe = "statistic_at_rounding_half"
    arm = p.parameters.spared_arm
    decimals = p.values["tfl.percent.format"]["decimals"]
    size = half_sizes(decimals)
    rng = p.rng.child(probe)
    column, _ = _column_now(p)
    added = [p.fresh(probe, number, arm=arm)
             for number in range(1, (-len(column.members)) % size + 1)]
    column, by_id = _column_now(p)
    total = len(column.members)
    if total % size:
        raise RuntimeError(f"the column {column.label!r} has {total} subjects after {len(added)} "
                           f"were added, not a multiple of {size}")
    changeable = {key for key in column.members
                  if not by_id[key].probes or probe in by_id[key].probes}

    def free(keys: list[str]) -> list[Subject]:
        """The subjects of `keys` that may be changed, in the order of their identifiers."""
        return [by_id[key] for key in sorted(keys) if key in changeable]

    def roomy(subject: Subject) -> bool:
        return subject.last_dose is not None and (subject.last_dose - subject.first_dose).days >= 3

    def add(subject: Subject, serious: bool) -> None:
        start = subject.first_dose + 2 * DAY
        if serious:
            p.event(subject, start, start + 2 * DAY, serious=True, severity="SEVERE")
        else:
            p.event(subject, start, start + 2 * DAY)

    halves = [count for count in range(1, total + 1) if is_rounding_half(count, total, decimals)]
    serious_target = halves[0]
    having, serious = set(column.with_any_event), set(column.with_serious_event)
    if len(serious) > serious_target:
        for subject in rng.child("less-serious").shuffled(
                [s for s in free(sorted(serious)) if not any(e.fatal for e in s.events)]
        )[:len(serious) - serious_target]:
            for event in subject.events:
                event.serious = False
    elif len(serious) < serious_target:
        lacking = serious_target - len(serious)
        plain = [s for s in free(sorted(having - serious)) if roomy(s)]
        quiet = [s for s in free(sorted(set(column.members) - having)) if roomy(s)]
        chosen = rng.child("more-serious").shuffled(plain)[:lacking]
        chosen += rng.child("new-serious").shuffled(quiet)[:lacking - len(chosen)]
        for subject in chosen:
            add(subject, serious=True)

    column, by_id = _column_now(p)
    having, serious = set(column.with_any_event), set(column.with_serious_event)
    target = min((count for count in halves if count >= len(serious)),
                 key=lambda count: (abs(count - len(having)), count))
    if len(having) > target:
        removable = [s for s in free(sorted(having - serious))
                     if not any(e.serious or e.fatal or e.action == "DRUG WITHDRAWN"
                                for e in s.events)]
        for subject in rng.child("fewer").shuffled(removable)[:len(having) - target]:
            subject.events = [e for e in subject.events if e.start <= subject.first_dose]
    elif len(having) < target:
        quiet = [s for s in free(sorted(set(column.members) - having)) if roomy(s)]
        for subject in rng.child("more").shuffled(quiet)[:target - len(having)]:
            add(subject, serious=False)

    column, by_id = _column_now(p)
    counts = (len(column.with_any_event), len(column.with_serious_event))
    if not all(is_rounding_half(count, total, decimals) for count in counts):
        raise RuntimeError(f"the column {column.label!r}: {counts[0]} and {counts[1]} of {total} "
                           f"subjects do not give a percentage at a rounding half at "
                           f"{decimals} decimals")
    population = p.values["tfl.population"]["rule"]
    return Planted(probe, "counts", [subject.key for subject in added], detail={
        "arm": arm, "column": column.label, "decimals": decimals,
        "subjects": total, "subjects_added": len(added),
        "with_any_event": counts[0], "with_serious_event": counts[1],
        "percent": [100.0 * count / total for count in counts],
        "population": population,
        "grouping": "actual" if population == "safety"
        and p.values["pop.safety.grouping"]["rule"] == "actual" else "planned",
        "decisions": {key: p.values[key] for key in sorted(p.values)}})


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
          picked: list[str], values: dict[str, dict]) -> list[Planted]:
    """Plant the chosen probes into the subjects of one dataset, in the order of RECIPES,
    for the decision vector `values` (entry -> value, as `decisions.sample` gives it)."""
    planter = Planter(ctx, people, rng, Parameters.of_kit(ctx.design, values), values)
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
        people: list[Subject], values: dict[str, dict]) -> list[dict]:
    """The lines of probes.jsonl for one dataset. Subjects must carry their identifiers.
    `values` is the decision vector the probes were planted for."""
    by_key = {subject.key: subject.usubjid for subject in people}
    parameters = Parameters.of_kit(design, values).as_record()
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
