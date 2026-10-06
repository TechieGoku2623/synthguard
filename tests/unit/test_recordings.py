from __future__ import annotations

from pathlib import Path

from synthguard.recordings import record_all, write_cast


def test_write_cast_is_asciinema_v2(tmp_path: Path) -> None:
    path = tmp_path / "demo.cast"
    write_cast(path, "demo", ["hello", "world"])
    text = path.read_text(encoding="utf-8")
    first, *rest = text.strip().splitlines()
    assert '"version":2' in first or '"version": 2' in first
    assert "hello" in rest[0]


def test_record_all_writes_four_casts() -> None:
    written = record_all()
    names = {path.name for path in written}
    assert names == {
        "01-screen-and-clear.cast",
        "02-unscreenable.cast",
        "03-split-order-graph.cast",
        "04-tradeoff-curve.cast",
    }
    for path in written:
        assert path.is_file()
        header = path.read_text(encoding="utf-8").splitlines()[0]
        assert '"version":2' in header
