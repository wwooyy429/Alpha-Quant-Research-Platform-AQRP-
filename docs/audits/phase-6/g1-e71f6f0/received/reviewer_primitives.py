"""Reviewer independent pre-implementation answers; integer/Fraction arithmetic.
No AQRP import, no UI/runtime/product test claim; expected values never from developer checker.
"""
from pathlib import Path
from fractions import Fraction as Q
import json,html,hashlib,importlib.util,itertools
O=Path(__file__).parent;P=Path('E:/WORK/AQRP-audits/p6-e71f6f0/src/docs/audits/phase-6');FIX='e71f6f090b102e4abfd70a5999e495f49546a1b5'
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
