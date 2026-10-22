"""Finish only the premature scanner step; preserve the complete failed helper attempt."""
import json,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
out=Path(__file__).resolve().parent
root=Path(r"C:/Users/11638/AppData/Local/AQRP/reviews/p3-recheck-9ac5db0")
sdk=next((out/"sdk").iterdir());py=sdk/"venv/Scripts/python.exe"
for src,dst in [("run_extras.py","run_extras-attempt1.py"),("extra-verification.json","extra-verification-attempt1.json")]+[("scanner-controls"+s,"scanner-controls-attempt1"+s) for s in (".command.json",".stdout.log",".stderr.log")]:
 assert not (out/dst).exists()
 shutil.copyfile(out/src,out/dst)
assert (sdk/"gitleaks.exe").exists()
record=json.loads((out/"extra-verification.json").read_bytes())
argv=[str(py),"-I",str(out/"verify_scanner_controls.py"),str(root)]
start=datetime.now(timezone.utc).isoformat();r=subprocess.run(argv,capture_output=True,cwd=out)
name="scanner-controls-retry"
for stream in ("stdout","stderr"):(out/(name+"."+stream+".log")).write_bytes(getattr(r,stream))
c=dict(name=name,executable=str(py),argv=argv[1:],cwd=str(out),started_utc=start,ended_utc=datetime.now(timezone.utc).isoformat(),exit_code=r.returncode)
(out/(name+".command.json")).write_text(json.dumps(c,indent=2),encoding="utf-8")
record["commands"].append(c)
record["helper_attempt1_note"]="Premature scanner call before SDK downloaded gitleaks.exe failed with FileNotFoundError. No scanner ran. Original helper failure and first four successful commands preserved. Only scanner control retried after SDK completed."
assert r.returncode==0,r.stderr.decode("utf-8","replace")
assert all(x["pass_"] for x in json.loads((out/"scanner-controls.json").read_bytes())["results"])
record.update(completed=True,completed_utc=datetime.now(timezone.utc).isoformat(),original_four="4 passed",original20="20 passed",independent_math=91,scanner_controls=3)
(out/"extra-verification.json").write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(dict(completed=True,original_four=4,original20=20,independent_math=91,scanner_controls=3,preserved_helper_failure=True),indent=2))

