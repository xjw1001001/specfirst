# Track gen

Result: generated studies for the parallel-group design PG-FIX (PLAN.md
section 13.5).

## Passed

- Nothing yet.

## Open

- Nothing blocks gen-1a: base-0 has passed and std-1 is delivered (catalog
  `draft-1`; node N1 is open).

## Next

- gen-1a first (ADR-005, decision 1): design model and sampler for PG-FIX,
  subject process, SDTM writers for DM, DS, EX and AE and the datasets CORE
  requires with them, probe recipes for the decisions of the slice. Its
  gate is the gate of gen-1 for these datasets and decisions.
- Then gen-2a (needs gen-1a, std-1 after N1 and real-3a) and gen-3a.
- Then the rest of gen-1 SDTM generator for PG-FIX, gen-2 (needs std-1
  after N1 and real-3) and gen-3, each with the gate PLAN.md gives it.

## Handed over by base-0

- CDISC CORE is not installed yet; gen-1 adds it to the environment through
  `env/requirements.in` or `env/apt-packages.txt` and `make lock`.
