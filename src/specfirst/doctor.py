"""`specfirst doctor`: is this the environment the lock files describe?

Hard failures (exit 1): Python older than 3.12, a Python package that
differs from env/requirements.lock, R missing or older than 4.2, an R
package that differs from env/r-packages.lock, pdftotext missing or not
poppler. Differences in system packages are printed as notes only.
"""

from __future__ import annotations

import importlib.metadata
import re
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

_PIN = re.compile(r"^([A-Za-z0-9][A-Za-z0-9_.-]*)==([^\s\\;]+)")


def read_requirements_lock(path: Path) -> dict[str, str]:
    """Package name to pinned version, from a pip requirements file."""
    pins: dict[str, str] = {}
    for line in path.read_text(encoding="ascii").splitlines():
        match = _PIN.match(line.strip())
        if match:
            pins[match.group(1)] = match.group(2)
    return pins


def read_table(path: Path) -> dict[str, str]:
    """Name to version from a two-column file; '#' starts a comment."""
    table: dict[str, str] = {}
    for line in path.read_text(encoding="ascii").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            name, version = line.split()
            table[name] = version
    return table


def read_list(path: Path) -> list[str]:
    """One name per line; '#' starts a comment."""
    text = path.read_text(encoding="ascii")
    lines = (line.split("#", 1)[0].strip() for line in text.splitlines())
    return [line for line in lines if line]


def python_drift(pins: dict[str, str]) -> list[str]:
    problems = []
    for name, version in sorted(pins.items()):
        try:
            installed = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            problems.append(f"{name}: not installed, lock has {version}")
            continue
        if installed != version:
            problems.append(f"{name}: installed {installed}, lock has {version}")
    return problems


def _first_line(argv: list[str]) -> str | None:
    """First output line of a command (some tools print their version on stderr)."""
    if shutil.which(argv[0]) is None:
        return None
    done = subprocess.run(argv, capture_output=True, text=True)
    lines = (done.stdout + done.stderr).strip().splitlines()
    return lines[0].strip() if lines else ""


def r_version() -> tuple[int, int] | None:
    line = _first_line(["R", "--version"])
    match = re.search(r"R version (\d+)\.(\d+)", line or "")
    return (int(match.group(1)), int(match.group(2))) if match else None


def r_library(root: Path) -> dict[str, str] | None:
    """Packages in the project's R library, or None when R cannot be run."""
    if shutil.which("Rscript") is None:
        return None
    done = subprocess.run(
        ["Rscript", "--vanilla", str(root / "env" / "check_r.R"), "--list"],
        capture_output=True,
        text=True,
    )
    if done.returncode != 0:
        return None
    return dict(line.split("\t") for line in done.stdout.splitlines() if "\t" in line)


def r_drift(root: Path) -> list[str]:
    lock = read_table(root / "env" / "r-packages.lock")
    installed = r_library(root)
    if installed is None:
        return ["Rscript could not list the project library"]
    problems = []
    for name, version in sorted(lock.items()):
        if name not in installed:
            problems.append(f"{name}: not installed, lock has {version}")
        elif installed[name] != version:
            problems.append(f"{name}: installed {installed[name]}, lock has {version}")
    problems += [f"{name}: installed {installed[name]}, not in the lock"
                 for name in sorted(set(installed) - set(lock))]
    return problems


def load_r_packages(root: Path, out: Callable[[str], None] = print) -> bool:
    """Load every package of env/r-packages.txt in R. This is a gate check."""
    packages = read_list(root / "env" / "r-packages.txt")
    if shutil.which("Rscript") is None:
        out("Rscript not found")
        return False
    done = subprocess.run(
        ["Rscript", "--vanilla", str(root / "env" / "check_r.R"), *packages],
        capture_output=True,
        text=True,
    )
    for line in (done.stdout + done.stderr).splitlines():
        out(line)
    return done.returncode == 0


def run(root: Path, out: Callable[[str], None] = print) -> int:
    failures: list[str] = []

    version = sys.version_info
    out(f"python     {version.major}.{version.minor}.{version.micro}  ({sys.executable})")
    if version < (3, 12):
        failures.append("Python 3.12 or later is required")

    lock = root / "env" / "requirements.lock"
    pins = read_requirements_lock(lock) if lock.is_file() else {}
    if not pins:
        failures.append("env/requirements.lock is missing or empty")
    drift = python_drift(pins)
    out(f"python lock: {len(pins)} packages pinned, {len(drift)} differ")
    failures += drift

    r = r_version()
    out(f"R          {_first_line(['R', '--version']) or 'not found'}")
    if r is None:
        failures.append("R is not installed")
    else:
        if r < (4, 2):
            failures.append("R 4.2 or later is required")
        r_lock = root / "env" / "r-packages.lock"
        if not r_lock.is_file():
            failures.append("env/r-packages.lock is missing")
        else:
            drift = r_drift(root)
            out(f"R lock: {len(read_table(r_lock))} packages pinned, {len(drift)} differ")
            failures += drift

    pdftotext = _first_line(["pdftotext", "-v"])
    out(f"pdftotext  {pdftotext or 'not found'}")
    if pdftotext is None:
        failures.append("pdftotext (poppler-utils) is not installed")
    else:
        done = subprocess.run(["pdftotext", "-v"], capture_output=True, text=True)
        if "poppler" not in (done.stdout + done.stderr).lower():
            failures.append("pdftotext is not poppler's; the CSR parsers need poppler")
    out(f"git        {_first_line(['git', '--version']) or 'not found'}")

    system_lock = root / "env" / "system.lock"
    if system_lock.is_file() and shutil.which("dpkg-query"):
        for name, version in sorted(read_table(system_lock).items()):
            done = subprocess.run(
                ["dpkg-query", "-W", "-f=${Version}", name], capture_output=True, text=True
            )
            installed = done.stdout.strip() if done.returncode == 0 else "not installed"
            if installed != version:
                out(f"note: system package {name} is {installed}, env/system.lock has {version}")

    for failure in failures:
        out(f"FAIL {failure}")
    out("doctor: " + ("FAILED" if failures else "ok"))
    return 1 if failures else 0
