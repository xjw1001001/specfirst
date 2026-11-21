# Issue #30 P4 by class on a reference study: independent review

Reviewed: the work on issue #30 of `xjw1001001/specfirst` ("[P4] On a
real reference many decisions do not separate: classify them ...") on
branch `track/gen`, as it is at `b9a38f4`.

- The diff `cf1bddc..b9a38f4`. `cf1bddc` is `main` (the merge of
  track/read) and an ancestor of `b9a38f4`. The work is two commits:
  `8154075` (code, tests, ADR-019, docs/state/gen.md, CLAUDE.md, lesson 71;
  10 files, 1740 insertions, 4 deletions) and `b9a38f4` (the report, its
  nine logs, two paragraphs added to the Consequences of ADR-019; 10 files,
  1963 insertions). The worktree was clean at `b9a38f4` before and after
  the reviewer's runs (`git status --short` prints nothing).
- The files the findings quote, as committed at `b9a38f4`:

  | File | Lines | SHA-256 |
  | --- | --- | --- |
  | `src/specfirst/machine/separation.py` | 358 | `03870f659bf0ce90c0493929bbf70c9dc64ef75e57e22db9dd7eff12284e488c` |
  | `src/specfirst/gen/separate.py` | 465 | `891d0a0524ba06295d651e9d0fa0d029e6e72f59dc2c366121276e6de9e6f1a2` |
  | `src/specfirst/gen/sep01.py` | 272 | `63f43a60e8739c2ca29088f5d944715139388a3c282fc43c1f99ccf3bdc05f05` |
  | `src/specfirst/gen/command.py` | 391 | `105244cfd3f5ba87251516fd26c371082df3a8b7055bd38c63e83050ab191ea2` |
  | `tests/unit/test_separation.py` | 285 | `944b7cff7c6072cc2406ec6a42cde2e7fd85f04372b12b78f64124644f64ef68` |
  | `docs/decisions/ADR-019.md` | 235 | `1a30ba50fd3267d416fd7c333ed8644e14522da8b2180100f89a7ae8e55ec79a` |
  | `docs/reports/issue-30.md` | 639 | `bb8e6c95c07726be8441131510a120b0995593c00876cd27856a136b15bb36d7` |
  | `docs/state/gen.md` | 433 | `28b9661960422ee0b2a69b27038ff5b43c61c5c370b9461f141421cbb7c8f74a` |
  | `docs/reports/issue-30.sep01.log` | 108 | `9480d8899eb18a5fd62559d1c7556cc2348257727ec5642188593b80b24a824f` |
  | `docs/reports/issue-30.cdiscpilot01-house.log` | 102 | `df343a6c09833a0ffb610e8d8598b3810e76c905610d9280d65bda46afda98f2` |
  | `docs/reports/issue-30.cdiscpilot01-window.log` | 127 | `1c59c772368a54136b083baaebb4c006cdc7d8b33bd417c7d018d36e1ca789cd` |
  | `docs/reports/issue-30.plants.log` | 26 | `388748e5bc1127e25d97645fb11e77c959dde1fcf8c3773e814d9a508614d1e2` |

Date: 2026-11-21.

Reviewer: an independent agent with a fresh context that did not write the
work (rule R7). Correctness only, no style remarks. The reviewer changed no
tracked file, made no commit and wrote this file only. Nothing was pushed,
posted, labelled or closed; no package was installed; no model was called;
nothing was written into the fetch cache (R12). Every run went under
`flock /run/lock/specfirst-heavy.lock` with at most four worker processes.

## Outcome

No finding blocks. Each point of the brief, with the reviewer's own
evidence:

1. Scope. `git diff --name-only cf1bddc b9a38f4` names no file under
   `standard/` (schemas included), `kits/`, `src/specfirst/score/` or
   `src/specfirst/compile/`, and not PLAN.md, `gen/verify.py`,
   `gen/kits.py`, `gen/gate2.py` or `gen/__init__.py` (`GENERATOR =
   "gen-3a.2"` on `main` and at `b9a38f4`). No text of P4 changes. P4 as
   stated stays the requirement of generated kits: their matrix
   (`gen.verify.mutate`) is not touched. On a reference ADR-019 applies
   section 4.7, the decision record keeps its schema (`identifiable` in
   {separated, unseparated}), and the identifiability matrix has no
   schema. No ADR needed the owner first. CLAUDE.md has 59 lines.
2. The classes are those of the issue and complete. `classify` gives every
   combination of `read` and levels one of the four classes, or
   `no_alternative` when nothing was tried. `identifiable` is `separated`
   for `separated` only, `unseparated` for the other three, empty for
   `no_alternative`, as for a generated kit (`verify.identifiable`). The
   review lists `unseparated` first, then `separated_at_dataset_only`. The
   definitions are defensible (section "The definitions against PLAN.md
   and the issue"), with two edges noted in F2 and F3.
3. The static reach. The reviewer found no decision called `inert` while
   an output reads it, and none called `read` while none does: on SEP01
   and on the pilot, no value of an inert decision changes a column that
   an analysis reads, and every `read` decision of SEP01 sets something
   the table counts (R7); the reach covers every kind of element a
   compile can change (section "What was read"). A reach without its walk
   over `derives_from` fails the test file (R3, S1), and `problems`
   catches an inert decision whose value changes an output (R3, M4; R8).
4. The interval. On SEP01 (35 to 38; 34 and 39 separate) and on seven
   pairs of gold value and span that reach the slot's minimum or the scan
   limit, every interval, every end and every list of values is what the
   reviewer worked out by hand (R4, R5); a value seen twice is built once;
   the scan stops at the first value that separates. On the pilot every
   end of the interval 13 to 36 is explained by the reviewer's own count of
   the late events (R9). The tests do not hold the limits of the scan (F1).
5. SEP01. The table, the window, the inert rule and the dataset-only rule
   are what the docstring says (R5). `CLASSES` is what mutation gives (R1:
   30 passed; R6: the command's output equals the committed log line for
   line), and every entry is plausible from the data (R5).
6. Rule R5. Each of the four plants makes the check of its class fail (R1,
   R8). Nine mutants of `separation.py`, the brief's two among them, each
   fail the test file (R3). Two mutants of the scan in `separate.py` pass
   it (F1).
7. The pilot. Both vectors give the committed logs line for line (R6). The
   SDTM is read through `separate._pinned`, which checks the SHA-256 of
   every file against kits/cdiscpilot01/kit.yaml before reading it; no file
   of the fetch cache is newer than a marker set before the runs, and the
   worktree is clean (R12).
8. The report. Every result it states is in a command output of the report
   or of the nine logs it names (R10); its description of the pilot's arm
   doses has no output (F4), and its plants come from a script that was
   not kept (F5).
9. The note for the read track in docs/state/gen.md is accurate about the
   scorer today (R11). One path in the code part of the note is loose (F6).
10. `ruff check src tests`: "All checks passed!"; `python -m
    specfirst.asciicheck`: "612 files checked, 0 with non-ASCII bytes"
    (R2). This file is ASCII.

## The definitions against PLAN.md and the issue

- `separated` only when every value tried separates. PLAN.md section 4.6
  states P4 for every other listed alternative ("changing any decision to
  another listed alternative changes at least one result"), and section
  4.7 marks a decision `unseparated` where data cannot separate two
  alternatives; one value that reproduces is such a pair. The issue's
  table says "an alternative changes the reference", but under that looser
  reading the issue's own first example (a window that four values
  reproduce, while 7 days does not) would be `separated`. The generated
  kits read it the same way (`verify.mutate`: `separated` when every pair
  of the gold value separates). Mutant M3 (the looser reading) fails six
  tests (R3).
- The levels. The issue speaks of the reference as printed ("the same
  cells in the summary table", "changes ADaM but not the outputs that read
  it"), P2 compares grid text with a reference, and the matrix of a
  generated kit compares grids. Section 4.6's test column reads "diff the
  ARD"; ADR-019 names that departure and puts it to the owner (item 2).
  On a real reference a person holds the CSR, not its ARD, so separating
  at the printed outputs is the reading that never credits what the
  reference cannot show. Defensible. Two edges of it: F2 (`fails`) and F3
  (an ARD row identified by its grouping).

## Findings

### F1 (not blocking) The limits of the scan are held by no test

`Mutation.scan` stops at the slot's minimum (`int(minimum)`), at `span`
steps from gold, or at the first value that separates. On SEP01 the
window's scan ends at 34 and 39, far from either limit, and no other
integer slot of the slice is scanned there; so no test reaches a limit.
Two planted defects of the scan pass all 30 tests (R3):

- S3, the value at a limit is not built (`>`/`<` for `>=`/`<=` in the
  loop): every interval that reaches a limit then stops with `ValueError:
  days = 0 was not scanned` (5 of the 7 cases of R4);
- S4, the slot's minimum is ignored (`low_limit` stays `gold - span`):
  silently wrong. On a SEP01 window of 3 days it builds windows of -1 to
  -15 days, which the compile accepts although the catalog says `min: 0`,
  and reports the interval -14 (`separated`) to 6, where the committed
  code gives 0 (`slot_minimum`) to 6 (R4).

The committed code is right in all seven cases worked out by hand (R4),
`separation.interval` is tested at both kinds of end with given levels, and
the interval of the report (pilot, 13 to 36) reaches no limit; nothing the
report states is wrong. A test of a window near the minimum and of a short
span would hold the scan; the reviewer's cases are ready to use: gold 3
gives 0 (`slot_minimum`) to 6 (`separated`); gold 3 with span 2 gives 1 to
5, `scan_limit` on both sides; gold 35 with span 3 gives 35 (`separated`)
to 38 (`scan_limit`).

### F2 (not blocking) A value that cannot be built separates, whatever stops it

ADR-019 decision 1 counts `fails` with `outputs`, and the presence check of
`compare` counts an output that one build has and the other has not. A
value that the machine cannot build for a reason of its own (layout draft
0, an engine, the compile) then counts as evidence against that value, and
a decision whose other values all fail would be `separated` and
`identifiable: separated`: credited without the data having shown a
difference. That is the one way a decision can be credited wrongly. It
does not happen in this work: on the pilot no value fails (`fails 0` in
both vectors, R6). On SEP01 one value fails, `tfl.population` = efficacy
("grouping 'Grp_TRT01P': no record of ADSL in the analysis set has a
value"), and the class `separated` of `tfl.population` rests on counting
that failure as a separation; there the failure is the data's: no subject of SEP01 is in the efficacy set (no
SYSBP record), so no table on that set can print the reference's N of 3,
3, 3. The generated kits read a failed build the same way (`verify.mutate`
appends a view `failed`, which differs from every grid). For the owner's
item 2 or for the read track: a failure that is the machine's rather than
the data's should not credit a decision.

### F3 (not blocking) An ARD row that differs only in its ID counts as a result

`result_changes` compares ARD rows by ID, and an ID names its grouping. A
value that groups by another variable with the same values (planned and
actual treatment equal for every subject: the plant against `separated`)
changes every ARD row by name and no number: `planned=results (adam 0,
results 66, cells 0)` (R8), so the decision is `separated_at_dataset_only`,
not `unseparated`. ADR-019 says so (Consequences, added in `b9a38f4`). Only
the name of the grouping variable tells the two values apart, which a
reference with its ARS or ARD file shows and a CSR does not. The decision
is asked either way, second instead of first; the report's table and the
plants log say exactly this. Not blocking; worth a line in the review
text a person reads ("the results differ in the name of a grouping only")
when std-2 takes the classes.

### F4 (not blocking) The doses of the pilot's arms are not shown by any output

Section "cdiscpilot01, report only" of the report says the arms are "Pbo 0
mg, Xan_Lo 54 mg, Xan_Hi 81 mg"; the matrix prints no arm, and no command
output in the report or in its logs shows them. They are true: the
reviewer's call of `separate.pilot_arms` on the pinned SDTM gives
`[{'code': 'Pbo', 'dose': 0.0, ...}, {'code': 'Xan_Lo', 'dose': 54.0, ...},
{'code': 'Xan_Hi', 'dose': 81.0, ...}]` and no arm for the screen failures
(R7). They describe the input of the runs (the public design of the pilot:
placebo, xanomeline 54 and 81 mg), not a result; no class, count or
interval of the report depends on them beyond their order, which only
orders the columns. The brief makes an unbacked number blocking; the
reviewer reads that rule as applying to the numbers the report offers as
evidence of its results, and these are not such numbers. Rule R8 still
asks for the command: one line of output (for example printed in the house
log) settles it. The count "18" of custom decisions is that of the file the
report names (`wc -l` 18; 18 lines with `custom:`).

### F5 (not blocking) The plants log comes from a script that was not kept

docs/reports/issue-30.plants.log is the output of `python plants.py`, "a
scratch script of the session, not kept", so the command cannot be run
again as written. The tests hold the same four plants (the class of the
decision changes, and `sep01.check` names that decision only), and the
reviewer's own script, which calls `sep01.planted`, `separate.Mutation(...)
.matrix(keys=[...])` and `sep01.check`, prints the same classes, the same
interval 35 to 35 and the same lines of the check (R8), including the class
`separated_at_dataset_only` of the plant against `separated`, which the
report's table states and the tests do not assert.

### F6 (not blocking) A path in docs/state/gen.md

The note says "the matrix goes to build/separation/<study>.json"; for the
pilot the command writes `build/separation/cdiscpilot01-<vector>.json`
(`command._separate`), as the report's logs show. Text only.

## What was read

`CLAUDE.md`; PLAN.md sections 2 (2.1 to 2.4), 4.3 to 4.8, 6.5, 8, 9 and
13.5; the issue (`gh issue view 30 -R xjw1001001/specfirst`, read only);
ADR-019 in full, ADR-007 decision 6 and the owner's answer on it;
`docs/reports/issue-30.md` and its nine logs; the part of docs/state/gen.md
the work adds; lesson 71; docs/state/std.md (std-2 not started);
`docs/reports/issue-27.review.md` (the form). In full:
`src/specfirst/machine/separation.py`, `src/specfirst/gen/separate.py`,
`src/specfirst/gen/sep01.py`, `tests/unit/test_separation.py`,
`src/specfirst/score/candidate.py`; the diffs of `gen/command.py` and
`cli.py`. In part: `compile/compiler.py` (`ARS_LISTS`, `FRAGMENT_PARTS`,
the writing of fragments and dataset specs, `other_values`),
`machine/ars.py` (`reads`, `columns`), `gen/verify.py` (`mutate`,
`identifiable`), `gen/display.py` (where the columns of a grid come from),
`score/reading.py`, `score/report.py`, `score/kit.py`, `score/pilot.py`,
`score/scorer.py` (`separation`), `paths.py`,
`standard/catalog/entries/ae.teae.end.yaml` and its template,
`standard/schemas/decision-record.schema.json`, `kits/cdiscpilot01/kit.yaml`
(the pinned SDTM).

What an output reads, traced by hand. `reach` takes the analyses behind
every cell of a grid (numerators and, through `cell_paths`, the
denominators), their analysis sets, data subsets, groupings and methods,
the output and every part of its layout; the ADaM columns `ars.reads` names
for those analyses (variable, set, subset and grouping conditions, model
terms); the walk over `derives_from` edges to other ADaM columns; and for
each column the working columns, lookups and row templates its rule passes
through (`passes_through`). `element_changes` names the same kinds of
element: ARS elements of the six lists, layout parts, and the columns,
intermediates and row templates of fragments, the only parts a fragment may
write (`FRAGMENT_PARTS`). The column headers of the AE summary come from
the treatment grouping (an element of the reach), its groups listed from
ADSL. A value whose compile fails changes every element (`element_changes`
with an empty side) and is read by every output; a value whose build fails
after a good compile is read through its compile only, and if it is then
unread, `problems` reports it. So for the AE summary no element that a
decision can change and that changes a printed text is outside the reach.

## What was run

All Linux commands ran in Ubuntu 24.04 under WSL2 as root, from script
files kept outside the repository, after the `scripts/env.sh` of the
worktree, with `PYTHONDONTWRITEBYTECODE=1`, in two acquisitions of `flock
/run/lock/specfirst-heavy.lock` (07:47 to 07:53 and 08:10 to 08:11 UTC),
under `taskset -c 0-3`, at most four processes at a time. `<scratch>` =
`/root/scratch-review30`; `<scratch>/base` is a copy of the worktree at
`b9a38f4` (without build/ and .git); each mutant is a copy of it with one
exact replacement, run with `SPECFIRST_ROOT` and `PYTHONPATH` set to the
copy (each log prints the module file it loaded). Python 3.12.3, ruff
0.17.4.

| # | What | Result |
| --- | --- | --- |
| R1 | the test file in the worktree | 30 passed in 56.53 s |
| R2 | ruff and the ASCII check in the worktree | All checks passed; 612 files, 0 with non-ASCII bytes |
| R3 | 12 mutants: 9 of `separation.py`, 3 of `separate.py` | 10 fail the test file (1 to 6 tests each); S3 and S4 pass 30 of 30 (F1) |
| R4 | the scan at its limits on SEP01: 7 pairs of gold and span, on the base copy and on S3, S4 | as worked out by hand; S3 stops in 5 of 7; S4 gives -14 to 6 |
| R5 | SEP01 by hand | table, window, inert rule, dataset-only rule and every class as the study states |
| R6 | `specfirst gen separate sep01`, `cdiscpilot01 --vector house`, `--vector window`, `--out` under `<scratch>` | each equals its committed log line for line (101, 95, 120 lines); 48, 42, 67 builds |
| R7 | the columns that the values of the inert decisions change, against the columns the analyses read | SEP01 10 values, pilot 12 values: none read; the pilot's arms |
| R8 | the four plants again, by the reviewer's script | the classes, interval and check lines of the plants log |
| R9 | the pilot's adverse events after the last dose, by day (reviewer's count) | 13 (1), 14 (3), 37 (4), none from 15 to 36 |
| R10 | every output block of the report against the logs it names | 0 lines missing in 8 blocks; 2 blocks (pytest) stand in the report itself |
| R11 | the scorer, for the note of docs/state/gen.md | as the note says |
| R12 | the fetch cache and the worktree after the runs | 0 files newer than the markers; `git status --short` empty |

### R1 The test file in the worktree

```text
$ python -c 'import specfirst; print(specfirst.__file__)'
/mnt/d/trial_work/specfirst-gen/src/specfirst/__init__.py
$ time taskset -c 0-3 python -m pytest tests/unit/test_separation.py -v -p no:cacheprovider
...
tests/unit/test_separation.py::test_a_planted_matrix_differs_from_a_new_mutation PASSED [ 96%]
tests/unit/test_separation.py::test_the_arms_of_a_study_come_from_dm_and_ex_in_the_order_of_the_dose PASSED [100%]
============================= 30 passed in 56.53s ==============================
worktree tests exit 0
```

The 30 test names are those of the report's listing.

### R2 Ruff and ASCII

```text
$ ruff check --no-cache src tests
All checks passed!
$ python -m specfirst.asciicheck
ASCII check: 612 files checked, 0 with non-ASCII bytes
```

### R3 Mutants

`python -m pytest tests/unit/test_separation.py -q -p no:cacheprovider
--tb=line -rf` in each copy. A mutant is made only when its pattern occurs
exactly once (all 12 were made).

| Mutant | The change | Result | Tests that fail |
| --- | --- | --- | --- |
| M1 | `classify` treats `adam` as `none` (the brief's first) | 4 failed, 26 passed | the class table [outputs, adam]; the dataset-only rule; every class of SEP01; the plant against `separated_at_dataset_only` |
| M2 | `interval` ignores the scan limit: an end at the limit is always the slot's bound (the brief's second) | 1 failed | the interval's ends |
| M3 | `separated` when any value separates | 6 failed | the class table (3 rows); the window of four values; every class; the plant against `unseparated` |
| M4 | `problems` never flags an inert decision | 2 failed | the inert problem; the planted reach |
| M5 | the interval stops at a value of level `adam` | 1 failed | the interval's ends |
| M6 | `identifiable` is `separated` for `separated_at_dataset_only` too | 2 failed | both tests of `identifiable` |
| M7 | the review puts `separated_at_dataset_only` before `unseparated` | 2 failed | both review tests |
| M8 | `compare` ignores the ARD | 1 failed | the three layers |
| M9 | `differences` ignores the intervals | 1 failed | the planted matrix |
| S1 | `reach` without the walk over `derives_from` | 3 failed | the dataset-only rule; every class (`trt.date.imputation` and `ae.start.imputation` become `inert`); its plant |
| S3 | `scan` does not build the value at a limit | 30 passed | none |
| S4 | `scan` ignores the slot's minimum | 30 passed | none |

### R4 The scan at its limits

A script of the reviewer builds `separate.Mutation(machine, sep01.data(),
sep01.ARMS, records, span).matrix(keys=[ae.teae.end])` with the window
set to the gold value of each case. By hand from SEP01 (R5): the events
start 7 (H2), 35 (P2) and 39 (L2) days after a last dose, so a window of d
days gives the table of 35 days for d in 35..38 and that of 3 days for d in
0..6; the slot's minimum is 0, and 30 and 7 are the catalog's examples,
tried anyway. On the base copy:

```text
gold 35 span 30: class unseparated; interval 35 (separated) to 38 (separated); same [36, 37, 38]; dataset_only []; problems []
gold 35 span 3: class unseparated; interval 35 (separated) to 38 (scan_limit); same [36, 37, 38]; dataset_only []; problems []
gold 35 span 2: class unseparated; interval 35 (separated) to 37 (scan_limit); same [36, 37]; dataset_only []; problems []
gold 3 span 30: class unseparated; interval 0 (slot_minimum) to 6 (separated); same [0, 1, 2, 4, 5, 6]; dataset_only []; problems []
   values: end_of_study=outputs, last_dose_plus_days(days=0)=none, last_dose_plus_days(days=1)=none, last_dose_plus_days(days=2)=none, last_dose_plus_days(days=30)=outputs, last_dose_plus_days(days=4)=none, last_dose_plus_days(days=5)=none, last_dose_plus_days(days=6)=none, last_dose_plus_days(days=7)=outputs, no_end=outputs
   each value once: True
gold 3 span 2: class unseparated; interval 1 (scan_limit) to 5 (scan_limit); same [1, 2, 4, 5]; dataset_only []; problems []
gold 1 span 30: class unseparated; interval 0 (slot_minimum) to 6 (separated); same [0, 2, 3, 4, 5, 6]; dataset_only []; problems []
gold 0 span 30: class unseparated; interval 0 (slot_minimum) to 6 (separated); same [1, 2, 3, 4, 5, 6]; dataset_only []; problems []
exit 0
```

Every case prints "each value once: True": in gold 3 span 30 the value 7,
an example of the catalog and the first that separates going up, stands
once, and the scan stops there (8 is not built). With span 2 the value 0,
a legal value, is not scanned, and the end says `scan_limit`, not
`slot_minimum`. On S3 the first case passes, the next five stop (`ERROR
ValueError: days = 38 was not scanned`, ... `days = 0 was not scanned`),
gold 0 passes. On S4:

```text
gold 3 span 30: class unseparated; interval -14 (separated) to 6 (separated); same [-14, -13, -12, -11, -10, -9, -8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 4, 5, 6]; dataset_only []; problems []
```

### R5 SEP01 by hand

From `sep01.SUBJECTS` and `sep01.EVENTS` (2024, February of 29 days):

- After the last dose: P2's rash 03-15 after 02-09 is 20 + 15 = 35 days;
  L2's fatigue 03-20 after 02-10 is 19 + 20 = 39; H2's cardiac arrest 02-20
  after 02-13 is 7. P1 (01-15), L1 (01-20), L3 (01-20) and H1 (01-25) are
  within treatment. The plant's cough of P3, 03-17 after 02-10, is 36.
  Hence 35 to 38 reproduce, 34 drops the rash (Placebo, any event, 2 to
  1), 39 adds the fatigue (Low Dose 2 to 3); with the plant, 36 separates
  too and the interval is 35 to 35.
- The table, by actual treatment (L4 is High Dose): N 3, 3, 3, 9. Any
  event: P1, P2 / L1, L3 / H1, H2: 2, 2, 2, 6. Related (POSSIBLE,
  PROBABLE): L1, H1: 0, 1, 1, 2. Serious: L1, H2: 0, 1, 1, 2. Drug
  withdrawn: H1: 0, 0, 1, 1. Fatal: H2: 0, 0, 1, 1. Percents 66.67, 33.33,
  22.22, 11.11: none on a half, so the rounding rule cannot separate. This
  is `sep01.EXPECTED`.
- Inert: the origin of the study day changes ADVS.ADY (9 subjects x 2
  records) and ADAE.ASTDY (8 records): 26 cells, the log's count; the
  summary reads neither (R7: the 9 columns the analyses read are SAFFL,
  TRT01A, TRTEMFL, RELGR1, AESER, AEACN, AESDTH and the two subject keys).
- Dataset only: L3's dizziness in 2024-01, first dose 01-12. Gold (first
  of month, not before the first dose) gives 01-12, emergent; first of
  month gives 01-01, not emergent; L3 is counted in "any" by the headache,
  and the dizziness (causality NONE, not serious, dose not changed, not
  fatal) is in no other row. With the plant's full date both imputations
  give the same build (R8: `none`, adam 0).
- The other entries of `CLASSES`, from the log: L4 moving to Low Dose under
  `pop.safety.grouping` = planned changes 10 cells (N 2, any 2, related
  2, serious 2, withdrawn 1, fatal 1); `trt.actual.source` = same as
  planned changes 3 ADaM cells (L4 in ADSL and in its 2 ADVS records, L4
  has no event); `tfl.percent.format` = one decimal always changes the 6
  zero cells; one exposure record with full dates per subject and RFXSTDTC
  = the first dose make the sources and the imputation of the treatment
  dates reproduce; every subject randomized makes `randomized_and_dosed`
  reproduce; no causality PROBABLE makes `["POSSIBLE"]` reproduce; the
  arms in the order of the dose make `protocol_order` reproduce; "Active
  Control" names no arm. All plausible.

### R6 The command, three times

```text
$ time taskset -c 0-3 specfirst gen separate sep01 --out <scratch>/sep01.json                          # real 0m51.863s, exit 0
$ time taskset -c 0-3 specfirst gen separate cdiscpilot01 --vector house --out <scratch>/pilot-house.json  # real 1m22.338s, exit 0
$ time taskset -c 0-3 specfirst gen separate cdiscpilot01 --vector window --out <scratch>/pilot-window.json  # real 2m9.000s, exit 0
```

Each output, without the command line, the path of the matrix, the time
and blank lines, held against the committed log stripped the same way:

```text
== sep01-command vs issue-30.sep01: 101 and 101 lines
   identical
== pilot-house vs issue-30.cdiscpilot01-house: 95 and 95 lines
   identical
== pilot-window vs issue-30.cdiscpilot01-window: 120 and 120 lines
   identical
```

So every class, level, count, interval and problem count of the three logs
is reproduced, including `fails 0` on the pilot in both vectors, 42 and 67
builds, and `problems: 0`.

### R7 Inert decisions against what the analyses read

A script of the reviewer builds gold and every value of every decision
the matrix calls `inert`, lists the ADaM columns that differ (a column of
another length counts), and intersects them with the columns that
`ars.columns` gives for the reporting event of either build:

```text
sep01: the analyses read 9 ADaM columns: ['ADAE.AEACN', 'ADAE.AESDTH', 'ADAE.AESER', 'ADAE.RELGR1', 'ADAE.TRTEMFL', 'ADAE.USUBJID', 'ADSL.SAFFL', 'ADSL.TRT01A', 'ADSL.USUBJID']
  trt.planned.source = dm_armcd_map(map=[{"code": "A", ...}, {"code": "B", ...}]): level adam; 3 columns differ; read by an analysis: none
  date.studyday.origin = dm_rfstdtc: level adam; 2 columns differ; read by an analysis: none
  pop.randomized.rule = randomized_with_postbaseline(test="SYSBP"): level adam; 3 columns differ; read by an analysis: none
  disp.status.record = disposition_event_by_subcategory(subcategory="END OF STUDY"): level adam; 2 columns differ; read by an analysis: none
  (6 more values: level none, 0 columns differ)
pilot arms: [{'code': 'Pbo', 'dose': 0.0, 'names': ['PLACEBO', 'Placebo']}, {'code': 'Xan_Lo', 'dose': 54.0, 'names': ['Xanomeline Low Dose']}, {'code': 'Xan_Hi', 'dose': 81.0, 'names': ['Xanomeline High Dose']}]
cdiscpilot01: the analyses read 9 ADaM columns: (the same 9)
  trt.end.source = ds_date_when_ex_missing: level adam; 2 columns differ; read by an analysis: none
  trt.end.source = last_ex_start_date: level adam; 25 columns differ; read by an analysis: none
  (10 more values of trt.planned.source, date.studyday.origin, pop.randomized.rule, pop.efficacy.rule, disp.status.record: 0 to 3 columns differ, read by an analysis: none)
exit 0
```

No value of an inert decision changes a column an analysis reads, on
either study. The other way: a decision is `read` only when the compile of
one of its values changes an element of the reach, or the value adds or
drops an output; no decision of the three matrices is read only through a
value whose compile fails (the one value that fails, R6 and F2, compiles
and stops at the results). Traced by hand from the templates, every `read`
decision of SEP01 sets what the table counts: TRT01A or the grouping, SAFFL
or the analysis set, RELGR1, TRTEMFL through TRTSDT, TRTEDT, ASTDT or the
working columns of the window, or an element of the ARS file or the
layout.

### R8 The plants again

```text
== separated: pop.safety.grouping: class separated_at_dataset_only; intervals []
   values: planned=results (adam 0, results 66, cells 0)
   check: pop.safety.grouping (mod-populations): separated_at_dataset_only; the study states separated
== unseparated: ae.teae.end: class separated; intervals [{'slot': 'days', 'gold': 35, 'low': 35, 'high': 35, 'below': 'separated', 'above': 'separated', 'same': [], 'dataset_only': []}]
   check: ae.teae.end (mod-ae-emergence): separated; the study states unseparated
   check: ae.teae.end (mod-ae-emergence): the interval is [...]; the study states {... 'low': 35, 'high': 38, ...}
== separated_at_dataset_only: ae.start.imputation: class unseparated; intervals []
   values: first_of_month=none (adam 0, results 0, cells 0), not_completed=none (adam 0, results 0, cells 0)
   check: ae.start.imputation (mod-ae-emergence): unseparated; the study states separated_at_dataset_only
== inert (planted reach): [('date.studyday.origin', 'inert'), ('ae.teae.end', 'inert')]
   check: ae.teae.end (mod-ae-emergence): inert, yet end_of_study changes the outputs
   ... (the same seven lines as the plants log)
exit 0
```

### R9 The pilot's late events

A script of the reviewer reads the pinned SDTM through
`separate.pilot_data` (hashes checked) and counts the adverse events of
dosed subjects with a full start date after the last EXENDTC of the
subject (`trt.end.source` = `last_ex_end_date`), by days after it:

```text
dosed subjects 254 with an end date 252
events with a partial start date (left out of this count): 26
events with a full start date after the last dose, by days after it:
    1: 16    2: 7    4: 4    5: 1    6: 3    7: 1   13: 1   14: 3   37: 4
events 10 to 40 days after the last dose: subject, arm, days, rows, rows not kept by 12:
  01-715-1319 Xanomeline High Dose    13 ['any'] new ['any'] AEREL NONE
  01-710-1070 Xanomeline High Dose    14 ['any'] new [] AEREL NONE
  01-718-1066 Xanomeline Low Dose     14 ['any'] new [] AEREL REMOTE
  01-718-1066 Xanomeline Low Dose     14 ['any'] new [] AEREL POSSIBLE
  01-705-1303 Xanomeline High Dose    37 ['any'] new ['any'] AEREL POSSIBLE   (4 events)
```

(The count is printed one value per line; joined here. "new" is the rows
among any, serious, withdrawn and fatal that no event of the subject kept
by a window of 12 days already gives; the script does not look at the
related row.) No event with a full date starts 15 to 36 days after a last
dose, so every window from 14 to 36 days gives the ADaM of 30 days
(`none`). 13 drops the three events of day 14, whose subjects keep other
emergent events in those rows (`adam`, no cell; that the related row of
01-718-1066 does not change either is the run's finding, not checked by
this count). 12 also drops the event of day 13, the only emergent event of
its subject: "any", High Dose and total, 2 cells. 37 adds the four events
of one High Dose subject with no other emergent event, causality POSSIBLE:
"any" and "related", High Dose and total, 4 cells. These are the log's
levels and cells. The count leaves out 26 events with a partial start
date; it explains every end of the interval without them.

### R10 The report's outputs against its logs

A script of the reviewer takes every `text` block of the report and looks
for each of its non-blank lines in the logs: the SEP01 run (51 lines), its
check (3), the plants (26), the house run (48, its "(five of 22)" heading
aside), the window run (66) and its check (3) are found line for line (0
missing); of the gate blocks only the command line, which the logs do not
repeat, is missing. The two pytest blocks (30 passed in 58.87 s; 1238
passed in 1181.00 s) are outputs given in the report itself. The prose
numbers of the report (26, 4 and 3 ADaM cells; 9, 7, 6 and 0 decisions;
13 to 36, 12 and 37, 7, 2 and 4, 11, 68, 82 and 372,426 cells) are in those
logs; the gold table is held by a test and by R5.

### R11 The scorer, for the note

`score/reading.py`: "A decision that gold marks `unseparated` is scored
like any other here: its values are compared." `score/report.py` lists
"unseparated in gold, compared by value only". `score/kit.py` reads the
matrix of a generated kit (`unseparated_read`, `unseparated_not_read`,
`matrix_problems`). `score/pilot.py` has no word `identifiab`, `matrix` or
`unseparated`. No exam of section 11.4 exists. `separation.credited` is
called by no scorer, as the note says ("What is left for the scorer"). Under
the house vector the three table decisions that are `unseparated` on the
pilot are `tfl.columns.arms`, `tfl.columns.total` and `tfl.rounding.rule`
(R6). The note is accurate.

### R12 The cache and the worktree

```text
SPECFIRST_CACHE=/root/.local/share/specfirst/cache
files of the cache newer than the marker: 0        (first acquisition)
files of the cache newer than the marker: 0        (second acquisition)
$ git -C D:/trial_work/specfirst-gen status --short
(nothing)
```

The marker of each acquisition was set before its pilot runs.

## For the owner

Nothing in this work is the owner's to decide before it merges: no case of
PLAN.md section 2.3 applies, and nothing under PLAN.md or
`standard/schemas/` changed. ADR-019's three points stand for later; F2 and
F3 add to its item 2 (what "separated" means on a reference): a failure of
the machine, and a difference of names only in the ARD, both count as a
difference today.

Verdict: SIGNED
