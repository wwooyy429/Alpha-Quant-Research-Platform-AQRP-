import json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
out=Path(__file__).resolve().parent;root=out.parent/"p3-implementation-5a5e093";SHA="5a5e093c2e9b39abe1332e49d1df40d20f9fd33f";BASE="f26255fc40a3080bfa883ad64938f60036a14759";cmds=[]
def git(path,*args):
 p=subprocess.run(["git","-C",str(path),*args],capture_output=True,text=True,encoding="utf-8");cmds.append(dict(argv=["git","-C",str(path),*args],stdout=p.stdout,stderr=p.stderr,exit_code=p.returncode));assert p.returncode==0;return p.stdout.strip()
for path in (root,Path(r"C:\Users\11638\AppData\Local\AQRP\checkouts\phase1-57461d5d-5de2-4c78-9b4e-5fad2b5ccb29")):
 assert git(path,"rev-parse","HEAD")==SHA and git(path,"status","--porcelain=v1","--untracked-files=all")==""
raw=git(root,"ls-remote","https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-.git","refs/heads/main","refs/tags/phase2-baseline","refs/tags/phase2-baseline^{}","refs/tags/v0.2.0","refs/tags/v0.2.0^{}")
refs={line.split()[1]:line.split()[0] for line in raw.splitlines()}
for n in ("refs/heads/main","refs/tags/phase2-baseline^{}","refs/tags/v0.2.0^{}"):assert refs[n]==BASE
pr=json.loads((out/"pr5-end.json").read_bytes());assert pr["head"]["sha"]==SHA and "AQRP_FIXED_REVIEW_SHA: "+SHA in pr["body"] and not pr["merged"]
result=dict(reviewed_sha=SHA,baseline=BASE,end_utc=datetime.now(timezone.utc).isoformat(),fixed_clone_and_developer_clean=True,pr_head=pr["head"]["sha"],pr_state=pr["state"],pr_merged=pr["merged"],stable_remote_refs=refs,drift_detected=False,deployed=False,merged=False,tagged=False,p4=False,commands=cmds)
(out/"end-state.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in result.items() if k!="commands"},ensure_ascii=False,indent=2))

