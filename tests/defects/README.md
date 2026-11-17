# Planted defects

The defects a checker or scorer must detect before it is trusted (PLAN.md
section 9.5, rule R5). A defect is planted as the real case, not a simpler
cousin (lessons 9 and 16): in the real inputs, run by the real engines,
judged by the function the gate calls.

`test_defects.py` (real-2) plants in the ARS example and the binding of the
pilot kit, and runs on the ADaM datasets the kit builds:

| Test | Defect | Must be seen by |
| --- | --- | --- |
| D1-arms | the low dose and the high dose group exchange their conditions (E3); and the values of the two arms are exchanged in one analysis only, for five analyses | P2 for results; the differences are attributed to the treatment grouping. In one analysis: P2 fails and the engines disagree; in the analysis of ethnicity, where the reference has the same exchange, the kit's 8 entries become stale |
| D2-set | the analysis set reads another population flag | P2 for results, in the analyses of that set |
| D3-quantile | the quantile definition is R's default (E4) | P2 for results, in quartiles only; the options hash marks the rows |
| D4-subset | an analysis loses its data subset | P2 for results, in that analysis only |
| D5-engines | each of the four, in the R engine's input alone | rule R11: the engines disagree |
| D6-proofs | a proof that proves nothing, in the kit's exceptions file: the cases A3 and A8 to A11 of the review of real-2, each on the entry it was found on, and the proof the median of height had until real-3a | the check of the proofs: each fails for the reason the test names |

What the pilot data cannot show is printed, not counted as caught: the
safety set and the intent-to-treat set hold the same subjects, and for 3
of the 18 analyses with a data subset, dropping it changes nothing the
reference lists.

The tests need the fetch cache, the engine and R; they carry the marker
`evidence`. read-1 adds the defects of the scorer.
