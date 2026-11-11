"""Spike: CSR Table 14-5.01 (TEAE by system organ class and preferred term) against the public ADAE.
Usage: python csr_ae_spike.py <csr.txt from pdftotext -layout> <adam dir>"""
import re, sys
from decimal import Decimal, ROUND_HALF_UP
import pandas as pd
from scipy import stats

text = open(sys.argv[1], errors="replace").read(); A = sys.argv[2]
parts = re.split(r"\n\s{20,}Table (14-\d+\.\d+)\s*\n", text)
pages = [parts[i + 1] for i in range(1, len(parts), 2) if parts[i] == "14-5.01"]

ARM = re.compile(r"^(\d+)\s*\(\s*(\d+\.\d)%\)\s*\[(\d+)\]$")
adae0 = pd.read_parquet(f"{A}/adae.parquet"); SOCS = sorted(adae0.AEBODSYS.dropna().unique())
def soc_of(label):                                           # the listing truncates organ class names at 40 characters
    for s_ in SOCS:
        if s_ == label or (len(label) == 40 and s_.startswith(label)): return s_
    return None
rows = []
for pg in pages:
    body = pg.split("Preferred Term", 1)[1] if "Preferred Term" in pg else pg
    for line in body.split("\n")[1:]:
        if line.strip().startswith("Note:"): break
        if not line.strip(): continue
        fields = re.split(r"\s{2,}", line.strip())
        cells = [f for f in fields[1:] if ARM.match(f) or f == "0"]
        if len(cells) < 3:                                   # wrapped label: belongs to the previous row
            if rows: rows[-1]["label"] += " " + line.strip()
            continue
        rows.append({"label": fields[0], "arms": fields[1:4], "p": fields[4:]})
soc = None
for r in rows:                                               # classify once wrapped labels are whole
    full = soc_of(r["label"])
    r["pt"] = full is None and r["label"] != "ANY BODY SYSTEM"
    if not r["pt"]: soc = full or r["label"]; r["label"] = soc
    r["soc"] = soc

adsl = pd.read_parquet(f"{A}/adsl.parquet"); adae = pd.read_parquet(f"{A}/adae.parquet")
ARMS = ["Placebo", "Xanomeline Low Dose", "Xanomeline High Dose"]
N = {a: adsl[(adsl.SAFFL == "Y") & (adsl.TRT01A == a)].USUBJID.nunique() for a in ARMS}
te = adae[adae.TRTEMFL == "Y"]
r1 = lambda x: str(Decimal(repr(float(x))).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))
def pfmt(p, rule):
    """Display rules for p-values. 'single' rounds once to 3 decimals. 'csr' is the rule that fits the
    printed CSR: values of 0.001 or more are first rounded to 4 decimals and then to 3 (double rounding)."""
    if p > 0.99: return ">0.99"
    d = Decimal(repr(float(p)))
    if rule == "csr" and p >= 0.001: d = d.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    p3 = d.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
    s_ = str(p3)
    if p3 != 0: s_ = s_.rstrip("0").rstrip(".")           # trailing zeros are dropped, except in 0.000
    return s_ + ("*" if p < 0.15 else "")
RULE = sys.argv[3] if len(sys.argv) > 3 else "csr"
tot = ok = 0; bad = []; unmatched = 0
for r in rows:
    d = te if r["label"] == "ANY BODY SYSTEM" else (te[(te.AEBODSYS == r["soc"]) & ((te.AEDECOD == r["label"]) | ((len(r["label"]) >= 38) & te.AEDECOD.str.startswith(r["label"])))] if r["pt"] else te[te.AEBODSYS == r["label"]])
    if len(d) == 0 and r["label"] != "ANY BODY SYSTEM": unmatched += 1
    n = {a: d[d.TRTA == a].USUBJID.nunique() for a in ARMS}; ev = {a: int((d.TRTA == a).sum()) for a in ARMS}
    for a, cell in zip(ARMS, r["arms"]):
        exp = "0" if n[a] == 0 else f"{n[a]} ({r1(100*n[a]/N[a])}%) [{ev[a]}]"
        tot += 1
        if re.sub(r"\s+", "", cell) == re.sub(r"\s+", "", exp): ok += 1
        else: bad.append((r["label"], a, cell, exp))
    exp_p = []
    for a in ARMS[1:]:
        if n["Placebo"] == 0 and n[a] == 0: continue
        exp_p.append(pfmt(stats.fisher_exact([[n["Placebo"], N["Placebo"] - n["Placebo"]], [n[a], N[a] - n[a]]])[1], RULE))
    for i, cell in enumerate(r["p"]):
        tot += 1
        if i < len(exp_p) and cell == exp_p[i]: ok += 1
        else: bad.append((r["label"], "p", cell, exp_p))
    if len(exp_p) != len(r["p"]): bad.append((r["label"], "p count", r["p"], exp_p))
socs = sum(1 for r in rows if not r["pt"]) - 1
print(f"CSR Table 14-5.01: rows parsed={len(rows)} (1 overall, {socs} organ classes, {sum(r['pt'] for r in rows)} preferred terms); rows with no ADAE match={unmatched}")
print(f"p-value display rule={RULE}: printed cells parsed={tot} reproduced={ok} ({100*ok/tot:.1f}%)")
for b in bad[:25]: print("  differs:", b)
# completeness the other way: terms in ADAE that the CSR table does not show
have = {(r["soc"], r["label"][:38]) for r in rows if r["pt"]}
miss = sorted({(a_, b_) for a_, b_ in map(tuple, te[["AEBODSYS", "AEDECOD"]].drop_duplicates().values) if (a_, b_[:38]) not in have})
print("TEAE terms in ADAE missing from the parsed CSR table:", len(miss), miss[:5])
