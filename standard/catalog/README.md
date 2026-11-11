# Decision catalog

The closed list of questions a study answers (PLAN.md section 5, appendix
B). This is the draft of std-1, version `draft-1`. The owner approves it at
node N1; only then is it frozen as `catalog@1`. ADR-004 records the choices
behind it.

| File | Holds |
| --- | --- |
| `catalog.yaml` | name and version, the units, the design features, the entries in the order of the standard form, and what was left out of appendix B with the reason |
| `entries/<id>.yaml` | one entry: question, alternatives with statement templates, house default, sources, probes (schema: `standard/schemas/catalog-entry.schema.json`) |
| `templates/<id>.yaml` | the compile template: one fragment per alternative, a yamaa fragment by ADaM dataset or parameters for the ARS and layout templates |
| `phrasings/<id>.yaml` | three natural variants of every statement (`plain`, `formal`, `brief`), each with the slots of its statement |
| `knowledge/<id>.md` | reading notes: where documents state the decision, words to look for, traps |
| `sources.yaml` | the public sources that entries cite |
| `probes.yaml` | probe recipes: the planted record that separates two alternatives |

Commands (see CLAUDE.md for the environment):

```text
specfirst catalog                 schema, cross-references, probes, phrasings, notes, parameters
specfirst catalog --roundtrip     decisions to statements to decisions, for every alternative
specfirst catalog --sources       the cited files and texts, on the fetch cache
specfirst catalog --yamaa --run   compile every alternative; yamaa check; build a tiny study
specfirst catalog --tables        compile every alternative; ARS schema and layouts
specfirst gate std-1              all of the above with lint, tests and the house standard
```

To change an entry: edit its file, its template, its phrasings and its
notes together, then run `specfirst catalog` and `specfirst house --write`
(the standards document is rendered from the catalog). After N1 a change
needs an ADR.
