"""Spike: how many printed cells of CSR Table 14-2.01 does the public ADSL reproduce?
Usage: python csr_demog_spike.py <csr.txt from pdftotext -layout> <adsl.parquet>"""
import re, sys, math
from decimal import Decimal, ROUND_HALF_UP
import numpy as np, pandas as pd
from scipy import stats

csr_txt, adsl_path = sys.argv[1], sys.argv[2]
text = open(csr_txt, errors="replace").read()

# ---- 1. reference grid parsed from the CSR text -------------------------------
parts = re.split(r"\n\s{20,}Table (14-\d+\.\d+)\s*\n", text)
pages = [parts[i + 1] for i in range(1, len(parts), 2) if parts[i] == "14-2.01"]
ref = {}          # (variable, row) -> list of printed strings [placebo, low, high, total] and p
STAT = {"n", "Mean", "SD", "Median", "Min", "Max"}
var = None
for pg in pages:
    for line in pg.split("\n"):
        if "(N=" in line: continue                                   # column header repeated on each page
        if re.search(r"^\s*(\[1\]|NOTE|Source|Protocol|Population|square test)", line): 
            if line.strip().startswith("Source"): break
            continue
        m = re.match(r"^\s{4,8}(\S.*?)\s{2,}(\S.*)$", line)          # variable label in the first column
        body = line
        if m and not re.match(r"^\s{20,}", line):
            var = m.group(1).strip(); body = " " * 30 + m.group(2)
        m2 = re.match(r"^\s{20,}(n|Mean|SD|Median|Min|Max|[<>=A-Za-z0-9\- ]+?)\s{2,}(.*)$", body)
        if not (m2 and var): continue
        row, rest = m2.group(1).strip(), m2.group(2)
        cells = re.findall(r"\d+\s*\(\s*<?\d+%\)|-?\d+\.\d+|-?\d+|<\.\d+", rest)
        if not cells: continue
        ref[(var, row)] = cells

# ---- 2. the same cells computed from ADSL -------------------------------------
adsl = pd.read_parquet(adsl_path); itt = adsl[adsl.ITTFL == "Y"].copy()
ARMS = ["Placebo", "Xanomeline Low Dose", "Xanomeline High Dose"]
def r(x, d):                                   # round half away from zero, as SAS prints
    return str(Decimal(repr(float(x))).quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_UP)) if x == x else ""
def cont(v):
    out = {}
    cols = [itt[itt.TRT01P == a][v].dropna() for a in ARMS] + [itt[v].dropna()]
    out["n"] = [str(len(c)) for c in cols]
    out["Mean"] = [r(c.mean(), 1) for c in cols]; out["SD"] = [r(c.std(), 2) for c in cols]
    out["Median"] = [r(c.median(), 1) for c in cols]
    out["Min"] = [r(c.min(), 1) for c in cols]; out["Max"] = [r(c.max(), 1) for c in cols]
    p = stats.f_oneway(*cols[:3]).pvalue
    out["n"].append(r(p, 4))
    return out
def cat(series, levels, labels, test=True):
    out = {}; d = itt.assign(_c=series)
    den = [len(d[d.TRT01P == a]) for a in ARMS] + [len(d)]
    for lv, lab in zip(levels, labels):
        cnt = [int(((d.TRT01P == a) & (d._c == lv)).sum()) for a in ARMS] + [int((d._c == lv).sum())]
        out[lab] = [f"{c} ({r(100*c/n,0)}%)" if c else "0" for c, n in zip(cnt, den)]
    out["n"] = [str(x) for x in den]
    if test:
        tab = pd.crosstab(d.TRT01P, d._c); tab = tab.loc[:, (tab.sum() > 0)]
        out["_p"] = r(stats.chi2_contingency(tab, correction=False)[1], 4)
    return out
origin = np.select([itt.ETHNIC == "HISPANIC OR LATINO", itt.RACE == "WHITE", itt.RACE == "BLACK OR AFRICAN AMERICAN"],
                   ["Hispanic", "Caucasian", "African Descent"], default="Other")
calc = {
 "Age (y)": {**cat(itt.AGEGR1, ["<65", "65-80", ">80"], ["<65 yrs", "65-80 yrs", ">80 yrs"]), **cont("AGE")},
 "Sex": cat(itt.SEX, ["M", "F"], ["Male", "Female"]),
 "Race (Origin)": cat(pd.Series(origin, index=itt.index), ["Caucasian", "African Descent", "Hispanic", "Other"], ["Caucasian", "African Descent", "Hispanic", "Other"]),
 "MMSE": cont("MMSETOT"),
 "Duration of disease": {**cat(itt.DURDSGR1, ["<12", ">=12"], ["<12 months", ">=12 months"]), **cont("DURDIS")},
 "Years of education": cont("EDUCLVL"),
 "Baseline weight(kg)": cont("WEIGHTBL"), "Baseline height(cm)": cont("HEIGHTBL"),
 "Baseline BMI": {**cat(itt.BMIBLGR1, ["<25", "25-<30", ">=30"], ["<25", "25-<30", ">=30"]), **cont("BMIBL")},
}
norm = lambda s: re.sub(r"\s+", "", s).replace("(<1%)", "(0%)")
tot = ok = 0; bad = []
for (v, row), cells in ref.items():
    if v not in calc: bad.append((v, row, "no mapping", cells)); tot += len(cells); continue
    c = calc[v]
    if row in c: exp = list(c[row])
    else: bad.append((v, row, "row not computed", cells)); tot += len(cells); continue
    if row not in STAT and len(cells) == 5: exp = exp + [c.get("_p", "")]          # category row carrying the p-value
    if row == "n" and len(cells) == 5 and len(exp) == 4: exp = exp + [c.get("_p", "")]
    for i, cell in enumerate(cells):
        tot += 1
        e = exp[i] if i < len(exp) else None
        same = e is not None and (norm(cell) == norm(e) or (re.fullmatch(r"-?\d+(\.\d+)?", cell) and re.fullmatch(r"-?\d+(\.\d+)?", e or "x") and abs(float(cell) - float(e)) < 1e-9))
        if same: ok += 1
        else: bad.append((v, row, i, cell, e))
print(f"CSR Table 14-2.01: printed cells parsed={tot} reproduced={ok} ({100*ok/tot:.1f}%)")
for b in bad: print("  differs:", b)
