"""Display contiguous extracted blocks in bounded batches; actual reading is recorded separately."""
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parent/'primary_xml_attempt01'
key=sys.argv[1]
assert key in {'acquisition','unlearning','bezier'}
blocks=json.loads((root/(key+'_blocks.json')).read_text(encoding='utf-8'))
sys.stdout.reconfigure(encoding='utf-8')
if len(sys.argv)==2:
    ranges=[];start=0;size=0
    for block in blocks:
        if size+len(block['text'])>17000 and block['index']>start:
            ranges.append([start,block['index'],size]);start=block['index'];size=0
        size+=len(block['text'])
    ranges.append([start,len(blocks),size]);print(json.dumps(dict(key=key,ranges=ranges)))
else:
    start,end=map(int,sys.argv[2:4]);assert 0<=start<end<=len(blocks)
    for block in blocks[start:end]:
        print(f"[{key} {block['index']} {block['kind']} {block['id']}] {block['text']}")
