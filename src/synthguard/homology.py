"""Identity and k-mer homology against the committed benign reference only."""

from __future__ import annotations

from collections.abc import Iterable

from synthguard import KMER_SIZE
from synthguard.reference import BENIGN_REFERENCE
from synthguard.schemas import FastaRecord, HomologyHit


def kmers(sequence: str, k: int = KMER_SIZE) -> set[str]:
    if len(sequence) < k:
        return set()
    return {sequence[i : i + k] for i in range(len(sequence) - k + 1)}


def jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    union = left | right
    return len(left & right) / len(union)


def window_identity(query: str, reference: str) -> float:
    """Best same-length window identity. No affine alignment."""

    if not query or not reference:
        return 0.0
    if len(query) == len(reference):
        return sum(a == b for a, b in zip(query, reference, strict=True)) / len(query)
    longer, shorter = (query, reference) if len(query) >= len(reference) else (reference, query)
    best = 0.0
    width = len(shorter)
    limit = len(longer) - width + 1
    for start in range(limit):
        window = longer[start : start + width]
        ident = sum(a == b for a, b in zip(window, shorter, strict=True)) / width
        if ident > best:
            best = ident
    return best


def score_pair(query: str, reference: str, k: int = KMER_SIZE) -> tuple[float, float]:
    return window_identity(query, reference), jaccard(kmers(query, k), kmers(reference, k))


def best_hit(
    query: str,
    panel: Iterable[FastaRecord] | None = None,
    k: int = KMER_SIZE,
) -> HomologyHit | None:
    records = tuple(panel) if panel is not None else BENIGN_REFERENCE
    if not records or not query:
        return None
    ranked: list[HomologyHit] = []
    for record in records:
        identity, jac = score_pair(query, record.sequence, k=k)
        ranked.append(HomologyHit(reference_id=record.header, identity=identity, jaccard=jac))
    ranked.sort(key=lambda hit: (hit.identity, hit.jaccard), reverse=True)
    return ranked[0]


def naive_best_identity(query: str, panel: Iterable[FastaRecord]) -> float:
    hit = best_hit(query, panel=panel)
    return hit.identity if hit else 0.0


def indexed_candidates(
    query: str,
    panel: Iterable[FastaRecord],
    k: int = KMER_SIZE,
    min_shared: int = 1,
) -> list[FastaRecord]:
    """k-mer prefilter, then the caller still runs identity on survivors."""

    query_kmers = kmers(query, k)
    hits: list[FastaRecord] = []
    for record in panel:
        shared = len(query_kmers & kmers(record.sequence, k))
        if shared >= min_shared:
            hits.append(record)
    return hits


def indexed_best_identity(
    query: str,
    panel: Iterable[FastaRecord],
    k: int = KMER_SIZE,
) -> float:
    candidates = indexed_candidates(query, panel, k=k)
    if not candidates:
        return 0.0
    return naive_best_identity(query, candidates)
