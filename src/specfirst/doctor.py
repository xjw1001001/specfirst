"""`specfirst doctor`: is this the environment the lock files describe?

Hard failures (exit 1): Python older than 3.12, a Python package that
differs from env/requirements.lock, R missing or not the version of
env/r-version.txt, an R package that differs from env/r-packages.lock, R or
one of its recommended packages (system packages named r-*) that differs
from env/system.lock, pdftotext missing or not poppler, CDISC CORE not
installed as env/core-source.txt and env/core-requirements.lock pin it
(specfirst.cdisccore). Differences in other
system packages are printed as notes only: the Ubuntu archive does not keep
old versions, so they cannot be pinned.
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

# A package name no repository has: the planted defect of the R load check.
NO_SUCH_R_PACKAGE = "specfirst.no.such.package"


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
        parts = line.split("#", 1)[0].split()
        if not parts:
            continue
        if len(parts) != 2:
            raise ValueError(f"{path.name}: expected a name and a version, found {line!r}")
        table[parts[0]] = parts[1]
    return table


def _two_words(path: Path) -> dict[str, str]:
    """Like read_table, for a file that may not be well formed: bad lines are left out."""
    lines = (line.split("#", 1)[0].split() for line in path.read_text("ascii").splitlines())
    return {parts[0]: parts[1] for parts in lines if len(parts) == 2}


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


def table_drift(lock: dict[str, str], installed: dict[str, str], extra_is_drift: bool) -> list[str]:
    """Differences between a lock and what is installed, as readable lines."""
    problems = []
    for name, version in sorted(lock.items()):
        if name not in installed:
            problems.append(f"{name}: not installed, lock has {version}")
        elif installed[name] != version:
            problems.append(f"{name}: installed {installed[name]}, lock has {version}")
    if extra_is_drift:
        problems += [f"{name}: installed {installed[name]}, not in the lock"
                     for name in sorted(set(installed) - set(lock))]
    return problems


def r_version_problem(installed: str | None, pinned: str) -> str | None:
    if installed is None:
        return "R is not installed"
    if installed != pinned:
        return f"R is {installed}, env/r-version.txt pins {pinned}"
    return None


def pdftotext_problem(version_output: str | None) -> str | None:
    """`version_output` is what `pdftotext -v` prints, or None when it is not installed."""
    if version_output is None:
        return "pdftotext (poppler-utils) is not installed"
    if "poppler" not in version_output.lower():
        return "pdftotext is not poppler's; the CSR parsers need poppler"
    return None


def is_r_system_package(name: str) -> bool:
    """R itself and the recommended packages that come with it, as system packages."""
    return name.startswith(("r-base", "r-recommended", "r-cran-"))


def _output(argv: list[str]) -> str | None:
    """Everything a command prints (some tools print their version on stderr)."""
    if shutil.which(argv[0]) is None:
        return None
    done = subprocess.run(argv, capture_output=True, text=True)
    return done.stdout + done.stderr


def _first_line(argv: list[str]) -> str | None:
    text = _output(argv)
    if text is None:
        return None
    lines = text.strip().splitlines()
    return lines[0].strip() if lines else ""


def r_version() -> str | None:
    """The installed R version, for example "4.6.2"."""
    match = re.search(r"R version (\d+\.\d+\.\d+)", _first_line(["R", "--version"]) or "")
    return match.group(1) if match else None


def pinned_r_version(root: Path) -> str:
    """The R version of env/r-version.txt, without the package revision."""
    return read_list(root / "env" / "r-version.txt")[0].split("-")[0]


def r_library(root: Path) -> dict[str, str] | None:
    """Packages in the project's R library, or None when R cannot list it."""
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
    installed = r_library(root)
    if installed is None:
        return ["Rscript could not list the project library"]
    return table_drift(read_table(root / "env" / "r-packages.lock"), installed, extra_is_drift=True)


def system_packages(names: list[str]) -> dict[str, str]:
    """Installed versions of Debian packages; a missing one is left out."""
    found: dict[str, str] = {}
    for name in names:
        done = subprocess.run(
            ["dpkg-query", "-W", "-f=${db:Status-Abbrev}${Version}", name],
            capture_output=True,
            text=True,
        )
        if done.returncode == 0 and done.stdout.startswith("ii "):
            found[name] = done.stdout[3:].strip()
    return found


def load_r_packages(root: Path, out: Callable[[str], None] = print) -> bool:
    """Load every package of env/r-packages.txt in R. This is a gate check.

    The check first proves itself on a planted defect (rule R5): it must
    fail for a package that does not exist.
    """
    packages = read_list(root / "env" / "r-packages.txt")
    if shutil.which("Rscript") is None:
        out("Rscript not found")
        return False
    script = str(root / "env" / "check_r.R")
    planted = subprocess.run(
        ["Rscript", "--vanilla", script, NO_SUCH_R_PACKAGE], capture_output=True, text=True
    )
    if planted.returncode == 0:
        out(f"the check did not fail for the planted package {NO_SUCH_R_PACKAGE}")
        return False
    out(f"planted defect: the check fails for {NO_SUCH_R_PACKAGE} (exit {planted.returncode})")
    done = subprocess.run(
        ["Rscript", "--vanilla", script, *packages], capture_output=True, text=True
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
    problem = r_version_problem(r, pinned_r_version(root))
    if problem:
        failures.append(problem)
    if r is not None:
        r_lock = root / "env" / "r-packages.lock"
        if not r_lock.is_file():
            failures.append("env/r-packages.lock is missing")
        else:
            drift = r_drift(root)
            out(f"R lock: {len(read_table(r_lock))} packages pinned, {len(drift)} differ")
            failures += drift

    pdftotext = _output(["pdftotext", "-v"])
    out(f"pdftotext  {(pdftotext or 'not found').strip().splitlines()[0]}")
    problem = pdftotext_problem(pdftotext)
    if problem:
        failures.append(problem)
    out(f"git        {_first_line(['git', '--version']) or 'not found'}")

    from specfirst import cdisccore

    if (root / cdisccore.SOURCE_FILE).is_file():
        drift = cdisccore.drift(root)
        pins = _two_words(root / cdisccore.SOURCE_FILE)
        out(f"CDISC CORE {pins.get('tag', '?')} at {pins.get('commit', '?')[:12]}: "
            f"{len(drift)} differ")
        failures += drift
    else:
        failures.append(f"{cdisccore.SOURCE_FILE} is missing")

    system_lock = root / "env" / "system.lock"
    if system_lock.is_file() and shutil.which("dpkg-query"):
        pinned = read_table(system_lock)
        drift = table_drift(pinned, system_packages(sorted(pinned)), extra_is_drift=False)
        hard = [line for line in drift if is_r_system_package(line.split(":", 1)[0])]
        out(f"system lock: {len(pinned)} packages recorded, {len(drift)} differ")
        failures += hard
        for line in drift:
            if line not in hard:
                out(f"note: system package {line}")

    for failure in failures:
        out(f"FAIL {failure}")
    out("doctor: " + ("FAILED" if failures else "ok"))
    return 1 if failures else 0
