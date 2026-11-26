"""Build a provisional, evidence-tracked recent-equity dataset; never modify raw."""
import csv, hashlib, json, argparse
from pathlib import Path
from decimal import Decimal
def read(p):
    with p.open(newline='',encoding='utf-8-sig') as f: return list(csv.DictReader(f))
def blob(p):
    b=p.read_bytes();return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('.'));p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=a.root.resolve();out=a.output.resolve()
    if out==root or out.is_relative_to(root/'03_stock_charts_ohlcv'): raise ValueError('Output must be separate from raw')
    ref=root/'reference'
    inventory=read(ref/'P4_5_recent_equity_consolidated_2026-11-26.csv')
    exclusions=read(ref/'P4_5_closed_date_exclusion_overlay_2026-11-26.csv')
    shifts=read(ref/'P4_5_date_shift_overlay_2026-11-26.csv')
    calendar={r['date']:r['status'] for r in read(ref/'nepse_canonical_session_calendar_2025-2026.csv')}
    assert len(inventory)==21 and len(exclusions)==343 and len(shifts)==20
    ex={(r['symbol'],r['raw_date']):r for r in exclusions};sh={(r['symbol'],r['raw_date']):r for r in shifts}
    assert len(ex)==343 and len(sh)==20 and not set(ex)&set(sh)
    fields=['Date','Open','High','Low','Close','Volume']; results={};seen=set();manifest=[]
    for inv in inventory:
        s=inv['symbol'];path=root/'03_stock_charts_ohlcv'/f'{s}_OHLCV.csv';sha=blob(path)
        if sha!=inv['source_blob_sha']: raise ValueError(f'Source changed: {s}')
        raw=read(path);rows=[];removed=changed=0
        for r in raw:
            key=(s,r['Date'])
            if key in ex:
                e=ex[key];assert e['raw_blob_sha']==sha
                assert all(Decimal(r[k])==Decimal(e[k.lower()]) for k in fields[1:])
                assert calendar[r['Date']]=='verified_closed'
                seen.add(key);removed+=1;continue
            if key in sh:
                e=sh[key];assert e['raw_blob_sha']==sha and calendar[r['Date']]=='verified_closed'
                assert calendar[e['corrected_date']]=='verified_open_observed'
                r=dict(r,Date=e['corrected_date']);seen.add(key);changed+=1
            o,h,l,c,v=(Decimal(r[k]) for k in fields[1:])
            assert all(x.is_finite() for x in (o,h,l,c,v)) and h>=max(o,l,c) and l<=min(o,h,c) and v>0
            assert calendar.get(r['Date'])!='verified_closed'
            rows.append(r)
        rows.sort(key=lambda r:r['Date'])
        assert len({r['Date'] for r in rows})==len(rows)
        results[s]=rows
        manifest.append(dict(symbol=s,raw_rows=len(raw),excluded=removed,date_corrected=changed,derived_rows=len(rows),raw_blob_sha=sha,status='PROVISIONAL_NOT_INDEPENDENTLY_VERIFIED'))
    assert seen==set(ex)|set(sh)
    assert sum(r['raw_rows'] for r in manifest)==2877
    assert sum(r['derived_rows'] for r in manifest)==2534
    out.mkdir(parents=True,exist_ok=True)
    for s,rows in results.items():
        with (out/f'{s}_OHLCV.csv').open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    with (out/'manifest.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(manifest[0]));w.writeheader();w.writerows(manifest)
    print(json.dumps({'symbols':21,'raw_rows':2877,'derived_rows':2534,'excluded':343,'date_corrected':20,'status':'provisional'}))
if __name__=='__main__': main()
