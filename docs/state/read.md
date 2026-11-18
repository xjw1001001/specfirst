# Track read

Result: scorer, harness, reader agent, first scores (PLAN.md section 13.6),
first for the slice "adverse event summary first" (ADR-005).

## Passed

- read-1a (2026-11-17): the scorer for the slice. Reading score, build
  score with the four scores of ADR-005, decision 4, attribution, the arms
  S and C, the planted defects of section 9.5 that apply to the slice; on
  a hand-made study, on the pilot (report only) and on the ten kits of the
  gate of gen-2a; the gate `read-1a`; `specfirst score ...`. Report:
  docs/reports/read-1a.md (the gate, its numbers, the pilot table, the
  limits). Review: docs/reports/read-1a.review.md. Choices:
  docs/decisions/ADR-008.md, with four points for the owner.

## What exists (`src/specfirst/score/`; each module says what it does)

- `reading`: the reading score of section 9.1, by class and by unit.
- `build`: the four scores of ADR-005, decision 4, each with its
  denominator, for the visible data and for the twin.
- `candidate`: a decision vector built on a dataset, as gen-2a builds the
  gold of a kit (listed groups, `specfirst.gen.display`). A `Build` is
  what the rest of the scorer reads.
- `attribute`: section 9.4. The layer and the decision that own a wrong
  cell or an axis, and every attribution to a decision run by building
  again.
- `scorer`: a candidate on a case; arm S and arm C; stage C (the chain)
  and stage T (table decisions on the ADaM of gold).
- `defects`: the planted defects of section 9.5 for the slice.
- `hand`: the study HAND01 (7 and 9 subjects) with its table by hand.
- `kit`: a generated kit as a case; `gold_problems`, `matrix_problems`,
  `sweep`, `score_kit`, `score_set`.
- `pilot`: arm S at stage T on the reference ADaM of CDISCPILOT01.
- `gate`, `command`: `specfirst gate read-1a`, `specfirst score ...`.

## How to score a candidate on a kit (for read-2a)

```python
from specfirst.score import kit as kits, report, scorer

kit = kits.load(kit_dir)                       # a folder that `specfirst gen kit` wrote
machine = kits.machine_of(root, kit)           # builds ADSL and ADAE, each vector once
assert kits.gold_problems(machine, kit) == []  # else the kit or the scorer is wrong
case = kits.case(kit, machine.catalog)         # stage C; kits.case(kit, catalog, "T")
result = scorer.run(machine, case, records, arm="R", asked=asked, unmapped=unmapped)
print("\n".join(report.lines(result)))
```

- `records` are the lines of `out/decisions.jsonl` (decision-record schema
  v0); `asked` and `unmapped` come from `reading.ask_keys` and
  `reading.unmapped_keys` on the other two files of section 11.1. The
  command line does the same: `specfirst score kit DIR --decisions FILE
  [--questions FILE] [--unmapped FILE] [--stage T]`.
- A record of a unit that is not scored is counted and ignored. A decision
  the candidate leaves out takes the house default; one without a default
  stays open (`ae.related.values`), and the chain is then not built.
- `result.reading` has every dimension per decision (`counts("class")`,
  `counts("unit")`, `wrong()`); `result.builds[dataset]` the four scores
  (`lines()` names every denominator); `result.owners[dataset]` and
  `result.axes[dataset]` the owner of every wrong cell and axis;
  `result.silent` the wrong decisions that no cell of the case can show;
  `result.behind` those that stand behind another owner.
- The arms that need no reader: `scorer.standard_alone(machine, case)` and
  `scorer.control(machine, case)`. Arm C reads `gold/docs/sap.md` of the
  kit with the parser; gen-3a replaces that file, and a kit whose
  standard-form document has another ID needs `Case.standard_form`.
- One `Machine` keeps every build it made: a vector is built once per
  dataset. A kit takes about a second per new vector.
- A kit of another generator version than the checkout fails
  `gold_problems`: generate the kits again, never patch them.

## What the scorer says about the kits of the gate of gen-2a

Numbers are in docs/reports/read-1a.md. In short:

- On each of the ten kits the gold decisions, built again, give the files
  of the kit, and arm C scores 100% in both stages.
- Arm S builds nothing on the chain in any kit (below). At stage T it
  gives between 0 and 25 of the 15 to 30 gold cells of a kit's twin: the
  report has the line of every kit. That is the floor arm R is compared
  with.
- Every decision of every kit, read as each other value of its matrix,
  is found by the reading score, shown on the twin exactly where the
  matrix says, and attributed to that decision in every wrong cell.

## Open

For the owner (docs/decisions/ADR-008.md, "For the owner"):

- How this part reads the text of its gate: which planted defects apply
  to the slice, and what "detected" means on a kit that cannot show a
  decision.
- Arm S builds nothing on the chain. `ae.related.values` has no house
  default in `catalog@1`, ADAE needs it, and ADR-005 says that what cannot
  be built without a decision counts as not produced. So "R against S" on
  the chain compares with zero in every study. A default for that
  decision, or an ADAE that builds without it, is the std track's.
- The sweep of the matrices is a check of the gate that its text does not
  ask for.
- The crosswalk of the pilot rows.

Not done, and not part of read-1a:

- The three layers of ADaM scoring of section 9.3 (variables that reach a
  printed number, used but not printed, conformance only): they need all
  four table families. `build.adam_differences` compares every column.
- The cost dimension of section 9.2 (read-2a: the run record).
- Citations into natural-form documents: the span of an anchor is read
  from a standard-form line (`reading.Documents.span`); gen-3a decides how
  a natural-form document marks its anchors.
- `asks` and `unmapped` have no gold in a kit of gen-2a: no decision has
  the status `asked`, and no kit lists what the catalog lacks. Both rates
  are computed and are "none to judge" until gen-3a writes such kits.
- The inclusion dimension of section 9.2 beyond outputs (datasets,
  variables, analyses) is not reported as precision and recall.
- Two wrong decisions can cancel in a table (docs/state/gen.md); the
  scorer attributes one owner per cell and lists the other as `behind`
  only when it shows alone.

For other tracks:

- std: `ae.related.values` without a default (above). The pilot shows
  three rows that `tfl.ae.summary.rows` cannot name: related serious
  events, related events leading to death, events leading to dose
  modification (ADR-005, "For the owner", item 3).
- std, gen: the 22 decisions of the slice do not compile alone with the
  full house standard. `date.studyday.origin` writes into ADVS, so ADVS
  needs every decision of mod-bds-visits (lesson 50). A kit builds from a
  view of the house with ADSL and ADAE; HAND01 holds the decisions of
  mod-bds-visits.
- gen: the visible data of every kit of the gate set hold every causality
  value, so "a frozen list" can be planted only with visible data that
  lack one value (ADR-008, decision 7). A kit whose visible data lack a
  value the twin has would show it as it is.
- gen: when `GENERATOR` changes, the unit tests of the scorer write their
  kit again and assert nothing that depends on its seed.

## Next

- read-2a (needs read-1a and gen-3a): task builder, adapter, isolation,
  canary scan, run records; the `core-reader` skill and reading notes v0;
  the three arms. Then the report docs/reports/slice-ae-summary.md. It is
  not a delivery.
- Then the rest of read-1 Scorer (needs real-3 for fixtures, then gen-2),
  read-2 (needs gen-2) and read-3 (D3, node N3).

How to run things:

- `specfirst score hand --arm C` (or `--arm S`, `--stage T`,
  `--decisions FILE`), `specfirst score defects`, `specfirst score pilot`.
  The first two need neither the fetch cache nor R; a run takes seconds.
- `specfirst gen kits --seed gen-2a --count 10 --out DIR` writes the kits
  of the gate, each twice (P1). `specfirst.score.gate.write_kits` writes
  each once, four at a time: a minute and a half. `specfirst score kits
  DIR` is what the gate runs on them (half a minute per kit on the Linux
  file system, a minute from the worktree on `/mnt/d`); `specfirst score
  kit DIR/kit-001` scores one kit.
- `specfirst gate read-1a` takes about 9 minutes on a clone in the Linux
  file system: 3 and a half for the unit tests, 4 and a half for the kits.
  Wrap a gate, a test suite or a build of kits in `flock
  /run/lock/specfirst-heavy.lock <command>` (lesson 32).
- A gate of a commit runs on a clone (lesson 28). On this machine a clone
  in the Linux file system that uses the environment of the worktree is
  four times faster than the worktree on `/mnt/d`; it is not the clean
  clone of `scripts/clean_clone_gate.sh`.

## Handed over by base-0

- The planted-defect pattern of rule R5 is in use already:
  `tests/unit/test_evidence_checks.py` and the invalid examples in
  `standard/schemas/examples/`.
