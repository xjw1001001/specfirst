"""A made-up study of three subjects, as a checkout with a fetch cache and a kit.

Everything here is invented for the tests: no study data. `make` writes

    <root>/PLAN.md, third_party/sources.yaml     so that <root> is a checkout
    <root>/standard/schemas/graph.schema.json    copied from the real checkout
    <root>/third_party/cache/toy/...             what `specfirst fetch` would have fetched
    <root>/kits/toy/kit.yaml                     the manifest, with the right hashes

The two specifications are small but use a helper column, a literal, a case
expression, a date and a lookup from one ADaM dataset into another.
"""

from __future__ import annotations

import datetime
import json
import shutil
from pathlib import Path

from specfirst.kit import KitFile, files_block
from specfirst.machine.canonical import sha256_file

COMMIT = "0123456789abcdef0123456789abcdef01234567"

SOURCES = f"""\
sources:
  - name: toy
    title: Toy study
    repository: example/toy
    commit: {COMMIT}
    license: MIT
    used_for: tests
"""

PROJECT = """\
yamaa: "1.0"
type: project
adam:
  specs:
    - adsl.yaml
    - adae.yaml
"""

ADSL = """\
yamaa: "1.0"
type: spec
model: ADaM
domain: ADSL
keys:
  - USUBJID
input:
  DM:
    path: ../data/sdtm/dm.parquet
    relative_to: entry
base: DM
output:
  path: ../data/adam/adsl.parquet
  relative_to: entry
  columns:
    - STUDYID
    - USUBJID
    - AGE
    - AGEGR1
    - SAFFL
    - TRTSDT
  order_by:
    - variable: USUBJID
      nulls: last
columns:
  - name: STUDYID
    type: str
    label: Study Identifier
    derivation: "'TOY'"
  - name: USUBJID
    type: str
    label: Unique Subject Identifier
    derivation: DM.USUBJID
  - name: AGE
    type: float
    label: Age
    derivation: DM.AGE
  - name: AGE_N
    type: float
    label: Age, helper
    derivation: DM.AGE
  - name: AGEGR1
    type: str
    label: Age Group
    derivation:
      case:
        - when: "AGE_N < 65"
          then: "'<65'"
        - otherwise: "'>=65'"
  - name: SAFFL
    type: str
    label: Safety Flag
    derivation:
      case:
        - when: "DM.ARM <> 'Screen Failure'"
          then: "'Y'"
        - otherwise: "'N'"
  - name: TRTSDT
    type: date
    label: Date of First Dose
    derivation:
      impute:
        source: DM.RFSTDTC
        type: date
"""

ADAE = """\
yamaa: "1.0"
type: spec
model: ADaM
domain: ADAE
keys:
  - USUBJID
  - AESEQ
input:
  AE:
    path: ../data/sdtm/ae.parquet
    relative_to: entry
  ADSL:
    path: ../data/adam/adsl.parquet
    relative_to: entry
    schema: adsl.yaml
base: AE
output:
  path: ../data/adam/adae.parquet
  relative_to: entry
  columns:
    - USUBJID
    - AESEQ
    - AEDECOD
    - AGE
    - TRTEMFL
  order_by:
    - variable: USUBJID
      nulls: last
    - variable: AESEQ
      nulls: last
intermediates:
  - id: SBJ
    dataset: ADSL
    key:
      - USUBJID
columns:
  - name: USUBJID
    type: str
    label: Unique Subject Identifier
    derivation: AE.USUBJID
  - name: AESEQ
    type: float
    label: Sequence Number
    derivation: AE.AESEQ
  - name: AEDECOD
    type: str
    label: Dictionary-Derived Term
    derivation: AE.AEDECOD
  - name: AGE
    type: float
    label: Age
    derivation: SBJ.AGE
  - name: TRTEMFL
    type: str
    label: Treatment Emergent Flag
    derivation:
      case:
        - when: "AE.AESTDTC >= '2020-01-05'"
          then: "'Y'"
        - otherwise: "''"
"""

DEFINE = """\
<?xml version="1.0" encoding="UTF-8"?>
<ODM>
  <ItemDef OID="DM.USUBJID" Name="USUBJID" DataType="text"/>
  <ItemDef OID="DM.AGE" Name="AGE" DataType="integer"/>
  <ItemDef OID="DM.ARM" Name="ARM" DataType="text"/>
  <ItemDef OID="AE.USUBJID" Name="USUBJID" DataType="text"/>
  <ItemDef OID="AE.AESEQ" Name="AESEQ" DataType="integer"/>
  <ItemDef OID="AE.AEDECOD" Name="AEDECOD" DataType="text"/>
</ODM>
"""

SAP = """\
# Toy analysis plan

## 1 Populations

Subjects are grouped by age: under 65, 65 or over.
"""

CLAIMS = {
    "schema_version": 2,
    "dataset": "ADSL",
    "claims": [
        {
            "variable": "AGEGR1",
            "rule": "Group age at 65.",
            "citations": [
                {"document": "docs/sap.md", "section": "section 1", "quote": "under 65"},
                {"document": "programs/adsl.sas", "section": "L1-L2", "quote": "if age < 65"},
            ],
        },
        {
            "variable": "NOTBUILT",
            "rule": "A variable the specification does not build.",
            "citations": [{"document": "docs/sap.md", "section": "section 1", "quote": "x"}],
        },
    ],
}

KIT_HEAD = f"""\
# A made-up kit for the tests.
kit: 0
id: toy
title: Toy study of three subjects
tier: {{tier}}
pins:
  engines:
    yamaa: "{{engine}}"
  sources:
    toy: {COMMIT}
build:
  project: gold/spec/project.yaml
  sdtm: inputs/data/sdtm
  reference: gold/reference/adam
  claims: gold/claims
documents:
  - id: sap
    file: inputs/docs/sap.md
    cited_as: [docs/sap.md]
  - id: define-sdtm
    file: inputs/data/sdtm/define.xml
    cited_as: []
trace_gaps: {{gaps}}
"""

# kit path -> path in the source
LAYOUT = {
    "gold/spec/project.yaml": "spec/project.yaml",
    "gold/spec/adsl.yaml": "spec/adsl.yaml",
    "gold/spec/adae.yaml": "spec/adae.yaml",
    "inputs/data/sdtm/dm.parquet": "data/sdtm/dm.parquet",
    "inputs/data/sdtm/ae.parquet": "data/sdtm/ae.parquet",
    "inputs/data/sdtm/define.xml": "define/define-sdtm.xml",
    "inputs/docs/sap.md": "docs/sap.md",
    "gold/reference/adam/adsl.parquet": "data/adam/adsl.parquet",
    "gold/reference/adam/adae.parquet": "data/adam/adae.parquet",
    "gold/claims/adsl-claims.json": "review/adsl-claims.json",
}


# A reporting event on the toy ADaM, with results embedded as a reference would
# have them. The two means of age are exchanged between the age groups, as the
# arms are in the real example (E3); gold/exceptions.yaml classifies them.
ARS_FILE = "gold/spec/ars/event.json"
RESULTS_HEAD = f"""\
results:
  - id: event
    ars: {ARS_FILE}
"""
EXCEPTIONS = """\
exceptions: 0
results:
  event:
    - result: "ard:A_AGE/M_AGE_mean/Old"
      embedded: "50"
      class: reference_error
      proof: {kind: value_of_other_result, result: "ard:A_AGE/M_AGE_mean/Young"}
    - result: "ard:A_AGE/M_AGE_mean/Young"
      embedded: "70"
      class: reference_error
      proof: {kind: value_of_other_result, result: "ard:A_AGE/M_AGE_mean/Old"}
"""


def reporting_event() -> dict:
    def where(dataset, variable, value):
        return {"condition": {"dataset": dataset, "variable": variable, "comparator": "EQ",
                              "value": [value]}}

    def analysis(analysis_id, method, dataset, variable, results, **more):
        return {
            "id": analysis_id, "name": analysis_id, "methodId": method, "dataset": dataset,
            "variable": variable, "analysisSetId": "SAF",
            "reason": {"controlledTerm": "SPECIFIED IN SAP"},
            "purpose": {"controlledTerm": "PRIMARY OUTCOME MEASURE"},
            "orderedGroupings": [{"order": 1, "groupingId": "AGEGR", "resultsByGroup": True}],
            "results": [{"operationId": operation, "rawValue": raw, "resultGroups": [
                {"groupingId": "AGEGR", "groupId": group}]} for operation, group, raw in results],
            **more,
        }

    return {
        "id": "TOY", "name": "Toy reporting event", "version": 1,
        "mainListOfContents": {"name": "contents", "contentsList": {"listItems": []}},
        "analysisSets": [{"id": "SAF", "name": "Safety set", **where("ADSL", "SAFFL", "Y")}],
        "dataSubsets": [{"id": "TEAE", "name": "Emergent", **where("ADAE", "TRTEMFL", "Y")}],
        "analysisGroupings": [{
            "id": "AGEGR", "name": "Age group", "groupingDataset": "ADSL",
            "groupingVariable": "AGEGR1", "dataDriven": False,
            "groups": [{"id": "Young", "name": "Under 65", **where("ADSL", "AGEGR1", "<65")},
                       {"id": "Old", "name": "65 or over", **where("ADSL", "AGEGR1", ">=65")}]}],
        "methods": [
            {"id": "M_N", "name": "Count", "operations": [
                {"id": "M_N_n", "name": "Count of subjects", "order": 1}]},
            {"id": "M_AGE", "name": "Summary", "operations": [
                {"id": "M_AGE_n", "name": "Count of non-missing values", "order": 1},
                {"id": "M_AGE_mean", "name": "Mean", "order": 2, "resultPattern": "XX.X"}]},
        ],
        "analyses": [
            analysis("A_N", "M_N", "ADSL", "USUBJID", [("M_N_n", "Young", "1"),
                                                       ("M_N_n", "Old", "1")]),
            analysis("A_AGE", "M_AGE", "ADSL", "AGE", [
                ("M_AGE_n", "Young", "1"), ("M_AGE_n", "Old", "1"),
                ("M_AGE_mean", "Young", "70"), ("M_AGE_mean", "Old", "50")]),
            analysis("A_TEAE", "M_N", "ADAE", "USUBJID", [("M_N_n", "Young", "1"),
                                                          ("M_N_n", "Old", "1")],
                     dataSubsetId="TEAE"),
        ],
    }


def engine() -> str:
    import yamaa

    return yamaa.__version__


def tables(reference_age: float = 70.0) -> dict[str, object]:
    """The SDTM inputs and the expected ADaM, written by hand.

    The reference stores its text as large_string, as the pilot's does.
    """
    import pyarrow as pa

    def large(values):
        return pa.array(values, pa.large_string())

    day = datetime.date
    return {
        "data/sdtm/dm.parquet": pa.table({
            "USUBJID": ["S1", "S2", "S3"],
            "AGE": [70.0, 50.0, None],
            "ARM": ["Drug", "Placebo", "Screen Failure"],
            "RFSTDTC": ["2020-01-02", "2020-01-10", None],
        }),
        "data/sdtm/ae.parquet": pa.table({
            "USUBJID": ["S2", "S1", "S1"],
            "AESEQ": [1.0, 2.0, 1.0],
            "AEDECOD": ["NAUSEA", "RASH", "HEADACHE"],
            "AESTDTC": ["2020-01-11", "2020-01-08", "2020-01-01"],
        }),
        "data/adam/adsl.parquet": pa.table({
            "STUDYID": large(["TOY", "TOY", "TOY"]),
            "USUBJID": large(["S1", "S2", "S3"]),
            "AGE": [reference_age, 50.0, None],
            "AGEGR1": large([">=65", "<65", ">=65"]),
            "SAFFL": large(["Y", "Y", "N"]),
            "TRTSDT": pa.array([day(2020, 1, 2), day(2020, 1, 10), None], pa.date32()),
        }),
        "data/adam/adae.parquet": pa.table({
            "USUBJID": large(["S1", "S1", "S2"]),
            "AESEQ": [1.0, 2.0, 1.0],
            "AEDECOD": large(["HEADACHE", "RASH", "NAUSEA"]),
            "AGE": [70.0, 70.0, 50.0],
            "TRTEMFL": large(["", "Y", "Y"]),
        }),
    }


def make(
    root: Path, real_root: Path, *, tier: str = "A", engine_version: str | None = None,
    reference_age: float = 70.0, adsl: str = ADSL, adae: str = ADAE, gaps: str = "{}",
    layout: dict[str, str] | None = None, results: bool = False,
    exceptions: str | None = EXCEPTIONS,
) -> Path:
    """Write the toy checkout into `root` and return `root`.

    With `results`, the kit also has the reporting event above, the method
    registry of the real checkout, and (unless `exceptions` is None) its
    gold/exceptions.yaml.
    """
    import pyarrow.parquet as pq

    cache = root / "third_party" / "cache" / "toy"
    texts = {
        "spec/project.yaml": PROJECT, "spec/adsl.yaml": adsl, "spec/adae.yaml": adae,
        "define/define-sdtm.xml": DEFINE, "docs/sap.md": SAP,
        "review/adsl-claims.json": json.dumps(CLAIMS, indent=2) + "\n",
    }
    layout = dict(layout or LAYOUT)
    head = KIT_HEAD
    if results:
        texts["ars/event.json"] = json.dumps(reporting_event(), indent=1) + "\n"
        layout[ARS_FILE] = "ars/event.json"
        head = KIT_HEAD + RESULTS_HEAD
        if exceptions is not None:
            head = head.replace("  claims: gold/claims\n",
                                "  claims: gold/claims\n  exceptions: gold/exceptions.yaml\n")
            own = root / "kits" / "toy" / "gold" / "exceptions.yaml"
            own.parent.mkdir(parents=True, exist_ok=True)
            own.write_text(exceptions, encoding="ascii", newline="\n")
        for folder in ("standard/methods", "tests/methods", "r/specfirstr"):
            shutil.copytree(real_root / folder, root / folder, dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns("__pycache__", "*.py"))
        ard_schema = Path("standard") / "schemas" / "ard.schema.json"
        (root / ard_schema).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(real_root / ard_schema, root / ard_schema)
    for name, text in texts.items():
        (cache / name).parent.mkdir(parents=True, exist_ok=True)
        (cache / name).write_text(text, encoding="ascii", newline="\n")
    for name, table in tables(reference_age).items():
        (cache / name).parent.mkdir(parents=True, exist_ok=True)
        pq.write_table(table, cache / name)
    (root / "PLAN.md").write_text("plan\n", encoding="ascii")
    (root / "third_party" / "sources.yaml").write_text(SOURCES, encoding="ascii")
    schema = Path("standard") / "schemas" / "graph.schema.json"
    (root / schema).parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(real_root / schema, root / schema)
    entries = [
        KitFile(path, "toy", origin, sha256_file(cache / origin))
        for path, origin in layout.items()
    ]
    head = head.format(tier=tier, engine=engine_version or engine(), gaps=gaps)
    manifest = root / "kits" / "toy" / "kit.yaml"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(head + files_block(entries), encoding="ascii", newline="\n")
    return root
