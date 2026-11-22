# Which record gives baseline weight and height? (`demo.baseline.record`)

The answer picks the weight and height values shown in the demographics table and used for
the body mass index at baseline.

## Where it is stated

- SAP: section on demographics and baseline characteristics; general definition of baseline.
- Protocol: schedule of assessments, the visits at which weight and height are measured
  (height is often measured at screening only).
- Often covered only by the general baseline definition of the SAP.

## Words to look for

- `last_on_or_before_first_dose`: "the last available value on or before the first dose
  date", "the last value prior to or on the day of first study treatment".
- `at_visit`: "the screening value is used", "height and weight as measured at the Screening
  visit", "the Day 1 measurement". The slot `visit` is the visit name as the schedule of
  assessments writes it.

## Traps

- "On or before" compares dates: a value on the first dose date counts. This entry has no
  alternative that uses the time of the dose and none that leaves out the first dose date;
  if the text requires either for weight and height, say so in the answer.
- One rule serves both weight and height. "Screening height and Day 1 weight" names two
  visits and matches no alternative; report the passage.
- A general baseline definition in the SAP covers weight and height unless the demographics
  section names a visit. The baseline of by-visit parameters is `bds.baseline.rule`.
- The visit name is compared exactly with the collected visit name; copy it as written.
- Silent documents: use the house default and cite the house standard.
