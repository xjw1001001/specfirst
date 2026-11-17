# specfirst

A spec-first framework for clinical analysis and reporting. `specfirst` is a
working name.

AI reads; machines build. A language model turns a study's protocol and SAP
into a short list of decisions in a standard form. Fixed machinery compiles
those decisions into specifications and builds every dataset and output, so
that each printed number traces back to its analysis, its derivation rule,
its source data and the sentence that justified it.

[PLAN.md](PLAN.md) is the plan. Start there.

## Status

Passed so far: base-0 (repository, environment, pinned sources, evidence
tests, shared formats), real-1 (the pilot kit, its ADaM proof and the SDTM
to ADaM part of the trace graph), real-2 (method registry, the Python and
the R result engine, classified differences from a reference) and std-1
(decision catalog, standard form, compiler and house standard; a draft
until the owner approves it at node N1).
`specfirst status` prints the state of every track; the reports are in
`docs/reports/`.

## Quick start (Ubuntu 24.04, also under WSL2)

```bash
sudo bash env/system.sh      # system packages: Python, R, poppler, git, make
make install                 # Python environment and R library from the lock files
. scripts/env.sh             # once per shell
specfirst fetch              # pinned public sources into the ignored cache
specfirst gate base-0        # the gate of work package base-0
```

`env/README.md` describes the environment and its lock files.

## Layout

| Folder | Content |
| --- | --- |
| `docs/` | state per track, lessons, decisions (ADRs), gate reports |
| `standard/` | schemas, decision catalog, method registry, house standards |
| `src/specfirst/` | the Python package and the `specfirst` command |
| `r/specfirstr/` | the R result engine and the model-based methods |
| `skills/` | the reader's knowledge as Agent Skills |
| `kits/` | small generated fixtures; other kits are generated or fetched |
| `viewer/` | the static page template |
| `evidence/` | the feasibility spikes behind PLAN.md section 3 |
| `tests/` | unit tests, evidence tests, method vectors, planted defects |
| `third_party/` | the pinned sources; the fetch cache itself is not committed |
| `env/` | lock files and install scripts |

## Clean room

Public sources only. No third-party study data or documents are committed:
they are fetched at pinned commits into an ignored cache. See PLAN.md
section 2.1 and `third_party/SOURCES.md`.

## License

MIT for original code and documents. See [LICENSE](LICENSE).
