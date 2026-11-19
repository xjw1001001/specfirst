# read-2a: the reader harness, and a dry run of each arm (report)

Part read-2a of ADR-005 (PLAN.md section 13.6, read-2 for the slice
"adverse event summary first"). Choices: docs/decisions/ADR-010.md. Code:
`src/specfirst/harness/`, `skills/`, `tests/unit/test_harness.py`. The
dry run of arm R and the isolation probe are kept in
`src/specfirst/harness/kept/`.

Gate (ADR-005, decision 1): "A dry run of each arm on one train kit ends
within budget with valid output files. The canary scan is clean." The owner
approved how this part reads that text for arm R (ADR-010, decision 9, for
the slice only): the gate never calls a model; the dry run of arm R is made
once with Opus 5.5, kept, and checked from its record; arms S and C, and
arm R with a stub reader, run live at every gate.

## Result

The gate `read-2a` passed on a clean clone of `e36e443` (fresh install and
fetch), and so did the gates gen-3a, gen-2a and read-1a, each on its own
clean clone of the same commit, one after the other:

```
$ scripts/clean_clone_gate.sh read-2a      (docs/reports/read-2a.gate.log, 601 s)
gate read-2a at commit e36e4430830691f7a295a35b62cb7d0ef40af50a (clean)
...
1080 passed, 23 deselected in 397.12s (0:06:37)
...
PASS  environment          0.4 s
PASS  pins                 0.8 s
PASS  lint                 0.0 s
PASS  unit tests         397.8 s
PASS  kit                 15.2 s
PASS  skills               0.2 s
PASS  task                 0.2 s
PASS  oracle               0.1 s
PASS  adapter              0.0 s
PASS  budget               0.0 s
PASS  output files         0.2 s
PASS  canary scan          4.6 s
PASS  arm S               27.2 s
PASS  arm C                2.0 s
PASS  arm R, stub reader      8.4 s
PASS  arm R, kept dry run      3.1 s
PASS  scratch removed      0.0 s
PASS  cache untouched      0.1 s
PASS  ASCII                0.0 s
GATE read-2a: PASS

clean clone gate read-2a: PASS (clone: /tmp/specfirst-clean-Sw9cWo/specfirst)

$ scripts/clean_clone_gate.sh gen-3a       (docs/reports/read-2a.gen-3a.gate.log, 548 s)
GATE gen-3a: PASS
$ scripts/clean_clone_gate.sh gen-2a       (docs/reports/read-2a.gen-2a.gate.log, 795 s)
GATE gen-2a: PASS
$ scripts/clean_clone_gate.sh read-1a      (docs/reports/read-2a.read-1a.gate.log, 1,610 s)
GATE read-1a: PASS
```

Each gate ran under `flock /run/lock/specfirst-heavy.lock taskset -c 0-3`
(lesson 32); the times include the fresh install and fetch. The commits
after `e36e443` change records only (this report, the review, the state).

How the gate text is met, check by check:

- "A dry run of each arm on one train kit": kit 4 of the seed of the gate
  gen-2a (`gen-2a/kit-4`, split train, the ask demo), written again by the
  check `kit`; its gold built again is the gold of the kit. Arms S and C
  run live (`arm S`, `arm C`); arm R is the kept run of the model, checked
  against the task built again now (`arm R, kept dry run`: "task
  task-50024a8d7ca2, built again now: task-50024a8d7ca2"), and the adapter
  runs live with the stub (`arm R, stub reader`).
- "ends within budget": each record against the budget of ADR-010,
  decision 8 ("budget: ... within"); the check `budget` plants a record
  over each limit.
- "with valid output files": the rules of ADR-010, decision 6 ("output
  files: valid"); the check `output files` plants a defect for each rule.
- "The canary scan is clean": every run "clean", the kept run "canary scan
  clean against the canaries of the kit written now: yes"; the check
  `canary scan` plants a read of each protected kind.

The planted defects of the gate (rule R5), each "found" in the log:

| Check | Planted |
| --- | --- |
| skills | a skill that names the kit; that names a subject; that quotes the store; notes that are not their rendering; a SKILL.md without a name |
| task | the oracle file of the kit in a task; a file outside the allow list; a TASK.md that names the kit |
| oracle | an oracle that answers every decision |
| adapter | settings without the deny rule of the store; no `--strict-mcp-config`; an `--add-dir`; another model; Bash allowed for every command |
| budget | 101 turns; 46 minutes; USD 10.01; an error at the end; stopped at the time limit; no result event; a model without a price |
| output files | a line that is not JSON; a record without a status; a decision the task does not ask for; a second record of a decision; `binds` filled; `identifiable` filled; an alternative the entry lacks; a slot left out; a citation of another document; a citation of an anchor that is not there; a question about no entry; questions that are not the ask log; an unmapped anchor that is not there; no unmapped.jsonl |
| canary scan | a transcript that read gold/decisions.jsonl, gold/docs/sap.md, gold/oracle.yaml, gold/summary.md, twin/data/sdtm/ae.json, twin/gold/ard/reporting-event.jsonl, kit.yaml, the store's paragraphs.jsonl, the run's private/oracle.json; that names the seed; a workspace file with a line of gold; a statement typed from the store (and, as the case the rule is for, a reader's own record judged without it) |
| arm R, stub reader | a kept run whose task differs by one file; a kept transcript that read gold/summary.md; a kept record over budget |

What the scan protects, in the gate log: "29347 canaries from 81 sources"
(kit gold and twin, kit.yaml, the store, the seed, the planted canaries of
the run's private files).

## What was built

| Piece | Where | What it does |
| --- | --- | --- |
| task builder | `harness.task` | the task folder of a kit (section 11.1): natural documents, house standard, visible SDTM (stage C) or the ADaM of gold (stage T), the catalog's entries, the registry, the record schema, the knowledge, TASK.md; deterministic, ID from its manifest; `problems` holds a folder against an allow list and against the files of the kit |
| knowledge | `harness.knowledge`, `skills/` | `core-reader` (by hand) and reading notes v0 of `mod-treatment`, `mod-populations`, `mod-ae-emergence`, `tfl-ae-summary`, rendered from the catalog; Agent Skill format; the leak check of section 11.4 |
| oracle | `harness.oracle`, `specfirst ask` | answers from the run's copy of `gold/oracle.yaml` only what it lists; every ask logged |
| outputs | `harness.outputs`, `bin/check` | the validity rules of ADR-010, decision 6 |
| canary scan | `harness.canary` | canaries planted in the run's private files and drawn from the kit's gold and twin, the store of model text and the seed; scan of every decoded string of a transcript and of every file the run wrote |
| record | `harness.record` | `run.json`: tokens by model and kind, turns, wall and API time, dollars from the tokens (and the CLI's own figure), the budget |
| adapter | `harness.adapter`, `harness.stub` | `claude -p` with the flags of ADR-010, decision 1, and the deny rules of decision 4; a stub that speaks the CLI's stream-json |
| runs | `harness.runs`, `specfirst run ...` | a run of arm S, R or C on one task and one record; the isolation probe; a run kept and checked again |
| gate | `harness.gate`, `specfirst gate read-2a` | 18 checks, each with planted defects |

## The isolation probe (ADR-010, decisions 4 and 8)

Before any dry run: the reader is asked to run `bin/check` (allowed), then
to read four protected files with the Read tool (the kit's oracle and gold
decisions on the WSL share, the store of model text on drive D, the run's
own copy of the oracle on drive C) and to print the last with Bash, plain
and behind `bin/check;`.

```
$ specfirst run probe /root/scratch-read2a/kits/kit-004
run probe-task-50024a8d7ca2: arm R, stage C, condition notes, kit sfrrl2uh (train), task task-50024a8d7ca2 (22 decisions)
  reader: claude-code, model claude-opus-5-5, used ['claude-opus-5-5'], CLI 2.1.327
  cost: 8 turns, 17.1 s wall, 10.2 s API, tokens in 10 out 910 cache write 4854 cache read 42836, USD 0.0656 (CLI: 0.06563920000000001)
  budget: {'turns': 10, 'seconds': 600, 'usd': 1.0}: within
  outputs: decisions.jsonl None lines, questions.jsonl 0 lines, unmapped.jsonl None lines
  asks: 0, answered 0
  output files: 2 problems
    decisions.jsonl: missing
    unmapped.jsonl: missing
  task folder: holds only what a reader may see
  canary scan: 29575 canaries from 80 files; clean
  permission denials: 6
  RUN probe-task-50024a8d7ca2: FAIL
every attempt was denied; the scan is clean
PROBE: PASS
```

(The line "RUN ... FAIL" is the check of a reading task: the probe writes no
output files. The probe's own verdict is the last line.) The tool results,
from the kept transcript: step 1 `bin/check` ran through WSL ("out/: 2
problems"); steps 2 to 5 "File is in a directory that is denied by your
permission settings."; steps 6 and 7 "Permission to use Bash with command
... has been denied.". The deny rules hold for all three kinds of path.

## The dry runs, on kit 4 of the gate seed (train, the ask demo), stage C

Arm R, made once with the model and kept (the second of two runs; the first
was made before the fix of lesson 61 and is not kept, see "Found"):

```
$ specfirst run arm /root/scratch-read2a/kits/kit-004 --arm R --seed gen-2a/kit-4 --keep
run R-task-50024a8d7ca2: arm R, stage C, condition notes, kit sfrrl2uh (train), task task-50024a8d7ca2 (22 decisions)
  reader: claude-code, model claude-opus-5-5, used ['claude-opus-5-5'], CLI 2.1.327
  cost: 20 turns, 71.3 s wall, 55.5 s API, tokens in 22 out 7084 cache write 43185 cache read 317644, USD 0.5508 (CLI: 0.5507768000000001)
  budget: {'turns': 100, 'seconds': 2700, 'usd': 10.0}: within
  outputs: decisions.jsonl 22 lines, questions.jsonl 2 lines, unmapped.jsonl 0 lines
  asks: 2, answered 2; pop.efficacy.rule (mod-populations); ae.related.values (mod-ae-emergence)
  output files: valid
  task folder: holds only what a reader may see
  canary scan: 29344 canaries from 81 files; clean
  permission denials: 1
  RUN R-task-50024a8d7ca2: PASS
kept in /mnt/d/trial_work/specfirst-read/src/specfirst/harness/runs/R-task-50024a8d7ca2
```

(The run was kept under the earlier name of the store, `harness/runs`, and
moved to `harness/kept` before the commit: a folder named like the module
`runs.py` could be taken for a namespace package by a fresh install.) The
one denial: a Bash command `cd "<task>"; ls -R | head -80; cat
knowledge/...`; the reader then read the files with the Read tool. Its two
questions, from `workspace/out/questions.jsonl`:

- `pop.efficacy.rule`: "Who is in the efficacy-evaluable set: safety-set
  subjects with a baseline and at least one post-baseline value of a named
  vital sign (which one), or safety-set subjects who attended a named visit
  (which one)?"
- `ae.related.values`: "Which collected causality values (scale NOT
  RELATED, UNLIKELY RELATED, POSSIBLY RELATED, PROBABLY RELATED, RELATED)
  count as related to study treatment?"

The kept run checked again, as the gate does:

```
$ specfirst run check src/specfirst/harness/kept/R-task-50024a8d7ca2 --kit /root/scratch-read2a/kits/kit-004 --tasks /tmp/sf-check-tasks --seed gen-2a/kit-4 --score
kept run R-task-50024a8d7ca2: PASS
```

Arms S and C and the stub reader run in the gate; their lines are in the
gate log (below).

## Cost per run

| Run | Model | Turns | Wall | API | Input | Output | Cache write | Cache read | USD (computed) | USD (CLI) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| isolation probe | claude-opus-5-5 | 8 | 17.1 s | 10.2 s | 10 | 910 | 4,854 | 42,836 | 0.0656 | 0.0656 |
| arm R, first dry run (not kept) | claude-opus-5-5 | 20 | 69.1 s | 54.2 s | 22 | 7,053 | 42,023 | 333,231 | 0.5440 | 0.5440 |
| arm R, kept dry run | claude-opus-5-5 | 20 | 71.3 s | 55.5 s | 22 | 7,084 | 43,185 | 317,644 | 0.5508 | 0.5508 |
| arm S (gate) | none | 0 | 0.0 s | - | 0 | 0 | 0 | 0 | 0 | - |
| arm C (gate) | none | 0 | 0.1 s | - | 0 | 0 | 0 | 0 | 0 | - |

Model use of the part: USD 1.16 computed from the tokens at API prices,
on the owner's subscription (no money charged per token). Before the login
two print-mode calls answered "Invalid API key" with 0 tokens, and one
probe started no program (lesson 62), at no cost. The prices of ADR-010,
decision 7 give the CLI's own figure to the fourth decimal.

## Scores (report only: they decide nothing in the gate)

From the gate log, stage C, kit 4 of the gate seed (22 decisions of the four
units; 15 gold cells of the adverse event summary on each dataset):

| Arm | Values right | Status right | Span right | Asks (precision, recall) | Decisions to change | Cells right, visible | Cells right, twin |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S, the standard alone | 13 of 22 | 13 of 22 | 13 of 20 | none given, recall 0.00 | 9 | 0 of 15 (not built: no value for `ae.related.values`) | 0 of 15 |
| C, the parser control | 22 of 22 | 22 of 22 | 20 of 20 | 1.00, 1.00 | 0 | 15 of 15 | 15 of 15 |
| R, the reader (kept dry run) | 21 of 22 | 20 of 22 | 18 of 20 | 1.00, 1.00 | 1 | 15 of 15 | 15 of 15 |

The reader's one wrong value: `disp.status.record` as
`disposition_event_by_subcategory` with "STUDY PARTICIPATION" (gold: the
house default `disposition_event`), read from the design paragraph of the
protocol on disposition subcategories. Gold marks it unseparated: no cell
of either dataset can show it ("wrong by value, and these data cannot show
it"). Its second wrong status: `tfl.output.include` recorded `stated` with
a citation of the SAP's table section, where gold has the house default.
One kit and one run: these numbers show that the loop works, nothing about
how hard reading is (ADR-005, "Consequences").

## Found during the part

- Lesson 61. The canary scan took the text a reader may read from the task
  folder after the run, out/ included: a line of gold copied into out/
  would have been allowed. Seen when the kept dry run was checked against a
  task built anew (four hits the live record lacked). The task text is now
  read before the reader runs; a unit test fails on the old code (shown:
  "1 failed" with the sources of `688c514`). The same check showed two
  false hits: the reader's own wrong but valid value of
  `disp.status.record`, in its own words, matches the prose of a paragraph
  of the store and the JSON of a value of the store. Now the reader's
  records as the catalog renders them, and the prose of the store, are no
  canaries; what the reader typed is (ADR-010, decision 5). The dry run was
  made again on the fixed code, and only that one is kept.
- Lesson 62. The CLI went from 2.0.29 to 2.1.327 between the check of its
  flags and the login: `--permission-mode default` is gone, and `cli.js`
  became a native `claude.exe`. The flags were checked again (ADR-010,
  decision 1): `manual` with `--permission-prompts none`, `--tools`,
  `--max-budget-usd`, `--disable-slash-commands`,
  `--no-session-persistence`. `--bare` cannot run on a subscription.
- The stub's two asks first reached no oracle: `specfirst ask --run ...`
  was dropped by the REMAINDER of the top-level parser (a rest that starts
  with an option). `run` and `ask` are now dispatched before that parser.
  The gate's stub check now asks that the decisions gold marks `asked` were
  asked and answered, so an empty ask log cannot pass.
- The tool wrappers first put the reader's arguments last; a reader could
  have pointed `bin/check` at another folder. The run and the task now come
  last, and win.

## Limits

- M1 isolation (PLAN.md section 11.2, to be stated in every M1 report):
  the reader runs as the owner's Windows user under deny rules and the
  CLI's working-directory boundary, not in a container where gold is not
  mounted (M2). A path that no rule names and that the CLI lets a tool
  reach is readable, and the canary scan sees a read only when its text
  reaches the transcript or the workspace. The probe showed the rules hold
  for the three kinds of path the harness uses; it names no file of a
  person's own folders and does not test them.
- Canaries are drawn from gold, not planted in it: kits are the
  generator's and are never patched. Parquet files are not scanned; the
  ADaM Parquet of gold has no text copy. Prose that a reader may write in
  its own words (statements, answers, the paragraphs of the store) is no
  canary when it is all but 16 characters of a line. Planting canary lines
  at generation is for the gen track.
- One train kit, one stage (C), one condition (`notes`), one run of the
  model: a dry run of the harness, not a measure of reading. The scores
  above are not first scores of the slice (that report is
  docs/reports/slice-ae-summary.md, which this part does not start).
- The gate checks the dry run of arm R from its record (decision 9,
  approved by the owner for the slice). The stub covers the plumbing of the
  adapter, not the CLI.
- The CLI is a Windows program and changes with its updates; the record
  names the version it ran (2.1.327). A gate on another machine checks the
  kept run, never the CLI.
- Without `--bare` the CLI looks for `CLAUDE.md` files on the path of the
  task folder and in the user's `.claude`; there are none on this machine
  (checked by name).
- Arm S builds nothing on the chain: `ae.related.values` has no house
  default in `catalog@1` (ADR-008, "For the owner", item 1).
- A reader is told to write no record for a question that does not apply;
  the scorer lists a record of a decision gold does not make as unknown
  (read-1a), so a `not_applicable` record would lower the reading score.

## Files

- docs/decisions/ADR-010.md, docs/lessons.md (61, 62), docs/state/read.md
- docs/reports/read-2a.gate.log (the gate read-2a on a clean clone), and
  read-2a.gen-3a.gate.log, read-2a.gen-2a.gate.log,
  read-2a.read-1a.gate.log
- src/specfirst/harness/kept/R-task-50024a8d7ca2/ (the kept dry run),
  src/specfirst/harness/kept/probe-task-50024a8d7ca2/ (the probe)
