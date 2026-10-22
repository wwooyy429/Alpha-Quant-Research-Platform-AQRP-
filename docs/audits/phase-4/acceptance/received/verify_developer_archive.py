import pathlib,json,zipfile,hashlib,io
O=pathlib.Path(__file__).parent;D=O.parent/'work-p4-g2-repair-3c87579'
H=lambda b:hashlib.sha256(b).hexdigest()
seal=json.loads((D/'Developer-Evidence-Seal.json').read_bytes());p=D/seal['archive'];assert p.stat().st_size==seal['bytes'] and H(p.read_bytes())==seal['sha256']
manifest=(D/'EVIDENCE_MANIFEST.json').read_bytes();assert H(manifest)==seal['manifest_sha256'];m=json.loads(manifest)
with zipfile.ZipFile(p) as z:
 assert z.testzip() is None and len(z.namelist())==len(m['files'])+1
 assert set(z.namelist())=={e['path'] for e in m['files']}|{'EVIDENCE_MANIFEST.json'}
 assert z.read('EVIDENCE_MANIFEST.json')==manifest
 for e in m['files']:
  b=z.read(e['path']);assert len(b)==e['bytes'] and H(b)==e['sha256'],e['path']
 source=zipfile.ZipFile(io.BytesIO(z.read('Fixed-Source.zip')));C=O.parent/'p4-g2-recheck-3c87579';names=[n for n in source.namelist() if not n.endswith('/')]
 # Source ZIP paths are repo-relative (assert rather than infer arbitrary roots).
 assert 'src/aqrp/portfolio/service.py' in names
 for n in names:assert source.read(n)==(C/n).read_bytes(),n
old=O.parent/'work-p4-g2-18439f3-independent/EVIDENCE.zip';assert H(old.read_bytes())=='6ee677b012669dc2cd9f47598386baeef2da453d40767447497abe571d86a170'
result={'fixed_sha':m['fixed_sha'],'archive':str(p),'bytes':p.stat().st_size,'sha256':seal['sha256'],'manifest_files':len(m['files']),'CRC_and_all_member_hashes':'PASS','fixed_source_byte_matches':len(names),'previous_independent_archive_unchanged':True,'result':'PASS'}
(O/'DEVELOPER_ARCHIVE_VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))
