"""Expose bounded source text; completion of reading is recorded separately after tool inspection."""
import sys,gzip,json,hashlib,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import entry,dump,resource_guard
name=sys.argv[1];lo=int(sys.argv[2]);hi=int(sys.argv[3]);assert name in ('greedy','openmasc','active_fewshot')
p=HERE/'primary_html_attempt01'/name/'blocks.json.gz';blocks=json.loads(gzip.decompress(p.read_bytes()));assert 0<=lo<hi<=len(blocks)
r=resource_guard();remaining=22_800_000
for d,cap in ((ROOT/'six_resolution_training_preparation_2026_10_09',7_000_000),(ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09',20_000_000),(ROOT/'gin_accepted_primary_followup_2026_10_09',6_000_000),(HERE,2_000_000)):
    size=sum(v.stat().st_size for v in d.rglob('*') if v.is_file());assert size<cap;remaining+=cap-size
assert r['workspace_free_bytes']-remaining>=8_000_000_000
out=HERE/'range_display_attempt01';out.mkdir(exist_ok=True)
receipt=out/(name+f'_{lo:03d}_{hi:03d}.json');assert not receipt.exists()
dump(receipt,dict(source=entry(p),start=lo,end_exclusive=hi,blocks_exposed=hi-lo,text_actually_read=False,
    scope='Exposure recorded before actual assistant reading; final provenance appends inspected tool chunk IDs'))
for v in blocks[lo:hi]:print(f"[{name}:{v['index']}:{v['tag']}:{v['id']}]\n{v['text']}\n")
