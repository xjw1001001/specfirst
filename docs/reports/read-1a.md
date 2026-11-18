# read-1a Scorer of the slice "adverse event summary first": report

Date: 2026-11-18. Branch: `track/read`. Part read-1a of ADR-005, decision 1.
It needs real-3a and gen-2a; both are on `main` (`d5c7e50`). PLAN.md
section 13.6 says of read-1: "Start on the pilot and on hand-made fixtures;
finish on the kits of gen-2". The first half (2026-11-17, `134c6f7`) was the
start; this report is the whole part and replaces the report of the first
half.

## Verdict

The gate passed: `scripts/clean_clone_gate.sh read-1a` exited 0 on a clean
clone of `55dba60` (fresh install, fresh fetch), 14 of 14 checks.
The independent review has not run yet (rule R7): nothing is merged.

- On the hand-made study HAND01 the gold decisions build the table that
  was worked out by hand, 24 of 24 cells on each dataset. The parser
  control (arm C) scores 100% in both stages, and does not when one
  statement of the document is changed. Ten planted defects, each
  detected and attributed to the layer it was planted at; where a decision
  was planted, to that decision, and building with its gold value gives
  the gold text again. Three defects of section 9.5 do not apply to a
  table of counts and percents.
- On the ten kits of the gate of gen-2a, written again from its seed: the
  gold decisions, built again by the scorer, give the files of every kit
  (the grid, every result, every ADaM value); arm C scores 100% in both
  stages on every kit; no planted defect fails on any kit, and each of the
  ten is detected and attributed on at least one kit, most on all ten.
  Where a kit cannot show a planted decision the scorer reports it as
  silent, and the identifiability matrix of the kit says the same.
- The sweep: every decision of every kit, read as each other value of the
  kit's matrix, 293 candidates with one wrong decision each. The reading
  score has exactly that decision wrong in all 293. The twin shows 209
  and not 84, as the matrices say (one of the 84 shows on the visible
  data only, 83 on neither). All 2307 wrong cells and axes are owned by
  the changed decision, and its gold value gives the gold text again.
- Arm S builds nothing on the chain, in the hand-made study and in every
  kit: `ae.related.values` has no house default. At stage T it gives the
  whole table of HAND01, and between 0 and 25 of the 15 to 30 gold cells
  of a kit's twin.
- The pilot, report only: arm S at stage T gives 10 of the 15 cells of the
  rows both tables have, and 10 of all 27 cells of the key. Every one of
  the 17 other cells has a reason; none is unexplained.

`PLAN.md`, `standard/schemas/` and the catalog `catalog@1` are not changed.
Nothing was written into the fetch cache; no R package was installed. No
kit, no study data and no third-party document is in the repository.

## What read-1a asks for, and where it is

ADR-005, decision 1: "Reading score and build score for the decisions of
the slice and for one output, with attribution. The scores of decision 4."
Gate: "The planted defects of section 9.5 that apply to the slice are each
detected and attributed to the right layer. The parser control scores 100%."

| Item | State | Where |
| --- | --- | --- |
| Reading score: a candidate's records against gold, by class and by unit | value, status, citation (the quote stands in its document; it stands inside an anchor that gold cites), asks and unmapped as precision and recall. A decision left out takes the house default; a study input counts only when it was asked; a quirk and a decision without gold are counted and never scored; a decision that gold marks unseparated is compared by value and listed apart | `src/specfirst/score/reading.py`; `tests/unit/test_score_reading.py` |
| Build score for one output, on the visible data and on the twin: produced; cells correct with three denominators; strict; lenient | each printed with its denominator. A row is its section and label, a column its header; position counts for strict only | `score/build.py`; `tests/unit/test_score_build.py` |
| Attribution (section 9.4) | L4 analysis data, L5 analysis, L6 results, L7 layout, or a build that stopped; the differing decision that decides the first element, proven by compiling; every attribution to a decision run by building again; the same walk for an axis | `score/attribute.py` |
| Arm S (`specfirst compile --defaults`) and arm C (the parser on standard-form documents) | both, with the two stages of ADR-005, decision 2 | `score/scorer.py`, `score/candidate.py` |
| The planted defects of section 9.5 that apply to the slice | on HAND01 and on the ten kits | `score/defects.py`; `tests/unit/test_score_hand.py`, `test_score_kit.py` |
| Hand-made fixtures | HAND01, 7 and 9 subjects, three arms, with its table by hand | `score/hand.py` |
| The pilot, arm S, report only | done | `score/pilot.py`; `tests/score/test_score_pilot.py` |
| The kits of gen-2a | the ten kits of the gate of gen-2a, written again from its seed: gold built again, both arms in both stages, the planted defects, the sweep of each matrix | `score/kit.py`; check `kits of gen-2a` of the gate |
| The gate `read-1a`, `specfirst score ...` | 14 checks | `score/gate.py`, `src/specfirst/gates.py`, `score/command.py` |
| Choices where the plan is silent | ADR-008 | `docs/decisions/ADR-008.md` |

How a candidate is built. The scorer compiles a decision vector, runs the
compiled ADaM specs with the yamaa runner of the machine, lists the groups
of the treatment grouping from the ADaM data, runs the Python result engine
and builds the grid with `specfirst.gen.display`: from the groups on, the
functions that build the gold of a generated kit (ADR-007). Gold is built
the same way from the gold decisions, so two builds differ only where the
decisions do. The stand-in grid builder of the first half is gone. With it
went one text of HAND01: 100% is "(100.0)" under the pattern of gen-2a,
where the stand-in wrote "( 100.0)".

## The hand-made study, against the table worked out by hand

`specfirst.score.gate.hand_table` (check 5 of the gate). The docstring of
`score/hand.py` lists every subject and event; `EXPECTED` there is the
table by hand.

```text
== [5/14] hand-made study: specfirst.score.gate.hand_table: HAND01 against the table worked out by hand
HAND01, visible: 7 subjects, 8 adverse events; columns Placebo | Low Dose | High Dose | Total
  (column header)                                              (N=2) | (N=2) | (N=2) | (N=6)
  Any adverse event                                            1 ( 50.0) | 1 ( 50.0) | 2 (100.0) | 4 ( 66.7)
  Related adverse event                                        0 | 1 ( 50.0) | 1 ( 50.0) | 2 ( 33.3)
  Serious adverse event                                        0 | 1 ( 50.0) | 1 ( 50.0) | 2 ( 33.3)
  Adverse event leading to discontinuation of study treatment  0 | 0 | 1 ( 50.0) | 1 ( 16.7)
  Fatal adverse event                                          0 | 0 | 1 ( 50.0) | 1 ( 16.7)
HAND01, visible: 24 of 24 cells are the cells worked out by hand
HAND01, twin: 9 subjects, 7 adverse events; columns Placebo | Low Dose | High Dose | Total
  (column header)                                              (N=3) | (N=2) | (N=3) | (N=8)
  Any adverse event                                            1 ( 33.3) | 2 (100.0) | 2 ( 66.7) | 5 ( 62.5)
  Related adverse event                                        0 | 2 (100.0) | 0 | 2 ( 25.0)
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
-- PASS separation (31.9 s)
```

The first version of the study marked two decisions as unseparated, the
two its author had thought of; mutation finds nine (lesson 51). The gold
records carry what mutation finds, and the check fails when they do not.

## Arm C, the parser control, on the hand-made study

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
-- PASS parser control (1.0 s)
```

## Arm S, the standard alone, on the hand-made study

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
built without it counts as not produced"). That is so in every study; the
kits below show it ten times. With the gold value of that decision the
visible table is right; on the twin 2 cells stay wrong, because the default
of `ae.teae.end` (no end) counts the event on the 31st day: the report
lists that decision as "behind another owner".

## The planted defects on the hand-made study

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
    planted at L5 (planted in the ARS file: no decision of the slice changes a denominator): in the ARS file, the percent of the second row takes its denominator from the subjects counted in the first row, not from the subjects of the analysis set
    visible: 2 of 24 gold cells wrong, strict 0 of 1
    twin: 1 of 24 gold cells wrong, strict 0 of 1
    visible: 2 cells owned by layer L5, unit -, decision -
    twin: 1 cells owned by layer L5, unit -, decision -
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
planted defects on hand01: 13 of section 9.5 with the one planted at two layers; 3 do not apply to the slice; 10 of 10 planted here; 10 of 10 detected and attributed; 0 silent on these data
-- PASS planted defects (2.9 s)
```

The cells each defect must change were worked out by hand before the run,
and `tests/unit/test_score_hand.py` asserts them. Two examples. S2-set
changes 10 cells of the visible table (the never-dosed subject L3 enters
the low dose column) and 8 of the twin. S4-denominator divides the related
events by the subjects with any event: on the visible data the low dose
cell becomes 1 of 1 and the total 2 of 4, while the high dose cell stays
1 of 2, so 2 cells are wrong; on the twin only the total is (2 of 5).

The plant of the wrong denominator is not that of the first half. It was a
count on another analysis set; the groups of a grouping are now listed for
one analysis set, and that plant would have stopped the build. The numbers
by hand were worked out again for the new plant.

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
-- PASS pilot (0.4 s)
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
- The numbers are those of the first half: the builder of gen-2a and the
  stand-in give the pilot the same texts.
- Arm R on the pilot is read-2a's.

## The kits of gen-2a

`specfirst.score.gate.kits` (check 12): it writes the ten kits of the seed
of the gate gen-2a and then runs what `specfirst score kits DIR` runs. A
kit is never in the repository. It is a pure function of the generator, the
catalog, the house standard and the seed (property P1, which the gate
gen-2a holds), so these are the kits of that gate; the IDs are those of
`docs/reports/gen-2a.gate.log`.

```text
kit 1 of the set of the seed 'gen-2a': sfpbt5zj, train, generator gen-2a.2, 121 files, kit.yaml 653117abf6cabbbb
kit 2 of the set of the seed 'gen-2a': sfmyncmq, train, generator gen-2a.2, 121 files, kit.yaml 5ea25e857d834702
kit 3 of the set of the seed 'gen-2a': sfg5vbvq, train, generator gen-2a.2, 120 files, kit.yaml b5c3dc2402630988
kit 4 of the set of the seed 'gen-2a': sfrrl2uh, train, generator gen-2a.2, 121 files, kit.yaml 6692cd252c73ddb4
kit 5 of the set of the seed 'gen-2a': sflnykvq, dev, generator gen-2a.2, 120 files, kit.yaml ccd7d7363e41ea9f
kit 6 of the set of the seed 'gen-2a': sfphbktr, dev, generator gen-2a.2, 120 files, kit.yaml cc4e4ec595e66e4c
kit 7 of the set of the seed 'gen-2a': sfp6x45g, dev, generator gen-2a.2, 121 files, kit.yaml 4fe791c87f35eafc
kit 8 of the set of the seed 'gen-2a': sf6xjw92, test, generator gen-2a.2, 120 files, kit.yaml f6fa450783be651a
kit 9 of the set of the seed 'gen-2a': sfyf9ekd, test, generator gen-2a.2, 121 files, kit.yaml 1cfbc4305c4de083
kit 10 of the set of the seed 'gen-2a': sf4tvbdp, test, generator gen-2a.2, 121 files, kit.yaml d69a08d18d867c30
```

What is done on each kit, with kit 9 as the example (the kit in which the
table reads three decisions that its twin does not separate, the rounding
rule among them):

```text
kit sfyf9ekd (kit-009), test: 3 arms; 114 subjects in the visible data, 137 in the twin; 22 decisions of the slice, 13 stated
  unseparated on the twin by the matrix of the kit, compared by value only: 8: date.studyday.origin, disp.status.record, pop.randomized.rule, pop.safety.grouping, trt.actual.source, pop.safety.rule, tfl.rounding.rule, trt.end.source (read by the table: pop.safety.rule, tfl.rounding.rule, trt.end.source)
  gold: built again from the gold decisions, it is the gold of the kit on both datasets: visible 24 cells, 44 results, 59 ADaM columns; twin 24 cells, 44 results, 59 ADaM columns
  arm C, stage C: 22 decisions: value 22 of 22; status 22 of 22; quote 22 of 22; span 22 of 22; visible: produced 1 of 1; cells correct 24 of 24, 24 and 24; strict 1 of 1; lenient 1 of 1; twin: produced 1 of 1; cells correct 24 of 24, 24 and 24; strict 1 of 1; lenient 1 of 1: 100%
  arm C, stage T: 7 decisions: value 7 of 7; status 7 of 7; quote 7 of 7; span 7 of 7; visible: produced 1 of 1; cells correct 24 of 24, 24 and 24; strict 1 of 1; lenient 1 of 1; twin: produced 1 of 1; cells correct 24 of 24, 24 and 24; strict 1 of 1; lenient 1 of 1: 100%
  arm S, stage C: 13 of 22 decisions to change (trt.planned.source, trt.start.source, pop.randomized.rule, pop.safety.rule, pop.efficacy.rule, ae.start.imputation, ae.teae.end, ae.related.values, tfl.population, tfl.columns.arms, tfl.columns.total, tfl.percent.format, tfl.rounding.rule); visible: produced 0 of 1; cells correct 0 of 0, 0 and 24; strict 0 of 1; lenient 0 of 1 (not valid: compile: ADAE: no value for ae.related.values); twin: produced 0 of 1; cells correct 0 of 0, 0 and 24; strict 0 of 1; lenient 0 of 1 (not valid: compile: ADAE: no value for ae.related.values)
  arm S, stage T: 5 of 7 decisions to change (tfl.population, tfl.columns.arms, tfl.columns.total, tfl.percent.format, tfl.rounding.rule); visible: produced 1 of 1; cells correct 3 of 24, 24 and 24; strict 0 of 1; lenient 0 of 1; twin: produced 1 of 1; cells correct 0 of 24, 24 and 24; strict 0 of 1; lenient 0 of 1
  S1-arms (L6): passed: in the results of the first analysis in which two arms differ, the results of the two arms are exchanged. visible 2 of 24 gold cells wrong, strict 0 of 1; twin 2 of 24 gold cells wrong, strict 0 of 1; visible owned by L6 (no decision); twin owned by L6 (no decision)
  S2-set (L5): passed: tfl.population (tfl-ae-summary): {"rule": "efficacy"} becomes {"rule": "safety"}. visible 18 of 24 gold cells wrong, strict 0 of 1; twin 22 of 24 gold cells wrong, strict 0 of 1; visible owned by L5 (tfl.population); twin owned by L5 (tfl.population); the matrix: separated on the twin
  S2-set-rule (L4): passed: pop.efficacy.rule (mod-populations): {"rule": "baseline_and_postbaseline", "test": "SYSBP"} becomes {"rule": "attended_visit", "visit": "WEEK 2"}. visible 15 of 24 gold cells wrong, strict 0 of 1; twin 19 of 24 gold cells wrong, strict 0 of 1; visible owned by L4 (pop.efficacy.rule); twin owned by L4 (pop.efficacy.rule); the matrix: separated on the twin
  S3-window (L4): passed: ae.teae.end (mod-ae-emergence): {"days": 14, "rule": "last_dose_plus_days"} becomes {"days": 15, "rule": "last_dose_plus_days"}. visible every score 100%; twin 2 of 24 gold cells wrong, strict 0 of 1; twin owned by L4 (ae.teae.end); the matrix holds no such pair
  S4-denominator (L5): passed: in the ARS file, the percent of the second row takes its denominator from the subjects counted in the first row, not from the subjects of the analysis set. visible 4 of 24 gold cells wrong, strict 0 of 1; twin 4 of 24 gold cells wrong, strict 0 of 1; visible owned by L5 (no decision); twin owned by L5 (no decision)
  S5-column (L7): passed: in the layout, the total column is left out; the ARS file still has its analyses. visible 6 of 24 gold cells wrong, strict 0 of 1; twin 6 of 24 gold cells wrong, strict 0 of 1; visible owned by L7 (no decision); twin owned by L7 (no decision)
  S9-sort (L7): passed: tfl.columns.arms (tfl-ae-summary): {"rule": "protocol_order"} becomes {"rule": "ascending_dose_placebo_first"}. visible 0 of 24 gold cells wrong, strict 0 of 1; twin 0 of 24 gold cells wrong, strict 0 of 1; visible owned by L7 (tfl.columns.arms); twin owned by L7 (tfl.columns.arms); the matrix: separated on the twin
  S10-frozen (L4): not planted: the gold list has one value, and the visible data hold it: a list frozen from them is the gold list
  S11-quote (L0): passed: trt.planned.source (mod-treatment): the quote gets words the document does not have. reading quote: wrong for trt.planned.source
  S12-span (L0): passed: trt.planned.source (mod-treatment): the citation names the anchor 1/s2, that of another decision; the quote is unchanged. reading span: wrong for trt.planned.source
  sweep of the matrix: 28 other values of 22 decisions, each as the one wrong decision of a candidate: 19 shown on the twin and 8 silent, as the matrix says; 1 shown on the visible data only; 273 wrong cells and axes, each owned by the changed decision and confirmed; 0 problems
```

- `gold`: the scorer builds the gold decisions of the kit on both datasets
  and holds the build against the files of the kit: the grid as a whole
  (IDs, texts, the ARD rows of every cell), every result, every value of
  every ADaM column. The scorer never reads gold from the files.
- `arm C`: the parser of `specfirst parse` reads `gold/docs/sap.md` of the
  kit; the defaults are the records of the house standards document.
- `arm S`: reported, it decides nothing.
- The planted defects, one line each, with what the matrix of the kit says
  of a planted decision. `silent`: no cell of either dataset shows the
  planted value; the reading score has it wrong by value.
- The sweep (ADR-008, decision 9): every decision of the kit read as each
  other value of its matrix, each as the one wrong decision of a candidate.

Arm C on the ten kits:

```text
  arm C, stage C: 22 decisions: value 22 of 22; status 22 of 22; quote 22 of 22; span 22 of 22; visible: produced 1 of 1; cells correct 30 of 30, 30 and 30; strict 1 of 1; lenient 1 of 1; twin: produced 1 of 1; cells correct 30 of 30, 30 and 30; strict 1 of 1; lenient 1 of 1: 100%
  arm C, stage T: 7 decisions: value 7 of 7; status 7 of 7; quote 7 of 7; span 7 of 7; visible: produced 1 of 1; cells correct 30 of 30, 30 and 30; strict 1 of 1; lenient 1 of 1; twin: produced 1 of 1; cells correct 30 of 30, 30 and 30; strict 1 of 1; lenient 1 of 1: 100%
  arm C, stage C: 22 decisions: value 22 of 22; status 22 of 22; quote 22 of 22; span 22 of 22; visible: produced 1 of 1; cells correct 18 of 18, 18 and 18; strict 1 of 1; lenient 1 of 1; twin: produced 1 of 1; cells correct 18 of 18, 18 and 18; strict 1 of 1; lenient 1 of 1: 100%
  arm C, stage T: 7 decisions: value 7 of 7; status 7 of 7; quote 7 of 7; span 7 of 7; visible: produced 1 of 1; cells correct 18 of 18, 18 and 18; strict 1 of 1; lenient 1 of 1; twin: produced 1 of 1; cells correct 18 of 18, 18 and 18; strict 1 of 1; lenient 1 of 1: 100%
  arm C, stage C: 21 decisions: value 21 of 21; status 21 of 21; quote 21 of 21; span 21 of 21; visible: produced 1 of 1; cells correct 16 of 16, 16 and 16; strict 1 of 1; lenient 1 of 1; twin: produced 1 of 1; cells correct 16 of 16, 16 and 16; strict 1 of 1; lenient 1 of 1: 100%
  arm C, stage T: 7 decisions: value 7 of 7; status 7 of 7; quote 7 of 7; span 7 of 7; visible: produced 1 of 1; cells correct 16 of 16, 16 and 16; strict 1 of 1; lenient 1 of 1; twin: produced 1 of 1; cells correct 16 of 16, 16 and 16; strict 1 of 1; lenient 1 of 1: 100%
  arm C, stage C: 22 decisions: value 22 of 22; status 22 of 22; quote 22 of 22; span 22 of 22; visible: produced 1 of 1; cells correct 15 of 15, 15 and 15; strict 1 of 1; lenient 1 of 1; twin: produced 1 of 1; cells correct 15 of 15, 15 and 15; strict 1 of 1; lenient 1 of 1: 100%
  arm C, stage T: 7 decisions: value 7 of 7; status 7 of 7; quote 7 of 7; span 7 of 7; visible: produced 1 of 1; cells correct 15 of 15, 15 and 15; strict 1 of 1; lenient 1 of 1; twin: produced 1 of 1; cells correct 15 of 15, 15 and 15; strict 1 of 1; lenient 1 of 1: 100%
  arm C, stage C: 21 decisions: value 21 of 21; status 21 of 21; quote 21 of 21; span 21 of 21; visible: produced 1 of 1; cells correct 20 of 20, 20 and 20; strict 1 of 1; lenient 1 of 1; twin: produced 1 of 1; cells correct 20 of 20, 20 and 20; strict 1 of 1; lenient 1 of 1: 100%
  arm C, stage T: 7 decisions: value 7 of 7; status 7 of 7; quote 7 of 7; span 7 of 7; visible: produced 1 of 1; cells correct 20 of 20, 20 and 20; strict 1 of 1; lenient 1 of 1; twin: produced 1 of 1; cells correct 20 of 20, 20 and 20; strict 1 of 1; lenient 1 of 1: 100%
  arm C, stage C: 21 decisions: value 21 of 21; status 21 of 21; quote 21 of 21; span 21 of 21; visible: produced 1 of 1; cells correct 30 of 30, 30 and 30; strict 1 of 1; lenient 1 of 1; twin: produced 1 of 1; cells correct 30 of 30, 30 and 30; strict 1 of 1; lenient 1 of 1: 100%
  arm C, stage T: 7 decisions: value 7 of 7; status 7 of 7; quote 7 of 7; span 7 of 7; visible: produced 1 of 1; cells correct 30 of 30, 30 and 30; strict 1 of 1; lenient 1 of 1; twin: produced 1 of 1; cells correct 30 of 30, 30 and 30; strict 1 of 1; lenient 1 of 1: 100%
  arm C, stage C: 22 decisions: value 22 of 22; status 22 of 22; quote 22 of 22; span 22 of 22; visible: produced 1 of 1; cells correct 24 of 24, 24 and 24; strict 1 of 1; lenient 1 of 1; twin: produced 1 of 1; cells correct 24 of 24, 24 and 24; strict 1 of 1; lenient 1 of 1: 100%
  arm C, stage T: 7 decisions: value 7 of 7; status 7 of 7; quote 7 of 7; span 7 of 7; visible: produced 1 of 1; cells correct 24 of 24, 24 and 24; strict 1 of 1; lenient 1 of 1; twin: produced 1 of 1; cells correct 24 of 24, 24 and 24; strict 1 of 1; lenient 1 of 1: 100%
  arm C, stage C: 21 decisions: value 21 of 21; status 21 of 21; quote 21 of 21; span 21 of 21; visible: produced 1 of 1; cells correct 16 of 16, 16 and 16; strict 1 of 1; lenient 1 of 1; twin: produced 1 of 1; cells correct 16 of 16, 16 and 16; strict 1 of 1; lenient 1 of 1: 100%
  arm C, stage T: 7 decisions: value 7 of 7; status 7 of 7; quote 7 of 7; span 7 of 7; visible: produced 1 of 1; cells correct 16 of 16, 16 and 16; strict 1 of 1; lenient 1 of 1; twin: produced 1 of 1; cells correct 16 of 16, 16 and 16; strict 1 of 1; lenient 1 of 1: 100%
  arm C, stage C: 22 decisions: value 22 of 22; status 22 of 22; quote 22 of 22; span 22 of 22; visible: produced 1 of 1; cells correct 24 of 24, 24 and 24; strict 1 of 1; lenient 1 of 1; twin: produced 1 of 1; cells correct 24 of 24, 24 and 24; strict 1 of 1; lenient 1 of 1: 100%
  arm C, stage T: 7 decisions: value 7 of 7; status 7 of 7; quote 7 of 7; span 7 of 7; visible: produced 1 of 1; cells correct 24 of 24, 24 and 24; strict 1 of 1; lenient 1 of 1; twin: produced 1 of 1; cells correct 24 of 24, 24 and 24; strict 1 of 1; lenient 1 of 1: 100%
  arm C, stage C: 22 decisions: value 22 of 22; status 22 of 22; quote 22 of 22; span 22 of 22; visible: produced 1 of 1; cells correct 18 of 18, 18 and 18; strict 1 of 1; lenient 1 of 1; twin: produced 1 of 1; cells correct 18 of 18, 18 and 18; strict 1 of 1; lenient 1 of 1: 100%
  arm C, stage T: 7 decisions: value 7 of 7; status 7 of 7; quote 7 of 7; span 7 of 7; visible: produced 1 of 1; cells correct 18 of 18, 18 and 18; strict 1 of 1; lenient 1 of 1; twin: produced 1 of 1; cells correct 18 of 18, 18 and 18; strict 1 of 1; lenient 1 of 1: 100%
```

Arm S at stage T on the ten kits (on the chain it builds nothing in any
kit, for the reason above):

```text
  arm S, stage T: 1 of 7 decisions to change (tfl.columns.total); visible: produced 1 of 1; cells correct 24 of 30, 30 and 30; strict 0 of 1; lenient 0 of 1; twin: produced 1 of 1; cells correct 25 of 30, 30 and 30; strict 0 of 1; lenient 0 of 1
  arm S, stage T: 3 of 7 decisions to change (tfl.population, tfl.columns.total, tfl.percent.format); visible: produced 1 of 1; cells correct 12 of 18, 18 and 18; strict 0 of 1; lenient 0 of 1; twin: produced 1 of 1; cells correct 8 of 18, 18 and 18; strict 0 of 1; lenient 0 of 1
  arm S, stage T: 4 of 7 decisions to change (tfl.columns.total, tfl.percent.format, tfl.rounding.rule, tfl.ae.summary.rows); visible: produced 1 of 1; cells correct 12 of 16, 16 and 16; strict 0 of 1; lenient 0 of 1; twin: produced 1 of 1; cells correct 9 of 16, 16 and 16; strict 0 of 1; lenient 0 of 1
  arm S, stage T: 3 of 7 decisions to change (tfl.population, tfl.columns.total, tfl.ae.summary.rows); visible: produced 1 of 1; cells correct 4 of 15, 15 and 15; strict 0 of 1; lenient 0 of 1; twin: produced 1 of 1; cells correct 7 of 15, 15 and 15; strict 0 of 1; lenient 0 of 1
  arm S, stage T: 4 of 7 decisions to change (tfl.population, tfl.columns.arms, tfl.percent.format, tfl.ae.summary.rows); visible: produced 1 of 1; cells correct 7 of 20, 20 and 20; strict 0 of 1; lenient 0 of 1; twin: produced 1 of 1; cells correct 7 of 20, 20 and 20; strict 0 of 1; lenient 0 of 1
  arm S, stage T: 2 of 7 decisions to change (tfl.percent.format, tfl.rounding.rule); visible: produced 1 of 1; cells correct 18 of 30, 30 and 30; strict 0 of 1; lenient 0 of 1; twin: produced 1 of 1; cells correct 21 of 30, 30 and 30; strict 0 of 1; lenient 0 of 1
  arm S, stage T: 1 of 7 decisions to change (tfl.percent.format); visible: produced 1 of 1; cells correct 18 of 24, 24 and 24; strict 0 of 1; lenient 0 of 1; twin: produced 1 of 1; cells correct 19 of 24, 24 and 24; strict 0 of 1; lenient 0 of 1
  arm S, stage T: 5 of 7 decisions to change (tfl.population, tfl.columns.arms, tfl.percent.format, tfl.rounding.rule, tfl.ae.summary.rows); visible: produced 1 of 1; cells correct 6 of 16, 16 and 16; strict 0 of 1; lenient 0 of 1; twin: produced 1 of 1; cells correct 1 of 16, 16 and 16; strict 0 of 1; lenient 0 of 1
  arm S, stage T: 5 of 7 decisions to change (tfl.population, tfl.columns.arms, tfl.columns.total, tfl.percent.format, tfl.rounding.rule); visible: produced 1 of 1; cells correct 3 of 24, 24 and 24; strict 0 of 1; lenient 0 of 1; twin: produced 1 of 1; cells correct 0 of 24, 24 and 24; strict 0 of 1; lenient 0 of 1
  arm S, stage T: 1 of 7 decisions to change (tfl.rounding.rule); visible: produced 1 of 1; cells correct 17 of 18, 18 and 18; strict 0 of 1; lenient 0 of 1; twin: produced 1 of 1; cells correct 16 of 18, 18 and 18; strict 0 of 1; lenient 0 of 1
```

What each kit leaves unseparated on its twin. The scorer compares these by
value and lists them apart (section 9.3; ADR-007, "The owner's answer on
decision 6"):

```text
  unseparated on the twin by the matrix of the kit, compared by value only: 8: date.studyday.origin, disp.status.record, pop.efficacy.rule, pop.randomized.rule, trt.actual.source, trt.end.source, pop.safety.grouping, pop.safety.rule (read by the table: pop.safety.grouping, pop.safety.rule)
  unseparated on the twin by the matrix of the kit, compared by value only: 7: date.studyday.origin, disp.status.record, pop.efficacy.rule, pop.safety.grouping, pop.safety.rule, trt.actual.source, trt.end.source
  unseparated on the twin by the matrix of the kit, compared by value only: 6: ae.related.values, date.studyday.origin, disp.status.record, pop.randomized.rule, pop.safety.grouping, pop.safety.rule (read by the table: pop.safety.grouping, pop.safety.rule)
  unseparated on the twin by the matrix of the kit, compared by value only: 8: date.studyday.origin, disp.status.record, pop.randomized.rule, pop.safety.grouping, trt.actual.source, trt.end.source, pop.safety.rule, tfl.rounding.rule (read by the table: pop.safety.rule, tfl.rounding.rule)
  unseparated on the twin by the matrix of the kit, compared by value only: 5: date.studyday.origin, pop.safety.grouping, pop.safety.rule, trt.actual.source, trt.end.source
  unseparated on the twin by the matrix of the kit, compared by value only: 6: date.studyday.origin, disp.status.record, pop.randomized.rule, trt.actual.source, trt.end.source, pop.safety.rule (read by the table: pop.safety.rule)
  unseparated on the twin by the matrix of the kit, compared by value only: 5: date.studyday.origin, pop.efficacy.rule, pop.randomized.rule, trt.actual.source, pop.safety.rule (read by the table: pop.safety.rule)
  unseparated on the twin by the matrix of the kit, compared by value only: 6: ae.related.values, date.studyday.origin, pop.safety.grouping, pop.safety.rule, trt.actual.source, trt.end.source
  unseparated on the twin by the matrix of the kit, compared by value only: 8: date.studyday.origin, disp.status.record, pop.randomized.rule, pop.safety.grouping, trt.actual.source, pop.safety.rule, tfl.rounding.rule, trt.end.source (read by the table: pop.safety.rule, tfl.rounding.rule, trt.end.source)
  unseparated on the twin by the matrix of the kit, compared by value only: 6: date.studyday.origin, disp.status.record, pop.efficacy.rule, pop.randomized.rule, trt.end.source, trt.planned.source
```

The sweeps:

```text
  sweep of the matrix: 31 other values of 22 decisions, each as the one wrong decision of a candidate: 21 shown on the twin and 10 silent, as the matrix says; 0 shown on the visible data only; 343 wrong cells and axes, each owned by the changed decision and confirmed; 0 problems
  sweep of the matrix: 30 other values of 22 decisions, each as the one wrong decision of a candidate: 21 shown on the twin and 9 silent, as the matrix says; 0 shown on the visible data only; 164 wrong cells and axes, each owned by the changed decision and confirmed; 0 problems
  sweep of the matrix: 29 other values of 21 decisions, each as the one wrong decision of a candidate: 21 shown on the twin and 8 silent, as the matrix says; 0 shown on the visible data only; 172 wrong cells and axes, each owned by the changed decision and confirmed; 0 problems
  sweep of the matrix: 31 other values of 22 decisions, each as the one wrong decision of a candidate: 21 shown on the twin and 10 silent, as the matrix says; 0 shown on the visible data only; 190 wrong cells and axes, each owned by the changed decision and confirmed; 0 problems
  sweep of the matrix: 29 other values of 21 decisions, each as the one wrong decision of a candidate: 22 shown on the twin and 7 silent, as the matrix says; 0 shown on the visible data only; 200 wrong cells and axes, each owned by the changed decision and confirmed; 0 problems
  sweep of the matrix: 28 other values of 21 decisions, each as the one wrong decision of a candidate: 20 shown on the twin and 8 silent, as the matrix says; 0 shown on the visible data only; 270 wrong cells and axes, each owned by the changed decision and confirmed; 0 problems
  sweep of the matrix: 28 other values of 22 decisions, each as the one wrong decision of a candidate: 22 shown on the twin and 6 silent, as the matrix says; 0 shown on the visible data only; 244 wrong cells and axes, each owned by the changed decision and confirmed; 0 problems
  sweep of the matrix: 29 other values of 21 decisions, each as the one wrong decision of a candidate: 19 shown on the twin and 10 silent, as the matrix says; 0 shown on the visible data only; 143 wrong cells and axes, each owned by the changed decision and confirmed; 0 problems
  sweep of the matrix: 28 other values of 22 decisions, each as the one wrong decision of a candidate: 19 shown on the twin and 8 silent, as the matrix says; 1 shown on the visible data only; 273 wrong cells and axes, each owned by the changed decision and confirmed; 0 problems
  sweep of the matrix: 30 other values of 22 decisions, each as the one wrong decision of a candidate: 23 shown on the twin and 7 silent, as the matrix says; 0 shown on the visible data only; 308 wrong cells and axes, each owned by the changed decision and confirmed; 0 problems
```

The checks of the kits fail on what they are for (rule R5), and the result
of the set:

```text
the checks on planted defects, on the first kit that passes:
  planted in the gold of the kit: the first cell of the twin's grid reads '(N=48)9': the gold check fails: yes
  planted in the document: the statement [1/s1] of trt.actual.source is taken out: the control is not 100%; wrong by value: trt.actual.source: the control fails: yes
  planted in the matrix: the pair of tfl.population with randomized says the opposite: the comparison with the matrix fails: yes

planted defects on 10 kits: per defect, the kits by outcome
  S1-arms (L6): detected and attributed on 10 kits; 
  S2-set (L5): detected and attributed on 10 kits; 
  S2-set-rule (L4): detected and attributed on 6 kits; silent on 4
  S3-window (L4): detected and attributed on 3 kits; not planted on 7
  S4-denominator (L5): detected and attributed on 10 kits; 
  S5-column (L7): detected and attributed on 8 kits; not planted on 2
  S9-sort (L7): detected and attributed on 10 kits; 
  S10-frozen (L4): detected and attributed on 5 kits; not planted on 3; silent on 2
  S11-quote (L0): detected and attributed on 10 kits; 
  S12-span (L0): detected and attributed on 10 kits; 
sweep of the matrices: 293 other values, each as the one wrong decision of a candidate: 209 shown on the twin, 1 on the visible data only, 83 silent; 2307 wrong cells and axes owned by the changed decision and confirmed; 0 problems
  the layer at which each decision owns its cells: ae.related.values L4; ae.start.imputation L4; ae.teae.end L4; ae.teae.start L4; disp.status.record L4; pop.efficacy.rule L4; pop.randomized.rule L4; pop.safety.grouping L5; pop.safety.rule L4; tfl.ae.summary.rows L5; tfl.columns.arms L7; tfl.columns.total L5; tfl.output.include L5; tfl.percent.format L7; tfl.population L5; tfl.rounding.rule L7; trt.actual.source L4; trt.date.imputation L4; trt.end.source L4; trt.planned.source L4; trt.start.source L4
gold built again is the gold of the kit: 10 of 10 kits
parser control 100% in both stages: 10 of 10 kits
planted defects that failed: 0
disagreements with the matrices of the kits: 0
every defect that applies is detected and attributed on at least one kit: yes
the checks fail on their planted defects: yes
kits: PASS
-- PASS kits of gen-2a (265.2 s)
```

Read with it:

- Per defect: S1-arms, S2-set, S4-denominator, S9-sort, S11-quote and
  S12-span are detected and attributed on all ten kits. S2-set-rule on
  six; on four the rule of the safety set is silent, and the matrices of
  those kits mark the pair unseparated. S3-window on the three kits whose
  gold decision names a window of days. S5-column on the eight kits whose
  gold table has a total column. S10-frozen on five; three kits state a
  list of one value, and in two the table has no row of related events,
  so the list is silent there, as their matrices say.
- A planted decision is held against the matrix of the kit wherever the
  matrix has the pair: no disagreement. The window one day longer is a
  slot of the gold alternative, which no matrix holds as a pair.
- `not planted` and `silent` on a kit do not fail the gate; the reading
  of the gate text that allows it is in ADR-008, decision 8, and is point
  1 for the owner below.
- Arm S at stage T is the floor that arm R is compared with (read-2a). It
  is low where a kit states table decisions: the analysis set, the total
  column, the rows.

## What the sweep found

The planted defects of section 9.5 are one case per kind of error. They
passed on HAND01 and on the ten kits at the first run. The sweep then
failed on every kit: a candidate that reads `trt.planned.source` or
`trt.actual.source` as another value writes other treatment labels, the
headers of the treatment columns change, and the axis was owned by "no
decision, layer L7". Every wrong cell of those candidates was owned
rightly. The walk of an axis started at the analyses and never looked at
the data (lesson 52). `attribute._own_axis` now walks the data first, like
the walk of a cell, and the sweep is a check of the gate.

## The gate

`scripts/clean_clone_gate.sh read-1a`, run from the worktree at `55dba60`
under the lock the sessions share: a clean clone, a fresh install of the
Python environment, the R library and CDISC CORE, a fresh fetch of the
pinned sources, then `specfirst gate read-1a --clean`.

```text
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 bash scripts/clean_clone_gate.sh read-1a
...
clean clone gate read-1a: PASS (clone: /tmp/specfirst-clean-1v6CL8/specfirst)
```

The 1028 unit tests of check 4 include `tests/unit/test_score_kit.py`,
which writes one kit of another seed and holds the checks of the kits
against planted defects (rule R5): a gold grid with another text, a
result, an ADaM column and a gold decision that differ; a document
without one statement; a matrix that says the opposite of one pair; a
machine that proves no `decides` edge.

The gate of the first half ran on `e091d15` and failed in its last check
by design (13 of 14: no kit had been scored). Its log is
`docs/reports/read-1a.first-half.gate.log`.

```text
gate read-1a at commit 55dba60a5df1d12272b0a5660a627a928f5e6189 (clean)
...
PASS  environment          0.4 s
PASS  pins                 1.1 s
PASS  lint                 0.1 s
PASS  unit tests         213.5 s
PASS  hand-made study      1.1 s
PASS  separation          31.9 s
PASS  parser control       1.0 s
PASS  standard alone       0.1 s
PASS  planted defects      2.9 s
PASS  pilot                0.4 s
PASS  pilot tests          1.0 s
PASS  kits of gen-2a     265.2 s
PASS  cache untouched      0.1 s
PASS  ASCII                0.0 s
GATE read-1a: PASS

clean clone gate read-1a: PASS (clone: /tmp/specfirst-clean-1v6CL8/specfirst)
The clone does not last: under WSL /tmp is cleared when the instance restarts, about a
minute after the last command ends. Copy what must be kept in the same command that
runs this script (docs/lessons.md, lesson 39). The log is in build/gates/read-1a/ here.
```

The complete output is `docs/reports/read-1a.gate.log`.

## GitHub and CI

`track/read` is pushed to the private origin. CI (`make lint`, `make
ascii`, `make test`) on `track/read`: success on `55dba60`, the commit of
the gate (run 44244463001), and before it on `134c6f7`, the end of the
first half (run 44167007496).

## The review

Not run yet. Rule R7: a fresh-context reviewer signs
`docs/reports/read-1a.review.md` before the merge.

## For the owner

`docs/decisions/ADR-008.md`, "For the owner", has these in full.

1. How this part reads the text of its gate. Which planted defects "apply
   to the slice" is said by a table this part wrote: nine of twelve, two of
   them as the nearest thing the slice has (the order of the treatment
   columns for "an unstable sort", the list of related causality values
   for "a frozen site list"). On the kits a planted defect may be `silent`
   (the matrix of the kit says the twin cannot show it) or `not planted`
   (the kit has nothing to plant it in); every defect is detected and
   attributed on at least one kit. Lesson 47 says such a reading is the
   owner's to accept.
2. Arm S builds nothing on the chain, in any study (`ae.related.values`
   has no default in `catalog@1`). "R against S" is then a comparison with
   zero on the chain, and arm S says something at stage T only. A default,
   or an ADAE that builds without the decision, belongs to the std track.
3. The sweep is a check of the gate that its text does not ask for.
4. The pilot's crosswalk of rows.

## Limits

- The kits are ten kits of one development seed, with one output. What
  the scorer does on kits of another seed is not in the gate; the unit
  tests write one kit of another seed.
- The matrix of a kit changes one decision at a time, and so does the
  sweep. Two wrong decisions can cancel in a table (docs/state/gen.md);
  the scorer gives a cell one owner and lists a second wrong decision as
  "behind another owner" only when it shows alone.
- A wrong value of a slot of the gold alternative is in the matrix for one
  decision only (`ae.related.values`). The window off by one day is such a
  value: it is planted where the gold decision names a window, and nothing
  holds it against a matrix.
- The frozen list is planted on a kit with visible data that lack the
  records of one causality value. The visible data of the ten kits hold
  every value, so it could not be planted otherwise.
- The candidate is built with the Python engine only. Rule R11 is the
  business of the gold build (gen-2a).
- Documents are in standard form. The anchors of natural-form documents
  come with gen-3a. No kit has a decision with the status `asked` or a
  list of what the catalog lacks: the two rates of the reading score are
  computed and have nothing to judge yet.
- Not in this part: the three layers of ADaM scoring of section 9.3, the
  cost dimension, questions answered by an oracle (read-2a).
