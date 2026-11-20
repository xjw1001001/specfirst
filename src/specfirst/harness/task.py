"""The task folder of a reading task (PLAN.md section 11.1; ADR-005, decision 2;
docs/decisions/ADR-010.md, decision 2).

    <task>/
      TASK.md                    what to do, the files, the formats, the tools
      inputs/docs/               protocol.md, sap.md: the natural form of the kit
      inputs/house/              the house standard of the kit
      inputs/data/sdtm/          stage C: the visible SDTM of the kit
      inputs/data/adam/          stage T only: the ADaM of gold on the visible data
      standard/catalog/          catalog.yaml and entries/
      standard/methods/registry.json, standard/schemas/decision-record.schema.json
      knowledge/core-reader/SKILL.md, knowledge/<unit>/SKILL.md (condition `notes`)
      bin/ask, bin/check         written by the run (specfirst.harness.runs), not here
      out/                       what the reader writes

A task is a pure function of the kit, the stage, the condition, the catalog
and the skills of the checkout (rule R4). Its ID is a prefix of the SHA-256
of its manifest: the SHA-256 of every file but those of bin/ and out/. It
names no kit, seed or split; the data and the documents name the study.

`problems` holds a task folder against the allow list and against the
files of the kit that a reader must not see (section 11.2).

A real study (tier C) gives its task through a folder of the same shape
(specfirst.harness.pilot): stage T only, the documents it has as text taken
from their PDF, anchored by page and paragraph (`render_real`).
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from specfirst.compile import catalog as catalogs
from specfirst.compile.catalog import Catalog
from specfirst.gen import gold as kitgold
from specfirst.gen import kits as genkits
from specfirst.machine.canonical import content_hash, sha256_file

STAGES = ("C", "T")
CONDITIONS = ("catalog", "notes")
TASK_FILE = "TASK.md"
OUT = "out"
BIN = "bin"
OUTPUTS = ("decisions.jsonl", "questions.jsonl", "unmapped.jsonl")
CORE = "core-reader"
SKILLS = "skills"
KNOWLEDGE = "knowledge"
# The documents a reader cites, by ID: the natural form and the house standard.
DOCUMENTS = {"protocol": "inputs/docs/protocol.md", "sap": "inputs/docs/sap.md",
             "house": "inputs/house/STANDARD.md"}
SDTM = "inputs/data/sdtm"
ADAM = "inputs/data/adam"
STANDARD = ("standard/catalog/catalog.yaml", "standard/methods/registry.json",
            "standard/schemas/decision-record.schema.json")
ENTRIES = "standard/catalog/entries"
# What a task folder may hold, by path prefix (bin/ and out/ are the run's).
ALLOWED = (TASK_FILE, "inputs/docs/", "inputs/house/", f"{SDTM}/", f"{ADAM}/",
           *STANDARD, f"{ENTRIES}/", f"{KNOWLEDGE}/", f"{BIN}/", f"{OUT}/")
EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
# A real study (PLAN.md section 6.1, tier C): its documents are text taken from a PDF, its
# anchors are page and paragraph, and its task is stage T (specfirst.harness.pilot).
REAL_TIER = "C"
REAL_ANCHORS = ("12/p3", "14/p2")  # the anchors of the examples of TASK.md


class TaskError(RuntimeError):
    """A task folder cannot be written here, or from this kit."""


@dataclass(frozen=True)
class Task:
    folder: Path
    id: str
    stage: str
    condition: str
    units: tuple[str, ...]
    keys: tuple[tuple[str, str], ...]  # (entry, unit): the decisions to make
    manifest: dict[str, str]  # path -> SHA-256, every file but bin/ and out/

    @property
    def knowledge(self) -> list[str]:
        return sorted(path for path in self.manifest if path.startswith(f"{KNOWLEDGE}/"))


def scope(catalog: Catalog, units: tuple[str, ...], stage: str) -> tuple[str, ...]:
    """The units a task scores: the units of the kit in stage C, its table families in T."""
    if stage not in STAGES:
        raise TaskError(f"a stage is one of {', '.join(STAGES)}, not '{stage}'")
    if stage == "C":
        return tuple(units)
    return tuple(unit for unit in units if catalog.units[unit].kind == "table_family")


def keys_of(catalog: Catalog, units: tuple[str, ...]) -> tuple[tuple[str, str], ...]:
    """Every catalog question of the units, in catalog order, as (entry, unit)."""
    return tuple((entry.id, unit) for unit in units for entry in catalog.entries.values()
                 if unit in entry.units)


def inside_checkout(path: Path) -> Path | None:
    """The checkout a path lies in (a folder with PLAN.md or .git), or None."""
    path = path.resolve()
    for folder in (path, *path.parents):
        if (folder / "PLAN.md").is_file() or (folder / ".git").exists():
            return folder
    return None


def manifest(folder: Path) -> dict[str, str]:
    """SHA-256 of every file of a task folder but those of bin/ and out/, by path."""
    found = {}
    for path in sorted(folder.rglob("*")):
        relative = path.relative_to(folder).as_posix()
        if path.is_file() and not relative.startswith((f"{BIN}/", f"{OUT}/")):
            found[relative] = sha256_file(path)
    return found


def task_id(found: dict[str, str]) -> str:
    return f"task-{content_hash(found)[:12]}"


def skill_path(root: Path, name: str) -> Path:
    return root / SKILLS / name / "SKILL.md"


def _copy(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


def _copy_tree(source: Path, target: Path) -> None:
    for path in sorted(source.rglob("*")):
        if path.is_file():
            _copy(path, target / path.relative_to(source))


def build(root: Path, kit_dir: Path, tasks_dir: Path, stage: str = "C",
          condition: str = "notes") -> Task:
    """Write the task folder of a kit into `tasks_dir`, as `tasks_dir/<task ID>`.

    A folder of that ID is written again. `tasks_dir` must lie outside every
    checkout (section 11.2).
    """
    if condition not in CONDITIONS:
        raise TaskError(f"a condition is one of {', '.join(CONDITIONS)}, not '{condition}'")
    home = inside_checkout(tasks_dir)
    if home is not None:
        raise TaskError(f"{tasks_dir} lies inside the checkout {home}: a task folder lies "
                        "outside every checkout (PLAN.md section 11.2)")
    catalog = catalogs.load(catalogs.default_dir(root))
    kit_manifest = genkits.read_manifest(kit_dir)
    units = scope(catalog, tuple(kit_manifest["units"]), stage)
    keys = keys_of(catalog, units)
    real = kit_manifest.get("tier") == REAL_TIER
    docs = tuple(doc for doc in ("protocol", "sap") if (kit_dir / DOCUMENTS[doc]).is_file())
    if not real and docs != ("protocol", "sap"):
        raise TaskError(f"the kit {kit_dir} lacks a document: a generated kit has the natural "
                        "protocol and SAP")
    if real and (not docs or stage != "T"):
        raise TaskError("a task of a real study has stage T and at least one document "
                        "(ADR-005, decision 5)")
    tasks_dir.mkdir(parents=True, exist_ok=True)
    staging = tasks_dir / ".building"
    shutil.rmtree(staging, ignore_errors=True)
    staging.mkdir()
    for doc in docs:
        _copy(kit_dir / DOCUMENTS[doc], staging / DOCUMENTS[doc])
    _copy_tree(kit_dir / kitgold.HOUSE, staging / kitgold.HOUSE)
    if stage == "C":
        _copy_tree(kit_dir / SDTM, staging / SDTM)
    else:
        # Stage T: the ADaM of gold on the visible data, an exception to section 11.2
        # for this stage only (ADR-005, decision 2).
        for path in sorted((kit_dir / "gold" / "data" / "adam").glob("*.parquet")):
            _copy(path, staging / ADAM / path.name)
    for relative in STANDARD:
        _copy(root / relative, staging / relative)
    for path in sorted((root / ENTRIES).glob("*.yaml")):
        _copy(path, staging / ENTRIES / path.name)
    skills = [CORE] + (list(units) if condition == "notes" else [])
    for name in skills:
        source = skill_path(root, name)
        if not source.is_file():
            raise TaskError(f"no skill {source.relative_to(root)}: write it first "
                            "(`specfirst run skills --write`)")
        _copy(source, staging / KNOWLEDGE / name / "SKILL.md")
    knowledge = [f"{KNOWLEDGE}/{name}/SKILL.md" for name in skills]
    text = (render_real(catalog, units, keys, docs, knowledge) if real
            else render(catalog, units, keys, stage, knowledge))
    (staging / TASK_FILE).write_text(text, encoding="ascii", newline="\n")
    (staging / OUT).mkdir()
    found = manifest(staging)
    ident = task_id(found)
    folder = tasks_dir / ident
    shutil.rmtree(folder, ignore_errors=True)
    staging.rename(folder)
    return Task(folder, ident, stage, condition, units, keys, found)


def render(catalog: Catalog, units: tuple[str, ...], keys: tuple[tuple[str, str], ...],
           stage: str, knowledge: list[str]) -> str:
    """TASK.md: the task, in words. It names the files present, never a kit."""
    data = (f"- `{SDTM}/`: the visible SDTM data of the study: one Dataset-JSON file per\n"
            "  domain (one record per line), the same tables as Parquet, and define.xml.\n"
            "  The decisions are in the documents; look at the data only when a document\n"
            "  sends you there."
            if stage == "C" else
            f"- `{ADAM}/`: the analysis datasets ADSL and ADAE of the study (Parquet),\n"
            "  already built. Only the table decisions are asked here.")
    lines = [
        "# Reading task",
        "",
        "You read the protocol and the statistical analysis plan of one clinical study and",
        "record, for every catalog question listed below, the decision the study makes. You",
        "write three files in `out/`. Work only inside this folder.",
        "",
        "## The files",
        "",
        "- `inputs/docs/protocol.md` (document ID `protocol`) and `inputs/docs/sap.md`",
        "  (document ID `sap`): the documents of the study. Every paragraph starts with its",
        "  anchor in brackets, for example `[4.1/p2]`.",
        "- `inputs/house/STANDARD.md` (document ID `house`): the house standard. Each of its",
        "  numbered statements, for example `[1/s3]`, is the default that holds when the",
        "  documents do not state the decision. The other files of `inputs/house/` are the",
        "  templates the house builds with.",
        data,
        "- `standard/catalog/catalog.yaml` and `standard/catalog/entries/<id>.yaml`: the",
        "  decision catalog. Each entry is a question with its alternatives; each",
        "  alternative has an ID (`rule`), a statement template and typed slots.",
        "- `standard/schemas/decision-record.schema.json`: the format of a decision record.",
        "- `standard/methods/registry.json`: the statistical methods the standard knows.",
        "",
        "Read these files first, in this order:",
        "",
        *[f"- `{path}`" for path in knowledge],
        "",
        "## The decisions to make",
        "",
        "One record per line below, for the unit named. An entry that is answered once per",
        "table family (its entry file lists `units`) is answered for the unit named here.",
        "",
        "| Entry | Unit |",
        "| --- | --- |",
        *[f"| `{entry}` | `{unit}` |" for entry, unit in keys],
        "",
        "A question that does not apply to this study (the study has nothing it asks about)",
        "gets no record.",
        "",
        "## out/decisions.jsonl",
        "",
        "One JSON object per line, one per decision:",
        "",
        "```json",
        '{"id": "<entry>", "unit": "<unit>", "value": {"rule": "<alternative>", '
        '"<slot>": <value>}, "status": "stated", "class": "document_rule", '
        '"statement": "<the statement template, its slots filled>", "citations": '
        '[{"doc": "sap", "anchor": "4.1/p2", "quote": "<words copied from that paragraph>"}]}',
        "```",
        "",
        "- `stated`, class `document_rule`: a document states the decision. Cite the",
        "  paragraph (`doc`, `anchor`, and a `quote` copied exactly from it).",
        "- `default`, class `house_default`: no document states it and the house standard",
        "  has a default. Cite the statement of the house standard (`doc` `house`).",
        "- `asked`, class `study_input`: no document states it and the house standard has",
        "  no default. Ask (below) and record the answer as the value; no citation.",
        "- `value` holds the alternative's ID as `rule` and every slot of that alternative.",
        "- Do not write `binds` or `identifiable`: the machine fills them.",
        "",
        "## Asking: bin/ask",
        "",
        "```",
        'bin/ask "<your question>" --decision <entry> --unit <unit>',
        "```",
        "",
        "The answer comes from a person who knows the study. Ask only about a decision that",
        "no document states and that the house standard has no default for. Every question",
        "is recorded in `out/questions.jsonl`; do not edit that file.",
        "",
        "## out/unmapped.jsonl",
        "",
        "One JSON object per line for a paragraph that states an analysis convention that",
        "no catalog entry asks about:",
        "",
        "```json",
        '{"doc": "sap", "anchor": "5/p1", "quote": "<words copied from it>", '
        '"note": "<what it decides>"}',
        "```",
        "",
        "The file may be empty, but write it.",
        "",
        "## Check before you finish",
        "",
        "```",
        "bin/check",
        "```",
        "",
        "It reads `out/` and prints every problem it finds. Fix them and run it again. When",
        "it prints no problem, reply with the single word: done.",
        "",
    ]
    return "\n".join(lines)


def render_real(catalog: Catalog, units: tuple[str, ...], keys: tuple[tuple[str, str], ...],
                docs: tuple[str, ...], knowledge: list[str]) -> str:
    """TASK.md of a real study (tier C, stage T; specfirst.harness.pilot): its documents
    are text taken from their PDF, with an anchor of page and paragraph before every
    paragraph. Everything else is the text of `render` at stage T."""
    text = render(catalog, units, keys, "T", knowledge)
    names = {"protocol": "the protocol", "sap": "the statistical analysis plan"}
    files = " and ".join(f"`{DOCUMENTS[doc]}` (document ID `{doc}`)" for doc in docs)
    missing = [names[doc].removeprefix("the ") for doc in ("protocol", "sap") if doc not in docs]
    swaps = [
        ("You read the protocol and the statistical analysis plan of one clinical study and\n",
         f"You read {' and '.join(names[doc] for doc in docs)} of one clinical study and\n"),
        ("- `inputs/docs/protocol.md` (document ID `protocol`) and `inputs/docs/sap.md`\n"
         "  (document ID `sap`): the documents of the study. Every paragraph starts with its\n"
         "  anchor in brackets, for example `[4.1/p2]`.\n",
         _wrap(f"- {files}: {' and '.join(names[doc] for doc in docs)} of the study, as text "
               "taken from the PDF. Every paragraph starts with its anchor in brackets: the "
               "page of the PDF and the number of the paragraph on that page, for example "
               f"`[{REAL_ANCHORS[0]}]`."
               + (f" The {' and the '.join(missing)} is not given." if missing else ""))),
        ('"anchor": "4.1/p2"', f'"anchor": "{REAL_ANCHORS[0]}"'),
        ('"anchor": "5/p1"', f'"anchor": "{REAL_ANCHORS[1]}"'),
    ]
    for old, new in swaps:
        if text.count(old) != 1:
            raise TaskError(f"TASK.md of a real study: the text of a kit task changed ({old!r})")
        text = text.replace(old, new)
    return text


def _wrap(text: str, width: int = 86) -> str:
    """A bullet of TASK.md, its lines at most `width` characters, the rest indented."""
    lines, line = [], ""
    for word in text.split():
        if line and len(line) + 1 + len(word) > width:
            lines.append(line)
            line = "  " + word
        else:
            line = f"{line} {word}" if line else word
    lines.append(line)
    return "\n".join(lines) + "\n"


def protected_hashes(kit_dir: Path) -> dict[str, str]:
    """The SHA-256 of every file of the kit outside inputs/, by SHA-256: the path. A file
    that has the bytes of an input (the trial design tables of the twin) is no secret."""
    files = genkits.read_manifest(kit_dir).get("files") or {}
    inputs = {sha for path, sha in files.items() if str(path).startswith("inputs/")}
    found = {sha: path for path, sha in sorted(files.items())
             if not str(path).startswith("inputs/") and sha not in inputs
             and sha != EMPTY_SHA256}
    found.setdefault(sha256_file(kit_dir / genkits.MANIFEST), genkits.MANIFEST)
    return found


def problems(folder: Path, kit_dir: Path) -> list[str]:
    """Why a task folder is not one a reader may get: a path outside the allow list, or
    a file of the kit that is not an input (stage T may hold the ADaM of gold on the
    visible data, ADR-005, decision 2)."""
    found = []
    protected = protected_hashes(kit_dir)
    allowed_adam = {sha for sha, path in protected.items()
                    if path.startswith("gold/data/adam/")}
    for path in sorted(folder.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(folder).as_posix()
        if not relative.startswith(ALLOWED):
            found.append(f"{relative}: not a file a task holds")
            continue
        sha = sha256_file(path)
        if sha in protected and not (relative.startswith(f"{ADAM}/") and sha in allowed_adam):
            found.append(f"{relative}: the file {protected[sha]} of the kit")
    return found
