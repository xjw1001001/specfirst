# read-1a Scorer of the slice "adverse event summary first": independent review

Rule R7 of PLAN.md. Reviewer: an agent with a fresh context that did not
write the work. Date: 2026-11-18. Correctness only, no style.

Reviewed: branch `track/read` at `fd02360`, in the worktree of the track;
base `main` = `d5c7e50`; seven commits, 29 files, 7,267 lines added. The
code is that of `55dba60`, the commit on which the gate ran: `git diff
--stat 55dba60 fd02360` names three files, all of them documents. The tree
was clean when I began (`git status --short` printed nothing) and has
this file as its one change now; `origin/track/read` is `fd02360`.

Result: NOT SIGNED. One finding blocks (R1). Six do not (R2 to R7).

What blocks is not a defect of the code. The part reads the text of its
own gate by a table that it wrote, and ran the gate before the owner was
asked. The project has a lesson for exactly that (lesson 47), and it gives
the answer to the owner, not to the executor and not to me. On its merits
I found the reading reasonable: R1 says which parts of it are facts and
which are choices. If the owner accepts it, nothing more is owed for R1.

The scorer held under most of what I tried. The gold tables of the
hand-made study are right by my own count. The four scores are right on
cases I counted by hand. A defect planted alone, in a decision or in a
step of the build, is owned by the right layer in everything I ran. Arm C
reads the document of the kit. Three kits of a seed of my own pass what
the gate asks of the ten. What I would not rely on yet is the owner of a
wrong cell when two decisions are wrong at once (R2).

## How the review was done

- In the worktree, with Windows git for the diff and the history, and
  read-only commands. Nothing was searched or listed outside the worktree,
  my scratch folder on the Windows side and the scratch folders under
  `/root` of the WSL machine. The folder `reference/` beside the checkout
  was not touched. Nothing I read looked internal to an employer.
- Everything that runs, under WSL (Ubuntu 24.04, root) in the environment
  of the worktree. Every test run, every build of kits and every script
  that builds or scores ran inside `flock /run/lock/specfirst-heavy.lock
  taskset -c 0-3`, one at a time; a script that only reads a log or a
  document ran without the lock. The gate was not run again: no doctor,
  no pins, no lint, not the whole test suite, no run of CDISC CORE.
  Nothing was installed. The fetch cache was read (the pilot) and not
  written.
- The ten kits of the gate seed that the author kept
  (`/root/scratch-read1a/kits/kit-001` to `kit-010`) were read and never
  written. Kits and copies of my own are in `/root/scratch-review-read1a/`.
- A defect "planted in the scorer" below is a function replaced in memory
  by my script, for the length of one run. No file of the repository was
  changed but this one. Nothing was committed. My scripts are in my
  scratch folder and are not kept; each is described where its output is
  quoted.

## What I read

- `CLAUDE.md`; `PLAN.md` sections 2, 4.1 to 4.8, 8, 9, 13.5 and 13.6;
  `docs/decisions/ADR-005.md`; `ADR-007.md` to line 240: the decisions
  and "The owner's answer on decision 6" with the first two things that
  follow from it; `ADR-008.md`; `docs/reports/read-1a.md`, all of it;
  `read-1a.gate.log`, lines 1 to 112 and the summary of every check, and
  the other lines by the scripts of sections B and C;
  `docs/state/read.md`; `docs/state/gen.md`, "A kit: what the folder
  holds" to "What a scorer must know"; `docs/lessons.md`, lessons 44 to
  52; of `docs/reports/gen-2a.review.md`, as a model, pass 1 to finding
  G1, "Checked and found correct" and "What settles G1".
- The diff `d5c7e50..fd02360`. In full: the thirteen files of
  `src/specfirst/score/`; the parts of `src/specfirst/gates.py` and
  `cli.py` that the diff adds; `tests/unit/test_score_hand.py`,
  `test_score_kit.py`, `test_score_build.py`, `test_score_reading.py`,
  `test_score_pilot_pins.py` and `tests/score/test_score_pilot.py`; the
  changes of `CLAUDE.md`, `docs/lessons.md` and `tests/defects/README.md`.
- `git diff 134c6f7 55dba60 -- src/specfirst/score/defects.py`: what the
  planted defects were at the end of the first half, and what they are
  now.
- Of the code the scorer uses and does not own: `specfirst.gen.display`
  in full; `verify.options` and `verify.label`; `decisions.variants`;
  `compiler.other_values`; the default functions of `compile.house`; the
  catalog entry `ae.related.values`; the analyses and methods of
  `standard/houses/open-default@1/ars/ae-summary.yaml`.
- Not read: `docs/reports/read-1a.first-half.gate.log`.

## What I ran

Outputs are cut to the lines that matter. Where several lines say the
same, I put them into one, or a line in brackets says so; the numbers and
the texts of the cells are as printed.

A. The tests of the scorer. The first run is `pytest.main` in my script
`mutants.py` with nothing planted (`-q -x -p no:cacheprovider -o
addopts=`); the second is the command.

```text
tests/unit/test_score_hand.py tests/unit/test_score_build.py tests/unit/test_score_reading.py
65 passed in 58.04s
$ SPECFIRST_STRICT=1 flock /run/lock/specfirst-heavy.lock taskset -c 0-3 python -m pytest
    -p no:cacheprovider -q -m "evidence or not evidence" tests/unit/test_score_kit.py
    tests/unit/test_score_pilot_pins.py tests/score
19 passed in 95.42s (0:01:35)
```

B. The checks 5 to 10 and 12 of the gate, run again in the worktree on the
kept kits and held line by line against the committed gate log
(`parts.py`: it calls the functions of `specfirst.score.gate` and
`kit.score_set`, collects what they print and asks of every line whether
it is a line of `docs/reports/read-1a.gate.log`). This is not the gate:
no kit is written, and checks 1 to 4, 11, 13 and 14 are not run.

```text
kit.yaml of the kept kits has the hash the gate log prints: 10 of 10
hand_table: returns True; 16 lines, 0 not in the gate log
separated: returns True; 24 lines, 0 not in the gate log
control: returns True; 11 lines, 0 not in the gate log
arms: returns True; 71 lines, 0 not in the gate log
planted_defects: returns True; 72 lines, 0 not in the gate log
pilot_report: returns True; 46 lines, 0 not in the gate log
score_set on the kept kits: returns True; 206 lines, 0 not in the gate log
```

C. The report against the gate log (`r8.py`: every line of every code
block of `docs/reports/read-1a.md`, and the sums of the verdict).

```text
15 code blocks, 377 lines in them; not a line of the gate log: 1
  report line 644: $ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 bash scripts/clean_clone_gate.sh read-1a
sweeps per kit: 10 values 293 shown 209 silent 83 visible only 1 cells 2307
arm S, stage T, twin, correct of gold cells: ['25/30', '8/18', '9/16', '7/15', '7/20', '21/30', '19/24', '1/16', '0/24', '16/18']
  S1-arms: passed 10
  S2-set: passed 10
  S2-set-rule: passed 6, silent 4
  S3-window: passed 3, not planted 7
  S4-denominator: passed 10
  S5-column: passed 8, not planted 2
  S9-sort: passed 10
  S10-frozen: passed 5, silent 2, not planted 3
  S11-quote: passed 10
  S12-span: passed 10
log lines: 639 ; tests: ['1028 passed, 23 deselected in 213.11s (0:03:33)', '1 passed in 0.81s']
```

The one line that is not in the log is the command that wrote the log.

D. Candidates of my own on the hand-made study (`hand_probes.py`: the
records of arm C with values changed, records added or left out, or a
hook of my own; each scored by `scorer.run` and printed by
`report.lines`). First what one wrong decision does alone, then two at
once.

```text
a2  ae.teae.end = no_end, alone
    twin: 22 of 24; "L4 mod-ae-emergence ae.teae.end 2  2 of 2  adam:ADAE.TRTEMFL"
    the two cells: Any adverse event / Placebo and / Total
a3  tfl.percent.format = one_decimal_always, alone
    visible: 18 of 24; "L7 tfl-ae-summary tfl.percent.format  6  6 of 6   layout:tfl-ae-summary/formats"
    twin:    14 of 24; "L7 tfl-ae-summary tfl.percent.format 10  10 of 10 layout:tfl-ae-summary/formats"
a   both at once
    decisions a reviewer would have to change: 2
    visible: 18 of 24; "L7 tfl-ae-summary   tfl.percent.format  6  6 of 6   layout:tfl-ae-summary/formats"
    twin:    12 of 24; "L4 mod-ae-emergence ae.teae.end        12  2 of 12  adam:ADAE.TRTEMFL"
    twin: Fatal adverse event | Placebo | L4 | ae.teae.end | confirmed False | adam:ADAE.TRTEMFL
    (nine more cells of a3 on the twin, the same; no line "wrong by value, and behind another owner")
```

Wrong values of a slot, records of other units, records without a value,
decisions gold does not have:

```text
b1  ae.teae.end with 29 days: both tables 24 of 24; "wrong by value, and these data cannot show it"
b2  ae.related.values with a value no record has: the same
b3  ae.related.values ["PROBABLE", "POSSIBLE"] for ["POSSIBLE", "PROBABLE"]:
    decisions a reviewer would have to change: 1; both tables 24 of 24; "these data cannot show it"
c2  a record of a unit the catalog does not have, else the records of arm C: both tables 24 of 24;
    "records for decisions that gold does not have: tfl.population (tfl-no-such-unit)"; "not every score is 100%"
h1  stage T, the rule of the safety set and the percent format wrong: decisions a reviewer would have to change: 1;
    "records of units that are not scored here, ignored: 26"; visible 18 of 24, twin 14 of 24;
    "L7 tfl-ae-summary tfl.percent.format 6  6 of 6" and "10  10 of 10"
d1  tfl.columns.total with the status asked and no value (it has a house default):
    asks: 1 given, 0 in gold; valid: no (compile: ... 'total.mode' is not defined); 0 of 24;
    "build  tfl-ae-summary  tfl.columns.total  24  24 of 24"
d2  ae.teae.end in conflict, no value: valid: no (compile: ADAE: no value for ae.teae.end); owner build, ae.teae.end
e1  pop.efficacy.rule stated, which gold does not decide: both tables 24 of 24; listed; not 100%
e2  the same with the table on the efficacy set: valid: no (results: grouping 'Grp_TRT01P': no record ...);
    owner build, "tfl.population, pop.efficacy.rule", confirmed 24 of 24
e4  tfl.population = per_protocol: valid: no (compile: entry tfl.population has no alternative 'per_protocol')
e5  a value that is no object: valid: no (compile: tfl.population: a value is a mapping with a rule)
i1  the quote of ae.teae.end is the letter e: "case hand01, arm R: every score is 100%"
```

The four scores, counted by hand before the run. The gold table has 6
rows and 4 columns. In f1 the candidate has 4 of the rows and 3 of the
columns: 16 gold cells are in rows both have, and 12 of them are in
columns the candidate has.

```text
f1  rows ANY, SERIOUS, FATAL and no total column
    cells correct: 12 of 16 (rows both have); 12 of 24 (outputs produced); 12 of 24 (all); strict 0; lenient 0
    L5 tfl.ae.summary.rows 6 cells; L5 tfl.columns.total 4; L5 "tfl.columns.total, tfl.ae.summary.rows" 2
    axis rows: L5, "tfl.columns.total, tfl.ae.summary.rows", confirmed yes
f2  the output not included: produced 0 of 1; 0 of 0; 0 of 0; 0 of 24; strict 0; lenient 0
f3  the five rows in another order: 24 of 24 three times; strict 0; lenient 1; axis rows L7 tfl.ae.summary.rows
```

Defects of my own in a step of the build, no decision changed:

```text
g1  the layout orders the columns by the other rule: 24 of 24; strict 0; lenient 1;
    "axis columns of Out_AESUM: layer L7, decision -, ... layout:tfl-ae-summary/columns"
g2  every percent rounded to a whole number before it is shown: visible 19 of 24, twin 18 of 24;
    "L6  -  -  5" and "L6  -  -  6", first element ard:An_AESUM_ANY_Tot/Mth_CatSumm_pct/Grp_Total_AESUM_1
g3  one record of ADAE made serious: 22 of 24; "L4  -  -  2  -  adam:ADAE.AESER"
g4  g2 and tfl.population = randomized at once: twin "L5 tfl-ae-summary tfl.population 11  5 of 11"
```

E. Defects planted in the scorer, rule R5 (`mutants.py`). For each: do
the checks of the gate notice on HAND01 (`gate.hand_table`,
`gate.control`, `gate.arms`, `defects.suite`) and on kit 7 of the gate
seed (`kit.score_kit`, then `kit.planted`), each with new machines; and
where they do not, do the tests of section A, first run.

```text
M0  nothing planted                                  nothing fails; sweep of kit 7: 28 values, 244 owned
M1  the walk skips layer L4                          suite: S2-set-rule, S3, S10 fail; kit: S3 fails, sweep 66 problems
M2  confirm says yes and builds nothing              NO CHECK OF THE GATE; sweep: 244 owned, 0 problems
       tests: FAILED test_the_standard_alone_cannot_build_the_chain
M3  every second wrong cell gets no owner            NO CHECK OF THE GATE; sweep: 131 owned, 0 problems
       tests: FAILED test_the_standard_alone_cannot_build_the_chain
M4  attribution returns nothing                      arm S, suite, kit fail; the sweep itself: 0 owned, 0 problems
M5  the cells of the header row always count right   NO CHECK OF THE GATE
       tests: FAILED test_a_planted_defect_is_detected_and_attributed[S2-set]
M6  the reading score calls every value right        control (HAND01) and kit fail
M7  arm C takes the gold records, reads no document  HAND01: NOTHING (check 7 passes); kit: kit.planted returns False
M8  the owner is the first differing decision,       NO CHECK OF THE GATE; sweep: 244 owned, 0 problems
    whatever it decides                              tests: FAILED test_two_wrong_decisions_behind_one_cell_have_one_owner
M9  the two axes always count as equal               suite: S9 silent; kit: 1 disagreement with the matrix, sweep 1 problem
M10 every candidate is built from the gold vector    arm S, suite, kit fail; sweep 22 problems
M11 layers L5 and L7 exchange their names            suite: S2-set, S4, S5 fail; the sweep itself: 0 problems
```

F. Kits of a seed of my own (`own_kits.sh`).

```text
$ flock ... specfirst gen kits --seed review-r1a --count 3 --out /root/scratch-review-read1a/kits
kit 1 of the set: sfhxnu89, train, 121 files; 13 of 22 decisions separated on the twin
kit 2 of the set: sfnbgbn7, train, 120 files; 16 of 21 decisions separated on the twin
kit 3 of the set: sfwtee7d, train, 120 files; 15 of 21 decisions separated on the twin
$ flock ... specfirst score kits /root/scratch-review-read1a/kits
kit sfhxnu89 (kit-001), train: 3 arms; 167 subjects in the visible data, 179 in the twin; 22 decisions of the slice, 10 stated
  S9-sort (L7): silent: tfl.columns.arms (tfl-ae-summary): {"rule": "ascending_dose_placebo_first"} becomes {"rule": "protocol_order"}. visible every score 100%; twin every score 100%; the matrix: unseparated on the twin
  (S3-window, S5-column and S10-frozen: not planted)
planted defects on 3 kits: per defect, the kits by outcome
  S3-window (L4): detected and attributed on 1 kits; not planted on 2
  S5-column (L7): detected and attributed on 2 kits; not planted on 1
  S9-sort (L7): detected and attributed on 2 kits; silent on 1
  S10-frozen (L4): detected and attributed on 1 kits; not planted on 2
  (the six others: detected and attributed on 3 kits)
sweep of the matrices: 83 other values, each as the one wrong decision of a candidate: 61 shown on the twin, 0 on the visible data only, 22 silent; 666 wrong cells and axes owned by the changed decision and confirmed; 0 problems
gold built again is the gold of the kit: 3 of 3 kits
parser control 100% in both stages: 3 of 3 kits
planted defects that failed: 0
disagreements with the matrices of the kits: 0
every defect that applies is detected and attributed on at least one kit: yes
the checks fail on their planted defects: yes
kits: PASS
```

G. Candidates of my own on the ten kits of the gate seed
(`kit_probes.py`; the gold check of each kit first).

K1, arm S at stage T, the owners (the report gives the counts of cells
only). Three of the ten kits:

```text
kit 2 (sfmyncmq), arm S, stage T: wrong by value: tfl.population, tfl.columns.total, tfl.percent.format
   visible: 6 wrong cells; L5 tfl.population: 6 cells, confirmed 0 | axis columns: L5 tfl.population, tfl.columns.total confirmed True
   twin: 10 wrong cells; L5 tfl.population: 10 cells, confirmed 4 | axis columns: ...
   silent: []; behind: {'tfl.percent.format': {'visible': 6, 'twin': 6}}
kit 3 (sfg5vbvq), arm S, stage T: wrong by value: tfl.columns.total, tfl.percent.format, tfl.rounding.rule, tfl.ae.summary.rows
   twin: 7 wrong cells; L7 tfl.columns.total, tfl.percent.format, tfl.rounding.rule, tfl.ae.summary.rows: 7 cells, confirmed 7
kit 9 (sfyf9ekd), arm S, stage T: wrong by value: tfl.population, tfl.columns.arms, tfl.columns.total, tfl.percent.format, tfl.rounding.rule
   twin: 24 wrong cells; L5 tfl.population: 18 cells, confirmed 14; L5 tfl.population, tfl.columns.total: 6 cells, confirmed 5
arm S, stage T, 10 kits: 188 wrong cells on both datasets, 146 confirmed
```

K2, two wrong decisions at once: per kit, each of four module decisions
that the twin separates with each of three table decisions that it
separates (of `tfl.percent.format`, `tfl.rounding.rule`,
`tfl.columns.total`, `tfl.columns.arms`), 12 candidates a kit. For every
wrong cell I also know which of the two decisions makes it wrong alone.

```text
kit 1 (sfpbt5zj): 4 module decisions x 3 table decisions = 12 candidates with two wrong decisions; wrong cells 247: owner is the one cause 173; owner is the decision that does not change the cell alone 56 (of them confirmed 0); owner is both decisions and one changes it 0; both change it 18; neither alone 0
     visible, (header) / Total: owned by L4 trt.planned.source (confirmed False); wrong under tfl.columns.total alone
kit 3 (sfg5vbvq): ... twin, Fatal adverse event / Placebo: owned by L4 trt.planned.source (confirmed False); wrong under tfl.percent.format alone
all: {'candidates': 120, 'cells': 2018, 'right': 1410, 'other': 464, 'both': 136, 'neither': 0, 'other_confirmed': 0, 'not_listed': 0, 'wider': 8}
```

`other`: the owner is only the decision that alone leaves the cell right.
`wider`: the owner is both decisions and one of them changes the cell.
`not_listed`: a wrong decision that is neither an owner somewhere nor
listed as silent or behind.

K11, a module decision that the matrix of the kit marks unseparated on the
twin, and that alone gives the gold tables on both datasets, wrong
together with one table decision:

```text
kit 1 (sfpbt5zj): 10 unseparated pairs of module decisions, each with tfl.percent.format = {"rule": "one_decimal_always"}
   pop.safety.rule = {"rule": "randomized_and_dosed"} (alone: every score 100%, silent True) with tfl.percent.format = {"rule": "one_decimal_always"}: 8 wrong cells, 6 owned by pop.safety.rule at ['L4'], first element adam:ADSL.SAFFL, confirmed 0; behind: []; silent: []
   pop.safety.grouping = {"rule": "actual"} (alone: every score 100%, silent True) with ...: 8 wrong cells, 8 owned by pop.safety.grouping at ['L5'], first element ars:An_AESUM_FATAL, confirmed 0; behind: ['tfl.percent.format']; silent: []
kit 9 (sfyf9ekd): 8 unseparated pairs of module decisions, each with tfl.percent.format = {"rule": "one_decimal_zero_blank"}
   trt.end.source = {"rule": "ds_date_when_ex_missing"} (alone: every score 100%, silent True) with ...: 7 wrong cells, 7 owned by trt.end.source at ['L4'], first element adam:ADSL.TRTEDT, confirmed 0; behind: ['tfl.percent.format']; silent: []
all: {'candidates': 82, 'wrong cells': 782, 'owned by the unseparated decision': 69, 'of them confirmed': 0, 'candidates in which it owns a cell': 9}
```

K3, a wrong value of a slot that no matrix holds:

```text
kit 7: ae.teae.end = {"days": 29, "rule": "last_dose_plus_days"}; in the matrix: None; wrong by value: ['ae.teae.end']; visible 2 wrong, twin 2 wrong; twin: L4 ae.teae.end: 2 cells, confirmed 2; silent []
kit 7: ae.teae.end = {"days": 330, ...}; ... visible 2 wrong, twin 5 wrong; twin: L4 ae.teae.end: 5 cells, confirmed 5
kit 9: tfl.columns.total = {"control": "No Such Arm", "rule": "active_arms"}; in the matrix: None; ... twin: L5 tfl.columns.total: 5 cells, confirmed 5
kit 2: ae.related.values = {"rule": "stated_list", "values": ["PROBABLE", "POSSIBLE"]}; in the matrix: None; wrong by value: ['ae.related.values']; visible 0 wrong, twin 0 wrong; twin: ; silent ['ae.related.values']
(the gold list in the other order: the same in kits 1, 2, 3, 4, 6, 8 and 10; kits 5, 7 and 9 state one value)
```

K4, arm C on a document of the kit that says something else, in memory:

```text
kit 1: the document arm C reads is gold/docs/sap.md of the kit: True; 46 lines
   stage C: without [5/s1] of tfl.columns.total: 100%: False; wrong by value: ['tfl.columns.total']; twin 5 wrong cells
   stage T: without [5/s1] of tfl.columns.total: 100%: False; wrong by value: ['tfl.columns.total']; twin 5 wrong cells
kit 7: ... stage C: '[3/s1] Treatment emergence ends 30 days after the treatment end date.' with one day more: 100%: False; wrong by value: ['ae.teae.end']; twin 2 wrong cells; L4 ae.teae.end: 2 cells, confirmed 2
(the ten kits: the document is the file of the kit; without the statement of one stated table decision
 the control is not 100% in either stage, and the decision wrong by value is that one)
```

K5, "a percent rounded twice": a hook of my own rounds every percent of
the results to two decimals, half up, before the grid rounds it to one.
No decision is changed.

```text
kit 1, visible: 1 of 30 cells wrong [('4 (  7.5)', '4 (  7.6)')]; L6 -: 1 cells, confirmed 0
kit 1, twin: 2 of 30 cells wrong [('52 ( 94.5)', '52 ( 94.6)'), ('148 ( 86.5)', '148 ( 86.6)')]; L6 -: 2 cells, confirmed 0
kit 6, twin: 4 of 30 cells wrong [('22 ( 95.7)', '22 ( 95.6)'), ('1 (  4.3)', '1 (  4.4)'), ...]; L6 -: 4 cells, confirmed 0
(it shows in 8 of the 10 kits, on one dataset or both; not in kits 2 and 4)
```

K6, more rows than gold has (kits 3, 4, 5 and 8 state a list of rows):

```text
kit 4, twin: gold rows ['FATAL', 'SERIOUS', 'RELATED', 'ANY']; the candidate has the standard rows: correct 15 of {'shared_rows': 15, 'produced': 15, 'all': 15}; strict 0; lenient 1; extra rows ['Adverse event leading to discontinuation of study treatment'];  | axis rows: L5 tfl.ae.summary.rows confirmed True
```

K9, what of a grid the build score does not compare:

```text
kit 1: titles ['Summary of Treatment-Emergent Adverse Events']; footnotes []; {'values': 31, 'titles or footnotes differ': 0, 'and every cell is equal': 0}
(the ten kits, 293 values: 0)
```

K10, the sweep again, with two counts the sweep does not make:

```text
after kit 10: {"axes that differ": 98, "axis owners": 98, "cell owners": 2209, "pairs with another number": 35, "pairs with the cells of the matrix": 258, "values": 293, "wrong cells": 2209}
   kit 3 tfl.columns.arms=protocol_order: matrix 16, scorer 0 wrong cells, axes rows/columns equal True/False, produced 1
(all 35: an axis of the candidate is not the gold axis)
```

H. The pilot (`pilot_probe.py`; it reads the fetch cache).

```text
`pilot.lines`: 45 lines; not in the gate log: []
cells by (reason, state): {('no_row', 'open'): 3, ('differs', 'decision'): 5, ('no_row', 'no_row'): 9}
AEREL in the reference ADAE: ['', 'NONE', 'POSSIBLE', 'PROBABLE', 'REMOTE']
  Related adverse event | Placebo | key '43 ( 50.0)' | arm S with RELGR1 '43 ( 50.0)'
  Related adverse event | Xanomeline Low Dose | key '72 ( 85.7)' | arm S with RELGR1 '72 ( 85.7)'
  Related adverse event | Xanomeline High Dose | key '70 ( 83.3)' | arm S with RELGR1 '70 ( 83.3)'
with RELGR1: correct 13 of {'shared_rows': 18, 'produced': 27, 'all': 27}
```

The second half is mine: the reference ADAE with a column RELGR1 added in
memory, RELATED where AEREL is POSSIBLE or PROBABLE, and arm S built on
it.

I. A kit whose files are not the files of its manifest (`drift.py`: a
copy of kit 2 of my seed, one file changed, the manifest left as it was).

```text
== class: gold/decisions.jsonl: the class of tfl.population (stated) is now gold_quirk
   specfirst score kit --arm C: exit 0
          document_rule                       7  7 of 7      7 of 7      7 of 7      7 of 7
          gold_quirk                          1  -           -           -           -
      case sfnbgbn7, arm C: every score is 100%
   specfirst score kit (all the gate runs on a kit): exit 1
          problem: tfl.population = safety: the reading score has wrong by value: nothing
   specfirst gen verify --no-mutation: exit 1
      file gold/decisions.jsonl: the hashes differ
== identifiable: gold/decisions.jsonl: tfl.output.include is now marked unseparated (the matrix file is not changed)
   specfirst score kit --arm C: exit 0
   specfirst score kit (all the gate runs on a kit): exit 0
   specfirst gen verify --no-mutation: exit 1
== truth: twin/truth/subjects.jsonl: one byte more
   specfirst score kit --arm C: exit 0;  specfirst score kit: exit 0;  specfirst gen verify --no-mutation: exit 1
```

J. The commands, as a user runs them, on kit 3 of my seed (`cli.sh`).

```text
$ specfirst score kit KIT --decisions gold.jsonl                  (the gold records, as a candidate writes them)
case sfwtee7d, arm R: every score is 100%
$ specfirst score kit KIT --stage T --decisions left.jsonl --questions questions.jsonl --unmapped unmapped.jsonl
  asks: 1 given, 0 in gold (decisions with the status asked), 0 of them right; precision 0.00, recall none to judge
  unmapped: 1 given, 0 in gold (what the catalog lacks), 0 of them right; precision 0.00, recall none to judge
    tfl.percent.format (tfl-ae-summary), document_rule: gold {"rule": "one_decimal_always"}; the candidate (default) has {"rule": "one_decimal_zero_blank"}
  L7     tfl-ae-summary     tfl.percent.format           8  8 of 8     layout:tfl-ae-summary/formats
$ specfirst score defects --kit KIT
planted defects on sfwtee7d: 13 of section 9.5 with the one planted at two layers; 3 do not apply to the slice; 9 of 10 planted here; 9 of 9 detected and attributed; 0 silent on these data
```

In `left.jsonl` two table decisions are left out: one that gold takes from
the house (right by default) and one that gold states.

K. Small things. `git diff --name-only d5c7e50 fd02360 -- PLAN.md standard
third_party env kits` prints nothing. `CLAUDE.md` has 59 lines. The IDs
and the file counts of the ten kits in the gate log of read-1a are those
of `docs/reports/gen-2a.gate.log`. The catalog entry `ae.related.values`
has `house_default: null`. The analyses of the house template of the
output use two methods, a count (`Mth_Count`) and a count with a percent
(`Mth_CatSumm`); the output has one title and no footnote.

## What I could not review

- The gate run itself. Its clean clone under `/tmp` is gone; I read the
  log. Section B shows that the code of the commit, on kits with the same
  manifests, prints the lines of checks 5 to 10 and 12 of that log. The
  1028 tests of check 4 I did not run as a whole: 83 of them, the unit
  tests of the scorer, in section A, with the one test of check 11.
- The run of CI on GitHub that the report quotes.
- The compiler and the templates of std-1, yamaa, the Python result
  engine, `specfirst.gen.display`, `gold.resolve_groupings` and the
  matrices of the kits: used, and read where I needed them, not reviewed.
  They are gen-2a's, real-2's and std-1's, and their reviews hold them. A
  defect in code that the gold build and the candidate build share is
  invisible to a scorer that compares the two; the kit holds its gold
  against a hand calculation (gen-2a, P2).
- The R engine: the scorer does not use it.
- `asks` and `unmapped` against a gold that has some, and citations into
  natural-form documents: no kit has them. The unit tests hold the two
  rates on toy records.
- Whether what the base session relayed on 2026-11-17 is what the owner
  said (ADR-008, "For the owner", point 1): the repository has that one
  sentence.

## Findings

### R1. BLOCKS: the part reads the text of its gate by a table of its own, and the gate ran before the owner was asked

The gate text (ADR-005, decision 1, row read-1a): "The planted defects of
section 9.5 that apply to the slice are each detected and attributed to
the right layer. The parser control scores 100%."

How the part reads it (ADR-008, decisions 7 and 8; `DEFECTS` in
`src/specfirst/score/defects.py`; `kit.score_set`):

- "that apply to the slice" is a table that the part wrote. Of the twelve
  defects of section 9.5, three do not apply (a quantile, a p-value, a
  baseline). Nine apply. Two of the nine are planted as "the nearest thing
  the slice has": "an unstable sort" as the other value of the decision
  `tfl.columns.arms`, "a frozen site list" as the list of related
  causality values.
- "each detected and attributed" is, on the hand-made study, all ten
  plants. On the kits it is: no plant fails on any kit, where a plant may
  be `silent` or `not planted` on a kit; and each defect passes on at
  least one kit of the ten.

What I was asked to judge: does this reading weaken the gate, or is it
true by construction, and is it the owner's to accept.

It is not true by construction. On HAND01 all ten plants must show and
must be owned by their layer, with numbers of cells that I counted again
by hand. On a kit a plant that shows and is owned by another layer fails,
and a plant that is called silent while the matrix of the kit says
`separated` fails. Section E: the suite fails on a scorer that skips a
layer (M1), owns nothing (M4), builds every candidate from gold (M10) or
exchanges the names of two layers (M11). A set of kits can fail the last
criterion for an honest reason: of my three kits, one has a window of
days and one a list of two causality values (section F).

It asks less than the words of section 9.5 in three places. Each is a
choice, and none is hidden: ADR-008 and the report name them.

1. Which defects apply is decided by two criteria, not by one. Three
   defects are left out because the table has nothing of the kind. That is
   a fact of the house template (section K). Two others have nothing of
   the kind either, no sort that can be unstable and no list of sites, and
   are planted as the nearest thing. By the first criterion seven of the
   twelve apply; by the second at least ten do: "a p-value rounded twice"
   has a nearest thing as well, a percent rounded twice, and it can be
   planted. I planted it in the results (G, K5; a coarser one in D, g2):
   it shows in eight of the ten kits, and the scorer owns it at L6 with
   no decision, as it should. The table has nine.
2. "An unstable sort" is a defect of a build. The suite plants a decision
   read as its other value, and asks that the axis be owned by layer L7
   and by that decision. That is a candidate the sweep has anyway. The
   case that section 9.5 names, an order that is wrong while no decision
   is, is not in the suite. The scorer handles it: with the layout
   ordering the columns by the other rule and every decision at gold, the
   axis is owned by L7 and by no decision (D, g1).
3. On the kits "a frozen list" is planted by taking the records of one
   causality value out of the visible data of the case
   (`defects._frozen`). "Caught on the twin only" is then true of the
   visible data by construction. On HAND01 it is not: the visible data of
   that study lack the value as they are.

What the kits allow, `silent` and `not planted`, I find sound. A plant
that changes no cell of either dataset cannot be found by a table, and
the scorer does not only say so: it builds the gold vector with the one
value, and the matrix of the kit is asked the same question (M9 and M10
fail there). That a wrong value of an unseparated decision is compared by
value is the owner's answer on decision 6 of ADR-007. `not planted` is a
fact of the gold vector of a kit: no window of days, no total column, a
list of one value.

So the reading hides no failure of the scorer that I could find. But that
is my opinion of a choice, and the choice is not mine to accept. Lesson 47
of `docs/lessons.md`, written after the same thing happened in gen-2a: "A
word of a gate text that is filled in by a table the work itself writes is
a changed gate: a case of PLAN.md section 2.3, put to the owner before the
gate runs, not listed for the owner afterwards." ADR-008 says of itself
that this is such a word, and that "the rest of this reading has not been
put to the owner as a question. The independent review is asked to judge
it." Its status is "decided in read-1a ... by the executor"; "The
decisions stand unless the owner objects." The gate ran on `55dba60` with
this reading, and the reading is listed for the owner afterwards, as point
1 of four.

One thing of the history belongs here (`git diff 134c6f7 55dba60` of
`defects.py`). At the end of the first half the suite passed when every
planted defect was detected and attributed, and the frozen list was not
planted where the visible data hold every value. When the kits came, the
state `silent` was added and the frozen list got its changed visible data.
Both are reasonable, and both are a gate that moved to fit what the kits
gave.

Plainly: this is a case of PLAN.md section 2.3 as lesson 47 reads it. It
must be put to the owner before the merge, and until it is, the gate has
passed on the executor's reading only. My signature would make the gate
pass on a reading of its text that lesson 47 gives to the owner. I do not
sign. What settles the finding is at the end.

### R2. Does not block: when two decisions are wrong, the owner of a wrong cell is often a decision that does not change it

Section 9.4: "For each wrong cell, walk the gold graph upstream and
compare candidate and gold artifacts layer by layer. The first element
that differs owns the error. Report errors by owning unit and layer. An
end-to-end failure then becomes a task for one unit."

What the scorer does (`attribute._own`; ADR-008, decision 5). It starts at
the far end. If any ADaM column that the analyses of the cell read, or
that such a column derives from, has another value in any record, the
cell is owned at L4 by the decisions that decide that column. It does not
ask whether the difference reaches the cell: whether a result of the cell
differs. Every row of events reads ADAE.TRTEMFL and every row reads
ADSL.SAFFL, so one record that differs in such a column takes every wrong
cell below it.
The same holds one layer down: an analysis that is defined in another way
owns the cell at L5 although its results are the same. The claim is then
run, and `confirmed` says that it does not hold. The walk does not go on.

Evidence.

1. HAND01 (D, a). `ae.teae.end` read as "no end" changes two cells of the
   twin. `tfl.percent.format` read as the other alternative changes ten
   others. With both wrong, the twin has "L4 mod-ae-emergence ae.teae.end
   12 cells, confirmed 2 of 12": ten cells of the display are given to a
   module, at the layer of the analysis data. The report of the candidate
   has no line that says whose they are; `tfl.percent.format` is not
   listed as "behind another owner", because it owns cells of the visible
   data.
2. The ten kits (G, K2). In 120 candidates with one module decision and
   one table decision wrong, both of them separated on the twin, 2,018
   cells are wrong. 464 of them, 23%, are owned by the decision that alone
   leaves the cell right; 1,410 by the one that changes it; for 136 both
   do; 8 are owned by both where one does.
3. A decision that the kit says cannot be shown (G, K11).
   `docs/state/gen.md` says of an unseparated decision: "a table that
   differs is not caused by one". In 9 of 82 candidates, 69 wrong cells
   are owned by a module decision that the matrix of the kit marks
   unseparated and that the scorer itself calls silent when it is wrong
   alone. In kit 1 the rule of the safety set owns 6 of 8 wrong cells at
   L4, nothing is listed as behind, and the decision is not listed as
   silent either, because it now owns cells.
4. The gate's own arm S (G, K1). At stage T on the ten kits 188 cells are
   wrong and 146 owners are confirmed. In kit 2 all six wrong cells of the
   visible data are owned by `tfl.population` at L5, confirmed 0 of 6;
   the line `behind` of the same result gives `tfl.percent.format` six
   cells of the visible data when it is wrong alone. In kit 3 the owner
   of every wrong cell is four decisions at once, all that are wrong;
   with all four at gold the candidate is gold, so "confirmed 7 of 7"
   says nothing.
5. A defect of the build with a wrong decision (D, g4): all eleven wrong
   cells of the twin are owned by `tfl.population`, five confirmed; the
   cells that only the rounded results make wrong are among the other
   six.

What is right in it. `confirmed` is honest: of the 464 and of the 69, not
one is confirmed. No wrong decision goes unlisted (K2, `not_listed` 0).
With one wrong decision, or one defect of the build, I found no wrong
owner in anything I ran (D, g1 to g3; G, K3, K5, K10). And the words of
section 9.4, read as "the element furthest upstream that differs", are
what the code does.

Why it does not block. The gate asks for one planted defect at a time,
and where the owner is wrong the scorer says in the same line that its
claim did not hold. Why it matters all the same: a reader is wrong in
several decisions at once, the arm S of this very report in up to five,
and the table "by owning unit and layer" then counts the errors of the
table family as errors of a module. Until this is settled I would report
no such table for a candidate with more than one wrong decision, and I
would read an owner that is not confirmed as no owner.

What is wrong in the documents as they stand. ADR-008, decision 5: "A
second wrong decision behind the same cell shows when the first is right;
the report lists it as 'behind another owner', with the cells it changes
alone on gold." In evidence 1 and in kit 1 of evidence 3 it is not
listed. The limits of the report and the handover (`docs/state/read.md`:
"`result.owners[dataset]` ... the owner of every wrong cell") say nothing
of an owner that does not touch its cell.

What would settle it, one of two. (a) An element upstream owns a cell only
when its difference reaches the cell: when every result of the cell is
the same in both builds, the owner is the display, whatever differs above;
and a claim that fails when it is run is not kept as the owner. With a
test that has a module decision and a display decision wrong at once, and
pairs like those of K2 and K11 in the check of the kits. (b) Or the walk
stays, and the report, the summary by unit and layer, ADR-008 and the
handover say that an owner that is not confirmed is a claim that failed,
and count it apart.

### R3. Does not block: what the checks of the gate print and cannot fail on

The report says of the sweep: "All 2307 wrong cells and axes are owned by
the changed decision, and its gold value gives the gold text again." The
check `kits of gen-2a` prints "each owned by the changed decision and
confirmed". Section E:

- "Confirmed" cannot fail in the suite or in the sweep (M2). A candidate
  with one wrong decision, built again with that decision at its gold
  value, is the gold vector. The clause is true of every such candidate,
  whatever the scorer does. What holds `confirmed` is two unit tests on
  HAND01 with two wrong decisions.
- "Every wrong cell" is not asked (M3). `defects.judge` and `kit.sweep`
  walk the list of owners; neither holds its length against the number of
  wrong cells. A scorer that leaves every second wrong cell without an
  owner passes the suite on HAND01, the suite on the kit and the sweep,
  which then counts 131 where it counted 244. It is true today: I counted
  (G, K10), 2,209 wrong cells with 2,209 owners and 98 axes with 98
  owners, which is the 2,307 of the log.
- "Owned by the changed decision" can fail in one way only, as "no
  decision": a candidate with one wrong decision has no other decision to
  name (M8).
- The sweep does not hold the layer (M11). It prints "the layer at which
  each decision owns its cells". The ten plants hold a layer; the 293
  values of the sweep do not.
- On a kit nothing holds how many cells are wrong (M5). The matrix of the
  kit has that number for every pair. I compared (K10): the same number in
  258 of 293 pairs, and in the other 35 an axis differs, where the matrix
  counts places and the scorer counts by label.
- The line "the control fails on the changed document: yes" of check 7
  does not go through `scorer.control` (M7). `gate._changed_document`
  parses the changed text itself and calls `scorer.run`. An arm C that
  reads no document passes check 7. On the kits the same check does go
  through `scorer.control` and fails as it should.
- Check 9 passes when a defect cannot be planted on HAND01:
  `defects.suite` returns whether all that were planted passed. A unit
  test holds "10 of 10 planted here". (Read in the code, not run.)

M2, M3, M5 and M8 are noticed by the unit tests on HAND01, check 4 of
the gate, and by nothing else. So the gate as a whole notices them; check
12, the one that "finishes on the kits", does not. M7 is noticed on the
kits and not on HAND01. Lesson 47 has the remedy in its second
half: a check that is true by construction says what would make it fail
and plants that. What would settle it: the sweep holds the number of
owners against the number of wrong cells, and the number of wrong cells
of the twin against the matrix where the axes are equal; a few pairs of
two wrong decisions of the kit's own matrix give `confirmed` something to
fail on; check 7 changes the document of the case and calls
`scorer.control`; and the report says "owned by the changed decision" for
the 2,307, without "confirmed".

### R4. Does not block: two measures of the reading score

- A list that is a set is compared in its order (D, b3; G, K3). The entry
  `ae.related.values` reads "its causality is one of {values}". A
  candidate that names the values of gold in another order has "decisions
  a reviewer would have to change: 1", in seven of the ten kits, and the
  line "these data cannot show it", which is true of any data: it is the
  same rule. For `tfl.ae.summary.rows` the order is the decision; here it
  is not. `test_a_slot_is_compared_exactly` holds the behaviour for every
  list. The catalog types both slots as lists, so the place to say which
  list is a set may be the catalog, and that is the std track's.
- A quote of one letter passes both dimensions of a citation (D, i1).
  Section 9.1 measures "quote found; overlap with the gold anchor". Under
  the right anchor any piece of text that stands there scores as the gold
  quote does. In standard-form documents the anchor carries the meaning,
  and little is lost. In natural-form documents (gen-3a) a reader could
  cite a word. The handover names citations into natural-form documents
  as open; this belongs to that item.

### R5. Does not block: "0 unexplained" on the pilot says less than it seems to

`pilot.run` gives a cell the state `unexplained` only when the candidate
has the cell and no other value of one table decision gives the key's
text. A cell of a row that arm S does not have is always `open` or
`no_row` (H: the three and the nine). So of the 17 cells, 5 are explained
by a build each, and 12 are classed by the crosswalk of rows and by the
list of rows of the catalog; for those 12 the count of unexplained cells
could not have been anything but 0.

The classes are right as far as I can tell. The catalog has five row
codes. And the three `open` cells are open for the reason given and for
no other: with the variable the reference ADaM lacks, written as the
example's own subset reads the causality, arm S has the key's text in all
three (H). The report would be exact with: 5 explained by a decision; 12
in rows that arm S does not build, 3 of them for a variable and 9 for the
catalog; and of the 15 cells of the rows both tables have, none
unexplained. It is a report and decides nothing in the gate.

### R6. Does not block: the scorer does not hold the files of a kit against its manifest (rule R3)

"Every replay checks for drift first." A kit lists the SHA-256 of every
file in `kit.yaml`, and `specfirst gen verify` checks them. The scorer
reads `kit.yaml` and checks no hash (`kit.load`). Its gold check catches
what changes a value: the data, a gold decision, a grid, a result. It
does not catch what changes how a decision is scored (I). With the class
of one stated decision set to `gold_quirk` in `gold/decisions.jsonl`,
`specfirst score kit --arm C` exits 0 with "every score is 100%" on seven
document rules in place of eight, and a candidate would be scored the
same way; only the sweep of the full run notices. With `identifiable`
changed, nothing of the scorer notices. What would settle it: the hash
check of the kit before anything is scored, as `specfirst gen verify`
does it.

### R7. Does not block: records

- `docs/state/read.md` lists read-1a under "Passed", with the date
  2026-11-17 and with this file as its review. At `fd02360` no review had
  run, and the gate ran on 2026-11-18. A part has passed when its gate and
  its review have (section 2.4).
- ADR-008, decision 5, the sentence quoted in R2.
- ADR-008, "For the owner", point 1: what the base session relayed is in
  the repository as one sentence, without the question and without the
  words of the answer. The answer on decision 6 of ADR-007 is recorded in
  full; this one should be, in whatever settles R1.
- The report gives arm S on the kits as counts of cells. The owners of
  those cells are part of what the scorer says, and they are where R2
  shows first (G, K1).
- `specfirst.score.reading`: a record for a decision that gold does not
  make, whatever its unit, is listed under "records for decisions that
  gold does not have", and the result then reads "not every score is
  100%" although every score is (D, c2 and e1). The handover says "A
  record of a unit that is not scored is counted and ignored", which is
  true of the units that gold has.

## Checked and found correct

- Scope and rules. `PLAN.md`, `standard/`, `third_party/`, `env/` and
  `kits/` are not in the diff. The 29 files are code, tests, documents
  and two gate logs. No kit, no data file. The report and the logs print
  the cells of the adverse event summary of CDISC's ARS example, as the
  report of real-3a does. The identifiers are HAND01 and generated ones.
  `CLAUDE.md` has 59 lines. HEAD adds documents only to the commit of the
  gate.
- The gate table. 14 checks, the environment first, the cache checked
  before and after. The checks of the scorer print what they count. A
  folder without a kit fails check 12.
- The report against the log, and the log against the code. Every line of
  the 15 code blocks of the report is a line of the gate log but the
  command (C). The sums of the verdict are the sums of the log: 293, 209,
  83 and 1, 2,307; arm S between 0 and 25 of 15 to 30 cells. The checks 5
  to 10 and 12, run again on kits with the manifests of the gate, print
  the lines of the log and nothing else (B).
- The hand-made study. I worked the two gold tables out from the lists of
  subjects and events in `hand.py`, 48 cells: they are `EXPECTED` and the
  tables of the report. The same for the cells that S1, S2 (both plants),
  S3, S4, S5 and S10 change: 2 and 2; 10 and 8; 0 and 8; 0 and 2; 2 and
  1; 6 and 6; 0 and 2.
- The four scores. Counted by hand on a candidate without two rows and
  without the total column (12 of 16, of 24 and of 24), an output that is
  not included (0 of 0, 0 of 0, 0 of 24), rows in another order and rows
  that gold does not have (strict 0, lenient 1) (D, f1 to f3; G, K6; F,
  arm S of kit 1). The header row is a row. Where the axes are the gold
  axes the number of wrong cells is the number the matrix of the kit has
  (K10).
- What the build score compares. Cells and the two axes; not titles and
  not footnotes. In this slice that is the whole text of the grid: no
  value of any decision changes a title or a footnote (G, K9). It will
  not be so for every family.
- The reading score. Value, status, quote and span each fall alone on
  their planted record (the unit tests). A decision left out takes the
  default; one without a default stays open; a second record for a
  decision is a problem and the first is taken; a record without a value,
  a value that is no alternative and a value that is no object stop the
  build with the rule that failed, and the build has that decision as its
  owner (D, d1 to e5).
- Attribution of one thing. One wrong decision, a wrong value of a slot
  that no matrix holds, a defect in the layout, in the results or in the
  ADaM data with no decision changed: the right layer, the right decision
  or none (D, g1 to g3; G, K3, K5). 293 values of ten matrices: every
  wrong cell and every axis has an owner (K10).
- Arm C. The document it reads is `gold/docs/sap.md` of the kit, through
  the parser of the standard form. Without one statement, or with one day
  more in one statement, the control is not 100% in either stage, and the
  decision that is wrong by value is the one of the statement (G, K4). An
  arm C that reads nothing fails the planted check of the kits (M7). The
  defaults are the records of the house standard of the checkout; the
  house document of the kit is what their quotes are held against.
- Arm S. "Builds nothing on the chain" is a fact of `catalog@1` and of
  the compiler: the entry has `house_default: null`, and the compiler
  refuses ADAE without the decision ("compile: ADAE: no value for
  ae.related.values"). ADR-005, decision 3 covers it. It is point 2 for
  the owner, rightly.
- Gold. `kit.gold_problems` holds the scorer's build of the gold
  decisions against the grid as a whole, every result and every value of
  every ADaM column of the kit, in both directions, and the unit test
  plants four kinds of difference. The command line runs it before it
  scores a file of decisions. A scorer that builds every candidate from
  gold fails the suite and the sweep (M10).
- Kits of another seed. Three kits of my seed: the gold of each built
  again, the control 100% in both stages, no plant failed, no
  disagreement with a matrix, 83 values swept with no problem (F).
- The pilot. The numbers of the report are what `pilot.lines` prints (H,
  B). The five cells that differ are counts of zero, each made equal by
  the other alternative of `tfl.percent.format` in a build.
- Stage T. A module decision of the candidate is ignored there and the
  ADaM is that of gold (D, h1: the wrong rule of the safety set changes
  nothing, the wrong format owns its cells at L7). A case that scores a
  module at stage T is refused.

## What settles R1

It is not mine to choose, and it needs no change of the code.

1. The owner is asked, in the question dialog, whether ADR-008, decisions
   7 and 8, are the reading of the gate text for read-1a: nine of the
   twelve defects apply, two of them as the nearest thing the slice has;
   on the kits a plant may be `silent` or `not planted`, and each defect
   passes on at least one of the ten. The question, the options and the
   answer are recorded in ADR-008, as the answer on decision 6 is in
   ADR-007. If the owner approves, I would sign the same code for R1.
2. Or the owner asks for more. What I would put before the owner as the
   two things that cost little and that the scorer already does right:
   plant "an unstable sort" as a defect of the build as well, with no
   decision changed (D, g1); and plant the nearest thing of "a p-value
   rounded twice", a percent rounded twice (D, g2; G, K5).

R2 to R7 can be settled in the same pass or booked. Of R2 I ask at least
that the documents say what the scorer does (the sentence of ADR-008, the
limits of the report, the handover for read-2a). After that I read the
diff, the new log and the report again.

Verdict: NOT SIGNED
