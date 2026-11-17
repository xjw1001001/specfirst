"""SDTM from the latent truth (PLAN.md section 6.4, stage S4).

The datasets follow SDTMIG v3.4 (SDTM v2.0): names, labels, order and
controlled terms. There is no CRF layer in M1; the domains are written
directly from the truth of the subjects and from the design.

The code is general: `DOMAINS` describes every domain the generator knows,
and a caller limits a study to a list of them.

    subject data   DM, SE, SV, DS, EX, AE, VS
    trial design   TA, TE, TV, TS

Conventions the house standard relies on (docs/state/std.md): a subject is
randomized when ARMCD is present; a placebo record has EXDOSE 0 and an
EXTRT that contains PLACEBO; an unscheduled visit has no VISITDY.
SDTMIG v3.4 leaves ARMCD empty for a subject without an arm and gives the
reason in ARMNRS; the values SCRNFAIL and NOTASSGN of earlier versions are
not written.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass

from specfirst.gen import design as designs
from specfirst.gen import terms
from specfirst.gen.subjects import DAY, Dose, Subject

Date = datetime.date

SDTMIG_VERSION = "3.4"
SDTM_VERSION = "2.0"


@dataclass(frozen=True)
class Variable:
    name: str
    label: str
    kind: str        # text | integer | float | datetime (ISO 8601 text, maybe partial)
    core: str        # Req | Exp | Perm
    codelist: str | None = None   # a key of terms.CT, or a study codelist such as "ARM"
    origin: str = "Collected"     # Collected | Derived | Assigned | Protocol
    method: str | None = None     # a key of METHODS, for a derived variable


@dataclass(frozen=True)
class Domain:
    name: str
    label: str
    observation_class: str
    structure: str
    keys: tuple[str, ...]
    variables: tuple[Variable, ...]
    reference: bool = False       # trial design data: no subject
    repeating: bool = True

    def variable(self, name: str) -> Variable:
        for variable in self.variables:
            if variable.name == name:
                return variable
        raise KeyError(f"{self.name}.{name}")


METHODS = {
    "USUBJID": "The study identifier, the site identifier and the subject number at the site, "
               "joined with hyphens.",
    "SEQ": "A number that is unique within the subject, in the order of the dataset keys.",
    "STUDYDAY": "The date minus the date part of DM.RFSTDTC, plus one day when the date is on "
                "or after it. Empty when either date is incomplete.",
    "EPOCH": "The epoch of the trial element in which the start date of the record falls.",
    "REFERENCE": "Derived from the exposure, consent and disposition records of the subject.",
    "LOBXFL": "Y for the last result of the test on or before the date of first study treatment.",
    "STRES": "The collected result, unchanged: results are collected in the standard unit.",
    "CODED": "Assigned from the adverse event dictionary of the study.",
}


def _v(name: str, label: str, kind: str, core: str, codelist: str | None = None,
       origin: str = "Collected", method: str | None = None) -> Variable:
    return Variable(name, label, kind, core, codelist, "Derived" if method else origin, method)


def _ids(domain: str, subject: bool = True) -> tuple[Variable, ...]:
    head = (
        _v("STUDYID", "Study Identifier", "text", "Req", origin="Protocol"),
        _v("DOMAIN", "Domain Abbreviation", "text", "Req", origin="Assigned"),
    )
    if not subject:
        return head
    return (*head, _v("USUBJID", "Unique Subject Identifier", "text", "Req", method="USUBJID"))


def _seq(domain: str) -> Variable:
    return _v(f"{domain}SEQ", "Sequence Number", "integer", "Req", method="SEQ")


_EPOCH = _v("EPOCH", "Epoch", "text", "Perm", "EPOCH", method="EPOCH")

DOMAINS: dict[str, Domain] = {d.name: d for d in (
    Domain("DM", "Demographics", "SPECIAL PURPOSE", "One record per subject",
           ("STUDYID", "USUBJID"), (
        *_ids("DM"),
        _v("SUBJID", "Subject Identifier for the Study", "text", "Req", origin="Assigned"),
        _v("RFSTDTC", "Subject Reference Start Date/Time", "datetime", "Exp",
           method="REFERENCE"),
        _v("RFENDTC", "Subject Reference End Date/Time", "datetime", "Exp", method="REFERENCE"),
        _v("RFXSTDTC", "Date/Time of First Study Treatment", "datetime", "Exp",
           method="REFERENCE"),
        _v("RFXENDTC", "Date/Time of Last Study Treatment", "datetime", "Exp",
           method="REFERENCE"),
        _v("RFICDTC", "Date/Time of Informed Consent", "datetime", "Exp", method="REFERENCE"),
        _v("RFPENDTC", "Date/Time of End of Participation", "datetime", "Exp",
           method="REFERENCE"),
        _v("DTHDTC", "Date/Time of Death", "datetime", "Exp"),
        _v("DTHFL", "Subject Death Flag", "text", "Exp", "NY", method="REFERENCE"),
        _v("SITEID", "Study Site Identifier", "text", "Req", origin="Assigned"),
        _v("AGE", "Age", "integer", "Exp"),
        _v("AGEU", "Age Units", "text", "Exp", "AGEU"),
        _v("SEX", "Sex", "text", "Req", "SEX"),
        _v("RACE", "Race", "text", "Exp", "RACE"),
        _v("ETHNIC", "Ethnicity", "text", "Perm", "ETHNIC"),
        _v("ARMCD", "Planned Arm Code", "text", "Exp", "ARMCD", origin="Assigned"),
        _v("ARM", "Description of Planned Arm", "text", "Exp", "ARM", origin="Assigned"),
        _v("ACTARMCD", "Actual Arm Code", "text", "Exp", "ARMCD", origin="Assigned"),
        _v("ACTARM", "Description of Actual Arm", "text", "Exp", "ARM", origin="Assigned"),
        _v("ARMNRS", "Reason Arm and/or Actual Arm is Null", "text", "Exp", "ARMNULRS",
           origin="Assigned"),
        _v("ACTARMUD", "Description of Unplanned Actual Arm", "text", "Exp", origin="Assigned"),
        _v("COUNTRY", "Country", "text", "Req", origin="Assigned"),
    ), repeating=False),
    Domain("SE", "Subject Elements", "SPECIAL PURPOSE",
           "One record per actual Element per subject", ("STUDYID", "USUBJID", "SESEQ"), (
        *_ids("SE"), _seq("SE"),
        _v("ETCD", "Element Code", "text", "Req", "ETCD", origin="Assigned"),
        _v("ELEMENT", "Description of Element", "text", "Perm", "ELEMENT", origin="Assigned"),
        _v("TAETORD", "Planned Order of Element within Arm", "integer", "Perm",
           origin="Assigned"),
        _v("EPOCH", "Epoch", "text", "Perm", "EPOCH", origin="Assigned"),
        _v("SESTDTC", "Start Date/Time of Element", "datetime", "Req", method="REFERENCE"),
        _v("SEENDTC", "End Date/Time of Element", "datetime", "Exp", method="REFERENCE"),
        _v("SESTDY", "Study Day of Start of Element", "integer", "Perm", method="STUDYDAY"),
        _v("SEENDY", "Study Day of End of Element", "integer", "Perm", method="STUDYDAY"),
    )),
    Domain("SV", "Subject Visits", "SPECIAL PURPOSE",
           "One record per actual or planned visit per subject",
           ("STUDYID", "USUBJID", "VISITNUM"), (
        *_ids("SV"),
        _v("VISITNUM", "Visit Number", "float", "Req", origin="Assigned"),
        _v("VISIT", "Visit Name", "text", "Perm", origin="Assigned"),
        _v("SVPRESP", "Pre-specified", "text", "Exp", "NY", origin="Assigned"),
        _v("SVOCCUR", "Occurrence", "text", "Exp", "NY"),
        _v("VISITDY", "Planned Study Day of Visit", "integer", "Perm", origin="Protocol"),
        _v("SVSTDTC", "Start Date/Time of Observation", "datetime", "Exp"),
        _v("SVENDTC", "End Date/Time of Observation", "datetime", "Exp"),
        _v("SVSTDY", "Study Day of Start of Observation", "integer", "Perm", method="STUDYDAY"),
        _v("SVENDY", "Study Day of End of Observation", "integer", "Perm", method="STUDYDAY"),
        _v("SVUPDES", "Description of Unplanned Visit", "text", "Perm"),
    )),
    Domain("DS", "Disposition", "EVENTS",
           "One record per disposition status or protocol milestone per subject",
           ("STUDYID", "USUBJID", "DSSEQ"), (
        *_ids("DS"), _seq("DS"),
        _v("DSTERM", "Reported Term for the Disposition Event", "text", "Req"),
        _v("DSDECOD", "Standardized Disposition Term", "text", "Req", "DSDECOD",
           origin="Assigned"),
        _v("DSCAT", "Category for Disposition Event", "text", "Exp", "DSCAT",
           origin="Assigned"),
        _v("DSSCAT", "Subcategory for Disposition Event", "text", "Perm", "DSSCAT",
           origin="Assigned"),
        _EPOCH,
        _v("DSSTDTC", "Start Date/Time of Disposition Event", "datetime", "Exp"),
        _v("DSSTDY", "Study Day of Start of Disposition Event", "integer", "Exp",
           method="STUDYDAY"),
    )),
    Domain("EX", "Exposure", "INTERVENTIONS",
           "One record per protocol-specified study treatment, constant-dosing interval, "
           "per subject", ("STUDYID", "USUBJID", "EXSEQ"), (
        *_ids("EX"), _seq("EX"),
        _v("EXTRT", "Name of Treatment", "text", "Req", "EXTRT"),
        _v("EXDOSE", "Dose", "float", "Exp"),
        _v("EXDOSU", "Dose Units", "text", "Exp", "UNIT"),
        _v("EXDOSFRM", "Dose Form", "text", "Exp", "FRM"),
        _v("EXDOSFRQ", "Dosing Frequency per Interval", "text", "Perm", "FREQ"),
        _v("EXROUTE", "Route of Administration", "text", "Perm", "ROUTE"),
        _EPOCH,
        _v("EXSTDTC", "Start Date/Time of Treatment", "datetime", "Exp"),
        _v("EXENDTC", "End Date/Time of Treatment", "datetime", "Exp"),
        _v("EXSTDY", "Study Day of Start of Treatment", "integer", "Perm", method="STUDYDAY"),
        _v("EXENDY", "Study Day of End of Treatment", "integer", "Perm", method="STUDYDAY"),
    )),
    Domain("AE", "Adverse Events", "EVENTS", "One record per adverse event per subject",
           ("STUDYID", "USUBJID", "AESEQ"), (
        *_ids("AE"), _seq("AE"),
        _v("AETERM", "Reported Term for the Adverse Event", "text", "Req"),
        _v("AELLT", "Lowest Level Term", "text", "Exp", method="CODED"),
        _v("AELLTCD", "Lowest Level Term Code", "integer", "Exp", method="CODED"),
        _v("AEDECOD", "Dictionary-Derived Term", "text", "Req", method="CODED"),
        _v("AEPTCD", "Preferred Term Code", "integer", "Exp", method="CODED"),
        _v("AEHLT", "High Level Term", "text", "Exp", method="CODED"),
        _v("AEHLTCD", "High Level Term Code", "integer", "Exp", method="CODED"),
        _v("AEHLGT", "High Level Group Term", "text", "Exp", method="CODED"),
        _v("AEHLGTCD", "High Level Group Term Code", "integer", "Exp", method="CODED"),
        _v("AEBODSYS", "Body System or Organ Class", "text", "Exp", method="CODED"),
        _v("AEBDSYCD", "Body System or Organ Class Code", "integer", "Exp", method="CODED"),
        _v("AESOC", "Primary System Organ Class", "text", "Exp", method="CODED"),
        _v("AESOCCD", "Primary System Organ Class Code", "integer", "Exp", method="CODED"),
        _v("AESEV", "Severity/Intensity", "text", "Perm", "AESEV"),
        _v("AESER", "Serious Event", "text", "Exp", "NY"),
        _v("AEACN", "Action Taken with Study Treatment", "text", "Exp", "ACN"),
        _v("AEREL", "Causality", "text", "Exp", "AEREL"),
        _v("AEOUT", "Outcome of Adverse Event", "text", "Perm", "OUT"),
        _v("AESCONG", "Congenital Anomaly or Birth Defect", "text", "Perm", "NY"),
        _v("AESDISAB", "Persist or Signif Disability/Incapacity", "text", "Perm", "NY"),
        _v("AESDTH", "Results in Death", "text", "Perm", "NY"),
        _v("AESHOSP", "Requires or Prolongs Hospitalization", "text", "Perm", "NY"),
        _v("AESLIFE", "Is Life Threatening", "text", "Perm", "NY"),
        _v("AESMIE", "Other Medically Important Serious Event", "text", "Perm", "NY"),
        _EPOCH,
        _v("AESTDTC", "Start Date/Time of Adverse Event", "datetime", "Exp"),
        _v("AEENDTC", "End Date/Time of Adverse Event", "datetime", "Exp"),
        _v("AESTDY", "Study Day of Start of Adverse Event", "integer", "Perm",
           method="STUDYDAY"),
        _v("AEENDY", "Study Day of End of Adverse Event", "integer", "Perm", method="STUDYDAY"),
    )),
    Domain("VS", "Vital Signs", "FINDINGS",
           "One record per vital sign measurement per time point per visit per subject",
           ("STUDYID", "USUBJID", "VSTESTCD", "VISITNUM"), (
        *_ids("VS"), _seq("VS"),
        _v("VSTESTCD", "Vital Signs Test Short Name", "text", "Req", "VSTESTCD"),
        _v("VSTEST", "Vital Signs Test Name", "text", "Req", "VSTEST"),
        _v("VSPOS", "Vital Signs Position of Subject", "text", "Perm", "POSITION"),
        _v("VSORRES", "Result or Finding in Original Units", "text", "Exp"),
        _v("VSORRESU", "Original Units", "text", "Exp", "VSRESU"),
        _v("VSSTRESC", "Character Result/Finding in Std Format", "text", "Exp", method="STRES"),
        _v("VSSTRESN", "Numeric Result/Finding in Standard Units", "float", "Exp",
           method="STRES"),
        _v("VSSTRESU", "Standard Units", "text", "Exp", "VSRESU", method="STRES"),
        _v("VSLOBXFL", "Last Observation Before Exposure Flag", "text", "Exp", "NY",
           method="LOBXFL"),
        _v("VISITNUM", "Visit Number", "float", "Exp", origin="Assigned"),
        _v("VISIT", "Visit Name", "text", "Perm", origin="Assigned"),
        _v("VISITDY", "Planned Study Day of Visit", "integer", "Perm", origin="Protocol"),
        _EPOCH,
        _v("VSDTC", "Date/Time of Measurements", "datetime", "Exp"),
        _v("VSDY", "Study Day of Vital Signs", "integer", "Perm", method="STUDYDAY"),
    )),
    Domain("TA", "Trial Arms", "TRIAL DESIGN", "One record per planned Element per Arm",
           ("STUDYID", "ARMCD", "TAETORD"), (
        *_ids("TA", subject=False),
        _v("ARMCD", "Planned Arm Code", "text", "Req", "ARMCD", origin="Protocol"),
        _v("ARM", "Description of Planned Arm", "text", "Req", "ARM", origin="Protocol"),
        _v("TAETORD", "Planned Order of Element within Arm", "integer", "Req",
           origin="Protocol"),
        _v("ETCD", "Element Code", "text", "Req", "ETCD", origin="Protocol"),
        _v("ELEMENT", "Description of Element", "text", "Perm", "ELEMENT", origin="Protocol"),
        _v("TABRANCH", "Branch", "text", "Exp", origin="Protocol"),
        _v("TATRANS", "Transition Rule", "text", "Exp", origin="Protocol"),
        _v("EPOCH", "Epoch", "text", "Req", "EPOCH", origin="Protocol"),
    ), reference=True),
    Domain("TE", "Trial Elements", "TRIAL DESIGN", "One record per planned Element",
           ("STUDYID", "ETCD"), (
        *_ids("TE", subject=False),
        _v("ETCD", "Element Code", "text", "Req", "ETCD", origin="Protocol"),
        _v("ELEMENT", "Description of Element", "text", "Req", "ELEMENT", origin="Protocol"),
        _v("TESTRL", "Rule for Start of Element", "text", "Req", origin="Protocol"),
        _v("TEENRL", "Rule for End of Element", "text", "Perm", origin="Protocol"),
        _v("TEDUR", "Planned Duration of Element", "text", "Perm", origin="Protocol"),
    ), reference=True),
    Domain("TV", "Trial Visits", "TRIAL DESIGN", "One record per planned Visit per Arm",
           ("STUDYID", "VISITNUM"), (
        *_ids("TV", subject=False),
        _v("VISITNUM", "Visit Number", "float", "Req", origin="Protocol"),
        _v("VISIT", "Visit Name", "text", "Req", origin="Protocol"),
        _v("VISITDY", "Planned Study Day of Visit", "integer", "Perm", origin="Protocol"),
        _v("ARMCD", "Planned Arm Code", "text", "Exp", "ARMCD", origin="Protocol"),
        _v("TVSTRL", "Visit Start Rule", "text", "Req", origin="Protocol"),
        _v("TVENRL", "Visit End Rule", "text", "Perm", origin="Protocol"),
    ), reference=True),
    Domain("TS", "Trial Summary", "TRIAL DESIGN",
           "One record per trial summary parameter value", ("STUDYID", "TSPARMCD", "TSSEQ"), (
        *_ids("TS", subject=False),
        _v("TSSEQ", "Sequence Number", "integer", "Req", origin="Assigned"),
        _v("TSPARMCD", "Trial Summary Parameter Short Name", "text", "Req", "TSPARMCD",
           origin="Assigned"),
        _v("TSPARM", "Trial Summary Parameter", "text", "Req", "TSPARM", origin="Assigned"),
        _v("TSVAL", "Parameter Value", "text", "Exp", origin="Protocol"),
        _v("TSVALNF", "Parameter Value Null Flavor", "text", "Perm", origin="Assigned"),
        _v("TSVALCD", "Parameter Value Code", "text", "Exp", origin="Assigned"),
        _v("TSVCDREF", "Name of the Reference Terminology", "text", "Exp", origin="Assigned"),
        _v("TSVCDVER", "Version of the Reference Terminology", "text", "Exp",
           origin="Assigned"),
    ), reference=True),
)}

# The order in which a study lists its datasets.
ORDER = ("TA", "TE", "TV", "TS", "DM", "SE", "SV", "DS", "EX", "AE", "VS")
# What the part gen-1a writes: the four domains of the slice, the vital signs
# and visits that its population decisions read, and what CDISC CORE asks for.
SLICE_DOMAINS = ORDER


# -- values ------------------------------------------------------------------


def iso(date: Date | None) -> str | None:
    return None if date is None else date.isoformat()


def _complete_date(text: str | None) -> Date | None:
    """The date of an ISO 8601 text that has a full date; None for a partial one."""
    if not text or len(text) < 10:
        return None
    try:
        return Date.fromisoformat(text[:10])
    except ValueError:
        return None


def study_day(text: str | None, reference: str | None) -> int | None:
    """--DY: relative to RFSTDTC, no day 0. Empty when either date is incomplete."""
    date, start = _complete_date(text), _complete_date(reference)
    if date is None or start is None:
        return None
    days = (date - start).days
    return days + 1 if days >= 0 else days


def epoch_of(subject: Subject, date: Date) -> str:
    if subject.first_dose is None or date < subject.first_dose:
        return "SCREENING"
    if subject.last_dose is not None and date > subject.last_dose:
        return "FOLLOW-UP"
    return "TREATMENT"


def reference_start(subject: Subject) -> str | None:
    """DM.RFSTDTC: the date of the first dose, unless the truth says otherwise."""
    if subject.reference_start is not None:
        return iso(subject.reference_start)
    return iso(subject.first_dose)


def exposure_texts(dose: Dose) -> tuple[str, str | None]:
    """EXSTDTC and EXENDTC of an exposure record, as collected."""
    start = dose.start_text or (
        f"{iso(dose.start)}T{dose.start_time}" if dose.start_time else iso(dose.start))
    end = None if dose.end is None else (dose.end_text or iso(dose.end))
    return start, end


def last_exposure(subject: Subject) -> str | None:
    """DM.RFXENDTC: the latest collected exposure date, an end date or else a start date."""
    latest: tuple[Date, str] | None = None
    for dose in subject.doses:
        start, end = exposure_texts(dose)
        for date, text in ((dose.start, start), (dose.end, end)):
            if date is not None and text is not None and len(text) >= 10 and (
                    latest is None or date > latest[0]):
                latest = (date, text)
    return latest[1] if latest else None


def treatment_name(design: dict, intervention: str) -> str:
    """EXTRT: the name of the study intervention; PLACEBO for the placebo."""
    item = designs.intervention(design, intervention)
    return "PLACEBO" if item["role"] == designs.PLACEBO_ROLE else item["name"]


def element_of(design: dict, arm: str) -> dict:
    for element in design["studyDesign"]["elements"]:
        if element.get("armId") == arm:
            return element
    raise KeyError(arm)


def _element(design: dict, name: str) -> dict:
    for element in design["studyDesign"]["elements"]:
        if element["name"] == name:
            return element
    raise KeyError(name)


def _number(value: float, decimals: int) -> str:
    return f"{value:.{decimals}f}"


# -- subject data ------------------------------------------------------------


def _dm(design: dict, subjects: list[Subject]) -> list[dict]:
    rows = []
    for s in subjects:
        planned = designs.arm(design, s.planned_arm) if s.planned_arm else None
        actual = designs.arm(design, s.actual_arm) if s.actual_arm else None
        if s.state == "screen_failure":
            reason = "SCREEN FAILURE"
        elif planned is None:
            reason = "NOT ASSIGNED"
        elif actual is None:
            reason = "ASSIGNED, NOT TREATED"
        else:
            reason = None
        first = last = None
        if s.first_dose is not None:
            first = s.first_exposure_text or (
                f"{iso(s.first_dose)}T{s.first_dose_time}" if s.first_dose_time
                else iso(s.first_dose))
            last = last_exposure(s)
        rows.append({
            "USUBJID": s.usubjid, "SUBJID": s.subjid,
            "RFSTDTC": reference_start(s), "RFENDTC": last[:10] if last else None,
            "RFXSTDTC": first, "RFXENDTC": last,
            "RFICDTC": iso(s.consent), "RFPENDTC": iso(s.end_of_study),
            "DTHDTC": iso(s.death), "DTHFL": "Y" if s.death else None,
            "SITEID": s.site, "AGE": s.age, "AGEU": "YEARS", "SEX": s.sex, "RACE": s.race,
            "ETHNIC": s.ethnic,
            "ARMCD": planned["name"] if planned else None,
            "ARM": planned["description"] if planned else None,
            "ACTARMCD": actual["name"] if actual else None,
            "ACTARM": actual["description"] if actual else None,
            "ARMNRS": reason, "ACTARMUD": None, "COUNTRY": s.country,
        })
    return rows


def _se(design: dict, subjects: list[Subject]) -> list[dict]:
    rows = []
    for s in subjects:
        reference = reference_start(s)
        parts: list[tuple[str, Date, Date | None]] = []
        screening_end = s.first_dose or s.end_of_study
        parts.append(("SCRN", s.consent, screening_end))
        if s.first_dose is not None and s.actual_arm:
            # Without a known last dose the treatment element lasts to the end of the study.
            after = (s.last_dose or s.end_of_study) + DAY
            follows = s.end_of_study is not None and s.end_of_study >= after
            parts.append((element_of(design, s.actual_arm)["name"], s.first_dose,
                          after if follows else s.end_of_study))
            if follows:
                parts.append(("FUP", after, s.end_of_study))
        planned = ["SCRN", element_of(design, s.planned_arm)["name"], "FUP"] \
            if s.planned_arm else ["SCRN"]
        for number, (code, start, end) in enumerate(parts, start=1):
            element = _element(design, code)
            rows.append({
                "USUBJID": s.usubjid, "SESEQ": number, "ETCD": code,
                "ELEMENT": element["label"],
                "TAETORD": planned.index(code) + 1 if code in planned else None,
                "EPOCH": element["epochId"], "SESTDTC": iso(start), "SEENDTC": iso(end),
                "SESTDY": study_day(iso(start), reference),
                "SEENDY": study_day(iso(end), reference),
            })
    return rows


def _sv(design: dict, subjects: list[Subject]) -> list[dict]:
    rows = []
    for s in subjects:
        reference = reference_start(s)
        for visit in sorted(s.visits, key=lambda v: (v.number, v.date)):
            planned = visit.planned_day is not None
            rows.append({
                "USUBJID": s.usubjid, "VISITNUM": visit.number, "VISIT": visit.name,
                "SVPRESP": "Y" if planned else None, "SVOCCUR": "Y" if planned else None,
                "VISITDY": visit.planned_day,
                "SVSTDTC": iso(visit.date), "SVENDTC": iso(visit.date),
                "SVSTDY": study_day(iso(visit.date), reference),
                "SVENDY": study_day(iso(visit.date), reference),
                "SVUPDES": None if planned else "Unscheduled visit",
            })
    return rows


def _ds(design: dict, subjects: list[Subject]) -> list[dict]:
    rows = []
    for s in subjects:
        reference = reference_start(s)
        ordered = sorted(s.dispositions,
                         key=lambda d: (d.date, d.category != "PROTOCOL MILESTONE"))
        for number, item in enumerate(ordered, start=1):
            milestone = item.category == "PROTOCOL MILESTONE"
            if milestone:
                epoch = "SCREENING"
            else:
                epoch = epoch_of(s, item.date)
            rows.append({
                "USUBJID": s.usubjid, "DSSEQ": number,
                "DSTERM": item.decod.capitalize(), "DSDECOD": item.decod,
                "DSCAT": item.category, "DSSCAT": item.subcategory, "EPOCH": epoch,
                "DSSTDTC": iso(item.date), "DSSTDY": study_day(iso(item.date), reference),
            })
    return rows


def _ex(design: dict, subjects: list[Subject]) -> list[dict]:
    rows = []
    for s in subjects:
        reference = reference_start(s)
        for number, dose in enumerate(sorted(s.doses, key=lambda d: d.start), start=1):
            item = designs.intervention(design, dose.treatment)
            start, end = exposure_texts(dose)
            rows.append({
                "USUBJID": s.usubjid, "EXSEQ": number,
                "EXTRT": treatment_name(design, dose.treatment), "EXDOSE": float(dose.dose),
                "EXDOSU": item["unit"], "EXDOSFRM": item["doseForm"],
                "EXDOSFRQ": item["frequency"], "EXROUTE": item["route"],
                "EPOCH": "TREATMENT", "EXSTDTC": start, "EXENDTC": end,
                "EXSTDY": study_day(start, reference), "EXENDY": study_day(end, reference),
            })
    return rows


def _ae(design: dict, subjects: list[Subject]) -> list[dict]:
    dictionary = {row["pt"]: row for row in terms.ae_terms()}
    rows = []
    for s in subjects:
        reference = reference_start(s)
        ordered = sorted(s.events, key=lambda e: (e.start, e.term))
        for number, event in enumerate(ordered, start=1):
            term = dictionary[event.term]
            start = event.start_text or iso(event.start)
            end = iso(event.end)
            flag = "Y" if event.serious else "N"
            rows.append({
                "USUBJID": s.usubjid, "AESEQ": number, "AETERM": event.term.upper(),
                "AELLT": term["llt"], "AELLTCD": term["llt_code"],
                "AEDECOD": term["pt"], "AEPTCD": term["pt_code"],
                "AEHLT": term["hlt"], "AEHLTCD": term["hlt_code"],
                "AEHLGT": term["hlgt"], "AEHLGTCD": term["hlgt_code"],
                "AEBODSYS": term["soc"], "AEBDSYCD": term["soc_code"],
                "AESOC": term["soc"], "AESOCCD": term["soc_code"],
                "AESEV": event.severity, "AESER": flag, "AEACN": event.action,
                "AEREL": event.causality, "AEOUT": event.outcome,
                "AESCONG": "N", "AESDISAB": "N", "AESDTH": "Y" if event.fatal else "N",
                "AESHOSP": flag, "AESLIFE": "N", "AESMIE": "N",
                "EPOCH": epoch_of(s, event.start), "AESTDTC": start, "AEENDTC": end,
                "AESTDY": study_day(start, reference), "AEENDY": study_day(end, reference),
            })
    return rows


def _vs(design: dict, subjects: list[Subject]) -> list[dict]:
    tests = {t["testCode"]: t for t in designs.vital_signs(design)}
    order = {code: position for position, code in enumerate(tests)}
    seated = {"SYSBP", "DIABP", "PULSE"}
    rows = []
    for s in subjects:
        reference = reference_start(s)
        records = sorted(s.vitals, key=lambda v: (v.date, v.visit_number, order[v.code]))
        last_before: dict[str, int] = {}
        if s.first_dose is not None:
            for position, vital in enumerate(records):
                if vital.date <= s.first_dose:
                    last_before[vital.code] = position
        for position, vital in enumerate(records):
            test = tests[vital.code]
            text = _number(vital.value, test["decimals"])
            rows.append({
                "USUBJID": s.usubjid, "VSSEQ": position + 1, "VSTESTCD": vital.code,
                "VSTEST": test["test"], "VSPOS": "SITTING" if vital.code in seated else None,
                "VSORRES": text, "VSORRESU": test["unit"], "VSSTRESC": text,
                "VSSTRESN": float(text), "VSSTRESU": test["unit"],
                "VSLOBXFL": "Y" if last_before.get(vital.code) == position else None,
                "VISITNUM": vital.visit_number, "VISIT": vital.visit_name,
                "VISITDY": vital.planned_day, "EPOCH": epoch_of(s, vital.date),
                "VSDTC": iso(vital.date), "VSDY": study_day(iso(vital.date), reference),
            })
    return rows


# -- trial design ------------------------------------------------------------


def _ta(design: dict, subjects: list[Subject]) -> list[dict]:
    rows = []
    for arm in sorted(designs.arms(design), key=lambda a: a["name"]):
        treatment = element_of(design, arm["name"])
        steps = (
            ("SCRN", f"Randomized to {arm['description']}", None),
            (treatment["name"], None, None),
            ("FUP", None, None),
        )
        for number, (code, branch, transition) in enumerate(steps, start=1):
            element = _element(design, code)
            rows.append({"ARMCD": arm["name"], "ARM": arm["description"], "TAETORD": number,
                         "ETCD": code, "ELEMENT": element["label"], "TABRANCH": branch,
                         "TATRANS": transition, "EPOCH": element["epochId"]})
    return rows


def _te(design: dict, subjects: list[Subject]) -> list[dict]:
    screening = -designs.encounters(design)[0]["plannedDay"]
    rules = {
        "SCREENING": ("Informed consent", "First dose of study treatment", f"P{screening}D"),
        "TREATMENT": ("First dose of study treatment",
                      "One day after the last dose of study treatment",
                      f"P{designs.treatment_days(design)}D"),
        "FOLLOW-UP": ("One day after the last dose of study treatment",
                      "Follow-up visit or end of study participation",
                      f"P{designs.follow_up_days(design)}D"),
    }
    rows = []
    for element in sorted(design["studyDesign"]["elements"], key=lambda e: e["name"]):
        start, end, duration = rules[element["epochId"]]
        rows.append({"ETCD": element["name"], "ELEMENT": element["label"], "TESTRL": start,
                     "TEENRL": end, "TEDUR": duration})
    return rows


def _tv(design: dict, subjects: list[Subject]) -> list[dict]:
    rows = []
    for visit in designs.encounters(design):
        day = visit["plannedDay"]
        if visit["epochId"] == "SCREENING":
            rule = f"Informed consent, at most {-day} days before the first dose"
        elif visit["windowLower"] == 0 and visit["windowUpper"] == 0:
            rule = f"Study day {day}"
        else:
            rule = (f"Study day {day}, not more than {visit['windowLower']} days earlier "
                    f"or {visit['windowUpper']} days later")
        # ARMCD is empty: the visits are the same for every arm.
        rows.append({"VISITNUM": float(visit["visitNumber"]), "VISIT": visit["label"],
                     "VISITDY": day, "ARMCD": None, "TVSTRL": rule,
                     "TVENRL": "End of the visit day"})
    return rows


def _ts(design: dict, subjects: list[Subject]) -> list[dict]:
    body = design["studyDesign"]
    drug = next(i for i in body["studyInterventions"] if i["role"] != designs.PLACEBO_ROLE)
    ages = body["population"]["plannedAge"]
    dosed = [s for s in subjects if s.first_dose is not None]
    ends = [s.end_of_study for s in subjects if s.end_of_study is not None]
    consents = [s.consent for s in subjects]
    length = designs.encounters(design)[-1]["plannedDay"] - designs.encounters(design)[0][
        "plannedDay"]
    ct = ("CDISC CT", terms.CT_PACKAGE)
    iso8601 = ("ISO 8601", None)
    doses = [a["dose"] for a in designs.arms(design) if a["dose"] > 0]
    values: dict[str, tuple[str | None, str | None, tuple | None, str | None]] = {
        # code: value, value code, (reference terminology, version), null flavor
        "ACTSUB": (str(len(dosed)), None, None, None),
        "ADAPT": ("N", "C49487", ct, None),
        "ADDON": ("N", "C49487", ct, None),
        "AGEMAX": (f"P{ages['maxValue']}Y", None, iso8601, None),
        "AGEMIN": (f"P{ages['minValue']}Y", None, iso8601, None),
        "DOSFRQ": (drug["frequency"], "C25473", ct, None),
        "DOSU": (drug["unit"], "C28253", ct, None),
        "HLTSUBJI": ("N", "C49487", ct, None),
        "INTMODEL": ("PARALLEL", "C82639", ct, None),
        "INTTYPE": ("DRUG", "C1909", ct, None),
        "LENGTH": (f"P{length}D", None, iso8601, None),
        "NARMS": (str(len(body["arms"])), None, None, None),
        "PLANSUB": (str(body["population"]["plannedEnrollmentNumber"]), None, None, None),
        "RANDOM": ("Y", "C49488", ct, None),
        "ROUTE": (drug["route"], "C38288", ct, None),
        "SDTIGVER": (SDTMIG_VERSION, None, None, None),
        "SDTMVER": (SDTM_VERSION, None, None, None),
        "SENDTC": (iso(max(ends)) if ends else None, None, iso8601, None if ends else "NA"),
        "SEXPOP": ("BOTH", "C49636", ct, None),
        "SPONSOR": ("specfirst generator", None, None, None),
        "SSTDTC": (iso(min(consents)) if consents else design["study"]["startDate"], None,
                   iso8601, None),
        "STYPE": ("INTERVENTIONAL", "C98388", ct, None),
        "TBLIND": ("DOUBLE BLIND", "C15228", ct, None),
        "TCNTRL": ("PLACEBO", "C49648", ct, None),
        "TITLE": (design["study"]["label"], None, None, None),
        "TPHASE": (design["study"]["studyPhase"],
                   {"PHASE II TRIAL": "C15601", "PHASE III TRIAL": "C15602"}[
                       design["study"]["studyPhase"]], ct, None),
        "TRT": (drug["name"], None, None, None),
        "TTYPE": ("SAFETY", "C49667", ct, None),
    }
    rows = []
    for code in sorted({*values, "DOSE"}):
        name = terms.TS_PARAMETERS[code][0]
        if code == "DOSE":
            for number, dose in enumerate(doses, start=1):
                rows.append({"TSSEQ": number, "TSPARMCD": code, "TSPARM": name,
                             "TSVAL": str(dose), "TSVALNF": None, "TSVALCD": None,
                             "TSVCDREF": None, "TSVCDVER": None})
            continue
        value, value_code, reference, flavor = values[code]
        rows.append({"TSSEQ": 1, "TSPARMCD": code, "TSPARM": name, "TSVAL": value,
                     "TSVALNF": flavor, "TSVALCD": value_code,
                     "TSVCDREF": reference[0] if reference else None,
                     "TSVCDVER": reference[1] if reference else None})
    return rows


_BUILDERS = {"DM": _dm, "SE": _se, "SV": _sv, "DS": _ds, "EX": _ex, "AE": _ae, "VS": _vs,
             "TA": _ta, "TE": _te, "TV": _tv, "TS": _ts}


def build(design: dict, subjects: list[Subject],
          domains: tuple[str, ...] = SLICE_DOMAINS) -> dict[str, list[dict]]:
    """The rows of every requested domain, each row with every variable of its domain.

    Subjects must carry their identifiers and be sorted by them. A value
    that is missing is None.
    """
    study = designs.study_id(design)
    tables: dict[str, list[dict]] = {}
    for name in ORDER:
        if name not in domains:
            continue
        domain = DOMAINS[name]
        rows = []
        for row in _BUILDERS[name](design, subjects):
            full = {"STUDYID": study, "DOMAIN": name, **row}
            unknown = set(full) - {v.name for v in domain.variables}
            if unknown:
                raise KeyError(f"{name}: no metadata for {sorted(unknown)}")
            rows.append({v.name: full.get(v.name) for v in domain.variables})
        tables[name] = rows
    return tables


def study_codelists(design: dict, tables: dict[str, list[dict]]) -> dict[str, dict]:
    """Codelists that belong to the study, not to CDISC CT: name -> label and values."""
    arms = sorted(designs.arms(design), key=lambda a: a["name"])
    elements = sorted(design["studyDesign"]["elements"], key=lambda e: e["name"])
    lists = {
        "ARMCD": {"label": "Arm Code", "decode": {a["name"]: a["description"] for a in arms}},
        "ARM": {"label": "Arm", "values": [a["description"] for a in arms]},
        "ETCD": {"label": "Element Code", "decode": {e["name"]: e["label"] for e in elements}},
        "ELEMENT": {"label": "Element", "values": [e["label"] for e in elements]},
        "AEREL": {"label": "Causality",
                  "values": list(design["collection"]["adverseEvents"]["causality"])},
        "EXTRT": {"label": "Study Treatment",
                  "values": sorted({treatment_name(design, i["name"])
                                    for i in design["studyDesign"]["studyInterventions"]})},
    }
    if "TS" in tables:
        codes = sorted({(r["TSPARMCD"], r["TSPARM"]) for r in tables["TS"]})
        lists["TSPARMCD"] = {"label": "Trial Summary Parameter Test Code",
                             "decode": dict(codes), "nci": "C66738"}
        lists["TSPARM"] = {"label": "Trial Summary Parameter Test Name",
                           "values": [name for _, name in codes], "nci": "C67152"}
    return lists
