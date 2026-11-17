# read-1a Scorer of the slice "adverse event summary first": report of the first half

Date: 2026-11-17. Branch: `track/read`. Part read-1a of ADR-005, decision 1.
It needs real-3a (on `main`) and gen-2a (not on `main` yet: `main` is
`843c890`). PLAN.md section 13.6 says of read-1: "Start on the pilot and on
hand-made fixtures; finish on the kits of gen-2". This report is the start.

## Verdict

The first half is done. The part is not: its gate has not passed and
cannot pass before the kits of gen-2a are scored.

- The scorer exists: the reading score (section 9.1), the build score with
  the four scores of ADR-005, decision 4, attribution (section 9.4), the
  arms S and C, and the planted defects of section 9.5 for the slice.
- On the hand-made study HAND01 the gold decisions build the table that was
  worked out by hand, 24 of 24 cells on each dataset. The parser control
  (arm C) scores 100% in both stages, and does not when one statement of
  the document is changed.
- HAND01 can show 12 of the 21 decisions of the slice. For the other nine,
  no other value changes a cell of either dataset; the scorer finds this
  by mutation and reports a wrong value of such a decision as silent.
- Ten planted defects, each detected and attributed to the layer it was
  planted at; where a decision was planted, to that decision, and building
  with its gold value gives the gold text again. Three defects of section
  9.5 do not apply to a table of counts and percents.
- The pilot, report only: arm S at stage T gives 10 of the 15 cells of the
  rows both tables have, and 10 of all 27 cells of the key. Every one of
  the 17 other cells has a reason; none is unexplained.
- `specfirst gate read-1a` on a clone of `e091d15`: 13 of 14 checks pass.
  The check "kits of gen-2a" fails, as it must. The complete output is in
  `docs/reports/read-1a.first-half.gate.log`; the sections below quote it.

No review yet: rule R7 applies when the gate passes. `PLAN.md`,
`standard/schemas/` and the catalog are not changed. Nothing was read from
`track/gen`.

## What read-1a asks for, and where it stands

ADR-005, decision 1: "Reading score and build score for the decisions of
the slice and for one output, with attribution. The scores of decision 4."
Gate: "The planted defects of section 9.5 that apply to the slice are each
detected and attributed to the right layer. The parser control scores 100%."

| Item | State | Where |
| --- | --- | --- |
| Reading score: a candidate's records against gold, by class and by unit | done: value, status, citation (the quote stands in its document; it stands inside an anchor that gold cites), asks and unmapped as precision and recall. A decision left out takes the house default; a study input counts only when it was asked; a quirk and a decision without gold are counted and never scored | `src/specfirst/score/reading.py`; `tests/unit/test_score_reading.py` (20 tests, one planted difference each) |
| Build score for one output, on the visible data and on the twin: produced; cells correct with three denominators; strict; lenient | done, each printed with its denominator. A row is its section and label, a column its header; position counts for strict only | `score/build.py`; `tests/unit/test_score_build.py` |
| Attribution (section 9.4) | done: L4 analysis data, L5 analysis, L6 results, L7 layout, or a build that stopped; the differing decision that decides the first element, proven by compiling; every attribution to a decision run by building again | `score/attribute.py` |
| Arm S (`specfirst compile --defaults`) and arm C (the parser on the documents `specfirst render` writes) | done, with the two stages of ADR-005, decision 2 | `score/scorer.py`, `score/candidate.py` |
| The planted defects of section 9.5 that apply to the slice | done on HAND01: 10 planted, 3 do not apply | `score/defects.py`; `tests/unit/test_score_hand.py` |
| Hand-made fixtures | done: HAND01, 7 and 9 subjects, three arms, with the columns of `specfirst.compile.tiny` and its table by hand | `score/hand.py` |
| The pilot, arm S, report only | done | `score/pilot.py`; `tests/score/test_score_pilot.py` |
| The kits of gen-2a: the scorer and the planted defects on them; the gate | waits for gen-2a on `main` | `score/gate.py`, check `kits` |
| An ADR for the choices; the review; the clean-clone gate; the merge | wait for the gate | `docs/state/read.md` |

How a candidate is built. The scorer compiles a decision vector, runs the
compiled ADaM specs with the yamaa runner of the machine (a project file
with `adam.specs` is enough), runs the Python result engine and shows the
result as a grid. Gold is built the same way from the gold decisions, so
two builds differ only where the decisions do. The grid comes from a
stand-in, `score/display0.py`: the compiler writes layout draft 0 and the
grid builder of the machine reads layout version 0, which has no total
column, no rule for a count of zero and one rounding rule (ADR-003). Three
of the seven table decisions say exactly these things. The stand-in is for
the scorer's own builds and goes when the builder of gen-2a is used.

## The hand-made study, against the table worked out by hand

`specfirst.score.gate.hand_table` (check 5 of the gate). The docstring of
`score/hand.py` lists every subject and event; `EXPECTED` there is the
table by hand.

```text
== [5/14] hand-made study: specfirst.score.gate.hand_table: HAND01 against the table worked out by hand
HAND01, visible: 7 subjects, 8 adverse events; columns Placebo | Low Dose | High Dose | Total
  (column header)                                              (N=2) | (N=2) | (N=2) | (N=6)
  Any adverse event                                            1 ( 50.0) | 1 ( 50.0) | 2 ( 100.0) | 4 ( 66.7)
  Related adverse event                                        0 | 1 ( 50.0) | 1 ( 50.0) | 2 ( 33.3)
  Serious adverse event                                        0 | 1 ( 50.0) | 1 ( 50.0) | 2 ( 33.3)
  Adverse event leading to discontinuation of study treatment  0 | 0 | 1 ( 50.0) | 1 ( 16.7)
  Fatal adverse event                                          0 | 0 | 1 ( 50.0) | 1 ( 16.7)
HAND01, visible: 24 of 24 cells are the cells worked out by hand
HAND01, twin: 9 subjects, 7 adverse events; columns Placebo | Low Dose | High Dose | Total
  (column header)                                              (N=3) | (N=2) | (N=3) | (N=8)
  Any adverse event                                            1 ( 33.3) | 2 ( 100.0) | 2 ( 66.7) | 5 ( 62.5)
  Related adverse event                                        0 | 2 ( 100.0) | 0 | 2 ( 25.0)
  Serious adverse event                                        0 | 1 ( 50.0) | 0 | 1 ( 12.5)
  Adverse event leading to discontinuation of study treatment  0 | 0 | 1 ( 33.3) | 1 ( 12.5)
  Fatal adverse event                                          0 | 0 | 0 | 0
HAND01, twin: 24 of 24 cells are the cells worked out by hand
-- PASS hand-made study (1.1 s)
```

## What the hand-made study can show

`specfirst.score.gate.separated` (check 6). Every decision of the slice
takes, alone on the gold vector, every other value the catalog offers: each
alternative with the examples of its slots, and each list with one item
left out. The two numbers are the cells or axes that change on the visible
data and on the twin. A value under which the build stops changes all 24
cells (`tfl.population` = efficacy: the study defines no such set).

```text
== [6/14] separation: specfirst.score.gate.separated: every other value of every decision, alone on gold
decision: other value -> cells or axes changed on the visible data / on the twin
  trt.planned.source (UNSEPARATED): {"map": [{"code": "PBO", "label": "Placebo"}, {"code": "LOW", "label": "Low Dose"}, {"code": "HIGH", "label": "High Dose"}], "rule": "dm_armcd_map"} -> 0/0; {"map": [{"code": "A", "label": "Drug X, 10 mg"}, {"code": "B", "label": "Placebo"}], "rule": "dm_armcd_map"} -> 0/0
  trt.actual.source (separated on visible and twin): {"rule": "first_ex_treatment"} -> 19/19; {"rule": "same_as_planned"} -> 0/4
  trt.start.source (UNSEPARATED): {"rule": "first_ex_record"} -> 0/0; {"rule": "dm_rfxstdtc"} -> 0/0
  trt.end.source (separated on visible): {"rule": "last_ex_start_date"} -> 4/0; {"rule": "ds_date_when_ex_missing"} -> 0/0
  trt.date.imputation (UNSEPARATED): {"rule": "first_day_of_month"} -> 0/0
  date.studyday.origin (UNSEPARATED): {"rule": "dm_rfstdtc"} -> 0/0
  pop.randomized.rule (UNSEPARATED): {"rule": "randomized_with_postbaseline", "test": "SYSBP"} -> 0/0; {"rule": "randomized_with_postbaseline", "test": "WEIGHT"} -> 0/0
  pop.safety.rule (separated on twin): {"rule": "randomized_and_dosed"} -> 0/8
  pop.safety.grouping (separated on twin): {"rule": "planned"} -> 0/4
  disp.status.record (UNSEPARATED): {"rule": "disposition_event_by_subcategory", "subcategory": "STUDY PARTICIPATION"} -> 0/0; {"rule": "disposition_event_by_subcategory", "subcategory": "END OF STUDY"} -> 0/0
  ae.start.imputation (UNSEPARATED): {"rule": "first_of_month"} -> 0/0; {"rule": "not_completed"} -> 0/0
  ae.teae.start (UNSEPARATED): {"rule": "at_or_after_first_dose_time"} -> 0/0
  ae.teae.end (separated on twin): {"rule": "no_end"} -> 0/2; {"days": 7, "rule": "last_dose_plus_days"} -> 0/0; {"rule": "end_of_study"} -> 0/2
  ae.related.values (separated on visible and twin): {"rule": "stated_list", "values": ["RELATED"]} -> 3/2; {"rule": "stated_list", "values": ["POSSIBLY RELATED", "PROBABLY RELATED", "DEFINITELY RELATED"]} -> 3/2; {"rule": "stated_list", "values": ["PROBABLE"]} -> 3/2; {"rule": "stated_list", "values": ["POSSIBLE"]} -> 0/2
  tfl.output.include (separated on visible and twin): {"rule": "not_included"} -> 24/24
  tfl.population (separated on visible and twin): {"rule": "randomized"} -> 10/8; {"rule": "efficacy"} -> 24/24
  tfl.columns.arms (separated on visible and twin): {"rule": "protocol_order"} -> 1/1
  tfl.columns.total (separated on visible and twin): {"rule": "none"} -> 7/7; {"control": "Placebo", "rule": "active_arms"} -> 6/5; {"control": "Active Control", "rule": "active_arms"} -> 0/0
  tfl.percent.format (separated on visible and twin): {"rule": "one_decimal_always"} -> 6/10
  tfl.rounding.rule (UNSEPARATED): {"rule": "half_even"} -> 0/0
  tfl.ae.summary.rows (separated on visible and twin): {"rows": ["ANY", "SERIOUS", "FATAL"], "rule": "stated_rows"} -> 9/9; {"rows": ["ANY"], "rule": "stated_rows"} -> 17/17; {"rows": ["SERIOUS", "RELATED", "ANY"], "rule": "stated_rows"} -> 9/9
HAND01 separates 12 of 21 decisions of the slice on one of its two datasets; unseparated on both: trt.planned.source, trt.start.source, trt.date.imputation, date.studyday.origin, pop.randomized.rule, disp.status.record, ae.start.imputation, ae.teae.start, tfl.rounding.rule
the gold records mark the same 9 as unseparated: yes
-- PASS separation (29.7 s)
```

The first version of the study marked two decisions as unseparated, the
two its author had thought of; mutation finds nine (lesson 43). The gold
records now carry what mutation finds, and the check fails when they do
not. A kit of gen-2a has probes for every pair of alternatives; this study
has none for partial dates, dose times, a second exposure record or a
second disposition event, and says so.

## Arm C, the parser control

`specfirst score hand --arm C`, in both stages (check 7). The last lines
are rule R5 for the control itself: one statement of the document says 31
days in place of 30, and the control must not score 100%.

```text
== [7/14] parser control: specfirst score hand --arm C (both stages)
parser control on HAND01, stage C: 21 decisions; value 21 of 21; status 21 of 21; quote 21 of 21; span 21 of 21
  visible: produced 1 of 1; cells correct 24 of 24, 24 and 24 (its three denominators); strict 1 of 1; lenient 1 of 1
  twin: produced 1 of 1; cells correct 24 of 24, 24 and 24 (its three denominators); strict 1 of 1; lenient 1 of 1
parser control on HAND01, stage C: 100%
parser control on HAND01, stage T: 7 decisions; value 7 of 7; status 7 of 7; quote 7 of 7; span 7 of 7
  visible: produced 1 of 1; cells correct 24 of 24, 24 and 24 (its three denominators); strict 1 of 1; lenient 1 of 1
  twin: produced 1 of 1; cells correct 24 of 24, 24 and 24 (its three denominators); strict 1 of 1; lenient 1 of 1
parser control on HAND01, stage T: 100%
planted in the document: '[1/s1] Treatment emergence ends 30 days after the treatment end date.' with 31 days in place of 30
  the control is not 100%: wrong by value: ae.teae.end; twin: 2 cells wrong
the control fails on the changed document: yes
-- PASS parser control (0.9 s)
```

## Arm S, the standard alone

`specfirst score hand --arm S` and `--arm S --stage T` (check 8).

```text
== [8/14] standard alone: specfirst score hand --arm S (both stages)
case hand01, arm S, stage C
reading score: 21 gold decisions of the units mod-treatment, mod-populations, mod-ae-emergence, tfl-ae-summary
  by class:                     decisions  value       status      quote       span        
    document_rule                       2  0 of 2      0 of 2      1 of 2      0 of 2      
    house_default                      19  19 of 19    19 of 19    19 of 19    19 of 19    
  by unit:                      decisions  value       status      quote       span        
    mod-ae-emergence                    4  2 of 4      2 of 4      3 of 4      2 of 4      
    mod-populations                     4  4 of 4      4 of 4      4 of 4      4 of 4      
    mod-treatment                       6  6 of 6      6 of 6      6 of 6      6 of 6      
    tfl-ae-summary                      7  7 of 7      7 of 7      7 of 7      7 of 7      
  (value and status: right, of the decisions scored on it; quote: every quote stands in its document; span: a quote stands inside an anchor that gold cites)
  asks: 0 given, 0 in gold (decisions with the status asked), 0 of them right; precision none to judge, recall none to judge
  unmapped: 0 given, 0 in gold (what the catalog lacks), 0 of them right; precision none to judge, recall none to judge
  decisions a reviewer would have to change: 2
    ae.teae.end (mod-ae-emergence), document_rule: gold {"days": 30, "rule": "last_dose_plus_days"}; the candidate (default) has {"rule": "no_end"}
    ae.related.values (mod-ae-emergence), document_rule: gold {"rule": "stated_list", "values": ["POSSIBLE", "PROBABLE"]}; the candidate (open) has nothing
    ae.teae.end (mod-ae-emergence): wrong in status, span: cites house#4/s3; gold cites sap#1/s1
    ae.related.values (mod-ae-emergence): wrong in status, quote, span
  unseparated in gold, compared by value only: 9 trt.planned.source (right), trt.start.source (right), trt.date.imputation (right), date.studyday.origin (right), pop.randomized.rule (right), disp.status.record (right), ae.start.imputation (right), ae.teae.start (right), tfl.rounding.rule (right)
build score:
  visible: valid: no (compile: ADAE: no value for ae.related.values)
  visible: produced: 0 of 1 outputs in gold
  visible: cells correct: 0 of 0 gold cells of the rows that gold and the candidate both have
  visible: cells correct: 0 of 0 gold cells of the outputs produced
  visible: cells correct: 0 of 24 gold cells (an output that was not produced counts as wrong)
  visible: whole output, strict: 0 of 1 outputs in gold (both axes equal and every cell equal)
  visible: whole output, lenient: 0 of 1 outputs in gold (every gold cell present and equal)
  twin: valid: no (compile: ADAE: no value for ae.related.values)
  twin: produced: 0 of 1 outputs in gold
  twin: cells correct: 0 of 0 gold cells of the rows that gold and the candidate both have
  twin: cells correct: 0 of 0 gold cells of the outputs produced
  twin: cells correct: 0 of 24 gold cells (an output that was not produced counts as wrong)
  twin: whole output, strict: 0 of 1 outputs in gold (both axes equal and every cell equal)
  twin: whole output, lenient: 0 of 1 outputs in gold (every gold cell present and equal)
attribution, visible: 24 wrong cells
  layer  unit               decision                 cells  confirmed  first element that differs
  build  mod-ae-emergence   ae.related.values           24  24 of 24   compile: ADAE: no value for ae.related.values
attribution, twin: 24 wrong cells
  layer  unit               decision                 cells  confirmed  first element that differs
  build  mod-ae-emergence   ae.related.values           24  22 of 24   compile: ADAE: no value for ae.related.values
wrong by value, and behind another owner: ae.teae.end (mod-ae-emergence); alone, on gold, it changes 0 cells or axes of visible, 2 cells or axes of twin
case hand01, arm S: not every score is 100%
case hand01, arm S, stage T
reading score: 7 gold decisions of the units tfl-ae-summary
  by class:                     decisions  value       status      quote       span        
    house_default                       7  7 of 7      7 of 7      7 of 7      7 of 7      
  by unit:                      decisions  value       status      quote       span        
    tfl-ae-summary                      7  7 of 7      7 of 7      7 of 7      7 of 7      
  (value and status: right, of the decisions scored on it; quote: every quote stands in its document; span: a quote stands inside an anchor that gold cites)
  asks: 0 given, 0 in gold (decisions with the status asked), 0 of them right; precision none to judge, recall none to judge
  unmapped: 0 given, 0 in gold (what the catalog lacks), 0 of them right; precision none to judge, recall none to judge
  decisions a reviewer would have to change: 0
  unseparated in gold, compared by value only: 1 tfl.rounding.rule (right)
build score:
  visible: valid: yes
  visible: produced: 1 of 1 outputs in gold
  visible: cells correct: 24 of 24 gold cells of the rows that gold and the candidate both have
  visible: cells correct: 24 of 24 gold cells of the outputs produced
  visible: cells correct: 24 of 24 gold cells (an output that was not produced counts as wrong)
  visible: whole output, strict: 1 of 1 outputs in gold (both axes equal and every cell equal)
  visible: whole output, lenient: 1 of 1 outputs in gold (every gold cell present and equal)
  twin: valid: yes
  twin: produced: 1 of 1 outputs in gold
  twin: cells correct: 24 of 24 gold cells of the rows that gold and the candidate both have
  twin: cells correct: 24 of 24 gold cells of the outputs produced
  twin: cells correct: 24 of 24 gold cells (an output that was not produced counts as wrong)
  twin: whole output, strict: 1 of 1 outputs in gold (both axes equal and every cell equal)
  twin: whole output, lenient: 1 of 1 outputs in gold (every gold cell present and equal)
case hand01, arm S: every score is 100%
arm S, chain: no output produced: yes; owned by ae.related.values
arm S, stage T: every score 100%: yes
-- PASS standard alone (0.1 s)
```

On the chain arm S builds nothing: `ae.related.values` has no house default
and ADAE does not compile without it (ADR-005, decision 3: "what cannot be
built without it counts as not produced"). That is so in every study, not
only in this one. The 24 cells are owned by that decision. With its gold
value the visible table is right; on the twin 2 cells stay wrong, because
the default of `ae.teae.end` (no end) counts the event on the 31st day:
the report lists that decision as "behind another owner". At stage T the
ADaM is given, the seven table decisions of this study are all defaults,
and arm S scores 100%.

## The planted defects

`specfirst score defects` (check 9).

```text
== [9/14] planted defects: specfirst score defects
planted defects on the case hand01, stage C
  control: the gold decisions, through the parser, score 100%
  S1-arms: arms exchanged in one analysis (E3)
    planted at L6 (planted in the results, after the engine): in the results of the first analysis in which two arms differ, the results of the two arms are exchanged
    visible: 2 of 24 gold cells wrong, strict 0 of 1
    twin: 2 of 24 gold cells wrong, strict 0 of 1
    visible: 2 cells owned by layer L6, unit -, decision -
    twin: 2 cells owned by layer L6, unit -, decision -
    detected: yes; attributed to its layer: yes
  S2-set: a wrong analysis set
    planted at L5 (the table names another analysis set (decision tfl.population)): tfl.population (tfl-ae-summary): {"rule": "safety"} becomes {"rule": "randomized"}
    visible: 10 of 24 gold cells wrong, strict 0 of 1
    twin: 8 of 24 gold cells wrong, strict 0 of 1
    visible: 10 cells owned by layer L5, unit tfl-ae-summary, decision tfl.population; confirmed 10 of 10
    twin: 8 cells owned by layer L5, unit tfl-ae-summary, decision tfl.population; confirmed 8 of 8
    detected: yes; attributed to its layer: yes
  S2-set-rule: a wrong analysis set
    planted at L4 (the set of the table is formed by another rule (a decision of mod-populations)): pop.safety.rule (mod-populations): {"rule": "at_least_one_dose"} becomes {"rule": "randomized_and_dosed"}
    visible: every score 100%
    twin: 8 of 24 gold cells wrong, strict 0 of 1
    twin: 8 cells owned by layer L4, unit mod-populations, decision pop.safety.rule; confirmed 8 of 8
    detected: yes; attributed to its layer: yes
  S3-window: a window off by one day
    planted at L4 (treatment emergence ends one day later (decision ae.teae.end)): ae.teae.end (mod-ae-emergence): {"days": 30, "rule": "last_dose_plus_days"} becomes {"days": 31, "rule": "last_dose_plus_days"}
    visible: every score 100%
    twin: 2 of 24 gold cells wrong, strict 0 of 1
    twin: 2 cells owned by layer L4, unit mod-ae-emergence, decision ae.teae.end; confirmed 2 of 2
    detected: yes; attributed to its layer: yes
  S4-denominator: a wrong denominator
    planted at L5 (planted in the ARS file: no decision of the slice changes a denominator): in the ARS file, the percent of the first row takes its denominator from a count of another analysis set
    visible: 1 of 24 gold cells wrong, strict 0 of 1
    twin: 2 of 24 gold cells wrong, strict 0 of 1
    visible: 1 cells owned by layer L5, unit -, decision -
    twin: 2 cells owned by layer L5, unit -, decision -
    detected: yes; attributed to its layer: yes
  S5-column: a missing column
    planted at L7 (planted in the layout): in the layout, the total column is left out; the ARS file still has its analyses
    visible: 6 of 24 gold cells wrong, strict 0 of 1
    twin: 6 of 24 gold cells wrong, strict 0 of 1
    visible: 6 cells owned by layer L7, unit -, decision -
    visible: the axis columns owned by layer L7, unit -, decision -
    twin: 6 cells owned by layer L7, unit -, decision -
    twin: the axis columns owned by layer L7, unit -, decision -
    detected: yes; attributed to its layer: yes
  S6-quantile: a changed quantile definition (E4)
    does not apply: the adverse event summary shows counts of subjects and percents, no quantile
  S7-pvalue: a p-value rounded twice (E25)
    does not apply: the adverse event summary shows counts of subjects and percents, no p-value
  S8-baseline: a baseline taken from the wrong record (E26)
    does not apply: the adverse event summary shows counts of subjects and percents, no baseline value
  S9-sort: an unstable sort
    planted at L7 (the slice orders one thing, the treatment columns: planted as the other order (decision tfl.columns.arms). An order that changes from run to run is for P1 to find): tfl.columns.arms (tfl-ae-summary): {"rule": "ascending_dose_placebo_first"} becomes {"rule": "protocol_order"}
    visible: 0 of 24 gold cells wrong, strict 0 of 1
    twin: 0 of 24 gold cells wrong, strict 0 of 1
    visible: the axis columns owned by layer L7, unit tfl-ae-summary, decision tfl.columns.arms; confirmed yes
    twin: the axis columns owned by layer L7, unit tfl-ae-summary, decision tfl.columns.arms; confirmed yes
    detected: yes; attributed to its layer: yes
  S10-frozen: a frozen site list (caught on the twin only)
    planted at L4 (the slice has no site list; its frozen list is the causality values that count as related, cut down to those the visible data hold (decision ae.related.values)): ae.related.values (mod-ae-emergence): {"rule": "stated_list", "values": ["POSSIBLE", "PROBABLE"]} becomes {"rule": "stated_list", "values": ["POSSIBLE"]}
    visible: every score 100%
    twin: 2 of 24 gold cells wrong, strict 0 of 1
    twin: 2 cells owned by layer L4, unit mod-ae-emergence, decision ae.related.values; confirmed 2 of 2
    detected: yes; attributed to its layer: yes
  S11-quote: a quote that is not in the document
    planted at L0 (planted in a citation of the candidate): ae.teae.end (mod-ae-emergence): the quote gets words the document does not have
    reading: quote: wrong for ae.teae.end
    detected: yes; attributed to its layer: yes
  S12-span: a citation that points at the wrong span
    planted at L0 (planted in a citation of the candidate): ae.teae.end (mod-ae-emergence): the citation names the anchor 1/s2, that of another decision; the quote is unchanged
    reading: span: wrong for ae.teae.end
    detected: yes; attributed to its layer: yes
planted defects on hand01: 13 of section 9.5 with the one planted at two layers; 3 do not apply to the slice; 10 of 10 planted here; 10 of 10 detected and attributed
-- PASS planted defects (2.8 s)
```

The cells each defect must change were worked out by hand before the first
run, and `tests/unit/test_score_hand.py` asserts them: for example S2-set
changes 10 cells of the visible table (the never-dosed subject L3 enters
the low dose column) and 8 of the twin.

## The pilot (ADR-005, decision 5): arm S, stage T, report only

`specfirst score pilot` (check 10). The adverse event summary is built from
the house defaults on the reference ADaM of CDISCPILOT01 (the two datasets
the kit pins, read from the fetch cache after their SHA-256 is checked) and
held against the results CDISC's ARS example embeds for the analyses of its
output Out14-3-1-1. Nothing was tuned on the pilot.

```text
== [10/14] pilot: specfirst score pilot (report only)
pilot CDISCPILOT01, arm S (the house standard alone), stage T (table decisions on the reference ADaM); report only
key: the results CDISC's ARS example embeds for its adverse event summary (Out14-3-1-1), as the kit's layout places them
  row | column | key | arm S | state
  (column header) | Placebo | (N=86) | (N=86) | equal
  (column header) | Xanomeline Low Dose | (N=84) | (N=84) | equal
  (column header) | Xanomeline High Dose | (N=84) | (N=84) | equal
  Any adverse event | Placebo | 65 ( 75.6) | 65 ( 75.6) | equal
  Any adverse event | Xanomeline Low Dose | 77 ( 91.7) | 77 ( 91.7) | equal
  Any adverse event | Xanomeline High Dose | 76 ( 90.5) | 76 ( 90.5) | equal
  Related adverse event | Placebo | 43 ( 50.0) | - | the row is not built: the reference ADaM has no ADAE.RELGR1, which the house standard writes by ae.related.values
  Related adverse event | Xanomeline Low Dose | 72 ( 85.7) | - | the row is not built: the reference ADaM has no ADAE.RELGR1, which the house standard writes by ae.related.values
  Related adverse event | Xanomeline High Dose | 70 ( 83.3) | - | the row is not built: the reference ADaM has no ADAE.RELGR1, which the house standard writes by ae.related.values
  Serious adverse event | Placebo | 0 (  0.0) | 0 | differs; explained by tfl.percent.format = {"rule": "one_decimal_always"}
  Serious adverse event | Xanomeline Low Dose | 1 (  1.2) | 1 (  1.2) | equal
  Serious adverse event | Xanomeline High Dose | 2 (  2.4) | 2 (  2.4) | equal
  Related Serious TEAE | Placebo | 0 (  0.0) | - | the catalog has no such row (tfl.ae.summary.rows)
  Related Serious TEAE | Xanomeline Low Dose | 1 (  1.2) | - | the catalog has no such row (tfl.ae.summary.rows)
  Related Serious TEAE | Xanomeline High Dose | 1 (  1.2) | - | the catalog has no such row (tfl.ae.summary.rows)
  Fatal adverse event | Placebo | 2 (  2.3) | 2 (  2.3) | equal
  Fatal adverse event | Xanomeline Low Dose | 1 (  1.2) | 1 (  1.2) | equal
  Fatal adverse event | Xanomeline High Dose | 0 (  0.0) | 0 | differs; explained by tfl.percent.format = {"rule": "one_decimal_always"}
  Related TEAE Leading to Death | Placebo | 1 (  1.2) | - | the catalog has no such row (tfl.ae.summary.rows)
  Related TEAE Leading to Death | Xanomeline Low Dose | 0 (  0.0) | - | the catalog has no such row (tfl.ae.summary.rows)
  Related TEAE Leading to Death | Xanomeline High Dose | 0 (  0.0) | - | the catalog has no such row (tfl.ae.summary.rows)
  TEAE Leading to Dose Modification [a] | Placebo | 0 (  0.0) | - | the catalog has no such row (tfl.ae.summary.rows)
  TEAE Leading to Dose Modification [a] | Xanomeline Low Dose | 0 (  0.0) | - | the catalog has no such row (tfl.ae.summary.rows)
  TEAE Leading to Dose Modification [a] | Xanomeline High Dose | 0 (  0.0) | - | the catalog has no such row (tfl.ae.summary.rows)
  Adverse event leading to discontinuation of study treatment | Placebo | 0 (  0.0) | 0 | differs; explained by tfl.percent.format = {"rule": "one_decimal_always"}
  Adverse event leading to discontinuation of study treatment | Xanomeline Low Dose | 0 (  0.0) | 0 | differs; explained by tfl.percent.format = {"rule": "one_decimal_always"}
  Adverse event leading to discontinuation of study treatment | Xanomeline High Dose | 0 (  0.0) | 0 | differs; explained by tfl.percent.format = {"rule": "one_decimal_always"}
  reference ADaM: valid: yes
  reference ADaM: produced: 1 of 1 outputs in gold
  reference ADaM: cells correct: 10 of 15 gold cells of the rows that gold and the candidate both have
  reference ADaM: cells correct: 10 of 27 gold cells of the outputs produced
  reference ADaM: cells correct: 10 of 27 gold cells (an output that was not produced counts as wrong)
  reference ADaM: whole output, strict: 0 of 1 outputs in gold (both axes equal and every cell equal)
  reference ADaM: whole output, lenient: 0 of 1 outputs in gold (every gold cell present and equal)
  the rows are not the key's (the key has 4 rows that arm S lacks): no other value of one table decision makes them equal
  the columns are not the key's (arm S has more: Total): explained by tfl.columns.total = {"rule": "none"}
  cells of the key that differ or are missing: 17. 5 differ and are explained by another value of one table decision; 3 are in a row that needs a variable the reference ADaM lacks; 9 are in rows the catalog does not have; 0 unexplained
  variables the house template reads: 9; in the reference ADaM under the same name: ADAE.AEACN, ADAE.AESDTH, ADAE.AESER, ADAE.TRTEMFL, ADAE.USUBJID, ADSL.SAFFL, ADSL.TRT01A, ADSL.USUBJID
  variables the house template reads and the reference ADaM does not have: 1
    ADAE.RELGR1: the house standard writes it by ae.related.values; rows not built: RELATED
  analyses of the example with no row in the catalog: An07_04_RelSerTEAE_Summ_ByTrt, An07_06_RelTEAELd2Dth_Summ_ByTrt, An07_07_TEAELd2DoseMod_Summ_ByTrt
  the crosswalk of rows (example analysis = house row): An07_01_TEAE_Summ_ByTrt = ANY, An07_02_RelTEAE_Summ_ByTrt = RELATED, An07_03_SerTEAE_Summ_ByTrt = SERIOUS, An07_05_TEAELd2Dth_Summ_ByTrt = FATAL, An07_08_TEAELd2TrtDsc_Summ_ByTrt = DISCONTINUATION
pilot: report only; its scores decide nothing in this gate
-- PASS pilot (0.2 s)
```

Read with it:

- The five cells that differ are counts of zero. The house default shows a
  count of zero without a percent (`tfl.percent.format`, the alternative
  the CSR follows, E25); the example shows "0 (  0.0)". With the other
  alternative each of the five has the key's text: that is the proof of a
  `rule_choice` (section 4.8).
- The row of related events is not built. The house template reads
  ADAE.RELGR1, which the house standard derives by the decision
  `ae.related.values`; the reference ADaM has the collected AEREL and no
  pooled group, and the example's own data subset reads AEREL IN
  (POSSIBLE, PROBABLE). Stage T is given ADaM, so the variable cannot be
  derived there. Every other variable the template reads is in the
  reference ADaM under the same name.
- Three analyses of the example have no row in the catalog: related
  serious events, related events leading to death, events leading to dose
  modification. `tfl.ae.summary.rows` has five row codes. This is a gap of
  the catalog, not a difference a decision explains (ADR-005, "For the
  owner", item 3).
- The house default has a total column and the example has none
  (`tfl.columns.total`).
- Which analysis of the example is which row of the house table is a
  reading of two public definitions (`ROWS` in `score/pilot.py`): the data
  subsets say the same thing for five of the eight.
- Arm R on the pilot is read-2a's.

## The gate

`specfirst gate read-1a --clean` on a clone of `e091d15` in the Linux file
system, with the installed environment of the worktree, under the lock the
sessions share. It is not the clean-clone gate (no fresh install or fetch);
that one is run when the gate can pass.

```text
gate read-1a at commit e091d15a344cc191b23cf731fa26afbffc23abc0 (clean)
...
PASS  environment          0.3 s
PASS  pins                 0.1 s
PASS  lint                 0.0 s
PASS  unit tests          89.9 s
PASS  hand-made study      1.1 s
PASS  separation          29.7 s
PASS  parser control       0.9 s
PASS  standard alone       0.1 s
PASS  planted defects      2.8 s
PASS  pilot                0.2 s
PASS  pilot tests          0.9 s
FAIL  kits of gen-2a       0.0 s
PASS  cache untouched      0.1 s
PASS  ASCII                0.0 s
GATE read-1a: FAIL
```

The check "kits of gen-2a" prints why it fails:

```text
== [12/14] kits of gen-2a: specfirst.score.gate.kits
the kits of gen-2a are not on this checkout: the scorer and the planted defects have run on the hand-made study and on the pilot only
read-1a is not done before this check runs on the kits (docs/state/read.md)
-- FAIL kits of gen-2a (0.0 s)
```

CI on `track/read`: success on `4ef81c8` (run 44164364090), on `35ffcc2` (run
44164889780) and on `e091d15` (run 44166086677), the commit of the gate.

## What waits for gen-2a

`docs/state/read.md` has the five steps. In short: merge `main`; build the
candidate with the builder that builds the kits' gold (arm C on every kit
is the test: the gold decisions must give the kit's own grids cell for
cell); score the kits; run the planted defects on them; then the ADR, the
review, the clean-clone gate and the merge.

## For the owner

Choices made where the plan is silent. They stand unless the owner objects.

1. Arm S builds nothing on the chain, in any study (`ae.related.values`
   has no default in `catalog@1`). "R against S" is then a comparison with
   zero on the chain, and arm S says something at stage T only. A default,
   or an ADAE that builds without the decision, belongs to the std track
   and to a new catalog version; the scorer needs no change for either.
2. A row is its section and label, a column its header. A candidate whose
   treatment labels differ from gold's (another source of planned
   treatment, for example) has no column in common with gold.
3. One owner per wrong cell, found from the far end of the path (data
   before analysis before results before layout). A second wrong decision
   behind the same cell is listed as "behind another owner".
4. Three planted defects of section 9.5 do not apply to the slice. Two are
   planted as the nearest thing the slice has: "an unstable sort" as the
   other order of the treatment columns, "a frozen site list" as the list
   of related causality values cut down to those in the visible data.
   Three are planted in the build and not in a decision (arms exchanged,
   wrong denominator, missing column).
5. The pilot's crosswalk of rows, and that titles, footnotes and the header
   of the row labels are not compared.

## Limits

- One hand-made study and one real study. What a twin with many subjects
  does to the planted decisions (docs/state/gen.md: planted subjects that
  cancel, values of one slot, pairs that are not separated) is seen only
  on the kits. The scorer reports a wrong value that changes no cell as
  `silent`; HAND01 has nine such decisions, and its twin is no superset
  of its visible data (`trt.end.source` is shown by the visible data only).
- The candidate is built with the Python engine only. Rule R11 is the
  business of the gold build.
- Documents are in standard form. The anchors of natural-form documents
  come with gen-3a.
- Not in this part: the three layers of ADaM scoring of section 9.3, the
  cost dimension, questions answered by an oracle (read-2a).
