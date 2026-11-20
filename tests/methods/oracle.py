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


def _kron(a, b):
    """The Kronecker product of two matrices given as lists of rows."""
    return [[x * y for x in row_a for y in row_b] for row_a in a for row_b in b]


def _matmul(a, b):
    return [[sum((a[i][k] * b[k][j] for k in range(len(b))), Fraction(0))
             for j in range(len(b[0]))] for i in range(len(a))]


def _quadratic_form(w, g):
    """g' W- g and the rank of W, for a symmetric W with g in its range, exactly.

    The pivot columns of W (Gauss-Jordan in fractions) give a nonsingular
    block W_SS of the size of the rank; with g in the range of W, g' W- g is
    the same for every generalized inverse, so it is g_S' W_SS^-1 g_S.
    """
    size = len(w)
    work = [row[:] for row in w]
    pivots, row = [], 0
    for column in range(size):
        found = next((i for i in range(row, size) if work[i][column] != 0), None)
        if found is None:
            continue
        work[row], work[found] = work[found], work[row]
        for i in range(size):
            if i != row and work[i][column] != 0:
                factor = work[i][column] / work[row][column]
                work[i] = [x - factor * y for x, y in zip(work[i], work[row], strict=True)]
        pivots.append(column)
        row += 1
    rank = len(pivots)
    if rank == 0:
        return Fraction(0), 0
    block = [[w[i][j] for j in pivots] for i in pivots]
    right = [g[i] for i in pivots]
    # Solve block * x = right exactly.
    augmented = [block[i][:] + [right[i]] for i in range(rank)]
    for column in range(rank):
        found = next(i for i in range(column, rank) if augmented[i][column] != 0)
        augmented[column], augmented[found] = augmented[found], augmented[column]
        for i in range(rank):
            if i != column and augmented[i][column] != 0:
                factor = augmented[i][column] / augmented[column][column]
                augmented[i] = [x - factor * y
                                for x, y in zip(augmented[i], augmented[column], strict=True)]
    x = [augmented[i][rank] / augmented[i][i] for i in range(rank)]
    # g must be in the range of W: W[:, S] x = g.
    for i in range(size):
        if sum((w[i][j] * x[k] for k, j in enumerate(pivots)), Fraction(0)) != g[i]:
            raise NotCovered("test.cmh: G is not in the range of W")
    return sum((right[k] * x[k] for k in range(rank)), Fraction(0)), rank


def cmh_p(strata, values=None, statistic="general_association", scores="table"):
    """test.cmh in fractions: the statistic exactly, the tail by its finite series."""
    tables = [[[Fraction(count) for count in row] for row in table] for table in strata]
    if not tables:
        return None
    r_all, c_all = len(tables[0]), len(tables[0][0])
    rows = [i for i in range(r_all) if sum(sum(t[i]) for t in tables) > 0]
    columns = [j for j in range(c_all) if sum(t[i][j] for t in tables for i in range(r_all)) > 0]
    if len(rows) < 2 or len(columns) < 2:
        return None
    r, c = len(rows), len(columns)
    picked = [[Fraction(int(i == j)) for j in range(r)] for i in range(r - 1)]
    g_sum, w_sum, used = None, None, 0
    for table in tables:
        x = [[table[i][j] for j in columns] for i in rows]
        n = sum(sum(row) for row in x)
        if n < 2:
            continue
        used += 1
        p = [sum(row) / n for row in x]
        q = [sum(x[i][j] for i in range(r)) / n for j in range(c)]
        mean = [n * pi * qj for pi in p for qj in q]
        dp = [[(p[i] if i == j else 0) - p[i] * p[j] for j in range(r)] for i in range(r)]
        dq = [[(q[i] if i == j else 0) - q[i] * q[j] for j in range(c)] for i in range(c)]
        cov = [[n * n / (n - 1) * v for v in row] for row in _kron(dp, dq)]
        if statistic == "general_association":
            right = [[Fraction(int(i == j)) for j in range(c)] for i in range(c - 1)]
        else:
            if scores == "table":
                a = [Fraction(str(values[j])) for j in columns]
            else:
                totals = [sum(x[i][j] for i in range(r)) for j in range(c)]
                a = [sum(totals[:j], Fraction(0)) + (totals[j] + 1) / 2 for j in range(c)]
            right = [a]
        b = _kron(picked, right)
        flat = [x[i][j] for i in range(r) for j in range(c)]
        g = [sum((b[k][m] * (flat[m] - mean[m]) for m in range(len(flat))), Fraction(0))
             for k in range(len(b))]
        bt = [list(column) for column in zip(*b, strict=True)]
        w = _matmul(_matmul(b, cov), bt)
        g_sum = g if g_sum is None else [u + v for u, v in zip(g_sum, g, strict=True)]
        w_sum = w if w_sum is None else [[u + v for u, v in zip(ru, rv, strict=True)]
                                         for ru, rv in zip(w_sum, w, strict=True)]
    if not used:
        return None
    statistic_value, df = _quadratic_form(w_sum, g_sum)
    if df == 0:
        return None
    return chisq_sf(_float(statistic_value), df)


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
    if method == "test.cmh":
        return {"p_value": cmh_p(given["strata"], given.get("values"), **options)}
    if method.startswith("model.mmrm."):
        import oracle_mmrm

        return oracle_mmrm.expected(method, case)
    if method.startswith("model."):
        import oracle_models

        return oracle_models.expected(method, case)
    raise NotCovered(method)
