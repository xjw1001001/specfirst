# read-2a The reader harness of the slice "adverse event summary first": independent review

Rule R7 of PLAN.md. Reviewer: an agent with a fresh context that did not
write the work. Date: 2026-11-18. Correctness only, no style.

Reviewed: branch `track/read`, commits `688c514` (the harness, the skills,
ADR-010, the gate), `d208f9a` (the owner's answers), `e36e443` (the probe
and the dry run of arm R, kept; the adapter on CLI 2.1.327; the fix of
lesson 61) and `da848ae` (the report and four gate logs), base `3fbe162`
(main). `git diff 3fbe162..da848ae`: 40 files, 8114 lines in, 8 out.
`PLAN.md`, `standard/`, `env/` and `third_party/` are not changed.

Result: NOT SIGNED. Two findings block (H1, H2) and one question is the
owner's (Q1). Seven do not block (H3 to H9). What the gate text asks is
met by the commit as it stands: the dry run of arm R is kept and checks
out against kit 4 written again, arms S and C and the stub run live, every
check of the gate fails on its plants, and the record of the kept run
agrees with its transcript to the last digit. What blocks is in the two
places the gate text leans on and the plants do not reach: a reader can
make any quote-free line of gold invisible to the canary scan by writing
it into a text slot of a valid record (H1, lesson 61 again), and a reader
can rewrite `bin/check` or `bin/ask` and then run anything through the
Bash rule that allows them, with nothing recorded (H2). Neither happened
in the kept run (its transcript shows it), and neither fix needs a new
run of the model.

## How the review was done

- Windows git for the diff and the history (`git -C
  /d/trial_work/specfirst-read ...`); nothing committed, branched or
  stashed. Nothing was read, listed or searched outside the worktree, my
  scratch folders (`C:\Users\11764\AppData\Local\Temp\review-read2a\`,
  `/tmp/review-read2a/`, `/root/scratch-review-read2a/`) and the author's
  kit `/root/scratch-read2a/kits/kit-004` (read and copied, never written).
  `reference/` was not touched.
- No model was called: no `claude`, no `specfirst run probe`, no arm R
  without the stub. Every run of arm R below is the stub reader.
- Under WSL with `scripts/env.sh` of the worktree. The unit tests ran
  under `flock /run/lock/specfirst-heavy.lock taskset -c 0-3`. The scoring
  of the kept run (`specfirst run check ... --score`) waited behind another
  session's clean-clone gate on the lock and I withdrew it before it ran:
  its scores are taken from the author's gate log. My other probes (r1 to
  r4) write tasks and runs under
  `/tmp/review-read2a/` and build no kit and score nothing, so they did not
  take the lock. I did not run the full gate: the clean-clone logs of the
  author are quoted where I rely on them.
- Kit: a copy of kit 4 of the gate seed, `cp -a
  /root/scratch-read2a/kits/kit-004 /root/scratch-review-read2a/kits/`;
  `kit.yaml` SHA-256 `e23d3a90...95bd18`, the kit the kept run read.
- My scripts `r1.py` to `r4.py`, `t1.sh`, `t2.sh` are in
  `C:\Users\11764\AppData\Local\Temp\review-read2a\` and are not kept;
  each is described where its output is quoted.
- No file of the repository was changed but this one.

## What I read

- `CLAUDE.md`; `PLAN.md` sections 2, 9.1 to 9.3, 10, 11.1 to 11.4, 13.6;
  `ADR-005` (all); `ADR-010` (all); `docs/state/read.md`;
  `docs/reports/read-2a.md`; `docs/reports/read-2a.gate.log` (all) and the
  summaries of the other three gate logs; `docs/lessons.md` rows 47, 54,
  58, 59, 61, 62; the layout of `read-1a.review.md` and `gen-3a.review.md`.
- In full: every module of `src/specfirst/harness/` (`__init__`,
  `adapter`, `canary`, `command`, `gate`, `knowledge`, `oracle`, `outputs`,
  `record`, `runs`, `stub`, `task`); the diffs of `cli.py`, `gates.py`,
  `CLAUDE.md`, `docs/lessons.md`, `docs/state/read.md`;
  `tests/unit/test_harness.py`; `skills/core-reader/SKILL.md`; the heads of
  the four rendered notes.
- Parts: `compile/standard_form.py` (`check_value`, `render`),
  `compile/slots.py` (the scalar types and their checks), the entries
  `pop.efficacy.rule` and `ae.related.values`, the record schema (statuses),
  `gen/gate3.py` and `gen/documents.py` (where the oracle file is held).
- The kept runs: every file of `kept/R-task-50024a8d7ca2/` and
  `kept/probe-task-50024a8d7ca2/`; every tool use and tool result of both
  transcripts; their init and result events.
- The prices of decision 7 against the claude-api reference bundled with
  the CLI (its model table, cached 2026-11-03).

## What I ran, with the key output

A. The unit tests of the part.

```text
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 python -m pytest tests/unit/test_harness.py -q -p no:cacheprovider
.........................                                                [100%]
25 passed in 87.00s (0:01:26)
```

B. The kept run and the skills from the command line.

```text
$ specfirst run check src/specfirst/harness/kept/R-task-50024a8d7ca2 --kit /root/scratch-review-read2a/kits/kit-004 --tasks /tmp/review-read2a/tasks-check --seed gen-2a/kit-4
kept run R-task-50024a8d7ca2: PASS
$ specfirst run skills
skills: rendered, Agent Skill format, no leak of the store
```

C. The light checks of the gate, in one process, on my copy of kit 4
(`r4.py`: `gate._STATE` set to my scratch and my kit, then each check
function called with a list as its output).

```text
skills: PASS; plants found 5; not found []
task: PASS; plants found 3; not found []
oracle_check: PASS; plants found 1; not found []
adapter_check: PASS; plants found 5; not found []
budget: PASS; plants found 7; not found []
outputs_check: PASS; plants found 14; not found []
canary_check: PASS; plants found 13; not found []
```

D. The kept record against its own transcript (`r1.py`, part A:
`record.cost` of the last `result` event of `transcript.jsonl`, with the
recorded wall time).

```text
result events: 1 position of the last: [70] of 72
  tokens: record {...} | from transcript {...} | same
  tokens_by_model: ... | same
  turns: record 20 | from transcript 20 | same
  api_seconds: record 55.5 | from transcript 55.5 | same
  usd: record 0.550777 | from transcript 0.550777 | same
  usd_cli: record 0.5507768000000001 | from transcript 0.5507768000000001 | same
  unpriced_models: record [] | from transcript [] | same
  is_error False subtype success stop_reason end_turn terminal_reason completed
  init: model claude-opus-5-5 | tools ['Bash', 'Edit', 'Glob', 'Grep', 'Read', 'Write'] | mcp [] | permissionMode default | cwd <task> | apiKeySource none
  by hand, Opus 5.5 at 4/20/8 (1 h write)/0.2: 0.5507768
  1h writes 43185 5m writes 0 costUSD 0.5507768000000001
  probe: record usd 0.065639 turns 8 | from transcript usd 0.065639 turns 8 | budget {'seconds': 600, 'turns': 10, 'usd': 1.0} | over []
```

The init event also names a scratchpad of the reader outside the task
folder (`<home>\AppData\Local\Temp\claude\...\scratchpad`), `skills: []`,
`slash_commands: []`, `additional_directories: []`.

E. What the allowance for the reader's own records removes from the scan
of the kept run (`r1.py`, part B: `runs.kit_canaries` on the task built
again, without and with the records of `workspace/out/decisions.jsonl`,
then the scan of the kept transcript and workspace).

```text
  task built again: task-50024a8d7ca2 recorded: task-50024a8d7ca2
  canaries: without 29347 with 29344
  hits without the allowance: 1
     workspace:out/decisions.jsonl: holds 'gory", "subcategory": "STUDY PARTICIPATION"}}' (from store:paragraphs.jsonl:58)
  hits with the allowance: 0
  canaries the allowance removes: 3
     store:paragraphs.jsonl:58 | gory", "subcategory": "STUDY PARTICIPATION"}}
     store:calls/rewrite-1.request.json:329 | ject with the subcategory \"STUDY PARTICIPATION\".",
     store:paragraphs.jsonl:58 | sposition event record of the subject with the subcategory \"STUDY PARTICIPATION
```

"STUDY PARTICIPATION" stands in the task's `inputs/docs/protocol.md` (and
in the visible `ds.json`). The slot values of the kept records are
`SYSBP`, `WEIGHT`, `STUDY PARTICIPATION`, `["PROBABLY RELATED",
"RELATED"]`, `Placebo` and `["FATAL", "SERIOUS", "RELATED", "ANY"]`.

F. Leaks the run lets through, with the stub reader (`r2.py`). Three
quote-free lines of protected files, each a canary as it stands:

```text
picked from gold/summary.md: 'Study SFRRL2UH, archetype PG-FIX, split train, generator gen-3a.2.'; a canary as it stands: ['kit:gold/summary.md:3']
picked from gold/design.yaml: '# design.yaml of the study SFRRL2UH: generated by specfirst gen-3a.2'; a canary as it stands: ['kit:gold/design.yaml:1']
picked from gold/spec/adam/fragments/adsl/pop.efficacy.rule.yaml: "filter: VS.VSTESTCD = 'WEIGHT' AND VS.VSSTRESN IS NOT NULL"; a canary as it stands: ['kit:gold/spec/adam/fragments/adsl/demo.baseline.record.yaml:9']
```

The plan of each run is `gate.stub_plan` (the records of a reader that
reads gold right, both asks, `bin/check`) with one change. "control": the
stub reads a file that holds the three lines (a tool result in the
transcript) and writes them to `out/notes.txt`. "slot": the same read, and
the record of `ae.related.values` takes the value `{"rule":
"stated_list", "values": [the three lines]}` with the statement the
catalog renders from it. "wrapper": the stub writes `bin/check` as
`base64 -w0 '<kit>/gold/decisions.jsonl'; echo` and then runs `bin/check`,
as the plan always does.

```text
--- control
  output files: valid
  canary scan: 29347 canaries from 81 files; 9 hits
    transcript:3: holds '# design.yaml of the study SFRRL2UH: generated by specfirst gen-3a.2' (from kit:gold/design.yaml:1)
    ...
    workspace:out/notes.txt: holds 'filter: VS.VSTESTCD = 'WEIGHT' AND VS.VSSTRESN IS NOT NULL' (from kit:gold/spec/adam/fragments/adsl/demo.baseline.record.yaml:9)
  RUN R-review-control: FAIL
--- slot
  outputs: decisions.jsonl 22 lines, questions.jsonl 2 lines, unmapped.jsonl 0 lines
  output files: valid
  task folder: holds only what a reader may see
  canary scan: 29344 canaries from 81 files; clean
  RUN R-review-slot: PASS
  the picked lines stand in the transcript: [True, True, True]
--- wrapper
  output files: valid
  task folder: holds only what a reader may see
  canary scan: 29347 canaries from 81 files; clean
  RUN R-review-wrapper: PASS
  workspace files recorded: ['out/decisions.jsonl', 'out/questions.jsonl', 'out/unmapped.jsonl']
```

And on the wrapper run, afterwards:

```text
Write bin/check: "#!/usr/bin/env bash\nbase64 -w0 '/root/scratch-review-read2a/kits/kit-004/gold/decisions.jsonl'; echo\n"
tool result of 19140 chars; decodes to gold/decisions.jsonl byte for byte: True
$ head -3 /tmp/review-read2a/tasks/task-50024a8d7ca2/bin/check
#!/usr/bin/env bash
base64 -w0 '/root/scratch-review-read2a/kits/kit-004/gold/decisions.jsonl'; echo
passed True workspace ['out/decisions.jsonl', 'out/questions.jsonl', 'out/unmapped.jsonl'] task_problems []
```

G. The check `skills` against a mutant (`r3.py`). A copy of `standard/`
and `skills/` in `/tmp/review-read2a/fakeroot`, with one line of the
`mod-treatment` notes changed (`House default: dm_arm` to
`ex_first_dose`); the mutant is `knowledge.problems` with the comparison
with the rendering taken out.

```text
the copy's mod-treatment notes changed: True
knowledge.problems on the changed copy: ['mod-treatment: SKILL.md is not the rendering of the catalog (`specfirst run skills --write`)']
the mutant on the changed copy: []
gate check `skills` with the mutant:
    planted, a skill that names the kit: found (names 'SFRRL2UH')
    planted, a skill that names a subject: found (names 'SFRRL2UH')
    planted, a skill that quotes the store: found (...)
    planted, notes that are not their rendering: found (not the rendering)
    planted, a SKILL.md without a name: found (mod-treatment: the front matter names 'None')
  skills: no problem
gate check `skills` with the mutant passes: True
$ python -c "... knowledge.secrets_of(kit, 'gen-2a/kit-4') ..."
117 ['SFRRL2UH', 'SFRRL2UH-101-001', 'SFRRL2UH-101-002'] ... ['SFRRL2UH-106-014', 'gen-2a/kit-4', 'sfrrl2uh']
```

H. The wrappers' arguments, the deny roots (`r1.py`, parts C to E;
`command.ask_main` with the oracle replaced by a recorder; the fixed
`--run /RUN --task /TASK` appended as the wrapper appends them).

```text
  ask ['q', '--decision', 'd', '--run', '/other/run', '--task', '/other/task'] -> /RUN /TASK
  ask ['--run=/other/run', 'q', '--decision', 'd'] -> /RUN /TASK
  ask ['q', '--decision', 'd', '--run', '/other/run', '--'] -> refused (exit 2 )
  ask ['--decision', 'd', '--run', '/other/run', '--task', '/o', '--', 'q'] -> refused (exit 2 )
== D. deny roots when the task folder lies in the folder that holds the checkouts
  tasks in /tmp/review-read2a/tasks: holder /mnt/d/trial_work denied: True; denied: /mnt/d/trial_work, ...
  tasks in /mnt/d/trial_work/tasks-x: holder /mnt/d/trial_work denied: False; denied: /mnt/d/trial_work/specfirst-read, /mnt/d/trial_work/specfirst-read/src/specfirst/gen/rewrites, /root/scratch-review-read2a/kits, /tmp/review-read2a/runs
== E. a Windows reader when the Windows home is not found
  denied: ['/mnt/c/x/runs', '/mnt/d/trial_work', '/mnt/d/trial_work/specfirst-read/src/specfirst/gen/rewrites', '/root/scratch-review-read2a/kits']
  command problems: []
```

I. Also: `grep -rniE "sf[a-z0-9]{6}\b|gen-2a|kit-[0-9]|seed|USUBJID|[A-Z0-9]{8}-[0-9]" skills/`
finds nothing; a search of `kept/` for the user's name, mail addresses,
`Users\`, `oauth`, `sk-ant` finds only the words "token_counts" and
"taking the time into account".

## Findings

### H1. BLOCKS: a line of gold written into a text slot of a valid record is no canary anywhere in the run

`runs.kit_canaries(..., written)` adds the reader's records "as the
catalog renders them" to what a reader may write: their values as JSON
(`canary.reader_views`) to `allowed`, and the statements rendered from
them to `atoms`. A candidate found in `allowed`, or all but 16 of whose
characters stand in an atom, is dropped from the canaries of the run, for
the transcript and the workspace alike (`canary.build`). ADR-010 decision
5 and lesson 61 say what this allows is "never what the reader typed". But
a slot of type `text` or `list[text]` takes any printable ASCII without a
double quote (`slots._TEXT_BODY`), and a value that holds such text is
valid (`StandardForm.check_value` checks the rule and the slot names;
`render` checks each slot's type). The slice has such slots:
`ae.related.values` (`values`, a list of texts),
`pop.efficacy.rule`/`attended_visit` (`visit`), `disp.status.record`
(`subcategory`) among them. So the text of those slots is what the reader
typed, and whatever it types there is allowed.

Run F shows the consequence. The control run, which read three lines of
gold and wrote them into `out/notes.txt`, has 9 hits and fails. The slot
run read the same three lines (they stand in its transcript) and wrote
them as the values of `ae.related.values`: the output files are valid, the
scan is clean, the run passes. Writing a line into a slot whitelists it
for the read that brought it as well. A list slot takes as many lines as
the reader likes. This is the defect of lesson 61 in another place: a line
of gold copied into `out/` is allowed, now inside `decisions.jsonl` rather
than beside it, and no plant of the gate or the unit tests writes into a
slot (the plant "a statement typed from the store" types into the
`statement` field, which the allowance ignores). The limit in the report,
"the canary scan sees a read only when its text reaches the transcript or
the workspace", is not true while this stands.

The kept run is not touched by it: the allowance removes 3 canaries there,
all pieces around its value "STUDY PARTICIPATION", which stands in the
task's `protocol.md` (run E).

What settles it: an allowance that gives the reader's records only what
the reader could have had from the task. For example, a text slot value
counts as the reader's own only when it stands in the texts of the task as
built or in an answer of the oracle; otherwise the record adds nothing to
`allowed` or to `atoms`. Then the slot run of F must give hits in the
transcript and in `out/decisions.jsonl` (a unit test and a plant of the
gate), the kept run must stay clean in the gate (run E suggests it will),
and the sentence of the limits is true again. No new run of the model is
needed.

### H2. BLOCKS: the reader may rewrite `bin/check` and `bin/ask`, and Bash then runs what it wrote; the run records nothing

The adapter allows `Read`, `Glob`, `Grep`, `Write` and `Edit` with no path
and Bash for the prefixes `bin/ask` and `bin/check`. The deny rules name
protected folders; none names the task's own `bin/`. The wrappers are
files of the task folder, the reader's working directory, where the reader
writes `out/` with the same Write tool (the kept transcript: two Writes
into `out/`, both allowed). So a reader can write `bin/check` and then run
`bin/check` under its allow rule: any command, as the owner's Windows user
and, through `wsl.exe`, as root in the WSL distribution where the kits
lie. After the run nothing looks at `bin/`: `changed_files` builds on
`tasks.manifest`, which skips `bin/`, so the record's `workspace` does not
list the change, and `tasks.problems` allows `bin/`. ADR-010 decision 4
says "Bash runs the two wrappers and nothing else"; the item of the report
on the wrappers is about their arguments only (which do hold: run H).

Run F, "wrapper", does it with the stub: `gold/decisions.jsonl` comes back
in base64 in a tool result of 19,140 characters, the scan is clean (no
string scan can see an encoded copy), the output files are valid, the run
passes, and after the run `bin/check` still holds the reader's script. The
stub stands in for the CLI: that the CLI permits both steps is read from
its rules as the adapter sets them, not run (no model). The kept run did
not do it: its tool uses are Read and Glob inside the task, Write of
`out/decisions.jsonl` and `out/unmapped.jsonl`, Bash `cd <task> && bin/ask
...` twice and `cd <task> && bin/check` once, and one Bash denied.

What settles it: Edit and Write denied on the task's `bin/` in the run's
settings, and `command_problems` holding that rule; after the run every
file of `bin/` held against what `write_tools` wrote, a change failing the
run and named in its record; a plant of each (settings without the rule; a
stub that rewrites `bin/check` fails its run). ADR-010 decision 4 and the
limits of the report say what the rules then do and do not stop, and that
the scan cannot see an encoded copy. Whether the isolation probe is run
again with a step that tries to write `bin/check` is the owner's to decide
(model use of about USD 0.07); my signature does not wait for it.

### H3. Does not block: three plants of the gate do not go through the check they stand for

Rule R5 and lesson 54 ("for every clause a check prints, plant the scorer
that makes the clause false").

- "notes that are not their rendering" compares a rendered text with the
  same text after a replace and never calls `knowledge.problems`. With the
  comparison taken out of `knowledge.problems`, the check `skills` still
  passes with every plant "found" (run G). The check itself is right: on a
  copy with one changed line it names the note.
- "a skill that names a subject" plants `secrets[-1]`, which is the kit ID
  `sfrrl2uh` (the list is sorted; run G), and is found by the study ID. No
  subject is planted. Every USUBJID of the kit starts with the study ID,
  so a subject is caught today through that.
- "a TASK.md that names the kit" calls `knowledge.leaks` with every
  secret; the check holds TASK.md against the secrets that are lower case
  or the seed only.

ADR-010 decision 10 asks the leak check for the IDs of "a kit of the gate
set"; the gate holds kit 4 only. Run I found nothing that looks like a kit
ID, a subject ID or a seed in `skills/`.

What settles it: plants through the code path they stand for (a copy of
the skills with one changed note through `knowledge.problems`, as run G
does; a USUBJID for the subject; the TASK.md plant through the check's own
filter).

### H4. Does not block, but fix before read-3: two ways the deny list narrows without a word

- `runs.protected_roots`: when the task or run folder lies in the folder
  that holds the checkouts (`D:\trial_work`), that folder is not denied,
  only the current checkout (run H, part D). The reader's file tools then
  reach `reference/` (rule 2 of section 2.1, which has no exceptions, and
  which section 2.1 says to enforce with deny rules wherever such a path
  exists), every other checkout and their copies of the store of model
  text. ADR-010 decision 4 names the holder without this exception.
- `runs.windows_home()` returns None when `cmd.exe` fails; then
  `.claude`, `Desktop`, `Documents` and `Downloads` are not denied, and
  `command_problems` does not notice, because it holds the settings against
  the same list (run H, part E).

In the kept runs both hold: their `reader.deny` names `//D:/trial_work`
and the four folders of the home. What settles it: a `RunError` in both
cases, and `command_problems` held against the fixed list (the holder; the
four home folders for a Windows reader) rather than the list the run made.

### H5. Does not block: the check of a kept run holds the record against itself

`runs.check` takes the budget, the cost and the command problems as the
record states them: `over_budget(made)` compares the recorded cost with
the recorded budget, not with `record.BUDGETS["R"]` of decision 8; the
cost is not computed again from the `result` event of the kept transcript;
`command_problems` are those recorded at run time (the settings are not
kept); the init event (model, tools, MCP servers) is not read; stage and
condition are not held to decision 8 (stage C, notes). A record whose
budget and cost are raised together passes; the plant "a kept record over
budget" raises the cost only. `command_problems` also does not hold the
values of `--max-turns` and `--max-budget-usd` to the budget.

I held the kept records by hand (run D): every cost field equals
`record.cost` of the transcript's `result` event, the budget is that of
decision 8, the init event names `claude-opus-5-5`, the six tools, no MCP
server and `apiKeySource: none`. So nothing is wrong in the record today.
What settles it: `check` computes these from the kept transcript and the
recorded argv and holds the budget to decision 8; a plant with the budget
raised.

### H6. Does not block: the M1 limit says more than the probe shows

The report's limits: the reader runs "under deny rules and the CLI's
working-directory boundary"; ADR-010 decision 4: "A file tool that reaches
outside the working directory needs a permission that print mode cannot
give". The probe tried only paths that a deny rule names (its six
denials are all "denied by your permission settings" or a Bash rule), so it
shows the deny rules, not the boundary. `--allowedTools` grants the file
tools with no path; whether such a rule lifts the boundary is not shown
(I could not try: no model). Outside the task folder and named by no rule:
the reader's scratchpad that the CLI hands it (run D), and the other task
folders of the tasks folder, among them any stage-T task with the ADaM of
gold. Together with H2's encoded copy, the limit should say that only the
deny rules were shown to hold, that any path no rule names is readable,
and that the scan sees only literal text. A probe step on a harmless file
next to the task folder, with a planted canary, would settle the boundary;
it costs model use and is the owner's to want.

### H7. Does not block: records

- `docs/state/read.md` at `da848ae` still says of read-2a: "read-2a waits
  for that: do not try the CLI before the owner says the login is done",
  and its "What exists" does not name `specfirst.harness`. The report says
  the commits after `e36e443` change "this report, the review, the state";
  `da848ae` changes no state file. The handover must say what passed and
  what is open before the merge (section 2.4).
- ADR-010: decision 1 dates the login "(2026-11-18, the last section)",
  but the last section records only the answers that the login comes later
  and that read-2a waits; when and through whom the owner said the login
  was done, before the CLI was run again, is written only in the message of
  `e36e443`. The status line still reads "will log in the CLI later".

### H8. Does not block: the reader is never told the status `conflict`, which PLAN.md scores

PLAN.md 4.3 lists `conflict` among the statuses, the record schema has it,
and 9.1 scores whether "the reader tell stated from default from must-ask
from conflict" and lists as unmapped "only what the catalog truly lacks".
TASK.md names three statuses; `core-reader` section 4 says that when the
documents state two alternatives the reader records what the SAP states
and lists the case in `out/unmapped.jsonl`; `runs.own_records` keeps no
other status. No kit of the slice has a conflict (the word is in none of
`gen/documents.py`, `gen/decisions.py`, `score/reading.py`), so nothing is
scored on it today. For the part that first writes a kit with one.

### H9. Does not block: prices

The prices of decision 7 agree with the claude-api reference (Opus 5.5 at
4 and 20, cache read 0.20; Sonnet 5.5 at 2 and 10, cache read 0.10; Haiku
5.5 at 0.10 and 0.50; Haiku 4.5 at 1 and 5) and, for Opus 5.5, with the
CLI's own figure to the last digit (run D, at the one-hour write price,
which the transcript confirms: 43,185 one-hour writes, no five-minute
writes). Two details: Haiku 5.5's price holds for prompts up to 100K
tokens (0.50 and 2.50 beyond), which the table does not model; and once a
run writes any one-hour cache, every cache write is priced at the one-hour
rate, though `modelUsage` gives the two kinds apart per model. Neither
touches the kept runs.

## Checked and found correct

- The task folder: 92 files, an allow list, a pure function of kit, stage,
  condition, catalog and skills (built twice, the same manifest; the task
  of the kept run built again from my copy of the kit:
  `task-50024a8d7ca2`); no `gold/`, `twin/`, `kit.yaml`, `study.json`,
  store, catalog `knowledge/`, `phrasings/`, `templates/`; stage T holds
  exactly `adae.parquet` and `adsl.parquet` of gold; TASK.md is rendered
  without any input of the kit; the two conditions differ in the files of
  `knowledge/` only. `tasks.problems` finds a protected file by its hash
  wherever it is put (the twin's ADaM in stage T included).
- The oracle answers exactly the decisions its file lists and logs every
  ask to `asks.jsonl` and `out/questions.jsonl`; that the file lists the
  asked decisions is held by the gate gen-3a (`gen/documents.py`), and the
  stub check of this gate asks that both decisions gold marks `asked` were
  asked and answered. The scorer gets `asked=` from `asks.jsonl`
  (`runs.score`). The wrappers put `--run` and `--task` last and they win;
  a `--` makes `specfirst ask` refuse (run H).
- The output files: every rule of decision 6 has a plant that goes through
  `outputs.problems`; the documents a run cites are read before the reader
  runs, so a reader cannot edit the SAP to make a citation valid.
- The fix of lesson 61: the task texts are read before the reader runs and
  in `check` from the task built again; a line of gold in `out/notes.txt`
  is a hit (run F, control). The second half of the fix is H1.
- The scan finds a read of each protected kind (the gate's plants; my
  control run).
- The record: cost from the `result` event; wall time from the harness;
  within budget means at or below every limit, a `result` event, no error,
  not stopped; the limits are those of decision 8; arms S and C cost
  nothing.
- The kept dry run of arm R: what decision 9 says the gate holds (the task
  it read is the one built now, within budget, valid output files, scan
  clean against the kit written now, a score with its questions) is held
  by the check `arm R, kept dry run`, and run B and the gate log show it.
  Its record agrees with its transcript (run D). No private datum in the
  kept files (run I). The reader worked inside the task folder only.
- The probe: six denials for the six forbidden steps, `bin/check` ran,
  scan clean, within its budget of 10 turns and USD 1.
- The skills: the four notes equal their rendering (gate; `specfirst run
  skills`); Agent Skill front matter; no kit, study or subject ID, seed or
  store paragraph.
- The adapter's command line is that of ADR-010 decision 1, and each plant
  of the check `adapter` is found.
- The report: the cost table and "USD 1.16" (0.0656 + 0.5440 + 0.5508)
  agree with the records that are kept; the score table agrees with the
  gate log; the planted defects listed are those the log prints.

## What I could not review

- The behaviour of the CLI: no model was called. What H2 and H6 say about
  the CLI is read from the rules the adapter sets and from the kept
  transcripts.
- The first dry run of arm R, which is not kept.
- The four clean-clone gates: I took their logs (each at `e36e443`, each
  "PASS"). I did not run the full gate; I ran the unit tests of the
  harness, the light checks of the gate in one process, and the check of
  the kept run without its score. The scores of arms S, C and R are those
  of the gate log; the report's table agrees with it.
- That `test_what_the_reader_writes_into_out_is_scanned_not_allowed` fails
  on the sources of `688c514` (lesson 61): not run again.

## Questions for the owner

Q1. The gate text says "The canary scan is clean." PLAN.md section 11.2
says what the scan is: "every transcript and workspace is scanned for
canary strings planted in gold files". This part plants canaries only in
the run's private files; from the kit's gold and twin, and from the store
of model text, it draws every line as a canary, and it decides itself what
is no canary: the task, the oracle's answers, gold's records in the form a
reader writes them, the statements of gold and the prose of the store with
16 characters of slack, and the reader's own records (ADR-010 decision 5).
ADR-010 lists this among the decisions that "stand unless the owner
objects". That is how this part fills in a word of its own gate text,
which lesson 47 says is put to the owner before the gate counts. Drawing
every line finds more than a few planted lines would, except where the
allowances reach, and H1 is one place they reach too far.
Recommendation: accept it for the slice, once H1 is fixed; the planted
canary lines in gold and twin stay booked for the gen track, as decision 5
says. My signature waits for the answer.

## What settles the blocking findings

1. H1: the allowance for the reader's records takes nothing the reader
   could not have from the task; a unit test and a plant of the gate with a
   line of gold in a text slot; the limit sentence of the report true.
2. H2: Edit and Write denied on the task's `bin/`; `bin/` held after the
   run; a plant of each; ADR-010 decision 4 and the limits corrected.
3. Q1 answered by the owner.
4. The gate `read-2a` on a clean clone of the commit that does 1 and 2,
   with the kept run of arm R passing its check unchanged; H7 updated with
   it.

Verdict: NOT SIGNED
