"""Screen a benign query. Detection only; never proposes a modified sequence."""

from __future__ import annotations

from pathlib import Path

from synthguard import DEFAULT_IDENTITY_THRESHOLD, MIN_SCREENABLE_LENGTH
from synthguard.fasta import read_fasta
from synthguard.homology import best_hit
from synthguard.length import is_screenable
from synthguard.reference import PLASMID_BACKBONE
from synthguard.schemas import Annotation, FastaRecord, ScreenResult


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


def screen_sequence(
    sequence: str,
    query_id: str = "query",
    min_length: int = MIN_SCREENABLE_LENGTH,
    threshold: float = DEFAULT_IDENTITY_THRESHOLD,
    panel: list[FastaRecord] | None = None,
) -> ScreenResult:
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
    )


def screen_fasta_path(path: Path) -> list[ScreenResult]:
    return [screen_sequence(record.sequence, query_id=record.header) for record in read_fasta(path)]


def plasmid_backbone_sequence() -> str:
    return PLASMID_BACKBONE
