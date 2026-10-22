"""Run original immutable reviewer scripts against the new installed wheel."""
import hashlib,json,os,shutil,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
out=Path(__file__).resolve().parent;root=Path(sys.argv[1]).resolve();sdk=next((out/"sdk").iterdir());py=sdk/"venv/Scripts/python.exe"
H=lambda b:hashlib.sha256(b).hexdigest();received=root/"docs/audits/phase-3/g2-5a5e093/received"
copies=[("test_review_regressions.py","798005e905817b322d723bb261efac9d6f4d83b284bde82d99f0724dff53c788"),("independent_implementation_math.py","8838c9153ca914ad257849a2c7b26c468f15a8ad2e5c1dab7bf683ada60056c3"),("verify_scanner_controls.py","97d1e9ee47e31bc8e3a647e76135c9a8d8f1aaa0e45e51520f6e81e00043ef83")]
for name,sha in copies:
 b=(received/name).read_bytes();assert H(b)==sha;(out/name).write_bytes(b)
original=out/"original-probes";original.mkdir(exist_ok=True)
for name,path in (("test_work_p1_regressions.py","docs/audits/phase-1/repairs/data-validation/review-input/test_work_p1_regressions.py"),("test_round2_regressions.py","docs/audits/phase-1/repairs/data-validation/round2/review-input/test_round2_regressions.py"),("test_work_p2_regressions.py","docs/audits/phase-2/recheck-c836/raw/test_work_p2_regressions.py")):
 shutil.copyfile(root/path,original/name)
for rel in ("source/tests/golden/phase1_input.json","phase1/tests/golden/phase1_input.json"):
 p=original/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/"tests/golden/phase1_input.json",p)
record=dict(reviewed_sha="9ac5db069287a6e4a095e25ae8c3cc8fa229cded",actual_executor="GPT Work independent current rerun, not developer",interpreter=str(py.resolve()),started_utc=datetime.now(timezone.utc).isoformat(),original_scripts_byte_unchanged=[dict(path=n,sha256=h) for n,h in copies],legacy_label_note="Original 91-math/scanner script printed old5a SHA/GPT Work label is an immutable inherited source label. Actual new target/executor/source identity recorded here and in installed identity check.",completed=False,commands=[])
def save(): (out/"extra-verification.json").write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
def run(name,args):
 start=datetime.now(timezone.utc).isoformat();r=subprocess.run([str(py),*args],capture_output=True,cwd=out)
 (out/(name+".stdout.log")).write_bytes(r.stdout);(out/(name+".stderr.log")).write_bytes(r.stderr)
 c=dict(name=name,executable=str(py.resolve()),argv=args,cwd=str(out),started_utc=start,ended_utc=datetime.now(timezone.utc).isoformat(),exit_code=r.returncode)
 record["commands"].append(c);(out/(name+".command.json")).write_text(json.dumps(c,ensure_ascii=False,indent=2),encoding="utf-8");save()
 assert r.returncode==0,(name,r.stderr.decode("utf-8","replace")[-2000:])
 return r.stdout
identity=json.loads(run("installed-identity",["-I","-c","import json,aqrp; from aqrp.factors.admission import bundle_hash; print(json.dumps(dict(module_file=aqrp.__file__,bundle_sha256=bundle_hash())))"]))
assert identity["bundle_sha256"]=="3cec8a9da49a49a93010d7fa6a2012dded25185e2cdca49144cf4d719d56876e";record["installed_identity"]=identity;save()
run("original-four",["-I","-m","pytest",str(out/"test_review_regressions.py"),"-q","-o","cache_dir="+str(out/"original-four-cache"),"--basetemp",str(out/"original-four-temp"),"--junitxml="+str(out/"original-four.xml")])
run("original20",["-I","-m","pytest",*[str(original/n) for n in ("test_work_p1_regressions.py","test_round2_regressions.py","test_work_p2_regressions.py")],"-q","-o","cache_dir="+str(out/"original20-cache"),"--basetemp",str(out/"original20-temp"),"--junitxml="+str(out/"original20.xml")])
run("independent-math",["-I",str(out/"independent_implementation_math.py")])
assert json.loads((out/"independent-implementation-math.json").read_bytes())["passed"]==91
run("scanner-controls",["-I",str(out/"verify_scanner_controls.py"),str(root)])
assert all(r["pass_"] for r in json.loads((out/"scanner-controls.json").read_bytes())["results"])
record.update(completed=True,completed_utc=datetime.now(timezone.utc).isoformat(),original_four="4 passed",original20="20 passed",independent_math=91,scanner_controls=3);save()
print(json.dumps({k:v for k,v in record.items() if k!="commands"},ensure_ascii=False,indent=2))

