# Which record is analyzed when several fall in one analysis visit? (`bds.window.tiebreak`)

The answer picks the one record per subject, parameter and analysis visit that enters the
by-visit summaries when repeats or windowing put several records in one visit.

## Where it is stated

- SAP: section on analysis visits or visit windows, right after the window table; sometimes
  under handling of multiple or repeated measurements.
- Protocol: almost never.
- Often unstated when analyses are by nominal visit.

## Words to look for

- `closest_then_earlier`: "the value closest to the target day is used; if two are equally
  close, the earlier one".
- `closest_then_later`: "the value closest to the scheduled day; in case of a tie, the later
  one" or "the most recent one".
- `last_record`: "the last value within the window", "the latest assessment in the visit
  window is used".

## Traps

- Read the tie rule apart from the main rule. "Closest to the target day" with no tie rule
  leaves the tie unstated: take the tie rule of the house standard, and say that the
  tie rule comes from it.
- Only non-missing values compete. Earlier and later are by date and time, and the sequence
  number breaks a remaining tie.
- Averages of repeated measurements, or the worst value in the window, match no alternative;
  report the passage.
- Whether records of unscheduled visits take part at all is `bds.unscheduled.use`.
- Silent documents: use the house default and cite the house standard.
