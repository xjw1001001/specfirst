"""`specfirst view <kit>`: write the review page of a built kit (issue #31, ADR-022).

The page goes to build/kits/<kit>/viewer/index.html, next to the build it
shows. It reads the recomputation of issue #29 when there is one
(build/recompute/<kit>), and the classes of a P4 matrix when one is given
(`--p4`, a file of `specfirst gen separate`: its `decisions`, each with
`id`, `unit`, `class` and the value the class was found at, `value` and
`gold`; a record with another value is not tested). It prints what the page
checks find and the
acceptance lines of issue #31 on every output of the kit.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

from specfirst.paths import build_dir
from specfirst.viewer import check, model, page

VIEWER = "viewer/index.html"
Out = Callable[[str], None]


def read_p4(path: Path | None) -> dict[tuple[str, str], model.P4Run] | None:
    """(decision ID, unit) -> its run: the class and the value it was found at, from a
    matrix file."""
    if path is None:
        return None
    matrix = json.loads(path.read_text(encoding="ascii"))
    return {(str(item["id"]), str(item["unit"])): model.P4Run(
                str(item["class"]), model.canonical(item["value"]), str(item["gold"]))
            for item in matrix.get("decisions") or []}


def write(root: Path, kit_id: str, folder: Path | None = None,
          p4: dict[tuple[str, str], model.P4Run] | None = None
          ) -> tuple[Path, model.Review, str]:
    """Load the review, write the page; the page's path, the review and its text."""
    folder = folder or build_dir(root) / "kits" / kit_id
    review = model.load(root, kit_id, folder, p4=p4)
    text = page.html(review)
    target = folder / VIEWER
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(text.encode("utf-8"))
    return target, review, text


def main(root: Path, kit_id: str, folder: Path | None = None, p4_file: Path | None = None,
         out: Out = print) -> int:
    try:
        target, review, text = write(root, kit_id, folder, read_p4(p4_file))
    except (model.ReviewError, OSError, ValueError, KeyError) as error:
        out(f"view {kit_id}: FAIL ({error})")
        return 1
    # What the review could not read (no recomputation, a result the ARD lacks) is printed
    # on the page and counted here (the review of issue #31, F3).
    problems = [*review.problems, *check.page_problems(text, review)]
    lines, found = check.acceptance(review, text, tuple(o.id for o in review.outputs))
    for line in lines:
        out(line)
    for problem in [*problems, *found][:20]:
        out(f"  problem: {problem}")
    total = len(problems) + len(found)
    out(f"view {kit_id}: {target} ({len(text.encode('utf-8'))} bytes), "
        f"{len(review.analyses)} analyses, {len(review.cells)} cells with a panel, "
        f"{len(review.sheet)} lines on the sheet; {total} problems")
    return 0 if total == 0 else 1
