"""Map all outstanding bulk recovery requests to hash-pinned secondary archives."""
import argparse,csv,json,re
from collections import Counter,defaultdict
from pathlib import Path
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--directory",required=True)
    root=Path(p.parse_args().directory)
    tree=json.loads(Path("reference/p433_floorsheets/huggingface_repo_tree.json").read_text())
    inventory={}
    for r in tree["files"]:
        m=re.fullmatch(r"floorsheet/(\d{4}-\d{2}-\d{2})\.csv\.gz",r["path"])
        if not m:continue
        day=m[1]
        if day in inventory:raise ValueError("duplicate date in secondary inventory")
        if not re.fullmatch(r"[0-9a-f]{64}",(r.get("lfs") or {}).get("oid","")) or r["size"]<=0:raise ValueError("invalid metadata")
        inventory[day]=r
    with (root/"bulk_equity_floorsheet_disposition.csv").open(newline="") as f:
        rows=list(csv.DictReader(f))
    keys={(r["symbol"],r["date"]) for r in rows}
    if len(keys)!=len(rows) or len(keys)!=68773:raise ValueError("queue coverage")
    counts=Counter()
    dates=defaultdict(set)
    with (root/"secondary_bulk_coverage.csv").open("w",newline="") as f:
        w=csv.writer(f)
        w.writerow(["symbol","date","primary_status","secondary_status","secondary_path","secondary_sha256","secondary_size","promotion_allowed"])
        for r in rows:
            d=r["date"]
            item=inventory.get(d)
            if r["status"]=="NO_PINNED_PARTITION":category="SECONDARY_ONLY_CANDIDATE" if item else "NO_INDEXED_SOURCE"
            else:category="PRIMARY_AND_SECONDARY" if item else "PRIMARY_ONLY"
            counts[category]+=1
            dates[category].add(d)
            w.writerow([r["symbol"],d,r["status"],category,item["path"] if item else "",item["lfs"]["oid"] if item else "",item["size"] if item else "","false"])
    report={"requests":len(rows),"secondary_inventory_dates":len(inventory),"counts":dict(counts),"dates":{k:len(v) for k,v in dates.items()},"promoted":0,"limitations":"Inventory coverage only; contents and actual session status not yet verified."}
    (root/"secondary_bulk_coverage_summary.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(report))
if __name__=="__main__":main()
