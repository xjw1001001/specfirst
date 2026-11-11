"""Shared fixtures."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from specfirst.paths import repo_root


@pytest.fixture(scope="session")
def root() -> Path:
    return repo_root(Path(__file__).resolve().parent)


@pytest.fixture
def git(tmp_path, monkeypatch):
    """Run git in a sandbox: no user or system configuration, a fixed identity.

    The variables are set in the environment, so code under test that calls
    git sees the same sandbox.
    """
    config = tmp_path / "gitconfig-empty"
    config.write_text("", encoding="ascii")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(config))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    for role in ("AUTHOR", "COMMITTER"):
        monkeypatch.setenv(f"GIT_{role}_NAME", "Test")
        monkeypatch.setenv(f"GIT_{role}_EMAIL", "test@example.invalid")
        monkeypatch.setenv(f"GIT_{role}_DATE", "2026-01-01T00:00:00+00:00")

    def run(cwd: Path, *args: str) -> str:
        done = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
        assert done.returncode == 0, f"git {' '.join(args)}: {done.stderr}"
        return done.stdout.strip()

    return run


@pytest.fixture
def repo(tmp_path, git) -> Path:
    """An empty git repository on branch main with one commit."""
    path = tmp_path / "repo"
    path.mkdir()
    git(path, "init", "--quiet", "-b", "main")
    (path / "README.md").write_bytes(b"demo\n")
    git(path, "add", "README.md")
    git(path, "commit", "--quiet", "-m", "first")
    return path
