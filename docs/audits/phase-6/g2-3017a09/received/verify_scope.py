from pathlib import Path
import json,hashlib,subprocess,csv,sys
O=Path(__file__).parent;C=Path('E:/WORK/AQRP-audits/p6-3017a09/src');P=C/'docs/audits/phase-6'
H=lambda b:hashlib.sha256(b).hexdigest()
save=lambda n,x:(O/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
git=lambda *a:subprocess.check_output(['git','-C',str(C),*a])
identity=json.loads((P/'IMPLEMENTATION_IDENTITY.json').read_bytes());start=identity['archival_start'];FIX='3017a097b49ecdae68228ca9a417fcd03c313200'
assert git('rev-parse','HEAD').decode().strip()==FIX and git('status','--porcelain')==b''
tree=git('ls-tree','-r','-z',start);(O/'ARCHIVAL_START_TREE_NUL.bin').write_bytes(tree)
blobs={}
for row in tree.rstrip(b'\0').split(b'\0'):
 meta,name=row.split(b'\t',1);blobs[name.decode()]=meta.split()[2].decode()
assert len(identity['preserved_files'])==5016
for entry in identity['preserved_files']:
 raw=(C/entry['path']).read_bytes()
 assert len(raw)==entry['bytes'] and H(raw)==entry['sha256']
 assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blobs[entry['path']],entry['path']
for entry in identity['current_files']:
 raw=(C/entry['path']).read_bytes();assert len(raw)==entry['bytes'] and H(raw)==entry['sha256']
tracked=set(git('ls-files','-z').decode().rstrip('\0').split('\0'))
listed=[e['path'] for e in identity['preserved_files']+identity['current_files']]
assert len(listed)==len(set(listed)) and tracked==set(listed)|{'docs/audits/phase-6/IMPLEMENTATION_IDENTITY.json'}
compat=json.loads((P/'COMPATIBILITY_IMPACT.json').read_bytes())
changed_existing=set(blobs)&set(git('diff','--name-only',start,FIX).decode().splitlines())
assert changed_existing==set(compat['explicit_existing_adapters']),(changed_existing^set(compat['explicit_existing_adapters']))
assert (C/'requirements.lock').read_bytes()==git('show','59246f9fd391c1713b6bed65dd22280f4d248493:requirements.lock')
for osname in ['windows','linux']:
 assert (C/('requirements-ui-'+osname+'.lock')).read_bytes()==(P/('UI_EXTENSION_'+osname.upper()+'.lock')).read_bytes()
 assert (C/('requirements-ui-'+osname+'.lock')).read_bytes()==(C/('src/aqrp/ui/requirements-'+osname+'.lock')).read_bytes()
for e in identity['bundle_manifest']['files']:assert H((C/'src/aqrp'/e['path']).read_bytes())==e['sha256']
canon=lambda v:json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
assert H(canon(identity['bundle_manifest']))==identity['bundle_sha256']
rows=list(csv.DictReader((C/'docs/requirements.csv').read_text(encoding='utf-8').splitlines()))
req=[r for r in rows if r['phase']=='6'];snap=json.loads((P/'REQUIREMENTS_SNAPSHOT.json').read_bytes())
assert len(rows)==106 and len(req)==8 and sum(r['tier']=='MVP' for r in req)==5 and req==snap['requirements']
for n in ['GOLDEN_CANDIDATES.json','SUPPLEMENTAL_CANDIDATES.json','TASK_COMPLETION_CONTRACT.md','NESTED_CONTEXT_CONTRACT.md','NUMERIC_REFERENCE_CONTRACT.md']:
 assert (P/n).read_bytes()==git('show','e71f6f090b102e4abfd70a5999e495f49546a1b5:docs/audits/phase-6/'+n),n
refs=git('ls-remote','origin','refs/heads/main','refs/tags/*').decode();(O/'REMOTE_REFS_START.txt').write_text(refs,encoding='utf-8')
r={n:h for h,n in (l.split() for l in refs.splitlines())}
assert r['refs/heads/main']==r['refs/tags/phase5-baseline^{}']==r['refs/tags/v0.5.0^{}']=='59246f9fd391c1713b6bed65dd22280f4d248493'
old=(O.parent/'p6-g1-recheck-e71f6f0-independent/REMOTE_REFS_START.txt').read_text(encoding='utf-8')
for h,n in (l.split() for l in old.splitlines()):
 if n.startswith('refs/tags/'):assert r[n]==h,n
(O/'IMPLEMENTATION_DIFF.patch').write_bytes(git('diff','--binary',start,FIX))
(O/'ADAPTER_DIFF.patch').write_bytes(git('diff',start,FIX,'--','src/aqrp/backtest','src/aqrp/portfolio/service.py','src/aqrp/services/research.py','src/aqrp/services/backtest.py','src/aqrp/experiments/ledger.py'))
context=['src/aqrp/services/tasks.py','src/aqrp/services/task_requests.py','src/aqrp/services/task_state.py','src/aqrp/services/task_context.py','src/aqrp/ui/app.py','src/aqrp/experiments/ledger.py','docs/audits/phase-3/STATISTICAL_CONVENTIONS.md','docs/audits/phase-6/TASK_AND_RECOVERY_CONTRACT.md','docs/audits/phase-6/TASK_COMPLETION_CONTRACT.md']
with (O/'FIXED_LINE_CONTEXT.txt').open('w',encoding='utf-8') as out:
 for n in context:
  out.write('\n===== '+n+' =====\n')
  for i,line in enumerate((C/n).read_text(encoding='utf-8').splitlines(),1):out.write(str(i)+': '+line+'\n')
save('SCOPE_IDENTITY_VERIFICATION.json',dict(fixed_sha=FIX,archival_start=start,preserved_files=5016,current_files=len(identity['current_files']),all_tracked_files=len(tracked),declared_existing_adapters=sorted(changed_existing),requirements=req,core_lock_sha256=identity['core_lock_sha256'],bundle_sha256=identity['bundle_sha256'],modules=83,old_Golden_G1_contracts_unchanged=True,main_and_tags_unchanged=True,result='PASS'))
print(json.dumps(dict(preserved=5016,current=len(identity['current_files']),tracked=len(tracked),explicit_existing_adapters=len(changed_existing),requirements=8,result='PASS')))

