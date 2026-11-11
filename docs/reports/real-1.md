# real-1 Kit and ADaM proof: report

Date: 2026-11-11. Branch: `track/real`. Depends on base-0 (passed).

## Verdict

The gate passed. `specfirst gate real-1 --clean` exited 0 on a clean clone
of commit `6e6a2ce`, after a fresh install and a fresh fetch. The complete
output is in `docs/reports/real-1.gate.log` (270 lines); the section "The
gate" below quotes it.

This was the second gate run. The first one passed at commit `4b12c86`. The
independent reviewer then failed the work on one blocking finding, a
function adapted from Pilot 7 that was recorded nowhere, and made eleven
findings that do not block (section "Review, first pass"). All were acted
on, and the gate was run again on the commit that holds the fixes.

The independent review (rule R7) is in `docs/reports/real-1.review.md`. Its
verdict after the second pass is PASS (section "Review, second pass"). With
gate and review passed, `track/real` merges to `main` and both are pushed
(section 2.4); the git history and `docs/state/real.md` record the merge.

## What real-1 asks for, and where it stands

| Item of PLAN.md section 13.3 | State | Where |
| --- | --- | --- |
| Assemble `kits/cdiscpilot01/` from the cache: SAP, data guide, Define-XML files and SDTM as inputs; Pilot 7's yamaa specs and the reference ADaM as gold | done | `kits/cdiscpilot01/kit.yaml` (64 files by source, path and SHA-256), `specfirst kit assemble`; gate check 5 |
| Commit no study data (E20) | done | the kit folder holds `kit.yaml` and `README.md` only; gate check 5 and `tests/unit/test_kit.py` look for study data in git |
| ADR-001: wheel with our runner, or source build at Pilot 7's pin (E19) | done: the wheel, with our runner | `docs/decisions/ADR-001.md`; gate check 9 (A1, A2) |
| The name that differs in Pilot 7 (`adqsnipx.yaml`, `adqsnpix.parquet`) | handled | datasets are named by the specification's `domain` (ADQSNPIX), so the built file and the reference file are both `adqsnpix.parquet`; the spec file keeps its name |
| Canonical writers | done | `src/specfirst/machine/canonical.py`; `tests/unit/test_canonical.py` |
| P1 and P2 as tests | done | `specfirst check <kit> [--twice]`; gate checks 6 and 7; `tests/unit/test_build.py`, `test_compare.py` |
| The SDTM to ADaM part of the graph from the resolved specs: one node per ADaM output column and per SDTM column read, `derives_from` edges with source file and line | done | `src/specfirst/machine/graph.py`, `lineage.py`; gate check 8 |
| Pilot 7's claims as candidate `cites` edges for ADaM variables, marked as imported | done | 706 edges, `origin: imported`, `proof: judged`, `quote_verified: false`, `approved_by: null` |

## The gate

Gate text of PLAN.md section 13.3: P1 passes (two builds, identical hashes).
P2 passes (E1). Every output column of the 10 datasets reaches SDTM columns,
literals or declared inputs through `derives_from`; any gap is listed with
its reason.

Command, run in Ubuntu 24.04 under WSL2 as root, in the worktree of
`track/real`:

```text
$ SPECFIRST_ROOT=/mnt/d/trial_work/specfirst bash scripts/clean_clone_gate.sh real-1
```

The script clones the repository with `git clone --no-local` into a new
folder under `/tmp`, checks out the commit, and puts the Python
environment, the R library and the fetch cache of the clone under the same
new folder. It then runs `env/install.sh`, `specfirst fetch` and
`specfirst gate real-1 --clean`. `SPECFIRST_ROOT` was set to another
checkout on purpose (section "Review finding N2 of base-0").

The gate has eleven checks. The plan's gate text names P1, P2 and the
trace (checks 6 to 8). The others are additions: drift first (rule R3),
the pins, lint, the unit tests with their planted defects (rule R5), the
kit with the search for study data in git (E20), five tests on the fetch
cache and the pilot kit (ADR-001 and the review), a second verification of
the fetch cache after everything that reads it (lesson 13), and the ASCII
check (rule R10).

Output. Lines are quoted as printed from `docs/reports/real-1.gate.log`.
`[...]` marks where lines of the full log are left out: the three git
commands that make the clone and the commit line they print, two lines
about the R library, the lines of `specfirst doctor` and of the pin
listings, pytest's progress dots, 19 of the 23 hash lines of P1, and 9 of
the 10 per-dataset lines of the claims and of the tests A1 to A3.

```text
clean clone gate real-1
repository: /mnt/d/trial_work/specfirst/.git
commit:     6e6a2ce1bc54e7fe7b6351ec5b2e6f94720cc002
clone:      /tmp/specfirst-clean-mdfd8f/specfirst
environment and cache: /tmp/specfirst-clean-mdfd8f/env
[...]
$ bash env/install.sh
python environment: /tmp/specfirst-clean-mdfd8f/env/venv-specfirst-3393077720
[...]
R packages: 99 wanted, 99 to install from https://packagemanager.posit.co/cran/__linux__/noble/2026-11-10
[...]
doctor: ok

$ specfirst fetch
[...]
fetch: every pin verified

$ specfirst gate real-1 --clean
gate real-1 at commit 6e6a2ce1bc54e7fe7b6351ec5b2e6f94720cc002 (clean)

== [1/11] environment: specfirst doctor
[...]
doctor: ok
-- PASS environment (0.3 s)

== [2/11] pins: specfirst fetch --verify
[...]
fetch: every pin verified
-- PASS pins (0.7 s)

== [3/11] lint: ruff check .
All checks passed!
-- PASS lint (0.0 s)

== [4/11] unit tests: pytest -m "not evidence" -q
[...]
340 passed, 13 deselected in 10.15s
-- PASS unit tests (10.4 s)

== [5/11] kit: specfirst kit assemble cdiscpilot01
study data in git (E20): 116 maintained files checked, 0 problems
kit cdiscpilot01: 64 files match their pinned SHA-256 (26 inputs, 38 gold) in /tmp/specfirst-clean-mdfd8f/specfirst/build/kits/cdiscpilot01
-- PASS kit (0.1 s)

== [6/11] P1 determinism: specfirst check cdiscpilot01 --twice (its first part)
build into build/p1/cdiscpilot01/first: exit 0 (build cdiscpilot01: 10 datasets, 805 nodes, 3975 edges, 23 files in /tmp/specfirst-clean-mdfd8f/specfirst/build/p1/cdiscpilot01/first)
build into build/p1/cdiscpilot01/second: exit 0 (build cdiscpilot01: 10 datasets, 805 nodes, 3975 edges, 23 files in /tmp/specfirst-clean-mdfd8f/specfirst/build/p1/cdiscpilot01/second)
same      98966f855b1f9a06 98966f855b1f9a06 gold/data/adam/adae.parquet
[...]
same      356127185426e1e0 356127185426e1e0 gold/graph/coverage.json
same      63a13aa8ca5d2306 63a13aa8ca5d2306 gold/graph/edges.jsonl
same      45af1a74e0a35c89 45af1a74e0a35c89 gold/graph/nodes.jsonl
[...]
P1 determinism: 23 of 23 files have the same SHA-256 in both builds
-- PASS P1 determinism (30.9 s)

== [7/11] P2 reproduction: specfirst check cdiscpilot01 --build build/p1/cdiscpilot01/first (its first part)
ADSL      rows=   254 cols= 48 cells=   12192 mismatched=     0 storage_type_diffs=28
ADAE      rows=  1191 cols= 55 cells=   65505 mismatched=     0 storage_type_diffs=38
ADLBC     rows= 74264 cols= 46 cells= 3416144 mismatched=     0 storage_type_diffs=22
ADLBH     rows= 49932 cols= 46 cells= 2296872 mismatched=     0 storage_type_diffs=22
ADLBHY    rows=  9954 cols= 43 cells=  428022 mismatched=     0 storage_type_diffs=21
ADQSADAS  rows= 12463 cols= 40 cells=  498520 mismatched=     0 storage_type_diffs=20
ADQSCIBC  rows=   730 cols= 36 cells=   26280 mismatched=     0 storage_type_diffs=19
ADQSNPIX  rows= 31140 cols= 41 cells= 1276740 mismatched=     0 storage_type_diffs=21
ADTTE     rows=   254 cols= 26 cells=    6604 mismatched=     0 storage_type_diffs=14
ADVS      rows= 32139 cols= 34 cells= 1092726 mismatched=     0 storage_type_diffs=16
TOTAL cells=9119605 mismatched=0
numbers equal within the tolerance but not exactly: 1869 cells, largest difference 4.5e-13
storage type only, same values (reference -> built): large_string -> string in 221 columns
P2 reproduction: 10 of 10 datasets equal their reference (numeric tolerance 1e-10)
-- PASS P2 reproduction (0.5 s)

== [8/11] trace: specfirst check cdiscpilot01 --build build/p1/cdiscpilot01/first (its second part)
dataset   columns to SDTM by rows literal  gaps
ADSL           48      48       0       0     0
ADAE           55      55       0       0     0
ADLBC          46      46       1       0     0
ADLBH          46      46       1       0     0
ADLBHY         43      43       3       0     0
ADQSADAS       40      40       1       0     0
ADQSCIBC       36      36       5       0     0
ADQSNPIX       41      41       3       0     0
ADTTE          26      24       0       2     0
ADVS           34      34       0       0     0
TOTAL         415     413      14       2     0
to SDTM: reaches SDTM columns through derives_from. by rows: those of them whose own rule reads no column
and that reach SDTM only through the filter of a row template.
nodes: L0 279, L3 111, L4 415
edges: cites 706, derives_from 3269
cites edges: 706 imported, 0 with a verified quote, 0 approved by a person
literal columns sit on rows of: adam:ADSL (2)
claims ADAE       21 claims,  57 citations of kit documents ->  49 cites edges (one per column and span); 28 citations of programs or other files, not imported; 0 variables that are not output columns
[...]
trace: complete
-- PASS trace (0.9 s)

== [9/11] pilot tests: SPECFIRST_STRICT=1 pytest tests/pilot -m evidence -s -q

--- A1-resolve
ADSL      composed specification equals Pilot 7's snapshot: True
[...]
Pilot 7 pins yamaa at git revision c039509082b545fe913c00d1686426c3d245778c (cdiscpilot01/program/adam/python/requirements.txt)
snapshots were made with yamaa 0.7.0 built from git revision c039509082b545fe913c00d1686426c3d245778c
installed: yamaa 0.7.0 (wheel)
.
--- A2-runner
ADSL         254 rows x  48 columns: runner equals yamaa's project run: True
[...]
.
--- A3-lineage
ADSL       305 elements: dependencies equal Pilot 7's: True; unresolved ours [] theirs []
[...]
.
--- A4-unread
SDTM columns with a node in the graph: 111; without one: 202, all of them rolled by one row (131 hold more than one value)
ADaM datasets that changed: none
.
--- A5-adapted
recorded as adapted: src/specfirst/machine/lineage.py shares 73 lines with cached sources
recorded as adapted: src/specfirst/machine/runner.py shares 3 lines with cached sources
compared 45 Python files of ours with 673 of p7, yamaa, p6, ars; the most lines a file that is not recorded shares: 1 (allowed: 2)
.
5 passed in 54.56s
-- PASS pilot tests (54.8 s)

== [10/11] cache untouched: specfirst fetch --verify
[...]
fetch: every pin verified
-- PASS cache untouched (0.1 s)

== [11/11] ASCII: python -m specfirst.asciicheck
ASCII check: 116 files checked, 0 with non-ASCII bytes
-- PASS ASCII (0.0 s)

PASS  environment          0.3 s
PASS  pins                 0.7 s
PASS  lint                 0.0 s
PASS  unit tests          10.4 s
PASS  kit                  0.1 s
PASS  P1 determinism      30.9 s
PASS  P2 reproduction      0.5 s
PASS  trace                0.9 s
PASS  pilot tests         54.8 s
PASS  cache untouched      0.1 s
PASS  ASCII                0.0 s
GATE real-1: PASS

clean clone gate real-1: PASS (clone kept in /tmp/specfirst-clean-mdfd8f/specfirst until /tmp is cleared)
```

P1 beyond the gate. The `build.json` of the clean clone is byte for byte
the `build.json` of a build made from the same code in the worktree, on
the Windows drive and in another virtual environment (`cmp` exits 0). The
reviewer compared the `build.json` of six builds of this commit in three
checkouts: byte for byte the same (review, S5). In its first pass it had
built commit `4b12c86` three more times from other folders, with other
hash seeds, time zone and locale, and got the 23 hashes of that commit's
gate build (review, R3). The gate itself compares two folders of one
checkout in one environment (review, N2).

## The kit

`kits/cdiscpilot01/kit.yaml` pins yamaa 0.7.0 and Pilot 7 at commit
`213cb6ab3adc51abe4295cbbc546c0e6d46c3df8`, and lists 64 files of Pilot 7,
7,093,621 bytes in all:

| Part of the kit | Files | From Pilot 7 |
| --- | --- | --- |
| `inputs/docs/` | 3 | `SAP.pdf`, `dataguide.pdf`, `define-adam.xml` |
| `inputs/data/sdtm/` | 23 | the 22 SDTM datasets and `define-sdtm.xml` |
| `gold/spec/` | 18 | `project.yaml`, `codelists.yaml`, the 10 specifications, and the 6 parent specifications they inherit from |
| `gold/reference/adam/` | 10 | the reference ADaM datasets |
| `gold/claims/` | 10 | the reviewed claims, one file per dataset |

The SAP is byte for byte the file pinned for Pilot 6 in
`third_party/sources.yaml` (SHA-256 `210b7f1f...1bc7`). A test checks that the
kit's pin of Pilot 7 is the commit of `third_party/sources.yaml`.
`kits/cdiscpilot01/README.md` shows the layout of the assembled kit. A build
assembles the kit in the folder it builds in, so a build stands on its own.

The additions to the kit layout of PLAN.md section 8 are item 3 of ADR-001:
`gold/reference/`, `gold/claims/`, `gold/resolved/` and `gold/build.json`,
and the ADaM Define-XML under `inputs/docs/`. PLAN.md is not changed, and
section 8 is a design an ADR may improve; whether this ADR needs the
owner's approval is the owner's call (review, F12).

## The engine and the runner (ADR-001)

The choice E19 left open: the PyPI wheel of yamaa 0.7.0 with our own thin
runner, not a source build at Pilot 7's pinned revision. Tests in
`tests/pilot/` hold the evidence and run in the gate (check 9):

| Test | Result |
| --- | --- |
| A1-resolve | The wheel composes each of the 10 specifications to exactly the snapshot Pilot 7 committed, which was made with yamaa built from git revision `c039509082b545fe913c00d1686426c3d245778c`, the revision Pilot 7's requirements file pins: 10 of 10 equal. |
| A2-runner | Our runner (kit layout, every input in memory, nothing saved) builds the same tables as yamaa's own project run on Pilot 7's layout: 10 of 10 equal in values and types. |
| A3-lineage | `specfirst.machine.lineage` gives the same column dependencies as Pilot 7's own code, run from the cache: 10 of 10 equal, no unresolved name on either side. |
| A4-unread | With the 202 SDTM columns that have no node in the graph rolled by one row, the engine builds the same 10 datasets. A roll changes the 131 of them that hold more than one value. The reviewer ran a stronger form, which also empties the 70 constant columns and fills the one that is all missing, with the same result (review, S9). Together: the graph has a node for every SDTM column the build reads. |
| A5-adapted | No Python file of ours that `third_party/SOURCES.md` does not record shares more than 2 lines with a Python file of Pilot 7, yamaa, Pilot 6 or the ARS repository (the most is 1). |

## P2: what "equal" rests on

- E1 reported 0 mismatched cells and 14 to 38 "type differences" per
  dataset. They are all one thing: the reference files store text as Arrow
  `large_string` and yamaa returns `string`, in 221 columns. P2 compares
  values by logical kind, so these are not differences; the gate prints
  the count. A column of another kind (text against number, a time stamp
  with a time zone against one without) mismatches in every cell that is
  not missing on both sides.
- The tolerance of 1e-10 is absolute. 1,869 of the 9,119,605 cells are
  numbers that are equal within the tolerance but not bit for bit; the
  largest difference is 4.5e-13. Every other cell is equal exactly.
- The comparison keeps the cell count of the E1 spike and closes three
  holes the spike had (lesson 11): NaN against a number, a column the
  reference does not have, and another column order.

## The graph

`gold/graph/` of the build holds `nodes.jsonl` (805 nodes), `edges.jsonl`
(3,975 edges) and `coverage.json`. Every line fits
`standard/schemas/graph.schema.json`; the schema was not changed.

| Nodes | Count |
| --- | --- |
| ADaM output columns (L4) | 415 |
| SDTM columns read (L3) | 111 |
| Document spans cited by the imported claims (L0) | 279 |

| Edges | Count | Proof |
| --- | --- | --- |
| `derives_from` | 3,269 | static, built from the resolved specifications |
| `cites` | 706 | judged; imported from Pilot 7, no quote verified, none approved |

Of the 415 output columns, 413 reach SDTM columns and 2 are literals
(ADTTE.PARAM and ADTTE.PARAMCD, on the rows of the declared input ADSL).
There is no gap, so `trace_gaps` in the kit manifest is empty.

What the edges mean (ADR-001, item 6):

- An edge says what a column's rule reads, not which rows contributed.
  Keys, filters and ordering give edges like values do, and the v0 edge
  schema cannot tell them apart. Of the 413 columns, 14 have a rule that
  reads no column and reach SDTM only through the filter of their row
  template (the column "by rows" of the gate output; for example
  ADLBC.PARCAT1 and ADQSCIBC.PARAMCD). `coverage.json` records this per
  column.
- There is one edge per pair of columns, with the file and line of one
  place that reads the target: a rule before a lookup declaration or a row
  template, then the nearest. A join key is cited at the rule that causes
  the join. The reviewer counted 129 of the 3,269 edges where the cited
  line does not name the target column: 128 join keys and one edge through
  a lookup over `SELF` (review, S6 and N3).
- The hash of an ADaM node covers the column's rule and every helper,
  lookup and row template it passes through.

One column end to end, ADSL.BMIBL (baseline body mass index), with the
lines of `gold/spec/spec/yamaa/pilot-program/adsl_v1.yaml` the edges name:

```text
adam:ADSL.BMIBL      defined at line 677
  -> adam:ADSL.WEIGHTBL, adam:ADSL.HEIGHTBL   line 671: the helper BMIBL_RAW divides them
  -> sdtm:DM.ACTARM                           line 775: the row template keeps treated subjects
adam:ADSL.HEIGHTBL   defined at line 656
  -> sdtm:VS.VSSTRESN                         line 656: its rule rounds BASE_HT.VSSTRESN
  -> sdtm:VS.VSTESTCD, VS.VISITNUM, VS.STUDYID, VS.USUBJID
                                              line 109: filter, order and key of the lookup BASE_HT
  -> adam:ADSL.STUDYID, adam:ADSL.USUBJID     line 109: the keys of that lookup
adam:ADSL.WEIGHTBL   defined at line 664
  -> sdtm:VS.VSSTRESN                         line 664: its rule rounds BASE_WT.VSSTRESN
  -> the same VS columns and VS.VSBLFL        line 120: the lookup BASE_WT (baseline weight)
sdtm:VS.VSSTRESN     inputs/data/sdtm/define.xml line 4997 (its ItemDef)
```

`coverage.json` records that BMIBL reaches 9 SDTM columns. The helper
BMIBL_RAW and the lookups are not nodes; the edges pass through them.

What the trace check proves, and what else covers the rest. Check 8 proves
that the graph files fit the schema, agree with each other, have a node for
every output column of the built data, name only SDTM columns the kit has,
and record no gap that the kit does not list. It cannot see a reference
that the dependency analysis missed: such a column would be `literal` in
both files. For the pilot that is covered from two other sides: A3 (the
analysis equals Pilot 7's own for all ten specifications) and A4 with the
review's S9 (changing the SDTM columns without a node does not change the
build). The reviewer also rolled each of
the 111 columns that have a node, one build each: of the 72 that built,
every changed ADaM column had a `derives_from` path to the rolled column
(review, R7); the other 39 could not be tested that way (21 hold one
value, 18 make the engine refuse the data).

Claims. Pilot 7's 10 claims files hold 222 claims, all for output columns,
with 1,261 citations. The 913 citations of the SAP, the data guide and the
ADaM Define-XML became the 706 `cites` edges: one edge per column and
document span, carrying the line of the claim. The 348 citations of
programs (`adae.sas` and Pilot 6's R programs) were not imported, because
programs are not kit documents. The gate prints these counts per dataset.

## Planted defects (rule R5)

| Checker | Defects it must catch | Test |
| --- | --- | --- |
| Kit assembly | a source file with another hash; a missing source file; a stray file in the inputs; a changed file in the assembled kit; a kit pin that differs from `sources.yaml`; 16 kinds of bad manifest | `tests/unit/test_kit.py` |
| No study data in git | a data file in a tier C kit folder; a study document by suffix; a Define-XML; a pinned file under another name and suffix | `test_kit.py`, two tests |
| Canonical Parquet | metadata, storage type, chunking and dictionary encoding must not change the bytes; a changed value, a missing value and a renamed column must | `tests/unit/test_canonical.py` |
| P2 comparison | 10 kinds of changed cell; another number of rows; a missing, extra or reordered column; large integers; a time zone; the absolute tolerance | `tests/unit/test_compare.py` |
| P2 end to end | a reference with one other value; a dataset without a reference | `tests/unit/test_build.py` |
| P1 | absolute paths left in the built files, planted in the build processes: `determinism` fails; hand-made records with another hash, a missing file, another engine version | `test_build.py::test_p1_fails_when_a_built_file_depends_on_its_folder`, `test_compare_builds_sees_planted_differences` |
| Build | a changed fetch cache; another engine version than the kit pins; a specification the engine refuses; an input that is not in the kit; a build changed after it was built | `tests/unit/test_build.py` |
| Dependencies | a reference to a column no schema has; an unknown bare name; keywords, literals and function names must not count as names | `tests/unit/test_lineage.py` |
| Trace check | a gap with no listed reason; a gap behind another column; a listed gap that is none; an output column without a node; an SDTM node that is not a column of the kit; a line that breaks the schema; an edge to a missing node; an unsorted file; graph files that disagree | `tests/unit/test_graph.py` |
| Missed reference | every SDTM column without a node changed, on the real kit | `tests/pilot` A4-unread |

The end-to-end unit tests run on a made-up study of three subjects
(`tests/toy_kit.py`): two specifications written for the tests and an
expected ADaM written by hand. No study data is in the tests.

## Review, first pass

The reviewer read the diff of `4b12c86` against PLAN.md, ran the gate, and
made experiments of its own. Verdict of that pass: FAIL, on F1. The gate
statement held in every check the reviewer made. What was done:

| # | Finding | Action |
| --- | --- | --- |
| F1, blocking | `runner._relocate` follows `relocate` of Pilot 7's `resolved_specs.py` statement by statement and was recorded nowhere (rule 1 of section 2.1) | Recorded in `third_party/SOURCES.md`, named in the code, covered by the notice file. New test A5-adapted looks for adapted code that nobody recorded. Lessons 12 and 14. |
| F2 | A column that reads a column with a gap was recorded as complete | A gap is passed on, in the builder and again in the check; test with the reviewer's case. Could not show on the pilot, which has no gap. |
| F3 | P1 could not see bytes that depend on the folder: both builds read one assembled kit | Each build assembles the kit in its own folder; a test plants absolute paths in the build processes and sees `determinism` fail. Lesson 15. |
| F4 | The trace check cannot see a reference the analysis missed; the two wrong-literal tests changed one file only | New test A4-unread on the real kit. The check's docstring, ADR-001 and this report say what the check proves. Lesson 16. |
| F5 | The search for study data in git went by suffix only; `kits/README.md` claimed more | Also by content: ODM files, and files byte for byte equal to a pinned file. README says what is and is not seen. |
| F6 | "not verified, not approved" was fixed text; SDTM nodes were not checked against the data | The line counts what the edges say; SDTM nodes are checked against the kit's SDTM files. |
| F7 | 913 citations become 706 edges, and the log did not show it | The log shows both counts per dataset; ADR-001 says what an edge stands for. A note for real-3. |
| F8 | ADR-001 did not say that edges mix value and context, that 238 edges cite a line that does not name the target, and that a changed helper changed no hash | `coverage.json` records `value`; a rule is preferred to a lookup declaration as the place of an edge, which brought the reviewer's count from 238 to 129 (the 128 join keys remain, and ADR-001 says so; the one other is N3 of the second pass); the node hash covers what the rule passes through. |
| F9 | The tolerance is absolute; a time zone would have counted as storage | Stated; a time zone is now another kind; P2 prints how many cells rest on the tolerance. |
| F10 | A1 asserted the version of the snapshots, not the revision | It asserts the revision Pilot 7 pins. |
| F11 | Which planted defects were real cases and which simpler cousins | The three cousins are F3, F4 and F5, fixed there. |
| F12, for the owner | ADR-001 adds to the kit layout of section 8 without the owner's approval | Not for the executor to settle. Stated in ADR-001 and in section "The kit" above. |

The reviewer's suggestion to name polars in `build.json` was not followed:
the build does not use polars (yamaa is used through its own tables and
pyarrow). The reviewer withdrew it in the second pass.

## Review, second pass

The reviewer read the diff of `6e6a2ce` against `4b12c86`, this report, the
state file and the gate log, ran the gate in the worktree (11 of 11) and
planted its cases of the first pass again. Verdict: PASS. It covers commit
`6e6a2ce`, the clean-clone gate log, and this report and the state file as
the reviewer read them. What it found:

- The actions on F1 to F12 are real and sufficient. A5 fails when the row
  of the runner is taken out of `third_party/SOURCES.md`. The gate log is
  the log of the clean clone, and the lines this report quotes are in it,
  in order. The old and the new graph code give the same 3,975 pairs of
  nodes on the pilot; places and hashes differ, as intended.
- Four sentences of this report needed a correction (C1 to C4 of the
  review: the lines left out of the quoted log, what A4 shows by itself,
  what the reviewer's extra builds varied, and "every cell"). They are
  corrected above. The reviewer has not read the corrected sentences, this
  section or the last paragraph of the verdict; they were written after
  its second pass.
- Seven new findings, none blocking. They are not fixed here, so that the
  code of the merge is the code that passed the gate. They are listed in
  `docs/state/real.md` for the first commit of real-2:

| # | Finding | Effect on the pilot |
| --- | --- | --- |
| N1 | A4 rolls 202 columns, but a roll changes only the 131 that hold more than one value; ADR-001 item 6, lesson 16 and the docstring of A4 say "every". Let A4 also empty constant columns, or reword. | The claim is true: the review's stronger run (S9) changed all 202 and no dataset changed. |
| N2 | P1 sees the folder of a build, not the checkout root or the environment, which both builds share. | No such dependence: `build.json` is the same in three checkouts. That comparison is made by hand. |
| N3 | The place of an edge falls outside the stated rule in two cases: a lookup over `SELF` to an output column is cited at the lookup; of two rules at the same distance the first walked wins, not the lowest line. | One edge, ADQSNPIX.AWTDIFF to ADQSNPIX.ADY. The place is the same in every build. |
| N4 | `value` is true for a literal column when the specification has a top-level `filter`. | None: no pilot specification has one, so the 14 and the 2 are right. |
| N5 | An ODM file in git is seen only with the suffix `.xml`, in ASCII or UTF-8, with `<ODM` in its first 64 KiB; `kits/README.md` says more. | None is committed. |
| N6 | Two different time zones at the same instant would be printed as "storage type only". | None: the pilot has no time stamp column. |
| N7 | ADR-001 item 5 says the plan "words" the tolerance as absolute (the plan says only "numeric tolerance 1e-10"), and "every cell" where it is every cell not missing on both sides. | Wording. |

After the second pass this branch gained one commit, with four files only:
this report, the gate log, the state file and the review. Code, tests,
scripts, schemas, ADR-001 and the lessons are those of `6e6a2ce`.

## GitHub and CI

`track/real` is pushed to the owner's private repository. CI succeeded on
both gated commits: run 43070667115 on `4b12c86` (`331 passed, 11
deselected`) and run 43077253906 on `6e6a2ce` (`340 passed, 13
deselected`), each with the environment from the lock file, the ASCII check
(116 files) and lint. The unit tests on GitHub's runner include the
end-to-end tests on the made-up study, with yamaa from the lock file. CI
has no fetch cache, so it does not run the gate checks 5 to 10.

## Review finding N2 of base-0

`scripts/clean_clone_gate.sh` obeyed a caller's `SPECFIRST_ROOT` when it
looked up the repository and the commit. It now sets the variable to its
own checkout for that lookup. The gate above is the evidence: it was
started in the worktree of `track/real` with `SPECFIRST_ROOT` pointing at
the main checkout, which stood at commit `54f8934` on `track/base`. The log
shows that the script cloned commit `6e6a2ce`, the HEAD of the worktree it
was started in.

## Open

- For the owner: item 3 of ADR-001 adds to the kit layout of PLAN.md
  section 8 (review, F12).
- The seven findings N1 to N7 of the review's second pass (section
  "Review, second pass"): for the first commit of real-2.
- The quotes of the imported claims are not checked against the documents,
  and no one has approved them: the 706 `cites` edges are candidates. real-3
  completes the graph to the documents; one flag per edge will not be
  enough there, because an edge can stand for several quotes.
- The v0 edge schema cannot tell a value dependency from a key, filter or
  ordering dependency. `coverage.json` has the count per column. If
  real-3's viewer needs it per edge, that is a schema change and needs an
  ADR.
- P1 was tested with yamaa's Python host only. Section 4.6 also names
  yamaa's R host; it is not in the environment section 13.2 lists.
- A1 and P2 show that the wheel and Pilot 7's pinned revision agree on the
  ten pilot specifications. They do not cover constructs these
  specifications do not use.
- The search for study data in git cannot see a document that was retyped
  or converted to another format. `evidence/csr_hylaw_spike.py`, the
  owner's file with typed-in CSR values, is such a case and is still open
  from base-0.
- A5 finds code taken over nearly as it was, not code rewritten line by
  line.
- The kit manifest is checked by code, not by a schema in
  `standard/schemas/` (ADR-001, item 3).
- The pilot's protocol is not in the kit; nothing has needed it yet.
- Building in a worktree on the Windows drive takes about 45 seconds per
  build (13 seconds on the Linux file system).

## Files

| Path | Content |
| --- | --- |
| `kits/cdiscpilot01/` | `kit.yaml` (manifest), `README.md` |
| `src/specfirst/kit.py` | manifest, assemble, lock, study data in git |
| `src/specfirst/machine/` | `runner.py`, `canonical.py`, `compare.py`, `lineage.py`, `graph.py`, `build.py` |
| `src/specfirst/cli.py`, `gates.py` | `kit`, `build`, `check`; gate `real-1` |
| `tests/unit/` | `test_kit.py`, `test_canonical.py`, `test_compare.py`, `test_lineage.py`, `test_graph.py`, `test_build.py`; `tests/toy_kit.py` |
| `tests/pilot/test_pilot.py` | A1 to A5 |
| `docs/decisions/ADR-001.md` | the decisions |
| `third_party/SOURCES.md`, `third_party/licenses/PILOT7-MIT.txt` | the adapted code and its license |
| `docs/reports/real-1.gate.log` | the complete output of the gate on the clean clone |
| `docs/reports/real-1.review.md` | the independent review |
