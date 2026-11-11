# Track std

Result: catalog and standard form, identifiability, the edit loop (PLAN.md
section 13.4).

## Passed

- std-1 Catalog, standard form, compiler, house standard. Gate:
  `scripts/clean_clone_gate.sh std-1` (2026-11-11). Evidence:
  docs/reports/std-1.md and std-1.gate.log. Review:
  docs/reports/std-1.review.md. Choices: docs/decisions/ADR-004.md.

## Open

- Owner node N1. The owner approves the decision catalog, the standard form
  and the house standard; docs/reports/std-1.md has a reading guide. The
  catalog stays at version `draft-1` until then. Nobody else freezes it.
- ADR-004 is a proposal. It carries the four schema points of ADR-000 item
  7 with a recommendation each; none is applied.
- Deferred by std-1 (standard/catalog/catalog.yaml, `deferred`): four
  entries of appendix B and two alternatives that need a derived record by
  aggregation.
- The layout files are layout draft 0. real-3 fixes the format (ADR-003);
  std-2 aligns the house layout templates.
- `yamaa check` is the gate; yamaa's lint is not run on compiled files (its
  findings are spacing and line width, and `unused_input_key`).
- The compiled specs are proven to run on a tiny hand-made study. For the
  alternatives that study can tell apart, 40 cases compare a built value
  with the statement (`tests/unit/test_alternatives_on_tiny.py`). That is
  not a proof on real or generated data: std-2 checks by result on the
  pilot; gen-2 checks P4 on the twin.
- Known limits of the house specs, for the owner and for std-2: ADVS has
  one parameter per VSTESTCD (position and time point, VSPOS and VSTPT, are
  not read) and PARAM is VSTEST without the unit; AOCCFL, AOCCSFL and
  AOCCPFL take the first event by AESEQ; BMI assumes kg and cm; a record
  on the first dose day timed after the dose is neither baseline nor
  post-baseline; the baseline weight of ADSL and the baseline of ADVS
  follow two rules (ADR-004, item 7).
- Three alternatives have no public source of their own
  (`unsourced_alternatives` in standard/catalog/catalog.yaml).

## Next

- std-2 Pilot decisions, mutation and identifiability. Needs real-3.
- Then std-3 (D1).

## For other tracks

- gen-1 can start from the draft catalog now. Entries, alternatives, slots
  with examples and probe recipes (`standard/catalog/probes.yaml`) are
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
  - `specfirst.compile.tiny` is a three-subject study in these domains.
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
  9.3; `standard/catalog/knowledge/` holds reading notes v0.

## Handed over by base-0

- `standard/schemas/decision-record.schema.json` is version 0 of the
  decision record. std-1 added `catalog-entry.schema.json` and changed no
  version 0 schema. A change to one needs an ADR.
