"""Print only explicitly requested text anchors to avoid invisible truncated reading."""
import sys,json
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8');folder=Path(__file__).resolve().parent/'source_cache/global_local_task_fulltexts_2026-10-03';key,start,end=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]);blocks=json.loads((folder/(key+'_blocks.json')).read_text(encoding='utf-8'))
for i in range(start,min(end,len(blocks))):print('[%04d %s] %s\n'%(i,blocks[i]['tag'],blocks[i]['text']))
