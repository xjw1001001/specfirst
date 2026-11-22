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
    assert states == {"decision": 0, "open": 6, "no_row": 6, "unexplained": 0}
    assert found.missing == [("ADAE", "RELGR1", ["ae.related.values"])]
    assert [f"{d}.{n}" for d, n, there in found.reads if there] == [
        "ADAE.AEACN", "ADAE.AESDTH", "ADAE.AESER", "ADAE.TRTEMFL", "ADAE.USUBJID",
        "ADSL.SAFFL", "ADSL.TRT01A", "ADSL.USUBJID"]
    # The rows of related and of serious related events read RELGR1; the related fatal
    # events and the dose modifications are no row of the standard rows (catalog@2).
    assert found.not_built == ["RELATED", "SERIOUS_RELATED"]
    assert len(found.no_row) == 2
    assert set(found.axes) == {"rows"} and found.axes["rows"] == []
    text = "\n".join(pilot.lines(found))
    assert "Any adverse event | Placebo | 65 ( 75.6) | 65 ( 75.6) | equal" in text
    assert "UNEXPLAINED" not in text


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
    assert states == {"decision": 5, "open": 6, "no_row": 6, "unexplained": 0}
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


def arm_r_no_output() -> None:
    """A reader that reads the SAP as planning no such table: nothing is built, and the
    trace sets tfl.output.include first, then explains each cell against that build."""
    records = [{"id": pilot.INCLUDE, "unit": pilot.UNIT, "value": {"rule": "not_included"}}]
    found = pilot.run(Machine(repo_root()), records, "R")
    score = found.score
    assert (score.produced, score.in_gold) == (0, 1)
    assert score.denominators() == {"shared_rows": 0, "produced": 0, "all": 27}
    assert (score.correct, score.strict, score.lenient) == (0, 0, 0)
    assert found.first == ((pilot.INCLUDE, pilot.UNIT), {"rule": "included"})
    alone = [item for item in found.cells if item.by == [found.first] and item.first is None]
    joint = [item for item in found.cells if item.state == "decision" and item.first]
    # Under open-default@2 the output decision alone gives the key's text in the 15
    # cells of the rows both tables have; no cell needs one more decision.
    assert len(found.cells) == 27 and len(alone) == 15 and joint == []
    states = {state: sum(1 for item in found.cells if item.state == state)
              for state in pilot.STATES}
    assert states == {"decision": 15, "open": 6, "no_row": 6, "unexplained": 0}
    assert set(found.axes) == {"rows"} and found.axes["rows"] == []
    text = "\n".join(pilot.lines(found))
    assert "arm R built no output" in text and "UNEXPLAINED" not in text
    assert ('Any adverse event | Placebo | 65 ( 75.6) | - | 65 ( 75.6) | missing; explained '
            'by tfl.output.include = {"rule": "included"}') in text
    assert "the key has 4 rows that arm R with tfl.output.include" in text


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
