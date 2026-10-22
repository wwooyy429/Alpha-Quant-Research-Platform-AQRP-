"""Verify reviewer clean SDK result and collect per-module coverage/identity."""
import hashlib,io,json,sys,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
out=Path(__file__).resolve().parent;root=Path(sys.argv[1]).resolve();sdk=next((out/"sdk").iterdir());H=lambda b:hashlib.sha256(b).hexdigest()
J=lambda p:json.loads(p.read_bytes())
env=J(sdk/"environment.json");assert env["complete"] and not env["dirty"] and env["code_commit"]=="9ac5db069287a6e4a095e25ae8c3cc8fa229cded"
selection=J(sdk/"upload-selection.json")
for row in selection["files"]:assert H((sdk/row["path"]).read_bytes())==row["sha256"]
xml=ET.parse(sdk/"junit.xml");cases=xml.findall(".//testcase");assert len(cases)==578 and all(not any(c.findall(t)) for c in cases for t in ("failure","error","skipped"))
w=next((sdk/"wheel").glob("*.whl"));assert H(w.read_bytes())==env["wheel_sha256"]
with zipfile.ZipFile(w) as z:
 local={"aqrp/"+p.relative_to(root/"src/aqrp").as_posix():p for p in (root/"src/aqrp").rglob("*.py")}
 assert {n for n in z.namelist() if n.endswith(".py")}==set(local)
 for n,p in local.items():assert z.read(n)==p.read_bytes()
 assert z.read("aqrp/factors/reviewed_code.json")==(root/"src/aqrp/factors/reviewed_code.json").read_bytes()
coverage=J(sdk/"coverage.json");stats=[]
critical={"time.py","units.py","pit.py","actions.py","snapshot.py","environment.py","exposures.py","numerics.py","pipeline.py","ledger.py","reproduction.py"}
for f,v in coverage["files"].items():
 s=v["summary"];normalized=f.replace("\\","/");basename=normalized.split("/")[-1]
 line=100*s["covered_lines"]/max(1,s["num_statements"]);branch=100*s["covered_branches"]/s["num_branches"] if s["num_branches"] else 100
 strict=basename in critical or "/core/security/" in normalized or "/validation/" in normalized or normalized.endswith("/services/research.py") or ("/factors/" in normalized and basename in {"contracts.py","input.py","admission.py","builtins.py","engine.py"})
 threshold=(95,90) if strict else (90,85);assert not s["num_statements"] or (line>=threshold[0] and branch>=threshold[1]),f
 if any("/"+p+"/" in normalized for p in ("research","validation","experiments","services")) or basename in ("environment.py","exposures.py"):stats.append(dict(file=normalized,line=line,branch=branch,required=threshold))
original=ET.parse(out/"original20.xml").findall(".//testcase");assert len(original)==20 and not any(c.findall("failure")+c.findall("error")+c.findall("skipped") for c in original)
reg=ET.parse(out/"original-four.xml").findall(".//testcase");assert len(reg)==4 and all(not any(c.findall(t)) for c in reg for t in ("failure","error","skipped"))
def same_copy(a,b):assert a.read_bytes()==b.read_bytes()
for name,src in (("test_work_p1_regressions.py","docs/audits/phase-1/repairs/data-validation/review-input/test_work_p1_regressions.py"),("test_round2_regressions.py","docs/audits/phase-1/repairs/data-validation/round2/review-input/test_round2_regressions.py"),("test_work_p2_regressions.py","docs/audits/phase-2/recheck-c836/raw/test_work_p2_regressions.py")):same_copy(out/"original-probes"/name,root/src)
old=J(sdk/"reproduction/published-original-replay.json");assert len(old["verified_original_files"])==66 and len(old["runs"])==3
r=dict(reviewed_sha=env["code_commit"],executor="GPT Work independently executed full clean installed SDK",sdk_root=str(sdk.resolve()),environment=env,selected_files_verified=len(selection["files"]),junit=dict(tests=578,failures=0,errors=0,skipped=0),original_supplementary=dict(p1=16,p2=4,passed=20,sources_byte_unchanged=True),new_reviewer_regressions=dict(tests=4,failures=0,errors=0,scope="Unmodified original four reviewer regressions now pass"),new_independent_math=J(out/"independent-implementation-math.json")["passed"],wheel=dict(path=str(w.resolve()),sha256=H(w.read_bytes()),source_modules_exact=45),coverage_totals=coverage["totals"],p3_coverage=stats,old_files=66,old_runs=3,locked_dependency_wheels=len(list((sdk/"reproduction/wheelhouse").glob("*.whl"))))
(out/"sdk-verification.json").write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in r.items() if k not in ("p3_coverage","environment")},ensure_ascii=False,indent=2))

