# Review of work package std-1: catalog, standard form, compiler, house standard

Rule R7 of PLAN.md: a fresh-context agent that did not write the work reviews
the diff against the plan. Correctness only, no style.

Commit reviewed: `9a4b09f829da6b99ff10ab68da33c5cace3fe14e` on branch
`track/std` ("std-1: catalog, standard form, compiler and house standard
(draft for N1)"), against `main` (`addde1a`). The diff has 215 files, 11393
insertions and 23 deletions.

## How the review was done

While I worked, another session changed the working tree of the worktree
without committing: `M src/specfirst/cli.py`, `M tests/unit/test_compile.py`,
and the new files `src/specfirst/compile/overview.py`,
`tests/unit/test_alternatives_on_tiny.py` and `docs/reports/std-1.catalog.md`.
None of that is part of this review. To review the commit and nothing else I
exported it with `git archive 9a4b09f` into a scratch folder outside the
repository (302 files, no CR bytes) and ran my experiments on the export, with
the Python environment of the worktree and `PYTHONPATH` set to the export.
The scratch folder was shared with that other session; I did not read its
files. I changed no file of the repository except this one. My first runs,
made in the worktree before I saw the uncommitted changes, wrote into the
ignored folder `build/` only.

## What I read

- `CLAUDE.md`; `PLAN.md` sections 2, 3 (evidence table), 4, 5, 6.5, 6.6, 12,
  13 (head) and 13.4, appendices A and B; `docs/decisions/ADR-000.md` item 7;
  `docs/decisions/ADR-004.md`; `docs/state/std.md`; `docs/lessons.md`.
- All of `src/specfirst/compile/*.py`, `src/specfirst/gates.py`, the std-1
  part of `src/specfirst/cli.py`, the diff of `schemas.py`.
- `standard/schemas/catalog-entry.schema.json`; `standard/catalog/catalog.yaml`,
  `sources.yaml`, `probes.yaml`; all 43 entries; all 43 compile templates; all
  43 phrasing files (96 alternatives, 288 phrasings); nine reading notes in
  full (23 alternatives).
- `standard/houses/open-default@1/`: `house.yaml`, `STANDARD.md`, the three
  parent specs, the five ARS templates, the four layout templates.
- `tests/unit/test_standard_form.py`, `tests/unit/test_compile.py` (as
  committed), `tests/defects/test_std1_checkers.py`, the diff of
  `tests/unit/test_gates.py` and `tests/unit/test_schemas.py`.
- In the fetch cache (read only): the cited places of 31 pinned citations
  with their context, the ARS schema and the example "Common Safety Displays",
  and the text of the Pilot 6 CSR and SAP for three citations.

## What I ran

Checks of the gate, on a copy of the exported commit on a Linux file system
(under `/tmp`, removed afterwards). Every command exited 0:

```text
$ specfirst catalog
catalog specfirst-m1 draft-1: 43 entries, 62 questions (entry and unit), 96 alternatives, 9 units, 46 probes
schema and cross-references: 0 problems
compile templates on their examples: 0 problems
probes: every pair of alternatives, every slot: 0 problems
phrasings and reading notes: 0 problems
parameters set and read: 0 problems
$ specfirst catalog --sources
43 entries, 0 without a public source
105 citations: 60 to pinned sources, checked on the fetch cache (44 with a text that must stand in the file); 45 to published documents, judged and not checked by script
public sources: 0 problems
$ specfirst catalog --roundtrip
245 statements rendered and parsed back, for 140 alternatives (entry, unit and alternative)
round trip decisions to statements to decisions: 0 problems
document round trip on 62 decisions: 0 problems
$ specfirst catalog --yamaa --run --tables
106 decision vectors (the base and one changed decision each), 106 compiled
  note: tfl.pvalue.format/four_decimals #1: shows only beside another decision, for example tfl.tests.include/anova_chisq #1
every alternative compiles and changes the compiled files: 0 problems
47 distinct sets of ADaM specs, 141 entry specs checked by yamaa (each with its house parent and one fragment per decision)
yamaa check: 0 problems
106 decision vectors, compiled by an earlier check
47 distinct sets of ADaM specs, 141 datasets built by yamaa on the tiny study of specfirst.compile.tiny (3 subjects; this shows that the specs run, not that their values are right)
yamaa run: 0 problems
106 decision vectors, compiled by an earlier check
ARS schema: project/jsonschema/ars_ldm.schema.json of the pinned source 'ars'
negative controls: 3 schema defects planted in the base ARS file, 3 reported
59 distinct ARS files with their layouts checked: schema, references, and that layouts and ARS name the same analyses
ARS schema and layouts: 0 problems
$ specfirst house
house standard open-default@1: 58 defaults, 4 decisions without a default, 3 parent specs, 4 table families
house standard: 0 problems
$ python -m pytest tests/unit/test_standard_form.py tests/unit/test_compile.py tests/unit/test_gates.py tests/unit/test_schemas.py tests/defects -q
219 passed in 22.35s
```

My own script compiled all 106 decision vectors twice, reading the catalog
again in between: `two compiles of all 106 decision vectors: True`.

The same slow command with its build folder on a Windows drive (the worktree
on `/mnt/d`, and the export on `/mnt/c`), traceback shortened:

```text
$ specfirst catalog --yamaa --run --tables
47 distinct sets of ADaM specs, 141 entry specs checked by yamaa (each with its house parent and one fragment per decision)
yamaa check: 0 problems
106 decision vectors, compiled by an earlier check
  File ".../src/specfirst/compile/checks.py", line 765, in yamaa_run
    result.save()
yamaa.Error: cannot save ADSL: build/gates/std-1/compiled/v001/adam/adsl.yaml:25:3: the engine refused the operation in its output step: target_changed [engine_rejected]
exit=1
```

In the worktree (with the other session's uncommitted files present):

```text
$ python -m pytest tests/defects -q
45 passed in 156.57s (0:02:36)
$ python -m pytest -m "not evidence" -q
406 passed, 8 deselected in 219.86s (0:03:39)
```

I did not run `scripts/clean_clone_gate.sh std-1` or the whole
`specfirst gate std-1` myself. The author's log of the clean clone gate is in
the ignored folder (`build/gates/std-1/clean-clone.log`): "gate std-1 at
commit 9a4b09f829da6b99ff10ab68da33c5cace3fe14e (clean)", twelve checks PASS,
"GATE std-1: PASS", the clone under `/tmp`.

My own experiments (scripts in my scratch folder, not in the repository; each
finding says how to repeat it):

- Standard form: 9317 statements with random and hostile slot values (texts
  that hold separators, other statements and template literals; names and
  numbers taken from the literals of other templates), rendered and matched
  against every template: 0 not unique, 0 not exact. 21 hand-made statements
  and 6 values: every one that is not a canonical statement or value was
  refused. Accepted were a changed number (another valid decision), the
  float 0.1 + 0.2 (it renders and reads back exactly) and the tables of
  finding 13. 11 changed documents: findings 9 and 14.
- 8 planted defects on copies of the catalog and house: the table after the
  findings.
- Values on hand-made SDTM data (the tiny study, changed per case), built
  with yamaa from compiled specs: 66 expectations read off the statements of
  16 entries, all met; the cases of findings 3 and 4; the window, baseline
  and study day cases of 7 more entries, listed under "Checked and found
  correct".
- All 106 compiled decision vectors: my own reference checks on the 38
  distinct ARS documents (0 problems), and a comparison of the recorded
  `binds` with what each decision changes (finding 5).

Verdict: PASS

The three claims of the gate text of PLAN.md section 13.4 hold at this commit,
and nothing is frozen or started that must wait for the owner. The verdict is
PASS only because no finding is blocking by the definition I was given. Ten
findings are major. Findings 3, 4, 6, 9 and 10 touch what the owner approves
at N1 (definitions, defaults, probe recipes, the document form, the house
templates) and should be settled before that node.

## Findings

### 1. major: the state file claims a passed review and names evidence that the commit does not hold

`docs/state/std.md` lines 8 to 11 list std-1 under "Passed" with "Evidence:
docs/reports/std-1.md and std-1.gate.log. Review:
docs/reports/std-1.review.md." At commit 9a4b09f `docs/reports/` holds
`README.md` and the three base-0 files only. The report that rule R8 and
section 2.4 ask for (the commands and their output) is not in the diff I was
given, so I could not check its claims; and the review did not exist. Write
"Passed" after the review, and commit the report and the gate log with it.

### 2. major: the gate check "yamaa run" cannot pass in a checkout on a Windows drive

`src/specfirst/compile/gate.py` line 94 puts the build folder into the
checkout (`build/gates/std-1/compiled`); `checks.yamaa_run` (checks.py line
765) saves each dataset there. With that folder on a Windows drive under WSL,
yamaa refuses to save the first dataset (`target_changed [engine_rejected]`,
output above), and `run_problems` does not catch the error. I saw it three
ways: `specfirst catalog --yamaa --run --tables` in the worktree on `/mnt/d`;
the same on the isolated export on `/mnt/c`; and `checks.run_problems` on the
base vector alone, which returns `([], 3)` with the folder under `/tmp` and
raises with it on `/mnt/c`, twice. The checkout of this project is on a
Windows drive (CLAUDE.md, gotchas), so check 9 of `specfirst gate std-1`, and
`specfirst catalog --run` as CLAUDE.md names it, fail there; the gate passes
only in the clean clone, which lives under `/tmp`. Neither CLAUDE.md nor
`docs/lessons.md` says so. I did not run the whole gate in the worktree; the
check is the same function.

### 3. major: one partial exposure date can remove the treatment date of a dosed subject, depending on how its text sorts

Entries `trt.start.source`, `trt.end.source`, `trt.date.imputation`.
`templates/trt.start.source.yaml` lines 13 and 22 take `MIN(EX.EXSTDTC)` and
`templates/trt.end.source.yaml` lines 11, 20 and 29 take `MAX(...)` of the
date texts; the date is completed afterwards. A partial text that is the
start of a complete one sorts before it. Under the house defaults
(`first_ex_with_dose`, `last_ex_end_date`, `not_completed`), subject S1 of
the tiny study has two complete records, 2024-03-10T08:00 to 2024-03-31 and
2024-04-01 to 2024-04-20. With a third dosed record:

```text
third record starts 2024-03 : TRTSDT=None       TRTEDT=2024-04-20 SAFFL=N
third record starts 2024-04 : TRTSDT=2024-03-10 TRTEDT=2024-04-20 SAFFL=Y
third record starts 2024    : TRTSDT=None       TRTEDT=2024-04-20 SAFFL=N
third record ends   2024-04 : TRTSDT=2024-03-10 TRTEDT=2024-04-20 SAFFL=Y
third record ends   2024-05 : TRTSDT=2024-03-10 TRTEDT=None       SAFFL=Y
```

In rows 1 and 3 a subject with a complete first dose date leaves the safety
set, loses baseline weight and has no treatment-emergent event. The statement
"The treatment start date is the earliest start date of an exposure record
with a dose" does not say that; "A partial exposure date ... gives no
treatment date" holds in rows 1, 3 and 5 and not in rows 2 and 4. The admiral
source the entry cites drops records without a usable date and takes the
first of the rest. The probe `partial_exposure_date` plants only the case in
which the partial date is the earliest. Decide the rule (ignore partial
dates, or let any partial date void the result), state it in the definition,
and compute it on dates, not on texts.

### 4. major: `demo.baseline.record/last_on_or_before_first_dose` does not do what its definition says on a tie

Definition (entry, and STANDARD.md [3/s3]): "Of several values on the last
date the highest VSSEQ is taken." The fragment
(`templates/demo.baseline.record.yaml` line 19) orders by
`[VS.VSDTC, VS.VSSEQ]` and keeps the last, so the latest date and time text
wins, and a value without a time sorts before a timed value of the same day.
Tiny study, S1, two weights on the first dose date: VSSEQ 9 at
`2024-03-10T07:00` (71.0) and VSSEQ 11 at `2024-03-10` (73.0). Built:
`WEIGHTBL = 71.0`; the definition gives 73.0. Either the definition or the
order is wrong.

Two related points for the owner, both minor. Appendix B proposes "last
before first dose" for this entry; the delivered default is "on or before the
treatment start date", and ADR-004 item 7 does not list the change. And the
two baseline defaults disagree: with a weight timed 09:00 on the first dose
date (dose at 08:00), ADSL has `WEIGHTBL = 75.0` (that value) while ADVS
flags the screening value 70.0 as the baseline of WEIGHT.

### 5. major: the `binds` the compiler records are neither complete nor sound

PLAN.md 4.2 and 4.3: `binds` are filled by the compiler and are the `decides`
edges. For each of the 62 decisions I compared the ARS elements and layout
parts that differ between the base vector and each alternative with the
recorded binds (`compile.json`).

- 11 decisions change elements they do not bind. `tfl.output.include` binds
  nothing at all in the four families (it removes 16 to 30 elements);
  `tfl.population` does not bind the analysis sets; `tfl.tests.include` not
  the test methods; `tfl.ae.summary.rows` not the data subsets.
- 13 decisions bind elements that no alternative changes.
  `tfl.quantile.definition` (tfl-demographics) binds the categorical
  summaries `An_DM_SEX_Summ`, `An_DM_AGEGR1_Summ` and others;
  `tfl.denominator` binds the continuous summaries; `tfl.columns.total` binds
  the analyses that are not total. Cause: `compiler.py` lines 361 to 381
  record the names read by a whole template member (a `$for` over all rows)
  for every element that member yields.
- ADaM binds name working columns that are not in the dataset
  (`ae.teae.end` binds `adam:ADAE._TEEND`), where section 4.3 shows
  `adam:ADAE.TRTEMFL`; `bds.eot.record` binds `adam:ADVS._EOTRN` only. This
  may be intended, but ADR-004 does not say it.

No check of the gate looks at binds beyond their form. std-2 and std-3
predict changed cells from these edges.

### 6. major: the probe `output_shape` does not separate the alternatives of `tfl.columns.arms`

`standard/catalog/probes.yaml` lines 16 to 38: "No planted record. The
alternatives ... give outputs with different rows, columns or cell text for
any data", `separates: tfl.columns.arms: all`. "Ascending order of dose,
with placebo first" and "the order in which the protocol lists the arms" give
the same columns whenever the protocol lists the arms in that order, which is
the usual case (and the pilot's). It needs a design in which the two orders
differ; nothing says so, and the generator will plant nothing. Rule 5 of
section 5.2 (a probe that separates each alternative from each sibling) is
not met for this entry. The checker cannot see it: a structural probe may
claim `all`. Two more claims of the same probe hold only beside another
decision: `tfl.pvalue.format` (only when `tfl.tests.include` is not `none`;
ADR-004 says this) and `bds.eot.record` (only when `tfl.vs.scope` lists the
visit End of Treatment).

### 7. major: the ARS reference check misses wrong references of the kind it exists for

`checks.ars_problems` (checks.py line 786) checks the schema and that named
IDs exist. Two planted defects of mine pass the coverage, ARS schema,
reference and layout checks with 0 problems (the first also the house and
parameter checks):

- In `ars/ae-summary.yaml` the denominator analysis of the percentage is set
  to `An_AESUM_N` for both variants. The Total analysis `An_AESUM_ANY_Tot`
  (grouping `Grp_Total_AESUM`) then takes its denominator from the per-arm
  count. The CDISC example states the rule: "The referenced analysis should
  have the same analysis set and subject grouping(s)".
- In `ars/common.yaml` the denominator relationship names
  `operationId: Mth_Count_x`, an operation no method defines.

The delivered templates do not have these defects: my own check of both
rules, and of the method behind each referenced operation, found 0 problems
in the 38 distinct ARS documents.

### 8. major: nothing checks that an alternative computes what its statement says, except for the base vector

Planted: in `templates/ae.teae.end.yaml`, `last_dose_plus_days`,
`ASTDT <= _TEENDDT` becomes `ASTDT < _TEENDDT`. The definition says the last
day of the window is inside. Every static checker, the coverage check,
`yamaa check` and `yamaa run` report 0 problems. At this commit only
`test_the_base_decisions_build_the_tiny_study` compares values with
statements, and only for the base vector. `docs/state/std.md` says this
openly ("proven to run ... not to give the right values"), and the gate text
does not ask for more; but section 5.2 rule 2 rests on the templates being
right, and findings 3 and 4 are what this hole lets through. (The other
session's uncommitted `tests/unit/test_alternatives_on_tiny.py` may close
it; it is not part of this commit and I did not read it.)

### 9. major: `parse_document` drops a statement line that does not start in column 1, without a word

`standard_form.py` lines 349 to 353: a line that is not an anchored statement
raises only when it starts with `[`; any other line is skipped. A document of
10 rendered decisions in which the line `[2/s3] Treatment emergence has no
end date.` gets one leading space, a list marker (`- `) or bold marks parses
without an error to 9 decisions. Section 6.6 says a parser recovers every
decision of a standard-form document. Refuse any line that holds an anchor
and is not a statement. (The gate cannot show this: it parses only what it
rendered.)

### 10. major: the result patterns in the compiled ARS file do not follow the decisions on decimals and p-values

`ars/common.yaml` gives every operation a fixed `resultPattern` (mean
`XX.X`, SD `XX.XX`, p-value `X.XXX`). `tfl.decimals.rule` and
`tfl.pvalue.format` change the layout file only:

```text
decimals stated (mean 2, sd 3): ARS mean/sd/min ['XX.X', 'XX.XX', 'XX'], layout {'rule': 'stated', 'mean': 2, 'sd': 3, 'median': 2, 'range': 1}
p-value four decimals         : ARS X.XXX, layout {'decimals': 4, 'below': '<0.0001'}
files that differ from the default: layout/tfl-demographics.json only
```

So one compiled kit states two display precisions, and under the default
`relative_to_data` the fixed pattern is right only for whole-number data.
The entry cites the ARS pattern as its source ("result patterns fix the
decimals of each operation"). Compile the patterns, or drop them from the
ARS file and say in ADR-004 that the layout alone carries display formats.
In the same vein, `tfl.demog.stats` changes only the layout: the ARS method
`Mth_ContSumm` always has the operations Q1 and Q3, also for the vital signs
table, which never shows them.

### 11. minor: citations that are wrong or claim too much

- `pop.safety.rule` and `pop.safety.grouping` cite ICH E9 "section 5.2.3".
  From memory (the session did not fetch the document, and I could not open
  it): 5.2.3 is "Roles of the Different Analysis Sets"; the sentence on
  subjects who received at least one dose is in section 6.3, the E9 glossary
  has no entry for a safety analysis set, and I know no sentence of E9 that
  says safety is analyzed by treatment received.
- `demo.race.pooling` cites the CSR's origin categories (E15) for pooling.
  E15 is a regrouping by race and ethnicity, not a pooling below a count; no
  cited source supports `pooled_below_count`.
- Section 5.2 rule 5 asks for a public source per alternative; the checker
  and the gate text ask per entry. No cited source supports
  `ae.teae.end/end_of_study` or
  `tfl.ae.socpt.sort/descending_frequency_highest_dose`.
- `ae.start.imputation` cites a yamaa benchmark that completes with day 15,
  not with the first day; it supports `not_before` only.
- `pop.efficacy.rule`: the pilot's EFFFL asks for post-baseline records of
  two measures and for no baseline value; the citation supports half of
  `baseline_and_postbaseline`.

The other pinned citations I opened support their entries (list below).

### 12. minor: a missing `tfl.output.include` compiles as "not included"

`compiler.py` line 335. A decision vector without `tfl.output.include` for
tfl-ae-soc-pt compiles without a problem and leaves the table out. A missing
ADaM decision is refused ("ADVS: no value for bds.eot.record"), and so is a
missing `tfl.population`. Rule 4 of section 5.2: never guess.

### 13. minor: record slots accept tables that contradict themselves

The parser accepts as valid decisions: a protocol window with `low` above
`high`, two overlapping windows, two windows with one visit name, an arm
code decoded twice, age cuts that do not ascend. The compiler compiles
without a word: a window with `low` above `high`, overlapping windows (by
the order of the compiled case list the first one wins), a target day
outside its window, and midpoint windows whose first target is day 1 (the
first window starts on day 2). Cuts and midpoint targets that do not ascend
and an arm code decoded twice are refused, but only at compile time.

### 14. minor: the parser ignores the `Catalog:` line and a second `Document:` line

A document rendered for `specfirst-m1 draft-1` parses the same when the line
names another catalog or is missing; a second `Document:` line is skipped.
The catalog version changes at N1.

### 15. minor: places where ADR-004 or the notes are not accurate

- "tfl.denominator ... apply to the table families that show such values":
  the two adverse event tables show percentages and have a fixed
  denominator; `tfl.denominator` applies to the demographics table only.
- The notes of `pop.safety.rule` say "A subject is randomized as decision
  pop.randomized.rule defines it". The fragment uses RANDFL (the planned arm
  code), not the randomized set of that decision; under
  `randomized_with_postbaseline` the two differ.

### 16. minor: defaults and parent specs a statistician may not expect

None of these contradicts its statement; each follows from the definitions
and notes. The owner should see them before N1.

- A record on the first dose date timed after the dose is neither baseline
  nor post-baseline under the defaults: no analysis visit, no change (tiny
  study, S1, SYSBP at 09:00). Without a collected time it is baseline.
- The start rule counts records with a dose, the end rule counts any record:
  with a zero-dose record that ends 2024-03-02 and a dosed record from
  2024-03-05 with no end date, TRTSDT is 2024-03-05 and TRTEDT is 2024-03-02.
- `first_day_of_month` completes end dates with the first day too.
- With `ae.teae.start/at_or_after_first_dose_time`, a partial start that
  `ae.start.imputation` moved to the first dose date is not
  treatment-emergent when the dose has a time (it counts from 00:00).
- ADVS has one parameter per VSTESTCD: position and time point (VSPOS,
  VSTPT) are not read, so of repeated measurements of one visit one record
  is analyzed. PARAM is VSTEST without the unit.
- AOCCFL, AOCCSFL and AOCCPFL take the first event by AESEQ, not by start
  date. BMI assumes kg and cm; no unit is read.
- The age groups of the default are those of the pilot (below 65, 65 to 80,
  above 80).

## My planted defects

| # | Planted | Result |
| --- | --- | --- |
| P1 | a name slot whose value can spell another statement of the catalog (`Study day 1 is ... ({variable}).` beside `(DM.RFSTDTC)`) | found: round trip, "ambiguous" |
| P2 | Total percentage with the per-arm denominator | not found (finding 7) |
| P3 | relationship to an operation that does not exist | not found (finding 7) |
| P4 | `<=` to `<` at the end of the emergence window | not found (finding 8) |
| P5 | an alternative's own citation with a text that is not in the pinned file (real fetch cache) | found: sources |
| P6 | a phrasing that says "after the first dose" and keeps its slot | not found; the wording check is on slots only, as section 6.6 has it |
| P7 | a layout row that shows the per-arm analysis in the Total column | found: "no layout shows the analysis" |
| P8 | window tables that contradict themselves | not found (finding 13) |

## Checked and found correct

- Scope. 43 entries (appendix B has 46; four left out with reasons, one
  added), each with alternatives, statements, a default or none, sources, a
  compile template, phrasings, reading notes and probes; the compiler; the
  renderer and parser; the house standard with STANDARD.md, three parent
  specs, ARS and layout templates. The catalog version is `draft-1`, ADR-004
  is "proposed", the four schema points of ADR-000 item 7 carry
  recommendations and none is applied. No version 0 schema changed
  (`git diff main..9a4b09f -- standard/schemas` adds two files). No std-2
  code (no rebuild, no mutation runner). `third_party/`, `PLAN.md` and `env/`
  are untouched. CLAUDE.md has 53 lines.
- Gate text. Round trip exact for every alternative and unit; compiled specs
  pass `yamaa check` (141 entry specs, 47 distinct sets); 59 distinct ARS
  files fit the pinned schema, and the three negative controls are reported;
  every entry names at least one source of `sources.yaml`. No check passes on
  an empty loop: a failed compile empties the variant list and the three
  compiled checks then fail; the dedupes are by content hash. Each checker
  function has at least one planted-defect test of a real kind (the run
  check plants the case of lesson 10). Branches without a planted defect:
  phrase prefixes, a default per unit, fewer than 40 entries, an unlisted
  entry file, note headings, "never compiled", the document round trip.
- Standard form. No template literal holds a double quote, so a text slot
  cannot spell literal text; my fuzz and attacks found no statement that two
  decisions fit and no value that renders and does not parse back. Refused:
  `30.0`, `05`, a value outside its limits, a repeated or unknown list item,
  another output phrase, typographic quotes, a trailing or double space, a
  changed word, a whole float, a bool. A changed number is another valid
  decision, as it must be; the citation quote is the guard for that.
- Compile templates, by reading all 43 and by building: treatment emergence
  start (date and time rules), the end window at N and N + 1 days, end of
  study on the day and the day after, the three imputation rules with a
  partial start in and before the month of the first dose and with a year
  only, the related list, both safety rules with a dosed subject who is not
  randomized, both randomized rules, both efficacy rules, the three start
  sources, the three end sources (with and without any end date), the
  end-of-study record by subcategory, the three sources of actual treatment,
  the arm code map with a code it does not name, race pooling at the count,
  the three age group rules at the cut points, BMI derived and collected,
  baseline weight at a visit; the three baseline rules with a value before
  and after the dose time and with only an unscheduled value; protocol,
  midpoint and nominal windows with a day in a gap and a day on the tie;
  the three tie-break rules with a missing value in the window; unscheduled
  records excluded; study day from DM.RFSTDTC (no day 0); the
  end-of-treatment record with BASE and CHG. A visit name with an apostrophe
  compiles and runs.
- ARS. Denominators are the count of subjects of the analysis set by the
  same column grouping, also for Total; numerators refer to their own
  analysis; the Total analyses use a grouping of one group (`NOTIN ""`, or
  the control as well); the treatment variable is TRT01A only for the safety
  set with `pop.safety.grouping/actual`, else TRT01P; comparisons use
  `resultsByGroup: false`; the comparators are in the schema's list; the
  list of contents names every output and analysis. Each table decision
  changes the ARS file, a layout file or both.
- Citations. Of the pinned ones I opened, these support their entries:
  `ae.related.values`, `ae.teae.end`, `ae.teae.start` (both),
  `bds.baseline.rule` (the yamaa verb; SAP: "collected at Week -2 (Visit
  1)"), `bds.eot.record`, `bds.unscheduled.use`, `bds.window.table` (both),
  `bds.window.tiebreak`, `date.studyday.origin`, `demo.age.groups` (both),
  `demo.baseline.record`, `demo.bmi.rule`, `disp.status.record`,
  `pop.randomized.rule`, `pop.safety.rule` (Pilot 7), `pop.safety.grouping`
  (ARS), `tfl.denominator`, `tfl.percent.format` (CSR Table 12-1, drawn from
  Table 14-5.01, prints a zero count without a percentage), `tfl.population`
  (CSR: "all ITT subjects"), `tfl.quantile.definition`, `tfl.rounding.rule`,
  `trt.actual.source`, `trt.date.imputation`, `trt.end.source`,
  `trt.planned.source`, `trt.start.source`. From memory, the ICH E3 sections
  (11.1, 11.2, 12.5, 14.1, 14.3.1), ICH E9 5.2.1 and 5.2.2, the ADaMIG,
  OCCDS and SDTMIG variables, the admiral arguments and the SAS and R
  quantile definitions are cited correctly.
- Clean room. No file other than code, YAML, Markdown and JSON was added; no
  study data; the pilot appears only as paths and titles of citations;
  variable names are those of ADaMIG, OCCDS and SDTMIG, EFFFL and the
  baseline variables those of the public pilot; working names start with an
  underscore. No non-ASCII byte and no CR in the files of the diff.
- House standard. STANDARD.md equals its rendering and parses back to the 58
  defaults; the four decisions without a default are listed. Variable names
  and labels are those of ADaMIG and OCCDS; the values of EOSSTT are the
  controlled terms; DTYPE LOV is a controlled term as far as I recall.
- Phrasings: I read all 288; each says what its statement says. Reading
  notes: the nine I read agree with the entries, `bds.baseline.rule` with
  the definition that changed late among them.
- Determinism: compiling all 106 vectors twice gives the same bytes; the
  order of the records does not matter (the author's test); no clock in the
  compiler.

## What I could not check

- The published documents themselves (ADaMIG, OCCDS, SDTMIG, ICH E3, ICH E9,
  the FDA guide, admiral): judged from memory. I could not judge the five
  citations of the FDA guide at all.
- Whether the layout files mean what they say: layout draft 0 has no grid
  builder yet. Whether the probes separate on data (P4) and whether the
  compiled specs reproduce the pilot: std-2 and gen-2.
- The clean clone gate and the whole `specfirst gate std-1`: not run by me.
- The gate report `docs/reports/std-1.md`: not in the commit (finding 1).

Independent reviewer (fresh-context agent), 2026-11-11

## Second pass (commit 4002fc1)

Commit reviewed: `4002fc1fa67609d50a744bee6806be6cef66d9c0` on `track/std`
("std-1: fixes from the first pass of the independent review"). Since
9a4b09f the branch has three commits: 4c97d1c (catalog overview, 40 value
cases, the first-pass review), 36f8cf1 (merge of main with real-1) and
4002fc1 (the fixes). I read the diff `9a4b09f..4002fc1` of
`src/specfirst/compile`, `standard`, the std-1 tests, ADR-004, the state
file, the lessons, CLAUDE.md and `third_party/SOURCES.md`, and the new
`tests/unit/test_alternatives_on_tiny.py`. The code of real-1 that came with
the merge is not std-1's and I did not review it. The worktree was clean at
4002fc1 during this pass. I ran the gate in the worktree and my experiments
on a `git archive` export of 4002fc1 in my scratch folder. The text of the
first pass above is unchanged.

### What I ran

In the worktree on `/mnt/d` (clean, HEAD 4002fc1):

```text
$ specfirst catalog
catalog specfirst-m1 draft-1: 43 entries, 62 questions (entry and unit), 96 alternatives, 9 units, 50 probes
schema and cross-references: 0 problems
compile templates on their examples: 0 problems
probes: every pair of alternatives, every slot: 0 problems
structural probes separate for any data: 0 problems
phrasings and reading notes: 0 problems
parameters set and read: 0 problems
$ specfirst catalog --sources
43 entries, 0 without a public source
104 citations: 59 to pinned sources, checked on the fetch cache (44 with a text that must stand in the file); 45 to published documents, judged and not checked by script
public sources: 0 problems
$ specfirst catalog --roundtrip
243 statements rendered and parsed back, for 140 alternatives (entry, unit and alternative)
round trip decisions to statements to decisions: 0 problems
document round trip on 62 decisions: 0 problems
$ specfirst house
house standard open-default@1: 58 defaults, 4 decisions without a default, 3 parent specs, 4 table families
house standard: 0 problems
$ specfirst catalog --yamaa --run --tables
compiled files and built datasets: /tmp/specfirst-std1-_pt3ufd1 (removed when the command ends)
106 decision vectors (the base and one changed decision each), 106 compiled
  note: tfl.pvalue.format/four_decimals #1: shows only beside another decision, for example tfl.tests.include/anova_chisq #1
every alternative compiles and changes the compiled files: 0 problems
47 distinct sets of ADaM specs, 141 entry specs checked by yamaa (each with its house parent and one fragment per decision)
yamaa check: 0 problems
47 distinct sets of ADaM specs, 141 datasets built by yamaa on the tiny study of specfirst.compile.tiny (3 subjects; this shows that the specs run, not that their values are right)
yamaa run: 0 problems
negative controls: 3 schema defects planted in the base ARS file, 3 reported
59 distinct ARS files with their layouts checked: schema, references, and that layouts and ARS name the same analyses
ARS schema and layouts: 0 problems
$ python -m pytest tests/unit/test_standard_form.py tests/unit/test_compile.py tests/unit/test_alternatives_on_tiny.py tests/unit/test_gates.py tests/unit/test_schemas.py tests/defects -q
281 passed in 251.28s (0:04:11)
```

Every command exited 0, and no folder `/tmp/specfirst-std1-*` was left.
Then the whole gate, in the worktree on the Windows drive:

```text
$ specfirst gate std-1
gate std-1 at commit 4002fc1fa67609d50a744bee6806be6cef66d9c0 (clean)
PASS  environment          0.4 s
PASS  pins                 0.3 s
PASS  lint                 0.4 s
PASS  unit tests         239.2 s
PASS  catalog             10.4 s
PASS  public sources       0.3 s
PASS  round trip           0.7 s
PASS  yamaa check        102.1 s
PASS  yamaa run           30.1 s
PASS  ARS schema           0.7 s
PASS  house standard       0.9 s
PASS  ASCII                3.2 s
GATE std-1: PASS
```

On the export: the first-pass experiments again (the fuzz of 9317
statements: 0 problems; the 66 value expectations: 64 met, and the two that
differ follow the changed statement of `trt.end.source`), and the new ones
named under each finding.

### The findings of the first pass

| # | First pass | Status at 4002fc1 |
| --- | --- | --- |
| 1 | state file names evidence the commit lacks | open, as announced: `docs/state/std.md` lines 8 to 11 are unchanged and `docs/reports/` has no `std-1.md` and no `std-1.gate.log`. The author will commit them with this review after the final gate. Nothing for me to verify yet |
| 2 | "yamaa run" on a Windows drive | fixed |
| 3 | partial exposure dates | partly fixed; the rest is finding 17 |
| 4 | baseline order against its definition | fixed, by changing the definitions |
| 5 | binds neither complete nor sound | partly fixed; the rest is finding 18 |
| 6 | probe `output_shape` and `tfl.columns.arms` | fixed in the catalog; the new check is weaker than its name (finding 19) |
| 7 | ARS reference check | fixed |
| 8 | no value check of alternatives | partly fixed; the rest is finding 20 |
| 9 | statement lines dropped by the parser | fixed for every line that holds an anchor; a rest in finding 21 |
| 10 | result patterns in the ARS file | fixed |
| 11 | citations | fixed; three alternatives are now listed as unsourced, for the owner |
| 12 | missing `tfl.output.include` | fixed |
| 13 | tables that contradict themselves | fixed |
| 14 | `Catalog:` and `Document:` lines | fixed |
| 15 | ADR-004 and notes | fixed |
| 16 | defaults a statistician may not expect | listed for the owner, in part |

Evidence, finding by finding:

- 2. `gate._variants` builds in a new folder under the system's temporary
  folder; the slow command and the whole gate above ran in the worktree on
  `/mnt/d`, with 141 datasets and 0 problems. `checks.run_problems` with
  its folder on `/mnt/c` now returns the problem `base: ADSL: run refused:
  cannot save ADSL: ...` where it crashed before. Lesson 20 and a CLAUDE.md
  gotcha say it. No test plants a refusal.
- 4. `demo.baseline.record`, `bds.baseline.rule` and `bds.window.tiebreak`
  now say: latest by the collected date and time, a value without a time
  before the timed values of its day, then the sequence number. My case of
  the first pass gives `WEIGHTBL = 71.0` (the timed value, VSSEQ 9), which
  is what the new text says, and ADVS flags the same record. ADR-004 item 7
  lists the changed default wording and that ADSL and ADVS follow two
  baseline rules.
- 6. `tfl.columns.arms` has the probe `arms_listed_out_of_dose_order` of
  the new kind `design`; `bds.eot.record` and `tfl.pvalue.format` have
  structural probes with `needs`. The state file tells gen-1 what a design
  probe is.
- 7. My two planted defects are found now: "analysis An_AESUM_ANY_Tot:
  'An_AESUM_N' has other subject groupings" and "relationship
  Mth_CatSumm_pct_DEN: the operation 'Mth_Count_x' is not defined". A third
  one (the SOC and PT percentages divided by the count of subjects with any
  event) is found too: "'An_AESOCPT_Any' has no operation 'Mth_Count_n'".
  Four planted tests were added. No false problem on the 59 ARS files.
- 9, 14. A statement line with a leading space, a tab, a list marker, a
  quote marker or bold marks is refused ("not an anchored statement"), and
  so is an anchor with a space or a capital S. A `Catalog:` line of another
  catalog or version, a missing one, an indented one and a second
  `Document:` line are refused.
- 10. The compiled ARS file has no `resultPattern`. Under the default
  statistics the methods are `Mth_Count` (1 operation), `Mth_CatSumm` (2)
  and `Mth_ContSumm` (6); with quartiles the demographics summaries use
  `Mth_ContSummQ` (8) and the vital signs table keeps `Mth_ContSumm`.
  ADR-004 item 5 says the layout alone holds display formats.
- 11. `pop.safety.rule` cites ICH E9 section 6.3; `pop.safety.grouping` no
  longer cites E9; `pop.randomized.rule` names what 5.2.1 says;
  `sources.yaml` records that E9 was read. This agrees with what I wrote
  from memory. The CSR citation of `demo.race.pooling` is gone, and
  `catalog.yaml` lists three `unsourced_alternatives`. Rule 5 of section
  5.2 is thereby not met for these three, openly; the owner decides at N1.
  No document was committed.
- 12. A decision vector without `tfl.output.include` for one family is
  refused: "tfl-ae-soc-pt: no value for tfl.output.include".
- 13. Refused now, when rendered and when parsed: a window with `low` above
  `high`, overlapping windows, windows out of order, a target outside its
  window, two windows or visits with one name, a first midpoint target on
  day 1, targets that do not ascend, an arm code decoded twice, cuts that
  do not ascend.
- 15. ADR-004 says which table families each display decision applies to;
  the notes of `pop.safety.rule` say that the rule of the randomized set
  does not enter.
- 16. The state file ("Known limits") lists the record timed after the dose
  on the first dose day, the parameters of ADVS, the occurrence flags and
  the units of BMI, and the two baseline rules. The end date now reads
  dosed records only, so my example of an end before the start is gone.
  Not listed: `first_day_of_month` completes end dates with the first day
  too; a partial start moved to the first dose date is not emergent under
  the time rule when the dose has a time; the default age groups are the
  pilot's.

### New findings

#### 17. major: a partial exposure date in the SDTM form with hyphens for the unknown part still removes the treatment date (rest of finding 3)

The fix works for the forms `2024-03` and `2024`. With the two complete
records of S1 and a third dosed record that starts `2024-03` and ends
`2024-05`: `TRTSDT=2024-03-10`, `TRTEDT=2024-04-20`, `SAFFL=Y` under
`not_completed`, and 2024-03-01 and 2024-05-01 under `first_day_of_month`.
The templates decide what a complete date is by the text patterns
`LIKE '%-%-%'` and `LIKE '%-%'` (`templates/trt.start.source.yaml`,
`templates/trt.end.source.yaml`). SDTM writes an unknown middle part with
hyphens, and those texts pass the patterns and sort first or last:

```text
third record starts 2024---15 (month unknown): TRTSDT=None       TRTEDT=2024-04-20 SAFFL=N  (both alternatives)
third record starts --03-05 (year unknown)   : TRTSDT=None       TRTEDT=2024-04-20 SAFFL=N  (both alternatives)
third record ends 2025---01 (month unknown)  : TRTSDT=2024-03-10 TRTEDT=None       SAFFL=Y  (both alternatives)
third record ends 2024-05--T10:00            : TRTEDT=None under not_completed, 2024-05-01 under first_day_of_month
```

The definition says the dates are taken "from the exposure dates that have a
year, a month and a day". It is the defect of finding 3 for rarer texts: a
dosed subject with a complete first dose date leaves the safety set. Decide
whether a text is a complete date by reading it as a date, not by counting
hyphens.

Two smaller points in the same templates, both minor. Under `not_completed`
with `ds_date_when_ex_missing`, a subject whose only dosed record starts
`2024-03` and has no end date gets `TRTSDT=None`, `SAFFL=N` and
`TRTEDT=2024-05-02` from the disposition record; the definition says that
date "is taken only for a subject with a treatment start" (the template
asks for `_TRTSDTCM`, the candidate with a known month, not for the decided
start). And of two dosed records on the first dose day, `2024-03-10` and
`2024-03-10T08:00`, the text without a time is the minimum:
`TRTSDTM=2024-03-10 00:00:00`, `TRTSTMF=H`, so the collected time of the
first dose is not used.

#### 18. major: the binds are complete only against the example values written in the catalog (rest of finding 5)

`compiler.bind_tables` binds what another alternative or another example of
the entry changes or removes. Against that measure it is exact: for all 62
decisions of the base vector, 0 with a changed element that is not bound and
0 with a bound element that never changes; the same binds for another order
of the records; the compiled files untouched. But a list slot has more
values than its examples:

```text
base vector, tfl.demog.rows changed to [RACEGR1] (not an example): changes 18 elements, 16 bound;
  changed and not bound: An_DM_AGE_Summ, An_DM_AGE_Summ_Tot, An_DM_SEX_Summ, An_DM_SEX_Summ_Tot, Grp_SEX
base vector, tfl.ae.summary.rows changed to [SERIOUS]: changed and not bound: An_AESUM_ANY, An_AESUM_ANY_Tot
study with tfl.demog.rows = [AGE, SEX]:  ARS binds [], layout binds [layout:tfl-demographics/rows]
study with tfl.ae.summary.rows = [ANY]:  ARS binds [], layout binds [layout:tfl-ae-summary/rows]
```

A decision that alone decides which analyses exist binds none of them when
every example of the catalog holds the same rows, because a change to an
example can then only add rows. The `decides` edge of section 4.2 misses
the analyses, the path from a printed number to "the decisions behind it"
(P3) lacks this decision, and an edit to a value outside the examples
changes cells the graph does not predict (the gate of std-3). The binds of
a kit also change when somebody edits an example in the catalog. For the
alternatives themselves (P4) the binds are complete. This does not touch
what the owner approves at N1; it should be settled before std-2 relies on
it, for example by also removing each item of a list.

A note on cost, not a finding: `specfirst compile` runs `bind_tables` each
time; for the base vector it took 38 seconds on my export on a Windows
drive.

#### 19. minor: the new check of structural probes cannot fail on the defect of finding 6

`checks.structural_probe_problems` asks that the two alternatives compile to
different table files. Its label in the gate log is "structural probes
separate for any data". I planted the defect of finding 6 again
(`output_shape` separates `tfl.columns.arms: all`, the design probe
removed): 0 problems, because the two column orders give different layout
files and still the same table for the usual design. The check does find a
structural claim on `bds.eot.record` (my plant) and on `tfl.pvalue.format`
(the author's planted test). A `needs` text is not checked: with "Nothing
at all." the claim passes. Name the check for what it shows (the compiled
files differ), or keep rules that only reorder a layout out of structural
probes.

#### 20. minor: four of eight more planted template defects still pass every committed test (rest of finding 8)

The 40 cases of `tests/unit/test_alternatives_on_tiny.py` find my planted
`<` at the end of the emergence window (the case with a window of 35 days),
and with `test_compile.py` four more plants: `>=` to `>` in the default
start rule; race pooling `<` to `<=`; age 80 in the upper group; the first
value as the end-of-treatment value. On a copy of the commit, these four
pass both test files (61 passed): `ae.teae.end/end_of_study` with `<` in
place of `<=`; `bds.window.tiebreak/closest_then_later` with the fragment
of `closest_then_earlier`; `pop.safety.rule/randomized_and_dosed` without
the randomization; `trt.end.source/ds_date_when_ex_missing` that never
falls back. The tiny study has no event on the end-of-study date, no tie in
a window, no dosed subject who is not randomized and no dosed subject
without an end date. The state file says the cases cover "the alternatives
that study can tell apart"; these are among the ones it cannot.

#### 21. minor: a statement line that lost its anchor is still skipped (rest of finding 9)

With the anchor removed (`Treatment emergence has no end date.` alone on its
line) or written in round brackets (`(2/s3) ...`), the document of 10
decisions parses without an error to 9. The parser could refuse any line
that a template matches.

### My planted defects, second pass

| # | Planted | Result |
| --- | --- | --- |
| P2 | Total percentage with the per-arm denominator | found now |
| P3 | relationship to an operation that does not exist | found now |
| P4 | `<=` to `<` at the end of the emergence window | found now (value case) |
| P8 | window tables that contradict themselves | refused now |
| P9 | SOC and PT percentages divided by the count of subjects with any event | found |
| P10 | `output_shape` claims `tfl.columns.arms` again | not found (finding 19) |
| P11 | `output_shape` claims `bds.eot.record` again | found |
| P12 | a `needs` text that says nothing | not found; it cannot be checked |
| P13 | eight more boundary and rule defects in compile templates | 4 found, 4 not (finding 20) |

### Also checked in this pass

- No version 0 schema of base-0 changed between 9a4b09f and 4002fc1; the
  catalog entry schema gained the four table rules (ADR-004 item 1). The
  catalog is still `draft-1`, ADR-004 still "proposed", no std-2 code.
- The statements changed by the fixes (`trt.date.imputation/not_completed`,
  the three of `trt.end.source`) round-trip, the fifteen phrasings of the
  two entries say what the statements say, and the old statements are
  refused. STANDARD.md equals its rendering.
- `docs/reports/std-1.catalog.md` equals `overview.render` at this commit
  (637 lines).
- The end date reads dosed records only, as the statements now say: a
  zero-dose record that ends later does not move `TRTEDT`.
- The 50 files of the std-1 part that changed have no non-ASCII byte and no
  CR; the three commits added no data file and no document. CLAUDE.md has
  57 lines.

Not checked: the code of real-1 that the merge brought; the clean clone gate
(the author's log `build/gates/std-1/clean-clone.log` shows "GATE std-1:
PASS" at 4002fc1); the report and gate log that are still to be committed.

Verdict after second pass: PASS

No finding is blocking: the three claims of the gate text hold at 4002fc1,
the gate passes in the worktree, and nothing is frozen or started that
waits for the owner. Open: finding 1 (until the report and the gate log are
committed), the major findings 17 and 18, and the minor findings 19 to 21.
Finding 17 touches a default the owner approves at N1.

Independent reviewer (fresh-context agent), second pass, 2026-11-11
