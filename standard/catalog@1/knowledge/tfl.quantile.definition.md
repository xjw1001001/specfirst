# Which quantile definition gives the median and the quartiles? (`tfl.quantile.definition`)

The definition changes the first and third quartile of small groups. It is given once per
table family that shows continuous statistics.

## Where it is stated

- SAP: general conventions, the section on statistical software, or a note on descriptive
  statistics.
- Protocol: never.
- Almost always unstated; at most the software and its version are named.

## Words to look for

- `sas5`: "SAS default percentile definition", "definition 5", "empirical distribution
  function with averaging".
- `r7`: "R default quantile type", "type 7", "linear interpolation of the order statistics".

## Traps

- Naming the software is not naming the definition. "Analyses are done in SAS" or "in R"
  leaves this entry silent unless the text says that the default percentiles are used.
- Other definitions (SAS definitions 1 to 4, other R types) match no alternative; report the
  passage. R type 2 gives the same values as SAS definition 5; if a text names it, say so
  in the answer.
- The median is the same under both alternatives; they differ in the quartiles. A text that
  defines only the median does not settle this entry.
- Silent documents: use the house default `sas5` and cite the house standard.
