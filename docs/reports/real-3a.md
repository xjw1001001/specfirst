# real-3a Layout, grid and trace for the adverse event summary: report

Date: 2026-11-17. Branch: `track/real`. Part `real-3a` of ADR-005
(decision 1): the first part of real-3, for the unit `tfl-ae-summary`.
Depends on real-2 (passed).

## Verdict

The gate passed. `scripts/clean_clone_gate.sh real-3a` exited 0 on a clean
clone of commit `9730843`, after a fresh install and a fresh fetch: 16 of 16
checks. The complete output is in
`docs/reports/real-3a.clean-clone.gate.log` (455 lines); the section "The
clean-clone gate" quotes it.

It was the second run of the gate. For most of 2026-11-17 the Linux
environment of the machine reached no network, so nothing could be
installed or fetched. In that time `specfirst gate real-3a --clean` passed
on a clone of commit `0938fe4` with the environment and the fetch cache
that were already installed, 16 of 16 (`docs/reports/real-3a.gate.log`, 405
lines; the section "The gate" quotes that run in full). `9730843` adds
this report and two gate logs to `0938fe4` and changes nothing else. The
two runs built the same bytes: all 30 file hashes of P1 are equal.

The independent review (rule R7) is a PASS with nine findings that do not
block (section "Review"). One of them, F1, is a statement of fact in
ADR-003 and in this report that was wrong, and it is corrected: the table
shell the example names is in the pinned repository.

After the review `main` was merged into `track/real` (commit `26667ed`:
`catalog@1` of std-1, 10 files, none that real-3a changed), and
`scripts/clean_clone_gate.sh real-3a` exited 0 again on a clean clone of
that commit, 16 of 16 (`docs/reports/real-3a.merged.gate.log`, 455
lines; the section "The gate after the merge of main"). What follows
`26667ed` on the branch is documents only: the review, the corrections it
asked for, this report and the state file.

- 27 cells of the grid show 51 results. Every cell text equals the
  formatted values the example embeds; no difference had to be classified.
- All 27 cells print a number, and all 27 have a complete path to SDTM
  columns: through 51 ARD rows, 9 analyses and 15 ADaM columns (the 9 the
  analyses read and 6 behind them) to 15 SDTM columns.
- P1: 30 of 30 built files have the same SHA-256 in two builds; the grid,
  its mock shell, the two pages and the three graph files are among them.
- Everything the gate of real-2 checks is checked again: both engines
  reproduce 3,711 of the 3,735 embedded results with 0 unexplained and
  agree on all 4,238.
- The new checks failed on planted defects before they counted: D6 (proofs
  that prove nothing), D7 (the grid text) and D8 (the trace), and the unit
  tests of the layout, the grid, the page and the walk of the cells.

Five things are for the owner (ADR-003 says each in full): the layout is
our own format and tfrmt was read, not run; a count under a column header
is a cell of a row with the section `@header`, within grid schema version
0; the new registry entry `display.pattern` follows what the example's
formatted values show; the kit layout of section 8 has grown again; and
the comparison of grid text is per result, with the formatted values of the
example's ARS file; the example's table shell, which shows the cells, is
not yet held against the grid (review, F1).

## What real-3a asks for, and where it stands

| Item | State | Where |
| --- | --- | --- |
| The first commit: the findings F2 to F12 of the review of real-2; then `specfirst gate real-2` again | done: commit `bd34260`; the gate passed on a clone of it, 15 of 15 | section "The first commit" |
| ADR-003: own layout format or tfrmt JSON (rule R2, with the evidence) | done: our own format; tfrmt was read at a pinned commit and not run, its rounding was run in base R | `docs/decisions/ADR-003.md`; `evidence/adr003_rounding.sh` and `.out` |
| Layout spec v0, grid builder, mock shell and HTML renderer for the adverse event summary output of the ARS example; general code, limited by a list of outputs | done: `Out14-3-1-1`, listed under `outputs` in `kit.yaml`; no viewer | `specfirst.machine.layout`, `grid`, `render`; `kits/cdiscpilot01/gold/layout/Out14-3-1-1.yaml` |
| Compare every cell text of the grid with the example's `formattedValue`; a difference gets one class and its proof in the exceptions file | done: 27 cells show 51 results, all 27 are equal; no entry was needed | `grid.compare_reference`; gate check 12 |
| Complete the graph for the cells of this grid: every numeric cell reaches SDTM variables through ARD rows and ADaM columns | done: 27 of 27 cells, through 51 ARD rows, 9 analyses and 15 ADaM columns to 15 SDTM columns | `graph.add_displays`, `graph.check_cells`; gate check 10 |
| A gate `real-3a`: the environment first; everything the gate of real-2 checks; the cell texts; the paths; determinism; each new check failed on a planted defect first | done: 16 checks | `src/specfirst/gates.py`; section "The gate" |

`PLAN.md`, `standard/schemas/` and `env/` are not changed (`PLAN.md` has
the SHA-256 `234a642a...2e4c`, as in the report of real-2). Nothing of the
rest of real-3 is started. The folder of the track gen was not touched. In
the files both tracks edit, the changes are: one gate and two constants in
`gates.py`, three texts in `cli.py`, two lines of `CLAUDE.md` (59 lines),
five rows at the end of `docs/lessons.md` (the fifth, lesson 31, after the
review).

## The first commit: the findings F2 to F12

Commit `bd34260`. `docs/reports/real-2.review.md` has each finding in full.

| # | What was done | Where it is tested |
| --- | --- | --- |
| F2 | The check of the proofs is narrowed. `value_of_other_result`: the same analysis and operation in one other group of one grouping, and the exchange must hold in both directions. `same_under_every`, `no_alternative`: only for an option that changes some result of the same operation. `no_records`: one count of the cell's own groups for every group the test compares. New proof `between_equal_values`. | `tests/unit/test_results.py` (A3, A8 to A11 on the made-up study); `tests/defects` D6 on the kit's own entries |
| F3 | The R Fisher test gives a 2 x 2 table to `fisher.test` and sums over every table itself for a larger one; statements 5 and 6 say what holds for both implementations, statement 8 what `fisher.test` does. Two of the reviewer's tables are vectors; their expected values are those of the Python implementation, 9.2e-14 and 2.1e-13 from the sum in exact fractions and inside the 1e-12 of the test (the vectors' own note says "the sum in exact fractions": review of real-3a, F9). The build catches `MethodError`. | `tests/methods`: `fisher-r`, `fisher-limit` |
| F4 | The standard deviation of equal values is 0, decided by comparing the values, in both engines; statement 10 and two vectors. | `tests/methods` |
| F5 | R reads the hand-over without jsonlite's simplification; `json_string` escapes every control character; one rule for a number as a group value (rule I9) in both engines; a number in a condition is written as in JSON, and a value that is not text is a problem of the event (rule I3). | `tests/unit/test_rengine.py` |
| F6 | Test A6 asserts the rows of each of the 31 analyses. | `tests/pilot` A6 |
| F7 | Test A5 compares the R files of ours with the R files of every cached source; `json_string` is written anew, by code point. | `tests/pilot` A5 |
| F8 | ADR-002: the four sentences are reworded and marked "(real-3a)"; no decision is changed. | - |
| F9 | The entry of the first quartile of age says in its `sources` that the example has the average in 68 of 69 such quartiles and medians. The count was made again (below). | - |
| F10 | `README.md` lists std-1; the note on ars in `third_party/SOURCES.md` names what is quoted; rule I3 says what both engines do; "every quantile definition" is the two of the registry; the refusal of statement 6 is tested in R. | `fisher-limit` |
| F11 | D1 also exchanges the two arms in one analysis, for five analyses. Both engines are tested on 13 cases of rule I3 and on seven texts that are not a number. | `tests/defects` D1; `tests/unit/test_rengine.py` |
| F12 | `results.py` and the registry README say that the allowance of 1e-9 also covers a reference value rounded to ten digits. | - |

Two things the fix of F2 found that the review did not:

- The review says that none of the 25 committed entries uses the holes. One
  did. The median of height (embedded 162.2, ours 162.6) was "the same
  under every quantile definition", and the two definitions of the registry
  never differ on a median (statement 9 of `summary.continuous`). The
  narrowed check refuses that proof. The entry now has the proof
  `between_equal_values`: every definition of a sample quantile in Hyndman
  and Fan (1996) puts the median of 84 values between the 41st and the 43rd
  sorted value, and these are all 162.6. The class is unchanged.
- The fix as the review words it leaves the review's own case A3 open: the
  placebo arm is "one other group of the same analysis and operation" too,
  and it has the embedded value by coincidence. An exchange is now proven in
  both directions: the reference's value of the named result must be our
  value of this one.

What was left as it was: three rows of the table of F5 that are floating
arithmetic at its limits (the engines differ there and rule R11 stops the
build); F1, the choice in F8 and the classes in F9, which are the owner's.

The count for F9, made again with a script of this session on the built
data (not committed; it uses `Engine.cell_values`):

```text
embedded quartiles and medians where n p is whole and the two neighbours differ: 69
  the reference has the average: 68 ; the lower value alone: 1 ; neither: 0
```

The planted proofs (test D6; lines 321 to 327 of the gate log of real-3a, which
runs the same test):

```text
A3 an exchanged count, proven by the placebo arm, which has the same value: check passes: False; the proof (value_of_other_result) does not hold: the reference's value of ard:An03_04_Ethnic_Summ_ByTrt/Mth01_CatVar_Summ_ByGrp_1_n/AnlsGrouping_01_Trt_1/AnlsGrouping_05_Ethnic_1 (3) is not our value of this result (6): the two are not exchanged
A8 the quartile of age, by an option with one value: check passes: False; the proof (no_alternative) does not hold: no value of sd_denominator changes a result of the operation Mth02_ContVar_Summ_ByGrp_5_Q1: the option says nothing about this result
A9 an exchanged mean, as the same under every quantile definition: check passes: False; the proof (same_under_every) does not hold: no value of quantile_definition changes a result of the operation Mth02_ContVar_Summ_ByGrp_2_Mean: the option says nothing about this result
A10 the same mean, as given by no quantile definition: check passes: False; the proof (no_alternative) does not hold: no value of quantile_definition changes a result of the operation Mth02_ContVar_Summ_ByGrp_2_Mean: the option says nothing about this result
A11 no records, by a count of 0 of another analysis: check passes: False; the proof (no_records) does not hold: ard:An03_05_Race_Summ_ByTrt/Mth01_CatVar_Summ_ByGrp_1_n/AnlsGrouping_01_Trt_1/AnlsGrouping_04_Race_1 is not a count of the cell's own groups in one group of AnlsGrouping_01_Trt
no records, by the count of one of the two compared arms: check passes: False; the proof (no_records) does not hold: the counts are for the groups AnlsGrouping_01_Trt_1 of AnlsGrouping_01_Trt; the test compares AnlsGrouping_01_Trt_1, AnlsGrouping_01_Trt_2: one count per compared group is needed
the median of height, as the same under every quantile definition: check passes: False; the proof (same_under_every) does not hold: no value of quantile_definition changes a result of the operation Mth02_ContVar_Summ_ByGrp_4_Median: the option says nothing about this result
```

The Fisher test on the two tables of the review where `fisher.test` is
looser than the registry (test `fisher-r`; lines 86 to 88 of the same log):

```text
2 x 3 2 x 3 with one table a relative 2.7e-07 more probable:  Python 0.06040878692449231    R 0.060408786924501114   fisher.test 0.06533690837383269  (a table 2.666e-07 more probable)
2 x 3 2 x 3 with one table a relative 3.2e-07 more probable:  Python 0.009798846806875698   R 0.009798846806877703   fisher.test 0.011455024125087577  (a table 3.209e-07 more probable)
tables larger than 2 x 2: 10; with a table just above the observed probability, where fisher.test is looser: 2
```

### The gate of real-2 again

Run in Ubuntu 24.04 under WSL2 as root, on a clone of `bd34260` in the
Linux file system, with the installed environment and the existing fetch
cache (the section "The gate" describes this kind of run). The complete
output is in `docs/reports/real-3a.real-2.gate.log` (358 lines).

```text
$ git clone --quiet --no-local /mnt/d/trial_work/specfirst/.git /root/scratch/real3a/clone-bd34260
$ git -C /root/scratch/real3a/clone-bd34260 checkout --quiet --detach bd34260
$ cd /root/scratch/real3a/clone-bd34260 && PYTHONPATH=$PWD/src python -u -m specfirst gate real-2 --clean
gate real-2 at commit bd342607acf0e6bad5fd08b8662b0a41e0f98145 (clean)
[...]
693 passed, 20 deselected in 65.12s (0:01:05)
[...]
P1 determinism: 26 of 26 files have the same SHA-256 in both builds
[...]
TOTAL cells=9119605 mismatched=0
[...]
trace: complete
[...]
results common-safety-displays, Python engine: 0 unexplained
[...]
results common-safety-displays, R engine: 0 unexplained
[...]
results common-safety-displays, engines: 4238 results in both, 0 disagree; largest relative difference 2.4e-13 (allowed 1e-09)
results: pass
[...]
compared 76 Python files of ours with 673 of p7, yamaa, p6, ars; the most lines a file that is not recorded shares: 1 (allowed: 2)
compared 5 R files of ours with 827 of 13 cached sources; the most lines a file that is not recorded shares: 2 (allowed: 2)
[...]
rows per analysis: 31 analyses, 4238 rows; expected 31 analyses, 4238 rows
[...]
PASS  environment          0.6 s
PASS  pins                 0.4 s
PASS  lint                 0.1 s
PASS  registry             0.0 s
PASS  unit tests          65.8 s
PASS  method vectors       2.1 s
PASS  kit                  0.1 s
PASS  P1 determinism      51.4 s
PASS  P2 reproduction      0.7 s
PASS  trace                1.4 s
PASS  results              4.6 s
PASS  pilot tests         81.0 s
PASS  planted defects     87.2 s
PASS  cache untouched      0.1 s
PASS  ASCII                0.0 s
GATE real-2: PASS
```

## ADR-003 in short

The layout is our own format, not tfrmt's JSON. tfrmt was read at commit
`8feb95a` of its public repository; it was not installed or run, because it
is not among the locked R packages and the Linux environment had no network
on the day. Five reasons, each in the ADR: tfrmt's result has no link from
a cell to the ARD rows in it; it rounds by R's `round` and has no option;
its JSON is R code in text, and the builder, the compiler and the scorer
are Python; its input is not an ARS result set, so the mapping a layout
holds is needed either way; the JSON has no schema and no version.

One claim was run without tfrmt (`evidence/adr003_rounding.out`):

```text
$ bash evidence/adr003_rounding.sh /root/scratch/real3a/b1 /root/scratch/real3a/adr003
results of the pilot with a value and a pattern with decimals: 2537 of 4238
R 4.6.2 : format(round(x, digits), nsmall = digits) on 2537 values
values that lie exactly on a half at their displayed decimals: 3
values that R's round shows as another number than half away from zero: 2
  of them the example formats: 2; its text is ours for 2, R's for 0
  ard:An03_06_Height_Summ_ByTrt/Mth02_ContVar_Summ_ByGrp_6_Q3/AnlsGrouping_01_Trt_3: value 172.85: half away 172.9, R 172.8, the example '172.9'
  ard:An08_02_ChgBl_Summ_ByTrt/Mth02_ContVar_Summ_ByGrp_6_Q3/AnlsGrouping_01_Trt_3/AnlsGrouping_08_Param_4/AnlsGrouping_09_Visit_05: value 0.25: half away 0.3, R 0.2, the example ' 0.3'
not counted: 4 small values that format() writes with an exponent when it is given one value at a time
```

The lines of tfrmt that the ADR quotes were read twice: through a summary
of each file, and then as the text of the raw files at that commit (the
line with `round(vals, dig)`, the lines with `as_label`, `deparse`,
`str2lang`, `parse_expr` and `as.formula` in `R/JSON.R`, `validate_cols_match`
and `@noRd` in `R/apply_tfrmt.R`).

## The grid

The layout, `kits/cdiscpilot01/gold/layout/Out14-3-1-1.yaml`, without its
comment:

```yaml
layout: 0
output: Out14-3-1-1
columns:
  grouping: AnlsGrouping_01_Trt
rows:
  - kind: header
    cell: "{N}"
    parts:
      N: {analysis: An01_05_SAF_Summ_ByTrt, operation: Mth01_CatVar_Count_ByGrp_1_n}
  - kind: analyses
    cell: "{n} {pct}"
    parts:
      n: {operation: Mth01_CatVar_Summ_ByGrp_1_n}
      pct: {operation: Mth01_CatVar_Summ_ByGrp_2_pct}
    analyses:
      - An07_01_TEAE_Summ_ByTrt
      - An07_02_RelTEAE_Summ_ByTrt
      - An07_03_SerTEAE_Summ_ByTrt
      - An07_04_RelSerTEAE_Summ_ByTrt
      - An07_05_TEAELd2Dth_Summ_ByTrt
      - An07_06_RelTEAELd2Dth_Summ_ByTrt
      - An07_07_TEAELd2DoseMod_Summ_ByTrt
      - An07_08_TEAELd2TrtDsc_Summ_ByTrt
```

Titles, footnotes, the header of the row labels, the labels of the rows,
the names of the columns and the three patterns ("(N=XX)", "XXX",
"( XX.X)") are taken from the ARS file. The grid of the build, as text
(`gold/grid/Out14-3-1-1.json`; the first row has the section `@header`):

```text
Table 14.3.1.<x>.<y>
Overall Summary of Treatment-Emergent Adverse Events
Safety Population

                                           Placebo     Xanomeline Low Dose  Xanomeline High Dose
Categories, n (%)                          (N=86)      (N=84)               (N=84)
TEAE                                       65 ( 75.6)  77 ( 91.7)           76 ( 90.5)
Related TEAE                               43 ( 50.0)  72 ( 85.7)           70 ( 83.3)
Serious TEAE                               0 (  0.0)   1 (  1.2)            2 (  2.4)
Related Serious TEAE                       0 (  0.0)   1 (  1.2)            1 (  1.2)
TEAE Leading to Death                      2 (  2.3)   1 (  1.2)            0 (  0.0)
Related TEAE Leading to Death              1 (  1.2)   0 (  0.0)            0 (  0.0)
TEAE Leading to Dose Modification [a]      0 (  0.0)   0 (  0.0)            0 (  0.0)
TEAE Leading to Treatment Discontinuation  0 (  0.0)   0 (  0.0)            0 (  0.0)

Note: TEAE=Treatment-Emergent Adverse Events.
[a] Dose Modification includes Dose Reduced; Drug Interrupted in the AE action taken with study treatment.
```

The mock shell (`gold/grid/Out14-3-1-1.shell.json`) is the same grid with
"(N=xx)" in the header row and "xxx ( xx.x)" in the 24 other cells; its
cells name the same ARD rows. Each of the two has a page in `gold/out/`:
one HTML file without a script, a link or a date.

## The gate

Gate text of ADR-005 for real-3a: every cell text equals the example's
`formattedValue` or has one classified difference. Every numeric cell of
the grid has a complete path to SDTM variables. The build is deterministic.
The task adds: the environment check first; everything the gate of real-2
checks; each new check has failed on a planted defect before it counts.

The gate has sixteen checks: the fifteen of real-2, by the same functions,
and check 12, the grids.

| Statement | Check | It fails when |
| --- | --- | --- |
| The environment first | 1 | `specfirst doctor` finds drift from the lock files |
| Everything the gate of real-2 checks | 2 to 11, 13 to 16 | as in real-2; the planted defects are now D1 to D8 |
| Every cell text equals `formattedValue` or has one classified difference | 12 | a cell differs without a class; the kit builds another set of outputs than the gate names; the grid has other than 27 cells and 51 results; a result has no formatted value to compare with; the grid file is not what the layout and the ARD give; the rows of the R engine give another grid; the shell or a page does not hold |
| Every numeric cell has a complete path to SDTM variables | 10 | a cell that prints a digit shows no ARD row; a step of the walk has no edge or no node; a column on the way has a gap; no SDTM column is reached; `coverage.json` disagrees with the graph files |
| The build is deterministic | 8 | one of the 30 built files differs between two builds in two folders |
| Each new check failed on a planted defect | 5 and 14 | a planted defect passes: the unit tests of `test_grid.py`, `test_cells_trace.py` and `test_gates.py`, and D6 to D8 on the pilot |

Command, run in Ubuntu 24.04 under WSL2 as root:

```text
$ git clone --quiet --no-local /mnt/d/trial_work/specfirst/.git /root/scratch/real3a/clone-0938fe4
$ git -C /root/scratch/real3a/clone-0938fe4 checkout --quiet --detach 0938fe4
$ cd /mnt/d/trial_work/specfirst-real && . scripts/env.sh
$ cd /root/scratch/real3a/clone-0938fe4
$ export PYTHONPATH=$PWD/src PYTHONDONTWRITEBYTECODE=1
$ flock /run/lock/specfirst-heavy.lock python -u -m specfirst gate real-3a --clean
```

`0938fe4` was the HEAD of `track/real`. The clone is on the Linux file
system. The Python environment is the one installed for the worktree
(`specfirst` itself is taken from the clone through `PYTHONPATH`), the R
library and the fetch cache are the shared ones under
`/root/.local/share/specfirst`. Nothing was installed or fetched for this
run: that is what the clean-clone gate adds; it ran later the same day
(section "The clean-clone gate"). The `flock` keeps heavy runs of the
sessions on this machine apart.

Output. Lines are quoted as printed from `docs/reports/real-3a.gate.log`
(405 lines). `[...]` marks where lines of the log are left out: the lines
of `specfirst doctor`, the pin listings, the registry listing, pytest's
progress dots, the ten lines of the test `fisher-r` for its ten tables (the
last two are quoted above), 23 of the 30 hash lines of P1, the per-dataset lines of P2, of the trace
and of the claims, 16 lines of check 11 (for each engine the lines on the
result that agrees only as printed and on the two results at the edge; the
four `explained` lines of the R engine, which are those of the Python
engine; the line on the 504 results the reference does not list and the
line on the ARS file with our results), the tests A1 to A4, and the tests
D2 to D6 (D6 is quoted above).

```text
gate real-3a at commit 0938fe4e3bef90b0a47762acc9b4c1ea9b731123 (clean)

== [1/16] environment: specfirst doctor
[...]
doctor: ok
-- PASS environment (0.3 s)

== [2/16] pins: specfirst fetch --verify
cache: /root/.local/share/specfirst/cache
[...]
fetch: every pin verified
-- PASS pins (0.1 s)

== [3/16] lint: ruff check .
All checks passed!
-- PASS lint (0.1 s)

== [4/16] registry: specfirst methods
[...]
methods: 8 entries
-- PASS registry (0.0 s)

== [5/16] unit tests: pytest -m "not evidence" -q
[...]
775 passed, 22 deselected in 53.02s
-- PASS unit tests (53.6 s)

== [6/16] method vectors: SPECFIRST_STRICT=1 pytest tests/methods -s -q

--- python-vectors
Python implementations: 99 cases of 8 methods, 0 differences
.
--- r-vectors
R implementations: 64 cases of 6 methods, 0 differences
.
--- exact-arithmetic
expected values computed again in exact arithmetic: 64 cases, 0 differences; written by hand: 35 cases (the display rules)
.
--- fisher-r
[...]
tables larger than 2 x 2: 10; with a table just above the observed probability, where fisher.test is looser: 2
.
--- fisher-limit
R, with a limit of 50 tables: the R vectors run exited 1: Error: test.fisher.exact: more than 50 tables to sum; the method does not approximate
..
6 passed in 1.33s
-- PASS method vectors (1.6 s)

== [7/16] kit: specfirst kit assemble cdiscpilot01
study data in git (E20): 387 maintained files checked, 0 problems
kit cdiscpilot01: 66 files match their pinned SHA-256 (26 inputs, 40 gold) in /root/scratch/real3a/clone-0938fe4/build/kits/cdiscpilot01
-- PASS kit (0.1 s)

== [8/16] P1 determinism: specfirst check cdiscpilot01 --twice (its first part)
build into build/p1/cdiscpilot01/first: exit 0 (build cdiscpilot01: 10 datasets, 892 nodes, 4153 edges, 30 files in /root/scratch/real3a/clone-0938fe4/build/p1/cdiscpilot01/first)
build into build/p1/cdiscpilot01/second: exit 0 (build cdiscpilot01: 10 datasets, 892 nodes, 4153 edges, 30 files in /root/scratch/real3a/clone-0938fe4/build/p1/cdiscpilot01/second)
[...]
same      9089c86643646467 9089c86643646467 gold/graph/coverage.json
same      9963981263e837e6 9963981263e837e6 gold/graph/edges.jsonl
same      c5b9582b6f2f3870 c5b9582b6f2f3870 gold/graph/nodes.jsonl
same      978c9e2977e3f5fc 978c9e2977e3f5fc gold/grid/Out14-3-1-1.json
same      2ac2586e11fbb636 2ac2586e11fbb636 gold/grid/Out14-3-1-1.shell.json
same      e9db6ca3f5d7ce63 e9db6ca3f5d7ce63 gold/out/Out14-3-1-1.html
same      41c207f1d512d596 41c207f1d512d596 gold/out/Out14-3-1-1.shell.html
[...]
P1 determinism: 30 of 30 files have the same SHA-256 in both builds
-- PASS P1 determinism (37.4 s)

== [9/16] P2 reproduction: specfirst check cdiscpilot01 --build build/p1/cdiscpilot01/first (its second part)
[...]
TOTAL cells=9119605 mismatched=0
[...]
P2 reproduction: 10 of 10 datasets equal their reference (numeric tolerance 1e-10)
-- PASS P2 reproduction (0.5 s)

== [10/16] trace: specfirst check cdiscpilot01 --build build/p1/cdiscpilot01/first (its third part)
[...]
TOTAL         415     413      14       2     0
[...]
nodes: L0 279, L3 111, L4 415, L5 9, L6 51, L7 27
edges: cites 706, computes 75, derives_from 3269, reads 52, shows 51
cites edges: 706 imported, 0 with a verified quote, 0 approved by a person
[...]
grid Out14-3-1-1: 27 cells, 27 print a number; 27 of the 27 cells with results have a complete path to SDTM columns
  through 51 ARD rows, 9 analyses, 15 ADaM columns, to 15 SDTM columns
trace: complete
-- PASS trace (1.0 s)

== [11/16] results: specfirst check cdiscpilot01 --build build/p1/cdiscpilot01/first (its fourth part)
ARS schema (gold/spec/ars/ars_ldm.schema.json): gold/spec/ars/common-safety-displays.json fits; gold/ars/common-safety-displays.json fits
results common-safety-displays, Python engine: 3735 embedded results, 3711 reproduced as printed, 23 with another value, 1 without a result of ours
[...]
  explained:   1 reference_error, proof between_equal_values
  explained:   1 reference_error, proof no_alternative
  explained:   1 reference_error, proof no_records
  explained:  22 reference_error, proof value_of_other_result
results common-safety-displays, Python engine: 0 unexplained
results common-safety-displays, R engine: 3735 embedded results, 3711 reproduced as printed, 23 with another value, 1 without a result of ours
[...]
results common-safety-displays, R engine: 0 unexplained
[...]
results common-safety-displays, engines: 4238 results in both, 0 disagree; largest relative difference 2.4e-13 (allowed 1e-09)
results: pass
-- PASS results (3.1 s)

== [12/16] grids: specfirst check cdiscpilot01 --build build/p1/cdiscpilot01/first (its last part)
grid Out14-3-1-1: 27 cells show 51 results; 27 cells equal the reference's formatted values, 0 differ, 0 of them with one class
grid Out14-3-1-1: the R engine's rows give the same grid; the mock shell and the two pages hold; 0 problems
grids: 1 outputs, pass
-- PASS grids (2.1 s)

== [13/16] pilot tests: SPECFIRST_STRICT=1 pytest tests/pilot -s -q
[...]
--- A5-adapted
recorded as adapted: src/specfirst/machine/lineage.py shares 73 lines with cached sources
recorded as adapted: src/specfirst/machine/runner.py shares 3 lines with cached sources
compared 82 Python files of ours with 673 of p7, yamaa, p6, ars; the most lines a file that is not recorded shares: 1 (allowed: 2)
compared 5 R files of ours with 827 of 13 cached sources; the most lines a file that is not recorded shares: 2 (allowed: 2)
.
--- A6-engine
Python engine: 31 analyses on 23 columns of ADAE, ADSL, ADVS: 4238 rows in 0.45 s (the spike: about 3 minutes; the target: under 10 seconds)
embedded results: 3735; reproduced as printed: 3711
rows per analysis: 31 analyses, 4238 rows; expected 31 analyses, 4238 rows
.
6 passed in 53.33s
-- PASS pilot tests (53.7 s)

== [14/16] planted defects: SPECFIRST_STRICT=1 pytest tests/defects -s -q

--- D1-arms
unchanged: 3711 of 3735 reproduced, 25 explained, check passes: True
low and high dose exchanged: check passes: False; 1836 of 3735 reproduced; 1898 other values, of which 1896 are our value of the other arm
entries with the proof value_of_other_result that are reproduced now: 22 of 22
low and high dose exchanged in An03_03_Sex_Summ_ByTrt only: 8 values change; check passes: False; unexplained 8, of which stale entries 0; against the other engine 8 disagree
low and high dose exchanged in An03_01_Age_Summ_ByTrt only: 12 values change; check passes: False; unexplained 12, of which stale entries 0; against the other engine 12 disagree
low and high dose exchanged in An07_03_SerTEAE_Summ_ByTrt only: 4 values change; check passes: False; unexplained 4, of which stale entries 0; against the other engine 4 disagree
low and high dose exchanged in An08_01_Obs_Summ_ByTrt only: 600 values change; check passes: False; unexplained 31, of which stale entries 0; against the other engine 600 disagree
low and high dose exchanged in An03_04_Ethnic_Summ_ByTrt only: 8 values change; check passes: False; unexplained 8, of which stale entries 8; against the other engine 8 disagree
.
[...]
--- D7-display
grid Out14-3-1-1: 27 cells show 51 results; 27 cells equal the reference's formatted values, 0 differ, 0 of them with one class
layout, the percent under the pattern (XX.X), without the blank: 24 cells differ, 24 problems
layout, the percent with two decimals: 24 cells differ, 24 problems
layout, the count with one decimal: 24 cells differ, 24 problems
layout, the header count without its brackets: 3 cells differ, 3 problems
layout, the percent in place of the count: 24 cells differ, 48 problems
layout, the last row left out: 0 cells differ, 6 problems
layout, the header left out: 0 cells differ, 3 problems
layout, the first two rows in the other order: 0 cells differ, 1 problems
results, low and high dose exchanged in An07_01_TEAE_Summ_ByTrt: 2 cells differ, 2 problems
results, every percent of the first row with the placebo arm as its denominator: 2 cells differ, 2 problems
grid file, a text changed: 1 problems, for example: cell:Out14-3-1-1/r2/c1: the text '66 ( 76.7)' is not what the layout and the ARD give
grid file, the texts of two cells of a row exchanged: 2 problems, for example: cell:Out14-3-1-1/r2/c1: the text '76 ( 90.5)' is not what the layout and the ARD give
grid file, the cells of a row in another order: 1 problems, for example: row r2: its cells are not one per column, in order
grid file, the ARD rows of a cell taken from the next row: 1 problems, for example: cell:Out14-3-1-1/r2/c1: its ARD rows are not those the layout shows there
not separable by this reference: the percent before the count: 0 problems (it formats results, not cells)
not separable on these data: the rounding rule; results of the output that lie on a half at their displayed decimals: 0 of 51
.
--- D8-trace
grid Out14-3-1-1: 27 cells, 27 print a number; 27 of the 27 cells with results have a complete path to SDTM columns
  through 51 ARD rows, 9 analyses, 15 ADaM columns, to 15 SDTM columns
shows: 51 results changed one at a time, 4187 results without a shows edge changed at once; 0 problems
reads: 9 analyses; for each, the columns without a reads edge emptied and rolled (310 changes of a column in all), then the columns it reads emptied; 0 problems
reads: 9 analyses; for each, the columns without a reads edge emptied and rolled (312 changes of a column in all), then the columns it reads emptied; 2 problems
planted, the reads edge from An07_01_TEAE_Summ_ByTrt to ADAE.TRTEMFL left out (1 edges): 2 problems, for example: ars:An07_01_TEAE_Summ_ByTrt: with the 19 columns it has no reads edge to emptied, 6 of its 6 results change, for example ard:An07_01_TEAE_Summ_ByTrt/M
shows: 51 results changed one at a time, 4189 results without a shows edge changed at once; 3 problems
planted, the shows edges of cell:Out14-3-1-1/r2/c1 left out (2 edges): 3 problems, for example: ard:An07_01_TEAE_Summ_ByTrt/Mth01_CatVar_Summ_ByGrp_1_n/AnlsGrouping_01_Trt_1: changing it changes the cells ['cell:Out14-3-1-1/r2/c1']; its shows edg
planted in the files, a result node left out: 2 problems
planted in the files, every computes edge left out: 52 problems
planted in the files, every reads edge left out: 103 problems
[...]
59 passed in 70.58s (0:01:10)
-- PASS planted defects (71.0 s)

== [15/16] cache untouched: specfirst fetch --verify
cache: /root/.local/share/specfirst/cache
[...]
fetch: every pin verified
-- PASS cache untouched (0.1 s)

== [16/16] ASCII: python -m specfirst.asciicheck
ASCII check: 387 files checked, 0 with non-ASCII bytes
-- PASS ASCII (0.0 s)

PASS  environment          0.3 s
PASS  pins                 0.1 s
PASS  lint                 0.1 s
PASS  registry             0.0 s
PASS  unit tests          53.6 s
PASS  method vectors       1.6 s
PASS  kit                  0.1 s
PASS  P1 determinism      37.4 s
PASS  P2 reproduction      0.5 s
PASS  trace                1.0 s
PASS  results              3.1 s
PASS  grids                2.1 s
PASS  pilot tests         53.7 s
PASS  planted defects     71.0 s
PASS  cache untouched      0.1 s
PASS  ASCII                0.0 s
GATE real-3a: PASS
```

Check 14 runs the folder `tests/defects`: the eight tests D1 to D8 and the
51 of std-1's checkers. The second `reads:` and the second `shows:` line of
D8 are the two planted cases: the same check, on the edges of the graph
with one edge left out, finds 2 and 3 problems.

## The clean-clone gate

After the network was back. Command, run in Ubuntu 24.04 under WSL2 as
root, in the worktree of `track/real` (`taskset` holds the fresh install to
four processors; the `flock` keeps heavy runs of the sessions apart):

```text
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 bash scripts/clean_clone_gate.sh real-3a /mnt/d/trial_work/specfirst/.git 9730843
```

`9730843` was the HEAD of `track/real`. The script clones the repository
with `git clone --no-local` into a new folder under `/tmp`, checks out the
commit, puts the Python environment, the R library and the fetch cache of
the clone under the same new folder, and runs `env/install.sh`,
`specfirst fetch` and `specfirst gate real-3a --clean`.

Output, from `docs/reports/real-3a.clean-clone.gate.log` (455 lines).
`[...]` marks where lines are left out: the three git commands with the
commit line they print, the lines of `specfirst doctor`, the pin listings,
and everything of the gate between its first line and its summary but for
the lines shown. Those lines are the lines of the run quoted above, apart
from seconds, folders and the count of maintained files (390, with this
report and the two logs, where the first run had 387).

```text
clean clone gate real-3a
repository: /mnt/d/trial_work/specfirst/.git
commit:     9730843
clone:      /tmp/specfirst-clean-iARXrv/specfirst
environment and cache: /tmp/specfirst-clean-iARXrv/env
[...]
$ bash env/install.sh
python environment: /tmp/specfirst-clean-iARXrv/env/venv-specfirst-21289105
R library: /tmp/specfirst-clean-iARXrv/env/r-lib
R packages: 99 wanted, 99 to install from https://packagemanager.posit.co/cran/__linux__/noble/2026-11-10
R library matches the lock: 99 packages in /tmp/specfirst-clean-iARXrv/env/r-lib
[...]
doctor: ok

$ specfirst fetch
cache: /tmp/specfirst-clean-iARXrv/env/cache
ok   p7              fetched  213cb6ab3adc51abe4295cbbc546c0e6d46c3df8  (RConsortium/submissions-pilot7-synthetic-data)
[...]
fetch: every pin verified

$ specfirst gate real-3a --clean
gate real-3a at commit 973084376618c487cd98902aa5cd8b8153ea8983 (clean)
[...]
775 passed, 22 deselected in 41.30s
[...]
P1 determinism: 30 of 30 files have the same SHA-256 in both builds
[...]
TOTAL cells=9119605 mismatched=0
[...]
grid Out14-3-1-1: 27 cells, 27 print a number; 27 of the 27 cells with results have a complete path to SDTM columns
  through 51 ARD rows, 9 analyses, 15 ADaM columns, to 15 SDTM columns
trace: complete
[...]
results common-safety-displays, Python engine: 0 unexplained
[...]
results common-safety-displays, R engine: 0 unexplained
[...]
results common-safety-displays, engines: 4238 results in both, 0 disagree; largest relative difference 2.4e-13 (allowed 1e-09)
results: pass
[...]
grid Out14-3-1-1: 27 cells show 51 results; 27 cells equal the reference's formatted values, 0 differ, 0 of them with one class
grid Out14-3-1-1: the R engine's rows give the same grid; the mock shell and the two pages hold; 0 problems
grids: 1 outputs, pass
[...]
59 passed in 51.90s
[...]
ASCII check: 390 files checked, 0 with non-ASCII bytes
-- PASS ASCII (0.0 s)

PASS  environment          0.2 s
PASS  pins                 1.0 s
PASS  lint                 0.0 s
PASS  registry             0.0 s
PASS  unit tests          41.6 s
PASS  method vectors       1.1 s
PASS  kit                  0.1 s
PASS  P1 determinism      32.4 s
PASS  P2 reproduction      0.3 s
PASS  trace                0.9 s
PASS  results              2.8 s
PASS  grids                1.8 s
PASS  pilot tests         45.6 s
PASS  planted defects     52.1 s
PASS  cache untouched      0.1 s
PASS  ASCII                0.0 s
GATE real-3a: PASS

clean clone gate real-3a: PASS (clone kept in /tmp/specfirst-clean-iARXrv/specfirst until /tmp is cleared)
```

The 30 hash lines of P1 in this log are those of the first run, file by
file: a fresh environment and a fresh fetch give the same grid, shell,
pages and graph.

## The gate after the merge of main

`main` moved while the review ran: std-1 merged `catalog@1` (`f560171`).
It was merged into `track/real` as `26667ed`. The merge changes 10 files:
the catalog and its README, two files of the house standard, two lines of
`src/specfirst/compile/overview.py`, and five documents of std-1. None is a
file that real-3a changed. Because the unit tests of the gate read the
catalog, the gate was run again on the result, as before:

```text
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 bash scripts/clean_clone_gate.sh real-3a /mnt/d/trial_work/specfirst/.git 26667ed
```

Output, from `docs/reports/real-3a.merged.gate.log` (455 lines);
`[...]` marks where lines are left out, the same kinds of lines as in the
section before:

```text
clean clone gate real-3a
repository: /mnt/d/trial_work/specfirst/.git
commit:     26667ed
clone:      /tmp/specfirst-clean-dl9nUb/specfirst
environment and cache: /tmp/specfirst-clean-dl9nUb/env
[...]
$ bash env/install.sh
[...]
R packages: 99 wanted, 99 to install from https://packagemanager.posit.co/cran/__linux__/noble/2026-11-10
R library matches the lock: 99 packages in /tmp/specfirst-clean-dl9nUb/env/r-lib
[...]
doctor: ok

$ specfirst fetch
[...]
fetch: every pin verified

$ specfirst gate real-3a --clean
gate real-3a at commit 26667edce111e257b17e16ee349bc706e723be48 (clean)
[...]
775 passed, 22 deselected in 41.52s
[...]
P1 determinism: 30 of 30 files have the same SHA-256 in both builds
[...]
TOTAL cells=9119605 mismatched=0
[...]
grid Out14-3-1-1: 27 cells, 27 print a number; 27 of the 27 cells with results have a complete path to SDTM columns
  through 51 ARD rows, 9 analyses, 15 ADaM columns, to 15 SDTM columns
trace: complete
[...]
results common-safety-displays, Python engine: 0 unexplained
[...]
results common-safety-displays, R engine: 0 unexplained
[...]
results common-safety-displays, engines: 4238 results in both, 0 disagree; largest relative difference 2.4e-13 (allowed 1e-09)
results: pass
[...]
grid Out14-3-1-1: 27 cells show 51 results; 27 cells equal the reference's formatted values, 0 differ, 0 of them with one class
grid Out14-3-1-1: the R engine's rows give the same grid; the mock shell and the two pages hold; 0 problems
grids: 1 outputs, pass
[...]
grid Out14-3-1-1: 27 cells show 51 results; 27 cells equal the reference's formatted values, 0 differ, 0 of them with one class
[...]
grid Out14-3-1-1: 27 cells, 27 print a number; 27 of the 27 cells with results have a complete path to SDTM columns
  through 51 ARD rows, 9 analyses, 15 ADaM columns, to 15 SDTM columns
[...]
59 passed in 54.09s
[...]
ASCII check: 392 files checked, 0 with non-ASCII bytes
[...]
PASS  environment          0.2 s
PASS  pins                 0.7 s
PASS  lint                 0.0 s
PASS  registry             0.0 s
PASS  unit tests          41.8 s
PASS  method vectors       1.1 s
PASS  kit                  0.1 s
PASS  P1 determinism      31.3 s
PASS  P2 reproduction      0.3 s
PASS  trace                0.8 s
PASS  results              2.7 s
PASS  grids                1.9 s
PASS  pilot tests         45.2 s
PASS  planted defects     54.3 s
PASS  cache untouched      0.1 s
PASS  ASCII                0.0 s
GATE real-3a: PASS

clean clone gate real-3a: PASS (clone kept in /tmp/specfirst-clean-dl9nUb/specfirst until /tmp is cleared)
```

Of the 30 hash lines of P1 in this log, 30 are those of the run at `9730843`: the merge
changed nothing that a build of the pilot reads.

## One cell, end to end

`cell:Out14-3-1-1/r2/c1`, the row "TEAE" under "Placebo", walked from
`nodes.jsonl`, `edges.jsonl` and `coverage.json` of the first build of the
gate by a script of this session (not committed; it reads the three files
and nothing else):

```text
cell:Out14-3-1-1/r2/c1  text '65 ( 75.6)'  (gold/grid/Out14-3-1-1.json:1)
  shows    ard:An07_01_TEAE_Summ_ByTrt/Mth01_CatVar_Summ_ByGrp_1_n/AnlsGrouping_01_Trt_1  (gold/ard/common-safety-displays.jsonl:150)
    computes ars:An07_01_TEAE_Summ_ByTrt
  shows    ard:An07_01_TEAE_Summ_ByTrt/Mth01_CatVar_Summ_ByGrp_2_pct/AnlsGrouping_01_Trt_1  (gold/ard/common-safety-displays.jsonl:153)
    computes ars:An01_05_SAF_Summ_ByTrt
    computes ars:An07_01_TEAE_Summ_ByTrt
  ars:An07_01_TEAE_Summ_ByTrt  (gold/spec/ars/common-safety-displays.json:4482)  Summary of Subjects with At Least One TEAE, by Treatment
    reads    adam:ADAE.TRTEMFL
    reads    adam:ADAE.USUBJID
    reads    adam:ADSL.SAFFL
    reads    adam:ADSL.TRT01A
    reads    adam:ADSL.USUBJID
  ars:An01_05_SAF_Summ_ByTrt  (gold/spec/ars/common-safety-displays.json:1823)  Summary of Subjects by Treatment
    reads    adam:ADSL.SAFFL
    reads    adam:ADSL.TRT01A
    reads    adam:ADSL.USUBJID
  roles of ars:An07_01_TEAE_Summ_ByTrt: {'adam:ADAE.TRTEMFL': ['subset'], 'adam:ADAE.USUBJID': ['key', 'variable'], 'adam:ADSL.SAFFL': ['set'], 'adam:ADSL.TRT01A': ['grouping'], 'adam:ADSL.USUBJID': ['key']}
  roles of ars:An01_05_SAF_Summ_ByTrt: {'adam:ADSL.SAFFL': ['set'], 'adam:ADSL.TRT01A': ['grouping'], 'adam:ADSL.USUBJID': ['key', 'variable']}
  adam:ADAE.TRTEMFL  (gold/spec/spec/yamaa/pilot-program/adae_v1.yaml:387)
    derives_from, directly: adam:ADAE.ASTDT, adam:ADAE.TRTSDT
    SDTM columns reached: sdtm:AE.AESTDTC, sdtm:AE.STUDYID, sdtm:AE.USUBJID, sdtm:DM.ACTARM, sdtm:DM.STUDYID, sdtm:DM.USUBJID, sdtm:EX.EXSTDTC, sdtm:EX.STUDYID, sdtm:EX.USUBJID
  adam:ADAE.USUBJID  (gold/spec/spec/yamaa/pilot-program/adae_v1.yaml:112)
    derives_from, directly: sdtm:AE.USUBJID
    SDTM columns reached: sdtm:AE.USUBJID
  adam:ADSL.SAFFL  (gold/spec/spec/yamaa/pilot-program/adsl_v1.yaml:507)
    derives_from, directly: adam:ADSL.ITTFL, adam:ADSL.TRTSDT, sdtm:DM.ACTARM
    SDTM columns reached: sdtm:DM.ACTARM, sdtm:DM.ARMCD, sdtm:DM.STUDYID, sdtm:DM.USUBJID, sdtm:EX.EXSTDTC, sdtm:EX.STUDYID, sdtm:EX.USUBJID
  adam:ADSL.TRT01A  (gold/spec/spec/yamaa/pilot-program/adsl_v1.yaml:304)
    derives_from, directly: sdtm:DM.ACTARM, sdtm:DM.ARM
    SDTM columns reached: sdtm:DM.ACTARM, sdtm:DM.ARM
  adam:ADSL.USUBJID  (gold/spec/spec/yamaa/pilot-program/adsl_v1.yaml:259)
    derives_from, directly: sdtm:DM.ACTARM, sdtm:DM.USUBJID
    SDTM columns reached: sdtm:DM.ACTARM, sdtm:DM.USUBJID
```

The percent is computed from two analyses: its own, for the numerator, and
the count of the safety set, for the denominator. The count 65 is the 150th
row of the ARD file, the percent the 153rd.

## What the checks do not cover

- The comparison of grid text is per result. The ARS file of the example
  formats results, not cells, and the expected text of a cell is built with
  the layout's own template. So that a count and its percent share a cell,
  in this order, with one blank between them, is held against nothing
  here. Test D7 plants the percent before the count and prints that it
  passes (lesson 29).
- The first version of this report said that the shell the example names
  (`AE_Summary_Table_Shell.pdf`) is not in its repository. That was wrong
  (review, F1; lesson 31). The shell is next to the example in the pinned
  repository. It shows the cell as the layout has it (count, blank,
  percent), and one line of the row axis that the grid does not have,
  "Number of subjects with at least one event" above the eight rows.
  ADR-003, "The example's table shell", lists every difference. Nothing
  holds the mock shell against the shell yet.
- What else the review found to pass (F3, F4, F6): a body cell that pairs
  the count of one row with the percent of another; another title,
  footnote, section or indent in a layout; a page whose cells or rows
  stand in another place. With a data-driven column grouping, an arm
  without a record of an analysis stops the build (F2); the pilot has
  defined groups.
- The column labels and the row labels are taken from the ARS file. A
  layout may override them; nothing holds an overridden label against the
  reference.
- No result of this output lies on a half at its displayed decimals (D7
  counts 0 of 51), so the rounding rule cannot be told apart on this grid.
  The vectors of the two display rules are the evidence for it.
- `display.pattern`, statements 3 to 5, are read off the example. On the
  other four outputs the rule gives the example's text for all but 130
  formatted values (docs/state/real.md lists them); none is in this output.
- The static walk of the graph cannot see an edge that was never recorded.
  D8 holds the `shows` edges against the builder and the `reads` edges
  against the engine, on this grid and its 9 analyses only.
- The `reads` edges come from what the ARS file names. Both engines are
  handed exactly those columns, so a column that the ARS file does not name
  cannot reach a result. D8 runs an analysis together with the analyses
  its results are computed from and empties the columns none of them
  reads. So a `reads` edge to a column that the analysis of the denominator
  also reads is not tested, and neither is the `computes` edge of a single
  percent to that analysis (review, F4). No cell of this grid loses a
  column by it.
- The citations of the analyses (ARS `documentRefs`) and the viewer are not
  part of real-3a.
- tfrmt was not run (ADR-003).

## The environment on the day

Three things about the machine shaped how the gate was run. None is a
property of the code.

- No network in the Linux environment. From about 10:35 on 2026-11-17 every
  outbound TCP connection from WSL failed (pypi.org, github.com,
  packagemanager.posit.co, by address too), while name lookup and ping
  worked and Windows itself was online. A fresh install and a fresh fetch
  were impossible until the owner rebooted Windows at 11:54; after that the
  connections worked, and `scripts/clean_clone_gate.sh real-3a` ran from
  11:57 to 12:02.
- Out of memory. At 11:16 the virtual machine of WSL (15 GB, shared by all
  sessions) ran out of memory while three sessions ran test suites. After
  that the Ubuntu instance was terminated every 30 to 120 seconds, attached
  sessions included, and four runs of this gate were killed before their
  end. The owner had WSL restarted at 11:40; the run reported here started
  at 11:44:53 and ended at 11:49:44. Since then every session wraps a heavy
  run in `flock /run/lock/specfirst-heavy.lock`.
- The worktree is on a Windows drive, where a gate takes several times as
  long. The gates of this report ran on clones in the Linux file system.

What the owner decided, and what became of it. While the network was
down, the base session asked the owner whether real-3a and std-1 may merge
on the gate with the installed environment; the owner answered that they
may, and that the clean-clone gate is to be run afterwards. The question
and the answer reached this session through the base session; their
words, which are not ASCII, are in the hand-over note of the session
group, outside the repository. The permission was not used: the network
came back before the review was done, the clean-clone gate passed, and
nothing is owed.

Two mistakes of this session on the way, both recorded in
`docs/lessons.md`: a gate was started in the worktree while files of the
next step were written there (lesson 28; the run was stopped and does not
count), and a command passed through `wsl -- bash -lc` cloned the
repository into the worktree (lesson 30; the folder was removed). One more
thing is not a lesson but must be said: to stop that spoiled test run, the
session used a kill by name at 11:16; a test run of another session ended
in the same minute. The kernel log shows the out-of-memory kill at
11:16:08, which explains it, but the kill by name cannot be ruled out as
the cause.

## Review

The independent review (rule R7) is `docs/reports/real-3a.review.md`. A
fresh-context agent that did not write the work read this report as it
stood at `9730843` and at `f55f40d`. Verdict: PASS. It ran the gate
itself on a clone of `9730843` (16 of 16), counted the grid again without
any code of specfirst (27 cells, 51 results, 27 equal), walked the 27
cells to SDTM itself, built three more times under other settings (the
same 30 hashes), and planted 44 changes of the display and 22 gaps of the
trace.

Nine findings, none blocking:

| # | Finding | State |
| --- | --- | --- |
| F1 | ADR-003 and this report said that the table shell the example names is not in its repository. It is. | The sentences are corrected: ADR-003, this report, the state file, lesson 31. Holding the mock shell against the shell, and the line of the row axis the grid lacks, are open. |
| F2 | With a data-driven column grouping, an arm without a record of an analysis stops the build. | Open. Named in ADR-003 and, for gen-2a, in the state file. |
| F3 | The comparison passes a cell that pairs results of two rows, and another title, footnote, section or indent. | Open. Named under "What the checks do not cover". |
| F4 | A single `reads` or `computes` edge can be left out unseen when the analysis of the denominator covers for it. | Open. The sentence on D8 is corrected. |
| F5 | `between_equal_values` and `same_under_every` still hold when our own cell is wrong. | Open. |
| F6 | The check of a page does not see where a text stands. | Open. |
| F7 | `registry.json` loses a blank in statement 3 of `display.pattern`. | Open. |
| F8 | One sentence of rule I9 holds in R only. | Open. |
| F9 | Small things in the texts. | Corrected: the state file, the list of the lines left out of the long quote, the 15 ADaM columns, the row of F3 above, the sentence on the padding in ADR-003. Open: the note of the two vectors, `fisher-limit` among the tests the gate requires, cells without a formatted value in `specfirst check`. |

"Open" means that the fix changes code or a built file. It is the first
commit of the rest of real-3, with a gate run of its own, as the findings
of the review of real-2 were the first commit of this part;
`docs/state/real.md` lists each. What was corrected now is documents only,
so the gate evidence stands, as the review says.

What the review could not check: the source of tfrmt (no network at the
time), so every row of the table "tfrmt, read" in ADR-003 rests on the
author's reading; and it did not run the clean-clone gate again, but
compared the committed log with the log in the clean clone, byte for byte.

## GitHub and CI

`track/real` is pushed to the owner's private repository. CI
(`.github/workflows/ci.yml`: the ASCII check, lint, the unit tests, on
GitHub's runner, which has no R and no fetch cache) ran on every pushed
commit of the branch. On `faa8a5f`, the last commit of real-3a that changes
code:

```text
run 44126884475 on track/real at faa8a5f: completed, success
ASCII check: 387 files checked, 0 with non-ASCII bytes
All checks passed!
756 passed, 19 skipped, 22 deselected in 45.28s
```

The 19 skipped tests need R. In the gate, where R is installed, the same
selection gives 775 passed and none skipped. The later runs:

```text
run 44128018115 on track/real at 0938fe4: completed, success
run 44130810840 on track/real at 9730843: completed, success
run 44133080945 on track/real at f55f40d: completed, success
run 44139428759 on track/real at 26667ed: completed, success
```

The runs on the commit that holds this report and on `main` after the
merge cannot be in it; they are in GitHub, and the session reports them
when it hands the work back.
