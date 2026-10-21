import json,sys,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'phase1/src'))
from aqrp.core.contracts import SnapshotRef
from aqrp.data.query import universe_at
base=R/'probe-snapshots/unknown-flag-universe_membership'
m=json.loads((base/'manifest.json').read_bytes());ref=SnapshotRef(base.parent,m['snapshot_id'],m['manifest_hash'])
rows=universe_at('SYN_U','2024-01-03T12:05:00Z',ref)
assert any(r['quality_status']=='UNKNOWN_AVAILABILITY' for r in rows)
(R/'unknown-universe-direct-lookup.json').write_text(json.dumps(dict(audit='GPT Work 补充审核',target_sha='f579b2c99e762085772de6e70ba1fa98792a7add',actual='FORMAL_UNIVERSE_LOOKUP_RETURNED_UNKNOWN_AVAILABILITY',rows=rows),ensure_ascii=False,indent=2,default=str),encoding='utf-8')
print('Formal universe lookup returned UNKNOWN_AVAILABILITY row')
for name in ['GPT-Work-Phase0-Phase1-Round2-Review.md','Codex-Round2-Repair-Tasks.md']:
    p=R/name;t=p.read_text(encoding='utf-8')
    t=t.replace('其余三类未知元数据也参与正常查询','master/calendar未知元数据参与正常查询；成员表另用正式universe_at复核，也直接返回UNKNOWN_AVAILABILITY记录')
    p.write_text(t,encoding='utf-8')
