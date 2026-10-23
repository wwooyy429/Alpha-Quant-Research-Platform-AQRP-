from pathlib import Path
O=Path(__file__).parent;old=O.parent/'p5-g1-recheck-5262032-independent';fix='bfdcf30e525ff802ea483974f58163eedc029ce8'
s=(old/'independent_original_math.py').read_text(encoding='utf-8').replace("C=O.parent/'p5-g1-review-5262032'","C=pathlib.Path('E:/WORK/AQRP-audits/p5-bfdcf30/src')").replace('5262032bee4f631f68763e57510e1878945f6b8c',fix)
(O/'independent_original_math.py').write_text(s,encoding='utf-8')
s=(old/'independent_revision_math.py').read_text(encoding='utf-8').replace("P=O.parent/'p5-g1-review-5262032/docs/audits/phase-5'","P=Path('E:/WORK/AQRP-audits/p5-bfdcf30/src/docs/audits/phase-5')").replace('5262032bee4f631f68763e57510e1878945f6b8c',fix)
(O/'independent_revision_math.py').write_text(s,encoding='utf-8')
