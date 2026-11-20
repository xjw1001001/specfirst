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
