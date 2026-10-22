"""Independent official CI ZIP verification, no execution of archived code."""
import hashlib,io,json,sys,zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
out=Path(__file__).resolve().parent;root=Path(sys.argv[1]).resolve()
SHA="5a5e093c2e9b39abe1332e49d1df40d20f9fd33f"
H=lambda b:hashlib.sha256(b).hexdigest()
meta=json.loads((out/"ci-artifacts.json").read_bytes());merge=json.loads((out/"ci-merge.json").read_bytes())
local={"aqrp/"+p.relative_to(root/"src/aqrp").as_posix():p.read_bytes() for p in (root/"src/aqrp").rglob("*.py")}
receip=(root/"src/aqrp/factors/reviewed_code.json").read_bytes()
records=[]
for a in meta["artifacts"]:
 archive=out/f'artifact-{a["id"]}.zip';payload=archive.read_bytes()
 assert len(payload)==a["size_in_bytes"] and "sha256:"+H(payload)==a["digest"]
 with zipfile.ZipFile(io.BytesIO(payload)) as z:
  assert z.testzip() is None
  paths=z.namelist();prefix=paths[0].split("/")[0]+"/"
  read=lambda n:z.read(prefix+n)
  selection=json.loads(read("upload-selection.json"))
  expected={prefix+r["path"] for r in selection["files"]}|{prefix+"upload-selection.json"}
  assert expected==set(paths)
  for r in selection["files"]:assert H(read(r["path"]))==r["sha256"],r["path"]
  env=json.loads(read("environment.json"));assert env["code_commit"]==merge["sha"] and env["dirty"] is False and env["complete"] is True and env["python"].startswith("3.13.16")
  assert env["lock_sha256"]==H((root/"requirements.lock").read_bytes())
  xml=ET.fromstring(read("junit.xml"));tests=xml.findall(".//testcase")
  counts=dict(tests=len(tests),failures=sum(len(t.findall("failure")) for t in tests),errors=sum(len(t.findall("error")) for t in tests),skipped=sum(len(t.findall("skipped")) for t in tests))
  assert counts==dict(tests=564,failures=0,errors=0,skipped=0)
  wname=next(n[len(prefix):] for n in paths if n.startswith(prefix+"wheel/") and n.endswith(".whl"));wheel=read(wname)
  assert H(wheel)==env["wheel_sha256"]
  with zipfile.ZipFile(io.BytesIO(wheel)) as w:
   assert {n for n in w.namelist() if n.endswith(".py")}==set(local)
   for n,b in local.items():assert w.read(n)==b,n
   assert w.read("aqrp/factors/reviewed_code.json")==receip
  # Raw immutable research and factor ledgers, original bytes/config hash semantics.
  manifests=[];engine_batches=0;origin_refs=0
  for n in paths:
   rel=n[len(prefix):]
   if rel.endswith("/manifest.json"):
    m=json.loads(z.read(n));parent=n.rsplit("/",1)[0]+"/"
    if "files" in m and "status" in m and "event_prefix_hash" in m:
     for f in m["files"]:assert H(z.read(parent+f["path"]))==f["sha256"],n
     events=[json.loads(line) for line in z.read(parent+"events.jsonl").splitlines()]
     previous="0"*64
     for i,e in enumerate(events):
      d={k:v for k,v in e.items() if k!="hash"}
      b=json.dumps(d,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode()
      assert e["seq"]==i and e["previous"]==previous and H(b)==e["hash"];previous=e["hash"]
     assert H(z.read(n))==events[-1]["payload"]["manifest_sha256"] and events[-1]["kind"]==m["status"]
     manifests.append(dict(path=rel,status=m["status"],files=len(m["files"])))
   if rel.endswith("/engine.json"):
    batches=json.loads(z.read(n))
    for b in batches:
     cfg=b["config_snapshot_utf8"];assert H(cfg.encode())==b["config_snapshot_sha256"]
     raw=json.dumps({"rows":b["signals"],"config":cfg},sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode()
     assert H(raw)==b["content_hash"]
     engine_batches+=1
   if rel=="reproduction/published-original-replay.json":
    old=json.loads(z.read(n));assert old["status"]=="ALL_ORIGINAL_BYTES_VERIFIED_AND_THREE_RUNS_REPLAYED" and len(old["verified_original_files"])==66 and len(old["runs"])==3
    for r in old["runs"]:assert r["status"]=="DECLARED_PROJECTION_MATCH"
    origin_refs=len(old["runs"])
  deps=[n for n in paths if "/reproduction/wheelhouse/" in n and n.endswith(".whl")]
  assert len(deps)==(22 if "windows" in a["name"] else 21)
  envarchive=json.loads(read("reproduction/environment-archive.json"))
  assert len(envarchive["dependency_wheels"])==len(deps)
  for r in envarchive["dependency_wheels"]:assert H(read("reproduction/wheelhouse/"+r["path"]))==r["sha256"]
  for name in ("environment.json","junit.xml","coverage.json","upload-selection.json","commands.log","reproduction/environment-archive.json","reproduction/published-original-replay.json"):
   path=out/f'artifact-{a["id"]}'/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(read(name))
  records.append(dict(artifact_id=a["id"],name=a["name"],bytes=len(payload),sha256=H(payload),crc="PASS",selected_files=len(selection["files"]),exact_uploaded_members=len(paths),junit=counts,wheel_sha256=H(wheel),source_modules_exact=len(local),environment=env,immutable_research_runs=manifests,engine_batches_checked_including_cache_refs=engine_batches,old_published_files=66,old_runs_replayed=origin_refs,original_dependency_wheels_verified=len(deps)))
r=dict(reviewed_sha=SHA,actual_ci_checkout=merge["sha"],actual_ci_tree=merge["commit"]["tree"]["sha"],executor="GitHub hosted runners executed; GPT Work independently verified official original ZIPs",artifacts=records)
(out/"ci-verification.json").write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({**r,"artifacts":[{k:v for k,v in a.items() if k not in ("environment","immutable_research_runs")} for a in records]},indent=2))

