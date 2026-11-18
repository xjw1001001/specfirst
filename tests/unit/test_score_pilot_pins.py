"""The pilot report reads pinned files only (rule R3): a file of the fetch cache that
is missing, or is not the pinned one, stops it before anything is scored."""

from __future__ import annotations

import pytest

from specfirst import kit as kits
from specfirst.machine.canonical import sha256_bytes
from specfirst.score import pilot


def kit_with(sha256: str) -> kits.Kit:
    entry = kits.KitFile("gold/reference/adam/adsl.parquet", "p7", "study/adam/adsl.parquet",
                         sha256)
    return kits.Kit(id="toy", title="toy", tier="C", engines={}, sources={"p7": "0" * 40},
                    project="", sdtm="", reference="gold/reference/adam", claims=None,
                    documents=(), files=(entry,), trace_gaps={})


def test_a_pinned_file_is_found_by_its_hash(tmp_path, monkeypatch):
    monkeypatch.setenv("SPECFIRST_CACHE", str(tmp_path))
    kit = kit_with(sha256_bytes(b"the reference"))
    with pytest.raises(pilot.PilotError, match="not in the fetch cache"):
        pilot._pinned(tmp_path, kit, "gold/reference/adam/adsl.parquet")
    origin = tmp_path / "p7" / "study" / "adam" / "adsl.parquet"
    origin.parent.mkdir(parents=True)
    origin.write_bytes(b"the reference")
    assert pilot._pinned(tmp_path, kit, "gold/reference/adam/adsl.parquet") == origin
    origin.write_bytes(b"another file")
    with pytest.raises(pilot.PilotError, match="pinned SHA-256"):
        pilot._pinned(tmp_path, kit, "gold/reference/adam/adsl.parquet")
    with pytest.raises(pilot.PilotError, match="lists no file"):
        pilot._pinned(tmp_path, kit, "gold/reference/adam/adae.parquet")


def test_every_analysis_of_the_examples_summary_has_its_place_in_the_crosswalk():
    """Five analyses count what a row of the house table counts; three have no row."""
    assert len(pilot.ROWS) == 8
    assert sorted(code for code in pilot.ROWS.values() if code) == [
        "ANY", "DISCONTINUATION", "FATAL", "RELATED", "SERIOUS"]
    assert sum(1 for code in pilot.ROWS.values() if code is None) == 3
