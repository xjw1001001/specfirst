# real-5a review (rule R7)

Reviewer: an independent agent with a fresh context, which did not write the
work. Date: 2026-11-19. Correctness only, no style.

Under review: commit `d2e6d8b` on branch `track/real`, the real-5a commits
`0c12cf5`, `cd066ad`, `b8bb1f5` and `d2e6d8b` (`553375a` merges `main`
`b0a5530`; `b8bb1f5..d2e6d8b` adds only the report and its gate log).
Read: CLAUDE.md; ADR-012; ADR-015; the amendment "of real-5a" of ADR-003;
docs/reports/real-5a.md and real-5a.clean-clone.gate.log; PLAN.md sections
2.3, 4.3, 4.5, 4.8, 7.3, 10, 13.3 (real-5) and 17; lessons 47 and 66 to 68;
the diff `b0a5530..d2e6d8b` of every file the brief names; ADR-010 decision
9 and `src/specfirst/harness/runs.py`, `gate.py` for question 5.

## Files I quote, with their SHA-256

At `d2e6d8b` (`git show d2e6d8b:<path> | sha256sum`):

```text
efa272f29c68a417fc97a67153982d083ca86c77a6b0b586dded44db83143ace  docs/decisions/ADR-015.md
a64589303ee692e79509a18b86c7ea0df5b8d49413831a71f76fceb7f48a33ba  docs/decisions/ADR-003.md
6caa78d43a49b03875566e1f9dc1dba1c2713f6e4212eb93d6322747947e8acd  docs/reports/real-5a.md
6fb2d3e1bbb41a225f738e4b1a6d8e81f3ec2ad8a1c57130e6b9a95c4a71f34d  docs/reports/real-5a.clean-clone.gate.log
ab52103931e4b1eac7c989c0df68089cf8dee5246039090990b4fb13fca7d973  standard/methods/model.ancova.lsmeans.yaml
7a463c1d7a0d9ad0827dc5b525e9f6409307ad5167740cc9c5407efc0d3a4904  standard/methods/model.ancova.pairwise.yaml
50b4e851bd6abcffb2890ecfc7771da015fc19ef16518ba792ae8e620c7f0f87  standard/methods/model.ancova.dose_response.yaml
e5f47480c46d1aae1affb3bd9f4b69f4c9d2ec5d8d99c4e78f30dd5ecb5634cb  standard/methods/registry.json
ef3d9e0fad43a15c0291ca72f694c5075ee496b386c8bc37e406deabb6518d9c  r/specfirstr/R/models.R
4a2f0b876d7ce42740672fd52bfcc31111cd03d70abe0afaa44a3500bcca3948  r/specfirstr/R/engine.R
d6b7b03fb5642a388d502182e87c711dc2dafbcd2ba22b38003573508863609c  src/specfirst/machine/csr.py
306dad7ff37274bf36764a02065d6c8c51c29bfa1bd7084fcda67b681a3a72c1  src/specfirst/machine/decisions.py
454026866bed0cb03fd2980338f339061545bc10b314fca50a6e56c404f2574f  src/specfirst/machine/build.py
a41aa63f57228e16198e2bff34785b2075d52f8e76bd09912d58146d04a9fc14  src/specfirst/gates.py
4b1a2102aadf0ab3945a6542e67e63eeb688aa6d86a612e9451a0f60b83ad79d  src/specfirst/gen/kits.py
528d99205b5f8dc5162f476aaf4859a832a38082f755ef368a0831c3ecef6bf3  src/specfirst/harness/runs.py
7c9b34a23d1c320da2f6ca527ff042222ad1a3b701fe96a694f78201dd751dfa  tests/methods/oracle_models.py
15155acfbd8ce033912b9c724698455f2c5603eb25870db880e11eef3a279be1  tests/methods/test_methods.py
0db2a4fd2b1f04c5bfa187a84162ec32b083ca27bcb2f36413a51604f22ac115  tests/defects/test_defects.py
b0cfebfdef1ba7d35d3e660f18a5799915834931a2c4850f800ea15a77ede88c  tests/unit/test_efficacy.py
e5b3dcfe53a8359101967f87fa183b837b89fec96bfefb5de833c89967db3f53  kits/cdiscpilot01/kit.yaml
5efdf53b320f7a39f0808adcc45abfde02067603d8890bb7d67de8ced1dc1ebb  kits/cdiscpilot01/gold/exceptions.yaml
481979bfaf091eacd91ccb7a6a843eb73225d0d173b136208ada218a847d56c7  kits/cdiscpilot01/gold/decisions/efficacy.jsonl
fb4350f53bbb04bda6765ce6d20560ac46ce4e74fd46f515c960f5e72cb0fc16  kits/cdiscpilot01/gold/events/efficacy-adas.json
16d0626e1e216d14c89f1972360e1ac52f6fc6e8cf85b091f519ce6a80a2ef9f  kits/cdiscpilot01/gold/layout/Out14-3-01.yaml
```

Pinned sources, read in the fetch cache (nothing written there):

```text
0cab016c76abb3dcaef31110611c95dbd9cd00df083b35e6d28fd69fca0d842d  p6/documents/CSR.pdf
210b7f1fdb0fd95e1b00b64fe1c7527d0000bd4e66b6ae31fdc08e2741af1bc7  p6/documents/SAP.pdf (= the kit's inputs/docs/sap.pdf)
7e6d580e0839564f6f119c4ba7e15963d3cf7cd0c88e9f3d7da5ad396221b1cd  p7/cdiscpilot01/spec/define/define-adam.xml
```

## Commands I ran, with their output (rule R8)

Setup: under WSL Ubuntu-24.04, a clone in the Linux file system, the
worktree's environment, every heavy run under the shared lock. Scratch
files only under `/root/scratch-review-real5a/` (two more clones, `clone2`
and `clone3`, for plants). Nothing was written into the checkout but this
file, nor into the fetch cache (the gate's "cache untouched" passed).

```text
$ git clone -q --no-local /mnt/d/trial_work/specfirst/.git /root/scratch-review-real5a/clone
$ git -C /root/scratch-review-real5a/clone checkout -q --detach d2e6d8b
$ . /mnt/d/trial_work/specfirst-real/scripts/env.sh
$ cd /root/scratch-review-real5a/clone; export SPECFIRST_ROOT=$PWD PYTHONPATH=$PWD/src
```

### C1. The method vectors

```text
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 env SPECFIRST_STRICT=1 \
    python -m pytest tests/methods -s -q -p no:cacheprovider
--- python-vectors
Python implementations: 120 cases of 9 methods, 0 differences
--- r-vectors
R implementations: 94 cases of 9 methods, 0 differences
--- exact-arithmetic
expected values computed again in exact arithmetic: 94 cases, 0 differences; written by hand: 56 cases (the display rules)
...
--- model-vectors
model-based methods in R: 30 cases of 3 methods, 0 differences
planted: model.ancova.dose_response always with dose = group_rank: 7 cases differ
planted: model.ancova.lsmeans always with weights = equal: 1 cases differ
planted: model.ancova.pairwise always with df = residual: 1 cases differ
7 passed in 6.49s
```

### C2. The gate, on the clone of d2e6d8b

```text
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 python -m specfirst gate real-5a
...
P1 determinism: 45 of 45 files have the same SHA-256 in both builds
grid Out14-3-01: 51 cells, 40 print a number; 40 of the 40 cells with results have a complete path to SDTM columns
grid Out14-3-03: 51 cells, 40 print a number; 40 of the 40 cells with results have a complete path to SDTM columns
grid Out14-3-05: 51 cells, 40 print a number; 40 of the 40 cells with results have a complete path to SDTM columns
results efficacy-adas: 102 results of model-based methods (R only, section 7.3): the gold ARD holds them as the R engine gave them, each stamped with the registry's hash of its options
results efficacy-adas, engines: 165 results in both, 0 disagree; largest relative difference 2.1e-16 (allowed 1e-09)
grid Out14-3-01 against CSR Table 14-3.01: 51 cells, 40 of them printed in the CSR; 48 equal the CSR, 3 differ, 3 of them with one class and a proof that holds
  cell:Out14-3-01/r14/c2: ours '(-2.08;1.15)', CSR '(-2.1;1.1)' (rule_choice)
  cell:Out14-3-01/r14/c3: ours '(-2.66;0.65)', CSR '(-2.7;0.7)' (rule_choice)
  cell:Out14-3-01/r17/c3: ours '(-2.19;1.11)', CSR '(-2.2;1.1)' (rule_choice)
grid Out14-3-03 against CSR Table 14-3.03: 51 cells, 40 of them printed in the CSR; 48 equal the CSR, 3 differ, 3 of them with one class and a proof that holds
  cell:Out14-3-03/r14/c2: ours '(-0.20;2.36)', CSR '(-0.2;2.4)' (rule_choice)
  cell:Out14-3-03/r14/c3: ours '(-1.10;1.53)', CSR '(-1.1;1.5)' (rule_choice)
  cell:Out14-3-03/r17/c3: ours '(-2.17;0.44)', CSR '(-2.2;0.4)' (rule_choice)
grid Out14-3-05 against CSR Table 14-3.05: 51 cells, 40 of them printed in the CSR; 48 equal the CSR, 3 differ, 3 of them with one class and a proof that holds
  cell:Out14-3-05/r14/c2: ours '(-1.78;1.24)', CSR '(-1.8;1.2)' (rule_choice)
  cell:Out14-3-05/r14/c3: ours '(-2.23;0.88)', CSR '(-2.2;0.9)' (rule_choice)
  cell:Out14-3-05/r17/c3: ours '(-1.95;1.14)', CSR '(-1.9;1.1)' (rule_choice)
efficacy: 3 tables, 153 cells; 144 equal the CSR; classified differences: 9 rule_choice
decisions: 8 records, 8 IDs; 45 options of analyses held against the decisions that set them; 0 problems
decisions: by class: 7 document_rule, 1 study_input
--- D9-efficacy
unchanged: 0 problems
planted, the ANCOVA without the baseline covariate: 19 problems, ...
planted, the dose as the rank of the group: 3 problems, ...
planted, the site in place of the pooled site group: 26 problems, ...
planted, the comparisons with asymptotic degrees of freedom: 8 problems, ...
planted, the comparison with placebo made against the low dose: 3 problems, ...
planted, the intent-to-treat set in place of the efficacy set: 109 problems, ...
planted, week 16 in place of week 24: 22 problems, ...
decision records, unchanged: 0 problems
decision records, the ANCOVA without the baseline covariate: 9 problems, ...
what the CSR cannot show: the LS means with equal weights change 36 results of the LS means and 0 cells (the tables print no LS mean)
planted, a cell of the CSR changed (0.245 to 0.254): 1 problems, ...
planted, the confidence limits shown with the CSR's 1 decimal (the 9 exceptions are stale): 9 problems, ...
planted, an exception whose other pattern proves nothing (3 decimals): 1 problems, ...
planted, an exception left out: 1 problems, ...
planted, an exception with the class reference_error: 1 problems, ...
planted, an exception that names no decision record: 1 problems, ...
--- D10-trace-model
  unchanged: the 1 columns without a reads edge emptied: 0 of 66 results change
  unchanged: the 1 columns without a reads edge rolled: 0 of 66 results change
  planted: the 2 columns without a reads edge emptied: 66 of 66 results change
  planted: the 2 columns without a reads edge rolled: 0 of 66 results change
planted, the reads edges to ADQSADAS.BASE left out (12 edges): 1 problems, ...
61 passed in 76.91s (0:01:16)
...
PASS  environment          0.5 s
PASS  pins                 0.3 s
PASS  lint                 0.1 s
PASS  registry             0.0 s
PASS  unit tests         332.0 s
PASS  method vectors       6.4 s
PASS  kit                  0.1 s
PASS  P1 determinism      39.1 s
PASS  P2 reproduction      0.4 s
PASS  trace                1.1 s
PASS  results              3.3 s
PASS  grids                2.4 s
PASS  efficacy             2.4 s
PASS  decisions            0.4 s
PASS  pilot tests         53.0 s
PASS  planted defects     77.2 s
PASS  cache untouched      0.1 s
PASS  ASCII                0.0 s
GATE real-5a: PASS
```

The reference grids were written to the clone's `build/csr/cdiscpilot01/`
(14-3.01.json, 14-3.03.json, 14-3.05.json); `git status` of the clone stays
empty (ignored).

### C3. Defects I planted (the executor did not)

On the gate's first build, with the check the gate calls
(`build.csr_against`, `decisions.problems`), changing only the inputs held
in memory (script `p_plants.py`):

```text
control: efficacy problems 0, decision problems 0
P1 the 9 exceptions name custom:eff-analysis-set, not custom:eff-display-decimals: 0 problems, NOT seen
P2 custom:eff-display-decimals says confidence_limit 1 (gold shows 2): 0 problems, NOT seen
P3 custom:eff-analysis-set says ADSL.ITTFL (gold reads EFFFL): 0 problems, NOT seen
P3b custom:eff-visit-record says ANL02FL: 0 problems, NOT seen
P4 custom:eff-pairwise says confidence_level 90: 6 problems, seen; e.g. custom:eff-pairwise: ars:An_ADAS_W24_PwPbo has confidence_level = 95, the decision confidence_level = 90
P5 layout 14-3.01, the blocks Week 24 and Change from Baseline exchanged: 14 problems, seen; e.g. Out14-3-01: line 5: the grid has the heading 'Change from Baseline', the CSR 'Week 24' with cells None
P6 layout 14-3.01, the 95% CI template with its limits exchanged: 2 problems, seen; e.g. ... ours '(1.15;-2.08)', CSR '(-2.1;1.1)': the proof does not hold: with the other patterns the cell is '(1.1;-2.1)'
P7 CSR 14-3.01 parsed with another population line: 0 problems, NOT seen
P8 CSR 14-3.01 parsed with another footnote [1]: 0 problems, NOT seen (footnotes are not compared, as the report says)
```

In the code, in scratch clones of d2e6d8b (the first four by `patch.py` in
`clone2`, each on a fresh checkout; the last two in `clone3`;
`SPECFIRST_STRICT=1`):

```text
plant lsmeans-covariate-mean (models.R: the covariate at its mean over every record with a value, not the model records)
$ pytest tests/methods -k "r-vectors or model-vectors"      -> exit 1
R implementations: 94 cases of 9 methods, 12 differences
E  model.ancova.lsmeans, records with a missing value are left out: lsmean, A: 2.849383667180277, expected 2.992050707381986
plant lsmeans-level-ignored (models.R: the limits of the LS means always at 95%)   -> exit 1
R implementations: 94 cases of 9 methods, 12 differences
E  model.ancova.lsmeans, asymptotic, 90 percent: lower_cl, A: 2.4802892283987306, expected 2.52517877503082
plant pairwise-adjusted (models.R: adjust = "sidak" in place of "none")             -> exit 1
R implementations: 94 cases of 9 methods, 42 differences
E  model.ancova.pairwise, each group against A: p_value, B: 0.3348517707381595, expected 0.18443379835733578
plant csr-header-not-compared (csr.compare: the counts under the column labels skipped)
$ pytest tests/unit/test_efficacy.py                        -> exit 1
FAILED tests/unit/test_efficacy.py::test_every_cell_is_compared_without_its_blanks   (line 122: the cell counts)
plant grid-columns-ignored (grid.plan: a statistics block in every column)
$ pytest tests/unit/test_efficacy.py                        -> 1 failed, 36 passed
FAILED tests/unit/test_efficacy.py::test_a_statistics_block_gives_a_row_per_statistic   (line 220: the ARD rows of the columns)
plant decisions-not-compared (decisions.problems: an option never held against the value)
$ pytest tests/unit/test_efficacy.py                        -> 1 failed, 36 passed
FAILED tests/unit/test_efficacy.py::test_a_decision_is_held_against_the_parameters_of_the_analyses_it_binds   (line 382)
unchanged: 37 passed in 1.77s
```

### C4. An independent computation of the models and of the cells

Every model-based result of the gold ARD fitted again with numpy and scipy
(least squares, `scipy.stats.t`) from the build's ADQSADAS and ADSL, with
the selection of the event (PARAMCD ACTOT, the week, ANL01FL Y, ADSL.EFFFL
Y), SITEGR1 as a factor, BASE as a covariate, the planned dose or the
treatment as a factor, proportional weights for the LS means:

```text
W24: n=234, sites=11, dose response with BASE: p=0.2447 (b=-0.011792, df=221)
W24: n=234, sites=11, dose response without BASE: p=0.2532 (b=-0.011521, df=222)
W08: n=234, sites=11, dose response with BASE: p=0.4967 (b=0.005498, df=221)
W08: n=234, sites=11, dose response without BASE: p=0.4761 (b=0.005735, df=222)
W16: n=234, sites=11, dose response with BASE: p=0.4115 (b=-0.007796, df=221)
W16: n=234, sites=11, dose response without BASE: p=0.4004 (b=-0.007941, df=222)
W16: PwLow Grp_High: diff -0.4046 se 0.7837 CI (-1.9491;1.1398) p 0.6061
independent OLS (numpy, scipy): 102 of 102 model-based gold rows compared; largest relative difference 5.3e-14
```

The built grids against the pdftotext pages, without `specfirst.machine.csr`
(script `p_cells.py`: each CSR line split on two blanks or more, compared in
order with the grid's non-empty cells, blanks removed):

```text
$ pdftotext -layout -f 49 -l 49 .../p6/documents/CSR.pdf text/csr-p49.txt   (and 51, 53; poppler 24.02.0)
$ python -I p_cells.py clone/build/p1/cdiscpilot01/first/gold/grid text
Out14-3-01 (CSR page 49): 19 lines, CSR 19; 3 differences:
  95% CI: ours (-2.08;1.15), CSR (-2.1;1.1)
  95% CI: ours (-2.66;0.65), CSR (-2.7;0.7)
  95% CI: ours (-2.19;1.11), CSR (-2.2;1.1)
Out14-3-03 (CSR page 51): 19 lines, CSR 19; 3 differences:
  (the three cells of the report)
Out14-3-05 (CSR page 53): 19 lines, CSR 19; 3 differences:
  (the three cells of the report)
printed cells compared: 120, equal: 111
```

### C5. The R implementation on inputs no vector holds

`r_edges.R` sources util.R, methods.R and models.R of the clone:

```text
-- lsmeans, one group with model records
"ERROR: contrasts can be applied only to factors with 2 or more levels"
-- pairwise, only the reference has model records
"ERROR: contrasts can be applied only to factors with 2 or more levels"
-- pairwise, group IDs with '-'
 $ estimate:NA  $ se:NA  $ lower_cl:NA  $ upper_cl:NA  $ p_value:NA
-- pairwise, the same with IDs without '-'
 $ estimate:-0.146  $ se:0.238  $ lower_cl:-0.707  $ upper_cl:0.416  $ p_value:0.559
-- lsmeans, a factor confounded with the groups
NOTE: A nesting structure was detected in the fitted model:
    .g %in% .f1
 $ lsmean:3.18  $ se:0.164  $ lower_cl:2.8  $ upper_cl:3.56
-- pairwise, a factor confounded with the groups
 $ estimate:NA  $ se:NA  $ lower_cl:NA  $ upper_cl:NA  $ p_value:NA
$ Rscript --vanilla r_label.R
emmeans 2.0.4 contrast labels: '(Grp-2) - (Grp-1)' '(Grp-3) - (Grp-1)'
looked up as: 'Grp-2 - Grp-1'
```

### C6. The sources and the hashes behind findings F1, F2 and question 5

```text
$ pdftotext -layout .../p6/documents/SAP.pdf text/sap.txt; tr '\n' ' ' < sap.txt | tr -s ' ' > sap.flat
$ grep -o -F "<quote>" sap.flat | wc -l     (every SAP quote of gold/decisions/efficacy.jsonl)
1 x: will not assess site*treatment interaction
1 x: the assessment closest to the target day will be selected
1 x: All patients who were randomized and took drug, and have at least 1 post-baseline measure
1 x: Missing postbaseline efficacy values will be imputed using last observation carried forward
1 x: a new pooled site identifier assigned for the purpose of analysis
2 x: an ANCOVA model will be used with the baseline score, site, and treatment
2 x: H0: b = 0, where b is the coefficient for treatment
3 x: Treatment will be included as a continuous variable
3 x: pairwise comparisons among the 3 groups will be performed
5 x: p-values without adjustment for multiple comparisons
(sap.txt lines 584 to 592, read in the file viewer: SAP 10.1.1)
... For each of these analyses, an ANCOVA model will be used with the baseline score, site,
and treatment included as independent variables. Treatment will be included as a
continuous variable, and results for a test of dose response will be produced. Interaction
terms will not be investigated. If the test for dose response is statistically significant,
pairwise comparisons among the 3 groups will be performed and evaluated at a
significance level of 0.05.
$ sed -n 18407,18490p define-adam.xml   (Table_14-3.01, R.1 and R.2; abridged)
R.1 Documentation: Linear model analysis of CHG for dose response; using randomized dose
    (0 for placebo; 54 for low dose; 81 for high dose) and site group in model. ...
R.1 ProgrammingCode: class sitegr1; model CHG = trtpn sitegr1;
R.2 Documentation: ... using randomized treatment as class variable and site group as class
    variable in model and the baseline value as a covariate.
R.2 ProgrammingCode: class trtpn sitegr1; model CHG = trtpn sitegr1 base; ...
    lsmeans trtpn / OM STDERR PDIFF CL;
$ git show b0a5530:standard/methods/registry.json | sha256sum
21b83df6c573f54fbaa79c311a2e8aea4b5053674067938c3d226f8d026eafe5  -
$ git show d2e6d8b:standard/methods/registry.json | sha256sum
e5f47480c46d1aae1affb3bd9f4b69f4c9d2ec5d8d99c4e78f30dd5ecb5634cb  -
$ git show d2e6d8b:src/specfirst/gen/kits.py | grep -n registry_sha256
326:            "registry_sha256": sha256_file(registries.json_path(root)),
(Grep) src/specfirst/harness/kept/R-task-50024a8d7ca2/task.json:185:
  "standard/methods/registry.json": "21b83df6c573f54fbaa79c311a2e8aea4b5053674067938c3d226f8d026eafe5",
```

## Answers to the five questions

### 1. The semantics against the R implementation; the independence of the vectors

I read the 21 statements of the three entries against `models.R`
(`model_frame`, `m_ancova_lsmeans`, `m_ancova_pairwise`,
`m_ancova_dose_response`) and `engine.R` (`run_model`). On the inputs the
vectors and the pilot hold they say what R computes: the model records
(statement 1: a missing y, group, factor or covariate drops the record);
the terms (a factor with one level dropped, levels in code-point order, no
interaction); the variance (lm, N - r); the LS means (emmeans with
`data = frame`, so the covariate at its mean over the model records; equal
or proportional weights, the latter the share of each level over all model
records, which is SAS's OM in a main-effects model); the SE and the limits
(t with the residual df, or `update(df = Inf)`); the pairwise differences
(`trt.vs.ctrl`, `adjust = "none"`, equal weights, which statement 3 rightly
says do not matter); the dose response (lm with the dose first, car::Anova
type 3, equal for a one-degree term to the t test the statement names, and
the t test when a coefficient is aliased, lesson 67); the linear contrast
(dose minus the unweighted mean of the doses of the groups present).
`run_model` takes the dose of a record from the grouping variable through
the subject key and refuses a text column. Three inputs no vector holds
leave the statements (F5): one group with records (R stops), group IDs
with a minus sign (silent NA), a factor nested in the groups (a number where
statement 7 says missing). None arises on the pilot.

The expected values are independent of R. `oracle_models.py` imports only
`decimal` and `fractions`: Gauss-Jordan on the normal equations in
fractions, the LS-mean and contrast vectors as the statements write them,
p-values and quantiles from the closed form of the t distribution and the
erf series. `exact-arithmetic` recomputes every stored value with it (94
cases, 0 differences, C1), and `r-vectors` and `model-vectors` hold R
against the stored values at a relative 1e-12. Its limit is full rank
(`NotFullRank`), so "not estimable" is tested only through the
missing-group and no-df cases. My own fit with numpy and scipy (C4) gives
all 102 model-based gold rows to a relative 5.3e-14, and the three
dose-response p-values the report gives, with BASE (0.2447, 0.4967, 0.4115)
and without it (0.2532, 0.4761, 0.4004). My three plants in `models.R`
(C3) were each seen by the vectors.

### 2. The cells against the CSR, and the class of the 9

Yes. The gate on my clone (C2) gives 153 cells, 120 printed in the CSR, 144
equal (111 printed and 33 empty in both), 9 different, each with one entry
whose proof holds. My own comparison without the project's parser (C4)
finds the same 19 lines per table with the same labels and headings and the
same 9 differences among the 120 printed cells. I read pages 49, 51 and 53
myself: the nine CSR texts are those of the report, and my raw limits show
the CSR rounds the raw value (W16, high against low: -1.9491 gives "-1.9";
the 2-decimal "-1.95" would give "-2.0").

SAP template 5 (SAP lines 1003 to 1032) gives the masks: n "xxx", Mean (SD)
"xx.x (xx.xx)", Median (Range) "xx.x (xx;xxx)", p-values "x.xxx", "Diff. of
LS Means (SE)" "xx.x(x.xx)", "95% CI" "(xx.xx;xx.xx)". The CSR follows
every mask but the last. Under decision 17 (the documents decide; what the
CSR does differently is a `rule_choice` with its proof) gold with 2 decimals
and a `rule_choice` for the CSR's 1 decimal is sound, provided a shell's
mask counts as a document's rule, which is the owner's call at N2 (section
4.8: "The owner still confirms each new case"). The proof `other_pattern`
meets section 4.8 in substance for a display decision: the alternative
applied to the cell's own raw results gives the CSR's text, and the 3-decimal
plant shows it is not true of any pattern. Two weak points: the same
template's labels are not followed (F8), and the proof's link to its
decision is not checked (F3, F4).

### 3. Can each new check fail?

Yes, each fails for the right reason:

- `efficacy`: D9's 13 plants (C2), and mine P5 and P6 (C3). Not seen, by
  design or not stated: an exception naming another existing decision (P1,
  F3), the population line (P7, F7), the footnotes (P8, stated).
- `decisions`: D9's plant without BASE (9 problems), my P4 (6 problems), and
  in code my plant that drops the comparison (unit test fails). Not seen:
  the values of four records (P2, P3, P3b; F4).
- `method vectors` / `model-vectors`: the executor's three option plants,
  and my three plants in `models.R` (12, 12 and 42 differences).
- D9 and D10: the planted halves fail; the controls pass (C2).
- Unit tests of csr, layout and decisions: my plants in `csr.compare`,
  `grid.plan` and `decisions.problems` each fail one test at the assertion
  that names the defect (C3).

### 4. Checks that pass by construction; what the comparison hides; unsupported statements; the records

By construction (lesson 47): no gate check is filled in by a table the work
writes. Two links are true of any value, though: the proof of a classified
cell accepts any existing decision ID (F3), and `decisions` accepts any value
of four of the eight records, among them the record the 9 classified cells
rest on (F4). Titles, column labels and row labels are written from the CSR,
so their equality is by construction; the report counts none of them as a
reproduced cell (51 cells per table = 3 counts + 48 body cells), which is
right. D10's control half has one column to empty; its planted half is what
shows it can fail.

Hidden by the comparison: blanks in cells, labels and titles; no number can
hide there, since every mask separates its numbers by a parenthesis or a
semicolon. Footnotes (stated; ours are tied to nothing the event runs);
indentation (stated); the population line (parsed, not compared, not
stated: F7). The header row is compared: its three counts are computed
(D9's intent-to-treat plant changes them) and the column labels are
compared without blanks.

Not supported by the runs: ADR-015's "their bytes do not change" for
generated kits (F1); "defects planted in the R implementation" (F6); the
decisions module's reference to a test file that does not exist (F9).
Everything else I checked holds: 144 and 9; the p-values with and without
BASE; 40 of 40 traced cells per table; 45 options; P1 on 45 files; the D9
and D10 counts; the SAP quotes word for word (C6).

The records: all 8 fit the schema, carry custom IDs and owning units, and
every quote is in its source. Three are not honest about their status, and
one quote is cut from a conditional sentence (F2).

### 5. read-2a's kept dry run

The analysis is right. `runs.check` (runs.py lines 666 to 684) builds the
task of the kept run again and compares its manifest file by file, and the
SHA-256 of the kit.yaml written now with the recorded one. The kept task
pins `standard/methods/registry.json` at `21b83df6...` (C6), the registry
before real-5a, and the gate's generated kit.yaml pins the registry's hash
(gen/kits.py line 326). Any change of the registry fails "arm R, kept dry
run", and real-5a must change it. The other kept folder (`probe-task-...`)
is not read by the gate (`gate.kept_runs` takes `R-*` only), so only that
check fails, as the executor's run showed. I did not run read-2a's gate
myself: another session holds the chain of clean-clone gates.

Putting it to the base session is right as a first step, but the choice is
the owner's: the brief makes read-2a's gate a condition of the merge, and
the ways out are a model run (the owner's spend, the owner's login of the
CLI) or a change of read-2a's gate (section 2.3, "a gate cannot pass without
changing the gate"). The executor's recommended option 1 merges with a red
gate on `main`; see "The owner's choices", item 1.

## Findings

### F1 (blocks the merge): ADR-015 says the bytes of generated kits do not change; they do

Where: ADR-015, "Consequences", first item: "Generated kits use no
model-based method; their bytes do not change (docs/reports/real-5a.md shows
the check)."

Evidence (C6): `src/specfirst/gen/kits.py` line 326 writes the SHA-256 of
`registry.json` into the pins of every generated kit.yaml, and this commit
changes `registry.json` (`21b83df6...` to `e5f47480...`). So every generated
kit.yaml changes. The report says so ("every generated kit's kit.yaml
changes"), as do CLAUDE.md and lesson 68; the report holds no check that the
bytes of a generated kit are unchanged. The ADR contradicts the evidence on
the point the brief asked to be stated.

Fix: every generated kit.yaml changes (its `registry_sha256`); the data,
gold and documents of a generated kit do not (binding rule B3 takes
descriptive methods only, `ars.py` line 285, so the new operation names
cannot reach a generated event).

### F2 (blocks the merge): three decision records present as settled what the documents leave open

PLAN.md section 4.5: "Documents that contradict each other (contradicts)
need a person before any class is given"; decision-record.schema.json
encodes it (a record with status `conflict` needs no class). ADR-015 lists
the contradictions for the owner; the records do not show them:

- `custom:eff-model-terms` (status `stated`, class `document_rule`) binds
  the three dose-response analyses `An_ADAS_W*_Dose` with the covariate BASE
  and cites SAP 10.1.1 and the Define-XML's `Table_14-3.01.R.2` (the
  pairwise result). The Define-XML's metadata of the dose-response result
  itself, `R.1`, has "randomized dose ... and site group in model" and
  `model CHG = trtpn sitegr1;` (C6). `custom:eff-dose-response` cites R.1 for
  the doses; `eff-model-terms` leaves out the R.1 that contradicts it. The
  choice is well argued (SAP 3.3 and 10.1.1, template 5 footnote [1], and
  only the model with BASE reproduces the CSR, C4), but the record reads as
  if there were no contradiction.
- `custom:eff-pairwise` quotes SAP 10.1.1 as "pairwise comparisons among the
  3 groups will be performed". The sentence is "If the test for dose
  response is statistically significant, pairwise comparisons among the 3
  groups will be performed and evaluated at a significance level of 0.05"
  (C6), and SAP 7.3 says they "will only be performed if the test for dose
  response is significant". None of the three tests is (0.245, 0.497,
  0.412). The quote drops the condition, and the choice to show the
  comparisons anyway (as template 5 and the CSR do) has no record.
- `custom:eff-baseline-rows`: status `stated`, class `study_input`, no
  citation; ADR-015 says it "has no source". Nothing states it, and a
  `study_input` is what a person supplies (section 4.5).

Fix, in text only (no check reads the status; the schema accepts a
`conflict` record with a value): records with status `conflict`, no class
and both sides cited for the dose-response model terms and for showing the
pairwise comparisons unconditionally; SAP 10.1.1 quoted with its condition;
the baseline rows marked as the owner's input. Or the owner answers items 2
and 3 of ADR-015 "For the owner" now and the records cite the answers.

### F3 (does not block): a proof may name any decision record

`csr.judge` (csr.py lines 251 and 252) asks only that `entry["decision"]` is
the ID of a record of the kit. P1 (C3): with all 9 entries naming
`custom:eff-analysis-set`, 0 problems. The executor's plant names a record
that does not exist and is seen; a wrong existing one is not. Recommendation:
tie `other_pattern` to its decision (the record's value gives the decimals of
the statistic and the entry's patterns are another alternative of it), or at
least ask that the decision binds the cell's analysis or method.

### F4 (does not block): the check `decisions` holds the values of 4 of the 8 records

`decisions.PARAMETERS` covers `eff-model-terms`, `eff-dose-response`,
`eff-pairwise` and `eff-lsmeans-weights`. The values of `eff-analysis-set`,
`eff-visit-record`, `eff-display-decimals` and `eff-baseline-rows` are held
against nothing but the schema and their bound elements: P2, P3 and P3b give
0 problems (C3). The report's sentence on the 45 options is accurate; the
gate's comment "the decision records hold against the reporting event" says
more. It matters for `eff-display-decimals`, which all 9 classified cells
rest on. Recommendation: hold it against the `resultPattern` of the
operations it binds, and the analysis-set and visit records against the set
and the subsets; or say in ADR-015 decision 10 which records are held.

### F5 (does not block): the R implementation leaves its statements on three inputs no vector holds

Evidence C5. (a) One group with model records: `m_ancova_lsmeans` stops
("contrasts can be applied only to factors with 2 or more levels"); by
statement 7 the present group has its LS mean and the others are missing.
The same in `m_ancova_pairwise` when only the reference has records. Loud,
so no wrong number reaches a table. (b) Group IDs with a minus sign: every
pairwise result is NA, silently, because emmeans labels the contrast
"(Grp-2) - (Grp-1)" and the row is looked up as `paste(id, "-", reference)`;
ARS IDs may hold a minus sign. (c) A factor nested in the groups: emmeans
detects the nesting and gives an LS mean of 3.18 (SE 0.164) that statements
4 and 7 call not estimable, so missing. None arises on the pilot (Grp_Pbo,
Grp_Low, Grp_High; SITEGR1 crosses the arms). Recommendation: vectors for
the three (the oracle needs a rank-deficient path or hand values),
`nesting = NULL` in the emmeans call, contrast rows taken by position, a fit
without the group term when one group is left.

### F6 (does not block): "defects planted in the R implementation" are options changed in the inputs

ADR-015 decision 5, tests/methods/README.md and the report say
`model-vectors` plants one defect per entry in the R implementation. It runs
the unchanged R code on cases whose option was overwritten
(test_methods.py lines 184 to 198). That stands for "an option ignored" but
plants nothing in R. My plants in `models.R` were all seen (C3), so the
claim that the vectors see implementation defects holds; the wording should
say what is planted.

### F7 (does not block): the CSR's population line is parsed and never compared

`csr.parse` keeps `population` ("Efficacy" on the three pages);
`csr.compare` does not read it, the grids have none, and "What the checks do
not cover" does not list it. P7 (C3): 0 problems. The counts would show a
changed analysis set, so no number is hidden; the printed text is.
Recommendation: list it, or compare it with the name of the analysis set.

### F8 (does not block; for N2): template 5 rules the decimals but not the labels

ADR-015 decision 9 follows template 5's masks over the CSR, which makes the
9 classified cells, but takes the CSR's row labels over the same template's
("N", "P-value(Dose Response)", "Diff. of LS Means (SE)" against "n",
"p-value(Dose Response)", "Diff of LS Means (SE)"), with no record. "Labels
are not cells" explains why no exception is needed, not why decision 17
binds one part of the shell and not the other. Item 1 of "For the owner"
should name both: one answer settles both.

### F9 (does not block): two small inaccuracies

The docstring of `src/specfirst/machine/decisions.py` says
"tests/unit/test_decisions.py plants both"; there is no such file (the tests
are in tests/unit/test_efficacy.py). In tests/defects/README.md an empty line
between the rows D8 and D9 ends the table, so D9 and D10 render as text.

## The owner's choices (PLAN.md section 2.3), with my recommendation

1. **read-2a's kept dry run** (blocks the merge, not this signature). The
   ways out are a model run or a change of read-2a's gate; both are the
   owner's (question 5). Recommendation: do not merge with a red gate on
   `main`. Record the new dry run of arm R against the tree as it will be
   merged (track/real at the fixed commit, which already holds `main`
   b0a5530), keep it in `src/specfirst/harness/kept/`, run read-2a's gate on
   a clean clone of that commit, then merge. real-5b changes the registry
   again (the mixed model, CMH): before it, ask the read track for a kept run
   that survives a registry change it did not depend on (the direction of
   issue #28), or plan one dry run per registry change.
2. **The class of the 9 cells (N2).** Recommendation: accept `rule_choice`,
   and decide the labels the same way (F8): either template 5 rules both
   (its labels become gold and a label difference needs a class), or the
   CSR's display rules both (then `custom:eff-display-decimals` takes 1
   decimal and the 9 entries go).
3. **The dose-response model (section 4.5).** SAP 3.3, 10.1.1 and template
   5 keep BASE; the Define-XML's R.1 leaves it out. Recommendation: the SAP
   (only it reproduces the CSR, C4), recorded as the owner's answer.
4. **Pairwise comparisons when the dose response is not significant
   (section 4.5).** SAP 7.3 and 10.1.1 say they are not performed; template 5
   and the CSR show them. Recommendation: show them, as the reference does,
   recorded as the owner's answer.
5. **`custom:eff-baseline-rows`** (a `study_input`; both readings give the
   same cells here). Recommendation: BASE on the week's records, as built,
   recorded as the owner's input.
6. **The proposals for `catalog@2`**: for the std track; nothing is needed
   for real-5a.

## Verdict

The machine is sound: the gate passes on my clone of d2e6d8b, every printed
cell equals the CSR or is one of the 9 classified limits, the model results
match an independent fit to 5.3e-14, and every new check fails on defects I
planted. Two documentation defects block the merge until fixed (text only,
no code): F1 and F2. Apart from the findings, read-2a's kept run needs the
owner's choice before the merge (item 1 above); that is not a defect of
real-5a.

Verdict: NOT SIGNED (blocking: F1, F2)

## Pass 2

Reviewer: another independent agent with a fresh context, which wrote
neither the work nor pass 1. Date: 2026-11-19. Correctness only.

Under review: commit `2626186` (the executor's answer to pass 1), read as
the full diff `d2e6d8b..2626186`: ADR-015, docs/reports/real-5a.md, this
file (pass 1 as above), `kits/cdiscpilot01/gold/decisions/efficacy.jsonl`,
`src/specfirst/machine/build.py`, `src/specfirst/machine/decisions.py`,
tests/defects/README.md. Read besides: PLAN.md sections 2.3, 4.3, 4.5 and
4.8; decision-record.schema.json; `build.csr_comparison` and
`build.decision_checks`; `specfirst.harness.task` (what a task folder
copies, its ID); `specfirst.gen.documents` (how a generated kit writes an
`asked` record); the SAP and the Define-XML themselves. The checkout's
working tree also holds an uncommitted paragraph in docs/reports/real-5a.md
("For the base session", on pass 1's recommendation); it is not part of
`2626186` and not reviewed here.

### Files I quote, with their SHA-256

At `2626186` (`git show 2626186:<path> | sha256sum`):

```text
a918658798bb1443c0f9f1ab153c07172a699324d16f02651af51231bad81dd7  docs/decisions/ADR-015.md
d0676bf50e86f059b282ba7beb7a83ed62091edd952e06a6f83ebcf29792ba18  docs/reports/real-5a.md
d3381ed855e693e9106c566da1948595446c25d270636c0f3efe64155c745bea  docs/reports/real-5a.review.md
2befca3beba883658cfaa40ddabe85981d50424b9429dfc732eb55d97790a793  kits/cdiscpilot01/gold/decisions/efficacy.jsonl
2d151aa2923ed96e195e1a4348e5180c495f8b25f6029082d5dc72c274456585  src/specfirst/machine/build.py
386f26fffaf6799bbb6e8783c97850175b3e14ea71aff6274872bc8268c73da9  src/specfirst/machine/decisions.py
7c15436e0da641837703ea0268c65f86f0106c4ef75e677324ef4c59e60a222d  tests/defects/README.md
1c606e284d791ef092a029e5b40f4aff4e46e04b2f605cfec4d9517970548bfc  standard/schemas/decision-record.schema.json
```

The pinned sources, read only in the fetch cache, have the SHA-256 pass 1
gives (SAP.pdf `210b7f1f...`, define-adam.xml `7e6d580e...`, CSR.pdf
`0cab016c...`; `sha256sum` again today, the same). I quote no cell of the
CSR.

### Commands I ran, with their output (rule R8)

Setup, under WSL Ubuntu-24.04; scratch only under
`/root/scratch-review2-real5a/`; nothing written into the checkout but
this section, nor into the fetch cache:

```text
$ git clone -q --no-local /mnt/d/trial_work/specfirst/.git /root/scratch-review2-real5a/clone
$ git -C /root/scratch-review2-real5a/clone checkout -q --detach 2626186
$ . /mnt/d/trial_work/specfirst-real/scripts/env.sh
$ cd /root/scratch-review2-real5a/clone; export SPECFIRST_ROOT=$PWD PYTHONPATH=$PWD/src
$ pdftotext -layout $SPECFIRST_CACHE/p6/documents/SAP.pdf ../text/sap.txt   (poppler 24.02.0; 2035 lines)
```

#### D1. The SAP and the Define-XML at the places the records cite

Line numbers of sap.txt as `sed -n` counts them.

```text
$ sed -n 396,404p sap.txt   (SAP 7.3)
7.3.        Multiple Comparisons and Multiplicity
...
The primary analyses for the 2 primary efficacy endpoints will be a test for dose
response. Within each primary efficacy endpoint, 3 sets of pairwise comparisons for the
2 active treatment groups and placebo will only be performed if the test for dose response
is significant.
$ sed -n 582,596p sap.txt   (SAP 10.1.1; abridged)
10.1.1.     ADAS-COG (11)
... an ANCOVA model will be used with the baseline score, site,
and treatment included as independent variables. Treatment will be included as a
continuous variable, and results for a test of dose response will be produced. Interaction
terms will not be investigated. If the test for dose response is statistically significant,
pairwise comparisons among the 3 groups will be performed and evaluated at a
significance level of 0.05.

Summary statistics will be generated for each visit including baseline using the efficacy
population with LOCF imputation. ...
$ sed -n 808,809p sap.txt   (the SAP's list of tables)
14.        ADAS Cog (11) - Mean and Mean Change from Baseline over Time (Template
      9)
$ sed -n 1026p sap.txt; sed -n 1036p sap.txt   (template 5)
    P-value(Xan - Placebo) [1][3]                                x.xxx              x.xxx
[3] Pairwise comparison with treatment as a categorical variable: p-values without adjustment for multiple
$ sed -n 18405,18485p define-adam.xml   (Table_14-3.01; abridged, file line numbers in front)
18409 OID="Table_14-3.01.R.1" ResultIdentifier="dose response analysis for ADAS-Cog changes from baseline"
18430 Linear model analysis of CHG for dose response; using randomized dose (0 for
      placebo; 54 for low dose; 81 for high dose) and site group in model. ...
18437   class sitegr1;
18438   model CHG = trtpn sitegr1;
18443 OID="Table_14-3.01.R.2" ResultIdentifier="pairwise comparisons to placebo for ADAS-Cog changes from baseline"
18471   class trtpn sitegr1;
18472   model CHG = trtpn sitegr1 base;
18474   lsmeans trtpn / OM STDERR PDIFF CL;
```

#### D2. The records against the schema, and their citations against the sources

`p_records.py`: jsonschema's Draft 2020-12 validator on each record with
the schema of the clone; the same records with three plants; every SAP
quote searched in sap.txt (blanks and line ends as one blank); every
Define-XML quote searched in the text of the elements whose `OID` is the
citation's anchor (ElementTree).

```text
$ python -I p_records.py clone text/sap.txt $SPECFIRST_CACHE/p7/cdiscpilot01/spec/define/define-adam.xml
jsonschema 4.26.0: 8 records
  custom:eff-analysis-set: status stated, class document_rule, 3 citations, schema errors 0 []
  custom:eff-visit-record: status stated, class document_rule, 3 citations, schema errors 0 []
  custom:eff-model-terms: status conflict, class None, 5 citations, schema errors 0 []
  custom:eff-dose-response: status stated, class document_rule, 3 citations, schema errors 0 []
  custom:eff-pairwise: status conflict, class None, 5 citations, schema errors 0 []
  custom:eff-lsmeans-weights: status stated, class document_rule, 1 citations, schema errors 0 []
  custom:eff-baseline-rows: status asked, class study_input, 0 citations, schema errors 0 []
  custom:eff-display-decimals: status stated, class document_rule, 2 citations, schema errors 0 []
  planted, conflict record without class but status stated: 1 schema errors
  planted, asked record without class: 1 schema errors
  planted, a stated document_rule without citations: 1 schema errors
citations:
  custom:eff-analysis-set sap '6': 1 x at sap.txt lines [362]: ...
  custom:eff-visit-record sap '8.1': 1 x at sap.txt lines [418]: ...
  custom:eff-visit-record sap '8.2': 1 x at sap.txt lines [437]: ...
  custom:eff-model-terms sap '10.1.1': 2 x at sap.txt lines [587, 641]: 'an ANCOVA model will be used with the baseline score, site, and treatment'
  custom:eff-model-terms sap '7.1': 1 x at sap.txt lines [383]: ...
  custom:eff-model-terms sap '15.1': 1 x at sap.txt lines [1914]: ...
  custom:eff-model-terms define 'Table_14-3.01.R.2': in the element True ...: 'model CHG = trtpn sitegr1 base'
  custom:eff-model-terms define 'Table_14-3.01.R.1': in the element True (2 elements with that OID);
      also in ['CDISC.ADaM.2.1', 'CDISCPILOT01', 'Table_14-3.01', 'Table_14-3.01.R.2']: 'model CHG = trtpn sitegr1'
  custom:eff-dose-response sap '3.3': 2 x at sap.txt lines [296, 300]: ...
  custom:eff-dose-response sap '10.1.1': 3 x at sap.txt lines [588, 625, 643]: ...
  custom:eff-dose-response define 'Table_14-3.01.R.1': in the element True ...: 'randomized dose (0 for placebo; 54 for low dose; 81 for high dose)'
  custom:eff-pairwise sap '10.1.1': 3 x at sap.txt lines [590, 626, 644]: 'If the test for dose response is statistically significant, pairwise comparisons among the 3 groups will be performed'
  custom:eff-pairwise sap '7.3': 1 x at sap.txt lines [403]: 'will only be performed if the test for dose response is significant'
  custom:eff-pairwise sap 'template 5': 5 x at sap.txt lines [1026, 1060, 1104, 1147, 1255]: 'P-value(Xan - Placebo) [1][3]'
  custom:eff-pairwise sap 'template 5, footnote 3': 5 x at sap.txt lines [1036, 1069, 1114, 1157, 1267]: ...
  custom:eff-pairwise define 'Table_14-3.01.R.2': in the element True ...: 'lsmeans trtpn / OM STDERR PDIFF CL'
  custom:eff-lsmeans-weights define 'Table_14-3.01.R.2': in the element True ...
  custom:eff-display-decimals sap 'template 5': 10 x at sap.txt lines [1027, ...]: 'Diff. of LS Means (SE) xx.x(x.xx)'
  custom:eff-display-decimals sap 'template 5': 12 x at sap.txt lines [1028, ...]: '95% CI (xx.xx;xx.xx)'
  (the two quotes of the Define-XML's selection, EFFFL="Y" and ANL01FL="Y" and AVISIT="Week 24",
   are in Table_14-3.01.R.2.SC1: True; "using randomized treatment as class variable" in R.2: True)
R.1 code has 'model CHG = trtpn sitegr1;': True | R.1 mentions base: False
R.2 code has 'model CHG = trtpn sitegr1 base;': True
$ (specfirst.schemas.problems("decision-record", record) on the clone, each record)
custom:eff-analysis-set [] ... custom:eff-display-decimals []   (8 of 8 empty)
```

The first match of each SAP quote lies in the section its anchor names
(3.3 starts at line 291, 6 at 341, 7.1 at 381, 7.3 at 396, 8.1 at 409, 8.2
at 428, 10.1.1 at 582, template 5 at 1003, 15.1 at 1912).

#### D3. The line `build.py` replaced, on the records of 2626186

```text
$ python -I - clone   (Counter(r.get("class") for r in records); sorted(by_class.items()), as at d2e6d8b)
TypeError: '<' not supported between instances of 'NoneType' and 'str'
```

#### D4. The gate, on the clone of 2626186

```text
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 python -m specfirst gate real-5a --clean
  (queued at 08:27 UTC behind another session's clean-clone gates; exit 0 at 08:50; output 531 lines)
== [5/18] unit tests: pytest -m "not evidence" -q
1129 passed, 25 deselected in 325.00s (0:05:25)
...
efficacy: 3 tables, 153 cells; 144 equal the CSR; classified differences: 9 rule_choice
== [14/18] decisions: specfirst.machine.build.decision_checks on build/p1/cdiscpilot01/first
decisions: 8 records, 8 IDs; 45 options of analyses held against the decisions that set them; 0 problems
decisions: by class: 5 document_rule, 2 no class (conflict), 1 study_input; by status: 1 asked, 2 conflict, 5 stated
decisions: pass
...
--- D9-efficacy
unchanged: 0 problems
... (the 7 plants in the reporting event: 19, 3, 26, 8, 3, 109 and 22 problems, as pass 1)
decision records, unchanged: 0 problems
decision records, the ANCOVA without the baseline covariate: 9 problems, for example: custom:eff-model-terms: ars:An_ADAS_W24_Dose has covariates = [], the decision covariates = ['BASE']
... (the 6 plants in the reference and the exceptions: 1, 9, 1, 1, 1 and 1 problems, as pass 1)
61 passed in 75.70s (0:01:15)
...
PASS  environment          0.3 s
PASS  pins                 0.1 s
PASS  lint                 0.0 s
PASS  registry             0.0 s
PASS  unit tests         325.6 s
PASS  method vectors       6.1 s
PASS  kit                  0.1 s
PASS  P1 determinism      38.1 s
PASS  P2 reproduction      0.4 s
PASS  trace                1.1 s
PASS  results              3.2 s
PASS  grids                2.3 s
PASS  efficacy             2.3 s
PASS  decisions            0.4 s
PASS  pilot tests         51.9 s
PASS  planted defects     76.1 s
PASS  cache untouched      0.1 s
PASS  ASCII                0.0 s
GATE real-5a: PASS
$ git -C clone status --short    (empty)
```

#### D5. The check `decisions` with defects planted in the records

`p_decisions.py` calls `build.decision_checks`, the function of the gate
check, on the gate's first build, with `decisions.load` returning the
records of 2626186 with one plant each (in memory):

```text
$ python p_decisions.py clone
control: the records of 2626186: decision_checks returned True; 0 problems
conflict eff-model-terms with covariates []: decision_checks returned False; 12 problems
  e.g. decisions: custom:eff-model-terms: ars:An_ADAS_W24_Dose has covariates = ['BASE'], the decision covariates = []
conflict eff-model-terms with factors ['SITEID']: decision_checks returned False; 12 problems
conflict eff-pairwise with df asymptotic: decision_checks returned False; 6 problems
conflict eff-pairwise with confidence_level 90: decision_checks returned False; 6 problems
conflict eff-model-terms made stated, still without class: decision_checks returned False; 1 problems
  e.g. decisions: custom:eff-model-terms: <root>: 'class' is a required property
asked eff-baseline-rows without class: decision_checks returned False; 1 problems
conflict eff-pairwise binds ars:An_NONE: decision_checks returned False; 1 problems
not held (F4 and the new key): eff-pairwise shown if_significant: decision_checks returned True; 0 problems
not held (F4): eff-display-decimals confidence_limit 1: decision_checks returned True; 0 problems
```

### Answers

#### 1. F1 and F2

**F1 is resolved.** ADR-015 "Consequences" now says every generated kit's
kit.yaml changes (its `registry_sha256`), every reader task folder and its
ID change, the data, gold and documents of a generated kit do not depend on
the new entries ("not checked byte for byte"), and read-2a's kept dry run
fails. Each part holds in the code: `gen/kits.py` pins the registry's hash
(pass 1, C6); `harness/task.py` copies `standard/methods/registry.json`
into every task folder (line 51) and its ID is the hash of the folder's
manifest (lines 113 and 114); the `method_options_hash` of an ARD row is
the hash of that method's resolved options (`registry.py` lines 216 to 218),
so new entries do not reach the rows of a kit that does not use them. The
report's section "Generated kits and reader task folders" says the same.

**F2 is resolved.** Each of the three records now says what its sources say
(D1, D2):

- `custom:eff-model-terms`: status `conflict`, no class (the schema allows
  none for `conflict`, section 4.5 asks for none). It cites both sides:
  SAP 10.1.1, 7.1, 15.1 and R.2's `model CHG = trtpn sitegr1 base` keep
  BASE; R.1's `model CHG = trtpn sitegr1` leaves it out (line 18438; R.1
  has no "base" anywhere). Its statement names the disagreement, says the
  value is the executor's reading under which the CSR is reproduced, and
  that a person decides. The value is unchanged and still held by the
  check `decisions` (12 options, D5).
- `custom:eff-pairwise`: status `conflict`, no class. SAP 10.1.1 is now
  quoted with its condition, SAP 7.3 is cited, and template 5's row
  "P-value(Xan - Placebo) [1][3]" stands for the other side. The value
  gains `shown: always`, which is what the build does; no check reads that
  key (D5) and nothing claims one does.
- `custom:eff-baseline-rows`: status `asked`, class `study_input`, no
  citation. That is section 4.5's `study_input` and the project's own form
  of an asked gold record (`gen/documents.py` lines 355, 356, 684 and 690:
  an asked record has the class `study_input` and cites nothing). The
  nearest text, SAP 10.1.1 "Summary statistics will be generated for each
  visit including baseline", belongs to the by-visit table (template 9,
  sap.txt line 808), not to template 5, so "No document says it" stands.

All 8 records fit the schema (jsonschema and `specfirst.schemas`, D2), and
the schema sees a `stated` record without class and an `asked` one without
class (D2, D5). Every quote of the 8 records is a real quote of its
document, at the anchor it names: each SAP quote's first match is in the
named section, each Define-XML quote is in the element with the named OID
(D2). The other five records are unchanged from `d2e6d8b`.

#### 2. The check `decisions` with the conflict records

It passes and still fails. The gate passes with `--clean` on a fresh
clone of 2626186 with the installed environment (D4), with the new line "by class: 5 document_rule, 2 no
class (conflict), 1 study_input; by status: 1 asked, 2 conflict, 5 stated".
D9's plant (the event without BASE) gives 9 problems, as before; my plants
in the conflict and asked records give 12, 12, 6, 6, 1, 1 and 1 problems
(D5). The change in `build.decision_checks` was needed: the line it
replaced raises a TypeError on records without a class (D3), outside the
`try` of the check, and the gate counts a crashing check as failed
(`gates.py` line 701). The unit tests,
`tests/unit/test_efficacy.py` and `tests/unit/test_gates.py` among them,
pass inside the gate (1129 passed).

#### 3. What the changes introduce; the non-blocking findings of pass 1

Nothing in the diff is wrong in a way that changes a number, a check or a
record's meaning. The non-blocking findings, against what the report and
ADR-015 say:

- F3, F7: in the report's "What the checks do not cover", as pass 1 found
  them. Honest.
- F4: in the same section and in the docstring of `decisions.py`. Which
  records are held is stated rightly; one clause says more (G3 below).
- F5: in the same section, open for real-5b. Honest; it names the LS means
  with one group, not the pairwise comparisons when only the reference has
  records (pass 1, C5), which fail the same way.
- F8: ADR-015, "For the owner", item 4. Honest.
- F9: fixed. The docstring names tests/unit/test_efficacy.py, which plants
  a changed value of a record; the table of tests/defects/README.md is one
  table from D1 to D10 (the empty lines after D6 and D8 are gone).
- F6: neither fixed nor recorded (G1 below).

Findings of this pass, none blocking:

- **G1. F6 is dropped silently.** ADR-015 decision 5, the report (its
  summary and "The methods") and tests/methods/README.md still say that
  `model-vectors` plants defects "in the R implementation". It overwrites
  an option of the inputs (pass 1, F6). Fix the wording, or record F6 with
  the others.
- **G2. The report's gate evidence is of `b8bb1f5`.** It shows
  "decisions: by class: 7 document_rule, 1 study_input", which 2626186 no
  longer prints, and no run covers the change of `build.decision_checks`.
  D4 shows the gate passing on 2626186; the report should carry the
  clean-clone run of the commit that merges (its section "The gates on
  clean clones" is still to be filled).
- **G3. "The decimals are held by the comparison with the CSR and the 9
  exceptions"** (report, F4 item; `decisions.py`: "the decimals are seen by
  the comparison with the CSR and its exceptions"). The comparison holds
  the masks of the reporting event. Of the decision records it reads only
  their IDs (`build.csr_comparison`, `build.py` lines 492 to 494). A record
  `custom:eff-display-decimals` with `confidence_limit: 1` passes
  `decisions` (D5) and the CSR check (pass 1, P2). Say "the decimals the
  event prints are held by the CSR; the record's value is held by nothing".
- **G4. Two smaller points about the conflict records.** (a) The quote of
  R.1, `model CHG = trtpn sitegr1`, is also the start of R.2's line 18472.
  It is true of R.1, but it does not show by itself that BASE is left out.
  The quote with its semicolon, or R.1's "randomized dose ... and site
  group in model", would. (b) `conflict` covers whole records: the 12
  analyses of `eff-model-terms`, where the documents disagree on the 3
  dose-response tests, and every option of `eff-pairwise`, where they
  disagree only on `shown`. This asks more of the owner than needed and
  claims nothing false. When the owner answers, the parts the documents
  agree on can go back to `document_rule`.

#### 4. What is left for the owner (PLAN.md section 2.3)

- **read-2a's kept dry run**: the report states it correctly. "arm R, kept
  dry run" fails on any change of `registry.json`, because the kept task
  pins it and the kit.yaml written again now pins its hash (pass 1,
  question 5; `harness/task.py` lines 51 and 113 confirm that the task's
  files and ID change). The remedies the report lists (a new model run,
  which is the owner's spend and login, or a change of read-2a's gate)
  are the owner's. The executor's option 1 merges with a red check on
  `main`; pass 1 recommends otherwise.
- **N2**: the class `rule_choice` of the 9 cells, together with the labels
  (ADR-015, "For the owner", items 1 and 4).
- **Section 4.5**: the two `conflict` records (the dose-response model;
  showing the pairwise comparisons when the dose response is not
  significant) and the `asked` record (the Baseline rows). Each keeps the
  value the build uses until the owner answers. The answers turn them
  into records that cite the answer, with no change to a cell (both
  readings of the Baseline rows give the same cells; the other answers
  change cells, and D9 shows which).
- The proposals for `catalog@2` go to the std track. Nothing is needed for
  real-5a.

None of these is the executor's to settle, and none blocks this signature.

### Verdict of pass 2

F1 and F2 are resolved. The records say what their sources say, fit the
schema and quote the SAP and the Define-XML truly. The gate passes on a
fresh clone of 2626186 (installed environment, not
`scripts/clean_clone_gate.sh`), and the check `decisions` fails on the defects
planted in the new conflict and asked records. G1 to G4 do not block. The
merge still waits for the owner's choice on read-2a's kept dry run, which
is not a defect of real-5a.

Verdict: SIGNED
