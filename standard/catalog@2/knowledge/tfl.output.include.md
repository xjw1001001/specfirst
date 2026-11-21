# Is the output part of the planned outputs of the study? (`tfl.output.include`)

The answer is given once per table family: the demographics table, the adverse event summary
table, the adverse event table by system organ class and preferred term, and the vital signs
table by visit. An output that is not included is not produced, and no other decision of its
family applies.

## Where it is stated

- SAP: list of planned tables, listings and figures, or the contents page of the shells.
- SAP: the sections on demographics, adverse events and vital signs, which say what is
  summarized.
- Protocol: statistical section, in general words only.

## Words to look for

- `included`: the output has a title in the list of planned tables, or the text says that
  the item "will be summarized by treatment group" (for vital signs, by visit).
- `not_included`: the text says the item is listed only ("vital signs will be provided in
  listings"), or a complete list of planned tables has no such table.

## Traps

- Match by content, not by title. An "overview of adverse events" is the adverse event
  summary table; "incidence of adverse events by primary system organ class and preferred
  term" is the table by system organ class and preferred term.
- Absence from a list counts only when the list is clearly complete. A SAP with no list of
  outputs is silent; it does not say that the output is left out.
- A listing or a figure of the same data is not the table.
- Answer each table family on its own; one can be included and another not.
- Silent documents: use the house default `included` and cite the house standard.
