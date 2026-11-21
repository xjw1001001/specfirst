# real-5b-answers review (rule R7)

Reviewer: an independent agent with a fresh context, which did not write the
work. Date: 2026-11-21. Correctness only, no style.

Under review: commit `4660e8c` on branch `track/real` ("real-5b-answers:
carry out the owner's answers of 2026-11-20 (ADR-015)"), against its parent
`2911198`. The owner's four answers as the brief gives them in translation:
(1) the documents against the CSR, "keep as it is"; (2) the five records the
documents leave open or contradict go from conflict/asked to answered with
their current values (`custom:eff-baseline-rows` not in the question); (3)
G2 and K1 of the review of real-5b, "add both", each with its planted
defect; (4) answer 2 recorded as status `stated`, with a class, citing the
answer recorded in ADR-015, schema unchanged. Read: CLAUDE.md; PLAN.md
sections 2, 4.5 and 4.8; ADR-004, "The four open schema points of ADR-000,
item 7"; ADR-015, the amendment of real-5b and "The owner's answers
(2026-11-20)"; standard/schemas/decision-record.schema.json;
docs/reports/real-5b.review.md, G2 (pass 2) and K1 (pass 4); the diff
`2911198..4660e8c` of all 12 files; r/specfirstr/R/models.R (`mmrm_frame`,
`mmrm_emmeans`, `m_mmrm_lsmeans`) and engine.R (`run_model`); ard.Engine,
ars.bind and `_analysis_parameters`, rengine.handover_text;
docs/reports/real-5b-answers.md (its claims checked below).

## Files I quote, with their SHA-256

At `4660e8c` (`git show 4660e8c:<path> | sha256sum`; in my copy of the
clean worktree, made by rsync, `sha256sum` gives the same for the 21 I
hashed there, all but PLAN.md, ADR-004, the review of real-5b, gates.py and
the layout):

```text
9e814eb006075cb56ed841e88d29e2faaaa416395e436d7d6f347b213fb2fe22  docs/decisions/ADR-015.md
9a30538a2f692e4b8e905a9f53488ec1ba663d2d6820fbe6a7459ba7eb54d742  docs/reports/real-5b-answers.md
0ae217e4a5ef0be97763129537fc3b24ec20e035f3a3bc54fef5020f9d057eb1  docs/state/real.md
b26eb797bed664d093e227fbd98f9c29834500c892c8c46fe9e38adc9cccfbe4  docs/reports/real-5a.md
6722ff5e13729f32a274ac66020159352ae19a7206fe0546620007f5f9648398  docs/reports/real-5b.md
8946b62bfa79e42b60ae07197ef647f66dc3cf3bd4ad12266eac83e64d9bcf28  docs/reports/real-5b.review.md
ef4ad14d3c4ca69e9b48ddcff2098bb6b52e3d0c9fec8b0220becf993eccec1f  docs/decisions/ADR-004.md
60ac969b1cbb5d6a956caa769de8d5aceb3261f5b6bedd4035a92b6c941b30ce  PLAN.md
1c606e284d791ef092a029e5b40f4aff4e46e04b2f605cfec4d9517970548bfc  standard/schemas/decision-record.schema.json
d01404828e9c062f5e42234b8956767f6a5b23980776898c726708e687bd5c0f  kits/cdiscpilot01/gold/decisions/efficacy.jsonl
73ebaaa5ac2c2e0df61fc140f51dd487e399b6957acaca9aa9d405b65f85472e  kits/cdiscpilot01/gold/exceptions.yaml
01f290d85220a0d6f83d162f99e6c81a33017fff62d962765e91cc1f5fe9f717  kits/cdiscpilot01/gold/events/efficacy-adas.json
ebb5d5418a33a21b4c1a37caf545e78515571a517ebec834cfe80cad889a5699  kits/cdiscpilot01/gold/events/efficacy-cibic.json
85aa29f0723b031b6aaa9f61cd25e1c94920c9f94a57dcb86b148d33a467024b  kits/cdiscpilot01/gold/layout/Out14-3-13.yaml
3d63aeba2a4bf8b84032ac922b5a51eae5418fe66a1b6efd642036aa3d5aa7e1  src/specfirst/machine/build.py
a8b9d9202bcfbf2c297ee46dd20f0ff68af9f09bcb9b1168be85d18663fd9093  src/specfirst/machine/csr.py
e5c4ca823693399ed3e4f40222eac192fb62ad9c82b5a36dbd0d2c5af688f7a8  src/specfirst/machine/decisions.py
4421a689eef91163da035bd0d90d02bc1c7bb151038f879c5239c053f30aaef9  src/specfirst/machine/ard.py
a366ee9440f6a0dfdfeebad2155d1c197b54b7c77f46afa5115d861d90548d1b  src/specfirst/machine/ars.py
d398218e7e98fc7bb21a646269435127e6d436990c9fa7e701ced36c615f4e2b  src/specfirst/machine/rengine.py
e7e4ef721535b67349b91f20ea2930224aaa8d908b08a06143a05ea17f9a7c5f  src/specfirst/gates.py
287ecd1f099e0ce333d2693225f2daf31f7dd6ca67486051b0bb3799a4d649b2  r/specfirstr/R/models.R
411b457f9c5c167047b00037855742770f85f85c3d39a8fa1ce76097607a64fa  r/specfirstr/R/engine.R
a7052a57f89f159f413ff742f7277812628169f2b7affca1fb916e8817bbf890  tests/defects/test_defects.py
c6f189f70a18c502ccbcbd9e89c16588f130b2efc50f2c84d38bbb768adb536f  tests/unit/test_efficacy.py
ac1c6a6b5e05910bdab79519e96b3457b6876c943b9e0d06541a7ab5bc31fffc  tests/unit/test_efficacy_5b.py
```

At `2911198` (the parent's files I put in place of the new ones to run
"without the change"):

```text
f4f9591a764d443defe9c48e42c57c8653ea3d23a8f57e5314a94a82adbc9b3f  src/specfirst/machine/csr.py
46fbff426c09cd48c050019e2faae9a251d9725dcc225e9aa00bb1deee812a2d  src/specfirst/machine/decisions.py
bc9f3b91e866037152b49c3f90cd05c4040141e1d0a09b73d8f999a0c1798e1b  src/specfirst/machine/build.py
650a344f128c03a51425bdcedc438f5f16af2f782b118b244cd2ccf0f2171a51  kits/cdiscpilot01/gold/decisions/efficacy.jsonl
```

My scripts, in my session's temporary folder (not in the checkout):

```text
991558f697bbab6c3e7373883236a8b58326508eb696c2f0b9004d5c41947e44  review.py  (build, checks, records, G2)
aa336cf510ee062b73445e3498e5450e8d26beecbb1bbab6c6fe6517a2a574eb  frame.R    (engine.R's run_model and mmrm_frame, no fit)
e5a9a7707626bf5118558990f38540373d3a36918a42e446223d0d32c99eeacd  k1.py      (K1)
28b4d54a77e3c417db2bb7bed7802d7c0c81be6732b4ad0d7dc200b26ab262af  k1dec.py   (the check decisions on two K1 cases)
2c1303c514e52df9b78e3721daded974dc34e2ce513ac7e1fcbe8d3065deee90  d911.sh
9dae7b5bc17f6e5d14e2919129231721ad41474fbfcdd1b68aa8ce287c9b67d1  run2.sh
511778ea0c2dbcca0178a842f8c5092b11e4138af8f67e853d7a20e4277ee824  run3.sh
b34361c1f1411288b613509652f0fde295e22adbed0c5cce4c4d4c134892ae95  run4.sh
a2ca362d6306d083143aedd0b0af95847d548e743d6f36beed21ae876244eb00  verify.sh
f4cbf26fafcac40f02697ca63c59d86d659edec4278e200f428be96e14e0f761  ascii.py
```

CSR text below is CDISC material: I quote only the cells a finding needs.

## Commands I ran, with their output (rule R8)

Setup: WSL Ubuntu-24.04 as root, the worktree's environment
(`. /mnt/d/trial_work/specfirst-real/scripts/env.sh`), my copy
`/root/scratch-review-answers/wt/` made by the brief's rsync (600 files; the
worktree was clean at `4660e8c`), `SPECFIRST_ROOT` and `PYTHONPATH` set to
the copy. Two more copies for "without the change": `old-csr/` (the copy
with the parent's csr.py) and `old-code/` (the parent's csr.py, decisions.py
and build.py, the new tests). Every test suite, build and defects run under
`flock /run/lock/specfirst-heavy.lock taskset -c 0-3`. The build and the
parsed CSR pages are under the copy's `build/` only. No gate and no
clean-clone script was run; nothing was written into the checkout but this
file, and nothing into the fetch cache (C10). No model ran.

### C1. D9 and D11 on my copy of 4660e8c

```text
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 env SPECFIRST_STRICT=1 python -m pytest -p no:cacheprovider -q -s tests/defects -k 'D9 or D11'
--- D9-efficacy
unchanged: 0 problems
planted, the ANCOVA without the baseline covariate: 19 problems, ...   (7 plants of the event, each seen)
decision records, unchanged: 0 problems
decision records, the ANCOVA without the baseline covariate: 9 problems, for example: custom:eff-model-terms: ars:An_ADAS_W24_Dose has covariates = [], the decision covariates = ['BASE']
...                                                                      (6 plants of references and exceptions, each seen)
--- D11-efficacy-5b
unchanged, efficacy-adas: 0 problems
unchanged, efficacy-cibic: 0 problems
...                                                                      (13 plants of the events, each seen)
decision records, unchanged: 0 problems
decision records, gold takes the LS means averaged over the weeks: 3 problems, for example: custom:eff-mmrm-visit: ars:An_ADAS_MMRM_LSM has at = 'average', the decision rule = 'last'
decision records, the CMH test of general association: 3 problems, for example: custom:eff-cmh: ars:An_CIBIC_W08_Cmh has statistic = 'general_association', the decision rule = 'row_mean_scores'
decision records, the visits by AVISIT, in custom:eff-mmrm-terms and the six analyses alike (G2): 3 problems, for example: custom:eff-mmrm-visit: the last visit of the model records of ars:An_ADAS_MMRM_LSM is AVISIT = 'Week 8', where AVISIT is ['Week 8']; the
decision records, custom:eff-mmrm-visit names Week 16 as the last week (G2): 3 problems, for example: custom:eff-mmrm-visit: the last visit of the model records of ars:An_ADAS_MMRM_LSM is AVISITN = '24', where AVISIT is ['Week 24']; the decision names AVISIT =
...                                                                      (14 plants of references and exceptions, each seen)
planted, gold's week 8 CMH without its strata, proved by the analysis with them (K1): 1 problems, for example: Out14-3-13: cell:Out14-3-13/r2/c4: ours '0.264', CSR '0.2727': the proof does not hold: An_CIBIC_W08_Cmh_Site differs from An_CIBIC_W08_Cmh in an opt
2 passed, 61 deselected in 53.59s
```

The lines of the report's section "Planted defects" are these, word for
word (cut at other places).

### C2. The gate's checks `decisions` and `efficacy` on my build (review.py, sections 0 and 1)

```text
== 0. specfirst build cdiscpilot01 (in the copy)
build exit 0; 24 lines; last: build cdiscpilot01: 10 datasets, 1576 nodes, 5251 edges, 56 files in /root/scratch-review-answers/wt/build/kits/cdiscpilot01
== 1a. build.decision_checks (the gate's check `decisions`)
decisions: 18 records, 18 IDs; 99 options of analyses held against the decisions that set them; the last visit held on the model records of 3 analyses; 0 problems
decisions: by class: 15 document_rule, 3 study_input; by status: 1 asked, 17 stated
decisions: pass
== 1b. build.display_checks (the gate's check `efficacy`)
grid Out14-3-01 against CSR Table 14-3.01: 51 cells, 40 of them printed in the CSR; 48 equal the CSR, 3 differ, 3 of them with one class and a proof that holds
grid Out14-3-03 against CSR Table 14-3.03: ... 3 differ, 3 of them with one class and a proof that holds
grid Out14-3-05 against CSR Table 14-3.05: ... 3 differ, 3 of them with one class and a proof that holds
grid Out14-3-11 against CSR Table 14-3.11: 24 cells, 15 of them printed in the CSR; 12 equal the CSR, 12 differ, 12 of them with one class and a proof that holds
grid Out14-3-13 against CSR Table 14-3.13: 100 cells, 78 of them printed in the CSR; 76 equal the CSR, 24 differ, 24 of them with one class and a proof that holds
grid <each>: the R engine's rows give the same grid; the mock shell and the two pages hold; 0 problems
grids: 6 outputs, pass
```

The first line of 1a is the line the report's section G2 leaves for the
gate ("the last visit held on the model records of 3 analyses").

### C3. The records (review.py, section 2)

```text
18 records (old 18); jsonschema errors 0; schemas.problems 0; same ids in the same order: True
custom:eff-model-terms: changed ['citations', 'class', 'statement', 'status']; status conflict -> stated; class None -> document_rule; value same True; binds same True; old citations kept True; added [('answers', "ADR-015, The owner's answers (2026-11-20), item 2")]
custom:eff-pairwise: changed [... the same four]; status conflict -> stated; class None -> document_rule; value same True; binds same True; old citations kept True; added [('answers', ...)]
custom:eff-mmrm-records: changed [... the same four]; status conflict -> stated; class None -> document_rule; value same True; binds same True; old citations kept True; added [('answers', ...)]
custom:eff-mmrm-df: changed [... the same four]; status asked -> stated; class gold_quirk -> study_input; value same True; binds same True; old citations kept True; added [('answers', ...)]
custom:eff-mmrm-visit: changed ['statement', 'value']; status stated -> stated; class document_rule -> document_rule; value same False; binds same True; old citations kept True; added []
   value {"rule": "last"} -> {"rule": "last", "label": "AVISIT", "last": "Week 24"}
custom:eff-cmh: changed [... the same four]; status asked -> stated; class gold_quirk -> study_input; value same True; binds same True; old citations kept True; added [('answers', ...)]
answer quotes ['the owner answers as the person section 4.5 asks']; each in ADR-015 (blanks folded): True
```

The other 12 records are byte for byte the parent's.

### C4. G2: the check `decisions`, new against the parent's decisions.py (review.py, section 3a)

The parent's `decisions.problems` takes no engines; both are run on the same
events and records. "mine" marks plants of my own.

```text
unchanged: new 0 problems, old 0
visits by AVISIT, record of the terms and six analyses (D11 plant 1): new 3 problems, old 0; new e.g. custom:eff-mmrm-visit: the last visit of the model records of ars:An_ADAS_MMRM_LSM is AVISIT = 'Week 8', where AVISIT is ['Week 8']; the decision names AVISIT = 'Week 24'
the record names Week 16 (D11 plant 2): new 3 problems, old 0; ...
mine: the mixed model's subset without Week 24 (all six analyses): new 3 problems, old 0; new e.g. ... is AVISITN = '16', where AVISIT is ['Week 16']; the decision names AVISIT = 'Week 24'
mine: the record of the visit {rule: last} without label and last: new 1 problems, old 0; new e.g. custom:eff-mmrm-visit: the rule last names no visit (a column `label` and its value `last`)
mine: the record names a column no analysis reads (label VISIT): new 3 problems, old 0; new e.g. custom:eff-mmrm-visit: ars:An_ADAS_MMRM_LSM: dataset ADQSADAS has no column VISIT
mine: the record binds An_ADAS_MMRM_LSM only; visits by AVISIT as plant 1: new 1 problems, old 0; ...
```

### C5. G2: the model records by a route of my own (review.py, section 3b)

pandas on the built adqsadas.parquet and adsl.parquet, with the analysis
set and the data subset of the event written out by hand (EFFFL = Y on
ADSL; PARAMCD = ACTOT, AVISIT in weeks 8, 16, 24, ANL01FL = Y, DTYPE
missing), then CHG, AVISITN, BASE, SITEGR1, USUBJID present and TRT01PN in
the three groups:

```text
pandas: 539 model records, 234 subjects; by AVISITN {8.0: 234, 16.0: 150, 24.0: 155}; last AVISITN 24.0 with AVISIT ['Week 24']; by text the last is Week 8
An_ADAS_MMRM_LSM: model_records 539, the same (subject, visit) pairs as pandas: True; last_visit ('24', ['Week 24'])
An_ADAS_MMRM_PwPbo: model_records 539, the same (subject, visit) pairs as pandas: True; last_visit ('24', ['Week 24'])
An_ADAS_MMRM_PwLow: model_records 539, the same (subject, visit) pairs as pandas: True; last_visit ('24', ['Week 24'])
```

### C6. G2: Python against R's own frame, on planted data (review.py, section 3c; frame.R)

frame.R sources r/specfirstr/R/{util,methods,models,engine}.R, sets up the
engine as `run_job` does, takes the analysis records and the inputs as
`run_model` does (analysis set, data subset, `members`, `eng_text`,
`eng_numbers`, the visit by its kind) and calls `mmrm_frame`; it prints the
number of model records and `tail(m$visits, 1)` and writes the (subject,
visit) pairs. The data are handed over by `rengine.handover_text`, as the
build does. Planted in the Table objects before both engines see them: 8
records each without CHG, BASE, SITEGR1 and AVISITN and 4 without USUBJID
(seeded draw), and CHG missing on every Week 24 record.

```text
unchanged data, visit AVISITN, An_ADAS_MMRM_LSM: R 539 records, last '24'; Python 539, last '24', AVISIT there ['Week 24']; same pairs True
missing CHG, BASE, SITEGR1, AVISITN and USUBJID on 36 records, An_ADAS_MMRM_LSM: R 514 records, last '24'; Python 514, last '24', AVISIT there ['Week 24']; same pairs True
CHG missing on every Week 24 record, An_ADAS_MMRM_LSM: R 384 records, last '16'; Python 384, last '16', AVISIT there ['Week 16']; same pairs True
unchanged data, visit AVISIT (text), An_ADAS_MMRM_LSM: R 539 records, last 'Week 8'; Python 539, last 'Week 8', AVISIT there ['Week 8']; same pairs True
missing values as above, visit AVISIT (text), An_ADAS_MMRM_LSM: R 520 records, last 'Week 8'; Python 520, last 'Week 8', AVISIT there ['Week 8']; same pairs True
(the same for An_ADAS_MMRM_PwPbo and An_ADAS_MMRM_PwLow: 15 of 15 lines with the same pairs)
```

### C7. K1 (k1.py, on the build of C2; Python engine only)

```text
== 4a. K1: pass 4's O2 (gold's week 8 p-value is week 16's; an other analysis with searched strata and rank scores; a CSR that printed its p-value)
the searched analysis: ard:An_CIBIC_W16_Cmh_S/Mth_Cmh_1_pval/* = 0.2728159428756223, shown 0.2728
control, the wrong gold without the proof: 1 problems: Out14-3-13: cell:Out14-3-13/r2/c4: ours '0.400', CSR '0.2728': the proof does not hold: ...
new csr.py: 1 problems: Out14-3-13: cell:Out14-3-13/r2/c4: ours '0.400', CSR '0.2728': the proof does not hold: An_CIBIC_W16_Cmh_S differs from An_CIBIC_W16_Cmh in an option whose values are columns (strata): an other analysis may differ only in the options of custom:eff-cmh, custom:eff-cibic-display that take no colum
old csr.py: 0 problems
== 4b. K1: other analyses of 14-3.11 that differ in a column-valued option
factors SITEGR1, SEX, entry names ['custom:eff-mmrm-visit', 'custom:eff-mmrm-terms']: 1 problems: An_ADAS_MMRM_LSM_Avg_K1 differs from An_ADAS_MMRM_LSM in an option whose values are columns (by_visit, covariates, factors, visit): ...
factors SITEGR1, SEX, entry names custom:eff-mmrm-visit: 1 problems: An_ADAS_MMRM_LSM_Avg_K1 differs from An_ADAS_MMRM_LSM in more than the options at of custom:eff-mmrm-visit
covariates none / visit AVISIT / by_visit none: the same two answers each (6 lines)
== 4c. K1: the 12 genuine proofs of 14-3.11, each also naming custom:eff-mmrm-terms
0 problems
```

And the check `decisions` on two K1 cases (k1dec.py, `nice`, Python only):

```text
$ nice python k1dec.py
decisions, D11's K1 plant: 1 problems: custom:eff-cmh: ars:An_CIBIC_W08_Cmh has strata = [], the decision strata = ['SITEGR1']
decisions, O2 of pass 4: 0 problems
```

### C8. Without the change: D11 with the parent's csr.py, and the new unit tests on the parent's code

```text
$ SPECFIRST_STRICT=1 python -m pytest -p no:cacheprovider -q -s tests/defects -k D11   (old-csr)
planted, gold's week 8 CMH without its strata, proved by the analysis with them (K1): 0 problems
E       AssertionError: gold's week 8 CMH without its strata, proved by the analysis with them (K1): not seen
E         gold's week 8 CMH without its strata, proved by the analysis with them (K1): not seen by the rule of K1
1 failed, 62 deselected in 38.99s
$ python -m pytest -p no:cacheprovider -q <the three new unit tests>   (wt)
3 passed in 0.43s
$ python -m pytest -p no:cacheprovider -q <the three new unit tests>   (old-code)
E       AttributeError: module 'specfirst.machine.decisions' has no attribute 'LAST_VISIT'
E       AttributeError: module 'specfirst.machine.decisions' has no attribute 'model_records'
E       AssertionError: []      (test_an_other_analysis_may_not_differ_in_an_option_whose_values_are_columns, line 182)
3 failed in 0.40s
$ python -m pytest -p no:cacheprovider -q tests/unit/test_efficacy.py tests/unit/test_efficacy_5b.py   (wt)
74 passed in 0.99s
```

### C9. The unit tests and ruff on my copy

```text
$ flock ... taskset -c 0-3 python -m pytest -p no:cacheprovider -q tests/unit
FAILED tests/unit/test_asciicheck.py::test_this_repository_is_ascii - Runtime...
FAILED tests/unit/test_gen_natural.py::test_the_store_in_a_checkout_takes_no_secret_statement
FAILED tests/unit/test_kit.py::test_the_repository_tracks_no_study_data - Run...
FAILED tests/unit/test_layout.py::test_text_files_have_lf_endings - RuntimeEr...
4 failed, 1149 passed in 329.99s (0:05:29)
$ ruff check <the six changed Python files>
All checks passed!
```

The four failures are the four of the brief ("git ls-files failed ... not a
git repository"); the report has the same line.

### C10. ASCII, LF, what the commit leaves alone, the fetch cache

```text
$ python3 ascii.py /root/scratch-review-answers/wt <the 12 changed files>
docs/decisions/ADR-015.md: 28584 bytes, non-ASCII bytes 0, CR bytes 0, ends with LF True
... (the same "non-ASCII bytes 0, CR bytes 0, ends with LF True" for all 12)
$ git diff --stat 2911198 4660e8c -- standard/ src/specfirst/harness/ src/specfirst/gen/ kits/ env/ r/ PLAN.md CLAUDE.md .github/
 kits/cdiscpilot01/gold/decisions/efficacy.jsonl | 12 ++++++------
 1 file changed, 6 insertions(+), 6 deletions(-)
$ git show -s --format="%h %p %s" edeea2c
edeea2c 7806105 2911198 Merge track/real: real-5b, Tables 14-3.11 and 14-3.13 (gates passed, review signed)
$ nice python -m specfirst fetch --verify        (after all my runs)
fetch: every pin verified
```

## Answers to the six questions

### 1. G2: the model records and the last visit as models.R takes them; the gate

Yes, exactly, for every case I could build. By reading: `model_records`
takes the analysis set and the data subset as `ard.Engine._analysis` and
engine.R's rule I6 do; drops a record without a value of the analysis
variable, the subject key, the visit, a factor or a covariate, a number by
NaN and a text by "" (the hand-over turns both into R's NA and "", which
`mmrm_frame` drops the same way, a numeric factor as text included); keeps
a record in a group of the grouping (R: `group %in% groups`, the members of
the same where clauses). `last_visit` orders as numbers when the column is
a number column and by characters otherwise; Python's `str` order is code
point order, R's radix sort in the C collation is byte order, the same for
UTF-8. The kinds are the Table's, which `rengine.handover_text` hands to R,
so a text and a number visit column cannot be read differently by the two.
By running: on the pilot 539 model records, the same (subject, visit) pairs
as a pandas route of my own (C5) and as R's own `mmrm_frame` reached
through engine.R's code (C6), also with missing values planted in every
column the frame reads, with every Week 24 record losing CHG (last visit 16
on both sides) and with the text visit AVISIT (Week 8 on both sides). The
three analyses the record binds have one registry method each (R refuses
more), and `by_visit`, a column the frame does not filter on, is left out
on both sides. Where R stops (a record in two groups, two records of one
subject at one visit, a text covariate) Python takes records, but the build
fails first, so no gate reaches the check.

The check runs in the gate: `gates._decisions` calls
`build.decision_checks` on the gate's first build, which now builds a
Python engine per result set on that build's ADaM data and hands it over;
on my build it holds the last visit of 3 analyses, 0 problems (C2). A
record of the visit does not pass unseen in any way I found (C4): a value
without `label` or `last`, a column the engines were not handed, an
analysis without data, a call without engines, a missing record or one
whose rule disagrees with `at` are each a problem. What it holds is
limited to the analyses the record binds (C4, last line: with LSM alone
bound, PwPbo and PwLow are not held), as every record of decisions.py is;
the report's "What the checks do not cover" says the other visits are held
by nothing.

### 2. K1: what an other_build proof can still do; the genuine entries

The rule is as asked. The options an entry's decisions set are split into
those whose values are columns (`ars.MODEL_TERMS`, which the registry
makes the only names an option that takes columns may have) and the
others; an other analysis must equal the cell's with only the others
stripped, so any difference in a column-valued option, alone or with a
free one, is refused; an option no named decision sets is compared as
before. The binding cannot carry the difference instead: its options are
per registry method, so they reach the cell's and the other analysis
alike, and `methodId`, the sets, subsets, groupings and the dataset are
compared. Pass 4's O2 (a searched strata set with rank scores for the
wrong gold B2, against a CSR printing its p-value 0.2728) passes the
parent's csr.py and is refused by the new one (C7, 4a); other factors,
covariates, visit or by_visit for 14-3.11 are refused under either message
(4b). I found no other way to bring other columns into an other analysis.
No genuine entry is refused: the 45 proofs hold in the gate's check (C2),
D9 and D11 pass on the unchanged inputs (C1), and only the 12 of 14-3.11
name an other analysis, which differs in `at` alone; they hold even with
`custom:eff-mmrm-terms` named too (4c). The message lists every column
option of the named decisions, not the one that differs ("(by_visit,
covariates, factors, visit)" for a change of factors); that is wording.

### 3. The plants and the unit tests

Each is seen by the new code and not by the old. D11's two G2 plants: 3
problems each with the new decisions.py, 0 with the parent's (C4); D11's
K1 plant: seen and named by the K1 rule with the new csr.py, "not seen"
with the parent's (C1, C8). The unchanged inputs give 0 problems in D9 and
D11 (both the event checks and the records), and in the gate's checks on
my build (C1, C2). The three new unit tests pass on the new code and fail
on the parent's: two because the names they test do not exist, the K1 one
by its assertion (C8); the G2 unit test's three cases (numbers, text, a
missing factor) are the ones C6 confirms against R. D9 changed only to
hand over the engines. One limit, finding L3: D11's K1 wrong gold is also
caught by the check `decisions`, which O2 is not.

### 4. The five records

They match answers 2 and 4: the five keep their values and binds and all
their citations, each adds the one citation of the answer (doc `answers`,
anchor "ADR-015, The owner's answers (2026-11-20), item 2", a quote that is
a line of ADR-015), and each is `stated` with a class: the three former
conflicts `document_rule`, `custom:eff-mmrm-df` and `custom:eff-cmh`
`study_input`; `custom:eff-baseline-rows` stays `asked` (C3). All 18
validate with jsonschema (Draft 2020-12) and with `schemas.problems`. With
PLAN.md 4.5: a conflict now has the person's answer before its class, as
4.5 asks; `study_input` ("a person supplies it") is what the two former
gold quirks now are, and the answer citation is ADR-004 point 3's form for
a study input, with ADR-015's section in place of the ID of an ask (there
was none), as answer 4 says. `document_rule` for the three conflicts is the
executor's choice of class (answer 4 names none); each cites the document
whose reading the owner took, so the record meets the schema's rule for a
document_rule. The only other record changed is `custom:eff-mmrm-visit`,
for G2 (value and statement; status, class, citations, binds kept).

### 5. ADR-015, the report, the state, the notes

Accurate against the code and my runs, but for small things (L1, L2, L4).
ADR-015's section "The owner's answers" states the four answers, the table
of the five records and the two rules as the code has them. Its first
paragraph and its "For the owner" of real-5a say items 1 to 4 of real-5a
are answered; item 3 is not (L1). The report's records, plants, outputs,
unit tests and "without K1" agree with C1, C3, C8 and C9; its gate lines
are left as placeholders, and C2 has the line of the check `decisions`
(L4). docs/state/real.md moves the answered items out of "Open" correctly,
but its "Handed over by real-5b" still gives the other_build rule without
K1 (L2). The notes in real-5a.md and real-5b.md point to the answers and
are right. All 12 changed files are ASCII with LF endings (C10).

### 6. What the commit must not change

It changes none of them: no file under standard/ (so not the registry), no
file of src/specfirst/gen or src/specfirst/harness (so not read-2a's kept
run), no generated kit, no env/ and no R code; under kits/ only the
pilot's records (C10). The changed machine code is reached only by the
check `decisions` and by CSR proofs, which no generated kit has.

## Findings

### L1 (does not block): ADR-015 says item 3 of real-5a is answered

Where: docs/decisions/ADR-015.md, the status paragraph ("The owner answered
items 1 to 4 of real-5a") and the first line of "For the owner (N2, not
blocking real-5a)" ("Items 1 to 4 are answered ...; item 5 is open").

What: item 3 is `custom:eff-baseline-rows`, which was in no question and
stays `asked`, as the same ADR's answer 2, the report and docs/state/real.md
say. The answered items of real-5a are 1, 2 and 4.

Fix: "items 1, 2 and 4 of real-5a"; "items 3 and 5 are open".

### L2 (does not block): the handover and a docstring describe the checks as they were

Where: docs/state/real.md, "Handed over by real-5b", the item on
`other_build`; src/specfirst/machine/decisions.py, docstring, "A changed
parameter in the reporting event, or a changed value in a record, is seen
by the last rule".

What: the handover still says an other analysis differs "only in its
naming and in the options its decisions set (`decisions.PARAMETERS`)",
without K1's refusal of column-valued options, and says nothing of the
check of the last visit and its need of the built data; the report says a
new session takes the track from here. In the docstring "the last rule" was
the rule of `PARAMETERS`; with `LAST_VISIT` added after it, it now names
the wrong rule.

Fix: add K1 and G2 to the handover item; "seen by the rule of
`PARAMETERS`".

### L3 (does not block): D11's K1 plant is not a case only the K1 rule sees

Where: tests/defects/test_defects.py, D11, the plant "gold's week 8 CMH
without its strata, proved by the analysis with them (K1)".

What: the plant counts for the rule (rule R5): it asks for the rule's own
message, and the parent's csr.py passes it (C8). But its wrong gold also
fails the check `decisions` (`custom:eff-cmh` binds An_CIBIC_W08_Cmh, whose
strata become [], C7), so in the gate it was never past every check. Pass
4's O2 is the case K1 was about: `decisions` gives 0 problems on it and the
parent's csr.py accepts its proof (C7), and only the count of the gate's
check `CMH` stopped it before K1.

Fix (optional): add O2 as a D11 plant (the layout's week 8 p-value from
An_CIBIC_W16_Cmh, the added analysis with strata RACEN, SEX, QSSEQ and rank
scores, the CSR cell at its p-value), asking for the K1 message.

### L4 (does not block): the report waits for its gate lines; one sentence is loose

Where: docs/reports/real-5b-answers.md, "Verdict", "G2: the last visit of
the mixed model" (the line of the check `decisions`), "The gates on clean
clones"; "K1", "The genuine proofs of real-5b differ only in options that
take no columns (`at` ...; the CMH display)".

What: the placeholders are expected (the author runs the gates after the
commit); the line of the check `decisions` on my build is in C2. Of the 45
genuine proofs only the 12 of 14-3.11 name an other analysis; those of
14-3.13 name none, so they "differ" in no option.

Fix: fill in the lines from the clean clones; "the 12 proofs of 14-3.11
differ only in `at`; the others name no other analysis".

## The owner's choices (PLAN.md section 2.3)

Nothing new blocks. Two points the owner may want to know, with my
recommendation:

1. **The class of the three former conflicts.** Answer 4 asks for "a
   class" and names none; the executor gave `document_rule`, since each
   value is a reading a document states (SAP 10.1.1, template 5, template
   10). `study_input` would say instead that a person supplied the choice
   between the documents. PLAN.md 4.5 scores the two differently once a
   reader is scored on these records ("yes" against "as a question
   asked"). Recommendation: keep `document_rule`, and decide the scoring of
   a record whose documents contradict when real data are first scored.
2. **What K1 costs.** An alternative of a record whose values are columns
   (another set of model terms, other strata) can no longer be proved by an
   other analysis. No entry of the pilot needs one; the report says so.
   Recommendation: accept, as the owner did.

## Verdict

G2 and K1 are carried out as the owner's answer 3 asks, and each holds:
the check `decisions` takes the model records and the last visit as
models.R does (the same records as R's own frame and as a pandas route,
with missing values planted, with a text visit and with Week 24 emptied;
C5, C6), runs in the gate on the built data and holds 3 analyses with 0
problems on the pilot (C2), and no record of the visit passed unseen in my
plants (C4); the K1 rule refuses an other analysis in other columns, pass
4's O2 included, and no genuine proof (C7). Each plant and unit test is
seen by the new code and not by the parent's, and the unchanged inputs give
0 problems (C1, C4, C8). The five records follow answers 2 and 4 with
their values unchanged, validate, and fit PLAN.md 4.5 and ADR-004 point 3;
only `custom:eff-mmrm-visit` changes besides (C3). Nothing under
standard/, the generator, the harness or env/ changes (C10). The findings
L1 to L4 are wording and one optional plant; none blocks.

Verdict: SIGNED
