# Data

Phase 0 does not download BLAST databases or sequences of concern. The committed objects are benign by construction:

- `data/sample/plasmid.fa` — designed plasmid-backbone-style fragment
- `data/sample/housekeep.fa` — designed human housekeeping-style ORF
- `data/sample/near-miss.fa` — designed homolog of a benign E. coli-like ORF
- `data/sample/too-short.fa` — 20 nt, below the 50 nt gate
- `data/sample/split-orders/` — five overlapping fragments of one benign gene
- `research/phase0/benign_fpr/probe_set/benign_queries.fa` — 220 designed benign queries
- `research/phase0/split_order_sim/probe_set/orders.json` — R001 plus 3 control requesters

No hazardous sequences. No customer-identifiable orders. License notes are in `docs/phase-0/research-memo.md` §3.
