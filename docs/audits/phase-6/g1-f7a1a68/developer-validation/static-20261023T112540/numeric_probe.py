from pathlib import Path
import argparse,hashlib,importlib.util,json

parser=argparse.ArgumentParser();parser.add_argument('source',type=Path);parser.add_argument('output',type=Path);a=parser.parse_args()
spec=importlib.util.spec_from_file_location('candidate_reference',a.source);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
cases=[
 {'kind':'weight','inputs':{'percent':'0.123456789012345678901234567890123456789'},'expected':'0.00123456789012345678901234567890123456789'},
 {'kind':'money','inputs':{'value':'999999999999999999999999999999.995'},'expected':'1,000,000,000,000,000,000,000,000,000,000.00'},
]
records=[]
for c in cases:
 try:actual=module.reference(c);error=None
 except Exception as e:actual=None;error=type(e).__name__
 records.append({**c,'actual':actual,'error':error,'match':actual==c['expected'] and error is None})
result={'executor':'Codex developer actual execution of repository design reference, not P6 product or independent audit','reference_file':str(a.source),'reference_sha256':hashlib.sha256(a.source.read_bytes()).hexdigest(),'records':records,'matched':sum(r['match'] for r in records),'mismatched':sum(not r['match'] for r in records)}
a.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(result));raise SystemExit(0 if all(r['match'] for r in records) else 1)
