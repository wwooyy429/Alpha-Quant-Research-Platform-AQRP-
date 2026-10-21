"""Recompute original query identities using recorded roots; no product mutation."""
import json
from dataclasses import asdict
from datetime import date, datetime
from pathlib import Path, PureWindowsPath, PurePosixPath
from aqrp.core.canonical import digest
from aqrp.core.contracts import QuerySpec, SnapshotRef
from aqrp.core.time import utc

ROOT=Path(__file__).resolve().parent
bases=[next((ROOT/'runs').iterdir())]
bases.extend(p.parent for p in (ROOT/'zip-replay').glob('*/*/environment.json'))
assert len(bases)==3
checks=[]
for base in bases:
    env=json.loads((base/'environment.json').read_bytes())
    config=json.loads((base/'smoke-config.json').read_bytes())
    receipt=json.loads((base/'smoke-run.json').read_bytes())
    manifest=json.loads((base/'smoke-snapshot.json').read_bytes())
    spec=QuerySpec(tuple(config['security_ids']),config['market_id'],config['calendar_id'],tuple(date.fromisoformat(d) for d in config['session_range']),tuple(config['fields']),config['price_basis'])
    q=asdict(spec);q.pop('request_id')
    ref=SnapshotRef(base/'dataset',config['snapshot_id'],config['manifest_hash'])
    expected=digest({'snapshot':asdict(ref)|{'root':receipt['dataset']},'cutoff':utc(config['as_of']),'spec':q,'rule_version':'pit/1.0.0','provenance':manifest['provenance']})
    assert expected==receipt['query_hash']
    checks.append({'run_id':env['run_id'],'kind':'data','recorded_root':receipt['dataset'],'query_hash':expected})
    original_root=(PureWindowsPath(env['run_root']) if PureWindowsPath(env['run_root']).drive else PurePosixPath(env['run_root']))/'factor-dataset'
    for cfgpath in (base/'factor-runs').glob('*/config.json'):
        cfg=json.loads(cfgpath.read_bytes())
        manifest=json.loads((base/'factor-dataset'/cfg['snapshot_id']/'manifest.json').read_bytes())
        spec=QuerySpec(tuple(cfg['security_ids']),cfg['market_id'],cfg['calendar_id'],(date.fromisoformat(cfg['sessions'][0][0]),date.fromisoformat(cfg['target_session'])),('close','volume'),'split_adjusted')
        q=asdict(spec);q.pop('request_id')
        ref=SnapshotRef(base/'factor-dataset',cfg['snapshot_id'],cfg['manifest_hash'])
        expected=digest({'snapshot':asdict(ref)|{'root':str(original_root)},'cutoff':utc(cfg['decision_time']),'spec':q,'rule_version':'pit/1.0.0','provenance':manifest['provenance']})
        assert expected==cfg['query_hash']
        checks.append({'run_id':env['run_id'],'kind':cfg['spec']['factor_id'],'recorded_root':str(original_root),'query_hash':expected})
assert len(checks)==12
(ROOT/'original-query-identity.json').write_text(json.dumps({'audit':'GPT Work 补充审核','target_sha':'c70727c39182f81ee142730da9a9833a51581cd1','status':'PASS','checks':checks,'finished_at':datetime.now().astimezone().isoformat(),'scope':'Original root-sensitive identities recomputed separately from relocated SDK result replay; no raw evidence rewritten'},ensure_ascii=False,indent=2),encoding='utf-8')
print('PASS: 12 original query identities recomputed using recorded Windows/Linux/local roots.')
