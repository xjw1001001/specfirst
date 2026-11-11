# When does treatment emergence begin? (`ae.teae.start`)

The answer decides whether an event on the day of the first dose counts as treatment-emergent
when its time is unknown or earlier than the dose. Every adverse event count depends on it.

## Where it is stated

- SAP: adverse event section, definition of a treatment-emergent adverse event.
- Protocol: safety or adverse event section, sometimes the statistical section.
- Nearly always stated; whether dates or dates and times are compared is often left open.

## Words to look for

- `on_or_after_first_dose_date`: "onset on or after the date of first dose", "starting on or
  after the day of first study treatment", "on or after Day 1".
- `at_or_after_first_dose_time`: "onset at or after the time of the first dose", "start date
  and time on or after the date and time of first dose", "after the first administration,
  taking the time into account".

## Traps

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
