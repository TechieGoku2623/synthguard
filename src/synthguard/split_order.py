"""Overlap-graph reassembly detection for multi-fragment orders.

Detection only. This module does not invent missing bases.
"""

from __future__ import annotations

from collections import defaultdict

from synthguard.schemas import OrderFragment, SplitDetection


def overlap_length(left: str, right: str, min_overlap: int = 20) -> int:
    best = 0
    max_n = min(len(left), len(right))
    for size in range(max_n, min_overlap - 1, -1):
        if left[-size:] == right[:size] or right[-size:] == left[:size]:
            return size
        if left[:size] == right[:size] or left[-size:] == right[-size:]:
            best = max(best, size)
    if left in right or right in left:
        return min(len(left), len(right))
    return best


def build_edges(
    fragments: list[OrderFragment], min_overlap: int = 20
) -> list[tuple[int, int, int]]:
    edges: list[tuple[int, int, int]] = []
    for i, a in enumerate(fragments):
        for j, b in enumerate(fragments):
            if j <= i:
                continue
            shared = overlap_length(a.sequence, b.sequence, min_overlap=min_overlap)
            if shared >= min_overlap:
                edges.append((i, j, shared))
    return edges


def _greedy_chain_length(fragments: list[OrderFragment], min_overlap: int) -> int:
    """Greedy end-join. Counts each overlap once; does not emit the parent sequence."""

    unused = set(range(len(fragments)))
    start = max(unused, key=lambda i: len(fragments[i].sequence))
    unused.remove(start)
    used = [start]
    total = len(fragments[start].sequence)
    while unused:
        best_idx = -1
        best_overlap = 0
        for candidate in unused:
            for member in used:
                shared = overlap_length(
                    fragments[member].sequence,
                    fragments[candidate].sequence,
                    min_overlap=min_overlap,
                )
                if shared > best_overlap:
                    best_overlap = shared
                    best_idx = candidate
        if best_idx < 0 or best_overlap < min_overlap:
            break
        unused.remove(best_idx)
        used.append(best_idx)
        total += len(fragments[best_idx].sequence) - best_overlap
    return total


def reconstructed_span(
    fragments: list[OrderFragment],
    edges: list[tuple[int, int, int]],
    min_overlap: int = 20,
) -> int:
    if not fragments:
        return 0
    if not edges:
        return max(len(item.sequence) for item in fragments)
    return _greedy_chain_length(fragments, min_overlap=min_overlap)


def detect_requester(
    fragments: list[OrderFragment],
    parent_length: int,
    min_overlap: int = 20,
    reconstruct_threshold: float = 0.80,
) -> SplitDetection:
    edges = build_edges(fragments, min_overlap=min_overlap)
    span = reconstructed_span(fragments, edges, min_overlap=min_overlap)
    fraction = span / parent_length if parent_length else 0.0
    requester = fragments[0].requester_id if fragments else "unknown"
    detected = len(fragments) >= 3 and fraction >= reconstruct_threshold and len(edges) >= 2
    return SplitDetection(
        requester_id=requester,
        detected=detected,
        n_fragments=len(fragments),
        n_edges=len(edges),
        reconstructed_fraction=fraction,
        notes=(
            "Overlapping fragments reconstruct a committed benign parent."
            if detected
            else "No reassembly signal at the configured overlap threshold."
        ),
    )


def detect_orders(
    fragments: list[OrderFragment],
    parent_length: int,
    min_overlap: int = 20,
) -> list[SplitDetection]:
    by_requester: dict[str, list[OrderFragment]] = defaultdict(list)
    for fragment in fragments:
        by_requester[fragment.requester_id].append(fragment)
    return [
        detect_requester(group, parent_length, min_overlap=min_overlap)
        for group in by_requester.values()
    ]
