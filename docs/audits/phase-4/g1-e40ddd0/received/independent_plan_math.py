"""GPT Work own QA-004 derivation. Exact rational/Decimal design checks, NOT P4 implementation tests.
No import, execution or reuse of AQRP/developer golden routines. Expected literals transcribed
from fixed GOLDEN_REFERENCE.md. Generic arithmetic independently derives actual results.
"""
from fractions import Fraction as Q
from decimal import Decimal, localcontext, ROUND_HALF_EVEN
from pathlib import Path
import hashlib, json, sys
O=Path(sys.argv[1]); cases=[]; edges=[]
def encode(x):
    if isinstance(x,(Q,Decimal)): return str(x)
    if isinstance(x,dict): return {k:encode(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)): return [encode(v) for v in x]
    return x
def record(target,name,inputs,formula,actual,expected):
    item=dict(case=name,inputs=encode(inputs),formula=formula,actual=encode(actual),expected=encode(expected),pass_=actual==expected)
    target.append(item)
    if actual!=expected: raise AssertionError(item)
def C(n,i,f,a,e): record(cases,n,i,f,a,e)
def X(n,i,f,a,e): record(edges,n,i,f,a,e)
def combined(factors,a):
    common=set.intersection(*(set(f) for f in factors))
    return {k:sum(Q(aj)*Q(f[k]) for f,aj in zip(factors,a))/sum(abs(Q(v)) for v in a) for k in sorted(common)}
def rank(s): return sorted(s,key=lambda k:(-s[k],k))
def long_only(s,k,method='score',allow_cash=True):
    selected=rank(s)[:k]
    positive={i:max(Q(s[i]),0) for i in selected}
    if not selected or (method=='score' and sum(positive.values())==0):
        return dict(status='CASH' if allow_cash else 'INFEASIBLE',reason='NO_POSITIVE_SCORE' if selected else 'EMPTY_INTERSECTION',weights={},cash=Q(1))
    w={i:Q(1,len(selected)) if method=='equal' else positive[i]/sum(positive.values()) for i in selected}
    return dict(status='SUCCEEDED',weights=w,cash=1-sum(w.values()))
def budgets(g,n):
    if g<abs(n) or g<0: raise ValueError('infeasible budgets')
    return (g+n)/2,(g-n)/2
def exposures(w): return sum(abs(x) for x in w),sum(w)
def quantize(w,p,lot,E):
    raw=[wi*E/pi for wi,pi in zip(w,p)]
    out=[(1 if qi>=0 else -1)*(abs(qi)//li)*li for qi,li in zip(raw,lot)]
    return raw,out
def funding(q,p,E,nonshort=0,reserve=0):
    notion=[qi*pi for qi,pi in zip(q,p)]; short=sum(max(-v,0) for v in notion)
    cash=E-sum(notion); restricted=nonshort+short; margin=short
    return dict(cash=cash,restricted=restricted,margin=margin,free=cash-restricted-margin-reserve)
def turnover(q,q0,p,E): return sum(abs((qi-oi)*pi) for qi,oi,pi in zip(q,q0,p))/E
def sale(q0,qt,sellable,borrow,permission=True):
    delta=qt-q0; sell=max(-delta,0); longsale=min(sell,max(q0,0)); short=max(-qt,0)
    return dict(delta=delta,long_sale=longsale,target_short=short,new_short=max(short-max(-q0,0),0),qualified=longsale<=sellable and (short==0 or permission and short<=borrow))
tol=Q(1,10**12)
def upper(v,cap): return v<=cap+tol
def lower(v,floor): return v>=floor-tol

s={'A':Q(3),'B':Q(1)}
C('G01',s,'max(S,0)/sum(max(S,0))',long_only(s,2)['weights'],{'A':Q(3,4),'B':Q(1,4)})
f=[{'A':2,'B':4},{'A':4,'B':2}]; s=combined(f,[3,1])
C('G02',dict(factors=f,a=[3,1]),'S=sum(a*s)/sum(abs(a)); then positive score normalization',(s,long_only(s,2)['weights']),({'A':Q(5,2),'B':Q(7,2)},{'A':Q(5,12),'B':Q(7,12)}))
s={'C':Q(2),'B':Q(2),'A':Q(2)}; selected=rank(s)[:2]
C('G03',dict(scores=s,K=2),'sort(-score, full_id); equal; ties iff repeated selected cutoff score',(selected,list(long_only(s,2,'equal')['weights'].values()),len(set(s.values()))<len(s)),(['A','B'],[Q(1,2),Q(1,2)],True))
s={'A':Q(-1),'B':Q(-2)}
C('G04',dict(scores=s,K=2),'sum positive selected scores is zero; cash policy decides status',[(long_only(s,2,allow_cash=a)['status'],long_only(s,2,allow_cash=a)['cash'],long_only(s,2,allow_cash=a)['reason']) for a in [True,False]],[('CASH',Q(1),'NO_POSITIVE_SCORE'),('INFEASIBLE',Q(1),'NO_POSITIVE_SCORE')])
C('G05',s,'equal=1/n independent of negative score magnitude',long_only(s,2,'equal')['weights'],{'A':Q(1,2),'B':Q(1,2)})
f=[{'A':8,'B':2},{'B':4,'C':6}]; s=combined(f,[1,1])
C('G06',dict(factors=f,a=[1,1]),'intersect keys before weighted sum; drop union minus intersection',(s,long_only(s,2)['weights'],sorted(set.union(*(set(x) for x in f))-set(s))),({'B':Q(3)},{'B':Q(1)},['A','C']))
for name,g,n,expected in [('G07',Q(1),Q(0),(Q(1,2),-Q(1,2),Q(1),Q(0))),('G08',Q(6,5),Q(1,5),(Q(7,10),-Q(1,2),Q(6,5),Q(1,5)))]:
    l,h=budgets(g,n); gross,net=exposures([l,-h]); C(name,dict(G=g,N=n),'L=(G+N)/2; H=(G-N)/2; gross=L+H; net=L-H',(l,-h,gross,net),expected)
vals=list(map(Q,[3,1,-1,-3])); mean=sum(vals)/len(vals); centered=[v-mean for v in vals]; l,h=budgets(Q(1),Q(0))
w=[l*v/sum(x for x in centered if x>0) if v>0 else -h*abs(v)/sum(abs(x) for x in centered if x<0) if v<0 else Q(0) for v in centered]
C('G09',dict(scores=vals,G=1,N=0),'cross-sectional mean; each centered sign leg normalized separately',(mean,w),(Q(0),[Q(3,8),Q(1,8),-Q(1,8),-Q(3,8)]))
E=Q(1000); prices=list(map(Q,[30,40])); lots=[10,10]
raw,q=quantize([Q(1,2)]*2,prices,lots,E); w=[qi*pi/E for qi,pi in zip(q,prices)]
C('G10',dict(E=E,weights=[Q(1,2)]*2,prices=prices,lots=lots),'q*=wE/p; sign*floor(abs(q*)/lot)*lot; w=q*p/E; cash=E-sum(q*p)',(raw,q,w,funding(q,prices,E)['cash']),([Q(50,3),Q(25,2)],[10,10],[Q(3,10),Q(2,5)],Q(300)))
raw,q=quantize([Q(1,2),-Q(1,2)],prices,lots,E); w=[qi*pi/E for qi,pi in zip(q,prices)]; gross,net=exposures(w)
C('G11',dict(E=E,weights=[Q(1,2),-Q(1,2)],prices=prices,lots=lots),'signed toward-zero quantization; cash; 100% short restriction plus 100% additional margin',(q,net,gross,funding(q,prices,E)),([10,-10],-Q(1,10),Q(7,10),dict(cash=Q(1100),restricted=Q(400),margin=Q(400),free=Q(300))))
C('G12',dict(weight=Q(3,4),cap=Q(7,10)),'overage=abs(w)-cap; compare fixed tolerance',(Q(3,4)-Q(7,10),upper(Q(3,4),Q(7,10))),(Q(1,20),False))
t=sum(abs(x-y) for x,y in zip([Q(3,4),Q(1,4)],[Q(1,2)]*2))
C('G13',dict(current=[Q(1,2)]*2,target=[Q(3,4),Q(1,4)],cap=Q(2,5)),'sum absolute target-current weights; half diagnostic',(t,t/2,upper(t,Q(2,5))),(Q(1,2),Q(1,4),False))
C('G14',dict(continuous_net=Q(0),rounded_net=net,lower=0),'check lower independently before and after rounding',(lower(Q(0),Q(0)),lower(net,Q(0))),(True,False))
w=[Q(3,4),-Q(1,4)]; g,n=exposures(w)
C('G15',dict(same_sector_weights=w,gross_cap=Q(9,10)),'sector_net=sum(w); sector_gross=sum(abs(w))',(n,g,upper(g,Q(9,10))),(Q(1,2),Q(1),False))
w=[Q(3,4),Q(1,4)]; b=[Q(6,5),Q(4,5)]; beta=sum(wi*bi for wi,bi in zip(w,b))
C('G16',dict(weights=w,beta=b,upper=1),'signed beta=sum(w*beta); missing beta deliberately NOT evaluated',(beta,upper(beta,Q(1))),(Q(11,10),False))
C('G17',dict(current=10,target=-5,sellable=10,borrow_total=5,short_permission=True),'delta; sell_long=min(max(-delta,0),max(q0,0)); target_short=max(-qt,0)',[sale(10,-5,10,5),sale(10,-5,9,5)['qualified'],sale(10,-5,10,4)['qualified']], [dict(delta=-15,long_sale=10,target_short=5,new_short=5,qualified=True),False,False])
C('G18',dict(current=-4,target=-6,borrow_total=5),'new=max(target_short-current_short,0); test TOTAL target against borrow',sale(-4,-6,0,5),dict(delta=-2,long_sale=0,target_short=6,new_short=2,qualified=False))
C('G19',dict(E=1000,notionals=[[500,-500],[700,-500]]),'cash=E-netNotional; required=short; margin=short; free=cash-2*short',[funding(list(map(Q,ns)),[Q(1),Q(1)],E) for ns in [[500,-500],[700,-500]]],[dict(cash=Q(1000),restricted=Q(500),margin=Q(500),free=Q(0)),dict(cash=Q(800),restricted=Q(500),margin=Q(500),free=Q(-200))])
cap=Q(3,4); vv=[cap,cap+Q(5,10**13),cap+Q(2,10**12)]
C('G20',dict(cap=cap,tol=tol,values=vv),'value<=cap+tol; quantities exact',([upper(v,cap) for v in vv],Q(5)+tol/2<=Q(5)),([True,True,False],False))

# Reviewer counterexamples: full quantities/cash account, not future product execution.
E=Q(1000); p=[Q(10),Q(10)]; lot=[10,10]; q0=[15,0]; cash0=Q(850)
w=list(long_only({'A':Q(1),'B':Q(9)},2)['weights'].values())
# dict follows ranking B,A: explicitly restore A,B security order.
wm=long_only({'A':Q(1),'B':Q(9)},2)['weights']; w=[wm['A'],wm['B']]
raw,qt=quantize(w,p,lot,E); delta=[t-c for t,c in zip(qt,q0)]; fund=funding(qt,p,E)
X('X01-target-lot-does-not-protect-delta',dict(E=E,current_cash=cash0,current_qty=q0,prices=p,lot=lot,scores={'A':1,'B':9},sellable_A=15),'plan quantizes target, subtracts current; only full close odd-lot is excepted',dict(equity=cash0+sum(c*pi for c,pi in zip(q0,p)),target=qt,delta=delta,target_aligned=all(t%l==0 for t,l in zip(qt,lot)),delta_A_aligned=delta[0]%lot[0]==0,full_close_A=qt[0]==0,turnover=turnover(qt,q0,p,E),funding=fund),dict(equity=Q(1000),target=[10,90],delta=[-5,90],target_aligned=True,delta_A_aligned=False,full_close_A=False,turnover=Q(19,20),funding=dict(cash=Q(0),restricted=Q(0),margin=Q(0),free=Q(0))))
X('X02-no-trade-odd-holding-conflict',dict(E=1000,p=10,current=15,weight=Q(3,20),lot=10,tradable=False),'unchanged q=15 would have delta=0 but target rounding creates sell5',(quantize([Q(3,20)],[Q(10)],[10],Q(1000))[1][0],15%10==0),(10,False))
raw,qt=quantize([Q(1,2),-Q(1,2)],[Q(60),Q(50)],[10,10],Q(1000)); wp=[qt[0]*Q(60,1000),qt[1]*Q(50,1000)]
X('X03-rounding-increases-absolute-Beta-sector-net',dict(E=1000,w=[Q(1,2),-Q(1,2)],p=[60,50],lot=[10,10],beta=[1,1],same_sector=True,beta_interval=[-Q(1,10),Q(1,10)]),'toward-zero cancels an offsetting long leg: net and Beta 0 -> -1/2',(qt,wp,abs(sum(wp)),exposures(wp)[0],funding(qt,[Q(60),Q(50)],Q(1000))['free']),([0,-10],[Q(0),-Q(1,2)],Q(1,2),Q(1,2),Q(500)))
E=Q(1000); p=[Q(60),Q(50)]; q0=[10,0]; raw,qt=quantize([Q(1,2),Q(1,2)],p,[10,10],E)
pre=turnover(raw,q0,p,E); post=turnover(qt,q0,p,E)
X('X04-rounding-increases-turnover',dict(E=E,current_cash=400,current_qty=q0,p=p,lot=[10,10],target_weights=[Q(1,2),Q(1,2)],turnover_cap=Q(4,5)),'sum abs(delta*p)/E before vs after target rounding',(pre,post,upper(pre,Q(4,5)),upper(post,Q(4,5)),funding(qt,p,E)['free']),(Q(3,5),Q(11,10),True,False,Q(500)))
X('X05-funding-implied-gross-ceiling',dict(E=1000,long=700,short=500,nonshort=0,reserve=0),'free=E-(long+short)-nonshort-reserve independent of signed net',Q(1000)-(Q(700)+Q(500)),Q(-200))
with localcontext() as ctx:
    ctx.prec=34; ctx.rounding=ROUND_HALF_EVEN
    capD=Decimal('0.75'); tolD=Decimal('0.000000000001')
    X('X06-decimal-tolerance-crosscheck',dict(cap=capD,tol=tolD,precision=34,rounding='ROUND_HALF_EVEN'),'Decimal independent numeric representation vs exact rational boundary',[v<=capD+tolD for v in [capD,capD+Decimal('0.0000000000005'),capD+Decimal('0.000000000002')]],[True,True,False])
result=dict(actual_executor='GPT Work primary reviewer',fixed_sha='e40ddd0009cc30664c3a0fe0b74c4a497a541d77',independence='Reviewer-authored standard-library Fraction/Decimal only. No AQRP/developer script imports. Arithmetic consistency is not implementation or formal approval verification.',golden_groups=len(cases),golden_result='20/20 arithmetic groups match documented candidates',golden=cases,reviewer_edges=edges,not_verified=['Missing exposure/permission/PIT/approval/cancellation/ledger behavior requires future implementation tests; a normative design statement is not a passed runtime test.','Golden groups are arithmetic slices, not complete executable account fixtures. Full immutable fixtures remain an implementation prerequisite.'])
(O/'independent-math-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(actual_executor=result['actual_executor'],golden_groups=len(cases),reviewer_edges=len(edges),all_assertions=True,AQRP_imports=False,implementation_tests=False),indent=2))
