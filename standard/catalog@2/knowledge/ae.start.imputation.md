# How are partial adverse event start dates completed? (`ae.start.imputation`)

The completed date is the analysis start date of the event, which decides whether an event
with an incomplete start date counts as treatment-emergent.

## Where it is stated

- SAP: section on missing or partial dates, or within the adverse event section, often as a
  list of cases (day missing; day and month missing).
- Protocol: rarely.
- Often stated only as "imputed conservatively" or "worst case", which names no rule.

## Words to look for

- `first_of_month_not_before_first_dose`: "a missing day is set to the first of the month;
  if month and year are those of the first dose, the date of first dose is used instead".
- `first_of_month`: "a missing day is set to 01", "first day of the month", with no reference
  to the first dose.
- `not_completed`: "partial dates will not be imputed", "incomplete start dates stay missing".

## Traps

- "Not before first dose" acts only when the treatment start date falls in the month of the
  partial date. A partial date in an earlier month becomes the first of that month.
- No alternative completes a date with an unknown month. Rules that set a missing month to
  January, or use the first dose date within the year of first dose, are not covered; report
  the passage.
- Under `not_completed` the event has no analysis start date, and `ae.teae.start` then counts
  it as treatment-emergent. Not completed does not mean not treatment-emergent.
- Rules for end dates (last day of the month) and for medication dates are other topics.
- Silent documents: use the house default and cite the house standard.
