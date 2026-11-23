# gen-2b The probes follow the decisions of a kit: report

Date: 2026-11-23. Branch: `track/gen`, from `main` `34bbc14`. The part
that the owner's answer of 2026-11-17 on finding G1 of the gen-2a review
booked before the gate of the full gen-2 (ADR-007, "The owner's answer on
decision 6"); the owner chose on 2026-11-23 that it be done now. Choices:
docs/decisions/ADR-023.md.

## Verdict

GATE_VERDICT

## What changed

- Order (section 6.4, S1 before S3). `kits._generate` draws the design,
  then the decision vector (`kits.draw_values`: the stream of the first
  vector of gen-2a, so no vector of any seed changes), then generates the
  data for that vector (`study.generate(..., values=...)`), then gold. A
  study of its own draws its vector from its seed (`study.own_values`); the
  gate gen-1a gives seed n the decisions of scenario n where the design
  can carry them (`gate.values_for`). `study.json` names the vector.
- The recipes follow the vector (`specfirst.gen.probes`):
  - `statistic_at_rounding_half`: the column of the placebo arm under the
    kit's analysis set, grouping, sources of treatment and decimals, found
    by the hand calculation (`probes.spared_column`); subjects of the arm
    added until its size is a multiple of 8, 16 or 32 (0, 1, 2 decimals);
    then the counts with a serious event and with any event set at a
    rounding half (`probes.is_rounding_half(count, total, decimals)`);
  - `no_exposure_end_date`: the subject completes its treatment where the
    analysis set asks for a post-baseline value or a later visit;
  - the window probes: built around the kit's own window
    (`Parameters.of_kit`);
  - `ae_with_each_causality_value`: serious events where the table shows
    serious related events and not related events;
  - the subject dosed off plan in a design with two arms: the placebo arm
    is the arm the table does not group by.
- `probes.REACHES` keeps the conditions of kind (a) only (ADR-023, decision
  4); the per-pair conditions and `_ANALYZED` are gone; `tfl.columns.arms`
  reads the new parameter `placebo_first`.
- `kits.generate` writes no kit in which a read decision that data could
  separate is unseparated, and draws no second vector (`MAX_ATTEMPTS` and
  `vectors_drawn_before` are gone). `decisions.fits` is gone: the owner
  lifted its three limits (ADR-023, decision 6), and three recipes follow
  them: a second subject of the partial start in the month of the first
  dose, whose first dose has no time; a treatment and a study disposition
  record for the subject without an exposure end date; a second such
  subject without a study-level disposition record (per recommendation,
  pending SME review).
- The gates gen-2a and gen-2b (one list of checks, `gates._gen2_checks`)
  plant the failure: `gate2.planted_unfit_build` (the generator refuses kit
  9 built with the probes of gen-2a) and `gate2.planted_unfollowed` (the
  twin of kit 9 made with them is unfit: the rounding rule and the source of
  the treatment end date applicable and unseparated).
- `present` decides the count probe again from the data under the logged
  vector; `present.planted_for` says what a twin's probes were made for (in
  the logs of the gates gen-1a and gen-2a/2b).
- `score.kit` reads the parameters of a kit from its log of probes.
- `GENERATOR` is `gen-2b.1`.

GATES_AND_EVIDENCE
