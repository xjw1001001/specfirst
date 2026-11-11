"""Feasibility spike: one generic interpreter for the CDISC ARS v1 example
(Common Safety Displays) on CDISC pilot ADaM. No per-table code."""
import json, sys, math, itertools
from collections import Counter, defaultdict
import numpy as np, pandas as pd
from scipy import stats

ars_path, adam_dir = sys.argv[1], sys.argv[2]
QDEF = sys.argv[3] if len(sys.argv) > 3 else "sas5"
RE = json.load(open(ars_path))
DS = {}
def data(name):
    if name not in DS:
        DS[name] = pd.read_parquet(f"{adam_dir}/{name.lower()}.parquet")
    return DS[name]

def cond_mask(df, c):
    v, cmp_, vals = c["variable"], c["comparator"], c.get("value", [])
    s = df[v]
    if cmp_ == "EQ": return s == vals[0]
    if cmp_ == "NE": return s != vals[0]
    if cmp_ == "IN": return s.isin(vals)
    if cmp_ == "NOTIN": return ~s.isin(vals)
    num = pd.to_numeric(s, errors="coerce"); x = float(vals[0])
    return {"GT": num > x, "GE": num >= x, "LT": num < x, "LE": num <= x}[cmp_]

def where_mask(df, w, dsname):
    """Mask on df for a where clause; conditions on another dataset are applied via USUBJID."""
    if w.get("condition"):
        c = w["condition"]
        if c["dataset"] == dsname: return cond_mask(df, c)
        other = data(c["dataset"]); ids = set(other.loc[cond_mask(other, c), "USUBJID"])
        return df["USUBJID"].isin(ids)
    ce = w["compoundExpression"]; ms = [where_mask(df, x, dsname) for x in ce["whereClauses"]]
    op = ce["logicalOperator"]
    if op == "AND": return np.logical_and.reduce(ms)
    if op == "OR": return np.logical_or.reduce(ms)
    if op == "NOT": return ~ms[0]
    raise ValueError(op)

BY = lambda key: {x["id"]: x for x in RE.get(key, [])}
SETS, SUBS, GRPS, METH, ANA = BY("analysisSets"), BY("dataSubsets"), BY("analysisGroupings"), BY("methods"), BY("analyses")
OPS = {o["id"]: (m, o) for m in RE["methods"] for o in m["operations"]}

def quantile(x, p):
    x = np.sort(np.asarray(x, float)); n = len(x)
    if n == 0: return np.nan
    if QDEF == "r7": return float(np.quantile(x, p))
    np_ = n * p; j = int(math.floor(np_ + 1e-12)); g = np_ - j   # SAS QNTLDEF=5
    if g < 1e-12: return float((x[j-1] + x[j]) / 2) if 0 < j < n else float(x[min(max(j-1,0), n-1)])
    return float(x[j])

def prepared(a):
    """Analysis dataset restricted to the analysis set and data subset, with grouping variables attached."""
    dsname = a["dataset"]; df = data(dsname).copy()
    if a.get("analysisSetId"): df = df[where_mask(df, SETS[a["analysisSetId"]], dsname)]
    if a.get("dataSubsetId"): df = df[where_mask(df, SUBS[a["dataSubsetId"]], dsname)]
    for og in a.get("orderedGroupings", []):
        g = GRPS[og["groupingId"]]; gv, gd = g["groupingVariable"], g.get("groupingDataset", dsname)
        if gd != dsname and gv not in df.columns:
            df = df.merge(data(gd)[["USUBJID", gv]], on="USUBJID", how="left")
    return df

def group_cells(a, df):
    """Yield (resultGroups, sub-dataframe) for every combination of result-by groupings."""
    levels = []
    for og in sorted(a.get("orderedGroupings", []), key=lambda x: x["order"]):
        if not og.get("resultsByGroup"): continue
        g = GRPS[og["groupingId"]]; gv = g["groupingVariable"]
        if g.get("dataDriven"):
            levels.append([({"groupingId": g["id"], "groupValue": v}, gv, ("EQ", [v])) for v in sorted(df[gv].dropna().unique())])
        else:
            levels.append([({"groupingId": g["id"], "groupId": x["id"]}, gv, (x["condition"]["comparator"], x["condition"]["value"])) for x in g["groups"] if x.get("condition")])
    for combo in itertools.product(*levels):
        sub = df
        for _, gv, (cmp_, vals) in combo:
            sub = sub[cond_mask(sub, {"variable": gv, "comparator": cmp_, "value": vals})]
        yield [c[0] for c in combo], sub

def key(op_id, rgs):
    return (op_id, frozenset((r["groupingId"], r.get("groupId") or r.get("groupValue")) for r in rgs))


def category(df, g):
    """Label rows by the pre-defined groups of a grouping (None when no group matches)."""
    lab = pd.Series([None]*len(df), index=df.index, dtype=object)
    for x in g.get("groups", []):
        c = x["condition"]; lab[cond_mask(df, {"variable": g["groupingVariable"], "comparator": c["comparator"], "value": c["value"]})] = x["id"]
    return lab

def pvalue(a, m, sub, var):
    nonby = [GRPS[og["groupingId"]] for og in a.get("orderedGroupings", []) if not og.get("resultsByGroup")]
    trt = nonby[0]; tv = trt["groupingVariable"]; mname = m["name"].lower()
    if "variance" in mname:
        gs = [pd.to_numeric(d[var], errors="coerce").dropna().values for _, d in sub.groupby(tv)]
        return float(stats.f_oneway(*gs).pvalue)
    if "chi-square" in mname:
        tab = pd.crosstab(sub[tv], category(sub, nonby[1]))
        return float(stats.chi2_contingency(tab, correction=False)[1])
    if "fisher" in mname:
        # subjects with the event per arm, against the analysis-set subjects of the same arms (implicit in ARS)
        adsl = data("ADSL"); pop = adsl[where_mask(adsl, SETS[a["analysisSetId"]], "ADSL")]
        arms = sorted(sub[tv].dropna().unique()) if len(sub) else []
        full = prepared(a); arms = sorted(full[tv].dropna().unique())
        if len(arms) != 2: return None
        tab = []
        for arm in arms:
            n = pop[pop[tv] == arm]["USUBJID"].nunique(); e = sub[sub[tv] == arm][var].nunique(); tab.append([e, n - e])
        return float(stats.fisher_exact(tab)[1])
    return None

COMPUTED = {}
def run(aid):
    if aid in COMPUTED: return COMPUTED[aid]
    a = ANA[aid]; m = METH[a["methodId"]]; df = prepared(a); var = a["variable"]; out = {}
    refs = {r["referencedOperationRelationshipId"]: r["analysisId"] for r in a.get("referencedAnalysisOperations", [])}
    compare_by = [GRPS[og["groupingId"]]["groupingVariable"] for og in a.get("orderedGroupings", []) if not og.get("resultsByGroup")]
    for rgs, sub in group_cells(a, df):
        for o in m["operations"]:
            name = o["name"].lower(); val = None
            if name.startswith("count of subjects"): val = sub[var].nunique()
            elif name.startswith("percent"):
                num = sub[var].nunique(); den = None
                for rel in o.get("referencedOperationRelationships", []):
                    if rel["referencedOperationRole"]["controlledTerm"] == "DENOMINATOR":
                        den_res = run(refs[rel["id"]])
                        want = dict(key("x", rgs)[1])
                        for (op2, fs), v in den_res.items():   # match on the groupings the denominator analysis has
                            if op2 == rel["operationId"] and all(want.get(g) == lv for g, lv in fs): den = v
                val = 100 * num / den if den else None
            elif name.startswith("count of non-missing"): val = int(pd.to_numeric(sub[var], errors="coerce").notna().sum())
            else:
                x = pd.to_numeric(sub[var], errors="coerce").dropna().values
                if name == "mean": val = float(np.mean(x)) if len(x) else None
                elif name.startswith("standard dev"): val = float(np.std(x, ddof=1)) if len(x) > 1 else None
                elif name == "median": val = quantile(x, .5) if len(x) else None
                elif name.startswith("first quart"): val = quantile(x, .25) if len(x) else None
                elif name.startswith("third quart"): val = quantile(x, .75) if len(x) else None
                elif name == "minimum": val = float(np.min(x)) if len(x) else None
                elif name == "maximum": val = float(np.max(x)) if len(x) else None
                elif name == "p-value":
                    val = pvalue(a, m, sub, var)
            if val is not None:
                extra = [{"groupingId": GRPS[og["groupingId"]]["id"]} for og in a.get("orderedGroupings", []) if not og.get("resultsByGroup")] if name == "p-value" else []
                out[key(o["id"], extra + rgs)] = val
    COMPUTED[aid] = out; return out

def close(raw, val):
    try: r = float(raw)
    except Exception: return False
    dec = len(raw.split(".")[1]) if "." in raw else 0
    return abs(r - val) <= 0.5 * 10 ** (-dec) + 1e-9

tot = Counter(); bymeth = defaultdict(Counter); examples = []
for a in RE["analyses"]:
    try: got = run(a["id"])
    except Exception as e:
        got = {}; examples.append((a["id"], "ERROR " + repr(e)[:120]))
    for r in a.get("results", []):
        k = key(r["operationId"], r.get("resultGroups", [])); st = "not_computed"
        if k in got: st = "match" if close(r["rawValue"], got[k]) else "differ"
        tot[st] += 1; bymeth[a["methodId"]][st] += 1
        if st != "match" and len(examples) < 40: examples.append((a["id"], r["operationId"], sorted(k[1]), r["rawValue"], got.get(k)))
print("quantile definition:", QDEF)
print("embedded results:", sum(tot.values()), dict(tot))
for mth, c in bymeth.items(): print("  ", mth, dict(c))
for e in examples[:25]: print("   !", e)
