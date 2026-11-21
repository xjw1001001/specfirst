"""Load the decision catalog (PLAN.md section 5).

A catalog version is a folder, `standard/catalog@<n>/` (ADR-020); its label
is `catalog@<n>`, and `specfirst.compile.versions` says which versions are
frozen and which pair a loader takes by default:

    catalog.yaml          name, version, units, design features, entry order
                          (from catalog@2: the entry schema, the terms)
    migration.yaml        from catalog@2: what the step from the version before keeps
    sources.yaml          the public sources that entries cite
    probes.yaml           probe recipes (section 6.5)
    entries/<id>.yaml     one entry per file (section 5.1)
    templates/<id>.yaml   compile template: one fragment per alternative
    phrasings/<id>.yaml   natural variants of every statement
    knowledge/<id>.md     reading notes

Loading is lenient: it reads what is there. `specfirst.compile.checks` says
what is wrong with it.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from specfirst.compile import versions
from specfirst.compile.slots import Slot, SlotError, slot_from_spec
from specfirst.paths import repo_root

# The schema of the entry files when catalog.yaml names none (catalog@1).
ENTRY_SCHEMA = "catalog-entry"


class CatalogError(ValueError):
    """The catalog cannot be read at all."""


@dataclass(frozen=True)
class Alternative:
    id: str
    statement: str
    definition: str = ""
    slots: tuple[Slot, ...] = ()
    sources: tuple[dict, ...] = ()

    def slot(self, name: str) -> Slot:
        for slot in self.slots:
            if slot.name == name:
                return slot
        raise KeyError(name)


@dataclass(frozen=True)
class Entry:
    id: str
    units: tuple[str, ...]
    per_family: bool  # declared with `units`: answered once per table family
    applies_when: str
    question: str
    alternatives: tuple[Alternative, ...]
    # catalog@1: an alternative ID, a mapping unit -> ID, or None. From catalog@2 an
    # entry has none: the house holds the defaults (specfirst.compile.house).
    house_default: object
    compile: str
    phrasings: str
    reading: str
    probes: tuple[str, ...]
    sources: tuple[dict, ...]
    raw: dict = field(compare=False, default_factory=dict)
    fixed_rules: tuple[dict, ...] = ()  # from catalog@2: {id, text, sources}

    def alternative(self, rule: str) -> Alternative:
        for alternative in self.alternatives:
            if alternative.id == rule:
                return alternative
        raise KeyError(f"entry {self.id} has no alternative '{rule}'")

    def default_for(self, unit: str) -> str | None:
        """The ID of the house default for a unit, or None when there is none."""
        if isinstance(self.house_default, dict):
            return self.house_default.get(unit)
        return self.house_default if isinstance(self.house_default, str) else None


@dataclass(frozen=True)
class Unit:
    id: str
    kind: str  # module | table_family
    title: str
    phrase: str = ""  # table families: how a statement names the output


@dataclass(frozen=True)
class Catalog:
    directory: Path
    name: str
    version: str
    units: dict[str, Unit]
    design_features: dict[str, str]
    entries: dict[str, Entry]  # in catalog order
    sources: dict[str, dict]
    probes: dict[str, dict]
    raw: dict = field(compare=False, default_factory=dict)
    load_problems: tuple[str, ...] = ()

    @property
    def label(self) -> str:
        """The version label: `catalog@<version>`."""
        return f"catalog@{self.version}"

    @property
    def entry_schema(self) -> str:
        """The schema of its entry files (standard/schemas/)."""
        return str(self.raw.get("entry_schema") or ENTRY_SCHEMA)

    @property
    def has_defaults(self) -> bool:
        """catalog@1 holds the house defaults in its entries; later versions do not."""
        return self.entry_schema == ENTRY_SCHEMA

    def entry(self, entry_id: str) -> Entry:
        if entry_id not in self.entries:
            raise KeyError(f"the catalog has no entry '{entry_id}'")
        return self.entries[entry_id]

    def keys(self) -> list[tuple[str, str]]:
        """Every (entry ID, unit) pair: the questions a study answers, in order."""
        return [(entry.id, unit) for entry in self.entries.values() for unit in entry.units]

    def read_yaml(self, relative: str) -> object:
        return read_yaml(self.directory / relative)


_YAML_CACHE: dict[tuple[str, int, int], object] = {}


def read_yaml(path: Path) -> object:
    """A YAML file as data. A file is parsed once until it changes; callers get a copy."""
    stat = path.stat()
    key = (str(path), stat.st_mtime_ns, stat.st_size)
    if key not in _YAML_CACHE:
        with open(path, encoding="ascii") as handle:
            _YAML_CACHE[key] = yaml.safe_load(handle)
    return copy.deepcopy(_YAML_CACHE[key])


def default_dir(root: Path | None = None, label: str | None = None) -> Path:
    """The folder of a catalog version; without a label, the default (versions.DEFAULT_CATALOG)."""
    label = label or versions.DEFAULT_CATALOG
    versions.catalog_number(label)
    return versions.folder(root or repo_root(), label)


def _alternative(entry_id: str, raw: dict, problems: list[str]) -> Alternative:
    slots = []
    for name, spec in (raw.get("slots") or {}).items():
        try:
            slots.append(slot_from_spec(str(name), spec if isinstance(spec, dict) else {}))
        except SlotError as error:
            problems.append(f"{entry_id}/{raw.get('id')}: {error}")
    return Alternative(
        id=str(raw.get("id", "")),
        statement=str(raw.get("statement", "")),
        definition=str(raw.get("definition", "") or ""),
        slots=tuple(slots),
        sources=tuple(s for s in (raw.get("sources") or []) if isinstance(s, dict)),
    )


def _entry(raw: dict, problems: list[str]) -> Entry:
    entry_id = str(raw.get("id", ""))
    per_family = "units" in raw
    units = tuple(raw.get("units") or ()) if per_family else (str(raw.get("unit", "")),)
    alternatives = tuple(
        _alternative(entry_id, alt, problems)
        for alt in (raw.get("alternatives") or [])
        if isinstance(alt, dict)
    )
    return Entry(
        id=entry_id,
        units=tuple(str(unit) for unit in units),
        per_family=per_family,
        applies_when=str(raw.get("applies_when", "")),
        question=str(raw.get("question", "")),
        alternatives=alternatives,
        house_default=raw.get("house_default"),
        compile=str(raw.get("compile", "")),
        phrasings=str(raw.get("phrasings", "")),
        reading=str(raw.get("reading", "")),
        probes=tuple(str(p) for p in (raw.get("probes") or ())),
        sources=tuple(s for s in (raw.get("sources") or []) if isinstance(s, dict)),
        raw=raw,
        fixed_rules=tuple(r for r in (raw.get("fixed_rules") or []) if isinstance(r, dict)),
    )


def load(directory: Path | None = None) -> Catalog:
    """Read a catalog folder. Problems found while reading are kept in `load_problems`."""
    directory = directory or default_dir()
    index_path = directory / "catalog.yaml"
    if not index_path.is_file():
        raise CatalogError(f"no catalog at {directory}")
    index = read_yaml(index_path)
    if not isinstance(index, dict):
        raise CatalogError(f"{index_path} is not a mapping")
    problems: list[str] = []
    units = {}
    for unit_id, raw in (index.get("units") or {}).items():
        raw = raw if isinstance(raw, dict) else {}
        units[str(unit_id)] = Unit(
            id=str(unit_id),
            kind=str(raw.get("kind", "")),
            title=str(raw.get("title", "")),
            phrase=str(raw.get("phrase", "") or ""),
        )
    entries: dict[str, Entry] = {}
    listed = [str(entry_id) for entry_id in (index.get("entries") or [])]
    for entry_id in listed:
        path = directory / "entries" / f"{entry_id}.yaml"
        if not path.is_file():
            problems.append(f"catalog.yaml lists '{entry_id}', but {path.name} is missing")
            continue
        raw = read_yaml(path)
        if not isinstance(raw, dict):
            problems.append(f"entries/{path.name} is not a mapping")
            continue
        if raw.get("id") != entry_id:
            problems.append(f"entries/{path.name} has the id '{raw.get('id')}'")
        if entry_id in entries:
            problems.append(f"catalog.yaml lists '{entry_id}' twice")
        entries[entry_id] = _entry(raw, problems)
    on_disk = sorted(p.stem for p in (directory / "entries").glob("*.yaml"))
    for entry_id in on_disk:
        if entry_id not in listed:
            problems.append(f"entries/{entry_id}.yaml is not listed in catalog.yaml")

    def registry(name: str, key: str) -> dict[str, dict]:
        path = directory / name
        if not path.is_file():
            problems.append(f"{name} is missing")
            return {}
        raw = read_yaml(path)
        body = raw.get(key) if isinstance(raw, dict) else None
        if not isinstance(body, dict):
            problems.append(f"{name} has no mapping '{key}'")
            return {}
        return {str(k): (v if isinstance(v, dict) else {}) for k, v in body.items()}

    return Catalog(
        directory=directory,
        name=str(index.get("catalog", "")),
        version=str(index.get("version", "")),
        units=units,
        design_features={str(k): str(v) for k, v in (index.get("design_features") or {}).items()},
        entries=entries,
        sources=registry("sources.yaml", "sources"),
        probes=registry("probes.yaml", "probes"),
        raw=index,
        load_problems=tuple(problems),
    )
