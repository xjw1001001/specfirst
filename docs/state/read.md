# Track read

Result: scorer, harness, reader agent, first scores (PLAN.md section 13.6),
first for the slice "adverse event summary first" (ADR-005).

## Passed

- adr-017 (2026-11-20): carries out ADR-017, which the owner approved for
  the slice only (2026-11-19). A kept dry run of arm R is bound by bytes to
  everything the reader of the slice reads and the check scores or scans
  against, and by version to the method registry (the entries the slice
  reaches on kit 4 of the gate seed: `count.subjects`, `percent.subjects`,
  `display.pattern`, `display.round.half_away_from_zero`) and to kit.yaml
  without `pins`; its outputs are written again from its transcript and
  tied to the record (K4 of the real-5a review). New: `harness/binding.py`,
  binding.json beside every kept run (`runs.keep`), `runs.held`,
  `specfirst run bind` (decision 6, no model call), the plants of decision
  7 in the gate read-2a. R-task-04119188ff71 has its binding.json. A new R
  or pyarrow still makes the run stale (ADR-017, "Found while carrying it
  out"); the owner keeps it so (2026-11-20, "Open"). Report:
  docs/reports/adr-017.md. Review:
  docs/reports/adr-017.review.md (signed in pass 2; pass 1 found F1, the
  engines, and F2, a check without a plant of its own, both fixed). The
  gates read-2a (19 of 19) and read-1a (14 of 14) passed on clean clones
  of `13b946e`. Model use: none. real-5b may merge once this is on `main`
  (the owner's answer).

- slice-ae-summary (2026-11-19): the report of ADR-005, decision 1, last
  paragraph: the first scores of the slice on four dev kits (kits 5, 6, 7
  and 15 of a dev seed whose file lies outside every checkout), arms S, R
  and C at stages T and C, and the pilot of decision 5 (stage T on the
  reference ADaM of CDISCPILOT01, arms S and R, arm R reading the real
  SAP). Not a delivery: N3 applies first. Report:
  docs/reports/slice-ae-summary.md. Review:
  docs/reports/slice-ae-summary.review.md (signed in its third pass; pass
  1 found a decision of a dev kit named with its gold class, pass 2 the
  same pairing in unpushed commits, both fixed before anything was
  pushed). Choices: docs/decisions/ADR-016.md. The owner's answers
  (2026-11-19, relayed by the base session): the first scores stand with
  the limit stated that 8 of the 66 decision paragraphs are the phrasing
  template (Q2); no more runs (Q3). The gates read-2a and read-1a passed
  on clean clones of `0a58979` (this part with `main` `548c0f5` merged in).
  Nine runs of arm R, USD 4.05 computed from the tokens, within the
  owner's USD 10. No run folder, task, transcript or log of these runs is
  in the repository (ADR-016, decision 4); the report holds their numbers
  and command output, values of dev kits withheld. Kits, logs and the
  pilot folder lie in WSL `/root/scratch-slice/`, the seed files in
  `/root/specfirst-secrets/slice-ae-summary/`, tasks and runs in a folder
  of drive C outside every checkout. New: `specfirst run pilot`,
  `specfirst score pilot --run` (`harness/pilot.py`, `task.render_real`,
  arm R in `score/pilot.py`).

- read-2a (2026-11-18): the reader harness for the slice. The task builder,
  the oracle (`specfirst ask`), the canary scan, run records with cost, the
  adapter (`claude -p`, CLI 2.1.327 on the owner's subscription) and a stub
  reader, the arms S, R and C on one run folder and record; `core-reader`
  and the reading notes v0 of the four units (skills/); the gate
  `read-2a`. Report: docs/reports/read-2a.md (the gates on clean clones,
  the isolation probe, the dry runs and their cost, the limits, the M1
  isolation limit first). Review: docs/reports/read-2a.review.md (signed in
  its second pass). Choices: docs/decisions/ADR-010.md. The owner approved
  decision 9 (the gate checks the kept dry run of arm R from its record)
  and accepted decision 5 (the canary scan), each for the slice only, and
  logged in the CLI. The dry run of arm R and the isolation probe are kept
  in src/specfirst/harness/kept. Model use of the part: USD 1.24, computed
  from the tokens.

- read-1a (2026-11-18): the scorer for the slice. Reading score, build
  score with the four scores of ADR-005, decision 4, attribution, the arms
  S and C, the planted defects of section 9.5 that apply to the slice; on
  a hand-made study, on the pilot (report only) and on the ten kits of the
  gate of gen-2a; the gate `read-1a`; `specfirst score ...`. Report:
  docs/reports/read-1a.md (the gate on a clean clone of `a95d9a9`, its
  numbers, the pilot table, the limits). Review:
  docs/reports/read-1a.review.md (signed in its second pass). Choices:
  docs/decisions/ADR-008.md; the owner approved its reading of the gate
  text, for the slice of ADR-005 only.

## What exists (`src/specfirst/score/`; each module says what it does)

- `reading`: the reading score of section 9.1, by class and by unit.
- `build`: the four scores of ADR-005, decision 4, each with its
  denominator, for the visible data and for the twin.
- `candidate`: a decision vector built on a dataset, as gen-2a builds the
  gold of a kit (listed groups, `specfirst.gen.display`). A `Build` is
  what the rest of the scorer reads.
- `attribute`: section 9.4. Every layer with a difference on the path of
  a wrong cell makes a claim; a claim is run by building again, and the
  owner is a claim that held (ADR-008, decision 5).
- `scorer`: a candidate on a case; arm S and arm C; stage C (the chain)
  and stage T (table decisions on the ADaM of gold).
- `defects`: the planted defects of section 9.5 for the slice.
- `hand`: the study HAND01 (7 and 9 subjects) with its table by hand.
- `kit`: a generated kit as a case; `gold_problems`, `matrix_problems`,
  `sweep`, `score_kit`, `score_set`.
- `pilot`: arms S and R at stage T on the reference ADaM of CDISCPILOT01.
- `gate`, `command`: `specfirst gate read-1a`, `specfirst score ...`.

`src/specfirst/harness/` (read-2a, ADR-010; each module says what it does):
`task` (the task folder), `knowledge` (core-reader and the reading notes,
skills/), `oracle` (`specfirst ask`), `outputs` (the validity of out/),
`canary` (the scan), `record` (cost and budget), `adapter` and `stub` (the
CLI and its stand-in), `runs` (a run of an arm, the probe, a kept run and
its check), `binding` (what a kept run is bound to, by bytes and by
version, and its outputs written again from the transcript; ADR-017),
`gate`, `command` (`specfirst run ...`), `pilot` (the pilot as a task of
stage T, ADR-016); `kept/` holds the dry run of arm R with its
binding.json, and the probe.

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
- A record of a decision that gold makes in a unit that is not scored is
  counted and ignored. A record of a decision that gold does not make
  (another unit, a unit the catalog does not have) is listed, and the
  reading score is then not perfect. A decision the candidate leaves out
  takes the house default; one without a default stays open
  (`ae.related.values`), and the chain is then not built. Since ADR-014
  (std track, approved 2026-11-18) the build leaves out only what such a
  decision binds: its gold cells are pending (`result.pending`, a line
  "pending" in the build score), counted apart, and the rest is scored.
- `result.reading` has every dimension per decision (`counts("class")`,
  `counts("unit")`, `wrong()`); `result.builds[dataset]` the four scores
  (`lines()` names every denominator); `result.owners[dataset]` and
  `result.axes[dataset]` the owner of every wrong cell and axis;
  `result.silent` the wrong decisions that no cell of the case can show;
  `result.behind` those that stand behind another owner.
- An owner has `layer`, `element`, `decisions`, `confirmed` and `note`.
  `confirmed` True: with these decisions at their gold values the cell has
  the gold text; they are the fewest among the decisions that the claims
  name, so two decisions mean that neither is enough (`note`: JOINT, or
  HIDDEN when another wrong decision hides one of them). None: no
  decision is named (a step of the build). False: a claim that failed
  when it was run; read it as "no owner was found" and count it apart.
  The lines of a kit do (`kit._owned`); `report.lines` prints such a
  claim in the line of its layer and decision, as "confirmed 6 of 20". It
  can happen only where a step of the build was changed: without that the
  gold decisions give the gold text. A table of errors by unit and layer
  takes the first decision of an owner as its unit.
- `scorer.run(..., prove=False)` runs no claim: fast, and every owner is
  the far-end claim, unconfirmed. Do not report owners from it.
- The arms that need no reader: `scorer.standard_alone(machine, case)` and
  `scorer.control(machine, case)`. Arm C reads `gold/docs/sap.md` of the
  kit with the parser; gen-3a replaces that file, and a kit whose
  standard-form document has another ID needs `Case.standard_form`.
- One `Machine` keeps every build it made: a vector is built once per
  dataset. A kit takes about a second per new vector.
- `kits.load` holds the files of a kit against the hashes of its manifest
  and refuses a kit that differs. A kit of another generator version than
  the checkout fails `gold_problems`: generate the kits again, never patch
  them.

## What the scorer says about the kits of the gate of gen-2a

Numbers are in docs/reports/read-1a.md. In short:

- On each of the ten kits the gold decisions, built again, give the files
  of the kit, and arm C scores 100% in both stages.
- Arm S builds nothing on the chain in any kit (below; superseded by
  ADR-014: arm S now builds the chain, and the cells of the row of related
  events are pending, docs/reports/std-issues.md). At stage T it
  gives between 0 and 25 of the 15 to 30 gold cells of a kit's twin: the
  report has the line of every kit. That is the floor arm R is compared
  with.
- Every decision of every kit, read as each other value of its matrix,
  is found by the reading score, shown on the twin exactly where the
  matrix says and in as many cells, and attributed to that decision at
  its layer in every wrong cell. With two wrong decisions (120 pairs of
  a module decision with a table decision) every wrong cell is owned by
  the decision that changes it alone, or by both where each does.

## From catalog-2c (std track, 2026-11-21)

The slice moved to version 2 of the standard (ADR-020, decision 8 as
amended); the std track made the change in the files of read, which this
track left alone meanwhile. Report: docs/reports/catalog-2c.md.

- The scorer takes the features of the study's design (`Case.features`,
  `candidate.vector(..., features)`): a default of open-default@2 may depend
  on the design (`pop.safety.rule`). A kit's case gives its design's
  features; HAND01 has `hand.FEATURES`.
- HAND01 states two decisions of the slice: `ae.related.values` and a total
  column over all arms (the house has none; the planted defect S5 leaves
  the total column out). Its table has the six standard rows of catalog@2
  (28 cells), worked out again by hand; mutation finds ten decisions it
  cannot show (the grouping of the safety set is the tenth).
- The checks of read-1a on HAND01: the control plants the list of related
  causality values ("PROBABLE" in place of "POSSIBLE", "PROBABLE"); arm S
  leaves the six cells of the two rows of related events waiting and the
  seven cells of the total column to `tfl.columns.total`.
- The reader's skills render the house defaults of open-default@2 (a
  default by design names its cases); TASK.md and the core-reader skill
  describe the anchors by entry ID, the cases and the fixed rules.
- The kept dry run of arm R is `R-task-b6706bdac1d8` (kit 4 of the gate
  seed, catalog@2), in place of `R-task-04119188ff71`.
- The pilot task of ADR-016 takes catalog@2: the real kit names no catalog
  version (BACKLOG i28.real-kit-pins waits for real-4).

## Open

For the read track, from the owner (2026-11-19, relayed by the base session
in real-5a). The binding of a kept run to versions (K5, the owner's choices
item 1) and K4 are settled by ADR-017 and the part adr-017 ("Passed").

- Review of adr-017, F1: ADR-017 as approved frees a kept run from
  yamaa's version only. R's version also stands in kit.yaml's
  `properties`, and pyarrow's in every Parquet file. The owner keeps it as
  it is (2026-11-20, relayed by the base session; ADR-017, "The owner's
  answer on R and pyarrow"): when R or pyarrow really is upgraded, the dry
  run of arm R is made again, once (about USD 0.6), and kept with
  `specfirst run arm KIT --arm R --keep`. Freeing R or pyarrow is not
  taken.

- Review of real-5a, K3: the kept transcripts hold the CLI's
  `rate_limit_event` (the subscription's usage, no credential). The owner
  keeps it as it is (2026-11-19, relayed by the base session): `runs.keep`
  need not drop it.

From the review of read-2a (docs/reports/read-2a.review.md), not blocking:

- H10, before read-3 relies on the scan: a list slot filled with texts the
  task holds still takes most canary pieces of a twin Dataset-JSON row out
  of the scan (38 of 58 over 30 rows; no row lost all of them). What
  settles it: the reader's own statements stop counting for the slack of
  16 characters, or a row-shaped candidate is held whole.
- H12: the record's `reader.deny` lists the folders denied to every file
  tool and not the rule on `bin/` (Edit and Write only); and
  `runs.tool_writes` counts a write of `bin/` even when the CLI denied it
  (strict; `specfirst run check` on the kept probe fails for it, and for the
  probe's budget and missing files, and the gate does not check the probe).

- H8: the reader is never told the status `conflict`, which PLAN.md 4.3
  and 9.1 score; TASK.md and core-reader name three statuses. No kit of the
  slice has a conflict. For the part that first writes a kit with one; a
  change of TASK.md or core-reader gives another task, so the dry run of
  arm R is made again with it.
- H6: whether the CLI keeps a file tool inside the working directory is not
  shown (the probe names only denied paths); a probe step on a harmless
  file beside the task, with a planted canary, would show it (model use,
  the owner's to want).

From the review, booked for the rest of read-1 (they did not block;
docs/reports/read-1a.review.md, findings R8 and R9):

- Where more than one decision is wrong, nothing holds the layer of an
  owner (the sweep of pairs holds the decisions of an owner and that the
  claim held), and nothing holds that an owner has no decision too many.
  In the reviewer's runs both were right: 8,590 owners of one decision,
  each at the layer of its decision, and no owner with a part that would
  do. What settles it: the pairs held against `kit.OWNING_LAYER`, and a
  test with three wrong decisions whose owners are worked out by hand.
- The decisions of an owner are the fewest among those that a claim
  names. A wrong decision that no claim names (the gold table does not
  read what it sets, the candidate's table does) is tried only when the
  named ones fail. In 7 of 8,445 wrong cells and axes of the reviewer's
  312 candidates with two to four wrong decisions, one such decision
  alone would have done, and the owner was two others together. Both are
  true. What
  settles it: every wrong decision is tried alone before two are taken
  together.

For the owner (docs/decisions/ADR-008.md):

- How this part reads the text of its gate (decisions 7 and 8): which
  planted defects apply to the slice, and what "detected" means on a kit
  that cannot show a decision. Asked and answered: the last section of
  ADR-008.
- Arm S builds nothing on the chain. `ae.related.values` has no house
  default in `catalog@1`, ADAE needs it, and ADR-005 says that what cannot
  be built without a decision counts as not produced. So "R against S" on
  the chain compares with zero in every study. A default for that
  decision, or an ADAE that builds without it, is the std track's.
  Settled by ADR-014 (approved 2026-11-18): the chain is built without
  what the decision binds, and those cells are pending.
- The sweep of the matrices is a check of the gate that its text does not
  ask for.
- The crosswalk of the pilot rows.

Not done, and not part of read-1a:

- The three layers of ADaM scoring of section 9.3 (variables that reach a
  printed number, used but not printed, conformance only): they need all
  four table families. `build.adam_differences` compares every column.
- The cost dimension of section 9.2 in the scores: read-2a records tokens,
  turns, time and dollars per run (`specfirst.harness.record`); the reading
  report does not print them yet.
- Citations into natural-form documents: the span of an anchor is read
  from a standard-form line (`reading.Documents.span`); gen-3a decides how
  a natural-form document marks its anchors.
- `asks` and `unmapped` have no gold in a kit of gen-2a: no decision has
  the status `asked`, and no kit lists what the catalog lacks. Both rates
  are computed and are "none to judge" until gen-3a writes such kits.
- The inclusion dimension of section 9.2 beyond outputs (datasets,
  variables, analyses) is not reported as precision and recall.
- Two wrong decisions can cancel in a table (docs/state/gen.md): a cell
  that is right by cancellation is no wrong cell and has no owner. A
  wrong decision that owns no cell at all is listed as `behind`, with
  what it changes alone.
- Three or more wrong decisions behind one cell are attributed (the
  decisions are added one by one until the cell has the gold text, then
  pruned). No check of the gate and no unit test holds that: the sweep
  has pairs, and the lines of arm S are printed, not checked. The
  reviewer ran 312 candidates with two to four wrong decisions and found
  every owner confirmed and honest (review, pass 2).
- The reading score compares a list in its order (`ae.related.values`:
  the same values in another order count as a decision to change), and a
  quote passes when it stands in the document and inside the gold anchor,
  however short it is (review, finding R4). The first is for the catalog
  to settle (ADR-008, "For the owner"); the second belongs to citations
  into natural-form documents, with gen-3a.

For other tracks:

- std: `ae.related.values` without a default (above; its effect on the
  build is settled by ADR-014, a default is still `catalog@2`'s). The pilot shows
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

- The rest of read-1 Scorer (needs real-3 for fixtures, then gen-2),
  read-2 (needs gen-2) and read-3 (D3, node N3).
- From the report slice-ae-summary, for whoever takes them up:
  - The reader read a design paragraph of the natural protocol as stating
    a decision of `mod-populations` in three of the four dev kits (which
    one is withheld: ADR-016, decision 4). No cell shows it. A change of
    the reading notes is the training loop's (M2) to propose and the dev
    kits' to accept; a design paragraph that reads like a decision may also
    be the generator's to rephrase.
  - The pilot: the real SAP plans no adverse event summary; the reader
    said so (`tfl.output.include` = `not_included`). A pilot task that
    gives the output as planned (one run of about USD 0.6) was offered;
    the owner wanted no more runs for this report (2026-11-19). It stays
    a choice for a later part (ADR-016, "For the owner").
  - Dev kits of another seed state statements the store lacks (8 of 66
    decision paragraphs here are the phrasing template; the owner accepted
    the first scores with that limit): the loop of the natural form for
    dev seeds is the gen track's (ADR-009).

How to run things:

- `specfirst score hand --arm C` (or `--arm S`, `--stage T`,
  `--decisions FILE`), `specfirst score defects`, `specfirst score pilot`.
  The first two need neither the fetch cache nor R; a run takes seconds.
- `specfirst gen kits --seed gen-2a --count 10 --out DIR` writes the kits
  of the gate, each twice (P1). `specfirst.score.gate.write_kits` writes
  each once, four at a time: a minute and a half. `specfirst score kits
  DIR` is what the gate runs on them (under a minute per kit on the Linux
  file system, two to three minutes from the worktree on `/mnt/d`);
  `specfirst score kit DIR/kit-001` scores one kit.
- `specfirst gate read-1a` takes about 14 minutes on a clone in the Linux
  file system (the log of `a95d9a9`: 805 seconds, 254 of them the unit
  tests and 509 the kits). Wrap a gate, a test suite or a build of kits
  in `flock /run/lock/specfirst-heavy.lock <command>` (lesson 32).
- A gate of a commit runs on a clone (lesson 28). On this machine a clone
  in the Linux file system that uses the environment of the worktree is
  four times faster than the worktree on `/mnt/d`; it is not the clean
  clone of `scripts/clean_clone_gate.sh`.

## Handed over by base-0

- The planted-defect pattern of rule R5 is in use already:
  `tests/unit/test_evidence_checks.py` and the invalid examples in
  `standard/schemas/examples/`.
