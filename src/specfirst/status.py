"""`specfirst status`: print the handover file of every track (PLAN.md section 2.4)."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path


def run(root: Path, out: Callable[[str], None] = print) -> int:
    files = sorted((root / "docs" / "state").glob("*.md"))
    if not files:
        out("no state files in docs/state/")
        return 1
    for path in files:
        out(f"==> docs/state/{path.name} <==")
        out(path.read_text(encoding="ascii").rstrip())
        out("")
    return 0
