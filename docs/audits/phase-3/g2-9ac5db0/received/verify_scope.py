import csv,hashlib,json,subprocess,sys,zipfile
from pathlib import Path
out=Path(__file__).resolve().parent;root=Path(sys.argv[1]).resolve()
SHA="9ac5db069287a6e4a095e25ae8c3cc8fa229cded";G1="3861ef1637bc2b4c28725d7afc5f2e1f02242e80";BASE="f26255fc40a3080bfa883ad64938f60036a14759"
def H(b):return hashlib.sha256(b).hexdigest()
def J(p):return json.loads(p.read_bytes())
cmds=[]
def git(*args):
 p=subprocess.run(["git","-C",str(root),*args],capture_output=True)
 cmds.append(dict(argv=["git","-C",str(root),*args],exit_code=p.returncode,stdout=p.stdout.decode("utf-8","replace"),stderr=p.stderr.decode("utf-8","replace")));assert p.returncode==0
 return p.stdout
assert git("rev-parse","HEAD").decode().strip()==SHA
assert git("status","--porcelain")==b""
identity=J(root/"docs/audits/phase-3/IMPLEMENTATION_IDENTITY.json")
for row in identity["frozen_files"]:
 p=root/row["path"];assert p.is_file() and H(p.read_bytes())==row["sha256"],row["path"]
manifest=J(root/"docs/audits/phase-3/FILE_MANIFEST.json")
for row in manifest["files"]:
 p=root/"docs/audits/phase-3"/row["path"];assert p.is_file() and p.stat().st_size==row["bytes"] and H(p.read_bytes())==row["sha256"],row["path"]
rows=list(csv.DictReader((root/"docs/requirements.csv").open(encoding="utf-8-sig",newline="")))
assert len(rows)==106 and len({r["id"].split('-')[0] for r in rows})==16
p3=[r for r in rows if r["phase"]=="3"];assert len(p3)==26 and sum(r["tier"]=="MVP" for r in p3)==23
assert H((root/"docs/requirements.csv").read_bytes())==identity["requirements_sha256"]
assert (root/"docs/requirements.csv").read_bytes()==git("show",G1+":docs/requirements.csv")
assert (root/"requirements.lock").read_bytes()==git("show",BASE+":requirements.lock")
for name in ("golden_cases.json","supplemental_cases.json","label_visibility_v2.json","hac_growth_cases.json","reference_arithmetic.py","supplemental_reference.py","recheck_reference_v2.py"):
 rel="docs/audits/phase-3/"+name;assert git("show",G1+":"+rel)==(root/rel).read_bytes()
modules=[dict(path=p.relative_to(root/"src/aqrp").as_posix(),sha256=H(p.read_bytes())) for p in sorted((root/"src/aqrp").rglob("*.py"))]
assert len(modules)==45 and identity["code_bundle_manifest"]["files"]==modules
c=lambda o:json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode()
assert H(c(identity["code_bundle_manifest"]))==identity["code_bundle_sha256"]=="3cec8a9da49a49a93010d7fa6a2012dded25185e2cdca49144cf4d719d56876e"
assert H((root/"src/aqrp/factors/reviewed_code.json").read_bytes())==identity["receipt_sha256"]
unchanged=git("diff","--name-only","1b4be236e888805f5c4e45357b158fcdb6058df0",SHA,"--","src","tests","tools",".github","requirements.lock","pyproject.toml")
assert unchanged==b""
merge=J(out/"ci-merge.json")
assert git("rev-parse","HEAD^{tree}").decode().strip()==merge["commit"]["tree"]["sha"]
archive=subprocess.run(["git","-C",str(root),"archive","--format=zip",SHA],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
assert archive.returncode==0
(out/"fixed-source.zip").write_bytes(archive.stdout)
r=dict(reviewed_sha=SHA,baseline=BASE,g1=G1,canonical=106,groups=16,phase3=26,MVP=23,CR=3,frozen_files=len(identity["frozen_files"]),p3_manifest=len(manifest["files"]),source_modules=45,source_bundle=identity["code_bundle_sha256"],lock_sha256=identity["lock_sha256"],business_tree_scoped_equal=True,actual_ci_checkout=merge["sha"],whole_ci_tree_equal_fixed=True,fixed_source_archive_sha256=H(archive.stdout),new_gitleaks_delta=git("diff","1b4be236e888805f5c4e45357b158fcdb6058df0",SHA,"--",".gitleaks.toml").decode(),commands=cmds)
(out/"scope-verification.json").write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
(out/"canonical-phase3.csv").write_text("\n".join(",".join('"'+str(r.get(k,"")).replace('"','""')+'"' for k in rows[0]) for r in [dict(zip(rows[0],rows[0])),*p3]),encoding="utf-8")
for id in (12403373418,12404165070):
 with zipfile.ZipFile(out/f"artifact-{id}.zip") as z:print(json.dumps(dict(id=id,members=len(z.namelist()),first=z.namelist()[:8]),ensure_ascii=False))
print(json.dumps({k:v for k,v in r.items() if k not in ("commands","new_gitleaks_delta")},indent=2))

