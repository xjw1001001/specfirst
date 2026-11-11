# base-0 Bootstrap: report

Date: 2026-11-11. Branch: `track/base`.

## Verdict

The gate passed. `specfirst gate base-0 --clean` exited 0 on a clean clone
of commit `1b509d2`, after a fresh install and a fresh fetch. The complete
output is in `docs/reports/base-0.gate.log` (250 lines); the section "The
gate" below quotes it.

This was the second gate run. The first one passed at commit `154f67e`. The
independent reviewer then found two blocking defects that the gate could
not see (section "Review, first pass"). They were fixed, eight smaller
findings with them, and the gate was run again on the commit that holds the
fixes.

The private GitHub repository exists and holds `main` and `track/base`. CI
succeeded on both gated commits (section "GitHub and CI").

The independent review (rule R7) is in `docs/reports/base-0.review.md`.
`track/base` merges to `main` once that review is signed (section 2.4).

## What base-0 asks for, and where it stands

| Item of PLAN.md section 13.2 | State | Where |
| --- | --- | --- |
| Folder under git, first commit of PLAN.md and evidence/ | done | commit `004c24f` on `main` |
| Private GitHub repository `specfirst`, pushed | done | section "GitHub and CI" |
| Layout of section 12, MIT license, CLAUDE.md | done, except the container definition | `tests/unit/test_layout.py`; section "Open" |
| `.claude/settings.json` with deny rules for employer material | done, for `D:\trial_work\reference` | `.claude/settings.json`; the same rules in `D:\trial_work\.claude\settings.json` |
| Environment in WSL2: Python, R, poppler, lock files | done | `env/`; section "Environment" |
| `specfirst fetch` at pinned commits, verified | done | gate check 2 |
| The seven evidence scripts as tests | done | `tests/evidence/`; gate check 5 |
| Shared formats v0: decision record, ARD, grid, graph | done | `standard/schemas/`; `tests/unit/test_schemas.py` |
| CI: tests, lint, ASCII check | done | `.github/workflows/ci.yml`; section "GitHub and CI" |
| Worktree script, one state file per track | done | `scripts/worktree.sh`, `docs/state/`; section "A worktree under WSL" |
| Licenses confirmed again in `third_party/SOURCES.md` | done | `third_party/SOURCES.md` |

## The gate

Gate text of PLAN.md section 13.2: on a clean clone, install, fetch and run
the evidence tests; they print the numbers of E1, E2 and E3, E24, E25, E26
and E27; R loads the listed packages; the ASCII check passes.

Command, run in Ubuntu 24.04 under WSL2 as root:

```text
$ bash scripts/clean_clone_gate.sh base-0
```

The script clones the repository with `git clone --no-local` into a new
folder under `/tmp`, checks out the commit, clears the environment variables
of the working checkout, and puts the Python environment, the R library and
the fetch cache of the clone under the same new folder. It then runs
`env/install.sh`, `specfirst fetch` and `specfirst gate base-0 --clean`.
`--clean` makes the gate fail if the tree has uncommitted changes.

The gate has seven checks. The plan's gate text names the evidence tests,
the R packages and the ASCII check; the environment check (drift first,
rule R3), the pin check, lint and the unit tests are additions.

Output. Lines are quoted as printed. `[...]` marks where lines of the full
log are left out: the 16 lines of each pin listing, the lines of
`specfirst doctor` already shown above them, pytest's progress dots, the
yamaa run summary with the ten per-dataset lines of E1, and the per-method
counts and listed differences of the two ARS runs.

```text
clean clone gate base-0
repository: /mnt/d/trial_work/specfirst/.git
commit:     1b509d284e55d260f6a2dbdf7a1c011dc03367c6
clone:      /tmp/specfirst-clean-wavkCP/specfirst
environment and cache: /tmp/specfirst-clean-wavkCP/env

$ git clone --quiet --no-local /mnt/d/trial_work/specfirst/.git /tmp/specfirst-clean-wavkCP/specfirst

$ git -C /tmp/specfirst-clean-wavkCP/specfirst checkout --quiet --detach 1b509d284e55d260f6a2dbdf7a1c011dc03367c6

$ git -C /tmp/specfirst-clean-wavkCP/specfirst log -1 --format=%H %s
1b509d284e55d260f6a2dbdf7a1c011dc03367c6 base-0: fixes from the first pass of the independent review

$ bash env/install.sh
python environment: /tmp/specfirst-clean-wavkCP/env/venv-specfirst-1299132708
R library: /tmp/specfirst-clean-wavkCP/env/r-lib
R packages: 99 wanted, 99 to install from https://packagemanager.posit.co/cran/__linux__/noble/2026-11-10
R library matches the lock: 99 packages in /tmp/specfirst-clean-wavkCP/env/r-lib
python     3.12.3  (/tmp/specfirst-clean-wavkCP/env/venv-specfirst-1299132708/bin/python)
python lock: 23 packages pinned, 0 differ
R          R version 4.6.2 (2026-10-29) -- "Diversified Portfolio"
R lock: 99 packages pinned, 0 differ
pdftotext  pdftotext version 24.02.0
git        git version 2.43.0
system lock: 32 packages recorded, 0 differ
doctor: ok

$ specfirst fetch
cache: /tmp/specfirst-clean-wavkCP/env/cache
ok   p7              fetched  213cb6ab3adc51abe4295cbbc546c0e6d46c3df8  (RConsortium/submissions-pilot7-synthetic-data)
ok   yamaa           fetched  93a6757594988fddc9b05d220d5f53deb5085d50  (elong0527/yamaa)
ok   ars             fetched  2c9b4b68724386e8f91dc576724855af7fafac65  (cdisc-org/analysis-results-standard)
ok   p6              fetched  a4f85c95cfef1f6aa27795362630f8ae43210185  (RConsortium/submissions-pilot6-adams-tlfs)
ok   atorus          fetched  fc8d658d7709aac0cccd753d0ca9ae6726090a61  (atorus-research/CDISC_pilot_replication)
ok   phuse           fetched  398a6d33ced9359ffb58c46650a6d488811176b1  (phuse-org/phuse-scripts)
ok   c360i           fetched  24bd98bdcea3db3046436e6a749bbbc92196fe12  (cdisc-org/360i)
ok   acdc            fetched  739344ca31203bb502efeee2b855286e17977be6  (cdisc-org/analysis-concepts)
ok   siera           fetched  9208a9b6a00876f13d2b17f01aa318290c066674  (clymbclinical/siera)
ok   cardinal        fetched  b1fe03a760a1ca3b4610830ba64be5bd3e6ff4a5  (pharmaverse/cardinal)
ok   pharma-skills   fetched  e5db96d54ef5a79cbfd06e2339a3351e4583f8da  (RConsortium/pharma-skills)
ok   pharmaverseraw  fetched  e0771afea8bead7e64bc7cf2ff53ef8b638c6c1b  (pharmaverse/pharmaverseraw)
ok   c360i-pocs      fetched  9f6de449cbff0c3f16fb10a93e4e79c7cd6ad43e  (lexjansen/cdisc360i-pocs)
ok   ars:workfiles/examples/ARS v1/Common Safety Displays.json  sha256 90358dd60d687332f2138aa50435b4050fa91be3f52958169229daa269fe31b3
ok   p6:documents/CSR.pdf  sha256 0cab016c76abb3dcaef31110611c95dbd9cd00df083b35e6d28fd69fca0d842d
ok   p6:documents/SAP.pdf  sha256 210b7f1fdb0fd95e1b00b64fe1c7527d0000bd4e66b6ae31fdc08e2741af1bc7
fetch: every pin verified

$ specfirst gate base-0 --clean
gate base-0 at commit 1b509d284e55d260f6a2dbdf7a1c011dc03367c6 (clean)

== [1/7] environment: specfirst doctor
[...]
system lock: 32 packages recorded, 0 differ
doctor: ok
-- PASS environment (0.3 s)

== [2/7] pins: specfirst fetch --verify
[...]
fetch: every pin verified
-- PASS pins (1.3 s)

== [3/7] lint: ruff check .
All checks passed!
-- PASS lint (0.0 s)

== [4/7] unit tests: pytest -m "not evidence" -q
[...]
241 passed, 8 deselected in 6.85s
-- PASS unit tests (7.0 s)

== [5/7] evidence tests: SPECFIRST_STRICT=1 pytest tests/evidence -m evidence -s -q

--- E1: yamaa rebuilds the 10 pilot ADaM datasets: 9,119,605 cells, 0 mismatches
[...]
TOTAL cells=9119605 mismatched=0 match=100.0000%
.
--- E2-E3: the ARS interpreter matches 3,711 of 3,735 results; 23 differ, 1 not computed
quantile definition: sas5
embedded results: 3735 {'match': 3711, 'differ': 23, 'not_computed': 1}
[...]
--- E4: with the R default quantile definition only 3,662 results match
quantile definition: r7
embedded results: 3735 {'match': 3662, 'differ': 72, 'not_computed': 1}
[...]
--- E24: CSR Table 14-2.01: 244 of 244 printed cells
CSR Table 14-2.01: printed cells parsed=244 reproduced=244 (100.0%)
.
--- E25-csr: CSR Table 14-5.01 with the CSR's double rounding: 1,175 of 1,175
CSR Table 14-5.01: rows parsed=254 (1 overall, 23 organ classes, 230 preferred terms); rows with no ADAE match=0
p-value display rule=csr: printed cells parsed=1175 reproduced=1175 (100.0%)
TEAE terms in ADAE missing from the parsed CSR table: 0 []
.
--- E25-single: CSR Table 14-5.01 with single rounding: 1,171 of 1,175
CSR Table 14-5.01: rows parsed=254 (1 overall, 23 organ classes, 230 preferred terms); rows with no ADAE match=0
p-value display rule=single: printed cells parsed=1175 reproduced=1171 (99.7%)
  differs: ('VOMITING', 'p', '0.209', ['>0.99', '0.208'])
  differs: ('SALIVARY HYPERSECRETION', 'p', '0.058*', ['0.057*'])
  differs: ('APPLICATION SITE ERYTHEMA', 'p', '0.003*', ['0.015*', '0.002*'])
  differs: ('SYNCOPE', 'p', '0.058*', ['0.057*', '0.118*'])
TEAE terms in ADAE missing from the parsed CSR table: 0 []
.
--- E26: CSR Table 14-6.06 under three pairs of rules: 38, 45 and 51 of 51
shift=footnote   baseline=reference    equal 38 of 51  p-values 0.405 and 0.386  (CSR prints 0.392 and 0.381)
shift=worst_case baseline=reference    equal 45 of 51  p-values 0.405 and 0.386  (CSR prints 0.392 and 0.381)
shift=worst_case baseline=last_predose equal 51 of 51  p-values 0.392 and 0.381  (CSR prints 0.392 and 0.381)
.
--- E27: CSR Tables 14-6.02 and 14-6.03: exact Fisher on 3 x 3 tables gives 59 of 59
14-6.02 BASOPHILS    no p-value printed; test defined: False
14-6.02: rows 30, with a printed p-value 29
14-6.03: rows 30, with a printed p-value 30
3 x 3 reading (low, normal, high): equal 59 of 59
3 x 2 reading (normal, abnormal):  equal 10 of 59
.
8 passed in 212.98s (0:03:32)
-- PASS evidence tests (213.1 s)

== [6/7] R packages: Rscript --vanilla env/check_r.R $(cat env/r-packages.txt)
planted defect: the check fails for specfirst.no.such.package (exit 1)
R version 4.6.2 (2026-10-29)
library paths: /tmp/specfirst-clean-wavkCP/env/r-lib : /usr/lib/R/library
cards      0.9.0
cardx      0.3.4
siera      0.5.6
emmeans    2.0.4
mmrm       0.3.19
coin       1.4.6
car        3.1.5
R loads 7 of 7 packages
-- PASS R packages (1.0 s)

== [7/7] ASCII: python -m specfirst.asciicheck
ASCII check: 95 files checked, 0 with non-ASCII bytes
-- PASS ASCII (0.0 s)

PASS  environment          0.3 s
PASS  pins                 1.3 s
PASS  lint                 0.0 s
PASS  unit tests           7.0 s
PASS  evidence tests     213.1 s
PASS  R packages           1.0 s
PASS  ASCII                0.0 s
GATE base-0: PASS

clean clone gate base-0: PASS (clone kept in /tmp/specfirst-clean-wavkCP/specfirst until /tmp is cleared)
```

### The numbers against the plan

| Evidence | PLAN.md expects | The gate printed |
| --- | --- | --- |
| E1 | 9,119,605 cells with 0 mismatches | `TOTAL cells=9119605 mismatched=0 match=100.0000%` |
| E2, E3 | 3,711 matches, 23 differences, 1 not computed | `3735 {'match': 3711, 'differ': 23, 'not_computed': 1}` |
| E4 (section 3.1, not in the gate text) | 3,662 matches with the R quantile definition | `3735 {'match': 3662, 'differ': 72, 'not_computed': 1}` |
| E24 | 244 of 244 | `parsed=244 reproduced=244 (100.0%)` |
| E25 | 1,175 of 1,175 and 1,171 of 1,175 | `reproduced=1175 (100.0%)` with rule `csr`; `reproduced=1171 (99.7%)` with rule `single` |
| E26 | 38, 45 and 51 of 51 | `equal 38 of 51`, `equal 45 of 51`, `equal 51 of 51` |
| E27 | 59 of 59 | `3 x 3 reading (low, normal, high): equal 59 of 59`; the 3 x 2 reading gives 10 of 59 |

The gate does not pass by skipping. Under `SPECFIRST_STRICT=1` a missing
prerequisite fails the test, a crashing spike fails it everywhere, and the
gate reads pytest's report and fails on any skipped, failed or missing
evidence test (`tests/unit/test_gates.py`). The checks on the printed text
have their own planted-defect tests (`tests/unit/test_evidence_checks.py`).
The reviewer looked for a way to pass the gate vacuously and found none.

The first gate run, at commit `154f67e`, printed the same evidence numbers
(`8 passed in 211.89s`), with 213 unit tests and six checks.

## Review, first pass

A fresh-context agent reviewed the diff `004c24f..154f67e` against the plan
while the first gate ran. It found no way for the gate to pass vacuously
and no wrong expected number. It reported ten findings. All ten were acted
on in commit `1b509d2`:

| # | Finding | Blocking | What was done |
| --- | --- | --- | --- |
| F1 | A track worktree made by Windows git cannot be opened by Linux git under WSL, so the ASCII check, two unit tests, the gate's commit line and the clean-clone script failed in a worktree | yes | `specfirst.paths.git_env` translates the worktree link for specfirst's own git calls; the clean-clone script uses it; `tests/unit/test_checkout_git.py`; section "A worktree under WSL" |
| F2 | `specfirst fetch --verify` did not see files the source itself ignores, such as Pilot 7's `*-yamaa.parquet`; the planted-defect test used a source without that rule | yes | the status call lists ignored files; the test uses a source with the rule |
| F3 | The graph schema rejected the `cites` edges real-1 and real-3 must write (from ADaM variables and analyses) | no | a `cites` edge may start at a decision, an ADaM variable or an analysis; ADR-000 names the tension in the plan |
| F4 | The decision-record schema required a class for a record in conflict and a citation for a `gold_quirk` | no | relaxed as section 4.5 and 4.8 say; ADR-000 lists what stays open |
| F5 | R's recommended packages came from apt unpinned; `doctor` only printed a note; the gate did not run `doctor`; `install_r.R` resolved by itself when the lock was missing | no | pinned in `env/system.lock` and installed at those versions; `doctor` fails on a difference and is gate check 1; `install_r.R` stops without a lock |
| F6 | No planted-defect tests for the R load check, the lock comparisons, the R version and the poppler check | no | `tests/unit/test_doctor.py`; the gate's R check proves itself on a package that does not exist |
| F7 | The shell deny rules matched only the absolute path of the reference folder | no | rules for the path relative to the checkout added, and tested |
| F8 | Outside the gate, a crashing spike was reported as skipped | no | only a missing prerequisite may skip |
| F9 | The clean-clone script was not isolated when `TMPDIR` is on a Windows drive; two checkouts with the same folder name shared an environment | no | the clone's environment and cache are under its own folder; one environment per checkout path |
| F10 | `docs/state/base.md` was stale; the gate only printed a dirty tree; no container definition | no | state file updated; `specfirst gate --clean`; the container definition stays open (section "Open") |

The reviewer also noted, outside the diff: `evidence/csr_hylaw_spike.py`
has the 51 printed values of CSR Table 14-6.06 typed in (finding 11 of
"Findings for the owner").

Lessons 8 and 9 in `docs/lessons.md` record F1 and F2. Both slipped through
because the first tests planted a simpler case than the real one.

## A worktree under WSL

Evidence for F1. A scratch clone at commit `1b509d2`, with a worktree made
by Windows git (`git worktree add -b track/real ../specfirst-real
track/base`), then used under WSL. `<scratch>` stands for the session's
scratch folder on the Windows drive C:.

```text
$ git rev-parse HEAD        (plain Linux git)
fatal: not a git repository: /mnt/c/<scratch>/wtreal/specfirst-real/C:/<scratch>/wtreal/specfirst/.git/worktrees/specfirst-real
exit=128

$ python3 -m specfirst.paths
export GIT_DIR=/mnt/c/<scratch>/wtreal/specfirst/.git/worktrees/specfirst-real
export GIT_OPTIONAL_LOCKS=0
export GIT_WORK_TREE=/mnt/c/<scratch>/wtreal/specfirst-real

$ git rev-parse HEAD        (with that environment)
1b509d284e55d260f6a2dbdf7a1c011dc03367c6
exit=0

$ make install
doctor: ok
$ make ascii
ASCII check: 95 files checked, 0 with non-ASCII bytes
$ make test
241 passed, 8 deselected in 11.16s
```

What still does not work in a worktree under WSL: plain `git`. Commits,
branches and merges are made with Windows git (CLAUDE.md, ADR-000 item 3).

## GitHub and CI

The owner approved the GitHub CLI login in a browser (device code). The
executor never saw a password or a token. The repository was created with
the command of the plan, without `--push`, because the checked-out branch
was `track/base` and `main` had to become the default branch:

```text
> gh repo create specfirst --private --source=. --remote=origin
https://github.com/xjw1001001/specfirst

> git push -u origin main
 * [new branch]      main -> main
> git push -u origin track/base
 * [new branch]      track/base -> track/base

> gh repo view --json nameWithOwner,visibility,defaultBranchRef
repository: xjw1001001/specfirst  visibility: PRIVATE  default branch: main
```

CI ran on each push of `track/base`:

```text
> gh run view 43033235794 --json status,conclusion,headSha,headBranch,url,jobs
status: completed  conclusion: success  branch: track/base  commit: 154f67e6db5a49026143fb5964adb044a91a9ccd
https://github.com/xjw1001001/specfirst/actions/runs/43033235794
  success  Set up job
  success  Run actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803
  success  Python environment from the lock file
  success  ASCII check
  success  Lint
  success  Unit tests
  success  Post Run actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803
  success  Complete job

> gh run view 43037218136 --json status,conclusion,headSha,headBranch,url,jobs
status: completed  conclusion: success  branch: track/base  commit: 1b509d284e55d260f6a2dbdf7a1c011dc03367c6
https://github.com/xjw1001001/specfirst/actions/runs/43037218136
  success  Set up job
  success  Run actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803
  success  Python environment from the lock file
  success  ASCII check
  success  Lint
  success  Unit tests
  success  Post Run actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803
  success  Complete job
```

The `gh ... view` commands ran with `--json` and a `--jq` filter that prints
the fields shown.

git reaches GitHub through `gh` as the credential helper for github.com,
set in this repository's own configuration only (`.git/config`), not in the
user's global configuration.

## Environment

Ubuntu 24.04.5 LTS in WSL2 (kernel 6.6.87.2), installed in this session. It
has no Linux user of its own yet; everything ran as root. The checkout stays
on the Windows drive (`/mnt/d/trial_work/specfirst`).

| Part | Version | Pinned by |
| --- | --- | --- |
| Python | 3.12.3 (Ubuntu) | `env/system.lock`, for information |
| yamaa, polars, pyarrow, PyYAML | 0.7.0, 1.44.2, 25.0.1, 6.0.3 | `env/requirements.lock`, with hashes |
| pandas, SciPy, NumPy | 3.1.1, 1.18.1, 2.5.4 (the versions of appendix A) | `env/requirements.lock` |
| jsonschema, pytest, ruff, setuptools | 4.26.0, 9.2.0, 0.17.4, 84.2.1 | `env/requirements.lock` |
| R | 4.6.2, from CRAN's repository for Ubuntu | `env/r-version.txt` |
| R's recommended packages (Matrix 1.7-6, MASS 7.3-66, nlme 3.1.172, survival 3.8-12 and 11 more) | system packages from the same repository | `env/system.lock`; `doctor` fails on a difference |
| cards, cardx, siera, emmeans, mmrm, coin, car | 0.9.0, 0.3.4, 0.5.6, 2.0.4, 0.3.19, 1.4-6, 3.1-5 | `env/r-packages.lock` (99 packages, snapshot of 2026-11-10) |
| poppler `pdftotext` | 24.02.0 | `env/system.lock`, for information |
| git, make | 2.43.0, 4.3 | `env/system.lock`, for information |

Python is 3.12.3, not the 3.13.18 of the plan's sandbox; the plan asks for
3.12 or later, and every evidence number is the same.

## Decisions and deviations

`docs/decisions/ADR-000.md` records them. In short:

1. The repository is its own folder next to `reference/`, not the folder
   the session started in (owner's choice).
2. Ubuntu 24.04 in WSL2 (owner's choice). The machine had no Linux
   distribution.
3. Windows git writes the checkout and its worktrees; under WSL
   specfirst's own git calls translate a worktree's link.
4. Under WSL the Python environment, the R library and the fetch cache live
   on the Linux file system (`scripts/env.sh`).
5. R is 4.6.2 from CRAN's Ubuntu repository, not Ubuntu's 4.3.3, which the
   current `car` no longer supports (lesson 7).
6. The spikes run unchanged, as subprocesses; the tests check their output.
7. The version 0 schema choices where the plan is silent, and four points
   where the plan pulls two ways. The owner should confirm those four, at
   N1 at the latest.

The plan itself was not changed. `PLAN.md` in the repository is byte for
byte the file of 2026-11-11 07:52 (SHA-256 `234a642a...072e4c`); the copy in
`D:\trial_work\plan` was compared again before each gate run and had not
changed.

## Findings for the owner

1. The contents of `reference/` were never read, listed or searched; only
   the folder's name was seen, in the listing of `D:\trial_work`.
2. "CC BY 4.0 for content" could not be confirmed for the two CDISC
   repositories (ars, c360i): at the pinned commits only an MIT `LICENSE`
   file states a license. Nothing from them is committed
   (`third_party/SOURCES.md`).
3. E1 reports 0 mismatched cells and also 14 to 38 type differences per
   dataset between the built and the reference ADaM (the column types
   differ, the values do not). The spike does not count them. real-1 should
   decide what its P2 test and its canonical writers do with them.
4. The single rounding of E25 differs from the CSR in 4 cells, on 4 terms:
   VOMITING, SALIVARY HYPERSECRETION, APPLICATION SITE ERYTHEMA, SYNCOPE.
   This is the known case of decision 17.
5. E27: Table 14-6.02 prints no p-value for BASOPHILS, so 29 of its 30 rows
   and all 30 of Table 14-6.03 make the 59.
6. Pilot 6 keeps its datasets as DVC pointers. Only its documents are real
   files; base-0 pinned the CSR and the SAP by SHA-256.
7. E5 (23 of 137 variables read) has no script output to test:
   `ars_spike.py` does not print it. It is not in the gate.
8. ADR-000 is a proposal until the owner has read it.
9. The Ubuntu distribution has no Linux user. The environment is under
   `/root/.local/share/specfirst`. If the owner creates a user later, run
   `make install` and `specfirst fetch` once as that user.
10. `gh` 2.103.3 is the portable build in
    `%LOCALAPPDATA%\Programs\gh\bin\gh.exe`. It is not on the PATH. The
    system-wide installer was cancelled because its elevation prompt was
    never answered.
11. From the review: `evidence/csr_hylaw_spike.py` (the owner's file, first
    commit) has the 51 printed values of CSR Table 14-6.06 typed in. Rule 4
    of section 2.1 keeps reference grids parsed from the CSR in the cache.
    The repository is private, so nothing is redistributed now. Decide
    before it becomes public (question 1 of section 16); real-5 replaces
    the spike in any case.

## Open

- Merge `track/base` to `main` after the review is signed, then push both
  (section 2.4).
- The container definition section 12 lists under `env/`: not written,
  because it could not be tested here; M2 needs it (ADR-000). The owner
  should accept or reject this gap.
- The cache fetched on the Windows side during the first checks
  (`third_party/cache`, 2.7 GB, ignored by git) is no longer needed by the
  Linux environment and can be deleted.

## Lessons

Nine, in `docs/lessons.md`, each with the check that now catches it.
