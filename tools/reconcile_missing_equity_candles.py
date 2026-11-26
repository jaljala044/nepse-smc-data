"""Reconcile missing candidates against actual derived output; never insert data."""
import argparse,csv,json
from pathlib import Path
from collections import Counter
from reconcile_equity_external_archive import read,key,valid,write,sha

def main():
    p=argparse.ArgumentParser()
    for n in ('root','external','evidence','derived','output'):p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    candidates=read(a.evidence/'missing_candidates.csv')
    ledger=read(a.derived/'decision_ledger.csv')
    shifts={(r['symbol'],r['target_date']):r for r in ledger if r['action']=='SHIFT_DATE'}
    assert len(shifts)==sum(r['action']=='SHIFT_DATE' for r in ledger)
    assert len({(r['symbol'],r['date']) for r in candidates})==len(candidates)
    cal={r['date']:r['status'] for r in read(a.root/'reference/nepse_canonical_session_calendar_2025-2026.csv')}
    cache={};results=[];counts=Counter()
    for r in candidates:
        s,d=r['symbol'],r['date']
        if s not in cache:
            ep=a.external/'data'/'series'/f'{s}.csv';dp=a.derived/f'{s}_OHLCV.csv'
            ee=read(ep);dd=read(dp)
            assert len({x['date'] for x in dd})==len(dd)
            cache[s]=(ee,{x['date']:x for x in dd},sha(ep),sha(dp))
        ee,dd,eh,dh=cache[s];assert eh==r['external_sha256']
        matches=[x for x in ee if x['date']==d and x['symbol']==s]
        v=key(matches[0]) if len(matches)==1 else None
        if (s,d) in shifts:
            assert d in dd and key(dd[d])==v and valid(v)
            status='ALREADY_RECOVERED_DATE_SHIFT'
        elif d in dd:status='ALREADY_PRESENT_REVIEW'
        elif not valid(v):status='QUARANTINE_INVALID_EXTERNAL_OHLCV'
        elif cal.get(d)=='verified_closed':status='QUARANTINE_CLOSED_DATE'
        elif cal.get(d)=='verified_open_observed':status='SOURCE_SUPPORTED_MISSING_NEEDS_INDEPENDENT_CHECK'
        else:status='MISSING_CALENDAR_UNVERIFIED'
        counts[status]+=1
        results.append(dict(symbol=s,date=d,status=status,calendar_status=cal.get(d,'outside_calendar'),open=str(v[0]) if v else '',high=str(v[1]) if v else '',low=str(v[2]) if v else '',close=str(v[3]) if v else '',volume=str(v[4]) if v else '',turnover=matches[0].get('turnover','') if len(matches)==1 else '',external_sha256=eh,derived_sha256=dh))
    fields=['symbol','date','status','calendar_status','open','high','low','close','volume','turnover','external_sha256','derived_sha256']
    write(a.output/'all_candidates.csv',results,fields)
    pending=[r for r in results if not r['status'].startswith('ALREADY_')]
    write(a.output/'recovery_queue.csv',pending,fields)
    totals=dict(candidates=len(results),remaining=len(pending),shift_targets=len(shifts),inserted=0,**counts)
    (a.output/'totals.json').write_text(json.dumps(totals,indent=2)+'\n')
    print(json.dumps(totals,indent=2))
if __name__=='__main__':main()
