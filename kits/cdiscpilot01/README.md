# Kit cdiscpilot01

CDISCPILOT01, the CDISC SDTM/ADaM pilot study, as Pilot 7 stages it: the
tier C kit of PLAN.md section 6.1, the reproduction anchor of D1 and D2.

This folder holds `kit.yaml`, this file and the files of our own that the
manifest names: `gold/exceptions.yaml`, one layout per output in
`gold/layout/`, the reporting event of the efficacy tables in
`gold/events/` and their decision records in `gold/decisions/` (real-5a,
ADR-015). It holds nothing else. The study data and documents are not
ours to redistribute
(rule 4 of PLAN.md section 2.1, E20). They are fetched at pinned commits and
assembled on demand:

```bash
specfirst fetch                      # Pilot 7, Pilot 6 and the ARS repository, into the cache
specfirst kit assemble cdiscpilot01  # copy 67 files, checking the SHA-256 of each
specfirst build cdiscpilot01         # resolved specs, ADaM, results (needs R), grids, graph
specfirst check cdiscpilot01         # P2 for ADaM, the trace, P2 for results, the engines, the grids
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
  spec/ars/              CDISC's ARS v1 example "Common Safety Displays" (5 outputs, 31
                         analyses, 3,735 embedded results) and the JSON Schema generated
                         from the ARS model
  reference/adam/        the 10 reference ADaM datasets: what P2 compares with
  reference/csr/CSR.pdf  the CSR (Pilot 6): its Tables 14-3.01, 14-3.03 and 14-3.05 are the
                         references of the efficacy grids, parsed from their pages on
                         every check into build/csr/cdiscpilot01/ (never into git)
  claims/                Pilot 7's reviewed claims, one file per dataset
  exceptions.yaml        a copy of ours: the classified differences from the references
  layout/                a copy of ours: one layout per output that is built as a grid
  events/                a copy of ours: the reporting event of the efficacy tables
  decisions/             a copy of ours: the decision records of the efficacy tables
  resolved/              built: each specification as yamaa composes it, with the file
                         and line of every element
  data/adam/             built: the 10 ADaM datasets, as canonical Parquet
  graph/                 built: nodes.jsonl, edges.jsonl, coverage.json
  ard/                   built: the results of the analyses of each reporting event, one row
                         per value; <id>.jsonl the gold ARD (the Python engine's rows, and
                         the R engine's rows of the model-based methods, which only R
                         implements), <id>.r.jsonl from the R engine
  ars/                   built: each reporting event with our results as raw values
  grid/                  built: per output <id>.json, the display grid, and
                         <id>.shell.json, its mock shell (masks in place of numbers)
  out/                   built: a page for each of the two, <id>.html and <id>.shell.html
  build.json             built: the SHA-256 of every built file
work/                    what a build hands to the R engine; not part of what was built
```

The specifications keep their paths because a child names its parent by a
relative path. They are not edited. The runner hands every input over in
memory (ADR-001), so the data paths written in them do not have to exist.

`gold/reference/`, `gold/claims/`, `gold/resolved/`, `gold/build.json`,
`gold/ars/` and the two files per reporting event in `gold/ard/` are not in
the layout of PLAN.md section 8. ADR-001 and ADR-002 give the reasons.
`gold/layout/` is not in it either: section 8 puts layout files under
`gold/spec/`, which in this kit only the manifest may fill, from the fetch
cache. ADR-003 gives the reason; the shells are in `gold/grid/`.

## Displays (real-3a)

`kit.yaml` lists the outputs that are built as grids, each with its layout.
So far that is one: `Out14-3-1-1`, the overall summary of adverse events
(ADR-005). The grid is built from the layout and the ARD of the Python
engine. Every cell text is compared with the `formattedValue`s the example
embeds: 27 cells show 51 results, and all 27 are equal. The graph leads
from each cell to its ARD rows, their analyses, the ADaM columns the
analyses read, and on to SDTM columns.

## Results (real-2)

`kit.yaml` names one reporting event, `common-safety-displays`. The result
engines read its analyses and the ADaM datasets of the build, never the
reference ADaM and never the fetch cache. The results the example embeds
are a reference: both engines reproduce 3,711 of 3,735 as printed, and
`gold/exceptions.yaml` gives a class and a proof to the 25 that differ (the
24 of evidence E3 and one first quartile; ADR-002).

## What is not here yet

- The protocol. The pilot's protocol is in the CDISC 360i repository; no
  work package has needed it so far.
- `gold/decisions.jsonl`, the grids of the other four outputs of the
  example, and the ARS files of the CSR tables: real-3 to real-5 and std-2.
- Two datasets the CSR tables need and the reference ADaM lacks (E28):
  real-4.
