"""Compare daily trades against separately reviewed official session controls."""
import csv
import io
import json
import re
import hashlib
from datetime import date
from decimal import Decimal
from pathlib import Path

def reconcile(raw, day, control_path, evidence_path):
    if date.fromisoformat(day).isoformat() != day:
        raise ValueError("Invalid session date")
    control = json.loads(Path(control_path).read_text(encoding="utf-8"))
    if control["date"] != day or control["source_tier"] != "official_nepse" or control["review_status"] != "independently_verified":
        raise ValueError("Session control not eligible")
    if not re.fullmatch(r"https://(?:www\.)?nepalstock\.(?:com|com\.np)/[^\s]+", control["source_url"]):
        raise ValueError("Official source URL required")
    if hashlib.sha256(Path(evidence_path).read_bytes()).hexdigest() != control["evidence_sha256"]:
        raise ValueError("Session control evidence digest mismatch")
    if type(control["contracts"]) is not int or type(control["quantity"]) is not int:
        raise ValueError("Integer control totals required")
    expected = (control["contracts"], control["quantity"], Decimal(control["turnover_npr"]))
    if not all(x > 0 for x in expected) or not expected[2].is_finite():
        raise ValueError("Invalid official totals")
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    count = 0
    qty = Decimal(0)
    amount = Decimal(0)
    seen = set()
    for row in reader:
        identity = row["Contract_No"].strip()
        if identity in seen or not identity.isascii() or not identity.isdecimal() or not identity.startswith(day.replace("-", "")):
            raise ValueError("Duplicate or wrong-session contract")
        seen.add(identity)
        q, a = Decimal(row["Quantity"]), Decimal(row["Amount"])
        if not q.is_finite() or not a.is_finite() or q <= 0 or q != q.to_integral_value() or a <= 0:
            raise ValueError("Invalid trade totals")
        count += 1
        qty += q
        amount += a
    actual = (count, qty, amount)
    if actual != expected:
        raise ValueError(f"Session totals mismatch: actual={actual}, expected={expected}")
    return {"date":day,"contracts":count,"quantity":int(qty),"turnover_npr":str(amount)}
