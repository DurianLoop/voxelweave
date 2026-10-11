"""Replay actual228 network-input batches without GT/model loads; raw compare for the failed large case."""
import os
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='1'
import sys,gzip,json,time,traceback,collections,gc
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,dump,resource_guard
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_3d_19series_common_init_2026_10_07 import development_cases,lattice,source_image,physical_mr,array_sha,np,torch
sys.path.insert(0,str(ROOT/'intensity_precision_failure_diagnosis_2026_10_09'))
import intensity_float64_stats as intensity
import selective_certified_resolution as selected

def main():
 started=time.perf_counter();torch.set_num_threads(1);assert torch.get_num_interop_threads()==1
 out=HERE/'selective_resampling_attempt01';out.mkdir(exist_ok=False)
 r=dict(complete=False,errors=[],batches=[],raw_comparisons=[],MRI_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,
  training_updates=0,CUDA_initialized=False,validation_pixels_loaded=False,confirmation_patients_opened=False,
  lockedIXI_opened=False,original_training_modified=False,full35904_qualified=False,
  publication_claim_confirmed=False,goal_status='active')
 def save():
  tmp=out/'receipt.json.tmp';tmp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');tmp.replace(out/'receipt.json')
 def guard():
  v=resource_guard();size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
  assert size<2_000_000 and v['workspace_free_bytes']-40_800_000-(2_000_000-size)>=8_000_000_000
  assert time.perf_counter()-started<3600 and not torch.cuda.is_initialized()
  return v
 save()
 try:
  guard();audit=read(HERE/'terminal_audit_attempt01/receipt.json');assert audit['complete']
  for b in audit['source_bindings']:bind(b)
  coverage=read(HERE/'coverage_attempt01/receipt.json');cfg=read(HERE/'coverage_attempt01/frozen_config.json')
  with gzip.open(bind(coverage['journal']),'rt',encoding='utf-8') as f:actual={(v['case'],v['kind'],v['mode'],v['optimizer_step']):v for v in map(json.loads,f)}
  assert len(actual)==228
  oldp=ROOT/'real_context_and_author_code_followup_2026_10_08/full_schedule_attempt01/receipt.json';old=read(oldp);jp=ROOT/old['journal_path'];assert sha(jp)==old['journal_sha256']
  with gzip.open(jp,'rt',encoding='utf-8') as f:geometry={(v['step'],v['patch']):v for v in map(json.loads,f)}
  r['source_bindings']=[entry(p) for p in [Path(__file__),HERE/'SELECTIVE_RESAMPLING_PROTOCOL.md',Path(selected.__file__),Path(selected.full.__file__),
   Path(intensity.__file__),HERE/'terminal_audit_attempt01/receipt.json',HERE/'coverage_attempt01/receipt.json',HERE/'coverage_attempt01/frozen_config.json',bind(coverage['journal']),oldp,jp]]
  r['source_bindings'] += cfg['source_bindings'];seen=set()
  for ci,(c,row) in enumerate(development_cases()):
   for kind in cfg['kinds']:
    guard();image,_=source_image(c,row,kind);grid=lattice(c);cache=physical_mr(image,grid);del image;r['MRI_arrays_loaded']+=1
    assert array_sha(cache)==actual[(ci,kind,cfg['modes'][0],1)]['cache_sha256']
    for step,scheduled in enumerate(cfg['cases'][ci]['scheduled_steps'],1):
     for mode in cfg['modes']:
      tick=time.perf_counter();patches=[];metas=[]
      for p in range(2):
       v=geometry[(scheduled,p)];assert v['uid']==c['uid']
       z,s,m=selected.apply(cache,grid,v['geometry'],v['primitive'],mode);patches.append(z);metas.append(m)
       if ci==2 and step==1:
        at=time.perf_counter();reference,rs,rm=selected.full.apply(cache,grid,v['geometry'],v['primitive'],mode)
        full_seconds=time.perf_counter()-at
        assert np.array_equal(z,reference) and np.array_equal(s,rs) and m['exact_fallback_voxels']==rm['exact_fallback_voxels']
        r['raw_comparisons'].append(dict(case=ci,kind=kind,mode=mode,patch=p,raw_bitwise_equal=True,support_bitwise_equal=True,
         selected_seconds=m['elapsed_seconds'],original_full_grid_seconds=full_seconds,selected_source_voxels=m.get('selected_source_voxels'),
         full_source_voxels=m.get('full_source_voxels'),fallback_voxels=m['exact_fallback_voxels']))
      final=intensity.apply(np.stack(patches)[:,None],intensity.primitives(scheduled));key=(ci,kind,mode,step)
      assert array_sha(final)==actual[key]['input_sha256'];assert key not in seen;seen.add(key)
      r['batches'].append(dict(case=ci,kind=kind,mode=mode,optimizer_step=step,scheduled_step=scheduled,
       actual_GPU_input_sha256_reproduced=True,production_candidate_seconds=sum(m['elapsed_seconds'] for m in metas),
       elapsed_seconds_including_raw_reference=time.perf_counter()-tick))
      save();del patches,final;guard()
    del cache;gc.collect();print(json.dumps(dict(series_input_pairs_completed=r['MRI_arrays_loaded'],matched_batches=len(r['batches']))),flush=True)
  assert len(seen)==228 and len(r['raw_comparisons'])==12 and r['MRI_arrays_loaded']==38
  for b in r['source_bindings']:bind(b)
  r.update(complete=True,status='completed',all228_actual_GPU_network_input_hashes_reproduced=True,
   all456_selected_patch_fields_completed=True,all12_raw_full_grid_and_support_comparisons_bitwise_equal=True,resources_after=guard())
 except Exception as e:r.update(status='failed',traceback=traceback.format_exc());r['errors'].append(type(e).__name__+': '+str(e))
 r['elapsed_seconds']=time.perf_counter()-started;save();print(json.dumps({k:r[k] for k in ['complete','errors','MRI_arrays_loaded','elapsed_seconds']}),flush=True)
 return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
