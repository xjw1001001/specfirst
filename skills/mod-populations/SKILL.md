---
name: mod-populations
description: Reading notes v0 for the unit mod-populations (Analysis populations and disposition). For each of its 5 catalog questions, where a protocol or a statistical analysis plan states the decision, the words to look for and the traps. Rendered from the decision catalog specfirst-m1 1.
---

# Analysis populations and disposition (mod-populations): reading notes v0

Rendered from the decision catalog `specfirst-m1` version 1 by `specfirst run skills --write`; do not edit by hand. Read `core-reader` first: it says how to record a decision. Here, for every question of the unit: its alternatives with the statement each gives, the house default, and where documents state it.

Questions of this unit: `pop.randomized.rule`, `pop.safety.rule`, `pop.safety.grouping`, `pop.efficacy.rule`, `disp.status.record`.

## `pop.randomized.rule`: Who is in the randomized set?

Alternatives:

- `all_randomized` (the house default): "The randomized set holds every randomized subject."
- `randomized_with_postbaseline`, slots test: "The randomized set holds every randomized subject with at least one post-baseline value of the vital sign {test}."
  Meaning: A post-baseline value is a non-missing result dated after the treatment start date.

House default: `all_randomized`.

The answer fixes the subjects and the column counts of every output on the randomized set,
which documents usually call the intent-to-treat set or the full analysis set.

### Where it is stated

- SAP: section on analysis populations or analysis sets.
- Protocol: statistical section, "analysis populations".
- Almost always stated, under names such as ITT, FAS, randomized set or all randomized.

### Words to look for

- `all_randomized`: "all randomized subjects", "all subjects assigned to a treatment arm",
  "regardless of whether study treatment was received".
- `randomized_with_postbaseline`: "randomized subjects with at least one post-baseline
  assessment of ...", often called modified intent-to-treat. The slot `test` is the test code
  of the vital sign named in that sentence (systolic blood pressure gives SYSBP).

### Traps

- "Randomized and received at least one dose" is a dosing condition, not a post-baseline
  value. It matches no alternative here; report the passage (compare `pop.safety.rule`).
- Post-baseline means dated after the treatment start date. A value on the day of the first
  dose does not count, and "after randomization" is not the same condition.
- The second alternative needs a vital sign. If the required assessment is a questionnaire,
  a laboratory test or "any efficacy assessment", report the passage.
- When the SAP defines both an all-randomized set and a narrower evaluable set, this entry is
  the all-randomized one; the narrower set belongs to `pop.efficacy.rule`.
- Silent documents: use the house default `all_randomized` and cite the house standard.

## `pop.safety.rule`: Who is in the safety set?

Alternatives:

- `at_least_one_dose` (the house default): "The safety set holds every subject who received at least one dose of study treatment."
- `randomized_and_dosed`: "The safety set holds every randomized subject who received at least one dose of study treatment."

House default: `at_least_one_dose`.

The answer fixes the subjects and the column counts of every safety output. The alternatives
differ only for a subject who was dosed without being randomized.

### Where it is stated

- SAP: section on analysis populations or analysis sets.
- Protocol: statistical section, definition of the safety population.
- Almost always stated; the wording is usually close to ICH E9 section 6.3 (subjects who
  received at least one dose).

### Words to look for

- `at_least_one_dose`: "all subjects who received at least one dose of study treatment", "all
  treated subjects", "all subjects exposed to study drug".
- `randomized_and_dosed`: "all randomized subjects who received at least one dose",
  "randomized and treated subjects".

### Traps

- The word "randomized" in the sentence is the whole difference. It means assigned to an arm:
  a planned arm code that is neither screen failure nor not assigned. Pick by the text, even
  though both alternatives give the same set when nobody was dosed without randomization.
- "Received a dose" means that the subject has a treatment start date (`trt.start.source`,
  `trt.date.imputation`). Dispensing of study drug alone is not a dose.
- Added conditions such as "and at least one post-dose safety assessment" match no
  alternative; report the passage.
- Whether the set is grouped as treated or as randomized is `pop.safety.grouping`.
- Silent documents: use the house default `at_least_one_dose` and cite the house standard.

## `pop.safety.grouping`: Which treatment groups the safety analyses?

Alternatives:

- `actual` (the house default): "Safety analyses group subjects by actual treatment."
- `planned`: "Safety analyses group subjects by planned treatment."

House default: `actual`.

The answer decides under which column a subject counts in every output on the safety set,
when the treatment received differs from the treatment assigned.

### Where it is stated

- SAP: section on analysis sets, usually the sentence after the definition of the safety set.
- SAP: general conventions on treatment groups; titles or footnotes of the safety shells.
- Protocol: statistical section, safety analyses. Often stated, sometimes only implied.

### Words to look for

- `actual`: "as treated", "according to the treatment actually received", "by actual
  treatment", "by treatment received".
- `planned`: "as randomized", "according to the randomized treatment", "by planned
  treatment", "by assigned treatment", when said of the safety analyses.

### Traps

- "As randomized" said of the efficacy or intent-to-treat analyses says nothing about safety.
  Outputs on another analysis set group by planned treatment whatever is chosen here.
- This entry says which treatment is used, not how the actual treatment is found; that is
  `trt.actual.source`.
- A sentence that all analyses use the randomized treatment does cover safety: choose
  `planned`.
- If protocol and SAP disagree, cite both passages; the SAP, as the later and more detailed
  document, normally governs the analysis.
- Silent documents: use the house default `actual` and cite the house standard.

## `pop.efficacy.rule`: Who is efficacy-evaluable?

Alternatives:

- `baseline_and_postbaseline`, slots test: "The efficacy-evaluable set holds every subject of the safety set with a baseline value and at least one post-baseline value of the vital sign {test}."
  Meaning: A baseline value is a non-missing result dated on or before the treatment start date; a post-baseline value is one dated after it.
- `attended_visit`, slots visit: "The efficacy-evaluable set holds every subject of the safety set who attended the visit {visit}."
  Meaning: A subject attended a visit when the subject visits domain (SV) has a record of it.

House default: none. A document states it, or it is asked.

The answer fixes who is in the efficacy-evaluable set, a subset of the safety set, and so
the subjects and column counts of every output on that set.

### Where it is stated

- SAP: section on analysis populations, under names such as efficacy-evaluable, evaluable,
  completers or modified intent-to-treat.
- Protocol: statistical section, "analysis populations".
- The set has no standard definition, so it must be read from the documents.

### Words to look for

- `baseline_and_postbaseline`: "subjects with a baseline and at least one post-baseline
  measurement of ...". The slot `test` is the test code of the vital sign named there
  (systolic blood pressure gives SYSBP, weight gives WEIGHT).
- `attended_visit`: "subjects who attended the Week 8 visit", "subjects who completed the
  Week 24 visit", "completers through Week 24". The slot `visit` is the visit name as the
  schedule of assessments writes it.

### Traps

- Baseline is a value on or before the treatment start date; post-baseline is a value dated
  after it. A value on the day of the first dose is baseline, not post-baseline.
- "Completed the study" or "completed treatment" is a disposition status, not attendance of
  a named visit. Attended means that the subject visits data hold a record of that visit.
- Both alternatives start from the safety set. Sets built on protocol deviations, compliance
  limits or an assessment that is not a vital sign match no alternative; report the passage.
- The visit name is compared exactly with the collected visit name; copy it as written.
- Silent documents: this entry has no house default. Do not guess; a person must be asked.

## `disp.status.record`: Which record gives the end-of-study status?

Alternatives:

- `disposition_event` (the house default): "The end-of-study record is the disposition event record of the subject."
  Meaning: The DS record with DSCAT equal to DISPOSITION EVENT. Of several such records the last by DSSEQ is taken.
- `disposition_event_by_subcategory`, slots subcategory: "The end-of-study record is the disposition event record of the subject with the subcategory {subcategory}."
  Meaning: The DS record with DSCAT equal to DISPOSITION EVENT and DSSCAT equal to the named subcategory. Of several such records the last by DSSEQ is taken.

House default: `disposition_event`.

The chosen record gives the end-of-study date and the status completed, discontinued or
ongoing. Rules that fall back on the end-of-study date use the same record.

### Where it is stated

- SAP: section on subject disposition, and definitions of study completion.
- Protocol: sections on completion, discontinuation of treatment and withdrawal from study.
- The choice of record is rarely spelled out; look for whether the study collects separate
  end-of-treatment and end-of-study forms.

### Words to look for

- `disposition_event`: one completion or discontinuation form per subject, "study completion
  status as recorded on the end-of-study page", no split between treatment and study.
- `disposition_event_by_subcategory`: separate records for end of treatment and end of
  study, "disposition is summarized separately for treatment and for study". The slot
  `subcategory` is the subcategory text of the end-of-study record, for example END OF STUDY.

### Traps

- Discontinuation of treatment is not discontinuation from the study. With both collected,
  the plain rule takes the last disposition event by sequence number, which may be either.
- Protocol milestones such as informed consent or randomization are not disposition events
  and never compete.
- Status is COMPLETED only for the term COMPLETED; any other term gives DISCONTINUED, and a
  subject with no such record is ONGOING.
- The subcategory is compared exactly. Use the text the documents or annotated forms give;
  if none is given, report that instead of inventing one.
- Silent documents: use the house default `disposition_event` and cite the house standard.
