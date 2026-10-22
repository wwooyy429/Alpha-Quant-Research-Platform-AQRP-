import json,sys
from pathlib import Path
from aqrp.validation.splits import purged_train
out=Path(__file__).resolve().parent;r=json.loads((out/"late-master-causal-results.json").read_bytes())
kwargs=dict(fit_range=["2024-01-02","2024-01-03"],eval_range=["2024-01-05","2024-01-06"],fit_cutoff="2024-01-04T12:10:00Z",calendar=["2024-01-02","2024-01-03","2024-01-04","2024-01-05"],embargo=0)
before=purged_train([r["before"]],**kwargs);after=purged_train([r["after"]],**kwargs)
assert len(before["train"])==0 and len(after["train"])==1
result=dict(reviewed_sha=r["reviewed_sha"],executor="GPT Work installed-wheel causal fit proof",before_train_count=len(before["train"]),after_train_count=len(after["train"]),after_split_reason=after["train"][0]["split_reason"],fit_cutoff=kwargs["fit_cutoff"],causal_master_available_at="2024-01-05T00:00:00Z",expected_after_train_count=0,actual_after_train_count=1,formal_test_executed=False)
(out/"fit-leak-results.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
print(json.dumps(result,indent=2))

