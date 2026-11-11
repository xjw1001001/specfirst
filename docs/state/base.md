# Track base

Result: repository, environment, pins, shared formats (PLAN.md section 13.2).

## Passed

- base-0 Bootstrap. Gate: `specfirst gate base-0 --clean` exited 0 on a
  clean clone of commit `1b509d2` (2026-11-11). Evidence:
  docs/reports/base-0.md and base-0.gate.log. Review:
  docs/reports/base-0.review.md.

## Open

- ADR-000 is a proposal until the owner has read it. Four schema points in
  its item 7 need the owner's word, at N1 at the latest.
- No container definition in env/ yet (section 12; needed in M2).
- The Ubuntu distribution has no Linux user; the environment is root's.
- `evidence/csr_hylaw_spike.py` holds typed-in CSR values: decide before
  the repository becomes public (report, finding 11).

## Next

- The track has no further work package. Changes to the environment or to
  the shared formats go through an ADR.
- Other tracks start from `main`: `scripts/worktree.sh <track>` with
  Windows git, then `make install` in the new worktree under WSL.
