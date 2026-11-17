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
  docs/reports/gen-2a.review.md. Choices: docs/decisions/ADR-007.md.

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
gold/design.yaml  probes.jsonl  truth/subjects.jsonl
gold/decisions.jsonl        one record per decision: value, status, class, statement,
                            citations, binds, identifiable
gold/docs/sap.md            the stated decisions in standard form (document ID sap)
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
  table: compare decision values and report it apart (section 9.3). Three
  kinds occur. Not read: the output does not read it under the decisions
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

## For gen-3a

- `gold/docs/sap.md` is one standard-form document with every stated
  decision; the records cite it by anchor, the defaults cite
  `inputs/house/STANDARD.md` (document ID `house`). gen-3a owns the
  documents of a kit (protocol and SAP, natural form, tiers): it replaces
  that file and the citations, in `kits._attempt`, where stage S6 belongs.
- A decision is `stated` when its value is not the house default, else
  `default`. The tier `full` states defaults too; that changes `status`
  and `citations`, not values.
- Change `GENERATOR` with any change that gives other bytes. Kits are
  generated again, never patched.

## Open

- The data of a kit are a function of the design and the seed (gen-1a);
  the decisions are sampled to fit them. A probe that holds for one
  analysis set (the calibrated counts) cannot follow the decisions.
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

- gen-3a (needs gen-2a): protocol and SAP in standard form and in natural
  form for the decisions of the slice.
- read-1a (needs real-3a and gen-2a): the scorer.
- Then the rest of gen-1, gen-2 and gen-3.

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
