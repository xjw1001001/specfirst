"""The scorer on the pilot (ADR-005, decision 5): arms S and R, stage T, report only.

    P1-arm-s   the adverse event summary of the house standard alone, built on
               the reference ADaM of CDISCPILOT01, against the results CDISC's
               ARS example embeds; every difference in one of its states
    P2-arm-r   the same with two table decisions as a reader may write them
    P3-pilot-folder  the folder of the pilot task (specfirst.harness.pilot)
    P4-arm-r-no-output  a reader that leaves the output out: the trace goes
               through tfl.output.include first

The numbers are those of the report docs/reports/read-1a.md, moved to the
default pair of catalog-2c (`catalog@2`, `open-default@2`; its report says
how). They are held here so that a change of the scorer that moves them is
seen; they decide nothing about the reader, and nothing is tuned on them
(PLAN.md section 6.1).

The test needs `specfirst fetch` and carries the marker `evidence`: `make
test` leaves it out and `specfirst gate read-1a` runs it. A missing cache
skips it, except under SPECFIRST_STRICT=1 (set by the gate), where it
fails: a gate never passes by skipping.
"""

from __future__ import annotations

import os

import pytest

from specfirst.paths import repo_root
from specfirst.score import pilot
from specfirst.score.candidate import Machine

pytestmark = pytest.mark.evidence


def arm_s() -> None:
    found = pilot.run(Machine(repo_root()))
    score = found.score
    # The key: the header row and the eight analyses of the example, three arms.
    assert (score.produced, score.in_gold) == (1, 1)
    assert score.denominators() == {"shared_rows": 15, "produced": 27, "all": 27}
    # open-default@2 shows a count of zero with its percent and has no total column, as
    # the example: every cell of the rows both tables have is the key's.
    assert (score.correct, score.strict, score.lenient) == (15, 0, 0)
    states = {state: sum(1 for item in found.cells if item.state == state)
              for state in pilot.STATES}
    assert states == {"decision": 3, "open": 9, "no_row": 0, "unexplained": 0}
    # The three cells of the dose modifications, a row the standard rows leave out, are
    # explained by the key's list of rows (catalog@2 has a row for every analysis, #13).
    fits = {(key[0], value["rule"]) for item in found.cells for key, value in item.by}
    assert fits == {("tfl.ae.summary.rows", "stated_rows")}
    assert {item.cell.row[1] for item in found.cells if item.state == "decision"} == {
        "Adverse event leading to dose modification"}
    assert found.missing == [("ADAE", "RELGR1", ["ae.related.values"])]
    assert [f"{d}.{n}" for d, n, there in found.reads if there] == [
        "ADAE.AEACN", "ADAE.AESDTH", "ADAE.AESER", "ADAE.TRTEMFL", "ADAE.USUBJID",
        "ADSL.SAFFL", "ADSL.TRT01A", "ADSL.USUBJID"]
    # The rows of related, serious related and related fatal events read RELGR1: open (the
    # first two are standard rows, the third a row of the key's list).
    assert found.not_built == ["RELATED", "SERIOUS_RELATED", "FATAL_RELATED"]
    assert {item.cell.row[1] for item in found.cells if item.state == "open"} == {
        "Related adverse event", "Serious related adverse event", "Fatal related adverse event"}
    assert found.no_row == []
    assert set(found.axes) == {"rows"} and found.axes["rows"] == []
    text = "\n".join(pilot.lines(found))
    assert "Any adverse event | Placebo | 65 ( 75.6) | 65 ( 75.6) | equal" in text
    assert "UNEXPLAINED" not in text
    # Review of catalog-2c, G1: the summary counts the explained cells of the dose
    # modifications among the rows arm S does not build, not among the rows it shares.
    assert ("cells of the key that differ or are missing: 12. Of the 15 cells of the rows "
            "both tables have, 0 differ and are explained by another value of one table "
            "decision, and 0 are unexplained. 12 are in rows that arm S does not build: 3 "
            "explained by another value of one table decision, 9 for a variable the reference "
            "ADaM lacks, 0 in rows the catalog does not have, 0 in rows the table decisions "
            "do not ask for that no one table decision gives;") in text
    assert "rows not built: RELATED, SERIOUS_RELATED, FATAL_RELATED" in text


def arm_r() -> None:
    """Arm R with two table decisions read otherwise than the house (those of
    open-default@1): the five counts of zero then lose the key's percent, explained by
    tfl.percent.format, and the total column is one the key lacks."""
    records = [{"id": "tfl.percent.format", "unit": pilot.UNIT,
                "value": {"rule": "one_decimal_zero_blank", "decimals": 1}},
               {"id": "tfl.columns.total", "unit": pilot.UNIT, "value": {"rule": "all_arms"}}]
    found = pilot.run(Machine(repo_root()), records, "R")
    score = found.score
    assert score.denominators() == {"shared_rows": 15, "produced": 27, "all": 27}
    assert (score.correct, score.strict, score.lenient) == (10, 0, 0)
    states = {state: sum(1 for item in found.cells if item.state == state)
              for state in pilot.STATES}
    # The dose modifications need the key's rows and the percent format: two decisions.
    assert states == {"decision": 5, "open": 9, "no_row": 3, "unexplained": 0}
    fits = {(key[0], value["rule"]) for item in found.cells for key, value in item.by}
    assert fits == {("tfl.percent.format", "one_decimal_always")}
    assert all(item.cell.gold.startswith("0 (") and item.cell.candidate == "0"
               for item in found.cells if item.state == "decision")
    assert set(found.axes) == {"rows", "columns"} and found.axes["rows"] == []
    assert [(key[0], value) for key, value in found.axes["columns"]] == [
        ("tfl.columns.total", {"rule": "none"})]
    text = "\n".join(pilot.lines(found))
    assert "arm R (a reader's table decisions" in text
    assert 'tfl.columns.total = {"rule": "all_arms"}' in text.split("\n")[2]
    assert ("Fatal adverse event | Xanomeline High Dose | 0 (  0.0) | 0 | differs; explained "
            "by tfl.percent.format") in text
    # The dose modifications are a row of catalog@2 the decisions do not ask for, not a gap
    # of the catalog (G1).
    assert ("Of the 15 cells of the rows both tables have, 5 differ and are explained by "
            "another value of one table decision, and 0 are unexplained. 12 are in rows that "
            "arm R does not build: 0 explained by another value of one table decision, 9 for "
            "a variable the reference ADaM lacks, 0 in rows the catalog does not have, 3 in "
            "rows the table decisions do not ask for that no one table decision gives;") in text


def arm_r_no_output() -> None:
    """A reader that reads the SAP as planning no such table, and the count of zero
    without its percent: nothing is built, and the trace sets tfl.output.include first,
    then explains each cell against that build, one more decision where it needs one."""
    records = [{"id": pilot.INCLUDE, "unit": pilot.UNIT, "value": {"rule": "not_included"}},
               {"id": "tfl.percent.format", "unit": pilot.UNIT,
                "value": {"rule": "one_decimal_zero_blank", "decimals": 1}}]
    found = pilot.run(Machine(repo_root()), records, "R")
    score = found.score
    assert (score.produced, score.in_gold) == (0, 1)
    assert score.denominators() == {"shared_rows": 0, "produced": 0, "all": 27}
    assert (score.correct, score.strict, score.lenient) == (0, 0, 0)
    assert found.first == ((pilot.INCLUDE, pilot.UNIT), {"rule": "included"})
    alone = [item for item in found.cells if item.by == [found.first] and item.first is None]
    joint = [item for item in found.cells if item.state == "decision" and item.first]
    # The five counts of zero need the percent format as well.
    assert len(found.cells) == 27 and len(alone) == 10 and len(joint) == 5
    assert {(key[0], value["rule"]) for item in joint for key, value in item.by} == {
        ("tfl.percent.format", "one_decimal_always")}
    states = {state: sum(1 for item in found.cells if item.state == state)
              for state in pilot.STATES}
    assert states == {"decision": 15, "open": 9, "no_row": 3, "unexplained": 0}
    assert set(found.axes) == {"rows"} and found.axes["rows"] == []
    text = "\n".join(pilot.lines(found))
    assert "arm R built no output" in text and "UNEXPLAINED" not in text
    assert ('Any adverse event | Placebo | 65 ( 75.6) | - | 65 ( 75.6) | missing; explained '
            'by tfl.output.include = {"rule": "included"}') in text
    assert "the key has 4 rows that arm R with tfl.output.include" in text
    assert ("10 have the key's text, 5 differ and are explained by one more table decision, "
            "and 0 are unexplained. 12 are in rows that this build does not have: 0 explained "
            "by one more table decision, 9 for a variable the reference ADaM lacks, 0 in rows "
            "the catalog does not have, 3 in rows the table decisions do not ask for that no "
            "one table decision gives;") in text


def pilot_folder() -> None:
    """The folder of the pilot task, written from the cache outside every checkout: the SAP
    as anchored ASCII text, the reference ADaM, the key outside inputs/."""
    import tempfile
    from pathlib import Path

    import yaml

    from specfirst.harness import pilot as task_pilot
    from specfirst.harness import task as tasks
    from specfirst.machine.canonical import sha256_file

    root = repo_root()
    with tempfile.TemporaryDirectory() as scratch:
        folder = task_pilot.write(root, Path(scratch) / "pilot")
        manifest = yaml.safe_load((folder / "kit.yaml").read_text(encoding="ascii"))
        assert (manifest["tier"], manifest["split"]) == ("C", "pilot")
        assert all(sha256_file(folder / path) == sha for path, sha in manifest["files"].items())
        assert task_pilot.KEY in manifest["files"] and task_pilot.EXAMPLE in manifest["files"]
        sap = (folder / tasks.DOCUMENTS["sap"]).read_text(encoding="ascii")
        # 51 pages; pdftotext ends the last with a form feed too, which starts no page.
        assert sap.startswith("[1/p1] ") and "[51/p" in sap and "[52/p" not in sap
        made = tasks.build(root, folder, Path(scratch) / "tasks", "T")
        assert tasks.problems(made.folder, folder) == []
        assert not (made.folder / tasks.DOCUMENTS["protocol"]).exists()


CASES = {"P1-arm-s": arm_s, "P2-arm-r": arm_r, "P3-pilot-folder": pilot_folder,
         "P4-arm-r-no-output": arm_r_no_output}


@pytest.mark.parametrize("case", list(CASES), ids=list(CASES))
def test_score_pilot(case):
    try:
        CASES[case]()
    except pilot.PilotError as error:
        if os.environ.get("SPECFIRST_STRICT") == "1":
            raise
        pytest.skip(str(error))
