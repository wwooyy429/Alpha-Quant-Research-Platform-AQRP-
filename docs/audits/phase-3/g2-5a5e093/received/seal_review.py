"""Seal fixed-SHA reviewer evidence. Preserve raw original ZIPs and actual product failures."""
import hashlib,json,os,subprocess,sys,zipfile
from datetime import datetime,timezone
from pathlib import Path
out=Path(__file__).resolve().parent;root=out.parent/"p3-implementation-5a5e093"
SHA="5a5e093c2e9b39abe1332e49d1df40d20f9fd33f"
H=lambda b:hashlib.sha256(b).hexdigest();J=lambda p:json.loads(p.read_bytes())
findings=J(out/"finding-disposition.json");assert len(findings["findings"])==3 and [f["severity"] for f in findings["findings"]]==["High","Medium","Medium"]
sdkv=J(out/"sdk-verification.json");assert sdkv["junit"]["tests"]==564 and sdkv["junit"]["failures"]==0 and sdkv["original_supplementary"]["passed"]==20 and sdkv["new_reviewer_regressions"]["failures"]==4 and sdkv["new_independent_math"]==91
assert J(out/"scope.command.json")["exit_code"]!=0 and J(out/"scope-final.command.json")["exit_code"]==0
assert J(out/"reviewer-regressions.command.json")["exit_code"]==1
assert J(out/"clean-sdk.command.json")["exit_code"]==0
assert J(out/"scanner-controls.json")["results"] and all(r["pass_"] for r in J(out/"scanner-controls.json")["results"])
pr=J(out/"pr5-end.json");assert pr["head"]["sha"]==SHA and "AQRP_FIXED_REVIEW_SHA: "+SHA in pr["body"] and not pr["merged"]
rpt=(out/"GPT-Work-Phase3-G2-5a5e093-Review.md").read_text(encoding="utf-8");assert all(f["id"] in rpt for f in findings["findings"]) and SHA in rpt
checks=[]
for path in (root,Path(r"C:\Users\11638\AppData\Local\AQRP\checkouts\phase1-57461d5d-5de2-4c78-9b4e-5fad2b5ccb29")):
 for args in (["rev-parse","HEAD"],["status","--porcelain=v1","--untracked-files=all"]):
  r=subprocess.run(["git","-C",str(path),*args],capture_output=True,text=True);assert r.returncode==0 and (r.stdout.strip()==SHA if args[0]=="rev-parse" else r.stdout=="")
  checks.append(dict(argv=["git","-C",str(path),*args],stdout=r.stdout,stderr=r.stderr,exit_code=r.returncode))
sdk=Path(sdkv["sdk_root"]);selection=J(sdk/"upload-selection.json");winenv=J(out/"artifact-12385054743/reproduction/environment-archive.json");ownenv=J(sdk/"reproduction/environment-archive.json")
dep_equal={(r["path"],r["sha256"]) for r in winenv["dependency_wheels"]}=={(r["path"],r["sha256"]) for r in ownenv["dependency_wheels"]}
operation=dict(executable=sys.executable,argv=["-I",str(Path(__file__).resolve())],cwd=str(Path.cwd()),started_utc=datetime.now(timezone.utc).isoformat(),git_checks=checks,own_windows_dependency_wheels_exact_duplicate_of_official_archive=dep_equal,full_sdk_preserved_locally=True,not_a_full_virtual_environment_copy=True)
(out/"seal-operation.json").write_text(json.dumps(operation,ensure_ascii=False,indent=2),encoding="utf-8")
paths=set();omitted=[]
for p in out.iterdir():
 if p.is_file():
  if p.name!="REVIEW_EVIDENCE_MANIFEST.json":paths.add(p)
 elif p.name=="sdk":
  omitted.append(dict(path=p.relative_to(out).as_posix(),reason="Full SDK retained locally. Package only immutable selected evidence below; omit source duplicate, venvs, caches and tool executables. Fixed-source.zip and official original CI ZIPs included."))
 elif "pytest" in p.name or p.name=="__pycache__":
  omitted.append(dict(path=p.relative_to(out).as_posix(),reason="Transient reviewer pytest/caches; actual JUnit/stdout and public reproducer fixtures included."))
 else:
  for q in p.rglob("*"):
   if q.is_file() and "__pycache__" not in q.parts and q.suffix!=".pyc":paths.add(q)
for row in selection["files"]:
 p=sdk/row["path"];assert H(p.read_bytes())==row["sha256"]
 if row["path"].startswith("reproduction/wheelhouse/"):
  omitted.append(dict(path=p.relative_to(out).as_posix(),sha256=row["sha256"],bytes=p.stat().st_size,reason="Duplicate locked dependency wheel; full local SDK preserved, exact same Windows official original ZIP bytes included." if dep_equal else "Locked binary copy omitted from selected SDK evidence; full local SDK preserved with original hash."))
 else:paths.add(p)
paths.add(sdk/"upload-selection.json")
files=[]
for p in sorted(paths):
 b=p.read_bytes();files.append(dict(path=p.relative_to(out).as_posix(),bytes=len(b),sha256=H(b)))
manifest=dict(schema="gpt-work-primary-phase3-implementation-review-evidence/1",reviewed_sha=SHA,verdict="G2 REQUEST CHANGES / IMPLEMENTATION BLOCKED",self_excluded=True,actual_executor="GPT Work primary independent review; not Gemini",findings=dict(High=1,Medium=2),included_original_ci_archives=[r["artifact_id"] for r in J(out/"ci-verification.json")["artifacts"]],full_sdk_selected_evidence_only=True,omitted_local_files_or_trees=omitted,reviewer_helper_failed_attempts_preserved=["scope.command.json","scope.stderr.log","verify_scope-attempt1.py"],product_failures_preserved=["reviewer-regressions.command.json","reviewer-regressions.stdout.log","reviewer-regressions.xml"],files=files)
mb=json.dumps(manifest,ensure_ascii=False,indent=2).encode()
(out/"REVIEW_EVIDENCE_MANIFEST.json").write_bytes(mb)
target=out.parent/"GPT-Work-P3-G2-5a5e093-Evidence.zip"
with zipfile.ZipFile(target,"w",zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for f in files:z.write(out/f["path"],f["path"])
 z.writestr("REVIEW_EVIDENCE_MANIFEST.json",mb)
with zipfile.ZipFile(target) as z:
 assert z.testzip() is None
 assert set(z.namelist())=={f["path"] for f in files}|{"REVIEW_EVIDENCE_MANIFEST.json"}
 for f in files:
  b=z.read(f["path"]);assert len(b)==f["bytes"] and H(b)==f["sha256"]
 assert z.read("REVIEW_EVIDENCE_MANIFEST.json")==mb
receipt=dict(reviewed_sha=SHA,verdict="G2 REQUEST CHANGES / IMPLEMENTATION BLOCKED",completed_utc=datetime.now(timezone.utc).isoformat(),zip_path=str(target.resolve()),zip_bytes=target.stat().st_size,zip_sha256=H(target.read_bytes()),manifest_files=len(files),manifest_sha256=H(mb),zip_crc="PASS",members_exact=True,report_sha256=H((out/"GPT-Work-Phase3-G2-5a5e093-Review.md").read_bytes()),tasks_sha256=H((out/"Codex-Phase3-G2-5a5e093-Fix-Tasks.md").read_bytes()),original_raw_ci_zips_included=True,full_sdk_selected_evidence_only=True,actual_product_regressions_failed=4,reviewer_scope_helper_failure_preserved=True,formal_repository_modified=False,deployed=False,merged=False,tagged=False,p4=False)
(out.parent/"GPT-Work-P3-G2-5a5e093-Seal.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(receipt,ensure_ascii=False,indent=2))

