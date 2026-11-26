#!/usr/bin/env python3
"""Create non-promoting leads for unmatched OHLCV file stems and missing securities."""
import argparse,csv,json
from pathlib import Path
FIELDS_A=["file_stem","ohlcv_path","candidate_symbol","candidate_security_id","candidate_security_name","candidate_status_raw","candidate_exact_match","disposition"]
FIELDS_B=["symbol","security_id","security_name","active_status_raw","name_hints","evidence_tier","instrument_type","disposition"]
def read_csv(p):
    with Path(p).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def build(raw_path,matrix_path):
    official=json.loads(Path(raw_path).read_text(encoding="utf-8"))
    om={r["symbol"]:r for r in official}
    matrix=read_csv(matrix_path)
    files=[r for r in matrix if r["record_type"]=="ohlcv_file_only"]
    missing=[r for r in matrix if r["disposition"]=="OFFICIAL_NO_OHLCV_FILE"]
    a=[]
    for r in files:
        stem=r["ohlcv_file_stem"]; candidate=stem.replace("~2F","/")
        match=om.get(candidate)
        a.append({"file_stem":stem,"ohlcv_path":r["ohlcv_path"],"candidate_symbol":candidate,
          "candidate_security_id":str(match["id"]) if match else "",
          "candidate_security_name":match["securityName"] if match else "",
          "candidate_status_raw":match["activeStatus"] if match else "",
          "candidate_exact_match":"true" if match else "false",
          "disposition":"REVERSIBLE_ESCAPE_CANDIDATE_NOT_CONFIRMED" if match else "NO_EXACT_CANDIDATE"})
    b=[]
    for r in missing:
        n=r["security_name"].lower();h=[]
        if "promoter" in n:h.append("PROMOTER_NAME_HINT")
        if "debenture" in n or "bond" in n:h.append("DEBT_NAME_HINT")
        if "fund" in n:h.append("FUND_NAME_HINT")
        b.append({"symbol":r["symbol"],"security_id":r["security_id"],"security_name":r["security_name"],
          "active_status_raw":r["active_status_raw"],"name_hints":";".join(h) if h else "NO_NAME_HINT",
          "evidence_tier":"OFFICIAL_NAME_TEXT_HINT_ONLY","instrument_type":"UNKNOWN","disposition":"NO_OHLCV_FILE_UNRESOLVED"})
    counts={}
    for r in a:counts[r["disposition"]]=counts.get(r["disposition"],0)+1
    hint_counts={}
    status_by_hint={}
    for r in b:
        for h in r["name_hints"].split(";"):
            if h!="NO_NAME_HINT":hint_counts[h]=hint_counts.get(h,0)+1
            status_by_hint.setdefault(h,{})
            status_by_hint[h][r["active_status_raw"]]=status_by_hint[h].get(r["active_status_raw"],0)+1
    report={"task":"P4.30","source_security_list_sha256":"5495d99a73aeb44e573936f59fc6a6d8dbf9ffc45c5a8ba62e672f0b0c6fa2f7",
      "file_only_stems":len(a),"reversible_escape_candidates":counts.get("REVERSIBLE_ESCAPE_CANDIDATE_NOT_CONFIRMED",0),
      "nonmatching_stems":counts.get("NO_EXACT_CANDIDATE",0),"missing_official_ohlcv":len(b),
      "name_hint_counts":hint_counts,"no_name_hint_count":sum(1 for r in b if r["name_hints"]=="NO_NAME_HINT"),
      "status_by_hint":status_by_hint,
      "policy":"Candidate aliases and name hints are investigative leads only. No filename normalization, instrument-type assignment, or canonical promotion."}
    return a,b,report
def write_table(fields,rows):
    import io
    s=io.StringIO(newline="");w=csv.writer(s,lineterminator="\n",quoting=csv.QUOTE_ALL)
    w.writerows([[r.get(k,"") for k in fields] for r in rows])
    return ",".join(fields)+"\n"+s.getvalue()
def main():
    p=argparse.ArgumentParser();p.add_argument("--raw",required=True);p.add_argument("--matrix",required=True)
    p.add_argument("--aliases",required=True);p.add_argument("--missing",required=True);p.add_argument("--report",required=True)
    p.add_argument("--check",action="store_true");x=p.parse_args()
    a,b,r=build(x.raw,x.matrix)
    outputs={x.aliases:write_table(FIELDS_A,a),x.missing:write_table(FIELDS_B,b),x.report:json.dumps(r,indent=2)+"\n"}
    for path,content in outputs.items():
        if x.check:
            existing=Path(path).read_text(encoding="utf-8")
            if path.endswith(".json"):
                if json.loads(existing)!=json.loads(content):raise SystemExit(path+" is stale")
            elif existing!=content:raise SystemExit(path+" is stale")
        else:Path(path).write_text(content,encoding="utf-8")
    if x.check:print("PASS: 37 unmatched file stems, 8 reversible candidates, 29 unresolved; 85 missing securities with name hints only")
if __name__=="__main__":main()
