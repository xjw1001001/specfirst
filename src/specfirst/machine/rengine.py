"""Run the R result engine of r/specfirstr/ and read what it wrote.

The locked R library has no Parquet reader, and adding one would change
env/ for every checkout that shares the library (ADR-002). So the data are
handed over: for every dataset, the columns the analyses read, as one JSON
file with one array per column. Numbers are written as the shortest decimal
that reads back as the same double, so nothing is lost, and both sides
prove it: the R engine reports a fingerprint of every column as it read it,
and `fingerprints` computes the same from the data the Python engine uses.

A job file tells the R engine what to read and where to write. It holds
absolute paths, so it is a working file, not a built one.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
import subprocess
from pathlib import Path

from specfirst.machine import ars
from specfirst.machine.ard import Table
from specfirst.machine.canonical import json_text

SEPARATOR = "\x1f"


class REngineError(RuntimeError):
    """The R engine could not be run, or it failed."""


def script(root: Path) -> Path:
    return root / "r" / "specfirstr" / "run.R"


def available() -> bool:
    return shutil.which("Rscript") is not None


def handover_text(table: Table) -> str:
    """One dataset as JSON: {"dataset", "rows", "columns": [{"name", "kind", "values"}]}."""
    columns = []
    for name in sorted(table.columns):
        values = table.columns[name].tolist()
        if table.kinds[name] == "number":
            values = [None if math.isnan(value) else value for value in values]
        else:
            values = [None if value == "" else value for value in values]
        columns.append({"name": name, "kind": table.kinds[name], "values": values})
    return json_text({"dataset": table.name, "rows": table.rows, "columns": columns}) + "\n"


def fingerprints(tables: dict[str, Table]) -> dict[str, str]:
    """SHA-256 of every column's values as text; the R engine computes the same."""
    found = {}
    for table in tables.values():
        for name, values in table.columns.items():
            if table.kinds[name] == "number":
                texts = ["NA" if math.isnan(value) else f"{value:.17g}"
                         for value in values.tolist()]
            else:
                texts = values.tolist()
            found[f"{table.name}.{name}"] = hashlib.sha256(
                SEPARATOR.join(texts).encode("utf-8")).hexdigest()
    return found


def run(root: Path, work: Path, ars_path: Path, registry_json: Path, binding: ars.Binding,
        tables: dict[str, Table], subject_key: str) -> tuple[list[dict], dict, str]:
    """Run the R engine on a job. Returns its rows, what it says about itself, and its output."""
    if not available():
        raise REngineError("Rscript is not installed; the R engine cannot run")
    work.mkdir(parents=True, exist_ok=True)
    data = {}
    for name, table in sorted(tables.items()):
        path = work / f"{name}.json"
        path.write_bytes(handover_text(table).encode("ascii"))
        data[name] = str(path)
    rows_path, meta_path = work / "rows.jsonl", work / "meta.json"
    for stale in (rows_path, meta_path):
        stale.unlink(missing_ok=True)
    job = {
        "ars": str(ars_path), "registry": str(registry_json), "binding": binding.record(),
        "subject_key": subject_key, "data": data, "out": str(rows_path), "meta": str(meta_path),
    }
    job_path = work / "job.json"
    job_path.write_bytes((json_text(job) + "\n").encode("ascii"))
    done = subprocess.run(
        ["Rscript", "--vanilla", str(script(root)), str(job_path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env={**os.environ, "LC_ALL": "C.UTF-8"},
    )
    output = (done.stdout + done.stderr).strip()
    if done.returncode != 0 or not rows_path.is_file() or not meta_path.is_file():
        raise REngineError(f"the R engine exited {done.returncode}: {output}")
    try:
        with open(rows_path, encoding="utf-8") as handle:
            rows = [json.loads(line) for line in handle if line.strip()]
        with open(meta_path, encoding="utf-8") as handle:
            meta = json.load(handle)
    except ValueError as error:
        raise REngineError(f"the R engine wrote a file that is not JSON: {error}") from error
    return rows, meta, output


def data_problems(meta: dict, tables: dict[str, Table]) -> list[str]:
    """Why the R engine did not read the values the Python engine read."""
    ours, theirs = fingerprints(tables), meta.get("columns") or {}
    problems = [f"column {name}: the R engine read other values"
                for name in sorted(set(ours) & set(theirs)) if ours[name] != theirs[name]]
    problems += [f"column {name}: not read by the R engine"
                 for name in sorted(set(ours) - set(theirs))]
    problems += [f"column {name}: read by the R engine only"
                 for name in sorted(set(theirs) - set(ours))]
    return problems


def run_vectors(root: Path, work: Path, files: list[dict]) -> dict[tuple[str, int], dict]:
    """Run method vectors through the R implementations: (method, case index) -> result."""
    if not available():
        raise REngineError("Rscript is not installed; the R implementations cannot run")
    work.mkdir(parents=True, exist_ok=True)
    given, out = work / "vectors.in.json", work / "vectors.out.jsonl"
    given.write_bytes((json_text(files) + "\n").encode("ascii"))
    out.unlink(missing_ok=True)
    done = subprocess.run(
        ["Rscript", "--vanilla", str(script(root)), "--vectors", str(given), str(out)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env={**os.environ, "LC_ALL": "C.UTF-8"},
    )
    if done.returncode != 0 or not out.is_file():
        raise REngineError(f"the R vectors run exited {done.returncode}: "
                           f"{(done.stdout + done.stderr).strip()}")
    with open(out, encoding="utf-8") as handle:
        lines = [json.loads(line) for line in handle if line.strip()]
    return {(line["method"], line["case"]): line["result"] for line in lines}
