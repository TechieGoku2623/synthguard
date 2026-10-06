"""synthguard: open screening gateway for DNA synthesis orders.

DETECTION ONLY. This package never generates, completes, optimizes, or
suggests sequence modifications. There is no generative component.
"""

__version__ = "0.1.0"

SAFETY_DISCLAIMER = (
    "Detection only. This tool does not generate, complete, optimize, or "
    "suggest sequence modifications. Benign public sequences only."
)
MIN_SCREENABLE_LENGTH = 50
DEFAULT_IDENTITY_THRESHOLD = 0.90
KMER_SIZE = 8
