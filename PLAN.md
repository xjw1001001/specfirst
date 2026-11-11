# specfirst: an open-source, spec-first framework for clinical analysis and reporting

Plan v0.2.1, 2026-11-11. Revised after the design review of 2026-11-10 and
11. Section 17 lists the 22 decisions of that review.
Owner: Jingwei Xiong. Executor: Claude Code (Opus 5.5).
`specfirst` is a working name. Nothing depends on it.

## How to use this file

1. In WSL2 (Linux), make a new folder that holds no employer material.
   Copy this file and the `evidence/` folder into it. Log in to GitHub once
   with `gh auth login`.
2. Start one Claude Code session there. First prompt:
   `Read PLAN.md completely. Do work package base-0 only. Stop at its gate and write docs/reports/base-0.md.`
   base-0 begins by putting the folder under git and creating the owner's
   private GitHub repository.
3. After base-0, run up to four sessions in parallel, one per track
   (section 13), each in its own git worktree. Prompt for each:
   `Read PLAN.md sections 2 and 13 and docs/state/<track>.md. You own track <track>. Do its next work package whose dependencies are met.`
4. A work package is done when its gate command exits 0 and an independent
   reviewer agent has signed its report. The session then goes on to the
   next package. It stops only at the three owner nodes of section 2.3.
5. This file changes only through an ADR in `docs/decisions/` that the owner
   approves. Sections 4 and 5 are contracts. Sections 6 to 12 are designs
   that an ADR may improve.

Contents: 1 What we are building. 2 Rules. 3 Evidence. 4 The standard.
5 Decision catalog. 6 Studies. 7 Machine. 8 Kit format. 9 Scoring.
10 Units and knowledge. 11 Harness and training loop. 12 Repository layout.
13 Tracks, work packages and gates. 14 Upstream. 15 Risks. 16 Open
questions. 17 Decisions of the design review.
Appendices: A pins, B seed catalog, C glossary, D the 30 CSR tables.

## 1. What we are building

AI reads; machines build. A language model turns a study's free-text
protocol and SAP into a short list of decisions in a standard form. Fixed
machinery compiles those decisions into specifications and builds every
dataset and output. Every printed number traces back to its analysis, its
derivation rule, its source data and the sentence that justified it.
Simulated studies with known answers make the model's reading measurable,
so it can be improved.

| Product | Contents | Used by |
| --- | --- | --- |
| Standard | trace model, decision catalog with its standard form, method registry, kit format | anyone describing a study |
| Machine | compile and build from decisions: ADaM, results, displays, trace graph; checkers; scorer; the edit loop for people | programmers, reviewers, CI |
| Gym | study generator by trial design, reader agent and harness, training loop, exams | whoever trains or tests the reader |

The work splits into two stages.

| Stage | Who | In | Out |
| --- | --- | --- | --- |
| Read | the reader agent, a language model | protocol, SAP, house standards, the catalog | one decision record per applicable decision, in standard form, with quotes; questions for a person; statements it could not map |
| Build | the machine, no model | decision records and SDTM data | yamaa ADaM specs, ARS and layout files, then ADaM, ARD, display grids and the trace graph |

People review the standard form: uniform sentences, each linked to its
source quote and to the cells it affects. To change something, a person
tells the agent, the agent edits the decision, and the machine rebuilds and
shows what changed (section 7.6).

"Training" means improving the reader's working system (skills, knowledge
files, tools) against gold. It never means changing model weights.

M1 has three deliveries.

| Delivery | Content | Target |
| --- | --- | --- |
| D1 | CDISCPILOT01 end to end: the 16 descriptive CSR tables built from specs, the study map, and the edit loop | end of week 3 |
| D2 | the 14 model-based CSR tables (ANCOVA, mixed model, CMH), so that all 30 CSR tables are done | end of week 5 |
| D3 | generated studies for the parallel-group design, the reader agent, and its first scores | end of week 7 |

The targets assume four parallel sessions and automatic gates. They are
estimates. Recalibrate them after the first week from the measured pace.

Out of scope for M1:

- Everything before SDTM (study design as data, CRF collection, SDTM
  mapping) is a placeholder. SDTM, the protocol and the SAP are inputs.
- Study-specific derivations outside the catalog (M2).
- Clinical realism of simulated efficacy, any server, model fine-tuning.
- Any claim of regulatory validation. Agreement with a reference is
  evidence, not validation.

## 2. Rules

### 2.1 Clean room

These have no exceptions. Enforce the first two with deny rules in
`.claude/settings.json` wherever such a path exists.

1. Public sources only. Record every imported file in
   `third_party/SOURCES.md` with URL, commit and license.
2. Never read a folder named `reference/` or any employer material. If the
   owner pastes text that looks internal (tool names, study numbers,
   unpublished metrics), stop and ask.
3. Unit names, module boundaries and table families come from public
   standards: ADaMIG and OCCDS, ICH E3 section 14, the FDA Standard Safety
   Tables and Figures Integrated Guide, the CDISC ARS examples, and the
   admiral and cardinalfda APIs. Each catalog entry cites its source.
4. Do not redistribute third-party study data or documents. CDISC pilot
   material and Pilot 7 synthetic data are fetched at pinned commits into an
   ignored cache (E20). Reference grids parsed from the CSR stay in the
   cache too; only the parser is committed.
5. Original code and documents are MIT.
6. Publishing is the owner's act. Pushing to the owner's private repository
   is allowed and expected. Anything other people can see needs the owner's
   approval of the exact text first: an issue, a pull request or a comment
   on someone else's repository, a post, or a change of this repository's
   visibility. Draft it and stop.
7. One-way flow. The framework may be used anywhere, including on an
   employer's machines and on an employer's studies. Nothing produced there
   comes back into this repository: no results, logs, lessons, kits, catalog
   entries or fixes. One exception: the owner may report, by hand, aggregate
   scores from runs there on public or generated studies. Such scores guide
   the work. They are not committed and not published; a number that is
   committed or published is run again on the owner's own equipment. Nothing
   about an employer's studies comes back in any form. A defect found there
   is first reproduced on public or generated data, then fixed here.

### 2.2 Engineering

| # | Rule |
| --- | --- |
| R1 | Agents propose, scripts decide. Nothing an agent writes counts until a deterministic check passes. |
| R2 | Reuse before build. Before writing a component, check the projects in section 3. Record reuse, wrap or build in an ADR. |
| R3 | Pin everything. Engines by version, inputs by SHA-256, one manifest per kit. Every replay checks for drift first. |
| R4 | Determinism. No clock, no unseeded randomness, sorted outputs, canonical serializers. Same inputs give the same bytes. Logs of human edits may carry time stamps; built artifacts may not. |
| R5 | Tests first. A checker or scorer is trusted only after it fails on planted defects (section 9.5). |
| R6 | Specs carry rules, not numbers. A spec that only works on the data it was written against fails the twin check (section 6.5). |
| R7 | Independent review at every gate: a fresh-context agent that did not write the work reviews the diff against this plan. Correctness only, no style. |
| R8 | Reports show evidence: the command and its output, not a summary. |
| R9 | Keep scope. A work package starts only when its dependencies have passed. No second trial design before D3. |
| R10 | ASCII only in maintained files, to keep upstreaming to Pilot 7 easy. |
| R11 | Two engines, one answer. Every result of a descriptive method, a simple test or a CMH test is computed in Python and in R. A disagreement blocks the gate. |

### 2.3 Owner nodes and stop-and-ask

Gates pass automatically: the gate script exits 0 and the reviewer agent
signs the report. Work stops for the owner at three nodes only.

| Node | When | What the owner decides |
| --- | --- | --- |
| N1 | after std-1 | the decision catalog, the standard form and the house standard for the M1 families. This is the contract. |
| N2 | at real-4 and real-5 | the class of every difference between our tables and the CSR, and which rule is gold where the CSR and the reference ADaM follow different rules (section 4.8) |
| N3 | before D1, D2 and D3 | whether the delivery is ready to show |

Outside the nodes, stop and ask when: a license is unclear; a gate cannot
pass without changing the gate; a public standard is ambiguous and no public
source settles it; an action publishes or deletes; a work package exceeds
twice its budget; or two reused components conflict.

### 2.4 Session protocol

- One session per track, each in its own git worktree on branch
  `track/<name>`. A work package merges to `main` only after its gate and
  its review pass. Push `main` and the track branches to `origin` after
  each merge.
- `CLAUDE.md` stays under 60 lines: the commands for tests and gates, the
  rules above in one line each, and the gotchas found so far. base-0
  creates it.
- `docs/state/<track>.md` is each track's handover: what passed, what is
  open, what is next. `specfirst status` prints all of them.
- `docs/reports/<wp>.md` holds the gate evidence and `<wp>.review.md` the
  reviewer's verdict.
- `docs/decisions/ADR-nnn.md` records each choice with its evidence.
- `docs/lessons.md` records each failure once, with the check that now
  catches it.
- The environment is WSL2 Linux with Python and R side by side. Lock files
  live in `env/`.

## 3. Evidence (verified 2026-11-10 and 11)

Each row was checked against the pinned sources in appendix A. E1 to E5 and
E24 to E27 were run in a clean Linux sandbox with the scripts in
`evidence/`.

| # | Verified fact | Source | Consequence |
| --- | --- | --- | --- |
| E1 | yamaa 0.7.0 (PyPI wheel) rebuilds all 10 CDISCPILOT01 ADaM datasets from Pilot 7's specs: 9,119,605 cells, 0 mismatches, 14 seconds. | Pilot 7 | SDTM to ADaM is solved. Reuse it. Our work starts at the analysis layer. |
| E2 | A 170-line generic interpreter reproduces 3,711 of the 3,735 results embedded in the CDISC ARS v1 example (5 outputs, 31 analyses), p-values included. | ARS repo | ADaM to results works with fixed machinery and no per-table code. |
| E3 | The other 24: 22 values are exchanged between the two active arms (20 counts and percents for ethnicity and race, 2 height means), 1 height median differs, 1 p-value is empty. The pilot ADSL gives our numbers, and CSR Table 14-2.01 confirms them where its categories are comparable (Hispanic 3, 6, 3; height means 163.4 and 165.8; height median 162.6). | ARS repo, CSR | Gold must be proven by reproduction, and every difference classified. Official examples contain errors too. |
| E4 | Switching quantiles from the SAS default to the R default changes 49 more results. | ARS repo | ARS alone is not executable. Methods need numbered semantics: the method registry. |
| E5 | The 5 outputs read 23 of the 137 variables in ADSL, ADAE and ADVS directly. | ARS repo | Scope follows the outputs. The reader decides what outputs need; templates complete the rest. |
| E6 | Pilot 7 compared documents with reproducing rules for 222 CDISCPILOT01 variables. Of 690 clauses, 64% agree, 19% differ, 7% are missing from the documents, 5% contradict them, 4% are missing from the spec. | Pilot 7 `spec/review/*-claims.json` | ADaM is hard mainly because documents are incomplete. Decisions need classes, and silence needs a rule. |
| E7 | Pilot 7's verifier has the verdict `equivalent_on_data`: a rule differs from the documented one but gives the same values on this data. Its ADSL review notes that SITEGR1 is specified as a list of sites, not as the pooling rule. | Pilot 7 `verify_derivations.py`, `adsl-claims.json` | Real data cannot separate many rules. Generated data must. |
| E8 | KN189 and KN564 (real protocol, simulated data) carry 17 and 19 review findings. All are open. | Pilot 7 `findings.json` | Human-reviewed gold does not scale. Gold by construction does. |
| E9 | The CDISC pilot protocol exists as USDM v4.0 JSON (3 arms, 5 epochs, 12 encounters, 40 activities, 11 endpoints, 1 estimand), next to a redacted protocol PDF. | cdisc-org/360i | The design layer has a public standard and a public instance. We reserve its place and build it later. |
| E10 | CDISC 360i Phase 2 (ADaM to TLF) is under way and plans to use ARS, siera and admiral. Its roadmap says a synthetic raw data generator will be an important part of the infrastructure. | 360i roadmap posts | The gap is recognized. Align with 360i; do not compete. |
| E11 | CDISC Analysis Concepts (AC/DC) publishes a method library and an eSAP schema, both v0.x, with no executable gold. | cdisc-org/analysis-concepts | Cross-reference method IDs. Do not depend on it at run time. |
| E12 | siera 0.5.6 turns ARS JSON into R scripts that compute ARDs and stamps each row with ARS IDs. It has 13 method templates. | clymbclinical/siera | A candidate base for the R engine. Try it before writing our own. |
| E13 | cardinalfda implements the FDA safety tables on gtsummary, cards and cardx. The FDA guide itself is public (MAPP 6025.9). | pharmaverse/cardinal, fda.gov | A public house standard for safety tables, with an independent implementation. |
| E14 | Pilot 6 holds the CDISCPILOT01 CSR (492 pages; table numbers 14-1.01 to 14-7.04, 30 in all, and Figure 14-1) and the SAP. Its 3 finished tables are hand-written R. | Pilot 6 | TFL gold for the real study, and the contrast case: AI writes code. |
| E15 | The CSR reports race as origin (Caucasian 75, 72, 71). ADSL has no such variable, yet RACE and ETHNIC rebuild it exactly. | CSR, ADSL | Real tables need study-specific groupings: a custom decision, flagged and counted. Try to derive before calling a difference a data problem. |
| E16 | pharma-skills has admiral skills that require an existing ADaM spec, and no skill that writes a spec or a TFL spec. Skills are benchmarked with and without the skill. | RConsortium/pharma-skills | Our reading knowledge ships as Agent Skills. The niche is open. |
| E17 | `clinical-trial-ipd-sim` builds one cited causal model per trial, calibrated to posted results, and emits CRF data as ODM v2.0. It plants no decision probes and builds no gold spec. | pharma-skills | Build the decision-aware generator. Reuse its conventions when the CRF layer is added. |
| E18 | yamaa specs inherit from a parent. Resolved specs record the source file and line of every element. Its agent evaluation states rules in tiers (full, conventions, brief). | yamaa | Parent specs carry the house standard. Build the trace from resolved specs. |
| E19 | Pilot 7's own runner refuses a wheel install. It requires yamaa installed from the pinned git revision, which needs Rust 1.99.1. | Pilot 7 `resolved_specs.py` | Use our own thin runner with the wheel, or build from source. Decide in real-1. |
| E20 | Pilot 7 excludes all study data from its MIT grant. CDISC pilot data stay under CDISC terms. | Pilot 7 `LICENSING.md` | Fetch data at build time. Do not commit it. |
| E21 | Pilot 7 has yamaa specs, cited claims, a verifier and a review dashboard for ADaM. Every study's `tlf/` folder is empty. | Pilot 7 | The ADaM half exists upstream. The TFL half and the cell-level trace are ours to add. |
| E22 | Atorus publishes R programs and outputs for all 30 CSR tables, updated in 2026, with its divergences listed. Its notes fix method details: the repeated-measures table matches SAS when fitted with `mmrm` (unstructured covariance, Kenward-Roger); the CMH tables match with `coin`. It compares with its own earlier R outputs, not with the CSR, and its dataset names show another edition of the pilot ADaM than Pilot 7's. | atorus-research/CDISC_pilot_replication | A source of method details and of hints. It does not settle what the CSR printed (E26). |
| E23 | 16 of the 30 CSR tables are descriptive or use simple tests (Fisher, ANOVA, chi-square), by their footnotes and E27. The other 14 use ANCOVA with a dose-response test, a mixed model, or CMH. Appendix D lists them. | CSR | Two batches: D1 and D2. |
| E24 | CSR Table 14-2.01 (demographics): all 244 printed cells reproduce from the public ADSL, p-values included, with rounding half away from zero and the origin grouping of E15. | CSR, ADSL | The descriptive CSR tables are within reach from public data. |
| E25 | CSR Table 14-5.01 (adverse events by organ class and term, 16 pages, 254 rows): all 1,175 printed cells reproduce from the public ADAE, given three display rules found by trial: terms cut at 38 or 40 characters, trailing zeros dropped from p-values, and p-values of 0.001 or more rounded to 4 decimals and then to 3. With correct single rounding, 4 p-values differ by 0.001. | CSR, ADAE | Display rules need numbered semantics too. A reference's rounding quirk is the owner's call at N2: reproduce it as a declared option, or print the exact value and record the difference. |
| E26 | CSR Table 14-6.06 (Hy's law shifts, with CMH): the CSR's two p-values follow from its own printed counts. All 51 printed cells reproduce from the public data under two rules. First, a subject is High when any visit during treatment is high; the SAP states this rule ("the most extreme value"), though the table's footnote reads differently. Second, baseline is the last value before the first dose, unscheduled included. The SAP names Visit 1 as baseline and the reference ADaM follows it, so two subjects whose only pre-dose samples are unscheduled (visits 1.2 and 1.3) have none; with that baseline, 45 cells match and the p-values are 0.405 and 0.386, not 0.392 and 0.381. Atorus prints 0.405 and no second p-value. | CSR, SAP, ADLBHY, ADLBC | A difference from the CSR is often a decision, not an error. Two references can follow different rules. Each difference needs a class and a proof (section 4.8). A model-based table is within reach. |
| E27 | CSR Tables 14-6.02 and 14-6.03 print 59 p-values under a footnote mark that has no footnote. The SAP names Fisher's exact test for "the incidence of abnormal (high or low) measures", which can be read two ways. On the printed counts alone, an exact test on the 3 x 3 table (low, normal, high) gives all 59; on the 3 x 2 table (normal, abnormal) it gives 10. SciPy's `fisher_exact` samples for tables larger than 2 x 2, so it is neither exact nor repeatable. | CSR, SAP | A method and its reading can be identified from the reference's own counts before any data work. The registry needs its own exact Fisher test for larger tables, checked against R's `fisher.test`. |
| E28 | Two of the 16 descriptive tables read data outside the 10 reference ADaM datasets: Table 14-6.03 (change from the previous visit; Atorus reads ADLBCPV and ADLBHPV for it) and Table 14-7.04 (concomitant medications). Pilot 7 holds SDTM CM. A public copy of ADLBCPV and ADLBHPV is in the PHUSE repository (`data/adam/TDF_ADaM_v1.0/`), in another edition of the pilot ADaM. | Pilot 7, phuse-org/phuse-scripts, Atorus notes | real-4 writes specs for these datasets. Their only firm reference is the CSR table; the PHUSE copy is a hint. |

### 3.1 Reproduce E1 to E5 and E24 to E27

```bash
git clone https://github.com/RConsortium/submissions-pilot7-synthetic-data p7
git -C p7 checkout 213cb6ab3adc51abe4295cbbc546c0e6d46c3df8
git clone https://github.com/cdisc-org/analysis-results-standard ars
git -C ars checkout 2c9b4b68724386e8f91dc576724855af7fafac65
git clone https://github.com/RConsortium/submissions-pilot6-adams-tlfs p6
git -C p6 checkout a4f85c95cfef1f6aa27795362630f8ae43210185
python -m venv .venv   # Python 3.12 or later
.venv/bin/pip install yamaa==0.7.0 polars==1.44.2 pyarrow==25.0.1 PyYAML==6.0.3 pandas scipy

# E1: expect "TOTAL cells=9119605 mismatched=0"
(cd p7 && ../.venv/bin/python ../evidence/run_yamaa_project.py cdiscpilot01/spec/yamaa/project.yaml)
.venv/bin/python evidence/compare_adam.py p7/cdiscpilot01/data/adam \
  adsl adae adtte advs adlbc adlbh adlbhy adqsnipx adqsadas adqscibc

# E2, E3: expect "{'match': 3711, 'differ': 23, 'not_computed': 1}" (about 3 minutes)
.venv/bin/python evidence/ars_spike.py "ars/workfiles/examples/ARS v1/Common Safety Displays.json" \
  p7/cdiscpilot01/data/adam sas5
# E4: the same command with r7 gives 3662 matches

# E24, E25: needs pdftotext from poppler (24.02 was used)
pdftotext -layout p6/documents/CSR.pdf csr.txt
.venv/bin/python evidence/csr_demog_spike.py csr.txt p7/cdiscpilot01/data/adam/adsl.parquet   # 244 of 244
.venv/bin/python evidence/csr_ae_spike.py csr.txt p7/cdiscpilot01/data/adam csr               # 1175 of 1175
.venv/bin/python evidence/csr_ae_spike.py csr.txt p7/cdiscpilot01/data/adam single            # 1171 of 1175

# E26: expect 38, 45 and 51 of 51 for the three variants.
# E27: expect "equal 59 of 59" for the 3 x 3 reading and "equal 10 of 59" for the 3 x 2 reading
.venv/bin/python evidence/csr_hylaw_spike.py p7/cdiscpilot01/data/adam
.venv/bin/python evidence/csr_fisher_rxc_spike.py csr.txt
```

The run step writes `<dataset>-yamaa.parquet` files into the clone. Work on a
copy, or clean the clone afterwards.

## 4. The standard: one chain, seven layers, four properties

This section is the contract. Everything else serves it.

### 4.1 Layers

| Layer | Content | Format (public standard) | Example ID |
| --- | --- | --- | --- |
| L0 Documents | protocol, SAP, house standards | Markdown or PDF with stable anchors | `doc:sap#9.2/s3` |
| L1 Design | arms, epochs, visits, endpoints, estimands, populations | USDM v4 JSON. Placeholder in M1 | `usdm:Encounter_3` |
| L2 Collection | forms and items | ODM v2.0 metadata. Placeholder in M1 | `odm:AE.AESTDAT` |
| L3 Tabulation | SDTM datasets | SDTM with Define-XML. An input in M1 | `sdtm:AE.AESTDTC` |
| L4 Analysis data | ADaM datasets | yamaa ADaM spec, Define-XML | `adam:ADAE.TRTEMFL` |
| L5 Analysis | sets, subsets, groupings, methods, analyses, outputs | CDISC ARS v1 plus the method registry | `ars:An07_01` |
| L6 Results | one row per computed value | ARD: ARS result rows, flattened | `ard:An07_01/n/Trt_1` |
| L7 Display | titles, rows, columns, cell text, footnotes | display grid (JSON). RTF, PDF and HTML are projections of it | `cell:Out14-3-1-1/r4/c2` |

Every element in every layer has one stable ID, a content hash, and the file
and line it came from. For L1 and L2 the IDs and edge types are reserved and
nothing is generated in M1. Traces end at SDTM variables, and decisions cite
the documents.

### 4.2 Edges

| Edge | From, to | Proven by |
| --- | --- | --- |
| `shows` | cell to ARD rows | execution: the grid builder records it |
| `computes` | ARD row to analysis and operation | execution: stamped IDs |
| `reads` | analysis to ADaM variables (set, subset, grouping, analysis variable) | static, from the ARS |
| `derives_from` | ADaM variable to ADaM or SDTM variables | static, from the resolved yamaa spec |
| `maps_from` | SDTM variable to CRF item | reserved; not built in M1 |
| `collects` | CRF item to design activity and encounter | reserved; not built in M1 |
| `decides` | decision to the spec elements it sets | the compile check (section 5.2) |
| `cites` | decision to document span | quote check by script, then review by a person |

All edges except `cites` are executed or static: scripts prove them. `cites`
is judged: a script proves the quote stands at the anchor, and only a person
can approve that it supports the decision. Report the two kinds apart.
Never present a judged edge as proven.

### 4.3 Decision record

The decision record is the source of truth. Specs are compiled from it.

```yaml
id: ae.teae.end                 # catalog ID, or custom:<slug>
unit: mod-ae-emergence          # owning unit (section 10)
value: {rule: last_dose_plus_days, days: 30}
status: stated                  # stated | default | asked | conflict | not_applicable
class: document_rule
statement: >                    # standard form, rendered from the value
  An adverse event is treatment-emergent if it starts on or after the first
  dose date and no later than 30 days after the last dose date.
citations:
  - doc: sap
    anchor: "9.2/s3"
    quote: "... up to 30 days after the last dose ..."
binds: ["adam:ADAE.TRTEMFL"]    # filled by the compiler
identifiable: separated         # filled by the machine, never by the agent
```

### 4.4 Standard form

Each alternative of each catalog entry has one statement template: a
controlled English sentence with typed slots. The standard form of a study
is the list of statements for its decisions, grouped by unit.

- It is what people review and approve: short, uniform, each statement
  linked to its source quote and to the cells it affects.
- It is what the reader agent must produce from free text.
- It is unambiguous: a parser maps any standard-form statement back to its
  decision without a model. Decisions to statements to decisions is an exact
  round trip.

### 4.5 Decision classes

| Class | Where the information lives | Scored |
| --- | --- | --- |
| `document_rule` | protocol or SAP, cited | yes |
| `house_default` | the house standards shipped with the kit, cited | yes |
| `study_input` | nowhere in the inputs; a person supplies it | as a question asked, not as a guess |
| `gold_quirk` | the reference does it and no source supports it (errors included) | never rewarded |
| `no_gold` | cannot be reproduced from the available data | excluded and counted |

Pilot 7's clause relations (E6) are the evidence for assigning a class. A
clause the documents state (`same`, `differs`) supports `document_rule`. A
clause they do not state (`absent_in_document`) is a `house_default` or a
`study_input`. Documents that contradict each other (`contradicts`) need a
person before any class is given.

### 4.6 Four properties

| Property | Statement | Test |
| --- | --- | --- |
| P1 Determinism | Same decisions and inputs give the same bytes. | Build twice and compare hashes of canonical specs, ADaM, ARD, grid and graph. Where two engines exist (yamaa in R and Python; our result engines in Python and R), compare across them. |
| P2 Reproduction | The build equals the reference, or each difference has exactly one class (section 4.8). | ADaM cell by cell (numeric tolerance 1e-10). ARD at the reference's printed precision. Grid text. |
| P3 Traceability | Every printed number has a complete path to SDTM variables and to the decisions behind it. No spec element is unused. | Graph queries: path coverage per cell; share of decisions with verified citations; orphan elements = 0 except those tagged `conformance_only`. |
| P4 Identifiability | Changing any decision to another listed alternative changes at least one result. | Mutation: for each decision and alternative, recompile, rebuild, diff the ARD. Save the changed cells in the identifiability matrix. |

### 4.7 One-to-one, stated precisely

Let D be the canonical decision vector of a study and R its results. The
machine is a function R = M(D, data) (P1). On probe-complete data, M is
injective over the catalog's alternatives (P4): no two decision vectors give
the same results. The graph gives the other direction explicitly, from any
result back to the decisions that produced it (P3). P2 ties D to what the
study really delivered.

This is the correspondence the project must demonstrate, study by study.
Where data cannot separate two alternatives, the decision is marked
`unseparated` and reported. It is not counted as proven.

### 4.8 Differences from a reference

A reference is something the study really delivered: the reference ADaM,
the CSR tables. P2 compares our build with each one. A difference is kept in
`gold/exceptions.yaml` with exactly one class and its proof.

| Class | Meaning | Proof |
| --- | --- | --- |
| `rule_choice` | The reference follows another alternative of a decision than our gold does. | A build with that alternative, in which the cells equal the reference (E25, E26). |
| `reference_error` | The reference contradicts its own data or documents. | The contradiction, shown from public sources (E3). |
| `data_difference` | The public data are not the data behind the reference. No alternative of any decision gives the value. | Record-level evidence, and the owner's approval. |

- A difference with no class blocks the gate.
- Two references can follow different rules. In E26 the CSR counts two
  subjects' unscheduled pre-dose samples as baseline; the SAP and the
  reference ADaM do not. Gold has one decision vector, so one reference
  then carries a `rule_choice` difference. The order is fixed (decision
  17): the documents decide; where they are silent, the reference ADaM
  decides; where neither speaks, the house default decides. The owner still
  confirms each new case at N2.
- When gold reproduces a rule of the reference that no source supports,
  that decision has the class `gold_quirk` (section 4.5).
- Elements behind a `data_difference` are `no_gold` for scoring.
- Before blaming a method, test it on the reference's own printed counts
  (E26, E27).

## 5. Decision catalog: the unit of standardization

Studies become comparable when they answer the same closed list of
questions. The catalog is that list. It is what the reader fills, what a
person reviews and what the generator samples.

### 5.1 Entry format

```yaml
id: bds.baseline.rule
unit: mod-bds-visits
applies_when: design.has_bds_parameters        # predicate over design features
question: Which record is the baseline for each parameter?
alternatives:
  - id: last_before_first_dose
    statement: "Baseline is the last non-missing value before the first dose."
  - id: last_on_or_before_first_dose_date
    statement: "Baseline is the last non-missing value on or before the first dose date."
  - id: scheduled_baseline_visit
    statement: "Baseline is the value at the scheduled baseline visit ({visit})."
  - id: mean_of_predose_records
    statement: "Baseline is the mean of all values before the first dose."
house_default: last_before_first_dose          # null: ask a person when the documents are silent
compile: templates/adam/bds_baseline.yaml.j2   # one yamaa fragment per alternative
phrasings: phrasings/bds_baseline.yaml         # natural variants the generator may use
reading: knowledge/bds_baseline.md             # where documents state it, synonyms, traps
probes: [two_predose_records, day1_after_dose_time, missing_day1]
sources:
  - "ADaMIG 1.3, ABLFL and BASE"
  - "admiral::derive_var_extreme_flag"
```

### 5.2 Rules

1. Closed vocabulary. Every decision in a kit is a catalog entry or
   `custom:<slug>`. A custom decision carries a hand-written fragment and is
   flagged and counted. In M1, custom decisions appear only in the gold of
   the real study. Generated studies use catalog decisions only.
2. Canonical compile. For a catalog decision, the spec fragment is a pure
   function of the decision value. So reviewers approve decisions, not
   YAML, and a decision can never disagree with its spec. For a real study
   whose spec was written by hand, the check is by result: swapping in the
   compiled fragment must leave the ADaM unchanged.
3. Standard form. Each alternative has one unambiguous statement template
   (section 4.4). The round trip is a test.
4. Silence. When the documents do not state a decision, use the house
   default and cite the house standard. If the entry has no default, ask a
   person. Never guess. Asking too much and asking too little both cost
   points.
5. Every alternative has a public source, a set of phrasings and at least
   one probe that separates it from each sibling.
6. `applies_when` is a predicate over design features (section 6.2). The
   design decides which questions exist.
7. Output inclusion is a decision too: which table families a study needs
   and in which variants. The planned output list is the ARS
   `mainListOfContents`.
8. Method names and options in TFL decisions resolve to the method registry
   (section 7.3). Display rules (rounding, p-value format, truncation) are
   decisions as well (E25).

### 5.3 Sources for entries

| Source | What it gives |
| --- | --- |
| ADaMIG 1.1 to 1.3, OCCDS | variable definitions and permitted approaches |
| admiral function arguments (`derive_var_trtemfl`, `derive_vars_dt`, `derive_var_extreme_flag`, `derive_param_tte`, ...) | a community-reviewed list of alternatives per derivation |
| yamaa's closed verb registry | what a spec can express without custom code |
| CDISC ARS model and examples | the analysis-side decision classes |
| ICH E3 section 14 | which table families a report has |
| FDA safety tables guide, cardinalfda arguments | safety table variants and defaults |
| CDISC AC/DC method library | method identifiers and configuration options |
| Atorus replication notes (E22) | method details of the model-based tables |
| Pilot 7 claims and findings | alternatives seen in real documents: readings, open decisions |

Appendix B lists the seed entries for M1.

## 6. Studies: three tiers, generated by trial design

### 6.1 Tiers

| Tier | Source | Gold | Volume | Role |
| --- | --- | --- | --- | --- |
| A Generated | the generator: design x decisions x seed | by construction | unlimited | training, regression, exams |
| B Real documents | real protocol and SAP with simulated data: Pilot 7's kn189 and kn564, later ClinicalTrials.gov studies | reviewed, partial | tens | transfer check (M2) |
| C Real data | CDISCPILOT01: its SDTM, ADaM, SAP and the 30 CSR tables | reproduced from the delivery | one study | reproduction anchor, D1 and D2 |

Reality feeds the generator, not the reader. When a Tier B or C study shows
a decision, a phrasing or a data pattern the catalog lacks, add it to the
catalog and the generator. Do not tune reading knowledge on Tier B or C.
They are the honest test of transfer.

### 6.2 Design model

`design.yaml` is the generator's internal description of a study. Its terms
follow USDM v4, so import and export can be added later. Reading the pilot's
USDM file (E9) is an optional test, off the critical path. The reader agent
never sees the design file; it reads documents.

| Feature | Values |
| --- | --- |
| allocation | randomized (ratio, strata) or not |
| arms | 1 to 4; control: placebo, active or none; dose levels |
| model | parallel, crossover (sequences, periods, washout), single group, sequential cohorts |
| treatment duration | fixed, until an event, single dose, cycles |
| epochs | screening, treatment (1 to n), washout, follow-up |
| schedule | visits with target days and windows; unscheduled visits; early termination |
| endpoints | continuous change from baseline, responder, time to event, PK concentrations and parameters |
| analysis timing | landmark, repeated measures, event-driven with a data cutoff |
| populations | all randomized, safety, efficacy-evaluable, PK |

An archetype is a preset of features plus the ranges the sampler may vary.

| Archetype | Preset | Public anchor | Milestone |
| --- | --- | --- | --- |
| PG-FIX | randomized, parallel, placebo-controlled, fixed duration, continuous endpoints, visit windows | CDISCPILOT01 (Tier C) | M1 |
| ONC-TTE | randomized, treatment until progression, cycles, tumor assessments, OS and PFS, data cutoff | kn189, kn564 (Tier B) | M2 |
| P1-PK | healthy volunteers; ascending-dose cohorts or a 2x2 crossover; dense PK sampling | EIDD-2801 in Pilot 7's archive | M3 |

### 6.3 What the design changes downstream

The design decides structure and which decisions apply. This table is the
start of the `applies_when` rules.

| Design feature | ADaM structure | Decisions it activates | TFL effect |
| --- | --- | --- | --- |
| k arms, ratio, strata | levels of TRT01P and TRT01A; strata variables | arm order, pooling, actual-treatment source | columns, Total |
| fixed visits with windows | AVISIT, analysis flags | window table, tie-break, baseline, end-of-treatment record | by-visit rows |
| crossover periods | TRTxxP and TRTxxA, APERIOD, record-level TRTA | period assignment, events during washout, baseline per period | columns by treatment within period |
| treatment until event | open-ended exposure, cycles, cutoff date | cutoff handling, on-treatment window, censoring rules | time-to-event tables, exposure by cycle |
| ascending-dose cohorts | cohort and dose-level variables | placebo pooling, dose order | columns by dose level |
| dense PK sampling | nominal and actual times, concentration records | below-limit values, time deviations, exclusions | concentration and parameter summaries |

### 6.4 Generator pipeline

The generator plays the study's statistician: it makes the decisions, then
produces data and documents that are consistent with them.

| Stage | Produces | Notes |
| --- | --- | --- |
| S1 Design and decisions | `design.yaml` and the decision vector | sampled from an archetype and the catalog, within one house standard |
| S2 Subjects | latent truth per subject: enrolment, arm, exposure, visits, dropout, measurements, events | simple, documented models; kept in gold for audit |
| S3 Probes | extra subjects and records that separate decision alternatives | from catalog recipes; logged in `probes.jsonl` |
| S4 SDTM | SDTM datasets and their Define-XML, written directly | no CRF layer in M1; checked with CDISC CORE |
| S5 Gold | compiled specs, then ADaM, ARD, grids and graph | section 5.2 compile, then the machine with both result engines |
| S6 Documents | the standard form (gold), then the natural form | section 6.6 |
| S7 Twin and verify | a second dataset (new seed, same design and decisions) with its gold; P1 to P4; manifest | a kit that fails a property is not written |

Stages S1 to S5 and S7 are pure functions of (generator version, design,
decisions, seed). The natural form in S6 is written by a model. It is
generated once, checked, frozen in the kit and identified by its hash.

### 6.5 Probes, identifiability and the twin

A probe is a planted subject or record on which two alternatives of one
decision give different results.

| Decision | Probe |
| --- | --- |
| TEAE start boundary | an AE starting on the first dose date with no time |
| TEAE window end | AEs starting exactly N and N+1 days after the last dose |
| Partial AE start date | an AE with only year and month, in the month of first dose |
| Safety population | a randomized subject never dosed; a subject dosed with another arm's treatment |
| Baseline record | a screening value and a day 1 pre-dose value; a day 1 value timed after the first dose; a subject whose only pre-dose value is unscheduled (E26) |
| Visit window tie | two records equally far from the target day; an unscheduled record inside a window |
| Percent denominator | a subject in the population with no record for the parameter at a visit |
| Sort order of AE terms | two preferred terms with the same frequency |
| Age group cut | a subject aged exactly at the cut-point |
| Quantile method | a group whose size makes the two definitions differ |

Each kit has two datasets. The twin is hidden from the agent and used only
for scoring.

- The twin carries the full set of probes. Every applicable decision must
  be separated on the twin.
- The visible data carry a sampled part of the probes, recorded in the kit.
  The agent cannot tell which decisions matter from the edge cases it
  happens to see. Real data are like this: edge cases are never all there.

The identifiability matrix (decision x alternative, with the cells that
change) is predicted from `probes.jsonl` and then verified by mutation (P4).

A decision set that froze a number from the visible data (a site list, a
denominator, a category set) passes on the visible data and fails on the
twin. E7 shows the real case.

### 6.6 Documents: standard form and natural form

S6 writes each kit's protocol and SAP twice.

1. Standard form. Sections rendered from the statement templates, one
   anchor per decision. This is the gold. A parser recovers every decision
   from it without a model.
2. Natural form. A model rewrites the standard form into ordinary document
   prose: reworded, reordered, with neutral filler sections. This is what
   the reader agent gets.

A rewrite can change the meaning without anyone noticing, and then the gold
is wrong. Three checks guard against it.

| Check | How |
| --- | --- |
| Slots | A script confirms that every number, unit, visit name and variable name of each statement still stands in the paragraph anchored to that decision. |
| Read-back | A verifier agent with a fresh context picks, for each decision, the alternative the paragraph states. Any mismatch regenerates the paragraph, up to three times, then falls back to a phrasing template. |
| Sample | The owner reads a sample of pairs at N3 before D3. |

Known limit: the natural form holds only rewordings that a model can read
back. It measures robustness to wording, not the full difficulty of real
documents. The real SAP of CDISCPILOT01 is run for that, report only.

What M1 documents state:

| Tier | Protocol and SAP state | The rest |
| --- | --- | --- |
| full | every decision | nothing |
| standard | the study-specific decisions | house defaults stand only in the house standards document |
| ask demo | as `standard`, in two kits | one or two decisions without a house default are left out; an oracle answers when asked |

M2 adds what M1 leaves out: study-specific decisions at scale (left out of
the documents and supplied by the oracle, as a person would), derivations
outside the catalog (the generator composes new variables from yamaa's
verbs and describes them in words), irrelevant sections, and statements that
contradict each other.

### 6.7 Splits

| Split | Use | Who sees gold |
| --- | --- | --- |
| train | develop reading knowledge | the improver agent and people |
| dev | accept or reject a change | the scorer only; scores come back |
| test | report progress | the scorer only; aggregate scores come back |
| sealed | exam after a freeze, run once | nobody before the exam |

Sealed Tier A kits are generated at exam time from seeds the owner keeps
outside the repository. The repository stores only the SHA-256 of the seed
file. Exams hold out factors, not just seeds: one phrasing family, one house
standard, some combinations of alternatives, and one design variation per
archetype. The first-contact score of a new archetype is its score before
any development on it. Record it before starting.

### 6.8 Limits

Tier A is built for decision coverage, not clinical realism. Its outcome
models are simple and documented. Realistic distributions and real document
language come from Tier B and C. Do not claim more.

## 7. The machine

`build(decisions, inputs)` returns specs, ADaM, ARD, grids and the graph.
No model is involved anywhere in it.

### 7.1 Components

| Step | Component | Decision |
| --- | --- | --- |
| Decisions to specs | the compiler: catalog templates to yamaa, ARS and layout files | Build. |
| SDTM to ADaM | yamaa, pinned at 0.7.0, Python host | Reuse (E1), with our own thin runner (E19). |
| ADaM to ARD, descriptive methods, simple tests and CMH | two engines: Python, grown from `evidence/ars_spike.py`; and R, on cards and cardx | Build both. They must agree (R11). ADR-002 in real-2 decides whether the R engine wraps siera (E12) or is our own. |
| ADaM to ARD, model-based methods (ANCOVA, mixed models) | R only: `emmeans`, `mmrm` and their peers, behind registry contracts | Build. Checked against the CSR's printed values. |
| Methods and display rules | the method registry | Build (E4, E25). |
| ARD to grid | layout spec and grid builder | Build, minimal. real-3 evaluates tfrmt's JSON format as the on-disk layout. |
| Grid to files | renderers: HTML first; RTF and PDF through R later | Swappable. A renderer never computes a number. |
| Trace | graph builder | Build. Reuse the approach of Pilot 7's `lineage.py` for column dependencies. |
| Edit loop | rebuild and diff (section 7.6) | Build. |
| Checks | yamaa check and lint; the ARS JSON Schema; CDISC CORE; the Define-XML XSD | Reuse. |
| Viewer | one static HTML page per kit | Build, small. |

### 7.2 ARD

One row per analysis, operation and group combination: `analysis_id`,
`operation_id`, `group<n>_groupingId`, `group<n>_groupId` or
`group<n>_groupValue` (siera's stamping names), `raw_value`, `method_id`,
and a hash of the method options. Rows are sorted. Numbers are stored at
full precision; rounding happens once, at display, by a declared rule.

### 7.3 Method registry

ARS names a method; it does not fix its arithmetic (E4). A registry entry
does.

```yaml
id: summary.continuous
operations: [n, mean, sd, median, q1, q3, min, max]
options:
  quantile_definition: {values: [sas5, r7], default: sas5}   # numbered semantics
  sd_denominator: {values: [n_minus_1], default: n_minus_1}
implementations: [python, r]      # model-based methods list r only
vectors: tests/methods/summary_continuous.json               # inputs with expected outputs
xref:
  ars_example: Mth02_ContVar_Summ_ByGrp
  siera: 03_continuous_summary
  acdc: null                      # map to AC/DC method IDs in M2 (E11)
```

- Descriptive methods, simple tests (chi-square, ANOVA, Fisher) and CMH
  have a Python and an R implementation. The spike matched ANOVA,
  chi-square and Fisher p-values to 10 digits in Python. Fisher exact on
  tables larger than 2 x 2 needs our own enumeration in Python, because
  SciPy samples there (E27). The CMH statistic in
  `evidence/csr_hylaw_spike.py` is the start of the Python version (E26);
  its options are the scores and the strata.
- Model-based methods (ANCOVA with LS means and a dose-response test, mixed
  models for repeated measures) are R only. Their options carry the choices
  that change numbers: model terms, LS-means weights, covariance structure
  and degrees-of-freedom method (E22).
- Each analysis states the implicit choices ARS leaves to code, such as the
  denominator of a 2x2 test.
- Display rules are registry entries too: rounding half away from zero,
  p-value formats, truncation of long terms (E24, E25).

### 7.4 Layout and grid

The layout spec holds what ARS does not: the column axis (grouping to
headers, Total), the row axis (sections, statistic rows, indentation), cell
templates that combine operations (such as count with percent), decimals,
sort and threshold rules, and how missing values display. The grid builder
turns layout plus ARD into `grid.json`: every cell has its text and the IDs
of the ARD rows behind it. Scoring and tracing use the grid. RTF, PDF and
HTML are projections of it, so each company can keep its own style.

A mock shell is the same grid built on a dummy ARD: masks in place of
numbers. A study's TFL decisions can be reviewed as shells before data
exist.

### 7.5 Graph and viewer

`graph/nodes.jsonl` and `graph/edges.jsonl`, sorted, with the fields of
section 4. The viewer is one HTML file that embeds them. It needs no server
and no model. Six views:

| View | Shows |
| --- | --- |
| Overview | SDTM domains to ADaM datasets to outputs |
| Trace a cell | the cell, its ARD rows, its analysis, the ADaM variables with their rules, the SDTM variables, and the decisions with their quotes |
| Derivation chain | one variable's rules down to SDTM |
| Impact | what a source variable or a decision reaches |
| Decisions | the study's standard form: non-default decisions first, each with class, quote and the cells it affects |
| Changes | after an edit: which decision changed, and every changed cell before and after |

### 7.6 The edit loop: how a person changes what the AI delivered

1. The person says what to change, in plain words, in a Claude Code session
   that has the `edit-decision` skill.
2. The agent finds the decision in the catalog and shows the edit as two
   standard-form statements, old and new. If no alternative fits, it writes
   a custom fragment, flags it, and files a proposal to extend the catalog.
3. `specfirst rebuild --diff` recompiles, rebuilds what the graph says is
   affected, and writes the diff: every changed cell, before and after,
   with its trace.
4. The Changes view shows which decision changed and what it reached. The
   change is appended to `decisions.log.jsonl` with the reason.

The agent only edits the decision record. Compile, rebuild and diff are
deterministic. A wrong edit shows up as a wrong statement before anything is
built, and as an unexpected set of changed cells after.

The other direction, the agent asking the person, uses `specfirst ask`
(section 11.3). M1 only demonstrates it.

## 8. Kit format

A kit is one study, packaged so that inputs and gold can never be confused.

```text
kits/<kit_id>/
  kit.yaml            id, tier, archetype, split, generator version, pins,
                      SHA-256 of every file, identifiability summary
  inputs/             everything an agent may read
    docs/             protocol and SAP in natural form, with anchors
    house/            the house standards: document, parent specs, templates
    data/sdtm/        the visible SDTM datasets and their Define-XML
  gold/               never placed in an agent's workspace
    docs/             protocol and SAP in standard form
    decisions.jsonl   the decision vector, with classes and citations
    spec/             compiled yamaa ADaM specs, ARS JSON, layout files
    data/adam/  ard/  grid/  out/
    graph/            nodes and edges
    identifiability.json  probes.jsonl  oracle.yaml  exceptions.yaml
  twin/               the hidden second dataset and its gold results
```

`specfirst kit export --layout pilot7` projects a kit into Pilot 7's study
folder layout (`data/`, `program/`, `spec/`, `tlf/`, `log/`) for upstream
contributions. Seeds and decision vectors of dev, test and sealed kits are
secrets: gold can be rebuilt from them.

## 9. Scoring

A run submits decision records. The scorer compares them with gold, then
builds them on the visible data and on the twin and compares the results.

### 9.1 Reading score, per decision

| Dimension | Question | Measure |
| --- | --- | --- |
| value | Is the alternative, with its parameters, the gold one? | exact match |
| status | Did the reader tell stated from default from must-ask from conflict? | exact match |
| citation | Does the quote stand in the document, inside the gold span? | quote found; overlap with the gold anchor |
| questions | Did the reader ask for exactly the decisions that have no default and no statement? | precision and recall of asks |
| unmapped | Did it list as unmapped only what the catalog truly lacks? | precision and recall |

### 9.2 Build score, the effect of the reading

| Dimension | Question | Measure |
| --- | --- | --- |
| validity | Do the decisions compile and build? | pass or fail, with the failing rule |
| inclusion | Are the right datasets, variables, outputs and analyses present? | precision and recall |
| structure | Keys of each dataset; rows and columns of each grid | exact match per axis |
| values | ADaM cells, ARD values, grid text | share correct, on visible data and on the twin |
| cost | tokens, turns, wall time | from the run record |

### 9.3 Reading the scores

- Report every dimension by decision class and by unit. One number hides
  whether the reader misread a document or guessed a convention.
- Score ADaM in three layers: variables that reach a printed number,
  variables used but not printed, and conformance-only variables. The last
  layer is checked for compliance and credited to no one.
- `gold_quirk` and `no_gold` elements never earn credit.
- A decision that is unseparated on the visible data is settled by the
  twin. If the twin cannot separate it either, compare decision values and
  report it apart.
- Headlines (decision 22): the number of decisions a reviewer would have
  to change; the share of printed cells correct on the twin; for the real
  study, the share of CSR cells reproduced, with the count of proven
  differences; and the cost per study in tokens, time and questions asked.
- A control: the deterministic parser on standard-form documents must score
  100%. If it does not, the kit or the scorer is wrong.

### 9.4 Attribution

For each wrong cell, walk the gold graph upstream and compare candidate and
gold artifacts layer by layer. The first element that differs owns the
error. Report errors by owning unit and layer. An end-to-end failure then
becomes a task for one unit.

### 9.5 Planted defects

The scorer is trusted only when it detects and correctly attributes each of
these: arms exchanged in one analysis (E3); a wrong analysis set; a window
off by one day; a wrong denominator; a missing column; a changed quantile
definition (E4); a p-value rounded twice (E25); a baseline taken from the
wrong record (E26); an unstable sort; a frozen site list (caught on the twin
only); a quote that is not in the document; and a citation that points at
the wrong span.

The generator has its own planted defect: a rewrite that changes a number
must be rejected by the checks of section 6.6.

## 10. Units and knowledge

A unit owns a family of catalog entries: their statement templates, compile
templates, phrasings, reading notes, probes and tests. Units are what people
own and what is scored. There is one reader agent; it uses a core skill plus
each unit's reading notes. Units ship as Agent Skill folders, the format
pharma-skills uses (E16), so reading knowledge can be published and
benchmarked with and without it.

| Kind | Owns | M1 units |
| --- | --- | --- |
| core | the shared procedure: read, locate, quote, record, apply the silence rule, list what is unmapped | `core-reader`, `edit-decision` |
| module | decisions shared by several outputs, compiled to yamaa fragments | `mod-treatment`, `mod-populations`, `mod-demographics`, `mod-ae-emergence`, `mod-bds-visits` |
| table family | inclusion, variants, parameters and layout of one kind of output, plus the ADaM variables only it reads | `tfl-demographics`, `tfl-ae-summary`, `tfl-ae-soc-pt`, `tfl-vitals-by-visit` |

Ownership is computed, not assigned. From each gold graph, build the matrix
variable x table family. A variable read by two or more families belongs to
a module. Read by one, it belongs to that family. Read by none, a
deterministic conformance template adds it and no agent decides it (E5).
Recompute when kits are added.

Shared facts that are not variables (the on-treatment window, the data
cutoff, a grading scale) also have exactly one owning unit. Other units read
the owner's decision. They never decide it again.

Integration is deterministic: merge compiled fragments into dataset specs in
dependency order, fail on conflict (a conflict is a finding for a person),
then add conformance-only variables from the house templates.

The real study adds table families that M1 does not generate: disposition,
exposure, efficacy, laboratory, concomitant medications. Their decisions
enter the catalog as they are understood. Until then they are custom, and
counted.

## 11. Harness and training loop

### 11.1 Task contract

A reading task is a folder: `inputs/` from the kit, the standard (catalog,
method registry, schemas), the reading knowledge under test, and a
`TASK.md`. The reader may run `specfirst check` and `specfirst preview` to
see what its own decisions build on the visible data. It writes
`out/decisions.jsonl`, `out/questions.jsonl` and `out/unmapped.jsonl`.

The default adapter runs Claude Code non-interactively: `claude -p` with
`--output-format json`, the model set to Opus 5.5 and tools limited with
`--allowedTools`. The task prompt names the knowledge files to read, so the
with-knowledge and without-knowledge conditions differ only in the files
present. Confirm the flags against the current CLI reference in read-2.

M1 runs on the owner's Claude Code subscription. The adapter also accepts an
API key (`--bare`, with `--max-budget-usd`), which gives the most repeatable
runs; use it when a result must stand on its own. Any other agent that
honours the folder contract can be plugged in.

### 11.2 Isolation

Gold, twins and seeds are never inside a task folder. In M1, tasks run in a
temporary directory outside the repository with deny rules for the kit
store, and every transcript and workspace is scanned for canary strings
planted in gold files. State this limit in M1 reports. In M2, tasks run in
containers (Docker, or Harbor as yamaa uses) where gold is not mounted.

### 11.3 Questions

The reader asks with `specfirst ask "<question>" --decision <id>`. The
oracle answers only decisions that have no house default and are not stated
in the documents, from the kit's oracle file. Every ask is logged and
scored. In real use the oracle is a person. M1 only demonstrates this, on
two kits.

### 11.4 Training loop (M2)

1. Run the reader on the train kits and score by unit.
2. The improver agent reads the classified, attributed failures and edits a
   unit's reading notes or the core skill on a branch.
3. Accept the change only if no dev score falls in any class and train
   scores rise. The planted-defect suite must still pass.
4. Write the lesson in `docs/lessons.md` with the check that proves it.
5. Repeat until dev scores stop moving. Freeze. Run the sealed exam once.

Leak checks before each exam: no kit IDs, subject IDs, seeds or literal gold
values in skills or knowledge; a canary scan; and the sealed kits come from
the frozen generator version.

## 12. Repository layout

```text
PLAN.md  CLAUDE.md  README.md  LICENSE
docs/         state/ (one file per track), lessons.md, decisions/, reports/
standard/     schemas/ (decision record, catalog entry, kit, ARD, grid, graph, method)
              catalog/  methods/  houses/open-default@1/
src/specfirst/
  compile/    decisions to yamaa, ARS and layout; standard-form render and parse
  machine/    runner (yamaa), ard (Python engine), methods, grid, render, graph, validate
  edit/       rebuild and diff, decision log
  gen/        design, subjects, probes, sdtm, gold, documents, verify
  score/      reading, build, attribute, defects
  harness/    task, adapters, oracle, records
  cli.py      doctor, fetch, status, compile, build, check, preview, rebuild,
              gen, score, run, ask, gate, kit
r/specfirstr/ the R result engine and the model-based methods
skills/       core-reader/  edit-decision/  mod-*/  tfl-*/
kits/         small Tier A fixtures only; other kits are generated or fetched
viewer/       the static page template
evidence/     spike scripts and their recorded output
tests/        unit/  methods/  defects/  golden/
third_party/  SOURCES.md; the fetch cache is ignored by git
env/          lock files for Python and R, container definition
```

## 13. Tracks, work packages and gates

Each work package has one gate: `specfirst gate <wp>` exits 0 only when
every listed check passes. A package is done when its gate passes and the
reviewer agent has signed `docs/reports/<wp>.review.md`. It then merges to
`main` and the track goes on. Owner nodes (section 2.3) are marked N1 to N3.

### 13.1 Tracks and dependencies

| Track | Work packages | Result |
| --- | --- | --- |
| base | base-0 | repository, environment, pins, shared formats |
| real | real-1 to real-5 | CDISCPILOT01: ADaM proof, result engines, grids and viewer, the 30 CSR tables |
| std | std-1 to std-3 | catalog and standard form, identifiability, the edit loop |
| gen | gen-1 to gen-3 | generated studies for PG-FIX |
| read | read-1 to read-3 | scorer, harness, reader agent, first scores |

| Work package | Needs | Sessions (estimate) |
| --- | --- | --- |
| base-0 | nothing | 1 |
| real-1 | base-0 | 1 to 2 |
| real-2 | real-1 | 2 to 3 |
| real-3 | real-2 | 2 |
| real-4 | real-3 | 4 to 6, fanned out by table family |
| real-5 | real-4 | 4 to 6 |
| std-1 | base-0 | 2 to 3, then N1 |
| std-2 | std-1, real-3 | 2 |
| std-3 | std-2 | 1 to 2 |
| gen-1 | base-0, and a draft of std-1 | 2 to 3 |
| gen-2 | gen-1, std-1 after N1, real-3 | 2 |
| gen-3 | gen-2 | 2 to 3 |
| read-1 | real-3 for fixtures, then gen-2 | 2 |
| read-2 | read-1, gen-2 | 2 |
| read-3 | read-2, gen-3, std-2 | 2 |

Deliveries: D1 = real-4 and std-3. D2 = real-5. D3 = read-3. Each delivery
passes N3 before it is shown.

### 13.2 base

#### base-0 Bootstrap

- Put the folder under git (`git init -b main`), commit this file and
  `evidence/`, and create the owner's private repository:
  `gh repo create specfirst --private --source=. --remote=origin --push`.
  If `gh auth status` fails, stop and ask the owner to run `gh auth login`.
- Create the layout of section 12, the MIT license, `CLAUDE.md` (section
  2.4) and `.claude/settings.json` with deny rules for any nearby folder
  that holds employer material (ask the owner for the paths).
- Environment in WSL2. Python 3.12 or later with yamaa 0.7.0, polars,
  pyarrow, PyYAML, pandas and SciPy. R 4.2 or later with cards, cardx,
  siera, emmeans, mmrm, coin and car. Poppler's `pdftotext`. Lock files.
- `specfirst fetch`: clone the sources of appendix A at their pinned commits
  into the ignored cache and verify the commits.
- Turn the seven `evidence/` scripts into tests.
- Shared formats, version 0: JSON Schemas for the decision record, ARD,
  grid and graph, so that tracks can work in parallel. Changing one needs
  an ADR.
- CI: tests, lint, ASCII check. A worktree script and one `docs/state/`
  file per track.

Gate: on a clean clone, install, fetch and run the evidence tests. They
print 9,119,605 cells with 0 mismatches (E1); 3,711 matches, 23 differences
and 1 not computed (E2, E3); 244 of 244 (E24); 1,175 of 1,175 and 1,171 of
1,175 (E25); 38, 45 and 51 of 51 (E26); 59 of 59 (E27). R loads the listed
packages. The ASCII check passes.

### 13.3 real: CDISCPILOT01

#### real-1 Kit and ADaM proof

- Assemble `kits/cdiscpilot01/` from the cache: SAP, data guide, Define-XML
  files and SDTM as inputs; Pilot 7's yamaa specs and the reference ADaM as
  gold. Commit no study data (E20).
- ADR-001: wheel with our runner, or source build at Pilot 7's pin (E19).
  One name differs in Pilot 7: the spec is `adqsnipx.yaml`, the reference
  file is `adqsnpix.parquet`.
- Canonical writers. P1 and P2 as tests.
- Build the SDTM to ADaM part of the graph from the resolved specs: one
  node per ADaM output column and per SDTM column read, `derives_from` edges
  with source file and line.
- Import Pilot 7's claims as candidate `cites` edges for ADaM variables,
  marked as imported.

Gate: P1 passes (two builds, identical hashes). P2 passes (E1). Every
output column of the 10 datasets reaches SDTM columns, literals or declared
inputs through `derives_from`; any gap is listed with its reason.

#### real-2 Result engines

- ADR-002: the R engine wraps siera, or is our own on cards and cardx.
- Method registry v0: count of subjects, percent with a referenced
  denominator, continuous summary, chi-square, one-way ANOVA, Fisher exact,
  and the display rule "round half away from zero". Each has numbered
  semantics, test vectors and cross-references. Fisher exact must be exact
  for tables larger than 2 x 2: write the enumeration in Python and check
  it against R's `fisher.test` (E27).
- ARD format and canonical writer. Validate ARS files against the schema
  generated from the ARS model.
- Python engine: rewrite the spike. It takes about 3 minutes now; the
  target is under 10 seconds. R engine: the same ARS, the same registry.
- `gold/exceptions.yaml` for the pilot: the 24 results of E3, each with its
  class and proof (section 4.8). Our gold ARS carries regenerated results.
- Draft the issue text for the ARS repository (section 14). Do not post it.

Gate: both engines reproduce at least 3,711 of the 3,735 embedded results,
with 0 unexplained. The engines agree on every result (relative tolerance
1e-9). P1 passes. Planted defects are caught: exchanged arm labels, a wrong
analysis set, a changed quantile definition, a dropped data subset.

#### real-3 Grid, trace, viewer

- Layout spec v0, grid builder, mock shells, HTML renderer. ADR-003: own
  layout format or tfrmt JSON.
- Build the 5 outputs of the ARS example as the first grids. Compare cell
  text with the example's `formattedValue`.
- Complete the graph from cells to SDTM variables, and to the documents
  through the ARS `documentRefs` (SAP pages) and the imported claims.
- Viewer: overview, trace a cell, derivation chain, impact.

Gate: 100% of numeric cells in the 5 grids have a complete path to SDTM
variables. The graph build is deterministic. The viewer opens from the file
system with no network. The report walks one cell end to end.

#### real-4 The 16 descriptive CSR tables (D1)

- Reference grids. A parser turns the fetched CSR PDF into one reference
  grid per table of appendix D, kept in the cache. The two spikes (E24,
  E25) are the starting point.
- For each table: its ARS analyses and its layout, written from the SAP and
  the CSR shell; the methods and display rules it needs; and yamaa specs
  for data the reference ADaM lacks: concomitant medications for Table
  14-7.04 and change from the previous visit for Table 14-6.03 (E28).
- Build with both engines. Compare every printed cell with the reference
  grid.
- `gold/exceptions.yaml`: each difference gets one class and its proof
  (section 4.8). When a cell differs, first test the method on the CSR's
  own printed counts, then look for the decision that explains it (E26,
  E27). Use Atorus's notes as hints, not as truth (E22).
- Fan out by table family: populations and disposition (14-1.x),
  demographics (14-2.01), efficacy over time (14-3.10), exposure (14-4.01),
  adverse events (14-5.x), laboratory (14-6.01 to 14-6.04), vital signs,
  weight and concomitant medications (14-7.x).

Gate: all 16 tables are built from specs by both engines. Every printed
cell equals the CSR at its printed precision, or has exactly one classified
difference with its proof. Every cell has a complete trace. Then N2: the
owner reviews the classes and rules which reference wins where two
disagree.

#### real-5 The 14 model-based CSR tables (D2)

- Registry entries. R only: ANCOVA with LS means, pairwise comparisons and
  the dose-response test; the mixed model for repeated measures. Their
  options carry model terms, weights, covariance structure and
  degrees-of-freedom method. Python and R: CMH, with its scores and strata.
  Sources: the SAP, the analysis results metadata in the pilot's
  Define-XML, and Atorus's notes (E22).
- ARS and layout per table. Build, compare, classify. Start with Table
  14-6.06, which E26 has already reproduced by hand; the spike's CMH
  statistic is the start of the Python implementation.
- Known hint to verify: Atorus reports that the LS means printed in Table
  14-3.11 are averages over weeks 8, 16 and 24, although the title says
  Week 24.

Gate: all 14 tables are built from specs. The same cell rule holds. Each
method has test vectors. The two engines agree on the three CMH tables.
Every cell has a complete trace. Then N2.

### 13.4 std: the standard

#### std-1 Catalog, standard form, compiler, house standard

- Schemas for catalog entries and decision records.
- Entries for the M1 families (appendix B; at least 40). Each has its
  alternatives with statement templates, a house default or none, public
  sources, a compile template, phrasings, reading notes and probe recipes.
- The compiler (decisions to yamaa, ARS and layout). The standard-form
  renderer and parser.
- House standard `open-default@1`: a citable standards document, parent
  yamaa specs, ARS and layout templates.

Gate: the round trip decisions to statements to decisions is exact for
every alternative. Compiled fragments pass `yamaa check` and the ARS schema.
Every entry has at least one public source. Then N1: the owner approves and
the catalog is frozen as `catalog@1`.

#### std-2 Pilot decisions, mutation and identifiability

- Express the pilot's gold as decision records where the catalog covers it.
  Check by result (section 5.2). Count what stays custom.
- `specfirst rebuild --diff`: recompile, rebuild what the graph says is
  affected, and diff the results (section 7.6).
- The mutation runner and the identifiability matrix, on the pilot.

Gate: for every pilot decision the catalog covers, the compiled fragment
leaves the ADaM unchanged. The matrix is reproducible. The report states
how many decisions are separated and how many are unseparated on the pilot
data, with one worked example of each.

#### std-3 The edit loop (D1)

- The `edit-decision` skill, the decision log, and the viewer's Decisions
  and Changes views (section 7.6).
- A demo script with three edits on the pilot: the end of the
  treatment-emergent window, the age groups, and the Total column. Run it
  again on the CSR tables when real-4 has passed.

Gate: for the three scripted edits, the changed cells predicted from the
graph equal the observed diff. An edit with no catalog alternative is
flagged as custom and files a proposal. The log is written.

### 13.5 gen: generated studies

#### gen-1 SDTM generator for PG-FIX

- Design model and sampler. Subject process. SDTM writers for DM, DS, EX,
  AE, VS and SV, plus the trial design datasets CORE expects.
- Probe recipes for every M1 decision; a draft of std-1 is enough to start.
  The twin gets all probes; the visible data get a sampled part.

Gate: for 10 seeds, visible and twin SDTM pass CORE with no unexplained
error. Regenerating gives identical hashes. `probes.jsonl` shows at least
one probe in the twin for every pair of alternatives.

#### gen-2 Gold and verification

- Sample decisions within the house standard. Compile. Build with both
  engines on the visible data and on the twin. P1 to P4. Manifest. Splits.

Gate: 10 kits pass P1 to P4. Every applicable decision is separated on the
twin. The engines agree.

#### gen-3 Documents

- Protocol and SAP in standard form with anchors. The natural form by model
  rewrite, with the three checks of section 6.6. Tiers `full` and
  `standard`. The ask demo in two kits. A one-page summary per kit.

Gate: the parser recovers 100% of the decisions from every standard-form
document. Every natural document passes the slot check and the read-back
check. A planted bad rewrite (a changed number) is rejected. Each kit
records which probes are visible.

### 13.6 read: the reader and its scores

#### read-1 Scorer

- Reading score and build score (section 9), attribution, and the
  planted-defect suite. Start on the pilot and on hand-made fixtures; finish
  on the kits of gen-2.

Gate: the planted-defect suite passes, each defect detected and attributed
to the right layer. The parser control scores 100% on standard-form
documents.

#### read-2 Harness and reader v0

- Task builder, Claude Code adapter, isolation and canary scan, oracle, run
  records with cost.
- The `core-reader` skill. Reading notes v0 for each unit, taken from the
  catalog.

Gate: a dry run on one train kit ends within budget with valid output
files. The canary scan is clean.

#### read-3 First scores (D3)

- Runs on dev kits in natural form: the reader with the catalog only, and
  the reader with the units' reading notes.
- The real SAP of CDISCPILOT01, report only: compare with the pilot's
  decision records from std-2 and list what the reader could not map.
- The ask demo on two kits.

Gate: the report gives scores by dimension, class and unit, and the cost
per run. The canary scan is clean. Then N3.

### 13.7 After M1 (outline; plan in detail after D3)

| Milestone | Content |
| --- | --- |
| M2 | Study-specific decisions: left out of the documents and supplied by the oracle; derivations outside the catalog, composed from yamaa's verbs. Noise and contradictions in documents. The training loop and the first sealed exam. Container isolation. The ONC-TTE archetype with kn189 and kn564 as Tier B. A second house standard. The spec-versus-code track: the same tasks solved by writing programs. First pull requests to Pilot 7. |
| M3 | The P1-PK archetype with EIDD-2801 as anchor; concentration and parameter datasets; figures and listings. The layers before SDTM: USDM import and export, CRF collection. A Tier B pipeline from ClinicalTrials.gov. Public benchmark and write-up. |

## 14. Upstream contributions

Claude Code drafts each of these. The owner approves each text before it
is sent. Contact with maintainers starts with D1 (decision 20).

| Where | What | When |
| --- | --- | --- |
| cdisc-org/analysis-results-standard | Issue: 23 embedded results of the Common Safety Displays example disagree with the pilot ADaM (E3). Attach the comparison. | after real-2; may go before D1 |
| RConsortium/submissions-pilot7-synthetic-data | Proposal for the empty `tlf/` layer: ARS, ARD, grid and cell-level trace for cdiscpilot01. Then a pull request in their layout and checks. | with D1 |
| elong0527/yamaa | Issues for anything the catalog needs that yamaa cannot express. Ask whether result datasets (the draft `adam-results-ae-incidence` benchmark) are a planned direction. | collected as found, sent from D1 on |
| clymbclinical/siera | Differences found when the two engines are compared. | after real-2 |
| atorus-research/CDISC_pilot_replication | Differences from the CSR that our classification explains and theirs leaves open. | after D2 |
| RConsortium/pharma-skills | The reader's skills and their benchmark cases. | after M2 |
| cdisc-org/analysis-concepts, 360i | A mapping between our method registry and the AC/DC method IDs. | M2 |

## 15. Risks

| Risk | Handling |
| --- | --- |
| The reader overfits the generator's wording | Rewrites by a model, phrasing families with one held out, and the real SAP report at D3. The natural form's limit is stated (section 6.6). Reality feeds the generator. |
| A rewrite changes the meaning and corrupts gold | The slot check, the read-back check and the owner's sample (section 6.6); a planted bad rewrite must be rejected. |
| Thirty tables are too many for M1 | Two batches. D1 ships without the model-based half. E24 and E25 show the descriptive half is within reach. |
| A CSR number cannot be reached from public data | The `data_difference` class of section 4.8, approved by the owner at N2. Never force a match. |
| The CSR and the reference ADaM follow different rules (E26) | One decision vector is gold; the other reference carries a proven `rule_choice` difference. The owner rules at N2. |
| Two descriptive tables need datasets the reference ADaM lacks (E28) | real-4 writes their specs from the SAP; the CSR table is the reference. If one cannot be settled in time, it moves to D2 and D1 ships without it. |
| Parallel tracks drift apart | Shared formats fixed at base-0, the catalog frozen at N1, one gate per package on `main`, an ADR for any format change. |
| The owner's review becomes the bottleneck | Three nodes only. Everything else passes by gate and independent review. |
| yamaa moves fast and has one main maintainer | Pin it. Keep the adapter thin. Report issues upstream. Decisions and plain yamaa specs outlive our code. |
| ARS cannot express a table | Record the gap. Extend through the method registry and the layout, never through code inside a spec. Raise it upstream. |
| Simulated data are not clinically realistic | Not a goal of Tier A (section 6.8). |
| Subscription runs are less repeatable than API runs | Fixed prompts, full transcripts kept with every run record, the API path ready for results that must stand alone. |
| Gold leaks to the agent | Section 11.2; containers in M2. |
| Employer intellectual property | Section 2.1, rule 7 in particular. The owner checks employment terms before anything is published. |

## 16. Open questions for the owner

Section 17 records what the review settled. These remain.

1. Project name, and whether the repository becomes public. Decided at D1,
   after the owner has checked the employment terms.
2. The acceptance rule of the training loop (M2). Proposed: no class may
   fall on the dev kits.
3. The second house standard, and which Tier B studies follow kn189 and
   kn564 (M2).

## 17. Decisions of the design review (2026-11-10 and 11)

| # | Question | Decision |
| --- | --- | --- |
| 1 | What does the AI deliver? | Decision records are the source of truth. Specs are compiled from them. Hand-written fragments are the flagged exception. |
| 2 | Derivations outside the catalog | M2. They are study-specific decisions: a person supplies them in real use; the generator plays that person in training. M1 covers the standard decisions. |
| 3 | Decisions the documents do not state | Use the house default and cite it. Ask only where no default exists. Both over-asking and under-asking cost points. |
| 4 | The layers before SDTM | Placeholders in M1. SDTM, protocol and SAP are inputs. Reading the pilot's USDM file is optional. |
| 5 | Human in the loop | M1 builds the edit loop in full and only demonstrates the ask loop, with one or two must-ask decisions. |
| 6 | How a person edits | By telling the agent. The agent edits the decision; rebuild and diff are deterministic; the viewer shows which decision changed and what it reached. |
| 7 | Document realism | A separate read stage: a model turns free text into the standard form, which people review. The generator writes the standard form first, then a model rewrites it into the natural form. |
| 8 | Probes | The twin carries all of them. The visible data carry a sampled part. |
| 9 | The reader in M1 | Trained and scored on rewritten documents. Run on the real SAP of CDISCPILOT01 for a report only. |
| 10 | Target on the real study | All 30 CSR tables: each printed cell equal to the CSR, or one classified difference with its proof. |
| 11 | Table families in generated studies | Demographics, AE summary, AE by organ class and term, and vital signs by visit. All four are required. |
| 12 | Result engines | Python and R, both complete, for descriptive methods and simple tests. |
| 13 | Model-based methods | R only. No second implementation; checked against the CSR's printed values. |
| 14 | Gates | Automatic, with an independent reviewer agent. The owner is asked at three nodes: N1, N2, N3. |
| 15 | Environment | WSL2 Linux, with Python and R. |
| 16 | Model usage | Designed for the Claude Code subscription; the adapter also accepts an API key. |
| 17 | Gold when references disagree | The documents decide; where they are silent, the reference ADaM; where neither speaks, the house default. What the CSR does differently is recorded as a `rule_choice` difference with its proof. For the two known cases this leaves 4 cells of Table 14-5.01 and 6 cells of Table 14-6.06 different from the CSR. |
| 18 | Runs on an employer's machine | The owner may run the framework there on public, generated and employer studies. By hand, the owner brings back aggregate scores for public and generated studies only. They guide the work; they are not committed or published. A number that is committed or published is run again on the owner's own equipment (section 2.1, rule 7). |
| 19 | Repository | A private repository under the owner's personal GitHub account, working name specfirst. Claude Code creates it in base-0 and pushes to it. Name and visibility are decided at D1. |
| 20 | Upstream contact | With D1. The ARS issue may go earlier, once real-2 confirms it. The owner approves each text before it is sent. |
| 21 | CMH | Python and R, like the simple tests. ANCOVA and the mixed model stay R only. This refines decision 13. |
| 22 | Headline numbers | Decisions a reviewer must change; share of printed cells correct on the twin; CSR cells reproduced, with the count of proven differences; cost per study. |

## Appendix A. Pinned sources

| Source | Repository | Commit | License | Used for |
| --- | --- | --- | --- | --- |
| Pilot 7 | RConsortium/submissions-pilot7-synthetic-data | 213cb6ab3adc51abe4295cbbc546c0e6d46c3df8 | MIT for code; study data excluded | pilot specs and data, claims, verifier, kn189, kn564 |
| yamaa | elong0527/yamaa | 93a6757594988fddc9b05d220d5f53deb5085d50 (documentation); engine from PyPI, version 0.7.0 | MIT | SDTM and ADaM engine |
| CDISC ARS | cdisc-org/analysis-results-standard | 2c9b4b68724386e8f91dc576724855af7fafac65 | MIT for code, CC BY 4.0 for content | ARS model and examples |
| Pilot 6 | RConsortium/submissions-pilot6-adams-tlfs | a4f85c95cfef1f6aa27795362630f8ae43210185 | no license file: fetch, never redistribute | CSR, SAP, table programs |
| Atorus replication | atorus-research/CDISC_pilot_replication | fc8d658d7709aac0cccd753d0ca9ae6726090a61 | MIT | R programs and notes for the 30 CSR tables |
| PHUSE scripts | phuse-org/phuse-scripts | 398a6d33ced9359ffb58c46650a6d488811176b1 | MIT-style for code; pilot data under CDISC terms | other editions of the pilot ADaM, with ADLBCPV and ADLBHPV |
| CDISC 360i | cdisc-org/360i | 24bd98bdcea3db3046436e6a749bbbc92196fe12 | MIT for code, CC BY 4.0 for content | pilot USDM JSON and protocol |
| AC/DC | cdisc-org/analysis-concepts | 739344ca31203bb502efeee2b855286e17977be6 | MIT | method library, eSAP schema |
| siera | clymbclinical/siera | 9208a9b6a00876f13d2b17f01aa318290c066674 | MIT | candidate base for the R engine |
| cardinal | pharmaverse/cardinal | b1fe03a760a1ca3b4610830ba64be5bd3e6ff4a5 | Apache-2.0 | FDA safety table templates |
| pharma-skills | RConsortium/pharma-skills | e5db96d54ef5a79cbfd06e2339a3351e4583f8da | MIT per skill folder | skill format, benchmark runner, simulator |
| pharmaverseraw | pharmaverse/pharmaverseraw | e0771afea8bead7e64bc7cf2ff53ef8b638c6c1b | Apache-2.0 | raw data and annotated CRFs for pilot domains (M3) |
| 360i proofs of concept | lexjansen/cdisc360i-pocs | 9f6de449cbff0c3f16fb10a93e4e79c7cd6ad43e | MIT | USDM to CRF (ODM) generation (M3) |

base-0 confirms every license again and records it in
`third_party/SOURCES.md`.

Other public documents:

- ARS example file `workfiles/examples/ARS v1/Common Safety Displays.json`,
  SHA-256 `90358dd60d687332f2138aa50435b4050fa91be3f52958169229daa269fe31b3`.
- The CSR is `documents/CSR.pdf` in Pilot 6 (492 pages; the 30 tables are
  pages 43 to 150, Figure 14-1 is page 151).
- FDA Standard Safety Tables and Figures: Integrated Guide
  (https://www.fda.gov/media/187065/download) and MAPP 6025.9
  (https://www.fda.gov/media/187066/download).
- 360i roadmap posts: https://humedatalabs.com/360i-technical-roadmap/ and
  https://humedatalabs.com/phuse-sde-360i-oss/.
- Claude Code: https://code.claude.com/docs/en/headless and
  https://code.claude.com/docs/en/best-practices.

Sandbox used for E1 to E5 and E24 to E27: Linux x86_64, Python 3.13.18,
yamaa 0.7.0, polars 1.44.2, pyarrow 25.0.1, pandas 3.1.1, SciPy 1.18.1,
NumPy 2.5.4, poppler 24.02.0.

## Appendix B. Seed catalog for M1

The first alternative is the proposed default of `open-default@1`. Entries
marked "no default" have none: the documents state the value, or the reader
asks. The ask demo (section 6.6) leaves one or two of them out of the
documents. std-1 confirms each entry and each default against a public
source, and may rename, split or drop entries.

| ID | Unit | Question | Alternatives |
| --- | --- | --- | --- |
| `trt.planned.source` | mod-treatment | Where does planned treatment come from? | DM.ARM; DM.ARMCD through a map |
| `trt.actual.source` | mod-treatment | Where does actual treatment come from? | DM.ACTARM; first treatment received in EX; same as planned |
| `trt.start.source` | mod-treatment | What is the treatment start date? | first EX record with a dose; first EX record; DM.RFXSTDTC |
| `trt.end.source` | mod-treatment | What is the treatment end date? | last EX end date; last EX start date; disposition date when EX has none |
| `trt.date.imputation` | mod-treatment | How are partial exposure dates completed? | not completed; first day of the month |
| `date.studyday.origin` | mod-treatment | Which date is day 1? | treatment start; DM.RFSTDTC |
| `pop.randomized.rule` | mod-populations | Who is in the randomized set? | all randomized; randomized with a post-baseline value |
| `pop.safety.rule` | mod-populations | Who is in the safety set? | at least one dose; randomized and at least one dose |
| `pop.safety.grouping` | mod-populations | Which treatment groups safety analyses? | actual; planned |
| `pop.efficacy.rule` | mod-populations | Who is efficacy-evaluable? | a baseline and one post-baseline value; completed a stated visit |
| `disp.status.record` | mod-populations | Which record gives end-of-study status? | the DS disposition event; a DS record selected by term |
| `disp.reason.source` | mod-populations | Which variable gives the discontinuation reason? | DSDECOD; DSTERM |
| `demo.age.groups` | mod-demographics | Which age groups? | under 65, 65 to 80, over 80; under 65, 65 and over; a stated list |
| `demo.race.pooling` | mod-demographics | Are small race categories pooled? | no; pooled below a stated count |
| `demo.baseline.record` | mod-demographics | Which record gives baseline weight and height? | last before first dose; screening visit |
| `demo.bmi.rule` | mod-demographics | How is BMI obtained? | derived from baseline weight and height, one decimal; as collected |
| `ae.start.imputation` | mod-ae-emergence | How are partial AE start dates completed? | first day of the month, or the first dose date in the month of first dose; first day of the month; not completed |
| `ae.teae.start` | mod-ae-emergence | When does emergence begin? | on or after the first dose date; after the first dose date and time |
| `ae.teae.end` | mod-ae-emergence | When does emergence end? | no end; last dose plus N days; end of study |
| `ae.teae.worsening` | mod-ae-emergence | Do pre-existing events that worsen count? | no; yes, when severity increases |
| `ae.related.values` | mod-ae-emergence | Which relationship values count as related? | a stated list (no default) |
| `ae.severity.worst` | mod-ae-emergence | How is a subject's severity per term chosen? | maximum over events; first event |
| `ae.occurrence.flags` | mod-ae-emergence | Which first-occurrence flags exist? | by subject, by organ class, by term; none |
| `bds.baseline.rule` | mod-bds-visits | Which record is baseline? | last before first dose; last on or before the first dose date; the scheduled baseline visit; mean of pre-dose records |
| `bds.window.table` | mod-bds-visits | How are records assigned to analysis visits? | protocol windows; midpoint windows; nominal visit |
| `bds.window.tiebreak` | mod-bds-visits | Which record wins inside a window? | closest to target, then earlier; closest, then later; last; average |
| `bds.unscheduled.use` | mod-bds-visits | Do unscheduled records compete, for baseline and for windows? | yes; no |
| `bds.eot.record` | mod-bds-visits | Is there an end-of-treatment record? | last on-treatment value; none |
| `tfl.population` | each table family | Which analysis set does the output use? | safety; randomized; efficacy-evaluable |
| `tfl.columns.arms` | each table family | Column order and labels? | ascending dose with placebo first; protocol order |
| `tfl.columns.total` | each table family | Is there a Total column? | yes; no; active arms only |
| `tfl.denominator` | each table family | What is the percent denominator? | subjects in the set per column; subjects with data |
| `tfl.percent.format` | each table family | Percent decimals and zero display? | one decimal, zero count without percent; one decimal always |
| `tfl.quantile.definition` | each table family | Which quantile definition? | sas5; r7 |
| `tfl.rounding.rule` | each table family | How are displayed numbers rounded? | half away from zero; half to even |
| `tfl.decimals.rule` | each table family | How many decimals per statistic? | mean and median one more than the data, SD two more, minimum and maximum as the data; a stated list |
| `tfl.pvalue.format` | each table family | How are p-values displayed? | three decimals, with "<0.001" below that; four decimals, with "<0.0001" below that |
| `tfl.demog.rows` | tfl-demographics | Which characteristics, in which order? | a stated list (no default) |
| `tfl.demog.stats` | tfl-demographics | Which statistics for continuous rows? | n, mean, SD, median, min, max; the same with Q1 and Q3 |
| `tfl.tests.include` | tfl-demographics | Are treatment comparisons shown? | none; ANOVA and chi-square; ANOVA and Fisher exact |
| `tfl.ae.summary.rows` | tfl-ae-summary | Which overview rows? | any, related, serious, leading to discontinuation, fatal; a stated subset |
| `tfl.ae.socpt.sort` | tfl-ae-soc-pt | How are terms sorted? | alphabetical; descending frequency in Total; descending frequency in the highest dose |
| `tfl.ae.socpt.threshold` | tfl-ae-soc-pt | Is there a display threshold? | none; at least X percent in any arm |
| `tfl.ae.socpt.counts` | tfl-ae-soc-pt | Subjects, events or both? | subjects; subjects and events |
| `tfl.vs.scope` | tfl-vitals-by-visit | Which parameters and visits? | stated lists (no default) |
| `tfl.vs.layout` | tfl-vitals-by-visit | How are observed value and change arranged? | side by side; stacked |

The real study adds decisions that the generated studies of M1 do not use.
Two are already known from E25 and E26: the double rounding of p-values,
and the rule that counts a subject as High in a shift table.

## Appendix C. Glossary

| Term | Meaning |
| --- | --- |
| ADaM, SDTM | CDISC analysis and tabulation data models |
| ARS | CDISC Analysis Results Standard: metadata for analyses and outputs |
| ARD | analysis results dataset: one row per computed value |
| CSR, SAP | clinical study report; statistical analysis plan |
| TFL | tables, figures and listings |
| USDM | CDISC Unified Study Definitions Model: the study design as data |
| ODM | CDISC Operational Data Model: CRF metadata and data |
| kit | one study packaged as inputs, gold and twin (section 8) |
| decision | one answered catalog question, with status, class and citation (section 4.3) |
| catalog | the closed list of questions a study answers, with their alternatives (section 5) |
| standard form | the decisions of a study as uniform sentences that a parser can read back (section 4.4) |
| natural form | the same content rewritten as ordinary document prose (section 6.6) |
| reader | the agent that turns documents into decision records |
| machine | the fixed, model-free code that compiles decisions and builds everything else |
| house standard | the conventions, parent specs and templates a company ships to every study |
| probe | a planted record that separates two alternatives of a decision |
| twin | a hidden second dataset with the same design and decisions |
| grid | the canonical display: cell text with references to ARD rows |
| engine | an implementation of the methods: Python or R |
| unit | a module or table family: owner of decisions, scored on its own |
| gold | decisions, specs and results proven to reproduce a reference, or correct by construction |
| reference | something a real study delivered: its ADaM, its CSR tables |
| exception | a recorded difference from a reference, with one class and its proof (section 4.8) |
| mutation | switching one decision to another alternative and rebuilding, to see what changes |
| gate | one command that decides whether a work package is done |
| track | a chain of work packages that one session owns |
| owner node | one of the three points where work waits for the owner (section 2.3) |

## Appendix D. The 30 CSR tables of CDISCPILOT01

Pages are those of `CSR.pdf` in Pilot 6. "Reads" is the expected ADaM
source; confirm it in real-4 and real-5. Figure 14-1 (time to dermatologic
event, page 151) is out of scope for M1.

### D.1 Batch D1: descriptive tables and simple tests (16)

| Table | Title | Population | Method | Reads | Pages |
| --- | --- | --- | --- | --- | --- |
| 14-1.01 | Summary of Populations | all subjects | counts, percents | ADSL | 43 |
| 14-1.02 | Summary of End of Study Data | intent-to-treat | counts, percents; Fisher exact | ADSL | 44 |
| 14-1.03 | Summary of Number of Subjects by Site | all subjects | counts by site, arm and population | ADSL | 45 |
| 14-2.01 | Summary of Demographic and Baseline Characteristics | intent-to-treat | summaries, counts; ANOVA, chi-square. Reproduced in E24 | ADSL | 46 to 48 |
| 14-3.10 | ADAS-Cog (11) - Mean and Mean Change from Baseline over Time | efficacy | summaries by visit, windowed and LOCF | ADQSADAS | 58 |
| 14-4.01 | Summary of Planned Exposure to Study Drug, as of End of Study | safety; completers at week 24 | summaries | ADSL | 62 |
| 14-5.01 | Incidence of Treatment Emergent Adverse Events by Treatment Group | safety | subjects, percents, events; Fisher exact per row. Reproduced in E25 | ADAE, ADSL | 63 to 78 |
| 14-5.02 | Incidence of Treatment Emergent Serious Adverse Events by Treatment Group | safety | as 14-5.01 | ADAE, ADSL | 79 |
| 14-6.01 | Summary Statistics for Continuous Laboratory Values | safety | summaries of value and change by visit | ADLBC, ADLBH | 80 to 94 |
| 14-6.02 | Frequency of Normal and Abnormal (Beyond Normal Range) Laboratory Values During Treatment | safety | counts, percents; exact Fisher on 3 x 3 tables (E27) | ADLBC, ADLBH | 95 to 96 |
| 14-6.03 | Frequency of Normal and Abnormal (Clinically Significant Change from Previous Visit) Laboratory Values During Treatment | safety | as 14-6.02 | a new dataset (E28) | 97 to 98 |
| 14-6.04 | Shifts of Laboratory Values During Treatment, Categorized Based on Threshold Ranges, by Visit | safety | shift counts by visit | ADLBC, ADLBH | 99 to 131 |
| 14-7.01 | Summary of Vital Signs at Baseline and End of Treatment | safety | summaries | ADVS | 139 to 143 |
| 14-7.02 | Summary of Vital Signs Change from Baseline at End of Treatment | safety | summaries | ADVS | 144 to 147 |
| 14-7.03 | Summary of Weight Change from Baseline at End of Treatment | safety | summaries | ADVS | 148 |
| 14-7.04 | Summary of Concomitant Medications (Number of Subjects) | safety | subjects and percents by class and medication | a new dataset from SDTM CM (E28) | 149 to 150 |

### D.2 Batch D2: model-based tables (14)

| Table | Title | Population | Method | Reads | Pages |
| --- | --- | --- | --- | --- | --- |
| 14-3.01 | Primary Endpoint Analysis: ADAS-Cog (11) - Change from Baseline to Week 24 - LOCF | efficacy | ANCOVA with treatment and site group as factors and baseline as covariate; dose-response test; pairwise comparisons | ADQSADAS | 49 |
| 14-3.02 | Primary Endpoint Analysis: CIBIC+ - Summary at Week 24 - LOCF | efficacy | ANCOVA with treatment and site group as factors; dose-response test; pairwise comparisons | ADQSCIBC | 50 |
| 14-3.03 | ADAS-Cog (11) - Change from Baseline to Week 8 - LOCF | efficacy | as 14-3.01 | ADQSADAS | 51 |
| 14-3.04 | CIBIC+ - Summary at Week 8 - LOCF | efficacy | as 14-3.02 | ADQSCIBC | 52 |
| 14-3.05 | ADAS-Cog (11) - Change from Baseline to Week 16 - LOCF | efficacy | as 14-3.01 | ADQSADAS | 53 |
| 14-3.06 | CIBIC+ - Summary at Week 16 - LOCF | efficacy | as 14-3.02 | ADQSCIBC | 54 |
| 14-3.07 | ADAS-Cog (11) - Change from Baseline to Week 24 - Completers at Week 24 - Observed Cases - Windowed | completers | as 14-3.01 | ADQSADAS | 55 |
| 14-3.08 | ADAS-Cog (11) - Change from Baseline to Week 24 in Male Subjects - LOCF | efficacy | as 14-3.01 | ADQSADAS | 56 |
| 14-3.09 | ADAS-Cog (11) - Change from Baseline to Week 24 in Female Subjects - LOCF | efficacy | as 14-3.01 | ADQSADAS | 57 |
| 14-3.11 | ADAS-Cog (11) - Repeated Measures Analysis of Change from Baseline to Week 24 | efficacy | mixed model for repeated measures | ADQSADAS | 59 |
| 14-3.12 | Mean NPI-X Total Score from Week 4 through Week 24 - Windowed | efficacy | as 14-3.01 | ADQSNPIX | 60 |
| 14-3.13 | CIBIC+ - Categorical Analysis - LOCF | efficacy | counts, percents; CMH test controlling for site group | ADQSCIBC | 61 |
| 14-6.05 | Shifts of Laboratory Values During Treatment, Categorized Based on Threshold Ranges | safety | shift counts; CMH test controlling for baseline status | ADLBC, ADLBH | 132 to 137 |
| 14-6.06 | Shifts of Hy's Law Values During Treatment | safety | shift counts; CMH test controlling for baseline status. Reproduced in E26 | ADLBHY | 138 |
