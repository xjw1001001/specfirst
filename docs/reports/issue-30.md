# Issue #30 P4 on a real reference: one class per decision instead of a failure: report

Date: 2026-11-21. Branch: `track/gen`. Issue #30 of `xjw1001001/specfirst`:
"[P4] On a real reference many decisions do not separate: classify them
(unseparated with interval, inert, separated at data-set level only)
instead of failing". The route is ADR-019 (docs/decisions/ADR-019.md).

## Verdict

- P4's mutation, run on a reference study, gives every decision one class:
  `separated`, `unseparated` (with the values that reproduce and, for an
  integer slot of the gold value, the interval that reproduces),
  `inert`, or `separated_at_dataset_only` (with the outputs that read the
  decision named). The review lists the `unseparated` decisions first.
  Command: `specfirst gen separate sep01|cdiscpilot01`.
- The change stays within PLAN.md: P4 as stated stays the requirement for
  generated studies, whose matrix, gate and files do not change; on a
  reference, section 4.7 ("marked `unseparated` and reported") is the rule,
  and the classes say which kind of `unseparated`. No schema changes: the
  decision record keeps `identifiable` with its two values, `separated`
  only for the class `separated`. ADR-019 is therefore the executor's and
  needs no approval before it is carried out; three points are for the
  owner, none blocking.
- The acceptance of the issue, on the test study SEP01: a window that 4
  values reproduce (35 to 38 days; 34 and 39 separate), one inert rule
  (the origin of the study day: 26 ADaM cells change, no output reads
  them), one rule separated in ADaM and not in the table (the imputation of
  a partial start date). The classes and the interval are in the
  identifiability matrix of the study.
- Planted defects make the check of each class fail (rule R5): four, one
  per class, and a written matrix with two entries changed.
- cdiscpilot01, report only: 22 decisions of the slice under the house
  standard: 9 `unseparated`, 7 `separated`, 6 `inert`, no
  `separated_at_dataset_only`. With a window of 30 days: every window from
  13 to 36 days gives the same table (12 and 37 do not; 13 changes 7 ADaM
  cells and no cell), and `trt.end.source` is `separated_at_dataset_only`.
- The scoring rule, as far as it is the machine's: every decision of
  another class than `separated` is `unseparated` in its record, which the
  scorer compares by value and reports apart. What the scorer itself must
  do is a note for the read track (docs/state/gen.md, "For the read
  track"); no code of the read track is changed.
- Unit tests, ruff and the ASCII check pass; the gates gen-2a and gen-3a
  pass on clean clones of `8154075`, and gen-2a again on `5356478` with the
  test the review asked for (section "Gates"). The independent review
  signs (six findings, none blocking; section "The review"). Issue #30 is
  finished as far as track gen goes; see "What is left".

## Where P4 was computed and read before this work

- Generated kits: `specfirst.gen.verify.mutate`, in the gate gen-2a and in
  `specfirst gen verify`. Every alternative of every decision is built on
  the twin and the grids are compared pair by pair; a pair the log of
  probes claims and that gives the same grid makes the kit unfit. The
  matrix is `gold/identifiability.json`: per decision `read`,
  `applicable`, `identifiable` (`separated`, `unseparated`,
  `no_alternative`), a reason ("the output does not read what the decision
  sets", or "no probe that the log of probes claims"), and the pairs. The
  decision records repeat `identifiable`.
- cdiscpilot01: no mutation at all. The pilot has no decision vector of
  `catalog@1` (std-2, "Pilot decisions, mutation and identifiability", has
  not started). Its 18 decision records (kits/cdiscpilot01/gold/decisions/
  efficacy.jsonl, real-5a and real-5b) are custom: they have no listed
  alternative, and `specfirst.machine.decisions` holds them against the
  reporting events, not against data.
- The scorer (read track): `score.kit` reads the matrix of a generated kit
  (its pairs, and the summary lists `unseparated_read` and
  `unseparated_not_read`); `score.reading` scores the value of an
  `unseparated` decision like any other, and `score.report` lists it apart
  ("unseparated in gold, compared by value only"). `score.scorer.separation`
  mutates the hand-made study HAND01 and counts wrong cells (lesson 51);
  `score.pilot` explains a cell of the pilot's table by another value of a
  table decision (stage T). None looks at ADaM or the ARD for separation,
  and none scans a numeric slot.
- The identifiability matrix of the std track: owed by std-2 on the pilot;
  `compiler.bind_tables` proves the binds of a decision by mutation of the
  compile, not of the data.

## Does this stay within PLAN.md?

Yes (ADR-019, "Does this stay within PLAN.md?").

- P4 as stated (section 4.6) stays the requirement for generated studies:
  nothing in `specfirst.gen.verify`, `kits`, `gate2` or the generator
  changed, and `GENERATOR` is `gen-3a.2` as before.
- On a reference, section 4.7 applies: "Where data cannot separate two
  alternatives, the decision is marked `unseparated` and reported. It is
  not counted as proven." The classes are kinds of `unseparated`, kept in
  the identifiability matrix of the reference; section 8 names that file
  and gives it no form, and `standard/schemas/` has no schema of it.
- The decision record is unchanged: `identifiable` is `separated` or
  `unseparated` (decision-record.schema.json), `separated` only for the
  class `separated`.

So no ADR needed the owner before the work was done. The three points of
ADR-019 "For the owner" are questions for later, none blocking.

## The classes

From `specfirst.machine.separation`. Each other value of a decision is
built with every other decision at gold, and gets the highest layer at
which its build differs from gold's:

| Level | The other value |
| --- | --- |
| `fails` | cannot be built on these data, or compiled with the other decisions |
| `outputs` | changes a printed cell, a label of a row or a column, a title or a footnote, or adds or drops an output |
| `results` | changes an ARD row, no printed cell |
| `adam` | changes an ADaM cell, no ARD row |
| `none` | the same ADaM datasets, ARD and outputs |

| Class | When | `identifiable` | Review |
| --- | --- | --- | --- |
| `inert` | no value tried changes an element that an output reads (static) | `unseparated` | not asked |
| `separated` | every value tried is `fails` or `outputs` | `separated` | not asked |
| `unseparated` | some value tried is `none` | `unseparated` | asked first: the values that reproduce, the interval |
| `separated_at_dataset_only` | no value is `none`, some are `results` or `adam` | `unseparated` | asked, with the outputs that read it |

The values tried: every alternative with the examples of its slots and
every list with one item left out (`compiler.other_values`), and, for each
integer slot of the gold alternative, the values next to gold, one at a
time in both directions, until one separates or the scan ends (the bound
of the slot, or 30 steps). The interval is the run of values around gold
that give the same outputs as gold; each end is `separated`,
`slot_minimum`, `slot_maximum` or `scan_limit`.

## The test study SEP01 (the acceptance)

`specfirst.gen.sep01`: one dataset, nine subjects in three arms, six SDTM
domains with the columns of `specfirst.compile.tiny`, all dates in 2024. The
docstring lists every subject and event; what matters here:

- P2's rash starts 35 days after P2's last dose (03-15 after 02-09), and
  L2's fatigue 39 days after L2's last dose (03-20 after 02-10); neither has
  another event, and no event starts 36 to 38 days after a last dose. So a
  window of 35 to 38 days flags the same events; 34 loses the rash, 39 adds
  the fatigue.
- Every subject is randomized on 01-09, the reference start date of DM
  (RFSTDTC), before the first dose: the study day from RFSTDTC is not the
  one from the first dose. The adverse event summary shows no study day.
- L3 has a headache on 01-20 and a dizziness in 2024-01 with no day (the
  month of L3's first dose, 01-12). Under a first-of-month imputation the
  dizziness starts before the first dose and is not treatment-emergent; L3
  is in the table by the headache, and the dizziness is neither related,
  serious, fatal nor a cause to withdraw the drug.
- L4 is randomized to Low Dose and dosed with High Dose.

The gold table, worked out by hand (`sep01.EXPECTED`, held by
`test_the_gold_decisions_build_the_table_worked_out_by_hand`): N 3, 3, 3,
9 by actual treatment; any event 2, 2, 2, 6; related 0, 1, 1, 2; serious 0,
1, 1, 2; leading to discontinuation 0, 0, 1, 1; fatal 0, 0, 1, 1.

The run, from the worktree at `8154075` (the full output, every value of
every decision, is docs/reports/issue-30.sep01.log; the time of the logs
includes the wait for the shared lock):

```text
$ specfirst gen separate sep01
P4 by class on sep01/reference (sep01): 22 decisions of the units mod-treatment, mod-populations, mod-ae-emergence, tfl-ae-summary; outputs Out_AESUM; 48 builds; integer slots scanned up to 30 steps from gold
  unseparated: 10: ae.related.values (mod-ae-emergence), ae.teae.end (mod-ae-emergence), ae.teae.start (mod-ae-emergence), pop.safety.rule (mod-populations), tfl.columns.arms (tfl-ae-summary), tfl.columns.total (tfl-ae-summary), tfl.rounding.rule (tfl-ae-summary), trt.date.imputation (mod-treatment), trt.end.source (mod-treatment), trt.start.source (mod-treatment)
  separated_at_dataset_only: 1: ae.start.imputation (mod-ae-emergence)
  separated: 6: pop.safety.grouping (mod-populations), tfl.ae.summary.rows (tfl-ae-summary), tfl.output.include (tfl-ae-summary), tfl.percent.format (tfl-ae-summary), tfl.population (tfl-ae-summary), trt.actual.source (mod-treatment)
  inert: 5: date.studyday.origin (mod-treatment), disp.status.record (mod-populations), pop.efficacy.rule (mod-populations), pop.randomized.rule (mod-populations), trt.planned.source (mod-treatment)
  no_alternative: 0
  values tried, by level: fails 1, outputs 21, results 0, adam 7, none 18
  review (unseparated first):
    unseparated: ae.related.values (mod-ae-emergence); reproduce: stated_list(values=["POSSIBLE"])
    unseparated: ae.teae.end (mod-ae-emergence); days from 35 (separated) to 38 (separated)
    unseparated: ae.teae.start (mod-ae-emergence); reproduce: at_or_after_first_dose_time
    unseparated: pop.safety.rule (mod-populations); reproduce: randomized_and_dosed
    unseparated: tfl.columns.arms (tfl-ae-summary); reproduce: protocol_order
    unseparated: tfl.columns.total (tfl-ae-summary); reproduce: active_arms(control="Active Control")
    unseparated: tfl.rounding.rule (tfl-ae-summary); reproduce: half_even
    unseparated: trt.date.imputation (mod-treatment); reproduce: first_day_of_month
    unseparated: trt.end.source (mod-treatment); reproduce: ds_date_when_ex_missing
    unseparated: trt.start.source (mod-treatment); reproduce: dm_rfxstdtc, first_ex_record
    separated_at_dataset_only: ae.start.imputation (mod-ae-emergence); outputs: Out_AESUM
    separated (not asked): pop.safety.grouping (mod-populations)
    separated (not asked): tfl.ae.summary.rows (tfl-ae-summary)
    separated (not asked): tfl.output.include (tfl-ae-summary)
    separated (not asked): tfl.percent.format (tfl-ae-summary)
    separated (not asked): tfl.population (tfl-ae-summary)
    separated (not asked): trt.actual.source (mod-treatment)
    inert (not asked): date.studyday.origin (mod-treatment)
    inert (not asked): disp.status.record (mod-populations)
    inert (not asked): pop.efficacy.rule (mod-populations)
    inert (not asked): pop.randomized.rule (mod-populations)
    inert (not asked): trt.planned.source (mod-treatment)
  decisions: (four of 22)
    ae.teae.end (mod-ae-emergence) = last_dose_plus_days(days=35): unseparated, identifiable unseparated; the same ADaM datasets, results and outputs as gold under last_dose_plus_days(days=36), last_dose_plus_days(days=37), last_dose_plus_days(days=38): the data cannot tell them apart
      end_of_study: outputs (adam 4, results 4, cells 2); read by Out_AESUM
      last_dose_plus_days(days=30): outputs (adam 4, results 4, cells 2); read by Out_AESUM
      last_dose_plus_days(days=34): outputs (adam 4, results 4, cells 2); read by Out_AESUM
      last_dose_plus_days(days=36): none (adam 0, results 0, cells 0); read by Out_AESUM
      last_dose_plus_days(days=37): none (adam 0, results 0, cells 0); read by Out_AESUM
      last_dose_plus_days(days=38): none (adam 0, results 0, cells 0); read by Out_AESUM
      last_dose_plus_days(days=39): outputs (adam 4, results 4, cells 2); read by Out_AESUM
      last_dose_plus_days(days=7): outputs (adam 4, results 4, cells 2); read by Out_AESUM
      no_end: outputs (adam 4, results 4, cells 2); read by Out_AESUM
    date.studyday.origin (mod-treatment) = treatment_start: inert, identifiable unseparated; no output reads what the decision sets, under any value tried
      dm_rfstdtc: adam (adam 26, results 0, cells 0)
    ae.start.imputation (mod-ae-emergence) = first_of_month_not_before_first_dose: separated_at_dataset_only, identifiable unseparated; the outputs that read it (Out_AESUM) are the same as gold under first_of_month, not_completed; the ADaM datasets or the results differ
      first_of_month: adam (adam 4, results 0, cells 0); read by Out_AESUM
      not_completed: adam (adam 3, results 0, cells 0); read by Out_AESUM
    pop.safety.grouping (mod-populations) = actual: separated, identifiable separated; every value tried changes the outputs
      planned: outputs (adam 0, results 66, cells 10); read by Out_AESUM
  problems: 0
matrix written to /mnt/d/trial_work/specfirst-gen/build/separation/sep01.json
```

The three decisions of the acceptance:

- `ae.teae.end` = 35 days: `unseparated`; the interval of `days` is 35 to
  38, ended by 34 and 39, which separate; 36, 37 and 38 give the same ADaM
  datasets, results and table. The other alternatives (no end, end of
  study) and the examples 30 and 7 separate.
- `date.studyday.origin`: `inert`; its other value changes 26 ADaM cells
  (the study day of ADVS) and no output reads them.
- `ae.start.imputation`: `separated_at_dataset_only`; both other values
  change ADaM cells (4 and 3: the start date, its flag, the emergence
  flag) and no ARD row and no cell of Out_AESUM, the output that reads it.

`pop.safety.grouping` is the plain `separated` case (L4). Of the other 18
decisions, 9 are `unseparated`: 8 for reasons of the data that the
docstring of `sep01.CLASSES` names (one exposure record per subject with
full dates and no times, every subject randomized, no percent on a half,
the protocol order is the order of the dose, no causality PROBABLE), and
one for a reason of the catalog: the example "Active Control" of `tfl.columns.total`
names no arm of the study, so a total over all arms but that control is
the total over all arms (ADR-019, "Consequences").

The matrix written by the first run, held against a new mutation in a new
process (docs/reports/issue-30.sep01-check.log):

```text
$ specfirst gen separate sep01 --check build/separation/sep01.json
  problems: 0
the matrix build/separation/sep01.json against a new mutation: 0 differences
```

## Planted defects (rule R5)

Each plant makes the check of one class fail. The check is `sep01.check`:
every class as `sep01.CLASSES` states it, the interval of the window as
`sep01.INTERVAL` states it, and no problem of the matrix
(`separation.problems`, which holds an inert decision against its values).

| Class | Planted | What the check then finds |
| --- | --- | --- |
| `separated` | L4 dosed as randomized (`sep01.planted("separated")`) | `pop.safety.grouping` is no longer `separated`: the planned grouping gives the same cells, and its ARD rows name another grouping (TRT01P), so it is `separated_at_dataset_only` |
| `unseparated` | an event 36 days after P3's last dose | no other window reproduces: `ae.teae.end` is `separated`, its interval 35 to 35 |
| `separated_at_dataset_only` | L3's dizziness with a full date | every imputation gives the same build: `ae.start.imputation` is `unseparated` |
| `inert` | a reach that names nothing (`reach_of=lambda build: {}`) | every decision looks `inert`, and each value of the window that changes the table is a problem |

And a written matrix with the interval of the window and the class of the
rounding rule changed differs from a new mutation in exactly those two
(`separation.differences`).

What the check prints on each plant (a scratch script of the session, not
kept, that calls `sep01.planted`, `separate.Mutation` and `sep01.check`;
the log is docs/reports/issue-30.plants.log):

```text
$ python plants.py
== planted against separated: L4 dosed as randomized: pop.safety.grouping no longer separates
  pop.safety.grouping (mod-populations): separated_at_dataset_only
  check: pop.safety.grouping (mod-populations): separated_at_dataset_only; the study states separated
  the check of SEP01 fails: yes (1 lines)
== planted against unseparated: an event 36 days after P3's last dose: no other window reproduces
  ae.teae.end (mod-ae-emergence): separated; days 35 to 35
  check: ae.teae.end (mod-ae-emergence): separated; the study states unseparated
  check: ae.teae.end (mod-ae-emergence): the interval is [{'slot': 'days', 'gold': 35, 'low': 35, 'high': 35, 'below': 'separated', 'above': 'separated', 'same': [], 'dataset_only': []}]; the study states {'slot': 'days', 'gold': 35, 'low': 35, 'high': 38, 'below': 'separated', 'above': 'separated', 'same': [36, 37, 38], 'dataset_only': []}
  the check of SEP01 fails: yes (2 lines)
== planted against separated_at_dataset_only: L3's dizziness with a full date: every imputation gives the same build
  ae.start.imputation (mod-ae-emergence): unseparated
  check: ae.start.imputation (mod-ae-emergence): unseparated; the study states separated_at_dataset_only
  the check of SEP01 fails: yes (1 lines)
== planted against inert: a reach that names no element for any output: every decision looks inert, and a value that changes the table is a defect
  date.studyday.origin (mod-treatment): inert
  ae.teae.end (mod-ae-emergence): inert; days 35 to 38
  check: ae.teae.end (mod-ae-emergence): inert, yet end_of_study changes the outputs
  check: ae.teae.end (mod-ae-emergence): inert, yet last_dose_plus_days(days=30) changes the outputs
  check: ae.teae.end (mod-ae-emergence): inert, yet last_dose_plus_days(days=34) changes the outputs
  check: ae.teae.end (mod-ae-emergence): inert, yet last_dose_plus_days(days=39) changes the outputs
  check: ae.teae.end (mod-ae-emergence): inert, yet last_dose_plus_days(days=7) changes the outputs
  check: ae.teae.end (mod-ae-emergence): inert, yet no_end changes the outputs
  check: ae.teae.end (mod-ae-emergence): inert; the study states unseparated
  the check of SEP01 fails: yes (7 lines)
== the study itself: the check prints 0 lines
```

The tests that hold all of it, from the worktree at `8154075`:

```text
$ python -m pytest tests/unit/test_separation.py -v -p no:cacheprovider
tests/unit/test_separation.py::test_the_class_of_a_decision_follows_from_the_levels_of_its_values[True-levels0-separated] PASSED
tests/unit/test_separation.py::test_the_class_of_a_decision_follows_from_the_levels_of_its_values[True-levels1-unseparated] PASSED
tests/unit/test_separation.py::test_the_class_of_a_decision_follows_from_the_levels_of_its_values[True-levels2-unseparated] PASSED
tests/unit/test_separation.py::test_the_class_of_a_decision_follows_from_the_levels_of_its_values[True-levels3-separated_at_dataset_only] PASSED
tests/unit/test_separation.py::test_the_class_of_a_decision_follows_from_the_levels_of_its_values[True-levels4-separated_at_dataset_only] PASSED
tests/unit/test_separation.py::test_the_class_of_a_decision_follows_from_the_levels_of_its_values[False-levels5-inert] PASSED
tests/unit/test_separation.py::test_the_class_of_a_decision_follows_from_the_levels_of_its_values[False-levels6-inert] PASSED
tests/unit/test_separation.py::test_the_class_of_a_decision_follows_from_the_levels_of_its_values[True-levels7-no_alternative] PASSED
tests/unit/test_separation.py::test_the_class_of_a_decision_follows_from_the_levels_of_its_values[False-levels8-no_alternative] PASSED
tests/unit/test_separation.py::test_a_level_that_is_not_one_is_refused PASSED
tests/unit/test_separation.py::test_only_separated_is_separated_in_the_decision_record PASSED
tests/unit/test_separation.py::test_two_builds_are_compared_at_three_layers PASSED
tests/unit/test_separation.py::test_the_interval_says_what_ends_it_on_each_side PASSED
tests/unit/test_separation.py::test_the_review_asks_unseparated_decisions_first PASSED
tests/unit/test_separation.py::test_an_inert_decision_whose_value_changes_an_output_is_a_problem PASSED
tests/unit/test_separation.py::test_the_gold_decisions_build_the_table_worked_out_by_hand PASSED
tests/unit/test_separation.py::test_the_study_states_two_decisions_and_takes_the_house_for_the_rest PASSED
tests/unit/test_separation.py::test_a_window_that_four_values_reproduce PASSED
tests/unit/test_separation.py::test_an_inert_rule_changes_adam_and_no_output_reads_it PASSED
tests/unit/test_separation.py::test_a_rule_separated_in_adam_and_not_in_the_table PASSED
tests/unit/test_separation.py::test_every_decision_of_the_slice_has_the_class_the_study_states PASSED
tests/unit/test_separation.py::test_the_decision_record_takes_separated_only_for_the_separated_class PASSED
tests/unit/test_separation.py::test_the_review_lists_the_unseparated_decisions_first PASSED
tests/unit/test_separation.py::test_a_new_mutation_gives_the_matrix_again PASSED
tests/unit/test_separation.py::test_planted_data_make_the_check_of_one_class_fail[separated] PASSED
tests/unit/test_separation.py::test_planted_data_make_the_check_of_one_class_fail[unseparated] PASSED
tests/unit/test_separation.py::test_planted_data_make_the_check_of_one_class_fail[separated_at_dataset_only] PASSED
tests/unit/test_separation.py::test_a_planted_reach_makes_the_check_of_inert_fail PASSED
tests/unit/test_separation.py::test_a_planted_matrix_differs_from_a_new_mutation PASSED
tests/unit/test_separation.py::test_the_arms_of_a_study_come_from_dm_and_ex_in_the_order_of_the_dose PASSED
============================= 30 passed in 58.87s ==============================
```

The whole unit suite at the same commit, in the worktree:

```text
$ python -m pytest -m "not evidence" -q -p no:cacheprovider
1238 passed, 30 deselected in 1181.00s (0:19:41)
```

## cdiscpilot01, report only

The SDTM files that kits/cdiscpilot01 pins, read from the fetch cache after
their SHA-256 is checked (`separate.pilot_data`); the arms from DM and EX,
by their highest dose (the high dose is titrated; the screen failures have
no exposure and no arm):

```text
$ python -c 'from pathlib import Path; from specfirst.gen import separate; [print(arm) for arm in separate.pilot_arms(separate.pilot_data(Path.cwd()))]'
{'code': 'Pbo', 'dose': 0.0, 'names': ['PLACEBO', 'Placebo']}
{'code': 'Xan_Lo', 'dose': 54.0, 'names': ['Xanomeline Low Dose']}
{'code': 'Xan_Hi', 'dose': 81.0, 'names': ['Xanomeline High Dose']}
```
 The full house standard is
built (ADSL, ADAE, ADVS); the slice's 22 decisions are mutated. Nothing is
tuned on the pilot: neither vector is the pilot's rule set (expressing that
is std-2's).

### The house standard alone (`--vector house`)

Full output: docs/reports/issue-30.cdiscpilot01-house.log.

```text
$ specfirst gen separate cdiscpilot01 --vector house
P4 by class on cdiscpilot01/sdtm (cdiscpilot01, vector house): 22 decisions of the units mod-treatment, mod-populations, mod-ae-emergence, tfl-ae-summary; outputs Out_AESUM; 42 builds; integer slots scanned up to 30 steps from gold
  unseparated: 9: ae.start.imputation (mod-ae-emergence), ae.teae.end (mod-ae-emergence), ae.teae.start (mod-ae-emergence), pop.safety.rule (mod-populations), tfl.columns.arms (tfl-ae-summary), tfl.columns.total (tfl-ae-summary), tfl.rounding.rule (tfl-ae-summary), trt.date.imputation (mod-treatment), trt.start.source (mod-treatment)
  separated_at_dataset_only: 0
  separated: 7: ae.related.values (mod-ae-emergence), pop.safety.grouping (mod-populations), tfl.ae.summary.rows (tfl-ae-summary), tfl.output.include (tfl-ae-summary), tfl.percent.format (tfl-ae-summary), tfl.population (tfl-ae-summary), trt.actual.source (mod-treatment)
  inert: 6: date.studyday.origin (mod-treatment), disp.status.record (mod-populations), pop.efficacy.rule (mod-populations), pop.randomized.rule (mod-populations), trt.end.source (mod-treatment), trt.planned.source (mod-treatment)
  no_alternative: 0
  values tried, by level: fails 0, outputs 18, results 0, adam 12, none 11
  review (unseparated first):
    unseparated: ae.start.imputation (mod-ae-emergence); reproduce: first_of_month
    unseparated: ae.teae.end (mod-ae-emergence); reproduce: end_of_study
    unseparated: ae.teae.start (mod-ae-emergence); reproduce: at_or_after_first_dose_time
    unseparated: pop.safety.rule (mod-populations); reproduce: randomized_and_dosed
    unseparated: tfl.columns.arms (tfl-ae-summary); reproduce: protocol_order
    unseparated: tfl.columns.total (tfl-ae-summary); reproduce: active_arms(control="Active Control")
    unseparated: tfl.rounding.rule (tfl-ae-summary); reproduce: half_even
    unseparated: trt.date.imputation (mod-treatment); reproduce: first_day_of_month
    unseparated: trt.start.source (mod-treatment); reproduce: dm_rfxstdtc, first_ex_record
    separated (not asked): ae.related.values (mod-ae-emergence)
    separated (not asked): pop.safety.grouping (mod-populations)
    separated (not asked): tfl.ae.summary.rows (tfl-ae-summary)
    separated (not asked): tfl.output.include (tfl-ae-summary)
    separated (not asked): tfl.percent.format (tfl-ae-summary)
    separated (not asked): tfl.population (tfl-ae-summary)
    separated (not asked): trt.actual.source (mod-treatment)
    inert (not asked): date.studyday.origin (mod-treatment)
    inert (not asked): disp.status.record (mod-populations)
    inert (not asked): pop.efficacy.rule (mod-populations)
    inert (not asked): pop.randomized.rule (mod-populations)
    inert (not asked): trt.end.source (mod-treatment)
    inert (not asked): trt.planned.source (mod-treatment)
  decisions: (five of 22)
    ae.teae.end (mod-ae-emergence) = no_end: unseparated, identifiable unseparated; the same ADaM datasets, results and outputs as gold under end_of_study: the data cannot tell them apart
      end_of_study: none (adam 0, results 0, cells 0); read by Out_AESUM
      last_dose_plus_days(days=30): outputs (adam 8, results 8, cells 4); read by Out_AESUM
      last_dose_plus_days(days=7): outputs (adam 19, results 8, cells 4); read by Out_AESUM
    ae.start.imputation (mod-ae-emergence) = first_of_month_not_before_first_dose: unseparated, identifiable unseparated; the same ADaM datasets, results and outputs as gold under first_of_month: the data cannot tell them apart
      first_of_month: none (adam 0, results 0, cells 0); read by Out_AESUM
      not_completed: adam (adam 82, results 0, cells 0); read by Out_AESUM
    trt.end.source (mod-treatment) = last_ex_end_date: inert, identifiable unseparated; no output reads what the decision sets, under any value tried
      ds_date_when_ex_missing: adam (adam 68, results 0, cells 0)
      last_ex_start_date: adam (adam 372426, results 0, cells 0)
    tfl.rounding.rule (tfl-ae-summary) = half_away_from_zero: unseparated, identifiable unseparated; the same ADaM datasets, results and outputs as gold under half_even: the data cannot tell them apart
      half_even: none (adam 0, results 0, cells 0); read by Out_AESUM
    date.studyday.origin (mod-treatment) = treatment_start: inert, identifiable unseparated; no output reads what the decision sets, under any value tried
      dm_rfstdtc: none (adam 0, results 0, cells 0)
  problems: 0
matrix written to /mnt/d/trial_work/specfirst-gen/build/separation/cdiscpilot01-house.json
```

- 9 `unseparated`, 7 `separated`, 6 `inert`, 0 `separated_at_dataset_only`;
  no problem (no inert decision changes an output).
- With no end of treatment emergence, the end of study reproduces it: the
  table, the ARD and ADaM are the same. The pilot's data cannot tell "no
  end" from "end of study".
- The first-of-month imputation reproduces the house default exactly;
  `not_completed` changes 82 ADaM cells and nothing printed.
- The treatment end date (`trt.end.source`) is `inert` under this vector:
  without a window no output reads it, although `last_ex_start_date`
  changes 372,426 ADaM cells (ADVS included).
- The origin of the study day changes nothing on the pilot (RFSTDTC is the
  first dose date there); it is `inert` because no output reads it.

### With a window of 30 days (`--vector window`)

The same vector with `ae.teae.end` = `last_dose_plus_days(days=30)`, the
first example of the catalog, to show the interval of a numeric parameter
on real data. Full output: docs/reports/issue-30.cdiscpilot01-window.log.

```text
$ specfirst gen separate cdiscpilot01 --vector window
P4 by class on cdiscpilot01/sdtm (cdiscpilot01, vector window): 22 decisions of the units mod-treatment, mod-populations, mod-ae-emergence, tfl-ae-summary; outputs Out_AESUM; 67 builds; integer slots scanned up to 30 steps from gold
  unseparated: 9: ae.start.imputation (mod-ae-emergence), ae.teae.end (mod-ae-emergence), ae.teae.start (mod-ae-emergence), pop.safety.rule (mod-populations), tfl.columns.arms (tfl-ae-summary), tfl.columns.total (tfl-ae-summary), tfl.rounding.rule (tfl-ae-summary), trt.date.imputation (mod-treatment), trt.start.source (mod-treatment)
  separated_at_dataset_only: 1: trt.end.source (mod-treatment)
  separated: 7: ae.related.values (mod-ae-emergence), pop.safety.grouping (mod-populations), tfl.ae.summary.rows (tfl-ae-summary), tfl.output.include (tfl-ae-summary), tfl.percent.format (tfl-ae-summary), tfl.population (tfl-ae-summary), trt.actual.source (mod-treatment)
  inert: 5: date.studyday.origin (mod-treatment), disp.status.record (mod-populations), pop.efficacy.rule (mod-populations), pop.randomized.rule (mod-populations), trt.planned.source (mod-treatment)
  no_alternative: 0
  values tried, by level: fails 0, outputs 22, results 0, adam 12, none 32
  review (unseparated first):
    unseparated: ae.start.imputation (mod-ae-emergence); reproduce: first_of_month
    unseparated: ae.teae.end (mod-ae-emergence); days from 13 (separated) to 36 (separated)
    unseparated: ae.teae.start (mod-ae-emergence); reproduce: at_or_after_first_dose_time
    unseparated: pop.safety.rule (mod-populations); reproduce: randomized_and_dosed
    unseparated: tfl.columns.arms (tfl-ae-summary); reproduce: protocol_order
    unseparated: tfl.columns.total (tfl-ae-summary); reproduce: active_arms(control="Active Control")
    unseparated: tfl.rounding.rule (tfl-ae-summary); reproduce: half_even
    unseparated: trt.date.imputation (mod-treatment); reproduce: first_day_of_month
    unseparated: trt.start.source (mod-treatment); reproduce: dm_rfxstdtc, first_ex_record
    separated_at_dataset_only: trt.end.source (mod-treatment); outputs: Out_AESUM
    separated (not asked): ae.related.values (mod-ae-emergence)
    separated (not asked): pop.safety.grouping (mod-populations)
    separated (not asked): tfl.ae.summary.rows (tfl-ae-summary)
    separated (not asked): tfl.output.include (tfl-ae-summary)
    separated (not asked): tfl.percent.format (tfl-ae-summary)
    separated (not asked): tfl.population (tfl-ae-summary)
    separated (not asked): trt.actual.source (mod-treatment)
    inert (not asked): date.studyday.origin (mod-treatment)
    inert (not asked): disp.status.record (mod-populations)
    inert (not asked): pop.efficacy.rule (mod-populations)
    inert (not asked): pop.randomized.rule (mod-populations)
    inert (not asked): trt.planned.source (mod-treatment)
  decisions: (two of 22)
    ae.teae.end (mod-ae-emergence) = last_dose_plus_days(days=30): unseparated, identifiable unseparated; the same ADaM datasets, results and outputs as gold under last_dose_plus_days(days=14), last_dose_plus_days(days=15), last_dose_plus_days(days=16), last_dose_plus_days(days=17), last_dose_plus_days(days=18), last_dose_plus_days(days=19), last_dose_plus_days(days=20), last_dose_plus_days(days=21), last_dose_plus_days(days=22), last_dose_plus_days(days=23), last_dose_plus_days(days=24), last_dose_plus_days(days=25), last_dose_plus_days(days=26), last_dose_plus_days(days=27), last_dose_plus_days(days=28), last_dose_plus_days(days=29), last_dose_plus_days(days=31), last_dose_plus_days(days=32), last_dose_plus_days(days=33), last_dose_plus_days(days=34), last_dose_plus_days(days=35), last_dose_plus_days(days=36): the data cannot tell them apart
      end_of_study: outputs (adam 8, results 8, cells 4); read by Out_AESUM
      last_dose_plus_days(days=12): outputs (adam 11, results 4, cells 2); read by Out_AESUM
      last_dose_plus_days(days=13): adam (adam 7, results 0, cells 0); read by Out_AESUM
      last_dose_plus_days(days=14): none (adam 0, results 0, cells 0); read by Out_AESUM
      last_dose_plus_days(days=15): none (adam 0, results 0, cells 0); read by Out_AESUM
      last_dose_plus_days(days=16): none (adam 0, results 0, cells 0); read by Out_AESUM
      last_dose_plus_days(days=17): none (adam 0, results 0, cells 0); read by Out_AESUM
      last_dose_plus_days(days=18): none (adam 0, results 0, cells 0); read by Out_AESUM
      last_dose_plus_days(days=19): none (adam 0, results 0, cells 0); read by Out_AESUM
      last_dose_plus_days(days=20): none (adam 0, results 0, cells 0); read by Out_AESUM
      last_dose_plus_days(days=21): none (adam 0, results 0, cells 0); read by Out_AESUM
      last_dose_plus_days(days=22): none (adam 0, results 0, cells 0); read by Out_AESUM
      last_dose_plus_days(days=23): none (adam 0, results 0, cells 0); read by Out_AESUM
      last_dose_plus_days(days=24): none (adam 0, results 0, cells 0); read by Out_AESUM
      last_dose_plus_days(days=25): none (adam 0, results 0, cells 0); read by Out_AESUM
      last_dose_plus_days(days=26): none (adam 0, results 0, cells 0); read by Out_AESUM
      last_dose_plus_days(days=27): none (adam 0, results 0, cells 0); read by Out_AESUM
      last_dose_plus_days(days=28): none (adam 0, results 0, cells 0); read by Out_AESUM
      last_dose_plus_days(days=29): none (adam 0, results 0, cells 0); read by Out_AESUM
      last_dose_plus_days(days=31): none (adam 0, results 0, cells 0); read by Out_AESUM
      last_dose_plus_days(days=32): none (adam 0, results 0, cells 0); read by Out_AESUM
      last_dose_plus_days(days=33): none (adam 0, results 0, cells 0); read by Out_AESUM
      last_dose_plus_days(days=34): none (adam 0, results 0, cells 0); read by Out_AESUM
      last_dose_plus_days(days=35): none (adam 0, results 0, cells 0); read by Out_AESUM
      last_dose_plus_days(days=36): none (adam 0, results 0, cells 0); read by Out_AESUM
      last_dose_plus_days(days=37): outputs (adam 8, results 8, cells 4); read by Out_AESUM
      last_dose_plus_days(days=7): outputs (adam 11, results 4, cells 2); read by Out_AESUM
      no_end: outputs (adam 8, results 8, cells 4); read by Out_AESUM
    trt.end.source (mod-treatment) = last_ex_end_date: separated_at_dataset_only, identifiable unseparated; the outputs that read it (Out_AESUM) are the same as gold under ds_date_when_ex_missing; the ADaM datasets or the results differ
      ds_date_when_ex_missing: adam (adam 68, results 0, cells 0); read by Out_AESUM
      last_ex_start_date: outputs (adam 372870, results 22, cells 11); read by Out_AESUM
  problems: 0
matrix written to /mnt/d/trial_work/specfirst-gen/build/separation/cdiscpilot01-window.json
```

- The window: every value from 13 to 36 days gives the table of 30 days;
  12 and 37 separate (2 and 4 cells). From 14 to 36 the ADaM datasets are
  the same as well. 13 changes 7 ADaM cells and no printed cell: a window
  of 13 days drops what one of 14 keeps, the events that start exactly 14
  days after a last dose, and their subjects are counted by other events.
  On the pilot's data a window of 30 days cannot be told from one of 14 or
  of 36: the first case of the issue, on real data. The other alternatives
  (no end, end of study, 7 days) separate.
- `trt.end.source`: with a window the table reads the treatment end date.
  `last_ex_start_date` separates (11 cells); `ds_date_when_ex_missing`
  changes 68 ADaM cells and no printed cell, so the decision is
  `separated_at_dataset_only`, with Out_AESUM named.
- The other classes are those of the house vector.

The window's matrix held against a new mutation in a new process
(docs/reports/issue-30.cdiscpilot01-window-check.log):

```text
$ specfirst gen separate cdiscpilot01 --vector window --check build/separation/cdiscpilot01-window.json
  problems: 0
the matrix build/separation/cdiscpilot01-window.json against a new mutation: 0 differences
```

### The custom decisions of the efficacy tables

The 18 records of kits/cdiscpilot01/gold/decisions/efficacy.jsonl are
`custom:` decisions: they have no catalog entry, hence no listed
alternative, and no compiler joins them to the reporting events
(`specfirst.machine.decisions`). P4 has nothing to change in them; they
are not in the matrix.

## The scoring rule

The issue: "An exam never credits an `unseparated` decision as learned.
Report it apart." What is the machine's, done here:

- `separation.identifiable(class)` gives the decision record `separated`
  for the class `separated` only; `inert`, `unseparated` and
  `separated_at_dataset_only` give `unseparated`. A scorer that reads
  `identifiable` therefore never takes a table that equals gold as
  evidence for a decision of those classes; the scorer of the read track
  already compares such a decision by value and reports it apart
  (`score.reading`, `score.report`, `score.kit`).
- `separation.credited(record)`: whether results can confirm a record.
- The matrix's `review` lists the decisions in the order a person asks
  them: `unseparated` first, with the values that reproduce and the
  interval; then `separated_at_dataset_only` with the outputs named.

What is the scorer's, not done here (no file of the read track is
changed): an exam that leaves `unseparated` decisions out of "learned",
and a report that lists the classes of a reference matrix apart. The note
for the read track is in docs/state/gen.md, "P4 on a reference study",
"For the read track"; the exam itself (section 11.4, M2) does not exist
yet.

## Gates

The change adds modules, a command and tests; no check of any gate calls
it, but every gate runs the unit tests, which now hold it. The gates of
the gen track run on clean clones of `8154075` (the later commits change
documents only). read-1a and the gates of the real track are not run:
nothing they read changed (`src/specfirst/score/`, `src/specfirst/machine/`
other than the new module, `kits/`, `standard/` and the generator are as
on `main`), and the unit suite above passes.

```text
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 bash scripts/clean_clone_gate.sh gen-2a /mnt/d/trial_work/specfirst/.git 8154075
commit:     8154075
PASS  environment          0.3 s
PASS  pins                 0.9 s
PASS  lint                 0.0 s
PASS  registry             0.1 s
PASS  unit tests         393.9 s
PASS  method vectors      11.8 s
PASS  pilot tests         52.3 s
PASS  kits               172.1 s
PASS  separation          23.5 s
PASS  engines              0.1 s
PASS  splits               1.4 s
PASS  cache untouched      0.1 s
PASS  ASCII                0.0 s
GATE gen-2a: PASS

clean clone gate gen-2a: PASS (clone: /tmp/specfirst-clean-lxNLsT/specfirst)
The clone does not last: under WSL /tmp is cleared when the instance restarts, about a
minute after the last command ends. Copy what must be kept in the same command that
runs this script (docs/lessons.md, lesson 39). The log is in build/gates/gen-2a/ here.
```

```text
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 bash scripts/clean_clone_gate.sh gen-3a /mnt/d/trial_work/specfirst/.git 8154075
commit:     8154075
PASS  environment          0.3 s
PASS  pins                 1.8 s
PASS  lint                 0.0 s
PASS  unit tests         398.3 s
PASS  kits                34.8 s
PASS  parser               0.8 s
PASS  slots                0.3 s
PASS  read-back            0.3 s
PASS  bad rewrite          0.2 s
PASS  tiers                0.3 s
PASS  anchors              0.3 s
PASS  visible probes       0.3 s
PASS  summary              0.3 s
PASS  cache untouched      0.1 s
PASS  ASCII                0.0 s
GATE gen-3a: PASS

clean clone gate gen-3a: PASS (clone: /tmp/specfirst-clean-lnnobs/specfirst)
```

After the review added a test (F1, commit `0d5c153`), gen-2a ran again on a
clean clone of `5356478`, the code as it merges (the commits after it change
documents only):

```text
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 bash scripts/clean_clone_gate.sh gen-2a /mnt/d/trial_work/specfirst/.git 5356478
commit:     5356478
PASS  environment          0.3 s
PASS  pins                 0.9 s
PASS  lint                 0.1 s
PASS  registry             0.1 s
PASS  unit tests         404.2 s
PASS  method vectors      12.1 s
PASS  pilot tests         52.8 s
PASS  kits               174.4 s
PASS  separation          23.6 s
PASS  engines              0.1 s
PASS  splits               1.4 s
PASS  cache untouched      0.1 s
PASS  ASCII                0.0 s
GATE gen-2a: PASS

clean clone gate gen-2a: PASS (clone: /tmp/specfirst-clean-Zixwkz/specfirst)
```

Then `main` moved (real-5b-answers, `876938f`: 15 files, none of them
changed here). `main` was merged into `track/gen` (`db68baf`) and gen-2a
ran on a clean clone of that merge, which is the tree that goes to `main`
(the commits after it change documents only; lesson 72 says why):

```text
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 bash scripts/clean_clone_gate.sh gen-2a /mnt/d/trial_work/specfirst/.git db68baf
commit:     db68baf
PASS  environment          0.3 s
PASS  pins                 0.7 s
PASS  lint                 0.1 s
PASS  registry             0.1 s
PASS  unit tests         403.5 s
PASS  method vectors      11.3 s
PASS  pilot tests         52.2 s
PASS  kits               174.4 s
PASS  separation          23.8 s
PASS  engines              0.1 s
PASS  splits               1.3 s
PASS  cache untouched      0.1 s
PASS  ASCII                0.0 s
GATE gen-2a: PASS

clean clone gate gen-2a: PASS (clone: /tmp/specfirst-clean-e2DEpo/specfirst)
```

Logs: docs/reports/issue-30.gen-2a.gate.log, issue-30.gen-3a.gate.log,
issue-30.gen-2a.final.gate.log, issue-30.gen-2a.merged.gate.log.
Ruff and the ASCII check pass in both gates and in the worktree.

## The review

docs/reports/issue-30.review.md, an independent agent with a fresh
context, on `b9a38f4`: SIGNED, six findings, none blocking. What was done
with each:

- F1, no test reached the limits of the scan (two mutants of the scan
  passed every test). Settled: `test_the_scan_stops_at_the_bound_of_the_
  slot_and_at_its_span`, with the reviewer's three cases worked out by
  hand (a window of 3 days gives 0 to 6, `slot_minimum` and `separated`;
  with a span of 2, 1 to 5, `scan_limit` on both sides; 35 days with a span
  of 3, 35 to 38, `separated` and `scan_limit`). On the two mutants it
  fails, on the code it passes:

```text
$ flock /run/lock/specfirst-heavy.lock bash scan_mutants.sh   # a scratch script: three copies of the tree outside the worktree, the code, S3 and S4 (one line of separate.py each), then pytest -k scan_stops in each
== base: 0 changed lines
3 passed, 30 deselected in 9.04s
== S3: 1 changed lines
E               ValueError: days = 38 was not scanned
src/specfirst/machine/separation.py:266: ValueError
3 failed, 30 deselected in 8.29s
== S4: 1 changed lines
E       AssertionError: assert (-14, 'separa...-10, -9, ...]) == (0, 'slot_min..., 2, 4, 5, 6])
tests/unit/test_separation.py:243: AssertionError
1 failed, 2 passed, 30 deselected in 17.02s
```

  Log: docs/reports/issue-30.scan-mutants.log.

- F2, a value that cannot be built counts as a separation, whatever stops
  it; F3, an ARD row that differs only in the grouping it names counts as
  a changed result. Both are how ADR-019 reads "separated" and both are
  now in its item 2 for the owner; F3 was already among its consequences.
- F4, the doses of the pilot's arms had no command: the command and its
  output are in the section on the pilot.
- F5, the plants log comes from a script that was not kept: left as it
  is; the tests hold the same four plants, and the reviewer's own script
  gave the same lines.
- F6, the path of a pilot's matrix in docs/state/gen.md: corrected.

## Limits

- The values tried are the catalog's examples, so an example that names
  nothing in the study can reproduce gold for that reason alone
  (`tfl.columns.total`, control "Active Control", on SEP01 and on the
  pilot). A person reads the value that reproduces before asking.
- The scan is one integer slot of the gold alternative at a time, at most
  30 steps from gold; number slots, lists and the slots of other
  alternatives are not scanned.
- The arms of a study are given once; a value that labels the arms
  otherwise is built with the same arms.
- One dataset per study. A reference with a twin would have two matrices;
  section 9.3 settles a decision unseparated on the visible data by the
  twin.
- The pilot's two vectors are the house standard and one variant, not the
  pilot's rules: std-2 owes those, and its matrix of the pilot.
- At stage T (the reference ADaM given, the scorer's pilot) no matrix is
  made here; `separate.Mutation` takes `Data(adam=...)` the same way.

## What is left

- For the read track: the exam's "learned" and the report of the classes
  (above). Not a blocker of issue #30 as far as track gen goes.
- For the owner (ADR-019, none blocking): the class in the decision
  record (a schema change); "separated" at the outputs or at the ARD; the
  classes in std-2's matrix of the pilot.

## Files

| File | What |
| --- | --- |
| src/specfirst/machine/separation.py | the levels, the classes, the interval, the review, two matrices compared |
| src/specfirst/gen/separate.py | the builds, the reach, the scan, the matrix; the pilot's data and arms |
| src/specfirst/gen/sep01.py | the test study, its expected classes, its planted variants, its check |
| src/specfirst/gen/command.py, src/specfirst/cli.py | `specfirst gen separate` |
| tests/unit/test_separation.py | 30 tests |
| docs/decisions/ADR-019.md | the choices |
| docs/state/gen.md, CLAUDE.md, docs/lessons.md (71) | the handover, the command, the lesson |
| docs/reports/issue-30.*.log | the logs this report quotes |
