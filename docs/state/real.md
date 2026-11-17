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
  Decisions: docs/decisions/ADR-002.md.

## Open

For the owner, from real-2 (ADR-002 and docs/reports/real-2.md say each in
full):

- The R engine is our own and takes its arithmetic from R's `stats`
  package. It does not go through cards and cardx, which section 7.1 names,
  and it is neither of the two ways section 13.3 gives. The review finds
  the decision not to wrap siera proven by the trial and the decision
  against cards and cardx a choice; four sentences of ADR-002 say more
  than its evidence (review finding F8; the report says what they should
  say).
- 25 results of CDISC's ARS example need a class, not the 24 of evidence
  E3: one first quartile ("70" against 70.5) was hidden by the spike's
  tolerance. That result is counted as reproduced as printed and as a
  difference: 3,711 as the plan counts, 3,710 at the precision the check
  asks for (F1). With R's quantile definition 97 results differ, not the
  49 of E4. PLAN.md is not changed; its numbers (E2 to E4, the gate text of
  real-2, section 14) are the owner's to revise.
- All 25 are classed `reference_error` in
  kits/cdiscpilot01/gold/exceptions.yaml; the classes are the executor's
  reading. The review finds 24 well supported and the empty Fisher p-value
  the weakest: closer to a difference of rule than to a contradiction
  (F9).
- docs/upstream/ars-issue-common-safety-displays.md is the draft of the
  issue for the ARS repository. It is not posted; it needs the owner's
  approval of the exact text (section 2.1, rule 6).
- The kit layout of section 8 has grown again: `results` and
  `build.exceptions` in kit.yaml, `gold/spec/ars/`, `gold/ard/`,
  `gold/ars/`, and `gold/exceptions.yaml` in the kit folder in git
  (ADR-002, decision 5). The owner's approval of 2026-11-11 is for the
  additions of ADR-001 and does not cover these.
- The R library has no Parquet and no YAML reader. The R engine is handed
  JSON instead. Adding a reader changes env/ for every track at once (all
  checkouts share one R library); it is not done.

Settled:

- Item 3 of ADR-001 (`gold/reference/`, `gold/claims/`, `gold/resolved/`
  and `gold/build.json` in the kit layout of PLAN.md section 8; finding F12
  of the review of real-1): approved by the owner on 2026-11-11. ADR-001
  records it.

Findings of the review of real-2, none blocking, for the first commit of
real-3; then run `specfirst gate real-2` again. Each is in full in
docs/reports/real-2.review.md.

- F2 `results._proof_problem` accepts proofs that prove nothing. Let
  `value_of_other_result` name a result of the same analysis and operation
  that differs in one group of one grouping; allow `same_under_every` and
  `no_alternative` only where some value of the option changes some result
  of that operation; allow `no_records` only with the counts of the cell's
  own groups, one per compared group. Plant the reviewer's cases A3, A8, A9
  and A11 as tests. Needed before real-3 compares formatted values.
- F3 `test.fisher.exact`: statements 5 and 6 describe the Python
  enumeration. R's `fisher.test` allows more than a relative 1e-7 for
  tables larger than 2 x 2 and refuses none. Say which implementation a
  statement describes; add one of the reviewer's six tables as a vector
  with the exact value; let the R implementation follow the registry for
  larger tables; catch `MethodError` in `build.build`. Needed before real-4
  (59 Fisher tests on 3 x 3 tables).
- F4 `methods.summary_continuous`: the standard deviation of equal values
  must be 0, decided by comparing the values (three values of 0.1 give
  1.7e-17 today, R gives 0). A statement and a vector.
- F5 Inputs on which the engines differ or only one stops. Read the
  hand-over in R with `simplifyVector = FALSE` and convert by kind (a text
  column whose every value is "NA" stops the build today); escape every
  control character in `json_string`; one rule for the text of a number as
  a group value, in the README and in both engines; say in rule I3 how a
  number is written.
- F6 Nothing asserts the number of rows. Assert the rows per analysis, in
  A6 or in the kit, so that a result lost in both engines shows.
- F7 `json_string` in r/specfirstr/R/util.R shares five statements with a
  function of siera, and A5 reads Python files only. Let A5 compare the R
  files with the R files of the cache; write `json_string` anew (F5 asks
  for that too), or record siera in third_party/SOURCES.md.
- F8 Reword four sentences of ADR-002 (the note on F8 in the report has
  what they should say).
- F9 Say in the `sources` of the entry for the first quartile of age that
  the example has the averaged value in 68 of the 69 embedded quartiles and
  medians where averaging matters.
- F10 Texts: README.md does not list std-1 as passed; the note on ars in
  third_party/SOURCES.md says nothing of it is committed (25 embedded
  values are in the exceptions file and the issue draft, three in tests);
  rule I3 in standard/methods/README.md says less than both engines do;
  "every quantile definition" in ADR-002 and in the exceptions file means
  the two of the registry; the refusal of statement 6 of the Fisher test is
  tested for Python only.
- F11 D1 exchanges the arms in every analysis: add the exchange in one
  analysis, the case of E3. The R side of rule I3 has no test: add the
  reviewer's ten cases.
- F12 The allowance of a relative 1e-9 also covers a reference value
  rounded to ten decimals; `results.py` and the README name floating error
  only.

Other open points:

- The method registry is checked by code, not by a schema in
  standard/schemas/ (section 12 lists one). It needs an ADR the owner
  approves.
- P2 for results sees what a reference embeds. The 504 results of ours that
  CDISC's example does not list are covered by the agreement of the two
  engines only, and the engines share the binding, the choice of the
  columns and the preparation of the data (F6).
- What the pilot data cannot show (tests/defects prints the first two on
  every run): the safety set and the intent-to-treat set hold the same 254
  subjects; for 3 of the 18 analyses with a data subset, dropping it
  changes nothing the reference lists. From the review (F11): no analysis
  variable of a count is missing; no column under NE has a missing value;
  every chi-square table is larger than 2 x 2, so a continuity correction
  would not show; every Fisher table is 2 x 2, so for "exact beyond 2 x 2"
  the eight vectors are the whole evidence in the gate.
- The 706 `cites` edges imported from Pilot 7's claims are candidates: no
  quote is checked against its document and no one has approved one.
  real-3 completes the graph to the documents. One edge stands for all
  citations of one span by one column (913 citations, 706 edges), so one
  `quote_verified` per edge will not be enough there.
- The v0 edge schema cannot tell a value dependency from a key, filter or
  ordering dependency; coverage.json has it per column (`value`). If the
  viewer of real-3 needs it per edge, it is a schema change (an ADR the
  owner approves).
- P1 is tested with yamaa's Python host only; its R host is not installed.
- The kit manifest is checked by code, not by a schema in
  standard/schemas/ (ADR-001, item 3). gen-2 writes kits too: agree on the
  format with it before a schema is proposed.
- The pilot's protocol is not in the kit.

## Next

- real-3a first (ADR-005, decision 1): layout spec v0 and ADR-003, then
  grid, mock shell, HTML and trace for the adverse event summary output of
  the ARS example. It has its own gate and review and merges to `main`.
- Then the rest of real-3 Grid, trace, viewer, with the gate PLAN.md gives
  it. Needs real-2. First commit of real-3a: the findings F2
  to F12 of the review of real-2 (above), then `specfirst gate real-2`
  again. Decide ADR-003 first: own layout format or tfrmt JSON.
- Then real-4 (D1, node N2), real-5 (D2, node N2), in order.

## Handed over by real-2

- `specfirst build cdiscpilot01` now also writes, per reporting event of
  the kit: `gold/ard/<id>.jsonl` (the Python engine: the gold ARD),
  `gold/ard/<id>.r.jsonl` (the R engine) and `gold/ars/<id>.json` (the ARS
  file with our results as raw values). The build needs R.
  `specfirst check cdiscpilot01` adds P2 for results and rule R11.
- An ARD row is identified by `id`:
  `ard:<analysis>/<operation>/<one part per grouping>`; the grid of real-3
  names these IDs in its cells. standard/methods/README.md has the format,
  the rules I1 to I15 an analysis is run by, and the rules B1 to B3 that
  bind an ARS operation to the registry.
- `specfirst.machine.ars.reads(event, analysis_id, subject_key)` gives what
  an analysis reads, by role (variable, set, subset, grouping, key): the
  `reads` edges of section 4.2. The example reads 23 columns of ADSL, ADAE
  and ADVS (E5).
- The example's `formattedValue`s are not used yet. real-3 compares cell
  text with them: the 25 results of gold/exceptions.yaml will differ there
  too, and the result the engines do not give (the empty p-value) has no
  ARD row.
- The display rule `display.round.half_away_from_zero` is in the registry
  with a Python implementation (`specfirst.machine.methods.round_half_away`)
  and 17 vectors. The p-value formats and the truncation of long terms
  (E25) are not: real-3 or real-4 adds them as registry entries.
- A new method: an entry in standard/methods/ with numbered semantics,
  vectors in tests/methods/ (and `oracle.py` if it can be computed
  exactly), a function in `specfirst/machine/methods.py` and one in
  r/specfirstr/R/methods.R, a branch in both engines, then
  `specfirst methods --write`. Add statements of semantics at the end:
  vectors cite them by number.
- A new reference with results: its differences go to the kit's
  gold/exceptions.yaml, each with a proof kind that
  `specfirst.machine.results` checks. A proof kind that is missing is added
  there, with a planted defect in tests/unit/test_results.py. Until F2 is
  fixed, a proof that passes the check is not yet a proof: read what it
  names.
- A planted defect that passes is not yet a hole: tests/defects D4 sorts
  such cases by what the defect changed (lesson 24). Do the same before
  trusting or blaming a checker.

## For other tracks

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
- gen, read: a kit with a reporting event names it under `results` in
  kit.yaml (ADR-002, decision 5); the engines read the ADaM datasets of the
  build.

## Handed over by real-1

- `specfirst build cdiscpilot01` writes the 10 ADaM datasets as canonical
  Parquet into build/kits/cdiscpilot01/gold/data/adam/; the result engines
  read them from there, not from the fetch cache. `specfirst check
  cdiscpilot01` proves they equal the reference.
- `specfirst.machine.canonical` has the writers for JSON, JSONL and
  Parquet; every built file goes through it (P1).
- The graph is in gold/graph/ (nodes.jsonl, edges.jsonl, coverage.json).
  ADaM node IDs are `adam:<DATASET>.<COLUMN>`; real-3 adds the `reads`
  edges from analyses to them.
- A new work package adds its gate to `GATES` in src/specfirst/gates.py and
  its cache-dependent tests under tests/ with the marker `evidence`.
- Reading or importing anything from the fetch cache must leave it
  untouched (lesson 13): the gate verifies the cache again at its end.
- Code taken over from a cached source, even retyped, goes into
  third_party/SOURCES.md with its license (lessons 12 and 14); the test
  A5-adapted of tests/pilot looks for what was not recorded.
- A static check of the graph cannot see a reference the analysis missed.
  tests/pilot A4-unread tests the pilot graph against the engine; a new
  graph layer needs a check of that kind (lesson 16).
