# Track real

Result: CDISCPILOT01 end to end: ADaM proof, result engines, grids and
viewer, the 30 CSR tables (PLAN.md section 13.3).

## Passed

- real-1 Kit and ADaM proof. Gate: `specfirst gate real-1 --clean` exited 0
  on a clean clone of commit `6e6a2ce` (2026-11-11). Evidence:
  docs/reports/real-1.md and real-1.gate.log. Review:
  docs/reports/real-1.review.md. Decisions: docs/decisions/ADR-001.md.
- real-2 Result engines. Gate: `scripts/clean_clone_gate.sh real-2` exited
  0 on a clean clone of commit `1e0f164` (2026-11-11). Evidence:
  docs/reports/real-2.md and real-2.gate.log. Review:
  docs/reports/real-2.review.md (PASS, twelve findings that do not block).
  Decisions: docs/decisions/ADR-002.md. The findings F2 to F12 are fixed in
  commit `bd34260` (2026-11-17), and `specfirst gate real-2 --clean` exited
  0 on a clone of it (the report of real-3a will hold the log).

## In progress: real-3a (ADR-005, decision 1)

The work is on `track/real` at `faa8a5f`, pushed, three commits on top of
`main` (`f42a3fa`). It is not merged and has not passed its gate.

Done, and how it is known:

- `bd34260`: the findings F2 to F12 of the review of real-2.
  `specfirst gate real-2 --clean` exited 0 on a clone of this commit, 15 of
  15 checks, with the installed environment and the existing fetch cache
  (2026-11-17, 10:57).
- `4f7e581`, `faa8a5f`: ADR-003, layout spec v0, the grid builder, the mock
  shell, the page, the comparison with the example's formatted values, the
  trace of the cells, the gate `real-3a`, the planted defects D6 to D8.
  `specfirst check cdiscpilot01` on a build of the working tree before
  these commits: 27 cells show 51 results, all 27 equal the example's
  formatted values, and 27 of 27 cells reach SDTM columns. The tests D6 and
  D8 passed in the worktree. D7 saw every planted case but one (the cells
  of a row in another order, which the check of the form of a grid sees and
  the comparison of texts does not); the test now judges a grid file as the
  gate does, and has not run since.
- CI on `faa8a5f` (run 44126884475): 756 passed, 19 skipped (no R on the
  runner), 22 deselected; lint clean; ASCII check on 387 files.

Not done:

- `specfirst gate real-3a` has not run to its end on any commit, and
  `scripts/clean_clone_gate.sh real-3a` has not been started. From 11:16 on
  2026-11-17 the Ubuntu instance of WSL was terminated every 30 to 120
  seconds, after the virtual machine had run out of memory with three
  sessions testing at once; from about 10:35 it reached no network. Both
  are for the owner to repair: a session may not restart WSL or change a
  system setting.
- The report docs/reports/real-3a.md, the review (rule R7), the merge to
  `main`.

To go on, once WSL is stable (one heavy run at a time: wrap it in
`flock /run/lock/specfirst-heavy.lock`; at most four worker processes):

1. Merge `main` into `track/real` again (std-1 freezes `catalog@1`).
2. `scripts/clean_clone_gate.sh real-3a` needs the network. Without it,
   the gate can be run on a clone with the installed environment
   (`git clone --no-local`, check out the commit, source the worktree's
   `scripts/env.sh`, then in the clone
   `PYTHONPATH=<clone>/src python -m specfirst gate real-3a --clean`), so
   that report and review can go on; whether that may stand for the
   clean-clone gate is the owner's decision (PLAN.md section 2.3). No merge
   before that.
3. Report with the gate log, review by a fresh-context agent, this file,
   merge, push, CI.

## Open

For the owner, from real-3a (ADR-003 and docs/reports/real-3a.md say each
in full):

- The layout is our own format, not tfrmt JSON (ADR-003, decision 1). tfrmt
  was read at a pinned commit and not run: it is not among the locked R
  packages. Its rounding was run in base R: it changes 2 results of the
  pilot, and the example agrees with the registry on both.
- A count under a column header is a cell of a row with the section
  `@header`, because grid schema version 0 has no place for a result in a
  column (decision 4). A field for it is a schema change, which is the
  owner's.
- The registry has a new entry, `display.pattern`. Three of its statements
  are read off the formatted values of CDISC's example; no public standard
  states them (decision 3).
- The kit layout of section 8 has grown again: `gold/layout/` in the kit
  folder and in the build, `outputs` under a result set in kit.yaml, and the
  mock shell next to the grid in `gold/grid/` (decision 7).
- The comparison of grid text is per result: the example formats results,
  not cells. The order of the parts of a cell is the layout's alone, and no
  check can hold it against this reference (decision 5).
- The median of height had a proof of the kind the review of real-2 found
  (F2), although the review said no entry had one. It has a new kind of
  proof now, `between_equal_values`. The class is unchanged.

For the owner, from real-2 (ADR-002 and docs/reports/real-2.md say each in
full); none of these changed in real-3a:

- The R engine is our own and takes its arithmetic from R's `stats`
  package. It does not go through cards and cardx, which section 7.1 names,
  and it is neither of the two ways section 13.3 gives. ADR-002 is reworded
  as the review asked (F8); the choice is the owner's.
- 25 results of CDISC's ARS example need a class, not the 24 of evidence
  E3. 3,711 are reproduced as the plan counts, 3,710 at the precision the
  check asks for (F1). With R's quantile definition 97 results differ, not
  the 49 of E4. PLAN.md is not changed; its numbers (E2 to E4, the gate text
  of real-2, section 14) are the owner's to revise.
- All 25 are classed `reference_error`; the classes are the executor's
  reading. The review finds 24 well supported and the empty Fisher p-value
  the weakest (F9).
- docs/upstream/ars-issue-common-safety-displays.md is the draft of the
  issue for the ARS repository. It is not posted; it needs the owner's
  approval of the exact text (section 2.1, rule 6).
- The additions of ADR-002 (decision 5) to the kit layout of section 8.
- The R library has no Parquet and no YAML reader. The R engine is handed
  JSON instead. Adding a reader changes env/ for every track at once.

Settled:

- Item 3 of ADR-001 (`gold/reference/`, `gold/claims/`, `gold/resolved/`
  and `gold/build.json` in the kit layout of PLAN.md section 8): approved by
  the owner on 2026-11-11. ADR-001 records it.

What the fixes of F2 to F12 left as it was:

- F5, three rows of the review's table that are floating arithmetic at its
  limits (the mean of 1e20, 1 and -1e20; two analyses of variance whose
  groups differ by 1e9 or by one rounding). The engines differ there, and
  rule R11 stops the build; nothing is silent.
- F1, F8 (the choice itself) and F9 (the classes) are the owner's.

Other open points:

- Layout spec v0 has two kinds of block (`header`, `analyses`). The other
  four outputs of the example need more (see "Next").
- A difference of display has no class yet. The exceptions file has no
  section for cells: a cell that differs takes the class of the result it
  shows, and any other difference blocks the gate until a proof kind
  exists (ADR-003, decision 5).
- The method registry and the layout are checked by code, not by schemas in
  standard/schemas/ (section 12 lists one for the registry). Each needs an
  ADR the owner approves.
- P2 for results sees what a reference embeds. The 504 results of ours that
  CDISC's example does not list are covered by the agreement of the two
  engines and by the rows per analysis that test A6 asserts (F6).
- What the pilot data cannot show (tests/defects prints these on every
  run): the safety set and the intent-to-treat set hold the same 254
  subjects; for 3 of the 18 analyses with a data subset, dropping it changes
  nothing the reference lists; no result of the adverse event summary lies
  on a half, so the rounding rule cannot be told apart on that grid. From
  the review of real-2 (F11): no analysis variable of a count is missing; no
  column under NE has a missing value; every chi-square table is larger than
  2 x 2; every Fisher table is 2 x 2, so for "exact beyond 2 x 2" the ten
  vectors are the whole evidence in the gate.
- The 706 `cites` edges imported from Pilot 7's claims are candidates: no
  quote is checked against its document and no one has approved one. The
  rest of real-3 completes the graph to the documents. One edge stands for
  all citations of one span by one column (913 citations, 706 edges).
- The v0 edge schema cannot carry the role of a `reads` edge (variable,
  set, subset, grouping, key) or tell a value dependency from a filter in a
  `derives_from` edge; coverage.json has both. If the viewer needs them per
  edge, it is a schema change (an ADR the owner approves).
- P1 is tested with yamaa's Python host only; its R host is not installed.
- The kit manifest is checked by code, not by a schema in
  standard/schemas/ (ADR-001, item 3). gen-2 writes kits too: agree on the
  format with it before a schema is proposed.
- The pilot's protocol is not in the kit.

## Next

- The rest of real-3 Grid, trace, viewer, with the gate PLAN.md gives it:
  the other four outputs of the example as grids, the citations through the
  ARS `documentRefs`, the viewer. It runs the code of real-3a on more
  outputs: add each to `outputs` in kit.yaml with a layout in
  `kits/cdiscpilot01/gold/layout/`, and to `PILOT_GRIDS` in gates.py.
- Then real-4 (D1, node N2), real-5 (D2, node N2), in order.

What the rest of real-3 will meet (measured in real-3a, on all 3,734
formatted values of the example; the display rule gives the example's text
for 3,580 of them):

- 24 differ because the result itself has a classified difference: their
  cells take that class without a new entry.
- 130 differ by display only, none of them in the adverse event summary:
  125 minima and maxima that the example shows with the decimals of the data
  under the pattern `XX`; 4 medians of the vital signs where our value is a
  half only up to floating error (0.05 computed as 0.04999...), shown as
  " 0.0" where the example has " 0.1"; and one p-value of 1 that the example
  shows as "1" under `X.XXXX`. Each needs a rule in the registry or a proof
  kind for a difference of display.
- Layout kinds that do not exist yet: one row per group of a row grouping
  (defined groups for demographics; data-driven and nested for organ class
  and term), one row per statistic, columns that compare two groups
  (p-values), a total column, sort and threshold rules. The plan of a grid
  (`grid.plan`) is the place: the builder, the comparison and the trace all
  read the plan.
- Display rules that are not registry entries yet: p-value formats and the
  truncation of long terms (E25).

## Handed over by real-3a

- `specfirst build cdiscpilot01` now also writes, per output the kit lists:
  `gold/grid/<output>.json` (the grid), `gold/grid/<output>.shell.json` (its
  mock shell) and a page for each in `gold/out/`. The graph gets the cells,
  the ARD rows they show and their analyses (`shows`, `computes`, `reads`).
  `specfirst check cdiscpilot01` adds the check of the grids, and its trace
  part walks every cell to SDTM columns.
- A layout is a YAML file of our own, layout spec v0: every key is described
  in the docstring of `specfirst.machine.layout`; ADR-003 has the reasons.
  What the ARS file holds is taken from it (titles, footnotes, labels, group
  names, result patterns) unless the layout says otherwise.
- A cell ID is `cell:<output>/r<n>/c<n>`; the node of an analysis is
  `ars:<analysis ID>`. A count under a column header is a cell of the row
  with the section `@header`.
- `grid.compare_reference` is P2 for grid text. It needs the classes of the
  results (`results.judge_entries`), so a result that differs must be
  classified first.
- `display.pattern` is the registry entry for a result pattern; a new
  display rule is added as real-2 describes for a method.
- A new check of a graph layer needs a test against what executes
  (lesson 16): tests/defects D8 holds `shows` against the grid builder and
  `reads` against the engine. A static walk cannot see an edge that was
  never recorded.
- A reference can only show what it holds (lesson 29): sort a planted
  defect that passes by what the reference could have shown.
- Gates of a commit are run in a clone (lesson 28). On this machine a clone
  on the Linux file system ran the gate of real-2 in about 5 minutes; the
  worktree on the Windows drive takes several times as long.

## For other tracks

- std-2: ADR-003 has a table "from layout draft 0 to version 0" for the four
  house layout templates. A compiled ARS file has no result pattern, so a
  compiled layout names a pattern for every part; a data-driven treatment
  grouping needs `columns.values` in the order the decision gives, and a
  mock shell cannot be built without it.
- gen-2a, read-1a: `grid.build(event, layout, rows)` gives the grid of one
  output from an indexed reporting event, a layout and the ARD rows by ID;
  `grid.shell` gives the mock shell without rows. The two axes and the cell
  texts of a grid are what section 9.2 scores as structure and values. The
  builder shows an analysis whose only grouping is the column grouping; the
  compiled adverse event summary fits that (one analysis per row, the
  treatment grouping, and `An_AESUM_N` for the header).
- std: the ARS file compiled from the base decision vector of std-1 (44
  analyses) has no problem for `specfirst.machine.ars.index` and binds
  completely: `Mth_Count` and `Mth_ContSumm` by their description
  `Method registry: <id>` (rule B2), `Mth_CatSumm` by the names of its
  operations (rule B3), and `quantile_definition` from `programmingCode`
  with the context `specfirst method registry`. A test's method is bound
  by its description too (rule B2).
  Registry v0 has no `count.records`: `Mth_EventCount` cannot run until an
  entry exists. Data-driven treatment groupings work, for descriptive
  results and for tests. The engines have not been run on the tiny study.
- Every track: a condition value in an ARS file must be text, and a number
  in it is written as in JSON (rule I3); `ars.index` reports any other.
- gen, read: a kit with a reporting event names it under `results` in
  kit.yaml (ADR-002, decision 5), and the outputs to build under its
  `outputs` (ADR-003, decision 7); the engines read the ADaM datasets of the
  build.

## Handed over by real-2

- `specfirst build cdiscpilot01` writes, per reporting event of the kit:
  `gold/ard/<id>.jsonl` (the Python engine: the gold ARD),
  `gold/ard/<id>.r.jsonl` (the R engine) and `gold/ars/<id>.json` (the ARS
  file with our results as raw values). The build needs R.
  `specfirst check cdiscpilot01` adds P2 for results and rule R11.
- An ARD row is identified by `id`:
  `ard:<analysis>/<operation>/<one part per grouping>`.
  standard/methods/README.md has the format, the rules I1 to I15 an analysis
  is run by, and the rules B1 to B3 that bind an ARS operation to the
  registry.
- `specfirst.machine.ars.reads(event, analysis_id, subject_key)` gives what
  an analysis reads, by role (variable, set, subset, grouping, key): the
  `reads` edges of section 4.2. The example reads 23 columns of ADSL, ADAE
  and ADVS (E5).
- A new method: an entry in standard/methods/ with numbered semantics,
  vectors in tests/methods/ (and `oracle.py` if it can be computed
  exactly), a function in `specfirst/machine/methods.py` and one in
  r/specfirstr/R/methods.R, a branch in both engines, then
  `specfirst methods --write`. Add statements of semantics at the end:
  vectors cite them by number. A display rule has a Python function only.
- A new reference with results: its differences go to the kit's
  gold/exceptions.yaml, each with a proof kind that
  `specfirst.machine.results` checks. A proof kind that is missing is added
  there, with a planted defect in tests/unit/test_results.py and, on the
  real entries, in tests/defects (D6).
- A planted defect that passes is not yet a hole: tests/defects D4 sorts
  such cases by what the defect changed (lesson 24). Do the same before
  trusting or blaming a checker.

## Handed over by real-1

- `specfirst build cdiscpilot01` writes the 10 ADaM datasets as canonical
  Parquet into build/kits/cdiscpilot01/gold/data/adam/; the result engines
  read them from there, not from the fetch cache. `specfirst check
  cdiscpilot01` proves they equal the reference.
- `specfirst.machine.canonical` has the writers for JSON, JSONL and
  Parquet; every built file goes through it (P1).
- The graph is in gold/graph/ (nodes.jsonl, edges.jsonl, coverage.json).
  ADaM node IDs are `adam:<DATASET>.<COLUMN>`.
- A new work package adds its gate to `GATES` in src/specfirst/gates.py and
  its cache-dependent tests under tests/ with the marker `evidence`.
- Reading or importing anything from the fetch cache must leave it
  untouched (lesson 13): the gate verifies the cache again at its end.
- Code taken over from a cached source, even retyped, goes into
  third_party/SOURCES.md with its license (lessons 12 and 14); the test
  A5-adapted of tests/pilot looks for what was not recorded, in Python and
  in R files.
- A static check of the graph cannot see a reference the analysis missed.
  tests/pilot A4-unread tests the pilot graph against the engine; a new
  graph layer needs a check of that kind (lesson 16).
