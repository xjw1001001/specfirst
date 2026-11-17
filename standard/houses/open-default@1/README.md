# House standard open-default@1

The conventions that hold for a study where its protocol and SAP are silent
(PLAN.md sections 5.2 and 13.4), built from public standards only.
Delivered by std-1 and accepted by the owner at node N1 with `catalog@1`
(2026-11-17; ADR-004).

| File | Holds |
| --- | --- |
| `STANDARD.md` | the citable standards document: every default as a statement of the standard form with its anchor. Rendered by `specfirst house --write`; never edited by hand |
| `house.yaml` | the manifest: slot values of defaults (none yet), the parent specs with the order of their output variables, the templates |
| `adam/adsl.yaml`, `adae.yaml`, `advs.yaml` | parent yamaa specs: what no decision changes. A compiled study spec names one as its parent and includes one fragment per decision |
| `ars/common.yaml`, `ars/<family>.yaml` | ARS templates: analysis sets and methods, then groupings, data subsets, analyses and the output of each table family |
| `layout/<family>.yaml` | layout templates (layout draft 0, to be aligned with ADR-003 of real-3) |

The defaults themselves are the `house_default` of each catalog entry.
A decision taken from this standard has the status `default`, the class
`house_default`, and cites `doc:house#<anchor>`.

Names follow ADaMIG 1.3 and OCCDS 1.1 for variables and the CDISC ARS v1
example "Common Safety Displays" for analyses. A column whose name starts
with an underscore is a working value: it is not written to the dataset.
