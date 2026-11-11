"""The manifest of pinned public sources (third_party/sources.yaml).

PLAN.md appendix A is the list. Rule R3: engines are pinned by version,
inputs by commit and SHA-256.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

_NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")
_COMMIT = re.compile(r"^[0-9a-f]{40}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


class ManifestError(ValueError):
    """The manifest is not usable."""


@dataclass(frozen=True)
class Source:
    name: str  # folder name in the cache
    title: str
    repository: str  # GitHub owner/name
    commit: str
    license: str
    used_for: str
    url: str  # what git clones from

    @property
    def web_url(self) -> str:
        return f"https://github.com/{self.repository}"


@dataclass(frozen=True)
class PinnedFile:
    source: str
    path: str  # relative to the source's root, with forward slashes
    sha256: str
    note: str = ""


@dataclass(frozen=True)
class Manifest:
    sources: tuple[Source, ...]
    files: tuple[PinnedFile, ...]

    def source(self, name: str) -> Source:
        for src in self.sources:
            if src.name == name:
                return src
        raise KeyError(name)


def _text(entry: dict, key: str, where: str) -> str:
    value = entry.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ManifestError(f"{where}: '{key}' is missing or empty")
    return value.strip()


def parse_manifest(data: object) -> Manifest:
    if not isinstance(data, dict) or not isinstance(data.get("sources"), list):
        raise ManifestError("manifest: expected a mapping with a 'sources' list")
    sources: list[Source] = []
    for i, entry in enumerate(data["sources"]):
        where = f"sources[{i}]"
        if not isinstance(entry, dict):
            raise ManifestError(f"{where}: expected a mapping")
        name = _text(entry, "name", where)
        where = f"source '{name}'"
        if not _NAME.match(name):
            raise ManifestError(f"{where}: the name must match {_NAME.pattern}")
        if any(s.name == name for s in sources):
            raise ManifestError(f"{where}: listed twice")
        repository = _text(entry, "repository", where)
        if not _REPOSITORY.match(repository):
            raise ManifestError(f"{where}: 'repository' must be owner/name")
        commit = _text(entry, "commit", where)
        if not _COMMIT.match(commit):
            raise ManifestError(f"{where}: 'commit' must be 40 lower-case hex digits")
        url = entry.get("url") or f"https://github.com/{repository}.git"
        sources.append(
            Source(
                name=name,
                title=_text(entry, "title", where),
                repository=repository,
                commit=commit,
                license=_text(entry, "license", where),
                used_for=_text(entry, "used_for", where),
                url=str(url),
            )
        )
    files: list[PinnedFile] = []
    for i, entry in enumerate(data.get("files") or []):
        where = f"files[{i}]"
        if not isinstance(entry, dict):
            raise ManifestError(f"{where}: expected a mapping")
        source = _text(entry, "source", where)
        if not any(s.name == source for s in sources):
            raise ManifestError(f"{where}: unknown source '{source}'")
        path = _text(entry, "path", where)
        if path.startswith("/") or "\\" in path or ".." in path.split("/"):
            raise ManifestError(f"{where}: 'path' must be relative, with forward slashes")
        sha256 = _text(entry, "sha256", where)
        if not _SHA256.match(sha256):
            raise ManifestError(f"{where}: 'sha256' must be 64 lower-case hex digits")
        files.append(PinnedFile(source, path, sha256, str(entry.get("note") or "")))
    return Manifest(tuple(sources), tuple(files))


def manifest_path(root: Path) -> Path:
    return root / "third_party" / "sources.yaml"


def load_manifest(path: Path) -> Manifest:
    with open(path, encoding="ascii") as handle:
        return parse_manifest(yaml.safe_load(handle))
