"""The Python implementations of the method registry (PLAN.md section 7.3).

One function per registry entry. Each follows the numbered semantics of its
entry in standard/methods/ and is tested on the vectors in tests/methods/,
which the R implementations in r/specfirstr/ must reproduce as well (rule
R11). A missing result is None.

The Fisher exact test sums over every table with the observed margins, for
any number of rows and columns. scipy.stats.fisher_exact is exact for 2 x 2
tables only and samples for larger ones (E27), so it is not used.
"""

from __future__ import annotations

import math
import re
from collections.abc import Iterable, Sequence
from decimal import ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal, localcontext

QUANTILE_DEFINITIONS = ("sas5", "r7")
# test.fisher.exact, statement 5: the relative excess that still counts as "not larger".
FISHER_RELATIVE_EXCESS = 1e-7
# test.fisher.exact, statement 6: more tables than this are refused, not approximated.
FISHER_MAX_TABLES = 10_000_000


class MethodError(ValueError):
    """A method was given input it does not accept."""


def _missing(value: object) -> bool:
    return value is None or value == "" or (isinstance(value, float) and math.isnan(value))


# ---- count.subjects, percent.subjects -------------------------------------------


def count_subjects(values: Iterable[object]) -> int:
    """count.subjects: the number of distinct values that are not missing."""
    return len({value for value in values if not _missing(value)})


def percent(numerator: float | None, denominator: float | None) -> float | None:
    """percent.subjects: 100 * numerator / denominator; missing when it does not exist."""
    if numerator is None or denominator is None or denominator == 0:
        return None
    return 100.0 * numerator / denominator


# ---- summary.continuous ---------------------------------------------------------


def quantile(ordered: Sequence[float], quarters: int, definition: str) -> float | None:
    """The quantile at p = quarters / 4 of values sorted upwards.

    The position is computed in whole numbers, so that no rounding decides
    between two values (summary.continuous, statements 7 and 8).
    """
    n = len(ordered)
    if n == 0:
        return None
    if quarters not in (1, 2, 3):
        raise MethodError(f"quantile at {quarters}/4: only 1/4, 1/2 and 3/4 are defined")
    if definition == "sas5":
        j, rest = divmod(n * quarters, 4)  # n * p = j + rest / 4
        if rest:
            return float(ordered[j])  # x[j + 1], counted from 1
        return (ordered[j - 1] + ordered[j]) / 2.0
    if definition == "r7":
        j, rest = divmod((n - 1) * quarters, 4)  # (n - 1) * p = j + rest / 4
        if not rest:
            return float(ordered[j])
        return ordered[j] + (rest / 4.0) * (ordered[j + 1] - ordered[j])
    raise MethodError(f"unknown quantile definition '{definition}'")


def summary_continuous(values: Iterable[float | None], quantile_definition: str = "sas5",
                       sd_denominator: str = "n_minus_1") -> dict[str, float | int | None]:
    """summary.continuous: n, mean, sd, median, q1, q3, min and max of the non-missing values."""
    if sd_denominator != "n_minus_1":
        raise MethodError(f"unknown sd denominator '{sd_denominator}'")
    ordered = sorted(float(value) for value in values if not _missing(value))
    n = len(ordered)
    result: dict[str, float | int | None] = {
        "n": n, "mean": None, "sd": None, "median": None, "q1": None, "q3": None,
        "min": None, "max": None,
    }
    if n == 0:
        if quantile_definition not in QUANTILE_DEFINITIONS:
            raise MethodError(f"unknown quantile definition '{quantile_definition}'")
        return result
    mean = math.fsum(ordered) / n
    result["mean"] = mean
    if n > 1:
        if ordered[0] == ordered[-1]:
            # Statement 10: equal values have no spread, whatever the rounding of the mean.
            result["sd"] = 0.0
        else:
            result["sd"] = math.sqrt(
                math.fsum((value - mean) ** 2 for value in ordered) / (n - 1))
    result["median"] = quantile(ordered, 2, quantile_definition)
    result["q1"] = quantile(ordered, 1, quantile_definition)
    result["q3"] = quantile(ordered, 3, quantile_definition)
    result["min"], result["max"] = ordered[0], ordered[-1]
    return result


# ---- tables ---------------------------------------------------------------------


def _reduced(table: Sequence[Sequence[int]]) -> list[list[int]]:
    """The table as whole numbers, without the rows and columns whose total is 0."""
    rows = [list(row) for row in table]
    width = len(rows[0]) if rows else 0
    for row in rows:
        if len(row) != width:
            raise MethodError("the rows of a table must have the same length")
        for count in row:
            if isinstance(count, bool) or count != int(count) or count < 0:
                raise MethodError(f"a table holds counts, not {count!r}")
    rows = [[int(count) for count in row] for row in rows]
    keep = [j for j in range(width) if any(row[j] for row in rows)]
    return [[row[j] for j in keep] for row in rows if any(row)]


def chisq_p(table: Sequence[Sequence[int]]) -> float | None:
    """test.chisq: the p-value of Pearson's chi-square test, without continuity correction."""
    from scipy.special import chdtrc

    rows = _reduced(table)
    if len(rows) < 2 or len(rows[0]) < 2:
        return None
    row_totals = [sum(row) for row in rows]
    column_totals = [sum(column) for column in zip(*rows, strict=True)]
    total = sum(row_totals)
    statistic = math.fsum(
        (count - row_total * column_total / total) ** 2 / (row_total * column_total / total)
        for row, row_total in zip(rows, row_totals, strict=True)
        for count, column_total in zip(row, column_totals, strict=True)
    )
    return float(chdtrc((len(rows) - 1) * (len(rows[0]) - 1), statistic))


def anova_oneway_p(groups: Iterable[Iterable[float | None]]) -> float | None:
    """test.anova.oneway: the p-value of the F test of equal means, with equal variances."""
    from scipy.special import fdtrc

    samples = [[float(value) for value in group if not _missing(value)] for group in groups]
    samples = [sample for sample in samples if sample]
    k, n = len(samples), sum(len(sample) for sample in samples)
    if k < 2 or n - k < 1:
        return None
    if all(min(sample) == max(sample) for sample in samples):  # statement 5: SSW is 0
        return 0.0 if len({sample[0] for sample in samples}) > 1 else None
    grand = math.fsum(value for sample in samples for value in sample) / n
    means = [math.fsum(sample) / len(sample) for sample in samples]
    between = math.fsum(len(sample) * (mean - grand) ** 2
                        for sample, mean in zip(samples, means, strict=True))
    within = math.fsum((value - mean) ** 2
                       for sample, mean in zip(samples, means, strict=True) for value in sample)
    statistic = (between / (k - 1)) / (within / (n - k))
    return float(fdtrc(k - 1, n - k, statistic))


def fisher_exact_p(table: Sequence[Sequence[int]]) -> float | None:
    """test.fisher.exact: the two-sided p-value, by summing over every table.

    The tables with the observed margins are walked row by row. A row is
    filled cell by cell; its last cell and the whole last row are what is
    left. The largest row and the largest column are put last, so that the
    cells that are walked are bounded by the smaller totals.
    """
    rows = _reduced(table)
    if len(rows) < 2 or len(rows[0]) < 2:
        return None
    rows.sort(key=sum)
    order = sorted(range(len(rows[0])), key=lambda j: sum(row[j] for row in rows))
    rows = [[row[j] for j in order] for row in rows]
    row_totals = [sum(row) for row in rows]
    column_totals = [sum(column) for column in zip(*rows, strict=True)]
    total = sum(row_totals)
    log_factorial = [0.0] * (total + 1)
    for value in range(2, total + 1):
        log_factorial[value] = log_factorial[value - 1] + math.log(value)
    constant = (sum(log_factorial[value] for value in row_totals + column_totals)
                - log_factorial[total])
    observed = constant - sum(log_factorial[count] for row in rows for count in row)
    limit = observed + math.log1p(FISHER_RELATIVE_EXCESS)
    last_row, last_column = len(rows) - 1, len(column_totals) - 1
    terms: list[float] = []
    tables = 0

    def fill(i: int, j: int, left_in_row: int, left: list[int], cells: float) -> None:
        """Walk the cells from row i, column j. `cells` is the sum of log(count!) so far."""
        nonlocal tables
        if i == last_row:  # the last row is what the columns have left
            tables += 1
            if tables > FISHER_MAX_TABLES:
                raise MethodError(
                    f"test.fisher.exact: more than {FISHER_MAX_TABLES} tables to sum; "
                    "the method does not approximate")
            log_probability = constant - cells - sum(log_factorial[count] for count in left)
            if log_probability <= limit:
                terms.append(math.exp(log_probability))
            return
        if j == last_column:  # the last cell of a row is what the row has left
            if left_in_row <= left[j]:
                left[j] -= left_in_row
                fill(i + 1, 0, row_totals[i + 1], left, cells + log_factorial[left_in_row])
                left[j] += left_in_row
            return
        # What the later columns can still take bounds this cell from below.
        lowest = max(0, left_in_row - sum(left[j + 1:]))
        for count in range(lowest, min(left_in_row, left[j]) + 1):
            left[j] -= count
            fill(i, j + 1, left_in_row - count, left, cells + log_factorial[count])
            left[j] += count

    fill(0, 0, row_totals[0], list(column_totals), 0.0)
    return min(1.0, math.fsum(terms))


# ---- display.round.half_away_from_zero, display.round.half_even ------------------

ROUNDING_RULES = {"half_away_from_zero": ROUND_HALF_UP, "half_even": ROUND_HALF_EVEN}


def _rounded(value: float | int | None, decimals: int, rule: str) -> str | None:
    """A number as text with `decimals` decimals, by a rounding rule of the registry."""
    if rule not in ROUNDING_RULES:
        raise MethodError(f"unknown rounding rule '{rule}'; the registry has "
                          f"{', '.join(sorted(ROUNDING_RULES))}")
    if isinstance(decimals, bool) or not isinstance(decimals, int) or not 0 <= decimals <= 15:
        raise MethodError(f"decimals must be a whole number from 0 to 15, not {decimals!r}")
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise MethodError(f"a number is expected, not {value!r}")
    if isinstance(value, float) and not math.isfinite(value):
        raise MethodError(f"{value!r} cannot be rounded")
    # repr gives the shortest decimal that reads back as the same double.
    exact = Decimal(repr(value)) if isinstance(value, float) else Decimal(value)
    with localcontext() as context:
        context.prec = 400  # a double has at most 309 digits before the point
        rounded = exact.quantize(Decimal(1).scaleb(-decimals), rounding=ROUNDING_RULES[rule])
    if rounded == 0:
        rounded = abs(rounded)  # a zero has no sign
    return format(rounded, "f")


def round_half_away(value: float | int | None, decimals: int) -> str | None:
    """display.round.half_away_from_zero: the number as text with `decimals` decimals."""
    return _rounded(value, decimals, "half_away_from_zero")


def round_half_even(value: float | int | None, decimals: int) -> str | None:
    """display.round.half_even: the number as text with `decimals` decimals."""
    return _rounded(value, decimals, "half_even")


# ---- display.pattern ------------------------------------------------------------

_MASK = re.compile(r"X+(?:[.]X+)?")


def pattern_mask(pattern: object) -> tuple[str, str, str]:
    """A result pattern taken apart: the text before its mask, the mask, the text after."""
    found = list(_MASK.finditer(pattern)) if isinstance(pattern, str) else []
    if len(found) != 1:
        raise MethodError(f"a pattern holds exactly one mask of the letter X, such as XX.X; "
                          f"{pattern!r} holds {len(found)}")
    return pattern[:found[0].start()], found[0].group(), pattern[found[0].end():]


def pattern_text(value: float | int | None, pattern: str, mock: bool = False,
                 rounding: str = "half_away_from_zero") -> str | None:
    """display.pattern: a number as the text a result pattern asks for.

    With `mock` the mask itself is shown, in lower case, in place of the
    number: the text of a mock shell. `rounding` is the option of that name.
    """
    before, mask, after = pattern_mask(pattern)
    if rounding not in ROUNDING_RULES:
        raise MethodError(f"unknown rounding rule '{rounding}'")
    if mock:
        return before + mask.lower() + after
    if value is None:
        return None
    rounded = _rounded(value, len(mask.partition(".")[2]), rounding)
    sign = "-" if rounded.startswith("-") else ""
    digits = rounded.removeprefix("-")
    if "." in mask:
        digits = digits.rjust(len(mask))
    return before + sign + digits + after
