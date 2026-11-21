# Which rows does the adverse event summary table have? (`tfl.ae.summary.rows`)

The answer fixes the rows of the adverse event summary (overview) table and their order.
Every row counts subjects with at least one treatment-emergent event of its kind.

## Where it is stated

- SAP: adverse event section, the sentence or list that describes the overview table.
- SAP table shells: the row labels of the summary or overview table.
- Protocol: statistical section, in general words.

## Words to look for

- `standard_rows`: exactly these six rows in this order, the order of the ARS example: any
  event, related events, serious events, serious related events, fatal events, events
  leading to discontinuation of study treatment.
- `stated_rows`: another selection or another order. The slot `rows` lists the codes in the
  stated order, out of ANY, RELATED, SERIOUS, SERIOUS_RELATED, DISCONTINUATION,
  DOSE_MODIFIED, FATAL and FATAL_RELATED.

## Traps

- Only these eight kinds can be rows. Severe events, events by seriousness criterion, events
  of special interest or events by action taken cannot be expressed; report them with the
  answer.
- "Leading to discontinuation" means that the action taken with study treatment was
  withdrawal of the drug, not that the subject left the study. "Leading to dose
  modification" is a dose reduction or an interruption.
- "Fatal" is an event marked as resulting in death (AESDTH), not the number of deaths from
  any cause. A SAP that counts events with an outcome of death (AEOUT) states another rule:
  report the passage.
- The same six rows in another order are `stated_rows`, not `standard_rows`.
- Silent documents: use the house default and cite the house standard.
