from dataclasses import asdict
import json
from pathlib import Path
import aqrp
from aqrp.factors.admission import BUILTINS, builtin_spec, reviewed_policy
policy=reviewed_policy()
print(json.dumps({"scope":"Read-only installed package metadata lookup; no factor compute or P7 business execution","package_path":str(Path(aqrp.__file__).resolve()),"policy":policy,"refs":[asdict(builtin_spec(name).ref) for name in BUILTINS]},ensure_ascii=False))
