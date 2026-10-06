"""Screen a benign query. Detection only; never proposes a modified sequence."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Literal

from synthguard import DEFAULT_IDENTITY_THRESHOLD, MIN_SCREENABLE_LENGTH
from synthguard.fasta import read_fasta
from synthguard.homology import best_hit
from synthguard.length import is_screenable
from synthguard.reference import PLASMID_BACKBONE
from synthguard.schemas import Annotation, FastaRecord, HomologyHit, ScreenResult

Tier = Literal["auto-clear", "review", "not-screenable"]


def query_hash(sequence: str) -> str:
    return hashlib.sha256(sequence.encode("ascii", errors="ignore")).hexdigest()


def _looks_like_orf(sequence: str) -> bool:
    if len(sequence) < 6 or len(sequence) % 3 != 0:
        return False
    if not sequence.startswith("ATG"):
        return False
    return sequence[-3:] in {"TAA", "TAG", "TGA"}


def annotate(sequence: str, max_identity: float, reference_id: str | None) -> Annotation:
    if not is_screenable(sequence):
        return "too-short"
    if reference_id == "plasmid_backbone_puc_style" and max_identity >= 0.95:
        return "known-benign-backbone"
    if 0.70 <= max_identity < DEFAULT_IDENTITY_THRESHOLD:
        return "near-miss-benign-homolog"
    if _looks_like_orf(sequence):
        return "orf-like"
    return "unannotated"


def _rules(annotation: Annotation, hit: HomologyHit | None, threshold: float) -> list[str]:
    rules = ["R1 min-length gate (50 nt default)"]
    if annotation == "too-short":
        rules.append("R1 fired: measured length below minimum → NOT SCREENABLE")
        return rules
    rules.append("R2 local identity vs committed benign panel")
    if hit is not None:
        rules.append(f"R2 hit {hit.reference_id} identity={hit.identity:.3f}")
    if annotation == "known-benign-backbone":
        rules.append("R3 known-benign-backbone (identity ≥ 0.95) → auto-clear")
    elif annotation == "near-miss-benign-homolog":
        rules.append(f"R4 near-miss: identity below threshold {threshold:.2f} → do not escalate")
    elif annotation == "orf-like":
        rules.append("R5 orf-like annotation only; not a hazard hit")
    else:
        rules.append("R6 unannotated benign query; not a hazard hit")
    return rules


def _decision_log(
    sequence: str,
    min_length: int,
    threshold: float,
    hit: HomologyHit | None,
    annotation: Annotation,
    status: str,
) -> list[str]:
    log = [
        f"measured_length={len(sequence)} min_length={min_length}",
        f"query_hash={query_hash(sequence)}",
    ]
    if not is_screenable(sequence, min_length=min_length):
        log.append("gate=NOT_SCREENABLE (does not clear)")
        return log
    identity = hit.identity if hit else 0.0
    ref = hit.reference_id if hit else "none"
    log.append(f"best_hit={ref} identity={identity:.3f} threshold={threshold:.3f}")
    if annotation == "near-miss-benign-homolog":
        log.append(f"why_not_escalated: identity {identity:.3f} < threshold {threshold:.3f}")
    log.append(f"annotation={annotation} status={status}")
    log.append("detection_only: no sequence is generated or modified")
    return log


def _tier(status: str) -> Tier:
    if status == "NOT_SCREENABLE":
        return "not-screenable"
    if status == "REVIEW":
        return "review"
    return "auto-clear"


def screen_sequence(
    sequence: str,
    query_id: str = "query",
    min_length: int = MIN_SCREENABLE_LENGTH,
    threshold: float = DEFAULT_IDENTITY_THRESHOLD,
    panel: list[FastaRecord] | None = None,
) -> ScreenResult:
    digest = query_hash(sequence)
    if not is_screenable(sequence, min_length=min_length):
        return ScreenResult(
            query_id=query_id,
            status="NOT_SCREENABLE",
            exit_code=1,
            length=len(sequence),
            min_length=min_length,
            max_identity=0.0,
            identity_threshold=threshold,
            would_flag_at_threshold=False,
            annotation="too-short",
            notes=[f"Length {len(sequence)} is below minimum screenable length {min_length}."],
            query_hash=digest,
            tier="not-screenable",
            rules=_rules("too-short", None, threshold),
            decision_log=_decision_log(
                sequence, min_length, threshold, None, "too-short", "NOT_SCREENABLE"
            ),
        )

    hit = best_hit(sequence, panel=panel)
    max_identity = hit.identity if hit else 0.0
    annotation = annotate(sequence, max_identity, hit.reference_id if hit else None)
    # Benign-panel homology never auto-flags. would_flag_at_threshold is the
    # counterfactual used by the FPR harness (reference as a stand-in hit list).
    would_flag = max_identity >= threshold and annotation != "known-benign-backbone"
    notes = [
        "Detection only. No sequence modification is suggested.",
        f"Max identity vs benign reference: {max_identity:.3f} (threshold {threshold:.3f}).",
    ]
    if annotation == "known-benign-backbone":
        notes.append("Exact/near-exact match to the committed plasmid backbone fixture. CLEAR.")
    if annotation == "near-miss-benign-homolog":
        notes.append("High homology to a benign relative. Must not auto-flag.")
    return ScreenResult(
        query_id=query_id,
        status="CLEAR",
        exit_code=0,
        length=len(sequence),
        min_length=min_length,
        max_identity=max_identity,
        identity_threshold=threshold,
        would_flag_at_threshold=would_flag,
        annotation=annotation,
        best_hit=hit,
        notes=notes,
        query_hash=digest,
        tier=_tier("CLEAR"),
        rules=_rules(annotation, hit, threshold),
        decision_log=_decision_log(sequence, min_length, threshold, hit, annotation, "CLEAR"),
    )


def screen_fasta_path(path: Path) -> list[ScreenResult]:
    return [screen_sequence(record.sequence, query_id=record.header) for record in read_fasta(path)]


def plasmid_backbone_sequence() -> str:
    return PLASMID_BACKBONE
