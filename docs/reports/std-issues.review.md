# std-issues: review

Reviewer: a fresh-context reviewer (rule R7), 2026-11-18. Branch
`track/std` at `2456303` (its code is that of `d92dd57`; `529e6d7` and
`2456303` change documents only), against `main` at `5fedd14`, the commit
the branch starts from. Read: CLAUDE.md; issues #26, #24 and #25; ADR-005
(decision 3), ADR-008, ADR-014; PLAN.md sections 4.3, 5.2 (rule 4), 9 and
11.3; docs/reports/std-issues.md and its gate log
docs/reports/std-issues.read-1a.d92dd57.gate.log; the diff
`5fedd14..2456303` (compiler, template, candidate, build, scorer, report,
kit, gate, the tests).

## Pass 1

Pass 1 is about the code and the evidence that exists now. The gates on
clean clones are not yet run (they wait for read-2a to be on `main`); their
logs are for pass 2.

### How the checks were run

Two clones in the Linux file system, made with
`git clone --no-local /mnt/d/trial_work/specfirst/.git`: `c` at `2456303`
and `m` at `5fedd14`, under `/root/scratch-review-std/`. The environment of
the worktree (`. scripts/env.sh`), `PYTHONPATH=<clone>/src`,
`SPECFIRST_ROOT=<clone>`, `PYTHONDONTWRITEBYTECODE=1`, every run inside
`flock /run/lock/specfirst-heavy.lock taskset -c 0-3`. My scripts were kept
outside the repository; what they do is said with each result. No gate was
run.

```text
$ git diff --stat 5fedd14 2456303 -- standard PLAN.md
(nothing: no file under standard/, standard/schemas/ or PLAN.md changes)
$ git diff --stat d92dd57 2456303 -- src tests
(nothing: no code change after d92dd57)
$ git merge-tree --write-tree --name-only origin/main track/std
2b0e753bfe09d9fb34ea1fffe1015849dafa21d3          (no conflict with main 2be5a08)
$ git merge-tree --write-tree --name-only track/read track/std
c5820733c8dec779b826ce8325872d2f2f4e12c2          (no conflict with track/read)
```

The two new test files, on the branch and on `main` (rule R5):

```text
$ git log --oneline -1                                         # clone c
2456303 std-issues: the report so far, and the read-1a gate on d92dd57
$ flock ... python -m pytest -q -p no:cacheprovider --no-header -rf tests/unit/test_pending.py tests/unit/test_sdtm_gaps.py
.........................                                                [100%]
25 passed in 15.61s

# clone m (5fedd14) with the two files of 2456303 copied in
$ flock ... python -m pytest -q -p no:cacheprovider --no-header -rf tests/unit/test_pending.py tests/unit/test_sdtm_gaps.py
FAILED tests/unit/test_pending.py::test_the_repro_of_issue_26_builds_every_output
... (the same 24 lines as the report, in the same order)
FAILED tests/unit/test_sdtm_gaps.py::test_a_study_with_start_dates_is_not_stopped
24 failed, 1 passed in 9.12s
```

That is the report's run, line for line. Lint and ASCII on `2456303`:

```text
$ python -m ruff check .
All checks passed!
$ python -m specfirst.asciicheck
ASCII check: 496 files checked, 0 with non-ASCII bytes
$ for f in $(git diff --name-only 5fedd14 2456303); do LC_ALL=C grep -l -P '[^\x00-\x7F]' "$f"; done
(no file named: every changed file is ASCII)
```

(494 in the report is `d92dd57`; `2456303` adds the report and the log.)

### Question 1: the pending mode

Read: `compile_decisions(pending=True)` (src/specfirst/compile/compiler.py:
`_compile_adam` 403-527, `_left_out` 352-400, `_compile_tables` 722-817,
`_without_what_is_gone` 820-869), `Machine.compile` and `pending_cells`
(src/specfirst/score/candidate.py:172-189, 394-418), `compare_output` and
`BuildScore` (src/specfirst/score/build.py:131-277), `scorer.run`.

My script `exp_pending.py`, part A: on HAND01 with the full house
(`Machine(root)`), the gold vector (33 decisions); each decision in turn
left without a value, built on the visible data and on the twin, and held
against the build of the full vector: the cells of the pending build must
be those of the full build but for the cells `pending_cells` marks (no
wrong cell, `correct` equal to every denominator, axes equal); the ADaM
columns missing from the pending build must be exactly the `adam:` elements
of `Build.pending`, and every other column must have the same records and
values. 66 builds, every one `OK`. Excerpt:

```text
== A. HAND01, full house: every decision of the gold vector left without a value
  33 decisions in the gold vector of HAND01
  OK visible trt.planned.source@mod-treatment: ok=True; pending cells 0; correct 24 of 24/24/24; wrong 0; produced 1/1 waiting 0; axes [(True, True)]; perfect True
      pending elements: ['adam:ADAE.TRTP', 'adam:ADSL.TRT01P', 'adam:ADVS.TRTP']
      ADaM: ADAE: missing ['TRTP'] = pending
  OK visible trt.start.source@mod-treatment: ok=True; pending cells 24; correct 0 of 0/0/0; wrong 0; produced 0/1 waiting 1; axes [(False, False)]; perfect False
      pending elements: [... 'adam:ADSL.SAFFL', 'adam:ADSL.TRTSDT', ..., 'adam:ADVS', 'output:Out_AESUM']
  OK visible pop.safety.grouping@mod-populations: ok=True; pending cells 24; correct 0 of 0/0/0; wrong 0; produced 0/1 waiting 1; axes [(False, False)]; perfect False
      pending elements: ['output:Out_AESUM']
  OK visible disp.status.record@mod-populations: ok=True; pending cells 0; correct 24 of 24/24/24; wrong 0; produced 1/1 waiting 0; axes [(True, True)]; perfect True
      pending elements: ['adam:ADSL.DCSREAS', 'adam:ADSL.EOSDT', 'adam:ADSL.EOSSTT']
  OK twin ae.related.values@mod-ae-emergence: ok=True; pending cells 4; correct 20 of 20/20/20; wrong 0; produced 1/1 waiting 0; axes [(True, True)]; perfect False
      pending elements: ['adam:ADAE.RELGR1', 'ars:An_AESUM_RELATED', 'ars:An_AESUM_RELATED_Tot']
  OK visible bds.unscheduled.use@mod-bds-visits: ok=True; pending cells 0; correct 24 of 24/24/24; wrong 0; produced 1/1 waiting 0; axes [(True, True)]; perfect True
      pending elements: ['adam:ADVS']
  OK visible bds.eot.record@mod-bds-visits: ok=True; pending cells 0; correct 24 of 24/24/24; wrong 0; produced 1/1 waiting 0; axes [(True, True)]; perfect True
      pending elements: []
  OK visible tfl.output.include@tfl-demographics: ok=True; pending cells 0; correct 24 of 24/24/24; wrong 0; produced 1/1 waiting 0; axes [(True, True)]; perfect True
      pending elements: ['output:Out_DM']
  OK twin tfl.ae.summary.rows@tfl-ae-summary: ok=True; pending cells 24; correct 0 of 0/0/0; wrong 0; produced 0/1 waiting 1; axes [(False, False)]; perfect False
      pending elements: ['output:Out_AESUM']
```

So on HAND01 the mode leaves out what the decision binds and only that,
for module decisions (ADSL, ADAE, ADVS), a module decision with a table
parameter (`pop.safety.grouping`), table decisions and `tfl.output.include`;
a cell is pending exactly when it is missing from the build; denominators,
axes and `perfect` follow. Two decisions are not covered by HAND01 and fail
elsewhere (findings 1 and 3), and the output-level counts of an output that
waits do not match ADR-014's wording (finding 4).

Part B, `pop.efficacy.rule` (no house default) on kit 4 of gen-2a
(`sfrrl2uh`, the kit of read-2a; gold: `tfl.population` = efficacy,
`pop.efficacy.rule` status `asked`), the candidate being the gold records
with `pop.efficacy.rule` asked and not answered (`scorer.run`):

```text
== B. kit sfrrl2uh: pop.efficacy.rule asked and not answered (tfl.population of gold: {'rule': 'efficacy'})
  visible: valid: no (compile: the tables read ADSL.EFFFL, which no decision of the study writes)
  visible: produced: 0 of 1 outputs in gold
  visible: cells correct: 0 of 15 gold cells (an output that was not produced counts as wrong)
  twin: valid: no (compile: the tables read ADSL.EFFFL, which no decision of the study writes)
  result.pending: {}
  with tfl.population = safety: ok=True failure=None pending={}
```

Finding 1.

Part C, the full house on the SDTM of kit 4, the gold records of the kit
with the house defaults (or the first alternative with its examples) of
`mod-demographics` and `mod-bds-visits` added, every other family not
included; each of those decisions left without a value and held against
the full build as in part A, then `bds.eot.record` three ways:

```text
== C. full house on the SDTM of kit sfrrl2uh ...
  compile: ok, ['ADSL', 'ADAE', 'ADVS'] ['tfl-ae-summary']
  reference build: ok=True failure=None grids=['Out_AESUM'] not_produced={}
  ADVS: 3701 records; DTYPE values ['', 'LOV']; LOV records 358
  OK visible bds.baseline.rule@mod-bds-visits: ... pending elements: ['adam:ADVS.ABLFL', 'adam:ADVS.ANL01FL', 'adam:ADVS.AVISIT', 'adam:ADVS.AVISITN', 'adam:ADVS.BASE', 'adam:ADVS.CHG']
  OK visible bds.unscheduled.use@mod-bds-visits: ... pending elements: ['adam:ADVS']
  OK visible bds.eot.record@mod-bds-visits: ... pending elements: []
      ADaM: ADVS: 3701 records, pending build 3343
  ADVS with bds.eot.record gold value: 3701 records, LOV 358; pending []
  ADVS with bds.eot.record pending: 3343 records, LOV 0; pending []
  ADVS with bds.eot.record value none: 3343 records, LOV 0; pending []
  pending build of ADVS equals the build with the value none: True
```

(The vitals table itself cannot be held this way: with it included, the
reference build stops in `specfirst.gen.display.build` with
`AttributeError: 'str' object has no attribute 'get'`; the branch does not
change that module, and the layout of that family is draft 0.) Finding 3.

### Question 2: the default mode

By reading. Without `pending` and `sdtm`: `missing` stops the dataset as
before (compiler.py:417), `waiting` is empty, `sdtm` is None and `gone`
stays empty, so the new block of `_compile_adam` (464-512) is skipped and
the entry spec is built from the same `columns`. In `_compile_tables` the
family is now evaluated (defines, ARS members, list item, layout) before its
elements are merged into the document. `template.evaluate` does not change
its scope (template.py:182 and 194 copy it), no template reads the
document, and the merge loop visits the elements in the order the old loop
did (lists in `ARS_LISTS` order, members in template order), so the
document, the list items (their `order` is taken from `items` at merge
time, as before) and the layouts are the same. `missing` is empty without
`pending`, so no family is skipped; a family with an evaluation error adds
its problems and the compile raises, as before (only the list of problems
can be shorter: the old loop also merged the half-evaluated family).
`Compiled.manifest` adds `pending`, `left_out` and `warnings` only when they
are not empty.

By a run: my script `dump_compile.py` compiles, in the default mode, the
gold vector of HAND01 and the house defaults on the full house, each with
every other value of every decision (`compiler.other_values`, as
`bind_tables` does) and with every decision removed, and the gold records
of kits 1 to 4 of gen-2a through `specfirst.gen.gold.compile_records` (the
generator's call; `bind=True` for the gold vector itself), and prints one
line per compile: the SHA-256 of the files, `compile.json`, the ARS
document, the layouts and the binds, or the text of the error. Run with the
code of `5fedd14` and with the code of `2456303`:

```text
== m: 5fedd14 ADR-013: the repository is public; rule 6 of PLAN.md section 2.1 rewritten
COUNTS {'ok': 275, 'error': 317}
== c: 2456303 std-issues: the report so far, and the read-1a gate on d92dd57
COUNTS {'ok': 275, 'error': 317}
   592 /root/scratch-review-std/out/dump-m.txt
   592 /root/scratch-review-std/out/dump-c.txt
$ cmp dump-m.txt dump-c.txt && echo IDENTICAL
IDENTICAL
```

592 compiles, the same outcome for each, including the text of every
error. The claim of the report holds in the code and in a run wider than
the four kits.

The report's run of the generator on kits 1 to 4 is on the disk of the
machine (`/root/scratch-std`, the executor's clones):

```text
clone-main: 5fedd14 ADR-013: the repository is public; rule 6 of PLAN.md
clone-after: d92dd57 std-issues: pending decisions (#26), SDTM gaps (#25)
$ diff -r kits-main kits-after && echo identical
identical
$ find kits-main -type f | wc -l; find kits-after -type f | wc -l
511
511
(the four SHA-256 of kit.yaml as in the report; each appears in docs/reports/issue-27.md on main)
```

### Question 3: issue #25

Read: `_left_out`, `absent_reason`, `_sdtmig_core` (compiler.py:288-400),
the block of `_compile_adam` that uses them (464-512), the absent branch of
`_without_what_is_gone` (839-844), `Machine.compile` and `Machine._lacks`
(candidate.py:394-442).

My script `exp_sdtm.py`: every column of every SDTM file dropped in turn,
the gold decisions built; for each, what `_lacks` says on the compile
without the SDTM columns, and whether the build is that of the full data
(grids and every ADaM table equal, no warning). FALSE-NEGATIVE would be
`_lacks` saying no while the build is not that of the full data.

```text
== HAND01 visible, slice ...      {'fails': 21, 'left out': 24, 'unchanged': 13}
== HAND01 twin, slice ...         {'fails': 21, 'left out': 24, 'unchanged': 13}
== HAND01 visible, full house ... {'fails': 30, 'left out': 19, 'unchanged': 9}
== HAND01 twin, full house ...    {'fails': 30, 'left out': 19, 'unchanged': 9}
== kit sfrrl2uh visible, slice    {'fails': 21, 'unchanged': 71, 'left out': 24}
$ grep -c FALSE exp_sdtm.out
0
```

On the slice (ADSL and ADAE, the datasets of every kit), every failure is a
Required variable, with a clear message, and every non-Required variable
is left out with a warning:

```text
  fails     AE.AEDECOD (Req) lacks=True ok=False ... failure='compile: ADAE: the SDTM AE has no AEDECOD, which SDTMIG v3.4 requires (Required); ADAE needs it for AEDECOD, AOCCPFL'
  left out  AE.AESEV (Perm) lacks=True ok=True grids=['Out_AESUM'] left out=['ADAE.AESEV'] not produced={}
  left out  AE.AESOC (Exp) lacks=True ok=True grids=['Out_AESUM'] left out=['ADAE.AESOC', 'ADAE.AOCCSFL'] not produced={}
  left out  AE.AESDTH (Perm) lacks=True ok=True grids=[] ... not produced={'Out_AESUM': 'Out_AESUM is not produced: its analysis An_AESUM_FATAL reads ADAE.AESDTH, which is left out: the SDTM AE has no AESDTH (Permissible in SDTMIG v3.4)'}
  left out  DM.ARM (Exp) lacks=True ok=True grids=['Out_AESUM'] left out=['ADAE.TRTP', 'ADSL.ARM', 'ADSL.TRT01P'] not produced={}
  left out  AE.AEENDTC (Exp) lacks=True ok=True grids=[] left out=['ADAE.AENDT', 'ADAE.AENDY', 'ADAE.AOCCFL', 'ADAE.AOCCPFL', 'ADAE.AOCCSFL', 'ADAE.TRTEMFL', ...]
```

The table that reads a column left out is not produced, with the variable
named; one that does not is built with the cells of the full data; what
ADR-014 says of the seven carried AE variables and of AEENDTC holds. The
core designations of `specfirst.gen.sdtm` for the variables of AE, DM, EX,
DS and VS that the house reads are those of SDTMIG v3.4 as far as I can
check them (for example ARM and ARMCD Expected, EXDOSE Expected, AESEV
Permissible, AEDECOD Required). No file under `standard/` changes.
`_lacks` said yes for every variable whose absence changes the build (0
false negatives in 348 drops); it compares the SDTMIG names and the
qualified names it finds in the parent specs and the compiled fragments
with the columns of the data, so it can only err by saying yes. Every
qualified SDTM name in the house parents and the compile templates is a
variable that `specfirst.gen.sdtm` lists (a `grep -ohE` over both), so the
bare-name test covers them too. By reading: a domain missing as a whole is
not looked at (`_lacks` loops over the files given, candidate.py:434-441),
so the compile without the SDTM columns is used and the build fails in
yamaa on the missing input, as on `main`: no regression.

On the full house the eight non-Required variables that the records of
ADVS rest on stop the whole compile, and with it the adverse event summary,
which reads no ADVS:

```text
  fails  EX.EXDOSE (Exp) lacks=True ok=False ... failure='compile: ADVS: its key STUDYID, USUBJID, VSSEQ, DTYPE, PARAMCD cannot be built: the SDTM EX has no EXDOSE (Expected in SDTMIG v3.4)'
  (the same for EX.EXSTDTC, EX.EXENDTC, VS.VSSTRESN, VS.VSDTC, VS.VISIT (Perm), VS.VISITNUM, VS.VISITDY (Perm))
```

Finding 2.

### Question 4: issue #24

`no_treatment_start` (candidate.py:207-257) returns None unless ADSL has a
TRTSDT column, at least one record and TRTSDT missing in every record; it
runs only when the scorer builds ADaM from SDTM (stage T is untouched) and
before the planted ADaM hooks, so a planted defect cannot reach it. The
message, on HAND01 (slice), in cases beyond the tests:

```text
== #24: no treatment start date, other causes (HAND01 visible, slice)
  EXSTDTC null: ok=False ... failure="ADaM: ADSL: no subject has a treatment start date (TRTSDT is missing in all 7 records). TRTSDT is taken from _TRTSDTC, which trt.start.source (first_ex_with_dose) writes from the records that pass the filter (...) AND EX.EXSTDTC LIKE '____-__-__%' AND EX.EXSTDTC NOT LIKE '%--%'; EXSTDTC is missing in every record of EX, so the filter removes every record"
  EXTRT null (doses given): ok=True warnings=[] failure=None
  EXDOSE 0, EXTRT not placebo: ok=False ... the filter (...)        [ends there: no variable is empty]
  EXSTDTC year-month only: ok=False ... the filter (...)            [ends there]
  EX without EXDOSE: ok=True warnings=['ADSL.TRTSDT is left out: the SDTM EX has no EXDOSE (Expected in SDTMIG v3.4)', ...]
  EX with no record: ok=False ... the filter (...)
  dm_rfxstdtc, RFXSTDTC null: ok=False failure='ADaM: ADSL: no subject has a treatment start date (TRTSDT is missing in all 7 records). TRTSDT is taken from _TRTSDTC, which trt.start.source (dm_rfxstdtc) writes; RFXSTDTC is missing in every record of DM'
```

It fires only when no subject has TRTSDT, names the right decision and
alternative, and adds "so the filter removes every record" only when there
is a filter. Could it change a build that used to succeed? Only one whose
TRTSDT is missing for every subject, whose tables used to be built with
every subject out of the treatment-emergent counts. No such build is in the
gate read-1a on `d92dd57`:

```text
$ grep -c "no subject has a treatment start" docs/reports/std-issues.read-1a.d92dd57.gate.log
0
```

and the sweeps and planted defects of that log are line for line those of
read-2a's run (question 6). Issue #24 asks for this failure.

### Question 5: the check "standard alone" of read-1a

src/specfirst/score/gate.py:187-207 now holds the four facts that ADR-014's
first consequence names: the output built on both datasets
(`valid` and produced 1 of 1), the pending map equal to
`{ae.related.values: {visible: 4, twin: 4}}` (so no other decision and no
other cell waits), 20 of 20 on the visible data with no owner, and exactly
two owners on the twin, `ae.teae.end` alone at L4, confirmed; plus stage T
at 100%. That is a fair reading of ADR-014 and of what HAND01 is built to
show. Rule R5, my script `exp_gate.py`: `gate.arms` on the committed code
and on five planted defects of the pending mode (each patched in the
process, the machine cache cleared between runs):

```text
D0 as committed: check returns True
D1 the compile of the scorer without the pending mode (ADR-005 decision 3 as before): check returns False
    arm S, chain: the output is built on both datasets: NO; ... NO; ... NO; ... NO
D2 pending cells counted as wrong (no cell marked pending): check returns False
D3 one more gold cell (Any adverse event, first column) marked pending: check returns False
D4 the output waits as a whole when one analysis waits: check returns False
D5 the build also loses the row of serious events (not pending: wrong): check returns False
D6 as committed, again: check returns True
```

It fails on each. tests/unit/test_score_hand.py:428-438 runs the check as a
test.

### Question 6: the evidence

- Gate log of read-1a on `d92dd57` against read-2a's log of the same gate
  (`git show track/read:docs/reports/read-2a.read-1a.gate.log`, clean clone
  of `e36e443`), from check 1 on, without timing and paths (my
  `logdiff.py`): 631 and 625 lines, 64 differ. They are the arm S lines of
  HAND01 (valid, 20 of 20 visible, 18 of 20 twin, 4 pending on each, the
  two L4 owners of `ae.teae.end`, the pending line), the check line, the
  ten lines "arm S, stage C" of the kits, the trailer of the clean clone,
  and one more: `ASCII check: 518 files` before, `494` now (finding 5).
- Each kit line adds up: before `0 of 0, 0 and N`, now produced 1 of 1 with
  `all` + pending = N (30 = 25 + 5, 18 = 15 + 3, 16 = 16, 15 = 12 + 3,
  20 = 16 + 4, 30 = 25 + 5, 24 = 20 + 4, 16 = 16, 24 = 20 + 4,
  18 = 15 + 3); kits 3 and 8 have no pending line, as the report says.
- The R5 run and the repro lines: reproduced above. The generated kits:
  reproduced above (same 511 files).
- Not reproduced here: the full unit suite (1080 passed) and the repro
  scripts of the issues as the report ran them; the clean-clone gates will
  show the suite, and the tests above hold each repro.
- R4: every new list is sorted or in catalog, dataset or column order
  (`Compiled.pending` sorted at compile_decisions:243-244, `left_out` and
  `pending` sorted in the manifest, `Build.pending` and `Result.pending`
  sorted); no clock, no randomness. R10: above. Scope: nothing under
  `standard/`, `PLAN.md` unchanged.

### Findings

1. BLOCKING. `pop.efficacy.rule` without a value still stops the whole
   build when a table reads EFFFL. It is one of the four entries without a
   house default that ADR-014 names (Context), and ADR-014 decision 1 makes
   pending "a decision of the study that a dataset or a table needs and that
   has no value (no house default and not given, or asked and not
   answered)". The house lists it as `optional` for ADSL
   (standard/houses/open-default@1/house.yaml:23), and the pending mode
   takes `waiting` from `missing`, which leaves the optional decisions out
   (compiler.py:415-416, 460-461). So EFFFL is not written, nothing records
   it as left out, the analyses of the efficacy set are kept, and
   `unread_variables` (compiler.py:937-947) stops the compile. Failure
   scenario, reproduced above (question 1, part B): kit 4 of gen-2a
   (`sfrrl2uh`, the kit of read-2a), gold `tfl.population` = efficacy and
   `pop.efficacy.rule` status `asked`; a reader that asks and gets no answer,
   or leaves the decision out, scores `valid: no (compile: the tables read
   ADSL.EFFFL, which no decision of the study writes)`, produced 0 of 1,
   0 of 15 cells, and `Result.pending` is empty: the build ADR-014 exists to
   avoid, and nothing names the decision. With `tfl.population` = safety the
   same vector builds. The tests do not see it: HAND01 has no
   `pop.efficacy.rule` and uses the randomized set. Wanted: in the pending
   mode, a missing optional decision of a compiled dataset puts the columns
   its alternatives write into `gone` with its key (they are not written
   anyway), so the analyses that read EFFFL are left out and the adverse
   event summary waits for `pop.efficacy.rule` as a whole (its analysis set
   is read by every analysis); a test of it (HAND01 with `tfl.population` =
   efficacy is enough); the report's statement of what is pending checked
   against the four entries without a default.

2. NOT BLOCKING (the scorer builds only ADSL and ADAE from data that may
   lack a variable today). On the full house, a non-Required variable that
   the records of ADVS rest on stops the whole compile. ADVS takes its rows
   from the row templates `collected` and (bds.eot.record) `eot`; every
   column of ADVS reads the row templates, and `eot` filters on
   `_EOTRN`, which reads the treatment dates and VS. So without EXDOSE,
   EXSTDTC, EXENDTC, VSSTRESN, VSDTC, VISIT (Permissible), VISITNUM or
   VISITDY (Permissible) the key of ADVS "cannot be built" and
   compiler.py:497-499 makes that a problem of the compile: the adverse
   event summary, which reads no ADVS, is not built either (question 3,
   `Machine(root)`, HAND01 without EX.EXDOSE). ADR-014's last section says
   "a table that does not read it is built". Failure scenario: the scorer's
   default machine (`Machine(root)`, the one `gate.machine_of` makes), or a
   later slice that includes ADVS, given an SDTM without the column
   EX.EXDOSE (not only its values) gives `valid: no (compile: ADVS: its key
   ... cannot be built ...)` and no output at all. Wanted: leave such a
   dataset out with a warning (as the pending mode does at
   compiler.py:481-496) so that the tables that read it are not produced
   with the reason and the others are built; or say in ADR-014 and the
   report that a variable that the records of a dataset rest on stops the
   compile, with a test.

3. NOT BLOCKING (no output of the scorer reads ADVS today; the vitals
   layout is draft 0 and `specfirst.gen.display` does not build it). The
   pending mode does not see a decision whose fragment adds records:
   `bds.eot.record` without a value leaves nothing out (`pending elements:
   []` in question 1, part A) and the dataset is built as with the value
   `none`, without the end-of-treatment records. ADR-014 decision 2 says "A
   dataset whose records themselves depend on the decision ... waits as a
   whole". The test of `_compile_adam` asks whether a key or an ordering
   column derives from a column the decision writes (compiler.py:460-470);
   the row template `eot` that the fragment adds is not in the composed spec
   when the decision is missing, so no element reads it. Failure scenario:
   on the SDTM of kit 4 with the full house (question 1, part C),
   `bds.eot.record` without a value gives an ADVS of 3343 records instead
   of 3701, with none of the 358 end-of-treatment (LOV) records, the same
   table as with the value `none`, and `Build.pending` is empty; once a
   vitals table is built, its End of Treatment rows would count as wrong
   (no row) instead of pending. Wanted: a decision with a `rows` part in any
   alternative of a dataset makes that dataset wait as a whole when it has
   no value (only `bds.eot.record` has one in `catalog@1`).

4. NOT BLOCKING. An output that waits as a whole stays in the denominator of
   "produced" and of both "whole output" scores: `in_gold` is
   `len(self.outputs)` (build.py:193-195), and the scorer prints
   `produced: 0 of 1 outputs in gold (1 waits for a decision without a
   value)`, `strict 0 of 1`, `lenient 0 of 1` (question 1, part A, for
   example `tfl.ae.summary.rows`; tests/unit/test_pending.py:134 holds
   `(0, 1, 1)`). ADR-014 decision 3: "it is neither produced nor counted as
   not produced". Failure scenario: a reader that asks `tfl.ae.summary.rows`
   and gets no answer scores "produced 0 of 1", which reads exactly as a
   build that failed; the note in brackets is the only difference. Wanted:
   leave the waiting outputs out of the denominator of those three scores,
   or record in ADR-014 (and the docstring of build.py) that they stay in it
   and are named apart. No number of any gate log changes either way today
   (no output waits as a whole in them).

5. NOT BLOCKING. The report (section "The gate read-1a before the gates on
   clean clones") says that apart from the lines of arm S on the chain
   "every other line ... is the same". One more line differs:
   `ASCII check: 518 files checked` in read-2a's log, `494` in the log of
   `d92dd57` (read-2a's commit holds more files). Say so (rule R8).

6. NOT BLOCKING. ADR-014 (Consequences) says the line on arm S in
   docs/state/read.md is superseded, but docs/state/read.md:100 and :139
   still say "Arm S builds nothing on the chain", with no pointer. That file
   is track read's; add the pointer when `track/std` merges after read-2a.

### For pass 2

Finding 1 fixed with its test (rule R5: the test fails on `2456303`);
findings 2 to 6 fixed or answered in the report; then the logs of the gates
on clean clones (std-1, real-2, real-3a, gen-2a, gen-3a, read-1a, read-2a)
on the commit that merges the then-current `main`, the full unit suite
among them.

Pass 1 covers the code of `d92dd57` and the evidence that exists now; the
gate logs on clean clones are not yet run and are for pass 2. The default
mode (question 2), issue #24 (question 4), the check of read-1a
(question 5) and the evidence of the report (question 6, but finding 5)
hold. Issue #25 holds on the slice. The pending mode holds on every
decision of HAND01 but fails on `pop.efficacy.rule`, one of the four
decisions it exists for, on the kit of read-2a.

Verdict: NOT SIGNED

## Pass 2

2026-11-19. Branch `track/std` at `42212b8`. Since pass 1
(`2456303..42212b8`): `307efb9` and `5d1876f` merge `main` (`2be5a08`, the
fix of issue #27; `b0a5530`, read-2a); `7095199` the tests of findings 1 to
4, alone; `1d26c2a` the fix, with ADR-014 and the report; `37e5b61` my pass 1
and the pointers in docs/state/read.md; `42212b8` the axis of attribution.
Read: those diffs (compiler, build, attribute, the tests, ADR-014,
docs/state/read.md, docs/reports/std-issues.md), the logs of the seven
gates on `37e5b61` and on `42212b8`.

### How the checks were run

As in pass 1, on clones in the Linux file system (`c` at `42212b8`, `m` at
`main` `b0a5530`, `r5` for the commits of the tests), with my scripts in a
folder of my own. One batch, one hold of the heavy lock (about seven
minutes, while the coordinator's chain ran on `42212b8`):

```text
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 bash batch.sh
```

```text
$ git diff --stat 2456303 42212b8 -- standard PLAN.md
(nothing)
$ git diff --stat 5fedd14 b0a5530 -- src/specfirst/compile standard
(nothing: main changed neither the compiler nor the standard)
$ git diff --stat 37e5b61 42212b8 -- src/specfirst/compile standard src/specfirst/gen
(nothing)
```

### The findings of pass 1

Rule R5 first. The five tests of `7095199`, on `7095199` (the code of pass
1), and the new test of `42212b8` on `37e5b61` (the file copied in):

```text
== 2. R5: the tests of 7095199 on 7095199          (the E lines filtered by grep; two "assert False" left out)
7095199 std-issues: tests for findings 1 to 4 of review pass 1 (they fail before the fix)
E           assert (0, 1, 1) == (0, 0, 1)
E       AssertionError: compile: the tables read ADSL.EFFFL, which no decision of the study writes
E       KeyError: 'adam:ADVS'
E       assert (0, 1, 1, [], 0) == (0, 0, 1, [], 0)
E       AssertionError: compile: ADVS: its key STUDYID, USUBJID, VSSEQ, DTYPE, PARAMCD cannot be built: the SDTM VS has no VSSTRESN (Expected in SDTMIG v3.4)
FAILED tests/unit/test_pending.py::test_a_table_decision_without_a_value_leaves_the_output_pending
FAILED tests/unit/test_pending.py::test_an_optional_decision_without_a_value_that_a_table_reads
FAILED tests/unit/test_pending.py::test_a_decision_that_adds_records_makes_its_dataset_wait
FAILED tests/unit/test_pending.py::test_pending_cells_are_neither_right_nor_wrong
FAILED tests/unit/test_sdtm_gaps.py::test_a_variable_the_records_of_a_dataset_rest_on_leaves_that_dataset_out
5 failed in 2.91s
== 2b. R5: test_an_axis_is_owned_without_the_rows_that_wait on 37e5b61 (the file of 42212b8 copied in)
E             At index 0 diff: ('Out_AESUM', 'rows', (('ae.related.values', 'mod-ae-emergence'), ('tfl.ae.summary.rows', 'tfl-ae-summary')), True) != ('Out_AESUM', 'rows', (('tfl.ae.summary.rows', 'tfl-ae-summary'),), True)
FAILED tests/unit/test_pending.py::test_an_axis_is_owned_without_the_rows_that_wait
1 failed in 4.31s
== 1. the new and changed tests on 42212b8
.............................                                            [100%]
29 passed in 14.21s
```

Each fails for the reason of its finding before the fix and passes after
it. Then my pass 1 scripts again, unchanged, on `42212b8`:

- Finding 1 (BLOCKING): fixed. `_compile_adam` now takes the optional
  decisions that the study leaves out (`left_optional`, only in the pending
  mode) and records the columns they would write as gone for them
  (compiler.py:470-491); `_without_what_is_gone` then leaves out the
  analyses that read one and names the column (compiler.py:873-874). Part B
  of `exp_pending.py`, kit 4 of gen-2a, `pop.efficacy.rule` asked and not
  answered, everything else at gold:

  ```text
  == B. kit sfrrl2uh: pop.efficacy.rule asked and not answered (tfl.population of gold: {'rule': 'efficacy'})
    visible: valid: yes
    visible: produced: 0 of 0 outputs in gold, and 1 waits for a decision without a value
    visible: pending: 15 gold cells, neither right nor wrong and in no denominator above, wait for a decision without a value: pop.efficacy.rule (15 cells); 1 output waits as a whole
    twin: valid: yes
    twin: pending: 15 gold cells, ... pop.efficacy.rule (15 cells); 1 output waits as a whole
    result.pending: {('pop.efficacy.rule', 'mod-populations'): {'visible': 15, 'twin': 15}}
    OK visible pop.efficacy.rule@mod-populations: ok=True; pending cells 15; correct 0 of 0/0/0; wrong 0; produced 0/0 waiting 1; axes [(False, False)]; perfect False
        pending elements: ['adam:ADSL.EFFFL', 'output:Out_AESUM']
    with tfl.population = safety: ok=True failure=None pending={}
  ```

  A study that reads no EFFFL waits for nothing (the last line, and part A
  below, where HAND01 never has `pop.efficacy.rule`). In the default mode
  `left_optional` is empty and nothing changes (below).
- Finding 2: fixed. A dataset whose keys rest on a variable the SDTM lacks
  is left out as a whole with a warning (compiler.py:505-528), instead of
  stopping the compile. `exp_sdtm.py` on HAND01 (visible), every SDTM
  column dropped in turn:

  ```text
  == HAND01 visible, slice: ...       {'fails': 21, 'left out': 24, 'unchanged': 13}
  == HAND01 visible, full house: ...  {'fails': 22, 'left out': 27, 'unchanged': 9}
  (0 FALSE-NEGATIVE; 0 failures of a non-Required variable on either machine)
    left out  EX.EXDOSE (Exp) lacks=True ok=True grids=[] left out=[..., 'ADSL.SAFFL', ..., 'ADVS', 'Out_AESUM is not produced: its analysis An_AESUM_N r...
    left out  VS.VSSTRESN (Exp) lacks=True ok=True grids=['Out_AESUM'] left out=['ADSL.BMIBL', 'ADSL.HEIGHTBL', 'ADSL.WEIGHTBL', 'ADVS'] not produced={}
    left out  VS.VISIT (Perm) lacks=True ok=True grids=['Out_AESUM'] left out=['ADVS'] not produced={}
    fails     VS.VSTEST (Req) lacks=True ok=False ... failure='compile: ADVS: the SDTM VS has no VSTEST, which SDTMIG v3.4 requires (Required); ...'
  ```

  In pass 1 the full house had 30 failures, eight of them non-Required
  (EXDOSE, EXSTDTC, EXENDTC, VSSTRESN, VSDTC, VISIT, VISITNUM, VISITDY);
  now those eight leave ADVS out and the adverse event summary is built
  where it reads none of them (EXDOSE still removes it, through SAFFL, with
  the reason). The slice is as in pass 1. Without EXDOSE the summary is not
  produced because the safety flag derives from it, which is right.
- Finding 3: fixed. A pending decision with a row template in any
  alternative (`adds_records`) makes its dataset wait as a whole
  (compiler.py:473-480, 505). Part C, full house on the SDTM of kit 4:

  ```text
    OK visible bds.eot.record@mod-bds-visits: ok=True; pending cells 0; correct 15 of 15/15/15; wrong 0; produced 1/1 waiting 0; axes [(True, True)]; perfect True
        pending elements: ['adam:ADVS']
    ADVS with bds.eot.record gold value: 3701 records, LOV 358; pending []
    ADVS with bds.eot.record pending: not built; pending ['adam:ADVS']
    ADVS with bds.eot.record value none: 3343 records, LOV 0; pending []
  ```

- Finding 4: fixed. `in_gold` leaves out the outputs that wait as a whole
  (build.py:195-198); `produced: 0 of 0 outputs in gold, and 1 waits for a
  decision without a value` (part B above, and `tfl.ae.summary.rows` in part
  A: `produced 0/0 waiting 1`). The other users of `in_gold` (gate.py:139,
  193; kit.py:379, 495; defects.py:448) print it or compare it with
  `produced`; none divides by it. In the sweep of kit.py:379 an output that
  waits would now make `produced == in_gold` true, but a sweep gives every
  decision a value, so no output waits there.
- Finding 5: answered in the report (the ASCII line, 518 against 494).
- Finding 6: docs/state/read.md now points to ADR-014 where it said that
  arm S builds nothing on the chain (its lines 85, 127, 195 and 237).

Part A, all 33 decisions of HAND01 one at a time on the full house, both
datasets, as in pass 1: `66` builds, every one `OK` (no wrong cell, every
denominator equal to the cells counted, the ADaM columns missing equal to
the `adam:` elements of `Build.pending`, every other column the same).
Parts B and C: every line `OK` (76 in all, no `CHECK`). The check
"standard alone" on the planted defects of pass 1: `True` as committed,
`False` on D1 to D5, `True` again (unchanged).

### The default mode, again

The compiler changed after pass 1 (`1d26c2a`): `left_optional` exists only
in the pending mode, `waiting` and `adds_records` are then empty, `gone`
stays empty without `sdtm`, so the block at compiler.py:483-539 is skipped
as before. By a run: the 592 compiles of pass 1 (`dump_compile.py`) on
`main` `b0a5530` and on `42212b8`:

```text
m: b0a5530 Merge track/read: part read-2a of ADR-005 (gates passed, review signed,
COUNTS {'ok': 275, 'error': 317}
c: 42212b8 std-issues: an axis is held without the rows that wait (attribution)
COUNTS {'ok': 275, 'error': 317}
   592 /root/scratch-review-std/out/p2-dump-m.txt
   592 /root/scratch-review-std/out/p2-dump-c.txt
$ cmp p2-dump-m.txt p2-dump-c.txt && echo IDENTICAL
IDENTICAL
```

(The dump of `b0a5530` is also byte for byte that of `5fedd14` in pass 1.)
The report's kit run on `37e5b61` (511 files, the same `kit.yaml` hashes)
is on a commit whose compiler, generator and standard are those of
`42212b8`.

### The axis of attribution (`42212b8`)

`attribute._Runs.axis` held the axis of a rebuild against the whole gold
axis, so a row that waits in the rebuild made the pending decision a
co-owner of the axis. It now holds it against the gold axis without the
rows and columns whose every cell still waits in that rebuild
(`build.axes_without`, `candidate.pending_cells` of the rebuild,
attribute.py:395-433). When the rebuild sets the pending decision to its
gold value nothing waits and the whole gold axis is held, as before; when
there is no pending cell the code path is the old one. The new test fails
on `37e5b61` and passes (above). `cell()` only unpacks the new tuple. In the
log of read-2a on `37e5b61` the line was:

```text
    axis rows of Out_AESUM: layer L5, decision ae.related.values, tfl.ae.summary.rows, confirmed yes, first element that differs ars:An_AESUM_N
```

In the log of read-2a on `42212b8` (both datasets) it is:

```text
    axis rows of Out_AESUM: layer L5, decision tfl.ae.summary.rows, confirmed yes, first element that differs ars:An_AESUM_N
```

The rows of arm S on kit 4 differ from gold's because of the rows decision
alone once the row that waits is out of the axis, which is what ADR-014
decision 3 says. Against `main`'s own log of read-2a (`b0a5530`), the
other lines of arm S there change as ADR-014 says they would: valid, 4 and
3 of 12 cells right, 3 cells pending on each dataset, owners at L4 and L5
in place of the build that stopped; `trt.actual.source` moves from a
co-owner of the build that stopped to "these data cannot show it" (alone,
on gold, it changes no cell), which only a build that runs can say. Arm C
and both runs of arm R score 15 of 15 on both datasets, as on `main`.

### ADR-014 after the owner's answer

`1d26c2a` changes the text of decisions 2 and 3, which the owner approved,
and says so in a note under "The owner's answer" ("What the owner approved
is unchanged"). I held each added sentence against the approved text: the
lookups and the row template are cases of "what the decision binds" and of
"a dataset whose records themselves depend on the decision"; the optional
decision is a case of decision 1 ("a decision of the study that ... a
table needs and that has no value"); the denominator of outputs is what
"neither produced nor counted as not produced" means. I read no change of
meaning; finding 7 asks only that the owner be told.

### The report

docs/reports/std-issues.md at `42212b8`, held against the logs and runs
above: the R5 runs of `7095199` and of the axis test are reproduced line
for line; the log diffs it describes hold (finding 5 is answered); the kit
claim holds for the code of `42212b8`. Finding 9 names three places that
are not right yet, and its section "Gates on clean clones" is not final
(finding 8).

### The gates on clean clones of `42212b8`

Read in `build/gates/<wp>/clean-clone.log` of the worktree (each names
`commit: 42212b8` and checks out
`42212b85abade0fa050031a61c7b381971b2f391`). Each log was held, by my
`logdiff.py` (timing and paths left out), against the log of the same gate
on `37e5b61` (kept aside before the copies in docs/reports/ are replaced):

| Gate | Checks | Unit tests | Result | Against `37e5b61` |
| --- | --- | --- | --- | --- |
| std-1 | 12 PASS, 0 FAIL | 1118 passed, 23 deselected | GATE std-1: PASS | the unit count only |
| real-2 | 15 PASS, 0 FAIL | 1118 passed, 23 deselected | GATE real-2: PASS | the unit count, a timing inside a line |
| real-3a | 16 PASS, 0 FAIL | 1118 passed, 23 deselected | GATE real-3a: PASS | the same |
| gen-2a | 13 PASS, 0 FAIL | 1118 passed, 23 deselected | GATE gen-2a: PASS | the same |
| gen-3a | 15 PASS, 0 FAIL | 1118 passed, 23 deselected | GATE gen-3a: PASS | the unit count only |
| read-1a | 14 PASS, 0 FAIL | 1118 passed, 23 deselected | GATE read-1a: PASS | the unit count only |
| read-2a | 19 PASS, 0 FAIL | 1118 passed, 23 deselected | GATE read-2a: PASS | the unit count and the two axis lines above |

1118 is 1117 of `37e5b61` and the new test of `42212b8`. The log of
read-1a on `42212b8` is that of `d92dd57` (pass 1) but for the unit count,
the ASCII count and the trailer of the clean clone: the fixes and the
merge of read-2a change no line of the hand-made study, the arms, the
planted defects, the ten kits or the sweeps, as the report says for
`37e5b61`.

### Findings of pass 2

Findings 1 to 6 of pass 1 are settled (above). New ones, numbered on:

7. NOT BLOCKING. ADR-014's decisions 2 and 3 were edited after the owner
   approved them (`1d26c2a`), with a note under "The owner's answer" that
   says so. I read no change of meaning (section "ADR-014 after the owner's
   answer"), but the owner approved a text and the text changed: when the
   base session reports the merge to the owner, it should name the note.
   Failure scenario: the owner reads decision 2 later, finds the optional
   decision and the row template, and cannot tell whether those were
   approved; the note answers it only if the owner is pointed to it.

8. NOT BLOCKING (the coordinator is finishing it). The section "Gates on
   clean clones" of docs/reports/std-issues.md at `42212b8` held
   placeholders. In the worktree, while I wrote this (not committed), the
   table now holds the numbers of `42212b8` (the same as my table above),
   and the seven untracked copies docs/reports/std-issues.<wp>.gate.log are
   byte for byte build/gates/<wp>/clean-clone.log of `42212b8` (`cmp`).
   Still to do there: line 383 holds `GATES-COMMIT`, and the command on
   line 388 names `37e5b61`; both should name `42212b8`. Two sentences of
   the new text are not exact (rule R8): "The wrong cells are now owned at
   L4 by `pop.efficacy.rule` with `tfl.population` ... with
   `ae.start.imputation` for two of them" holds for the visible data; on
   the twin, 7 of the 9 are owned at L5 (`ars:An_AESUM_N`, `_Tot`) and 2 by
   `trt.start.source` with those, at L4. And against `main`'s log of
   read-2a, two more lines differ than the report names: the ASCII count
   (535 there, 541 here) and the wall time inside the cost line of the stub
   reader (1.1 s, 0.8 s). Failure scenario: the report merges with the
   placeholder and with a command that names a commit whose axis line
   differs from the merged code's.

9. NOT BLOCKING (rule R8, wording). In docs/reports/std-issues.md:
   "findings 1 to 4 are four new tests and two changed ones" (section
   "After pass 1"): `7095199` adds three tests and changes two, five in
   all, as the run below that sentence shows. Item 3 of the same list says
   that a dataset waits as a whole "and so does a decision whose lookups
   (intermediates) another column reads": the code leaves out the columns
   that read such a lookup (compiler.py:395-396), and the dataset only when
   a key or an ordering column is one of them. The first table still says
   that ADR-014 is "the owner's to approve"; it was approved on 2026-11-18.

### For the merge

This signature covers the code of `42212b8` and the seven logs of
`42212b8` named above. A later commit that changes only
docs/reports/std-issues.md and the copies of the logs (findings 8 and 9)
does not need another pass; one that changes code or a test does.

Verdict: SIGNED
