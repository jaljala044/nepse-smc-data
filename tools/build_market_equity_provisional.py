"""Build a conservative provisional market-wide dataset from reconciliation evidence.
Only exact, unique external matches on observed-open dates can support shifts or
closed-row exclusions. Other conflicts are quarantined; no external-only insertion.
"""
import argparse,csv,json,hashlib
from pathlib import Path
from collections import Counter,defaultdict
from reconcile_equity_external_archive import read,key,valid,sha,write

def main():
    p=argparse.ArgumentParser()
    for name in ('root','external','evidence','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();root=a.root.resolve();out=a.output.resolve()
    if out==root or out.is_relative_to(root/'03_stock_charts_ohlcv') or out.is_relative_to(a.external.resolve()):raise ValueError('Unsafe output')
    if out.exists() and any(out.iterdir()):raise ValueError('Output directory must be empty')
    out.mkdir(parents=True,exist_ok=True)
    calendar={r['date']:r['status'] for r in read(root/'reference/nepse_canonical_session_calendar_2025-2026.csv')}
    summary=read(a.evidence/'summary.csv');flags=read(a.evidence/'row_flags.csv')
    assert len(summary)==281 and len({r['symbol'] for r in summary})==281
    by=defaultdict(dict)
    for r in flags:
        assert r['date'] not in by[r['symbol']]
        by[r['symbol']][r['date']]=r
    manifest=[];ledger=[]
    fields=['date','open','high','low','close','volume']
    for s in summary:
        symbol=s['symbol'];assert s['status']=='COMPARED'
        raw=root/'03_stock_charts_ohlcv'/f'{symbol}_OHLCV.csv';ext=a.external/'data'/'series'/f'{symbol}.csv'
        assert sha(raw)==s['raw_sha256'] and sha(ext)==s['external_sha256']
        rows=read(raw);external=read(ext);rm=defaultdict(list);em=defaultdict(list)
        for r in rows:rm[r['date']].append(r)
        for r in external:
            assert r['symbol']==symbol
            em[r['date']].append(r)
        assert len(rows)==int(s['raw_rows'])
        counts=Counter();result=[];dates=set()
        proposed=Counter()
        for r in by[symbol].values():
            if 'DATE_SHIFT_CANDIDATE' in r['flags'].split(';'):proposed.update(r['matching_dates'].split(';'))
        for r in rows:
            d=r['date'];v=key(r);flag=by[symbol].get(d,{});labels=set(flag.get('flags','').split(';'))
            action='RETAIN_PROVISIONAL';target=d
            if flag:assert flag['raw_sha256']==s['raw_sha256'] and flag['external_sha256']==s['external_sha256']
            if not valid(v) or len(rm[d])!=1 or 'DUPLICATE_DATE_CONFLICT' in labels:action='QUARANTINE_INVALID'
            elif calendar.get(d)=='verified_closed':
                matches=flag.get('matching_dates','').split(';');m=matches[0]
                exact=len(matches)==1 and len(em[m])==1 and key(em[m][0])==v and calendar.get(m)=='verified_open_observed'
                if exact and 'REDUNDANT_CLOSED_CANDIDATE' in labels and len(rm[m])==1 and key(rm[m][0])==v:action='EXCLUDE_REDUNDANT'
                elif exact and 'DATE_SHIFT_CANDIDATE' in labels and m not in rm and proposed[m]==1:action='SHIFT_DATE';target=m
                else:action='QUARANTINE_CLOSED'
            elif 'SAME_DATE_VALUE_CONFLICT' in labels:action='QUARANTINE_CONFLICT'
            elif len(em[d])==1 and key(em[d][0])==v:action='RETAIN_SOURCE_MATCH'
            elif 'ADJACENT_REPEAT' in labels:action='QUARANTINE_UNMATCHED_REPEAT'
            else:action='QUARANTINE_UNMATCHED'
            counts[action]+=1
            if action.startswith('RETAIN') or action=='SHIFT_DATE':
                assert target not in dates and calendar.get(target)!='verified_closed' and valid(v)
                dates.add(target);result.append({**{k:r[k] for k in fields},'date':target})
            if action!='RETAIN_SOURCE_MATCH':
                ledger.append(dict(symbol=symbol,raw_date=d,target_date=target,action=action,flags=flag.get('flags',''),raw_sha256=s['raw_sha256'],external_sha256=s['external_sha256']))
        result.sort(key=lambda r:r['date'])
        assert len(result)==len(dates)
        assert sum(counts.values())==len(rows)
        write(out/f'{symbol}_OHLCV.csv',result,fields)
        manifest.append(dict(symbol=symbol,raw_rows=len(rows),output_rows=len(result),**counts))
    write(out/'manifest.csv',manifest,sorted({k for r in manifest for k in r}))
    write(out/'decision_ledger.csv',ledger,['symbol','raw_date','target_date','action','flags','raw_sha256','external_sha256'])
    totals={k:sum(r.get(k,0) for r in manifest) for k in sorted({k for r in manifest for k in r}-{'symbol'})}
    totals.update(symbols=len(manifest),status='PROVISIONAL_SOURCE_MATCHED_NOT_SCANNER_APPROVED',external_only_rows_inserted=0)
    (out/'totals.json').write_text(json.dumps(totals,indent=2)+'\n');print(json.dumps(totals,indent=2))
if __name__=='__main__':main()
