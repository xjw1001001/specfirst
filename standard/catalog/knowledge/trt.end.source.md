# What is the treatment end date? (`trt.end.source`)

The treatment end date bounds the duration of exposure, the end-of-treatment record and any
treatment emergence window that is counted from the last dose.

## Where it is stated

- SAP: general definitions ("date of last dose") and the section on extent of exposure, where
  duration is often given as last dose date minus first dose date plus one.
- SAP: section on missing dates, for a fallback when the last dose date is unknown.
- Protocol: definitions of end of treatment; rarely more precise than "last dose".

## Words to look for

- `last_ex_end_date`: "date of last dose", "date of last administration", "end date of the
  last dosing record", "treatment stop date".
- `last_ex_start_date`: "start date of the last dosing record", "date the last cycle or
  infusion was started", "start of the last dosing interval".
- `ds_date_when_ex_missing`: a fallback sentence such as "if the date of last dose is missing,
  the date of study completion or discontinuation is used".

## Traps

- With one record per dose, start and end date agree; the first two alternatives differ only
  when a record spans several days. Plain "date of last dose" means `last_ex_end_date`.
- The fallback of `ds_date_when_ex_missing` applies only when no exposure record of the
  subject has an end date, and it takes the date of the end-of-study record
  (`disp.status.record`).
- A fallback to the last visit, the last contact or a data cut-off date matches no
  alternative. Report the passage instead of picking the nearest one.
- The date of an "end of treatment visit" is a visit date, not the treatment end date.
- Silent documents: use the house default `last_ex_end_date` and cite the house standard.
