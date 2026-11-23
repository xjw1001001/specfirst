# gen-2b The probes follow the decisions of a kit: report

Date: 2026-11-23. Branch: `track/gen`, from `main` `34bbc14`. The part
that the owner's answer of 2026-11-17 on finding G1 of the gen-2a review
booked before the gate of the full gen-2 (ADR-007, "The owner's answer on
decision 6"); the owner chose on 2026-11-23 that it be done now. Choices:
docs/decisions/ADR-023.md.

## Verdict

GATE_VERDICT

## What changed

- Order (section 6.4, S1 before S3). `kits._generate` draws the design,
  then the decision vector (`kits.draw_values`: the stream of the first
  vector of gen-2a; a vector differs only where gen-2a's sampler refused a
  draw that is now taken), then generates the data for that vector (`study.generate(..., values=...)`), then gold. A
  study of its own draws its vector from its seed (`study.own_values`); the
  gate gen-1a gives seed n the decisions of scenario n where the design
  can carry them (`gate.values_for`). `study.json` names the vector.
- The recipes follow the vector (`specfirst.gen.probes`):
  - `statistic_at_rounding_half`: the column of the placebo arm under the
    kit's analysis set, grouping, sources of treatment and decimals, found
    by the hand calculation (`probes.spared_column`); subjects of the arm
    added until its size is a multiple of 8, 16 or 32 (0, 1, 2 decimals);
    then the counts with a serious event and with any event set at a
    rounding half (`probes.is_rounding_half(count, total, decimals)`);
  - `no_exposure_end_date`: the subject completes its treatment where the
    analysis set asks for a post-baseline value or a later visit;
  - the window probes: built around the kit's own window
    (`Parameters.of_kit`);
  - `ae_with_each_causality_value`: serious events where the table shows
    serious related events and not related events;
  - the subject dosed off plan in a design with two arms: the placebo arm
    is the arm the table does not group by.
- `probes.REACHES` keeps the conditions of kind (a) only (ADR-023, decision
  4); the per-pair conditions and `_ANALYZED` are gone; `tfl.columns.arms`
  reads the new parameter `placebo_first`.
- `kits.generate` writes no kit in which a read decision that data could
  separate is unseparated, and draws no second vector (`MAX_ATTEMPTS` and
  `vectors_drawn_before` are gone). `decisions.fits` is gone: the owner
  lifted its three limits (ADR-023, decision 6), and three recipes follow
  them: a second subject of the partial start in the month of the first
  dose, whose first dose has no time; a treatment and a study disposition
  record for the subject without an exposure end date; a second such
  subject without a study-level disposition record (per recommendation,
  pending SME review).
- The gates gen-2a and gen-2b (one list of checks, `gates._gen2_checks`)
  plant the failure: `gate2.planted_unfit_build` (the generator refuses kit
  9 built with the probes of gen-2a) and `gate2.planted_unfollowed` (the
  twin of kit 9 made with them is unfit: the rounding rule and the source of
  the treatment end date applicable and unseparated).
- `present` decides the count probe again from the data under the logged
  vector; `present.planted_for` says what a twin's probes were made for (in
  the logs of the gates gen-1a and gen-2a/2b).
- `score.kit` reads the parameters of a kit from its log of probes.
- After the first pass of the review (docs/reports/gen-2b.review.md, NOT
  SIGNED on `29bc57a`, findings H1 to H7):
  - H1: a pair of two values of one alternative is claimed like a pair of
    two alternatives (`verify.claims`), so `ae.related.values` is
    applicable where the table shows a row of related events, and the gate
    can fail on it; planted: `gate2.planted_one_causality`; the coverage of
    the gate asks for a kit where an entry with one alternative is
    applicable and separated.
  - H2: the row of `pop.safety.rule` in `REACHES` stays, with its premise
    written down (a subject who is not randomized has no planned arm,
    SDTMIG v3.4 DM; per recommendation, pending SME review: ADR-023,
    decision 4); the reason of the matrix quotes the note of the row;
    `test_a_subject_without_a_randomization_has_no_planned_arm`.
  - H3: the subject with a partial first exposure date gets a value of the
    test before the month of its first dose where the efficacy-evaluable
    set asks for a baseline value; and the subject who misses the visits
    has a mild event, so that planted subjects that move the other way do
    not cancel it (a kit of the review).
  - H4, H6, H7: the documents say what the code does; the sweep shows its
    scripts (docs/reports/gen-2b.sweep.md); ADR-023 decision 7 says where
    the failure of the gate lives.
  - H5: a planted defect for every branch gen-2b added to `present`
    (`test_a_variant_of_gen_2b_that_is_undone_is_missed`, and the event of
    the subject who misses the visits in `F9`).
- `GENERATOR` is `gen-2b.2` (`gen-2b.1` before the review).

## Before any gate: the vectors, and a sweep of 54 kits

Scripts, commands and the full output: docs/reports/gen-2b.sweep.md.

The vectors of the ten kits of the gate seed (`lifted.py`, the vectors as
`kits.draw_values` draws them): kits 2, 3, 8 and 10 have emergence by the
time of the first dose with a partial start completed to a day (limit (a)
of gen-2a's sampler), kit 7 the treatment record as the end-of-study
record (limit (b)); kits 1, 4, 5, 6 and 9 none of the three. The stream of
the vector is gen-2a's, so these five are the vectors that changed.

The sweep, on `gen-2b.2` (the code of the commit after the review), 54
kits written without R by processes of their own, four at a time: the
twelve vectors the reviewer forced (the three lifted combinations; each
analysis set and grouping; 0, 1 and 2 decimals; windows of 7, 14 and 30
days and of the follow-up; the first exposure record; the code map; the
latest record end; the total over the active arms), kits 1 to 10 of the
seeds `review-g2b-sweep` and `sweep-a`, and all 22 kits 4 and 9 of the
reviewer's 100 sets whose table is on the efficacy-evaluable set by values
with the treatment start from DM.RFXSTDTC (the vector of finding H3, of
which seven of the first eight were not written on `29bc57a`).

```text
$ grep -c "written;" $SCRATCH/sweep.out; grep -c "NOT WRITTEN" $SCRATCH/sweep.out
54
0
$ grep -o "read, not applicable: .*" $SCRATCH/sweep.out | sort | uniq -c
      5 read, not applicable: [['ae.related.values', 'no_alternative']]
      8 read, not applicable: [['pop.safety.rule', 'unseparated'], ['ae.related.values', 'no_alternative']]
      2 read, not applicable: [['pop.safety.rule', 'unseparated'], ['pop.safety.grouping', 'unseparated']]
     25 read, not applicable: [['pop.safety.rule', 'unseparated']]
     14 read, not applicable: []
```

Every kit was written, and in every one "applicable and unseparated" is
empty. What is read and not applicable: `pop.safety.rule` in a table by
planned treatment and `pop.safety.grouping` with actual treatment the same
as planned (the rows of `REACHES`, the first on its premise: ADR-023,
decision 4), and `ae.related.values` where the scale allows one stated list
only (`no_alternative`). Before the fix of H1 the reviewer counted that
decision read, separated and not applicable in 11 of 21 kits; now it is
applicable wherever it has two lists. The kit of the review that still
failed after the fix of H3 (`review-g2b-rfx-40` kit 4, on
`pop.efficacy.rule`) is traced in the evidence file: two pairs of planted
subjects without events moved the other way in two arms; with the event of
the subject who misses the visits it is written.

## The natural form (two model calls, approved)

Lifting the limits changed the vectors of kits 2, 3, 7, 8 and 10, whose
documents state five statements without an accepted text (a script of the
executor, `natural.statements_of` against the store): emergence at or after
the date and time of the first dose (kits 2, 3, 8, 10); a window of 7 days
(kit 2); the efficacy set by the visit WEEK 2 (kit 2); the row list ANY,
SERIOUS, SERIOUS_RELATED, DOSE_MODIFIED, FATAL (kit 2); the end-of-study
record with the subcategory STUDY TREATMENT (kit 7). The owner approved up
to USD 1.3 and four calls (2026-11-23, through the base session). Two
calls, both accepted on the first attempt, on the ten kits written without
R into `/root/scratch-gen2b/kits`:

```text
$ specfirst gen natural requests --kits /root/scratch-gen2b/kits --out .../gen-2b-rewrite-1.request.json
.../gen-2b-rewrite-1.request.json: 5 paragraphs, 0 filler
$ specfirst gen natural propose .../gen-2b-rewrite-1.answer.json --kits /root/scratch-gen2b/kits --call gen-2b-rewrite-1 --request ... --tokens 53339 --tool-uses 2 --seconds 8 --message ...
11ee259f001c2bc5 tfl.ae.summary.rows: attempt 1: slots ok
5bbee3ec5e7ab09f disp.status.record: attempt 1: slots ok
d2f9a256648e4202 ae.teae.end: attempt 1: slots ok
d9de48b6b30d2725 pop.efficacy.rule: attempt 1: slots ok
fc84969c89c84bf4 ae.teae.start: attempt 1: slots ok
store .../src/specfirst/gen/rewrites: 92 statements, 87 accepted (0 by the phrasing template), 5 open; 10 of 10 filler paragraphs accepted; 8 calls, 469905 tokens
$ specfirst gen natural readback-requests --out .../gen-2b-readback-1.request.json
.../gen-2b-readback-1.request.json: 5 items, 0 filler
$ specfirst gen natural readback .../gen-2b-readback-1.answer.json --call gen-2b-readback-1 --request ... --tokens 54659 --tool-uses 2 --seconds 7 --message ...
11ee259f001c2bc5 tfl.ae.summary.rows: attempt 1: read back as stated_rows: ACCEPTED
5bbee3ec5e7ab09f disp.status.record: attempt 1: read back as disposition_event_by_subcategory: ACCEPTED
d2f9a256648e4202 ae.teae.end: attempt 1: read back as last_dose_plus_days: ACCEPTED
d9de48b6b30d2725 pop.efficacy.rule: attempt 1: read back as attended_visit: ACCEPTED
fc84969c89c84bf4 ae.teae.start: attempt 1: read back as at_or_after_first_dose_time: ACCEPTED
store .../src/specfirst/gen/rewrites: 92 statements, 92 accepted (0 by the phrasing template), 0 open; 10 of 10 filler paragraphs accepted; 9 calls, 524564 tokens
the kits state 68 statements; without an accepted text: 0
```

The store grew by 5 lines of `paragraphs.jsonl` and 2 of `calls.jsonl`; no
line changed (`git diff --stat`: 7 insertions, 0 deletions). The final
messages were written with LF.

GATES_AND_EVIDENCE

## Model use and spend

| Call | Role | Model | Items | Tokens | Tool uses | Time | Result |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gen-2b-rewrite-1 | rewriter | Sonnet 5.5 subagent | 5 paragraphs | 53,339 | 2 | 7.6 s | 5 of 5 slots ok |
| gen-2b-readback-1 | verifier, a new fresh context | Sonnet 5.5 subagent | 5 items | 54,659 | 2 | 6.8 s | 5 of 5 accepted |

The subagent calls report tokens only, 107,998 in all; their USD is computed
as in docs/reports/catalog-2c.md ("Model use") from the list prices of
Sonnet 5.5: with the context written to the cache once and read twice,
107,998 x (2.50 + 2 x 0.10) / 1e6 = USD 0.29; without any cache,
107,998 x 3 x 2 / 1e6 = USD 0.65. Approved: up to USD 1.3 and four calls.

DRYRUN_SPEND
