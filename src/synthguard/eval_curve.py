"""FP/FN tradeoff on the committed benign corpus, plus a latency sample."""

from __future__ import annotations

import time
from pathlib import Path

from synthguard import DEFAULT_IDENTITY_THRESHOLD
from synthguard.config import get_settings
from synthguard.fasta import read_fasta
from synthguard.homology import best_hit
from synthguard.screen import screen_sequence

THRESHOLDS: tuple[float, ...] = (0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 0.99)


def benign_corpus_path() -> Path:
    return get_settings().research_dir / "benign_fpr" / "probe_set" / "benign_queries.fa"


def tradeoff_rows(
    fasta: Path | None = None,
) -> tuple[list[tuple[float, int, int, float]], float, int]:
    records = read_fasta(fasta or benign_corpus_path())
    start = time.perf_counter()
    identities: list[float] = []
    for record in records:
        hit = best_hit(record.sequence)
        identities.append(hit.identity if hit else 0.0)
        screen_sequence(record.sequence, query_id=record.header)
    elapsed = time.perf_counter() - start
    rows: list[tuple[float, int, int, float]] = []
    n = len(identities)
    for threshold in THRESHOLDS:
        flagged = sum(1 for ident in identities if ident >= threshold)
        fpr = flagged / n if n else 0.0
        rows.append((threshold, flagged, n, fpr))
    return rows, elapsed, n


def format_tradeoff(rows: list[tuple[float, int, int, float]], elapsed: float, n: int) -> str:
    lines = [
        "synthguard eval — FP/FN tradeoff (benign corpus)",
        "DETECTION ONLY. FN / TPR against sequences of concern is unmeasured.",
        f"n={n}  default_threshold={DEFAULT_IDENTITY_THRESHOLD:.2f}  "
        f"latency={elapsed:.3f}s for full corpus screen",
        "",
        "threshold  flagged  n    FPR    FN",
    ]
    for threshold, flagged, total, fpr in rows:
        lines.append(f"{threshold:.2f}       {flagged:<7} {total:<4} {fpr:.3f}  unmeasured")
    lines.append("")
    lines.append(
        "SOC TPR is structurally unmeasured: this repository does not commit hazardous sequences."
    )
    return "\n".join(lines)
