"""Where things live: the checkout root, the fetch cache, and git in a checkout."""

from __future__ import annotations

import os
import re
import shlex
import sys
from pathlib import Path

_WINDOWS_PATH = re.compile(r"^([A-Za-z]):[\\/](.*)$")


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


def _other_system_path(target: str) -> Path | None:
    """A path written by the other operating system's git, as this one names it.

    Under Linux, `D:/a/b` is `/mnt/d/a/b` (WSL mounts the Windows drives
    there; SPECFIRST_DRIVE_MOUNT names another mount point). Under Windows,
    `/mnt/d/a/b` is `D:/a/b`.
    """
    mount = os.environ.get("SPECFIRST_DRIVE_MOUNT", "/mnt").rstrip("/")
    if os.name == "posix":
        match = _WINDOWS_PATH.match(target)
        if match:
            return Path(mount) / match.group(1).lower() / match.group(2).replace("\\", "/")
        return None
    match = re.match(rf"^{re.escape(mount)}/([A-Za-z])/(.*)$", target)
    if match:
        return Path(f"{match.group(1).upper()}:/{match.group(2)}")
    return None


def git_env(root: Path) -> dict[str, str]:
    """Extra environment for running git in the checkout `root`.

    A linked worktree names its git folder by an absolute path, written in
    the form of the git that made it. A worktree made by Windows git is
    therefore not a repository to Linux git under WSL, and the reverse. In
    that case this returns GIT_DIR and GIT_WORK_TREE with the path as this
    system names it, so that git works all the same. Otherwise it returns
    nothing. GIT_OPTIONAL_LOCKS=0 is always set: reading the state of a
    checkout must not rewrite its index.
    """
    env = {"GIT_OPTIONAL_LOCKS": "0"}
    dotgit = root / ".git"
    if not dotgit.is_file():
        return env
    text = dotgit.read_text(encoding="utf-8", errors="replace").strip()
    if not text.startswith("gitdir:"):
        return env
    target = text[len("gitdir:"):].strip()
    native = Path(target)
    if not native.is_absolute():
        native = root / native
    if native.is_dir():
        return env
    translated = _other_system_path(target)
    if translated is not None and translated.is_dir():
        env["GIT_DIR"] = str(translated)
        env["GIT_WORK_TREE"] = str(root)
    return env


def main() -> int:
    """Print `export NAME=value` lines for git in the current checkout (for shell scripts)."""
    for name, value in sorted(git_env(repo_root()).items()):
        print(f"export {name}={shlex.quote(value)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
