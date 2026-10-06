# Contributing

**DETECTION ONLY.** This repository screens DNA synthesis orders.

Never generate, complete, optimize, or suggest sequence modifications.
There is no generative component and patches that add one will be rejected.

- Commit benign public sequences only.
- Do not commit, construct, or reference hazardous sequences or sequences of concern.
- Do not bundle BLAST databases of regulated agents.
- Do not add a model that proposes edits to a query so that it would clear.
- Phase 0 uses a local k-mer / identity scorer against a tiny benign reference panel.
