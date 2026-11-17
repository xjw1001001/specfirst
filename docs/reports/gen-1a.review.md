# Review of the part gen-1a: SDTM generator for PG-FIX, slice "adverse event summary first"

Rule R7 of PLAN.md: a fresh-context agent that did not write the work reviews
the diff against the plan. Correctness only, no style.

Commit reviewed: `ec07012c48ec94d5e9177a9daa9fb76cafbe18d5` on branch
`track/gen`, against `f42a3fa` (`main` with ADR-005). `ec07012` adds only a
note in `docs/state/gen.md` to `85b5c7e`; the code reviewed is that of
`85b5c7e` (40 files, 7483 insertions).

## Pass 1, before the gate

This is pass 1 of the review. The gate `specfirst gate gen-1a` has not run
to its end: it needs the WSL machine, which was down. So this pass cannot
sign. It reports what should be settled before the gate is run and counted.
A second pass follows.

Verdict of pass 1: NOT SIGNED. Four findings block (F1 to F4), sixteen do
not (F5 to F20). The verdict and its reasons are at the end.

## How the review was done

A first run of this review was cut off by a restart of the machine; this
file is the second run, written from the start. I worked in the worktree
`specfirst-gen` only, with Windows git and a scratch Python environment
under Windows (Python 3.13 with the packages of `env/requirements.lock`;
not the reference platform). I used no WSL, no network and no CDISC CORE.
I changed no file of the repository except this one. My scripts are in a
scratch folder outside the repository (named `review1/` below) and are not
kept; each finding says what the script did, so that it can be repeated.

Near the end of my work another session began to change files of the
working tree without committing: first `src/specfirst/gen/command.py`,
`core_findings.yaml`, `gate.py` and `tests/unit/test_gen_gate.py` (at
12:19 local time), a few minutes later also `src/specfirst/cdisccore.py`,
`src/specfirst/gates.py` and `tests/unit/test_cdisccore.py`. None of that
is part of this review. No file that my experiments import was among
them: at my last look `git diff ec07012` was empty for `probes.py`,
`present.py`, `subjects.py`, `sdtm.py`, `study.py`, `pgfix.py`,
`design.py`, `rng.py`, `terms.py`, `datasetjson.py`, `define.py`, `env/`,
`scripts/` and `standard/`. To be sure that what I quote is of the commit,
I exported it with `git archive ec07012` into my scratch folder and ran
there again the six test files (108 passed), the pair table for the seed
`gen-1a-1` and the scripts behind F1, F2 (`rfx2.py`), F3, F7, F8 and F9
(`b6.py`), F9 to F11 (`breaks.py`) and F12 (the one script that imports
`gate.py` and `cdisccore.py`), with the same output. I looked once at the
uncommitted diff of the first three files and reviewed none of it; F4 says
what I saw in `core_findings.yaml`.

## What I read

- `CLAUDE.md`; `PLAN.md` sections 2, 4.3 to 4.8, 5, 6, 8 and 13.5;
  `docs/decisions/ADR-004.md`, `ADR-005.md`, `ADR-006.md`;
  `docs/state/std.md` and `docs/state/gen.md`; `docs/lessons.md`;
  the form of `docs/reports/std-1.review.md`.
- The 22 entries of the units `mod-treatment`, `mod-populations`,
  `mod-ae-emergence` and `tfl-ae-summary` in `standard/catalog/entries/`,
  their 22 compile templates, `standard/catalog/probes.yaml` and
  `catalog.yaml`; of the house standard `open-default@1`: `house.yaml`,
  `adam/adsl.yaml`, `adam/adae.yaml`, `ars/common.yaml`,
  `ars/ae-summary.yaml`, `layout/ae-summary.yaml`.
- All of `src/specfirst/gen/` (14 Python files and `core_findings.yaml`),
  `src/specfirst/cdisccore.py`, `src/specfirst/gates.py`, the diffs of
  `cli.py`, `doctor.py`, `env/`, `scripts/`, `.gitignore`, `CLAUDE.md`,
  `docs/lessons.md` and `third_party/SOURCES.md`.
- `tests/unit/test_gen_probes.py`, `test_gen_gate.py`, `test_gen_rng.py`,
  `test_cdisccore.py` in full; `test_gen_design.py` and
  `test_gen_subjects.py` by their test names;
  `tests/unit/test_alternatives_on_tiny.py` and
  `src/specfirst/compile/tiny.py` (std-1), for what an alternative computes.

## What I could not review

- Anything that needs CDISC CORE: whether the generated Dataset-JSON and
  Define-XML are accepted, what CORE reports for them, whether
  `core_findings.yaml` fits those reports, the options of the command line
  (`-ps`, `-of`, `-dxp`), the form of a real report, the planted defects of
  the check "CDISC CORE". The list of accepted findings rests on one study
  run by hand; I treat it as unproven and read only its logic.
- The install of `env/` on Linux, the clean-clone gate, and whether
  `env/core-requirements.lock` is what `make lock` gives on the reference
  platform. Whether `env/core-requirements.in` is the dependency list of
  CORE's `pyproject.toml` (the source is not in the worktree).
- The compiled specs on generated data. yamaa does not run in my
  environment. In its place I wrote my own reading of the 22 templates and
  of the parent specs (`review1/refimpl.py`: ADSL, ADAE and the cells of
  the adverse event summary for one decision vector). It gives the value
  std-1 expects in all 31 cases of `test_alternatives_on_tiny.py` that are
  about ADSL or ADAE (`review1/validate_ref.py`: "31 expectations of std-1
  on ADSL and ADAE, 31 met"). It is still my reading, not the engine:
  gen-2a decides by mutation. One place stays open: what yamaa's
  `not_before` does with a partial date of a month before the treatment
  start. I took the text of the entry `ae.start.imputation` ("when it falls
  in that month"). If the engine moves every earlier date up to the
  treatment start, the pair first_of_month_not_before_first_dose |
  not_completed is not separated in the table by its two probes.
- The gate log and the report `docs/reports/gen-1a.md`: neither exists yet.

## What I ran

All from the root of the worktree, with `PYTHONPATH=src` and `python -B`.

```text
$ python -m pytest tests/unit/test_gen_design.py tests/unit/test_gen_gate.py
    tests/unit/test_gen_probes.py tests/unit/test_gen_rng.py
    tests/unit/test_gen_subjects.py tests/unit/test_cdisccore.py -q
108 passed in 20.83s
```

`review1/pairs.py`, on the twins of the ten gate seeds `gen-1a-1` to
`gen-1a-10`: for every pair of alternatives of every decision of the slice
it builds ADSL, ADAE and the table under the house defaults with only that
decision changed, and compares. Where the table is the same it tries every
single change of one other decision. "x/y" is the number of twins; a dash
means the decision writes no ADaM value.

```text
decision              pair                                  ADSL or  table    table differs
                                                            ADAE     differs  only under
trt.planned.source    dm_arm | dm_armcd_map                 10/10    0/10     (1)
trt.actual.source     all three pairs                       10/10   10/10
trt.start.source      first_ex_with_dose | first_ex_record  10/10    0/10     nothing
trt.start.source      first_ex_with_dose | dm_rfxstdtc      10/10   10/10     (2)
trt.start.source      first_ex_record | dm_rfxstdtc         10/10   10/10     (2)
trt.end.source        last_ex_end_date | last_ex_start_date 10/10    0/10     (3)
trt.end.source        last_ex_start_date | ds_date_when..   10/10    0/10     (3)
trt.end.source        last_ex_end_date | ds_date_when..     10/10    0/10     nothing
trt.date.imputation   not_completed | first_day_of_month    10/10    0/10     (4)
date.studyday.origin  treatment_start | dm_rfstdtc           0/10    0/10     nothing
pop.randomized.rule   all_randomized | ..with_postbaseline  10/10    0/10     (5)
pop.safety.rule       the pair                              10/10   10/10
pop.safety.grouping   actual | planned                       -      10/10
pop.efficacy.rule     baseline_and.. | attended_visit        7/7     0/7      (6)
disp.status.record    disposition_event | by subcategory
                        STUDY PARTICIPATION                  0/10    0/10     nothing
                        STUDY TREATMENT                     10/10    0/10     (7)
ae.start.imputation   all three pairs                       10/10   10/10
ae.teae.start         the pair                              10/10   10/10
ae.teae.end           all three pairs, days = N             10/10   10/10     (8)
tfl.population        safety | randomized                    -       9/10     F3
tfl.population        safety or randomized | efficacy        -       7/7
tfl.columns.total     all three pairs                        -      10/10
tfl.ae.summary.rows   standard_rows | stated_rows            -      10/10
tfl.percent.format    the pair (cell texts)                  -      10/10     F8
tfl.rounding.rule     the pair (cell texts)                  -      10/10     F8

(1) trt.actual.source=same_as_planned, pop.safety.grouping=planned,
    tfl.population=randomized or efficacy
(2) through the subject of the probe partial_exposure_date, who leaves the
    safety set; the same table in 20 of 20 comparisons once
    trt.date.imputation=first_day_of_month (F2)
(3) ae.teae.end=last_dose_plus_days, for some values of days
(4) trt.start.source=dm_rfxstdtc
(5) tfl.population=randomized
(6) tfl.population=efficacy
(7) ae.teae.end=end_of_study
(8) N is the follow-up length of the design; other values in F6
```

`review1/many.py`, 150 further seeds (`review-0` to `review-149`), twin and
visible data: generation never stopped; `present.coverage` found no
problem; the two rounding rules and the two percentage formats gave
different cell texts in all 150 twins under the house defaults; in 18 twins
the table on the safety set equals the table on the randomized set (F3).

```text
   52  twin designs with 2 arms
   51  twin designs with 3 arms
   47  twin designs with 4 arms
  150  twin: generated
   15  twin: safety and randomized set give the same table (3 arms)
    3  twin: safety and randomized set give the same table (4 arms)
  150  visible: generated
```

`review1/gen_one.py`: the studies of `gen-1a-1` and `gen-1a-4`, each
written by three separate processes with `PYTHONHASHSEED` 0, 1 and 4242
into three folders: `diff -rq` finds no difference (50 files each).

`review1/consist.py`, 40 designs, twin and visible, 10409 subjects: the
truth and the SDTM agree with themselves (list under "Checked and found
correct"). Every disagreement it found is in a planted subject: those the
probes intend, the one of F4 and the two of F20.

The other scripts (`cancel.py`, `breaks.py`, `b6.py`, `rounding.py`,
`rfx.py`, `lockline.sh`, `small.py`) are quoted in the findings.

## Findings

Each finding says whether it blocks. "Blocks" means: to be settled before
the gate is counted and the review signed. "Does not block" means: to be
fixed or written down, and looked at again in pass 2.

### F1. BLOCKS: `env/lock.sh` cannot write `env/core-requirements.lock`

`env/lock.sh` line 27 is one line that holds the two characters backslash
and `n` five times, where lines 21 to 26 (the lock of the project) end in a
backslash. The last line of the script has the same. Outside quotes bash
reads `\n` as the letter `n`. With a stand-in for uv that prints its
arguments (`review1/lockline.sh`):

```text
env/lock.sh line 27
arg 1: [pip]
arg 2: [compile]
arg 3: [env/core-requirements.in]
arg 4: [n]
arg 5: [--python]
arg 7: [n]
arg 8: [--generate-hashes]
arg 9: [n]
arg 10: [--no-annotate]
arg 11: [n]
arg 12: [--custom-compile-command]
arg 13: [bash env/lock.sh]
arg 14: [n]
arg 15: [--output-file]
arg 16: [env/core-requirements.lock]
--- the last line of the script:
locks written: env/requirements.lock env/core-requirements.lock n env/r-packages.lock env/system.lock
```

uv gets five more requirement files named `n`. I did not run uv; I expect
it to stop at a file it cannot find, and the script has `set -e`. So
`make lock` cannot produce the lock that ADR-006 (decision 2) and
`env/README.md` say it produces, and the step ADR-006 leaves open ("`make
lock` on the reference platform ... whether the file came out the same")
cannot be done with the script as committed. The lock in the repository was
resolved by hand under Windows, which is how the line was never run. Its
first lines say "autogenerated by uv via the following command: bash
env/lock.sh"; that is not how it was made. Rule R3 (pin everything) holds
only when the pins can be made again.

### F2. BLOCKS: the probes of the treatment dates and of the study day change no result by themselves

PLAN.md section 6.5: "A probe is a planted subject or record on which two
alternatives of one decision give different results." Section 4.6 (P4)
measures results in the ARD. The slice has one output, the adverse event
summary. A treatment date reaches that table only through an event whose
emergence it decides, or through the safety flag. `Planter.fresh`
(`probes.py` line 102) makes every planted subject "without adverse
events", and the recipes of the treatment dates add none. So:

- `reference_start_before_first_dose` (`_reference_start`, lines 258 to
  267), claimed for `date.studyday.origin`. The two alternatives write
  ASTDY and AENDY of ADAE; the subject has no AE record. In the ten gate
  twins no value of ADSL or ADAE differs for any subject under the house
  defaults, and no cell of the table under any single change of another
  decision. The check `present._reference_start` (lines
  180 to 184) passes: it asks for RFSTDTC before the first dose and for no
  record whose study day would differ. The table shows no study day at
  all, so no recipe can separate this decision in the slice. Section 4.7
  has the word for it: `unseparated`, "reported", "not counted as proven".
  The gate counts it.
- `zero_dose_record_before_first_dose` (`_zero_dose`, lines 196 to 203),
  claimed for `trt.start.source` first_ex_with_dose | first_ex_record.
  TRTSDT of the one subject is day 4 or day 1; no event lies between. No
  cell differs in any of the ten twins under any single change of another
  decision, and none can: the subject has no AE record and both dates keep
  the subject in the safety set.
- `no_exposure_end_date` (`_no_end_date`, lines 221 to 228), claimed for
  `trt.end.source` last_ex_end_date | ds_date_when_ex_missing. TRTEDT of
  the one subject is missing or the disposition date; the subject has no
  event. No cell differs under any decision vector.
- `rfxstdtc_differs_from_exposure` (`_rfxstdtc`, lines 206 to 210), claimed
  for the two pairs with dm_rfxstdtc. Its own subject changes no cell
  (TRTSDT one day earlier, no event that day). The table differs in the
  twins all the same, through another probe: the subject of
  `partial_exposure_date` has RFXSTDTC with a year and a month only and
  drops out of the safety set. `review1/rfx.py`, gate seeds 1, 4 and 7:
  "twin as generated: ... table differs", "without the subject of
  partial_exposure_date: ... table same". And only while
  `trt.date.imputation` is not_completed: with first_day_of_month "20 of
  20 comparisons (10 twins, two pairs with dm_rfxstdtc) give the same
  table" (`review1/rfx2.py`).
- `partial_exposure_date` (`_partial_exposure`), claimed for
  `trt.date.imputation`: TRTSDT is day 4 or the first of the month; no
  event lies between. The table differs only when `trt.start.source` is
  dm_rfxstdtc (the same effect on the safety flag).

So for three pairs of alternatives, one of them the whole decision
`date.studyday.origin`, the twin holds no data on which the output of the
slice can differ; for three more (the two with dm_rfxstdtc and the pair of
`trt.date.imputation`) the difference comes from one subject's safety flag
and depends on another decision.
`probes.jsonl` states all of them as separated without a condition, and the
check "probes" passes them, because `present.py` looks for the pattern in
SDTM and not for a difference. gen-2a needs "every applicable decision of
the slice is separated on the twin" (ADR-005) and would stop here.

What would settle it: an event of the subject in the interval where the two
alternatives disagree (day 2 for the zero-dose subject; the day before the
first dose for the RFXSTDTC subject; between the first of the month and day
4 for the partial date; after the disposition date plus the window for the
subject without an end date, which then still needs `ae.teae.end` =
last_dose_plus_days); an event at all for the study day subject, and the
word `unseparated` for that decision in the log of the slice.

### F3. BLOCKS: the probe of `tfl.population` cancels in one of the ten gate twins

`randomized_never_dosed` is the only probe claimed for safety | randomized.
Three planted subjects move between the two analysis sets: A
(`actual_arm_differs_from_planned`) is counted under the actual arm in one
table and under the planned arm in the other; B (never dosed) is in the
randomized set only; C (`dosed_but_not_randomized`) is in the safety set
only. None of them has an event. When B is planned for the actual arm of A
and C is treated with the planned arm of A, every column has the same
count in both tables, and so has every cell. The arms are drawn
independently (`probes.py` lines 172 to 183, 283 to 293).

`review1/cancel.py`, twin of gate seed `gen-1a-9`:

```text
actual_arm_differs_from_planned: SFH7ULLD-101-025 ARMCD=TNB25 ACTARMCD=TNB50 AE records=0; check: found
randomized_never_dosed: SFH7ULLD-106-005 ARMCD=TNB50 ACTARMCD=None AE records=0; check: found
dosed_but_not_randomized: SFH7ULLD-103-033 ARMCD=None ACTARMCD=TNB25 AE records=0; check: found
analysis set safety:
   <Total>: {'N': 170, 'ANY': 115, 'RELATED': 24, 'SERIOUS': 10, 'DISCONTINUATION': 11, 'FATAL': 0}
   Placebo: {'N': 48, 'ANY': 27, 'RELATED': 3, 'SERIOUS': 3, 'DISCONTINUATION': 0, 'FATAL': 0}
   TNB-686 25 mg once daily: {'N': 63, 'ANY': 45, 'RELATED': 9, 'SERIOUS': 4, 'DISCONTINUATION': 4, 'FATAL': 0}
   TNB-686 50 mg once daily: {'N': 59, 'ANY': 43, 'RELATED': 12, 'SERIOUS': 3, 'DISCONTINUATION': 7, 'FATAL': 0}
analysis set randomized:
   (the same four lines)
present.coverage: 35 pairs, 28 probes, problems: []
```

Over 150 other seeds: 15 of 51 twins with three arms and 3 of 47 with four
arms, none of 52 with two (the expected shares are 1 in 4 and 1 in 9). This
is a decision of the table family itself, at the house defaults of every
other decision; in such a twin gen-2a cannot separate it.

### F4. BLOCKS (known to the author): the list of accepted CORE findings is unproven and one finding is open

`docs/state/gen.md` says it: CORE ran on one study, and rule CORE-000239
reported two subjects of the twin, of which only one belongs to the probe
that `core_findings.yaml` names for the rule (lines 146 to 153). As
committed, the gate would fail on that finding in every twin, or the list
would be widened without a look. I cannot run CORE. One observation for
whoever looks it up, a suspicion and no more: my own consistency script
compares the date part of DM.RFXSTDTC with the smallest EXSTDTC text of the
subject, and it reports exactly two planted subjects per twin: that of
`rfxstdtc_differs_from_exposure` and that of
`partial_exposure_date_not_earliest`, whose middle record has the text
"YYYY-MM", which sorts before the complete first date of the same month.
The subject of `partial_exposure_date` (the author's guess) is not
reported by it: its RFXSTDTC is the same "YYYY-MM" text as its first
record. If CORE takes the minimum of the texts, the second subject is the
one of the stress probe, and the entry needs that probe, in every twin.

The uncommitted change that another session made to `core_findings.yaml`
while I worked says the same of CORE-000239 and adds that probe. It also
changes the entry for CORE-000544 on SV from "every record" to "every
record of a subject with more than one visit". I did not review that
change; I note what it implies for the commit I reviewed: every generated
dataset has subjects with one visit (a screen failure and a subject who is
never dosed attend the screening visit only). So, if CORE reports what
that change says, the entry `sv-has-no-sequence-number` of the commit does
not hold for any generated dataset either. Both are for pass 2, on the
commit that holds them.

More about the logic of the list is in F12 and F13.

### F5. Does not block: seven decisions reach the table only under another decision's value, and the log does not say so

Notes (1) to (7) of the table above. Under the house defaults the adverse
event summary reads actual treatment, the safety flag and TRTEMFL. It does
not read planned treatment (`trt.planned.source`), the randomized flag
(`pop.randomized.rule`), the efficacy flag (`pop.efficacy.rule`), the
treatment end date (`trt.end.source`; only last_dose_plus_days reads it)
or the end-of-study date (`disp.status.record`; only end_of_study reads
it). That is the catalog, not the generator, and std-1 said so for gen-2
(ADR-004, consequences). But `probes.jsonl` repeats the `separates` of the
catalog without a condition, and section 6.5 predicts the identifiability
matrix from that file. A field in the log that names the other decision
(the catalog has `needs` for structural probes) would make the prediction
right; without it gen-2a finds these one by one.

For `trt.end.source` there is more: the base property
`last_exposure_record_spans_days` reaches the table only through events
after the last dose, and the base process has none ("no event after the
last dose", `subjects.py`). The table differed in my runs through the
planted events of the three `ae.teae.end` probes, for the values of days
near N.

### F6. Does not block: two recipes separate only for some values of a slot

- `ae.teae.end`, slot `days`. `Parameters.window_days` is the follow-up
  length N of the design (7, 14, 28 or 30); the three probes put events at
  N, N + 1, N + 2 days after the last dose and 2 days after the end of the
  study (which is N to N + 3 days after the last dose). The log repeats N
  "so that the decisions of a kit can be sampled to fit". For other values:
  no_end | last_dose_plus_days(30) differs in nothing, not even in ADAE,
  in the 7 gate twins with N = 7 or 14; last_dose_plus_days(30) |
  end_of_study differs in nothing in the 2 twins with N = 28. The examples
  of the entry are 30 and 7. So in every kit whose data separate the
  decision, the number of days in the SAP equals the follow-up length of
  the protocol. That is a limit of the generated studies that the report
  should state (section 6.8), and gen-2 must follow it.
- The same decision at the boundary: last_dose_plus_days(N) |
  last_dose_plus_days(N + 1) changes TRTEMFL of one event in every twin
  and no cell in any (0/10): the subject of
  `ae_starts_after_emergence_window` has both events, and the table counts
  subjects with at least one. The two events have different terms, which
  will show in the table by organ class and term of the full gen-1, not in
  the summary.
- `disp.status.record`, slot `subcategory`. The planted subject has the
  end of treatment first and the end of the study last, as the recipe of
  the catalog says. "The last by DSSEQ" and "the record with the
  subcategory STUDY PARTICIPATION" are then the same record, for this
  subject and for every other: 0/10 in ADSL. The pair is separated only
  when the decision names STUDY TREATMENT, the value that makes the
  statement false for the study, or a subcategory that no record has. The
  recipe comes from std-1; the finding goes to the std track as well.

### F7. Does not block: in a design without an efficacy set the log claims two pairs that cannot be built

`tfl.population` applies to every design and has the alternative
`efficacy`. In a design without the efficacy-evaluable population
(`gen-1a-1`: "efficacy set: False decisions: 21 pairs: 34") the twin still
logs `dosed_without_postbaseline_value` with `separates` safety | efficacy
and randomized | efficacy, and the check counts both pairs as covered. No
decision writes EFFFL in such a study; the compiler refuses a table that
reads it (ADR-004, decision 5). The catalog has no applicability per
alternative; until it has, the log should not claim these pairs.

### F8. Does not block: the count probes hold under fewer decisions than the log says

The arithmetic is right. `is_rounding_half` accepts exactly the
percentages that end in .25: halfway at one decimal with an even digit
before the half, so half away from zero gives .3 and half to even gives
.2; .75 would round the same under both rules and is refused. With arms
that are multiples of 16 the count over the total is k/16, which binary
floating point holds exactly, whether an engine computes 100 * n / N or
n / N * 100. Under the house defaults the two rules gave different cell
texts in all 150 twins; in the ten gate twins and in the 40 further twins
where I looked at the cells, the two calibrated cells of the placebo
column are among them, for example "18 (56.3)" and "18 (56.2)", "2 (6.3)"
and "2 (6.2)".

What is claimed and not true:

- The log says `"assumes": {"tfl.population": "safety",
  "pop.safety.grouping": "actual"}` (`probes.py` line 479). It also
  assumes `trt.actual.source` = dm_actarm and that `tfl.ae.summary.rows`
  shows ANY or SERIOUS. `review1/rounding.py`, 40 twins, one other
  decision changed, twins in which the two rounding rules give the same
  table:

  ```text
     14  pop.safety.grouping=planned
      9  tfl.population=efficacy
     14  tfl.population=randomized
     40  trt.actual.source=first_ex_treatment
     14  trt.actual.source=same_as_planned
  ```

  Under first_ex_treatment the subject of `first_exposure_other_treatment`
  joins the group PLACEBO in every twin, whose count is then no multiple
  of 16. The module text "the placebo arm, which no planted subject enters
  under actual treatment" holds for DM.ACTARM only. With the rows RELATED and
  FATAL alone, the rounding rules differ in no cell in 6 of the 10 gate
  twins (`review1/b6.py`).
- `category_with_zero_count` logs no assumption. It needs the row FATAL:
  with the rows `[ANY]` (an example of the entry) the two percentage
  formats differ in 0 cells in all ten gate twins, with `[SERIOUS,
  RELATED, ANY]` in 0 cells in 8 of them.

### F9. Does not block: `present.py` finds patterns that do not separate, and misses one that does

For each case I changed the data of the twin of `gen-1a-4` and asked two
things: does `present.find` still find the probe, and do the two
alternatives still differ for the subject (`review1/breaks.py`)?

```text
--- B1a ae_on_first_dose_date_without_time: the time is taken off EX.EXSTDTC, DM.RFXSTDTC keeps it
    before: check finds the probe; ... ADAE for 2 (the probe subject: yes)
    after:  check finds the probe; ... ADAE for 1 (the probe subject: no)
--- B1b the same probe: the time is taken off DM.RFXSTDTC, EX.EXSTDTC keeps it (the planted defect of tests/unit/test_gen_probes.py)
    after:  check ['SF8NT5GG-101-033: the first dose has no time after 00:00']; ... ADAE for 2 (the probe subject: yes)
--- B2 no_exposure_end_date: the records of the subject get the dose 0 (no treatment start)
    after:  check finds the probe; ADSL differs for 0 subjects, ADAE for 0 (the probe subject: no)
--- B3 dosed_but_not_randomized: the records of the subject get the dose 0
    after:  check finds the probe; ADSL differs for 0 subjects, ADAE for 0 (the probe subject: no); table cells same
--- B4 zero_dose_record_before_first_dose: a placebo record (dose 0) on the same first day
    after:  check finds the probe; ADSL differs for 0 subjects, ADAE for 0 (the probe subject: no)
--- B5 partial_ae_start_in_month_of_first_dose: the event ended on day 2 of the month, before the first dose
    after:  check finds the probe; ... table cells same, cell texts same
```

- B1: `_on_first_dose_date` (`present.py` lines 289 to 297) reads the time
  of the first dose from DM.RFXSTDTC. The house default of
  `trt.start.source` reads it from EX.EXSTDTC. The planted defect of the
  unit test (`_undo_dose_time`, `test_gen_probes.py` lines 236 to 238)
  takes the time off the DM value: the check then reports the probe as
  gone while the alternatives still differ for the subject, and it stays
  silent in the real case, the time missing in EX. A simpler cousin
  (lesson 9), and here the wrong variable.
- B2, B3, B4: `_no_end_date`, `_not_randomized` and `_zero_dose` do not ask
  whether the subject has a treatment start in the sense of the decision
  (a record with a dose and a complete date). The alternatives need it.
- B5: `_partial_ae_in_month` does not ask that the event is not over
  before the first dose; the parent spec flags no event that ended before
  it.
- `_rounding_half` (`arm_counts`, lines 383 to 393) counts events that
  start after the day of the first dose. The house default counts an event
  on that day as emergent. `review1/b6.py`: one serious event on the day
  of the first dose, for one more subject of the calibrated arm; the check
  "finds the probe" in all ten gate twins, the two calibrated cells are no
  longer at a half, and in the twins of `gen-1a-1` and `gen-1a-10` no cell
  differs between the rounding rules any more. The base process starts no
  event on day 1, so this is a hole of the check, not a defect seen in
  generated data.
- `_reference_start`: see F2.

None of these was seen in generated data: the recipes plant the full
pattern. They are the cases the check exists for when a recipe changes.

### F10. Does not block: the check trusts the log for which pairs a probe separates

`present.coverage` (lines 480 to 482) reads the pairs from the field
`separates` of each log line, which the generator wrote, and never from
`catalog.probes`. `review1/breaks.py`, B7: I left `two_disposition_events`
out of the log and wrote its pair into the line of `output_shape`, a
structural probe whose check always passes:

```text
two_disposition_events left out of the log, its pair written into the line of output_shape: coverage problems = []
```

The planted defect of the gate ("a probe is left out of the log") is the
simple case. The claims should come from the catalog; the log is what is
being checked. The module says it itself: "A line of a log proves nothing
by itself."

### F11. Does not block: the gate does not ask that the twin carries every probe

PLAN.md section 13.5: "The twin gets all probes"; section 6.5: "The twin
carries the full set of probes." `probes_check` prints "{checked} of
{needed} probes logged" and fails on no difference between the two numbers
(`gate.py` lines 414 to 418). A probe that separates no pair (it varies a
slot, or stresses a rule) can be missing without a word. B8:

```text
ae_with_each_causality_value left out of the log (27 of 28 probes): coverage problems = []
baseline_value_of_other_test_only left out of the log (27 of 28 probes): coverage problems = []
partial_exposure_date_not_earliest left out of the log (27 of 28 probes): coverage problems = []
```

`ae.related.values` has one alternative and no default; its only probe is
the first of these, so the gate protects nothing of that decision. The
unit test `test_the_twin_carries_every_probe_of_the_slice` asks for the
full list, for four seeds of its own, not for the gate seeds.

### F12. Does not block: a report of CORE is not tied to the datasets, and "identical hashes" compares builds of one process

- `gate.report_problems` (lines 220 to 230) asks for the engine version,
  the standard and at least 100 rules. It does not ask that the report
  lists the eleven datasets that were handed over, nor that CORE read the
  Define-XML. `gate.report_problems(root, Report(..., datasets=()))`
  returns `[]` (`review1/small.py`); the unit test builds such a report
  and expects no problem. `Report.datasets` is read and never used. If
  CORE skips a file it cannot read, the gate cannot see it. I do not know
  whether CORE does; the check is cheap.
- `determinism_check` generates both builds in the gate's own process.
  What is constant within one process (the hash seed, the working folder,
  the environment, a cache of a module) is the same in both; lesson 15 is
  this case one level up. The planted defect, a build with another time
  stamp, proves the comparison of two lists of hashes and nothing about
  where a dependence could come from. My three processes with three hash
  seeds gave identical folders, so the generator passes the stronger
  check today; the gate does not make it.
- The same check compares the hashes of the files and not the manifest
  `study.json`, which `file_hashes` leaves out. A clock in the manifest
  would pass the gate. The unit test compares the manifests of one seed.

### F13. Does not block: three places where "explained" is wider than its reason

All in `gate._holds` and `core_findings.yaml`; unproven in both
directions, since I have no report of CORE.

- Kind `probe`: the subjects come from the detail rows of the report, the
  count from its summary. `_holds` does not ask that the two agree. A
  finding with more issues than detail rows would be explained by the
  subjects that happen to be listed. Asking `count == number of detail
  rows` costs one line. (A suspicion: I do not know whether CORE ever
  lists fewer rows.)
- Kind `every_record` for CORE-002056 and CORE-002084 (lines 103 to 117)
  has no `datasets`: any dataset whose number of records equals the number
  of issues is accepted. For a dataset with one record that is one issue
  about one record.
- CORE-002056 is accepted as a whole with the reason that the study has no
  TI, TD and TM. TI (inclusion and exclusion criteria) is a trial design
  dataset; PLAN.md section 13.5 asks for "the trial design datasets CORE
  expects" and ADR-005 for "the datasets CORE requires". Whether an
  invented TI is owed is a question for the author and the owner; the
  explanation decides it silently.

### F14. Does not block: ADR-006 and the code

- Decision 7 says the datasets go to CORE with "the controlled terminology
  package that the Define-XML names". The code passes no package:
  `gate.run_core` calls `cdisccore.validate` without `terminology`, so no
  `-ct` is on the command line. Whether CORE 1.0.0 then takes the package
  from the Define-XML I cannot tell. The planted defect SEX = X is what
  would show it; until the gate has run, the sentence of the ADR is not
  supported by the code.
- Decision 2 and the header of the lock: F1.
- The doctor compares names and versions of the installed packages with
  the lock. pip itself is left out on purpose and is whatever the system's
  Python brings; say so in the ADR. I found no way to an install that is
  unpinned or partly done and passes the doctor: every step uses
  `--no-deps --require-hashes`, the folder is named after both pins, the
  source must be at the commit with a clean tree, ignored files included,
  and a package outside the lock is reported.
- Nothing checks that `env/core-requirements.in` is still the dependency
  list of CORE's `pyproject.toml` at the pinned commit. After an install
  the file is there to compare with.

### F15. Does not block: `rng.py` claims more than it gives

"Its numbers ... depend on nothing but the name: not on a library version"
(`rng.py` lines 3 to 7). True for `uniform`, `below`, `choice`, `shuffled`.
`normal`, `exponential` and `poisson` (lines 88 to 107) go through
`math.log`, `math.cos` and `math.exp` of the C library, which need not be
correctly rounded and can differ in the last bit between platforms and
versions; the results are then rounded to days, years, counts and
decimals, so a difference would show only for a value on a rounding edge.
The unit test "the same numbers on every machine and version" rounds these
three to nine decimals. The chance is tiny and I saw no difference (I have
one platform). But the bytes of a study were compared only between builds
of one machine, and the sentence should say what holds: the same bytes on
the pinned platform.

### F16. Does not block: the documented models leave out what the code does

`subjects.py` promises the models "documented here" (section 6.4: "simple,
documented models"). Not in its text: a serious, severe event after the
first dose is fatal with a chance of 0.10 and the subject dies on the day
it ends (`base_subjects`, lines 460 to 465, `make_fatal`); nobody dies in
the placebo arm when the zero count probe is chosen; a subject who stops
for an adverse event gets the action DRUG WITHDRAWN on the last event;
there is no follow-up visit after LOST TO FOLLOW-UP and WITHDRAWAL BY
SUBJECT (the text says "except the follow-up visit"); the follow-up visit
is timed from the last dose, not from its planned day. The report of the
part should also say that every twin has a placebo arm of 16 k subjects
with exactly k and 5 k, 9 k or 13 k of them affected, and no death in it.

### F17. Does not block: the hash of the seed is not the hash of the seed file

PLAN.md section 6.7: "The repository stores only the SHA-256 of the seed
file." `read_seed` strips the text of the file and `seed_sha256` hashes the
text (`command.py` line 40, `rng.py` line 112). For a file "abc" with a
line end, `sha256sum` of the file gives another value than `study.json`.
Either is fine; the two should be the same thing. Also: a seed file inside
another worktree of the same repository is accepted, because only the
checkout that runs the command is looked at.

### F18. Does not block: records

- `third_party/SOURCES.md` names `sdtm.py` for the metadata of SDTMIG.
  `sdtm._ts` (lines 641 to 674) also holds 14 NCI codes of controlled
  terms (C49487, C82639 and so on); the row of `terms.py` covers that kind
  of fact, the row of `sdtm.py` does not name it.
- I found nothing in a generated study that is not invented: the study
  code, the drug name, sites, subjects and values come from the seed; the
  event dictionary is the generator's own and Define-XML names it so.
- The catalog version is in every generated file I looked at (design,
  probes, truth, Dataset-JSON, Define-XML, manifest; the Parquet files in
  their schema note), and the test asks for it. A design of another
  catalog version is refused.
- No seed is in a generated file (the test searches all bytes); the gate
  seeds are development seeds.

### F19. Does not block: scope

- SV and VS are needed by the slice: the parent spec of ADSL reads both
  files, `pop.randomized.rule` and `pop.efficacy.rule` read VS, and
  `pop.efficacy.rule` reads SV. SE and the four trial design datasets are
  what CORE asks for; TI is the open question of F13.
- The design model has no place for strata (section 6.2: "randomized
  (ratio, strata)"), endpoints or analysis timing. The slice does not need
  them; the full gen-1 does.
- Missing, as the state file says: the gate run, the clean-clone gate, the
  report `docs/reports/gen-1a.md` (rule R8), `make lock` on Linux.
- ADR-006 is "proposed" and "stands unless the owner objects". The task
  asked for an ADR for the change of `env/`; whether silence is approval
  is the owner's call.

### F20. Does not block: two small things in the data

- The events that the three `ae.teae.end` probes plant after the last dose
  have AEACN "DOSE NOT CHANGED" (`Planter.event`, line 128). After the end
  of treatment the base process would say NOT APPLICABLE, as it does
  before the first dose. No row of the table reads it.
- An event planted two days after the end of the study has the epoch
  FOLLOW-UP and lies after DM.RFPENDTC and after the last element of SE.
  The probe intends it and the list of CORE findings names it.

## Checked and found correct

- The gate table: environment first, then lint, unit tests, the three
  checks, ASCII. A check that raises is a failed check (`gates.run_gate`),
  so a missing or crashing CORE fails the gate; it cannot be skipped
  (`--no-core` exists for `specfirst gen check` only). No check passes on
  nothing: zero seeds raise; a report with fewer than 100 rules is a
  problem; a probe logged without a subject is "not there"; an entry of
  the list that no finding needed fails the gate; if the units of the
  slice named no decision, the three planted defects of the probe check
  would fail first.
- `classify`: a finding of a `probe` entry with one subject that no probe
  planted is unexplained as a whole; a rule that cannot run is explained
  only with its error text; a subject of the visible data does not explain
  a finding of the twin.
- Determinism: no clock (the time stamp is the last study date), no
  unseeded randomness, no set or dictionary order in what is written
  (every set is sorted before use), explicit line ends, ASCII; identical
  folders from three processes with different hash seeds.
- 150 seeds, twin and visible: no recipe stopped, every logged probe was
  found, and every arm of the base process had exactly its planned number.
- Probes that hold as claimed, at the house defaults, in the ADaM and in
  the table of all ten gate twins: the three pairs of `trt.actual.source`,
  `pop.safety.rule`, `pop.safety.grouping`, the three pairs of
  `ae.start.imputation` (with the reading of `not_before` named above),
  `ae.teae.start`, the three pairs of `ae.teae.end` for days = N, and two
  lists of `ae.related.values` that differ in one causality value.
- Truth and SDTM, 10409 subjects: exposure records are contiguous and end
  with the last dose; every study day follows from RFSTDTC with no day 0;
  EPOCH is the epoch of the SE element of the date; the SE elements are
  contiguous; keys are unique; RFXSTDTC and RFXENDTC are the first and
  last exposure dates; death date, flag, fatal event and the DS record
  agree and nothing is dated after a death; outcome and end date of an
  event agree; every VS record has its SV visit on that date and the visit
  of TV; the milestone RANDOMIZED and ARMCD agree; DRUG WITHDRAWN and the
  disposition ADVERSE EVENT agree.
- The conventions std-1 states: ARMCD empty for a subject without an arm,
  PLACEBO with dose 0, no VISITDY for an unscheduled visit; every variable
  the house specs read is written, with the file names the parent specs
  expect; AGE and VISITDY are floating point in Parquet as in
  `compile.tiny`.
- Planted subjects are numbered with the others in the order of consent;
  their kind shows only in gold.
- The sampler: 2 to 4 arms, placebo control, 1:1 or 2:1, fixed duration,
  visits with windows, three epochs; the ten features of `catalog.yaml`
  are all computed; every design lists its arms out of dose order and has
  arms in multiples of 16, as the module says and why.
- `env/requirements.lock` is unchanged; CI installs and runs no CORE; the
  clean-clone script unsets the two new variables.
- The 38 rules that cannot run and the six that report on any data are the
  numbers of ADR-006.

## Verdict of pass 1

NOT SIGNED. The gate has not run, so nothing could be signed today; apart
from that, four findings block:

- F1: `env/lock.sh` cannot write the lock of CORE.
- F2: under the house defaults none of the five probes of the treatment
  dates and of the study day changes a cell of the one output for the
  pairs it claims; for three pairs of alternatives, one of them all of
  `date.studyday.origin`, the twin holds no data on which the output can
  differ under any decisions, and the gate counts them as separated.
- F3: the probe of `tfl.population` cancels against two other probes in
  the twin of gate seed `gen-1a-9` and in about one twin in four with
  three arms.
- F4: the list of accepted CORE findings rests on one study, and one
  finding is open.

F2 and F3 are not failures of the gate script: it passes them, and that is
the finding. They are failures against the definition of a probe in
section 6.5, and gen-2a would meet them as failures of its own gate. If
the author and the owner decide that gen-1a owes only the pattern in SDTM
and gen-2a the difference in results, then that belongs in the report, the
log must mark what is conditional or unseparated (F5 to F8), and F2 and F3
move to gen-2a as known defects of the generator.

For pass 2 I will read the gate log and the report, look at
`core_findings.yaml` against real reports of CORE, and repeat the pair
table on the commit that is to be merged.

## Pass 2

Commit reviewed: `39ff635c614031a89c44e9ab533f9674219b761b` on `track/gen`,
the commit on which the gate ran. Since pass 1 (`ec07012`): `5f40ae7` the
answers to the findings of pass 1, `11fec2c` the lessons renumbered,
`18c23c8` the merge of `main` (catalog version 1, real-3a), `39ff635` the
gate keeps the reports of CORE. I read the diff `ec07012..39ff635` for
`src/specfirst/gen/`, `src/specfirst/cdisccore.py`, the gate table in
`gates.py`, the six test files, `env/lock.sh`, ADR-006 and
`third_party/SOURCES.md`; the 70 files that the merge brought from other
tracks are not mine to review. Beside the code I read, as they stood in the
worktree, not yet committed: the report `docs/reports/gen-1a.md`, the gate
log `docs/reports/gen-1a.gate.log`, the log of the second run of the check
"CDISC CORE" `docs/reports/gen-1a.core.log`, the handover
`docs/state/gen.md` and lesson 39. The verdict at the end holds for the
code of `39ff635` and for these texts as I read them.

Pass 1 names two lessons by number, 9 and 15; both numbers stand. The
lessons of gen-1a, which were 27 to 33 on the branch before the merge of
`main`, are 32 to 38 now (real-3a took 27 to 31 first); 39 is new.

The pass had three parts: A, the code and my pair table, while the gate
ran; B1, the gate log, the report and the handover; B2, the reports of
CORE. The author changed no code after part A, so that the code of the
merge is the code that passed the gate; what parts A and B1 found went
into the report and the handover, and I read them again in B2.

### How pass 2 was done

As pass 1: in the worktree, with Windows git and the scratch Python under
Windows; no WSL, no network, no run of CORE by me. My scripts are in my
scratch folder (`review1/` and `review1/pass2/`) and are not kept. Where a
result rests on the compiled specs, it rests on my own reading of the
templates (`refimpl.py` of pass 1, unchanged; the 22 entries and templates
of the slice did not change with catalog version 1), not on yamaa.

### What I ran

```text
$ python -m pytest tests/unit/test_gen_design.py tests/unit/test_gen_gate.py
    tests/unit/test_gen_probes.py tests/unit/test_gen_rng.py
    tests/unit/test_gen_subjects.py tests/unit/test_cdisccore.py -q
133 passed in 41.87s
$ python -m pytest tests/unit/test_gates.py tests/unit/test_layout.py
    tests/unit/test_sources.py -q
87 passed in 1.78s
```

- `review1/pairs.py`, unchanged, on the twins of the ten gate seeds. Its
  output and its summary are byte for byte the files the author had made
  with the same scripts (`pairs2.txt`, `summary2.txt`).
- `pass2/reach.py`: every claim of the new field `reaches` of
  `probes.jsonl` against the table, on the ten gate twins and on 200
  further twins (`p2-0` to `p2-199`); with `--broad`, on the gate twins,
  every pair under every single change of one other decision as well.
  `pass2/reach2.py`, `eff.py`, `slots.py`: other values of the slots, 200
  twins.
- `review1/many.py`, 150 seeds, twin and visible: every study generated,
  every logged probe found, no twin whose table on the safety set equals
  the one on the randomized set (pass 1: 18 of 150).
  `review1/consist.py`, 40 designs, 10466 subjects.
- `review1/breaks.py` and `b6.py` of pass 1 again; `pass2/newcode.py`, my
  own planted cases against `cdisccore.requirement_problems`,
  `command.read_seed`, `gate._holds` and `gate.term_problems`;
  `pass2/f3teeth.py`.
- `pass2/core.py`, `ctrules.py`, `hashes.py`: the 21 reports of CORE read
  with `cdisccore.read_report` and judged with `gate.classify` and
  `gate.report_problems` against the ten studies generated again here
  with `gate.generate_all`. `pass2/unchecked.py`, `taetord.py`: what the
  rules that could not run would have looked at, in those 20 datasets.

### The blocking findings of pass 1

F1, settled. Lines 27 to 32 of `env/lock.sh` are six lines with a
backslash at the end again; with my stand-in for uv the command gets the
same 11 arguments as the one for the project lock. No test reads the
script (F28). The report quotes `bash env/lock.sh` on a copy under WSL and
`cmp` on the four locks, all "same"; that is the author's output, which I
could not repeat.

F2, settled. The five recipes plant the event that carries the difference
(`probes.py`: `_zero_dose`, `_rfxstdtc`, `_partial_exposure`,
`_no_end_date`, `_reference_start`), and each finder asks for it; the
tests `_f9_no_event` remove the event and the finder then misses the
probe. At the house defaults the table differs for the three pairs of
`trt.start.source` and for `trt.date.imputation` in 10 of 10 gate twins
and 200 of 200 further twins (pass 1: one pair of the first and the pair
of the second in 0 of 10). last_ex_end_date | ds_date_when_ex_missing
differs with a window of N days in 10 of 10 and 200 of 200.
`date.studyday.origin` now differs in ADAE (ASTDY) in 10 of 10 and in no
cell, and the log says `never`; the report hands it to the owner as
`unseparated` in the sense of section 4.7.

F3, settled, by construction: the subject who is never dosed is planned
for the arm that the subject dosed off plan left, so that arm is short in
the safety set whatever the third subject does. 0 of 150 and 0 of 200
twins have equal tables. The new test has teeth: with the never-dosed
subject in a freely drawn arm again, 10 of its 60 designs have the same
counts in both sets (`pass2/f3teeth.py`); with the recipe of the commit,
0 of 60.

F4, settled. The list was read against real reports. Judged here, with
the studies generated again under Windows, the 20 reports give what the
gate log gives: 1,825 findings, each explained by exactly the entries the
log counts, no problem of a report, no finding unexplained. Entry by
entry (`pass2/core.py`):

- The 38 rules of the six `cannot_run` entries have the status EXECUTION
  ERROR in 20 of 20 reports, each with the error text of its entry.
- CORE-000510: one issue per dataset and run, no record (220).
- CORE-000544 on SV: in 20 of 20 reports the detail rows are exactly the
  SV records of the subjects with more than one visit (twin of
  `gen-1a-1`: 814 records, 29 subjects with one visit, 785 issues). The
  entry of pass 1 ("every record") could not have held; this one does.
- CORE-000757 on EX and CORE-002034, CORE-002056, CORE-002084 on AE: the
  detail rows are the rows 1 to n of the dataset in every finding.
  CORE-002056 lists 61 domains that the study lacks, TI, TD and TM among
  them, as the reason says.
- CORE-000735 and CORE-002081 on TS: one issue each, no subject.
- The five `probe` entries: every detail row of every finding belongs to
  a subject of a probe that the entry names. CORE-000239 reports the
  subject of `rfxstdtc_differs_from_exposure` (15 rows) and the subject
  of `partial_exposure_date_not_earliest` (15 rows; the report shows the
  minimum "2020-05" against RFXSTDTC "2020-05-09T11:45"): the suspicion
  of pass 1. CORE-000717 and CORE-002088 report the events after the end
  of the study of two probes (12 and 15 rows).
- In all 505 findings with issues the number of issues equals the number
  of detail rows; the reports name no issue limit.

`planted-twin.json`: against the report of the twin of `gen-1a-1`, three
findings differ and nothing else. CORE-000544 on AE, 2 issues, rows 1 and
2 of SFATXTPG-101-001; CORE-000655 and CORE-000656 on DM, 2 issues each,
SFATXTPG-101-002 (planted) beside SFATXTPG-102-016 (the probe). All three
are unexplained when judged here. That is what the gate log says, by
rule, dataset and subject.

The reports are those of a second run: the gate kept its own beside its
log in the clean clone under `/tmp`, which the WSL instance cleared (lesson
39; the report says so). Lines 2 to 46 of `gen-1a.core.log` equal lines
96 to 140 of the gate log but for the name of the folder. And the
datasets are the same ones: the last line of the core log is a SHA-256
over the hashes of the 510 files of the Linux run; the same value comes
out of the 510 files I generated under Windows (SHA-256 of the JSON text
of seed, file and hash with sorted keys; I found the formula by trying,
the log does not give it). So the ten studies are byte for byte the same
under Linux with Python 3.12 and under Windows with Python 3.13, Parquet
files and manifests included.

### The other findings of pass 1

State at `39ff635`:

- F5, settled: the field `reaches`. Its claims hold in the 10 gate twins
  and in 200 more, with the exception F21 and the narrowings F22.
- F6: N against N + 1 days now differs in the table (10 of 10, 200 of
  200); the rest is stated as a limit.
- F7, settled: 32 pairs in a design without an efficacy set (34 before).
- F8, settled: `detail.assumes` names every decision under which my broad
  run loses a count probe.
- F9, settled: the finders now miss every case B1a to B6 of pass 1;
  twelve tests.
- F10 and F11, settled: B7 and B8 of pass 1 are reported now.
- F12, settled: a report must name the datasets with their records,
  Define-XML 2.1.0 and the terminology (all 20 do); the second build is a
  process of its own; the manifest is compared.
- F13: the kind `probe` is exact; the two rules about every record are
  bound to AE; the missing TI is stated and left to the owner.
- F14, settled in the text of ADR-006; the doctor compares
  `env/core-requirements.in` with the list of CORE.
- F15 to F18, settled.
- F19, stated: no strata, endpoints, analysis timing or TI.
- F20, settled: a planted event outside the treatment period has the
  action NOT APPLICABLE.

Nothing is called settled in the report's table of the review that is
not.

### New findings

None blocks.

#### F21. Does not block: one more cancellation, in `pop.efficacy.rule`

With `tfl.population` = efficacy, the condition that `reaches` names,
baseline_and_postbaseline | attended_visit gives the same table in 4 of
109 twins with an efficacy set when the visit is the first one after day
1 (both tests), and in 2 of 109 for WEIGHT with the follow-up visit; 6
twins have at least one such pair of slot values, none has it for all,
and none of the 7 gate twins has it. In `p2-41` (two arms) four planted
subjects without an event sit in the one active arm: two enter the set
and two leave it. The report (Limits) and the handover state it; it is
not fixed. The remedy of the other two cases would do: an event for one
of the four.

#### F22. Does not block: `reaches` promises less than it reads

- `always` assumes a table that shows the row ANY. With the rows RELATED
  and FATAL alone nothing differs in 10 of 10 gate twins for
  `trt.date.imputation`, `ae.start.imputation`, `ae.teae.start`,
  `ae.teae.end` and one pair of `trt.start.source`.
- For `trt.end.source` the log says "an emergence window"; it needs the
  window of N days. With N + 2, last_ex_end_date | ds_date_when_ex_missing
  is the same in 200 of 200; with N - 1, last_ex_start_date |
  ds_date_when_ex_missing in 99 of 200.
- Two interplays are not in it: first_of_month_not_before_first_dose |
  first_of_month is lost under `ae.teae.start` =
  at_or_after_first_dose_time, and no_end | end_of_study under
  `disp.status.record` with the subcategory of the treatment record (10
  of 10 each).

All three are in the report or the handover now, for the first commit of
gen-2a.

#### F23. Does not block: two values of one slot often give the same table

The two subjects planted for the two values cancel in one arm: the test
of `pop.randomized.rule` (SYSBP | WEIGHT, table on the randomized set) in
125 of 200 twins, the test of `pop.efficacy.rule` in 52 of 109, its visit
(first | second after day 1) in 5 of 97. The gate asks for pairs of
alternatives only, and the log repeats the `varies` of the catalog. A
wrong value of such a slot is invisible in the table of such a twin;
gen-2a and read-1a are told so in the handover.

#### F24. Does not block: what CORE did not check is not in the report

From the 20 reports: 315 rules passed in every report, 191 were not
applicable in any, 18 reported issues (8 in every report, 10 where a
probe is), 38 could not run. The 38, by subject: MedDRA terms, codes and
version (13; the dictionary is the generator's own, so these would report
every event if they ran); codes of the trial summary in SRS, NDF-RT,
MED-RT and SNOMED (10); country codes in DM and TS (3); race and
ethnicity options, variable lengths and file tags from the Define-XML
(4); the versions in TS (2); FDA's desired TS parameters (2); extended
terms of extensible codelists and LOINC (2); and two that touch every
record: CORE-002121, "Value must be a valid ISO 8601 datetime or
interval", on all 11 datasets, and CORE-002101, TAETORD against TA, on 9.
So "passes CORE" says nothing about the form of a date value as such,
about TAETORD or about a country code. I looked at the three in the 20
datasets myself (`pass2/unchecked.py`, `taetord.py`): all 199,315 date
values have an ISO 8601 form; the six country codes are valid; SE.TAETORD
is the order of TA for the planned arm in all 7,225 records of subjects
with a planned arm and empty for the element of an unplanned treatment.
One thing a rule might report if it ran: the screening element of a
subject without an arm (342 screen failures, 12 not assigned) carries
TAETORD 1, though no arm of TA is theirs. The evidence for all of this is
the unit tests and not CORE; the report should name the subjects of the
38 rules beside their number.

#### F25. Does not block: the claim about controlled terms holds

16 of the 562 rules name a codelist, a terminology or valid values. Over
the 20 reports: 8 were not applicable (six on PK units, one on FDA's
therapeutic area guides, and CORE-002123, "A new term has been added to a
non-extensible code list", the one rule that would speak of SEX = X), 5
could not run, 3 passed (the domain code, TSVALCD in the CT version,
TSVCDVER). No rule that compares a value of a subject with its codelist
ran with a result; a few rules name fixed values of one variable
(CORE-000124, AESCONG 'Y' or 'N'). The reports name the package
`sdtmct-2025-09-26`, so the terminology was loaded. That fits the claim
"CORE 1.0.0, run this way, reports no value outside its codelist". The
report now quotes a run with eight planted defects, of which SEX, AGEU
and AESEV passed and five others were reported; that is the author's
output from a scratch script, not repeated by me. The gate's own check
"controlled terms" found my planted values in controlled variables
(`pass2/newcode.py`, with a package made from the generator's table; the
check itself needs the cache of CORE).

#### F26. Does not block: a planted DM record that the v3.4 rules refuse

Four rules report the subject of `dosed_but_not_randomized` in every
dataset that has it: CORE-000192, CORE-000758, CORE-000927, CORE-002099
("Subject is not assigned to treatment (ARMCD is not populated) but
ACTARMCD is populated."; "RFSTDTC must not be populated when ARMNRS is
populated with a value other than 'UNPLANNED TREATMENT'"). The list
explains them as planted, and the report says that four rules report the
subject. What a reader of the datasets should also know: by these rules
the record is not an edge case of conformant data but a record that the
rules for v3.4 do not allow, with the reason NOT ASSIGNED beside an actual
arm and a reference period. The recipe of the catalog ("ARMCD is
NOTASSGN") is older than v3.4. Whether the probe can be written as a
conformant record is a question for the std track, with the two points
the handover already has; the reason of the entry should say it in one
sentence.

#### F27. Does not block: two checks compare less than their text says

- `gate._holds`, kind `repeated_key`, compares the number of issues only;
  a finding of the right size that names one-visit subjects is explained
  (`pass2/newcode.py`). In the 20 real reports the rows are exactly the
  right ones (F4 above), and the report's table now says "the number,
  not the subjects".
- `gate.term_problems` accepts a milestone term in a disposition event
  (it joins the two codelists of DSDECOD) and does not look at COUNTRY or
  at the codelists of the study (AEREL, EXTRT, ARMCD).

Both are in the handover.

#### F28. Does not block: small things

- `GENERATOR` is still "gen-1a.1" although the same design and seed give
  other bytes than at `ec07012`; its own comment asks for a new name. No
  study of the old recipe was kept. In the handover.
- The new event of `no_exposure_end_date` is dated N + 2 days after the
  subject was lost to follow-up, after DM.RFPENDTC, with the epoch
  TREATMENT. CORE reports it as an event after the end of the study and
  says nothing about the epoch. In the handover.
- No test or gate check would see `env/lock.sh` break again; `bash -n`
  passed the broken script of pass 1 too.
- `scripts/clean_clone_gate.sh` still prints "clone kept ... until /tmp
  is cleared" (lesson 39 says so).

### The gate log, the report and the handover

The gate: `scripts/clean_clone_gate.sh gen-1a` on a clean clone of
`39ff635`, fresh install and fetch, 8 of 8 checks PASS, 908 tests passed
and none skipped, ten lines "planted defect" inside checks 4 to 7. The
three clauses of the gate text of PLAN.md section 13.5 are checks 5, 4 and
7; the environment check is first. Nothing the plan or ADR-005 asks of
gen-1a is missing from the eight checks. Two things pass in a weaker sense
than the words suggest, and the report says both: 38 of 562 rules of CORE
never ran (F24), and there is no TI dataset (for the owner).

The report against the log: all 91 lines that the section "The gate"
quotes are in the log; 1,825 findings (885 in the visible data, 940 in
the twins), 84 to 94 per dataset; 1,320, 220, 20, 80, 40 and 145 by kind;
18 rules with issues in every twin and 8 to 18 in the visible data; 510
files and 2,799 subjects per build; 32 or 35 pairs; 5,250 lines of
Python. All agree. The table "What the probes prove" is my own rerun.
"Limits" and the handover state F21 to F23 with my numbers, the open
reading of `not_before` of pass 1, and what the gate does not prove: that
both alternatives were built. A session that starts gen-2a from
`docs/state/gen.md` is told what it must not assume.

### What I could not check

- Anything under WSL: the gate run itself, `make lock`, the doctor, the
  second run of CORE and the run with eight planted defects. I read their
  logs and, for CORE, the 21 reports.
- The reports of the gate run proper, which are gone. The second run is
  held to it by its 45 lines, equal but for one folder name, and by the
  hash above.
- The CI runs on GitHub, the times of the lock, and the author's scratch
  run of 1,500 seeds.
- The engine. Whether a table differs is my reading of the templates;
  gen-2a decides by mutation. The reading of `not_before` named in pass 1
  is still open, and the handover says so.
- `terms_check` against the real terminology package; the gate log shows
  its result (95 terms, 709,791 values, 0 problems).

Verdict of pass 2: SIGNED. The gate passed on a clean clone of `39ff635`;
the four blocking findings of pass 1 are settled in that code; the list
of explained CORE findings holds on the 20 reports as its reasons say;
the report says what the logs show. Eight new findings (F21 to F28), none
blocking: all but F24, F26 and one point of F28 (no test for
`env/lock.sh`) are already in the report, the handover or a lesson; those
three are for the report, the std track and the first commit of gen-2a.
The two markers that the report keeps for this verdict were still open
when I read it.
