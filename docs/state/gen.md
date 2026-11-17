# Track gen

Result: generated studies for the parallel-group design PG-FIX (PLAN.md
section 13.5).

## Passed

- Nothing yet. gen-1a is written and committed on `track/gen`; its gate has
  not passed (see Open).

## Open

- gen-1a (ADR-005, decision 1) is not done. Written: CDISC CORE in the
  environment (ADR-006), the design model and the sampler for PG-FIX, the
  subject process, SDTM for eleven domains, the probe recipes of the slice,
  the gate `gen-1a`. Missing: a run of the gate to its end, the clean-clone
  gate, the review, the report.
- The catalog is `specfirst-m1 draft-1` in this branch. Every generated
  file names the catalog it was made for; a design sampled for another
  version is refused (`specfirst.gen.study.generate`).

## Next

- gen-1a: `flock /run/lock/specfirst-heavy.lock specfirst gate gen-1a`,
  then `scripts/clean_clone_gate.sh gen-1a`, the review and the report.
- Then gen-2a (needs gen-1a, std-1 after N1 and real-3a) and gen-3a.
- Then the rest of gen-1 SDTM generator for PG-FIX, gen-2 (needs std-1
  after N1 and real-3) and gen-3, each with the gate PLAN.md gives it.

## Handed over by base-0

- CDISC CORE: installed by gen-1a through `env/` (docs/decisions/ADR-006.md).
