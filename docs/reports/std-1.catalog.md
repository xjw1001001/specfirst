# Decision catalog specfirst-m1 draft-1: overview

Rendered by `specfirst catalog --overview` from `standard/catalog/` and the house standard open-default@1. 43 entries, 62 questions when an entry is counted once per unit, 96 alternatives, 4 questions without a default.

In a statement, `{name}` is a typed slot and `{output}` names the table: tfl-demographics is "the demographics table"; tfl-ae-summary is "the adverse event summary table"; tfl-ae-soc-pt is "the adverse event table by system organ class and preferred term"; tfl-vitals-by-visit is "the vital signs table by visit".

## mod-treatment: Treatment and exposure

### `trt.planned.source`: Where does planned treatment come from?

Applies when: `design.has_exposure`. Default: `dm_arm`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `dm_arm` | Planned treatment is the planned arm of the subject (DM.ARM). |  |
| `dm_armcd_map` | Planned treatment is decoded from the planned arm code (DM.ARMCD) as follows: {map}. | A code that the list does not name gives no planned treatment. |

- Slot `map` of `dm_armcd_map`: type `records`; each written as `{code} means {label}`.
- Sources: CDISC ADaM Implementation Guide (ADSL treatment variables, TRTxxP); CDISC SDTM Implementation Guide (DM domain, ARM and ARMCD); R Consortium Submissions Pilot 7, yamaa specs and reviews of CDISCPILOT01 (TRT01P of the pilot ADSL).
- Probes: arm_label_differs_from_decode.

### `trt.actual.source`: Where does actual treatment come from?

Applies when: `design.has_exposure`. Default: `dm_actarm`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `dm_actarm` | Actual treatment is the actual arm of the subject (DM.ACTARM). |  |
| `first_ex_treatment` | Actual treatment is the treatment named on the first exposure record of the subject (EX.EXTRT). | The first exposure record is the one with the earliest start date; the lowest EXSEQ breaks a tie. |
| `same_as_planned` | Actual treatment is the same as planned treatment. |  |

- Sources: CDISC ADaM Implementation Guide (ADSL treatment variables, TRTxxA); CDISC SDTM Implementation Guide (DM domain, ACTARM; EX domain, EXTRT); R Consortium Submissions Pilot 7, yamaa specs and reviews of CDISCPILOT01 (TRT01A of the pilot ADSL: actual set equal to planned).
- Probes: actual_arm_differs_from_planned, first_exposure_other_treatment.

### `trt.start.source`: What is the treatment start date?

Applies when: `design.has_exposure`. Default: `first_ex_with_dose`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `first_ex_with_dose` | The treatment start date is the earliest start date of an exposure record with a dose. | An exposure record has a dose when EXDOSE is above zero, or when EXDOSE is zero and EXTRT contains PLACEBO. |
| `first_ex_record` | The treatment start date is the earliest start date of any exposure record. |  |
| `dm_rfxstdtc` | The treatment start date is the date of first exposure in the demographics domain (DM.RFXSTDTC). |  |

For every alternative: Which partial dates take part is decision trt.date.imputation.

- Sources: CDISC ADaM Implementation Guide (ADSL treatment timing variables, TRTSDT); admiral (pharmaverse), function reference and source (ADSL vignette, TRTSDTM from EX records with EXDOSE > 0 or a placebo record); CDISC SDTM Implementation Guide (DM domain, RFXSTDTC); R Consortium Submissions Pilot 7, yamaa specs and reviews of CDISCPILOT01 (TRTSDT of the pilot program template).
- Probes: zero_dose_record_before_first_dose, rfxstdtc_differs_from_exposure.

### `trt.end.source`: What is the treatment end date?

Applies when: `design.has_exposure`. Default: `last_ex_end_date`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `last_ex_end_date` | The treatment end date is the latest end date of an exposure record with a dose. |  |
| `last_ex_start_date` | The treatment end date is the latest start date of an exposure record with a dose. |  |
| `ds_date_when_ex_missing` | The treatment end date is the latest end date of an exposure record with a dose, or the end-of-study disposition date when no such record has an end date. | The disposition date is the start date of the end-of-study record (decision disp.status.record). It is taken only for a subject with a treatment start. |

For every alternative: An exposure record has a dose when EXDOSE is above zero, or when EXDOSE is zero and EXTRT contains PLACEBO. Which partial dates take part is decision trt.date.imputation.

- Sources: CDISC ADaM Implementation Guide (ADSL treatment timing variables, TRTEDT); admiral (pharmaverse), function reference and source (ADSL vignette, TRTEDTM from the last EX record with EXDOSE > 0 or a placebo record); R Consortium Submissions Pilot 7, yamaa specs and reviews of CDISCPILOT01 (TRTEDT of the pilot ADSL: disposition date when the date of final dose is missing).
- Probes: last_exposure_record_spans_days, no_exposure_end_date.

### `trt.date.imputation`: How are partial exposure dates completed?

Applies when: `design.has_exposure`. Default: `not_completed`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `not_completed` | A partial exposure date is not completed and is left out of the treatment dates. | The treatment start and end dates are taken from the exposure dates that have a year, a month and a day. A date with a missing part in the middle (a year and a day without the month) is partial. |
| `first_day_of_month` | A partial exposure date with a known month is completed with the first day of that month. | A date with an unknown month is left out of the treatment dates. |

- Sources: admiral (pharmaverse), function reference and source (derive_vars_dt(), highest_imputation (default n: no imputation) and date_imputation (first)); yamaa, language documentation, rules and benchmarks (the impute verb: a source with no day gives missing unless a day is supplied).
- Probes: partial_exposure_date, partial_exposure_date_not_earliest.

### `date.studyday.origin`: Which date is study day 1?

Applies when: `design.always`. Default: `treatment_start`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `treatment_start` | Study day 1 is the treatment start date. |  |
| `dm_rfstdtc` | Study day 1 is the reference start date of the subject (DM.RFSTDTC). |  |

For every alternative: There is no study day 0. The day before study day 1 is day -1.

- Sources: CDISC ADaM Implementation Guide (BDS timing variables, ADY: relative to a reference date such as TRTSDT); CDISC SDTM Implementation Guide (study day variables (--DY): relative to RFSTDTC); yamaa, language documentation, rules and benchmarks (the study_day verb).
- Probes: reference_start_before_first_dose.

## mod-populations: Analysis populations and disposition

### `pop.randomized.rule`: Who is in the randomized set?

Applies when: `design.randomized`. Default: `all_randomized`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `all_randomized` | The randomized set holds every randomized subject. |  |
| `randomized_with_postbaseline` | The randomized set holds every randomized subject with at least one post-baseline value of the vital sign {test}. | A post-baseline value is a non-missing result dated after the treatment start date. |

For every alternative: A subject is randomized when the planned arm code (DM.ARMCD) is present and is neither SCRNFAIL nor NOTASSGN.

- Slot `test` of `randomized_with_postbaseline`: type `name`.
- Sources: ICH E9: Statistical Principles for Clinical Trials (section 5.2.1, full analysis set: all randomised subjects; lack of any data post randomisation as a possible exclusion); CDISC ADaM Implementation Guide (ADSL population flags, ITTFL and RANDFL); R Consortium Submissions Pilot 7, yamaa specs and reviews of CDISCPILOT01 (ITTFL of the pilot ADSL).
- Probes: randomized_without_postbaseline_value.

### `pop.safety.rule`: Who is in the safety set?

Applies when: `design.has_exposure`. Default: `at_least_one_dose`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `at_least_one_dose` | The safety set holds every subject who received at least one dose of study treatment. |  |
| `randomized_and_dosed` | The safety set holds every randomized subject who received at least one dose of study treatment. |  |

For every alternative: A subject received a dose when the treatment start date is present. A subject is randomized when the planned arm code (DM.ARMCD) is present and is neither SCRNFAIL nor NOTASSGN; the rule of the randomized set (pop.randomized.rule) does not enter.

- Sources: ICH E9: Statistical Principles for Clinical Trials (section 6.3: for safety and tolerability, the subjects who received at least one dose); CDISC ADaM Implementation Guide (ADSL population flags, SAFFL); R Consortium Submissions Pilot 7, yamaa specs and reviews of CDISCPILOT01 (SAFFL of the pilot ADSL: randomized and dosed).
- Probes: dosed_but_not_randomized, randomized_never_dosed.

### `pop.safety.grouping`: Which treatment groups the safety analyses?

Applies when: `design.has_exposure and design.multiple_arms`. Default: `actual`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `actual` | Safety analyses group subjects by actual treatment. |  |
| `planned` | Safety analyses group subjects by planned treatment. |  |

For every alternative: The decision holds for every output whose analysis set is the safety set. Outputs on another analysis set group subjects by planned treatment.

- Sources: CDISC Analysis Results Standard v1, model and examples (the treatment grouping of the safety displays); FDA Standard Safety Tables and Figures: Integrated Guide (general conventions: safety tables by actual treatment arm).
- Probes: actual_arm_differs_from_planned.

### `pop.efficacy.rule`: Who is efficacy-evaluable?

Applies when: `design.has_efficacy_set`. Default: none: the documents state it, or a person is asked.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `baseline_and_postbaseline` | The efficacy-evaluable set holds every subject of the safety set with a baseline value and at least one post-baseline value of the vital sign {test}. | A baseline value is a non-missing result dated on or before the treatment start date; a post-baseline value is one dated after it. |
| `attended_visit` | The efficacy-evaluable set holds every subject of the safety set who attended the visit {visit}. | A subject attended a visit when the subject visits domain (SV) has a record of it. |

- Slot `test` of `baseline_and_postbaseline`: type `name`.
- Slot `visit` of `attended_visit`: type `text`.
- Sources: ICH E9: Statistical Principles for Clinical Trials (section 5.2.2, per protocol set and criteria such as availability of measurements); R Consortium Submissions Pilot 7, yamaa specs and reviews of CDISCPILOT01 (EFFFL of the pilot ADSL: post-baseline records of the efficacy measures are required (it asks for no baseline value)); R Consortium Submissions Pilot 7, yamaa specs and reviews of CDISCPILOT01 (COMP24FL of the pilot ADSL: a population defined by an attended visit).
- Probes: postbaseline_value_but_visit_missed, baseline_value_of_other_test_only.

### `disp.status.record`: Which record gives the end-of-study status?

Applies when: `design.always`. Default: `disposition_event`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `disposition_event` | The end-of-study record is the disposition event record of the subject. | The DS record with DSCAT equal to DISPOSITION EVENT. Of several such records the last by DSSEQ is taken. |
| `disposition_event_by_subcategory` | The end-of-study record is the disposition event record of the subject with the subcategory {subcategory}. | The DS record with DSCAT equal to DISPOSITION EVENT and DSSCAT equal to the named subcategory. Of several such records the last by DSSEQ is taken. |

For every alternative: The record gives the end-of-study date (its DSSTDTC) and status: COMPLETED when DSDECOD is COMPLETED, DISCONTINUED for any other term, ONGOING when the subject has no such record.

- Slot `subcategory` of `disposition_event_by_subcategory`: type `text`.
- Sources: CDISC SDTM Implementation Guide (DS domain, DSCAT (DISPOSITION EVENT) and DSSCAT); CDISC ADaM Implementation Guide (ADSL trial experience variables, EOSSTT, EOSDT and DCSREAS); R Consortium Submissions Pilot 7, yamaa specs and reviews of CDISCPILOT01 (DCDECOD of the pilot ADSL).
- Probes: two_disposition_events.

## mod-demographics: Demographics and baseline characteristics

### `demo.age.groups`: Which age groups are used?

Applies when: `design.always`. Default: `lt65_65to80_gt80`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `lt65_65to80_gt80` | Age groups are below 65, 65 to 80, and above 80 years. | The groups are labelled <65, 65-80 and >80. An age of exactly 80 is in 65-80. |
| `lt65_ge65` | Age groups are below 65 years, and 65 years and above. | The groups are labelled <65 and >=65. |
| `stated_cuts` | Age groups start at the ages {cuts} years, with one more group below the first of them. | For the cuts 18 and 65 the groups are labelled <18, 18-<65 and >=65. An age equal to a cut is in the group that starts there. |

- Slot `cuts` of `stated_cuts`: type `list[int]`.
- Sources: CDISC ADaM Implementation Guide (ADSL subject-level grouping variables, AGEGRy); R Consortium Submissions Pilot 7, yamaa specs and reviews of CDISCPILOT01 (AGEGR1N of the pilot ADSL: <65, 65-80, >80); yamaa, language documentation, rules and benchmarks (the cut verb: left-closed intervals from ascending breaks).
- Probes: age_at_cut_points.

### `demo.race.pooling`: Are small race categories pooled?

Applies when: `design.always`. Default: `not_pooled`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `not_pooled` | Race categories are shown as collected and are not pooled. |  |
| `pooled_below_count` | A race category with fewer than {count} subjects is pooled into the category OTHER. | The subjects are counted over all subjects of the subject-level dataset, whatever their arm. |

- Slot `count` of `pooled_below_count`: type `int`.
- Sources: CDISC ADaM Implementation Guide (ADSL subject-level grouping variables, RACEGRy (pooled race group); the rule of pooling is the sponsor's).
- Probes: race_category_at_pooling_count.

### `demo.baseline.record`: Which record gives baseline weight and height?

Applies when: `design.collects_vital_signs`. Default: `last_on_or_before_first_dose`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `last_on_or_before_first_dose` | Baseline weight and height are the last non-missing values on or before the treatment start date. | The last value is the latest by the collected date and time; of the values of one day, a value without a collected time comes before those with a time, and the highest VSSEQ breaks a remaining tie. A subject without a treatment start date has no baseline weight and height. |
| `at_visit` | Baseline weight and height are the non-missing values at the visit {visit}. | Of several values at the visit the highest VSSEQ is taken. |

- Slot `visit` of `at_visit`: type `text`.
- Sources: R Consortium Submissions Pilot 7, yamaa specs and reviews of CDISCPILOT01 (HEIGHTBL of the pilot ADSL: the value of a named visit); CDISC ADaM Implementation Guide (ADSL baseline characteristics; BDS baseline record (ABLFL)).
- Probes: weight_at_screening_and_day_1.

### `demo.bmi.rule`: How is baseline body mass index obtained?

Applies when: `design.collects_vital_signs`. Default: `derived`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `derived` | Baseline body mass index is derived from baseline weight and height and rounded to one decimal. | Weight in kg divided by the square of height in m; rounding is half away from zero. |
| `as_collected` | Baseline body mass index is the collected body mass index, selected by the rule for baseline weight and height. | The collected value is the vital sign with VSTESTCD equal to BMI. |

- Sources: R Consortium Submissions Pilot 7, yamaa specs and reviews of CDISCPILOT01 (BMIBL of the pilot ADSL: derived from baseline weight and height); admiral (pharmaverse), function reference and source (compute_bmi(): weight in kg divided by squared height in m).
- Probes: collected_bmi_differs_from_derived.

## mod-ae-emergence: Adverse event emergence

### `ae.start.imputation`: How are partial adverse event start dates completed?

Applies when: `design.collects_adverse_events`. Default: `first_of_month_not_before_first_dose`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `first_of_month_not_before_first_dose` | A partial adverse event start date with a known month is completed with the first day of that month, or with the treatment start date when it falls in that month. | A date with an unknown month is not completed. |
| `first_of_month` | A partial adverse event start date with a known month is completed with the first day of that month. | A date with an unknown month is not completed. |
| `not_completed` | A partial adverse event start date is not completed and gives no analysis start date. |  |

- Sources: admiral (pharmaverse), function reference and source (derive_vars_dt(), date_imputation = first with min_dates: the imputed date is not before the given dates); yamaa, language documentation, rules and benchmarks (the benchmark of partial adverse event start dates: a completed date is not before the treatment start date (the benchmark supplies day 15, not the first day)); CDISC ADaM Implementation Guide (date imputation flag, ASTDTF).
- Probes: partial_ae_start_in_month_of_first_dose, partial_ae_start_before_month_of_first_dose.

### `ae.teae.start`: When does treatment emergence begin?

Applies when: `design.collects_adverse_events and design.has_exposure`. Default: `on_or_after_first_dose_date`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `on_or_after_first_dose_date` | An adverse event is treatment-emergent when it starts on or after the treatment start date. | Dates are compared; times are ignored. |
| `at_or_after_first_dose_time` | An adverse event is treatment-emergent when it starts at or after the date and time of the first dose. | A start or a first dose collected without a time counts from 00:00 of its day. |

For every alternative: For every alternative: an event of a subject without a treatment start date is not treatment-emergent; an event that ends before the treatment start date is not treatment-emergent; an event without an analysis start date is treatment-emergent.

- Sources: admiral (pharmaverse), function reference and source (derive_var_trtemfl(): start on or after treatment start; a missing start date is flagged); R Consortium Submissions Pilot 7, yamaa specs and reviews of CDISCPILOT01 (TRTEMFL of the pilot program template); yamaa, language documentation, rules and benchmarks (the benchmark of treatment emergence timing: comparison of date and time).
- Probes: ae_on_first_dose_date_without_time.

### `ae.teae.end`: When does treatment emergence end?

Applies when: `design.collects_adverse_events and design.has_exposure`. Default: `no_end`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `no_end` | Treatment emergence has no end date. |  |
| `last_dose_plus_days` | Treatment emergence ends {days} days after the treatment end date. | An event that starts on the last day of the window is still treatment-emergent. A subject without a treatment end date has no end. |
| `end_of_study` | Treatment emergence ends at the end-of-study date. | An event that starts on the end-of-study date is still treatment-emergent. A subject without an end-of-study date has no end. |

- Slot `days` of `last_dose_plus_days`: type `int`.
- Sources: admiral (pharmaverse), function reference and source (derive_var_trtemfl(), end_window: events starting more than the given days after end of treatment are not flagged); yamaa, language documentation, rules and benchmarks (the benchmark of treatment emergence timing: a window after last exposure).
- Probes: ae_starts_after_emergence_window, ae_starts_after_end_of_study, ae_between_window_end_and_end_of_study.

### `ae.related.values`: Which causality values count as related to study treatment?

Applies when: `design.collects_adverse_events`. Default: none: the documents state it, or a person is asked.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `stated_list` | An adverse event is related to study treatment when its causality is one of {values}. | The causality is the collected value of AEREL, compared exactly. |

- Slot `values` of `stated_list`: type `list[text]`.
- Sources: CDISC Analysis Results Standard v1, model and examples (related events defined as a list of AEREL values); CDISC ADaM Structure for Occurrence Data (OCCDS) (pooled causality group, RELGRy).
- Probes: ae_with_each_causality_value.

## mod-bds-visits: Baseline and analysis visits

### `bds.baseline.rule`: Which record is the baseline of each parameter?

Applies when: `design.has_bds_parameters`. Default: `last_before_first_dose`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `last_before_first_dose` | Baseline is the last non-missing value before the first dose. | A value is before the first dose when its date is before the treatment start date. A value on that date is before the first dose unless both its time and the time of the first dose were collected and its time is not earlier. |
| `last_on_or_before_first_dose_date` | Baseline is the last non-missing value on or before the treatment start date. | Dates are compared; times are ignored. |
| `scheduled_baseline_visit` | Baseline is the last non-missing value at the scheduled visit {visit}. |  |

For every alternative: The last value is the latest by the collected date and time; of the values of one day, a value without a collected time comes before those with a time, and the highest sequence number breaks a remaining tie. Whether records of unscheduled visits may be baseline is decision bds.unscheduled.use.

- Slot `visit` of `scheduled_baseline_visit`: type `text`.
- Sources: CDISC ADaM Implementation Guide (BDS, baseline record flag ABLFL and baseline value BASE); admiral (pharmaverse), function reference and source (derive_var_extreme_flag(), order and mode, for the last record before treatment); yamaa, language documentation, rules and benchmarks (the baseline_flag verb: the last eligible row up to a reference date); R Consortium Submissions Pilot 6, CSR and SAP of CDISCPILOT01 (baseline defined as the value of a named visit (PLAN.md, E26)).
- Probes: day_1_value_after_first_dose_time, only_unscheduled_predose_value.

### `bds.window.table`: How are records assigned to analysis visits?

Applies when: `design.has_bds_parameters and design.fixed_visits`. Default: `nominal_visit`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `protocol_windows` | Post-baseline records are assigned to analysis visits by these study day windows: {windows}. | Both limits belong to the window, the target day lies in it, and the windows are listed in ascending order without overlap. A record on a study day outside every window has no analysis visit. |
| `midpoint_windows` | Post-baseline records are assigned to the analysis visit with the nearest target day, the earlier visit on a tie: {visits}. | The first window starts on study day 2 and the last one has no upper limit. |
| `nominal_visit` | Post-baseline records keep their collected visit as the analysis visit. | The target day of the visit is its planned study day (VISITDY). A record of an unscheduled visit has no analysis visit. |

For every alternative: A record is post-baseline when its date is after the treatment start date.

- Slot `windows` of `protocol_windows`: type `records`; each written as `{visit} with target day {target} from day {low} to day {high}`.
- Slot `visits` of `midpoint_windows`: type `records`; each written as `{visit} with target day {target}`.
- Sources: CDISC ADaM Implementation Guide (BDS analysis visit windowing variables, AVISIT, AWTARGET, AWLO and AWHI); yamaa, language documentation, rules and benchmarks (the benchmark of analysis windows by study day); R Consortium Submissions Pilot 7, yamaa specs and reviews of CDISCPILOT01 (AVISIT of the pilot ADVS: the collected visit).
- Probes: record_in_other_window_than_collected_visit, record_in_gap_between_protocol_windows.

### `bds.window.tiebreak`: Which record is analyzed when several fall in one analysis visit?

Applies when: `design.has_bds_parameters and design.fixed_visits`. Default: `closest_then_earlier`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `closest_then_earlier` | Of several records in one analysis visit, the one closest to the target day is analyzed, and the earlier one on a tie. |  |
| `closest_then_later` | Of several records in one analysis visit, the one closest to the target day is analyzed, and the later one on a tie. |  |
| `last_record` | Of several records in one analysis visit, the last one is analyzed. |  |

For every alternative: Only non-missing values compete. Earlier and later are by the collected date and time; of the values of one day, a value without a collected time comes before those with a time, and the sequence number breaks a remaining tie.

- Sources: CDISC ADaM Implementation Guide (BDS analysis record flag ANLzzFL and distance from target AWTDIFF); yamaa, language documentation, rules and benchmarks (the benchmark of closest visit selection: distance, then a tie rule).
- Probes: two_records_equally_far_from_target, two_records_in_window_later_one_farther, unscheduled_record_inside_window.

### `bds.unscheduled.use`: Do records of unscheduled visits compete for baseline and for analysis visits?

Applies when: `design.has_bds_parameters and design.unscheduled_visits`. Default: `compete`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `compete` | Records of unscheduled visits compete for baseline and for analysis visits. |  |
| `excluded` | Records of unscheduled visits are not used for baseline or for analysis visits. |  |

For every alternative: A visit is unscheduled when it has no planned study day (VISITDY is missing).

- Sources: R Consortium Submissions Pilot 7, yamaa specs and reviews of CDISCPILOT01 (AVISIT of the pilot ADVS: unscheduled visits are left out of the per visit analysis); R Consortium Submissions Pilot 6, CSR and SAP of CDISCPILOT01 (Table 14-6.06: unscheduled pre-dose samples counted as baseline (PLAN.md, E26)); CDISC SDTM Implementation Guide (visit variables: VISITDY is the planned study day of a visit).
- Probes: only_unscheduled_predose_value, unscheduled_record_inside_window.

### `bds.eot.record`: Is there an end-of-treatment record?

Applies when: `design.has_bds_parameters and design.has_exposure`. Default: `last_on_treatment_value`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `last_on_treatment_value` | An end-of-treatment record repeats the last non-missing post-baseline value on or before the treatment end date. | The record has the analysis visit End of Treatment and the derivation type LOV. A subject without a treatment end date takes the last post-baseline value. |
| `none` | There is no end-of-treatment record. |  |

- Sources: R Consortium Submissions Pilot 7, yamaa specs and reviews of CDISCPILOT01 (the end-of-treatment records of the pilot ADVS); yamaa, language documentation, rules and benchmarks (the benchmark of the end-of-treatment record); CDISC ADaM Implementation Guide (BDS derivation type DTYPE for derived records).
- Probes: end_of_treatment_visit_shown.

## Table families: tfl-demographics, tfl-ae-summary, tfl-ae-soc-pt, tfl-vitals-by-visit

### `tfl.output.include`: Is the output part of the planned outputs of the study?

Applies when: `design.always`. Default: `included`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `included` | The planned outputs include {output}. |  |
| `not_included` | The planned outputs do not include {output}. | No other decision of the table family applies then. |

- Sources: ICH E3: Structure and Content of Clinical Study Reports (section 14: 14.1 demographic data, 14.3.1 displays of adverse events; section 12.5 vital signs); CDISC Analysis Results Standard v1, model and examples (the list of planned analyses and outputs of a reporting event).
- Probes: output_shape.

### `tfl.population`: Which analysis set does the output use?

Applies when: `design.always`. Default: `randomized` for tfl-demographics; `safety` for tfl-ae-summary; `safety` for tfl-ae-soc-pt; `safety` for tfl-vitals-by-visit.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `safety` | The analysis set of {output} is the safety set. |  |
| `randomized` | The analysis set of {output} is the randomized set. |  |
| `efficacy` | The analysis set of {output} is the efficacy-evaluable set. |  |

- Sources: CDISC Analysis Results Standard v1, model and examples (analysis sets of the safety displays); R Consortium Submissions Pilot 6, CSR and SAP of CDISCPILOT01 (Table 14-2.01 on the intent-to-treat population; Tables 14-5.01 and 14-7.01 on the safety population (PLAN.md, appendix D)); ICH E3: Structure and Content of Clinical Study Reports (sections 11.1 and 11.2: data sets analysed; demographic and other baseline characteristics).
- Probes: randomized_never_dosed, dosed_without_postbaseline_value.

### `tfl.columns.arms`: In which order are the treatment columns?

Applies when: `design.multiple_arms`. Default: `ascending_dose_placebo_first`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `ascending_dose_placebo_first` | The treatment columns of {output} are in ascending order of dose, with placebo first. |  |
| `protocol_order` | The treatment columns of {output} are in the order in which the protocol lists the arms. |  |

For every alternative: Each column is headed by the treatment and the number of subjects of the analysis set in it.

- Sources: CDISC Analysis Results Standard v1, model and examples (the treatment grouping: placebo, low dose, high dose); R Consortium Submissions Pilot 6, CSR and SAP of CDISCPILOT01 (column order of Tables 14-2.01 and 14-5.01: placebo, low dose, high dose).
- Probes: arms_listed_out_of_dose_order.

### `tfl.columns.total`: Is there a total column?

Applies when: `design.multiple_arms`. Default: `all_arms`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `all_arms` | A total column of {output} pools all treatment arms. |  |
| `none` | There is no total column in {output}. |  |
| `active_arms` | A total column of {output} pools the treatment arms other than {control}. | The control is named by its treatment label as the treatment columns show it. |

For every alternative: A total column is the last column.

- Slot `control` of `active_arms`: type `text`.
- Sources: R Consortium Submissions Pilot 6, CSR and SAP of CDISCPILOT01 (Table 14-2.01 with a Total column; Table 14-5.01 without one); FDA Standard Safety Tables and Figures: Integrated Guide (demographic table with a total column; pooled active arms as an option of the safety tables).
- Probes: output_shape.

## tfl-demographics: Table of demographic and baseline characteristics

### `tfl.denominator`: What is the denominator of a percentage?

Applies when: `design.always`. Default: `analysis_set_per_column`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `analysis_set_per_column` | Percentages in the demographics table are based on the number of subjects of the analysis set in the column. |  |
| `subjects_with_data` | Percentages in the demographics table are based on the number of subjects with a non-missing value in the column. |  |

- Sources: CDISC Analysis Results Standard v1, model and examples (the percent operation names the analysis that gives its denominator).
- Probes: missing_characteristic_value.

## Table families: tfl-demographics, tfl-ae-summary, tfl-ae-soc-pt

### `tfl.percent.format`: How are percentages displayed?

Applies when: `design.always`. Default: `one_decimal_zero_blank`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `one_decimal_zero_blank` | Percentages in {output} have one decimal, and a count of zero is shown without a percentage. |  |
| `one_decimal_always` | Percentages in {output} have one decimal, and a count of zero is shown with its percentage. |  |

- Sources: CDISC Analysis Results Standard v1, model and examples (result pattern of a percentage: one decimal); R Consortium Submissions Pilot 6, CSR and SAP of CDISCPILOT01 (Table 14-5.01: zero counts printed without a percentage (PLAN.md, E25)).
- Probes: category_with_zero_count.

## Table families: tfl-demographics, tfl-vitals-by-visit

### `tfl.quantile.definition`: Which quantile definition gives the median and the quartiles?

Applies when: `design.always`. Default: `sas5`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `sas5` | Quantiles in {output} follow SAS definition 5, the empirical distribution function with averaging. |  |
| `r7` | Quantiles in {output} follow R type 7, linear interpolation of the order statistics. |  |

- Sources: SAS documentation, PROC UNIVARIATE, option PCTLDEF= (definitions 1 to 5) (PCTLDEF=5, the default: empirical distribution function with averaging); R documentation, stats::quantile (types 1 to 9, after Hyndman and Fan 1996) (type 7, the default; type 2 equals SAS definition 5); yamaa, language documentation, rules and benchmarks (FORMULA-18: a named quantile definition).
- Probes: group_size_separating_quantiles.

## Table families: tfl-demographics, tfl-ae-summary, tfl-ae-soc-pt, tfl-vitals-by-visit

### `tfl.rounding.rule`: How are displayed numbers rounded?

Applies when: `design.always`. Default: `half_away_from_zero`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `half_away_from_zero` | Displayed numbers in {output} are rounded half away from zero. |  |
| `half_even` | Displayed numbers in {output} are rounded half to even. |  |

For every alternative: A number is rounded once, from its full precision to the displayed decimals.

- Sources: yamaa, language documentation, rules and benchmarks (the rounding verb of the ADaM engine); R Consortium Submissions Pilot 6, CSR and SAP of CDISCPILOT01 (Table 14-2.01 reproduces with rounding half away from zero (PLAN.md, E24)).
- Probes: statistic_at_rounding_half.

## Table families: tfl-demographics, tfl-vitals-by-visit

### `tfl.decimals.rule`: How many decimals does each statistic have?

Applies when: `design.always`. Default: `relative_to_data`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `relative_to_data` | In {output}, the mean and the median have one more decimal than the data, the standard deviation has two more, and the minimum and the maximum have as many as the data. | The decimals of the data are the largest number of decimals among the values summarized in the row. Quartiles are shown as the median is. |
| `stated_decimals` | In {output}, the mean has {mean} decimals, the standard deviation {sd}, the median {median}, and the minimum and the maximum {range}. | Quartiles are shown as the median is. |

- Slot `mean` of `stated_decimals`: type `int`.
- Slot `sd` of `stated_decimals`: type `int`.
- Slot `median` of `stated_decimals`: type `int`.
- Slot `range` of `stated_decimals`: type `int`.
- Sources: R Consortium Submissions Pilot 6, CSR and SAP of CDISCPILOT01 (Table 14-2.01: mean one more decimal than the data, standard deviation two more (PLAN.md, E24)); CDISC Analysis Results Standard v1, model and examples (result patterns fix the decimals of each operation).
- Probes: data_decimals_differ_from_stated.

## tfl-demographics: Table of demographic and baseline characteristics

### `tfl.pvalue.format`: How are p-values displayed?

Applies when: `design.multiple_arms`. Default: `three_decimals`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `three_decimals` | P-values in the demographics table have three decimals, and a value below 0.001 is shown as <0.001. |  |
| `four_decimals` | P-values in the demographics table have four decimals, and a value below 0.0001 is shown as <0.0001. |  |

- Sources: R Consortium Submissions Pilot 6, CSR and SAP of CDISCPILOT01 (p-values of Tables 14-2.01 and 14-5.01 (PLAN.md, E24 and E25)); CDISC Analysis Results Standard v1, model and examples (a p-value operation with its result pattern).
- Probes: pvalue_column_shown, pvalue_below_display_limit.

### `tfl.demog.rows`: Which characteristics does the demographics table show, in which order?

Applies when: `design.always`. Default: none: the documents state it, or a person is asked.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `stated_list` | The rows of the demographics table are, in this order, {rows}. | Each row is named by its variable of the subject-level dataset: AGE, AGEGR1, SEX, RACEGR1, ETHNIC, HEIGHTBL, WEIGHTBL or BMIBL. |

- Slot `rows` of `stated_list`: type `list[name]`; one of AGE, AGEGR1, SEX, RACEGR1, ETHNIC, HEIGHTBL, WEIGHTBL, BMIBL.
- Sources: CDISC Analysis Results Standard v1, model and examples (the analyses of the demographics output: age, age group, sex, ethnicity, race, height); ICH E3: Structure and Content of Clinical Study Reports (section 11.2: demographic variables such as age, sex and race).
- Probes: output_shape.

### `tfl.demog.stats`: Which statistics do the continuous rows show?

Applies when: `design.always`. Default: `n_mean_sd_median_min_max`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `n_mean_sd_median_min_max` | Continuous rows of the demographics table show n, mean, standard deviation, median, minimum and maximum. |  |
| `with_quartiles` | Continuous rows of the demographics table show n, mean, standard deviation, median, first and third quartile, minimum and maximum. |  |

- Sources: CDISC Analysis Results Standard v1, model and examples (the continuous summary method: n, mean, SD, median, Q1, Q3, minimum, maximum); R Consortium Submissions Pilot 6, CSR and SAP of CDISCPILOT01 (Table 14-2.01: n, mean, SD, median, minimum, maximum).
- Probes: output_shape.

### `tfl.tests.include`: Are treatments compared in the demographics table?

Applies when: `design.multiple_arms`. Default: `none`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `none` | The demographics table shows no comparison between treatments. |  |
| `anova_chisq` | The demographics table compares treatments by analysis of variance for continuous rows and by the chi-square test for categorical rows. |  |
| `anova_fisher` | The demographics table compares treatments by analysis of variance for continuous rows and by Fisher's exact test for categorical rows. |  |

For every alternative: A comparison adds one p-value column after the treatment columns. The analysis of variance is one-way, with treatment as the factor.

- Sources: CDISC Analysis Results Standard v1, model and examples (comparison methods of the demographics output: chi-square, analysis of variance, Fisher's exact test); R Consortium Submissions Pilot 6, CSR and SAP of CDISCPILOT01 (Table 14-2.01, footnotes: analysis of variance and chi-square test (PLAN.md, E23)).
- Probes: output_shape, sparse_categorical_row.

## tfl-ae-summary: Summary table of adverse events

### `tfl.ae.summary.rows`: Which rows does the adverse event summary table have?

Applies when: `design.collects_adverse_events`. Default: `standard_rows`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `standard_rows` | The rows of the adverse event summary table are any event, related events, serious events, events leading to discontinuation of study treatment, and fatal events. |  |
| `stated_rows` | The rows of the adverse event summary table are, in this order, {rows}. | Each row is named by its code: ANY, RELATED, SERIOUS, DISCONTINUATION or FATAL. |

For every alternative: Every row counts subjects with at least one treatment-emergent event of its kind. Related is decision ae.related.values; serious is AESER equal to Y; leading to discontinuation is AEACN equal to DRUG WITHDRAWN; fatal is AESDTH equal to Y.

- Slot `rows` of `stated_rows`: type `list[name]`; one of ANY, RELATED, SERIOUS, DISCONTINUATION, FATAL.
- Sources: CDISC Analysis Results Standard v1, model and examples (the data subsets of the adverse event overview: related, serious, leading to death, leading to discontinuation); FDA Standard Safety Tables and Figures: Integrated Guide (overview of adverse events).
- Probes: output_shape.

## tfl-ae-soc-pt: Table of adverse events by system organ class and preferred term

### `tfl.ae.socpt.sort`: How are system organ classes and preferred terms sorted?

Applies when: `design.collects_adverse_events`. Default: `alphabetical`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `alphabetical` | System organ classes and preferred terms are sorted alphabetically. |  |
| `descending_frequency_total` | System organ classes and preferred terms are sorted by descending frequency over all arms, and alphabetically on a tie. |  |
| `descending_frequency_highest_dose` | System organ classes and preferred terms are sorted by descending frequency in the arm with the highest dose, and alphabetically on a tie. |  |

For every alternative: Frequency is the number of subjects. Preferred terms are sorted within their system organ class.

- Sources: R Consortium Submissions Pilot 6, CSR and SAP of CDISCPILOT01 (Table 14-5.01: organ classes and terms in alphabetical order (PLAN.md, E25)); FDA Standard Safety Tables and Figures: Integrated Guide (adverse event tables sorted by descending frequency).
- Probes: term_frequency_order_not_alphabetical, term_order_differs_between_total_and_highest_dose, terms_with_equal_frequency.

### `tfl.ae.socpt.threshold`: Is there a display threshold for preferred terms?

Applies when: `design.collects_adverse_events`. Default: `none`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `none` | Every preferred term with at least one event is shown. |  |
| `min_percent_any_arm` | A preferred term is shown only when at least {percent} percent of the subjects of an arm have it. | The percentage is taken at full precision in each treatment column. A system organ class is shown when one of its terms is shown; its own row still counts every subject with an event in the class. |

- Slot `percent` of `min_percent_any_arm`: type `number`.
- Sources: FDA Standard Safety Tables and Figures: Integrated Guide (common adverse events: terms at or above a stated percentage in any arm); R Consortium Submissions Pilot 6, CSR and SAP of CDISCPILOT01 (Table 14-5.01 shows every term (PLAN.md, E25)).
- Probes: term_at_display_threshold.

### `tfl.ae.socpt.counts`: Does the table count subjects, events or both?

Applies when: `design.collects_adverse_events`. Default: `subjects`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `subjects` | The adverse event table by system organ class and preferred term counts subjects. |  |
| `subjects_and_events` | The adverse event table by system organ class and preferred term counts subjects and events. | The number of events follows the subjects and their percentage in each cell. |

- Sources: R Consortium Submissions Pilot 6, CSR and SAP of CDISCPILOT01 (Table 14-5.01: subjects, percentages and events (PLAN.md, appendix D)); CDISC Analysis Results Standard v1, model and examples (subjects by system organ class and preferred term).
- Probes: output_shape.

## tfl-vitals-by-visit: Table of vital signs by visit

### `tfl.vs.scope`: Which parameters and analysis visits does the vital signs table show?

Applies when: `design.has_bds_parameters`. Default: none: the documents state it, or a person is asked.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `stated_lists` | The vital signs table by visit shows the parameters {parameters} at the analysis visits {visits}. | Parameters are named by their code (PARAMCD) and visits by their analysis visit (AVISIT), each in the order of the list. Baseline and End of Treatment are analysis visits. |

- Slot `parameters` of `stated_lists`: type `list[name]`.
- Slot `visits` of `stated_lists`: type `list[text]`.
- Sources: CDISC Analysis Results Standard v1, model and examples (the vital signs analyses grouped by parameter and visit); ICH E3: Structure and Content of Clinical Study Reports (section 12.5: vital signs, physical findings and other observations related to safety).
- Probes: output_shape.

### `tfl.vs.layout`: How are the observed value and the change from baseline arranged?

Applies when: `design.has_bds_parameters`. Default: `side_by_side`.

| Alternative | Statement | Meaning |
| --- | --- | --- |
| `side_by_side` | The vital signs table by visit shows the observed value and the change from baseline side by side. |  |
| `stacked` | The vital signs table by visit shows the observed value and the change from baseline in separate blocks. |  |

For every alternative: Change from baseline is shown for post-baseline visits only.

- Sources: CDISC Analysis Results Standard v1, model and examples (observed value and change from baseline as two analyses of one output); R Consortium Submissions Pilot 6, CSR and SAP of CDISCPILOT01 (Tables 14-7.01 and 14-7.02: observed value and change in separate tables (PLAN.md, appendix D)).
- Probes: output_shape.

## Alternatives without a public source of their own

Kept by the owner at node N1 on 2026-11-17 as the plan's own alternatives (seed list of PLAN.md appendix B); the answer is provisional.

- `demo.race.pooling/pooled_below_count`: ADaMIG has the variable for a pooled race group (RACEGRy) and leaves the rule to the sponsor. No public source states pooling below a count.
- `ae.teae.end/end_of_study`: admiral takes any treatment end date and a window after it; no cited source names the end-of-study date as the end of emergence.
- `tfl.ae.socpt.sort/descending_frequency_highest_dose`: The FDA guide is cited for sorting by descending frequency; that it names the arm with the highest dose was not confirmed.

## Left out of this draft

- `ae.teae.worsening`: Needs the severity before treatment, which the SDTM domains of M1 (DM, DS, EX, AE, VS, SV) do not hold: the public sources use a sponsor variable (admiral, initial_intensity) or Findings About records (yamaa benchmark adam-adae-worsening-emergence).
- `ae.severity.worst`: No table family of M1 prints severity by term, so no alternative can change a result.
- `ae.occurrence.flags`: The M1 tables count subjects from the records themselves, so the flags change no result. The house parent spec of ADAE adds AOCCFL, AOCCSFL and AOCCPFL as conformance variables.
- `disp.reason.source`: No table family of M1 prints the reason for discontinuation. The house parent spec of ADSL adds DCSREAS from DSDECOD as a conformance variable.
- `bds.baseline.rule/mean_of_predose_records`: Needs a derived record (DTYPE AVERAGE) built by aggregation; kept for std-2 together with its yamaa row template.
- `bds.window.tiebreak/average`: Needs a derived record (DTYPE AVERAGE) per analysis visit; kept for std-2 together with its yamaa row template.
