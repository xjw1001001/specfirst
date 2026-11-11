"""Small tools: paths, the lock readers of doctor, status, the command line, the worktree script."""

from __future__ import annotations

import shutil
import subprocess
import sys

import pytest

from specfirst import cli, doctor, status
from specfirst.paths import cache_dir, repo_root


def checkout(tmp_path):
    (tmp_path / "third_party").mkdir()
    (tmp_path / "PLAN.md").write_text("plan\n", encoding="ascii")
    (tmp_path / "third_party" / "sources.yaml").write_text("sources: []\n", encoding="ascii")
    return tmp_path


def test_repo_root_is_found_from_a_subfolder(tmp_path, monkeypatch):
    monkeypatch.delenv("SPECFIRST_ROOT", raising=False)
    root = checkout(tmp_path)
    (root / "a" / "b").mkdir(parents=True)
    assert repo_root(root / "a" / "b") == root.resolve()


def test_cache_dir_order(tmp_path, monkeypatch):
    root = checkout(tmp_path)
    monkeypatch.delenv("SPECFIRST_CACHE", raising=False)
    assert cache_dir(root) == root / "third_party" / "cache"
    (root / "third_party" / "cache-location").write_text("../../main/third_party/cache\n", "ascii")
    assert cache_dir(root) == (root.parent / "main" / "third_party" / "cache").resolve()
    monkeypatch.setenv("SPECFIRST_CACHE", str(tmp_path / "elsewhere"))
    assert cache_dir(root) == (tmp_path / "elsewhere").resolve()


def test_read_requirements_lock(tmp_path):
    lock = tmp_path / "requirements.lock"
    lock.write_text(
        "# comment\n"
        "numpy==2.5.4 \\\n"
        "    --hash=sha256:aaaa \\\n"
        "    --hash=sha256:bbbb\n"
        "    # via pandas\n"
        "PyYAML==6.0.3 ; python_version >= '3.8'\n",
        encoding="ascii",
    )
    assert doctor.read_requirements_lock(lock) == {"numpy": "2.5.4", "PyYAML": "6.0.3"}


def test_python_drift_reports_planted_differences():
    installed = pytest.__version__
    assert doctor.python_drift({"pytest": installed}) == []
    assert doctor.python_drift({"pytest": "0.0.1"}) == [
        f"pytest: installed {installed}, lock has 0.0.1"
    ]
    assert doctor.python_drift({"no-such-package-xyz": "1.0"}) == [
        "no-such-package-xyz: not installed, lock has 1.0"
    ]


def test_read_table_and_list(tmp_path):
    table = tmp_path / "t.lock"
    table.write_text("# header\ncards 0.7.0\nmmrm\t0.3.15  # note\n\n", encoding="ascii")
    assert doctor.read_table(table) == {"cards": "0.7.0", "mmrm": "0.3.15"}
    assert doctor.read_list(table) == ["cards 0.7.0", "mmrm\t0.3.15"]


def test_pinned_r_version_is_the_one_the_lock_was_resolved_with(root):
    pinned = doctor.pinned_r_version(root)
    assert tuple(int(part) for part in pinned.split(".")) >= (4, 2)  # PLAN.md: R 4.2 or later
    header = (root / "env" / "r-packages.lock").read_text(encoding="ascii").splitlines()[:2]
    assert any(f"R version {pinned} " in line for line in header)


def test_python_lock_has_the_pins_of_the_plan(root):
    pins = doctor.read_requirements_lock(root / "env" / "requirements.lock")
    planned = {"yamaa": "0.7.0", "polars": "1.44.2", "pyarrow": "25.0.1", "pyyaml": "6.0.3"}
    lower = {name.lower(): version for name, version in pins.items()}
    for name, version in planned.items():
        assert lower.get(name) == version, name


def test_status_prints_every_track(root):
    lines: list[str] = []
    assert status.run(root, lines.append) == 0
    text = "\n".join(lines)
    for track in ("base", "real", "std", "gen", "read"):
        assert f"==> docs/state/{track}.md <==" in text


def test_status_without_state_files(tmp_path):
    assert status.run(tmp_path, lambda line: None) == 1


def test_command_line(root, monkeypatch, capsys):
    monkeypatch.setenv("SPECFIRST_ROOT", str(root))
    assert cli.main(["status"]) == 0
    assert "docs/state/base.md" in capsys.readouterr().out
    assert cli.main(["gate", "no-such-wp"]) == 2
    with pytest.raises(SystemExit):
        cli.main(["no-such-command"])


@pytest.mark.skipif(sys.platform == "win32", reason="the worktree script is a bash script")
def test_worktree_script(root, tmp_path, git):
    main = tmp_path / "specfirst"
    (main / "scripts").mkdir(parents=True)
    shutil.copy(root / "scripts" / "worktree.sh", main / "scripts" / "worktree.sh")
    git(main, "init", "--quiet", "-b", "main")
    git(main, "add", ".")
    git(main, "commit", "--quiet", "-m", "first")

    def worktree(*args):
        return subprocess.run(
            ["bash", "scripts/worktree.sh", *args], cwd=main, capture_output=True, text=True
        )

    done = worktree("real")
    assert done.returncode == 0, done.stderr
    tree = tmp_path / "specfirst-real"
    assert git(tree, "branch", "--show-current") == "track/real"
    location = (tree / "third_party" / "cache-location").read_text(encoding="ascii").strip()
    assert location == "../../specfirst/third_party/cache"

    again = worktree("real")
    assert again.returncode == 0 and "already" in again.stdout
    assert worktree("nonsense").returncode == 2
    assert worktree().returncode == 2
