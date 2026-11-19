---
name: mod-treatment
description: Reading notes v0 for the unit mod-treatment (Treatment and exposure). For each of its 6 catalog questions, where a protocol or a statistical analysis plan states the decision, the words to look for and the traps. Rendered from the decision catalog specfirst-m1 1.
---

# Treatment and exposure (mod-treatment): reading notes v0

Rendered from the decision catalog `specfirst-m1` version 1 by `specfirst run skills --write`; do not edit by hand. Read `core-reader` first: it says how to record a decision. Here, for every question of the unit: its alternatives with the statement each gives, the house default, and where documents state it.

Questions of this unit: `trt.planned.source`, `trt.actual.source`, `trt.start.source`, `trt.end.source`, `trt.date.imputation`, `date.studyday.origin`.

## `trt.planned.source`: Where does planned treatment come from?

Alternatives:

- `dm_arm` (the house default): "Planned treatment is the planned arm of the subject (DM.ARM)."
- `dm_armcd_map`, slots map: "Planned treatment is decoded from the planned arm code (DM.ARMCD) as follows: {map}."
  Meaning: A code that the list does not name gives no planned treatment.

House default: `dm_arm`.

The answer fixes the planned treatment label of each subject. That label names the treatment
columns and groups every analysis done by planned treatment.

### Where it is stated

- Protocol: study design and treatment arms, randomization section (the list of arms).
- SAP: section on treatment groups or display conventions; column headers of the table shells.
- Often unstated: documents name the arms in prose and do not say how the label is obtained.

### Words to look for

- `dm_arm`: "planned treatment is the arm assigned at randomization", "as randomized", arm
  names used in tables exactly as the protocol lists the arms, with no relabelling rule.
- `dm_armcd_map`: an explicit list or table that pairs arm codes with display labels, such as
  "A = Drug X 10 mg, B = Placebo" or "treatment groups will be labelled as follows". The slot
  `map` is that list: one code and label pair per arm, copied as written.

### Traps

- Choose `dm_armcd_map` only when the text gives both codes and labels. Do not invent codes
  from arm names, and do not shorten or reword the labels.
- Under the map a code that is not listed gives no planned treatment. Copy every arm, placebo
  included; do not add entries for screen failures or subjects not assigned.
- Pooled groups such as "all active" or "total" are columns (`tfl.columns.total`), not map
  rows. Wording on the treatment actually received belongs to `trt.actual.source`.
- Silent documents: use the house default `dm_arm` and cite the house standard. Do not guess
  a map from the data.

## `trt.actual.source`: Where does actual treatment come from?

Alternatives:

- `dm_actarm` (the house default): "Actual treatment is the actual arm of the subject (DM.ACTARM)."
- `first_ex_treatment`: "Actual treatment is the treatment named on the first exposure record of the subject (EX.EXTRT)."
  Meaning: The first exposure record is the one with the earliest start date; the lowest EXSEQ breaks a tie.
- `same_as_planned`: "Actual treatment is the same as planned treatment."

House default: `dm_actarm`.

The answer fixes the treatment a subject counts under whenever an analysis groups by actual
treatment. It matters only for subjects dosed with something other than their planned arm.

### Where it is stated

- SAP: section on analysis sets ("analyzed according to the treatment actually received") and
  any paragraph on dosing errors or treatment misallocation.
- Protocol: statistical section, definition of the safety population.
- Often only "as treated" is written, with no rule for how the actual treatment is found.

### Words to look for

- `dm_actarm`: "actual treatment arm", "the treatment the subject actually received" as
  recorded for the subject as a whole, "actual arm" with no rule based on single doses.
- `first_ex_treatment`: "the first treatment received", "the treatment given at the first
  dose", "based on the first administration of study drug".
- `same_as_planned`: "actual treatment is set equal to planned treatment", "treatment received
  is taken to be the treatment assigned", "actual treatment is assumed to be as randomized".

### Traps

- "As treated" alone answers `pop.safety.grouping` (group by actual treatment), not this
  entry. With no derivation rule stated, this entry is silent.
- "As randomized" said of the efficacy analyses only does not mean `same_as_planned`; that
  alternative needs a statement that actual treatment itself equals planned treatment.
- "First" in `first_ex_treatment` is the exposure record with the earliest start date, and
  the lowest sequence number on a tie.
- Rules such as "the treatment received for most of the study" or "the highest dose received"
  match no alternative. Report the passage instead of picking the nearest one.
- Silent documents: use the house default `dm_actarm` and cite the house standard.

## `trt.start.source`: What is the treatment start date?

Alternatives:

- `first_ex_with_dose` (the house default): "The treatment start date is the earliest start date of an exposure record with a dose."
  Meaning: An exposure record has a dose when EXDOSE is above zero, or when EXDOSE is zero and EXTRT contains PLACEBO.
- `first_ex_record`: "The treatment start date is the earliest start date of any exposure record."
- `dm_rfxstdtc`: "The treatment start date is the date of first exposure in the demographics domain (DM.RFXSTDTC)."

House default: `first_ex_with_dose`.

The treatment start date anchors study days, baseline, post-baseline, treatment emergence and
who counts as dosed. Another source moves all of them for the subjects it affects.

### Where it is stated

- SAP: general definitions ("date of first dose", "treatment start date") and the section on
  exposure or extent of exposure.
- Protocol: study treatment administration; schedule of assessments footnotes on first dosing.
- Usually only "date of first dose of study treatment" is written, with no detail on records.

### Words to look for

- `first_ex_with_dose`: "date of the first dose of study treatment", "first dose actually
  taken", "first non-zero dose", "records with no drug given are ignored".
- `first_ex_record`: "earliest dosing record", "start date of the first exposure record",
  "first entry of the drug administration log, whatever the dose".
- `dm_rfxstdtc`: "date of first exposure as recorded in demographics", "reference first
  treatment date", or the variable RFXSTDTC named directly.

### Traps

- Plain "first dose" means `first_ex_with_dose`. Choose `first_ex_record` only when the text
  says that any record counts, including one with a dose of zero.
- Under `first_ex_with_dose` a placebo record with a dose of zero still has a dose. Do not
  read "dose above zero" as leaving out placebo subjects.
- RFXSTDTC (first exposure) is not RFSTDTC (reference start). "Day 1" and the randomization
  date are matters for `date.studyday.origin`, not for this entry.
- This entry gives a date. Comparisons with the time of the first dose are decided in
  `ae.teae.start` and `bds.baseline.rule`.
- Silent documents: use the house default `first_ex_with_dose` and cite the house standard.

## `trt.end.source`: What is the treatment end date?

Alternatives:

- `last_ex_end_date` (the house default): "The treatment end date is the latest end date of an exposure record with a dose."
- `last_ex_start_date`: "The treatment end date is the latest start date of an exposure record with a dose."
- `ds_date_when_ex_missing`: "The treatment end date is the latest end date of an exposure record with a dose, or the end-of-study disposition date when no such record has an end date."
  Meaning: The disposition date is the start date of the end-of-study record (decision disp.status.record). It is taken only for a subject with a treatment start.

House default: `last_ex_end_date`.

The treatment end date bounds the duration of exposure, the end-of-treatment record and any
treatment emergence window that is counted from the last dose.

### Where it is stated

- SAP: general definitions ("date of last dose") and the section on extent of exposure, where
  duration is often given as last dose date minus first dose date plus one.
- SAP: section on missing dates, for a fallback when the last dose date is unknown.
- Protocol: definitions of end of treatment; rarely more precise than "last dose".

### Words to look for

- `last_ex_end_date`: "date of last dose", "date of last administration", "end date of the
  last dosing record", "treatment stop date".
- `last_ex_start_date`: "start date of the last dosing record", "date the last cycle or
  infusion was started", "start of the last dosing interval".
- `ds_date_when_ex_missing`: a fallback sentence such as "if the date of last dose is missing,
  the date of study completion or discontinuation is used".

### Traps

- With one record per dose, start and end date agree; the first two alternatives differ only
  when a record spans several days. Plain "date of last dose" means `last_ex_end_date`.
- Only exposure records with a dose count (a dose above zero, or a placebo record). The
  fallback of `ds_date_when_ex_missing` applies only when no such record of the subject has
  an end date, and it takes the date of the end-of-study record (`disp.status.record`).
- A fallback to the last visit, the last contact or a data cut-off date matches no
  alternative. Report the passage instead of picking the nearest one.
- The date of an "end of treatment visit" is a visit date, not the treatment end date.
- Silent documents: use the house default `last_ex_end_date` and cite the house standard.

## `trt.date.imputation`: How are partial exposure dates completed?

Alternatives:

- `not_completed` (the house default): "A partial exposure date is not completed and is left out of the treatment dates."
  Meaning: The treatment start and end dates are taken from the exposure dates that have a year, a month and a day. A date with a missing part in the middle (a year and a day without the month) is partial.
- `first_day_of_month`: "A partial exposure date with a known month is completed with the first day of that month."
  Meaning: A date with an unknown month is left out of the treatment dates.

House default: `not_completed`.

The answer decides whether a dosing date collected without a day can still give a treatment
start or end date, and so whether such a subject has study days and counts as dosed.

### Where it is stated

- SAP: section on missing or partial dates, or on data handling conventions.
- Many SAPs cover only adverse event and concomitant medication dates and say nothing about
  dosing dates.
- Protocol: almost never.

### Words to look for

- `not_completed`: "dosing dates will not be imputed", "incomplete dates of study drug
  administration are left missing", "no imputation of exposure dates".
- `first_day_of_month`: "a missing day is set to the first day of the month", "day imputed as
  01 when month and year are known", said of dosing or exposure dates.

### Traps

- A rule written for adverse event or medication dates does not carry over to exposure dates.
  Adverse event start dates are `ae.start.imputation`.
- Under `first_day_of_month` a date with an unknown month is still not completed. Rules that
  set a missing month to January or to mid-year match no alternative.
- The entry has one rule for start and end dates alike. A SAP that completes end dates with
  the last day of the month, or any date with the 15th, is not covered: report the passage.
- A general sentence such as "partial dates are imputed conservatively" names no rule; treat
  it as silent.
- Silent documents: use the house default `not_completed` and cite the house standard. Do not
  infer a rule from the data.

## `date.studyday.origin`: Which date is study day 1?

Alternatives:

- `treatment_start` (the house default): "Study day 1 is the treatment start date."
- `dm_rfstdtc`: "Study day 1 is the reference start date of the subject (DM.RFSTDTC)."

House default: `treatment_start`.

Study days are counted from this date, so it moves the study day of every record and with it
the assignment of records to visit windows and target days.

### Where it is stated

- SAP: general definitions ("study day", "relative day", "Day 1"), often with a formula.
- Protocol: schedule of assessments, the Day 1 column and its footnotes.
- Often clear from a formula even when no sentence defines Day 1.

### Words to look for

- `treatment_start`: "Day 1 is the day of the first dose", "study day is the date minus the
  date of first dose plus one", "relative to the start of study treatment".
- `dm_rfstdtc`: "relative to the reference start date", "study day as in the tabulation
  data", or the variable RFSTDTC named as the origin.

### Traps

- There is no study day 0: the day before day 1 is day -1. A document that calls the dosing
  day "Day 0" does not match that convention; report the passage.
- "Day 1 is the day of randomization" fits `dm_rfstdtc` only when the documents say that the
  reference start date is the randomization date. Otherwise report the passage.
- The "Day 1" visit of the schedule is a planned visit. It tells the origin only if a
  footnote ties it to first dosing or to another event.
- When first dose and reference start fall on the same day for every subject, both
  alternatives give the same days. Choose by the wording, not by that coincidence.
- Silent documents: use the house default `treatment_start` and cite the house standard.
