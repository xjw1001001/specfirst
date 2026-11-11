# Kit cdiscpilot01

CDISCPILOT01, the CDISC SDTM/ADaM pilot study, as Pilot 7 stages it: the
tier C kit of PLAN.md section 6.1, the reproduction anchor of D1 and D2.

This folder holds `kit.yaml` and this file, and nothing else. The study data
and documents are not ours to redistribute (rule 4 of PLAN.md section 2.1,
E20). They are fetched at a pinned commit and assembled on demand:

```bash
specfirst fetch                      # Pilot 7 at the pinned commit, into the cache
specfirst kit assemble cdiscpilot01  # copy 64 files, checking the SHA-256 of each
specfirst build cdiscpilot01         # assemble, then resolved specs, ADaM datasets, graph
specfirst check cdiscpilot01         # P2 against the reference ADaM, and the trace
specfirst check cdiscpilot01 --twice # first two fresh builds, each in its own folder (P1)
```

## Layout of the assembled kit (build/kits/cdiscpilot01/)

```text
kit.yaml                 a copy of the manifest
inputs/                  everything an agent may read
  docs/sap.pdf           the statistical analysis plan (the same file as Pilot 6's)
  docs/dataguide.pdf     the analysis data reviewer's guide
  docs/define-adam.xml   the published ADaM Define-XML
  data/sdtm/             22 SDTM datasets (Parquet) and their Define-XML, define.xml
gold/                    never placed in an agent's workspace
  spec/                  Pilot 7's yamaa specifications, at their paths in Pilot 7:
    cdiscpilot01/spec/yamaa/   project.yaml, codelists.yaml and the 10 specifications
    spec/yamaa/pilot-program/  the parent specifications they inherit from
  reference/adam/        the 10 reference ADaM datasets: what P2 compares with
  claims/                Pilot 7's reviewed claims, one file per dataset
  resolved/              built: each specification as yamaa composes it, with the file
                         and line of every element
  data/adam/             built: the 10 ADaM datasets, as canonical Parquet
  graph/                 built: nodes.jsonl, edges.jsonl, coverage.json
  build.json             built: the SHA-256 of every built file
```

The specifications keep their paths because a child names its parent by a
relative path. They are not edited. The runner hands every input over in
memory (ADR-001), so the data paths written in them do not have to exist.

`gold/reference/`, `gold/claims/`, `gold/resolved/` and `gold/build.json`
are not in the layout of PLAN.md section 8. ADR-001 gives the reasons.

## What is not here yet

- The protocol. The pilot's protocol is in the CDISC 360i repository; no
  work package has needed it so far.
- `gold/decisions.jsonl`, ARS, layouts, ARD, grids: real-2 to real-5 and
  std-2.
- Two datasets the CSR tables need and the reference ADaM lacks (E28):
  real-4.
