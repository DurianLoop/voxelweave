"""Print precise JATS block ranges for actual reading; no automatic reading attestation."""
import json,sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
root=Path(__file__).resolve().parent/'source_cache/task_adaptation_direct_fulltexts_2026-10-03'
blocks=json.loads((root/(sys.argv[1]+'_blocks.json')).read_text(encoding='utf-8'))
for i in range(int(sys.argv[2]),min(int(sys.argv[3]),len(blocks))):
    x=blocks[i]
    print('[%04d %s] %s\n'%(i,x['tag'],x['text']))
