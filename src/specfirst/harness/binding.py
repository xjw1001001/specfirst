"""The binding of a kept run of arm R (docs/decisions/ADR-017.md, approved for the slice).

A kept dry run is bound by bytes to everything the reader of the slice reads
and everything the check scores or scans against, and by version only to
the parts of shared files that the slice does not reach (decision 1):

    by bytes      every file of the task but standard/methods/registry.json;
                  every file of the kit, through `files` of its kit.yaml
    by version    the entries of the method registry that the slice reaches,
                  each by the SHA-256 of its canonical JSON, and the format
                  of the file; kit.yaml without `pins` (the generator, the
                  catalog and the house by name and version)
    not at all    `pins` of kit.yaml: the versions of the engines, and the
                  SHA-256 of the whole registry

`runs.keep` writes binding.json beside the record (decision 4); `runs.held`
compares it with the task and the kit as they are built now (`problems`),
holds every kept file against the SHA-256 it records, and writes out/ again
from the transcript (`replay`, decision 5; finding K4 of the real-5a
review). `write` gives a run kept before ADR-017 its binding file without a
model run (decision 6).
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

from specfirst.gen import gold as kitgold
from specfirst.gen import kits as genkits
from specfirst.harness import oracle
from specfirst.harness import task as tasks
from specfirst.machine import ars
from specfirst.machine import registry as registries
from specfirst.machine.canonical import content_hash, sha256_bytes, sha256_file

BINDING = "binding.json"
FORMAT = 1
REGISTRY = tasks.STANDARD[1]  # standard/methods/registry.json
LAYOUTS = f"{kitgold.SPEC}/layout"
PATTERN = "display.pattern"
ROUNDING = "display.round.{rule}"
DEFAULT_ROUNDING = "half_away_from_zero"  # specfirst.gen.display.build
UNBOUND = ("pins",)  # the keys of kit.yaml bound by nothing (decision 3)
WRITES = ("Write", "Edit", "MultiEdit")
# How a line that `specfirst ask` prints begins: an answer, or no answer (`oracle.ask`).
ASKED = (oracle.ANSWER.split("{", 1)[0], oracle.NO_ANSWER.split(".", 1)[0] + ".")
QUESTIONS = f"{tasks.OUT}/questions.jsonl"
# The files out/ holds before the reader starts: the run writes questions.jsonl empty.
OUT_START = {QUESTIONS: ""}


class BindingError(RuntimeError):
    """A binding file cannot be written for this run."""


# ---- the parts bound by version -----------------------------------------------------------


def registry_file(task_dir: Path) -> dict:
    """standard/methods/registry.json of a task folder, as data."""
    return json.loads((task_dir / REGISTRY).read_text(encoding="ascii"))


def registry_of(data: dict) -> registries.Registry:
    """The registry that registry.json holds (its entries read as the YAML entries are)."""
    return registries.Registry({key: registries.parse_method(value, f"{REGISTRY}: {key}")
                                for key, value in sorted((data.get("methods") or {}).items())})


def reached(kit_dir: Path, registry: registries.Registry) -> list[str]:
    """The entries of the registry the slice reaches on a kit: those `ars.bind` gives the
    operations of the kit's reporting event, as the gold of the kit is built
    (`specfirst.gen.gold`), and those the build of its cells calls: `display.pattern`
    with the rounding rule each layout names (`specfirst.gen.display`)."""
    event = ars.index(json.loads((kit_dir / kitgold.ARS_FILE).read_text(encoding="ascii")))
    found = {method for method, _ in ars.bind(event, registry, {}).operations.values()}
    for path in sorted((kit_dir / LAYOUTS).glob("*.json")):
        layout = json.loads(path.read_text(encoding="ascii"))
        rule = (layout.get("formats") or {}).get("rounding", DEFAULT_ROUNDING)
        found |= {PATTERN, ROUNDING.format(rule=rule)}
    return sorted(found)


def entries(data: dict, names: list[str]) -> dict[str, str | None]:
    """The SHA-256 of the canonical JSON of each named entry; None for one not held."""
    methods = data.get("methods") or {}
    return {name: content_hash(methods[name]) if name in methods else None for name in names}


def registry_part(kit_dir: Path, task_dir: Path) -> dict:
    """The registry as the binding holds it: its format and the entries the slice
    reaches, from the registry.json of the task folder."""
    data = registry_file(task_dir)
    return {"format": data.get("registry"),
            "reached": entries(data, reached(kit_dir, registry_of(data)))}


def kit_part(kit_dir: Path) -> dict:
    """kit.yaml without `pins`: its SHA-256 in canonical JSON, the SHA-256 of each of its
    keys (to name the part that differs), and the generator, catalog and house it names."""
    manifest = genkits.read_manifest(kit_dir)
    kept = {key: value for key, value in manifest.items() if key not in UNBOUND}
    return {"kit_yaml_sha256": content_hash(kept),
            "keys": {key: content_hash(value) for key, value in sorted(kept.items())},
            "generator": manifest.get("generator"), "catalog": manifest.get("catalog"),
            "house": manifest.get("house")}


def bytes_part(manifest: dict[str, str]) -> dict:
    """The task bound by bytes: every file of its manifest but registry.json."""
    found = {path: sha for path, sha in manifest.items() if path != REGISTRY}
    return {"manifest_sha256": content_hash(found), "files": len(found)}


# ---- the kept files ------------------------------------------------------------------------


def kept_form(name: str, text: str, redact: Callable[[object], object] = lambda v: v) -> str:
    """A file of a run as `runs.keep` writes it: JSON lines and JSON in canonical form
    (sorted keys, ASCII), any other text in ASCII; `redact` replaces the local paths."""
    if name.endswith(".jsonl"):
        return "".join(json.dumps(redact(json.loads(line)), sort_keys=True,
                                  ensure_ascii=True) + "\n"
                       for line in text.splitlines() if line.strip())
    if name.endswith(".json"):
        return json.dumps(redact(json.loads(text)), indent=1, sort_keys=True,
                          ensure_ascii=True) + "\n"
    kept = str(redact(text))
    return kept.encode("ascii", errors="backslashreplace").decode("ascii")


def kept_files(kept: Path) -> dict[str, str]:
    """The SHA-256 of every file of a kept run but its binding file."""
    return {path.relative_to(kept).as_posix(): sha256_file(path)
            for path in sorted(kept.rglob("*"))
            if path.is_file() and path.relative_to(kept).as_posix() != BINDING
            and "__pycache__" not in path.relative_to(kept).parts}


def make(kit_dir: Path, task_dir: Path, manifest: dict[str, str], kept: Path) -> dict:
    """The binding of a kept run: the task it read (by bytes), the registry and kit.yaml
    (by version), and the files `keep` wrote."""
    return {"binding": FORMAT, "adr": "ADR-017", "task": bytes_part(manifest),
            "registry": registry_part(kit_dir, task_dir), "kit": kit_part(kit_dir),
            "files": kept_files(kept)}


def save(kept: Path, binding: dict) -> Path:
    path = kept / BINDING
    path.write_text(json.dumps(binding, indent=1, sort_keys=True, ensure_ascii=True) + "\n",
                    encoding="ascii", newline="\n")
    return path


def read(kept: Path) -> dict | None:
    path = kept / BINDING
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="ascii"))


# ---- out/ written again from the transcript (decision 5) ----------------------------------


def _text(content: object) -> str:
    """The text of a tool result: a string, or a list of text blocks."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(str(block.get("text") or "") for block in content
                         if isinstance(block, dict))
    return ""


def out_path(path: str) -> str | None:
    """The path in the task folder of a file a tool use writes, when it lies in out/:
    the task folder is `<task>` in a kept transcript, or the folder the reader runs in."""
    given = path.replace("\\", "/")
    for prefix in ("<task>/", "./"):
        if given.startswith(prefix):
            given = given[len(prefix):]
    return given if given.startswith(f"{tasks.OUT}/") and ".." not in given.split("/") else None


def _edit(text: str, old: str, new: str, every: bool) -> str | None:
    if every:
        return text.replace(old, new) if old else None
    return text.replace(old, new, 1) if old and text.count(old) == 1 else None


def ask_texts(asks: list[dict], answers: list[dict], known: set[str]) -> list[str]:
    """What `specfirst ask` printed for each ask of the log (`oracle.ask`): the answer of
    the oracle of the kit, or the text of no answer."""
    found = []
    for item in asks:
        if not item.get("answered"):
            found.append(oracle.NO_ANSWER if item.get("decision") in known
                         else oracle.UNKNOWN.format(decision=item.get("decision")))
            continue
        given = [a["answer"] for a in answers if a.get("decision") == item.get("decision")
                 and a.get("unit") == item.get("unit")]
        found.append(oracle.ANSWER.format(answer=given[0]) if len(given) == 1 else "")
    return found


def replay(transcript: Path, asks: list[dict], texts: list[str]) -> tuple[dict[str, str],
                                                                          list[str]]:
    """Write out/ again from a transcript: from the start the run gives it, each Write,
    Edit and MultiEdit of a file in out/ that has a result without an error, in the order
    of the results; and the line `bin/ask` appends to out/questions.jsonl for each ask of
    the log, at the Bash result that shows what `specfirst ask` printed for it (`texts`,
    from `ask_texts`). The Bash results show as many answers of `specfirst ask` as the
    log holds asks. Returns the files by path and what does not replay."""
    files = dict(OUT_START)
    problems: list[str] = []
    uses: dict[str, tuple[str, dict]] = {}
    pending = printed = 0
    for number, line in enumerate(transcript.read_text(
            encoding="utf-8", errors="replace").splitlines(), start=1):
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        message = event.get("message") if isinstance(event, dict) else None
        content = (message or {}).get("content") if isinstance(message, dict) else None
        for block in content if isinstance(content, list) else []:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_use":
                uses[str(block.get("id"))] = (str(block.get("name")), block.get("input") or {})
                continue
            if block.get("type") != "tool_result":
                continue
            name, given = uses.get(str(block.get("tool_use_id")), ("", {}))
            if name == "Bash":
                shown, at = _text(block.get("content")), 0
                printed += sum(1 for text in shown.splitlines() if text.startswith(ASKED))
                while pending < len(asks) and texts[pending] and (
                        found := shown.find(texts[pending], at)) >= 0:
                    item = asks[pending]
                    files[QUESTIONS] = files.get(QUESTIONS, "") + json.dumps(
                        {"decision": item.get("decision"), "unit": item.get("unit"),
                         "question": item.get("question")}, sort_keys=True,
                        ensure_ascii=True) + "\n"
                    at, pending = found + len(texts[pending]), pending + 1
                continue
            if name not in WRITES or block.get("is_error"):
                continue
            target = out_path(str(given.get("file_path") or ""))
            if target is None:
                continue
            if name == "Write":
                files[target] = str(given.get("content") or "")
                continue
            edits = given.get("edits") if name == "MultiEdit" else [given]
            text = files.get(target)
            for edit in edits if isinstance(edits, list) else []:
                if text is None:
                    break
                text = _edit(text, str(edit.get("old_string") or ""),
                             str(edit.get("new_string") or ""), bool(edit.get("replace_all")))
            if text is None:
                problems.append(f"transcript:{number}: {name} of {target} does not apply to "
                                "the file written again so far")
            else:
                files[target] = text
    problems += [f"asks: ask {item.get('n')} of the log ({item.get('decision')}) is not "
                 "shown by a Bash result of the transcript, in the order of the log"
                 for item in asks[pending:]]
    if printed != len(asks):
        problems.append(f"asks: the Bash results of the transcript show {printed} answers of "
                        f"`specfirst ask`, the ask log {len(asks)}")
    return files, problems


# ---- the check ----------------------------------------------------------------------------


def _differ(first: dict, second: dict) -> list[str]:
    return sorted(key for key in set(first) | set(second) if first.get(key) != second.get(key))


def task_problems(made: dict, told: dict, manifest: dict[str, str],
                  binding: dict | None) -> list[str]:
    """The task the run read against the task built now, every file but registry.json
    by bytes, and the record, task.json and binding.json against each other."""
    found = []
    differ = [path for path in _differ(manifest, told.get("manifest") or {}) if path != REGISTRY]
    if differ:
        found.append(f"task: built again, {len(differ)} files differ from the task the run "
                     f"read, for example {', '.join(differ[:3])}")
    if REGISTRY not in manifest or REGISTRY not in (told.get("manifest") or {}):
        found.append(f"task: {REGISTRY} is not in the task built now and in the task the run "
                     "read")
    own = told.get("manifest") or {}
    if tasks.task_id(own) != told.get("id") or told.get("id") != (made.get("task") or {}).get(
            "id") or content_hash(own) != (made.get("task") or {}).get("manifest_sha256"):
        found.append("task: the ID and manifest of task.json are not those of the record")
    if binding is not None and binding.get("task") != bytes_part(own):
        found.append("binding: the task of binding.json is not the task of task.json")
    return found


def problems(binding: dict | None, made: dict, told: dict, task: tasks.Task,
             kit_dir: Path, kept: Path) -> list[str]:
    """A kept run against its binding (ADR-017, decision 4): the task built now agrees
    with the task the run read on every part bound by bytes; the registry on the entries
    the slice reaches; kit.yaml without `pins`; and every kept file is the file `keep`
    wrote. Each problem names the bound part that differs."""
    found = task_problems(made, told, task.manifest, binding)
    if binding is None:
        return [f"binding: no {BINDING} beside the record (ADR-017, decision 4)", *found]
    if binding.get("binding") != FORMAT:
        found.append(f"binding: format {binding.get('binding')}, not {FORMAT}")
    try:
        now = registry_part(kit_dir, task.folder)
    except (OSError, ValueError, ars.ArsError, registries.RegistryError) as error:
        now = None
        found.append(f"registry: the entries the slice reaches cannot be found now: {error}")
    then = binding.get("registry") or {}
    if now is not None:
        if now["format"] != then.get("format"):
            found.append(f"registry: the format of {REGISTRY} is {now['format']} now, "
                         f"{then.get('format')} for the run")
        held, reach = then.get("reached") or {}, now["reached"]
        found += [f"registry: the slice now reaches {name}, which the binding of the run "
                  "does not hold" for name in sorted(set(reach) - set(held))]
        found += [f"registry: the binding holds {name}, which the slice no longer reaches"
                  for name in sorted(set(held) - set(reach))]
        found += [f"registry: the entry {name} is not the one the run read"
                  + (" (the registry no longer holds it)" if reach[name] is None else "")
                  for name in sorted(set(held) & set(reach)) if held[name] != reach[name]]
    kit_now, kit_then = kit_part(kit_dir), binding.get("kit") or {}
    if kit_now["kit_yaml_sha256"] != kit_then.get("kit_yaml_sha256"):
        keys = _differ(kit_now["keys"], kit_then.get("keys") or {})
        found.append("kit: kit.yaml without pins is not the one the run read; it differs in "
                     + (", ".join(keys) if keys else "its form"))
    listed = genkits.read_manifest(kit_dir).get("files") or {}
    wrong = [path for path, sha in sorted(listed.items())
             if not (kit_dir / path).is_file() or sha256_file(kit_dir / path) != sha]
    if wrong:
        found.append(f"kit: {len(wrong)} files of the kit are not those its kit.yaml lists, "
                     f"for example {', '.join(wrong[:3])}")
    files = kept_files(kept)
    held_files = binding.get("files") or {}
    found += [f"kept: {path} is not the file keep wrote" for path in sorted(
        set(files) & set(held_files)) if files[path] != held_files[path]]
    found += [f"kept: {path} was not written by keep" for path in sorted(
        set(files) - set(held_files))]
    found += [f"kept: {path}, which keep wrote, is missing" for path in sorted(
        set(held_files) - set(files))]
    return found


def output_problems(made: dict, kept: Path, workspace: str, transcript: str,
                    answers: list[dict], known: set[str]) -> list[str]:
    """The kept outputs tied to the run (decision 5, K4): out/ written again from the
    transcript is the file the record names (its SHA-256 as the reader wrote it) and, in
    the form `keep` writes, the kept file; the asks of the record are those of the log."""
    asks = oracle.read_asks(kept)
    found = []
    logged = [{key: item.get(key) for key in ("decision", "unit", "answered")} for item in asks]
    if logged != (made.get("asks") or []):
        found.append("asks: the asks of the record are not those of the ask log")
    files, found_replay = replay(kept / transcript, asks, ask_texts(asks, answers, known))
    found += found_replay
    out = kept / workspace
    held = {path.relative_to(out).as_posix() for path in sorted(
        (out / tasks.OUT).rglob("*")) if path.is_file()} if (out / tasks.OUT).is_dir() else set()
    for path in sorted(set(files) | held):
        if path not in files:
            found.append(f"outputs: {path} is kept, and the transcript does not write it")
            continue
        if path not in held:
            found.append(f"outputs: {path} is written by the transcript, and not kept")
            continue
        try:
            same = (out / path).read_text(encoding="ascii") == kept_form(path, files[path])
        except (ValueError, UnicodeDecodeError):
            same = False
        if not same:
            found.append(f"outputs: {path} kept is not the file the transcript wrote")
    for name in tasks.OUTPUTS:
        path = f"{tasks.OUT}/{name}"
        written = sha256_bytes(files[path].encode("utf-8")) if path in files else None
        if written != ((made.get("outputs") or {}).get(name) or {}).get("sha256"):
            found.append(f"outputs: {path} written again from the transcript is not the file "
                         "the record names")
    return found


# ---- a run kept before ADR-017 (decision 6) -----------------------------------------------


def write(made: dict, told: dict, task: tasks.Task, kit_dir: Path, kept: Path,
          answers: list[dict], known: set[str], workspace: str,
          transcript: str) -> tuple[Path | None, list[str]]:
    """Write the binding file of a run kept before ADR-017, from the task and the kit
    built now, without a model run. Refuses unless the task built now is the task the run
    read, file for file (so the registry is the one it read); kit.yaml is the one the
    record holds; and out/ written again from the transcript is the kept files and the
    files the record names."""
    if (kept / BINDING).exists():
        return None, [f"{kept.name} has a {BINDING} already"]
    refused = []
    if task.manifest != told.get("manifest"):
        refused.append(f"the task built now is not the task the run read ("
                       f"{', '.join(_differ(task.manifest, told.get('manifest') or {})[:3])})")
    if sha256_file(kit_dir / genkits.MANIFEST) != (made.get("kit") or {}).get(
            "kit_yaml_sha256"):
        refused.append("the kit's kit.yaml is not the one the record holds")
    refused += task_problems(made, told, task.manifest, None)
    refused += output_problems(made, kept, workspace, transcript, answers, known)
    if refused:
        return None, refused
    return save(kept, make(kit_dir, task.folder, told["manifest"], kept)), []
