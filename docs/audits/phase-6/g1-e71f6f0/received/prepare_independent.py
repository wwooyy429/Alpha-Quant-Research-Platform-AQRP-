"""Prepare independent reviewer references from the reviewer's prior arithmetic definitions only.
Never imports developer functions to derive expected answers.
"""
from pathlib import Path
O=Path(__file__).parent
prior=(O.parent/'p6-g1-f7a1a68-independent/independent_design.py').read_text(encoding='utf-8')
prefix=prior.split("cases=json.loads")[0].replace("p6-f7a1a68/src","p6-e71f6f0/src").replace("FIX='f7a1a68c5f747090f8c8a0e934f2fea859aec998'","FIX='e71f6f090b102e4abfd70a5999e495f49546a1b5'")
(O/'reviewer_primitives.py').write_text(prefix,encoding='utf-8')
print('Prior independent typed/non-numeric primitives copied; no developer oracle used.')

