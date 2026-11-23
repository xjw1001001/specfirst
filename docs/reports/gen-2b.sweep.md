# gen-2b: the sweep after the review (scripts, commands, output)

Evidence for docs/reports/gen-2b.md (rule R8). The scripts lay in a
scratch folder of the executor outside every checkout (here `$SCRATCH`);
they are kept here as they ran. `one_kit.py` and `summarize.py` are
the reviewer's scripts of the first pass of the review (E2 to E4 of
docs/reports/gen-2b.review.md), unchanged. Every kit is written without R
(`with_r=False`): the engines are compared by the gate, not here.

## The decision vectors of the gate seed (lifted.py)

```text
$ cd /mnt/d/trial_work/specfirst-gen && . scripts/env.sh
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 python -B $SCRATCH/lifted.py gen-2a
kit 1: table on the safety set; none of the three
kit 2: table on the randomized set; (a) emergence by the time of the first dose, a partial start completed (first_of_month)
kit 3: table on the randomized set; (a) emergence by the time of the first dose, a partial start completed (first_of_month_not_before_first_dose)
kit 4: table on the efficacy set; none of the three
kit 5: table on the randomized set; none of the three
kit 6: table on the safety set; none of the three
kit 7: table on the efficacy set; (b) the treatment record as the end-of-study record
kit 8: table on the randomized set; (a) emergence by the time of the first dose, a partial start completed (first_of_month)
kit 9: table on the efficacy set; none of the three
kit 10: table on the safety set; (a) emergence by the time of the first dose, a partial start completed (first_of_month)
```

## The sweep (job.sh, make_list.sh, one_kit.py, summarize.py)

```text
$ bash $SCRATCH/make_list.sh
54
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 bash $SCRATCH/job.sh sweep < $SCRATCH/sweep.list
lift-a-efficacy-0dec (review-g2b/lift-a-efficacy-0dec, number 4): written; 16 separated, 18 read, 16 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated'], ['ae.related.values', 'no_alternative']]
    gold: start first_ex_record, end ds_date_when_ex_missing, imput first_day_of_month, disp disposition_event_by_subcategory, aestart first_of_month, teae at_or_after_first_dose_time/last_dose_plus_days, pop efficacy, actual dm_actarm, arms ascending_dose_placebo_first, total active_arms, rows standard_rows
    planted for: table on the efficacy set, by planned treatment; 0 decimals; window 30 days; column 'Placebo' of 16 subjects (1 added), 10 with an event, 2 with a serious one; the subject without an exposure end date completes its treatment, and a second one without a study-level disposition record; a partial event in the month of a first dose
lift-b-efficacy-followup (review-g2b/lift-b-efficacy-followup, number 9): written; 16 separated, 18 read, 16 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated'], ['ae.related.values', 'no_alternative']]
    gold: start dm_rfxstdtc, end ds_date_when_ex_missing, imput first_day_of_month, disp disposition_event_by_subcategory, aestart first_of_month_not_before_first_dose, teae on_or_after_first_dose_date/last_dose_plus_days, pop efficacy, actual first_ex_treatment, arms protocol_order, total none, rows standard_rows
    planted for: table on the efficacy set, by planned treatment; 1 decimals; window 14 days; column 'Placebo' of 32 subjects (0 added), 26 with an event, 2 with a serious one; the subject without an exposure end date completes its treatment, with a treatment and a study disposition record; causality events not serious
lift-b-safety-planned-2dec (review-g2b/lift-b-safety-planned-2dec, number 6): written; 17 separated, 18 read, 17 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated']]
    gold: start first_ex_with_dose, end ds_date_when_ex_missing, imput not_completed, disp disposition_event_by_subcategory, aestart first_of_month_not_before_first_dose, teae at_or_after_first_dose_time/last_dose_plus_days, pop safety, actual dm_actarm, arms protocol_order, total none, rows standard_rows
    planted for: table on the safety set, by planned treatment; 2 decimals; window 30 days; column 'Placebo' of 32 subjects (16 added), 9 with an event, 1 with a serious one; the subject without an exposure end date stops early, with a treatment and a study disposition record; a partial event in the month of a first dose without a time; causalit
lift-a-notbefore-rand-2dec (review-g2b/lift-a-notbefore-rand-2dec, number 2): written; 16 separated, 16 read, 16 applicable; applicable+unseparated none; read, not applicable: []
    gold: start first_ex_with_dose, end last_ex_end_date, imput not_completed, disp disposition_event_by_subcategory, aestart first_of_month_not_before_first_dose, teae at_or_after_first_dose_time/last_dose_plus_days, pop randomized, actual same_as_planned, arms ascending_dose_placebo_first, total all_arms, rows standard_rows
    planted for: table on the randomized set, by planned treatment; 2 decimals; window 30 days; column 'Placebo' of 32 subjects (16 added), 13 with an event, 1 with a serious one; the subject without an exposure end date completes its treatment, with a treatment and a study disposition record; a partial event in the month of a first dose without
lift-c-randomized-post (review-g2b/lift-c-randomized-post, number 8): written; 17 separated, 17 read, 17 applicable; applicable+unseparated none; read, not applicable: []
    gold: start first_ex_record, end ds_date_when_ex_missing, imput not_completed, disp disposition_event_by_subcategory, aestart first_of_month, teae by_time_when_collected/last_dose_plus_days, pop randomized, actual dm_actarm, arms protocol_order, total active_arms, rows standard_rows
    planted for: table on the randomized set, by planned treatment; 1 decimals; window 30 days; column 'Placebo' of 32 subjects (0 added), 26 with an event, 2 with a serious one; the subject without an exposure end date completes its treatment, and a second one without a study-level disposition record; causality events not serious
lift-c-firstex-0dec (review-g2b/lift-c-firstex-0dec, number 2): written; 17 separated, 17 read, 17 applicable; applicable+unseparated none; read, not applicable: []
    gold: start first_ex_with_dose, end ds_date_when_ex_missing, imput first_day_of_month, disp disposition_event_by_subcategory, aestart first_of_month, teae on_or_after_first_dose_date/last_dose_plus_days, pop safety, actual first_ex_treatment, arms ascending_dose_placebo_first, total none, rows stated_rows
    planted for: table on the safety set, by actual treatment; 0 decimals; window 14 days; column 'PLACEBO' of 24 subjects (7 added), 15 with an event, 3 with a serious one; the subject without an exposure end date stops early, and a second one without a study-level disposition record; causality events not serious
lift-c-efficacy-visit (review-g2b/lift-c-efficacy-visit, number 4): written; 16 separated, 17 read, 16 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated']]
    gold: start first_ex_with_dose, end ds_date_when_ex_missing, imput first_day_of_month, disp disposition_event_by_subcategory, aestart first_of_month_not_before_first_dose, teae on_or_after_first_dose_date/last_dose_plus_days, pop efficacy, actual same_as_planned, arms ascending_dose_placebo_first, total none, rows stated_rows
    planted for: table on the efficacy set, by planned treatment; 2 decimals; window 30 days; column 'Placebo' of 32 subjects (0 added), 25 with an event, 1 with a serious one; the subject without an exposure end date completes its treatment, and a second one without a study-level disposition record; causality events not serious
firstex-2dec-protocol (review-g2b/firstex-2dec-protocol, number 6): written; 15 separated, 15 read, 15 applicable; applicable+unseparated none; read, not applicable: []
    gold: start first_ex_record, end last_ex_end_date, imput first_day_of_month, disp disposition_event_by_subcategory, aestart first_of_month_not_before_first_dose, teae on_or_after_first_dose_date/no_end, pop safety, actual first_ex_treatment, arms protocol_order, total none, rows stated_rows
    planted for: table on the safety set, by actual treatment; 2 decimals; window none; column 'PLACEBO' of 32 subjects (15 added), 9 with an event, 1 with a serious one; the subject without an exposure end date stops early, with a treatment and a study disposition record; causality events not serious
planned-same-0dec-related (review-g2b/planned-same-0dec-related, number 1): written; 15 separated, 17 read, 15 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated'], ['pop.safety.grouping', 'unseparated']]
    gold: start dm_rfxstdtc, end last_ex_end_date, imput first_day_of_month, disp disposition_event_by_subcategory, aestart first_of_month_not_before_first_dose, teae by_time_when_collected/last_dose_plus_days, pop safety, actual same_as_planned, arms protocol_order, total none, rows stated_rows
    planted for: table on the safety set, by planned treatment; 0 decimals; window 30 days; column 'Placebo' of 48 subjects (0 added), 30 with an event, 6 with a serious one; the subject without an exposure end date stops early, with a treatment and a study disposition record; causality events not serious
armcd-map-recordend-serrel (review-g2b/armcd-map-recordend-serrel, number 2): written; 16 separated, 16 read, 16 applicable; applicable+unseparated none; read, not applicable: []
    gold: start dm_rfxstdtc, end last_ex_record_end, imput not_completed, disp disposition_event, aestart first_of_month, teae on_or_after_first_dose_date/last_dose_plus_days, pop randomized, actual first_ex_treatment, arms protocol_order, total none, rows stated_rows
    planted for: table on the randomized set, by planned treatment; 0 decimals; window 30 days; column 'Placebo' of 32 subjects (0 added), 20 with an event, 4 with a serious one; the subject without an exposure end date stops early; causality events serious
laststart-bytime-2dec-actual (review-g2b/laststart-bytime-2dec-actual, number 10): written; 16 separated, 16 read, 16 applicable; applicable+unseparated none; read, not applicable: []
    gold: start first_ex_with_dose, end last_ex_start_date, imput not_completed, disp disposition_event_by_subcategory, aestart first_of_month_not_before_first_dose, teae at_or_after_first_dose_time/last_dose_plus_days, pop safety, actual dm_actarm, arms ascending_dose_placebo_first, total active_arms, rows stated_rows
    planted for: table on the safety set, by actual treatment; 2 decimals; window 7 days; column 'Placebo' of 32 subjects (16 added), 9 with an event, 1 with a serious one; the subject without an exposure end date stops early, with a treatment and a study disposition record; a partial event in the month of a first dose without a time; causality
efficacy-values-active-total (review-g2b/efficacy-values-active-total, number 4): written; 16 separated, 17 read, 16 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated']]
    gold: start first_ex_with_dose, end last_ex_end_date, imput not_completed, disp disposition_event_by_subcategory, aestart first_of_month_not_before_first_dose, teae on_or_after_first_dose_date/last_dose_plus_days, pop efficacy, actual same_as_planned, arms ascending_dose_placebo_first, total active_arms, rows stated_rows
    planted for: table on the efficacy set, by planned treatment; 1 decimals; window 30 days; column 'Placebo' of 32 subjects (0 added), 26 with an event, 2 with a serious one; the subject without an exposure end date completes its treatment, and a second one without a study-level disposition record; causality events serious
drawn (review-g2b-sweep/kit-1, number 1): written; 16 separated, 16 read, 16 applicable; applicable+unseparated none; read, not applicable: []
    gold: start first_ex_with_dose, end last_ex_record_end, imput first_day_of_month, disp disposition_event_by_subcategory, aestart first_of_month, teae on_or_after_first_dose_date/last_dose_plus_days, pop randomized, actual dm_actarm, arms ascending_dose_placebo_first, total all_arms, rows standard_rows
    planted for: table on the randomized set, by planned treatment; 2 decimals; window 30 days; column 'Placebo' of 32 subjects (16 added), 9 with an event, 1 with a serious one; the subject without an exposure end date stops early, with a treatment and a study disposition record; causality events not serious
drawn (sweep-a/kit-1, number 1): written; 15 separated, 15 read, 15 applicable; applicable+unseparated none; read, not applicable: []
    gold: start first_ex_record, end last_ex_end_date, imput first_day_of_month, disp disposition_event_by_subcategory, aestart not_completed, teae by_time_when_collected/last_dose_plus_days, pop randomized, actual dm_actarm, arms ascending_dose_placebo_first, total active_arms, rows stated_rows
    planted for: table on the randomized set, by planned treatment; 1 decimals; window 28 days; column 'Placebo' of 32 subjects (0 added), 18 with an event, 2 with a serious one; the subject without an exposure end date completes its treatment, with a treatment and a study disposition record; causality events not serious
drawn (review-g2b-sweep/kit-2, number 2): written; 16 separated, 16 read, 16 applicable; applicable+unseparated none; read, not applicable: []
    gold: start first_ex_record, end last_ex_end_date, imput not_completed, disp disposition_event_by_subcategory, aestart first_of_month, teae on_or_after_first_dose_date/last_dose_plus_days, pop randomized, actual dm_actarm, arms ascending_dose_placebo_first, total none, rows standard_rows
    planted for: table on the randomized set, by planned treatment; 1 decimals; window 14 days; column 'Placebo' of 32 subjects (0 added), 26 with an event, 2 with a serious one; the subject without an exposure end date completes its treatment, and a second one without a study-level disposition record; causality events not serious
drawn (sweep-a/kit-2, number 2): written; 16 separated, 16 read, 16 applicable; applicable+unseparated none; read, not applicable: []
    gold: start first_ex_with_dose, end last_ex_end_date, imput not_completed, disp disposition_event, aestart first_of_month_not_before_first_dose, teae on_or_after_first_dose_date/last_dose_plus_days, pop randomized, actual same_as_planned, arms ascending_dose_placebo_first, total all_arms, rows stated_rows
    planted for: table on the randomized set, by planned treatment; 2 decimals; window 14 days; column 'Placebo' of 32 subjects (0 added), 25 with an event, 1 with a serious one; the subject without an exposure end date completes its treatment; causality events not serious
drawn (review-g2b-sweep/kit-3, number 3): written; 17 separated, 17 read, 17 applicable; applicable+unseparated none; read, not applicable: []
    gold: start first_ex_record, end ds_date_when_ex_missing, imput first_day_of_month, disp disposition_event_by_subcategory, aestart first_of_month_not_before_first_dose, teae on_or_after_first_dose_date/last_dose_plus_days, pop randomized, actual dm_actarm, arms ascending_dose_placebo_first, total all_arms, rows standard_rows
    planted for: table on the randomized set, by planned treatment; 1 decimals; window 30 days; column 'Placebo' of 16 subjects (0 added), 13 with an event, 1 with a serious one; the subject without an exposure end date completes its treatment, with a treatment and a study disposition record; causality events not serious
drawn (sweep-a/kit-3, number 3): written; 16 separated, 16 read, 16 applicable; applicable+unseparated none; read, not applicable: []
    gold: start first_ex_with_dose, end last_ex_record_end, imput not_completed, disp disposition_event, aestart first_of_month_not_before_first_dose, teae at_or_after_first_dose_time/last_dose_plus_days, pop randomized, actual dm_actarm, arms ascending_dose_placebo_first, total none, rows stated_rows
    planted for: table on the randomized set, by planned treatment; 1 decimals; window 30 days; column 'Placebo' of 48 subjects (0 added), 27 with an event, 3 with a serious one; the subject without an exposure end date completes its treatment; a partial event in the month of a first dose without a time; causality events not serious
drawn (review-g2b-sweep/kit-4, number 4): written; 16 separated, 17 read, 16 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated']]
    gold: start first_ex_with_dose, end last_ex_end_date, imput first_day_of_month, disp disposition_event, aestart first_of_month_not_before_first_dose, teae on_or_after_first_dose_date/last_dose_plus_days, pop efficacy, actual dm_actarm, arms protocol_order, total none, rows stated_rows
    planted for: table on the efficacy set, by planned treatment; 0 decimals; window 30 days; column 'Placebo' of 32 subjects (1 added), 20 with an event, 4 with a serious one; the subject without an exposure end date completes its treatment; causality events not serious
drawn (sweep-a/kit-4, number 4): written; 16 separated, 17 read, 16 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated']]
    gold: start first_ex_with_dose, end last_ex_end_date, imput first_day_of_month, disp disposition_event_by_subcategory, aestart not_completed, teae at_or_after_first_dose_time/last_dose_plus_days, pop efficacy, actual dm_actarm, arms protocol_order, total active_arms, rows standard_rows
    planted for: table on the efficacy set, by planned treatment; 1 decimals; window 30 days; column 'Placebo' of 32 subjects (0 added), 26 with an event, 2 with a serious one; the subject without an exposure end date completes its treatment, with a treatment and a study disposition record; a partial event in the month of a first dose without a
drawn (review-g2b-sweep/kit-5, number 5): written; 14 separated, 15 read, 14 applicable; applicable+unseparated none; read, not applicable: [['ae.related.values', 'no_alternative']]
    gold: start first_ex_with_dose, end last_ex_end_date, imput first_day_of_month, disp disposition_event_by_subcategory, aestart first_of_month, teae on_or_after_first_dose_date/no_end, pop randomized, actual dm_actarm, arms protocol_order, total none, rows standard_rows
    planted for: table on the randomized set, by planned treatment; 2 decimals; window none; column 'Placebo' of 64 subjects (16 added), 34 with an event, 2 with a serious one; the subject without an exposure end date stops early, with a treatment and a study disposition record; causality events not serious
drawn (sweep-a/kit-5, number 5): written; 14 separated, 15 read, 14 applicable; applicable+unseparated none; read, not applicable: [['ae.related.values', 'no_alternative']]
    gold: start first_ex_record, end last_ex_record_end, imput not_completed, disp disposition_event, aestart first_of_month_not_before_first_dose, teae at_or_after_first_dose_time/no_end, pop randomized, actual dm_actarm, arms protocol_order, total active_arms, rows standard_rows
    planted for: table on the randomized set, by planned treatment; 2 decimals; window none; column 'Placebo' of 64 subjects (17 added), 42 with an event, 2 with a serious one; the subject without an exposure end date completes its treatment; a partial event in the month of a first dose without a time; causality events not serious
drawn (review-g2b-sweep/kit-6, number 6): written; 14 separated, 15 read, 14 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated']]
    gold: start dm_rfxstdtc, end last_ex_end_date, imput not_completed, disp disposition_event, aestart first_of_month_not_before_first_dose, teae at_or_after_first_dose_time/no_end, pop safety, actual first_ex_treatment, arms ascending_dose_placebo_first, total none, rows stated_rows
    planted for: table on the safety set, by planned treatment; 1 decimals; window none; column 'Placebo' of 32 subjects (0 added), 26 with an event, 2 with a serious one; the subject without an exposure end date stops early; a partial event in the month of a first dose without a time; causality events not serious
drawn (sweep-a/kit-6, number 6): written; 15 separated, 17 read, 15 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated'], ['ae.related.values', 'no_alternative']]
    gold: start dm_rfxstdtc, end last_ex_end_date, imput first_day_of_month, disp disposition_event_by_subcategory, aestart first_of_month_not_before_first_dose, teae by_time_when_collected/last_dose_plus_days, pop safety, actual dm_actarm, arms protocol_order, total none, rows standard_rows
    planted for: table on the safety set, by planned treatment; 1 decimals; window 30 days; column 'Placebo' of 16 subjects (0 added), 9 with an event, 1 with a serious one; the subject without an exposure end date stops early, and a second one without a study-level disposition record; causality events not serious
drawn (review-g2b-sweep/kit-7, number 7): written; 16 separated, 17 read, 16 applicable; applicable+unseparated none; read, not applicable: [['ae.related.values', 'no_alternative']]
    gold: start first_ex_record, end ds_date_when_ex_missing, imput first_day_of_month, disp disposition_event_by_subcategory, aestart first_of_month, teae on_or_after_first_dose_date/last_dose_plus_days, pop randomized, actual dm_actarm, arms protocol_order, total active_arms, rows standard_rows
    planted for: table on the randomized set, by planned treatment; 1 decimals; window 30 days; column 'Placebo' of 16 subjects (0 added), 9 with an event, 1 with a serious one; the subject without an exposure end date completes its treatment, and a second one without a study-level disposition record; causality events not serious
drawn (sweep-a/kit-7, number 7): written; 17 separated, 19 read, 17 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated'], ['pop.safety.grouping', 'unseparated']]
    gold: start first_ex_with_dose, end ds_date_when_ex_missing, imput not_completed, disp disposition_event_by_subcategory, aestart first_of_month_not_before_first_dose, teae on_or_after_first_dose_date/last_dose_plus_days, pop safety, actual same_as_planned, arms protocol_order, total active_arms, rows stated_rows
    planted for: table on the safety set, by actual treatment; 1 decimals; window 30 days; column 'Placebo' of 64 subjects (15 added), 20 with an event, 4 with a serious one; the subject without an exposure end date stops early, and a second one without a study-level disposition record; causality events not serious
drawn (review-g2b-sweep/kit-8, number 8): written; 14 separated, 15 read, 14 applicable; applicable+unseparated none; read, not applicable: [['ae.related.values', 'no_alternative']]
    gold: start first_ex_record, end ds_date_when_ex_missing, imput first_day_of_month, disp disposition_event_by_subcategory, aestart first_of_month, teae at_or_after_first_dose_time/no_end, pop randomized, actual dm_actarm, arms protocol_order, total active_arms, rows standard_rows
    planted for: table on the randomized set, by planned treatment; 0 decimals; window none; column 'Placebo' of 32 subjects (0 added), 20 with an event, 4 with a serious one; the subject without an exposure end date stops early, and a second one without a study-level disposition record; a partial event in the month of a first dose without a tim
drawn (sweep-a/kit-8, number 8): written; 15 separated, 15 read, 15 applicable; applicable+unseparated none; read, not applicable: []
    gold: start first_ex_with_dose, end last_ex_end_date, imput first_day_of_month, disp disposition_event, aestart not_completed, teae by_time_when_collected/no_end, pop randomized, actual same_as_planned, arms protocol_order, total none, rows standard_rows
    planted for: table on the randomized set, by planned treatment; 1 decimals; window none; column 'Placebo' of 32 subjects (0 added), 26 with an event, 2 with a serious one; the subject without an exposure end date stops early; causality events not serious
drawn (review-g2b-sweep/kit-9, number 9): written; 15 separated, 16 read, 15 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated']]
    gold: start first_ex_record, end last_ex_end_date, imput not_completed, disp disposition_event, aestart not_completed, teae by_time_when_collected/last_dose_plus_days, pop efficacy, actual dm_actarm, arms ascending_dose_placebo_first, total none, rows stated_rows
    planted for: table on the efficacy set, by planned treatment; 1 decimals; window 30 days; column 'Placebo' of 32 subjects (2 added), 18 with an event, 2 with a serious one; the subject without an exposure end date completes its treatment; causality events not serious
drawn (sweep-a/kit-9, number 9): written; 15 separated, 17 read, 15 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated'], ['ae.related.values', 'no_alternative']]
    gold: start first_ex_record, end last_ex_end_date, imput not_completed, disp disposition_event, aestart first_of_month_not_before_first_dose, teae at_or_after_first_dose_time/last_dose_plus_days, pop efficacy, actual dm_actarm, arms protocol_order, total active_arms, rows stated_rows
    planted for: table on the efficacy set, by planned treatment; 1 decimals; window 30 days; column 'Placebo' of 48 subjects (0 added), 39 with an event, 3 with a serious one; the subject without an exposure end date completes its treatment; a partial event in the month of a first dose without a time; causality events serious
drawn (review-g2b-sweep/kit-10, number 10): written; 17 separated, 17 read, 17 applicable; applicable+unseparated none; read, not applicable: []
    gold: start dm_rfxstdtc, end last_ex_end_date, imput first_day_of_month, disp disposition_event_by_subcategory, aestart not_completed, teae on_or_after_first_dose_date/last_dose_plus_days, pop safety, actual dm_actarm, arms ascending_dose_placebo_first, total active_arms, rows standard_rows
    planted for: table on the safety set, by actual treatment; 1 decimals; window 30 days; column 'Placebo' of 32 subjects (0 added), 26 with an event, 2 with a serious one; the subject without an exposure end date stops early, with a treatment and a study disposition record; causality events not serious
drawn (sweep-a/kit-10, number 10): written; 15 separated, 16 read, 15 applicable; applicable+unseparated none; read, not applicable: [['ae.related.values', 'no_alternative']]
    gold: start dm_rfxstdtc, end last_ex_end_date, imput not_completed, disp disposition_event, aestart first_of_month_not_before_first_dose, teae by_time_when_collected/no_end, pop safety, actual dm_actarm, arms protocol_order, total active_arms, rows stated_rows
    planted for: table on the safety set, by actual treatment; 2 decimals; window none; column 'Placebo' of 64 subjects (16 added), 26 with an event, 2 with a serious one; the subject without an exposure end date stops early; causality events not serious
drawn (review-g2b-rfx-3/kit-4, number 4): written; 14 separated, 15 read, 14 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated']]
    gold: start dm_rfxstdtc, end last_ex_end_date, imput first_day_of_month, disp disposition_event_by_subcategory, aestart first_of_month_not_before_first_dose, teae on_or_after_first_dose_date/no_end, pop efficacy, actual dm_actarm, arms ascending_dose_placebo_first, total none, rows stated_rows
    planted for: table on the efficacy set, by planned treatment; 0 decimals; window none; column 'Placebo' of 32 subjects (1 added), 20 with an event, 4 with a serious one; the subject without an exposure end date completes its treatment, with a treatment and a study disposition record; causality events not serious
drawn (review-g2b-rfx-5/kit-4, number 4): written; 16 separated, 17 read, 16 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated']]
    gold: start dm_rfxstdtc, end last_ex_start_date, imput not_completed, disp disposition_event, aestart first_of_month_not_before_first_dose, teae on_or_after_first_dose_date/last_dose_plus_days, pop efficacy, actual dm_actarm, arms ascending_dose_placebo_first, total none, rows stated_rows
    planted for: table on the efficacy set, by planned treatment; 1 decimals; window 30 days; column 'Placebo' of 32 subjects (0 added), 18 with an event, 2 with a serious one; the subject without an exposure end date completes its treatment; causality events not serious
drawn (review-g2b-rfx-14/kit-9, number 9): written; 15 separated, 16 read, 15 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated']]
    gold: start dm_rfxstdtc, end last_ex_end_date, imput not_completed, disp disposition_event_by_subcategory, aestart first_of_month_not_before_first_dose, teae on_or_after_first_dose_date/last_dose_plus_days, pop efficacy, actual dm_actarm, arms protocol_order, total none, rows stated_rows
    planted for: table on the efficacy set, by planned treatment; 1 decimals; window 30 days; column 'Placebo' of 32 subjects (1 added), 26 with an event, 2 with a serious one; the subject without an exposure end date completes its treatment, with a treatment and a study disposition record; causality events not serious
drawn (review-g2b-rfx-17/kit-4, number 4): written; 16 separated, 17 read, 16 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated']]
    gold: start dm_rfxstdtc, end last_ex_start_date, imput not_completed, disp disposition_event_by_subcategory, aestart first_of_month_not_before_first_dose, teae on_or_after_first_dose_date/last_dose_plus_days, pop efficacy, actual dm_actarm, arms ascending_dose_placebo_first, total none, rows stated_rows
    planted for: table on the efficacy set, by planned treatment; 2 decimals; window 30 days; column 'Placebo' of 64 subjects (19 added), 34 with an event, 2 with a serious one; the subject without an exposure end date completes its treatment, with a treatment and a study disposition record; causality events not serious
drawn (review-g2b-rfx-22/kit-9, number 9): written; 16 separated, 17 read, 16 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated']]
    gold: start dm_rfxstdtc, end last_ex_end_date, imput not_completed, disp disposition_event_by_subcategory, aestart first_of_month_not_before_first_dose, teae by_time_when_collected/last_dose_plus_days, pop efficacy, actual first_ex_treatment, arms ascending_dose_placebo_first, total all_arms, rows standard_rows
    planted for: table on the efficacy set, by planned treatment; 2 decimals; window 30 days; column 'Placebo' of 64 subjects (16 added), 42 with an event, 2 with a serious one; the subject without an exposure end date completes its treatment, and a second one without a study-level disposition record; causality events not serious
drawn (review-g2b-rfx-27/kit-4, number 4): written; 16 separated, 17 read, 16 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated']]
    gold: start dm_rfxstdtc, end last_ex_end_date, imput first_day_of_month, disp disposition_event, aestart first_of_month_not_before_first_dose, teae by_time_when_collected/last_dose_plus_days, pop efficacy, actual dm_actarm, arms protocol_order, total none, rows standard_rows
    planted for: table on the efficacy set, by planned treatment; 1 decimals; window 30 days; column 'Placebo' of 32 subjects (1 added), 26 with an event, 2 with a serious one; the subject without an exposure end date completes its treatment; causality events not serious
drawn (review-g2b-rfx-40/kit-4, number 4): written; 15 separated, 16 read, 15 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated']]
    gold: start dm_rfxstdtc, end last_ex_end_date, imput not_completed, disp disposition_event, aestart first_of_month_not_before_first_dose, teae on_or_after_first_dose_date/no_end, pop efficacy, actual first_ex_treatment, arms ascending_dose_placebo_first, total all_arms, rows stated_rows
    planted for: table on the efficacy set, by planned treatment; 1 decimals; window none; column 'Placebo' of 16 subjects (0 added), 9 with an event, 1 with a serious one; the subject without an exposure end date completes its treatment; causality events not serious
drawn (review-g2b-rfx-48/kit-9, number 9): written; 16 separated, 17 read, 16 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated']]
    gold: start dm_rfxstdtc, end ds_date_when_ex_missing, imput not_completed, disp disposition_event_by_subcategory, aestart first_of_month_not_before_first_dose, teae on_or_after_first_dose_date/last_dose_plus_days, pop efficacy, actual first_ex_treatment, arms protocol_order, total active_arms, rows stated_rows
    planted for: table on the efficacy set, by planned treatment; 0 decimals; window 30 days; column 'Placebo' of 32 subjects (1 added), 20 with an event, 4 with a serious one; the subject without an exposure end date completes its treatment, and a second one without a study-level disposition record; causality events not serious
drawn (review-g2b-rfx-52/kit-9, number 9): written; 16 separated, 17 read, 16 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated']]
    gold: start dm_rfxstdtc, end last_ex_end_date, imput first_day_of_month, disp disposition_event_by_subcategory, aestart first_of_month_not_before_first_dose, teae by_time_when_collected/last_dose_plus_days, pop efficacy, actual dm_actarm, arms ascending_dose_placebo_first, total none, rows standard_rows
    planted for: table on the efficacy set, by planned treatment; 1 decimals; window 30 days; column 'Placebo' of 48 subjects (0 added), 39 with an event, 3 with a serious one; the subject without an exposure end date completes its treatment, and a second one without a study-level disposition record; causality events not serious
drawn (review-g2b-rfx-56/kit-9, number 9): written; 16 separated, 17 read, 16 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated']]
    gold: start dm_rfxstdtc, end last_ex_start_date, imput not_completed, disp disposition_event_by_subcategory, aestart first_of_month_not_before_first_dose, teae at_or_after_first_dose_time/last_dose_plus_days, pop efficacy, actual first_ex_treatment, arms protocol_order, total none, rows standard_rows
    planted for: table on the efficacy set, by planned treatment; 1 decimals; window 30 days; column 'Placebo' of 16 subjects (0 added), 9 with an event, 1 with a serious one; the subject without an exposure end date completes its treatment, with a treatment and a study disposition record; a partial event in the month of a first dose without a t
drawn (review-g2b-rfx-57/kit-4, number 4): written; 15 separated, 17 read, 15 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated'], ['ae.related.values', 'no_alternative']]
    gold: start dm_rfxstdtc, end last_ex_record_end, imput first_day_of_month, disp disposition_event_by_subcategory, aestart first_of_month_not_before_first_dose, teae by_time_when_collected/last_dose_plus_days, pop efficacy, actual dm_actarm, arms ascending_dose_placebo_first, total none, rows standard_rows
    planted for: table on the efficacy set, by planned treatment; 1 decimals; window 30 days; column 'Placebo' of 32 subjects (1 added), 10 with an event, 2 with a serious one; the subject without an exposure end date completes its treatment, with a treatment and a study disposition record; causality events not serious
drawn (review-g2b-rfx-61/kit-9, number 9): written; 15 separated, 17 read, 15 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated'], ['ae.related.values', 'no_alternative']]
    gold: start dm_rfxstdtc, end last_ex_record_end, imput not_completed, disp disposition_event_by_subcategory, aestart first_of_month_not_before_first_dose, teae on_or_after_first_dose_date/last_dose_plus_days, pop efficacy, actual dm_actarm, arms protocol_order, total none, rows stated_rows
    planted for: table on the efficacy set, by planned treatment; 1 decimals; window 30 days; column 'Placebo' of 48 subjects (0 added), 39 with an event, 3 with a serious one; the subject without an exposure end date completes its treatment, with a treatment and a study disposition record; causality events not serious
drawn (review-g2b-rfx-64/kit-9, number 9): written; 15 separated, 16 read, 15 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated']]
    gold: start dm_rfxstdtc, end last_ex_start_date, imput first_day_of_month, disp disposition_event_by_subcategory, aestart first_of_month, teae on_or_after_first_dose_date/last_dose_plus_days, pop efficacy, actual dm_actarm, arms ascending_dose_placebo_first, total none, rows stated_rows
    planted for: table on the efficacy set, by planned treatment; 1 decimals; window 30 days; column 'Placebo' of 16 subjects (0 added), 13 with an event, 1 with a serious one; the subject without an exposure end date completes its treatment, with a treatment and a study disposition record; causality events not serious
drawn (review-g2b-rfx-66/kit-9, number 9): written; 16 separated, 17 read, 16 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated']]
    gold: start dm_rfxstdtc, end last_ex_end_date, imput first_day_of_month, disp disposition_event_by_subcategory, aestart first_of_month_not_before_first_dose, teae on_or_after_first_dose_date/last_dose_plus_days, pop efficacy, actual same_as_planned, arms ascending_dose_placebo_first, total active_arms, rows standard_rows
    planted for: table on the efficacy set, by planned treatment; 1 decimals; window 30 days; column 'Placebo' of 32 subjects (1 added), 18 with an event, 2 with a serious one; the subject without an exposure end date completes its treatment, and a second one without a study-level disposition record; causality events not serious
drawn (review-g2b-rfx-68/kit-4, number 4): written; 14 separated, 16 read, 14 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated'], ['ae.related.values', 'no_alternative']]
    gold: start dm_rfxstdtc, end last_ex_record_end, imput first_day_of_month, disp disposition_event, aestart first_of_month_not_before_first_dose, teae by_time_when_collected/no_end, pop efficacy, actual same_as_planned, arms protocol_order, total none, rows standard_rows
    planted for: table on the efficacy set, by planned treatment; 2 decimals; window none; column 'Placebo' of 32 subjects (0 added), 21 with an event, 1 with a serious one; the subject without an exposure end date completes its treatment; causality events not serious
drawn (review-g2b-rfx-72/kit-4, number 4): written; 16 separated, 17 read, 16 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated']]
    gold: start dm_rfxstdtc, end last_ex_end_date, imput first_day_of_month, disp disposition_event_by_subcategory, aestart first_of_month_not_before_first_dose, teae on_or_after_first_dose_date/last_dose_plus_days, pop efficacy, actual dm_actarm, arms ascending_dose_placebo_first, total active_arms, rows stated_rows
    planted for: table on the efficacy set, by planned treatment; 1 decimals; window 30 days; column 'Placebo' of 32 subjects (0 added), 26 with an event, 2 with a serious one; the subject without an exposure end date completes its treatment, with a treatment and a study disposition record; causality events serious
drawn (review-g2b-rfx-74/kit-9, number 9): written; 16 separated, 17 read, 16 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated']]
    gold: start dm_rfxstdtc, end last_ex_record_end, imput not_completed, disp disposition_event_by_subcategory, aestart first_of_month_not_before_first_dose, teae on_or_after_first_dose_date/last_dose_plus_days, pop efficacy, actual dm_actarm, arms protocol_order, total active_arms, rows stated_rows
    planted for: table on the efficacy set, by planned treatment; 1 decimals; window 30 days; column 'Placebo' of 32 subjects (1 added), 26 with an event, 2 with a serious one; the subject without an exposure end date completes its treatment, and a second one without a study-level disposition record; causality events not serious
drawn (review-g2b-rfx-79/kit-4, number 4): written; 16 separated, 17 read, 16 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated']]
    gold: start dm_rfxstdtc, end last_ex_record_end, imput not_completed, disp disposition_event, aestart first_of_month_not_before_first_dose, teae by_time_when_collected/last_dose_plus_days, pop efficacy, actual dm_actarm, arms protocol_order, total active_arms, rows standard_rows
    planted for: table on the efficacy set, by planned treatment; 1 decimals; window 30 days; column 'Placebo' of 16 subjects (1 added), 13 with an event, 1 with a serious one; the subject without an exposure end date completes its treatment; causality events not serious
drawn (review-g2b-rfx-83/kit-4, number 4): written; 16 separated, 17 read, 16 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated']]
    gold: start dm_rfxstdtc, end last_ex_end_date, imput first_day_of_month, disp disposition_event, aestart not_completed, teae on_or_after_first_dose_date/last_dose_plus_days, pop efficacy, actual dm_actarm, arms protocol_order, total active_arms, rows standard_rows
    planted for: table on the efficacy set, by planned treatment; 2 decimals; window 28 days; column 'Placebo' of 64 subjects (18 added), 34 with an event, 2 with a serious one; the subject without an exposure end date completes its treatment; causality events not serious
drawn (review-g2b-rfx-87/kit-9, number 9): written; 16 separated, 17 read, 16 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated']]
    gold: start dm_rfxstdtc, end last_ex_start_date, imput not_completed, disp disposition_event_by_subcategory, aestart first_of_month, teae on_or_after_first_dose_date/last_dose_plus_days, pop efficacy, actual dm_actarm, arms protocol_order, total active_arms, rows standard_rows
    planted for: table on the efficacy set, by planned treatment; 1 decimals; window 30 days; column 'Placebo' of 48 subjects (0 added), 39 with an event, 3 with a serious one; the subject without an exposure end date completes its treatment, and a second one without a study-level disposition record; causality events not serious
drawn (review-g2b-rfx-88/kit-9, number 9): written; 16 separated, 17 read, 16 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated']]
    gold: start dm_rfxstdtc, end last_ex_end_date, imput first_day_of_month, disp disposition_event, aestart not_completed, teae on_or_after_first_dose_date/last_dose_plus_days, pop efficacy, actual first_ex_treatment, arms ascending_dose_placebo_first, total none, rows stated_rows
    planted for: table on the efficacy set, by planned treatment; 2 decimals; window 30 days; column 'Placebo' of 32 subjects (0 added), 21 with an event, 1 with a serious one; the subject without an exposure end date completes its treatment; causality events serious
drawn (review-g2b-rfx-95/kit-4, number 4): written; 14 separated, 16 read, 14 applicable; applicable+unseparated none; read, not applicable: [['pop.safety.rule', 'unseparated'], ['ae.related.values', 'no_alternative']]
    gold: start dm_rfxstdtc, end ds_date_when_ex_missing, imput not_completed, disp disposition_event, aestart first_of_month_not_before_first_dose, teae on_or_after_first_dose_date/no_end, pop efficacy, actual first_ex_treatment, arms protocol_order, total none, rows stated_rows
    planted for: table on the efficacy set, by planned treatment; 1 decimals; window none; column 'Placebo' of 32 subjects (1 added), 26 with an event, 2 with a serious one; the subject without an exposure end date completes its treatment; causality events not serious
seconds: 492
```

## The kit of finding H3 that still failed, traced (diag.py)

Before the event of the subject who misses the visits (ADR-023, decision 2):

```text
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 python -B $SCRATCH/diag.py review-g2b-rfx-40 4 pop.efficacy.rule
gold pop.efficacy.rule {'rule': 'baseline_and_postbaseline', 'test': 'WEIGHT'} | others [{'rule': 'attended_visit', 'visit': 'WEEK 4'}]
population {'rule': 'efficacy'} grouping {'rule': 'actual'}
-- {'rule': 'attended_visit', 'visit': 'WEEK 4'}
  SFNXLECR-101-006 probes ['baseline_value_of_other_test_only'] planned MVK-482 10 mg once daily actual MVK-482: in False -> True; events [] -> []
  SFNXLECR-103-016 probes ['postbaseline_value_but_visit_missed'] planned MVK-482 10 mg once daily actual MVK-482: in True -> False; events [] -> []
  SFNXLECR-104-004 probes ['randomized_without_postbaseline_value'] planned MVK-482 5 mg once daily actual MVK-482: in False -> True; events [] -> []
  SFNXLECR-104-006 probes ['two_disposition_events'] planned MVK-482 5 mg once daily actual MVK-482: in True -> False; events [] -> []
```

## lifted.py

```python
"""The decision vectors of kits 1 to 10 of a seed, as the generator draws them, and which of the
three combinations that gen-2a's sampler refused (ADR-023, decision 6) each one has.

Usage: python lifted.py SEED
"""

import sys
from pathlib import Path

from specfirst.compile import catalog as catalogs
from specfirst.compile import house as houses
from specfirst.gen import decisions, kits, probes, study

ROOT = Path("/mnt/d/trial_work/specfirst-gen")
catalog = catalogs.load(catalogs.default_dir(ROOT))
house = houses.load(houses.default_dir(ROOT))
seed = sys.argv[1]
for number in range(1, 11):
    kit_seed = kits.kit_seed(seed, number)
    split = kits.split_of(number)
    scenario = decisions.SCENARIOS[kits.scenario_of(kit_seed, number)]
    design, _ = kits.sample_design(kit_seed, study.catalog_label(catalog), split, scenario)
    values = kits.draw_values(catalog, house, design, kit_seed, split, scenario["values"])
    names = probes.Parameters.of(design)
    record = values["disp.status.record"]
    read = values["ae.teae.end"]["rule"] == "last_dose_plus_days" and \
        values["trt.end.source"]["rule"] == "ds_date_when_ex_missing"
    lifted = []
    if values["ae.teae.start"]["rule"] == "at_or_after_first_dose_time" and \
            values["ae.start.imputation"]["rule"] != "not_completed":
        lifted.append("(a) emergence by the time of the first dose, a partial start "
                      f"completed ({values['ae.start.imputation']['rule']})")
    if record.get("subcategory") == names.treatment_subcategory:
        lifted.append("(b) the treatment record as the end-of-study record")
    if read and record.get("subcategory") == names.study_subcategory:
        lifted.append("(c) the study record, read through a window")
    print(f"kit {number}: table on the {values['tfl.population']['rule']} set; "
          f"{'; '.join(lifted) or 'none of the three'}")
```

## make_list.sh

```bash
#!/bin/bash
# The kits of the sweep after the fixes of the gen-2b review: the reviewer's forced vectors,
# kits 1 to 10 of two drawn sets, and every drawn kit 4 or 9 of the reviewer's 100 sets whose
# table is on the efficacy set by values with the treatment start from DM.RFXSTDTC (H3).
F=$SCRATCH
{
  for pair in lift-a-efficacy-0dec:4 lift-a-notbefore-rand-2dec:2 lift-b-efficacy-followup:9 \
      lift-b-safety-planned-2dec:6 lift-c-randomized-post:8 lift-c-firstex-0dec:2 \
      lift-c-efficacy-visit:4 firstex-2dec-protocol:6 planned-same-0dec-related:1 \
      armcd-map-recordend-serrel:2 laststart-bytime-2dec-actual:10 efficacy-values-active-total:4; do
    name=${pair%%:*}
    echo "$name review-g2b/$name ${pair##*:}"
  done
  for n in 1 2 3 4 5 6 7 8 9 10; do
    echo "drawn review-g2b-sweep/kit-$n $n"
    echo "drawn sweep-a/kit-$n $n"
  done
  grep '^HIT' $REVIEW_SCRATCH/sampler2.txt | awk '{print "drawn", $2, $3}'
} > $F/sweep.list
wc -l < $F/sweep.list
```

## job.sh

```bash
#!/bin/bash
# gen-2b fixes: write kits without R, four at a time, from a list of "NAME SEED NUMBER" lines
# (stdin), with the reviewer's one_kit.py; print one summary per kit.
# Usage: bash job.sh OUTNAME < list
set -u
cd /mnt/d/trial_work/specfirst-gen
. scripts/env.sh
F=$SCRATCH
K=/root/scratch-gen2b/fix-$1
mkdir -p $K
rm -rf $K/*
start=$(date +%s)
xargs -P 4 -L 1 bash -c 'python -B '"$F"'/one_kit.py "$0" "$1" "$2" '"$K"'/$(echo "$1" | tr / _) 2>'"$K"'/$(echo "$1" | tr / _).err' > $F/$1.jsonl
python $F/summarize.py $F/$1.jsonl
echo "seconds: $(( $(date +%s) - start ))"
```

## one_kit.py

```python
"""Reviewer's sweep (gen-2b review): write one kit without R, with some decisions of its vector
forced (the rest drawn as the generator draws them), and print what came out.

Usage: python one_kit.py NAME SEED NUMBER OUT   (NAME is a key of FORCED, or "drawn")
"""

import json
import sys
from pathlib import Path

from specfirst.gen import decisions, kits, probes

ROOT = Path("/mnt/d/trial_work/specfirst-gen")


def window(p, days=None):
    return {"rule": "last_dose_plus_days", "days": days or p["window_days"]}


def record(p, kind):
    return {"rule": "disposition_event_by_subcategory", "subcategory": p[f"{kind}_subcategory"]}


FORCED = {
    "drawn": lambda p: {},
    # (a) lifted: emergence by the time of the first dose, a partial start completed to a day
    "lift-a-efficacy-0dec": lambda p: {
        "ae.teae.start": {"rule": "at_or_after_first_dose_time"},
        "ae.start.imputation": {"rule": "first_of_month"},
        "tfl.population": {"rule": "efficacy"},
        "pop.efficacy.rule": {"rule": "attended_visit", "visit": p["visits"][-1]},
        "tfl.percent.format": {"rule": "one_decimal_always", "decimals": 0}},
    "lift-a-notbefore-rand-2dec": lambda p: {
        "ae.teae.start": {"rule": "at_or_after_first_dose_time"},
        "ae.start.imputation": {"rule": "first_of_month_not_before_first_dose"},
        "tfl.population": {"rule": "randomized"},
        "pop.randomized.rule": {"rule": "randomized_with_postbaseline", "test": p["tests"][-1]},
        "tfl.percent.format": {"rule": "one_decimal_zero_blank", "decimals": 2}},
    # (b) lifted: the treatment record as the end-of-study record
    "lift-b-efficacy-followup": lambda p: {
        "disp.status.record": record(p, "treatment"),
        "ae.teae.end": window(p, p["follow_up_days"]),
        "trt.end.source": {"rule": "ds_date_when_ex_missing"},
        "tfl.population": {"rule": "efficacy"},
        "pop.efficacy.rule": {"rule": "baseline_and_postbaseline", "test": p["tests"][0]}},
    "lift-b-safety-planned-2dec": lambda p: {
        "disp.status.record": record(p, "treatment"),
        "ae.teae.end": window(p),
        "trt.end.source": {"rule": "ds_date_when_ex_missing"},
        "tfl.population": {"rule": "safety"},
        "pop.safety.grouping": {"rule": "planned"},
        "tfl.percent.format": {"rule": "one_decimal_always", "decimals": 2}},
    # (c) lifted: the study participation record where the table reads the end-of-study date
    "lift-c-randomized-post": lambda p: {
        "disp.status.record": record(p, "study"),
        "ae.teae.end": window(p),
        "trt.end.source": {"rule": "ds_date_when_ex_missing"},
        "tfl.population": {"rule": "randomized"},
        "pop.randomized.rule": {"rule": "randomized_with_postbaseline", "test": p["tests"][0]}},
    "lift-c-firstex-0dec": lambda p: {
        "disp.status.record": record(p, "study"),
        "ae.teae.end": window(p, p["follow_up_days"]),
        "trt.end.source": {"rule": "ds_date_when_ex_missing"},
        "tfl.population": {"rule": "safety"},
        "pop.safety.grouping": {"rule": "actual"},
        "trt.actual.source": {"rule": "first_ex_treatment"},
        "tfl.percent.format": {"rule": "one_decimal_always", "decimals": 0}},
    "lift-c-efficacy-visit": lambda p: {
        "disp.status.record": record(p, "study"),
        "ae.teae.end": window(p),
        "trt.end.source": {"rule": "ds_date_when_ex_missing"},
        "tfl.population": {"rule": "efficacy"},
        "pop.efficacy.rule": {"rule": "attended_visit", "visit": p["visits"][0]}},
    # groupings, decimals, windows
    "firstex-2dec-protocol": lambda p: {
        "tfl.population": {"rule": "safety"},
        "pop.safety.grouping": {"rule": "actual"},
        "trt.actual.source": {"rule": "first_ex_treatment"},
        "tfl.columns.arms": {"rule": "protocol_order"},
        "tfl.columns.total": {"rule": "none"},
        "tfl.percent.format": {"rule": "one_decimal_zero_blank", "decimals": 2}},
    "planned-same-0dec-related": lambda p: {
        "tfl.population": {"rule": "safety"},
        "pop.safety.grouping": {"rule": "planned"},
        "trt.actual.source": {"rule": "same_as_planned"},
        "tfl.percent.format": {"rule": "one_decimal_always", "decimals": 0},
        "tfl.ae.summary.rows": {"rule": "stated_rows",
                                "rows": ["ANY", "RELATED", "FATAL", "FATAL_RELATED"]}},
    "armcd-map-recordend-serrel": lambda p: {
        "trt.planned.source": {"rule": "dm_armcd_map", "map": None},
        "tfl.population": {"rule": "randomized"},
        "pop.randomized.rule": {"rule": "all_randomized"},
        "ae.teae.end": window(p),
        "trt.end.source": {"rule": "last_ex_record_end"},
        "tfl.ae.summary.rows": {"rule": "stated_rows", "rows": [
            "ANY", "SERIOUS", "SERIOUS_RELATED", "DOSE_MODIFIED", "FATAL"]}},
    "laststart-bytime-2dec-actual": lambda p: {
        "tfl.population": {"rule": "safety"},
        "pop.safety.grouping": {"rule": "actual"},
        "trt.actual.source": {"rule": "dm_actarm"},
        "trt.end.source": {"rule": "last_ex_start_date"},
        "ae.teae.end": window(p, p["follow_up_days"]),
        "ae.teae.start": {"rule": "at_or_after_first_dose_time"},
        "tfl.percent.format": {"rule": "one_decimal_always", "decimals": 2}},
    "efficacy-values-active-total": lambda p: {
        "tfl.population": {"rule": "efficacy"},
        "pop.efficacy.rule": {"rule": "baseline_and_postbaseline", "test": p["tests"][-1]},
        "tfl.columns.total": {"rule": "active_arms", "control": None},
        "tfl.percent.format": {"rule": "one_decimal_zero_blank", "decimals": 1}},
}


def main() -> int:
    name, seed, number, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), Path(sys.argv[4])
    original = kits.draw_values

    def forced(catalog, house, design, seed_, split, given):
        values = original(catalog, house, design, seed_, split, given)
        parameters = probes.Parameters.of(design).as_record()
        for key, value in FORCED[name](parameters).items():
            if key == "trt.planned.source" and value.get("rule") == "dm_armcd_map":
                value = decisions.variants(catalog.entry(key), design, parameters)[1]
            values[key] = value
        total = values.get("tfl.columns.total")
        if total and total["rule"] == "active_arms":
            total["control"] = decisions.placebo_label(design, values)
        return values

    if name != "drawn":
        kits.draw_values = forced
    try:
        manifest = kits.generate(ROOT, seed, out, kits.split_of(number), with_r=False,
                                 number=number)
    except kits.KitError as error:
        print(json.dumps({"name": name, "seed": seed, "number": number, "written": False,
                          "error": str(error)[-1500:]}))
        return 0
    summary = manifest["properties"]["identifiability"]
    with open(out / kits.IDENTIFIABILITY, encoding="ascii") as handle:
        matrix = json.load(handle)
    values = {item["id"]: item["gold"] for item in matrix["decisions"]}
    read_not_applicable = [(item["id"], item["identifiable"]) for item in matrix["decisions"]
                           if item["read"] and not item["applicable"]]
    from specfirst.gen import present, study
    print(json.dumps({"name": name, "seed": seed, "number": number, "written": True,
                      "planted_for": present.planted_for(study.read_probes(out)),
                      "separated": len(summary["separated"]), "read": summary["read"],
                      "applicable": summary["applicable"],
                      "applicable_and_unseparated": summary["applicable_and_unseparated"],
                      "unseparated_read": summary["unseparated_read"],
                      "read_not_applicable": read_not_applicable,
                      "gold": values}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

## summarize.py

```python
"""One line per kit of the reviewer's sweep (job2.jsonl)."""
import json
import sys

for line in open(sys.argv[1], encoding="ascii"):
    r = json.loads(line)
    head = f"{r['name']} ({r['seed']}, number {r['number']}):"
    if not r["written"]:
        print(f"{head} NOT WRITTEN: {r['error'][-700:]}")
        continue
    g = r["gold"]
    print(f"{head} written; {r['separated']} separated, {r['read']} read, {r['applicable']} "
          f"applicable; applicable+unseparated {r['applicable_and_unseparated'] or 'none'}; "
          f"read, not applicable: {r['read_not_applicable']}")
    print(f"    gold: start {g['trt.start.source']}, end {g['trt.end.source']}, imput "
          f"{g['trt.date.imputation']}, disp {g['disp.status.record']}, aestart "
          f"{g['ae.start.imputation']}, teae {g['ae.teae.start']}/{g['ae.teae.end']}, pop "
          f"{g['tfl.population']}, actual {g['trt.actual.source']}, arms {g['tfl.columns.arms']}, "
          f"total {g['tfl.columns.total']}, rows {g['tfl.ae.summary.rows']}")
    print(f"    planted for: {r['planted_for'][:330]}")
```

## diag.py

```python
"""Which subjects of the twin move in or out of the analysis set between the gold value of a
decision and another value of `verify.options`, by the hand calculation (gen-2b fixes).

Usage: python diag.py SEED NUMBER ENTRY
"""

import sys
from pathlib import Path

from specfirst.compile import catalog as catalogs
from specfirst.compile import house as houses
from specfirst.gen import decisions, kits, probes, reference, sdtm, study, verify

ROOT = Path("/mnt/d/trial_work/specfirst-gen")
seed_text, number, entry_id = sys.argv[1], int(sys.argv[2]), sys.argv[3]
catalog = catalogs.load(catalogs.default_dir(ROOT))
house = houses.load(houses.default_dir(ROOT))
seed = kits.kit_seed(seed_text, number)
split = kits.split_of(number)
scenario = decisions.SCENARIOS[kits.scenario_of(seed, number)]
design, _ = kits.sample_design(seed, study.catalog_label(catalog), split, scenario)
values = kits.draw_values(catalog, house, design, seed, split, scenario["values"])
people, log = study.simulate(design, catalog, seed, "twin", values=values)
tables = sdtm.build(design, people)
parameters = next(line["parameters"] for line in log)
entry = catalog.entry(entry_id)
choices = verify.options(entry, design, parameters, values)
print("gold", entry_id, choices[0], "| others", choices[1:])
print("population", values["tfl.population"], "grouping", values["pop.safety.grouping"])
probe_of = {s.usubjid: s.probes for s in people}
flag = {"safety": "in_safety", "randomized": "in_randomized",
        "efficacy": "in_efficacy"}[values["tfl.population"]["rule"]]
by = [{p.usubjid: p for p in reference.people(tables, {**values, entry_id: c})} for c in choices]
for other in range(1, len(choices)):
    print("--", choices[other])
    for key in sorted(by[0]):
        a, b = by[0][key], by[other][key]
        if getattr(a, flag) != getattr(b, flag) or [e["emergent"] for e in a.events] != [
                e["emergent"] for e in b.events]:
            print(f"  {key} probes {probe_of.get(key)} planned {a.planned} actual {a.actual}: "
                  f"in {getattr(a, flag)} -> {getattr(b, flag)}; events "
                  f"{[(e['emergent'], sorted(e['kinds'])) for e in a.events]} -> "
                  f"{[(e['emergent'], sorted(e['kinds'])) for e in b.events]}")
```
