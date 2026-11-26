#!/usr/bin/env python3
"""Capture four official NEPSE today-price boards and record date-filter behavior."""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

JOBS=[
 ("NMLBBL","2024-05-19"),
 ("NMLBBL","2024-05-16"),
 ("SMPDA","2024-08-18"),
 ("SMPDA","2024-08-14"),
]
def run_batch(output_root,runner=subprocess.run,now=None):
 root=Path(output_root);root.mkdir(parents=True,exist_ok=True);records=[]
 for symbol,business_date in JOBS:
  out=root/f"{symbol}_{business_date}";out.mkdir(parents=True,exist_ok=True)
  command=[sys.executable,"tools/capture_nepse_official_eod.py","--date",business_date,"--symbol",symbol,"--output-dir",str(out),"--allow-missing"]
  completed=runner(command,capture_output=True,text=True,env=os.environ.copy())
  manifest_path=out/"capture_manifest.json";error_path=out/"capture_error.json"
  item={"symbol":symbol,"business_date":business_date,"command_exit_code":completed.returncode,"output_dir":str(out)}
  if manifest_path.exists():
   manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
   item.update(status=manifest.get("status"),returned_business_dates=manifest.get("returned_business_dates"),target_row_count=manifest.get("target_row_count"),symbol_row_count=manifest.get("symbol_row_count"),total_pages=manifest.get("total_pages"),upstream_total_elements=manifest.get("upstream_total_elements"),pagination_row_count_matches=manifest.get("pagination_row_count_matches"),captured_pages=manifest.get("captured_pages"),target_row=manifest.get("target_row"))
  elif error_path.exists():
   item["status"]="CAPTURE_ERROR";item["capture_error"]=json.loads(error_path.read_text(encoding="utf-8"))
  else:
   item["status"]="CAPTURE_FAILED";item["stderr_preview"]=(completed.stderr or "")[:500]
  records.append(item)
 result={"task":"P4.37","source":"NEPSE official today-price EOD API","retrieved_at_utc":now or datetime.now(timezone.utc).isoformat(),"timezone_policy":"TZ=Asia/Kathmandu for date.today() used by pinned public client","records":records,"interpretation":"Only a unique exact-symbol/exact-businessDate row is a target match. Returned dates are recorded to detect ignored historical businessDate parameters. A missing target row is TARGET_ROW_MISSING, never NO_TRADE. All pages and upstream totals must reconcile before completeness is asserted."}
 (root/"batch_report.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 return result
if __name__=="__main__":
 result=run_batch("reference/p437_official_today_price")
 for r in result["records"]:
  print(r["symbol"],r["business_date"],r["status"],"dates=",r.get("returned_business_dates"),"target_rows=",r.get("target_row_count"),"total=",r.get("upstream_total_elements"))
