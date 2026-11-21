"""The parents of open-default@2 on the tiny study and on changed copies of it.

The gate check "yamaa run" shows that every alternative of catalog@2 runs on
the tiny study; these cases build (catalog@2, open-default@2) on data that
reach the rules of the parents that ADR-020 added: randomization from the
disposition record and its study-level fallback (#10), PARAM per parameter
and AVALU (#17), no end-of-study status for a screen failure (#17), AEBODSYS
(#17) and the first occurrence by date, then sequence (#17).
"""

from __future__ import annotations

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq
import pytest

from specfirst.compile import checks, tiny
from specfirst.compile import house as house_module
from specfirst.compile.compiler import compile_decisions, relative_reference

KEYS = {"ADSL": ["USUBJID"], "ADAE": ["USUBJID", "AESEQ"],
        "ADVS": ["USUBJID", "PARAMCD", "VSSEQ", "DTYPE"]}


@pytest.fixture(scope="module")
def standard(root):
    catalog, house = house_module.load_pair(root, "catalog@2", "open-default@2")
    return catalog, house, checks.base_vector(catalog, house)


def _set(table: pa.Table, column: str, values: list) -> pa.Table:
    index = table.column_names.index(column)
    return table.set_column(index, column, pa.array(values, type=table.schema.field(column).type))


def _without_randomized(tables: dict) -> dict:
    ds = tables["ds"]
    return {**tables, "ds": ds.filter(pc.not_equal(ds["DSDECOD"], "RANDOMIZED"))}


def _units(tables: dict) -> dict:
    vs = tables["vs"]
    units = []
    for code, seq, subject in zip(vs["VSTESTCD"].to_pylist(), vs["VSSEQ"].to_pylist(),
                                  vs["USUBJID"].to_pylist(), strict=True):
        if code == "SYSBP":
            units.append("" if (subject, seq) == ("S1", 4) else "mmHg")
        else:
            units.append("kg" if code == "WEIGHT" else "")
    return {**tables, "vs": _set(vs, "VSSTRESU", units)}


def _screen_failure(tables: dict) -> dict:
    ds = tables["ds"]
    decod = ["SCREEN FAILURE" if (s, d) == ("S2", "ADVERSE EVENT") else d
             for s, d in zip(ds["USUBJID"].to_pylist(), ds["DSDECOD"].to_pylist(), strict=True)]
    return {**tables, "ds": _set(ds, "DSDECOD", decod)}


def _same_term_earlier_later_seq(tables: dict) -> dict:
    """S2: the event of sequence 3 becomes a headache dated before the one of sequence 2."""
    ae = tables["ae"]
    rows = ae.to_pylist()
    for row in rows:
        if (row["USUBJID"], row["AESEQ"]) == ("S2", 3):
            row.update(AEDECOD="HEADACHE", AETERM="Headache", AESTDTC="2024-04-20",
                       AEBODSYS="NERVOUS SYSTEM DISORDERS", AESOC="NERVOUS SYSTEM DISORDERS")
    return {**tables, "ae": pa.Table.from_pylist(rows, schema=ae.schema)}


@pytest.fixture(scope="module")
def build(standard, tmp_path_factory):
    catalog, house, base = standard
    built: dict[str, dict] = {}

    def run(name: str, change=None) -> dict:
        if name not in built:
            folder = tmp_path_factory.mktemp("tiny2")
            tables = tiny.tables()
            if change is not None:
                tables = change(tables)
            (folder / "sdtm").mkdir()
            for domain, table in tables.items():
                pq.write_table(table, folder / "sdtm" / f"{domain}.parquet")
            compiled = compile_decisions(
                catalog, house, base, relative_reference(house.directory, folder / "spec" / "adam"),
                sdtm_dir="../../sdtm", adam_dir="../../adam")
            compiled.write(folder / "spec")
            (folder / "adam").mkdir()
            rows = {}
            for dataset in compiled.datasets:
                spec = folder / "spec" / "adam" / f"{dataset.lower()}.yaml"
                assert checks.yamaa_run(spec) == []
                table = pq.read_table(folder / "adam" / f"{dataset.lower()}.parquet")
                rows[dataset] = {tuple(row[k] for k in KEYS[dataset]): row
                                 for row in table.to_pylist()}
            built[name] = rows
        return built[name]

    return run


def test_randomized_by_the_disposition_record_when_the_study_has_one(build):
    adsl = build("base")["ADSL"]
    assert {key[0]: row["RANDFL"] for key, row in adsl.items()} == {
        "S1": "Y", "S2": "N", "S3": "N", "S4": "N"}
    assert str(adsl[("S1",)]["RANDDT"]) == "2024-03-08"
    assert adsl[("S2",)]["RANDDT"] is None


def test_randomized_by_the_planned_arm_when_the_study_has_no_such_record(build):
    adsl = build("no-randomized", _without_randomized)["ADSL"]
    assert {key[0]: row["RANDFL"] for key, row in adsl.items()} == {
        "S1": "Y", "S2": "Y", "S3": "Y", "S4": "N"}
    assert adsl[("S1",)]["RANDDT"] is None


def test_param_has_the_unit_of_its_parameter(build):
    advs = build("units", _units)["ADVS"]
    params = {(key[1], row["PARAM"]) for key, row in advs.items()}
    assert params == {("SYSBP", "Systolic BP (mmHg)"), ("WEIGHT", "Weight (kg)"),
                      ("HEIGHT", "Height")}
    assert advs[("S1", "SYSBP", 4, "")]["AVALU"] is None
    assert advs[("S1", "SYSBP", 2, "")]["AVALU"] == "mmHg"


def test_a_screen_failure_has_no_end_of_study_status(build):
    adsl = build("screen-failure", _screen_failure)["ADSL"]
    assert adsl[("S2",)]["EOSSTT"] is None
    assert adsl[("S1",)]["EOSSTT"] == "COMPLETED"
    assert adsl[("S3",)]["EOSSTT"] == "ONGOING"


def test_aebodsys_is_carried_and_first_occurrence_is_by_date(build):
    adae = build("base")["ADAE"]
    assert adae[("S1", 1)]["AEBODSYS"] == "NERVOUS SYSTEM DISORDERS"
    changed = build("same-term", _same_term_earlier_later_seq)["ADAE"]
    assert changed[("S2", 3)]["TRTEMFL"] == "Y" and changed[("S2", 2)]["TRTEMFL"] == "Y"
    assert changed[("S2", 3)]["AOCCPFL"] == "Y"
    assert changed[("S2", 2)]["AOCCPFL"] is None
