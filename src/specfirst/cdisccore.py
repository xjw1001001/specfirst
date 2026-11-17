"""CDISC CORE in the environment (docs/decisions/ADR-006.md).

CORE (the CDISC Rules Engine) checks the SDTM that the generator writes
(PLAN.md section 6.4, stage S4). It runs from source: the repository at the
commit of env/core-source.txt, with the rules, the controlled terminology
and the library metadata that the repository ships at that commit, in a
virtual environment of its own built from env/core-requirements.lock.

    python -m specfirst.cdisccore install    what env/install.sh runs
    specfirst doctor                         checks both parts for drift

Both parts live in one folder named after the two pins, so checkouts with
the same pins share it and a change of a pin never reuses an old install.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from specfirst import fetch
from specfirst.sources import Source

SOURCE_FILE = "env/core-source.txt"
LOCK_FILE = "env/core-requirements.lock"
SDIST_FILE = "env/core-sdist.txt"

_COMMIT = re.compile(r"^[0-9a-f]{40}$")
_PIN = re.compile(r"^([A-Za-z0-9][A-Za-z0-9_.-]*)==([^\s\\;]+)")


class CoreError(RuntimeError):
    """CORE is not installed as pinned, or a run of it failed."""


@dataclass(frozen=True)
class Pin:
    repository: str
    tag: str
    commit: str
    lock_sha256: str

    @property
    def key(self) -> str:
        """The folder name of an install: both pins, shortened."""
        return f"{self.commit[:12]}-{self.lock_sha256[:12]}"

    @property
    def version(self) -> str:
        return self.tag.lstrip("v")


def _two_columns(path: Path) -> dict[str, str]:
    table: dict[str, str] = {}
    for line in path.read_text(encoding="ascii").splitlines():
        parts = line.split("#", 1)[0].split()
        if len(parts) == 2:
            table[parts[0]] = parts[1]
    return table


def read_pin(root: Path) -> Pin:
    table = _two_columns(root / SOURCE_FILE)
    commit = table.get("commit", "")
    if not _COMMIT.match(commit) or not table.get("repository") or not table.get("tag"):
        raise CoreError(f"{SOURCE_FILE} must name a repository, a tag and a 40-digit commit")
    lock = hashlib.sha256((root / LOCK_FILE).read_bytes()).hexdigest()
    return Pin(table["repository"], table["tag"], commit, lock)


def normalize(name: str) -> str:
    """A package name as PEP 503 compares it."""
    return re.sub(r"[-_.]+", "-", name).lower()


def read_lock(text: str) -> dict[str, str]:
    """Normalized package name to pinned version."""
    pins: dict[str, str] = {}
    for line in text.splitlines():
        match = _PIN.match(line.strip())
        if match:
            pins[normalize(match.group(1))] = match.group(2)
    return pins


def sdist_names(root: Path) -> set[str]:
    """Packages that have no wheel and are built from their pinned source archive."""
    path = root / SDIST_FILE
    if not path.is_file():
        return set()
    lines = (line.split("#", 1)[0].strip() for line in path.read_text("ascii").splitlines())
    return {normalize(line) for line in lines if line}


def split_lock(text: str, sdists: set[str]) -> tuple[str, str]:
    """The lock as two requirement files: packages with wheels, packages built from source.

    A requirement is its `name==version` line and the indented hash lines
    after it; comment lines are dropped.
    """
    wheels: list[str] = []
    sources: list[str] = []
    target = wheels
    for line in text.splitlines():
        if line.startswith("#") or not line.strip():
            continue
        match = _PIN.match(line)
        if match:
            target = sources if normalize(match.group(1)) in sdists else wheels
        target.append(line)
    return "\n".join(wheels) + "\n", ("\n".join(sources) + "\n" if sources else "")


def base_dir(root: Path) -> Path:
    """Where installs of CORE live: SPECFIRST_CORE (scripts/env.sh), else .core in the checkout."""
    env = os.environ.get("SPECFIRST_CORE")
    return Path(env).expanduser().resolve() if env else root / ".core"


def core_dir(root: Path) -> Path:
    return base_dir(root) / read_pin(root).key


def python_path(root: Path) -> Path:
    return core_dir(root) / "venv" / "bin" / "python"


def source_dir(root: Path) -> Path:
    return core_dir(root) / "src"


def _source(pin: Pin) -> Source:
    url = os.environ.get("SPECFIRST_CORE_URL") or f"https://github.com/{pin.repository}.git"
    return Source(name="src", title="CDISC CORE", repository=pin.repository, commit=pin.commit,
                  license="MIT", used_for="SDTM conformance checks", url=url)


def _run(argv: list[str], out: Callable[[str], None]) -> int:
    done = subprocess.run(argv, capture_output=True, text=True)
    for line in (done.stdout + done.stderr).splitlines():
        out(line)
    return done.returncode


def install(root: Path, out: Callable[[str], None] = print) -> int:
    """Create the environment of CORE and fetch its source, exactly as pinned."""
    pin = read_pin(root)
    home = core_dir(root)
    out(f"CDISC CORE {pin.tag}: {home}")
    python = python_path(root)
    if not python.is_file():
        home.mkdir(parents=True, exist_ok=True)
        if _run([sys.executable, "-m", "venv", str(home / "venv")], out) != 0:
            return 1
    wheels, sources = split_lock((root / LOCK_FILE).read_text("ascii"), sdist_names(root))
    pip = [str(python), "-m", "pip", "install", "--quiet", "--disable-pip-version-check",
           "--no-deps", "--require-hashes"]
    with tempfile.TemporaryDirectory() as scratch:
        # Wheels first: exact versions with hashes, nothing resolved or built.
        first = Path(scratch) / "wheels.txt"
        first.write_text(wheels, encoding="ascii")
        if _run([*pip, "--only-binary=:all:", "-r", str(first)], out) != 0:
            return 1
        if sources:
            # Then the few packages without a wheel, built from their pinned
            # archives with the setuptools that the first step installed.
            second = Path(scratch) / "sources.txt"
            second.write_text(sources, encoding="ascii")
            names = ",".join(sorted(read_lock(sources)))
            if _run([*pip, "--no-binary", names, "--no-build-isolation", "-r", str(second)],
                    out) != 0:
                return 1
    result = fetch.fetch_source(_source(pin), home)
    out(f"source: {result.action} {result.detail}")
    if not result.ok:
        return 1
    problems = drift(root)
    for problem in problems:
        out(f"FAIL {problem}")
    return 1 if problems else 0


def installed_packages(python: Path) -> dict[str, str] | None:
    """Normalized name to version of every package in the environment of CORE."""
    code = ("import importlib.metadata as m, json; "
            "print(json.dumps({d.metadata['Name']: d.version for d in m.distributions()}))")
    done = subprocess.run([str(python), "-I", "-c", code], capture_output=True, text=True)
    if done.returncode != 0:
        return None
    return {normalize(name): version for name, version in json.loads(done.stdout).items()}


def package_drift(lock: dict[str, str], installed: dict[str, str]) -> list[str]:
    """Differences between the lock and the environment. pip itself is not in a lock."""
    problems = []
    for name, version in sorted(lock.items()):
        if name not in installed:
            problems.append(f"CORE environment: {name} is not installed, lock has {version}")
        elif installed[name] != version:
            problems.append(
                f"CORE environment: {name} is {installed[name]}, lock has {version}")
    for name in sorted(set(installed) - set(lock) - {"pip"}):
        problems.append(f"CORE environment: {name} {installed[name]} is not in the lock")
    return problems


def source_problems(source: Path, commit: str) -> list[str]:
    """Why a folder is not the source of CORE at the pinned commit, untouched."""
    if not (source / ".git").exists():
        return [f"CORE source: not installed in {source}; run make install"]
    head = fetch.head_commit(source)
    if head != commit:
        return [f"CORE source: HEAD is {head}, {SOURCE_FILE} pins {commit}"]
    try:
        changed = fetch.changed_paths(source)
    except fetch.GitError as error:
        return [f"CORE source: {error}"]
    if changed:
        return [f"CORE source: the tree is not clean: {len(changed)} path(s), "
                f"first: {changed[0]}"]
    return []


def drift(root: Path) -> list[str]:
    """Everything in which the installed CORE differs from its pins (for `specfirst doctor`)."""
    try:
        pin = read_pin(root)
    except (CoreError, OSError) as error:
        return [f"CORE pins: {error}"]
    python = python_path(root)
    if not python.is_file():
        return [f"CORE environment: not installed in {core_dir(root)}; run make install"]
    installed = installed_packages(python)
    if installed is None:
        return ["CORE environment: its Python could not list the packages"]
    lock = read_lock((root / LOCK_FILE).read_text("ascii"))
    return package_drift(lock, installed) + source_problems(source_dir(root), pin.commit)


# -- running -------------------------------------------------------------------


@dataclass(frozen=True)
class Finding:
    """One line of a CORE report: a rule that reported issues, or failed to run, on a dataset."""

    rule: str
    dataset: str      # empty when the report names none
    message: str
    status: str       # ISSUE REPORTED | EXECUTION ERROR
    count: int = 0
    subjects: tuple[str, ...] = ()   # USUBJID of the records, where the report gives one
    variables: tuple[str, ...] = ()
    examples: tuple[dict, ...] = field(default=(), compare=False)


@dataclass(frozen=True)
class Report:
    path: Path
    engine: str                      # the version CORE says it is
    standard: str
    rules: dict[str, str]            # rule ID -> run status
    findings: tuple[Finding, ...]
    datasets: tuple[str, ...]

    def counts(self) -> dict[str, int]:
        """How many rules ended in each run status."""
        tally: dict[str, int] = {}
        for status in self.rules.values():
            tally[status] = tally.get(status, 0) + 1
        return dict(sorted(tally.items()))


ISSUE, EXECUTION_ERROR = "ISSUE REPORTED", "EXECUTION ERROR"


def read_report(path: Path) -> Report:
    """A JSON report of `core.py validate` as findings and rule statuses.

    A finding is a rule and a dataset. A rule that reported issues gives one
    finding per dataset of its issues; a rule that CORE could not execute
    gives one as well, whether or not the report lists details for it.
    """
    with open(path, encoding="utf-8") as handle:
        raw = json.load(handle)
    rules = {str(r.get("core_id", "")): str(r.get("status", ""))
             for r in raw.get("Rules_Report") or []}
    messages = {str(r.get("core_id", "")): str(r.get("message", ""))
                for r in raw.get("Rules_Report") or []}
    details: dict[tuple[str, str], list[dict]] = {}
    for detail in raw.get("Issue_Details") or []:
        key = (str(detail.get("core_id", "")), str(detail.get("dataset", "") or ""))
        details.setdefault(key, []).append(detail)
    counts = {(str(s.get("core_id", "")), str(s.get("dataset", "") or "")):
              int(s.get("issues", 0) or 0) for s in raw.get("Issue_Summary") or []}
    keys = sorted(set(details) | set(counts))
    reported = {rule for rule, _ in keys}
    keys += [(rule, "") for rule, status in sorted(rules.items())
             if status in (ISSUE, EXECUTION_ERROR) and rule not in reported]
    findings = []
    for rule, dataset in keys:
        rows = details.get((rule, dataset), [])
        status = rules.get(rule, ISSUE)
        if status not in (ISSUE, EXECUTION_ERROR):
            status = ISSUE
        message = str(rows[0].get("message", "")) if rows else messages.get(rule, "")
        findings.append(Finding(
            rule=rule, dataset=dataset, message=message, status=status,
            count=counts.get((rule, dataset), len(rows)),
            subjects=tuple(sorted({str(r["USUBJID"]) for r in rows if r.get("USUBJID")})),
            variables=tuple(sorted({str(v) for r in rows for v in (r.get("variables") or [])})),
            examples=tuple(rows[:3])))
    conformance = raw.get("Conformance_Details") or {}
    return Report(
        path=path, engine=str(conformance.get("CORE_Engine_Version", "")),
        standard=f"{conformance.get('Standard', '')} {conformance.get('Version', '')}".strip(),
        rules=rules, findings=tuple(findings),
        datasets=tuple(str(d.get("filename", "")) for d in raw.get("Dataset_Details") or []))


# CORE starts one worker process per processor unless told otherwise, and each
# worker loads the rule cache. On a machine with many processors several runs at
# once need more memory than the machine has (docs/lessons.md, lesson 27).
POOL_SIZE = 1


def command_line(python: Path, source: Path, datasets: list[Path], out: Path,
                 define: Path | None, standard: str, version: str,
                 terminology: tuple[str, ...] = (), pool_size: int = POOL_SIZE) -> list[str]:
    """The command that runs `core.py validate` and writes a JSON report to `<out>.json`."""
    argv = [str(python), "-B", str(source / "core.py"), "validate",
            "-s", standard, "-v", version, "-of", "JSON", "-o", str(out),
            "-p", "disabled", "-l", "critical", "-ps", str(pool_size)]
    for path in datasets:
        argv += ["-dp", str(path)]
    if define is not None:
        argv += ["-dxp", str(define)]
    for package in terminology:
        argv += ["-ct", package]
    return argv


def validate(
    root: Path,
    datasets: list[Path],
    out: Path,
    define: Path | None = None,
    standard: str = "sdtmig",
    version: str = "3-4",
    terminology: tuple[str, ...] = (),
) -> Report:
    """Run `core.py validate` on dataset files and read its JSON report.

    `out` is the report path without its extension; what CORE prints goes to
    `<out>.log`. CORE finds its resources relative to the working folder, so
    it runs in a scratch folder that links them, with a Python that writes
    no bytecode: the pinned source tree stays as it was fetched.
    """
    python = python_path(root)
    source = source_dir(root)
    if not python.is_file() or not (source / "core.py").is_file():
        raise CoreError("CDISC CORE is not installed; run make install")
    out.parent.mkdir(parents=True, exist_ok=True)
    report = out.with_name(out.name + ".json")
    report.unlink(missing_ok=True)
    argv = command_line(python, source, [path.resolve() for path in datasets], out.resolve(),
                        define.resolve() if define is not None else None, standard, version,
                        terminology)
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    for name in ("PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV"):
        env.pop(name, None)
    log = out.with_name(out.name + ".log")
    with tempfile.TemporaryDirectory(prefix="specfirst-core-") as scratch:
        (Path(scratch) / "resources").symlink_to(source / "resources")
        with open(log, "w", encoding="utf-8") as handle:
            done = subprocess.run(argv, cwd=scratch, env=env, stdout=handle,
                                  stderr=subprocess.STDOUT)
    if done.returncode != 0 or not report.is_file():
        tail = log.read_text(encoding="utf-8", errors="replace").strip().splitlines()[-5:]
        raise CoreError(f"core.py validate exited {done.returncode}: " + " | ".join(tail))
    return read_report(report)


def main(argv: list[str] | None = None) -> int:
    from specfirst.paths import repo_root

    args = sys.argv[1:] if argv is None else argv
    if args != ["install"]:
        print("usage: python -m specfirst.cdisccore install")
        return 2
    return install(repo_root())


if __name__ == "__main__":
    sys.exit(main())
