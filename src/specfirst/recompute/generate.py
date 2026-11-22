"""Write the recomputation bundle of a kit (issue #29, ADR-021, decisions 2, 7 and 8).

The bundle is what a reviewer runs in their own session:

    README.txt      how to run it
    manifest.json   the reference ADaM files (pinned source, path, SHA-256), the
                    package versions of the locks, the generator's commit
    plan.json       per analysis: its script, its operations, its tolerance, or why
                    it is not covered
    scripts/<event>/<analysis>.py or .R
    ard/<event>.jsonl   the gold ARD rows the scripts are compared with
    adam_csv.py     CSV copies of the reference ADaM for the R scripts (pyarrow only)
    compare.py      the comparison (standard library only)
    run_all.sh      every script, then the comparison

It holds no study data (rule 4): the reviewer fetches the pinned source.
"""

from __future__ import annotations

import json
import re
import shutil
from collections.abc import Callable
from pathlib import Path

from specfirst import __version__
from specfirst import kit as kits
from specfirst.machine.canonical import read_jsonl, sha256_file, write_json
from specfirst.paths import build_dir
from specfirst.recompute import pywrite, rwrite
from specfirst.recompute.common import (
    TOLERANCE,
    TOLERANCE_ITERATIVE,
    Decisions,
    Plan,
)
from specfirst.recompute.reading import Event, NotCovered, decisions_binding

Out = Callable[[str], None]
FILES = Path(__file__).resolve().parent / "bundle"
STANDALONE = ("adam_csv.py", "compare.py")
PYTHON_PACKAGES = ("pandas", "numpy", "scipy", "pyarrow")
R_PACKAGES = ("emmeans", "mmrm", "coin")
ITERATIVE = {"model.mmrm.lsmeans", "model.mmrm.pairwise"}


class GenerateError(ValueError):
    pass


def recompute_dir(root: Path, kit_id: str) -> Path:
    """build/recompute/<kit>: the bundle and the runs of it (ignored, like all of build/)."""
    return build_dir(root) / "recompute" / kit_id


def versions(root: Path) -> dict[str, str]:
    """The package versions the scripts run with, from the lock files."""
    found: dict[str, str] = {}
    text = (root / "env" / "requirements.lock").read_text(encoding="ascii")
    for name in PYTHON_PACKAGES:
        match = re.search(rf"^{name}==([^\s\\]+)", text, re.MULTILINE)
        found[name] = match.group(1) if match else "unknown"
    text = (root / "env" / "r-packages.lock").read_text(encoding="ascii")
    for name in R_PACKAGES:
        match = re.search(rf"^{re.escape(name)} (\S+)", text, re.MULTILINE)
        found[name] = match.group(1) if match else "unknown"
    lines = [line for line in (root / "env" / "r-version.txt").read_text(encoding="ascii")
             .splitlines() if line.strip() and not line.startswith("#")]
    found["R"] = lines[-1].split("-")[0] if lines else "unknown"
    return found


def column_types(adam: Path, datasets: list[str]) -> dict[str, dict[str, str]]:
    """Per dataset and column, `number`, `text` or another kind, from the Parquet schema of
    the reference ADaM (rule I3 compares numbers as numbers)."""
    import pyarrow as pa
    import pyarrow.parquet as pq

    found: dict[str, dict[str, str]] = {}
    for name in datasets:
        schema = pq.read_schema(adam / f"{name.lower()}.parquet")
        kinds = {}
        for item in schema:
            t = item.type
            if pa.types.is_integer(t) or pa.types.is_floating(t) or pa.types.is_decimal(t):
                kinds[item.name] = "number"
            elif pa.types.is_string(t) or pa.types.is_large_string(t):
                kinds[item.name] = "text"
            else:
                kinds[item.name] = str(t)
        found[name.upper()] = kinds
    return found


def reference_files(kit: kits.Kit, folder: Path) -> list[dict]:
    """The reference ADaM files of the kit, each checked against its pinned SHA-256."""
    files = []
    prefix = kit.reference.rstrip("/") + "/"
    for entry in kit.files:
        if not entry.path.startswith(prefix) or not entry.path.endswith(".parquet"):
            continue
        path = folder / entry.path
        if not path.is_file() or sha256_file(path) != entry.sha256:
            raise GenerateError(f"{entry.path}: missing, or not the pinned file")
        files.append({"dataset": Path(entry.path).stem.upper(), "file": Path(entry.path).name,
                      "source": entry.source, "commit": kit.sources.get(entry.source),
                      "from": entry.origin, "sha256": entry.sha256})
    return sorted(files, key=lambda f: f["file"])


# The evidence of PLAN.md section 3 that names tables of the kit's study, and where each
# stands here (ADR-021, decision 2; the owner's answer of 2026-11-21 to Q1). plan.json carries
# them, and compare.py writes them into the report.
EVIDENCE_TABLES = {
    "cdiscpilot01": [
        ("E24", "CSR 14-2.01 (demographics)",
         "not built as a CSR table (real-4); covered in part: its rows of age, age group, sex, "
         "race and height are recomputed by the demographics analyses of CDISC's example "
         "(Out14-1-1), on the safety population and race by another grouping; its ITT "
         "population and its rows of MMSE, duration of disease, education, weight and BMI "
         "are not"),
        ("E25", "CSR 14-5.01 (adverse events by organ class and term)",
         "not built as a CSR table (real-4); its content is recomputed by the analyses of "
         "CDISC's example Out14-3-2-1, on ADAE (AESOC, equal to AEBODSYS on every record)"),
        ("E26", "CSR 14-6.06 (Hy's law shifts, CMH)",
         "not built: no ARS analysis in the kit (real-5); its method, test.cmh, is recomputed "
         "for CSR 14-3.13"),
    ],
}


def generate(root: Path, kit_id: str, build: Path, dest: Path, commit: str = "unknown",
             clean: bool | None = None, out: Out = print) -> dict:
    """Write the bundle of the kit built in `build` into `dest`. Returns plan.json."""
    kit = kits.load_kit(root, kit_id)
    if not kit.results:
        raise GenerateError(f"kit {kit_id} has no reporting event")
    registry = json.loads((root / "standard" / "methods" / "registry.json")
                          .read_text(encoding="ascii"))["methods"]
    adam = build / kit.reference
    references = reference_files(kit, build)
    types_of = column_types(adam, [f["dataset"] for f in references])

    def types(dataset: str, column: str) -> str:
        return types_of.get(dataset.upper(), {}).get(column, "absent")

    records: list[dict] = []
    if kit.decisions:
        records = read_jsonl(build / kit.decisions) if (build / kit.decisions).is_file() \
            else read_jsonl(root / "kits" / kit_id / kit.decisions)
    by_element = decisions_binding(records)
    found = versions(root)
    if dest.exists():
        shutil.rmtree(dest)
    (dest / "scripts").mkdir(parents=True)
    plans: list[dict] = []
    for spec in kit.results:
        data = json.loads((build / spec.ars).read_text(encoding="utf-8"))
        event = Event(data, spec.id, registry, spec.binding)
        if not (build / "gold" / "ard" / f"{spec.id}.jsonl").is_file():
            raise GenerateError(f"{build}: no gold ARD of {spec.id}; build the kit first")
        (dest / "ard").mkdir(exist_ok=True)
        shutil.copyfile(build / "gold" / "ard" / f"{spec.id}.jsonl",
                        dest / "ard" / f"{spec.id}.jsonl")
        for analysis_id in event.analyses:
            try:
                plan = write_script(event, analysis_id, kit_id, registry,
                                    Decisions(by_element=by_element), types,
                                    spec.subject_key, found, dest)
                plans.append(plan.record())
            except NotCovered as error:
                plans.append({"analysis": analysis_id, "event": spec.id,
                              "not_covered": str(error)})
    plan = {"kit": kit_id, "analyses": plans,
            "evidence": [{"evidence": e, "table": t, "where": w}
                         for e, t, w in EVIDENCE_TABLES.get(kit_id, [])]}
    write_json(dest / "plan.json", plan)
    manifest = {
        "kit": kit_id, "reference_adam": references,
        "packages": {"python": {p: found[p] for p in PYTHON_PACKAGES},
                     "r": {"R": found["R"], **{p: found[p] for p in R_PACKAGES}}},
        "generator": {"specfirst": __version__, "commit": commit, "clean": clean},
    }
    write_json(dest / "manifest.json", manifest)
    for name in STANDALONE:
        shutil.copyfile(FILES / name, dest / name)
    write_text(dest / "run_all.sh", run_all(plans))
    write_text(dest / "README.txt", readme(kit, plans, references))
    covered = sum(1 for p in plans if "not_covered" not in p)
    out(f"recompute {kit_id}: {covered} scripts of {len(plans)} analyses written to {dest}")
    return plan


def write_script(event: Event, analysis_id: str, kit_id: str, registry: dict,
                 decisions: Decisions, types: Callable[[str, str], str], key: str,
                 found: dict[str, str], dest: Path) -> Plan:
    analysis = event.analysis(analysis_id)
    methods = tuple(analysis.methods)
    if methods in pywrite.DESCRIPTIVE or methods in pywrite.TESTS:
        writer = pywrite.PyWriter(analysis, kit_id, registry, decisions, types, key, found,
                                  event.analysis)
        language, suffix = "python", "py"
    else:
        writer = rwrite.RWriter(analysis, kit_id, registry, decisions, types, key, found)
        language, suffix = "r", "R"
    text, template = writer.write()
    relative = f"scripts/{event.id}/{analysis_id}.{suffix}"
    write_text(dest / relative, text)
    tolerance = TOLERANCE_ITERATIVE if set(methods) & ITERATIVE else TOLERANCE
    return Plan(analysis=analysis_id, event=event.id, language=language, template=template,
                file=relative, datasets=sorted(d.lower() for d in writer.datasets),
                operations={op.id: {"method": op.method, "operation": op.operation,
                                    "result": op.result} for op in analysis.operations},
                groupings=[g.id for g in analysis.groupings], tolerance=tolerance,
                numbers=sorted(analysis.numbers))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("ascii"))


def run_all(plans: list[dict]) -> str:
    covered = [p for p in plans if "not_covered" not in p]
    csv = sorted({d for p in covered if p["language"] == "r" for d in p["datasets"]})
    lines = [
        "#!/bin/sh",
        "# Run every recomputation script of this bundle, then compare their results with the",
        "# ARD rows in ard/ (issue #29). From the folder of this file:",
        "#   sh run_all.sh <folder of the reference ADaM as Parquet> <work folder>",
        "# PYTHON and RSCRIPT name the interpreters (default python3 and Rscript).",
        "set -eu",
        "adam=\"$1\"; work=\"$2\"",
        "py=\"${PYTHON:-python3}\"; rs=\"${RSCRIPT:-Rscript}\"",
        f"\"$py\" adam_csv.py \"$adam\" \"$work/csv\" {' '.join(csv)}",
    ]
    for event in sorted({p["event"] for p in covered}):
        lines.append(f"mkdir -p \"$work/out/{event}\"")
    for p in covered:
        target = f"\"$work/out/{p['event']}/{p['analysis']}.csv\""
        if p["language"] == "python":
            lines.append(f"\"$py\" {p['file']} \"$adam\" {target}")
        else:
            lines.append(f"\"$rs\" --vanilla {p['file']} \"$work/csv\" {target}")
    lines.append("\"$py\" compare.py . \"$work/out\" ard \"$work/report.json\"")
    return "\n".join(lines) + "\n"


def readme(kit: kits.Kit, plans: list[dict], references: list[dict]) -> str:
    covered = [p for p in plans if "not_covered" not in p]
    sources = sorted({(f["source"], f["commit"]) for f in references})
    lines = [
        f"Recomputation scripts of the kit {kit.id} (specfirst, issue #29, ADR-021)",
        "",
        f"One script per analysis: {len(covered)} of {len(plans)} analyses. Each reads the "
        "reference",
        "ADaM, applies the analysis set, the data subset and the groupings of its ARS analysis,",
        "and computes the statistic with standard packages; above each step stands the",
        "decision it follows. No script imports, sources or reads any part of specfirst;",
        "each reads only the ADaM datasets its plan names, from the folder it is given.",
        "",
        "This folder holds no study data. Fetch the reference ADaM at its pin:",
    ]
    for source, commit in sources:
        lines.append(f"  source {source} at commit {commit}")
    lines += ["and check each file against manifest.json (path 'from', SHA-256).", "",
              "Run (Python with pandas, numpy, scipy and pyarrow; R with emmeans, mmrm and coin,",
              "at the versions manifest.json lists):",
              "  sh run_all.sh <folder of the reference ADaM> <work folder>",
              "or one script: python scripts/<event>/<analysis>.py <ADaM folder> <out.csv>,",
              "Rscript scripts/<event>/<analysis>.R <folder of adam_csv.py's CSV copies>",
              "<out.csv>.",
              "",
              "compare.py compares every output with ard/<event>.jsonl at full precision: the",
              "same rows; counts exactly; other values within the relative tolerance plan.json",
              "gives (1e-9; 1e-6 for the mixed model). It writes one line per analysis:",
              "reproduced, differs (with the rows) or not covered (with the reason)."]
    evidence = EVIDENCE_TABLES.get(kit.id, [])
    if evidence:
        lines += ["", "Tables of the study's CSR named by the plan's evidence, and where each "
                  "stands:"]
        lines += [f"  {e} {t}: {w}" for e, t, w in evidence]
    return "\n".join(lines) + "\n"


def export(bundle: Path, target: Path) -> Path:
    """Copy the bundle to `target`/recompute-<kit>."""
    plan = json.loads((bundle / "plan.json").read_text(encoding="ascii"))
    dest = target / f"recompute-{plan['kit']}"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(bundle, dest)
    return dest


def bundle_hashes(bundle: Path) -> dict[str, str]:
    return {p.relative_to(bundle).as_posix(): sha256_file(p)
            for p in sorted(bundle.rglob("*")) if p.is_file()}
