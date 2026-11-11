"""The manifest of pinned sources agrees with PLAN.md appendix A and SOURCES.md."""

from __future__ import annotations

import re

import pytest

from specfirst.sources import ManifestError, load_manifest, manifest_path, parse_manifest

ROW = re.compile(
    r"^\| [^|]+ \| ([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+) \| ([0-9a-f]{40})\b", re.MULTILINE
)


@pytest.fixture(scope="module")
def manifest(root):
    return load_manifest(manifest_path(root))


def appendix_a(root) -> str:
    plan = (root / "PLAN.md").read_text(encoding="ascii")
    return plan.split("## Appendix A. Pinned sources", 1)[1].split("## Appendix B", 1)[0]


def test_manifest_is_appendix_a(root, manifest):
    planned = set(ROW.findall(appendix_a(root)))
    assert len(planned) == 13
    assert {(s.repository, s.commit) for s in manifest.sources} == planned


def test_pinned_ars_example_is_the_one_in_the_plan(root, manifest):
    text = appendix_a(root)
    (pin,) = [f for f in manifest.files if f.source == "ars"]
    assert pin.path in text.replace("`", "")
    assert pin.sha256 in text


def test_sources_md_records_every_source(root, manifest):
    text = (root / "third_party" / "SOURCES.md").read_text(encoding="ascii")
    for src in manifest.sources:
        assert src.web_url in text, src.name
        assert src.commit in text, src.name
    for pin in manifest.files:
        assert pin.sha256 in text, pin.path


def entry(**changes):
    base = {
        "name": "demo",
        "title": "Demo",
        "repository": "example/demo",
        "commit": "a" * 40,
        "license": "MIT",
        "used_for": "tests",
    }
    return {**base, **changes}


def test_default_url_is_github():
    (src,) = parse_manifest({"sources": [entry()]}).sources
    assert src.url == "https://github.com/example/demo.git"
    assert src.web_url == "https://github.com/example/demo"


@pytest.mark.parametrize(
    "sources, files",
    [
        ([entry(commit="abc123")], []),  # a short commit is not a pin
        ([entry(commit="A" * 40)], []),
        ([entry(), entry()], []),  # the same name twice
        ([entry(name="Bad Name")], []),
        ([entry(repository="not-a-repository")], []),
        ([entry(license="")], []),
        ([entry()], [{"source": "other", "path": "a.txt", "sha256": "b" * 64}]),
        ([entry()], [{"source": "demo", "path": "../a.txt", "sha256": "b" * 64}]),
        ([entry()], [{"source": "demo", "path": "/etc/passwd", "sha256": "b" * 64}]),
        ([entry()], [{"source": "demo", "path": "a.txt", "sha256": "b" * 10}]),
    ],
)
def test_bad_manifests_are_rejected(sources, files):
    with pytest.raises(ManifestError):
        parse_manifest({"sources": sources, "files": files})


def test_manifest_must_be_a_mapping():
    with pytest.raises(ManifestError):
        parse_manifest([])
