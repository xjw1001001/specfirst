---
name: mod-ae-emergence
description: Reading notes v0 for the unit mod-ae-emergence (Adverse event emergence). For each of its 4 catalog questions, where a protocol or a statistical analysis plan states the decision, the words to look for and the traps. Rendered from the decision catalog specfirst-m1 2 and the house standard open-default@2.
---

# Adverse event emergence (mod-ae-emergence): reading notes v0

Rendered from the decision catalog `specfirst-m1` version 2 and the house standard `open-default@2` by `specfirst run skills --write`; do not edit by hand. Read `core-reader` first: it says how to record a decision. Here, for every question of the unit: its alternatives with the statement each gives, the house default, and where documents state it.

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
- Silent documents: use the house default and cite the house standard.

## `ae.teae.start`: When does treatment emergence begin?

Alternatives:

- `on_or_after_first_dose_date` (the house default): "An adverse event is treatment-emergent when it starts on or after the treatment start date."
  Meaning: Dates are compared; times are ignored.
- `at_or_after_first_dose_time`: "An adverse event is treatment-emergent when it starts at or after the date and time of the first dose."
  Meaning: A start or a first dose collected without a time counts from 00:00 of its day.
- `by_time_when_collected`: "An adverse event is treatment-emergent when it starts on or after the first dose, comparing date and time where both were collected and dates otherwise."
  Meaning: On the first dose date, an event is not treatment-emergent only when both its start time and the time of the first dose were collected and it starts before the dose; an event on that date without a collected time is treatment-emergent.

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
  taking the time into account", with no rule for a missing time.
- `by_time_when_collected`: "the time is used when it is available", "if the time is
  missing, the date is used", "events on the day of the first dose are emergent unless known
  to start before the dose".
- A protocol written to ICH M11 says "participant" for subject and "study intervention" for
  study treatment: "on or after the first dose of study intervention".

### Traps

- "After the first dose" without a word on time does not settle dates against times. If the
  documents never mention times for this comparison, treat that question as silent.
- Under `at_or_after_first_dose_time` a start or a dose without a time counts from 00:00 of
  its day: an event on the dose day with no time is before a dose timed later that day. Under
  `by_time_when_collected` the same event is emergent.
- The fixed rules hold for every alternative (STANDARD.md anchors them): a subject without a
  treatment start date has no emergent events; an event that ends before the treatment start
  date is not emergent; an event without an analysis start date is emergent; worsening does
  not make an event emergent. A document that states one of them differently is a conflict:
  cite the fixed rule.
- The end of the emergence period is `ae.teae.end`.
- Silent documents: use the house default and cite the house standard.

## `ae.teae.end`: When does treatment emergence end?

Alternatives:

- `no_end`: "Treatment emergence has no end date."
  Meaning: Every event that starts on or after the start of treatment emergence is treatment-emergent, however long after the treatment end date (the on-study reading of the FDA guide).
- `last_dose_plus_days` (the house default), slots days: "Treatment emergence ends {days} days after the treatment end date, that day included."
  Meaning: An event that starts later than that many days after the treatment end date is not treatment-emergent; one that starts on the last day of the window still is.

House default: `last_dose_plus_days`, days 30.

The answer decides whether events that start long after the last dose still count as
treatment-emergent, and so changes the counts of every adverse event table.

### Where it is stated

- SAP: adverse event section, in or right after the definition of treatment-emergent.
- Protocol: adverse event reporting period and safety follow-up; statistical section.
- Often missing from the definition itself, with a follow-up period described elsewhere.

### Words to look for

- `no_end`: a definition with a start condition only, "on or after the first dose" with no
  upper limit, "all events after the start of treatment", an "on-study" analysis.
- `last_dose_plus_days`: "up to 30 days after the last dose", "within 7 days of the last
  administration", "through N days after the end of treatment", an "on-treatment" analysis
  with a window. The slot `days` is that number.

### Traps

- The limit is inclusive: an event that starts exactly N days after the treatment end date is
  still treatment-emergent. "Within 30 days" gives 30.
- The window is counted from the treatment end date (`trt.end.source`), not from the last
  visit. A period in weeks converts to days (4 weeks gives 28); a period in half-lives has
  no number of days, so report the passage.
- "Until the end of the study" or "through study completion" matches no alternative of this
  catalog version (catalog@1 had one without a public source, removed in catalog@2): report
  the passage.
- The protocol's reporting period (how long sites collect events) is not the analysis rule.
  Use it only if the SAP defines emergence by it.
- A subject without a treatment end date has no end (fixed rule `no_end_date`).
- A SAP that is silent on the end of emergence rarely means "no end": a follow-up period
  elsewhere in the documents may state it. Look before taking the house default.
- Silent documents: use the house default and cite the house standard.

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
- A protocol written to ICH M11 says "participant" for subject and "study intervention" for
  study treatment; read them as the same words.

### Traps

- Values are compared exactly with the collected causality. Use the wording of the collected
  scale (for example POSSIBLE, not "possibly related") when the documents show it; if only
  the prose form is given, say so in the answer.
- Many SAPs count an event with missing causality as related. A list of values cannot
  express that; report the sentence with the answer.
- "Unlikely related" is the usual boundary case. Include it only if the text does.
- A two-level scale (related, not related) still needs the list; it then has one value.
- Silent documents: when the house standard states no default for this entry, do not guess
  from the scale; a person must be asked.
