"""The thin yamaa runner: SDTM to ADaM (PLAN.md section 7.1, ADR-001).

yamaa is used as the pinned wheel. This runner does what a project run of
yamaa does, with one difference that makes the kit layout possible: every
input of every specification is handed over in memory. An input that another
specification of the project produces is that specification's output of this
run; any other input is the SDTM file of the same name in the kit's inputs.
The specifications themselves are not changed, and nothing is written next to
them (`save()` is never called).

`resolve_project` reads no study data: it composes each specification and
records where every element was written (file and line), which the graph
builder uses.
"""

from __future__ import annotations

import re
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pyarrow as pa

ENGINE = "yamaa"
_ALIAS = re.compile(r"^input\.([^.]+)\.path$")


class RunnerError(RuntimeError):
    """The specifications could not be resolved or run."""


@dataclass(frozen=True)
class InputSource:
    alias: str  # the name the specification uses
    layer: str  # "sdtm" or "adam"
    dataset: str  # SDTM domain or ADaM dataset, upper case
    file: str | None  # kit path of the SDTM file; None for an output of this run


@dataclass
class SpecPlan:
    name: str  # the specification's domain, for example ADSL
    entry: str  # kit path of the specification file
    record: dict  # yamaa's resolution, with every path made relative to the kit
    specification: dict  # the composed specification
    origins: dict  # JSON pointer -> where that element was written
    inputs: tuple[InputSource, ...]
    table: pa.Table | None = None  # the built dataset, after run_project

    @property
    def columns(self) -> list[str]:
        return list(self.specification["output"]["columns"])


def engine_version() -> str:
    import yamaa

    return yamaa.__version__


def _relocate(record: dict, kit_dir: Path) -> dict:
    """Every path of a resolution, relative to the kit, with forward slashes.

    A resolution names files by absolute path. Two builds in two folders must
    give the same bytes (P1), and the graph cites kit paths.
    """
    base = kit_dir.resolve()
    result = deepcopy(record)
    placed: dict[str, str] = {}

    def place(value: str) -> str:
        # A resolution names a handful of files many thousands of times, and
        # resolving a path asks the file system: do it once per file.
        if value not in placed:
            placed[value] = Path(value).resolve().relative_to(base).as_posix()
        return placed[value]

    result["entry"] = place(result["entry"])
    if result.get("project"):
        result["project"] = place(result["project"])
    for entry in result["entries"]:
        entry["entry"] = place(entry["entry"])
        entry["layers"] = [place(layer) for layer in entry["layers"]]
        for origin in entry["origins"].values():
            if origin.get("declaring_source") and origin.get("source_kind") != "schema_default":
                origin["declaring_source"] = place(origin["declaring_source"])
        for resource in entry["resources"]:
            for key in ("declaring_source", "base_source", "owning_entry"):
                if resource.get(key):
                    resource[key] = place(resource[key])
            resource["location"]["path"] = place(resource["location"]["path"])
    return result


def _open(kit_dir: Path, project: str):
    import yamaa

    path = kit_dir / project
    if not path.is_file():
        raise RunnerError(f"the project file {project} is not in the kit")
    return yamaa, yamaa.project(str(path))


def _plans(kit_dir: Path, project: str, sdtm: str) -> tuple[list[SpecPlan], dict[str, object]]:
    yamaa, handle = _open(kit_dir, project)
    try:
        names = handle.names
        specs = {name: handle.spec(name) for name in names}
        records = {name: _relocate(specs[name].resolve(), kit_dir) for name in names}
    except yamaa.Error as error:
        raise RunnerError(f"yamaa cannot resolve {project}: {error}") from error
    entries = {}
    produced: dict[str, str] = {}  # where a specification would save its output -> its name
    for name in names:
        record = records[name]
        entry = next((e for e in record["entries"] if e["entry"] == record["entry"]), None)
        if entry is None:
            raise RunnerError(f"{name}: the resolution has no entry for {record['entry']}")
        entries[name] = entry
        for resource in entry["resources"]:
            if resource["role"] == "output_data":
                produced[resource["location"]["path"]] = name
    plans = []
    for name in names:
        entry = entries[name]
        inputs = []
        for resource in entry["resources"]:
            if resource["role"] != "input_data":
                continue
            match = _ALIAS.match(resource.get("spec_path", ""))
            if not match:
                raise RunnerError(f"{name}: cannot name the input at {resource.get('spec_path')}")
            alias, location = match.group(1), resource["location"]["path"]
            if location in produced:
                inputs.append(InputSource(alias, "adam", produced[location], None))
                continue
            file = f"{sdtm}/{Path(location).name}"
            if not (kit_dir / file).is_file():
                raise RunnerError(
                    f"{name}: input {alias} ({location}) is neither the output of a "
                    f"specification of the project nor a file in {sdtm}"
                )
            inputs.append(InputSource(alias, "sdtm", Path(location).stem.upper(), file))
        plans.append(
            SpecPlan(
                name=name,
                entry=entry["entry"],
                record=records[name],
                specification=entry["specification"],
                origins=entry["origins"],
                inputs=tuple(sorted(inputs, key=lambda source: source.alias)),
            )
        )
    return plans, specs


def resolve_project(kit_dir: Path, project: str, sdtm: str) -> list[SpecPlan]:
    """Compose every specification of the project, in run order. Reads no study data."""
    return _plans(kit_dir, project, sdtm)[0]


def run_project(kit_dir: Path, project: str, sdtm: str) -> list[SpecPlan]:
    """Build every dataset of the project in memory, in run order."""
    import pyarrow.parquet as pq
    import yamaa

    plans, specs = _plans(kit_dir, project, sdtm)
    built: dict[str, pa.Table] = {}
    files: dict[str, pa.Table] = {}
    for plan in plans:
        inputs = {}
        for source in plan.inputs:
            if source.layer == "adam":
                if source.dataset not in built:
                    raise RunnerError(
                        f"{plan.name}: input {source.alias} is the output of {source.dataset}, "
                        "which the project lists later"
                    )
                inputs[source.alias] = built[source.dataset]
            else:
                if source.file not in files:
                    files[source.file] = pq.read_table(kit_dir / source.file)
                inputs[source.alias] = files[source.file]
        try:
            run = specs[plan.name].run(inputs=inputs)
            issues = run.issues.to_pylist()
            table = run.output
        except yamaa.Error as error:
            raise RunnerError(f"{plan.name}: {error}") from error
        if run.status != "succeeded" or issues or table is None:
            first = f"; first issue: {issues[0]}" if issues else ""
            raise RunnerError(
                f"{plan.name}: the run {run.status} with {len(issues)} issues{first}"
            )
        plan.table = table.to_arrow()
        built[plan.name] = plan.table
    return plans
