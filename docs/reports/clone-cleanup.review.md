# clone-cleanup: review (rule R7), pass 1

Reviewer: a fresh-context agent, 2026-11-23. Subject: `git diff 16ddfd8 fa1c7c3`
on `track/base` (commits `86d356b` and `fa1c7c3`). File and line numbers are
those of `fa1c7c3` unless named otherwise.

## Scope and method

Read in full: scripts/clean_clone_gate.sh (old at `16ddfd8` and new),
scripts/env.sh (sourced by the script at line 128), the CLAUDE.md line,
lesson 73, docs/state/base.md, docs/reports/clone-cleanup.md,
clone-cleanup.tests.sh, clone-cleanup.tests.log and clone-cleanup.gate.log;
the parts of src/specfirst/gates.py and src/specfirst/cli.py that create
build/gates/<wp>/ and parse the work package; the N2 fix `4b12c86`.

Commands (Windows git in the checkout, reading only):

```text
$ git log --oneline -5; git status --short; git diff --stat 16ddfd8 fa1c7c3
8 files changed, 586 insertions(+), 9 deletions(-); working tree clean
$ git worktree list
D:/trial_work/specfirst-gen   b22289b [track/gen]   (and the other tracks)
$ git merge-base --is-ancestor 86d356b b22289b || echo "not in gen"
not in gen
$ git show 4b12c86 -- scripts/clean_clone_gate.sh
in_checkout: eval "$(SPECFIRST_ROOT="$here" PYTHONPATH="$here/src" python3 -m specfirst.paths)"
$ git grep -n -E 'specfirst-clean|clean_clone_gate|clean-clone\.log|KEEP_CLONE|PASS \(clone' fa1c7c3 -- . ':!docs/reports'
(only CLAUDE.md, docs/lessons.md, docs/decisions/ADR-020.md, docs/state/*.md and the script itself)
$ git grep -n -E '(\$ |cp |ls |cat |du |find ).*/tmp/specfirst-clean' fa1c7c3 -- docs
(only gate output quoted in gate logs; no reviewer reads a clone after a run)
$ for each changed file: bytes, CR bytes, bytes above 0x7F of the blob at fa1c7c3
all 8 files: cr=0 high=0, each ends with LF
$ wsl -d Ubuntu-24.04 -u root -- bash -n scripts/clean_clone_gate.sh
exit 0
```

No gate, test suite or clean-clone run was started. To check the trap
logic, small synthetic scripts were run under WSL (bash 5.2.21) in a scratch
folder outside the checkout; they create one empty folder per case and no
lock is needed. `exp_trap.sh` copies the structure of the script: line 58
(`exec > >(tee "$log") 2>&1`), mktemp, `finish` as in lines 66-90 (an
`echo "copied"` when a `gates` folder exists in the work folder, then
`if rm -rf "$work"; then echo "deleted: ..."`), the EXIT trap and the three
traps of lines 92-94, then `sleep 4` as the long foreground step. The driver
turns job control on (`set -m`), so the job has its own process group, then
sends one signal to the PID (`kill -SIG "$pid"`) or to the group
(`kill -SIG -- -"$pid"`). Case G pipes the output into `head -c 1`, so the
caller's end of the output closes. Case H sends a second TERM to the PID while
`finish` copies (a `sleep 3` there). Results (exit code; work folders left;
the log's lines after "step starts"):

```text
case                                   exp_trap.sh (as the script)       with trap '' HUP INT TERM PIPE     with tee as in F1 (a)
                                                                         first in finish
A TERM to PID, gates folder exists     143; 0 left; copied, deleted       143; 0 left; copied, deleted       143; 0 left; copied, deleted
B TERM to group, gates folder exists   141; 1 LEFT; (none)                143; 0 left; (none)                143; 0 left; copied, deleted
C INT to group, gates folder exists    141; 1 LEFT; (none)                130; 0 left; (none)                130; 0 left; copied, deleted
D HUP to group, gates folder exists    141; 1 LEFT; (none)                129; 0 left; (none)                129; 0 left; copied, deleted
E INT to group, no gates folder        141; 0 left; (none)                130; 0 left; (none)                130; 0 left; deleted
F INT to PID, gates folder exists      130; 0 left; copied, deleted       130; 0 left; copied, deleted       130; 0 left; copied, deleted
G caller's output closed, no signal    141; 1 LEFT; (none)                141; 0 left; (none)                0; 0 left; step ended, copied, deleted
H second TERM to PID during the copy   143; 1 LEFT; copied                (not run)                          (not run)
race: last line read right after a normal exit, 30 runs: missing 0 times
```

## Findings

### F1 (blocking): the trap leaves the clone when tee is gone

`finish` writes `copied: ...` (line 73) before it deletes the folder (line 81).
Its output goes to the pipe of line 58. When tee has died, that echo raises
SIGPIPE. Bash then ends inside the trap, before the `rm -rf`. The exit code is
141, the folder of about 4.7 GB stays, and the log has none of the trap's
lines (cases B, C, D and G). The copy branch applies as soon as the gate step
has started, because `specfirst gate` creates build/gates/<wp>/ in the clone
first (src/specfirst/gates.py:37-39). That step is also the longest one, so
it is when a run is most likely to be stopped. Without the gates folder the
deletion happens, but the exit code is still 141 instead of 129/130/143
(case E).

Tee dies in two situations:
- A signal reaches the whole process group. This is what a terminal's Ctrl-C
  or hangup does, and what timeout(1) does without `--foreground`. The script
  uses no job control, so the script, tee and the current step share one
  group.
- The caller's end of the output closes (case G).

It was not checked here which of these happens when a Windows session that
drives WSL is stopped or times out. Either one gives case B to D or case G.

The fix is small and was tried on the copy of the structure:
- (a) Line 58 becomes
  `exec > >(trap '' HUP INT TERM; exec tee -p "$log") 2>&1`. Tee then ignores
  the three signals (dispositions set to ignore survive `exec`). With `-p`
  (coreutils `--output-error=warn-nopipe`) tee also keeps writing the log
  after its stdout closes. Tee still exits at end of file. All cases end with
  the folder deleted, the right exit code, and the trap's lines in the log
  (third column).
- (b) As a second line of defence, the top of `finish` gets
  `trap '' HUP INT TERM PIPE`. That alone deletes the folder in every case,
  but the log then lacks the trap's lines (second column). It also fixes F3.

Then add a test that sends INT or TERM to the process group during the gate
step, once `gate <wp> at commit` is in the log. For example, use `set -m` in
the test script, or `setsid`, and `kill -INT -- -"$pid"`. Add another test
that closes the output (`| head -c 1`).

### F2 (blocking): the report and lesson 73 say more than the runs show

The report says "HUP and INT were not sent. They take the same path as TERM
(T4)" (clone-cleanup.md:137). It also says that a signal during a long step
waits for that step (clone-cleanup.md:41-43). Lesson 73 says that the script
copies and deletes "after a PASS, a FAIL or a signal" (docs/lessons.md:79).
These hold only when the signal is sent to the script's PID alone, which is
what T4 did (clone-cleanup.tests.sh:41, `kill -TERM "$pid"`). T4 also sent it
during `git clone`, before the copy branch applies (tests.log:29-33).
Against the logs, the commands and outputs shown are true. The gaps:
- The copy branch on a FAIL was never exercised. T2 and T3 fail at the
  checkout, before the clone has build/gates/<wp>/. Only T5 (PASS)
  exercised the copy.
- The "Not covered" list misses these cases:
  - a signal sent to the process group;
  - a signal during the gate step, when the copy branch applies;
  - a FAIL of the gate step itself;
  - the caller's output closing;
  - a second signal while the trap runs (F3);
  - mktemp failing;
  - a TMPDIR other than /tmp (F5).

After F1, rerun the tests with the cases of F1. Then state the delivery
(PID or group) and the step in which each signal arrived.

### F3 (not blocking): a second signal cuts the trap short

Line 68 resets only the EXIT trap, so the traps of lines 92-94 stay set while
`finish` runs. A second HUP, INT or TERM runs `exit N` after the command in
progress, and the rest of `finish` is skipped. In case H the folder is left,
the exit code is 143 and the log ends at `copied`. A second signal sent to the
PID during the `rm -rf` lets the rm finish but drops the `clone deleted` line.
Sent to the group, it kills the rm part way. Fix: `trap '' HUP INT TERM` (and
PIPE, F1 (b)) as the first line of `finish`.

### F4 (not blocking): a stale clone/ copy can sit next to a new log

The previous copy is removed only when the clone has build/gates/<wp>/ (lines
70-71). Some runs end before the gate starts: a clone, checkout, install or
fetch failure, or a signal in those steps. They leave the previous run's
build/gates/<wp>/clone/ in place, which may hold a passing gate.log of another
commit, next to the new failing clean-clone.log. A caller that copies
clone/gate.log as evidence could take the old one. Its header names its commit
(gate.log:53, `gate base-0 at commit ...`), so this is a trap for the careless
reader, not a false result. Fix: delete build/gates/<wp>/clone/ at the start
of the run (beside line 56), or as the first step of `finish`. There is an old
equivalent that this change did not create: an early exit at lines 51-54
leaves the previous clean-clone.log.

### F5 (not blocking): deletions are confined; the guard could be tighter

`rm -rf` at line 81 runs only when `$work` matches
`"${TMPDIR:-/tmp}"/specfirst-clean-??????` (line 80). `$work` is mktemp's
output (line 61), is never assigned again, and is set before the trap exists
(line 91). With `--one-file-system`, this rm can delete only the run's own
folder. The value of TMPDIR is quoted in the pattern, so glob characters in
it are literal. A trailing slash or `/` itself gives the same string on both
sides.

Line 71 deletes `"$here/build/gates/$wp/clone"`. `$here` is absolute (line
37). `$wp` has no `/`, no leading `.`, and only `A-Za-z0-9._-` (lines 31-36).
Bash 5.2 has `globasciiranges` on by default, so the ranges are ASCII. That
rm stays inside the checkout's build/gates/. Every current gate name passes
the check (gates.py:678 onward). No input was found that reaches anything
else. Three weak spots remain:
- (a) The guard reads TMPDIR again at line 80. Between line 61 and line 80,
  line 128 sources scripts/env.sh of the commit under test, and through it a
  venv activate script, into this shell. If one of them ever sets TMPDIR, the
  guard skips the deletion. It does so silently, because the `case` has no
  `*)` branch. The same applies if they set `here`, `work`, `clone`, `wp` or
  `keep`, which would also move the copy. Today's env.sh uses only `_sf_*`
  names. Keep the base in a variable once, make these variables `readonly`,
  and add a `*)` branch that prints `clone NOT deleted`.
- (b) A relative TMPDIR: mktemp creates the folder relative to the caller's
  cwd, but `finish` first does `cd "$here"` (line 69). The rm then aims at a
  path under the checkout that does not exist, exits 0, and `clone deleted:`
  is printed while the folder stays. Refuse a relative TMPDIR, or make `$work`
  absolute right after line 61.
- (c) `clone deleted:` rests on rm's exit code. A check `[ ! -e "$work" ]`
  would make the line true by construction.

### F6 (not blocking): a name that starts with `-` gives a false PASS

The new check accepts a leading `-` (line 32). `scripts/clean_clone_gate.sh -h`
(or `--help`) clones, installs and fetches, about 5 GB and many minutes. It
then runs `specfirst gate -h --clean`, where argparse prints the help of the
subcommand and exits 0 (src/specfirst/cli.py:42-43). The script then prints
`clean clone gate -h: PASS`. This is older than the change, but the new check
is the place to refuse a leading `-`, or a name that is not a known gate,
before anything is cloned.

### F7 (not blocking): the log's last lines

After a normal end, the trap's lines reach the log
(clone-cleanup.gate.log:275-276, tests.log:43-44). Bash does not wait for the
process substitution at exit. A caller that copies clean-clone.log right
after the script returns could therefore, in principle, miss the trap's last
line. In 30 tries with the same structure it never did. The test script
waits 2 s before it copies the log in T4 and T5 (tests.sh:42, 48), and the
report does not say why. The PASS and FAIL lines are safer than before,
because the copy and the deletion take seconds after them. When tee is gone,
the trap's lines are lost entirely (F1). Optionally keep `$!` after line 58,
and at the end of `finish` close stdout and stderr and `wait` for tee.

### F8 (not blocking): callers and other text

No code in scripts/, src/, tests/ or .github does any of these:
- parse the last log line or the old "which does not last" text;
- read the clone after the script;
- look inside build/gates/ beyond <wp>/gate.log, evidence.xml, pilot.xml and
  gen-1a's `core` folder (gates.py:37-39, 112, 222, 253; gen/gate.py:822).

All of these are under build/gates/<wp>/ and so are copied. build/ is ignored
by git (.gitignore:20), and the ASCII check lists files through `git ls-files
--exclude-standard` (asciicheck.py:27), so the new clone/ folder breaks no
check. Past reviews match lines by pattern, not by position (for example
issue-29.review.md:1295).

One text now gives wrong advice. docs/state/gen.md:492-493 says "A clean
clone is under `/tmp`, which WSL clears a minute after the last command: copy
what must last in the same command (lesson 39)". After this change, nothing
in the clone outlives the script except build/gates/<wp>/, which is copied to
clone/, unless SPECFIRST_KEEP_CLONE=1. That file belongs to the gen track:
name it in base's handover, or fix it on main at the merge.

The CLAUDE.md line and base.md are accurate apart from F1.

### F9 (not blocking): details of the report

- (a) The report says the PASS and FAIL lines "are no longer the last line of
  the log" (clone-cleanup.md:49-52). That is true for FAIL. For PASS, the old
  script already printed three lines after it (the last lines of
  scripts/clean_clone_gate.sh at `16ddfd8`).
- (b) The disk figures come with no command or output (rule R8):
  clone-cleanup.md:15-16, 21-25, 140-141 and lesson 73. Two of them do not
  agree: the disk file is 486 GB at clone-cleanup.md:16 and lessons.md:79,
  but 491 GB at clone-cleanup.md:24. Show the commands, or say these are
  readings taken at the time and when each was taken.
- (c) T2's shortened output leaves out tests.log:14, where git reads
  `no-such-commit` as a path argument. The step still fails with 128, so the
  test holds, but the line explains the exit code.

### F10 (not blocking): the edges of the signal handling

- A signal between mktemp (line 61) and the traps (lines 91-94) leaves the
  folder. Setting the traps before mktemp, with `finish` accepting an empty
  `$work`, closes this window.
- A TERM sent to the PID alone waits for the step in progress. During
  `specfirst gate` that can be the whole gate, about 20 minutes for gen-1a
  (docs/state/gen.md:486-487). The report says so. A supervisor that sends
  KILL after a grace period would therefore never reach the trap. Running
  each step in the background and `wait`ing for it would let the trap act at
  once and pass the signal on to the step.

These are optional.

### F11 (not blocking): what holds

- **Exit codes.** PASS gives 0 (T5). A FAIL gives the step's code (T2 and
  T3: 128). TERM to the PID gives 143 (T4). Usage errors give 2 (T1; lines
  26-36 and 51-54 exit before the log and the trap exist, and there is
  nothing to delete). A mktemp failure gives 2: line 61 runs before the trap,
  and its message goes to the log. `exit "$code"` (line 89) keeps the code
  whatever happens inside `finish`. flock passes the code on.
- **`set -u`.** Every variable `finish` uses is set before line 91, and the
  optional ones use `:-` defaults.
- **N2.** T5 sets SPECFIRST_ROOT to the gen worktree. That worktree's HEAD,
  `b22289b`, does not contain `86d356b`, yet the log names `86d356b`
  (tests.log:38-39, gate.log:53). T5 discriminates, and base.md's entry is
  right.
- **SPECFIRST_KEEP_CLONE.** It is read (line 60) before it is unset (line
  103), and T3 shows it works.
- **Repository rules.** All eight changed files are ASCII only and LF only.
  They hold no Windows user path, credential or e-mail address. The paths in
  them are WSL paths. The script keeps mode 100755, and the test script
  (100644) is run with bash.
- **The logs.** The report's outputs match tests.log and gate.log line for
  line where they quote them. gate.log shows the gate of `86d356b` (clean)
  passing 7 of 7 checks, and ends with the trap's lines.

## Summary

The change does what it should when the script fails, passes, or receives a
signal sent to its PID. It does not hold when a signal reaches the whole
process group or the caller's output closes during the gate step. Then the
clone stays and the log says nothing, which is the failure the change exists
to remove, and the report claims those cases are covered. F1 needs one or two
lines in the script plus two test cases. F2 is the matching correction of the
report and lesson 73 after a rerun. The rest are recommendations.

Verdict: NOT SIGNED (pass 1); blocking: F1, F2

# Pass 2

Reviewer: the same agent, 2026-11-23. Subject: `git diff fa1c7c3 00f740c`
(commits `679a291`, `67674a9`, `00f740c`). File and line numbers are those
of `00f740c` unless named otherwise.

## Scope and method

Read in full at 00f740c:
- scripts/clean_clone_gate.sh;
- clone-cleanup.tests.sh, clone-cleanup.tests.log, clone-cleanup.gate.log and
  clone-cleanup.group-int.log;
- the report;
- the changes to lesson 73 and docs/state/base.md.

Commands, reading only:

```text
$ git diff --stat fa1c7c3 00f740c
8 files changed, 488 insertions(+), 173 deletions(-)
$ git diff --stat 679a291 67674a9
docs/reports/clone-cleanup.tests.sh only (T7)
$ git diff --stat 67674a9 00f740c
docs only: lessons.md, the report, the three logs, base.md
  (so the script that was tested, at 67674a9, is the script of 00f740c)
$ for each of the 9 files changed since 16ddfd8: bytes, CR bytes, bytes above 0x7F of the blob at 00f740c
all: cr=0 high=0, each ends with LF; no Windows user path, credential or e-mail address in the diff
$ git ls-files -s scripts/clean_clone_gate.sh docs/reports/clone-cleanup.tests.sh
100755 ... scripts/clean_clone_gate.sh; 100644 ... docs/reports/clone-cleanup.tests.sh
```

No gate, test suite or clean-clone run was started. To test the real trap
code without a clone, I built a harness in a scratch folder outside the
checkout. It is lines 1-148 of scripts/clean_clone_gate.sh at 00f740c,
unchanged: the checks, `base`, the tee, `finish`, the traps, mktemp, the
unsets and `step`. A synthetic body follows, which does this in order:
1. prints the `clone:` line and makes the clone folder;
2. optionally makes 1500 empty files in the work folder;
3. runs `step sleep PRE`;
4. writes build/gates/<wp>/gate.log in the clone;
5. optionally starts a background `sleep 8`;
6. runs `step sleep STEP`;
7. optionally sources a file;
8. prints the PASS line.

It is called as `gate.sh c<case> repo ref`, so `in_checkout` is not called,
and every case has a TMPDIR folder of its own. Group cases start the job
with `set -m`. Results (exit code; folders left; the log after the step
lines):

```text
A  TERM to the PID during the step                    143; 0 left; copied, clone deleted
B  TERM to the group during the step                  143; 0 left; Terminated, copied, clone deleted
C  INT to the group during the step                   130; 0 left; copied, clone deleted
D  HUP to the group during the step                   129; 0 left; Hangup, copied, clone deleted
E  INT to the group before the gates folder exists    130; 0 left; clone deleted
G  caller's output closed after one byte              0;   0 left; PASS line, copied, clone deleted
H  second TERM to the PID while the trap deletes      143; 0 left; copied, clone deleted
   (at that moment: script alive, no "clone deleted" line yet)
H2 second INT to the group while the trap deletes     130; 0 left; copied, clone deleted
   (at that moment: script alive, no "clone deleted" line yet)
I  a background child of a step holds the output 8 s  0 after 8 s (step 1 s); 0 left; PASS, copied, clone deleted
J  a sourced file assigns work= and here=             0; 0 left; "work: readonly variable",
                                                        "here: readonly variable", values unchanged
K  20 normal runs, last log line read at once         "clone deleted" was the last line 20 times
```

## The findings of pass 1

- **F1: resolved.**
  - Line 74 runs tee as `exec > >(trap '' HUP INT TERM; exec tee -p "$log")
    2>&1`.
  - Line 88 makes `finish` ignore HUP, INT, TERM and PIPE first.
  - T7-INT and T7-HUP send the signal to the process group during
    `specfirst gate base-0 --clean`. They end 130 and 129, with copied and
    clone deleted, and 0 clones after (tests.log:52-72). The log of T7-INT
    ends with the gate's KeyboardInterrupt and then the trap's lines
    (group-int.log:93-111).
  - T8 closes the caller's output after one byte and still ends 0 with the
    whole log (tests.log:74-86; gate.log:272-276).
  - Harness cases B to E and G show the same for TERM to the group as well.
  - The ps line of T7 shows that the job led its own group (tests.log:53, 64).
- **F2: resolved.**
  - The report now says which delivery and which step each signal had
    (report:53-60, 151-168).
  - It explains why the first T7 tested nothing (report:204-208).
  - It lists what is not covered: KILL, the end of the instance, a PID-only
    signal waiting for the step, a second signal, and a gate that itself
    fails (report:210-234).
  - Lesson 73 now names the ways tested and the ones not tested.
  - The copy branch on a run that did not pass is shown by T7.
- **F3: resolved.** Line 88 makes `finish` ignore the signals. The report says
  this was not sent in a test (report:222-223). Harness cases H and H2 now
  send it, while the deletion runs, and the folder is deleted.
- **F4: resolved.** Line 70 removes build/gates/<wp>/clone/ at the start. T2
  plants a stale clone/gate.log and prints `stale clone/ removed`
  (tests.log:23).
- **F5: resolved.**
  - `base` is read once and made absolute with `pwd -P` (lines 61-67).
  - The deletion pattern uses `"$base"` (line 102).
  - A `*)` branch prints `clone NOT deleted (not a folder of this script)`
    (lines 110-112).
  - The result is checked with `[ -e "$work" ]` (lines 103-108).
  - `wp`, `here`, `base`, `teepid`, `keep`, `work` and `clone` are readonly
    (lines 42, 67, 76, 79, 127).
  - T4 shows a relative TMPDIR, resolved from the caller's folder and
    deleted (tests.log:34-38).
  - Harness case J shows that a sourced file cannot move `work` or `here`:
    bash reports the readonly variable and goes on with the old value.
  - No path reaches anything but the run's folder or
    build/gates/<wp>/clone.
- **F6: resolved.** Line 36 refuses a leading `-`, and T1 shows `-h` with exit
  2 (tests.log:11-12).
- **F7: resolved.**
  - `finish` closes its output and waits for tee (lines 75-76 and 115-117).
  - T6 copies the log right after `wait` with no sleep, and the trap's line
    is there (tests.sh:59-61; tests.log:47-48).
  - In harness case K, `clone deleted` was the last line 20 times in 20.
  - See N1 for the cost of this wait.
- **F8: resolved.** docs/state/base.md now names the out-of-date note in
  docs/state/gen.md for the gen track, and the report lists it
  (report:230-234). See N2 (c) for the wording.
- **F9: resolved.**
  - (a) The report now compares the old and new endings correctly
    (report:78-81).
  - (b) The disk figures are a table of readings, with the tools named
    (report:25-33), and 486 and 491 GB are now two readings at different
    times. One figure remains outside the table, see N2 (b).
  - (c) T2's git error line is shown (report:133).
- **F10: resolved.**
  - The traps are set before mktemp (lines 120-127).
  - `finish` handles an empty `work` and `clone` (lines 91 and 96).
  - The wait of a PID-only signal for the step in progress is stated in the
    script (lines 21-22) and in the report (report:218-221). That is
    sufficient; the background-step design was optional.
- **F11: still holds.** I re-checked it on the 9 files at 00f740c.

## New in pass 2

### N1 (not blocking): the wait for tee has no bound

`wait "$teepid"` (line 117) returns only when tee ends. Tee ends only when
every writer of its pipe has closed it. A process started by a step that
keeps the script's output open, such as a daemon or a stray background
child, therefore keeps the script from exiting until that process ends. The
caller's flock holds the heavy lock for that whole time. In harness case I a
background `sleep 8` made a 1 s run take 8 s. The deletion had already
happened, so no space is lost. No such process appeared in T7 or T8 (gate
base-0). Other gates (gen-1a with CORE, read-2a with its reader) were not
run under the new script. Optional: bound the wait, for example by polling
`kill -0 "$teepid"` for up to some seconds.

### N2 (not blocking): small points in the report

- (a) "Every case ended with `clones after: 0`" (report:183). T1 and T5 print
  no such line, and T4 prints `left in /root/scratch/reltmp: 0` instead.
  Every case that made a folder ended with none left.
- (b) "used space was 15 GB, against 18 GB before" (report:216-217). The 18
  GB is not in the table of readings, whose row before the restart says 28
  GB. Add the row or the time of that reading.
- (c) The gen.md advice to copy what must last in the same command "remains
  safe to do" (report:232-233). It is harmless, but it no longer works: when
  the script returns, the clone is gone. Only build/gates/<wp>/clone/ is
  left, or the whole folder with SPECFIRST_KEEP_CLONE=1. base.md says this
  correctly.
- (d) "The log ends with the last `$ ` line, then the trap's lines"
  (report:83). The step's own output can come between them, as in
  group-int.log:94-109.
- (e) tests.log was edited by hand at one line for rule R10, and the report
  says so (report:113-115). That is acceptable. Running the test script with
  `LC_ALL=C` next time would make mktemp print ASCII quotes, so no log needs
  editing.

## Summary of pass 2

Both blocking findings of pass 1 are resolved. So are F3 to F10. The tests
now send INT and HUP to the process group during the gate step and close the
caller's output, and the report states what each case sent and where. The
harness, run on the script's own trap code, agrees and also covers TERM to
the group and a second signal. N1 and N2 are recommendations.

Verdict: SIGNED (pass 2) of 00f740c
