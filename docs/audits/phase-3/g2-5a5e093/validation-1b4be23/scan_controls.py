from pathlib import Path
import hashlib,json,subprocess,random,string
root=Path(r'C:\Users\11638\AppData\Local\AQRP\checkouts\phase1-57461d5d-5de2-4c78-9b4e-5fad2b5ccb29')
run=Path(r'C:\Users\11638\AppData\Local\AQRP\runs\p3-g2-repair-20261022')
sdk=run/'clean-sdk/aqrp-991faaf3-2e20-471d-a576-d1b64dbe3eaa'
out=run/'scanner-controls';out.mkdir(exist_ok=True)
exe=sdk/'gitleaks.exe'
version=subprocess.check_output([str(exe),'version']).decode().strip();assert version=='8.30.1'
rel='docs/audits/phase-3/implementation/validation-07e7c88/sdk/research/runs/826873ac-7112-4114-8518-1ae98b5c11d9/events.jsonl'
raw=(root/rel).read_text(encoding='utf-8').splitlines()[7]
token='gh'+'p_'+''.join(random.Random(718).choices(string.ascii_letters+string.digits,k=36))
rows=[]
for name,path,text,expected in [('exact_event',rel,raw,0),('same_digest_other_path','elsewhere/events.jsonl',raw,1),('changed_line_synthetic_credential',rel,raw[:-1]+',"token":"'+token+'"}',1)]:
    folder=out/'inputs'/name;p=folder/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text+'\n',encoding='utf-8',newline='\n')
    args=[str(exe),'dir',str(folder),'--config',str(root/'.gitleaks.toml'),'--redact=100','--no-banner']
    with (out/(name+'.log')).open('wb') as f: r=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT)
    rows.append({'case':name,'argv':args,'expected_exit':expected,'actual_exit':r.returncode,'passed':r.returncode==expected,'input_sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
assert all(r['passed'] for r in rows)
receipt={'actual_executor':'Codex developer','business_sha':'1b4be236e888805f5c4e45357b158fcdb6058df0','version':version,'scanner_exe_sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),'config_sha256':hashlib.sha256((root/'.gitleaks.toml').read_bytes()).hexdigest(),'config_unchanged_from_reviewed_5a5e093':subprocess.check_output(['git','diff','5a5e093','HEAD','--','.gitleaks.toml'],cwd=root)==b'','controls':rows,'raw_synthetic_positive_inputs':'Retained locally, omitted from repository; redacted controls and exact input hashes archived','deployed':False}
(out/'SCANNER_CONTROLS.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({'controls':len(rows),'passed':True}))
