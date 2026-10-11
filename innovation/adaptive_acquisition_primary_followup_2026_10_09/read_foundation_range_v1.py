"""Expose bounded fixed-version text; record actual reading separately."""
import sys,gzip,json,time
from resource_guard_v1 import HERE,guard,read,entry,dump
name=sys.argv[1];lo=int(sys.argv[2]);hi=int(sys.argv[3]);assert name in ('swin_pretraining','brainsegfounder')
d=HERE/('foundation_primary_html_attempt01/swin_pretraining' if name=='swin_pretraining' else 'brainsegfounder_identity_html_attempt02')
p=d/'blocks.json.gz';blocks=json.loads(gzip.decompress(p.read_bytes()));assert 0<=lo<hi<=len(blocks);guard()
out=HERE/'foundation_range_exposure_attempt01';out.mkdir(exist_ok=True);rp=out/f'{name}_{lo:03d}_{hi:03d}.json';assert not rp.exists()
dump(rp,dict(source=entry(p),start=lo,end_exclusive=hi,text_actually_read=False,blocks_exposed=hi-lo,
 scope='Exposure only; inspected returned chunks recorded separately after actual reading'))
for v in blocks[lo:hi]:print(f"[{name}:{v['index']}:{v['tag']}:{v['id']}]\n{v['text']}\n")
