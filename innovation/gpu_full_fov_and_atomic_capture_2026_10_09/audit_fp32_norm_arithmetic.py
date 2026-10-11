"""Audit all prospective full-FOV candidate identities/repeats/gates; no second pixel recomputation."""
import sys,json,time,traceback
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,entry,bind,dump,resource_guard
def main():
 started=time.perf_counter();out=HERE/'fp32_norm_arithmetic_audit_attempt01';out.mkdir(exist_ok=False)
 r=dict(complete=False,errors=[],MRI_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,
  second_independent_pixel_recomputation=False,full38_FOV_qualified=False,publication_claim_confirmed=False,goal_status='active')
 try:
  resource_guard();tp=HERE/'ACTUAL_FP32_NORM_ARITHMETIC_TERMINAL_TOOL.json';terminal=read(tp)
  assert terminal['exit_code']==0 and 'session_id' not in terminal and terminal['observed_unified_exec_session']==28213
  rp=HERE/'fp32_norm_arithmetic_attempt01/receipt.json';v=read(rp);assert v['complete'] and v['status']=='completed' and not v['errors']
  for b in v['source_bindings']:bind(b)
  oldp=HERE/'full_fov_attempt01/receipt.json';old=read(oldp)['series'][-1]
  assert v['CPU_reference_sha256']==old['CPU_probability_sha256']
  q=v['comparisons'];assert len(q)==3 and [x['mode'] for x in q]==['native','fp32_centered','fp32_affine_addcmul']
  for x in q:
   assert x['complete_FOV'] and x['total_tiles']==192 and x['repeats']==(1 if x['mode']=='native' else 2)
   assert len(x['full_pipeline_seconds'])==x['repeats'] and min(x['full_pipeline_seconds'])>0
   assert x['GPU_peak_reserved_bytes']<=2_500_000_000
   assert x['strict_probability_binary_gate_passed']==(x['max_probability_error']<=3e-6 and x['binary_disagreements']==0)
   if x['mode']=='native':
    assert x['probability_sha256']==old['GPU_probability_sha256'] and x['max_probability_error']==old['max_probability_error']
   else:assert x['complete_FOV_repeat_bitwise_equal'] and x['probability_sha256']==x['repeat_probability_sha256']
  expected=[x['mode'] for x in q if x['mode']!='native' and x['strict_probability_binary_gate_passed']]
  assert expected==v['qualifying_single_case_candidates'] and v['coordinate_gate_passed'] and v['coordinate_error']<=3e-12
  assert v['MRI_arrays_loaded']==v['parent_model_arrays_loaded']==1 and v['GT_arrays_loaded']==v['training_updates']==0
  assert not v['medical_effect_scored'] and not v['full38_FOV_qualified'] and not v['confirmation_patients_opened'] and not v['lockedIXI_opened']
  r.update(complete=True,all3_complete192tile_comparisons_verified=True,all4_candidate_complete_FOV_repeats_verified=True,
   recorded_CPU_native_GPU_original_hashes_reproduced=True,actual_GPU_FOV_runs=5,actual_GPU_tile_forwards=960,
   qualifying_single_case_candidates=expected,comparisons=q,resources=resource_guard(),
   source_bindings=[entry(p) for p in [Path(__file__),tp,rp,oldp,HERE/'diagnose_fp32_norm_arithmetic.py',HERE/'fp32_norm_arithmetic_v1.py',HERE/'FP32_NORM_ARITHMETIC_DIAGNOSIS_PROTOCOL.md']])
 except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
 r['elapsed_seconds']=time.perf_counter()-started;dump(out/'receipt.json',r);print(json.dumps(r),flush=True);return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
