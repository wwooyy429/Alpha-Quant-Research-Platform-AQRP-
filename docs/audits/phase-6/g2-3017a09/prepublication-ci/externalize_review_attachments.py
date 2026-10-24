from pathlib import Path
from datetime import datetime,UTC
import hashlib,json,shutil,subprocess,zipfile
O=Path(__file__).resolve().parent
R=Path(r'C:/Users/11638/AppData/Local/AQRP/checkouts/phase1-57461d5d-5de2-4c78-9b4e-5fad2b5ccb29')
D=R/'docs/audits/phase-6/g2-3017a09'
C='3017a097b49ecdae68228ca9a417fcd03c313200';H='e0d8d79cecbb0f3d36ace7fa9fdc983c13b30bee'
F=O/'premerge-ci/ci-40087892421'
git=lambda *a:subprocess.check_output(['git',*a],cwd=R)
sha=lambda b:hashlib.sha256(b).hexdigest()
save=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
assert git('rev-parse','HEAD').decode().strip()==H and not git('status','--porcelain')
proof=json.loads((F/'VARIANT_IDENTITY_PROVENANCE.json').read_bytes())
assert proof['findings']==proof['recomputed_matches']==54
assert all(x['independent_recomputation_match'] for x in proof['classification'])
classification=json.loads((F/'SCANNER_FIELD_CLASSIFICATION.json').read_bytes())
names=sorted(Path(n).name for n in classification['paths']);assert len(names)==7
identity=json.loads(git('show',C+':docs/audits/phase-6/IMPLEMENTATION_IDENTITY.json'))
protected={x['path'] for x in identity['preserved_files']+identity['current_files']}
index=json.loads((D/'EVIDENCE_INDEX.json').read_bytes())
archive=Path(index['original_external_source'])/'EVIDENCE.zip'
assert archive.stat().st_size==index['original_external_archive']['bytes']
manifest=json.loads((D/'received/EVIDENCE_MANIFEST.json').read_bytes())
entries={e['path']:e for e in manifest['files']}
X=O/'external-review-originals';X.mkdir(exist_ok=False)
out=[]
with zipfile.ZipFile(archive) as z:
 for n in names:
  rel='docs/audits/phase-6/g2-3017a09/received/'+n
  assert rel not in protected
  assert subprocess.run(['git','cat-file','-e',C+':'+rel],cwd=R,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode!=0
  raw=(D/'received'/n).read_bytes();e=entries[n]
  assert len(raw)==e['bytes'] and sha(raw)==e['sha256'] and z.read(n)==raw
  (X/n).write_bytes(raw);assert (X/n).read_bytes()==raw
  out.append({**e,'storage':'EXTERNAL_ORIGINAL_BYTES_NOT_REDACTED','direct_read_path':str(X/n),'original_archive_path':str(archive),'original_zip_member':n,'also_retained_in_git_history':H+':'+rel})
external={'scope':'Seven verbatim reviewer attachments retained externally, with complete original sealed audit ZIP and immutable prior Git history; no security scanner rules changed and no evidence erased.','reviewed_sha':C,'failed_archival_head':H,'failed_CI_run':40087892421,'external_files':out,'original_archive_receipt':index['original_external_archive'],'scanner_classification':'54 public engineering configuration hashes independently recomputed; not credentials. Failed CI remains failure. New documentation-only HEAD must pass fresh unchanged scanner and complete CI.','provenance':'prepublication-ci/VARIANT_IDENTITY_PROVENANCE.json','unchanged':'Source/tests/tools/workflow/locks/.gitleaks.toml/.gitattributes/5016 frozen files','created_utc':datetime.now(UTC).isoformat()}
save(D/'EXTERNAL_ORIGINALS.json',external)
save(X/'MANIFEST.json',external)
index['received_files_copied_verbatim']=[e for e in index['received_files_copied_verbatim'] if e['path'] not in names]
index['external_small_original_files']=out
index['storage_policy_update']={'reason':'Public engineering variant-identity hashes in seven new reviewer attachments triggered generic-api-key during H final secret scan. All 54 independently recomputed. Preserve raw originals externally instead of altering scanner or original audit files.','original_manifest_scope':'received/EVIDENCE_MANIFEST.json describes all 348 files in the original sealed349-member ZIP, not the subset copied into Git. It remains byte-identical.','external_originals':'EXTERNAL_ORIGINALS.json','new_CI_required':True,'old_CI_failure_retained':True}
save(D/'EVIDENCE_INDEX.json',index)
A=D/'prepublication-ci';A.mkdir()
for n in ('VARIANT_IDENTITY_PROVENANCE.json','SCANNER_FIELD_CLASSIFICATION.json','WINDOWS_FAILURE.json','FAILED_WINDOWS_scan-findings.json','FAILED_WINDOWS_secret-scan.log','FAILED_WINDOWS_environment.json','FAILED_WINDOWS_junit.xml','windows-job-120854440506-official-original.log'):
 shutil.copyfile(F/n,A/n)
save(A/'RETAINED_EXECUTION.json',{'scope':'Original failure, not reclassified as PASS. This is a developer administrative archival correction, not GPT Work G2.','failed_head':H,'reviewed_implementation':C,'original_run':40087892421,'Windows_full_SDK':{'tests':1567,'failures':0,'errors':0,'skipped':0},'overall_job':'failure at final unchanged pinned secret scanner','raw_official_original_zip':json.loads((F/'WINDOWS_FAILURE.json').read_bytes()),'all_original_attempt_files_directory':str(F),'originals_externalized':'../EXTERNAL_ORIGINALS.json','source_and_security_controls_changed':False})
prefix='> 2026-10-24 发布前归档修正：用户已验收八项并有条件授权发布。归档头 `'+H+'` 的 Windows CI 在最终密钥扫描失败，1567用例全通过也不能把该CI改判成功。54项触发均已由独立stdlib重算为公开工程配置哈希。7份新审查附件按原字节完整保留于外部直读目录、原始封存ZIP及旧Git历史，定位/成员/长度/SHA见 [EXTERNAL_ORIGINALS.json](EXTERNAL_ORIGINALS.json)，原报告/manifest原字节不改；其余Git镜像清单见 EVIDENCE_INDEX。密钥扫描规则、业务、测试、工具、CI及锁完全不改，新文档头须重新CI通过才可合并。以下原接收说明保留为当时历史。\n\n'
p=D/'DEVELOPER_RESPONSE.md';p.write_bytes(prefix.encode()+p.read_bytes())
for n in names:(D/'received'/n).unlink()
save(O/'EXTERNALIZATION_RECEIPT.json',{'result':'PASS_ORIGINAL_BYTES_RETAINED','files':out,'original_manifest_unchanged':sha((D/'received/EVIDENCE_MANIFEST.json').read_bytes())==index['original_external_archive']['manifest_sha256'],'source_security_controls_unchanged':not git('diff',H,'--','src','tests','tools','.github','requirements.lock','requirements-ui-windows.lock','requirements-ui-linux.lock','.gitleaks.toml','.gitattributes','pyproject.toml')})
print(json.dumps({'external_files':len(out),'public_config_hashes_recomputed':54,'scanner_controls_changed':False,'new_CI_required':True}))
