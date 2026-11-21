# catalog-2b: the content of catalog@2 and open-default@2 (ADR-020, part 2 of 3)

Work package catalog@2, track std, part catalog-2b: decision 7 of ADR-020 as
the owner answered it on 2026-11-21 (A to questions 1, 2, 3 and 5). Part
catalog-2a (the structure) merged first; part catalog-2c (the slice moved to
version 2) follows. The slice stays on (`catalog@1`, `open-default@1`) in
this part: generated kits, the reader's tasks and the kept run are unchanged.

## What changed, by issue

| Issue | catalog@2 | open-default@2 | Backlog |
| --- | --- | --- | --- |
| #1 | `tfl.percent.format`: the slot `decimals` (0 to 2) in both alternatives; a probe varies it | default `one_decimal_always`, 1 decimal, for the three families (the ARS example) | i01.zero-shown, i01.decimals-slot done; i01.below-one waits |
| #2 | the FDA wording in the reading note, marked ambiguous; FDA and admiral citations | default by design: randomized and dosed when `design.randomized`, dosed otherwise | i02.* done |
| #3 | `ae.teae.end/end_of_study` removed with its two probes | default `last_dose_plus_days`, 30 days (admiral's template) | i03.* done |
| #4 | the three edge rules of emergence as fixed rules with anchors; the doubled "For every alternative:" gone | the fixed rules anchored in STANDARD.md | i04.fixed-rules done |
| #5 | `ae.teae.start/by_time_when_collected`, its fragment, phrasing and probe `ae_timed_before_timed_first_dose` | | i05.date-time done |
| #6 | the definitions say where a value timed after the dose on the first dose day goes; `demo.baseline.record` states that it agrees with ADVS | default `last_on_or_before_first_dose_date` for ADVS (admiral); post-baseline time-aware in the ADVS parent | i06.* done |
| #7 | the source of `lt65_ge65` (the ARS grouping) | default `lt65_ge65` | i07.age-default done; i07.fda-bands waits |
| #8 | the FDA citation "pooled active arms" removed | a total column in the demographics table only | i08.* done |
| #9 | `soc_alpha_pt_descending_in_column` replaces `descending_frequency_highest_dose`; citations fixed; "alphabetical" defined; probes for the new pairs | the layout reads the column | i09.* done |
| #10 | the randomized subject as a fixed rule, from the disposition record RANDOMIZED first; mITT named in the definition | RANDFL by that rule (a lookup keyed by STUDYID for the study-level fallback), RANDDT | i10.* done |
| #11 | | default `last_record` (admiral) | i11.last-record done |
| #12 | BMIBL not rounded in ADSL; the units stated | | i12.bmi-unrounded done |
| #13 | rows SERIOUS_RELATED, FATAL_RELATED, DOSE_MODIFIED; `standard_rows` in the order of the ARS example with serious related; "fatal" defined | their data subsets | i13.* done; i13.severity-rows waits |
| #14 | the FDA guide as Version 2.0 (April 2025); five citations with section, table and page | | i14.fda-guide done |
| #15 | | STANDARD.md anchored by entry ID, with status, scope, order of precedence, a source line per statement, terms, conventions, conformance rules and a change log | i15.citable-document done |
| #17 | the status words with no status for a screen failure (fixed rule); `bds.eot.record` states AVISITN 9999 and carries the unit | AEBODSYS; PARAM with the unit, AVALU; first occurrence by date then sequence; the conformance rules in STANDARD.md | i17.conformance, i17.screen-failure, i17.eot-record done; i17.positions-refused, i17.dtype-null, i17.dose-order wait |
| #18 | boundary words in the statements of `ae.teae.end`, `bds.baseline.rule`, `demo.age.groups`; fixed rules; the list of terms | the terms printed once | i18.* done |
| #20 | (2a: the entry schema v1, the `$fn` list) | the sources of every alternative printed | i20.alternative-sources done |
| #21 | `demo.race.pooling/fixed_groups` replaces `pooled_below_count`; the unscheduled visit as a fixed rule with the VISIT fallback; the kept answer of N1 question 1 in the reading note of `tfl.population` | `_SCHED` by the fixed rule | i21.* done |
| #22 | `tfl.quantile.definition` for the demographics table only; its probe needs quartiles; "(R type 2)" in the statement | the vital signs templates fix `sas5` | i22.quantiles done |
| #23 | items 9 to 11: worsening as a fixed rule; ICH M11 words in the reading notes; the meaning of halfway | | i23.reading-words done; the rest waits |
| #24 | `trt.end.source/last_ex_record_end` and its probe | | i24.last-end-any-record done |
| #33 | | the label and time-of-day rules in STANDARD.md; the check of carried labels; `specfirst.compile.attributes` | i33.* done |

## Evidence

(Filled in from the commands and gate logs below.)
