"""The versions of the standard: one folder each, frozen by its tree (ADR-020).

`standard/versions.yaml` lists every version of the catalog and of each
house standard with its status (`draft` or `frozen`), the date and the
answer that froze it, and, when frozen, the git tree hash of its folder:

    standard/catalog@<n>/                  a catalog version
    standard/houses/<house>@<n>/           a house version

A label names a version: `catalog@2`, `open-default@2`. Every loader takes a
label; without one it takes the default pair below, the pair the slice of
ADR-005 is built on. A frozen folder never changes: a change is a new
version (ADR-020, decision 4), and `frozen_problems` computes each frozen
tree again and compares. A draft version may change, and no kit, task, run
or score may name it (`require_usable`).

The tree hash is git's own (`git rev-parse <commit>:<folder>`), computed
here from the files on disk without calling git, so it holds in any clone,
under Windows and under WSL. Every file counts as a regular file (mode
100644): a frozen folder of the standard holds no script and no link.
"""

from __future__ import annotations

import hashlib
import os
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import yaml

from specfirst.paths import repo_root

VERSIONS = "standard/versions.yaml"
# The pair every loader takes when it is given no label (ADR-020, decision 3).
DEFAULT_CATALOG = "catalog@1"
DEFAULT_HOUSE = "open-default@1"
STATUSES = ("draft", "frozen")
_CATALOG = re.compile(r"^catalog@([1-9][0-9]*)$")
_HOUSE = re.compile(r"^([a-z][a-z0-9-]*)@([1-9][0-9]*)$")


class VersionError(ValueError):
    """A label that names no version, or a version that may not be used here."""


@dataclass(frozen=True)
class Version:
    label: str
    kind: str  # catalog | house
    status: str  # draft | frozen
    date: str
    by: str
    tree: str
    catalog: str  # a house: the catalog version it needs

    @property
    def number(self) -> int:
        return int(self.label.rsplit("@", 1)[1])


def catalog_number(label: str) -> int:
    match = _CATALOG.match(label)
    if not match:
        raise VersionError(f"'{label}' is not a catalog label (catalog@<n>)")
    return int(match.group(1))


def folder(root: Path | None, label: str) -> Path:
    """The folder of a version, from its label alone."""
    base = (root or repo_root()) / "standard"
    if _CATALOG.match(label):
        return base / label
    if _HOUSE.match(label):
        return base / "houses" / label
    raise VersionError(f"'{label}' is not a label (catalog@<n> or <house>@<n>)")


def relative(label: str) -> str:
    return folder(Path("."), label).as_posix()


def load(root: Path | None = None) -> dict[str, Version]:
    """Every version of `standard/versions.yaml`, by label."""
    path = (root or repo_root()) / VERSIONS
    with open(path, encoding="ascii") as handle:
        raw = yaml.safe_load(handle) or {}
    found: dict[str, Version] = {}
    for kind, key in (("catalog", "catalogs"), ("house", "houses")):
        for label, body in (raw.get(key) or {}).items():
            body = body if isinstance(body, dict) else {}
            found[str(label)] = Version(
                label=str(label), kind=kind, status=str(body.get("status", "")),
                date=str(body.get("date") or ""), by=str(body.get("by") or ""),
                tree=str(body.get("tree") or ""), catalog=str(body.get("catalog") or ""))
    return found


# -- git's tree hash ----------------------------------------------------------


def _object(kind: bytes, body: bytes) -> bytes:
    return hashlib.sha1(kind + b" " + str(len(body)).encode() + b"\0" + body).digest()


def _tree(path: str) -> bytes | None:
    """The tree object ID of a folder, or None for a folder without files (git keeps none)."""
    items = []
    with os.scandir(path) as listing:
        for item in listing:
            name = item.name.encode("utf-8")
            if item.is_dir(follow_symlinks=False):
                digest = _tree(item.path)
                if digest is not None:
                    items.append((name + b"/", b"40000 " + name + b"\0" + digest))
            else:
                with open(item.path, "rb") as handle:
                    digest = _object(b"blob", handle.read())
                items.append((name, b"100644 " + name + b"\0" + digest))
    if not items:
        return None
    return _object(b"tree", b"".join(entry for _, entry in sorted(items)))


def tree_hash(path: Path) -> str:
    """git's tree hash of a folder as it is on disk (every file a regular file)."""
    digest = _tree(str(path))
    return digest.hex() if digest is not None else ""


# -- checks -------------------------------------------------------------------


def frozen_problems(root: Path) -> list[str]:
    """Every frozen folder has the tree it was frozen with; every folder is listed."""
    problems = []
    try:
        versions = load(root)
    except (OSError, yaml.YAMLError) as error:
        return [f"{VERSIONS}: {error}"]
    for label, version in versions.items():
        try:
            path = folder(root, label)
        except VersionError as error:
            problems.append(f"{VERSIONS}: {error}")
            continue
        if version.kind == "catalog" and not _CATALOG.match(label):
            problems.append(f"{VERSIONS}: '{label}' is listed as a catalog")
        if version.status not in STATUSES:
            problems.append(f"{label}: the status '{version.status}' is not one of "
                            f"{', '.join(STATUSES)}")
        if version.kind == "house" and version.catalog not in versions:
            problems.append(f"{label}: needs the catalog '{version.catalog}', which "
                            f"{VERSIONS} does not list")
        if not path.is_dir():
            problems.append(f"{label}: no folder {relative(label)}")
            continue
        if version.status == "frozen":
            if not (version.date and version.by and version.tree):
                problems.append(f"{label}: a frozen version names its date, what froze it "
                                "and its tree")
            found = tree_hash(path)
            if found != version.tree:
                problems.append(
                    f"{label}: the folder {relative(label)} has the tree {found}, frozen as "
                    f"{version.tree}: a frozen version does not change; a change is a new "
                    "version (ADR-020, decision 4)")
    base = root / "standard"
    on_disk = sorted(p.name for p in base.glob("catalog@*") if p.is_dir())
    on_disk += sorted(p.name for p in (base / "houses").glob("*@*") if p.is_dir())
    for label in on_disk:
        if label not in versions:
            problems.append(f"{label}: a folder that {VERSIONS} does not list")
    if (base / "catalog").exists():
        problems.append("standard/catalog: a catalog lives in standard/catalog@<n>/")
    for label in (DEFAULT_CATALOG, DEFAULT_HOUSE):
        problems += named_problems(versions, [("the default pair", label)])
    return problems + named_problems(versions, kits_named(root))


def kits_named(root: Path) -> list[tuple[str, str]]:
    """(where, label) for every label the kits of the repository name (kits/*/kit.yaml)."""
    named = []
    for path in sorted((root / "kits").glob("*/kit.yaml")):
        with open(path, encoding="ascii") as handle:
            manifest = yaml.safe_load(handle)
        if isinstance(manifest, dict):
            named += [(f"{path.relative_to(root).as_posix()} ({kind})", label)
                      for kind, label in kit_labels(manifest)]
    return named


def named_problems(versions: dict[str, Version],
                   named: Iterable[tuple[str, str]]) -> list[str]:
    """Why a kit, task, run or score may not name these labels (where, label)."""
    problems = []
    for where, label in named:
        version = versions.get(label)
        if version is None:
            problems.append(f"{where}: names '{label}', which {VERSIONS} does not list")
        elif version.status != "frozen":
            problems.append(f"{where}: names '{label}', a {version.status} version; only a "
                            "frozen version may be named by a kit, a task, a run or a score "
                            "(ADR-020, decision 1)")
    return problems


def kit_labels(manifest: dict) -> list[tuple[str, str]]:
    """The labels a kit's kit.yaml names: the catalog (name and version) and the house."""
    found = []
    catalog = manifest.get("catalog")
    if isinstance(catalog, dict) and catalog.get("version") not in (None, ""):
        found.append(("catalog", f"catalog@{catalog['version']}"))
    if manifest.get("house"):
        found.append(("house", str(manifest["house"])))
    return found


def require_usable(root: Path, labels: Iterable[str], where: str) -> None:
    """Raise unless every label names a frozen version."""
    problems = named_problems(load(root), [(where, label) for label in labels])
    if problems:
        raise VersionError("; ".join(problems))


def pair_problems(catalog_label: str, house_label: str, versions: dict[str, Version]) -> list[str]:
    """A house is used with the catalog version it names."""
    house = versions.get(house_label)
    if house is None:
        return [f"'{house_label}' is not a house version of {VERSIONS}"]
    if house.catalog != catalog_label:
        return [f"{house_label} needs {house.catalog}, not {catalog_label}"]
    return []
