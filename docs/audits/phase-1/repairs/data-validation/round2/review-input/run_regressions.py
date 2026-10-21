import sys,json,hashlib
from pathlib import Path
import pytest
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'phase1/src'))
import aqrp
files={p.relative_to(R/'phase1/src').as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (R/'phase1/src').rglob('*.py')}
(R/'regression-target.json').write_text(json.dumps(dict(audit='GPT Work 补充审核',target_sha='f579b2c99e762085772de6e70ba1fa98792a7add',sdk_file=aqrp.__file__,python=sys.version,source_hashes=files),indent=2),encoding='utf-8')
print('FIXED SDK:',aqrp.__file__,flush=True)
args=[str(R/'test_round2_regressions.py'),r'C:\Users\11638\AppData\Local\AQRP\reviews\work-p1-18d51fb-20261021\test_work_p1_regressions.py','-v','-o',f'cache_dir={R / "pytest-cache"}',f'--basetemp={R / "pytest-tmp"}',f'--junitxml={R / "round2-junit.xml"}']
(R/'regression-command.json').write_text(json.dumps(dict(executable=sys.executable,args=args),indent=2),encoding='utf-8')
raise SystemExit(pytest.main(args))
