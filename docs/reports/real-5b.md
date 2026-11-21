# real-5b The mixed model, CMH and Tables 14-3.11 and 14-3.13 against the CSR: report

Date: 2026-11-19; gates and review 2026-11-20. Branch: `track/real`. Part `real-5b` of the slice
`efficacy-first` (ADR-012, approved by the owner on 2026-11-18). Depends on
real-5a (merged, `548c0f5`). Decisions: the amendment "of real-5b" at the
end of docs/decisions/ADR-015.md and the one at the end of ADR-003.md. The
owner's go-ahead came through the base session on 2026-11-19 (section "For
the base session"); its merge waited for the read track's ADR-017, which
binds a kept reader run by version where its slice does not reach. ADR-017
is carried out on `main` (`7806105`) and merged into this branch
(`2d7164c`); section "Generated kits and reader task folders".

## Verdict

The gate passed. `scripts/clean_clone_gate.sh real-5b` exited 0 on a clean
clone of commit `2d7164c` (the work with `main` `7806105` merged in) after a
fresh install and a fresh fetch: 19 of 19 checks
(`docs/reports/real-5b.clean-clone.gate.log`; section "The gate"). On clean
clones of the same commit the other gates the brief names passed, read-2a
among them, its kept dry run of arm R included (section "The gates on clean
clones"). The review is signed in its fourth pass (section "Review").

In short, what the gate shows:

- Every printed cell of Tables 14-3.11 and 14-3.13 equals the CSR at its
  printed precision, or has exactly one classified difference with a proof
  that holds: 124 cells, 93 of them printed in the CSR; 88 cells equal the
  CSR, 36 differ, each classed `rule_choice` with its proof (section "The
  classified differences").
- The hint of E22 is tested and holds: none of the 12 numbers of the model
  in 14-3.11 follows from Week 24, every one from the LS means averaged over
  weeks 8, 16 and 24. Gold follows the SAP (Week 24); the 12 cells are
  classified differences.
- The two engines agree on CMH: the three p-values, 0.2727, 0.4003 and
  0.6180 as the CSR prints them, within 9.7e-16 (rule R11).
- Every cell with a result has a complete path to SDTM columns: 15 of 15 and
  78 of 78.
- Each new method has vectors: 12 CMH cases computed in fractions, 23 of the
  mixed model from a second optimization outside R, which agrees with R to
  about 1e-8, and 7 of display.pattern.signed; options left at one value
  are planted and seen.
- P1: two builds give 56 of 56 files with the same SHA-256.
- Each new check fails on defects planted for it: D11 (27 plants, and 2
  against the decision records), D12 (4), the vectors, and the unit tests
  of the parser, the proofs, the layout and the gate's checks.

## What real-5b asks for, and where it stands

| ADR-012 asks | Where |
| --- | --- |
| The mixed model for repeated measures, R only, `mmrm`, with its covariance structure and degrees-of-freedom method as options | `standard/methods/model.mmrm.lsmeans.yaml` (11 statements), `model.mmrm.pairwise.yaml` (7); options `factors`, `covariates`, `visit`, `by_visit`, `treatment_by_visit`, `covariance` (unstructured, toeplitz), `df` (kenward_roger_linear, satterthwaite), `at` (last, average), `confidence_level`, `reference`; R in `r/specfirstr/R/models.R` (mmrm 0.3.19 with nlminb, emmeans 2.0.4) |
| CMH, Python and R, with its scores and strata; the start is the spike | `standard/methods/test.cmh.yaml` (7 statements); options `statistic` (general_association, row_mean_scores), `scores` (table, rank), `strata` (columns); `specfirst.machine.methods.cmh_p`, `m_cmh_p` in `r/specfirstr/R/methods.R`; rule I12d in both engines |
| Test vectors | `tests/methods/test_cmh.json` (12 cases, fractions), `model_mmrm_lsmeans.json` (15), `model_mmrm_pairwise.json` (8), from `tests/methods/oracle_mmrm.py`; `display_pattern_signed.json` (7) |
| Tables 14-3.11 (repeated measures) and 14-3.13 (CIBIC+, CMH controlling for site group) | `kits/cdiscpilot01/gold/events/efficacy-adas.json` (6 analyses added), `gold/events/efficacy-cibic.json` (new, 10 analyses), `gold/layout/Out14-3-11.yaml`, `Out14-3-13.yaml` |
| The cell rule of real-5a for the two tables | the gate check `efficacy` (section "The gate") |
| The two engines agree on CMH (R11) | the gate checks `results` and `CMH` |
| The hint of E22 on the LS means of 14-3.11 tested and its result recorded | the gate check `E22 hint`; section "The hint of E22"; `custom:eff-mmrm-visit` |
| The F5 edge cases of the R implementation (review of real-5a) | fixed in `models.R` for ANCOVA and, after review pass 1 (F3), for the mixed model; a vector each (section "The methods") |
| Nothing added to `catalog@1`; proposals for `catalog@2` | nothing added; section "Proposals for catalog@2" |

## The methods

### The mixed model for repeated measures

Two entries of kind `model`, R only (amendment of real-5b to ADR-015,
decisions 12 to 14). The mean of a record is

    mu + tau[group] + alpha[visit] + (tau alpha)[group, visit]
       + factors + gamma * covariates + the by_visit terms

and the records of one subject are normal with the covariance matrix of the
visits, unstructured or Toeplitz, estimated by restricted maximum
likelihood. An LS mean is taken at the last visit or averaged over the
visits; a factor is averaged over its levels with equal weights, a
covariate is at its mean over the model records.

The vectors' expected values come from `tests/methods/oracle_mmrm.py`: the
restricted likelihood maximized by Fisher scoring in numpy, in the entries
of the covariance matrix, with the adjusted covariance of Kenward and Roger
and the degrees of freedom written out from their formulas. It shares no
code with mmrm, TMB or emmeans. Three things were found on the way, each
now in the statements or the code:

- mmrm's default optimizer, L-BFGS-B, stops before the maximum. On the
  CSR's data its REML log-likelihood is -1543.9215174808 against
  -1543.9215174373 with nlminb or a tight BFGS, and the standard error of
  an LS mean moves from 0.49233568 to 0.49234173. The R implementation runs
  nlminb; then mmrm and the oracle agree to 8 digits (0.49234173 both).
- mmrm's Kenward-Roger degrees of freedom are its Satterthwaite degrees of
  freedom (on the CSR's data 179.903645 both with the default optimizer,
  179.899745 both with nlminb): W is the inverse of the observed
  information, not of the expected one Kenward and Roger (1997) write. Statement 8 says so; for one contrast Kenward and Roger's lambda
  is 1 and their degrees of freedom are 2 (l'Vl)^2 / (g'Wg).
- `Kenward-Roger-Linear` leaves out the second derivatives of the
  covariance, so its adjusted covariance does not depend on how mmrm
  parametrizes the covariance: it is that of the entries the covariance is
  linear in (statement 7), which the oracle computes.

```text
$ SPECFIRST_STRICT=1 pytest tests/methods -s -q   (gate check "method vectors", clean clone of 2d7164c)
--- python-vectors
Python implementations: 139 cases of 11 methods, 0 differences
--- r-vectors
R implementations: 134 cases of 12 methods, 0 differences
--- exact-arithmetic
expected values computed again in exact arithmetic: 134 cases, 0 differences; written by hand: 63 cases (the display rules)
...
--- model-vectors
model-based methods in R: 58 cases of 5 methods, 0 differences
planted: model.ancova.dose_response always with dose = group_rank: 7 cases differ
planted: model.ancova.lsmeans always with weights = equal: 1 cases differ
planted: model.ancova.pairwise always with df = residual: 1 cases differ
planted: model.mmrm.lsmeans always with at = last: 2 cases differ
planted: model.mmrm.pairwise always with df = kenward_roger_linear: 1 cases differ
```

### CMH

`test.cmh` follows the generalized statistic of the spike: per stratum the
counts' mean and covariance under the null hypothesis, a matrix B that picks
the comparison (every row with every column, or the mean scores of the
rows), the statistic G' W+ G with the Moore-Penrose inverse and its rank as
the degrees of freedom. Both implementations are written from the
statements; the vectors are computed in fractions, the rank and the
generalized inverse by exact elimination (`tests/methods/oracle.py`), and
the two engines agree with them within 3.5e-15.

### The edge cases of real-5a (review, F5) and of the mixed model

The mixed model had the first of them too (review of real-5b, F3): with
one group of model records it now gives that group its LS mean (the model
without the group term), with the reference alone missing comparisons,
and with fewer than two visits missing results (statement 11); a vector
each. Those of ANCOVA, each with a vector in `model_ancova_lsmeans.json` or
`model_ancova_pairwise.json`: one group with model records gives its LS
mean (the model without the group term) and the others missing, where R
stopped; group IDs with a minus sign give their comparisons, which emmeans
had labelled "(Grp-2) - (Grp-1)" so that the lookup missed them (the
contrasts are now named by position); a factor nested in the groups gives
missing LS means and differences (`nesting = NULL`), where emmeans gave a
number statements 4 and 7 call not estimable.

## The tables

Table 14-3.11 is six analyses of the event `efficacy-adas.json`: the LS
means, each dose against placebo and the high dose against the low, at
Week 24 (gold), and the same three averaged over the weeks
(`An_ADAS_MMRM_*_Avg`, reason "DATA DRIVEN"), which no row shows and the
proofs read. Their records: ADQSADAS, PARAMCD = ACTOT, weeks 8, 16 and 24,
ANL01FL = Y and no DTYPE (539 records of 234 subjects).

Table 14-3.13 is a new event, `efficacy-cibic.json`: per week the subjects
with a value (the row n), the subjects by CIBIC+ category (seven defined
groups of AVAL, every one shown) with their percent of n, and the CMH test
of row mean scores with the CIBIC+ values as scores, controlling for
SITEGR1. Its layout has an extra column, "p-value [1]", which the row n of
each week fills with the week's CMH p-value, and a groups block per week
(amendment of real-5b to ADR-003).

The CSR parser reads the shape of 14-3.13: a column without a count, the
header of the row labels ("Assessment"), and "Week 8" and "n" on one line,
read as a heading and a row; and the note of 14-3.11 as a footnote. The
three pages of real-5a parse as before:

```text
$ python parse_check.py   (a scratch script: csr.parse of real-5a's code and of real-5b's on pages 49, 51, 53)
14-3.01 same as before: True
14-3.03 same as before: True
14-3.05 same as before: True
```

## The hint of E22

Atorus reports that the LS means of Table 14-3.11 are averages over weeks
8, 16 and 24, although the title says Week 24 (PLAN.md, real-5;
evidence E22). Tested: of the 12 numbers of the model that the CSR prints,
none follows from Week 24 and every one follows from the average, with the
mixed model of the SAP (terms of SAP 10.1.1, unstructured covariance) and
Kenward-Roger standard errors. Two cells, quoted as the proofs need them:

| Cell | Ours, Week 24 (gold) | Averaged over the weeks | CSR |
| --- | --- | --- | --- |
| LS Means (SE), placebo | 2.3 (0.69) | 1.6 (0.49) | 1.6 (0.49) |
| Diff of LS Means (SE), low dose against placebo | -0.6 (1.02) | -0.0 (0.70), with the sign kept | -0.0 (0.70) |

The gold LS means are 2.3291, 1.7352 and 1.5009; averaged, 1.5535, 1.5136
and 1.1270. SAP 10.1.1 and the title of template 10 say Week 24, so gold
follows them (PLAN.md decision 17; `custom:eff-mmrm-visit`) and the 12
cells are `rule_choice` differences, each with an `other_build` proof that
reads the averaged analyses. The gate check `E22 hint` holds it:

```text
$ specfirst gate real-5b   (its check "E22 hint", on the clean clone of 2d7164c)
E22: Table 14-3.11 prints 12 numbers of the model; at Week 24 0 of them equal the CSR; averaged over weeks 8, 16 and 24, 12 cells give the CSR's text (other_build proofs that hold: 12 of 12 differing cells)
E22: the LS means of Table 14-3.11 are averages over the weeks: the hint holds
-- PASS E22 hint (2.5 s)
```

Two details of the same reproduction: with Satterthwaite's standard errors
two printed cells differ, a standard error of 0.55 where the CSR prints
0.56 and a p-value of 0.605 where it prints 0.606 (`custom:eff-mmrm-df`,
D11); with the records LOCF adds, nothing matches
(`custom:eff-mmrm-records`, D11).

## The classified differences (for N2)

| Class | Table | Cells | What | Proof |
| --- | --- | --- | --- | --- |
| `rule_choice` | 14-3.11 | 12 | the LS means and their differences at Week 24 (SAP) against their average over the weeks (CSR); 3 confidence intervals also with 1 decimal (template 10: 2) and one difference with the sign of -0.04 kept; those 4 entries name `custom:eff-mmrm-visit` and `custom:eff-mmrm-display` | `other_build`: the averaged analyses, the patterns `X.X` for the limits, the display rule `display.pattern.signed` |
| `rule_choice` | 14-3.13 | 21 | a count of 0 as "0 (0%)" (ad hoc template 1) against "0" (CSR) | `other_build`: the template `{n}` |
| `rule_choice` | 14-3.13 | 3 | the CMH p-values with 3 decimals (template) against 4 (CSR) | `other_pattern`: `X.XXXX` |

No other cell differs. The classes are the executor's proposal; the owner
reviews them at N2 (ADR-012). `gold/exceptions.yaml` holds the CSR's text of
each of these cells, as the proofs need; for 14-3.11 that is all 12 numbers
of the model (not the counts of the header).

## The decisions

Ten records added to `kits/cdiscpilot01/gold/decisions/efficacy.jsonl` (18
in all), each fitting decision-record.schema.json:

| Record | Unit | Value | Status, class | Source |
| --- | --- | --- | --- | --- |
| `custom:eff-mmrm-records` | mod-bds-visits | observed records of weeks 8, 16, 24 (ANL01FL = Y, no DTYPE) | conflict | SAP 8.1 (LOCF in general), 10.1.1 (likelihood-based), template 10 (title without LOCF) |
| `custom:eff-mmrm-terms` | tfl-efficacy-ancova | treatment, SITEGR1, week, treatment by week; BASE, BASE by week | stated, document_rule | SAP 10.1.1, 7.1, template 10 |
| `custom:eff-mmrm-covariance` | tfl-efficacy-ancova | unstructured; Toeplitz on a singularity (not met, not implemented) | stated, document_rule | SAP 10.1.1 |
| `custom:eff-mmrm-df` | tfl-efficacy-ancova | REML, Kenward-Roger with linear parameters | asked, gold_quirk | none; E22, the CSR's numbers |
| `custom:eff-mmrm-visit` | tfl-efficacy-ancova | the LS means at the last week, Week 24 | stated, document_rule | SAP 10.1.1, template 10 |
| `custom:eff-mmrm-display` | tfl-efficacy-ancova | template 10: LS mean 1, SE 2, p 3, difference 1, CI 2; no sign on a number that rounds to zero | stated, document_rule | template 10 |
| `custom:eff-cibic-records` | mod-bds-visits | weeks 8, 16, 24, ANL01FL = Y, LOCF included | stated, document_rule | SAP 10.1.2 (its LOCF sentence), ad hoc template 1 |
| `custom:eff-cibic-categories` | tfl-efficacy-categorical | all seven categories; the percent of the subjects of the week | stated, document_rule | SAP 14.1.2, ad hoc template 1 (its row N under each week; the denominator is a reading) |
| `custom:eff-cmh` | tfl-efficacy-categorical | row mean scores, table scores, strata SITEGR1 | asked, gold_quirk | SAP 16.1, ad hoc template 1, 7.1; both readings of "Pearson Chi-Square" given |
| `custom:eff-cibic-display` | tfl-efficacy-categorical | template: "xx (xx%)" also for 0, p 3 decimals | stated, document_rule | ad hoc template 1 |

The Define-XML has no analysis results metadata for these two tables; the
SAP is their only document. The gate check `decisions` holds the options
the records set (99 in all) against the two events.

## Where the documents are silent or disagree (section 4.5; for the owner)

- The records of the mixed model. SAP 8.1 imputes missing efficacy values
  by LOCF; SAP 10.1.1 calls the analysis likelihood-based; template 10's
  title has no LOCF. The CSR's numbers follow the observed records only.
- Its degrees of freedom and estimation: no document says. Atorus's notes
  name Kenward-Roger; the CSR's standard errors follow Kenward-Roger with
  linear parameters.
- The CMH statistic. SAP 16.1 says the CMH test controlling for site; the
  footnote of ad hoc template 1 adds "Pearson Chi-Square". Read as a name
  of no CMH statistic, the documents are silent, and the CSR's p-values are
  those of row mean scores with the CIBIC+ values as scores. Read as general
  association (for one stratum (n - 1)/n times Pearson's chi-square), the
  documents decide, gold would be general association (0.478, 0.770 and
  0.868) and the CSR's three p-values rule_choice differences. The record
  gives both readings (review, F5).
- "Site" in the SAP, "site group" in the CSR: SAP 7.1 pools the sites
  (SITEGR1), as in real-5a.
- Template 10 says Week 24 and the CSR averages over the weeks (section
  "The hint of E22").

## The gate

`specfirst gate real-5b`: 19 checks, those of real-5a without the grids of
the ARS example (real-3a's gate holds them) and with two more, `E22 hint`
and `CMH`; `efficacy` counts the two tables of real-5b; `planted defects`
requires D11 and D12. The gate real-5a counts its own three tables (a
table of another part is judged by the same function and counted by its
own gate).

It ran on a clean clone of `2d7164c` (a fresh clone, a fresh install of the
Python environment and the R library, a fresh fetch), under the shared lock:

```text
$ scripts/clean_clone_gate.sh real-5b /mnt/d/trial_work/specfirst/.git 2d7164c
clean clone gate real-5b
repository: /mnt/d/trial_work/specfirst/.git
commit:     2d7164c
...
1208 passed, 30 deselected in 346.89s (0:05:46)
...
P1 determinism: 56 of 56 files have the same SHA-256 in both builds
...
grid Out14-3-11: 24 cells, 15 print a number; 15 of the 15 cells with results have a complete path to SDTM columns
grid Out14-3-13: 100 cells, 78 print a number; 78 of the 78 cells with results have a complete path to SDTM columns
...
results efficacy-cibic, engines: 141 results in both, 0 disagree; largest relative difference 9.7e-16 (allowed 1e-09)
...
grid Out14-3-11 against CSR Table 14-3.11: 24 cells, 15 of them printed in the CSR; 12 equal the CSR, 12 differ, 12 of them with one class and a proof that holds
  cell:Out14-3-11/r2/c1: ours '2.3 (0.69)', CSR '1.6 (0.49)' (rule_choice)
...
  cell:Out14-3-11/r4/c2: ours '-0.6 (1.02)', CSR '-0.0 (0.70)' (rule_choice)
...
grid Out14-3-11: the R engine's rows give the same grid; the mock shell and the two pages hold; 0 problems
grid Out14-3-13 against CSR Table 14-3.13: 100 cells, 78 of them printed in the CSR; 76 equal the CSR, 24 differ, 24 of them with one class and a proof that holds
...
grid Out14-3-13: the R engine's rows give the same grid; the mock shell and the two pages hold; 0 problems
efficacy: 2 tables, 124 cells; 88 equal the CSR; classified differences: 36 rule_choice
-- PASS efficacy (2.4 s)
...
CMH: ard:An_CIBIC_W08_Cmh/Mth_Cmh_1_pval/*: Python 0.2727284040371243, R 0.27272840403712434
CMH: ard:An_CIBIC_W16_Cmh/Mth_Cmh_1_pval/*: Python 0.40031471449145817, R 0.40031471449145856
CMH: ard:An_CIBIC_W24_Cmh/Mth_Cmh_1_pval/*: Python 0.6180439310104722, R 0.6180439310104722
CMH: 3 results in both engines; largest relative difference 9.7e-16 (allowed 1e-09)
-- PASS CMH (0.0 s)
...
decisions: 18 records, 18 IDs; 99 options of analyses held against the decisions that set them; 0 problems
decisions: by class: 12 document_rule, 2 gold_quirk, 3 no class (conflict), 1 study_input; by status: 3 asked, 3 conflict, 12 stated
decisions: pass
...
PASS  environment          0.3 s
PASS  pins                 0.7 s
PASS  lint                 0.1 s
PASS  registry             0.1 s
PASS  unit tests         347.4 s
PASS  method vectors      11.2 s
PASS  kit                  0.1 s
PASS  P1 determinism      39.1 s
PASS  P2 reproduction      0.3 s
PASS  trace                1.2 s
PASS  results              3.2 s
PASS  efficacy             2.4 s
PASS  E22 hint             2.5 s
PASS  CMH                  0.0 s
PASS  decisions            0.5 s
PASS  pilot tests         49.3 s
PASS  planted defects     97.5 s
PASS  cache untouched      0.1 s
PASS  ASCII                0.0 s
GATE real-5b: PASS
```

The complete output is `docs/reports/real-5b.clean-clone.gate.log` (697
lines). The 124 cells of the two tables are 24 of 14-3.11 (3 counts in the
header, 21 in 7 rows of 3 columns, 9 of them empty as in the CSR) and 100 of
14-3.13 (4 in the header, the fourth empty; per week 8 rows of 4 columns).

## Planted defects (rule R5)

D11-efficacy-5b plants in the two reporting events, run by both engines,
in the CSR's parse and in the exceptions, and holds the decision records
against the planted events; every plant must fail the check the gate
calls. D12-cmh-engines plants in the R engine's input alone: the engines
must be seen to disagree on CMH.

```text
$ SPECFIRST_STRICT=1 pytest tests/defects -s -q   (the gate's check "planted defects" on the clean clone of 2d7164c)
...
--- D11-efficacy-5b
unchanged, efficacy-adas: 0 problems
unchanged, efficacy-cibic: 0 problems
planted, gold's analyses alone at 90% confidence: 12 problems, for example: Out14-3-11: cell:Out14-3-11/r2/c1: ours '2.3 (0.69)', CSR '1.6 (0.49)': the proof does not hold: An_ADAS_MMRM_LSM_Avg differs from An_ADAS_MMRM_LSM in more than the optio
planted, gold's analyses alone on the records LOCF adds: 12 problems, for example: Out14-3-11: cell:Out14-3-11/r2/c1: ours '2.3 (0.60)', CSR '1.6 (0.49)': the proof does not hold: An_ADAS_MMRM_LSM_Avg differs from An_ADAS_MMRM_LSM in more than the optio
planted, the mixed model with the records LOCF adds: 12 problems, for example: Out14-3-11: cell:Out14-3-11/r2/c1: ours '2.3 (0.60)', CSR '1.6 (0.49)': the proof does not hold: with the other build the cell is '1.5 (0.48)'
planted, Satterthwaite in place of Kenward-Roger: 2 problems, for example: Out14-3-11: cell:Out14-3-11/r2/c3: ours '1.5 (0.83)', CSR '1.1 (0.56)': the proof does not hold: with the other build the cell is '1.1 (0.55)'
planted, a Toeplitz covariance: 12 problems, for example: Out14-3-11: cell:Out14-3-11/r2/c1: ours '2.3 (0.60)', CSR '1.6 (0.49)': the proof does not hold: with the other build the cell is '1.6 (0.47)'
planted, no baseline by week: 5 problems, for example: Out14-3-11: cell:Out14-3-11/r2/c3: ours '1.5 (0.83)', CSR '1.1 (0.56)': the proof does not hold: with the other build the cell is '1.1 (0.55)'
planted, the site in place of the pooled site group: 10 problems, for example: Out14-3-11: cell:Out14-3-11/r2/c1: ours '2.2 (0.75)', CSR '1.6 (0.49)': the proof does not hold: with the other build the cell is '1.5 (0.58)'
planted, gold takes the LS means averaged over the weeks, as the CSR does: 8 problems, for example: Out14-3-11: cell:Out14-3-11/r2/c1: an exception for a cell that does not differ from the CSR
planted, the CMH test of general association: 3 problems, for example: Out14-3-13: cell:Out14-3-13/r10/c4: ours '0.770', CSR '0.4003': the proof does not hold: with the other patterns the cell is '0.7699'
planted, the CMH test without strata: 3 problems, for example: Out14-3-13: cell:Out14-3-13/r10/c4: ours '0.334', CSR '0.4003': the proof does not hold: with the other patterns the cell is '0.3341'
planted, the CMH test with rank scores: 3 problems, for example: Out14-3-13: cell:Out14-3-13/r10/c4: ours '0.559', CSR '0.4003': the proof does not hold: with the other patterns the cell is '0.5592'
planted, week 24 with the observed records only, without LOCF: 18 problems, for example: Out14-3-13: cell:Out14-3-13/r18/c1: ours '66', CSR '79': a difference with no class
planted, the percent of the efficacy population in place of the subjects of the week: 3 problems, for example: Out14-3-13: cell:Out14-3-13/r5/c1: ours '19 (24%)', CSR '19 ( 25%)': a difference with no class
decision records, unchanged: 0 problems
decision records, gold takes the LS means averaged over the weeks: 3 problems, for example: custom:eff-mmrm-visit: ars:An_ADAS_MMRM_LSM has at = 'average', the decision rule = 'last'
decision records, the CMH test of general association: 3 problems, for example: custom:eff-cmh: ars:An_CIBIC_W08_Cmh has statistic = 'general_association', the decision rule = 'row_mean_scores'
planted, a p-value of the CSR changed (0.2727 to 0.2737): 1 problems, for example: Out14-3-13: cell:Out14-3-13/r2/c4: ours '0.273', CSR '0.2737': the proof does not hold: the entry says the CSR prints '0.2727'; with the other patterns the cell is '0.272
planted, an other_build proof that names the analysis at Week 24 itself: 1 problems, for example: Out14-3-11: cell:Out14-3-11/r2/c1: ours '2.3 (0.69)', CSR '1.6 (0.49)': the proof does not hold: with the other build the cell is '2.3 (0.69)'; the other build...
planted, the proof of '-0.0' without the sign kept: 1 problems, for example: Out14-3-11: cell:Out14-3-11/r4/c2: ours '-0.6 (1.02)', CSR '-0.0 (0.70)': the proof does not hold: with the other build the cell is '0.0 (0.70)'
planted, a count of 0 proved by another pattern, not by the template: 1 problems, for example: Out14-3-13: cell:Out14-3-13/r3/c1: ours '0 (0%)', CSR '0': the proof does not hold: with the other patterns the cell is '0 (0%)'; the other patterns change nothing
planted, an exception of 14-3.13 left out: 1 problems, for example: Out14-3-13: cell:Out14-3-13/r2/c4: ours '0.273', CSR '0.2727': a difference with no class
planted, a proof whose template is the CSR's text: 1 problems, for example: Out14-3-11: cell:Out14-3-11/r2/c1: ours '2.3 (0.69)', CSR '1.6 (0.49)': the proof does not hold: the other template must show parts of the cell and add no text the cell's
planted, a proof whose template adds text ('{lsm} (0.49)'): 1 problems, for example: Out14-3-11: cell:Out14-3-11/r2/c1: ours '2.3 (0.69)', CSR '1.6 (0.49)': the proof does not hold: the other template must show parts of the cell and add no text the cell's
planted, an entry that names an unrelated decision (custom:eff-cmh): 1 problems, for example: Out14-3-11: cell:Out14-3-11/r2/c1: ours '2.3 (0.69)', CSR '1.6 (0.49)': the proof does not hold: custom:eff-cmh binds no analysis of the cell nor its method; An_AD...
planted, a proof whose pattern carries the CSR's text ('X.2727', other_pattern): 1 problems, for example: Out14-3-13: cell:Out14-3-13/r2/c4: ours '0.273', CSR '0.2727': the proof does not hold: the other pattern 'X.2727' of p changes more than the mask of '...
planted, a proof whose pattern carries the CSR's text ('X.2727', other_build): 1 problems, for example: Out14-3-13: cell:Out14-3-13/r2/c4: ours '0.273', CSR '0.2727': the proof does not hold: the other pattern 'X.2727' of p changes more than the mask of 'X....
planted, gold's week 8 p-value is week 16's, proved by a pattern that carries the CSR's text: 1 problems, for example: Out14-3-13: cell:Out14-3-13/r2/c4: ours '0.400', CSR '0.2727': the proof does not hold: the other pattern 'X.2727' of p changes more than ...
planted, a proof of 14-3.11 whose pattern carries the CSR's text ('X.X (0.49)'): 1 problems, for example: Out14-3-11: cell:Out14-3-11/r2/c1: ours '2.3 (0.69)', CSR '1.6 (0.49)': the proof does not hold: the other pattern 'X.X (0.49)' of lsm changes more tha...
planted, gold's week 8 p-value is week 16's, proved by a template whose format specs spell the CSR's text: 1 problems, for example: Out14-3-13: cell:Out14-3-13/r2/c4: ours '0.400', CSR '0.2727': the proof does not hold: the other template is no cell templat...
planted, a proof of 14-3.11 whose template's format specs spell the CSR's text: 1 problems, for example: Out14-3-11: cell:Out14-3-11/r2/c1: ours '2.3 (0.69)', CSR '1.6 (0.49)': the proof does not hold: the other template is no cell template: cell template '...
.
--- D12-cmh-engines
unchanged: engines: 141 results in both, 0 disagree; largest relative difference 9.7e-16 (allowed 1e-09)
R engine alone, general association: 3 CMH results disagree
R engine alone, no strata: 3 CMH results disagree
R engine alone, rank scores: 3 CMH results disagree
R engine alone, week 24 with the observed records only, without LOCF: 1 CMH results disagree
....................................................
63 passed in 97.23s (0:01:37)
-- PASS planted defects (97.5 s)
```

Satterthwaite's standard errors move 2 cells, not 12: the other 10 still
show the CSR's text at its printed precision, so the planted model is seen
only where the CSR prints a digit it changes. The last plant of D12 is no
option of the test, so the rows' stamps stay the same and the values
differ.

D9, D10 and the rest are unchanged in what they plant; D9 now plants in the
ANCOVA analyses only (their IDs start with An_ADAS_W), since the event holds
the mixed model too, and holds the records against both events.

The unit tests (`tests/unit/test_efficacy_5b.py`, without R and without the
cache) plant: a line of three labels and a text between two counts (2
cases), 16 proofs other_build that prove nothing (among them, after the
reviews, an other analysis that differs in more than its decision's
option, a template that is the CSR's text or adds to it, a template whose
format specs carry text, and a pattern that carries text of its own), a
rule_choice it does not prove and a build that
changes nothing, entries whose decisions bind no analysis of the cell or
set no option (4), extra columns and groups blocks that do not fit their
event (6) or have another form (6). `tests/unit/test_efficacy.py` plants
the same pattern of its own in the proof other_pattern (2).
`tests/unit/test_gates.py` plants three ways the hint of E22 is not shown
and three ways the engines disagree on CMH (a value moved, a row left out,
a missing value).

## Generated kits and reader task folders

The brief asks to say so when the change alters the files of a generated
kit or anything a reader's task folder holds. It does:

- The method registry has four more entries (`model.mmrm.lsmeans`,
  `model.mmrm.pairwise`, `test.cmh`, `display.pattern.signed`). The entries
  the read track's slice reaches (count.subjects, percent.subjects,
  display.pattern, the rounding rules) do not change (ADR-017; the first
  version of real-5b gave display.pattern an option, which review pass 1
  saw and the second moved to an entry of its own). No catalog entry,
  house file, schema or skill changes.
- Every generated kit pins `registry_sha256` in its kit.yaml, so every
  generated kit's kit.yaml changes; their data, gold and documents do not
  (no generated kit uses the new methods).
- Every reader task folder copies `standard/methods/registry.json`, so
  every task folder, and its task ID, changes. read-2a's kept dry run of arm
  R (`src/specfirst/harness/kept/R-task-04119188ff71`) was tied to those
  bytes; before ADR-017 the gate read-2a failed its check "arm R, kept dry
  run" on this branch (clean clone of `4028b54`). Under ADR-017 (merged in
  at `2d7164c`) the run is bound to the registry by the four entries its
  slice reaches, which keep their bytes, and the check passes on a clean
  clone of `2d7164c` (`docs/reports/real-5b.read-2a.gate.log`):

```text
$ scripts/clean_clone_gate.sh read-2a /mnt/d/trial_work/specfirst/.git 2d7164c
...
== [16/19] arm R, kept dry run: specfirst run check src/specfirst/harness/kept/R-... --kit KIT --score
kept run R-task-04119188ff71: arm R, reader claude-code, model claude-opus-5-5, used ['claude-opus-5-5'], CLI 2.1.327
  task task-04119188ff71, built again now: task-9ce7b749071b, the same on every bound part (ADR-017)
...
  a task that agrees with the task it read on every bound part, within budget, valid output files that are the run's own, canary scan clean against the canaries of the kit written now: yes
...
-- PASS arm R, kept dry run (1.7 s)
GATE read-2a: PASS
```

The owner's answer (section "For the base session"): real-5b merges after
the read track's ADR that ties a kept run to versions is approved and on
`main`, and read-2a's gate passes under it; the kept run is not made again
without the owner's word. It was not made again.

## What the checks do not cover

- The Toeplitz fallback of SAP 10.1.1 is not implemented; on the pilot the
  unstructured fit reaches its maximum, so it is not met.
- The vectors of the mixed model agree with the R implementation to about
  1e-8, the precision of two optimizations; they are held to 1e-6. On a flat
  likelihood (monotone dropout) the oracle does not converge and the two
  agree to about 1e-5 only (review, F4); the vectors keep away from such
  data.
- The values of the records that set no registry option are held by no
  check: of real-5b eff-mmrm-records, eff-cibic-records,
  eff-cibic-categories, eff-mmrm-display and eff-cibic-display (review, F5;
  decisions.py lists them). The proofs now ask that every decision an
  entry names binds an analysis of the cell or its method, that an other
  analysis differ only in the options its decisions set, that an other
  pattern change only the mask (review, G1), and that an other template be
  a cell template without format specs (review, H1).
- Which visit is the last one (`at: last`) is held by no cell: the CSR
  prints no number of that visit. `custom:eff-mmrm-terms` names AVISITN,
  whose order puts Week 24 last; with AVISIT (text) in the record and the
  analyses alike, Week 8 would be last and no check would see it (review,
  G2; ADR-015, "For the owner" item 6).
- An other analysis of a proof may differ from the cell's in the options
  its decisions set, at any value: for an option whose values are columns
  (`strata`, `factors`, `covariates`, `visit`, `by_visit`) that is any
  columns, not the other alternative of the record (review, K1). No genuine
  entry uses it (the 12 proofs of 14-3.11 differ in `at` only). The
  reviewer's search of up to 3 strata columns for the CMH p-values found
  none that gives the CSR's text (nearest 0.2728 for 0.2727), and the gate's
  check CMH counts its p-values; for 14-3.11 no such count exists. ADR-015,
  "For the owner" item 7.
- The averaged analyses of 14-3.11 are in the gold ARD (they are results of
  our event), although no row shows them.
- The CMH vectors and the pilot have full-rank and rank-deficient W, but no
  table whose columns are text with table scores (refused, statement 6).
- The header of the row labels of 14-3.13 ("Assessment") is parsed and not
  compared, like the population line (review of real-5a, F7).
- What real-5a's report lists stays: footnotes not compared, blanks not
  compared. Its third item, the proofs' decision records held for existence
  only, no longer holds: with the records at hand each must bind an
  analysis of the cell or its method.

## Proposals for `catalog@2`

Next to those of real-5a (docs/reports/real-5a.md), for the std track;
nothing is added to `catalog@1`.

1. In the family `tfl-efficacy-ancova` (real-5a's proposal), the decisions
   of a model for repeated measures: the records (observed, LOCF), the
   covariance (unstructured, Toeplitz, compound symmetry; a fallback), the
   degrees of freedom (Kenward-Roger, Satterthwaite, between-within), the
   interactions with the visit (treatment, baseline, site), and the visit of
   the LS means (the last visit, averaged over the visits).
2. A family `tfl-efficacy-categorical` (a categorical efficacy endpoint by
   visit, counts and percents, with a stratified test), owning: the
   categories shown (all, those with subjects), the denominator of a
   percent (the subjects with a value at the visit, the population), the
   test (CMH general association, row mean scores, correlation; Fisher;
   chi-square), its scores (the values, ranks, ridits) and strata, and its
   display (a count of 0 with or without its percent, the decimals of a
   p-value).
3. In `mod-bds-visits`: whether LOCF records enter an analysis, per
   analysis (real-5a proposed the imputation rule itself).

## The gates on clean clones

All nine on clean clones of `2d7164c`, the commit the fourth review pass
signed (track/real with `main` `7806105`, ADR-017 carried out, merged in),
one after another, each under the shared lock with at most 4 processors:

```text
$ for wp in real-5b read-2a real-5a real-3a real-2 gen-2a gen-3a read-1a std-1; do
    flock /run/lock/specfirst-heavy.lock taskset -c 0-3       bash scripts/clean_clone_gate.sh $wp /mnt/d/trial_work/specfirst/.git 2d7164c
  done
real-5b: 19 PASS, 0 FAIL; clean clone gate real-5b: PASS    (653 s)
read-2a: 19 PASS, 0 FAIL; clean clone gate read-2a: PASS    (1053 s)
real-5a: 18 PASS, 0 FAIL; clean clone gate real-5a: PASS    (1068 s)
real-3a: 16 PASS, 0 FAIL; clean clone gate real-3a: PASS    (1191 s)
real-2:  15 PASS, 0 FAIL; clean clone gate real-2: PASS     (641 s)
gen-2a:  13 PASS, 0 FAIL; clean clone gate gen-2a: PASS     (685 s)
gen-3a:  15 PASS, 0 FAIL; clean clone gate gen-3a: PASS     (480 s)
read-1a: 14 PASS, 0 FAIL; clean clone gate read-1a: PASS    (1033 s)
std-1:   12 PASS, 0 FAIL; clean clone gate std-1: PASS      (463 s)
```

The seconds include the waits for the lock, which other sessions held in
between. The logs of real-5b and read-2a are in docs/reports
(`real-5b.clean-clone.gate.log`, `real-5b.read-2a.gate.log`); the seven
others are not copied, and the line per gate above is counted from their
logs. read-2a passes all 19 checks, "arm R, kept dry run" among them
(section "Generated kits and reader task folders").

Before ADR-017 was merged in, the eight other gates ran on clean clones
of `4028b54` (the commit of review pass 1): seven PASS, and read-2a 18 PASS
and FAIL in "arm R, kept dry run" alone, the kept run tied to the bytes of
the registry. real-5b also passed on clean clones of `10c6bbc`, `753b5ac`
and `1b0ad01` (real-5a too on `1b0ad01`). The commits after `2d7164c` change docs/reports,
docs/decisions and docs/state only.

## For the base session

The base session's message of 2026-11-19, in its words: "The owner says
start real-5b now. Its merge waits for the read track's version-binding
ADR." The owner's answer was given in Chinese; this file stays ASCII (rule
R10), so it is quoted as "[in Chinese: both in parallel] (Recommended)",
with the option as the base session translated it: "real track starts real-5b (MMRM 14-3.11, CMH 14-3.13). After
the slice report merges, the read track drafts an ADR that binds kept reader
runs to versions instead of bytes. real-5b merges after that ADR is
settled, so there is no further ~USD 0.6 re-record."

The same message, also from the owner: the usage event stays in kept
transcripts (K3 of read-2a), and ADR-015's "For the owner" stays open and
does not block real-5b.

The base session's second message: the owner approved the read track's
ADR-017, quoted as "[in Chinese: approved, this slice only]
(Recommended)"; real-5b merges once ADR-017's implementation is on `main`;
no registry entry the slice reaches changes; a new ADR of real-5b would be
ADR-018 (none was needed).

What was done with it:

1. `track/real` was brought to `main` `548c0f5`, then to `1ef7636` (the
   read track's slice-ae-summary, ADR-016), then to `7806105` (ADR-017
   carried out), at `2d7164c`; one conflict, a line of CLAUDE.md, where
   both texts were kept.
2. real-5b is done per ADR-012, with its gates on clean clones and the
   review (sections "The gates on clean clones" and "Review").
3. ADR-017 is approved and its implementation on `main`; read-2a's gate
   passes under it on a clean clone of `2d7164c`, the kept run as it was
   (section "Generated kits and reader task folders"). The kept run was
   not made again.

## Review

By fresh-context reviewers (rule R7); `docs/reports/real-5b.review.md`
has every pass in full.

| Pass | Commit | Verdict | Blocking | Fixed in |
| --- | --- | --- | --- | --- |
| 1 | `4028b54` | NOT SIGNED | F1: other_build not held to "a build with that alternative" (gold's analyses alone, a literal template, an unrelated decision passed) | `753b5ac`, with F2 to F7 (F4 stated) |
| 2 | `753b5ac` | NOT SIGNED | G1: a pattern of a proof could carry the CSR's text around its mask | `1b0ad01`, with G2 (stated) and G3 (figures) |
| 3 | `1b0ad01` | NOT SIGNED | H1: a template of a proof could carry the CSR's text in its format specs | `f392447`, with H2 |
| 4 | `2d7164c` | SIGNED | none | K1 stated for the owner (section "What the checks do not cover"); K2, the figures of this report, in the commit after `2d7164c` |

Each blocking finding was a way to prove a wrong gold number of Table
14-3.11 or 14-3.13 with a proof that proves nothing; each fix closes its
route with plants in D11 and the unit tests, and no genuine entry changed.
Pass 4 found no route left except K1, which it searched without success
for the CMH p-values.

## For the owner

All three were answered on 2026-11-20: ADR-015, section "The owner's
answers (2026-11-20)", and docs/reports/real-5b-answers.md.

- The classes of the 36 differences (N2), and the three records the
  documents do not settle (section "Where the documents are silent or
  disagree"); ADR-015's amendment of real-5b lists them.
- Whether the last visit of the mixed model should be held by a check
  (ADR-015, "For the owner" item 6; review, G2).
- Whether an other analysis of a proof may differ in an option whose values
  are columns (ADR-015, "For the owner" item 7; review, K1).
