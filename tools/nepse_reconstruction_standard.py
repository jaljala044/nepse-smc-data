"""Research-only NEPSE candle reconstruction, with explicit ordering and lot gates."""
from decimal import Decimal
from datetime import datetime

def reconstruct(trades, *, lot_size, order_mode="contract_proxy"):
    if not isinstance(lot_size,int) or lot_size<=0: raise ValueError("invalid lot size")
    if order_mode not in ("contract_proxy","timestamp"): raise ValueError("unknown ordering")
    seen=set(); parsed=[]
    for r in trades:
        cid=str(r["contract"]).strip()
        q=Decimal(str(r["quantity"])); p=Decimal(str(r["rate"]))
        if not cid or cid in seen or not q.is_finite() or not p.is_finite() or q<=0 or q!=q.to_integral_value() or p<=0: raise ValueError("invalid or duplicate trade")
        seen.add(cid)
        eligible=q>=lot_size
        if order_mode=="timestamp" and eligible:
            ts=datetime.fromisoformat(r["time"])
            if ts.tzinfo is None: raise ValueError("timestamp must have timezone")
            key=ts
        elif order_mode=="contract_proxy" and eligible:
            if not cid.isascii() or not cid.isdigit(): raise ValueError("invalid contract proxy")
            key=int(cid)
        else: key=None
        parsed.append((key,q,p,eligible))
    regular=[r for r in parsed if r[3]]
    if not regular: return {"status":"NO_ELIGIBLE_PRICE_TRADES","volume":sum(r[1] for r in parsed),"promotion_allowed":False}
    if len({r[0] for r in regular})!=len(regular): raise ValueError("ambiguous ordering; authenticated tie-break required")
    ordered=sorted(regular,key=lambda r:r[0])
    return dict(open=ordered[0][2],high=max(r[2] for r in regular),low=min(r[2] for r in regular),close=ordered[-1][2],volume=sum(r[1] for r in parsed),regular_volume=sum(r[1] for r in regular),odd_proxy_volume=sum(r[1] for r in parsed if not r[3]),status="RESEARCH_ONLY",order_mode=order_mode,trade_type_status="QUANTITY_PROXY",promotion_allowed=False)
