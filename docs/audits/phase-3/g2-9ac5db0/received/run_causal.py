import subprocess,json
from pathlib import Path
from datetime import datetime,timezone
out=Path(__file__).resolve().parent
argv=[r"C:/Users/11638/AppData/Local/AQRP/reviews/work-p3-g2-recheck-9ac5db0/sdk/aqrp-b95750e5-e167-4173-94b6-20568b25fab4/venv/Scripts/python.exe","-I",str(out/"after_causal_independent.py")]
start=datetime.now(timezone.utc).isoformat();r=subprocess.run(argv,capture_output=True,cwd=out)
for s in ("stdout","stderr"):(out/("after-causal."+s+".log")).write_bytes(getattr(r,s))
(out/"after-causal.command.json").write_text(json.dumps(dict(argv=argv,cwd=str(out),started_utc=start,ended_utc=datetime.now(timezone.utc).isoformat(),exit_code=r.returncode),indent=2),encoding="utf-8")
print(r.stdout.decode("utf-8","replace"));assert r.returncode==0,r.stderr.decode("utf-8","replace")

