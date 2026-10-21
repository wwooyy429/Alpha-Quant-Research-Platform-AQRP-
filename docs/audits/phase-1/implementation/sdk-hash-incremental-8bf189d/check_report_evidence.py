from pathlib import Path
import hashlib,json,zipfile,subprocess,csv
from fractions import Fraction
from decimal import Decimal,localcontext
from xml.etree import ElementTree
repo=Path("C:\\Users\\11638\\AppData\\Local\\AQRP\\checkouts\\phase1-57461d5d-5de2-4c78-9b4e-5fad2b5ccb29")
out=Path("C:\\Users\\11638\\AppData\\Local\\AQRP\\runs\\sdk-incremental-reconciliation-1792529096498")
out.mkdir()
userdir=Path(r"B:\BaiduSyncdisk\学习\投资\量化\量化交易比赛\审查")
report=userdir/"aqrp_phase1_sdk_hash_incremental_recheck_report.md"
def sha(raw):return hashlib.sha256(raw).hexdigest()
def git(*args):return subprocess.check_output(["git",*args],cwd=repo,text=True).strip()
def canon(obj):return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode()
result={"date":"2026-10-21","execution_by":"Codex developer report reconciliation; not Gemini execution",
        "reviewed_sha":"8bf189d76f15273a89eb4c2672c86e05a81aa148",
        "business_sha":"74bdb9216c585d27de91123605aff0266ca028cc",
        "new_report_sha256":sha(report.read_bytes()),"new_report_bytes":report.stat().st_size,
        "git_scope_8bf_vs_d825":git("diff","--name-only","d82536ae9ac7f61153747e63d044a640fea17b50","8bf189d76f15273a89eb4c2672c86e05a81aa148").splitlines()}
prior=repo/"docs/audits/phase-1/implementation/SDK_HASH_MANIFEST.json"
manifest=json.loads(prior.read_bytes())
assert all(sha((repo/f["path"]).read_bytes())==f["sha256"] for f in manifest["files"])
result["prior_8bf_manifest_checks"]={"files":len(manifest["files"]),"all_match":True}
idx=json.loads((repo/"docs/audits/phase-1/gemini/SDK_HASH_VERIFICATION_INDEX.json").read_bytes())
rawreport=repo/"docs/audits/phase-1/gemini/aqrp_phase1_sdk_and_remote_hash_verification_report.md"
assert sha(rawreport.read_bytes())==idx["sha256"]
assert all(sha((repo/f["path"]).read_bytes())==f["sha256"] for f in idx["raw_evidence"])
result["original_report_and_five_evidence_hashes"]="PASS"
assert not git("diff",result["business_sha"],"--","src","tests","tools",".github/workflows/ci.yml","requirements.lock","pyproject.toml",".python-version",".gitleaks.toml")
frozen=json.loads((repo/"docs/audits/phase-1/implementation/CORE_PRESERVATION.json").read_bytes())
assert all(sha((repo/f["path"]).read_bytes())==f["sha256"] for f in frozen["files"])
with (repo/"docs/requirements.csv").open(encoding="utf-8",newline="") as f:
    req=list(csv.DictReader(f))
assert len(req)==106 and len({r["id"].rsplit("-",1)[0] for r in req})==16
result["protected_assets"]={"business_code_tests_tools_ci_locks_unchanged":True,"phase0_files":len(frozen["files"]),"requirements":106,"groups":16}
dev=repo/"docs/audits/phase-1/implementation/sdk-hash-74bdb92"
expected={
12288989083:"73385602dad830f3157dba8f5629616127777511830b02675fd06df517f93e7c",
12288679676:"8f092b7214202292995276a4dab3187063cd481d8a6556ac342e450738b64ea5"}
items=[]
smoke_bytes=[]
for aid,digest in expected.items():
    zpath=dev/f"{aid}.zip"
    assert sha(zpath.read_bytes())==digest
    with zipfile.ZipFile(zpath) as z:
        assert z.testzip() is None
        names=z.namelist()
        assert len(names)==len(set(names)) and all(".." not in Path(n).parts for n in names)
        indexname=next(n for n in names if n.endswith("/artifacts.json"))
        prefix=indexname.removesuffix("artifacts.json")
        index=json.loads(z.read(indexname))
        verified=[];missing=[]
        for rec in index:
            name=prefix+rec["path"]
            if name in names:
                assert sha(z.read(name))==rec["sha256"]
                verified.append(rec["path"])
            else:missing.append(rec["path"])
        assert len(index)==14 and len(verified)==11
        assert set(missing)=={".coverage","pip-26.2.1-py3-none-any.whl","gitleaks.exe" if aid==12288679676 else "gitleaks"}
        assert "artifacts.json" not in {r["path"] for r in index}
        assert not any(r["path"].startswith("dataset") or r["path"]=="aqrp-0.1.0-py3-none-any.whl" for r in index)
        run=json.loads(z.read(prefix+"smoke-run.json"))
        config=json.loads(z.read(prefix+"smoke-config.json"))
        data=z.read(prefix+"smoke-result.json")
        assert sha(data)==run["result_hash"]=="70202a124f458f829caa5ac72e136d9c40c76801a63f113aec9863d3bed864d6"
        assert sha(canon(config))==run["config_hash"]
        assert "command-log.txt" not in {n.removeprefix(prefix) for n in names}
        assert "smoke-receipt.json" not in {n.removeprefix(prefix) for n in names}
        sman=json.loads(z.read(prefix+"smoke-snapshot.json"))
        actual_manifest=z.read(prefix+"dataset/"+run["snapshot_id"]+"/manifest.json")
        assert actual_manifest==z.read(prefix+"smoke-snapshot.json")
        assert sha(canon({k:v for k,v in sman.items() if k not in ("snapshot_id","manifest_hash")}))==run["manifest_hash"]
        tablehashes=[]
        for t,entry in sman["tables"].items():
            name=prefix+"dataset/"+run["snapshot_id"]+"/"+entry["path"]
            assert sha(z.read(name))==entry["sha256"]
            tablehashes.append({"table":t,"sha256":entry["sha256"],"pass":True})
        suites=list(ElementTree.fromstring(z.read(prefix+"junit.xml")).iter("testsuite"))
        junit={k:sum(int(s.attrib.get(k,0)) for s in suites) for k in ("tests","failures","errors","skipped")}
        assert junit=={"tests":102,"failures":0,"errors":0,"skipped":0}
        env=json.loads(z.read(prefix+"environment.json"))
        assert env["code_commit"]==env["github_sha"]=="f093faca9a9dd4977caa1142267ff494766d3c7e"
        smoke_bytes.append(data)
        items.append({"artifact_id":aid,"sha256":digest,"zip_bytes":zpath.stat().st_size,"verified_root_paths":verified,"missing_root_paths":missing,"root_entries":len(index),"actual_uploaded_root_members":sorted(n.removeprefix(prefix) for n in names if "/" not in n.removeprefix(prefix)),"project_wheel_hash_location":"environment.json.wheel_sha256; not artifacts.json","tables":tablehashes,"junit":junit,"result_sha256":run["result_hash"],"query_config_keys":sorted(config)})
result["artifacts"]=items
assert smoke_bytes[0]==smoke_bytes[1]
result["cross_os_smoke_bytes_match"]=True
merge="f093faca9a9dd4977caa1142267ff494766d3c7e"
assert git("rev-parse",merge+"^{tree}")==git("rev-parse",result["business_sha"]+"^{tree}")=="66dc03a5cf38e8db9968873f2a0f1349b45eda09"
result["merge_tree"]="66dc03a5cf38e8db9968873f2a0f1349b45eda09"
result["merge_parents"]=git("show","-s","--format=%P",merge).split()
errors={}
for val,ref in [(0.05,Fraction(1,20)),(0.1,Fraction(1,10))]:
    err=abs(Fraction.from_float(val)-ref)
    with localcontext() as ctx:
        ctx.prec=60
        dec=str(Decimal(err.numerator)/Decimal(err.denominator))
    errors[str(val)]={"exact_fraction":str(err),"absolute_error":dec,"within_original_tolerances":err<Fraction(1,10**12) and err/ref<Fraction(1,10**10)}
result["exact_float_errors"]=errors
result["new_reviewer_execution_attachments"]="None newly supplied beyond incremental report; original five files are previous round"
result["checks_passed"]=True
(out/"checks.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
print(json.dumps({"new_report_sha256":result["new_report_sha256"],"zip_checks":"2 PASS","root_hashes":"11/14 each, actual names captured","original_evidence":"6 hashes match","protected_assets":result["protected_assets"],"prior_manifest":"223 match","new_gemini_raw_execution_logs":"not supplied"},ensure_ascii=False))
