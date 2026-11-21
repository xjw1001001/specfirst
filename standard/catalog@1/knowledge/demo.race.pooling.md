# Are small race categories pooled? (`demo.race.pooling`)

The answer decides whether the race rows of the demographics table show every collected
category or fold the rare ones into OTHER.

## Where it is stated

- SAP: section on demographics and baseline characteristics; footnotes of the table shell.
- Protocol: almost never.
- Usually unstated; a pooling rule is the exception.

## Words to look for

- `not_pooled`: "race will be summarized as collected", "all race categories are presented",
  a shell that lists every category of the case report form.
- `pooled_below_count`: "categories with fewer than 5 subjects will be combined into Other",
  "race groups with small numbers are pooled". The slot `count` is the stated number.

## Traps

- "Fewer than N" leaves out N itself: a category with exactly N subjects stays. A text that
  says "N or fewer" means a count of N + 1.
- The count is over all subjects of the subject-level dataset, whatever their arm; it is not
  taken per treatment column.
- A fixed regrouping such as "White, Black, Other", or pooling by a percentage, is not this
  rule and matches no alternative. Report the passage.
- "Small categories will be pooled" with no number leaves the slot open: report that the
  number is missing instead of choosing one.
- Silent documents: use the house default `not_pooled` and cite the house standard.
