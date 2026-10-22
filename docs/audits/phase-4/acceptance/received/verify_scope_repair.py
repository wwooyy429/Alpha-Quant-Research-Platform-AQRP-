import pathlib,json,subprocess,hashlib,csv,datetime
O=pathlib.Path(__file__).parent;C=O.parent/'p4-g2-recheck-3c87579';FIX='3c8757949b0fd5c97953b06a74ebc2d0e56676e4';OLD='18439f31536295aea42e57e566d07cce345a35cf';BASE='0a57dccb5618ba08cd3572d6d6b78fec963a3041';G1='265af16353d85ce8c2d229a7517809d707498da8'
def git(*a):return subprocess.check_output(['git','-C',str(C),*a])
H=lambda b:hashlib.sha256(b).hexdigest()
assert git('rev-parse','HEAD').decode().strip()==FIX and not git('status','--porcelain')
rows=list(csv.DictReader((C/'docs/requirements.csv').read_text(encoding='utf-8-sig').splitlines()));p4=[r for r in rows if r['phase']=='4'];assert len(rows)==106 and len(p4)==7 and sum(r['tier']=='MVP' for r in p4)==4
d=json.loads((C/'docs/audits/phase-4/g2-18439f3/IDENTITY.json').read_bytes());f=json.loads((C/'docs/audits/phase-4/FROZEN_INPUTS.json').read_bytes())
for e in d['preserved_files']+f['files']:assert H((C/e['path']).read_bytes())==e['sha256'],e['path']
for e in d['bundle_manifest']['files']:assert H((C/'src/aqrp'/e['path']).read_bytes())==e['sha256']
canon=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
assert H(canon(d['bundle_manifest']))==d['bundle_sha256']=='0ccd7642b3c69d06c552bc328195387f0a9ec8a06a45398df0076bde8f81cdf7'
assert git('show',BASE+':requirements.lock')==(C/'requirements.lock').read_bytes()
oldmodules=[p for p in git('ls-tree','-r','--name-only',BASE,'src/aqrp').decode().splitlines() if p.endswith('.py')];same=[];changed=[]
for p in oldmodules:(same if git('show',BASE+':'+p)==(C/p).read_bytes() else changed).append(p)
assert len(same)==43 and set(changed)=={'src/aqrp/__init__.py','src/aqrp/factors/admission.py'}
assert git('show',BASE+':src/aqrp/factors/admission.py').replace(b'"1.1.0"',b'"1.2.1"')==(C/'src/aqrp/factors/admission.py').read_bytes()
plans=[p for p in git('ls-tree','-r','--name-only',G1,'docs/audits/phase-4').decode().splitlines() if any(k in p.lower() for k in ['golden','rounding_reference'])]
for p in plans:assert git('show',G1+':'+p)==(C/p).read_bytes()
diff=git('diff','--name-only',OLD,FIX).decode().splitlines();(O/'repair-complete.patch').write_bytes(git('diff','--binary',OLD,FIX));(O/'SOURCE_STATUS.txt').write_bytes(git('status','--porcelain=v1'))
refs=git('ls-remote','origin','refs/heads/main','refs/tags/phase3-baseline','refs/tags/phase3-baseline^{}','refs/tags/v0.3.0','refs/tags/v0.3.0^{}').decode();assert all(l.split()[0]==BASE for l in refs.splitlines() if '^{}' in l or 'refs/heads/main' in l)
result={'fixed_sha':FIX,'old_sha':OLD,'clean':True,'canonical_requirements':len(rows),'phase4_requirements':p4,'preserved_files':len(d['preserved_files']),'frozen_files':len(f['files']),'bundle_sha256':d['bundle_sha256'],'bundle_modules':len(d['bundle_manifest']['files']),'unchanged_P3_modules':same,'metadata_exceptions':changed,'unchanged_G1_answers':plans,'all_repair_changes':diff,'stable_refs':refs,'result':'PASS'}
(O/'SCOPE_VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:result[k] for k in ['fixed_sha','preserved_files','frozen_files','bundle_modules','result']}))
