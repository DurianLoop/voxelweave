"""Audit ended whole-FOV negative comparisons; never call an unsuccessful qualification passed."""
import sys,json,math,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,entry,bind,dump,resource_guard
started=time.perf_counter();resource_guard()
attempts=[('layout_diagnosis_attempt02','ACTUAL_LAYOUT_V2_TERMINAL_TOOL.json',25418),
 ('cpu_norm_diagnosis_attempt01','ACTUAL_CPU_NORM_TERMINAL_TOOL.json',15492)]
sources=[Path(__file__),HERE/'NUMERICAL_FINDINGS_AND_NEXT.md'];rows=[]
for directory,name,session in attempts:
 tp=HERE/name;t=read(tp);assert t['exit_code']==0 and 'session_id' not in t and t['observed_unified_exec_session']==session
 rp=HERE/directory/'receipt.json';r=read(rp);assert r['complete'] and not r['errors'] and len(r['comparisons'])==2
 assert r['MRI_arrays_loaded']==r['model_arrays_loaded']==1 and r['GT_arrays_loaded']==r['training_updates']==0
 for k in ['medical_effect_scored','validation_pixels_loaded','confirmation_patients_opened','lockedIXI_opened',
  'other_PIDs_enumerated','other_PIDs_modified','original_training_modified','full38_FOV_qualified','publication_claim_confirmed']:assert not r[k]
 for b in r['source_bindings']:bind(b)
 assert r['reference_original_hash_reproduced'] and r['coordinate_gate_passed']
 for c in r['comparisons']:
  assert c['total_tiles']==192 and c['complete_native_shape']==[512,512,144] and c['binary_disagreements']==0
  assert math.isfinite(c['max_probability_error']) and c['max_probability_error']>3e-6 and not c['strict_probability_binary_passed']
  assert 0<c['peak_reserved_bytes']<=2_500_000_000 and c['GPU_full_pipeline_seconds']>0
 rows.append(dict(attempt=directory,comparisons=r['comparisons'],CPU_reference_seconds=r['CPU_reference_seconds']))
 sources += [tp,rp]
assert rows[0]['comparisons'][0]['probability_sha256']==rows[0]['comparisons'][1]['probability_sha256']
assert rows[1]['comparisons'][1]['max_probability_error']>rows[1]['comparisons'][0]['max_probability_error']
result=dict(complete=True,errors=[],all_two_diagnostics_actual_terminal_and_failure_identities_verified=True,
 both_attempted_interventions_failed_original_probability_gate=True,original_binary_agreement_preserved=True,
 full38_qualification_passed=False,array_level_replay_in_this_audit=False,diagnostics=rows,
 source_bindings=[entry(p) for p in sources],resources=resource_guard(),publication_claim_confirmed=False,goal_status='active',elapsed_seconds=time.perf_counter()-started)
out=HERE/'negative_terminal_audit_attempt01';out.mkdir(exist_ok=False);dump(out/'receipt.json',result);print(json.dumps(result))
