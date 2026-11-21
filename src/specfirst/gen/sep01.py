"""SEP01: the test study of issue #30, small enough to check by hand.

It is not generated data and has no clinical meaning. It stands for a
reference: one dataset, made so that P4 by class (ADR-019,
specfirst.machine.separation) has one decision of each kind to find:

- a window that four values reproduce: treatment emergence ends 35 days
  after the treatment end date, and every value from 35 to 38 gives the same
  ADaM datasets, results and table; 34 and 39 do not;
- an inert rule: the origin of the study day sets the study day of ADVS,
  and the adverse event summary reads no study day;
- a rule separated in ADaM and not in the table: the imputation of a partial
  start date changes the start date and the emergence flag of one event,
  and the subject is counted in the table by another event all the same.

Arms, in the order of the protocol: Placebo, Low Dose (10 mg), High Dose
(20 mg). All dates are in 2024, a leap year. Columns as in
`specfirst.compile.tiny`.

    P1  Placebo, dosed 01-10 to 02-08. Headache on 01-15.
    P2  Placebo, dosed 01-11 to 02-09. Rash on 03-15: 35 days after the last
        dose, the last day of a window of 35 days. No other event.
    P3  Placebo, dosed 01-12 to 02-10. No event.
    L1  Low Dose, dosed 01-10 to 02-08. Nausea on 01-20: possibly related,
        serious.
    L2  Low Dose, dosed 01-12 to 02-10. Fatigue on 03-20: 39 days after the
        last dose, one day after a window of 38 days. No other event.
    L3  Low Dose, dosed 01-12 to 02-10. Headache on 01-20; dizziness in
        2024-01, the month of the first dose, with no day.
    L4  Low Dose by randomization, dosed with High Dose 01-11 to 02-09
        (DM.ACTARM and EX). No event.
    H1  High Dose, dosed 01-10 to 02-08. Vomiting on 01-25: possibly
        related, drug withdrawn.
    H2  High Dose, dosed 01-15 to 02-13. Cardiac arrest on 02-20: serious,
        fatal.

Every subject is randomized on 2024-01-09, the reference start date of DM
(RFSTDTC), and has a disposition record (completed, 2024-04-30). The study
day from RFSTDTC is therefore not the one from the first dose. No event
starts 36 to 38 days after a last dose, so the window from 35 to 38 days
flags the same events (P2's rash in, L2's fatigue out). Under a
first-of-month imputation L3's dizziness starts on 01-01, before L3's
first dose, and is not treatment-emergent; L3 stays in the table by the
headache, which is neither related, serious, fatal nor a cause to withdraw
the drug, like the dizziness.

Gold decisions: the house defaults (`specfirst.gen.separate.house_vector`)
and two stated decisions: treatment emergence ends 35 days after the
treatment end date (ae.teae.end); an adverse event is related when its
causality is POSSIBLE or PROBABLE (ae.related.values, which has no house
default). The three other table families are not included.

`CLASSES` is what P4 by class gives on this study, decision by decision;
tests/unit/test_separation.py builds every value and holds it, and plants
one defect against each class (`PLANTS`).
"""

from __future__ import annotations

import pyarrow as pa

from specfirst.score.candidate import Data, Key

STUDY = "SEP01"
OUTPUT = "Out_AESUM"
_CODES = {"Placebo": "PBO", "Low Dose": "LOW", "High Dose": "HIGH"}
_DOSES = {"Placebo": 0.0, "Low Dose": 10.0, "High Dose": 20.0}
# The arms in the order of the protocol, as a build takes them (specfirst.gen.gold.arms_of).
ARMS = [{"code": _CODES[name], "dose": dose, "names": sorted({name, name.upper()})}
        for name, dose in _DOSES.items()]
STATED: dict[Key, dict] = {
    ("ae.teae.end", "mod-ae-emergence"): {"rule": "last_dose_plus_days", "days": 35},
    ("ae.related.values", "mod-ae-emergence"):
        {"rule": "stated_list", "values": ["POSSIBLE", "PROBABLE"]},
}

# subject: (planned arm, actual arm, first dose, last dose)
SUBJECTS = {
    "P1": ("Placebo", "Placebo", "2024-01-10", "2024-02-08"),
    "P2": ("Placebo", "Placebo", "2024-01-11", "2024-02-09"),
    "P3": ("Placebo", "Placebo", "2024-01-12", "2024-02-10"),
    "L1": ("Low Dose", "Low Dose", "2024-01-10", "2024-02-08"),
    "L2": ("Low Dose", "Low Dose", "2024-01-12", "2024-02-10"),
    "L3": ("Low Dose", "Low Dose", "2024-01-12", "2024-02-10"),
    "L4": ("Low Dose", "High Dose", "2024-01-11", "2024-02-09"),
    "H1": ("High Dose", "High Dose", "2024-01-10", "2024-02-08"),
    "H2": ("High Dose", "High Dose", "2024-01-15", "2024-02-13"),
}
# subject, term, start, causality, serious, action taken, fatal
EVENTS = [
    ("P1", "HEADACHE", "2024-01-15", "NONE", "N", "DOSE NOT CHANGED", "N"),
    ("P2", "RASH", "2024-03-15", "NONE", "N", "DOSE NOT CHANGED", "N"),
    ("L1", "NAUSEA", "2024-01-20", "POSSIBLE", "Y", "DOSE NOT CHANGED", "N"),
    ("L2", "FATIGUE", "2024-03-20", "NONE", "N", "DOSE NOT CHANGED", "N"),
    ("L3", "HEADACHE", "2024-01-20", "NONE", "N", "DOSE NOT CHANGED", "N"),
    ("L3", "DIZZINESS", "2024-01", "NONE", "N", "DOSE NOT CHANGED", "N"),
    ("H1", "VOMITING", "2024-01-25", "POSSIBLE", "N", "DRUG WITHDRAWN", "N"),
    ("H2", "CARDIAC ARREST", "2024-02-20", "NONE", "Y", "NOT APPLICABLE", "Y"),
]

# The adverse event summary of the gold decisions, by hand. The first row is the header
# row: the subjects of the safety set in each column (by actual treatment: L4 is High Dose).
_ROWS = ("Any adverse event", "Related adverse event", "Serious adverse event",
         "Adverse event leading to discontinuation of study treatment", "Fatal adverse event")
_COLUMNS = ("Placebo", "Low Dose", "High Dose", "Total")
EXPECTED = {
    "": ("(N=3)", "(N=3)", "(N=3)", "(N=9)"),
    _ROWS[0]: ("2 ( 66.7)", "2 ( 66.7)", "2 ( 66.7)", "6 ( 66.7)"),
    _ROWS[1]: ("0", "1 ( 33.3)", "1 ( 33.3)", "2 ( 22.2)"),
    _ROWS[2]: ("0", "1 ( 33.3)", "1 ( 33.3)", "2 ( 22.2)"),
    _ROWS[3]: ("0", "0", "1 ( 33.3)", "1 ( 11.1)"),
    _ROWS[4]: ("0", "0", "1 ( 33.3)", "1 ( 11.1)"),
}

# What P4 by class gives on SEP01, decision by decision: what the mutation finds, not what
# the author expected; tests/unit/test_separation.py builds every value and holds it. The
# three the study is made for are named in the docstring. The others, in short: the data
# have one exposure record per subject with full dates and no times, every subject is
# randomized, no percent lies on a half, the protocol order is the order of the dose, no
# causality is PROBABLE, and the table counts the safety set by actual treatment. The
# example "Active Control" of tfl.columns.total names no arm of the study, so a total over
# the arms but that control is the total over all arms.
CLASSES: dict[Key, str] = {
    ("trt.planned.source", "mod-treatment"): "inert",
    ("trt.actual.source", "mod-treatment"): "separated",
    ("trt.start.source", "mod-treatment"): "unseparated",
    ("trt.end.source", "mod-treatment"): "unseparated",
    ("trt.date.imputation", "mod-treatment"): "unseparated",
    ("date.studyday.origin", "mod-treatment"): "inert",
    ("pop.randomized.rule", "mod-populations"): "inert",
    ("pop.safety.rule", "mod-populations"): "unseparated",
    ("pop.safety.grouping", "mod-populations"): "separated",
    ("pop.efficacy.rule", "mod-populations"): "inert",
    ("disp.status.record", "mod-populations"): "inert",
    ("ae.start.imputation", "mod-ae-emergence"): "separated_at_dataset_only",
    ("ae.teae.start", "mod-ae-emergence"): "unseparated",
    ("ae.teae.end", "mod-ae-emergence"): "unseparated",
    ("ae.related.values", "mod-ae-emergence"): "unseparated",
    ("tfl.output.include", "tfl-ae-summary"): "separated",
    ("tfl.population", "tfl-ae-summary"): "separated",
    ("tfl.columns.arms", "tfl-ae-summary"): "unseparated",
    ("tfl.columns.total", "tfl-ae-summary"): "unseparated",
    ("tfl.percent.format", "tfl-ae-summary"): "separated",
    ("tfl.rounding.rule", "tfl-ae-summary"): "unseparated",
    ("tfl.ae.summary.rows", "tfl-ae-summary"): "separated",
}
WINDOW: Key = ("ae.teae.end", "mod-ae-emergence")
INTERVAL = {"slot": "days", "gold": 35, "low": 35, "high": 38, "below": "separated",
            "above": "separated", "same": [36, 37, 38], "dataset_only": []}

# The planted defects (rule R5): a variant of the study, or of the reach, under which the
# check of one class fails. Each names the decision it is held against.
PLANTS = {
    "separated": "L4 dosed as randomized: pop.safety.grouping no longer separates",
    "unseparated": "an event 36 days after P3's last dose: no other window reproduces",
    "separated_at_dataset_only": "L3's dizziness with a full date: every imputation gives "
                                 "the same build",
    "inert": "a reach that names no element for any output: every decision looks inert, "
             "and a value that changes the table is a defect",
}


# Which decision each planted defect is held against.
PLANTED_DECISION: dict[str, Key] = {
    "separated": ("pop.safety.grouping", "mod-populations"),
    "unseparated": WINDOW,
    "separated_at_dataset_only": ("ae.start.imputation", "mod-ae-emergence"),
    "inert": ("date.studyday.origin", "mod-treatment"),
}


def expected_cells() -> dict[tuple[str, str], str]:
    """The expected text of every cell, by row label and column header."""
    return {(row, column): text for row, texts in EXPECTED.items()
            for column, text in zip(_COLUMNS, texts, strict=True)}


def check(matrix: dict) -> list[str]:
    """Where a matrix of SEP01 is not what the study states: a class other than
    `CLASSES` gives, an interval of the window other than `INTERVAL`, a problem of the
    matrix itself (specfirst.machine.separation.problems). A matrix of some decisions
    only is held for those."""
    found = list(matrix["problems"])
    for item in matrix["decisions"]:
        key = (item["id"], item["unit"])
        if key not in CLASSES:
            found.append(f"{key[0]} ({key[1]}): not a decision of the study")
        elif item["class"] != CLASSES[key]:
            found.append(f"{key[0]} ({key[1]}): {item['class']}; the study states "
                         f"{CLASSES[key]}")
        if key == WINDOW and item["intervals"] != [INTERVAL]:
            found.append(f"{key[0]} ({key[1]}): the interval is {item['intervals']}; the "
                         f"study states {INTERVAL}")
    return found


def _table(names: list[str], rows: list[tuple], types: dict[str, pa.DataType]) -> pa.Table:
    columns = {name: [row[index] for row in rows] for index, name in enumerate(names)}
    return pa.table({name: pa.array(values, type=types.get(name, pa.string()))
                     for name, values in columns.items()})


def tables(subjects: dict | None = None, events: list | None = None) -> dict[str, pa.Table]:
    """The six SDTM domains of the study, by file stem (or of a planted variant)."""
    subjects = SUBJECTS if subjects is None else subjects
    events = EVENTS if events is None else events
    number, integer = pa.float64(), pa.int64()
    dm, ex, ds, sv, vs, ae = [], [], [], [], [], []
    for order, (subject, (planned, actual, first, last)) in enumerate(subjects.items(), start=1):
        dm.append((STUDY, subject, subject[1:], "01", 60.0 + order, "YEARS",
                   "F" if order % 2 else "M", "WHITE", "NOT HISPANIC OR LATINO", planned,
                   _CODES[planned], actual, "2024-01-09", first))
        ex.append((STUDY, subject, 1, actual.upper(), _DOSES[actual], first, last))
        sv.append((STUDY, subject, "BASELINE", 2.0, first))
        vs.append((STUDY, subject, 1, "WEIGHT", "Weight", 70.0 + order, "", first,
                   "BASELINE", 2.0, 1.0))
        vs.append((STUDY, subject, 2, "HEIGHT", "Height", 165.0 + order, "", first,
                   "BASELINE", 2.0, 1.0))
        ds.append((STUDY, subject, 1, "PROTOCOL MILESTONE", None, "RANDOMIZED", "2024-01-09"))
        ds.append((STUDY, subject, 2, "DISPOSITION EVENT", "STUDY PARTICIPATION",
                   "COMPLETED", "2024-04-30"))
    counts: dict[str, int] = {}
    for subject, term, start, causality, serious, action, fatal in events:
        counts[subject] = counts.get(subject, 0) + 1
        ae.append((STUDY, subject, counts[subject], term.title(), term, "GENERAL DISORDERS",
                   "MILD", serious, causality, action,
                   "FATAL" if fatal == "Y" else "RECOVERED/RESOLVED", fatal, start, None))
    return {
        "dm": _table(["STUDYID", "USUBJID", "SUBJID", "SITEID", "AGE", "AGEU", "SEX", "RACE",
                      "ETHNIC", "ARM", "ARMCD", "ACTARM", "RFSTDTC", "RFXSTDTC"], dm,
                     {"AGE": number}),
        "ex": _table(["STUDYID", "USUBJID", "EXSEQ", "EXTRT", "EXDOSE", "EXSTDTC", "EXENDTC"],
                     ex, {"EXSEQ": integer, "EXDOSE": number}),
        "ds": _table(["STUDYID", "USUBJID", "DSSEQ", "DSCAT", "DSSCAT", "DSDECOD", "DSSTDTC"],
                     ds, {"DSSEQ": integer}),
        "sv": _table(["STUDYID", "USUBJID", "VISIT", "VISITNUM", "SVSTDTC"], sv,
                     {"VISITNUM": number}),
        "vs": _table(["STUDYID", "USUBJID", "VSSEQ", "VSTESTCD", "VSTEST", "VSSTRESN",
                      "VSSTRESU", "VSDTC", "VISIT", "VISITNUM", "VISITDY"], vs,
                     {"VSSEQ": integer, "VSSTRESN": number, "VISITNUM": number,
                      "VISITDY": number}),
        "ae": _table(["STUDYID", "USUBJID", "AESEQ", "AETERM", "AEDECOD", "AESOC", "AESEV",
                      "AESER", "AEREL", "AEACN", "AEOUT", "AESDTH", "AESTDTC", "AEENDTC"], ae,
                     {"AESEQ": integer}),
    }


def data() -> Data:
    return Data(f"{STUDY.lower()}/reference", sdtm=tables())


def planted(name: str) -> Data:
    """A planted variant of the data (`PLANTS`); `inert` plants the reach, not the data."""
    subjects, events = dict(SUBJECTS), list(EVENTS)
    if name == "separated":
        subjects["L4"] = ("Low Dose", "Low Dose", "2024-01-11", "2024-02-09")
    elif name == "unseparated":
        # 36 days after P3's last dose of 02-10.
        events.append(("P3", "COUGH", "2024-03-17", "NONE", "N", "DOSE NOT CHANGED", "N"))
    elif name == "separated_at_dataset_only":
        events = [(*event[:2], "2024-01-20", *event[3:]) if event[:2] == ("L3", "DIZZINESS")
                  else event for event in events]
    else:
        raise ValueError(f"no planted data {name!r}")
    return Data(f"{STUDY.lower()}/planted-{name}", sdtm=tables(subjects, events))


def records(catalog, house) -> list[dict]:
    """The gold decision vector: id, unit and value, in catalog order."""
    from specfirst.gen.separate import house_vector

    return house_vector(catalog, house, STATED)
