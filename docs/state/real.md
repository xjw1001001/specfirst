# Track real

Result: CDISCPILOT01 end to end: ADaM proof, result engines, grids and
viewer, the 30 CSR tables (PLAN.md section 13.3).

## Passed

- real-1 Kit and ADaM proof. Gate: `specfirst gate real-1 --clean` exited 0
  on a clean clone of commit `6e6a2ce` (2026-11-11). Evidence:
  docs/reports/real-1.md and real-1.gate.log. Review:
  docs/reports/real-1.review.md. Decisions: docs/decisions/ADR-001.md.

## Open

- For the owner: item 3 of ADR-001 adds `gold/reference/`, `gold/claims/`,
  `gold/resolved/` and `gold/build.json` to the kit layout of PLAN.md
  section 8 (review finding F12).
- The 706 `cites` edges imported from Pilot 7's claims are candidates: no
  quote is checked against its document and no one has approved one.
  real-3 completes the graph to the documents. One edge stands for all
  citations of one span by one column (913 citations, 706 edges), so one
  `quote_verified` per edge will not be enough there.
- The v0 edge schema cannot tell a value dependency from a key, filter or
  ordering dependency; coverage.json has it per column (`value`). If the
  viewer of real-3 needs it per edge, it is a schema change (an ADR the
  owner approves).
- Review of real-1, second pass, findings N1 to N7: none blocked, none is
  fixed yet. Fix them with the first commit of real-2 and run the gate of
  real-1 again with it. Details in docs/reports/real-1.review.md.
  - N1: let test A4 also empty the constant SDTM columns (a roll does not
    change them), or reword ADR-001 item 6, lesson 16 and the docstring.
  - N2: P1 compares two folders of one checkout; say so in ADR-001 item 4.
  - N3: the place of an edge for a lookup over SELF to an output column,
    and for two rules at the same distance (`graph._trace_column`).
  - N4: `value` must not count a top-level `filter` as part of the rule.
  - N5: the search for ODM files in git sees `.xml` in ASCII or UTF-8 only;
    widen it or narrow the sentence in kits/README.md.
  - N6: two time zones at one instant are not "storage type only"
    (`compare.kind`).
  - N7: two sentences of ADR-001 item 5 (how the plan words the tolerance;
    "every cell").
- P1 is tested with yamaa's Python host only; its R host is not installed.
- The kit manifest is checked by code, not by a schema in
  standard/schemas/ (ADR-001, item 3). gen-2 writes kits too: agree on the
  format with it before a schema is proposed.
- The pilot's protocol is not in the kit.

## Next

- real-2 Result engines. Needs real-1. Decide ADR-002 first: the R engine
  wraps siera, or is our own on cards and cardx.
- Then real-3, real-4 (D1, node N2), real-5 (D2, node N2), in order.

## Handed over by real-1

- `specfirst build cdiscpilot01` writes the 10 ADaM datasets as canonical
  Parquet into build/kits/cdiscpilot01/gold/data/adam/; real-2 reads them
  from there, not from the fetch cache. `specfirst check cdiscpilot01`
  proves they equal the reference.
- `specfirst.machine.canonical` has the writers for JSON, JSONL and
  Parquet; every built file goes through it (P1).
- The graph is in gold/graph/ (nodes.jsonl, edges.jsonl, coverage.json).
  ADaM node IDs are `adam:<DATASET>.<COLUMN>`; real-3 adds the `reads`
  edges from analyses to them.
- A new work package adds its gate to `GATES` in src/specfirst/gates.py and
  its cache-dependent tests under tests/ with the marker `evidence`.
- Reading or importing anything from the fetch cache must leave it
  untouched (lesson 13): the gate verifies the cache again at its end.
- Code taken over from a cached source, even retyped, goes into
  third_party/SOURCES.md with its license (lessons 12 and 14); the test
  A5-adapted of tests/pilot looks for what was not recorded.
- A static check of the graph cannot see a reference the analysis missed.
  tests/pilot A4-unread tests the pilot graph against the engine; a new
  graph layer needs a check of that kind (lesson 16).
