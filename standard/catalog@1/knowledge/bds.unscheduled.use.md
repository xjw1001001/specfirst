# Do records of unscheduled visits compete for baseline and for analysis visits? (`bds.unscheduled.use`)

The answer decides whether a measurement taken at an unscheduled visit can become the
baseline or the analyzed record of a visit, or is kept out of both.

## Where it is stated

- SAP: section on analysis visits or visit windows; general definition of baseline; handling
  of repeated or unscheduled assessments.
- Protocol: rarely; it may say when unscheduled visits can occur.
- Often split over two places: one sentence for baseline, another for by-visit summaries.

## Words to look for

- `compete`: "all assessments, including unscheduled ones, are considered", "scheduled and
  unscheduled values are used for baseline and for visit windows".
- `excluded`: "unscheduled assessments are not used as baseline or in by-visit summaries",
  "only scheduled visits are analyzed", "unscheduled values appear in listings only".

## Traps

- One answer covers baseline and analysis visits together. Many SAPs allow unscheduled
  values for baseline but leave them out of by-visit tables; that mixed rule matches no
  alternative. Report both sentences.
- Unscheduled here means a visit without a planned study day. Do not assume that an early
  termination or end-of-treatment visit is unscheduled in that sense.
- When records keep their collected visit (`bds.window.table`), a record of an unscheduled
  visit gets no analysis visit whatever is chosen here; this entry then still decides
  whether it can be baseline.
- Use of unscheduled values in listings is outside this entry.
- Silent documents: use the house default `compete` and cite the house standard.
