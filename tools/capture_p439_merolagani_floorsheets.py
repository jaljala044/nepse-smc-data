#!/usr/bin/env python3
"""Capture Merolagani's datewise full-market floorsheet for P4.39."""
import hashlib
import json
import re
import time
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

BASE_URL="https://merolagani.com/Floorsheet.aspx"
UPSTREAM_IMPLEMENTATION_REPO="vuwon/NEPSEAPI"
UPSTREAM_IMPLEMENTATION_COMMIT="ae8c1ded3007d8105be6ba987734994ea7f56eac"
DATE_FIELD="ctl00$ContentPlaceHolder1$txtFloorsheetDateFilter"
SEARCH_EVENT_TARGET="ctl00$ContentPlaceHolder1$lbtnSearchFloorsheet"
PAGER_BUTTON_TARGET="ctl00$ContentPlaceHolder1$PagerControl1$btnPaging"
PAGER_PAGE_FIELD="ctl00$ContentPlaceHolder1$PagerControl1$hdnCurrentPage"
HEADERS={
 "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
 "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
 "Accept-Language":"en-US,en;q=0.9",
 "Origin":"https://merolagani.com",
 "Referer":BASE_URL,
}
DATES=[
 {"date":"2024-05-16","symbol":"NMLBBL","role":"prior","expected_rows":None},
 {"date":"2024-05-19","symbol":"NMLBBL","role":"candidate","expected_rows":15,"expected_volume":"864","expected_turnover":"557461.60"},
 {"date":"2024-08-14","symbol":"SMPDA","role":"prior","expected_rows":None},
 {"date":"2024-08-18","symbol":"SMPDA","role":"candidate","expected_rows":192,"expected_volume":"5314","expected_turnover":"6175193.80"},
]
def sha256(data):
 return hashlib.sha256(data).hexdigest()
def decimal(value):
 if value is None:return None
 try:return Decimal(str(value).replace(",","").strip())
 except InvalidOperation:return None
def extract_form_state(soup):
 state={}
 for name in ("__VIEWSTATE","__VIEWSTATEGENERATOR","__EVENTVALIDATION","__VIEWSTATEENCRYPTED","__PREVIOUSPAGE"):
  tag=soup.find("input",{"name":name})
  if tag is not None and tag.get("value") is not None:state[name]=tag["value"]
 if "__VIEWSTATE" not in state:raise ValueError("Missing ASP.NET __VIEWSTATE; page layout may have changed or request was blocked")
 return state
def get_total_pages(soup):
 match=re.search(r"Total pages:\\s*(\\d+)",soup.get_text(" ",strip=True),re.I)
 return int(match.group(1)) if match else None
def get_total_records(soup):
 match=re.search(r"of\\s+([\\d,]+)\\s+records",soup.get_text(" ",strip=True),re.I)
 return int(match.group(1).replace(",","")) if match else None
def parse_rows(soup,trade_date):
 target=None
 for table in soup.find_all("table"):
  headers={th.get_text(strip=True).lower() for th in table.find_all("th")}
  if {"symbol","buyer","seller","quantity","rate","amount"}<=headers:
   target=table;break
 if target is None:return []
 rows=[]
 for tr in target.find_all("tr"):
  cells=tr.find_all("td")
  if len(cells)<8:continue
  sn,txn,symbol,buyer,seller,qty,rate,amount=cells[:8]
  def link_or_text(cell):
   a=cell.find("a")
   return (a.get_text(strip=True),a.get("title","").strip()) if a else (cell.get_text(strip=True),"")
  sym,sym_name=link_or_text(symbol);buy,buy_name=link_or_text(buyer);sell,sell_name=link_or_text(seller)
  rows.append({
   "transaction_no":txn.get_text(strip=True),"trade_date":trade_date,"symbol":sym.upper(),
   "company_name":sym_name,"buyer_broker_code":buy,"buyer_broker_name":buy_name,
   "seller_broker_code":sell,"seller_broker_name":sell_name,
   "quantity":decimal(qty.get_text()),"rate":decimal(rate.get_text()),"amount":decimal(amount.get_text()),
  })
 return rows
def summarize_day(date_record,pages,expected_total):
 rows=[row for page in pages for row in page["rows"]]
 symbol=date_record["symbol"];target=[row for row in rows if row["symbol"]==symbol]
 txn_ids=[row["transaction_no"] for row in rows]
 target_txns=[row["transaction_no"] for row in target]
 duplicate_ids=len(txn_ids)-len(set(txn_ids))
 arithmetic_errors=sum(1 for row in rows if row["quantity"] is None or row["rate"] is None or row["amount"] is None or abs(row["quantity"]*row["rate"]-row["amount"])>Decimal("0.01"))
 date_prefix=date_record["date"].replace("-","")
 date_prefix_mismatches=sum(1 for row in rows if not row["transaction_no"].startswith(date_prefix))
 qty=sum((row["quantity"] or Decimal(0)) for row in target)
 amount=sum((row["amount"] or Decimal(0)) for row in target)
 page_count=pages[0]["total_pages"] if pages else None
 expected_page_rows=pages[0]["total_records"] if pages else None
 pagination_complete=(isinstance(page_count,int) and page_count>0 and len(pages)==page_count and expected_page_rows==len(rows)==expected_total)
 content_valid=(duplicate_ids==0 and arithmetic_errors==0 and date_prefix_mismatches==0)
 candidate_match=None
 if date_record["role"]=="candidate":
  candidate_match={
   "target_rows":len(target)==date_record["expected_rows"],
   "shares":qty==Decimal(date_record["expected_volume"]),
   "turnover":amount==Decimal(date_record["expected_turnover"]),
  }
 return {
  "date":date_record["date"],"symbol":symbol,"role":date_record["role"],
  "total_market_rows":len(rows),"upstream_total_records":expected_total,
  "total_pages":page_count,"pages_captured":len(pages),
  "pagination_complete":pagination_complete,"content_valid":content_valid,
  "unique_transaction_numbers":len(set(txn_ids)),"duplicate_transaction_numbers":duplicate_ids,
  "amount_arithmetic_errors":arithmetic_errors,"transaction_date_prefix_mismatches":date_prefix_mismatches,
  "target_transaction_count":len(target),"target_unique_transaction_numbers":len(set(target_txns)),
  "target_shares":str(qty),"target_turnover":str(amount),
  "target_rows":target,"candidate_parity":candidate_match,
  "target_absent_in_complete_market_sheet":(len(target)==0 and pagination_complete and content_valid),
  "secondary_evidence_gate":pagination_complete and content_valid and (candidate_match is None or all(candidate_match.values())),
 }
def capture_day(client,date_record,out_dir,delay=0.25):
 date=date_record["date"];folder=out_dir/date;folder.mkdir(parents=True,exist_ok=True);pages=[];requests=[]
 def save_response(response,name):
  raw=response.content;path=folder/name;path.write_bytes(raw)
  return {"file":str(path),"url":str(response.request.url),"http_status":response.status_code,"content_type":response.headers.get("content-type"),"bytes":len(raw),"sha256":sha256(raw),"retrieved_at_utc":datetime.now(timezone.utc).isoformat()}
 initial=client.get(BASE_URL);requests.append(save_response(initial,"initial.html"));initial.raise_for_status()
 state=extract_form_state(BeautifulSoup(initial.text,"html.parser"))
 form=dict(state);form["__EVENTTARGET"]=SEARCH_EVENT_TARGET;form["__EVENTARGUMENT"]="";form[DATE_FIELD]=datetime.strptime(date,"%Y-%m-%d").strftime("%Y/%m/%d")
 response=client.post(BASE_URL,data=form);requests.append(save_response(response,"search_page_001.html"));response.raise_for_status()
 soup=BeautifulSoup(response.text,"html.parser");state=extract_form_state(soup)
 total_pages=get_total_pages(soup);total_records=get_total_records(soup)
 if total_pages is None or total_records is None:
  return {"date":date,"symbol":date_record["symbol"],"status":"PAGINATION_METADATA_MISSING","requests":requests,"total_pages":total_pages,"total_records":total_records}
 if total_pages<1:
  return {"date":date,"symbol":date_record["symbol"],"status":"NO_PAGES_REPORTED","requests":requests,"total_pages":total_pages,"total_records":total_records}
 for page_no in range(1,total_pages+1):
  if page_no>1:
   time.sleep(delay)
   form=dict(state);form["__EVENTTARGET"]=PAGER_BUTTON_TARGET;form["__EVENTARGUMENT"]="";form[PAGER_PAGE_FIELD]=str(page_no);form[DATE_FIELD]=datetime.strptime(date,"%Y-%m-%d").strftime("%Y/%m/%d")
   response=client.post(BASE_URL,data=form);requests.append(save_response(response,f"search_page_{page_no:03d}.html"));response.raise_for_status()
   soup=BeautifulSoup(response.text,"html.parser");state=extract_form_state(soup)
   if get_total_pages(soup)!=total_pages or get_total_records(soup)!=total_records:raise RuntimeError(f"{date}: upstream pagination totals changed on page {page_no}")
  page_rows=parse_rows(soup,date)
  page_meta=requests[-1].copy();page_meta.update(page=page_no,rows=len(page_rows),total_pages=total_pages,total_records=total_records)
  pages.append({"meta":page_meta,"rows":page_rows})
 result=summarize_day(date_record,pages,total_records)
 result.update(status="CAPTURED",requests=requests,pages=[p["meta"] for p in pages])
 (folder/"summary.json").write_text(json.dumps(result,indent=2,default=str)+"\n",encoding="utf-8")
 return result
def capture(output_dir):
 out=Path(output_dir);out.mkdir(parents=True,exist_ok=True);results=[]
 with httpx.Client(headers=HEADERS,verify=True,timeout=45.0,http2=True,follow_redirects=True) as client:
  for item in DATES:
   try:results.append(capture_day(client,item,out))
   except Exception as exc:results.append({"date":item["date"],"symbol":item["symbol"],"role":item["role"],"status":"CAPTURE_FAILED","error":f"{type(exc).__name__}: {exc}"})
 report={"task":"P4.39","provider":"Merolagani.com datewise floorsheet","source_tier":"SECONDARY_PROVIDER_TRANSACTION_LEDGER","upstream_implementation":{"repo":UPSTREAM_IMPLEMENTATION_REPO,"commit":UPSTREAM_IMPLEMENTATION_COMMIT},"retrieved_at_utc":datetime.now(timezone.utc).isoformat(),"results":results,"interpretation":"Only a fully paginated market sheet with matching total record count, unique transaction numbers, valid amount arithmetic and transaction-number date prefixes can support a secondary target-absence claim. This is not NEPSE primary evidence."}
 (out/"capture_report.json").write_text(json.dumps(report,indent=2,default=str)+"\n",encoding="utf-8")
 return report
if __name__=="__main__":
 result=capture("reference/p439_merolagani_floorsheets")
 for item in result["results"]:print(item["date"],item["symbol"],item["status"],"rows=",item.get("total_market_rows"),"target=",item.get("target_transaction_count"),"complete=",item.get("pagination_complete"))
