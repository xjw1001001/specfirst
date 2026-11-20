"""A second computation of the vectors of the mixed model for repeated measures.

The R implementation fits the model with the package mmrm and takes the LS
means and their differences from emmeans (ADR-015, amendment of real-5b).
This module computes the same quantities another way, from the statements
of standard/methods/model.mmrm.*.yaml and from Kenward and Roger (1997), in
numpy: the restricted likelihood is maximized by Fisher scoring in the
distinct entries of the covariance matrix, which it is linear in; the
coefficients follow by generalized least squares; the degrees of freedom
and the adjusted covariance of Kenward and Roger, and the degrees of freedom
of Satterthwaite, are written out from their formulas. It shares no code
with mmrm, TMB or emmeans. The tail and the quantile of the t distribution
for degrees of freedom that are not whole come from scipy.

There is no closed form: the values agree with the R implementation to the
precision the two optimizations reach (test_methods, model-vectors).

Nothing here is used by an engine.
"""

from __future__ import annotations

import math

import numpy as np
from scipy.special import stdtr, stdtrit


class NotFitted(Exception):
    """The model cannot be fitted (statement 10 of model.mmrm.lsmeans)."""


def _missing(value) -> bool:
    return value is None or value == "" or (isinstance(value, float) and math.isnan(value))


def _order(values) -> list:
    """The distinct values in increasing order: numbers by value, text by code points."""
    distinct = set(values)
    if all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in distinct):
        return sorted(distinct, key=float)
    return sorted(distinct, key=str)


class Model:
    """The model of statements 1 to 5 of model.mmrm.lsmeans, fitted."""

    def __init__(self, given: dict, options: dict):
        factors = list(options.get("factors") or [])
        covariates = list(options.get("covariates") or [])
        visit_names = list(options.get("visit") or [])
        by_visit = list(options.get("by_visit") or [])
        if len(visit_names) != 1:
            raise ValueError("the option visit names one column")
        if set(factors) & set(covariates):
            raise ValueError("a column is both a factor and a covariate")
        if not set(by_visit) <= set(factors) | set(covariates):
            raise ValueError("a column of by_visit is not a factor or a covariate")
        groups = list(given["groups"])
        y_all, group_all = given["y"], given["group"]
        visit_all, subject_all = given["visit"], given["subject"]
        keep = []
        for i in range(len(y_all)):
            if _missing(y_all[i]) or _missing(group_all[i]) or group_all[i] not in groups:
                continue
            if _missing(visit_all[i]) or _missing(subject_all[i]):
                continue
            if any(_missing(given["factors"][f][i]) for f in factors):
                continue
            if any(_missing(given["covariates"][c][i]) for c in covariates):
                continue
            keep.append(i)
        self.groups = groups
        self.y = np.array([float(y_all[i]) for i in keep])
        self.group = [group_all[i] for i in keep]
        visits = [visit_all[i] for i in keep]
        self.visits = _order(visits)
        self.visit = [self.visits.index(v) for v in visits]
        subjects = [str(subject_all[i]) for i in keep]
        seen = set()
        for s, v in zip(subjects, self.visit, strict=True):
            if (s, v) in seen:
                raise ValueError("two model records of one subject at one visit")
            seen.add((s, v))
        self.present = [g for g in groups if g in set(self.group)]
        self.n = len(keep)
        t = len(self.visits)
        if t < 2:
            raise NotFitted("fewer than two visits (statement 11)")
        # The columns of the design, each with a function of a reference-grid point.
        cols: list[tuple[str, object]] = [("mu", lambda p: 1.0)]
        for g in self.present[1:]:
            cols.append((f"tau[{g}]", lambda p, g=g: float(p["group"] == g)))
        for v in range(1, t):
            cols.append((f"alpha[{v}]", lambda p, v=v: p["visit"].get(v, 0.0)))
        if options.get("treatment_by_visit", "yes") == "yes":
            for g in self.present[1:]:
                for v in range(1, t):
                    cols.append((f"tau.alpha[{g},{v}]",
                                 lambda p, g=g, v=v:
                                 float(p["group"] == g) * p["visit"].get(v, 0.0)))
        levels = {}
        for f in factors:
            values = [str(given["factors"][f][i]) for i in keep]
            levels[f] = sorted(set(values))
            if len(levels[f]) < 2:
                continue  # a factor with one level is left out
            for level in levels[f][1:]:
                cols.append((f"beta[{f}={level}]",
                             lambda p, f=f, level=level: p["factor"][f].get(level, 0.0)))
                if f in by_visit:
                    for v in range(1, t):
                        cols.append((f"beta.alpha[{f}={level},{v}]",
                                     lambda p, f=f, level=level, v=v:
                                     p["factor"][f].get(level, 0.0) * p["visit"].get(v, 0.0)))
        means = {}
        for c in covariates:
            values = np.array([float(given["covariates"][c][i]) for i in keep])
            means[c] = float(values.mean()) if len(values) else 0.0
            cols.append((f"gamma[{c}]", lambda p, c=c: p["covariate"][c]))
            if c in by_visit:
                for v in range(1, t):
                    cols.append((f"delta[{c},{v}]",
                                 lambda p, c=c, v=v: p["covariate"][c] * p["visit"].get(v, 0.0)))
        self.columns = cols
        self.levels = {f: levels[f] for f in factors if len(levels[f]) >= 2}
        self.means = means
        rows = []
        for k, i in enumerate(keep):
            point = {"group": self.group[k], "visit": {self.visit[k]: 1.0},
                     "factor": {f: {str(given["factors"][f][i]): 1.0} for f in factors},
                     "covariate": {c: float(given["covariates"][c][i]) for c in covariates}}
            rows.append([fn(point) for _, fn in cols])
        self.x = np.array(rows, dtype=float).reshape(self.n, len(cols))
        if self.n == 0 or np.linalg.matrix_rank(self.x) < len(cols):
            raise NotFitted("the design has no full column rank")
        # Subjects and their records, in the order of the records.
        by_subject: dict[str, list[int]] = {}
        for k, s in enumerate(subjects):
            by_subject.setdefault(s, []).append(k)
        self.blocks = [(rows_, [self.visit[k] for k in rows_]) for rows_ in by_subject.values()]
        # Statement 4: the covariance, linear in its distinct entries.
        self.basis = []
        if options.get("covariance", "unstructured") == "unstructured":
            for j in range(t):
                for k in range(j, t):
                    e = np.zeros((t, t))
                    e[j, k] = e[k, j] = 1.0
                    self.basis.append(e)
        else:  # toeplitz
            for d in range(t):
                e = np.zeros((t, t))
                for j in range(t - d):
                    e[j, j + d] = e[j + d, j] = 1.0
                self.basis.append(e)
        self._fit()

    # ---- the restricted likelihood ------------------------------------------------

    def sigma(self, theta) -> np.ndarray:
        return sum(th * e for th, e in zip(theta, self.basis, strict=True))

    def _parts(self, theta):
        """V^-1 as a dense matrix over the records, the G_k as dense matrices, Phi, Pi."""
        s = self.sigma(theta)
        n = self.n
        vinv = np.zeros((n, n))
        logdet = 0.0
        for rows_, vis in self.blocks:
            block = s[np.ix_(vis, vis)]
            sign, value = np.linalg.slogdet(block)
            if sign <= 0:
                return None
            logdet += value
            vinv[np.ix_(rows_, rows_)] = np.linalg.inv(block)
        gs = []
        for e in self.basis:
            g = np.zeros((n, n))
            for rows_, vis in self.blocks:
                g[np.ix_(rows_, rows_)] = e[np.ix_(vis, vis)]
            gs.append(g)
        xtv = self.x.T @ vinv
        info = xtv @ self.x
        sign, logdet_x = np.linalg.slogdet(info)
        if sign <= 0:
            return None
        phi = np.linalg.inv(info)
        pi = vinv - xtv.T @ phi @ xtv
        return vinv, gs, phi, pi, logdet, logdet_x

    def _loglik(self, parts) -> float:
        vinv, gs, phi, pi, logdet, logdet_x = parts
        return -0.5 * (logdet + logdet_x + float(self.y @ pi @ self.y))

    def _fit(self):
        t = len(self.visits)
        # Start: the variance of the records of each visit around the least-squares fit.
        beta, *_ = np.linalg.lstsq(self.x, self.y, rcond=None)
        resid = self.y - self.x @ beta
        start = np.zeros((t, t))
        for v in range(t):
            values = [resid[k] for k in range(self.n) if self.visit[k] == v]
            start[v, v] = max(float(np.mean(np.square(values))) if values else 1.0, 1e-6)
        theta = np.array([float(np.sum(start * e) / np.sum(e * e)) for e in self.basis])
        parts = self._parts(theta)
        if parts is None:
            raise NotFitted("the starting covariance is singular")
        value = self._loglik(parts)
        for _ in range(500):
            vinv, gs, phi, pi, *_ = parts
            pig = [pi @ g for g in gs]
            piy = pi @ self.y
            score = np.array([-0.5 * np.trace(a) + 0.5 * float(piy @ g @ piy)
                              for a, g in zip(pig, gs, strict=True)])
            expected = np.array([[0.5 * np.sum(a * b.T) for b in pig] for a in pig])
            step = np.linalg.solve(expected, score)
            factor = 1.0
            while True:
                trial = theta + factor * step
                trial_parts = self._parts(trial)
                if (trial_parts is not None
                        and self._loglik(trial_parts) >= value - 1e-12 * abs(value)):
                    break
                factor /= 2
                if factor < 1e-10:
                    raise NotFitted("the restricted likelihood does not increase")
            change = np.max(np.abs(trial - theta)) / max(1.0, np.max(np.abs(theta)))
            theta, parts, value = trial, trial_parts, self._loglik(trial_parts)
            # On a flat ridge of the likelihood theta wanders and this does not converge
            # (review of real-5b, F4): the vectors keep away from such data.
            if change < 1e-14:
                break
        else:
            raise NotFitted("Fisher scoring did not converge")
        self.theta = theta
        vinv, gs, phi, pi, *_ = parts
        self.phi = phi
        self.beta = phi @ self.x.T @ vinv @ self.y
        pig = [pi @ g for g in gs]
        piy = pi @ self.y
        self.expected = np.array([[0.5 * np.sum(a * b.T) for b in pig] for a in pig])
        self.observed = np.array([[-0.5 * np.sum(a * b.T) + float(piy @ ga @ pi @ gb @ piy)
                                   for b, gb in zip(pig, gs, strict=True)]
                                  for a, ga in zip(pig, gs, strict=True)])
        vg = [vinv @ g @ vinv for g in gs]  # V^-1 G_k V^-1
        self.p = [-(self.x.T @ m @ self.x) for m in vg]
        self.q = [[self.x.T @ vinv @ gs[k] @ vinv @ gs[j] @ vinv @ self.x
                   for j in range(len(gs))] for k in range(len(gs))]

    # ---- the LS means and their differences ---------------------------------------

    def l_vector(self, group: str, at: str) -> np.ndarray:
        """Statement 6: the coefficients of the LS mean of a group."""
        t = len(self.visits)
        visit_weights = {t - 1: 1.0} if at == "last" else {v: 1.0 / t for v in range(t)}
        point = {"group": group, "visit": visit_weights,
                 "factor": {f: {level: 1.0 / len(levels) for level in levels}
                            for f, levels in self.levels.items()},
                 "covariate": dict(self.means)}
        # A product of a factor or a covariate with the visit: the average of the products,
        # which with the weights above is the product of the averages.
        for f in self.levels:
            point["factor"].setdefault(f, {})
        return np.array([fn(point) for _, fn in self.columns])

    def inference(self, c: np.ndarray, df_method: str) -> dict:
        """Statements 7 and 8: the estimate, its standard error and degrees of freedom."""
        estimate = float(c @ self.beta)
        variance = float(c @ self.phi @ c)
        # The gradient of c' Phi c in the covariance parameters: dPhi = -Phi P_k Phi.
        gradient = np.array([-float(c @ self.phi @ pk @ self.phi @ c) for pk in self.p])
        # W: the inverse of the observed information of the restricted likelihood, for
        # both methods (statement 8).
        w = np.linalg.inv(self.observed)
        if df_method == "satterthwaite":
            se = math.sqrt(variance)
        else:  # kenward_roger_linear: Kenward and Roger (1997), R_ij = 0
            k = len(self.p)
            inner = sum(w[i, j] * (self.q[i][j] - self.p[i] @ self.phi @ self.p[j])
                        for i in range(k) for j in range(k))
            adjusted = self.phi + 2 * self.phi @ inner @ self.phi
            se = math.sqrt(float(c @ adjusted @ c))
        df = 2 * variance ** 2 / float(gradient @ w @ gradient)
        return {"estimate": estimate, "se": se, "df": df}


def _limits(estimate, se, df, level):
    q = float(stdtrit(df, 1 - (1 - level / 100) / 2))
    return estimate - q * se, estimate + q * se


def lsmeans(given: dict, options: dict) -> dict:
    groups = list(given["groups"])
    ops = ("lsmean", "se", "lower_cl", "upper_cl")
    out = {op: {g: None for g in groups} for op in ops}
    try:
        model = Model(given, options)
    except NotFitted:
        return out
    level = options.get("confidence_level", 95)
    for g in model.present:
        found = model.inference(model.l_vector(g, options.get("at", "last")),
                                options.get("df", "kenward_roger_linear"))
        low, high = _limits(found["estimate"], found["se"], found["df"], level)
        out["lsmean"][g], out["se"][g] = found["estimate"], found["se"]
        out["lower_cl"][g], out["upper_cl"][g] = low, high
    return out


def pairwise(given: dict, options: dict) -> dict:
    groups = list(given["groups"])
    reference = options["reference"]
    others = [g for g in groups if g != reference]
    ops = ("estimate", "se", "lower_cl", "upper_cl", "p_value")
    out = {op: {g: None for g in others} for op in ops}
    try:
        model = Model(given, options)
    except NotFitted:
        return out
    if reference not in model.present:
        return out
    level = options.get("confidence_level", 95)
    at = options.get("at", "last")
    base = model.l_vector(reference, at)
    for g in others:
        if g not in model.present:
            continue
        found = model.inference(model.l_vector(g, at) - base,
                                options.get("df", "kenward_roger_linear"))
        low, high = _limits(found["estimate"], found["se"], found["df"], level)
        tail = float(stdtr(found["df"], -abs(found["estimate"] / found["se"])))
        out["estimate"][g], out["se"][g] = found["estimate"], found["se"]
        out["lower_cl"][g], out["upper_cl"][g] = low, high
        out["p_value"][g] = 2 * tail
    return out


def expected(method: str, case: dict) -> dict:
    given, options = case["input"], case.get("options") or {}
    if method == "model.mmrm.lsmeans":
        return lsmeans(given, options)
    if method == "model.mmrm.pairwise":
        return pairwise(given, options)
    raise ValueError(method)
