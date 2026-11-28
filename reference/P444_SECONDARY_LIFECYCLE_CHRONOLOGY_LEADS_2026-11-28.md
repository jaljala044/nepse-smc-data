# P4.44 secondary lifecycle chronology register

This is a research-only register derived from the P4.44 secondary lifecycle leads report. It separates last trading, maturity, announcement, delisting and merger-operation dates rather than collapsing them into one lifecycle boundary.

- 21 chronology claims are recorded.
- Most rows are secondary leads only; two SABSL/SDLBSL joint-business rows quote rendered text from a NEPSE-hosted issuer notice, but the original PDF bytes and SHA-256 are still missing.
- The SABSL/SDLBSL merger chronology conflict remains unresolved: a secondary merger table reports BS 2081-03-30, while the NEPSE-hosted issuer notice text reports BS 2082-03-30.
- No row is copied into the canonical lifecycle ledger, no stable security ID is inferred, and every row has `canonical_promotion_allowed=false`.

Use this register to prioritize primary-document retrieval and exact event-type reconciliation. It is not a source of verified effective dates.
