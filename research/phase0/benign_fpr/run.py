"""FPR of identity≥T on 200+ committed benign sequences."""

from __future__ import annotations

import sys
from pathlib import Path

from synthguard import DEFAULT_IDENTITY_THRESHOLD
from synthguard.fasta import read_fasta
from synthguard.homology import best_hit
from synthguard.screen import screen_sequence
from synthguard.store import write_screens

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import md_table, write_json  # noqa: E402

HERE = Path(__file__).resolve().parent
PROBE = HERE / "probe_set" / "benign_queries.fa"
RESULTS = HERE / "results"
THRESHOLDS = (0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 0.99)
TARGET_FPR = 0.05


def main() -> None:
    records = read_fasta(PROBE)
    identities: list[float] = []
    screens = []
    for record in records:
        hit = best_hit(record.sequence)
        identities.append(hit.identity if hit else 0.0)
        screens.append(screen_sequence(record.sequence, query_id=record.header))

    rows = []
    fpr_by_t: dict[str, float] = {}
    for threshold in THRESHOLDS:
        flagged = sum(1 for ident in identities if ident >= threshold)
        fpr = flagged / len(identities)
        fpr_by_t[f"{threshold:.2f}"] = fpr
        rows.append([f"{threshold:.2f}", str(flagged), str(len(identities)), f"{fpr:.3f}"])
    eligible = [t for t in THRESHOLDS if fpr_by_t[f"{t:.2f}"] <= TARGET_FPR]
    chosen = eligible[0] if eligible else THRESHOLDS[-1]
    chosen_fpr = fpr_by_t[f"{chosen:.2f}"]

    default_fpr = fpr_by_t[f"{DEFAULT_IDENTITY_THRESHOLD:.2f}"]
    decision = (
        f"Lowest threshold with FPR ≤ {TARGET_FPR:.2f} is {chosen:.2f} "
        f"(FPR {chosen_fpr:.3f}). Phase 0 default remains "
        f"{DEFAULT_IDENTITY_THRESHOLD:.2f} (FPR {default_fpr:.3f}). "
        + (
            "Keep 0.90."
            if chosen == DEFAULT_IDENTITY_THRESHOLD
            else f"Recommend moving the default to {chosen:.2f} in Phase 1."
        )
    )
    RESULTS.mkdir(parents=True, exist_ok=True)
    write_screens(RESULTS / "screens.duckdb", screens)
    payload = {
        "n_queries": len(records),
        "thresholds": list(THRESHOLDS),
        "fpr_by_threshold": fpr_by_t,
        "target_fpr": TARGET_FPR,
        "recommended_threshold": chosen,
        "recommended_fpr": chosen_fpr,
        "default_threshold": DEFAULT_IDENTITY_THRESHOLD,
        "default_fpr": default_fpr,
        "mean_identity": sum(identities) / len(identities),
        "max_identity": max(identities),
        "decision": decision,
    }
    write_json(RESULTS / "results.json", payload)
    table = md_table(["threshold", "flagged", "n", "FPR"], rows)
    md = (
        "# benign_fpr results\n\n"
        f"n = {len(records)} designed benign sequences. "
        f"Mean identity vs benign panel: {payload['mean_identity']:.3f}. "
        f"Max identity: {payload['max_identity']:.3f}.\n\n"
        f"Decision: {decision}\n\n"
        f"{table}\n"
    )
    (RESULTS / "results.md").write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
