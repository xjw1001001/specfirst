# Which rows does the adverse event summary table have? (`tfl.ae.summary.rows`)

The answer fixes the rows of the adverse event summary (overview) table and their order.
Every row counts subjects with at least one treatment-emergent event of its kind.

## Where it is stated

- SAP: adverse event section, the sentence or list that describes the overview table.
- SAP table shells: the row labels of the summary or overview table.
- Protocol: statistical section, in general words.

## Words to look for

- `standard_rows`: exactly these five rows in this order: any event, related events, serious
  events, events leading to discontinuation of study treatment, fatal events.
- `stated_rows`: another selection or another order of those five. The slot `rows` lists
  the codes in the stated order, out of ANY, RELATED, SERIOUS, DISCONTINUATION and FATAL.

## Traps

- Only these five kinds can be rows. Severe events, serious related events, events of
  special interest or events leading to dose reduction cannot be expressed; report them with
  the answer.
- "Leading to discontinuation" means that the action taken with study treatment was
  withdrawal of the drug, not that the subject left the study.
- "Fatal" is an event that resulted in death, not the number of deaths from any cause.
- The same five rows in another order are `stated_rows`, not `standard_rows`.
- Silent documents: use the house default `standard_rows` and cite the house standard.
