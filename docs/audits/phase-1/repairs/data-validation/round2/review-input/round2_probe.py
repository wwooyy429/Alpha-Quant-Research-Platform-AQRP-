import json,sys,traceback,dataclasses,importlib.resources
from pathlib import Path
from copy import deepcopy
from datetime import date
from aqrp.core.contracts import QuerySpec
from aqrp.data.quality import validate_table,validate_dataset
from aqrp.data.snapshot import publish_snapshot
from aqrp.data.query import query
from aqrp.data.synthetic import PROVENANCE
from aqrp.core.time import iana,utc
R=Path(__file__).resolve().parent
BASE=json.loads((R/'phase1/tests/golden/phase1_input.json').read_bytes())
results=[]
for table in ['bars_daily','security_master','calendar','universe_membership']:
    t=deepcopy(BASE);t[table][0].update(quality_status='UNKNOWN_AVAILABILITY',reason_code='SOURCE_HISTORY_UNVERIFIED')
    d=dict(case='unknown-flag-'+table,input=t[table][0])
    try:
        ref=publish_snapshot(t,PROVENANCE,R/'probe-snapshots',snapshot_id=d['case'])
        spec=QuerySpec(('SYN_A:001',),'SYN_A','SYN_A_CAL',(date(2024,1,2),date(2024,1,3)))
        view=query(spec,'2024-01-03T12:05:00Z',ref)
        d.update(actual='FORMAL_QUERY_SUCCEEDED',manifest_pit_status=json.loads((ref.root/ref.snapshot_id/'manifest.json').read_bytes())['pit_status'],rows=view.table.to_pylist())
    except Exception as e:d.update(actual='REJECTED',type=type(e).__name__,error=str(e))
    results.append(d)
for value in [2**63,-1]:
    r=deepcopy(BASE['bars_daily'][0]);r['revision_id']=value
    try:
        v=validate_table('bars_daily',[r]);results.append(dict(case='revision-int64-'+str(value),actual='QUALITY_REPORT',report=dataclasses.asdict(v.report)))
    except Exception as e:results.append(dict(case='revision-int64-'+str(value),actual='UNSTRUCTURED_ERROR',type=type(e).__name__,error=str(e),traceback=traceback.format_exc()))
path=Path(str(importlib.resources.files('tzdata.zoneinfo').joinpath('UTC')))
for zone in [str(path),path.as_posix()]:
    try: z=iana(zone);results.append(dict(case='iana-absolute-path',input=zone,actual='ACCEPTED',tzkey=z.key))
    except Exception as e:results.append(dict(case='iana-absolute-path',input=zone,actual='REJECTED',error=str(e)))
for value in ['2024-01-02T16:00:00.000000+00:00:00.000000001','2024-01-02T16:00:00+00:00:00.000000001']:
    try:results.append(dict(case='offset-nanoseconds',input=value,actual='ACCEPTED',utc=str(utc(value))))
    except Exception as e:results.append(dict(case='offset-nanoseconds',input=value,actual='REJECTED',error=str(e)))
(R/'round2-probe-results.json').write_text(json.dumps(dict(audit='GPT Work 补充审核',phase1_sha='f579b2c99e762085772de6e70ba1fa98792a7add',sdk_file=__import__('aqrp').__file__,python=sys.version,results=results),indent=2,ensure_ascii=False,default=str),encoding='utf-8')
for r in results:
    print(r['case'],r['actual'],r.get('manifest_pit_status',''),r.get('type',''),r.get('input','') if r['case']=='iana-absolute-path' else '')
