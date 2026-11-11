"""The ASCII check (rule R10): maintained files hold ASCII bytes only.

Maintained files are the files git tracks plus the new files it does not
ignore. Binary formats that cannot be ASCII are skipped by suffix.

Run it with `python -m specfirst.asciicheck` or `make ascii`.
"""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

from specfirst.paths import git_env, repo_root

BINARY_SUFFIXES = frozenset(
    {".parquet", ".xpt", ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".ico", ".rds", ".woff", ".woff2"}
)


def maintained_files(root: Path) -> list[str]:
    """Tracked files and untracked files that are not ignored, sorted."""
    done = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=root,
        capture_output=True,
        env={**os.environ, **git_env(root)},
    )
    if done.returncode != 0:
        message = done.stderr.decode("utf-8", "replace").strip()
        raise RuntimeError(f"git ls-files failed in {root}: {message}")
    names = {name for name in done.stdout.decode("utf-8", "surrogateescape").split("\0") if name}
    return sorted(names)


def find_non_ascii(data: bytes, limit: int = 5) -> list[tuple[int, int, int]]:
    """The first `limit` non-ASCII bytes as (line, column, byte value), counted from 1."""
    hits: list[tuple[int, int, int]] = []
    if data.isascii():
        return hits
    for number, line in enumerate(data.split(b"\n"), start=1):
        if line.isascii():
            continue
        for column, byte in enumerate(line, start=1):
            if byte > 127:
                hits.append((number, column, byte))
                if len(hits) >= limit:
                    return hits
    return hits


def check(root: Path, out: Callable[[str], None] = print) -> int:
    """Print every offending file. Returns 0 when all maintained files are ASCII."""
    checked = bad = 0
    for name in maintained_files(root):
        path = root / name
        if path.suffix.lower() in BINARY_SUFFIXES or not path.is_file():
            continue
        checked += 1
        hits = find_non_ascii(path.read_bytes())
        if hits:
            bad += 1
            for line, column, byte in hits:
                out(f"{name}:{line}:{column}: non-ASCII byte 0x{byte:02x}")
    out(f"ASCII check: {checked} files checked, {bad} with non-ASCII bytes")
    return 1 if bad else 0


def main() -> int:
    return check(repo_root())


if __name__ == "__main__":
    sys.exit(main())
