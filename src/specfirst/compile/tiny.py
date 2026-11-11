"""A tiny hand-made SDTM study for tests: four subjects, six domains.

It is not generated data and has no clinical meaning. Each record is there
to exercise one rule of the house parent specs or of a catalog decision.

    S1  randomized to Low Dose and dosed from 2024-03-10T08:00 to 2024-04-20;
        a third exposure record has partial dates (2024-03 to 2024-05)
    S2  randomized to Placebo and dosed from 2024-03-12; partial dates
    S3  randomized to Low Dose and never dosed
    S4  dosed without being randomized; no exposure end date
"""

from __future__ import annotations

from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

STUDY = "TINY01"

DM = [
    # USUBJID, AGE, SEX, RACE, ETHNIC, ARM, ARMCD, ACTARM, RFSTDTC, RFXSTDTC
    ("S1", 65.0, "F", "WHITE", "NOT HISPANIC OR LATINO", "Low Dose", "LOW", "Low Dose",
     "2024-03-08", "2024-03-10T08:00"),
    ("S2", 80.0, "M", "ASIAN", "NOT HISPANIC OR LATINO", "Placebo", "PBO", "Placebo",
     "2024-03-12", "2024-03-12"),
    ("S3", 81.0, "M", "WHITE", "HISPANIC OR LATINO", "Low Dose", "LOW", "Low Dose",
     "2024-03-15", None),
    ("S4", 50.0, "F", "WHITE", "NOT HISPANIC OR LATINO", "Not Assigned", "NOTASSGN", "Low Dose",
     "2024-03-20", "2024-03-20"),
]

EX = [
    # USUBJID, EXSEQ, EXTRT, EXDOSE, EXSTDTC, EXENDTC
    ("S1", 1, "Low Dose", 10.0, "2024-03-10T08:00", "2024-03-31"),
    ("S1", 2, "Low Dose", 10.0, "2024-04-01", "2024-04-20"),
    ("S1", 3, "Low Dose", 10.0, "2024-03", "2024-05"),  # partial dates
    ("S1", 4, "Low Dose", 10.0, "2024---15", "--04-25"),  # a missing part in the middle
    ("S4", 1, "Low Dose", 10.0, "2024-03-20", None),
    ("S2", 1, "PLACEBO", 0.0, "2024-03-12", "2024-04-30"),
]

DS = [
    # USUBJID, DSSEQ, DSCAT, DSSCAT, DSDECOD, DSSTDTC
    ("S1", 1, "PROTOCOL MILESTONE", None, "RANDOMIZED", "2024-03-08"),
    ("S1", 2, "DISPOSITION EVENT", "STUDY PARTICIPATION", "COMPLETED", "2024-05-01"),
    ("S2", 1, "DISPOSITION EVENT", "STUDY PARTICIPATION", "ADVERSE EVENT", "2024-05-02"),
    ("S4", 1, "DISPOSITION EVENT", "STUDY PARTICIPATION", "COMPLETED", "2024-04-15"),
]

SV = [
    # USUBJID, VISIT, VISITNUM, SVSTDTC
    ("S1", "SCREENING", 1.0, "2024-03-01"),
    ("S1", "BASELINE", 2.0, "2024-03-10"),
    ("S1", "WEEK 2", 3.0, "2024-03-24"),
    ("S1", "WEEK 4", 4.0, "2024-04-08"),
    ("S2", "BASELINE", 2.0, "2024-03-12"),
    ("S2", "WEEK 2", 3.0, "2024-03-26"),
]

VS = [
    # USUBJID, VSSEQ, VSTESTCD, VSTEST, VSSTRESN, VSDTC, VISIT, VISITNUM, VISITDY
    ("S1", 1, "SYSBP", "Systolic BP", 120.0, "2024-03-01", "SCREENING", 1.0, -7.0),
    ("S1", 2, "SYSBP", "Systolic BP", 124.0, "2024-03-10T07:30", "BASELINE", 2.0, 1.0),
    ("S1", 3, "SYSBP", "Systolic BP", 130.0, "2024-03-10T09:00", "BASELINE", 2.0, 1.0),
    ("S1", 4, "SYSBP", "Systolic BP", 128.0, "2024-03-24", "WEEK 2", 3.0, 15.0),
    ("S1", 5, "SYSBP", "Systolic BP", 126.0, "2024-03-26", "UNSCHEDULED 3.1", 3.1, None),
    ("S1", 6, "SYSBP", "Systolic BP", 122.0, "2024-04-08", "WEEK 4", 4.0, 29.0),
    ("S1", 7, "SYSBP", "Systolic BP", 118.0, "2024-04-25", "WEEK 6", 5.0, 43.0),
    ("S1", 8, "WEIGHT", "Weight", 70.0, "2024-03-01", "SCREENING", 1.0, -7.0),
    ("S1", 9, "WEIGHT", "Weight", 71.0, "2024-03-10", "BASELINE", 2.0, 1.0),
    ("S1", 10, "HEIGHT", "Height", 170.0, "2024-03-01", "SCREENING", 1.0, -7.0),
    ("S1", 11, "SYSBP", "Systolic BP", 125.0, "2024-04-06", "UNSCHEDULED 3.2", 3.2, None),
    ("S2", 1, "SYSBP", "Systolic BP", 140.0, "2024-03-11", "UNSCHEDULED 1.1", 1.1, None),
    ("S2", 2, "SYSBP", "Systolic BP", 138.0, "2024-03-26", "WEEK 2", 3.0, 15.0),
    ("S2", 3, "WEIGHT", "Weight", 82.5, "2024-03-12", "BASELINE", 2.0, 1.0),
    ("S2", 4, "HEIGHT", "Height", 180.0, "2024-03-12", "BASELINE", 2.0, 1.0),
]

AE = [
    # USUBJID, AESEQ, AEDECOD, AESOC, AESER, AEREL, AEACN, AESDTH, AESTDTC, AEENDTC
    ("S1", 1, "HEADACHE", "NERVOUS SYSTEM DISORDERS", "N", "POSSIBLE", "DOSE NOT CHANGED", "N",
     "2024-03-05", "2024-03-06"),
    ("S1", 2, "NAUSEA", "GASTROINTESTINAL DISORDERS", "N", "NONE", "DOSE NOT CHANGED", "N",
     "2024-03-10", None),
    ("S1", 3, "HEADACHE", "NERVOUS SYSTEM DISORDERS", "Y", "PROBABLE", "DRUG WITHDRAWN", "N",
     "2024-05-25", None),
    ("S2", 1, "RASH", "SKIN AND SUBCUTANEOUS TISSUE DISORDERS", "N", "NONE", "DOSE NOT CHANGED",
     "N", "2024-03", None),
    ("S2", 2, "HEADACHE", "NERVOUS SYSTEM DISORDERS", "N", "NONE", "DOSE NOT CHANGED", "N",
     "2024-05-02", None),
    ("S2", 3, "NAUSEA", "GASTROINTESTINAL DISORDERS", "N", "NONE", "DOSE NOT CHANGED", "N",
     "2024-05-03", None),
    ("S3", 1, "FATIGUE", "GENERAL DISORDERS", "N", "NONE", "NOT APPLICABLE", "N",
     "2024-03-20", None),
]


def _table(names: list[str], rows: list[tuple], types: dict[str, pa.DataType]) -> pa.Table:
    columns = {name: [row[index] for row in rows] for index, name in enumerate(names)}
    return pa.table({name: pa.array(values, type=types.get(name, pa.string()))
                     for name, values in columns.items()})


def tables() -> dict[str, pa.Table]:
    """The six SDTM domains as Arrow tables."""
    number, integer = pa.float64(), pa.int64()

    def with_study(rows: list[tuple]) -> list[tuple]:
        return [(STUDY, *row) for row in rows]

    dm = [(STUDY, usubjid, usubjid[1:], "01", age, "YEARS", *rest)
          for usubjid, age, *rest in DM]
    ae = [(STUDY, usubjid, seq, decod.title(), decod, soc, "MILD", ser, rel, acn,
           "RECOVERED/RESOLVED", dth, start, end)
          for usubjid, seq, decod, soc, ser, rel, acn, dth, start, end in AE]
    vs = [(STUDY, usubjid, seq, code, test, value, "", dtc, visit, visitnum, visitdy)
          for usubjid, seq, code, test, value, dtc, visit, visitnum, visitdy in VS]
    return {
        "dm": _table(["STUDYID", "USUBJID", "SUBJID", "SITEID", "AGE", "AGEU", "SEX", "RACE",
                      "ETHNIC", "ARM", "ARMCD", "ACTARM", "RFSTDTC", "RFXSTDTC"], dm,
                     {"AGE": number}),
        "ex": _table(["STUDYID", "USUBJID", "EXSEQ", "EXTRT", "EXDOSE", "EXSTDTC", "EXENDTC"],
                     with_study(EX), {"EXSEQ": integer, "EXDOSE": number}),
        "ds": _table(["STUDYID", "USUBJID", "DSSEQ", "DSCAT", "DSSCAT", "DSDECOD", "DSSTDTC"],
                     with_study(DS), {"DSSEQ": integer}),
        "sv": _table(["STUDYID", "USUBJID", "VISIT", "VISITNUM", "SVSTDTC"], with_study(SV),
                     {"VISITNUM": number}),
        "vs": _table(["STUDYID", "USUBJID", "VSSEQ", "VSTESTCD", "VSTEST", "VSSTRESN",
                      "VSSTRESU", "VSDTC", "VISIT", "VISITNUM", "VISITDY"], vs,
                     {"VSSEQ": integer, "VSSTRESN": number, "VISITNUM": number,
                      "VISITDY": number}),
        "ae": _table(["STUDYID", "USUBJID", "AESEQ", "AETERM", "AEDECOD", "AESOC", "AESEV",
                      "AESER", "AEREL", "AEACN", "AEOUT", "AESDTH", "AESTDTC", "AEENDTC"], ae,
                     {"AESEQ": integer}),
    }


def write(folder: Path) -> None:
    """Write the six domains as parquet files into a folder."""
    folder.mkdir(parents=True, exist_ok=True)
    for name, table in tables().items():
        pq.write_table(table, folder / f"{name}.parquet")
