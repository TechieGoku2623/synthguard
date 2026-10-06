"""Data contracts for screening results and split-order graphs."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

ScreenStatus = Literal["CLEAR", "NOT_SCREENABLE", "REVIEW"]
Annotation = Literal[
    "known-benign-backbone",
    "orf-like",
    "near-miss-benign-homolog",
    "unannotated",
    "too-short",
]


class FastaRecord(BaseModel):
    header: str
    sequence: str

    @property
    def length(self) -> int:
        return len(self.sequence)


class HomologyHit(BaseModel):
    reference_id: str
    identity: float
    jaccard: float


class ScreenResult(BaseModel):
    query_id: str
    status: ScreenStatus
    exit_code: int
    length: int
    min_length: int
    max_identity: float
    identity_threshold: float
    would_flag_at_threshold: bool
    annotation: Annotation
    best_hit: HomologyHit | None = None
    notes: list[str] = Field(default_factory=list)
    query_hash: str = ""
    tier: Literal["auto-clear", "review", "not-screenable"] = "auto-clear"
    rules: list[str] = Field(default_factory=list)
    decision_log: list[str] = Field(default_factory=list)


class OrderFragment(BaseModel):
    order_id: str
    requester_id: str
    sequence: str
    source_path: str = ""


class SplitDetection(BaseModel):
    requester_id: str
    detected: bool
    n_fragments: int
    n_edges: int
    reconstructed_fraction: float
    notes: str = ""


class SampleCase(BaseModel):
    sample_id: str
    filename: str
    path_exercised: str
    why_present: str
    expected_behavior: str
