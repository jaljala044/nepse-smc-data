# NEPSE Common-Equity OHLCV — Derived Dataset v3

Status: official-EOD-backed; 11 additional recent Open corrections applied
Scope: 281 common-equity securities; 246238 rows

## P4.30 corrections

- 11 official NEPSE EOD Open corrections applied to the v2 derived series.
- Each correction has exact symbol/date, official security ID, payload SHA-256, source URL and retrieval timestamp.
- Only Open changed; High, Low, Close and Volume were independently checked against the official row.
- v2 and raw OHLCV sources remain immutable.
- Historical anomalies without primary evidence remain flagged; no other rows were repaired.
