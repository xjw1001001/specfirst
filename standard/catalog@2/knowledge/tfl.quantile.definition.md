# Which quantile definition gives the median and the quartiles? (`tfl.quantile.definition`)

The definition changes the first and third quartile of small groups. From catalog@2 it is
given for the demographics table only, the one table that can show quartiles.

## Where it is stated

- SAP: general conventions, the section on statistical software, or a note on descriptive
  statistics.
- Protocol: never.
- Almost always unstated; at most the software and its version are named.

## Words to look for

- `sas5`: "SAS default percentile definition", "definition 5", "empirical distribution
  function with averaging", "R type 2".
- `r7`: "R default quantile type", "type 7", "linear interpolation of the order statistics".

## Traps

- Naming the software is not naming the definition. "Analyses are done in SAS" or "in R"
  leaves this entry silent unless the text says that the default percentiles are used.
- Other definitions (SAS definitions 1 to 4, R types other than 2 and 7) match no
  alternative; report the passage.
- The median is the same under both alternatives; they differ in the quartiles. A text that
  defines only the median does not settle this entry, and a definition for the vital signs
  table changes nothing (it shows no quartile).
- Silent documents: use the house default and cite the house standard.
