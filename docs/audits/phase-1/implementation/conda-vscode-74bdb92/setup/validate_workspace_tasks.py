from pathlib import Path
import json,os,re,subprocess,sys
from xml.etree import ElementTree
root=Path("C:\\Users\\11638\\AppData\\Local\\AQRP\\runs\\conda-vscode-1792572943050")
paths=json.loads((root/"physical-paths.json").read_bytes())
workspace=Path(paths[1]["physical"])
cfg=json.loads(workspace.read_text(encoding="utf-8-sig"))
old=r"C:\Users\11638\AppData\Local\AQRP"
physical_base=str(Path(paths[0]["physical"]).parent.parent.parent)
def convert(v):
 if isinstance(v,str):return v.replace(old,physical_base)
 if isinstance(v,list):return [convert(x) for x in v]
 if isinstance(v,dict):return {k:convert(x) for k,x in v.items()}
 return v
cfg=convert(cfg)
zip_task=cfg["tasks"]["tasks"][1]
program=zip_task["args"][-1]
program=program.replace("; raise SystemExit",'; print("Artifacts: "+str(out),flush=True); raise SystemExit')
zip_task["args"][-1]=program
workspace.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
(root/"workspace-final.json").write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
commands=[]
for i,task in enumerate(cfg["tasks"]["tasks"]):
 label="workspace-sdk-task" if i==0 else "workspace-zip-task"
 print(label+": START",flush=True)
 env=dict(os.environ,**task["options"].get("env",{}));env.pop("PYTHONPATH",None)
 args=[task["command"],*task["args"]]
 with (root/(label+".log")).open("w",encoding="utf-8") as log:
  p=subprocess.run(args,cwd=task["options"]["cwd"],env=env,stdout=log,stderr=subprocess.STDOUT)
 logtext=(root/(label+".log")).read_text(encoding="utf-8",errors="replace")
 record={"label":task["label"],"command":args,"cwd":task["options"]["cwd"],"exit_code":p.returncode,"log":label+".log","execution":"Exact workspace task process configuration executed through CLI; no GUI click claim"}
 commands.append(record)
 (root/"workspace-task-results.json").write_text(json.dumps({"workspace":str(workspace),"tasks":commands},ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
 print(label+": EXIT "+str(p.returncode),flush=True)
 if p.returncode:
  print(logtext[-5000:]);raise SystemExit(p.returncode)
 matches=re.findall(r"^Artifacts: (.+)$",logtext,re.MULTILINE);assert len(matches)==1
 output=Path(matches[0].strip());record["output"]=str(output)
 if i==0:
  meta=json.loads((output/"environment.json").read_bytes())
  assert meta["complete"] and meta["code_commit"]=="74bdb9216c585d27de91123605aff0266ca028cc" and not meta["dirty"]
  suites=list(ElementTree.fromstring((output/"junit.xml").read_bytes()).iter("testsuite"))
  junit={k:sum(int(s.attrib.get(k,0)) for s in suites) for k in ("tests","failures","errors","skipped")}
  assert junit=={"tests":102,"failures":0,"errors":0,"skipped":0}
  record["junit"]=junit;record["environment"]=meta
 else:
  ver=json.loads((output/"verification.json").read_bytes())
  assert ver["cross_platform"]["all_8_table_schemas_and_logical_records"]=="PASS"
  record["result"]="PASS, explicit missing-upload limits retained"
 (root/"workspace-task-results.json").write_text(json.dumps({"workspace":str(workspace),"tasks":commands},ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
print("WORKSPACE CONFIGURED TASK COMMANDS: PASS",flush=True)

