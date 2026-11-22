# Which parameters and analysis visits does the vital signs table show? (`tfl.vs.scope`)

The two lists fix the parameters and the analysis visits of the vital signs table by visit,
each in the order given. Anything left out of a list is not shown.

## Where it is stated

- SAP: vital signs section ("the following vital signs will be summarized by visit").
- SAP table shells: parameter headings and visit rows of the vital signs table.
- Protocol: schedule of assessments (when vital signs are measured) and the vital signs
  section (which measurements are taken).

## Words to look for

- `stated_lists`: a sentence or shell that names the measurements and the time points. The
  slot `parameters` holds the parameter codes in order (systolic blood pressure SYSBP,
  diastolic blood pressure DIABP, pulse rate PULSE, weight WEIGHT). The slot `visits` holds
  the analysis visit names in order, such as Baseline, Week 2, End of Treatment.

## Traps

- The schedule of assessments says when vital signs are collected, not which visits the
  table shows. Use it only if the SAP says "at each scheduled visit", and then list the
  visits that the schedule names.
- Baseline and End of Treatment are analysis visits and must be listed to appear. An End of
  Treatment row needs the end-of-treatment record to exist (`bds.eot.record`).
- Visit names must equal the analysis visit names: those of the window table when
  `bds.window.table` has one, otherwise the collected visit names.
- "All vital signs" or "each visit" with no names leaves the slots open; report that.
- Silent documents: when the house standard states no default for this entry, do not guess
  the lists; a person must be asked.
