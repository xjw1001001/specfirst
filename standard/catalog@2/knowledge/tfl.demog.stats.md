# Which statistics do the continuous rows show? (`tfl.demog.stats`)

The answer decides whether continuous rows of the demographics table (age, height, weight,
body mass index) show the first and third quartile next to the other statistics.

## Where it is stated

- SAP: general conventions ("continuous variables are summarized by ...").
- SAP table shells: the statistic labels under a continuous row of the demographics table.
- Protocol: statistical section, sometimes in the same words. Usually stated somewhere.

## Words to look for

- `n_mean_sd_median_min_max`: "n, mean, standard deviation, median, minimum and maximum",
  "number of observations, mean, SD, median and range".
- `with_quartiles`: the same list with "first and third quartiles", "Q1 and Q3", "25th and
  75th percentiles" or "interquartile range".

## Traps

- "Range" means minimum and maximum. "Interquartile range" selects `with_quartiles`, which
  shows the two quartiles, not their difference.
- Other sets (with standard error, coefficient of variation, geometric mean or the number
  missing) match no alternative; report the passage.
- A general convention applies to the demographics table unless its shell shows otherwise;
  if text and shell disagree, cite both passages.
- This entry is for the demographics table only; it does not decide the vital signs table.
- Silent documents: use the house default and cite the house standard.
