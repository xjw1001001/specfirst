# How are p-values displayed? (`tfl.pvalue.format`)

The answer fixes the decimals of the p-value column of the demographics table and the text
shown for a very small p-value. It matters only when treatments are compared there.

## Where it is stated

- SAP: general conventions for tables ("p-values are presented to ... decimal places").
- SAP table shells: the pattern of the p-value column, such as 0.xxx.
- Protocol: never.

## Words to look for

- `three_decimals`: "p-values are reported to three decimal places", "values below 0.001 are
  shown as <0.001", shell pattern 0.xxx.
- `four_decimals`: "p-values are reported to four decimal places", "values below 0.0001 are
  shown as <0.0001", shell pattern 0.xxxx.

## Traps

- Decimals and lower limit go together in each alternative. Four decimals with "<0.001", or
  a rule to print a very small value as 0.000, match neither; report the passage. Decimals
  stated with no word on small values select the alternative with those decimals.
- Conventions for large p-values (">0.999") and for marks of significance are not covered.
- When treatments are not compared (`tfl.tests.include`) there is no p-value column and
  this answer changes nothing; still record what the documents state.
- A convention stated for all p-values of the study covers the demographics table; one
  stated for a single analysis does not.
- Silent documents: use the house default `three_decimals` and cite the house standard.
