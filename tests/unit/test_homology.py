from __future__ import annotations

import pytest

from synthguard.dna import gc_fraction, random_dna
from synthguard.homology import (
    best_hit,
    indexed_best_identity,
    jaccard,
    kmers,
    naive_best_identity,
    window_identity,
)
from synthguard.reference import (
    BENIGN_REFERENCE,
    PLASMID_BACKBONE,
    reference_by_id,
    reference_records,
)
from synthguard.schemas import FastaRecord


def test_identity_and_jaccard_bounds() -> None:
    assert window_identity("ACGT", "ACGT") == 1.0
    assert window_identity("", "ACGT") == 0.0
    assert window_identity("AAAA", "ACGTAAAA") == 1.0
    assert jaccard(set(), {"A"}) == 0.0
    assert jaccard({"ACGT"}, {"ACGT"}) == 1.0
    assert not kmers("AC", k=8)


def test_reference_helpers() -> None:
    assert len(reference_records()) == 3
    assert "plasmid_backbone_puc_style" in reference_by_id()


def test_best_hit_finds_plasmid() -> None:
    hit = best_hit(PLASMID_BACKBONE)
    assert hit is not None
    assert hit.reference_id == "plasmid_backbone_puc_style"
    assert hit.identity == 1.0


def test_indexed_matches_naive_on_identical() -> None:
    panel = list(BENIGN_REFERENCE)
    assert naive_best_identity(PLASMID_BACKBONE, panel) == 1.0
    assert indexed_best_identity(PLASMID_BACKBONE, panel) == 1.0
    far = random_dna("far-from-panel", 80, gc=0.2)
    assert indexed_best_identity(far, panel) >= 0.0


def test_empty_best_hit() -> None:
    assert best_hit("", panel=[]) is None
    assert naive_best_identity("ACGT", []) == 0.0


def test_mutate_and_orf() -> None:
    from synthguard.dna import designed_orf, mutate

    orf = designed_orf("orf-unit", 10)
    assert orf.startswith("ATG")
    assert orf.endswith("TAA")
    assert mutate(orf, "none", 0) == orf
    changed = mutate(orf, "mut-unit", 4)
    assert changed != orf
    assert len(changed) == len(orf)


def test_gc_and_random_dna() -> None:
    seq = random_dna("gc-test", 200, gc=0.7)
    assert gc_fraction(seq) == pytest.approx(0.7, abs=0.15)
    with pytest.raises(ValueError):
        random_dna("bad", 10, gc=1.5)
    assert gc_fraction("") == 0.0


def test_score_unrelated_decoy() -> None:
    decoy = FastaRecord(header="d", sequence="A" * 80)
    hit = best_hit("C" * 80, panel=[decoy])
    assert hit is not None
    assert hit.identity == 0.0
