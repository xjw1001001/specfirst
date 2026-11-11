"""The repository has the layout and the bootstrap files base-0 must create."""

from __future__ import annotations

import json

import pytest

DIRECTORIES = [
    "docs/state", "docs/decisions", "docs/reports",
    "standard/schemas", "standard/catalog", "standard/methods", "standard/houses/open-default@1",
    "src/specfirst/compile", "src/specfirst/machine", "src/specfirst/edit",
    "src/specfirst/gen", "src/specfirst/score", "src/specfirst/harness",
    "r/specfirstr", "skills", "kits", "viewer", "evidence",
    "tests/unit", "tests/methods", "tests/defects", "tests/golden",
    "third_party", "env",
]
FILES = [
    "PLAN.md", "CLAUDE.md", "README.md", "LICENSE",
    "docs/lessons.md", "third_party/SOURCES.md", "third_party/sources.yaml",
    "src/specfirst/cli.py", "env/requirements.lock", "env/r-packages.lock",
    ".claude/settings.json", ".github/workflows/ci.yml", "scripts/worktree.sh",
]
TRACKS = ["base", "real", "std", "gen", "read"]
EVIDENCE = [
    "ars_spike.py", "compare_adam.py", "csr_ae_spike.py", "csr_demog_spike.py",
    "csr_fisher_rxc_spike.py", "csr_hylaw_spike.py", "run_yamaa_project.py",
]


@pytest.mark.parametrize("path", DIRECTORIES)
def test_directory_of_section_12_exists(root, path):
    assert (root / path).is_dir()


@pytest.mark.parametrize("path", FILES)
def test_bootstrap_file_exists(root, path):
    assert (root / path).is_file()


@pytest.mark.parametrize("track", TRACKS)
def test_every_track_has_a_state_file(root, track):
    text = (root / "docs" / "state" / f"{track}.md").read_text(encoding="ascii")
    for heading in ("## Passed", "## Open", "## Next"):
        assert heading in text


@pytest.mark.parametrize("script", EVIDENCE)
def test_the_seven_evidence_scripts_are_kept(root, script):
    assert (root / "evidence" / script).is_file()


def test_claude_md_stays_under_60_lines(root):
    lines = (root / "CLAUDE.md").read_text(encoding="ascii").splitlines()
    assert len(lines) < 60


def test_license_is_mit(root):
    text = (root / "LICENSE").read_text(encoding="ascii")
    assert text.startswith("MIT License")


def test_deny_rules_cover_the_reference_folder(root):
    with open(root / ".claude" / "settings.json", encoding="ascii") as handle:
        deny = json.load(handle)["permissions"]["deny"]
    for tool in ("Read", "Edit"):
        assert any(rule.startswith(f"{tool}(") and "reference/**" in rule for rule in deny), tool


def test_text_files_have_lf_endings(root):
    from specfirst import asciicheck

    assert "* text=auto eol=lf" in (root / ".gitattributes").read_text(encoding="ascii")
    with_cr = [
        name
        for name in asciicheck.maintained_files(root)
        if (root / name).is_file()
        and (root / name).suffix.lower() not in asciicheck.BINARY_SUFFIXES
        and b"\r" in (root / name).read_bytes()
    ]
    assert with_cr == []


def test_cache_and_reference_are_ignored(root):
    ignored = (root / ".gitignore").read_text(encoding="ascii").splitlines()
    assert "/third_party/cache/" in ignored
    assert "/reference/" in ignored
