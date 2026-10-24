from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
import hashlib, json, re, sys, traceback, zipfile, zlib

SRC = Path('C:/Users/11638/AppData/Local/AQRP/reviews/p6-g2-recheck-3017a09-independent-20261024')
OUT = Path('C:/Users/11638/AppData/Local/AQRP/runs/p6-g2-pass-3017a09-20261024/receipt-check')
FIXED = '3017a097b49ecdae68228ca9a417fcd03c313200'
CHUNK = 4 * 1024 * 1024
res = {'kind':'administrative_received_evidence_integrity_check', 'not_an_independent_G2_audit':True, 'source_directory':str(SRC), 'fixed_sha':FIXED, 'started_utc':datetime.now(timezone.utc).isoformat(), 'errors':[]}

def require(ok, detail):
    if not ok:
        res['errors'].append(detail)

def stream_hash(p):
    n = 0
    h = hashlib.sha256()
    with p.open('rb') as f:
        while b := f.read(CHUNK):
            n += len(b)
            h.update(b)
    return n, h.hexdigest()

def safe_name(n):
    return bool(n) and not n.startswith('/') and '\\' not in n and ':' not in n and '\x00' not in n and all(v not in ('', '.', '..') for v in n.split('/')) and not PurePosixPath(n).is_absolute()

try:
    receipt = json.loads((SRC/'RECEIPT.json').read_bytes())
    manifest_bytes = (SRC/'EVIDENCE_MANIFEST.json').read_bytes()
    manifest = json.loads(manifest_bytes)
    require(receipt.get('fixed_sha') == FIXED, 'Receipt fixed SHA differs')
    require(manifest.get('fixed_sha') == FIXED, 'Manifest fixed SHA differs')
    manifest_hash = hashlib.sha256(manifest_bytes).hexdigest()
    require(manifest_hash == receipt.get('manifest_sha256'), 'Manifest SHA differs from receipt')
    files = manifest['files']
    require(isinstance(files, list), 'Manifest files is not a list')
    declared = {}
    casefold = set()
    for row in files:
        p = row['path']
        require(safe_name(p), f'Unsafe manifest path: {p!r}')
        require(p not in declared, f'Duplicate manifest path {p!r}')
        require(p.casefold() not in casefold, f'Casefold duplicate manifest path {p!r}')
        require(isinstance(row.get('bytes'), int) and row['bytes'] >= 0, f'Invalid bytes {p!r}')
        require(bool(re.fullmatch('[0-9a-f]{64}', str(row.get('sha256','')))), f'Invalid SHA {p!r}')
        declared[p] = row
        casefold.add(p.casefold())
    require(len(files) == receipt.get('manifest_files'), 'Manifest count differs from receipt')
    archive_name = receipt['archive']
    require(safe_name(archive_name) and '/' not in archive_name, 'Unsafe archive filename')
    archive = SRC/archive_name
    before = archive.stat()
    print('Hashing original archive...', flush=True)
    size, digest = stream_hash(archive)
    require(size == receipt.get('bytes'), 'Archive bytes differ from receipt')
    require(digest == receipt.get('sha256'), 'Archive SHA256 differs from receipt')
    res['archive'] = {'path':str(archive), 'bytes':size, 'sha256':digest, 'receipt_bytes':receipt.get('bytes'), 'receipt_sha256':receipt.get('sha256')}
    res['manifest'] = {'bytes':len(manifest_bytes), 'sha256':manifest_hash, 'declared_file_count':len(files)}
    print(f'Archive size/SHA read; checking {len(files)} manifest entries...', flush=True)
    members = []
    external = {}
    with zipfile.ZipFile(archive) as z:
        infos = z.infolist()
        names = [i.filename for i in infos]
        require(len(names) == len(set(names)), 'Duplicate ZIP member names')
        require(len(names) == len({n.casefold() for n in names}), 'Casefold duplicate ZIP member names')
        for n in names:
            require(safe_name(n), f'Unsafe ZIP member {n!r}')
        require(len(infos) == receipt.get('zip_members'), 'ZIP count differs from receipt')
        expected = set(declared) | {'EVIDENCE_MANIFEST.json'}
        missing = sorted(expected-set(names))
        extra = sorted(set(names)-expected)
        require(not missing, f'Missing ZIP members: {missing!r}')
        require(not extra, f'Extra ZIP members: {extra!r}')
        res['exact_member_sets'] = {'expected_count':len(expected), 'actual_count':len(infos), 'missing':missing, 'extra':extra}
        total = 0
        for idx, info in enumerate(infos, 1):
            require(not info.is_dir(), f'Unexpected ZIP directory {info.filename!r}')
            require(not (info.flag_bits & 1), f'Encrypted ZIP member {info.filename!r}')
            require(((info.external_attr >> 16) & 0o170000) != 0o120000, f'ZIP symlink {info.filename!r}')
            h = hashlib.sha256()
            crc = 0
            n = 0
            with z.open(info) as f:
                while b := f.read(CHUNK):
                    h.update(b)
                    crc = zlib.crc32(b, crc)
                    n += len(b)
            sha = h.hexdigest()
            crc &= 0xffffffff
            total += n
            require(n == info.file_size, f'ZIP header size mismatch {info.filename!r}')
            require(crc == info.CRC, f'ZIP CRC mismatch {info.filename!r}')
            if info.filename == 'EVIDENCE_MANIFEST.json':
                require(sha == manifest_hash and n == len(manifest_bytes), 'ZIP manifest differs from external manifest')
            elif info.filename in declared:
                row = declared[info.filename]
                require(n == row['bytes'], f'Manifest size mismatch {info.filename!r}')
                require(sha == row['sha256'], f'Manifest SHA mismatch {info.filename!r}')
            members.append({'path':info.filename, 'bytes':n, 'sha256':sha, 'crc32':f'{crc:08x}', 'CRC_matches_header':crc == info.CRC, 'manifest_matches':info.filename == 'EVIDENCE_MANIFEST.json' or (n == declared.get(info.filename,{}).get('bytes') and sha == declared.get(info.filename,{}).get('sha256'))})
            if info.filename in ('REPORT.md', 'DEVELOPER_HANDOFF.txt', 'FINDINGS.json'):
                en, eh = stream_hash(SRC/info.filename)
                equal = en == n and eh == sha
                require(equal, f'External copy differs from ZIP original: {info.filename}')
                external[info.filename] = {'bytes':en, 'sha256':eh, 'matches_ZIP_original_bytes':equal}
            if idx % 50 == 0:
                print(f'Checked {idx}/{len(infos)} members', flush=True)
        res['members_checked'] = len(members)
        res['declared_files_checked'] = len(declared)
        res['uncompressed_bytes_streamed'] = total
    require(set(external) == {'REPORT.md','DEVELOPER_HANDOFF.txt','FINDINGS.json'}, 'Required external reports missing from ZIP')
    report = (SRC/'REPORT.md').read_text(encoding='utf-8-sig')
    handoff = (SRC/'DEVELOPER_HANDOFF.txt').read_text(encoding='utf-8-sig')
    findings = json.loads((SRC/'FINDINGS.json').read_bytes())
    require(FIXED in report, 'Fixed SHA absent from REPORT.md')
    require(FIXED in handoff, 'Fixed SHA absent from DEVELOPER_HANDOFF.txt')
    require(FIXED in json.dumps(findings,ensure_ascii=False), 'Fixed SHA absent from FINDINGS.json')
    after = archive.stat()
    require((before.st_size,before.st_mtime_ns) == (after.st_size,after.st_mtime_ns), 'Original archive changed during validation')
    res['external_report_copies'] = external
    res['fixed_SHA_in_report_handoff_findings'] = all(FIXED in x for x in (report, handoff, json.dumps(findings,ensure_ascii=False)))
    (OUT/'MEMBER_VERIFICATION.json').write_text(json.dumps({'members':members},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
except BaseException as exc:
    res['errors'].append({'exception':type(exc).__name__, 'message':str(exc), 'traceback':traceback.format_exc()})
res['completed_utc'] = datetime.now(timezone.utc).isoformat()
res['result'] = 'PASS' if not res['errors'] else 'FAIL'
res['scope_limit'] = 'Bytes, hashes, CRC, member safety and fixed identity only; no G2 reevaluation, business/test execution, acceptance, merge, release or deployment.'
(OUT/'VERIFICATION.json').write_text(json.dumps(res,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(res,indent=2,ensure_ascii=False),flush=True)
sys.exit(0 if res['result'] == 'PASS' else 1)
