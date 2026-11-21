"""The natural form: model text, its two checks, and the store it is frozen in
(PLAN.md section 6.6; docs/decisions/ADR-009.md).

A model rewrites each standard-form statement of a kit into a paragraph of
ordinary document prose. What the model writes counts only after two
deterministic checks (rule R1):

    slots      every number, unit, visit name, variable name, quoted value of
               the statement, and the name of its output, still stands in the
               paragraph, as whole words and in the order of the statement
               (`slot_problems`)
    read-back  a verifier agent with a fresh context, given the paragraph, the
               question of its entry and the alternatives, picked the
               alternative of the statement (`readback` records the pick; the
               check compares it with the alternative)

A statement whose rewrite fails three times gets its phrasing template: the
`plain` family of `standard/catalog@<n>/phrasings/`, rendered with the slots of
its value. It is read back like any rewrite.

The store (`rewrites/`, or the folder `SPECFIRST_REWRITES` names):

    paragraphs.jsonl   one record per statement: every attempt with its text,
                       the call that wrote it, its slot problems, the pick of
                       the verifier and the call that read it; the accepted
                       attempt
    filler.jsonl       neutral paragraphs for the natural documents, each read
                       back as stating none of the decisions of the slice
    calls.jsonl        every model call: role, model, items, tokens, time

The store is append-only: an accepted attempt is never changed. A kit takes
the accepted text of each statement and records the SHA-256 of every
paragraph it used. A gate never calls a model (rule R4): it runs the slot
check again and holds the recorded pick against gold, for exactly the text
of each paragraph.

The model is reached through subagents of a Claude Code session (ADR-009,
decision 1). A subagent cannot be called from a script, so the loop is a
list of commands (`specfirst gen natural`): each writes the request a
subagent gets, or reads the file a subagent wrote, and decides.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import re
from pathlib import Path

from specfirst.compile import catalog as catalogs
from specfirst.compile.slots import SCALARS, Slot, SlotError, _render_scalar, render_value
from specfirst.compile.standard_form import StandardForm, StandardFormError, compile_template

STORE = Path(__file__).resolve().parent / "rewrites"
PARAGRAPHS = "paragraphs.jsonl"
FILLER = "filler.jsonl"
CALLS = "calls.jsonl"
MAX_FAILED = 3  # failed rewrites before the phrasing template (section 6.6)
FALLBACK_FAMILY = "plain"
NONE = "(none)"  # the verifier's answer when a paragraph states no alternative; never an ID
MAX_LENGTH = 700  # characters of one paragraph
MODEL = "claude-sonnet-5-5 (subagent of a Claude Code session, Agent tool, model option sonnet)"
UNIT_WORDS = ("day", "days", "week", "weeks", "month", "months", "year", "years", "subject",
              "subjects", "decimal", "decimals")
_VARIABLE = re.compile(r"\b[A-Z][A-Z0-9]{1,7}\.[A-Z][A-Z0-9_]*\b")
_NUMBER = re.compile(r"(?<![\w.])-?[0-9]+(?:\.[0-9]+)?(?![\w]|\.[0-9])")
_ANCHOR = re.compile(r"\[[0-9.]+/[sp][0-9]+\]")
_CAPITALS = re.compile(r"(?<![\w.])[A-Z][A-Z0-9]+(?!\w|\.\w)")

# What the rewriter is told (ADR-009, decision 6). The request file repeats it.
REWRITE_RULES = (
    "Write one paragraph per statement, one to three sentences, in the plain voice of a "
    "clinical study protocol or statistical analysis plan, in the future or present tense.",
    "Keep every number, unit, visit name, variable name (such as DM.ARMCD), quoted value and "
    "the name of the table exactly as the statement writes it, and in the same order as in "
    "the statement. Quotation marks may be dropped; the words inside them may not change.",
    "Say the same rule and nothing else: add no rule, no example, no number, no value and no "
    "reason. Do not mention the standard form, a catalog or a template.",
    "Reword freely: change the sentence structure and the ordinary words; the meaning must "
    "stay exactly the same.",
    "One line of plain ASCII text: no line breaks, no Markdown, no brackets around numbers, "
    "no curly quotes, no dashes other than the ASCII hyphen.",
)
FILLER_RULES = (
    "Write one neutral paragraph of two to four sentences for the heading given, in the voice "
    "of a clinical study protocol or statistical analysis plan.",
    "It must state no analysis rule at all: nothing about analysis sets or populations, "
    "treatment dates or groups, study days, disposition, adverse events, causality, "
    "imputation of dates, baseline values, age or race groups, body mass index, which tables "
    "are produced, table columns, rows, percentages, rounding or decimals.",
    "No numbers, no dates, no names of variables or datasets. One line of plain ASCII text.",
)


class NaturalError(ValueError):
    """The store or a file of the loop cannot be used."""


def store_dir() -> Path:
    """The folder of the store: `SPECFIRST_REWRITES`, else the store of the gate's kits."""
    named = os.environ.get("SPECFIRST_REWRITES")
    return Path(named) if named else STORE


def key_of(statement: str) -> str:
    return hashlib.sha256(statement.encode("ascii")).hexdigest()[:16]


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("ascii")).hexdigest()


def item_of(kind: str, text: str) -> str:
    """The opaque ID of one read-back item: it tells the verifier nothing."""
    return "r" + hashlib.sha256(f"{kind}\n{text}".encode("ascii")).hexdigest()[:12]


# ---- the store ----------------------------------------------------------------------------


def _read_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    with open(path, encoding="ascii") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(json.dumps(record, sort_keys=True, ensure_ascii=True) + "\n"
                   for record in records)
    path.write_text(text, encoding="ascii", newline="\n")


@dataclasses.dataclass
class Store:
    folder: Path
    paragraphs: dict[str, dict]  # statement key -> record
    filler: dict[str, dict]  # filler key -> record
    calls: list[dict]

    @classmethod
    def load(cls, folder: Path | None = None) -> Store:
        folder = folder or store_dir()
        paragraphs = {record["key"]: record for record in _read_jsonl(folder / PARAGRAPHS)}
        filler = {record["key"]: record for record in _read_jsonl(folder / FILLER)}
        return cls(folder, paragraphs, filler, _read_jsonl(folder / CALLS))

    def save(self) -> None:
        _write_jsonl(self.folder / PARAGRAPHS,
                     [self.paragraphs[k] for k in sorted(self.paragraphs)])
        _write_jsonl(self.folder / FILLER, [self.filler[k] for k in sorted(self.filler)])
        _write_jsonl(self.folder / CALLS, self.calls)

    def accepted(self, statement: str) -> dict | None:
        """The accepted attempt of a statement, or None."""
        record = self.paragraphs.get(key_of(statement))
        if not record or not record.get("accepted"):
            return None
        return record["attempts"][record["accepted"] - 1]

    def accepted_filler(self) -> list[dict]:
        """The filler paragraphs read back as stating nothing, by key."""
        return [self.filler[key] for key in sorted(self.filler)
                if (self.filler[key].get("readback") or {}).get("states") == []]

    def failed(self, record: dict) -> int:
        return sum(1 for attempt in record["attempts"]
                   if attempt["by"] != "template" and (
                       attempt.get("slots") or self.readbacks(attempt)) and not any(
                       item["agrees"] for item in self.readbacks(attempt)))

    def abstention(self, call: str) -> str:
        """The answer the verifier of a call was told to give for "none of them"."""
        found = next((item for item in self.calls if item["call"] == call), {})
        return str(found.get("abstention", NONE))

    def readbacks(self, attempt: dict) -> list[dict]:
        """The read-backs of an attempt that count: a pick that is also the abstention
        marker of its call tells agreement from abstention apart only when no alternative
        has that ID, so it does not count (lesson 57)."""
        found = [attempt.get("readback"), *(attempt.get("again") or [])]
        return [item for item in found if item and item["pick"] != self.abstention(
            item["by"])]

    def add_call(self, call: dict) -> None:
        if any(item["call"] == call["call"] for item in self.calls):
            raise NaturalError(f"the call {call['call']} is in the store already")
        self.calls.append(call)


# ---- the slot check -----------------------------------------------------------------------


def _scalars(slot: Slot, value: object) -> list[str]:
    """The texts of the scalars of a slot value, in the order the statement writes them."""
    if slot.type in SCALARS:
        return [_bare(_render_scalar(slot.type, value))]
    if slot.item_type:
        return [_bare(_render_scalar(slot.item_type, item)) for item in value]
    kinds = dict(slot.fields)
    order = re.findall(r"\{([a-z][a-z0-9_]*)\}", slot.item)
    return [_bare(_render_scalar(kinds[name], record[name])) for record in value
            for name in order]


def _bare(text: str) -> str:
    return text[1:-1] if len(text) >= 2 and text[0] == text[-1] == '"' else text


def _from_text(text: str, after_number: bool) -> tuple[list[str], list[str], list[str]]:
    """In a piece of template text: the unit word that follows a numeric slot, the numbers
    with the unit word after each, and the names (variable names, and words in capitals
    such as OTHER)."""
    lead: list[str] = []
    if after_number:
        match = re.match(r"\s+([a-z]+)\b", text)
        if match and match.group(1) in UNIT_WORDS:
            lead.append(match.group(1))
    numbers: list[str] = []
    for match in _NUMBER.finditer(text):
        if _VARIABLE.search(text[max(0, match.start() - 12):match.end()]):
            continue
        numbers.append(match.group(0))
        unit = re.match(r"\s+([a-z]+)\b", text[match.end():])
        if unit and unit.group(1) in UNIT_WORDS:
            numbers.append(unit.group(1))
    names = [(match.start(), match.group(0)) for match in _VARIABLE.finditer(text)]
    names += [(match.start(), match.group(0)) for match in _CAPITALS.finditer(text)
              if not _VARIABLE.search(text[max(0, match.start() - 9):match.end() + 9])]
    return lead, numbers, [name for _, name in sorted(names)]


def token_groups(catalog: catalogs.Catalog, entry_id: str, unit: str,
                 value: dict) -> list[list[str]]:
    """What the slot check asks of a paragraph that states this decision, in groups.

    One group per slot (its scalars, and the unit word after a number); one for the
    numbers of the template text with their unit words; one for its variable names; one
    for the name of the output. A group keeps its order: the items of a list, the codes
    and labels of a map, the numbers of the text. Groups may stand in any order.
    """
    entry = catalog.entries[entry_id]
    template = compile_template(entry.alternative(value["rule"]))
    slots: list[list[str]] = []
    numbers: list[str] = []
    variables: list[str] = []
    output: list[str] = []
    previous: list[str] | None = None
    for kind, token in template.tokens:
        if kind == "text":
            lead, found, names = _from_text(token, previous is not None)
            if previous is not None:
                previous += lead
            numbers += found
            variables += names
            previous = None
        elif kind == "output":
            phrase = catalog.units[unit].phrase
            output.append(phrase[4:] if phrase.startswith("the ") else phrase)
            previous = None
        else:
            slots.append(_scalars(token, value[token.name]))
            numeric = (token.item_type or token.type) in ("int", "number")
            previous = slots[-1] if numeric else None
    return [group for group in (*slots, numbers, variables, output) if group]


def tokens(catalog: catalogs.Catalog, entry_id: str, unit: str, value: dict) -> list[str]:
    """Every token of `token_groups`, group after group."""
    return [token for group in token_groups(catalog, entry_id, unit, value) for token in group]


def _cased(text: str) -> str:
    return " ".join(text.replace('"', " ").replace("`", " ").split())


def _normal(text: str) -> str:
    return _cased(text).lower()


def _find(token: str, text: str, start: int) -> re.Match | None:
    """The next whole-word match of a token at or after `start`. `text` is `_cased` of
    the paragraph: a token with a capital letter is matched with its case (the data
    compare such values exactly), any other token without case."""
    exact = any(char.isupper() for char in token)
    body = re.escape(_cased(token) if exact else _normal(token)).replace(r"\ ", r"\s+")
    pattern = rf"(?<![A-Za-z0-9_.]){body}(?![A-Za-z0-9_]|\.[0-9])"
    return re.compile(pattern, 0 if exact else re.IGNORECASE).search(text, start)


def _count(token: str, text: str) -> int:
    found, position = 0, 0
    while (match := _find(token, text, position)) is not None:
        found, position = found + 1, match.end()
    return found


def _numbers(text: str) -> list[str]:
    return [match.group(0) for match in _NUMBER.finditer(text)
            if not _VARIABLE.search(text[max(0, match.start() - 12):match.end()])]


def _capitals(text: str) -> set[str]:
    return {word for word in re.findall(r"[A-Za-z0-9]+", text)
            if len(word) > 1 and word.isupper()}


def slot_problems(paragraph: str, wanted: list[str] | list[list[str]]) -> list[str]:
    """Why a paragraph does not keep the tokens of its statement (empty: it does).

    `wanted` is `token_groups` of the statement, or one list of tokens taken as one
    group: every token must stand in the paragraph, and the tokens of a group in their
    order; a token with a capital letter with its case. The paragraph may hold no number
    and no word in capitals that the statement lacks.
    """
    problems = []
    if not paragraph or not paragraph.strip():
        return ["the paragraph is empty"]
    if not paragraph.isascii():
        problems.append("the paragraph is not ASCII")
    if "\n" in paragraph or "\r" in paragraph:
        problems.append("the paragraph is not one line")
    if paragraph != paragraph.strip() or paragraph.lstrip().startswith(("#", "-", "*", ">")):
        problems.append("the paragraph starts with a blank or a Markdown mark")
    if _ANCHOR.search(paragraph):
        problems.append("the paragraph holds an anchor")
    if len(paragraph) > MAX_LENGTH:
        problems.append(f"the paragraph is longer than {MAX_LENGTH} characters")
    text = _cased(paragraph)
    groups = [wanted] if wanted and isinstance(wanted[0], str) else wanted
    flat = [token for group in groups for token in group]
    allowed = [number for token in flat for number in _numbers(token)]
    for number in sorted(set(_numbers(text))):
        if _numbers(text).count(number) > allowed.count(number):
            problems.append(f"the number {number} is not in the statement" if number not in
                            allowed else f"the number {number} stands more often than in "
                            "the statement")
    known = set().union(*(_capitals(token) for token in flat)) if flat else set()
    problems += [f"'{word}' is not in the statement" for word in sorted(_capitals(text) - known)]
    for group in groups:
        position = 0
        for token in group:
            match = _find(token, text, position)
            if match is None:
                stands, needed = _count(token, text), group.count(token)
                problems.append(
                    f"'{token}' is not in the paragraph" if not stands else
                    f"'{token}' stands {stands} times in the paragraph, the statement has it "
                    f"{needed} times" if stands < needed else
                    f"'{token}' is out of the order of the statement")
                continue
            position = match.end()
    return problems


# ---- the phrasing template (the fallback) --------------------------------------------------


def phrasing(catalog: catalogs.Catalog, entry_id: str, unit: str, value: dict,
             family: str = FALLBACK_FAMILY) -> str:
    """A decision in a phrasing of the catalog, rendered with its slots."""
    StandardForm(catalog).check_value(entry_id, unit, value)
    entry = catalog.entries[entry_id]
    texts = catalog.read_yaml(entry.phrasings)["alternatives"][value["rule"]]
    alternative = entry.alternative(value["rule"])
    try:
        template = compile_template(dataclasses.replace(alternative, statement=texts[family]))
        parts = []
        for kind, token in template.tokens:
            if kind == "text":
                parts.append(token)
            elif kind == "output":
                parts.append(catalog.units[unit].phrase)
            else:
                parts.append(render_value(token, value[token.name]))
    except (KeyError, StandardFormError, SlotError) as error:
        raise NaturalError(f"{entry_id}: the phrasing '{family}' cannot be rendered: "
                           f"{error}") from None
    return "".join(parts)


# ---- the loop: requests and answers -------------------------------------------------------


def question(catalog: catalogs.Catalog, entry_id: str, unit: str) -> dict:
    """What the verifier is shown of a decision: its question and its alternatives, the
    output named. Nothing of the value of a study."""
    entry = catalog.entries[entry_id]
    phrase = catalog.units[unit].phrase if entry.per_family else ""

    def named(text: str) -> str:
        text = text.replace("{output}", phrase) if phrase else text
        return re.sub(r"\{([a-z_]+)\}", lambda m: f"<{m.group(1)}>", text)

    asked = entry.question + (f" (for {phrase})" if phrase else "")
    return {"question": asked, "alternatives": [
        {"id": alternative.id, "rule": named(alternative.statement),
         **({"meaning": " ".join(alternative.definition.split())}
            if alternative.definition else {})}
        for alternative in entry.alternatives]}


def statements_of(kit_records: list[list[dict]]) -> dict[str, dict]:
    """The statements that the natural documents of some kits state, by key."""
    found: dict[str, dict] = {}
    for records in kit_records:
        for record in records:
            for citation in record.get("citations") or []:
                if citation["doc"] in ("protocol", "sap"):
                    found[key_of(record["statement"])] = {
                        "key": key_of(record["statement"]), "entry": record["id"],
                        "unit": record["unit"], "value": record["value"],
                        "statement": record["statement"], "document": citation["doc"]}
    return found


def rewrite_request(catalog: catalogs.Catalog, store: Store, wanted: dict[str, dict],
                    filler: list[dict]) -> dict:
    """The request of a rewriter: the statements that need a rewrite, and filler."""
    items = []
    for key in sorted(wanted):
        record = store.paragraphs.get(key)
        if record and (record.get("accepted") or store.failed(record) >= MAX_FAILED
                       or any(a.get("readback") is None and not a.get("slots")
                              for a in record["attempts"])):
            continue  # accepted, given up, or waiting for its read-back
        item = wanted[key]
        alternative = catalog.entries[item["entry"]].alternative(item["value"]["rule"])
        items.append({"key": key, "document": item["document"], "statement": item["statement"],
                      **({"meaning": " ".join(alternative.definition.split())}
                         if alternative.definition else {})})
    wanted_filler = [item for item in filler if item["key"] not in store.filler]
    return {"rules": list(REWRITE_RULES), "paragraphs": items,
            "filler_rules": list(FILLER_RULES), "filler": wanted_filler,
            "answer": {"paragraphs": [{"key": "<key>", "text": "<paragraph>"}],
                       "filler": [{"key": "<key>", "text": "<paragraph>"}]}}


def propose(catalog: catalogs.Catalog, store: Store, wanted: dict[str, dict], answer: dict,
            call: str, by: str = "") -> list[str]:
    """Store the paragraphs a rewriter wrote, each with the problems of its slot check.
    Returns one line per paragraph."""
    lines = []
    for item in answer.get("paragraphs") or []:
        key, text = str(item.get("key")), str(item.get("text") or "")
        if key not in wanted:
            lines.append(f"{key}: not a statement of the request; ignored")
            continue
        info = wanted[key]
        record = store.paragraphs.setdefault(key, {
            "key": key, "entry": info["entry"], "unit": info["unit"], "value": info["value"],
            "statement": info["statement"], "attempts": [], "accepted": None})
        if record.get("accepted") or store.failed(record) >= MAX_FAILED:
            lines.append(f"{key}: accepted or given up already; ignored")
            continue
        problems = slot_problems(text, token_groups(catalog, info["entry"], info["unit"],
                                                    info["value"]))
        record["attempts"].append({"n": len(record["attempts"]) + 1, "by": by or call,
                                   "text": text, "slots": problems, "readback": None})
        lines.append(f"{key} {info['entry']}: attempt {len(record['attempts'])}: "
                     + ("slots ok" if not problems else "SLOTS: " + "; ".join(problems)))
        _fall_back(catalog, record, store, lines)
    for item in answer.get("filler") or []:
        key, text = str(item.get("key")), str(item.get("text") or "")
        if key in store.filler:
            lines.append(f"{key}: in the store already; ignored")
            continue
        problems = slot_problems(text, [])
        if _NUMBER.search(text) or _VARIABLE.search(text):
            problems.append("filler holds a number or a variable name")
        store.filler[key] = {"key": key, "heading": str(item.get("heading") or ""),
                             "document": str(item.get("document") or ""), "text": text,
                             "by": by or call, "problems": problems, "readback": None}
        lines.append(f"{key}: filler: " + ("ok" if not problems else "; ".join(problems)))
    return lines


def _fall_back(catalog: catalogs.Catalog, record: dict, store: Store, lines: list[str]) -> None:
    """After the third failed rewrite, the phrasing template becomes the next attempt."""
    if store.failed(record) < MAX_FAILED or any(a["by"] == "template"
                                                for a in record["attempts"]):
        return
    text = phrasing(catalog, record["entry"], record["unit"], record["value"])
    problems = slot_problems(text, token_groups(catalog, record["entry"], record["unit"],
                                                record["value"]))
    record["attempts"].append({"n": len(record["attempts"]) + 1, "by": "template",
                               "family": FALLBACK_FAMILY, "text": text, "slots": problems,
                               "readback": None})
    lines.append(f"{record['key']} {record['entry']}: {MAX_FAILED} failed rewrites: the "
                 f"phrasing template '{FALLBACK_FAMILY}' is attempt {len(record['attempts'])}")


def readback_request(catalog: catalogs.Catalog, store: Store) -> dict:
    """What the verifier gets: every paragraph that waits for its read-back, under an opaque
    ID, with the question of its decision and the alternatives. No statement, no answer."""
    items = []
    for key in sorted(store.paragraphs):
        record = store.paragraphs[key]
        for attempt in record["attempts"]:
            if not attempt["slots"] and not store.readbacks(attempt):
                items.append({"item": item_of(record["entry"], attempt["text"]),
                              "paragraph": attempt["text"],
                              **question(catalog, record["entry"], record["unit"])})
    filler = [{"item": item_of("filler", record["text"]), "paragraph": record["text"]}
              for record in store.filler.values()
              if record["readback"] is None and not record["problems"]]
    decisions = sorted({(r["entry"], r["unit"]) for r in store.paragraphs.values()})
    questions = sorted({question(catalog, entry_id, unit)["question"]
                        for entry_id, unit in decisions})
    items.sort(key=lambda item: item["item"])
    filler.sort(key=lambda item: item["item"])
    return {
        "rules": [
            "For each item, read the paragraph alone and pick the one alternative whose rule "
            "the paragraph states for the question, by its id. Values in angle brackets may "
            f"be any value. If the paragraph states none of them, or more than one, answer "
            f"'{NONE}'.",
            "For each filler item, list the questions (by their text) whose answer the "
            "paragraph states, or an empty list.",
            "Judge from the text only; do not read any other file.",
        ],
        "items": items, "filler": filler, "filler_questions": questions,
        "answer": {"items": [{"item": "<id>", "pick": "<alternative id or none>"}],
                   "filler": [{"item": "<id>", "states": []}]},
    }


def readback(catalog: catalogs.Catalog, store: Store, answer: dict, call: str) -> list[str]:
    """Record the verifier's picks; an attempt is accepted when its pick is the
    alternative of its statement. A statement with three failed rewrites gets its
    phrasing template as its next attempt. Returns one line per item."""
    picks = {str(item.get("item")): str(item.get("pick")) for item in answer.get("items") or []}
    states = {str(item.get("item")): list(item.get("states") or [])
              for item in answer.get("filler") or []}
    lines = []
    for key in sorted(store.paragraphs):
        record = store.paragraphs[key]
        for attempt in record["attempts"]:
            item = item_of(record["entry"], attempt["text"])
            if store.readbacks(attempt) or attempt["slots"] or item not in picks:
                continue
            # A pick that is also the abstention marker of this call agrees with nothing.
            agrees = picks[item] == record["value"]["rule"] != store.abstention(call)
            made = {"pick": picks[item], "agrees": agrees, "by": call}
            if attempt.get("readback") is None:
                attempt["readback"] = made
            else:   # read again: the first read-back does not count (`Store.readbacks`)
                attempt.setdefault("again", []).append(made)
            if agrees and not record.get("accepted"):
                record["accepted"] = attempt["n"]
            lines.append(f"{key} {record['entry']}: attempt {attempt['n']}: read back as "
                         f"{picks[item]}: " + ("ACCEPTED" if agrees else
                                               f"MISMATCH, the statement is "
                                               f"{record['value']['rule']}"))
    for record in store.filler.values():
        item = item_of("filler", record["text"])
        if record["readback"] is None and item in states:
            record["readback"] = {"states": states[item], "by": call}
            lines.append(f"{record['key']}: filler read back as stating "
                         f"{states[item] or 'nothing'}")
    for key in sorted(store.paragraphs):
        if not store.paragraphs[key].get("accepted"):
            _fall_back(catalog, store.paragraphs[key], store, lines)
    return lines


# ---- the check of a paragraph that a kit uses ------------------------------------------------


def paragraph_problems(catalog: catalogs.Catalog, store: Store, record: dict,
                       text: str) -> list[str]:
    """Why the paragraph of a decision does not pass both checks of section 6.6.

    `record` is a gold decision record with its value and statement. The
    paragraph passes when it keeps the tokens of the statement and the
    store holds a read-back of exactly this text, by its hash, whose pick is
    the alternative of the record.
    """
    problems = slot_problems(text, token_groups(catalog, record["id"], record["unit"],
                                                record["value"]))
    problems = [f"slot check: {problem}" for problem in problems]
    stored = store.paragraphs.get(key_of(record["statement"]))
    attempts = [attempt for attempt in (stored or {}).get("attempts", [])
                if sha256_text(attempt["text"]) == sha256_text(text)]
    readbacks = [item for attempt in attempts for item in store.readbacks(attempt)]
    if not readbacks and any(attempt.get("readback") for attempt in attempts):
        problems.append("read-back: the only read-back of this text cannot tell agreement "
                        "from abstention")
    elif not readbacks:
        problems.append("read-back: no read-back of this text in the store")
    elif not any(item["pick"] == record["value"]["rule"] for item in readbacks):
        problems.append(f"read-back: read back as {readbacks[0]['pick']}, the decision is "
                        f"{record['value']['rule']}")
    return problems
