"""Predeclared developer negative: complete same-bundle history must retain Task pointer boundary."""
import datetime
import hashlib
import importlib.metadata
import json
import pathlib
import sqlite3
import traceback
import uuid

from aqrp.core.canonical import canonical
from aqrp.core.errors import ContractError
from aqrp.factors.admission import bundle_hash
from aqrp.services.task_requests import initialize
from aqrp.services.task_state import TaskState
from aqrp.services.tasks import TaskService

O = pathlib.Path(__file__).resolve().parent
out = O / ('migration-pointer-probe-' + str(uuid.uuid4()))
out.mkdir()
(out / 'PROBE_SCRIPT.py').write_bytes(pathlib.Path(__file__).read_bytes())
W = out / 'workspace'
report = {'purpose': 'Developer same-bundle migration negative; not formal Test, independent audit or financial approval', 'candidate_sha': 'b6ed148ba73e478ebc4b6581403714fb39781316', 'expected_bundle': 'd9d020a80111e2f679e3bb00b1151d6961e28e9bf0569c80cd03169352e77f4a', 'actual_bundle': bundle_hash(), 'package_version': importlib.metadata.version('aqrp'), 'declared_mutation': 'After healthy complete same-bundle migration control, change only SQL Task completion.file to ../../relocated-original-completion.json and put exact original completion bytes there. Original task/run bytes and completion sha remain unchanged.', 'expected': {'migration': 'ADMISSION_HISTORY_UNVERIFIED', 'new_admission': False}, 'started_at_utc': datetime.datetime.now(datetime.UTC).isoformat()}
assert report['actual_bundle'] == report['expected_bundle']
(out / 'DECLARED_PROBE.json').write_bytes(canonical(report))
print(out, flush=True)


def save(name, item):
    (out / name).write_bytes(canonical(item))


def backup(name, state):
    with sqlite3.connect(state.db) as source, sqlite3.connect(out / name) as target:
        source.backup(target)


def history(state):
    with state.budget.transaction() as c:
        return state.budget.history(c)


def strip_schema(state):
    # Explicit pre-control-schema simulator: preserve all original business rows,
    # Task files, source manifests, trial/run events and actual successful result.
    with state.transaction() as c:
        names = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        for name in names:
            if name.startswith(('admission_', 'execution_plan')) or name in {'budget_domains', 'admissions', 'trial_claims', 'legacy_execution_owners'}:
                c.execute('DROP TABLE "' + name + '"')
    state.budget.anchor.unlink()


try:
    initialize(W, 'a' * 40)
    service = TaskService(W)
    frozen = service.freeze({'kind': 'research', 'factor_ids': ['momentum'], 'horizons': [1], 'start': '2024-01-06', 'end': '2024-01-06'})
    task = service.submit(frozen, 'original-source')['task_id']
    done = service.work(task)
    assert done['status'] == 'SUCCEEDED', done
    save('ORIGINAL_SUCCEEDED_STATUS.json', done)
    save('ORIGINAL_HISTORY.json', history(service.state))
    backup('ORIGINAL_AUTHORITY.sqlite', service.state)
    strip_schema(service.state)
    healthy = TaskState(W)
    healthy_status = TaskService(W).status(task)
    assert healthy_status['status'] == 'SUCCEEDED', healthy_status
    save('HEALTHY_MIGRATION_CONTROL.json', {'status': healthy_status, 'history': history(healthy)})
    strip_schema(healthy)
    backup('HEALTHY_PRE_SCHEMA.sqlite', healthy)
    original = dict(healthy.get(task))
    pointer = json.loads(original['completion'])
    raw = (W / 'tasks' / task / pointer['file']).read_bytes()
    (out / 'ORIGINAL_COMPLETION_BYTES.json').write_bytes(raw)
    before_files = {p: p.read_bytes() for d in ('tasks', 'research-runs', 'research-campaigns') for p in (W / d).rglob('*') if p.is_file() and p.suffix in ('.json', '.jsonl', '.html')}
    (W / 'relocated-original-completion.json').write_bytes(raw)
    pointer['file'] = '../../relocated-original-completion.json'
    with healthy.transaction() as c:
        c.execute('UPDATE tasks SET completion=? WHERE id=?', (canonical(pointer).decode(), task))
    mutated = dict(healthy.get(task))
    save('SINGLE_LOGICAL_MUTATION.json', {'before': original, 'after': mutated, 'changed_fields': [k for k in original if original[k] != mutated[k]], 'original_completion_sha256': hashlib.sha256(raw).hexdigest()})
    backup('CORRUPTED_PRE_SCHEMA.sqlite', healthy)
    try:
        migrated = TaskState(W)
    except ContractError as exc:
        report['actual_migration'] = 'REFUSED'
        report['code'] = exc.code
        report['traceback'] = traceback.format_exc()
        report['new_admission'] = False
    else:
        report['actual_migration'] = 'ACCEPTED'
        report['history_after_migration'] = history(migrated)
        report['original_status_after_migration'] = TaskService(W).status(task)
        backup('ACCEPTED_MIGRATION.sqlite', migrated)
        after = TaskService(W).submit(frozen, 'after-invalid-original-pointer')
        report['new_task'] = after
        report['new_admission'] = after['status'] == 'QUEUED'
        report['history_after_new_submit'] = history(migrated)
        backup('AFTER_NEW_SUBMIT.sqlite', migrated)
    report['original_task_run_bytes_preserved'] = all(p.read_bytes() == b for p, b in before_files.items())
    report['expected_refusal_observed'] = report['actual_migration'] == 'REFUSED' and report.get('code') == 'ADMISSION_HISTORY_UNVERIFIED' and report['new_admission'] is False
except BaseException:
    report['unexpected_probe_error'] = traceback.format_exc()
finally:
    report['finished_at_utc'] = datetime.datetime.now(datetime.UTC).isoformat()
    save('RESULT.json', report)
    entries = []
    for p in out.rglob('*'):
        if p.is_file() and p.name != 'MANIFEST.json':
            raw = p.read_bytes()
            entries.append({'path': p.relative_to(out).as_posix(), 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)})
    save('MANIFEST.json', {'candidate_sha': report['candidate_sha'], 'bundle': report['actual_bundle'], 'files': entries})
    print(json.dumps({k: report.get(k) for k in ['actual_migration', 'code', 'new_admission', 'expected_refusal_observed', 'original_task_run_bytes_preserved', 'unexpected_probe_error']}, indent=2), flush=True)
raise SystemExit(0 if report.get('expected_refusal_observed') else 1)
