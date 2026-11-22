# catalog-2c: the slice on catalog@2 and open-default@2 (ADR-020, part 3 of 3)

Work package catalog@2, track std, part catalog-2c: decision 8 of ADR-020 as
the owner amended it (question 4, answer B). The slice of ADR-005 moves from
(`catalog@1`, `open-default@1`) to (`catalog@2`, `open-default@2`), frozen
in catalog-2b. The base session gave all of it to the std track, in one
package with one review: the gen and read tracks left their files alone
while it was open. `catalog@1` and `open-default@1` stay frozen and
loadable by label.

Commits on track/std, from main `6cdeded`: `681697b` (the part), `982e7cb`
(five checks of three gates fixed after their first run on clean clones),
`b183940` (the findings of the review, pass 1), `f5de3fb` (the generator
label `catalog-2c.2`: the kits changed with F1), `9d4b48f` (the five new
texts and the kept dry run of `catalog-2c.2`), `1e24e3c` (main merged in:
issue #29 of track/real, below), `03f12fe` (G1 of the review, pass 2: the
pilot report's summary), and one commit of documents after it (this report,
the review, the gate logs, docs/state/std.md and docs/state/gen.md).

## What changed

### The default pair and the gate std-1

- `versions.DEFAULT_CATALOG`, `DEFAULT_HOUSE` = `catalog@2`, `open-default@2`.
  Every loader, the generator, the scorer and the harness take them.
- The gate std-1 checks `catalog@1`, `open-default@1` by label
  (`compile.gate.FIRST`; its commands name `--catalog catalog@1 --house
  open-default@1`): the gates catalog-2a and catalog-2b check version 2, and
  std-1 keeps holding the frozen version 1 loadable. The tests of std-1
  (planted defects, the alternatives on the tiny study, the compiler, the
  standard form) name version 1 the same way.

### The generator (gen; `GENERATOR` = `catalog-2c.2`)

`catalog-2c.1` wrote the kits of `681697b`; the fixes of pass 1 (F1, F4)
change the bytes the same design and seed give, so the label moved to
`catalog-2c.2` (`f5de3fb`). Every kit, task and run below is of `catalog-2c.2`.

- Probes. New, each with its recipe (`probes.RECIPES`), its check
  (`present.FINDERS`) and its plant (tests/unit/test_gen_probes.py, `UNDO`):
  - `undosed_record_after_last_dose` (#24, `trt.end.source/last_ex_record_end`):
    the last exposure record of a dosed subject is cut three days before its
    end, and the three days get a record of dose zero (not placebo); an event
    the window plus two days after the last record with a dose is emergent
    only when every record ends treatment.
  - `ae_timed_before_timed_first_dose` (#5, `ae.teae.start/by_time_when_collected`):
    an event on the first dose date, collected two hours before the dose time.
  - Gone with `ae.teae.end/end_of_study` (#3): `ae_starts_after_end_of_study`,
    `ae_between_window_end_and_end_of_study`.
- `REACHES`: the end-of-study record is read only by the disposition date that
  stands in for a missing exposure end date; `ae.teae.end` has no pair
  condition left; `_ALL_ROWS` is the six standard rows of catalog@2;
  `tfl.rounding.rule` is claimed at one decimal only (`tfl.percent.format`
  with `decimals` 1: the planted percentages lie on a half at one decimal,
  and at 0 or 2 decimals both rules agree; F1).
- The window (F1): the probes of `ae.teae.end` are built around the house's
  default window (`probes.house_window()`, 30 days under open-default@2), so
  that a kit that takes the default tells it apart from `no_end` whatever
  the follow-up length of its design; a study may state the follow-up length
  instead (`Parameters.follow_up_days`, a second value of the slot `days`).
  The test of REACHES holds both claims on a vector of each kind.
- Sampling (`decisions.py`):
  - a stated value is any alternative with any combination of its slot
    values but the default's (`decisions.stated`); the sampler draws an
    alternative first, then its slot values (F4): `one_decimal_always` is
    stated with 0 and 2 decimals as well, `last_dose_plus_days` with the
    follow-up length;
  - `tfl.percent.format` draws its decimals from 1, 0 and 2 (the first is the
    one the rounding probe separates with);
  - `stated_rows` has two more lists, with SERIOUS_RELATED, DOSE_MODIFIED and
    FATAL_RELATED;
  - the scenarios that named `end_of_study` name `no_end`;
  - the held-out combination is the total over all arms with the protocol
    order: under open-default@2 a table has no total column by default, so
    the total over all arms stands where "none" stood (two stated
    alternatives, as before).
- The reference (`reference.py`) reads catalog@2: the six standard rows in the
  order of the ARS example; the decimals slot (a whole number under the mask
  "XXX" is not padded, as display.pattern says); emergence by time where both
  times were collected (READING: the dose time counts as collected when it is
  after 00:00); the latest end of any exposure record; the randomized subject
  by a disposition record RANDOMIZED, the planned arm code when the study has
  none.
- Defaults by design: `documents.statuses` and `without_default`, the gate
  gen-3a's plant and the separation take the design's features
  (`checks.base_vector(..., features)`, `separate.house_vector(..., features)`).
- The kit summary shows a house anchor by entry ID without the ID (its line
  of 100 characters would not hold `house tfl.output.include/tfl-demographics`).
- core_findings.yaml: the event after the end of the study is explained by
  `no_exposure_end_date` alone.
- SEP01 (#30): the AE table gains AEBODSYS (the columns of the tiny study);
  `FEATURES`; `EXPECTED` worked out again; `CLASSES` from mutation (below).

### The natural form

On `681697b`, 21 statements of the kits of the gate seed had no accepted
text: the changed and new statements of catalog@2 (decimals, the standard
rows, emergence by time, the window "that day included", the latest start of
a dosed record), and statements new to these kits because the sampling draws
other values (arm code maps, causality lists, row lists, the BMI rule, the
age groups). Two calls, both accepted on the first attempt; no regeneration,
no phrasing template:

```text
$ specfirst gen natural requests --kits <kits> --out .../catalog-2c-rewrite-1.request.json
.../catalog-2c-rewrite-1.request.json: 21 paragraphs, 0 filler
$ specfirst gen natural propose ... --call catalog-2c-rewrite-1 --tokens 57251 --tool-uses 2 --seconds 14
027d3ea21e53817d tfl.percent.format: attempt 1: slots ok
... (21 lines "slots ok")
$ specfirst gen natural readback ... --call catalog-2c-readback-1 --tokens 60793 --tool-uses 2 --seconds 9
027d3ea21e53817d tfl.percent.format: attempt 1: read back as one_decimal_zero_blank: ACCEPTED
... (21 lines ACCEPTED)
store .../src/specfirst/gen/rewrites: 82 statements, 82 accepted (0 by the phrasing template), 0 open; 10 of 10 filler paragraphs accepted; 5 calls, 308925 tokens
the kits state 68 statements; without an accepted text: 0
```

The store grew by 21 lines of paragraphs.jsonl and 2 of calls.jsonl; no line
changed. The final message of the read-back was saved with CRLF before the
commit; it was turned to LF and its recorded SHA-256 set to the LF bytes
(nothing reads that hash; the text is the same).

After pass 1 of the review the kits of `catalog-2c.2` state 67 statements, 5
of them new (the window of 30 days stated, 0 and 2 decimals with the count
of zero shown, the latest end of any exposure record, an efficacy set by
WEIGHT): two more calls, both accepted on the first attempt, with the owner's
approval of the spend (relayed by the base session, 2026-11-22):

```text
$ specfirst gen natural requests --kits <kits> --out .../catalog-2c-rewrite-2.request.json
.../catalog-2c-rewrite-2.request.json: 5 paragraphs, 0 filler
$ specfirst gen natural propose ... --call catalog-2c-rewrite-2 --tokens 53220 --tool-uses 2 --seconds 7
143a25f85d7f62f4 tfl.percent.format: attempt 1: slots ok
38ada0f9a172ae32 pop.efficacy.rule: attempt 1: slots ok
cb149eac0baa5239 trt.end.source: attempt 1: slots ok
d1314e75c2820be3 tfl.percent.format: attempt 1: slots ok
df27755fc9e15ca1 ae.teae.end: attempt 1: slots ok
$ specfirst gen natural readback ... --call catalog-2c-readback-2 --tokens 54421 --tool-uses 2 --seconds 5
143a25f85d7f62f4 tfl.percent.format: attempt 1: read back as one_decimal_always: ACCEPTED
38ada0f9a172ae32 pop.efficacy.rule: attempt 1: read back as baseline_and_postbaseline: ACCEPTED
cb149eac0baa5239 trt.end.source: attempt 1: read back as last_ex_record_end: ACCEPTED
d1314e75c2820be3 tfl.percent.format: attempt 1: read back as one_decimal_always: ACCEPTED
df27755fc9e15ca1 ae.teae.end: attempt 1: read back as last_dose_plus_days: ACCEPTED
store .../src/specfirst/gen/rewrites: 87 statements, 87 accepted (0 by the phrasing template), 0 open; 10 of 10 filler paragraphs accepted; 7 calls, 416566 tokens
the kits state 67 statements; without an accepted text: 0
```

The store grew by 5 more lines of paragraphs.jsonl and 2 of calls.jsonl; no
line changed. The texts of the first two calls stay in the store (it is
append-only), whether or not a kit of `catalog-2c.2` states them.

### The scorer (read)

- `scorer.Case.features`: the features of the study's design, for a default
  by design; `candidate.vector(..., features)`; a kit's case gives its
  design's features.
- HAND01: `FEATURES` (randomized); it states `ae.related.values` and a total
  column over all arms (the house has none, and the planted defect S5 needs a
  total column to leave out); `ae.teae.end` is the house default now (30
  days). The AE table gains AEBODSYS. `EXPECTED` is worked out again by hand:
  six rows, four columns, a count of zero with its percentage; the safety set
  of the randomized subjects who were dosed leaves X1 out of the twin.
  Mutation finds ten decisions it cannot show (`pop.safety.grouping` is the
  tenth: every subject of the set is dosed as planned).
- The checks of read-1a on HAND01 (`score/gate.py`): the control plants the
  list of related causality values ("PROBABLE" in place of "POSSIBLE",
  "PROBABLE"), since the plan states no window any more; arm S leaves six
  cells of the two rows of related events waiting and the seven cells of the
  total column to `tfl.columns.total` (with `ae.related.values` for the two
  rows that wait); at stage T `tfl.columns.total` owns those seven alone.
- The pilot report and the separation on the pilot take `PILOT_FEATURES`.
- The pilot report's summary (G1 of the review, pass 2): each state is
  counted apart in the rows both tables have and in the rows the build lacks
  (the three explained cells of the dose modifications lie in a row arm S
  does not build), and a row the catalog lacks is told from a row the table
  decisions do not ask for. `Pilot.not_built` lists the rows of the key's list
  that it does not build either (FATAL_RELATED, which reads RELGR1 too).
  tests/score/test_score_pilot.py holds the sentence for the three arms.

### The reader (read)

- The skills render the house defaults of the default pair (`harness.knowledge`;
  a default by design names its cases); TASK.md and `skills/core-reader`
  describe the anchors by entry ID, the cases and the fixed rules.
- The kept dry run of arm R is `R-task-6e527ae6baab` (below), in place of
  `R-task-04119188ff71`.

### The gates of the part (after the first run on clean clones)

Five checks of three gates failed on `681697b` and are fixed in `982e7cb`:

- gen-3a, slots and bad rewrite: their plants took the paragraph of the age
  groups of open-default@1 ("below 65, 65 to 80, and above 80"); under
  open-default@2 the groups are "below 65, and 65 and above". They now take a
  stated paragraph of the first kit of the tier full: two of its tokens
  exchanged (the slot check reports the order), one of its numbers raised by 5
  (the slot check and the read-back reject it, and so does the loop).
- read-1a, kits of gen-2a: the planted defect S7 (every percent rounded to a
  whole number before the grid rounds it) failed on the two kits that state 0
  decimals: there it changes nothing. It does not apply to a table of whole
  percentages now, as S5 does not apply to a table without a total column.
- read-1a, pilot tests: the numbers of the pilot report under open-default@2
  (below). The crosswalk of the example's rows maps "Related Serious TEAE"
  (An07_04) to SERIOUS_RELATED, a row of the standard rows of catalog@2 (#13).
  On `982e7cb` the related fatal events and the dose modifications stayed
  without a row; pass 1 of the review (F2, F3) changed that in `b183940`:
  the crosswalk maps all eight analyses of the example to their rows of
  catalog@2 (An07_06 FATAL_RELATED, An07_07 DOSE_MODIFIED), the trace tries
  the key's list of rows as a stated value of `tfl.ae.summary.rows`, a row is
  `no_row` only when the catalog has none (a gap of the catalog), and the
  reader without the output holds a joint explanation again.
- read-2a, skills: the planted skills are checked on a copy of the catalog and
  the skills; from catalog@2 the reading notes render the house's defaults,
  so the copy holds the house and standard/versions.yaml too.

### Gates on clean clones

Each gate on a fresh clone with a fresh install and fetch, one at a time
under the heavy lock, on at most four processors, on `9d4b48f`, the last
commit of the part before the merge:

```text
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 bash scripts/clean_clone_gate.sh <wp> /mnt/d/trial_work/specfirst/.git 9d4b48f
```

| Gate | Commit | Unit tests | Result | Log |
| --- | --- | --- | --- | --- |
| catalog-2b | 9d4b48f | 1341 passed, 30 deselected | GATE catalog-2b: PASS (17 checks) | docs/reports/catalog-2c.catalog-2b.gate.log |
| std-1 | 9d4b48f | 1341 passed, 30 deselected | GATE std-1: PASS (12 checks; the pair `catalog@1`, `open-default@1` by label) | docs/reports/catalog-2c.std-1.gate.log |
| gen-1a | 9d4b48f | 1341 passed, 30 deselected | GATE gen-1a: PASS (8 checks) | docs/reports/catalog-2c.gen-1a.gate.log |
| gen-2a | 9d4b48f | 1341 passed, 30 deselected | GATE gen-2a: PASS (13 checks) | docs/reports/catalog-2c.gen-2a.gate.log |
| gen-3a | 9d4b48f | 1341 passed, 30 deselected | GATE gen-3a: PASS (15 checks; "read-back": the store 87 statements, 87 accepted, 7 model calls) | docs/reports/catalog-2c.gen-3a.gate.log |
| read-1a | 9d4b48f | 1341 passed, 30 deselected | GATE read-1a: PASS (14 checks) | docs/reports/catalog-2c.read-1a.gate.log |
| read-2a | 9d4b48f | 1341 passed, 30 deselected | GATE read-2a: PASS (19 checks; "arm R, kept dry run": `R-task-6e527ae6baab` checks, the same task on every bound part) | docs/reports/catalog-2c.read-2a.gate.log |

The commits before `9d4b48f` are gated through it. The first runs, on
`681697b` (catalog-2b, std-1, gen-1a and gen-2a passed; gen-3a, read-1a and
read-2a failed in the five checks above), are not kept: their logs are
replaced by those of `9d4b48f`. SEP01's invariants are held by
tests/unit/test_separation.py, which every gate's unit tests run (the window
reproduces from 35 to 38 days, `date.studyday.origin` is inert,
`ae.start.imputation` is separated at dataset level only, and each planted
defect fails).

The gate gen-2a against the same gate before the part (catalog-2b, on
`catalog@1`) and on `681697b`: the separation tables of the three logs side
by side, the rows that differ (in: kits that hold the decision; read: kits
whose output reads it; appl: kits where a probe claims a difference;
sep: kits whose twin separates it):

```text
decision                2b (937ae95)      681697b           9d4b48f
                        in read appl sep  in read appl sep  in read appl sep
trt.planned.source      10  9  9  9       10  8  8  8       10  7  7  7
trt.actual.source       10  2  2  2       10  2  2  2       10  3  3  3
trt.start.source        10 10  8 10       10 10  5 10       10 10  7 10
trt.end.source          10  3  2  2       10  6  3  3       10  7  5  5
trt.date.imputation     10 10  8 10       10 10  5 10       10 10  7 10
pop.randomized.rule     10  3  3  3       10  4  4  4       10  3  3  3
pop.safety.rule         10  7  1  1       10  6  2  2       10  7  3  3
pop.safety.grouping     10  5  3  3       10  4  4  4       10  5  5  5
disp.status.record      10  3  3  3       10  1  1  1       10  1  1  1
ae.start.imputation     10 10  8 10       10 10  5 10       10 10  7 10
ae.teae.start           10 10  8 10       10 10  5 10       10 10  7 10
ae.teae.end             10 10  8 10       10 10  5  9       10 10  7 10
ae.related.values       10  8  0  6       10 10  0  8       10  9  0  7
tfl.rounding.rule       10 10  1  8       10 10  2  4       10 10  3  3
vectors drawn again     0                 19                0
-- PASS kits            208.4 s           480.6 s           242.3 s
```

- In all three every applicable decision is separated on the twin of its kit
  ("separation: 0 holes in the matrix of 10 kits"). Eight of the 22 rows are
  the same in all three, `date.studyday.origin` among them (read by no
  output and unseparated; PLAN.md section 4.7).
- Vectors drawn again: a vector whose kit is unfit (a probe that claims a
  difference the twin does not make) is drawn again from the same stream.
  On `681697b` REACHES claimed differences that no planted record makes
  under catalog@2 (F1), and the ten kits needed 19 vectors more; on
  `9d4b48f` every kit takes its first vector, as on catalog@1. The time of
  the kits step follows (each vector drawn again writes its kit again).
- The rows move because the vectors move: the sampler of catalog@2 draws
  other values (an alternative first, then its slot values; F4), so the
  kits read other decisions.
- `tfl.rounding.rule`: claimed at one decimal only (F1). Kits 1, 3 and 10
  show one decimal (six kits show two, one kit none), and these three are
  the kits where it is applicable and separated. On catalog@1, without the
  decimals slot, every kit showed one decimal: separated in 8 kits, claimed
  by a probe in 1.
- `ae.related.values` has one alternative; its slot values are separated in
  7 kits, a probe claims none.

### main merged in (`1e24e3c`)

main moved from `6cdeded` to `e123599` while 2c was open: track/real merged
issue #29 (ADR-021, a standalone recomputation script per analysis of a
built kit). The merge of lesson 72 builds the merge commit on the tip and
needs main to be an ancestor of it, so main was merged into track/std first,
as track/real merged catalog-2b before issue #29 (`711c032`):

```text
$ git merge --no-ff main
Auto-merging CLAUDE.md
CONFLICT (content): Merge conflict in CLAUDE.md
Auto-merging src/specfirst/gates.py
Automatic merge failed; fix conflicts and then commit the result.
```

- CLAUDE.md: two adjacent lines, each changed by one side. Both changes are
  kept: the kit line ends with main's `specfirst recompute <kit> [--export
  DIR]`, the gen line keeps 2c's `[--vector house] [--check FILE]`.
- src/specfirst/gates.py merged without a conflict: 2c changes std-1's
  commands (the pair by label), main adds the gate issue-29; the two are
  separate parts of the file.
- The two sides are independent otherwise: specfirst.recompute imports
  specfirst.kit, specfirst.machine, specfirst.paths, the package's version
  and itself; 2c changes
  nothing under machine/, kit/, recompute/, standard/ or env/. The gates of
  track/real are run on the merge all the same (below).

Every gate that 2c or issue #29 touches, on a clean clone of `1e24e3c`, one
at a time under the heavy lock, on at most four processors (the command as
above, with `1e24e3c`). The unit tests are 1357 passed and 36 deselected,
where `9d4b48f` had 1341 and 30: the tests issue #29 adds.

| Gate | Unit tests | Result | Log |
| --- | --- | --- | --- |
| issue-29 | 1357 passed, 36 deselected | GATE issue-29: PASS (12 checks) | docs/reports/catalog-2c.merged.issue-29.gate.log |
| catalog-2b | 1357 passed, 36 deselected | GATE catalog-2b: PASS (17 checks) | docs/reports/catalog-2c.merged.catalog-2b.gate.log |
| std-1 | 1357 passed, 36 deselected | GATE std-1: PASS (12 checks) | docs/reports/catalog-2c.merged.std-1.gate.log |
| gen-1a | 1357 passed, 36 deselected | GATE gen-1a: PASS (8 checks) | docs/reports/catalog-2c.merged.gen-1a.gate.log |
| gen-2a | 1357 passed, 36 deselected | GATE gen-2a: PASS (13 checks) | docs/reports/catalog-2c.merged.gen-2a.gate.log |
| gen-3a | 1357 passed, 36 deselected | GATE gen-3a: PASS (15 checks; the store 87 statements, 87 accepted, 7 model calls) | docs/reports/catalog-2c.merged.gen-3a.gate.log |
| read-1a | 1357 passed, 36 deselected | GATE read-1a: PASS (14 checks; the pilot report's summary as before G1) | docs/reports/catalog-2c.merged.read-1a.gate.log |
| read-2a | 1357 passed, 36 deselected | GATE read-2a: PASS (19 checks; "arm R, kept dry run": `R-task-6e527ae6baab` checks) | docs/reports/catalog-2c.merged.read-2a.gate.log |
| real-2 | 1357 passed, 36 deselected | GATE real-2: PASS (15 checks) | docs/reports/catalog-2c.merged.real-2.gate.log |
| real-3a | 1357 passed, 36 deselected | GATE real-3a: PASS (16 checks) | docs/reports/catalog-2c.merged.real-3a.gate.log |
| real-5a | 1357 passed, 36 deselected | GATE real-5a: PASS (18 checks) | docs/reports/catalog-2c.merged.real-5a.gate.log |
| real-5b | 1357 passed, 36 deselected | GATE real-5b: PASS (19 checks) | docs/reports/catalog-2c.merged.real-5b.gate.log |

The separation matrix of gen-2a on `1e24e3c` is that of `9d4b48f`, row for
row (the 22 decisions; in, read, applicable, separated), with 0 vectors
drawn again and 0 holes, as it should be: the merge changes nothing the
generator reads. The kits step
took 189.2 s (242.3 s on `9d4b48f`).

Two gates are not run. real-1: its checks are those of real-2 (the same
commands; real-2 runs tests/pilot in full, real-1 its evidence tests).
base-0: its checks besides the evidence tests are in every gate above, and
the evidence tests (tests/evidence, tests/evidence_cases.py) import
specfirst.paths alone; neither 2c nor issue #29 changes them or it.

G1 of the review, pass 2 (the pilot report's summary, under "The scorer"
above) is `03f12fe`, after the merge. It changes src/specfirst/score/pilot.py
and tests/score/test_score_pilot.py. What reads pilot.py: the check "pilot
tests" of read-1a (tests/score), the harness's pilot task
(harness/pilot.py), the command `specfirst score pilot`, and two unit tests
(tests/unit/test_harness_pilot.py, test_score_pilot_pins.py);
specfirst.gen.separate imports its `PILOT_FEATURES`, which G1 leaves alone.
So read-1a is run again on a clean clone of `03f12fe`, and no other gate:

| Gate | Commit | Unit tests | Result | Log |
| --- | --- | --- | --- | --- |
| read-1a | 03f12fe | 1357 passed, 36 deselected | GATE read-1a: PASS (14 checks) | docs/reports/catalog-2c.g1.read-1a.gate.log |

The pilot report of arm S in that log (its lines 398 and 401), where
`1e24e3c` printed "3 differ and are explained ... 9 are in rows that arm S
does not build" and "rows not built: RELATED, SERIOUS_RELATED":

```text
  cells of the key that differ or are missing: 12. Of the 15 cells of the rows both tables have, 0 differ and are explained by another value of one table decision, and 0 are unexplained. 12 are in rows that arm S does not build: 3 explained by another value of one table decision, 9 for a variable the reference ADaM lacks, 0 in rows the catalog does not have, 0 in rows the table decisions do not ask for that no one table decision gives; the open cells and those without a row are classed by the crosswalk of rows, not by a build
    ADAE.RELGR1: the house standard writes it by ae.related.values; rows not built: RELATED, SERIOUS_RELATED, FATAL_RELATED
```

The commit of documents after `03f12fe` changes nothing but docs/: this
report, the review, the gate logs, docs/state/std.md and docs/state/gen.md.

## Every number held against a hand calculation

The tests hold numbers that a change of 2c moves. Each was worked out from the
written-out data of its study first, then held against the build; where the
two differed the cause was found, never the number copied.

- HAND01 (`score/hand.py`): the gold table, 28 cells (`EXPECTED`). Visible:
  safety set P1, P2 / L1, L2 / H1, H2 (L3 never dosed); twin: P1 to P3 / L1, L2
  / H1, H2 (X1 dosed without being randomized is outside the safety set of
  open-default@2). L1's rash on the 30th day after the last dose is inside the
  window of 30 days, P2's on the 31st is not. Serious related: L1's nausea
  (visible), L2's dizziness (twin). The test of the table passes cell for cell.
- HAND01's planted defects (tests/unit/test_score_hand.py, `EXPECTED`): S2-set
  12 and 11 cells (the randomized set adds L3 to the low dose and to the
  total; FATAL and DISCONTINUATION keep their zeros in the low dose), S2-set-rule
  0 and 9 (X1 joins the high dose), S5-column 7 and 7, S7-rounded 6 and 6 (the
  six percents of the visible total column that are no whole number; on the
  twin 33.3 of placebo and five of the total column). S1, S3, S4, S9, S10 keep
  their numbers.
- HAND01's attribution scenarios: a window without an end and a count of zero
  without its percent own 2 + 12 cells of the twin and 8 of the visible
  table; the safety rule and the table's set both wrong own 5 cells of the low
  dose (the set alone) and 6 of the total column jointly (back on the safety
  set the rule brings X1 in, on the randomized set L3 is in); arm S leaves the
  6 treatment-column cells of the two related rows waiting and the 7 cells of
  the total column to `tfl.columns.total`; at stage T it owns those 7 alone.
- HAND01's separation: ten decisions unseparated; `trt.end.source` by the latest
  start date changes 4 visible cells (H2's cardiac arrest on 02-20 falls out of
  the window from the start of its only record, 01-15).
- SEP01 (`gen/sep01.py`): six rows, three columns; every count as before (P1
  and P2's events in placebo, L1 and L3 in the low dose, H1 and H2 in the high
  dose), the serious related row holds L1's nausea alone. Its classes from
  `specfirst gen separate sep01`: the one change is `tfl.columns.total`,
  separated (every total column changes a table that has none); the three
  invariants of #30 hold (the window reproduces from 35 to 38 days;
  `date.studyday.origin` is inert; `ae.start.imputation` is separated at
  dataset level only), and the four plants fail as before.
- The reference on its five subjects (tests/unit/test_gen_reference.py): the
  cases of open-default@1 kept with the decimals slot, and new cases: the
  defaults of open-default@2 (N1 out of the safety set; L1's serious event on
  day 41 out of the window), emergence by time collected (P1's event without
  a time is emergent; at 07:30, before the dose at 08:00, it is not), the
  latest end of any exposure record (H1's record of dose zero to 2024-04-30),
  the randomized subject by the disposition record, the new rows, and 0 and 2
  decimals ("1 (33)", "1 ( 33.33)").
- The pilot report (tests/score/test_score_pilot.py; 27 cells, nine rows by
  three arms): arm S has the key's text in the 15 cells of the rows both
  tables have (the house now shows a count of zero with its percent and has
  no total column, as the example); 9 cells are open (the related, serious
  related and related fatal rows read RELGR1, which only `ae.related.values`
  writes) and the 3 cells of the dose modifications, a row the standard rows
  leave out, are explained by the key's list of rows. Arm R with the readings
  of open-default@1 (zero blank, a total column): 10 cells right, 5 counts of
  zero explained by `tfl.percent.format`, 9 open, 3 without a row (the dose
  modifications need the key's rows and the percent format, two decisions)
  and the column axis by `tfl.columns.total`. A reader without the output
  (with zero blank): 10 cells explained by `tfl.output.include` alone, 5 by
  it with `tfl.percent.format`, 9 open, 3 without a row.

## The kept dry run of arm R

Kit 4 of the gate seed, written as the gate writes it
(`harness.gate._kit`, from the worktree): `sfrrl2uh`, train, the ask demo,
nine natural paragraphs, all from the model. The task and run folders lie on
a Windows drive outside every checkout, and the run starts from the worktree
(whose parent folder is denied whole).

Two runs were made, one per approval. The first, `R-task-b6706bdac1d8`,
committed in `681697b` (generator `catalog-2c.1`; 25 turns, 108.7 s, USD
0.8003, PASS, 21 of 22 values and 21 of 21 cells as below), was bound to
kit 4 of `catalog-2c.1`. Pass 1 of the review changed that kit (F1), so the
gate would have failed it; it is deleted. The second, from the worktree at
`f5de3fb` with the five new texts in the store:

```text
$ specfirst run arm <kit-004> --arm R --seed gen-2a/kit-4 --keep
run R-task-6e527ae6baab: arm R, stage C, condition notes, kit sfrrl2uh (train), task task-6e527ae6baab (22 decisions)
  reader: claude-code, model claude-opus-5-5, used ['claude-opus-5-5'], CLI 2.1.327
  cost: 23 turns, 94.9 s wall, 88.6 s API, tokens in 20 out 7868 cache write 63137 cache read 336614, USD 0.7299 (CLI: 0.7298587999999999)
  budget: {'turns': 100, 'seconds': 2700, 'usd': 10.0}: within
  outputs: decisions.jsonl 22 lines, questions.jsonl 2 lines, unmapped.jsonl 0 lines
  asks: 2, answered 2; pop.efficacy.rule (mod-populations); ae.related.values (mod-ae-emergence)
  output files: valid
  task folder: holds only what a reader may see
  canary scan: 30581 canaries from 92 files; clean
  permission denials: 1
  RUN R-task-6e527ae6baab: PASS
kept in <checkout>/src/specfirst/harness/kept/R-task-6e527ae6baab
```

The old kept run `R-task-04119188ff71` is deleted as well. The kept files
are ASCII, hold `<home>` and `<checkout>` for the local folders and no
account name. The deny list of the run names the folders of the machine as
the old run's did: the folder of the checkouts (`D:/trial_work`), the kit's
folder under WSL, the CLI's executable under `<home>`, and the run and task
folders, which lay in the scratchpad of the author's Claude Code session
under `<home>` (its path holds a session ID, no account name; one of them is
the task folder of the first run, `task-b6706bdac1d8`, which was still
there). Checked again as the gate does, with its scores (report only; they
decide nothing):

```text
$ specfirst run check src/specfirst/harness/kept/R-task-6e527ae6baab --kit <kit-004> --tasks <scratch> --seed gen-2a/kit-4 --score
kept run R-task-6e527ae6baab: PASS
...
  asks: 2 given, 2 in gold (decisions with the status asked), 2 of them right; precision 1.00, recall 1.00
  decisions a reviewer would have to change: 1
    disp.status.record (mod-populations), house_default: gold {"rule": "disposition_event"}; the candidate (given) has {"rule": "disposition_event_by_subcategory", "subcategory": "STUDY PARTICIPATION"
...
  visible: cells correct: 21 of 21 gold cells (an output that was not produced counts as wrong)
  twin: cells correct: 21 of 21 gold cells (an output that was not produced counts as wrong)
wrong by value, and these data cannot show it (alone, on gold, it changes no cell and no axis of any dataset): disp.status.record (mod-populations)
```

21 of 22 values right; the one wrong value cites a paragraph of the protocol
(4.3/p1) where gold takes the house default, and these data cannot show it.
The first run of 2c gave the same: the same value wrong, the same citation.
One or two runs of a model say nothing about a difference from the old run
(22 of 22).

## Model use

| Call | Role | Model | Items | Tokens | Tool uses | Time | Result |
| --- | --- | --- | --- | --- | --- | --- | --- |
| catalog-2c-rewrite-1 | rewriter, fresh context | Sonnet 5.5 subagent | 21 statements | 57,251 | 2 | 14 s | 21 of 21 slots ok |
| catalog-2c-readback-1 | verifier, a new fresh context | Sonnet 5.5 subagent | 21 paragraphs | 60,793 | 2 | 9 s | 21 of 21 accepted |
| R-task-b6706bdac1d8 (deleted) | reader, arm R | claude-opus-5-5, CLI 2.1.327 | 22 decisions | in 22, out 9,031, cache write 67,120, cache read 412,998 | 25 turns | 108.7 s | PASS; USD 0.8003 |
| catalog-2c-rewrite-2 | rewriter, fresh context | Sonnet 5.5 subagent | 5 statements | 53,220 | 2 | 7 s | 5 of 5 slots ok |
| catalog-2c-readback-2 | verifier, a new fresh context | Sonnet 5.5 subagent | 5 paragraphs | 54,421 | 2 | 5 s | 5 of 5 accepted |
| R-task-6e527ae6baab (kept) | reader, arm R | claude-opus-5-5, CLI 2.1.327 | 22 decisions | in 20, out 7,868, cache write 63,137, cache read 336,614 | 23 turns | 94.9 s | PASS; USD 0.7299 |

The two runs of arm R report their cost (the CLI's USD): USD 1.5302 in
all. The four subagent calls report tokens only, 225,685 in all; their USD
is computed here from the list prices of Sonnet 5.5 (USD 2 per million input
tokens, 2.50 per million written to the five-minute cache, 0.10 per million
read from it, 10 per million output tokens) and the three requests of a call
with two tool uses; the exact bill of a subagent is not reported to the
session that starts it:

- the estimate, each call's context written to the cache once and read back
  twice: 225,685 x (2.50 + 2 x 0.10) / 1e6 = USD 0.61;
- without any cache, each request billing the call's whole context as
  input: 225,685 x 3 x 2 / 1e6 = USD 1.35 (the output, a few hundred tokens
  a call, adds under a cent a call).

| Approval | For | Limit | Spent (no cache) |
| --- | --- | --- | --- |
| 2026-11-21 | rewrite and read-back, at most 4 calls; one dry run | about USD 1.6 | 2 calls, USD 0.32 (0.71); dry run USD 0.80 |
| 2026-11-22 | at most 2 more text calls (about USD 0.7); one more dry run (about USD 0.8) | about USD 1.5 more, 3.0 in all | 2 calls, USD 0.29 (0.65); dry run USD 0.73 |
| 2c in all | | about USD 3.0 | USD 2.14 (2.88) |

The first dry run cost USD 0.2 above its share of the first approval (0.6);
the first approval's total held, and so does the whole: below USD 3.0 in
either case.

## Review

docs/reports/catalog-2c.review.md, a fresh-context reviewer (rule R7):

- Pass 1, of `681697b` and `982e7cb`: NOT SIGNED; F1 blocking (REACHES
  claimed two differences that no planted record makes under catalog@2), F2
  to F6 to fix, F7 to F11 notes. All are answered in `b183940`, `f5de3fb`
  and `9d4b48f` (above).
- Pass 2, of `b183940` to `9d4b48f` and the merge `1e24e3c`: SIGNED of
  `1e24e3c`, on the condition that the twelve gates of the merge pass on
  clean clones (they do, "main merged in" above). G1 to fix: fixed in
  `03f12fe`, read-1a run again on it. G2 to G6, notes of the generator, are
  in docs/state/gen.md, "Left open by the review of catalog-2c"; G7 is said
  under "Gates on clean clones" (`tfl.rounding.rule`); G8: docs/state/std.md
  is committed with this report, after the gates.
- Pass 2, condition: the twelve gates of the merge met (the reviewer read
  each log, and the table above agrees with them), G1 settled (the diff of
  `03f12fe`, the sentences the tests hold, and read-1a on a clean clone of
  it). Verdict: SIGNED (pass 2, condition met) of `1e24e3c`, with G1 settled
  in `03f12fe`.
