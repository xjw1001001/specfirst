# How is baseline body mass index obtained? (`demo.bmi.rule`)

The answer decides whether the body mass index in the demographics table is computed from
baseline weight and height or taken from the value recorded at the site.

## Where it is stated

- SAP: section on demographics and baseline characteristics, often as a formula; sometimes a
  list of derived variables.
- Protocol: schedule of assessments or vital signs section, if body mass index is collected.
- Often unstated when the index is simply listed among the characteristics.

## Words to look for

- `derived`: "BMI will be calculated as weight (kg) divided by height (m) squared", "derived
  from baseline weight and height", any formula.
- `as_collected`: "BMI as recorded on the case report form", "as reported by the site", "the
  collected value is used and not recalculated".

## Traps

- A protocol that has sites calculate the index for an inclusion criterion does not say that
  the table uses that value. Only a statement about the analysis counts.
- `derived` uses the baseline weight and height of `demo.baseline.record` and keeps the value
  at full precision (catalog@1 rounded it to one decimal in ADSL). A SAP that asks for a
  rounded BMIBL in the data is not covered; report the passage. The decimals a table shows
  are `tfl.decimals.rule`.
- Weight in kg and height in cm are assumed; other units are not converted.
- `as_collected` selects the collected value by the same rule as baseline weight and height
  (`demo.baseline.record`); it is not the screening value by default.
- A formula written with height in cm and a factor of 10000 is the same rule as `derived`.
- Silent documents: use the house default `derived` and cite the house standard.
