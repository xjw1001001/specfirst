"""The checks on what the evidence spikes print, with planted wrong outputs.

A check is trusted only after it fails on a planted defect (rule R5). The
good outputs below have the format the scripts in evidence/ print.
"""

from __future__ import annotations

import pytest
from evidence_cases import (
    CASES,
    PILOT_DATASETS,
    check_ars,
    check_e1,
    check_e24,
    check_e25,
    check_e26,
    check_e27,
)

from specfirst import gates

E1_ROW = "{:9s} rows={:6d} cols={:3d} cells={:8d} mismatched={:6d} type_diffs=0  \n"
E1_GOOD = "".join(
    E1_ROW.format(name.upper(), 254, 48, 12192, 0) for name in PILOT_DATASETS
) + "TOTAL cells=9119605 mismatched=0 match=100.0000%\n"

ARS_GOOD = (
    "quantile definition: sas5\n"
    "embedded results: 3735 {'match': 3711, 'differ': 23, 'not_computed': 1}\n"
    "   Mth01_CatVar_Count_ByGrp {'match': 1200}\n"
)
ARS_R7 = (
    "quantile definition: r7\n"
    "embedded results: 3735 {'match': 3662, 'differ': 72, 'not_computed': 1}\n"
)

E24_GOOD = "CSR Table 14-2.01: printed cells parsed=244 reproduced=244 (100.0%)\n"

E25_CSR = (
    "CSR Table 14-5.01: rows parsed=254 (1 overall, 23 organ classes, 230 preferred terms); "
    "rows with no ADAE match=0\n"
    "p-value display rule=csr: printed cells parsed=1175 reproduced=1175 (100.0%)\n"
    "TEAE terms in ADAE missing from the parsed CSR table: 0 []\n"
)
E25_SINGLE = "p-value display rule=single: printed cells parsed=1175 reproduced=1171 (99.7%)\n"

E26_GOOD = (
    "shift=footnote   baseline=reference    equal 38 of 51  p-values 0.405 and 0.386"
    "  (CSR prints 0.392 and 0.381)\n"
    "shift=worst_case baseline=reference    equal 45 of 51  p-values 0.405 and 0.386"
    "  (CSR prints 0.392 and 0.381)\n"
    "shift=worst_case baseline=last_predose equal 51 of 51  p-values 0.392 and 0.381"
    "  (CSR prints 0.392 and 0.381)\n"
)

E27_GOOD = (
    "14-6.02: rows 30, with a printed p-value 30\n"
    "14-6.03: rows 30, with a printed p-value 29\n"
    "3 x 3 reading (low, normal, high): equal 59 of 59\n"
    "3 x 2 reading (normal, abnormal):  equal 10 of 59\n"
)

SAS5 = check_ars("sas5", {"match": 3711, "differ": 23, "not_computed": 1})
R7 = check_ars("r7", {"match": 3662})


@pytest.mark.parametrize(
    "check, good",
    [
        (check_e1, E1_GOOD),
        (SAS5, ARS_GOOD),
        (R7, ARS_R7),
        (check_e24, E24_GOOD),
        (check_e25("csr", 1175), E25_CSR),
        (check_e25("single", 1171), E25_SINGLE),
        (check_e26, E26_GOOD),
        (check_e27, E27_GOOD),
    ],
)
def test_expected_output_passes(check, good):
    assert check(good) == []


@pytest.mark.parametrize(
    "check, bad",
    [
        # E1: one mismatched cell; another total; a dataset missing
        (check_e1, E1_GOOD.replace("mismatched=0 match=100.0000%", "mismatched=1 match=100.0000%")),
        (check_e1, E1_GOOD.replace("cells=9119605", "cells=9119604")),
        (check_e1, E1_GOOD.replace("mismatched=     0", "mismatched=     7", 1)),
        (check_e1, "".join(E1_GOOD.splitlines(keepends=True)[1:])),
        (check_e1, ""),
        # E2, E3: one result more or fewer in any class; the other quantile definition
        (SAS5, ARS_GOOD.replace("'match': 3711, 'differ': 23", "'match': 3710, 'differ': 24")),
        (SAS5, ARS_GOOD.replace("'differ': 23, 'not_computed': 1", "'differ': 24")),
        (SAS5, ARS_GOOD.replace("3735 {'match': 3711", "3734 {'match': 3710")),
        (SAS5, ARS_R7),
        (SAS5, "quantile definition: sas5\n"),
        # E4: must show the drop to 3,662
        (R7, ARS_GOOD.replace("sas5", "r7")),
        # E24: one cell short; a listed difference
        (check_e24, E24_GOOD.replace("reproduced=244 (100.0%)", "reproduced=243 (99.6%)")),
        (check_e24, E24_GOOD + "  differs: ('Sex', 'Male', 0, '33 (38%)', '34 (40%)')\n"),
        # E25: the two display rules must not be confused
        (check_e25("csr", 1175), E25_SINGLE),
        (check_e25("csr", 1175), E25_CSR.replace("=1175 (100.0%)", "=1171 (99.7%)")),
        (check_e25("single", 1171), E25_CSR),
        # E26: a count, a p-value, a missing or reordered variant
        (check_e26, E26_GOOD.replace("equal 51 of 51", "equal 50 of 51")),
        (check_e26, E26_GOOD.replace("p-values 0.392 and 0.381", "p-values 0.392 and 0.386")),
        (check_e26, "".join(E26_GOOD.splitlines(keepends=True)[:2])),
        (check_e26, "".join(reversed(E26_GOOD.splitlines(keepends=True)))),
        # E27: each reading has its own count
        (check_e27, E27_GOOD.replace("equal 59 of 59", "equal 58 of 59")),
        (check_e27, E27_GOOD.replace("equal 10 of 59", "equal 59 of 59")),
        (check_e27, ""),
    ],
)
def test_planted_wrong_output_fails(check, bad):
    assert check(bad) != []


def test_the_gate_requires_every_case():
    assert tuple(case.id for case in CASES) == gates.BASE0_EVIDENCE
