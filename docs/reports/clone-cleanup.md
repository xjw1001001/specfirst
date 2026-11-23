# clone-cleanup: the clean-clone gate deletes its clone

Track base, 2026-11-22. Commit `86d356b` on `track/base`, which starts from
`main` `16ddfd8`. The owner asked for this change after drive C filled up.
The owner's answer, in translation: "change it, delete after each run". The
question had said that the log is kept.

## What went wrong

`scripts/clean_clone_gate.sh` made a new folder `/tmp/specfirst-clean-XXXXXX`
for every run. The folder held the clone, a Python environment, the R
library, a fetch cache and CORE: about 4.7 GB. The script never deleted it.
Lesson 39 had counted on WSL clearing `/tmp` when the instance restarts. But
while sessions keep running commands, the instance does not stop, and it ran
for days. On 2026-11-22, 103 such folders (about 470 GB) had grown the WSL
disk file on drive C to 486 GB, and drive C had 18.6 GB left (lesson 73).

The cleanup was done by hand the same day, with the owner's approval:

- Every folder that no process used was deleted. Two sessions did this; the
  only folder kept was the one a running gate used. Used space in WSL fell
  from 489 GB to 28 GB.
- `fstrim` was run, and then the owner compacted the disk file with WSL
  stopped. The disk file went from 491 GB to 27 GB, and drive C has 500 GB
  free.

## The change

`scripts/clean_clone_gate.sh`:

- **A trap on EXIT** runs once, however the script ends:
  1. It copies the clone's `build/gates/<wp>/` to `build/gates/<wp>/clone/`
     in the checkout. That folder holds `gate.log` and what a gate keeps there,
     such as `evidence.xml` or gen-1a's CORE reports. This also covers lesson
     39's case.
  2. It deletes the new folder. It deletes only a path of the form
     `${TMPDIR:-/tmp}/specfirst-clean-??????`, and with
     `--one-file-system`.
  3. It prints `clone deleted: <folder>`, or `clone kept ...` when
     `SPECFIRST_KEEP_CLONE=1`.
- **HUP, INT and TERM** end the script through `exit 129/130/143`, so the
  trap runs for them too. Bash runs a trap after the command in progress
  ends, so a signal during a long step waits for that step.
- **The work package name** must be a plain folder name (letters, digits, `.`,
  `_`, `-`, not starting with `.`), because the script now writes and deletes
  in `build/gates/<wp>/clone/`.
- **`SPECFIRST_KEEP_CLONE`** is unset before the clone's own commands run, like
  the other variables of the caller.
- **The PASS and FAIL lines** are the same apart from the old text "which does
  not last". **They are no longer the last line of the log:** the lines of the
  trap follow them. A tool that reads only the last line must look for
  `clean clone gate <wp>: PASS` instead.

Also changed: `CLAUDE.md` (the line on the script), `docs/lessons.md`
(lesson 73) and `docs/state/base.md`.

## Review finding N2 of base-0

N2 said that the script took the checkout from a caller's `SPECFIRST_ROOT`.
It was fixed in `4b12c86` (real-1): `in_checkout` sets `SPECFIRST_ROOT` to
the script's own checkout. Run T5 below checks it. It sets `SPECFIRST_ROOT`
to the gen worktree, whose HEAD is `b22289b`, and the log names this
checkout's repository and commit `86d356b`.

## Runs

The test script was run under WSL as a copy outside the checkout, with
nothing else running. It works in the base checkout itself.

```text
flock /run/lock/specfirst-heavy.lock taskset -c 0-3 bash /root/clone-tests.sh
```

`docs/reports/clone-cleanup.tests.sh` is that copy. Its whole output is
`docs/reports/clone-cleanup.tests.log`, and the log of the passing gate (T5)
is `docs/reports/clone-cleanup.gate.log`. The output, shortened:

```text
== commit: 86d356b clone-cleanup: the clean-clone gate deletes its clone when it ends
== T0 syntax
bash -n: ok
shellcheck: not installed
== T1 a name that is not a plain folder name
not a work package name: ../x
exit 2
not a work package name: .hidden
exit 2
== T2 FAIL (a commit that does not exist); clones before: 0
exit 128
clean clone gate clone-test-fail: FAIL ('git -C /tmp/specfirst-clean-hKDGig/specfirst checkout --quiet --detach no-such-commit' exited 128; clone: /tmp/specfirst-clean-hKDGig/specfirst)
clone deleted: /tmp/specfirst-clean-hKDGig
folder gone: /tmp/specfirst-clean-hKDGig
clones after: 0
== T3 FAIL with SPECFIRST_KEEP_CLONE=1; clones before: 0
exit 128
clone kept (SPECFIRST_KEEP_CLONE=1): /tmp/specfirst-clean-W6sEnk
folder kept: /tmp/specfirst-clean-W6sEnk
removed by this test
clones after: 0
== T4 TERM while a step runs; clones before: 0
sending TERM to the script at: $ git clone --quiet --no-local /mnt/d/trial_work/specfirst/.git /tmp/specfirst-clean-5tV65z/specfirst
exit 143
clone deleted: /tmp/specfirst-clean-5tV65z
folder gone: /tmp/specfirst-clean-5tV65z
clones after: 0
== T5 PASS: gate base-0, with SPECFIRST_ROOT set to another worktree (N2); clones before: 0
exit 0
repository: /mnt/d/trial_work/specfirst/.git
commit:     86d356b733ec28894ea259a078eb1bc44d301ae0
clean clone gate base-0: PASS (clone: /tmp/specfirst-clean-Nfvc9c/specfirst)
copied: the clone's build/gates/base-0/ to build/gates/base-0/clone/ here
clone deleted: /tmp/specfirst-clean-Nfvc9c
folder gone: /tmp/specfirst-clean-Nfvc9c
evidence.xml
gate.log
clones after: 0
== done
```

The gate of T5 (`specfirst gate base-0 --clean` in the clone):

```text
PASS  environment          0.3 s
PASS  pins                 0.8 s
PASS  lint                 0.0 s
PASS  unit tests         467.0 s
PASS  evidence tests     212.1 s
PASS  R packages           1.0 s
PASS  ASCII                0.0 s
GATE base-0: PASS
```

## Not covered

- **shellcheck** is not installed in the environment, so only `bash -n` checked
  the syntax.
- **HUP and INT** were not sent. They take the same path as TERM (T4).
- **A SIGKILL or `wsl --shutdown`** ends the script without the trap. Its
  folder then stays until `/tmp` is cleared at the next start of the instance.
  That clearing was seen on 2026-11-22: used space fell from 18 GB to 15 GB
  across the restart.
- **Other tracks' worktrees** still hold the old script until they merge `main`.
  A clean-clone gate run from such a worktree leaves its folder as before.
