"""Reviewer independent pre-implementation answers; integer/Fraction arithmetic.
No AQRP import, no UI/runtime/product test claim; expected values never from developer checker.
"""
from pathlib import Path
from fractions import Fraction as Q
import json,html,hashlib,importlib.util,itertools
O=Path(__file__).parent;P=Path('E:/WORK/AQRP-audits/p6-f7a1a68/src/docs/audits/phase-6');FIX='f7a1a68c5f747090f8c8a0e934f2fea859aec998'
def decimal(q):
 q=Q(q);n,d=abs(q.numerator),q.denominator;k=0
 while d>1:
  if d%2==0:d//=2
  elif d%5==0:d//=5
  else:raise ValueError('NONTERMINATING')
  k+=1
 while (n*10**k)%q.denominator:k+=1
 s=str(n*10**k//q.denominator).zfill(k+1);s=(s[:-k]+'.'+s[-k:]) if k else s;s=s.rstrip('0').rstrip('.') if '.' in s else s
 return ('-' if q<0 else '')+s
def rounded(v,places,commas=False):
 q=Q(v)*10**places;n,r=divmod(abs(q.numerator),q.denominator)
 if 2*r>q.denominator or (2*r==q.denominator and n%2):n+=1
 integer,frac=divmod(n,10**places);out=(format(integer,',') if commas else str(integer))+('.'+str(frac).zfill(places) if places else '')
 return ('-' if q<0 and n else '')+out
def strict_load(raw):
 def pairs(xs):
  d={}
  for k,v in xs:
   if k in d:raise ValueError('DUPLICATE_KEY')
   d[k]=v
  return d
 return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda s:(_ for _ in ()).throw(ValueError('NONFINITE')))
def exact(a,b):
 if type(a)!=type(b):return False
 if isinstance(a,dict):return a.keys()==b.keys() and all(exact(a[k],b[k]) for k in a)
 if isinstance(a,list):return len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
 return a==b
def compute(kind,x):
 if kind=='weight':return decimal(Q(x['percent'])/100)
 if kind=='money':return rounded(x['value'],2,True)
 if kind=='quantity':return str(int(x['value']))
 if kind=='small':return decimal(Q(x['value']))
 if kind=='ic_display':return rounded(x['value'],4)
 if kind=='nullable':return dict(text='N/A' if x['value'] is None else str(x['value']),reason=x['reason'])
 if kind=='percent_display':return rounded(Q(x['value'])*100,4)+'%'
 if kind=='canonical':return json.dumps(strict_load(x['raw']),ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
 if kind in ['nullable_equal','array_order']:return exact(x['left'],x['right'])
 if kind=='status_counts':return dict(total=len(x['rows']),succeeded=len([r for r in x['rows'] if r['status']=='SUCCEEDED' and r['verified'] is True]),integrity_errors=len([r for r in x['rows'] if r['verified'] is False]))
 if kind=='financial_view':return x['verified_balance'] if x['known'] is True and x['manifest_valid'] is True and exact(x['reported_balance'],x['verified_balance']) else None
 if kind=='idempotency':
  groups={};conflicts=0
  for k,h in x['calls']:
   if k not in groups:groups[k]=h
   elif groups[k]!=h:conflicts+=1
  return dict(tasks=len(groups),conflicts=conflicts)
 if kind=='lifecycle':
  s='QUEUED';table={('QUEUED','START'):'RUNNING',('QUEUED','CANCEL_REQUEST'):'CANCELLED',('RUNNING','CANCEL_REQUEST'):'CANCEL_REQUESTED',('RUNNING','SUCCESS'):'SUCCEEDED',('CANCEL_REQUESTED','SUCCESS'):'SUCCEEDED',('RUNNING','FINANCIAL_UNKNOWN'):'FAILED',('CANCEL_REQUESTED','FINANCIAL_UNKNOWN'):'FAILED',('CANCEL_REQUESTED','SAFE_CANCEL'):'CANCELLED'}
  for e in x['trace']:
   if s in {'SUCCEEDED','FAILED','CANCELLED'}:continue
   s=table[(s,e)]
  return s
 if kind=='artifact_membership':return sum(v==x['name'] for v in x['manifest'])==1
 if kind=='defaults_rollback':return dict(old_fee=x['history'][0]['fee'],active_fee=x['history'][x['rollback_to']]['fee'],revisions=len(x['history'])+1)
 if kind=='formal_gate':return 'APPROVAL_REQUIRED' if x['financial_approval']=='NONE' else 'REQUIRES_REAL_APPROVAL_VALIDATION'
 if kind=='family_trials':return x['initial']+len({key for key,status in x['attempts']})
 if kind=='escape':return html.escape(x['value'])
 if kind=='parent_identity':return x['expected_parent']==x['actual_parent'] or x['mapping_proven'] is True
 if kind=='rerun':return x['explicit_submits']
 raise ValueError(kind)
cases=json.loads((P/'GOLDEN_CANDIDATES.json').read_bytes())['cases'];answers=[]
for c in cases:
 got=compute(c['kind'],c['inputs']);answers.append(dict(id=c['id'],inputs=c['inputs'],actual=got,expected=c['expected'],passed=exact(got,c['expected']),tolerance=c['tolerance']))
assert len(answers)==32 and all(a['passed'] for a in answers)
extensions=[]
for p in ['0','100','-12.50','0.123456789012345678901234567890123456789','999999999999999999999999999999.99']:
 v=compute('weight',dict(percent=p));assert Q(v)==Q(p)/100;extensions.append(dict(kind='weight',input=p,exact=v,result='PASS'))
for n in ['1009.005','1009.015','-1009.005','-1009.015','999999999999999999999999999999.995','0.0000000000000000000000000001']:
 extensions.append(dict(kind='money',input=n,exact=rounded(n,2,True),result='PASS'))
for a,b in [(None,0),(None,False),(0,False),('',None),(0,0),(False,False)]:extensions.append(dict(kind='typed_equal',left=a,right=b,result=exact(a,b)))
for raw in ['{"a":1,"a":2}','{"v":NaN}','{"v":Infinity}']:
 try:strict_load(raw);result='ACCEPTED'
 except ValueError as e:result=str(e)
 assert result!='ACCEPTED';extensions.append(dict(kind='strict_json',input=raw,result=result))
# Design trace: existing prose recovers a terminal core run into a Task terminal,
# but does not specify an all-required-slots barrier for multi-stage pipelines.
recovery=[]
for present in [('P3',),('P3','P4'),('P3','P4','P5')]:
 observed={s:'SUCCEEDED' for s in present};required=['P3','P4','P5'];literal='SUCCEEDED' if observed else 'RECOVERY_REQUIRED';safe='SUCCEEDED' if set(required)<=observed.keys() else 'NOT_SUCCEEDED'
 recovery.append(dict(required=required,verified_terminal_children=observed,task_mapping_lost=True,document_literal_core_terminal_promotion=literal,necessary_all_required_slots=safe,gap=literal=='SUCCEEDED' and safe!='SUCCEEDED',scope='Document design model only; no P6 implementation exists'))
# Observe the developer design helper against independently computed long-decimal answers.
spec=importlib.util.spec_from_file_location('candidate_design_only',P/'reference_check.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);oracle=[]
for kind,x in [('weight',{'percent':'0.123456789012345678901234567890123456789'}),('money',{'value':'999999999999999999999999999999.995'})]:
 expected=compute(kind,x)
 try:got=module.reference(dict(kind=kind,inputs=x));error=None
 except Exception as e:got=None;error=type(e).__name__
 oracle.append(dict(kind=kind,input=x,independent_expected=expected,developer_reference_actual=got,error=error,match=got==expected))
out=dict(fixed_sha=FIX,executor='GPT Work supplemental reviewer',scope='Independent design arithmetic and contract counterexamples only; NOT P6 products/AppTest/browser tests',golden_groups=32,golden_passed=32,golden_answers=answers,extensions=extensions,multistage_recovery_counterexamples=recovery,developer_reference_boundary_observations=oracle)
(O/'INDEPENDENT_DESIGN_RESULTS.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(golden_groups=32,golden_passed=32,extension_records=len(extensions),multistage_design_gaps=sum(r['gap'] for r in recovery),oracle_boundary_mismatches=sum(not r['match'] for r in oracle))))
