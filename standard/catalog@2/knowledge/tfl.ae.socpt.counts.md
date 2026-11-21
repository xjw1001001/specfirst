# Does the table count subjects, events or both? (`tfl.ae.socpt.counts`)

The answer decides whether each cell of the adverse event table by system organ class and
preferred term shows only subjects with their percentage, or also the number of events.

## Where it is stated

- SAP: adverse event section ("number and percentage of subjects", "number of events").
- SAP table shells: the cell pattern and column sub-headers, such as "n (%)" or "n (%) E".
- Protocol: statistical section, in general words.

## Words to look for

- `subjects`: "number and percentage of subjects with at least one event", "a subject is
  counted once per preferred term", cell pattern "n (%)".
- `subjects_and_events`: "number of subjects, percentage and number of events", cell pattern
  "n (%) E", "the number of occurrences is also shown".

## Traps

- "Incidence of adverse events" still means subjects. Only an explicit number of events or
  occurrences in the same table selects `subjects_and_events`.
- A subject with several events of one term counts once as a subject and once per event in
  the number of events. The percentage is of subjects.
- A separate table of event counts or of exposure-adjusted rates is another output. A table
  of events only matches no alternative; report the passage.
- Under `subjects_and_events` the number of events follows the subjects and their percentage
  in each cell.
- Silent documents: use the house default and cite the house standard.
