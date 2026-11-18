# gen-2a Gold and verification, slice "adverse event summary first": independent review

Rule R7 of PLAN.md. Reviewer: an agent with a fresh context that did not
write the work. Date: 2026-11-17. Correctness only, no style.

Reviewed: branch `track/gen` at `ce70734`, in the worktree of the track;
base `843c890`, five commits. The code is that of `3c503de`, the commit on
which the gate ran: `git diff --stat 3c503de..ce70734` names six files, all
of them documents. While I worked the author was still writing. The
sections "The pilot kit" and "GitHub and CI" of `docs/reports/gen-2a.md`
and three lines of `docs/state/gen.md` were not committed, and
`docs/reports/gen-2a.real-3a.gate.log` was a new file. I read these texts
as they stood in the worktree at the end of the review.

Result of pass 1, on `ce70734`: NOT SIGNED. One finding blocks (G1).
Seven do not (G2 to G8). The machine, the hand calculation and the checks
of P1, P2 and P3 held under everything I tried. What blocks is what the
gate asks of P4.

Result of pass 2, on `d20cab2`: SIGNED. The owner approved the reading
that G1 is about, for the slice only, and the rework is booked before the
gate of the full gen-2. G2 to G8 are settled. One new finding, G9, does
not block. Pass 2 is the last section of this file. Everything before it
is pass 1 as it was written on `ce70734`; two places of it were touched
for pass 2, the paragraph above and the name of the verdict line of pass
1.

## How the review was done

- In the worktree, with Windows git for the diff and the history. Nothing
  was searched or listed outside the worktree, my scratch folder and the
  scratch folders under `/root` of the WSL machine; the folder
  `reference/` beside the checkout was not touched.
- Everything that runs, under WSL (Ubuntu 24.04, root) in the environment
  of the worktree, each command inside `flock
  /run/lock/specfirst-heavy.lock`, one process at a time. No run of CDISC
  CORE, no rerun of the gate, nothing installed, the fetch cache not
  written.
- The ten kits of the gate seed that the author kept
  (`/root/scratch-gen2a/gate2/first/kit-001` to `kit-010`) were read and
  never written. A build on their data was made in a scratch folder
  (`gold.Workbench` copies the SDTM files and the house standard there).
  Kits of my own were written to `/root/scratch-review-gen2a/`.
- No file of the repository was changed but this one. Nothing was
  committed. My scripts are in my scratch folder and are not kept; each is
  described where its output is quoted.

## What I read

- `CLAUDE.md`; `PLAN.md` sections 2, 4.6 to 4.8, 6.4 to 6.8, 8, 9 and
  13.5; `docs/decisions/ADR-005.md` and `ADR-007.md`;
  `docs/reports/gen-2a.md`, `gen-2a.gate.log` (all 394 lines),
  `gen-2a.gen-1a.gate.log` and `gen-2a.real-3a.gate.log` (their summary
  lines and the lines the report quotes); `docs/state/gen.md`;
  `docs/lessons.md`, lessons 34 to 46; `docs/reports/gen-1a.review.md`
  from finding F13 of pass 1 to the end: the verdict of pass 1 and all of
  pass 2.
- The diff `843c890..ce70734`, 43 files. In full: `gen/decisions.py`,
  `gold.py`, `display.py`, `reference.py`, `verify.py`, `kits.py`,
  `gate2.py`, the changes in `gen/probes.py`, `gen/gate.py`, `gen/sdtm.py`,
  `gen/command.py`, `gen/core_findings.yaml`, `gates.py`, `doctor.py`,
  `machine/methods.py`, `machine/lineage.py`, `standard/methods/`,
  `tests/methods/`; the tests `test_gen_reference.py`, `test_gen_gold.py`,
  `test_gen_kits.py`; of the other test files the names of the new tests,
  and in full the test of `reaches` and the test of the broken lock
  script.
- The 22 catalog entries of the slice, `standard/catalog/entries/*.yaml`,
  each against `gen/reference.py`.
- The files of the ten kept kits: decisions, matrices, grids, the log of
  probes, one manifest, one compiled set of specs.

## What I ran

Outputs are cut to the lines that matter. Where several lines say the
same, I put them into one line, or a line in brackets says so; the
numbers and the texts of the cells are as printed.

A. The unit tests of the new and changed test files, and the method
vectors.

```text
$ flock /run/lock/specfirst-heavy.lock python -m pytest -p no:cacheprovider -q
    tests/unit/test_gen_reference.py tests/unit/test_gen_gold.py
    tests/unit/test_gen_decisions.py tests/unit/test_gen_kits.py
    tests/unit/test_gen_gate.py tests/unit/test_gen_probes.py
    tests/unit/test_gen_subjects.py tests/unit/test_doctor.py
    tests/unit/test_registry.py tests/methods
178 passed in 247.91s (0:04:07)
```

B. A count by hand on the twin of gate kit 9 (`handcount.py`, about 110
lines of my own that import nothing of specfirst). It reads the Dataset-JSON files
of the twin, follows the words of the catalog entries for the 22 decision
values of the kit (the efficacy-evaluable set by SYSBP, planned treatment
by a decoded arm code, treatment start from DM.RFXSTDTC, partial event
starts not completed, a window of 14 days, half to even, a total over the
active arms) and prints the table beside the grid of the kit.

```text
header                    grid ['(N=44)', '(N=37)', '(N=31)', '(N=81)']
                          mine ['(N=44)', '(N=37)', '(N=31)', '(N=81)']  equal
Any adverse event         grid ['32 ( 72.7)', '28 ( 75.7)', '26 ( 83.9)', '60 ( 74.1)']
                          mine ['32 ( 72.7)', '28 ( 75.7)', '26 ( 83.9)', '60 ( 74.1)']  equal
Related adverse event     grid ['16 ( 36.4)', '21 ( 56.8)', '10 ( 32.3)', '37 ( 45.7)']
                          mine ['16 ( 36.4)', '21 ( 56.8)', '10 ( 32.3)', '37 ( 45.7)']  equal
... (three more rows, equal)
my count equals the grid of the kit in every cell: True
subjects in DM: 137 randomized: 121 safety: 119 efficacy: 112
```

C. The machine against the hand calculation on decision vectors that the
gate does not build (`random_vectors.py`). The gate builds the gold vector
of a kit and vectors that differ from it in one decision. Here every
decision of a vector is drawn at random, with slot values the sampler of
gen-2a never draws (a window of 0, 1, N - 1, N + 1, N + 2 or 60 days, any
list of rows, any list of causality values, a control that names no
column, the treatment record as the end-of-study record). Each vector is
compiled and built by the machine on the twin of a gate kit and its grid
is held against `reference.table` with `verify.p2`.

```text
$ flock ... python random_vectors.py <kit> 150
kit 1 twin: 150 random vectors: {'built': 150, 'equal': 150, 'differ': 0, 'not built': 0, 'not calculated': 0, 'sampler would refuse': 113}; runs of yamaa: 150
kit 2 twin: 150 random vectors: {'built': 150, 'equal': 150, 'differ': 0, 'not built': 0, 'not calculated': 0, 'sampler would refuse': 110}; runs of yamaa: 150
kit 4 twin: 150 random vectors: {'built': 150, 'equal': 150, 'differ': 0, 'not built': 0, 'not calculated': 0, 'sampler would refuse': 117}; runs of yamaa: 150
kit 5 twin: 150 random vectors: {'built': 150, 'equal': 150, 'differ': 0, 'not built': 0, 'not calculated': 0, 'sampler would refuse': 107}; runs of yamaa: 150
kit 9 twin: 150 random vectors: {'built': 150, 'equal': 150, 'differ': 0, 'not built': 0, 'not calculated': 0, 'sampler would refuse': 109}; runs of yamaa: 149
kit 10 twin: 150 random vectors: {'built': 150, 'equal': 150, 'differ': 0, 'not built': 0, 'not calculated': 0, 'sampler would refuse': 105}; runs of yamaa: 150
```

A first run of 40 vectors on kit 1, with another seed of my script, gave
the same: 40 built, 40 equal. In all 940 vectors on six twins (designs
with two, three and four arms, with and without an efficacy-evaluable
set), 940 grids equal to the hand calculation; 661 of the 900 are vectors
that the sampler of gen-2a refuses.

D. Planted defects of my own against P2 (`planted.py`). Each case plants
one defect in what the machine does, in memory, builds the twin of a gate
kit and asks whether `verify.p2` against the hand calculation of the gold
decisions reports it.

```text
kit 3, no defect planted: P2 reports 0 differences       (also kits 7, 9, 10)
case 1 (window + 1 day), kit 3, decision 14 days, machine 15: P2 reports 1 differences, for example: row 'Any adverse event', column 'TNB-373 50 mg once daily': the grid '18 ( 69.2)', the reference '17 ( 65.4)'
case 2 (window - 1 day), kit 3, decision 14 days, machine 13: P2 reports 1 differences
case 1 and case 2 on kits 7 (30 days) and 9 (14 days): P2 reports 2 differences each
case 3 (ASTDT > TRTSDT), kit 9: P2 reports 2 differences, for example: row 'Any adverse event', column 'Low Dose': the grid '30 ( 68.2)', the reference '32 ( 72.7)'
case 3 (ASTDT > TRTSDT), kit 10: P2 reports 2 differences
case 4 (rounding ignored), kit 10, decision half_even: P2 reports 2 differences, for example: row 'Any adverse event', column 'Placebo': the grid '39 ( 81.3)', the reference '39 ( 81.2)'
case 4 (rounding ignored), kit 9, decision half_even: P2 reports 0 differences: THE DEFECT IS NOT SEEN
case 5 (columns reversed), kit 9: P2 reports 1 differences, for example: columns: the grid ['Placebo', 'High Dose', 'Low Dose', 'Total'], the reference ['Low Dose', 'High Dose', 'Placebo', 'Total']
case 6 (zero rule turned round), kit 9: P2 reports 5 differences; kit 10: P2 reports 3 differences
case 7 (AE of SF4TVBDP-103-033 missing in Parquet: 1 rows), kit 10: P2 reports 2 differences
case 8 (safety set by randomized_and_dosed, decision at_least_one_dose), kit 10, table on safety grouped actual/dm_actarm: P2 reports 8 differences
case 8 (safety set by at_least_one_dose, decision randomized_and_dosed), kit 7, table on safety grouped planned/dm_actarm: P2 reports 0 differences: THE DEFECT IS NOT SEEN
case 8 (safety set by at_least_one_dose, decision randomized_and_dosed), kit 9, table on efficacy grouped actual/dm_actarm: P2 reports 0 differences: THE DEFECT IS NOT SEEN
```

Case 3 is a rule that no alternative of the catalog states (strictly after
the first dose date, written into the compiled ADAE spec): only a
reference can see it, and it does. The three cases that are not seen are
the three places where the matrix of the kit says `unseparated`: they are
what `unseparated` means for a check of results (G1).

E. Kits written by the code of the worktree (`gen_own.py`).

```text
== 1: gate kit 9 again
  122 files, the manifest included; differ from the kept kit of the gate: 0 []; built in 28 s
== 2: kits of seeds of my own
 seed review-g2a-a/kit-4: written in 28 s
  kit sfwvfjwq (train), scenario 4 {'tfl.population': 'efficacy'}, 4 arms; vectors drawn before: 0
  decisions 22, read 16, applicable 8, separated 14, applicable and unseparated []
    read and unseparated: pop.safety.rule = {"rule": "at_least_one_dose"} (default); the same table under ['randomized_and_dosed']
    read and unseparated: tfl.rounding.rule = {"rule": "half_away_from_zero"} (default); the same table under ['half_even']
 seed review-g2a-b/kit-9: kit sfbnc6fq (test), scenario 9, 3 arms; applicable 8, separated 14
    read and unseparated: trt.end.source = {"rule": "last_ex_end_date"} (default); the same table under ['ds_date_when_ex_missing']
    read and unseparated: pop.safety.rule = {"rule": "randomized_and_dosed"} (stated); the same table under ['at_least_one_dose']
 seed review-g2a-c/kit-4: kit sf8fq62t (train), scenario 4, 3 arms; applicable 8, separated 13
    read and unseparated: pop.safety.rule = {"rule": "at_least_one_dose"} (default); the same table under ['randomized_and_dosed']
    read and unseparated: tfl.rounding.rule = {"rule": "half_even"} (stated); the same table under ['half_away_from_zero']
 seed review-g2a-d/kit-9: kit sfk8vjuz (test), scenario 9, 3 arms; applicable 8, separated 14
    read and unseparated: trt.date.imputation = {"rule": "first_day_of_month"} (stated); the same table under ['not_completed']
    read and unseparated: pop.safety.rule = {"rule": "randomized_and_dosed"} (stated); the same table under ['at_least_one_dose']
    read and unseparated: tfl.rounding.rule = {"rule": "half_even"} (stated); the same table under ['half_away_from_zero']
 seed review-g2a-e/kit-2: kit sfpryn52 (train), scenario 2, 3 arms; applicable 8, separated 15
    read and unseparated: trt.end.source = {"rule": "last_ex_end_date"} (default); the same table under ['ds_date_when_ex_missing']
 (every kit: all cells of the visible data and of the twin equal the reference; engines agree: True; R: 4.6.2; kits.check without mutation: 0 problems)
== 3: a matrix changed by hand
  before: tfl.rounding.rule is unseparated
  kits.check without mutation: 0 problems []
  kits.check with mutation (15 s): 3 problems
    gold/identifiability.json is not the matrix a new mutation gives
    kit.yaml: the identifiability summary is not that of a new mutation
    decision tfl.rounding.rule: 'identifiable' is not what the matrix says
```

Part 1 is P1 by another route: the kept kit was written at 16:10 as a
first build of the author's run of the gate checks; mine at 16:30 in the
process of my script, with no hash seed set, in another folder. In part 3 the
copy of the kit had the unseparated decision marked `separated` in the
matrix, in the decision record and in the summary of `kit.yaml`, and the
hashes written again.

F. The commands, as a user runs them (`cli.sh`).

```text
$ specfirst gen verify /root/scratch-review-gen2a/own/review-g2a-d-9
kit sfk8vjuz (test): 121 files have the hashes of kit.yaml; 29 decision records fit the schema, 17 stated in gold/docs/sap.md and read back by the parser
  visible: P2 18 of 18 cells equal the hand calculation; P3 grid Out_AESUM: 18 cells, 18 print a number; 18 of the 18 cells with results have a complete path to SDTM columns; engines: 33 results in both, 0 disagree; largest relative difference 0.0e+00 (allowed 1e-09)
  twin: P2 18 of 18 cells equal the hand calculation; ... 0 disagree ...
  twin: P4 52 builds of 22 decisions: 14 separated, 8 applicable, 0 applicable and unseparated; not read: date.studyday.origin, disp.status.record, pop.randomized.rule, pop.safety.grouping, trt.actual.source; read without a probe: pop.safety.rule, tfl.rounding.rule, trt.date.imputation
kit: ok
$ specfirst gen kit --seed review-g2a-cli --number 7 --split dev --out /root/scratch-review-gen2a/cli-kit
kit sff4jkgm (dev): 121 files in /root/scratch-review-gen2a/cli-kit; P1: two builds have the same bytes; P2 to P4 hold; 14 of 22 decisions separated on the twin
$ specfirst gen verify /root/scratch-review-gen2a/cli-kit --no-mutation
... visible: P2 24 of 24 cells equal the hand calculation ... twin: P2 24 of 24 ...
kit: ok
$ grep -rl review-g2a-cli /root/scratch-review-gen2a/cli-kit | wc -l
0
```

In the kit of the seed `review-g2a-d/kit-9` the subject of the probe
`partial_exposure_date` is in the safety set and not in the
efficacy-evaluable set (`own_kit9.py`): that is why the stated decision
`trt.date.imputation` changes no cell of its table. The kit of the seed
`review-g2a-cli` has scenario 7, which gives it a window and the
disposition date as the treatment end date; its table was drawn on the
randomized set with a post-baseline value. Its matrix (`facts.py`): 8
applicable; read and unseparated: `trt.end.source`, `disp.status.record`
and `tfl.rounding.rule`. All six kits of my seeds were written from the
first decision vector.

G. The claims of `probes.REACHES` on vectors the gate kits do not have
(`scan2.py`, `scan.py`; by the hand calculation alone, which C holds
against the machine). `scan2.py`: on the twin of each gate kit, the gold
vector and every vector that differs from it in one decision (every
alternative, every slot value the sampler knows); for each such vector and
each decision, every pair of its value with another alternative.

```text
366 vectors on 10 twins
  pairs claimed and separated: 6068
  pairs claimed and not separated: 4
  pairs not claimed and separated: 1009
  pairs not claimed and not separated: 2897
claims that do not hold: 4
   kit 5, vector disp.status.record=disposition_event_by_subcategory(subcategory=STUDY PARTICIPATION) (the sampler refuses it): disp.status.record: disposition_event_by_subcategory | disposition_event
   kit 7, the same vector; kit 8, the same vector
   kit 10, vector ae.teae.end=end_of_study (the sampler refuses it): disp.status.record: disposition_event_by_subcategory | disposition_event
pairs not claimed and not separated, by decision, in vectors the sampler can draw (interplays with another decision included):
   date.studyday.origin     345
   tfl.rounding.rule        86
   trt.date.imputation      1
   ... (eight more decisions; most of their pairs are interplays)
```

345 of the 366 vectors can be drawn by the sampler
(`date.studyday.origin` has one pair in each, never claimed and never
separated). `scan.py`: 85 vectors that the sampler can draw, the table of
each gate twin put on the efficacy-evaluable set (every rule and slot
value), on the randomized set (both rules) and on the safety set; pairs
that are not claimed and not separated, after leaving out the pairs that
another decision of the vector keeps the output from reading:

```text
     44     NOT claimed, NOT separated: tfl.rounding.rule
     19     NOT claimed, NOT separated: trt.end.source
      9     NOT claimed, NOT separated: disp.status.record
      2     NOT claimed, NOT separated: trt.date.imputation
{'vectors': 85, 'unclaimed_unseparated': 74, 'claimed_unseparated': 0}
```

H. Could data separate what kit 9 leaves unseparated, under the decisions
of kit 9? (`could_separate.py`; the rows of the twin changed in memory, the
tables by the hand calculation.)

```text
a, the twin as it is: tfl.rounding.rule: half_even | half_away_from_zero: 0 cells differ; header ['(N=44)', '(N=37)', '(N=31)', '(N=81)']
a, the twin as it is: trt.end.source: last_ex_end_date | ds_date_when_ex_missing: 0 cells differ
b: 31 placebo subjects in the set; 15 taken out, none planted
b, 16 in the placebo arm: tfl.rounding.rule: half_even | half_away_from_zero: 2 cells differ; header ['(N=44)', '(N=37)', '(N=16)', '(N=81)']
     row 'Any adverse event', column 'Placebo': half_even '13 ( 81.2)', half_away_from_zero '13 ( 81.3)'
c: subject SFYF9EKD-105-023: planned High Dose, start 2022-06-11, in the safety set True, in the efficacy-evaluable set False; its SYSBP records: [('2022-06-03', 132), ('2022-06-11', 128)]
c, the planted subject in the set: trt.end.source: last_ex_end_date | ds_date_when_ex_missing: 4 cells differ; header ['(N=44)', '(N=38)', '(N=31)', '(N=82)']
```

I. Planted defects of my own against `gate2.splits_check`
(`splits_planted.py`): a copy of gate kit 1 as a set of one kit.

```text
0 unchanged: the check returns True
1 the seed in gold/docs/sap.md: the check returns False
     kit 1: gold/docs/sap.md holds the seed
2 split dev in the manifest of kit 1: the check returns False
     kit 1: split dev, the plan gives train
3 another seed_sha256: the check returns False
     kit 1: seed_sha256 is not the hash of its seed
```

J. Small things: `git diff --name-only 843c890..HEAD -- PLAN.md
standard/schemas standard/catalog third_party env` prints nothing;
`CLAUDE.md` has 59 lines; the two ARD files of kit 9
(`reporting-event.jsonl` and `.r.jsonl`) differ in bytes and agree in
values; the manifests of the first and the second build of kit 9 were
written 0.08 seconds apart (16:10:36.51 and 16:10:36.42).

## What I could not review

- The gate run itself. Its clean clone under `/tmp` is gone; I read the
  log. I did not run the gate again. The kits I looked at are those the
  author built from the seed of the gate with the same code and kept; I
  built kit 9 again and it is the same bytes.
- The gate of gen-1a with CORE on `3c503de` and the gate of real-3a on
  `3c503de`: their logs only.
- The compiler and the templates of std-1, yamaa, the two result engines,
  the R code, `graph.check_graph` and `graph.check_cells` of the machine:
  used, not reviewed. For the R engine I saw its results, not its run.
- The run of CI on GitHub that the report quotes, and the push.
- Separation on the visible data: the work computes none, and neither
  did I.
- Whether a failed kit leaves a folder behind: read in the code only (G7).

## Findings

### G1. BLOCKS: "applicable" is what the generator claims, so the gate passes kits in which a decision that the output reads, and that data could separate, is not separated on the twin

The gate text (PLAN.md section 13.5, limited by ADR-005 to the one
output): "10 kits pass P1 to P4. Every applicable decision is separated on
the twin." P4 (section 4.6): "Changing any decision to another listed
alternative changes at least one result." Section 6.5: "The twin carries
the full set of probes. Every applicable decision must be separated on the
twin."

What the gate checks (`verify.mutate`, `kits.generate`,
`gate2.separation_check`; ADR-007, decision 6). A decision is applicable
in a kit when `probes.reaches` holds for every pair of its gold value with
another alternative. `probes.REACHES` is a table in the code of the
generator, which the log of probes of every kit repeats. It is a condition
on the decision vector; the data of the kit do not enter. A kit in which
a pair with this condition gives the same table is never written. So the
sentence "every applicable decision is separated" is true of every kit
that exists, by construction; check 9 of the gate can fail on it only when
a claim of the table is false. What the table does not claim, the gate
asks of no kit. The one other demand is on the set: every pair must be
separated in some kit of the ten.

The conditions of the table are of two kinds, and the definition does not
tell them apart.

- (a) Another decision of the kit keeps the output from reading the
  difference: the table groups by planned treatment and the subject who
  was dosed without being randomized has no planned treatment; actual
  treatment is the same as planned; there is no emergence window, so no
  cell reads the treatment end date. No data could separate the decision
  under the other decisions of the kit. Not counting these is what
  sections 4.7 and 9.3 provide for.
- (b) The probe of the twin does not work under the decisions of the kit,
  and other data would. The condition of `tfl.rounding.rule` is "the
  counts of one arm are set for these decisions" (the safety set, actual
  treatment, DM.ACTARM). The condition `_ANALYZED` takes eight decisions
  (`trt.start.source`, `trt.end.source`, `trt.date.imputation`,
  `disp.status.record`, `ae.start.imputation`, `ae.teae.start`,
  `ae.teae.end`, `ae.related.values`) out of every kit whose table is on
  the efficacy-evaluable set or on a randomized set that asks for a
  post-baseline value, because some planted subjects are not in those
  sets. Lesson 43 says how these conditions came in: the first mutations
  showed five claims that did not hold, and "The conditions are corrected
  in `specfirst.gen.probes.REACHES`." In
  gen-1a a probe that changed no result was a blocking finding (F2 of its
  review) and the recipes were changed. Here the claim was made smaller.

Evidence.

1. The gate log. In kits 4 and 9, 8 of 22 decisions are applicable: six
   table decisions, the efficacy rule and the source of planned treatment.
   The log lists eleven cases "unseparated, read, no probe claimed" in the
   ten kits. Eight are of kind (a): `pop.safety.rule` in six kits,
   `pop.safety.grouping` in two. Three are of kind (b):
   `tfl.rounding.rule` in kits 4 and 9, and `trt.end.source` in kit 9.
   Kit 9 is a test kit; its document states "rounded half to even", and
   under the house default, half away from zero, every cell of its twin
   has the same text.
2. Experiment H. Under the decisions of kit 9 data can separate both:
   with 16 subjects of the placebo arm in the set the two rounding rules
   give other texts in two cells; with the planted subject in the set the
   two sources of the treatment end date give other counts in four cells.
3. Experiment D. A machine that ignores the stated rounding rule passes
   P2 on the twin of kit 9 (case 4). What is unseparated is not checked by
   any result, by P2 no more than by a scorer.
4. Experiments E and F. Each of my six kits has at least one decision of
   kind (b) that is read and unseparated; in each, 8 decisions are
   applicable. The test kit of the seed `review-g2a-d/kit-9` states two
   decisions that its twin cannot tell from the house default: partial
   exposure dates completed to the first day of the month, and rounding
   half to even. `specfirst gen verify` says "0 applicable and
   unseparated" and "kit: ok". In the kit of scenario 7 the decision that
   the scenario exists for, the treatment end date from the disposition
   date, is read and unseparated.
5. Experiment G. On 85 vectors that the sampler can draw, the rounding
   rule is neither claimed nor separated in 44, the pair of
   `trt.end.source` with the disposition date in 19, `disp.status.record`
   in 9, `trt.date.imputation` in 2. In the set of the gate the rounding
   rule is applicable in one kit of ten, kit 10; in the other nine the
   gate does not ask for it. In my runs every decision of
   `mod-ae-emergence` that the output read was separated; the gate would
   not have failed on a kit in which one was not.

So the gate passes on work in which, in two of its own ten kits, a
decision of the slice that the table reads is not separated on the twin
although data could separate it. That is not "every applicable decision is
separated on the twin" in the words of the plan. It is that sentence with
"applicable" read as "claimed by the generator".

Nothing of this is hidden. The verdict of the report, its limits, ADR-007
and the handover say that the gate reads "applicable" this way and name
the classes; the log lists every case per kit, and
`gold/identifiability.json` tells a scorer the truth per kit. The finding
is not about what the report says. It is about what the gate proves, and
about who decides the reading:

- ADR-007 lists this reading as the last of five points that are "for
  the owner, because they touch what other tracks own or go beyond the
  words of the plan"; this point touches no other track. The status of
  the ADR is "decided in gen-2a, 2026-11-17, by the executor", and "The
  decisions stand unless the owner objects." The text of the gate is not
  changed, but what it asks is, and that is the owner's: PLAN.md changes
  "only through an ADR in docs/decisions/ that the owner approves"
  (CLAUDE.md), and section 2.3 asks to stop and ask when "a gate cannot
  pass without changing the gate". The review of gen-1a said of probes
  that change no result: "gen-2a would meet them as failures of its own
  gate."
- The cause is named in ADR-007 and in the report: the data of a kit are a
  function of the design and the seed, and the decisions are sampled to
  fit them. Section 6.4 has the decisions first (S1) and the probes after
  them (S3). The report says of the remedy: "possible (stage S3 after S1)
  and was not done".

My signature would make the gate pass with a reading of its text that is
the owner's to accept. I do not sign it. What settles the finding is at
the end.

### G2. Does not block: P3 is checked without "no spec element is unused", and P2 holds the table only

Section 4.6 asks for P3: "No spec element is unused", orphans 0 but for
those tagged `conformance_only`. `verify.p3` reports how many ADaM columns
are on the way of a cell and fails on none that is not. The report says so
in the section "The four properties": with one output most of ADSL is read
by no cell. That follows from ADR-005 (one output, "limited by a list of
units"), and it is owed by the full gen-2. P2 compares the grid with the
hand calculation; no ADaM value and no ARD value that no cell shows is
held against anything (ASTDY under `date.studyday.origin` is the
example). Both belong under "Limits" and in the paragraph of the verdict
that says what the gate does not prove; today the first stands only in
the body, and the second is said as what P2 is, not as a limit.

### G3. Does not block: the hand calculation shares a little more with the machine than "nothing", and three of its readings are not marked

`reference.py` imports nothing of the machine, and I found no reading in
it that follows the engine against the words of an entry. Two limits of
the claim "shares nothing":

- The order of the columns. `verify.p2` and `kits._reference_file` give
  the reference the arms that `gold.arms_of` makes, with the texts that
  can name each arm, and `reference.column_order` (lines 389 to 407) is
  the rule of `gold.order_values` (lines 122 to 141) written a second
  time: "a label that names several arms stands where the first of them
  stands; a label that names none comes last". A name missing in
  `arms_of` would put the column last in both. P2 sees a machine that
  orders otherwise (D, case 5) and both alternatives are separated in all
  ten kits, but for this one rule the reference is a copy with a shared
  input. The report names the order "from the design" as a limit; it
  should name the shared names.
- The row labels and the label "Total" are constants copied from the
  house layout template. The docstring of the module lists what it takes
  from elsewhere and leaves these out.

Readings that the words leave open and that are not marked `READING`:

- An event without an analysis start date that ended before the treatment
  start: two notes of `ae.teae.start` apply; the reference lets the end
  decide (lines 289 to 293).
- "An event that ends before the treatment start date": a partial end
  date is no end (`full_date`, line 289).
- A subject of the analysis set without a treatment stands in no column,
  the total included (line 425). The words of `tfl.columns.total` ("pools
  all treatment arms") carry it. It is the reason why `pop.safety.rule`
  cannot be separated on a table by planned treatment, so it should be
  said. The same holds for an arm without a subject in the set, which has
  no column.

For the third the machine does the same: the mutated builds of
`pop.safety.rule` equal the reference. The first two are not exercised
at all: the ten twins hold 2,012 events, none with a partial end date,
and none with a partial start date that ended before the first dose
(`partial.py`). So neither P2 nor my runs say what the machine does
there. As the report says, a wrong reading that both share does not
show; a reading that the data never meet does not show either.

### G4. Does not block: some checks have no planted defect in the repository (rule R5)

The report says "each new check fails on a planted defect first". That
holds for P1, P2, P3, the mutation, the matrix of the set, the engines and
the held-out combination. It does not hold for:

- "no file of a kit holds its seed", the split by the place of a kit, and
  `seed_sha256` (`gate2.splits_check`). The comment at line 532 says
  "Planted: a seed in a file", and no seed is planted there or in a unit
  test.
- "`identifiability.json` is the matrix a new mutation gives"
  (`kits.check`), on which check 9 rests, since it reads the matrix from
  the kit.

I planted all four (I, and part 3 of E). Each is seen. The planted
defects should be in the gate or in the unit tests, so that the next
change of these checks is held by them and not by a review.

### G5. Does not block: the sampler never draws some values, and the limits do not say so

`decisions.slot_values` and `decisions.fits`: a stated list of rows is one
of four lists, each with ANY and FATAL and none with DISCONTINUATION; a
window is always the follow-up length of the design. The report states
the like for `disp.status.record`, and not these. Two consequences: the
conditions of `REACHES` on the rows are true in every kit that is ever
written, and a reader is never scored on "the rows are any event and
serious events" or on a window of another length. The machine and the
hand calculation agree on such vectors (C: about three quarters of the
random vectors are vectors the sampler refuses). The limits should name
them.

### G6. Does not block: the two builds of P1 run at the same moment

`gate2.write_all` starts the first and the second build of a kit as
neighbouring jobs of a pool of four. The manifests of the two builds of
kit 9 were written 0.08 seconds apart. The two processes differ in hash
seed, time zone (the local date differs between them for most of a day),
locale (C.UTF-8 against C), working folder and output folder. They do not
differ in the clock: a time read from UTC at a resolution of a second
could be the same in both. The planted defect "a time that depends on its
process" is a dependence on the hash seed, not a clock. I found no call
of a clock in `src/specfirst` and none in `r/`, and kit 9 built twenty
minutes later is the same bytes (E). The same twenty builds in another
order, the second builds after the first ones, would make the clock
differ as well.

### G7. Does not block: records

- The report, "What was built": "942 unit tests in all". The gate log and
  the CI section of the same report say 943 (908 + 28 + 7).
- `docs/state/gen.md` lists gen-2a under "Passed". By section 2.3 a gate
  has passed when the script exits 0 and the reviewer signs; with this
  verdict the line is not true yet.
- The sections "The pilot kit" and "GitHub and CI" of the report were
  written while I reviewed and are not committed. The first agrees with
  `gen-2a.real-3a.gate.log` line by line (commit `3c503de`, 16 of 16
  checks PASS). The second I cannot check.
- `kits.generate` raises on a kit that fails a property and leaves the
  folder with what was written so far, without a manifest; only a failure
  of P1 removes it (`generate_checked`). "A kit that fails a property is
  not written" means: it gets no `kit.yaml`. Read in the code, not run.

### G8. Does not block: one claim of `REACHES` is false on vectors that the sampler refuses

`REACHES["disp.status.record"]` claims its pair whenever the end-of-study
date is read. With the study participation record as the gold value the
two alternatives pick the same record: 4 claims of 6,072 in G, all on
vectors that `decisions.fits` refuses. The truth about this decision is
in two places, the table and `fits`. A kit with such a vector would be
drawn again, not passed, so the error is on the safe side. On every
vector that the sampler can draw, every claim I evaluated held.

## Checked and found correct

- Scope and rules. `PLAN.md`, `standard/schemas/` and `standard/catalog/`
  are not in the diff; nor is `third_party/` or `env/`. The 43 files are
  code, tests, method vectors and documents; no data file, no study data
  of a third party, nothing that looks like material of an employer. The
  identifiers in the logs are generated (`SFYF9EKD`, `KRD-542`). The
  changes outside the folder of the track are the ones the report names.
  `CLAUDE.md` has 59 lines. HEAD adds only documents to the commit of the
  gate.
- The gate table. 13 checks, the environment first. The three clauses of
  the text are checks 8, 9 and 10. Check 8 writes every kit twice in
  processes of their own and decides P2, P3, the engines and the matrix
  again from the files (`kits.check`); a matrix changed by hand is seen
  (E). A check that finds no kits fails.
- The report against the log. 1,216 files, 422 cells, 509 mutated
  builds, 766 results, 17 lines "planted defect", 13 of 13 checks, 0
  vectors drawn again; the table of the section "Separation" is lines 312
  to 336 of the log; 394, 188 and 468 lines; 3,192 lines in the seven new
  modules, 464 in the reference; 28 tests in four new files and 7 more.
  The limits name every case of kind (a) and (b) that the ten kits have.
- P1. Two processes with what G6 lists; every file by SHA-256, the
  manifest included; the planted manifest differs in `kit.yaml` alone.
  Kit 9 built by me is the kept kit, byte for byte.
- P2. The hand calculation follows the words of the 22 entries as I read
  them: the treatment dates and which partial dates take part, the three
  analysis sets, the grouping, the two notes of `ae.teae.start` and the
  two definitions of `ae.teae.end`, the rows, the zero rule, rounding on
  exact fractions. The machine computes a percentage as `100.0 *
  numerator / denominator`, one division of whole numbers, so a half is
  exact where the fraction has one. My own count equals kit 9 in 24 of
  24 cells (B). On 940 random vectors the machine and the hand calculation
  give the same table, 940 times (C). My planted defects are seen
  wherever the kit separates the decision (D).
- P3. The four planted defects of the gate are real cases, the lost
  `reads` edge of lesson 45 among them. A decision that is not read and
  changes the output is a defect in `mutate`, so the static `read` is
  held against the builds in one direction.
- P4, the mechanics. Every alternative of every decision is compiled and
  built on the twin; a state is `separated` when the gold value differs
  from every other alternative; each mutated build is held against the
  reference. The claims that `REACHES` makes are true on every vector the
  sampler can draw that I evaluated (G), and the ten gate kits and my six
  needed no second vector.
- The engines. Both ARD files are in every kit and are compared again by
  check 10; they are two files (J); my kits report R 4.6.2 and agreement.
- The splits. My three planted defects are seen (I); the seed of my kit
  is in none of its files (F).
- `not_before`. The unit test of the report exists and passes (A), and
  the reference reads the statement as yamaa does.
- The pilot kit. `display.pattern` keeps its default; the pilot tests and
  the method vectors are in the gate; the gate of real-3a passed on
  `3c503de` by its log.

## The findings F21 to F28 of the gen-1a review

| Finding | State |
| --- | --- |
| F21 a cancellation in `pop.efficacy.rule` | stated as open: not removed from the data; the pair is claimed, and a kit in which it cancels is drawn again |
| F22 `reaches` promises less than it reads | settled: a condition on the vector with the rows, the exact window and the two interplays (`probes.holds`, `test_reaches_is_evaluated_on_a_decision_vector`); it also became narrower than the interplays (G1) |
| F23 two values of a slot give the same table | stated as a limit in the report and the handover |
| F24 what CORE did not check; TAETORD without an arm | settled: TAETORD is empty for a subject without a planned arm (`sdtm._se`, with a test); the subjects of the 38 rules are in the report of gen-1a |
| F25 the claim about controlled terms | nothing was owed |
| F26 the reason of `probe-dosed-but-not-randomized` | settled in `core_findings.yaml`; the question stays with the std track |
| F27 two checks compare less than their text | settled: `repeated_key` compares the subjects (test with a finding of the right size about other subjects); `term_problems` takes the codelist of DSDECOD by DSCAT, checks COUNTRY and the codelists of the study, which come from the design and not from the data; three planted values in the gate log of gen-1a |
| F28 small things | settled: `GENERATOR` is `gen-2a.1`; a record after the end of the participation has the epoch FOLLOW-UP, after a first attempt that the gate of gen-1a refused (lesson 40); `specfirst doctor` reads `env/lock.sh`, with the script as it was once committed as a planted defect; the message of the clean clone script |

The gate of gen-1a passed again on `3c503de`, CORE included, by
`docs/reports/gen-2a.gen-1a.gate.log`: 8 of 8 checks, 943 tests, no
unexplained finding in 20 datasets.

## What settles G1

One of two, and it is not mine to choose.

1. The owner approves the reading of ADR-007, decision 6, as the reading
   of the gate text for the slice. Then nothing more is owed for G1 but
   the points of G2 in the limits, and I would sign the same code.
2. Or the gate asks what the words ask. "Applicable" keeps the conditions
   of kind (a) and loses those of kind (b): a decision that the output
   reads is applicable unless another decision of the kit makes its
   alternatives equal on any data. The probes then have to follow the
   decisions of the kit: the calibrated counts for the analysis set and
   the grouping of its table, and the planted subjects inside its
   analysis set. The gate fails on a kit in which a read decision of kind
   (b) is unseparated.

G4 and the wrong number of G7 can be settled in the same pass. After
that I read the diff, the new log and the report again.

Verdict of pass 1: NOT SIGNED

## Pass 2

Commit reviewed: `d20cab2` on `track/gen`; `main` is `843c890`. Since
pass 1 (`ce70734`) there are three commits: `f2dac3b`, the review of pass
1 and the changes for G2 to G8; `f5381da`, the logs of the two gates on
`f2dac3b`, in the report; `d20cab2`, the owner's answer on G1, records
only. The file of pass 1 is in `f2dac3b` with the 653 lines I wrote, and
the two later commits did not touch it. `git diff --stat f2dac3b d20cab2
-- src tests standard scripts env r kits` prints nothing: the code of
`d20cab2` is the code on which both gates ran. Since `ce70734` no file
changed under `src/specfirst/machine`, `src/specfirst/compile`, `r/`,
`standard/`, `env/` or `scripts/`, and `PLAN.md` did not change.

I was told the owner's answer by the session of gen-2a, which had it from
the base session. I did not take it from either; what I checked is under
G1.

### How pass 2 was done

As pass 1: in the worktree, with Windows git; everything that runs, under
WSL in the environment of the worktree, each command inside the shared
lock, one at a time, and where kits of a set are built, four processes at
a time. No run of CORE, no run of a gate, nothing installed, the fetch
cache not written. The kits the author kept were read only; mine are
under `/root/scratch-review-gen2a/`. No file of the repository was
changed but this one; nothing was committed.

One thing is new. To check the owner's answer I searched the transcripts
of the owner's other sessions with the session tool of the desktop app:
six searches for words of the question and of its options. A search
returns a few words around a hit. I opened no transcript.

### What I read

- The diff `ce70734..d20cab2`, 15 files. Every changed line of
  `gen/gate2.py`, `gen/kits.py`, `gen/probes.py`, `gen/reference.py`,
  `gen/__init__.py`, the two test files, ADR-007, `docs/lessons.md`
  (lesson 47) and `docs/state/gen.md`. Of the report, as it stands now:
  "Verdict", "The gate", "The pilot kit", "What was built", "The four
  properties", "Separation", "Limits", "Review", "GitHub and CI", "For
  the owner".
- The two gate logs of `f2dac3b`, each as a diff against the log of
  `ce70734`, and their summary lines.

### What I ran

Outputs are cut as in pass 1.

K. The logs in the repository against the logs the gate runs left.

```text
$ sha256sum docs/reports/gen-2a.gate.log /root/scratch-gen2a/gate-gen-2a/clean-clone.log
77d3ea8651d632579364dba650858ba41035e873e87d8301a82b5acdae231e2c  (both)
$ sha256sum docs/reports/gen-2a.gen-1a.gate.log /root/scratch-gen2a/gate-gen-1a/clean-clone.log
472ff5177b0041e1d03cccaef09087c520bafc7ab7e085b90bb5182f659b8b24  (both)
$ grep -c "^planted defect" docs/reports/gen-2a.gate.log
21
$ grep "^GATE\|^commit" docs/reports/gen-2a.gate.log docs/reports/gen-2a.gen-1a.gate.log
commit:     f2dac3b07f6614c37de47233e0edfe135574fc65      (both)
GATE gen-2a: PASS
GATE gen-1a: PASS
```

The log of gen-2a differs from the one of `ce70734` in the commit, the
folder of the clone, the times, 945 tests for 943, 443 files for 438 in
the ASCII check and four new lines "planted defect". No line of a kit and
no line of the matrix differs. The log of gen-1a differs in the same
kinds of lines; none of its 30 lines "seed gen-1a-..." differs.

L. Is the change of `reference.py` comments only? (`p2_ast.py`: the syntax
trees of the two versions without their docstrings.)

```text
reference.py, ce70734 against d20cab2, without comments and docstrings: the same code: True (75188 characters of syntax tree)
```

M. The unit tests of pass 1 again (experiment A), with the two new tests.

```text
180 passed in 277.60s (0:04:37)
```

N. The changed code, run by me (`p2_build.py`): `gate2.write_all` for kit
9 of the gate seed; `kits.check` on what it wrote; the kit against the kit
of the old generator that the author kept; then three kits that cannot be
written.

```text
GENERATOR: gen-2a.2
== 1: write_all, kit 9, two builds
  failed: {}; 64 s
  first build: files written from 19:20:07 to 19:20:39; second build: from 19:20:40 to 19:21:10; the second starts 1.4 s after the first has ended
  122 files, the manifest included; differ between the two builds: 0 []
  kit sfyf9ekd (test), generator gen-2a.2
      twin: P4 50 builds of 22 decisions: 13 separated, 8 applicable, 0 applicable and unseparated; not read: date.studyday.origin, disp.status.record, pop.randomized.rule, pop.safety.grouping, trt.actual.source; read without a probe: pop.safety.rule, tfl.rounding.rule, trt.end.source
  kits.check with a new mutation: 0 problems []
  visible: the table of the new kit equals the table of the kept kit of gen-2a.1: True
  twin: the table of the new kit equals the table of the kept kit of gen-2a.1: True
  the matrix equals that of the kept kit: True
  files: 122 now, 122 before, the same names: True; with other bytes than before: 52
== 3: the log of probes of the new kit
  reaches of disp.status.record in the log equals probes.REACHES: True; it names the study record: True
== 2: a kit that cannot be written
  planted P2 difference on the twin: KitError: study SFAZE6C8, decision vector 0: 1 defects: twin: P2: a planted difference
  the folder exists afterwards: False
  planted error of another kind: ZeroDivisionError: a planted error that is no KitError
  the folder exists afterwards: False
  a folder that is not empty: KitError: eview-gen2a/pass2/not-empty is not empty
  the folder and its file are still there: True; files in it: ['mine.txt']
```

The 52 files with other bytes (`p2_changed.py`): the 22 Dataset-JSON
files, the 22 Parquet files and the two Define-XML files of the SDTM,
`gold/design.yaml`, `gold/probes.jsonl`, the two truth files, `study.json`
and `kit.yaml`. The Parquet files hold the same data. The text files are
the same once the name of the generator is put back, but for the log of
probes, where the table of `disp.status.record` differs on two lines, and
the two manifests, which hold hashes. The 70 other files, every ADaM
dataset, result, grid, page, graph file, reference, compiled spec, the
matrix and the decision records among them, are the same bytes as under
`gen-2a.1`.

O. The claims of the new table (`p2_scan2.py`: experiment G of pass 1,
with `probes.REACHES` of the code in place of the table in the logs of the
kept kits).

```text
366 vectors on 10 twins
  pairs claimed and separated: 6068
  pairs not claimed and separated: 1009
  pairs not claimed and not separated: 2901
claims that do not hold: 0
```

P. The machine against the hand calculation again (experiment C), on the
twin of the new kit 9 and on the twin of the kept kit 10.

```text
kit 9 twin: 100 random vectors: {'built': 100, 'equal': 100, 'differ': 0, 'not built': 0, 'not calculated': 0, 'sampler would refuse': 81}; runs of yamaa: 100
kit 10 twin: 100 random vectors: {'built': 100, 'equal': 100, 'differ': 0, 'not built': 0, 'not calculated': 0, 'sampler would refuse': 79}; runs of yamaa: 100
```

Q. The commands.

```text
$ specfirst gen kit --seed review-g2a-p2 --number 4 --out /root/scratch-review-gen2a/p2-cli-kit
kit sfvcqbcw (train): 121 files in /root/scratch-review-gen2a/p2-cli-kit; P1: two builds have the same bytes; P2 to P4 hold; 14 of 22 decisions separated on the twin
$ specfirst gen verify /root/scratch-review-gen2a/p2-cli-kit
  visible: P2 20 of 20 cells equal the hand calculation; ... 0 disagree ...
  twin: P2 20 of 20 cells equal the hand calculation; ... 0 disagree ...
  twin: P4 53 builds of 22 decisions: 14 separated, 8 applicable, 0 applicable and unseparated; ... read without a probe: pop.safety.rule
kit: ok
$ specfirst gen verify /root/scratch-review-gen2a/cli-kit --no-mutation       (a kit of pass 1, generator gen-2a.1)
kit.yaml: 'generator' is 'gen-2a.1', this checkout has 'gen-2a.2'
kit: FAILED
```

R. Two sets of ten kits of seeds of my own (`p2_set.py`): the ten
scenarios, each kit built once in a process of its own. Per kit, the
decisions that the output reads and that its twin does not separate. Kind
(a) and kind (b) are those of G1; `pop.safety.rule` and
`pop.safety.grouping` are the cases of kind (a).

```text
set 'review-g2a-set'
kit 7 (dev, scenario 7 ...): 21 decisions, read 17, applicable 15, separated 16
    read and unseparated, kind (a): none; kind (b): tfl.rounding.rule = half_away_from_zero (default)
kit 9 (test, scenario 9 ...): 22 decisions, read 17, applicable 8, separated 15
    read and unseparated, kind (a): pop.safety.rule; kind (b): trt.end.source = last_ex_end_date (default)
(the eight other kits: kind (b): none)
set 'review-g2a-set': kits with a decision of kind (b) read and unseparated: 2 of 10; such cases: 2, of them stated in the document of the kit: 0

set 'review-g2a-set2'
kit 1 (train, scenario 1 (all drawn)): ... kind (b): tfl.rounding.rule = half_away_from_zero (default)
kit 3 (train, scenario 3 ...): ... kind (b): tfl.rounding.rule = half_away_from_zero (default)
kit 5 (dev, scenario 5 ...): ... kind (b): tfl.rounding.rule = half_even (stated)
kit 9 (test, scenario 9 ...): ... kind (b): trt.end.source = last_ex_end_date (default), tfl.rounding.rule = half_away_from_zero (default)
(the six other kits: kind (b): none)
set 'review-g2a-set2': kits with a decision of kind (b) read and unseparated: 4 of 10; such cases: 5, of them stated in the document of the kit: 1
```

All twenty kits were written from the first decision vector.

S. The owner's answer in the transcripts. The question was put in
Chinese and this file is ASCII (rule R10), so I give the searches in my
own translation. Of six searches two had a hit, both in one session, the
base session, whose last activity was 2026-11-18 00:06 UTC, the evening
of 2026-11-17 on this machine.

- The label of the chosen option, "A approve the reading, merge today".
  The hit is the end of the question ("... holds that this reading needs
  your approval. Which do you choose?"), then an equals sign, then that
  label with "(Recommended)", then the sentence "You can now continue
  with these answers in mind." That is the form in which the question
  dialog hands an answer back to a session.
- The words "2 of the 10 kits" of the question. The hit is the first half
  of the question as it was relayed to me, word for word: the gate passes
  in full, the review did not sign, kits 4 and 9, one or two decisions
  each (the rounding rule, the source of the treatment end date), other
  data could have told them apart.
- Four searches for words of the description of option A (accept decision
  6 as the reading for this slice; the rework booked as a later part) had
  no hit. The search reaches what a session was told, and the description
  of an option stands in what a session asked.

### The findings of pass 1

G1, settled, by the owner. Way 1 of pass 1 was taken; no code changed for
it. What I checked:

- The answer. By S, the owner was asked the question that ADR-007 quotes
  and chose the option "approve the reading, merge today". I have this
  from the transcript of the session that asked, not from the two
  sessions that passed it on.
- The record. ADR-007 gives the question, the chosen option with its
  description and the option that was not chosen, in English. Held
  against the Chinese words as they were relayed to me, sentence by
  sentence, the translation is faithful. The description of the option I
  have as relayed only (S). Its sentences make the approval smaller, not
  larger: this slice only; decision values compared where a kit marks a
  decision unseparated; the rework before the gate of the full gen-2.
- What was drawn from it. The three points under "What follows" in
  ADR-007 say what the option says. The content of the rework is way 2 of
  pass 1 (the decisions first, the probes after them; `REACHES` keeps the
  conditions of kind (a); the gate fails on kind (b)). It is booked in
  `docs/state/gen.md` under "Next", with what it changes (the generator
  of gen-1a, its gate with CORE, `GENERATOR`), and in the report under
  "For the owner". The status of ADR-007 says that the approval is for
  the slice of ADR-005 only and that the other four points are open.
- The limit stays said. The verdict of the report names the three cases
  of the gate set that other data could separate; "Limits" has the
  reading and, with experiment D, what it means for P2; the handover
  tells a scorer that a table equal to the gold table is no evidence for
  a decision marked `unseparated`. Lesson 47 names what was done in the
  wrong order.

What pass 1 found about what the gate proves is unchanged, and the
records say so. What blocked was that the reading was not the executor's
to choose. The owner has chosen it.

G2, settled. "Limits" has both: P2 holds the table and nothing else, with
ASTDY as the example and the machine that ignores the rounding rule on
the twin of kit 9; P3 is checked without "no spec element is unused", and
the full gen-2 owes it.

G3, settled. The text of the module says what is shared: the arms and
their names from `gold.arms_of`, the column order as a rule written a
second time, the labels copied from the layout template. The three
readings are marked `READING`. Nothing but text changed (L). "Limits"
lists the five readings and the shared input. Three small things are
left, none worth a pass: the second bullet of the verdict of the report
still says "shares nothing with the machine" where the module now says
"shares no code"; "about 460 lines" is 483 now; and "Limits" does not say
that two of the readings meet no record in the data (0 of 2,012 events in
the ten twins), so that nothing shows what the machine does there.

G4, settled. `gate2.planted_splits` plants the seed in a document of a
copy of kit 1, another split and the hash of another seed, and asks that
each is reported alone. `gate2.planted_matrix` marks an unseparated
decision as separated in the matrix, the decision record and the
manifest of a copy, writes the hashes again, and asks that the check
without a mutation reports nothing and a new mutation exactly three
problems. Both are in the gate log (lines 291 and 347 to 349) and in the
unit tests (M). The gate plants 21 defects now.

G5, settled. "Limits" names the four lists of rows, the missing
DISCONTINUATION, the window and what follows for `REACHES` and for a
reader.

G6, settled. `gate2.write_all` runs every first build before any second
build. In my run the second build of kit 9 started 1.4 seconds after the
first had ended, and the two are the same bytes (N).

G7, settled. The report says 943, and 945 for the second run, which is
what the two logs say. A kit that cannot be written leaves no folder: a
planted difference and a planted error of another kind both left nothing,
and a folder that was not empty was refused and left as it was (N); the
repository has a test of its own. The line "Passed" of the handover
becomes true with this verdict. The sections "The pilot kit" and "GitHub
and CI" are committed.

G8, settled. `REACHES` of `disp.status.record` does not claim the pair
when the end-of-study record is the one of the study participation. With
the table of the code no claim fails on the 366 vectors of experiment G
(O: 0, where pass 1 had 4). The log of probes carries the table, so the
name of the generator changed, and both gates ran again on that code. A
kit of `gen-2a.1` is refused by `gen verify` (Q), as it should be. The
gold of kit 9 is byte for byte what it was under `gen-2a.1` (N).

### New in pass 2

G9. Does not block: "2 of the 10 kits" is the gate set, not a bound. The
question to the owner named the two kits of the gate set, which is right
for that set. The reading that was approved holds for every kit this
generator writes. In two sets of ten of my own seeds (R) the kits with a
decision of kind (b) read and unseparated are 2 and 4; the cases are the
rounding rule five times and `trt.end.source` twice, one of them stated
in the document of a dev kit. Pass 1 has kits in which it was
`trt.date.imputation` and `disp.status.record`, from scenarios I picked
to find them. Point 3 of ADR-007 covers all of this ("wherever
`gold/identifiability.json` of a kit says `unseparated`"), and so does
the handover. The verdict and the limits of the report speak of the ten
kits of the gate only; one sentence there should say that another set
has other kits and other counts, so that nobody plans a set of dev and
test kits on "2 of 10". Until the rework a set is best looked at with
its matrices before it is used.

Nothing else is new. The changed code does what the report says, and I
found no defect in it.

### What I could not check in pass 2

- The two gate runs on `f2dac3b`: their logs only. The logs in the
  repository are the files the runs left (K).
- The runs of CI on GitHub that the report quotes: I have no way to
  GitHub here. The remote-tracking branch `origin/track/gen` of the local
  repository is at `d20cab2`.
- The description of the chosen option, in the transcript (S).
- The gate of real-3a was not run again and the report says why. I agree:
  no file of the machine changed since `ce70734`.

### Verdict of pass 2

SIGNED. Both gates passed on clean clones of `f2dac3b`, and nothing but
records changed after it. The one blocking finding of pass 1 was a
question for the owner, and the owner answered it: the reading of
"applicable" in ADR-007, decision 6, is the reading of the gate text for
this slice, and the rework that makes the gate ask what its words ask is
owed before the gate of the full gen-2. G2 to G8 are settled in the code,
the gate and the records. G9 and the three small things under G3 are for
the next change of the report; they do not hold up the merge.

The signature is for the slice of ADR-005. It is not a signature under
the reading for the full gen-2, and it rests on the owner's answer as the
transcript of the base session has it.

Verdict: SIGNED
