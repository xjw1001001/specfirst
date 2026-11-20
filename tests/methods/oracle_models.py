"""A second computation of the vectors of the model-based methods (ADR-015).

The R implementations fit with stats::lm and take the LS means, their
differences and their limits from emmeans, and the F test of the dose from
car::Anova. This module shares none of that: the least-squares solution is
computed in exact fractions (Gauss-Jordan elimination on the normal
equations), the LS means and contrasts from their coefficient vectors as the
registry's statements write them, and the t distribution from its closed form
for whole degrees of freedom (Abramowitz and Stegun 26.7.3 and 26.7.4), in
decimal arithmetic with 60 digits. A quantile is found by bisection on that
closed form. The normal distribution comes from the series of erf.

The vectors use designs of full rank, apart from groups without model records,
which this module leaves out of the design as the statements say.

Nothing here is used by an engine.
"""

from __future__ import annotations

from decimal import Decimal, localcontext
from fractions import Fraction

PRECISION = 60


class NotFullRank(Exception):
    """The design matrix of a vector is not of full rank."""


# ---- exact linear algebra ------------------------------------------------------------


def _inverse(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    size = len(matrix)
    work = [list(row) + [Fraction(int(i == j)) for j in range(size)]
            for i, row in enumerate(matrix)]
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column] != 0), None)
        if pivot is None:
            raise NotFullRank("the normal equations are singular")
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [value / scale for value in work[column]]
        for row in range(size):
            if row != column and work[row][column] != 0:
                factor = work[row][column]
                work[row] = [a - factor * b for a, b in zip(work[row], work[column], strict=True)]
    return [row[size:] for row in work]


def _fit(rows: list[list[Fraction]], y: list[Fraction]) -> tuple[list[Fraction],
                                                                   list[list[Fraction]], int]:
    """Coefficients, their covariance matrix and the residual degrees of freedom."""
    columns = len(rows[0])
    if len(rows) - columns < 1:  # no residual degrees of freedom: nothing is estimated
        return [], [], len(rows) - columns
    xtx = [[sum(row[i] * row[j] for row in rows) for j in range(columns)] for i in range(columns)]
    xty = [sum(row[i] * value for row, value in zip(rows, y, strict=True))
           for i in range(columns)]
    inverse = _inverse(xtx)
    beta = [sum(inverse[i][j] * xty[j] for j in range(columns)) for i in range(columns)]
    residual = sum((value - sum(b * x for b, x in zip(beta, row, strict=True))) ** 2
                   for row, value in zip(rows, y, strict=True))
    df = len(rows) - columns
    variance = residual / df
    return beta, [[variance * value for value in row] for row in inverse], df


def _quadratic(vector: list[Fraction], covariance: list[list[Fraction]]) -> Fraction:
    return sum(vector[i] * covariance[i][j] * vector[j]
               for i in range(len(vector)) for j in range(len(vector)))


def _dot(one: list[Fraction], two: list[Fraction]) -> Fraction:
    return sum(a * b for a, b in zip(one, two, strict=True))


# ---- the t and the normal distribution ---------------------------------------------


def _decimal(value: Fraction) -> Decimal:
    return Decimal(value.numerator) / Decimal(value.denominator)


def _atan(x: Decimal) -> Decimal:
    """arctan by halving the angle until the series converges fast."""
    halvings = 0
    while abs(x) > Decimal("0.1"):
        x = x / (1 + (1 + x * x).sqrt())
        halvings += 1
    term, total, n = x, x, 1
    square = x * x
    while True:
        term = -term * square
        step = term / (2 * n + 1)
        if abs(step) < Decimal(10) ** -(PRECISION + 5):
            break
        total += step
        n += 1
    return total * (2 ** halvings)


def _pi() -> Decimal:
    return 4 * (4 * _atan(Decimal(1) / 5) - _atan(Decimal(1) / 239))


def t_central(t: Decimal, df: int) -> Decimal:
    """P(|T| <= t) for T with the t distribution of df degrees of freedom, t >= 0."""
    with localcontext() as context:
        context.prec = PRECISION
        nu = Decimal(df)
        denominator = (nu + t * t).sqrt()
        sine, cosine = t / denominator, nu.sqrt() / denominator
        square = cosine * cosine
        if df % 2 == 0:  # A and S 26.7.4
            term, total = Decimal(1), Decimal(1)
            for k in range(1, df // 2):
                term = term * square * Decimal(2 * k - 1) / Decimal(2 * k)
                total += term
            return sine * total
        theta = _atan(t / nu.sqrt())  # A and S 26.7.3
        if df == 1:
            return 2 * theta / _pi()
        term, total = cosine, cosine
        for k in range(1, (df - 1) // 2):
            term = term * square * Decimal(2 * k) / Decimal(2 * k + 1)
            total += term
        return 2 * (theta + sine * total) / _pi()


def normal_central(z: Decimal) -> Decimal:
    """P(|Z| <= z) = erf(z / sqrt 2), by the series of erf."""
    with localcontext() as context:
        context.prec = PRECISION + 20
        x = z / Decimal(2).sqrt()
        term, total, n = x, x, 0
        while True:
            n += 1
            term = -term * x * x / n
            step = term / (2 * n + 1)
            if abs(step) < Decimal(10) ** -(PRECISION + 10):
                break
            total += step
        return 2 * total / _pi().sqrt()


def central(value: Decimal, df: int | None) -> Decimal:
    return normal_central(value) if df is None else t_central(value, df)


def two_sided_p(statistic: Decimal, df: int | None) -> float:
    with localcontext() as context:
        context.prec = PRECISION
        return float(1 - central(abs(statistic), df))


def quantile(level: int, df: int | None) -> Decimal:
    """The q with P(|T| <= q) = level / 100, by bisection on the closed form."""
    with localcontext() as context:
        context.prec = PRECISION
        wanted = Decimal(level) / 100
        low, high = Decimal(0), Decimal(10000 if df is not None else 40)
        for _ in range(260):
            middle = (low + high) / 2
            if central(middle, df) < wanted:
                low = middle
            else:
                high = middle
        return (low + high) / 2


# ---- the models ----------------------------------------------------------------------


def _number(value) -> Fraction:
    return Fraction(str(value))


def _model(case: dict, lead: str) -> dict | None:
    """The model records and the design of statement 2 of model.ancova.lsmeans.

    lead "groups": the groups as a factor; "dose": the dose of statement 2 of
    model.ancova.dose_response as a covariate.
    """
    given, options = case["input"], case.get("options") or {}
    factors = list(options.get("factors") or [])
    covariates = list(options.get("covariates") or [])
    keep = []
    for i, value in enumerate(given["y"]):
        if value is None or given["group"][i] in (None, ""):
            continue
        if any(given["factors"][name][i] in (None, "") for name in factors):
            continue
        if any(given["covariates"][name][i] is None for name in covariates):
            continue
        keep.append(i)
    groups = [g for g in given["groups"] if any(given["group"][i] == g for i in keep)]
    if not keep:
        return None
    levels = {}
    for name in factors:
        found = sorted({given["factors"][name][i] for i in keep})
        if len(found) > 1:  # a factor with one level is left out
            levels[name] = found
    means = {name: sum(_number(given["covariates"][name][i]) for i in keep) / len(keep)
             for name in covariates}
    doses = {}
    if lead == "dose" or options.get("model") == "linear_contrast":
        for g in groups:
            if options.get("dose", "grouping_value") == "group_rank":
                doses[g] = Fraction(given["groups"].index(g) + 1)
            else:
                values = {_number(given["dose"][i]) for i in keep if given["group"][i] == g}
                assert len(values) == 1, "a group with two doses"
                doses[g] = values.pop()

    def row(i: int | None, group: str | None, dose: Fraction | None,
            weights: str = "equal") -> list[Fraction]:
        """A row of the design; with i None, the averaged row of an LS mean."""
        out = [Fraction(1)]
        if lead == "groups":
            out += [Fraction(int(group == g)) for g in groups[1:]]
        else:
            out.append(dose)
        for name, found in levels.items():
            if i is not None:
                out += [Fraction(int(given["factors"][name][i] == level)) for level in found[1:]]
            elif weights == "equal":
                out += [Fraction(1, len(found)) for _ in found[1:]]
            else:
                out += [Fraction(sum(1 for k in keep if given["factors"][name][k] == level),
                                 len(keep)) for level in found[1:]]
        for name in covariates:
            out.append(_number(given["covariates"][name][i]) if i is not None else means[name])
        return out

    if lead == "dose" and (len(groups) < 2 or len(set(doses.values())) < 2):
        # Statement 6 of model.ancova.dose_response: nothing to fit.
        return {"groups": groups, "doses": doses, "df": 0}
    rows = [row(i, given["group"][i],
                doses.get(given["group"][i]) if lead == "dose" else None) for i in keep]
    y = [_number(given["y"][i]) for i in keep]
    beta, covariance, df = _fit(rows, y)
    return {"groups": groups, "row": row, "beta": beta, "covariance": covariance, "df": df,
            "doses": doses, "lead": lead}


def _df(model: dict, options: dict) -> int | None:
    return None if options.get("df", "residual") == "asymptotic" else model["df"]


def _inference(vector: list[Fraction], model: dict, options: dict,
               level: int | None) -> dict:
    estimate = _dot(vector, model["beta"])
    with localcontext() as context:
        context.prec = PRECISION
        se = _decimal(_quadratic(vector, model["covariance"])).sqrt()
        df = _df(model, options)
        out = {"estimate": float(_decimal(estimate)), "se": float(se),
               "p_value": two_sided_p(_decimal(estimate) / se, df)}
        if level is not None:
            q = quantile(level, df)
            out["lower_cl"] = float(_decimal(estimate) - q * se)
            out["upper_cl"] = float(_decimal(estimate) + q * se)
    return out


def lsmeans(case: dict) -> dict:
    options = case.get("options") or {}
    names = ("lsmean", "se", "lower_cl", "upper_cl")
    out = {name: {g: None for g in case["input"]["groups"]} for name in names}
    model = _model(case, "groups")
    if model is None or model["df"] < 1:
        return out
    for g in model["groups"]:
        vector = model["row"](None, g, None, options.get("weights", "equal"))
        found = _inference(vector, model, options, options.get("confidence_level", 95))
        out["lsmean"][g] = found["estimate"]
        for name in ("se", "lower_cl", "upper_cl"):
            out[name][g] = found[name]
    return out


def pairwise(case: dict) -> dict:
    options = case.get("options") or {}
    reference = options["reference"]
    names = ("estimate", "se", "lower_cl", "upper_cl", "p_value")
    others = [g for g in case["input"]["groups"] if g != reference]
    out = {name: {g: None for g in others} for name in names}
    model = _model(case, "groups")
    if model is None or model["df"] < 1 or reference not in model["groups"]:
        return out
    base = model["row"](None, reference, None)
    for g in others:
        if g not in model["groups"]:
            continue
        vector = [a - b for a, b in zip(model["row"](None, g, None), base, strict=True)]
        found = _inference(vector, model, options, options.get("confidence_level", 95))
        for name in names:
            out[name][g] = found[name]
    return out


def dose_response(case: dict) -> dict:
    options = case.get("options") or {}
    missing = {"p_value": None, "estimate": None}
    contrast = options.get("model", "continuous_dose") == "linear_contrast"
    model = _model(case, "groups" if contrast else "dose")
    if model is None or len(model["groups"]) < 2 or model["df"] < 1:
        return missing
    doses = model["doses"]
    if len(set(doses.values())) < 2:
        return missing
    if contrast:
        mean = sum(doses.values()) / len(doses)
        vector = [Fraction(0)] * len(model["beta"])
        for place, g in enumerate(model["groups"][1:], start=1):
            vector[place] = doses[g] - mean  # tau of the first group is 0
    else:
        vector = [Fraction(0)] * len(model["beta"])
        vector[1] = Fraction(1)
    found = _inference(vector, model, options, None)
    return {"p_value": found["p_value"], "estimate": found["estimate"]}


def expected(method: str, case: dict) -> dict:
    if method == "model.ancova.lsmeans":
        return lsmeans(case)
    if method == "model.ancova.pairwise":
        return pairwise(case)
    if method == "model.ancova.dose_response":
        return dose_response(case)
    raise KeyError(method)
