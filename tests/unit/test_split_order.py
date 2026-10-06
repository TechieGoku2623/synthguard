from __future__ import annotations

from synthguard.dna import random_dna
from synthguard.reference import SPLIT_PARENT_GENE
from synthguard.samples import split_fragments
from synthguard.schemas import OrderFragment
from synthguard.split_order import detect_orders, detect_requester, overlap_length


def test_r001_overlapping_fragments_detected() -> None:
    fragments = [
        OrderFragment(order_id=f"o{i}", requester_id="R001", sequence=record.sequence)
        for i, record in enumerate(split_fragments())
    ]
    result = detect_requester(fragments, parent_length=len(SPLIT_PARENT_GENE))
    assert result.detected is True
    assert result.n_edges >= 2
    assert result.reconstructed_fraction >= 0.80


def test_unrelated_customers_not_flagged() -> None:
    fragments = [
        OrderFragment(
            order_id=f"{req}-{i}",
            requester_id=req,
            sequence=random_dna(f"{req}-{i}", 80, gc=0.4 + n * 0.1),
        )
        for n, req in enumerate(("R002", "R003", "R004"))
        for i in range(3)
    ]
    detections = detect_orders(fragments, parent_length=len(SPLIT_PARENT_GENE))
    assert detections
    assert all(item.detected is False for item in detections)


def test_overlap_helpers() -> None:
    assert overlap_length("AAAAACCCCC", "CCCCCTTTTT", min_overlap=5) >= 5
    assert overlap_length("ACGT", "TGCA", min_overlap=3) == 0
    empty = detect_requester([], parent_length=10)
    assert empty.detected is False
