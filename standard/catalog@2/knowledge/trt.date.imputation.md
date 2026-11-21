# How are partial exposure dates completed? (`trt.date.imputation`)

The answer decides whether a dosing date collected without a day can still give a treatment
start or end date, and so whether such a subject has study days and counts as dosed.

## Where it is stated

- SAP: section on missing or partial dates, or on data handling conventions.
- Many SAPs cover only adverse event and concomitant medication dates and say nothing about
  dosing dates.
- Protocol: almost never.

## Words to look for

- `not_completed`: "dosing dates will not be imputed", "incomplete dates of study drug
  administration are left missing", "no imputation of exposure dates".
- `first_day_of_month`: "a missing day is set to the first day of the month", "day imputed as
  01 when month and year are known", said of dosing or exposure dates.

## Traps

- A rule written for adverse event or medication dates does not carry over to exposure dates.
  Adverse event start dates are `ae.start.imputation`.
- Under `first_day_of_month` a date with an unknown month is still not completed. Rules that
  set a missing month to January or to mid-year match no alternative.
- The entry has one rule for start and end dates alike. A SAP that completes end dates with
  the last day of the month, or any date with the 15th, is not covered: report the passage.
- A general sentence such as "partial dates are imputed conservatively" names no rule; treat
  it as silent.
- Silent documents: use the house default and cite the house standard. Do not
  infer a rule from the data.
