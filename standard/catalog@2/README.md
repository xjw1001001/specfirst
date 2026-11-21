# Decision catalog, version 2

The closed list of questions a study answers (PLAN.md section 5, appendix
B). Version 2, `catalog@2` (ADR-020): frozen when the part catalog-2b merged,
on 2026-11-21, and tagged; `standard/versions.yaml` holds its status and tree.
Version 1 is `standard/catalog@1/`, frozen at owner node N1 on 2026-11-17
(ADR-004). What changed from version 1 is in `migration.yaml`, each line with
its record of `standard/BACKLOG.yaml`.

| File | Holds |
| --- | --- |
| `catalog.yaml` | name and version, the schema of the entries, the units, the design features, the entries in the order of the standard form, and what was left out of appendix B with the reason |
| `entries/<id>.yaml` | one entry: question, alternatives with statement templates, fixed rules, sources, probes (schema: `standard/schemas/catalog-entry.v1.schema.json`). No defaults: a house holds them (`standard/houses/<house>@<n>/defaults.yaml`) |
| `templates/<id>.yaml` | the compile template: one fragment per alternative, a yamaa fragment by ADaM dataset or parameters for the ARS and layout templates |
| `phrasings/<id>.yaml` | three natural variants of every statement (`plain`, `formal`, `brief`), each with the slots of its statement |
| `knowledge/<id>.md` | reading notes: where documents state the decision, words to look for, traps |
| `sources.yaml` | the public sources that entries cite |
| `probes.yaml` | probe recipes: the planted record that separates two alternatives |
| `migration.yaml` | what the step from `catalog@1` keeps: every alternative added, removed, renamed or changed in meaning |

Commands (see CLAUDE.md for the environment):

```text
specfirst catalog --catalog catalog@2 --house open-default@2              schema, cross-references, probes, phrasings, notes, parameters
specfirst catalog --roundtrip --house open-default@2                      decisions to statements to decisions
specfirst catalog --sources --house open-default@2                        the cited files and texts, on the fetch cache
specfirst catalog --yamaa --run --house open-default@2                    compile every alternative; yamaa check; build a tiny study
specfirst catalog --tables --house open-default@2                         compile every alternative; ARS schema and layouts
specfirst gate catalog-2b                                                 all of the above with the checks of the versions
```

This version is frozen: a change is a new version, `catalog@3`, with its
own `migration.yaml` and backlog records (ADR-020, decision 4).
