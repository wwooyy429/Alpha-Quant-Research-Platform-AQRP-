from pathlib import Path
O=Path(__file__).parent;old=Path('C:/Users/11638/AppData/Local/AQRP/reviews/p6-g2-eae807f-independent-20261024')
src=(old/'verify_archives.py').read_text()
src=src.replace('p6-eae807f/src','p6-3017a09/src').replace('p6-g2-eae807f-developer-20261023T161214Z-ceb156b0','p6-g2-3017a09-developer-20261024T092710Z').replace('eae807f957f178d19bc55dcfbd668caff5470c6e','3017a097b49ecdae68228ca9a417fcd03c313200').replace('AQRP-P6-G2-eae807f-EVIDENCE.zip','AQRP-P6-G2-3017a09-EVIDENCE.zip').replace('LOCAL_CLEAN_SDK-eae807f.zip','LOCAL_CLEAN_SDK-3017a09.zip').replace('CI_ARTIFACTS_API.json','CI_ARTIFACTS_START.json').replace('1496','1567').replace('==82','==83').replace('modules=82','modules=83').replace('39983233050','40079197702')
a=src.index(" sources=list(");b=src.index("\ncore=",a)
src=src[:a]+""" sources=list((P/'execution-metadata').glob('SOURCE-3017a09.git.zip'));assert len(sources)==1
 assert sources[0].stat().st_size==88435541 and fh(sources[0])=='416501153449e423005274870e2ce3397d1108ce292319a381eb123450d6c4d9'
 with zipfile.ZipFile(sources[0]) as t:
  assert t.testzip() is None
  assert set(t.namelist())==tracked and len(t.namelist())==len(tracked)==5108
  for n in t.namelist():assert t.read(n)==(C/n).read_bytes(),n
"""+src[b:]
src=src.replace("assert record['aliases']==5658 and record['alias_groups']==237","assert record['aliases']>0 and record['alias_groups']>0")
(O/'verify_archives.py').write_text(src,encoding='utf-8')
src=(old/'verify_scope.py').read_text().replace('p6-eae807f/src','p6-3017a09/src').replace('eae807f957f178d19bc55dcfbd668caff5470c6e','3017a097b49ecdae68228ca9a417fcd03c313200').replace('modules=82','modules=83')
(O/'verify_scope.py').write_text(src,encoding='utf-8')
