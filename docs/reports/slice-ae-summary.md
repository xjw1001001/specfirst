# The slice "adverse event summary first": first scores on dev kits, and the pilot (report)

Date: 2026-11-19. Branch: `track/read`. ADR-005, decision 1, last
paragraph: "After read-2a comes a report ... with the first scores of the
slice on dev kits and the report on the pilot of decision 5. It is not a
delivery." Node N3 applies before any of it is shown outside (PLAN.md
section 13.1). Scope, chosen by the owner in the base session on
2026-11-19: four dev kits, and at most USD 10 of model use computed from
the tokens. Choices where PLAN.md, ADR-005 and ADR-010 are silent:
docs/decisions/ADR-016.md.

## Result

- 26 runs through the harness of read-2a: on each of four dev kits, the
  three arms of ADR-005, decision 3 (S, R, C) at both stages (T and C),
  and on the pilot arms S and R at stage T. Nine runs of arm R (Opus 5.5
  through `claude -p`, CLI 2.1.327, condition `notes`). Every run passed:
  within budget, valid output files, the task folder holds only what a
  reader may see, the canary scan clean, no tool rewritten.
- Model use: USD 4.0458 computed from the tokens for the nine runs of
  arm R (USD 3.4778 for the eight on dev kits, 0.5680 for the pilot), 162
  turns. No run came near its budget (ADR-010, decision 8). Arms S and C
  use no model.
- Stage T (the seven table decisions, on the ADaM of gold): arm R has
  every value right on every kit (28 of 28) and builds every gold cell,
  92 of 92 on the visible data and on the twin, the four tables whole.
  The same as the parser control. Arm S: 16 of 28 values, 52 of 92 cells
  on the visible data and 44 of 92 on the twin.
- Stage C (the chain, 21 or 22 decisions of four units per kit, on SDTM):
  arm R has 82 of 85 values right and builds 92 of 92 cells on each
  dataset, the four tables whole. Its three wrong values are one decision
  of the unit `mod-populations`, in three kits (not named: see "What arm R
  got wrong"); no cell of either dataset can show it (silent). It asked
  the one question gold asks for (kit 7, the ask
  demo) and no other. Arm C: 85 of 85 and 92 of 92. Arm S: 42 of 85
  values, 31 of 80 cells on the visible data and 19 of 80 on the twin,
  with 12 more cells on each dataset pending (ADR-014): they wait for
  `ae.related.values`, which has no house default.
- The pilot. The reader read the real SAP of CDISCPILOT01 and recorded
  one decision: `tfl.output.include` = `not_included`, citing the SAP's
  list of data displays. The SAP plans adverse event tables by treatment
  group (by organ class and term, and the serious events) and no summary
  table, though the templates of those two tables open with the counts of
  subjects with any event and with a serious event; the key is the
  summary of CDISC's ARS example, made later. So arm
  R built no table, and every one of the 27 cells of the key is missing.
  Every one is traced: with `tfl.output.include` = `included` 10 cells
  have the key's text, 5 more need `tfl.percent.format` as well, and 12
  are in rows that cannot be built (3 for ADAE.RELGR1, which the reference
  ADaM lacks; 9 for rows the catalog does not have). None is unexplained.
  Arm S is the table of read-1a, again: 10 of 15 cells of the rows both
  tables have.

These are first scores of a small slice. Stage T has seven decisions and
two alternatives for the rows of the table; as ADR-005 foresaw, its scores
are close to the control. The natural documents are mostly the statement
with a word changed (one rewrite per statement), and an eighth of the
decision paragraphs of these kits is the phrasing template. The scores
show that the loop works end to end on dev kits; they say little yet about
how hard reading is. The limits are below.

## What ran

### The kits

Four dev kits of a dev seed, written by `specfirst gen kits --seed-file`
at `1a94134` (generator `gen-3a.2`, `catalog@1`, `open-default@1`): kits 5,
6, 7 and 15 of the set, the first four that the split plan marks dev (ADR-016,
decision 1). The seed is a random text in a file outside every checkout;
it is not in the repository, and neither is its SHA-256. The kits, the
seed file and every run lie outside the repository (ADR-016, decision 4).

| Kit | ID | Tier of documents | Decisions | Separated on the twin | Decision paragraphs: model, template |
| --- | --- | --- | --- | --- | --- |
| kit 5 | `sf5plprv` | standard | 21 | 16 | 13, 1 |
| kit 6 | `sfm9lll3` | full | 21 | 14 | 26, 2 |
| kit 7 | `sfz57n2a` | the ask demo | 21 (1 asked) | 16 | 10, 2 |
| kit 15 | `sfpndwux` | standard | 22 | 17 | 9, 3 |

"Template": the store of model text has no rewrite of the statement, so
the paragraph is its phrasing template, marked `missing` (ADR-016,
decision 3): 8 of 66 decision paragraphs. A kit with such a paragraph does
not pass the gate gen-3a (ADR-009, decision 5); it is scored as it is.

### The runs

Each run: `specfirst run arm KIT --arm S|R|C --stage T|C --seed-file
<the kit's seed file>`, then `specfirst run score RUN --kit KIT` (run
under the heavy lock, one scorer process for all 24 runs, with the same
calls as `runs.score`). Task and run folders lie on drive C outside every
checkout; kits, seed files and logs in the WSL file system. The reader:
`claude -p` with the flags of ADR-010, decision 1, model
`claude-opus-5-5`, the deny rules of decision 4, and six more folders
denied through `SPECFIRST_DENY`: three folders of the desktop app's data,
the CLI's own folder of data, the scratch folder of the executor's
session, and the folder of the seed files. Condition
`notes` only (ADR-016, decision 2). Budget per run of arm R: 100 turns, 45
minutes, USD 10 (ADR-010, decision 8). Before each run of arm R the driver
held the total so far, plus twice the dearest run (at least USD 1), to USD
10 (ADR-016, decision 7); it never stopped. The pilot run of arm R was
started by hand (`pilot.sh`, which holds no budget) after the same sum
was checked by hand: USD 3.4778 so far plus twice 0.6212 is 4.72.

The code: the runs were made on the working tree that became `d7bea75`
(`1a94134` with this part's changes to the harness and the scorer). One
file changed after a run: `score/pilot.py`, the fix of the pilot's score
(section "Found"), after the pilot run of arm R, whose score was then
computed again without running the reader again. For a generated kit the
task is the one `1a94134` builds, file for file (section "Checks").

## The four scores (ADR-005, decision 4)

Each score with its denominator: produced (outputs built, of the outputs
in gold); cells correct of the cells of the rows that gold and the
candidate both have, of all gold cells of the outputs produced, and of all
gold cells (an output not produced counts as wrong); whole output strict
(both axes and every cell equal) and lenient (every gold cell present and
equal). Pending cells (ADR-014) are in no denominator and are counted in
the last column. Summed over the four kits: the scores of a single dev
kit stay in the records outside the repository, because with the public
catalog and house templates the cell counts of one kit can narrow its
table decisions (ADR-016, decision 4; review, pass 2).

Stage T:

| Arm | Data | Produced | Cells, rows both have | Cells, outputs produced | Cells, all gold | Strict | Lenient | Pending cells |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S | visible | 4 of 4 | 52 of 92 | 52 of 92 | 52 of 92 | 0 of 4 | 0 of 4 | 0 |
| S | twin | 4 of 4 | 44 of 92 | 44 of 92 | 44 of 92 | 0 of 4 | 0 of 4 | 0 |
| R | visible | 4 of 4 | 92 of 92 | 92 of 92 | 92 of 92 | 4 of 4 | 4 of 4 | 0 |
| R | twin | 4 of 4 | 92 of 92 | 92 of 92 | 92 of 92 | 4 of 4 | 4 of 4 | 0 |
| C | visible | 4 of 4 | 92 of 92 | 92 of 92 | 92 of 92 | 4 of 4 | 4 of 4 | 0 |
| C | twin | 4 of 4 | 92 of 92 | 92 of 92 | 92 of 92 | 4 of 4 | 4 of 4 | 0 |

Stage C:

| Arm | Data | Produced | Cells, rows both have | Cells, outputs produced | Cells, all gold | Strict | Lenient | Pending cells |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S | visible | 4 of 4 | 31 of 80 | 31 of 80 | 31 of 80 | 0 of 4 | 0 of 4 | 12 |
| S | twin | 4 of 4 | 19 of 80 | 19 of 80 | 19 of 80 | 0 of 4 | 0 of 4 | 12 |
| R | visible | 4 of 4 | 92 of 92 | 92 of 92 | 92 of 92 | 4 of 4 | 4 of 4 | 0 |
| R | twin | 4 of 4 | 92 of 92 | 92 of 92 | 92 of 92 | 4 of 4 | 4 of 4 | 0 |
| C | visible | 4 of 4 | 92 of 92 | 92 of 92 | 92 of 92 | 4 of 4 | 4 of 4 | 0 |
| C | twin | 4 of 4 | 92 of 92 | 92 of 92 | 92 of 92 | 4 of 4 | 4 of 4 | 0 |

Read with it:

- In every run each output was built, and the candidate had the rows of
  gold wherever its axes were compared, so the three denominators of
  "cells correct" coincide. The pending cells of arm S are why its
  denominators at stage C are 80 and not 92: counted as wrong, arm S has
  31 of 92 and 19 of 92.
- Arm R and arm C build the same tables. Where they differ in a value
  (three times, below) no cell shows it.

## The reading score by class and by unit

Summed over the four kits. Value and status: right, of the decisions
scored on them. Quote: every quote stands in its document. Span: a quote
stands inside an anchor that gold cites. Class and unit are those of the
gold record.

Stage T, by class (the unit is `tfl-ae-summary` throughout, so the table
by unit is the line "all"):

| Class | Arm | Decisions | Value | Status | Quote | Span |
| --- | --- | --- | --- | --- | --- | --- |
| document_rule | S | 15 | 3 of 15 | 0 of 15 | 15 of 15 | 0 of 15 |
| document_rule | R | 15 | 15 of 15 | 15 of 15 | 15 of 15 | 15 of 15 |
| document_rule | C | 15 | 15 of 15 | 15 of 15 | 15 of 15 | 15 of 15 |
| house_default | S | 13 | 13 of 13 | 13 of 13 | 13 of 13 | 13 of 13 |
| house_default | R | 13 | 13 of 13 | 13 of 13 | 13 of 13 | 13 of 13 |
| house_default | C | 13 | 13 of 13 | 13 of 13 | 13 of 13 | 13 of 13 |
| all | S | 28 | 16 of 28 | 13 of 28 | 28 of 28 | 13 of 28 |
| all | R | 28 | 28 of 28 | 28 of 28 | 28 of 28 | 28 of 28 |
| all | C | 28 | 28 of 28 | 28 of 28 | 28 of 28 | 28 of 28 |

Stage C, by class:

| Class | Arm | Decisions | Value | Status | Quote | Span |
| --- | --- | --- | --- | --- | --- | --- |
| document_rule | S | 50 | 8 of 50 | 0 of 50 | 46 of 50 | 0 of 50 |
| document_rule | R | 50 | 50 of 50 | 50 of 50 | 50 of 50 | 50 of 50 |
| document_rule | C | 50 | 50 of 50 | 50 of 50 | 50 of 50 | 50 of 50 |
| house_default | S | 34 | 34 of 34 | 34 of 34 | 34 of 34 | 34 of 34 |
| house_default | R | 34 | 31 of 34 | 31 of 34 | 34 of 34 | 31 of 34 |
| house_default | C | 34 | 34 of 34 | 34 of 34 | 34 of 34 | 34 of 34 |
| study_input | S | 1 | 0 of 1 | 0 of 1 | - | - |
| study_input | R | 1 | 1 of 1 | 1 of 1 | - | - |
| study_input | C | 1 | 1 of 1 | 1 of 1 | - | - |
| all | S | 85 | 42 of 85 | 34 of 85 | 80 of 84 | 34 of 84 |
| all | R | 85 | 82 of 85 | 82 of 85 | 84 of 84 | 81 of 84 |
| all | C | 85 | 85 of 85 | 85 of 85 | 84 of 84 | 84 of 84 |

Stage C, by unit:

| Unit | Arm | Decisions | Value | Status | Quote | Span |
| --- | --- | --- | --- | --- | --- | --- |
| mod-ae-emergence | S | 16 | 4 of 16 | 2 of 16 | 12 of 15 | 2 of 15 |
| mod-ae-emergence | R | 16 | 16 of 16 | 16 of 16 | 15 of 15 | 15 of 15 |
| mod-ae-emergence | C | 16 | 16 of 16 | 16 of 16 | 15 of 15 | 15 of 15 |
| mod-populations | S | 17 | 10 of 17 | 9 of 17 | 16 of 17 | 9 of 17 |
| mod-populations | R | 17 | 14 of 17 | 14 of 17 | 17 of 17 | 14 of 17 |
| mod-populations | C | 17 | 17 of 17 | 17 of 17 | 17 of 17 | 17 of 17 |
| mod-treatment | S | 24 | 12 of 24 | 10 of 24 | 24 of 24 | 10 of 24 |
| mod-treatment | R | 24 | 24 of 24 | 24 of 24 | 24 of 24 | 24 of 24 |
| mod-treatment | C | 24 | 24 of 24 | 24 of 24 | 24 of 24 | 24 of 24 |
| tfl-ae-summary | S | 28 | 16 of 28 | 13 of 28 | 28 of 28 | 13 of 28 |
| tfl-ae-summary | R | 28 | 28 of 28 | 28 of 28 | 28 of 28 | 28 of 28 |
| tfl-ae-summary | C | 28 | 28 of 28 | 28 of 28 | 28 of 28 | 28 of 28 |

Questions (section 9.1): arm R asked once, in kit 7 at stage C, about the
one decision gold marks asked there (`ae.related.values`), and the oracle
answered: precision 1.00, recall 1.00. It asked nothing elsewhere, and
nothing was to be asked elsewhere ("none to judge"). Arm S asks nothing:
recall 0.00 in kit 7. Unmapped: no run listed a paragraph and no kit has
one to list ("none to judge" in every run).

What arm R got wrong, in every run. A decision of a dev kit is not named
here: beside the counts by class, its ID would give its gold value
(ADR-016, decision 4; review, finding 1). The run records outside the
repository name it.

| Kit | Stage | Values wrong | Status and span wrong | Shown by a cell? |
| --- | --- | --- | --- | --- |
| kits 5, 6, 7, 15 | T | none | none | - |
| kit 5 | C | 1, of `mod-populations` | the same decision | no: silent on both datasets |
| kit 6 | C | none | none | - |
| kit 7 | C | 1, of `mod-populations` | the same decision | no: silent on both datasets |
| kit 15 | C | 1, of `mod-populations` | the same decision | no: silent on both datasets |

The one error, three times, is one decision: the reader cited a design
paragraph of the natural protocol, which describes the study and states
no convention, as stating the decision, and recorded another alternative
than gold's. No cell of either dataset shows it: alone, on gold, the
reader's value changes no cell and no axis (`silent`), though the twin
separates other values of the decision. It is a reading error that this
table cannot show, compared by value only (PLAN.md section 9.3). That the
reading notes should say "a design paragraph states no decision" is for
the training loop of M2 to propose and the dev kits to accept, not for
this report.

## R against S, and R against C

Summed over the four kits:

| Stage | Measure | S | R | C | R - S | C - R |
| --- | --- | --- | --- | --- | --- | --- |
| T | decision values right | 16 of 28 | 28 of 28 | 28 of 28 | +12 | +0 |
| T | cells correct, visible (all gold cells) | 52 of 92 | 92 of 92 | 92 of 92 | +40 | +0 |
| T | cells correct, twin (all gold cells) | 44 of 92 | 92 of 92 | 92 of 92 | +48 | +0 |
| C | decision values right | 42 of 85 | 82 of 85 | 85 of 85 | +40 | +3 |
| C | cells correct, visible (all gold cells) | 31 of 80 (12 pending) | 92 of 92 | 92 of 92 | +61 | +0 |
| C | cells correct, twin (all gold cells) | 19 of 80 (12 pending) | 92 of 92 | 92 of 92 | +73 | +0 |

By class (values right, stage C): `document_rule` S 8, R 50, C 50 of 50;
`house_default` S 34, R 31, C 34 of 34; `study_input` S 0, R 1, C 1 of 1.
By unit (stage C): `mod-ae-emergence` S 4, R 16, C 16 of 16;
`mod-populations` S 10, R 14, C 17 of 17; `mod-treatment` S 12, R 24, C 24
of 24; `tfl-ae-summary` S 16, R 28, C 28 of 28 (the same 28 at stage T).

- R against S: the reader gains every decision the documents state that
  differs from the house (42 at stage C, 12 at stage T) and the one it
  asks, and loses three that the house had right. On the twin that is 48
  and 73 more cells.
- R against C: the control reads the standard-form documents with the
  parser and asks what they leave open. The reader, on the natural form,
  matches it on every built cell and on every stated decision, and
  differs only in reading a default as stated (the class
  `house_default`, unit `mod-populations`).
- Arm S builds the chain since ADR-014. Before it, "R against S" at stage
  C compared with nothing (ADR-008, first consequence).

## Pending cells (ADR-014), counted apart

Summed over the four kits, as above.

| Stage | Arm | Data | Pending cells, four kits | Waiting for |
| --- | --- | --- | --- | --- |
| C | S | visible | 12 | `ae.related.values` (mod-ae-emergence) |
| C | S | twin | 12 | `ae.related.values` (mod-ae-emergence) |

Only arm S has pending cells: `ae.related.values` has no house default,
and arm S states nothing. Arm R stated or asked the decision in every
kit, and the oracle answered its one question, so nothing of arm R
waits. No output waited as a whole. At stage T the ADaM is given, and
nothing waits.

## Cost per run

Arm R, from each run's record (`run.json`; tokens by kind; USD computed
from the tokens with the prices of ADR-010, decision 7, beside the CLI's
own figure). Every token was Opus 5.5 (`claude-opus-5-5`); on the owner's
subscription no money is charged per token.

| Kit | Stage | Turns | Wall s | API s | Input | Output | Cache write | Cache read | USD computed | USD (CLI) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| kit 5 | T | 14 | 33.3 | 26.2 | 16 | 3,104 | 25,479 | 140,412 | 0.2941 | 0.2941 |
| kit 6 | T | 13 | 28.1 | 21.6 | 16 | 2,621 | 24,262 | 135,913 | 0.2738 | 0.2738 |
| kit 7 | T | 15 | 33.8 | 26.9 | 16 | 3,194 | 27,653 | 144,787 | 0.3141 | 0.3141 |
| kit 15 | T | 15 | 37.0 | 27.6 | 16 | 3,245 | 27,356 | 144,820 | 0.3128 | 0.3128 |
| kit 5 | C | 25 | 73.1 | 65.1 | 24 | 8,026 | 47,742 | 393,092 | 0.6212 | 0.6212 |
| kit 6 | C | 21 | 59.5 | 50.3 | 18 | 6,570 | 46,008 | 249,637 | 0.5495 | 0.5495 |
| kit 7 | C | 23 | 63.5 | 51.7 | 22 | 6,551 | 45,351 | 336,859 | 0.5613 | 0.5613 |
| kit 15 | C | 20 | 65.5 | 56.7 | 18 | 7,296 | 44,859 | 231,281 | 0.5511 | 0.5511 |
| eight runs | | 146 | 393.8 | 326.1 | 146 | 40,607 | 288,710 | 1,776,801 | 3.4778 | 3.4778 |
| pilot | T | 16 | 42.8 | 35.4 | 20 | 3,135 | 54,953 | 328,163 | 0.5680 | 0.5680 |
| nine runs | | 162 | 436.6 | 361.5 | 166 | 43,742 | 343,663 | 2,104,964 | 4.0458 | 4.0458 |

A run of stage T costs about USD 0.30 (13 to 15 turns, half a minute); a
run of stage C about USD 0.57 (20 to 25 turns, about a minute). Wall time
is the reader's; the harness takes 8 to 21 seconds more per run (the task
built on drive C, the canary scan). Arms S and C: 0 turns, 0 tokens, at
most 1.8 seconds each. The total, USD 4.05, is within the owner's USD
10. Every cache write of the CLI was a one-hour write (USD 8 per million
tokens, twice the five-minute price): USD 2.75 of the 4.05, about two
thirds. With five-minute writes the same tokens would compute to USD 3.01;
worth knowing for the budget of read-3.

## The pilot (ADR-005, decision 5)

Stage T on the reference ADaM of CDISCPILOT01, held against the results
CDISC's ARS example embeds for its adverse event summary (output
Out14-3-1-1), as the kit's layout places them. Arm R read the real SAP:
the PDF of the pilot kit, as text with page and paragraph anchors
(`specfirst run pilot`, ADR-016, decisions 5 and 6). Report only; nothing
was tuned on the pilot. The run, its transcript and the folder stay
outside the repository (rule 4).

### Arm R

The reader read TASK.md, the two skills, the SAP, the house standard and
the catalog entry of `tfl.output.include`, ran `bin/check`, and wrote:

| Decision | Value | Status | Cites (SAP, page/paragraph) |
| --- | --- | --- | --- |
| `tfl.output.include` | `not_included` | stated | `18/p9` (the heading of the table of contents of the data displays), `19/p8` (the title of the table of treatment-emergent adverse events by treatment group), `16/p13` (no formal summarization of adverse events leading to discontinuation or withdrawal) |

It wrote no record of the other six table decisions: the catalog says of
`not_included` "No other decision of the table family applies then", and
TASK.md asks for no record of a question that does not apply. It listed
three paragraphs as unmapped (pooling of small sites, multiplicity, the
sort order of a medication table); they lie outside the units of the
slice, and the pilot has no gold to score them against. It asked nothing.

Is the reading right? The SAP's list of data displays (pages 18 and 19)
names the incidence of treatment-emergent adverse events and of serious
adverse events by treatment group, as tables by organ class and term, and
no summary table of the kind `tfl-ae-summary` builds; the CSR's adverse
event tables are 14-5.01 and 14-5.02 (ADR-005, "Context"). The templates
those two tables follow (templates 13 and 14, pages 32 and 33) open with a
row of the subjects with at least one event, any and serious, by
treatment group: two rows of the summary are planned, inside other
tables. The reader read those templates (its transcript shows it) and
recorded `not_included` for the summary as a display, which is a
defensible reading. So the answer the key implies (the table is planned)
is not what the SAP says. The key is a display CDISC built for the ARS
example; nothing in the SAP plans it as a table. On this output the pilot
cannot score a reader of the SAP against the key without first giving it
the output as planned (below, "For the owner").

### The trace of every cell

`specfirst score pilot --run $SPECFIRST_RUNS/R-task-28efd3ea363d` (output
in "Commands"). Arm R built no table: produced 0 of 1, cells correct 0 of
0 of the rows both tables have, 0 of 0 of the outputs produced, 0 of 27
of all gold cells, strict and lenient 0 of 1. The trace sets
`tfl.output.include` = `included` first, which builds arm S's table (the
reader set no other decision), and explains each cell against it:

| Cells of the key | How many | Explained by |
| --- | --- | --- |
| the column headers, any adverse event, 2 of serious, 2 of fatal | 10 | `tfl.output.include` = `included` alone |
| the counts of zero (serious, fatal, discontinuation: 1, 1, 3) | 5 | `tfl.output.include` = `included` together with `tfl.percent.format` = `one_decimal_always` (the house default shows a count of zero without a percent; the example shows "0 (  0.0)") |
| related adverse event | 3 | not built: the reference ADaM has no ADAE.RELGR1, which the house standard writes by `ae.related.values`, a module decision that stage T does not ask |
| related serious, related leading to death, leading to dose modification | 9 | not built: the catalog has no such row (`tfl.ae.summary.rows`; ADR-005, "For the owner", item 3) |
| unexplained | 0 | |

The axes, with `tfl.output.include` = `included`: the columns are the
key's with `tfl.columns.total` = `none` (the house default has a total
column, the example none); the 4 rows the key has and the build lacks are
those of the last two lines above. Of the 9 variables the house template
reads, 8 are in the reference ADaM under the same name; ADAE.RELGR1 is
not.

### Arm S

The same table as read-1a (docs/reports/read-1a.md, "The pilot"), now run
through the harness (`specfirst run pilot --arm S`): produced 1 of 1;
cells correct 10 of 15 of the rows both tables have, 10 of 27 of the
outputs produced and of all gold cells; strict and lenient 0 of 1. The 5
cells that differ are the counts of zero, each explained by
`tfl.percent.format` = `one_decimal_always`; 12 cells are in rows arm S
does not build (3 for ADAE.RELGR1, 9 the catalog lacks); the columns are
explained by `tfl.columns.total` = `none`; 0 unexplained.

### Pilot table

| Arm | Records | Produced | Cells, rows both have | Cells, all gold | Explained by one or two table decisions | Rows not buildable | Unexplained |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S | none (every house default) | 1 of 1 | 10 of 15 | 10 of 27 | 5 (`tfl.percent.format`) | 12 | 0 |
| R | 1 (`tfl.output.include` = `not_included`) | 0 of 1 | 0 of 0 | 0 of 27 | 15 (10 by `tfl.output.include`, 5 by it and `tfl.percent.format`) | 12 | 0 |

## Checks

- Every run passed its own checks (the line `RUN ...: PASS`): 24 runs on
  the dev kits and 2 on the pilot; canaries per run 16,756 to 44,665 on
  the dev kits (gold and twin of the kit, the store, the seed, the
  planted canaries of the private files) and 2,918 (arm S) and 2,913 (arm
  R) on the pilot (of arm R's: 1,913 from the example, 90 from the key, the
  rest from the store, the manifest and the two planted); no hit in any
  run.
- Permission denials: 12 in the nine runs of arm R, every one a Bash
  command other than the two tools (a listing of the task folder, `cat`
  of the skills or of catalog entries, a `mkdir`, and once `bin/check`
  called by its absolute path, which the rule `Bash(bin/check *)` does not
  cover). None names a path outside the task folder. No tool of `bin/`
  changed in any run.
- The kept dry run of read-2a still checks against the task built now
  (the task of a generated kit is unchanged by this part): see
  "Commands".
- Tests: `tests/unit/test_harness_pilot.py` (the pilot task from a toy
  folder: the anchors, TASK.md of a real study, the documents a task may
  cite, the stub reader on it, each check with a planted defect: the key
  in the task, a citation of the protocol, an anchor of an empty page, a
  changed kit text, a reader that reads the key) and
  `tests/score/test_score_pilot.py` P2 to P4 (evidence: arm R with two
  table decisions; the pilot folder from the cache; a reader that leaves
  the output out, the record on which the code before the fix of
  `score.pilot.run` stopped, as the log of the pilot run shows). P2 to P4
  carry the marker `evidence` (they need the fetch cache): `make test` and
  CI leave them out, and the gate read-1a runs them; they ran on the
  working tree (above) and, in the review, on the commit. Two more unit
  tests, from the review: `--folder` never deletes a folder that is not a
  pilot folder, and the pilot report refuses a run that is not of arm S
  or R on the pilot (findings 4 and 5).

## Found during the part

- **The pilot report assumed a candidate builds the output.** The score
  of arm S always does. Arm R left the output out, the build had no ARS
  file, and `score.pilot.run` stopped at `ars.index(None)` ("a reporting
  event is a JSON object") after the run itself had passed. Now a
  candidate without the output is traced through the value of
  `tfl.output.include` that builds it, and every cell is explained
  against that build, one more decision at a time. Case P4 of
  `tests/score/test_score_pilot.py` holds it. The run was not made again:
  only its score (lesson 69).
- **The real SAP does not plan the output of the slice.** See the pilot.
  ADR-005, decision 5 takes the key from the ARS example and the reading
  from the SAP; for this output the two do not meet.
- **One reading error recurs.** A design paragraph of the natural
  protocol is read as stating one decision of `mod-populations`, in three
  of the four kits. No cell of these kits shows it.
- **A report on dev kits must not pair a decision with its class.** The
  first version of this report named the decision the reader got wrong
  together with its gold class, which with the house standard gives the
  gold value (review, finding 1). The decisions of dev kits are now given
  by unit and as counts (ADR-016, decision 4).

## The review

Pass 1 (docs/reports/slice-ae-summary.review.md) found every number it
checked to hold (the tables from the records, the cost to the token, seven
dev runs and both pilot runs scored again byte for byte, the nine tasks
rebuilt with the same IDs) and did not sign, for finding 1. What changed:

1. Blocking: the report and the state of the track named the decision
   arm R got wrong in three dev kits with its gold class, which gives its
   value. Now the decision is given by unit and as counts, the score block
   of kit 7 withholds its ID, its class, the reader's anchor and the
   unseparated decisions named "right", and ADR-016, decision 4 says so.
2. The pilot's canary count: 2,918 for arm S, 2,913 for arm R.
3. H10: the list and map slots the readers wrote are counted, not only one.
4. `run pilot --folder` deleted any folder outside a checkout; now it
   replaces only a missing or empty folder or a pilot folder (a unit test
   with a planted folder of other files).
5. `score pilot --run` took any run and printed its records; now it
   refuses a run that is not of arm S or R on the pilot, before reading
   its records, and exits non-zero (a unit test with a dev run and a run
   of arm C).
6. The pilot section says that the SAP's templates 13 and 14 open with the
   counts of subjects with any and with a serious event.
7. The state of the track lists the part under "In progress" until the
   merge, and says what is not committed exactly.
8. Smaller statements: whose the nine runs are; the hand check of the
   budget before the pilot run; the one-hour cache writes; what `anchored`
   drops from the SAP text; that `make test` and CI leave P2 to P4 out.

Pass 2 found the fixes in the files and did not sign, for one more
finding: the two earlier commits of the report, not pushed, still held
the pairing of finding 1, and a push of the branch would publish them.
Those commits were rebuilt as one, on the code commit, with the tree of
the fixed files; nothing had been pushed. Its finding P2-2 (not
blocking): the cell counts of a single dev kit, beside its number of
arms and with the public templates, can narrow its table decisions. The
four scores and the pending cells are now summed over the four kits, and
the number of arms per kit is not given (ADR-016, decision 4).

Pass 3 confirmed both (the rebuilt history holds none of the withheld
text, and the summed rows equal the rows pass 1 checked against the
records) and signed.

Questions Q2 and Q3 of the review are the owner's and went to the base
session: whether first scores on kits with template paragraphs stand (Q2),
and whether more runs are wanted within the USD 10 (Q3). Q1 does not need
the owner: the report now withholds the pairing (finding 1).

## Limits

- **M1 isolation** (PLAN.md section 11.2, to be stated in every M1
  report). The reader runs as the owner's Windows user under deny rules,
  not in a container where gold is not mounted (M2). The probe of read-2a
  shows that the rules hold for the three kinds of path the harness uses
  (the WSL share, drive D, drive C); it does not show that the CLI keeps a
  file tool inside the working directory, so a path no rule names may be
  readable. This part added six folders to the rules (above); kits, seed
  files and the pilot folder lie in the WSL file system, which every run
  denies. The canary scan sees a read only when its text reaches the
  transcript or the workspace as it stands: an encoded copy is not seen.
  Parquet files are not scanned. No `CLAUDE.md` lies on the path of the
  task folders or in the user's `.claude` (checked by name).
- **One rewrite per statement** (gen-3a review, finding D9). 38 of the 61
  accepted paragraphs of the store are within 0.9 of their statement, two
  equal to it: the natural form measures little robustness to wording.
  And 8 of the 66 decision paragraphs of these kits are the phrasing
  template (ADR-016, decision 3), nearer still to the standard form.
- **Open findings H10 to H12 of the read-2a review**
  (docs/reports/read-2a.review.md):
  - H10 (open): a list slot filled with texts the task holds can still
    take most canary pieces of a twin Dataset-JSON row out of the scan.
    The readers wrote list and map slots of three entries here, at most
    four items each and none longer than 42 characters (counted by the
    review), nothing of the shape of a twin row; no run had a hit, and a
    scan with that gap closed is owed before read-3 relies on it.
  - H11 (settled at the merge of read-2a): the records the merge owed
    (the state of the track, the report's result, lessons 64 and 65) are
    on `main`.
  - H12 (open): a record's `reader.deny` does not list the rule on `bin/`
    (Edit and Write only), and `runs.tool_writes` counts a write of
    `bin/` even when the CLI denied it. No run here wrote `bin/`.
- **Small numbers.** Four kits, one run of the reader per kit and stage,
  one condition (`notes`), one model. Stage T has seven decisions and two
  alternatives for the rows (ADR-005, "Consequences"). The scores of the
  reader would move with another run; nothing here measures that.
- **Silent decisions.** A decision the twin cannot separate is compared
  by value only: 4 to 7 per kit at stage C and 0 or 1 at stage T
  (`unseparated` in gold), and the reader's one error is of that kind for
  its value.
- **The pilot** is one study, and its SAP does not plan the output the
  key holds. It has no gold decision records before std-2, so it has no
  reading score; the reader's records are listed, not scored.
- **The cost** is computed from the tokens at API prices; the runs were
  made on the owner's subscription.
- **The kits would not pass the gate gen-3a**: a paragraph marked
  `missing` fails it (ADR-009, decision 5), and these kits have 8. The
  scorer's build of the gold decisions gives the files of each kit (the
  scorer refuses a kit otherwise, and none was refused).

## For the owner

Nothing blocks. One choice, if the owner wants the pilot to say more
about reading: a second pilot task in which the output is given as
planned (`tfl.output.include` fixed at `included`, as stage T fixes the
module decisions at gold), so that the reader decides the other six table
decisions from the SAP. One more run of arm R, about USD 0.6. This report
does not make it: the owner's scope is four dev kits and USD 10, and the
nine runs of arm R are this part's reading of it (ADR-016, decisions 2 and
5; the brief of the base session named them). USD 5.95 of the 10 is left.

## Commands and their output (rule R8)

Paths of the machine are shown as they are in WSL; `<dev seed>` and
`<kit seed file>` stand for files outside every checkout. In the output
of a score on a dev kit every value of a decision and every anchor gold
cites is shown as `<withheld>`, and so are a wrong decision's ID, its
class and the anchor the reader cited for it (ADR-016, decision 4); the
files outside the repository hold them.

The kits:

```text
$ specfirst gen kits --seed-file <dev seed> --first 5 --count 3 --out /root/scratch-slice/kits
kit 5 of the set: sf5plprv, dev, 126 files; 16 of 21 decisions separated on the twin
kit 6 of the set: sfm9lll3, dev, 126 files; 14 of 21 decisions separated on the twin
kit 7 of the set: sfz57n2a, dev, 126 files; 16 of 21 decisions separated on the twin
exit 0
$ specfirst gen kits --seed-file <dev seed> --first 15 --count 1 --out /root/scratch-slice/kits
kit 15 of the set: sfpndwux, dev, 127 files; 17 of 22 decisions separated on the twin
exit 0
```

The three arms on kit 7 (the ask demo), stage C:

```text
$ specfirst run arm /root/scratch-slice/kits/kit-007 --arm S --stage C --seed-file <kit seed file>
run S-task-47de94f74e05: arm S, stage C, condition notes, kit sfz57n2a (dev), task task-47de94f74e05 (22 decisions)
  reader: none
  cost: 0 turns, 0.0 s wall, 0.0 s API, tokens in 0 out 0 cache write 0 cache read 0, USD 0.0000 (CLI: 0)
  budget: {'turns': 0, 'seconds': 600, 'usd': 0.0}: within
  outputs: decisions.jsonl 0 lines, questions.jsonl 0 lines, unmapped.jsonl 0 lines
  asks: 0, answered 0
  output files: valid
  task folder: holds only what a reader may see
  canary scan: 39511 canaries from 80 files; clean
  RUN S-task-47de94f74e05: PASS
(exit 0, 12 s)

$ specfirst run arm /root/scratch-slice/kits/kit-007 --arm C --stage C --seed-file <kit seed file>
run C-task-47de94f74e05: arm C, stage C, condition notes, kit sfz57n2a (dev), task task-47de94f74e05 (22 decisions)
  reader: none
  cost: 0 turns, 1.0 s wall, 0.0 s API, tokens in 0 out 0 cache write 0 cache read 0, USD 0.0000 (CLI: 0)
  budget: {'turns': 0, 'seconds': 600, 'usd': 0.0}: within
  outputs: decisions.jsonl 21 lines, questions.jsonl 1 lines, unmapped.jsonl 0 lines
  asks: 1, answered 1; ae.related.values (mod-ae-emergence)
  output files: valid
  task folder: holds only what a reader may see
  canary scan: 39498 canaries from 78 files; clean
  RUN C-task-47de94f74e05: PASS
(exit 0, 18 s)

$ specfirst run arm /root/scratch-slice/kits/kit-007 --arm R --stage C --seed-file <kit seed file>
run R-task-47de94f74e05: arm R, stage C, condition notes, kit sfz57n2a (dev), task task-47de94f74e05 (22 decisions)
  reader: claude-code, model claude-opus-5-5, used ['claude-opus-5-5'], CLI 2.1.327
  cost: 23 turns, 63.5 s wall, 51.7 s API, tokens in 22 out 6551 cache write 45351 cache read 336859, USD 0.5613 (CLI: 0.5612878000000001)
  budget: {'turns': 100, 'seconds': 2700, 'usd': 10.0}: within
  outputs: decisions.jsonl 21 lines, questions.jsonl 1 lines, unmapped.jsonl 0 lines
  asks: 1, answered 1; ae.related.values (mod-ae-emergence)
  output files: valid
  task folder: holds only what a reader may see
  canary scan: 39508 canaries from 80 files; clean
  permission denials: 1
  RUN R-task-47de94f74e05: PASS
(exit 0, 73 s)

$ specfirst run score $SPECFIRST_RUNS/R-task-47de94f74e05 --kit /root/scratch-slice/kits/kit-007
case sfz57n2a, arm R, stage C
reading score: 21 gold decisions of the units mod-treatment, mod-populations, mod-ae-emergence, tfl-ae-summary
  by class:                     decisions  value       status      quote       span        
    document_rule                       9  9 of 9      9 of 9      9 of 9      9 of 9      
    house_default                      11  10 of 11    10 of 11    11 of 11    10 of 11    
    study_input                         1  1 of 1      1 of 1      -           -           
  by unit:                      decisions  value       status      quote       span        
    mod-ae-emergence                    4  4 of 4      4 of 4      3 of 3      3 of 3      
    mod-populations                     4  3 of 4      3 of 4      4 of 4      3 of 4      
    mod-treatment                       6  6 of 6      6 of 6      6 of 6      6 of 6      
    tfl-ae-summary                      7  7 of 7      7 of 7      7 of 7      7 of 7      
  (value and status: right, of the decisions scored on it; quote: every quote stands in its document; span: a quote stands inside an anchor that gold cites)
  asks: 1 given, 1 in gold (decisions with the status asked), 1 of them right; precision 1.00, recall 1.00
  unmapped: 0 given, 0 in gold (what the catalog lacks), 0 of them right; precision none to judge, recall none to judge
  decisions a reviewer would have to change: 1
    <decision withheld> (mod-populations), <class withheld>: gold <withheld>; the candidate (given) has <withheld>
    <decision withheld> (mod-populations): wrong in status, span: cites <withheld>; gold cites <withheld>
  unseparated in gold, compared by value only: 4 <decisions withheld> (right, right, right, right)
build score:
  visible: valid: yes
  visible: produced: 1 of 1 outputs in gold
  visible: cells correct: 20 of 20 gold cells of the rows that gold and the candidate both have
  visible: cells correct: 20 of 20 gold cells of the outputs produced
  visible: cells correct: 20 of 20 gold cells (an output that was not produced counts as wrong)
  visible: whole output, strict: 1 of 1 outputs in gold (both axes equal and every cell equal)
  visible: whole output, lenient: 1 of 1 outputs in gold (every gold cell present and equal)
  twin: valid: yes
  twin: produced: 1 of 1 outputs in gold
  twin: cells correct: 20 of 20 gold cells of the rows that gold and the candidate both have
  twin: cells correct: 20 of 20 gold cells of the outputs produced
  twin: cells correct: 20 of 20 gold cells (an output that was not produced counts as wrong)
  twin: whole output, strict: 1 of 1 outputs in gold (both axes equal and every cell equal)
  twin: whole output, lenient: 1 of 1 outputs in gold (every gold cell present and equal)
wrong by value, and these data cannot show it (alone, on gold, it changes no cell and no axis of any dataset): <decision withheld> (mod-populations)
case sfz57n2a, arm R: not every score is 100%
```

Every run, as the driver logged it (`specfirst run arm`, then the record;
a script outside the repository that runs the commands above and, before
a run of arm R, holds the budget of ADR-016, decision 7). A first call of
the driver got the kit numbers as `5,6,7,15` (PowerShell had read `005`
as a number), found no seed file `kit-5.seed` and stopped before any run;
its log was replaced by the call below.

```text
$ drive.py 005,006,007,015 T,C S,C        (SKIP_SCORE=1)
005-T-S: S-task-3691e773436b PASS USD 0.0000 turns 0 wall 0.0 s; total of arm R USD 0.0000
005-T-C: C-task-3691e773436b PASS USD 0.0000 turns 0 wall 1.2 s; total of arm R USD 0.0000
005-C-S: S-task-4f8c812ea057 PASS USD 0.0000 turns 0 wall 0.1 s; total of arm R USD 0.0000
005-C-C: C-task-4f8c812ea057 PASS USD 0.0000 turns 0 wall 0.8 s; total of arm R USD 0.0000
006-T-S: S-task-16b4b5bbd5d5 PASS USD 0.0000 turns 0 wall 0.0 s; total of arm R USD 0.0000
006-T-C: C-task-16b4b5bbd5d5 PASS USD 0.0000 turns 0 wall 0.8 s; total of arm R USD 0.0000
006-C-S: S-task-8c15d8fceefe PASS USD 0.0000 turns 0 wall 0.0 s; total of arm R USD 0.0000
006-C-C: C-task-8c15d8fceefe PASS USD 0.0000 turns 0 wall 1.8 s; total of arm R USD 0.0000
007-T-S: S-task-bc033bce59a9 PASS USD 0.0000 turns 0 wall 0.1 s; total of arm R USD 0.0000
007-T-C: C-task-bc033bce59a9 PASS USD 0.0000 turns 0 wall 0.9 s; total of arm R USD 0.0000
007-C-S: S-task-47de94f74e05 PASS USD 0.0000 turns 0 wall 0.0 s; total of arm R USD 0.0000
007-C-C: C-task-47de94f74e05 PASS USD 0.0000 turns 0 wall 1.0 s; total of arm R USD 0.0000
015-T-S: S-task-c887770e798d PASS USD 0.0000 turns 0 wall 0.1 s; total of arm R USD 0.0000
015-T-C: C-task-c887770e798d PASS USD 0.0000 turns 0 wall 1.2 s; total of arm R USD 0.0000
015-C-S: S-task-2f2ce1b181bf PASS USD 0.0000 turns 0 wall 0.1 s; total of arm R USD 0.0000
015-C-C: C-task-2f2ce1b181bf PASS USD 0.0000 turns 0 wall 0.9 s; total of arm R USD 0.0000
DRIVE-DONE
exit 0
$ drive.py 005,006,007,015 T,C R          (SKIP_SCORE=1)
005-T-R: R-task-3691e773436b PASS USD 0.2941 turns 14 wall 33.3 s; total of arm R USD 0.2941
005-C-R: R-task-4f8c812ea057 PASS USD 0.6212 turns 25 wall 73.1 s; total of arm R USD 0.9152
006-T-R: R-task-16b4b5bbd5d5 PASS USD 0.2738 turns 13 wall 28.1 s; total of arm R USD 1.1890
006-C-R: R-task-8c15d8fceefe PASS USD 0.5495 turns 21 wall 59.5 s; total of arm R USD 1.7385
007-T-R: R-task-bc033bce59a9 PASS USD 0.3141 turns 15 wall 33.8 s; total of arm R USD 2.0526
007-C-R: R-task-47de94f74e05 PASS USD 0.5613 turns 23 wall 63.5 s; total of arm R USD 2.6139
015-T-R: R-task-c887770e798d PASS USD 0.3128 turns 15 wall 37.0 s; total of arm R USD 2.9266
015-C-R: R-task-2f2ce1b181bf PASS USD 0.5511 turns 20 wall 65.5 s; total of arm R USD 3.4778
DRIVE-DONE
exit 0
$ aggregate.py                  (under the heavy lock: the 24 runs scored as `specfirst run score` scores them)
005-C-C: scored; values right 21 of 21
005-C-R: scored; values right 20 of 21
005-C-S: scored; values right 10 of 21
005-T-C: scored; values right 7 of 7
005-T-R: scored; values right 7 of 7
005-T-S: scored; values right 4 of 7
006-C-C: scored; values right 21 of 21
006-C-R: scored; values right 21 of 21
006-C-S: scored; values right 8 of 21
006-T-C: scored; values right 7 of 7
006-T-R: scored; values right 7 of 7
006-T-S: scored; values right 3 of 7
007-C-C: scored; values right 21 of 21
007-C-R: scored; values right 20 of 21
007-C-S: scored; values right 11 of 21
007-T-C: scored; values right 7 of 7
007-T-R: scored; values right 7 of 7
007-T-S: scored; values right 4 of 7
015-C-C: scored; values right 22 of 22
015-C-R: scored; values right 21 of 22
015-C-S: scored; values right 13 of 22
015-T-C: scored; values right 7 of 7
015-T-R: scored; values right 7 of 7
015-T-S: scored; values right 5 of 7
AGGREGATE-DONE
exit 0
```

The pilot, arm S and arm R:

```text
$ specfirst run pilot --arm S --folder /root/scratch-slice/pilot/cdiscpilot01 --score
pilot folder: /root/scratch-slice/pilot/cdiscpilot01
run S-task-28efd3ea363d: arm S, stage T, condition notes, kit cdiscpilot01 (pilot), task task-28efd3ea363d (7 decisions)
  reader: none
  cost: 0 turns, 0.1 s wall, 0.0 s API, tokens in 0 out 0 cache write 0 cache read 0, USD 0.0000 (CLI: 0)
  budget: {'turns': 0, 'seconds': 600, 'usd': 0.0}: within
  outputs: decisions.jsonl 0 lines, questions.jsonl 0 lines, unmapped.jsonl 0 lines
  asks: 0, answered 0
  output files: valid
  task folder: holds only what a reader may see
  canary scan: 2918 canaries from 17 files; clean
  RUN S-task-28efd3ea363d: PASS
pilot CDISCPILOT01, arm S (the house standard alone), stage T (table decisions on the reference ADaM); report only
key: the results CDISC's ARS example embeds for its adverse event summary (Out14-3-1-1), as the kit's layout places them
  row | column | key | arm S | state
  (column header) | Placebo | (N=86) | (N=86) | equal
  (column header) | Xanomeline Low Dose | (N=84) | (N=84) | equal
  (column header) | Xanomeline High Dose | (N=84) | (N=84) | equal
  Any adverse event | Placebo | 65 ( 75.6) | 65 ( 75.6) | equal
  Any adverse event | Xanomeline Low Dose | 77 ( 91.7) | 77 ( 91.7) | equal
  Any adverse event | Xanomeline High Dose | 76 ( 90.5) | 76 ( 90.5) | equal
  Related adverse event | Placebo | 43 ( 50.0) | - | the row is not built: the reference ADaM has no ADAE.RELGR1, which the house standard writes by ae.related.values
  Related adverse event | Xanomeline Low Dose | 72 ( 85.7) | - | the row is not built: the reference ADaM has no ADAE.RELGR1, which the house standard writes by ae.related.values
  Related adverse event | Xanomeline High Dose | 70 ( 83.3) | - | the row is not built: the reference ADaM has no ADAE.RELGR1, which the house standard writes by ae.related.values
  Serious adverse event | Placebo | 0 (  0.0) | 0 | differs; explained by tfl.percent.format = {"rule": "one_decimal_always"}
  Serious adverse event | Xanomeline Low Dose | 1 (  1.2) | 1 (  1.2) | equal
  Serious adverse event | Xanomeline High Dose | 2 (  2.4) | 2 (  2.4) | equal
  Related Serious TEAE | Placebo | 0 (  0.0) | - | the catalog has no such row (tfl.ae.summary.rows)
  Related Serious TEAE | Xanomeline Low Dose | 1 (  1.2) | - | the catalog has no such row (tfl.ae.summary.rows)
  Related Serious TEAE | Xanomeline High Dose | 1 (  1.2) | - | the catalog has no such row (tfl.ae.summary.rows)
  Fatal adverse event | Placebo | 2 (  2.3) | 2 (  2.3) | equal
  Fatal adverse event | Xanomeline Low Dose | 1 (  1.2) | 1 (  1.2) | equal
  Fatal adverse event | Xanomeline High Dose | 0 (  0.0) | 0 | differs; explained by tfl.percent.format = {"rule": "one_decimal_always"}
  Related TEAE Leading to Death | Placebo | 1 (  1.2) | - | the catalog has no such row (tfl.ae.summary.rows)
  Related TEAE Leading to Death | Xanomeline Low Dose | 0 (  0.0) | - | the catalog has no such row (tfl.ae.summary.rows)
  Related TEAE Leading to Death | Xanomeline High Dose | 0 (  0.0) | - | the catalog has no such row (tfl.ae.summary.rows)
  TEAE Leading to Dose Modification [a] | Placebo | 0 (  0.0) | - | the catalog has no such row (tfl.ae.summary.rows)
  TEAE Leading to Dose Modification [a] | Xanomeline Low Dose | 0 (  0.0) | - | the catalog has no such row (tfl.ae.summary.rows)
  TEAE Leading to Dose Modification [a] | Xanomeline High Dose | 0 (  0.0) | - | the catalog has no such row (tfl.ae.summary.rows)
  Adverse event leading to discontinuation of study treatment | Placebo | 0 (  0.0) | 0 | differs; explained by tfl.percent.format = {"rule": "one_decimal_always"}
  Adverse event leading to discontinuation of study treatment | Xanomeline Low Dose | 0 (  0.0) | 0 | differs; explained by tfl.percent.format = {"rule": "one_decimal_always"}
  Adverse event leading to discontinuation of study treatment | Xanomeline High Dose | 0 (  0.0) | 0 | differs; explained by tfl.percent.format = {"rule": "one_decimal_always"}
  reference ADaM: valid: yes
  reference ADaM: produced: 1 of 1 outputs in gold
  reference ADaM: cells correct: 10 of 15 gold cells of the rows that gold and the candidate both have
  reference ADaM: cells correct: 10 of 27 gold cells of the outputs produced
  reference ADaM: cells correct: 10 of 27 gold cells (an output that was not produced counts as wrong)
  reference ADaM: whole output, strict: 0 of 1 outputs in gold (both axes equal and every cell equal)
  reference ADaM: whole output, lenient: 0 of 1 outputs in gold (every gold cell present and equal)
  the rows are not the key's (the key has 4 rows that arm S lacks): no other value of one table decision makes them equal
  the columns are not the key's (arm S has more: Total): explained by tfl.columns.total = {"rule": "none"}
  cells of the key that differ or are missing: 17. Of the 15 cells of the rows both tables have, 5 differ and are explained by another value of one table decision, and 0 are unexplained. 12 are in rows that arm S does not build: 3 for a variable the reference ADaM lacks, 9 in rows the catalog does not have; these are classed by the crosswalk of rows, not by a build
  variables the house template reads: 9; in the reference ADaM under the same name: ADAE.AEACN, ADAE.AESDTH, ADAE.AESER, ADAE.TRTEMFL, ADAE.USUBJID, ADSL.SAFFL, ADSL.TRT01A, ADSL.USUBJID
  variables the house template reads and the reference ADaM does not have: 1
    ADAE.RELGR1: the house standard writes it by ae.related.values; rows not built: RELATED
  analyses of the example with no row in the catalog: An07_04_RelSerTEAE_Summ_ByTrt, An07_06_RelTEAELd2Dth_Summ_ByTrt, An07_07_TEAELd2DoseMod_Summ_ByTrt
  the crosswalk of rows (example analysis = house row): An07_01_TEAE_Summ_ByTrt = ANY, An07_02_RelTEAE_Summ_ByTrt = RELATED, An07_03_SerTEAE_Summ_ByTrt = SERIOUS, An07_05_TEAELd2Dth_Summ_ByTrt = FATAL, An07_08_TEAELd2TrtDsc_Summ_ByTrt = DISCONTINUATION
(exit 0)

$ specfirst run pilot --arm R --folder /root/scratch-slice/pilot/cdiscpilot01 --score
pilot folder: /root/scratch-slice/pilot/cdiscpilot01
run R-task-28efd3ea363d: arm R, stage T, condition notes, kit cdiscpilot01 (pilot), task task-28efd3ea363d (7 decisions)
  reader: claude-code, model claude-opus-5-5, used ['claude-opus-5-5'], CLI 2.1.327
  cost: 16 turns, 42.8 s wall, 35.4 s API, tokens in 20 out 3135 cache write 54953 cache read 328163, USD 0.5680 (CLI: 0.5680366)
  budget: {'turns': 100, 'seconds': 2700, 'usd': 10.0}: within
  outputs: decisions.jsonl 1 lines, questions.jsonl 0 lines, unmapped.jsonl 3 lines
  asks: 0, answered 0
  output files: valid
  task folder: holds only what a reader may see
  canary scan: 2913 canaries from 17 files; clean
  permission denials: 1
  RUN R-task-28efd3ea363d: PASS
Traceback (most recent call last):
  File "/root/.local/share/specfirst/venv-specfirst-read-2337255930/bin/specfirst", line 8, in <module>
    sys.exit(main())
             ^^^^^^
  File "/mnt/d/trial_work/specfirst-read/src/specfirst/cli.py", line 246, in main
    return harness_command.main(repo_root(), given[1:])
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/d/trial_work/specfirst-read/src/specfirst/harness/command.py", line 155, in main
    print("\n".join(pilot.score(root, made.folder)))
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/d/trial_work/specfirst-read/src/specfirst/harness/pilot.py", line 200, in score
    found = scorepilot.run(Machine(root), records, arm)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/d/trial_work/specfirst-read/src/specfirst/score/pilot.py", line 270, in run
    for dataset, names in ars.columns(ars.index(compiled.ars), SUBJECT_KEY).items()
                                      ^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/d/trial_work/specfirst-read/src/specfirst/machine/ars.py", line 127, in index
    raise ArsError("a reporting event is a JSON object")
specfirst.machine.ars.ArsError: a reporting event is a JSON object
(exit 1)

$ specfirst score pilot --run $SPECFIRST_RUNS/R-task-28efd3ea363d
the reader's records: 1
  tfl.output.include (tfl-ae-summary): {"rule": "not_included"}, stated; cites sap [18/p9] "Table of Contents for Data Display Specifications"; sap [19/p8] "Incidence of Treatment Emergent Adverse Events by Treatme..."; sap [16/p13] "For this submission, no formal summarization of adverse e..."
pilot CDISCPILOT01, arm R (a reader's table decisions, the house default where it wrote none), stage T (table decisions on the reference ADaM); report only
key: the results CDISC's ARS example embeds for its adverse event summary (Out14-3-1-1), as the kit's layout places them
  the table decisions built: tfl.output.include = {"rule": "not_included"}; tfl.population = {"rule": "safety"}; tfl.columns.arms = {"rule": "ascending_dose_placebo_first"}; tfl.columns.total = {"rule": "all_arms"}; tfl.percent.format = {"rule": "one_decimal_zero_blank"}; tfl.rounding.rule = {"rule": "half_away_from_zero"}; tfl.ae.summary.rows = {"rule": "standard_rows"}
  arm R built no output: its decisions leave it out. The trace sets tfl.output.include = {"rule": "included"} first and explains each cell against that build (the column 'with tfl.output.include = {"rule": "included"}')
  row | column | key | arm R | with tfl.output.include = {"rule": "included"} | state
  (column header) | Placebo | (N=86) | - | (N=86) | missing; explained by tfl.output.include = {"rule": "included"}
  (column header) | Xanomeline Low Dose | (N=84) | - | (N=84) | missing; explained by tfl.output.include = {"rule": "included"}
  (column header) | Xanomeline High Dose | (N=84) | - | (N=84) | missing; explained by tfl.output.include = {"rule": "included"}
  Any adverse event | Placebo | 65 ( 75.6) | - | 65 ( 75.6) | missing; explained by tfl.output.include = {"rule": "included"}
  Any adverse event | Xanomeline Low Dose | 77 ( 91.7) | - | 77 ( 91.7) | missing; explained by tfl.output.include = {"rule": "included"}
  Any adverse event | Xanomeline High Dose | 76 ( 90.5) | - | 76 ( 90.5) | missing; explained by tfl.output.include = {"rule": "included"}
  Related adverse event | Placebo | 43 ( 50.0) | - | - | missing; with tfl.output.include = {"rule": "included"}, the row is not built: the reference ADaM has no ADAE.RELGR1, which the house standard writes by ae.related.values
  Related adverse event | Xanomeline Low Dose | 72 ( 85.7) | - | - | missing; with tfl.output.include = {"rule": "included"}, the row is not built: the reference ADaM has no ADAE.RELGR1, which the house standard writes by ae.related.values
  Related adverse event | Xanomeline High Dose | 70 ( 83.3) | - | - | missing; with tfl.output.include = {"rule": "included"}, the row is not built: the reference ADaM has no ADAE.RELGR1, which the house standard writes by ae.related.values
  Serious adverse event | Placebo | 0 (  0.0) | - | 0 | missing; explained by tfl.output.include = {"rule": "included"} together with tfl.percent.format = {"rule": "one_decimal_always"}
  Serious adverse event | Xanomeline Low Dose | 1 (  1.2) | - | 1 (  1.2) | missing; explained by tfl.output.include = {"rule": "included"}
  Serious adverse event | Xanomeline High Dose | 2 (  2.4) | - | 2 (  2.4) | missing; explained by tfl.output.include = {"rule": "included"}
  Related Serious TEAE | Placebo | 0 (  0.0) | - | - | missing; with tfl.output.include = {"rule": "included"}, the catalog has no such row (tfl.ae.summary.rows)
  Related Serious TEAE | Xanomeline Low Dose | 1 (  1.2) | - | - | missing; with tfl.output.include = {"rule": "included"}, the catalog has no such row (tfl.ae.summary.rows)
  Related Serious TEAE | Xanomeline High Dose | 1 (  1.2) | - | - | missing; with tfl.output.include = {"rule": "included"}, the catalog has no such row (tfl.ae.summary.rows)
  Fatal adverse event | Placebo | 2 (  2.3) | - | 2 (  2.3) | missing; explained by tfl.output.include = {"rule": "included"}
  Fatal adverse event | Xanomeline Low Dose | 1 (  1.2) | - | 1 (  1.2) | missing; explained by tfl.output.include = {"rule": "included"}
  Fatal adverse event | Xanomeline High Dose | 0 (  0.0) | - | 0 | missing; explained by tfl.output.include = {"rule": "included"} together with tfl.percent.format = {"rule": "one_decimal_always"}
  Related TEAE Leading to Death | Placebo | 1 (  1.2) | - | - | missing; with tfl.output.include = {"rule": "included"}, the catalog has no such row (tfl.ae.summary.rows)
  Related TEAE Leading to Death | Xanomeline Low Dose | 0 (  0.0) | - | - | missing; with tfl.output.include = {"rule": "included"}, the catalog has no such row (tfl.ae.summary.rows)
  Related TEAE Leading to Death | Xanomeline High Dose | 0 (  0.0) | - | - | missing; with tfl.output.include = {"rule": "included"}, the catalog has no such row (tfl.ae.summary.rows)
  TEAE Leading to Dose Modification [a] | Placebo | 0 (  0.0) | - | - | missing; with tfl.output.include = {"rule": "included"}, the catalog has no such row (tfl.ae.summary.rows)
  TEAE Leading to Dose Modification [a] | Xanomeline Low Dose | 0 (  0.0) | - | - | missing; with tfl.output.include = {"rule": "included"}, the catalog has no such row (tfl.ae.summary.rows)
  TEAE Leading to Dose Modification [a] | Xanomeline High Dose | 0 (  0.0) | - | - | missing; with tfl.output.include = {"rule": "included"}, the catalog has no such row (tfl.ae.summary.rows)
  Adverse event leading to discontinuation of study treatment | Placebo | 0 (  0.0) | - | 0 | missing; explained by tfl.output.include = {"rule": "included"} together with tfl.percent.format = {"rule": "one_decimal_always"}
  Adverse event leading to discontinuation of study treatment | Xanomeline Low Dose | 0 (  0.0) | - | 0 | missing; explained by tfl.output.include = {"rule": "included"} together with tfl.percent.format = {"rule": "one_decimal_always"}
  Adverse event leading to discontinuation of study treatment | Xanomeline High Dose | 0 (  0.0) | - | 0 | missing; explained by tfl.output.include = {"rule": "included"} together with tfl.percent.format = {"rule": "one_decimal_always"}
  reference ADaM: valid: yes
  reference ADaM: produced: 0 of 1 outputs in gold
  reference ADaM: cells correct: 0 of 0 gold cells of the rows that gold and the candidate both have
  reference ADaM: cells correct: 0 of 0 gold cells of the outputs produced
  reference ADaM: cells correct: 0 of 27 gold cells (an output that was not produced counts as wrong)
  reference ADaM: whole output, strict: 0 of 1 outputs in gold (both axes equal and every cell equal)
  reference ADaM: whole output, lenient: 0 of 1 outputs in gold (every gold cell present and equal)
  the rows are not the key's (the key has 4 rows that arm R with tfl.output.include = {"rule": "included"} lacks): no other value of one table decision makes them equal
  the columns are not the key's (arm R with tfl.output.include = {"rule": "included"} has more: Total): explained by tfl.columns.total = {"rule": "none"}
  cells of the key that differ or are missing: 27, every one missing: arm R built no output. With tfl.output.include = {"rule": "included"}, 10 have the key's text, 5 differ and are explained by one more table decision, and 0 are unexplained. 12 are in rows that this build does not have: 3 for a variable the reference ADaM lacks, 9 in rows the catalog does not have; these are classed by the crosswalk of rows, not by a build
  variables the house template reads: 9; in the reference ADaM under the same name: ADAE.AEACN, ADAE.AESDTH, ADAE.AESER, ADAE.TRTEMFL, ADAE.USUBJID, ADSL.SAFFL, ADSL.TRT01A, ADSL.USUBJID
  variables the house template reads and the reference ADaM does not have: 1
    ADAE.RELGR1: the house standard writes it by ae.related.values; rows not built: RELATED
  analyses of the example with no row in the catalog: An07_04_RelSerTEAE_Summ_ByTrt, An07_06_RelTEAELd2Dth_Summ_ByTrt, An07_07_TEAELd2DoseMod_Summ_ByTrt
  the crosswalk of rows (example analysis = house row): An07_01_TEAE_Summ_ByTrt = ANY, An07_02_RelTEAE_Summ_ByTrt = RELATED, An07_03_SerTEAE_Summ_ByTrt = SERIOUS, An07_05_TEAELd2Dth_Summ_ByTrt = FATAL, An07_08_TEAELd2TrtDsc_Summ_ByTrt = DISCONTINUATION
(exit 0)
```

The tests of this part:

```text
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 python -m pytest -q -p no:cacheprovider tests/unit/test_harness.py tests/unit/test_score_pilot_pins.py tests/score/test_score_pilot.py
E           AssertionError: assert (True and '[52/p' in '[1/p1] ... (the text of the SAP, cut here)')
FAILED tests/score/test_score_pilot.py::test_score_pilot[P3-pilot-folder] - A...
1 failed, 34 passed in 110.42s (0:01:50)
(the failure: the test asked for page 52 of the SAP, which has 51; the test was fixed)
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 python -m pytest -q -p no:cacheprovider tests/unit/test_harness_pilot.py tests/score/test_score_pilot.py
13 passed in 34.30s
$ ruff check src tests
All checks passed!
```

The kept dry run of read-2a against the task built now from kit 4 of the
gate seed (the task of a generated kit is unchanged), and what CI runs:

```text
$ specfirst gen kits --seed gen-2a --first 4 --count 1 --out /root/scratch-slice/gatekits
kit 4 of the set: sfrrl2uh, train, 127 files; 14 of 22 decisions separated on the twin
(exit 0)
$ specfirst run check src/specfirst/harness/kept/R-task-50024a8d7ca2 --kit /root/scratch-slice/gatekits/kit-004 --tasks /root/scratch-slice/check-tasks --seed gen-2a/kit-4
kept run R-task-50024a8d7ca2: PASS
(exit 0)
$ make test
........................................................................ [ 76%]
........................................................................ [ 83%]
........................................................................ [ 89%]
........................................................................ [ 95%]
...............................................                          [100%]
1127 passed, 26 deselected in 1030.47s (0:17:10)
$ make lint
. scripts/env.sh && python -m ruff check .
All checks passed!
$ make ascii
. scripts/env.sh && python -m specfirst.asciicheck
ASCII check: 553 files checked, 0 with non-ASCII bytes
```

## Files

- docs/decisions/ADR-016.md (the choices), docs/lessons.md (69),
  docs/state/read.md.
- `src/specfirst/harness/pilot.py`, `harness/task.py` (`render_real`),
  `harness/outputs.py`, `harness/command.py` (`run pilot`),
  `score/pilot.py`, `score/command.py` (`score pilot --run`);
  `tests/unit/test_harness_pilot.py`, `tests/score/test_score_pilot.py`.
- Outside the repository: the kits and the logs (WSL,
  `/root/scratch-slice/`), the seed files (WSL,
  `/root/specfirst-secrets/slice-ae-summary/`), the task and run folders
  (drive C, `$SPECFIRST_TASKS` and `$SPECFIRST_RUNS`), the pilot folder
  (WSL, `/root/scratch-slice/pilot/`).
