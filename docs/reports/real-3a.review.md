# real-3a Layout, grid and trace: independent review

Reviewed: part real-3a of ADR-005 (decision 1), on branch `track/real`, as
it is at `f55f40d`.

- The diff `main..track/real`: `main` is `f42a3fa`, `track/real` is
  `f55f40d67f47ae5fbbdd9d559a2e5c47c0a88850`; 60 files, 6,737 insertions,
  417 deletions. Six commits: `bd34260` (the findings F2 to F12 of the
  review of real-2), `4f7e581` and `faa8a5f` (real-3a), `0938fe4` (the
  state file), `9730843` (the report and two gate logs), `f55f40d` (the log
  of the clean-clone gate and the report again). The review began at
  `9730843`; `f55f40d` changes two files under `docs/reports/` and nothing
  else (R14). Nothing under `src/`, `r/`, `tests/`, `standard/` or `kits/`
  differs between `0938fe4` and `f55f40d`.
- No file was uncommitted but this one. The documents the findings quote,
  as committed at `f55f40d`:

  | File | Lines | SHA-256 |
  | --- | --- | --- |
  | `docs/reports/real-3a.md` | 774 | `ba414e23a2543d95d6ba27a0b57aa410e3e41818db3e160738791cf40880deb9` |
  | `docs/reports/real-3a.gate.log` | 405 | `d80be3d8bcdd44f4c844f15747430e4707f9c0c4f17580c888a38f47cefb4ec1` |
  | `docs/reports/real-3a.real-2.gate.log` | 358 | `e4d6a90f580a599f9e13bc35feaaffc4a954a49ec4433d593179d4cad095c727` |
  | `docs/reports/real-3a.clean-clone.gate.log` | 455 | `ca4ee42ce104ddc08132ed70db9793ea330a7879305f9ea8bbd0d6ef7dc3cd35` |
  | `docs/decisions/ADR-003.md` | 300 | `cc874c028f277866770aef1a598f88a003fc8188fe55ad94241c26b2159be737` |
  | `docs/state/real.md` | 313 | `01d9bb7e4db1c26f80bfd6b88110b19c2b470a507b83b7cfbf9c7593134f3e0c` |

Date: 2026-11-17.

Reviewer: an independent agent with a fresh context that did not write the
work (rule R7). Correctness only, no style remarks. The reviewer changed no
tracked file, made no commit, and wrote this file only. No network was
used, nothing was posted, no package was installed.

## Outcome

No finding blocks, by the measure this review was given: a statement of the
gate text that is not proven, a check that passes on a defect it claims to
catch, a number that matters that is wrong, or a rule of PLAN.md section
2.1 that is broken. The three statements of the gate text hold in every
check the reviewer made:

- `specfirst gate real-3a --clean` exited 0 on the reviewer's clone of
  `9730843`: 16 of 16 checks. Its 405 lines are those of the author's two
  logs, apart from the commit, the count of files, seconds and folders
  (R1). The two committed logs are, byte for byte, the logs of the runs
  they name (R2).
- Cell text. The reviewer's own recount, which uses none of the checking
  code: 27 cells show 51 results, and every cell is the example's formatted
  values of its results joined by one blank (R3).
- Trace. The reviewer's own walk from `nodes.jsonl` and `edges.jsonl`: 27
  of 27 cells reach SDTM columns, through 51 ARD rows, 9 analyses and 15
  ADaM columns to 15 SDTM columns; the 52 `reads` and the 75 `computes`
  edges are what the reviewer reads from the ARS file (R5).
- Determinism. Three builds of the reviewer in other folders, two of them
  under other settings, give the 30 hashes of the author's log (R6).
- The findings F2 to F12 of the review of real-2 are fixed as the report
  says, and the fixes changed no result: the three result files have the
  hashes that review recorded (R6 to R9).

Nine findings do not block (F1 to F9). One of them is a statement of fact
that is wrong and should be corrected before the merge, although it is none
of the four kinds above: ADR-003 and the report say that the table shell
the example names is not in its repository. It is, at the pinned commit,
next to the example (F1). So the conclusion that no check can hold the
order of the parts of a cell against this reference, which the state file
repeats, does not stand, and the grid differs from that shell by one line
of the row axis that nobody recorded. The others with weight: with a
data-driven column grouping, which a compiled study has, an arm without a
record in one analysis stops the build (F2); the comparison passes a
layout that pairs the count of one row with the percent of another (F3);
and the tests of D8 do not see a single `reads` or `computes` edge that is
left out when the analysis of the denominator covers for it (F4).

The verdict covers `f55f40d`. The reviewer asks for two corrections of
documents in the commit that adds this review: the sentences of F1, and
`docs/state/real.md`, which still describes the part as it stood before
its gate ran (F9). Neither changes code, so the gate evidence stands. A fix
of any other finding changes code or a built file: it belongs to a later
commit with its own gate run, as F2 to F12 of real-2 were handled.

## Scope and method

### What was read

- `CLAUDE.md`; PLAN.md sections 2, 4.1, 4.2, 4.6, 4.8, 7.1 to 7.5, 9.5 and
  the entries real-1 to real-3 of section 13.3; `docs/decisions/ADR-005.md`
  and `ADR-003.md`; `docs/reports/real-2.review.md`;
  `docs/reports/real-3a.md` as at `9730843` and its change in `f55f40d`;
  `docs/state/real.md`; `docs/lessons.md`; `standard/methods/README.md`.
- Of the diff, in full: `src/specfirst/machine/{results,layout,grid,render,
  graph,build,methods}.py` and `src/specfirst/gates.py` as they are now;
  the changes of `machine/{ard,ars,rengine}.py`, `kit.py` and `cli.py`; the
  changes of `r/specfirstr/R/{engine,methods,util,vectors}.R`; the entries
  `display.pattern`, `test.fisher.exact` and `summary.continuous` and
  `registry.json`; `tests/defects/test_defects.py`; `tests/toy_displays.py`
  and `tests/toy_results.py`; the changes of `tests/methods/` and of
  `tests/pilot/test_pilot.py`; `kits/cdiscpilot01/{kit.yaml,README.md,
  gold/exceptions.yaml,gold/layout/Out14-3-1-1.yaml}`;
  `evidence/adr003_rounding.{sh,out}`; the changes of `ADR-002.md`,
  `README.md`, `third_party/SOURCES.md` and the README files.
- In part: `tests/unit/test_grid.py` (the tests of the data-driven
  grouping, of the planted layouts, of the page and of the built display),
  `tests/unit/test_rengine.py` (the tests of rules I3 and I9),
  `tests/unit/test_gates.py` (the test of this gate); of
  `tests/unit/test_cells_trace.py` and `test_results.py` the names of the
  tests only. All of them ran in R1.
- In the fetch cache, read only: the pinned ARS repository (the list of its
  files, the folder of the example, the example's JSON, and the shell
  `AE_Summary_Table_Shell.pdf`, as text made with poppler 24.02 in the
  scratch folder); the R files of every cached source, by a script that
  compares lines (R13).
- Outside the repository, read only: the author's clones and logs under
  `/root/scratch/real3a` and the clean clone under `/tmp`, for R2.

### What was run

All Linux commands ran in Ubuntu 24.04 under WSL2 as root, from script
files, after the `scripts/env.sh` of the worktree, with
`PYTHONDONTWRITEBYTECODE=1` and with `specfirst` taken from the reviewer's
clone of `9730843` on the Linux file system. The gate, the builds and the
large Fisher tables ran under `flock /run/lock/specfirst-heavy.lock`.
Python 3.12.3, R 4.6.2. `<scratch>` is `/root/scratch/review-real3a`:
everything the review wrote is there, and the scripts are in
`<scratch>/scripts`. Experiments that need a build used a copy of the first
build of the author's gate run or the reviewer's own builds; all of these
have the same 30 hashes (R6). R1 to R14 name the runs of this review; a
rule of the plan is always written out as "rule R11". The text blocks show
what the reviewer's scripts printed. Where a block is an excerpt, or lines
are shortened or drawn together, the scripts print them in full when they
are run again.

Side effects outside `<scratch>`: none in the worktree but this file. The
reviewer's gate wrote its `build/` folder into the reviewer's clone, and
pytest its folders under `/tmp`. In the
author's two clones, in the clean clone and in the cached ARS repository
`git status`, `git rev-parse`, `git ls-files` and `git log` were run; a
`git status` may refresh the index file of a repository, and nothing else
of them was written. `specfirst fetch --verify` after the last run: every
pin verified.

| # | What | Result |
| --- | --- | --- |
| R1 | `specfirst gate real-3a --clean` on a clone of `9730843` | `GATE real-3a: PASS`, exit 0, 16 of 16 |
| R2 | the committed logs against the runs; the report's quotes against the logs | byte for byte the logs of the runs; 263 lines of the three long quotes, all in the logs, in order |
| R3 | the reviewer's own recount of the grid, the shell and the pages | 27 cells, 51 results, 27 equal |
| R4 | 44 planted changes of the layout, the results, the grid, the shell and the pages | 23 pass `display_problems`, 21 of them the counts of the gate too; F3, F6 |
| R5 | the reviewer's own walk of the cells; 22 planted gaps of the trace | 27 of 27 complete; 4 single edges are seen by nothing; F4 |
| R6 | three more builds in other folders, two of them under other settings | 30 files, the hashes of the author's log |
| R7 | the proofs: every entry with every other proof; a planted population | nothing passes on the 25 entries; 36 wrong quartiles of ours pass; F5 |
| R8 | the Fisher test: Python, R, `fisher.test`, exact fractions | agree to 2.1e-13 on 356 tables; the six tables of F3 follow the registry |
| R9 | both engines at the edges of rules I3 and I9 and of the hand-over | the same rows; one sentence of I9 holds in R only (F8) |
| R10 | `display.pattern` at its edges; the bound of `between_equal_values` | 40 of 40 as the statements say; the bound holds for the nine definitions |
| R11 | 31 layouts and data sets of the reviewer on the made-up study | as worked out by hand; F2 |
| R12 | ADR-003: the rounding script; the counts on the formatted values; the shell | the same bytes; the same counts; F1 |
| R13 | clean-room scans; what did not change | nothing found; `PLAN.md`, `standard/schemas/`, `env/` unchanged |
| R14 | `f55f40d`: what it changes; the ASCII check | two files of `docs/reports/`; 391 files, 0 with non-ASCII bytes |

#### R1 The gate

```text
$ git clone --quiet --no-local /mnt/d/trial_work/specfirst/.git <scratch>/clone
$ git -C <scratch>/clone checkout --quiet --detach 9730843
$ cd <scratch>/clone && export PYTHONPATH=$PWD/src PYTHONDONTWRITEBYTECODE=1
$ flock /run/lock/specfirst-heavy.lock python -u -m specfirst gate real-3a --clean
gate real-3a at commit 973084376618c487cd98902aa5cd8b8153ea8983 (clean)
775 passed, 22 deselected in 43.45s
Python implementations: 99 cases of 8 methods, 0 differences
R implementations: 64 cases of 6 methods, 0 differences
P1 determinism: 30 of 30 files have the same SHA-256 in both builds
TOTAL cells=9119605 mismatched=0
grid Out14-3-1-1: 27 cells, 27 print a number; 27 of the 27 cells with results have a complete path to SDTM columns
trace: complete
results common-safety-displays, engines: 4238 results in both, 0 disagree; largest relative difference 2.4e-13 (allowed 1e-09)
results: pass
grid Out14-3-1-1: 27 cells show 51 results; 27 cells equal the reference's formatted values, 0 differ, 0 of them with one class
grids: 1 outputs, pass
6 passed in 46.82s
59 passed in 54.16s
ASCII check: 390 files checked, 0 with non-ASCII bytes
GATE real-3a: PASS
```

It waited for the lock from 11:58 and ran from 12:17:49 to 12:20:59. The
gate part has 405 lines, as both logs of the author have. After seconds,
folders and pytest's progress dots are made alike, 375 lines remain in
each:

```text
against the author's run at 0938fe4: differing lines: 4
against the clean-clone run at 9730843: differing lines: 6
```

The four are the commit, 390 against 387 files (twice: the report and the
two logs that `9730843` adds) and the form of one pytest time. The six are
folders only (the environment and the cache of the clean clone). All 30
hash lines of P1 of the reviewer's run stand in the author's log.

#### R2 The logs are the logs of this code; the quotes

```text
cmp docs/reports/real-3a.gate.log <author>/clone-0938fe4/build/gates/real-3a/gate.log   -> identical
cmp docs/reports/real-3a.real-2.gate.log <author>/clone-bd34260/build/gates/real-2/gate.log -> identical
clone-0938fe4: HEAD 0938fe4e3bef90b0a47762acc9b4c1ea9b731123, no change in its tree
clone-bd34260: HEAD bd342607acf0e6bad5fd08b8662b0a41e0f98145
/tmp/specfirst-clean-iARXrv/specfirst: HEAD 973084376618c487cd98902aa5cd8b8153ea8983, no change in its tree
lines 49 to 453 of docs/reports/real-3a.clean-clone.gate.log == its build/gates/real-3a/gate.log (written 12:02:04)
/tmp/specfirst-clean-iARXrv/env: cache, r-lib (99 packages), venv-specfirst-21289105
P1 hash lines: first run 30, clean clone 30, equal: True
P1 of the gate of real-2 at bd34260: 26 files; with the same hash in real-3a: 23; differing: the three graph files
```

So the clean-clone gate ran as the report says, on a clone of `9730843`
with an environment of its own; the reviewer did not run it again (it
needs the network). The clean clone was read at 12:07. It is gone since:
after 12:29, when no run of any session was left, the Ubuntu instance was
found newly started at each of the reviewer's commands, and `/tmp` empty.
So this comparison cannot be made again. The report's quotes:

```text
block at line 139 (The gate of real-2 again) against real-3a.real-2.gate.log: 28 quoted lines found in order, 0 not found
block at line 323 (The gate) against real-3a.gate.log: 183 quoted lines found in order, 0 not found, 0 places where lines are left out without [...]
block at line 557 (The clean-clone gate) against real-3a.clean-clone.gate.log: 52 quoted lines found in order, 0 not found
block at line 113 (The first commit): lines of real-3a.gate.log: [321, 322, 323, 324, 325, 326, 327]
block at line 126 (The first commit): lines of real-3a.gate.log: [86, 87, 88]
```

What `[...]` leaves out in the long quote is what the report lists, and in
one place more: 16 lines of check 11 (F9).

#### R3 The reviewer's recount

A script of the reviewer (Python's standard library, nothing of specfirst)
reads the grid, the shell, the two pages, the two ARD files and the pinned
example of a build. It finds the embedded result of an ARD row by the
row's analysis, operation and groups, and formats our values by its own
reading of a pattern.

```text
embedded results: 3735 with a formattedValue: 3734
rows: 9 columns: 3 cells: 27 results shown: 51 distinct: 51 cells that print a digit: 27
cells whose text is the example's formatted values joined by one blank: 27; differ: 0
cells whose text is the reviewer's own formatting of the ARD values: 27
results whose R value gives the same text: 51 of 51
   ('Mth01_CatVar_Count_ByGrp_1_n', '(N=XX)', True) 3
   ('Mth01_CatVar_Summ_ByGrp_1_n', 'XXX', True) 24
   ('Mth01_CatVar_Summ_ByGrp_2_pct', '( XX.X)', True) 24
results of the grid that lie on a half at their displayed decimals: 0
every result of a cell is of the group of its column: True
results the example formats for these analyses: 51 | shown by a cell: 51 | shown and not of these: 0
order of the analyses in the rows equals the order of the list: True
titles equal: True | footnotes equal: True | header of the row labels: True
shell: same columns, titles, footnotes, rows: True | same labels: True | same ARD rows per cell: True | texts: {'(N=xx)': 3, 'xxx ( xx.x)': 24}
page Out14-3-1-1.html: 4186 characters; cells equal the grid: True (27); row labels equal: True; column labels: True; outside references: []; dates: []; paths: []
page Out14-3-1-1.shell.html: 4228 characters; cells equal the grid: True (27); row labels equal: True; column labels: True; outside references: []; dates: []; paths: []
```

Every row shows results of one analysis, and its label is the label of
that analysis in the ARS file. The columns are the three groups of
`AnlsGrouping_01_Trt` in their order, under their names. The display of the
example also has a Header and a Footer section (the name of the study, a
page count, a line on the source and one on the program, each with a place
for the time of the run); the grid leaves both out, and schema version 0
has no place for them.

#### R4 Planted defects of the display

Judged by `build.display_problems`, the function `specfirst check` and the
gate call, and by what `gates._grids` asks of the counts (27 cells, 51
results, none without a formatted value, every cell equal or classified).
A layout is planted as a build would leave it: the grid, the shell and the
two pages are made from the planted layout.

| Planted | `display_problems` | The check of the gate |
| --- | --- | --- |
| the labels of the low and the high dose column exchanged (`columns.labels`) | 0 | passes |
| the labels of the first two rows exchanged | 0 | passes |
| another title, and no footnote | 0 | passes |
| the header of the row labels changed | 0 | passes |
| the percent of the first row in the second row, and the other way round | 0 | passes |
| the percent before the count; no blank between them; the header as `N={N}` | 0 | passes |
| the count under the pattern `XX` (the same texts, another shell) | 0 | passes |
| the body rows indented by 3, in a section `Deaths` | 0 | passes |
| a row of another output added (age: n and mean) | 0 | fails: 30 cells, 57 results |
| the first row again, in a second block | 0 | fails: 30 cells, 57 results |
| a text with a number in every cell (`{n} {pct} of 86`) | 24 (the shell shows a number) | fails |
| the header count in place of the count of every row | 48 | fails |
| the header after the body | 1 (the order of the analyses) | fails |
| the first row twice in a block; the section `@header` for body rows | the layout is refused | - |
| results: a count one higher; the header count one higher; a percent without a value | 1 each | fails |
| results: a percent changed below its displayed decimal (75.58 to 75.60) | 0 | passes (check 11 sees it) |
| results: the R engine alone has a count one higher | 1 | fails |
| results: a result of the grid is not in the ARD | the build stops | - |
| grid file: the header row without its section; an indent; a spanner; two column labels exchanged; a footnote changed; the ARD rows of a cell in the other order | 1 to 4 each | fails |
| shell file: a mask replaced; a row label changed | 2 each | fails |
| page: a cell text changed; a cell that is not of the grid; a script | 1 or 2 each | fails |
| page: two cells of a row exchanged, each with its attribute; two rows exchanged; the header row moved into the body | 0 | passes |
| page: a number in the `title` element; a comment with a date; a style rule that prints text after every cell, or hides a column | 0 | passes |
| page: an `onload` handler that fetches; a style that imports from another address; a `meta` refresh to another address | 0 | passes |

A file of a build that is changed after the build is stopped earlier, by
the hashes of `build.json`; the lines on files say what the checks would
see of a builder or a renderer that wrote such a file. Findings F3 and F6.

#### R5 The trace

A script of the reviewer (standard library only) reads `nodes.jsonl`,
`edges.jsonl`, `coverage.json`, the grid, the ARD file and the example. It
works out again, from the ARS file, what every analysis behind the grid
reads and which analyses a result is computed from.

```text
nodes 892 {'L0': 279, 'L3': 111, 'L4': 415, 'L5': 9, 'L6': 51, 'L7': 27}
edges 4153 {'cites': 706, 'computes': 75, 'derives_from': 3269, 'reads': 52, 'shows': 51}
edges with an end that is no node: 0
cells 27; complete by the reviewer's walk: 27; problems: 0
through 51 ARD rows, 9 analyses, 9 ADaM columns read directly, 15 ADaM columns in all, to 15 SDTM columns
SDTM columns per cell: {8: 3, 11: 3, 12: 15, 13: 6}
```

"Problems: 0" includes: every `shows` list is the `ard` list of its cell;
every result node cites its own line of the ARD file; the `computes` edges
of every result are its own analysis and, for a percent, the analysis of
its denominator; every analysis node cites the line of its `id` in the ARS
file; the `reads` edges of every analysis are the columns the reviewer
reads from the ARS file (variable, set, subset, grouping, and the subject
key of both datasets). The walk of `cell:Out14-3-1-1/r2/c1` printed by the
same script names what the walk of the report names: lines 150 and 153 of
the ARD file, lines 4482 and 1823 of the ARS file, the same eight `reads`
edges with their roles, the same five ADaM columns with their lines, and
the same SDTM columns behind each.

Planted gaps, on the graph of the build with something left out. Static:
`graph.check_cells` and `graph.check_graph`. D8: the two tests of
`tests/defects`, `shows_problems` and `reads_problems`, called with the
changed edges.

| Left out | `check_cells` | `check_graph` | D8 shows | D8 reads |
| --- | --- | --- | --- | --- |
| nothing | 0 | 0 | 0 | 0 |
| `reads` An07_01 to ADAE.TRTEMFL (the case D8 plants) | 0 | 0 | 0 | 2 |
| `reads` An07_01 to ADAE.USUBJID | 0 | 0 | 0 | 2 |
| `reads` An07_01 to ADSL.SAFFL | 0 | 0 | 0 | 0 |
| `reads` An07_01 to ADSL.TRT01A | 0 | 0 | 0 | 0 |
| `reads` An07_01 to ADSL.USUBJID | 0 | 0 | 0 | 0 |
| `reads` An01_05 to ADSL.SAFFL | 0 | 0 | 0 | 1 |
| `reads` to ADSL.SAFFL of all 9 analyses | 1 | 0 | 0 | 9 |
| `reads` An07_03 to ADAE.AESER turned to ADAE.AEREL | 0 | 0 | 0 | 2 |
| `computes` of one percent to the analysis of its denominator | 0 | 0 | 0 | 0 |
| `computes` of the three percents of An07_01 to that analysis | 0 | 0 | 0 | 2 |
| `computes` of all 24 percents to that analysis | 0 | 0 | 0 | 16 |
| `computes` of one count to its own analysis | 2 | 0 | 0 | 0 |
| `shows` to one percent | 2 | 0 | 2 | 0 |
| the node of a cell, of an analysis, of ADAE.TRTEMFL, of ADAE.ASTDT | 2 to 25 | 2 to 23 | - | - |
| the `derives_from` edges of ADAE.TRTEMFL | 1 | 15 | - | - |
| every `derives_from` edge of the 9 columns the analyses read | 52 | 236 | - | - |
| `coverage.json`: 14 SDTM columns; a column that is not built | 1; 4 | 0 | - | - |
| `coverage.json`: An07_01 reads one column only (the edges unchanged) | 0 | 0 | - | - |

Finding F4.

#### R6 P1 beyond the gate

```text
b1: cd <clone> && specfirst build cdiscpilot01 --into <scratch>/b1
b2: cd / && TZ=Asia/Tokyo PYTHONHASHSEED=12345 LC_ALL=C LANG=C specfirst build cdiscpilot01 --into <scratch>/b2-with-a-longer-name/and/depth
b3: cd <scratch> && umask 077 && TZ=America/St_Johns PYTHONHASHSEED=987 LC_ALL=C.UTF-8 LANG=C.UTF-8 COLUMNS=40 specfirst build cdiscpilot01 --into "<scratch>/b3 with a blank"
b1: 30 files; every file has the hash build.json gives: True; equal to the author's hashes: 30 of 30
depth: 30 files; build.json equal to the first: True; every file has the hash build.json gives: True; equal to the author's hashes: 30 of 30
b3 with a blank: 30 files; build.json equal to the first: True; every file has the hash build.json gives: True; equal to the author's hashes: 30 of 30
   gold/graph/coverage.json        9089c86643646467
   gold/graph/edges.jsonl          9963981263e837e6
   gold/graph/nodes.jsonl          c5b9582b6f2f3870
   gold/grid/Out14-3-1-1.json      978c9e2977e3f5fc
   gold/grid/Out14-3-1-1.shell.json 2ac2586e11fbb636
   gold/out/Out14-3-1-1.html       e9db6ca3f5d7ce63
   gold/out/Out14-3-1-1.shell.html 41c207f1d512d596
files in the built folders that build.json does not list: []
nodes sorted by id: True | edges sorted by type, from, to: True
grid, shell and coverage.json are sorted, compact JSON with one final line feed: True
```

The first build of the reviewer's gate run and the copy of the author's
first build have the same 30 hashes. None of the seven new files holds a
folder of a build, a date or a time. The three result files
(`76c528ce523c6a13`, `de20ea90cae0946d`, `a3d51da218b6839e`) are those the
review of real-2 recorded: the fixes of F2 to F12 changed no result.

#### R7 The proofs

On the kit's own entries, judged by `results.judge_entries` with
`build.proof_evidence`:

```text
control: 3735 embedded, 3711 reproduced, open 25, explained 25, problems 0
kinds: {'no_alternative': 1, 'value_of_other_result': 22, 'between_equal_values': 1, 'no_records': 1}
(2) value_of_other_result: every one of our rows tried as the named result
   entries by the number of results their proof accepts: {1: 22}
(3) every entry with every other kind of proof
   counts of 0 among our rows: 376
   no_records: single counts of 0 that pass: 0; with the first right count, another second: 0; with the second right count, another first: 0; three counts (the two and one more): False; the same count twice: False
   proofs tried: 2178; accepted other than the committed kind and class: 0
   cell_values: median n 84 sorted 39th to 45th: [161.3, 161.8, 162.6, 162.6, 162.6, 162.6, 162.6]
```

"Every other kind" is: `between_equal_values`; `same_under_every`,
`no_alternative` and `alternative` with every option and value of the
registry; each with every class. So on the 25 entries nothing passes but
what is committed, an exchange is proven by exactly one of our 4,238 rows,
and the median of height is proven on the data: the 41st to the 43rd of
the 84 sorted values are 162.6. In the cell of that median the n, the sd,
both quartiles, the minimum and the maximum are reproduced; its mean is one
of the 22 exchanged values.

With a defect of our own planted (a copy of the build in which one
analysis reads its set from EFFFL; the embedded results unchanged; the
evidence made from the changed file):

```text
An08_01_Obs_Summ_ByTrt with the set read from EFFFL: 218 new differences {'n': 56, 'Mean': 56, 'SD': 56, 'Median': 12, 'Q1': 11, 'Q3': 22, 'Min': 1, 'Max': 4}; accepted as reference_error: {('between_equal_values', 'Median'): 7, ('between_equal_values', 'Q1'): 4, ('same_under_every', 'Q1'): 9, ('same_under_every', 'Q3'): 11, ('between_equal_values', 'Q3'): 5}
      for example .../Mth02_ContVar_Summ_ByGrp_4_Median/AnlsGrouping_01_Trt_1/AnlsGrouping_08_Param_1/AnlsGrouping_09_Visit_01 embedded 137 ours 136.0 between_equal_values
An03_01_Age_Summ_ByTrt with the set read from EFFFL: 14 new differences; accepted as reference_error: {('between_equal_values', 'Median'): 1, ('same_under_every', 'Q3'): 2}
An03_06_Height_Summ_ByTrt with the set read from EFFFL: 12 new differences; accepted as reference_error: {('between_equal_values', 'Q1'): 1, ('same_under_every', 'Q1'): 1}
```

`no_alternative` accepts none of them. Finding F5.

The bound of `between_equal_values` (the values `x[low]` to `x[high]` that
must all be our value), against the nine definitions of Hyndman and Fan as
the reviewer reads them, and against R's `quantile` types 1 to 9:

```text
n = 1 to 400, p = 1/4, 1/2, 3/4, nine definitions: 10800 quantiles; outside the values x[low] to x[high] of the check: 0
how many values the check asks for beyond what some definition uses (below, above): {(0, 0): 404, (0, 1): 200, (1, 0): 399, (1, 1): 197}
n = 84, the median: the check asks for the sorted values 41 to 43; the nine definitions use [41, 42, 43]
60 samples, R's quantile types 1 to 9: largest difference from the reviewer's reading 6.4e-14; R quantiles outside x[low] to x[high]: 0 of 1620
```

The bound is right for p = 1/4, 1/2 and 3/4. Where it is not tight it asks
for one value more, which refuses a proof and never grants one.

The count of the exceptions file for the first quartile of age (finding F9
of real-2), made again from the cell values of the engine and the
reviewer's arithmetic: 69 quartiles and medians where n p is whole and the
two neighbours differ; the reference has the average in 68, the lower value
alone in 1, neither in 0. As the entry says.

#### R8 The Fisher test

420 tables of the reviewer: the six of finding F3 of real-2, 18 with
margins of zero or with ties, and 396 random ones with 2 to 5 rows, 2 to 6
columns and 4 to 34 subjects. Of the 356 that were summed, 151 have a row
or a column of zeros as given. The sum in exact fractions is the
reviewer's own (not `oracle.py`).

```text
tables: 420; too many tables for the fractions: 11; without two rows and two columns after the zero margins are left out: 53; summed: 356
shapes after reduction: {(2, 2): 19, (2, 3): 41, (2, 4): 39, (2, 5): 23, (2, 6): 11, (3, 2): 46, (3, 3): 42, (3, 4): 23, (3, 5): 12, (4, 2): 30, (4, 3): 26, (4, 4): 10, (5, 2): 18, (5, 3): 16}
degenerate tables: Python None for all 53, R None for all 53
largest relative difference: {'python-exact': '2.1e-13', 'r-exact': '6.2e-14', 'python-r': '2.0e-13', 'fisher.test-exact': '2.9e-14'}
tables on which fisher.test differs from the exact sum by more than 1e-9: 6
    [[0, 6, 20], [8, 27, 40]] exact 0.06040878692449789 fisher.test 0.06533690837383269 Python 0.06040878692449231 R 0.060408786924501114
    [[4, 8, 30], [0, 6, 56]] exact 0.00979884680687777 fisher.test 0.011455024125087577 Python 0.009798846806875698 R 0.009798846806877703
    [[4, 9, 30], [0, 5, 56]] exact 0.0028204363374983482 fisher.test 0.0035861957426922 Python 0.002820436337498024 R 0.0028204363374982697
    [[27, 15, 6], [0, 15, 41]] exact 1.2195957080825592e-14 fisher.test 1.3623367277605544e-14 Python 1.2195957080824101e-14 R 1.2195957080824997e-14
    [[1, 6, 20], [10, 28, 40]] exact 0.12824554631222063 fisher.test 0.13531681960680528 Python 0.1282455463122018 R 0.12824554631221344
    [[5, 0, 40], [10, 27, 20]] exact 5.724148010367469e-10 fisher.test 6.358880701965926e-10 Python 5.724148010367068e-10 R 5.724148010367792e-10
```

The six are the tables of the review of real-2: there both registry
implementations now give the exact sum and `fisher.test` does not, as
statement 8 says. The R sum is read as correct for any number of rows and
columns: the last free cell is taken for all its values at once, and the
count of tables is the count the Python sum makes, so both refuse the same
tables. Large tables:

```text
3 x 3 of 254 [[20, 40, 26], [25, 35, 24], [22, 38, 24]]: Python 0.9170897792546375 (2.4 s)
   R 0.9170897792550804 (1.0 s)
   relative difference Python against R: 4.8e-13
   fisher.test 0.9170897792574392 (0.1 s)
3 x 4 of 143 [[12, 12, 12, 12], [12, 12, 12, 12], [11, 12, 12, 12]]: Python refused: test.fisher.exact: more than 10000000 tables to sum; the method does not approximate (4.6 s)
   R refused: the R vectors run exited 1: Error: test.fisher.exact: more than 10000000 tables to sum; the method does not approximate (5.1 s)
4 x 4 of 97 [[9, 3, 4, 8], [2, 11, 6, 5], [7, 5, 12, 3], [4, 6, 2, 10]]: Python refused: [the same] (5.2 s)
   R refused: [the same] (11.6 s)
```

Statement 6 now holds in both implementations. A 4 x 4 table of 97
subjects is already beyond the limit of 10,000,000 tables.

#### R9 Both engines at the edges

```text
rule I9: 770 numbers as group values; Python rows, R rows
  groups: Python 769, R 769; only in Python 0, only in R 0; disagreements 0
  texts that are not what rule I9 says: 0
  the group 0 holds 2 subjects (0.0 and -0.0)
  a group variable that holds inf: Python rows [..., 'ard:A_BY/M_N_n/=inf']; R: ValueError before R is started: Out of range float values are not JSON compliant: inf
hand-over: 60 distinct texts as group values, one missing, one empty, 'NA' three times; Python rows, R rows
  groups: Python 60, R 60; same keys True; disagreements 0; the group NA holds 3 subjects
  a text with U+0000: R data ['column ADSL.SEX: the R engine read other values']
hand-over: 18 numbers in a column that is summarised: Python rows, R rows; disagreements []
rule I3: 56 texts compared with a number column (EQ, GE and NE each)
  taken as a number by Python: ['61', '-0', '0', '6.1e1', '61.0', '1E0', '1e+2', '1e-2', '-0.5', '0.5', '0.0e0', '-0.0', '1e-400', '4.9e-324', '9007199254740993', '0.1', '0e0', '1e05', '-1E-05', '100000000000000000000000', '0.1e1']
  taken as a number by R:      the same 21
  a condition value that is a JSON number: ["data subset 'C': a condition has a value that is not text"]
135 cells of 2 to 10 equal values: Python sd not 0: 0; R sd not 0: 0
```

The 770 numbers are 48 chosen ones (1e15 to 1e100, the smallest and the
largest doubles, values at 0.0001), 25 powers of 2 and of 3, 400 random
ones of 1e-14 to 1e20 and 300 doubles of random bits, each number once,
and -0.0 next to 0.0. The 60 texts hold "NA",
"NaN", "NULL", "true", numbers as text, every control character the
review of real-2 named, a quotation mark, a backslash and letters outside
ASCII and outside the BMP. The 35 other texts of rule I3 ("61.", ".5",
"+61", "0x3D", "6_1", "nan", "Infinity", " 61", "061", "1e999", "1d2",
"1L" and so on) are refused by both engines. Finding F8.

#### R10 display.pattern

```text
40 cases worked out by hand from the seven statements; other than expected: 0
patterns without exactly one mask ('', 'xx.x', 'XX.X.X', 'XX,X', 'XX XX', 'N=XX (XX.X%)', 'MAX XX', None, 5, 'X X', '(XX) [XX]', '--'): refused, all 12
values that are no plain number: None gives None; True, '12', nan, inf, a Decimal, a Fraction: refused
16 decimals: refused: decimals must be a whole number from 0 to 15, not 16
mock: ['( xx.x)', '(N=xx)', 'x.xxxx', 'xx %']
statement 3: registry.json is not the text of the entry:
   entry:         '9.52 under "( XX.X)" is "(  9.5)". '
   registry.json: '9.52 under "( XX.X)" is "( 9.5)". '
statements 7, vectors 18; statements cited by a vector: [1, 2, 3, 4, 5, 6, 7]
```

Among the 40: -0.0 is " 0.0" under `XX.X` and "0" under `XX`; -0.05 is
"- 0.1" and -0.04 is " 0.0"; 1e22 is written out under `XX.X` and under
`XX`; 5e-324 is "0.0000"; 99.95 is "100.0" and -9.95 is "-10.0" (longer
than the mask, not cut); 0.5, 1.5, 2.5 and -2.5 go away from zero; 2.675 is
"2.68"; a count of 1234 under `(N=XX)` is "(N=1234)". Finding F7.

#### R11 The made-up study

31 layouts and data sets of the reviewer on the study of
`tests/toy_displays.py`, each built, checked as a grid, rendered and read
back. As worked out by hand: the control; a data-driven column grouping
without and with listed values (order and labels as listed; no shell
without the list); values that need encoding ("%41", "A B", "C/D", a
letter outside ASCII); defined groups with the orders 3, 1, 2; a cell with
the count of another analysis (`{n}/{N} {pct}`); braces in a template and a
text for a missing value; a header after the body and a second header (the
page shows both in the table header); no header; an analysis in two
blocks; labels and titles with markup, blanks and a letter outside ASCII
(the page escapes them and reads back). Refused, each with a message that
names the place: an analysis with two groupings, a test, an operation of
another method, a part without a pattern, a pattern with two masks or in
lower case, a label for a group that is none, values for defined groups,
an output that is not in the event, parts that the template does not name
or names twice, a format or an attribute in a template, an unknown key,
`layout: 1`. What stops the build where it should not:

```text
data-driven arms, listed as A, B, C; no subject is in arm C: stops: GridError: 5 results of the layout are not in the ARD, for example ard:A_AE/M_CAT_n/=C
data-driven arms; arm B has no treatment-emergent event (no list of values): stops: GridError: 2 results of the layout are not in the ARD, for example ard:A_TEAE/M_CAT_n/=B
data-driven arms; arm B has no treatment-emergent event (values A, B listed): stops: GridError: 2 results of the layout are not in the ARD, for example ard:A_TEAE/M_CAT_n/=B
the same data with the arms as defined groups: texts [['(N=4)', '(N=3)', '(N=0)'], ['2 ( 50.0)', '2 ( 66.7)', '0 '], ['2 ( 50.0)', '0 (  0.0)', '0 ']]
```

Finding F2.

#### R12 ADR-003

`bash evidence/adr003_rounding.sh <scratch>/b1 <scratch>/adr003` wrote the
same bytes as `evidence/adr003_rounding.out` (2537 of 4238; 3 on a half; 2
that R's `round` shows otherwise; the example has ours for both).

The counts on the formatted values, by a script of the reviewer that
formats our ARD values by its own reading of a pattern:

```text
embedded 3735, with a formatted value 3734; our rows 4238; outputs 5, analyses 31
    '( XX.X)': '(  9.9)' 767, '( 99.9)' 61
    '(N=XX)': '(N=99)' 3
    '(XX.XX)': '(99.99)' 142, '( 9.99)' 116
    'X.XXXX': '9.9999' 10, '9' 1
    'XX': '99' 320, '999' 233, '-99' 90, '99.99' 62, '-9.99' 27, '9.99' 27, '999.9' 6, '99.9' 3, '9' 3, '-9' 3
    'XX.X': '99.9' 414, ' 9.9' 225, '- 9.9' 199, '999.9' 144, '-99.9' 50
    'XXX': '9' 775, '99' 53
our value under the pattern is the example's text: 3580; differs and the result is classified: 24; differs by display only: 130
    display only, by operation and pattern: {('Minimum', 'XX'): 62, ('Maximum', 'XX'): 63, ('P-value', 'X.XXXX'): 1, ('Median', 'XX.X'): 4}
```

This is the table of the ADR, shape by shape, and the 3,580, 24 and 130 of
the ADR and of the state file.

The shell. The example names one reference document for this output:

```text
$ git -C <cache>/ars rev-parse HEAD
2c9b4b68724386e8f91dc576724855af7fafac65
$ git -C <cache>/ars ls-files | grep -i shell
workfiles/examples/ARS v1/AE_SOC_PT_Table_Shell.rtf
workfiles/examples/ARS v1/AE_Summary_Table_Shell.pdf
workfiles/examples/ARS v1/Demog_Table_Shell.rtf
workfiles/examples/ARS v1/Vitals_Obs_ChgBaseline_Table_Shell.pdf
workfiles/examples/ARS v1/Vitals_Obs_ChgBaseline_Table_Shell_vertical.pdf
[9 more, in the folders Hackathon and PHUSE Connect Workshop]
referenceDocuments of the example, each with whether its location is a file in the folder of the example:
  CDISCPILOT01_SAP ./sap.pdf True
  CDISCPILOT01_CSR ./csr-cdiscpilot01.pdf True
  at14-5-01_sas ./at14-5-01.sas True
  AE_Summary_Table_Shell ./AE_Summary_Table_Shell.pdf True
Out14-3-1-1 documentRefs: ['AE_Summary_Table_Shell']
sha256 7c744c2d93c981244aa1414fdff9575d6eea34329a40b5a180de44f473e80a63  workfiles/examples/ARS v1/AE_Summary_Table_Shell.pdf
```

Finding F1 says what the shell shows.

#### R13 Clean room and scope

```text
git diff --name-only f42a3fa..f55f40d -- PLAN.md standard/schemas env .github scripts Makefile pyproject.toml   -> nothing
PLAN.md sha256 234a642af58fba20d4ab608a76952b43b9a67b6ff1895d1eec315dce37072e4c
CLAUDE.md: 59 lines; tracked files: 391; the diff: 44 files changed, 16 added
R files in the cache: 827; distinct code lines of more than 30 characters: 25190
  r/specfirstr/R/engine.R: 249 lines, shared 0      r/specfirstr/R/methods.R: 52 lines, shared 0
  r/specfirstr/R/vectors.R: 31 lines, shared 0      r/specfirstr/run.R: 12 lines, shared 1 (commandArgs)
  r/specfirstr/R/util.R: 41 lines, shared 2 (the definition of %||%; the line of json_scalar that writes true or false)
  util.R still escapes with gsub: False
added lines of the diff: 6737
embedded raw values with 9 or more digits: 539 distinct; found in added lines: 2 (in the three gate logs: the two results "at the edge")
added lines with something like a subject number of the pilot: 0
files whose added lines name tfrmt: ADR-003.md 20, real-3a.md 8, real.md 1, evidence/README.md 1, adr003_rounding.sh 6
env/r-packages.lock: 99 lines; gt: False; forcats: False; tfrmt: False
<author's scratch>/tfrmt-lib: empty
```

The 16 added files: 6 Python, 2 Markdown, 3 logs, 2 YAML, 1 JSON, 1 shell
script and its recorded output. No file is added outside the folders of
the track. The names of tfrmt's functions stand in ADR-003 and in the
comment of the evidence script only; no code file of the diff names one.

#### R14 f55f40d

```text
$ git diff --stat 9730843 f55f40d
 2 files changed, 583 insertions(+), 26 deletions(-)    (docs/reports/real-3a.clean-clone.gate.log, docs/reports/real-3a.md)
$ git diff --name-only 0938fe4 f55f40d
docs/reports/real-3a.clean-clone.gate.log  docs/reports/real-3a.gate.log  docs/reports/real-3a.md  docs/reports/real-3a.real-2.gate.log
ASCII check: 391 files checked, 0 with non-ASCII bytes     (a clone of f55f40d)
```

## Findings

### F1 (not blocking; to correct before the merge) The example's shell is in the pinned repository

ADR-003, decision 5: "The shell the example names
(`AE_Summary_Table_Shell.pdf`) is not in its repository." The report says
the same under "What the checks do not cover", and both conclude that which
results share a cell, in which order and with what text between them "is
the layout's alone". The context of the ADR says of the example: "It does
not say which analysis is which row, which results share a cell". The
state file: "no check can hold it against this reference". Lesson 29 and
the lines of D7 that begin "not separable by this reference" rest on it.

The file is in the pinned repository, at the pinned commit, in the folder
of the example, where the example's own `location` points (R12). All four
reference documents of the example are there. As text (poppler 24.02), the
shell of the output shows, in the reviewer's words:

- the three columns under the names of the three arms, each with the mask
  `(N=XX)` below it, and the header of the row labels on that line;
- eight rows with the eight labels of the grid, each cell with the mask
  `XX ( XX.X)`: the count, one blank, the percent in brackets;
- above the eight rows, one line that has no cells, "Number of subjects
  with at least one event", and the eight rows indented under it;
- the titles and the two footnotes of the grid, and the header and footer
  lines of the page.

So the reference does hold what a cell looks like. Held against it:

- The cell of the layout is right: count, blank, percent, in this order.
  The three cases that pass the comparison (the percent before the count,
  another text between them, another header) are separable by this
  reference, and could be planted defects that are caught.
- The grid lacks one line of the row axis. The same text is in the ARS file
  the builder reads: it is the name of the item of the list of contents
  above the eight analyses (level 2, the analyses are level 3).
  `ars.listed_analyses` walks that list and drops the names. Layout spec v0
  has `section` and `indent` for a block; the layout of the kit uses
  neither, and the page would not print a section name if it did.
- The mask of the count differs: `XX` in the shell, `XXX` in the
  `resultPattern` of the operation, which the mock shell follows ("xxx
  ( xx.x)"). That is a difference inside the example; the mock shell of
  the build should say which of the two it follows.

Nothing of this makes a statement of the gate text false: the 27 cell texts
are the example's formatted values, in the order and with the blank the
shell shows. But a sentence the owner is asked to accept (point 5 of the
ADR's list for the owner) is wrong, a limit of the main new check is
explained by it, and the first grid of the project differs from the
example's own shell in a way no file records. Four more shells stand in
the same folder, by their names those of the other four outputs; the
reviewer did not open them. The rest of real-3 needs them.

Fix: correct the sentences in ADR-003 (context, decision 5, point 5 for
the owner), in the report, in the state file and in lesson 29. Pin the
shell in `kit.yaml` (source `ars`, the path and hash of R12). Hold the mock
shell of the build against its text, as the CSR parser of real-4 will have
to do anyway: the row labels in order, the mask of every cell, the masks
under the column labels. Then plant "the percent before the count" again;
it must fail. Give the line above the eight rows a place in the layout or
record it as an open difference, and settle the mask of the count.

### F2 (not blocking; for gen-2a and the owner) Data-driven columns: an arm without a record stops the build

Rule I9 gives a data-driven grouping one group per value that occurs on
the analysis records. An arm that has subjects and no record of the
analysis has no group there, so the ARD has no row for it: rule I11 gives
a count of 0 to a cell that exists, and by rule I10 a value that does not
occur makes no cell. `grid.fill` raises `GridError` for a planned result
that is not in the ARD. Together (R11): on the made-up study with the arms
data-driven, and arm B without a treatment-emergent event, the build
stops, with or without `columns.values`. With defined groups the same data
give "0 (  0.0)". An arm that the layout lists and that has no subject
stops the build too.

On the pilot the treatment grouping has defined groups, so the gate does
not meet this. A compiled study has a data-driven treatment grouping (the
state file says so, and that "the compiled adverse event summary fits"
the builder). An adverse event summary has rows such as "leading to
death" that are empty in some arm of most studies: the first generated kit
with such a row will not build. `tests/unit/test_grid.py` holds the case
"a value the layout lists and the results do not have" as an error and has
no case of an arm with subjects and no record. Neither the ADR, the report
nor the state file names the limit; the report calls the code general,
"limited by a list of outputs".

Fix: decide what a cell shows when the ARD has no row for a column the
grid has: a rule of the layout (a count of 0, a percent of 0 by the
denominator that exists, or the text for a missing value), or a rule of
the engine that gives every listed value of a data-driven grouping a
result. It is a decision about numbers on a display, so it needs a
statement, a planted defect and a line in ADR-003; and gen-2a must know it
before it builds.

### F3 (not blocking) The comparison passes a cell that pairs results of two rows

`grid.compare_reference` builds the expected text of a cell from the
layout's own template and the formatted values of the results the layout
puts there. So it cannot see a wrong choice of results as long as every
result of the output is shown somewhere and the analyses first appear in
the order of the list. A part of an `analyses` block may name another
analysis than that of its row (R4):

```text
the percent of the first row in the second and the other way round: display_problems 0; cells 27, results 51, equal 27; the check of the gate passes: True
```

The grid then shows the count of "TEAE" with the percent of "Related TEAE"
in one cell, and the gate passes. The report's list covers this in
general words ("which results share a cell"), and D7 plants only the
harmless case, the percent before the count. But this case the reference
can show without any shell: it lists every result under its analysis, and
the label of the row is the label of that analysis.

Also passing, and not in the report's list of what the checks do not
cover: another title and no footnote (`titles`, `footnotes`); a section
and an indent for the body rows. In `specfirst check`, outside the gate: a
row of another output, and the same analysis again in a second block (a
block refuses a repeated analysis; two blocks do not). The gate stops
these two only by its constants (27 cells, 51 results).

Fix: in a body row, ask that every result is of the row's analysis or of
an analysis it is computed from, or refuse `analysis` in a part of an
`analyses` block until a display needs it; plant the crossed percent in
D7. Name titles, footnotes, sections and indents in the list of what
nothing holds against the reference, or hold them against the shell (F1).
Refuse an analysis that stands in two blocks, or say that it may.

### F4 (not blocking) A single reads or computes edge can be left out unseen

`graph.check_cells` asks every result for a `computes` edge to its own
analysis and every analysis for some `reads` edge that reaches SDTM. It
does not ask for the edge of a percent to the analysis of its
denominator, and not for every `reads` edge. The report says so of the
static walk and names D8 as the test of the edges against the engine.

D8's `reads_problems` runs an analysis together with the analyses its
results are computed from, and empties the columns that none of them
reads. So a `reads` edge of an analysis is not tested when the analysis of
its denominator reads the same column. For An07_01 that is three of its
five edges (R5: ADSL.SAFFL, ADSL.TRT01A, ADSL.USUBJID left out one at a
time: 0 problems everywhere). By the construction of the test the same
holds for the other seven analyses of the body, 24 of the 52 `reads` edges
in all; the reviewer ran An07_01 only. A `computes` edge of one percent to
the analysis of its denominator is seen by nothing either; D8 notices only
when all three percents of an analysis have lost it, because the engine
then cannot run. The roles in `coverage.json`, the only place that has
them, are held against nothing (an analysis with one of its five columns
passes).

For this grid no cell loses a column by it: every body cell shows a
percent, and the analysis of the denominator reads nothing the others do
not. The gate statement is about cells, and it holds (R5). But the report's
sentence "D8 tests, per analysis, the columns the other analyses read" says
more than the test does, and a display whose cells show a count alone, or
whose denominator reads another set, would not be covered.

Fix: in `check_cells`, give the walk the event, or record per result in
`coverage.json` which analyses it is computed from, and compare; hold the
`reads` list of `coverage.json` against the edges. In D8, test the results
that are computed from one analysis alone (the counts) with that analysis
alone, and plant one `reads` edge to ADSL.SAFFL and one `computes` edge of
a percent.

### F5 (not blocking) Two kinds of proof still hold when our own cell is wrong

The narrowing asked for by finding F2 of real-2 is done and holds on the
kit's entries (R7): an exchange is proven in both directions, by exactly
one result; an option must change the operation; `no_records` wants one
count of the cell's own groups per compared group. On the 25 entries no
other proof passes.

`between_equal_values` and `same_under_every` say: given the values of our
cell, no definition gives the embedded value. Neither asks whether our
cell holds the values the reference had. `no_alternative` does: the other
statistics of the cell must be reproduced. With one analysis of ours
reading a wrong population, 36 of its wrong quartiles and medians are
accepted as errors of the reference by the two kinds, and none by
`no_alternative` (R7). Vital signs and ages have many tied values, so such
cells are common.

The gate would still fail on that defect: the n, the mean and the sd of
the same cells have no proof (56 each). And the one committed entry of
this kind is sound: in the cell of the median of height the n, the sd,
both quartiles, the minimum and the maximum are reproduced. The hole is
that an entry of these two kinds can be written for a difference that is
ours.

Fix: let both kinds ask what `no_alternative` asks, in the form the entry
of the height can meet (its mean is itself exchanged): the n, the minimum
and the maximum of the same cell are reproduced. Plant the wrong
population in D6.

### F6 (not blocking) The check of a page does not see where a text stands

`render.projection_problems` collects the texts of a page by their
attributes and compares each with the grid. It passes a page in which two
cells of a row are exchanged together with their attributes, two rows are
exchanged, or the header row stands in the body (R4): the table then shows
a value under another column or label. It passes a number in the `title`
element, a comment with a date, and style rules that print text after
every cell or hide a column. Of the ways a page can reach outside it sees
elements (`script`, `link`, `img` and others) and the attributes `src` and
`href`; an `onload` handler, a style that imports from another address
and a `meta` refresh pass. The module says of the page: "without scripts,
without anything fetched from elsewhere and without a date".

The page of the build is right (R3) and is written by one deterministic
function; a page changed after the build is stopped by its hash. So this
is a check that is weaker than its words, on files no gate statement
names. It matters for the rest of real-3, whose gate asks that the viewer
opens with no network.

Fix: read the page back as a table (the cells of a row in the order of the
columns, the rows in the order of the grid, header rows in the header),
and refuse any attribute that begins with `on`, `style` content beyond
the fixed sheet, `meta` refresh, comments and text in `head`.

### F7 (not blocking) registry.json loses a blank in statement 3 of display.pattern

`registry.load` joins the words of a statement with single blanks. The
statement is about padding with blanks, and its example loses one: the
entry says that 9.52 under `( XX.X)` is `(  9.5)`, with two blanks;
`registry.json`, which is said to be the same content, says `( 9.5)` (R10).
The implementation and the vector have two blanks. The README says the
order and the text of a statement are part of the contract.

Fix: write the example so that it survives (a number that fills the mask,
or the count of characters in words), or do not join the words.

### F8 (not blocking) One sentence of rule I9 holds in R only

Since real-3a rule I9 ends: "A number that is not finite cannot be a group
value." The report says the rule is one in both engines. R's `number_text`
refuses such a number. Python's
`_number_text` writes it: a group variable that holds infinity gives the
row `ard:.../=inf` (R9). In a build nothing is silent: the hand-over to R
then fails, but with a `ValueError` of the JSON writer, which
`build.build` does not catch, so the build ends in a traceback and not in
"FAIL". For all 770 finite numbers the two engines write the same text.

Fix: refuse it in `ard._number_text` with an `EngineError`, and add the
case to the test of rule I9.

### F9 (not blocking) Small things in the texts

- `docs/state/real.md` at `f55f40d`: "It is not merged and has not passed
  its gate", "`specfirst gate real-3a` has not run to its end on any
  commit", "D7 [...] has not run since", and the report as something not
  done. All four are overtaken: the gate ran three times (R1, R2). The
  state file is what `specfirst status` prints.
- The two new Fisher vectors say of their expected value that it "is the
  sum in exact fractions (oracle.py)". It is the value of the Python
  implementation: 0.06040878692449231 where `oracle.py` gives
  0.06040878692449789, and 0.009798846806875698 where it gives
  0.00979884680687777. They differ by a relative 9.2e-14 and 2.1e-13,
  inside the 1e-12 of the test, so the test passes; the sentence, and the
  row of F3 in the report, say more.
- The report's list of what `[...]` leaves out of the long quote does not
  name the 16 lines it leaves out of check 11: the lines on the result that
  agrees only as printed and on the two results at the edge (for each
  engine), the four `explained` lines of the R engine, the line on the 504
  results the reference does not list and the line on the ARS file.
- The report: "through 51 ARD rows, 9 analyses and 15 ADaM columns". The
  analyses read 9 ADaM columns; the 15 are these and the 6 behind them on
  the way to SDTM. The gate prints the 15, so the number is right; "15
  ADaM columns the analyses read" would not be.
- ADR-003, on the padding: "a longer number is not cut" is shown by the
  example for `XX.X` (144 values of four digits) and for `XX`. Under
  `( XX.X)` no value of the example is longer than the mask, so the vector
  "( 100.0)" is the registry's choice, not the example's.
- `gates.REAL2_METHOD_TESTS` names four tests that must have run. The new
  test `fisher-limit`, which is the only test of statement 6 in R, is not
  among them: it must pass when it is there, and nothing notices when it
  is gone.
- `specfirst check` counts a cell whose result has no formatted value in
  the reference as not compared and passes; only the gate asks for none.
  The made-up study has two such cells. That is as written, and worth a
  line where the limits are listed.

## The ten questions

1. The gate. Each statement of the gate text is proven by a check that
   fails when it does not hold, in the sense the ADR gives the first one:
   a cell is its template filled with formatted values. Check 12 fails on
   a cell that differs without a class, on other outputs, on other counts
   than 27 and 51, on a result without a formatted value, on a grid, shell
   or page that is not what the layout and the ARD give, and when the rows
   of the R engine give another grid (R4; the unit test of the gate plants
   the counts). Check 10 fails on a cell without a complete path (R5).
   Check 8 compares 30 files of two builds. What check 12 does not prove
   is the composition of a cell, and the reason the documents give for
   that is wrong (F1, F3). Everything the gate of real-2 checks is checked
   again, by the same fifteen functions (a unit test asserts that they are
   the same objects), with the planted defects D1 to D5 still required.
   The reviewer's run gives the lines of the author's two logs (R1).
2. F2 to F12 of real-2. Each is fixed as the report says. F2: R7; the
   proofs are narrow, with the rest in F5. The bound of
   `between_equal_values` is right for p = 1/4, 1/2 and 3/4, and the proof
   of the median of height is right on the data (R7). The exchange is
   proven in both directions and by one result only. F3: the R sum is
   correct, agrees with the Python sum and with exact arithmetic on 356
   tables of the reviewer, among them tables with more than two rows and
   columns and with margins of zero (R8); `MethodError` is caught by the
   build. F4: 135 cells of equal values, sd 0 in both engines. F5: the
   hand-over reads "NA" and every control character rightly; rules I3 and
   I9 are one in both engines on every finite input the reviewer tried
   (R9), with F8 for the one sentence that is not. F6: test A6 asserts the
   31 counts, which sum to 4,238. F7: test A5 reads R files; the
   reviewer's own count of shared lines is 0, 0, 0, 1 and 2 (R13). F8 to
   F12: the texts are changed as said. No fix broke anything: the result
   files have the hashes of the review of real-2 (R6), and the gate of
   real-2 passed at `bd34260` (R2).
3. Layout, grid, shell, page. Correct on everything the reviewer built
   (R3, R11): the recount of the 27 cells agrees. General within the two
   kinds of block that version 0 has, with one limit that is not stated:
   F2. Against the example's own shell the grid lacks one line (F1).
4. P2 for grid text. A grid file, a shell file or a result that is wrong
   does not pass (R4). A layout that is wrong can pass: the report names
   labels and the order and the text between the parts of a cell; it does
   not name the pairing of results of two rows, titles, footnotes,
   sections and indents (F3). The list rests on the sentence that the
   shell is not in the repository, which is not so (F1). So the list is
   honest in what it says of the check and incomplete, and its reason is
   wrong.
5. The trace. The reviewer's walk agrees with the gate, cell by cell, and
   the `shows`, `computes` and `reads` edges are right (R5). A gap can
   pass `check_cells`: one `reads` edge among several, and the `computes`
   edge of a percent to the analysis of its denominator. The test of
   `shows` in D8 is a real test against the builder. The test of `reads`
   is a real test against the engine for a cell's analyses taken
   together, not for each analysis. `computes` has no test of its own
   (F4).
6. Determinism. Five builds in five folders, two of them under another
   time zone, hash seed and locale and from another working folder, one
   with a umask of 077 and a blank in its path: the same 30 hashes. No
   path, time or order dependence was found in the seven new files (R6).
7. `display.pattern`. The seven statements and the implementation agree on
   the 18 vectors and on 40 cases of the reviewer, among them negative
   zero, numbers longer than any mask, the smallest double, halves, and
   masks at their edges; a missing value gives none; what is no number or
   no pattern is refused (R10). `registry.json` has one example wrong (F7).
8. Clean room and scope. No study data and no study document is committed;
   the diff adds two embedded values of nine or more digits, both in gate
   logs. What is quoted from the example: the IDs of its analyses,
   operations and groups in the layout and the tests; and, in the report,
   the whole grid as text: its three titles, eight row labels, two
   footnotes and the 27 cell texts, which are our results and equal the
   example's formatted values. That is more of one output than any earlier
   report holds; the repository is private and the example's repository is
   MIT, so the reviewer lists it for the owner and does not count it
   against rule 4. Nothing of tfrmt is copied as far as the repository
   can show (R13); its source could not be read. `PLAN.md`,
   `standard/schemas/` and `env/` are unchanged. Nothing of the rest of
   real-3 is started (no viewer, no citations, one output). The edits of
   the shared files are small: one gate, two constants and two functions
   in `gates.py`, three texts in `cli.py`, two lines of `CLAUDE.md` (59
   lines), four rows of `docs/lessons.md`.
9. ADR-003. Decision 1 follows from what the ADR says it read, and it says
   plainly that tfrmt was read and not run; the one claim that was run
   (T1) gives the recorded output again (R12). Sentences that say more
   than the evidence: every row of the table "tfrmt, read" (nothing in
   the repository or the cache can show it; the reviewer has no network);
   "that changes 2 of the 3 results" as a statement about tfrmt (T1 runs
   the expression of base R; that tfrmt applies it, and to a column at
   once, is read); "a longer number is not cut" for `( XX.X)` (F9). One
   sentence is wrong: the shell (F1). Decisions 2 to 4, 6 and 7 are
   choices and are described as the code is. Decision 5 has to be
   written again.
10. Claims. Checked and right: 27 cells, 51 results, 27 equal; 51 ARD
    rows, 9 analyses, 15 ADaM and 15 SDTM columns; 30 of 30 files; 3,711
    of 3,735 and 4,238; 16 checks; 775 passed and 22 deselected; 99 cases
    of 8 methods; 13 cases of rule I3 and seven texts; 10 Fisher tables
    larger than 2 x 2; 69, 68, 1 and 0; 2537, 3, 2, 2 and 4; 3,734; the
    table of shapes; 3,580, 24 and 130 (125, 4 and 1); seven statements
    and 18 vectors; the line counts of the three logs; lines 321 to 327
    and 86 to 88; 387 and 390 files; 66 files and 22 SDTM datasets in the
    kit README; the hash of `PLAN.md`. The quotes of the logs are faithful
    (R2), with one category of left-out lines not named (F9). The report
    says plainly what was not done: no viewer, no citations, tfrmt not
    run, what the checks do not cover; and, before `f55f40d`, that the
    clean-clone gate was owed. Not right: the shell (F1), the state file
    (F9), the two vectors (F9).

## Not checked

- The source of tfrmt, its commit, version, license and imports: no
  network. Whether gt and forcats are two of fifteen imports.
- The clean-clone gate was not run again; R2 has what was compared. The
  CI run, whether `track/real` is pushed, and whether anything was posted.
- What the report says of the day (the network, the memory, the times,
  the kill by name, the owner's answer through the base session), except
  the times of the two log files.
- The page in a browser: its text was read, it was not opened.
- Tests A5 and A6 by a planted defect: they were read, and they pass.
- `tests/unit/test_cells_trace.py`, `test_results.py`, `test_rengine.py`
  and `test_grid.py` line by line; the two engines beyond the diff, which
  the review of real-2 covers; the 51 tests of std-1's checkers, beyond
  that they pass in the gate.
- The other seven analyses of the body in the planted `reads` edges of F4.
- The other four outputs of the example and their shells.

Verdict: PASS
