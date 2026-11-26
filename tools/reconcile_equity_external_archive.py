"""Compare the historical equity universe with a pinned external archive.
Evidence only: no source rows are changed, no candidates promoted."""
import argparse,csv,hashlib,json
from pathlib import Path
from collections import Counter,defaultdict
from datetime import date
from decimal import Decimal,InvalidOperation

def read(p):
    with p.open(newline='',encoding='utf-8-sig') as f:
        return [{k.strip().lower():v for k,v in r.items() if k is not None} for r in csv.DictReader(f)]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def key(r):
    try:
        v=tuple(Decimal(r[k]) for k in ('open','high','low','close','volume'))
        return v if all(x.is_finite() for x in v) else None
    except (KeyError,InvalidOperation,TypeError): return None
def valid(v):
    if v is None:return False
    o,h,l,c,q=v
    return min(o,h,l,c,q)>0 and h>=max(o,l,c) and l<=min(o,h,c)
def write(p,rows,fields):
    with p.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--external',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    ref=a.root/'reference'; a.output.mkdir(parents=True,exist_ok=True)
    universe=sorted({r['symbol'] for r in read(ref/'equity_observed_date_coverage_2026-11-26.csv')})
    cal={r['date']:r['status'] for r in read(ref/'nepse_canonical_session_calendar_2025-2026.csv')}
    summaries=[];flags=[];missing=[]
    for s in universe:
        raw=a.root/'03_stock_charts_ohlcv'/f'{s}_OHLCV.csv'; ext=a.external/'data'/'series'/f'{s}.csv'
        if not raw.is_file() or not ext.is_file():
            summaries.append(dict(symbol=s,status='SOURCE_MISSING',raw_present=raw.is_file(),external_present=ext.is_file()));continue
        rr=read(raw);ee=read(ext);rh=sha(raw);eh=sha(ext)
        rm=defaultdict(list);em=defaultdict(list);ek=defaultdict(list)
        for r in rr:rm[r['date']].append(r)
        for r in ee:
            if r.get('symbol')!=s:raise ValueError(f'Identity mismatch {s}')
            em[r['date']].append(r)
            if key(r) is not None:ek[key(r)].append(r['date'])
        counts=Counter();prior=None
        for r in rr:
            d=r['date'];v=key(r);closed=cal.get(d)=='verified_closed';repeat=v is not None and v==prior;prior=v
            same=em.get(d,[]);match=len(same)==1 and v is not None and key(same[0])==v
            near=[x for x in ek.get(v,[]) if x!=d and abs((date.fromisoformat(x)-date.fromisoformat(d)).days)<=7 and cal.get(x)!='verified_closed' and len(em[x])==1]
            retained=[x for x in near if len(rm.get(x,[]))==1 and key(rm[x][0])==v]
            labels=[]
            if len(rm[d])>1 or len(same)>1:labels.append('DUPLICATE_DATE_CONFLICT')
            if not valid(v):labels.append('INVALID_RAW_OHLCV')
            if closed:
                if same:labels.append('CLOSED_DATE_EXTERNAL_CONFLICT')
                elif valid(v) and len(rm[d])==1 and len(near)==1 and len(retained)==1 and cal.get(retained[0])=='verified_open_observed':labels.append('REDUNDANT_CLOSED_CANDIDATE')
                elif valid(v) and len(rm[d])==1 and len(near)==1 and near[0] not in rm and cal.get(near[0])=='verified_open_observed':labels.append('DATE_SHIFT_CANDIDATE')
                else:labels.append('CLOSED_DATE_UNRESOLVED')
            if repeat:labels.append('ADJACENT_REPEAT')
            if same and not match:labels.append('SAME_DATE_VALUE_CONFLICT')
            if match:counts['exact_same_date']+=1
            if not same:counts['raw_date_absent_external']+=1
            for label in labels:counts[label]+=1
            if labels:flags.append(dict(symbol=s,date=d,flags=';'.join(labels),matching_dates=';'.join(sorted(set(near))),raw_ohlcv=';'.join(map(str,v)) if v else '',raw_sha256=rh,external_sha256=eh))
        first=min(rm,default='');last=max(rm,default='')
        for d,rs in em.items():
            if first<=d<=last and d not in rm:
                counts['external_only_within_raw_span']+=1
                v=key(rs[0]);missing.append(dict(symbol=s,date=d,status='MISSING_CANDIDATE' if len(rs)==1 and valid(v) and cal.get(d)!='verified_closed' else 'QUARANTINE',ohlcv=';'.join(map(str,v)) if v else '',calendar_status=cal.get(d,'outside_calendar'),external_sha256=eh))
        summaries.append(dict(symbol=s,status='COMPARED',raw_present=True,external_present=True,raw_rows=len(rr),external_rows=len(ee),raw_sha256=rh,external_sha256=eh,**counts))
    fields=sorted({k for r in summaries for k in r})
    write(a.output/'summary.csv',summaries,fields)
    write(a.output/'row_flags.csv',flags,['symbol','date','flags','matching_dates','raw_ohlcv','raw_sha256','external_sha256'])
    write(a.output/'missing_candidates.csv',missing,['symbol','date','status','ohlcv','calendar_status','external_sha256'])
    totals={'symbols_expected':len(universe),'symbols_compared':sum(r['status']=='COMPARED' for r in summaries),'source_missing':[r['symbol'] for r in summaries if r['status']!='COMPARED'],'flagged_rows':len(flags),'missing_candidates':len(missing),'status':'REVIEW_ONLY_NOT_INDEPENDENTLY_VERIFIED'}
    for k in fields:
        if k not in ('symbol','status','raw_present','external_present','raw_sha256','external_sha256'):totals[k]=sum(r.get(k,0) for r in summaries)
    (a.output/'totals.json').write_text(json.dumps(totals,indent=2)+'\n');print(json.dumps(totals,indent=2))
if __name__=='__main__':main()
