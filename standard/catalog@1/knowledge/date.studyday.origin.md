# Which date is study day 1? (`date.studyday.origin`)

Study days are counted from this date, so it moves the study day of every record and with it
the assignment of records to visit windows and target days.

## Where it is stated

- SAP: general definitions ("study day", "relative day", "Day 1"), often with a formula.
- Protocol: schedule of assessments, the Day 1 column and its footnotes.
- Often clear from a formula even when no sentence defines Day 1.

## Words to look for

- `treatment_start`: "Day 1 is the day of the first dose", "study day is the date minus the
  date of first dose plus one", "relative to the start of study treatment".
- `dm_rfstdtc`: "relative to the reference start date", "study day as in the tabulation
  data", or the variable RFSTDTC named as the origin.

## Traps

- There is no study day 0: the day before day 1 is day -1. A document that calls the dosing
  day "Day 0" does not match that convention; report the passage.
- "Day 1 is the day of randomization" fits `dm_rfstdtc` only when the documents say that the
  reference start date is the randomization date. Otherwise report the passage.
- The "Day 1" visit of the schedule is a planned visit. It tells the origin only if a
  footnote ties it to first dosing or to another event.
- When first dose and reference start fall on the same day for every subject, both
  alternatives give the same days. Choose by the wording, not by that coincidence.
- Silent documents: use the house default `treatment_start` and cite the house standard.
