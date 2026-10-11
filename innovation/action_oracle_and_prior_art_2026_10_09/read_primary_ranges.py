"""Emit complete ordered primary blocks in <=15000-character batches; record extraction scope."""
import sys,json,gzip,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import resource_guard,read,entry,dump
started=time.perf_counter();resource_guard();key=sys.argv[1];start=int(sys.argv[2]);assert key in ['routing','active']
source=HERE/f'primary_xml_attempt01/{key}.blocks.json.gz';blocks=json.loads(gzip.decompress(source.read_bytes()))
selected=[];size=0
for b in blocks[start:]:
    text=f"[{b['index']}] {b['kind']} {'/'.join(b['scope'])}: {b['text']}\n"
    if selected and size+len(text)>15000:break
    selected.append(b);size+=len(text)
out=HERE/'reading_ranges_attempt01';out.mkdir(exist_ok=True)
next_index=selected[-1]['index']+1 if selected else start
record=dict(complete=True,key=key,start=start,next_index=next_index,total_blocks=len(blocks),emitted_indices=[b['index'] for b in selected],
    emitted_characters=size,maintext_read_provenance_not_automatically_asserted=True,source_bindings=[entry(Path(__file__)),entry(source)])
dump(out/f'{key}_{start:03d}_{next_index:03d}.json',record)
print(json.dumps({k:record[k] for k in ['key','start','next_index','total_blocks','emitted_characters']}))
for b in selected:print(f"[{b['index']}] {b['kind']} {'/'.join(b['scope'])}: {b['text']}")
