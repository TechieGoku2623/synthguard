"""Reassembly detection for R001 vs unrelated multi-order customers."""

from __future__ import annotations

import sys
from pathlib import Path

from synthguard.schemas import OrderFragment
from synthguard.split_order import detect_orders

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import md_table, read_json, write_json  # noqa: E402

HERE = Path(__file__).resolve().parent
PROBE = HERE / "probe_set" / "orders.json"
RESULTS = HERE / "results"


def _load(rows: list[dict[str, object]]) -> list[OrderFragment]:
    return [
        OrderFragment(
            order_id=str(row["order_id"]),
            requester_id=str(row["requester_id"]),
            sequence=str(row["sequence"]),
        )
        for row in rows
    ]


def main() -> None:
    raw = read_json(PROBE)
    parent_length = int(raw["parent_length"])
    fragments = _load(raw["r001"]) + _load(raw["controls"])
    detections = detect_orders(fragments, parent_length=parent_length)
    by_id = {item.requester_id: item for item in detections}
    r001 = by_id["R001"]
    controls = [item for item in detections if item.requester_id != "R001"]
    false_positives = sum(1 for item in controls if item.detected)
    decision = (
        "Split-order graph is in scope for Phase 2: R001 detected and "
        f"{false_positives} of {len(controls)} control requesters flagged."
        if r001.detected and false_positives == 0
        else (
            "Do not ship split-order detection as-is: "
            f"R001 detected={r001.detected}, control flags={false_positives}."
        )
    )
    payload = {
        "parent_length": parent_length,
        "n_requesters": len(detections),
        "r001_detected": r001.detected,
        "r001_edges": r001.n_edges,
        "r001_reconstructed_fraction": r001.reconstructed_fraction,
        "control_false_positives": false_positives,
        "n_controls": len(controls),
        "decision": decision,
        "detections": [item.model_dump(mode="json") for item in detections],
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    write_json(RESULTS / "results.json", payload)
    table = md_table(
        ["requester", "fragments", "edges", "reconstructed", "detected"],
        [
            [
                item.requester_id,
                str(item.n_fragments),
                str(item.n_edges),
                f"{item.reconstructed_fraction:.3f}",
                str(item.detected),
            ]
            for item in detections
        ],
    )
    md = (
        "# split_order_sim results\n\n"
        f"R001 detected: {r001.detected}. "
        f"Reconstructed fraction: {r001.reconstructed_fraction:.3f}. "
        f"Control false positives: {false_positives}/{len(controls)}.\n\n"
        f"Decision: {decision}\n\n"
        f"{table}\n"
    )
    (RESULTS / "results.md").write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
