"""Audit only four pinned third-party gzip floorsheets. No source writes."""
import csv, gzip, hashlib, io, json, re
from pathlib import Path
from collections import Counter

ROOT = Path("reference/p433_floorsheets")
DATES = ("2024-05-16", "2024-05-19", "2024-08-14", "2024-08-18")
def scan():
    manifest = json.loads((ROOT / "capture_report.json").read_text())
    results, all_ids = [], {}
    for day in DATES:
        path = ROOT / ("floorsheet_" + day + ".csv.gz")
        candidates = [r for r in manifest["records"] if r["date"] == day]
        if not candidates:
            raise ValueError("missing capture metadata: " + day)
        raw = path.read_bytes()
        decoded = gzip.decompress(raw)
        h = hashlib.sha256(raw).hexdigest()
        dh = hashlib.sha256(decoded).hexdigest()
        for m in candidates:
            if h != m["compressed_sha256"] or dh != m["uncompressed_sha256"]:
                raise ValueError("hash mismatch: " + day)
            if len(raw) != m["compressed_bytes"] or len(decoded) != m["uncompressed_bytes"]:
                raise ValueError("size mismatch: " + day)
        reader = csv.DictReader(io.StringIO(decoded.decode("utf-8-sig"), newline=""))
        required = {"contract_no", "calculation_date", "time", "stock_symbol", "id"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("missing columns: " + day)
        counts, ids, record_ids, exceptions = Counter(), set(), set(), []
        for line, row in enumerate(reader, 2):
            counts["rows"] += 1
            cid = row["contract_no"].strip()
            rid = row["id"].strip()
            reasons = []
            if row["calculation_date"].strip() != day:
                reasons.append("business_date_mismatch")
            if not re.fullmatch(r"[0-9]{16}", cid) or not cid.startswith(day.replace("-", "")):
                reasons.append("contract_date_or_format_mismatch")
            if cid in ids:
                reasons.append("duplicate_contract")
            if not rid or rid in record_ids:
                reasons.append("missing_or_duplicate_record_id")
            if cid in all_ids and all_ids[cid] != day:
                reasons.append("cross_date_contract_collision")
            ids.add(cid)
            record_ids.add(rid)
            all_ids.setdefault(cid, day)
            for reason in reasons:
                counts[reason] += 1
            if reasons:
                exceptions.append({"csv_line": line, "contract_no": cid, "reasons": reasons})
        if not counts["rows"]:
            raise ValueError("empty archive: " + day)
        results.append({"date": day, "path": str(path), "compressed_sha256": h,
                        "uncompressed_sha256": dh, "counts": dict(counts),
                        "distinct_contract_ids": len(ids), "exceptions": exceptions,
                        "admission_allowed": False})
    return {"scope": "four pinned third-party gzip archives only; no completeness or exchange certification",
            "files": results, "rows": sum(r["counts"]["rows"] for r in results),
            "exception_occurrences": sum(len(r["exceptions"]) for r in results),
            "admission_allowed": False}

if __name__ == "__main__":
    result = scan()
    out = Path("artifacts/p443-gzip-date-scan.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("x", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(json.dumps({k:v for k,v in result.items() if k != "files"}))
