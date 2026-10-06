"""Build R001 overlapping fragments and unrelated multi-order controls."""

from __future__ import annotations

import json
from pathlib import Path

from synthguard.dna import random_dna
from synthguard.reference import SPLIT_PARENT_GENE
from synthguard.samples import SPLIT_WINDOWS, split_fragments

HERE = Path(__file__).resolve().parent


def main() -> None:
    r001 = [
        {
            "order_id": f"R001-O{index}",
            "requester_id": "R001",
            "sequence": record.sequence,
            "header": record.header,
        }
        for index, record in enumerate(split_fragments(), start=1)
    ]
    controls = []
    for requester, gc in (("R002", 0.35), ("R003", 0.50), ("R004", 0.65)):
        for i in range(3):
            controls.append(
                {
                    "order_id": f"{requester}-O{i + 1}",
                    "requester_id": requester,
                    "sequence": random_dna(f"{requester}-{i}", 80, gc=gc),
                    "header": f"{requester} unrelated fragment {i + 1}",
                }
            )
    payload = {
        "parent_length": len(SPLIT_PARENT_GENE),
        "windows": [{"start": a, "end": b} for a, b in SPLIT_WINDOWS],
        "r001": r001,
        "controls": controls,
    }
    (HERE / "orders.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (HERE / "README.md").write_text(
        "# split_order_sim probe set\n\n"
        "Five overlapping fragments of one designed benign gene (R001) and "
        "unrelated benign fragments from R002–R004.\n",
        encoding="utf-8",
    )
    print("wrote split-order probe set")


if __name__ == "__main__":
    main()
