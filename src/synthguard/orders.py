"""Ingest and analyze multi-fragment orders. Detection only. No assembler."""

from __future__ import annotations

import json
from pathlib import Path

from synthguard.fasta import read_fasta
from synthguard.reference import SPLIT_PARENT_GENE
from synthguard.schemas import OrderFragment, SplitDetection
from synthguard.split_order import detect_requester


def default_store_path(repo_root: Path) -> Path:
    return repo_root / "data" / "local" / "orders.json"


def _requester_from_name(name: str) -> str:
    token = name.split()[0]
    if token.startswith("R") and "-" in token:
        return token.split("-", 1)[0]
    return token


def ingest_directory(path: Path) -> list[OrderFragment]:
    if not path.is_dir():
        raise FileNotFoundError(f"Order directory not found: {path}")
    fragments: list[OrderFragment] = []
    for fasta in sorted(path.glob("*.fa")):
        if fasta.name.startswith("parent-"):
            continue
        for record in read_fasta(fasta):
            requester = _requester_from_name(record.header)
            fragments.append(
                OrderFragment(
                    order_id=record.header.split()[0],
                    requester_id=requester,
                    sequence=record.sequence,
                    source_path=str(fasta),
                )
            )
    return fragments


def write_store(path: Path, fragments: list[OrderFragment]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = [item.model_dump(mode="json") for item in fragments]
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def read_store(path: Path) -> list[OrderFragment]:
    if not path.is_file():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [OrderFragment.model_validate(item) for item in raw]


def analyze_requester(
    fragments: list[OrderFragment],
    requester_id: str,
    parent_length: int | None = None,
) -> SplitDetection:
    group = [item for item in fragments if item.requester_id == requester_id]
    length = parent_length if parent_length is not None else len(SPLIT_PARENT_GENE)
    if not group:
        return SplitDetection(
            requester_id=requester_id,
            detected=False,
            n_fragments=0,
            n_edges=0,
            reconstructed_fraction=0.0,
            notes=f"No ingested fragments for requester {requester_id}.",
        )
    return detect_requester(group, parent_length=length)
