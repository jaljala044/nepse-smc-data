"""Consolidate session recovery candidates without granting official approval."""
import csv
import hashlib
import json
import subprocess
from collections import Counter
from decimal import Decimal
from pathlib import Path
from p443_recover_session_counts import rows, summarize, SOURCE

def unique(records):
    result = {r["date"]: r for r in records}
    if len(result) != len(records):
        raise ValueError("Duplicate session date")
    return result

def main(source, output):
    market = unique(rows(Path("scanner_inputs/market_summary_daily.csv")))
    recovered = unique(rows(output / "session_recovery.csv"))
    crosswalk = unique(rows(Path("reference/P443_SESSION_CONTROL_ARCHIVE_CROSSWALK_2026-11-27.csv")))
    disposition = json.loads(Path("reference/P443_SESSION_CONTROL_MARCH01_DISPOSITION.json").read_text())
    if len(market) != 195 or set(market) != set(crosswalk) or len(recovered) != 149:
        raise ValueError("Unexpected recovery scope")
    result = []
    for day, base in sorted(market.items()):
        ref = crosswalk[day]
        source_date = day
        source_blob = ""
        if base["transactions"]:
            if day in recovered or ref["existing_transactions"] != base["transactions"]:
                raise ValueError("Baseline overlap or mismatch")
            count = int(base["transactions"])
            status = "EXISTING_BASELINE_CANDIDATE"
        elif ref["comparison_status"] == "CANDIDATE_COUNT_RECOVERED":
            if day in recovered:
                raise ValueError("Duplicate recovery route")
            count = int(ref["archive_transactions"])
            status = "ARCHIVE_CONTRACT_PARITY_CANDIDATE"
        else:
            row = recovered[day]
            if row["publication_allowed"] != "false":
                raise ValueError("Unexpected promotion")
            if row["status"] == "CANDIDATE_TOTALS_MATCH":
                count = int(row["transactions"])
                source_blob = row["source_blob"]
                status = "SECONDARY_TOTALS_MATCH_CANDIDATE"
            elif day == disposition["date"] == "2026-03-01" and row["status"] == "BASELINE_TOTALS_CONFLICT":
                alt = disposition["alternative"]
                source_date = alt["date"]
                raw = subprocess.check_output(["git","-C",str(source),"show",SOURCE+":docs/Data/"+source_date.replace("-","_")+".csv"])
                source_blob = hashlib.sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest()
                if source_blob != alt["blob"] or row["source_blob"] != disposition["original_archive"]["blob"]:
                    raise ValueError("March source lineage mismatch")
                n,q,a,count = summarize(raw)
                if (n,q,a,count) != (int(base["traded_securities"]),int(base["traded_shares"]),Decimal(base["turnover_npr"]),alt["transactions"]):
                    raise ValueError("March alternative mismatch")
                status = "SECONDARY_DATE_SHIFT_CANDIDATE"
            else:
                raise ValueError("Unresolved recovery: "+day)
        if count <= 0:
            raise ValueError("Invalid transaction count")
        result.append(dict(date=day,transactions=count,quantity=base["traded_shares"],turnover_npr=base["turnover_npr"],securities=base["traded_securities"],source_date=source_date,source_blob=source_blob,status=status,official_review="PENDING",publication_allowed="false"))
    counts = Counter(r["status"] for r in result)
    if counts != {"EXISTING_BASELINE_CANDIDATE":41,"ARCHIVE_CONTRACT_PARITY_CANDIDATE":5,"SECONDARY_TOTALS_MATCH_CANDIDATE":148,"SECONDARY_DATE_SHIFT_CANDIDATE":1}:
        raise ValueError("Unexpected disposition counts")
    with (output/"master_session_candidates.csv").open("x",newline="",encoding="utf-8") as stream:
        w=csv.DictWriter(stream,fieldnames=list(result[0]))
        w.writeheader()
        w.writerows(result)
    summary=dict(rows=len(result),counts=dict(counts),officially_approved=0,promoted=0)
    (output/"master_summary.json").write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))
if __name__ == "__main__":
    import sys
    main(Path(sys.argv[1]),Path(sys.argv[2]))
