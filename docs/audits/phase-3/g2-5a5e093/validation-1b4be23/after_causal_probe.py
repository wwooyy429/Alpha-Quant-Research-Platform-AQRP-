from pathlib import Path
from copy import deepcopy
from datetime import date
from decimal import Decimal
import json
from aqrp.core.canonical import canonical
from aqrp.core.time import utc
from aqrp.data.synthetic import load_synthetic,PROVENANCE
from aqrp.data.snapshot import publish_snapshot
from aqrp.validation.labels import CoverageRef,make_labels
from aqrp.validation.splits import purged_train
out=Path(__file__).resolve().parent/'extras/after-causal'
out.mkdir(exist_ok=True)
tables=load_synthetic(sessions=[(date(2024,1,d),'12:00:00') for d in (2,3,4,5)])
for r in tables['bars_daily']:
    p=Decimal(100 if r['session_date'].day==3 else 110)
    r.update({k:p for k in ('open','high','low','close')})
    r.update(amount=p*r['volume'],source_amount=str(p*r['volume']))
old=tables['security_master'][0]
old['delisting_at']=utc('2024-01-04T08:00:00Z')
new=deepcopy(old)
new.update(revision_id=2,delisting_at=None,event_time=utc('2024-01-05T00:00:00Z'),available_at=utc('2024-01-05T00:00:00Z'),known_at=utc('2024-01-05T00:00:00Z'),source_record_id='late-delisting-correction')
tables['security_master'].append(new)
s=publish_snapshot(tables,PROVENANCE,out/'snapshot')
c=CoverageRef.create(s.manifest_hash,[dict(coverage_id='jan4',event_time='2024-01-04T12:00:00Z',available_at='2024-01-04T12:05:00Z',complete_through='2024-01-04T12:00:00Z',revision_id=1)],authority='developer-public-known-review-input',scope='PUBLIC_ENGINEERING')
def at(cutoff):
    return make_labels(s,[dict(session=date(2024,1,2),decision_time='2024-01-02T12:05:00Z')],['SYN_A:001'],[1],cutoff,c)[0]
before=at('2024-01-04T12:10:00Z');after=at('2024-01-05T12:10:00Z')
assert before['label'] is None and after['label']==.1
assert after['available_at']==utc('2024-01-05T00:00:00Z')
split=purged_train([after],('2024-01-02','2024-01-03'),('2024-01-05','2024-01-06'),'2024-01-04T12:10:00Z',[],0)
assert not split['train'] and split['rejected'][0]['split_reason']=='LABEL_NOT_AVAILABLE_AT_FIT'
r={'actual_executor':'Codex developer on newly installed repair wheel, not independent review','business_commit':'1b4be236e888805f5c4e45357b158fcdb6058df0','input_origin':'GPT Work late-master causal example, before unchanged; correct after expectations from review','expected_return':'.1 = 110/100 - 1','expected_earliest_label_available_at':'2024-01-05T00:00:00Z','before':before,'after':after,'fit_train_count':len(split['train']),'fit_rejection':split['rejected'][0]['split_reason'],'formal_test_or_deployment':False}
(out/'AFTER_CAUSAL_PROBE.json').write_bytes(canonical(r))
print(json.dumps({'label':after['label'],'available_at':str(after['available_at']),'fit_train_count':len(split['train']),'fit_reason':split['rejected'][0]['split_reason']}))
