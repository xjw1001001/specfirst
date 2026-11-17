"""HAND01: a hand-made study for the scorer, small enough to check by hand.

It is not generated data and has no clinical meaning (PLAN.md section 13.6:
"Start on the pilot and on hand-made fixtures"). Three arms, two datasets
of seven and nine subjects, six SDTM domains with the columns of
`specfirst.compile.tiny`. Every record is there for one decision of the
slice "adverse event summary first" (ADR-005), and the twin holds what the
visible data lack, as a kit's twin does (section 6.5).

Arms, in the order of the protocol: Low Dose (10 mg), High Dose (20 mg),
Placebo. All dates are in 2024, a leap year.

Visible data

    P1  Placebo, dosed 01-10 to 02-08. Headache on 01-15.
    P2  Placebo, dosed 01-11 to 02-09. No event.
    L1  Low Dose, dosed 01-10 to 02-08. Nausea on 01-20: possibly related,
        serious. Rash on 03-09, the 30th day after the last dose.
    L2  Low Dose, dosed 01-12 to 02-10. Dizziness from 01-05 to 01-06,
        before the first dose.
    L3  Low Dose, randomized and never dosed. Fatigue on 01-20.
    H1  High Dose, dosed 01-10 to 02-08. Vomiting on 01-25: possibly
        related, drug withdrawn.
    H2  High Dose, dosed 01-15 to 02-13. Headache on 02-01. Cardiac arrest
        on 02-20: serious, fatal.

Twin

    P1  Placebo, dosed 01-10 to 02-08. Headache on 01-15.
    P2  Placebo, dosed 01-11 to 02-09. Rash on 03-11, the 31st day after
        the last dose: outside a window of 30 days.
    P3  Placebo, dosed 01-12 to 02-10. No event.
    L1  Low Dose, dosed 01-10 to 02-08. Nausea on 01-20: probably related,
        a causality the visible data do not have.
    L2  Low Dose, dosed 01-12 to 02-10. Dizziness on 01-18: possibly
        related, serious.
    L3  Low Dose, randomized and never dosed. Fatigue on 01-20.
    H1  High Dose, dosed 01-10 to 02-08. Vomiting on 01-25: drug withdrawn.
    H2  High Dose, dosed 01-15 to 02-13. No event.
    X1  dosed with High Dose from 01-16 to 02-14 without being randomized.
        Headache on 01-30.

Gold decisions: the house defaults, and two stated decisions. An adverse
event is related when its causality is POSSIBLE or PROBABLE
(ae.related.values has no default). Treatment emergence ends 30 days after
the treatment end date (ae.teae.end). The three other table families are
not part of the planned outputs.

`EXPECTED` is the adverse event summary these decisions give, worked out by
hand from the lists above; tests/unit/test_score_hand.py holds the build
against it.
"""

from __future__ import annotations

import pyarrow as pa

from specfirst.compile import house as houses
from specfirst.compile.catalog import Catalog
from specfirst.compile.standard_form import StandardForm, decision_record
from specfirst.score.candidate import Data
from specfirst.score.display0 import Arm
from specfirst.score.reading import Documents

STUDY = "HAND01"
UNITS = ("mod-treatment", "mod-populations", "mod-ae-emergence", "tfl-ae-summary")
OUTPUT = "Out_AESUM"
ARMS = (Arm("Low Dose", 10.0, 1), Arm("High Dose", 20.0, 2), Arm("Placebo", 0.0, 3))
_CODES = {"Placebo": "PBO", "Low Dose": "LOW", "High Dose": "HIGH"}

# The decisions the documents of the study state; every other decision of the
# scope and of mod-demographics is the house default.
STATED = {
    ("ae.related.values", "mod-ae-emergence"):
        {"rule": "stated_list", "values": ["POSSIBLE", "PROBABLE"]},
    ("ae.teae.end", "mod-ae-emergence"): {"rule": "last_dose_plus_days", "days": 30},
    ("tfl.output.include", "tfl-demographics"): {"rule": "not_included"},
    ("tfl.output.include", "tfl-ae-soc-pt"): {"rule": "not_included"},
    ("tfl.output.include", "tfl-vitals-by-visit"): {"rule": "not_included"},
}
# Units whose decisions the compiled ADaM specs need although the slice does
# not score them: ADSL has columns that mod-demographics writes, and a decision
# of the slice (the origin of the study day) writes into ADVS, which then needs
# every decision of mod-bds-visits. Where such a decision has no house default
# the study states the first alternative of the catalog with its first example.
BUILT_UNITS = (*UNITS, "mod-demographics", "mod-bds-visits")

# subject: (planned arm, actual arm or None when never dosed, first dose, last dose)
# A planned arm of None is a subject who was dosed without being randomized.
SUBJECTS = {
    "visible": {
        "P1": ("Placebo", "Placebo", "2024-01-10", "2024-02-08"),
        "P2": ("Placebo", "Placebo", "2024-01-11", "2024-02-09"),
        "L1": ("Low Dose", "Low Dose", "2024-01-10", "2024-02-08"),
        "L2": ("Low Dose", "Low Dose", "2024-01-12", "2024-02-10"),
        "L3": ("Low Dose", None, None, None),
        "H1": ("High Dose", "High Dose", "2024-01-10", "2024-02-08"),
        "H2": ("High Dose", "High Dose", "2024-01-15", "2024-02-13"),
    },
    "twin": {
        "P1": ("Placebo", "Placebo", "2024-01-10", "2024-02-08"),
        "P2": ("Placebo", "Placebo", "2024-01-11", "2024-02-09"),
        "P3": ("Placebo", "Placebo", "2024-01-12", "2024-02-10"),
        "L1": ("Low Dose", "Low Dose", "2024-01-10", "2024-02-08"),
        "L2": ("Low Dose", "Low Dose", "2024-01-12", "2024-02-10"),
        "L3": ("Low Dose", None, None, None),
        "H1": ("High Dose", "High Dose", "2024-01-10", "2024-02-08"),
        "H2": ("High Dose", "High Dose", "2024-01-15", "2024-02-13"),
        "X1": (None, "High Dose", "2024-01-16", "2024-02-14"),
    },
}

# subject, term, start, end, causality, serious, action taken, fatal
EVENTS = {
    "visible": [
        ("P1", "HEADACHE", "2024-01-15", None, "NONE", "N", "DOSE NOT CHANGED", "N"),
        ("L1", "NAUSEA", "2024-01-20", None, "POSSIBLE", "Y", "DOSE NOT CHANGED", "N"),
        ("L1", "RASH", "2024-03-09", None, "NONE", "N", "DOSE NOT CHANGED", "N"),
        ("L2", "DIZZINESS", "2024-01-05", "2024-01-06", "NONE", "N", "NOT APPLICABLE", "N"),
        ("L3", "FATIGUE", "2024-01-20", None, "NONE", "N", "NOT APPLICABLE", "N"),
        ("H1", "VOMITING", "2024-01-25", None, "POSSIBLE", "N", "DRUG WITHDRAWN", "N"),
        ("H2", "HEADACHE", "2024-02-01", None, "NONE", "N", "DOSE NOT CHANGED", "N"),
        ("H2", "CARDIAC ARREST", "2024-02-20", None, "NONE", "Y", "NOT APPLICABLE", "Y"),
    ],
    "twin": [
        ("P1", "HEADACHE", "2024-01-15", None, "NONE", "N", "DOSE NOT CHANGED", "N"),
        ("P2", "RASH", "2024-03-11", None, "NONE", "N", "DOSE NOT CHANGED", "N"),
        ("L1", "NAUSEA", "2024-01-20", None, "PROBABLE", "N", "DOSE NOT CHANGED", "N"),
        ("L2", "DIZZINESS", "2024-01-18", None, "POSSIBLE", "Y", "DOSE NOT CHANGED", "N"),
        ("L3", "FATIGUE", "2024-01-20", None, "NONE", "N", "NOT APPLICABLE", "N"),
        ("H1", "VOMITING", "2024-01-25", None, "NONE", "N", "DRUG WITHDRAWN", "N"),
        ("X1", "HEADACHE", "2024-01-30", None, "NONE", "N", "DOSE NOT CHANGED", "N"),
    ],
}

_ROWS = ("Any adverse event", "Related adverse event", "Serious adverse event",
         "Adverse event leading to discontinuation of study treatment", "Fatal adverse event")
_COLUMNS = ("Placebo", "Low Dose", "High Dose", "Total")
# The adverse event summary of the gold decisions, by hand. The first row is the
# header row: the subjects of the safety set in each column.
EXPECTED = {
    "visible": {
        "": ("(N=2)", "(N=2)", "(N=2)", "(N=6)"),
        _ROWS[0]: ("1 ( 50.0)", "1 ( 50.0)", "2 ( 100.0)", "4 ( 66.7)"),
        _ROWS[1]: ("0", "1 ( 50.0)", "1 ( 50.0)", "2 ( 33.3)"),
        _ROWS[2]: ("0", "1 ( 50.0)", "1 ( 50.0)", "2 ( 33.3)"),
        _ROWS[3]: ("0", "0", "1 ( 50.0)", "1 ( 16.7)"),
        _ROWS[4]: ("0", "0", "1 ( 50.0)", "1 ( 16.7)"),
    },
    "twin": {
        "": ("(N=3)", "(N=2)", "(N=3)", "(N=8)"),
        _ROWS[0]: ("1 ( 33.3)", "2 ( 100.0)", "2 ( 66.7)", "5 ( 62.5)"),
        _ROWS[1]: ("0", "2 ( 100.0)", "0", "2 ( 25.0)"),
        _ROWS[2]: ("0", "1 ( 50.0)", "0", "1 ( 12.5)"),
        _ROWS[3]: ("0", "0", "1 ( 33.3)", "1 ( 12.5)"),
        _ROWS[4]: ("0", "0", "0", "0"),
    },
}


def expected_cells(which: str) -> dict[tuple[str, str], str]:
    """The expected text of every cell, by row label and column header."""
    return {(row, column): text for row, texts in EXPECTED[which].items()
            for column, text in zip(_COLUMNS, texts, strict=True)}


def _table(names: list[str], rows: list[tuple], types: dict[str, pa.DataType]) -> pa.Table:
    columns = {name: [row[index] for row in rows] for index, name in enumerate(names)}
    return pa.table({name: pa.array(values, type=types.get(name, pa.string()))
                     for name, values in columns.items()})


def tables(which: str) -> dict[str, pa.Table]:
    """The six SDTM domains of one dataset of the study, by file stem."""
    number, integer = pa.float64(), pa.int64()
    dm, ex, ds, sv, vs, ae = [], [], [], [], [], []
    for order, (subject, (planned, actual, first, last)) in enumerate(
            SUBJECTS[which].items(), start=1):
        arm = planned or "Not Assigned"
        code = _CODES.get(planned, "NOTASSGN")
        dm.append((STUDY, subject, subject[1:], "01", 60.0 + order, "YEARS",
                   "F" if order % 2 else "M", "WHITE", "NOT HISPANIC OR LATINO", arm, code,
                   actual or arm, first or "2024-01-09", first))
        if first:
            dose = 0.0 if actual == "Placebo" else next(
                a.dose for a in ARMS if a.label == actual)
            ex.append((STUDY, subject, 1, actual.upper(), dose, first, last))
            sv.append((STUDY, subject, "BASELINE", 2.0, first))
            vs.append((STUDY, subject, 1, "WEIGHT", "Weight", 70.0 + order, "", first,
                       "BASELINE", 2.0, 1.0))
            vs.append((STUDY, subject, 2, "HEIGHT", "Height", 165.0 + order, "", first,
                       "BASELINE", 2.0, 1.0))
        sequence = 1
        if planned:
            ds.append((STUDY, subject, sequence, "PROTOCOL MILESTONE", None, "RANDOMIZED",
                       "2024-01-09"))
            sequence += 1
        ds.append((STUDY, subject, sequence, "DISPOSITION EVENT", "STUDY PARTICIPATION",
                   "COMPLETED", "2024-04-30"))
    counts: dict[str, int] = {}
    for subject, term, start, end, causality, serious, action, fatal in EVENTS[which]:
        counts[subject] = counts.get(subject, 0) + 1
        ae.append((STUDY, subject, counts[subject], term.title(), term, "GENERAL DISORDERS",
                   "MILD", serious, causality, action,
                   "FATAL" if fatal == "Y" else "RECOVERED/RESOLVED", fatal, start, end))
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


def data(which: str) -> Data:
    return Data(f"{STUDY.lower()}/{which}", sdtm=tables(which))


def gold_values(catalog: Catalog, house: houses.House) -> list[dict]:
    """The gold decision vector: id, unit and value, in catalog order."""
    found = []
    for key in catalog.keys():
        if key in STATED:
            value = STATED[key]
        elif key[1] in BUILT_UNITS:
            value = houses.default_value(catalog, house, *key)
            if value is None and key[1] not in UNITS:
                alternative = catalog.entry(key[0]).alternatives[0]
                value = {"rule": alternative.id,
                         **{slot.name: slot.examples[0] for slot in alternative.slots}}
        else:
            value = None
        if value is not None:
            found.append({"id": key[0], "unit": key[1], "value": value})
    return found


SAP_TITLE = "Statistical analysis plan of the study HAND01, in standard form"


def sap(catalog: Catalog, house: houses.House) -> str:
    """The statistical analysis plan in standard form: the decisions the study states.

    The tier is `standard` (section 6.6): the house defaults stand only in
    the house standards document.
    """
    stated = [record for record in gold_values(catalog, house)
              if not _is_default(catalog, house, record)]
    return StandardForm(catalog).render_document("sap", SAP_TITLE, stated)


def _is_default(catalog: Catalog, house: houses.House, record: dict) -> bool:
    return record["value"] == houses.default_value(catalog, house, record["id"], record["unit"])


def documents(catalog: Catalog, house: houses.House) -> Documents:
    return Documents({"sap": sap(catalog, house),
                      houses.DOCUMENT_ID: houses.standards_document(catalog, house)})


def gold_records(catalog: Catalog, house: houses.House) -> list[dict]:
    """The gold decision records: stated decisions cite the plan, defaults the house
    standard. Every one is marked as the machine would mark it: `separated`, but
    for the two decisions no record of this study can show."""
    form = StandardForm(catalog)
    _, stated = form.parse_document(sap(catalog, house))
    by_key = {(item["id"], item["unit"]): decision_record(item, "sap", "stated", "document_rule")
              for item in stated}
    defaults = {(r["id"], r["unit"]): r for r in houses.default_decisions(catalog, house)}
    found = []
    for record in gold_values(catalog, house):
        key = (record["id"], record["unit"])
        full = dict(by_key[key] if key in by_key else defaults[key])
        if full["value"] != record["value"]:
            raise ValueError(f"{key[0]}: the documents do not state the gold value")
        if key[1] in UNITS:
            full["identifiable"] = "unseparated" if key[0] in UNSEPARATED else "separated"
        found.append(full)
    return found


# Decisions of the scope whose alternatives give the same adverse event summary on
# both datasets of this study, whatever the candidate chooses: the study day is on
# no table of the slice (docs/state/gen.md), and no percent of these 16 subjects
# lies on a half at one decimal.
UNSEPARATED = ("date.studyday.origin", "tfl.rounding.rule")


def case(catalog: Catalog, house: houses.House, stage: str = "C"):
    """The study as a case of the scorer (specfirst.score.scorer).

    Stage C scores the four units of the slice. Stage T scores the table
    decisions alone, on the ADaM datasets of gold (ADR-005, decision 2).
    """
    from specfirst.score.scorer import Case

    units = UNITS if stage == "C" else tuple(unit for unit in UNITS if unit.startswith("tfl-"))
    return Case(id=STUDY.lower(), units=units, gold=gold_records(catalog, house), arms=ARMS,
                data={which: data(which) for which in ("visible", "twin")},
                documents=documents(catalog, house), stage=stage)
