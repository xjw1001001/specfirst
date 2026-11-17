"""The scorer on the pilot (ADR-005, decision 5): arm S, stage T, report only.

    P1-arm-s   the adverse event summary of the house standard alone, built on
               the reference ADaM of CDISCPILOT01, against the results CDISC's
               ARS example embeds; every difference in one of its states

The numbers are those of the report docs/reports/read-1a.md. They are held
here so that a change of the scorer that moves them is seen; they decide
nothing about the reader, and nothing is tuned on them (PLAN.md section
6.1).

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
    assert (score.correct, score.strict, score.lenient) == (10, 0, 0)
    states = {state: sum(1 for item in found.cells if item.state == state)
              for state in pilot.STATES}
    assert states == {"decision": 5, "open": 3, "no_row": 9, "unexplained": 0}
    # The five cells that differ are counts of zero, which the house default shows
    # without a percent and the example with one.
    fits = {(key[0], value["rule"]) for item in found.cells for key, value in item.by}
    assert fits == {("tfl.percent.format", "one_decimal_always")}
    assert all(item.cell.gold.startswith("0 (") and item.cell.candidate == "0"
               for item in found.cells if item.state == "decision")
    assert found.missing == [("ADAE", "RELGR1", ["ae.related.values"])]
    assert [f"{d}.{n}" for d, n, there in found.reads if there] == [
        "ADAE.AEACN", "ADAE.AESDTH", "ADAE.AESER", "ADAE.TRTEMFL", "ADAE.USUBJID",
        "ADSL.SAFFL", "ADSL.TRT01A", "ADSL.USUBJID"]
    assert found.not_built == ["RELATED"]
    assert len(found.no_row) == 3
    # The house default has a total column; the example has none.
    assert set(found.axes) == {"rows", "columns"}
    assert [(key[0], value) for key, value in found.axes["columns"]] == [
        ("tfl.columns.total", {"rule": "none"})]
    assert found.axes["rows"] == []
    text = "\n".join(pilot.lines(found))
    assert "Any adverse event | Placebo | 65 ( 75.6) | 65 ( 75.6) | equal" in text
    assert "UNEXPLAINED" not in text


CASES = {"P1-arm-s": arm_s}


@pytest.mark.parametrize("case", list(CASES), ids=list(CASES))
def test_score_pilot(case):
    try:
        CASES[case]()
    except pilot.PilotError as error:
        if os.environ.get("SPECFIRST_STRICT") == "1":
            raise
        pytest.skip(str(error))
