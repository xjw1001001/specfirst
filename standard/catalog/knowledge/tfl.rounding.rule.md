# How are displayed numbers rounded? (`tfl.rounding.rule`)

The rule changes a displayed mean, percentage or other statistic only when its exact value
lies halfway between two values that can be displayed. It is given once per table family.

## Where it is stated

- SAP: general conventions for tables or for numerical precision.
- Protocol: never.
- Almost always unstated; "rounded to one decimal" says how far, not how.

## Words to look for

- `half_away_from_zero`: "conventional rounding", "a final 5 is rounded up", "rounded away
  from zero".
- `half_even`: "round half to even", "banker's rounding", "a final 5 is rounded to the
  nearest even digit".

## Traps

- For positive numbers "round half up" and half away from zero agree; for negative numbers
  such as changes from baseline they differ. Treat plain "half up" as `half_away_from_zero`
  and say so in the answer.
- A number is rounded once, from full precision to the displayed decimals. A text that
  rounds a value and then computes from the rounded value describes something else; report
  the passage.
- Truncation ("values are cut to one decimal") matches no alternative.
- The number of decimals is not decided here (`tfl.decimals.rule`, `tfl.percent.format`).
- Silent documents: use the house default `half_away_from_zero` and cite the house standard.
