# Issue #31 A calculation-first review view and a study decision sheet: independent review, pass 1 (code)

Reviewed: the work on issue #31 ("[viewer] A calculation-first review view:
click a number for the analysis, decisions, why each variable and its
derivation, the recomputation; plus a study decision sheet") on branch
`track/real`, as it is at `db50a40`.

- The diff `e123599..db50a40` (32 files, 3437 insertions, 120 deletions).
  `e123599` is `main`. The work is two commits: `ece4301` (part 1: the
  grids Out14-1-1 and Out14-3-2-1, the citations of the ARS file, the
  review page, the gate `issue-31`) and `db50a40` (part 2: the 48 decision
  records of the demographics and AE tables over `catalog@2` /
  `open-default@2`, the new rules of the decisions check, the kit format
  change). The worktree was clean at `db50a40` (`git status --short`
  prints nothing); the only file the reviewer wrote in it is this one.
- The report docs/reports/issue-31.md is a draft at `db50a40`: its `@@`
  placeholders are filled after the gates and are not reviewed; its prose
  is.
- The files the findings quote, as committed at `db50a40`:

  | File | Lines | SHA-256 |
  | --- | --- | --- |
  | `src/specfirst/viewer/check.py` | 216 | `3d7a09fbdd31223a9574c1543026c3e5602e52c81991dd841e712cd0c0b377c2` |
  | `src/specfirst/viewer/model.py` | 466 | `ee59bda1de6bc4d0b75da42b06ba5880131c8fb7c7cab50750ab534be676bf7d` |
  | `src/specfirst/viewer/page.py` | 305 | `b721d41925df21245ef5ecc138eb209f788544f457e9ea274bccda596aec271b` |
  | `src/specfirst/machine/graph.py` | 905 | `a5d49ce17f71e415359f384f48b6c581811ff48f741c24c36aa5d705ce949cb7` |
  | `src/specfirst/machine/decisions.py` | 415 | `e213571b1a4d78324bf73e766eb993e85b9795178a2c2297a54baacddc565b36` |
  | `src/specfirst/machine/build.py` | 859 | `da22f16d88c41c607344daeb19bf22f6725661c9e1c4494170975a9097e4e19d` |
  | `src/specfirst/gates.py` | 1080 | `92ab0de65663f712d19ec7f3bea080aa57c0bc733e92dea2fe24ebcf49b9761c` |
  | `kits/cdiscpilot01/gold/decisions/safety.jsonl` | 48 | `bd4e208ba55bb0e38bcb964efddc95ce17df5ad9a579239cff5da07eca12bad8` |
  | `kits/cdiscpilot01/gold/layout/Out14-1-1.yaml` | 152 | `405bf98a4d87b2495adf4325080765c9b9d9e9bfaa642738afe2222ed666652c` |
  | `docs/decisions/ADR-022.md` | 243 | `c4dbd4b40415b695ec0533e94ada4253e7c9019849f899c434c322e4e3a12ca1` |
  | `docs/reports/issue-31.md` | 118 | `0572a968e919dab1608be4a87adae46fa0f4046ee42cb3ba7dfee8804fdf6a9e` |
  | `docs/state/real.md` | 644 | `35581fdc93e7785d0dba9974baf786772f7c5ec35b286e24c6bc5b83416b6281` |

## Outcome

One blocking finding, six not blocking:

- F1 (blocking): the statuses of several records of safety.jsonl miss what
  the SAP's display templates say (the population of the demographics
  table, the p-value format and the AE counts are conflicts recorded as
  `asked` or `default`); the owner's lists built from them are incomplete
  and in part false.
- F2: decisions that bind ADaM columns reach a panel as links to a sheet
  row without alternatives, and those of upstream columns not at all.
- F3: the acceptance and the page check decide most of what they claim of
  the page on the review model.
- F4: page references without page numbers give no edge and no count; the
  report's sentence on the 24 analyses overstates.
- F5: `formats` entries under a key that is no result set of the kit are
  never read.
- F6: the sheet's binding and layout lines (mark, status, no citation) and
  the kind of a P4 class.
- F7: small errors of the documents (a record named that does not exist,
  ADR-003 without the amendment it is said to have, "one differs").

What holds, checked against the code and runs (section "What was run"):

- The grids. Out14-1-1 (104 cells, 147 results) and Out14-3-2-1 (1275
  cells, 1940 results, 408 of them without a formatted value in the
  example) are built from the layouts as the layout spec says: the extra
  cell of a groups block stands in its first row; a terms block has one
  row per value the results have, A to Z, each followed by its nested
  values, with the Fisher p-values of the split comparisons and an empty
  cell where a comparison has no result; the spanner reaches the grid's
  columns. A wrong grid does not pass the comparison with the example:
  every result the example formats for an analysis of the output must be
  shown by a cell (grid.py, `compare_reference`), the counts of the gate pin
  the cells and results (a terms row or a p-value lost changes them), and
  the R engine's rows must give the same grid. The 408 results without a
  formatted value are counted, not compared, as ADR-022 says. The proof of
  `formats` holds what ADR-022 decision 6 says (the reference's raw value
  under the pattern is our text, its formatted value is the entry's and
  another), and an entry no cell differs by fails (D13; the unit test
  plants a wrong formatted text and a different raw value).
- The gates real-3a and real-5a still hold what they held on Out14-3-1-1:
  with `unformatted` 0, `no_reference` must be 0, and `uncompared` grows
  only with it, so `equal + classified + uncompared == cells` is the old
  `equal + classified == cells`; they now also ask for the two new grids.
  D7 and D8 plant in Out14-3-1-1 by name (`SUMMARY_OUTPUT`), as before by
  position.
- The citations of the ARS file: `quote_verified` is true only where the
  label, blanks removed, stands in pdftotext's text of that page of the
  kit's SAP (graph.py, `add_citations`); the unit test plants a page
  without its label. On the build: 29 edges, 29 verified, none approved.
- The page: no script, handler, frame, image, form, import, refresh or
  remote link; every link to an anchor, every anchor once; every citation
  drawn `judged` with "awaiting approval" (2069 citations, 2069 marks);
  every decision "not tested". D13 plants a script, a handler, a remote
  link, a judged edge drawn executed, an unseparated decision drawn static,
  a cell block gone from the page and a derives_from edge lost in the graph
  files, and each is seen. The page of the second build of P1 is the same
  bytes (the author's clean-clone gate); the page the gate wrote is
  `page.html` of the review loaded again from that build, byte for byte
  (R2).
- The panels show what the model holds: the analysis in sentences (set,
  subset, groupings, statistic with its denominator), the records that
  bind the analysis's elements, the columns it reads with the Define-XML
  comment next to the rule that runs and its file and line (for ADSL.TRTSDT
  the comment "SV.SVSTDTC when SV.VISITNUM=3, converted to SAS date" next to
  the rule `impute ... source EX_MINDTC` at
  gold/spec/spec/yamaa/pilot-program/adsl_v1.yaml:327, which is the owner's
  answer to Q3 at work), the derivation chain down to SDTM, and the
  recomputation (all 69 analyses reproduced) with the script in a fold.
- The acceptance as the issue states it holds on the build: 84, 27 and
  1178 printed numbers of Out14-1-1, Out14-3-1-1 and Out14-3-2-1 open a
  panel that reaches SDTM and a citation or a house default; the sheet has
  92 lines (66 records, 17 catalog entries without a record, 1 binding, 8
  layouts) and lists every record and every entry of catalog@2 (61 keys).
- The decisions check: `catalog_problems` fails on a wrong unit, a value
  that is no alternative, a statement the catalog does not render, a
  `default` that is not the house's and an unknown ID; the quote check fails
  on a quote that is not in its document, a stated record without a
  citation, a citation of an unknown document and a bind to a column the
  build lacks; `answers` is counted, not checked (unit tests, each first
  passing unchanged). On the build: 66 records, 92 quotes held, 0 problems,
  "answers 5".
- The counts of ADR-022 decision 7 are those of the file: 48 records, 44
  of catalog entries (every entry and unit of the seven units but the four
  it names), 4 custom; statuses 15 / 20 / 7 / 6. The values spot-checked
  against the build's resolved specifications are the build's
  (trt.start.source: `EX_MINDTC`; trt.date.imputation and
  ae.start.imputation: day 1, month 1; trt.end.source: the disposition date
  when the last EX record has no end date; demo.age.groups: AGE < 65, <=
  80, else >80; ae.teae.start/end: `ASTDT >= TRTSDT`, no end;
  ae.related.values: `Dss02_Related_TEAE` is AEREL IN POSSIBLE, PROBABLE),
  except custom:demog-baseline-visits (F1). The quotes spot-checked stand
  in the SAP and the Define-XML.
- The kit format change: every reader of `kit.decisions` reads the tuple
  (build.py `csr_comparison` and `decision_checks`, recompute/generate.py,
  viewer/model.py, tests/defects); the reader's task of the pilot still
  writes an empty gold/decisions.jsonl (harness/pilot.py:164) and its own
  manifest, so safety.jsonl reaches no task and no score; score/pilot.py
  takes Out14-3-1-1 by its ID. `kit lock` keeps everything before `files:`.
- The gate `issue-31` has the checks ADR-022 decision 9 lists, in that
  order; its check `review` holds the page checks, the acceptance on the
  three outputs of the issue and the page of the second build byte for
  byte.
- Nothing claims std-2's check: ADR-022 decision 7, the state file, the
  report draft, decisions.py (`problems`) and test_safety_records.py all
  say the records are held for form, binds and quotes, not by result.
- Rules 6, R10, R4: the diff has no byte outside ASCII, no local user
  path, no credential or token; the page states no date; nodes, edges and
  coverage are sorted.

## Findings

### F1 (blocking) The statuses of several records miss what the SAP's display templates say

ADR-022 decision 7 gives each status a meaning: `stated` when a kit
document states the value; `default` when the value is the house's and "no
kit document states it"; `conflict` when a kit document says other than the
build; `asked` when "no document states it" and the value is not the
house's. The reading behind safety.jsonl took the SAP's text (its records
cite sections 6, 7, 9.2 and 11.2) and the Define-XML, but not the SAP's
templates of its section 13.2
(the mock tables, Templates 1 to 24), which state values for these very
tables:

- safety.jsonl:18, `tfl.population` (tfl-demographics): status `asked`,
  class `gold_quirk`, value `safety`, no citation. SAP PDF page 22 (printed
  page 21), Template 3 "Summary of Demographic and Baseline
  Characteristics", heads its table "Population: Intent-to-Treat". The
  house's default is `randomized` (`decisions.house_values` gives
  `[{"rule": "randomized"}]`), and catalog@2's own entry cites "Table
  14-2.01 on the intent-to-treat population". A kit document states a value
  other than the build's: by decision 7 this is a `conflict`, and the
  owner's list says the opposite ("asked ... CDISC's example does it and no
  document of the kit says so (... the population ... of the
  demographics ...)", docs/state/real.md and docs/reports/issue-31.md:84).
- safety.jsonl:25, `tfl.pvalue.format`: `asked`, value `four_decimals`.
  Every p-value mask of the SAP's templates is `0.xxx` or `x.xxx` (Template
  3 among them; none has four decimals), which is also the house's default
  (`three_decimals`). A `conflict`, not "no document".
- safety.jsonl:44, `tfl.ae.socpt.counts`: `default`, value `subjects`. SAP
  PDF page 32, Template 13 "Incidence of Treatment Emergent Adverse Events
  by Treatment Group", has for each arm the columns "n (%)" and "Total
  Events", with a note that the latter count every time an event was
  recorded: the alternative
  `subjects_and_events`. A `conflict`, not a default no document states.
- safety.jsonl:47, `custom:demog-decimals`: `asked` ("no document"); Template
  3 prints Mean `xx.x`, SD `x.xx`, Median `xx.x`, which is the record's
  value for those three, and Min/Max `xx.x`: stated in part, in conflict in
  part.
- Of the same kind, with no change of value: `tfl.population`
  (tfl-ae-soc-pt) is `default`, and Template 13 states "Population: Safety";
  `tfl.columns.arms` is `default` in all three units, and Templates 3 and
  13 order Placebo, Low Dose, High Dose. Templates 3 and 13 also print
  percentages as `xx (xx%)` against the house's one decimal
  (`tfl.percent.format`, `default`): a person should judge whether a mock
  mask states the decimals.
- A second kind, one representative: `custom:demog-baseline-visits`
  (safety.jsonl:46) is `stated` "Baseline height is the value at Visit 1,
  and baseline weight the value at Visit 3", and the state file says "a
  record's value is the build's". The build takes the first HEIGHT record
  by VISITNUM, whatever its visit (`BASE_HT`, adsl_v1.yaml:109-118), and the
  WEIGHT record with `VSBLFL = 'Y'` (`BASE_WT`, adsl_v1.yaml:120-129), while
  the Define-XML says `VS.VISITNUM=1` and `VS.VISITNUM=3`. The file treats
  the same kind of difference for the start of treatment (Define-XML: SV
  visit 3; the build: the first exposure) as a `conflict`; here it is
  `stated`. Whether the two rules give the same values on the pilot is
  std-2's check by result, but the status and the state file's sentence
  should not decide it.

Why it blocks: the status is the record's statement of where its value
comes from, which the owner's answer to Q1 made the point of the file
("each stated with a SAP quote that a script checks or default with the
house's source"); the lists "for the owner" in docs/state/real.md and the
report are built from it, so at least three conflicts are missing from
them (the population and the p-value format of the demographics, the AE
counts) and three `asked` records are said to be ones "no document of the
kit says" where the SAP does (those two and custom:demog-decimals). No
check can see this
(the decisions check holds form, binds and quotes, as ADR-022 says).

What would fix it: read the SAP's templates (section 13.2) for the units of
the file; give the records above the status decision 7 defines, each
`conflict` citing the template's line as its quote (a script finds
"Population: Intent-to-Treat" and "Total Events" in the SAP's text); state
for custom:demog-baseline-visits what the build does or make it a
`conflict`; then the counts 15 / 20 / 7 / 6 in ADR-022 decision 7, in
test_safety_records.py:47 and in the report, and the owner's lists in the
report and the state file.

### F2 (not blocking) Decisions behind a number that bind ADaM columns: links without alternatives, or not on the panel

The issue asks, for each number, "the decisions behind it (standard-form
sentence, alternatives not chosen, citation, house default or study
customized)". Section 2 of a panel shows the records that bind the
analysis's ARS elements (model.py:377, ADR-022 decision 2.2); a record that
binds a column the analysis reads stands in section 3 as a link to its row
of the sheet (page.py:125-131), and the sheet row (page.py:263-283) has the
statement, status, class, mark, citations and P4, not the alternatives
not chosen; a record that binds a column the read column derives from is
not on the panel at all (page.py:133-147 shows the derivation of each
column of the chain, not its records). On the build, of the 48 safety
records (R2):

- in section 2 of some panel of the three outputs: 37;
- only as a link in section 3: ae.teae.end, custom:demog-baseline-visits,
  demo.age.groups, trt.start.source (a `conflict`);
- behind the numbers through a derived column, on no panel:
  ae.start.imputation (a `conflict`; it binds ADAE.ASTDT, from which
  TRTEMFL derives, which every TEAE count reads), trt.date.imputation
  (`asked`; TRTSDT, from which SAFFL derives), pop.randomized.rule (ITTFL);
- behind no number of the three tables: date.studyday.origin,
  disp.status.record, trt.end.source, trt.planned.source (on the sheet).

So the panel of a TEAE count does not show the AE start-date imputation
decision at all, and shows the treatment-start decision without its
alternatives. ADR-022 and the report describe section 2 as implemented
("the records that bind the analysis or one of its elements"), so no
document is false; it is a gap against the issue's item 2, and the
acceptance (a citation or a house default) does not see it. What would fix
it: show, in section 3, the decision block of every record that binds a
column of the chain (or give the sheet rows the alternatives), or say in
ADR-022 that a column's decisions are shown as links and upstream ones not
at all; the owner may prefer either.

### F3 (not blocking) The acceptance and the page check hold the model for most of what they claim of the page

`check.acceptance` reads the page only for "opens a panel" (an anchor
`c-<cell>` and a link to it, check.py:135-152). "Reaches SDTM" and "a
citation or a house default" are decided on the review model
(`_reaches_sdtm`, `_supported`, check.py:180-216), and "the sheet lists
every decision" on `review.sheet` (check.py:166-172). The citation check
counts "awaiting approval" over the whole page against the number of
citations (check.py:109-114), not per citation. Planted on the review of
tests/unit/test_viewer.py (R3):

- `page._column` replaced to print only the column's ID (no derivation, no
  "Down to SDTM"): `page_problems` [], `acceptance` [];
- `page._sheet` replaced by an empty section: `acceptance` []
  (`page_problems` sees only the link of a panel to the missing row,
  `#s-demo.sex_(mod-demographics)`);
- one citation's "awaiting approval" moved into another citation: 3
  citations, 3 marks, `page_problems` [].

D13's "a decision left off the sheet" and "an entry of the catalog left off
the sheet" plant in the model (`off.sheet = ...`), not in the page. Also,
what the review could not read (`review.problems`, model.py:298 and 353:
no recomputation, an ARD row missing for a cell) is printed on the page but
counted neither by `specfirst view` (command.py:58) nor by the gate's check
`review` (gates.py, `_review`). Since the page is a deterministic function
of the model this is no defect of the pilot's page; it is a claim of the
checks (check.py's docstring, D13's) wider than what they read. What would
fix it: read the page back (per cell, the SDTM codes in its panel; per
record and catalog key, a sheet row by `data-key`; per citation element,
its approval words; `review.problems` counted), or say in ADR-022 decision
9 and check.py that the acceptance holds the model the page is written
from.

### F4 (not blocking) Page references without page numbers give no edge and no count; the report says otherwise

Nine AE analyses of the example (An07_01_TEAE, An07_09_Soc and
An07_10_SocPt, each its summary and its two Fisher comparisons) reference
CDISCPILOT01_SAP with the label "11.2. Adverse Events" and no
`pageNumbers`. `add_citations` iterates
`page_ref.get("pageNumbers") or []` (graph.py:779): no edge and no count.
coverage.json on the build: `{"cites_edges_of_analyses": 29,
"quotes_verified": 29, "references_not_to_kit_documents": {}}`; the AE
summaries get the method's reference only ("7. GENERAL CONSIDERATIONS",
16 edges), the Fisher comparisons none. The report draft says "Its page
references (24 analyses and 2 methods) are judged, imported `cites` edges
now, from every analysis of a built grid to the page" (issue-31.md:47-51):
of the 24 analyses, 13 give edges (An01_05 and the 12 of the
demographics), 9 give none, 2 are not built (vital signs). ADR-022 decision
5 counts the references that give no edge because the kit lacks their
document; a reference without a page also gives no edge and is counted
nowhere. What would fix it: count references without pages
(or find the label in the whole document and say so), and correct the
report's sentence.

### F5 (not blocking) The `formats` entries of a result set the kit does not have are never read

`display_checks` reads `formats.get(spec.id, {})` for each result set of
the kit (build.py:559) and fails on the unused entries of that set
(build.py:613). An entry under any other key (a misspelt result set) is
neither used nor reported, while ADR-022 decision 6 says "an entry that no
cell differs by fails". Planted on the build (R6): an entry of the Fisher
p-value of a term under the key `common-safety-display` (the result set is
`common-safety-displays`): `display_checks` passes (`True`) and no line
names it. What would fix it: fail on a key of `formats` that is not a
result set of the kit, as the section `cells` does for an output
(build.py:545-547).

### F6 (not blocking) The sheet's lines that are no record, and the P4 kind

- model.py:454-465: the kit's binding and each layout are marked `study
  customized` with the status `stated` and no citation. The binding
  `summary.continuous: quantile_definition = "sas5"` is the house's default
  (the record `tfl.quantile.definition` (tfl-demographics) with the same
  value is marked `house default`). The issue asks for each line "house
  default or study customized, with its citation".
- page.py:93: a P4 class other than `unseparated` and `not tested`
  (separated, inert, separated at dataset level only) is drawn with the
  kind `static`, whose legend says "read from the specification or the ARS
  file by a script"; a P4 class comes from a run. Not reached until `--p4`
  is used (catalog-2c).

What would fix it: mark a binding by the house's value where the house has
one and say where a binding or a layout comes from; draw a P4 class with a
kind of its own.

### F7 (not blocking) Small errors of the documents

- Out14-1-1.yaml:16-17: "That is the decision tfl.decimals.rule of the
  pilot's records (gold/decisions/safety.jsonl)". No record of
  tfl.decimals.rule exists: it is one of the four entries without a record;
  the record is custom:demog-decimals (ADR-022 decision 7).
- ADR-003 records its amendments in sections of its own ("Amendment of
  real-5a", line 377; "Amendment of real-5b", line 424); ADR-022 decision 6
  and the state file call the layout pieces "ADR-003, amendment of issue
  #31", and ADR-003 has no such section.
- ADR-022 decision 6, "One differs by display only": true, and on
  Out14-1-1 another 14 cells differ from the example by results classed
  `reference_error` in the section `results` (the gate's log: "14 cells
  differ by a result classed reference_error"); a reader of decision 6
  takes "one" for all.

## What was read

- CLAUDE.md; docs/decisions/ADR-022.md; docs/state/real.md, section "Handed
  over by issue #31"; docs/reports/issue-31.md (draft); ADR-003's
  amendments (to compare).
- The whole diff `e123599..db50a40`: src/specfirst/viewer/ (all four
  modules, in full), machine/layout.py, grid.py (`plan`, `fill`,
  `compare_reference`), results.py (`load_formats`), graph.py
  (`add_citations`), decisions.py, build.py, kit.py, gates.py, cli.py,
  recompute/generate.py; the kit's kit.yaml, the two layouts,
  exceptions.yaml (section `formats`), safety.jsonl (every record);
  tests/unit/test_viewer.py, test_layout_terms.py, test_citations.py,
  test_safety_records.py, the changes of test_kit.py, test_grid.py,
  test_gates.py, tests/defects/test_defects.py (D13 and the D7/D8/D9/D11
  changes).
- Readers of the kit format outside the diff: harness/pilot.py,
  score/pilot.py, gen/separate.py, kit.py `lock`; the grid schema
  (`spanner` since base-0); the decision-record schema (statuses).
- The kit's documents, read from the fetch cache without writing to it:
  the SAP (sections 6, 7, 9, 11, and the templates of 13.2: Templates 2, 3,
  13 and 14 in full, the p-value masks of all, by poppler's pdftotext
  24.02.0; SHA-256 `210b7f1f...`, the kit's), the
  Define-XML of ADaM (`7e6d580e...`, the comments of ADSL.TRTSDT, TRTEDT,
  TRT01P, AGEGR1, RACE, SAFFL, HEIGHTBL, WEIGHTBL, DCDECOD, ADAE.ASTDT,
  ASTDY, TRTEMFL, AEREL), CDISC's ARS example "Common Safety Displays.json"
  (groupings, data subsets, `documentRefs`, result patterns); catalog@2's
  entries tfl.population, tfl.pvalue.format, tfl.ae.socpt.counts,
  tfl.demog.rows; open-default@2's STANDARD.md anchors.
- The author's clean-clone gate log of `db50a40`,
  build/gates/issue-31/clean-clone.log (GATE issue-31: PASS), and the build
  of that clean clone (read only).

## What was run

All under WSL Ubuntu-24.04 as root, on a clone of the repository at
`db50a40` in /tmp/review31 (`git clone --no-local`, `checkout --detach
db50a40`), with the installed environment of scripts/env.sh and
`PYTHONPATH=/tmp/review31/src PYTHONDONTWRITEBYTECODE=1`; builds, tests and
checks under `flock /run/lock/specfirst-heavy.lock taskset -c 0-3`.

### R1 The records against the catalog and the house

A script loading `houses.load_pair(root, "catalog@2", "open-default@2")`
and running `decisions.catalog_problems` and `decisions.house_values` on
every record of safety.jsonl:

    records 48 Counter({'default': 20, 'stated': 15, 'conflict': 7, 'asked': 6})
    custom 4
    catalog keys 61
    keys of the seven units 48
    not taken in the seven units [('demo.baseline.record', 'mod-demographics'),
      ('demo.bmi.rule', 'mod-demographics'), ('pop.efficacy.rule', 'mod-populations'),
      ('tfl.decimals.rule', 'tfl-demographics')]
    not taken at all 17
    tfl.population      tfl-demographics  asked     house=[{"rule": "randomized"}]     []
    tfl.pvalue.format   tfl-demographics  asked     house=[{"rule": "three_decimals"}] []
    tfl.ae.socpt.counts tfl-ae-soc-pt     default   house=[{"rule": "subjects"}]       []
    (every record: catalog_problems [])

The SAP's templates (pdftotext -layout of the cached SAP.pdf, the lines
condensed):

    page 22:  Population: Intent-to-Treat
              Template 3
              Summary of Demographic and Baseline Characteristics
              ...   Age (y)  ...  Mean xx.x  SD x.xx  Median xx.x  Min. xx.x  Max. xx.x
              ...   <65 yrs  xx (xx%) ...  0.xxx
    page 32:  Population: Safety
              Template 13
              Incidence of Treatment Emergent Adverse Events by Treatment Group
              ...   n (%)   Events   ...   p-value[1]
              Subjects with at least one AE    xx (xx%)  xxx  ...  0.xxx  0.xxx
              Note: Total Events represent the total number of times an event was
              recorded ...

The build's baseline rows (gold/spec/spec/yamaa/pilot-program/adsl_v1.yaml of
the build): `BASE_HT` filter `VS.VSTESTCD = 'HEIGHT'`, ordered by VISITNUM,
keep first; `BASE_WT` filter `VS.VSTESTCD = 'WEIGHT' AND VS.VSBLFL = 'Y'`.
The Define-XML: HEIGHTBL "VSSTRESN when VS.VSTESTCD='HEIGHT' and
VS.VISITNUM=1", WEIGHTBL "... VS.VISITNUM=3".

### R2 The review of the built pilot

The inspection script (model, page, checks of the built review) on the
reviewer's build (R4: build/kits/cdiscpilot01 and build/recompute of the
clone) and, before it, read only, on the build of the author's clean clone
of `db50a40` (its build/p1/cdiscpilot01/first): the same output on both.
The two pages, from two builds on two clones, have the same SHA-256,
`18009f5ea46f475f41aef7e5325e3285925835b3273a9a12ffc4487fe338d1e3`.

    page bytes 3515425 same as html(): True
    problems of the review []
    page_problems []
    Out14-1-1: 84 printed numbers; 84 open a panel; 84 reach SDTM; 84 reach a citation or a house default
    Out14-3-1-1: 27 printed numbers; 27 open a panel; 27 reach SDTM; 27 reach a citation or a house default
    Out14-3-2-1: 1178 printed numbers; 1178 open a panel; 1178 reach SDTM; 1178 reach a citation or a house default
    sheet: 17 catalog entry, 1 kit binding, 8 layout, 66 record; 66 of 66 records listed
    acceptance problems []
    cells 1502 analyses 61
    awaiting approval count 2069 citations 2069
    safety records 48
    in section 2 of some panel 37
    only as a column link (section 3): ['ae.teae.end (mod-ae-emergence)',
      'custom:demog-baseline-visits (mod-demographics)', 'demo.age.groups (mod-demographics)',
      'trt.start.source (mod-treatment)']
    bound only to upstream columns (on no panel): ['ae.start.imputation (mod-ae-emergence)',
      'pop.randomized.rule (mod-populations)', 'trt.date.imputation (mod-treatment)']
    on no panel at all: ['date.studyday.origin (mod-treatment)', 'disp.status.record (mod-populations)',
      'trt.end.source (mod-treatment)', 'trt.planned.source (mod-treatment)']
    coverage documents {'cites_edges_of_analyses': 29, 'quotes_verified': 29,
      'references_not_to_kit_documents': {}}
    adam:ADSL.TRTSDT | comment: SV.SVSTDTC when SV.VISITNUM=3, converted to SAS date |
      rule: {"value": {"impute": {"day": 1, ..., "month": 1, "source": "EX_MINDTC", "type": "date"}}} |
      src gold/spec/spec/yamaa/pilot-program/adsl_v1.yaml:327 | decisions ['trt.date.imputation
      (mod-treatment)', 'trt.start.source (mod-treatment)']

The page references of the example (a script over its `documentRefs`):

    ('An01_05_SAF_Summ_ByTrt', 'CDISCPILOT01_SAP', 'PhysicalRef', '6. ANALYSIS POPULATIONS', [9])
    ('An03_01_Age_Summ_ByTrt', 'CDISCPILOT01_SAP', 'PhysicalRef', '9.2. Demographic and Baseline Characteristics', [13])
    ... (the 12 analyses of the demographics, page 13)
    ('An07_01_TEAE_Summ_ByTrt', 'CDISCPILOT01_SAP', 'PhysicalRef', '11.2. Adverse Events', None)
    ... (the 9 AE analyses, no page)
    ('Mth01_CatVar_Summ_ByGrp', 'CDISCPILOT01_SAP', 'PhysicalRef', '7. GENERAL CONSIDERATIONS FOR DATA ANALYSES', [9])

### R3 Planted page defects on the review of test_viewer.py

    unchanged: [] []
    1. no SDTM, no derivation on the page; 'Down to SDTM' in page: False
       page_problems: []
       acceptance: []
    2. no sheet rows on the page; 'demo.sex' rows: 1
       page_problems: ["the link '#s-demo.sex_(mod-demographics)' has no anchor on the page"]
       acceptance: []
    3. counts: citations 3 awaiting 3
       page_problems: []

### R4 Build, check, recompute, view on the clone

    $ python -m specfirst kit assemble cdiscpilot01
    kit cdiscpilot01: 67 files match their pinned SHA-256 (26 inputs, 41 gold) in /tmp/review31/build/kits/cdiscpilot01
    $ python -m specfirst build cdiscpilot01
    build cdiscpilot01: 10 datasets, 5053 nodes, 10343 edges, 64 files in /tmp/review31/build/kits/cdiscpilot01
    $ python -m specfirst check cdiscpilot01          (exit 0)
    P2 reproduction: 10 of 10 datasets equal their reference (numeric tolerance 1e-10)
    grid Out14-1-1: 104 cells, 84 print a number; 84 of the 84 cells with results have a complete path to SDTM columns
    grid Out14-3-2-1: 1275 cells, 1178 print a number; 1178 of the 1178 cells with results have a complete path to SDTM columns
    trace: complete
    results common-safety-displays, Python engine: 3735 embedded results, 3711 reproduced as printed, 23 with another value, 1 without a result of ours
    results common-safety-displays, Python engine: 0 unexplained
    results common-safety-displays, R engine: ... 0 unexplained
    grid Out14-1-1: 104 cells show 147 results; 90 cells equal the reference's formatted values, 14 differ, 14 of them with one class
    grid Out14-1-1: the R engine's rows give the same grid; the mock shell and the two pages hold; 0 problems
    grid Out14-3-1-1: 27 cells show 51 results; 27 cells equal the reference's formatted values, 0 differ, 0 of them with one class
    grid Out14-3-2-1: 1275 cells show 1940 results; 866 cells equal the reference's formatted values, 1 differ, 1 of them with one class
      results the reference gives no formatted value for: 408 (their cells are not compared)
    grid Out14-3-2-1: the R engine's rows give the same grid; the mock shell and the two pages hold; 0 problems
    grids: 8 outputs, pass
    $ python -m specfirst recompute cdiscpilot01      (exit 0)
    cdiscpilot01: 69 analyses: reproduced 69
    static check: 69 of 69 scripts pass it (imports, calls, reads, texts and numbers; ADR-021, decision 5)
    recompute cdiscpilot01: PASS
    $ python -m specfirst view cdiscpilot01           (exit 0)
    Out14-1-1: 84 printed numbers; 84 open a panel; 84 reach SDTM; 84 reach a citation or a house default
    Out14-3-1-1: 27 printed numbers; 27 open a panel; 27 reach SDTM; 27 reach a citation or a house default
    Out14-3-2-1: 1178 printed numbers; 1178 open a panel; 1178 reach SDTM; 1178 reach a citation or a house default
    Out14-3-01: 40 printed numbers; 40 open a panel; 40 reach SDTM; 40 reach a citation or a house default
    (Out14-3-03 40, Out14-3-05 40, Out14-3-11 15, Out14-3-13 78: the same)
    sheet: 17 catalog entry, 1 kit binding, 8 layout, 66 record; 66 of 66 records listed
    view cdiscpilot01: /tmp/review31/build/kits/cdiscpilot01/viewer/index.html (3515425 bytes), 61 analyses, 1502 cells with a panel, 92 lines on the sheet; 0 problems

### R5 Unit tests and planted defects

    $ python -m pytest -q tests/unit/test_viewer.py tests/unit/test_layout_terms.py \
        tests/unit/test_citations.py tests/unit/test_safety_records.py tests/unit/test_kit.py \
        tests/unit/test_grid.py tests/unit/test_gates.py
    154 passed in 1.62s
    $ SPECFIRST_STRICT=1 python -m pytest -q -s tests/defects -k "D7 or D8 or D13"
    --- D13-review
    planted, a cell without a panel: 1 problems, for example: cell:Out14-3-2-1/r1/c1: prints '(N=86)' and opens no panel
    planted, a script: 1 problems, for example: the page has a <script>
    planted, a handler: 1 problems, for example: the page has the handler 'onmouseover'
    planted, a link that leaves the page: 1 problems, for example: the link 'https://example.org/' leaves the page
    planted, a judged edge drawn as proven: 1 problems, for example: citation 1 is drawn executed, not judged
    planted, an unseparated decision drawn as proven: 4 problems, for example: the decision ae.related.values (mod-ae-emergence) is unseparated and not drawn so
    planted, a decision left off the sheet: 2 problems, for example: the sheet does not list the decision ae.related.values (mod-ae-emergence)
    planted, an entry of the catalog left off the sheet: 1 problems, for example: the sheet does not list the entry pop.efficacy.rule (mod-populations) of the catalog
    planted in the graph files, the derives_from edges of ADSL.AGEGR1 left out: 7 cells seen
    planted in the exceptions, a difference of display no cell shows: passes False
    3 passed, 97 deselected in 33.64s

(D7 and D8 print their plants in Out14-3-1-1: the reads edge to
ADAE.TRTEMFL, the shows edges of cell:Out14-3-1-1/r2/c1, a result node,
every computes edge, every reads edge: each seen.)

### R6 Plants on the build

`build.decision_checks` on the build, as the gate's check `decisions` runs
it:

    decision_checks passes: True
    decisions: 66 records, 66 IDs; 99 options of analyses held against the decisions that set them;
      the last visit held on the model records of 3 analyses; 92 quotes held against their documents; 0 problems
    decisions: citations of sources that are no document of the kit, not checked by script: answers 5
    decisions: by class: 30 document_rule, 6 gold_quirk, 20 house_default, 7 no class (conflict),
      3 study_input; by status: 7 asked, 7 conflict, 20 default, 32 stated

`build.display_checks` with `results.load_formats` patched (as D13 does) to
add the entry `{"result": "ard:An07_09_Soc_Comp_ByTrt_PlacHigh/Mth03_CatVar_Comp_FishEx_1_pval/*/=X",
"formatted": "1", "class": "reference_error", "proof": {"kind":
"not_its_own_pattern"}}` under the key `common-safety-display`:

    formats entry under an unknown result set: display_checks passes True ; lines naming it: []

### R7 Rules, worktree, clone

    $ git diff e123599 db50a40 | LC_ALL=C grep -n '[^[:print:][:space:]]'     (nothing)
    $ git status --short        (the worktree at db50a40, before this file: nothing; the clone after every run: nothing)

and a search of the added lines of the diff for home folders, Windows user
folders, mount points of a drive, and the words token, password, secret
and the prefix of a GitHub token: nothing.

The author's clean-clone gate of `db50a40` (build/gates/issue-31/clean-clone.log),
read: every check PASS (unit tests 549.7 s, 1391 passed; P1 55.4 s; review
1.1 s: "the second build of P1 gives the same page: True"; planted defects
168.1 s, 100 passed); "GATE issue-31: PASS". Pass 2 reviews the logs of
part 2.

Pass 1 verdict (the code at `db50a40`): NOT SIGNED (F1).

## Pass 2: the fixes of the findings, commit `5671c8b`

Reviewed: the diff `db50a40..5671c8b` (19 files, 645 insertions, 224
deletions), commit `5671c8b` ("issue-31: the findings of the first review
(F1 to F7)"), child of `db50a40`. The worktree was clean at `5671c8b` but for
this file. The report's `@@` placeholders are still unfilled; the report and
the logs of the seven clean-clone gates come in part 2 of this pass.

### The findings of pass 1

- **F1 (was blocking): closed.** The owner answered on 2026-11-22 (ADR-022,
  "The owner's answer"): a SAP mock table states what it shows, its masks
  included. safety.jsonl was read again against the SAP's text, the list of
  tables (13.1.1), Template 3, Template 13 and section 11.4. It now has 49
  records: 18 stated, 12 default, 17 conflict, 2 asked (R9). Every case of
  F1 has the status decision 7 defines, and each conflict cites the line
  that says otherwise:
  - tfl.population (demographics): `conflict`, "Population:
    Intent-to-Treat";
  - tfl.pvalue.format: `conflict`, the mask `0.xxx`;
  - tfl.ae.socpt.counts: `conflict`, Template 13's "n (%) Events" and its
    note on total events;
  - custom:demog-decimals: `conflict` (minimum and maximum `xx.x`);
  - tfl.percent.format (two units): `conflict`, the mask `xx (xx%)`;
  - tfl.population and tfl.columns.arms (organ class and term) and
    tfl.columns.arms (demographics): `stated`;
  - custom:demog-baseline-visits: `conflict`, holding the build's rows
    (first height by VISITNUM, weight with VSBLFL = 'Y') against SAP 9.2
    and the two Define-XML comments.

  The second reading found more: tfl.output.include (AE summary) is a
  `conflict` (13.1.1 lists no AE summary); tfl.ae.summary.rows is a
  `conflict` (11.4: no formal summary of AEs leading to discontinuation);
  custom:socpt-pvalue-format is a new `conflict` (four decimals against
  `0.xxx`; catalog@2's tfl.pvalue.format has the demographics unit only).
  Checks on these records:
  - every quote of the 49 records stands in the reviewer's own pdftotext
    text of the cached SAP or in the Define-XML ("quotes not found: 0");
  - every catalog record still fits catalog@2;
  - no `asked` record has the house's value;
  - the SAP's note (13.1.3) that ADR-022 and the report quote is there;
  - the decisions check: 67 records, 102 quotes, 0 problems.

  The lists for the owner in ADR-022, the report and docs/state/real.md
  name the 17 conflicts and the 2 asked records as the file has them. They
  now count the conflicts as 4 of the modules, 8 of the demographics, 2 of
  the AE summary and 3 of the table by organ class and term.

  One judgment is left as it was, and needs no finding: tfl.ae.socpt.sort
  stays `default` although Template 13's example rows are A to Z. ADR-022
  says a mock table states its population, its columns and their order,
  and its masks; it does not say the order of its rows.
- **F2: closed.** Section 2 of a panel now draws, after the records of the
  analysis, a full decision block for every record that binds a column of
  its derivation chain. Each block has its statement, alternatives,
  citations, mark and P4 class, and says which column it binds through
  which column read (model.py `_column_decisions` and `behind`; page.py
  `_via`). On the build, 45 of the 49 safety records stand behind some
  number of the three tables. The panel of the TEAE count now draws:
  - ae.teae.end through TRTEMFL;
  - ae.start.imputation through ADAE.ASTDT and TRTEMFL;
  - trt.date.imputation and trt.start.source through ADSL.TRTSDT and
    TRTEMFL;
  - pop.randomized.rule through ADSL.ITTFL and SAFFL.

  The four that no number reads (date.studyday.origin, disp.status.record,
  trt.end.source, trt.planned.source) are on the sheet, as the report's
  "What is not done" now says. The acceptance holds it: "every decision
  behind" a number is drawn as a block in its panels, and D13 plants
  ae.start.imputation off the panels (1199 cells seen).
- **F3: closed.** `check.acceptance` reads the page back:
  - a cell's block must stand inside a panel;
  - the "Down to SDTM" lines of the cell's panels must name every SDTM
    column its columns reach;
  - a panel must draw a citation or a house-default mark;
  - the decision blocks are read by key;
  - the sheet rows are read by `data-key`.

  `page_problems` checks the approval words of each citation.
  `review.problems` is counted by `specfirst view` (command.py) and by the
  gate's check `review` (gates.py `_review`). The pass-1 plants run again
  on the toy review (R10):
  - the page without derivations and "Down to SDTM" lines fails the
    acceptance;
  - the page without the sheet's rows fails it ("the sheet does not list
    the decision ...");
  - one citation's approval words moved into another citation fail
    `page_problems` ("citation 1 is not marked awaiting approval or
    approved by a person").

  D13 plants the sheet rows and the "Down to SDTM" lines in the page
  itself (R11).
- **F4: closed.** A reference without `pageNumbers` gives an edge to
  `doc:<document>#<label>`, verified where the label stands anywhere in the
  document's text, and counted in `edges_to_a_whole_document`. On the
  build, coverage.json has `{"cites_edges_of_analyses": 38,
  "edges_to_a_whole_document": 9, "quotes_verified": 38,
  "references_not_to_kit_documents": {}}`, to 4 spans, none approved. The
  report's sentence now says what the build has: 13 analyses and the
  methods name a page, the 9 AE analyses name 11.2 without a page, and the
  2 vital-sign analyses are not built. The unit test adds a reference
  without a page.
- **F5: closed.** A key of `formats` that is not a result set of the kit
  with a grid fails (build.py, `display_checks`). The pass-1 plant (an
  entry under `common-safety-display`) now gives `display_checks passes
  False`. D13 plants the same kind of key ("passes False").
- **F6: closed.** The sas5 binding is marked `house default` through the
  compile template of catalog@2's tfl.quantile.definition, and its line
  says so. The layout lines say where they come from (status `kit layout`).
  A P4 class other than `unseparated` or `not tested` is drawn with a kind
  of its own, `tested`, with its legend. The page check fails on a tested
  class drawn otherwise (unit test).
- **F7: closed.**
  - Out14-1-1.yaml:16-17 names custom:demog-decimals.
  - ADR-003 has "Amendment of issue #31 (2026-11-22)", with the three
    pieces as the code has them.
  - ADR-022 decision 6 names the 14 cells of Out14-1-1 classed by the
    section `results`.

### New findings

None. The code of the fixes was read in full (check.py, model.py, page.py,
command.py, gates.py `_review`, build.py, graph.py, csr.py), with the
changed tests. Nothing in the diff claims std-2's check: the state file
leaves to std-2 whether the baseline rows give the same values as Visit 1
and Visit 3. The diff has no byte outside ASCII and no local user path,
credential or token.

### What was run in pass 2

The clone /tmp/review31 fetched and checked out at `5671c8b`, its build
folder removed. Then, under one hold of `flock
/run/lock/specfirst-heavy.lock taskset -c 0-3`, as in pass 1:

#### R8 Build, check, recompute, view

    $ python -m specfirst kit assemble cdiscpilot01; python -m specfirst build cdiscpilot01   (exit 0, 0)
    $ python -m specfirst check cdiscpilot01          (exit 0)
    P2 reproduction: 10 of 10 datasets equal their reference (numeric tolerance 1e-10)
    trace: complete
    results common-safety-displays, Python engine: 0 unexplained  (and R; and the two efficacy sets)
    grid Out14-1-1: 104 cells show 147 results; 90 cells equal the reference's formatted values, 14 differ, 14 of them with one class
    grid Out14-3-2-1: 1275 cells show 1940 results; 866 cells equal the reference's formatted values, 1 differ, 1 of them with one class
    grids: 8 outputs, pass
    $ python -m specfirst recompute cdiscpilot01      (exit 0)
    cdiscpilot01: 69 analyses: reproduced 69
    $ python -m specfirst view cdiscpilot01           (exit 0)
    Out14-1-1: 84 printed numbers; 84 open a panel; 84 reach SDTM; 84 reach a citation or a house default; 84 draw every decision behind them
    Out14-3-1-1: 27 printed numbers; 27 open a panel; 27 reach SDTM; 27 reach a citation or a house default; 27 draw every decision behind them
    Out14-3-2-1: 1178 printed numbers; 1178 open a panel; 1178 reach SDTM; 1178 reach a citation or a house default; 1178 draw every decision behind them
    (Out14-3-01, -03, -05, -11, -13: 40, 40, 40, 15, 78; the same)
    sheet: 17 catalog entry, 1 kit binding, 8 layout, 67 record; 67 of 67 records listed
    view cdiscpilot01: .../viewer/index.html (3885495 bytes), 61 analyses, 1502 cells with a panel, 93 lines on the sheet; 0 problems

The page has the SHA-256
`1d1735e46dd7ac1cdc5d8f5445e7e24e663999c35be08224954f327fd70a4003`. The page
of the author's clean-clone gate on `5671c8b` has the same SHA-256 (two
builds, two clones).

#### R9 The review and the records

The inspection script on the build:

    page bytes 3885495 same as html(): True
    problems of the review []
    page_problems []
    acceptance problems []
    sheet kinds Counter({'record': 67, 'catalog entry': 17, 'layout': 8, 'kit binding': 1}) lines 93
       kit binding | common-safety-displays: summary.continuous.quantile_definition | kit binding | house default |
         summary.continuous: quantile_definition = "sas5", bound in kit.yaml (the ARS file leaves it to code);
         the alternative sas5 of the catalog's tfl.quantile.definition (tfl-demographics), the house default
    safety records 49 behind some number 45
    behind no number of the three tables: ['date.studyday.origin (mod-treatment)', 'disp.status.record
      (mod-populations)', 'trt.end.source (mod-treatment)', 'trt.planned.source (mod-treatment)']
    TEAE column decisions: [('ae.teae.end (mod-ae-emergence)', 'adam:ADAE.TRTEMFL', 'adam:ADAE.TRTEMFL'),
      ('ae.start.imputation (mod-ae-emergence)', 'adam:ADAE.ASTDT', 'adam:ADAE.TRTEMFL'),
      ('trt.date.imputation (mod-treatment)', 'adam:ADSL.TRTSDT', 'adam:ADAE.TRTEMFL'),
      ('trt.start.source (mod-treatment)', 'adam:ADSL.TRTSDT', 'adam:ADAE.TRTEMFL'),
      ('pop.randomized.rule (mod-populations)', 'adam:ADSL.ITTFL', 'adam:ADSL.SAFFL')]
    coverage documents {'cites_edges_of_analyses': 38, 'edges_to_a_whole_document': 9,
      'quotes_verified': 38, 'references_not_to_kit_documents': {}}

The records against the documents and the catalog (`decisions.Quotes` on
the reviewer's pdftotext text of the cached SAP and on the Define-XML;
`catalog_problems`; `house_values`):

    records 49 Counter({'stated': 18, 'conflict': 17, 'default': 12, 'asked': 2})
    quotes not found: 0
    13.1.3 sentence in the SAP: True
    (no CATALOG problem, no ASKED BUT HOUSE DEFAULT line)

`build.decision_checks` on the build:

    decisions: 67 records, 67 IDs; 99 options of analyses held against the decisions that set them;
      the last visit held on the model records of 3 analyses; 102 quotes held against their documents; 0 problems
    decisions: citations of sources that are no document of the kit, not checked by script: answers 5

#### R10 The pass-1 plants against `5671c8b`

On the toy review of tests/unit/test_viewer.py (as in R3):

    1. no SDTM, no derivation on the page; 'Down to SDTM' in page: False
       page_problems: []
       acceptance: ['cell:Out_X/r2/c1: its panel reaches no SDTM column through every column it reads']
    2. no sheet rows on the page
       acceptance: ['the sheet does not list the decision demo.sex (mod-demographics)',
                    'the sheet does not list the decision pop.safety.rule (mod-populations)']
    3. the approval words of the first citation moved into the second (5 citations, 5 marks before and after):
       page_problems: ['citation 1 is not marked awaiting approval or approved by a person']

On the build, the `formats` entry under `common-safety-display` (as in
R6): `display_checks passes False`.

#### R11 Unit tests, planted defects, lint

    $ python -m pytest -q tests/unit/test_viewer.py tests/unit/test_layout_terms.py \
        tests/unit/test_citations.py tests/unit/test_safety_records.py tests/unit/test_kit.py \
        tests/unit/test_grid.py tests/unit/test_gates.py
    158 passed in 2.60s
    $ SPECFIRST_STRICT=1 python -m pytest -q -s tests/defects -k "D7 or D8 or D13"
    planted, a decision left off the sheet: 2 problems, for example: the sheet does not list the decision ae.related.values (mod-ae-emergence)
    planted, an entry of the catalog left off the sheet: 1 problems, for example: the sheet does not list the entry pop.efficacy.rule (mod-populations) of the catalog
    planted, the decision ae.start.imputation (mod-ae-emergence) left off the panels: 1199 problems, for example: cell:Out14-3-1-1/r2/c1: its panel does not draw the decision ae.start.imputation (mod-ae-emergence)
    planted, no SDTM column named in the panels: 1289 problems, for example: cell:Out14-1-1/r1/c1: its panel reaches no SDTM column through every column it reads
    planted in the exceptions, a difference of display under common-safety-display: passes False
    (and the plants of pass 1: each seen)
    3 passed, 97 deselected in 38.38s
    $ ruff check src tests
    All checks passed!
    $ git status --short        (the clone after the runs: nothing)

The author's clean-clone gate of `5671c8b` (build/gates/issue-31/clean-clone.log),
read: "commit: 5671c8b", every check PASS (unit tests 1395 passed; review:
"67 of 67 records listed", "the second build of P1 gives the same page:
True"; decisions: 102 quotes, 0 problems; planted defects 100 passed);
"GATE issue-31: PASS".

This verdict is on the code and the records at `5671c8b`. The verdict on
the whole package waits for part 2 of this pass: the report with its
placeholders filled and the logs of the seven clean-clone gates.

Pass 2 verdict (the code and the records at `5671c8b`): SIGNED.

## Pass 3: the merge of main and the P4 part, commit `78fb49b`

Reviewed: the two commits after `5671c8b` on track/real.

- `b23dafb`, the merge of main `0046194` (catalog-2c) into track/real.
  Parents: `5671c8b` and `0046194`.
- `78fb49b`, "P4 on the page holds a class at the value it was found at"
  (ADR-022 decision 8). It changes viewer/command.py, model.py and
  page.py, ADR-022, docs/state/real.md, D13 and test_viewer.py.

The worktree at `78fb49b` has this untracked file and an uncommitted
change of docs/reports/issue-31.md that is not mine (the report, for part
2). Neither was reviewed here as code.

### The merge `b23dafb`

- **Files changed on both sides** since the merge base `e123599`:
  CLAUDE.md and src/specfirst/gates.py only.
- **CLAUDE.md** (the one conflict):
  - against main, the merged file differs only in the kit line, which
    keeps `specfirst view <kit> [--p4 FILE]` of #31;
  - against `5671c8b`, it takes main's catalog line (default pair
    `catalog@2`, `open-default@2`) and the gen line with `--vector house`.

  The resolution is right.
- **gates.py**: main changed the std-1 checks only (they now name
  `catalog@1` / `open-default@1` by label). At `78fb49b` the issue-31 gate,
  `PILOT_GRIDS`, `REVIEW_OUTPUTS`, `REVIEW_DEFECTS` and `_review` (with
  `review.problems` counted) are as at `5671c8b`.
- **The standard and the kit**: the merge changes nothing under
  standard/ or kits/. catalog@2 and open-default@2 were frozen before
  #31, so the records, their statements and the house defaults the viewer
  and the decisions check read are those of pass 2.
- **score/pilot.py** (read-1a, rewritten in part by catalog-2c):
  - it takes `kit.results[0]`, which is still `common-safety-displays`;
  - it finds Out14-3-1-1 by its ID (`next(... output == OUTPUT)`);
  - its `key_grid` calls `grid.plan(event, layout, None)`, `cell_text`,
    `template_of` and `cell_rows` on a layout of header and statistics
    blocks only. #31 left the planning of those blocks as it was;
    `cell_rows` drops only the empty ARD IDs of a terms placeholder, which
    this layout has none of.
- **Readers of `Kit.decisions`** (a tuple since #31): build.py,
  recompute/generate.py, viewer/model.py and tests/defects. The `.decisions`
  that gen/, score/ and harness/ use are those of reading and owner
  objects, not of `Kit`. harness/pilot.py still writes an empty
  gold/decisions.jsonl.
- **Runs on the merge's code**, within R12 at `78fb49b`:
  - `specfirst score pilot` exits 0;
  - tests/score passes (4, `SPECFIRST_STRICT=1`);
  - build, check, recompute and view pass on all eight outputs;
  - D7 and D8 pass.

### The P4 part `78fb49b`

**The rule.** A class of the matrix is drawn only where the record's value,
as canonical JSON, equals the matrix's `value`. This is right for what a
class says. `specfirst.machine.separation.classify` decides a class at the
gold value:
- `separated`: every other value tried separates from the gold;
- `unseparated`: some value gives the same outputs as the gold;
- `inert`: no output reads it.

A record at another value B is a different point. The class at A says
nothing of how B compares with the third values, so "not tested" is the
only safe drawing.

**Is a class at another value ever drawn?** No. The comparison is exact on
canonical JSON, so a value of another shape is drawn "not tested", never
classed. On the reviewer's build with the coordinator's matrix (R12):
- for every record, the drawn class equals the rule's ("against the rule:
  []");
- no decision block or sheet row drawn `tested` or `unseparated` has a value
  other than the matrix's.

The matrix holds 22 decisions (8 separated, 9 unseparated, 5 inert). 21
have a record; 14 are at the matrix's value. The 7 others are real value
differences, not shapes: trt.actual.source, trt.start.source,
trt.end.source, trt.date.imputation, ae.start.imputation, ae.teae.end and
tfl.ae.summary.rows. Each is drawn "not tested" with the note "the P4 run
tried another value, <gold>: <class>". The sheet has P4 separated 6, inert
4, unseparated 4 and not tested 79, as the coordinator said. The page with
`--p4` has 0 problems, and its acceptance holds on the three outputs.

**Without `--p4`** the page stays as before: against the page of
`5671c8b` (6828 lines each), it differs in one line only, the legend of
`not-tested` ("... reaches the decision" becomes "... reaches the decision
at the value it has"). Every decision is "not tested" with no note.

#### P3-F1 (not blocking) A drawn class is the house vector's, not the kit's

The matrix is that of the house vector. Every decision of the four units
it covers was run with every other decision at the house's value. A
class drawn on the kit's page is therefore the class of the decision in
that vector's builds. The kit's own records differ from that vector in 7
of the matrix's 21 decisions. Also, the kit's reference build is Pilot 7's
specifications, not a build compiled from decisions.

Example: ae.teae.start is drawn "not proven by the data: unseparated" from
a run in which ae.teae.end was `last_dose_plus_days(days=30)` and
trt.start.source `first_ex_with_dose`. The kit's records hold `no_end` and
`first_ex_record`. Whether a class holds under the kit's own values is
what a run of the kit's vector would show, and the state file says that
run is not done.

ADR-022 decision 8 says the matrix "classes the kit's records where they
take the house's value", and the page's legend says "a run of the
decision's other values on the data gives its class". Neither says that
the run held every other decision at the house's value. No statement is
false, but the drawing invites more trust than the run gives.

What would fix it: say so in the legend or in each drawn class's note
("in the run of the house vector, every other decision at the house's
value") and in decision 8. Or draw a class only when the kit's records
equal the house vector on the decisions the class depends on. The owner may
prefer to wait for a kit-vector run.

#### P3-F2 (not blocking, latent) `no_alternative` would be drawn as tested

`separation.classify` returns `no_alternative` when no other value is
tried, and `P4Run`'s comment lists it. `page._p4` draws every class other
than `unseparated` and `not tested` with the kind `tested`, so it would
draw "P4: no_alternative", though nothing was run. The legend of `tested`
lists separated, inert and separated at dataset level only. The pilot's
matrix has no such decision, so the page of the pilot is not affected.

What would fix it: draw `no_alternative` as "not tested" with a note, or
give it a kind of its own.

### What was run in pass 3

The clone /tmp/review31 fetched and checked out at `78fb49b`, its build
folder removed. The page of `5671c8b` was kept aside first (SHA-256
`1d1735e4...`, as in pass 2). The matrix was copied from the coordinator's
scratch folder, read only: `cdiscpilot01-house.json`, `vector: house`,
units mod-treatment, mod-populations, mod-ae-emergence and tfl-ae-summary,
`problems: []`. I did not run `specfirst gen separate` again: it takes
about 22 minutes under the lock that the seven gates hold. The matrix is
the input whose use is reviewed here.

All of R12 ran under one hold of `flock /run/lock/specfirst-heavy.lock
taskset -c 0-3`.

#### R12 Build, the page without and with `--p4`, tests

    $ python -m specfirst kit assemble cdiscpilot01; build; check; recompute    (exit 0 each)
    P2 reproduction: 10 of 10 datasets equal their reference (numeric tolerance 1e-10)
    trace: complete
    grids: 8 outputs, pass
    cdiscpilot01: 69 analyses: reproduced 69
    $ python -m specfirst view cdiscpilot01           (exit 0)
    view cdiscpilot01: .../viewer/index.html (3885515 bytes), 61 analyses, 1502 cells with a panel, 93 lines on the sheet; 0 problems
    $ python -m specfirst view cdiscpilot01 --p4 matrix.json   (exit 0)
    sheet: 17 catalog entry, 1 kit binding, 8 layout, 67 record; 67 of 67 records listed
    view cdiscpilot01: .../viewer/index.html (3900321 bytes), 61 analyses, 1502 cells with a panel, 93 lines on the sheet; 0 problems

    inspection (model.load with command.read_p4 of the matrix; the written page):
    p4 page same as html(): True bytes 3900321
    p4 page_problems: []
    Out14-1-1: 84 printed numbers; 84 open a panel; 84 reach SDTM; 84 reach a citation or a house default; 84 draw every decision behind them
    Out14-3-1-1: 27 ...; 27 draw every decision behind them
    Out14-3-2-1: 1178 ...; 1178 draw every decision behind them
    p4 acceptance problems: []
      trt.planned.source (mod-treatment)     record {"rule": "dm_arm"}             drawn inert
      trt.actual.source (mod-treatment)      record {"rule": "same_as_planned"}    drawn not tested   note the P4 run tried another value, dm_actarm: separated
      trt.start.source (mod-treatment)       record {"rule": "first_ex_record"}    drawn not tested   note the P4 run tried another value, first_ex_with_dose: unseparated
      ae.teae.end (mod-ae-emergence)         record {"rule": "no_end"}             drawn not tested   note the P4 run tried another value, last_dose_plus_days(days=30): unseparated
      ae.teae.start (mod-ae-emergence)       record {"rule": "on_or_after_first_dose_date"}  drawn unseparated
      pop.safety.grouping (mod-populations)  record {"rule": "actual"}             drawn separated
      ... (21 lines, one per record the matrix reaches)
    records drawn: {'not tested': 53, 'inert': 4, 'unseparated': 4, 'separated': 6} against the rule: []
    sheet P4: {'not tested': 79, 'inert': 4, 'unseparated': 4, 'separated': 6}
    no-p4 page against 5671c8b's: 6828 and 6828 lines; 2 lines differ
        -<li><span class="kind not-tested">not-tested</span> not tested: no P4 run reaches the decision</li>
        +<li><span class="kind not-tested">not-tested</span> not tested: no P4 run reaches the decision at the value it has</li>
    no-p4 review: every decision not tested: True

    the matrix against the kit's records (canonical JSON):
    decisions 22 Counter({'unseparated': 9, 'separated': 8, 'inert': 5})
    with a record: 21 at its value: 14 at another: 7
    (pop.efficacy.rule has no record: inert, not drawn)

    $ SPECFIRST_STRICT=1 python -m pytest -q -s tests/score
    4 passed in 3.29s
    $ SPECFIRST_STRICT=1 python -m pytest -q -s tests/defects -k "D7 or D8 or D13"
    planted, an unseparated decision drawn as proven: 4 problems, for example: the decision ae.related.values (mod-ae-emergence) is unseparated and not drawn so
    (every plant of passes 1 and 2: seen)
    3 passed, 97 deselected in 38.62s
    $ python -m specfirst score pilot        (exit 0; the pilot report, Out14-3-1-1 by the kit's layout)
    $ ruff check src tests
    All checks passed!
    $ python -m pytest -q tests/unit/test_viewer.py tests/unit/test_kit.py tests/unit/test_gates.py \
        tests/unit/test_safety_records.py tests/unit/test_citations.py tests/unit/test_layout_terms.py \
        tests/unit/test_grid.py tests/unit/test_harness_pilot.py tests/unit/test_score_pilot_pins.py \
        tests/unit/test_separation.py
    1 failed, 204 passed in 50.54s
    FAILED tests/unit/test_harness_pilot.py::test_arm_r_on_a_real_study_with_the_stub_reader
      RunError: /tmp/pytest-of-root/.../tasks lies in /tmp, the folder that holds the checkouts;
      tasks and runs lie outside it, so that it is denied whole

The failure is the reviewer's setup, not the commit. The harness refuses a
task folder inside the folder that holds the checkout (ADR-010, decision
4). The reviewer's clone is /tmp/review31, so that folder is /tmp, where
pytest also puts its temporary folders. The author's clones lie one level
deeper (/tmp/specfirst-clean-*/specfirst, and a scratch clone outside
/tmp). The test
again with pytest's folders outside /tmp, under the lock:

    $ python -m pytest -q --basetemp=<a folder outside /tmp> tests/unit/test_harness_pilot.py
    11 passed in 2.81s
The clone after the runs: `git status --short` prints nothing.

This verdict is on the code and the records at `78fb49b`. The verdict on
the whole package waits for part 2: the report with its placeholders
filled and the logs of the seven clean-clone gates of `78fb49b`.

Pass 3 verdict (the code and the records at `78fb49b`): SIGNED.

## Final: the fixes of pass 3 (`bfdcadf`), the report and the logs (`121dbe2`)

Reviewed:
- `bfdcadf`, child of `78fb49b`: src/specfirst/viewer/ (command.py,
  model.py, page.py), tests/unit/test_viewer.py, ADR-022 and
  docs/state/real.md;
- `121dbe2`, child of `bfdcadf`: documents only (12 files: the report, ADR-022's
  "The owner's answer on P4", docs/state/real.md, this review as
  committed, and the eight gate logs; `git diff --name-only bfdcadf 121dbe2`
  lists no file under src/ or tests/).

The worktree was clean at `121dbe2`; this section is the reviewer's only
change.

### P3-F1 and P3-F2: closed

- **P3-F1.** `read_p4` reads the matrix's `vector`, and
  `model.p4_of` gives every class drawn the note "the P4 run of the vector
  house, every other decision at that vector's value". A record at another
  value gets "the P4 run of the vector house tried another value, <gold>:
  <class>". The legends of `tested` and `unseparated` say that every other
  decision stood at the value of the run's vector, which "may not be the
  kit's". ADR-022 decision 8 says the same, and records the owner's answer
  (A: show the class and state the condition).
- **P3-F2.** A `no_alternative` class is checked before the value
  comparison and drawn "not tested" with the note "... had no other value
  of it to try".
- **On the reviewer's build of `121dbe2`, with the coordinator's matrix
  (R13):**
  - 14 records are drawn with a class (separated 6, inert 4, unseparated
    4), and each carries the vector's note;
  - no class is drawn at another value;
  - the note counts on the page are those the report prints (264 notes on
    drawn classes, and 30, 62, 17, 17, 1, 62, 9 for the seven values
    tried);
  - a planted `no_alternative` at the record's own value
    (pop.safety.grouping) is drawn "not tested" with its note,
    `page_problems` is empty, and "P4: no_alternative" is nowhere on the
    page;
  - without `--p4`, the page differs from `78fb49b`'s in the two legend
    lines only, and every decision is "not tested" with no note.

  The unit test covers both cases, and D13 passes.

### The report docs/reports/issue-31.md

Its numbers are those of the reviewer's runs and of the logs:
- 1502 cells with a panel, 61 panels, 93 lines on the sheet;
- 84, 27 and 1178 printed numbers on the three outputs;
- 90 + 14 cells of Out14-1-1, and 866 + 1 + 408 of Out14-3-2-1;
- 38 citation edges to 4 spans, 9 of them to the whole document;
- 49 records: 18 stated, 12 default, 17 conflict, 2 asked, with 102
  quotes and 0 problems;
- 2505 citations;
- 45 of the 49 records in a panel, 7 of them through a column;
- the page of 3885705 bytes without `--p4` and 3926383 with it;
- the P4 counts and notes;
- 69 analyses reproduced.

The prose claims checked:
- PLAN.md, standard/ and env/ are unchanged: `git diff --stat 0046194
  121dbe2` lists none of them, and no file under gen/, score/, harness/ or
  compile/.
- What gen and score import from the changed modules is unchanged:
  `grid.ard_id`, `grid.SCHEMA` and `grid.grid_problems` have no changed
  line, and in graph.py the only changes are the import of `Callable` and
  the new `add_citations` after `add_displays`.
- Nothing in gen, score or harness reads `Kit.decisions`.
- The owner's lists name the 17 conflicts and the 2 asked records of the
  file.
- No statement claims std-2's check.

The review's passes are summarized correctly.

### The eight logs

Read from git at `121dbe2`:

| Log | Commit | Checks | Unit tests | Last lines |
| --- | --- | --- | --- | --- |
| issue-31.clean-clone.gate.log | `bfdcadf` | 14 PASS, 0 FAIL | 1400 passed, 37 deselected | GATE issue-31: PASS; clean clone gate issue-31: PASS |
| issue-31.merged.issue-31.gate.log | `78fb49b` | 14 PASS, 0 FAIL | 1400 passed, 37 deselected | GATE issue-31: PASS; clean clone gate issue-31: PASS |
| issue-31.read-1a.gate.log | `78fb49b` | 14 PASS, 0 FAIL | 1400 passed, 37 deselected | GATE read-1a: PASS; clean clone gate read-1a: PASS |
| issue-31.issue-29.gate.log | `78fb49b` | 12 PASS, 0 FAIL | 1400 passed, 37 deselected | GATE issue-29: PASS; clean clone gate issue-29: PASS |
| issue-31.real-2.gate.log | `78fb49b` | 15 PASS, 0 FAIL | 1400 passed, 37 deselected | GATE real-2: PASS; clean clone gate real-2: PASS |
| issue-31.real-3a.gate.log | `78fb49b` | 16 PASS, 0 FAIL | 1400 passed, 37 deselected | GATE real-3a: PASS; clean clone gate real-3a: PASS |
| issue-31.real-5a.gate.log | `78fb49b` | 18 PASS, 0 FAIL | 1400 passed, 37 deselected | GATE real-5a: PASS; clean clone gate real-5a: PASS |
| issue-31.real-5b.gate.log | `78fb49b` | 19 PASS, 0 FAIL | 1400 passed, 37 deselected | GATE real-5b: PASS; clean clone gate real-5b: PASS |

The planted defects passed 100 in each log that runs tests/defects. No log
has a byte outside ASCII, a user's home folder or a Windows user folder.
They name the clone folders under /tmp and the repository's mount path,
as the logs of issue-29 did.

**After `bfdcadf`, only issue-31 needed to run again.** The claim holds,
though one of its reasons is not exact (P4-F1 below):
- `bfdcadf` changes only the viewer, its unit test and two documents;
- `121dbe2` changes documents only;
- every gate runs the same full unit suite, which passed (1400) in the
  issue-31 gate on `bfdcadf`;
- the only other code of the seven gates that reaches the viewer is the
  command `pytest tests/defects -s -q` with `SPECFIRST_STRICT=1`. That
  command passed 100 of 100 in the same run, and the other gates check
  only that their named cases are among those passed.

#### P4-F1 (not blocking) Four more gates reach the viewer through their planted defects

The report says "Of the seven gates, only issue-31 has checks that reach
the viewer (its checks review and planted defects)". The planted-defect
checks of real-2, real-3a, real-5a and real-5b also run
`pytest tests/defects` whole (gates.py `_pytest`, with the folder and no
`-k`), D13-review included. Their logs of `78fb49b` show "--- D13-review"
and "100 passed". As said above, the conclusion holds.

What would fix it: say in the report that these four gates also run D13
through their planted defects, and that the issue-31 gate's run of the
same command on `bfdcadf` covers them. This needs no run again.

### What was run (final)

#### R13 The code of `121dbe2` (that of `bfdcadf`)

The clone /tmp/review31 checked out at `121dbe2`, its build folder
removed. Then, under one hold of `flock /run/lock/specfirst-heavy.lock
taskset -c 0-3`:

    $ python -m specfirst kit assemble cdiscpilot01; build; recompute      (exit 0 each)
    cdiscpilot01: 69 analyses: reproduced 69
    $ python -m specfirst view cdiscpilot01
    view cdiscpilot01: .../viewer/index.html (3885705 bytes), 61 analyses, 1502 cells with a panel, 93 lines on the sheet; 0 problems
    $ python -m specfirst view cdiscpilot01 --p4 matrix.json      (the coordinator's matrix, as in pass 3)
    view cdiscpilot01: .../viewer/index.html (3926383 bytes), 61 analyses, 1502 cells with a panel, 93 lines on the sheet; 0 problems

    inspection:
    vector of the runs: ['house']
    p4 page same as html(): True bytes 3926383
    p4 page_problems: []
    p4 acceptance problems: []
    records drawn with a class: 14 {'inert': 4, 'unseparated': 4, 'separated': 6}
    each names the vector: True
    a class at another value: []
    sheet P4: {'not tested': 79, 'inert': 4, 'unseparated': 4, 'separated': 6}
         30 the P4 run of the vector house tried another value, dm_actarm: separated
         62 the P4 run of the vector house tried another value, first_ex_with_dose: unseparated
         17 the P4 run of the vector house tried another value, first_of_month_not_before_first_dose: unseparated
         17 the P4 run of the vector house tried another value, last_dose_plus_days(days=30): unseparated
          1 the P4 run of the vector house tried another value, last_ex_end_date: unseparated
         62 the P4 run of the vector house tried another value, not_completed: unseparated
          9 the P4 run of the vector house tried another value, standard_rows: separated
        264 the P4 run of the vector house, every other decision at that vector&#x27;s value
    no_alternative planted: drawn not tested | note: the P4 run of the vector house had no other value of it
      to try | page_problems: [] | 'P4: no_alternative' on the page: False
    no-p4 page against 78fb49b's: 6828 and 6828 lines; 4 lines differ   (the legends of unseparated and tested)
    no-p4: every decision not tested, no note: True
    citations on the no-p4 page: 2505

    $ python -m pytest -q --basetemp=<outside /tmp> tests/unit/test_viewer.py tests/unit/test_kit.py \
        tests/unit/test_gates.py tests/unit/test_safety_records.py tests/unit/test_citations.py \
        tests/unit/test_harness_pilot.py
    90 passed in 8.64s
    $ SPECFIRST_STRICT=1 python -m pytest -q -s tests/defects -k D13
    1 passed, 99 deselected in 71.42s (0:01:11)
    $ ruff check src tests
    All checks passed!
    (the clone after the runs: git status --short prints nothing)

#### R14 The documents and the logs

`git show 121dbe2:<file>` for the report, ADR-022, docs/state/real.md, this
file and the eight logs:
- ASCII and paths: no byte outside ASCII in any of them, and no user's
  home folder or Windows user folder;
- per log: the commit line, the PASS and FAIL lines, the pytest summaries
  and the last lines (the table above);
- `git diff --stat 0046194 121dbe2` against PLAN.md, standard/, env/,
  gen/, score/, harness/ and compile/: nothing;
- `git diff 0046194 121dbe2` of grid.py and graph.py: no changed line in
  `ard_id`, `SCHEMA`, `grid_problems`, `build_graph` or `write_graph`.

### Verdict on the package

All findings that blocked are closed (pass 1, F1), and so is every other
finding of passes 1 to 3. The one finding of this part, P4-F1, is a
sentence of the report and does not block. The code and the records at
`bfdcadf` hold, and so do the documents and logs at `121dbe2`. The gates
ran on clean clones and passed. Left for the owner, as the report and the
state file say: the 17 conflicts and the 2 asked records of
safety.jsonl, and a P4 run on the kit's own values.

Verdict: SIGNED
