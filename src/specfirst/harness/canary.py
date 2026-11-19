"""The canary scan (PLAN.md section 11.2; docs/decisions/ADR-010.md, decision 5).

What a reader must not see: of the kit, every file outside inputs/ (kit.yaml,
study.json, gold/, twin/); the store of model text (src/specfirst/gen/rewrites);
the seed of the kit; the private files of the run. A canary is a string of
that material that a reader can only have from there:

- planted: every private file of a run carries `planted(kit, name)`;
- drawn: a kit is written by the generator, named by the SHA-256 of its
  files and never patched, so no string can be planted in its gold. Every
  line of a protected text file, blanks collapsed, of at least MIN
  characters is a canary; a line longer than LONG gives its pieces of
  PIECE characters. A line or piece is dropped when it stands in what the
  reader may read or is meant to write: anywhere in the task folder, in an
  answer the oracle gives, in the reader's form of a gold decision record
  (its value, statement and citations as JSON), or when all but SLACK of
  its characters stand inside a statement of the gold decisions or an
  answer of the oracle (a reader writes those with words of its own
  around them);
- the seed, whatever its length.

A scan reads every string of every event of a transcript (stream-json,
decoded) and every text file of a workspace, blanks collapsed, and reports
each canary it finds with the file and line it was drawn from. Binary files
(Parquet) are neither drawn from nor scanned: every SDTM table of a kit has
a Dataset-JSON copy, which is drawn from; the ADaM Parquet of gold has none.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

MIN = 24
LONG = 120
PIECE = 80
SLACK = 16  # characters of its own a reader may write around a statement or an answer
PREFIX = "specfirst-canary-"


def squeeze(text: str) -> str:
    return " ".join(text.split())


def planted(kit_sha256: str, name: str) -> str:
    """The canary planted in a private file of a run: a function of the kit and the file."""
    digest = hashlib.sha256(f"{kit_sha256}/{name}".encode("ascii")).hexdigest()
    return f"{PREFIX}{digest[:32]}"


def is_text(data: bytes) -> bool:
    if b"\x00" in data[:65536]:
        return False
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def read_text(path: Path) -> str | None:
    data = path.read_bytes()
    return data.decode("utf-8") if is_text(data) else None


def pieces(line: str) -> list[str]:
    """The canary candidates of one line."""
    line = squeeze(line)
    if len(line) < MIN:
        return []
    if len(line) <= LONG:
        return [line]
    return [part for part in (line[at:at + PIECE] for at in range(0, len(line), PIECE))
            if len(part) >= MIN]


@dataclass(frozen=True)
class Canary:
    text: str
    source: str  # where it was drawn from: <label>:<line>


@dataclass(frozen=True)
class Hit:
    canary: Canary
    where: str

    def line(self) -> str:
        return (f"{self.where}: holds '{self.canary.text[:70]}' "
                f"(from {self.canary.source})")


class Finder:
    """Which of many strings stand in a text, in one pass over the text."""

    def __init__(self, items: list[str]):
        self.by_prefix: dict[str, list[str]] = {}
        for item in items:
            self.by_prefix.setdefault(item[:MIN], []).append(item)

    def found(self, text: str) -> set[str]:
        hits: set[str] = set()
        if not self.by_prefix:
            return hits
        index = self.by_prefix
        for at in range(len(text) - MIN + 1):
            listed = index.get(text[at:at + MIN])
            if listed:
                hits.update(item for item in listed if text.startswith(item, at))
        return hits


class Canaries:
    def __init__(self, items: list[Canary]):
        self.items = {item.text: item for item in items}
        self.finder = Finder(sorted(text for text in self.items if len(text) >= MIN))
        self.short = sorted(text for text in self.items if len(text) < MIN)

    def __len__(self) -> int:
        return len(self.items)

    def find(self, text: str) -> list[Canary]:
        text = squeeze(text)
        found = self.finder.found(text) | {item for item in self.short if item in text}
        return [self.items[item] for item in sorted(found)]

    def sources(self) -> dict[str, int]:
        """How many canaries each source gave, by the label before its line number."""
        counts: dict[str, int] = {}
        for item in self.items.values():
            label = item.source.rsplit(":", 1)[0]
            counts[label] = counts.get(label, 0) + 1
        return dict(sorted(counts.items()))


def drawn(sources: list[tuple[str, Path]]) -> dict[str, str]:
    """Every candidate of the text files named, with where it was drawn from."""
    found: dict[str, str] = {}
    for label, path in sources:
        text = read_text(path)
        if text is None:
            continue
        for number, line in enumerate(text.splitlines(), start=1):
            for part in pieces(line):
                found.setdefault(part, f"{label}:{number}")
    return found


def build(sources: list[tuple[str, Path]], allowed: list[str], atoms: list[str],
          always: list[tuple[str, str]]) -> Canaries:
    """The canaries of a run.

    `sources`: the protected text files, each with a label; `allowed`: the texts a
    reader may read or is meant to write; `atoms`: statements and answers, which a
    reader may write inside a line of its own; `always`: canaries kept as they are
    (the planted ones and the seed), with their label.
    """
    candidates = drawn(sources)
    seen = Finder(sorted(candidates)).found(squeeze("\n".join(allowed)))
    grams = {atom[at:at + MIN] for atom in {squeeze(a) for a in atoms}
             for at in range(len(atom) - MIN + 1)}
    items = [Canary(text, source) for text, source in sorted(candidates.items())
             if text not in seen and not mostly_in(text, grams)]
    items += [Canary(text, label) for label, text in always if text]
    return Canaries(items)


def mostly_in(text: str, grams: set[str]) -> bool:
    """Whether all but SLACK characters of a candidate stand inside a statement or an
    answer (`grams`: their substrings of MIN characters): a reader may write a
    statement or an answer with a few words of its own around it."""
    covered = [False] * len(text)
    for at in range(len(text) - MIN + 1):
        if text[at:at + MIN] in grams:
            for index in range(at, at + MIN):
                covered[index] = True
    return len(text) - sum(covered) <= SLACK


def json_strings(value: object) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from json_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from json_strings(item)


def scan_transcript(canaries: Canaries, path: Path, label: str = "transcript") -> list[Hit]:
    """Every canary in every string of a stream-json transcript."""
    hits = []
    if not path.is_file():
        return hits
    text = path.read_bytes().decode("utf-8", errors="replace")
    for number, line in enumerate(text.splitlines(), start=1):
        try:
            strings = list(json_strings(json.loads(line)))
        except json.JSONDecodeError:
            strings = [line]
        found: dict[str, Canary] = {}
        for string in strings:
            for canary in canaries.find(string):
                found[canary.text] = canary
        hits += [Hit(canary, f"{label}:{number}") for _, canary in sorted(found.items())]
    return hits


def scan_files(canaries: Canaries, folder: Path, names: list[str],
               label: str = "workspace") -> list[Hit]:
    """Every canary in the text files `names` of a folder: in the text, and in the
    strings of a JSON file decoded."""
    hits = []
    for name in sorted(names):
        path = folder / name
        if not path.is_file():
            continue
        text = read_text(path)
        if text is None:
            continue
        strings = [text]
        for line in text.splitlines():
            try:
                strings += list(json_strings(json.loads(line)))
            except json.JSONDecodeError:
                pass
        found: dict[str, Canary] = {}
        for string in strings:
            for canary in canaries.find(string):
                found[canary.text] = canary
        hits += [Hit(canary, f"{label}:{name}") for _, canary in sorted(found.items())]
    return hits


def reader_views(records: list[dict], documents: tuple[str, ...]) -> list[str]:
    """What a reader that reads gold right writes: each gold record as JSON in the forms
    a writer of JSON gives it (keys sorted or not, with blanks or without), with the
    citations of each kind of document, and each value and citation alone."""
    forms = []

    def dump(value: object) -> None:
        for keys in (True, False):
            for separators in ((",", ":"), (", ", ": ")):
                forms.append(json.dumps(value, sort_keys=keys, separators=separators))

    for record in records:
        base = {key: record[key] for key in ("id", "unit", "value", "status", "class",
                                             "statement") if key in record}
        cited = [c for c in record.get("citations") or [] if isinstance(c, dict)]
        kinds = [[c for c in cited if c.get("doc") in documents],
                 [c for c in cited if c.get("doc") not in documents], cited, []]
        for kind in kinds:
            dump({**base, "citations": kind} if kind else base)
        for citation in cited:
            dump(citation)
        if record.get("value") is not None:
            dump(record["value"])
    return forms
