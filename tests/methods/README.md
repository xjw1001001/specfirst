# Method vectors

Inputs with expected outputs for each entry of the method registry (PLAN.md
section 7.3). One file per entry, named by the entry's `vectors` key.

```json
{"method": "<registry id>",
 "cases": [{"name": "...", "statements": [3, 4], "input": {...},
            "options": {...}, "expected": {"<operation>": <value or null>}}]}
```

`statements` names the statements of the entry's semantics a case
exercises. Every statement has a case, except the two of
`percent.subjects` that say which results an analysis references; the
engine tests have those.

| File | Content |
| --- | --- |
| `*.json` | the vectors: 81 cases for 7 entries |
| `oracle.py` | the expected values computed again, with fractions and closed forms; used by no engine |
| `test_methods.py` | the Python implementations, the R implementations and the oracle against the vectors; both Fisher sums against R's own `fisher.test` on tables larger than 2 x 2 (E27), and against exact fractions on the two tables where `fisher.test` is looser than statement 5; the limit of statement 6 in R |

Numbers must agree within a relative 1e-12. The tests that need R are
skipped where R is not installed, except in a gate.

To add a case: write its input, take the expected value from `oracle.py`
or from a source you name in a `source` key, and run
`python -m pytest tests/methods -s`.
