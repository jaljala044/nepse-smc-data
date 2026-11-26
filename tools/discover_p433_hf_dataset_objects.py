#!/usr/bin/env python3
"""Discover actual immutable files in the HF dataset repo; do not infer from card examples."""
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API="https://huggingface.co/api/datasets/urekmazino69/Nepse-floorsheet-and-indices/tree/main?recursive=true&expand=false"
def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"NEPSE-P433-Archive-Discovery/1.0"})
    with urllib.request.urlopen(req,timeout=45) as response:
        return response.status,dict(response.headers.items()),response.read()
def discover(fetcher=fetch):
    status,headers,body=fetcher(API)
    payload=json.loads(body.decode("utf-8"))
    files=[]
    for item in payload:
        if item.get("type")=="file":
            files.append({"path":item.get("path"),"size":item.get("size"),"oid":item.get("oid"),"lfs":item.get("lfs")})
    targets={d:[] for d in ("2024-05-16","2024-05-19","2024-08-14","2024-08-18")}
    for f in files:
        for d in targets:
            if d in (f.get("path") or ""):
                targets[d].append(f)
    return {"retrieved_at_utc":datetime.now(timezone.utc).isoformat(),"api_url":API,"http_status":status,"file_count":len(files),"files":files,"target_date_path_matches":targets}
if __name__=="__main__":
    result=discover()
    out=Path("reference/p433_floorsheets");out.mkdir(parents=True,exist_ok=True)
    (out/"huggingface_repo_tree.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(f"HF repo tree: HTTP {result['http_status']}; {result['file_count']} files")
    for date,matches in result["target_date_path_matches"].items():
        print(f"{date}: {len(matches)} path matches")
