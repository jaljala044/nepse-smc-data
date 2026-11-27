"""Pinned equity exception holds; separate from the repeat-candle overlay."""
import csv
import hashlib
import io
from pathlib import Path
from .historical_quarantine import key

REFERENCE = Path(__file__).resolve().parent.parent / "reference"
REGISTERS = {
  "AHPC": [
    588,
    "0d662db6310d65116dc0e84ad5ed424ff1f7d26b"
  ],
  "API": [
    122,
    "b743f07527baa4da4b32f14e7fbe96481799dc9c"
  ],
  "CHL": [
    45,
    "8c7cc365feb30e168fc5c4d97ac6f9a8b62d5b9d"
  ],
  "HIDCL": [
    30,
    "94783d943aec38bb88b6aa7d5936336d1510fac9"
  ],
  "MERO": [
    102,
    "5e6361b17b9fec14b0af099a9e84f90d84ea1d97"
  ],
  "SKBBL": [
    379,
    "c899afa2499a7e1242d7a2fb0d3a6e3a33c8aafa"
  ],
  "SPDL": [
    53,
    "dbd7aca95de9f7ffac1fbf06b47cf3b33310c0be"
  ],
  "remaining_six_equity": [
    10,
    "dc748a9c06e8e3c1f457d7d6ca2198ee351b80bd"
  ]
}


def load_equity_holds(reference=REFERENCE):
    holds = {}
    for name, (expected, digest) in REGISTERS.items():
        raw = (reference / f"{name}_ohlc_exception_register_2026-11-26.csv").read_bytes()
        if hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() != digest:
            raise ValueError("Equity exception register integrity mismatch: " + name)
        reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
        count = 0
        for row in reader:
            k = key(row["symbol"], row["date"])
            if k in holds or not row["flag"] or not row["source_blob_sha"]:
                raise ValueError("Duplicate or incomplete equity exception")
            holds[k] = "INVALID_OHLCV_EXCEPTION_HOLD"
            count += 1
        if count != expected:
            raise ValueError("Equity exception coverage mismatch: " + name)
    if len(holds) != 1329:
        raise ValueError("Incomplete equity exception coverage")
    return holds
