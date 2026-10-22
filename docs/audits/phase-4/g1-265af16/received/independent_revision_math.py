"""GPT Work own QA-004 plan-reference derivation. Not P4 business implementation/tests.
Manually transcribed fixed doc inputs and expected literals; no developer script/AQRP imports.
Decimal lattice membership checks and exact rational cash/exposure calculations.
"""
from decimal import Decimal as D, localcontext, ROUND_DOWN, ROUND_HALF_EVEN
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json, sys
O=Path(__file__).resolve().parent; groups=[]; edges=[]
def encode(x):
    if isinstance(x,(D,F)): return str(x)
    if isinstance(x,dict): return {k:encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)): return [encode(v) for v in x]
    return x
def record(to,n,inputs,formula,actual,expected):
    to.append(dict(case=n,inputs=encode(inputs),formula=formula,actual=encode(actual),expected=encode(expected),pass_=actual==expected))
    assert actual==expected,to[-1]
def lot(q,t,L,flag):
    if not L.is_finite() or L<=0: raise ValueError('lot must be finite positive')
    if not q.is_finite() or not t.is_finite(): raise ValueError('quantities must be finite')
    delta=t-q
    aligned_target=t%L==0; aligned_delta=delta%L==0
    allowed_hold=delta==0
    allowed_close=(q!=0 and t==0 and flag)
    if allowed_hold: status='UNCHANGED_HOLDING'
    elif t!=0 and not aligned_target: status='TARGET_LOT_MISMATCH'
    elif aligned_delta: status='ALIGNED_QUANTITIES_ONLY'
    elif allowed_close: status='FULL_CLOSE_LOT_EXCEPTION'
    else: status='DELTA_LOT_MISMATCH'
    return status,delta
def target(ideal,current,L):
    if ideal==current: return current
    # Decimal ROUND_DOWN is truncation toward zero; no float round trip.
    return (ideal/L).to_integral_value(rounding=ROUND_DOWN)*L
def funds(notion,E,R=F(0),reserve=F(0)):
    short=sum(max(-x,0) for x in notion); cash=E-sum(notion)
    return dict(cash=cash,restricted=R+short,margin=short,free_cash=cash-R-2*short-reserve)
def turn(q,q0,p,E): return sum(abs((a-b)*v) for a,b,v in zip(q,q0,p))/E
def interval(x,lo,hi): return lo-F(1,10**12)<=x<=hi+F(1,10**12)
# Quantity expected statuses/deltas frozen from ROUNDING_REFERENCE.md, not calculated by tested AQRP.
matrix=[
 ('R01','15','10',True,('DELTA_LOT_MISMATCH',-5)),
 ('R02','15','20',True,('DELTA_LOT_MISMATCH',5)),
 ('R03','15','15',False,('UNCHANGED_HOLDING',0)),
 ('R04','15','0',True,('FULL_CLOSE_LOT_EXCEPTION',-15)),
 ('R05','15','0',False,('DELTA_LOT_MISMATCH',-15)),
 ('R06','-15','0',True,('FULL_CLOSE_LOT_EXCEPTION',15)),
 ('R07','-15','0',False,('DELTA_LOT_MISMATCH',15)),
 ('R08','15','-10',True,('DELTA_LOT_MISMATCH',-25)),
 ('R09','-15','10',True,('DELTA_LOT_MISMATCH',25)),
 ('R10','10','20',False,('ALIGNED_QUANTITIES_ONLY',10)),
 ('R11','-15','-10',True,('DELTA_LOT_MISMATCH',5)),
 ('R12','-15','-20',True,('DELTA_LOT_MISMATCH',-5)),
 ('R13','-15','-15',False,('UNCHANGED_HOLDING',0)),
 ('R17','10','15',True,('TARGET_LOT_MISMATCH',5)),
]
for name,c,t,flag,expected in matrix:
    c,t=D(c),D(t); answer=lot(c,t,D(10),flag)
    record(groups,name,dict(current=c,target=t,lot=10,full_close=flag),'delta=t-current; exact Decimal remainders for both target/delta; only hold or full close exceptions',answer,expected)
    if name in ('R03','R13'):
        assert target(t,c,D(10))==c
# R01 includes the entire original counterexample, not just the A-leg status.
q=[F(10),F(90)]; q0=[F(15),F(0)]; p=[F(10),F(10)]; E=F(1000); w=[a*b/E for a,b in zip(q,p)]
record(edges,'X01-complete-account',dict(E=E,original_cash=850,current=q0,target=q,prices=p,scores=[1,9]),'equity identity; w=q*p/E; gross/net/Beta/same-industry; delta; turnover; funding',dict(equity=F(850)+sum(a*b for a,b in zip(q0,p)),weights=w,delta=[a-b for a,b in zip(q,q0)],gross=sum(abs(a) for a in w),net=sum(w),beta=sum(w),sector_net=sum(w),sector_gross=sum(abs(a) for a in w),turnover=turn(q,q0,p,E),funding=funds([a*b for a,b in zip(q,p)],E)),dict(equity=F(1000),weights=[F(1,10),F(9,10)],delta=[F(-5),F(90)],gross=F(1),net=F(1),beta=F(1),sector_net=F(1),sector_gross=F(1),turnover=F(19,20),funding=dict(cash=F(0),restricted=F(0),margin=F(0),free_cash=F(0))))
E=F(1000); p=[F(60),F(50)]; wc=[F(1,2),-F(1,2)]; qc=[a*E/b for a,b in zip(wc,p)]
# Independent exact floor via Decimal only for this finite integer final lattice.
qr=[F(target(D(500)/D(60),D(0),D(10))),F(target(D(-500)/D(50),D(0),D(10)))]
wr=[a*b/E for a,b in zip(qr,p)]; beta=sum(wr); sector_net=sum(wr); postfund=funds([a*b for a,b in zip(qr,p)],E)
record(groups,'R14',dict(E=E,continuous_weights=wc,prices=p,lot=10,beta=[1,1],sector=['X','X'],interval=[-F(1,10),F(1,10)]),'ideal=w*E/p; toward-zero target; same-industry net=sum(w); beta=sum(w*1); pre/post signed interval',dict(ideal=qc,target=qr,delta=qr,weights=wr,pre_gross=sum(abs(a) for a in wc),post_gross=sum(abs(a) for a in wr),pre_beta=sum(wc),post_beta=beta,pre_sector_net=sum(wc),post_sector_net=sector_net,pre_abs_beta=abs(sum(wc)),post_abs_beta=abs(beta),pre_interval=interval(sum(wc),-F(1,10),F(1,10)),post_interval=interval(beta,-F(1,10),F(1,10)),pre_funding=funds([a*b for a,b in zip(qc,p)],E),post_funding=postfund),dict(ideal=[F(25,3),F(-10)],target=[F(0),F(-10)],delta=[F(0),F(-10)],weights=[F(0),-F(1,2)],pre_gross=F(1),post_gross=F(1,2),pre_beta=F(0),post_beta=-F(1,2),pre_sector_net=F(0),post_sector_net=-F(1,2),pre_abs_beta=F(0),post_abs_beta=F(1,2),pre_interval=True,post_interval=False,pre_funding=dict(cash=F(1000),restricted=F(500),margin=F(500),free_cash=F(0)),post_funding=dict(cash=F(1500),restricted=F(500),margin=F(500),free_cash=F(500))))
q0=[F(10),F(0)]; qc=[E*F(1,2)/v for v in p]; qr=[F(0),F(10)]; pre=turn(qc,q0,p,E); post=turn(qr,q0,p,E)
record(groups,'R15',dict(E=E,current=q0,prices=p,weights=[F(1,2)]*2,lot=10,cap=F(4,5)),'turnover=sum(abs((q-q0)*p))/E; half=turnover/2; independent pre/post comparisons',dict(current_cash=E-sum(a*b for a,b in zip(q0,p)),ideal=qc,target=qr,ideal_delta=[a-b for a,b in zip(qc,q0)],delta=[a-b for a,b in zip(qr,q0)],pre_turnover=pre,post_turnover=post,pre_half=pre/2,post_half=post/2,pre_pass=pre<=F(4,5)+F(1,10**12),post_pass=post<=F(4,5)+F(1,10**12),post_funding=funds([a*b for a,b in zip(qr,p)],E)),dict(current_cash=F(400),ideal=[F(25,3),F(10)],target=[F(0),F(10)],ideal_delta=[-F(5,3),F(10)],delta=[F(-10),F(10)],pre_turnover=F(3,5),post_turnover=F(11,10),pre_half=F(3,10),post_half=F(11,20),pre_pass=True,post_pass=False,post_funding=dict(cash=F(500),restricted=F(0),margin=F(0),free_cash=F(500))))
ideal=[F(25,3),F(-10)]; rounded=[F(0),F(-10)]
funding=[]
for long,short in [(F(500),F(500)),(F(700),F(500))]:
    by_cash=funds([long,-short],E)['free_cash']; by_gross=E*(1-(long+short)/E); funding.append((by_cash,by_gross))
record(groups,'R16',dict(E=E,ideal=ideal,rounded=rounded,prices=p,same_sector=True),'component absolute contraction implies fixed positive-weight sum contraction; free=E-long-short-R-fee',dict(abs_qty=[abs(a)<=abs(b) for a,b in zip(rounded,ideal)],abs_notional=[abs(a*v)<=abs(b*v) for a,b,v in zip(rounded,ideal,p)],gross=sum(abs(a*v/E) for a,v in zip(rounded,p))<=sum(abs(a*v/E) for a,v in zip(ideal,p)),sector_gross=sum(abs(a*v/E) for a,v in zip(rounded,p))<=sum(abs(a*v/E) for a,v in zip(ideal,p)),funding=funding),dict(abs_qty=[True,True],abs_notional=[True,True],gross=True,sector_gross=True,funding=[(F(0),F(0)),(F(-200),F(-200))]))
for name,c,t,flag,expected in [
 ('ordinary_long_close_flag_false','10','0',False,('ALIGNED_QUANTITIES_ONLY',-10)),
 ('ordinary_short_close_flag_false','-10','0',False,('ALIGNED_QUANTITIES_ONLY',10)),
 ('aligned_long_to_short_flag_false','10','-10',False,('ALIGNED_QUANTITIES_ONLY',-20)),
 ('aligned_short_to_long_flag_false','-10','10',False,('ALIGNED_QUANTITIES_ONLY',20)),
 ('no_ratio_tolerance_for_target','10','10.0000000000001',True,('TARGET_LOT_MISMATCH',D('0.0000000000001'))),
]:
    record(edges,name,dict(current=c,target=t,lot=10,flag=flag),'exact quantity gate only, no success claim for other risk items',lot(D(c),D(t),D(10),flag),expected)
tiny=D('0.0000000000001'); ideal=D(15)+tiny; t=target(ideal,D(15),D(10))
record(edges,'no_tolerant_unchanged_fallback',dict(ideal=ideal,current=15,lot=10),'ideal!=current exactly; quantize to10, then reject delta -5',(t,lot(D(15),t,D(10),True)),(D(10),('DELTA_LOT_MISMATCH',D(-5))))
badlots=[]
for value in ['0','-10','NaN','Infinity','-Infinity']:
    try: lot(D(0),D(10),D(value),True)
    except ValueError: badlots.append(value)
record(edges,'invalid_lot_candidates_rejected',dict(values=['0','-10','NaN','Infinity','-Infinity']),'lot finite and strictly positive',badlots,['0','-10','NaN','Infinity','-Infinity'])
record(edges,'funding_with_restricted_and_fee',dict(E=1000,long=500,short=500,nonshort=17,reserve=3),'free=E*(1-gross)-nonshort-reserve',funds([F(500),F(-500)],E,F(17),F(3))['free_cash'],F(-20))
sample_count=0; quantities=list(map(D,['-25.5','-15','-0.5','0','0.5','15','25.5']))
with localcontext() as ctx:
    ctx.prec=34;ctx.rounding=ROUND_HALF_EVEN
    for ideal in product(quantities,repeat=3):
        prices=list(map(D,['3','7','11'])); lots=list(map(D,['10','3','2.5'])); current=list(map(D,['15','-15','0']))
        rounded=[target(a,c,l) for a,c,l in zip(ideal,current,lots)]
        assert all(abs(a)<=abs(b) for a,b in zip(rounded,ideal))
        assert sum(abs(a*p) for a,p in zip(rounded,prices))<=sum(abs(a*p) for a,p in zip(ideal,prices))
        for industry in [(0,2),(1,)]:
            assert sum(abs(rounded[i]*prices[i]) for i in industry)<=sum(abs(ideal[i]*prices[i]) for i in industry)
        sample_count+=1
assert len(groups)==17
groups.sort(key=lambda x:int(x['case'][1:]))
result=dict(actual_executor='GPT Work primary reviewer',fixed_sha='265af16353d85ce8c2d229a7517809d707498da8',scope='Independent stdlib Decimal/Fraction mathematical design verification only; no AQRP, developer reference imports or future product expected generation',groups=groups,groups_passed=len(groups),additional_edge_groups=edges,additional_edge_groups_passed=len(edges),monotonicity_vector_samples=sample_count,quantity_gate_success_is_not_portfolio_success=True,old_20_groups='Not re-executed; both original candidate doc and script byte-pinned to previous independently audited SHA',implementation_tests=False)
(O/'independent-math-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(actual_executor=result['actual_executor'],new_design_groups=len(groups),edge_groups=len(edges),property_samples=sample_count,result='PASS',implementation_tests=False),indent=2))
