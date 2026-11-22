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
  0 on a clone of it (docs/reports/real-3a.md has the run, and
  real-3a.real-2.gate.log the log).
- real-3a Layout, grid and trace for the adverse event summary (ADR-005,
  decision 1: the unit `tfl-ae-summary`, output `Out14-3-1-1` of CDISC's
  ARS example). Gate: `scripts/clean_clone_gate.sh real-3a` exited 0 on a
  clean clone of commit `9730843`, and again on a clean clone of `26667ed`,
  which is that work with `main` merged into it (`catalog@1` of std-1), 16
  of 16 checks both times (2026-11-17). Evidence: docs/reports/real-3a.md,
  real-3a.clean-clone.gate.log and real-3a.merged.gate.log;
  real-3a.gate.log is an earlier run on a clone of `0938fe4` with the
  installed environment, which built the same bytes. Review:
  docs/reports/real-3a.review.md (PASS, nine findings that do not block;
  they are listed under "Open"). Decisions: docs/decisions/ADR-003.md.
- Fix of issue #27 (2026-11-18): the table by organ class and term counts
  arms x the pairs that occur, not every organ class with every term.
  Gates: `scripts/clean_clone_gate.sh` real-2, real-3a, gen-2a, gen-3a and
  read-1a exited 0 on clean clones of `c7f09a0` (the change `e00bbb7` with
  `main` merged in). Evidence: docs/reports/issue-27.md and
  issue-27.<gate>.gate.log. Review: docs/reports/issue-27.review.md
  (SIGNED, four findings that do not block, nothing for the owner).
  Decisions: docs/decisions/ADR-011.md.
- real-5a ANCOVA and Tables 14-3.01, 14-3.03 and 14-3.05 against the CSR
  (slice `efficacy-first`, ADR-012, approved 2026-11-18). Gate:
  `scripts/clean_clone_gate.sh real-5a` exited 0 on a clean clone of
  commit `4d0b3cf` (the work with `main` `1a94134` merged in), 18 of 18
  checks (2026-11-19). On clean clones of the same commit real-2, real-3a,
  gen-2a, gen-3a, read-1a, std-1 and read-2a (19 of 19) passed too.
  read-2a's kept dry run of arm R was made again at the owner's answer and
  kept in place of the old one (USD 0.58). Evidence:
  docs/reports/real-5a.md, real-5a.clean-clone.gate.log and
  real-5a.read-2a.gate.log. Review: docs/reports/real-5a.review.md (pass 1
  NOT SIGNED, its two blocking findings fixed; passes 2 and 3 SIGNED).
  Decisions: docs/decisions/ADR-015.md and the amendment "of real-5a" at
  the end of ADR-003.md.
- real-5b The mixed model for repeated measures, CMH and Tables 14-3.11 and
  14-3.13 against the CSR (slice `efficacy-first`, ADR-012). Gate:
  `scripts/clean_clone_gate.sh real-5b` exited 0 on a clean clone of commit
  `2d7164c` (the work with `main` `7806105`, ADR-017 carried out, merged
  in), 19 of 19 checks (2026-11-20). On clean clones of the same commit
  read-2a (19 of 19, "arm R, kept dry run" among them), real-5a, real-3a,
  real-2, gen-2a, gen-3a, read-1a and std-1 passed too. The kept dry run of
  arm R was not made again: under ADR-017 it is bound by the four registry
  entries its slice reaches, which real-5b leaves as they were. Evidence:
  docs/reports/real-5b.md, real-5b.clean-clone.gate.log and
  real-5b.read-2a.gate.log. Review:
  docs/reports/real-5b.review.md (passes 1 to 3 NOT SIGNED, their blocking
  findings F1, G1 and H1 fixed; pass 4 SIGNED). Decisions: the amendments
  "of real-5b" at the end of ADR-015.md and ADR-003.md.
- real-5b-answers The owner's answers of 2026-11-20 on real-5a and real-5b
  carried out: five records `stated`, G2 (the last visit of the mixed model
  held on the model records) and K1 (no other columns in an other_build
  proof). Gate: `scripts/clean_clone_gate.sh` exited 0 for real-5b (19 of
  19), read-2a (19 of 19), real-5a, real-3a, real-2, gen-2a, gen-3a,
  read-1a and std-1 on clean clones of commit `4660e8c` (2026-11-21). The
  kept dry run of arm R was not made again. Evidence:
  docs/reports/real-5b-answers.md, real-5b-answers.clean-clone.gate.log and
  real-5b-answers.read-2a.gate.log. Review:
  docs/reports/real-5b-answers.review.md (pass 1 SIGNED, four findings that
  do not block). Decisions: ADR-015, section "The owner's answers
  (2026-11-20)".
- Issue #29 A standalone recomputation script per analysis (2026-11-21):
  `specfirst recompute cdiscpilot01` writes, runs sealed and compares 69
  scripts (42 Python, 27 R), 69 of 69 `reproduced`; the planted break of
  the LS-means weights, and the quartile and CMH plants, are found. Gates:
  `scripts/clean_clone_gate.sh` exited 0 for issue-29 (12 of 12), real-5a,
  real-5b, real-2 and real-3a on clean clones of commit `22c2932` (the
  work on `main` `9dc6b20`). Evidence: docs/reports/issue-29.md and
  issue-29.clean-clone.gate.log, issue-29.<gate>.gate.log. Review:
  docs/reports/issue-29.review.md. Decisions: docs/decisions/ADR-021.md.

## Open

Answered by the owner on 2026-11-20 (ADR-015, "The owner's answers
(2026-11-20)"; docs/reports/real-5b-answers.md):

- The documents against the CSR: the 45 differences of the five efficacy
  tables stay `rule_choice` (gold follows the documents), the sign of
  "-0.0" and the LS means at Week 24 as they were, the row labels the
  CSR's. Nothing changed.
- The records the documents leave open or contradict:
  `custom:eff-model-terms`, `custom:eff-pairwise` and
  `custom:eff-mmrm-records` (were `conflict`) are `stated`,
  `document_rule`; `custom:eff-mmrm-df` and `custom:eff-cmh` (were
  `asked`, `gold_quirk`) are `stated`, `study_input`. Each keeps its value
  and cites the answer (doc `answers`). No number changed.
- G2 and K1 of the review of real-5b are closed: `custom:eff-mmrm-visit`
  names Week 24 and the check `decisions` holds the last visit of the
  model records against it; an other_build proof refuses an other analysis
  that differs in a column-valued option. Each is planted in D11.

Left by the review of real-5b-answers (does not block): L3, D11's K1 plant
is also seen by the check `decisions`; pass 4's case O2 (an other analysis
with strata RACEN, SEX and QSSEQ, rank scores) is the case only K1 sees,
and could be added as a plant. For the owner, the class of the three former
conflicts: `document_rule`, with `study_input` the alternative (review,
"The owner's choices").

Still open for the owner, from real-5b and real-5a (none blocks):

- `custom:eff-baseline-rows` is `asked` (not in the questions): no source;
  both readings give the same cells here.
- The Toeplitz fallback of SAP 10.1.1 is not implemented (not met on the
  pilot). The gate real-5a counts its own three tables.
- The proposals for `catalog@2` in docs/reports/real-5a.md (an efficacy
  table family, an imputation rule in `mod-bds-visits`, the pooling of
  sites) and docs/reports/real-5b.md, for the std track.
- The kept transcript holds the Claude Code CLI's usage event (the
  subscription's usage, no credential); the old run on `main` had it too.
  The reviewer finds it acceptable (review pass 3, K3); the owner keeps it
  (2026-11-19). The kept run's tie to the registry's bytes is settled by
  ADR-017 (read track): only the entries its slice reaches bind it.

Left open by the review of real-5a (none blocks; the report's section
"What the checks do not cover" has each):

- F3: closed in real-5b (with the records at hand, each decision an entry
  names must bind an analysis of the cell or its method). F4 and G3: the
  check `decisions` holds the records that set an option; nothing holds
  `custom:eff-display-decimals` (decisions.py lists the unheld records).
- F5: closed in real-5b, with a vector each.
- F7: the CSR's population line is parsed and not compared.

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
- The comparison of grid text is per result, with the formatted values of
  the example's ARS file. The expected text of a cell is built with the
  layout's own template, so the order of the parts of a cell is held
  against nothing yet (decision 5). The example's table shell shows the
  cells, and it is in the pinned repository; ADR-003 first said it was not
  (finding F1 of the review, corrected in the documents). The grid differs
  from that shell by one line of the row axis; see F1 below.
- The report of real-3a quotes the whole grid of this output as text: its
  titles, row labels, footnotes and the 27 cell texts, which are our
  results and equal the example's formatted values. The review lists this
  for the owner: it is more of one output than an earlier report holds; the
  repository is private and the example's repository is MIT.
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

What the review of real-3a leaves open (docs/reports/real-3a.review.md has
each in full; none blocks). Each changes code or a built file, so they are
the first commit of the rest of real-3, with a gate run of its own, as F2
to F12 of real-2 were for real-3a:

- F1: the example's table shell
  (`workfiles/examples/ARS v1/AE_Summary_Table_Shell.pdf` in the pinned ARS
  repository) is not pinned in kit.yaml, and nothing holds the mock shell
  against it. Against the grid it has: one more line of the row axis
  ("Number of subjects with at least one event", above the eight rows,
  which are indented under it; the ARS list of contents has the same text
  and `ars.listed_analyses` drops it); the count under the mask `XX`,
  where the mock shell follows the operation's `XXX`; "Table 14.3.1.1"
  where the ARS file and the grid have "Table 14.3.1.<x>.<y>"; the note on
  the abbreviation without its final point. Once the mock shell is held
  against the shell's text, the planted layouts that pass today (the
  percent before the count, another text between the parts, another
  header) must fail. D7, `tests/defects/README.md` and two comments of
  `grid.py` still give the old reason for their passing.
- F2: with a data-driven column grouping, an arm that has subjects and no
  record of an analysis stops the build (`GridError`: rule I9 gives it no
  group, so the ARD has no row). Defined groups give "0 (  0.0)" on the
  same data. What such a cell shows needs a decision, a statement and a
  planted defect.
- F3: `grid.compare_reference` passes a body cell with a part that names
  another analysis than that of its row (the percent of one row in
  another), and another title, footnote, section or indent. Outside the
  gate, `specfirst check` passes a row of another output and an analysis
  that stands in two blocks; the gate stops these by its counts only.
- F4: neither `graph.check_cells` nor D8 sees a single `reads` edge to a
  column that the analysis of the denominator also reads (24 of the 52
  `reads` edges by the construction of the test; the review ran one
  analysis), or the `computes` edge of one percent to that analysis. The
  roles in coverage.json are held against nothing.
- F5: `between_equal_values` and `same_under_every` do not ask whether our
  own cell is right: with a wrong population planted, 36 wrong quartiles
  and medians of ours were accepted as errors of the reference. The
  committed entry is sound. Fix: ask that the n, the minimum and the
  maximum of the cell are reproduced; plant the population in D6.
- F6: `render.projection_problems` does not see where a text stands (two
  cells or rows exchanged, the header row in the body), nor an `onload`
  handler, a style that imports, a `meta` refresh, a comment or text in
  `title`. It matters for the viewer, whose gate asks for no network.
- F7: `registry.load` joins the words of a statement with one blank, so
  registry.json has "( 9.5)" where statement 3 of `display.pattern` has two
  blanks.
- F8: Python's `ard._number_text` writes a group value that is not finite
  (`=inf`), against the last sentence of rule I9; the hand-over to R then
  ends in a `ValueError` that the build does not catch.
- F9, the parts in code and tests: the two new Fisher vectors call their
  expected value the sum in exact fractions, and it is the value of the
  Python implementation (within 2.1e-13 of it); `fisher-limit` is not among
  the tests the gate requires to have run; `specfirst check` passes a cell
  whose result has no formatted value in the reference (the gate does not).

The review could not read the source of tfrmt (no network at the time):
every row of the table "tfrmt, read" in ADR-003 rests on the author's
reading.

Other open points:

- Layout spec v0 has three kinds of block (`header`, `analyses` and, since
  real-5a, `statistics`). The other four outputs of the example need more
  (see "Next").
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

- The slice `efficacy-first` (ADR-012) is done with real-5b. What comes
  next on this track is the owner's call (PLAN.md, real-5: the other CSR
  tables).
- The findings F1 to F9 of the review of real-3a ("Open" above), as one
  commit with a gate run.
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
  and term), a total column, sort and threshold rules (a row per statistic
  and columns that compare two groups exist since real-5a: the block kind
  `statistics`). The plan of a grid
  (`grid.plan`) is the place: the builder, the comparison and the trace all
  read the plan. For organ class and term the results are ready since the
  fix of issue #27 (ADR-011): the analysis by term gives arms x the pairs
  that occur, each result identified by its values
  (`.../Grp_TRT01A_1/=<organ class>/=<term>`), so the rows of the grid are
  read from the ARD; the rows themselves are still layout work.
- Display rules that are not registry entries yet: p-value formats and the
  truncation of long terms (E25).

## Handed over by issue #29

- `specfirst recompute <kit> [--build DIR] [--export DIR]` writes, from a
  build of the kit, one standalone script per analysis of its reporting
  events into build/recompute/<kit>/bundle/ (with plan.json, manifest.json,
  the gold ARD rows, adam_csv.py, compare.py, run_all.sh and README.txt; no
  study data), runs each script sealed on copies of the reference ADaM, and
  writes build/recompute/<kit>/run/ (outputs, logs, report.json,
  report.txt, checks.json). ADR-021 has the design.
- A script is written by a template per registry method: Python
  (`specfirst.recompute.pywrite`) for count, percent, continuous summary,
  chi-square and one-way ANOVA; R (`rwrite`) for Fisher, CMH, ANCOVA and
  the mixed model. An analysis whose method or shape no template covers is
  `not covered`, with the reason: a new registry method, a new kind of
  grouping or a new comparator needs a template first. The templates cite
  registry statements by number (`common.statement` finds an option's
  statement by its first words): add statements at the end, as before.
- The generator reads the ARS, kit.yaml, the decision records and
  registry.json as plain data, with its own reading of the rules of
  standard/methods/README.md it needs (B1 to B3, I3 to I5, I8 to I10, I12
  to I19; `specfirst.recompute.reading` and the writers). Of specfirst it
  imports only `specfirst.recompute`, `kit`, `paths` and `machine.canonical`
  (`static.GENERATOR_IMPORTS`; a unit test holds it).
- The static check (`specfirst.recompute.static`) holds the scripts to
  allow-lists (Python imports, builtins and attributes; R calls) and to one
  form of a read (`adam / "<d>.parquet"`, `file.path(adam, "<d>.csv")`): a
  template that needs another function, attribute or form of a read needs
  it added there, and a reason. seal.py's audit hook refuses every import
  of specfirst or yamaa and every open by Python in the checkout and the
  build, so a script writes its output in its own folder and run.py copies
  it out. Neither check is a proof (ADR-021, decision 5, says what they do
  not hold).
- The gate issue-29 holds the pilot at 69 analyses
  (`gates.RECOMPUTE_ANALYSES`): an analysis added to a reporting event of
  the kit changes that number. tests/recompute plants three breaks of the
  engine and the checks' own defects (RC1 to RC6).

## Handed over by real-5b

- The mixed model for repeated measures is R only (`model.mmrm.lsmeans`,
  `.pairwise`; mmrm 0.3.19 with nlminb, emmeans); its vectors come from a
  second optimization, tests/methods/oracle_mmrm.py, held to 1e-6. CMH is
  Python and R (`test.cmh`, rule I12d; `strata` are columns, the first test
  with a columns option).
- A second proof kind, `other_build` (csr.py): another build of the cell,
  held to "that alternative": an other analysis differs from the cell's
  only in its naming and in the options its decisions set
  (`decisions.PARAMETERS`), and never in an option whose values are
  columns (`ars.MODEL_TERMS`; K1, the owner's answer of 2026-11-20); an
  other pattern changes only the mask; an
  other template is a cell template of the layout (parts as {name}) and
  adds no text; every decision an entry names binds an analysis of the
  cell or its method; `decision` may be a list. `display.pattern.signed` is
  a display rule of its own: display.pattern and the other entries the
  read track's slice reaches must not change (ADR-017).
- Layout spec v0 has extra columns, statistics-row `extra` cells and the
  block kind `groups` (amendment of real-5b to ADR-003). The CSR parser
  reads a column without a count, the header of the row labels, a line of
  two labels and "Note:" as a footnote.
- The check `decisions` holds the last visit of the model records against
  `custom:eff-mmrm-visit` (`decisions.LAST_VISIT`; G2, the owner's answer
  of 2026-11-20). It needs the built ADaM data: `build.decision_checks`
  hands it the Python engines, and without them the record is a problem.
- The gate real-5b holds the hint of E22 (`E22 hint`) and the engines' CMH
  p-values (`CMH`); the gate real-5a counts its own three tables
  (`gates.EFFICACY_GRIDS`), real-5b its two (`REAL5B_GRIDS`).

## Handed over by real-5a

- Model-based methods are kind `model`, R only (ADR-015):
  `model.ancova.lsmeans`, `.pairwise`, `.dose_response` in
  standard/methods/, R in r/specfirstr/R/models.R (stats::lm, emmeans,
  car). An analysis names its terms in `programmingCode` (`factors`,
  `covariates`, `reference`; `ars.reads` role `model`); rules I16 to I19 of
  standard/methods/README.md. The gold ARD takes the R engine's rows. Their
  vectors' expected values come from tests/methods/oracle_models.py (exact
  fractions), not from R.
- A CSR table is a reference grid: `specfirst.machine.csr` parses the page
  with poppler's pdftotext into build/csr/<kit>/ on every check, never into
  the cache or git; an output names it as `reference: {csr, page, table}`
  in kit.yaml. A cell that differs needs one entry in the `cells` section
  of gold/exceptions.yaml (proof `other_pattern` exists).
- Layout spec v0 has a block kind `statistics` (a row per statistic,
  `columns` for comparisons); pages show section headings (the amendment
  of ADR-003).
- Decision records of the pilot are in kits/cdiscpilot01/gold/decisions/
  (`build.decisions` in kit.yaml); the gate check `decisions` holds the
  options they set against the reporting event.
- The gates real-2 and real-3a count the ARS example's result set only
  (`gates.PILOT_EXAMPLE`).
- A change of standard/methods/ changes every generated kit.yaml
  (`registry_sha256`) and every reader task folder, and makes read-2a's
  check "arm R, kept dry run" fail until the run is made again (CLAUDE.md,
  Gotchas).

## Handed over by the fix of issue #27

- `specfirst.gen.gold.resolve_groupings` lists the groups of a data-driven
  grouping only when its dataset is ADSL (it subdivides the subject
  population). A data-driven grouping on another dataset (ADAE.AESOC,
  ADAE.AEDECOD) stays data-driven, and the engines give the combinations
  that occur (rules I9, I10), each with every listed arm. This is how
  CDISC's example "Common Safety Displays" models the table, and why
  ADR-011 chose it over nesting in the ARS file or a grouping on the pair:
  the ARS model has neither a nested nor a dependent grouping.
- `tests/unit/test_soc_pt_pairs.py` is the vector of the issue (two sizes,
  invented data): counts, the total column, the organ classes, and the R
  engine on the same event (rule R11).
- For real-4 (review of the fix, F4): the rule is a dataset name. A
  grouping of records whose categories a table shows in full (severity or
  relationship as rows or columns) gets no result for a category without a
  record, so its template gives it defined groups, as CDISC's examples do
  for every grouping but organ class and term; or real-4 widens the rule.
  The vector covers the scorer's build and no analysis of event counts.
- ADR-007's item 1 for the owner (decision 1 or a change of rule I9) is
  still open; whichever stays has to keep the pairs that occur for
  groupings of records.

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
  on the Linux file system runs the gate of real-3a in about 5 minutes; the
  worktree on the Windows drive takes several times as long.
- The Linux virtual machine is shared by the sessions of all tracks. On
  2026-11-17 it ran out of memory with three test runs at once, and the
  instance was terminated again and again until WSL was restarted. One
  heavy run at a time: `flock /run/lock/specfirst-heavy.lock <command>`
  around a gate, a test suite or a build, and at most four worker
  processes. A session never restarts WSL itself and never stops a process
  there by a name pattern: other sessions run in the same machine.
- That a pinned source lacks a file is a claim to be run (lesson 31): list
  the folder of the pin and record the output.

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
  treatment grouping, and `An_AESUM_N` for the header). One limit, found by
  the review of real-3a (F2): with a data-driven treatment grouping, an arm
  without a record of an analysis has no ARD row, and the builder stops
  with `GridError`. Until that is decided, a compiled summary builds only
  when every arm has a record in every row it shows.
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
