from __future__ import annotations

from pathlib import Path

from synthguard.config import get_settings
from synthguard.orders import (
    analyze_requester,
    ingest_directory,
    read_store,
    write_store,
)
from synthguard.schemas import OrderFragment


def test_ingest_skips_parent_and_flags_r001() -> None:
    settings = get_settings()
    fragments = ingest_directory(settings.split_order_dir)
    assert fragments
    assert all(not item.order_id.startswith("benign-parent") for item in fragments)
    assert {item.requester_id for item in fragments} == {"R001"}
    detection = analyze_requester(fragments, "R001")
    assert detection.detected is True
    missing = analyze_requester(fragments, "R999")
    assert missing.detected is False
    assert missing.n_fragments == 0


def test_store_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "orders.json"
    rows = [OrderFragment(order_id="o1", requester_id="R001", sequence="A" * 40, source_path="x")]
    write_store(path, rows)
    loaded = read_store(path)
    assert loaded[0].order_id == "o1"
    assert read_store(tmp_path / "missing.json") == []
