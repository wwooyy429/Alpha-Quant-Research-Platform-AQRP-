"""Narrow scanner exception controls; synthetic-only adversarial credentials."""
import hashlib,json,random,string,subprocess,sys
from pathlib import Path
out=Path(__file__).resolve().parent;root=Path(sys.argv[1]).resolve();sdk=next((out/"sdk").iterdir())
H=lambda b:hashlib.sha256(b).hexdigest()
digest_value="69266f2ffa606b5e7b3f052cb193dcf9de2e8c0b70a71467217e8b848332c554"
rel=Path("docs/audits/phase-3/implementation/validation-07e7c88/sdk/research/runs/826873ac-7112-4114-8518-1ae98b5c11d9/events.jsonl")
original=(root/rel).read_bytes()
cachepath=root/"docs/audits/phase-3/implementation/validation-07e7c88/sdk/research/runs"/("cache-"+digest_value+".json")
cache=json.loads(cachepath.read_bytes());canonical=lambda obj:json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode()
assert H(canonical(cache["key"]))==digest_value
assert any(json.loads(line).get("payload",{}).get("key_hash")==digest_value for line in original.splitlines())
exe=sdk/"gitleaks.exe";version=subprocess.run([str(exe),"version"],capture_output=True,text=True);assert version.returncode==0 and "8.30.1" in version.stdout
control=out/"scanner-controls";results=[]
for name,relative,content,expected in (("exact_event",rel,original,0),("same_digest_elsewhere",Path("elsewhere/events.jsonl"),original,1),("changed_line_at_exact_path",rel,original+b'\n'+canonical({"api_key":"".join(random.Random(556).choices(string.ascii_letters+string.digits,k=40))})+b'\n',1)):
 case=control/name;p=case/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(content)
 argv=[str(exe),"dir",str(case),"--config",str(root/".gitleaks.toml"),"--redact=100","--no-banner","--report-format","json","--report-path",str(control/(name+"-findings.json"))]
 r=subprocess.run(argv,capture_output=True);(control/(name+".stdout.log")).write_bytes(r.stdout);(control/(name+".stderr.log")).write_bytes(r.stderr)
 results.append(dict(case=name,argv=argv,exit_code=r.returncode,expected_exit_code=expected,pass_=r.returncode==expected,input_sha256=H(content)))
 assert r.returncode==expected,results[-1]
r=dict(executor="GPT Work independently recomputed public cache key and executed pinned scanner controls",reviewed_sha="5a5e093c2e9b39abe1332e49d1df40d20f9fd33f",scanner_version=version.stdout.strip(),scanner_executable_sha256=H(exe.read_bytes()),configuration_sha256=H((root/".gitleaks.toml").read_bytes()),verified_public_cache_digest=digest_value,script_sha256=H(Path(__file__).read_bytes()),results=results,real_credentials_used=False)
(out/"scanner-controls.json").write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in r.items() if k!="results"},indent=2));print(json.dumps([dict(case=x["case"],exit_code=x["exit_code"],pass_=x["pass_"]) for x in results],indent=2))

