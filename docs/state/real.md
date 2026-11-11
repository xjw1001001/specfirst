# Track real

Result: CDISCPILOT01 end to end: ADaM proof, result engines, grids and
viewer, the 30 CSR tables (PLAN.md section 13.3).

## Passed

- Nothing yet.

## Open

- Waits for base-0.

## Next

- real-1 Kit and ADaM proof. Needs base-0. Decide ADR-001 first: the yamaa
  wheel with our own runner, or a source build at Pilot 7's pin (E19).
- Then real-2, real-3, real-4 (D1, node N2), real-5 (D2, node N2), in order.

## Handed over by base-0

- `specfirst fetch` puts Pilot 7, Pilot 6, the ARS repository and the other
  pinned sources in the cache; `tests/evidence_cases.py` shows how the
  spikes read them.
- The run of the pilot's yamaa project writes into the data folder: work on
  a copy, as the E1 test does.
