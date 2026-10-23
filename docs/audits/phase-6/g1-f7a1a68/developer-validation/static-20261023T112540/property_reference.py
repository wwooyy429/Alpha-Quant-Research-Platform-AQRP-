from pathlib import Path
from decimal import localcontext, Inexact, Rounded, InvalidOperation
from fractions import Fraction
import argparse,hashlib,importlib.util,json

parser=argparse.ArgumentParser();parser.add_argument('directory',type=Path);parser.add_argument('output',type=Path);a=parser.parse_args()
spec=importlib.util.spec_from_file_location('revision_design',a.directory/'revision_reference.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
original=json.loads((a.directory/'GOLDEN_CANDIDATES.json').read_bytes())['cases'];extra=json.loads((a.directory/'SUPPLEMENTAL_CANDIDATES.json').read_bytes())['cases']
numeric_kinds={'weight','money','quantity','small','ic_display','percent_display','numeric_rejection'}
cases=[c for c in original+extra if c['kind'] in numeric_kinds]
observations=[]
for precision in (1,2,9,28,50,200):
 with localcontext() as context:
  context.prec=precision
  context.traps[Inexact]=True;context.traps[Rounded]=True;context.traps[InvalidOperation]=True
  for c in cases:
   try:actual=module.evaluate(c);error=None
   except Exception as exc:actual=None;error=type(exc).__name__
   observations.append({'id':c['id'],'ambient_precision':precision,'pass':error is None and type(actual) is type(c['expected']) and actual==c['expected'],'error':error})
oracle=[]
for c in cases:
 if c['kind']=='numeric_rejection':continue
 kind,x=c['kind'],c['inputs'];actual=module.evaluate(c)
 value=Fraction(x['percent'] if kind=='weight' else x['value'])
 if kind=='weight':expected=value/100;got=Fraction(actual)
 elif kind=='money':expected=Fraction(round(value*100),100);got=Fraction(actual.replace(',',''))
 elif kind=='ic_display':expected=Fraction(round(value*10000),10000);got=Fraction(actual)
 elif kind=='percent_display':expected=Fraction(round(value*100*10000),10000);got=Fraction(actual[:-1])
 else:expected=value;got=Fraction(actual)
 oracle.append({'id':c['id'],'oracle':'stdlib Fraction with exact rational round; separate from coefficient/scale formatter','pass':got==expected})
result={'executor':'Codex developer independent-reference method, not GPT Work independent audit','scope':'Design numeric ambient-context property and independent rational oracle only; no UI/product execution','numeric_cases':len(cases),'context_configurations':6,'context_observations':len(observations),'context_failures':sum(not r['pass'] for r in observations),'Fraction_oracle_cases':len(oracle),'Fraction_failures':sum(not r['pass'] for r in oracle),'observations':observations,'oracle':oracle,'source_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [a.directory/'reference_check.py',a.directory/'revision_reference.py',a.directory/'GOLDEN_CANDIDATES.json',a.directory/'SUPPLEMENTAL_CANDIDATES.json']}}
a.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({k:result[k] for k in ('numeric_cases','context_observations','context_failures','Fraction_oracle_cases','Fraction_failures')}));assert not result['context_failures'] and not result['Fraction_failures']
