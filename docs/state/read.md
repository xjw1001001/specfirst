# Track read

Result: scorer, harness, reader agent, first scores (PLAN.md section 13.6).

## Passed

- Nothing yet.

## Open

- Waits for real-3a (fixtures) and gen-2a (ADR-005).

## Next

- read-1a first (ADR-005, decisions 1 to 4): reading score and build score
  for the decisions of the slice and one output, the three arms and the
  scores per output. Needs real-3a and gen-2a.
- Then read-2a (needs read-1a and gen-3a) and the report
  docs/reports/slice-ae-summary.md. It is not a delivery.
- Then the rest of read-1 Scorer (needs real-3 for fixtures, then gen-2),
  read-2 (needs gen-2) and read-3 (D3, node N3).

## Handed over by base-0

- The planted-defect pattern of rule R5 is in use already:
  `tests/unit/test_evidence_checks.py` and the invalid examples in
  `standard/schemas/examples/`.
