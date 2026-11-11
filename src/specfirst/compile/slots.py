"""Typed slots of statement templates (PLAN.md section 4.4).

A statement template is a controlled English sentence with typed slots,
written as `{name}`. Every slot type has one canonical text form, so that
rendering a value and parsing the text back gives the same value, exactly.

| Type | Value | Text |
| --- | --- | --- |
| int | integer | `30`, `-1` |
| number | integer, or a float that is not a whole number | `5`, `2.5` |
| text | printable ASCII without a double quote | `"Week 24"` |
| name | upper-case identifier, optionally DATASET.VARIABLE | `DM.ARM` |
| list[T] | non-empty list of one of the four types above | `"a", "b"` |
| records | non-empty list of records with typed fields | items joined by `; ` |
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field

SCALARS = ("int", "number", "text", "name")
_INT = re.compile(r"-?(0|[1-9][0-9]*)")
_NUMBER = re.compile(r"-?(0|[1-9][0-9]*)(\.[0-9]+)?")
_NAME = re.compile(r"[A-Z][A-Z0-9_]*(\.[A-Z][A-Z0-9_]*)?")
_TEXT_BODY = re.compile(r"[ !#-~]+")  # printable ASCII without the double quote
_FIELD = re.compile(r"\{([a-z][a-z0-9_]*)\}")
SLOT_NAME = re.compile(r"^[a-z][a-z0-9_]*$")
LIST_SEPARATOR = ", "
RECORD_SEPARATOR = "; "


class SlotError(ValueError):
    """A value does not fit its slot, or a text is not the canonical form of one."""


@dataclass(frozen=True)
class Slot:
    name: str
    type: str
    minimum: float | None = None
    maximum: float | None = None
    choices: tuple | None = None
    fields: tuple[tuple[str, str], ...] = ()  # records: (field name, scalar type)
    item: str = ""  # records: the template of one record
    examples: tuple = field(default=(), compare=False)

    @property
    def item_type(self) -> str | None:
        """The scalar type of the items of a list slot."""
        if self.type.startswith("list[") and self.type.endswith("]"):
            return self.type[5:-1]
        return None


def slot_from_spec(name: str, spec: dict) -> Slot:
    """Build a slot from its declaration in a catalog entry."""
    if not SLOT_NAME.match(name) or name in ("rule", "output"):
        raise SlotError(f"slot name '{name}' is not allowed")
    kind = spec.get("type")
    slot = Slot(
        name=name,
        type=str(kind),
        minimum=spec.get("min"),
        maximum=spec.get("max"),
        choices=tuple(spec["choices"]) if spec.get("choices") is not None else None,
        fields=tuple((k, str(v)) for k, v in (spec.get("fields") or {}).items()),
        item=str(spec.get("item") or ""),
        examples=tuple(spec.get("examples") or ()),
    )
    if kind in SCALARS or slot.item_type in SCALARS:
        if slot.fields or slot.item:
            raise SlotError(f"slot '{name}': fields and item belong to the type records")
    elif kind == "records":
        if not slot.fields or not slot.item:
            raise SlotError(f"slot '{name}': the type records needs fields and item")
        for field_name, field_type in slot.fields:
            if field_type not in SCALARS:
                raise SlotError(f"slot '{name}': field '{field_name}' has no scalar type")
        used = _FIELD.findall(slot.item)
        if sorted(used) != sorted(k for k, _ in slot.fields):
            raise SlotError(f"slot '{name}': item must use every field exactly once")
        pieces = _FIELD.split(slot.item)[0::2]
        if any("{" in piece or "}" in piece or '"' in piece for piece in pieces):
            raise SlotError(f"slot '{name}': item has a stray brace or double quote")
        if any(piece == "" for piece in pieces[1:-1]):
            raise SlotError(f"slot '{name}': two fields of item touch each other")
        if RECORD_SEPARATOR.strip() in "".join(pieces):
            raise SlotError(f"slot '{name}': item may not contain the record separator")
    else:
        raise SlotError(f"slot '{name}': unknown type '{kind}'")
    return slot


# -- scalars -----------------------------------------------------------------


def _check_scalar(kind: str, value: object, where: str) -> None:
    if kind == "int":
        if isinstance(value, bool) or not isinstance(value, int):
            raise SlotError(f"{where}: expected an integer, got {value!r}")
    elif kind == "number":
        if isinstance(value, bool) or not isinstance(value, int | float):
            raise SlotError(f"{where}: expected a number, got {value!r}")
        if isinstance(value, float):
            if not math.isfinite(value) or value == int(value):
                raise SlotError(f"{where}: write a whole number as an integer, got {value!r}")
            if not _NUMBER.fullmatch(repr(value)):
                raise SlotError(f"{where}: {value!r} has no plain decimal form")
    elif kind == "text":
        if not isinstance(value, str) or not _TEXT_BODY.fullmatch(value):
            raise SlotError(f"{where}: expected printable ASCII text without '\"', got {value!r}")
        if value != value.strip():
            raise SlotError(f"{where}: text may not start or end with a space, got {value!r}")
    elif kind == "name":
        if not isinstance(value, str) or not _NAME.fullmatch(value):
            raise SlotError(f"{where}: expected a name such as DM.ARM, got {value!r}")
    else:
        raise SlotError(f"{where}: unknown scalar type '{kind}'")


def _render_scalar(kind: str, value: object) -> str:
    if kind == "text":
        return f'"{value}"'
    if kind == "number" and isinstance(value, float):
        return repr(value)
    return str(value)


def _parse_scalar(kind: str, text: str, pos: int, where: str) -> tuple[object, int]:
    if kind == "text":
        if text[pos : pos + 1] != '"':
            raise SlotError(f"{where}: expected a double quote at position {pos}")
        end = text.find('"', pos + 1)
        if end < 0:
            raise SlotError(f"{where}: unterminated text at position {pos}")
        value: object = text[pos + 1 : end]
        _check_scalar("text", value, where)
        return value, end + 1
    pattern = {"int": _INT, "number": _NUMBER, "name": _NAME}[kind]
    match = pattern.match(text, pos)
    if not match:
        raise SlotError(f"{where}: no {kind} at position {pos}")
    token = match.group(0)
    if kind == "name":
        value = token
    elif kind == "int" or "." not in token:
        if token == "-0":
            raise SlotError(f"{where}: '-0' is not canonical")
        value = int(token)
    else:
        value = float(token)
        if repr(value) != token:
            raise SlotError(f"{where}: '{token}' is not the canonical form of {value!r}")
    _check_scalar(kind, value, where)
    return value, match.end()


# -- slots -------------------------------------------------------------------


def check_value(slot: Slot, value: object) -> None:
    """Raise SlotError unless `value` is a canonical value of the slot."""
    where = f"slot '{slot.name}'"
    if slot.type in SCALARS:
        _check_scalar(slot.type, value, where)
        items: list = [value]
    elif slot.item_type:
        if not isinstance(value, list) or not value:
            raise SlotError(f"{where}: expected a non-empty list, got {value!r}")
        for item in value:
            _check_scalar(slot.item_type, item, where)
        if len({repr(item) for item in value}) != len(value):
            raise SlotError(f"{where}: an item is listed twice")
        items = list(value)
    else:
        if not isinstance(value, list) or not value:
            raise SlotError(f"{where}: expected a non-empty list of records, got {value!r}")
        names = [k for k, _ in slot.fields]
        for record in value:
            if not isinstance(record, dict) or sorted(record) != sorted(names):
                raise SlotError(f"{where}: a record needs exactly the fields {names}")
            for field_name, field_type in slot.fields:
                _check_scalar(field_type, record[field_name], f"{where}, field '{field_name}'")
        items = []
    for item in items:
        if slot.minimum is not None and item < slot.minimum:
            raise SlotError(f"{where}: {item!r} is below the minimum {slot.minimum!r}")
        if slot.maximum is not None and item > slot.maximum:
            raise SlotError(f"{where}: {item!r} is above the maximum {slot.maximum!r}")
        if slot.choices is not None and item not in slot.choices:
            raise SlotError(f"{where}: {item!r} is not one of {list(slot.choices)}")


def render_value(slot: Slot, value: object) -> str:
    """The canonical text of a value."""
    check_value(slot, value)
    if slot.type in SCALARS:
        return _render_scalar(slot.type, value)
    if slot.item_type:
        return LIST_SEPARATOR.join(_render_scalar(slot.item_type, item) for item in value)
    kinds = dict(slot.fields)
    rendered = []
    for record in value:
        rendered.append(
            _FIELD.sub(lambda m, r=record: _render_scalar(kinds[m.group(1)], r[m.group(1)]),
                       slot.item)
        )
    return RECORD_SEPARATOR.join(rendered)


def _parse_record(slot: Slot, text: str, pos: int) -> tuple[dict, int]:
    where = f"slot '{slot.name}'"
    kinds = dict(slot.fields)
    pieces = _FIELD.split(slot.item)
    record: dict = {}
    for index, piece in enumerate(pieces):
        if index % 2 == 0:
            if not text.startswith(piece, pos):
                raise SlotError(f"{where}: expected '{piece}' at position {pos}")
            pos += len(piece)
        else:
            record[piece], pos = _parse_scalar(kinds[piece], text, pos, where)
    return record, pos


def parse_value(slot: Slot, text: str, pos: int = 0) -> tuple[object, int]:
    """Read one value of the slot at `pos`; return it with the position after it."""
    where = f"slot '{slot.name}'"
    if slot.type in SCALARS:
        value, pos = _parse_scalar(slot.type, text, pos, where)
    elif slot.item_type:
        items = []
        item, pos = _parse_scalar(slot.item_type, text, pos, where)
        items.append(item)
        while text.startswith(LIST_SEPARATOR, pos):
            try:
                item, after = _parse_scalar(slot.item_type, text, pos + len(LIST_SEPARATOR), where)
            except SlotError:
                break  # the separator belongs to the sentence, not to the list
            items.append(item)
            pos = after
        value = items
    else:
        records = []
        record, pos = _parse_record(slot, text, pos)
        records.append(record)
        while text.startswith(RECORD_SEPARATOR, pos):
            try:
                record, after = _parse_record(slot, text, pos + len(RECORD_SEPARATOR))
            except SlotError:
                break
            records.append(record)
            pos = after
        value = records
    check_value(slot, value)
    return value, pos
