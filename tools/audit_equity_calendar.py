"""Read-only audit of both equity repositories against captured market closures."""
import argparse, csv, hashlib, json
from pathlib import Path
from collections import Counter
from decimal import Decimal
def read(p):
    with p.open(newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--smc',type=Path,required=True)
    p.add_argument('--starter',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(); a.output.mkdir(parents=True,exist_ok=True)
    ref=a.smc/'reference'
    symbols=sorted({r['symbol'] for r in read(ref/'nepse_target_universe_candidates_2026-11-26.csv') if r['instrument_class_from_rendered_list']=='Equity'})
    if len(symbols)!=281: raise ValueError(f'Unexpected universe: {len(symbols)}')
    calendar={r['date']:r['status'] for r in read(ref/'nepse_canonical_session_calendar_2025-2026.csv')}
    summary=[]; flags=[]
    for name,root in [('starter',a.starter),('smc',a.smc)]:
        for symbol in symbols:
            path=root/'03_stock_charts_ohlcv'/f'{symbol}_OHLCV.csv'
            if not path.is_file():
                summary.append(dict(repository=name,symbol=symbol,status='MISSING')); continue
            raw=path.read_bytes(); sha=hashlib.sha256(raw).hexdigest()
            rows=read(path); counts=Counter(); prior=None
            for idx,original in enumerate(rows,2):
                r={k.strip().lower():v for k,v in original.items()}; date=r['date']
                status=calendar.get(date,'outside_calendar')
                counts[status]+=1
                try: values=tuple(Decimal(r[k]) for k in ('open','high','low','close','volume'))
                except (KeyError,ValueError,ArithmeticError): values=None
                repeat=values is not None and values==prior
                if status=='verified_closed':
                    counts['closed_repeat']+=int(repeat)
                    flags.append(dict(repository=name,symbol=symbol,date=date,line=idx,adjacent_repeat=repeat,open=r.get('open'),high=r.get('high'),low=r.get('low'),close=r.get('close'),volume=r.get('volume'),source_sha256=sha))
                prior=values
            summary.append(dict(repository=name,symbol=symbol,status='AUDITED',rows=len(rows),verified_closed=counts['verified_closed'],closed_repeat=counts['closed_repeat'],outside_calendar=counts['outside_calendar'],verified_open_observed=counts['verified_open_observed'],other_calendar_status=len(rows)-counts['verified_closed']-counts['outside_calendar']-counts['verified_open_observed'],source_sha256=sha))
    def write(name,rows,fields):
        with (a.output/name).open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    write('summary.csv',summary,['repository','symbol','status','rows','verified_closed','closed_repeat','outside_calendar','verified_open_observed','other_calendar_status','source_sha256'])
    write('closed_date_flags.csv',flags,['repository','symbol','date','line','adjacent_repeat','open','high','low','close','volume','source_sha256'])
    totals={n:{'files_audited':sum(r['status']=='AUDITED' for r in summary if r['repository']==n),**{k:sum(r.get(k,0) for r in summary if r['repository']==n) for k in ('rows','verified_closed','closed_repeat','outside_calendar','verified_open_observed','other_calendar_status')}} for n in ('starter','smc')}
    (a.output/'totals.json').write_text(json.dumps(totals,indent=2)+'\n'); print(json.dumps(totals))
    if any(r['status']!='AUDITED' for r in summary): raise SystemExit('Missing equity files; see summary')
if __name__=='__main__': main()
