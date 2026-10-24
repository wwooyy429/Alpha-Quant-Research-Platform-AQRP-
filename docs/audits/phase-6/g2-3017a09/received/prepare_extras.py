from pathlib import Path
import shutil
O=Path(__file__).parent;old=Path('C:/Users/11638/AppData/Local/AQRP/reviews/p6-g2-eae807f-independent-20261024');C=Path('E:/WORK/AQRP-audits/p6-3017a09/src')
first=(old/'run_original_extras.py').read_text();first=first[:first.index("args=[")].replace('p6-eae807f/src','p6-3017a09/src').replace('eae807f957f178d19bc55dcfbd668caff5470c6e','3017a097b49ecdae68228ca9a417fcd03c313200')
exec(compile(first,'unchanged-original-copies','exec'))
script=(old/'run_original_extras_rerun.py').read_text().replace('p6-eae807f/src','p6-3017a09/src').replace('eae807f957f178d19bc55dcfbd668caff5470c6e','3017a097b49ecdae68228ca9a417fcd03c313200')
(O/'run_original_extras.py').write_text(script,encoding='utf-8')
shutil.copyfile(old/'verify_installed_numbers.py',O/'verify_installed_numbers.py')
