"""The method registry: the entries of standard/methods/, and entries that must be refused."""

from __future__ import annotations

import shutil

import pytest
import yaml

from specfirst.machine import registry

EMPTY_OPTIONS = "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a"


def test_the_registry_of_this_repository_is_valid(root):
    known = registry.load(root)
    assert sorted(known.methods) == [
        "count.subjects", "display.pattern", "display.round.half_away_from_zero",
        "display.round.half_even", "percent.subjects",
        "summary.continuous", "test.anova.oneway", "test.chisq", "test.fisher.exact",
    ]
    for method in known.methods.values():
        assert (root / method.vectors).is_file()
        assert method.semantics and all(" " in statement for statement in method.semantics)
        # Rule R11: what is not a display rule has both engines.
        assert method.kind == "display" or set(method.implementations) == {"python", "r"}
    assert known.method("summary.continuous").options["quantile_definition"] == {
        "values": ["sas5", "r7"], "default": "sas5"}


def test_registry_json_is_what_the_yaml_entries_give(root):
    assert registry.json_problems(root) == []
    assert registry.json_bytes(registry.load(root)).endswith(b"\n")


def test_a_stale_or_missing_registry_json_is_found(root, tmp_path):
    shutil.copytree(root / "standard" / "methods", tmp_path / "standard" / "methods")
    shutil.copytree(root / "tests" / "methods", tmp_path / "tests" / "methods")
    assert registry.json_problems(tmp_path) == []
    entry = tmp_path / "standard/methods/test.chisq.yaml"
    entry.write_text(entry.read_text("ascii").replace("No continuity correction is applied",
                                                      "No correction is applied"), "ascii")
    assert registry.json_problems(tmp_path) == [
        "standard/methods/registry.json is stale; run `specfirst methods --write`"]
    lines: list[str] = []
    assert registry.run(tmp_path, out=lines.append) == 1
    assert registry.run(tmp_path, write=True, out=lines.append) == 0
    assert registry.json_problems(tmp_path) == []
    registry.json_path(tmp_path).unlink()
    assert "is missing" in registry.json_problems(tmp_path)[0]


def test_options_are_resolved_checked_and_hashed(root):
    known = registry.load(root)
    assert known.options("count.subjects") == {}
    assert known.options_hash("count.subjects") == EMPTY_OPTIONS  # the hash of {}
    assert known.options("summary.continuous", {"quantile_definition": "r7"}) == {
        "quantile_definition": "r7", "sd_denominator": "n_minus_1"}
    assert known.options_hash("summary.continuous") != known.options_hash(
        "summary.continuous", {"quantile_definition": "r7"})
    assert known.options_hash("summary.continuous") == known.options_hash(
        "summary.continuous", {"sd_denominator": "n_minus_1", "quantile_definition": "sas5"})
    with pytest.raises(registry.RegistryError, match="'sas4' is not one of"):
        known.options("summary.continuous", {"quantile_definition": "sas4"})
    with pytest.raises(registry.RegistryError, match="has no option trim"):
        known.options("summary.continuous", {"trim": 1})
    with pytest.raises(registry.RegistryError, match="no method 'count.records'"):
        known.options("count.records")


def test_operations_are_found_by_the_name_ars_gives_them(root):
    known = registry.load(root)
    assert known.by_ars_name("count of subjects") == [("count.subjects", "n")]
    assert known.by_ars_name(" Mean ") == [("summary.continuous", "mean")]
    assert known.by_ars_name("P-value") == [
        ("test.anova.oneway", "p_value"), ("test.chisq", "p_value"),
        ("test.fisher.exact", "p_value")]
    assert known.by_ars_name("Geometric mean") == []


def entry(root, **changes) -> dict:
    with open(root / "standard/methods/summary.continuous.yaml", encoding="ascii") as handle:
        data = yaml.safe_load(handle)
    for key, value in changes.items():
        if value is None:
            data.pop(key)
        else:
            data[key] = value
    return data


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"kind": "model"}, "'kind' must be one of"),
        ({"semantics": []}, "'semantics' must be a list of statements"),
        ({"semantics": None}, "'semantics' is missing"),
        ({"notes": "x"}, "unknown key 'notes'"),
        ({"operations": {}}, "'operations' must name at least one operation"),
        ({"operations": {"n": {"result": "count", "ars_names": []}}}, "'result' must be one of"),
        ({"operations": {"n": {"result": "integer"}}}, "needs exactly 'result' and 'ars_names'"),
        ({"options": {"quantile_definition": {"values": ["sas5"], "default": "r7"}}},
         "the default is not one of its values"),
        ({"options": {"trim": {"values": [0.1], "default": 0.1}}},
         "'values' must list text, whole numbers"),
        ({"implementations": ["python"]}, "needs both engines (rule R11)"),
        ({"implementations": ["python", "sas"]}, "'implementations' must list some of"),
        ({"xref": {"ars_example": []}}, "'xref' needs exactly"),
        ({"xref": {"ars_example": "Mth02", "siera": [], "acdc": None}},
         "xref.ars_example: must be a list"),
    ],
)
def test_an_entry_that_is_not_valid_is_refused(root, changes, message):
    with pytest.raises(registry.RegistryError) as error:
        registry.parse_method(entry(root, **changes), "entry")
    assert message in str(error.value)


def test_a_folder_of_entries_is_checked_as_a_whole(root, tmp_path):
    folder = tmp_path / "standard" / "methods"
    shutil.copytree(root / "standard" / "methods", folder)
    shutil.copytree(root / "tests" / "methods", tmp_path / "tests" / "methods")
    # The file name is not the ID; the vectors are missing; a name is taken twice.
    (folder / "count.subjects.yaml").rename(folder / "count.yaml")
    (tmp_path / "tests/methods/test_chisq.json").unlink()
    other = entry(root, id="summary.other", operations={
        "n": {"result": "integer", "ars_names": ["Count of subjects"]}})
    (folder / "summary.other.yaml").write_text(yaml.safe_dump(other), encoding="ascii")
    with pytest.raises(registry.RegistryError) as error:
        registry.load(tmp_path)
    text = str(error.value)
    assert "standard/methods/count.yaml: the entry is named 'count.subjects'" in text
    assert "test.chisq.yaml: no test vectors at 'tests/methods/test_chisq.json'" in text
    assert "ARS operation name 'Count of subjects' is taken by" in text
