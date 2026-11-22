# catalog-2c: review (rule R7), pass 1

- Package: catalog-2c, track std (ADR-020, decision 8 as amended): the slice
  of ADR-005 moved from (`catalog@1`, `open-default@1`) to (`catalog@2`,
  `open-default@2`).
- Commits reviewed: `681697b` and `982e7cb` (`git diff 6cdeded 982e7cb`, 73
  files), with the uncommitted draft docs/reports/catalog-2c.md and the
  uncommitted section "catalog-2c (the slice)" of docs/decisions/ADR-020.md.
- Reviewer: a fresh context; no model call, no file changed but this one.
- Date: 2026-11-22.

## What I checked and how

Read first: CLAUDE.md; ADR-020 decisions 1 to 9, the owner's answer, the
amendment of decision 8 and the section "catalog-2c (the slice)"; the report
draft. Then the diff file by file, with Windows git
(`git -C D:\trial_work\specfirst-std diff 6cdeded 982e7cb -- <path>`).

1. Meaning (gen/reference.py against catalog@2 and open-default@2). Held each
   changed rule against standard/catalog@2/entries/ae.teae.start.yaml,
   ae.teae.end.yaml, trt.end.source.yaml, pop.randomized.rule.yaml,
   pop.safety.rule.yaml, tfl.ae.summary.rows.yaml, tfl.percent.format.yaml,
   their templates, and the house's defaults.yaml, adam/adsl.yaml (RANDFL),
   ars/ae-summary.yaml and layout/ae-summary.yaml. Carried right: the six
   standard rows in the order of the ARS example and of the template
   (`ANY, RELATED, SERIOUS, SERIOUS_RELATED, FATAL, DISCONTINUATION`); serious
   related and fatal related on one event (the data subsets AND both clauses);
   DOSE_MODIFIED as AEACN DOSE REDUCED or DRUG INTERRUPTED; the decimals slot;
   `by_time_when_collected` (the template's `_TRTSTMF IS NULL` and the
   reference's "dose time after 00:00" agree for every possible event, since
   nothing on that day precedes 00:00); `last_ex_record_end` over every
   exposure record; the fixed rule `randomized_subject` (a DS record
   RANDOMIZED, the study-level fallback to ARMCD, as RANDFL of the house
   does); `end_of_study` refused. One latent gap: F8.
2. The probes. Read probes.yaml of catalog@2, the two recipes
   (`_undosed_after_last`, `_timed_before_dose`), their finders and plants.
   Worked the dates: the record of dose zero covers the last three days, the
   event lies at the last dosed day + window + 2, so it is emergent only under
   `last_ex_record_end` (window from the last dosed day + 3), not under the
   three other alternatives; the timed event two hours before a dose of 08:00
   to 11:45 separates the two pairs probes.yaml names and not the third. The
   probes of `end_of_study` are gone from RECIPES, FINDERS, UNDO, REACHES,
   core_findings.yaml and the scenarios; what remains names catalog@1 by label
   (std-1 tests) or is the append-only store. REACHES and `fits`: F1.
3. Sampling. Read decisions.py whole; reproduced the vectors of kits 1, 2, 6
   and 10 of the gate seed attempt by attempt (script below) and held them
   against the gate log of gen-2a on `681697b`
   (docs/reports/catalog-2c.gen-2a.gate.log): they match line for line.
   Findings F1 and F4.
4. The numbers. Worked out by hand from the subject lists in the module
   docstrings, before looking at the asserts:
   - HAND01 `EXPECTED`, visible and twin, all 56 cells (safety set
     randomized and dosed: visible P1 P2 / L1 L2 / H1 H2, N = 2, 2, 2, 6; twin
     P1 P2 P3 / L1 L2 / H1 H2, N = 3, 2, 2, 7; L1's rash 02-08 + 30 = 03-09 in,
     P2's rash 02-09 + 30 = 03-10 < 03-11 out). All equal.
   - HAND01 planted defects (tests/unit/test_score_hand.py `EXPECTED`): S1 2/2,
     S2-set 12/11 (2 headers + 4 low dose + 6 total; twin 2 + 4 + 5, FATAL
     total stays 0 (0.0)), S2-set-rule 0/9 (X1 into high dose: header, ANY,
     DISCONTINUATION; total: header, ANY, RELATED, SERIOUS, SERIOUS_RELATED,
     DISCONTINUATION), S3 0/2, S4 2/1, S5 7/7, S7 6/6 (visible: the six total
     percents; twin: 33.3 and 57.1, 28.6, 14.3, 14.3, 14.3), S10 0/2. All equal.
   - The attribution scenarios: 8 visible and 2 + 12 twin cells for no_end with
     zero blank; 12 visible, 5 + 6 twin for the safety rule with the randomized
     set (the six total cells wrong under each decision alone); arm S 6 pending
     + 7 total-column cells + 15 right; stage T 21 right. The separation of
     `trt.end.source` by the last start date: 4 visible, 0 twin. All equal.
   - SEP01 `EXPECTED`, 21 cells (window 35: P2's rash on 03-15 in, L2's
     fatigue on 03-20 out; L3's dizziness completed to 01-12). Equal.
   - tests/unit/test_gen_reference.py: `HOUSE_2` table (N 1 and 2; L1's
     serious event 41 days after 04-30), the timed cases (07:30 and 08:00
     against 08:00), H1's record of dose 0 to 04-30, the randomized set by DS,
     the decimals ("1 (33)", "0 (0)", "1 ( 33.33)", "0 (  0.00)") and the rows
     case (SERIOUS_RELATED and FATAL_RELATED 1 (33.3) and 1 (25.0),
     DOSE_MODIFIED 1 (100.0), 0, 1 (25.0)). All equal.
   - The pilot test numbers (15 correct, 6 open, 6 no_row, 27 cells) agree with
     9 rows by 3 columns and the crosswalk; I did not rebuild the pilot.
5. Changed expectations. Every changed assert of the 20 test files read with
   its reason. Most follow from catalog@2 (pairs 3 to 1 for ae.teae.end, the
   late subject 2 to 1, classes 7/9/5/1, stage T of HAND01 now one wrong
   decision); the std-1 tests are pinned to version 1 by label. Findings F3 and
   F7.
6. Defaults by design. Grepped every call of `default_decisions`,
   `default_value`, `defaults`, `base_vector` and `house_vector` in src/. Where
   the design is known each takes its features (documents, gate3 tiers,
   decisions, scorer `Case.features`, kit case and plant, HAND01, SEP01, pilot,
   separation of the pilot). The calls without features are the catalog and
   house checks, the overview, the reading notes (after `by_design`) and
   `specfirst compile --defaults`, where no design is known; `default_value`
   raises there for a default by design rather than guess. No finding.
7. The gate fixes of `982e7cb`. gen-3a plants: generic, and a wrong pick fails
   the check rather than passes it. S7: right to not apply at 0 decimals.
   harness/gate.py skills copy: needed, hides nothing. The pilot crosswalk:
   F2.
8. The kept run and the store. Scanned the kept files for account names, user
   folders, `Users`, the e-mail of the commits and non-ASCII: none; the
   placeholders and the classes of local folders are those of the old run
   (F9 is a note). The store: `git diff` of paragraphs.jsonl and calls.jsonl
   has 23 added lines and no other; the six new call files hash to the
   SHA-256 recorded in calls.jsonl; 64268 + 74146 + 52467 + 57251 + 60793 =
   308925 tokens as the report says; the kept run's record has USD 0.800268,
   25 turns, 108.7 s.
9. The documents: report, ADR-020's section, CLAUDE.md, docs/state/gen.md and
   docs/state/read.md held against the code. Findings F4, F5, F6.

Commands with their output (excerpts):

```text
$ grep -c "drawn again" docs/reports/catalog-2b.gen-2a.gate.log docs/reports/catalog-2c.gen-2a.gate.log
docs/reports/catalog-2b.gen-2a.gate.log:0
docs/reports/catalog-2c.gen-2a.gate.log:19
$ grep "PASS kits" docs/reports/catalog-2b.gen-2a.gate.log docs/reports/catalog-2c.gen-2a.gate.log
docs/reports/catalog-2b.gen-2a.gate.log:-- PASS kits (208.4 s)
docs/reports/catalog-2c.gen-2a.gate.log:-- PASS kits (480.6 s)
```

A script outside the checkout (scratchpad, `window_claims.py`; no build, only
`pgfix.sample`, `decisions.sample` and `probes.reaches`), 60 designs of seeds
`review-2c-<n>`, 6 attempts each:

```text
vectors 360; ae.teae.end at the house default (30 days): 202; claimed no_end|30 days with a follow-up other than 30: 104
  follow-up  7 days: 66 vectors, default kept 44, claim with no planted event 24
  follow-up 14 days: 96 vectors, default kept 48, claim with no planted event 41
  follow-up 28 days: 114 vectors, default kept 61, claim with no planted event 39
  follow-up 30 days: 84 vectors, default kept 49, claim with no planted event 0
```

The vectors of kit 10 of the gate seed, attempt by attempt (`kit_attempts.py`,
same functions as `kits._generate`; window_days 14; the gate refused 0 to 9
and took 10):

```text
attempt 0: end last_dose_plus_days 14, percent zero_blank 2, claims window True, rounding True
attempt 1: end last_dose_plus_days 30, percent always 1,     claims window True, rounding True
attempt 2: end last_dose_plus_days 30, percent zero_blank 0, claims window True, rounding True
attempt 3: end last_dose_plus_days 14, percent zero_blank 2, claims window True, rounding True
attempt 4: end last_dose_plus_days 30, percent always 1,     claims window True, rounding True
attempt 5: end no_end,                 percent zero_blank 0, claims window True, rounding True
attempts 6 to 9: end last_dose_plus_days 30, percent ... 1,  claims window True, rounding True
attempt 10: end no_end,                percent always 1,     claims window True, rounding True   (taken)
attempt 11: end last_dose_plus_days 30, percent zero_blank 1, claims window True, rounding True
```

(output shortened to the three values; the gate log of kit 10 names
tfl.rounding.rule for attempts 0, 2, 3, 5 and ae.teae.end for 1, 2, 4, 6 to 9.)
The same functions give the follow-up length of each kit of the gate seed
(`kit_follow.py`): kits 1 to 10 have 7, 7, 14, 30, 28, 14, 30, 28, 14 and 14
days.

Targeted tests, under the heavy lock with 4 processors:

```text
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 python -m pytest -q -p no:cacheprovider \
    tests/unit/test_gen_reference.py tests/unit/test_gen_probes.py tests/unit/test_gen_decisions.py \
    tests/unit/test_score_hand.py tests/unit/test_pending.py tests/unit/test_separation.py
167 passed in 188.28s (0:03:08)
```

The tests pass on `982e7cb`: the findings below are not failing tests, they
are what the tests do not hold.

## Findings

### F1 (blocking): REACHES claims two differences that no planted record makes under catalog@2 and open-default@2

Where: src/specfirst/gen/probes.py:155-158 (`ae.teae.end`), :172-177
(`tfl.rounding.rule`); the recipes `_after_window` (:643-656) and
`_rounding_half` (:707-752); src/specfirst/gen/decisions.py:209-243 (`fits`);
src/specfirst/gen/kits.py:91 (`MAX_ATTEMPTS = 12`).

What is wrong. A line of REACHES is a prediction that a pair of alternatives
differs in the output under the other decisions of the vector; a kit whose
claimed pair does not differ is unfit and its vector is drawn again. Two
predictions no longer hold under the values catalog-2c brought in:

- (a) `ae.teae.end`: `no_end|last_dose_plus_days` is claimed whenever the
  table shows ANY or SERIOUS on an analyzed set, whatever the window's days.
  The planted events of `ae_starts_after_emergence_window` lie N and N + 1
  days after the last dose, N the follow-up length (7, 14, 28 or 30 days in
  pgfix). Under open-default@1 the default was `no_end` and a stated window
  always had N days. Under open-default@2 the default window is 30 days: in
  every design whose follow-up is 7, 14 or 28 days both planted events lie
  inside it, and the claim is false. The note of REACHES says so in words ("a
  window that is longer or shorter may leave the planted events on one
  side"); the condition does not.
- (b) `tfl.rounding.rule`: the rounding probe sets the counts of one arm to
  1, 5, 9 or 13 in 16 (6.25, 31.25, 56.25, 81.25 percent), a half at one
  decimal only. catalog@2 gives `tfl.percent.format` the slot `decimals` and
  the sampler now draws 0 and 2 (decisions.py:186-188); at 0 decimals both
  rules give 6, 31, 56, 81, at 2 decimals nothing is rounded. The claim has
  no condition on the decimals, though the report says of the decimals that
  1 "is the one the probes separate with" (catalog-2c.md:46-47).

Why it matters.

- The gate seed came within one draw of failing: kit 10 was taken at attempt
  10 of 12, and attempt 11 would have been refused as well (window 30, claim
  true). One more refusal and `specfirst gen kits` raises KitError; any
  change of a stream (a new generator, a new scenario) can tip it. Seeds
  outside the checkout (dev, test, and the sealed kits generated at exam
  time) meet the same odds unseen: in my sample 104 of 276 vectors of designs
  with a follow-up other than 30 days carry claim (a) with nothing planted
  behind it, before (b) is counted.
- The kits are biased against the house's own default. The default window
  survives only in a vector where it is not claimed (a table on the
  efficacy set, or on a randomized set that asks for a post-baseline value).
  In the gate seed eight kits have a follow-up other than 30 days (kits 1, 2,
  3, 5, 6, 8, 9, 10; kits 4 and 7 have 30); of these only kit 2 keeps the
  default window, and there ae.teae.end is "read without a probe". No kit of
  the gate seed separates the default window of open-default@2 in a design
  whose follow-up is not 30 days, and the survivors drag the coverage down.
  Against catalog-2b's gen-2a log: kits that are applicable for trt.start.source,
  trt.date.imputation, ae.start.imputation, ae.teae.start and ae.teae.end go
  from 8 to 5; tfl.rounding.rule is separated in 4 kits instead of 8;
  ae.teae.end in 9 instead of 10; the kits step takes 480.6 s instead of
  208.4 s (19 vectors drawn again, 0 before).
- The report says nothing of it, though decision 8 as amended asks that the
  gates be run "with their new expected values, each difference stated in the
  report".

What would settle it. Make the two predictions true and test them in
`test_reaches_is_evaluated_on_a_decision_vector`: for (a) a pair condition
that claims `no_end|last_dose_plus_days` only when the vector's window is
`no_end` or has `parameters.window_days` days, or (better for the reader) a
recipe that also plants events at the house's 30 and 31 days so that the
default is separated; for (b) a condition on `tfl.percent.format` decimals
equal to 1 (or counts at a half for 0 and 2 decimals). Then run gen-2a again
and state in the report the vectors drawn again and the coverage table
against catalog-2b's.

### F2 (to fix): the pilot's crosswalk leaves out two rows the house now has

Where: src/specfirst/score/pilot.py:17-24 and :72-81 (`ROWS`), :194-195 (the
key's row label), :353-355 (`no_row`).

What is wrong. The module defines the crosswalk as "the same row when they
count the same events". catalog@2 and open-default@2 have `FATAL_RELATED`
(TRTEMFL, AESDTH and RELGR1) and `DOSE_MODIFIED` (AEACN DOSE REDUCED or DRUG
INTERRUPTED), the data subsets the catalog's notes take from the same ARS
example; `982e7cb` still maps An07_06 and An07_07 to None and redefines
`no_row` as "the house's standard rows have no such row".

Why it matters. With None the key keeps the example's label for those rows
(line 195), so a reader of arm R on the pilot who states a list of rows with
FATAL_RELATED and DOSE_MODIFIED builds rows that never meet the key's: their
cells stay `no_row`, right or wrong. `no_row` becomes a property of arm S's
vector, not of the catalog, which changes what the pilot report means
without a decision saying so.

What would settle it. Map the two analyses to their codes and let the trace
try a stated list that holds the key's rows (or class those cells as
explained by tfl.ae.summary.rows); or keep None and record the narrowing as a
reading with its reason (ADR-016 or ADR-020) and say in the report that arm R
cannot earn those cells.

### F3 (to fix): the pilot's joint explanation lost its only witness

Where: tests/score/test_score_pilot.py:88-111 (`arm_r_no_output`), the path
it held being src/specfirst/score/pilot.py:337-344.

What is wrong. Before, the reader that leaves the output out had 5 cells
explained by `tfl.output.include` together with one more decision; under
open-default@2 the house default already gives the key's text, and the test
now asserts `joint == []`. No other test makes a cell that needs the output
decision and one more decision.

Why it matters. Rule R5 in spirit: the branch that keeps `item.first` and
adds a second decision is now exercised only by an assert that it finds
nothing; a regression that drops the second decision would pass.

What would settle it. Give `arm_r_no_output` the percent format of
open-default@1 as well (`one_decimal_zero_blank`, 1 decimal): the five counts
of zero are then joint again, and the assert can say so.

### F4 (to fix): the sampler never states `one_decimal_always` with 0 or 2 decimals, and the documents say it draws them

Where: src/specfirst/gen/decisions.py:137-150 (`variants`, one value per
alternative with the first slot value), :264-283 (`others` and the slot
draw); docs/reports/catalog-2c.md:43-47, docs/state/gen.md (the sampling
paragraph of "From catalog-2c"), ADR-020 section "catalog-2c", bullet 5.

What is wrong. `variants` offers `one_decimal_always` only with 1 decimal,
which is the house default and is dropped from `others`; the slot is drawn
again only for the alternative that was picked, so only
`one_decimal_zero_blank` takes 0 and 2. My reproduction of 48 vectors shows
`one_decimal_always` with 1 decimal every time. "A stated value may be the
default's alternative with other slot values" holds for ae.teae.end only,
because there the first slot value (the follow-up length) differs from 30.

Why it matters. Whole percentages with a count of zero shown "0 (0)", the
shape of #1 and of the pilot's 14-2.01, never reach a kit or the reader; and
the three documents claim more than the code does.

What would settle it. Offer every alternative with each slot value whose
value differs from the default (and add the texts the new statements need),
or write in the report, gen.md and ADR-020 that only `one_decimal_zero_blank`
takes 0 and 2 decimals.

### F5 (to fix): ADR-007, decision 10, still names the old held-out combination

Where: docs/decisions/ADR-007.md:153-158; src/specfirst/gen/decisions.py:56-63.

What is wrong. ADR-007 holds out "no total column" with "columns in protocol
order"; `HELD_OUT` is now the total over all arms with the protocol order.
The change is told in ADR-020's new section and in gen.md, not in the ADR
whose decision it changes.

Why it matters. A reader of ADR-007 (the exam's split rule, PLAN.md section
6.7) gets the wrong combination.

What would settle it. One line in ADR-007, decision 10 (or under it) naming
the change and ADR-020; and in ADR-020's section the words "this changes
ADR-007, decision 10".

### F6 (to fix): the report leaves out what the gates and the model use need

Where: docs/reports/catalog-2c.md:11, :129-151, :253-264.

What is wrong.

- Line 11 names `681697b` only; `982e7cb` is part of the package.
- "Three checks failed" lists five checks of three gates (gen-3a slots and
  bad rewrite, read-1a kits and pilot tests, read-2a skills).
- The gates catalog-2b, std-1, gen-1a and gen-2a ran on `681697b` (their logs
  say so); the report does not say which commit each gate ran on, nor that
  `982e7cb` changes none of the files those four run.
- The differences of gen-2a against its earlier expected values (F1: 19
  vectors drawn again, the coverage table, the time) are not stated.
- "the whole stays inside the total" (USD 1.6) is said without the USD of
  the two subagent calls; only their tokens are given (rule R8: the number
  behind the claim). The dry run's USD 0.80 against its share of 0.6 is
  stated, which is right; the base session's condition ("any model use beyond
  the estimate sent needs the owner again") should be answered with the
  number.

What would settle it. Name both commits; say "three gates, five checks";
give each gate's commit; add the gen-2a differences; give the cost of the
two calls in USD (or say how it is bounded) beside the dry run's.

### F7 (note): no F9 case for the two new probes

Where: tests/unit/test_gen_probes.py:616-639 (`F9`).

The UNDO plants make both finders fail (R5 holds), but no case keeps the
pattern while the alternatives stop differing: the record of dose zero made
placebo (then it has a dose by the catalog's definition), or the time of the
dose kept in EX and dropped from DM.RFXSTDTC for the timed event. Both
finders already handle them (`with_dose`, the two texts compared); a case
each would hold it.

### F8 (note): an hour-only start time is "collected" but counted as 00:00

Where: src/specfirst/gen/reference.py:138-144 (`seconds_of` returns 0 below 16
characters) and :333-341.

For `by_time_when_collected` an AESTDTC such as "2024-03-10T09" is `timed`,
yet its seconds are 0: the reference calls it before a dose at 08:00 and not
emergent, while the template (precision hour, time imputed first, 09:00)
calls it emergent. No generated record has an hour-only time, so no build
differs; the reference as a second reading is wrong there. Read the hour
(and minutes when present), or mark the case as a READING.

### F9 (note): the deny list of the kept run names the author's session folder

Where: src/specfirst/harness/kept/R-task-b6706bdac1d8/run.json:213-230.

Besides `<home>` and `<checkout>`, the list holds
`<home>/AppData/Local/Temp/claude/<project hash>/<session id>/scratchpad/r2c/runs`,
`D:/trial_work` and `/root/sf-2c-r/kits`. No account name, no credential;
the old run held the same classes (`specfirst-real5a`, `/root/scratch-real5a`).
The report's "the CLI's own folders under `<home>` stay" is a little short of
it: the runs folder in a session's scratchpad is not the CLI's own.

### F10 (note): two pilot vectors that are one

Where: src/specfirst/gen/separate.py:438-447; CLAUDE.md (`--vector
house|window`).

Under open-default@2 `window` equals `house`, as the comment says;
`specfirst gen separate cdiscpilot01 --vector window` reports the same matrix
twice. Drop it, or make it a value that is not the default (`no_end`).

### F11 (note): S7's words still say one decimal

Where: src/specfirst/score/defects.py:289-305 and :403-405.

"the grid then rounds that number again, to its one decimal: 66.7 becomes
67.0": with 2 decimals it becomes 67.00, with 0 the defect does not apply.

## Verdict

F1 blocks: REACHES must be true for the values the move brought in (the
house's default window, the decimals slot) before the kits of every seed are
generated on it; F2 to F6 are to fix with it, F7 to F11 are notes.

Verdict: NOT SIGNED (pass 1); blocking: F1.

# Pass 2

- Commits reviewed: `b183940` (the answers to F1 to F11), `f5de3fb` (the
  generator `catalog-2c.2`), `9d4b48f` (five texts, the new kept dry run)
  and the merge `1e24e3c` (main `e123599`, issue #29). Read as
  `git diff 982e7cb 9d4b48f` (36 files), `git show --cc 1e24e3c`, and
  `git diff 9d4b48f 1e24e3c` / `git diff e123599 1e24e3c`; with the
  uncommitted report docs/reports/catalog-2c.md, docs/state/std.md and the
  gate logs docs/reports/catalog-2c.<wp>.gate.log of `9d4b48f`.
- Same rules as pass 1: no model call, no file changed but this one.
- Date: 2026-11-22.

## What I checked and how

1. Each finding of pass 1 against the code and the gate logs of `9d4b48f`
   (below, "F1 to F11").
2. The fix of F1 on data, not only on the claim: a script outside the
   checkout (scratchpad, `followup_window.py`; `pgfix`, `study.simulate`,
   `sdtm.build` and the hand calculation `gen.reference`, no machine, no
   build) on six twins whose follow-up is 7, 14 or 28 days, at the house
   defaults otherwise:

   ```text
   review-2c-fw-0: follow-up 7; cells that differ: no_end vs 30 days 2, no_end vs 7 days 2, 30 vs 7 days 1
   review-2c-fw-1: follow-up 7; cells that differ: no_end vs 30 days 1, no_end vs 7 days 1, 30 vs 7 days 1
   review-2c-fw-4: follow-up 14; cells that differ: no_end vs 30 days 1, no_end vs 14 days 1, 30 vs 14 days 1
   review-2c-fw-5: follow-up 7; cells that differ: no_end vs 30 days 1, no_end vs 7 days 2, 30 vs 7 days 1
   review-2c-fw-6: follow-up 28; cells that differ: no_end vs 30 days 1, no_end vs 28 days 2, 30 vs 28 days 1
   review-2c-fw-7: follow-up 14; cells that differ: no_end vs 30 days 2, no_end vs 14 days 2, 30 vs 14 days 1
   ```

3. The sampler of F4 (`kit_vectors2.py`, same functions as
   `kits._generate`): the first vector of each kit of the gate seed, which is
   the vector the gate took (it drew none again), and the shares over 400
   vectors of 80 designs:

   ```text
   kit 1: follow-up 7; end no_end; percent always 1; claims rounding True
   kit 2: follow-up 7; end 30 days; percent zero_blank 2; claims rounding False
   kit 3: follow-up 14; end 30 days; percent always 1; claims rounding True
   kit 4: follow-up 30; end 30 days; percent always 2; claims rounding False
   kit 5: follow-up 28; end no_end; percent always 2; claims rounding False
   kit 6: follow-up 14; end 30 days; percent always 0; claims rounding False
   kit 7: follow-up 30; end 30 days; percent always 2; claims rounding False
   kit 8: follow-up 28; end no_end; percent zero_blank 2; claims rounding False
   kit 9: follow-up 14; end 30 days; percent always 2; claims rounding False
   kit 10: follow-up 14; end 30 days; percent always 1; claims rounding True
   tfl.percent.format over 400 vectors: always 0: 40, always 1: 212, always 2: 52, zero_blank 0: 33, zero_blank 1: 34, zero_blank 2: 29
   ae.teae.end over 400 vectors: 30 days (the house): 224, the follow-up length: 69, no_end: 107
   ```

   (shortened to the values that matter; window_days is 30 in every kit.)
4. The gate logs of `9d4b48f`: all seven say "at commit 9d4b48f... (clean)"
   and PASS; gen-2a has 0 lines "drawn again" and "-- PASS kits (242.3 s)".
   I held the report's three-column table of gen-2a (2b, `681697b`,
   `9d4b48f`) row by row against the separation tables of the three logs
   (the first two as quoted in pass 1): every number agrees.
5. The kept run `R-task-6e527ae6baab`: the SHA-256 of its seven files equal
   binding.json; the binding names generator `catalog-2c.2`, `open-default@2`,
   catalog version 2; run.json USD 0.729859, 23 turns, 94.9 s, passed; no
   account name, no e-mail, no non-ASCII. `R-task-b6706bdac1d8` is gone from
   src/specfirst/harness/kept/.
6. The store: `git diff 982e7cb 9d4b48f` of paragraphs.jsonl and calls.jsonl
   has 7 added lines and none other; the six files of `catalog-2c-rewrite-2`
   and `catalog-2c-readback-2` hash to calls.jsonl; 308925 + 53220 + 54421 =
   416566 tokens. Read the five new texts against their statements: each
   says the same.
7. Model use: the report's arithmetic redone (118,044 and 107,641 tokens;
   x 2.7 and x 6 per million; USD 0.32/0.71 and 0.29/0.65; 1.5302 + 0.61 =
   2.14, + 1.35 = 2.88). The list prices it uses are those of the model table
   of the claude-api skill bundled with this CLI (Sonnet 5.5: USD 2 input, 10
   output, 0.10 cache read per million; a five-minute cache write at 1.25
   times input, 2.50). Under the owner's USD 3.0 in either case.
8. The merge. `git show --cc 1e24e3c`: one conflict, CLAUDE.md, the kit line
   (main: `specfirst recompute`) and the gen line (2c: `--vector house`), both
   kept. `git diff e123599 1e24e3c -- src/specfirst/gates.py` is exactly 2c's
   change of the file (the std-1 checks by label, 34 lines);
   `git diff 9d4b48f 1e24e3c -- src/specfirst/gates.py` is issue #29's part.
   The merge base is `6cdeded`. src/specfirst/recompute imports only
   `specfirst.kit`, `machine`, `paths` and `recompute` (grep of its
   imports), and so do its tests; `git diff --stat 6cdeded 9d4b48f --
   src/specfirst/machine src/specfirst/kit.py src/specfirst/kit
   src/specfirst/recompute standard env kits r` is empty. The coordinator's
   claim holds.
9. ASCII and CRLF over the 74 files changed since pass 1 (the merge
   included), the report, std.md and the gate logs: none. No name or user
   path in the 2c documents (one false match: the study ID `SF6XJW92`).
10. Targeted tests on the merged tree, under the heavy lock with 4
    processors:

    ```text
    $ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 python -m pytest -q -p no:cacheprovider \
        tests/unit/test_gen_probes.py tests/unit/test_gen_decisions.py tests/unit/test_gen_reference.py \
        tests/unit/test_score_pilot_pins.py tests/unit/test_versions.py tests/unit/test_recompute.py
    118 passed in 37.82s
    ```

    The pilot tests (marker `evidence`) and the full suite I did not run: the
    gates read-1a and the twelve of the merge run them.

## F1 to F11

- F1, settled. `Parameters.window_days` is the house's window
  (`probes.house_window()`, 30 days), `follow_up_days` a second slot value;
  REACHES claims the rounding rule at 1 decimal only. On `9d4b48f` gen-2a
  drew no vector again, ae.teae.end is separated in 10 of 10 kits (9 on
  `681697b`), and the default window of 30 days is separated in kits 2, 3,
  6, 9 and 10, whose follow-up is 7 or 14 days. On data (item 2 above) the
  default, the follow-up window and no_end differ in every twin. The
  stated follow-up window appears in no kit of the gate seed (item 3), so
  it is held by that check and by reasoning (both planted events, at 30 and
  31 days, lie outside any shorter window), not by a gate. G3 and G4 are
  what the tests do not hold.
- F2, settled in substance. All eight analyses map to their codes, the trace
  tries the key's list of rows, and arm S's three cells of the dose
  modifications are explained by tfl.ae.summary.rows. The report's own
  summary sentence is now wrong: G1.
- F3, settled: `arm_r_no_output` holds 5 joint cells
  (tfl.output.include with tfl.percent.format) again.
- F4, settled: `decisions.stated`, an alternative first, then its slot
  values; `one_decimal_always` with 0 and 2 decimals is drawn (item 3).
  No unit test holds it: G4.
- F5, settled: ADR-007, decision 10 names the change and ADR-020.
- F6, settled: the report names the six commits; "five checks of three
  gates"; the gate table gives each gate's commit; the gen-2a comparison and
  the vectors drawn again are stated; the model use has the USD of the
  subagent calls, estimated from list prices, with the no-cache bound.
- F7, settled: three F9 cases (the zero-dose record named placebo, the
  event removed, the dose time in DM only).
- F8, settled for the event; it moves the asymmetry to the dose: G5.
- F9, settled: the report describes the deny list as it is (the session
  scratchpad, the task folder of the first run, `D:/trial_work`, the kit
  folder under WSL).
- F10, settled: the vector `window` is gone from separate.py, the command's
  help and CLAUDE.md.
- F11, settled.

## Findings of pass 2

### G1 (to fix): the pilot report's summary sentence miscounts after F2

Where: src/specfirst/score/pilot.py:461-481 (`lines`), :339 and :343
(`not_built`, `never_built`), :486-490 ("rows not built").

What is wrong. The sentence was written when a cell explained by a decision
lay in a row both tables have and a `no_row` cell lay in a row the catalog
lacks. Since F2 neither holds. On arm S the read-1a log of `9d4b48f` prints
(line 398): "Of the 15 cells of the rows both tables have, 3 differ and are
explained by another value of one table decision ... 9 are in rows that arm
S does not build: 9 for a variable the reference ADaM lacks, 0 in rows the
catalog does not have". The 15 shared cells are all right (correct 15); the
3 explained cells are the dose modifications, a row arm S does not build, so
12 cells lie in rows it does not build. For arm R and the reader without the
output the sentence would say "3 in rows the catalog does not have" of the
dose modifications, which catalog@2 has. And "rows not built: RELATED,
SERIOUS_RELATED" (line 401 of the log) leaves out FATAL_RELATED, whose three
cells are `open` through `never_built`.

Why it matters. The pilot report is report only, but it is the text a
reader of ADR-005, decision 5 reads; the per-cell lines are right and the
summary contradicts them. The tests hold the states, not the sentence.

What would settle it. Count the cells by state and by whether their row is
in the candidate's table; word `no_row` as "rows no one table decision
builds with the key's text"; list `never_built` with `not_built`; and assert
the sentence of arm S and of arm R in tests/score/test_score_pilot.py.

### G2 (note): the generator reads the house window from `repo_root()`, not from the root it is given

Where: src/specfirst/gen/probes.py:245-252 (`house_window`, `lru_cache`,
`houses.load_pair(None)`) and :269-281 (`Parameters.of`).

`kits._generate(root, ...)` and `study.simulate` pass a root and a house;
`Parameters.of(design)` ignores both and loads the default pair of
`repo_root()` once per process. With SPECFIRST_ROOT naming another place the
generator raises `HouseError` (my first script run met it: SPECFIRST_ROOT
pointed at a folder that is no checkout) or, with another checkout, takes
that checkout's window. Normally the two are the same checkout. Pass the
house (or its window) to `Parameters.of` and drop the cache.

### G3 (note): two asserts of the probe tests hold the old meaning by coincidence

Where: tests/unit/test_gen_probes.py:696 and :703.

They assert `window_days == designs.follow_up_days(design)`; window_days is
now the house's window, and the asserts pass only because the test design
`probes-full-0` has a follow-up of 30 days (`probes-a`, `-c`, `-d` too;
`probes-b` has 28). For the same reason every UNDO, F9 and reach test runs on
a design where the house window is the follow-up, the case pass 1's F1 was
not about; the case is held by test_gen_decisions.py:51-53 (a design of 28
days whose variant has 30) and by the gate. Assert `window_days ==
probes.house_window()` and `follow_up_days == designs.follow_up_days(design)`.

### G4 (note): no unit test holds F4

Where: tests/unit/test_gen_decisions.py:67-95.

The sampled-vector test collects the alternatives drawn, not their slot
values: a return to the old draw (one value per alternative) passes every
unit test. It would show at read-2a, where the kept run is bound to kit 4
(`one_decimal_always`, 2 decimals). Assert that over the 150 vectors
`one_decimal_always` appears with 0 and 2 decimals and `last_dose_plus_days`
with the follow-up length, and never the default as a stated value.

### G5 (note): F8 moves the reference's asymmetry from the event to the dose

Where: src/specfirst/gen/reference.py:138-146 and :337-341; the template
standard/catalog@2/templates/ae.teae.start.yaml (`_TRTSTMF IS NULL`) with
trt.date.imputation.yaml (`imputation_flag ... seconds_collected: false`).

For `by_time_when_collected` the template counts an event time of the hour
alone as collected (precision hour) but a dose time of the hour alone as not
(TRTSTMF is set when the minutes are imputed). The reference now reads both
as collected (start_time of "T09" is 09:00), so for an event timed before an
hour-only dose on that day the reference says not emergent and the build
emergent. Before F8 the mismatch was on the event side. No generated dose or
event has an hour-only time, so no build differs. Pick one reading for both
sides and state it (READING in reference.py, or the template).

### G6 (note): the stated follow-up window has texts for 14 days only

Where: src/specfirst/gen/rewrites/paragraphs.jsonl.

`last_dose_plus_days` with 7 or 28 days (a stated follow-up length in a third
of the designs) has no accepted text; a kit of another seed that states it
fails gen-3a until a call adds one. This is the rule CLAUDE.md states for
any new statement, and no gate kit states it (item 3); the note is so that
the next set of kits is not a surprise.

### G7 (note): tfl.rounding.rule is separated in 3 kits of 10

With the claim at one decimal only, rounding is applicable and separated in
the three kits that show one decimal; six kits of the gate seed draw 2
decimals (over 400 vectors one decimal is 61.5%; the seed is an unlucky
draw). The report says so. A count at a half for 0 and 2 decimals
(x.5 and x.xx5 percent) would let the probe separate there too.

### G8 (note): docs/state/std.md says what is not yet so

The uncommitted std.md says the twelve gates of the merge passed and
"pass 2 signed". Commit it only when both are true, as the report's section
"main merged in" will show.

## Verdict (pass 2)

F1 is settled, and F2 to F11 with it. Nothing of the fixes, the five texts,
the kept run or the merge blocks: G1 is to fix (it can come with the
commit of documents before the merge), G2 to G8 are notes.

Verdict: SIGNED (pass 2) of 1e24e3c, on the condition that the twelve
gates of the merge (issue-29, catalog-2b, std-1, gen-1a, gen-2a, gen-3a,
read-1a, read-2a, real-2, real-3a, real-5a, real-5b) pass on clean clones of
`1e24e3c`, as the report's section "main merged in (1e24e3c)" will show.

## Pass 2, condition

Checked with the same rules (no model call, no file changed but this one).

1. The twelve gates of the merge. Each log
   docs/reports/catalog-2c.merged.<wp>.gate.log says "gate <wp> at commit
   1e24e3c7d349... (clean)", "GATE <wp>: PASS" and "clean clone gate <wp>:
   PASS", for issue-29, catalog-2b, std-1, gen-1a, gen-2a, gen-3a, read-1a,
   read-2a, real-2, real-3a, real-5a and real-5b; the unit tests are 1357
   passed, 36 deselected. The two gen-2a logs (`9d4b48f` and `1e24e3c`)
   differ, after the timings and the clone paths are masked, only in the
   commit, the test count (issue #29's tests) and the counts of the ASCII and
   copied-code checks (its files): the separation table is the same row for
   row, 0 vectors are drawn again, and the kits step is "-- PASS kits (189.2 s)".
   read-2a on `1e24e3c` checks `R-task-6e527ae6baab` ("PASS arm R, kept dry
   run"). The table in the report's section "main merged in (`1e24e3c`)"
   agrees with the logs. The condition is met.
2. G1. `git show 03f12fe` changes src/specfirst/score/pilot.py and
   tests/score/test_score_pilot.py only. The summary now counts each state
   apart in the rows both tables have and in the rows the build lacks, tells
   a gap of the catalog (`GAP_NOTE`) from a row the table decisions do not
   ask for, and `not_built` adds the rows of the key's list that it cannot
   build either. The tests hold the sentence for arm S, arm R and the reader
   without the output; their numbers are those I counted in pass 2 (arm S
   0 of 15 shared and 12 outside: 3 explained, 9 open; arm R 5 of 15 and 12
   outside: 9 open, 3 not asked for; the reader without the output 10 alone,
   5 joint, 12 outside). read-1a on a clean clone of `03f12fe`
   (docs/reports/catalog-2c.g1.read-1a.gate.log): "gate read-1a at commit
   03f12fe9... (clean)", 1357 passed, 36 deselected, all 14 checks PASS
   ("pilot tests" 4 passed), "GATE read-1a: PASS". Its arm S summary (line
   398): "Of the 15 cells of the rows both tables have, 0 differ ... 12 are
   in rows that arm S does not build: 3 explained by another value of one
   table decision, 9 for a variable the reference ADaM lacks, 0 in rows the
   catalog does not have, 0 in rows the table decisions do not ask for ...";
   line 401: "rows not built: RELATED, SERIOUS_RELATED, FATAL_RELATED". The
   reason given for re-running read-1a alone holds: pilot.py is read by
   read-1a's checks "pilot" and "pilot tests" and by unit tests that every
   gate runs; read-2a does not use it, and specfirst.gen.separate takes only
   `PILOT_FEATURES`, which 03f12fe leaves alone. G1 is settled.

G2 to G8 remain notes (docs/state/gen.md, "Left open by the review of
catalog-2c", and the report), as pass 2 classed them.

Verdict: SIGNED (pass 2, condition met) of 1e24e3c, with G1 settled in
03f12fe.
