"""A score as text: every number with its denominator (PLAN.md section 9.3, rule R8)."""

from __future__ import annotations

import json

from specfirst.score import attribute
from specfirst.score.reading import DIMENSIONS, Rate, Reading
from specfirst.score.scorer import Result


def _of(count: int, total: int) -> str:
    return f"{count} of {total}" if total else "-"


def _rate(name: str, rate: Rate, what: str) -> str:
    def share(value: float | None) -> str:
        return "none to judge" if value is None else f"{value:.2f}"

    return (f"  {name}: {rate.given} given, {rate.gold} in gold ({what}), {rate.hits} of them "
            f"right; precision {share(rate.precision)}, recall {share(rate.recall)}")


def _value(value: object) -> str:
    return "nothing" if value is None else json.dumps(value, sort_keys=True)


def reading_lines(read: Reading) -> list[str]:
    said = [f"reading score: {len(read.decisions)} gold decisions of the units "
            f"{', '.join(read.units)}"]
    for by, title in (("class", "class"), ("unit", "unit")):
        said.append(f"  by {title}:".ljust(32) + "decisions  " + "".join(
            name.ljust(12) for name in DIMENSIONS))
        for row in read.counts(by):
            said.append(f"    {row[by]:26s}  {row['decisions']:9d}  " + "".join(
                _of(row[name], row[f"{name}_of"]).ljust(12) for name in DIMENSIONS))
    said.append("  (value and status: right, of the decisions scored on it; quote: every quote "
                "stands in its document; span: a quote stands inside an anchor that gold cites)")
    said.append(_rate("asks", read.asks, "decisions with the status asked"))
    said.append(_rate("unmapped", read.unmapped, "what the catalog lacks"))
    wrong = read.wrong()
    said.append(f"  decisions a reviewer would have to change: {len(wrong)}")
    for item in wrong:
        said.append(f"    {item.key[0]} ({item.key[1]}), {item.gold_class}: gold "
                    f"{_value(item.gold_value)}; the candidate ({item.source}) has "
                    f"{_value(item.value_given)}")
    for item in read.decisions:
        marks = item.marks()
        bad = [name for name in ("status", "quote", "span") if marks[name] is False]
        if bad:
            said.append(f"    {item.key[0]} ({item.key[1]}): wrong in {', '.join(bad)}"
                        + (": " + "; ".join(item.notes) if item.notes else ""))
    apart = [item for item in read.decisions if item.identifiable == "unseparated"]
    if apart:
        said.append(f"  unseparated in gold, compared by value only: {len(apart)} "
                    + ", ".join(f"{item.key[0]} ({'right' if item.value else 'wrong'})"
                                for item in apart))
    counted = [item for item in read.decisions if not item.scored]
    if counted:
        said.append(f"  counted and not scored (gold_quirk, no_gold): {len(counted)}")
    if read.outside:
        said.append(f"  records of units that are not scored here, ignored: {len(read.outside)}")
    if read.unknown:
        said.append("  records for decisions that gold does not have: "
                    + ", ".join(f"{k[0]} ({k[1]})" for k in read.unknown))
    said += [f"  problem: {problem}" for problem in read.problems]
    return said


def owner_lines(name: str, owners: list[attribute.Owner],
                axes: list[attribute.AxisOwner]) -> list[str]:
    if not owners and not axes:
        return []
    said = [f"attribution, {name}: {len(owners)} wrong cells",
            "  layer  unit               decision                 cells  confirmed  "
            "first element that differs"]
    first: dict[tuple, str] = {}
    for owner in owners:
        key = (owner.layer, owner.unit or "-",
               ", ".join(k[0] for k in owner.decisions) or "-")
        first.setdefault(key, str(owner.element))
    for layer, unit, decisions, cells, confirmed in attribute.summary(owners):
        proved = "-" if decisions == "-" else f"{confirmed} of {cells}"
        said.append(f"  {layer:5s}  {unit:17s}  {decisions:23s}  {cells:5d}  {proved:9s}  "
                    f"{first[(layer, unit, decisions)]}")
    for axis in axes:
        decisions = ", ".join(k[0] for k in axis.decisions) or "-"
        proved = {None: "-", True: "yes", False: "no"}[axis.confirmed]
        said.append(f"  axis {axis.axis} of {axis.output}: layer {axis.layer}, decision "
                    f"{decisions}, confirmed {proved}, first element that differs "
                    f"{axis.element}")
    return said


def lines(result: Result) -> list[str]:
    said = [f"case {result.case}, arm {result.arm}, stage {result.stage}"]
    said += reading_lines(result.reading)
    said.append("build score:")
    for score in result.builds.values():
        said += ["  " + line for line in score.lines()]
    for name in result.builds:
        said += owner_lines(name, result.owners[name], result.axes[name])
    if result.silent:
        said.append("wrong by value, and these data cannot show it (alone, on gold, it changes "
                    "no cell and no axis of any dataset): "
                    + ", ".join(f"{key[0]} ({key[1]})" for key in result.silent))
    for key, changed in result.behind.items():
        said.append(f"wrong by value, and behind another owner: {key[0]} ({key[1]}); alone, on "
                    "gold, it changes " + ", ".join(
                        f"{count} cells or axes of {name}" for name, count in changed.items()))
    said.append(f"case {result.case}, arm {result.arm}: "
                f"{'every score is 100%' if result.perfect else 'not every score is 100%'}")
    return said
