---
name: tfl-ae-summary
description: Reading notes v0 for the unit tfl-ae-summary (Summary table of adverse events). For each of its 7 catalog questions, where a protocol or a statistical analysis plan states the decision, the words to look for and the traps. Rendered from the decision catalog specfirst-m1 1.
---

# Summary table of adverse events (tfl-ae-summary): reading notes v0

Rendered from the decision catalog `specfirst-m1` version 1 by `specfirst run skills --write`; do not edit by hand. Read `core-reader` first: it says how to record a decision. Here, for every question of the unit: its alternatives with the statement each gives, the house default, and where documents state it.

Questions of this unit: `tfl.output.include`, `tfl.population`, `tfl.columns.arms`, `tfl.columns.total`, `tfl.percent.format`, `tfl.rounding.rule`, `tfl.ae.summary.rows`.

## `tfl.output.include`: Is the output part of the planned outputs of the study?

Alternatives:

- `included` (the house default): "The planned outputs include {output}."
- `not_included`: "The planned outputs do not include {output}."
  Meaning: No other decision of the table family applies then.

House default: `included`.

The answer is given once per table family: the demographics table, the adverse event summary
table, the adverse event table by system organ class and preferred term, and the vital signs
table by visit. An output that is not included is not produced, and no other decision of its
family applies.

### Where it is stated

- SAP: list of planned tables, listings and figures, or the contents page of the shells.
- SAP: the sections on demographics, adverse events and vital signs, which say what is
  summarized.
- Protocol: statistical section, in general words only.

### Words to look for

- `included`: the output has a title in the list of planned tables, or the text says that
  the item "will be summarized by treatment group" (for vital signs, by visit).
- `not_included`: the text says the item is listed only ("vital signs will be provided in
  listings"), or a complete list of planned tables has no such table.

### Traps

- Match by content, not by title. An "overview of adverse events" is the adverse event
  summary table; "incidence of adverse events by primary system organ class and preferred
  term" is the table by system organ class and preferred term.
- Absence from a list counts only when the list is clearly complete. A SAP with no list of
  outputs is silent; it does not say that the output is left out.
- A listing or a figure of the same data is not the table.
- Answer each table family on its own; one can be included and another not.
- Silent documents: use the house default `included` and cite the house standard.

## `tfl.population`: Which analysis set does the output use?

Alternatives:

- `safety` (the house default): "The analysis set of {output} is the safety set."
- `randomized`: "The analysis set of {output} is the randomized set."
- `efficacy`: "The analysis set of {output} is the efficacy-evaluable set."

House default: `safety`.

The analysis set fixes which subjects the table counts and the number in each column header.
The answer is given once per table family.

### Where it is stated

- SAP: the section of each analysis ("demographics will be summarized for the ... set"), the
  section on analysis sets, and the title or subtitle line of each table shell.
- Protocol: statistical section, in general words.
- Usually stated for safety tables; for demographics it varies between studies.

### Words to look for

- `safety`: "safety population", "safety analysis set", "all treated subjects".
- `randomized`: "intent-to-treat population", "full analysis set", "all randomized subjects",
  "randomized set".
- `efficacy`: "efficacy-evaluable set", "evaluable population", when it is the set that
  `pop.efficacy.rule` defines.

### Traps

- Map the name through the SAP's own definitions, not by the name alone: a "full analysis
  set" is all randomized subjects in one study and a narrower set in another.
- Demographics are often shown on several sets. Take the set of the main demographics table;
  if the text names several and no main one, report the passage.
- If a shell subtitle and the SAP text disagree, cite both passages in the answer.
- "All enrolled" or "all screened" subjects match no alternative; report the passage.
- Silent documents: the house default depends on the table family. It is `randomized` for the
  demographics table and `safety` for the two adverse event tables and the vital signs table.
  Cite the house standard.

## `tfl.columns.arms`: In which order are the treatment columns?

Alternatives:

- `ascending_dose_placebo_first` (the house default): "The treatment columns of {output} are in ascending order of dose, with placebo first."
- `protocol_order`: "The treatment columns of {output} are in the order in which the protocol lists the arms."

House default: `ascending_dose_placebo_first`.

The answer fixes the left-to-right order of the treatment columns of the table. It is given
once per table family; the counts do not change.

### Where it is stated

- SAP: general conventions for tables ("treatment groups are displayed in the order ..."),
  and the column headers of the table shells.
- Protocol: the order in which the study design section lists the arms.
- Often shown only by the shells.

### Words to look for

- `ascending_dose_placebo_first`: "placebo, then active doses from lowest to highest",
  "placebo first, followed by increasing dose", shells headed Placebo, Low Dose, High Dose.
- `protocol_order`: "in the order of the treatment arms in the protocol", "as listed in the
  study design", shells that follow the protocol's list of arms where it is not dose order.

### Traps

- "Active treatment first, then placebo" is `protocol_order` only if the protocol lists the
  arms that way. Otherwise it matches no alternative; report the passage.
- When the protocol lists placebo first and the doses ascending, both alternatives give the
  same order. Pick the one the text states.
- An active comparator has no place in a dose order. If the study has one and the text does
  not say where its column goes, report that.
- The total column is `tfl.columns.total`, not this entry.
- Silent documents: use the house default `ascending_dose_placebo_first` and cite the house
  standard.

## `tfl.columns.total`: Is there a total column?

Alternatives:

- `all_arms` (the house default): "A total column of {output} pools all treatment arms."
- `none`: "There is no total column in {output}."
- `active_arms`, slots control: "A total column of {output} pools the treatment arms other than {control}."
  Meaning: The control is named by its treatment label as the treatment columns show it.

House default: `all_arms`.

The answer decides whether the table has a last column that pools arms, and which arms it
pools. It is given once per table family.

### Where it is stated

- SAP: general conventions for tables, the section of each analysis, and the column headers
  of the table shells ("Total", "Overall", "All Active").
- Protocol: almost never.
- Often shown only by the shells, and often different for demographics and safety tables.

### Words to look for

- `all_arms`: "a total column over all treatment groups", "overall", shell column "Total".
- `none`: "by treatment group" with no total in the shell, "no total column is shown".
- `active_arms`: "all active doses combined", "pooled active", shell column "Total Active".
  The slot `control` is the label of the arm left out, as its column shows it (usually
  Placebo).

### Traps

- "Total" in a shell next to dose columns can mean all arms or all active arms; read the
  header and its footnote before choosing.
- One answer per table family: a total column in the demographics shell says nothing about
  the adverse event tables.
- A table with both a pooled active column and an overall column, or with a pooled column
  that leaves out more than one arm, matches no alternative; report the passage.
- A total column is the last column. If a shell puts it elsewhere, mention that with the
  answer.
- Silent documents: use the house default `all_arms` and cite the house standard.

## `tfl.percent.format`: How are percentages displayed?

Alternatives:

- `one_decimal_zero_blank` (the house default): "Percentages in {output} have one decimal, and a count of zero is shown without a percentage."
- `one_decimal_always`: "Percentages in {output} have one decimal, and a count of zero is shown with its percentage."

House default: `one_decimal_zero_blank`.

The answer decides what a cell with a count of zero shows: the count alone, or the count
with its percentage. It is given once per table family.

### Where it is stated

- SAP: general conventions for tables and the notes to the table shells.
- Protocol: never.
- Often unstated, or visible only in the layout of a shell.

### Words to look for

- `one_decimal_zero_blank`: "percentages are shown to one decimal place; no percentage is
  shown for a count of zero", shell cells written "0" where others are "xx (xx.x)".
- `one_decimal_always`: "percentages are shown to one decimal place" together with zero
  cells written "0 (0.0)", or "a percentage is always displayed".

### Traps

- Both alternatives have one decimal. A SAP that asks for whole-number percentages or for
  two decimals matches no alternative; report the passage.
- "One decimal place" alone does not say what happens at zero. Use the house default then,
  and say that only the decimal was stated.
- Special displays such as "<0.1" for small percentages, or "100" without a decimal, are not
  covered; report them.
- A shell is a layout sketch: "xx (xx.x)" in every cell does not prove that a zero count gets
  a percentage.
- Silent documents: use the house default `one_decimal_zero_blank` and cite the house
  standard.

## `tfl.rounding.rule`: How are displayed numbers rounded?

Alternatives:

- `half_away_from_zero` (the house default): "Displayed numbers in {output} are rounded half away from zero."
- `half_even`: "Displayed numbers in {output} are rounded half to even."

House default: `half_away_from_zero`.

The rule changes a displayed mean, percentage or other statistic only when its exact value
lies halfway between two values that can be displayed. It is given once per table family.

### Where it is stated

- SAP: general conventions for tables or for numerical precision.
- Protocol: never.
- Almost always unstated; "rounded to one decimal" says how far, not how.

### Words to look for

- `half_away_from_zero`: "conventional rounding", "a final 5 is rounded up", "rounded away
  from zero".
- `half_even`: "round half to even", "banker's rounding", "a final 5 is rounded to the
  nearest even digit".

### Traps

- For positive numbers "round half up" and half away from zero agree; for negative numbers
  such as changes from baseline they differ. Treat plain "half up" as `half_away_from_zero`
  and say so in the answer.
- A number is rounded once, from full precision to the displayed decimals. A text that
  rounds a value and then computes from the rounded value describes something else; report
  the passage.
- Truncation ("values are cut to one decimal") matches no alternative.
- The number of decimals is not decided here (`tfl.decimals.rule`, `tfl.percent.format`).
- Silent documents: use the house default `half_away_from_zero` and cite the house standard.

## `tfl.ae.summary.rows`: Which rows does the adverse event summary table have?

Alternatives:

- `standard_rows` (the house default): "The rows of the adverse event summary table are any event, related events, serious events, events leading to discontinuation of study treatment, and fatal events."
- `stated_rows`, slots rows: "The rows of the adverse event summary table are, in this order, {rows}."
  Meaning: Each row is named by its code: ANY, RELATED, SERIOUS, DISCONTINUATION or FATAL.

House default: `standard_rows`.

The answer fixes the rows of the adverse event summary (overview) table and their order.
Every row counts subjects with at least one treatment-emergent event of its kind.

### Where it is stated

- SAP: adverse event section, the sentence or list that describes the overview table.
- SAP table shells: the row labels of the summary or overview table.
- Protocol: statistical section, in general words.

### Words to look for

- `standard_rows`: exactly these five rows in this order: any event, related events, serious
  events, events leading to discontinuation of study treatment, fatal events.
- `stated_rows`: another selection or another order of those five. The slot `rows` lists
  the codes in the stated order, out of ANY, RELATED, SERIOUS, DISCONTINUATION and FATAL.

### Traps

- Only these five kinds can be rows. Severe events, serious related events, events of
  special interest or events leading to dose reduction cannot be expressed; report them with
  the answer.
- "Leading to discontinuation" means that the action taken with study treatment was
  withdrawal of the drug, not that the subject left the study.
- "Fatal" is an event that resulted in death, not the number of deaths from any cause.
- The same five rows in another order are `stated_rows`, not `standard_rows`.
- Silent documents: use the house default `standard_rows` and cite the house standard.
