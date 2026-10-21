import subprocess,json,hashlib
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
R=Path(__file__).resolve().parent
records=[]
for name,repo,args in [
('review-final-status',r'C:\Users\11638\AppData\Local\AQRP\reviews\p1-18d51fb',['status','--porcelain=v1','-b']),
('developer-final-status',r'C:\Users\11638\AppData\Local\AQRP\checkouts\phase1-57461d5d-5de2-4c78-9b4e-5fad2b5ccb29',['status','--porcelain=v1','-b']),
('developer-final-head',r'C:\Users\11638\AppData\Local\AQRP\checkouts\phase1-57461d5d-5de2-4c78-9b4e-5fad2b5ccb29',['rev-parse','HEAD']),
('legacy-final-status',r'B:\BaiduSyncdisk\学习\投资\量化\量化交易比赛\Alpha Quant Research Platform (AQRP)',['status','--porcelain=v1','-b']),
('final-refs',r'C:\Users\11638\AppData\Local\AQRP\reviews\p1-18d51fb',['ls-remote','https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-.git','refs/heads/main','refs/pull/2/head','refs/tags/phase0-baseline^{}','refs/tags/phase1-baseline^{}'])]:
    cmd=['git','--no-optional-locks',*args];p=subprocess.run(cmd,cwd=repo,capture_output=True)
    (R/(name+'.stdout.log')).write_bytes(p.stdout);(R/(name+'.stderr.log')).write_bytes(p.stderr)
    records.append(dict(name=name,command=cmd,cwd=repo,exit_code=p.returncode))
    print(name,p.returncode,p.stdout.decode(errors='replace').strip() if name not in ['legacy-final-status'] else 'recorded')
(R/'final-facts-receipt.json').write_text(json.dumps(dict(audit='GPT Work 补充审核',time=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),commands=records),ensure_ascii=False,indent=2),encoding='utf-8')
# Independent manifest for generated review outputs plus experiment sealed bytes; skip cache/temp environments.
paths=[p for p in R.iterdir() if p.is_file() and p.name!='ROUND2_EVIDENCE_MANIFEST.json']
for sub in ['probe-snapshots','zone-snapshots']:
    paths.extend(p for p in (R/sub).rglob('*') if p.is_file())
manifest={'audit':'GPT Work 补充审核','phase0_sha':'7de1d0e81385ae97f98ea673fe05dd726f0b577b','phase1_sha':'f579b2c99e762085772de6e70ba1fa98792a7add','created_at':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'scope':'Reports, command/script/log/receipt outputs, fixed source ZIPs, and probe snapshots; excludes self and pytest caches/tmp. Fixed source trees are represented by their archive ZIPs and verified project manifests.','files':[dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(set(paths))]}
(R/'ROUND2_EVIDENCE_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
for f in manifest['files']:assert hashlib.sha256((R/f['path']).read_bytes()).hexdigest()==f['sha256']
print('Round2 evidence manifest hashes verified',len(manifest['files']))
print(R/'GPT-Work-Phase0-Phase1-Round2-Review.md')
