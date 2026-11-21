# Which record is the baseline of each parameter? (`bds.baseline.rule`)

The baseline record gives the baseline value of each parameter, so it changes every change
from baseline and the Baseline row of the by-visit tables.

## Where it is stated

- SAP: general definitions, "baseline"; sometimes repeated in single analysis sections.
- Protocol: statistical section; schedule of assessments (which visit is called Baseline,
  and footnotes saying that assessments are done before dosing).
- Nearly always stated in the SAP, but often without saying how the dose day is handled.

## Words to look for

- `last_before_first_dose`: "the last non-missing value before the first dose", "prior to
  the first administration of study treatment", "the last pre-dose value".
- `last_on_or_before_first_dose_date`: "the last value on or before the date of first dose",
  "on or prior to Day 1", "up to and including the first dose date".
- `scheduled_baseline_visit`: "baseline is the value at the Baseline visit", "the Screening
  value", "the Day 1 assessment". The slot `visit` is the visit name as the schedule of
  assessments writes it.

## Traps

- Under `last_before_first_dose` a value on the first dose date counts as before the dose,
  unless both its time and the time of the first dose were collected and its time is not
  earlier. A dose-day value without a collected time can therefore be baseline.
- Under `last_on_or_before_first_dose_date` times are ignored: a value taken after dosing on
  the first dose date can become baseline.
- "The Day 1 value, or the screening value if it is missing" does not fit
  `scheduled_baseline_visit`, which uses one visit only. Report the passage with the answer.
- Whether records of unscheduled visits may be baseline is `bds.unscheduled.use`. An average
  of several pre-dose values matches no alternative; report the passage.
- Silent documents: use the house default `last_before_first_dose` and cite the house
  standard.
