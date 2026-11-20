# real-5b review (rule R7)

Reviewer: an independent agent with a fresh context, which did not write the
work. Date: 2026-11-19. Correctness only, no style.

Under review: commit `4028b54` on branch `track/real`: the real-5b commits
`e8d244f`, `4e7ed4c`, `7eeff23`, `10c6bbc` and `4028b54` after `548c0f5`.
`b6ec6a5` merges `main` `1ef7636` (the read track's slice-ae-summary); of
it I reviewed only what real-5b changes in it, two lines of
`src/specfirst/score/pilot.py` (`grids.template_of`, the merge against its
second parent). Read: CLAUDE.md; PLAN.md sections 2.3, 4.5, 4.8 and
decision 17; ADR-012; the amendments "of real-5b" of ADR-015 and ADR-003;
docs/reports/real-5b.md and real-5b.clean-clone.gate.log;
docs/reports/real-5a.review.md (pass 1); lesson 47; the diff
`548c0f5..4028b54` of every file the brief names.

## Files I quote, with their SHA-256

At `4028b54` (`git show 4028b54:<path> | sha256sum`):

```text
aeac7576b5e331c48b3162a2b3154f4a3e2950f42414b7e47c5a8caead3f4c87  docs/reports/real-5b.md
09ee7d89846da41e0f462c128d9de185d419bc1cbefb3041a5a45a15a6481151  docs/reports/real-5b.clean-clone.gate.log
5ce8896b29fb5c873c47b8834e33c1ee823b5bf9b923208217c9a47acf91a8c0  docs/decisions/ADR-015.md
51bd0c1e885af5e4e4e86270a77d5fe83710d7616cd1ad9a5ddc5575935926a7  docs/decisions/ADR-003.md
90e84bc6cfb2db86277e850f2d913fc1dd25e468798ce180c7c0bf928948f4a6  standard/methods/model.mmrm.lsmeans.yaml
eb5fa2f9d1b1ec0647e6a3b0eb58f1bbe2bc6dda712775c7bfbf6363753d761e  standard/methods/model.mmrm.pairwise.yaml
e67825b61a211e858eb3c5bcb64c6c7f2031fd5bb597239f23f55507a0bfbd56  standard/methods/test.cmh.yaml
0e753dbc7668141576d0bcf6fd9a4423215e02eff39af9dfc17510ae9cb6dcac  standard/methods/display.pattern.yaml
38fd8558a949c13e2f537d6e01c0095ee8b46efb98dda704818ff03de56fff93  standard/methods/registry.json
5b344f21c51f241b1fe5934b14f236fc571ff6922a26866590580a5564eb77e6  r/specfirstr/R/models.R
8de84d7d454486e5510a8fd826a867c70cf95fec6a533c080020f4e400965a9a  r/specfirstr/R/methods.R
411b457f9c5c167047b00037855742770f85f85c3d39a8fa1ce76097607a64fa  r/specfirstr/R/engine.R
6f6be9410d1632d0d15ae58e56dbd5e37e2118e0783f21e9ad75e014e4818308  src/specfirst/machine/methods.py
4421a689eef91163da035bd0d90d02bc1c7bb151038f879c5239c053f30aaef9  src/specfirst/machine/ard.py
a6790a2a44b6a3a1ad2f10ef713d4899131609794ab00634d445540679678c76  src/specfirst/machine/csr.py
d7cdf06d93d663e9e6709bd8ce8ef507dcbad8f588ffca883211abcc6c59748d  src/specfirst/machine/layout.py
4d3d6b95973288c1824731a2a056abb22474daf3aec57d4f11b7f8e9422c35d2  src/specfirst/machine/grid.py
0008825a6cacee8183b4e5af9e054e818d86da5ec421eacf721ee9977d526aa3  src/specfirst/machine/decisions.py
e7e4ef721535b67349b91f20ea2930224aaa8d908b08a06143a05ea17f9a7c5f  src/specfirst/gates.py
fa14c676adb64ef64022efb255ded9fd5a9f6873ce84465e6a4449d697fd18d8  tests/methods/oracle_mmrm.py
a7f0f4dd7087695fdb3b3d36e5a171e9f7c6043ceae091ae3a6b2ca1dd43e359  tests/methods/oracle.py
e221906b6410dd1fcbdc793aaba1882bd0d06b29a4b497ca04e339e1d69b0a43  tests/methods/test_methods.py
0b38e065b14e46c5a1411d63543e174e4569c7392bfc70edc88cf230f9f7442d  tests/defects/test_defects.py
0f4f8411c7906d13de20e9c3cfc9d0a1ef245d87935c35e8b00a8af70d6f0e4d  tests/unit/test_efficacy_5b.py
01f290d85220a0d6f83d162f99e6c81a33017fff62d962765e91cc1f5fe9f717  kits/cdiscpilot01/gold/events/efficacy-adas.json
ebb5d5418a33a21b4c1a37caf545e78515571a517ebec834cfe80cad889a5699  kits/cdiscpilot01/gold/events/efficacy-cibic.json
dc2bac712f0a362cd4f532ef57e70168bb381e4e9f636cb73156e4f4543c9f78  kits/cdiscpilot01/gold/exceptions.yaml
79c35080fbb9fea550a3c0b7b117be8555aba9261f10f7710c79fc3ab6d69fd9  kits/cdiscpilot01/gold/decisions/efficacy.jsonl
29027aa6503d5f9e3d952e121a0fa1ab7542b7600a81b8ad9928bcfc9cf4467b  kits/cdiscpilot01/gold/layout/Out14-3-11.yaml
85aa29f0723b031b6aaa9f61cd25e1c94920c9f94a57dcb86b148d33a467024b  kits/cdiscpilot01/gold/layout/Out14-3-13.yaml
67890a4fc2d6e170b9bc69750c51c0d583558dea5d6cc97b387811f55078e68f  kits/cdiscpilot01/kit.yaml
```

Pinned sources, read in my assembled kit (nothing written into the fetch
cache):

```text
0cab016c76abb3dcaef31110611c95dbd9cd00df083b35e6d28fd69fca0d842d  build/kits/cdiscpilot01/gold/reference/csr/CSR.pdf
210b7f1fdb0fd95e1b00b64fe1c7527d0000bd4e66b6ae31fdc08e2741af1bc7  build/kits/cdiscpilot01/inputs/docs/sap.pdf
```

CSR and SAP text below is CDISC material: I quote only the cells and
sentences a finding needs.

## Commands I ran, with their output (rule R8)

Setup: under WSL Ubuntu-24.04 as root, clones in the Linux file system,
the worktree's environment, every heavy run under the shared lock. Scratch
only under `/root/scratch-review-real5b/` (clones `clone`, `clone2` for
plants in the R code, `clone3` for the gate real-5a; `work/`, `text/`) and
my session's temporary folder (the scripts). Nothing was written into the
checkout but this file, nor into the fetch cache (both gates: "cache
untouched" PASS).

```text
$ git clone -q --no-local /mnt/d/trial_work/specfirst/.git /root/scratch-review-real5b/clone
$ git -C /root/scratch-review-real5b/clone checkout -q --detach 4028b54
$ . /mnt/d/trial_work/specfirst-real/scripts/env.sh
$ cd /root/scratch-review-real5b/clone; export SPECFIRST_ROOT=$PWD PYTHONPATH=$PWD/src
$ python -m specfirst kit assemble cdiscpilot01
kit cdiscpilot01: 67 files match their pinned SHA-256 (26 inputs, 41 gold) in .../clone/build/kits/cdiscpilot01
$ /usr/bin/pdftotext -v      -> pdftotext version 24.02.0
$ /usr/bin/pdftotext -layout build/kits/cdiscpilot01/inputs/docs/sap.pdf text/sap.txt
$ /usr/bin/pdftotext -layout -f P -l P build/kits/cdiscpilot01/gold/reference/csr/CSR.pdf text/csr-P.txt   (P = 49, 51, 53, 59, 61)
```

### C1. The gate real-5b on my clone of 4028b54

```text
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 python -m specfirst gate real-5b
1196 passed, 30 deselected in 483.88s (0:08:03)
Python implementations: 136 cases of 10 methods, 0 differences
R implementations: 131 cases of 12 methods, 0 differences
expected values computed again in exact arithmetic: 131 cases, 0 differences; written by hand: 60 cases (the display rules)
model-based methods in R: 55 cases of 5 methods, 0 differences
planted: model.mmrm.lsmeans always with at = last: 2 cases differ
planted: model.mmrm.pairwise always with df = kenward_roger_linear: 1 cases differ
P1 determinism: 56 of 56 files have the same SHA-256 in both builds
grid Out14-3-11: 24 cells, 15 print a number; 15 of the 15 cells with results have a complete path to SDTM columns
grid Out14-3-13: 100 cells, 78 print a number; 78 of the 78 cells with results have a complete path to SDTM columns
results efficacy-adas, engines: 165 results in both, 0 disagree; largest relative difference 2.1e-16 (allowed 1e-09)
results efficacy-cibic, engines: 141 results in both, 0 disagree; largest relative difference 9.7e-16 (allowed 1e-09)
grid Out14-3-11 against CSR Table 14-3.11: 24 cells, 15 of them printed in the CSR; 12 equal the CSR, 12 differ, 12 of them with one class and a proof that holds
grid Out14-3-13 against CSR Table 14-3.13: 100 cells, 78 of them printed in the CSR; 76 equal the CSR, 24 differ, 24 of them with one class and a proof that holds
efficacy: 2 tables, 124 cells; 88 equal the CSR; classified differences: 36 rule_choice
E22: Table 14-3.11 prints 12 numbers of the model; at Week 24 0 of them equal the CSR; averaged over weeks 8, 16 and 24, 12 cells give the CSR's text (other_build proofs that hold: 12 of 12 differing cells)
E22: the LS means of Table 14-3.11 are averages over the weeks: the hint holds
CMH: 3 results in both engines; largest relative difference 9.7e-16 (allowed 1e-09)
decisions: 18 records, 18 IDs; 99 options of analyses held against the decisions that set them; 0 problems
--- D11-efficacy-5b   (18 plants, each with problems; as in the report)
--- D12-cmh-engines   (4 plants, each with CMH results that disagree)
63 passed in 141.22s (0:02:21)
PASS environment, pins, lint, registry, unit tests, method vectors, kit, P1 determinism,
     P2 reproduction, trace, results, efficacy, E22 hint, CMH, decisions, pilot tests,
     planted defects, cache untouched, ASCII
GATE real-5b: PASS
```

The log (628 lines) agrees line for line in substance with
docs/reports/real-5b.clean-clone.gate.log, which was made on `10c6bbc`
(`10c6bbc..4028b54` adds the report and its log only).

### C2. The mixed model on inputs no vector holds: R against the oracle

`mmrm_cases.py`: data from a seeded numpy generator (an unstructured
covariance with unequal variances, a site factor of 3 levels, BASE and
BASE by visit), run through the registry's R implementation
(`rengine.run_vectors`) and through `oracle_mmrm.expected`.

```text
model.mmrm.lsmeans: visit 2 missing for 65%, unbalanced 8/15/25, KR, last [97 records, 47 subjects]: agree
model.mmrm.lsmeans: same, Satterthwaite, average [97 records, 47 subjects]: agree
model.mmrm.pairwise: same, pairwise ref B, KR, average [97 records, 47 subjects]: agree
model.mmrm.lsmeans: text visits V10 < V2 < V9 by characters, last = V9 [107 records, 42 subjects]: agree
model.mmrm.pairwise: text visits, pairwise ref A, Toeplitz, KR, last [107 records, 42 subjects]: agree
model.mmrm.lsmeans: numeric visits 0.5, 2, 10, no treatment by visit, SITE by visit, average [98 records, 42 subjects]: agree
model.mmrm.pairwise: numeric visits, 90%, ref C, last [98 records, 42 subjects]: agree
model.mmrm.lsmeans: group C without records at the last visit: missing [78 records, 30 subjects]: agree (both missing)
largest relative difference, R against oracle (the inputs above): 2.3e-07
model.mmrm.lsmeans: 4 groups, monotone dropout, Toeplitz, KR, last [126 records, 46 subjects]: oracle None (NotFitted), R gives results
model.mmrm.pairwise: 4 groups, Toeplitz, ref D, Satterthwaite, average: oracle None (NotFitted), R gives results
```

On the last input the oracle stops with "Fisher scoring did not
converge", for the unstructured covariance too. Its trace:

```text
iterations 500
0 change ... ; 50 change 3.798e-06 loglik -154.706839983151
100 change 2.313e-06 loglik -154.706839983135; 300 change 2.915e-06 loglik -154.706839983075
499 change 1.828e-06 loglik -154.706839983075
oracle with the stop at 1e-5, against R: LS means (KR, last) 2.1e-06; pairwise (Satterthwaite, average) 2.3e-05
```

(finding F4).

### C3. Edge cases of the statements

```text
model.mmrm.lsmeans, only group A has model records: oracle {lsmean: {'A': 4.777243661288176, 'B': None, 'C': None}}; R FAILS: the R vectors run exited 1: Error in `contrasts<-`(`*tmp*`, value = contr.funs[1 + isOF[nn]]) :
model.mmrm.pairwise, only the reference A has model records: oracle {estimate: {'B': None, 'C': None}}; R FAILS: ... Error in `contrasts<-`(...)
model.mmrm.lsmeans, one visit only (visit 3): oracle {lsmean: {'A': 4.869867822085636, 'B': 3.9229973411255936, 'C': 5.043023744319396}}; R FAILS: ... Error in `contrasts<-`(...)
```

(finding F3).

### C4. The pilot by routes of my own: the hint of E22, Kenward-Roger, the optimizer

`pilot_indep.py` reads the reference ADaM with pyarrow (no specfirst
engine): ADQSADAS, PARAMCD = ACTOT, AVISIT in weeks 8, 16, 24, ANL01FL =
Y, DTYPE empty, EFFFL = Y on ADSL, the arm by TRT01PN; then
`oracle_mmrm` (numpy) on those records, `nlme::gls` (REML, `corSymm` and
`varIdent`, a third implementation) and mmrm itself four ways.

```text
ADQSADAS model records: 539 subjects: 234
oracle last/kenward_roger_linear:    LS means ['2.3 (0.69)', '1.7 (0.77)', '1.5 (0.84)'] ...
oracle average/kenward_roger_linear: every one of the 12 numbers of the model is the CSR's text
                                     (e.g. LS mean of placebo '1.6 (0.49)', difference low - placebo '-0.0 (0.70)')
oracle average/satterthwaite:        two cells move: SE of the high dose '0.55', p-value high - low '0.605'
nlme::gls REML unstructured: log-likelihood -1543.9215174477
gls LS means at Week 24 (estimate, naive SE): 2.329123 (0.688130), 1.735226 (0.763100), 1.500921 (0.832272)
gls LS means averaged   (estimate, naive SE): 1.553545 (0.492342), 1.513615 (0.522427), 1.126954 (0.553897)
oracle average/KR SEs:  0.49296704 0.52355663 0.55519613

$ Rscript kr_df.R   (mmrm on the same records)
kr_linear_nlminb       REML logLik -1543.9215174373; averaged LS means SE 0.49296704 0.52355663 0.55519613; df 179.899745 210.859143 214.949463
satterthwaite_nlminb   REML logLik -1543.9215174373; averaged LS means SE 0.49234173 0.52242694 0.55389691; df 179.899745 210.859143 214.949463
kr_full_nlminb         REML logLik -1543.9215174373; averaged LS means SE 0.49122914 0.52136273 0.55282237; df 179.899745 210.859143 214.949463
kr_linear_default      REML logLik -1543.9215174808; averaged LS means SE 0.49296099 0.52355028 0.55518947; df 179.903645 210.864195 214.954638
```

The oracle and mmrm with nlminb agree to 8 digits on the pilot; gls (a
route that shares nothing with either) gives the same estimates and the
same unadjusted SE as Satterthwaite. Kenward-Roger-Linear and
Satterthwaite have the same df; the full Kenward-Roger (mmrm's own
parameters) and Satterthwaite give 0.55 for the high dose, where the CSR
prints 0.56; the default optimizer stops below the maximum (4.4e-8 in the
log-likelihood) and moves the SE in the fifth decimal, no printed cell.


### C5. CMH: Python, R, fractions, coin and mantelhaen.test

`cmh_cases.py`: 13 tables of my own through `methods.cmh_p` (Python), the
registry's R implementation (`rengine.run_vectors`), `oracle.cmh_p`
(fractions) and, as a route that shares no code with any of them, coin
1.4-6 (in the lock) `independence_test(..., teststat = "quadratic")` on
the records the tables expand to (a nominal response for general
association, the values as a numeric response for row mean scores, and
`trafo(..., numeric_trafo = rank_trafo, block = stratum)` for midranks
within strata), or `mantelhaen.test` for 2 x 2 x K.

```text
3 x 7, 3 strata, empty first and last columns, row_mean_scores/table: Python 0.26002868233894294; R rel 1.5e-15; oracle rel 1.3e-14; coin (values) 0.26002868233894 (df 2) rel 1.1e-14
3 x 7, 3 strata, empty first and last columns, row_mean_scores/rank: Python 0.18426141541976299; R rel 7.5e-16; oracle rel 4.4e-15; coin (midranks within strata) (df 2) rel 5.4e-15
3 x 7, 3 strata, empty first and last columns, general_association/table: Python 0.5945229502827001; ... coin general association (df 8) rel 3.5e-15
random 3 x 5, 4 strata, row_mean_scores/table | rank | general_association: rel at most 5.2e-15 (df 2, 2, 8)
rank-deficient W (a row only in a one-column stratum), general_association/table: Python 0.2189491828168668; R rel 8.9e-16; oracle rel 0.0e+00; coin (df 2) rel 1.0e-15
rank-deficient W (a row only in a one-column stratum), row_mean_scores/table: Python 0.0830311123189681; ... coin (df 1) rel 1.3e-15
rank-deficient W (a row only in a one-column stratum), row_mean_scores/rank: Python 0.05172892492186324; ... coin (df 1) rel 3.1e-15
a zero row and a zero column overall, columns in one stratum only, rmsc/rank: Python 0.31019526441512735; ... coin (df 1) rel 8.6e-15
same, general association: Python 0.2908456962110568; ... coin (df 2) rel 5.7e-16
2 x 2 x 5, Mantel-Haenszel: Python 0.4128912554832084; R rel 0.0e+00; oracle rel 2.7e-16; mantelhaen.test (df 1) rel 9.4e-16
single stratum 4 x 3 rank scores with ties: Python 0.011673102543818351; ... coin (df 3) rel 4.3e-15
largest relative differences from Python: {'R': '9.3e-15', 'oracle': '1.3e-14', 'coin': '1.1e-14'}
```

The pilot's three p-values by coin and by `mantelhaen.test`, on the
records I selected myself (ADQSCIBC, PARAMCD = CIBICVAL, ANL01FL = Y,
EFFFL = Y, strata SITEGR1):

```text
Week 8: coin row mean scores (values) p = 0.2727284040 (df 2); mantelhaen.test general association p = 0.4782176391 (df 8)
Week 16: coin row mean scores (values) p = 0.4003147145 (df 2); mantelhaen.test general association p = 0.7698590545 (df 8)
Week 24: coin row mean scores (values) p = 0.6180439310 (df 2); mantelhaen.test general association p = 0.8684861376 (df 8)
methods.cmh_p and oracle.cmh_p, general association: 0.478218, 0.769859, 0.868486 (-> 0.478, 0.770, 0.868)
CIBIC+ n per week with LOCF [77, 81, 73], [79, 81, 74], [79, 81, 74]; observed only [77, 81, 73], [68, 42, 41], [66, 47, 40]
```

The engines' values in C1 (0.2727284040371243, 0.40031471449145817,
0.6180439310104722) are coin's to the 10 digits printed.

For F5 (the words "Pearson Chi-Square"), one stratum, a 3 x 4 table of
mine, `methods.cmh_p` against `scipy.stats.chi2_contingency`:

```text
one stratum: Pearson 14.1706366757; CMH general association 13.9304563931; (n-1)/n * Pearson 13.9304563931
```

### C6. The two tables cell by cell, and every proof recomputed

`cells.py` reads my poppler text of pages 59 and 61 (cells assigned to
the nearest count column; my code, not `csr.parse`) and the build's grids
of C1, and recomputes each classified difference from the raw ARD values
with Python's `decimal` (half away from zero), not with display.pattern.

```text
Out14-3-11: 24 cells, 15 printed in the CSR, 12 equal, 12 differ; entries 12; differing cells without an entry: []; entries for cells that do not differ: []
  cell:Out14-3-11/r2/c1: ours '2.3 (0.69)', CSR '1.6 (0.49)'; averaged by my rounding '1.6 (0.49)' == CSR; Week 24 in the CSR's display '2.3 (0.69)' != CSR
  cell:Out14-3-11/r4/c2: ours '-0.6 (1.02)', CSR '-0.0 (0.70)'; averaged by my rounding '-0.0 (0.70)' == CSR; Week 24 in the CSR's display '-0.6 (1.02)' != CSR
  ... (12 of 12: averaged == CSR; Week 24, even with 1 decimal for the limits and the sign kept, != CSR)
Out14-3-13: 100 cells, 78 printed in the CSR, 76 equal, 24 differ; entries 24; differing cells without an entry: []; entries for cells that do not differ: []
  cell:Out14-3-13/r2/c4: ours '0.273', CSR '0.2727'; raw 0.2727284040371243 with 4 decimals '0.2727' == CSR
  (and r10/c4, r18/c4 the same way)
  counts of 0 shown '0 (0%)' where the CSR prints '0': 21, each our count 0: True
total {'cells': 124, 'printed': 93, 'equal': 88, 'differ': 36}
```

C6a, the averaged analyses against the Week 24 ones in
gold/events/efficacy-adas.json: for each of LSM, PwPbo and PwLow the only
keys that differ are id, name, reason, purpose and programmingCode, and in
programmingCode only `at` (`last` against `average`).

### C7. Shared code: the parser and the grids of real-5a, old code against new

```text
$ python parse_same.py   (csr.py of 548c0f5, sha256 d6b7b03f..., against 4028b54's on my poppler text)
page 49 table 14-3.01: every key of the old parse equal in the new: True; keys added: ['stub'] = [None]; lines 19, footnotes 3
page 51 table 14-3.03: every key of the old parse equal in the new: True; keys added: ['stub'] = [None]; lines 19, footnotes 3
page 53 table 14-3.05: every key of the old parse equal in the new: True; keys added: ['stub'] = [None]; lines 19, footnotes 3
old parser, page 59: parses, 3 columns, footnotes []      (the Note lines become rows)
old parser, page 61: CsrError: Table 14-3.13, line 10: two texts in column 1

$ git archive 548c0f5 src kits standard | tar -x -C old548
$ PYTHONPATH=old548/src python oldgrids.py   (layout and grid code of 548c0f5 on the ARD of the C1 build)
Out14-3-1-1: grid of the code of 548c0f5 == grid of the 4028b54 build: True (27 cells); mock shell the same: True
Out14-3-01: grid of the code of 548c0f5 == grid of the 4028b54 build: True (51 cells); mock shell the same: True
Out14-3-03: grid of the code of 548c0f5 == grid of the 4028b54 build: True (51 cells); mock shell the same: True
Out14-3-05: grid of the code of 548c0f5 == grid of the 4028b54 build: True (51 cells); mock shell the same: True
old layout files equal the new ones: True
```

### C9. The quotes of the ten records in the SAP

`sapq.py`: each quote, blanks collapsed, searched in the poppler text of
sap.pdf.

```text
custom:eff-mmrm-records 8.1 'Missing postbaseline efficacy values will be imputed using l' found 1
custom:eff-mmrm-records 10.1.1 'likelihood-based repeated measures' found 1
custom:eff-mmrm-records template 10 'Repeated Measures Analysis of Change from Baseline to Week 2' found 2
custom:eff-mmrm-terms 10.1.1 'the fixed, categorical effects of treatment, site, time (wee' found 1
custom:eff-mmrm-terms 7.1 'a new pooled site identifier assigned for the purpose of ana' found 1
custom:eff-mmrm-terms template 10 'baseline ADAS-Cog (11) score by time interaction' found 2
custom:eff-mmrm-covariance 10.1.1 'an unstructured covariance matrix will be used' found 1
custom:eff-mmrm-covariance 10.1.1 'a Toeplitz covariance matrix will be used' found 1
custom:eff-mmrm-visit 10.1.1 'for the change from baseline in the ADAS-Cog (11) at Week 24' found 0
custom:eff-mmrm-visit template 10 'Repeated Measures Analysis of Change from Baseline to Week 2' found 2
custom:eff-mmrm-display template 10 'LS Means (SE) xx.x (x.xx)' found 3
custom:eff-mmrm-display template 10 '95% CI (xx.xx;xx.xx)' found 12
custom:eff-cibic-records 10.1.2 'The visits for CIBIC+ are Week 8, Week 16, and Week 24' found 1
custom:eff-cibic-records ad hoc template 1 'CIBIC+ - Categorical Analysis' found 1
custom:eff-cibic-categories 14.1.2 '7-point scale' found 1
custom:eff-cibic-categories ad hoc template 1 'Marked improvement xx (xx%)' found 2
custom:eff-cmh 16.1 'by using the CMH test, controlling for site' found 1
custom:eff-cmh ad hoc template 1 'Overall comparison of treatments using CMH test (Pearson Chi' found 1
custom:eff-cmh 7.1 'a new pooled site identifier assigned for the purpose of ana' found 1
custom:eff-cibic-display ad hoc template 1 'Marked improvement xx (xx%)' found 2
custom:eff-cibic-display ad hoc template 1 'x.xxx' found 93
```

The one not found is in SAP 10.1.1 with a line break inside "ADAS-Cog"
(the text reads "the change from baseline in the ADAS- / Cog (11) at Week
24"): it stands. Each quote is in the section it cites (I read 7.1, 8.1,
10.1.1, 10.1.2, 14.1.2, 16.1, template 10 and ad hoc template 1).


### C8. Defects I planted (the executor did not)

`plants.py` calls the functions the gate calls: `efficacy_problems` of
tests/defects (the grid of each table built and held against its CSR
table and the kit's exceptions by `build.csr_against`, as `efficacy` and
D11 do), `decisions.problems` (the check `decisions`), both engines on a
changed event (`efficacy_rows`), on the build of C1. Each group first runs
the unchanged inputs: "control efficacy-adas: 0 problems", "control
efficacy-cibic: 0 problems".

C8a, in the exceptions:

```text
plant: other_build whose template is the CSR's literal text '1.6 (0.49)' (no analysis): 0 problems -> NOT SEEN
plant: other_build with the template '{lsm} (0.49)', half literal: 0 problems -> NOT SEEN
plant: a p-value of 14-3.13 proved by an other_build with the template '0.2727': 0 problems -> NOT SEEN
plant: the 12 entries of 14-3.11 naming the decision custom:eff-cmh (exists, unrelated): 0 problems -> NOT SEEN
plant: an LS-mean proof that maps to the averaged pairwise analysis: 1 problems; first: ... the proof does not hold: no result ard:An_ADAS_MMRM_PwPbo_Avg/Mth_MmrmLsm_1_lsm/Grp_Pbo of the other analysis
plant: an entry of 14-3.11 with class reference_error: 1 problems; first: ... the proof does not hold: other_build proves a rule_choice
```

C8b, in the layouts:

```text
plant: 14-3.13: the week 8 n row shows the week 24 CMH p-value: 1 problems; first: Out14-3-13: cell:Out14-3-13/r2/c4: ours '0.618', CSR '0.2727': the proof does not hold: with the other patterns the cell is '0.6180'
plant: 14-3.13: the label 'No Change' written 'No change': 1 problems; first: Out14-3-13: line 6: the grid has the row 'No change', the CSR 'No Change'
plant: 14-3.11: the columns of the placebo comparison listed in another order (no defect): 0 problems   (right: the order of `columns` is not the order of the cells)
plant: 14-3.11: the placebo comparison rows show the averaged analysis: 6 problems; first: Out14-3-11: cell:Out14-3-11/r3/c2: an exception for a cell that does not differ from the CSR
plant: 14-3.13: the week 16 categories under the heading Week 8: 33 problems; first: Out14-3-13: the grid has 28 lines under the header, the CSR 27
```

C8c, in the decision records (check `decisions`):

```text
plant: control (no change): 0 problems
plant: eff-mmrm-covariance says toeplitz: 6 problems; first: custom:eff-mmrm-covariance: ars:An_ADAS_MMRM_LSM has covariance = 'unstructured', the decision rule = 'toeplitz'
plant: eff-cmh says rank scores: 3 problems; first: custom:eff-cmh: ars:An_CIBIC_W08_Cmh has scores = 'table', the decision scores = 'rank'
plant: eff-mmrm-terms without baseline by week: 6 problems; first: custom:eff-mmrm-terms: ars:An_ADAS_MMRM_LSM has by_visit = ['BASE'], the decision by_visit = []
plant: eff-cibic-categories: the percent of the population: 0 problems -> NOT SEEN
plant: eff-mmrm-records: weeks 8 and 16 only: 0 problems -> NOT SEEN
plant: eff-cibic-display: p-values with 4 decimals: 0 problems -> NOT SEEN
plant: eff-mmrm-df binds the averaged analyses no more: 0 problems -> NOT SEEN
```

C8d, in the CSR parser (a changed copy of csr.py parsing my poppler text
of pages 59 and 61, then the same comparison):

```text
plant: CSR parse: the note is not a footnote (the _FOOTNOTE of real-5a): 1 problems; first: Out14-3-11: the grid has 7 lines under the header, the CSR 10
plant: CSR parse: the section heading on the line of its first row is dropped: 49 problems; first: Out14-3-13: the grid has 27 lines under the header, the CSR 24
plant: CSR parse: the extra column keeps only its first label line: 25 problems; first: Out14-3-13: the column labels [... 'p-value [1]'] are not the CSR's [... 'p-value']
plant: CSR parse: the cell 0.6180 is put one column to the left: 1 problems; first: Out14-3-13: the parse fails: Table 14-3.13, line 28: two texts in column 3
```

C8e, in the events, both engines (under the lock):

```text
plant: the averaged analyses alone without treatment by week: 12 problems; first: ... the proof does not hold: with the other build the cell is '1.3 (0.48)'
plant: all MMRM analyses without treatment by week: 12 problems
plant: all MMRM analyses without the site group factor: 11 problems
plant: the averaged analyses alone at 90% confidence: 3 problems; first: Out14-3-11: cell:Out14-3-11/r5/c2: ... with the other build the cell is '(-1.2;1.1)'
plant: CMH strata SITEID (not pooled): 3 problems; first: ... with the other patterns the cell is '0.4115'
plant: the week 8 subset takes the records of week 16: 15 problems
plant: CIBIC+ categories 2 and 3 exchanged in the grouping: 18 problems
```

C8f, the gate check `CMH` (`gates._cmh_engines` on a root whose
`build/p1/cdiscpilot01/first/gold/ard` holds changed copies of the two
ARD files of the build):

```text
CMH check, control: PASS; CMH: 3 results in both engines; largest relative difference 9.7e-16 (allowed 1e-09)
CMH check, R p-value of week 16 larger by a relative 1e-6: FAIL; ... the largest relative difference is 1.0e-06 (allowed 1e-09)
CMH check, R p-value of week 16 larger by a relative 2e-9: FAIL; ... the largest relative difference is 2.0e-09 (allowed 1e-09)
CMH check, R p-value of week 16 larger by a relative 5e-10 (within 1e-9): PASS   (right)
CMH check, the R rows of week 24 missing: FAIL; ... the engines give [...] and [...]
CMH check, week 24 missing in both engines: FAIL; CMH: 2 results in both engines; ...
CMH check, an R p-value missing (null): FAIL; ... ard:An_CIBIC_W08_Cmh/Mth_Cmh_1_pval/*: 0.2727284040371243 and None
```

C8g, in the R code (`clone2`, one plant at a time, restored after each;
`rplants.sh`): the gate's method vectors (`SPECFIRST_STRICT=1 pytest
tests/methods`), then both engines on the pilot with that R code and the
check of Table 14-3.11, and the CMH results of the two engines. The control
first:

```text
mixed-model vectors: 20 cases; R against the oracle run now: largest relative difference 2.4e-08 (a factor with one level is left out lower_cl A); oracle now against the expected values in the files: 9.2e-15
control: 14-3.11 0 problems; CMH 0 results disagree
R1 the LS means averaged over the visits with weights by records (emmeans "proportional"), not equal:
   R implementations: 131 cases of 12 methods, 34 differences; 2 failed, 5 passed
   14-3.11: 12 problems; first: ... with the other build the cell is '1.6 (0.46)'
R2 Kenward-Roger in mmrm's own parameters (vcov "Kenward-Roger"), not linear:
   R implementations: 123 differences; 14-3.11: 6 problems; first: ... with the other build the cell is '1.1 (0.55)'
R3 mmrm's default optimizer (L-BFGS-B), not nlminb:
   R implementations: 155 differences (e.g. lsmean A 2.638289820777458, expected 2.63828705140341); 14-3.11: 0 problems
R4 the visits in decreasing order (the "last" visit is the first):
   R implementations: 148 differences; 14-3.11: 0 problems
R5 the covariates of by_visit get no effect by visit (the `:.v` term of a covariate dropped):
   R implementations: 183 differences; 14-3.11: 5 problems; first: ... with the other build the cell is '1.1 (0.55)'
   (my first run of R5 did not apply: a fault in my regular expression; run again alone under the lock, as shown)
R6 CMH: the covariance without n / (n - 1):
   R implementations: 9 differences; pilot: 3 CMH results disagree, largest relative difference 6.0e-02
R7 CMH: midranks over all strata, not within each:
   R implementations: 1 differences (row mean scores with midranks); pilot: 0 (the pilot uses table scores)
```

Every R plant fails the gate (its vectors). R3 and R4 change no cell the
gate compares with the CSR: R3 moves numbers below the printed precision;
R4 makes gold's Table 14-3.11 show Week 8 in place of Week 24, which the
CSR comparison cannot see, since every number of the model in that table
is a classified difference whose proof reads the averaged analyses (F1).

C8h, defects in the Week 24 analyses alone (the averaged ones unchanged),
both engines, under the lock:

```text
plant: the Week 24 analyses alone at 90% confidence (gold's confidence limits change): 0 problems -> NOT SEEN
plant: the Week 24 analyses alone at 90% confidence, check decisions: 0 problems -> NOT SEEN
plant: the Week 24 analyses alone on the records LOCF adds (gold cells now ['2.3 (0.60)', '1.8 (0.59)', '1.3 (0.62)'] ...): 0 problems -> NOT SEEN
plant: the Week 24 analyses alone on the records LOCF adds, check decisions: 0 problems -> NOT SEEN
```

### C10. The gate real-5a on a clone of 4028b54

```text
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 python -m specfirst gate real-5a   (clone3)
1196 passed, 30 deselected in 495.83s (0:08:15)
grid Out14-3-1-1: 27 cells show 51 results; 27 cells equal the reference's formatted values, 0 differ, 0 of them with one class
grid Out14-3-01 against CSR Table 14-3.01: 51 cells, 40 of them printed in the CSR; 48 equal the CSR, 3 differ, 3 of them with one class and a proof that holds
(the same for 14-3.03 and 14-3.05; 14-3.11 and 14-3.13 judged too, as in C1)
grids: 6 outputs, pass
efficacy: 3 tables, 153 cells; 144 equal the CSR; classified differences: 9 rule_choice
63 passed in 129.36s (0:02:09)
PASS environment, pins, lint, registry, unit tests, method vectors, kit, P1 determinism, P2
     reproduction, trace, results, grids, efficacy, decisions, pilot tests, planted defects,
     cache untouched, ASCII
GATE real-5a: PASS
```

The executor's clean-clone runs of real-5a and read-2a on 4028b54 were
running on the shared machine at the same time; their logs are theirs,
not my evidence.

## Answers to the six questions

### 1. The semantics against the implementations; the oracles

Mixed model. I read `mmrm_frame`, `mmrm_fit`, `mmrm_emmeans`,
`m_mmrm_lsmeans`, `m_mmrm_pairwise` and the R engine's `run_model`
against the statements. Records (statement 1): `keep` asks for a value of
y, group (in the grouping), visit, subject, every factor and covariate;
two records of one subject at one visit fail. Visits (2): numbers by
value, text by `sort(method = "radix")` (C locale bytes), and the oracle by
code points: the same for ASCII; my text visits V10 < V2 < V9 agree (C2).
Terms (3): `.g + .v + .g:.v` (when `treatment_by_visit` is yes), the
factors as text with one-level factors left out, covariates, and
`column:.v` for `by_visit`; a design without full rank gives NULL, so
missing results. Covariance (4): `us()` and `toep()` (homogeneous
Toeplitz on the positions of the levels), both a reparametrization of the
statement's linear form, which the oracle uses. REML (5): `reml = TRUE`,
nlminb, NULL unless converged. LS means (6): `emmeans(..., weights =
"equal")`, at the last level of `.v` or averaged over `.v`; covariates at
their mean over the model records (emmeans' default on the fit's data).
SE (7): `vcov = "Kenward-Roger-Linear"`, or the unadjusted one for
Satterthwaite. df (8): mmrm's df with `theta_vcov`, the inverse Hessian.
The pairwise contrasts are named by position. The statements are what
the code computes, with two exceptions on inputs the pilot does not have:
one group, the reference alone, one visit (F3).

The oracle (`oracle_mmrm.py`) imports numpy and scipy only. I checked its
algebra: the REML score and expected information, the observed
information `-1/2 tr(Pi G_i Pi G_j) + y' Pi G_i Pi G_j Pi y` (no second
derivative of Sigma: it is linear), P_i, Q_ij, the adjusted covariance of
Kenward and Roger with R_ij = 0 and W the inverse observed information,
the gradient `-c' Phi P_k Phi c`, df = 2 (c' Phi c)^2 / (g' W g), and the
l vector (visit and factor weights; for an interaction the product of the
averages, which is the average of the products with these weights). It is
independent of mmrm and computes what statements 6 to 9 say. On my inputs
(C2) R and the oracle agree to 2.3e-7 or better, including a visit missing
for 65% of subjects, unbalanced groups 8/15/25, Toeplitz, text visits and
numbers that are not whole; on the pilot to 8 digits, and nlme's gls
agrees on the estimates and the unadjusted SE (C4). Where the likelihood
is flat the oracle does not converge (F4). Kenward-Roger's df equal
Satterthwaite's in mmrm (179.899745 both with nlminb, C4).

CMH. `cmh_p` (Python) and `m_cmh_p` (R) follow statements 1 to 7 line by
line: rows and columns empty over all strata left out with their score,
strata with fewer than 2 subjects skipped, m and V of statement 3, B of
statement 5 (general association; row mean scores with the values or
midranks within the stratum), the Moore-Penrose inverse with one
tolerance, and the chi-square tail. Rule I12d is implemented the same way
in `ard.strata_tables` and `engine.R strata_tables`. On 13 tables of mine,
including two rank-deficient W, empty rows and columns, columns present in
one stratum only, and rank scores with ties, Python, R, the fractions and
coin agree to 1.4e-14 (C5). The pilot's three p-values are coin's row
mean scores to 10 digits; general association by `mantelhaen.test` gives
0.478, 0.770 and 0.868 (C5).

### 2. The tables against the CSR; the 36 differences; the hint of E22

My own reading of pages 59 and 61 gives the grid's rows and labels in
order, 124 cells, 93 printed, 88 equal and 36 different, with exactly one
entry per differing cell and no entry for an equal cell (C6), as the
report says. Every proof proves what it claims: the 12 cells of 14-3.11
are the averaged analyses' values under the CSR's display (limits with 1
decimal, the sign of -0.04 kept), the 21 cells of 14-3.13 are counts of 0
that the template shows with "(0%)", and the 3 p-values are our own
values with 4 decimals (C6, by my rounding). The class of each is
`rule_choice`, which the owner reviews at N2.

The hint of E22 is tested and could not hold by construction: the
averaged analyses differ from the Week 24 ones in `at` only (C6a), `at =
average` is statement 6 with vectors from the oracle, and the 12 numbers
follow from the average by two routes that share nothing with the
engine (the oracle on records I selected myself, and nlme for the
estimates, C4). None follows from Week 24, even under the CSR's display
(C6). A wrong model fails the proofs when the averaged analyses carry it:
D11 (LOCF records 12 problems, Toeplitz 12, the site 10, no baseline by
week 5, Satterthwaite 2) and my plants (C8e, C8g R1 and R2). Three
limits: Satterthwaite is seen in 2 cells only, since the others keep the
printed text (as the report says); the default optimizer is seen by no
printed cell, only by the vectors (C8g R3); and a wrong model in gold
alone, the Week 24 analyses with the averaged ones intact, fails no proof
at all, because no number of the model in Table 14-3.11 is compared with
anything but through the averaged analyses (C8g R4, C8h; F1).

### 3. Can each new check fail?

Mostly yes. The executor's D11 (18 plants), D12 (4), the planted options
of the vectors and the unit tests are seen in C1. My plants (C8): in the
events (the averaged analyses alone without treatment by week, at 90%,
all without treatment by week or without the site group, CMH strata by
site, the week 8 subset on week 16, two CIBIC+ categories exchanged), in
the layouts (a p-value of another week in the extra column, a label, a
comparison shown from the averaged analysis, a groups block under the
wrong heading), in the exceptions (a wrong analysis, a wrong class), in
the decision records (covariance, scores, by_visit), in the parser (the
note, the heading on the row line, the label of the extra column, a cell
moved), in the R code (all seven, by the vectors) and in the CMH check's
inputs: each is seen where it changes something.

Not seen, and passing by construction in lesson 47's sense: gold's
numbers of Table 14-3.11. Every one differs from the CSR and is proved by
the averaged analyses, and the proof is not held to differ from gold only
in the decision's option, so a defect in the Week 24 analyses alone
passes `efficacy`, `E22 hint` and `decisions` (C8h; F1). The work's
plants never change gold alone. Also not seen: an other_build proof that
shows no result, a proof that names an unrelated decision (F1), and the
values of four records that set no option (F5, item 4). The check `CMH`
fails on my plants but on none of the work's (F2).

### 4. The decision records

Every quote stands in the SAP, in the section it cites (C9). Status and
class: `eff-mmrm-records` is `conflict` without a class: right by section
4.5 (SAP 8.1 LOCF in general against the likelihood-based analysis of
10.1.1 and template 10's title). `eff-mmrm-terms`, `eff-mmrm-covariance`,
`eff-mmrm-visit`, `eff-mmrm-display`, `eff-cibic-display`: `stated`,
`document_rule`, as the quoted text says. `eff-mmrm-df`: `asked`,
`gold_quirk`: no document names a df method; gold reproduces the CSR (4.8:
"When gold reproduces a rule of the reference that no source supports").
`eff-cibic-records` and `eff-cibic-categories`: the values are right and
the documents support the first, but the quotes do not show LOCF or the
denominator (F5). `eff-cmh`: `asked` is right; its statement gives one of
two readings of "Pearson Chi-Square" (F5, item 3).

Decision 17 (the documents decide). Week 24 for 14-3.11: SAP 10.1.1 "In
this analysis for the change from baseline in the ADAS-Cog (11) at Week
24" and template 10's title; the documents decide, the CSR differs: gold
is right, and the 12 cells are rule_choice. The template's display for
14-3.13: ad hoc template 1 shows every category as "xx (xx%)" and the
p-value as "x.xxx"; that is the reading real-5a took for template 5
(still open for the owner, ADR-015 "For the owner" item 1), and real-5b
is consistent with it. The row labels again follow the CSR, not the
templates ("N", "p-value (Xan - placebo)"): finding F8 of real-5a, still
the owner's (see below).

### 5. Shared code

`csr.parse`: the three pages of real-5a give the same parse with the code
of 548c0f5 and of 4028b54, plus a key `stub` = None (C7): the claim holds.
`layout`, `grid` (`template_of`, extra columns, groups blocks): the grids
and mock shells of Out14-3-1-1, Out14-3-01, 03 and 05 built by the code of
548c0f5 from the C1 ARD equal those of the 4028b54 build (C7). The
registry: a test may now take a `columns` option; binding rule B3 binds
descriptive methods only, so no generated kit reaches it; registry.json
changes, so every generated kit.yaml and every reader task folder changes
(said in the report and ADR-015). D9 now plants in the ANCOVA analyses
only (prefix `An_ADAS_W`) and holds the records against both events: the
same defects as before. Gates: real-2 and real-3a are not changed by
real-5b; real-5a's `efficacy` now counts its three tables and no longer
fails on another table of its result set (owner's item 2 below); the
gate real-5a passes on my clone of 4028b54 (C10). The read track: the
merge changes `score/pilot.py` to `template_of`, which is the row's
template for every cell outside an extra column; the ARS example's layout
has none (its plan and grid are unchanged, C7), so read-1a's key grid
cannot change. read-2a's kept run fails
as known; I did not run the read or gen gates.

### 6. The report

Its statements are supported by my runs, except the five points of F6.
It says what the checks do not cover; it should add the unheld records
(F5) and the literal-template gap (F1).

## Findings

### F1 (blocks the merge): the proof other_build is not held to "a build with that alternative", so gold's numbers of Table 14-3.11 are guarded by no cell

Where: `csr._other_build` and `csr.judge` (csr.py); `gates._e22_hint`.

What: PLAN.md section 4.8 asks of a `rule_choice` difference "a build
with that alternative, in which the cells equal the reference"; ADR-015
decision 16 defines other_build as the cell built again "with the results
of other analyses of the same event (an analysis that follows the other
alternative of the decision ...)". The check holds neither "that
alternative" nor that the build is otherwise ours:

1. An `analyses` mapping may name any analysis of the event that has rows
   of the same suffix; nothing holds that it differs from the cell's
   analysis only in the option the named decision sets. All 12 numbers of
   the model in Table 14-3.11 differ from the CSR and are proved by the
   averaged analyses, so gold's own numbers are compared with nothing:
   a defect in the Week 24 analyses alone that leaves the averaged ones
   intact is not seen by `efficacy` nor by `E22 hint`. C8h: the Week 24
   analyses at 90% confidence, or on the records LOCF adds, pass the
   check `efficacy` (0 problems) and the check `decisions` (0 problems)
   (on the LOCF records gold's LS means become 2.3 (0.60), 1.8 (0.59) and 1.3 (0.62); the E22 count reads the same comparison and holds too); C8g R4: gold showing Week 8 in place of Week 24
   is seen only because the R code is planted and the vectors run. The
   executor's D11 plants change the Week 24 and the averaged analyses
   together (or make gold equal the CSR), never gold alone: the case that
   would make the check fail was not planted (lesson 47).
2. A `template` may show no result: the CSR's own text as the template is
   "the other build", and it holds (C8a: `"1.6 (0.49)"`, `"{lsm}
   (0.49)"`, `"0.2727"`, 0 problems each). Any differing cell can then be
   classed `rule_choice` with a proof that proves nothing.
3. The named decision is any record of the kit (C8a: the 12 entries of
   14-3.11 naming `custom:eff-cmh`, 0 problems; finding F3 of real-5a,
   still open, now for the new proof kind).

What holds today: I recomputed all 36 proofs from the raw ARD values with
my own rounding (C6); the averaged analyses differ from the Week 24 ones
in `at` only (C6a); and gold's Week 24 numbers are those of an
independent fit on records I selected myself (C4, the oracle at the last
visit: 2.3 (0.69), 1.7 (0.77), 1.5 (0.84), -0.6 (1.02), and so on, equal
to the build's cells). So no number of the two tables is wrong. What
blocks is the gate: ADR-012 asks real-5b for "the cell rule of real-5a for
the two tables", and for Table 14-3.11 the check as written passes
whatever gold prints, so long as it differs from the CSR and the averaged
analyses are untouched.

Fix (code and tests, small): in `_other_build`, a mapped analysis must
equal the cell's analysis in everything but its id, name, reason, purpose
and the programmingCode options that the entry's decision sets
(`decisions.PARAMETERS`; for the 12 entries `at` of
`custom:eff-mmrm-visit`), and the decision must bind the cell's analysis;
an other template must name at least one part of the cell and add no
text of its own beyond the original template's. Plant: a defect in the
Week 24 analyses alone (C8h), a literal template, an unrelated decision.

### F2 (does not block): the gate check `CMH` is planted by no test of the work

Where: `gates._cmh_engines`; the report, section "Verdict" ("Each new
check fails on defects planted for it") and section "Planted defects".

What: D12-cmh-engines plants in the R engine's input and asks
`results.agreement` (the function of the check `results`) to see the
disagreement; `_cmh_engines` itself is called by nothing but the gate
(grep: no test names it), and test_gates.py plants only `_e22_hint`. Rule
R5: a checker counts only after it fails on a planted defect.

Evidence C8f: I planted in copies of the two ARD files of the build. A
p-value of R larger by a relative 1e-6 or 2e-9, the R rows of week 24
removed, week 24 removed in both engines, an R p-value null: the check
fails each time; 5e-10 (inside its 1e-9) passes, as it should. So the
check works; the report's sentence is not true of it.

Fix: a unit test with those plants, or the sentence in the report
narrowed.

### F3 (does not block): the R implementation of the mixed model halts where the statements give results

Where: `mmrm_frame` and `mmrm_fit` in models.R (the design is made by
`stats::model.matrix` outside any `tryCatch`).

Evidence C3: with model records of one group only, `m_mmrm_lsmeans` stops
("Error in `contrasts<-` ..."), where the oracle gives that group its LS
mean (statements 3 and 10); with the reference alone, `m_mmrm_pairwise`
stops where statement 7 gives missing results; with one visit only,
`m_mmrm_lsmeans` stops where the oracle gives three LS means. These are
the cases (a) of finding F5 of real-5a, which real-5b fixed for ANCOVA
and which the report lists as fixed ("The F5 edge cases of the R
implementation ... fixed in models.R"); the new functions repeat them.
Loud: the R engine run fails and no wrong number reaches a table; the
pilot does not meet them.

Fix: fit without `.g` when one group is left (or return the missing
results the statements give), return missing results for the reference
alone, and say in statement 2 or 3 what one visit gives (or handle it);
a vector each.

### F4 (does not block): the oracle of the mixed model does not converge on an ordinary input, and agrees with R to about 1e-5 there

Where: `oracle_mmrm.Model._fit` (stop when the relative change of theta is
below 1e-14, at most 500 steps).

Evidence C2: 46 subjects in 4 groups with monotone dropout over 4 visits,
unstructured or Toeplitz: "Fisher scoring did not converge". The restricted
log-likelihood stays at -154.70683998 to 12 digits while theta moves by a
relative 2e-6 to 5e-6 per step; the line search accepts a decrease of
1e-12 relative, so the iteration wanders on a flat ridge. With the stop at
1e-5, the oracle and the R implementation agree to 2.1e-6 (LS means,
Kenward-Roger) and 2.3e-5 (pairwise, Satterthwaite, averaged): outside
the 1e-6 the vectors are held to. On the other 7 inputs of mine they agree
to 2.3e-7. So "agrees ... to about 1e-8" (ADR-015 decision 14, the
report) holds for the 20 vectors and for the pilot, not for every input;
a future vector on such data would fail for the oracle's sake, not the
implementation's.

Fix: none needed for real-5b; when vectors are added, a stop on the
change of the log-likelihood and of the gradient, and a tolerance that
follows the conditioning (or keep vectors away from flat likelihoods, as
tests/methods/README.md keeps limits away from 0).

### F5 (does not block): three records say less or more than their quotes, and five records are held by no check

Where: kits/cdiscpilot01/gold/decisions/efficacy.jsonl; decisions.py.

1. `custom:eff-cibic-records` (`stated`, `document_rule`): its value is
   "LOCF included", the point D11 shows matters (week 24 without LOCF: 18
   problems), but neither quote mentions LOCF ("The visits for CIBIC+ are
   Week 8, Week 16, and Week 24"; "CIBIC+ - Categorical Analysis", which
   drops the "- LOCF" of the template's title). SAP 10.1.2 says it in the
   sentence before the quoted one ("Summary statistics will be generated
   for each visit using the efficacy population with LOCF imputation").
2. `custom:eff-cibic-categories` (`stated`, `document_rule`): the
   denominator "the subjects of the week" is stated by neither quote
   ("7-point scale"; "Marked improvement xx (xx%)"). The template's row
   "N" under each week is the reading; it is not cited and not said to be
   a reading.
3. `custom:eff-cmh` (`asked`, `gold_quirk`) says the footnote's "Pearson
   Chi-Square" "names no CMH statistic". For one stratum the CMH
   statistic of general association is (n - 1)/n times Pearson's
   chi-square, so the footnote can be read as naming general association
   (0.478, 0.770, 0.868 on the pilot, C5). Under that reading the
   documents decide (decision 17), gold is general association and the 3
   p-values are rule_choice differences. The record should give both
   readings to the owner; it gives one.
4. Plants C8c: the denominator of `eff-cibic-categories`, the visits of
   `eff-mmrm-records`, the decimals of `eff-cibic-display`, and the binds
   of the averaged analyses in `eff-mmrm-df` changed: 0 problems for the
   check `decisions` each (finding F4 of real-5a, now for five more
   records; the CSR comparison sees the first through the cells, D11).
   decisions.py lists the unheld records of real-5a only.

Every quote of the ten records stands in the SAP (C9); one,
`eff-mmrm-visit`'s "for the change from baseline in the ADAS-Cog (11) at
Week 24", only once the SAP's line break after "ADAS-" is joined.

Fix: text only: quote the LOCF sentence of 10.1.2; cite the template's
per-week "N" row and say the denominator is a reading (or make it
`asked`); give both readings in `eff-cmh`; list the unheld records in
decisions.py and in "What the checks do not cover".

### F6 (does not block): small inaccuracies of the report

1. "general association gives 0.478, 0.770 and 0.869": week 24 is
   0.868486 (`mantelhaen.test`, our `cmh_p` and the fractions agree, C5),
   so 0.868.
2. "mmrm's Kenward-Roger degrees of freedom are its Satterthwaite degrees
   of freedom (179.903645 both, on the CSR's data)": 179.903645 is the
   value of mmrm's default optimizer; with nlminb, which the
   implementation runs, both are 179.899745 (C4). The claim itself holds.
3. "with Satterthwaite's standard errors ... one standard error is 0.55
   where the CSR prints 0.56" (report, and the statement of
   `custom:eff-mmrm-df`): Satterthwaite changes two printed cells, the SE
   of the high dose (0.55) and the p-value of high against low (0.605
   against 0.606) (C4; D11 says "2 problems").
4. "Each new check fails on defects planted for it": not the check `CMH`
   (F2).
5. "The F5 edge cases ... fixed in models.R": for ANCOVA; the mixed model
   repeats case (a) (F3).

### F7 (does not block; for N2): one classified difference rests on a display rule no record holds, three on two records

The entry of `cell:Out14-3-11/r4/c2` (CSR "-0.0 (0.70)") needs, besides
the averaged analysis, `zero_sign: kept`: gold's "0.0" for -0.04 follows
statement 5 of display.pattern, a default no decision record states, so
the owner cannot see at N2 that the CSR follows another sign rule. The
three confidence intervals of 14-3.11 need the averaged analyses and the
CSR's 1 decimal (`custom:eff-mmrm-display` says 2); each entry names
`custom:eff-mmrm-visit` only. The report's table says both in words.
Recommendation: name the zero-sign rule in `custom:eff-mmrm-display` and
list both points under "For the owner".

Note on the change the author announced after this review began (the
coordinator's message: display.pattern restored, the sign of -0.0 moved to
a display entry of its own that the other_build proof names, because
ADR-017 ties a kept reader run to display.pattern): I reviewed 4028b54 as
it stands. The finding holds either way: the new entry needs its numbered
statement and vectors (the case -0.04 under "X.X" and a 0 that stays
unsigned), the proof must still fail without it (D11's plant "the proof
of '-0.0' without the sign kept"), and a decision record should name the
rule gold follows. The changed commit needs its own look (a pass 2).

## The owner's choices (PLAN.md section 2.3), with my recommendation

1. **The classes of the 36 differences (N2).** All `rule_choice`, each
   with a proof that holds (C6). Recommendation: accept, and decide them
   together with real-5a's 9 cells and labels: if the shells' masks are a
   document's rule (decision 17), the templates also rule the row labels
   ("N", "p-value (Xan - placebo)"), which both parts take from the CSR
   (real-5a finding F8); if they are not, gold takes the CSR's display
   and 24 of the 36 entries (and real-5a's 9) go. Add the sign rule of
   "-0.0" (F7).
2. **real-5a's gate changed so that it passes on this branch.**
   `gates._efficacy_of` filters the result set to the gate's own tables;
   before, a table of the set that the gate did not know failed it
   (tests/unit/test_gates.py now expects True where it expected False).
   That is "a gate cannot pass without changing the gate" (2.3). The
   meaning of real-5a's gate is kept: `display_checks`, whose verdict the
   check keeps, still judges every table of the kit (C1, C10).
   Recommendation: accept, and record it in ADR-015's amendment of
   real-5b, as real-5a recorded the same change of real-2 and real-3a.
3. **The records of the mixed model (`conflict`).** Recommendation: the
   observed records (the CSR's, and the usual reading of
   "likelihood-based"), recorded as the owner's answer.
4. **The degrees of freedom (`asked`).** Recommendation: Kenward-Roger
   with linear parameters, as built (only it gives the CSR's 0.56, C4),
   recorded as the owner's answer; class `gold_quirk` stays.
5. **The CMH statistic (`asked`).** Two readings: the footnote names no
   statistic (the executor's; gold = row mean scores, the CSR's, class
   `gold_quirk`), or "Pearson Chi-Square" names the general association
   statistic (then by decision 17 gold is general association, 0.478,
   0.770, 0.868, and the 3 p-values become rule_choice with an
   other_build proof). The CSR prints the same footnote over row mean
   scores, which supports the first; the words alone favour the second.
   Recommendation: the owner decides and the record gives both readings
   and the answer; nothing in the build changes under the first.
6. **The Toeplitz fallback** of SAP 10.1.1 is not implemented; the pilot
   does not meet it. Recommendation: accept for real-5b; implement it
   before a study that needs it.
7. **The merge order** (the read track's binding ADR first) is the
   owner's answer already; nothing to add.

## Verdict

The machine is sound and the numbers are right. The gate real-5b passes
on my clone of 4028b54 (C1). The R implementations do what the statements
say on the pilot and on inputs no vector holds, and the vectors' oracle is
independent of mmrm and agrees with it (C2, C4); CMH agrees across
Python, R, fractions and coin, rank-deficient tables and rank scores
included (C5). Every printed cell of Tables 14-3.11 and 14-3.13 equals
the CSR or is one of the 36 classified differences, each of whose proofs
I recomputed (C6); the hint of E22 holds by routes that share nothing with
the engine (C4); gold's Week 24 numbers are those of an independent fit
(C4). The shared code keeps the parse and the grids of real-3a and real-5a
byte for byte (C7), and the gate real-5a passes (C10).

One finding blocks: the gate's cell rule does not guard gold's numbers of
Table 14-3.11, because the proof other_build is not held to "a build with
that alternative" (F1). A defect in the Week 24 analyses alone passes the
gate, and a literal template passes as a proof. The fix is small (code and
plants, no number changes) and fits the change the author already plans
(the sign of -0.0, F7). The other findings do not block. The merge also
waits, as the report says, for the read track's ADR on kept runs; that is
not a finding.

Verdict: NOT SIGNED (blocking: F1)

## Pass 2

Reviewer: an independent agent with a fresh context, which wrote neither
the work nor pass 1. Date: 2026-11-20. Correctness only, no style.

Under review: commit `753b5ac` on branch `track/real`, which answers pass 1
(above, on `4028b54`). I read the diff `4028b54..753b5ac` of every file it
changes, pass 1 in full, the amendment "of real-5b" of ADR-015 as it now
stands, the report docs/reports/real-5b.md as it now stands, and ADR-017
and `src/specfirst/harness/binding.py` and the kept run's `binding.json` on
`track/read` (`f104ef3`), which say what the read track's kept run is bound
to.

### Files I quote, with their SHA-256

At `753b5ac` (`git show 753b5ac:<path> | sha256sum`):

```text
4262ce5fbf1e2922332fc23ff9c6dc4b28d6477a093a853277366f448968b0ee  docs/reports/real-5b.md
e1cd8c9d0d3171e4055c0fd0183c616b7af4dc2ae1f37fcfd555a988c632ac8d  docs/reports/real-5b.review.md (pass 1, before this section)
09ee7d89846da41e0f462c128d9de185d419bc1cbefb3041a5a45a15a6481151  docs/reports/real-5b.clean-clone.gate.log
c8ffb8c05a306a595440e26c6b7e7a22fdf206acf2d43068a3727a01489eed8b  docs/decisions/ADR-015.md
e9dc75f73b0650340cc9dc7f1aafdbedf0335d1e83396747db03cd34f3422baa  src/specfirst/machine/csr.py
bc9f3b91e866037152b49c3f90cd05c4040141e1d0a09b73d8f999a0c1798e1b  src/specfirst/machine/build.py
46fbff426c09cd48c050019e2faae9a251d9725dcc225e9aa00bb1deee812a2d  src/specfirst/machine/decisions.py
ff509ac06d647c6af0bd3e445a0d8bcb6d4d23e7b1cc3f0e2ac193711df97782  src/specfirst/machine/methods.py
287ecd1f099e0ce333d2693225f2daf31f7dd6ca67486051b0bb3799a4d649b2  r/specfirstr/R/models.R
f22e5c95370d01d06cab4d0e1b58b7ba462bea4b302a76b7d0ddb8864ce570ae  standard/methods/display.pattern.yaml
40af290cbd18994cd802200072e28265c66c0ade916035e99d679838f0bbd91a  standard/methods/display.pattern.signed.yaml
4cab3003bf40e0581b5ad61d400ade9040225cb74e311b46ccdfba31f8bd1b9a  standard/methods/model.mmrm.lsmeans.yaml
d483f17d951d8597716a033a8e41ce8f88004b220389901aa92c65a22616c6de  standard/methods/model.mmrm.pairwise.yaml
edc5419a1e130a5da28694d02661897b2ab23ced6bd3c8df9776a0e9be048a7d  standard/methods/registry.json
e33a656e678911b40212dd640120c5557c12865ce7fc633ec9638dc54c0e3bfa  tests/methods/display_pattern.json
44169ae1a60ae781fdf466356ce13d8e795bf88834308d4ba1fd4dd63dc130ce  tests/methods/display_pattern_signed.json
247934c23f1b985c53289255eaf97cfb6ef03627736441993dc5a596c3c32dee  tests/methods/model_mmrm_lsmeans.json
f595b37ad461840b138b2663a1b40d2771864edd2952e513fe23e8f2c2c8329b  tests/methods/model_mmrm_pairwise.json
67fc6b83ce126f1324dd5864b59b8033a6179b305499a05bf7fdaf30851a90bc  tests/methods/oracle_mmrm.py
07c57c1a51036ed8ea9d52e6e0383c20ade6948b078ba81801d6389c3d2b3203  tests/defects/test_defects.py
32843f3a2edb18c52a025ec9955f745fa7495e64283addcec8b0d8276c7144b7  tests/unit/test_efficacy_5b.py
3b06f8acab5615ecab9b1b89ce742c26df4a237cd3f4d37aacd35fd9c5faa958  tests/unit/test_gates.py
ab0778f58a2e1701ca0ff1a1d8b15c2e64f39954d35e95b2e0b78c241f9a1ad2  kits/cdiscpilot01/gold/exceptions.yaml
650a344f128c03a51425bdcedc438f5f16af2f782b118b244cd2ccf0f2171a51  kits/cdiscpilot01/gold/decisions/efficacy.jsonl
29027aa6503d5f9e3d952e121a0fa1ab7542b7600a81b8ad9928bcfc9cf4467b  kits/cdiscpilot01/gold/layout/Out14-3-11.yaml
85aa29f0723b031b6aaa9f61cd25e1c94920c9f94a57dcb86b148d33a467024b  kits/cdiscpilot01/gold/layout/Out14-3-13.yaml
01f290d85220a0d6f83d162f99e6c81a33017fff62d962765e91cc1f5fe9f717  kits/cdiscpilot01/gold/events/efficacy-adas.json
```

At `548c0f5`: `standard/methods/display.pattern.yaml` f22e5c95...70ae and
`tests/methods/display_pattern.json` e33a656e...3bfa, the same as at
`753b5ac`. On `track/read` `f104ef3`:
`src/specfirst/harness/kept/R-task-04119188ff71/binding.json`
68822d77688e7759eda10b190a1fe95da6df82256c2252df24710a3babc6a641.
Pinned sources, read in my assembled kit (`kit assemble`: "67 files match
their pinned SHA-256"): sap.pdf 210b7f1f...1bc7, CSR.pdf 0cab016c...842d
(as in pass 1); poppler `pdftotext` 24.02.0.

### Commands I ran, with their output (rule R8)

Setup: WSL Ubuntu-24.04 as root, the worktree's environment
(`. /mnt/d/trial_work/specfirst-real/scripts/env.sh`), fresh clones of
`753b5ac` in the Linux file system under `/root/scratch-review-real5b-p2/`
(`gate-real-5b`, `gate-real-5a`, `gate-real-3a`, and `clone` for the light
runs), `SPECFIRST_ROOT` and `PYTHONPATH` set to the clone; my scripts in my
session's temporary folder. Every gate and every run of the engines under
`flock /run/lock/specfirst-heavy.lock taskset -c 0-3`. Nothing written into
the checkout but this section, nor into the fetch cache (each gate: "cache
untouched" PASS).

#### D1. The gate real-5b on my clone of 753b5ac

```text
$ git clone -q --no-local /mnt/d/trial_work/specfirst/.git gate-real-5b; git -C gate-real-5b checkout -q --detach 753b5ac
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 python -m specfirst gate real-5b
gate real-5b at commit 753b5acfc256979a7a494a616db1b5520d0ebc3b (clean)
1201 passed, 30 deselected in 519.53s (0:08:39)
Python implementations: 139 cases of 11 methods, 0 differences
R implementations: 134 cases of 12 methods, 0 differences
expected values computed again in exact arithmetic: 134 cases, 0 differences; written by hand: 63 cases (the display rules)
model-based methods in R: 58 cases of 5 methods, 0 differences
planted: model.mmrm.lsmeans always with at = last: 2 cases differ
planted: model.mmrm.pairwise always with df = kenward_roger_linear: 1 cases differ
P1 determinism: 56 of 56 files have the same SHA-256 in both builds
grid Out14-3-11 against CSR Table 14-3.11: 24 cells, 15 of them printed in the CSR; 12 equal the CSR, 12 differ, 12 of them with one class and a proof that holds
grid Out14-3-13 against CSR Table 14-3.13: 100 cells, 78 of them printed in the CSR; 76 equal the CSR, 24 differ, 24 of them with one class and a proof that holds
grid Out14-3-01 (03, 05) against CSR Table 14-3.01 (03, 05): ... 3 differ, 3 of them with one class and a proof that holds
efficacy: 2 tables, 124 cells; 88 equal the CSR; classified differences: 36 rule_choice
E22: Table 14-3.11 prints 12 numbers of the model; at Week 24 0 of them equal the CSR; averaged over weeks 8, 16 and 24, 12 cells give the CSR's text (other_build proofs that hold: 12 of 12 differing cells)
CMH: 3 results in both engines; largest relative difference 9.7e-16 (allowed 1e-09)
decisions: 18 records, 18 IDs; 99 options of analyses held against the decisions that set them; 0 problems
--- D11-efficacy-5b   (21 plants and 2 against the records, each with problems; among them:)
planted, gold's analyses alone at 90% confidence: 12 problems, ... An_ADAS_MMRM_LSM_Avg differs from An_ADAS_MMRM_LSM in more than the optio...
planted, gold's analyses alone on the records LOCF adds: 12 problems, ...
planted, a proof whose template is the CSR's text: 1 problems, ... the other template must show parts of the cell and add no text ...
planted, a proof whose template adds text ('{lsm} (0.49)'): 1 problems, ...
planted, an entry that names an unrelated decision (custom:eff-cmh): 1 problems, ... custom:eff-cmh binds no analysis of the cell nor its me...
63 passed in 148.97s (0:02:28)
PASS environment, pins, lint, registry, unit tests, method vectors, kit, P1 determinism,
     P2 reproduction, trace, results, efficacy, E22 hint, CMH, decisions, pilot tests,
     planted defects, cache untouched, ASCII
GATE real-5b: PASS
```

#### D2. The check of the cells against the plants of pass 1 and new ones

`plants2.py` (SHA-256 47932340...c0be5) on the build of D1
(`build/p1/cdiscpilot01/first`): the functions the gate calls
(`build.csr_against` for each table against its CSR table and the kit's
exceptions and records, `decisions.problems`), and both engines on a
changed event (`efficacy_rows` of tests/defects), under the lock.

```text
control Out14-3-11: 24 cells, 15 printed, 12 equal, 12 differ, 12 classified ['rule_choice'], 0 problems
control Out14-3-13: 100 cells, 78 printed, 76 equal, 24 differ, 24 classified ['rule_choice'], 0 problems
control: classified 36; decisions: 0 problems
A1 other_build template = the CSR's text '1.6 (0.49)': 1 problems -> seen; ... the other template must show parts of the cell and add no text ...
A2 template '{lsm} (0.49)' (no analyses): 1 problems -> seen; (the same reason)
A2b template '{lsm} (0.49)' with the averaged analysis: 1 problems -> seen; (the same reason)
A3 14-3.13 p-value proved by template '0.2727': 1 problems -> seen; (the same reason)
A4 the 12 entries of 14-3.11 naming custom:eff-cmh: 12 problems -> seen; ... custom:eff-cmh binds no analysis of the cell nor its method; An_ADAS_MMRM_LSM_Avg differs from An_ADAS_MMRM_LSM in more than the opti...
A4b one entry naming [custom:eff-mmrm-visit, custom:eff-cmh]: 1 problems -> seen; ... custom:eff-cmh binds no analysis of the cell nor its method
A5 an LS-mean proof mapping to the averaged pairwise analysis: 1 problems -> seen; ... An_ADAS_MMRM_PwPbo_Avg differs from An_ADAS_MMRM_LSM in more than the options at of custom:eff-mmrm-visit
A6 an entry of 14-3.11 with class reference_error: 1 problems -> seen; ... other_build proves a rule_choice
A7 an entry naming custom:eff-mmrm-df (binds the cell, sets df, not at): 1 problems -> seen; ... differs from An_ADAS_MMRM_LSM in more than the options df of custom:eff-mmrm-df
A8 an entry naming custom:eff-mmrm-display only (binds the method, sets nothing): 1 problems -> seen; ... set no option of an analysis ...
A9 '-0.0' proved without display.pattern.signed: 1 problems -> seen; ... with the other build the cell is '0.0 (0.70)'
A10 '-0.0' proved with display 'display.pattern' named: 1 problems -> seen; (the same)
A11 a template that drops a part, '{lsm}', with the averaged analysis: 1 problems -> seen; ... with the other build the cell is '1.6'
A12 a template that swaps the parts, '{se} ({lsm})', with the averaged analysis: 1 problems -> seen; ... '0.49 (1.6)'
B1 14-3.13 r2/c4 (gold right) proved by other_pattern {p: 'X.2727'}: 0 problems -> NOT SEEN
B1b the same by other_build {patterns: {p: 'X.2727'}}: 0 problems -> NOT SEEN
B2 gold's week 8 p-value cell now (ours, CSR): ('0.400', '0.2727')      (layout: the week 8 row shows An_CIBIC_W16_Cmh)
B2a gold wrong (week 16's p in the week 8 row), the entry as it is: 1 problems -> seen; ... with the other patterns the cell is '0.4003'
B2b gold wrong, the entry's pattern 'X.2727' (other_pattern): 0 problems -> NOT SEEN
B6 literal-pattern proofs for the 12 entries of 14-3.11, gold as it is:
   r2/c1 {se}: {"se": "X.6 (0.49)"}; r2/c2 {lsm}: {"lsm": "1.5 (0.5X)"}; r2/c3 {se}: {"se": "X.1 (0.56)"};
   r3/c3 {p}: {"p": "X.556"}; r5/c2 {upper}: {"upper": "(-X.4;1.3)"}; r5/c3 {upper}: {"upper": "(-X.9;1.0)"};
   r7/c3 {diff}: {"diff": "-X.4 (0.75)"}; r3/c2, r4/c2, r4/c3, r6/c3, r8/c3: none found (entry kept)
B6 the 12 entries of 14-3.11 with literal-pattern proofs (gold as it is): 0 problems -> NOT SEEN
--- both engines, under the lock
C8h-1 gold's Week 24 analyses alone at 90%: efficacy: 12 problems -> seen; ... An_ADAS_MMRM_LSM_Avg differs from An_ADAS_MMRM_LSM in more than the options at of custom:eff-mmrm-visit
C8h-1 the same: decisions: 0 problems
   LOCF alone: gold's cells of the model: r2/c1 '2.3 (0.60)', r2/c2 '1.8 (0.59)', r2/c3 '1.3 (0.62)', r3/c2 '0.613', r3/c3 '0.237', r4/c2 '-0.4 (0.82)', ...
C8h-2 gold's Week 24 analyses alone on the LOCF records: efficacy: 12 problems -> seen; (the same reason)
C8h-2 the same: decisions: 0 problems
B3 literal-pattern proofs for gold on the LOCF records: found for 9 cells
   (r2/c1, r2/c2, r2/c3, r3/c3, r4/c2 {"diff": "-X.0 (0.70)"}, r5/c2, r5/c3, r6/c3 {"p": "X.606"}, r8/c3); none for r3/c2, r4/c3, r7/c3
B3 gold's Week 24 analyses alone on the LOCF records, literal-pattern proofs: 3 problems -> seen; the 3 cells without one:
   cell:Out14-3-11/r3/c2: ours '0.613', CSR '0.955': ... An_ADAS_MMRM_PwPbo_Avg differs from An_ADAS_MMRM_PwPbo in more than the options at ...
   unchanged: gold's cells of the model: r2/c1 '2.3 (0.69)', r2/c2 '1.7 (0.77)', r2/c3 '1.5 (0.84)', r3/c2 '0.560', r3/c3 '0.440', r4/c2 '-0.6 (1.02)', ...
   visits by AVISIT: gold's cells of the model: r2/c1 '0.6 (0.48)', r2/c2 '1.6 (0.47)', r2/c3 '0.8 (0.50)', r3/c2 '0.108', r3/c3 '0.769', r4/c2 '1.1 (0.65)', r4/c3 '0.2 (0.67)', r5/c2 '(-0.23;2.33)', ...
B4 the visits ordered by AVISIT (record and six analyses): efficacy: 0 problems -> NOT SEEN
B4 the same: decisions: 0 problems -> NOT SEEN
B4 the six analyses by AVISIT, the record unchanged: decisions: 6 problems -> seen; first: custom:eff-mmrm-terms: ars:An_ADAS_MMRM_LSM has visit = ['AVISIT'], the decision visit = ['AVISITN']
B5 r2/c1 proved by an analysis averaged and with Satterthwaite (names visit, df): 0 problems -> passes
B5b the same naming custom:eff-mmrm-visit only: 1 problems -> seen; ... An_ADAS_MMRM_LSM_X differs from An_ADAS_MMRM_LSM in more than the options at of custom:eff-mmrm-visit
```

In B3 the 9 cells with a literal proof pass: the 3 problems are the cells
for which no single mask of their values gives a digit the CSR's text
holds, so they keep their original entry.

#### D3. display.pattern and the entries the read track's slice reaches

`registry_and_signed.py`: the canonical SHA-256 (`canonical.content_hash`,
as `binding.entries` of `track/read` computes it) of each record of
registry.json at `548c0f5` and `753b5ac`, against the kept run's
`binding.json` on `track/read` `f104ef3`.

```text
registry format: 548c0f5 0 753b5ac 0 kept binding 0
count.subjects                       548c0f5 59ebd98d4878fe2e 753b5ac 59ebd98d4878fe2e same; kept binding 59ebd98d4878fe2e equal
display.pattern                      548c0f5 cd734ed0247cc43c 753b5ac cd734ed0247cc43c same; kept binding cd734ed0247cc43c equal
display.pattern.signed               548c0f5 None             753b5ac 4247d61ce9b20592 added
display.round.half_away_from_zero    548c0f5 2cc13b617fd65862 753b5ac 2cc13b617fd65862 same; kept binding 2cc13b617fd65862 equal
display.round.half_even              548c0f5 7547577274e4fb9f 753b5ac 7547577274e4fb9f same
model.mmrm.lsmeans, model.mmrm.pairwise, test.cmh: added; the other 7 entries: same
percent.subjects                     548c0f5 6da10171ab4b2eef 753b5ac 6da10171ab4b2eef same; kept binding 6da10171ab4b2eef equal
$ git diff --stat 548c0f5 753b5ac -- (the YAML and vector files of count.subjects, percent.subjects,
      display.round.half_away_from_zero, display.round.half_even, display.pattern)
(no output)
```

#### D4. display.pattern.signed: its vectors against the implementation and against plants

The same script, the 7 cases called as test_methods.py calls them
(`pattern_text(..., zero_sign="kept", **options)`), and the 22 cases of
display.pattern, with `methods.pattern_text` and with six changed copies:

```text
display_pattern.json cases: 22 ; any with zero_sign: False
implementation as committed: signed vectors 7 of 7 pass; display.pattern vectors that fail: 0
plant: the sign never kept: signed vectors 4 of 7 pass (cases 1, 2, 4 fail)
plant: 0 signed too: signed vectors 6 of 7 pass (case 5: '-0.0' != '0.0')
plant: a positive number that rounds to zero signed: 6 of 7 pass (case 6)
plant: the sign after the padding: 5 of 7 pass (case 2: ' -0.0' != '- 0.0'; case 3)
plant: the option rounding ignored: 6 of 7 pass (case 4: '-0.1' != '-0.0')
plant: a missing number shown as empty text: 6 of 7 pass (case 7)
```

#### D5. The mixed model's edge cases and its 23 vectors

`mmrm_edges.py`: data from a seeded numpy generator (SITE of 3 levels,
BASE and BASE by visit), through the registry's R implementation
(`rengine.run_vectors`) and `oracle_mmrm.expected`; `vec23.py`: the 23
vectors through R now and the oracle now.

```text
model.mmrm.lsmeans: one group (B of A, B, C), KR, last [19 records]: agree; groups with results []        (oracle: does not increase; R: no fit)
model.mmrm.lsmeans: one group, Toeplitz, no treatment by visit [19 records]: agree; groups with results ['B']
model.mmrm.lsmeans: one group (C), 4 visits, average [37 records]: DIFFER; R gives C, oracle: Fisher scoring did not converge
model.mmrm.lsmeans: one visit, three groups [24 records]: agree; groups with results []
model.mmrm.lsmeans: one text visit, two groups [16 records]: agree; groups with results []
model.mmrm.lsmeans: two groups of three (B without records) [45 records]: agree; groups with results ['A', 'C']
model.mmrm.lsmeans: one group, text visits V16 < V24 < V8 [20 records]: DIFFER; R gives B, oracle: does not increase
model.mmrm.lsmeans: one group, 30 subjects, unstructured, KR, last [83 records]: agree; groups with results ['B']
model.mmrm.lsmeans: one group, 30 subjects, Satterthwaite, average [83 records]: agree; groups with results ['B']
model.mmrm.lsmeans: one group, 30 subjects, text visits V16 < V24 < V8, last [81 records]: agree; groups with results ['C']
model.mmrm.pairwise: one group (C) that is not the reference A [37 records]: agree; groups with results []
model.mmrm.pairwise: the reference alone (A) [20 records]: agree; groups with results []
model.mmrm.pairwise: the reference alone, average, Satterthwaite [23 records]: agree; groups with results []
model.mmrm.pairwise: one visit, three groups, pairwise [24 records]: agree; groups with results []
model.mmrm.pairwise: two groups, reference C, B without records [45 records]: agree; groups with results ['A']
model.mmrm.pairwise: reference B and one other group present of four [109 records]: agree; groups with results ['D']
largest relative difference R against oracle (results both give): 2.1e-08

$ python vec23.py
23 vectors; largest relative difference: R against the files 7.1e-09; oracle now against the files 1.3e-15; R against the oracle now 7.1e-09
```

#### D6. The quotes of the changed records in the SAP

My poppler text of sap.pdf, blanks collapsed:

```text
1  Summary statistics will be generated for each visit using the efficacy      (custom:eff-cibic-records, 10.1.2: 572 characters after the heading 10.1.2)
1  The visits for CIBIC+ are Week 8, Week 16, and Week 24
1  Week 8 N xx xx xx x.xxx                                                      (custom:eff-cibic-categories: in ad hoc template 1, "CIBIC+ - Categorical Analysis - LOCF")
2  Marked improvement xx (xx%)
1  7-point scale
1  Overall comparison of treatments using CMH test (Pearson Chi-Square),        (custom:eff-cmh)
1  by using the CMH test, controlling for site
3  LS Means (SE) xx.x (x.xx)                                                    (custom:eff-mmrm-display)
12 95% CI (xx.xx;xx.xx)
```

#### D7. The other gates and the unit tests of the proofs

```text
$ python -m pytest -q tests/unit/test_efficacy.py tests/unit/test_efficacy_5b.py tests/unit/test_gates.py -m "not evidence"   (clone of 753b5ac)
86 passed in 2.82s
$ grep -n "csr.judge" tests/unit/test_efficacy.py
129:    csr.judge(compared, [ENTRY], PLANNED, OURS, {"custom:d"})
145:        csr.judge(compared, entries, PLANNED, OURS, {"custom:d"})
$ flock ... taskset -c 0-3 python -m specfirst gate real-5a   (clone gate-real-5a of 753b5ac)
gate real-5a at commit 753b5acfc256979a7a494a616db1b5520d0ebc3b (clean)
1201 passed, 30 deselected in 455.05s (0:07:35)
grid Out14-3-01 (03, 05) against CSR Table 14-3.01 (03, 05): 51 cells, 40 of them printed in the CSR; 48 equal the CSR, 3 differ, 3 of them with one class and a proof that holds
grids: 6 outputs, pass
efficacy: 3 tables, 153 cells; 144 equal the CSR; classified differences: 9 rule_choice
decisions: 18 records, 18 IDs; 99 options of analyses held against the decisions that set them; 0 problems
63 passed in 130.14s (0:02:10)
GATE real-5a: PASS   (18 of 18 PASS)
$ flock ... taskset -c 0-3 python -m specfirst gate real-3a   (clone gate-real-3a of 753b5ac)
gate real-3a at commit 753b5acfc256979a7a494a616db1b5520d0ebc3b (clean)
1201 passed, 30 deselected in 463.12s (0:07:43)
grid Out14-3-1-1: 27 cells show 51 results; 27 cells equal the reference's formatted values, 0 differ, 0 of them with one class
grids: 6 outputs, pass
63 passed in 132.97s (0:02:12)
GATE real-3a: PASS   (16 of 16 PASS)
```

### Answers to the five questions

#### 1. F1: the cases of pass 1, the 36 entries, and other ways in

Every case pass 1 planted is now refused, and by the rule meant for it
(D2): the CSR's text as the template, the half-literal template with or
without the averaged analysis, the literal p-value template (A1 to A3: "the
other template must show parts of the cell and add no text"); the 12
entries naming `custom:eff-cmh`, alone or beside `custom:eff-mmrm-visit`
(A4, A4b: "binds no analysis of the cell nor its method"); an LS mean
mapped to the averaged pairwise analysis (A5: "differs ... in more than the
options at"); the class `reference_error` (A6); gold's Week 24 analyses
alone at 90% or on the records LOCF adds, both engines (C8h-1, C8h-2:
`efficacy` sees each, 12 problems, by "differs from ... in more than the
options at"; `decisions` still sees neither, which is right: no record sets
those). So are a decision that binds the cell but sets another option
(A7), a decision that sets no option (A8), the sign of "-0.0" without
display.pattern.signed (A9, A10) and a template that drops or swaps parts
of the averaged build (A11, A12). The 36 genuine entries hold: 12 of 12
and 24 of 24 classified `rule_choice`, 0 problems, `decisions` 0 problems
(D2 control; D1).

Other ways in. (a) An other analysis that differs only in an option a
named decision sets: the options allowed are those of all the decisions
an entry names, and nothing asks that the CSR follows each of them. B5:
the LS mean of placebo proved by an analysis averaged and with
Satterthwaite, the entry naming `custom:eff-mmrm-visit` and
`custom:eff-mmrm-df`: 0 problems; naming the first alone: seen
("differs ... in more than the options at"). That is the design the
amendment states ("an entry may name a list of decisions"), and
gold itself stays held by the check `decisions` for every option a record
sets, so I record it, not as a finding: the owner sees both names at N2.
(b) A template that drops a part: allowed and needed (`{n}` for the counts
of 0); with the averaged build it gives "1.6", not the CSR's text (A11).
(c) Text carried by a pattern: G1, which gets wrong gold numbers past the
check. (d) What "last" means: G2, inherent to a CSR that prints no
number of the last visit.

#### 2. F2 to F7

- F2: `test_the_cmh_check_of_real5b_sees_a_disagreement` plants a value
  moved by 2e-9, a row left out and a missing value in the R file and keeps
  5e-10 inside; it runs in the gate's unit tests (D1, D7). Fixed.
- F3: fixed as said. R against the oracle on inputs of mine (D5): one group
  of three with records, at the last visit and averaged, unstructured and
  Toeplitz, KR and Satterthwaite, text visits, gives that group's LS mean
  and the others missing; the reference alone, one visit (numeric or text),
  a non-reference group alone give missing results; where both give
  numbers they agree to 2.1e-8. On small data of one group (8 to 10
  subjects) the oracle stops ("does not increase", "did not converge")
  where R gives results: F4 again, not R. The 23 vectors: R against the
  files 7.1e-9, the oracle now against the files 1.3e-15 (D5).
- F4: not fixed, stated: the oracle's comment, ADR-015 decision 14, the
  report. Holds.
- F5: the four records now say what pass 1 asked; every new quote stands in
  the SAP section it cites (D6); decisions.py and the report list the
  records held by no check. Fixed.
- F6: items 1, 2, 3 and 5 corrected; item 4 true now that F2 is planted.
  Fixed, but the report has new stale figures (G3).
- F7: `custom:eff-mmrm-display` states gold's sign rule (`zero: no_sign`),
  the four entries name both decisions, ADR-015 "For the owner" item 5 lists
  both points. Fixed.

#### 3. display.pattern and display.pattern.signed

display.pattern is byte for byte what it was at `548c0f5`: the YAML and
its vectors have the same SHA-256, and its record in registry.json has the
same canonical SHA-256 (D3). So have count.subjects, percent.subjects and
both rounding rules (YAML, vectors and record), and the four records equal
those the kept run's `binding.json` on `track/read` holds for the entries
its slice reaches; the registry's format is 0 in both. `pattern_text`
without `zero_sign` does what it did at `548c0f5` (the 22 vectors of
display.pattern pass). The new entry adds no ARS name, so `ars.bind` (B3:
descriptive only) cannot make a generated kit reach it.

display.pattern.signed says what the code does: statement 1 is
`zero_sign == "kept" and value < 0 and not sign` (the sign before the
padding, as display.pattern places a sign), statement 2 that 0 and a
positive number get none (-0.0 is not < 0). Its 7 vectors fail on every
plant I made in the implementation (D4): the sign never kept (3 fail), 0
signed (1), a positive number signed (1), the sign after the padding (2),
the option rounding ignored (1), a missing number as empty text (1).

#### 4. What the fixes may have broken

Nothing I could find. The gates real-5a and real-3a pass on clones of
`753b5ac` (D7); real-5a's 9 entries (other_pattern) pass the new bind
check, and real-5a's D9 sees its plants as before. The unit tests of
real-5a that call `csr.judge` with a set of IDs pass (86 passed in
test_efficacy, test_efficacy_5b and test_gates, D7): with a set the bind
check is skipped and an other analysis is refused
("which the check was not given"); no caller outside the tests passes a
set (`build.csr_against` passes the records and the event's analyses, and
`csr_comparison` the kit's records), so the gates always run the full
check.

#### 5. The report and ADR-015's amendment

The amendment's decisions 16, 17 and 19 and its "For the owner" items 2, 4
and 5 are supported by my runs, except decision 16's "held to 'that
alternative'" and "adds no text", which patterns defeat (G1). Decision 14's
"23 vectors ... about 1e-8" holds (7.1e-9, D5). The report's changed
statements hold: the two Satterthwaite cells (D11 in D1: "2 problems"),
the edge cases (D5), the CMH reading of general association (0.770 for
week 16 in D11's plant, D1; 0.478 and 0.868 are pass 1's C5, as are the df
figures, C4). But its gate and counts are of `10c6bbc` (G3), and it does
not say G2.

### Findings

#### G1 (blocks the merge): a pattern of a proof may carry text of its own, so a proof that proves nothing still holds and a wrong gold number still passes

Where: `csr._other_build` and the `other_pattern` branch of `csr.judge`
(the `patterns` of a proof go to `methods.pattern_text` unchecked);
ADR-015, amendment of real-5b, decision 16.

What: pass 1's F1, item 2, was that "a template may show no result" (the
CSR's text as the template). The fix holds the template: it must show
parts of the cell and add no text. But `patterns` are not held, and a
result pattern is text around one mask of X (`methods.pattern_mask`:
"(XXX.X)" is a valid pattern), so the text the template may no longer add
comes in through the pattern of one part, and the template may drop the
other parts (`{se}` alone is allowed, rightly, for the counts of 0). The
mask then shows only one or two digits of the value: a p-value below 0.5
under "X" is "0", so "X.2727" shows "0.2727" for any such p-value.

Evidence (D2): on the genuine values, the p-value of week 8 in 14-3.13
proved by `{p: X.2727}` (other_pattern or other_build), 0 problems (B1,
B1b); 7 of the 12 entries of 14-3.11 replaced by proofs such as `{template:
"{se}", patterns: {se: "X.6 (0.49)"}}`, which read no averaged analysis, 0
problems (B6). With gold wrong: the week 8 row of 14-3.13 showing the CMH
p-value of week 16 ("0.400"), seen with the entry as it is (B2a), passes
with the pattern "X.2727" (B2b, 0 problems); gold's Week 24 analyses alone
on the records LOCF adds, which the fixed check now sees (C8h-2), pass in
the 9 cells for which one mask of a value gives a digit the CSR's text
holds; the 3 others fail only for want of such a digit (B3). So, for
Table 14-3.11 as for 14-3.13, a differing cell can still be classed
`rule_choice` with a proof that proves nothing, and ADR-015's "held to
'that alternative'" and the exceptions file's "(parts of the cell, no text
of its own)" are not what the check does.

Fix (small; no number and no genuine entry changes): a pattern of a proof
keeps the text of the part's own pattern before and after its mask and
changes only the mask (`pattern_mask(new)[0] == pattern_mask(old)[0]` and
the same for `[2]`), in both proof kinds. All 45 genuine entries of the kit
(the 36 of real-5b and the 9 of real-5a) give bare masks (`X.X`,
`X.XXXX`) for parts whose own patterns are bare masks, so they still hold.
Plants: B1, B2b and B6 (or one of each kind) in D11 and in
test_efficacy_5b.

#### G2 (does not block): what "the last visit" is, is held by no cell of the CSR

Where: Table 14-3.11; `custom:eff-mmrm-terms` (`visit`) and
`custom:eff-mmrm-visit`; the report's "What the checks do not cover".

What: since the fix, gold's analyses and the averaged ones that prove the
12 cells may differ only in `at`, so every defect the two share shows in
the averaged numbers and fails a proof (C8h-1, C8h-2: seen). What they do
not share is which visit is last, and the CSR prints no number of the last
visit. B4 (D2): the visits taken from AVISIT (text, so "Week 8" sorts last)
in the record `custom:eff-mmrm-terms` and in the six analyses alike: gold's
table under the title "to Week 24" shows the LS means of the last visit by
characters, Week 8 (statement 2): "0.6 (0.48)", "1.6 (0.47)", "0.8
(0.50)" in place of "2.3 (0.69)", "1.7 (0.77)", "1.5 (0.84)", and each of
the other 9 numbers of the model changes too; `efficacy` and `decisions`
give 0 problems. The R code's choice of the last level is held
by the vectors (pass 1, C8g R4); the record's choice of the visit column is
held by nothing but the owner's reading.

Fix: say it in "What the checks do not cover". Better, and small: let
`custom:eff-mmrm-visit` name the visit ("Week 24") and check that the last
visit of the model records of gold's analyses is that one.

#### G3 (does not block): the report's figures are those of 10c6bbc

Where: docs/reports/real-5b.md, sections "Verdict", "What real-5b asks
for", "The gate", "Planted defects", "What the checks do not cover".

What: the verdict and the gate's output are of the clean clone of
`10c6bbc`; on `753b5ac` the gate prints other lines (D1: 1201 tests
passed, not 1196; method vectors 139 cases of 11 methods in Python, 134 in
R, 58 model-based, not 136 of 10, 131, 55; D11 with 21 plants and 2
against the records, not 16 and 2).
Stale or wrong now: "D11 (18 plants)" (23: D1); "model.mmrm.lsmeans.yaml
(10 statements)" (11); "nine proofs other_build that prove nothing and two
more of their form" (12 cases and a new test); "test_gates.py plants three
ways the hint of E22 is not shown" (and now the check CMH, F2); and "What
real-5a's report lists stays: ... the proofs' decision records held for
existence only", which the bullet above it (and the code) contradicts.

Fix: the clean-clone gate of the commit that merges, and these figures
with it (the report says the next version records the gates).

### The owner's choices (PLAN.md section 2.3)

Pass 1's list stands; what changed:

1. **The classes of the 36 differences (N2).** As in pass 1; the four
   entries that also rest on the CSR's display (three with 1 decimal for the
   limits, one with the sign of -0.04) now name `custom:eff-mmrm-display`
   beside `custom:eff-mmrm-visit`, and the CSR's sign rule is an entry of
   its own (ADR-015, "For the owner" item 5). Recommendation unchanged.
2. **real-5a's gate changed** (pass 1, item 2): now recorded in ADR-015's
   amendment, "For the owner" item 4. Recommendation: accept.
3. **The CMH statistic.** The record and the amendment now give both
   readings of "Pearson Chi-Square". Recommendation unchanged: the owner
   decides; nothing changes under the first.
4. **What "the last visit" is (G2).** Recommendation: accept that the CSR
   cannot show it, record it in the report, and, if the owner wants it held,
   let `custom:eff-mmrm-visit` name Week 24 and check the last visit of the
   model records against it.
5. **The merge waits for ADR-017 on `main`** (the owner's answer). The
   entries the slice reaches are unchanged (D3), so under ADR-017 the kept
   run's binding still holds for them; I did not run read-2a.

### Verdict

The fixes of pass 1 are in and work. Every case pass 1 planted is refused,
by the rule meant for it, gold's Week 24 analyses alone at 90% or on the
LOCF records included, and the 36 genuine entries still hold (D2). F2 to
F7 are fixed or stated as the commit says (F4 stated). display.pattern, its
vectors and its record, and the other entries the read track's slice
reaches, are byte for byte those of `548c0f5` and of the kept run's binding
(D3); display.pattern.signed says what the code does, and each of six
plants fails its vectors (D4). The mixed model's edge cases agree with the
oracle wherever the oracle converges (D5). The gate real-5b passes on my
clone of `753b5ac` (D1), and so do real-5a and real-3a (D7).

One finding blocks: the proof is still not held to "a build with that
alternative", because a part's pattern may carry the CSR's text around its
mask (G1). A literal pattern proves a genuine cell and wrong gold numbers
of both tables (B1, B2b, B3, B6). The fix is a few lines and plants, and no
genuine entry changes. G2 and G3 do not block: G2 is a limit of what any
CSR comparison of 14-3.11 can see, to be stated; G3 is the report's
figures, to be brought to the commit that merges.

Verdict: NOT SIGNED (blocking: G1)

## Pass 3

Reviewer: an independent agent with a fresh context, which wrote neither
the work nor passes 1 and 2. Date: 2026-11-20. Correctness only, no style.

Under review: commit `1b0ad01` on branch `track/real`, which answers pass 2
(above, on `753b5ac`; blocking G1). I read the diff `753b5ac..1b0ad01` of
every file it changes but this one (csr.py, tests/defects/test_defects.py,
tests/unit/test_efficacy.py, tests/unit/test_efficacy_5b.py,
gold/exceptions.yaml, ADR-015.md, docs/reports/real-5b.md), passes 1 and 2,
and the code the proofs call: `layout.template_names`,
`methods.pattern_mask` and `pattern_text`, `gates._e22_hint`,
`decisions.PARAMETERS` and the records of efficacy.jsonl.
`origin/track/real` is `1b0ad01` (`git fetch origin; git log --oneline -3
origin/track/real`, Windows git, at the start and again after all my runs):
the commit with the clean-clone gate of `1b0ad01` and its log is not there,
so question 2 is answered for what `1b0ad01` holds.

### Files I quote, with their SHA-256

At `1b0ad01` (`git show 1b0ad01:<path> | sha256sum`):

```text
846d7a65cdb1a46b9ee58648d1c19447fcd3cb942f27fcce25ce8188bbd77c46  docs/reports/real-5b.md
bc8c85ad2a68d0e2150e11103597364c480b4a04f6d922dc1225eb713dec6e18  docs/reports/real-5b.review.md (passes 1 and 2, before this section)
09ee7d89846da41e0f462c128d9de185d419bc1cbefb3041a5a45a15a6481151  docs/reports/real-5b.clean-clone.gate.log
2fea7d984eacb708e3573ac776e69d0fe213ab44ca5c7843604dda9d7eb92ce7  docs/decisions/ADR-015.md
87ccdd4a9e251cb2617c470ee3459cccef9f9740713d8f45d905b7a881ee7b67  kits/cdiscpilot01/gold/exceptions.yaml
c0acc47e4075e6744f0d767da7a28ce801dac044b735488f0b8f0348e5f4077c  src/specfirst/machine/csr.py
d7cdf06d93d663e9e6709bd8ce8ef507dcbad8f588ffca883211abcc6c59748d  src/specfirst/machine/layout.py
ff509ac06d647c6af0bd3e445a0d8bcb6d4d23e7b1cc3f0e2ac193711df97782  src/specfirst/machine/methods.py
6ba5b56ff67f957866be97d286a0b2fce422d7d034c3b9abd7e1d09b93d3ea5d  tests/defects/test_defects.py
f74a464efacb53978acb41d5f95626d63c767cadddd1e5364bad87ecdd7cf3fd  tests/unit/test_efficacy.py
1bb25e9593222378a700c9676946cb70868d2ff9ba1610080f281a557cf54a90  tests/unit/test_efficacy_5b.py
```

The gate log at `1b0ad01` is the one of `4028b54` and `753b5ac` (09ee7d89...1151
in pass 1's list), the clean clone of `10c6bbc`. My script `plants3.py`
(SHA-256 499f699c33613881d49c93561ecd4d92bf06e44f3ea0c7f57a5b96e13bcd62c4)
is in my session's temporary folder.

### Commands I ran, with their output (rule R8)

Setup: WSL Ubuntu-24.04 as root, the worktree's environment
(`. /mnt/d/trial_work/specfirst-real/scripts/env.sh`), fresh clones of
`1b0ad01` in the Linux file system under `/root/scratch-review-real5b-p3/`
(`gate-real-5b`, `gate-real-5a`, `clone` for the unit tests), made by
`git clone -q --no-local /mnt/d/trial_work/specfirst/.git` and `git checkout
-q --detach 1b0ad01`; `SPECFIRST_ROOT` and `PYTHONPATH` set to the clone.
Both gates and every run of the engines under `flock
/run/lock/specfirst-heavy.lock taskset -c 0-3`. Nothing written into the
checkout but this section, nor into the fetch cache (each gate: "cache
untouched" PASS).

#### E1. The gate real-5b on my clone of 1b0ad01

```text
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 python -m specfirst gate real-5b   (639 lines)
gate real-5b at commit 1b0ad01af02d1e2c747affc53f0a8c18fb85dc21 (clean)
1203 passed, 30 deselected in 336.45s (0:05:36)
Python implementations: 139 cases of 11 methods, 0 differences
R implementations: 134 cases of 12 methods, 0 differences
expected values computed again in exact arithmetic: 134 cases, 0 differences; written by hand: 63 cases (the display rules)
model-based methods in R: 58 cases of 5 methods, 0 differences
kit cdiscpilot01: 67 files match their pinned SHA-256 (26 inputs, 41 gold) in .../gate-real-5b/build/kits/cdiscpilot01
P1 determinism: 56 of 56 files have the same SHA-256 in both builds
grid Out14-3-11: 24 cells, 15 print a number; 15 of the 15 cells with results have a complete path to SDTM columns
grid Out14-3-13: 100 cells, 78 print a number; 78 of the 78 cells with results have a complete path to SDTM columns
results efficacy-adas, engines: 165 results in both, 0 disagree; largest relative difference 2.1e-16 (allowed 1e-09)
results efficacy-cibic, engines: 141 results in both, 0 disagree; largest relative difference 9.7e-16 (allowed 1e-09)
grid Out14-3-11 against CSR Table 14-3.11: 24 cells, 15 of them printed in the CSR; 12 equal the CSR, 12 differ, 12 of them with one class and a proof that holds
grid Out14-3-13 against CSR Table 14-3.13: 100 cells, 78 of them printed in the CSR; 76 equal the CSR, 24 differ, 24 of them with one class and a proof that holds
efficacy: 2 tables, 124 cells; 88 equal the CSR; classified differences: 36 rule_choice
E22: Table 14-3.11 prints 12 numbers of the model; at Week 24 0 of them equal the CSR; averaged over weeks 8, 16 and 24, 12 cells give the CSR's text (other_build proofs that hold: 12 of 12 differing cells)
E22: the LS means of Table 14-3.11 are averages over the weeks: the hint holds
CMH: 3 results in both engines; largest relative difference 9.7e-16 (allowed 1e-09)
decisions: 18 records, 18 IDs; 99 options of analyses held against the decisions that set them; 0 problems
--- D9-efficacy        (7 plants and 1 against the records, then 6 in the CSR and the exceptions: each with problems)
--- D11-efficacy-5b    (25 plants and 2 against the records, each with problems; the four of G1:)
planted, a proof whose pattern carries the CSR's text ('X.2727', other_pattern): 1 problems, ... the other pattern 'X.2727' of p changes more than the mask of ...
planted, a proof whose pattern carries the CSR's text ('X.2727', other_build): 1 problems, ... (the same)
planted, gold's week 8 p-value is week 16's, proved by a pattern that carries the CSR's text: 1 problems, ... ours '0.400', CSR '0.2727': ... the other pattern 'X.2727' of p changes more than ...
planted, a proof of 14-3.11 whose pattern carries the CSR's text ('X.X (0.49)'): 1 problems, ... the other pattern 'X.X (0.49)' of lsm changes more th...
--- D12-cmh-engines    (4 plants, each with CMH results that disagree)
63 passed in 97.18s (0:01:37)
ASCII check: 590 files checked, 0 with non-ASCII bytes
PASS environment, pins, lint, registry, unit tests, method vectors, kit, P1 determinism,
     P2 reproduction, trace, results, efficacy, E22 hint, CMH, decisions, pilot tests,
     planted defects, cache untouched, ASCII   (19 of 19)
GATE real-5b: PASS
```

#### E2. The check of the cells, on the build of E1 (no engine)

`plants3.py` calls the functions the gate calls (`build.csr_against` for
each table against its CSR table, the kit's exceptions and its records;
`decisions.problems`; `efficacy_problems` of tests/defects, D11's own) on
`gate-real-5b/build/p1/cdiscpilot01/first`. The `B` plants are pass 2's;
`T` are new: a proof whose other template carries text in the format specs
of its fields, `filled(part, text)` = one field `{part:c<1.0}` per character
c of the CSR's text (the part cut to no characters, padded to width 1 with
c).

```text
control Out14-3-11: 24 cells, 15 printed, 12 equal, 12 differ, 12 classified ['rule_choice'], 0 problems
control Out14-3-13: 100 cells, 78 printed, 76 equal, 24 differ, 24 classified ['rule_choice'], 0 problems
control: classified 36; decisions: 0 problems
   entries Out14-3-01, 03, 05 other_pattern patterns {"lower": "X.X", "upper": "X.X"}: 3 each
   entries Out14-3-11 other_build patterns {"lower": "X.X", "upper": "X.X"}: 3; patterns {}: 9
   entries Out14-3-13 other_build patterns {}: 21; other_pattern patterns {"p": "X.XXXX"}: 3
B1  14-3.13 r2/c4 (gold right) proved by other_pattern {p: 'X.2727'}: 1 problems -> seen; ... the other pattern 'X.2727' of p changes more than the mask of 'X.XXX'
B1b the same by other_build {patterns: {p: 'X.2727'}}: 1 problems -> seen; (the same)
B1c other_pattern {p: '0.X'} (text before the mask): 1 problems -> seen; ... '0.X' of p changes more than the mask of 'X.XXX'
B1d other_pattern {p: ' X.XXXX'} (a blank before the mask): 1 problems -> seen
B1e other_pattern {p: 'XXXX.XXXX'} (a wider mask, genuine digits): 0 problems -> passes
B2  gold's week 8 p-value cell now (ours, CSR): ('0.400', '0.2727')      (layout: the week 8 row shows An_CIBIC_W16_Cmh)
B2a gold wrong, the entry as it is: 1 problems -> seen; ... with the other patterns the cell is '0.4003'
B2b gold wrong, the entry's pattern 'X.2727' (other_pattern): 1 problems -> seen; ... changes more than the mask of 'X.XXX'
B2c gold wrong, the entry's pattern 'X.2727' (other_build): 1 problems -> seen; (the same)
B6  the 12 entries of 14-3.11 with literal-pattern proofs (made for 7 of 12), gold as it is: 7 problems -> seen; ... the other pattern 'X.6 (0.49)' of se changes more than the mask of 'X.XX'
T0  csr._template_names / _literal of '{p:2<1.0}{p:7<1.0}': ['p', 'p'] ''
T0  layout.template_names('{p:2<1.0}'): refused: cell template '{p:2<1.0}': write a part as {name}
T1  template: {p:0<1.0}{p:.<1.0}{p:2<1.0}{p:7<1.0}{p:2<1.0}{p:7<1.0} -> '0.2727'   (formatted with p = '0.400')
T1  14-3.13 r2/c4 (gold right) proved by other_build {template: <that template>}: 0 problems -> NOT SEEN
T2  gold wrong (week 16's p in the week 8 row), proved by that template: 0 problems -> NOT SEEN
T2' the same through tests/defects' efficacy_problems (D11's function): 0 problems -> NOT SEEN
T2b the same, template '{p:.0}0.2727' (literal text): 1 problems -> seen; ... the other template must show parts of the cell and add no text the cell's template has not
T3  14-3.13 r2/c4 proved by template '{p!r}' with pattern X.XXXX: 1 problems -> seen; ... with the other build the cell is "'0.2727'"   (the conversion is accepted; only the quotes fail)
T4  the 12 entries of 14-3.11 proved by fill templates (gold as it is): 0 problems -> NOT SEEN
    e.g. cell:Out14-3-11/r2/c1 {lsm:1<1.0}{lsm:.<1.0}{lsm:6<1.0}{lsm:(<1.0}{lsm:0<1.0}...
T4b the same, each fill template with the entry's averaged analyses: 0 problems -> NOT SEEN
T5  the 24 entries of 14-3.13 proved by fill templates (gold as it is): 0 problems -> NOT SEEN
E22 by the gate's rule (my copy of the conditions of gates._e22_hint, on this table and these entries):
    control: at Week 24 0 of 12 equal the CSR; entries naming averaged analyses 12; classified 12: the hint holds
    T4:      ... entries naming averaged analyses 0; classified 12: not shown
    T4b:     ... entries naming averaged analyses 12; classified 12: the hint holds
```

`S`, every other_build without format specs, searched: templates of 1 to
3 fields from the cell's parts (repeated or not), the cell template's
literal text as any subsequence split among the gaps; for each part the
masks X to X.XXXXX with the part's own text around them; both display
rules; and, as other analyses, every analysis of the event that the widest
list of decisions binding the cell allows (`_stripped` on the union of
their options). A candidate whose text is the CSR's is then held by
`csr._other_build` itself.

```text
S control 14-3.11 (gold right): 12 cells with a proof that holds; 31914 candidate proofs tried
   (each the entry's own proof: the averaged analysis, patterns X.X and X.XX or X.XXX; r4/c2 with display.pattern.signed)
S control 14-3.13 p-values (gold right): 3 cells with a proof that holds   ({p} with X.XXXX)
S B2 gold wrong (week 16's p in the week 8 row): 0 cells with a proof that holds; 36 candidate proofs tried
```

#### E3. Both engines on changed events (under the lock, on the build of E1)

```text
   LOCF alone (gold's Week 24 analyses on the records LOCF adds): gold's cells of the model: r2/c1 '2.3 (0.60)', r2/c2 '1.8 (0.59)', r2/c3 '1.3 (0.62)', r3/c2 '0.613', r3/c3 '0.237', r4/c2 '-0.4 (0.82)', ...
C8h-2 gold's Week 24 analyses alone on the LOCF records: efficacy: 12 problems -> seen; ... An_ADAS_MMRM_LSM_Avg differs from An_ADAS_MMRM_LSM in more than the options at of custom:eff-mmrm-visit
C8h-2 the same: decisions: 0 problems
B3  the same wrong gold, literal-pattern proofs (made for 9 of 12): 12 problems -> seen; ... the other pattern 'X.6 (0.49)' of se changes more than the mask of 'X.XX'
T6a the same wrong gold, the 12 entries proved by fill templates: 0 problems -> NOT SEEN
    E22 by the gate's rule: ... entries naming averaged analyses 0; classified 12: not shown
T6b the same, fill templates with the averaged analyses: 12 problems -> seen; ... differs from An_ADAS_MMRM_LSM in more than the options at ...
S LOCF gold wrong (Week 24 analyses alone): 0 cells with a proof that holds; 320436 candidate proofs tried
   LOCF in all six analyses (D11's plant "the mixed model with the records LOCF adds"): gold's cells of the model: the same as LOCF alone
T6c LOCF in all six, the entries as they are: efficacy: 12 problems -> seen; ... with the other build the cell is '1.5 (0.48)'
T6c the same: decisions: 0 problems
T6d LOCF in all six, fill templates with the averaged analyses: efficacy: 0 problems -> NOT SEEN
    E22 by the gate's rule: at Week 24 0 of 12 equal the CSR; entries naming averaged analyses 12; classified 12: the hint holds
S LOCF in all six (gold wrong): 0 cells with a proof that holds; 640872 candidate proofs tried
C8h-1 gold's Week 24 analyses alone at 90%: efficacy: 12 problems -> seen; ... in more than the options at of custom:eff-mmrm-visit
C8h-1 the same: decisions: 0 problems
S 90% gold wrong (Week 24 analyses alone): 0 cells with a proof that holds; 320436 candidate proofs tried
T7  all six analyses at 90%, the entries as they are: efficacy: 3 problems -> seen; ... ours '(-2.28;1.09)', CSR '(-1.4;1.3)': ... with the other build the cell is '(-1.2;1.1)'
T7  the same: decisions: 0 problems
T7b all six at 90%, fill templates with the averaged analyses: efficacy: 0 problems -> NOT SEEN
    E22 by the gate's rule: ... entries naming averaged analyses 12; classified 12: the hint holds
   visits by AVISIT (record custom:eff-mmrm-terms and six analyses): gold's cells of the model: r2/c1 '0.6 (0.48)', r2/c2 '1.6 (0.47)', r2/c3 '0.8 (0.50)', r3/c2 '0.108', ...
G2  the visits ordered by AVISIT (record and six analyses): efficacy: 0 problems -> NOT SEEN
G2  the same: decisions: 0 problems -> NOT SEEN
```

#### E4. The unit tests of the proofs, and the new cases against the old check

```text
$ python -m pytest -q -p no:cacheprovider tests/unit/test_efficacy.py tests/unit/test_efficacy_5b.py tests/unit/test_gates.py -m "not evidence"   (clone of 1b0ad01)
88 passed in 1.73s
$ git show 753b5ac:src/specfirst/machine/csr.py > src/specfirst/machine/csr.py   (the check without _pattern_problems; restored after)
$ python -m pytest -q -p no:cacheprovider tests/unit/test_efficacy.py tests/unit/test_efficacy_5b.py -m "not evidence"
FAILED tests/unit/test_efficacy.py::test_a_difference_is_classified_by_its_one_proof
FAILED tests/unit/test_efficacy_5b.py::test_an_other_build_that_proves_nothing[proof12-the other pattern '-X.X' of d changes more than the mask of 'X.X']
FAILED tests/unit/test_efficacy_5b.py::test_an_other_build_that_proves_nothing[proof13-the other pattern of d is no pattern]
3 failed, 66 passed in 1.30s
```

#### E5. The gate real-5a on my clone of 1b0ad01

```text
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 python -m specfirst gate real-5a   (687 lines)
gate real-5a at commit 1b0ad01af02d1e2c747affc53f0a8c18fb85dc21 (clean)
1203 passed, 30 deselected in 336.80s (0:05:36)
grid Out14-3-01 against CSR Table 14-3.01: 51 cells, 40 of them printed in the CSR; 48 equal the CSR, 3 differ, 3 of them with one class and a proof that holds
grid Out14-3-03 against CSR Table 14-3.03: (the same: 3 differ, 3 with one class and a proof that holds)
grid Out14-3-05 against CSR Table 14-3.05: (the same)
grids: 6 outputs, pass
efficacy: 3 tables, 153 cells; 144 equal the CSR; classified differences: 9 rule_choice
decisions: 18 records, 18 IDs; 99 options of analyses held against the decisions that set them; 0 problems
--- D9-efficacy
unchanged: 0 problems
planted, the ANCOVA without the baseline covariate: 19 problems, ... (and 6 more plants, the records plant: 9 problems)
planted, an exception whose other pattern proves nothing (3 decimals): 1 problems, ... with the other patterns the cell is '(-2.079;1.145)'
planted, an exception left out / with the class reference_error / that names no decision record: 1 problems each
63 passed in 96.80s (0:01:36)
PASS environment, pins, lint, registry, unit tests, method vectors, kit, P1 determinism, P2 reproduction,
     trace, results, grids, efficacy, decisions, pilot tests, planted defects, cache untouched, ASCII   (18 of 18)
GATE real-5a: PASS
```

#### E6. Counts the report and ADR-015 state

```text
model.mmrm.lsmeans statements: 11; model.mmrm.pairwise: 7; test.cmh: 7; display.pattern.signed: 2
test_cmh cases: 12; model_mmrm_lsmeans: 15; model_mmrm_pairwise: 8; display_pattern_signed: 7
tests/unit/test_efficacy_5b.py, test_an_other_build_that_proves_nothing: 14 parametrized cases
```

### Answers to the four questions

#### 1. G1, the 45 genuine entries, and other ways in

G1 is fixed as asked. A pattern of a proof that changes more than the mask
is refused in both proof kinds, with the text before or after it, a blank
included: B1, B1b, B1c, B1d (gold right) and B2b, B2c (gold wrong) are
seen, by "changes more than the mask"; B6, pass 2's literal patterns for
the 12 entries of 14-3.11, is seen in all 7 cells it reaches, and B3, the
same on gold's Week 24 analyses on the LOCF records, in all 12 (the 9
literal patterns refused, the 3 others by the rule on other analyses; E2,
E3). A
wider bare mask still holds where the digits are the cell's own (B1e),
which is right. The four plants of G1 are in the gate's D11 and seen (E1),
and the four new unit cases fail on the check of `753b5ac` (E4: 3 tests;
the two cases of test_efficacy.py are in one test). The 45 genuine entries
hold: 12 and 24 of real-5b (E1, E2 control), 3, 3 and 3 of real-5a (E5);
each uses bare masks (E2: X.X, X.XXXX, or none).

Other ways in. Not by a pattern, an analysis, a display rule or a list of
decisions: my search over every template without format specs, every mask,
both display rules and every other analysis the widest list of decisions
binding the cell allows finds the 15 genuine proofs where gold is right,
and no proof for any cell where gold is wrong, in four wrong golds (B2 in
14-3.13; gold's Week 24 analyses alone on the LOCF records or at 90%; all
six analyses on the LOCF records; 0 cells each, up to 640872 candidates,
E2, E3). But by a template, yes: the format spec of a field carries text
(H1). A proof of one part repeated, whose specs spell the CSR's text, holds
for every one of the 36 cells (T1, T4, T5), and it gets wrong gold numbers
of both tables past the proofs: 14-3.13 with the week 8 row showing the
p-value of week 16 (T2, T2': 0 problems); 14-3.11 with all six analyses of
the mixed model on the records LOCF adds (gold's LS means 2.3 (0.60), 1.8
(0.59), 1.3 (0.62) ...) or at 90% (gold's limits (-2.28;1.09) ...), the
entries keeping their averaged analyses: `efficacy` 0 problems, `decisions`
0 problems, and the rule of `E22 hint` holds (T6d, T7b). Where gold's Week
24 analyses alone are wrong, the averaged analyses can no longer be named
(T6b) and without them `E22 hint` fails (T6a): that much the fix of F1
still guards. And G2 stays as stated (E3, below).

#### 2. G2 and G3

G2: stated where the commit says, in the report ("What the checks do not
cover", "For the owner") and in ADR-015 ("For the owner" item 6), and the
statement holds: with AVISIT in the record `custom:eff-mmrm-terms` and in
the six analyses, gold's table shows the LS means of Week 8 (0.6 (0.48),
1.6 (0.47), 0.8 (0.50) ...) under the title "to Week 24", and `efficacy`
and `decisions` give 0 problems (E3).

G3, for `1b0ad01` (the commit with the gate of `1b0ad01` is not on
`origin/track/real`): the figures that do not come from the gate are
refreshed and right: 11 and 7 statements (E6; the report's table and
ADR-015 decision 12), 12, 23 (15 and 8) and 7 vectors (E6), 14 proofs that
prove nothing (E6), 2 cases in test_efficacy.py, the third item of real-5a's
list now said not to hold (true: pass 2, A4). The gate's figures in the
report and the log are still those of the clean clone of `10c6bbc` (H2): on
`1b0ad01` the gate gives 1203 tests (report 1196), 139 Python cases of 11
methods (136 of 10), 134 R cases (131), 134 exact and 63 by hand (131 and
60), 58 model-based (55), and D11 25 plants and 2 against the records (the
report's summary: "D11 (18 plants)"; its D11 output lacks the plants added
by passes 1 to 3); the lines of the checks `efficacy`, `E22 hint`, `CMH`,
`decisions`, `results`, P1 and the paths are the same (E1). I cannot say
whether the next commit carries them; it should carry E1's figures.

#### 3. What the fix may have broken

Nothing I could find. The gate real-5a passes on my clone of `1b0ad01`,
its 9 other_pattern entries hold (bare X.X for parts of pattern X.XX) and
D9 sees each of its plants, the bad other pattern and the reference_error
included (E5). The unit tests of the proofs pass (88, E4; 86 at `753b5ac`
plus the 2 new parametrized cases). D11 passes with its four new plants
(E1), D12 as before. The gate real-5b passes (E1). `_pattern_problems` only
adds reasons; a part whose own pattern had text around its mask would need
the same text in its other pattern, and no entry of the kit has one.

#### 4. The changed statements

Supported: ADR-015 decision 12 ("11 and 7 statements", E6); decision 16's
new sentence on patterns ("changes only the mask ... so that no pattern
carries the CSR's text", E2, E3); "For the owner" item 6 (G2, E3); the
exceptions file's "other `patterns` (another mask, the text around it the
part's own; so for other_pattern too)"; the report's new bullets of "What
the checks do not cover" and "For the owner", and its counts (E6). One
small inaccuracy: "test_gates.py plants ... one way the engines disagree on
CMH": its test plants three (a value moved by 2e-9, a row left out, a
missing value; pass 2, F2).

Not supported, unchanged since pass 2 but now the open way in (H1): ADR-015
decision 16, "another template shows parts of the cell and adds no text
its template has not"; the exceptions file, "another cell `template` (parts
of the cell, no text of its own)"; the docstring of csr.py, the same; and
`csr._template_names`, "as specfirst.machine.layout.template_names", which
refuses what it accepts.

### Findings

#### H1 (blocks the merge): the other template of a proof may carry text in the format specs of its fields, so a proof that proves nothing still holds and wrong gold numbers of both tables still pass

Where: `csr._template_names` and the template branch of `csr._other_build`
(csr.py); stated otherwise in csr.py's docstring, ADR-015 decision 16 and
the exceptions file's comment.

What: pass 1's F1 (item 2) and pass 2's G1 closed two ways for a proof to
carry the CSR's text: the template's literal text and a pattern's text
around its mask. A third is open. `_other_build` takes the part names of
the other template from `string.Formatter().parse` and holds its literal
text (a subsequence of the cell template's); the format spec and the
conversion of each field are not looked at, and the template is then
filled by `str.format`. A format spec carries text: `{p:2<1.0}` is the part
p cut to no characters and padded to width 1 with the character "2",
whatever p is. So `{p:0<1.0}{p:.<1.0}{p:2<1.0}{p:7<1.0}{p:2<1.0}{p:7<1.0}`
is "0.2727" for any value; it has no literal text and names only a part of
the cell, and it holds as a proof (T0, T1). The layouts' own
`layout.template_names` refuses a spec or a conversion ("write a part as
{name}", T0); `csr._template_names`, which says it works "as" that
function, does not.

Evidence (E2, E3): every one of the 36 cells holds with such a template
(T1, T4, T5), and with the entries' averaged analyses kept the rule of
`E22 hint` holds too (T4b). Wrong gold of 14-3.13: the week 8 row showing
the CMH p-value of week 16 ("0.400" where the CSR prints "0.2727"), seen
with the entry as it is (B2a), passes with that template (T2, and T2' by
D11's own function); no other check of the gate compares that cell. Wrong
gold of 14-3.11: all six analyses of the mixed model on the records LOCF
adds (D11's own plant, seen with the entries as they are: T6c, 12
problems), or all six at 90% (T7, 3 problems), pass `efficacy` (0
problems), `decisions` (0) and the rule of `E22 hint` (holds) once the 12
entries prove by such templates and keep their averaged analyses (T6d,
T7b). Without format specs no proof of a wrong gold cell exists in my
search (S, 0 cells in four wrong golds), so this is the one way left.

Fix (small; no number and no genuine entry changes): take the other
template's part names with `layout.template_names` (it refuses a spec and a
conversion) or refuse any field with a spec or a conversion in
`_template_names`; plants: T2 and T6d (or T7b) in D11, and a unit case in
test_efficacy_5b.py (a template such as `{d:-<1.0}{d:0<1.0}...`, and one
with `!r`). The 36 entries use `{n}` or no template, so they still hold.

#### H2 (does not block): at 1b0ad01 the report's gate figures and its log are still those of 10c6bbc

Where: docs/reports/real-5b.md, sections "Verdict" ("clean clone of commit
`10c6bbc`", "D11 (18 plants)"), "The methods" (the method vectors' lines),
"The gate" (1196 tests, the log of 685 lines), "Planted defects" (the D11
output), "The gates on clean clones"; docs/reports/real-5b.clean-clone.gate.log.

What: pass 2's G3, as far as the gate goes; the commit says these follow
from the clean-clone gate of `1b0ad01`, which is not on
`origin/track/real` when I finish. E1 gives what they should be on
`1b0ad01` (answer 2). Also the one-word slip on test_gates.py's CMH plants
(answer 4).

Fix: the clean-clone gate of the commit that merges (after H1's fix), and
these figures with it.

### The owner's choices (PLAN.md section 2.3)

Passes 1 and 2 list them; nothing new. H1 is not the owner's: it is a hole
in the check, as F1 and G1 were. On G2 (pass 2's item 4) my runs agree with
what the report and ADR-015 now say.

### Verdict

G1 is fixed and works: no pattern can carry text any more, in either proof
kind, and every plant of passes 1 and 2 is refused by the rule meant for it
(E2, E3); the 45 genuine entries hold, and the gates real-5b and real-5a
pass on my clones of `1b0ad01` (E1, E5), with the new plants seen and the
new unit cases failing on the old check (E1, E4). G2 is stated and true.
G3 is done for the figures outside the gate; the gate's own wait for the
next commit (H2).

One finding blocks: a proof's other template can still carry the CSR's
text, through the format specs of its fields, which `layout.template_names`
refuses for the layouts but the proof's check does not (H1). With it a
proof that reads nothing holds for every cell, and wrong gold numbers of
both tables pass `efficacy`, `decisions` and the rule of `E22 hint` (T2,
T6d, T7b). My search found no other way: without format specs no wrong
gold cell has a proof (S). The fix is one call and two plants.

Verdict: NOT SIGNED (blocking: H1)
