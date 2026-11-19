"""A stub reader that speaks the stream-json of the Claude Code CLI (ADR-010, decision 9).

    python -m specfirst.harness.stub -p "<prompt>" --output-format stream-json ...

It takes the command line the adapter builds, refuses one that is not that
command line (its `result` is then an error), and does what the plan in
the file named by SPECFIRST_STUB_PLAN says, in the task folder it runs in:

    records      decision records, written to out/decisions.jsonl
    unmapped     records written to out/unmapped.jsonl
    asks         {decision, unit, question}: each runs bin/ask
    check        run bin/check
    read         files whose text it prints as a tool result (a planted leak)
    write        {path: text}: more files of the workspace
    sleep        seconds to wait before it ends
    error        a message: the run ends with is_error
    turns, usage, model_usage     what its result event reports

Each step is printed as the CLI prints a tool use and its result. Nothing in
it reads a clock or draws a random number.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from specfirst.harness import adapter

SESSION = "stub-session"


def _print(event: dict) -> None:
    sys.stdout.write(json.dumps(event, sort_keys=True) + "\n")
    sys.stdout.flush()


def _parse(argv: list[str]) -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-p", dest="prompt")
    for flag in ("--output-format", "--model", "--max-turns", "--max-budget-usd",
                 "--permission-mode", "--permission-prompts", "--tools", "--allowedTools",
                 "--disallowedTools", "--settings", "--setting-sources"):
        parser.add_argument(flag)
    for flag in ("--verbose", "--strict-mcp-config", "--disable-slash-commands",
                 "--no-session-persistence"):
        parser.add_argument(flag, action="store_true")
    return parser.parse_known_args(argv)


def _tool(number: int, name: str, given: dict, output: str) -> None:
    ident = f"toolu_stub_{number:03d}"
    _print({"type": "assistant", "session_id": SESSION, "parent_tool_use_id": None,
            "message": {"role": "assistant", "model": "stub", "content": [
                {"type": "tool_use", "id": ident, "name": name, "input": given}]}})
    _print({"type": "user", "session_id": SESSION, "parent_tool_use_id": None,
            "message": {"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": ident, "content": output}]}})


def _jsonl(records: list[dict]) -> str:
    return "".join(json.dumps(record, sort_keys=True) + "\n" for record in records)


def main(argv: list[str] | None = None) -> int:
    args, rest = _parse(list(sys.argv[1:] if argv is None else argv))
    plan_file = os.environ.get("SPECFIRST_STUB_PLAN")
    plan = json.loads(Path(plan_file).read_text(encoding="utf-8")) if plan_file else {}
    task = Path.cwd()
    _print({"type": "system", "subtype": "init", "session_id": SESSION, "cwd": str(task),
            "model": args.model, "tools": (args.allowedTools or "").split(","),
            "mcp_servers": [], "permissionMode": args.permission_mode,
            "claude_code_version": "stub"})
    problems = []
    try:
        settings = json.loads(Path(str(args.settings)).read_text(encoding="ascii"))
    except (OSError, ValueError):
        settings = {}
        problems.append("no settings file")
    command = adapter.command(adapter.Reader(("stub",), str(args.model), str(args.prompt)),
                              Path(str(args.settings)), adapter.Budget(
                                  int(args.max_turns or 0), 0,
                                  float(args.max_budget_usd or 0)))[1:]
    given = list(sys.argv[1:] if argv is None else argv)
    if given != command:
        problems.append("the command line is not the adapter's")
    if not adapter.denied_roots(settings):
        problems.append("the settings deny nothing")
    if rest:
        problems.append(f"unknown arguments {rest}")
    number = 0
    if not problems:
        for path in plan.get("read") or []:
            number += 1
            text = Path(path).read_text(encoding="utf-8", errors="replace")
            _tool(number, "Read", {"file_path": path}, text)
        for item in plan.get("asks") or []:
            number += 1
            line = ["bash", "bin/ask", item["question"], "--decision", item["decision"]]
            if item.get("unit"):
                line += ["--unit", item["unit"]]
            done = subprocess.run(line, cwd=task, capture_output=True, text=True)
            _tool(number, "Bash", {"command": " ".join(line[1:])}, done.stdout + done.stderr)
        out = task / "out"
        out.mkdir(exist_ok=True)
        for name, key in (("decisions.jsonl", "records"), ("unmapped.jsonl", "unmapped")):
            if key in plan:
                number += 1
                text = _jsonl(plan[key])
                (out / name).write_text(text, encoding="utf-8", newline="\n")
                _tool(number, "Write", {"file_path": f"out/{name}", "content": text},
                      f"File created successfully at: out/{name}")
        for name, text in sorted((plan.get("write") or {}).items()):
            number += 1
            (task / name).parent.mkdir(parents=True, exist_ok=True)
            (task / name).write_text(text, encoding="utf-8", newline="\n")
            _tool(number, "Write", {"file_path": name, "content": text}, "written")
        if plan.get("check"):
            number += 1
            done = subprocess.run(["bash", "bin/check"], cwd=task, capture_output=True,
                                  text=True)
            _tool(number, "Bash", {"command": "bin/check"}, done.stdout + done.stderr)
        if plan.get("sleep"):
            time.sleep(float(plan["sleep"]))
    error = "; ".join(problems) or plan.get("error")
    usage = plan.get("usage") or {"input_tokens": 0, "output_tokens": 0,
                                  "cache_creation_input_tokens": 0,
                                  "cache_read_input_tokens": 0}
    _print({"type": "result", "subtype": "success", "is_error": bool(error),
            "duration_ms": 0, "duration_api_ms": 0,
            "num_turns": int(plan.get("turns", number + 1)),
            "result": f"stub: {error}" if error else "done", "session_id": SESSION,
            "total_cost_usd": 0, "usage": usage, "modelUsage": plan.get("model_usage") or {},
            "permission_denials": []})
    return 0


if __name__ == "__main__":
    sys.exit(main())
