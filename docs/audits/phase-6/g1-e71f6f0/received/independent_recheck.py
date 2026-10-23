"""GPT Work independent design review. No AQRP imports or runtime/UI execution.
Expected numeric values use Fraction and Python's exact Fraction round; completion and
ownership use separate declarative requirements. Developer helpers are called only as SUT.
"""
from pathlib import Path
from fractions import Fraction as F
from decimal import localcontext
import decimal,copy,hashlib,importlib.util,itertools,json,re,random
from reviewer_primitives import compute,exact
O=Path(__file__).parent;P=Path('E:/WORK/AQRP-audits/p6-e71f6f0/src/docs/audits/phase-6')
FIX='e71f6f090b102e4abfd70a5999e495f49546a1b5'
H=lambda b:hashlib.sha256(b).hexdigest()
def save(name,x):(O/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
class Refusal(ValueError):pass
def checked(s,integer=False):
 if type(s) is not str:raise Refusal('REFERENCE_NUMERIC_TYPE')
 if len(s)>4098:raise Refusal('REFERENCE_NUMERIC_RANGE')
 if re.fullmatch(r'[+-]?(?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+)',s,flags=re.ASCII) is None:raise Refusal('REFERENCE_NUMERIC_SYNTAX')
 if sum('0'<=c<='9' for c in s)>4096:raise Refusal('REFERENCE_NUMERIC_RANGE')
 if integer and '.' in s:raise Refusal('REFERENCE_INTEGER_REQUIRED')
 return F(s)
def finite(q):
 sign='-' if q<0 else '';q=abs(q);d=q.denominator;a=b=0
 while d%2==0:d//=2;a+=1
 while d%5==0:d//=5;b+=1
 assert d==1
 places=max(a,b);v=q.numerator*(10**places//q.denominator)
 s=str(v).zfill(places+1)
 if places:s=(s[:-places]+'.'+s[-places:]).rstrip('0').rstrip('.')
 return sign+s
def view(q,places,group=False):
 units=round(q*10**places) # Fraction.__round__, exact ties-to-even, no Decimal.
 whole,fraction=divmod(abs(units),10**places)
 return ('-' if units<0 else '')+(format(whole,',') if group else str(whole))+'.'+str(fraction).zfill(places)
numeric_kinds={'weight','money','quantity','small','ic_display','percent_display'}
def number(kind,x):
 s=x['percent'] if kind=='weight' else x['value']
 q=checked(s,kind=='quantity')
 if kind=='weight':return finite(q/100)
 if kind=='small':return finite(q)
 if kind=='quantity':return str(q.numerator)
 return view(q*(100 if kind=='percent_display' else 1),2 if kind=='money' else 4,kind=='money')+('%' if kind=='percent_display' else '')
def completion(x):
 result=lambda a,b:dict(status=a,reason=b)
 failed=lambda r:result('FAILED',r)
 pending=lambda r:result('RUNNING',r)
 # Diagnostic precedence is checked for the supplied unambiguous cases, not general error priority.
 if x.get('financial_unknown'):return failed('COMMITTED_STATE_UNVERIFIED')
 if any(x.get(k) for k in ('unknown_side_effects','partial_publication','binding_conflict','artifact_corruption')):return failed('RECOVERY_REQUIRED')
 statuses=x['slot_statuses'];values=set(statuses.values())
 if 'FAILED' in values:return failed('REQUIRED_CHILD_FAILED')
 if 'REJECTED' in values:return failed('REQUIRED_STAGE_REJECTED')
 receipt=x.get('completion_verified') and x.get('terminal_commit_verified')
 if x.get('claimed_success') and not receipt:return failed('INTEGRITY_ERROR')
 if x.get('cancel_intent') and not x.get('success_committed_first'):
  return result('CANCELLED','SAFE_CANCELLATION_VERIFIED') if x.get('quiescent') and x.get('safe_cancel_verified') else pending('CANCEL_REQUESTED')
 kind=x['kind']
 templates={'research':{'R','RV'},'engineering_pipeline':{'R','PLAN','B','BV'},'replay':{'SV','E','CV'}}
 if kind not in templates:return failed('TASK_KIND_NOT_APPROVED')
 required=set(templates[kind])
 if kind=='engineering_pipeline':
  if not x.get('resolved_plan_frozen'):return failed('INTEGRITY_ERROR') if x.get('claimed_success') else pending('PLAN_NOT_FROZEN')
  if x['decisions']==0:return failed('NO_REQUIRED_DECISIONS')
 if kind=='replay' and x.get('profile') not in {'P5_NUMERICAL','PUBLISHED_REF_PROJECTION'}:return failed('REPLAY_PROFILE_NOT_APPROVED')
 if kind=='engineering_pipeline' or (kind=='replay' and x['profile']=='P5_NUMERICAL'):required.update('P:'+str(i) for i in range(x['decisions']))
 registry=x['registry_slots']
 if len(registry)!=len(set(registry)) or set(registry)!=required or not set(statuses)<=required:return failed('SLOT_SET_MISMATCH')
 done={slot for slot,s in statuses.items() if s=='VERIFIED_SUCCESS'}
 if statuses.get('B')=='VERIFIED_SUCCESS' and not {k for k in required if k.startswith('P:')}<=done:return failed('RECOVERY_REQUIRED')
 if x.get('claimed_success') and (done!=required or not receipt):return failed('INTEGRITY_ERROR')
 if done!=required:return pending('REQUIRED_SLOTS_PENDING')
 if not (x.get('required_artifacts_verified') and x.get('all_bindings_verified')):return failed('RECOVERY_REQUIRED')
 if kind=='replay' and not x.get('comparison_verified'):return failed('REPLAY_COMPARISON_FAILED')
 if not x.get('dispatch_closed'):return pending('DISPATCH_NOT_CLOSED')
 if not receipt:return pending('GLOBAL_COMPLETION_PENDING')
 # For current valid model premises dispatch closed + all children verified imply quiescence.
 assert x.get('quiescent') is True
 return result('SUCCEEDED','ALL_REQUIRED_EVIDENCE_COMMITTED')
def binding(x):
 if x['has_context'] is False:return dict(action='LEGACY_UNCHANGED',task_terminal=False)
 ok=all(x[k] is True for k in ['record_preexists','initial_binding_valid','unique_active_claim','root_enumeration_complete','adapted_bytes_bound_before_call'])
 ok=ok and exact(x['actual'],x['expected']) and x['active_epoch']==x['handle_epoch']
 ok=ok and x['actual']['physical_ledger_root']==x['parent_root'].rstrip('/')+'/portfolio-runs'
 start=x['core_start_seq'];end=x['core_terminal_seq']
 if start is not None:ok=ok and x['registration_seq']<start
 if not ok:action='RECOVERY_REQUIRED'
 elif end is not None:
  action='REUSE_VERIFIED_SLOT' if start is not None and end>start and x['terminal_verified'] else 'RECOVERY_REQUIRED'
 elif start is None and x['slot_state']=='BOUND' and x['no_core_side_effects_proven']:action='CALL_ONCE'
 else:action='RECOVERY_REQUIRED'
 return dict(action=action,task_terminal=False)
def own(c):
 k=c['kind'];x=c['inputs']
 if k=='task_completion':return completion(x)
 if k=='nested_binding':return binding(x)
 if k=='numeric_rejection':
  try:number(x['numeric_kind'],x['fields']);err=None
  except Refusal as e:err=str(e)
  return dict(error=err,raw_retained=True) # Design obligation, not implemented persistence.
 return number(k,x) if k in numeric_kinds else compute(k,x)
original=json.loads((P/'GOLDEN_CANDIDATES.json').read_bytes())['cases']
supplemental=json.loads((P/'SUPPLEMENTAL_CANDIDATES.json').read_bytes())['cases']
records=[]
for origin,cases in [('original',original),('supplemental',supplemental)]:
 for c in cases:
  got=own(c);passed=exact(got,c['expected'])
  records.append(dict(id=c['id'],origin=origin,kind=c['kind'],inputs=c['inputs'],expected=c['expected'],independent=got,passed=passed,tolerance=c['tolerance']))
save('INDEPENDENT_127_ANSWERS.json',dict(fixed_sha=FIX,scope='Design only; original lifecycle is single-slot, not whole-Task',records=records,passed=sum(r['passed'] for r in records)))
assert all(r['passed'] for r in records)
# Independent expected values are complete before importing either candidate helper.
def load(name,file):
 spec=importlib.util.spec_from_file_location(name,file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
candidate=load('candidate_only_after_expectations',P/'reference_check.py')
revised=load('candidate_finite_model',P/'revision_reference.py')
observations=[]
for c,r in zip(original+supplemental,records):
 actual=revised.evaluate(c) if r['origin']=='supplemental' else candidate.reference(c)
 observations.append(dict(id=c['id'],actual=actual,independent=r['independent'],passed=exact(actual,r['independent'])))
assert all(r['passed'] for r in observations)
save('CANDIDATE_HELPER_OBSERVATIONS.json',dict(scope='Candidate helpers are SUT, never expected-value generators',records=observations))
# Extended exact values and refusals, including lexical/text limits absent from original table.
extensions=[]
for value in ['+00012.500','-.5','+.5','-0','-0000.0000','0.'+'0'*4094+'1','-'+'9'*4093+'.995','+'+'9'*4093+'.995','.'+'9'*4096,'-.'+'9'*4096,'9'*4096]:
 for kind in ['weight','money','percent_display','ic_display','small']:
  x={'percent':value} if kind=='weight' else {'value':value};extensions.append(dict(kind=kind,inputs=x))
for value in [None,False,True,12,12.0,'',' ',' 12','12 ','1.','+','.','-.','1e2','-Infinity','１２.５','١٢.٥','0\x001','9'*4097,'-.'+'9'*4097,'0'*4096+'.0']:
 for kind in ['weight','money']:
  extensions.append(dict(kind=kind,inputs={'percent':value} if kind=='weight' else {'value':value}))
random_source=random.Random(20261023)
for _ in range(180):
 size=random_source.choice([1,4,27,28,29,39,80,200])
 n=''.join(str(random_source.randrange(10)) for j in range(size))
 cut=random_source.randrange(size+1)
 value=('-' if random_source.randrange(2) else '')+(n[:cut] or '0')+'.'+(n[cut:] or '0005')
 for kind in ['weight','money','ic_display','percent_display']:extensions.append(dict(kind=kind,inputs={'percent':value} if kind=='weight' else {'value':value}))
extended=[]
for c in extensions:
 try:expected=number(c['kind'],c['inputs']);error=None
 except Refusal as e:expected=None;error=str(e)
 extended.append(dict(**c,independent=expected,error=error))
numeric_original=[dict(kind=c['kind'],inputs=c['inputs'],independent=own(c),error=None) for c in original+supplemental if c['kind'] in numeric_kinds]
all_numeric=numeric_original+extended
contexts=[(2,False),(9,True),(28,False),(28,True),(60,True),(4300,True)]
context_records=[]
for precision,traps in contexts:
 with localcontext() as ctx:
  ctx.prec=precision
  for signal in ctx.traps:ctx.traps[signal]=traps
  for index,c in enumerate(all_numeric):
   try:actual=candidate.reference(c);error=None
   except candidate.ReferenceNumberError as e:actual=None;error=e.code
   matched=exact(actual,c['independent']) and error==c['error']
   context_records.append(dict(case_index=index,precision=precision,all_traps=traps,passed=matched,actual_sha256=H(str(actual).encode()),error=error))
assert all(r['passed'] for r in context_records)
save('NUMERIC_EXTENSION_INPUTS.json',dict(scope='Independent Fraction expected values; includes lexical refusals and boundary literals',records=extended))
save('NUMERIC_CONTEXT_OBSERVATIONS.json',dict(input_cases=len(all_numeric),contexts=contexts,observations=len(context_records),passed=sum(r['passed'] for r in context_records),records=context_records))
# Whole-stage exhaustive subset conjunction: no candidate product is executed.
completion_records=[]
for kind,profile,slots in [('research',None,['R','RV']),('engineering_pipeline',None,['R','PLAN','B','BV','P:0','P:1']),('replay','P5_NUMERICAL',['SV','E','CV','P:0','P:1']),('replay','PUBLISHED_REF_PROJECTION',['SV','E','CV'])]:
 for mask in itertools.product([False,True],repeat=len(slots)):
  for flags in itertools.product([False,True],repeat=5):
   evidence,bindings,closed,receipt,sql=flags
   x=dict(kind=kind,profile=profile,decisions=2,resolved_plan_frozen=True,comparison_verified=True,registry_slots=slots,slot_statuses={s:'VERIFIED_SUCCESS' for s,b in zip(slots,mask) if b},required_artifacts_verified=evidence,all_bindings_verified=bindings,dispatch_closed=closed,completion_verified=receipt,terminal_commit_verified=sql,quiescent=True)
   expected_success=all(mask) and all(flags)
   got=completion(x);dev=revised.completion_example(x)
   assert (got['status']=='SUCCEEDED')==expected_success and (dev['status']=='SUCCEEDED')==expected_success
   completion_records.append(dict(kind=kind,profile=profile,slot_mask=list(mask),flags=list(flags),expected_success=expected_success,independent=got,candidate=dev))
save('COMPLETION_SUBSET_CHALLENGES.json',dict(scope='Finite valid premises, not real SQLite crash/concurrency tests',cases=len(completion_records),passed=len(completion_records),records=completion_records))
base=copy.deepcopy(next(c['inputs'] for c in supplemental if c['kind']=='nested_binding'))
binding_records=[]
for key,old in base['actual'].items():
 x=copy.deepcopy(base)
 x['actual'][key]=old+1 if type(old) is int else str(old)+'-wrong'
 got=binding(x);dev=revised.binding_example(x)
 assert got['action']=='RECOVERY_REQUIRED' and exact(dev,got)
 binding_records.append(dict(changed_key=key,input=x,independent=got,candidate=dev))
# Additional half-initialized/claim/replay/ownership variants.
for patch in [dict(core_start_seq=None,core_terminal_seq=20),dict(registration_seq=base['core_start_seq']),dict(core_terminal_seq=base['core_start_seq']),dict(terminal_verified=False),dict(parent_root='/workspace/research-runs'),dict(core_terminal_seq=None,slot_state='BOUND',no_core_side_effects_proven=False)]:
 x=copy.deepcopy(base);x.update(patch);got=binding(x);dev=revised.binding_example(x)
 assert got['action']=='RECOVERY_REQUIRED' and exact(dev,got)
 binding_records.append(dict(changed_fields=patch,input=x,independent=got,candidate=dev))
save('BINDING_EXTENSION_CHALLENGES.json',dict(scope='Literal design ownership predicates; no live authority, OS or filesystem isolation',cases=len(binding_records),records=binding_records))
# Actual old helper failures rerun read-only, then observe revised helper against same independent expected.
old_helper=O.parent/'p6-g1-f7a1a68-independent/reviewed-source/docs/audits/phase-6/reference_check.py'
if not old_helper.exists():old_helper=Path('E:/WORK/AQRP-audits/p6-f7a1a68/src/docs/audits/phase-6/reference_check.py')
old=load('old_precision_helper_for_historical_reproduction',old_helper)
original_failures=[]
for kind,fields in [('weight',{'percent':'0.123456789012345678901234567890123456789'}),('money',{'value':'999999999999999999999999999999.995'})]:
 c=dict(kind=kind,inputs=fields);expect=number(kind,fields)
 try:old_got=old.reference(c);err=None
 except Exception as e:old_got=None;err=type(e).__name__
 new_got=candidate.reference(c)
 assert old_got!=expect and new_got==expect
 original_failures.append(dict(kind=kind,inputs=fields,independent_expected=expect,old=old_got,old_error=err,revised=new_got,passed=True))
save('ORIGINAL_TWO_COUNTEREXAMPLES.json',dict(old_source=str(old_helper),old_sha256=H(old_helper.read_bytes()),records=original_failures))
result=dict(fixed_sha=FIX,scope='G1 design/numeric reference only; zero P6 product/UI/SQLite/OS tests',original_groups=32,supplemental_groups=95,independent_answer_passed=127,supplemental_counts=dict(completion=31,binding=30,numeric=24,refusal=10),extended_numeric_cases=len(extended),numeric_cases_with_original=len(all_numeric),context_observations=len(context_records),completion_subset_cases=len(completion_records),binding_extension_cases=len(binding_records),old_precision_counterexamples=2,all_passed=True)
save('INDEPENDENT_RESULTS_SUMMARY.json',result);print(json.dumps(result))

