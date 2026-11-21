# real-5b-answers The owner's answers of 2026-11-20 on real-5a and real-5b: report

Date: 2026-11-20 and 2026-11-21. Branch: `track/real`. A small part of the
slice `efficacy-first` (ADR-012), after real-5b (merged, `edeea2c`). It
carries out three answers of the owner to the items "For the owner" of
real-5a and of the amendment of real-5b, and a fourth on how to record the
second. The answers came through the base session, quoted word for word
from its question dialog. Decisions: the section "The owner's answers
(2026-11-20)" at the end of docs/decisions/ADR-015.md. PLAN.md,
`standard/schemas/`, `standard/methods/`, `env/` and the kept run of arm R
are not changed. No model ran and nothing was spent.

## Verdict

The gates passed. `scripts/clean_clone_gate.sh` exited 0 for each of the
nine gates, on clean clones of commit `4660e8c` with a fresh install and a
fresh fetch: real-5b (19 of 19 checks), read-2a (19 of 19, the kept dry run
of arm R among them), real-5a, real-3a, real-2, gen-2a, gen-3a, read-1a and
std-1 (section "The gates on clean clones"). The review is signed
(section "Review").

- Answer 1 (the documents against the CSR): nothing changes. The 45
  differences of the five efficacy tables stay `rule_choice`, each with its
  proof, and the row labels stay the CSR's.
- Answer 2 (the records the documents leave open or contradict), recorded
  as the owner's fourth answer says: five records keep their values and
  become `stated`, with a class and a citation of the answer. No number
  of the build changes.
- Answer 3 (G2 and K1 of the review of real-5b): both are closed.
  - G2: the check `decisions` now holds the last visit of the model
    records against `custom:eff-mmrm-visit`, which names Week 24.
  - K1: an `other_build` proof now refuses an other analysis that differs
    in an option whose values are columns.
  - Each has its planted defect (rule R5), and each plant is seen.
- The review is signed in its first pass; none of its four findings
  blocks (section "Review").

## The answers

The owner answered in Chinese; this file stays ASCII (rule R10), so each
answer is a translation, with the option as the base session translated
it. ADR-015 has each in full.

| Question | Answer | The option |
| --- | --- | --- |
| 1. The documents against the CSR (real-5a items 1 and 4; real-5b items 1 and 5) | "[in Chinese: keep as it is] (Recommended)" | "format and computation follow the documents, row labels stay the CSR's, no change." |
| 2. The records the documents leave open or contradict (real-5a item 2; real-5b item 2) | "[in Chinese: decide by the reading that reproduces the CSR] (Recommended)" | "the owner answers as the person section 4.5 asks: these records go from conflict/asked to answered, with their current values; the numbers do not change." |
| 3. G2 and K1 of the review of real-5b (real-5b items 6 and 7) | "[in Chinese: add both] (Recommended)" | "the real track adds a check and tightens the proof rule; no model, no spend." |
| 4. How to record answer 2, given that schema v0 has no status "answered" | "[in Chinese: record as stated, cite your answer] (Recommended)" | "status stated, with a class, and the citation points to the owner's answer recorded in ADR-015. The schema is not changed." |

Question 4 came from this part. The status enum of
`decision-record.schema.json` is `stated`, `default`, `asked`, `conflict`
and `not_applicable`; adding "answered" would change `standard/schemas/`,
which needs an ADR the owner approves. The base session put the question
to the owner.

`custom:eff-baseline-rows` (real-5a item 3) was in no question and stays
`asked`. Not in the questions, and so as they stood:

- real-5a item 5 and the proposals of real-5b for `catalog@2`;
- real-5b item 3, the Toeplitz fallback (not implemented);
- real-5b item 4, the gate real-5a counting its own three tables.

## The five records (answer 2)

In `kits/cdiscpilot01/gold/decisions/efficacy.jsonl`:

| Record | Was | Now | The documents whose reading the owner took |
| --- | --- | --- | --- |
| `custom:eff-model-terms` | `conflict` | `stated`, `document_rule` | the SAP's: BASE in the model of the dose response too (SAP 10.1.1; the Define-XML's code R.2 against R.1) |
| `custom:eff-pairwise` | `conflict` | `stated`, `document_rule` | template 5's: the comparisons shown whatever the dose response gives (against SAP 7.3) |
| `custom:eff-mmrm-records` | `conflict` | `stated`, `document_rule` | the observed records of SAP 10.1.1 and template 10, no LOCF (against SAP 8.1) |
| `custom:eff-mmrm-df` | `asked`, `gold_quirk` | `stated`, `study_input` | none: no document names a method; the owner supplies Kenward-Roger |
| `custom:eff-cmh` | `asked`, `gold_quirk` | `stated`, `study_input` | none: "Pearson Chi-Square" read as the name of no CMH statistic; the owner supplies row mean scores |

Each record:

- keeps its value and its binds;
- keeps its citations of the documents, both sides of a conflict among
  them;
- adds one citation of the answer: `{"doc": "answers", "anchor": "ADR-015,
  The owner's answers (2026-11-20), item 2", "quote": "the owner answers as
  the person section 4.5 asks"}`. The quote is a line of ADR-015. The doc
  `answers` is the one ADR-004's open schema point 3 gives a person's
  answer; the owner took that point at N1;
- has its statement end with the owner's decision in place of "a person
  decides" or "Asked of the owner".

The records after the change, by a short script: it validates every
record with `decision-record.schema.json` (jsonschema, Draft 2020-12) and
prints the seven records of this part and of question 2:

```text
$ python records_show.py /mnt/d/trial_work/specfirst-real
18 records, schema errors 0
custom:eff-model-terms: stated, document_rule, citations ['sap', 'sap', 'sap', 'define-adam', 'define-adam', 'answers']
custom:eff-pairwise: stated, document_rule, citations ['sap', 'sap', 'sap', 'sap', 'define-adam', 'answers']
custom:eff-baseline-rows: asked, study_input, citations []
custom:eff-mmrm-records: stated, document_rule, citations ['sap', 'sap', 'sap', 'answers']
custom:eff-mmrm-df: stated, study_input, citations ['answers']
custom:eff-mmrm-visit: stated, document_rule, citations ['sap', 'sap']
  value {"rule": "last", "label": "AVISIT", "last": "Week 24"}
custom:eff-cmh: stated, study_input, citations ['sap', 'sap', 'sap', 'answers']
```

## G2: the last visit of the mixed model

The value of `custom:eff-mmrm-visit` was `{rule: last}`. It is now
`{rule: last, label: AVISIT, last: Week 24}`. The check `decisions` of the
gate (`specfirst.machine.decisions`, `LAST_VISIT`) holds every analysis the
record binds, in four steps:

1. It takes the model records as models.R takes them (`model_records`):
   - the analysis set and the data subset;
   - a value of the analysis variable, the visit, the subject key and
     every factor and covariate;
   - a group of every grouping.
2. It orders the visits as models.R does (`last_visit`): as numbers, or by
   their characters.
3. It takes the last visit.
4. It asks that every model record of that visit has AVISIT = Week 24.

The check needs the built ADaM data. `specfirst.machine.build` now hands
the check its Python engines. Without them, a record of the visit is a
problem ("none was handed over"): it cannot pass unseen.

On the pilot, all three analyses at Week 24 are held:

```text
$ specfirst gate real-5b    (in the clean clone of 4660e8c; docs/reports/real-5b-answers.clean-clone.gate.log)
decisions: 18 records, 18 IDs; 99 options of analyses held against the decisions that set them; the last visit held on the model records of 3 analyses; 0 problems
PASS  decisions            0.6 s
```

## K1: an other analysis in other columns

An `other_build` proof names an other analysis per analysis of the cell. In
real-5b that analysis could differ from the cell's in any option that the
entry's decision records set. Since this part it may not differ in an
option whose values are columns: `ars.MODEL_TERMS`, that is `factors`,
`covariates`, `visit`, `by_visit` and `strata`
(`specfirst.machine.csr._other_build`). The refusal names the rule:

```text
<other> differs from <mine> in an option whose values are columns
(<the options>): an other analysis may differ only in the options of
<the decisions> that take no columns
```

The genuine proofs of real-5b hold as before. Only the 12 proofs of Table
14-3.11 name an other analysis (`An_ADAS_MMRM_*_Avg`), and each differs
from the cell's only in `at` (the LS means averaged over the weeks), an
option that takes no columns.

## Planted defects (rule R5)

D9 and D11 on the pilot, in a copy of the worktree under WSL, under the
shared lock with at most 4 processors (lines cut at 300 characters):

```text
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3     env SPECFIRST_STRICT=1 python -m pytest -p no:cacheprovider -q -s tests/defects -k 'D9 or D11'
--- D9-efficacy
unchanged: 0 problems
decision records, unchanged: 0 problems
decision records, the ANCOVA without the baseline covariate: 9 problems, for example: custom:eff-model-terms: ars:An_ADAS_W24_Dose has covariates = [], the decision covariates = ['BASE']
--- D11-efficacy-5b
unchanged, efficacy-adas: 0 problems
unchanged, efficacy-cibic: 0 problems
decision records, unchanged: 0 problems
decision records, gold takes the LS means averaged over the weeks: 3 problems, for example: custom:eff-mmrm-visit: ars:An_ADAS_MMRM_LSM has at = 'average', the decision rule = 'last'
decision records, the CMH test of general association: 3 problems, for example: custom:eff-cmh: ars:An_CIBIC_W08_Cmh has statistic = 'general_association', the decision rule = 'row_mean_scores'
decision records, the visits by AVISIT, in custom:eff-mmrm-terms and the six analyses alike (G2): 3 problems, for example: custom:eff-mmrm-visit: the last visit of the model records of ars:An_ADAS_MMRM_LSM is AVISIT = 'Week 8', where AVISIT is ['Week 8']; the decision names AVISIT =
decision records, custom:eff-mmrm-visit names Week 16 as the last week (G2): 3 problems, for example: custom:eff-mmrm-visit: the last visit of the model records of ars:An_ADAS_MMRM_LSM is AVISITN = '24', where AVISIT is ['Week 24']; the decision names AVISIT = '
planted, gold's week 8 CMH without its strata, proved by the analysis with them (K1): 1 problems, for example: Out14-3-13: cell:Out14-3-13/r2/c4: ours '0.264', CSR '0.2727': the proof does not hold: An_CIBIC_W08_Cmh_Site differs from An_CIBIC_W08_Cmh in an option whose values are
2 passed, 61 deselected in 55.29s
```

The plants of this part:

- **G2, first plant.** The visits are taken from AVISIT (text) in the record
  `custom:eff-mmrm-terms` and in the six analyses alike, so every option is
  as its record says. Week 8 is then the last visit by its characters: 3
  problems, one per analysis at Week 24.
- **G2, second plant.** The record names Week 16 as the last week: 3
  problems.
- **K1.** Gold's CMH of week 8 loses its strata. The CSR's p-value of that
  week (0.2727 against ours, 0.264 unstratified) is then "proved" by an
  other analysis that keeps them, `An_CIBIC_W08_Cmh_Site`. The two differ
  only in `strata`, an option of `custom:eff-cmh`. The plant asks that the
  problem names the rule of K1 ("an option whose values are columns"),
  not another rule.

Without K1 the proof held. The same D11 with the `csr.py` of `2911198` (the
commit before this part) in place of the new one:

```text
planted, gold's week 8 CMH without its strata, proved by the analysis with them (K1): 0 problems
E       AssertionError: gold's week 8 CMH without its strata, proved by the analysis with them (K1): not seen
E         gold's week 8 CMH without its strata, proved by the analysis with them (K1): not seen by the rule of K1
1 failed, 62 deselected in 39.02s
```

Without G2 the first G2 plant passed every check. It is finding G2 of
review pass 2, and the reviewer of pass 3 ran it on `1b0ad01`
(docs/reports/real-5b.review.md, pass 3): "efficacy: 0 problems -> NOT
SEEN" and "decisions: 0 problems -> NOT SEEN".

## Unit tests and lint

```text
$ ruff check src/specfirst/machine/csr.py src/specfirst/machine/decisions.py     src/specfirst/machine/build.py tests/defects/test_defects.py     tests/unit/test_efficacy.py tests/unit/test_efficacy_5b.py
All checks passed!
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 python -m pytest -p no:cacheprovider -q tests/unit
FAILED tests/unit/test_asciicheck.py::test_this_repository_is_ascii - Runtime...
FAILED tests/unit/test_gen_natural.py::test_the_store_in_a_checkout_takes_no_secret_statement
FAILED tests/unit/test_kit.py::test_the_repository_tracks_no_study_data - Run...
FAILED tests/unit/test_layout.py::test_text_files_have_lf_endings - RuntimeEr...
4 failed, 1149 passed in 335.52s (0:05:35)
```

The copy has no `.git`. The four tests that fail ask git for the tracked
files ("git ls-files failed ... not a git repository"). On the clean clones
of the gates they pass (section "The gates on clean clones").

The new unit tests:

- `test_efficacy_5b.py`,
  `test_the_last_visit_of_the_model_records_follows_the_order_of_the_visit_column`:
  - the model records on a toy ADSL;
  - Week 24 last by numbers, and Week 8 last by text;
  - a missing factor value takes its record, and with it Week 24, out.
- `test_efficacy_5b.py`,
  `test_an_other_analysis_may_not_differ_in_an_option_whose_values_are_columns`:
  - other strata are refused;
  - another statistic, an option that takes no columns, is still a
    `rule_choice`.
- `test_efficacy.py`, `test_the_last_visit_is_held_on_the_built_data_only`:
  without the engines the record of the visit is a problem.

## The gates on clean clones

All nine ran on clean clones of `4660e8c`, one after another. Each ran
under the shared lock with at most 4 processors:

```text
$ for wp in real-5b read-2a real-5a real-3a real-2 gen-2a gen-3a read-1a std-1; do
    flock /run/lock/specfirst-heavy.lock taskset -c 0-3       bash scripts/clean_clone_gate.sh $wp /mnt/d/trial_work/specfirst/.git 4660e8c
  done
real-5b: 19 PASS, 0 FAIL; clean clone gate real-5b: PASS    (784 s)
read-2a: 19 PASS, 0 FAIL; clean clone gate read-2a: PASS    (627 s)
real-5a: 18 PASS, 0 FAIL; clean clone gate real-5a: PASS    (1901 s)
real-3a: 16 PASS, 0 FAIL; clean clone gate real-3a: PASS    (1019 s)
real-2:  15 PASS, 0 FAIL; clean clone gate real-2: PASS     (1873 s)
gen-2a:  13 PASS, 0 FAIL; clean clone gate gen-2a: PASS     (1392 s)
gen-3a:  15 PASS, 0 FAIL; clean clone gate gen-3a: PASS     (657 s)
read-1a: 14 PASS, 0 FAIL; clean clone gate read-1a: PASS    (1400 s)
std-1:   12 PASS, 0 FAIL; clean clone gate std-1: PASS      (489 s)
```

The seconds include the waits for the lock, which other sessions held in
between. Two logs are in docs/reports:

- real-5b: `real-5b-answers.clean-clone.gate.log`;
- read-2a: `real-5b-answers.read-2a.gate.log`.

The other seven are not copied. The line per gate above is counted from
their logs.

read-2a passes "arm R, kept dry run". The kept run was not made again:
this part changes no registry entry, and no file of the harness or of
`standard/`. In the clean clones, the four unit tests that fail in a copy
without git pass ("unit tests" PASS in each gate).

## What the checks do not cover

- G2 holds the label of the last visit. It does not hold that the other
  visits are weeks 8 and 16; `custom:eff-mmrm-records` names them, and
  nothing holds that record (decisions.py lists the unheld records).
- K1 refuses other columns in an other analysis. A record whose values
  are columns can still be proved by an other analysis only through its
  options that take no columns. No entry of the pilot needs one.
- The answer citations are not checked by script. ADR-004 point 3 is not
  in schema v0, which asks citations only of `document_rule` and
  `house_default`.

## Review

By a fresh-context reviewer (rule R7); docs/reports/real-5b-answers.review.md
has the pass in full, with the commands and their output.

| Pass | Commit | Verdict | Blocking |
| --- | --- | --- | --- |
| 1 | `4660e8c` | SIGNED | none |

The reviewer checked each point against R and against the parent:

- G2's model records against R's own `mmrm_frame`: 539 records on the
  pilot, the same (subject, visit) pairs. They also agree with missing
  values planted, with Week 24 emptied and with the text visit.
- The check `decisions` in the gate: "the last visit held on the model
  records of 3 analyses; 0 problems".
- K1 refuses pass 4's case O2, which the parent's csr.py accepted: an other
  analysis with strata RACEN, SEX and QSSEQ and rank scores, p = 0.2728.
  K1 refuses no genuine proof: all 45 hold.
- Each plant and new unit test is seen by the new code and not by the
  parent's.

The findings, none blocking, and what was done with them:

- L1: ADR-015 said items 1 to 4 of real-5a were answered. Item 3,
  `custom:eff-baseline-rows`, is still `asked`. Fixed: items 1, 2 and 4.
- L2: two texts still described the checks as they were before this part:
  the handover item on `other_build` in docs/state/real.md, and a sentence
  of the docstring of decisions.py ("the last rule"). Fixed: the handover
  has K1 and G2; the docstring says "the rule of `PARAMETERS`".
- L3: D11's K1 plant is also seen by the check `decisions`, since its
  wrong gold changes the strata `custom:eff-cmh` sets. The case only K1
  sees is pass 4's O2. Adding O2 as a plant is optional and was not done
  here: the merge keeps the code the gates ran on. Left in docs/state/real.md.
- L4: the report waited for its gate lines, and one sentence on the proofs
  of K1 was loose. Fixed: the lines from the clean clones are in, and only
  the 12 proofs of 14-3.11 name an other analysis.

The commit after `4660e8c` changes docs/reports, docs/decisions,
docs/state and one sentence of a docstring in
src/specfirst/machine/decisions.py; no code runs differently.

The reviewer's points for the owner (nothing blocks):

- The class of the three former conflicts: answer 4 names none; the
  executor gave `document_rule`, and `study_input` is the alternative.
  PLAN.md 4.5 scores the two differently once a reader is scored on these
  records. The reviewer recommends keeping `document_rule`.
- What K1 costs: an alternative whose values are columns can no longer be
  proved by an other analysis. No entry of the pilot needs one.

## For the base session

The base session's messages of 2026-11-20 and 2026-11-21 relayed the four
answers. They asked for the gates on clean clones, a fresh review, the
merge, and a push of `main` and `track/real`.

What was done with them:

- the answers are recorded in ADR-015, in ASCII, as a translation;
- the five records, G2 and K1 are as above;
- the sections "For the owner" of ADR-015, docs/reports/real-5a.md and
  docs/reports/real-5b.md now point to the answers;
- docs/state/real.md moves the answered items out of "Open".

After this merge a new session takes `track/real` for issue #29.
