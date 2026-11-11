# base-0 Bootstrap: report

Status: NOT PASSED. Interim report of 2026-11-11. The gate has not run,
because the Linux environment does not exist yet. Two steps need the owner
(section "Waiting for the owner"). Everything that could be built and
checked without Linux is done and committed on branch `track/base`.

Rule R8: the evidence below is the command and its output.

## What base-0 asks for, and where it stands

| Item of PLAN.md section 13.2 | State | Where |
| --- | --- | --- |
| Folder under git, first commit of PLAN.md and evidence/ | done | commit `004c24f` on `main` |
| Private GitHub repository `specfirst`, pushed | not done: `gh` is not installed and not logged in | waiting for the owner |
| Layout of section 12, MIT license, CLAUDE.md | done | commit `2ebb9a4`; `tests/unit/test_layout.py` |
| `.claude/settings.json` with deny rules for employer material | done, for `D:\trial_work\reference` | `.claude/settings.json`, and the same rules in `D:\trial_work\.claude\settings.json` |
| Environment in WSL2: Python, R, poppler, lock files | scripts written, not run: no Linux distribution in WSL | `env/`, `scripts/env.sh`; waiting for the owner |
| `specfirst fetch` at pinned commits, verified | done, run on Windows | below |
| The seven evidence scripts as tests | written, not run: they need the Linux environment | `tests/evidence/`, `tests/evidence_cases.py` |
| Shared formats v0: decision record, ARD, grid, graph | done | `standard/schemas/`, `tests/unit/test_schemas.py` |
| CI: tests, lint, ASCII check | written, not run: nothing is pushed yet | `.github/workflows/ci.yml` |
| Worktree script, one state file per track | done; the script's test runs under Linux only | `scripts/worktree.sh`, `docs/state/` |
| Licenses confirmed again in `third_party/SOURCES.md` | done | `third_party/SOURCES.md` |

## Waiting for the owner

1. Install the Linux distribution and create its user:
   `wsl --install -d Ubuntu-24.04`
2. Approve the Windows elevation prompt of the GitHub CLI installer (it has
   been open since 08:02), then run `gh auth login`.

After that the remaining steps are: `env/system.sh` and `make install` in
Ubuntu, `make lock` to write the lock files, `specfirst fetch` there,
`scripts/clean_clone_gate.sh base-0`, the final version of this report, the
independent review (R7), the merge to `main`, and the push.

## Evidence so far

All commands below ran on Windows with a scratch Python 3.13 environment
(PyYAML 6.0.3, jsonschema 4.26.0, pytest 9.2.0, ruff 0.17.4) and Git for
Windows 2.49. They are a first check only. They do not replace the gate.

### Fetch: 13 sources at their pinned commits

```text
> python -m specfirst fetch
cache: D:\trial_work\specfirst\third_party\cache
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
fetch: every pin verified
```

The cache is 2.7 GB with the git data; phuse-scripts is 1.1 GB of it. The
SHA-256 of the ARS example equals the one in appendix A. base-0 added two
file pins of its own, the CSR and the SAP of Pilot 6:

```text
> python -m specfirst fetch --verify      (last lines)
ok   ars:workfiles/examples/ARS v1/Common Safety Displays.json  sha256 90358dd60d687332f2138aa50435b4050fa91be3f52958169229daa269fe31b3
ok   p6:documents/CSR.pdf  sha256 0cab016c76abb3dcaef31110611c95dbd9cd00df083b35e6d28fd69fca0d842d
ok   p6:documents/SAP.pdf  sha256 210b7f1fdb0fd95e1b00b64fe1c7527d0000bd4e66b6ae31fdc08e2741af1bc7
fetch: every pin verified
```

### Lint and unit tests

```text
> python -m ruff check .
All checks passed!

> python -m pytest -m "not evidence" -q
SKIPPED [1] tests\unit\test_tools.py:92: the worktree script is a bash script
FAILED tests/unit/test_layout.py::test_bootstrap_file_exists[env/requirements.lock]
FAILED tests/unit/test_layout.py::test_bootstrap_file_exists[env/r-packages.lock]
2 failed, 207 passed, 1 skipped, 8 deselected in 15.12s
```

The two failures are the two lock files, which can only be written in the
Linux environment. The skipped test runs under Linux.

### The gate runner, on a machine that cannot pass

Run at commit `2ebb9a4` to see that the gate fails where it should:

```text
> python -m specfirst gate base-0      (headings and verdicts only)
gate base-0 at commit 2ebb9a4ab85a8b1546c226589bd3d860b27fbef0 (clean)
== [1/6] pins: specfirst fetch --verify
-- PASS pins (0.9 s)
== [2/6] lint: ruff check .
-- PASS lint (0.1 s)
== [3/6] unit tests: pytest -m "not evidence" -q
-- FAIL unit tests (15.3 s)
== [4/6] evidence tests: SPECFIRST_STRICT=1 pytest tests/evidence -m evidence -s -q
evidence: test_evidence[E1]: failure
evidence: test_evidence[E2-E3]: failure
evidence: test_evidence[E24]: failure
evidence: test_evidence[E25-csr]: failure
evidence: test_evidence[E25-single]: failure
evidence: test_evidence[E26]: failure
evidence: test_evidence[E27]: failure
evidence: test_evidence[E4]: failure
-- FAIL evidence tests (3.6 s)
== [5/6] R packages: Rscript --vanilla env/check_r.R $(cat env/r-packages.txt)
-- FAIL R packages (1.3 s)
== [6/6] ASCII: python -m specfirst.asciicheck
-- PASS ASCII (0.0 s)
GATE base-0: FAIL
exit code: 1
```

Seven evidence tests fail because the spikes cannot run without yamaa,
polars, pandas and SciPy. E27 runs, because it needs no library, and fails
on its counts: the `pdftotext` on the Windows path is Xpdf 4.00, not
poppler. That is lesson 3 in `docs/lessons.md`, caught by the check.

## Findings for the owner

1. The plan assumes WSL2; this machine had no Linux distribution. The owner
   chose to install Ubuntu 24.04 (ADR-000, item 2).
2. The session folder `D:\trial_work` holds `reference/` next to the plan.
   The repository is therefore its own folder, `D:\trial_work\specfirst`
   (ADR-000, item 1). The contents of `reference/` were never read, listed
   or searched; only the folder's name was seen, in the listing of
   `D:\trial_work`.
3. "CC BY 4.0 for content" could not be confirmed for the two CDISC
   repositories (ars, c360i): at the pinned commits only an MIT `LICENSE`
   file states a license. Nothing from them is committed, so nothing
   depends on it now (`third_party/SOURCES.md`).
4. Pilot 6 keeps its datasets as DVC pointers. Only its documents are real
   files. The evidence tests read the data from Pilot 7, as the plan does.
5. E5 (23 of 137 variables read) has no script output to test:
   `ars_spike.py` does not print it. It is not in the gate.
6. ADR-000 records the choices base-0 made where the plan is silent, the
   version 0 schema choices among them. It is a proposal until the owner
   has read it.

## Not done, and why

- Lock files, the Linux install, the evidence tests, the gate on a clean
  clone: no Linux environment yet.
- The private GitHub repository, the push, the first CI run: no `gh`.
- The container definition section 12 lists under `env/`: it could not be
  tested here; M2 needs it (ADR-000).
- The independent review (R7): it reviews the gate evidence, so it follows
  the gate.
