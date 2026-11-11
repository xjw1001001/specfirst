# Track base

Result: repository, environment, pins, shared formats (PLAN.md section 13.2).

## Passed

- Nothing yet. base-0 is in progress; its gate has not run.

## Open

- base-0 waits for the owner: install Ubuntu 24.04 in WSL
  (`wsl --install -d Ubuntu-24.04`), approve the GitHub CLI installer and
  run `gh auth login`. docs/reports/base-0.md has the interim evidence.
- Then, in order: `env/system.sh` and `make install` in Ubuntu, `make lock`
  (writes env/requirements.lock, env/r-packages.lock, env/system.lock),
  `specfirst fetch`, `scripts/clean_clone_gate.sh base-0`, the final
  report, the independent review, the merge to main, the push, the first
  CI run.
- ADR-000 is a proposal until the owner has read it.

## Next

- After base-0 the track has no further work package. Changes to the
  environment or to the shared formats go through an ADR.
