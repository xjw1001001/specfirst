# How are percentages displayed? (`tfl.percent.format`)

The answer decides what a cell with a count of zero shows: the count alone, or the count
with its percentage. It is given once per table family.

## Where it is stated

- SAP: general conventions for tables and the notes to the table shells.
- Protocol: never.
- Often unstated, or visible only in the layout of a shell.

## Words to look for

- `one_decimal_zero_blank`: "percentages are shown to one decimal place; no percentage is
  shown for a count of zero", shell cells written "0" where others are "xx (xx.x)".
- `one_decimal_always`: "percentages are shown to one decimal place" together with zero
  cells written "0 (0.0)", or "a percentage is always displayed".

## Traps

- Both alternatives have one decimal. A SAP that asks for whole-number percentages or for
  two decimals matches no alternative; report the passage.
- "One decimal place" alone does not say what happens at zero. Use the house default then,
  and say that only the decimal was stated.
- Special displays such as "<0.1" for small percentages, or "100" without a decimal, are not
  covered; report them.
- A shell is a layout sketch: "xx (xx.x)" in every cell does not prove that a zero count gets
  a percentage.
- Silent documents: use the house default `one_decimal_zero_blank` and cite the house
  standard.
