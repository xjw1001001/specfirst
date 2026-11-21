# When does treatment emergence end? (`ae.teae.end`)

The answer decides whether events that start long after the last dose still count as
treatment-emergent, and so changes the counts of every adverse event table.

## Where it is stated

- SAP: adverse event section, in or right after the definition of treatment-emergent.
- Protocol: adverse event reporting period and safety follow-up; statistical section.
- Often missing from the definition itself, with a follow-up period described elsewhere.

## Words to look for

- `no_end`: a definition with a start condition only, "on or after the first dose" with no
  upper limit, "all events after the start of treatment", an "on-study" analysis.
- `last_dose_plus_days`: "up to 30 days after the last dose", "within 7 days of the last
  administration", "through N days after the end of treatment", an "on-treatment" analysis
  with a window. The slot `days` is that number.

## Traps

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
