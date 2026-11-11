# Third-party sources

Rule 1 of PLAN.md section 2.1: public sources only, and every imported file
is recorded here with URL, commit and license.

## Imported files

No third-party study data or document is committed to this repository. The
sources below are fetched by `specfirst fetch` into an ignored cache and are
read there (rule 4, E20).

Code adapted from a source, with its license:

| File here | Adapted from | Commit | License | What changed |
| --- | --- | --- | --- | --- |
| `src/specfirst/machine/lineage.py` | https://github.com/RConsortium/submissions-pilot7-synthetic-data `.github/scripts/study_dashboard/references.py` and `.github/scripts/study_dashboard/lineage.py` | 213cb6ab3adc51abe4295cbbc546c0e6d46c3df8 | MIT (Pilot 7 `LICENSE`: original Pilot 7 code). Copyright notice and license text: `third_party/licenses/PILOT7-MIT.txt` | The rules that decide what an expression reads are unchanged. Added: the place of every read as a JSON pointer, unknown bare names, datasets read as a whole. Removed: source spans computed from YAML text. ADR-001, item 7. |
| `src/specfirst/machine/runner.py` | https://github.com/RConsortium/submissions-pilot7-synthetic-data `.github/scripts/resolved_specs.py`, the function `relocate` | 213cb6ab3adc51abe4295cbbc546c0e6d46c3df8 | MIT. Copyright notice and license text: `third_party/licenses/PILOT7-MIT.txt` | The function `_relocate` walks the same fields of a resolution. One direction only (absolute to relative); each distinct file is resolved once. The rest of the file is ours. |

Specifications and templates written for this repository that take over
idioms of a source. No file and no passage was copied; the table records
where a way of writing a rule comes from.

| Files here | Idiom taken from | Commit | License |
| --- | --- | --- | --- |
| `standard/houses/open-default@1/adam/*.yaml`, `standard/catalog/templates/*.yaml` (yamaa parent specs and fragments) | Pilot 7 `spec/yamaa/pilot-program/adsl_v1.yaml` and `adae_v1.yaml` (first-occurrence flags by a filtered row number; the earliest exposure date as the minimum of the date text; lookups that keep the first or last record) and `cdiscpilot01/spec/yamaa/advs.yaml` (the end-of-treatment record as a second row template that repeats one collected record) | 213cb6ab3adc51abe4295cbbc546c0e6d46c3df8 | MIT (Pilot 7 `LICENSE`); text in `third_party/licenses/PILOT7-MIT.txt` |
| the same files | yamaa `benchmarks/adam-adae-partial-dates` (a completed date not before the treatment start), `adam-adae-onset-emergence` (a window after last exposure), `adam-adlb-closest-visit` (rank by distance from the target day), `adam-adae-post-dose-window` (a range lookup with `between`) | 93a6757594988fddc9b05d220d5f53deb5085d50 | MIT (yamaa `LICENSE`) |
| `standard/houses/open-default@1/ars/*.yaml` (ARS templates) | CDISC ARS `workfiles/examples/ARS v1/Common Safety Displays.json`: the way analysis sets, groupings, data subsets, methods, analyses and the list of contents are laid out and named. IDs and texts are ours; no result value is taken | 2c9b4b68724386e8f91dc576724855af7fafac65 | MIT for code, CC BY 4.0 for content (as PLAN.md appendix A records it) |

`tests/pilot` (A5-adapted) compares our Python files with the Python files
of the cached sources line by line and fails when a file that is not in
this table shares more than a few lines with one of them: a row that is
missing cannot be found by reading the table.

## Pinned sources

`sources.yaml` is the machine-readable form; a test keeps it, this file and
appendix A of PLAN.md in agreement. "Confirmed" is what base-0 found in each
repository at the pinned commit on 2026-11-11.

| Name | Repository | Commit | License in the plan | Confirmed in base-0 |
| --- | --- | --- | --- | --- |
| p7 | https://github.com/RConsortium/submissions-pilot7-synthetic-data | 213cb6ab3adc51abe4295cbbc546c0e6d46c3df8 | MIT for code; study data excluded | `LICENSE` is MIT with the scope "original Pilot 7 code and documentation only". `LICENSING.md` excludes all study data and imported documents; CDISC pilot material stays under CDISC terms (`LICENSE-CDISC.txt`). |
| yamaa | https://github.com/elong0527/yamaa | 93a6757594988fddc9b05d220d5f53deb5085d50 | MIT | `LICENSE` is MIT (yamaa contributors). |
| ars | https://github.com/cdisc-org/analysis-results-standard | 2c9b4b68724386e8f91dc576724855af7fafac65 | MIT for code, CC BY 4.0 for content | `LICENSE` is MIT. No CC BY 4.0 statement was found in the repository's text files; see the note below. |
| p6 | https://github.com/RConsortium/submissions-pilot6-adams-tlfs | a4f85c95cfef1f6aa27795362630f8ae43210185 | no license file: fetch, never redistribute | No license file at any depth. Its data folders hold DVC pointers only; `documents/CSR.pdf` and `documents/SAP.pdf` are real files. |
| atorus | https://github.com/atorus-research/CDISC_pilot_replication | fc8d658d7709aac0cccd753d0ca9ae6726090a61 | MIT | `LICENSE` is MIT (Atorus Research). |
| phuse | https://github.com/phuse-org/phuse-scripts | 398a6d33ced9359ffb58c46650a6d488811176b1 | MIT-style for code; pilot data under CDISC terms | `LICENSE.md` is the MIT permission text without the "MIT License" title. It says nothing about the pilot data. |
| c360i | https://github.com/cdisc-org/360i | 24bd98bdcea3db3046436e6a749bbbc92196fe12 | MIT for code, CC BY 4.0 for content | `LICENSE` is MIT. No CC BY 4.0 statement was found in the repository's text files; see the note below. |
| acdc | https://github.com/cdisc-org/analysis-concepts | 739344ca31203bb502efeee2b855286e17977be6 | MIT | `LICENSE` is MIT. |
| siera | https://github.com/clymbclinical/siera | 9208a9b6a00876f13d2b17f01aa318290c066674 | MIT | `DESCRIPTION` says "MIT + file LICENSE"; `LICENSE.md` is MIT (siera authors). |
| cardinal | https://github.com/pharmaverse/cardinal | b1fe03a760a1ca3b4610830ba64be5bd3e6ff4a5 | Apache-2.0 | `LICENSE.md` is Apache License 2.0; `DESCRIPTION` says "Apache License (>= 2)". |
| pharma-skills | https://github.com/RConsortium/pharma-skills | e5db96d54ef5a79cbfd06e2339a3351e4583f8da | MIT per skill folder | No license file at the root. Each of the 15 skill and automation folders has its own `LICENSE`; all 15 are MIT. |
| pharmaverseraw | https://github.com/pharmaverse/pharmaverseraw | e0771afea8bead7e64bc7cf2ff53ef8b638c6c1b | Apache-2.0 | `LICENSE.md` is Apache License 2.0; `DESCRIPTION` says "Apache License (>= 2.0)". |
| c360i-pocs | https://github.com/lexjansen/cdisc360i-pocs | 9f6de449cbff0c3f16fb10a93e4e79c7cd6ad43e | MIT | `LICENSE` is MIT (Lex Jansen). |

Note on ars and c360i. The plan lists "CC BY 4.0 for content" for the two
CDISC repositories. At the pinned commits only the MIT `LICENSE` file states
a license; a search of their Markdown, text, YAML and HTML files for
"CC BY" and "Creative Commons" found nothing. This does not affect the
project now, because nothing from either repository is committed or
redistributed. It matters only if content from them is ever imported;
confirm the terms with CDISC before that.

## Pinned files

| Source | Path | SHA-256 | Used for |
| --- | --- | --- | --- |
| ars | `workfiles/examples/ARS v1/Common Safety Displays.json` | 90358dd60d687332f2138aa50435b4050fa91be3f52958169229daa269fe31b3 | the ARS v1 example of E2 to E5; the hash is the one in appendix A |
| p6 | `documents/CSR.pdf` | 0cab016c76abb3dcaef31110611c95dbd9cd00df083b35e6d28fd69fca0d842d | the CSR of CDISCPILOT01 (492 pages); recorded in base-0 |
| p6 | `documents/SAP.pdf` | 210b7f1fdb0fd95e1b00b64fe1c7527d0000bd4e66b6ae31fdc08e2741af1bc7 | the SAP of CDISCPILOT01; recorded in base-0 |

## Engines and libraries

Python and R packages are dependencies, not imported files. Their exact
versions are in `env/requirements.lock` and `env/r-packages.lock`. The
engine PLAN.md pins is yamaa 0.7.0 from PyPI (MIT).

## Other public documents

Listed in appendix A of PLAN.md: the FDA Standard Safety Tables and Figures
Integrated Guide and MAPP 6025.9, the 360i roadmap posts, and the Claude
Code documentation. None is fetched or committed.
