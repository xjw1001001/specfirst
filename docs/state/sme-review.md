# SME review: the domain judgement points

On 2026-11-23 the owner approved a standing rule. The owner is not a
clinical subject-matter expert (SME). At a domain judgement point, the work
takes the recommended option, backed by a public source, and marks it "per
recommendation, pending SME review". The points that were already waiting
for the owner are handled the same way. This file is the one list an SME
goes through, in one sitting.

Compiled on 2026-11-23 from the documents of `main` at `34bbc14`: the state
files, the ADRs and the reports they name. Nothing else was changed. A
point here is a clinical, statistical or standards question. What stays
with the owner is listed at the end.

The base session keeps this list. A session that takes a recommendation
under the rule tells the base session the record or the decision, and the
base session adds it here. The list has not had a review: each point names
its source, so check the source before acting on a point.

34 points: track real 27 (SME-01 to SME-26, SME-33), read 1 (SME-27),
gen 4 (SME-28, SME-29, SME-32 and SME-34), std 2 (SME-30 and SME-31).

Each point gives the question, where it is decided, the options, the
recommended option with its public source, the current state, and whether
a number in an output changes between the options, as far as the
documents say.

## The general order the documents give

The documents name no recommendation for the 19 records of issue #31
(SME-01 to SME-19): ADR-022, decision 7, leaves every `conflict` and
`asked` record of safety.jsonl for a person. For these records, "General
order" says what the project's own rules give. It is derived here from the
rules below; the documents do not name it as the record's recommendation.

- PLAN.md 4.8 (decision 17): the documents decide; where they are silent,
  the reference ADaM decides; where neither speaks, the house default
  decides. The owner confirms each new case at N2.
- PLAN.md 4.5: documents that contradict each other need a person before
  any class is given.
- The owner's answers of 2026-11-20 (ADR-015), each the recommended option,
  applied these rules to the efficacy tables. Where a document states a
  rule and the reference follows another, gold follows the document, and
  the reference's cell is a `rule_choice` difference with a proof (answer
  1). Where the documents contradict each other or are silent, the reading
  under which the reference's numbers are reproduced is taken; the record
  becomes `stated` and cites the answer (answer 2).

### What the rule does with SME-01 to SME-19 now

The "general order" above was derived when this list was compiled. No
session proposed it, and no source names it as the recommendation. So the
base session does not apply it under the rule:

- Each record keeps the build's value, which reproduces the reference.
  Each is marked "pending SME review" here.
- Taking the general order where it differs (SME-04 to SME-17) would change
  gold and several gates. SME-13 alone would take Out14-3-1-1 out of gold.
  That is a change of scope, so it stays with the owner. It is std-2's
  work once std-2 takes the file over (ADR-022).

## Track real

### Issue #31: the records of safety.jsonl (SME-01 to SME-19)

The file is kits/cdiscpilot01/gold/decisions/safety.jsonl; line numbers
are given below. docs/reports/issue-31.md, "The decision records of the two
tables", and docs/state/real.md, "Handed over by issue #31", list each
record.

- Each record keeps the build's value. The build follows CDISC's ARS
  example (Common Safety Displays) or Pilot 7's specifications. The built
  ADaM equals the reference ADaM (real-1).
- The documents are the pilot's SAP (its text and its mock tables, section
  13.2) and the Define-XML of ADaM. By the owner's answer of 2026-11-22
  (ADR-022), a mock table states what it shows, the decimals of its masks
  included. The SAP itself calls its templates examples only (13.1.3).
- A record that takes the document's value changes the build of the pilot.
  Each cell that then differs from CDISC's example needs one entry in
  gold/exceptions.yaml, class `rule_choice`, with a proof, as for the
  efficacy tables.
- std-2 takes the file over (ADR-022). Until then a change is track real's
  work.

#### SME-01 `trt.start.source`: the treatment start date

- Question: Is the treatment start date the earliest start date of any
  exposure record (as built), or the date of Visit 3 from SV, as the
  Define-XML describes ADSL.TRTSDT?
- Where: line 3, status `conflict`.
- Options: A, the earliest exposure start (the build; SAP 11.2 counts
  emergence from the date of first dose). B, SV.SVSTDTC at VISITNUM 3
  (Define-XML, ADSL.TRTSDT). The house default of open-default@2 is a
  third reading: the earliest exposure record with a dose.
- Recommended: none for this record in the documents. General order: the
  SAP and the Define-XML contradict each other, so a person decides; the
  precedent of 2026-11-20 takes the reading that reproduces the reference
  ADaM, which is A. Source: SAP 11.2; the reference ADaM of the pilot.
- Current state: follows A in its value. The record is still `conflict`;
  marking it "per recommendation, pending SME review" is work for track
  real.
- Numbers: the documents do not say whether B gives other dates on the
  pilot. The record binds TRTSDT and SAFFL.

#### SME-02 `ae.start.imputation`: a partial AE start date

- Question: Is a partial adverse event start date with a known month
  completed with day 01 (the Define-XML, as built), or "in a conservative
  manner", as SAP 11.2 says?
- Where: line 13, status `conflict`.
- Options: A, day 01 of the month (the build; Define-XML, ADAE.ASTDT). B,
  a conservative imputation (SAP 11.2; the docs give no rule for it). The
  house default of open-default@2 is `first_of_month_not_before_first_dose`.
- Recommended: none for this record. General order: the two documents
  contradict each other; the precedent takes the reading that reproduces
  the reference ADaM: A. Source: Define-XML, ADAE.ASTDT.
- Current state: follows A in its value. The record is still `conflict`;
  marking it is work for track real.
- Numbers: the documents do not say whether B changes a date or a flag on
  the pilot.

#### SME-03 `ae.teae.start`: treatment emergence

- Question: Is an adverse event treatment-emergent only when it starts on
  or after the treatment start date (the Define-XML, as built), or also
  when it started before the first dose and worsened or recurred after it
  (SAP 11.2)?
- Where: line 14, status `conflict`.
- Options: A, a start on or after the treatment start date (the build;
  Define-XML, ADAE.TRTEMFL). B, A and the SAP's two criteria of worsening
  and recurrence.
- Recommended: none for this record. General order: the documents
  contradict each other; the precedent: A. Source: Define-XML,
  ADAE.TRTEMFL.
- Current state: follows A in its value. The record is still `conflict`;
  marking it is work for track real.
- Numbers: the documents do not say whether the pilot has an event that B
  adds. Such an event would change counts of the two AE tables.

#### SME-04 `custom:demog-baseline-visits`: baseline height and weight

- Question: Is baseline height the height at Visit 1 and baseline weight
  the weight at Visit 3 (SAP 9.2 and the Define-XML), or the first height
  by visit number and the weight flagged VSBLFL = Y (as built)?
- Where: line 46, status `conflict`.
- Options: A, the build's rule. B, Visit 1 for height and Visit 3 for
  weight (SAP 9.2; Define-XML, ADSL.HEIGHTBL and ADSL.WEIGHTBL).
- Recommended: none for this record. General order: the two documents
  agree and decide: B. Source: SAP 9.2; the Define-XML.
- Current state: differs from the general order. Applying it is work for
  track real (std-2 after): the record and the build's rule take the
  visits.
- Numbers: the documents do not say. Whether the two rules give the same
  values on the pilot is std-2's check by result. Baseline height is a row
  of Out14-1-1.

#### SME-05 `tfl.population` (demographics): the analysis set

- Question: Is the demographics table on the intent-to-treat set (SAP
  Template 3) or on the safety set (CDISC's example, as built)?
- Where: line 18, status `conflict`.
- Options: A, the safety set. B, the intent-to-treat set (Template 3; it
  is also the house default, `randomized`).
- Recommended: none for this record. General order: the document decides:
  B. Source: SAP 13.2, Template 3.
- Current state: differs from the general order. Applying it is work for
  track real: the record and the analyses of Out14-1-1 take the
  intent-to-treat set.
- Numbers: none on the pilot. The two sets hold the same 254 subjects
  (docs/state/real.md, "Other open points").

#### SME-06 `tfl.columns.total` (demographics): a total column

- Question: Does the demographics table have a total column (SAP 9.2,
  "across all treatment groups", and Template 3), or none (CDISC's
  example, as built)?
- Where: line 20, status `conflict`.
- Options: A, no total column. B, a total over all arms (also the house
  default, `all_arms`).
- Recommended: none for this record. General order: B. Source: SAP 9.2;
  Template 3.
- Current state: differs from the general order. Applying it is work for
  track real: Out14-1-1 gets the total's analyses and a column.
- Numbers: no existing cell changes; B adds cells, which CDISC's example
  has no value for. The documents give no count.

#### SME-07 `tfl.percent.format` (demographics): decimals of a percent

- Question: Are the percents of the demographics table whole numbers
  (Template 3, "xx (xx%)"), or shown with one decimal (as built)?
- Where: line 22, status `conflict`.
- Options: A, one decimal. B, no decimal.
- Recommended: none for this record. General order: B. Source: Template
  3.
- Current state: differs from the general order. Applying it is work for
  track real: the record and the patterns of the layout of Out14-1-1.
- Numbers: the text of every percent of Out14-1-1 changes (0 decimals in
  place of 1); the counts do not.

#### SME-08 `tfl.pvalue.format` (demographics): decimals of a p-value

- Question: Are the p-values of the demographics table shown with three
  decimals (Template 3, "0.xxx"; also the house default) or four (as
  built)?
- Where: line 25, status `conflict`.
- Options: A, four decimals, below 0.0001 as "<0.0001". B, three decimals.
- Recommended: none for this record. General order: B. Source: Template
  3.
- Current state: differs from the general order. Applying it is work for
  track real: the record and the patterns of Out14-1-1.
- Numbers: every p-value of Out14-1-1 changes its text (3 decimals in
  place of 4).

#### SME-09 `tfl.demog.rows`: the rows of the demographics table

- Question: Are the rows those of CDISC's example (age, age group, sex,
  ethnicity, race group, baseline height; as built), or those SAP 9.2
  lists, which also name the Mini-Mental State, the duration of disease,
  education, weight and BMI?
- Where: line 26, status `conflict`.
- Options: A, the example's six rows. B, the rows of SAP 9.2.
- Recommended: none for this record. General order: B. Source: SAP 9.2.
- Current state: differs from the general order. Applying it is work for
  track real: rows of Out14-1-1 are added or removed, and a new row may
  need an ADaM variable the build does not write today.
- Numbers: rows and their cells change. The documents give no count.

#### SME-10 `tfl.demog.stats`: quartiles in the demographics table

- Question: Do the continuous rows show the first and third quartile
  (CDISC's example, as built), or n, mean, standard deviation, median,
  minimum and maximum only (SAP 7; also the house default)?
- Where: line 27, status `conflict`.
- Options: A, with quartiles. B, without.
- Recommended: none for this record. General order: B. Source: SAP 7.
- Current state: differs from the general order. Applying it is work for
  track real: the quartile lines of age and height leave Out14-1-1.
- Numbers: cells leave the table; the others do not change.

#### SME-11 `custom:demog-age-display`: age groups

- Question: Does the demographics table show two age groups (below 65,
  65 and above; CDISC's example, as built) or three (below 65, 65 to 80,
  above 80; SAP 9.2)?
- Where: line 45, status `conflict`.
- Options: A, two groups, pooled from ADSL.AGEGR1. B, the three groups
  ADSL.AGEGR1 already holds (record `demo.age.groups`, line 11).
- Recommended: none for this record. General order: B. Source: SAP 9.2.
- Current state: differs from the general order. Applying it is work for
  track real: the age group rows of Out14-1-1 and their analyses.
- Numbers: the rows of the age groups and their chi-square p-value change.
  The documents give no values.

#### SME-12 `custom:demog-decimals`: decimals of the minimum and maximum

- Question: Are the minimum and maximum of the demographics table shown
  with one decimal (Template 3, "xx.x"), or with the decimals of the data
  (CDISC's example, as built)? Mean, SD and median agree with Template 3.
- Where: line 47, status `conflict`.
- Options: A, the decimals of the data. B, one decimal.
- Recommended: none for this record. General order: B. Source: Template
  3.
- Current state: differs from the general order. Applying it is work for
  track real: the patterns of Out14-1-1.
- Numbers: the text of the minimum and maximum of age and height changes.

#### SME-13 `tfl.output.include` (AE summary): is the table planned?

- Question: Is the adverse event summary a planned output of the study?
  The SAP's list of tables (13.1.1) has none; CDISC's example has one (as
  built).
- Where: line 29, status `conflict`.
- Options: A, included. B, not included.
- Recommended: none for this record. General order: B. B takes
  Out14-3-1-1 out of the study's gold, and the documents do not weigh this
  against the kit's use of the example's output (real-3a, ADR-005).
  ADR-016 notes the same tension: the reader of the pilot read the SAP as
  planning no AE summary. Source: SAP 13.1.1.
- Current state: A. Under the general order it differs. Applying it is
  work for track real: Out14-3-1-1 is no longer gold, and the gates that
  count it (`gates.PILOT_GRIDS`: real-3a, real-5a, issue-31) change.
- Numbers: no number changes its value; the 27 printed numbers of
  Out14-3-1-1 leave gold under B.

#### SME-14 `tfl.ae.summary.rows`: the row of discontinuations

- Question: Does the AE summary show the row of events leading to
  discontinuation? SAP 11.4 says these events are not formally summarized;
  CDISC's example has the row (as built).
- Where: line 35, status `conflict`.
- Options: A, eight rows with DISCONTINUATION. B, the seven rows without
  it.
- Recommended: none for this record. General order: B. Source: SAP 11.4.
- Current state: differs from the general order. Applying it is work for
  track real: the row leaves the layout of Out14-3-1-1. Moot if SME-13
  takes B.
- Numbers: the row's 3 cells leave the table; the other cells do not
  change.

#### SME-15 `tfl.percent.format` (organ class and term): decimals of a percent

- Question: Are the percents of the table by organ class and term whole
  numbers (Template 13, "xx (xx%)"), or shown with one decimal (as built)?
- Where: line 40, status `conflict`.
- Options: A, one decimal. B, no decimal.
- Recommended: none for this record. General order: B. Source: Template
  13.
- Current state: differs from the general order. Applying it is work for
  track real: the patterns of Out14-3-2-1.
- Numbers: the text of every percent of Out14-3-2-1 changes (0 decimals
  in place of 1); the counts do not.

#### SME-16 `tfl.ae.socpt.counts`: subjects, or subjects and events

- Question: Does the table by organ class and term show n (%) of subjects
  and the total number of events per arm (Template 13), or subjects only
  (CDISC's example, as built)?
- Where: line 44, status `conflict`.
- Options: A, subjects. B, subjects and events (the catalog's
  `subjects_and_events`).
- Recommended: none for this record. General order: B. Source: Template
  13 and its note on total events.
- Current state: differs from the general order. Applying it is work for
  track real: Out14-3-2-1 gets the event counts, their analyses and a
  column per arm.
- Numbers: the counts of subjects do not change; B adds cells. The
  documents give no count.

#### SME-17 `custom:socpt-pvalue-format`: decimals of a p-value

- Question: Are the p-values of the table by organ class and term shown
  with three decimals (Template 13, "0.xxx") or four (as built)?
- Where: line 49, status `conflict`.
- Options: A, four decimals. B, three decimals.
- Recommended: none for this record. General order: B. Source: Template
  13.
- Current state: differs from the general order. Applying it is work for
  track real: the patterns of Out14-3-2-1.
- Numbers: every Fisher p-value of Out14-3-2-1 changes its text (3
  decimals in place of 4).

#### SME-18 `trt.date.imputation`: a partial exposure date

- Question: How is a partial exposure date completed? No document of the
  kit says. CDISC's example completes it with the first day of the month
  (as built).
- Where: line 5, status `asked`, class `gold_quirk`.
- Options: A, the first day of the month (the build). B, not completed,
  and left out of the treatment dates (the house default of
  open-default@2).
- Recommended: none for this record. General order: the documents are
  silent, so the reference decides: A. PLAN.md 4.8 classes such a value
  `gold_quirk`; the precedent of 2026-11-20 recorded an answer of this kind
  as `stated`, `study_input`. Source: what CDISC's example does
  (docs/reports/issue-31.md); no document of the kit.
- Current state: follows A in its value. The record is still `asked`;
  marking it is work for track real.
- Numbers: the documents do not say whether the pilot has a partial
  exposure date. The record binds TRTSDT and TRTEDT.

#### SME-19 `ae.related.values`: which causalities are related

- Question: Which causality values make an adverse event related to study
  treatment? No document of the kit says, and the house has no default.
  CDISC's example reads POSSIBLE and PROBABLE (as built).
- Where: line 16, status `asked`, class `gold_quirk`.
- Options: A, POSSIBLE and PROBABLE (the data subsets of CDISC's example).
  B, another list a person states (the documents name none).
- Recommended: none for this record. General order: the documents, the
  reference ADaM (it has AEREL and no pooled group) and the house are
  silent, so a person supplies it; the precedent takes the value that
  reproduces the reference: A. Source: CDISC's ARS example, its data
  subsets (docs/reports/read-1a.md, the pilot).
- Current state: follows A in its value. The record is still `asked`;
  marking it is work for track real.
- Numbers: A gives the example's related rows. Another list changes the
  counts of the related rows of Out14-3-1-1 (RELATED, SERIOUS_RELATED,
  FATAL_RELATED); the documents give no values for one.

### The efficacy tables (real-5a, real-5b)

The records are in kits/cdiscpilot01/gold/decisions/efficacy.jsonl.

#### SME-20 `custom:eff-baseline-rows`: the Baseline rows

- Question: Do the Baseline rows of the ANCOVA tables summarize BASE on
  the records of the week of the table (as built), or the records of the
  baseline visit?
- Where: efficacy.jsonl line 7, status `asked`, class `study_input`;
  ADR-015, "For the owner (N2, not blocking real-5a)", item 3;
  docs/state/real.md, "Open".
- Options: A, BASE on the week's records. B, the baseline visit.
- Recommended: A, recorded as the owner's input (review of real-5a, "The
  owner's choices", item 5). No source in the docs.
- Current state: follows A in its value. The record is still `asked`;
  marking it is work for track real.
- Numbers: none on the pilot. Both readings give the same cells: every
  subject of the efficacy population has a baseline record and a record in
  every week (docs/reports/real-5a.md).

#### SME-21 The Toeplitz fallback of SAP 10.1.1

- Question: SAP 10.1.1 falls back on a Toeplitz covariance when the
  unstructured one meets a computational singularity. The machine does not
  implement the fallback; a fit that fails gives missing results. Is that
  acceptable for now?
- Where: efficacy.jsonl line 11 (`custom:eff-mmrm-covariance`); ADR-015,
  amendment of real-5b, "For the owner", item 3; docs/state/real.md,
  "Open".
- Options: A, not implemented until a study needs it. B, implement it now.
- Recommended: A, "accept for real-5b; implement it before a study that
  needs it" (review of real-5b, "The owner's choices", item 6). Source:
  SAP 10.1.1 states the fallback; on the pilot the unstructured fit reaches
  its maximum (docs/reports/real-5b.md).
- Current state: follows the recommendation.
- Numbers: none on the pilot; the fallback is not met.

#### SME-22 The class of the three former conflicts

- Question: `custom:eff-model-terms`, `custom:eff-pairwise` and
  `custom:eff-mmrm-records` were conflicts that the owner answered on
  2026-11-20. Is their class `document_rule` (each value is a reading a
  document states: SAP 10.1.1, template 5, template 10), or `study_input`
  (a person chose between contradicting documents)?
- Where: efficacy.jsonl lines 3, 5 and 9; docs/reports/
  real-5b-answers.review.md, "The owner's choices", item 1;
  docs/state/real.md, "Open".
- Options: A, `document_rule` (now). B, `study_input`.
- Recommended: A, and decide how to score a record whose documents
  contradict when real data are first scored (the same review). No source
  in the docs; PLAN.md 4.5 defines the classes.
- Current state: follows the recommendation.
- Numbers: none in an output. PLAN.md 4.5 scores the two classes
  differently once a reader is scored on these records.

### Results and display (real-2, real-3a)

#### SME-23 The 24 classes `reference_error` of CDISC's example

- Question: 24 results that CDISC's ARS example embeds differ from the
  pilot data: 22 counts, percents and means of ethnicity, three race groups
  and height, each the value of the other active arm; the median of height
  in the low dose arm; the first quartile of age in the high dose arm. Is
  each an error of the reference?
- Where: kits/cdiscpilot01/gold/exceptions.yaml, section `results`;
  ADR-002, decision 6; docs/reports/real-2.review.md, F9;
  docs/state/real.md, "For the owner, from real-2".
- Options: A, `reference_error` (now). B, another class of PLAN.md 4.8
  (`rule_choice`, `data_difference`).
- Recommended: A. The review of real-2 (F9) finds the 22 and the median
  well supported and the quartile defensible: of 69 embedded quartiles and
  medians where the definitions differ, the example has the averaged value
  in 68, not in this one. Source: the pilot ADSL in both engines and CSR
  Table 14-2.01 (evidence E3 and E24).
- Current state: follows the recommendation.
- Numbers: none; a class changes no number. 14 cells of Out14-1-1 show
  these results (docs/reports/issue-31.md).

#### SME-24 The empty Fisher p-value of CDISC's example

- Question: CDISC's example lists a Fisher p-value for WOUND HAEMORRHAGE,
  placebo against low dose, without a value. Our engines give no result:
  the term has no records in the two arms. Is that an error of the
  reference, or a difference of rule (which groups give results)?
- Where: exceptions.yaml, section `results` (proof `no_records`);
  docs/reports/real-2.review.md, F9; docs/state/real.md.
- Options: A, `reference_error` (now). B, a difference of rule.
  PLAN.md 4.8 offers `rule_choice` for that, which needs another
  alternative of a decision and a build with it; none exists for which
  groups give results.
- Recommended: none in the docs. The review of real-2 finds this class
  the weakest, and the case closer to a difference of rule than to a
  contradiction. No source in the docs.
- Current state: A; no recommendation to follow.
- Numbers: none; neither side has a value.

#### SME-25 Three statements of `display.pattern` read off CDISC's example

- Question: `display.pattern` pads a number with blanks to the length of
  its mask when the mask has a decimal point, does not pad a mask without
  one, and puts the minus sign before the padding (statements 3 to 5). No
  public standard states these; they are read off the formatted values of
  CDISC's example. Should they stay the rule?
- Where: standard/methods/ (`display.pattern`); ADR-003, decision 3;
  docs/state/real.md, "For the owner, from real-3a".
- Options: A, keep them. B, another rule (the docs name none).
- Recommended: A: the example's rule, taken as version 0 of ours (ADR-003,
  decision 3). Source: the 3,734 formatted values of CDISC's ARS example
  (ADR-003, "What the example's formatted values show about a pattern").
- Current state: follows the recommendation.
- Numbers: no value changes; only the blanks and the place of the sign in
  a cell's text. On the example the rule gives the example's text.

#### SME-26 A value that is a half only up to floating error

- Question: Four medians of the change of temperature are a half only up
  to floating error. Each is one record's change of 0.05, such as AVAL
  36.94 - BASE 36.89, which binary floating point holds as
  0.04999999999999716 (three of the cells have an odd n, the fourth two
  equal middle records). The reference ADVS holds the same value in the
  same 56 records as ours. The display rule shows " 0.0"; CDISC's example
  shows " 0.1". Should a value this close to a half round as a half, and
  what class has the difference?
- Where: real-3, record real-3/vs-medians-at-half: 4 entries of `formats`
  in kits/cdiscpilot01/gold/exceptions.yaml; ADR-003, amendment of real-3,
  point 13; docs/reports/real-3.md.
- Options: A, round the value as computed (" 0.0"; the registry today) and
  record the 4 cells as exceptions. B, treat it as a half (" 0.1", as the
  example); that changes `display.pattern` and needs a new dry run of
  read-2a (a model call).
- Recommended: A, with the class `rule_choice` and the new proof
  `half_in_floating_error`; the owner picked the recommended A on
  2026-11-23, and the class is per recommendation, pending SME review.
  Source: PLAN.md 4.8 (`rule_choice`: the reference follows another
  alternative of a decision); the data are the same, and the example's
  rounding absorbs the floating error, most likely SAS's ROUND fuzz (not
  verified).
- Current state: follows the recommendation (real-3, not in main yet).
- Numbers: 4 medians of the vital signs tables, one digit each.

#### SME-33 The decimals of the minima and maxima of temperature

- Question: CDISC's example shows 119 minima and maxima of temperature (59
  minima, 60 maxima, in An08_01 and An08_02) with the decimals of the data
  ("35.33"), though its own shells give "Min, Max" the pattern "XX, XX".
  The grid follows the pattern. Is the example's text an error of the
  reference?
- Where: real-3, record real-3/vs-minmax-decimals: 119 entries of
  `formats` in kits/cdiscpilot01/gold/exceptions.yaml, proof
  `not_its_own_pattern`; docs/reports/real-3.md.
- Options: A, the shell's pattern, and the 119 are `reference_error`
  (taken). B, a pattern with the decimals of the data (`XX.XX` for the
  values, `X.XX` for the changes): it prints "35.33" in 63 cells of each
  grid and still leaves 10 of the 126 different, where the example drops
  trailing zeros.
- Recommended: A, per recommendation, pending SME review (real-3). Source:
  the example's own shells ("XX, XX"), as issue #31 did for the one Fisher
  p-value of 1. The SAP's Templates 21 and 22, "for example only", show the
  minimum and maximum of blood pressure and heart rate without decimals and
  do not list temperature. The demographics go the other way, because
  their SAP template shows decimals (SME-12).
- Current state: follows the recommendation (real-3, not in main yet).
- Numbers: none change in a value; 63 cells of each of the two vital signs
  grids print without the data's decimals.

## Track read

#### SME-27 The crosswalk of the pilot's AE summary rows

- Question: Which analysis of CDISC's AE summary is which row of the house
  table? The scorer maps all eight by their data subsets: An07_01 ANY,
  An07_02 RELATED, An07_03 SERIOUS, An07_04 SERIOUS_RELATED, An07_05
  FATAL, An07_06 FATAL_RELATED, An07_07 DOSE_MODIFIED, An07_08
  DISCONTINUATION.
- Where: src/specfirst/score/pilot.py (`ROWS`); ADR-008, decision 10 and
  "For the owner", item 3; docs/state/read.md, "Open";
  docs/reports/catalog-2c.md (the eight mapped since catalog@2).
- Options: A, the mapping as written. B, another mapping.
- Recommended: A, as decided (ADR-008, decision 10: "a reading of two
  public definitions"). Source: the data subsets of the analyses of
  CDISC's ARS example and the rows of `tfl.ae.summary.rows` in catalog@2
  (#13).
- Current state: follows the recommendation.
- Numbers: none in a gate; the pilot is a report. Another mapping changes
  how the pilot report classes its cells.

## Track gen

#### SME-28 The probe `dosed_but_not_randomized` and SDTMIG v3.4

- Question: The probe plants a DM record with no planned arm, the reason
  NOT ASSIGNED, an actual arm and a reference period. Four CDISC CORE rules
  for SDTMIG v3.4 do not allow such a record. Should the probe be written
  as a conformant record?
- Where: docs/reports/gen-1a.md, "For the owner", item 5;
  docs/reports/gen-1a.review.md, F26; docs/state/gen.md, "For the std
  track"; core_findings.yaml of the generator.
- Options: A, keep it; the four findings are accepted as planted (now). B,
  write a record that v3.4 allows, and change the catalog's recipe
  ("ARMCD is NOTASSGN", older than v3.4) in a new catalog version. One of
  the rules names ARMNRS "UNPLANNED TREATMENT" as the case in which RFSTDTC
  may be filled.
- Recommended: none in the docs. Source of the question: CORE-000192,
  CORE-000758, CORE-000927 and CORE-002099 (SDTMIG v3.4).
- Current state: A; no recommendation to follow.
- Numbers: none in an output of the pilot. B changes the SDTM of generated
  kits; whether the probe then still separates the two rules of the safety
  set, the docs do not say.

#### SME-29 A time of the hour alone: collected or not

- Question: For `ae.teae.start/by_time_when_collected`, the template counts
  an event time of the hour alone as collected, but a dose time of the hour
  alone as not. The generator's reference reads both as collected. Which
  reading holds, for the event and the dose alike?
- Where: docs/reports/catalog-2c.review.md, G5; docs/state/gen.md, "From
  catalog-2c" (left open by the review); src/specfirst/gen/reference.py
  and the template of catalog@2.
- Options: A, an hour-only time counts as collected, on both sides. B, it
  does not count, on both sides.
- Recommended: none in the docs. No source in the docs.
- Current state: no recommendation to follow. The two readings differ for
  the dose. Changing the template is a new catalog version (catalog@2 is
  frozen); changing the reference is gen's.
- Numbers: none today: no generated dose or event has an hour-only time.

#### SME-32 A subject in the study without a study-level disposition record

- Question: To separate the study-participation record as the end-of-study
  record, the generator plants a subject without an exposure end date who
  stopped treatment and is still in the study. Its only disposition event
  is the treatment record, and it has no study-level disposition record.
  Is that a valid SDTM shape?
- Where: gen-2b, ADR-023 decision 6(c); the CDISC CORE result on it in the
  gen-1a log of docs/reports/gen-2b.md.
- Options: A, plant such a subject (taken). B, give it a study-level
  disposition record, and separate the decision some other way.
- Recommended: A, per recommendation, pending SME review (2026-11-23).
  Source: SDTMIG v3.4, DS records only disposition events that have
  occurred.
- Current state: follows the recommendation.
- Numbers: in generated kits only. It is what makes the value "STUDY
  PARTICIPATION" of the end-of-study record separable.

#### SME-34 A planned arm without a randomization record

- Question: In a randomized design, can a dosed subject have a planned arm
  but no randomization record? If so, data can separate the decision
  `pop.safety.rule`, and its row of `REACHES` (kind (a), never separable)
  is wrong.
- Where: gen-2b, review finding H2 (docs/reports/gen-2b.review.md); ADR-023,
  decision 4; docs/reports/gen-2b.md; the test
  `test_a_subject_without_a_randomization_has_no_planned_arm`.
- Options: A, no: the row stays, with its premise written ("equal on any
  data in which a subject without a randomization has no planned arm"), and
  a test checks that generated data keep it (taken). B, yes: plant such a
  subject and claim the rule wherever a table reads the safety set; this
  goes beyond the recipe of the frozen catalog@2.
- Recommended: A, per recommendation, pending SME review (2026-11-23).
  Source: SDTMIG v3.4 DM, a subject not assigned has ARMCD and ARM null
  and ARMNRS "NOT ASSIGNED"; in a randomized design assignment is
  randomization. The catalog's recipe for `dosed_but_not_randomized` also
  reads "DM.ARMCD is NOTASSGN" (see SME-28).
- Current state: follows the recommendation (gen-2b, not in main yet).
- Numbers: in generated kits only; `pop.safety.rule` stays unseparated in
  gold.

## Track std

#### SME-30 `ae.related.values`: a list or a set

- Question: The catalog types the slot of `ae.related.values` as a list,
  and its statement reads "its causality is one of" the values. The
  reading score compares the list in its order, so the same values in
  another order count as a decision to change. Is the list a set?
- Where: ADR-008, "For the owner" (noted for the std track; review of
  read-1a, R4); docs/state/read.md, "Open".
- Options: A, an ordered list (now). B, a set.
- Recommended: none in the docs. No source in the docs.
- Current state: A; no recommendation to follow.
- Numbers: none in a build; only the reading score of a reader changes.

#### SME-31 Two dosed records on the first dose day

- Question: When two dosed exposure records start on the first dose day,
  one with a time and one without, the one without gives the treatment
  start (00:00, with the time flag set). So the collected time of the
  first dose is not used. Is that the right treatment start?
- Where: docs/state/std.md, "Open" (left open after the second pass of the
  review of std-1); docs/reports/std-1.review.md, finding 17.
- Options: A, as built: the record without a time, 00:00 imputed and
  flagged. B, the collected time of the timed record.
- Recommended: none in the docs. No source in the docs.
- Current state: A; no recommendation to follow. The docs do not say
  whether open-default@2 changed this.
- Numbers: none on the pilot, whose build follows Pilot 7's
  specifications. For generated kits the docs do not say.

## Answered by the owner before the rule (not counted above)

These domain points were answered by the owner, each time with the
recommended option, before 2026-11-23. Under the rule they stand as "per
recommendation"; the SME may want to confirm them.

- ADR-004, "Node N1: the owner's answer" (2026-11-17): the 14 questions of
  the reading guide (docs/reports/std-1.md), all "as delivered". The owner
  called the answer provisional.
- ADR-020, "The owner's answer (2026-11-21)": the eight new house defaults
  of open-default@2 (question 2) and two changed answers of N1 (question
  3); "The owner's answer on the three departures" (#17 and #21).
- ADR-015, "The owner's answers (2026-11-20)": the 45 `rule_choice`
  differences and the row labels of the efficacy tables (answer 1); the
  records `custom:eff-model-terms`, `custom:eff-pairwise`,
  `custom:eff-mmrm-records`, `custom:eff-mmrm-df` (Kenward-Roger) and
  `custom:eff-cmh` (row mean scores) (answer 2).
- ADR-022, "The owner's answer (2026-11-22)": a mock table of the SAP
  states what it shows, the decimals of its masks included (option A of
  three). With option B (its layout only), SME-07, SME-08, SME-12, SME-15
  and SME-17 would not be conflicts.

## Not for the SME (stays with the owner)

- Spending money: a second pilot task that gives the AE summary as planned
  (ADR-016, "For the owner"; one run of arm R, about USD 0.6); a probe step
  on a file beside the task (review of read-2a, H6; model use).
- Publishing: the draft issue for CDISC's ARS repository
  (docs/upstream/ars-issue-common-safety-displays.md); the whole grid of
  Out14-3-1-1 quoted in the report of real-3a; the typed-in CSR values of
  evidence/csr_hylaw_spike.py (docs/state/base.md, "Open").
- Scope and order of work: what comes next on the track real (real-5, the
  rest of real-3, real-4); the proposals for catalog@2 in
  docs/reports/real-5a.md and real-5b.md (ADR-015, item 5); ADR-005, items
  2 to 4; ADR-007, item 2 (who aligns the house layout templates); ADR-009,
  items 2 and 3; ADR-019, item 3 (std-2's matrix of the pilot); the rework
  of the probes before the gate of the full gen-2, the seed file of dev
  and test kits, and a TI dataset (docs/state/gen.md; gen-1a and gen-2a
  reports); a P4 run on the kit's own values (issue #31); the approval of
  judged citation edges, which waits for the edit loop of PLAN.md 7.6.
- Changes to PLAN.md or standard/schemas/, and readings of PLAN.md: the
  class in the decision record (ADR-019, item 1); "separated" read at the
  printed outputs or at the ARD (ADR-019, item 2; PLAN.md 4.6); the plan's
  numbers of real-2 (3,711 and 3,710, 24 and 25, 49 and 97; review of
  real-2, F1); the R engine not on cards and cardx (ADR-002; PLAN.md 7.1,
  13.3); the additions to the kit layout of PLAN.md section 8 (ADR-002,
  decision 5; ADR-003, decision 7); a grid field for a count under a column
  header (ADR-003, decision 4); schemas for the registry, the layout, the
  kit manifest and the role of a `reads` edge (docs/state/real.md, "Other
  open points"); the sweep of matrices as a check the gate text does not
  ask for (ADR-008, item 2); the change of the gate real-5a (ADR-015,
  amendment of real-5b, item 4); ADR-000, a proposal until the owner has
  read it.
- Technical choices without a domain question: listed groups or a change of
  rule I9 of the engines (ADR-007, item 1; ADR-011); `protocol_order` has
  no slot for the order of the arms (ADR-007, item 3; BACKLOG
  `i17.dose-order`); `display.round.half_even` in the registry (ADR-007,
  item 4); our own layout format, not tfrmt (ADR-003, decision 1); no
  Parquet or YAML reader in the R library (ADR-002); no container
  definition and no Linux user (docs/state/base.md).
