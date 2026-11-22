# How are records assigned to analysis visits? (`bds.window.table`)

The answer decides under which analysis visit a post-baseline record is summarized, and
whether a record taken off schedule moves to another visit or drops out.

## Where it is stated

- SAP: section on analysis visits or visit windows, usually a table with visit, target day
  and day range; sometimes an appendix.
- Protocol: schedule of assessments, with allowed visit windows such as "+/- 3 days".
- When the SAP has no window table, analyses are usually by the collected (nominal) visit.

## Words to look for

- `protocol_windows`: "assessments are assigned to analysis visits by the windows below",
  with a table that gives a lower and an upper study day per visit. The slot `windows`
  copies each row: visit, target day, first day and last day.
- `midpoint_windows`: "assigned to the visit with the closest target day", "windows run from
  midpoint to midpoint between scheduled visits". The slot `visits` lists each visit with its
  target day.
- `nominal_visit`: "summarized by nominal visit", "by scheduled visit as collected", "no
  windowing will be applied".

## Traps

- The protocol's allowed deviation ("Week 4 +/- 3 days") is a scheduling tolerance for sites.
  It is an analysis window only when a document says that records are assigned to visits by
  it; then target day 29 +/- 3 gives the days 26 to 32.
- Under `protocol_windows` both limits belong to the window, and a record in a gap between
  windows gets no analysis visit. Copy the limits as written; do not close gaps.
- Under `midpoint_windows` the first window starts on study day 2, the last has no upper
  limit, and a tie goes to the earlier visit. Under `nominal_visit` a record of an
  unscheduled visit has no analysis visit.
- Target days follow the study day convention (`date.studyday.origin`): with the first dose
  on day 1, Week 2 is day 15. Use the days the SAP gives; do not compute them from weeks.
- Silent documents: use the house default and cite the house standard.
