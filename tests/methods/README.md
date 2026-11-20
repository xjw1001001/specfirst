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
| `*.json` | the vectors: 150 cases for 12 entries, 30 of them for the three model-based entries (real-5a) |
| `oracle.py` | the expected values computed again, with fractions and closed forms; used by no engine |
| `oracle_models.py` | the same for the model-based entries: least squares in exact fractions, LS means and contrasts from their coefficient vectors, the t distribution from its closed form (ADR-015); shares nothing with lm, emmeans or car |
| `oracle_mmrm.py` | the same for the mixed model for repeated measures (amendment of real-5b to ADR-015): the restricted likelihood maximized by Fisher scoring in numpy, in the entries of the covariance matrix, which it is linear in; the adjusted covariance of Kenward and Roger and the degrees of freedom written out from their formulas; shares no code with mmrm, TMB or emmeans. No closed form exists: it agrees with the R implementation to about 1e-8 |
| `test_methods.py` | the Python implementations, the R implementations and the oracle against the vectors; both Fisher sums against R's own `fisher.test` on tables larger than 2 x 2 (E27), and against exact fractions on the two tables where `fisher.test` is looser than statement 5; the limit of statement 6 in R |

A model-based entry gives one value per group: its expected values are a
mapping per operation, from group to value. Its vectors are run in R only
(`r-vectors`, `model-vectors`); `model-vectors` also asks that the vectors
give every option every value it has, and runs the vectors again with one
option of each entry fixed at one value in the inputs (what an
implementation that ignored the option would compute), which the vectors
must see. That defect is planted in the inputs, not in the R code.

Numbers must agree within a relative 1e-12, those of `model.mmrm.*` within
1e-6: two optimizations meet there, not two computations of one closed form.
The `test.cmh` vectors are computed in fractions (the statistic) and its
finite series (the tail). The tests that need R are
skipped where R is not installed, except in a gate. Keep a value of a
vector away from 0 when it is the difference of two larger numbers (a
confidence limit near 0): its last digits are rounding, not arithmetic.

To add a case: write its input, take the expected value from `oracle.py`
or from a source you name in a `source` key, and run
`python -m pytest tests/methods -s`.
