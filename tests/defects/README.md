# Planted defects

The defects a checker or scorer must detect before it is trusted (PLAN.md
section 9.5, rule R5). A defect is planted as the real case, not a simpler
cousin (lessons 9 and 16): in the real inputs, run by the real engines,
judged by the function the gate calls.

`test_defects.py` (real-2, real-3a) plants in the ARS example, the binding
and the layout of the pilot kit, and runs on the ADaM datasets the kit
builds:

| Test | Defect | Must be seen by |
| --- | --- | --- |
| D1-arms | the low dose and the high dose group exchange their conditions (E3); and the values of the two arms are exchanged in one analysis only, for five analyses | P2 for results; the differences are attributed to the treatment grouping. In one analysis: P2 fails and the engines disagree; in the analysis of ethnicity, where the reference has the same exchange, the kit's 8 entries become stale |
| D2-set | the analysis set reads another population flag | P2 for results, in the analyses of that set |
| D3-quantile | the quantile definition is R's default (E4) | P2 for results, in quartiles only; the options hash marks the rows |
| D4-subset | an analysis loses its data subset | P2 for results, in that analysis only |
| D5-engines | each of the four, in the R engine's input alone | rule R11: the engines disagree |
| D6-proofs | a proof that proves nothing, in the kit's exceptions file: the cases A3 and A8 to A11 of the review of real-2, each on the entry it was found on, and the proof the median of height had until real-3a | the check of the proofs: each fails for the reason the test names |

| D7-display | real-3a, on the grid of the adverse event summary: in the layout, another pattern, a row or the header left out, rows in another order, the percent in place of the count; in the results, the arms exchanged in one analysis, a percent of another denominator; in the grid file, a text or the ARD rows of a cell changed, texts exchanged, cells in another order | the comparison of every cell text with the example's formatted values, and the check of the grid against its layout and the ARD |
| D8-trace | real-3a, on the graph of the same grid: a `shows` edge and a `reads` edge left out, where the files still agree with each other; a result node, the `computes` edges and the `reads` edges left out of the files | the `shows` edges against the grid builder (a changed result must change exactly the cells that show it), the `reads` edges against the engine (a column without an edge, emptied or rolled, must change no result of the analysis), and the walk from every cell to SDTM columns |

| D9-efficacy | real-5a, on the three efficacy tables against the CSR: in our own reporting event, run by both engines, the ANCOVA without the baseline covariate, the dose as the rank of its group, the site in place of the pooled site group, the comparisons with asymptotic degrees of freedom, the comparison with placebo made against the low dose, the intent-to-treat set for the efficacy set, week 16 for week 24; in the reference and the exceptions, a cell of the CSR changed, the confidence limits shown as the CSR prints them (the 9 exceptions stale), an exception whose other pattern proves nothing, one left out, one of another class, one that names no decision | the comparison of every cell with the CSR table parsed from its page, and the proof of each classified difference (`build.csr_against`) |
| D10-trace-model | real-5a, on the graph: the analyses that fit a model run by the R engine with the columns they have no `reads` edge to emptied and rolled (no result may change), and with the columns they read emptied (a result must change); planted, the `reads` edges to ADQSADAS.BASE, the covariate, left out | the `reads` edges against the R engine |

What the CSR cannot show is printed, not counted: the weights of the LS
means change the LS means and no printed cell (the tables print differences
of LS means only).

What the example cannot show for the grid is printed too: it formats
results, not cells, so the order of the parts of a cell is the layout's
alone; and none of the 51 results of the adverse event summary lies on a
half, so the rounding rule cannot be told apart on it.

What the pilot data cannot show is printed, not counted as caught: the
safety set and the intent-to-treat set hold the same subjects, and for 3
of the 18 analyses with a data subset, dropping it changes nothing the
reference lists.

The tests need the fetch cache, the engine and R; they carry the marker
`evidence`.

The defects of the scorer (read-1a, the slice "adverse event summary first")
are planted by `specfirst.score.defects`, S1 to S12: of the twelve of
section 9.5, two do not apply to a table of counts and percents (a quantile,
a baseline), three are planted as the nearest thing the table has (a percent
rounded twice, the order of the treatment columns, the list of related
causality values), and two are planted in two ways. Each is planted in a
candidate (a decision, a step of its build, a citation) and judged by
`specfirst.score.scorer.run`, the function that scores any candidate.
`specfirst score defects` runs them on the hand-made study HAND01;
`tests/unit/test_score_hand.py` holds each one against the cells worked out
by hand. They need no fetch cache and no R.
`specfirst score defects --kit DIR` runs them on a generated kit, and the
gate read-1a on the ten kits of the gate of gen-2a, with every pair of the
identifiability matrix of each kit as one more planted decision
(`specfirst.score.kit`, docs/decisions/ADR-008.md).
