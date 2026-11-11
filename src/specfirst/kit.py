"""Kits (PLAN.md section 8): one study, with inputs and gold kept apart.

A kit folder in the repository holds a manifest, kit.yaml, and no study data
or documents (rule 4 of section 2.1, E20). The manifest names every file of
the kit by pinned source, path and SHA-256. `assemble` copies those files
from the fetch cache into build/kits/<id>/ and refuses any file whose hash
is not the pinned one (rule R3: every replay checks for drift first).

What the machine builds (resolved specs, ADaM, graph) is written next to the
assembled files by specfirst.machine.build and is not listed here.
"""

from __future__ import annotations

import json
import re
import shutil
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import yaml

from specfirst import sources as pinned
from specfirst.machine.canonical import sha256_file
from specfirst.paths import build_dir, cache_dir

FORMAT = 0
TIERS = ("A", "B", "C")
# The parts of an assembled kit that only the manifest may fill.
PINNED_AREAS = ("inputs", "gold/spec", "gold/reference", "gold/claims")

_ID = re.compile(r"^[a-z0-9][a-z0-9-]*$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_COMMIT = re.compile(r"^[0-9a-f]{40}$")
_PLAIN = re.compile(r"^[A-Za-z0-9_./-]+$")


class KitError(ValueError):
    """The kit manifest is not usable."""


@dataclass(frozen=True)
class KitFile:
    path: str  # in the kit, with forward slashes
    source: str  # a source of third_party/sources.yaml
    origin: str  # path in that source ("from" in the manifest)
    sha256: str


@dataclass(frozen=True)
class Document:
    id: str  # the <id> of doc:<id>#<anchor>
    file: str
    cited_as: tuple[str, ...]  # the names other projects use for it in their citations


@dataclass(frozen=True)
class Kit:
    id: str
    title: str
    tier: str
    engines: dict[str, str]
    sources: dict[str, str]  # source name -> commit
    project: str  # the yamaa project file
    sdtm: str  # folder of the SDTM datasets
    reference: str  # folder of the reference ADaM datasets
    claims: str | None  # folder of imported claims files, if any
    documents: tuple[Document, ...]
    files: tuple[KitFile, ...]
    trace_gaps: dict[str, str]  # ADaM column ID -> why it has no complete trace

    def paths(self) -> set[str]:
        return {entry.path for entry in self.files}

    def document(self, cited_as: str) -> Document | None:
        for document in self.documents:
            if cited_as == document.file or cited_as in document.cited_as:
                return document
        return None


def _relative(path: object) -> bool:
    return (
        isinstance(path, str)
        and bool(path)
        and not path.startswith("/")
        and "\\" not in path
        and all(part not in ("", ".", "..") for part in path.split("/"))
    )


def parse_kit(data: object) -> Kit:
    """Read a manifest. Every problem is reported at once."""
    if not isinstance(data, dict):
        raise KitError("kit.yaml: expected a mapping")
    problems: list[str] = []

    def text(mapping: dict, key: str, where: str) -> str:
        value = mapping.get(key)
        if not isinstance(value, str) or not value.strip():
            problems.append(f"{where}: '{key}' is missing or empty")
            return ""
        return value.strip()

    if data.get("kit") != FORMAT:
        problems.append(f"kit: this code reads manifest format {FORMAT}")
    kit_id = text(data, "id", "kit.yaml")
    if kit_id and not _ID.match(kit_id):
        problems.append(f"id: must match {_ID.pattern}")
    title = text(data, "title", "kit.yaml")
    tier = text(data, "tier", "kit.yaml")
    if tier and tier not in TIERS:
        problems.append(f"tier: must be one of {', '.join(TIERS)} (PLAN.md section 6.1)")

    pins = data.get("pins") if isinstance(data.get("pins"), dict) else {}
    engines = pins.get("engines") if isinstance(pins.get("engines"), dict) else {}
    commits = pins.get("sources") if isinstance(pins.get("sources"), dict) else {}
    if not engines or not all(isinstance(v, str) and v for v in engines.values()):
        problems.append("pins.engines: name each engine with its version as text")
    if not commits:
        problems.append("pins.sources: name each source with its commit")
    for name, commit in commits.items():
        if not isinstance(commit, str) or not _COMMIT.match(commit):
            problems.append(f"pins.sources.{name}: must be 40 lower-case hex digits")

    build = data.get("build") if isinstance(data.get("build"), dict) else {}
    project = text(build, "project", "build")
    sdtm = text(build, "sdtm", "build")
    reference = text(build, "reference", "build")
    claims = build.get("claims")
    if claims is not None and not isinstance(claims, str):
        problems.append("build.claims: must be a folder or left out")
        claims = None

    files: list[KitFile] = []
    seen: set[str] = set()
    for i, entry in enumerate(data.get("files") or []):
        where = f"files[{i}]"
        if not isinstance(entry, dict):
            problems.append(f"{where}: expected a mapping")
            continue
        path = text(entry, "path", where)
        where = f"file '{path}'" if path else where
        source = text(entry, "source", where)
        origin = text(entry, "from", where)
        sha256 = text(entry, "sha256", where)
        if path and not _relative(path):
            problems.append(f"{where}: 'path' must be relative, with forward slashes")
        elif path and not any(path.startswith(area + "/") for area in PINNED_AREAS):
            problems.append(f"{where}: must be under one of {', '.join(PINNED_AREAS)}")
        if origin and not _relative(origin):
            problems.append(f"{where}: 'from' must be relative, with forward slashes")
        if sha256 and not _SHA256.match(sha256):
            problems.append(f"{where}: 'sha256' must be 64 lower-case hex digits")
        if source and source not in commits:
            problems.append(f"{where}: source '{source}' has no commit under pins.sources")
        if path in seen:
            problems.append(f"{where}: listed twice")
        seen.add(path)
        files.append(KitFile(path, source, origin, sha256))
    if not files:
        problems.append("files: the kit lists no file")

    documents: list[Document] = []
    for i, entry in enumerate(data.get("documents") or []):
        where = f"documents[{i}]"
        if not isinstance(entry, dict):
            problems.append(f"{where}: expected a mapping")
            continue
        doc_id = text(entry, "id", where)
        file = text(entry, "file", where)
        cited_as = entry.get("cited_as") or []
        if doc_id and not _ID.match(doc_id):
            problems.append(f"{where}: 'id' must match {_ID.pattern}")
        if any(doc.id == doc_id for doc in documents):
            problems.append(f"{where}: id '{doc_id}' is used twice")
        if not isinstance(cited_as, list) or not all(isinstance(v, str) for v in cited_as):
            problems.append(f"{where}: 'cited_as' must be a list of names")
            cited_as = []
        if file and file not in seen:
            problems.append(f"{where}: '{file}' is not in the list of files")
        documents.append(Document(doc_id, file, tuple(cited_as)))

    if project and project not in seen:
        problems.append(f"build.project: '{project}' is not in the list of files")
    for key, folder in (("sdtm", sdtm), ("reference", reference), ("claims", claims)):
        if folder and not any(path.startswith(folder.rstrip("/") + "/") for path in seen):
            problems.append(f"build.{key}: no listed file is under '{folder}'")
    if sdtm and not sdtm.startswith("inputs/"):
        problems.append("build.sdtm: the SDTM datasets are inputs and belong under inputs/")
    for key, folder in (("reference", reference), ("claims", claims), ("project", project)):
        if folder and not folder.startswith("gold/"):
            problems.append(f"build.{key}: this is gold and belongs under gold/")

    gaps = data.get("trace_gaps") or {}
    if not isinstance(gaps, dict) or not all(
        isinstance(k, str) and isinstance(v, str) and v.strip() for k, v in gaps.items()
    ):
        problems.append("trace_gaps: must map a column ID to the reason, as text")
        gaps = {}

    if problems:
        raise KitError("; ".join(problems))
    return Kit(
        id=kit_id, title=title, tier=tier,
        engines={str(k): str(v) for k, v in engines.items()},
        sources={str(k): str(v) for k, v in commits.items()},
        project=project, sdtm=sdtm.rstrip("/"), reference=reference.rstrip("/"),
        claims=claims.rstrip("/") if claims else None,
        documents=tuple(documents), files=tuple(files), trace_gaps=dict(gaps),
    )


def manifest_path(root: Path, kit_id: str) -> Path:
    return root / "kits" / kit_id / "kit.yaml"


def load_kit(root: Path, kit_id: str) -> Kit:
    path = manifest_path(root, kit_id)
    if not path.is_file():
        raise KitError(f"no kit '{kit_id}': {path} does not exist")
    with open(path, encoding="ascii") as handle:
        kit = parse_kit(yaml.safe_load(handle))
    if kit.id != kit_id:
        raise KitError(f"{path}: the manifest names kit '{kit.id}'")
    return kit


def assembled_dir(root: Path, kit_id: str) -> Path:
    return build_dir(root) / "kits" / kit_id


def pin_problems(kit: Kit, manifest: pinned.Manifest) -> list[str]:
    """Why the kit's pins are not those of third_party/sources.yaml."""
    problems = []
    for name, commit in sorted(kit.sources.items()):
        try:
            expected = manifest.source(name).commit
        except KeyError:
            problems.append(f"source '{name}' is not in third_party/sources.yaml")
            continue
        if commit != expected:
            problems.append(f"source '{name}': kit pins {commit}, sources.yaml pins {expected}")
    return problems


def _pinned_files(dest: Path) -> set[str]:
    found: set[str] = set()
    for area in PINNED_AREAS:
        folder = dest / area
        if folder.is_dir():
            found |= {p.relative_to(dest).as_posix() for p in folder.rglob("*") if p.is_file()}
    return found


def verify_assembled(kit: Kit, dest: Path) -> list[str]:
    """Why the folder is not the kit the manifest describes."""
    problems = []
    for entry in kit.files:
        target = dest / entry.path
        if not target.is_file():
            problems.append(f"{entry.path}: missing")
        elif sha256_file(target) != entry.sha256:
            problems.append(f"{entry.path}: SHA-256 is not the pinned one")
    for stray in sorted(_pinned_files(dest) - kit.paths()):
        problems.append(f"{stray}: not in the manifest")
    return problems


def assemble(root: Path, kit: Kit, dest: Path | None = None) -> list[str]:
    """Copy the kit's files from the fetch cache, checking every hash.

    Returns the problems found; an empty list means dest now holds exactly
    the pinned files in its pinned areas.
    """
    dest = dest or assembled_dir(root, kit.id)
    cache = cache_dir(root)
    problems = pin_problems(kit, pinned.load_manifest(pinned.manifest_path(root)))
    for entry in kit.files:
        origin = cache / entry.source / entry.origin
        target = dest / entry.path
        if not origin.is_file():
            problems.append(
                f"{entry.path}: {entry.source}:{entry.origin} is not in the fetch cache"
            )
            continue
        if sha256_file(origin) != entry.sha256:
            problems.append(
                f"{entry.path}: {entry.source}:{entry.origin} does not have the pinned SHA-256"
            )
            continue
        if not target.is_file() or sha256_file(target) != entry.sha256:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(origin, target)
    if problems:
        return problems
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(manifest_path(root, kit.id), dest / "kit.yaml")
    return verify_assembled(kit, dest)


# Formats of study data and study documents. A kit of real data or real
# documents (tiers B and C) keeps them in the fetch cache, never in git.
DATA_SUFFIXES = frozenset({
    ".parquet", ".xpt", ".sas7bdat", ".csv", ".tsv", ".rds", ".rda", ".feather", ".arrow",
    ".pdf", ".rtf", ".doc", ".docx", ".xls", ".xlsx",
})


def pinned_hashes(root: Path) -> dict[str, str]:
    """SHA-256 -> name, for every file a kit manifest or sources.yaml pins."""
    found: dict[str, str] = {}
    try:
        manifest = pinned.load_manifest(pinned.manifest_path(root))
        found.update({pin.sha256: f"{pin.source}:{pin.path}" for pin in manifest.files})
    except (OSError, ValueError, yaml.YAMLError):
        pass
    for path in sorted((root / "kits").glob("*/kit.yaml")):
        try:
            with open(path, encoding="ascii") as handle:
                kit = parse_kit(yaml.safe_load(handle))
        except (OSError, ValueError, yaml.YAMLError):
            continue
        if kit.tier != "A":
            found.update({entry.sha256: f"{entry.path} of kit {kit.id}" for entry in kit.files})
    return found


def tracked_data_problems(root: Path, names: list[str]) -> list[str]:
    """Why the maintained files `names` break rule 4 of PLAN.md section 2.1 (E20).

    Three checks. A kit folder of tier B or C may hold kit.yaml and README.md
    only (a generated kit, tier A, may hold its small fixtures). Outside
    such a folder, no file may have the suffix of a data or document format,
    be a Define-XML or other ODM file, or be byte for byte a file that a kit
    of tier B or C or third_party/sources.yaml pins. A study document
    retyped or converted to another format is beyond these checks.
    """
    problems = []
    tiers: dict[str, str] = {}
    pinned_files = pinned_hashes(root)
    for name in names:
        parts = name.split("/")
        tier = None
        if parts[0] == "kits" and len(parts) >= 3:
            kit_id = parts[1]
            if kit_id not in tiers:
                try:
                    tiers[kit_id] = load_kit(root, kit_id).tier
                except (KitError, OSError, yaml.YAMLError) as error:
                    tiers[kit_id] = "?"
                    problems.append(f"kits/{kit_id}: no usable kit.yaml ({error})")
            tier = tiers[kit_id]
            if tier != "A" and "/".join(parts[2:]) not in ("kit.yaml", "README.md"):
                problems.append(f"{name}: a tier {tier} kit folder holds kit.yaml and "
                                "README.md only")
                continue
        if tier == "A":
            continue
        path = root / name
        if path.suffix.lower() in DATA_SUFFIXES:
            problems.append(f"{name}: study data or a study document in git")
        elif path.is_file():
            if path.suffix.lower() == ".xml" and b"<ODM" in path.read_bytes()[:65536]:
                problems.append(f"{name}: a Define-XML or other ODM file in git")
            elif (same := pinned_files.get(sha256_file(path))) is not None:
                problems.append(f"{name}: byte for byte {same}, which stays in the fetch cache")
    return problems


def _scalar(value: str) -> str:
    return value if _PLAIN.match(value) else json.dumps(value)


def files_block(entries: list[KitFile]) -> str:
    lines = ["files:"]
    for entry in sorted(entries, key=lambda e: e.path):
        lines += [
            f"  - path: {_scalar(entry.path)}",
            f"    source: {_scalar(entry.source)}",
            f"    from: {_scalar(entry.origin)}",
            f"    sha256: {entry.sha256}",
        ]
    return "\n".join(lines) + "\n"


def lock(root: Path, kit_id: str) -> list[str]:
    """Rewrite the SHA-256 of every listed file from the fetch cache.

    `files:` must be the last key of kit.yaml: everything before it is kept
    as written. Returns the paths whose hash changed.
    """
    path = manifest_path(root, kit_id)
    text = path.read_text(encoding="ascii")
    marker = "\nfiles:\n"
    if marker not in text:
        raise KitError(f"{path}: no 'files:' key")
    head = text[: text.index(marker) + 1]
    data = yaml.safe_load(text)
    cache = cache_dir(root)
    entries, changed = [], []
    for entry in data.get("files") or []:
        origin = cache / entry["source"] / entry["from"]
        if not origin.is_file():
            raise KitError(
                f"{entry['path']}: {entry['source']}:{entry['from']} is not in the fetch cache"
            )
        digest = sha256_file(origin)
        if digest != entry.get("sha256"):
            changed.append(entry["path"])
        entries.append(KitFile(entry["path"], entry["source"], entry["from"], digest))
    path.write_text(head + files_block(entries), encoding="ascii", newline="\n")
    parse_kit(yaml.safe_load(path.read_text(encoding="ascii")))
    return changed


def run_assemble(root: Path, kit_id: str, out: Callable[[str], None] = print) -> int:
    """`specfirst kit assemble <id>`."""
    try:
        kit = load_kit(root, kit_id)
    except KitError as error:
        out(f"kit {kit_id}: {error}")
        return 1
    dest = assembled_dir(root, kit_id)
    problems = assemble(root, kit, dest)
    for problem in problems:
        out(f"kit {kit_id}: {problem}")
    if problems:
        out(f"kit {kit_id}: NOT assembled ({len(problems)} problems)")
        return 1
    inputs = sum(1 for entry in kit.files if entry.path.startswith("inputs/"))
    out(f"kit {kit_id}: {len(kit.files)} files match their pinned SHA-256 "
        f"({inputs} inputs, {len(kit.files) - inputs} gold) in {dest}")
    return 0
