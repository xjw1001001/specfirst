# Evidence scripts

Feasibility spikes run on 2026-11-10 and 11 against public sources. They
back rows E1 to E5 and E24 to E27 of PLAN.md. Section 3.1 of PLAN.md gives
the commands and the expected output. All seven were rerun from this folder
on 2026-11-11 and gave the expected output.

| File | Evidence | What it shows |
| --- | --- | --- |
| `run_yamaa_project.py` | E1 | Runs a yamaa project (the CDISCPILOT01 ADaM specs of R Consortium Pilot 7) and saves the datasets. |
| `compare_adam.py` | E1 | Compares the built ADaM with the reference, cell by cell. Expect 9,119,605 cells and 0 mismatches. |
| `ars_spike.py` | E2 to E5 | A generic interpreter for the CDISC ARS v1 example. Expect 3,711 matches, 23 differences and 1 not computed out of 3,735 embedded results. Takes about 3 minutes. |
| `csr_demog_spike.py` | E24 | Rebuilds CSR Table 14-2.01 (demographics) from the public ADSL. Expect 244 of 244 printed cells. |
| `csr_ae_spike.py` | E25 | Rebuilds CSR Table 14-5.01 (adverse events by organ class and term) from the public ADAE. Expect 1,175 of 1,175 with the display rule `csr` and 1,171 of 1,175 with `single`. |
| `csr_hylaw_spike.py` | E26 | Rebuilds CSR Table 14-6.06 (Hy's law shifts, with CMH p-values) under three pairs of rules. Expect 38, 45 and 51 of 51 printed cells. |
| `csr_fisher_rxc_spike.py` | E27 | Shows that the 59 p-values printed in CSR Tables 14-6.02 and 14-6.03 are exact Fisher tests on 3 x 3 tables (low, normal, high), using the printed counts only. Expect 59 of 59 for that reading and 10 of 59 for the 3 x 2 reading (normal, abnormal). |

Three of the `csr_` scripts read `csr.txt`, the output of
`pdftotext -layout CSR.pdf csr.txt` (poppler 24.02 was used) on the CSR of
R Consortium Pilot 6. `csr_hylaw_spike.py` reads the datasets only; the
values of its one-page table are typed into the script.

These are spikes, not product code. Work package base-0 turns them into
tests. real-2 replaces `ars_spike.py` with the real engines, and real-4
replaces the CSR parsers.

Two things the real engines of real-2 found that `ars_spike.py` could not
(ADR-002, decision 6): its comparison allows half a unit of a value the
example prints without decimals, so one of its 3,711 matches is a
difference ("70" against 70.5), and E4's 49 are 97 when the precision of
the display pattern counts. The spike is kept as it was run.

## Trials for decisions

| File | Decision | What it shows |
| --- | --- | --- |
| `adr002_siera_trial.sh` | ADR-002 | siera 0.5.6 on CDISC's ARS example and on its own variant of it, with the pilot ADaM; and what cards and cardx give for the methods of the registry. Recorded output: `adr002_siera_trial.out`. Needs `. scripts/env.sh` and a build of the pilot kit. |
| `adr003_rounding.sh` | ADR-003 | The expression tfrmt shows a number with, R's `format(round(x, digits), nsmall = digits)`, on the 2,537 results of the pilot that are shown with decimals, against the registry's rounding and the example's formatted values. tfrmt itself is not installed or run. Recorded output: `adr003_rounding.out`. Needs `. scripts/env.sh` and a build of the pilot kit. |
