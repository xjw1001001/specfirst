"""Compare the recomputation scripts' results with the ARD rows (issue #29, ADR-021).

    python compare.py <bundle folder> <folder of the outputs> <folder of the ARD rows> <report>

Standalone: the standard library only. For each analysis of plan.json the
output <event>/<analysis>.csv must hold exactly the rows of the ARD: the same
operations and groups, a count exactly, any other value within the relative
tolerance of the plan (an absolute 1e-12 near 0), and missing where the ARD is
missing. Each analysis is reported `reproduced`, `differs` (with its rows) or
`not covered` (with the reason). The report is JSON; a line per analysis is
printed.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ABSOLUTE = 1e-12
SHOWN = 10  # rows that differ, printed per analysis


def ard_key(row: dict, groupings: int) -> tuple[str, ...]:
    parts = [str(row["operation_id"])]
    for n in range(1, groupings + 1):
        if row.get(f"group{n}_groupId") is not None:
            parts.append(str(row[f"group{n}_groupId"]))
        elif row.get(f"group{n}_groupValue") is not None:
            parts.append("=" + str(row[f"group{n}_groupValue"]))
        else:
            parts.append("*")
    return tuple(parts)


def number(text: str) -> float | None:
    return None if text == "" else float(text)


def same(mine: float | None, theirs: float | None, result: str, tolerance: float) -> bool:
    if mine is None or theirs is None:
        return mine is None and theirs is None
    if result == "integer":
        return mine == theirs
    gap = abs(mine - theirs)
    return gap <= ABSOLUTE or gap <= tolerance * max(abs(mine), abs(theirs))


def relative(mine: float | None, theirs: float | None) -> float:
    if mine is None or theirs is None or mine == theirs:
        return 0.0
    return abs(mine - theirs) / max(abs(mine), abs(theirs))


def judge(entry: dict, ard: list[dict], output: Path) -> dict:
    line = {"analysis": entry["analysis"], "event": entry["event"]}
    if "not_covered" in entry:
        return {**line, "status": "not covered", "reason": entry["not_covered"]}
    groupings = len(entry["groupings"])
    expected = {ard_key(row, groupings): row for row in ard}
    if not output.is_file():
        return {**line, "status": "differs", "reason": "no output", "rows": len(expected)}
    with open(output, encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    header, body = rows[0], rows[1:]
    if len(header) != groupings + 2:
        return {**line, "status": "differs", "reason": f"the output has the columns {header}"}
    made: dict[tuple[str, ...], float | None] = {}
    for row in body:
        key = tuple(row[:-1])
        if key in made:
            return {**line, "status": "differs", "reason": f"the row {list(key)} twice"}
        made[key] = number(row[-1])
    differ = []
    largest = 0.0
    for key in sorted(set(expected) | set(made)):
        if key not in made:
            differ.append({"row": list(key), "script": "no row",
                           "ard": expected[key]["raw_value"]})
            continue
        if key not in expected:
            differ.append({"row": list(key), "script": made[key], "ard": "no row"})
            continue
        theirs = expected[key]["raw_value"]
        result = entry["operations"].get(key[0], {}).get("result", "number")
        if not same(made[key], theirs, result, entry["tolerance"]):
            differ.append({"row": list(key), "script": made[key], "ard": theirs})
        else:
            largest = max(largest, relative(made[key], theirs))
    if differ:
        return {**line, "status": "differs", "rows": len(expected), "differ": differ}
    return {**line, "status": "reproduced", "rows": len(expected), "largest": largest}


def compare(bundle: Path, outputs: Path, ard_dir: Path) -> dict:
    plan = json.loads((bundle / "plan.json").read_text(encoding="ascii"))
    rows: dict[str, dict[str, list[dict]]] = {}
    for entry in plan["analyses"]:
        event = entry["event"]
        if event not in rows:
            rows[event] = {}
            with open(ard_dir / f"{event}.jsonl", encoding="utf-8") as handle:
                for text in handle:
                    if text.strip():
                        row = json.loads(text)
                        rows[event].setdefault(row["analysis_id"], []).append(row)
    lines = [judge(entry, rows[entry["event"]].get(entry["analysis"], []),
                   outputs / entry["event"] / f"{entry['analysis']}.csv")
             for entry in plan["analyses"]]
    counts: dict[str, int] = {}
    for line in lines:
        counts[line["status"]] = counts.get(line["status"], 0) + 1
    return {"kit": plan["kit"], "counts": counts, "analyses": lines}


def text_lines(report: dict) -> list[str]:
    lines = []
    for line in report["analyses"]:
        head = f"{line['status']:12s} {line['event']}/{line['analysis']}"
        if line["status"] == "reproduced":
            lines.append(f"{head}: {line['rows']} rows, largest relative difference "
                         f"{line['largest']:.1e}")
        elif line["status"] == "not covered":
            lines.append(f"{head}: {line['reason']}")
        elif "differ" in line:
            lines.append(f"{head}: {len(line['differ'])} of {line['rows']} rows")
            for item in line["differ"][:SHOWN]:
                lines.append(f"    {'/'.join(item['row'])}: script {item['script']}, "
                             f"ARD {item['ard']}")
        else:
            lines.append(f"{head}: {line['reason']}")
    counts = ", ".join(f"{k} {v}" for k, v in sorted(report["counts"].items()))
    lines.append(f"{report['kit']}: {sum(report['counts'].values())} analyses: {counts}")
    return lines


if __name__ == "__main__":
    made = compare(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
    Path(sys.argv[4]).write_text(json.dumps(made, indent=1, sort_keys=True) + "\n",
                                 encoding="ascii")
    print("\n".join(text_lines(made)))
    sys.exit(0 if set(made["counts"]) <= {"reproduced"} else 1)
