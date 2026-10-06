"""Committed benign sample sequences. Detection fixtures only."""

from __future__ import annotations

from pathlib import Path

from synthguard.dna import mutate
from synthguard.fasta import write_fasta
from synthguard.reference import (
    ECOLI_GAPA_LIKE,
    HUMAN_HOUSEKEEP_ORF,
    PLASMID_BACKBONE,
    SPLIT_PARENT_GENE,
)
from synthguard.schemas import FastaRecord

TOO_SHORT = "ATGCGTACCGGTTAACCGAT"
NEAR_MISS = mutate(ECOLI_GAPA_LIKE, "synthguard-near-miss-v1", substitutions=21)
SPLIT_WINDOWS: tuple[tuple[int, int], ...] = (
    (0, 80),
    (30, 110),
    (60, 140),
    (90, 170),
    (118, len(SPLIT_PARENT_GENE)),
)


def split_fragments() -> list[FastaRecord]:
    records: list[FastaRecord] = []
    for index, (start, end) in enumerate(SPLIT_WINDOWS, start=1):
        records.append(
            FastaRecord(
                header=f"R001-frag{index} start={start} end={end}",
                sequence=SPLIT_PARENT_GENE[start:end],
            )
        )
    return records


def write_sample_tree(sample_dir: Path) -> None:
    write_fasta(
        sample_dir / "plasmid.fa",
        [FastaRecord(header="plasmid-backbone-fragment", sequence=PLASMID_BACKBONE)],
    )
    write_fasta(
        sample_dir / "housekeep.fa",
        [FastaRecord(header="human-housekeeping-orf-excerpt", sequence=HUMAN_HOUSEKEEP_ORF)],
    )
    write_fasta(
        sample_dir / "near-miss.fa",
        [FastaRecord(header="benign-homolog-near-miss", sequence=NEAR_MISS)],
    )
    write_fasta(
        sample_dir / "too-short.fa",
        [FastaRecord(header="below-min-length", sequence=TOO_SHORT)],
    )
    split_dir = sample_dir / "split-orders"
    for record in split_fragments():
        slug = record.header.split()[0]
        write_fasta(split_dir / f"{slug}.fa", [record])
    write_fasta(
        split_dir / "parent-benign-gene.fa",
        [FastaRecord(header="benign-parent-gene-R001", sequence=SPLIT_PARENT_GENE)],
    )
