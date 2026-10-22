import hashlib
import json
import os
import subprocess
from pathlib import Path

root = Path(r"C:\Users\11638\AppData\Local\AQRP\checkouts\phase1-57461d5d-5de2-4c78-9b4e-5fad2b5ccb29")
out = Path(__file__).parent/"original-probes-07e7c88"
out.mkdir(exist_ok=True)
runtime = Path(__file__).parent/"clean-sdk/aqrp-8f6226b8-5727-45b5-a08f-ed14aaa22673/venv/Scripts/python.exe"
env = dict(os.environ)
env.pop("PYTHONPATH", None)
env["PYTHONUTF8"] = "1"
for group in ("original16", "original4"):
    source = json.loads((root/f"docs/audits/phase-2/publication/{group}-command.json").read_bytes())
    inputs = source["original_inputs"]
    for item in inputs:
        assert hashlib.sha256(Path(item["path"]).read_bytes()).hexdigest() == item["sha256"]
    args = [str(runtime), "-m", "pytest", *[p["path"] for p in inputs], "-q", "-o", f"cache_dir={out/(group+'-cache')}", f"--basetemp={out/(group+'-tmp')}", f"--junitxml={out/(group+'.xml')}"]
    (out/(group+"-command.json")).write_text(json.dumps({"argv": args, "cwd": str(out), "PYTHONPATH": "unset", "original_inputs": inputs,
        "actual_executor": "Codex developer; original test authorship/fixture actor strings do not change execution identity", "source_commit": "07e7c88745c031feeaee5d1e374a02caada77777"}, indent=2)+"\n", encoding="utf-8", newline="\n")
    with (out/(group+".log")).open("wb") as f:
        result = subprocess.run(args, cwd=out, env=env, stdout=f, stderr=subprocess.STDOUT)
    (out/(group+"-exit.txt")).write_text(str(result.returncode)+"\n", encoding="utf-8", newline="\n")
    print(group, result.returncode)
    if result.returncode:
        raise SystemExit(result.returncode)
