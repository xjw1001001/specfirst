"""A house standard: the conventions a company ships to every study.

A house version is a folder, `standard/houses/<id>@<version>/` (ADR-020); its
label is `<id>@<version>`. It holds

    house.yaml     the manifest: the catalog version it needs, parent specs, templates
    defaults.yaml  from open-default@2: the defaults with their slot values and sources
    STANDARD.md    the citable standards document, in standard form
    adam/          parent yamaa specs, one per ADaM dataset
    ars/           ARS templates: common.yaml and one per table family
    layout/        layout templates, one per table family

In `open-default@1` the defaults are in the catalog (`house_default` of each
entry of `catalog@1`) and the manifest adds the slot values a default
alternative needs (`default_values`). From `open-default@2` the house holds
them in `defaults.yaml` (ADR-020, decision 2); a default there may depend on
the design (`cases` with `when`). STANDARD.md is rendered from the catalog
and the house, so it can never disagree with them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from specfirst.compile import predicate, versions
from specfirst.compile.catalog import Catalog, read_yaml
from specfirst.compile.standard_form import StandardForm, decision_record
from specfirst.paths import repo_root

DOCUMENT_ID = "house"


class HouseError(ValueError):
    """The house standard cannot be read or does not fit the catalog."""


@dataclass(frozen=True)
class House:
    directory: Path
    id: str
    version: int
    title: str
    catalog: str
    default_values: dict  # entry ID -> slot values, or unit -> slot values (open-default@1)
    adam: dict  # dataset -> {parent, inputs: {name: file stem}, output: file stem}
    ars: dict  # {common, families: {unit: file}}
    layout: dict  # {families: {unit: file}}
    raw: dict = field(compare=False, default_factory=dict)
    catalog_version: int = 1
    defaults_file: dict | None = None  # defaults.yaml as read, from open-default@2

    @property
    def label(self) -> str:
        return f"{self.id}@{self.version}"

    @property
    def catalog_label(self) -> str:
        """The catalog version the house needs."""
        return f"catalog@{self.catalog_version}"

    def read(self, relative: str) -> object:
        return read_yaml(self.directory / relative)


def default_dir(root: Path | None = None, label: str | None = None) -> Path:
    """The folder of a house version; without a label, the default (versions.DEFAULT_HOUSE)."""
    return versions.folder(root or repo_root(), label or versions.DEFAULT_HOUSE)


def load(directory: Path | None = None) -> House:
    directory = directory or default_dir()
    path = directory / "house.yaml"
    if not path.is_file():
        raise HouseError(f"no house standard at {directory}")
    raw = read_yaml(path)
    if not isinstance(raw, dict):
        raise HouseError(f"{path} is not a mapping")
    defaults_file = None
    if raw.get("defaults"):
        defaults_path = directory / str(raw["defaults"])
        if not defaults_path.is_file():
            raise HouseError(f"{path} names {raw['defaults']}, which is missing")
        defaults_file = read_yaml(defaults_path)
        if not isinstance(defaults_file, dict):
            raise HouseError(f"{defaults_path} is not a mapping")
    return House(
        directory=directory,
        id=str(raw.get("house", "")),
        version=int(raw.get("version", 0)),
        title=str(raw.get("title", "")),
        catalog=str(raw.get("catalog", "")),
        default_values=dict(raw.get("default_values") or {}),
        adam=dict(raw.get("adam") or {}),
        ars=dict(raw.get("ars") or {}),
        layout=dict(raw.get("layout") or {}),
        raw=raw,
        catalog_version=int(raw.get("catalog_version", 1)),
        defaults_file=defaults_file,
    )


def load_pair(root: Path | None, catalog_label: str | None = None,
              house_label: str | None = None) -> tuple[Catalog, House]:
    """A catalog and a house by label; a house that does not fit is refused.

    Without labels, the default pair. With a house and no catalog, the catalog
    version the house needs.
    """
    from specfirst.compile import catalog as catalogs

    house = load(default_dir(root, house_label))
    if catalog_label is None and house_label is not None:
        catalog_label = house.catalog_label
    catalog = catalogs.load(catalogs.default_dir(root, catalog_label))
    require_fit(catalog, house)
    return catalog, house


def fit_problems(catalog: Catalog, house: House) -> list[str]:
    """A house is used with the catalog version it names (ADR-020, decision 3)."""
    problems = []
    if house.catalog != catalog.name:
        problems.append(f"house: made for the catalog '{house.catalog}', not '{catalog.name}'")
    if house.catalog_label != catalog.label:
        problems.append(f"house: {house.label} needs {house.catalog_label}, not {catalog.label}")
    if catalog.has_defaults == (house.defaults_file is not None):
        where = "its entries" if catalog.has_defaults else "no entry"
        problems.append(f"house: {catalog.label} holds defaults in {where}, and {house.label} "
                        f"{'has' if house.defaults_file is not None else 'has no'} "
                        "defaults.yaml")
    return problems


def require_fit(catalog: Catalog, house: House) -> None:
    problems = fit_problems(catalog, house)
    if problems:
        raise HouseError("; ".join(problems))


def _item(house: House, entry_id: str, unit: str, per_family: bool) -> object:
    """The item of defaults.yaml for an (entry, unit): a choice, cases, or None if absent."""
    body = ((house.defaults_file or {}).get("defaults") or {}).get(entry_id)
    if per_family and isinstance(body, dict) and "units" in body:
        return (body.get("units") or {}).get(unit)
    return body


def choices(house: House, entry_id: str, unit: str, per_family: bool) -> list[dict]:
    """The choices of defaults.yaml for an (entry, unit): one, or the cases in order."""
    item = _item(house, entry_id, unit, per_family)
    if not isinstance(item, dict):
        return []
    if "cases" in item:
        return [case for case in item.get("cases") or [] if isinstance(case, dict)]
    return [item]


def choice(catalog: Catalog, house: House, entry_id: str, unit: str,
           features: dict[str, bool] | None = None) -> dict | None:
    """The default choice of an (entry, unit): {rule, values?, sources?}, or None.

    A default by design (`cases`) needs the design features; without them it
    raises, since the house cannot say which case holds.
    """
    entry = catalog.entry(entry_id)
    if house.defaults_file is None:
        rule = entry.default_for(unit)
        if rule is None:
            return None
        slots = house.default_values.get(entry_id) or {}
        if isinstance(slots.get(unit), dict):
            slots = slots[unit]
        values = {k: v for k, v in slots.items() if k not in catalog.units}
        return {"rule": rule, **({"values": values} if values else {})}
    found = choices(house, entry_id, unit, entry.per_family)
    if not found:
        return None
    if len(found) > 1 or "when" in found[0]:
        if features is None:
            raise HouseError(f"{entry_id} ({unit}): the default of {house.label} depends on the "
                             "design; give its features")
        for case in found:
            if "when" not in case or predicate.evaluate(predicate.parse(case["when"]), features):
                return case if case.get("rule") is not None else None
        return None
    return found[0] if found[0].get("rule") is not None else None


def by_design(catalog: Catalog, house: House, entry_id: str, unit: str) -> bool:
    """True when the default of an (entry, unit) depends on the design."""
    if house.defaults_file is None:
        return False
    found = choices(house, entry_id, unit, catalog.entry(entry_id).per_family)
    return len(found) > 1 or bool(found and "when" in found[0])


def default_value(catalog: Catalog, house: House, entry_id: str, unit: str,
                  features: dict[str, bool] | None = None) -> dict | None:
    """The value of the house default of an entry for a unit, or None."""
    found = choice(catalog, house, entry_id, unit, features)
    if found is None:
        return None
    return {"rule": found["rule"], **(found.get("values") or {})}


def defaults(catalog: Catalog, house: House,
             features: dict[str, bool] | None = None) -> list[dict]:
    """`id`, `unit` and `value` of every default, in catalog order.

    Without design features, a default that depends on the design is left out.
    """
    found = []
    for entry_id, unit in catalog.keys():
        if features is None and by_design(catalog, house, entry_id, unit):
            continue
        value = default_value(catalog, house, entry_id, unit, features)
        if value is not None:
            found.append({"id": entry_id, "unit": unit, "value": value})
    return found


def without_default(catalog: Catalog, house: House | None = None) -> list[tuple[str, str]]:
    """The (entry ID, unit) pairs that have no house default: state them or ask.

    With a house of defaults.yaml, a default by design is not listed here.
    """
    if house is None or house.defaults_file is None:
        return [(e, u) for e, u in catalog.keys() if catalog.entry(e).default_for(u) is None]
    return [(e, u) for e, u in catalog.keys()
            if not by_design(catalog, house, e, u)
            and default_value(catalog, house, e, u) is None]


def standards_document(catalog: Catalog, house: House) -> str:
    """The text of STANDARD.md: every default as a statement with its anchor."""
    if house.defaults_file is not None:
        return _document(catalog, house)
    form = StandardForm(catalog)
    preface = (
        f"This is the house standard {house.label}: {house.title}.",
        "Each numbered statement below is a default. It holds for a study whenever the "
        "study's protocol and statistical analysis plan do not state the decision. A "
        "decision taken from this document has the status `default` and the class "
        "`house_default`, and cites the statement by its anchor, for example "
        f"`doc:{DOCUMENT_ID}#1/s1`. A line that starts with \"Meaning:\" repeats what the "
        "catalog says the statement means; it is not a statement of its own.",
        "The statements are in the standard form of the decision catalog: a parser reads "
        "each one back to its decision. Do not edit this file by hand. It is rendered "
        "from the catalog and from `house.yaml`; `specfirst gate std-1` fails when it "
        "differs.",
    )
    text = form.render_document(DOCUMENT_ID, f"House standard {house.label}",
                                defaults(catalog, house), preface, explain=True)
    lines = [text.rstrip("\n"), "", "## Decisions without a default", "",
             "This standard sets no default for the decisions below. The study documents "
             "state them, or a person is asked. They are never guessed.", ""]
    for entry_id, unit in without_default(catalog, house):
        entry = catalog.entry(entry_id)
        scope = f" ({unit})" if entry.per_family else ""
        lines.append(f"- `{entry_id}`{scope}: {entry.question}")
    return "\n".join(lines) + "\n"


def cited(catalog: Catalog, sources: list | tuple) -> str:
    """Citations as one line of text: the source's title, its version, the place."""
    parts = []
    for source in sources:
        known = catalog.sources.get(str(source.get("ref")), {})
        title = " ".join(str(known.get("title", source.get("ref"))).split())
        version = known.get("version")
        if version and known.get("kind") == "document":
            title += f", {version}"
        parts.append(f"{title}: {str(source.get('where', '')).strip()}")
    return "; ".join(parts)


def _say(catalog: Catalog, case: dict) -> str:
    """The line before a case of a default by design: when it holds."""
    when = case.get("when")
    if when is None:
        return "For any other study:"
    described = catalog.design_features.get(str(when))
    return f"For a study where {when} holds" + (
        f" ({described[0].lower() + described[1:].rstrip('.')}):" if described else ":")


def _status(house: House) -> str:
    from specfirst.compile import versions as known

    root = house.directory.parents[2]
    try:
        version = known.load(root).get(house.label)
    except OSError:
        version = None
    if version is None:
        return "not listed in standard/versions.yaml"
    if version.status == "frozen":
        return f"frozen on {version.date}"
    return "draft: it may still change, and no kit, task, run or score names it"


def _document(catalog: Catalog, house: House) -> str:
    """STANDARD.md of a house with defaults.yaml: anchored by entry, with its sources."""
    form = StandardForm(catalog)
    raw = house.raw
    preface = (
        f"This is the house standard {house.label}: {house.title}.",
        f"Status: {_status(house)}. Version {house.version} of the house standard "
        f"{house.id}, for the catalog {catalog.label} ({catalog.name} {catalog.version}). "
        "Any change of a default, a statement, a definition, a parent spec, a template or "
        "this document is a new version of the house (ADR-020; standard/versions.yaml).",
        "Scope: " + " ".join(str(raw.get("scope", "")).split()),
        "Order of precedence: " + " ".join(str(raw.get("precedence", "")).split()),
        "Each anchored statement below is a default. A decision taken from this document has "
        "the status `default` and the class `house_default`, and cites the statement by its "
        f"anchor, which is the ID of its entry: `doc:{DOCUMENT_ID}#trt.start.source`, or "
        f"`doc:{DOCUMENT_ID}#tfl.population/tfl-demographics` for the decision of one table. "
        "A default that depends on the design has one numbered statement per case, after a "
        "line that says when it holds, for example "
        f"`doc:{DOCUMENT_ID}#pop.safety.rule/1`. A fixed rule holds for every alternative of "
        "its entry and is not a decision; a document that contradicts one is cited against "
        f"it, for example `doc:{DOCUMENT_ID}#ae.teae.start/no_start_date`. A line that starts "
        "with \"Meaning:\" repeats what the catalog says the statement means, and a line that "
        "starts with \"Source:\" names the public sources of the statement's alternative, or, "
        "when it has none of its own, \"the sources of the entry\", which may support another "
        "alternative of the same question; neither is a statement of its own.",
        "The statements are in the standard form of the decision catalog: a parser reads "
        "each one back to its decision. Do not edit this file by hand. It is rendered from "
        "the catalog, from `house.yaml` and `defaults.yaml` of this house, and from "
        f"standard/versions.yaml; `specfirst house --house {house.label}` fails when it "
        "differs.",
    )
    sections = []
    terms = catalog.raw.get("terms") or {}
    if terms:
        sections.append(("Terms", (
            "The words below have the meaning the named entry gives them, in every statement.",
            "\n".join(f"- {term}: {' '.join(str(body.get('text', '')).split())} "
                      f"(`{body.get('entry')}`)" for term, body in terms.items()))))
    conventions = raw.get("conventions") or []
    if conventions:
        sections.append(("Conventions every table assumes", (
            "No decision states these rules; every table of this standard follows them.",
            "\n".join(f"- {' '.join(str(item).split())}" for item in conventions))))
    records = []
    for entry_id, unit in catalog.keys():
        if by_design(catalog, house, entry_id, unit):
            cases = choices(house, entry_id, unit, catalog.entry(entry_id).per_family)
            records.append({"id": entry_id, "unit": unit, "cases": [
                {"say": _say(catalog, case),
                 "value": {"rule": case["rule"], **(case.get("values") or {})}}
                for case in cases]})
            continue
        value = default_value(catalog, house, entry_id, unit)
        if value is not None:
            records.append({"id": entry_id, "unit": unit, "value": value})

    def after(record: dict, value: dict) -> list[str]:
        entry = catalog.entry(record["id"])
        alternative = entry.alternative(value["rule"])
        lines = [f"Source: {cited(catalog, alternative.sources)}" if alternative.sources
                 else f"Source: the sources of the entry, {cited(catalog, entry.sources)}"]
        for case in choices(house, record["id"], record["unit"], entry.per_family):
            if case.get("rule") == value["rule"] and case.get("sources"):
                lines.append(f"Source: the choice of this house, {cited(catalog, case['sources'])}")
                break
        return lines

    text = form.render_document(DOCUMENT_ID, f"House standard {house.label}", records,
                                preface, explain=True, anchors="entry", after=after,
                                fixed=True, sections=tuple(sections))
    lines = [text.rstrip("\n"), "", "## Decisions without a default", "",
             "This standard sets no default for the decisions below. The study documents "
             "state them, or a person is asked. They are never guessed.", ""]
    for entry_id, unit in without_default(catalog, house):
        entry = catalog.entry(entry_id)
        scope = f" ({unit})" if entry.per_family else ""
        lines.append(f"- `{entry_id}`{scope}: {entry.question}")
    conformance = raw.get("conformance") or []
    if conformance:
        lines += ["", "## Conformance rules of the parent specs", "",
                  "The parent specs fix these rules; no decision states them.", ""]
        lines += [f"- {' '.join(str(item).split())}" for item in conformance]
    changes = raw.get("change_log") or []
    if changes:
        lines += ["", "## Change log", ""]
        lines += [f"- {item.get('version')} ({item.get('date')}): "
                  f"{' '.join(str(item.get('text', '')).split())}" for item in changes]
    return "\n".join(lines) + "\n"


def default_decisions(catalog: Catalog, house: House,
                      features: dict[str, bool] | None = None) -> list[dict]:
    """The defaults as decision records that cite the standards document.

    With design features, a default by design is among them, citing its case.
    """
    form = StandardForm(catalog)
    doc, parsed, cases, _ = form.parse_full(standards_document(catalog, house))
    if features is not None:
        for key, stated in cases.items():
            found = choices(house, key[0], key[1], catalog.entry(key[0]).per_family)
            for case, line in zip(found, stated, strict=False):
                if "when" not in case or predicate.evaluate(predicate.parse(case["when"]),
                                                            features):
                    parsed.append(line)
                    break
        parsed = form.order(parsed)
    return [decision_record(item, doc, "default", "house_default") for item in parsed]
