# specfirst

PLAN.md is the plan and the contract. Read the sections your prompt names.
Handover per track: docs/state/<track>.md. Failures seen once: docs/lessons.md.

## Commands (Linux: WSL2 Ubuntu 24.04)

- `sudo bash env/system.sh`, then `make install`: system packages, then the Python environment and R library from env/*.lock
- `. scripts/env.sh`: once per shell; puts `specfirst` on the path and finds the cache
- `make test`, `make lint`, `make ascii`: unit tests, ruff, ASCII check (what CI runs)
- `specfirst fetch`: clone the pinned sources into the ignored cache; `--verify` downloads nothing
- `specfirst gate <wp>`: the gate of a work package; its log is build/gates/<wp>/gate.log
- `specfirst catalog [--roundtrip|--sources|--yamaa|--run|--tables]`, `specfirst house [--write]`: the checks of the catalog and of the house standard
- `specfirst compile --decisions d.jsonl --defaults --out DIR`; `specfirst render`, `specfirst parse`: decisions to specs; decisions to a standard-form document and back
- `scripts/clean_clone_gate.sh <wp>`: the same gate on a fresh clone with a fresh install and fetch
- `make evidence`: rerun the evidence spikes (about 7 minutes)
- `specfirst status`, `specfirst doctor`: all state files; the environment against the locks
- `scripts/worktree.sh <track>`: worktree ../specfirst-<track> on branch track/<track>
- From a Windows session: `wsl -d Ubuntu-24.04 -- bash -lc "cd /mnt/d/trial_work/specfirst && make test"`

## Rules (PLAN.md section 2)

1. Public sources only. Record every imported file in third_party/SOURCES.md.
2. Never read a folder named reference/ or any employer material. If pasted text looks internal, stop and ask.
3. Names, module boundaries and table families come from public standards; each catalog entry cites its source.
4. Never commit third-party study data or documents. They stay in the fetch cache.
5. Original code and documents are MIT.
6. Publishing is the owner's act. Pushing to the private origin is expected; anything other people can see needs the owner's approval of the exact text first.
7. One-way flow: nothing from an employer's machines or studies comes back into this repository.

- R1 Agents propose, scripts decide. R2 Reuse before build; record the choice in an ADR.
- R3 Pin everything. R4 Determinism: no clock, no unseeded randomness, sorted outputs.
- R5 Tests first: a checker counts only after it fails on a planted defect.
- R6 Specs carry rules, not numbers. R7 A fresh-context reviewer signs docs/reports/<wp>.review.md.
- R8 Reports show the command and its output. R9 Keep scope: one work package, dependencies first.
- R10 ASCII only in maintained files. R11 Python and R must agree on descriptive methods, simple tests and CMH.
- Work on branch track/<name>. Merge to main only after gate and review, then push main and the track branch.
- PLAN.md and standard/schemas/ change only through an ADR in docs/decisions/ that the owner approves.
- Stop for the owner at N1, N2, N3 and in the cases of PLAN.md section 2.3.

## Gotchas

- The checkout is on a Windows drive and Windows git owns it and its worktrees: commit, branch and merge with Windows git only. Under WSL plain `git` fails in a worktree (its link is a Windows path); specfirst's own git calls translate the link (`specfirst.paths.git_env`).
- Under WSL the Python environment, R library and fetch cache are in ~/.local/share/specfirst, not in the checkout (scripts/env.sh). In a new worktree run `make install` once.
- .gitattributes keeps every text file LF. A new script needs `git update-index --chmod=+x <file>`.
- Git for Windows ships Xpdf's pdftotext. CSR text must come from poppler (24.02 in Ubuntu 24.04).
- The yamaa run writes <dataset>-yamaa.parquet next to the reference data. Work on a copy: `specfirst fetch --verify` fails on a cache with any changed, added or ignored file.
- R and its recommended packages are pinned system packages (env/r-version.txt, env/system.lock); `specfirst doctor` fails on drift and is the first check of every gate.
- scipy.stats.fisher_exact is exact for 2 x 2 tables only (E27).
- Pilot 7 names: the spec is adqsnipx.yaml, the reference file is adqsnpix.parquet.
- Searches started in D:\trial_work reach reference/. Always work from inside the checkout.
- `yamaa check` reads no data: a spec can pass it and fail when run. Run a changed fragment (`specfirst catalog --run`).
- standard/houses/open-default@1/STANDARD.md is rendered: after a catalog change run `specfirst house --write`.
