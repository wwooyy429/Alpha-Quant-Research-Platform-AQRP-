import json,importlib.resources,traceback,hashlib
from pathlib import Path
from copy import deepcopy
from aqrp.data.snapshot import publish_snapshot,verify_snapshot
from aqrp.data.synthetic import PROVENANCE
from aqrp.core.time import iana
R=Path(__file__).resolve().parent
zone=R/'external-clock.tzif'
zone.write_bytes(importlib.resources.files('tzdata.zoneinfo').joinpath('UTC').read_bytes())
t=json.loads((R/'phase1/tests/golden/phase1_input.json').read_bytes())
for rows in t.values():
    for row in rows:row['source_timezone']=str(zone)
result={'input_timezone':str(zone),'timezone_location':str(zone.resolve()),'before_tzif_sha256':hashlib.sha256(zone.read_bytes()).hexdigest()}
try:
    ref=publish_snapshot(t,PROVENANCE,R/'zone-snapshots',snapshot_id='external-zone')
    result['published']=True
    manifest,_=verify_snapshot(ref)
    result['before']='VERIFIED';result['manifest_hash']=ref.manifest_hash
    zone.write_bytes(importlib.resources.files('tzdata.zoneinfo').joinpath('Etc','GMT+12').read_bytes())
    result['after_tzif_sha256']=hashlib.sha256(zone.read_bytes()).hexdigest()
    try:verify_snapshot(ref);result['after']='VERIFIED'
    except Exception as e:result['after']=type(e).__name__+': '+str(e);result['after_traceback']=traceback.format_exc()
except Exception as e:result['error']=traceback.format_exc()
(R/'external-timezone-results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,default=str),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,default=str))
