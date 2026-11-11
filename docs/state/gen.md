# Track gen

Result: generated studies for the parallel-group design PG-FIX (PLAN.md
section 13.5).

## Passed

- Nothing yet.

## Open

- Waits for base-0 and for a draft of std-1.

## Next

- gen-1 SDTM generator for PG-FIX. Needs base-0 and a draft of std-1.
- Then gen-2 (needs std-1 after N1 and real-3) and gen-3.

## Handed over by base-0

- CDISC CORE is not installed yet; gen-1 adds it to the environment through
  `env/requirements.in` or `env/apt-packages.txt` and `make lock`.
