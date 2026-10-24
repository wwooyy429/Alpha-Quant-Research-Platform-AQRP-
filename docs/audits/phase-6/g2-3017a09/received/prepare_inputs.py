from pathlib import Path
import shutil,hashlib,json
O=Path(__file__).parent;D=Path('C:/Users/11638/AppData/Local/AQRP/reviews/p6-g2-3017a09-developer-20261024T092710Z');prior=O.parent/'p6-g2-eae807f-independent-20261024'
target=O/'developer-inputs';target.mkdir()
def fh(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
records=[]
for n in ['AQRP-P6-G2-3017a09-EVIDENCE.zip','SEAL.json','GPT_WORK_G2_INSTRUCTIONS.md','PR_PUBLICATION_RECEIPT.json','PR_PUBLICATION_REQUEST.json','POST_PUBLICATION_REMOTE_VERIFICATION.json']:
 p=target/n;shutil.copyfile(D/n,p);assert fh(p)==fh(D/n);records.append(dict(path=str(p.relative_to(O)),sha256=fh(p),bytes=p.stat().st_size))
p=O/'prior-independent-inputs';p.mkdir()
for n in ['EVIDENCE.zip','EVIDENCE_MANIFEST.json','RECEIPT.json','REPORT.md','DEVELOPER_HANDOFF.txt','probe_search_variants.py','probe_cancellation_financial.py','probe_stock_pool.py']:
 shutil.copyfile(prior/n,p/n);assert fh(p/n)==fh(prior/n)
 records.append(dict(path=str((p/n).relative_to(O)),sha256=fh(p/n),bytes=(p/n).stat().st_size))
(O/'RECEIVED_COPY_VERIFICATION.json').write_text(json.dumps(dict(result='PASS',files=records),indent=2)+'\n',encoding='utf-8')
(O/'EXTERNAL_DOCUMENTATION.json').write_text(json.dumps(dict(access_date='2026-10-24',primary_sources=[dict(url='https://www.sqlite.org/c3ref/busy_handler.html',verified_fact='Having a busy handler does not guarantee that SQLite will call it; a deadlock risk can produce an immediate BUSY.'),dict(url='https://www.sqlite.org/rescode.html',verified_fact='The low8 bits identify the primary result code.'),dict(url='https://www.sqlite.org/pragma.html#pragma_journal_mode',scope='Official PRAGMA reference inspected; candidate must explicitly verify returned wal mode.')],limits='These documents do not prove the precise cause of the old native crashes or the exact C5 race. Actual independent controls are separate.'),indent=2)+'\n',encoding='utf-8')
print('Input copies preserved exact')
