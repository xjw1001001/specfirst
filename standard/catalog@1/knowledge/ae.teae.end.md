# When does treatment emergence end? (`ae.teae.end`)

The answer decides whether events that start long after the last dose still count as
treatment-emergent, and so changes the counts of every adverse event table.

## Where it is stated

- SAP: adverse event section, in or right after the definition of treatment-emergent.
- Protocol: adverse event reporting period and safety follow-up; statistical section.
- Often missing from the definition itself, with a follow-up period described elsewhere.

## Words to look for

- `no_end`: a definition with a start condition only, "on or after the first dose" with no
  upper limit, "all events after the start of treatment".
- `last_dose_plus_days`: "up to 30 days after the last dose", "within 7 days of the last
  administration", "through N days after the end of treatment". The slot `days` is that
  number.
- `end_of_study`: "until the end of the study", "through the subject's date of study
  completion or discontinuation".

## Traps

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
