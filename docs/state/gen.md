# Track gen

Result: generated studies for the parallel-group design PG-FIX (PLAN.md
section 13.5), first for the slice "adverse event summary first" (ADR-005).

## Passed

- gen-1a (2026-11-17): CDISC CORE in the environment (ADR-006); the design
  model and the sampler for PG-FIX; the subject process; SDTM for eleven
  domains with Define-XML; 28 probes for the 22 decisions of the slice; the
  gate `gen-1a`; `specfirst gen design|study|check`. Report:
  docs/reports/gen-1a.md. Review: docs/reports/gen-1a.review.md (signed).
- gen-2a (2026-11-17): the decisions of a kit sampled within
  `open-default@1` at `catalog@1`; compile; gold on the visible data and on
  the twin with both result engines; P1 to P4; the manifest; the splits;
  the gate `gen-2a`; `specfirst gen kit|kits|verify`. Its first commits
  settle the eight findings of pass 2 of the gen-1a review. Report:
  docs/reports/gen-2a.md (the gate, its numbers, the limits). Review:
  docs/reports/gen-2a.review.md (signed in its second pass, for the slice).
  Choices: docs/decisions/ADR-007.md; the owner approved the gate's
  reading of "applicable" for the slice only, and a rework is owed before
  the gate of the full gen-2 (see "Next").
- gen-3a (2026-11-18), gate passed, review signed, merged into `main`
  after the owner approved the two choices the review left to the owner,
  for the slice only (ADR-009, "The owner's answers on items 4 and 5").
  The protocol and the SAP of each kit in standard form and in natural
  form; the tiers full, standard and the ask demo with the oracle; a
  one-page summary; the visible probes in `kit.yaml`; the store of model
  text and the loop of section 6.6 (`specfirst gen natural`); the gate
  `gen-3a`. Gates on clean clones of `901be3d`: gen-3a 15 of 15, gen-2a 13
  of 13, read-1a 14 of 14. Report: docs/reports/gen-3a.md. Review:
  docs/reports/gen-3a.review.md (signed in pass 2). Choices:
  docs/decisions/ADR-009.md.

- Issue #30 (2026-11-21): P4 on a reference study, one class per decision
  instead of a failure (ADR-019): `separated`, `unseparated` (with the
  values that reproduce and, for an integer slot, the interval),
  `inert`, `separated_at_dataset_only`. The test study SEP01 and the
  planted defects; the classes on cdiscpilot01, report only. Report:
  docs/reports/issue-30.md. Review: docs/reports/issue-30.review.md.
  Generated kits do not change. See "P4 on a reference study".

## A kit: what the folder holds

`specfirst gen kit --seed S --out DIR` writes one kit; `specfirst gen kits
--seed S --count N --out DIR` the kits 1 to N of the set of a seed, in
`kit-001`, `kit-002`, ... A kit is never in the repository.

```text
kit.yaml                    id, tier A, archetype, slice, split, generator, catalog, house,
                            pins, the properties, the SHA-256 of every file
study.json                  the manifest of the data (gen-1a)
inputs/data/sdtm/           visible SDTM: <domain>.parquet, <domain>.json, define.xml
inputs/house/               the house standard, as in standard/houses/open-default@1
inputs/docs/                protocol.md and sap.md in natural form (gen-3a, below)
gold/design.yaml  probes.jsonl  truth/subjects.jsonl
gold/decisions.jsonl        one record per decision: value, status, class, statement,
                            citations, binds, identifiable
gold/docs/                  protocol.md and sap.md in standard form, natural.json
gold/oracle.yaml  gold/summary.md     the oracle's answers; one page about the kit
gold/spec/                  adam/*.yaml with fragments/ and project.yaml,
                            ars/reporting-event.json, layout/tfl-ae-summary.json, compile.json
gold/resolved/  data/adam/  ars/  ard/  grid/  out/  graph/      built on the visible data
gold/reference/tfl-ae-summary.json    the table calculated by hand (P2)
gold/identifiability.json   the matrix of the twin (P4)
twin/data/sdtm/  twin/truth/
twin/gold/                  data/adam/, ars/, ard/, grid/, out/, graph/, reference/
```

- `gold/ard/reporting-event.jsonl` is the ARD of the Python engine,
  `.r.jsonl` that of the R engine. `gold/ars/reporting-event.json` is the
  ARS file with the groups of the treatment grouping listed and the results
  embedded; `gold/spec/ars/reporting-event.json` is the compiled file, with
  the grouping still data-driven.
- `gold/grid/Out_AESUM.json` is the grid, `Out_AESUM.shell.json` its mock
  shell. Row 1 has the section `@header` and holds the counts under the
  column headers. Every cell names the ARD rows behind it (`ard`), also a
  cell with a count of zero: the groups are listed, so the engines give a
  row for an arm without records.
- A kit of the slice builds ADSL and ADAE. The other three outputs of the
  house are stated as not included; the decisions of `mod-demographics`
  are at the house default; `mod-bds-visits` is not in the vector.

## How to load a kit and build a decision vector on it

```python
from specfirst.gen import decisions, gold, kits, study, verify
from specfirst.gen import design as designs

manifest = kits.read_manifest(kit_dir)             # kit.yaml
records = kits.read_decisions(kit_dir)             # gold/decisions.jsonl
values = decisions.as_values(records)              # entry -> value (the output of the slice)
design = designs.load(kit_dir / "gold" / "design.yaml")
rows = study.read_tables(kit_dir, "twin")          # SDTM as rows; or "visible"
made = verify.grid_of(kit_dir, "twin")             # the gold grid

bench = gold.Workbench(root, catalog, house, kit_dir, "twin", scratch_folder)
shown = bench.show(candidate_records, gold.arms_of(design, decisions.as_values(candidate_records)))
shown.grids["Out_AESUM"], shown.rows, shown.plans  # grid, ARD (Python), ADaM tables
```

- `candidate_records` are `{id, unit, value}`. They must hold the records
  the kit holds beyond the slice (the three outputs not included, the
  demographics defaults): take the gold records and replace values.
  `decisions.vector` builds the full list from slice values.
- `Workbench.show` raises `gold.GoldError` when a vector cannot be compiled
  or built (an analysis set without a subject, the efficacy-evaluable set in
  a design without one). That is the "validity" of section 9.2.
- `verify.table_view(grid)` gives the column labels and, per row, the label
  and the cell texts; `verify.differences` and `verify.changed_cells`
  compare two of them. `specfirst.gen.reference.table` is the hand
  calculation of any vector on any SDTM rows.
- `kits.check(root, kit_dir, print)` decides P2 to P4 of a written kit
  again; `specfirst gen verify DIR` is the command.

## What a scorer must know (read-1a)

- `gold/identifiability.json` is the matrix of the twin. Per decision:
  `read` (the output reads an element the decision sets), `applicable` (the
  log of probes claims a probe for every pair of the gold value with
  another alternative), `identifiable` (`separated`, `unseparated`, or
  `no_alternative`), `reason`, and `pairs` with `gold`, `claimed`,
  `separated` and the number of changed `cells`. The decision records
  repeat `identifiable`.
- A decision that is `unseparated` on the twin cannot be scored by the
  table: compare decision values and report it apart (section 9.3). This
  holds also for a decision that the table reads: a kit of this generator
  can state a decision, have a table that reads it, and still give the
  same table as under the house default (kit 9 of the gate set states
  rounding half to even; every cell of its twin has the same text under
  the default). The owner approved that for the slice on 2026-11-17
  (ADR-007, "The owner's answer on decision 6"). A table that equals the
  gold table is therefore no evidence for an `unseparated` decision, and a
  table that differs is not caused by one. Three kinds occur. Not read: the output does not read it under the decisions
  of the kit (`pop.randomized.rule` in a kit on the safety set;
  `date.studyday.origin` in every kit of this slice). Read without a probe:
  `tfl.rounding.rule` outside the safety set grouped by actual treatment
  from DM, and the decisions that act through one planted event in a kit on
  the efficacy-evaluable set. Equal by another decision:
  `pop.safety.grouping` when actual treatment is the same as planned.
- The matrix changes one decision at a time, from the gold vector. Two
  wrong decisions can cancel in the table, and so can two planted subjects
  in one arm; a kit is written only when every claimed pair is separated,
  not when every pair of pairs is.
- Slot values. A slot of an alternative is mutated to one value only, the
  one the probes are built around (`decisions.variants`). A wrong value of
  a slot of the gold alternative is not in the matrix, except for
  `ae.related.values`, which has one alternative. The review of gen-1a
  counted how often two values of a slot give the same table (F23).
- `disp.status.record` is never "the record with the subcategory STUDY
  TREATMENT" in a gold vector, and "STUDY PARTICIPATION" only where the
  output does not read the decision: see "For the std track".
- The visible data carry a part of the probes. There is no matrix for
  them; `verify.mutate(..., "visible", ...)` computes one.
- The order of the treatment columns needs the arms of the protocol
  (`gold.arms_of(design, values)`). A reader cannot state the order of the
  arms: the alternative `protocol_order` has no slot for it.

## The documents of a kit (gen-3a; for read-2a)

Choices: docs/decisions/ADR-009.md. Code: `specfirst.gen.documents` (stage
S6, the checks of a written kit), `specfirst.gen.natural` (the store, the
slot check, the read-back, the loop), `specfirst.gen.gate3` (the gate).

```text
inputs/docs/protocol.md     natural form, document ID protocol: what a reader gets
inputs/docs/sap.md          natural form, document ID sap
gold/docs/protocol.md       standard form, document ID protocol-standard
gold/docs/sap.md            standard form, document ID sap-standard
gold/docs/natural.json      every paragraph of the natural form: anchor, kind (design,
                            decision, filler), the decision, where its text came from
                            (model, template, missing), the SHA-256 of its text
gold/oracle.yaml            the answers of the oracle (empty outside the ask demo)
gold/summary.md             one page about the kit, for people
```

- Every decision a kit's documents state is stated once, in the document of
  its entry (`documents.home_of`): the protocol states `pop.randomized.rule`,
  `pop.safety.rule`, `pop.efficacy.rule` and `ae.related.values`; the SAP the
  rest. The natural protocol also describes the design: the arms in the
  order of the protocol (code, label, description, treatment name, dose),
  the visits with their planned days, the vital signs with their codes, the
  causality scale, the disposition subcategories. A reader needs it: the
  order of the arms is in no decision (ADR-007, decision 2).
- Anchors. The standard form: `[<section>/s<n>]` (ADR-004). The natural
  form: every paragraph of the body, design and filler included, starts
  with `[<section>/p<n>]`, where `<section>` is the number of its heading
  (`4.1`). A decision paragraph is one line. `Documents.span` of the scorer
  reads both.
- Citations. A stated decision cites first its standard-form statement
  (`sap-standard`, `3/s2`, the statement), then its natural paragraph
  (`sap`, `4.1/p2`, the whole paragraph). A reader cites the natural form;
  the reading score accepts either (a citation that names an anchor gold
  cites, with a quote inside its span).
- Tiers (`documents.TIER_PLAN`, by the number of a kit in a set): full in
  kits 1, 3, 6, 9; standard in 2, 5, 8, 10; the ask demo in 4 (train) and 7
  (dev). In a full kit every decision is `stated` (`document_rule`), house
  defaults included. In the ask demo every decision of the slice without a
  house default (`ae.related.values`; `pop.efficacy.rule` where the design
  has the efficacy-evaluable set) is in no document: status `asked`, class
  `study_input`, the gold value, no citation; `gold/oracle.yaml` holds its
  value and the answer the oracle gives (the standard-form statement).
- `specfirst ask` (section 11.3) is read-2a's: answer from
  `gold/oracle.yaml`, only for a decision that it lists.
- The parser control asks the oracle for what neither the standard-form
  documents nor the house standard decide (`scorer.control_records`). A
  candidate record with the status `asked` counts as asked when the run
  gives no list of questions; `specfirst score kit --decisions` always
  gives one (empty without `--questions`).
- `kit.yaml` has `documents` (the tier, the files, how many decisions are
  stated and which are asked, the paragraphs by source) and `probes`
  (`visible` and `twin`: the probes of the log by dataset).

How to load them:

```python
from specfirst.gen import documents
texts = documents.read_texts(kit_dir)        # {protocol, sap, protocol-standard, sap-standard}
oracle = documents.read_oracle(kit_dir)      # {"answers": [{decision, unit, value, answer}]}
paragraphs = documents.paragraphs(texts["sap"])   # anchor -> text
kit = specfirst.score.kit.load(kit_dir)      # kit.documents has the four and house;
                                             # kit.oracle (entry, unit) -> value
```

How the natural form is made (ADR-009): a model rewrites each statement
once; the text, the slot check and the verifier's read-back are frozen in
`src/specfirst/gen/rewrites/` (append only; README there), and a kit takes
the accepted text of each statement. The store holds the 61 statements of
the ten kits of the gate seed. A kit of another seed states statements the
store may not have: its paragraph is the phrasing template, marked
`missing`, and the kit fails the gate gen-3a until the loop has run for it
(`specfirst gen natural`, with `SPECFIRST_REWRITES` naming a store outside
every checkout for dev, test and sealed kits). The model is reached through
subagents of a Claude Code session; the CLI on this machine is not logged
in (ADR-009, decision 1).

- Change `GENERATOR` with any change that gives other bytes. Kits are
  generated again, never patched. It is `gen-3a.2` now.
- `specfirst gate` refuses to run while `SPECFIRST_REWRITES` is set, and
  `specfirst gen natural requests|propose` refuses dev, test and sealed
  kits (but those of the gate seed) while the store lies inside a
  checkout.

For read-2a, from the review of gen-3a:

- A run of the reader must give `scorer.run` the questions it asked
  (`asked=`); with `asked=None` a record with the status `asked` counts as
  asked (finding D8). `specfirst score kit --decisions` always gives the
  questions file (empty without `--questions`).
- Kits 5 to 10 of the gate seed carry the splits dev and test, but their
  seed is in the repository and their statements are in the store: never
  score on them as dev or test kits (finding D7).
- The store maps every natural paragraph back to its statement: keep it
  out of a task folder and under the canary scan (section 11.2).

## P4 on a reference study (issue #30, ADR-019)

Code: `specfirst.machine.separation` (the levels, the classes, the
interval, the review, two matrices compared; no builds),
`specfirst.gen.separate` (the builds by the scorer's chain, what an output
reads, the scan, the matrix, the pilot's data and arms),
`specfirst.gen.sep01` (the test study). Command: `specfirst gen separate
sep01|cdiscpilot01 [--vector house|window] [--span N] [--out FILE]
[--check FILE]`; the matrix goes to build/separation/<study>.json.

```python
from specfirst.gen import separate
from specfirst.score.candidate import Machine
machine = Machine(root)                       # the full house: ADSL, ADAE, ADVS
records = separate.house_vector(machine.catalog, machine.house, {key: value})
matrix = separate.Mutation(machine, data, arms, records).matrix(study="name")
# data: score.candidate.Data(name, sdtm={stem: Arrow table}); arms as gold.arms_of gives them
```

- Per decision: `class`, `identifiable` (for the decision record:
  `separated` only for the class `separated`), `read`, `outputs` (that
  read it), `values` (every value tried: `label`, `value`, `level` of
  fails/outputs/results/adam/none, the counts `adam`, `results`, `cells`,
  `reads`), `reproduce` (level none), `dataset_only` (results or adam),
  `intervals` (integer slots of gold: `low`, `high`, what ends each side:
  separated, slot_minimum, slot_maximum, scan_limit), `reason`. Then
  `summary`, `review` (unseparated first) and `problems` (an inert
  decision that changes an output; must be empty).
- A generated kit keeps its own matrix (gen-2a). Its `unseparated` with
  the reason "the output does not read what the decision sets" is `inert`
  here; its other `unseparated` is `unseparated` or
  `separated_at_dataset_only` here (the kit's matrix compares grids only).
- The values tried are the catalog's examples: an example that names
  nothing in the study can reproduce gold for that reason alone
  (`tfl.columns.total`, control "Active Control"). Read the value that
  reproduces before asking about it.
- The pilot: 22 decisions of the slice, under the house standard alone
  (`--vector house`) and with a window of 30 days (`--vector window`);
  about 40 builds of 2 s each. Neither vector is the pilot's own rule set
  (std-2). The custom decisions of the efficacy tables have no listed
  alternative and are not in the matrix.

For the read track (the scorer is not changed by issue #30):

- The rule of the issue: an exam never credits an `unseparated` decision
  as learned, and reports it apart. The machine's part is done: the
  matrix marks every decision that is not `separated` `unseparated` in
  `identifiable` (`separation.identifiable`), and `separation.credited`
  says whether results can confirm a record. What is left for the scorer:
  `score.reading` scores the value of an `unseparated` decision like any
  other and `score.report` lists it apart; when the exam of section 11.4
  is built, its "learned" must leave those out, and the report should
  list the classes of a reference matrix apart, in the order of its
  `review` (unseparated first, with the values that reproduce; dataset
  only, with the outputs named).
- `specfirst score pilot` (stage T, table decisions on the reference ADaM)
  reads no matrix. Built from the pilot's SDTM by the chain under the house
  standard, three table decisions are `unseparated` (`tfl.columns.arms`,
  `tfl.columns.total`, `tfl.rounding.rule`; build/separation/
  cdiscpilot01-house.json from `specfirst gen separate cdiscpilot01`). At
  stage T the ADaM is the reference's, not the chain's: a matrix of stage T
  would be made the same way, on `Data(adam=...)`, and is not made here.

## Open

From the review of gen-3a, to settle before the loop of the natural form
runs for another seed (docs/reports/gen-3a.review.md, pass 2):

- D14: a pick `(none)` (the paragraph states none of the alternatives)
  counts neither as agreement nor as failure, so the loop never falls back
  to the phrasing template for it. Drop a pick equal to the abstention only
  when an alternative of the entry has that ID; count it as a failure
  otherwise; plant three abstentions in the loop test.
- D13: the answer template of the read-back request writes `none`; it
  should write `(none)`.
- D15: plant a natural document with one filler section and a summary line
  of 101 characters (rule R5).
- D5, the known limit of the slot check: an ordinary word added to a value
  or a rule passes both checks; the verifier should also read back the slot
  values before rewrites that move further from the standard form.

- The data of a kit are a function of the design and the seed (gen-1a);
  the decisions are sampled to fit them. A probe that holds for one
  analysis set (the calibrated counts) cannot follow the decisions. The
  gate `gen-2a` therefore reads "applicable" as "claimed by the log of
  probes" (ADR-007, decision 6). The owner approved that reading for the
  slice only; the rework is the last point under "Next". Until it is
  done, look at the matrices of a set before the set is used: how many
  kits leave a decision unseparated that the table reads differs by seed
  (2 of 10 in the set of the gate; 2 and 4 of 10 in two sets of the
  reviewer, one case stated in the document of a dev kit).
- The scenarios of a set (`decisions.SCENARIOS`) are what makes every
  decision read and claimed in some kit of ten. A set of other size keeps
  the rotation.
- The seed of a set with dev and test kits must be a file outside every
  checkout. No such file exists yet. The kits of the gate are development
  kits and are removed after the gate.
- Not done, and not part of gen-2a: the other three table families and
  their probes; documents (gen-3a); strata, endpoints and analysis timing
  in the design model; TI.

For the std track:

- The recipe of the probe `two_disposition_events` gives a subject whose
  last disposition event is the study participation record, so
  `disposition_event` and `disposition_event_by_subcategory` pick the same
  record unless the subcategory is that of the treatment record. And with
  that subcategory nearly no subject has an end-of-study date. A kit can
  separate the decision only from `disposition_event` towards the treatment
  record; the value "STUDY PARTICIPATION" is never separated.
- `tfl.population` has the alternative `efficacy` in every design; in a
  design without that set it cannot be built. The catalog has no
  applicability per alternative.
- `tfl.columns.arms`: the alternative `protocol_order` carries no order. A
  build needs the arms of the protocol from elsewhere (ADR-007, decision 2).
- The house layout templates are layout draft 0. Four entries decide what
  layout spec v0 cannot carry: a total column, a column rule, a rounding
  rule, a rule for a count of zero (ADR-007, decision 3).
- The house ARS templates give the treatment grouping as data-driven; the
  engines then give no result for an arm without records (ADR-007,
  decision 1).
- The probe `dosed_but_not_randomized` is a DM record that four rules of
  CORE for SDTMIG v3.4 do not allow. `core_findings.yaml` says so now.
- `ae.start.imputation`, first alternative: yamaa's `not_before` moves a
  partial start up to the treatment start only when the treatment start is
  in the month of the partial date, as the statement reads. Settled by
  experiment (docs/reports/gen-2a.md).

For the real track:

- `specfirst.machine.lineage` has two more words (`part`, DATE).
  `display.pattern` has the option `rounding`; `display.round.half_even`
  is a new registry entry (ADR-007, decision 4).
- `graph.check_cells` is content with one `reads` edge per analysis
  (lesson 45).

## Next

- read-2a (needs read-1a and gen-3a): the task folder takes `inputs/` of a
  kit (the natural documents in `inputs/docs/`); `specfirst ask` answers from
  `gold/oracle.yaml`. See "The documents of a kit".
- Then the rest of gen-1, gen-2 and gen-3. For gen-3: the documents of the
  other three table families; more than one rewrite per statement, and a
  phrasing family held out for an exam (section 6.7); rewrites that move
  further from the standard form (ADR-009, "For the owner").
- Owed before the gate of the full gen-2 is run (the owner's answer of
  2026-11-17 on finding G1 of the gen-2a review; ADR-007): the probes
  follow the decisions of the kit. The decisions are sampled first and
  the probes are planted after them (section 6.4, S1 before S3): the
  calibrated counts for the analysis set and the grouping of the kit's
  own table, the planted subjects inside its analysis set.
  `probes.REACHES` keeps only the conditions under which another decision
  of the kit makes the alternatives equal on any data; the conditions
  `_ANALYZED` and that of `tfl.rounding.rule` go. The gate fails on a kit
  in which a decision that the output reads, and that data could
  separate, is not separated on the twin. This changes `study.generate`
  (the data of a kit then depend on its decisions) and the order in
  `kits._attempt`, so the gate of gen-1a runs again, with CORE, and
  `GENERATOR` changes. The kit folder and the loading API above need not
  change. Not started; when it is done, and as which part, is the owner's
  to plan.

How to run things:

- After merging `main`: `make install` once; `specfirst doctor`.
- `specfirst gate gen-2a` writes ten kits twice (20 builds, four at a
  time) and decides each again: about 15 minutes. `specfirst gate gen-1a`
  takes about 20 minutes, nearly all of it CORE. Wrap every gate, test
  suite or generator run in `flock /run/lock/specfirst-heavy.lock
  <command>` (lesson 32).
- One kit takes about half a minute per decision vector; a vector is drawn
  again when its kit does not separate what the log claims.
- A clean clone is under `/tmp`, which WSL clears a minute after the last
  command: copy what must last in the same command (lesson 39).

## Handed over by base-0

- CDISC CORE: installed by gen-1a through `env/` (docs/decisions/ADR-006.md).
