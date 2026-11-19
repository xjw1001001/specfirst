# specfirst

An open-source, spec-first framework for clinical analysis and reporting.

> Status: research prototype, work in progress. Nothing here is validated;
> agreement with a reference is evidence, not validation. `specfirst` is a
> working name. [PLAN.md](PLAN.md) is the full design and plan.

## The idea

Most of the work between a SAP and a set of tables is not statistics. It is
hundreds of small decisions: which adverse events count as
treatment-emergent, who is in the safety set, which record is baseline, how
a visit window breaks a tie, how a zero count is printed. Today these
decisions live inside programs and in people's heads. They are hard to
review, hard to compare across studies and hard to trace back to the
document that justified them.

specfirst makes the decisions the source of truth, and splits the work in
two:

| Stage | Who | In | Out |
| --- | --- | --- | --- |
| Read | a reader agent (a language model) | protocol, SAP, the house standard, the decision catalog | one record per decision, in standard form, with the quote it rests on; questions for a person; what it could not map |
| Build | the machine, with no model in it | decision records and SDTM | ADaM specs, analysis and display specs; then ADaM, analysis results, tables and a trace graph |

**AI reads; machines build.** The model only proposes decisions. Everything
after that is deterministic and checked by scripts.

```text
 protocol, SAP          house standard          decision catalog
       |                      |                        |
       +--------------> READ (language model) <--------+
                              |
              decision records: a standard-form sentence
              per decision, with its quote, class and status
                              |
              people review, answer questions, edit decisions
                              |
  SDTM ---------------> BUILD (deterministic, no model)
                              |
        yamaa ADaM specs, CDISC ARS analyses, layout specs
                              |
              ADaM -> analysis results (ARD) -> table grids
                              |
   trace: cell -> result -> method -> ADaM -> SDTM -> decision -> quote
```

## Design

### Decisions are data: the catalog

A study answers a closed list of questions, the decision catalog. Each entry
belongs to one unit (a module such as treatment, populations or AE
emergence, or a table family such as the AE summary). Each entry has a
question, a set of alternatives, a house default, a public source for every
alternative, and planted test cases ("probes") that tell the alternatives
apart.

```yaml
id: ae.teae.end
unit: mod-ae-emergence
value: {rule: last_dose_plus_days, days: 30}
status: stated            # stated | default | asked | conflict | not_applicable
class: document_rule      # where the information lives
statement: >
  An adverse event is treatment-emergent if it starts on or after the first
  dose date and no later than 30 days after the last dose date.
citations:
  - {doc: sap, anchor: "9.2/s3", quote: "... up to 30 days after the last dose ..."}
```

Rules that keep this honest:

- **Silence.** When the documents do not state a decision, the house
  default applies and is cited. If there is no default, the reader asks a
  person. It never guesses.
- **Closed vocabulary.** A decision the catalog lacks is `custom`: a
  hand-written fragment, flagged and counted, and a proposal to extend the
  catalog.
- **Classes.** A decision is scored by where its information lives (the
  documents, the house standard, a person), so a score can show whether the
  reader misread a document or guessed a convention.

### The standard form

Each alternative has one controlled sentence with typed slots. The list of
these sentences for a study is its standard form. It is what people review
and approve: short, uniform, each sentence linked to its source quote and to
the cells it affects. It is also exact: a parser maps every sentence back to
its decision without a model, so decisions to sentences to decisions is a
round trip that is tested.

### Compile, do not write code

For a catalog decision, the spec fragment is a pure function of the decision
value. Reviewers approve decisions, not code, and a decision can never
disagree with its spec. The build reuses public standards and tools rather
than inventing formats:

- ADaM specs in [yamaa](https://github.com/elong0527/yamaa), with parent specs that carry
  the house standard;
- analyses in CDISC's Analysis Results Standard (ARS v1);
- a small layout spec for what ARS does not cover (rows, columns, cell
  templates, decimals);
- Define-XML and CDISC CORE for conformance checks.

### Methods have numbered semantics

ARS names a method; it does not fix its arithmetic. A method registry does:
each entry lists the options that change numbers (quantile definition,
rounding rule, exact or asymptotic test, LS-means weights), with test
vectors. Descriptive methods and simple tests have a Python and an R
implementation that must agree. Model-based methods (ANCOVA, mixed models)
are R only, on `emmeans` and `mmrm`. Display rules such as rounding and
p-value formats are registry entries and decisions too.

### One chain, traced end to end

Every element of every layer (documents, SDTM, ADaM, analyses, results,
display cells) has a stable ID, a content hash and the file and line it came
from. Edges link a printed cell to its results, the analysis, the ADaM
variables, their derivation down to SDTM, and the decisions with their
quotes. Edges proven by execution or static analysis are kept apart from
judged ones (whether a quote supports a decision), which only a person can
approve. Four properties are tested for every study:

| Property | Meaning |
| --- | --- |
| P1 Determinism | The same decisions and inputs give the same bytes. |
| P2 Reproduction | The build equals the reference, or each difference has exactly one class and a proof. |
| P3 Traceability | Every printed number has a complete path to SDTM and to the decisions behind it. |
| P4 Identifiability | Changing any decision to another alternative changes at least one result. |

### Differences from a reference are classified

When our build differs from what a study delivered (its ADaM, its CSR
tables), the difference gets exactly one class: the reference followed
another alternative of a decision (proved by building with it), the
reference contradicts its own data or documents, or the public data are not
the data behind the reference. An unclassified difference fails the build.
Often a difference turns out to be a decision, not an error.

### Measuring the reader

A reader that is a language model has to be measured, not trusted. specfirst
generates simulated studies by trial design, with known decisions:

- SDTM generated from a design model, with probes planted for every
  decision of the study;
- two datasets per study: the visible one the reader sees, which carries
  only some of the probes, and a hidden twin on which every applicable
  decision changes a printed cell;
- the protocol and SAP written twice: in standard form (the gold) and in
  natural, reworded form, checked so that a rewrite cannot change a value.

The reader works in an isolated task folder with no gold in it; transcripts
and workspaces are scanned for canary strings planted in the gold. The
scorer compares its decisions with gold (value, status, citation, questions
asked), builds them on the visible data and on the twin, and attributes
every wrong cell to the decision and layer that caused it. Two controls run
on the same studies: the house standard alone, and a parser on the
standard-form documents, which must score 100%.

"Training" means improving the reader's knowledge files and skills against
these scores, never changing model weights.

### People stay in charge

To change something, a person says it in plain words. The agent edits the
decision record and shows the old and new standard-form sentences; the
machine rebuilds and lists every changed cell, before and after, with its
trace. The agent only ever edits decisions.

## Where it stands

Built, each part with a scripted gate passed on a clean clone and a signed
independent review (reports with commands and output in
[docs/reports/](docs/reports/)):

- the CDISCPILOT01 kit: ADaM rebuilt from SDTM with public specs, two
  result engines, and the first table (the adverse event summary) with its
  cell-level trace;
- the decision catalog, its standard form, the compiler and a house
  standard, frozen as `catalog@1`;
- the study generator for a parallel-group design, with documents in both
  forms;
- the scorer.

In progress: the reader harness and the reader's first scores. Next: all 30
CSR tables of CDISCPILOT01 (16 descriptive, 14 model-based), the edit loop,
more table families. `docs/state/<track>.md` has the state of each track.

## How it is built

[PLAN.md](PLAN.md) is a contract and changes only through a decision record
(an ADR in [docs/decisions/](docs/decisions/)) that the owner approves. The
code and documents are written by Claude Code agents working to that plan in
parallel tracks. A work package merges only after its gate (one command)
passes on a fresh clone with a fresh install, every checker has first caught
a defect planted for it, and an agent with a fresh context has reviewed and
signed it. Builds are deterministic: no clock, no unseeded randomness,
sorted output. Lessons from failures are kept in
[docs/lessons.md](docs/lessons.md).

## Quick start

Ubuntu 24.04, also under WSL2. The builds need R; the install pins it.

```bash
sudo bash env/system.sh             # system packages: Python, R, poppler, git, make
make install                        # Python environment and R library from the lock files
. scripts/env.sh                    # once per shell
specfirst fetch                     # pinned public sources into an ignored cache
specfirst kit assemble cdiscpilot01 # the pilot kit, copied from the cache by SHA-256
specfirst build cdiscpilot01        # ADaM, results (both engines), grids, trace graph
specfirst check cdiscpilot01        # compare with the references
specfirst status                    # the state of every track
```

`env/README.md` describes the environment. `make test`, `make lint` and
`make ascii` are what CI runs.

| Folder | Content |
| --- | --- |
| `standard/` | schemas, the decision catalog, the method registry, house standards |
| `src/specfirst/` | the Python package and the `specfirst` command |
| `r/specfirstr/` | the R result engine |
| `skills/` | the reader's knowledge, as Agent Skills |
| `kits/` | kit manifests; study data are fetched, never committed |
| `docs/` | state per track, decisions (ADRs), reports, lessons |
| `evidence/` | the feasibility spikes behind PLAN.md section 3 |
| `tests/`, `env/`, `third_party/` | tests and planted defects; lock files; pinned sources |

## Data and sources

Public sources only, each recorded with URL, commit and license in
[third_party/SOURCES.md](third_party/SOURCES.md). No study data or
third-party documents are committed: the CDISC pilot data (CDISCPILOT01) are
fetched at pinned commits into an ignored cache and stay under CDISC's
terms. Generated studies are simulated and make no claim of clinical
realism.

## License

MIT for original code and documents. See [LICENSE](LICENSE).

Questions and suggestions are welcome as GitHub issues.
