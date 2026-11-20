"""A second computation of the method vectors, in exact arithmetic where it exists.

The vectors in this folder are what both engines must reproduce, so their
expected values must not come from the engines. This module computes them
another way: fractions for sums, squares, quantiles and table
probabilities; closed forms for the tail probabilities that have one. The
test `test_the_vectors_are_what_exact_arithmetic_gives` compares the files
with it. Where no closed form exists the function returns NotCovered, and
the vector says where its expected value was taken from.

Nothing here is used by an engine.
"""

from __future__ import annotations

import itertools
import math
from decimal import Decimal, localcontext
from fractions import Fraction


class NotCovered(Exception):
    """This module has no independent way to compute the case."""


def _present(values):
    return [Fraction(str(value)) for value in values if value is not None and value != ""]


def _float(value: Fraction) -> float:
    return value.numerator / value.denominator  # correctly rounded by Python


def _sqrt(value: Fraction) -> float:
    with localcontext() as context:
        context.prec = 60
        return float((Decimal(value.numerator) / Decimal(value.denominator)).sqrt())


def summary_continuous(values, quantile_definition="sas5", sd_denominator="n_minus_1") -> dict:
    x = sorted(_present(values))
    n = len(x)
    empty = {"n": n, "mean": None, "sd": None, "median": None, "q1": None, "q3": None,
             "min": None, "max": None}
    if n == 0:
        return empty
    mean = sum(x) / n
    result = dict(empty, mean=_float(mean), min=_float(x[0]), max=_float(x[-1]))
    if n > 1:
        result["sd"] = _sqrt(sum((value - mean) ** 2 for value in x) / (n - 1))
    for name, p in (("q1", Fraction(1, 4)), ("median", Fraction(1, 2)), ("q3", Fraction(3, 4))):
        if quantile_definition == "sas5":
            position = n * p
            j = math.floor(position)
            value = x[j] if position != j else (x[j - 1] + x[j]) / 2
        else:
            position = (n - 1) * p
            j = math.floor(position)
            value = x[j] if position == j else x[j] + (position - j) * (x[j + 1] - x[j])
        result[name] = _float(value)
    return result


def _reduced(table):
    rows = [row for row in table if sum(row) > 0]
    keep = [j for j in range(len(table[0])) if sum(row[j] for row in table) > 0] if table else []
    return [[row[j] for j in keep] for row in rows]


def chisq_sf(statistic: float, df: int) -> float:
    """The upper tail of the chi-square distribution, by its finite series."""
    half = statistic / 2
    if df % 2 == 0:
        return math.exp(-half) * math.fsum(half ** k / math.factorial(k) for k in range(df // 2))
    series = math.fsum(half ** (k - 0.5) / math.gamma(k + 0.5) for k in range(1, df // 2 + 1))
    return math.erfc(math.sqrt(half)) + math.exp(-half) * series


def chisq_p(table) -> float | None:
    rows = _reduced(table)
    if len(rows) < 2 or len(rows[0]) < 2:
        return None
    row_totals = [sum(row) for row in rows]
    column_totals = [sum(row[j] for row in rows) for j in range(len(rows[0]))]
    total = sum(row_totals)
    statistic = sum(
        (Fraction(rows[i][j]) - Fraction(row_totals[i] * column_totals[j], total)) ** 2
        / Fraction(row_totals[i] * column_totals[j], total)
        for i in range(len(rows)) for j in range(len(rows[0])))
    return chisq_sf(_float(statistic), (len(rows) - 1) * (len(rows[0]) - 1))


def anova_oneway_p(groups) -> float | None:
    samples = [_present(group) for group in groups]
    samples = [sample for sample in samples if sample]
    k, n = len(samples), sum(len(sample) for sample in samples)
    if k < 2 or n - k < 1:
        return None
    grand = sum(value for sample in samples for value in sample) / n
    means = [sum(sample) / len(sample) for sample in samples]
    pairs = list(zip(samples, means, strict=True))
    between = sum(len(sample) * (mean - grand) ** 2 for sample, mean in pairs)
    within = sum((value - mean) ** 2 for sample, mean in pairs for value in sample)
    if within == 0:
        return 0.0 if between > 0 else None
    f = _float((between / (k - 1)) / (within / (n - k)))
    df1, df2 = k - 1, n - k
    if df1 == 2:  # the F tail has a closed form when one of its degrees of freedom is 2
        return (1 + df1 * f / df2) ** (-df2 / 2)
    if df2 == 2:
        return 1 - (df1 * f / (df1 * f + df2)) ** (df1 / 2)
    raise NotCovered(f"F tail with {df1} and {df2} degrees of freedom")


def _tables(row_totals, column_totals):
    """Every table of whole numbers with these margins, by brute force."""
    if len(row_totals) == 1:
        yield [list(column_totals)]
        return
    first = row_totals[0]
    for row in itertools.product(*(range(min(first, c) + 1) for c in column_totals)):
        if sum(row) == first:
            left = [c - x for c, x in zip(column_totals, row, strict=True)]
            for rest in _tables(row_totals[1:], left):
                yield [list(row), *rest]


def _fisher_probabilities(rows) -> tuple[Fraction, list[Fraction]]:
    """The probability of a table, and of every table with its margins, as fractions."""
    row_totals = [sum(row) for row in rows]
    column_totals = [sum(row[j] for row in rows) for j in range(len(rows[0]))]
    numerator = math.prod(math.factorial(v) for v in row_totals + column_totals)
    scale = math.factorial(sum(row_totals))

    def probability(candidate) -> Fraction:
        return Fraction(numerator,
                        scale * math.prod(math.factorial(v) for row in candidate for v in row))

    return probability(rows), [probability(candidate)
                               for candidate in _tables(row_totals, column_totals)]


def fisher_exact_p(table) -> float | None:
    rows = _reduced(table)
    if len(rows) < 2 or len(rows[0]) < 2:
        return None
    observed, every = _fisher_probabilities(rows)
    # Exact: equal probabilities are equal fractions.
    return _float(sum((p for p in every if p <= observed), Fraction(0)))


def fisher_just_above(table, low: Fraction, high: Fraction) -> list[float]:
    """The tables that are a little more probable than the observed one.

    Returns the relative excess of every table with the margins of `table`
    whose probability is above that of `table` by more than `low` and at
    most `high`, in exact fractions. Such a table does not count by
    statement 5 of test.fisher.exact when `low` is 1e-7; a looser
    implementation counts it.
    """
    rows = _reduced(table)
    if len(rows) < 2 or len(rows[0]) < 2:
        return []
    observed, every = _fisher_probabilities(rows)
    return sorted(_float(p / observed - 1) for p in every
                  if observed * (1 + low) < p <= observed * (1 + high))


def expected(method: str, case: dict) -> dict:
    """What a vector's case should give, by this module."""
    given, options = case["input"], case.get("options") or {}
    if method == "count.subjects":
        return {"n": len({str(v) if isinstance(v, str) else float(v)
                          for v in given["values"] if v is not None and v != ""})}
    if method == "percent.subjects":
        top, bottom = given["numerator"], given["denominator"]
        if top is None or bottom is None or bottom == 0:
            return {"pct": None}
        return {"pct": _float(Fraction(100 * top, 1) / Fraction(str(bottom)))}
    if method == "summary.continuous":
        return summary_continuous(given["values"], **options)
    if method == "test.chisq":
        return {"p_value": chisq_p(given["table"])}
    if method == "test.anova.oneway":
        return {"p_value": anova_oneway_p(given["groups"])}
    if method == "test.fisher.exact":
        return {"p_value": fisher_exact_p(given["table"])}
    if method.startswith("model."):
        import oracle_models

        return oracle_models.expected(method, case)
    raise NotCovered(method)
