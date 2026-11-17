"""The subject process: the latent truth of every subject (PLAN.md section 6.4, stage S2).

The models are simple and documented here; they are built for decision
coverage, not for clinical realism (section 6.8).

    Enrolment     Subjects give consent one after another; the gaps are
                  exponential with the mean the design gives. A share of them
                  fails screening. Screening goes on until the planned number
                  is randomized.
    Arm           Permuted blocks in the allocation ratio of the design, in
                  the order of screening, so every arm gets exactly its
                  planned number.
    Visits        A visit takes place on its planned day plus a uniform shift
                  inside its window. Visits after the end of treatment are
                  missed. The follow-up visit is timed from the last dose,
                  not from its planned day: the follow-up days of the design
                  plus a shift inside its window. A subject who is lost to
                  follow-up or withdraws has no follow-up visit and leaves
                  the study 0 to 3 days after the last dose.
    Exposure      One tablet a day from day 1. One exposure record per
                  interval between two attended visits. The first dose has a
                  collected time.
    Dropout       With the probability of the arm a subject stops early, on
                  a day uniform over the treatment period, for a reason drawn
                  from a fixed list. A subject who stops for an adverse event
                  has the action DRUG WITHDRAWN on the last event; a subject
                  with that reason and no event gets one in the last days of
                  treatment.
    Vital signs   A subject mean plus noise per visit; after day 1 a shift
                  per dose step.
    Adverse       The number of events is Poisson; the mean grows with the
    events        dose step and shrinks with a short exposure. An event starts
                  on a treatment day after day 1 and lasts an exponential
                  number of days. Severity, seriousness, causality, action
                  and outcome are drawn from fixed tables. An event that
                  lasts beyond the end of the study is ongoing. With a small
                  chance there is one event before the first dose that ends
                  before it.
    Death         A serious, severe event that starts after the first dose is
                  fatal with a chance of 0.10. The subject then dies on the
                  day the event ends (two days after its start when it was
                  ongoing): nothing of the subject is dated later, the
                  disposition is DEATH, and other events that have not ended
                  stay ongoing. Nobody dies in the placebo arm of a study
                  whose probes include the category with a zero count
                  (`spared` below): that probe needs an arm without a fatal
                  event.

In the base process every randomized subject is dosed with the planned
treatment, has complete dates, and has no event after the last dose. The
edge cases come from the probes (stage S3, `specfirst.gen.probes`), so that
the log of probes says exactly where each one is.
"""

from __future__ import annotations

import dataclasses
import datetime
from dataclasses import dataclass, field

from specfirst.gen import design as designs
from specfirst.gen import terms
from specfirst.gen.rng import Stream

Date = datetime.date
DAY = datetime.timedelta(days=1)


@dataclass
class Dose:
    """One exposure record: a constant-dosing interval."""

    treatment: str            # name of the study intervention
    dose: float
    start: Date
    end: Date | None          # None: the end was not collected
    start_time: str | None = None   # collected time of the start, "hh:mm"
    start_text: str | None = None   # collected text when it is not the full date
    end_text: str | None = None


@dataclass
class Visit:
    number: float
    name: str
    planned_day: int | None   # None: an unscheduled visit
    date: Date
    encounter: str | None = None


@dataclass
class Vital:
    code: str
    value: float
    date: Date
    visit_number: float
    visit_name: str
    planned_day: int | None


@dataclass
class Event:
    term: str                 # preferred term of the dictionary
    start: Date
    end: Date | None          # None: ongoing
    severity: str
    serious: bool
    causality: str
    action: str
    outcome: str
    fatal: bool = False
    start_text: str | None = None   # collected text when it is not the full date


@dataclass
class Disposition:
    category: str             # DISPOSITION EVENT or PROTOCOL MILESTONE
    decod: str
    date: Date
    subcategory: str | None = None


@dataclass
class Subject:
    key: str                  # how the generator names the subject: "base-17", "probe-..."
    site: str
    country: str
    consent: Date
    age: int
    sex: str
    race: str
    ethnic: str
    state: str                # screen_failure | not_assigned | randomized
    planned_arm: str | None = None
    actual_arm: str | None = None
    randomized_on: Date | None = None
    first_dose: Date | None = None
    first_dose_time: str | None = None
    last_dose: Date | None = None
    reference_start: Date | None = None      # DM.RFSTDTC when it is not the first dose date
    first_exposure_text: str | None = None   # DM.RFXSTDTC when it is not the first dose
    death: Date | None = None
    end_of_study: Date | None = None
    doses: list[Dose] = field(default_factory=list)
    visits: list[Visit] = field(default_factory=list)
    vitals: list[Vital] = field(default_factory=list)
    events: list[Event] = field(default_factory=list)
    dispositions: list[Disposition] = field(default_factory=list)
    probes: list[str] = field(default_factory=list)
    vital_means: dict[str, float] = field(default_factory=dict)  # latent level per test
    subjid: str = ""          # set when all subjects are known
    usubjid: str = ""

    @property
    def dosed(self) -> bool:
        return self.first_dose is not None


def as_record(subject: Subject) -> dict:
    """The truth of a subject as plain data, dates as ISO text (kept in gold for audit)."""

    def plain(value: object) -> object:
        if isinstance(value, Date):
            return value.isoformat()
        if isinstance(value, list):
            return [plain(item) for item in value]
        if isinstance(value, dict):
            return {key: plain(item) for key, item in value.items()}
        return value

    return plain(dataclasses.asdict(subject))


@dataclass
class Context:
    """What the process needs to know about one study."""

    design: dict
    start: Date
    dose_step: dict[str, int]       # arm -> 0 for placebo, 1.. for ascending doses
    dictionary: list[dict]
    scale: list[str]

    @classmethod
    def of(cls, design: dict) -> Context:
        order = designs.dose_order(design)
        return cls(
            design=design,
            start=Date.fromisoformat(design["study"]["startDate"]),
            dose_step={name: step for step, name in enumerate(order)},
            dictionary=terms.ae_terms(),
            scale=list(design["collection"]["adverseEvents"]["causality"]),
        )

    def treatment_of(self, arm: str) -> tuple[str, float]:
        item = designs.arm(self.design, arm)
        return item["studyInterventionId"], float(item["dose"])


def _demographics(rng: Stream, ctx: Context) -> dict:
    limits = ctx.design["studyDesign"]["population"]["plannedAge"]
    age = int(round(rng.normal(52.0, 14.0)))
    age = min(max(age, limits["minValue"]), limits["maxValue"])
    return {
        "age": age,
        "sex": rng.choice(("F", "M")),
        "race": rng.choice(terms.RACES, terms.RACE_WEIGHTS),
        "ethnic": rng.choice(terms.ETHNICITIES, terms.ETHNICITY_WEIGHTS),
    }


def _site(rng: Stream, ctx: Context) -> dict:
    sites = ctx.design["sites"]
    return rng.choice(sites, [s["weight"] for s in sites])


def measure(rng: Stream, ctx: Context, subject: Subject, visit: Visit) -> list[Vital]:
    """The vital signs of one visit. An unscheduled visit measures what a treatment visit does."""
    found = []
    like = visit.encounter or designs.encounters(ctx.design)[1]["name"]
    after_first_dose = subject.first_dose is not None and visit.date > subject.first_dose
    step = ctx.dose_step.get(subject.actual_arm or "", 0)
    for test in designs.vital_signs(ctx.design):
        if like not in test["encounterIds"]:
            continue
        model = terms.VITAL_SIGNS[test["testCode"]]
        value = subject.vital_means[test["testCode"]] + rng.normal(0.0, model["within"])
        if after_first_dose:
            value += model["dose_effect"] * step
        found.append(Vital(code=test["testCode"], value=round(value, test["decimals"]),
                           date=visit.date, visit_number=visit.number, visit_name=visit.name,
                           planned_day=visit.planned_day))
    return found


def _causality(rng: Stream, ctx: Context, active: bool) -> str:
    """Unrelated values are likelier; less so under the drug."""
    decay = 0.75 if active else 0.4
    weights = [decay ** position for position in range(len(ctx.scale))]
    return rng.choice(ctx.scale, weights)


def _event(rng: Stream, ctx: Context, subject: Subject, start: Date, last_day: Date) -> Event:
    step = ctx.dose_step.get(subject.actual_arm or "", 0)
    rows = ctx.dictionary
    weights = [row["weight"] * (1.0 + 0.5 * step if row["dose_related"] else 1.0)
               for row in rows]
    row = rng.choice(rows, weights)
    severity = rng.choice(terms.SEVERITIES, (60.0, 30.0, 10.0))
    serious = rng.chance({"MILD": 0.005, "MODERATE": 0.04, "SEVERE": 0.30}[severity])
    end: Date | None = start + (int(rng.exponential(6.0))) * DAY
    outcome = "RECOVERED/RESOLVED"
    if end > last_day:
        end, outcome = None, "NOT RECOVERED/NOT RESOLVED"
    action = "DRUG INTERRUPTED" if rng.chance(0.03) else "DOSE NOT CHANGED"
    return Event(term=row["pt"], start=start, end=end, severity=severity, serious=serious,
                 causality=_causality(rng, ctx, active=step > 0), action=action, outcome=outcome)


def simulate(
    ctx: Context,
    rng: Stream,
    key: str,
    consent: Date,
    *,
    state: str = "randomized",
    arm: str | None = None,
    first_dose: Date | None = None,
    stop_day: int | None = None,
    reason: str | None = None,
    complete: bool | None = None,
    events: bool = True,
    dosed: bool = True,
) -> Subject:
    """The truth of one subject.

    `first_dose` moves the consent so that day 1 falls on that date.
    `stop_day` is the study day of the last dose of a subject who stops
    early; `complete` forces completion (True) or leaves it to chance
    (None). `events=False` gives a subject without adverse events, for a
    probe that adds its own. `dosed=False` gives a randomized subject who
    never takes a dose.
    """
    design = ctx.design
    site = _site(rng.child("site"), ctx)
    subject = Subject(key=key, site=site["name"], country=site["country"], consent=consent,
                      state=state, **_demographics(rng.child("demographics"), ctx))
    visits = designs.encounters(design)
    screening = visits[0]
    subject.vital_means = {
        code: round(rng.child("vitals", code).normal(model["mean"], model["sd"]), 3)
        for code, model in terms.VITAL_SIGNS.items()}
    study = design["collection"]["disposition"]["subcategories"]["study"]

    def attend(encounter: dict, date: Date) -> Visit:
        visit = Visit(number=float(encounter["visitNumber"]), name=encounter["label"],
                      planned_day=encounter["plannedDay"], date=date, encounter=encounter["name"])
        subject.visits.append(visit)
        subject.vitals += measure(rng.child("vitals", encounter["name"]), ctx, subject, visit)
        return visit

    screening_days = rng.child("screening").between(3, -screening["plannedDay"])
    if first_dose is not None:
        consent = first_dose - screening_days * DAY
        subject.consent = consent
    subject.dispositions.append(
        Disposition("PROTOCOL MILESTONE", "INFORMED CONSENT OBTAINED", consent))
    attend(screening, consent)

    if state == "screen_failure":
        failed = consent + rng.child("screening").between(1, screening_days) * DAY
        subject.dispositions.append(
            Disposition("DISPOSITION EVENT", "SCREEN FAILURE", failed, study))
        subject.end_of_study = failed
        return subject

    day1 = consent + screening_days * DAY
    if state == "randomized":
        subject.planned_arm = arm
        subject.randomized_on = day1
        subject.dispositions.append(Disposition("PROTOCOL MILESTONE", "RANDOMIZED", day1))
    if not dosed:
        stopped = day1 + rng.child("stop").between(0, 3) * DAY
        subject.dispositions.append(
            Disposition("DISPOSITION EVENT", reason or "WITHDRAWAL BY SUBJECT", stopped, study))
        subject.end_of_study = stopped
        return subject

    subject.actual_arm = arm
    subject.first_dose = day1
    hour = rng.child("dose-time")
    subject.first_dose_time = f"{hour.between(8, 11):02d}:{hour.choice((0, 15, 30, 45)):02d}"
    planned_days = designs.treatment_days(design)
    stop = rng.child("stop")
    rates = design["process"]["discontinuation"]
    rate = rates["placebo"] if designs.is_placebo(design, arm) else rates["active"]
    early = stop_day is not None or (complete is not True and complete is not None) or (
        complete is None and stop.chance(rate))
    if early:
        last_day = stop_day if stop_day is not None else stop.between(2, planned_days - 1)
        reason = reason or stop.choice([r for r, _ in terms.DISCONTINUATION_REASONS],
                                       [w for _, w in terms.DISCONTINUATION_REASONS])
    else:
        last_day, reason = planned_days, None

    # Visits of the treatment epoch, as long as the subject is on treatment.
    shift = rng.child("visit-shift")
    attended: list[Visit] = []
    treatment_visits = [e for e in visits if e["epochId"] == "TREATMENT"]
    end_of_treatment = treatment_visits[-1]
    for encounter in treatment_visits:
        planned = day1 + (encounter["plannedDay"] - 1) * DAY
        date = planned + shift.between(-encounter["windowLower"], encounter["windowUpper"]) * DAY
        if attended and date <= attended[-1].date:
            date = attended[-1].date + DAY
        if early and date > day1 + (last_day - 1) * DAY:
            break
        attended.append(attend(encounter, date))
    if not early and attended[-1].encounter == end_of_treatment["name"]:
        subject.last_dose = attended[-1].date - DAY
    else:
        subject.last_dose = day1 + (last_day - 1) * DAY
    treatment, dose = ctx.treatment_of(arm)
    for position, visit in enumerate(attended):
        if visit.date > subject.last_dose:
            break
        following = attended[position + 1].date - DAY if position + 1 < len(attended) else None
        end = min(following, subject.last_dose) if following else subject.last_dose
        subject.doses.append(Dose(treatment=treatment, dose=dose, start=visit.date, end=end,
                                  start_time=subject.first_dose_time if position == 0 else None))

    # Follow-up visit and the end of the study.
    follow = [e for e in visits if e["epochId"] == "FOLLOW-UP"]
    no_follow_up = reason in ("LOST TO FOLLOW-UP", "WITHDRAWAL BY SUBJECT")
    if follow and not no_follow_up:
        gap = designs.follow_up_days(design) + shift.between(0, follow[0]["windowUpper"])
        subject.end_of_study = attend(follow[0], subject.last_dose + gap * DAY).date
    else:
        subject.end_of_study = subject.last_dose + stop.between(0, 3) * DAY

    if events:
        _adverse_events(rng.child("events"), ctx, subject, day1, drug_withdrawn=(
            reason == "ADVERSE EVENT"))
    if subject.death is not None:
        reason = "DEATH"
    subject.dispositions.append(Disposition(
        "DISPOSITION EVENT", reason or "COMPLETED", subject.end_of_study, study))
    return subject


def _adverse_events(rng: Stream, ctx: Context, subject: Subject, day1: Date,
                    drug_withdrawn: bool) -> None:
    process = ctx.design["process"]["adverseEvents"]
    step = ctx.dose_step.get(subject.actual_arm or "", 0)
    days_on = (subject.last_dose - day1).days + 1
    exposure = days_on / designs.treatment_days(ctx.design)
    mean = process["eventsPerSubject"] * (1.0 + process["doseEffect"] * step) * exposure
    count = rng.poisson(mean) if days_on >= 2 else 0
    starts = sorted(day1 + rng.between(1, days_on - 1) * DAY for _ in range(count))
    for number, start in enumerate(starts):
        subject.events.append(
            _event(rng.child(number), ctx, subject, start, subject.end_of_study))
    if drug_withdrawn:
        if not subject.events:
            start = max(day1 + DAY, subject.last_dose - rng.between(0, 3) * DAY)
            subject.events.append(
                _event(rng.child("withdrawn"), ctx, subject, start, subject.end_of_study))
        subject.events[-1].action = "DRUG WITHDRAWN"
    if rng.chance(process["pretreatmentRate"]) and (day1 - subject.consent).days >= 2:
        start = subject.consent + rng.between(0, (day1 - subject.consent).days - 2) * DAY
        end = min(start + rng.between(0, 5) * DAY, day1 - DAY)
        row = rng.choice(ctx.dictionary, [r["weight"] for r in ctx.dictionary])
        subject.events.insert(0, Event(
            term=row["pt"], start=start, end=end, severity="MILD", serious=False,
            causality=ctx.scale[0], action="NOT APPLICABLE", outcome="RECOVERED/RESOLVED"))


def make_fatal(subject: Subject, event: Event, study_subcategory: str) -> None:
    """Turn an event into a fatal one: the subject dies on the day it ends."""
    died = event.end or (event.start + 2 * DAY)
    event.end, event.fatal, event.serious = died, True, True
    event.severity, event.outcome, event.action = "SEVERE", "FATAL", "NOT APPLICABLE"
    subject.death = died
    subject.end_of_study = died
    if subject.last_dose and subject.last_dose > died:
        subject.last_dose = died
    subject.doses = [d for d in subject.doses if d.start <= died]
    for dose in subject.doses:
        if dose.end is not None and dose.end > died:
            dose.end = died
    subject.visits = [v for v in subject.visits if v.date <= died]
    subject.vitals = [v for v in subject.vitals if v.date <= died]
    subject.events = [e for e in subject.events if e.start <= died]
    for other in subject.events:
        if other is not event and (other.end is None or other.end > died):
            other.end, other.outcome = None, "NOT RECOVERED/NOT RESOLVED"
    subject.dispositions = [d for d in subject.dispositions if d.category != "DISPOSITION EVENT"]
    subject.dispositions.append(
        Disposition("DISPOSITION EVENT", "DEATH", died, study_subcategory))


def base_subjects(ctx: Context, rng: Stream, spared: str | None = None) -> list[Subject]:
    """Everyone the base process enrols: screen failures and randomized subjects.

    No subject of the arm `spared` dies: a probe asks for an arm without a
    fatal event.
    """
    design = ctx.design
    listed = designs.arms(design)
    ratio = design["studyDesign"]["randomization"]["allocationRatio"]
    block_size = design["studyDesign"]["randomization"]["blockSize"]
    unit = [a["name"] for a, share in zip(listed, ratio, strict=True) for _ in range(share)]
    planned = sum(a["plannedNumber"] for a in listed)
    process = design["process"]
    study = design["collection"]["disposition"]["subcategories"]["study"]
    gap = 7.0 / process["enrolmentPerWeek"]

    subjects: list[Subject] = []
    arrivals = rng.child("arrivals")
    blocks = rng.child("blocks")
    queue: list[str] = []
    consent = ctx.start
    randomized = 0
    index = 0
    while randomized < planned:
        index += 1
        stream = rng.child("subject", index)
        consent = consent + int(round(arrivals.exponential(gap))) * DAY
        if stream.child("screen").chance(process["screenFailureRate"]):
            subjects.append(simulate(ctx, stream, f"base-{index}", consent,
                                     state="screen_failure"))
            continue
        if not queue:
            queue = blocks.shuffled(unit * (block_size // len(unit)))
        arm = queue.pop()
        subject = simulate(ctx, stream, f"base-{index}", consent, arm=arm)
        fatal = stream.child("fatal")
        for event in (subject.events if arm != spared else []):
            if event.serious and event.severity == "SEVERE" and event.start > subject.first_dose \
                    and fatal.chance(0.10):
                make_fatal(subject, event, study)
                break
        subjects.append(subject)
        randomized += 1
    return subjects


def enrolment_end(subjects: list[Subject]) -> Date:
    """The last consent of the base process: probe subjects are enrolled before it."""
    return max(subject.consent for subject in subjects)


def assign_identifiers(design: dict, subjects: list[Subject]) -> None:
    """Number the subjects per site in the order of consent, and sort them by identifier."""
    study = designs.study_id(design)
    subjects.sort(key=lambda s: (s.consent, s.key))
    counters: dict[str, int] = {}
    for subject in subjects:
        counters[subject.site] = counters.get(subject.site, 0) + 1
        subject.subjid = f"{subject.site}-{counters[subject.site]:03d}"
        subject.usubjid = f"{study}-{subject.subjid}"
    subjects.sort(key=lambda s: s.usubjid)
