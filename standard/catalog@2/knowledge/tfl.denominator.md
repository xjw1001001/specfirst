# What is the denominator of a percentage? (`tfl.denominator`)

The answer changes every percentage of a categorical row of the demographics table in which
some subjects have no value.

## Where it is stated

- SAP: general conventions for tables ("percentages are based on ..."); footnotes of the
  demographics shell.
- Protocol: almost never.
- Frequently stated once for all tables, sometimes not at all.

## Words to look for

- `analysis_set_per_column`: "percentages are based on the number of subjects of the analysis
  set in each treatment group", "the denominator is the N of the column header".
- `subjects_with_data`: "percentages are based on the number of subjects with non-missing
  data", "subjects with a missing value are left out of the denominator".

## Traps

- Capital N against small n: by common usage N is the column total and n the number with
  data, but check the footnote that defines them before relying on it.
- A "Missing" row in the shell does not decide it. Use a stated rule; if there is none, the
  entry is silent.
- A convention written for adverse event tables (percent of subjects of the safety set) says
  nothing here; this entry is for the demographics table only.
- Silent documents: use the house default and cite the house standard.
