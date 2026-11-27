# real-3 Grid, trace, viewer: report

Date: 2026-11-23. Branch: `track/real`. Work package real-3 of PLAN.md
section 13.3, on top of real-3a (the adverse event summary) and issue #31
(the demographics, the table by organ class and term, the review page).
Decisions: docs/decisions/ADR-003.md, the amendment of real-3 (points 1 to
15).

## Verdict

- All five outputs of CDISC's ARS example are grids. The two new ones, the
  vital signs horizontal and vertical (`Out14-3-3-1a`, `Out14-3-3-1b`), have
  1,263 numeric cells each and show 2,019 results. Every cell equals the
  example's text, or differs by a result with one class: 63 cells by 119
  minima and maxima (proof `not_its_own_pattern`) and 4 by 4 medians (the
  new proof `half_in_floating_error`, class `rule_choice`: the owner's
  answer A). Both classifications are per recommendation, pending SME
  review.
- The gate real-3 passes on a clean clone of `b71c200`, 19 of 19 checks.
  Every numeric cell of the five grids, 3,815 in all, has a complete path
  to SDTM columns. Two builds give the same 72 files. The review page shows
  the five outputs, loads and runs nothing, and opens a panel for each of
  its 3,815 printed numbers that reaches SDTM.
- The findings F1 to F9 of the review of real-3a are carried out in the
  first commit, `70dc552`, with a gate run of its own (real-3a, 16 of 16),
  except F7, which needs a new dry run of read-2a (a model call): open, for
  the owner. The mock shells of three outputs are held against the
  example's own table shells.
- @@OTHERGATESHORT@@
- The layout format stays version 0, with one new kind of block
  (`by_groups`) and columns per group (`columns.within`); PLAN.md,
  `standard/` and `env/` are unchanged.
- The fresh-context review: pass 1 NOT SIGNED (F1 blocking: the facts of
  the four medians as first given to the owner were wrong); its six
  findings are carried out (section "Review"). @@PASS2@@

## What real-3 asks for, and where it stands

| PLAN.md 13.3, real-3 | Where |
| --- | --- |
| Layout spec v0, grid builder, mock shells, HTML renderer; ADR-003 | real-3a, issue #31 and this part: seven kinds of block now (`by_groups` and the columns per group, `columns.within`, are new: ADR-003, points 10 and 11) |
| Build the 5 outputs of the ARS example as the first grids; compare cell text with the example's `formattedValue` | all five: `Out14-1-1`, `Out14-3-1-1`, `Out14-3-2-1` (earlier), `Out14-3-3-1a` and `Out14-3-3-1b` (here); every cell equal to the example's formatted values or with one classified difference (section "The vital signs"); three of the five mock shells held against the example's own table shells (F1, point 1) |
| Complete the graph from cells to SDTM variables, and to the documents through the ARS `documentRefs` and the imported claims | the cells of the five grids reach SDTM (the gate's check "trace of the grids"); the `documentRefs` became judged `cites` edges in issue #31 and cover the analyses of the vital signs too |
| Viewer: overview, trace a cell, derivation chain, impact | the review page of issue #31 (`specfirst view`), now with the two grids of the vital signs |
| Gate: 100% of numeric cells in the 5 grids have a complete path to SDTM variables | check "trace of the grids" of the gate real-3 |
| The graph build is deterministic | check "P1 determinism": every built file, the graph files included, of two builds in two folders |
| The viewer opens from the file system with no network | check "review": the page has no script, no handler, no frame, no image, no style that imports, no link outside itself, no refresh; it is the same for both builds |
| The report walks one cell end to end | section "One cell, end to end" |

## The first commit: the findings F1 to F9 of the review of real-3a

`70dc552` carries out the nine findings (ADR-003, amendment of real-3,
points 1 to 9), alone, with a gate run of its own, as the findings of the
review of real-2 were the first commit of real-3a.

| # | Finding | Done |
| --- | --- | --- |
| F1 | The example's table shell is in the pinned repository; nothing held the mock shell against it; the grid lacked one line of the row axis; the mask of the count differed | `shell` of an output in kit.yaml, a pinned PDF; `specfirst.machine.shells` holds the mock shell against its text. The AE summary's eight rows stand in the section "Number of subjects with at least one event", and the count has the shell's mask `XX`. D7 now catches the percent before the count, another text between the two, another header, the mask `XXX`, another row label and the rows without the line above them |
| F2 | A data-driven column grouping: an arm without a record stops the build | It still stops: no number without its ARD row. The message says why and what to do (list the groups before the engines run, ADR-007; rule I11 then gives the count of 0); a unit test holds the review's case |
| F3 | A cell that pairs results of two rows passes; titles, footnotes, sections, indents; a row of another output; an analysis in two blocks | The percent of another row is refused by the layout (a denominator is not); an analysis stands in one block of the body; a cell shows only analyses the reference lists for the output; sections are held against the shell; titles, footnotes and indents are named as held against nothing |
| F4 | A single `reads` or `computes` edge can be left out unseen | `graph.check_cells` holds every edge against the ARS file, and coverage.json's reads against the edges; D8 runs the counts of an analysis against its own `reads` edges alone and plants the review's single edges |
| F5 | Two proofs hold when our own cell is wrong | Both ask that the n, the minimum and the maximum of the cell are reproduced; D6 plants the review's wrong population |
| F6 | The check of a page does not see where a text stands | The page is read back as a table; a handler, a foreign style, a refresh, a comment and text outside the body are refused |
| F7 | registry.json loses a blank in statement 3 of `display.pattern` | Open: any fix changes the entry's bytes, which bind read-2a's kept dry run (ADR-017); a new dry run is a model call the owner approves (section "For the owner") |
| F8 | One sentence of rule I9 holds in R only | The Python engine refuses a group value that is not finite, naming the column |
| F9 | Small things | The two Fisher vectors carry the exact fractions; `fisher-limit` is required by the gates; the limits of `specfirst check` are named |

The gate real-3a on a clone of `70dc552` on the Linux file system, with the
installed environment of the worktree (the way the first commit of real-3a
was checked), under the shared lock on four processors. Its log is
docs/reports/real-3.first-commit.gate.log (681 lines). The commands and the
lines of the log on the findings; `[...]` marks where lines are left out
(pytest's progress dots, the 64 hash lines of P1, the method vectors, the
pilot tests and most lines of the planted defects other than D6 to D8):

```text
$ git clone --quiet --no-local /mnt/d/trial_work/specfirst/.git /root/scratch/real3/clone-70dc552
$ git -C /root/scratch/real3/clone-70dc552 checkout --quiet --detach 70dc552
$ cd /root/scratch/real3/clone-70dc552 && PYTHONPATH=$PWD/src SPECFIRST_ROOT=$PWD \
    flock /run/lock/specfirst-heavy.lock taskset -c 0-3 python -u -m specfirst gate real-3a --clean
gate real-3a at commit 70dc552c56225cf18ae762b97c6b558c2350181d (clean)
[...]
1443 passed, 37 deselected in 432.26s (0:07:12)
[...]
P1 determinism: 64 of 64 files have the same SHA-256 in both builds
[...]
grid Out14-3-1-1: 27 cells, 27 print a number; 27 of the 27 cells with results have a complete path to SDTM columns
[...]
trace: complete
[...]
grid Out14-3-1-1: its mock shell against the table shell AE_Summary_Table_Shell.pdf: 9 rows held, 8 rows of the shell with cells
grid Out14-3-1-1: 27 cells show 51 results; 27 cells equal the reference's formatted values, 0 differ, 0 of them with one class
grid Out14-3-1-1: the R engine's rows give the same grid; the mock shell and the two pages hold; 0 problems
[...]
grids: 8 outputs, pass
[...]
An08_01_Obs_Summ_ByTrt with its population read from EFFFL: 243 differences, 45 of them quartiles and medians of the analysis; proven errors of the reference: {'between_equal_values': 0, 'same_under_every': 0}; without the question of the n, the minimum and the maximum: {'between_equal_values': 16, 'same_under_every': 20}
[...]
the mock shell against AE_Summary_Table_Shell.pdf: 9 rows held, 8 rows of the shell with cells, 0 problems
[...]
layout, the percent before the count: 0 cells differ, 16 problems
layout, another text between the count and the percent: 0 cells differ, 16 problems
layout, the header as N={N}: 0 cells differ, 1 problems
layout, the count under the mask XXX (the same texts, another shell): 0 cells differ, 16 problems
layout, another label of a row: 0 cells differ, 2 problems
layout, the rows without the line above them: 0 cells differ, 1 problems
layout, the percent of the second row in the first: 0 cells differ, 1 problems
[...]
reads: 29 analyses; for each, the columns without a reads edge emptied and rolled (1036 changes of a column in all), then the columns it reads emptied; for 14 of them the results computed from it alone, against its own reads edges alone; 0 problems
[...]
planted, the reads edge from An07_01_TEAE_Summ_ByTrt to ADSL.SAFFL left out (1 edges): 1 problems, for example: ars:An07_01_TEAE_Summ_ByTrt: with the 19 columns it has no reads edge to emptied, 3 of its 3 results computed from it alone change, [...]
[...]
planted in the files, the reads edge from An07_01_TEAE_Summ_ByTrt to ADSL.SAFFL left out (1 records): 7 problems of Out14-3-1-1, [...]
planted in the files, the computes edge of one percent to the analysis of its denominator left out (1 records): 2 problems of Out14-3-1-1, [...]
planted in the files, coverage.json: An07_01_TEAE_Summ_ByTrt reads one column only (0 records): 4 problems of Out14-3-1-1, [...]
[...]
100 passed in 123.31s (0:02:03)
[...]
PASS  environment          0.3 s
PASS  pins                 0.3 s
PASS  lint                 0.1 s
PASS  registry             0.1 s
PASS  unit tests         433.0 s
PASS  method vectors      10.9 s
PASS  kit                  0.1 s
PASS  P1 determinism      38.5 s
PASS  P2 reproduction      0.4 s
PASS  trace                2.5 s
PASS  results              3.1 s
PASS  grids                2.5 s
PASS  pilot tests         48.6 s
PASS  planted defects    123.8 s
PASS  cache untouched      0.1 s
PASS  ASCII                0.0 s
GATE real-3a: PASS
```

It ran from 10:54:25 to 11:07:38 (exit 0). The method vectors required by
the gate now include `fisher-limit` (F9). The F6 plants are unit tests
(`tests/unit/test_grid.py::test_where_a_text_stands_and_what_a_page_may_not_hold`,
nine plants, each passed the check of real-3a); F2 and F8 likewise
(`test_grid.py::test_columns_of_a_data_driven_grouping`,
`test_ard.py::test_a_number_that_is_not_finite_is_no_group_value`).

## The vital signs

The two outputs `Out14-3-3-1a` (horizontal) and `Out14-3-3-1b` (vertical)
show the same results: those of `An08_01_Obs_Summ_ByTrt` (the observed
value) and `An08_02_ChgBl_Summ_ByTrt` (the change from baseline), each split
by the treatment (3 arms), the parameter (4) and the visit (11), all three
groupings with defined groups, with the eight statistics of
`summary.continuous`. The example embeds 1,056 and 960 results of them, all
with a formatted value; our engines give 1,056 and 1,056: the 96 more are
the changes at baseline, a count of 0 and missing statistics (rule I11),
since the data subset of the changes leaves the baseline records out. The
example does not list them, and no cell shows them (the layouts `skip` the
baseline for the changes).

Their layouts (ADR-003, points 10 to 12) follow the example's table shells,
`Vitals_Obs_ChgBaseline_Table_Shell.pdf` and
`Vitals_Obs_ChgBaseline_Table_Shell_vertical.pdf`, which kit.yaml pins
(SHA-256 `bc76bda9...` and `e82c7388...`). The horizontal grid has, under
each arm, the observed value and the change side by side (columns
"Observed" and "Change from Baseline" under the arm as a spanner, the count
of the arm in its first column); every parameter is a section, every visit a
row without cells above the rows "n", "Mean (SD)", "Median", "Q1, Q3" and
"Min, Max". The vertical grid has one column per arm, and under each visit
the rows of the observed values and then, under "<visit> Change from
Baseline", those of the changes.

| Output | Rows | Columns | Cells | Cells that print a number | Results shown | Rows of the table shell with cells, held |
| --- | --- | --- | --- | --- | --- | --- |
| Out14-3-3-1a | 265 | 6 | 1,590 | 1,263 | 2,019 | 10 |
| Out14-3-3-1b | 505 | 3 | 1,515 | 1,263 | 2,019 | 15 |

The results shown are the 2,016 the example formats and the three counts of
the safety set under the column headers.

Against the example's formatted values, each of the 2,016 results under the
pattern of its operation (the shells show the same masks):

| | Results |
| --- | --- |
| our text is the example's formatted value | 1,893 |
| a minimum or a maximum of temperature that the example shows with the decimals of the data under its pattern `XX` ("35.33"); its raw value under the pattern is our text | 119 (59 minima, 60 maxima) |
| a median of the change of temperature that is 0.05 in the example (" 0.1") and 0.04999999999999716 in both our engines (" 0.0") | 4 |

The 119 are entries of `formats` in gold/exceptions.yaml with the existing
proof `not_its_own_pattern` and the class `reference_error`: the example's
own shells show "Min, Max" as "XX, XX"; the grid follows its pattern, as
issue #31 did for the one Fisher p-value of 1. (The SAP's Templates 21 and
22, "for example only", show the minimum and the maximum of blood pressure
and heart rate without decimals; they do not list temperature.) The
demographics follow the other way, because their SAP template shows the
minimum and the maximum of height with one decimal (custom:demog-decimals).
Per recommendation, pending SME review (SME-33, real-3/vs-minmax-decimals).

The 4 medians: each is one record's change of 0.05, such as AVAL 36.94 -
BASE 36.89, which binary floating point holds as 0.04999999999999716 (three
of the four cells have an odd n, the fourth two equal middle records). The
pilot's reference ADVS holds the same value in the same 56 records as ours
(P2), and the example writes its raw values of the vital signs in at most 12
characters, so its "0.05" is that value too. The data are the same: the
example's display rounds in a way that absorbs the floating error (most
likely SAS's ROUND fuzz; not verified here), another alternative of the
rounding than gold's. They are entries of `formats` with the proof kind
`half_in_floating_error` and the class `rule_choice` (ADR-003, point 13):
the owner's answer A, per recommendation, pending SME review
(SME-26, real-3/vs-medians-at-half). The first version of this report described
them as the half of the changes 0.0 and 0.1 and proposed the class
`data_difference`; the review found that wrong (pass 1, F1), and the owner
was told.

In the cells: of the 1,263 numeric cells of each grid, 63 show a minimum and
a maximum of temperature one of which is an entry of the 119, and 4 show
one of the 4 medians. Every other cell equals the example's text.

## The gate

`scripts/clean_clone_gate.sh real-3` on commit `b71c200`: a fresh clone
under `/tmp`, a fresh install of the Python environment, the R library and
CDISC CORE, a fresh fetch of the pinned sources, then the gate with
`--clean`; run under the shared lock on four processors. Its log is
docs/reports/real-3.clean-clone.gate.log (881 lines). The commands and the
lines of the log that say what the gate text asks; `[...]` marks where
lines are left out (the install and the fetch, pytest's progress dots, the
hash lines of P1 but those of the four new files, the lines of the outputs
that are not of the example, the method vectors, the decisions, the pilot
tests and the planted defects D1 to D13 but the lines of D8 on the trace):

```text
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 scripts/clean_clone_gate.sh real-3 /mnt/d/trial_work/specfirst/.git b71c200
clean clone gate real-3
$ git clone --quiet --no-local /mnt/d/trial_work/specfirst/.git /tmp/specfirst-clean-fiKgpo/specfirst
$ git -C /tmp/specfirst-clean-fiKgpo/specfirst checkout --quiet --detach b71c200
[...]
$ bash env/install.sh
[...]
$ specfirst fetch
[...]
$ specfirst gate real-3 --clean
gate real-3 at commit b71c200536b5a9686344b2760dfc6e5eb9a615ac (clean)
[...]
1454 passed, 38 deselected in 431.11s (0:07:11)
[...]
== [8/19] P1 determinism: specfirst check cdiscpilot01 --twice (its first part)
[...]
same      5e0dc4af97af66a7 5e0dc4af97af66a7 gold/grid/Out14-3-3-1a.json
same      2993e727a7f6036a 2993e727a7f6036a gold/grid/Out14-3-3-1a.shell.json
same      244261ee3dcbe1c8 244261ee3dcbe1c8 gold/grid/Out14-3-3-1b.json
same      a6c01585a4b0dfb0 a6c01585a4b0dfb0 gold/grid/Out14-3-3-1b.shell.json
[...]
same      07677ba96f9e3aae 07677ba96f9e3aae gold/out/Out14-3-3-1a.html
same      55e8adc753417927 55e8adc753417927 gold/out/Out14-3-3-1a.shell.html
same      a594db66ea116c5c a594db66ea116c5c gold/out/Out14-3-3-1b.html
same      3427a2d268a5fa70 3427a2d268a5fa70 gold/out/Out14-3-3-1b.shell.html
[...]
P1 determinism: 72 of 72 files have the same SHA-256 in both builds
[...]
== [10/19] trace of the grids: specfirst check cdiscpilot01 --build build/p1/cdiscpilot01/first (its third part), the five outputs
[...]
grid Out14-3-3-1a: 1590 cells, 1263 print a number; 1263 of the 1263 cells with results have a complete path to SDTM columns
[...]
grid Out14-3-3-1b: 1515 cells, 1263 print a number; 1263 of the 1263 cells with results have a complete path to SDTM columns
[...]
trace: complete
trace of the grids: 5 outputs; numeric cells with a complete path: Out14-1-1 84, Out14-3-1-1 27, Out14-3-2-1 1178, Out14-3-3-1a 1263, Out14-3-3-1b 1263
[...]
grid Out14-3-3-1a: its mock shell against the table shell Vitals_Obs_ChgBaseline_Table_Shell.pdf: 265 rows held, 10 rows of the shell with cells
grid Out14-3-3-1a: 1590 cells show 2019 results; 1523 cells equal the reference's formatted values, 67 differ, 67 of them with one class
grid Out14-3-3-1a: the R engine's rows give the same grid; the mock shell and the two pages hold; 0 problems
grid Out14-3-3-1b: its mock shell against the table shell Vitals_Obs_ChgBaseline_Table_Shell_vertical.pdf: 505 rows held, 15 rows of the shell with cells
grid Out14-3-3-1b: 1515 cells show 2019 results; 1448 cells equal the reference's formatted values, 67 differ, 67 of them with one class
grid Out14-3-3-1b: the R engine's rows give the same grid; the mock shell and the two pages hold; 0 problems
[...]
grids: 10 outputs, pass
[...]
== [14/19] review: specfirst view cdiscpilot01 --build build/p1/cdiscpilot01/first
Out14-1-1: 84 printed numbers; 84 open a panel; 84 reach SDTM; 84 reach a citation or a house default; 84 draw every decision behind them
Out14-3-1-1: 27 printed numbers; 27 open a panel; 27 reach SDTM; 27 reach a citation or a house default; 27 draw every decision behind them
Out14-3-2-1: 1178 printed numbers; 1178 open a panel; 1178 reach SDTM; 1178 reach a citation or a house default; 1178 draw every decision behind them
Out14-3-3-1a: 1263 printed numbers; 1263 open a panel; 1263 reach SDTM; 1263 reach a citation or a house default; 1263 draw every decision behind them
Out14-3-3-1b: 1263 printed numbers; 1263 open a panel; 1263 reach SDTM; 1263 reach a citation or a house default; 1263 draw every decision behind them
sheet: 17 catalog entry, 1 kit binding, 10 layout, 67 record; 67 of 67 records listed
review: build/p1/cdiscpilot01/first/viewer/index.html has 5597006 bytes, 63 panels of analyses, 4028 cells with a panel; it loads and runs nothing: True; the second build of P1 gives the same page: True
[...]
reads: 31 analyses; for each, the columns without a reads edge emptied and rolled (1096 changes of a column in all), then the columns it reads emptied; for 14 of them the results computed from it alone, against its own reads edges alone; 0 problems
[...]
--- D14-vital-signs
Out14-3-3-1a, unchanged: 0 problems
Out14-3-3-1b, unchanged: 0 problems
Out14-3-3-1a, the observed value and the change exchanged between their columns: 20 problems, for example: row r3 ('n'): its cells stand in the columns [2, 4, 6]; on line 16 of the shell in [1, 3, 5]
Out14-3-3-1a, the change shown at baseline: 7 problems, for example: line 16 of the shell ('n', ['XX', 'XX', 'XX']): no row of the mock shell has it
Out14-3-3-1b, the change shown at baseline: 2 problems, for example: 96 results without a formatted value; the gate asks for none
Out14-3-3-1a, the minimum and the maximum under XX.X: 242 problems, [...]
Out14-3-3-1b, the minimum and the maximum under XX.X: 283 problems, [...]
Out14-3-3-1a, the median above the mean: 138 problems, for example: row r4 ('Median'): in the shell it does not follow the row before it
Out14-3-3-1b, the median above the mean: 261 problems, for example: row r4 ('Median'): in the shell it does not follow the row before it
Out14-3-3-1a, Week 2 left out: 193 problems, [...]
Out14-3-3-1b, Week 2 left out: 193 problems, [...]
Out14-3-3-1a, a minimum proven to lie on a half: 1 problems, [...]
Out14-3-3-1a, a median at a half classed reference_error: 1 problems, [...]
Out14-3-3-1a, a median at a half without its entry: 1 problems, [...]
not separable by the shell: Out14-3-3-1b, the change rows under the visit alone: 0 problems (the shell has a placeholder there)
101 passed in 132.38s (0:02:12)
[...]
PASS  environment          0.3 s
PASS  pins                 0.9 s
PASS  lint                 0.0 s
PASS  registry             0.1 s
PASS  unit tests         431.7 s
PASS  method vectors      10.6 s
PASS  kit                  0.1 s
PASS  P1 determinism      40.2 s
PASS  P2 reproduction      0.3 s
PASS  trace of the grids      4.3 s
PASS  results              3.2 s
PASS  grids                3.1 s
PASS  recompute            9.2 s
PASS  review               1.5 s
PASS  decisions            0.6 s
PASS  pilot tests         49.9 s
PASS  planted defects    132.8 s
PASS  cache untouched      0.1 s
PASS  ASCII                0.0 s
GATE real-3: PASS
clean clone gate real-3: PASS (clone: /tmp/specfirst-clean-fiKgpo/specfirst)
```

The gate text, statement by statement:

- 100% of numeric cells in the 5 grids have a complete path to SDTM
  variables: check 10. It walks every cell of every grid of the build from
  the graph files and fails on a numeric cell without an ARD row or with a
  broken path, and on any of the five outputs not walked with its cells
  (the unit test of the gate plants each). Every edge on the way is held
  against the ARS file (F4).
- The graph build is deterministic: check 8, two builds in two folders, 72
  of 72 files the same, the three graph files among them.
- The viewer opens from the file system with no network: check 14. The page
  has no script, handler, frame, image, form, style that imports, link
  outside itself or refresh (D13 and tests/unit/test_viewer.py plant each), and the two builds give the
  same page.
- The report walks one cell end to end: section "One cell, end to end".

## The other gates

@@OTHERGATES@@

## One cell, end to end

`cell:Out14-3-3-1a/r10/c2`: Systolic Blood Pressure (mmHg), Week 2, the row
"Mean (SD)", the column "Change from Baseline" under "Placebo". Walked from
`nodes.jsonl`, `edges.jsonl` and `coverage.json` of the first build of a
run of the gate in the worktree's Linux copy (the build of `b71c200`'s
code; the grid file and the two graph files have the SHA-256 that P1 prints
for the clean clone: `5e0dc4af97af66a7` for the grid), by the script that
walked a cell for real-3a (it reads the three files and nothing else; not
committed). The first rows of the grid, for the place of the cell:

```text
r1 'Parameter (Units) Visit' @header ['(N=86)', '', '(N=84)', '', '(N=84)', '']
r2 'Baseline' Systolic Blood Pressure (mmHg) ['', '', '', '', '', '']
r3 'n' Systolic Blood Pressure (mmHg) ['255', '', '252', '', '252', '']
r4 'Mean (SD)' Systolic Blood Pressure (mmHg) ['136.8 (17.81)', '', '136.9 (17.57)', '', '138.8 (18.74)', '']
[...]
r8 'Week 2' Systolic Blood Pressure (mmHg) ['', '', '', '', '', '']
r9 'n' Systolic Blood Pressure (mmHg) ['252', '249', '251', '251', '243', '243']
r10 'Mean (SD)' Systolic Blood Pressure (mmHg) ['133.8 (17.80)', '- 3.3 (14.60)', '135.2 (17.72)', '- 1.8 (15.32)', '132.3 (16.61)', '- 6.1 (15.57)']
```

The walk:

```text
cell:Out14-3-3-1a/r10/c2  text '- 3.3 (14.60)'  (gold/grid/Out14-3-3-1a.json:1)
  shows    ard:An08_02_ChgBl_Summ_ByTrt/Mth02_ContVar_Summ_ByGrp_2_Mean/AnlsGrouping_01_Trt_1/AnlsGrouping_08_Param_1/AnlsGrouping_09_Visit_02  (gold/ard/common-safety-displays.jsonl:3316)
    computes ars:An08_02_ChgBl_Summ_ByTrt
  shows    ard:An08_02_ChgBl_Summ_ByTrt/Mth02_ContVar_Summ_ByGrp_3_SD/AnlsGrouping_01_Trt_1/AnlsGrouping_08_Param_1/AnlsGrouping_09_Visit_02  (gold/ard/common-safety-displays.jsonl:3448)
    computes ars:An08_02_ChgBl_Summ_ByTrt
  ars:An08_02_ChgBl_Summ_ByTrt  (gold/spec/ars/common-safety-displays.json:54268)  Summary of Change from Baseline by Treatment, Parameter and Visit
    reads    adam:ADSL.SAFFL
    reads    adam:ADSL.TRT01A
    reads    adam:ADSL.USUBJID
    reads    adam:ADVS.ANL01FL
    reads    adam:ADVS.AVISIT
    reads    adam:ADVS.CHG
    reads    adam:ADVS.PARAMCD
    reads    adam:ADVS.USUBJID
  roles of ars:An08_02_ChgBl_Summ_ByTrt: {'adam:ADSL.SAFFL': ['set'], 'adam:ADSL.TRT01A': ['grouping'], 'adam:ADSL.USUBJID': ['key'], 'adam:ADVS.ANL01FL': ['subset'], 'adam:ADVS.AVISIT': ['grouping', 'subset'], 'adam:ADVS.CHG': ['variable'], 'adam:ADVS.PARAMCD': ['grouping'], 'adam:ADVS.USUBJID': ['key']}
  adam:ADSL.SAFFL  (gold/spec/spec/yamaa/pilot-program/adsl_v1.yaml:507)
    derives_from, directly: adam:ADSL.ITTFL, adam:ADSL.TRTSDT, sdtm:DM.ACTARM
    SDTM columns reached: sdtm:DM.ACTARM, sdtm:DM.ARMCD, sdtm:DM.STUDYID, sdtm:DM.USUBJID, sdtm:EX.EXSTDTC, sdtm:EX.STUDYID, sdtm:EX.USUBJID
  adam:ADSL.TRT01A  (gold/spec/spec/yamaa/pilot-program/adsl_v1.yaml:304)
    derives_from, directly: sdtm:DM.ACTARM, sdtm:DM.ARM
    SDTM columns reached: sdtm:DM.ACTARM, sdtm:DM.ARM
  adam:ADSL.USUBJID  (gold/spec/spec/yamaa/pilot-program/adsl_v1.yaml:259)
    derives_from, directly: sdtm:DM.ACTARM, sdtm:DM.USUBJID
    SDTM columns reached: sdtm:DM.ACTARM, sdtm:DM.USUBJID
  adam:ADVS.ANL01FL  (gold/spec/cdiscpilot01/spec/yamaa/advs.yaml:777)
    derives_from, directly: sdtm:VS.STUDYID, sdtm:VS.USUBJID, sdtm:VS.VISIT, sdtm:VS.VISITNUM, sdtm:VS.VSDTC, sdtm:VS.VSDY, sdtm:VS.VSSEQ, sdtm:VS.VSSTRESN, sdtm:VS.VSTESTCD, sdtm:VS.VSTPT, sdtm:VS.VSTPTNUM
    SDTM columns reached: sdtm:VS.STUDYID, sdtm:VS.USUBJID, sdtm:VS.VISIT, sdtm:VS.VISITNUM, sdtm:VS.VSDTC, sdtm:VS.VSDY, sdtm:VS.VSSEQ, sdtm:VS.VSSTRESN, sdtm:VS.VSTESTCD, sdtm:VS.VSTPT, sdtm:VS.VSTPTNUM
  adam:ADVS.AVISIT  (gold/spec/cdiscpilot01/spec/yamaa/advs.yaml:445)
    derives_from, directly: sdtm:VS.STUDYID, sdtm:VS.USUBJID, sdtm:VS.VISIT, sdtm:VS.VISITNUM, sdtm:VS.VSDTC, sdtm:VS.VSDY, sdtm:VS.VSSEQ, sdtm:VS.VSSTRESN, sdtm:VS.VSTESTCD, sdtm:VS.VSTPT, sdtm:VS.VSTPTNUM
    SDTM columns reached: sdtm:VS.STUDYID, sdtm:VS.USUBJID, sdtm:VS.VISIT, sdtm:VS.VISITNUM, sdtm:VS.VSDTC, sdtm:VS.VSDY, sdtm:VS.VSSEQ, sdtm:VS.VSSTRESN, sdtm:VS.VSTESTCD, sdtm:VS.VSTPT, sdtm:VS.VSTPTNUM
  adam:ADVS.CHG  (gold/spec/cdiscpilot01/spec/yamaa/advs.yaml:640)
    derives_from, directly: adam:ADVS.AVAL, adam:ADVS.BASE, sdtm:VS.STUDYID, sdtm:VS.USUBJID, sdtm:VS.VISIT, sdtm:VS.VISITNUM, sdtm:VS.VSDTC, sdtm:VS.VSDY, sdtm:VS.VSSEQ, sdtm:VS.VSSTRESN, sdtm:VS.VSTESTCD, sdtm:VS.VSTPT, sdtm:VS.VSTPTNUM
    SDTM columns reached: sdtm:VS.STUDYID, sdtm:VS.USUBJID, sdtm:VS.VISIT, sdtm:VS.VISITNUM, sdtm:VS.VSDTC, sdtm:VS.VSDY, sdtm:VS.VSSEQ, sdtm:VS.VSSTRESN, sdtm:VS.VSTESTCD, sdtm:VS.VSTPT, sdtm:VS.VSTPTNUM
  adam:ADVS.PARAMCD  (gold/spec/cdiscpilot01/spec/yamaa/advs.yaml:300)
    derives_from, directly: sdtm:VS.STUDYID, sdtm:VS.USUBJID, sdtm:VS.VISIT, sdtm:VS.VISITNUM, sdtm:VS.VSDTC, sdtm:VS.VSDY, sdtm:VS.VSSEQ, sdtm:VS.VSSTRESN, sdtm:VS.VSTESTCD, sdtm:VS.VSTPT, sdtm:VS.VSTPTNUM
    SDTM columns reached: sdtm:VS.STUDYID, sdtm:VS.USUBJID, sdtm:VS.VISIT, sdtm:VS.VISITNUM, sdtm:VS.VSDTC, sdtm:VS.VSDY, sdtm:VS.VSSEQ, sdtm:VS.VSSTRESN, sdtm:VS.VSTESTCD, sdtm:VS.VSTPT, sdtm:VS.VSTPTNUM
  adam:ADVS.USUBJID  (gold/spec/cdiscpilot01/spec/yamaa/advs.yaml:107)
    derives_from, directly: sdtm:VS.STUDYID, sdtm:VS.USUBJID, sdtm:VS.VISIT, sdtm:VS.VISITNUM, sdtm:VS.VSDTC, sdtm:VS.VSDY, sdtm:VS.VSSEQ, sdtm:VS.VSSTRESN, sdtm:VS.VSTESTCD, sdtm:VS.VSTPT, sdtm:VS.VSTPTNUM
    SDTM columns reached: sdtm:VS.STUDYID, sdtm:VS.USUBJID, sdtm:VS.VISIT, sdtm:VS.VISITNUM, sdtm:VS.VSDTC, sdtm:VS.VSDY, sdtm:VS.VSSEQ, sdtm:VS.VSSTRESN, sdtm:VS.VSTESTCD, sdtm:VS.VSTPT, sdtm:VS.VSTPTNUM
```

The cell shows two results of one analysis, the mean and the standard
deviation of the change from baseline; neither is a percent, so each is
computed from its analysis alone. The analysis reads eight columns of ADSL
and ADVS in five roles; every one leads to SDTM columns of DM, EX and VS.
The example's formatted values of the two results are "- 3.3" and
"(14.60)": the cell is the template "{mean} {sd}" filled with them.

## What the checks do not cover

- Titles, footnotes and indents are held against nothing: the layout or
  the ARS display gives them, and the shells write them with placeholders
  ("Table 14.3.1.<x>.<y>", "<Vertical Layout>") or in their own words. The
  grid of the AE summary keeps the ARS file's first title, "Table
  14.3.1.<x>.<y>", where its shell has "Table 14.3.1.1".
- The labels of the columns are not read from a shell (pdftotext breaks
  them over lines); where a column stands is held through the place of the
  cells on their lines only when the shell's fullest rows have one cell per
  column.
- A shell's placeholder fits any text: the heading "<visit> Change from
  Baseline" of the vertical grid stands against "< Visit n Change from
  Baseline >"; D14 prints that a heading without "Change from Baseline"
  passes the shell.
- The shells of the demographics and of the table by organ class and term
  are RTF files: not pinned, not read. Their grids follow them by the
  reading of issue #31 only.
- `specfirst check` counts a cell whose result has no formatted value in
  the reference as not compared; the gate asks for none in the vital signs
  and the AE summary, and for 408 in the table by organ class and term (the
  example embeds one Fisher p-value per test analysis).
- F2: with a data-driven column grouping, a group without a record of an
  analysis still stops the build; no cell shows a 0 without its ARD row.
  The compiled studies list their groups before the engines run (ADR-007).
- F7 is open (section "For the owner").
- What the pilot data cannot show, printed by tests/defects on every run:
  as before (the safety and intent-to-treat sets hold the same subjects; no
  result of the AE summary lies on a half). Of the vital signs, results lie
  exactly on a half at their displayed decimals (among them the third
  quartile 0.25, " 0.3"); D14 prints them and plants the rounding rule
  half_even, which changes the grid.
- The labels of a statistic row are held against the labels of the ARS
  operations it shows; a row whose label names no operation's label ("LS
  Means (SE)" when no operation is labelled so) is held against nothing.
- A label the layout gives a group is refused only when it is the name of
  another group of the grouping; a wrong label that is no group's name
  ("Week 3", "week 4") is held against nothing (the review, pass 2, G2). The
  layouts of the vital signs give no label: the grids show the ARS names.

## For the owner

1. **Four medians of the vital signs: answered (A), 2026-11-23.** Keep
   gold's display rule and record the four as exceptions with a proof kind
   of their own and a planted defect; spend nothing. Class `rule_choice`
   (the base session's reading, which the review's pass 1 supports with the
   data). Per recommendation, pending SME review (docs/state/sme-review.md,
   SME-26, real-3/vs-medians-at-half). The question first went out with wrong
   facts (the half of 0.0 and 0.1); the correction went to the owner the
   same day. The other answer (B), a display rule that rounds to 12
   significant digits first, changes 4 texts of the 3,323 results held as
   floating-point numbers that the ten grids show (the 4 medians, now
   " 0.1"; measured by a script of this session on a build of the work) and
   changes `display.pattern`, so read-2a's kept dry run would be made again.
2. **F7 (does not block).** Statement 3 of `display.pattern` loses a blank
   in registry.json. Any fix changes the entry's bytes, which bind read-2a's
   kept dry run (ADR-017). It waits for the next remake of the kept dry run
   (ADR-003, point 7, has the exact fix; gen-2b remakes the run before this
   work merges, so it is not that one).
3. **The 119 minima and maxima (does not block).** Classed `reference_error`
   by the existing proof, because the example's own shells show no
   decimals; per recommendation, pending SME review
   (SME-33, real-3/vs-minmax-decimals). The alternative, a pattern with the decimals
   of the data (`XX.XX` for the observed values, `X.XX` for the changes),
   would print "35.33" in 63 cells of each grid and leave 10 of the 126
   minima and maxima of temperature different, where the example drops
   trailing zeros ("37.5", "-1").
4. **The layout of the AE summary changed (does not block).** Its eight
   rows now stand in the section "Number of subjects with at least one
   event", indented, as the example's shell shows them; the count's mask in
   the mock shell is the shell's `XX`. No cell text changes.
5. **ADR-003, amendment of real-3 (points 1 to 15)** stands unless the
   owner objects, as the earlier amendments do.

## Review

The independent review (rule R7) is docs/reports/real-3.review.md. Pass 1,
of `10805f6`, by a fresh-context agent that did not write the work: NOT
SIGNED. It ran the gate real-3 on its own clone of `10805f6` (19 of 19),
built a third time under other settings (72 of 72 files the same), recounted
both grids of the vital signs and walked all five grids without the checking
code (3,815 of 3,815 numeric cells reach SDTM), and planted its own defects.
The four statements of the gate text held. Six findings:

| # | Finding | Done |
| --- | --- | --- |
| F1 (blocking) | The four medians: the facts given to the owner were wrong (no change of 0.1 exists; each median is one record's change of 0.05 held as 0.04999999999999716, the same in the public ADVS), and the proof kind stated a cause it does not show | The report, ADR-003 point 13, the exceptions file and `grid.half_problem` say what the data show; the proof states only what it shows and builds the alternative rounding on our value; class `rule_choice`; the owner was told the corrected facts (the answer A stands; per recommendation, pending SME review) |
| F2 | Nothing held which statistic a row shows, or the order of two parts with one mask; the order of the analyses of a by_groups block; labels exchanged | The label of a statistic row is held against the labels of the ARS operations it shows; a label that is another group's name is refused; the analyses of a by_groups block follow the reference's list (ADR-003, point 15); D14 and the unit tests plant each of the review's cases |
| F3 | Both page checks passed hidden cells and other ways to fetch | The grid page refuses `hidden`, any style but the indent, and every fetching element and attribute; the review page treats `background`, `poster`, `xlink:href` and the like as links and refuses `image-set(` and SVG elements; unit tests plant each |
| F4 | The vertical grid lacked "Safety Population"; a sentence of its layout was wrong | `ars.display_sections` takes subsections that another display writes; the layout takes the titles and headers from the ARS file |
| F5 | The report and the state file were not finished; point 13 of the ADR glued to point 12 | Finished; the ADR is mended |
| F6 | Small things: the owner's answer said recorded; the sentence on results at a half; "D13 plants each"; 1,562 and 9 not reproduced; Templates 21 and 22 do not cover temperature | Corrected; D14 plants the rounding rule half_even; test_viewer.py plants every kind the page check names; the two numbers measured again (3,323 and 4; 10) |

@@PASS2TEXT@@

## GitHub and CI

@@CI@@
