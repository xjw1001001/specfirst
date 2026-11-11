# base-0 Bootstrap: independent review

Reviewed: work package base-0 of PLAN.md section 13.2, on branch
`track/base`.

- First pass: the diff `004c24f..154f67e` (commits `2ebb9a4`, `42583d8`,
  `75fc600`, `154f67e`) against PLAN.md.
- Second pass: the fixes in `154f67e..1b509d2`, and commit `9762296` with
  the final report `docs/reports/base-0.md`, the gate log
  `docs/reports/base-0.gate.log` and `docs/state/base.md`.

Date: 2026-11-11.

Reviewer: an independent agent with a fresh context that did not write the
work (rule R7). Correctness only, no style remarks. The reviewer changed no
file except this one and made no commit.

## Verdict

PASS: base-0 may merge to `main`. The verdict applies to commit
`97622965d140daaec6287b86a97b250cd9667898` (`9762296`).

The gate evidence is for commit `1b509d2`. Commit `9762296` adds only the
report, the gate log and the state file (`git diff --stat 1b509d2..9762296`
lists these three files and nothing else).

No blocking finding remains. The two blocking findings of the first pass
(F1, F2) are fixed and were verified by rerunning the planted defects. Two
new findings of the second pass (N1, N2) are not blocking. Items left open
for the owner are named in the sections below.

## Scope and method

### What was read

- PLAN.md sections 2, 3, 4, 5, 6.5, 7, 8, 9, 10, 11, 12, 13, 16, 17 and
  appendices A and B.
- Every file of the diff `004c24f..9762296`, in full: `src/specfirst/`,
  `tests/`, `standard/schemas/` with its examples, `env/`, `scripts/`,
  `Makefile`, `pyproject.toml`, `.claude/settings.json`, `.gitignore`,
  `.gitattributes`, `.github/workflows/ci.yml`, `CLAUDE.md`, `README.md`,
  `docs/` and `third_party/`.
- The seven scripts in `evidence/` as far as their printed output goes
  (they are the owner's files of commit `004c24f` and were not changed).
- The two gate logs: the first run at `154f67e` (read from
  `build/gates/base-0/clean-clone.log` while that run was still writing it)
  and the second run at `1b509d2` (`docs/reports/base-0.gate.log`).

### What was run

All Linux commands ran in Ubuntu 24.04.5 under WSL2 as root, after
`. scripts/env.sh`. Exit codes were read inside script files, not through
nested shells. `<scratch>` stands for a scratch folder outside the
repository.

In the main checkout at `9762296`:

| Command | Key output |
| --- | --- |
| `python -m pytest -m "not evidence" -q` | `241 passed, 8 deselected`, exit 0 |
| `python -m ruff check .` | `All checks passed!`, exit 0 |
| `python -m specfirst.asciicheck` | `ASCII check: 96 files checked, 0 with non-ASCII bytes`, exit 0 |
| `specfirst fetch --verify` | 13 sources `present`, 3 file hashes ok, `fetch: every pin verified`, exit 0 |
| `specfirst doctor` | `python lock: 23 packages pinned, 0 differ`; `R lock: 99 packages pinned, 0 differ`; `system lock: 32 packages recorded, 0 differ`; `doctor: ok`; exit 0 |
| `specfirst gate no-such-wp` | `no gate is defined for 'no-such-wp' yet`, exit 2 |
| `bash -n` on the six shell scripts of `env/` and `scripts/` | no syntax error |

In a worktree that Windows git made from a scratch clone at `1b509d2`
(its `.git` file reads `gitdir: C:<scratch>/specfirst/.git/worktrees/specfirst-real`):

| Command | Key output |
| --- | --- |
| `git rev-parse HEAD` (plain Linux git) | `fatal: not a git repository`, exit 128 |
| `python -m specfirst.paths` | `export GIT_DIR=...`, `export GIT_OPTIONAL_LOCKS=0`, `export GIT_WORK_TREE=...` |
| `git rev-parse HEAD` with those variables | `1b509d284e55d260f6a2dbdf7a1c011dc03367c6`, exit 0 |
| `python -m specfirst.asciicheck` | `ASCII check: 95 files checked, 0 with non-ASCII bytes`, exit 0 |
| `python -m pytest -m "not evidence" -q` | `241 passed, 8 deselected`, exit 0 |
| `gates.head(<worktree>)` | `('1b509d284e55d260f6a2dbdf7a1c011dc03367c6', True)` |

Planted defects, by hand, on scratch copies:

| What was planted | Key output |
| --- | --- |
| A source whose own `.gitignore` has `data/*-yamaa.parquet` (the rule of Pilot 7, line 12 of its `.gitignore`), fetched with `fetch.fetch_all`, then `data/adsl-yamaa.parquet` added | at `154f67e`: `fetch: every pin verified`. At `9762296`: `FAIL demo error working tree is not clean: 1 path(s), first: data/adsl-yamaa.parquet`, `fetch: FAILED` |
| `r-cran-matrix 0.0-0` and `curl 0.0.0` in a copy of `env/system.lock`, then `doctor.run` on that copy | `FAIL r-cran-matrix: installed 1.7-6-1.2404.0, lock has 0.0-0`; `note: system package curl: ...`; `doctor: FAILED`; return code 1 |
| `env/install_r.R` in a copy of `env/` without `r-packages.lock` | `Error: env/r-packages.lock is missing; an install never resolves versions by itself.`, exit 1, nothing written or installed |
| `Rscript --vanilla env/check_r.R cards nosuchpackagexyz` | `R loads 1 of 2 packages`, exit 1; also exit 1 with no argument and with `SPECFIRST_R_LIBS` unset |
| `doctor.load_r_packages` with the real R | `planted defect: the check fails for specfirst.no.such.package (exit 1)`, then `R loads 7 of 7 packages` |
| The 39 invalid schema examples and about 80 further instances | every invalid example is rejected, 38 of them for exactly one reason, the stated one (the 39th, an unknown ID prefix, trips two patterns); all 27 valid examples are accepted; details under F3, F4 and N1 |

Other checks:

| Command | Key output |
| --- | --- |
| Script: every line of the report's gate block against `docs/reports/base-0.gate.log` | 144 quoted lines, 6 `[...]` marks, 0 lines not found in order, 0 log lines left out without a mark |
| `cmp build/gates/base-0/clean-clone.log docs/reports/base-0.gate.log` | identical (the first file is what the script's `tee` wrote, between the commit times of `1b509d2` and `9762296`) |
| Byte check of the gate log and the report | 250 lines, 0 CR, 0 non-ASCII bytes |
| `git ls-tree -r --name-only <commit>`, counted | 95 files at `1b509d2`, the number the log's ASCII check prints; 96 at `9762296` |
| `git diff --quiet 004c24f..9762296 -- PLAN.md evidence`; `sha256sum PLAN.md` | unchanged; `234a642a...072e4c`, as the report says |
| `gh repo view xjw1001001/specfirst --json visibility,isPrivate,defaultBranchRef` | `visibility=PRIVATE isPrivate=true default=main` |
| `gh run list` and `gh run view` for runs 43033235794 and 43037218136 | both `completed success`, on `154f67e` and `1b509d2`; every step `success`, among them ASCII check, Lint, Unit tests |
| `gh api repos/xjw1001001/specfirst/branches` | `main 004c24f...`, `track/base 1b509d2...` |
| `git ls-remote https://github.com/actions/checkout` | `d23441a48e516b6c34aea4fa41551a30e30af803` is `refs/tags/v6.1.0`, as pinned in `ci.yml` |
| `apt-get install -s` with the `r-base*` and the 15 `r-cran-*=<version>` pins of `env/system.lock` (simulation, installs nothing) | `0 upgraded, 0 newly installed`, exit 0 |
| Count of pins and hashes in `env/requirements.lock` | 23 pins, 489 `--hash=sha256:` lines, no pin without a hash |

The reviewer did not rerun the gate or the evidence tests (see "Not
verified").

## The gate against PLAN.md section 13.2

The gate text asks for a clean clone, an install, a fetch, the evidence
numbers, R loading the listed packages and the ASCII check. Line numbers
are those of `docs/reports/base-0.gate.log`.

| Required | In the log | Line |
| --- | --- | --- |
| clean clone, fresh install, fresh fetch | clone under `/tmp`, own environment and cache under the same new folder, `99 to install`, 13 sources `fetched`; `gate base-0 at commit 1b509d28... (clean)` | 1 to 49 |
| E1: 9,119,605 cells, 0 mismatches | `TOTAL cells=9119605 mismatched=0 match=100.0000%` | 120 |
| E2, E3: 3,711, 23, 1 | `embedded results: 3735 {'match': 3711, 'differ': 23, 'not_computed': 1}` | 124 |
| E24: 244 of 244 | `printed cells parsed=244 reproduced=244 (100.0%)` | 192 |
| E25: 1,175 and 1,171 of 1,175 | `reproduced=1175 (100.0%)` with rule `csr`; `reproduced=1171 (99.7%)` with rule `single` | 196, 201 |
| E26: 38, 45 and 51 of 51 | `equal 38 of 51`, `equal 45 of 51`, `equal 51 of 51` | 209 to 211 |
| E27: 59 of 59 | `3 x 3 reading (low, normal, high): equal 59 of 59` | 217 |
| R loads the listed packages | `R loads 7 of 7 packages`, after the planted defect failed | 224, 234 |
| The ASCII check passes | `ASCII check: 95 files checked, 0 with non-ASCII bytes` | 238 |
| Exit 0 | `8 passed in 212.98s`; `GATE base-0: PASS`; `clean clone gate base-0: PASS` | 220, 248, 250 |

Every expected number in `tests/evidence_cases.py` equals PLAN.md (sections
3 and 3.1). The gate also checks E4 (3,662 matches) and the 3 x 2 reading
of E27 (10 of 59), which section 3.1 gives and the gate text does not.

The reviewer looked for a way to pass the gate without the evidence and
found none: a skipped, failed or missing evidence test fails it (the gate
reads pytest's JUnit report, `src/specfirst/gates.py:69-84`), a crashing
check is a failing check (`gates.py:182-184`), every exit code is checked,
the report file of an earlier run is deleted first, and the clean-clone
script stops at the first step that fails.

## Findings of the first pass and their status

Blocking means: the work package should not pass with it.

### F1. A track worktree made by Windows git could not run tests, the ASCII check or a gate under WSL. Blocking.

Linux git cannot follow the `gitdir: D:/...` link that Windows git writes,
and the code called `git` in the checkout.

Status: fixed and verified.

- `src/specfirst/paths.py:83-111` (`git_env`) translates the link and sets
  `GIT_DIR` and `GIT_WORK_TREE` for specfirst's own read-only git calls.
  `src/specfirst/asciicheck.py`, `src/specfirst/gates.py:141-151` and
  `scripts/clean_clone_gate.sh:26-34` use it.
- `tests/unit/test_checkout_git.py` plants a Windows-style link, shows the
  failure without the translation and the result with it.
- Rerun by the reviewer in a real worktree made by Windows git (table
  above): plain git exits 128; with `git_env` the ASCII check exits 0 and
  241 unit tests pass.
- Still true and documented (CLAUDE.md, ADR-000 item 3): plain `git` fails
  in such a worktree under WSL; commits are made with Windows git.

### F2. `specfirst fetch --verify` did not see a leftover file that the source itself ignores. Blocking.

Lesson 5 and a CLAUDE.md gotcha claimed that it did.

Status: fixed and verified.

- `src/specfirst/fetch.py:59` passes `--ignored`.
- `tests/unit/test_fetch.py::test_output_that_the_source_itself_ignores_fails`
  uses a source with the ignore rule and first shows that plain status sees
  nothing.
- The reviewer's own probe, which passed wrongly at `154f67e`, now prints
  `fetch: FAILED` (table above). The real cache has no ignored or untracked
  file in `p7`, `p6` or `ars`, and `specfirst fetch --verify` passes on it.
- Lessons 5 and 9 and the CLAUDE.md gotcha now say what the check does.

### F3. The graph schema rejected `cites` edges that section 13.3 tells real-1 and real-3 to write. Not blocking.

Status: fixed; one point is left to the owner by ADR-000.

- `standard/schemas/graph.schema.json:102-106`: a `cites` edge starts at a
  decision, an ADaM variable or an analysis and ends at a document span.
  This is not wider than the plan text: section 4.2 (decision), section 13.3
  real-1 (claims for ADaM variables) and real-3 (ARS `documentRefs`).
- A `cites` edge still cannot carry a proof other than `judged`
  (`graph.schema.json:86-94`). Probed for all three starting layers: proof
  `static`, proof `executed` and no proof are each rejected; a start at a
  cell, an SDTM variable, an ARD row, a document, a USDM or an ODM element
  is rejected; an end that is not a document is rejected.
- ADR-000 item 7 names the tension between sections 4.2 and 13.3 and asks
  the owner to confirm, at N1 at the latest.

### F4. The decision-record schema required `class` on a record in conflict, and no status fitted a `gold_quirk` with a value. Not blocking.

Status: fixed, with one rule now wider than needed (see N1).

- `standard/schemas/decision-record.schema.json:61-67`: a record in
  `conflict` needs no class (section 4.5); every other record does. Probed:
  `stated`, `default`, `asked` and `not_applicable` without a class are
  rejected.
- A `gold_quirk` no longer needs a citation (section 4.8). Which status it
  carries is left to the owner (ADR-000 item 7).

### F5. R's recommended packages were unpinned, `doctor` only printed a note, the gate did not run `doctor`, and `install_r.R` resolved versions when the lock was missing. Not blocking.

Status: fixed and verified, except that `env/system.sh` was not executed.

- `env/system.sh:42-49` installs the `r-cran-*` versions of
  `env/system.lock`. Not executed by the reviewer; an apt simulation with
  the same pins exits 0.
- `src/specfirst/doctor.py:233-241` fails on a difference for a system
  package named `r-*`. Verified with a planted lock (table above).
- `specfirst doctor` is check 1 of the gate (`gates.py:128`; log line 51
  onward, `doctor: ok` at line 59).
- `env/install_r.R:49-52` stops without a lock. Verified by running it.
- Declared and unchanged (ADR-000 item 5): Python, poppler and the other
  apt packages are recorded for information only; `doctor` prints a note.
  The comparison with `env/system.lock` is skipped where `dpkg-query` does
  not exist (`doctor.py:233`); the reference platform has it.

### F6. Several checkers had no planted-defect test (rule R5). Not blocking.

Status: fixed.

- `tests/unit/test_doctor.py` plants drift for the lock comparisons, the R
  version and the poppler check, and ties `env/r-packages.txt` to the seven
  packages of the plan and the Python lock to seven versions of the plan.
- `doctor.load_r_packages` (`doctor.py:169-192`) runs the checker on a
  package that does not exist on every call and fails if that passes; the
  gate log shows it (line 224).
- Remaining gap, small: no unit test covers how `doctor.run` itself sorts
  system-package differences into failures and notes. The reviewer planted
  that defect by hand and it failed as it should.

### F7. The shell deny rules matched only the absolute path of the reference folder. Not blocking.

Status: fixed. `.claude/settings.json` has six more rules for `../reference`
in its three spellings, for Bash and PowerShell, and
`tests/unit/test_layout.py:68-71` checks them. The rules match the text of
one command; whether the permission matcher applies them was not tested,
because that would mean touching the folder.

### F8. Outside the gate, a crashing spike was reported as skipped. Not blocking.

Status: fixed. `tests/evidence_cases.py:30-35` separates
`MissingPrerequisite` from `EvidenceError`;
`tests/evidence/test_evidence.py:32` skips only on the former. A unit test
in `tests/unit/test_tools.py` checks the two classes.

### F9. The clean-clone script was not isolated when `TMPDIR` is on a Windows drive; two checkouts with the same folder name shared one environment. Not blocking.

Status: fixed by reading; not executed by the reviewer.

- `scripts/clean_clone_gate.sh:47-53` unsets `PIP_*`, `PYTHONPATH`,
  `PYTHONHOME`, `GIT_DIR`, `GIT_WORK_TREE` and the `SPECFIRST_*` variables
  and sets `SPECFIRST_HOME` to a folder next to the clone. The log shows
  the result: environment and cache under `/tmp/specfirst-clean-wavkCP/env`,
  99 R packages installed, 13 sources fetched.
- `scripts/env.sh:40` adds a checksum of the checkout path to the
  environment name. Sourcing it with `SPECFIRST_HOME` set gave the three
  expected paths.

### F10. The state file was stale, the gate only printed a dirty tree, and `env/` has no container definition. Not blocking.

Status: two parts fixed, one declared open for the owner.

- `docs/state/base.md` is current.
- `specfirst gate <wp> --clean` fails on uncommitted changes
  (`gates.py:171-174`, `tests/unit/test_gates.py`); the clean-clone script
  uses it and the log shows `(clean)`.
- The container definition that section 12 lists under `env/` is not
  written. ADR-000 ("Not done in base-0") and the report ("Open") declare
  it. The owner should accept or reject this gap.

### Observation outside the diff: typed-in CSR values

`evidence/csr_hylaw_spike.py` (the owner's file, commit `004c24f`) holds the
51 printed values of CSR Table 14-6.06. Rule 4 of section 2.1 keeps
reference grids parsed from the CSR in the cache.

Status: not changed; declared open for the owner as finding 11 of the
report and in `docs/state/base.md`. The repository is private.

## New findings of the second pass

### N1. The citation rule of the decision record is wider than F4 needed. Not blocking.

`standard/schemas/decision-record.schema.json:77-90` asks for a citation
only when the class is `document_rule` or `house_default`. Probed: a record
with status `stated` or `default`, class `study_input` or `no_gold`, a
value and no citation is accepted.

- Plan text: a stated decision cites its document and a default cites the
  house standard (section 4.3, section 5.2 rule 4, decision 3 of section
  17). Section 4.5 defines `study_input` as "nowhere in the inputs", which
  fits neither `stated` nor `default`. Section 4.8 supports the exemption
  for `gold_quirk` only.
- `docs/decisions/ADR-000.md:96-97` states the rule as the schema has it,
  but lines 113-114 say version 0 "only stops asking a `gold_quirk` for a
  citation", which is not what the schema does. The report's row for F4
  says the same.
- No invalid example covers the combination.

Not blocking: the gate does not depend on it, std-1 owns the schemas of
decision records (section 13.4), and ADR-000 already sends the class and
status rules to the owner. Narrow the exemption to `gold_quirk`, or state
the wider rule in ADR-000, before N1.

### N2. The clean-clone script takes the checkout from `SPECFIRST_ROOT` when the caller has it set. Not blocking.

`scripts/clean_clone_gate.sh:26-34` finds the repository and the commit
with `python3 -m specfirst.paths`, whose `repo_root()`
(`src/specfirst/paths.py:114-116`) obeys `SPECFIRST_ROOT`. The script
unsets that variable only at line 51.

Probed: in the main checkout (HEAD `9762296`), with `SPECFIRST_ROOT` naming
the scratch worktree, the helper exported that worktree's `GIT_DIR` and
`git rev-parse HEAD` returned `1b509d28...`. The script would then gate the
commit of another checkout than the one it was started in.

Not blocking: nothing in the project sets `SPECFIRST_ROOT`, the variable
changes the result only when it names a worktree with a foreign link, and
the log prints the commit that was gated.

## Not verified

- The gate and the evidence tests were not rerun by the reviewer. The
  evidence numbers rest on `docs/reports/base-0.gate.log`, which is byte
  for byte the output file of the clean-clone script, and on the log of the
  first run at `154f67e`, which printed the same numbers. Everything else
  the gate checks (environment, pins, lint, unit tests, R packages, ASCII)
  was rerun by the reviewer at `9762296`.
- `scripts/clean_clone_gate.sh` was not executed by the reviewer, neither
  in the main checkout nor in a worktree; nor was `specfirst gate` in a
  worktree. The clone folder under `/tmp` was not inspected.
- `env/system.sh` and `env/lock.sh` were not executed, nor `make install`.
  Whether CRAN's repository for Ubuntu and the snapshot of 2026-11-10 keep
  serving the pinned versions cannot be known now.
- CI has not run on `9762296`, which was not pushed at review time, nor on
  the commit that will add this file. The three CI steps pass locally at
  `9762296`.
- `D:\trial_work\.claude\settings.json`, which the report says holds the
  same deny rules, is outside the repository and was not read. Whether
  Claude Code's permission matcher applies the rules as intended was not
  tested.
- The report's statement that PLAN.md was compared with a copy outside the
  repository. Verified instead: PLAN.md is unchanged since `004c24f` and
  has the SHA-256 the report gives.
- The license statements in `third_party/SOURCES.md` beyond the presence of
  the top-level license files in the cache (consistent for all 13 sources).
- The unit tests on Windows; the tests of `test_checkout_git.py` and the
  stand-in `Rscript` tests are skipped there.
