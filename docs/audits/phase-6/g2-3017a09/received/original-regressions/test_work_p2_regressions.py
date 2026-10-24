"""Independent audit probes. Expected values are manual 121/100-1 and 121/110-1."""
import hashlib
import json
from datetime import date
from decimal import Decimal

import pytest

from aqrp.core.canonical import canonical
from aqrp.core.contracts import QuerySpec
from aqrp.core.errors import ContractError
from aqrp.data.snapshot import publish_snapshot
from aqrp.data.synthetic import PROVENANCE, load_synthetic
from aqrp.factors import FactorEngine, FactorRegistry, SignalBatch, builtin_spec, write_run


def tables():
    result=load_synthetic(sessions=[(date(2024,1,d),'12:00:00') for d in (2,3,4)])
    for row in result['bars_daily']:
        index=row['session_date'].day-2
        price=Decimal((100,110,121)[index]);volume=Decimal((100,150,200)[index])
        row.update({key:price for key in ('open','high','low','close')})
        row.update(volume=volume,source_volume=str(volume),amount=price*volume,source_amount=str(price*volume))
    return result


def setup(data,root):
    snapshot=publish_snapshot(data,PROVENANCE,root/'snapshots')
    registry=FactorRegistry();spec=builtin_spec('momentum')
    registry.register(spec.implementation_version,spec,actor='GPT Work audit',reason='fixed builtin test',evidence=spec.review_ref)
    request=QuerySpec(('SYN_A:001',),'SYN_A','SYN_A_CAL',(date(2024,1,2),date(2024,1,4)),('close','volume'),'split_adjusted')
    return registry,spec,request,snapshot


@pytest.fixture
def case(tmp_path):
    registry,spec,request,snapshot=setup(tables(),tmp_path)
    batch=FactorEngine(registry).run(spec.ref,request,'2024-01-04T12:05:00Z',snapshot,parameters={'lookback':2})
    return registry,spec,request,snapshot,batch


def test_work_p2_positive_real_parameter_change_and_canonical_receipt(case,tmp_path):
    registry,spec,request,snapshot,batch=case
    assert batch.rows[0].factor_value==0.21
    one=FactorEngine(registry).run(spec.ref,request,'2024-01-04T12:05:00Z',snapshot,parameters={'lookback':1})
    assert one.rows[0].factor_value==0.1
    assert one.rows[0].params_hash!=batch.rows[0].params_hash
    assert SignalBatch(batch.rows,canonical(json.loads(batch.config_snapshot)))==batch
    root=write_run(batch,tmp_path/'normal-runs',registry)
    for entry in json.loads((root/'manifest.json').read_bytes())['artifacts']:
        assert hashlib.sha256((root/entry['path']).read_bytes()).hexdigest()==entry['sha256']


def test_work_p2_reformatted_valid_config_cannot_create_bad_artifact_hash(case,tmp_path):
    registry,_,_,_,batch=case
    reformatted=json.dumps(json.loads(batch.config_snapshot),indent=2).encode()
    assert json.loads(reformatted)==json.loads(batch.config_snapshot)
    try:
        roundtrip=SignalBatch(batch.rows,reformatted)
        root=write_run(roundtrip,tmp_path/'roundtrip-runs',registry)
    except ContractError:
        return  # Rejecting noncanonical config is also a valid contract response.
    manifest=json.loads((root/'manifest.json').read_bytes())
    entry=next(item for item in manifest['artifacts'] if item['path']=='config.json')
    actual=hashlib.sha256((root/'config.json').read_bytes()).hexdigest()
    assert entry['sha256']==actual, {'declared':entry['sha256'],'actual':actual,'status':manifest['status']}


def test_work_p2_parameters_must_match_their_own_hash(case):
    _,_,_,_,batch=case
    config=json.loads(batch.config_snapshot)
    config['params']=[['lookback',1]]
    assert dict(json.loads(batch.config_snapshot)['params'])=={'lookback':2}
    assert config['params_hash']==batch.rows[0].params_hash
    with pytest.raises(ContractError):
        SignalBatch(batch.rows,canonical(config))


def test_work_p2_unknown_calendar_availability_cannot_produce_formal_signal(tmp_path):
    data=tables()
    for row in data['calendar']:
        if row['market_id']=='SYN_A':
            row.update(quality_status='UNKNOWN_AVAILABILITY',reason_code='SOURCE_HISTORY_UNVERIFIED')
    with pytest.raises(ContractError):
        registry,spec,request,snapshot=setup(data,tmp_path)
        batch=FactorEngine(registry).run(spec.ref,request,'2024-01-04T12:05:00Z',snapshot,parameters={'lookback':2})
        assert batch.rows[0].validity=='VALID' and batch.rows[0].factor_value==0.21
