"""One requested Conda execution, all logs outside source; no main/tag mutations."""
import json,subprocess,os,sys,hashlib,time,shutil
from pathlib import Path
from xml.etree import ElementTree
ROOT=Path("C:\\Users\\11638\\AppData\\Local\\AQRP\\runs\\conda-vscode-1792572943050"); REPO=Path("C:\\Users\\11638\\AppData\\Local\\AQRP\\checkouts\\phase1-57461d5d-5de2-4c78-9b4e-5fad2b5ccb29")
CONDA=Path(r"E:\WORK\Anaconda\Scripts\conda.exe")
PREFIX=Path(r"E:\WORK\Anaconda\envs\aqrp-p1")
SOURCE=ROOT/"source-74bdb92"
TARGET="74bdb9216c585d27de91123605aff0266ca028cc"
ENTRY_SHA="7f4981b86fae7e293de8424a2631a873d90a62f3"
ENV=dict(os.environ,PYTHONUTF8="1",PYTHONPYCACHEPREFIX=str(ROOT/"bytecode"),PIP_CACHE_DIR=str(ROOT/"pip-cache"))
ENV.pop("PYTHONPATH",None)
commands=[]
summary={"performed_by":"Codex developer on user's Windows machine, not Gemini","business_sha":TARGET,"prior_archive_sha":ENTRY_SHA,"conda_prefix":str(PREFIX),"complete":False,"main_merge_tag_phase2_authorized":False}
def save():
 (ROOT/"execution.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8",newline="\n")
def command(label,args,cwd=ROOT,env=None):
 print(label+": START",flush=True)
 start=time.monotonic()
 with (ROOT/(label+".log")).open("w",encoding="utf-8") as log:
  r=subprocess.run([str(a) for a in args],cwd=cwd,env=env or ENV,stdout=log,stderr=subprocess.STDOUT)
 commands.append({"label":label,"args":[str(a) for a in args],"cwd":str(cwd),"exit_code":r.returncode,"seconds":round(time.monotonic()-start,2),"log":label+".log"})
 (ROOT/"commands.json").write_text(json.dumps(commands,indent=2)+"\n",encoding="utf-8",newline="\n")
 print(label+": EXIT "+str(r.returncode),flush=True)
 if r.returncode:
  summary["failed_command"]=label;save()
  print((ROOT/(label+".log")).read_text(encoding="utf-8",errors="replace")[-5000:],flush=True)
  raise SystemExit(r.returncode)
 return ROOT/(label+".log")
def conda(*args):
 return [CONDA,"run","--no-capture-output","--prefix",PREFIX,*args]
def read_probe(label):
 p=command(label,conda("python","-X","utf8",ROOT/"runtime_probe.py"))
 obj=json.loads(p.read_text(encoding="utf-8-sig"))
 (ROOT/(label+".json")).write_text(json.dumps(obj,indent=2)+"\n",encoding="utf-8",newline="\n")
 assert obj["version"]==[3,13,16] and obj["is_64_bit"] and not obj["gil_disabled"] and obj["implementation"]=="CPython"
 return obj
def junit(p):
 suites=list(ElementTree.fromstring(p.read_bytes()).iter("testsuite"))
 data={k:sum(int(s.attrib.get(k,0)) for s in suites) for k in ("tests","failures","errors","skipped")}
 assert data=={"tests":102,"failures":0,"errors":0,"skipped":0}
 return data
try:
 save()
 summary["before"]=read_probe("conda-before")
 command("clone-fixed-source",["git","clone","--no-hardlinks","--no-checkout",REPO,SOURCE])
 command("longpaths",["git","config","core.longpaths","true"],cwd=SOURCE)
 command("checkout-fixed",["git","checkout","--detach",TARGET],cwd=SOURCE)
 assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=SOURCE,text=True).strip()==TARGET
 command("conda-install-lock",conda("python","-X","utf8","-m","pip","--isolated","install","--index-url","https://pypi.org/simple","--require-hashes","--only-binary=:all:","-r",SOURCE/"requirements.lock"))
 command("conda-pip-check",conda("python","-X","utf8","-m","pip","check"))
 summary["lock_sha256"]=hashlib.sha256((SOURCE/"requirements.lock").read_bytes()).hexdigest()
 formal_env=dict(ENV,AQRP_RUN_ROOT=str(ROOT/"formal-sdk"))
 command("formal-clean-sdk",conda("python","-X","utf8",SOURCE/"tools/ci.py"),cwd=SOURCE,env=formal_env)
 runs=list((ROOT/"formal-sdk").glob("aqrp-*"));assert len(runs)==1
 formal=runs[0]
 formal_meta=json.loads((formal/"environment.json").read_bytes())
 assert formal_meta["complete"] and not formal_meta["dirty"] and formal_meta["code_commit"]==TARGET
 summary["formal"]={"run_root":str(formal),"environment":formal_meta,"junit":junit(formal/"junit.xml")}
 wheel=next((formal/"wheel").glob("aqrp-*.whl"))
 assert hashlib.sha256(wheel.read_bytes()).hexdigest()==formal_meta["wheel_sha256"]
 command("conda-install-project-wheel",conda("python","-X","utf8","-m","pip","install","--no-index","--no-deps",wheel))
 after=read_probe("conda-after")
 assert after["aqrp_import_path"] and str(PREFIX).lower() in after["aqrp_import_path"].lower()
 summary["after"]=after
 command("conda-pip-check-final",conda("python","-X","utf8","-m","pip","check"))
 direct=ROOT/"conda-direct";direct.mkdir()
 d_env=dict(ENV,COVERAGE_FILE=str(direct/".coverage"),HYPOTHESIS_STORAGE_DIRECTORY=str(direct/"hypothesis"))
 command("conda-direct-tests",conda("python","-X","utf8","-m","pytest","-o","cache_dir="+str(direct/"pytest-cache"),"--basetemp="+str(direct/"tmp"),"--cov=aqrp","--cov-branch","--cov-report=json:"+str(direct/"coverage.json"),"--cov-report=xml:"+str(direct/"coverage.xml"),"--junitxml="+str(direct/"junit.xml")),cwd=formal/"source",env=d_env)
 command("conda-direct-coverage",conda("python","-X","utf8",formal/"source/tools/check_coverage.py",direct/"coverage.json"),cwd=formal/"source",env=d_env)
 command("conda-direct-reference",conda("python","-X","utf8",formal/"source/tools/independent_reference.py"),cwd=formal/"source",env=d_env)
 command("conda-direct-smoke",conda("python","-X","utf8",formal/"source/tools/data_smoke.py",direct),cwd=formal/"source",env=d_env)
 summary["conda_direct"]={"junit":junit(direct/"junit.xml"),"wheel_sha256":formal_meta["wheel_sha256"],"aqrp_import_path":after["aqrp_import_path"],"coverage_gate":"PASS","smoke_result_sha256":hashlib.sha256((direct/"smoke-result.json").read_bytes()).hexdigest()}
 helper_rel="docs/audits/phase-1/implementation/sdk-hash-74bdb92/verify_artifacts.py"
 helper=ROOT/"verify_artifacts.py"
 helper.write_bytes(subprocess.check_output(["git","show",ENTRY_SHA+":"+helper_rel],cwd=REPO))
 zips=ROOT/"actions-original-zips";zips.mkdir()
 for aid in (12288989083,12288679676):
  shutil.copyfile(REPO/"docs/audits/phase-1/implementation/sdk-hash-74bdb92"/f"{aid}.zip",zips/f"{aid}.zip")
 command("conda-actions-zip-verification",conda("python","-X","utf8",helper,REPO,zips,ROOT/"zip-verification"))
 verification=json.loads((ROOT/"zip-verification/verification.json").read_bytes())
 assert verification["cross_platform"]["all_8_table_schemas_and_logical_records"]=="PASS"
 assert all(a["zip_hash_status"]=="PASS" for a in verification["artifacts"])
 assert all(a["result_hash"]==summary["conda_direct"]["smoke_result_sha256"] for a in verification["artifacts"])
 summary["zip_verification"]={"result":"PASS for uploaded files/data; exclusions remain explicit","output":str(ROOT/"zip-verification"),"helper_sha256":hashlib.sha256(helper.read_bytes()).hexdigest(),"artifact_ids":[a["id"] for a in verification["artifacts"]],"result_hash":summary["conda_direct"]["smoke_result_sha256"],"not_uploaded_root_files_each":3,"gemini_execution":False}
 summary["complete"]=True;save()
 print("CONDA FORMAL SDK, DIRECT 102 TESTS AND ACTIONS ZIP VERIFICATION: PASS",flush=True)
except BaseException as e:
 if not summary.get("complete"):
  summary["exception_type"]=type(e).__name__;summary["exception_message"]=str(e);save()
 raise

