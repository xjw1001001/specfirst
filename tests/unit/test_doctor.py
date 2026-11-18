"""`specfirst doctor` and the R load check, with planted drift (rule R5).

The functions that decide are tested on planted values. The R load check
is tested with a stand-in `Rscript`, so that the test needs no R.
"""

from __future__ import annotations

import os
import stat

import pytest

from specfirst import doctor

LOCK = {"cards": "0.9.0", "mmrm": "0.3.19"}
BACKSLASH, NEWLINE = chr(92), chr(10)


def test_table_drift_is_empty_when_everything_matches():
    assert doctor.table_drift(LOCK, dict(LOCK), extra_is_drift=True) == []


@pytest.mark.parametrize(
    "installed, expected",
    [
        ({"cards": "0.9.0", "mmrm": "0.3.20"}, ["mmrm: installed 0.3.20, lock has 0.3.19"]),
        ({"cards": "0.9.0"}, ["mmrm: not installed, lock has 0.3.19"]),
        ({**LOCK, "lme4": "1.1-38"}, ["lme4: installed 1.1-38, not in the lock"]),
    ],
)
def test_table_drift_reports_planted_differences(installed, expected):
    assert doctor.table_drift(LOCK, installed, extra_is_drift=True) == expected


def test_an_extra_system_package_is_not_drift():
    assert doctor.table_drift(LOCK, {**LOCK, "vim": "9.1"}, extra_is_drift=False) == []


def test_r_drift_uses_the_project_library(root, monkeypatch):
    locked = doctor.read_table(root / "env" / "r-packages.lock")
    monkeypatch.setattr(doctor, "r_library", lambda _root: dict(locked))
    assert doctor.r_drift(root) == []
    planted = {**locked, "cards": "0.0.1"}
    monkeypatch.setattr(doctor, "r_library", lambda _root: planted)
    assert doctor.r_drift(root) == [f"cards: installed 0.0.1, lock has {locked['cards']}"]
    monkeypatch.setattr(doctor, "r_library", lambda _root: None)
    assert doctor.r_drift(root) == ["Rscript could not list the project library"]


def test_r_version_must_be_the_pinned_one():
    assert doctor.r_version_problem("4.6.2", "4.6.2") is None
    assert doctor.r_version_problem("4.3.3", "4.6.2") == "R is 4.3.3, env/r-version.txt pins 4.6.2"
    assert doctor.r_version_problem(None, "4.6.2") == "R is not installed"


def test_pdftotext_must_be_poppler():
    poppler = "pdftotext version 24.02.0\nCopyright 2005-2024 The Poppler Developers\n"
    xpdf = "pdftotext version 4.00\nCopyright 1996-2017 Glyph & Cog, LLC\n"
    assert doctor.pdftotext_problem(poppler) is None
    assert "not poppler" in doctor.pdftotext_problem(xpdf)
    assert "not installed" in doctor.pdftotext_problem(None)


def test_r_system_packages_are_the_hard_ones():
    for name in ("r-base-core", "r-recommended", "r-cran-matrix"):
        assert doctor.is_r_system_package(name)
    for name in ("poppler-utils", "python3", "curl"):
        assert not doctor.is_r_system_package(name)


def test_system_lock_pins_r_and_its_recommended_packages(root):
    pinned = doctor.read_table(root / "env" / "system.lock")
    version = (root / "env" / "r-version.txt").read_text(encoding="ascii").split()[-1]
    assert pinned["r-base-core"] == version
    for name in ("r-cran-matrix", "r-cran-mass", "r-cran-nlme", "r-cran-survival"):
        assert name in pinned


def test_the_listed_r_packages_are_the_seven_of_the_plan(root):
    listed = doctor.read_list(root / "env" / "r-packages.txt")
    assert listed == ["cards", "cardx", "siera", "emmeans", "mmrm", "coin", "car"]
    locked = doctor.read_table(root / "env" / "r-packages.lock")
    assert set(listed) <= set(locked)


def test_python_lock_has_the_versions_of_the_plan(root):
    pins = doctor.read_requirements_lock(root / "env" / "requirements.lock")
    lower = {name.lower(): version for name, version in pins.items()}
    planned = {  # PLAN.md section 3.1 and the sandbox of appendix A
        "yamaa": "0.7.0", "polars": "1.44.2", "pyarrow": "25.0.1", "pyyaml": "6.0.3",
        "pandas": "3.1.1", "scipy": "1.18.1", "numpy": "2.5.4",
    }
    for name, version in planned.items():
        assert lower.get(name) == version, name
    lock_text = (root / "env" / "requirements.lock").read_text(encoding="ascii")
    assert lock_text.count("--hash=sha256:") >= len(pins)  # every pin carries a hash


# ---- the R load check, with a stand-in Rscript ------------------------------

FAKE_RSCRIPT = """#!/bin/sh
# Stand-in for Rscript: "loads" every package named after the script, and
# fails for the names listed in FAKE_R_MISSING, the way env/check_r.R does.
shift 2
status=0
for package in "$@"; do
  case " $FAKE_R_MISSING " in
    *" $package "*) echo "$package FAILED TO LOAD"; status=1 ;;
    *) echo "$package 1.0" ;;
  esac
done
exit $status
"""


@pytest.fixture
def fake_rscript(tmp_path, monkeypatch):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    script = bin_dir / "Rscript"
    script.write_text(FAKE_RSCRIPT, encoding="ascii", newline="\n")
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")

    def run(missing: str):
        monkeypatch.setenv("FAKE_R_MISSING", missing)
        lines: list[str] = []
        from specfirst.paths import repo_root

        return doctor.load_r_packages(repo_root(), lines.append), "\n".join(lines)

    return run


posix_only = pytest.mark.skipif(os.name != "posix", reason="the stand-in Rscript is a shell script")


@posix_only
def test_r_check_passes_when_every_package_loads(fake_rscript):
    ok, text = fake_rscript(doctor.NO_SUCH_R_PACKAGE)
    assert ok
    assert f"planted defect: the check fails for {doctor.NO_SUCH_R_PACKAGE}" in text
    assert "mmrm 1.0" in text


@posix_only
def test_r_check_fails_when_a_listed_package_does_not_load(fake_rscript):
    ok, text = fake_rscript(f"{doctor.NO_SUCH_R_PACKAGE} mmrm")
    assert not ok and "mmrm FAILED TO LOAD" in text


@posix_only
def test_r_check_that_cannot_fail_is_rejected(fake_rscript):
    """A checker that accepts the planted missing package proves nothing."""
    ok, text = fake_rscript("")
    assert not ok and "did not fail for the planted package" in text


def test_r_check_fails_without_rscript(root, monkeypatch, tmp_path):
    monkeypatch.setenv("PATH", str(tmp_path))
    lines: list[str] = []
    assert doctor.load_r_packages(root, lines.append) is False
    assert lines == ["Rscript not found"]


# -- env/lock.sh (review of gen-1a, findings F1 and F28) -----------------------------


def test_the_lock_script_writes_every_lock_the_doctor_reads(root):
    text = (root / doctor.LOCK_SCRIPT).read_text(encoding="ascii")
    assert doctor.lock_script_problems(text, root) == []
    assert set(doctor.LOCKS) == {"env/requirements.lock", "env/core-requirements.lock",
                                 "env/r-packages.lock", "env/system.lock"}
    for lock in doctor.LOCKS:
        assert (root / lock).is_file(), lock
    # The two commands of uv are read as one command each, options included.
    compiles = [c for c in doctor.shell_commands(text) if " pip compile " in c]
    assert len(compiles) == 2 and all("--output-file env/" in c for c in compiles)


def test_a_broken_lock_script_is_seen(root):
    """Planted: the defects that `bash -n` accepts. The first is the one that was committed."""
    text = (root / doctor.LOCK_SCRIPT).read_text(encoding="ascii")
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if "pip compile env/core-requirements.in"
                 in line)
    stop = next(i for i in range(start, len(lines)) if not lines[i].endswith(BACKSLASH))
    # As committed before the review of gen-1a: one line with the characters backslash
    # and n where the line breaks were meant.
    one_line = (" " + BACKSLASH + "n").join(
        line.rstrip(BACKSLASH).strip() for line in lines[start:stop + 1])
    broken = NEWLINE.join([*lines[:start], one_line, *lines[stop + 1:]]) + NEWLINE
    found = doctor.lock_script_problems(broken, root)
    assert found and found[0].startswith("a backslash inside a line, outside quotes")
    # A continuation that lost its backslash: the options become commands of their own.
    broken = text.replace("--generate-hashes " + BACKSLASH + NEWLINE,
                          "--generate-hashes" + NEWLINE, 1)
    found = doctor.lock_script_problems(broken, root)
    assert any(line.startswith("a command starts with an option") for line in found)
    assert "0 `pip compile` commands write env/requirements.lock, not one" in found
    # A blank after the backslash.
    broken = text.replace("--no-annotate " + BACKSLASH + NEWLINE,
                          "--no-annotate " + BACKSLASH + " " + NEWLINE, 1)
    assert any("followed by blanks" in line for line in doctor.lock_script_problems(broken, root))
    # A lock that no command writes, a lock without hashes, a lock from another input.
    assert "no command writes env/system.lock" in doctor.lock_script_problems(
        text.replace("env/system.lock", "env/system.txt"), root)
    broken = text.replace("  --generate-hashes " + BACKSLASH + NEWLINE, "", 1)
    assert doctor.lock_script_problems(broken, root) == [
        "env/requirements.lock is written without hashes"]
    broken = text.replace("pip compile env/core-requirements.in", "pip compile env/core.in")
    assert doctor.lock_script_problems(broken, root) == [
        "env/core-requirements.lock is not resolved from env/core.in"
        .replace("core.in", "core-requirements.in")]


def test_the_doctor_reads_the_lock_script(root):
    """The first check of every gate fails on a lock script that cannot write a lock."""
    said: list[str] = []
    doctor.run(root, said.append)
    assert f"lock script: {doctor.LOCK_SCRIPT} writes 4 lock files, 0 problems" in said
