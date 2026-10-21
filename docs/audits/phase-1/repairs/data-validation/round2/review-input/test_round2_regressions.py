import json
from copy import deepcopy
from pathlib import Path
from datetime import datetime,UTC
import importlib.resources
import pytest
from aqrp.core.errors import ContractError,DataQualityError,TimestampResolutionError
from aqrp.core.time import iana,utc
from aqrp.data.quality import validate_table
from aqrp.data.snapshot import publish_snapshot
from aqrp.data.synthetic import PROVENANCE
R=Path(__file__).resolve().parent
BASE=json.loads((R/'phase1/tests/golden/phase1_input.json').read_bytes())
@pytest.mark.parametrize('table',['bars_daily','security_master','calendar','universe_membership'])
def test_work_p1_006_unknown_flag_cannot_be_formal_pit(tmp_path,table):
    t=deepcopy(BASE);t[table][0].update(quality_status='UNKNOWN_AVAILABILITY',reason_code='SOURCE_HISTORY_UNVERIFIED')
    with pytest.raises((ContractError,DataQualityError)):
        publish_snapshot(t,PROVENANCE,tmp_path/'snapshots')
def test_work_p1_007_timezone_must_not_be_external_file(tmp_path):
    zone=tmp_path/'outside.tzif';zone.write_bytes(importlib.resources.files('tzdata.zoneinfo').joinpath('UTC').read_bytes())
    with pytest.raises(ContractError):iana(str(zone))
def test_work_p1_008_revision_overflow_is_counted_rejected():
    r=deepcopy(BASE['bars_daily'][0]);r['revision_id']=2**63
    v=validate_table('bars_daily',[r])
    assert (v.report.input,v.report.valid,v.report.rejected)==(1,0,1)
def test_work_p1_009_offset_submicrosecond_precision_rejected():
    with pytest.raises(TimestampResolutionError):utc('2024-01-02T16:00:00.000000+00:00:00.000000001')
def test_control_known_availability_is_publishable(tmp_path):
    assert publish_snapshot(deepcopy(BASE),PROVENANCE,tmp_path/'snapshots')
def test_control_max_int64_revision_accepted():
    r=deepcopy(BASE['bars_daily'][0]);r['revision_id']=2**63-1
    assert validate_table('bars_daily',[r]).report.valid==1
def test_control_utc_microsecond_preserved():
    assert utc('2024-01-02T16:00:00.123456000Z')==datetime(2024,1,2,16,0,0,123456,tzinfo=UTC)
