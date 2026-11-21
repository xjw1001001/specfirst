# Which treatment groups the safety analyses? (`pop.safety.grouping`)

The answer decides under which column a subject counts in every output on the safety set,
when the treatment received differs from the treatment assigned.

## Where it is stated

- SAP: section on analysis sets, usually the sentence after the definition of the safety set.
- SAP: general conventions on treatment groups; titles or footnotes of the safety shells.
- Protocol: statistical section, safety analyses. Often stated, sometimes only implied.

## Words to look for

- `actual`: "as treated", "according to the treatment actually received", "by actual
  treatment", "by treatment received".
- `planned`: "as randomized", "according to the randomized treatment", "by planned
  treatment", "by assigned treatment", when said of the safety analyses.

## Traps

- "As randomized" said of the efficacy or intent-to-treat analyses says nothing about safety.
  Outputs on another analysis set group by planned treatment whatever is chosen here.
- This entry says which treatment is used, not how the actual treatment is found; that is
  `trt.actual.source`.
- A sentence that all analyses use the randomized treatment does cover safety: choose
  `planned`.
- If protocol and SAP disagree, cite both passages; the SAP, as the later and more detailed
  document, normally governs the analysis.
- Silent documents: use the house default `actual` and cite the house standard.
