from pathlib import Path
import json,hashlib
from fractions import Fraction
O=Path(__file__).parent
source=O/'INDEPENDENT_UNIVERSE_RECHECK.json';raw=source.read_bytes();record=json.loads(raw)
r=next(x for x in record['browser_tasks'] if x['kind']=='engineering_pipeline')
f=r['finance']['fills'][0]
assert f['signed_qty']=='9' and f['position_after']=='9' and f['position_before']=='0'
assert f['price']=='100.1' and f['fee']=='1' and f['slippage_cost']=='0.9' and f['execution_side']=='BUY'
cash=Fraction('1000')-9*Fraction('100.1')-1
equity=cash+9*100
assert cash==Fraction('98.1')==Fraction(r['finance']['account']['cash_total'])
assert equity==Fraction('998.1')==Fraction(r['finance']['account']['equity'])
(O/'INDEPENDENT_FILL_LITERAL_CHECK.json').write_text(json.dumps(dict(result='PASS',expected_source='Original independent golden economic convention, recomputed with stdlib Fraction; no AQRP expected generator',input_cash='1000',shares=9,price='100.1',fee='1',cash_fraction=str(cash),equity_fraction=str(equity),actual_first_fill=f,source_sha256=hashlib.sha256(raw).hexdigest()),indent=2)+'\n',encoding='utf-8')
print('9 shares,100.1price,1fee ->98.1cash/998.1equity independent Fraction PASS')
