# Is there an end-of-treatment record? (`bds.eot.record`)

The answer decides whether each subject and parameter gets one extra record, with the
analysis visit End of Treatment, that the by-visit tables can show as a row.

## Where it is stated

- SAP: section on analysis visits or on handling of missing data; table shells that list an
  "End of Treatment" or "Last on-treatment value" row.
- Protocol: rarely; the schedule may have an end-of-treatment visit, which is another thing.
- Often visible only from the visit list of the shells.

## Words to look for

- `last_on_treatment_value`: "the end-of-treatment value is the last post-baseline value on
  or before the date of last dose", "last on-treatment observation", "last observed value on
  treatment" shown as its own time point.
- `none`: no derived end-of-treatment time point; "only scheduled visits are summarized".

## Traps

- A collected end-of-treatment visit in the schedule of assessments is not this derived
  record. The derived record repeats an existing value under the analysis visit End of
  Treatment.
- "Endpoint" or "last observation carried forward" rows that take the last post-baseline
  value whatever the treatment end date are another rule; report the passage.
- The value must be post-baseline and on or before the treatment end date
  (`trt.end.source`). A subject without a treatment end date takes the last post-baseline
  value.
- An End of Treatment row in `tfl.vs.scope` needs `last_on_treatment_value`; check the two
  answers against each other.
- Silent documents: use the house default `last_on_treatment_value` and cite the house
  standard.
