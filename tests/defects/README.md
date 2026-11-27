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
| D6-proofs | a proof that proves nothing, in the kit's exceptions file: the cases A3 and A8 to A11 of the review of real-2, each on the entry it was found on, and the proof the median of height had until real-3a; and a defect of ours (one analysis reads its population from EFFFL), whose quartiles and medians are tried as errors of the reference (the review of real-3a, F5) | the check of the proofs: each fails for the reason the test names; no quartile or median of the wrong population is proven, because the n, the minimum and the maximum of its cell are not reproduced |
| D7-display | real-3a, on the grid of the adverse event summary: in the layout, another pattern, a row or the header left out, rows in another order, the percent in place of the count, and (the review of real-3a, F1 and F3) the percent before the count, another text between the two, the header as N={N}, the count under the mask XXX, another row label, the rows without the line above them, the percent of another row; in the results, the arms exchanged in one analysis, a percent of another denominator; in the grid file, a text or the ARD rows of a cell changed, texts exchanged, cells in another order | the comparison of every cell text with the example's formatted values, the check of the grid against its layout and the ARD, the mock shell against the example's table shell (`specfirst.machine.shells`), and the layout's own refusal |
| D8-trace | real-3a, on the graph of the same grid: a `shows` edge and two `reads` edges left out (one to ADSL.SAFFL, which the analysis of the denominator reads too), where the files still agree with each other; a result node, the `computes` edges, the `reads` edges, the one `reads` edge to ADSL.SAFFL, the `computes` edge of one percent to the analysis of its denominator left out of the files, and an analysis that coverage.json records with one column (the review of real-3a, F4) | the `shows` edges against the grid builder (a changed result must change exactly the cells that show it), the `reads` edges against the engine (a column without an edge, emptied or rolled, must change no result of the analysis; the results computed from one analysis alone, against its own edges alone), and the walk from every cell to SDTM columns, which holds every `computes` and `reads` edge against the ARS file |
| D9-efficacy | real-5a, on the three efficacy tables against the CSR: in our own reporting event, run by both engines, the ANCOVA without the baseline covariate, the dose as the rank of its group, the site in place of the pooled site group, the comparisons with asymptotic degrees of freedom, the comparison with placebo made against the low dose, the intent-to-treat set for the efficacy set, week 16 for week 24; in the reference and the exceptions, a cell of the CSR changed, the confidence limits shown as the CSR prints them (the 9 exceptions stale), an exception whose other pattern proves nothing, one left out, one of another class, one that names no decision | the comparison of every cell with the CSR table parsed from its page, and the proof of each classified difference (`build.csr_against`) |
| D10-trace-model | real-5a, on the graph: the analyses that fit a model run by the R engine with the columns they have no `reads` edge to emptied and rolled (no result may change), and with the columns they read emptied (a result must change); planted, the `reads` edges to ADQSADAS.BASE, the covariate, left out | the `reads` edges against the R engine |
| D14-vital-signs | real-3, on the two grids of the vital signs: in their layouts, the observed value and the change exchanged between their columns, the change shown at baseline, the minimum and the maximum under XX.X, the median above the mean, Week 2 left out; (review of real-3, F2) Q1 and Q3 exchanged in their cell, the minimum and the maximum exchanged, the mean in the row of the median, the n and the minimum exchanged between rows, the changes above the observed values, two parameters exchanged by labels; in the exceptions, the proofs of the four medians at a half; the rounding rule half_even | the comparison of every cell text with the example's formatted values (with the kit's differences of display), the mock shell against the example's table shell (specfirst.machine.shells, with the place of each cell on its line), the layout's own refusals (the label of a statistic row against the labels of the operations it shows), and the counts of the gate (no result without a formatted value). The heading of the change rows of the vertical layout stands against a placeholder of the shell: printed, not counted |

What the CSR cannot show is printed, not counted: the weights of the LS
means change the LS means and no printed cell (the tables print differences
of LS means only).

What the example cannot show for the grid is printed too: none of the 51
results of the adverse event summary lies on a half, so the rounding rule
cannot be told apart on it. Its formatted values are of results, not of
cells; the order of the parts of a cell and the text between them are held
against the table shell the kit pins (until real-3 they were not held, and
D7 printed them as not separable).

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
