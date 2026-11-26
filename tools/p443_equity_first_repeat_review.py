"""Partition unresolved repeat findings by captured active instrument classification."""
import argparse,csv,json,subprocess
from collections import Counter,defaultdict
from pathlib import Path
PIN="56362fb4f65b91fdcca8f50b50e53ad80e703649"
MASTER="reference/nepse_ohlcv_active_instrument_crosscheck_2026-11-26.csv"

def classify(rows,master):
    for r in rows:
        if r["pair_classification"] not in {"BOTH_OPEN_TUPLE_UNVERIFIED","INSUFFICIENT_SESSION_EVIDENCE"}:continue
        kind=master.get(r["symbol"],"missing_master")
        priority={"current_equity_first_pass":"EQUITY_RECOVERY_PRIORITY","current_mutual_fund":"DEFER_MUTUAL_FUND"}.get(kind,"HOLD_UNCLASSIFIED")
        yield dict(r,instrument_classification=kind,review_priority=priority,promotion_allowed="false")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--directory",required=True)
    root=Path(p.parse_args().directory)
    master={}
    for r in csv.DictReader(subprocess.check_output(["git","show",PIN+":"+MASTER],text=True).splitlines()):
        k=r["ohlcv_symbol"]
        if k in master:raise ValueError("duplicate instrument master symbol")
        master[k]=r["classification"]
    counts=Counter()
    symbols=defaultdict(set)
    with (root/"repeat_calendar_triage.csv").open(newline="") as src,(root/"equity_first_repeat_review.csv").open("w",newline="") as dst:
        reader=csv.DictReader(src)
        w=csv.DictWriter(dst,fieldnames=reader.fieldnames+["instrument_classification","review_priority","promotion_allowed"])
        w.writeheader()
        for r in classify(reader,master):
            group=r["pair_classification"]
            priority=r["review_priority"]
            counts[(group,priority)]+=1
            symbols[(group,priority)].add(r["symbol"])
            w.writerow(r)
    expected={"BOTH_OPEN_TUPLE_UNVERIFIED":73,"INSUFFICIENT_SESSION_EVIDENCE":58899}
    for group,n in expected.items():
        if sum(v for (g,_),v in counts.items() if g==group)!=n:raise ValueError("coverage mismatch "+group)
    summary={"groups":[{"group":g,"priority":p,"pairs":n,"symbols":len(symbols[(g,p)]),"symbol_list":sorted(symbols[(g,p)]) if g=="BOTH_OPEN_TUPLE_UNVERIFIED" else None} for (g,p),n in sorted(counts.items())],"promoted":0,"limitations":"Current active classification is a prioritization aid, not point-in-time identity or historical execution verification."}
    (root/"equity_first_repeat_summary.json").write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary))
if __name__=="__main__":main()
