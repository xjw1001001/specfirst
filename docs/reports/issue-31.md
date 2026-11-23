# Issue #31 A calculation-first review view and a study decision sheet: report

Date: 2026-11-22. Branch: `track/real`. Issue #31 of `xjw1001001/specfirst`:
"[viewer] A calculation-first review view: click a number for the analysis,
decisions, why each variable and its derivation, the recomputation; plus a
study decision sheet". The design was sent to the owner through the base
session; the owner chose the recommended option of each question (Q1 to Q4)
and of the overlap with std-2 (ADR-022, "The owner's answers"), and, after
the first review, of the question of the SAP's mock tables (ADR-022, "The
owner's answer"). Decisions: docs/decisions/ADR-022.md. catalog-2c merged
to main first; track/real took main 0046194 in (`b23dafb`), then drew the
pilot's P4 classes on the page (`78fb49b`, `bfdcadf`; section "P4").

## Verdict

- `specfirst view cdiscpilot01` writes the review page of the built pilot.
  It has no script and fetches nothing, and it starts with the
  calculation. Each of 1502 printed cells opens the panel of its analysis
  (61 panels). The decision sheet has 93 lines: 67 records, the 17 entries
  of catalog@2 that no record takes, the kit's binding and 8 layouts. Two
  builds give the same page byte for byte.
- The acceptance holds on CDISCPILOT01's demographics and AE tables
  (Out14-1-1, Out14-3-1-1 and Out14-3-2-1: 84, 27 and 1178 printed
  numbers). Every number opens its panel, reaches SDTM, reaches a
  citation or a house default, and draws every decision behind it. This is
  held on the review and read back from the page by the gate's check
  `review`, which fails on each of D13's plants.
- The grids of the two new tables are built and compared with CDISC's
  example: 90 of Out14-1-1's 104 cells equal it, and the other 14 differ by
  results already classed. Of Out14-3-2-1's 1275 cells, 866 equal it, one
  differs (the p-value of 1, the one entry of `formats`) and 408 have no
  formatted reference value.
- 49 records of the two tables over catalog@2 and open-default@2:
  18 stated, 12 default, 17 conflict, 2 asked. All 102 quotes are found in
  their documents, with 0 problems. None of the 17 conflicts and 2 asked
  records is resolved here; they are for the owner, and none blocks.
- P4: the pilot's matrix (the house vector) draws a class on the 14
  records at its value, with the condition in a note. The 7 records at
  another value are not tested. This is the owner's answer A
  (2026-11-22).
- The gate issue-31 passes on a clean clone of `bfdcadf`. It and read-1a,
  issue-29, real-2, real-3a, real-5a and real-5b pass on clean clones of
  `78fb49b`, the work with main 0046194 (catalog-2c) merged in.
- PLAN.md and `standard/` are unchanged (no schema, catalog, house or
  registry change), and so is `env/`. The kit gains files of its own and a
  `standard` key (ADR-022, decision 7, the owner's answer of 2026-11-21).

## What the issue asks for, and where it stands

| The issue asks | Where |
| --- | --- |
| The grid, texts and RTF folded by default; the calculation first | each output of the page starts with its analyses, each in a sentence with its recomputation; the grid, its titles and footnotes, and a line on the RTF (not built) are in `<details>` (ADR-022, decision 1) |
| Click any number: a side panel | every printed number of every grid is a link to its cell's block in the panel of its analysis; 1502 cells with a panel (section "The page") |
| 1. The analysis in plain sentences | who (the analysis set), which records (the data subset), which groups, which statistic, its options and where each comes from, as `specfirst.recompute.reading` reads them (decision 2) |
| 2. The decisions: standard-form sentence, alternatives not chosen, citation, house default or customized | every record that binds the analysis or one of its elements, then every record that binds a column it reads or a column those derive from, down to SDTM; each with its statement, the alternatives of its catalog entry it does not take, its citations (each quote checked by script, awaiting approval), its mark and its P4 class (decisions 2, 3, 7) |
| 3. The ADaM variables it reads: why this variable, its derivation as one sentence, down to SDTM | the `reads` edges with their roles; why: the records that bind the column; its derivation in the study spec's own words (the Define-XML comment) next to the rule that runs with its file and line, for every column it derives from, down to the SDTM columns (the owner's answer to Q3) |
| 4. The recomputation and a link to the code that ran | the line of issue #29's report and the text of the script, in a fold |
| A study decision sheet, every study-level decision and template setting, each house default or study customized, with its citation | the sheet: 67 records (49 of the two tables, 18 of the efficacy tables), the 17 entries of catalog@2 no record takes, the kit's binding (sas5, the house default through catalog@2's tfl.quantile.definition) and the 8 layouts; 93 lines (decision 3) |
| Edge classes drawn distinctly: proven by execution, judged (a named approver), not proven by the data | six kinds, never merged: executed, static, judged ("awaiting approval": the owner's answer to Q4), unseparated, tested by P4, not tested (decision 4) |
| Acceptance, on CDISCPILOT01's demographics and AE tables: every printed number opens the panel | 84, 27 and 1178 printed numbers of Out14-1-1, Out14-3-1-1 and Out14-3-2-1, all with a panel |
| Every panel reaches SDTM and a citation or a house default | all of them, held on the review and read back from the page (the check `review`) |
| The decision sheet lists every study-level decision | all 67 records and every entry of the catalog the kit names, read back from the rows of the page (the check `review`) |

## The grids

The owner's answer to Q2: #31 builds the demographics (Out14-1-1) and the
table by organ class and term (Out14-3-2-1) of CDISC's example first. Their
layouts follow the example's table shells (Demog_Table_Shell.rtf and
AE_SOC_PT_Table_Shell.rtf in the pinned ARS repository). Two layout pieces
were needed (ADR-022, decision 6): the extra cells of a groups block (the
chi-square p-value of age group, sex, ethnicity and race in the first row of
each), and the block kind `terms` (the organ classes the results have, A to
Z, each followed by its terms, with the Fisher p-values of placebo against
each active arm in two columns under one spanner).

The check `grids` of the gate issue-31 (the clean clone of `bfdcadf`; its
log, docs/reports/issue-31.clean-clone.gate.log), its lines of the three
outputs of the issue (the efficacy grids follow in the log):

```text
== [8/14] grids: specfirst check cdiscpilot01 --build build/p1/cdiscpilot01/first (its last part), the ARS example
grid Out14-1-1: 104 cells show 147 results; 90 cells equal the reference's formatted values, 14 differ, 14 of them with one class
  14 cells differ by a result classed reference_error
grid Out14-1-1: the R engine's rows give the same grid; the mock shell and the two pages hold; 0 problems
grid Out14-3-1-1: 27 cells show 51 results; 27 cells equal the reference's formatted values, 0 differ, 0 of them with one class
grid Out14-3-1-1: the R engine's rows give the same grid; the mock shell and the two pages hold; 0 problems
grid Out14-3-2-1: 1275 cells show 1940 results; 866 cells equal the reference's formatted values, 1 differ, 1 of them with one class
  1 cells differ by a result classed reference_error
  results the reference gives no formatted value for: 408 (their cells are not compared)
grid Out14-3-2-1: the R engine's rows give the same grid; the mock shell and the two pages hold; 0 problems
```

The 14 cells of Out14-1-1 differ by results the section `results` of
gold/exceptions.yaml classes already; the one cell of Out14-3-2-1 is the
Fisher p-value of 1 that the example shows "1", the one entry of the
section `formats`. `gates.PILOT_GRIDS` pins the cells, results and
uncompared results of the three outputs (104, 147, 0; 27, 51, 0; 1275,
1940, 408), and `equal + classified + uncompared == cells` holds for each.

## The citations of the ARS file

CDISC's example names the SAP of the pilot as `CDISCPILOT01_SAP`, and its
sap.pdf has the SHA-256 of the kit's SAP. Its references to the SAP (24
analyses and their methods) are judged, imported `cites` edges now, from
every analysis of a built grid: 13 analyses (the safety population and the
12 of the demographics) and the methods name a page, and a script finds the
reference's label on that page; the 9 adverse event analyses name the
section "11.2. Adverse Events" without a page, so their edge goes to the
SAP as a whole and the script finds the label anywhere in it; the 2 of the
vital signs are not built. None is approved. On the build (coverage.json,
`documents`): 38 edges to 4 spans, 38 quotes verified, 9 of the edges to
the whole document, no reference to a document the kit lacks.

## The decision records of the two tables

The owner's answers to Q1 and to the overlap with std-2: the file
kits/cdiscpilot01/gold/decisions/safety.jsonl holds 49 records of the
demographics and AE tables over `catalog@2` and `open-default@2`: 44 of
catalog entries and 5 custom. std-2 takes the file over, extends it to the
whole pilot and adds its check by result; this package does not claim that
check.

The documents read are the SAP's text (sections 6, 7, 9, 11 and the list of
its tables, 13.1.1), its mock tables (13.2: Template 3 for the demographics,
Template 13 for the table by organ class and term; it has none for the AE
summary) and the Define-XML of ADaM. A mock table states what it shows: its
population, its columns and their order, and the decimals of its masks;
that is the owner's answer of 2026-11-22 (option A of three; ADR-022, "The
owner's answer"). The SAP itself says (13.1.3): "Note that the templates
that follow are for example only." The first review of this package found that the
records had not read the mock tables (F1); the statuses below are those of
the second reading.

| Status | Records | What it means |
| --- | --- | --- |
| stated | 18 | a document of the kit (the SAP's text or a mock table, the Define-XML) states the value; the record cites its quote |
| default | 12 | the value is the house's default and no document of the kit states it; the record cites the house standard's statement |
| conflict | 17 | a document of the kit says other than the build does; the record keeps the build's value and cites the document |
| asked | 2 | no document states it and it is not the house's default: CDISC's example does it (class `gold_quirk`) |

The check `decisions` of the gate issue-31 holds the 49 records with the 18
efficacy records of gold/decisions/efficacy.jsonl:

```text
== [11/14] decisions: specfirst.machine.build.decision_checks on build/p1/cdiscpilot01/first
decisions: 67 records, 67 IDs; 99 options of analyses held against the decisions that set them; the last visit held on the model records of 3 analyses; 102 quotes held against their documents; 0 problems
decisions: citations of sources that are no document of the kit, not checked by script: answers 5
decisions: by class: 33 document_rule, 2 gold_quirk, 12 house_default, 17 no class (conflict), 3 study_input; by status: 3 asked, 17 conflict, 12 default, 35 stated
decisions: pass
```

Of the statuses, 18 stated, 12 default, 17 conflict and 2 asked are the
safety records' (tests/unit/test_safety_records.py pins them); the rest are
the efficacy records'. The 102 quotes are those of the documents of the kit
and of the house standard, each found in its document's text; the five
citations of the owner's answers (efficacy) are counted, not checked.

For the owner (none blocks): the 17 conflicts and the 2 asked records.

- conflict, of the modules: trt.start.source (the Define-XML takes the date
  of Visit 3 from SV, the build the first exposure); ae.start.imputation
  (the SAP: a conservative imputation; the Define-XML and the build: day
  01); ae.teae.start (the SAP adds events that worsen or recur after the
  first dose; the build takes the start date);
  custom:demog-baseline-visits (the SAP and the Define-XML: height at Visit
  1, weight at Visit 3; the build: the first height by visit number and
  the weight flagged VSBLFL = 'Y'; whether the two give the same values on
  the pilot is std-2's check).
- conflict, of the demographics: tfl.population (Template 3:
  intent-to-treat; the build: the safety population); tfl.columns.total
  (the SAP: "across all treatment groups", and Template 3 has a total
  column; the example has none); tfl.demog.rows (the SAP lists MMSE,
  duration of disease, education, weight and BMI; the example has ethnicity
  and height); tfl.demog.stats (the SAP's continuous statistics have no
  quartiles; the example shows Q1 and Q3); custom:demog-age-display (the
  SAP: three age categories; the example: two); custom:demog-decimals
  (Template 3: the minimum and the maximum with one decimal; the example:
  as the data); tfl.percent.format ("xx (xx%)": whole numbers; the
  example: one decimal); tfl.pvalue.format ("0.xxx": three decimals; the
  example: four).
- conflict, of the AE summary: tfl.output.include (the SAP's list of
  tables has no AE summary) and tfl.ae.summary.rows (SAP 11.4: no formal
  summary of AEs leading to discontinuation; the example has that row).
- conflict, of the table by organ class and term: tfl.ae.socpt.counts
  (Template 13: n (%) and total events; the example: subjects);
  tfl.percent.format ("xx (xx%)"); custom:socpt-pvalue-format ("0.xxx";
  the example: four decimals).
- asked: trt.date.imputation, ae.related.values (POSSIBLE and PROBABLE).

## The page

The check `review` of the gate issue-31 writes the page of the first build
of P1, checks it, holds the acceptance on the three outputs of the issue,
and compares the page of the second build of P1:

```text
== [10/14] review: specfirst view cdiscpilot01 --build build/p1/cdiscpilot01/first
Out14-1-1: 84 printed numbers; 84 open a panel; 84 reach SDTM; 84 reach a citation or a house default; 84 draw every decision behind them
Out14-3-1-1: 27 printed numbers; 27 open a panel; 27 reach SDTM; 27 reach a citation or a house default; 27 draw every decision behind them
Out14-3-2-1: 1178 printed numbers; 1178 open a panel; 1178 reach SDTM; 1178 reach a citation or a house default; 1178 draw every decision behind them
sheet: 17 catalog entry, 1 kit binding, 8 layout, 67 record; 67 of 67 records listed
review: build/p1/cdiscpilot01/first/viewer/index.html has 3885705 bytes, 61 panels of analyses, 1502 cells with a panel, 93 lines on the decision sheet; the second build of P1 gives the same page: True
```

Each count is held on the review the page is written from and read back
from the page: the SDTM columns its lines "Down to SDTM" name, the
citations and house defaults drawn in the panels, the decision blocks of
the panels and the rows of the sheet by their key (the first review, F3).
The page check finds no script, handler, frame, image, form, import,
refresh or link that leaves the page; every link has its anchor, every
anchor stands once; each of the 2505 citations is drawn judged and says
"awaiting approval"; every decision is drawn "not tested". Of the 49
records of the two tables, 45 stand in a panel of a number of the three
tables, 7 of them through a column (the AE start-date imputation, for
one, in the panel of every TEAE count); the other four bind columns no
number of these tables reads and stand on the sheet only.

D13-review (in the check `planted defects`) plants in the page, the
review, the graph files and the exceptions, and each is seen:

```text
planted, a cell without a panel: 1 problems, for example: cell:Out14-3-2-1/r1/c1: prints '(N=86)' and opens no panel
planted, a script: 1 problems, for example: the page has a <script>
planted, a handler: 1 problems, for example: the page has the handler 'onmouseover'
planted, a link that leaves the page: 1 problems, for example: the link 'https://example.org/' leaves the page
planted, a judged edge drawn as proven: 1 problems, for example: citation 1 is drawn executed, not judged
planted, an unseparated decision drawn as proven: 4 problems, for example: the decision ae.related.values (mod-ae-emergence) is unseparated and not drawn so
planted, a decision left off the sheet: 2 problems, for example: the sheet does not list the decision ae.related.values (mod-ae-emergence)
planted, an entry of the catalog left off the sheet: 1 problems, for example: the sheet does not list the entry pop.efficacy.rule (mod-populations) of the catalog
planted, the decision ae.start.imputation (mod-ae-emergence) left off the panels: 1199 problems, for example: cell:Out14-3-1-1/r2/c1: its panel does not draw the decision ae.start.imputation (mod-ae-emergence)
planted, no SDTM column named in the panels: 1289 problems, for example: cell:Out14-1-1/r1/c1: its panel reaches no SDTM column through every column it reads
planted in the graph files, the derives_from edges of ADSL.AGEGR1 left out: 7 cells seen
planted in the exceptions, a difference of display no cell shows: passes False
planted in the exceptions, a difference of display under common-safety-display: passes False
```

## P4

catalog-2c merged first (main 0046194, merged into track/real as
`b23dafb`), so the pilot's matrix is now that of catalog@2 and
open-default@2 (ADR-022, decision 8). The matrix is made for a report only;
no gate runs it (about 22 minutes on four processors). On a scratch copy of
`78fb49b`, under the heavy lock:

```text
$ specfirst gen separate cdiscpilot01 --out build/separation/cdiscpilot01-house.json
P4 by class on cdiscpilot01/sdtm (cdiscpilot01, vector house): 22 decisions of the units mod-treatment, mod-populations, mod-ae-emergence, tfl-ae-summary; outputs Out_AESUM; 71 builds; integer slots scanned up to 30 steps from gold
  unseparated: 9: ae.start.imputation (mod-ae-emergence), ae.teae.end (mod-ae-emergence), ae.teae.start (mod-ae-emergence), pop.safety.rule (mod-populations), tfl.columns.arms (tfl-ae-summary), tfl.rounding.rule (tfl-ae-summary), trt.date.imputation (mod-treatment), trt.end.source (mod-treatment), trt.start.source (mod-treatment)
  separated_at_dataset_only: 0
  separated: 8: ae.related.values (mod-ae-emergence), pop.safety.grouping (mod-populations), tfl.ae.summary.rows (tfl-ae-summary), tfl.columns.total (tfl-ae-summary), tfl.output.include (tfl-ae-summary), tfl.percent.format (tfl-ae-summary), tfl.population (tfl-ae-summary), trt.actual.source (mod-treatment)
  inert: 5: date.studyday.origin (mod-treatment), disp.status.record (mod-populations), pop.efficacy.rule (mod-populations), pop.randomized.rule (mod-populations), trt.planned.source (mod-treatment)
  no_alternative: 0
  values tried, by level: fails 0, outputs 25, results 0, adam 12, none 33
  ...
  problems: 0
matrix written to build/separation/cdiscpilot01-house.json
```

The matrix classes the house vector: the house standard alone for the
adverse event summary. A class holds at the value it was found at (the
matrix's `value`, its gold). Of the kit's 67 records, 21 have a decision in
the matrix. 14 of them hold the matrix's value and are drawn with its
class. The other 7 hold the build's value, which is not the house's, and are
drawn "not tested". Their panels and sheet lines name the value the run
tried and its class (`78fb49b`; ADR-022, decision 8).

The run holds every other decision at the house's value, and the kit
differs from that in 7 of the 21 decisions (the review's pass 3, P3-F1). So
a class drawn names the run's vector in a note, and the legend says so. A
class `no_alternative` is drawn "not tested" (P3-F2; the pilot's matrix has
none). The owner was asked whether to draw the house vector's classes at
all, or none until a run on the kit's own values exists. The owner chose
A, the recommended option, through the base session: show them, and state
the condition (ADR-022, "The owner's answer on P4"). The page is that
option (`bfdcadf`):

```text
$ specfirst view cdiscpilot01 --p4 build/separation/cdiscpilot01-house.json
Out14-1-1: 84 printed numbers; 84 open a panel; 84 reach SDTM; 84 reach a citation or a house default; 84 draw every decision behind them
Out14-3-1-1: 27 printed numbers; 27 open a panel; 27 reach SDTM; 27 reach a citation or a house default; 27 draw every decision behind them
Out14-3-2-1: 1178 printed numbers; 1178 open a panel; 1178 reach SDTM; 1178 reach a citation or a house default; 1178 draw every decision behind them
...
sheet: 17 catalog entry, 1 kit binding, 8 layout, 67 record; 67 of 67 records listed
view cdiscpilot01: .../build/kits/cdiscpilot01/viewer/index.html (3926383 bytes), 61 analyses, 1502 cells with a panel, 93 lines on the sheet; 0 problems
$ grep -o 'the P4 run of the vector house[^<]*)' build/kits/cdiscpilot01/viewer/index.html | sort | uniq -c
     30 the P4 run of the vector house tried another value, dm_actarm: separated)
     62 the P4 run of the vector house tried another value, first_ex_with_dose: unseparated)
     17 the P4 run of the vector house tried another value, first_of_month_not_before_first_dose: unseparated)
     17 the P4 run of the vector house tried another value, last_dose_plus_days(days=30): unseparated)
      1 the P4 run of the vector house tried another value, last_ex_end_date: unseparated)
     62 the P4 run of the vector house tried another value, not_completed: unseparated)
      9 the P4 run of the vector house tried another value, standard_rows: separated)
    264 the P4 run of the vector house, every other decision at that vector&#x27;s value)
```

The P4 column of the sheet's 93 lines then reads:
- tested: 6 separated and 4 inert;
- not proven by the data: 4 unseparated (pop.safety.rule, tfl.columns.arms,
  tfl.rounding.rule, ae.teae.start);
- not tested: 79.

The seven records at another value are:
- trt.actual.source: the kit has `same_as_planned`, the matrix ran at
  `dm_actarm`;
- trt.start.source and trt.end.source;
- trt.date.imputation;
- ae.start.imputation;
- ae.teae.end: the kit has `no_end`, the matrix ran at 30 days after the
  last dose;
- tfl.ae.summary.rows.

Without `--p4` every decision is drawn "not tested", with no note. That is
the page the gate's check `review` holds.

## The gate issue-31

`specfirst gate issue-31` on a clean clone of `bfdcadf`, the commit that
merges, with a fresh install and a fresh fetch, under the heavy lock on
four processors. The log is committed in full as
docs/reports/issue-31.clean-clone.gate.log.

```text
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 bash scripts/clean_clone_gate.sh issue-31 <repository> bfdcadf
PASS  environment          0.5 s
PASS  pins                 1.4 s
PASS  lint                 0.1 s
PASS  unit tests         685.3 s
PASS  kit                  0.2 s
PASS  P1 determinism      63.4 s
PASS  trace                4.3 s
PASS  grids                4.6 s
PASS  recompute           16.5 s
PASS  review               1.4 s
PASS  decisions            1.0 s
PASS  planted defects    190.1 s
PASS  cache untouched      0.1 s
PASS  ASCII                0.0 s
GATE issue-31: PASS
clean clone gate issue-31: PASS (clone: /tmp/specfirst-clean-2OUStQ/specfirst)
```

The unit tests: 1400 passed, 37 deselected. The planted defects: 100
passed (D7-display, D8-trace and D13-review among them, every plant seen).
The check recompute: 69 analyses reproduced, the static check passes on
69 of 69 scripts. The check review:

```text
sheet: 17 catalog entry, 1 kit binding, 8 layout, 67 record; 67 of 67 records listed
review: build/p1/cdiscpilot01/first/viewer/index.html has 3885705 bytes, 61 panels of analyses, 1502 cells with a panel, 93 lines on the decision sheet; the second build of P1 gives the same page: True
```

The check decisions:

```text
decisions: 67 records, 67 IDs; 99 options of analyses held against the decisions that set them; the last visit held on the model records of 3 analyses; 102 quotes held against their documents; 0 problems
```

## The gates on clean clones

`scripts/clean_clone_gate.sh` for issue-31 and for the gates whose checks
the package reaches:
- read-1a, whose pilot report reads the kit;
- issue-29, whose recomputation reads the build;
- real-2, real-3a, real-5a and real-5b, the gates of the pilot kit.

Each ran one gate at a time, under the heavy lock and on four processors,
and each clone got a fresh install and a fresh fetch. Each log is
committed in full.

The commits:
- `5671c8b`, the findings of the first review: issue-31, real-2, real-3a,
  real-5a and real-5b passed on it. issue-29 and read-1a were stopped when
  catalog-2c merged to main, since all seven had to run again on the merge.
  These logs are not committed.
- `78fb49b`, main 0046194 merged in (`b23dafb`) and the P4 part: all seven.
- `bfdcadf`, the two findings of the review's pass 3: issue-31 again. That
  commit changes only src/specfirst/viewer/, its unit test, ADR-022 and the
  state file. Of the seven gates, only issue-31 has checks that reach the
  viewer (its checks review and planted defects); it also runs the whole
  unit suite, as every gate does.
- The commits after `bfdcadf` change documents only (this report, ADR-022's
  record of the owner's answer on P4, the review, the logs).

The exit codes and seconds below are the lines of the loops that ran the
gates; those loops are not committed files. The seconds include the wait
for the lock. Each log shows its own checks and verdict.

```text
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 bash scripts/clean_clone_gate.sh <gate> <repository> 78fb49b
read-1a: exit 0; 14 PASS, 0 FAIL; clean clone gate read-1a: PASS (1424 s)
issue-31: exit 0; 14 PASS, 0 FAIL; clean clone gate issue-31: PASS (959 s)
issue-29: exit 0; 12 PASS, 0 FAIL; clean clone gate issue-29: PASS (755 s)
real-2: exit 0; 15 PASS, 0 FAIL; clean clone gate real-2: PASS (1019 s)
real-3a: exit 0; 16 PASS, 0 FAIL; clean clone gate real-3a: PASS (2232 s)
real-5a: exit 0; 18 PASS, 0 FAIL; clean clone gate real-5a: PASS (1297 s)
real-5b: exit 0; 19 PASS, 0 FAIL; clean clone gate real-5b: PASS (1854 s)
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 bash scripts/clean_clone_gate.sh issue-31 <repository> bfdcadf
issue-31: exit 0; 14 PASS, 0 FAIL; clean clone gate issue-31: PASS (1983 s)
```

| Gate | Commit | Checks | Unit tests | Last lines | Log |
| --- | --- | --- | --- | --- | --- |
| issue-31 | `bfdcadf` | 14 PASS, 0 FAIL | 1400 passed, 37 deselected | `GATE issue-31: PASS`, `clean clone gate issue-31: PASS` | docs/reports/issue-31.clean-clone.gate.log |
| issue-31 | `78fb49b` | 14 PASS, 0 FAIL | 1400 passed, 37 deselected | `GATE issue-31: PASS`, `clean clone gate issue-31: PASS` | docs/reports/issue-31.merged.issue-31.gate.log |
| read-1a | `78fb49b` | 14 PASS, 0 FAIL | 1400 passed, 37 deselected | `GATE read-1a: PASS`, `clean clone gate read-1a: PASS` | docs/reports/issue-31.read-1a.gate.log |
| issue-29 | `78fb49b` | 12 PASS, 0 FAIL | 1400 passed, 37 deselected | `GATE issue-29: PASS`, `clean clone gate issue-29: PASS` | docs/reports/issue-31.issue-29.gate.log |
| real-2 | `78fb49b` | 15 PASS, 0 FAIL | 1400 passed, 37 deselected | `GATE real-2: PASS`, `clean clone gate real-2: PASS` | docs/reports/issue-31.real-2.gate.log |
| real-3a | `78fb49b` | 16 PASS, 0 FAIL | 1400 passed, 37 deselected | `GATE real-3a: PASS`, `clean clone gate real-3a: PASS` | docs/reports/issue-31.real-3a.gate.log |
| real-5a | `78fb49b` | 18 PASS, 0 FAIL | 1400 passed, 37 deselected | `GATE real-5a: PASS`, `clean clone gate real-5a: PASS` | docs/reports/issue-31.real-5a.gate.log |
| real-5b | `78fb49b` | 19 PASS, 0 FAIL | 1400 passed, 37 deselected | `GATE real-5b: PASS`, `clean clone gate real-5b: PASS` | docs/reports/issue-31.real-5b.gate.log |

catalog-2c's own gates (gen-1a, gen-2a, gen-3a, read-2a, catalog-2b,
std-1) are not run again; #31 changes no file of gen, score, harness,
compile or the standard. What #31 changed in machine/ that they import:
- graph.py gains one function (`add_citations`), and `build_graph` is
  unchanged;
- results.py gains `load_formats`;
- grid.py and layout.py change the plan of a grid for the new block kind
  `terms`, the extra cells of a groups block and spanners only. Those are
  layouts that only the pilot kit has.
- `grid.ard_id`, `grid.SCHEMA` and `grid.grid_problems`, which gen calls,
  are unchanged.
- score/pilot.py (read-1a, run again above) calls `grid.plan` on the AE
  summary's layout, which has none of the new features.
- Nothing in gen, score or harness reads `Kit.decisions`.

## The review

A fresh-context reviewer (rule R7) signs docs/reports/issue-31.review.md.

- **Pass 1, of `db50a40`: NOT SIGNED.**
  - F1 blocked: the record statuses had not read the SAP's mock tables
    (13.2, Templates 3 and 13). The owner was asked how a mock table
    counts and chose A: it states what it shows, its masks included
    (ADR-022, "The owner's answer").
  - F2 to F7 did not block:
    - F2: the panels lacked the records of the columns of the derivation
      chain;
    - F3: the acceptance did not read the page back;
    - F4: a reference without a page had no edge;
    - F5: a `formats` key that is no result set passed;
    - F6: the kit's binding and the layouts had no mark, and P4 had no
      kind `tested`;
    - F7: words in a layout comment, ADR-003 and ADR-022.
  - All seven were fixed in `5671c8b`.
- **Pass 2, of `5671c8b`: SIGNED** on the code and the records. F1 to F7
  are closed.
- **Pass 3, of `78fb49b`: SIGNED** on the code and the records. This
  covers the merge `b23dafb` of main 0046194 (the resolution of CLAUDE.md,
  and what score/pilot.py reads) and the P4 part.
  - P3-F1 (not blocking): a class drawn is the house vector's, not the
    kit's, and neither the page nor ADR-022 said so.
  - P3-F2 (not blocking): a class `no_alternative` would have been drawn
    tested.
  - Both were fixed in `bfdcadf`. P3-F1's question, whether to draw the
    house vector's classes at all, went to the owner, who chose A: show
    them and state the condition.
- **Part 2, of this report and its eight logs:** see the review file.

## What is not done

- P4 on the kit's own values: the pilot's matrix is that of the house
  vector, so 7 of the 21 records it reaches are drawn "not tested". A
  vector of the kit's records would be a new vector of gen/separate.py
  (gen's file, not #31's).
- The records are held for their form, their binds and their quotes, not
  by result (std-2).
- The vital signs of the example (the rest of real-3), and approvals of
  judged edges (the edit loop of PLAN.md section 7.6).
- The page is about 3.9 MB for the pilot; it holds the panel of every
  analysis once and a small block per cell.
- Four records of the two tables bind columns that no number of the three
  tables reads (date.studyday.origin, disp.status.record, trt.end.source,
  trt.planned.source): they stand on the sheet only.
