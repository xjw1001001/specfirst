"""Spike: CSR Table 14-6.06 (Shifts of Hy's Law Values During Treatment).

Usage: python csr_hylaw_spike.py <adam_dir>

Rebuilds the 51 printed cells of the table (counts, percents and two CMH
p-values) from the public ADLBHY and ADLBC datasets and compares them with
the values printed in the CSR (page 138 of CSR.pdf in R Consortium Pilot 6).
The CSR values are typed in below because the table is one small page.

Three variants are built. They differ in two decisions:

  shift rule     footnote:   a subject changes status when any visit during
                             treatment differs from baseline (CSR footnote 1)
                 worst_case: a subject is High when any visit during
                             treatment is high. This is the SAP's rule
                             (section 11.5: "the most extreme value").
  baseline rule  reference:  the baseline of the reference ADaM: the
                             scheduled screening visit only. The SAP says
                             baseline is the value collected at Visit 1.
                 last_predose: the last value before the first dose date,
                             unscheduled visits included. It gives the same
                             status as the reference for the 252 subjects
                             who have a screening value, and a baseline to
                             the 2 subjects who have none.

Expected output (reference ADaM of Pilot 7; SciPy 1.18.1):
  footnote   + reference     38 of 51   p 0.405 and 0.386
  worst_case + reference     45 of 51   p 0.405 and 0.386
  worst_case + last_predose  51 of 51   p 0.392 and 0.381
"""
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import chi2

ARMS = ["Placebo", "Xanomeline Low Dose", "Xanomeline High Dose"]

# Printed in the CSR: per parameter and arm, (n, Normal, High) for subjects
# normal at baseline and for subjects high at baseline; the percents printed
# next to the counts (None where the CSR prints a bare 0); the p-value.
CSR = {
    "TRANSHY": {"counts": [((82, 79, 3), (2, 0, 2)), ((80, 79, 1), (2, 1, 1)), ((80, 77, 3), (0, 0, 0))],
                "pct": [(("96", "4"), (None, "100")), (("99", "1"), ("50", "50")), (("96", "4"), (None, None))],
                "p": "0.392"},
    "HYLAW": {"counts": [((84, 83, 1), (0, 0, 0)), ((82, 82, 0), (0, 0, 0)), ((80, 80, 0), (0, 0, 0))],
              "pct": [(("99", "1"), (None, None)), (("100", None), (None, None)), (("100", None), (None, None))],
              "p": "0.381"},
}


def half_up(x, places):
    q = Decimal(1).scaleb(-places)
    return str(Decimal(repr(float(x))).quantize(q, rounding=ROUND_HALF_UP))


def cmh_general(tables):
    """Generalized CMH statistic for general association over strata.

    tables: list of (rows x columns) count arrays, one per stratum.
    A stratum with fewer than 2 subjects adds nothing. Returns (Q, df, p).
    """
    r, c = tables[0].shape
    keep = [i * c + j for i in range(r - 1) for j in range(c - 1)]
    d = np.zeros(len(keep))
    v = np.zeros((len(keep), len(keep)))
    for t in tables:
        t = np.asarray(t, dtype=float)
        n = t.sum()
        if n < 2:
            continue
        pr = t.sum(axis=1) / n
        pc = t.sum(axis=0) / n
        exp = n * np.outer(pr, pc)
        cov = n * n / (n - 1) * np.kron(np.diag(pr) - np.outer(pr, pr), np.diag(pc) - np.outer(pc, pc))
        d += (t - exp).reshape(-1)[keep]
        v += cov[np.ix_(keep, keep)]
    df = int(np.linalg.matrix_rank(v))
    q = float(d @ np.linalg.pinv(v) @ d)
    return q, df, float(chi2.sf(q, df))


def predose_baseline(adam_dir, subjects):
    """Baseline status from the last pre-dose chemistry record, unscheduled included."""
    c = pl.read_parquet(Path(adam_dir) / "adlbc.parquet")
    c = c.filter(pl.col("USUBJID").is_in(subjects) & pl.col("PARAMCD").is_in(["ALT", "AST", "BILI"])
                 & (pl.col("ADY") < 1))
    last = c.sort("ADT").group_by("USUBJID", "PARAMCD").agg(pl.col("R2A1HI").last())
    out = {}
    for s in subjects:
        r = {row["PARAMCD"]: row["R2A1HI"] for row in last.filter(pl.col("USUBJID") == s).iter_rows(named=True)}
        if not {"ALT", "AST", "BILI"} <= set(r):
            continue
        trans = r["ALT"] > 1.5 or r["AST"] > 1.5
        out[s] = {"TRANSHY": float(trans), "HYLAW": float(trans and r["BILI"] > 1.5)}
    return out


def build(adam_dir, shift_rule, baseline_rule):
    d = pl.read_parquet(Path(adam_dir) / "adlbhy.parquet").filter(pl.col("SAFFL") == "Y")
    ok = total = 0
    pvals = []
    for paramcd, ref in CSR.items():
        x = d.filter((pl.col("PARAMCD") == paramcd) & (pl.col("AVISITN") > 0) & (pl.col("AVISITN") <= 24))
        if baseline_rule == "last_predose":
            # replace the baseline status of every subject by the rule's result
            subjects = sorted(set(x["USUBJID"].to_list()))
            fill = {s: v[paramcd] for s, v in predose_baseline(adam_dir, subjects).items()}
            x = x.with_columns(
                pl.col("USUBJID").replace_strict(fill, default=None, return_dtype=pl.Float64).alias("BASE"))
        x = x.filter(pl.col("BASE").is_not_null())
        # BASE and AVAL are 0 (normal) or 1 (high). SHIFT1 is not used: it is
        # empty for records that are high at baseline and high at the visit.
        subj = x.group_by("USUBJID", "TRTA", "BASE").agg(
            (pl.col("AVAL") == 1).any().alias("ANY_HIGH"),
            (pl.col("AVAL") != pl.col("BASE")).any().alias("ANY_CHANGE"))
        if shift_rule == "worst_case":
            subj = subj.with_columns(pl.col("ANY_HIGH").alias("HIGH"))
        else:
            subj = subj.with_columns(
                pl.when(pl.col("ANY_CHANGE")).then(pl.col("BASE") == 0).otherwise(pl.col("BASE") == 1).alias("HIGH"))
        strata = []
        for bl in (0, 1):
            tab = np.zeros((3, 2))
            for i, arm in enumerate(ARMS):
                s = subj.filter((pl.col("TRTA") == arm) & (pl.col("BASE") == bl))
                tab[i, 1] = s.filter(pl.col("HIGH")).height
                tab[i, 0] = s.height - tab[i, 1]
            strata.append(tab)
        for i in range(3):
            for k, tab in enumerate(strata):
                n = int(tab[i].sum())
                for g, e in zip((n, int(tab[i, 0]), int(tab[i, 1])), ref["counts"][i][k]):
                    total += 1
                    ok += g == e
                for j in (0, 1):
                    e = ref["pct"][i][k][j]
                    if e is None:
                        continue
                    total += 1
                    ok += n > 0 and half_up(100 * tab[i, j] / n, 0) == e
        p = half_up(cmh_general(strata)[2], 3)
        pvals.append(p)
        total += 1
        ok += p == ref["p"]
    return ok, total, pvals


def main(adam_dir):
    for shift_rule, baseline_rule in (("footnote", "reference"), ("worst_case", "reference"),
                                      ("worst_case", "last_predose")):
        ok, total, pvals = build(adam_dir, shift_rule, baseline_rule)
        print(f"shift={shift_rule:10s} baseline={baseline_rule:12s} equal {ok} of {total}  "
              f"p-values {pvals[0]} and {pvals[1]}  (CSR prints 0.392 and 0.381)")


if __name__ == "__main__":
    main(sys.argv[1])
