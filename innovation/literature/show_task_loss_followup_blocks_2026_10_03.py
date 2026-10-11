"""Show requested loss paper anchors; acquisition is not reading."""
import json,sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
folder=Path(__file__).resolve().parent/'source_cache/task_loss_followup_fulltext_2026-10-03'
blocks=json.loads((folder/'unified_focal_blocks.json').read_text(encoding='utf-8'))
start,end=map(int,sys.argv[1:3])
for index in range(start,min(end,len(blocks))):
    print('[%04d %s] %s\n'%(index,blocks[index]['tag'],blocks[index]['text']))
