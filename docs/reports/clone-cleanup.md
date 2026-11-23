# clone-cleanup: the clean-clone gate deletes its clone

Track base, 2026-11-22 and 2026-11-23. Commits on `track/base`, which starts
from `main` `16ddfd8`:

- `86d356b`: the change.
- `fa1c7c3`: the first report.
- `679a291`: the fixes of the review, pass 1.
- `67674a9`: test T7 corrected.
- The commit of this report.

The owner asked for this change after drive C filled up. The owner's answer,
in translation, was "change it, delete after each run"; the question had said
that the log is kept.

## What went wrong

`scripts/clean_clone_gate.sh` made a new folder `/tmp/specfirst-clean-XXXXXX`
for every run. The folder held the clone, a Python environment, the R
library, a fetch cache and CORE: about 4.7 GB. The script never deleted it.
Lesson 39 had counted on WSL clearing `/tmp` when the instance restarts. But
while sessions keep running commands, the instance does not stop: on
2026-11-22, `uptime` under WSL said `up 2 days, 21:45`.

These are readings taken at the time. Drive C was read with PowerShell
(`Get-PSDrive C`, and the length of the WSL disk file `ext4.vhdx`); WSL was
read with `df -h /` and `du -xsh`.

| When (2026-11-22) | Drive C free | WSL disk file | Used in WSL | Note |
| --- | --- | --- | --- | --- |
| first look | 18.6 GB | 486.2 GB | 485 GB | `/tmp` 474 GB: 103 folders `specfirst-clean-*`, 4.6 to 4.7 GB each |
| after deleting the unused folders | 14.6 GB | 490.8 GB | 28 GB | gates ran meanwhile and grew the file; then 3 minutes of readings every 30 s: 490.79 GB each time |
| after `fstrim` and the owner's compaction | 500.4 GB | 27.1 GB | 15 GB | WSL started again; `specfirst doctor`: ok |

The cleanup was done by hand, with the owner's approval. Two sessions
deleted every folder that no process used, keeping the one a running gate
used. Later that day the base session deleted the 6 folders left by gates
that had finished since, then ran `fstrim -v /`. The owner then compacted
the disk file with diskpart, with WSL stopped.

## The change

`scripts/clean_clone_gate.sh`:

- **A trap on EXIT** runs once, however the script ends. It does three things:
  1. It copies the clone's `build/gates/<wp>/` to `build/gates/<wp>/clone/`
     in the checkout. That folder holds `gate.log` and what a gate keeps
     there, such as `evidence.xml` or gen-1a's CORE reports. This also covers
     lesson 39's case.
  2. It deletes the new folder, and checks afterwards that it is gone.
  3. It prints `clone deleted: <folder>`, `clone NOT deleted: ...` or
     `clone kept (SPECFIRST_KEEP_CLONE=1): ...`.
- **HUP, INT and TERM** end the script through `exit 129/130/143`, so the
  trap runs for them too. While the trap runs, these signals and PIPE are
  ignored.
- **The tee of the log** ignores HUP, INT and TERM. It runs with `-p`, so it
  keeps writing the log when the caller's output closes. It therefore
  outlives a signal sent to the whole process group (a terminal's Ctrl-C or
  hangup), and the trap's lines reach the log. The trap waits for tee before
  the script exits.
- **The folder under which the new folder is made** is read once from
  `TMPDIR` (default `/tmp`) and made absolute. The deletion is confined to a
  path of the form `<that folder>/specfirst-clean-??????`, with
  `--one-file-system`. The traps are set before mktemp.
- **The variables** `wp`, `here`, `base`, `keep`, `work` and `clone` are
  readonly. Sourcing `scripts/env.sh` of the commit under test cannot move
  them.
- **The work package name** must be a plain folder name: letters, digits,
  `.`, `_` and `-`, not starting with `.` or `-`. The script now writes and
  deletes in `build/gates/<wp>/clone/`, and a leading `-` would be an option
  of `specfirst gate`.
- **A stale `build/gates/<wp>/clone/`** from an earlier run is removed at the
  start.
- **`SPECFIRST_KEEP_CLONE`** is unset before the clone's own commands run, like
  the other variables of the caller.

What callers see:
- The PASS and FAIL lines are as before, without the old text "which does not
  last". After a PASS the old script printed three lines; now it prints two,
  and then the trap's lines. After a FAIL the FAIL line used to be the last
  line; now the trap's lines follow it.
- A run stopped by a signal has no PASS or FAIL line. Its exit code is 129,
  130 or 143. The log ends with the last `$ ` line, then the trap's lines.

Also changed:
- `CLAUDE.md`: the line on the script.
- `docs/lessons.md`: lesson 73.
- `docs/state/base.md`.

## Review finding N2 of base-0

N2 said that the script took the checkout from a caller's `SPECFIRST_ROOT`.
It was fixed in `4b12c86` (real-1): `in_checkout` sets `SPECFIRST_ROOT` to
the script's own checkout. Test T8 below checks it. It sets `SPECFIRST_ROOT`
to the gen worktree, whose HEAD `b22289b` does not contain this change, and
the log names this checkout's repository and commit.

## Runs

`docs/reports/clone-cleanup.tests.sh` runs the cases. It was run under WSL
from the base checkout, with nothing else running:

```text
flock /run/lock/specfirst-heavy.lock taskset -c 0-3 bash /mnt/d/trial_work/specfirst/docs/reports/clone-cleanup.tests.sh
```

The output files:
- `docs/reports/clone-cleanup.tests.log`: the whole output.
- `docs/reports/clone-cleanup.gate.log`: the log of the passing gate (T8).
- `docs/reports/clone-cleanup.group-int.log`: the log of the run stopped by
  INT (T7-INT).

tests.log was edited in one place for rule R10. Line 42, mktemp's message,
had two typographic quotes, which are now ASCII quotes. Nothing else in the
log was changed.

The output below is shortened, and the exit codes of T1 are joined to their
lines:

```text
== commit: 67674a9 clone-cleanup: T7 of the tests sends the signal to a job with its own process group
== T0 syntax
bash -n: ok
shellcheck: not installed
== T1 names that are not plain folder names, and a folder that cannot be used
not a work package name: ../x            exit 2
not a work package name: .hidden         exit 2
not a work package name: -h              exit 2
cannot use the folder /no/such/folder    exit 2
== T2 FAIL at the checkout (a commit that does not exist), with a stale clone/ from an earlier run; clones before: 0
exit 128
$ git -C /tmp/specfirst-clean-J8oFFE/specfirst checkout --quiet --detach no-such-commit
fatal: git checkout: --detach does not take a path argument 'no-such-commit'
clean clone gate clone-test-fail: FAIL ('git -C ... checkout --quiet --detach no-such-commit' exited 128; clone: /tmp/specfirst-clean-J8oFFE/specfirst)
clone deleted: /tmp/specfirst-clean-J8oFFE
folder gone: /tmp/specfirst-clean-J8oFFE
stale clone/ removed
== T3 FAIL with SPECFIRST_KEEP_CLONE=1
exit 128
clone kept (SPECFIRST_KEEP_CLONE=1): /tmp/specfirst-clean-4l0E75
folder kept: /tmp/specfirst-clean-4l0E75
removed by this test
== T4 a relative TMPDIR, FAIL at the checkout
exit 128
clone:      /root/scratch/reltmp/specfirst-clean-Bhw6i3/specfirst
clone deleted: /root/scratch/reltmp/specfirst-clean-Bhw6i3
left in /root/scratch/reltmp: 0
== T5 mktemp fails (TMPDIR=/proc)
exit 2
mktemp: failed to create directory via template '/proc/specfirst-clean-XXXXXX': No such file or directory
== T6 TERM to the script alone, during git clone
exit 143
clone deleted: /tmp/specfirst-clean-6H78YG
folder gone: /tmp/specfirst-clean-6H78YG
== T7-INT INT to the whole process group, during the gate step of base-0
process group of the script: 789 (pid 789)
sending INT to the process group at: $ specfirst gate base-0 --clean
exit 130
KeyboardInterrupt
copied: the clone's build/gates/base-0/ to build/gates/base-0/clone/ here
clone deleted: /tmp/specfirst-clean-QfpwWR
folder gone: /tmp/specfirst-clean-QfpwWR
== T7-HUP HUP to the whole process group, during the gate step of base-0
exit 129
Hangup
copied: the clone's build/gates/base-0/ to build/gates/base-0/clone/ here
clone deleted: /tmp/specfirst-clean-hXvgt8
folder gone: /tmp/specfirst-clean-hXvgt8
== T8 PASS of gate base-0: SPECFIRST_ROOT set to another worktree (N2), and the caller's output closed after one byte
exit 0
repository: /mnt/d/trial_work/specfirst/.git
commit:     67674a94ca8c41be07bd3d23ab1d6ce20f83a4e0
clean clone gate base-0: PASS (clone: /tmp/specfirst-clean-dMZDEj/specfirst)
copied: the clone's build/gates/base-0/ to build/gates/base-0/clone/ here
clone deleted: /tmp/specfirst-clean-dMZDEj
folder gone: /tmp/specfirst-clean-dMZDEj
evidence.xml
gate.log
clones after: 0
== done
```

Every case ended with `clones after: 0`. In T8 the caller's end of the
output closed after one byte, and the log still holds every line up to
`clone deleted`.

The gate of T8 (`specfirst gate base-0 --clean` in the clone):

```text
PASS  environment          0.4 s
PASS  pins                 0.7 s
PASS  lint                 0.0 s
PASS  unit tests         464.8 s
PASS  evidence tests     211.7 s
PASS  R packages           1.0 s
PASS  ASCII                0.0 s
GATE base-0: PASS
```

Earlier runs, for the record:
- **The run on `86d356b`**, before the review, had T1 to T5 only. It passed.
  The review then showed that it had sent its signal to the script alone,
  during `git clone`.
- **The first run on `679a291`** sent INT to a job started with `&` from a
  script. Such a job ignores INT from the start, and bash cannot trap a
  signal that was ignored on entry. The gate went on, passed, and the trap
  deleted the clone (`exit 0`). That T7 tested nothing. It now starts the job
  with job control (`set -m`), as a terminal does.

## Not covered

- **shellcheck** is not installed in the environment, so only `bash -n` checked
  the syntax.
- **KILL, or the end of the WSL instance** (`wsl --shutdown`), ends the script
  without the trap. Its folder stays until `/tmp` is cleared at the next start
  of the instance. That clearing was seen once: after the compaction, used
  space was 15 GB, against 18 GB before.
- **A signal sent to the script alone** acts only after the step in progress.
  During the gate step that can be the whole gate, about 20 minutes for
  gen-1a. T6 shows it during `git clone`. A supervisor that sends KILL after a
  grace period would never reach the trap.
- **A second signal while the trap runs** is ignored by the trap's first
  line. This was not sent in a test.
- **A gate that itself fails** was not run. Its path is that of T2 (a FAIL
  line, then the trap). The copy branch on a run that did not pass is shown
  by T7-INT and T7-HUP.
- **Other tracks' worktrees** still hold the old script until they merge
  `main`. A clean-clone gate run from such a worktree leaves its folder as
  before.
- **One handover text is out of date.** `docs/state/gen.md` (lines 492-493)
  still says that a clean clone lasts a minute after the last command, and to
  copy what must last in the same command (lesson 39). That remains safe to
  do, and the file belongs to the gen track. docs/state/base.md names it for
  gen.
