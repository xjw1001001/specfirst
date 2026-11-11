"""The Python method implementations: what the vectors of tests/methods/ do not reach.

The vectors test the arithmetic. Here: input a method must refuse, the
limit of the Fisher enumeration, and that the enumeration is exact where
SciPy's fisher_exact is not (E27).
"""

from __future__ import annotations

import math

import pytest

from specfirst.machine import methods


def test_quantiles_are_found_in_whole_numbers():
    # n * p is a whole number exactly when n * 4 * p is divisible by 4: no tolerance decides.
    values = [float(v) for v in range(1, 13)]  # 12 values: every quantile is an average
    assert [methods.quantile(values, k, "sas5") for k in (1, 2, 3)] == [3.5, 6.5, 9.5]
    assert [methods.quantile(values, k, "r7") for k in (1, 2, 3)] == [3.75, 6.5, 9.25]
    assert methods.quantile([], 2, "sas5") is None
    with pytest.raises(methods.MethodError, match="only 1/4, 1/2 and 3/4"):
        methods.quantile(values, 4, "sas5")
    with pytest.raises(methods.MethodError, match="unknown quantile definition 'sas4'"):
        methods.quantile(values, 1, "sas4")
    with pytest.raises(methods.MethodError, match="unknown quantile definition"):
        methods.summary_continuous([], quantile_definition="type7")
    with pytest.raises(methods.MethodError, match="unknown sd denominator"):
        methods.summary_continuous([1, 2], sd_denominator="n")


def test_not_a_number_is_a_missing_value():
    assert methods.count_subjects(["a", float("nan"), None, ""]) == 1
    assert methods.summary_continuous([1.0, float("nan"), 3.0])["n"] == 2
    assert methods.anova_oneway_p([[1.0, float("nan"), 2.0], [4.0, 7.0]]) == pytest.approx(
        1 - math.sqrt(16 / 21), rel=1e-12)


@pytest.mark.parametrize("table", [[[1, 2], [3]], [[1, -2], [3, 4]], [[1.5, 2], [3, 4]],
                                   [[True, 2], [3, 4]]])
def test_a_table_holds_counts(table):
    for test in (methods.chisq_p, methods.fisher_exact_p):
        with pytest.raises(methods.MethodError, match="table"):
            test(table)


def test_an_empty_table_has_no_result():
    assert methods.chisq_p([]) is None and methods.fisher_exact_p([]) is None
    assert methods.fisher_exact_p([[0, 0], [0, 0]]) is None


def test_the_fisher_enumeration_refuses_what_it_cannot_sum(monkeypatch):
    table = [[3, 1, 2], [4, 0, 5], [1, 2, 6]]
    assert methods.fisher_exact_p(table) == pytest.approx(0.26717532030494745, rel=1e-12)
    monkeypatch.setattr(methods, "FISHER_MAX_TABLES", 50)
    with pytest.raises(methods.MethodError, match="more than 50 tables to sum"):
        methods.fisher_exact_p(table)


def test_the_enumeration_is_exact_and_repeatable_where_scipy_samples():
    """E27: scipy.stats.fisher_exact is exact for 2 x 2 tables only."""
    scipy_stats = pytest.importorskip("scipy.stats")
    table = [[2, 35, 3], [4, 30, 6], [1, 36, 3]]
    ours = [methods.fisher_exact_p(table) for _ in range(3)]
    assert ours[0] == ours[1] == ours[2] == pytest.approx(0.446449085857414, rel=1e-12)
    # The same table turned or reordered is the same test.
    turned = [list(column) for column in zip(*table, strict=True)]
    assert methods.fisher_exact_p(turned) == pytest.approx(ours[0], rel=1e-12)
    assert methods.fisher_exact_p(table[::-1]) == pytest.approx(ours[0], rel=1e-12)
    # For 2 x 2 the two agree.
    small = [[61, 25], [74, 10]]
    assert methods.fisher_exact_p(small) == pytest.approx(
        scipy_stats.fisher_exact(small).pvalue, rel=1e-10)


@pytest.mark.parametrize("decimals", [-1, 16, 1.0, True, None])
def test_the_count_of_decimals_must_be_0_to_15(decimals):
    with pytest.raises(methods.MethodError, match="decimals must be"):
        methods.round_half_away(1.5, decimals)


@pytest.mark.parametrize("value", [float("inf"), float("-inf"), float("nan"), "1.5", True])
def test_what_cannot_be_rounded_is_refused(value):
    with pytest.raises(methods.MethodError):
        methods.round_half_away(value, 1)


def test_rounding_is_on_the_decimal_not_on_the_double():
    # Python's own round goes by the double behind 2.675 and gives 2.67.
    assert round(2.675, 2) == 2.67
    assert methods.round_half_away(2.675, 2) == "2.68"
    assert methods.round_half_away(1e22, 0) == "10000000000000000000000"
    assert methods.round_half_away(-0.0, 2) == "0.00"
    assert methods.round_half_away(7, 0) == "7" and methods.round_half_away(-7, 2) == "-7.00"
