# How many decimals does each statistic have? (`tfl.decimals.rule`)

The answer fixes the decimals of the mean, standard deviation, median, quartiles, minimum
and maximum in continuous rows. It is given once per table family.

## Where it is stated

- SAP: general conventions for tables ("descriptive statistics are presented with ...").
- SAP table shells: the cell patterns, such as xx.x for a mean and xx.xx for a standard
  deviation.
- Protocol: never.

## Words to look for

- `relative_to_data`: "mean and median to one more decimal place than the collected data,
  standard deviation to two more, minimum and maximum to the same number as the data".
- `stated_decimals`: fixed numbers, such as "means are shown to 1 decimal and standard
  deviations to 2". The slots `mean`, `sd`, `median` and `range` are the decimals stated for
  the mean, the standard deviation, the median, and the minimum and maximum.

## Traps

- A relative rule with other offsets (for example the standard deviation to one more decimal
  than the data, not two) matches neither alternative; report the passage.
- Under `relative_to_data` the decimals of the data are the largest number of decimals among
  the values summarized in the row, not the decimals the form allows.
- Shell patterns such as xx.x are sketches. Use them for `stated_decimals` only when the SAP
  says that the shells fix the precision, and only if all four slots can be filled.
- One number serves minimum and maximum; quartiles are shown as the median is.
- Silent documents: use the house default `relative_to_data` and cite the house standard.
