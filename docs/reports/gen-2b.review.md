# gen-2b: independent review (rule R7)

Reviewer: a fresh-context agent that did not write the work (PLAN.md
section 2.2, rule R7: correctness only, no style). Date: 2026-11-23.

Commit reviewed: `29bc57a` on `track/gen`, the diff `34bbc14..29bc57a`.
The worktree's `src/` and `tests/` are those of `29bc57a`; the report
`docs/reports/gen-2b.md` is an uncommitted draft whose gate section is not
yet filled (it still holds the placeholders `GATE_VERDICT`,
`GATES_AND_EVIDENCE` and `DRYRUN_SPEND`).

Result: NOT SIGNED. Three findings block (H1, H2, H3); four do not
(H4 to H7).

## How I reviewed

Read, in this order: PLAN.md sections 2.2, 2.3, 4.6, 4.7, 6.4, 6.5 and
13.5; docs/decisions/ADR-007.md in full; finding G1 of
docs/reports/gen-2a.review.md and "What settles G1"; ADR-023 in full; the
draft docs/reports/gen-2b.md and the gate log next to it,
docs/reports/gen-2b.gen-2b.gate.log (uncommitted); docs/state/gen.md;
docs/lessons.md, lessons 43, 44, 47, 74, 75 and 76; CLAUDE.md.

The code: the whole diff; `specfirst.gen.probes` in full (REACHES, holds,
Parameters.of and of_kit, Planter, every recipe, is_rounding_half,
spared_column, _rounding_half, log); `verify.mutate` and `verify.options`;
`kits` (draw_values, unfollowed, _generate, _attempt, check, main);
`gate2` (kits_check, planted_unfit_build, separation_check,
planted_separation, planted_unfollowed); `decisions`, `study`, `present`,
`gate` (values_for, OWN_DATA); `score.kit`; and in
`specfirst.gen.reference` the populations, the treatments and the table,
which the claims of REACHES are about. In the catalog: the entries of the
slice that REACHES names and the templates `pop.safety.rule.yaml`,
`pop.randomized.rule.yaml` and `tfl.columns.total.yaml` of
`standard/catalog@2`.

What I ran. Python only under WSL after `. scripts/env.sh`; every kit
build and generator run inside `flock /run/lock/specfirst-heavy.lock
taskset -c 0-3`; scripts and kits under /root/scratch-review-gen2b (the
kits deleted at the end). Four jobs:

- E1 (job1.sh): kit 6 of the gate seed written without R
  (`kits.generate_apart(root, kits.kit_seed("gen-2a", 6), out,
  kits.split_of(6), with_r=False, number=6)`), then two twins changed in
  one way each and mutated with the kit's own decision records by
  `verify.mutate`, as the gate's planted defects do (exp_variants.py).
- E2 (job2.sh): 22 kits written without R by processes of their own,
  four at a time (one_kit.py, which calls `kits.generate(...,
  with_r=False, number=n)`): 12 with some decisions forced on top of the
  vector `kits.draw_values` draws (the three lifted combinations; the
  safety set by actual and by planned treatment, the randomized set with
  and without a post-baseline value, the efficacy-evaluable set by visit
  and by values; 0, 1 and 2 decimals; the follow-up window; the first
  exposure record; the code map; the latest record end; the total over
  the active arms), and kits 1 to 10 of a seed of mine,
  `review-g2b-sweep`, drawn as the generator draws them.
- E3 (job3.sh): the kit that E2 could not write, explained by the hand
  calculation (exp_refused.py); variant C of E1 again on a subject outside
  the counted column (exp_c2.py); how often the sampler draws a part of
  that kit's vector, and four drawn kits of such seeds.
- E4 (job4.sh): how often the sampler draws the vector that matters for
  H3, and drawn kits of such seeds written without R.

I ran no gate, no test suite and not the dry run of arm R, made no model
call, and changed no file but this one.

## What I ran, with output

### 1. The diff, and the gate log that exists

```text
$ git diff --stat 34bbc14..29bc57a | tail -1
 28 files changed, 1799 insertions(+), 557 deletions(-)
$ git diff --quiet 29bc57a -- src tests && echo "src/tests same as 29bc57a"
src/tests same as 29bc57a
$ head -1 docs/reports/gen-2b.gen-2b.gate.log; tail -1 docs/reports/gen-2b.gen-2b.gate.log
gate gen-2b at commit 29bc57afed8ecd6b784fac3e623ae6f2493e4ffc (clean)
GATE gen-2b: PASS
$ grep -n "ae.related.values  \|pop.safety.rule  " docs/reports/gen-2b.gen-2b.gate.log
302:pop.safety.rule           10    6    2    2  at_least_one_dose|randomized_and_dosed: 1,10
309:ae.related.values         10    9    0    7  one alternative; kits that separate values of its slot: 2,3,4,5,6,8,10
(the matrix of the ten kits; columns: in, read, applicable, separated)
$ grep -n 'claimed = one\["rule"\]' src/specfirst/gen/verify.py
308:            claimed = one["rule"] != two["rule"] and entry.id in reach_tables and probes.reaches(
$ git show 34bbc14:src/specfirst/gen/verify.py | grep -n 'claimed = one\["rule"\]'
303:            claimed = one["rule"] != two["rule"] and entry.id in reach_tables and probes.reaches(
```

The clean-clone logs of the gates gen-1a, gen-2a and gen-3a on `29bc57a`
were written while I worked (build/gates/<wp>/clean-clone.log in the
worktree, not yet in the report):

```text
$ grep -n "^gate gen-.. at\|GATE gen-\|^CORE on" build/gates/gen-1a/clean-clone.log build/gates/gen-2a/clean-clone.log build/gates/gen-3a/clean-clone.log
build/gates/gen-1a/clean-clone.log:53:gate gen-1a at commit 29bc57afed8ecd6b784fac3e623ae6f2493e4ffc (clean)
build/gates/gen-1a/clean-clone.log:149:CORE on 20 datasets (10 seeds, visible and twin): no unexplained finding; the pinned source is unchanged
build/gates/gen-1a/clean-clone.log:199:GATE gen-1a: PASS
build/gates/gen-2a/clean-clone.log:53:gate gen-2a at commit 29bc57afed8ecd6b784fac3e623ae6f2493e4ffc (clean)
build/gates/gen-2a/clean-clone.log:426:GATE gen-2a: PASS
build/gates/gen-3a/clean-clone.log:53:gate gen-3a at commit 29bc57afed8ecd6b784fac3e623ae6f2493e4ffc (clean)
build/gates/gen-3a/clean-clone.log:296:GATE gen-3a: PASS
```

### 2. E1: kit 6 of the gate seed, and two changed twins

```text
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 /root/scratch-review-gen2b/job1.sh
kit 6 of the gate seed written without R: 126 files
seconds: 45
kit gate-kit-006: population {'rule': 'safety'}, grouping {'rule': 'planned'}, actual {'rule': 'dm_actarm'}, safety rule {'rule': 'randomized_and_dosed'}, rows {'rule': 'standard_rows'}, related {'rule': 'stated_list', 'values': ['POSSIBLE', 'PROBABLE']}
probes.reaches(ae.related.values) on the kit's vector: True
probes.reaches(pop.safety.rule) on the kit's vector: False
== the kit as written (gold/identifiability.json)
  pop.safety.rule: read=True applicable=False identifiable=unseparated gold=randomized_and_dosed
    pair randomized_and_dosed | at_least_one_dose: separated=False claimed=False cells=0
    reason: the output reads it, but under the other decisions of the kit its alternatives give the same output on any data (probes.REACHES): the same output under at_least_one_dose
  ae.related.values: read=True applicable=False identifiable=separated gold=stated_list(values=['POSSIBLE', 'PROBABLE'])
    pair stated_list(values=['POSSIBLE', 'PROBABLE']) | stated_list(values=['REMOTE', 'POSSIBLE', 'PROBABLE']): separated=True claimed=False cells=6
    pair stated_list(values=['POSSIBLE', 'PROBABLE']) | stated_list(values=['PROBABLE']): separated=True claimed=False cells=5
    pair stated_list(values=['REMOTE', 'POSSIBLE', 'PROBABLE']) | stated_list(values=['PROBABLE']): separated=True claimed=False cells=6
  summary: applicable_and_unseparated=[] unseparated_read=['pop.safety.rule']
== variant B-related: AEREL = 'PROBABLE' on all 233 AE rows
  ae.related.values: read=True applicable=False identifiable=unseparated gold=stated_list(values=['POSSIBLE', 'PROBABLE'])
    pair stated_list(values=['POSSIBLE', 'PROBABLE']) | stated_list(values=['REMOTE', 'POSSIBLE', 'PROBABLE']): separated=False claimed=False cells=0
    pair stated_list(values=['POSSIBLE', 'PROBABLE']) | stated_list(values=['PROBABLE']): separated=False claimed=False cells=0
    pair stated_list(values=['REMOTE', 'POSSIBLE', 'PROBABLE']) | stated_list(values=['PROBABLE']): separated=False claimed=False cells=0
    reason: the output reads it, but under the other decisions of the kit its alternatives give the same output on any data (probes.REACHES): the same output under stated_list(values=['REMOTE', 'POSSIBLE', 'PROBA
  summary: applicable_and_unseparated=[] unseparated_read=['ae.related.values', 'pop.safety.rule']
  defects (0): []
  unfit (0): []
  the generator would WRITE this kit
== variant C-unrandomized: SFPHBKTR-101-001 (ARMCD PBO, ARM 'Placebo', dosed) without its DS record RANDOMIZED (279 -> 278 DS rows)
  pop.safety.rule: read=True applicable=False identifiable=separated gold=randomized_and_dosed
    pair randomized_and_dosed | at_least_one_dose: separated=True claimed=False cells=4
  summary: applicable_and_unseparated=['tfl.rounding.rule'] unseparated_read=['tfl.rounding.rule']
  defects (0): []
  unfit (1): ['tfl.rounding.rule: half_even and half_away_from_zero can differ in the output under these decisions (the log of probes claims it); the two builds on the twin are the same']
  the generator would REFUSE this kit
seconds: 86
```

Variant C took its subject from the counted column (placebo), so the
column lost its rounding half as well; E3 repeats it outside that column.

### 3. E2: 22 kits without R (one line per kit; `summarize.py` on job2.jsonl)

```text
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 /root/scratch-review-gen2b/job2.sh   (seconds: 207)
$ python /root/scratch-review-gen2b/summarize.py /root/scratch-review-gen2b/job2.jsonl
lift-a-efficacy-0dec (number 4): written; 16 separated, 18 read, 16 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated'], ['ae.related.values', 'no_alternative']]
lift-b-efficacy-followup (number 9): NOT WRITTEN: study SFGXXY52: the twin does not separate 1 pairs of alternatives that the output reads and that no other decision makes equal: trt.date.imputation: first_day_of_month and not_completed can differ in the output under these decisions (the log of probes claims it); the two builds on the twin are the same (decisions: trt.date.imputation)
lift-a-notbefore-rand-2dec (number 2): written; 16 separated, 16 read, 15 applicable; applicable+unseparated none; read, not applicable: [['ae.related.values', 'separated']]
lift-b-safety-planned-2dec (number 6): written; 17 separated, 18 read, 16 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated'], ['ae.related.values', 'separated']]
lift-c-firstex-0dec (number 2): written; 17 separated, 17 read, 17 applicable; applicable+unseparated none; read, not applicable: []
lift-c-randomized-post (number 8): written; 17 separated, 17 read, 16 applicable; applicable+unseparated none; read, not applicable: [['ae.related.values', 'separated']]
lift-c-efficacy-visit (number 4): written; 16 separated, 17 read, 16 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated']]
firstex-2dec-protocol (number 6): written; 15 separated, 15 read, 15 applicable; applicable+unseparated none; read, not applicable: []
planned-same-0dec-related (number 1): written; 15 separated, 17 read, 14 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated'], ['pop.safety.grouping', 'unseparated'], ['ae.related.values', 'separated']]
armcd-map-recordend-serrel (number 2): written; 16 separated, 16 read, 15 applicable; applicable+unseparated none; read, not applicable: [['ae.related.values', 'separated']]
laststart-bytime-2dec-actual (number 10): written; 16 separated, 16 read, 16 applicable; applicable+unseparated none; read, not applicable: []
efficacy-values-active-total (number 4): written; 16 separated, 17 read, 15 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated'], ['ae.related.values', 'separated']]
drawn (review-g2b-sweep/kit-1, number 1): written; 16 separated, 16 read, 15 applicable; ...; read, not applicable: [['ae.related.values', 'separated']]
drawn (review-g2b-sweep/kit-2, number 2): written; 16 separated, 16 read, 15 applicable; ...; read, not applicable: [['ae.related.values', 'separated']]
drawn (review-g2b-sweep/kit-3, number 3): written; 17 separated, 17 read, 16 applicable; ...; read, not applicable: [['ae.related.values', 'separated']]
drawn (review-g2b-sweep/kit-4, number 4): written; 16 separated, 17 read, 15 applicable; ...; read, not applicable: [['pop.safety.rule', 'unseparated'], ['ae.related.values', 'separated']]
drawn (review-g2b-sweep/kit-5, number 5): written; 14 separated, 15 read, 14 applicable; ...; read, not applicable: [['ae.related.values', 'no_alternative']]
drawn (review-g2b-sweep/kit-6, number 6): written; 14 separated, 15 read, 14 applicable; ...; read, not applicable: [['pop.safety.rule', 'unseparated']]
drawn (review-g2b-sweep/kit-7, number 7): written; 16 separated, 17 read, 16 applicable; ...; read, not applicable: [['ae.related.values', 'no_alternative']]
drawn (review-g2b-sweep/kit-8, number 8): written; 14 separated, 15 read, 14 applicable; ...; read, not applicable: [['ae.related.values', 'no_alternative']]
drawn (review-g2b-sweep/kit-9, number 9): written; 15 separated, 16 read, 15 applicable; ...; read, not applicable: [['pop.safety.rule', 'unseparated']]
drawn (review-g2b-sweep/kit-10, number 10): written; 17 separated, 17 read, 16 applicable; ...; read, not applicable: [['ae.related.values', 'separated']]
```

Every kit the script wrote has "applicable+unseparated none"; `...` stands
for that phrase. What the probes of each were planted for (the line
`present.planted_for` prints) covers: columns 'Placebo' and 'PLACEBO' (the
first exposure record) of 16 to 64 subjects with 0 to 16 added; 0, 1 and 2
decimals; windows of 7, 14 and 30 days; the subject without an exposure
end date completing or stopping early, with a treatment and a study
record, or with a second subject without a study-level record; a partial
event in the month of a first dose without a time; serious causality
events where only serious related events are shown.

### 4. E3: the refused kit, variant C2, the sampler

```text
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 /root/scratch-review-gen2b/job3.sh
### refused kit
lift-b-efficacy-followup: efficacy rule {'rule': 'baseline_and_postbaseline', 'test': 'SYSBP'}, imputation {'rule': 'first_day_of_month'}, start {'rule': 'dm_rfxstdtc'}, window {'rule': 'last_dose_plus_days', 'days': 14}, rows standard_rows
-- trt.date.imputation = first_day_of_month
  partial_exposure_date_not_earliest SFGXXY52-105-009: start 2021-05-02, safety True, efficacy True, planned Low Dose, events []
  partial_exposure_date SFGXXY52-105-035: start 2021-07-01, safety True, efficacy False, planned High Dose, events [(datetime.date(2021, 7, 24), True)]
     EX [('2021-07', '2021-07-25', 10.0), ('2021-07-26', '2021-08-06', 10.0), ...]; VS of the test [('SYSBP', '2021-07-10'), ('SYSBP', '2021-07-23'), ('SYSBP', '2021-08-07'), ('SYSBP', '2021-08-17')]
  table header ['(N=32)', '(N=44)', '(N=39)']; ANY {'Placebo': 26, 'High Dose': 37, 'Low Dose': 27}
-- trt.date.imputation = not_completed
  partial_exposure_date_not_earliest SFGXXY52-105-009: start 2021-05-02, safety True, efficacy True, planned Low Dose, events []
  partial_exposure_date SFGXXY52-105-035: start None, safety False, efficacy False, planned High Dose, events [(datetime.date(2021, 7, 24), False)]
  table header ['(N=32)', '(N=44)', '(N=39)']; ANY {'Placebo': 26, 'High Dose': 37, 'Low Dose': 27}
### variant C2
== variant C2: SFPHBKTR-101-004 (ARMCD SFX100, ARM 'SFX-820 100 mg once daily', dosed; the counted column is the arm PBO) without its DS record RANDOMIZED (279 -> 278 DS rows)
  pop.safety.rule: read=True applicable=False randomized_and_dosed | at_least_one_dose: separated=True claimed=False cells=3
  summary: separated 17, applicable_and_unseparated=[], unseparated_read=[]
  defects (0): []
  unfit (0): []
### sampler
kits on the efficacy set (numbers 4 and 9 of 30 sets): 60; with baseline and post-baseline values and completion to the first day of the month: 13
### drawn kits of the first four hits
drawn (review-g2b-eff-6/kit-9, number 9): written; ...   (start first_ex_with_dose)
drawn (review-g2b-eff-14/kit-9, number 9): written; ...  (start first_ex_with_dose)
drawn (review-g2b-eff-14/kit-4, number 4): written; ...  (start first_ex_with_dose)
drawn (review-g2b-eff-11/kit-4, number 4): written; ...  (start first_ex_with_dose)
seconds: 65
```

The four drawn kits with the efficacy set by values and the completion to
the first day of the month were written: their treatment start comes from
the exposure records. What matters is the start from DM.RFXSTDTC (H3); E4
counts that.

### 5. E4: the vector of H3, as the sampler draws it

```text
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 /root/scratch-review-gen2b/job4.sh
kits on the efficacy set (numbers 4 and 9 of 100 sets): 200; with baseline and post-baseline values and the treatment start from DM.RFXSTDTC: 22
HIT review-g2b-rfx-3/kit-4 4 first_day_of_month
HIT review-g2b-rfx-5/kit-4 4 not_completed
HIT review-g2b-rfx-14/kit-9 9 not_completed
HIT review-g2b-rfx-17/kit-4 4 not_completed
HIT review-g2b-rfx-22/kit-9 9 not_completed
HIT review-g2b-rfx-27/kit-4 4 first_day_of_month
HIT review-g2b-rfx-40/kit-4 4 not_completed
HIT review-g2b-rfx-48/kit-9 9 not_completed
(14 more HIT lines)
drawn (review-g2b-rfx-14/kit-9, number 9): written; 15 separated, 16 read, 15 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated']]
drawn (review-g2b-rfx-3/kit-4, number 4): NOT WRITTEN: study SFMVNGW5: the twin does not separate 1 pairs of alternatives that the output reads and that no other decision makes equal: trt.date.imputation: first_day_of_month and not_completed can differ in the output under these decisions (the log of probes claims it); the two builds on the twin are the same (decisions: trt.date.imputation)
drawn (review-g2b-rfx-17/kit-4, number 4): NOT WRITTEN: study SFKUZX6U: ... trt.date.imputation: not_completed and first_day_of_month ... (decisions: trt.date.imputation)
drawn (review-g2b-rfx-5/kit-4, number 4): NOT WRITTEN: study SFWK5T8B: ... trt.date.imputation: not_completed and first_day_of_month ... (decisions: trt.date.imputation)
drawn (review-g2b-rfx-22/kit-9, number 9): NOT WRITTEN: study SFDGLPXP: ... trt.date.imputation: not_completed and first_day_of_month ... (decisions: trt.date.imputation)
drawn (review-g2b-rfx-27/kit-4, number 4): NOT WRITTEN: study SFZSGLD3: ... trt.date.imputation: first_day_of_month and not_completed ... (decisions: trt.date.imputation)
drawn (review-g2b-rfx-40/kit-4, number 4): NOT WRITTEN: study SFNXLECR: the twin does not separate 2 pairs of alternatives that the output reads and that no other decision makes equal: trt.date.imputation: not_completed and first_day_of_month can differ in the output under these decisions (the log of probes claims it); the two builds on the twin are the same; pop.efficacy.rule: baseline_and_postbaseline and attended_visit can differ in the output under these decisions (the log of probes claims it); the two builds on the twin are the same (decisions: pop.efficacy.rule, trt.date.imputation)
drawn (review-g2b-rfx-48/kit-9, number 9): NOT WRITTEN: study SF5Z9ZPT: ... trt.date.imputation: not_completed and first_day_of_month ... (decisions: trt.date.imputation)
seconds: 86
```

(`...` cuts the sentence that every refusal repeats.) Nothing was forced
here: these are kits 4 and 9 of sets of seeds of mine, drawn as the
generator draws them. Of the eight, seven were not written.

## Findings

### H1. BLOCKS: `ae.related.values` is never applicable, so the gate cannot fail on it

The owner's demand (ADR-007, "The owner's answer on decision 6", point 2):
the gate fails on a kit in which a decision that the output reads, and
that data could separate, is not separated on the twin. ADR-023, decision
4, lists `ae.related.values` as claimed when "the table shows a row of
related events", and decision 2 changed the causality probe (serious
events where only serious related events are shown) so that the twin
separates it.

The code never claims it. `verify.mutate` claims a pair only when its two
values have different rules (verify.py line 308, unchanged from line 303
of `34bbc14`). `ae.related.values` has one alternative, `stated_list`;
`verify.options` changes it between values of its slot, so every pair has
one rule, `claimed` is False, `applicable` (claimed for every pair of the
gold value) is never true, and an unseparated pair never makes a kit
`unfit`. Such a kit is written, and its matrix gives the decision the
reason `verify.NO_PROBE`: "under the other decisions of the kit its
alternatives give the same output on any data".

- The gate log of gen-2b: `ae.related.values 10 9 0 7`: read in 9 kits,
  applicable in none.
- E1, kit 6: `probes.reaches` holds for it; its three pairs are
  separated (5 and 6 cells) and none is claimed.
- E1, variant B: a twin of that kit on which the stated lists give one
  table (every AEREL the last value of the scale): unseparated, unfit
  empty, "the generator would WRITE this kit", with the reason "equal on
  any data" for a decision that the honest twin separates in 6 cells.
- E2: read, with two or more stated lists, and not applicable in 11 of
  the 21 kits written (separated in all 11; in 4 more the scale gives one
  list: `no_alternative`).

So for this decision the clause "a decision that the output reads and
that data could separate is separated in every kit" (docs/state/gen.md)
holds by luck of the data, not by the gate: lesson 47 again, for one
decision. In every kit I saw with two or more stated lists it was
separated; the gate would not have failed if it had not been.

What settles it: a pair of two values of an entry with one alternative is
claimed when its REACHES condition holds (or: claimed unless the two
values are equal), so that `applicable` and `unfit` cover it; variant B
planted (a twin whose causality values cannot tell the lists apart must
make the kit unfit); the docs follow. The matrix bytes change: a new
`GENERATOR` and the gates again.

### H2. BLOCKS: the row of `pop.safety.rule` in REACHES is not of kind (a): data separate the two rules in a table by planned treatment

REACHES claims `pop.safety.rule` only for a table on the safety set
grouped by actual treatment from DM.ACTARM or the first exposure record.
The reason given (ADR-023 decision 4, the note in REACHES, verify's
reason): "the subject dosed without being randomized has no planned
treatment". That is a property of the planted subject, not of any data.
By the fixed rule `randomized_subject` of `pop.randomized.rule`, a subject
is randomized when it has a disposition record RANDOMIZED (when any
subject of the study has one, as in every generated study:
`reference._populations`, the template `pop.safety.rule.yaml` reads
RANDFL); planned treatment comes from DM.ARM or DM.ARMCD. A dosed subject
with a planned arm and no record RANDOMIZED is not randomized and has a
planned treatment: in the safety set under `at_least_one_dose`, not under
`randomized_and_dosed`, and it stands in its planned column. The same holds
on the efficacy-evaluable set (it is a part of the safety set) and where
actual treatment is the same as planned.

- E1, kit 6 of the gate seed (safety set by planned treatment): the kit
  as written says `pop.safety.rule` is unseparated, "the same output on
  any data".
- E3, variant C2: one subject of the base process of an active arm, dosed,
  loses its record RANDOMIZED and keeps DM.ARM. `pop.safety.rule` is
  separated (3 cells); nothing else changes (17 separated, no read
  decision unseparated); no defect, so the machine and the hand
  calculation agree on that twin.
- The gate set: the matrix gives this reason for `pop.safety.rule` in
  kits 4, 6, 7 and 9; in 8 of my 21 written kits; in 8 of the 20 kits of
  the executor's sweep.

G1 of the gen-2a review counted this case as kind (a), and the owner's
answer refers to the kinds of G1. But the answer, as ADR-007 records it,
keeps "only the conditions under which another decision of the kit makes
the alternatives equal on any data", and ADR-023 calls every row "a case
where no data could separate the alternatives"; the evidence shows data
that do. Which reading stands
is the owner's (lesson 47: a word of a gate text filled in by a table the
work writes).

What settles it, one of two: a probe for the rule under a grouping by
planned treatment (a dosed subject with a planned arm and no record
RANDOMIZED, with CORE run on it), and the row reduced to "the table reads
the safety set" (the safety or the efficacy-evaluable set; on the
randomized set the output does not read SAFFL, and a claim there is a
defect of `verify.mutate`); or the owner keeps the row as it is, knowing
this, and then ADR-023, the state file and the reason `verify.NO_PROBE`
stop calling it "equal on any data" for this row, and the scorer is told.

### H3. BLOCKS: a vector that the sampler draws gives no kit: the subject with a partial first exposure date is outside the efficacy-evaluable set under both completions

E2 could not write the kit `lift-b-efficacy-followup` (number 9): the
twin does not separate `trt.date.imputation`. E3 shows why, by the hand
calculation. Its decisions: the efficacy-evaluable set by a baseline and
a post-baseline value of SYSBP; the treatment start from DM.RFXSTDTC;
partial dates completed to the first day of the month. The subject of the
probe `partial_exposure_date` has DM.RFXSTDTC "2021-07" and its SYSBP
values from 2021-07-10 on. Completed to the first day of the month its
treatment starts on 2021-07-01, before any value of the test: no
baseline, not in the set. Not completed, it has no treatment start: not
in the safety set. Outside the set both ways, its event changes nothing;
the second probe of the decision (`partial_exposure_date_not_earliest`)
has a complete first date and is the same under both. Data could separate
the pair (the same subject with a value of the test before the first day
of the month). The forced window and end-of-study record of that kit play
no part.

ADR-023 decision 2 and the report: "Every other planted subject that
carries an event of a probe of a decision of the table completes the
study already", which is why the condition `_ANALYZED` could go.
Completing is not being in the set here.

It is not a corner that forcing made. E4: the sampler draws the
efficacy-evaluable set by values with the treatment start from
DM.RFXSTDTC in 22 of 200 kits on that set (kits 4 and 9 of 100 sets), and
of the first eight such kits, drawn and not forced, seven were not
written; one of them (`review-g2b-rfx-40`) also left `pop.efficacy.rule`
unseparated, which I did not trace further. With two kits on that set in
every set of ten, that is roughly one set in five that the generator
cannot write. With no second vector (decision 5) such a seed gives no
kit, and `generate_set` stops on it. It fails closed: no kit passes the
gate wrongly. But the probes of these kits do not follow their decisions,
which is what the part says it does; the gate seed happens not to meet
it; and a set of dev, test or sealed kits of a new seed will often fail
to be written.

What settles it: the recipes plant their subjects inside the analysis
set under every value of the decisions their events separate (here: a
value of the test of the efficacy rule dated before the first day of the
month of the first dose; and the cause of `pop.efficacy.rule` in
`review-g2b-rfx-40`), and a sweep that crosses the start source, the
completion, the analysis set and the efficacy rule writes every kit; or
the owner accepts such refusals, and ADR-023 says so with their rate.

### H4. Does not block: what the documents say and the code does not do

1. docs/state/gen.md, "What a scorer must know": "`disp.status.record` is
   never 'the record with the subcategory STUDY TREATMENT' in a gold
   vector, and 'STUDY PARTICIPATION' only where the output does not read
   the decision". Since ADR-023 decision 6 both occur where the output
   reads it (gate kit 7: a treatment and a study record; my kits
   `lift-b-safety-planned-2dec` and the three `lift-c-*`, written, the
   decision read and separated).
2. docs/state/gen.md: "applicable (read, and no other decision of the kit
   makes its alternatives give the same output on any data ...)", "Read,
   and equal by another decision on any data: `pop.safety.rule` ..." and
   "A decision that the output reads and that data could separate is
   separated in every kit". Not for `ae.related.values` (H1) and
   `pop.safety.rule` (H2). The same in ADR-007's new section, CLAUDE.md
   ("names only decisions that make two alternatives equal on any data")
   and the reason `verify.NO_PROBE`.
3. ADR-023 decision 4 ("every row list a study can state shows them") and
   decision 6 ("Every row list the catalog lets a study state shows the
   rows ANY and FATAL"). The catalog's slot `rows` takes any list of its
   eight codes, and two of its own examples, `[ANY]` and `[SERIOUS,
   RELATED, ANY]`, lack FATAL. What holds is that the six lists of
   `decisions.slot_values` hold both (the test
   `test_every_row_list_shows_what_the_probes_of_one_event_need` checks
   those). REACHES then claims `tfl.percent.format` and the decisions of
   one planted event for every list, which is right (data could separate
   them); a vector with another list would be refused, not passed.
4. The report: "none left a read decision that data could separate
   unseparated", and its sweep labels `pop.safety.rule` "(kind a)" (H2).

### H5. Does not block: new branches of a checker without a planted defect (rule R5)

`present._no_end_date` got three new ways to fail: disposition events of
other subcategories than the log names; the event after the window that
follows the study record as well (the treatment record as the
end-of-study record); and the second subject with a treatment record
only. `present._partial_ae_in_month` got "the first dose has a time, and
the log says it has none". No test and no gate plants any of them
(`grep -rn "says it has none\|study record as well" tests/
src/specfirst/gen/gate.py` prints nothing and exits 1; the plants for
these two probes in `tests/unit/test_gen_probes.py`, `_undo_no_end`,
`_undo_partial_ae` and four of `F9`, change EX and AE rows of the first
subject of the probe: none changes its disposition records, touches a
second subject, or gives a first dose without a time one). They do not
decide separation (the mutation does), but the gate gen-1a counts these
probes as "found in the data" by them.

### H6. Does not block: the report (draft) and rule R8

- The two pieces of evidence before any gate (the vectors as before and
  now; the sweep of 20 kits) come from "a script of the executor, not
  kept": the output is shown, the command is not. They are the only
  evidence beyond the gate set; show the script in the report or keep it.
- The gate section is empty. See "What I could not see".

### H7. Does not block: where the gate's failure lives

The per-kit loop of `gate2.separation_check` reads the matrices of the
written kits. A kit with an applicable and unseparated decision is never
written (`kits._generate` raises on `unfit`), so on kits of the generator
that loop cannot fail: true by construction. The gate fails instead in
its check "kits": a kit that is not written fails `kits_check`, planted by
`planted_unfit_build` (kit 9 with the probes of gen-2a, refused, naming
`tfl.rounding.rule` and `trt.end.source`; the real case of G1 for that
kit), and `kits.check` mutates every written kit again and fails on a
stored matrix that is not the new one. `planted_unfollowed` shows that the
function the loop uses names such decisions, on a matrix the loop never
reads. That is sound; the report and ADR-023 decision 7 should say that
the failure is carried by the check "kits". Also: nothing compares the
vector that `study.json` and the count probe's log line name with
`gold/decisions.jsonl`; `present` decides the count probe under the
logged vector. The mutation is what decides separation, so this is a
note, not a defect.

## The questions of the brief

1. Every row of REACHES, argued against the templates and the hand
   calculation: `trt.planned.source` (a table by actual treatment from
   DM.ACTARM or EX reads no TRT01P; RANDFL's fallback reads ARMCD, not
   TRT01P), `trt.actual.source` (only a table by actual treatment reads
   TRT01A; SAFFL reads TRTSDT), `trt.end.source` (only a window reads
   TRTEDT), `date.studyday.origin` (no row reads a study day),
   `pop.randomized.rule` (only the randomized set reads ITTFL; SAFFL reads
   RANDFL), `pop.safety.grouping` (with actual the same as planned TRT01A
   is TRT01P), `pop.efficacy.rule`, `disp.status.record` (the end-of-study
   record reaches the table only as the date that stands in for a missing
   exposure end date, through a window; no row reads EOSDT or EOSSTT) and
   `ae.related.values` (only a row of related events reads the causality)
   are of kind (a). `tfl.columns.arms` is of kind (a) given the design: in
   PG-FIX the active arms are doses of one drug, EX names it alike, so by
   the first exposure record they share one column, and with placebo
   listed first the two orders are one; the condition reads the design
   (`placebo_first`), which no twin can change. `pop.safety.rule` is not of
   kind (a) (H2). Read decisions that data could separate and that the
   gate does not ask for: `pop.safety.rule` (H2) and `ae.related.values`
   (H1).
2. The probes follow the decisions in every vector I tried but one: the
   counted column at 0, 1 and 2 decimals on every analysis set and
   grouping, by the first exposure record with added subjects, the window
   of the follow-up (7 and 14 days), the three lifted combinations on the
   safety, randomized and efficacy-evaluable sets: 21 of 22 kits written,
   none with an applicable decision unseparated. The exception, H3: a
   table on the efficacy-evaluable set by values with the treatment start
   from DM.RFXSTDTC; then 7 of 8 drawn kits are not written (E4).
3. The gate fails on a kit with an applicable decision unseparated,
   through the check "kits" (H7); `planted_unfit_build` and
   `planted_unfollowed` are the real case for kit 9 (the two decisions of
   G1, built with gen-2a's probes; the honest kit separates both). It
   does not fail for the decisions of H1 and H2.
4. True by construction: the gate on `ae.related.values` (H1); the row of
   `pop.safety.rule`, whose claim rests on the generator's own probe (H2);
   the per-kit loop of the check "separation" (H7, with the failure
   carried elsewhere).
5. Determinism: the gen-2b log has "P1: ... 0 differ" for all ten kits,
   each written twice by two processes; so has the clean clone of gen-2a;
   gen-1a's "identical hashes" passed on its clean clone. `GENERATOR`
   moved to `gen-2b.1` in the commit that changed the bytes. I did not
   build my own kits twice.
6. The report shows output without the command for its sweep (H6); the
   gate sections are not yet written; the state file and the ADRs say
   things the code does not do (H4).

## What I could not see

- The report's gate section (placeholders) and the gate logs it will
  name. I read the log of the gate gen-2b on a clean clone of `29bc57a`
  (PASS) and, written while I worked, the clean-clone logs of gen-1a,
  gen-2a and gen-3a on `29bc57a` in build/gates/<wp>/clean-clone.log (each
  "GATE <wp>: PASS"; CORE in gen-1a: "no unexplained finding" on the 20
  datasets, which include the subject without a study-level disposition
  record and the first dose without a time). Not seen: read-1a on
  `29bc57a` (running when I finished; the log on disk is of `901be3d`) and
  issue-29 (no log yet).
- read-2a: the kept dry run of arm R is to be made again by the owner
  (ADR-017, ADR-023); I did not run it or the gate read-2a.
- My own kits were written without R; the agreement of the engines on
  them is not checked.

## Verdict

Verdict: NOT SIGNED

H1, H2 and H3 block. H1 and H2 are the owner's condition for this part
("the gate fails on a kit in which a decision that the output reads, and
that data could separate, is not separated on the twin"; REACHES keeps
only conditions that make the alternatives equal on any data); H3 is its
other half ("the planted subjects inside its analysis set"). The dry run
of arm R is not yet made, so a change of the generator now costs no
second dry run. After the fixes (or the owner's word on H2 and H3) I
would read the diff, the new logs and the report again.
