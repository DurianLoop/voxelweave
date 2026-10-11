"""Print complete previously clipped index summaries; do not count them as papers."""
import json,sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
q=json.loads((Path(__file__).resolve().parent/'index_attempt01/receipt.json').read_text(encoding='utf-8'))
assert q['complete'] and not q['errors']
print(json.dumps([dict(key=r['key'],total=r['total_results'],
    entries=[{k:e[k] for k in ('id','title','authors','summary')} for e in r['entries']])
    for r in q['records'][:2]],ensure_ascii=False,indent=2))
