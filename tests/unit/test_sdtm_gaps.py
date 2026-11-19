"""Issues #25 and #24: SDTM that lacks a variable, or has it empty everywhere.

#25. An SDTM variable that the data lack and that SDTMIG v3.4 does not
require (AESEV is Permissible) must not stop a dataset. The compiler,
given the columns of the SDTM, leaves out of the ADaM dataset every column
that derives from it, with a warning. A table that reads such a column is
not produced, with the reason; a table that does not is built. A Required
variable that the data lack stops the compile with a message that says so.

#24. When no subject has a treatment start date, the build stops with a
message that says so and names the filter of the decision that removed
every exposure record, instead of at the first grouping of a table.

The study is HAND01 (`specfirst.score.hand`), without and with the
variable: yamaa and the Python result engine, no fetch cache and no R.
"""

from __future__ import annotations

import pyarrow as pa
import pytest

from specfirst.gen import sdtm as sdtmig
from specfirst.score import build, hand
from specfirst.score.candidate import Data, Machine

# The variables of AE that the parent spec of ADAE carries and SDTMIG v3.4 does not
# require, with the row of the adverse event summary that reads each (through
# RELGR1 for AEREL), or None.
CARRIED = {"AESOC": None, "AESEV": None, "AEOUT": None, "AESER": "SERIOUS",
           "AEREL": "RELATED", "AEACN": "DISCONTINUATION", "AESDTH": "FATAL"}
ALL_ROWS = ("ANY", "RELATED", "SERIOUS", "DISCONTINUATION", "FATAL")


@pytest.fixture(scope="module")
def machine(root):
    return Machine(root, datasets=("ADSL", "ADAE"))


@pytest.fixture(scope="module")
def gold(machine):
    return hand.gold_values(machine.catalog, machine.house)


def without(which: str, domain: str, variable: str) -> Data:
    sdtm = hand.tables(which)
    return Data(f"hand01/{which}/no-{variable}", sdtm={**sdtm, domain: sdtm[domain].drop(
        [variable])})


def emptied(which: str, domain: str, variable: str) -> Data:
    sdtm = hand.tables(which)
    table = sdtm[domain]
    index = table.column_names.index(variable)
    field = table.schema.field(variable)
    return Data(f"hand01/{which}/null-{variable}", sdtm={**sdtm, domain: table.set_column(
        index, variable, pa.nulls(table.num_rows, field.type))})


def with_rows(records: list[dict], rows: tuple[str, ...]) -> list[dict]:
    return [{**r, "value": {"rule": "stated_rows", "rows": list(rows)}}
            if r["id"] == "tfl.ae.summary.rows" else r for r in records]


def texts(made) -> dict:
    table = build.table_of(made.grids[hand.OUTPUT])
    return {(row[1], column[0]): cell["text"] for (row, column), cell in table.cells.items()}


# ---- #25 ---------------------------------------------------------------------------------


def test_the_repro_of_issue_25_builds_without_aesev(machine, gold):
    """Before: `ADaM: ADAE: the run failed ... NAME-3 ... columns.AESEV`, no grid."""
    made = machine.build(gold, without("visible", "ae", "AESEV"), hand.ARMS)
    assert made.ok, made.failure
    assert texts(made) == hand.expected_cells("visible")
    assert "AESEV" not in made.adam["ADAE"].column_names
    assert any("ADAE.AESEV" in line and "AE has no AESEV" in line and "Permissible" in line
               for line in made.warnings), made.warnings


@pytest.mark.parametrize("variable", sorted(CARRIED))
def test_a_carried_variable_that_is_not_required(machine, gold, variable):
    assert sdtmig.DOMAINS["AE"].variable(variable).core != "Req"
    data = without("twin", "ae", variable)
    row = CARRIED[variable]
    # The rows that do not read it are built, with the text of gold on full data.
    rest = tuple(code for code in ALL_ROWS if code != row)
    made = machine.build(with_rows(gold, rest), data, hand.ARMS)
    full = machine.build(with_rows(gold, rest), hand.data("twin"), hand.ARMS)
    assert made.ok and full.ok, made.failure
    assert texts(made) == texts(full)
    assert variable not in made.adam["ADAE"].column_names
    assert any(f"AE has no {variable}" in line for line in made.warnings)
    made = machine.build(gold, data, hand.ARMS)
    if row is None:
        assert made.ok and texts(made) == hand.expected_cells("twin")
    else:
        # The table reads it: not produced, and the reason names the variable.
        assert made.ok and made.grids == {}, made.failure
        why = made.not_produced[hand.OUTPUT]
        assert f"AE has no {variable}" in why and "ADAE." in why


def test_what_derives_from_a_missing_variable_leaves_too(machine, gold):
    """AESOC: the first occurrence of an organ class derives from it."""
    made = machine.build(gold, without("visible", "ae", "AESOC"), hand.ARMS)
    assert made.ok, made.failure
    names = set(made.adam["ADAE"].column_names)
    assert not names & {"AESOC", "AOCCSFL"} and {"AOCCFL", "AOCCPFL", "TRTEMFL"} <= names
    assert any("ADAE.AOCCSFL" in line and "AESOC" in line for line in made.warnings)


@pytest.mark.parametrize("variable", ["AEDECOD", "AETERM"])
def test_a_required_variable_stops_the_build_with_a_message(machine, gold, variable):
    assert sdtmig.DOMAINS["AE"].variable(variable).core == "Req"
    made = machine.build(gold, without("visible", "ae", variable), hand.ARMS)
    assert not made.ok
    assert f"AE has no {variable}" in made.failure and "Required" in made.failure


def test_a_variable_the_records_of_a_dataset_rest_on_leaves_that_dataset_out(root):
    """The full house builds ADVS too. Every column of ADVS rests on its row templates,
    and they read VS.VSSTRESN (Expected): without it ADVS is left out with a warning,
    and the adverse event summary, which reads no ADVS, is built as gold (review of
    std-issues, finding 2; before, the compile stopped: `ADVS: its key ... cannot be
    built`)."""
    machine = Machine(root)
    gold = hand.gold_values(machine.catalog, machine.house)
    assert "ADVS" in machine.compile(gold).datasets
    made = machine.build(gold, without("visible", "vs", "VSSTRESN"), hand.ARMS)
    assert made.ok, made.failure
    assert "ADVS" not in made.adam
    assert texts(made) == hand.expected_cells("visible")
    assert any(line.startswith("ADVS is left out") and "VS has no VSSTRESN" in line
               for line in made.warnings), made.warnings


def test_the_compile_without_the_data_is_unchanged(machine, gold):
    """The generator and `specfirst compile` give no columns of SDTM: nothing is left
    out, and the files are those of before."""
    plain = machine.compile(gold)
    full = machine.compile(gold, sdtm={stem: set(t.column_names)
                                       for stem, t in hand.tables("visible").items()})
    assert not isinstance(plain, str) and not isinstance(full, str)
    assert plain.files == full.files and full.warnings == [] and full.left_out == {}


# ---- #24 ---------------------------------------------------------------------------------


@pytest.mark.parametrize("which", ["visible", "twin"])
def test_no_treatment_start_date_names_the_filter_that_removed_every_record(machine, gold,
                                                                            which):
    """EXDOSE is not Required in SDTMIG; empty everywhere, the house filter of a dosed
    record removes every exposure record. Before: `results: grouping 'Grp_TRT01A': no
    record of ADSL in the analysis set has a value`."""
    made = machine.build(gold, emptied(which, "ex", "EXDOSE"), hand.ARMS)
    assert not made.ok
    count = len(hand.SUBJECTS[which])
    assert made.failure.startswith(
        f"ADaM: ADSL: no subject has a treatment start date (TRTSDT is missing in all "
        f"{count} records)"), made.failure
    assert "trt.start.source (first_ex_with_dose)" in made.failure
    assert "EX.EXDOSE > 0 OR (EX.EXDOSE = 0 AND EX.EXTRT LIKE '%PLACEBO%')" in made.failure
    assert "EXDOSE is missing in every record of EX" in made.failure
    assert "grouping" not in made.failure


def test_the_start_from_any_exposure_record_still_builds(machine, gold):
    """With trt.start.source = first_ex_record the start dates come back and the build
    goes on (the end date is #24's other half: a new alternative, catalog@2)."""
    records = [{**r, "value": {"rule": "first_ex_record"}} if r["id"] == "trt.start.source"
               else r for r in gold]
    made = machine.build(records, emptied("visible", "ex", "EXDOSE"), hand.ARMS)
    assert made.ok, made.failure
    adsl = made.adam["ADSL"]
    assert sum(value is not None for value in adsl.column("TRTSDT").to_pylist()) == 6


def test_a_study_with_start_dates_is_not_stopped(machine, gold):
    made = machine.build(gold, hand.data("visible"), hand.ARMS)
    assert made.ok and made.warnings == []
