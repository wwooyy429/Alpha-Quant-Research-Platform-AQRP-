from pathlib import Path
import json
P=Path('E:/WORK/AQRP-audits/p6-e71f6f0/src/docs/audits/phase-6')
d=json.loads((P/'SUPPLEMENTAL_CANDIDATES.json').read_bytes());first=None
for c in d['cases']:
 x=c['inputs'];k=c['kind']
 if k=='nested_binding':
  if first is None:print('BINDING_BASE '+json.dumps(x));first=x
  x={k:v for k,v in x.items() if v!=first.get(k)}
  if 'actual' in x:x['actual_delta']={k:v for k,v in x.pop('actual').items() if v!=first['actual'].get(k)}
 elif c['group'] in ('numeric','numeric_refusal'):
  def shorten(v):
   if isinstance(v,str) and len(v)>200:return {'length':len(v),'prefix':v[:60],'suffix':v[-30:]}
   if isinstance(v,dict):return {k:shorten(v) for k,v in v.items()}
   return v
  x=shorten(x)
 print(json.dumps({'id':c['id'],'kind':k,'in':x,'expected':shorten(c['expected']) if c['group'].startswith('numeric') else c['expected'],'basis':c['basis']},ensure_ascii=False))

