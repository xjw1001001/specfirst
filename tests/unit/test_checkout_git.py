"""git in a checkout that the other operating system's git made.

The owner's checkouts are on a Windows drive: Windows git makes the track
worktrees, and the code runs under WSL. A worktree's `.git` file then holds
a Windows path (`gitdir: D:/...`) that Linux git cannot follow. The planted
defect here is exactly that file.
"""

from __future__ import annotations

import os

import pytest

from specfirst import asciicheck, gates
from specfirst.paths import git_env

posix_only = pytest.mark.skipif(
    os.name != "posix", reason="simulates WSL reading a Windows worktree"
)


def test_plain_checkout_needs_no_translation(repo):
    assert git_env(repo) == {"GIT_OPTIONAL_LOCKS": "0"}


@pytest.fixture
def windows_worktree(tmp_path, git, monkeypatch):
    """A worktree whose `.git` file is written the way Windows git writes it.

    The repository is at <tmp>/q/main, which plays the Windows path Q:/main,
    with <tmp> playing the folder where WSL mounts the drives.
    """
    main = tmp_path / "q" / "main"
    main.mkdir(parents=True)
    git(main, "init", "--quiet", "-b", "main")
    (main / "README.md").write_bytes(b"demo\n")
    git(main, "add", "README.md")
    git(main, "commit", "--quiet", "-m", "first")
    tree = tmp_path / "q" / "main-real"
    git(main, "worktree", "add", "--quiet", "-b", "track/real", str(tree))
    (tree / ".git").write_text("gitdir: Q:/main/.git/worktrees/main-real\n", encoding="ascii")
    monkeypatch.delenv("SPECFIRST_DRIVE_MOUNT", raising=False)
    return tree


@posix_only
def test_linux_git_cannot_read_a_windows_worktree_by_itself(windows_worktree, git):
    """The defect, unhandled: this is what the code met before git_env existed."""
    assert git_env(windows_worktree) == {"GIT_OPTIONAL_LOCKS": "0"}  # the drive is not mounted
    with pytest.raises(RuntimeError, match="git ls-files failed"):
        asciicheck.maintained_files(windows_worktree)
    assert gates.head(windows_worktree) == ("unknown", None)


@posix_only
def test_windows_worktree_is_usable_once_the_drive_is_found(
    windows_worktree, tmp_path, git, monkeypatch
):
    monkeypatch.setenv("SPECFIRST_DRIVE_MOUNT", str(tmp_path))
    env = git_env(windows_worktree)
    assert env["GIT_DIR"] == str(tmp_path / "q" / "main" / ".git" / "worktrees" / "main-real")
    assert env["GIT_WORK_TREE"] == str(windows_worktree)

    assert asciicheck.maintained_files(windows_worktree) == ["README.md"]
    commit, clean = gates.head(windows_worktree)
    assert commit == git(tmp_path / "q" / "main", "rev-parse", "track/real")
    assert clean is True

    (windows_worktree / "notes.md").write_bytes(b"caf\xc3\xa9\n")
    lines: list[str] = []
    assert asciicheck.check(windows_worktree, lines.append) == 1
    assert "notes.md:1:4: non-ASCII byte 0xc3" in lines
    assert gates.head(windows_worktree)[1] is False


@posix_only
def test_native_worktree_needs_no_translation(tmp_path, git):
    main = tmp_path / "main"
    main.mkdir()
    git(main, "init", "--quiet", "-b", "main")
    (main / "README.md").write_bytes(b"demo\n")
    git(main, "add", "README.md")
    git(main, "commit", "--quiet", "-m", "first")
    tree = tmp_path / "main-std"
    git(main, "worktree", "add", "--quiet", "-b", "track/std", str(tree))
    assert git_env(tree) == {"GIT_OPTIONAL_LOCKS": "0"}
    assert asciicheck.maintained_files(tree) == ["README.md"]
