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
  taking the time into account", with no rule for a missing time.
- `by_time_when_collected`: "the time is used when it is available", "if the time is
  missing, the date is used", "events on the day of the first dose are emergent unless known
  to start before the dose".
- A protocol written to ICH M11 says "participant" for subject and "study intervention" for
  study treatment: "on or after the first dose of study intervention".

## Traps

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
