# Are treatments compared in the demographics table? (`tfl.tests.include`)

The answer decides whether the demographics table has a p-value column after the treatment
columns, and which tests fill it.

## Where it is stated

- SAP: section on demographics and baseline characteristics; footnotes of the table shell.
- Protocol: statistical section, baseline comparability, if mentioned at all.
- Many SAPs say outright that no formal comparison of baseline data is made.

## Words to look for

- `none`: "no statistical testing of baseline characteristics", "summarized descriptively
  only", a shell without a p-value column.
- `anova_chisq`: "continuous variables are compared by analysis of variance, categorical
  variables by the chi-square test".
- `anova_fisher`: "analysis of variance for continuous variables and Fisher's exact test for
  categorical variables".

## Traps

- The analysis of variance is one-way, with treatment as the only factor. A model with site
  or strata, a t-test or a rank-based test matches no alternative; report the passage.
- "Chi-square test, or Fisher's exact test when expected counts are small" is a conditional
  rule that neither alternative expresses; report the passage.
- A stratified test for categorical data is not the chi-square test meant here.
- Tests named for efficacy endpoints do not say that demographics are tested.
- Silent documents: use the house default `none` and cite the house standard.
