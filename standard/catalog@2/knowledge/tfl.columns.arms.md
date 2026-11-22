# In which order are the treatment columns? (`tfl.columns.arms`)

The answer fixes the left-to-right order of the treatment columns of the table. It is given
once per table family; the counts do not change.

## Where it is stated

- SAP: general conventions for tables ("treatment groups are displayed in the order ..."),
  and the column headers of the table shells.
- Protocol: the order in which the study design section lists the arms.
- Often shown only by the shells.

## Words to look for

- `ascending_dose_placebo_first`: "placebo, then active doses from lowest to highest",
  "placebo first, followed by increasing dose", shells headed Placebo, Low Dose, High Dose.
- `protocol_order`: "in the order of the treatment arms in the protocol", "as listed in the
  study design", shells that follow the protocol's list of arms where it is not dose order.

## Traps

- "Active treatment first, then placebo" is `protocol_order` only if the protocol lists the
  arms that way. Otherwise it matches no alternative; report the passage.
- When the protocol lists placebo first and the doses ascending, both alternatives give the
  same order. Pick the one the text states.
- An active comparator has no place in a dose order. If the study has one and the text does
  not say where its column goes, report that.
- The total column is `tfl.columns.total`, not this entry.
- Silent documents: use the house default and cite the house standard.
