"""`specfirst fetch`: clone the pinned sources into the cache and verify them.

Each source is fetched at exactly its pinned commit (a shallow fetch of that
one commit) and then checked: HEAD is the pinned commit, the working tree is
clean (no changed, added or ignored file), and every pinned file has its
SHA-256. With verify_only nothing is downloaded.
"""

from __future__ import annotations

import hashlib
import subprocess
import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path

from specfirst.paths import cache_dir
from specfirst.sources import Manifest, PinnedFile, Source, load_manifest, manifest_path

# Settings that keep the clone byte-identical on every platform.
_GIT = ["git", "-c", "core.autocrlf=false", "-c", "advice.detachedHead=false"]


class GitError(RuntimeError):
    """A git command failed."""


@dataclass(frozen=True)
class Result:
    name: str
    ok: bool
    action: str  # present | fetched | updated | missing | error
    detail: str


def _git(args: list[str], cwd: Path) -> str:
    done = subprocess.run([*_GIT, *args], cwd=cwd, capture_output=True, text=True)
    if done.returncode != 0:
        message = (done.stderr or done.stdout).strip().splitlines()
        raise GitError(f"git {' '.join(args)}: {message[-1] if message else 'failed'}")
    return done.stdout


def head_commit(dest: Path) -> str | None:
    try:
        return _git(["rev-parse", "--verify", "HEAD"], dest).strip()
    except GitError:
        return None


def changed_paths(dest: Path) -> list[str]:
    """Modified, deleted, untracked or ignored paths. An empty list means a clean tree.

    Ignored files count: a source may ignore the very files a run leaves
    behind (Pilot 7 ignores its `*-yamaa.parquet` outputs), and a fresh
    fetch has none.
    """
    out = _git(["status", "--porcelain", "--untracked-files=all", "--ignored"], dest)
    return [line[3:] for line in out.splitlines() if line.strip()]


def _download(src: Source, dest: Path, attempts: int = 3) -> None:
    last: GitError | None = None
    for attempt in range(attempts):
        try:
            _git(["fetch", "--quiet", "--depth", "1", "origin", src.commit], dest)
            _git(["checkout", "--quiet", "--detach", "--force", src.commit], dest)
            return
        except GitError as error:
            last = error
            time.sleep(2 * attempt)
    assert last is not None
    raise last


def fetch_source(src: Source, cache: Path, verify_only: bool = False) -> Result:
    dest = cache / src.name
    action = "present"
    try:
        if not (dest / ".git").exists():
            if verify_only:
                return Result(src.name, False, "missing", "not in the cache; run `specfirst fetch`")
            if dest.exists() and any(dest.iterdir()):
                return Result(src.name, False, "error", f"{dest} exists and is not a git clone")
            dest.mkdir(parents=True, exist_ok=True)
            _git(["init", "--quiet"], dest)
            _git(["remote", "add", "origin", src.url], dest)
            action = "fetched"
        head = head_commit(dest)
        if head != src.commit:
            if verify_only:
                return Result(src.name, False, "error", f"HEAD is {head}, pinned is {src.commit}")
            _download(src, dest)
            action = "fetched" if action == "fetched" else "updated"
            head = head_commit(dest)
        if head != src.commit:
            return Result(src.name, False, "error", f"HEAD is {head}, pinned is {src.commit}")
        changed = changed_paths(dest)
        if changed:
            detail = f"working tree is not clean: {len(changed)} path(s), first: {changed[0]}"
            return Result(src.name, False, "error", detail)
    except GitError as error:
        return Result(src.name, False, "error", str(error))
    return Result(src.name, True, action, src.commit)


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_file(pin: PinnedFile, cache: Path) -> Result:
    label = f"{pin.source}:{pin.path}"
    path = cache / pin.source / Path(*pin.path.split("/"))
    if not path.is_file():
        return Result(label, False, "missing", "file not found")
    actual = sha256_of(path)
    if actual != pin.sha256:
        return Result(label, False, "error", f"sha256 is {actual}, pinned is {pin.sha256}")
    return Result(label, True, "present", pin.sha256)


def fetch_all(
    manifest: Manifest,
    cache: Path,
    only: Iterable[str] | None = None,
    verify_only: bool = False,
    out: Callable[[str], None] = print,
) -> bool:
    """Fetch and verify. Returns True when every source and file is as pinned."""
    wanted = set(only) if only else None
    if wanted:
        unknown = sorted(wanted - {s.name for s in manifest.sources})
        if unknown:
            out(f"unknown source(s): {', '.join(unknown)}")
            return False
    out(f"cache: {cache}")
    ok = True
    for src in manifest.sources:
        if wanted and src.name not in wanted:
            continue
        result = fetch_source(src, cache, verify_only)
        ok = ok and result.ok
        mark = "ok  " if result.ok else "FAIL"
        out(f"{mark} {src.name:15s} {result.action:8s} {result.detail}  ({src.repository})")
    for pin in manifest.files:
        if wanted and pin.source not in wanted:
            continue
        result = verify_file(pin, cache)
        ok = ok and result.ok
        mark = "ok  " if result.ok else "FAIL"
        out(f"{mark} {result.name}  sha256 {result.detail}")
    out("fetch: every pin verified" if ok else "fetch: FAILED")
    return ok


def run(
    root: Path,
    only: Iterable[str] | None = None,
    verify_only: bool = False,
    out: Callable[[str], None] = print,
) -> int:
    manifest = load_manifest(manifest_path(root))
    return 0 if fetch_all(manifest, cache_dir(root), only, verify_only, out) else 1
