# Is there a total column? (`tfl.columns.total`)

The answer decides whether the table has a last column that pools arms, and which arms it
pools. It is given once per table family.

## Where it is stated

- SAP: general conventions for tables, the section of each analysis, and the column headers
  of the table shells ("Total", "Overall", "All Active").
- Protocol: almost never.
- Often shown only by the shells, and often different for demographics and safety tables.

## Words to look for

- `all_arms`: "a total column over all treatment groups", "overall", shell column "Total".
- `none`: "by treatment group" with no total in the shell, "no total column is shown".
- `active_arms`: "all active doses combined", "pooled active", shell column "Total Active".
  The slot `control` is the label of the arm left out, as its column shows it (usually
  Placebo).

## Traps

- "Total" in a shell next to dose columns can mean all arms or all active arms; read the
  header and its footnote before choosing.
- One answer per table family: a total column in the demographics shell says nothing about
  the adverse event tables.
- A table with both a pooled active column and an overall column, or with a pooled column
  that leaves out more than one arm, matches no alternative; report the passage.
- A total column is the last column. If a shell puts it elsewhere, mention that with the
  answer.
- Silent documents: use the house default and cite the house standard.
