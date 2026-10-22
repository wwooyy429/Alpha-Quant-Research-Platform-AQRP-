"""Seal current repair recheck; preserve original failures and both official raw ZIPs."""
import hashlib,json,subprocess,sys,zipfile
from pathlib import Path
from datetime import datetime,timezone
out=Path(__file__).resolve().parent;root=out.parent/"p3-recheck-9ac5db0"
SHA="9ac5db069287a6e4a095e25ae8c3cc8fa229cded"
VERDICT="G2 TECHNICAL PASS WITH CONDITIONS"
H=lambda b:hashlib.sha256(b).hexdigest()
J=lambda p:json.loads(p.read_bytes())
f=J(out/"finding-disposition.json")
assert len(f["findings"])==3 and all(x["status"]=="CLOSED" for x in f["findings"]) and f["new_blocking_code_findings"]==0
v=J(out/"sdk-verification.json")
assert v["junit"]==dict(tests=578,failures=0,errors=0,skipped=0)
assert v["new_reviewer_regressions"]["tests"]==4 and v["new_reviewer_regressions"]["failures"]==0
assert v["original_supplementary"]["passed"]==20 and v["new_independent_math"]==91
extra=J(out/"extra-verification.json")
assert extra["completed"] and extra["scanner_controls"]==3
assert J(out/"extra-verification-attempt1.json")["commands"][-1]["exit_code"]!=0
assert J(out/"scanner-controls-retry.command.json")["exit_code"]==0
assert J(out/"extras.command.json")["exit_code"]!=0
assert J(out/"clean-sdk.command.json")["exit_code"]==0
for name in ("scope","sdk-verification","ci-verification","archive-verification","end-verification","causal-wrapper","extras-finish","report-generation"):
 assert J(out/(name+".command.json"))["exit_code"]==0,name
a=J(out/"archive-verification.json")
assert a["manifest_members"]==319 and a["old_product_failures_preserved"]==4 and a["original_report_unchanged"]
pr=J(out/"pr5-end.json");assert pr["head"]["sha"]==SHA and "AQRP_FIXED_REVIEW_SHA: "+SHA in pr["body"] and not pr["merged"]
assert J(out/"after-causal-independent.json")["observed_future_leak"] is False
assert len(J(out/"requirement-coverage.json"))==26
report=out/"GPT-Work-Phase3-G2-9ac5db0-Recheck.md";handoff=out/"Codex-Phase3-G2-9ac5db0-Handoff.md"
assert all(x["id"] in report.read_text(encoding="utf-8") for x in f["findings"])
checks=[]
for p in (root,Path(r"C:/Users/11638/AppData/Local/AQRP/checkouts/phase1-57461d5d-5de2-4c78-9b4e-5fad2b5ccb29")):
 for args in (["rev-parse","HEAD"],["status","--porcelain=v1","--untracked-files=all"]):
  r=subprocess.run(["git","-C",str(p),*args],capture_output=True,text=True)
  assert r.returncode==0 and (r.stdout.strip()==SHA if args[0]=="rev-parse" else r.stdout=="")
  checks.append(dict(argv=["git","-C",str(p),*args],stdout=r.stdout,stderr=r.stderr,exit_code=r.returncode))
sdk=Path(v["sdk_root"]);selection=J(sdk/"upload-selection.json")
win=J(out/"artifact-12404165070/reproduction/environment-archive.json")
own=J(sdk/"reproduction/environment-archive.json")
dep_equal={(x["path"],x["sha256"]) for x in win["dependency_wheels"]}=={(x["path"],x["sha256"]) for x in own["dependency_wheels"]}
operation=dict(executable=sys.executable,argv=["-I",str(Path(__file__).resolve())],cwd=str(Path.cwd()),started_utc=datetime.now(timezone.utc).isoformat(),git_checks=checks,full_sdk_preserved_locally=True,own_windows_dependency_wheels_exact_duplicate_of_official_archive=dep_equal,not_a_full_virtual_environment_copy=True)
(out/"seal-operation.json").write_text(json.dumps(operation,ensure_ascii=False,indent=2),encoding="utf-8")
paths=set();omitted=[]
for p in out.iterdir():
 if p.is_file():
  if p.name!="REVIEW_EVIDENCE_MANIFEST.json":paths.add(p)
 elif p.name=="sdk":
  omitted.append(dict(path="sdk",reason="Full SDK remains local. Include selected immutable evidence below; omit duplicate source, virtual environments, caches and tool executables. Fixed-source.zip and original official raw CI ZIPs included."))
 elif "cache" in p.name or p.name=="__pycache__":
  omitted.append(dict(path=p.relative_to(out).as_posix(),reason="Transient test cache; original JUnit/stdout/scripts/public reproducer inputs included."))
 else:
  for q in p.rglob("*"):
   if q.is_file() and "__pycache__" not in q.parts and q.suffix!=".pyc":paths.add(q)
for x in selection["files"]:
 p=sdk/x["path"];assert H(p.read_bytes())==x["sha256"]
 if x["path"].startswith("reproduction/wheelhouse/"):
  omitted.append(dict(path=p.relative_to(out).as_posix(),bytes=p.stat().st_size,sha256=x["sha256"],reason="Exact duplicate Windows dependency bytes are in included official original ZIP; full local SDK retained." if dep_equal else "Locked wheel omitted from selected copy; full original local SDK retained."))
 else:paths.add(p)
paths.add(sdk/"upload-selection.json")
files=[]
for p in sorted(paths):
 b=p.read_bytes();files.append(dict(path=p.relative_to(out).as_posix(),bytes=len(b),sha256=H(b)))
manifest=dict(schema="gpt-work-primary-phase3-g2-repair-recheck-evidence/1",reviewed_sha=SHA,verdict=VERDICT,actual_executor="GPT Work primary actual independent recheck; not Gemini/developer",self_excluded=True,findings_closed=3,new_blocking_code_findings=0,phase3_user_accepted=False,included_original_ci_archives=[x["artifact_id"] for x in J(out/"ci-verification.json")["artifacts"]],full_sdk_selected_evidence_only=True,previous_original_evidence=dict(path=a["original_zip_path"],bytes=a["original_zip_bytes"],sha256=a["original_zip_sha256"],original_files=319,not_duplicated_in_current_zip=True,verification="archive-verification.json"),failed_helper_attempt_preserved=True,omitted_local_files_or_trees=omitted,files=files)
mb=json.dumps(manifest,ensure_ascii=False,indent=2).encode()
(out/"REVIEW_EVIDENCE_MANIFEST.json").write_bytes(mb)
target=out.parent/"GPT-Work-P3-G2-9ac5db0-Evidence.zip"
assert not target.exists(),"Never silently overwrite an already sealed archive"
with zipfile.ZipFile(target,"w",zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for x in files:z.write(out/x["path"],x["path"])
 z.writestr("REVIEW_EVIDENCE_MANIFEST.json",mb)
with zipfile.ZipFile(target) as z:
 assert z.testzip() is None and set(z.namelist())=={x["path"] for x in files}|{"REVIEW_EVIDENCE_MANIFEST.json"}
 for x in files:
  b=z.read(x["path"]);assert len(b)==x["bytes"] and H(b)==x["sha256"]
 assert z.read("REVIEW_EVIDENCE_MANIFEST.json")==mb
receipt=dict(reviewed_sha=SHA,verdict=VERDICT,completed_utc=datetime.now(timezone.utc).isoformat(),zip_path=str(target.resolve()),zip_bytes=target.stat().st_size,zip_sha256=H(target.read_bytes()),manifest_files=len(files),manifest_sha256=H(mb),zip_crc="PASS",members_exact=True,report_sha256=H(report.read_bytes()),handoff_sha256=H(handoff.read_bytes()),original_raw_ci_zips_included=True,full_sdk_selected_evidence_only=True,findings_closed=3,new_blocking_code_findings=0,clean_sdk_passed=578,original_four_passed=4,original20_passed=20,independent_math_passed=91,scanner_controls_passed=3,reviewer_premature_scanner_helper_failure_preserved=True,previous_evidence_zip_sha256=a["original_zip_sha256"],formal_repository_modified=False,phase3_user_accepted=False,deployed=False,merged=False,tagged=False,p4=False)
(out.parent/"GPT-Work-P3-G2-9ac5db0-Seal.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(receipt,ensure_ascii=False,indent=2))

