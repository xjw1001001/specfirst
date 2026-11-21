# What is the treatment start date? (`trt.start.source`)

The treatment start date anchors study days, baseline, post-baseline, treatment emergence and
who counts as dosed. Another source moves all of them for the subjects it affects.

## Where it is stated

- SAP: general definitions ("date of first dose", "treatment start date") and the section on
  exposure or extent of exposure.
- Protocol: study treatment administration; schedule of assessments footnotes on first dosing.
- Usually only "date of first dose of study treatment" is written, with no detail on records.

## Words to look for

- `first_ex_with_dose`: "date of the first dose of study treatment", "first dose actually
  taken", "first non-zero dose", "records with no drug given are ignored".
- `first_ex_record`: "earliest dosing record", "start date of the first exposure record",
  "first entry of the drug administration log, whatever the dose".
- `dm_rfxstdtc`: "date of first exposure as recorded in demographics", "reference first
  treatment date", or the variable RFXSTDTC named directly.
- A protocol written to ICH M11 says "participant" for subject and "study intervention" for
  study treatment; read them as the same words.

## Traps

- Plain "first dose" means `first_ex_with_dose`. Choose `first_ex_record` only when the text
  says that any record counts, including one with a dose of zero.
- Under `first_ex_with_dose` a placebo record with a dose of zero still has a dose. Do not
  read "dose above zero" as leaving out placebo subjects.
- RFXSTDTC (first exposure) is not RFSTDTC (reference start). "Day 1" and the randomization
  date are matters for `date.studyday.origin`, not for this entry.
- This entry gives a date. Comparisons with the time of the first dose are decided in
  `ae.teae.start` and `bds.baseline.rule`.
- Silent documents: use the house default `first_ex_with_dose` and cite the house standard.
