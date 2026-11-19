---
name: mod-ae-emergence
description: Reading notes v0 for the unit mod-ae-emergence (Adverse event emergence). For each of its 4 catalog questions, where a protocol or a statistical analysis plan states the decision, the words to look for and the traps. Rendered from the decision catalog specfirst-m1 1.
---

# Adverse event emergence (mod-ae-emergence): reading notes v0

Rendered from the decision catalog `specfirst-m1` version 1 by `specfirst run skills --write`; do not edit by hand. Read `core-reader` first: it says how to record a decision. Here, for every question of the unit: its alternatives with the statement each gives, the house default, and where documents state it.

Questions of this unit: `ae.start.imputation`, `ae.teae.start`, `ae.teae.end`, `ae.related.values`.

## `ae.start.imputation`: How are partial adverse event start dates completed?

Alternatives:

- `first_of_month_not_before_first_dose` (the house default): "A partial adverse event start date with a known month is completed with the first day of that month, or with the treatment start date when it falls in that month."
  Meaning: A date with an unknown month is not completed.
- `first_of_month`: "A partial adverse event start date with a known month is completed with the first day of that month."
  Meaning: A date with an unknown month is not completed.
- `not_completed`: "A partial adverse event start date is not completed and gives no analysis start date."

House default: `first_of_month_not_before_first_dose`.

The completed date is the analysis start date of the event, which decides whether an event
with an incomplete start date counts as treatment-emergent.

### Where it is stated

- SAP: section on missing or partial dates, or within the adverse event section, often as a
  list of cases (day missing; day and month missing).
- Protocol: rarely.
- Often stated only as "imputed conservatively" or "worst case", which names no rule.

### Words to look for

- `first_of_month_not_before_first_dose`: "a missing day is set to the first of the month;
  if month and year are those of the first dose, the date of first dose is used instead".
- `first_of_month`: "a missing day is set to 01", "first day of the month", with no reference
  to the first dose.
- `not_completed`: "partial dates will not be imputed", "incomplete start dates stay missing".

### Traps

- "Not before first dose" acts only when the treatment start date falls in the month of the
  partial date. A partial date in an earlier month becomes the first of that month.
- No alternative completes a date with an unknown month. Rules that set a missing month to
  January, or use the first dose date within the year of first dose, are not covered; report
  the passage.
- Under `not_completed` the event has no analysis start date, and `ae.teae.start` then counts
  it as treatment-emergent. Not completed does not mean not treatment-emergent.
- Rules for end dates (last day of the month) and for medication dates are other topics.
- Silent documents: use the house default `first_of_month_not_before_first_dose` and cite
  the house standard.

## `ae.teae.start`: When does treatment emergence begin?

Alternatives:

- `on_or_after_first_dose_date` (the house default): "An adverse event is treatment-emergent when it starts on or after the treatment start date."
  Meaning: Dates are compared; times are ignored.
- `at_or_after_first_dose_time`: "An adverse event is treatment-emergent when it starts at or after the date and time of the first dose."
  Meaning: A start or a first dose collected without a time counts from 00:00 of its day.

House default: `on_or_after_first_dose_date`.

The answer decides whether an event on the day of the first dose counts as treatment-emergent
when its time is unknown or earlier than the dose. Every adverse event count depends on it.

### Where it is stated

- SAP: adverse event section, definition of a treatment-emergent adverse event.
- Protocol: safety or adverse event section, sometimes the statistical section.
- Nearly always stated; whether dates or dates and times are compared is often left open.

### Words to look for

- `on_or_after_first_dose_date`: "onset on or after the date of first dose", "starting on or
  after the day of first study treatment", "on or after Day 1".
- `at_or_after_first_dose_time`: "onset at or after the time of the first dose", "start date
  and time on or after the date and time of first dose", "after the first administration,
  taking the time into account".

### Traps

- "After the first dose" without a word on time does not settle dates against times. If the
  documents never mention times for this comparison, treat that question as silent.
- Under `at_or_after_first_dose_time` a start or a dose without a time counts from 00:00 of
  its day: an event on the dose day with no time is before a dose timed later that day.
- Fixed for every alternative: a subject without a treatment start date has no emergent
  events; an event that ends before the treatment start date is not emergent; an event
  without an analysis start date is emergent.
- Worsening of an event present before treatment is not part of this entry. The end of the
  emergence period is `ae.teae.end`.
- Silent documents: use the house default `on_or_after_first_dose_date` and cite the house
  standard.

## `ae.teae.end`: When does treatment emergence end?

Alternatives:

- `no_end` (the house default): "Treatment emergence has no end date."
- `last_dose_plus_days`, slots days: "Treatment emergence ends {days} days after the treatment end date."
  Meaning: An event that starts on the last day of the window is still treatment-emergent. A subject without a treatment end date has no end.
- `end_of_study`: "Treatment emergence ends at the end-of-study date."
  Meaning: An event that starts on the end-of-study date is still treatment-emergent. A subject without an end-of-study date has no end.

House default: `no_end`.

The answer decides whether events that start long after the last dose still count as
treatment-emergent, and so changes the counts of every adverse event table.

### Where it is stated

- SAP: adverse event section, in or right after the definition of treatment-emergent.
- Protocol: adverse event reporting period and safety follow-up; statistical section.
- Often missing from the definition itself, with a follow-up period described elsewhere.

### Words to look for

- `no_end`: a definition with a start condition only, "on or after the first dose" with no
  upper limit, "all events after the start of treatment".
- `last_dose_plus_days`: "up to 30 days after the last dose", "within 7 days of the last
  administration", "through N days after the end of treatment". The slot `days` is that
  number.
- `end_of_study`: "until the end of the study", "through the subject's date of study
  completion or discontinuation".

### Traps

- The limit is inclusive: an event that starts exactly N days after the treatment end date,
  or on the end-of-study date, is still treatment-emergent. "Within 30 days" gives 30.
- The window is counted from the treatment end date (`trt.end.source`), not from the last
  visit. A period in weeks converts to days (4 weeks gives 28); a period in half-lives has
  no number of days, so report the passage.
- The protocol's reporting period (how long sites collect events) is not the analysis rule.
  Use it only if the SAP defines emergence by it.
- A subject without a treatment end date, or without an end-of-study date, has no end under
  the alternative that needs that date.
- Silent documents: use the house default `no_end` and cite the house standard.

## `ae.related.values`: Which causality values count as related to study treatment?

Alternatives:

- `stated_list`, slots values: "An adverse event is related to study treatment when its causality is one of {values}."
  Meaning: The causality is the collected value of AEREL, compared exactly.

House default: none. A document states it, or it is asked.

The list decides which events count as related, as in the related row of the adverse event
summary table. An event whose causality value is not in the list is not related.

### Where it is stated

- SAP: adverse event section, definition of a treatment-related or drug-related event.
- Protocol: adverse event section, the causality (relationship) categories the investigator
  chooses from; the case report form shows the exact values.
- The scale differs from study to study, so it must be read from the documents.

### Words to look for

- `stated_list`: "related events are those assessed as possibly, probably or definitely
  related", "events with a relationship of related", "related includes ...". The slot
  `values` is the list of collected causality values that count, as the study collects them.

### Traps

- Values are compared exactly with the collected causality. Use the wording of the collected
  scale (for example POSSIBLE, not "possibly related") when the documents show it; if only
  the prose form is given, say so in the answer.
- Many SAPs count an event with missing causality as related. A list of values cannot
  express that; report the sentence with the answer.
- "Unlikely related" is the usual boundary case. Include it only if the text does.
- A two-level scale (related, not related) still needs the list; it then has one value.
- Silent documents: this entry has no house default. Do not guess from the scale;
  a person must be asked.
