# Review of the report slice-ae-summary (rule R7)

Date: 2026-11-19. Reviewer: a fresh-context session that did not write the
report, the code or ADR-016. Reviewed: the report as of `ede23d3` on
`track/read`, which is `7d2ff0a` (the report, ADR-016, lesson 69, the
state of the track) with the block of the last verification filled in
(`git diff 7d2ff0a ede23d3`: that block only, 21 lines of
`docs/reports/slice-ae-summary.md`), on top of `d7bea75` (the code) and
`1a94134` (main before the part); `git diff 1a94134 ede23d3`. Nothing was
committed, pushed or changed in the worktree except this file. Pass 2, at
the end of this file, reviews `d3974ec`, the fix of pass 1's findings. The
text of pass 1 was edited in pass 2 only to withhold what it named of dev
kits (the decision of finding 1, the entries of finding 3, the anchor the
reader cited); its numbers and findings are unchanged. No model was called. No value of a decision of a dev kit is
written here: decision IDs and counts only. `<home>` stands for the
Windows user's home folder; `$SPECFIRST_RUNS` for `<home>/AppData/Local/
specfirst-slice/runs`. My scripts lie in a folder of my own under
`<home>/AppData/Local/Temp/`; their outputs that hold dev values stay in the
WSL folder `/root/rv-slice-ae/`.

## What I checked and how

### 1. The numbers of the report against the records

`aggregate.json` (the executor's numbers per run) summed again by a script
of my own (`mytables.py`, not the executor's `tables.py`), and the cost
recomputed from each `run.json` and from the `result` event of each
`transcript.jsonl`.

The four scores, all 48 rows (kit x stage x arm x dataset), and the sums:

```text
$ python -I mytables.py          (counts and IDs only; the sums)
T all S visible: produced 4/4 cells 52/92 all 52/92 strict 0 lenient 0 pending 0
T all S twin:    produced 4/4 cells 44/92 all 44/92 strict 0 lenient 0 pending 0
T all R visible: produced 4/4 cells 92/92 all 92/92 strict 4 lenient 4 pending 0
T all R twin:    produced 4/4 cells 92/92 all 92/92 strict 4 lenient 4 pending 0
T all C visible: produced 4/4 cells 92/92 all 92/92 strict 4 lenient 4 pending 0
T all C twin:    produced 4/4 cells 92/92 all 92/92 strict 4 lenient 4 pending 0
C all S visible: produced 4/4 cells 31/80 all 31/80 strict 0 lenient 0 pending 12
C all S twin:    produced 4/4 cells 19/80 all 19/80 strict 0 lenient 0 pending 12
C all R visible: produced 4/4 cells 92/92 all 92/92 strict 4 lenient 4 pending 0
C all R twin:    produced 4/4 cells 92/92 all 92/92 strict 4 lenient 4 pending 0
C all C visible: produced 4/4 cells 92/92 all 92/92 strict 4 lenient 4 pending 0
C all C twin:    produced 4/4 cells 92/92 all 92/92 strict 4 lenient 4 pending 0
```

Every one of the 48 rows of the two tables "Stage T" and "Stage C" equals
the record (produced, the three denominators, strict, lenient, pending).
In every run `valid` is true, `failure` none, `waiting` 0, and the three
denominators coincide, as "Read with it" says.

The reading score by class and by unit (the sums over the classes, and
the units at stage C; the lines by class are left out here on purpose, see
finding 1):

```text
T class ALL S: dec 28 value 16/28 status 13/28 quote 28/28 span 13/28
T class ALL R: dec 28 value 28/28 status 28/28 quote 28/28 span 28/28
T class ALL C: dec 28 value 28/28 status 28/28 quote 28/28 span 28/28
C class ALL S: dec 85 value 42/85 status 34/85 quote 80/84 span 34/84
C class ALL R: dec 85 value 82/85 status 82/85 quote 84/84 span 81/84
C class ALL C: dec 85 value 85/85 status 85/85 quote 84/84 span 84/84
C unit mod-ae-emergence S: dec 16 value 4/16 status 2/16 quote 12/15 span 2/15
C unit mod-ae-emergence R: dec 16 value 16/16 status 16/16 quote 15/15 span 15/15
C unit mod-populations S: dec 17 value 10/17 status 9/17 quote 16/17 span 9/17
C unit mod-populations R: dec 17 value 14/17 status 14/17 quote 17/17 span 14/17
C unit mod-treatment S: dec 24 value 12/24 status 10/24 quote 24/24 span 10/24
C unit mod-treatment R: dec 24 value 24/24 status 24/24 quote 24/24 span 24/24
C unit tfl-ae-summary S: dec 28 value 16/28 status 13/28 quote 28/28 span 13/28
C unit tfl-ae-summary R: dec 28 value 28/28 status 28/28 quote 28/28 span 28/28
(arm C: every unit full; the lines by class of all three arms, not shown,
equal the report's cells as well)
```

Every cell of the three tables of "The reading score by class and by unit"
and of "R against S, and R against C" holds (+12, +40, +48 at stage T;
+40, +61, +73 and +3 at stage C; R - S at stage C counts the 12 pending
cells of arm S as wrong, as the report says).

Asks, unmapped, wrong decisions, silent decisions, pending, canaries,
denials (from the same script, one line per run, IDs only):

- Asks: only kit 7, stage C: arm R and arm C given 1, gold 1, hits 1;
  arm S given 0, gold 1. Every other run: 0, 0, 0. Unmapped: 0, 0, 0 in
  all 24 runs. As the report says.
- Arm R, values wrong: none at stage T; at stage C one decision of
  `mod-populations` (which one is withheld here, finding 1), in kits 5, 7
  and 15, its quote right, listed silent; none in kit 6. As the table
  "What arm R got wrong".
- Pending (ADR-014): arm S at stage C only, `ae.related.values`
  (mod-ae-emergence), 12 cells on each dataset summed over the four kits;
  each kit's count equals its row of the report's table at `ede23d3` (the
  counts by kit are withheld here, finding P2-2).
- Unseparated in gold, stage C: 4, 7, 4, 5 (kits 5, 6, 7, 15); stage T: 0,
  1, 0, 0. "4 to 7 per kit at stage C and 0 or 1 at stage T" holds.
- Canary counts of the 24 dev runs: 16,756 to 44,665, no hit. The pilot:
  2,918 (arm S) and 2,913 (arm R), no hit (finding 2).
- Permission denials: 3, 1, 1, 1, 1, 1, 2, 1 in the eight dev runs of arm
  R and 1 in the pilot run: 12. Every one is a Bash command inside the task
  folder: nine `cd <task>; ls -R ...; cat knowledge/...` (one per run),
  one `cat` of seven catalog entries, one `mkdir -p out` with an empty
  `unmapped.jsonl`, one `bin/check` by its absolute path.
  `tools_changed` is empty, `task_problems` empty, `command_problems`
  empty, `over_budget` empty in every run of arm R. As the report says.

The kits table: decisions and separated (21/16, 21/14, 21/16, 22/17) from
`kits.log`; the number of arms of each kit from `kit.yaml` (withheld
here, finding P2-2); tiers standard, full, ask,
standard (`documents.TIER_PLAN` of kits 5, 6, 7, 15 and `kit.yaml`); dev
by `SPLIT_PLAN` (5, 6, 7 dev, 8 to 14 test or train, 15 dev: the first four
dev kits); paragraph sources from `gold/docs/natural.json`: model 13, 26,
10, 9 and missing 1, 2, 2, 3, so 8 of 66. All hold. "38 of the 61
accepted paragraphs ... two equal" is the number of the gen-3a review, D9.

The cost, recomputed from the tokens with the prices of ADR-010, decision
7 (Opus 5.5: input 4.00, output 20.00, cache write 5 min 5.00 or 1 h 8.00,
cache read 0.20 per million). Every cache write of the nine runs is a
one-hour write (`usage.cache_creation.ephemeral_1h_input_tokens` equals
`cache_creation_input_tokens`; `ephemeral_5m` is 0):

```text
$ python -I cost.py
kit 5 T: turns 14 wall 33.3 api 26.2 in 16 out 3104 cw 25479 cr 140412 usd 0.294058 cli 0.2940584 | mine(split) 0.294058
kit 6 T: turns 13 wall 28.1 api 21.6 in 16 out 2621 cw 24262 cr 135913 usd 0.273763 cli 0.2737626 | mine(split) 0.273763
kit 7 T: turns 15 wall 33.8 api 26.9 in 16 out 3194 cw 27653 cr 144787 usd 0.314125 cli 0.3141254 | mine(split) 0.314125
kit 15 T: turns 15 wall 37.0 api 27.6 in 16 out 3245 cw 27356 cr 144820 usd 0.312776 cli 0.312776 | mine(split) 0.312776
kit 5 C: turns 25 wall 73.1 api 65.1 in 24 out 8026 cw 47742 cr 393092 usd 0.62117 cli 0.6211704 | mine(split) 0.621170
kit 6 C: turns 21 wall 59.5 api 50.3 in 18 out 6570 cw 46008 cr 249637 usd 0.549463 cli 0.5494634 | mine(split) 0.549463
kit 7 C: turns 23 wall 63.5 api 51.7 in 22 out 6551 cw 45351 cr 336859 usd 0.561288 cli 0.5612878 | mine(split) 0.561288
kit 15 C: turns 20 wall 65.5 api 56.7 in 18 out 7296 cw 44859 cr 231281 usd 0.55112 cli 0.5511202 | mine(split) 0.551120
pilot T: turns 16 wall 42.8 api 35.4 in 20 out 3135 cw 54953 cr 328163 usd 0.568037 cli 0.5680366 | mine(split) 0.568037
all   {'turns': 162, 'wall': 436.6, 'api': 361.5, 'in': 166, 'out': 43742, 'cw': 343663, 'cr': 2104964, 'usd': 4.0458, 'mine': 4.0458}
eight {'turns': 146, 'wall': 393.8, 'api': 326.1, 'in': 146, 'out': 40607, 'cw': 288710, 'cr': 1776801, 'usd': 3.4778, 'mine': 3.4778}
(models used in every run: claude-opus-5-5 only; unpriced models: none)
```

Every cell of the table "Cost per run" holds, and the CLI's figure equals
mine in every run. The overhead of the harness, from the `(exit 0, N s)`
lines of the 24 `.run.txt` files against the wall time of each record: 8
to 21 seconds, as the report says. The budget rule of ADR-016, decision 7
(`drive.py`: total so far plus the larger of USD 1 and twice the dearest
run, at most USD 10) never came near its limit: USD 2.93 + 1.24 before
the last run the driver started, and 3.48 + 1.24 before the pilot run of
arm R, which `pilot.sh` started without the check (finding 8).

The command blocks of the report against the logs, line for line
(`blocks.py`; a line that differs is held against the log with each
`<withheld>` and `<kit seed file>` matching any text):

```text
007-C-S run: 12 report lines, 12 log lines, 0 differ
007-C-C run: 12 report lines, 12 log lines, 0 differ
007-C-R run: 13 report lines, 13 log lines, 0 differ
007-C-R score: 36 report lines, 36 log lines, 2 differ
   report:     <decision> (mod-populations), <class>: gold <withheld>; the candidate (given) has <withheld>
   log matches with withheld parts: True
   report:     <decision> (mod-populations): wrong in <marks>: cites <anchor>; gold cites <withheld>
   log matches with withheld parts: True
(here `<decision>`, `<class>`, `<marks>` and `<anchor>` replace what the
report printed at `ede23d3`; finding 1)
kits: 8 report lines, 8 log lines, 0 differ
sc.log: 18 report lines, 18 log lines, 0 differ
r1.log: 10 report lines, 10 log lines, 0 differ
aggregate.log: 25 report lines, 25 log lines, 0 differ
runs/pilot-T-S.run.txt: 58 report lines, 58 log lines, 0 differ
runs/pilot-T-R.run.txt: 33 report lines, 33 log lines, 0 differ
runs/pilot-T-R.score.txt: 51 report lines, 51 log lines, 0 differ
```

### 2. The tasks the runs read are the tasks the committed code builds

The runs were made on a working tree, not on a commit. I built every task
again with the code of `7d2ff0a` (`tasks.build`, and `pilot.write` then
`tasks.build` for the pilot, into `/root/rv-slice-ae/`) and held its ID (a
prefix of the SHA-256 of its manifest) against the run's:

```text
$ python -I taskids.py
005 C task-4f8c812ea057 == task-4f8c812ea057
005 T task-3691e773436b == task-3691e773436b
006 C task-8c15d8fceefe == task-8c15d8fceefe
006 T task-16b4b5bbd5d5 == task-16b4b5bbd5d5
007 C task-47de94f74e05 == task-47de94f74e05
007 T task-bc033bce59a9 == task-bc033bce59a9
015 C task-2f2ce1b181bf == task-2f2ce1b181bf
015 T task-c887770e798d == task-c887770e798d
pilot T task-28efd3ea363d == task-28efd3ea363d
pilot problems []
pilot kit.yaml sha256 equals the run's: True
```

So every task folder a reader saw, file for file, is the one the committed
code builds, and the pilot folder written again from the fetch cache has
the bytes of the one the runs used.

### 3. Seven dev runs scored again with the committed code

`specfirst run score` (the CLI, not the executor's `aggregate.py`), under
the heavy lock, on the worktree at `7d2ff0a`/`ede23d3` (the code is
`d7bea75`'s), each output held against the executor's `.score.txt` (its
first line, the command, cut). At least one run per arm, five at stage C,
the ask demo, two runs of arm R with the wrong decision and one without,
and two runs with pending cells among them:

```text
$ for each: flock /run/lock/specfirst-heavy.lock taskset -c 0-3 specfirst run score $SPECFIRST_RUNS/<run> --kit /root/scratch-slice/kits/kit-<nnn> > <label>.score.txt
$           diff <label>.score.txt <the executor's file without its first line>
start 2026-11-19T13:26:28Z
005-C-S rc=0
005-C-S: identical to the executor's score file
007-C-R rc=0
007-C-R: identical to the executor's score file
015-C-C rc=0
015-C-C: identical to the executor's score file
006-T-R rc=0
006-T-R: identical to the executor's score file
006-C-S rc=0
006-C-S: identical to the executor's score file
015-T-S rc=0
015-T-S: identical to the executor's score file
005-C-R rc=0
005-C-R: identical to the executor's score file
end 2026-11-19T14:38:23Z
RESCORE-DONE
```

The lines of cells of each output (all gold cells, both datasets) equal
their rows of the report's tables at `ede23d3` and of `aggregate.json`
(the counts by kit are withheld here, finding P2-2). So
the executor's score files, from which `aggregate.json` and the tables
come, are what the committed scorer gives; with section 2, the scores
are those of the committed code on the tasks it builds.

The tests of the part on the commit (`d7bea75`'s code; P2 to P4 carry the
marker `evidence`, so `make test` in section 6 does not run them):

```text
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 python -m pytest -q -p no:cacheprovider tests/unit/test_harness_pilot.py tests/score/test_score_pilot.py
.............                                                            [100%]
13 passed in 33.81s
(exit 0)
$ python -m ruff check src tests
All checks passed!
(exit 0)
```

### 4. The pilot

The SAP as the task holds it (`inputs/docs/sap.md` of the pilot folder,
poppler text, 51 pages), pages 15 to 19 and the templates of pages 32 and
33, read in full:

- Section 11.2 (page 15 to 16) cross-tabulates treatment-emergent adverse
  events by organ class and preferred term; 11.3 (page 16) summarizes
  serious adverse events by organ class and term; 11.4 (`16/p13`) plans "no
  formal summarization" of events leading to discontinuation or
  withdrawal.
- The list of data displays, 13.1.1 (`18/p9` to `19/p30`), names 29
  tables. Its adverse event tables are number 18 (`19/p8`, incidence of
  treatment-emergent adverse events by treatment group, template 13) and
  number 19 (`19/p10`, serious ones, template 14). No overall summary table
  is listed. The claim of the report holds for a display of its own; see
  finding 6 for what templates 13 and 14 hold.
- The reader's three anchors stand where the report says: `18/p9` is the
  heading of 13.1, `19/p8` the title of table 18, `16/p13` section 11.4.
  The record (one line, `tfl.output.include` = `not_included`, stated) and
  the three unmapped paragraphs (`10/p5`, `10/p11`, `18/p3`: pooling of
  sites, multiplicity, the sort of the medication table) are as the report
  gives them; `asks.jsonl` does not exist (no ask). The reader read TASK.md,
  the two skills, the SAP (whole, then lines 2770 to 2969 and 4640 to 4844
  after a Grep for "Template 1[34]"), the house standard, the catalog entry
  and the schema, and ran `bin/check`.
- The ARS example embeds 3,735 results in 31 analyses (ADR-016, decision
  5); the key has 9 rows and 27 cells; the run's canary sources are the
  example (1,913), the key (90), `kit.yaml` (29), two planted, and the
  store (879).
- Both pilot runs: `passed` true, `valid` true, no task problem, no tool
  changed, within budget, no hit, a `result` event without error.

Both pilot runs scored again with the committed code, under the heavy
lock, and held against the report's blocks:

```text
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 specfirst score pilot --run $SPECFIRST_RUNS/S-task-28efd3ea363d > pilot-S.txt     (rc=0)
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 specfirst score pilot --run $SPECFIRST_RUNS/R-task-28efd3ea363d > pilot-R.txt     (rc=0)
$ diff pilot-S.txt <the report of arm S in pilot-T-S.run.txt>      && echo ...
pilot S: identical to the report's block (45 lines)
$ diff pilot-R.txt <pilot-T-R.score.txt without its command and exit lines> && echo ...
pilot R: identical to the report's block (49 lines)
$ grep ... pilot-R.txt
  reference ADaM: produced: 0 of 1 outputs in gold
  reference ADaM: cells correct: 0 of 27 gold cells (an output that was not produced counts as wrong)
  cells of the key that differ or are missing: 27, every one missing: arm R built no output. With tfl.output.include = {"rule": "included"}, 10 have the key's text, 5 differ and are explained by one more table decision, and 0 are unexplained. 12 are in rows ...
```

The trace of every one of the 27 cells in the report's block: 6 cells of
the header and of "Any adverse event", 2 of "Serious adverse event" and 2
of "Fatal adverse event" explained by `tfl.output.include` alone (10); the
zero counts of serious (Placebo), fatal (High Dose) and discontinuation
(three arms) by it together with `tfl.percent.format` =
`one_decimal_always` (5); the 3 cells of "Related adverse event" in the
row not built for ADAE.RELGR1; the 9 cells of the three rows the catalog
lacks. 10 + 5 + 3 + 9 = 27, none unexplained, as the report's two tables
say. The columns: `tfl.columns.total` = `none`; the rows: no single
decision, as the 4 rows of the last two classes.

Arm S equals read-1a's table: the 45 lines of the report of arm S in
`pilot-T-S.run.txt` (from "pilot CDISCPILOT01, arm S" to the crosswalk)
are lines 397 to 441 of docs/reports/read-1a.md, "The pilot":

```text
$ sed -n 397,441p docs/reports/read-1a.md > read1a-pilot.txt
$ awk '/^pilot CDISCPILOT01, arm S/{p=1} p' logs/runs/pilot-T-S.run.txt | grep -v '^(exit' > pilotS-run.txt
$ wc -l read1a-pilot.txt pilotS-run.txt; diff read1a-pilot.txt pilotS-run.txt && echo IDENTICAL
   45 read1a-pilot.txt
   45 pilotS-run.txt
IDENTICAL
```

### 5. The code of `d7bea75`

Read in full: `harness/pilot.py`, the changes to `harness/task.py`,
`harness/outputs.py`, `harness/command.py`, `score/pilot.py`,
`score/command.py`, and the two test files.

- The task of a generated kit: `build` takes the same two documents in
  the same order when the tier is not `C` and refuses a generated kit
  that lacks one; `render` is not changed; `render_real` is used only for
  tier `C` (a generated kit's `kit.yaml` has tier `A`, `gen/kits.py`). The
  task IDs above and the kept dry run of read-2a (section 6) show it.
- The pilot task leaks nothing I could find: the task holds TASK.md,
  `bin/`, the SAP text, the house standard, the reference ADSL and ADAE
  (the input of stage T), the catalog, schema, registry and the two
  skills; the key and the example stay outside `inputs/` and are canary
  sources; `tasks.problems` is empty; the pilot folder, the fetch cache
  and the seed folder lie in the WSL file system, which every run denies.
  The key is one JSON line of 7,311 characters, cut into 90 canary pieces,
  so any Read or Grep of it shows.
- Planted defects (rule R5): the key copied into the task (caught by
  `tasks.problems`); a citation of the protocol in a task without one and
  an anchor of an empty page (caught by `decision_problems`); the kit text
  changed where `render_real` swaps it (stops the build); stage C on a real
  study; a generated kit without its protocol; a stub reader that reads
  the key (a canary hit); a pilot folder inside a checkout (refused). Each
  new check has its plant, except two small ones (finding 5 and the
  `not docs` branch of `build`, which has no test).
- `score.pilot.run` for arm R: the reader's table decisions over arm S's
  vector (`given_vector`, other units ignored, tested); for a candidate
  without the output, the first other value of `tfl.output.include` that
  builds it, then every other value of every table decision on that
  traced vector. A cell right once the output is included is explained by
  that decision alone; any other is explained by it together with the one
  decision that fixes it, or classed by the crosswalk. P4 holds the counts
  10, 5, 3, 9, 0. The code does what the report and ADR-016, decision 6
  say.

### 6. What CI runs, and the kept dry run of read-2a

`/root/scratch-slice/logs/verify2.log`, run by the executor under the
heavy lock on the worktree at `7d2ff0a` (13:23:48Z to 13:41:38Z), ends
with `VERIFY-DONE`:

```text
$ specfirst gen kits --seed gen-2a --first 4 --count 1 --out /root/scratch-slice/gatekits
kit 4 of the set: sfrrl2uh, train, 127 files; 14 of 22 decisions separated on the twin
(exit 0)
$ specfirst run check src/specfirst/harness/kept/R-task-50024a8d7ca2 --kit /root/scratch-slice/gatekits/kit-004 --tasks /root/scratch-slice/check-tasks --seed gen-2a/kit-4
kept run R-task-50024a8d7ca2: PASS
(exit 0)
$ make test
...
1127 passed, 26 deselected in 1030.47s (0:17:10)
$ make lint
All checks passed!
$ make ascii
ASCII check: 553 files checked, 0 with non-ASCII bytes
```

The block that `ede23d3` puts into the report is this log without its
`start` and `end` lines, line for line. `run check` builds the task of the
gate's kit 4 again and holds its manifest, file by file, against the task
the kept run read (`runs.check`: "files differ" otherwise): the task of a
generated kit at stage C is unchanged by this part. The script pipes `make
test` into `tail -6`, so its exit status is not in the log; the summary
line shows no failure and no error. The 553 files of `make ascii` include
this review, untracked at the time.

### 7. What is committed

- `git diff 1a94134 ede23d3`: 13 files; every one is 7-bit ASCII at
  `ede23d3` (a byte count per file). No Windows user name, no `C:\Users`,
  no credential in the diff; its one 64-character hex string is the
  SHA-256 of the empty file, a context line of `task.py` (no seed hash). The report shows
  WSL paths under `/root/` (the logs, the kits, the folder of the seed
  files, the venv in a traceback): no person is named by them.
- No seed. Seed files are named only as `<dev seed>` and `<kit seed file>`.
- SAP text: three phrases of at most 57 characters (the reader's quotes,
  cut by `record_lines`) and the titles named in prose; the test file of
  the harness uses invented text. No SAP passage beyond a short phrase.
- The key's 27 cell texts and the IDs of the example's analyses are in
  the report, as in read-1a's report on `main`.
- A value of a decision of a dev kit: see finding 1.
- ADR-016 against PLAN.md: decision 1 keeps the dev seed and its SHA-256
  out of the repository (section 8: seeds of dev kits are secret; 6.7
  stores a seed's SHA-256 for sealed kits only); decision 4 keeps runs,
  tasks, transcripts and logs out (section 8: the decision vectors are
  secret); decision 5 keeps the pilot folder out (rule 4). They agree with
  PLAN.md. Decision 4's last sentence is where finding 1 lies.

### 8. The limits and the state of the track

Read against ADR-010, decision 4 (the M1 limit, to be stated in every M1
report), the gen-3a review (D9) and the read-2a review (H10 to H12):

- M1 isolation: stated as ADR-010 asks (the owner's Windows user under
  deny rules, not a container; the probe does not show that a file tool
  stays in the working directory; encoded copies unseen; Parquet not
  scanned; no `CLAUDE.md` on the path). The six folders of
  `SPECFIRST_DENY` are in every record's deny list (I read all nine), with
  the kits or the pilot folder, the folder of the seeds and the whole WSL
  file system. `<home>/AppData/Local/Temp/claude` is denied as a whole,
  wider than "the scratch folder of the executor's session"; that is on
  the safe side.
- One rewrite per statement: 38 of 61 within 0.9, two equal, as D9 has
  it; 8 of 66 template paragraphs, as counted above.
- H10: open, as said; the slot list is incomplete (finding 3). H11:
  settled on `main` (`1a94134`: read-2a under "Passed", lessons 64 and 65).
  H12: open, as said; no run here wrote `bin/` (`tools_changed` empty).
  Every tool use of the nine transcripts of arm R (8 to 18 Reads, 2 or 3
  Bash, at most one Glob and one Grep, two Writes each): every path inside
  the run's own task folder, every Write to `out/decisions.jsonl` or
  `out/unmapped.jsonl`, every Bash command `bin/...` or inside the task.
- Nothing material is missing. Overstated: the state file's "nothing of
  the runs" (finding 7). Understated: what the SAP plans (finding 6).

## Findings

### 1. Blocking: the report gives the gold of one decision of three dev kits

ADR-016, decision 4: "The report gives numbers, decision IDs and the
commands, never a value of a decision of a dev kit." PLAN.md section 8:
the decision vectors of dev kits are secrets; 6.7: of a dev kit only the
scorer sees gold, scores come back.

The report at `7d2ff0a` and `ede23d3` names one decision of
`mod-populations` (its ID is withheld here) in kits 5, 7 and 15 together
with the class of its gold record: in "What arm R got wrong" ("The one
error, three times: ..."), in the bullet "R against C", in the third bullet
of "Found during the part", and in the class word the score block of kit 7
keeps before "gold <withheld>". docs/state/read.md, "Next", says the same
of kits 5, 7 and 15. With the catalog and the house standard, both in the
repository, that class determines the gold value of the decision. So the
committed text gives the gold value of one decision in three dev kits. The
score block withholds the reader's value, but the prose names it,
alternative and slot.

Withholding the words alone would not be enough: the table by class and
the IDs of the three wrong decisions give the same by subtraction, and so
does "wrong in status" beside the reader's status. Any error list of a
dev kit beside counts by class does. This review names no class of a
decision of a dev kit; what the owner rules for the report applies to its
section 1 as well before it is committed.

The harm is small (one decision, the same in three kits) and nothing is
public yet: neither `7d2ff0a` nor `ede23d3` is on
the remote (`origin/track/read` is `d4cbe4c`). But a rule the part set for
itself, on a public repository, is broken, and only the owner can say
which way it goes. What would settle it, before the push:

- either the owner rules that a report on dev kits may name the decisions
  a reader got wrong together with their gold class (which, for some
  classes, is the value), and ADR-016, decision 4 says exactly that;
- or the report and docs/state/read.md stop pairing a decision of a dev
  kit with its class: no class word, and no phrase that implies one,
  beside a named decision, and the IDs of the wrong decisions not given
  beside counts by class or status marks that betray it (for example IDs
  by unit only, or the counts by class of arm R left out where they single
  one out).

### 2. Not blocking: the canary count of the pilot

"Checks", first bullet: "canaries per run ... 2,913 on the pilot", for
the two pilot runs. The run of arm S had 2,918 canaries (its record, and
the report's own command block: "2918 canaries from 17 files"); 2,913 is
the run of arm R. The breakdown (1,913 from the example, 90 from the key,
the rest from the store, `kit.yaml` and two planted) is right for arm R.
Settle: "2,918 (arm S) and 2,913 (arm R)".

### 3. Not blocking: the list slots of H10

"Limits", H10, at `ede23d3`, named the slots of one entry as the list
slots the readers wrote. The runs of arm R wrote list or map slots of
three entries. Every slot I counted has at most 4 items, none longer than
42 characters as text: nothing of the shape of a twin row, so the
conclusion stands. Settle: count the slots of all three entries (which
entries, in which kits, is withheld here: with arm R right on them, that
would give gold alternatives of dev kits).

### 4. Not blocking: `specfirst run pilot --folder DIR` deletes DIR

`pilot.write` starts with `shutil.rmtree(out, ignore_errors=True)`. The
only guard is `tasks.inside_checkout`. A slip such as `--folder /root` or
`--folder /root/scratch-slice` would delete that folder with everything in
it (the kits, the logs). Settle: refuse an existing folder that is not
empty and is not a pilot folder (no `kit.yaml` with generator `pilot-1`),
with a planted test.

### 5. Not blocking: `specfirst score pilot --run RUN` takes any run

`harness.pilot.score` does not check that the run is a run on the pilot.
Given a run of arm R on a dev kit it prints that reader's records (values
and quotes of a dev kit) and builds them on the pilot; given a run of arm
C it calls the house vector "a reader's table decisions". `score.command`
returns 0 also when it prints `pilot: <error>`. Settle: refuse a run whose
`run.json` names a kit other than `cdiscpilot01` or an arm other than S
and R, exit non-zero on an error, and plant both.

### 6. Not blocking: what the SAP does plan

The claim holds as written: the SAP's list of data displays (13.1.1, pages
18 and 19) has no overall summary of adverse events, its adverse event
tables are by organ class and term (11.2, 11.3; tables 18 and 19), and
11.4 plans no summary of events leading to discontinuation. But templates
13 and 14 (pages 32 and 33), which those tables follow, open with a row of
the subjects with at least one event (any, and serious), by treatment
group, with "xx (xx%)": the counts of the key's rows "Any adverse event"
and "Serious adverse event". The reader read those templates (a Grep for
"Template 1[34]", then lines 2770 to 2969) and still chose `not_included`,
which is defensible for the display. "The answer the key implies ... is
not what the SAP says" and lesson 69's "a right reading" are fair for the
table as a whole; the pilot section should say that the SAP plans two of
the summary's rows inside other tables, since that bears on the second
pilot task offered to the owner. Settle: one sentence in "The pilot".

### 7. Not blocking: docs/state/read.md ahead of the merge

At `7d2ff0a` the part is under "Passed" and names this review, which did
not exist yet; the same was H11 of the read-2a review. "Nothing of a dev
kit's runs and nothing of the pilot run is in the repository" is not true
as written: the report holds the output of the three runs of kit 7 and
the score of one (redacted), and the pilot run's record and whole report.
What is true, and what ADR-016, decision 4 means, is that no run folder,
task, transcript or log is committed. Its "Next" repeats finding 1. Settle:
move the part to "Passed" at the merge, after this review is signed, and
say "no run folder, task, transcript or log".

### 8. Not blocking: smaller statements

- "For the owner": "the owner's scope was nine runs". The report's own
  scope (its header, ADR-016) is four dev kits and at most USD 10; nine
  runs of arm R follow from ADR-016, decisions 2 and 5, the executor's.
  USD 5.95 of the owner's 10 were left. Settle: say whose the nine are.
- "Before each run of arm R the driver held the total so far ... it never
  stopped." The pilot run of arm R was started by `pilot.sh`, which holds
  no budget. The rule held in fact (3.48 + 1.24 = 4.72). Settle: say so.
- "Cost per run" does not say that every cache write was a one-hour write
  (USD 8 per million, twice the five-minute price): USD 2.75 of the 4.05,
  two thirds. With five-minute writes the same tokens would compute to
  USD 3.01. Worth a line for the budget of read-3.
- ADR-016, decision 5: "Nothing else is changed" in the SAP text.
  `anchored` also drops trailing blanks and every character that is not
  printable ASCII or a tab, the leading blanks of a paragraph's first
  line, and collapses runs of empty lines and the form feeds. A quote is
  checked against the anchored text, so nothing breaks; the sentence says
  more than the code. Settle: list what is dropped.
- "Tests": P2 to P4 carry the marker `evidence`, so `make test` and CI do
  not run them; the gate read-1a does (`pytest tests/score`, strict), and
  this part runs no gate. They ran on the working tree (`tests2.log`) and,
  in this review, on the commit (section 6).

## Questions for the owner

- Q1 (finding 1). May a report on dev kits name the decisions a reader
  got wrong together with their gold class, which for some classes is the
  value? If not, the report and the state of the track must withhold
  the pairing before the push; if so, ADR-016, decision 4 should say it.
- Q2 (lesson 47). ADR-016, decision 3 scores kits whose documents would
  fail the gate gen-3a (8 of 66 decision paragraphs are the phrasing
  template, nearer the standard form than a rewrite). That decides what
  "the first scores of the slice on dev kits" (ADR-005, decision 1) are
  read on, and it was decided by the executor and stated, not asked. Does
  the owner accept first scores on such kits, or want the loop of the
  natural form run for the dev seed first (gen track)?
- Q3 (finding 8). Were nine runs of arm R the owner's scope, or is the
  catalog condition (8 more runs, about USD 3.5) or the second pilot task
  (about USD 0.6) wanted within the USD 10 already granted?

## Verdict of pass 1

Every check I ran has ended: the tables from `aggregate.json`, the cost
from the records and transcripts, the command blocks against the logs,
the nine task IDs rebuilt, seven dev runs and both pilot runs scored again
under the heavy lock, the 13 tests of the part and ruff on the commit, the
tool uses of the nine transcripts of arm R, the SAP read where the report
relies on it, and `verify2.log`, which ends with `VERIFY-DONE` (the kept
dry run of read-2a PASS, `make test` 1127 passed, lint and ASCII clean).

Every number I checked holds: the four scores of the 48 rows and their
sums, the reading score by class and by unit, R against S and against C,
the pending cells and the decision they wait for, the asks, the wrong
decisions, the canary counts (but for the pilot count of finding 2), the
denials, the cost to the token and the dollar, and the pilot table with
the trace of all 27 cells. The code does what the report says, and each
new check has its planted defect but for the two small ones named.

One finding blocks: finding 1, the gold class, and so the value, of one
decision of three dev kits in the committed text, against ADR-016,
decision 4 and PLAN.md sections 6.7 and 8. It is settled by the owner's
answer to Q1 and the text that follows from it, before the push. Findings
2 to 8 do not block. Q2 and Q3 are for the owner and do not block.

Verdict: NOT SIGNED

## Pass 2

Reviewed: `d3974ec` on `track/read`, the fix of findings 1 to 8 of pass 1
(`git diff ede23d3 d3974ec`: ADR-016, lesson 69, the report, the state of
the track, `harness/pilot.py`, `harness/command.py`, `score/command.py`,
`tests/unit/test_harness_pilot.py`). The worktree is at `d3974ec`, clean
but for this file. Nothing of the track is on the remote:
`origin/track/read` is `d4cbe4c`, and `7d2ff0a`, `ede23d3` and `d3974ec`
are on no ref but the local `track/read`.

### What I checked

- Every changed line of `git diff ede23d3 d3974ec`, against the finding it
  answers and against the report's new section "The review". Each of its
  eight items says what changed, and the diff does that.
- Finding 1 in the text at `d3974ec`. No decision of a dev kit is named
  beside its class, its status or the reader's anchor: the decision IDs
  left in the report are, outside the pilot, `ae.related.values` (the
  pending cells and the ask of the ask demo, which `documents.TIER_PLAN`
  makes public; neither gives its value, which only the oracle and the
  documents of a kit hold) and none other. A search of the
  report and the state for the decision, its alternatives, its slot value
  and the protocol anchor of pass 1 finds nothing. The four redacted lines
  of the score block of kit 7, held against `007-C-R.score.txt` with each
  `<... withheld>` filled by any text (and the unseparated line by its
  count and four "(right)"): each has the log's shape.

  ```text
  report:     <decision withheld> (mod-populations), <class withheld>: gold <withheld>; the candidate (given) has <withheld>
     log has this shape with the withheld parts filled: True
  report:     <decision withheld> (mod-populations): wrong in status, span: cites <withheld>; gold cites <withheld>
     log has this shape with the withheld parts filled: True
  report:   unseparated in gold, compared by value only: 4 <decisions withheld> (right, right, right, right)
     log has this shape with the withheld parts filled: True
  report: wrong by value, and these data cannot show it (alone, on gold, it changes no cell and no axis of any dataset): <decision withheld> (mod-populations)
     log has this shape with the withheld parts filled: True
  ```

  Every other line of every command block still equals its log (the same
  comparison as pass 1: 0 lines differ elsewhere).
- Findings 2, 3, 6, 7 and 8: the new text is right against the records
  (2,918 and 2,913; three entries with list or map slots, at most four
  items, none over 42 characters; templates 13 and 14; "In progress";
  USD 2.75 of 4.05 and 3.01; the hand check 3.4778 + 2 x 0.6212 = 4.72;
  what `anchored` drops, now also in ADR-016 and the module text, as the
  code does).
- Findings 4 and 5 in the code. `pilot.not_replaceable` lets `write`
  replace only a missing or empty folder or one whose `kit.yaml` names a
  generator `pilot-<n>`; anything else, and a file, is refused before
  anything is deleted. `pilot.score` reads `run.json` and refuses any run
  that is not of arm S or R on the kit `cdiscpilot01` with split `pilot`
  before it reads the records; both commands print `pilot: <reason>` and
  exit non-zero. The two new tests plant what they guard against: a folder
  of other files, a file, a pilot folder whose generator was changed; a
  run of arm R on a dev kit and a run of arm C (each with a records file
  that must not be read), and a run folder without `run.json`.
- On the commit, under the heavy lock, and on the real records:

  ```text
  $ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 python -m pytest -q -p no:cacheprovider tests/unit/test_harness_pilot.py tests/score/test_score_pilot.py
  ...............                                                          [100%]
  15 passed in 32.69s
  (exit 0)
  $ python -m ruff check --no-cache src tests
  All checks passed!
  (exit 0)
  $ specfirst score pilot --run $SPECFIRST_RUNS/R-task-47de94f74e05   (a dev run)
  pilot: R-task-47de94f74e05 is not a run of arm S or R on the pilot (kit sfz57n2a, split dev, arm R)
  (exit 1)
  $ specfirst score pilot --run $SPECFIRST_RUNS/C-task-47de94f74e05   (arm C)
  pilot: C-task-47de94f74e05 is not a run of arm S or R on the pilot (kit sfz57n2a, split dev, arm C)
  (exit 1)
  $ specfirst run pilot --arm S --folder /root/rv-slice-ae/guard-test --tasks /root/rv-slice-ae/gt-tasks --runs /root/rv-slice-ae/gt-runs
  pilot: /root/rv-slice-ae/guard-test holds files and is not a pilot folder: it is not replaced; name a new folder
  (exit 2)
  keep.txt still there: keep
  pilot S-task-28efd3ea363d rc=0; identical to pass 1: yes
  pilot R-task-28efd3ea363d rc=0; identical to pass 1: yes
  ```

  The two pilot runs still pass the new guard, and their reports are byte
  for byte those of pass 1 and of the report. The executor's
  `/root/scratch-slice/logs/tests3.log` (14:54 to 14:56Z): `45 passed` for
  the two pilot files and `tests/unit/test_harness.py`, `make lint` and
  `make ascii` clean (553 files). The 13 files of `git diff 1a94134
  d3974ec` are ASCII, with no user name.
- This file: the text of pass 1 no longer names the decision of finding 1,
  the entries of finding 3 or the reader's anchor, and drops the pending
  count of kit 7 (finding P2-2); it is ASCII.

### Findings of pass 2

#### P2-1. Blocking: the pairing is withheld at `d3974ec`, not in the history

`d3974ec` withholds it, but `7d2ff0a` and `ede23d3` still hold it: 9
lines of the report and 2 of docs/state/read.md in each name the decision
with its class, the reader's alternative and slot, and the anchor.

```text
7d2ff0a: 9 in report, 2 in state
ede23d3: 9 in report, 2 in state
d3974ec: 0 in report, 0 in state
```

Both commits are ancestors of `d3974ec`. A push of `track/read`, or of
`main` after a merge of it (the project merges with merge commits), puts
them on the public remote, and anyone can read the withheld text with
`git show 7d2ff0a:docs/reports/slice-ae-summary.md`. Withholding in a
later commit does not withhold. Nothing is lost yet: no remote ref holds
them.

What settles it, before any push: the three unpushed commits after
`d7bea75` made again so that no commit holds the pairing (for example one
commit on `d7bea75` with the tree of `d3974ec`; only the local branch
changes, no force push is needed), then shown: `git diff d3974ec <new tip>`
empty, and the search above finding 0 in every commit of `git log
origin/track/read..track/read`. Pass 1's own findings would then stand
fixed. The commit messages hold no pairing (checked).

#### P2-2. Not blocking: what per-kit counts still tell

ADR-016, decision 4 now forbids naming a decision of a dev kit beside what
gives its value. Counts by kit remain, and with the catalog and the house
templates (both public) some of them narrow the gold alternatives of table
decisions of a dev kit: the gold cells of each kit's table (the four
scores) beside the number of its arms (the table of kits), and the pending
cells by kit beside the decision they wait for, with the sentence after
the pending table. It is the same kind of thing that pass 1's finding 3
named and that this pass withholds in its own text, only one inference
further. PLAN.md section 6.7 lets the scores of dev kits "come back" (and
asks only for aggregates of test kits), so I do not block. Settle, either
way: the owner accepts per-kit scores of dev kits in a public report at
N3, and ADR-016, decision 4 says that per-kit counts are given; or the
report gives sums over the four kits only.

### Verdict of pass 2

Every check of pass 2 has ended. Findings 2 to 8 of pass 1 are fixed as
"The review" says; findings 4 and 5 by code that does what it says, with
planted tests that pass. Finding 1 is fixed at `d3974ec` (Q1 is answered
by withholding, as pass 1 offered, not by the owner) but not in the
history the branch would push: P2-1 blocks until the unpushed commits are
made again without it, which a short pass 3 can check (`git diff d3974ec`
empty, the search clean in every commit). P2-2 does not block.

The verdict does not depend on an answer of the owner. Q2 (first scores
on kits with template paragraphs) and Q3 (more runs within USD 10) do not
change what is reviewed here; an answer that adds runs or other kits adds
text that needs its own review.

Verdict: NOT SIGNED

## Pass 3

Reviewed: `track/read` at `509c876`, one commit on `d7bea75` that replaces
`7d2ff0a`, `ede23d3`, `d3974ec` and `9fd775e` (the fix of P2-2) and has
the tree of `9fd775e`. The worktree is at `509c876`, clean but for this
file.

### What I checked

P2-1, the history:

```text
$ git rev-parse --short HEAD; git rev-parse --short track/read; git rev-parse --short origin/track/read
509c876
509c876
d4cbe4c
$ git ls-remote origin refs/heads/track/read      (read only)
d4cbe4c2cace...
$ git log --oneline 1a94134..track/read
509c876 slice-ae-summary: the report, ADR-016, lesson 69, the state of the track
d7bea75 slice-ae-summary: the pilot as a reading task, arm R scored on the pilot
$ git diff --stat 9fd775e 509c876
(nothing)
$ git rev-parse 509c876^{tree} 9fd775e^{tree}
2db8844663a12af8c2b2644f2da2a7daa578edff
2db8844663a12af8c2b2644f2da2a7daa578edff
$ git cat-file -p 509c876 | head -2
tree 2db8844663a12af8c2b2644f2da2a7daa578edff
parent d7bea7584c5395fbded46b9c3cff68027161c2c6
$ for c in 7d2ff0a ede23d3 d3974ec 9fd775e; do git merge-base --is-ancestor $c track/read && echo "$c IS ancestor" || echo "$c not ancestor"; done
7d2ff0a not ancestor
ede23d3 not ancestor
d3974ec not ancestor
9fd775e not ancestor
$ git for-each-ref --contains 7d2ff0a; git tag --contains 7d2ff0a
(nothing: no branch, remote branch, tag or stash holds it)
$ git worktree list       (no worktree is at an old commit)
$ git log -p 1a94134..track/read > hist.txt; grep -c -i -E '<pattern>' hist.txt
(the decision of finding 1):                    0
(its two alternatives, one pattern):            0
(the subcategory of the reader's value):        0
(the protocol anchor the reader cited):         0
(the entry of the map slot of pass 1, finding 3): 0
"house default holds":                          0
(the class word before ": gold" in pass 1's score block): 0
```

The entry of the list slot of finding 3 occurs in the history only in the
pilot sections of the report and in `score/pilot.py`, never beside a dev
kit. A case-blind search for the other subcategory finds only the pilot's
row "discontinuation of study treatment". The message of `509c876` holds
no pairing; it says it replaces three unpushed commits. Nothing was
pushed. The old commits stay only in the local reflog, which a push does
not send.

P2-2, the per-kit counts (`git diff d3974ec 9fd775e`, which is also
`git diff d3974ec 509c876`: ADR-016 and the report only, no code or test):

- The two tables of the four scores now have one row per arm and dataset,
  summed over the four kits; each row equals the old row "all four", which
  pass 1 checked against the records. The pending cells are summed (12 and
  12, `ae.related.values`), and the sentence on the ask demo's pending
  cells is gone. The kits table no longer has the number of arms.
- The only per-kit cell count left in the report is the score output of
  kit 7 in "Commands" (20 of 20 on each dataset), and the report gives
  no number of arms of any kit. A search of the report for cell
  counts by kit and for arms finds nothing else.
- ADR-016, decision 4 says the scores are summed and why, and that the
  scores of each kit stay in the records; "The review" records pass 2.
- At `509c876` the 13 files of `git diff 1a94134 509c876` are ASCII and
  hold no user name. No code or test changed after `d3974ec`, whose tests
  pass 2 ran (15 passed under the lock; the executor's `tests3.log`: 45
  passed, lint and ASCII clean).

This file, checked again: it names no decision of a dev kit beside its
class, status or value, and no entry of a dev kit beside a slot. It gives
no cell count of one kit beside a number of arms: in this pass I withheld
the number of arms of each kit (section 1), the pending cells by kit
(section 1) and the cell lines by kit of the seven re-scores (section 3).
The decision IDs left in it are `ae.related.values` (the summed pending
cells, the ask demo) and, in the pilot sections only, three table
decisions with the pilot's values. It is ASCII and holds no user name.

### Findings of pass 3

None. P2-1 is settled: no commit that `track/read` would push holds the
pairing, and the tree under review is unchanged. P2-2 is settled: the
report gives the scores of dev kits summed, as ADR-016, decision 4 now
says.

### Verdict of pass 3

Every check of pass 3 has ended. Finding 1 of pass 1 is settled by
withholding, in the files and in the history; findings 2 to 8 by the
fixes pass 2 checked; P2-1 and P2-2 as above. Every number checked in
passes 1 and 2 holds, and the summed tables are the sums pass 1 checked.
No blocking finding is left.

The signature depends on no answer of the owner. Q2 and Q3 are with the
owner: an answer that adds runs or other kits, or sets aside these kits,
adds or changes text that needs its own review. Rule 6 and node N3 still
apply: the push is expected after the merge; showing the report outside
waits for N3.

Verdict: SIGNED
