"""The ASCII check (rule R10), with planted non-ASCII bytes."""

from __future__ import annotations

from specfirst import asciicheck


def run(path):
    lines: list[str] = []
    return asciicheck.check(path, lines.append), "\n".join(lines)


def test_find_non_ascii_reports_line_and_column():
    assert asciicheck.find_non_ascii(b"plain text\nmore\n") == []
    hits = asciicheck.find_non_ascii(b"ok\ncaf\xc3\xa9\n")
    assert hits == [(2, 4, 0xC3), (2, 5, 0xA9)]


def test_find_non_ascii_stops_at_the_limit():
    assert len(asciicheck.find_non_ascii(b"\xff" * 50, limit=3)) == 3


def test_clean_repository_passes(repo):
    code, text = run(repo)
    assert code == 0
    assert "1 files checked, 0 with non-ASCII bytes" in text


def test_tracked_file_with_a_non_ascii_byte_fails(repo, git):
    (repo / "notes.md").write_bytes(b"line one\nna\xc3\xafve\n")
    git(repo, "add", "notes.md")
    code, text = run(repo)
    assert code == 1
    assert "notes.md:2:3: non-ASCII byte 0xc3" in text


def test_new_file_that_is_not_ignored_is_checked(repo):
    (repo / "draft.txt").write_bytes(b"\xe2\x80\x94 an em dash\n")
    code, text = run(repo)
    assert code == 1 and "draft.txt:1:1" in text


def test_ignored_and_binary_files_are_skipped(repo, git):
    (repo / ".gitignore").write_bytes(b"cache/\n")
    git(repo, "add", ".gitignore")
    (repo / "cache").mkdir()
    (repo / "cache" / "study.txt").write_bytes(b"\xff\xfe")
    (repo / "figure.png").write_bytes(b"\x89PNG\r\n\x1a\n\xff")
    git(repo, "add", "figure.png")
    code, text = run(repo)
    assert code == 0, text


def test_this_repository_is_ascii(root):
    code, text = run(root)
    assert code == 0, text
