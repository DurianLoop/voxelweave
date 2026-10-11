"""Independent denominator/identity/maxima audit, not a second forward or pixel recomputation."""
import sys,json,gzip,itertools,time,traceback
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,entry,bind,dump,resource_guard
def main():
 started=time.perf_counter();out=HERE/'layerwise_terminal_audit_attempt01';out.mkdir(exist_ok=False)
 r=dict(complete=False,errors=[],independent_arrays_recomputed=False,new_forward_evaluations=0,
  GT_arrays_loaded=0,MRI_arrays_loaded=0,model_arrays_loaded=0,full38_FOV_qualified=False,
  original_probability_gate_passed=False,publication_claim_confirmed=False,goal_status='active')
 try:
  resource_guard();tp=HERE/'ACTUAL_ALL_TILES_LAYERWISE_TERMINAL_TOOL.json';terminal=read(tp)
  assert terminal['exit_code']==0 and 'session_id' not in terminal and terminal['observed_unified_exec_session']==58242
  rp=HERE/'layerwise_all_tiles_attempt01/receipt.json';v=read(rp);assert v['complete'] and v['status']=='completed' and not v['errors']
  fp=HERE/'layerwise_all_tiles_attempt01/frozen_config.json';config=read(fp)
  for b in v['source_bindings']:bind(b)
  jp=bind(v['journal']);assert jp.name=='batches.jsonl.gz'
  assert v['frozen_config_sha256']==entry(fp)['sha256']
  locations=list(itertools.product(*config['axis_starts']));assert len(locations)==len(set(locations))==192
  batches=[locations[i:i+2] for i in range(0,192,2)];maxima={};seen=[];field_count=0
  expected=set()
  for prefix in ['encoders.'+str(i) for i in range(4)]+['decoders.'+str(i) for i in range(3)]:
   expected.update(prefix+'.layers.'+str(i) for i in range(6))
  expected.update('ups.'+str(i) for i in range(3));expected.update('heads.'+str(i) for i in range(3));expected.add('probability')
  assert len(expected)==49
  with gzip.open(jp,'rt',encoding='utf-8') as f:
   for n,line in enumerate(f):
    q=json.loads(line);assert q['batch']==n and n<96
    starts=[tuple(x) for x in q['tile_starts']];assert starts==batches[n];seen.extend(starts)
    assert q['CPU_all49_fields_repeat_bitwise_equal'] and q['GPU_all49_fields_repeat_bitwise_equal']
    checks=q['layer_checks'];assert len(checks)==49 and {c['name'] for c in checks}==expected
    for c in checks:
     assert c['elements']==int(__import__('math').prod(c['shape'])) and c['shape'][0]==2
     assert len(c['maximum_error_index'])==len(c['shape'])
     assert all(0<=a<b for a,b in zip(c['maximum_error_index'],c['shape']))
     assert c['max_absolute_error']>=c['mean_absolute_error']>=0
     if c['name'] not in maxima or c['max_absolute_error']>maxima[c['name']]['max_absolute_error']:
      maxima[c['name']]=dict(c,batch=n,tile_starts=q['tile_starts'])
     field_count+=1
    assert len(q['CPU_batch_probability_sha256'])==len(q['GPU_batch_probability_sha256'])==64
  assert seen==locations and len(set(seen))==192 and field_count==96*49
  assert maxima==v['layer_maxima']
  assert v['batches_completed']==96 and v['unique_tiles']==192 and v['actual_GPU_tile_forwards']==v['actual_CPU_tile_forwards']==384
  old=read(HERE/'full_fov_attempt01/receipt.json')['series'][-1]
  assert v['CPU_GPU_original_fullFOV_hashes_reproduced'] and v['all49_layer_fields_same_device_repeat_bitwise_equal']
  assert v['original_failed_probability_error']==old['max_probability_error']>3e-6
  assert v['binary_disagreements']==old['binary_disagreements']==0
  assert v['coordinate_error']<=3e-12 and v['coordinate_binary_disagreements']==0
  assert v['GT_arrays_loaded']==v['training_updates']==0 and not v['medical_effect_scored']
  size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file());res=resource_guard()
  assert size<20_000_000 and res['workspace_free_bytes']-22_800_000-(20_000_000-size)>=8_000_000_000
  r.update(complete=True,all96_batches192_unique_tiles4704_layer_fields_verified=True,
   recorded_same_device49_field_repeat_bitwise_equal=True,recorded_original_FOV_hash_assertions_executed=True,
   first_convolution_max_error=maxima['encoders.0.layers.0']['max_absolute_error'],
   first_InstanceNorm_max_error=maxima['encoders.0.layers.1']['max_absolute_error'],
   largest_tile_probability_error=maxima['probability']['max_absolute_error'],
   fullFOV_probability_error=v['original_failed_probability_error'],
   top5_layer_absolute_maxima=sorted(maxima.values(),key=lambda a:a['max_absolute_error'],reverse=True)[:5],
   source_bindings=[entry(p) for p in [Path(__file__),tp,rp,fp,jp,HERE/'diagnose_all_tiles_layerwise.py',HERE/'full_fov_attempt01/receipt.json']],resources=res)
 except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
 r['elapsed_seconds']=time.perf_counter()-started;dump(out/'receipt.json',r);print(json.dumps(r),flush=True);return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
