"""Tiny committed BENIGN public-style reference panel.

Plasmid-backbone-style and E. coli housekeeping-style fragments only.
No hazardous sequences are present or referenced.
"""

from __future__ import annotations

from synthguard.dna import designed_orf, random_dna
from synthguard.schemas import FastaRecord

# Designed stand-ins for common lab classes (pUC-style ori, E. coli gapA/rpoD).
# Sequences are seed-derived originals, not GenBank dumps.
PLASMID_BACKBONE = random_dna("synthguard-benign-plasmid-backbone-v1", 180, gc=0.52)
ECOLI_GAPA_LIKE = designed_orf("synthguard-benign-ecoli-gapa-like-v1", 45)
ECOLI_RPOD_LIKE = designed_orf("synthguard-benign-ecoli-rpod-like-v1", 45)
HUMAN_HOUSEKEEP_ORF = designed_orf("synthguard-benign-human-housekeep-orf-v1", 48)
SPLIT_PARENT_GENE = designed_orf("synthguard-benign-split-parent-v1", 64)

BENIGN_REFERENCE: tuple[FastaRecord, ...] = (
    FastaRecord(header="plasmid_backbone_puc_style", sequence=PLASMID_BACKBONE),
    FastaRecord(header="ecoli_gapa_like_housekeeping", sequence=ECOLI_GAPA_LIKE),
    FastaRecord(header="ecoli_rpod_like_housekeeping", sequence=ECOLI_RPOD_LIKE),
)


def reference_records() -> tuple[FastaRecord, ...]:
    return BENIGN_REFERENCE


def reference_by_id() -> dict[str, str]:
    return {record.header: record.sequence for record in BENIGN_REFERENCE}
