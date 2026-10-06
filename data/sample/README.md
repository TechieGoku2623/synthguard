# Sample records

All records are **benign** designed fixtures. Nothing in this directory is a
hazardous sequence or a sequences-of-concern identifier.

| File | Why it is here |
| --- | --- |
| `plasmid.fa` | Common lab plasmid-backbone-style fragment. Clears. Annotates as known-benign-backbone. |
| `housekeep.fa` | Human housekeeping-style ORF excerpt (designed public-class stand-in). Clears. Exercises ORF annotation. |
| `near-miss.fa` | High homology to a benign E. coli-like relative in the reference. Must **not** auto-flag. Identity is below the default threshold. |
| `split-orders/` | Five overlapping fragments of one benign gene, requester R001, plus the parent fixture used only as a length oracle. |
| `too-short.fa` | 20 nt. Below the 50 nt minimum. NOT SCREENABLE, non-zero exit, does not clear. |

`make research` rewrites these files from committed seeds so they stay
aligned with `src/synthguard/reference.py`.
