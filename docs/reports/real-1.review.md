# real-1 Kit and ADaM proof: independent review

Reviewed: work package real-1 of PLAN.md section 13.3, on branch
`track/real`, in two passes.

- First pass: the diff `main..track/real` at commit `4b12c86` against
  PLAN.md, and the reviewer's own gate run. Verdict of that pass: FAIL, on
  one blocking finding (F1).
- Second pass: the fixes in `4b12c86..6e6a2ce`, the report
  `docs/reports/real-1.md`, the gate log `docs/reports/real-1.gate.log` of
  a clean clone of `6e6a2ce`, and `docs/state/real.md`. Verdict: PASS.

Date: 2026-11-11.

Reviewer: an independent agent with a fresh context that did not write the
work (rule R7). Correctness only, no style remarks. The reviewer changed no
tracked file, made no commit, and wrote this file only.

The text of the first pass is kept as it was written. Two things are
changed in it: its headings are one level lower, and its verdict line now
reads "Verdict of the first pass". Where the second pass found the first
pass wrong, the correction is in the second pass ("Corrections to the
first pass"), not in the old text. The verdict that counts is the last
line of this file.

## First pass

Reviewed: work package real-1 of PLAN.md section 13.3, on branch
`track/real`.

- First pass (this text): the diff `main..track/real`, one commit,
  `4b12c860c2ef47389916222d94d9669b8ad58193` (`4b12c86`): 31 files, 4190
  insertions, 17 deletions, against PLAN.md.
- Second pass: not made yet. The author's report `docs/reports/real-1.md`,
  the gate log `docs/reports/real-1.gate.log`, the changed
  `docs/state/real.md` and the clean-clone gate log were being written
  while this pass ran. They are not committed and were not reviewed.

Date: 2026-11-11.

Reviewer: an independent agent with a fresh context that did not write the
work (rule R7). Correctness only, no style remarks. The reviewer changed no
tracked file, made no commit, and wrote this file only.

### Verdict

Verdict of the first pass: FAIL

This is the verdict of the first pass. It covers the code of commit
`4b12c86` and the gate run the reviewer made in the worktree. It does not
cover the author's report, the state file or the clean-clone gate.

One finding blocks: F1, code adapted from Pilot 7 that is not recorded
(rule 1 of PLAN.md section 2.1, which has no exceptions). The fix is a few
lines.

The gate statement itself held in every check the reviewer made:

- `specfirst gate real-1` exited 0 in the worktree: 11 of 11 checks.
- P1: 23 of 23 files have the same SHA-256 in both builds, and in three
  more builds the reviewer made from other folders and under other process
  settings.
- P2: 9,119,605 cells, 0 mismatches; the only type difference is Arrow
  `large_string` against `string`, in 221 columns.
- Trace: 415 output columns, 413 to SDTM, 2 literal, 0 gaps. A dynamic
  check by the reviewer (perturb SDTM columns, rebuild, compare) found no
  dependency that the graph lacks.

Eleven findings do not block (F2 to F12). F2 is a defect of the trace
check that cannot show on the pilot as long as the kit lists no gap; it
should be fixed before a kit lists its first one.

### Scope and method

#### What was read

- `CLAUDE.md`; PLAN.md "How to use this file" and sections 2, 3 (rows E1,
  E6, E18 to E21), 4.1, 4.2, 4.6, 4.8, 7.1, 7.5, 8 and 13.3 (real-1);
  `docs/decisions/ADR-001.md`; `docs/lessons.md`;
  `kits/cdiscpilot01/README.md` and `kit.yaml`; `kits/README.md`;
  `standard/schemas/graph.schema.json`; `third_party/SOURCES.md` and
  `third_party/licenses/PILOT7-MIT.txt`.
- Every file of the diff, in full: `src/specfirst/kit.py`,
  `src/specfirst/machine/{runner,canonical,compare,lineage,graph,build}.py`,
  `src/specfirst/gates.py`, `src/specfirst/cli.py`,
  `scripts/clean_clone_gate.sh`, `tests/toy_kit.py`,
  `tests/pilot/test_pilot.py`,
  `tests/unit/test_{kit,canonical,compare,lineage,graph,build}.py`, and the
  changed parts of `Makefile`, `pyproject.toml`, `tests/unit/test_gates.py`
  and `tests/unit/test_sources.py`.
- In the fetch cache, read only: Pilot 7's
  `.github/scripts/study_dashboard/references.py` and `lineage.py`,
  `.github/scripts/resolved_specs.py`, `LICENSE` and `LICENSING.md`; and
  yamaa's `docs/articles/derive.md` and expression schemas, to know what a
  specification can say.
- Not read: `docs/reports/real-1.md`, `docs/reports/real-1.gate.log`, the
  uncommitted change of `docs/state/real.md`.

#### What was run

All Linux commands ran in Ubuntu 24.04 under WSL2 as root, after
`. scripts/env.sh`, from script files in a scratch folder outside the
repository (`<scratch>`). Python 3.12.3, yamaa 0.7.0, pyarrow 25.0.1,
polars 1.44.2. Scripts that import from the worktree or read the cache ran
with `PYTHONDONTWRITEBYTECODE=1`. Experiments that build ran in folders
under `/tmp` and `/var/tmp`, removed afterwards.

Side effects in the worktree, all in the ignored folder `build/`: the
reviewer's gate run replaced `build/gates/real-1/gate.log`,
`build/gates/real-1/pilot.xml` and `build/p1/`, and assembled the kit in
`build/kits/cdiscpilot01` again (a file is copied only when its hash
differs). The log it replaced was of an earlier run that had failed at
`pins` with 10 checks.

| # | Command | Key output |
| --- | --- | --- |
| R1 | `python -m pytest -m "not evidence" -q` | `331 passed, 11 deselected in 17.98s` |
| R2 | `specfirst gate real-1` | `GATE real-1: PASS`, exit 0 (below) |
| R3 | `specfirst build cdiscpilot01` from three other places | all 23 hashes equal those of the gate's build (below) |
| R4 | `build.determinism` on the toy kit with two planted defects | one caught, one not (below, F3) |
| R5 | `compare_tables` on 23 made-up pairs; type pairs of the pilot | below, F9 |
| R6 | static analysis of the built graph | below, F7, F8 |
| R7 | perturb SDTM columns, rebuild, compare with the graph | no missing dependency (below) |
| R8 | five planted defects against the trace check and the data-in-git check | below, F2, F4, F5, F6 |
| R9 | scan of the new files for lines of third-party code | below, F1 |
| R10 | `specfirst fetch --verify`, before and after everything | `fetch: every pin verified`, exit 0, both times |

##### R2 The gate

`specfirst gate real-1` in the worktree at `4b12c86`. The tree had
untracked files of the author (`docs/reports/real-1.md`), so the first
line says so. Excerpts:

```text
gate real-1 at commit 4b12c860c2ef47389916222d94d9669b8ad58193 (with uncommitted changes)
== [5/11] kit: specfirst kit assemble cdiscpilot01
study data in git (E20): 118 maintained files checked, 0 problems
kit cdiscpilot01: 64 files match their pinned SHA-256 (26 inputs, 38 gold) in /mnt/d/trial_work/specfirst-real/build/kits/cdiscpilot01
== [6/11] P1 determinism: specfirst check cdiscpilot01 --twice (its first part)
build into build/p1/cdiscpilot01/first: exit 0 (build cdiscpilot01: 10 datasets, 805 nodes, 3975 edges, 23 files in ...)
build into build/p1/cdiscpilot01/second: exit 0 (build cdiscpilot01: 10 datasets, 805 nodes, 3975 edges, 23 files in ...)
P1 determinism: 23 of 23 files have the same SHA-256 in both builds
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
storage type only, same values (reference -> built): large_string -> string in 221 columns
P2 reproduction: 10 of 10 datasets equal their reference (numeric tolerance 1e-10)
== [8/11] trace: specfirst check cdiscpilot01 --build build/p1/cdiscpilot01/first (its second part)
dataset   columns to SDTM literal  gaps
ADSL           48      48       0     0
ADAE           55      55       0     0
ADLBC          46      46       0     0
ADLBH          46      46       0     0
ADLBHY         43      43       0     0
ADQSADAS       40      40       0     0
ADQSCIBC       36      36       0     0
ADQSNPIX       41      41       0     0
ADTTE          26      24       2     0
ADVS           34      34       0     0
TOTAL         415     413       2     0
nodes: L0 279, L3 111, L4 415
edges: cites 706, derives_from 3269 (706 imported, judged, not verified, not approved)
literal columns sit on rows of: adam:ADSL (2)
trace: complete
== [9/11] pilot tests: SPECFIRST_STRICT=1 pytest tests/pilot -m evidence -s -q
(A1-resolve: 10 of 10 "composed specification equals Pilot 7's snapshot: True";
 A2-runner: 10 of 10 "runner equals yamaa's project run: True";
 A3-lineage: 10 of 10 "dependencies equal Pilot 7's: True; unresolved ours [] theirs []")
3 passed in 36.39s

PASS  environment          0.4 s
PASS  pins                 0.1 s
PASS  lint                 0.2 s
PASS  unit tests          18.2 s
PASS  kit                  3.3 s
PASS  P1 determinism      93.4 s
PASS  P2 reproduction      4.4 s
PASS  trace                4.3 s
PASS  pilot tests         36.9 s
PASS  cache untouched      0.1 s
PASS  ASCII                1.4 s
GATE real-1: PASS
```

##### R3 P1 beyond the gate

The gate's two builds read the same assembled kit in the same environment.
The reviewer built three more times, each from a minimal checkout (PLAN.md,
`third_party/sources.yaml`, `kits/cdiscpilot01/kit.yaml`,
`standard/schemas/`) in another folder, with the shared cache:

```text
A: cd /tmp/sfreview-real1/a && SPECFIRST_ROOT=/tmp/sfreview-real1/a specfirst build cdiscpilot01
B: cd / && SPECFIRST_ROOT=/tmp/sfreview-real1/a-much-longer-folder-name/with/depth/b \
     POLARS_MAX_THREADS=1 TZ=Asia/Tokyo PYTHONHASHSEED=12345 LC_ALL=C specfirst build cdiscpilot01
C: SPECFIRST_ROOT=/tmp/sfreview-real1/a POLARS_MAX_THREADS=32 PYTHONHASHSEED=0 \
     TZ=America/Los_Angeles specfirst build cdiscpilot01 --into /tmp/sfreview-real1/c-out

A files 23 different from the gate's first build: [] meta diff: []
B files 23 different from the gate's first build: [] meta diff: []
C files 23 different from the gate's first build: [] meta diff: []
```

None of the 24 files of the gate's first build (the 23 and `build.json`)
contains `/mnt/`, `/root/`, `/tmp/` or the name of the worktree. So the
bytes do not depend on the folder, the number of threads, the hash seed,
the time zone or the locale.

##### R7 The graph against the engine: perturbation

A static graph can miss a dependency without any file showing it (F4). To
test the pilot graph against the engine, the reviewer changed SDTM columns
in a copy of the assembled kit, rebuilt with `runner.run_project`, and
compared the ADaM tables with the unchanged build. A change is a roll: the
same values, moved down one row, so types and value sets stay the same.

```text
(1) all 202 SDTM columns that have no node in the graph, rolled at once
  AE  columns 35 read per graph 30 perturbed  5      DM  columns 25 read per graph 15 perturbed 10
  DS  columns 13 read per graph  8 perturbed  5      EX  columns 17 read per graph  8 perturbed  9
  LB  columns 23 read per graph 13 perturbed 10      MH  columns 19 read per graph  5 perturbed 14
  QS  columns 20 read per graph 11 perturbed  9      SC  columns 14 read per graph  5 perturbed  9
  SV  columns  8 read per graph  4 perturbed  4      VS  columns 24 read per graph 12 perturbed 12
  (and every column of the 12 datasets no specification reads)
perturbed 202 SDTM columns that have no node in the graph; datasets with any change: none

(2) each of the 111 SDTM columns that have a node, rolled alone, one build each
status: {'constant': 21, 'ok': 72, 'error': 18}
perturbed and rebuilt: 72; with any change in the ADaM data: 69; changed ADaM columns in all: 417;
columns the graph says depend on the perturbed ones, in all: 1524; dataset row sets changed: 15
```

In (2), `constant` is a column with one value (rolling changes nothing) and
`error` is a build the engine refused on the rolled data (duplicate keys,
unmapped values and the like). For the 72 that built: every one of the 417
changed ADaM columns has a `derives_from` path to the rolled SDTM column.
Where the rows of a dataset changed (15 cases), every column of that
dataset has such a path in 14; the 15th is `QS.VISIT`, which is a key
column of ADQSNPIX, and there a comparison by position shows that only
`ADQSNPIX.VISIT` changed, which the graph connects.

Result: (1) the graph has a node for every SDTM column the build reads;
(2) no changed column lacks its edge. The graph says more than changes
(1524 against 417), as a static index must.

##### R9 Clean room

```text
tracked files: 116; by suffix: 52 py, 28 md, 10 json, 6 sh, 5 txt, 3 lock, 2 yaml, 2 R, ...
tracked .json: .claude/settings.json and the schemas and examples of standard/schemas/
tracked .yaml: kits/cdiscpilot01/kit.yaml, third_party/sources.yaml
largest tracked file: PLAN.md (96769 bytes)
```

No study data and no study document is committed. The kit folder holds
`kit.yaml` and `README.md` only. `PLAN.md` and `standard/schemas/` are not
in the diff. `third_party/licenses/PILOT7-MIT.txt` from line 11 on is
byte for byte Pilot 7's `LICENSE` (`diff` exits 0). `specfirst fetch
--verify` passed before and after the reviewer's work, and the cache holds
no `__pycache__` and no `-yamaa.parquet` of the pilot.

### Findings

#### F1 (blocking) `runner._relocate` is adapted from Pilot 7 and not recorded

Rule 1 of PLAN.md section 2.1: "Record every imported file in
`third_party/SOURCES.md` with URL, commit and license." Section 2.1 has no
exceptions, and lesson 12 of this work package says what adapted MIT code
needs.

`third_party/SOURCES.md` names one file with adapted code,
`src/specfirst/machine/lineage.py`. A second place is not named:
`_relocate` in `src/specfirst/machine/runner.py` (lines 64 to 95) follows
`relocate` in Pilot 7's `.github/scripts/resolved_specs.py` (lines 34 to
60) statement by statement.

```text
Pilot 7 resolved_specs.py lines 46-60: 15 statements; runner.py lines 81-95: 15 statements
identical after renaming location->place, p->layer and [..]->.get(..): 15 of 15 in the same order: True
```

A scan of all 15 new source and test files against every Python file of
the cached sources p7, yamaa, p6 and ars (lines of more than 30 characters,
white space ignored, comments and imports left out) found shared lines,
other than two common idioms (`path.parent.mkdir(...)` and
`if not isinstance(entry, dict):`), in two files only: `lineage.py` (69
lines of `references.py`, 11 of `lineage.py`, recorded) and `runner.py`
(`resolved_specs.py`: 4 lines in `_relocate`, and one loop header that
`_plans` has twice).

`runner.py` does not name Pilot 7 as the source of the function, and the
first sentence of `third_party/licenses/PILOT7-MIT.txt` covers
`lineage.py` only. `tests/unit/test_sources.py` asserts that the table has
exactly the one row, so it passes: it checks the rows that are there and
cannot see one that is missing.

Fix: add a row for `src/specfirst/machine/runner.py` (`_relocate`, from
`.github/scripts/resolved_specs.py`, the same commit and license) to the
table in `third_party/SOURCES.md`; name source, commit and license file in
`runner.py`; widen the first sentence of the notice file; let the test
expect both rows. Lesson 12 should say that its check cannot find an
adaptation nobody recorded.

#### F2 (not blocking) A column that reads a column with a gap is recorded as complete

`graph._trace_column` stops at another output column, and
`build_graph` decides `terminal` from the column's own gaps and from what
it reaches. A gap of the column it reads is not passed on. Planted with the
plans of `tests/unit/test_graph.py`: AGEGR1 reads an unknown name, AGEGR1N
reads only AGEGR1.

```text
AGEGR1 : {'column': 'adam:ADSL.AGEGR1', 'terminal': 'gap', 'sdtm': 0, 'inputs': ['sdtm:DM'], 'gaps': ['unknown name AGE_TYPO at gold/spec/adsl.yaml:30']}
AGEGR1N: {'column': 'adam:ADSL.AGEGR1N', 'terminal': 'literal', 'sdtm': 0, 'inputs': ['sdtm:DM'], 'gaps': []}
check, gap not listed  : ['adam:ADSL.AGEGR1: gap with no listed reason: unknown name AGE_TYPO at gold/spec/adsl.yaml:30']
check, AGEGR1 listed   : [] | ['  gap adam:ADSL.AGEGR1: ... (listed: known)', 'ADSL            5       2       2     1', 'TOTAL           5       2       2     1']
```

With the gap of AGEGR1 listed in the kit, the check passes and counts
AGEGR1N as `literal`, which it is not: its trace ends in a gap. The same
holds across datasets (ADAE reads ADSL), and a column that reaches SDTM
through other edges would be counted `to SDTM`.

It does not block, because the gate of real-1 can only pass this way when
a gap is listed, and the pilot kit lists none (`trace_gaps: {}`): with no
gap anywhere there is nothing to pass on. It is a defect of the check all
the same (rule R5), and ADR-001 item 6 ("A column that reads no column is
`literal`") does not describe what the code does.

Fix: a column is complete only if every column it reaches through
`derives_from` is complete. Compute that in `build_graph` and again in
`check_graph`; add the case above as a test.

#### F3 (not blocking) P1 as tested cannot see bytes that depend on the checkout folder

`build.determinism` builds twice into two folders, but both builds read
the same assembled kit (`build/kits/<kit>`) in the same environment. A
path of that kit left in a built file is the same in both builds. Planted
on the toy kit of `tests/toy_kit.py`, through a `sitecustomize` that is
active in the build processes only:

```text
control: P1 passed=True; P1 determinism: 7 of 7 files have the same SHA-256 in both builds; occurrences of the checkout path in the built JSON files: 0
absolute paths left in the resolution: P1 passed=True; P1 determinism: 7 of 7 files have the same SHA-256 in both builds; occurrences of the checkout path in the built JSON files: 213

hash of every graph element depends on the building process: P1 passed = False
DIFFERENT 3e394e1c6f5946dd 5d256f6bba2f9e03 gold/graph/nodes.jsonl
P1: gold/graph/nodes.jsonl: the two builds differ
```

So the check fails on a difference between processes and passes on a
dependence on the folder. The delivered code has no such dependence: R3
above, and `tests/unit/test_build.py` asserts it for the record of the toy
kit. The unit tests show `compare_builds` failing on planted records, but
`determinism` itself, which the gate calls, is never shown failing.

Fix: let the second build assemble and resolve in a folder of its own (or
build from a second root), and add one test in which `determinism` returns
False. `build.json` could also name polars beside yamaa and pyarrow.

#### F4 (not blocking) The trace check cannot see a reference the lineage misses

`check_graph` computes reachability from `edges.jsonl`, but it takes
`literal` and `gaps` from `coverage.json`, and both files come from the
same lineage. A reference the lineage does not find leaves two files that
agree. Planted: the edges of HT (`VS.VSSTRESN`) removed and its coverage
entry set to `literal`.

```text
HT = VS.VSSTRESN recorded as literal with no edge; check problems: [] | ['ADSL            5       3       2     0', 'TOTAL           5       3       2     0']
```

The two tests that plant a wrong literal change one file only
(`test_a_removed_edge_fails`, `test_a_column_wrongly_recorded_as_literal_fails`),
so they test that the files agree. In the sense of lesson 9 they are the
simpler cousin of a missed reference.

In the pilot the count `to SDTM` also says less than it seems to: all ten
specifications have row templates, and every column depends on the filter
of its template, so 14 columns whose own rule reads no column are counted
`to SDTM` (F8). A missed value reference would not lower that count.

What does carry the claim for the pilot: unknown and unresolved names
become gaps (tested with real cases); A3 shows the dependencies equal
Pilot 7's for all ten specifications; and R7 found no dependency the graph
lacks. The 16 columns with no value reference have at most as many
distinct values as their dataset has row templates.

Fix (suggestion): add part (1) of R7 to `tests/pilot` (one build, 13
seconds): rolling every SDTM column without a node must change nothing.
Say in the report that the trace check proves agreement of the graph files
and the absence of recorded gaps, not the absence of missed references.

#### F5 (not blocking) The data-in-git check knows fewer formats than `kits/README.md` says

`kits/README.md`: "A test and the gate of real-1 fail when study data or a
study document appears in git." `kit.tracked_data_problems` goes by a list
of suffixes. Outside a kit folder it does not see a Define-XML, a claims
file or the text of a CSR:

```text
names: docs/define-adam.xml, third_party/pilot/define.xml, tests/data/adsl-claims.json, docs/csr.txt,
       evidence/adsl.xpt, tests/fixtures/dm.json, docs/SAP.PDF, data/adsl.rds, data/adsl.sas7bdat,
       data/dm.feather, data/adsl.tsv
problems: ['evidence/adsl.xpt: ...', 'docs/SAP.PDF: ...', 'data/adsl.sas7bdat: ...']
```

Nothing of the kind is committed (R9). Fix: narrow the sentence, or widen
the check (`.xml` with an ODM root, `.rds`, `.feather`, `.tsv`, and a
SHA-256 comparison of tracked files with the files of the kit manifests).

#### F6 (not blocking) Two things the trace check prints or accepts without checking

- The line `edges: cites 706, derives_from 3269 (706 imported, judged, not
  verified, not approved)` counts edges with `origin: imported`; the words
  after the count are fixed text. A planted imported edge with
  `quote_verified: true` and `approved_by: "nobody"` passes, and the line
  still says "not verified, not approved". In the pilot graph all 706 are
  `false` and `null` (checked by the reviewer). Fix: until real-3 checks
  quotes, fail on an imported edge that is verified or approved, or print
  the counts.
- An L3 node is not compared with the SDTM data. A planted edge to
  `sdtm:ZZ.NOSUCH`, with a node of that name, passes. The builder makes L3
  nodes from the Parquet schemas only, so the pilot graph is right. Fix:
  let `check_graph` look each L3 node up in the kit's SDTM files.

#### F7 (not blocking) 913 citations of kit documents become 706 edges

The claims files hold 1,261 citations: 348 of programs (not imported, as
ADR-001 says and the log prints) and 913 of the SAP, the data guide and
the ADaM Define-XML. An edge is one per ADaM column and span, so several
quotes on one page fall into one edge: 913 citations, 706 edges. The edge
carries the line of the claim, not of the quote. The log line per dataset
("21 claims -> 49 cites edges; 28 citations of files that are not kit
documents") does not show the merged ones. Nothing is wrong for real-1:
the edges are candidates, marked `judged` and `imported`. For real-3: one
`quote_verified` per edge cannot say which of several quotes was found.

#### F8 (not blocking) What ADR-001 item 6 does not say about the edges

- `derives_from` holds value dependencies and context dependencies (row
  template filters, lookup keys, filters and order of lookups) without
  telling them apart. 399 of the 415 columns have a value reference; 16
  have none. Of these 16, 14 are counted `to SDTM` through the filter of
  their row template (for example `ADLBC.PARCAT1`, `ADQSCIBC.PARAMCD`) and
  2 are `literal` (`ADTTE.PARAM`, `ADTTE.PARAMCD`, on a template without a
  filter). The docstring of `lineage.py` says so; ADR-001 and the gate log
  do not.
- For 238 of the 3,269 `derives_from` edges the block at the cited line
  does not name the target column: 110 cite the declaration of a lookup
  (`- id: ADSL_SBJ`), where the column is chosen at the reading column's
  own rule, and 128 are join keys, named in `input.<alias>.key` and cited
  at the rule that causes the join. This follows the stated rule ("the
  nearest place on the way that reads the target"); a reader who opens the
  line will not find the column there. One edge per pair also names one
  place only (the nearest; at the same distance the lowest file and line):
  `ADSL.CUMDOSE -> EX.EXDOSE`, the only edge to that column, cites
  `adsl_v1.yaml` line 131, the lookup `LAST_EX`, and not line 370, where
  `EX.EXDOSE` is summed.
- The hash of an L4 node covers the column's own rule. Changing the rule of
  a helper column that an output column reads (`AGE_N` from `DM.AGE` to
  `DM.AGE + 10` in the test plans) leaves nodes, edges and coverage
  byte for byte the same. The pilot has 168 helper columns and 39 lookups.
  real-1 does not need more; the edit loop of section 7.6 will.

Fix: state the three in ADR-001 or the report.

#### F9 (not blocking) P2 comparison: two edge cases

The comparison is right for what the pilot holds. Type pairs, reference
against built: `large_string`/`string` 221, `double`/`double` 160,
`date32`/`date32` 34. Null cells in the reference: 661,930; NaN cells: 0.
Double cells that differ at tolerance 0: 1,869, the largest difference
4.5e-13. Text and dates are compared exactly, a missing value equals only
a missing value, rows by position. Of 23 made-up pairs, these behave as
they should: NaN against missing (both ways), missing against a value,
empty against missing text, infinity, a trailing blank, another row order,
text against number or date or Boolean, an extra column. Two notes:

- The tolerance is absolute: 1e-12 against 9e-11 is equal. PLAN.md section
  4.6 says "numeric tolerance 1e-10" and the E1 spike did the same.
- A time stamp with a time zone against one without, at the same instant,
  is equal and is printed under "storage type only, same values". A time
  zone is not a storage type. The pilot has no time stamp column.

Treating `large_string` against `string` as storage is sound: both hold
UTF-8 text and differ in the width of their offsets; the values are
compared exactly after a cast to one of them. It is disclosed in ADR-001
item 5, in the docstring of `compare.py` and in a line of the P2 output.

#### F10 (not blocking) A1 asserts the version of the snapshots, not the revision

`a1_resolve` prints the git revision the snapshots were made with and
fails only when the version differs. ADR-001 names the revision
`c039509082b545fe913c00d1686426c3d245778c`; the run printed the same. Fix:
assert it.

#### F11 (not blocking) Planted defects: real case or simpler cousin

- Real cases: every case of `tests/unit/test_compare.py` (the reference
  stores text as `large_string`, as the pilot does); a reference with
  another value through the real engine and real files; a changed, missing
  or stray file of a kit; a changed cache; another engine version; a
  specification the engine refuses; unknown and unresolved names and a
  column without a rule, through `build_graph` and `check_graph`.
- Simpler cousins: the two wrong-literal tests (F4); `compare_builds` on
  hand-made records in place of `determinism` on a build that differs
  (F3); the data-in-git test, which plants the suffixes the check knows
  (F5).

#### F12 (not blocking, for the owner) ADR-001 changes the kit layout of section 8 without approval

ADR-001 says so itself: decisions 2 to 7 "stand unless the owner objects",
and item 3 adds `gold/reference/`, `gold/claims/`, `gold/resolved/` and
`gold/build.json` to the layout of PLAN.md section 8 and puts the ADaM
Define-XML under `inputs/docs/`. PLAN.md is not changed, and section 8 is
a design "an ADR may improve". Whether such an ADR needs the owner's
approval is the owner's call. The other notes of the ADR's "Consequences"
(no comparison with yamaa's R host for P1, quotes not checked) are
disclosed limits, not findings.

### The eight questions

1. Does the gate prove each statement? P2: yes; it needs the exact E1 line
   and every dataset equal, and the build never reads `gold/reference/`.
   P1: for two builds in one place, yes; a dependence on the folder would
   pass (F3), and the reviewer's builds elsewhere show there is none.
   Trace: it proves that the graph files agree, fit the schema and record
   no gap; it cannot see a missed reference (F4) and it would count a
   column behind a listed gap as complete (F2). R7 supports the pilot
   graph from the engine's side. Kit: the hash check is complete; the
   data-in-git check is by suffix (F5).
2. Real cases or cousins: F11.
3. P2: right for the pilot; F9.
4. P1: the bytes are canonical in every variation tried (R3); F3 for the
   test.
5. Graph: all 805 nodes and 3,975 edges fit the schema; `derives_from` is
   `static`, `cites` is `judged`, `imported`, not verified, not approved.
   The lineage follows helper columns, lookups, row templates, `SELF` and
   inputs from other datasets as Pilot 7's code does (A3), and adds gaps
   for unknown names. No wrong `to SDTM` or `literal` was found in the
   pilot. One way to get a wrong `literal` exists (F2). Notes on the edge
   line and on context dependencies: F8.
6. Clean room: nothing third-party is committed except adapted code;
   `lineage.py` is recorded correctly; `runner._relocate` is not (F1).
7. Claims beyond the evidence: `kits/README.md` on the data-in-git check
   (F5); ADR-001 item 6 on `literal` (F2) and on what an edge means (F8).
   The rest of ADR-001, the kit README and CLAUDE.md match the code: the
   wheel is pinned by hash and installed with `--require-hashes
   --only-binary=:all:`; `save()` is never called; the kit has 64 files;
   221 columns differ in storage type only; all 111 SDTM nodes cite an
   `ItemDef` line of the SDTM Define-XML.
8. Scope: the diff does not touch PLAN.md or `standard/schemas/`, and
   holds nothing of real-2. The kit layout: F12.

### Not checked in this pass

- `docs/reports/real-1.md`, `docs/reports/real-1.gate.log`,
  `docs/state/real.md` and the clean-clone gate: second pass.
- A fresh install and a fresh fetch (no network was used).
- `specfirst kit lock cdiscpilot01` on the real kit: it rewrites a tracked
  file.
- The quotes of the imported claims against the documents (real-3).
- The 39 SDTM columns of R7 that could not be rolled (21 constant, 18
  refused by the engine).

## Second pass

Reviewed in this pass:

- Commit `6e6a2ce1bc54e7fe7b6351ec5b2e6f94720cc002` (`6e6a2ce`), "real-1:
  fixes from the first pass of the independent review": the diff
  `4b12c86..6e6a2ce`, 19 files, 768 insertions, 166 deletions.
- Three files that are not committed yet, as they stood when read:

  | File | Lines | SHA-256 |
  | --- | --- | --- |
  | `docs/reports/real-1.md` | 467 | `bb2693aaaf2db406d1eefbbab82eb945617a6e1e30028198566f37323b0aa27e` |
  | `docs/reports/real-1.gate.log` | 270 | `ed09036fc24ea03375d98a08dce948f2372ad51adda77dee216308ffadf22678` |
  | `docs/state/real.md` | 59 | `6ab7a40419e5aeebf03160fa09e0c1ec93099739ebf53c3dd798e3b2a4373eaa` |

  The report still held the line `@@REVIEW_VERDICT@@`, kept for the
  outcome of this pass.
- The clean clone of the second gate run,
  `/tmp/specfirst-clean-mdfd8f/specfirst`: HEAD `6e6a2ce`, no uncommitted
  change. It was read, not changed. It is gone now: the WSL distribution
  stopped while idle and cleared `/tmp` when it started again, after the
  comparisons below were made.

The same limits as in the first pass: no tracked file changed, no commit,
this file only; the fetch cache untouched (`specfirst fetch --verify`
passed before and after: `fetch: every pin verified`); no network.

### Outcome of the second pass

All twelve findings of the first pass are answered, and F1, the one that
blocked, is fixed. The gate passed on a clean clone of `6e6a2ce`, and the
log in `docs/reports/real-1.gate.log` is the log of that run. The report
agrees with the log and the code in every quoted line and every number
that was checked; four sentences need a correction of wording (C1 to C4
below), and none of them changes a result. Seven new findings (N1 to N7)
do not block. Nothing else blocks the merge of `track/real` into `main`.

### What was run

`<scratch>` is a scratch folder outside the repository. Builds of the
experiments ran under `/var/tmp` and were removed.

| # | What | Result |
| --- | --- | --- |
| S1 | `python -m pytest -m "not evidence" -q` in the worktree | `340 passed, 13 deselected in 22.16s` |
| S2 | `specfirst gate real-1` in the worktree at `6e6a2ce` | `GATE real-1: PASS`, exit 0, 11 of 11 checks |
| S3 | the gate log against the clean clone | the log is authentic (below) |
| S4 | every line the report quotes, against the log | 135 quoted lines, all in the log, in order |
| S5 | `build.json` of six builds in three checkouts | byte for byte the same (below) |
| S6 | the graph code of `4b12c86` and of `6e6a2ce` on the pilot | the same 3,975 pairs (below) |
| S7 | the planted defects of the first pass, again | below, per finding |
| S8 | A5 on the case of F1 | it fails, as it should (below) |
| S9 | A4 made stronger: constant columns changed too | no dataset changed (N1) |
| S10 | the numbers of the report, each from the built files | all agree (below) |

#### S2 The gate in the worktree

```text
gate real-1 at commit 6e6a2ce1bc54e7fe7b6351ec5b2e6f94720cc002 (with uncommitted changes)
340 passed, 13 deselected in 21.20s
study data in git (E20): 119 maintained files checked, 0 problems
P1 determinism: 23 of 23 files have the same SHA-256 in both builds
TOTAL cells=9119605 mismatched=0
numbers equal within the tolerance but not exactly: 1869 cells, largest difference 4.5e-13
storage type only, same values (reference -> built): large_string -> string in 221 columns
TOTAL         415     413      14       2     0
nodes: L0 279, L3 111, L4 415
edges: cites 706, derives_from 3269
cites edges: 706 imported, 0 with a verified quote, 0 approved by a person
trace: complete
Pilot 7 pins yamaa at git revision c039509082b545fe913c00d1686426c3d245778c (cdiscpilot01/program/adam/python/requirements.txt)
snapshots were made with yamaa 0.7.0 built from git revision c039509082b545fe913c00d1686426c3d245778c
SDTM columns with a node in the graph: 111; without one: 202, all of them rolled by one row (131 hold more than one value)
ADaM datasets that changed: none
recorded as adapted: src/specfirst/machine/lineage.py shares 73 lines with cached sources
recorded as adapted: src/specfirst/machine/runner.py shares 3 lines with cached sources
compared 45 Python files of ours with 673 of p7, yamaa, p6, ars; the most lines a file that is not recorded shares: 1 (allowed: 2)
5 passed in 56.70s
ASCII check: 119 files checked, 0 with non-ASCII bytes
PASS  environment          0.4 s
PASS  pins                 0.1 s
PASS  lint                 0.1 s
PASS  unit tests          21.7 s
PASS  kit                  5.2 s
PASS  P1 determinism     107.5 s
PASS  P2 reproduction      4.8 s
PASS  trace                5.3 s
PASS  pilot tests         57.2 s
PASS  cache untouched      0.1 s
PASS  ASCII                1.3 s
GATE real-1: PASS
```

The tree had the author's uncommitted report files and this review, so
the first line says so and the counts of maintained files are 119, not
the 116 of the clean clone. The ASCII check and the test for LF line
endings pass with them.

#### S3 The gate log is the log of the clean clone

```text
cmp build/gates/real-1/clean-clone.log docs/reports/real-1.gate.log          -> identical
clone: git rev-parse HEAD -> 6e6a2ce1bc54e7fe7b6351ec5b2e6f94720cc002; git status --porcelain -> 0 lines
clone gate.log lines: 220 ; equal to lines 49 to 268 of the report's log: True
```

The last line compares `build/gates/real-1/gate.log` inside the clone,
which the gate itself wrote, with the part of
`docs/reports/real-1.gate.log` from `gate real-1 at commit ... (clean)` to
`GATE real-1: PASS`.

#### S5 One build.json in three checkouts

```text
clean clone, /tmp/specfirst-clean-mdfd8f/specfirst/build/p1/cdiscpilot01/first and second:
    sha256 f452650d2cd08cb0... (both)
identical: /mnt/d/trial_work/specfirst-real/build/p1/cdiscpilot01/first/gold/build.json   (and second)
identical: /var/tmp/sfreview2/root-with-another-name/build/kits/cdiscpilot01/gold/build.json
identical: /var/tmp/sfreview2/root-with-another-name/build/p1/cdiscpilot01/first/gold/build.json
```

The third checkout was a minimal one of the reviewer (PLAN.md,
`third_party/sources.yaml`, the kit manifest, the schemas), built with
`PYTHONHASHSEED=7 TZ=Asia/Tokyo LC_ALL=C`. There `specfirst build`,
`specfirst check` and `specfirst check --twice` all exited 0. None of the
24 files of the worktree's first build holds `/mnt/`, `/root/`, `/tmp/`,
`trial_work` or the name of the worktree. This confirms the sentence of
the report that the `build.json` of the clean clone equals that of a build
in the worktree.

#### S6 The new graph code gives the same graph, with other places and hashes

`_trace_column` was rewritten. The code of `4b12c86` (from `git show`) and
the code of `6e6a2ce` were run on the same resolved pilot specifications:

```text
edges old 3975 new 3975 same pairs: True
node ids same: True
cites edges equal: True
coverage terminal/sdtm/inputs/gaps equal: True
derives_from edges whose cited place changed: 758 of 3269
node hashes changed: Counter({'adam': 415}) node sources equal: True
edges whose cited block does not name the target: old 238 new 129
new, by kind of cited line: {'rule': 128, 'lookup or row declaration': 1}
```

So nothing was lost: the same nodes and the same pairs, and the result of
the perturbation runs of the first pass (R7), which rest on the pairs
only, holds for the new graph. `lineage.py` and `canonical.py` are not in
the diff. The Parquet and resolved files have the hashes of the first
pass; the three graph files have new ones, as they must.

#### S10 Numbers of the report

| In the report | Checked against | Result |
| --- | --- | --- |
| 340 unit tests, 13 deselected | S1, S2, log line 93 | agree |
| 64 files, 7,093,621 bytes; 3, 23, 18, 10, 10 per part | the assembled kit | agree |
| SAP hash `210b7f1f...1bc7`, the pin of Pilot 6 | `kit.yaml`, `sources.yaml` | agree |
| 9,119,605 cells, 0 mismatched; 221 columns | log, S2 | agree |
| 1,869 cells within the tolerance, largest 4.5e-13 | own count of the first pass (F9), log, S2 | agree |
| 805 nodes: 415, 111, 279; 3,975 edges: 3,269 and 706 | log, built files | agree |
| 413 to SDTM, 14 by rows, 2 literal, 0 gaps | log; `value` is false for 16 columns, the same 16 the first pass found | agree |
| 222 claims, 1,261 citations: 913 of kit documents, 348 of programs; 706 edges | sums of the ten log lines; `coverage.json` | agree |
| 202 columns without a node, 131 with more than one value | own count | agree |
| A5: 45 and 673 files, at most 1 shared line | S2 | agree |
| ADSL.BMIBL: lines 677, 671, 775, 656, 109, 664, 120; `define.xml` line 4997; 9 SDTM columns | `edges.jsonl`, `nodes.jsonl`, `coverage.json`, the lines of `adsl_v1.yaml` | agree |
| the main checkout at `54f8934` on `track/base` | `git worktree list` | agrees |
| `track/real` pushed | `origin/track/real` is `6e6a2ce` in the local refs | agrees |

The walk of ADSL.BMIBL lists not every edge of HEIGHTBL and WEIGHTBL: both
also have the edge to `sdtm:DM.ACTARM` (line 775), and WEIGHTBL the two to
`adam:ADSL.STUDYID` and `adam:ADSL.USUBJID` (line 120). What it lists is
right.

Not checked, because it needs the network: the two CI runs on GitHub the
report names. Not checkable any more: the end of the first clean-clone
run at `4b12c86`; a copy of its log taken while it ran shows checks 1 to 7
passed.

### The findings of the first pass, one by one

| # | What was done, as found in the code | Tried again | Enough |
| --- | --- | --- | --- |
| F1 | `third_party/SOURCES.md` has a row for `runner.py`; the docstring of `_relocate` names source, commit, copyright and license file; the notice file lists both files and still ends with Pilot 7's `LICENSE`, unchanged; `test_sources.py` expects both rows; new test A5-adapted | S8 | yes |
| F2 | `build_graph` adds "reads X, which has a gap" for every column reached; `check_graph` computes the same from `edges.jsonl` | S7 | yes |
| F3 | `build` assembles the kit in the folder it builds in; the two builds of P1 share no path of the kit; a unit test plants the defect in the build processes | S7 | yes; N2 |
| F4 | A4-unread in `tests/pilot` and in the gate; the docstring of `check_graph`, ADR-001 and the report say what the check proves; the two unit tests are marked as what they are | S7, S9 | yes; N1 |
| F5 | more suffixes; an `.xml` file with `<ODM`; any file byte for byte equal to a pinned file; `kits/README.md` says what is seen | S7 | yes; N5 |
| F6 | the cites line counts imported, verified and approved edges; `build.trace` hands the SDTM columns of the kit to the check | S7 | yes |
| F7 | the log shows citations and edges per dataset; ADR-001 says what an edge stands for | S10 | yes |
| F8 | `coverage.json` has `value`; a rule is preferred as the place of an edge; the node hash covers helpers, lookups and row templates; ADR-001 item 6 says all three | S6, S7 | yes; N3, N4 |
| F9 | with and without a time zone are two kinds; P2 prints the cells that rest on the tolerance; the tolerance is stated as absolute | S7 | yes; N6, N7 |
| F10 | A1 fails when the snapshots' revision is not the one Pilot 7's requirements file pins | S2 | yes |
| F11 | the three cousins are replaced by real cases (F3, F4, F5) | S7 | yes |
| F12 | stated in the report, in the state file and in ADR-001; the owner's call | - | open for the owner, not blocking |

The suggestion of F3 to name polars in `build.json` was wrong, and the
report is right not to follow it: after a full build of the pilot the
Python module `polars` is not loaded, and yamaa's wheel requires polars
for its tests only.

#### S7 The planted defects again

The outputs below are shortened: `...` stands for text left out, lines of
one kind are put together, and the words in round brackets after a file
name are the reviewer's.

F2, the plans of `tests/unit/test_graph.py`, AGEGR1 with an unknown name:

```text
AGEGR1 : gap ['unknown name AGE_TYPO at gold/spec/adsl.yaml:30']
AGEGR1N: gap ['reads adam:ADSL.AGEGR1, which has a gap']
listed ['adam:ADSL.AGEGR1'] -> problems: ['adam:ADSL.AGEGR1N: gap with no listed reason: reads adam:ADSL.AGEGR1, which has a gap']
listed ['adam:ADSL.AGEGR1', 'adam:ADSL.AGEGR1N'] -> problems: [] | ['ADSL            5       2       0       1     2']
across datasets, ADAE.GRP = SBJ.AGEGR1 through a lookup on ADSL, ADAE.GRPN reads GRP:
   adam:ADAE.GRP gap ['reads adam:ADSL.AGEGR1, which has a gap']
   adam:ADAE.GRPN gap ['reads adam:ADSL.AGEGR1, which has a gap']
   adam:ADAE.USUBJID sdtm []
```

F3, the toy kit, defects planted through a `sitecustomize` in the build
processes:

```text
control: P1 passed=True; files that differ: none; occurrences of the checkout path in the built JSON files of the first build: 0
absolute paths of the kit left in the resolution: P1 passed=False; files that differ: ['gold/graph/edges.jsonl', 'gold/graph/nodes.jsonl', 'gold/resolved/adae.json', 'gold/resolved/adsl.json']; occurrences ...: 213
hash of a graph element depends on the process: P1 passed=False; files that differ: ['gold/graph/nodes.jsonl']
a built file names the checkout root: P1 passed=True; files that differ: none; occurrences ...: 2
```

The case of the first pass is caught now. The last line is N2.

F4, edges of HT removed and its coverage entry set to `literal`:

```text
check problems: [] | ['ADSL            5       3       0       2     0', ...]
```

As before, and as the docstring, ADR-001 and the report now say: the
trace check cannot see it. A4 is the test for it (S2, S9).

F5, real files in a checkout with a tier C kit:

```text
FOUND     docs/define-adam.xml           (an edited Define-XML)  a Define-XML or other ODM file in git
FOUND     third_party/pilot/define.xml   (the pinned one)        a Define-XML or other ODM file in git
FOUND     tests/data/adsl-claims.json    (the pinned claims)     byte for byte gold/claims/adsl-claims.json of kit toy
FOUND     data/dm.bin                    (a pinned dataset)      byte for byte inputs/data/sdtm/dm.parquet of kit toy
FOUND     evidence/adsl.xpt, docs/SAP.PDF, data/adsl.rds, data/adsl.sas7bdat, data/dm.feather, data/adsl.tsv
not found docs/csr.txt, docs/own.xml (an SVG), docs/not-there.xml, kits/toy/kit.yaml
not found docs/define.txt, docs/define-utf16.xml, docs/define-late.xml, docs/claims-pretty.json, docs/claims.json.gz
real checkout: 66 pinned hashes; problems: []
```

The first two "not found" lines are right. The third is N5.

F6:

```text
edge to sdtm:ZZ.NOSUCH with a node of that name: ["node sdtm:ZZ.NOSUCH: not a column of the kit's SDTM data"]
imported edge with quote_verified true and approved_by "nobody": problems [] | ['cites edges: 1 imported, 1 with a verified quote, 1 approved by a person']
```

F8, node hashes:

```text
helper AGE_N changed: hashes that changed: ['adam:ADSL.AGEGR1']
lookup BASE keep first -> last: changed: ['adam:ADSL.HT']
row template filter changed: changed: ['adam:ADSL.FLAG', 'adam:ADSL.HT', 'adam:ADSL.USUBJID']
pilot: the only edge to sdtm:EX.EXDOSE now cites adsl_v1.yaml line 370, where it is summed
```

F9:

```text
time zone against none, same instant: equal=False mismatched=1
seconds against milliseconds: equal=True storage=[('D', 'timestamp[s]', 'timestamp[ms]')]
1e-12 against 9e-11: equal=True mismatched=0 close=1 largest=8.9e-11
```

#### S8 A5 on the case of F1

A5 was run on a copy of `src/` and `tests/` with a `SOURCES.md` from
which the row of `runner.py` was taken out, and again with six lines of a
file of yamaa put into a new file of ours:

```text
== SOURCES.md without the row of runner.py
   problems: ['src/specfirst/machine/runner.py: shares 3 lines with cached sources, for example with p7:.github/scripts/resolved_specs.py, and is not in SOURCES.md']
== six lines of yamaa/evaluations/harbor/author.py in a new file of ours
   problems: ['src/specfirst/borrowed.py: shares 6 lines with cached sources, for example with yamaa:evaluations/harbor/author.py, and is not in SOURCES.md']
```

A5 would have found F1, by one line (3 shared, 2 allowed). Lesson 14 and
the report say what it cannot find.

### New findings of the second pass

None blocks.

#### N1 A4 changes 131 of the 202 columns it names, and the texts say all

A4 rolls every SDTM column that has no node. A roll changes nothing in a
column that holds one value, and 71 of the 202 are such columns; the test
prints it ("131 hold more than one value"). For those 71, A4 shows
nothing. ADR-001 item 6 ("with every SDTM column that has no node
changed"), lesson 16 ("changes every SDTM column that has no node") and
the report (C2) say more than that. The same holds for the sentence of
this review's first pass, R7: "(1) the graph has a node for every SDTM
column the build reads".

The claim itself is true. S9, on the assembled pilot kit: the 131 rolled,
the 70 constant columns emptied (all values missing), the one column that
is all missing filled:

```text
SDTM columns with a node: 111 ; without one: 202 {'constant, emptied': 70, 'rolled': 131, 'all missing, filled': 1} types: {'large_string': 176, 'double': 26}
ADaM datasets that changed: none
```

Fix: let A4 do the same (a few lines), or word the three texts as the test
prints it. Either can wait for the first commit of real-2.

#### N2 P1 sees the folder of a build, not the checkout or the environment

Both builds of P1 run in one checkout and one environment. A byte that
depends on the checkout root passes (S7, last line of F3). There is no
such byte in the delivered code: S5. That comparison between checkouts is
made by hand, in the report and here; the gate does not make it. A note
in ADR-001 item 4 would be enough; a comparison of the clone's
`build.json` with a recorded hash is not possible, because the hash
changes with every change of the graph.

#### N3 The place of an edge: two cases outside the stated rule

- A column taken through a lookup over `SELF` that is an output column is
  cited at the declaration of the lookup, not at the rule that names it:
  the first branch of the walk uses `site`, the second `taken`. One edge
  of the pilot: `ADQSNPIX.AWTDIFF -> ADQSNPIX.ADY` cites `adqsnipx.yaml`
  line 123 (`- id: BASE_LKP`); the rule that names `BASE_LKP.ADY` is line
  2625. It is the one of the 129 edges of S6 that is not a join key.
- When two rules at the same distance name the same lookup column, the
  one walked first gives the place, not the lowest line. Made-up case:
  helper AB (line 20) and helper ZA (line 10) both read `BASE.VSSTRESN`;
  the edge cites line 20. ADR-001 says "then the lowest file and line".

The place is the same in every build either way.

#### N4 `value` counts the filter of a specification as part of the rule

With a top-level `filter` in the specification, a literal column gets
`value: true` and is counted neither as literal nor "by rows":

```text
STUDYID = 'DEMO' with a top-level filter: {'column': 'adam:ADSL.STUDYID', 'terminal': 'sdtm', 'sdtm': 1, 'value': True, ...}
```

No specification of the pilot has such a filter, so the 14 and the 2 of
the gate output are right.

#### N5 An ODM file is seen only as `.xml`, in ASCII or UTF-8, near its start

`kits/README.md` says the check fails on "a Define-XML or other ODM file".
The code looks for `<ODM` in the first 65,536 bytes of a file with the
suffix `.xml`. Not found in S7: an edited Define-XML named `.txt`, one in
UTF-16, one with a long comment before the root element. A pinned file
that was indented again or compressed is not found either; the README's
last sentence ("retyped or converted") covers that.

#### N6 Two time zones at one instant are printed as storage type only

A time stamp in UTC against the same instant in another zone is equal and
is listed under "storage type only, same values". The comment in
`compare.kind` says a time zone is meaning, not storage. The pilot has no
time stamp column.

#### N7 Two sentences of ADR-001 item 5

- "The tolerance of 1e-10 is absolute, as PLAN.md section 4.6 words it":
  the plan says "numeric tolerance 1e-10" and no more. The docstring of
  `compare.py` has it right ("as in the E1 spike").
- "A column whose kind differs (text against number) mismatches in every
  cell": in every cell that is not missing on both sides, as the docstring
  of `compare.py` says and `test_compare.py` shows (3 of 4).

### The report, the state file and ADR-001

Every line the report quotes from the gate log is in the log, in order
(S4), and the log is the clean clone's (S3). Every number checked agrees
(S10). The table "Review, first pass" describes the actions as the code
has them. `docs/state/real.md` agrees with the report and the code.

Four sentences of the report need a correction. None changes a result.

- C1, section "The gate": "`[...]` marks where lines of the full log are
  left out: the lines of `specfirst doctor` and of the pin listings,
  pytest's progress dots, 19 of the 23 hash lines of P1, and 9 of the 10
  per-dataset lines of the claims and of the tests A1 to A3." Six more
  lines are left out and not named: lines 7 to 12 of the log (the three
  git commands that make the clone, and the commit line `git log` prints)
  and lines 16 and 18 (two lines about the R library).
- C2, table of section "The engine and the runner", row A4-unread: "With
  all 202 SDTM columns that have no node in the graph rolled by one row,
  the engine builds the same 10 datasets: the graph has a node for every
  SDTM column the build reads." The roll changes 131 of the 202 (N1). The
  conclusion is shown for all 202 by S9 of this review, not by A4.
- C3, paragraph "P1 beyond the gate": "The reviewer built three more times
  from other folders, with other thread counts, hash seeds, time zone and
  locale, and got the same 23 hashes (review, R3)." The thread counts
  were not varied: see the correction to R3 below. Those three builds
  were of `4b12c86`; for `6e6a2ce` see S5.
- C4, section "P2: what equal rests on": "A column of another kind (text
  against number, a time stamp with a time zone against one without)
  mismatches in every cell." In every cell that is not missing on both
  sides (N7).

One more, as the author sees fit: the row F8 of the table says the counts
were not made again. They are in S6: 238 became 129, the 128 join keys and
the one edge of N3.

### Corrections to the first pass

- R3 said the bytes do not depend on "the number of threads". The setting
  used, `POLARS_MAX_THREADS`, is not read by a build: the Python module
  `polars` is not loaded, and the name is not in yamaa's native library.
  Folder, hash seed, time zone and locale were varied; the thread count
  was not.
- R7 (1) said the graph has a node for every SDTM column the build reads.
  The roll showed it for 131 of the 202 columns; S9 shows it for all.
- F3 suggested naming polars in `build.json`. Withdrawn.

### What else could block the merge

Nothing found.

- `track/real` is two commits ahead of `main` and none behind
  (`git rev-list --count`: 2 and 0): the merge is a fast-forward as long
  as `main` stays where it is.
- The diff `main..6e6a2ce` does not touch PLAN.md or `standard/schemas/`
  and holds nothing of real-2.
- The commit that adds the report, the gate log, the state file and this
  review must add nothing else, so that the gate evidence of `6e6a2ce`
  stands for it, and the placeholder line of the report must be gone. The
  ASCII check and the LF test passed in the worktree with these files in
  place (S2).
- F12 stays open for the owner.

### Not checked in the second pass

- The two CI runs on GitHub (no network).
- A fresh install and a fresh fetch by the reviewer; the clean-clone log
  shows them, and its gate part equals the clone's own gate log (S3).
- The report after its corrections C1 to C4 and after the placeholder is
  replaced.

The first pass failed commit `4b12c86` on F1. The second pass covers
commit `6e6a2ce`, `docs/reports/real-1.md` and `docs/state/real.md` as
read (hashes above, with the corrections C1 to C4 still to be made), and
the clean-clone gate log `docs/reports/real-1.gate.log`.

Verdict: PASS
