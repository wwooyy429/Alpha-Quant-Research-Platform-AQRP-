from pathlib import Path
import json
O=Path(__file__).parent
p=O/'EXECUTION_DISPOSITIONS.json';d=json.loads(p.read_bytes())
d['seal_first_attempt']='Stopped before copying inputs or creating ZIP: refs saved as CRLF versus raw Git stdout LF differed in byte representation. Revised to exact ref-name/full-SHA mapping equality; original failed log and script preserved. No repository/tag drift.'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

