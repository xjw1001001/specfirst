# Issue #29 A standalone recomputation script per analysis: report

Date: 2026-11-21. Branch: `track/real`. Issue #29 of `xjw1001001/specfirst`:
"[review] A generated, standalone recomputation script per analysis, so a
statistician can rerun each number without the engine". The design was
sent to the owner through the base session and accepted as sent, with the
three recommendations (ADR-021, "The owner's answers"). Decisions:
docs/decisions/ADR-021.md.

## Verdict

- `specfirst recompute cdiscpilot01` writes a standalone script for each of
  the 69 analyses of the kit's three reporting events (42 Python, 27 R),
  runs each sealed on copies of the pinned reference ADaM and compares its
  rows with the ARD at full precision: 69 of 69 `reproduced`, none `not
  covered`. The largest relative difference is 2.4e-13 (a Fisher test).
  E25's content is recomputed through CDISC's example, E24's in part; E26
  (14-6.06) is not built, and the report says so (the owner's answer to
  Q1).
- The planted break of the owner's answer to Q2, the ANCOVA LS means with
  equal weights in a copy of the R engine, changes 36 ARD rows and no
  printed cell; the scripts find exactly the three LS-means analyses. The
  quartile and CMH plants, in both engines, are found too (4 and 3
  analyses).
- "No part of the engine" is checked by the static check of each script,
  the sealed run and the generator's imports; each first failed on its
  plants, the review's among them. They are checks of form, not a proof: R
  and pyarrow's own reads are not confined at run time.
- The export holds no study data (Q3). A reviewer's run of the bundle's
  run_all.sh in a fresh folder gives the sealed run's outputs byte for byte
  and the same report.
- The gate issue-29 and the gates real-5a, real-5b, real-2 and real-3a pass
  on clean clones of `22c2932`. PLAN.md, `standard/` (the schemas,
  `catalog@1`, `open-default@1`, the method registry), `env/` and the kit
  are not changed. Nothing is for the owner.

## What the issue asks for, and where it stands

| The issue asks | Where |
| --- | --- |
| One script per analysis, R or Python, about 10 to 40 lines, from the ARS analysis and its decisions | `specfirst recompute <kit>`, `src/specfirst/recompute/` (reading, pywrite, rwrite, generate); 69 scripts, 42 Python and 27 R, of 20 to 50 lines of code besides their comments (section "The scripts") |
| The analysis set filter, the record filter, the grouping, the statistic; for a model or test, the method with its registry options | the steps of every script, in that order (ADR-021, decision 3) |
| No part of the specfirst engine; base R or Python and standard method packages | the static check, the sealed run, the generator's imports; what they hold and what they do not (section "No part of the engine") |
| Written to be read: one step per line group, the decision sentence above each step | the comments of every script (section "The scripts") |
| Run on the reference ADaM, compared with the ARD at full precision | the sealed run on copies of the pinned reference ADaM; `compare.py` (section "The comparison") |
| reproduced, differs (with the cells), not covered (with the reason) | report.json and report.txt, one line per analysis (section "The gate issue-29") |
| Exported for a reviewer's own session | `build/recompute/<kit>/bundle/`, `--export DIR`; the gate runs it again by its run_all.sh (section "The export") |
| Acceptance: the tables already reproduced (E24 to E26), a script per analysis that reproduces the ARD | 69 of 69 analyses of the kit's three reporting events; E25 recomputed through CDISC's example, E24 in part, E26 not built (ADR-021, decision 2) |
| Acceptance: a planted break in the engine, one swapped option, caught | the ANCOVA LS-means weights in the R engine; also the quartiles and the CMH statistic in both engines (section "Planted breaks") |

## The scripts

`specfirst recompute cdiscpilot01` writes one script per analysis of the
kit's three reporting events: 31 of CDISC's ARS example
(`common-safety-displays`), 28 of `efficacy-adas` (CSR 14-3.01, 14-3.03,
14-3.05, 14-3.11) and 10 of `efficacy-cibic` (CSR 14-3.13). 42 are Python
(count, percent, continuous summary, chi-square, one-way ANOVA) and 27 are
R (Fisher, CMH, ANCOVA, the mixed model). None is `not covered`. Besides
their comments they have 20 to 50 lines of code, median 30; the longest
are the two vital-signs summaries, whose three defined groupings take a
line per group. Writing, checking and running all 69 takes about 15 s.

The script of the age summary of CDISC's example, as generated (no
decision record binds an element of CDISC's example, so its comments name
the ARS elements and the registry statements):

```python
# Recomputation of An03_01_Age_Summ_ByTrt (Summary of Age by Treatment), reporting event
#   common-safety-displays of the kit cdiscpilot01.
# Written by `specfirst recompute` from the ARS analysis, its decision records and the method
#   registry (issue #29, ADR-021). It calls no part of specfirst.
# Run: python An03_01_Age_Summ_ByTrt.py <folder of the reference ADaM as Parquet> <output CSV>
# Packages: pandas 3.1.1, numpy 2.5.4 (env/requirements.lock).
# Output: one row per result: operation_id; per grouping (AnlsGrouping_01_Trt) the group ID, '='
#   and the value of a data-driven group, or '*' for a compared grouping; the value at full
#   precision, empty when missing.
import sys
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd

adam, out = Path(sys.argv[1]), sys.argv[2]
adsl = pd.read_parquet(adam / "adsl.parquet")


def num(value):
    return "" if value is None or value != value else repr(float(value))


# Analysis set AnalysisSet_02_SAF (Safety Population): ADSL.SAFFL EQ Y
records = adsl[adsl["SAFFL"].fillna("").isin(["Y"])]
# Grouping AnlsGrouping_01_Trt (Treatment): defined groups by ADSL.TRT01A (rule I8)
g1 = {
    "AnlsGrouping_01_Trt_1": records["TRT01A"].fillna("").isin(["Placebo"]),
    "AnlsGrouping_01_Trt_2": records["TRT01A"].fillna("").isin(["Xanomeline Low Dose"]),
    "AnlsGrouping_01_Trt_3": records["TRT01A"].fillna("").isin(["Xanomeline High Dose"]),
}

# summary.continuous, statements 1 to 6 and 10; the quantiles by statement 7,
#   quantile_definition sas5 (kit.yaml's binding): numpy's method averaged_inverted_cdf
rows = []
for k0, m0 in g1.items():
    key, cell = (k0,), records[m0]
    x = np.sort(cell["AGE"].dropna().to_numpy(dtype=float))
    n = len(x)
    rows.append(("Mth02_ContVar_Summ_ByGrp_1_n", *key, num(n)))
    rows.append(("Mth02_ContVar_Summ_ByGrp_2_Mean", *key, num(x.mean() if n else None)))
    rows.append(("Mth02_ContVar_Summ_ByGrp_3_SD", *key, num(None if n < 2 else (0.0 if x[0] == x[-1] else x.std(ddof=1)))))
    rows.append(("Mth02_ContVar_Summ_ByGrp_4_Median", *key, num(np.quantile(x, 0.5, method="averaged_inverted_cdf") if n else None)))
    rows.append(("Mth02_ContVar_Summ_ByGrp_5_Q1", *key, num(np.quantile(x, 0.25, method="averaged_inverted_cdf") if n else None)))
    rows.append(("Mth02_ContVar_Summ_ByGrp_6_Q3", *key, num(np.quantile(x, 0.75, method="averaged_inverted_cdf") if n else None)))
    rows.append(("Mth02_ContVar_Summ_ByGrp_7_Min", *key, num(x[0] if n else None)))
    rows.append(("Mth02_ContVar_Summ_ByGrp_8_Max", *key, num(x[-1] if n else None)))

pd.DataFrame(rows, columns=["operation_id", "group1", "value"], dtype=object).to_csv(out, index=False)
```

The script of the Week 24 LS means of CSR 14-3.01, with the decision
records that bind its elements above the steps they bind:

```r
# Recomputation of An_ADAS_W24_LSM (ADAS-Cog (11), change to Week 24: LS means), reporting event
#   efficacy-adas of the kit cdiscpilot01.
# Written by `specfirst recompute` from the ARS analysis, its decision records and the method
#   registry (issue #29, ADR-021). It calls no part of specfirst.
# Run: Rscript An_ADAS_W24_LSM.R <folder of the CSV copies of the reference ADaM> <output CSV>
# Packages: R 4.6.2, emmeans 2.0.4 (env/r-packages.lock).
# Output: one row per result: operation_id; per grouping (AnlsGrouping_TRT01P) the group ID, '='
#   and the value of a data-driven group, or '*' for a compared grouping; the value at full
#   precision, empty when missing.
args <- commandArgs(trailingOnly = TRUE)
adam <- args[1]
adqsadas <- utils::read.csv(file.path(adam, "adqsadas.csv"), colClasses = "character", na.strings = "")
adqsadas$BASE <- as.numeric(adqsadas$BASE)
adqsadas$CHG <- as.numeric(adqsadas$CHG)
adsl <- utils::read.csv(file.path(adam, "adsl.csv"), colClasses = "character", na.strings = "")
adsl$TRT01PN <- as.numeric(adsl$TRT01PN)
num <- function(v) ifelse(is.na(v), "", sprintf("%.17g", v))

# custom:eff-analysis-set (stated): The efficacy tables analyze the efficacy population, the
#   subjects with ADSL.EFFFL = Y, each in the column of the planned treatment ADSL.TRT01PN (0,
#   54, 81).
# Analysis set AnalysisSet_EFF (Efficacy population): ADSL.EFFFL EQ Y
records <- adqsadas[adqsadas$USUBJID %in% adsl$USUBJID[adsl$EFFFL %in% c("Y")], ]
# custom:eff-visit-record (stated): The value of a subject at a week is the ADQSADAS record of
#   the parameter ACTOT with that AVISIT and ANL01FL = Y: the assessment of the window that is
#   closest to its target day, or, when the window has none, the last one carried forward (DTYPE
#   = LOCF).
# Data subset DS_ADAS_W24 (ADAS-Cog (11) total score at Week 24, LOCF): ADQSADAS.PARAMCD EQ
#   ACTOT AND ADQSADAS.AVISIT EQ Week 24 AND ADQSADAS.ANL01FL EQ Y
records <- records[(records$PARAMCD %in% c("ACTOT")) & (records$AVISIT %in% c("Week 24")) & (records$ANL01FL %in% c("Y")), ]
# model.ancova.lsmeans, statement 1: the model records belong to a group and have a value of
#   CHG, SITEGR1, BASE
# Grouping AnlsGrouping_TRT01P (Planned treatment): defined groups by ADSL.TRT01PN (rule I8);
#   decision custom:eff-analysis-set
member <- cbind(
  "Grp_Pbo" = records$USUBJID %in% adsl$USUBJID[adsl$TRT01PN %in% c(0)],
  "Grp_Low" = records$USUBJID %in% adsl$USUBJID[adsl$TRT01PN %in% c(54)],
  "Grp_High" = records$USUBJID %in% adsl$USUBJID[adsl$TRT01PN %in% c(81)]
)
stopifnot(all(rowSums(member) <= 1))  # rule I17: a record in two groups
records$TRT <- factor(apply(member, 1, function(m) colnames(member)[m][1]), levels = colnames(member))
d <- records[stats::complete.cases(records[c("TRT", "CHG", "SITEGR1", "BASE")]), ]

# custom:eff-model-terms (stated): The ANCOVA of the change from baseline has the treatment and
#   the pooled site group (SITEGR1) as factors and the baseline value (BASE) as a covariate,
#   with no interaction, in the test of dose response and in the pairwise comparisons alike.
# custom:eff-lsmeans-weights (stated): LS means average over the pooled site groups with weights
#   proportional to their numbers of model records (the observed margins).
stopifnot(length(unique(d$SITEGR1)) > 1)  # statement 2: a factor of one level would be left out
# Statements 2 and 3: y = mu + tau[group] + the factors + the covariates, no interaction, by
#   ordinary least squares
fit <- stats::lm(CHG ~ TRT + SITEGR1 + BASE, data = d)
# Statement 4: weights proportional (the analysis's programmingCode); covariates at their mean
#   over the model records; no factor is nested
emm <- emmeans::emmeans(fit, ~ TRT, weights = "proportional", nesting = NULL)
# df residual (the registry's default), confidence level 95 (the registry's default)
s <- as.data.frame(summary(emm, infer = c(TRUE, FALSE), level = 95 / 100))
group <- as.character(s$TRT)
rows <- rbind(
  data.frame(operation_id = "Mth_AncovaLsm_1_lsm", group1 = group, value = num(s[["emmean"]])),
  data.frame(operation_id = "Mth_AncovaLsm_2_se", group1 = group, value = num(s[["SE"]])),
  data.frame(operation_id = "Mth_AncovaLsm_3_lcl", group1 = group, value = num(s[["lower.CL"]])),
  data.frame(operation_id = "Mth_AncovaLsm_4_ucl", group1 = group, value = num(s[["upper.CL"]]))
)

utils::write.csv(rows, args[2], row.names = FALSE)
```

## No part of the engine

Three checks, each of which first fails on planted defects (rule R5;
ADR-021, decision 5):

- The static check (`specfirst.recompute.static`), on the syntax tree of a
  Python script and on the tokens of R's own parser. Python: the imports
  exactly the templates' statements, builtins and attributes in
  allow-lists, no dunder, no class, no match, try or type parameter, no
  store into an attribute, none of the names the templates use bound but in
  their own lines, `sys` read only as `sys.argv[1]` or `sys.argv[2]`. R:
  calls in an allow-list, nothing that runs other code, no string called,
  apply and sapply with a function written in place, the model functions
  with a formula written in place, update with `df = ...` only, no
  qualified function or file.path as a value. Each call of the one reader
  of a language has one form, a dataset of the plan in the data folder,
  and the one write is that of the script's output. No text holds a path,
  "..", a backslash, another file's name or a number; every number is one
  the ARS states for the analysis or one of a few constants.
- The sealed run: each script in a fresh folder outside every checkout, on
  copies of the reference ADaM checked against kit.yaml, with an
  environment of PATH, HOME, the locale and the R library. Python runs
  through seal.py, whose audit hook (PEP 578) refuses every import of
  specfirst or yamaa and every open by Python in the checkout and the
  build; R runs as `Rscript --vanilla`.
- The generator imports of specfirst only `specfirst.recompute`, `kit`,
  `paths` and `machine.canonical`, which load no module of the engine; its
  standalone files (seal.py, bundle/) import nothing of specfirst.

What they do not hold (ADR-021, decision 5): they check the form of a
script and the routes they name, and they are no proof. The sealed run
confines no read by R or by a library's own C code (pyarrow's reader);
there only the static check's form of a read stands. A number built from
the allowed constants passes. The review planted routes past the first two
versions of the checks (pass 1: 13 plants past the static check, and four
planted scripts past the static check, the sealed run and the comparison;
pass 2: seven more routes, N1, N2, N2c, M3 and RN1 to RN3, and the
writes); each is a plant now and is refused (RC5 below;
tests/unit/test_recompute.py). The 69 scripts are generated and short, so
that they can be read.

The plants of RC5 on the generated scripts, from the gate's log:

```text
planted in An03_01_Age_Summ_ByTrt: an import of the engine: ["line 11: the import `import specfirst`, which is not one of the templates'"]
planted in An03_01_Age_Summ_ByTrt: the ARD read: ['line 18: a read other than `adam / "<dataset>.parquet"` of a dataset of the plan']
planted in An03_01_Age_Summ_ByTrt: the built ADaM by a path: ['line 18: a read other than `adam / "<dataset>.parquet"` of a dataset of the plan']
planted in An03_01_Age_Summ_ByTrt: a number of the ARD: ['line 40: the number 1.4885404260186454, which the ARS does not state for the analysis']
planted in An03_01_Age_Summ_ByTrt: a number of the ARD in a text: ["line 40: the number '1.4885404260186454' in a text, which the ARS does not state for the analysis"]
planted in An03_01_Age_Summ_ByTrt: the built ADaM by parent folders: ['line 18: a read other than `adam / "<dataset>.parquet"` of a dataset of the plan']
planted in An03_01_Age_Summ_ByTrt: the root of the data folder: ['line 18: the attribute anchor']
planted in An03_01_Age_Summ_ByTrt: exec by __builtins__: ['line 18: the name __builtins__']
planted in An03_01_Age_Summ_ByTrt: a separator from chr: ['line 18: the name chr']
planted in An03_01_Age_Summ_ByTrt: memmap: ['line 18: the attribute memmap']
planted in An03_01_Age_Summ_ByTrt: pandas.eval: ['line 18: the attribute eval']
planted in An03_01_Age_Summ_ByTrt: the ARD's name in two parts: ['line 18: the data folder used otherwise than in a read of a dataset of the plan']
planted in An03_01_Age_Summ_ByTrt: N1, the arguments rewritten before the binding: ['line 18: sys used otherwise than as `sys.argv[1]` or `sys.argv[2]`, read']
planted in An03_01_Age_Summ_ByTrt: N2, Path bound again: ['line 17: the name Path of the template bound again']
planted in An03_01_Age_Summ_ByTrt: N2c, Path imported under another name and defined: ["line 12: the import `from pathlib import Path as Q`, which is not one of the templates'"]
planted in An03_01_Age_Summ_ByTrt: a write elsewhere: ['line 50: a write other than `.to_csv(out, index=False)`']
planted in An03_01_Age_Summ_ByTrt: M3, sys bound by a capture of match to a function with an argv: ['line 22: a Match statement or clause']
planted in An_ADAS_W24_LSM: a source of the engine: ["a path in the text 'r/specfirstr/R/models.R'"]
planted in An_ADAS_W24_LSM: a library: ['the call library']
planted in An_ADAS_W24_LSM: a number of the ARD: ['the number 1.4885404260186454, which the ARS does not state for the analysis']
planted in An_ADAS_W24_LSM: source handed to sapply as a string: ['the function of sapply is not written in place: `function(...)`']
planted in An_ADAS_W24_LSM: a call of a string: ['the call of the string "source"']
planted in An_ADAS_W24_LSM: a number of the ARD in a text: ["the number '1.4885404260186454' in a text, which the ARS does not state for the analysis"]
planted in An_ADAS_W24_LSM: the ARD from the root: ['a file other than `file.path(adam, "<dataset>.csv")` of a dataset of the plan']
planted in An_ADAS_W24_LSM: a reader as a value: ['the function utils::read.csv used as a value']
planted in An_ADAS_W24_LSM: RN1, a function name built for sapply: ['the function of sapply is not written in place: `function(...)`']
planted in An_ADAS_W24_LSM: RN2, a function name held for sapply: ['the function of sapply is not written in place: `function(...)`']
planted in An_ADAS_W24_LSM: RN3, a reader name built for sapply: ['the function of sapply is not written in place: `function(...)`']
planted in An_ADAS_W24_LSM: a write elsewhere: ['a write other than that of the output, `write.csv(rows, args[2], ...)`']
planted in An03_01_Age_Summ_ByTrt: the sealed run, an import of the engine: ImportError: refused by the sealed run: specfirst
planted in An03_01_Age_Summ_ByTrt: the sealed run, an import past the hook of meta_path: ImportError: refused by the sealed run: specfirst.machine.methods
planted in An03_01_Age_Summ_ByTrt: the sealed run, an open of the ARD: PermissionError: refused by the sealed run: an open of /tmp/specfirst-clean-g1agKZ/specfirst/build/p1/cdiscpilot01/first/gold/ard/common-safety-displays.jsonl
not held by the sealed run: a read by pyarrow's own code, and R; there only the static check's form of a read stands, as far as a check of the form holds (ADR-021, decision 5)
```

## The comparison

`compare.py` (standard library only, in the bundle) needs the rows of a
script to be the rows of the gold ARD; a count exactly, any other value
within a relative 1e-9 (an absolute 1e-12 where the ARD's value is 0), the
mixed model within 1e-6. Nothing is `reproduced` by default: an analysis
without ARD rows, ARD rows of more groupings than the plan reads, two ARD
rows of one key, and a script that fails (it leaves no output, but
`<analysis>.failed`) are `differs`. The pilot's ARD has 858 values of 0
and no other value below 1e-9 in magnitude (the review, pass 2).

RC6 plants a swapped option in a script, a lost row, an extra row, a value
off by a relative 1e-8, a script that fails after it wrote its output, and
an analysis without ARD rows:

```text
planted in the scripts' outputs: common-safety-displays/An03_01_Age_Summ_ByTrt, common-safety-displays/An03_06_Height_Summ_ByTrt, efficacy-adas/An_ADAS_W24_LSM, efficacy-adas/An_ADAS_W24_PwPbo, efficacy-adas/An_EFF_N, efficacy-cibic/An_CIBIC_EFF_N differ
```

## Planted breaks

The owner's answer to Q2: in a copy of the R engine, the ANCOVA LS means
with equal weights where the analysis states proportional; the ARS, the
decisions and the registry unchanged. Also, in both engines so that rule
R11 is silent, quartiles by R type 7 where the analysis states SAS
definition 5, and the CMH statistic: general association where the
analysis states row mean scores. That last one is the "CMH scores" plant
of the design the owner accepted; the statistic is swapped, not the
`scores` option. From the gate's log:

```text
planted: the ANCOVA LS means with equal weights where the analysis states proportional: 36 ARD rows change, 0 of them shown by a cell of a built grid; the scripts: 3 analyses differ: efficacy-adas/An_ADAS_W08_LSM, efficacy-adas/An_ADAS_W16_LSM, efficacy-adas/An_ADAS_W24_LSM
planted: quartiles by R type 7 in both engines: 106 ARD rows change, the engines disagree on 0; the scripts: 4 analyses differ: common-safety-displays/An03_01_Age_Summ_ByTrt, common-safety-displays/An03_06_Height_Summ_ByTrt, common-safety-displays/An08_01_Obs_Summ_ByTrt, common-safety-displays/An08_02_ChgBl_Summ_ByTrt
planted: CMH general association in both engines: 3 ARD rows change, the engines disagree on 0; the scripts: 3 analyses differ: efficacy-cibic/An_CIBIC_W08_Cmh, efficacy-cibic/An_CIBIC_W16_Cmh, efficacy-cibic/An_CIBIC_W24_Cmh
```

No printed cell of the CSR tables shows an LS mean, so the 36 changed ARD
rows of the first plant pass every check of the build (P2 compares the
printed cells); the scripts catch exactly the three LS-means analyses.

## The export

The bundle holds no study data (the owner's answer to Q3): README.txt
names the source and its pinned commit, and manifest.json the SHA-256 of
each reference file. The gate generates the bundle again, compares the
bytes, and runs the bundle's own run_all.sh in a fresh copy, as a
reviewer would:

```text
export: the bundle generated again has the same bytes: True
export: sh run_all.sh in a fresh copy of the bundle exited 0 in 36 s; its last line: E26 CSR 14-6.06 (Hy's law shifts, CMH): not built: no ARS analysis in the kit (real-5); its method, test.cmh, is recomputed for CSR 14-3.13
export: 69 of 69 outputs of the reviewer's run have the bytes of the sealed run's
export: the reviewer's report equals the sealed run's: True
```

## The gate issue-29

`specfirst gate issue-29` on a clean clone of `22c2932`, with a fresh
install and a fresh fetch, under the heavy lock on four processors. The
log is committed in full as docs/reports/issue-29.clean-clone.gate.log.

```text
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 bash scripts/clean_clone_gate.sh issue-29 <repository> 22c2932
PASS  environment          0.4 s
PASS  pins                 0.8 s
PASS  lint                 0.0 s
PASS  unit tests         487.0 s
PASS  kit                  0.1 s
PASS  P1 determinism      49.2 s
PASS  recompute           13.5 s
PASS  independence         0.0 s
PASS  export              36.0 s
PASS  planted break       19.1 s
PASS  cache untouched      0.1 s
PASS  ASCII                0.0 s
GATE issue-29: PASS
clean clone gate issue-29: PASS (clone: /tmp/specfirst-clean-g1agKZ/specfirst)
```

The unit tests: 1317 passed, 36 deselected. The check recompute prints
one line per analysis, 69 `reproduced`, and then:

```text
cdiscpilot01: 69 analyses: reproduced 69
E24 CSR 14-2.01 (demographics): not built as a CSR table (real-4); covered in part: its rows of age, age group, sex, race and height are recomputed by the demographics analyses of CDISC's example (Out14-1-1), on the safety population and race by another grouping; its ITT population and its rows of MMSE, duration of disease, education, weight and BMI are not
E25 CSR 14-5.01 (adverse events by organ class and term): not built as a CSR table (real-4); its content is recomputed by the analyses of CDISC's example Out14-3-2-1, on ADAE (AESOC, equal to AEBODSYS on every record)
E26 CSR 14-6.06 (Hy's law shifts, CMH): not built: no ARS analysis in the kit (real-5); its method, test.cmh, is recomputed for CSR 14-3.13
static check: 69 of 69 scripts pass it (imports, calls, reads, texts and numbers; ADR-021, decision 5)
```

The check independence:

```text
static check: 69 of 69 scripts (42 Python, 27 R) import, name and call only what the allow-lists hold, call their reader only in the one form of a read of a dataset of their plan, and state only the ARS's numbers
generator: src/specfirst/recompute imports 0 modules of the engine; its standalone files (seal.py, bundle/) import nothing of specfirst
sealed runs: 69 of 69 scripts ran in a fresh folder outside the checkout, on copies of the reference ADaM, the Python ones through seal.py, whose audit hook refuses specfirst, yamaa and every open of a file in the checkout or the build
```

## The gates on clean clones

`scripts/clean_clone_gate.sh` for issue-29 and for the gates of the track
that hold the pilot kit, real-5a, real-5b, real-2 and real-3a, on commit
`22c2932`: one gate at a time, each under the heavy lock and on four
processors; each clone gets a fresh install and a fresh fetch. The
commits after `22c2932` change documents only (this report, the review,
the logs, the state file). Each log is committed in full.

```text
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 bash scripts/clean_clone_gate.sh <gate> <repository> 22c2932
issue-29 exit 0 after 743 s
real-5a exit 0 after 1231 s
real-5b exit 0 after 924 s
real-2 exit 0 after 899 s
real-3a exit 0 after 945 s
```

| Gate | Checks | Unit tests | Last lines | Log |
| --- | --- | --- | --- | --- |
| issue-29 | 12 PASS, 0 FAIL | 1317 passed, 36 deselected | `GATE issue-29: PASS`, `clean clone gate issue-29: PASS` | docs/reports/issue-29.clean-clone.gate.log |
| real-5a | 18 PASS, 0 FAIL | 1317 passed, 36 deselected | `GATE real-5a: PASS`, `clean clone gate real-5a: PASS` | docs/reports/issue-29.real-5a.gate.log |
| real-5b | 19 PASS, 0 FAIL | 1317 passed, 36 deselected | `GATE real-5b: PASS`, `clean clone gate real-5b: PASS` | docs/reports/issue-29.real-5b.gate.log |
| real-2 | 15 PASS, 0 FAIL | 1317 passed, 36 deselected | `GATE real-2: PASS`, `clean clone gate real-2: PASS` | docs/reports/issue-29.real-2.gate.log |
| real-3a | 16 PASS, 0 FAIL | 1317 passed, 36 deselected | `GATE real-3a: PASS`, `clean clone gate real-3a: PASS` | docs/reports/issue-29.real-3a.gate.log |

The gate issue-29 passed on a clean clone of `694709b` too (12 of 12,
1170 s). The runs on `b43c336`, `0e06dd4` and `ae07c86` were stopped
when the review found a further route; only the runs on `22c2932` count.

## The review

A fresh-context reviewer (rule R7) signs docs/reports/issue-29.review.md.

- Pass 1, of `694709b` (the code): no finding blocked. F1: the checks of
  "no part of the engine" held only the direct routes, and the words
  claimed more; F2: an analysis with no ARD rows was `reproduced`; F3: a
  script that failed after its output was `reproduced` in the report; F4:
  the absolute 1e-12 held at every size; F5: E24 was "covered", but only in
  part, and the E24 to E26 lines were printed only. All five were fixed in
  `b43c336`.
- Pass 2, of `b43c336`: F2 to F5 closed; F1 narrowed, with five new
  deliberate routes past the checks (N1, N2, RN1 to RN3) and four sentences
  that still claimed more than the checks hold. Fixed in `0e06dd4`. At
  `0e06dd4` one more (N2c: `Path` imported under another name and a `Path`
  of the script's own) and the writes, which were not pinned; fixed in
  `ae07c86`. At `ae07c86` one more (M3: `sys` bound by a capture of
  `match` to a function given an `argv`); fixed in `22c2932`, with the
  other forms that bind a name without an assignment (`except ... as`, a
  type parameter) and every store into an attribute. `22c2932` is the
  commit the gates above ran on.
- Pass 2, part 2, of this report and the five gate logs: its verdict
  stands in docs/reports/issue-29.review.md.

## What is not done

- E24 (CSR 14-2.01) is recomputed in part: its ITT population and its rows
  of MMSE, duration of disease, education, weight and BMI have no ARS
  analysis in the kit (real-4). E26 (CSR 14-6.06) is not built (real-5).
  The report and README.txt say so in a line each.
- The checks of "no part of the engine" are checks of form, not a proof,
  and R is not confined at run time (section "No part of the engine").
- A new registry method needs a template in `specfirst.recompute` before
  its analyses are covered; until then they are `not covered`, with the
  reason (docs/state/real.md).
