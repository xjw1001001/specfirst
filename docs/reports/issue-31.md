# Issue #31 A calculation-first review view and a study decision sheet: report

Date: 2026-11-22. Branch: `track/real`. Issue #31 of `xjw1001001/specfirst`:
"[viewer] A calculation-first review view: click a number for the analysis,
decisions, why each variable and its derivation, the recomputation; plus a
study decision sheet". The design was sent to the owner through the base
session; the owner chose the recommended option of each question (Q1 to Q4)
and of the overlap with std-2 (ADR-022, "The owner's answers"), and, after
the first review, of the question of the SAP's mock tables (ADR-022, "The
owner's answer"). Decisions: docs/decisions/ADR-022.md.

## Verdict

@@VERDICT@@

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

@@GRIDS@@

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

@@DECISIONS@@

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

@@PAGE@@

## P4

The page draws every decision "not tested" for now: the matrix of `specfirst
gen separate cdiscpilot01` is read after catalog-2c merges, so that its
classes are those of `catalog@2` (ADR-022, decision 8).

## The gate issue-31

@@GATE@@

## The gates on clean clones

@@GATES@@

## The review

@@REVIEW@@

## What is not done

- P4 classes on the page (catalog-2c).
- The records are held for their form, their binds and their quotes, not
  by result (std-2).
- The vital signs of the example (the rest of real-3), and approvals of
  judged edges (the edit loop of PLAN.md section 7.6).
- The page is about 3.9 MB for the pilot; it holds the panel of every
  analysis once and a small block per cell.
- Four records of the two tables bind columns that no number of the three
  tables reads (date.studyday.origin, disp.status.record, trt.end.source,
  trt.planned.source): they stand on the sheet only.
