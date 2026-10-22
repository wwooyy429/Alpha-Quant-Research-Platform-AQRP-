"""Independent preservation audit of prior reviewer seal and repository receipt subset."""
import hashlib,json,sys,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
out=Path(__file__).resolve().parent;root=Path(sys.argv[1]).resolve();g2=root/"docs/audits/phase-3/g2-5a5e093";received=g2/"received"
H=lambda b:hashlib.sha256(b).hexdigest();J=lambda p:json.loads(p.read_bytes())
receipt=J(g2/"RECEIPT.json");oldzip=out.parent/"GPT-Work-P3-G2-5a5e093-Evidence.zip"
assert oldzip.stat().st_size==receipt["original_zip_bytes"]==296718793
assert H(oldzip.read_bytes())==receipt["original_zip_sha256"]=="54f559f9360cafcdc4d4fc9ab7af7a3eb6c13af846b6ab19524208e2cf336ca0"
with zipfile.ZipFile(oldzip) as z:
 assert z.testzip() is None
 mb=z.read("REVIEW_EVIDENCE_MANIFEST.json");assert H(mb)==receipt["manifest_sha256"]=="01431095060c77a283e8f409268172119985484afb0670dafb226637fec99cf7"
 m=json.loads(mb);assert len(m["files"])==319
 files={f["path"]:f for f in m["files"]}
 assert set(z.namelist())==set(files)|{"REVIEW_EVIDENCE_MANIFEST.json"}
 for f in m["files"]:
  b=z.read(f["path"]);assert len(b)==f["bytes"] and H(b)==f["sha256"],f["path"]
 stored=receipt["stored_received_files"];omitted=receipt["omitted_from_git_but_retained_in_original_zip"]
 assert len(stored)==147 and len(omitted)==172
 assert {f["path"] for f in stored}.isdisjoint({f["path"] for f in omitted})
 assert {f["path"] for f in stored+omitted}==set(files)
 for f in stored+omitted:assert files[f["path"]]==f
 for f in stored:
  b=(received/f["path"]).read_bytes();assert b==z.read(f["path"])
 assert (received/"REVIEW_EVIDENCE_MANIFEST.json").read_bytes()==mb
 oldcases=ET.fromstring(z.read("reviewer-regressions.xml")).findall(".//testcase")
 assert len(oldcases)==4 and all(c.findall("failure") for c in oldcases)
 assert json.loads(z.read("reviewer-regressions.command.json"))["exit_code"]==1
 assert json.loads(z.read("scope.command.json"))["exit_code"]!=0
 retained_keys=[n for n in z.namelist() if n in ("test_review_regressions.py","independent_implementation_math.py","verify_scanner_controls.py")]
 sources=[dict(path=n,sha256=H(z.read(n))) for n in retained_keys]
 oldseal=out.parent/"GPT-Work-P3-G2-5a5e093-Seal.json"
 assert J(oldseal)["zip_sha256"]==H(oldzip.read_bytes())
r=dict(reviewed_sha="9ac5db069287a6e4a095e25ae8c3cc8fa229cded",executor="GPT Work current independent preservation audit",prior_reviewed_sha=receipt["reviewed_sha"],original_zip_path=str(oldzip.resolve()),original_zip_sha256=receipt["original_zip_sha256"],original_zip_bytes=oldzip.stat().st_size,crc="PASS",manifest_members=319,stored_received_files=147,omitted_from_git_exact_partition=172,old_product_failures_preserved=4,old_reviewer_helper_failure_preserved=True,original_script_hashes=sources,original_report_unchanged=True)
(out/"archive-verification.json").write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(r,ensure_ascii=False,indent=2))

