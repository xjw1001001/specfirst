"""The checks of the gate gen-3a (PLAN.md section 13.5, gen-3; docs/decisions/ADR-005.md and
ADR-009.md).

The gate of gen-3 for the documents of the slice:

    The parser recovers 100% of the decisions from every standard-form
    document. Every natural document passes the slot check and the
    read-back check. A planted bad rewrite (a changed number) is rejected.
    Each kit records which probes are visible.

The kits are the ten kits of the development seed of the gate gen-2a, each
written once by a process of its own (the gate gen-2a writes them twice and
holds P1 to P4); their documents take the tiers of `documents.TIER_PLAN`.
The natural form comes from the store of model text in the repository
(`specfirst.gen.natural`): no model is called here (rule R4). Every check
first fails on planted defects (rule R5); only then does it count. The
defects are planted in copies of a kit, or in a copy of the store held in
memory.
"""

from __future__ import annotations

import copy
import json
import re
import shutil
import tempfile
from collections.abc import Callable
from pathlib import Path

import yaml

from specfirst.compile import catalog as catalogs
from specfirst.compile import house as houses
from specfirst.gen import GENERATOR, documents, gate2, kits, natural, study
from specfirst.gen import design as designs

Out = Callable[[str], None]
SEED = gate2.SEED
COUNT = gate2.COUNT


class Scratch:
    """The folder of the kits of one run of the gate; removed after the last check."""

    def __init__(self) -> None:
        self.folder: Path | None = None
        self.results: dict[int, tuple[dict, dict]] = {}

    def get(self) -> Path:
        if self.folder is None:
            self.folder = Path(tempfile.mkdtemp(prefix="specfirst-gen3a-"))
        return self.folder

    def remove(self) -> None:
        if self.folder is not None:
            shutil.rmtree(self.folder, ignore_errors=True)
        self.folder = None
        self.results = {}


SCRATCH = Scratch()


def kit_dir(number: int) -> Path:
    return SCRATCH.get() / f"kit-{number:03d}"


def _context(root: Path) -> tuple[catalogs.Catalog, houses.House]:
    return catalogs.load(catalogs.default_dir(root)), houses.load(houses.default_dir(root))


def check_kit(root: Path, folder: Path, store: natural.Store | None = None) -> tuple[dict, dict]:
    """documents.problems on a written kit."""
    catalog, house = _context(root)
    return documents.problems(catalog, house, folder, kits.read_manifest(folder),
                              kits.read_decisions(folder),
                              designs.load(folder / "gold" / "design.yaml"),
                              study.read_probes(folder), store)


def _results(root: Path, number: int) -> tuple[dict, dict]:
    if number not in SCRATCH.results:
        SCRATCH.results[number] = check_kit(root, kit_dir(number))
    return SCRATCH.results[number]


def _written() -> bool:
    return all((kit_dir(number) / kits.MANIFEST).is_file() for number in range(1, COUNT + 1))


def _copy(number: int) -> tuple[Path, Path]:
    scratch = Path(tempfile.mkdtemp(prefix="specfirst-gen3a-plant-"))
    target = scratch / "kit"
    shutil.copytree(kit_dir(number), target)
    return scratch, target


def _planted(root: Path, out: Out, what: str, number: int, change: Callable[[Path], None],
             check: str, expected: str, store: natural.Store | None = None) -> bool:
    """Plant a defect in a copy of kit `number` and ask that `check` reports it."""
    scratch, target = _copy(number)
    try:
        change(target)
        found, _ = check_kit(root, target, store)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    seen = [problem for problem in found[check] if expected in problem]
    out(f"planted defect in kit {number}: {what}: the check {'reports' if seen else 'MISSES'} "
        f"it" + (f": {seen[0][:200]}" if seen else f"; it reports {found[check][:3]}"))
    return bool(seen)


def _first(number: int, test: Callable[[dict], bool]) -> dict | None:
    return next((record for record in kits.read_decisions(kit_dir(number)) if test(record)),
                None)


def _kit_with(test: Callable[[dict], bool], tier: str | None = None) -> int:
    for number in range(1, COUNT + 1):
        if tier and documents.TIER_PLAN[number - 1] != tier:
            continue
        if _first(number, test):
            return number
    raise AssertionError("no kit of the gate has what the planted defect needs")


def _replace_paragraph(folder: Path, citation: dict, old: str, new: str) -> None:
    path = folder / documents.NATURAL[citation["doc"]]
    text = path.read_text(encoding="ascii")
    mark = f"[{citation['anchor']}] "
    lines = text.split("\n")
    index = next(i for i, item in enumerate(lines) if item.startswith(mark))
    body = lines[index][len(mark):]
    assert old in body, (old, body)
    lines[index] = mark + body.replace(old, new, 1)
    path.write_text("\n".join(lines), encoding="ascii", newline="\n")


def _report(out: Out, check: str, extra: Callable[[int, dict], str] | None = None,
            root: Path | None = None) -> bool:
    ok = True
    for number in range(1, COUNT + 1):
        found, counted = _results(root, number)
        problems = found[check]
        tier = kits.read_manifest(kit_dir(number))["documents"]["tier"]
        line = f"kit {number} ({tier}): " + (extra(number, counted) if extra else "")
        out(line + f"; {len(problems)} problems")
        for problem in problems[:8]:
            out(f"  {problem}")
        ok = ok and not problems
    return ok


# ---- the checks ----------------------------------------------------------------------------


def kits_written(root: Path, out: Out) -> bool:
    """The ten kits of the seed, each by a process of its own; their tiers."""
    from specfirst.score import gate as score_gate

    SCRATCH.remove()
    folder = SCRATCH.get()
    if not score_gate.write_kits(root, folder, out, SEED, COUNT):
        return False
    ok = True
    asks = 0
    for number in range(1, COUNT + 1):
        manifest = kits.read_manifest(kit_dir(number))
        tier = manifest["documents"]["tier"]
        asks += tier == "ask"
        wanted = documents.TIER_PLAN[number - 1]
        if manifest["generator"] != GENERATOR or tier != wanted:
            out(f"kit {number}: generator {manifest['generator']}, tier {tier}; the plan gives "
                f"{GENERATOR}, {wanted}")
            ok = False
    out(f"tiers of the documents: {', '.join(documents.TIER_PLAN)}; kits of the ask demo: "
        f"{asks}")
    return ok and asks == 2


def _need_kits(out: Out) -> bool:
    if not _written():
        out("the kits of the gate were not written")
        return False
    return True


def parser(root: Path, out: Out) -> bool:
    """Every standard-form document parses; 100% of the decisions are recovered."""
    if not _need_kits(out):
        return False
    number = 1
    stated = _first(number, lambda r: r["status"] == "stated" and
                    r["citations"][0]["doc"] == "sap-standard")

    def without_statement(folder: Path) -> None:
        path = folder / documents.STANDARD["sap"]
        mark = f"[{stated['citations'][0]['anchor']}] "
        path.write_text("\n".join(line for line in path.read_text(encoding="ascii").split("\n")
                                  if not line.startswith(mark)), encoding="ascii", newline="\n")

    def other_value(folder: Path) -> None:
        path = folder / documents.STANDARD["sap"]
        text = path.read_text(encoding="ascii")
        old = "Displayed numbers in the adverse event summary table are rounded half"
        if "rounded half to even" in text:
            text = text.replace(f"{old} to even.", f"{old} away from zero.")
        else:
            text = text.replace(f"{old} away from zero.", f"{old} to even.")
        path.write_text(text, encoding="ascii", newline="\n")

    seen = _planted(root, out, f"the standard-form SAP without the statement of "
                    f"{stated['id']}", number, without_statement, "parser", stated["id"])
    seen &= _planted(root, out, "the standard-form SAP states the other rounding rule",
                     number, other_value, "parser", "tfl.rounding.rule")
    if not seen:
        return False
    return _report(out, "parser", lambda n, c: f"{c['recovered']} of {c['decisions']} "
                   "decisions recovered from the standard-form documents, the house standard "
                   "and the oracle", root)


def _paragraph(root: Path, number: int,
               test: Callable[[list[str]], bool]) -> tuple[dict, str, list[str]]:
    """A stated decision of a kit whose tokens pass `test`, with its paragraph."""
    catalog, _ = _context(root)
    texts = documents.read_texts(kit_dir(number))
    for record in kits.read_decisions(kit_dir(number)):
        if record["status"] != "stated":
            continue
        wanted = natural.tokens(catalog, record["id"], record["unit"], record["value"])
        if test(wanted):
            citation = record["citations"][1]
            body = documents.paragraphs(texts[citation["doc"]])[citation["anchor"]]
            return record, body, wanted
    raise AssertionError("no paragraph of the kit has what the planted defect needs")


def slots(root: Path, out: Out) -> bool:
    """Every decision paragraph of every natural document passes the slot check."""
    if not _need_kits(out):
        return False
    number = _kit_with(lambda r: r["status"] == "stated" and bool(re.search(
        r"\b[A-Z]{2}\.[A-Z]", r["statement"])))
    record, body, wanted = _paragraph(root, number, lambda w: any("." in t for t in w))
    variable = next(token for token in wanted if "." in token)
    name = re.search(re.escape(variable), body, re.IGNORECASE).group(0)
    seen = _planted(root, out, f"the variable name {variable} taken out of the paragraph of "
                    f"{record['id']}", number,
                    lambda f: _replace_paragraph(f, record["citations"][1], name, "the variable"),
                    "slots", f"'{variable}' is not in the paragraph")
    number = _kit_with(lambda r: r["id"] == "demo.age.groups", "full")
    record, body, wanted = _paragraph(root, number, lambda w: w[:2] == ["65", "65"])
    first = re.search(r"\b65\b", body)
    last = [m for m in re.finditer(r"\b80\b", body)][-1]
    swapped = body[:first.start()] + "80" + body[first.end():last.start()] + "65" + \
        body[last.end():]
    seen &= _planted(root, out, f"the numbers 65 and 80 exchanged in the paragraph of "
                     f"{record['id']}", number,
                     lambda f: _replace_paragraph(f, record["citations"][1], body, swapped),
                     "slots", "out of the order")
    if not seen:
        return False
    return _report(out, "slots", lambda n, c: f"{c['paragraphs']} decision paragraphs keep the "
                   "tokens of their statements", root)


def readback(root: Path, out: Out) -> bool:
    """Every decision paragraph is a text the verifier read back as its alternative; every
    filler paragraph was read back as stating nothing."""
    if not _need_kits(out):
        return False
    store = natural.Store.load()
    number = 1
    record = _first(number, lambda r: r["status"] == "stated" and r["id"] == "tfl.rounding.rule")
    key = natural.key_of(record["statement"])

    wrong = copy.deepcopy(store)
    stored = wrong.paragraphs[key]
    attempt = stored["attempts"][stored["accepted"] - 1]
    other = next(a.id for a in _context(root)[0].entries[record["id"]].alternatives
                 if a.id != record["value"]["rule"])
    attempt["readback"] = {**attempt["readback"], "pick": other}
    seen = _planted(root, out, f"the store says the verifier read the paragraph of "
                    f"{record['id']} as {other}", number, lambda f: None, "readback",
                    f"read back as {other}", wrong)
    gone = copy.deepcopy(store)
    del gone.paragraphs[key]
    seen &= _planted(root, out, f"the store has no read-back of the paragraph of {record['id']}",
                     number, lambda f: None, "readback", "no read-back of this text", gone)
    filler = copy.deepcopy(store)
    texts = documents.read_texts(kit_dir(number))
    placed = documents.read_record(kit_dir(number))["documents"]["sap"]["paragraphs"]
    one = next(item for item in placed if item["kind"] == "filler")
    filler.filler[one["filler_key"]]["text"] = documents.paragraphs(texts["sap"])[
        one["anchor"]] + " It is filler."
    seen &= _planted(root, out, f"the filler paragraph sap#{one['anchor']} is not the text the "
                     "store read back", number, lambda f: None, "readback", "filler", filler)
    if not seen:
        return False
    ok = _report(out, "readback", lambda n, c: f"{c['paragraphs']} decision paragraphs read "
                 f"back as their alternative, {c['filler']} filler paragraphs as stating nothing",
                 root)
    records = list(store.paragraphs.values())
    templates = sum(1 for r in records if r.get("accepted")
                    and r["attempts"][r["accepted"] - 1]["by"] == "template")
    out(f"the store: {len(records)} statements, {sum(1 for r in records if r.get('accepted'))} "
        f"accepted, {templates} of them by the phrasing template; "
        f"{len(store.accepted_filler())} filler paragraphs; {len(store.calls)} model calls")
    return ok


def bad_rewrite(root: Path, out: Out) -> bool:
    """A planted bad rewrite, a changed number, is rejected: by the slot check and the
    read-back check in a kit, and by the loop when a rewriter proposes it."""
    if not _need_kits(out):
        return False
    catalog, _ = _context(root)
    number = _kit_with(lambda r: r["id"] == "demo.age.groups", "full")
    record, body, _ = _paragraph(root, number, lambda w: w[:2] == ["65", "65"])
    changed = re.sub(r"\b80\b", "85", body, count=1)
    citation = record["citations"][1]
    seen = _planted(root, out, f"the paragraph {citation['doc']}#{citation['anchor']} of "
                    f"{record['id']} with 80 changed to 85", number,
                    lambda f: _replace_paragraph(f, citation, body, changed), "slots",
                    "'80' stands 1 times in the paragraph")
    seen &= _planted(root, out, "the same rewrite, held against the read-back", number,
                     lambda f: _replace_paragraph(f, citation, body, changed), "readback",
                     "no read-back of this text")
    # The loop: the rewrite is proposed, kept as a failed attempt, and never read back.
    store = natural.Store(Path(tempfile.gettempdir()) / "not-saved", {}, {}, [])
    key = natural.key_of(record["statement"])
    wanted = {key: {"key": key, "entry": record["id"], "unit": record["unit"],
                    "value": record["value"], "statement": record["statement"],
                    "document": citation["doc"]}}
    lines = natural.propose(catalog, store, wanted, {"paragraphs": [{"key": key,
                                                                      "text": changed}]},
                            "planted")
    attempt = store.paragraphs[key]["attempts"][0]
    request = natural.readback_request(catalog, store)
    refused = bool(attempt["slots"]) and not store.paragraphs[key]["accepted"] and not \
        request["items"]
    out(f"planted bad rewrite proposed to the loop: {lines[0][:160]}; not accepted and not "
        f"sent to the verifier: {'yes' if refused else 'NO'}")
    return seen and refused


def tiers(root: Path, out: Out) -> bool:
    """Full, standard and the ask demo; the oracle answers exactly the asked decisions."""
    if not _need_kits(out):
        return False
    ask = documents.TIER_PLAN.index("ask") + 1

    def no_answers(folder: Path) -> None:
        path = folder / documents.ORACLE
        oracle = yaml.safe_load(path.read_text(encoding="ascii"))
        oracle["answers"] = []
        path.write_text(yaml.safe_dump(oracle, sort_keys=False), encoding="ascii", newline="\n")

    seen = _planted(root, out, "a kit of the ask demo whose oracle answers nothing", ask,
                    no_answers, "tiers", "the oracle answers []")
    full = documents.TIER_PLAN.index("full") + 1

    def default_in_full(folder: Path) -> None:
        records = kits.read_decisions(folder)
        catalog, house = _context(root)
        features = designs.features(designs.load(folder / "gold" / "design.yaml"))
        base = {(r["id"], r["unit"]): r
                for r in houses.default_decisions(catalog, house, features)}
        for index, record in enumerate(records):
            key = (record["id"], record["unit"])
            if key in base and base[key]["value"] == record["value"]:
                records[index] = {**{k: base[key][k] for k in ("id", "unit", "value", "status",
                                                               "class", "statement",
                                                               "citations")},
                                  **({"binds": record["binds"]} if "binds" in record else {})}
                break
        from specfirst.gen import gold

        gold.write_decisions(folder, records)

    seen &= _planted(root, out, "a kit of the tier full that leaves one house default to the "
                     "house standard", full, default_in_full, "tiers", "the tier full asks stated")
    if not seen:
        return False
    ok = _report(out, "tiers", lambda n, c: f"{c['decisions']} decisions", root)
    for number in range(1, COUNT + 1):
        if documents.TIER_PLAN[number - 1] == "ask":
            asked = kits.read_manifest(kit_dir(number))["documents"]["asked"]
            out(f"kit {number}: the ask demo leaves out {', '.join(asked)}; the oracle answers "
                "them")
    return ok


def anchors(root: Path, out: Out) -> bool:
    """Every citation's quote stands inside the span of its anchor, in either form; the
    record of the natural form names every paragraph with its hash."""
    if not _need_kits(out):
        return False
    number = 2
    record = _first(number, lambda r: r["status"] == "stated")

    def moved(folder: Path) -> None:
        records = kits.read_decisions(folder)
        for item in records:
            if item["id"] == record["id"] and item["unit"] == record["unit"]:
                anchor = item["citations"][1]["anchor"]
                section, paragraph = anchor.split("/p")
                item["citations"][1]["anchor"] = f"{section}/p{int(paragraph) + 1}"
        from specfirst.gen import gold

        gold.write_decisions(folder, records)

    seen = _planted(root, out, f"the natural citation of {record['id']} names the next "
                    "paragraph", number, moved, "citations", record["id"])

    def changed_text(folder: Path) -> None:
        _replace_paragraph(folder, record["citations"][1], record["citations"][1]["quote"],
                           record["citations"][1]["quote"] + " As planned.")

    seen &= _planted(root, out, f"the paragraph of {record['id']} changed after natural.json "
                     "was written", number, changed_text, "layout", "not the text")
    if not seen:
        return False
    ok = _report(out, "citations", lambda n, c: f"{c['citations']} citations stand at their "
                 "anchors", root)
    return _report(out, "layout", lambda n, c: "natural.json names every paragraph", root) and ok


def visible_probes(root: Path, out: Out) -> bool:
    """Each kit records which probes are visible, and each is in the visible data."""
    if not _need_kits(out):
        return False
    number = 1
    manifest = kits.read_manifest(kit_dir(number))
    only_twin = sorted(set(manifest["probes"]["twin"]) - set(manifest["probes"]["visible"]))[0]

    def listed(folder: Path) -> None:
        data = kits.read_manifest(folder)
        data["probes"]["visible"] = sorted([*data["probes"]["visible"], only_twin])
        kits.write_manifest(folder, data)

    def logged(folder: Path) -> None:
        lines = study.read_probes(folder)
        line = next(item for item in lines if item["probe"] == only_twin)
        path = folder / "gold" / "probes.jsonl"
        with open(path, "a", encoding="ascii", newline="\n") as handle:
            handle.write(json.dumps({**line, "data": "visible"}, sort_keys=True) + "\n")
        data = kits.read_manifest(folder)
        data["probes"]["visible"] = sorted([*data["probes"]["visible"], only_twin])
        kits.write_manifest(folder, data)

    seen = _planted(root, out, f"kit.yaml lists {only_twin} as visible", number, listed,
                    "probes", "does not list the probes of the log")
    seen &= _planted(root, out, f"the log and kit.yaml claim {only_twin} for the visible data",
                     number, logged, "probes", f"probe {only_twin}")
    if not seen:
        return False
    return _report(out, "probes", lambda n, c: f"{c['visible probes']} visible probes listed "
                   "and found in the visible data", root)


def summaries(root: Path, out: Out) -> bool:
    """A one-page summary per kit that names every decision."""
    try:
        if not _need_kits(out):
            return False
        number = 1
        record = kits.read_decisions(kit_dir(number))[0]

        def without_line(folder: Path) -> None:
            path = folder / documents.SUMMARY
            path.write_text("\n".join(line for line in path.read_text(encoding="ascii").split(
                "\n") if not line.startswith(f"| {record['id']} |")), encoding="ascii",
                newline="\n")

        def longer(folder: Path) -> None:
            path = folder / documents.SUMMARY
            path.write_text(path.read_text(encoding="ascii") + "Note.\n" * 30, encoding="ascii",
                            newline="\n")

        seen = _planted(root, out, f"the summary without the line of {record['id']}", number,
                        without_line, "summary", f"does not name {record['id']}")
        seen &= _planted(root, out, "the summary 30 lines longer", number, longer, "summary",
                         "more than")
        if not seen:
            return False
        return _report(out, "summary", lambda n, c: "one page, every decision named", root)
    finally:
        SCRATCH.remove()
