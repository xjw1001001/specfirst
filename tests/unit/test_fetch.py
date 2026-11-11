"""`specfirst fetch` on a local repository that plays the remote source.

The planted defects: a pin that moved, a commit that does not exist, a
changed or added file in the cache, a file with another SHA-256.
"""

from __future__ import annotations

import hashlib

import pytest

from specfirst import fetch
from specfirst.sources import parse_manifest


@pytest.fixture
def origin(tmp_path, git):
    """A source with two commits; returns (path, first commit, second commit)."""
    path = tmp_path / "origin"
    path.mkdir()
    git(path, "init", "--quiet", "-b", "main")
    git(path, "config", "uploadpack.allowAnySHA1InWant", "true")
    commits = []
    for text in (b"first\n", b"second\n"):
        (path / "data.txt").write_bytes(text)
        git(path, "add", "data.txt")
        git(path, "commit", "--quiet", "-m", text.decode().strip())
        commits.append(git(path, "rev-parse", "HEAD"))
    return path, commits[0], commits[1]


def manifest(origin_path, commit, files=()):
    return parse_manifest(
        {
            "sources": [
                {
                    "name": "demo",
                    "title": "Demo",
                    "repository": "example/demo",
                    "commit": commit,
                    "license": "MIT",
                    "used_for": "tests",
                    "url": str(origin_path),
                }
            ],
            "files": list(files),
        }
    )


def run(man, cache, **kwargs):
    lines: list[str] = []
    ok = fetch.fetch_all(man, cache, out=lines.append, **kwargs)
    return ok, "\n".join(lines)


def test_fetches_exactly_the_pinned_commit(tmp_path, origin):
    path, first, _ = origin
    cache = tmp_path / "cache"
    ok, text = run(manifest(path, first), cache)
    assert ok, text
    assert "fetched" in text
    assert fetch.head_commit(cache / "demo") == first
    assert (cache / "demo" / "data.txt").read_bytes() == b"first\n"


def test_second_run_downloads_nothing(tmp_path, origin):
    path, first, _ = origin
    cache = tmp_path / "cache"
    assert run(manifest(path, first), cache)[0]
    ok, text = run(manifest(path, first), cache, verify_only=True)
    assert ok and "present" in text


def test_verify_fails_on_an_empty_cache(tmp_path, origin):
    path, first, _ = origin
    ok, text = run(manifest(path, first), tmp_path / "cache", verify_only=True)
    assert not ok and "missing" in text and "FAILED" in text


def test_moved_pin_is_drift_until_fetched_again(tmp_path, origin):
    path, first, second = origin
    cache = tmp_path / "cache"
    assert run(manifest(path, first), cache)[0]
    ok, text = run(manifest(path, second), cache, verify_only=True)
    assert not ok and f"pinned is {second}" in text
    ok, text = run(manifest(path, second), cache)
    assert ok and "updated" in text
    assert (cache / "demo" / "data.txt").read_bytes() == b"second\n"


def test_unknown_commit_fails(tmp_path, origin):
    path, _, _ = origin
    ok, text = run(manifest(path, "0" * 40), tmp_path / "cache")
    assert not ok and "FAIL" in text


def test_changed_file_in_the_cache_fails(tmp_path, origin):
    path, first, _ = origin
    cache = tmp_path / "cache"
    assert run(manifest(path, first), cache)[0]
    (cache / "demo" / "data.txt").write_bytes(b"edited\n")
    ok, text = run(manifest(path, first), cache, verify_only=True)
    assert not ok and "not clean" in text


def test_added_file_in_the_cache_fails(tmp_path, origin):
    path, first, _ = origin
    cache = tmp_path / "cache"
    assert run(manifest(path, first), cache)[0]
    (cache / "demo" / "adsl-yamaa.parquet").write_bytes(b"left behind by a run")
    ok, text = run(manifest(path, first), cache, verify_only=True)
    assert not ok and "adsl-yamaa.parquet" in text


def test_pinned_file_hash(tmp_path, origin):
    path, first, _ = origin
    cache = tmp_path / "cache"
    good = hashlib.sha256(b"first\n").hexdigest()
    pin = {"source": "demo", "path": "data.txt", "sha256": good}
    ok, text = run(manifest(path, first, [pin]), cache)
    assert ok and good in text

    wrong = dict(pin, sha256=hashlib.sha256(b"other").hexdigest())
    ok, text = run(manifest(path, first, [wrong]), cache, verify_only=True)
    assert not ok and "pinned is" in text

    absent = dict(pin, path="no-such-file.txt")
    ok, text = run(manifest(path, first, [absent]), cache, verify_only=True)
    assert not ok and "file not found" in text


def test_unknown_source_name_fails(tmp_path, origin):
    path, first, _ = origin
    ok, text = run(manifest(path, first), tmp_path / "cache", only=["nope"])
    assert not ok and "unknown source" in text


def test_folder_that_is_not_a_clone_is_left_alone(tmp_path, origin):
    path, first, _ = origin
    cache = tmp_path / "cache"
    (cache / "demo").mkdir(parents=True)
    (cache / "demo" / "keep.txt").write_bytes(b"mine")
    ok, text = run(manifest(path, first), cache)
    assert not ok and "not a git clone" in text
    assert (cache / "demo" / "keep.txt").read_bytes() == b"mine"
