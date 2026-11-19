# std-issues: issues #26, #24 and #25 without the catalog, the house or the generator

Track std, branch `track/std`, 2026-11-18. The parts of three issues of
`xjw1001001/specfirst` that change neither `catalog@1`, nor the house
standard `open-default@1`, nor the generator. `PLAN.md`,
`standard/schemas/` and every file under `standard/` are unchanged.

| Issue | What is done here | Left for later |
| --- | --- | --- |
| #26 An asked decision without a house default stops every output | The scorer's build leaves out what such a decision binds and builds the rest; those gold cells are pending, counted apart. ADR-014, the owner's to approve. | The value of an ask in the reading score beyond section 9.1 (not asked for here). |
| #24 `trt.end.source` needs EXDOSE > 0 | When no subject has a treatment start date, the build stops at ADaM with a message that names the decision, its filter and the variable missing in every exposure record. | The counterpart of `first_ex_record` for `trt.end.source` (`catalog@2`, #23); a probe with EXDOSE missing everywhere (generator). |
| #25 An AE domain without AESEV stops the whole build | Given the columns of the SDTM, the compiler leaves out of the output every column that derives from a variable the data lack and that SDTMIG v3.4 does not require, with a warning; a table that reads one is not produced; a Required one stops the compile with a message. The house parent specs are not changed. | An option of `specfirst compile` that reads the columns of an SDTM folder. |

Choices: docs/decisions/ADR-014.md (decisions 1 to 5 for #26, the owner's;
the last section for #24 and #25, the executor's).

## What changed

- `src/specfirst/compile/compiler.py`. Two options of
  `compile_decisions`, both off by default:
  - `pending=True` (ADR-014). A decision that a dataset or a table needs
    and that has no value does not stop the compile. The columns its
    alternatives write and every output column that derives from them are
    left out of the output; a dataset whose keys would derive from it waits
    as a whole. The analyses that read a column left out, the analyses that
    refer to them and their layout rows are taken out; an output waits as a
    whole when its header count or every row is taken out, or when its
    template needs a parameter only that decision sets. `Compiled.pending`
    lists, per decision, what was left out (`adam:`, `ars:`, `output:`).
  - `sdtm={stem: columns}` (#25). An output column that derives from a
    variable the SDTM lacks is left out with a warning when SDTMIG v3.4
    (as `specfirst.gen.sdtm` lists it) does not require the variable; a
    table that reads such a column is not produced (`Compiled.left_out`);
    a Required one stops the compile.

  What derives from what is the static lineage of the machine
  (`specfirst.machine.lineage`) on the parent spec with the fragments
  composed in. yamaa evaluates only the columns an output needs, so leaving
  a column out of `output.columns` is enough: no house file changes. The
  family templates are now evaluated before they are put into the ARS
  document; a compile that needs neither option gives the same files as
  before. `compile.json` gains `pending`, `left_out` and `warnings` only
  when they are not empty.
- `src/specfirst/compile/template.py`: `UndefinedName`, a `TemplateError`
  that names the name the scope lacks.
- `src/specfirst/score/candidate.py`: `Machine.compile` uses the pending
  mode and gives the compiler the columns of the SDTM when the data may
  lack a variable the specs read (else the compile without them is reused,
  so attribution and the build share it). `Build.pending`,
  `Build.warnings`, `pending_cells`, and `no_treatment_start` (#24).
- `src/specfirst/score/build.py`: a pending cell leaves every count and the
  axes; `OutputScore.pending`, `waiting`; `BuildScore.waiting`,
  `pending_by_decision`; a line "pending" after the four scores when there
  is one; a build with a pending cell is not perfect.
- `src/specfirst/score/scorer.py`, `report.py`, `kit.py`:
  `Result.pending`, its line in the report and in the line of a kit; a
  pending decision is neither `silent` nor `behind`.
- `src/specfirst/score/gate.py`, check "standard alone" of the gate
  read-1a: rewritten for ADR-014 (below).
- Tests: `tests/unit/test_pending.py` (#26), `tests/unit/test_sdtm_gaps.py`
  (#24, #25); `test_score_hand.py` and `test_score_kit.py` held the old
  arm S on the chain and now hold the new one.

## Tests first (rule R5)

The two new test files hold the repro of each issue and what follows from
it. They were written before the code and run on a clone of `main`
(`5fedd14`), the files copied in, with the environment of the worktree
(`/root/scratch-std/clone-main`, in the Linux file system):

```text
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 python -m pytest -q -p no:cacheprovider --no-header -rf tests/unit/test_pending.py tests/unit/test_sdtm_gaps.py
FAILED tests/unit/test_pending.py::test_the_repro_of_issue_26_builds_every_output
FAILED tests/unit/test_pending.py::test_a_pending_decision_leaves_out_only_what_it_binds[visible]
FAILED tests/unit/test_pending.py::test_a_pending_decision_leaves_out_only_what_it_binds[twin]
FAILED tests/unit/test_pending.py::test_the_compiler_keeps_its_default - Type...
FAILED tests/unit/test_pending.py::test_the_standard_alone_builds_the_chain_with_the_related_row_pending
FAILED tests/unit/test_pending.py::test_a_table_decision_without_a_value_leaves_the_output_pending
FAILED tests/unit/test_pending.py::test_what_derives_from_a_pending_column_is_left_out_too
FAILED tests/unit/test_pending.py::test_pending_cells_are_neither_right_nor_wrong
FAILED tests/unit/test_pending.py::test_a_build_without_pending_cells_reads_as_before
FAILED tests/unit/test_sdtm_gaps.py::test_the_repro_of_issue_25_builds_without_aesev
FAILED tests/unit/test_sdtm_gaps.py::test_a_carried_variable_that_is_not_required[AEACN]
FAILED tests/unit/test_sdtm_gaps.py::test_a_carried_variable_that_is_not_required[AEOUT]
FAILED tests/unit/test_sdtm_gaps.py::test_a_carried_variable_that_is_not_required[AEREL]
FAILED tests/unit/test_sdtm_gaps.py::test_a_carried_variable_that_is_not_required[AESDTH]
FAILED tests/unit/test_sdtm_gaps.py::test_a_carried_variable_that_is_not_required[AESER]
FAILED tests/unit/test_sdtm_gaps.py::test_a_carried_variable_that_is_not_required[AESEV]
FAILED tests/unit/test_sdtm_gaps.py::test_a_carried_variable_that_is_not_required[AESOC]
FAILED tests/unit/test_sdtm_gaps.py::test_what_derives_from_a_missing_variable_leaves_too
FAILED tests/unit/test_sdtm_gaps.py::test_a_required_variable_stops_the_build_with_a_message[AEDECOD]
FAILED tests/unit/test_sdtm_gaps.py::test_a_required_variable_stops_the_build_with_a_message[AETERM]
FAILED tests/unit/test_sdtm_gaps.py::test_the_compile_without_the_data_is_unchanged
FAILED tests/unit/test_sdtm_gaps.py::test_no_treatment_start_date_names_the_filter_that_removed_every_record[visible]
FAILED tests/unit/test_sdtm_gaps.py::test_no_treatment_start_date_names_the_filter_that_removed_every_record[twin]
FAILED tests/unit/test_sdtm_gaps.py::test_a_study_with_start_dates_is_not_stopped
24 failed, 1 passed in 8.41s
```

The one that passes, `test_the_start_from_any_exposure_record_still_builds`,
holds what must not change: with `trt.start.source = first_ex_record` the
build goes on without EXDOSE. Some tests fail on a name the old code does
not have (`Build.warnings`, `pending=`) before they reach their assertion;
the repro tests fail on the assertion itself (the build stops).

The same files and the tests that changed with them, on a copy of the
worktree at the code of `d92dd57`:

```text
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 python -m pytest -q -p no:cacheprovider --no-header -rf tests/unit/test_pending.py tests/unit/test_sdtm_gaps.py tests/unit/test_score_hand.py tests/unit/test_score_build.py tests/unit/test_compile.py tests/unit/test_score_kit.py
119 passed in 158.88s (0:02:38)
```

## Generated kits

Kits 1 to 4 of the seed `gen-2a` (kit 4 is the one read-2a uses), written
on clones of `main` (`5fedd14`) and of `d92dd57`, in the Linux file system,
inside the heavy lock:

```text
$ python -m specfirst gen kits --out kits-main --count 4 --seed gen-2a     # clone of 5fedd14
kit 1 of the set: sfpbt5zj, train, 127 files; 14 of 22 decisions separated on the twin
kit 2 of the set: sfmyncmq, train, 127 files; 15 of 22 decisions separated on the twin
kit 3 of the set: sfg5vbvq, train, 126 files; 15 of 21 decisions separated on the twin
kit 4 of the set: sfrrl2uh, train, 127 files; 14 of 22 decisions separated on the twin

$ python -m specfirst gen kits --out kits-after --count 4 --seed gen-2a    # clone of d92dd57
kit 1 of the set: sfpbt5zj, train, 127 files; 14 of 22 decisions separated on the twin
kit 2 of the set: sfmyncmq, train, 127 files; 15 of 22 decisions separated on the twin
kit 3 of the set: sfg5vbvq, train, 126 files; 15 of 21 decisions separated on the twin
kit 4 of the set: sfrrl2uh, train, 127 files; 14 of 22 decisions separated on the twin

$ diff -r kits-main kits-after && echo identical
identical
$ find kits-main -type f | wc -l; find kits-after -type f | wc -l
511
511
$ sha256sum kits-*/kit-00?/kit.yaml
947f40b73a1078be6b299753315e83f828794bdd88e8366a1c8ecc2addb4f0bd  kits-after/kit-001/kit.yaml
7602f342569f61f46feca20a47625beec1ffa56ba71afde2f33274ff50f1f6af  kits-after/kit-002/kit.yaml
a91624ae4b2bca1b13ce40d0bd94c22119ca5389c04f7b0b11935f586337e218  kits-after/kit-003/kit.yaml
e23d3a9099492e0e6978b6a107fc3fb6648dafdc0e9f5de8334e9eeb0e95bd18  kits-after/kit-004/kit.yaml
947f40b73a1078be6b299753315e83f828794bdd88e8366a1c8ecc2addb4f0bd  kits-main/kit-001/kit.yaml
7602f342569f61f46feca20a47625beec1ffa56ba71afde2f33274ff50f1f6af  kits-main/kit-002/kit.yaml
a91624ae4b2bca1b13ce40d0bd94c22119ca5389c04f7b0b11935f586337e218  kits-main/kit-003/kit.yaml
e23d3a9099492e0e6978b6a107fc3fb6648dafdc0e9f5de8334e9eeb0e95bd18  kits-main/kit-004/kit.yaml
```

The manifest of a kit holds the SHA-256 of every file of the kit; all 511
files are the same bytes, and the hashes of `kit.yaml` are those of
docs/reports/issue-27.md (track real). Why: the generator compiles in the
default mode, and a compile that needs neither option gives the same files
(`test_the_compiler_keeps_its_default`, `test_the_compile_without_the_data_is_unchanged`).
The recorded reader run of read-2a on kit 4 is made from the kit, the
catalog, the method registry, the schemas and the skills; this part
changes none of them.

## The repros of the issues, before and after

Each issue's script, unchanged, run on the clone of `main` and on the
clone of `d92dd57` (a shared preamble, `common.py`, holds the six lines of
setup that the three scripts repeat):

```text
checkout: /root/scratch-std/clone-main (5fedd14 ADR-013: the repository is public; rule 6 of PLAN.md section 2.1 rewritten)
$ python repro26.py <checkout>
ae.related.values in the vector: False
build: ok = False | failure: compile: ADAE: no value for ae.related.values | grids: []
$ python repro24.py <checkout>
visible, EXDOSE null, house defaults: ok=False; non-null of 7: {'TRTSDT': 0, 'TRTEDT': 0}
   failure: results: grouping 'Grp_TRT01A': no record of ADSL in the analysis set has a value
visible, EXDOSE null, trt.start.source=first_ex_record: ok=True; non-null of 7: {'TRTSDT': 6, 'TRTEDT': 0}
twin, EXDOSE null, house defaults: ok=False; non-null of 9: {'TRTSDT': 0, 'TRTEDT': 0}
   failure: results: grouping 'Grp_TRT01A': no record of ADSL in the analysis set has a value
twin, EXDOSE null, trt.start.source=first_ex_record: ok=True; non-null of 9: {'TRTSDT': 8, 'TRTEDT': 0}
   row 'Any adverse event': EXDOSE given ['1 ( 33.3)', '2 (100.0)', '2 ( 66.7)', '5 ( 62.5)'] | EXDOSE null ['2 ( 66.7)', '2 (100.0)', '2 ( 66.7)', '6 ( 75.0)']
$ python repro25.py <checkout>
AE without AESEV: ok = False | grids: []
failure: ADaM: ADAE: the run failed with 1 issues; first issue: {'severity': 'error', 'phase': 'validation', 'condition': 'unknown_field', 'rule': 'NAME-3', 'spec_paths': ['columns.AESEV.derivation.source']

checkout: /root/scratch-std/clone-after (d92dd57 std-issues: pending decisions (#26), SDTM gaps (#25), no treatment start (#24))
$ python repro26.py <checkout>
ae.related.values in the vector: False
build: ok = True | failure: None | grids: ['Out_AESUM']
$ python repro24.py <checkout>
visible, EXDOSE null, house defaults: ok=False; non-null of 7: {'TRTSDT': 0, 'TRTEDT': 0}
   failure: ADaM: ADSL: no subject has a treatment start date (TRTSDT is missing in all 7 records). TRTSDT is taken from _TRTSDTC, which trt.start.source (first_ex_with_dose) writes from the records that pass the filter (EX.EXDOSE > 0 OR (EX.EXDOSE = 0 AND EX.EXTRT LIKE '%PLACEBO%')) AND EX.EXSTDTC LIKE '____-__-__%' AND EX.EXSTDTC NOT LIKE '%--%'; EXDOSE is missing in every record of EX, so the filter removes every record
visible, EXDOSE null, trt.start.source=first_ex_record: ok=True; non-null of 7: {'TRTSDT': 6, 'TRTEDT': 0}
twin, EXDOSE null, house defaults: ok=False; non-null of 9: {'TRTSDT': 0, 'TRTEDT': 0}
   failure: ADaM: ADSL: no subject has a treatment start date (TRTSDT is missing in all 9 records). TRTSDT is taken from _TRTSDTC, which trt.start.source (first_ex_with_dose) writes from the records that pass the filter (EX.EXDOSE > 0 OR (EX.EXDOSE = 0 AND EX.EXTRT LIKE '%PLACEBO%')) AND EX.EXSTDTC LIKE '____-__-__%' AND EX.EXSTDTC NOT LIKE '%--%'; EXDOSE is missing in every record of EX, so the filter removes every record
twin, EXDOSE null, trt.start.source=first_ex_record: ok=True; non-null of 9: {'TRTSDT': 8, 'TRTEDT': 0}
   row 'Any adverse event': EXDOSE given ['1 ( 33.3)', '2 (100.0)', '2 ( 66.7)', '5 ( 62.5)'] | EXDOSE null ['2 ( 66.7)', '2 (100.0)', '2 ( 66.7)', '6 ( 75.0)']
$ python repro25.py <checkout>
AE without AESEV: ok = True | grids: ['Out_AESUM']
failure: 
```

What stays as it was, on purpose: with `first_ex_record` the end dates are
still missing and the twin's "Any adverse event" still differs. That is
the other half of #24, an alternative of `trt.end.source` that reads no
dose: a step of the catalog (`catalog@2`, #23), left for later.

Only `_TRTSDTC` is named: the house default of `trt.date.imputation` takes
the complete start date, so TRTSDT reads no other working column.

## The unit suite, lint and ASCII on `d92dd57`

```text
$ python -m pytest -m 'not evidence' -q
1080 passed, 23 deselected in 396.71s (0:06:36)
$ python -m ruff check .
All checks passed!
$ python -m specfirst.asciicheck
ASCII check: 494 files checked, 0 with non-ASCII bytes
```

## The gate read-1a before the gates on clean clones

A first look at the gate whose numbers ADR-014 changes: `specfirst gate
read-1a --clean` on a clone of `d92dd57` in the Linux file system, with the
environment of the worktree (not the clean-clone gate: no fresh install or
fetch). Log: docs/reports/std-issues.read-1a.d92dd57.gate.log.

```text
== [8/14] standard alone: specfirst score hand --arm S (both stages)
...
arm S, chain: the output is built on both datasets: yes; the 4 cells of the row of related events wait for ae.related.values on each, and no other cell waits: yes; the other 20 cells of the visible data are right: yes; the 2 wrong cells of the twin are owned by ae.teae.end alone, at L4: yes
arm S, stage T: every score 100%: yes
...
PASS  standard alone       2.2 s
PASS  planted defects      7.3 s
PASS  kits of gen-2a     746.0 s
GATE read-1a: PASS
```

What changed in its numbers, as ADR-014 says it would. The log was held
against the log of the same gate that read-2a ran on a clean clone of
`e36e443` (`main` `3fbe162` with the harness of read-2a: the same
generator, the same ten kits; `track/read`,
docs/reports/read-2a.read-1a.gate.log), line by line, with the lines of
timing, paths and the install left out. The only lines that differ are
those of arm S on the chain:

- HAND01: before, `valid: no (compile: ADAE: no value for
  ae.related.values)`, `cells correct: 0 of 24`, and 24 cells owned by the
  build that stopped (22 by `ae.related.values`, 2 by it with
  `ae.teae.end`). Now `valid: yes`, 20 of 20 right on the visible data, 18
  of 20 on the twin, 4 cells pending on each, and the 2 wrong cells owned
  by `ae.teae.end` at L4 (`adam:ADAE.TRTEMFL`), confirmed.
- The check line "arm S, chain" (above).
- The line "arm S, stage C" of each of the ten kits. Before, every one said
  `produced 0 of 1` and `cells correct 0 of 0, 0 and N`. Now every one says
  `produced 1 of 1`. On eight kits the cells of the row of related events
  are pending (3 to 5 per dataset, one per column); on two (kits 3 and 8 of
  the set) the gold decisions leave that row out of the table, so no gold
  cell waits, and the line has no "pending".

Every other line, arm S at stage T, the control, the twelve planted
defects on HAND01 and on each kit, the matrices and both sweeps, is the
same, but one: the ASCII check counts 518 files in read-2a's log and 494
here, because read-2a's commit holds more files (review, finding 5).

## After pass 1 of the review

Pass 1 (docs/reports/std-issues.review.md) did not sign: one blocking
finding and five that do not block. What was done for each:

1. (blocking) `pop.efficacy.rule`, which the house lists as `optional`
   for ADSL, still stopped the build when the table is on the efficacy set
   (`compile: the tables read ADSL.EFFFL, which no decision of the study
   writes`). Now, in the pending mode, the columns of an optional decision
   that the study leaves out are recorded as waiting for it; an analysis
   that reads one is left out, and the adverse event summary waits for
   `pop.efficacy.rule` as a whole (its analysis set reads EFFFL). A study
   that reads no such column waits for nothing.
2. A variable that the records of a dataset rest on (ADVS: EXDOSE,
   VSSTRESN and others) stopped the whole compile when the SDTM lacked it.
   Now that dataset is left out with a warning (`ADVS is left out: its
   records cannot be built: ...`), and a table that does not read it is
   built.
3. A pending decision that adds records (`bds.eot.record`, a row template
   of ADVS) left nothing out. Now its dataset waits as a whole, and so does
   a decision whose lookups (intermediates) another column reads.
4. An output that waits as a whole stayed in the denominator of outputs.
   Now it leaves it (`in_gold`), as ADR-014 decision 3 says: on a waiting
   output the line reads `produced: 0 of 0 outputs in gold, and 1 waits for
   a decision without a value`.
5. The ASCII line of the compared logs: said above.
6. docs/state/read.md still says that arm S builds nothing on the chain:
   a pointer to ADR-014 is added when `track/std` takes `main` with read-2a
   merged (that file is the read track's, and read-2a changes it).

Tests first: findings 1 to 4 are four new tests and two changed ones,
committed alone (`7095199`) and run on that commit, where the code is still
that of pass 1, before the fix:

```text
7095199 std-issues: tests for findings 1 to 4 of review pass 1 (they fail before the fix)
$ python -m pytest -q --no-header -rf tests/unit/test_pending.py::test_a_table_decision_without_a_value_leaves_the_output_pending tests/unit/test_pending.py::test_an_optional_decision_without_a_value_that_a_table_reads tests/unit/test_pending.py::test_a_decision_that_adds_records_makes_its_dataset_wait tests/unit/test_pending.py::test_pending_cells_are_neither_right_nor_wrong tests/unit/test_sdtm_gaps.py::test_a_variable_the_records_of_a_dataset_rest_on_leaves_that_dataset_out
...
E       assert (0, 1, 1, [], 0) == (0, 0, 1, [], 0)
...
E       AssertionError: compile: ADVS: its key STUDYID, USUBJID, VSSEQ, DTYPE, PARAMCD cannot be built: the SDTM VS has no VSSTRESN (Expected in SDTMIG v3.4)
...
FAILED tests/unit/test_pending.py::test_a_table_decision_without_a_value_leaves_the_output_pending
FAILED tests/unit/test_pending.py::test_an_optional_decision_without_a_value_that_a_table_reads
FAILED tests/unit/test_pending.py::test_a_decision_that_adds_records_makes_its_dataset_wait
FAILED tests/unit/test_pending.py::test_pending_cells_are_neither_right_nor_wrong
FAILED tests/unit/test_sdtm_gaps.py::test_a_variable_the_records_of_a_dataset_rest_on_leaves_that_dataset_out
5 failed in 3.18s
```

The same files and the tests that changed with the code, on a copy of the
worktree with the fix (committed as the next commit):

```text
$ python -m pytest -q --no-header -rf tests/unit/test_pending.py tests/unit/test_sdtm_gaps.py tests/unit/test_score_hand.py tests/unit/test_score_build.py tests/unit/test_compile.py tests/unit/test_score_kit.py
122 passed in 142.93s (0:02:22)
```

## Gates on clean clones

Not yet run when this was written. The merge waits for read-2a to be on
`main`; then `track/std` takes the then-current `main`, and
`scripts/clean_clone_gate.sh` runs std-1, real-2, real-3a, gen-2a, gen-3a,
read-1a and read-2a on that commit, one at a time under the heavy lock.

## Review

Not yet done when this was written.
