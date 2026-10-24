import json
from copy import deepcopy
from datetime import date
from decimal import Decimal
from pathlib import Path
import pytest
from aqrp.core.errors import ContractError,DataQualityError
from aqrp.core.time import utc
from aqrp.data.snapshot import publish_snapshot
from aqrp.data.synthetic import PROVENANCE,record
ROOT=Path(__file__).resolve().parent
BASE=json.loads((ROOT/'source/tests/golden/phase1_input.json').read_bytes())
@pytest.mark.parametrize('change',[
    {'volume':'1.25','source_volume':'1.25','source_volume_unit':'currency'},
    {'amount':'3','source_amount':'3','source_amount_unit':'share'},
])
def test_work_p1_001_reject_wrong_unit_dimension(tmp_path,change):
    tables=deepcopy(BASE);tables['bars_daily'][0].update(change)
    with pytest.raises((ContractError,DataQualityError)):
        publish_snapshot(tables,PROVENANCE,tmp_path/'snapshots')
def test_work_p1_002_reject_action_exdate_conflict(tmp_path):
    tables=deepcopy(BASE)
    tables['corporate_actions']=[record('corporate_actions',action_id='div-1',revision_id=1,security_id='SYN_A:001',type='CASH_DIVIDEND',announcement_at=utc('2024-01-01T00:00:00Z'),effective_at=utc('2024-01-03T00:00:00Z'),ex_date=date(2024,1,4),cash_per_share=Decimal(2),currency='SYNCCY',dividend_basis='PER_OLD_SHARE')]
    with pytest.raises((ContractError,DataQualityError)):
        publish_snapshot(tables,PROVENANCE,tmp_path/'snapshots')
def test_work_p1_003_reject_known_ohlc_contradictions_with_null(tmp_path):
    tables=deepcopy(BASE);tables['bars_daily'][0].update(open='100',high='90',low='95',close=None)
    with pytest.raises((ContractError,DataQualityError)):
        publish_snapshot(tables,PROVENANCE,tmp_path/'snapshots')
def test_positive_valid_frozen_input(tmp_path):
    assert publish_snapshot(deepcopy(BASE),PROVENANCE,tmp_path/'snapshots')
def test_positive_valid_partial_ohlc(tmp_path):
    tables=deepcopy(BASE);tables['bars_daily'][0]['close']=None
    assert publish_snapshot(tables,PROVENANCE,tmp_path/'snapshots')
