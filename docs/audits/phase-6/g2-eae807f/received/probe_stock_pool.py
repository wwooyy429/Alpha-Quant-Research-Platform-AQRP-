from pathlib import Path
import json
from aqrp.services.tasks import TaskService
from aqrp.services.task_requests import FIELDS,catalogue
O=Path(__file__).parent
root=Path('E:/WORK/AQRP-runs/gpt-p6-independent-probes-20261024/search-family-variants')
s=TaskService(root);cat=catalogue(root);pool=cat['config']['universe_id']
try:
 s.freeze({'kind':'research','universe_id':pool});response='ACCEPTED'
except Exception as exc:response=getattr(exc,'code',type(exc).__name__)
record=dict(scope='Current installed shared builder and supported fields; synthetic catalogue only',catalogue_pool=pool,all_supported_draft_fields=sorted(FIELDS),requesting_current_pool_explicitly=response,universe_field_supported='universe_id' in FIELDS,source_locations=['ui/app.py:247 read-only fixed six-asset caption','services/task_requests.py:124 FIELDS','services/task_requests.py:229 config copied from singleton catalogue'],requirement='UI-003 / V3.0§9.3 / original PAGE_SPECIFICATIONS: stock-pool selection alongside factor/date/horizon',note='Unknown-field rejection is not alone a defect; combined UI and builder inspection shows no stock-pool selector/catalogue pool ID mechanism. No arbitrary path or real-market data support is requested.')
(O/'STOCK_POOL_SCOPE_PROBE.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))

