"""Fail-closed P4.44 lifecycle identity holds for canonical ingestion.

The current register has no verified historical stable IDs. Until that changes,
every listed symbol is held on every date; no effective-date boundary is inferred.
"""
import csv
from pathlib import Path

LEDGER = Path(__file__).resolve().parent.parent / "reference" / "P444_EFFECTIVE_DATED_LIFECYCLE_EVIDENCE_2026-11-27.csv"
EXPECTED_SYMBOLS = frozenset({
    "CMF1", "CMF2", "GBD80/81", "HBLD83", "JALPA", "KLBSL", "KLBSLP",
    "LEMF", "MKLB", "MMFDB", "NIBD2082", "NICAD8182", "NICAD8283",
    "NICD83/84", "NICGF", "NLBBL", "NMB50", "SABSL", "SAEF", "SAMAJ",
    "SBLD2082", "SBLD83", "SDLBSL", "SFCL", "SFCLP", "SRD80",
})
REQUIRED = {"symbol", "disposition", "effective_date_confidence"}


def load_lifecycle_holds(ledger=LEDGER):
    """Return symbol-wide wildcard holds; malformed or incomplete ledgers fail closed."""
    path = Path(ledger)
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames or []
        if len(fields) != len(set(fields)) or not REQUIRED.issubset(fields):
            raise ValueError("Invalid P4.44 lifecycle ledger schema")
        rows = list(reader)
    symbols = []
    for row in rows:
        symbol = (row.get("symbol") or "").strip().upper()
        disposition = (row.get("disposition") or "").strip()
        if not symbol or disposition != "HOLD_UNKNOWN":
            raise ValueError("P4.44 lifecycle ledger contains a non-held or blank identity")
        if (row.get("effective_date_confidence") or "").strip() == "verified":
            raise ValueError("Verified lifecycle evidence requires explicit gate review")
        symbols.append(symbol)
    if len(symbols) != len(set(symbols)) or frozenset(symbols) != EXPECTED_SYMBOLS:
        raise ValueError("P4.44 lifecycle ledger coverage mismatch")
    return {(symbol, "*"): "P444_LIFECYCLE_IDENTITY_HOLD" for symbol in symbols}
