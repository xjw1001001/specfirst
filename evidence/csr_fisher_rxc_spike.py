"""Spike: which test gives the p-values of CSR Tables 14-6.02 and 14-6.03?

Usage: python csr_fisher_rxc_spike.py <csr.txt>

<csr.txt> is `pdftotext -layout CSR.pdf csr.txt` of the CSR in R Consortium
Pilot 6. Both tables have a p-value column that points to a footnote [1]
which the CSR does not print. The SAP (section 11.5) says: "Fisher's exact
test will be used to analyze the incidence of abnormal (high or low)
measures". That sentence can be read as a test on three categories (low,
normal, high) or on two (normal, abnormal).

This script uses only the counts printed in the two tables (no dataset).
For each analyte it runs an exact Fisher test by full enumeration, once on
the 3 x 3 table (treatment by low, normal, high; empty columns dropped) and
once on the 3 x 2 table (treatment by normal, abnormal), and compares each
result, rounded half up to 3 decimals, with the printed p-value.

Expected last two lines:
  3 x 3 reading (low, normal, high): equal 59 of 59
  3 x 2 reading (normal, abnormal):  equal 10 of 59

Note: scipy.stats.fisher_exact is exact for 2 x 2 tables only. For larger
tables it samples (SciPy 1.18.1), so it is neither exact nor repeatable.
"""
import re
import sys
from decimal import Decimal, ROUND_HALF_UP
from math import exp, lgamma

CELL = r"(\d+)\s*(?:\(\s*\d+%\))?"
ROW = re.compile(r"^\s*([A-Z][A-Z0-9 \-\.'/]*?)\s+" + r"\s+".join([CELL] * 9) + r"(?:\s+(\d?\.\d+))?\s*$")
TABLES = {"14-6.02": (95, 96), "14-6.03": (97, 98)}   # pages of CSR.pdf


def fisher_exact_rxc(table):
    """Exact two-sided Fisher test: sum the probabilities of all tables with
    the observed margins that are no more likely than the observed table."""
    cols = [j for j in range(len(table[0])) if sum(r[j] for r in table) > 0]
    table = [[r[j] for j in cols] for r in table if sum(r) > 0]
    rows_t = [sum(r) for r in table]
    cols_t = [sum(r[j] for r in table) for j in range(len(cols))]
    if len(rows_t) < 2 or len(cols_t) < 2:
        return None
    const = sum(lgamma(x + 1) for x in rows_t + cols_t) - lgamma(sum(rows_t) + 1)

    def logp(t):
        return const - sum(lgamma(x + 1) for r in t for x in r)

    obs = logp(table)
    total = 0.0

    def fill(i, row, done, col_left):
        nonlocal total
        if i == len(rows_t) - 1:              # the last row is what is left
            lp = logp(done + [col_left])
            if lp <= obs + 1e-7:
                total += exp(lp)
            return
        j = len(row)
        left = rows_t[i] - sum(row)
        if j == len(cols_t) - 1:              # the last cell of a row is what is left
            if left <= col_left[j]:
                nxt = col_left[:]
                nxt[j] -= left
                fill(i + 1, [], done + [row + [left]], nxt)
            return
        for x in range(min(left, col_left[j]) + 1):
            nxt = col_left[:]
            nxt[j] -= x
            fill(i, row + [x], done, nxt)

    fill(0, [], [], cols_t)
    return min(1.0, total)


def half_up(x, places):
    return str(Decimal(repr(float(x))).quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP))


def main(csr_txt):
    pages = open(csr_txt, encoding="utf-8", errors="replace").read().split("\f")
    ok = ok2 = total = 0
    for table, page_numbers in TABLES.items():
        rows = with_p = 0
        for pg in page_numbers:
            for line in pages[pg - 1].split("\n"):
                m = ROW.match(line)
                if not m:
                    continue
                rows += 1
                c = [int(x) for x in m.groups()[1:10]]
                printed = m.group(11)
                p = fisher_exact_rxc([c[0:3], c[3:6], c[6:9]])
                if printed is None:
                    print(f"{table} {m.group(1):12s} no p-value printed; test defined: {p is not None}")
                    continue
                with_p += 1
                total += 1
                shown = half_up(p, 3)
                if shown == printed:
                    ok += 1
                else:
                    print(f"{table} {m.group(1):12s} exact p={p:.6f} shown {shown} csr {printed} DIFFERENT")
                p2 = fisher_exact_rxc([[c[i + 1], c[i] + c[i + 2]] for i in (0, 3, 6)])
                ok2 += p2 is not None and half_up(p2, 3) == printed
        print(f"{table}: rows {rows}, with a printed p-value {with_p}")
    print(f"3 x 3 reading (low, normal, high): equal {ok} of {total}")
    print(f"3 x 2 reading (normal, abnormal):  equal {ok2} of {total}")


if __name__ == "__main__":
    main(sys.argv[1])
