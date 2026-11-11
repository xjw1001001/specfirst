# Draft: issue for cdisc-org/analysis-results-standard

Status: draft, not posted. PLAN.md section 14 asks real-2 for this text and
section 2.1, rule 6, says who sends it: the owner, after approving the exact
words. Nothing below has been sent to anyone.

For the owner, before posting:

- The plan (E3, section 14) speaks of 23 or 24 results. The check of real-2
  finds 25: the 24 of E3 and one first quartile (ADR-002, decision 6).
- The numbers in the table come from `specfirst check cdiscpilot01` on the
  ADaM datasets this repository builds, which equal Pilot 7's reference
  ADaM cell by cell. `kits/cdiscpilot01/gold/exceptions.yaml` has the same
  25 with their proofs.
- The text names the two repositories and commits the numbers rest on, and
  nothing of this project.

The text to post starts below the line.

---

Title: Common Safety Displays (ARS v1): 25 embedded results do not agree with the CDISCPILOT01 ADaM

Thank you for the ARS v1 example. We used it as a test case: we ran its 31
analyses on the CDISCPILOT01 ADaM datasets with two separate
implementations, one in Python and one in R, and compared every embedded
`rawValue` with what the data give. 3,710 of the 3,735 embedded results
agree. 25 do not, and we think they are worth correcting in the example.

What was compared

- Example: `workfiles/examples/ARS v1/Common Safety Displays.json` at commit
  `2c9b4b68724386e8f91dc576724855af7fafac65` (SHA-256
  `90358dd60d687332f2138aa50435b4050fa91be3f52958169229daa269fe31b3`).
- Data: ADSL, ADAE and ADVS of CDISCPILOT01 as published in
  `RConsortium/submissions-pilot7-synthetic-data`, folder
  `cdiscpilot01/data/adam`, at commit
  `213cb6ab3adc51abe4295cbbc546c0e6d46c3df8`. ADSL has 254 subjects: 86
  placebo, 84 low dose, 84 high dose.
- Quartiles and medians by the SAS default (QNTLDEF=5). With that
  definition those of the example agree, except the two in the table.
- A value counts as agreeing when it equals the embedded raw value at the
  precision the example prints, and at least at the decimals of the
  operation's `resultPattern`.

The 25 results

| Analysis | Operation | Groups | Embedded `rawValue` | Embedded `formattedValue` | From the ADaM |
| --- | --- | --- | --- | --- | --- |
| `An03_01_Age_Summ_ByTrt` | Q1 | Xanomeline High Dose | 70 | 70.0 | 70.5 |
| `An03_04_Ethnic_Summ_ByTrt` | n | Xanomeline Low Dose; Hispanic or Latino | 3 | 3 | 6 |
| `An03_04_Ethnic_Summ_ByTrt` | n | Xanomeline Low Dose; Not Hispanic or Latino | 81 | 81 | 78 |
| `An03_04_Ethnic_Summ_ByTrt` | n | Xanomeline High Dose; Hispanic or Latino | 6 | 6 | 3 |
| `An03_04_Ethnic_Summ_ByTrt` | n | Xanomeline High Dose; Not Hispanic or Latino | 78 | 78 | 81 |
| `An03_04_Ethnic_Summ_ByTrt` | % | Xanomeline Low Dose; Hispanic or Latino | 3.5714285714285716 | (  3.6) | 7.142857143 |
| `An03_04_Ethnic_Summ_ByTrt` | % | Xanomeline Low Dose; Not Hispanic or Latino | 96.42857142857143 | ( 96.4) | 92.85714286 |
| `An03_04_Ethnic_Summ_ByTrt` | % | Xanomeline High Dose; Hispanic or Latino | 7.142857142857143 | (  7.1) | 3.571428571 |
| `An03_04_Ethnic_Summ_ByTrt` | % | Xanomeline High Dose; Not Hispanic or Latino | 92.85714285714286 | ( 92.9) | 96.42857143 |
| `An03_05_Race_Summ_ByTrt` | n | Xanomeline Low Dose; American Indian or Alaska Native | 1 | 1 | 0 |
| `An03_05_Race_Summ_ByTrt` | n | Xanomeline Low Dose; Black or African American | 9 | 9 | 6 |
| `An03_05_Race_Summ_ByTrt` | n | Xanomeline Low Dose; White | 74 | 74 | 78 |
| `An03_05_Race_Summ_ByTrt` | n | Xanomeline High Dose; American Indian or Alaska Native | 0 | 0 | 1 |
| `An03_05_Race_Summ_ByTrt` | n | Xanomeline High Dose; Black or African American | 6 | 6 | 9 |
| `An03_05_Race_Summ_ByTrt` | n | Xanomeline High Dose; White | 78 | 78 | 74 |
| `An03_05_Race_Summ_ByTrt` | % | Xanomeline Low Dose; American Indian or Alaska Native | 1.1904761904761905 | (  1.2) | 0 |
| `An03_05_Race_Summ_ByTrt` | % | Xanomeline Low Dose; Black or African American | 10.714285714285714 | ( 10.7) | 7.142857143 |
| `An03_05_Race_Summ_ByTrt` | % | Xanomeline Low Dose; White | 88.0952380952381 | ( 88.1) | 92.85714286 |
| `An03_05_Race_Summ_ByTrt` | % | Xanomeline High Dose; American Indian or Alaska Native | 0 | (  0.0) | 1.19047619 |
| `An03_05_Race_Summ_ByTrt` | % | Xanomeline High Dose; Black or African American | 7.142857142857143 | (  7.1) | 10.71428571 |
| `An03_05_Race_Summ_ByTrt` | % | Xanomeline High Dose; White | 92.85714285714286 | ( 92.9) | 88.0952381 |
| `An03_06_Height_Summ_ByTrt` | Mean | Xanomeline Low Dose | 165.8202381 | 165.8 | 163.4333333 |
| `An03_06_Height_Summ_ByTrt` | Mean | Xanomeline High Dose | 163.4333333 | 163.4 | 165.8202381 |
| `An03_06_Height_Summ_ByTrt` | Median | Xanomeline Low Dose | 162.2 | 162.2 | 162.6 |
| `An07_10_SocPt_Comp_ByTrt_PlacLow` | p-value | VASCULAR DISORDERS; WOUND HAEMORRHAGE | (empty) | (none) | no result |

What we see in them

1. Twenty-two values are exchanged between the two active arms: the counts
   and percents of ethnicity and of three race groups, and the two means of
   height. Each embedded value of the low dose arm is the value the data
   give for the high dose arm, and the reverse. The other results of the
   same analyses agree (placebo, the other race groups, and for height the
   standard deviations, the first and third quartiles, the minimum and the
   maximum), and so do the chi-square p-values of ethnicity and race, which
   do not change when two arms are exchanged. The CSR in the same folder
   supports the data: Table 14-2.01 prints 3, 6 and 3 Hispanic or Latino
   subjects for placebo, low dose and high dose, and mean heights of 163.4
   for low dose and 165.8 for high dose.
2. The median of height in the low dose arm is embedded as 162.2. The 41st
   to the 45th of the 84 sorted heights are all 162.6, so every quantile
   definition gives 162.6, and CSR Table 14-2.01 prints 162.6.
3. The first quartile of age in the high dose arm is embedded as 70. With
   84 subjects the SAS default is the mean of the 21st and the 22nd age,
   which are 70 and 71: 70.5. The example's other quartiles follow that
   definition; in the same arm its third quartile of height, 172.85, is the
   mean of the 63rd and the 64th value.
4. `An07_10_SocPt_Comp_ByTrt_PlacLow` has one result, for WOUND HAEMORRHAGE,
   with an empty `rawValue` and no `formattedValue`. No subject of the
   placebo or the low dose arm has a treatment-emergent event with that
   term, so there is no table to test.

A smaller observation, in case it is not intended: the four Fisher analyses
by organ class and by preferred term (`An07_09_Soc_Comp_ByTrt_*`,
`An07_10_SocPt_Comp_ByTrt_*`) embed one result each (VASCULAR DISORDERS,
and WOUND HAEMORRHAGE within it), where the matching summary analyses have
23 organ classes and 230 terms.

We are glad to share the full comparison (one row per embedded result, with
the value from the data) or to open a pull request with corrected values,
whichever helps.
