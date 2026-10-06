"""Minimum screenable length. Below this, the order is NOT SCREENABLE."""

from __future__ import annotations

from synthguard import MIN_SCREENABLE_LENGTH


def is_screenable(sequence: str, min_length: int = MIN_SCREENABLE_LENGTH) -> bool:
    return len(sequence) >= min_length
