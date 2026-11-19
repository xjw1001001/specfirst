"""Whether the output files of a run are valid (docs/decisions/ADR-010.md, decision 6).

    out/decisions.jsonl   every line a decision record of schema v0; one of the
                          decisions the task asks for; a value the standard form
                          renders for that entry and unit; no `binds` and no
                          `identifiable` (the compiler and the machine fill them,
                          PLAN.md section 4.3); every citation names a document the
                          run may cite and an anchor that stands in it; one record per
                          decision
    out/questions.jsonl   every line names a catalog entry and a question; the ask
                          log of the run, line for line
    out/unmapped.jsonl    every line names a document the run may cite and an anchor
                          that stands in it

All three files exist; each may be empty. Whether a quote stands inside its
anchor, and whether a value is right, is the reading score's to say, not
this module's. `bin/check` prints these problems to the reader.
"""

from __future__ import annotations

import json
from pathlib import Path

from specfirst import schemas
from specfirst.compile.catalog import Catalog
from specfirst.compile.standard_form import StandardForm, StandardFormError
from specfirst.harness import task as tasks
from specfirst.score.reading import Documents

MACHINE_FIELDS = ("binds", "identifiable")


def _lines(path: Path, name: str, found: list[str]) -> list[tuple[int, dict]]:
    if not path.is_file():
        found.append(f"{name}: missing")
        return []
    try:
        text = path.read_bytes().decode("utf-8")
    except UnicodeDecodeError as error:
        found.append(f"{name}: not UTF-8 ({error.reason})")
        return []
    records = []
    for number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            found.append(f"{name}:{number}: not JSON ({error.msg})")
            continue
        if not isinstance(record, dict):
            found.append(f"{name}:{number}: not a JSON object")
            continue
        records.append((number, record))
    return records


def _cites(where: str, doc: object, anchor: object, documents: Documents) -> list[str]:
    if doc not in documents.texts:
        return [f"{where}: cites the document '{doc}'; a run cites "
                + ", ".join(sorted(documents.texts))]
    if not isinstance(anchor, str) or documents.span(str(doc), anchor) is None:
        return [f"{where}: the document '{doc}' has no anchor '{anchor}'"]
    return []


def decision_problems(records: list[tuple[int, dict]], catalog: Catalog,
                      keys: tuple[tuple[str, str], ...], documents: Documents) -> list[str]:
    form = StandardForm(catalog)
    wanted = set(keys)
    seen: set[tuple[str, str]] = set()
    found = []
    for number, record in records:
        where = f"decisions.jsonl:{number}"
        found += [f"{where}: {problem}" for problem in schemas.problems("decision-record",
                                                                       record)]
        key = (str(record.get("id")), str(record.get("unit")))
        if key not in wanted:
            found.append(f"{where}: {key[0]} ({key[1]}) is not a decision this task asks for")
        elif key in seen:
            found.append(f"{where}: a second record of {key[0]} ({key[1]})")
        seen.add(key)
        for field in MACHINE_FIELDS:
            if field in record:
                found.append(f"{where}: `{field}` is filled by the machine, not the reader")
        value = record.get("value")
        if key in wanted and value is not None:
            try:
                form.render(key[0], key[1], value)
            except (StandardFormError, KeyError, TypeError, ValueError) as error:
                found.append(f"{where}: the value is not one of {key[0]}: {error}")
        for index, citation in enumerate(record.get("citations") or []):
            if isinstance(citation, dict):
                found += _cites(f"{where}: citation {index + 1}", citation.get("doc"),
                                citation.get("anchor"), documents)
    return found


def question_problems(records: list[tuple[int, dict]], catalog: Catalog,
                      asks: list[dict] | None) -> list[str]:
    found = []
    for number, record in records:
        where = f"questions.jsonl:{number}"
        if record.get("decision") not in catalog.entries:
            found.append(f"{where}: the catalog has no entry '{record.get('decision')}'")
        if not isinstance(record.get("question"), str) or not record["question"].strip():
            found.append(f"{where}: no question")
    if asks is not None:
        given = [(r.get("decision"), r.get("unit"), r.get("question")) for _, r in records]
        logged = [(a.get("decision"), a.get("unit"), a.get("question")) for a in asks]
        if given != logged:
            found.append(f"questions.jsonl: {len(given)} lines, the ask log of the run has "
                         f"{len(logged)}; they must be the same questions in the same order")
    return found


def unmapped_problems(records: list[tuple[int, dict]], documents: Documents) -> list[str]:
    found = []
    for number, record in records:
        found += _cites(f"unmapped.jsonl:{number}", record.get("doc"), record.get("anchor"),
                        documents)
    return found


def problems(out_dir: Path, catalog: Catalog, keys: tuple[tuple[str, str], ...],
             documents: Documents, asks: list[dict] | None = None) -> list[str]:
    """Why the files of `out_dir` are not valid output files of the task."""
    found: list[str] = []
    decisions = _lines(out_dir / "decisions.jsonl", "decisions.jsonl", found)
    questions = _lines(out_dir / "questions.jsonl", "questions.jsonl", found)
    unmapped = _lines(out_dir / "unmapped.jsonl", "unmapped.jsonl", found)
    found += decision_problems(decisions, catalog, keys, documents)
    found += question_problems(questions, catalog, asks)
    found += unmapped_problems(unmapped, documents)
    return found


def task_documents(task_dir: Path) -> Documents:
    """The documents a reader cites, from a task folder."""
    return Documents({doc: (task_dir / path).read_text(encoding="ascii")
                      for doc, path in tasks.DOCUMENTS.items()})


def read(out_dir: Path, name: str) -> list[dict]:
    """The records of an output file (an empty list when it is missing)."""
    found: list[str] = []
    return [record for _, record in _lines(out_dir / name, name, found)]
