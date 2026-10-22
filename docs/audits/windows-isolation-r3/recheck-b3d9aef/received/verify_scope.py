import pathlib,json,subprocess,hashlib,csv
O=pathlib.Path(r'C:/Users/11638/AppData/Local/AQRP/reviews/windows-isolation-r3-b3d9aef-independent');C=O.parent/'wi-r3-b3d9aef-review';FIX='b3d9aef79396db948d326f5ce247131f96739d9d';BASE='0a57dccb5618ba08cd3572d6d6b78fec963a3041';cmd=[]
def git(*a):
 p=subprocess.run(['git','-C',str(C),*a],capture_output=True);cmd.append({'argv':p.args,'exit_code':p.returncode});p.check_returncode();return p.stdout
sha=lambda b:hashlib.sha256(b).hexdigest()
assert git('rev-parse','HEAD').decode().strip()==FIX and not git('status','--porcelain')
d=json.loads((C/'docs/audits/windows-isolation-r3/IDENTITY.json').read_bytes());print('identityfields',list(d));pres=d['preserved_files']
for e in pres:assert sha((C/e['path']).read_bytes())==e['sha256'],e['path']
oldpy=[x for x in git('ls-tree','-r','--name-only',BASE,'src/aqrp').decode().splitlines() if x.endswith('.py')];changed=[];same=[]
for p in oldpy:
 if git('show',BASE+':'+p)==(C/p).read_bytes():same.append(p)
 else:changed.append(p)
assert set(changed)=={'src/aqrp/__init__.py','src/aqrp/factors/admission.py','src/aqrp/validation/evaluator.py'}
for path in ['requirements.lock','src/aqrp/data/snapshot.py','docs/requirements.csv']:
 assert git('show',BASE+':'+path)==(C/path).read_bytes()
files=[{'path':p.relative_to(C/'src/aqrp').as_posix(),'sha256':sha(p.read_bytes())} for p in sorted((C/'src/aqrp').rglob('*.py'))];bm={'factor_api':'1.0.0','data_contract':'contracts/1.0.0','dependency_lock_sha256':sha((C/'requirements.lock').read_bytes()),'files':files};bundle=sha(json.dumps(bm,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode());assert len(files)==47 and bundle=='4e657dea368b50b083030dbad32821683735be420f727b1db26ac2ba60e82dd5'
change=json.loads((O.parent/'windows-isolation-r3-b3d9aef/CHANGE_LIST.json').read_bytes())
for e in change['changes']:
 assert sha((C/e['path']).read_bytes())==e['new_sha256']
 if e['old_sha256'] is not None:assert sha(git('show',BASE+':'+e['path']))==e['old_sha256']
actual=set(git('diff','--name-only',BASE,FIX).decode().splitlines());assert actual=={e['path'] for e in change['changes']}
refs=git('ls-remote','origin','refs/heads/main','refs/tags/phase3-baseline','refs/tags/phase3-baseline^{}','refs/tags/v0.3.0','refs/tags/v0.3.0^{}').decode();assert all(l.split()[0]==BASE for l in refs.splitlines() if '^{}'in l or 'refs/heads/main'in l)
result={'fixed_sha':FIX,'base':BASE,'clean':True,'preserved_files':len(pres),'old_python_unchanged':len(same),'old_python_changed':changed,'bundle':bundle,'modules':47,'p1_snapshot_and_lock_unchanged':True,'canonical_rows':len(list(csv.DictReader((C/'docs/requirements.csv').read_text(encoding='utf-8-sig').splitlines()))),'declared_changes_all_match':True,'remote_refs':refs,'git_commands':cmd,'result':'PASS'};(O/'SCOPE_VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print({k:v for k,v in result.items() if k not in ['git_commands','remote_refs']})
