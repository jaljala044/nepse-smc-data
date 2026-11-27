"""Conservative observed execution boundary evidence, not official candle admission."""
import argparse,csv,gzip,hashlib,io,json,re
from collections import Counter,defaultdict
from datetime import datetime,time
from decimal import Decimal
from pathlib import Path
try:
    from tools.capture_p433_first_trade_floorsheets import BASE,fetch,tree_metadata
    from tools.p443_full_session_parity import signature
except ModuleNotFoundError:
    from capture_p433_first_trade_floorsheets import BASE,fetch,tree_metadata
    from p443_full_session_parity import signature

def trade_time(row,day):
    values=[]
    for field in ("time","trade_time","tradeTime","transaction_time","transactionTime","contract_time","contractTime"):
        raw=(row.get(field) or "").strip()
        if not raw:continue
        if re.fullmatch(r"\d{2}:\d{2}:\d{2}(\.\d{1,6})?",raw):
            values.append(time.fromisoformat(raw))
        else:
            dt=datetime.fromisoformat(raw)
            if dt.date().isoformat()!=day or dt.tzinfo is not None:
                raise ValueError("ambiguous timestamp date or timezone")
            values.append(dt.time())
    if not values or len(set(values))!=1:raise ValueError("missing or conflicting trade timestamp")
    return values[0]

def boundaries(trades):
    if not trades:return "NO_OBSERVED_CONTRACT_UNKNOWN",None,None
    if any(t is None for t,_ in trades):return "TIMESTAMP_INCOMPLETE",None,None
    first=min(t for t,_ in trades);last=max(t for t,_ in trades)
    opens={p for t,p in trades if t==first};closes={p for t,p in trades if t==last}
    if len(opens)!=1 or len(closes)!=1:return "AMBIGUOUS_BOUNDARY_TIE",None,None
    return "OBSERVED_BOUNDARIES",next(iter(opens)),next(iter(closes))

def main():
    p=argparse.ArgumentParser();p.add_argument("--directory",required=True);a=p.parse_args()
    root=Path(a.directory)
    with (root/"bulk_equity_floorsheet_disposition.csv").open(newline="") as f:
        targets=[r for r in csv.DictReader(f) if r["status"] in {"HIGH_LOW_VOLUME_MATCH_OPEN_CLOSE_UNVERIFIED","HIGHL_VOLUME_MATCH_OPEN_CLOSE_UNVERIFIED"}]
    keys={(r["symbol"],r["date"]) for r in targets}
    if not keys or len(keys)!=len(targets):raise ValueError("missing or duplicate targets")
    bydate=defaultdict(dict)
    for r in targets:bydate[r["date"]][r["symbol"]]=r
    meta=tree_metadata();counts=Counter()
    with (root/"observed_open_close_evidence.csv").open("w",newline="") as f:
        w=csv.writer(f);w.writerow(["symbol","date","status","source_open","source_close","observed_open","observed_close","source_sha256","promotion_allowed"])
        for day,group in sorted(bydate.items()):
            trades=defaultdict(list);hlv=defaultdict(list);ids=set();digest="";failure=""
            try:
                path=f"floorsheet/{day}.csv.gz";m=meta[path]
                status,_,data=fetch(BASE+path);digest=hashlib.sha256(data).hexdigest()
                if status!=200 or digest!=m["lfs"]["oid"] or len(data)!=m["size"]:raise ValueError("source integrity")
                for row in csv.DictReader(io.StringIO(gzip.decompress(data).decode("utf-8-sig"))):
                    k=signature(row,True,day)
                    if k[1] in ids:raise ValueError("duplicate contract")
                    ids.add(k[1])
                    if k[2] not in group:continue
                    try:t=trade_time(row,day)
                    except ValueError:t=None
                    trades[k[2]].append((t,k[6]));hlv[k[2]].append((k[6],k[5]))
                if not ids:raise ValueError("empty session")
            except Exception as e:failure=str(e)
            for sym,r in sorted(group.items()):
                o=c=None
                if failure:status="PARTITION_UNAVAILABLE_OR_INVALID"
                elif not hlv[sym]:status="NO_OBSERVED_CONTRACT_UNKNOWN"
                elif (max(x[0] for x in hlv[sym]),min(x[0] for x in hlv[sym]),sum(x[1] for x in hlv[sym]))!=tuple(Decimal(r[k]) for k in ("source_high","source_low","source_volume")):status="SECONDARY_HLV_CONFLICT"
                else:
                    status,o,c=boundaries(trades[sym])
                    if status=="OBSERVED_BOUNDARIES":status="OBSERVED_OHLCV_MATCH" if (o,c)==(Decimal(r["source_open"]),Decimal(r["source_close"])) else "OBSERVED_OPEN_CLOSE_CONFLICT"
                counts[status]+=1;w.writerow([sym,day,status,r["source_open"],r["source_close"],o if o is not None else "",c if c is not None else "",digest,"false"])
    report={"targets":len(keys),"dates":len(bydate),"status_counts":dict(counts),"promoted":0,"limitations":"Observed first/last trades only; no official candle convention, auction eligibility, corporate action adjustment, completeness, or independent upstream provenance established."}
    (root/"observed_open_close_summary.json").write_text(json.dumps(report,indent=2));print(json.dumps(report))
if __name__=="__main__":main()
