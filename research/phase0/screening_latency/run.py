"""Latency of indexed vs naive homology on synthetic benign queries."""

from __future__ import annotations

import sys
import time
from pathlib import Path

from synthguard.dna import random_dna
from synthguard.homology import indexed_best_identity, naive_best_identity
from synthguard.reference import BENIGN_REFERENCE
from synthguard.schemas import FastaRecord

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import md_table, write_json  # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
LENGTHS = (50, 100, 200, 400)
VOLUMES = (1, 10, 25)
REPEATS = 2


def _queries(length: int, volume: int) -> list[str]:
    return [random_dna(f"lat-{length}-{i}", length, gc=0.5) for i in range(volume)]


def _time_backend(fn_name: str, queries: list[str]) -> float:
    panel = list(BENIGN_REFERENCE)
    # Enlarge the panel with designed benign decoys so the prefilter has work.
    decoys = [
        FastaRecord(header=f"decoy-{i}", sequence=random_dna(f"decoy-{i}", 200, gc=0.45))
        for i in range(20)
    ]
    panel.extend(decoys)
    scorer = naive_best_identity if fn_name == "naive" else indexed_best_identity
    start = time.perf_counter()
    for query in queries:
        scorer(query, panel)
    return time.perf_counter() - start


def main() -> None:
    rows_md: list[list[str]] = []
    cells: list[dict[str, object]] = []
    naive_total = 0.0
    indexed_total = 0.0
    for length in LENGTHS:
        for volume in VOLUMES:
            queries = _queries(length, volume)
            naive_times = [_time_backend("naive", queries) for _ in range(REPEATS)]
            indexed_times = [_time_backend("indexed", queries) for _ in range(REPEATS)]
            naive_s = sum(naive_times) / REPEATS
            indexed_s = sum(indexed_times) / REPEATS
            naive_total += naive_s
            indexed_total += indexed_s
            speedup = naive_s / indexed_s if indexed_s else 0.0
            cells.append(
                {
                    "length": length,
                    "volume": volume,
                    "naive_seconds": naive_s,
                    "indexed_seconds": indexed_s,
                    "speedup": speedup,
                }
            )
            rows_md.append(
                [
                    str(length),
                    str(volume),
                    f"{naive_s * 1000:.2f}",
                    f"{indexed_s * 1000:.2f}",
                    f"{speedup:.2f}",
                ]
            )

    faster = "indexed" if indexed_total < naive_total else "naive"
    decision = (
        f"Local {faster} backend is faster on this grid "
        f"(indexed {indexed_total:.4f}s vs naive {naive_total:.4f}s total). "
        "BLAST vs DIAMOND vs HMM remains deferred. BLAST RTT: unmeasured."
    )
    payload = {
        "lengths": list(LENGTHS),
        "volumes": list(VOLUMES),
        "repeats": REPEATS,
        "cells": cells,
        "naive_total_seconds": naive_total,
        "indexed_total_seconds": indexed_total,
        "faster_backend": faster,
        "decision": decision,
        "blast_rtt": "unmeasured",
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    write_json(RESULTS / "results.json", payload)
    table = md_table(
        ["query length", "order volume", "naive ms", "indexed ms", "speedup"],
        rows_md,
    )
    md = (
        "# screening_latency results\n\n"
        f"Repeats per cell: {REPEATS}. Panel = 3 committed benign refs + 20 decoys.\n\n"
        f"Decision: {decision}\n\n"
        f"{table}\n"
    )
    (RESULTS / "results.md").write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
