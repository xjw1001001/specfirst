# real-5a ANCOVA and Tables 14-3.01, 14-3.03 and 14-3.05 against the CSR: report

Date: 2026-11-19. Branch: `track/real`. Part `real-5a` of the slice
`efficacy-first` (ADR-012, approved by the owner on 2026-11-18). Depends on
real-2 and real-3a (passed). Decisions: docs/decisions/ADR-015.md and the
amendment "of real-5a" at the end of docs/decisions/ADR-003.md.

## Verdict

The gate passed. `scripts/clean_clone_gate.sh real-5a` exited 0 on a clean
clone of commit `29b15ca` (this work with `main` `1a94134` merged in), after
a fresh install and a fresh fetch: 18 of 18 checks
(`docs/reports/real-5a.clean-clone.gate.log`; section "The gate").

On clean clones of the same commit the gates real-2, real-3a, gen-2a,
gen-3a, read-1a and std-1 passed; read-2a passed every check but "arm R,
kept dry run", which cannot pass after a change of the method registry
(section "The gates on clean clones"). At the owner's answer (section "For
the base session") the dry run of arm R was made again and kept in place of
the old one (USD 0.58; section "The dry run of arm R, made again"), and all
eight gates run again on clean clones of the commit that holds it (at the
time of writing; section "The gates on clean clones").

In short, what the gate shows (section "The gate"):

- Every printed cell of the three tables equals the CSR at its printed
  precision, or has exactly one classified difference with a proof that
  holds: 153 cells (51 per table), 120 of them printed in the CSR; 144
  equal the CSR, 9 differ, each classed `rule_choice` with the proof
  `other_pattern`. The 9 are the limits of the 95% confidence intervals:
  SAP template 5 shows them with 2 decimals, gold follows the SAP (PLAN.md
  decision 17), the CSR prints 1 decimal.
- Every number the CSR prints is reproduced from the public ADQSADAS and
  ADSL by the model the SAP describes. The dose-response p-values are
  0.2447, 0.4967 and 0.4115 (printed 0.245, 0.497, 0.412).
- Every cell with a result has a complete path to SDTM columns: 40 of 40
  per table, through 73 ARD rows, 7 analyses and 25 ADaM columns to 18
  SDTM columns.
- Each new method has vectors: 10, 9 and 11 cases, their expected values
  computed in exact fractions outside R; the R implementation gives them to
  a relative 1e-12, and three planted defects are seen (an option fixed at
  one value, as an implementation that ignored it would compute).
- P1: two builds in two processes give 45 of 45 files with the same
  SHA-256.
- Each new check fails on defects planted for it: D9-efficacy (13 plants),
  D10-trace-model, `model-vectors`, and the unit tests of the CSR parser,
  the comparison, the layout and the decision records.

What the change alters outside the pilot (section "Generated kits and
reader task folders"): the three registry entries change the registry, so
every generated kit's kit.yaml and every reader's task folder changes, and
read-2a's kept dry run of arm R, tied to those bytes, had to be made again.
No catalog entry, house file, schema or skill changes.

## What real-5a asks for, and where it stands

| ADR-012 asks | Where |
| --- | --- |
| Registry entries, R only: ANCOVA with LS means, pairwise comparisons, the dose-response test; numbered semantics; options for model terms, LS-means weights, the contrast or model of the dose-response test, degrees of freedom | `standard/methods/model.ancova.lsmeans.yaml` (8 statements), `model.ancova.pairwise.yaml` (7), `model.ancova.dose_response.yaml` (6); options `factors`, `covariates`, `weights`, `df`, `confidence_level`, `reference`, `dose`, `model`; R in `r/specfirstr/R/models.R` (stats::lm, emmeans 2.0.4, car 3.1-5) |
| Test vectors from an independent computation | `tests/methods/model_ancova_*.json`: 10, 9 and 11 cases; expected values from `tests/methods/oracle_models.py`; test `model-vectors` |
| The reference grids, parsed from the CSR pages with poppler, outside the cache, parsed again by the gate | `specfirst.machine.csr`; written to `build/csr/cdiscpilot01/<table>.json` (ignored); the CSR is a pinned file of the kit (Pilot 6, `gold/reference/csr/CSR.pdf`, the SHA-256 base-0 recorded) |
| ARS analyses and layouts from the SAP and the CSR shell, built from the reference ADQSADAS and ADSL | `kits/cdiscpilot01/gold/events/efficacy-adas.json` (22 analyses, 3 outputs), `gold/layout/Out14-3-01.yaml`, `Out14-3-03.yaml`, `Out14-3-05.yaml` |
| The layout kinds, as an amendment to ADR-003; of F1 to F9 only those the tables meet | block kind `statistics` with `columns`; section headings on the pages; none of F1 to F9 is met as a defect (the amendment says why for each) |
| Decision records, custom, each citing the SAP or the CSR | `kits/cdiscpilot01/gold/decisions/efficacy.jsonl`: 8 records (section "The decisions") |
| Nothing added to `catalog@1`; proposals for `catalog@2` | nothing added; section "Proposals for catalog@2" |
| Atorus's programs and notes as hints | not used: every detail is read in the SAP and the Define-XML and held against the CSR's numbers |
| Gate `real-5a` | `src/specfirst/gates.py`, 18 checks (section "The gate") |

## The methods

Three entries of a new kind `model`, R only (ADR-015, decisions 1 to 5):

| Entry | Results | Options |
| --- | --- | --- |
| `model.ancova.lsmeans` | lsmean, se, lower_cl, upper_cl, per group | factors, covariates, weights (equal, proportional), df (residual, asymptotic), confidence_level (90, 95, 99) |
| `model.ancova.pairwise` | estimate, se, lower_cl, upper_cl, p_value, per group against the reference | factors, covariates, reference (a group), df, confidence_level |
| `model.ancova.dose_response` | p_value, estimate, per analysis | factors, covariates, dose (grouping_value, group_rank), model (continuous_dose, linear_contrast), df |

The model is `y = mu + tau[group] + factors + gamma * covariates + error`
by ordinary least squares, no interaction. An analysis states its terms in
`programmingCode` (context `specfirst method registry`): parameters
`factors` and `covariates` (any number of columns) and `reference`. The ARS
reader gives those columns the role `model` (`ars.reads`), so they are
handed to R, have `reads` edges and are part of every cell's trace. Rules
I16 to I19 in standard/methods/README.md say how a model-based analysis is
run. The Python engine gives no row for it; the gold ARD takes the R
engine's rows (`build.gold_rows`), and the result check asks that the gold
ARD holds them as R gave them and that each is stamped with the registry's
hash of its options.

The vectors: `tests/methods/oracle_models.py` solves the normal equations
in exact fractions, builds the LS means and contrasts from their
coefficient vectors as the statements write them, and takes the t
distribution from its closed form for whole degrees of freedom (Abramowitz
and Stegun 26.7.3 and 26.7.4) in 60-digit decimals, a quantile by
bisection. It shares nothing with lm, emmeans or car. ADR-012 says "a
second R route, or published values"; an exact computation outside R is a
stronger independence, and the CSR checks the methods again on real data.
The vectors give every option every value, and `model-vectors` runs them
again with one option of each entry fixed at one value in the inputs, what
an implementation that ignored the option would compute (the defect is
planted in the inputs, not in the R code: review, F6; the reviewer's own
plants in the R code were seen):

```text
$ SPECFIRST_STRICT=1 pytest tests/methods -s -q   (gate check "method vectors")
--- model-vectors
model-based methods in R: 30 cases of 3 methods, 0 differences
planted: model.ancova.dose_response always with dose = group_rank: 7 cases differ
planted: model.ancova.lsmeans always with weights = equal: 1 cases differ
planted: model.ancova.pairwise always with df = residual: 1 cases differ
```

## The tables

`kits/cdiscpilot01/gold/events/efficacy-adas.json`, our own reporting
event: per week (24, 8, 16) a data subset (ADQSADAS.PARAMCD = ACTOT,
AVISIT = the week, ANL01FL = Y), summaries of BASE, AVAL and CHG
(`summary.continuous`), the dose-response test, the comparisons of each
dose with placebo and of the high with the low dose, and the LS means
(proportional weights; the tables print none). The analysis set is
ADSL.EFFFL = Y; the columns are the planned treatment ADSL.TRT01PN with
defined groups 0, 54 and 81. The masks of the ARS operations carry the
decimals of SAP template 5 without its padding; the layouts take them.

How a CSR table becomes a reference grid (`specfirst.machine.csr`): the
page is turned into text by `pdftotext -layout -f <page> -l <page>`
(poppler 24.02, as evidence E24 and E25), the counts line `(N=..)` gives
the centre of each column, every text that stands apart by two blanks or
more goes to the nearest column, a line without cells is a section heading,
lines from `[1]` on are footnotes. The grid of the build is compared line
by line: column labels, titles, the counts under the column labels, every
heading and row label (without blanks: page 49 prints
"p-value(Xan High - Xan Low)[1][3]" without the blank that pages 51 and 53
have) and every cell (without blanks). The footnotes are not compared: the
layouts state the methods in words of their own.

The 9 cells that differ, the only CSR cells this report quotes besides the
three dose-response p-values above:

| Cell | Ours (SAP template 5: 2 decimals) | CSR |
| --- | --- | --- |
| `cell:Out14-3-01/r14/c2` | (-2.08;1.15) | (-2.1;1.1) |
| `cell:Out14-3-01/r14/c3` | (-2.66;0.65) | (-2.7;0.7) |
| `cell:Out14-3-01/r17/c3` | (-2.19;1.11) | (-2.2;1.1) |
| `cell:Out14-3-03/r14/c2` | (-0.20;2.36) | (-0.2;2.4) |
| `cell:Out14-3-03/r14/c3` | (-1.10;1.53) | (-1.1;1.5) |
| `cell:Out14-3-03/r17/c3` | (-2.17;0.44) | (-2.2;0.4) |
| `cell:Out14-3-05/r14/c2` | (-1.78;1.24) | (-1.8;1.2) |
| `cell:Out14-3-05/r14/c3` | (-2.23;0.88) | (-2.2;0.9) |
| `cell:Out14-3-05/r17/c3` | (-1.95;1.14) | (-1.9;1.1) |

Each has one entry in the `cells` section of
`kits/cdiscpilot01/gold/exceptions.yaml`: class `rule_choice`, decision
`custom:eff-display-decimals`, proof `other_pattern` with the patterns
`X.X` for both limits. `csr.judge` shows the cell's own results with those
patterns and asks that the text is the CSR's and that ours is another. The
limit -1.949 of the last row shows that the CSR rounds the limit, not our
2-decimal text (-1.95 would give -2.0).

## The classified differences (for N2)

| Class | Cells | What | Proof |
| --- | --- | --- | --- |
| `rule_choice` | 9 | the limits of the 95% CI of a difference of LS means: 2 decimals by SAP template 5, 1 in the CSR | `other_pattern`: our results with 1 decimal are the CSR's text |

No other cell differs. Nothing is classed `reference_error` or
`data_difference`. The classes are the executor's proposal; the owner
reviews them at N2 (ADR-012).

## The decisions

Eight records, `kits/cdiscpilot01/gold/decisions/efficacy.jsonl`, each
fitting decision-record.schema.json. They are custom by their ID
(`custom:eff-*`, PLAN.md sections 4.3 and 10). The brief asked for "status
custom"; the schema's statuses are `stated`, `default`, `asked`,
`conflict` and `not_applicable` (ADR-015, decision 10). Five are `stated`;
two are `conflict`, where the documents disagree and section 4.5 asks a
person, each citing both sides and keeping the value the build uses; one
is `asked`. The first version had all eight `stated`; the review (finding
F2) showed that three of them claimed more than their sources. The gate
check `decisions` holds them against the reporting event: every bound
element exists, and the 45 options the model terms, the dose-response
test, the pairwise inference and the weights set in the analyses they bind
are the decisions' values.

| Record | Unit | Value | Status, class | Source |
| --- | --- | --- | --- | --- |
| `custom:eff-analysis-set` | tfl-efficacy-ancova | ADSL.EFFFL = Y; columns by ADSL.TRT01PN | stated, document_rule | SAP 6; Define-XML, Table_14-3.01.R.2 |
| `custom:eff-visit-record` | mod-bds-visits | the ADQSADAS record of the week with ANL01FL = Y (windowed; LOCF where the window is empty) | stated, document_rule | SAP 8.1, 8.2; Define-XML |
| `custom:eff-model-terms` | tfl-efficacy-ancova | factors treatment and SITEGR1, covariate BASE, no interaction | conflict | SAP 10.1.1, 7.1, 15.1 and Define-XML R.2 keep BASE; Define-XML R.1 (the dose-response test) leaves it out |
| `custom:eff-dose-response` | tfl-efficacy-ancova | the planned dose (0, 54, 81) as a continuous variable; the test of its coefficient | stated, document_rule | SAP 3.3, 10.1.1; Define-XML R.1 |
| `custom:eff-pairwise` | tfl-efficacy-ancova | each dose against placebo, the high dose against the low; residual df; 95%; not adjusted; shown always | conflict | SAP 10.1.1 and 7.3 (only if the dose response is significant) against template 5 (shown); Define-XML R.2 |
| `custom:eff-lsmeans-weights` | tfl-efficacy-ancova | proportional (observed margins) | stated, document_rule | Define-XML R.2 (`OM`) |
| `custom:eff-baseline-rows` | tfl-efficacy-ancova | the Baseline rows summarize BASE on the week's records | asked, study_input | none |
| `custom:eff-display-decimals` | tfl-efficacy-ancova | the decimals of SAP template 5; CI limits 2 | stated, document_rule | SAP template 5 |

What the data cannot show (printed by D9, not counted as caught): the LS
means' weights change the 36 LS means and no printed cell, because the
tables print differences of LS means only; and the two readings of the
Baseline rows give the same cells, because every subject of the efficacy
population has a baseline record and a record in every week.

## Where the documents disagree (section 4.5; for the owner)

- The Define-XML's code of the dose-response test,
  `model CHG = trtpn sitegr1;`, leaves the baseline out; its text says
  "using randomized dose ... and site group in model". The SAP (3.3,
  10.1.1) and the CSR's footnote [1] keep the baseline. The CSR's numbers
  follow the SAP: without the baseline the p-values are 0.2532, 0.4761 and
  0.4004. Gold follows the SAP; D9 plants the Define-XML's model and sees
  19 problems.
- The Define-XML's selection names PARAMCD "ATOT"; its parameter list and
  the data have "ACTOT".
- SAP 7.3 performs the pairwise comparisons only if the dose response is
  significant; template 5 and the CSR show them anyway (none of the three
  is significant). Gold shows them, as the template does.
- SAP 10.1.1 says "site"; SAP 7.1, the Define-XML and the CSR say the
  pooled site group. Gold uses SITEGR1; D9 plants SITEID and sees 26
  problems.

The records `custom:eff-model-terms` and `custom:eff-pairwise` are
`conflict` for the first and the third point: each cites both sides and
keeps the value under which the CSR's numbers are reproduced, until the
owner decides; an answer turns them into `stated` records that cite it.
A status is a record's: `conflict` covers the whole record, although the
documents disagree on a part of each (the covariate of the dose-response
test; when the comparisons are shown) (review, G4).

## The gate

`specfirst gate real-5a`: 18 checks, the 16 of real-3a and two more
(`efficacy`, `decisions`); `method vectors` and `planted defects` require
the tests of real-5a (`model-vectors`, `D9-efficacy`, `D10-trace-model`).

It ran on a clean clone of `29b15ca` (a fresh clone, a fresh install of the
Python environment and the R library, a fresh fetch), under the shared lock:

```text
$ scripts/clean_clone_gate.sh real-5a /mnt/d/trial_work/specfirst/.git 29b15ca
clean clone gate real-5a
repository: /mnt/d/trial_work/specfirst/.git
commit:     29b15ca
...
1158 passed, 25 deselected in 325.54s (0:05:25)
...
model-based methods in R: 30 cases of 3 methods, 0 differences
planted: model.ancova.dose_response always with dose = group_rank: 7 cases differ
planted: model.ancova.lsmeans always with weights = equal: 1 cases differ
planted: model.ancova.pairwise always with df = residual: 1 cases differ
...
P1 determinism: 45 of 45 files have the same SHA-256 in both builds
...
results efficacy-adas: 102 results of model-based methods (R only, section 7.3): the gold ARD holds them as the R engine gave them, each stamped with the registry's hash of its options
results efficacy-adas, engines: 165 results in both, 0 disagree; largest relative difference 2.1e-16 (allowed 1e-09)
...
grid Out14-3-01 against CSR Table 14-3.01: 51 cells, 40 of them printed in the CSR; 48 equal the CSR, 3 differ, 3 of them with one class and a proof that holds
  cell:Out14-3-01/r14/c2: ours '(-2.08;1.15)', CSR '(-2.1;1.1)' (rule_choice)
  cell:Out14-3-01/r14/c3: ours '(-2.66;0.65)', CSR '(-2.7;0.7)' (rule_choice)
  cell:Out14-3-01/r17/c3: ours '(-2.19;1.11)', CSR '(-2.2;1.1)' (rule_choice)
grid Out14-3-01: the R engine's rows give the same grid; the mock shell and the two pages hold; 0 problems
grid Out14-3-03 against CSR Table 14-3.03: 51 cells, 40 of them printed in the CSR; 48 equal the CSR, 3 differ, 3 of them with one class and a proof that holds
  cell:Out14-3-03/r14/c2: ours '(-0.20;2.36)', CSR '(-0.2;2.4)' (rule_choice)
  cell:Out14-3-03/r14/c3: ours '(-1.10;1.53)', CSR '(-1.1;1.5)' (rule_choice)
  cell:Out14-3-03/r17/c3: ours '(-2.17;0.44)', CSR '(-2.2;0.4)' (rule_choice)
grid Out14-3-03: the R engine's rows give the same grid; the mock shell and the two pages hold; 0 problems
grid Out14-3-05 against CSR Table 14-3.05: 51 cells, 40 of them printed in the CSR; 48 equal the CSR, 3 differ, 3 of them with one class and a proof that holds
  cell:Out14-3-05/r14/c2: ours '(-1.78;1.24)', CSR '(-1.8;1.2)' (rule_choice)
  cell:Out14-3-05/r14/c3: ours '(-2.23;0.88)', CSR '(-2.2;0.9)' (rule_choice)
  cell:Out14-3-05/r17/c3: ours '(-1.95;1.14)', CSR '(-1.9;1.1)' (rule_choice)
grid Out14-3-05: the R engine's rows give the same grid; the mock shell and the two pages hold; 0 problems
grids: 4 outputs, pass
efficacy: 3 tables, 153 cells; 144 equal the CSR; classified differences: 9 rule_choice
-- PASS efficacy (2.3 s)

...
decisions: 8 records, 8 IDs; 45 options of analyses held against the decisions that set them; 0 problems
decisions: by class: 5 document_rule, 2 no class (conflict), 1 study_input; by status: 1 asked, 2 conflict, 5 stated
decisions: pass
...
PASS  environment          0.4 s
PASS  pins                 0.8 s
PASS  lint                 0.0 s
PASS  registry             0.0 s
PASS  unit tests         326.0 s
PASS  method vectors       5.9 s
PASS  kit                  0.1 s
PASS  P1 determinism      38.3 s
PASS  P2 reproduction      0.3 s
PASS  trace                1.1 s
PASS  results              3.2 s
PASS  grids                2.3 s
PASS  efficacy             2.3 s
PASS  decisions            0.4 s
PASS  pilot tests         51.9 s
PASS  planted defects     76.0 s
PASS  cache untouched      0.1 s
PASS  ASCII                0.0 s
GATE real-5a: PASS
```

The complete output is `docs/reports/real-5a.clean-clone.gate.log`
(589 lines). The trace check walks the efficacy grids like the
example's (`grid Out14-3-0x: 51 cells, 40 print a number; 40 of the 40 cells
with results have a complete path to SDTM columns`). P1 builds the whole
kit twice in two processes; the 45 files include the ARD of both result
sets, the gold ARS, the grids, their shells and pages, and the graph.

Two earlier runs of the gate failed in `planted defects`, both in the test
D8 of real-3a, which assumed the example's grid to be the only grid of the
build: on a clone of `553375a` (D8 walked the `computes` edges of the
efficacy rows, which are not in the example's ARD: a KeyError) and on a
clean clone of `cd066ad` (D8 gave `graph.check_cells` the example's grid
alone, and coverage.json lists four grids). Each was fixed in the test
(`cd066ad`, `b8bb1f5`); every other check passed in both runs.

## Planted defects (rule R5)

D9-efficacy plants in our reporting event, run by both engines, and in the
reference and the exceptions; every plant must fail the check the gate
calls (`build.csr_against`), and the decision records are held against the
event planted without the baseline:

```text
$ SPECFIRST_STRICT=1 pytest tests/defects -s -q
  (the gate's check "planted defects" on the clean clone of 29b15ca; its log)
...
--- D9-efficacy
unchanged: 0 problems
planted, the ANCOVA without the baseline covariate: 19 problems, for example: Out14-3-01: cell:Out14-3-01/r11/c3: ours '0.253', CSR '0.245': a difference with no class
planted, the dose as the rank of the group: 3 problems, for example: Out14-3-01: cell:Out14-3-01/r11/c3: ours '0.232', CSR '0.245': a difference with no class
planted, the site in place of the pooled site group: 26 problems, for example: Out14-3-01: cell:Out14-3-01/r11/c3: ours '0.283', CSR '0.245': a difference with no class
planted, the comparisons with asymptotic degrees of freedom: 8 problems, for example: Out14-3-01: cell:Out14-3-01/r12/c2: ours '0.568', CSR '0.569': a difference with no class
planted, the comparison with placebo made against the low dose: 3 problems, for example: Out14-3-01: the grid cannot be built: 5 results of the layout are not in the ARD, for example ard:An_ADAS_W24_PwPbo/Mth_AncovaPw_1_diff/Grp_Low
planted, the intent-to-treat set in place of the efficacy set: 109 problems, for example: Out14-3-01: cell:Out14-3-01/r1/c1: ours '(N=86)', CSR '(N=79)': a difference with no class
planted, week 16 in place of week 24: 22 problems, for example: Out14-3-01: cell:Out14-3-01/r10/c1: ours '2.0 (-17;23)', CSR '2.0 (-11;16)': a difference with no class
decision records, unchanged: 0 problems
decision records, the ANCOVA without the baseline covariate: 9 problems, for example: custom:eff-model-terms: ars:An_ADAS_W24_Dose has covariates = [], the decision covariates = ['BASE']
what the CSR cannot show: the LS means with equal weights change 36 results of the LS means and 0 cells (the tables print no LS mean)
planted, a cell of the CSR changed (0.245 to 0.254): 1 problems, for example: Out14-3-01: cell:Out14-3-01/r11/c3: ours '0.245', CSR '0.254': a difference with no class
planted, the confidence limits shown with the CSR's 1 decimal (the 9 exceptions are stale): 9 problems, for example: Out14-3-01: cell:Out14-3-01/r14/c2: an exception for a cell that does not differ from the CSR
planted, an exception whose other pattern proves nothing (3 decimals): 1 problems, for example: Out14-3-01: cell:Out14-3-01/r14/c2: ours '(-2.08;1.15)', CSR '(-2.1;1.1)': the proof does not hold: with the other patterns the cell is '(-2.079;1.145)'
planted, an exception left out: 1 problems, for example: Out14-3-01: cell:Out14-3-01/r14/c2: ours '(-2.08;1.15)', CSR '(-2.1;1.1)': a difference with no class
planted, an exception with the class reference_error: 1 problems, for example: Out14-3-01: cell:Out14-3-01/r14/c2: ours '(-2.08;1.15)', CSR '(-2.1;1.1)': the proof does not hold: other_pattern proves a rule_choice
planted, an exception that names no decision record: 1 problems, for example: Out14-3-01: cell:Out14-3-01/r14/c2: ours '(-2.08;1.15)', CSR '(-2.1;1.1)': the proof does not hold: no decision record custom:none
```

D10-trace-model holds the `reads` edges of the 9 analyses that fit a model
against the R engine: with the columns they have no edge to emptied or
rolled no result may change; with the columns they read emptied one must;
the edges to ADQSADAS.BASE, the covariate, are then left out:

```text
--- D10-trace-model
  unchanged: the 1 columns without a reads edge emptied: 0 of 66 results change
  unchanged: the 1 columns without a reads edge rolled: 0 of 66 results change
  planted: the 2 columns without a reads edge emptied: 66 of 66 results change
  planted: the 2 columns without a reads edge rolled: 0 of 66 results change
planted, the reads edges to ADQSADAS.BASE left out (12 edges): 1 problems, for example: with the 2 columns they have no reads edge to emptied, 66 results change, for example ard:An_ADAS_W08_Dose/Mth_AncovaDose_1_pval/*
....................................................
61 passed in 75.72s (0:01:15)
-- PASS planted defects (76.0 s)
```

Rolling BASE by one row changes nothing (the rows above a record are the
same subject's other visits, with the same baseline); emptying it changes
all 66 results, and that is what is seen. D8 now walks the four grids of
the build and the ARD rows of the ARS example only (two fixes found by the
gate runs: commits `cd066ad` and `b8bb1f5`).

The unit tests (`tests/unit/test_efficacy.py`, without R and without the
cache) plant: a page that is not such a table (4 cases), a grid of another
shape (6), a difference with no class and six proofs that do not hold, a
statistics block that does not fit its event (5) or has another form (7),
invalid entries of a model-based method (5), options that are not columns
or a group, and decision records that do not fit their event (6).

## One cell, end to end

`cell:Out14-3-01/r11/c3`, the dose-response p-value of Table 14-3.01,
walked from the graph files of the build:

```text
$ python walk.py build/p1/cdiscpilot01/first/gold/graph 'cell:Out14-3-01/r11/c3'
  (a scratch script that follows shows, computes, reads and derives_from edges;
   on the first build of P1 of the clone of 553375a)
cell cell:Out14-3-01/r11/c3: text '0.245'
  shows ard:An_ADAS_W24_Dose/Mth_AncovaDose_1_pval/*  (gold/ard/efficacy-adas.jsonl, line 231)
    computes <- ars:An_ADAS_W24_Dose  (gold/events/efficacy-adas.json, line 642)
      reads adam:ADQSADAS.ANL01FL: 25 columns upstream, SDTM sdtm:DM.ACTARM, sdtm:DM.STUDYID, sdtm:DM.USUBJID, sdtm:EX.EXSTDTC, sdtm:EX.STUDYID, sdtm:EX.USUBJID, sdtm:QS.QSDTC, sdtm:QS.QSSEQ, sdtm:QS.QSTESTCD, sdtm:QS.STUDYID, sdtm:QS.USUBJID
      reads adam:ADQSADAS.AVISIT: 22 columns upstream, SDTM (the same 11)
      reads adam:ADQSADAS.BASE: 30 columns upstream, SDTM the same and sdtm:QS.QSBLFL, sdtm:QS.QSSTRESN
      reads adam:ADQSADAS.CHG: 31 columns upstream, SDTM the same and sdtm:QS.QSBLFL, sdtm:QS.QSSTRESN
      reads adam:ADQSADAS.PARAMCD: 22 columns upstream, SDTM (the same 11)
      reads adam:ADQSADAS.SITEGR1: 25 columns upstream, SDTM the same and sdtm:DM.SITEID
      reads adam:ADQSADAS.USUBJID: 22 columns upstream, SDTM (the same 11)
      reads adam:ADSL.EFFFL: 17 columns upstream, SDTM sdtm:DM.ACTARM, sdtm:DM.ARMCD, sdtm:DM.STUDYID, sdtm:DM.USUBJID, sdtm:EX.EXSTDTC, sdtm:EX.STUDYID, sdtm:EX.USUBJID, sdtm:QS.QSCAT, sdtm:QS.QSSEQ, sdtm:QS.STUDYID, sdtm:QS.USUBJID, sdtm:QS.VISITNUM
      reads adam:ADSL.TRT01PN: 2 columns upstream, SDTM sdtm:DM.ACTARM, sdtm:DM.ARM
      reads adam:ADSL.USUBJID: 2 columns upstream, SDTM sdtm:DM.ACTARM, sdtm:DM.USUBJID
$ (the ARD row)
{"analysis_id": "An_ADAS_W24_Dose", "group1_groupingId": "AnlsGrouping_TRT01P", "id": "ard:An_ADAS_W24_Dose/Mth_AncovaDose_1_pval/*", "method_id": "model.ancova.dose_response", "method_options_hash": "832102289f1953be31fbeb8e69f9686987d7598127e83e0a30db956ad7b3e52d", "operation_id": "Mth_AncovaDose_1_pval", "raw_value": 0.24470567386849953}
```

## Generated kits and reader task folders

The brief asks to say so when the change alters the files of a generated
kit or anything a reader's task folder holds. It does:

- The method registry (`standard/methods/*.yaml` and `registry.json`) has
  three more entries. No catalog entry, house file, schema or skill
  changes.
- Every generated kit pins `registry_sha256` in its kit.yaml
  (`specfirst.gen.kits`), so every generated kit's kit.yaml changes. The
  data, gold and documents of a generated kit do not depend on the
  registry's new entries (no generated kit uses a model-based method).
- Every reader task folder copies `standard/methods/registry.json`
  (`specfirst.harness.task`), so every task folder, and its task ID,
  changes.
- The gate read-2a holds its kept dry run of arm R
  (`src/specfirst/harness/kept/R-task-50024a8d7ca2/`) against the task and
  the kit.yaml written again now. On a clean clone of `29b15ca`, every
  check of read-2a passed but that one
  (`docs/reports/real-5a.read-2a.gate.log`):

```text
$ scripts/clean_clone_gate.sh read-2a /mnt/d/trial_work/specfirst/.git 29b15ca
...
== [16/19] arm R, kept dry run: specfirst run check src/specfirst/harness/kept/R-... --kit KIT --score
kept run R-task-50024a8d7ca2: arm R, reader claude-code, model claude-opus-5-5, used ['claude-opus-5-5'], CLI 2.1.327
  task task-50024a8d7ca2, built again now: task-04119188ff71
  ...
  task: built again, 1 files differ from the task the run read, for example standard/methods/registry.json
  kit: kit.yaml is not the one the run read
  the task it read, within budget, valid output files, canary scan clean against the canaries of the kit written now: NO
...
PASS  arm R, stub reader     10.5 s
FAIL  arm R, kept dry run      2.4 s
PASS  scratch removed      0.0 s
...
GATE read-2a: FAIL   (the other 18 checks: PASS)
```

Nothing else differs: the task differs in that one file. The kept run is
tied to the bytes of the registry by design (ADR-010, decision 9); any
change of the registry makes it fail. The owner answered (section "For the
base session"): the run is made again before the merge, below.

## The dry run of arm R, made again

At the owner's answer. Kit 4 of the gate seed was written again as the gate
writes it (`specfirst.harness.gate._kit`: `genkits.generate_apart(root,
gate.SEED, folder, split_of(4), number=4, hash_seed="1", zone=None)`), from
the worktree at `6bad961` (the code of `29b15ca`), outside the checkout:

```text
kit sfrrl2uh split train generator gen-3a.2
seed given matches the kit: True and the gate's seed: True
  (kit.yaml: registry_sha256: e5f47480c46d..., the SHA-256 of
   standard/methods/registry.json with the three entries of real-5a)
```

Then read-2a's command, budget and canary scan, once, with the Claude Code
CLI the owner logged in, the task and run folders on a Windows drive
outside every checkout (ADR-010, decision 1), under the shared lock:

```text
$ specfirst run arm <kit-004> --arm R --seed gen-2a/kit-4 --keep
run R-task-04119188ff71: arm R, stage C, condition notes, kit sfrrl2uh (train), task task-04119188ff71 (22 decisions)
  reader: claude-code, model claude-opus-5-5, used ['claude-opus-5-5'], CLI 2.1.327
  cost: 23 turns, 73.8 s wall, 60.4 s API, tokens in 24 out 7585 cache write 44168 cache read 375403, USD 0.5802 (CLI: 0.5802206)
  budget: {'turns': 100, 'seconds': 2700, 'usd': 10.0}: within
  outputs: decisions.jsonl 22 lines, questions.jsonl 2 lines, unmapped.jsonl 0 lines
  asks: 2, answered 2; pop.efficacy.rule (mod-populations); ae.related.values (mod-ae-emergence)
  output files: valid
  task folder: holds only what a reader may see
  canary scan: 29347 canaries from 81 files; clean
  permission denials: 2
  RUN R-task-04119188ff71: PASS
kept in <checkout>/src/specfirst/harness/kept/R-task-04119188ff71
```

It passed the first time; no second run was made. Its task,
`task-04119188ff71`, is the one the gate read-2a builds now (the line
"built again now: task-04119188ff71" of the failing runs above). The two
denials are Bash commands other than `bin/check` (a listing of the task
and `cat` of its files); the reader then read the files with its file
tools, as the old run did after its one denial. The old kept run
`R-task-50024a8d7ca2` is deleted; the new one is in its place.

| Run | Model | Turns | Wall | API | Input | Output | Cache write | Cache read | USD (computed) | USD (CLI) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| arm R, kept dry run of read-2a (deleted) | claude-opus-5-5 | 20 | 71.3 s | 55.5 s | 22 | 7,084 | 43,185 | 317,644 | 0.5508 | 0.5508 |
| arm R, kept dry run of real-5a | claude-opus-5-5 | 23 | 73.8 s | 60.4 s | 24 | 7,585 | 44,168 | 375,403 | 0.5802 | 0.5802 |

Model use of real-5a: USD 0.58, computed from the tokens at the prices of
ADR-010, decision 7, on the owner's subscription; the CLI's own figure is
the same to the fourth decimal. The kept files hold no local path (the
home folder is `<home>`, the checkout `<checkout>`, as `runs.keep` writes
them), no account name and no key (`api_key_source: none`); they are ASCII.

The kept run checked again, as the gate does:

```text
$ specfirst run check src/specfirst/harness/kept/R-task-04119188ff71 --kit <kit-004> --tasks <scratch> --seed gen-2a/kit-4 --score
kept run R-task-04119188ff71: PASS
case sfrrl2uh, arm R, stage C
...
  asks: 2 given, 2 in gold (decisions with the status asked), 2 of them right; precision 1.00, recall 1.00
...
  decisions a reviewer would have to change: 0
...
  visible: cells correct: 15 of 15 gold cells (an output that was not produced counts as wrong)
...
  twin: cells correct: 15 of 15 gold cells (an output that was not produced counts as wrong)
...
case sfrrl2uh, arm R: every score is 100%
```

The scores are report only (they decide nothing in a gate); the old run
had 21 of 22 values right. One run of a model says nothing about a
difference between the two.

What stays as it was: the isolation probe kept beside it
(`src/specfirst/harness/kept/probe-task-50024a8d7ca2/`) is of the old task.
The gate does not check it (read-2a's review, H12), and the owner asked
for the dry run of arm R only.

A kept run is tied to the bytes of the method registry, the catalog and
the generator: the task folder copies `standard/methods/registry.json` and
the catalog, and the kit's kit.yaml pins `registry_sha256` and the
generator. Any change of them makes the check "arm R, kept dry run" fail
until the run is made again. The owner's direction is that the read track
tie a kept run to their versions instead; it is an Open item of
docs/state/read.md.

## What the checks do not cover

- The footnotes of the CSR are not compared (ours are in our own words;
  the CSR's are not copied into git), and neither is the indentation of a
  row label (pdftotext places labels a column or two apart).
- Cells and labels are compared without their blanks. A difference made of
  blanks alone is not seen; a number cannot be one.
- The LS means are built and stamped but printed by no table; the vectors
  hold them, the CSR does not.
- The weights of the LS means and the source of the Baseline rows are not
  separable on these data (section "The decisions").
- The proof `other_pattern` holds a cell's text against the CSR's; it does
  not rebuild the grid with the decision's other value.
- The CSR's parse rests on its layout: a page of another shape (a table
  over two pages, a column without a count line) is refused, not read.
- The CSR's page header "Population: Efficacy" is parsed and not compared
  (review, F7); the analysis set is held by the counts under the column
  labels, which are compared.
- An exception's proof asks that its decision is a record of the kit, not
  that the record is about the cell (review, F3: all 9 entries naming
  `custom:eff-analysis-set` pass).
- The check `decisions` holds the values of the four records that set an
  option of the registry; the other four, among them
  `custom:eff-display-decimals`, are held against nothing there (review,
  F4). Nothing else holds the decimals record either: the proofs of the 9
  exceptions ask only that the decision they name exists (review, G3); a
  record saying 1 decimal passes every check. The decimals themselves are
  in the ARS operations' masks, which the CSR comparison does hold.
- Three edge cases of the R implementation that no vector covers and the
  pilot does not meet (review, F5): with only one group of records the
  LS means stop with an error instead of a missing result; group IDs
  containing "-" make emmeans label the contrasts so that the lookup
  misses them (missing results, no error); a factor nested in the groups
  gives an LS mean where statement 7 says missing. They are open for
  real-5b, with a vector each.

## Proposals for `catalog@2`

What the three tables needed and `catalog@1` does not have. For the std
track, next to issue #23; nothing is added to `catalog@1`.

1. A table family `tfl-efficacy-ancova` (an efficacy endpoint at a week,
   change from baseline, by ANCOVA), owning:
   - `tfl.eff.population`: efficacy population, intent-to-treat,
     completers (CSR Table 14-3.07 uses completers);
   - `tfl.eff.model.terms`: factors (site, pooled site group, none),
     covariates (baseline value, none), a treatment-by-site interaction (no,
     yes);
   - `tfl.eff.dose_response`: none, the dose as a continuous variable, a
     linear contrast; the dose scores (the planned doses, the ranks);
   - `tfl.eff.pairwise`: which pairs (each dose against placebo, all
     pairs), the adjustment, the confidence level, the degrees of freedom,
     and whether they are shown only when the dose response is significant
     (SAP 7.3 against template 5);
   - `tfl.eff.lsmeans.weights`: equal, proportional;
   - `tfl.eff.baseline.rows`: BASE on the week's records, the baseline
     visit;
   - its display: the decimals of each statistic, the limits of a
     confidence interval among them (the difference of this part).
2. In `mod-bds-visits`: `bds.imputation.rule` (LOCF on the targeted
   assessments of the windows, observed cases, none), next to the window
   entries that exist (`bds.window.table`, `bds.window.tiebreak`), and the
   retrieval visits (SAP 8.2: visit 201 counts for the week 24 window).
3. In `mod-populations` or `mod-demographics`: `pop.site.pooling` (SAP 7.1:
   sites with fewer than 3 subjects in a group are pooled; SITEGR1 of
   ADSL).
4. For the compile templates of the family: the three `model.ancova.*`
   entries and their parameters are what a compiled ARS file would name
   (`Method registry: <id>`; `factors`, `covariates`, `reference`,
   `weights`, `dose`, `model`).

## The gates on clean clones

All eight on clean clones of `29b15ca` (track/real with `main` `1a94134`,
the std track's issues #26, #24 and #25, merged in), one after another,
each under the shared lock with at most 4 processors:

```text
$ for wp in real-5a real-2 real-3a gen-2a gen-3a read-1a std-1 read-2a; do
    flock /run/lock/specfirst-heavy.lock taskset -c 0-3 \
      bash scripts/clean_clone_gate.sh $wp /mnt/d/trial_work/specfirst/.git 29b15ca
  done
real-5a: 18 PASS, 0 FAIL; clean clone gate real-5a: PASS    (603 s)
real-2:  15 PASS, 0 FAIL; clean clone gate real-2: PASS     (595 s)
real-3a: 16 PASS, 0 FAIL; clean clone gate real-3a: PASS    (599 s)
gen-2a:  13 PASS, 0 FAIL; clean clone gate gen-2a: PASS     (672 s)
gen-3a:  15 PASS, 0 FAIL; clean clone gate gen-3a: PASS     (470 s)
read-1a: 14 PASS, 0 FAIL; clean clone gate read-1a: PASS    (1004 s)
std-1:   12 PASS, 0 FAIL; clean clone gate std-1: PASS      (442 s)
read-2a: 18 PASS, 1 FAIL; clean clone gate read-2a: FAIL    (481 s)
         FAIL  arm R, kept dry run (section "Generated kits and reader task folders")
```

The logs of real-5a and read-2a are in docs/reports
(`real-5a.clean-clone.gate.log`, `real-5a.read-2a.gate.log`); the six
others are not copied, and the line per gate above is counted from their
logs. The same eight ran before on clean clones of `90c5198`
(this work before `main` moved to `1a94134`), with the same result: seven
PASS, read-2a FAIL in that one check alone. The commits after `29b15ca`
change docs/reports and docs/state only.

## For the base session

The brief asks that the gates real-2, real-3a, gen-2a, gen-3a and read-1a,
and read-2a and std-1 when they are on `main`, pass on clean clones before
the merge. read-2a is on `main` since `b0a5530`, and its check "arm R, kept
dry run" cannot pass after any change of the method registry: the kept run
is held against the task and the kit.yaml written again now, and both
carry the registry (section "Generated kits and reader task folders").
real-5a must change the registry (its scope is three registry entries).
The options, with the executor's recommendation first:

1. Merge real-5a with that one check of read-2a failing for this reason
   alone (every other check of read-2a passes), and let the read track
   record a new dry run of arm R on the kit and task as written after the
   merge. That is a model run: the owner's spend (USD 0.55 for the kept run
   by read-2a's report) and the Claude Code CLI logged in by the owner.
   Recommended: the kept run is tied to the bytes of its task by design
   (ADR-010, decision 9), and a new run is the remedy that design gives.
2. Hold real-5a until the read track keeps a dry run valid across a change
   of the registry (for example, the kept run names the registry and
   catalog it was made with, as the look at issue #28 proposes). The
   efficacy tables wait for that.
3. Keep the model-based entries out of `registry.json`. Not recommended:
   the task folder would no longer show the reader the registry the
   machine uses.

The independent review (pass 1, `docs/reports/real-5a.review.md`) agrees
with the analysis and recommends otherwise on the order: not to merge with
read-2a's gate failing on `main`, but to record the new kept dry run of arm
R on the commit that will be merged, run read-2a's gate on a clean clone of
it, and then merge; and, before real-5b changes the registry again, to make
a kept run survive a change of the registry. Both orders need the owner's
model run; they differ in whether `main` carries a failing check of
read-2a until then.

The base session's answer, in its words. The owner answered in the
owner's question dialog on 2026-11-19, in Chinese; this file stays ASCII
(rule R10), so the answer is quoted in the base session's translation:

> The owner's answer verbatim: "[in Chinese: run the dry run once more
> before the merge] (Recommended)", which means re-record the run before
> merging. The option said:
> - real-5a re-generates the kit with the new registry on its own branch
>   and runs the arm R dry run once more, then keeps it. About USD 0.55, on
>   the owner's subscription.
> - At the merge, every gate on main passes.
> - Afterwards the read track changes the binding to a version, so that a
>   kept run no longer goes stale on every change.

And the base session's instructions with it: write kit 4 of the gate seed
again through read-2a's harness and make the arm R dry run once more, with
the same command, the same budget (ADR-010, decision 8) and the same canary
scan; keep it in place of the old one and record its cost; stop and report
if it fails or goes over budget, retrying at most once; run all eight gates
again on a clean clone of the final commit, read-2a's kept run included;
write in docs/state/read.md (Open) and here that a kept run is tied to the
bytes of the registry, the catalog and the generator, and that the read
track is to tie it to their versions instead.

That is the order the review recommended (option 1 of the list above with
the run made before the merge). What was done: section "The dry run of arm
R, made again".

## Review

Two passes by fresh-context reviewers (rule R7);
`docs/reports/real-5a.review.md` has both in full.

- Pass 1, on `d2e6d8b`: NOT SIGNED. Blocking: F1 (ADR-015 said generated
  kits' bytes do not change; their kit.yaml pins the registry's hash) and
  F2 (three decision records claimed more than their sources). Not
  blocking: F3 to F9. The reviewer ran the method vectors, the gate (18 of
  18), an independent fit in numpy and scipy (all 102 model-based gold rows
  to a relative 5.3e-14), its own comparison of the grids with the CSR
  pages (the same 9 cells differ), and defects of its own in models.R,
  `csr.compare`, `grid.plan` and `decisions.problems`, each seen.
- The fixes, in `2626186`: ADR-015 corrected; `custom:eff-model-terms` and
  `custom:eff-pairwise` are `conflict`, citing both sides;
  `custom:eff-baseline-rows` is `asked`; the check `decisions` counts a
  record without a class by its status (it raised a TypeError on one);
  F3, F4, F5 and F7 are in "What the checks do not cover", F8 is for the
  owner in ADR-015, F9 is fixed.
- Pass 2, on `2626186`: SIGNED. The reviewer validated the records against
  the schema, read every quote in the SAP and the Define-XML, ran the gate
  on a clone (18 of 18) and planted defects in the new records (each
  seen). Not blocking: G1 (F6 said defects planted "in the R
  implementation"; they are planted in the inputs), G2 (the gate evidence
  was of `b8bb1f5`), G3 (nothing holds the decimals record), G4 (the quote
  of the dose-response code was also the start of the other line; a
  `conflict` covers a whole record). G1, G3 and G4 are corrected in the
  text, and the quotes now end with the semicolon of each line; G2 by the
  gates of the commit that merges (section "The gates on clean clones"):
  `29b15ca`, which is `90c5198` with `main` `1a94134` merged in; no file
  both sides changed.

## GitHub and CI

Not merged yet: the merge waits for the gates of the commit that holds
the new kept run and for the review's pass 3.
