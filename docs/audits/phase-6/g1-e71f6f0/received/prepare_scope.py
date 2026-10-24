from pathlib import Path
import json,subprocess
O=Path(__file__).parent
old=O.parent/'p6-g1-f7a1a68-independent'
s=(old/'verify_scope_release.py').read_text(encoding='utf-8').replace("C=Path('E:/WORK/AQRP-audits/p6-f7a1a68/src')","C=Path('E:/WORK/AQRP-audits/p6-e71f6f0/src')").replace("D=O.parent/'p6-g1-f7a1a68-20261023'","D=O.parent/'p6-g1-recheck-e71f6f0-20261023'")
s=s.replace("FIX='f7a1a68c5f747090f8c8a0e934f2fea859aec998'","FIX='e71f6f090b102e4abfd70a5999e495f49546a1b5';PARENT='f7a1a68c5f747090f8c8a0e934f2fea859aec998'")
s=s.replace("strip()==BASE","strip()==PARENT",1).replace("len(changes)==55","len(changes)==171")
s=s.replace("==83 and len(m['files'])==82","==207 and len(m['files'])==206").replace("members=83","members=207").replace("plan_archive_members=83","plan_archive_members=207")
# Current package and source evidence verification plus frozen inheritance retained; no new SDK execution.
extra="""
ident=json.loads((P/'g1-f7a1a68/DESIGN_REVISION_IDENTITY.json').read_bytes())
for entry in ident['unchanged_prior_G1_assets']:
 raw=(P/entry['path']).read_bytes()
 assert len(raw)==entry['bytes'] and H(raw)==entry['sha256']
 assert raw==git('show',PARENT+':docs/audits/phase-6/'+entry['path']),entry['path']
assert len(ident['unchanged_prior_G1_assets'])==13
for e in ident['model_files']:assert H((P/e['path']).read_bytes())==e['sha256']
old=O.parent/'p6-g1-f7a1a68-independent'
rr=json.loads((old/'RECEIPT.json').read_bytes());oldz=old/'EVIDENCE.zip'
assert oldz.stat().st_size==rr['bytes']==584855382 and fh(oldz)==rr['sha256']=='22cc883e7bd46f2b83ce4e5251505776862dedde3c532e15eddb5a8e07854273'
with zipfile.ZipFile(oldz) as z:
 assert z.testzip() is None
 mmraw=z.read('EVIDENCE_MANIFEST.json');assert H(mmraw)==rr['manifest_sha256']
 mm=json.loads(mmraw)
 assert len(mm['files'])==105 and len(z.namelist())==len(set(z.namelist()))==106
 assert set(z.namelist())=={e['path'] for e in mm['files']}|{'EVIDENCE_MANIFEST.json'}
 for e in mm['files']:
  with z.open(e['path']) as f:assert hashlib.file_digest(f,'sha256').hexdigest()==e['sha256']
 received=json.loads((P/'g1-f7a1a68/RECEIVED_IDENTITY.json').read_bytes())
 assert len(received['copied_originals'])==70
 for e in received['copied_originals']:
  raw=(P/'g1-f7a1a68/received'/e['path']).read_bytes()
  assert len(raw)==e['bytes'] and H(raw)==e['sha256'] and raw==(old/e['path']).read_bytes(),e['path']
# Capture exact changed files and numbered current contract/source context.
(O/'REVISION_DIFF.patch').write_bytes(git('diff','--binary',PARENT,FIX))
(O/'FULL_PLAN_DIFF.patch').write_bytes(git('diff','--binary',BASE,FIX))
names=['AGENTS.md']+['docs/'+n+'.md' for n in ['PROJECT_CHARTER','ARCHITECTURE','INTERFACES','REQUIREMENTS','TRACEABILITY','ROADMAP','PROGRESS','DECISIONS']]
names += [p.relative_to(C).as_posix() for p in P.glob('*.md')]
names += ['src/aqrp/'+n for n in ['services/backtest.py','backtest/engine.py','backtest/provider.py','portfolio/service.py','experiments/ledger.py']]
with (O/'REVIEWED_SOURCE_CONTEXT.txt').open('w',encoding='utf-8') as out:
 for name in names:
  f=C/name
  if f.exists():
   out.write('\\n===== '+name+' sha256='+fh(f)+' =====\\n')
   for i,line in enumerate(f.read_text(encoding='utf-8-sig').splitlines(),1):out.write(str(i)+': '+line+'\\n')
save('INHERITANCE_AND_ARCHIVE.json',dict(prior_13_assets_exact=True,old_reference_32_bytes_exact=True,old_independent_zip_crc_member_hashes=rr,received_original_files=70,developer_models_bound=ident['model_files'],prior_dependency_evidence='Same thirteen input/lock/metadata assets; prior metadata-only independent resolution retained, no fresh install/runtime or resolver claimed',new_developer_source_all_tracked=True))
"""
# Insert before result save.
s=s.replace("save('SCOPE_RELEASE_VERIFICATION.json'",extra+"\nsave('SCOPE_RELEASE_VERIFICATION.json'",1)
(O/'verify_scope_release.py').write_text(s,encoding='utf-8')
print('Review script prepared, preserved prior script.')

