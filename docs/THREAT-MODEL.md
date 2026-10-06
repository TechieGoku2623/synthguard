# Threat model — synthguard

**DETECTION ONLY.** This document states what the gateway can observe and
what it structurally cannot do. Features that would make it easier to
construct, complete, or optimize a hazardous sequence are refused.

## What this slice catches

| Signal | What fires | What the operator sees |
| --- | --- | --- |
| Minimum length | Query shorter than 50 nt | `NOT SCREENABLE`, non-zero exit, does **not** clear |
| Known benign backbone | Identity ≥ 0.95 vs committed plasmid fixture | `CLEAR`, annotation `known-benign-backbone` |
| Near-miss homolog | Identity in [0.70, 0.90) vs a benign relative | `CLEAR` with an explainable non-escalation |
| Split-order graph | ≥3 overlapping fragments from one requester covering ≥80% of a committed benign parent | Reviewer-queue flag. **No reconstructed sequence.** |
| Benign FPR | Identity ≥ T on the committed benign corpus | Public tradeoff table. TPR against sequences of concern is unmeasured |

The decision log and query hash are part of the product. A clear is an
auditable statement about this backend, not a license to synthesize.

## What this structurally cannot catch

- Sequences of concern. No SOC / select-agent / regulated-pathogen database
  is committed or bundled. SOC TPR is **unmeasured** and must stay that way
  in git.
- Remote homology, HMM profiles, or licensed BLAST/DIAMOND backends.
- Oligos below the 50 nt gate. They are refused, not guessed.
- Customer identity beyond the requester id on the ingest manifest.
- Intent. Overlap is a graph signal, not a motive.

## Refused features (would uplift hazardous construction)

The following are out of scope and will be rejected if proposed:

- Sequence completion, gap-filling, or "missing bases" suggestions.
- Silent or suggested substitutions that would raise or lower identity.
- A rewriter that makes a query clear the screen.
- Emission of a reconstructed parent gene from overlapping tiles.
- Codon optimization, host-adaptation, or "how to make this orderable".
- A bundled hazard catalog, accession list, or construct recipe.
- Any model whose output is a modified sequence.

Detection may flag. Detection may refuse to screen. Detection does not
help the order become a better construct.

## Residual risk

A determined actor can split orders below the overlap threshold, stay
under the identity threshold against this tiny benign panel, or submit
hazardous material that this backend has never seen. Those misses are
expected. They are why SOC TPR is labeled unmeasured and why this tool
is not a licensed select-agent screen.
