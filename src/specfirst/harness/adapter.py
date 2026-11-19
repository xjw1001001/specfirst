"""How a reader is run: the Claude Code CLI in print mode (PLAN.md section 11.1;
docs/decisions/ADR-010.md, decisions 1, 3 and 4).

    claude -p "<prompt>" --output-format stream-json --verbose --model claude-opus-5-5
           --max-turns N --max-budget-usd D --permission-mode manual
           --permission-prompts none --tools Read,Glob,Grep,Write,Edit,Bash
           --allowedTools ... --disallowedTools ... --settings <run>/settings.json
           --setting-sources "" --strict-mcp-config --disable-slash-commands
           --no-session-persistence

The flags are those of the CLI 2.1.327 (ADR-010, decision 1): `manual` is the
permission mode that asks, and `--permission-prompts none` denies whatever
would ask; `--tools` loads no other built-in tool; no user, project or local
settings, no MCP server, no skill or command, and no session saved to disk.

The reader's working directory is the task folder. The settings file denies
the file tools on every protected folder. Every line the CLI prints is one
JSON event; they are written to the run's transcript as they come. The run
ends with a `result` event, whose `is_error` says whether it failed (the
exit status of a failed call can be 0). After `budget.seconds` the process
is stopped.

`SPECFIRST_READER` names the program: a JSON list or a command line, default
`claude`. A program whose name ends in `.exe` is a Windows program started
through WSL interop: its paths are given in Windows form, and the tools it
runs reach the harness through `wsl.exe`. The stub reader
(specfirst.harness.stub) speaks the same stream-json and stands in for the
CLI in tests and in the gate.
"""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

from specfirst.harness.record import MODEL, Budget

TRANSCRIPT = "transcript.jsonl"
SETTINGS = "settings.json"
PROMPT = "Read TASK.md in the current folder and do the task it describes."
TOOLS = ("Read", "Glob", "Grep", "Write", "Edit", "Bash")
# A rule for each of the two tools, in the form of `Bash(<prefix> *)` and the older
# `Bash(<prefix>:*)`.
ALLOWED_TOOLS = ("Read", "Glob", "Grep", "Write", "Edit",
                 *(f"Bash({tool}{form})" for tool in ("bin/ask", "./bin/ask", "bin/check",
                                                     "./bin/check") for form in (" *", ":*")))
DISALLOWED_TOOLS = ("Agent", "Task", "WebFetch", "WebSearch", "NotebookEdit", "Skill",
                    "SlashCommand", "BashOutput", "KillShell")
FILE_TOOLS = ("Read", "Edit", "Write", "Glob", "Grep")
WSL_ROOTS = ("//wsl.localhost", "//wsl$")


@dataclass(frozen=True)
class Reader:
    argv: tuple[str, ...]
    model: str = MODEL
    prompt: str = PROMPT

    @property
    def windows(self) -> bool:
        return self.argv[0].lower().endswith(".exe")

    @property
    def stub(self) -> bool:
        return "specfirst.harness.stub" in self.argv


def default_reader(model: str = MODEL) -> Reader:
    named = os.environ.get("SPECFIRST_READER", "").strip()
    if not named:
        return Reader(("claude",), model)
    argv = json.loads(named) if named.startswith("[") else shlex.split(named)
    return Reader(tuple(str(item) for item in argv), model)


def stub_reader() -> Reader:
    return Reader((sys.executable, "-m", "specfirst.harness.stub"))


def windows_path(path: Path) -> str:
    """A path under /mnt/<drive>/ in Windows form; the WSL share for any other."""
    text = path.resolve().as_posix()
    parts = text.split("/")
    if len(parts) > 3 and parts[1] == "mnt" and len(parts[2]) == 1:
        return f"{parts[2].upper()}:\\" + "\\".join(parts[3:])
    distro = os.environ.get("WSL_DISTRO_NAME", "Ubuntu-24.04")
    return f"\\\\wsl.localhost\\{distro}" + text.replace("/", "\\")


def rule_paths(path: Path, windows: bool) -> list[str]:
    """The forms of a path in a permission rule (`//` starts an absolute path)."""
    text = path.resolve().as_posix()
    parts = text.split("/")
    if not windows:
        return [f"/{text}"]
    if len(parts) > 3 and parts[1] == "mnt" and len(parts[2]) == 1:
        rest = "/".join(parts[3:])
        return [f"//{parts[2]}/{rest}", f"//{parts[2].upper()}:/{rest}"]
    distro = os.environ.get("WSL_DISTRO_NAME", "Ubuntu-24.04")
    return [f"{root}/{distro}{text}" for root in WSL_ROOTS]


WRITE_TOOLS = ("Edit", "Write")


def settings(protected: list[Path], windows: bool, tools_dir: Path | None = None) -> dict:
    """The settings of a run: the file tools denied on every protected folder, and the
    tools that write denied on the task's own bin/ (the wrappers that Bash may run)."""
    roots = [form for path in protected for form in rule_paths(path, windows)]
    if windows:
        roots += list(WSL_ROOTS)
    deny = [f"{tool}({root}/**)" for root in roots for tool in FILE_TOOLS]
    if tools_dir is not None:
        deny += [f"{tool}({form}/**)" for form in rule_paths(tools_dir, windows)
                 for tool in WRITE_TOOLS]
    return {"permissions": {"deny": deny}}


def denied_roots(settings_value: dict, tools: tuple[str, ...] = FILE_TOOLS) -> set[str]:
    """The folders the settings deny every one of `tools` on."""
    by_root: dict[str, set[str]] = {}
    for rule in (settings_value.get("permissions") or {}).get("deny") or []:
        if "(" in rule and rule.endswith("/**)"):
            tool, root = rule[:-4].split("(", 1)
            by_root.setdefault(root, set()).add(tool)
    return {root for root, held in by_root.items() if held >= set(tools)}


def command(reader: Reader, settings_file: Path, budget: Budget) -> list[str]:
    path = windows_path(settings_file) if reader.windows else str(settings_file)
    return [*reader.argv, "-p", reader.prompt, "--output-format", "stream-json", "--verbose",
            "--model", reader.model, "--max-turns", str(budget.turns),
            "--max-budget-usd", f"{budget.usd:g}",
            "--permission-mode", "manual", "--permission-prompts", "none",
            "--tools", ",".join(TOOLS),
            "--allowedTools", ",".join(ALLOWED_TOOLS),
            "--disallowedTools", ",".join(DISALLOWED_TOOLS),
            "--settings", path, "--setting-sources", "", "--strict-mcp-config",
            "--disable-slash-commands", "--no-session-persistence"]


def flag_problems(argv: list[str], budget: Budget | None = None) -> list[str]:
    """Why a command line does not run a reader with the flags of ADR-010, decision 1
    (and, given a budget, with its turns and dollars)."""
    found = []

    def value(flag: str) -> str | None:
        return argv[argv.index(flag) + 1] if flag in argv[:-1] else None

    wanted_values = [("--output-format", "stream-json"), ("--model", MODEL),
                     ("--permission-mode", "manual"), ("--permission-prompts", "none"),
                     ("--tools", ",".join(TOOLS)), ("--setting-sources", "")]
    if budget is not None:
        wanted_values += [("--max-turns", str(budget.turns)),
                          ("--max-budget-usd", f"{budget.usd:g}")]
    for flag, wanted in wanted_values:
        if value(flag) != wanted:
            found.append(f"{flag} is {value(flag)!r}, not {wanted!r}")
    for flag in ("-p", "--verbose", "--strict-mcp-config", "--max-turns", "--max-budget-usd",
                 "--settings", "--disable-slash-commands", "--no-session-persistence"):
        if flag not in argv:
            found.append(f"no {flag}")
    allowed = set((value("--allowedTools") or "").split(","))
    if allowed != set(ALLOWED_TOOLS):
        found.append(f"--allowedTools is {sorted(allowed)}")
    if set(DISALLOWED_TOOLS) - set((value("--disallowedTools") or "").split(",")):
        found.append("--disallowedTools leaves out "
                     + ", ".join(sorted(set(DISALLOWED_TOOLS) - set(
                         (value("--disallowedTools") or "").split(",")))))
    if "--add-dir" in argv or "--dangerously-skip-permissions" in argv:
        found.append("the command widens the reader's reach")
    return found


def command_problems(argv: list[str], settings_value: dict, protected: list[Path],
                     windows: bool, tools_dir: Path | None = None,
                     budget: Budget | None = None) -> list[str]:
    """Why a command line and its settings do not run a reader as ADR-010 says: its
    flags; every protected folder denied to every file tool; the task's bin/ denied to
    the tools that write."""
    found = flag_problems(argv, budget)
    roots = denied_roots(settings_value)
    for path in protected:
        missing = [form for form in rule_paths(path, windows) if form not in roots]
        if missing:
            found.append(f"the settings do not deny the file tools on {path}")
    if windows and not set(WSL_ROOTS) <= roots:
        found.append("the settings do not deny the WSL file system")
    if tools_dir is not None:
        writable = denied_roots(settings_value, WRITE_TOOLS)
        if any(form not in writable for form in rule_paths(tools_dir, windows)):
            found.append(f"the settings let the reader write the tools in {tools_dir}")
    return found


@dataclass
class Outcome:
    argv: list[str]
    result: dict | None
    events: int
    wall_seconds: float
    stopped: bool
    returncode: int | None
    stderr: str = ""
    init: dict = field(default_factory=dict)


def run(reader: Reader, task_dir: Path, run_dir: Path, settings_value: dict, budget: Budget,
        env: dict[str, str] | None = None) -> Outcome:
    """Run a reader in a task folder; its events go to <run>/transcript.jsonl."""
    settings_file = run_dir / SETTINGS
    settings_file.write_text(json.dumps(settings_value, indent=1, sort_keys=True) + "\n",
                             encoding="ascii", newline="\n")
    argv = command(reader, settings_file, budget)
    transcript = run_dir / TRANSCRIPT
    state: dict = {"events": 0, "result": None, "init": {}}
    errors: list[str] = []
    started = time.monotonic()
    process = subprocess.Popen(argv, cwd=task_dir, stdin=subprocess.DEVNULL,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               env={**os.environ, **(env or {})})

    def read_out() -> None:
        assert process.stdout is not None
        with open(transcript, "wb") as handle:
            for raw in process.stdout:
                handle.write(raw)
                handle.flush()
                try:
                    event = json.loads(raw.decode("utf-8", errors="replace"))
                except json.JSONDecodeError:
                    continue
                state["events"] += 1
                if isinstance(event, dict) and event.get("type") == "result":
                    state["result"] = event
                if isinstance(event, dict) and event.get("subtype") == "init":
                    state["init"] = event

    def read_err() -> None:
        assert process.stderr is not None
        errors.append(process.stderr.read().decode("utf-8", errors="replace"))

    threads = [threading.Thread(target=read_out), threading.Thread(target=read_err)]
    for thread in threads:
        thread.start()
    stopped = False
    try:
        process.wait(timeout=budget.seconds)
    except subprocess.TimeoutExpired:
        stopped = True
        process.kill()
        process.wait()
    for thread in threads:
        thread.join()
    return Outcome(argv, state["result"], state["events"], time.monotonic() - started, stopped,
                   process.returncode, "".join(errors)[-4000:], state["init"])
