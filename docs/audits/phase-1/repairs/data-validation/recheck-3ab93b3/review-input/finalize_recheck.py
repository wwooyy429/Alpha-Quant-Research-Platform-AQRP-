from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import subprocess,hashlib,json
R=Path(__file__).resolve().parent
records=[]
for name,repo,args in [
('final-review-status',r'C:\Users\11638\AppData\Local\AQRP\reviews\p1-3ab93b3',['status','--porcelain=v1','-b']),
('final-developer-status',r'C:\Users\11638\AppData\Local\AQRP\checkouts\p1-fix-20261021',['status','--porcelain=v1','-b']),
('final-refs',r'C:\Users\11638\AppData\Local\AQRP\reviews\p1-3ab93b3',['ls-remote','https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-.git','refs/heads/main','refs/pull/4/head','refs/tags/phase0-baseline^{}','refs/tags/phase1-baseline^{}'])]:
    p=subprocess.run(['git','--no-optional-locks',*args],cwd=repo,capture_output=True)
    (R/(name+'.stdout.log')).write_bytes(p.stdout);(R/(name+'.stderr.log')).write_bytes(p.stderr)
    records.append(dict(name=name,cwd=repo,args=['git',*args],exit_code=p.returncode))
    assert p.returncode==0
    print(name,p.stdout.decode(errors='replace').strip())
(R/'final-receipt.json').write_text(json.dumps(dict(audit='GPT Work 补充审核',time=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),commands=records),ensure_ascii=False,indent=2),encoding='utf-8')
files=[p for p in R.iterdir() if p.is_file() and p.name!='RECHECK_EVIDENCE_MANIFEST.json']
run=R/'runs/aqrp-693e8864-c8ff-4369-86c3-defabf81dffd'
files.extend(p for p in run.iterdir() if p.is_file())
files.extend(p for p in (run/'wheel').iterdir() if p.is_file())
m={'audit':'GPT Work 补充审核','target_sha':'3ab93b35c0b5e4e7b5e85c27f641748aa86cb24f','scope':'Review outputs/scripts/logs, fixed source ZIP and actual SDK root artifacts/wheel; excludes self, environments and caches; data child hashes remain in their manifests','files':[dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(set(files))]}
(R/'RECHECK_EVIDENCE_MANIFEST.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
for f in m['files']:assert hashlib.sha256((R/f['path']).read_bytes()).hexdigest()==f['sha256']
print('manifest checked',len(m['files']))
