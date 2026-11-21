# Track std

Result: catalog and standard form, identifiability, the edit loop (PLAN.md
section 13.4).

## Passed

- std-1 Catalog, standard form, compiler, house standard. Gate:
  `scripts/clean_clone_gate.sh std-1` (2026-11-11). Evidence:
  docs/reports/std-1.md and std-1.gate.log. Review:
  docs/reports/std-1.review.md. Choices: docs/decisions/ADR-004.md.
- Owner node N1, 2026-11-17. The owner chose "as delivered" for all 14
  questions of the reading guide and called the answer provisional, then
  confirmed the freeze ("Freeze", in translation). The catalog is version
  1, tagged `catalog@1`. The words and their limits are in
  docs/decisions/ADR-004.md, "Node N1: the owner's answer". The gate on
  the frozen commit is in docs/reports/std-1.md, "After node N1".
- std-issues (2026-11-18 and 19): the parts of issues #26, #24 and #25
  that change neither `catalog@1`, nor `open-default@1`, nor the
  generator. Gates on clean clones of `42212b8`: std-1, real-2, real-3a,
  gen-2a, gen-3a, read-1a, read-2a, all PASS. Generated kits 1 to 4 of
  the seed gen-2a are the same bytes. Evidence: docs/reports/std-issues.md
  and its seven logs. Review: docs/reports/std-issues.review.md (pass 2
  signed). Choices: docs/decisions/ADR-014.md, approved by the owner on
  2026-11-18 (it changes ADR-005, decision 3).
  - #26: the scorer compiles in the pending mode
    (`compile_decisions(pending=True)`): a decision without a value that
    the build needs leaves out what it binds (columns and lookups and
    what derives from them; a dataset whose records rest on it; analyses,
    rows, whole outputs), and the build score counts those gold cells
    apart, neither right nor wrong. Arm S now builds the chain.
    `specfirst compile` and the generator are unchanged.
  - #25: `compile_decisions(sdtm=...)` leaves out a column, or a dataset
    whose records rest on one, that derives from a variable the SDTM lacks
    and SDTMIG v3.4 does not require (warning); a table reading what is
    left out is not produced; a Required one stops the compile.
  - #24: the scorer's build stops after ADaM when no subject has TRTSDT,
    naming the decision, its alternative, its filter and the empty
    variable.
- catalog-2a (2026-11-21): the versions of the standard (ADR-020, approved
  by the owner the same day). Versioned folders `standard/catalog@<n>/` and
  `standard/houses/<house>@<n>/`, listed with status and tree in
  standard/versions.yaml; the defaults move into the house
  (`defaults.yaml`); `migration.yaml` and standard/BACKLOG.yaml; the checks
  of the versions. Gates on clean clones: catalog-2a, std-1, gen-2a, gen-3a,
  read-1a, read-2a, all PASS. Evidence: docs/reports/catalog-2a.md. Review:
  docs/reports/catalog-2a.review.md (pass 2 signed).
- catalog-2b (2026-11-21): the content of `catalog@2` and `open-default@2`
  (ADR-020, decision 7): issues #1 to #24, #28 and #33 of the owner-side
  review, with the eight new house defaults and the two changed N1 answers.
  The owner accepted three departures as built before the freeze (ADR-020,
  "The owner's answer on the three departures"). Version 2 is frozen and
  tagged `catalog@2` and `open-default@2`. Gates on clean clones: catalog-2b,
  std-1, gen-2a, gen-3a, read-1a and read-2a, all PASS; then catalog-2b and
  std-1 again on the freeze commit. Generated kits are the same bytes.
  Evidence: docs/reports/catalog-2b.md. Review:
  docs/reports/catalog-2b.review.md.

## For other tracks (from std-issues)

- read: `scorer.Result.pending` and `BuildScore.pending_by_decision()`
  name the gold cells that wait for a decision without a value; a waiting
  output leaves `in_gold`. A candidate that asks and gets no answer is
  built and scored on the rest (ADR-014).
- gen, read: `compile_decisions` takes `pending` and `sdtm`; both are off
  by default, and a compile that needs neither gives the files it always
  gave (the kits are the same bytes).
- Left for later: a `trt.end.source` alternative that reads no dose
  (`catalog@2`, #23), a probe with EXDOSE missing everywhere (generator),
  `specfirst compile --sdtm`.

## Open

- `catalog@1`, `open-default@1`, `catalog@2` and `open-default@2` are
  frozen. A change of an entry, an alternative, a default or a statement is
  a new version (`catalog@3`, `open-default@3`) with its own
  `migration.yaml` and backlog records, and needs an ADR.
- What waits, and for what, is in standard/BACKLOG.yaml (status `waits`):
  for std-2 among others the refusal of a VS dataset with several positions
  or time points, DTYPE null on collected records (it needs another key of
  ADVS first), the unscheduled visit of an SDTM without VISITDY, ARS
  templates from the decision records, and the decision record schema.
- The four schema points of ADR-000 item 7: the owner took the
  recommendations of ADR-004. Point 3 (which records must cite) is for
  std-2 to apply; point 4 (the prefix `layout:`) for real-3 with ADR-003.
- Deferred by std-1 (standard/catalog@1/catalog.yaml, `deferred`): four
  entries of appendix B and two alternatives that need a derived record by
  aggregation.
- The layout files are layout draft 0. real-3 fixes the format (ADR-003);
  std-2 aligns the house layout templates.
- `yamaa check` is the gate; yamaa's lint is not run on compiled files (its
  findings are spacing and line width, and `unused_input_key`).
- The compiled specs are proven to run on a tiny hand-made study. For the
  alternatives that study can tell apart, 50 cases compare a built value
  with the statement (`tests/unit/test_alternatives_on_tiny.py`). That is
  not a proof on real or generated data: std-2 checks by result on the
  pilot; gen-2 checks P4 on the twin.
- Known limits of the house specs of `open-default@1`, for the owner and
  for std-2 (`open-default@2` gives PARAM the unit of its parameter and
  makes post-baseline time-aware, so that no record falls between baseline
  and post-baseline; the rest stands there too): ADVS has
  one parameter per VSTESTCD (position and time point, VSPOS and VSTPT, are
  not read) and PARAM is VSTEST without the unit; AOCCFL, AOCCSFL and
  AOCCPFL take the first event by AESEQ; BMI assumes kg and cm; a record
  on the first dose day timed after the dose is neither baseline nor
  post-baseline; the baseline weight of ADSL and the baseline of ADVS
  follow two rules (ADR-004, item 7).
- Left open after the second pass of the review: when two dosed exposure
  records start on the first dose day, one with a time and one without,
  the one without gives the treatment start (00:00, time flag set);
  `checks.structural_probe_problems` compares compiled files, so it cannot
  see a structural claim that fails only because two layout rules give the
  same table for a given design (the kind `design` exists for that); a
  bind is complete for the values `compiler.other_values` tries, not for
  every value a slot can take.
- Three alternatives of `catalog@1` have no public source of their own
  (`unsourced_alternatives` in standard/catalog@1/catalog.yaml);
  `catalog@2` removes them (ADR-020, question 3).

## Next

- catalog-2c: the slice of ADR-005 moves to version 2 (ADR-020, amended
  decision 8). The owner approved its model costs (about USD 1.6 in all:
  the natural-form rewrite and read-back, at most 4 calls, and one dry run
  of arm R). The std track makes all of it, the files of gen and read
  included, in one package with one review; the gen and read tracks touch
  none of those files while it is open. SEP01's expected values and classes
  (`specfirst.gen.sep01`) are worked out again with
  `specfirst gen separate sep01`. Until catalog-2c merges, the default pair
  stays (`catalog@1`, `open-default@1`).
- std-2 Pilot decisions, mutation and identifiability. Needs real-3.
- Then std-3 (D1).

## For other tracks

- From catalog-2a and catalog-2b: build a path to the catalog with
  `specfirst.compile.catalog.default_dir(root, label)`, never by hand; the
  loaders take a label (`house.load_pair(root, catalog, house)`). From
  `catalog@2` the defaults are the house's (`house.default_value`), and a
  default may depend on the design. STANDARD.md of `open-default@2`
  anchors by entry ID (`[ae.teae.end]`), with fixed rules
  (`[ae.teae.start/no_start_date]`) and one statement per case of a
  default by design (`[pop.safety.rule/1]`). In `open-default@2` a visit is
  unscheduled when VISITDY is missing or VISIT contains UNSCHED, a subject
  is randomized by the disposition record first, and PARAM carries the
  unit. What changed is in standard/catalog@2/migration.yaml.
- gen-1 and gen-2 work from `catalog@1`. Entries, alternatives, slots
  with examples and probe recipes (`standard/catalog@1/probes.yaml`) are
  usable as they are. A probe of the kind `design` asks for a property of
  the design (arms listed out of dose order), not for a planted record.
  What gen-1 should know:
  - SDTM variables the house specs read: DM (ARM, ARMCD, ACTARM, RFSTDTC,
    RFXSTDTC and the demographics), EX (EXSEQ, EXTRT, EXDOSE, EXSTDTC,
    EXENDTC), DS (DSSEQ, DSCAT, DSSCAT, DSDECOD, DSSTDTC), SV (VISIT,
    VISITNUM), VS (VSSEQ, VSTESTCD, VSTEST, VSSTRESN, VSDTC, VISIT,
    VISITNUM, VISITDY) and AE (AESEQ, AETERM, AEDECOD, AESOC, AESEV, AESER,
    AEREL, AEACN, AEOUT, AESDTH, AESTDTC, AEENDTC).
  - A visit is unscheduled when VISITDY is missing. A placebo record has
    EXDOSE 0 and an EXTRT that contains PLACEBO. A subject is randomized
    when ARMCD is present and is neither SCRNFAIL nor NOTASSGN.
  - `specfirst.compile.tiny` is a four-subject study in these domains.
- std-2 and std-3: `compiler.bind_tables` gives the `decides` edges to ARS
  elements and layout parts by mutation; `specfirst compile` writes them to
  `compile.json`. An ADaM bind is the column a fragment writes, often a
  working column; the dataset variables behind it follow from the
  `derives_from` edges that real-1 builds from the resolved spec.
- gen-2: a decision can compile into files no output reads (for example
  `pop.efficacy.rule` when no table uses the efficacy-evaluable set), and
  `tfl.pvalue.format` shows only beside a treatment comparison. Such a
  decision cannot be separated in that kit (ADR-004, consequences).
- real-2 and real-3: the compiled ARS file follows the CDISC example. Method
  IDs are `Mth_Count`, `Mth_CatSumm`, `Mth_ContSumm`, `Mth_EventCount`,
  `Mth_Anova`, `Mth_ChiSq`, `Mth_Fisher`; the method description names the
  registry entry; the quantile definition is an analysis parameter
  (`programmingCode.parameters`). Treatment groupings are data-driven; the
  column order rule and the total column are in the layout. Tell std when a
  convention of the engines differs: the house templates follow.
- read-1 and read-2: `specfirst parse` is the parser control of section
  9.3; `standard/catalog@1/knowledge/` holds reading notes v0.

## Handed over by base-0

- `standard/schemas/decision-record.schema.json` is version 0 of the
  decision record. std-1 added `catalog-entry.schema.json` and changed no
  version 0 schema. A change to one needs an ADR.
