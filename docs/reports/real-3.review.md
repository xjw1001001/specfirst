# real-3 Grid, trace, viewer: independent review

Reviewed: work package real-3 of PLAN.md section 13.3, on branch
`track/real`, as it is at `10805f6`.

- The diff `34bbc14..10805f6`: `34bbc14` is `main` (unchanged since),
  `10805f6` is `10805f6dbd99f9638f724dc5e56274d541936a2e`; 31 files, 4,634
  insertions, 100 deletions, 7 files added. Three commits: `70dc552` (the
  findings F1 to F9 of the review of real-3a, ADR-003 points 1 to 9);
  `b71c200` (the two grids of the vital signs, the block kind `by_groups`,
  `columns.within`, the gate real-3, 123 new entries of `formats`, lessons
  74 to 77, and the log of the gate run of `70dc552`); `10805f6` (the
  report, the log of the clean-clone gate of `b71c200`, ADR-003 points 13
  and 14). `10805f6` changes three files under `docs/` and nothing else, so
  the gate evidence of `b71c200` covers the code. `docs/state/real.md` is
  changed by none of the three.
- No file was uncommitted in the worktree but this one. The documents the
  findings quote, as committed at `10805f6`:

  | File | Lines | SHA-256 |
  | --- | --- | --- |
  | `docs/reports/real-3.md` | 473 | `44acdba80ff82a5166315cfe2ad2dc84b1802cbe26ffdb34eac5578d7c7522f0` |
  | `docs/reports/real-3.clean-clone.gate.log` | 881 | `a3b77517def0c25091fafa24f0719da87535e62f4e74afa37cc6be6ba696444b` |
  | `docs/reports/real-3.first-commit.gate.log` | 681 | `7f3cc678e2f320da41c09da3b5605a4ecd8dc17aeb713fadb64642c0f24993b0` |
  | `docs/decisions/ADR-003.md` | 667 (no final line feed) | `4ba2c92c5f009e12afa6714878f4aabbacd827b70c88a761ed486f75aabb1474` |
  | `kits/cdiscpilot01/gold/exceptions.yaml` | 1091 | `7280416a6b458bd2f131ba259ba768ba3f9af5a043fac67dd87fd66b722a55fb` |
  | `docs/state/real.md` | 685 | `9606f07662e131f897bf4f16209adae4b6f4ed73eabc67bf005492ec7c4f1536` |

Date: 2026-11-23.

Reviewer: an independent agent with a fresh context that did not write the
work (rule R7). Correctness only, no style remarks. The reviewer changed no
tracked file, made no commit, and wrote this file only. No network was
used, nothing was posted, no package was installed, nothing was written
into the fetch cache, and no model was called.

## Outcome

One finding blocks (F1); five do not (F2 to F6).

The four statements of the gate text hold, each in every check the
reviewer made:

- `specfirst gate real-3 --clean` exited 0 on the reviewer's clone of
  `10805f6`: 19 of 19 checks. After commit, seconds and folders are made
  alike, its gate part differs from the committed clean-clone log of
  `b71c200` in three pairs of lines only: the commit, and 945 against 947
  files in two counts (the two files `10805f6` adds) (R1, R2).
- 100% of numeric cells have a complete path to SDTM: the reviewer's own
  walk of the graph files gives 3,815 of 3,815 numeric cells of the five
  grids complete (84, 27, 1,178, 1,263 and 1,263), and the `reads` and
  `computes` edges of the vital signs are those the reviewer reads from the
  ARS file (R5). The new edge checks fail on six single gaps of the
  reviewer's planting (R8).
- The graph build is deterministic: 72 of 72 files in the gate, and 72 of
  72 again in a third build of the reviewer's under another time zone, hash
  seed, locale and umask, in a folder with a blank (R4).
- The viewer opens with no network: the page that was built holds nothing
  that could fetch (R7). Its check passes three ways to fetch (F3), so that
  holds by the page, not by the check alone.
- The report walks one cell end to end, and the walk is right line by line
  (R5).

The two grids of the vital signs are right: the reviewer's recount, without
the checking code, gives every row, label, section, column, ARD list and
cell text of both, and the 1,893, 119 and 4 of the report (R3).

What blocks is the question the owner is asked about the four medians
(F1): the description of the data on which recommendation (A) and the class
`data_difference` rest is wrong in its numbers. The pilot's reference ADaM
holds our value 0.04999999999999716 as a change of temperature itself (for
example 36.94 - 36.89), there is no change 0.1 held as 0.0999999999999943,
and the example's "0.05" is a 12-character writing of that same value. The
new proof kind is narrow in what it accepts, but it does not show the class
it is bound to. Nothing is merged before the owner answers anyway; the
question must be put again with the right facts.

The other findings with weight: nothing holds which statistic a row of the
vital signs shows under its label, or the order of Q1 and Q3 and of the
minimum and the maximum in a cell; the comparison's docstring says the
shell holds the order of the parts of a cell (F2). The two checks of a page
pass hidden cells and three or four ways to fetch (F3). The vertical grid
lacks the title "Safety Population" that its ARS display and shell have
(F4). The report has five unfilled placeholders, among them the whole
section "The other gates", and the state file is not updated (F5).

## Scope and method

### What was read

- `CLAUDE.md`; PLAN.md sections 2, 4.6, 4.8, 7.4, 7.5 and the entries
  real-1 to real-3 of section 13.3; `docs/reports/real-3a.review.md`;
  ADR-003, the amendment of real-3 (points 1 to 14); `docs/reports/real-3.md`;
  `docs/state/real.md` (its head and the section "Next"); `docs/lessons.md`
  rows 74 to 77.
- Of the diff, in full: `src/specfirst/machine/shells.py`; the changes of
  `machine/{layout,grid,graph,render,results,ard,build}.py`, `kit.py` and
  `gates.py`; the changes of `tests/unit/{test_shells,test_grid,
  test_cells_trace,test_results,test_ard,test_kit,test_gates}.py`, of
  `tests/defects/test_defects.py` (D6, D7, D8, D14) and of its README;
  `kits/cdiscpilot01/{kit.yaml,README.md}`, the two new layouts, the change
  of `Out14-3-1-1.yaml`, the head of the section `formats` of
  gold/exceptions.yaml and the comment of the four medians; the two Fisher
  vectors. Outside the diff, as the questions needed them:
  `specfirst/viewer/check.py`, the plants of D13 and of
  `tests/unit/test_viewer.py`, `ars.display_sections`,
  `harness/binding.py` and the `binding.json` of read-2a's kept dry run,
  `gates.junit_problems`, `_trace`, `_grids`, `_review`.
- In the fetch cache, read only: the three pinned shells (their SHA-256 are
  those of kit.yaml) and the SAP of Pilot 6, as text written by poppler
  24.02 into the reviewer's scratch folder; the pilot's reference ADVS and
  ADSL (Parquet, with the installed pyarrow).
- Outside the repository, read only: the build in the author's Linux copy
  of the worktree (`/root/scratch/real3/dev/build`), used only to write the
  reviewer's scripts while the reviewer's gate waited for the lock. Every
  number below is from the reviewer's own build.

### What was run

All Linux commands ran in Ubuntu 24.04 under WSL2 as root, from script
files, after the `scripts/env.sh` of the worktree, with
`PYTHONDONTWRITEBYTECODE=1` and with `specfirst` taken from the reviewer's
clone of `10805f6` on the Linux file system. The gate and the third build
ran under `flock /run/lock/specfirst-heavy.lock taskset -c 0-3`. The
reviewer's scripts only read files of the build: those that call
specfirst's functions (in memory, for seconds each) ran with the installed
environment under `taskset -c 0-3`, the others with the system's Python
3.12 and `-I`. `<scratch>` is
`/root/scratch/review-real3`: everything the review wrote is there, the
scripts in `<scratch>/scripts` and their outputs in `<scratch>/logs`.
Scripts marked "standard library only" use nothing of specfirst. R1 to R15
name the runs of this review; a rule of the plan is written out as "rule
R11". Where a text block is an excerpt, the scripts print it in full when
they are run again.

Side effects outside `<scratch>`: none in the worktree but this file; the
gate wrote its `build/` folder into the reviewer's clone, pytest its
folders under `/tmp`.

| # | What | Result |
| --- | --- | --- |
| R1 | `specfirst gate real-3 --clean` on a clone of `10805f6` | `GATE real-3: PASS`, exit 0, 19 of 19 |
| R2 | R1 against the committed clean-clone log; the report's quotes against the two logs | 6 lines differ (commit, two file counts); every quoted line in its log, in order |
| R3 | the reviewer's recount of the two grids of the vital signs | 0 problems; 1,263 numeric cells each, 2,019 results, 67 cells differ, all by the 123 entries |
| R4 | a third build under other settings | 72 of 72 files with the hashes of the gate's builds |
| R5 | the reviewer's walk of the five grids; the report's cell | 3,815 of 3,815 complete; the walk as the report gives it |
| R6 | 22 planted layouts and 3 controls, judged as the gate judges a grid | the plants of F1 and F3 of real-3a fail; 12 plants pass (F2), and 4 of the labels of columns |
| R7 | planted pages; a scan of the review page | the page holds nothing that fetches; 6 plants pass the check of a grid page and 3 the check of the review page (F3) |
| R8 | six gaps planted in the graph files of the vital signs | each fails, 4 to 2,642 problems |
| R9 | the titles of the two grids against their ARS displays | F4 |
| R10 | halves; answer (B); other patterns for temperature | F6 |
| R11 | the change of temperature in the reference ADVS and ours; the example's raw values | F1 |
| R12 | `grid.half_problem` on eight cases of the reviewer | narrow: refused where it must be |
| R13 | F5 of real-3a with three other analyses of a wrong population | 0 proven; 15, 1 and 2 without the question |
| R14 | the two Fisher vectors in exact fractions | equal to the digit |
| R15 | clean room and scope | nothing found |

#### R1 The gate

```text
$ git clone --quiet --no-local /mnt/d/trial_work/specfirst/.git <scratch>/clone
$ git -C <scratch>/clone checkout --quiet --detach 10805f6
$ cd <scratch>/clone && export PYTHONPATH=$PWD/src SPECFIRST_ROOT=$PWD PYTHONDONTWRITEBYTECODE=1
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 python -u -m specfirst gate real-3 --clean
gate real-3 at commit 10805f6dbd99f9638f724dc5e56274d541936a2e (clean)
1454 passed, 38 deselected in 438.39s (0:07:18)
study data in git (E20): 947 maintained files checked, 0 problems
P1 determinism: 72 of 72 files have the same SHA-256 in both builds
grid Out14-3-3-1a: 1590 cells, 1263 print a number; 1263 of the 1263 cells with results have a complete path to SDTM columns
grid Out14-3-3-1b: 1515 cells, 1263 print a number; 1263 of the 1263 cells with results have a complete path to SDTM columns
trace: complete
trace of the grids: 5 outputs; numeric cells with a complete path: Out14-1-1 84, Out14-3-1-1 27, Out14-3-2-1 1178, Out14-3-3-1a 1263, Out14-3-3-1b 1263
grid Out14-3-3-1a: its mock shell against the table shell Vitals_Obs_ChgBaseline_Table_Shell.pdf: 265 rows held, 10 rows of the shell with cells
grid Out14-3-3-1a: 1590 cells show 2019 results; 1523 cells equal the reference's formatted values, 67 differ, 67 of them with one class
grid Out14-3-3-1b: its mock shell against the table shell Vitals_Obs_ChgBaseline_Table_Shell_vertical.pdf: 505 rows held, 15 rows of the shell with cells
grid Out14-3-3-1b: 1515 cells show 2019 results; 1448 cells equal the reference's formatted values, 67 differ, 67 of them with one class
grids: 10 outputs, pass
review: build/p1/cdiscpilot01/first/viewer/index.html has 5597006 bytes, 63 panels of analyses, 4028 cells with a panel; it loads and runs nothing: True; the second build of P1 gives the same page: True
101 passed in 131.62s (0:02:11)
ASCII check: 947 files checked, 0 with non-ASCII bytes
GATE real-3: PASS
```

The script first ran `cd /mnt/d/trial_work/specfirst-real && . scripts/env.sh`.
The gate waited for the lock from 12:40 and ran from 13:07:51 to 13:19:14.
The block is an excerpt of its 827 lines. All 72 hash lines of P1 are those
of the committed log (R2); among them the eight files of the vital signs
the report quotes (`5e0dc4af97af66a7`, `2993e727a7f6036a`,
`244261ee3dcbe1c8`, `a6c01585a4b0dfb0`, `07677ba96f9e3aae`,
`55e8adc753417927`, `a594db66ea116c5c`, `3427a2d268a5fa70`) and the three
graph files (`8183aecc041ac10d` coverage, `2112a17bd291b75f` edges,
`c30a7c7f62c9005d` nodes).

#### R2 The logs and the quotes

```text
gate part: mine 823 lines; the committed log 823 lines
lines that differ after the normalisation: 6
   -gate real-3 at commit b71c200536b5a9686344b2760dfc6e5eb9a615ac (clean)
   +gate real-3 at commit 10805f6dbd99f9638f724dc5e56274d541936a2e (clean)
   -study data in git (E20): 945 maintained files checked, 0 problems
   +study data in git (E20): 947 maintained files checked, 0 problems
   -ASCII check: 945 files checked, 0 with non-ASCII bytes
   +ASCII check: 947 files checked, 0 with non-ASCII bytes
block at line 73 against the first log: 41 quoted lines found in order (4 shortened with [...]), 0 not found
block at line 215 against the clean log: 77 quoted lines found in order (7 shortened with [...]), 1 not found
    not found: $ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 scripts/clean_clone_gate.sh real-3 /mnt/d/trial_work/specfirst/.git b71c200
first-commit log, its commit line: ['gate real-3a at commit 70dc552c56225cf18ae762b97c6b558c2350181d (clean)']
first-commit log, its summary: [..., 'GATE real-3a: PASS'] PASS lines: 16
clean log, PASS lines: 19 ['GATE real-3: PASS']
```

The normalisation makes seconds, folders, pytest's progress dots and the
path of the environment alike. The one line not found is the command that
started the clean-clone script, which the script does not echo. So the
clean-clone gate ran as the report says on code that is the code of
`10805f6`; the reviewer did not run the clean-clone script (it needs the
network) and did not run the gate real-3a on `70dc552` again: its log is
read (16 of 16, the commit of `70dc552`).

#### R3 The reviewer's recount of the vital signs

A script of the reviewer (standard library only) reads the ARS file of
the build (SHA-256 `90358dd6...`, the pin), the two ARD files, the two grid
files and gold/exceptions.yaml. It builds both grids from its own reading
of the two shells: under each arm the observed value and the change
(horizontal) or one column per arm (vertical); per parameter in its order
of the ARS grouping, per visit in its order, a row without cells (the
visit; in the vertical grid also "<visit> Change from Baseline") and the
rows "n", "Mean (SD)", "Median", "Q1, Q3", "Min, Max", from the operations
1_n, 2_Mean and 3_SD, 4_Median, 5_Q1 and 6_Q3, 7_Min and 8_Max; no change at
baseline. It formats our values with its own reading of a pattern (round
half away from zero from the shortest decimal text; a mask with a point
pads on the left; a minus sign before) and takes the example's texts from
the ARS file.

```text
formats entries read by the reviewer: 124 {'not_its_own_pattern': 120, 'half_in_floating_error': 4}
Out14-3-3-1a: rows 265 columns 6 cells 1590 print a number 1263 results shown 2019
   cells with results equal to the example's text 1196; differ 67; results that differ 123; problems 0
Out14-3-3-1b: rows 505 columns 3 cells 1515 print a number 1263 results shown 2019
   cells with results equal to the example's text 1196; differ 67; results that differ 123; problems 0
An08_01_Obs_Summ_ByTrt: the example 1056 (with a formatted value 1056); ours 1056; shown in Out14-3-3-1a 1056; shown in Out14-3-3-1b 1056
An08_02_ChgBl_Summ_ByTrt: the example 960 (with a formatted value 960); ours 1056; shown in Out14-3-3-1a 960; shown in Out14-3-3-1b 960
changes at baseline in our ARD: 96 {('n', 0): 12, ('Mean', None): 12, ('SD', None): 12, ('Median', None): 12, ('Q1', None): 12, ('Q3', None): 12, ('Min', None): 12, ('Max', None): 12}
both grids show the same results: True | the same results differ: True
results that differ: 123 | entries of formats for the vital signs: 123 | the same set: True
    ('An08_', 'Max', 'Param_4', 'reference_error', 'not_its_own_pattern') 60
    ('An08_', 'Median', 'Param_4', 'data_difference', 'half_in_floating_error') 4
    ('An08_', 'Min', 'Param_4', 'reference_error', 'not_its_own_pattern') 59
not_its_own_pattern of the vital signs: 119; the example's text has decimals, its raw value under XX is our text, the entry's text is the example's: 119
   the example's raw value is ours (1e-9): 119 | the example's text is its raw value with trailing zeros dropped: 119
minima and maxima of the two analyses in the example: 504; whole numbers: 385; whole and the example's text is our text: 385; not whole: 119, by parameter {'Param_4': 119}
cells that differ, by what differs: {('Max', 'Min'): 52, ('Min',): 3, ('Max',): 4, ('Max', 'Median', 'Min'): 4} | cells: 63
```

"Problems 0" includes: every row's label and section, the labels and
spanners of the columns, the ARD rows of every cell in the order of its
template, every empty cell empty, every text the reviewer's formatting of
the Python value, and the R value giving the same text. The 1,196 cells
with results that equal the example plus the 327 empty cells are the gate's
1,523 (1a); 1,196 plus 252 are its 1,448 (1b). The 63 of the last line
(counted by analysis and groups) are the "Min, Max" cells of temperature:
56 with both values differing (4 of them in a group whose median differs
too) and 7 with one, so 119 results; with the 4 cells of the medians they
are the 67. So 1,893 + 119 (59 minima, 60 maxima) + 4 = 2,016, as the
report says.

#### R4 P1 beyond the gate

A third build after the gate, from another working folder, into a folder
with a blank in its path, under another time zone, hash seed, locale and
umask, then its files against the two builds of the gate (standard library
only):

```text
$ cd <scratch> && flock /run/lock/specfirst-heavy.lock taskset -c 0-3 env TZ=Asia/Tokyo PYTHONHASHSEED=12345 LC_ALL=C LANG=C COLUMNS=40 \
    bash -c "umask 077; python -m specfirst build cdiscpilot01 --into '<scratch>/b3 with a blank/and/depth'"
build cdiscpilot01: 10 datasets, 10181 nodes, 16428 edges, 72 files in <scratch>/b3 with a blank/and/depth
$ python3 -I <scratch>/scripts/p1.py <clone>/build/p1/cdiscpilot01/first <clone>/build/p1/cdiscpilot01/second '<scratch>/b3 with a blank/and/depth'
files listed in build.json: 72
second (the gate): listed files with the hash of the first build: 72 of 72; build.json the same: True
third (TZ, seed, locale, umask, a blank): listed files with the hash of the first build: 72 of 72; build.json the same: True
every listed file of the first build has the hash build.json gives: True
   gold/graph/nodes.jsonl c30a7c7f62c9005d c30a7c7f62c9005d
   gold/graph/edges.jsonl 2112a17bd291b75f 2112a17bd291b75f
   gold/graph/coverage.json 8183aecc041ac10d 8183aecc041ac10d
   gold/grid/Out14-3-3-1a.json 5e0dc4af97af66a7 5e0dc4af97af66a7
   gold/grid/Out14-3-3-1b.json 244261ee3dcbe1c8 244261ee3dcbe1c8
```

It ran from 13:34:30 to 13:34:49 (Eastern time). The 72 files are those
the build writes (`build.json` lists them); the kit's own and pinned files
that a build assembles are held by kit.yaml.

#### R5 The trace

A script of the reviewer (standard library only) walks every numeric cell
of the five grids of the example through `nodes.jsonl`, `edges.jsonl` and
`coverage.json`: the cell's `shows` edges equal its ARD rows, every ARD row
computes from its own analysis, every analysis reads ADaM columns, every
column reaches SDTM columns through `derives_from` and has no gap.

```text
nodes 10181 {'adam': 415, 'ard': 4517, 'ars': 63, 'cell': 4788, 'doc': 287, 'sdtm': 111}
edges 16428 {'cites': 750, 'computes': 5408, 'derives_from': 3269, 'reads': 441, 'shows': 6560} | edges with an end that is no node: 0
Out14-1-1: cells 104, numeric 84, complete by the reviewer's walk 84; 147 ARD rows, 13 analyses, 9 ADaM columns read, 17 SDTM columns
Out14-3-1-1: cells 27, numeric 27, complete by the reviewer's walk 27; 51 ARD rows, 9 analyses, 9 ADaM columns read, 15 SDTM columns
Out14-3-2-1: cells 1275, numeric 1178, complete by the reviewer's walk 1178; 1940 ARD rows, 10 analyses, 7 ADaM columns read, 13 SDTM columns
Out14-3-3-1a: cells 1590, numeric 1263, complete by the reviewer's walk 1263; 2019 ARD rows, 3 analyses, 9 ADaM columns read, 19 SDTM columns
Out14-3-3-1b: cells 1515, numeric 1263, complete by the reviewer's walk 1263; 2019 ARD rows, 3 analyses, 9 ADaM columns read, 19 SDTM columns
five grids: numeric 3815 complete 3815
reads of An01_05_SAF_Summ_ByTrt: the reviewer's 3, the edges 3, equal True; coverage.json equal True
reads of An08_01_Obs_Summ_ByTrt: the reviewer's 8, the edges 8, equal True; coverage.json equal True
reads of An08_02_ChgBl_Summ_ByTrt: the reviewer's 8, the edges 8, equal True; coverage.json equal True
cites edges of ars:An08_01_Obs_Summ_ByTrt: 3 | cites edges of ars:An08_02_ChgBl_Summ_ByTrt: 3 (to pages 9 and 17 of the SAP)
ARD nodes of the vital signs: 2016; computes edges other than to its own analysis alone: 0
```

The reviewer's reads are read from the ARS file by hand: the analysis set
(ADSL.SAFFL), the groupings (ADSL.TRT01A, ADVS.PARAMCD, ADVS.AVISIT), the
data subset (ADVS.ANL01FL; for the changes also ADVS.AVISIT), the variable
(ADVS.AVAL or ADVS.CHG) and the subject key of both datasets. The report's
cell, walked by the same script (lines shortened: the script prints each
node's record and the SDTM columns in full):

```text
cell:Out14-3-3-1a/r10/c2: text '- 3.3 (14.60)'; row 'Mean (SD)' in 'Systolic Blood Pressure (mmHg)'; column 'Change from Baseline' under 'Placebo'
   the row without cells above it: Week 2
   shows ard:An08_02_ChgBl_Summ_ByTrt/Mth02_ContVar_Summ_ByGrp_2_Mean/AnlsGrouping_01_Trt_1/AnlsGrouping_08_Param_1/AnlsGrouping_09_Visit_02 | gold/ard/common-safety-displays.jsonl line 3316
     computes ars:An08_02_ChgBl_Summ_ByTrt | gold/spec/ars/common-safety-displays.json line 54268
   shows ard:An08_02_ChgBl_Summ_ByTrt/Mth02_ContVar_Summ_ByGrp_3_SD/AnlsGrouping_01_Trt_1/AnlsGrouping_08_Param_1/AnlsGrouping_09_Visit_02 | gold/ard/common-safety-displays.jsonl line 3448
     computes ars:An08_02_ChgBl_Summ_ByTrt | the same
     reads adam:ADSL.SAFFL (gold/spec/spec/yamaa/pilot-program/adsl_v1.yaml:507) -> 7 SDTM columns
     reads adam:ADSL.TRT01A (gold/spec/spec/yamaa/pilot-program/adsl_v1.yaml:304) -> 2 SDTM columns
     reads adam:ADSL.USUBJID (gold/spec/spec/yamaa/pilot-program/adsl_v1.yaml:259) -> 2 SDTM columns
     reads adam:ADVS.ANL01FL (gold/spec/cdiscpilot01/spec/yamaa/advs.yaml:777) -> 11 SDTM columns
     reads adam:ADVS.AVISIT (gold/spec/cdiscpilot01/spec/yamaa/advs.yaml:445) -> 11 SDTM columns
     reads adam:ADVS.CHG (gold/spec/cdiscpilot01/spec/yamaa/advs.yaml:640) -> 11 SDTM columns
     reads adam:ADVS.PARAMCD (gold/spec/cdiscpilot01/spec/yamaa/advs.yaml:300) -> 11 SDTM columns
     reads adam:ADVS.USUBJID (gold/spec/cdiscpilot01/spec/yamaa/advs.yaml:107) -> 11 SDTM columns
   the example: Mth02_ContVar_Summ_ByGrp_2_Mean -3.301204819 '- 3.3'
   the example: Mth02_ContVar_Summ_ByGrp_3_SD 14.601205435 '(14.60)'
```

The SDTM columns behind each column (printed in full by the script) are
those of the report's walk.

#### R6 Planted layouts

Judged as D14 judges a grid, which is what the gate's check "grids" asks:
`layout.problems`, the build of the grid, `grid.compare_reference` with the
kit's entries of `formats`, `shells.compare` of the mock shell against the
pinned shell, and the counts of `gates.PILOT_GRIDS`.

```text
Out14-3-3-1a, control: unchanged: 0 problems
Out14-3-3-1b, control: unchanged: 0 problems
Out14-3-1-1, control: unchanged: 0 problems
Out14-3-3-1a, Q1 and Q3 exchanged in their cell: 0 problems
      a cell of the planted grid: cell:Out14-3-3-1a/r6/c1 '150.0, 124.0'
Out14-3-3-1b, Q1 and Q3 exchanged in their cell: 0 problems
Out14-3-3-1a, the minimum and the maximum exchanged in their cell: 0 problems
Out14-3-3-1b, the minimum and the maximum exchanged in their cell: 0 problems
Out14-3-3-1a, the mean in the row Median, the median in the row Mean (SD): 0 problems
      the planted row r5 'Median' shows '136.8' (Mth02_ContVar_Summ_ByGrp_2_Mean)
Out14-3-3-1b, the mean in the row Median, the median in the row Mean (SD): 0 problems
Out14-3-3-1a, the n in the place of the minimum, the minimum in the row n: 0 problems
Out14-3-3-1a, the labels Observed and Change from Baseline exchanged: 0 problems
Out14-3-3-1a, the labels of placebo and high dose exchanged (columns.labels): 0 problems
Out14-3-3-1b, the labels of placebo and high dose exchanged (columns.labels): 0 problems
Out14-3-3-1b, the headings of the observed rows and of the change rows exchanged: 1 problems; for example: shell: line 12 of the shell ('Baseline'): a heading no section and no row of the mock shell shows
Out14-3-3-1b, the change rows above the observed rows at every visit: 0 problems
Out14-3-3-1a, the sections of systolic and diastolic pressure exchanged (labels): 0 problems
Out14-3-3-1b, the sections of systolic and diastolic pressure exchanged (labels): 0 problems
Out14-3-3-1a, the visits Week 2 and Week 4 exchanged (labels): 0 problems
Out14-3-3-1b, the visits Week 2 and Week 4 exchanged (labels): 0 problems
Out14-3-1-1, the labels of the first two rows exchanged: 4 problems; for example: shell: row r3 ('TEAE'): in the shell it does not follow the row before it
Out14-3-1-1, the labels of placebo and high dose exchanged (columns.labels): 0 problems
Out14-3-1-1, the section renamed 'Number of subjects with at least one adverse event': 2 problems; for example: shell: section '...': no text of the shell, and no placeholder, fits it
Out14-3-1-1, the percent of the third row (Serious TEAE) in the first row: 8 problems; for example: rows[1], part 'pct': the row of 'An07_01_TEAE_Summ_ByTrt' shows a result of 'An07_03_SerTEAE_Summ_ByTrt', which none of its results is computed from
Out14-3-1-1, the second row again in a second analyses block: 2 problems; for example: rows[2]: the analysis 'An07_02_RelTEAE_Summ_ByTrt' stands in rows[1] already; an analysis stands in one block
Out14-3-1-1, the count as '{n} ({pct})' (another text around the percent): 16 problems; for example: shell: row r2 ('TEAE'): no row of the shell has this label and the masks ['XX (( XX.X))', ...]
```

The plants of F1 and F3 of real-3a on the AE summary fail: the labels of
two rows exchanged (which passed in real-3a), the section renamed, the
percent of another row, a row in a second block, another text around the
percent. Twelve plants on the vital signs pass: finding F2. Four more pass
that exchange labels of columns, which the report names as not held.

#### R7 Planted pages; the review page

```text
page Out14-3-3-1a.html: 114248 characters
  render.projection_problems, unchanged: 0 problems
  render.projection_problems, the cells of column c2 hidden by a style attribute: 0 problems
  render.projection_problems, the row r3 hidden by the attribute hidden: 0 problems
  render.projection_problems, <body background=...> (an image fetched): 0 problems
  render.projection_problems, <video poster=...> in the body: 0 problems
  render.projection_problems, <svg><image xlink:href=...>: 0 problems
  render.projection_problems, a style attribute with image-set(...): 0 problems
viewer page index.html: 5597006 bytes; 'http:' 0; 'https:' 0; '//' 0; 'src=' 0; 'srcset' 0; 'href="h' 0; 'url(' 0; '@import' 0; '<script' 0; '<link' 0; '<img' 0; '<iframe' 0; '<object' 0; '<embed' 0; '<video' 0; '<audio' 0; '<svg' 0; 'xlink' 0; 'background=' 0; 'poster' 0; 'image-set' 0; '<meta' 1; '<form' 0; '<base' 0
   attributes on...: 0 | hrefs not to an anchor: 0
  viewer.check.page_problems, unchanged: 0 problems
  viewer.check.page_problems, <body background=...>: 0 problems
  viewer.check.page_problems, <svg><image xlink:href=...>: 0 problems
  viewer.check.page_problems, a style attribute with image-set(...): 0 problems
  viewer.check.page_problems, <video poster=...>: 1 problems; the page has a <video>
  viewer.check.page_problems, <img src=...> (control): 2 problems; the page has a <img>
  viewer.check.page_problems, <iframe src=...>: 2 problems; the page has a <iframe>
  viewer.check.page_problems, <form action=...>: 2 problems; the page has a <form>
  viewer.check.page_problems, @import in the style element: 1 problems; the page holds '@import'
  viewer.check.page_problems, a meta refresh: 2 problems; the page holds 'http-equiv'
  viewer.check.page_problems, <object data=...>: 2 problems; the page has a <object>
```

The address planted is `https://example.org/x.png`; nothing was fetched
(the pages were held in memory). The review page is the one the gate wrote
from the first build (5,597,006 bytes, as the gate prints); its one `meta`
is the character set. It was not opened in a browser (the desktop app's
browser cannot open a local file).

#### R8 Planted gaps of the trace

Copies of the three graph files of the build, changed under
`<scratch>/graph-plants`, judged by `graph.check_cells` with the events, as
the gate's trace calls it.

```text
control: unchanged: 0 problems
the reads edge of the changes to ADVS.CHG left out: 2402 problems, 2402 of the vital signs
the reads edge of the observed values to ADSL.SAFFL left out: 2642 problems, 2642 of the vital signs
the reads edge of the changes to ADVS.AVISIT left out (the visit is a grouping and a subset): 2402 problems
a reads edge of the changes to ADVS.AVAL added, and recorded in coverage.json: 1202 problems
one ARD row of the changes computed from the observed values too (an edge added): 4 problems
coverage.json: the changes read ADVS.AVAL as well (the edges unchanged): 1202 problems
```

#### R9 The titles of the vital signs

```text
Out14-3-3-1b displayTitle: '... - Vital Signs <Vertical Layout>'
    Title ['Table 14.3.3.1b', "-> Disp14-3-3-1a_Title_2: 'Summary of Observed and Change from Baseline by Scheduled Visits - Vital Signs'", "-> GlobalDisp_Title_1: 'Safety Population'"]
    Legend ["-> Disp14-3-3-1a_Legnd_1: 'Note: Baseline is defined as ...'"]
    Footer ["-> Disp14-3-3-1a_Footer_1: '...'", "-> GlobalDisp_Footer_1: '...'"]
    Rowlabel Header ["-> Disp14-3-3-1a_RLbHd_1: 'Parameter (Units)'", "-> Disp14-3-3-1a_RLbHd_2: 'Visit'"]
   grid titles: ['Table 14.3.3.1b', 'Summary of Observed and Change from Baseline by Scheduled Visits - Vital Signs'] | footnotes: ['Notes: Baseline is defined as ...'] | header row label: Parameter (Units) Visit
Out14-3-3-1a grid titles: ['Table 14.3.3.1a', 'Summary of ... Vital Signs', 'Safety Population']
```

("->" marks a subsection the display names by its ID; the second title of
1a has a dash outside ASCII in the ARS file, written here as "-".)

#### R10 Halves, answer (B), other patterns

```text
the example's results with a raw and a formatted value: 3734; raw value exactly on a half at the pattern's decimals: 11
    ('An03_06_Height_Summ_ByTrt', 'Mth02_ContVar_Summ_ByGrp_6_Q3', '172.85', '172.9')
    ('An03_06_Height_Summ_ByTrt', 'Mth02_ContVar_Summ_ByGrp_8_Max', '190.5', '190.5')
    ('An08_01_Obs_Summ_ByTrt', 'Mth02_ContVar_Summ_ByGrp_8_Max', '37.5', '37.5')   [three times]
    ('An08_01_Obs_Summ_ByTrt', 'Mth02_ContVar_Summ_ByGrp_4_Median', '36.75', '36.8')
    ('An08_02_ChgBl_Summ_ByTrt', 'Mth02_ContVar_Summ_ByGrp_4_Median', '0.05', ' 0.1')   [four times]
    ('An08_02_ChgBl_Summ_ByTrt', 'Mth02_ContVar_Summ_ByGrp_6_Q3', '0.25', ' 0.3')
shown results of ours within a relative 1e-9 of a half at their decimals: 10 (the nine of the vital signs above and 172.85)
results shown with a number, by group of grids: {'example, both': 3, 'example, not vital': 2123, 'efficacy': 375, 'vital': 2016}
of them, whose text changes under (B): {'vital': 4}
example ARD: float typed 3053 int typed 1101 None 84
other grids 2501 float typed 1559 not whole 1074 number 2501
minima and maxima of temperature: 126; under XX.XX (the data's decimals) our text differs from the example's in 64; their cells: 63
   under XX.XX (observed) and X.XX (changes): 10 differ; the example's texts of these by their decimals: {1: 3, 0: 7}
```

(B) is "round a value to 12 significant digits before the display rule".
The script pairs every result of every grid with the mask of its cell in
the mock shell (in the terms block, with the numbers of the cell's text).

#### R11 The four medians in the data

The pilot's reference ADVS (in the fetch cache) and the ADVS of the
reviewer's build, read with pyarrow; the population, the subset and the
arms as the analysis has them (SAFFL, ANL01FL, AVISIT other than Baseline,
TRT01A of ADSL):

```text
reference: TEMP change records 1757; values within 1e-9 of +-0.1, as stored: {}
ours: TEMP change records 1757; values within 1e-9 of +-0.1, as stored: {}
reference: TEMP records whose CHG is 0.04999999999999716: 56; (AVAL, BASE) most common: [(('36.94', '36.89'), 16), (('36.44', '36.39'), 12), (('36.61', '36.56'), 8), (('36.33', '36.28'), 6)]
ours: TEMP records whose CHG is 0.04999999999999716: 56; (AVAL, BASE) most common: [the same four pairs and counts]
   reference Placebo, Week 12: n 69, the middle values ['0.04999999999999716'], median 0.04999999999999716
   reference Placebo, Week 16: n 68, the middle values ['0.04999999999999716', '0.04999999999999716'], median 0.04999999999999716
   reference Xanomeline Low Dose, End of Treatment: n 71, the middle values ['0.04999999999999716'], median 0.04999999999999716
   reference Xanomeline High Dose, Week 2: n 81, the middle values ['0.04999999999999716'], median 0.04999999999999716
   [the same four lines for ours]
```

The four cells are those of the four entries (placebo at weeks 12 and 16,
the low dose at the end of treatment, the high dose at week 2); their n are
the n of the ARD.

The example's raw values (standard library only), by the length of their
text:

```text
raw values with a point, by the length of their text: {3: 2, 4: 86, 5: 265, 6: 362, 7: 35, 8: 3, 9: 4, 10: 9, 11: 48, 12: 453, 16: 3, 17: 17, 18: 14, 19: 1}
   of the vital signs: {3: 2, 4: 85, 5: 218, 6: 15, 7: 1, 8: 2, 9: 1, 10: 4, 11: 44, 12: 441, 19: 1}
   for example: '17.807101157', '-3.301204819', '14.601205435'
```

813 of the 814 raw values of the vital signs that have a decimal point are
at most 12 characters long; 0.04999999999999716 in 12 characters is
"0.05".

#### R12 The proof `half_in_floating_error` on the reviewer's cases

```text
the kit's case: accepted
ours 2e-9 relative below the half: refused: our value 0.0499999999 is not the reference's 0.05 within a relative 1e-9
ours 1e-9 relative below the half (not binary floating error): refused: our value 0.04999999995 is not the reference's 0.05 within a relative 1e-9
ours exactly the double 0.05: refused: our value 0.05 is not on the other side of the half 0.05
a reference raw value of more digits on a half: accepted
the half 0.25 under XX.X, ours just below: accepted
a whole-number pattern: the half 37.5 under XX, ours just below: accepted
class rule_choice: refused: a value at a half in floating error proves a data_difference only
```

The eight cases are the reviewer's, on `results.Embedded` items made by
hand; "1e-9 relative" is at the edge of the tolerance and is refused by
floating error of its own.

#### R13 F5 of real-3a on other analyses

The reviewer's own plant, made as D6 makes its own (the reference
unchanged): each analysis in turn reads its population from EFFFL; every
differing quartile and median is tried as a `reference_error` with both
proofs, with the question of the n, the minimum and the maximum and, by a
patch, without it.

```text
An08_02_ChgBl_Summ_ByTrt with its population read from EFFFL: quartiles and medians 45; proven errors of the reference {'between_equal_values': 0, 'same_under_every': 0}; without the question {'between_equal_values': 15, 'same_under_every': 15}
An03_01_Age_Summ_ByTrt with its population read from EFFFL: quartiles and medians 4; proven errors of the reference {'between_equal_values': 0, 'same_under_every': 0}; without the question {'between_equal_values': 1, 'same_under_every': 2}
An03_06_Height_Summ_ByTrt with its population read from EFFFL: quartiles and medians 5; proven errors of the reference {'between_equal_values': 0, 'same_under_every': 0}; without the question {'between_equal_values': 2, 'same_under_every': 1}
```

#### R14 The Fisher vectors

The reviewer's own enumeration of every table with the margins, summed in
exact fractions (standard library only, not `oracle.py`):

```text
[[0, 6, 20], [8, 27, 40]] exact 0.06040878692449789 | vector 0.06040878692449789 | relative difference 0.0
[[4, 8, 30], [0, 6, 56]] exact 0.00979884680687777 | vector 0.00979884680687777 | relative difference 0.0
```

#### R15 Clean room and scope

```text
git diff --name-only 34bbc14..10805f6 -- PLAN.md standard env scripts Makefile pyproject.toml CLAUDE.md .github third_party r   -> nothing
PLAN.md sha256 2b49031c6fd7a668229752f2692fa1828065a9a5543fb9d3070114fc82b78372 at 34bbc14 and at 10805f6
CLAUDE.md: 59 lines; tracked files: 947
added lines with something like a subject number of the pilot: 0; with a byte outside ASCII: 0
files of the diff by type: 18 py, 5 md, 5 yaml, 2 log, 1 json; tracked files ending .pdf, .rtf, .xpt, .parquet, .sas7bdat: 0
numbers with nine or more decimals in added lines: 36, all in the two gate logs, the Fisher vectors and their names, the tests and texts of the four medians
added lines with a Windows user path: 0 (paths under /root and /tmp, as earlier reports have)
```

The three shells are pinned in kit.yaml by source, path and SHA-256 and
copied from the cache into a build; none is in git. What the diff quotes of
the example: the 123 formatted values of the new entries of `formats` and
rows of the grids in the report, as real-2, real-3a and issue #31 did.

## Findings

### F1 (blocking) The four medians: the facts given to the owner are wrong, and the new proof kind does not show its class

The report (sections "The vital signs" and "For the owner", item 1),
ADR-003 point 13, the comment of the four entries in gold/exceptions.yaml
and the docstring of `grid.half_problem` explain the four medians so: the
example's raw value 0.05 is "the half of the two middle changes 0.0 and
0.1"; "the ADaM holds the change 0.1 as 0.0999999999999943 (AVAL - BASE in
binary floating point)"; so "the exact value is the reference's: ours
carries the error of binary floating point from the data (a change from
baseline of 0.1 held as 0.0999999999999943)". On that reading the owner is
asked to approve the class `data_difference` ("the public data are not the
data behind the reference", PLAN.md section 4.8) with the new proof kind
`half_in_floating_error`, which the report recommends as answer (A).

The data say otherwise (R11):

- In the pilot's reference ADVS and in ours, no change of temperature lies
  within 1e-9 of 0.1 or -0.1. There is no change 0.1 held as
  0.0999999999999943.
- The four medians are not halves of the middle changes 0.0 and 0.1. Three
  of the four cells have an odd n (69, 71 and 81): the median is the middle
  record's own change. The fourth (n 68) has two middle records with the
  same change. That change is 0.04999999999999716, the value of 56 records
  of temperature, such as AVAL 36.94 and BASE 36.89: a change of 0.05 held
  in binary floating point. The pilot's reference ADVS holds exactly this
  value, in 56 records with the same pairs of AVAL and BASE, as ours does.
- The example's raw values of the vital signs are written in at most 12
  characters (813 of the 814 with a decimal point: "17.807101157",
  "-3.301204819"). 0.04999999999999716 written in 12 characters is "0.05".
  So the raw value "0.05" does not show that the reference's value lay
  exactly on the half; it is what the value the public ADaM holds gives in
  the example's own way of writing a raw value.

So the cause the proof kind states, and the class it is bound to, are not
shown, and two numbers of the description are wrong. What the repository
shows fits better a rule of display of the example: it rounds the value
(to its 12-character raw value, or by a rounding that absorbs such an
error) before it applies the pattern. That is answer (B) of the report, and
PLAN.md section 4.8 calls the case `rule_choice`, proven by "a build with
that alternative, in which the cells equal the reference"; the report has
measured what that build gives, and so has the reviewer: under (B) the four
cells show " 0.1" and nothing else of the pilot changes (R10). Whether the
example was made from other data (the SAS transport files, say) the
repository cannot show either way.

What `half_problem` checks is narrow (R12): it refuses our value 2e-9 off,
our value exactly on the half, another class; it accepts only a raw value
exactly on a half with ours within a relative 1e-9 on the other side. The
defect is in what it is taken to prove. This blocks because the owner is asked to decide on numbers that are
wrong, and the four cells pass the gate only by this class (PLAN.md 4.8: a
difference with no class blocks the gate).

Fix: correct the description in the report, ADR-003 point 13, the comment
in gold/exceptions.yaml, the docstring of `half_problem` and the docstring
of its test; put the question to the owner again with the facts of R11;
and either record the four as `rule_choice` proven by the build under (B),
or keep `half_in_floating_error` with a statement of what it does prove (a
value on a half at the reference's precision, ours the same number within
a relative 1e-9), not of a cause.

### F2 (not blocking; to correct before the merge) Nothing holds which statistic a row shows, or the order of two parts with one mask

The table shell holds a row by its label and its masks, and the comparison
builds the example's text of a cell from the layout's own template. So
nothing holds which operation a statistic row of a `by_groups` block (or of
a `statistics` block) shows under its label, nor the order in a cell of two
parts with the same mask. Planted in the layouts of the kit and judged as
the gate judges a grid (R6), each passes, on both grids of the vital signs
where it applies: Q1 and Q3 exchanged in their cell (the grid then shows
"150.0, 124.0" under "Q1, Q3"); the minimum and the maximum exchanged; the
mean in the row "Median" and the median in the row "Mean (SD)"; the n in
the place of the minimum. Also passing: in the vertical grid, the change
rows above the observed rows at every visit (the shell holds the order of
the rows within a run, not of the runs); and the sections of two parameters
or the rows of two visits exchanged through `labels` (the shells have
placeholders there).

`grid.compare_reference` says: "Which results share a cell, in which order,
and with what text between them is held against the example's table shell
where the kit pins one". For parts with one mask the order is not held. The
report's list of what the checks do not cover names neither this nor the
statistic behind a row's label. The grids of the build are right: the
reviewer's recount puts every statistic under its label, Q1 before Q3 and
the minimum before the maximum, from the example's own operations (R3). The
same limit stands in the statistics blocks of the demographics (issue #31),
which have no pinned shell.

Fix: hold the words of a statistic row's label against the labels of the
ARS operations of its parts, in order; in the example they are the words of
the shells ("n"; "Mean", "SD"; "Median"; "Q1", "Q3"; "Min", "Max"). Or name
the limit in the docstring and in the report.

### F3 (not blocking) The two checks of a page pass hidden cells and other ways to fetch

`render.projection_problems` (the grid pages; F6 of real-3a) passes, on the
page of Out14-3-3-1a (R7): the cells of a column hidden by `style`
attributes; a row hidden by the attribute `hidden`; an image fetched by
`<body background=...>`, by `<video poster=...>`, by an SVG `<image
xlink:href=...>`, and by a `style` attribute with `image-set(...)` (it
refuses a style attribute only with `url(`). The check of the review page,
`specfirst.viewer.check.page_problems`, by which the gate's check "review"
says the viewer "loads and runs nothing", passes `background=`,
`xlink:href` and `image-set(` (it sees `<video>`, `<img>`, `<iframe>`,
`<form>`, `<object>`, `@import` and a refresh, R7).

The gate statement holds for the page that was built: its 5.6 MB hold no
"//", no "http", no `url(`, no `src`, no `srcset`, no `xlink`, no
`background=`, no `image-set`, no handler and no link that is not to an
anchor (R7), and P1 compares it between two builds. So the check is weaker
than its words, as F6 of real-3a was, now on the page a gate statement
names. The check of the review page dates from issue #31.

Fix: refuse any attribute other than those the writers use (class, id,
href to an anchor, data-*, colspan) and any "//" or URL scheme in a style;
in the grid pages refuse `hidden` and a `style` attribute.

### F4 (not blocking) The vertical grid lacks a title its ARS display has; a sentence of its layout is wrong

The layout of Out14-3-3-1b gives its own titles and footnote because, its
comment says, "The display of this output in the ARS file has its first
title only and no footnote, no legend and no header of the row labels". The
display has all of them (R9): its second title, legend, footer and the two
row-label headers by reference to subsections of the display of
Out14-3-3-1a (`Disp14-3-3-1a_Title_2` and so on), and its third title is the
global "Safety Population". `ars.display_sections` resolves only global
subsections, so it would give "Table 14.3.3.1b" and "Safety Population";
the layout replaces both with two titles of its own, so the grid of 1b has
no "Safety Population", which its ARS display, its shell (line 4) and the
grid of 1a have. Titles are held against nothing (the report says so), so
no check sees it.

Fix: resolve in `ars.display_sections` a subsection that any display of the
event defines; take the titles of 1b from the ARS file; correct the comment.

### F5 (not blocking; to correct before the merge) The report and the state file are not finished

- docs/reports/real-3.md holds five placeholders: `@@OTHERGATESHORT@@` (in
  the verdict), `@@OTHERGATES@@` (all of the section "The other gates"),
  `@@ANSWER@@`, `@@REVIEW@@` and `@@CI@@`. "The other gates" is where the
  gates whose counts this work changes would show that they still pass:
  `PILOT_GRIDS` is read by the gates real-3a, real-5a and issue-31 too. At
  `10805f6` no run of them is recorded, and the reviewer did not run them
  (section "Not checked").
- docs/state/real.md is unchanged by the diff: it still lists F1 to F9 of
  real-3a as open and, as next, "Left: the two outputs of the vital signs,
  and the gate real-3 itself". `specfirst status` prints it.
- The report says the amendment has "points 1 to 12" (its lines 6 and 464);
  the ADR has 14. In ADR-003, point 13 runs on in the line of point 12
  ("...from the change.13. **The differences"), so the rendered list has no
  point 13.

### F6 (not blocking) Small things in the texts

- The comment of the four medians in gold/exceptions.yaml: "the owner's
  answer on them is recorded in ADR-003, amendment of real-3". It is not;
  point 13 says the owner was asked.
- The report, "What the checks do not cover": "Of the vital signs, 4
  results lie on a half up to floating error; they are the 4 medians", in
  an item that begins "printed by tests/defects on every run". Nothing in
  the gate log prints it (R1). And 5 more results of the vital signs lie
  exactly on a half at their displayed decimals (R10): three maxima 37.5
  under `XX`, among the 119; the median 36.75 and the third quartile 0.25,
  which the grids show as the example does ("36.8", " 0.3"). The 0.25 tells
  half away from zero from half to even on these grids; D14 does not plant
  the other rule.
- The report: the review page "has no script, handler, frame, image, form,
  style that imports, link outside itself or refresh (D13 plants each)". D13
  and `test_viewer.py` plant a script, a handler and a link that leaves the
  page. The check sees the other four kinds on the reviewer's plants (R7),
  but nothing in the repository plants them (rule R5).
- Answer (B): "0 of 1,562 results shown in the other grids". The reviewer
  finds 2,501 results with a number shown in the eight other grids, 1,559 of
  them held as floating-point numbers, and none changes under (B) (R10):
  1,562 is not reproduced, the conclusion is. "4 of 3,053 results of the
  example": 3,053 is the count of the example's ARD rows held as
  floating-point numbers; right.
- "would ... leave 9 differences where the example drops trailing zeros":
  under `XX.XX` for the observed values and `X.XX` for the changes the
  reviewer finds 10 (7 whole numbers and 3 with one decimal); under `XX.XX`
  for both, 64. 9 is not reproduced.
- The SAP's Templates 21 and 22 show "Min." `xx` and "Max." `xxx`, as the
  report says, but they list blood pressure and heart rate, not
  temperature, and the SAP says its templates "are for example only". For
  the 119 minima and maxima of temperature the direct support of the class
  is the example's own shells and the `resultPattern` `XX`.

## The seven questions

1. The gate. Each of the four statements is proven by a check that fails
   when it does not hold. "100% of numeric cells ... a complete path to
   SDTM variables": check 10 walks every cell of the five grids and fails on
   a numeric cell without ARD rows or with a gap, on an output not walked or
   with another count of cells (the unit test plants each), and now on any
   `computes` or `reads` edge that is not what the ARS file names (R8); the
   reviewer's own walk gives 3,815 of 3,815 (R5). "The graph build is
   deterministic": check 8, 72 of 72 files including the graph files, and
   R4. "The viewer opens from the file system with no network": check 14;
   it holds for the page that was built (R7), and the check passes three
   ways to fetch that it claims to refuse (F3). "The report walks one cell
   end to end": right in every line checked (R5). Check 12 (grids) holds
   what it compares, with F2 for what it does not.
2. F1 to F9 of real-3a are carried out as ADR-003 points 1 to 9 and the
   report say, and each new check fails on the reviewer's own plants: F1,
   the shell (R6: the labels of two rows exchanged, a section renamed,
   another text around the percent); F3, the percent of another row and a
   row in a second block refused (R6); F4, single `reads` and `computes`
   edges and a record of coverage.json (R8); F5, three other analyses with a
   wrong population: 0 quartiles or medians proven, 15, 1 and 2 without the
   question (R13); F6, the review's plants are refused, others are not (F3
   here); F8, by its unit test (read, not planted again); F9, the two Fisher
   vectors are the exact sums to the digit (R14) and `fisher-limit` is
   required by `junit_problems`. F2 is a message and a unit test with and
   without `columns.values`: as said. F7 is left open for the right reason:
   read-2a's kept dry run binds `display.pattern` by the SHA-256 of its
   canonical JSON (`harness/binding.py`, the kept `binding.json`), and
   either fix of F7 changes the text of that entry in registry.json.
3. The table-shell check holds what its docstring says on the three shells:
   0 problems on the controls; 9, 265 and 505 rows held; 8, 10 and 15 rows of
   the shells with cells, which is the reviewer's count of the shell texts.
   What passes that should not: the order of parts with one mask and the
   statistic behind a row's label (F2); in the vertical shell the order of
   the runs, and any heading against `< Visit n Change from Baseline >`;
   sections and visit rows against placeholders; a line of a shell counts as
   shown when any row has its label and masks, so in the vertical shell one
   run of five rows uses all three runs (a missing analysis is then seen by
   the comparison, not by the shell); the column of the header row.
4. The two grids are right: the reviewer's recount, from the ARS file and
   the two ARD files with its own reading of the shells and the patterns
   and none of the checking code, gives every row, label, section, column,
   ARD list and text of both grids with 0 problems, and 1,893, 119 and 4
   (R3). The layout is general within what ADR-003 points 10 to 12 say: two
   row groupings with defined groups, analyses of one method, `skip` by any
   group of either, `within` with header and by_groups blocks only. A
   `heading` given with `within` is accepted and not used.
5. The 119 entries `not_its_own_pattern` are each sound (R3): the example's
   text is its raw value with the data's decimals, its raw value under `XX`
   is our text, our raw value equals the example's, and they are exactly
   the minima and maxima of temperature that are not whole (the other 385 of
   504 are whole and agree). The class `reference_error` rests on the
   example's own shells and `resultPattern` (F6 on the SAP). The 4 entries
   `half_in_floating_error`: the check is narrow (R12); the proof kind does
   not show its class, and the facts given for it are wrong (F1).
6. Determinism: P1 72 of 72, and R4. Clean room: no PDF and no study data
   committed; the shells are pinned by SHA-256 and copied from the cache;
   the added lines hold no subject number, no byte outside ASCII and no
   Windows user path; what is quoted of the example is as in earlier work
   (R15). Scope: `PLAN.md`, `standard/` (and so `standard/schemas/` and
   `standard/methods/`), `env/`, `scripts/` and `CLAUDE.md` unchanged;
   nothing of real-4 (no CSR table of batch D1, no new result set).
7. The numbers of the report are right, checked against the logs, the
   reviewer's run and the reviewer's own counts, except where F1, F5 and F6
   say: the description of the four medians (F1), "points 1 to 12" (F5),
   1,562 and 9 (F6), and "printed by tests/defects" and "D13 plants each"
   (F6). Checked and right, among others: 1,263 numeric cells each, 2,019
   results, 63 and 4 cells, 3,815; 19 of 19 and 16 of 16; 72 and 64 files;
   681 and 881 lines; 1,443 and 1,454 passed, 37 and 38 deselected, 100 and
   101 defects tests; the table of the two grids (265, 6, 1,590, 1,263,
   2,019, 10; 505, 3, 1,515, 1,263, 2,019, 15); 1,056, 960, 1,056 and 96;
   1,893, 119 (59, 60) and 4; 504 and 385; the two SHA-256 of the shells;
   the hash lines of the new files; 5,597,006 bytes, 63 panels and 4,028
   cells; 31 analyses, 1,096 changes, 14; every line of the walk of
   `cell:Out14-3-3-1a/r10/c2`; 408; 3,053; the nine page plants of the
   unit test of F6 of real-3a.

## Not checked

- The clean-clone gate was not run again (it needs the network); R2 shows
  that the reviewer's gate on the same code gives its lines. The gate
  real-3a on `70dc552` was not run again; its log was read.
- The gates real-3a, real-5a and issue-31 at `10805f6` (F5). They are made
  of the same check functions on the same build as R1, with the constants
  that R1 passed (`PILOT_GRIDS`) or that this diff does not touch, and the
  planted defects they require ran in R1 (101 passed); so they would very
  likely pass, but there is no run.
- The pages in a browser.
- What the report says of times, of the question to the owner and of its
  cost (USD 0.6).
- Whether the example was computed from data other than the reference ADaM
  (F1 says what the repository shows).
- The shells of the demographics and of the table by organ class and term
  (RTF, not pinned); the unit tests beyond the changes listed; F2 and F8 of
  real-3a by a plant of the reviewer's (their unit tests were read).

Verdict: NOT SIGNED
