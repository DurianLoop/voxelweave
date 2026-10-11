"""Print selected exact primary blocks for manual reading, no automatic attestation."""
import json,sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parent/'source_cache/sparse_task_joint_fulltexts_2026-10-03'
items=json.loads((ROOT/(sys.argv[1]+'_blocks.json')).read_text(encoding='utf-8'))
for i in range(int(sys.argv[2]),min(int(sys.argv[3]),len(items))):
    x=items[i];print('[%04d %s] %s\n'%(i,x['tag'],x['text']))
