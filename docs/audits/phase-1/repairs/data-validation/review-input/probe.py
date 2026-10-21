import dataclasses, hashlib, json, platform, sys, traceback
from pathlib import Path
from datetime import date
from decimal import Decimal
from copy import deepcopy
from aqrp.core.contracts import QuerySpec
from aqrp.core.time import utc
from aqrp.data.quality import validate_table
from aqrp.data.snapshot import publish_snapshot
from aqrp.data.synthetic import PROVENANCE, record
from aqrp.data.query import query
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'source'
BASE=json.loads((SOURCE/'tests/golden/phase1_input.json').read_bytes())
OUT=ROOT/'probe-data'
OUT.mkdir(exist_ok=True)
results=[]
def run_case(name, change):
    tables=deepcopy(BASE)
    change(tables)
    result={'case':name, 'mutated_input':tables, 'expected':'Reject malformed input before snapshot publication'}
    try:
        reports={n:dataclasses.asdict(validate_table(n,rs).report) for n,rs in tables.items()}
        result['quality_reports']=reports
        ref=publish_snapshot(tables,PROVENANCE,OUT,snapshot_id=name)
        spec=QuerySpec(('SYN_A:001',),'SYN_A','SYN_A_CAL',(date(2024,1,2),date(2024,1,3)), fields=('open','high','low','close','volume','amount'))
        result['actual']='PUBLISHED_AND_QUERIED'
        result['rows']=query(spec,'2024-01-03T12:05:00Z',ref).table.to_pylist()
        result['snapshot_ref']=dataclasses.asdict(ref)
    except Exception as e:
        result.update(actual='REJECTED',error_type=type(e).__name__,error=str(e))
    results.append(result)

def volume_currency(t):
    t['bars_daily'][0].update(volume='1.25', source_volume='1.25', source_volume_unit='currency')
def amount_share(t):
    t['bars_daily'][0].update(amount='3', source_amount='3', source_amount_unit='share')
def partial_bad_ohlc(t):
    t['bars_daily'][0].update(open='100',high='90',low='95',close=None)
def bad_ex_date(t):
    t['bars_daily'][1].update(open='98',high='98',low='98',close='98')
    t['corporate_actions']=[record('corporate_actions',action_id='div-1',revision_id=1,security_id='SYN_A:001',type='CASH_DIVIDEND',announcement_at=utc('2024-01-01T00:00:00Z'),effective_at=utc('2024-01-03T00:00:00Z'),ex_date=date(2024,1,4),cash_per_share=Decimal(2),currency='SYNCCY',dividend_basis='PER_OLD_SHARE')]
def before_listing(t):
    t['security_master'][0]['listing_at']='2024-02-01T00:00:00Z'
for name,f in [('volume-currency',volume_currency),('amount-share',amount_share),('partial-bad-ohlc',partial_bad_ohlc),('dividend-exdate-mismatch',bad_ex_date),('bar-before-listing',before_listing)]:
    run_case(name,f)
    if name=='dividend-exdate-mismatch' and results[-1]['actual']=='PUBLISHED_AND_QUERIED':
        ref=results[-1]['snapshot_ref']
        from aqrp.core.contracts import SnapshotRef
        ref=SnapshotRef(Path(ref['root']),ref['snapshot_id'],ref['manifest_hash'])
        spec=QuerySpec(('SYN_A:001',),'SYN_A','SYN_A_CAL',(date(2024,1,2),date(2024,1,3)),fields=('total_return_index',),price_basis='total_return')
        results[-1]['total_return_rows']=query(spec,'2024-01-03T12:05:00Z',ref).table.to_pylist()
        results[-1]['expected_before_Jan4_exdate']='Reject inconsistent action dates, or do not credit Jan4 dividend into Jan3 index (which would be 0.98 without the dividend).'
summary={'audit':'GPT Work supplemental verification','target_sha':'18d51fbecc4a1526f2ab75d34874a0b25d00f6c1','python':sys.version,'executable':sys.executable,'os':platform.platform(),'sdk_file':__import__('aqrp').__file__,'cases':results}
(ROOT/'probe-results.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
for r in results:
    print(r['case'],r['actual'])
    for row in r.get('rows',[])[:1]: print(json.dumps(row,default=str))
    if 'total_return_rows' in r: print('total_return_index:',[row['total_return_index'] for row in r['total_return_rows']])
