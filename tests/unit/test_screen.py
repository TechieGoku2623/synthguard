from __future__ import annotations

from pathlib import Path

from synthguard import DEFAULT_IDENTITY_THRESHOLD
from synthguard.homology import window_identity
from synthguard.reference import ECOLI_GAPA_LIKE, PLASMID_BACKBONE
from synthguard.samples import NEAR_MISS, TOO_SHORT, write_sample_tree
from synthguard.screen import plasmid_backbone_sequence, screen_fasta_path, screen_sequence
from synthguard.store import count_screens, write_screens


def test_plasmid_clears_as_known_backbone(tmp_path: Path) -> None:
    write_sample_tree(tmp_path)
    result = screen_fasta_path(tmp_path / "plasmid.fa")[0]
    assert result.status == "CLEAR"
    assert result.exit_code == 0
    assert result.annotation == "known-benign-backbone"
    assert result.max_identity == 1.0
    assert result.would_flag_at_threshold is False
    assert result.query_hash
    assert result.tier == "auto-clear"
    assert result.decision_log


def test_housekeep_clears_orf_annotation(tmp_path: Path) -> None:
    write_sample_tree(tmp_path)
    result = screen_fasta_path(tmp_path / "housekeep.fa")[0]
    assert result.status == "CLEAR"
    assert result.annotation == "orf-like"
    assert result.exit_code == 0


def test_near_miss_does_not_auto_flag() -> None:
    identity = window_identity(NEAR_MISS, ECOLI_GAPA_LIKE)
    result = screen_sequence(NEAR_MISS, query_id="near-miss")
    assert result.status == "CLEAR"
    assert result.annotation == "near-miss-benign-homolog"
    assert result.max_identity < DEFAULT_IDENTITY_THRESHOLD
    assert result.would_flag_at_threshold is False
    assert identity < DEFAULT_IDENTITY_THRESHOLD
    assert identity >= 0.70


def test_unannotated_clear() -> None:
    result = screen_sequence("A" * 80, query_id="polyA")
    assert result.status == "CLEAR"
    assert result.annotation == "unannotated"


def test_orf_helpers_and_backbone_constant() -> None:
    assert plasmid_backbone_sequence() == PLASMID_BACKBONE
    not_orf = screen_sequence("ATG" + "AAA" * 20, query_id="no-stop")
    assert not_orf.status == "CLEAR"


def test_too_short_is_not_screenable() -> None:
    result = screen_sequence(TOO_SHORT, query_id="too-short")
    assert result.status == "NOT_SCREENABLE"
    assert result.exit_code != 0
    assert result.annotation == "too-short"
    assert len(TOO_SHORT) == 20
    assert result.length < result.min_length


def test_store_round_trip(tmp_path: Path) -> None:
    rows = [
        screen_sequence(PLASMID_BACKBONE, "p"),
        screen_sequence(TOO_SHORT, "s"),
    ]
    path = tmp_path / "s.duckdb"
    write_screens(path, rows)
    assert count_screens(path) == 2
