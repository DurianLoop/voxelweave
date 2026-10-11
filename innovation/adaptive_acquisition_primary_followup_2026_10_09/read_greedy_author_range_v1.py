"""Bounded static reading only; author modules/notebook never imported or executed."""
import sys,gzip,json
from pathlib import Path
from resource_guard_v1 import HERE,guard,entry,dump
name=sys.argv[1];lo=int(sys.argv[2]);hi=int(sys.argv[3]);base=HERE/'greedy_selected_sources_attempt01'
mapping={'train_policy':'src__train_policy.py.gz','compute_snr':'src__compute_snr.py.gz','data_loading':'src__helpers__data_loading.py.gz','policy_utils':'src__policy_model__policy_model_utils.py.gz'}
if name=='MI_cells':
 p=base/'mi_notebook_cells.json.gz';parts=json.loads(gzip.decompress(p.read_bytes()));n=len(parts)
else:
 assert name in mapping;p=base/mapping[name];parts=gzip.decompress(p.read_bytes()).decode('utf-8').splitlines();n=len(parts)
assert 0<=lo<hi<=n;guard();out=HERE/'greedy_author_range_exposure_attempt01';out.mkdir(exist_ok=True);rp=out/f'{name}_{lo:03d}_{hi:03d}.json';assert not rp.exists()
dump(rp,dict(source=entry(p),start=lo,end_exclusive=hi,text_actually_read=False,author_code_executed=False))
for i in range(lo,hi):
 if name=='MI_cells':print(f"[MI_cells:{i}]\n{parts[i]['source']}\n")
 else:print(f'[{name}:{i+1}] {parts[i]}')
