"""The pilot as a reading task (ADR-005, decision 5): CDISCPILOT01, stage T, report only.

`write` makes a folder of the shape of a generated kit, outside every
checkout, from the pinned files of the pilot kit (kits/cdiscpilot01, read
from the fetch cache after their SHA-256 is checked), so that the harness
runs an arm on it as on a kit (`specfirst.harness.runs.run`, stage T):

    <folder>/
      kit.yaml                      id cdiscpilot01, tier C, split pilot, the units of
                                    the slice, the pins, the SHA-256 of every file
      inputs/docs/sap.md            the SAP of the study as text (`sap_text`)
      inputs/house/                 the house standard, as a kit ships it
      gold/data/adam/               adsl.parquet and adae.parquet: the reference ADaM,
                                    which stage T gives the reader (ADR-005, decision 2)
      gold/ars/reporting-event.json CDISC's ARS example as pinned: its analyses and the
                                    results it embeds
      gold/key/Out14-3-1-1.json     the key: the example's formatted values in the cells
                                    of the kit's layout (specfirst.score.pilot)
      gold/oracle.yaml              no answer: every table decision has a house default
      gold/decisions.jsonl          empty: the decision records of the pilot are std-2's

Everything outside inputs/ is a canary source of the scan, as in a kit: the
example and the key are what a reader must not see. The protocol of the
study is not public, so the task has the SAP alone (`task.render_real`).
The folder holds third-party material (the SAP, the reference ADaM, the
example): it lies outside every checkout (rule 4), and so do the task and
the run made from it.

The SAP as text. poppler's pdftotext (pinned with the system, env/system.lock;
`specfirst doctor` checks it) with 7-bit ASCII output writes a form feed after
every page. A paragraph is a run of lines that are not empty; it gets the
anchor `[<page>/p<n>]`, the page of the PDF counted from 1 and its number on
that page, in front of its first line. Besides, lines lose their trailing
blanks and every character that is not printable ASCII or a tab, the first
line of a paragraph its leading blanks, and runs of empty lines and the
form feeds become one empty line. A quote is checked against this text.

`score` scores a run on the pilot: the reader's table decisions, with the
house default for the rest, built on the reference ADaM and held against the
key, every cell that differs explained or listed (specfirst.score.pilot). The
pilot has no gold decisions, so there is no reading score.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import yaml

from specfirst import kit as realkits
from specfirst.compile import catalog as catalogs
from specfirst.compile import house as houses
from specfirst.gen import gold as kitgold
from specfirst.harness import task as tasks
from specfirst.machine.canonical import sha256_file, write_json
from specfirst.score import pilot as scorepilot

FORMAT = 1
GENERATOR = f"pilot-{FORMAT}"
SPLIT = "pilot"
KEY = f"gold/key/{scorepilot.OUTPUT}.json"
EXAMPLE = "gold/ars/reporting-event.json"
ADAM = "gold/data/adam"
SAP = "inputs/docs/sap.pdf"  # the pilot kit's path of the SAP
UNITS = ("mod-treatment", "mod-populations", "mod-ae-emergence", "tfl-ae-summary")


class PilotTaskError(RuntimeError):
    """The pilot folder cannot be written here, or from this cache."""


def anchored(text: str) -> str:
    """The text of pdftotext with an anchor in front of every paragraph."""
    pages = text.split("\f")
    out: list[str] = []
    for number, page in enumerate(pages, start=1):
        paragraph = 0
        block: list[str] = []
        for line in [*page.split("\n"), ""]:
            line = "".join(ch for ch in line.rstrip() if ch == "\t" or " " <= ch <= "~")
            if line.strip():
                block.append(line)
                continue
            if block:
                paragraph += 1
                block[0] = f"[{number}/p{paragraph}] {block[0].lstrip()}"
                out += [*block, ""]
                block = []
    return "\n".join(out)


def sap_text(pdf: Path) -> str:
    """The SAP as anchored ASCII text (poppler's pdftotext)."""
    done = subprocess.run(["pdftotext", "-enc", "ASCII7", str(pdf), "-"], capture_output=True,
                          timeout=300)
    if done.returncode != 0:
        raise PilotTaskError(f"pdftotext failed on {pdf.name}: "
                             f"{done.stderr.decode('ascii', 'replace')[:300]}")
    return anchored(done.stdout.decode("ascii", "replace"))


def not_replaceable(out: Path) -> str | None:
    """Why `out` may not be replaced by a pilot folder, or None: it is missing, empty, or a
    pilot folder written before (its manifest names the generator `pilot-<n>`). Anything
    else is never deleted (review of slice-ae-summary, finding 4)."""
    if not out.exists():
        return None
    if not out.is_dir():
        return f"{out} is a file"
    if not any(out.iterdir()):
        return None
    manifest = out / "kit.yaml"
    try:
        made = yaml.safe_load(manifest.read_text(encoding="ascii")) if manifest.is_file() else None
    except (yaml.YAMLError, UnicodeDecodeError):
        made = None
    generator = made.get("generator") if isinstance(made, dict) else None
    if isinstance(generator, str) and generator.startswith("pilot-"):
        return None
    return f"{out} holds files and is not a pilot folder"


def write(root: Path, out: Path) -> Path:
    """Write the pilot folder into `out` (outside every checkout) and return it."""
    home = tasks.inside_checkout(out)
    if home is not None:
        raise PilotTaskError(f"{out} lies inside the checkout {home}: the pilot folder holds "
                             "third-party material and lies outside every checkout (rule 4)")
    refused = not_replaceable(out)
    if refused is not None:
        raise PilotTaskError(f"{refused}: it is not replaced; name a new folder")
    from specfirst.score.candidate import Machine

    kit = realkits.load_kit(root, scorepilot.KIT)
    try:
        sap = scorepilot._pinned(root, kit, SAP)
        data, event, layout = scorepilot.reference(root)
        machine = Machine(root)
        key = scorepilot.key_grid(event, layout, scorepilot.labels(machine))
        example = scorepilot._pinned(root, kit, kit.results[0].ars)
        adam = {name: scorepilot._pinned(root, kit, f"{kit.reference}/{name.lower()}.parquet")
                for name in scorepilot.DATASETS}
    except scorepilot.PilotError as error:
        raise PilotTaskError(str(error)) from error
    del data
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    sap_md = out / tasks.DOCUMENTS["sap"]
    sap_md.parent.mkdir(parents=True)
    sap_md.write_text(sap_text(sap), encoding="ascii", newline="\n")
    kitgold.copy_house(houses.load(houses.default_dir(root)), out)
    for name, path in adam.items():
        target = out / ADAM / f"{name.lower()}.parquet"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    (out / EXAMPLE).parent.mkdir(parents=True)
    shutil.copyfile(example, out / EXAMPLE)
    write_json(out / KEY, key)
    (out / "gold" / "oracle.yaml").write_text("answers: []\n", encoding="ascii", newline="\n")
    (out / "gold" / "decisions.jsonl").write_text("", encoding="ascii", newline="\n")
    catalog = catalogs.load(catalogs.default_dir(root))
    files = {path.relative_to(out).as_posix(): sha256_file(path)
             for path in sorted(out.rglob("*")) if path.is_file()}
    manifest = {
        "kit": FORMAT,
        "id": scorepilot.KIT,
        "title": kit.title,
        "tier": tasks.REAL_TIER,
        "slice": "ae-summary-first",
        "split": SPLIT,
        "generator": GENERATOR,
        "catalog": {"name": catalog.name, "version": catalog.version},
        "house": "open-default@1",
        "pins": {"sources": dict(kit.sources), "sap_sha256": sha256_file(sap),
                 "example_sha256": sha256_file(example)},
        "units": list(UNITS),
        "datasets": list(scorepilot.DATASETS),
        "outputs": [{"unit": scorepilot.UNIT, "id": scorepilot.OUR_OUTPUT}],
        "files": files,
    }
    (out / "kit.yaml").write_text(
        "# The pilot as a reading task (specfirst.harness.pilot): third-party material,\n"
        "# outside every checkout, written again from the fetch cache.\n"
        + yaml.safe_dump(manifest, sort_keys=False), encoding="ascii", newline="\n")
    return out


def records_of(run_dir: Path) -> list[dict]:
    """The decision records a run wrote (its workspace copy of out/decisions.jsonl)."""
    path = run_dir / "workspace" / tasks.OUT / "decisions.jsonl"
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def _short(text: str, width: int = 60) -> str:
    text = " ".join(str(text).split())
    return text if len(text) <= width else text[:width - 3] + "..."


def record_lines(records: list[dict]) -> list[str]:
    """The reader's records: decision, value, status, and where it cites (the quote cut
    short: the SAP is third-party text)."""
    said = [f"the reader's records: {len(records)}"]
    for item in sorted(records, key=lambda r: (str(r.get("id")), str(r.get("unit")))):
        cites = "; ".join(f"{c.get('doc')} [{c.get('anchor')}] \"{_short(c.get('quote', ''))}\""
                          for c in item.get("citations") or [] if isinstance(c, dict))
        said.append(f"  {item.get('id')} ({item.get('unit')}): "
                    f"{json.dumps(item.get('value'), sort_keys=True)}, {item.get('status')}"
                    + (f"; cites {cites}" if cites else ""))
    return said


def score(root: Path, run_dir: Path) -> list[str]:
    """The pilot report of a run of arm S or R on the pilot (specfirst.score.pilot). Any
    other run is refused before its records are read: a run on a dev kit holds that kit's
    values (review of slice-ae-summary, finding 5)."""
    from specfirst.score.candidate import Machine

    try:
        told = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise PilotTaskError(f"{run_dir} has no readable run.json: {error}") from error
    arm = told.get("arm")
    kit = told.get("kit") if isinstance(told.get("kit"), dict) else {}
    if (kit.get("id"), kit.get("split")) != (scorepilot.KIT, SPLIT) or arm not in ("S", "R"):
        raise PilotTaskError(f"{run_dir.name} is not a run of arm S or R on the pilot (kit "
                             f"{kit.get('id')}, split {kit.get('split')}, arm {arm})")
    records = records_of(run_dir) if arm == "R" else []
    try:
        found = scorepilot.run(Machine(root), records, arm)
    except scorepilot.PilotError as error:
        raise PilotTaskError(str(error)) from error
    said = record_lines(records) if arm == "R" else []
    return said + scorepilot.lines(found)
