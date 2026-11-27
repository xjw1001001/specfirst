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
from specfirst.machine.canonical import sha256_bytes, sha256_file
from specfirst.paths import build_dir, cache_dir

FORMAT = 0
TIERS = ("A", "B", "C")
# The parts of an assembled kit that only the manifest may fill.
PINNED_AREAS = ("inputs", "gold/spec", "gold/reference", "gold/claims")

_ID = re.compile(r"^[a-z0-9][a-z0-9-]*$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_COMMIT = re.compile(r"^[0-9a-f]{40}$")
# A version of the standard (ADR-020): catalog@<n> or <house>@<n>.
_LABEL = re.compile(r"^[a-z][a-z0-9-]*@[1-9][0-9]*$")
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
class CsrTable:
    """A table of a CSR that is the reference of a grid (ADR-012, decision 3; ADR-015)."""

    file: str  # the CSR: a pinned file of the kit
    page: int  # its page, counted from 1
    table: str  # its number, as the page prints it after "Table "


@dataclass(frozen=True)
class Display:
    """One output of a reporting event that the kit builds as a grid (PLAN.md section 7.4)."""

    output: str  # the ID of the ARS output
    layout: str  # its layout: a file of our own in the kit folder
    # The CSR table its cells are compared with; None: the formatted values the
    # reporting event embeds are the reference (real-3a).
    reference: CsrTable | None = None
    # The table shell its mock shell is held against: a pinned PDF of the kit
    # (specfirst.machine.shells; the review of real-3a, F1). None: no shell.
    shell: str | None = None


@dataclass(frozen=True)
class ResultSet:
    """One ARS reporting event of the kit, for the result engines (PLAN.md section 7.1)."""

    id: str
    # The reporting event: a pinned file, whose embedded results are a reference; or a
    # file of our own in the kit folder, written from the documents (ADR-015).
    ars: str
    schema: str | None  # the JSON Schema generated from the ARS model: a pinned file
    subject_key: str  # the column that says which records of two datasets belong together
    binding: dict  # ARS operations bound to the method registry, and method options
    # The outputs that are built as grids. This list is the limit of the display
    # checks: an output that is not listed is not built and not compared.
    displays: tuple[Display, ...] = ()


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
    results: tuple[ResultSet, ...] = ()
    # Our own file in the kit folder: the classified differences from the references.
    exceptions: str | None = None
    # Our own files in the kit folder: decision records (PLAN.md section 4.3), one per
    # line: custom decisions the catalog does not hold yet (custom:<slug>, section 10) and,
    # with a `standard`, records of the catalog it names (issue #31, ADR-022).
    decisions: tuple[str, ...] = ()
    # The catalog and house version the kit's catalog records are written over (ADR-022):
    # (catalog label, house label), e.g. ("catalog@2", "open-default@2"), or None.
    standard: tuple[str, str] | None = None

    def paths(self) -> set[str]:
        return {entry.path for entry in self.files}

    def own_files(self) -> list[str]:
        """The files of our own that the kit folder holds next to the manifest."""
        layouts = [display.layout for spec in self.results for display in spec.displays]
        events = [spec.ars for spec in self.results if spec.ars not in self.paths()]
        named = [name for name in (self.exceptions, *self.decisions) if name]
        return sorted({*layouts, *events, *named})

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

    def own(path: object) -> bool:
        """A file of our own: under gold/, and outside what only the manifest may fill."""
        return (_relative(path) and path.startswith("gold/") and path not in seen
                and not any(path.startswith(area + "/") for area in PINNED_AREAS))

    exceptions = build.get("exceptions")
    if exceptions is not None and not own(exceptions):
        problems.append("build.exceptions: must be a file of our own under gold/, outside "
                        f"{', '.join(PINNED_AREAS)}")
        exceptions = None
    # A file, or a list of files (issue #31: the efficacy records and the safety records).
    given = build.get("decisions")
    named = [given] if isinstance(given, str) else given if isinstance(given, list) else []
    decisions: tuple[str, ...] = ()
    if given is not None and (not named or len(set(named)) != len(named) or not all(
            own(name) and name != exceptions for name in named)):
        problems.append("build.decisions: must be a file of our own under gold/, outside "
                        f"{', '.join(PINNED_AREAS)}, or a list of such files, each once")
    else:
        decisions = tuple(named)
    standard = None
    pair = data.get("standard")
    if pair is not None:
        if (not isinstance(pair, dict) or set(pair) != {"catalog", "house"}
                or not all(isinstance(v, str) and _LABEL.match(v) for v in pair.values())
                or not pair["catalog"].startswith("catalog@")):
            problems.append("standard: names the 'catalog' and the 'house' by their labels, "
                            "such as catalog@2 and open-default@2")
        else:
            standard = (pair["catalog"], pair["house"])

    result_sets: list[ResultSet] = []
    for i, entry in enumerate(data.get("results") or []):
        where = f"results[{i}]"
        if not isinstance(entry, dict):
            problems.append(f"{where}: expected a mapping")
            continue
        unknown = sorted(set(entry) - {"id", "ars", "schema", "subject_key", "binding",
                                       "outputs"})
        if unknown:
            problems.append(f"{where}: unknown key {', '.join(unknown)}")
        displays: list[Display] = []
        for item in entry.get("outputs") or []:
            if not isinstance(item, dict) or set(item) - {"reference", "shell"} != {
                    "id", "layout"} or not isinstance(item["id"], str) or not item["id"]:
                problems.append(f"{where}: an output needs exactly its 'id' and its 'layout', "
                                "and may name its 'reference' and its 'shell'")
                continue
            shell = item.get("shell")
            if shell is not None and (shell not in seen or not str(shell).endswith(".pdf")):
                problems.append(f"{where}, output '{item['id']}': its shell must be a listed "
                                "file, a PDF")
                shell = None
            if not own(item["layout"]) or item["layout"] in (exceptions, *decisions):
                problems.append(f"{where}, output '{item['id']}': the layout must be a file of "
                                f"our own under gold/, outside {', '.join(PINNED_AREAS)}")
                continue
            if any(known.output == item["id"] for known in displays):
                problems.append(f"{where}: output '{item['id']}' is listed twice")
            csr_table = None
            given = item.get("reference")
            if given is not None:
                if not isinstance(given, dict) or set(given) != {"csr", "page", "table"} or \
                        given.get("csr") not in seen or isinstance(given.get("page"), bool) or \
                        not isinstance(given.get("page"), int) or given["page"] < 1 or \
                        not isinstance(given.get("table"), str) or not given["table"]:
                    problems.append(f"{where}, output '{item['id']}': a reference names the "
                                    "'csr' (a listed file), its 'page' and its 'table'")
                else:
                    csr_table = CsrTable(given["csr"], given["page"], given["table"])
            displays.append(Display(item["id"], item["layout"], csr_table, shell))
        set_id = text(entry, "id", where)
        ars_file = text(entry, "ars", where)
        schema = entry.get("schema")
        subject_key = entry.get("subject_key", "USUBJID")
        binding = entry.get("binding") or {}
        if set_id and not _ID.match(set_id):
            problems.append(f"{where}: 'id' must match {_ID.pattern}")
        if any(known.id == set_id for known in result_sets):
            problems.append(f"{where}: id '{set_id}' is used twice")
        if ars_file and ars_file not in seen and (
                not own(ars_file) or ars_file in (exceptions, *decisions)):
            problems.append(f"{where}: ars '{ars_file}' is neither in the list of files nor a "
                            f"file of our own under gold/, outside {', '.join(PINNED_AREAS)}")
        if schema is not None and schema not in seen:
            problems.append(f"{where}: schema '{schema}' is not in the list of files")
        if not isinstance(subject_key, str) or not subject_key:
            problems.append(f"{where}: 'subject_key' must name a column")
        if not isinstance(binding, dict) or set(binding) - {"operations", "options"} or not all(
                isinstance(part, dict) for part in binding.values()):
            problems.append(f"{where}: 'binding' may hold 'operations' and 'options', each a "
                            "mapping")
            binding = {}
        result_sets.append(ResultSet(set_id, ars_file, schema, str(subject_key), binding,
                                     tuple(displays)))
    layouts = [display.layout for spec in result_sets for display in spec.displays]
    if len(set(layouts)) != len(layouts):
        problems.append("results: two outputs name the same layout file")
    if set(layouts) & {spec.ars for spec in result_sets}:
        problems.append("results: a layout file is also a reporting event")

    if problems:
        raise KitError("; ".join(problems))
    return Kit(
        id=kit_id, title=title, tier=tier,
        engines={str(k): str(v) for k, v in engines.items()},
        sources={str(k): str(v) for k, v in commits.items()},
        project=project, sdtm=sdtm.rstrip("/"), reference=reference.rstrip("/"),
        claims=claims.rstrip("/") if claims else None,
        documents=tuple(documents), files=tuple(files), trace_gaps=dict(gaps),
        results=tuple(result_sets), exceptions=exceptions, decisions=decisions,
        standard=standard,
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
    for name in kit.own_files():  # our own files of the kit folder, kept next to the manifest
        own = manifest_path(root, kit.id).parent / name
        if not own.is_file():
            return [f"{name}: named by the manifest, but not in kits/{kit.id}/"]
        (dest / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(own, dest / name)
    return verify_assembled(kit, dest)


# Formats of study data and study documents. A kit of real data or real
# documents (tiers B and C) keeps them in the fetch cache, never in git.
DATA_SUFFIXES = frozenset({
    ".parquet", ".xpt", ".sas7bdat", ".csv", ".tsv", ".rds", ".rda", ".feather", ".arrow",
    ".pdf", ".rtf", ".doc", ".docx", ".xls", ".xlsx",
})


# An XML document whose root element is ODM, with or without a namespace
# prefix: after an optional declaration, comments, processing instructions and
# a document type.
_ODM_ROOT = re.compile(
    r"\A\s*(?:(?:<\?.*?\?>|<!--.*?-->|<!DOCTYPE[^>\[]*(?:\[.*?\])?[^>]*>)\s*)*"
    r"<(?:[A-Za-z_][\w.-]*:)?ODM[\s/>]",
    re.DOTALL,
)


def is_odm(data: bytes) -> bool:
    """Whether the bytes are a Define-XML or other ODM file, in UTF-8 or UTF-16.

    Decided by the root element, not by the name of the file or by where in
    the file the element starts.
    """
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        encodings = ("utf-16",)
    elif b"\x00" in data[:64]:
        encodings = ("utf-16-le", "utf-16-be")
    else:
        encodings = ("utf-8-sig",)
    return any(_ODM_ROOT.match(data.decode(encoding, errors="replace")) for encoding in encodings)


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
    be a Define-XML or other ODM file (an XML document with the root element
    ODM, in UTF-8 or UTF-16, under any name), or be byte for byte a file that
    a kit of tier B or C or third_party/sources.yaml pins. A study document
    retyped or converted to another format is beyond these checks, and so is
    an ODM file in another encoding or compressed.
    """
    problems = []
    tiers: dict[str, str] = {}
    own: dict[str, set[str]] = {}  # what a kit folder of tier B or C may hold
    pinned_files = pinned_hashes(root)
    for name in names:
        parts = name.split("/")
        tier = None
        if parts[0] == "kits" and len(parts) >= 3:
            kit_id = parts[1]
            if kit_id not in tiers:
                own[kit_id] = {"kit.yaml", "README.md"}
                try:
                    kit = load_kit(root, kit_id)
                    tiers[kit_id] = kit.tier
                    own[kit_id] |= set(kit.own_files())
                except (KitError, OSError, yaml.YAMLError) as error:
                    tiers[kit_id] = "?"
                    problems.append(f"kits/{kit_id}: no usable kit.yaml ({error})")
            tier = tiers[kit_id]
            if tier != "A" and "/".join(parts[2:]) not in own[kit_id]:
                problems.append(f"{name}: a tier {tier} kit folder holds kit.yaml, README.md "
                                "and the files of our own its manifest names (the exceptions, "
                                "the layouts), nothing else")
                continue
        if tier == "A":
            continue
        path = root / name
        if path.suffix.lower() in DATA_SUFFIXES:
            problems.append(f"{name}: study data or a study document in git")
        elif path.is_file():
            data = path.read_bytes()
            if is_odm(data):
                problems.append(f"{name}: a Define-XML or other ODM file in git")
            elif (same := pinned_files.get(sha256_bytes(data))) is not None:
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
