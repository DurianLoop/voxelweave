"""Read-only inventory of known immutable text; never touches MRI/model/live files."""
import sys,time,json,ctypes,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
BASE=ROOT/'uncertainty_dmri_primary_completion_2026_10_09'
EXTENSIONS={'.json','.md','.txt','.jsonl','.xml','.html','.csv','.log','.py','.yml','.yaml','.toml'}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1_048_576),b''):h.update(b)
 return h.hexdigest()
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def dump(p,v):
 with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def guard(started):
 r=resource_guard();assert time.perf_counter()-started<120
 assert r['workspace_free_bytes']-2_000_000-2_000_000-3_000_000-2_800_000>=8_000_000_000
 assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<2_000_000
 return r
def physical(p):
 k=ctypes.windll.kernel32;k.GetFileAttributesW.argtypes=[ctypes.c_wchar_p];k.GetFileAttributesW.restype=ctypes.c_uint32
 attrs=k.GetFileAttributesW(str(p));assert attrs!=0xffffffff
 k.GetCompressedFileSizeW.argtypes=[ctypes.c_wchar_p,ctypes.POINTER(ctypes.c_uint32)];k.GetCompressedFileSizeW.restype=ctypes.c_uint32
 high=ctypes.c_uint32(0);ctypes.set_last_error(0);low=k.GetCompressedFileSizeW(str(p),ctypes.byref(high));assert low!=0xffffffff or ctypes.get_last_error()==0
 return dict(physical_bytes=int(high.value)*2**32+int(low),attributes=int(attrs),compressed=bool(attrs&0x800))
def main():
 sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();before=guard(started)
 index=BASE/'APPEND_CAPACITY_INDEX.json';proof=BASE/'APPEND_CAPACITY_PROOF.json';assert sha(index)=='3d4514b07456ea239c7f91ba20af3f36902362613f50ff72fe5ddb5cb07f2a96' and sha(proof)=='399977a77f7f76132d15a84e75f8623e85baa1dae7c727e6709d9c99a8461197'
 v=read(index);assert v['complete'] and not v['errors'] and v['cumulative_frozen_evidence_files']==6923
 chain=v['prior_chain']+[entry(index)];old=[]
 for b in chain:
  p=ROOT/b['path'];assert sha(p)==b['sha256'];q=read(p);assert q['complete'] and not q['errors'];old.extend(q.get('evidence_files',q.get('new_evidence_files',[])))
 assert len(old)==len({b['path'] for b in old})==6923
 closed=[ROOT/'full_real_intensity_v2_2026_10_09/full_real_pipeline_attempt01',ROOT/'tools']
 candidates=[];all_text_count=compressed_count=0;logical_total=physical_total=0
 for b in old:
  p=(ROOT/b['path']).resolve()
  if not p.is_relative_to(ROOT) or p.suffix.lower() not in EXTENSIONS or any(p.is_relative_to(folder) for folder in closed):continue
  assert p.is_file() and p.stat().st_size==b['bytes'];s=physical(p);all_text_count+=1;compressed_count+=int(s['compressed']);logical_total+=b['bytes'];physical_total+=s['physical_bytes']
  if b['bytes']>=100_000 and not s['compressed']:candidates.append(dict(source_binding=b,storage=s))
 candidates.sort(key=lambda x:x['source_binding']['bytes'],reverse=True)
 selected=candidates[:40]
 for row in selected:
  b=row['source_binding'];assert sha(ROOT/b['path'])==b['sha256'];guard(started)
 r=dict(complete=True,errors=[],known_frozen_files=6923,read_only_inventory=True,text_files=all_text_count,already_compressed_text_files=compressed_count,text_logical_bytes=logical_total,text_physical_API_bytes=physical_total,uncompressed_large_text_candidates=len(candidates),candidate_logical_bytes=sum(v['source_binding']['bytes'] for v in candidates),selected_max40_files=len(selected),selected_logical_bytes=sum(v['source_binding']['bytes'] for v in selected),selected_frozen_SHA_verified=True,selected=selected,all_candidates=candidates,compression_executed=False,old_source_bytes_or_paths_modified=False,MRI_or_model_files_selected=False,live_files_selected=False,other_PIDs_enumerated=False,resources_before=before,resources_after=guard(started),elapsed_seconds=time.perf_counter()-started,source_bindings=[entry(p) for p in [Path(__file__),HERE/'PROTOCOL.md',index,proof]],publication_claim_confirmed=False,goal_status='active')
 out=HERE/'inventory_attempt01';out.mkdir(exist_ok=False);dump(out/'receipt.json',r)
 print(json.dumps({k:v for k,v in r.items() if k not in ['selected','all_candidates','source_bindings']},ensure_ascii=False),flush=True)
 for row in selected:print(json.dumps(row,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
