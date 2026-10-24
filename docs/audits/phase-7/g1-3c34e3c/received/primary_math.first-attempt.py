"""Primary GPT Work design oracle. Stdlib only; never imports AQRP or developer solvers."""
import json, hashlib, sys, platform, datetime
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal as D, getcontext
getcontext().prec=100
O=Path(__file__).parent
P=Path('E:/WORK/AQRP-audits/p7-3c34e3c/src/docs/audits/phase-7')
count=0
def check(v, name):
 global count
 count+=1
 if not v: raise AssertionError(name)
def dec(x):
 f=F(x); return D(f.numerator)/D(f.denominator)
def eq(a,b,name): check(abs(D(a)-D(b)) <= D('1e-12')+D('1e-10')*abs(D(b)),name)
def dot(x,y): return sum(a*b for a,b in zip(x,y))
def ranks(x): return [D(sum(t<v for t in x))+D(sum(t==v for t in x)+1)/2 for v in x]
def corr(x,y):
 a=[z-sum(x)/len(x) for z in x]; b=[z-sum(y)/len(y) for z in y]
 return dot(a,b)/(dot(a,a)*dot(b,b)).sqrt()
def price(a,i): return 100+3*a+((i*i+7*a*i)%(5*a+17))
def quant(x,q):
 s=sorted(x); at=q*(len(x)-1); k=at.numerator//at.denominator
 return s[k] if k==len(x)-1 else s[k]+(s[k+1]-s[k])*(at-k)
# Project using orthogonal columns, without normal equations or Gauss-Jordan.
cols=[[D(1)]*6,[D(a%2==0) for a in range(1,7)], [D(1000+113*a*a).ln() for a in range(1,7)]]
Q=[]; triangular=[]
for col in cols:
 v=col[:]; co=[]
 for q in Q:
  z=dot(q,v); co.append(z); v=[x-z*y for x,y in zip(v,q)]
 norm=dot(v,v).sqrt(); co.append(norm); Q.append([x/norm for x in v]); triangular.append(co)
main=json.loads((P/'MAIN_PIPELINE_CANDIDATES.json').read_bytes())
computed=[]; ics={f:{k:[] for k in ['pearson','spearman']} for f in ['momentum','reversal']}
for i,s in zip(range(2,21),main['sections']):
 raw=[F(price(a,i),price(a,i-2))-1 for a in range(1,7)]
 labels=[F(price(a,i+2),price(a,i+1))-1 for a in range(1,7)]
 check(s['decision_index']==i and s['label_entry_index']==i+1 and s['label_exit_index']==i+2,'time boundaries')
 check([F(x) for x in s['raw_momentum']]==raw,'raw fractions')
 check([F(x) for x in s['raw_next_open_label']]==labels,'next open labels')
 bounds=[quant(raw,F(1,20)),quant(raw,F(19,20))]
 clean=[dec(max(bounds[0],min(bounds[1],x))) for x in raw]
 mu=sum(clean)/6; sd=(sum((x-mu)**2 for x in clean)/5).sqrt(); z=[(x-mu)/sd for x in clean]
 projection=[dot(q,z) for q in Q]
 residual=[z[k]-sum(projection[j]*Q[j][k] for j in range(3)) for k in range(6)]
 beta=[D(0)]*3
 for j in range(2,-1,-1): beta[j]=(projection[j]-sum(triangular[k][j]*beta[k] for k in range(j+1,3)))/triangular[j][j]
 for field,values in [('clean_bounds',list(map(dec,bounds))),('momentum_clean',clean),('momentum_standardized',z),('OLS_beta',beta),('momentum_final',residual),('reversal_final',[-v for v in residual])]:
  for n,(a,b) in enumerate(zip(values,s[field])): eq(a,b,f'{i}/{field}/{n}')
 for col in cols: check(abs(dot(col,residual))<D('1e-90'),'orthogonality')
 tops={}
 for factor,vector in [('momentum',residual),('reversal',[-v for v in residual])]:
  top=max(range(6),key=lambda n:vector[n]); tops[factor]=f'SYN_A:{top+1:03}'
  check(tops[factor]==s['expected_top1'][factor],'top1')
  r=ranks(vector); ld=list(map(dec,labels)); g=[min(2,int((x-1)*3/6)) for x in r]
  means=[sum(v for v,k in zip(ld,g) if k==j)/g.count(j) for j in range(3)]
  st=s['statistics'][factor]; ic=corr(vector,ld); ric=corr(r,ranks(ld))
  eq(ic,st['pearson_ic'],'Pearson'); eq(ric,st['spearman_rank_ic'],'ties-aware Spearman')
  for a,b in zip(means,st['group_mean_returns']): eq(a,b,'group mean')
  eq(means[2]-means[0],st['top_minus_bottom'],'spread')
  check(st['group_counts']==[g.count(j) for j in range(3)] and st['n']==6,'counts')
  ics[factor]['pearson'].append(ic); ics[factor]['spearman'].append(ric)
 computed.append({'index':i,'session':s['session'],'top':tops,'residual':[str(x) for x in residual]})
for fac,stats in ics.items():
 for typ,values in stats.items():
  st=main['IC_summaries'][fac][typ]; mu=sum(values)/19; sd=(sum((x-mu)**2 for x in values)/18).sqrt()
  for k,v in [('mean',mu),('sample_std_ddof1',sd),('unannualized_icir',mu/sd),('positive_fraction',D(sum(x>0 for x in values))/19)]: eq(v,st[k],fac+typ+k)
  check(st['n']==19,'summary n')
# All numeric finite Golden groups. Other groups are contract/state proposals reviewed statically.
gold=json.loads((P/'GOLDEN_CANDIDATES.json').read_bytes()); cases={x['id']:x for x in gold['cases']}
def goldcheck(n,actual):
 expected=cases[f'P7-G{n:02}']['expected']
 def norm(x):
  if type(x) is dict:return {k:norm(v) for k,v in x.items()}
  if type(x) is list:return [norm(v) for v in x]
  if type(x) is str:
   try:return F(x)
   except ValueError:return x
  return x
 check(norm(actual)==norm(expected),'Golden '+str(n))
goldcheck(1,{'i2':[price(a,2) for a in range(1,7)],'i4':[price(a,4) for a in range(1,7)]})
raw=[F(price(a,4),price(a,2))-1 for a in range(1,7)]
goldcheck(2,raw); goldcheck(3,[-x for x in raw]); order=sorted(range(6),key=lambda a:raw[a],reverse=True)
goldcheck(4,[f'SYN_A:{a+1:03}' for a in order]); goldcheck(5,{'momentum':f'SYN_A:{order[0]+1:03}','reversal':f'SYN_A:{order[-1]+1:03}'})
q=(F(1000)-10)//100; notional=q*F('100.1'); fee=max(F(1),notional/1000); fee=F(round(fee*100),100)
cash=F(1000)-notional-fee; marked=q*100; equity=cash+marked
goldcheck(6,q);goldcheck(7,{'actual_fill_price':F('100.1'),'notional':notional,'commission':fee,'slippage_cost':q/10,'total_equity_drag':1000-equity})
goldcheck(8,cash);goldcheck(9,marked);goldcheck(10,equity);goldcheck(11,equity/1000-1)
goldcheck(12,{'different_selected_security':order[0]!=order[-1],'same_cash':cash,'same_equity':equity})
goldcheck(16,{'old_momentum':F(110,100)-1,'new_momentum':F(120,100)-1,'changed':True})
goldcheck(22,4*2+2+2);goldcheck(23,{'allowed':11+1<=12,'used_after':12})
goldcheck(31,None==0);goldcheck(32,{'equal':int('9007199254740993')==int('9007199254740992'),'raw_roundtrip':str(2**53+1)})
check(ranks([D(1),D(1),D(3)])==[D('1.5'),D('1.5'),D(3)],'tie control')
report={'executor':'Primary GPT Work reviewer; independently authored stdlib oracle','fixed_sha':'3c34e3ca75c9799307b8a98b34f045b40988bbca','not_product_tests':True,'checks':count,'sections':computed,'inputs_sha256':{f:hashlib.sha256((P/f).read_bytes()).hexdigest() for f in ['MAIN_PIPELINE_CANDIDATES.json','GOLDEN_CANDIDATES.json']},'golden_math_groups':[1,2,3,4,5,6,7,8,9,10,11,12,16,22,23,31,32],'remaining_golden':'15 state/interface proposals reviewed against existing contracts; no claim of future P7 execution','environment':{'python':sys.version,'executable':sys.executable,'platform':platform.platform(),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}}
(O/'PRIMARY_MATH.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'primary_math_checks':count,'sections':19,'golden_math_groups':17}))
