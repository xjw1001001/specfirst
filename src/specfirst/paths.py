"""Where things live: the checkout root and the fetch cache."""

from __future__ import annotations

import os
from pathlib import Path


def _is_root(path: Path) -> bool:
    return (path / "PLAN.md").is_file() and (path / "third_party" / "sources.yaml").is_file()


def repo_root(start: Path | None = None) -> Path:
    """The checkout to work on.

    Order: the SPECFIRST_ROOT variable, then the nearest parent of the
    current directory that is a checkout (so each git worktree is found from
    inside it), then the source tree this module was loaded from.
    """
    env = os.environ.get("SPECFIRST_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    here = (start or Path.cwd()).resolve()
    for candidate in (here, *here.parents):
        if _is_root(candidate):
            return candidate
    source_tree = Path(__file__).resolve().parents[2]
    if _is_root(source_tree):
        return source_tree
    raise SystemExit("specfirst: not inside a specfirst checkout (PLAN.md not found)")


def cache_dir(root: Path) -> Path:
    """The folder that holds the fetched sources. It is never committed.

    Order: the SPECFIRST_CACHE variable, then the path written in the ignored
    file third_party/cache-location (relative paths start at third_party/),
    then third_party/cache.
    """
    env = os.environ.get("SPECFIRST_CACHE")
    if env:
        return Path(env).expanduser().resolve()
    location = root / "third_party" / "cache-location"
    if location.is_file():
        text = location.read_text(encoding="ascii").strip()
        if text:
            path = Path(text).expanduser()
            if not path.is_absolute():
                path = root / "third_party" / path
            return path.resolve()
    return root / "third_party" / "cache"


def build_dir(root: Path) -> Path:
    """Ignored folder for logs and other products of a run."""
    return root / "build"
