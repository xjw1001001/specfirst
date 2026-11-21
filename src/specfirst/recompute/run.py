"""`specfirst recompute <kit>`: write the bundle, run it sealed, compare, report (ADR-021).

The scripts run on copies of the reference ADaM in a fresh folder outside
every checkout, each in a folder of its own, with an environment that holds
only what the interpreters need: Python as `python -I` through seal.py, whose
audit hook refuses every import of specfirst or yamaa and every open by Python
of a file in the checkout or the build; R as `Rscript --vanilla`. The sealed
run is not a confinement: R, and a library's own C code, can read any file the
user can. The engine's R code is not an installed package (ADR-002), and the
static check holds every read of a script to the ADaM datasets of its plan in
the data folder (static.py says what that check does not hold). A script that
fails leaves no output, but <analysis>.failed with the reason, so that it is
`differs`.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

from specfirst import kit as kits
from specfirst.machine.canonical import sha256_file, write_json
from specfirst.paths import git_env
from specfirst.recompute import generate, static
from specfirst.recompute.bundle.compare import text_lines
from specfirst.recompute.reading import Event, NotCovered

Out = Callable[[str], None]
SEAL = Path(__file__).resolve().parent / "seal.py"
WORKERS = 4  # at most four worker processes on the shared machine
TIMEOUT = 900


@dataclass
class Result:
    plan: dict
    report: dict
    static: dict[str, list[str]]
    sealed: dict[str, str] = field(default_factory=dict)  # analysis -> why its run failed
    lines: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        counts = self.report.get("counts", {})
        return set(counts) <= {"reproduced"} and not any(self.static.values()) and \
            not self.sealed


def head(root: Path) -> tuple[str, bool | None]:
    env = {**os.environ, **git_env(root)}

    def git(*args: str) -> str | None:
        done = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, env=env)
        return done.stdout.strip() if done.returncode == 0 else None

    commit, status = git("rev-parse", "HEAD"), git("status", "--porcelain")
    return commit or "unknown", None if status is None else status == ""


def sealed_env(home: Path, fence: tuple[Path, ...] = ()) -> dict[str, str]:
    """PATH, HOME, the locale, one thread, the R library, and the folders seal.py fences."""
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(home),
           "TMPDIR": str(home), "LC_ALL": "C.UTF-8", "LANG": "C.UTF-8",
           "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
    libs = os.environ.get("SPECFIRST_R_LIBS") or os.environ.get("R_LIBS_USER")
    if libs:
        env["R_LIBS_USER"] = libs
    if fence:
        env["SPECFIRST_SEAL_FENCE"] = os.pathsep.join(str(p.resolve()) for p in fence)
    return env


def analysis_numbers(root: Path, kit_id: str, build: Path) -> dict[tuple[str, str], set[float]]:
    """The numbers the ARS states for each analysis, read again for the static check."""
    kit = kits.load_kit(root, kit_id)
    registry = json.loads((root / "standard" / "methods" / "registry.json")
                          .read_text(encoding="ascii"))["methods"]
    found: dict[tuple[str, str], set[float]] = {}
    for spec in kit.results:
        event = Event(json.loads((build / spec.ars).read_text(encoding="utf-8")), spec.id,
                      registry, spec.binding)
        for analysis_id in event.analyses:
            try:
                found[(spec.id, analysis_id)] = event.analysis(analysis_id).numbers
            except NotCovered:
                found[(spec.id, analysis_id)] = set()
    return found


def data_folder(bundle: Path, adam: Path, folder: Path) -> tuple[Path, Path]:
    """Copies of the reference ADaM (each checked against the manifest) and their CSV copies
    for the R scripts, in `folder`, outside every checkout."""
    manifest = json.loads((bundle / "manifest.json").read_text(encoding="ascii"))
    plan = json.loads((bundle / "plan.json").read_text(encoding="ascii"))
    parquet, csv = folder / "adam", folder / "csv"
    parquet.mkdir(parents=True)
    for item in manifest["reference_adam"]:
        target = parquet / item["file"]
        shutil.copyfile(adam / item["file"], target)
        if sha256_file(target) != item["sha256"]:
            raise generate.GenerateError(f"{item['file']}: not the pinned reference file")
    names = sorted({d for e in plan["analyses"] if e.get("language") == "r"
                    for d in e["datasets"]})
    done = subprocess.run([sys.executable, "-I", str(bundle / "adam_csv.py"), str(parquet),
                           str(csv), *names], capture_output=True, text=True,
                          env=sealed_env(folder), cwd=folder, timeout=TIMEOUT)
    if done.returncode != 0:
        raise generate.GenerateError(f"adam_csv.py failed: {done.stderr.strip()[-500:]}")
    return parquet, csv


def run_one(bundle: Path, entry: dict, parquet: Path, csv: Path, outputs: Path, logs: Path,
            fence: tuple[Path, ...] = ()) -> str | None:
    """Run one script in a fresh folder of its own. Returns why it failed, or None; a failed
    script leaves no output, but <analysis>.failed with the reason."""
    target = outputs / entry["event"] / f"{entry['analysis']}.csv"
    failed = target.with_suffix(".failed")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.unlink(missing_ok=True)
    failed.unlink(missing_ok=True)
    why = run_sealed(bundle, entry, parquet, csv, target, logs, fence)
    if why:
        target.unlink(missing_ok=True)
        failed.write_text(why + "\n", encoding="utf-8")
    return why


def run_sealed(bundle: Path, entry: dict, parquet: Path, csv: Path, target: Path, logs: Path,
               fence: tuple[Path, ...]) -> str | None:
    with tempfile.TemporaryDirectory(prefix="specfirst-sealed-") as name:
        home = Path(name)
        script = home / Path(entry["file"]).name
        shutil.copyfile(bundle / entry["file"], script)
        local = home / "output.csv"  # in the script's own folder, outside the fence
        if entry["language"] == "python":
            shutil.copyfile(SEAL, home / "seal.py")
            argv = [sys.executable, "-I", str(home / "seal.py"), str(script), str(parquet),
                    str(local)]
        else:
            argv = ["Rscript", "--vanilla", str(script), str(csv), str(local)]
        env = sealed_env(home, fence if entry["language"] == "python" else ())
        try:
            done = subprocess.run(argv, cwd=home, env=env, capture_output=True,
                                  text=True, timeout=TIMEOUT)
        except subprocess.TimeoutExpired:
            return f"no result within {TIMEOUT} s"
        if local.is_file():
            shutil.copyfile(local, target)
    log = logs / entry["event"] / f"{entry['analysis']}.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(done.stdout + done.stderr, encoding="utf-8")
    if done.returncode != 0:
        return (done.stderr.strip().splitlines() or ["exit " + str(done.returncode)])[-1]
    if not target.is_file():
        return "the script wrote no output"
    return None


def run_bundle(bundle: Path, adam: Path, work: Path, ard: Path | None = None,
               workers: int = WORKERS, fence: tuple[Path, ...] = ()
               ) -> tuple[dict, dict[str, str]]:
    """Run every script of the bundle sealed on the reference ADaM and compare with `ard`
    (default the bundle's own ARD rows). Writes work/out, work/logs and work/report.json.
    `fence`: the folders the Python scripts may open nothing in (seal.py)."""
    plan = json.loads((bundle / "plan.json").read_text(encoding="ascii"))
    for stale in ("out", "logs", "report.json", "report.txt"):
        target = work / stale
        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists():
            target.unlink()
    work.mkdir(parents=True, exist_ok=True)
    covered = [e for e in plan["analyses"] if "not_covered" not in e]
    failed: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="specfirst-recompute-data-") as name:
        parquet, csv = data_folder(bundle, adam, Path(name))
        with ThreadPoolExecutor(max_workers=max(1, min(workers, WORKERS))) as pool:
            done = list(pool.map(lambda e: run_one(bundle, e, parquet, csv, work / "out",
                                                   work / "logs", fence), covered))
    for entry, why in zip(covered, done, strict=True):
        if why:
            failed[f"{entry['event']}/{entry['analysis']}"] = why
    report = compare(bundle, work / "out", ard or bundle / "ard", work / "report.json")
    return report, failed


def compare(bundle: Path, outputs: Path, ard: Path, report_path: Path) -> dict:
    """The bundle's own compare.py, run as a program (the reviewer runs the same file)."""
    done = subprocess.run([sys.executable, "-I", str(bundle / "compare.py"), str(bundle),
                           str(outputs), str(ard), str(report_path)], capture_output=True,
                          text=True, timeout=TIMEOUT, env=sealed_env(report_path.parent))
    if not report_path.is_file():
        raise generate.GenerateError(f"compare.py wrote no report: {done.stderr.strip()[-500:]}")
    (report_path.parent / "report.txt").write_text(done.stdout, encoding="ascii")
    return json.loads(report_path.read_text(encoding="ascii"))


def recompute(root: Path, kit_id: str, build: Path | None = None, out: Out = print,
              workers: int = WORKERS) -> Result:
    """Generate the bundle from a build of the kit (default build/kits/<kit>), run it, report."""
    kit = kits.load_kit(root, kit_id)
    build = (build or kits.assembled_dir(root, kit_id)).resolve()
    base = generate.recompute_dir(root, kit_id)
    bundle = base / "bundle"
    commit, clean = head(root)
    plan = generate.generate(root, kit_id, build, bundle, commit, clean, out)
    problems = static.check(bundle, plan, analysis_numbers(root, kit_id, build))
    report, failed = run_bundle(bundle, build / kit.reference, base / "run", workers=workers,
                                fence=(root, build))
    result = Result(plan=plan, report=report, static=problems, sealed=failed)
    result.lines = report_lines(result, kit_id)
    write_json(base / "run" / "checks.json", {
        "build": str(build), "static": problems, "sealed": failed, "passed": result.passed})
    for line in result.lines:
        out(line)
    return result


def report_lines(result: Result, kit_id: str) -> list[str]:
    lines = text_lines(result.report)
    for analysis, why in sorted(result.sealed.items()):
        lines.append(f"sealed run failed: {analysis}: {why}")
    bad = {k: v for k, v in result.static.items() if v}
    for analysis, problems in sorted(bad.items()):
        lines.append(f"static check: {analysis}: " + "; ".join(problems[:5]))
    lines.append(f"static check: {len(result.static) - len(bad)} of {len(result.static)} "
                 "scripts pass it (imports, calls, reads, texts and numbers; ADR-021, "
                 "decision 5)")
    return lines


def main(root: Path, kit_id: str, build: Path | None, export: Path | None,
         out: Out = print) -> int:
    try:
        result = recompute(root, kit_id, build, out)
    except (generate.GenerateError, kits.KitError, OSError) as error:
        out(f"recompute {kit_id}: FAIL ({error})")
        return 1
    if export is not None:
        dest = generate.export(generate.recompute_dir(root, kit_id) / "bundle", export)
        out(f"recompute {kit_id}: the bundle is exported to {dest}")
    out(f"recompute {kit_id}: {'PASS' if result.passed else 'FAIL'}")
    return 0 if result.passed else 1
