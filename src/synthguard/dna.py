"""Deterministic DNA helpers for committed benign fixtures.

These functions generate designed stand-in sequences from a seed. They are
not a sequence optimizer and must not be used to propose modifications to a
customer order.
"""

from __future__ import annotations

import hashlib

ALPHABET = "ACGT"
CODONS = tuple(
    f"{a}{b}{c}"
    for a in ALPHABET
    for b in ALPHABET
    for c in ALPHABET
    if f"{a}{b}{c}" not in {"TAA", "TAG", "TGA"}
)


def seeded_bytes(seed: str, n: int) -> bytes:
    out = bytearray()
    block = seed.encode("utf-8")
    while len(out) < n:
        block = hashlib.sha256(block).digest()
        out.extend(block)
    return bytes(out[:n])


def random_dna(seed: str, length: int, gc: float = 0.5) -> str:
    """Designed random DNA with an approximate GC fraction. Not an optimizer."""

    if not 0.0 <= gc <= 1.0:
        raise ValueError("gc must be in [0, 1]")
    raw = seeded_bytes(seed, length)
    gc_cutoff = int(gc * 256)
    bases: list[str] = []
    for i, byte in enumerate(raw):
        if byte < gc_cutoff:
            bases.append("G" if i % 2 == 0 else "C")
        else:
            bases.append("A" if i % 2 == 0 else "T")
    return "".join(bases)


def designed_orf(seed: str, amino_acids: int) -> str:
    """ATG + sense codons + TAA. Designed fixture, not a gene suggestion."""

    raw = seeded_bytes(seed, amino_acids)
    core = "".join(CODONS[byte % len(CODONS)] for byte in raw)
    return "ATG" + core + "TAA"


def mutate(sequence: str, seed: str, substitutions: int) -> str:
    """Apply a fixed number of substitutions. Used only to build fixtures."""

    if substitutions <= 0:
        return sequence
    target = min(substitutions, len(sequence))
    raw = seeded_bytes(seed, max(target * 8, 32))
    chars = list(sequence)
    used: set[int] = set()
    idx = 0
    changed = 0
    while changed < target:
        if idx + 1 >= len(raw):
            raw = seeded_bytes(seed + f":{idx}", len(raw) + 64)
            idx = 0
        pos = raw[idx] % len(chars)
        idx += 1
        if pos in used:
            continue
        used.add(pos)
        current = chars[pos]
        alt = ALPHABET[(ALPHABET.index(current) + 1 + raw[idx] % 3) % 4]
        idx += 1
        chars[pos] = alt
        changed += 1
    return "".join(chars)


def gc_fraction(sequence: str) -> float:
    if not sequence:
        return 0.0
    gc = sum(1 for base in sequence if base in {"G", "C"})
    return gc / len(sequence)
