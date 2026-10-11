"""Forecast from all19 ended GPU cases; certify only after actual terminal/audit prerequisites."""
import argparse,collections,gzip,itertools,json,math,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,dump,resource_guard
COVER=ROOT/'development_optimizer_coverage_2026_10_09'
FOV=ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09'
FULL=ROOT/'full_certified_schedule_2026_10_09'
PRODUCTION=['sampling','resolution_candidate','intensity_and_hash','transfer_sync','forward_sync','loss_sync',
 'backward_sync','gradient_capture','AdamW_sync']
REQUIRED_BYTES=104_156_359

def ended(path,session):
 if not path.exists():return False
 v=read(path);return v.get('exit_code')==0 and 'session_id' not in v and v.get('observed_unified_exec_session')==session

def audited(path,keys):
 if not path.exists():return False
 r=read(path)
 if not r.get('complete') or r.get('errors') or not all(r.get(k) is True for k in keys):return False
 for b in r.get('source_bindings',[]):bind(b)
 return True

def coverage_forecast():
 terminal=COVER/'ACTUAL_COVERAGE_TERMINAL_TOOL.json';ap=COVER/'terminal_audit_attempt01/receipt.json'
 assert ended(terminal,78758)
 assert audited(ap,['all228_unique_updates_and456_patch_fields_verified','all19_series11_patients_and114_branch_denominators_verified'])
 rp=COVER/'coverage_attempt01/receipt.json';r=read(rp);cfg=read(rp.with_name('frozen_config.json'))
 assert r['complete'] and r['training_updates']==228 and len(r['branches'])==114
 oldp=ROOT/'real_context_and_author_code_followup_2026_10_08/full_schedule_attempt01/receipt.json'
 old=read(oldp);jp=ROOT/old['journal_path'];assert sha(jp)==old['journal_sha256']
 with gzip.open(jp,'rt',encoding='utf-8') as f:rows=[json.loads(line) for line in f]
 assert len(rows)==5984 and len({(v['step'],v['patch']) for v in rows})==5984
 exposure=collections.Counter(v['uid'] for v in rows if v['patch']==0)
 patients=collections.Counter(v['patient'] for v in rows if v['patch']==0)
 assert sum(exposure.values())==2992 and len(exposure)==19 and len(patients)==11 and set(patients.values())=={272}
 by_arm=collections.Counter();details=[];measured=collections.Counter();peak=0
 for b in r['branches']:
  assert b['complete'] and len(b['steps'])==2 and exposure[b['uid']]>0
  samples=[]
  for s in b['steps']:
   c=s['cost_seconds'];assert all(math.isfinite(x) and x>=0 for x in c.values())
   seconds=sum(c[k] for k in PRODUCTION)+s['journal_write_seconds']
   samples.append(seconds);measured.update(c);peak=max(peak,s['peak_reserved_bytes'])
  predicted=max(samples)*exposure[b['uid']];by_arm[b['kind']+'_'+b['mode']]+=predicted
  details.append(dict(patient=b['patient'],uid=b['uid'],kind=b['kind'],mode=b['mode'],
   sample_production_step_seconds=samples,scheduled_exposures=exposure[b['uid']],predicted_seconds=predicted))
 identities={(b['uid'],b['kind'],b['mode']) for b in r['branches']}
 assert identities==set(itertools.product(exposure,cfg['kinds'],cfg['modes'])) and len(identities)==114
 cache_seconds=sum(v['MRI_load_resample_seconds']+v['GT_load_resample_seconds'] for v in r['cache_records'])
 model_seconds=sum(max(b['model_load_transfer_seconds'] for b in r['branches'] if b['kind']==k and b['mode']==m)
  for k,m in itertools.product(cfg['kinds'],cfg['modes']))
 point=sum(by_arm.values())+cache_seconds+model_seconds
 forecast=dict(actual_measured_updates=228,actual_series=19,actual_patients=11,planned_updates=17952,
  scheduled_patient_exposure_per_arm=272,actual_unique_branch_step_pairs=228,series_exposure_per_arm=dict(exposure),
  production_components=PRODUCTION+['journal_write_seconds'],per_arm_point_estimate_seconds=dict(by_arm),
  MRI_GT_cache_load_resample_seconds=cache_seconds,six_model_load_transfer_estimate_seconds=model_seconds,
  training_point_estimate_before_atomic_capture_seconds=point,measured_qualification_component_seconds=dict(measured),
  GPU_peak_reserved_bytes=peak,per_branch_forecast=details,samples_per_branch=2,
  forecast_is_statistical_or_deterministic_runtime_upper_bound=False,
  qualification_independent_replays_included_in_production_cost=False)
 return forecast,[terminal,ap,rp,rp.with_name('frozen_config.json'),oldp,jp]

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--qualify',action='store_true');args=parser.parse_args()
 started=time.perf_counter();res=resource_guard();forecast,sources=coverage_forecast()
 flags=dict(full35904_actual_exit0=ended(FULL/'ACTUAL_FULL_REAL_PIPELINE_TERMINAL_TOOL.json',44317),
  full35904_independent_audit=audited(FULL/'full_real_terminal_audit_attempt01/receipt.json',
   ['all35904_unique_journal_fields_verified','all_strict_numeric_gates_verified_from_actual_journal']),
  full38_FOV_actual_exit0=ended(FOV/'ACTUAL_FULL_FOV_TERMINAL_TOOL.json',74453),
  full38_FOV_independent_audit=audited(FOV/'terminal_audit_attempt01/receipt.json',
   ['all38_fullFOV_identities_and_entire_voxel_gates_verified','all_two_atomic_weight_files_source_hashes_verified']))
 report=dict(complete=True,errors=[],forecast_only=not args.qualify,prerequisites=flags,
  forecast=forecast,required_above_disk_reserve_bytes=REQUIRED_BYTES,
  available_above_reserve_bytes=res['workspace_free_bytes']-8_000_000_000,
  disk_shortfall_bytes=max(0,REQUIRED_BYTES-(res['workspace_free_bytes']-8_000_000_000)),
  resource_contract_or_scientific_scope_reduced=False,training_ready=False,new_training_launched=False,
  MRI_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,medical_effect_scored=False,
  confirmation_patients_opened=False,lockedIXI_opened=False,publication_claim_confirmed=False,goal_status='active')
 if args.qualify:
  assert all(flags.values()),'True terminal/audit prerequisites are missing; no qualification generated'
  rp=FOV/'full_fov_attempt01/receipt.json';r=read(rp);audit=read(FOV/'terminal_audit_attempt01/receipt.json')
  assert len(r['series'])==38 and r['GT_arrays_loaded']==0 and len(r['atomic_captures'])==2
  assert all(v['numeric_gate_passed'] and v['max_probability_error']<=3e-6 and v['coordinate_max_error']<=3e-12
   and v['binary_disagreements']==v['coordinate_binary_disagreements']==0 for v in r['series'])
  for c in r['atomic_captures']:bind(c['file']);assert c['reload_bitwise_equal']
  atomic=max(c['atomic_operation_seconds'] for c in r['atomic_captures'])*6
  train_point=forecast['training_point_estimate_before_atomic_capture_seconds']+atomic
  train_wall=math.ceil(2*train_point+1800)
  # 114 development +54 already-seen validation FOVs; latter is cost planning only.
  inference_point=168*max(v['cost_seconds']['GPU_full_pipeline']+v['cost_seconds']['MRI_load_resample']+
   v['cost_seconds']['comparison_and_hash'] for v in r['series'])
  complete_wall=train_wall+math.ceil(2*inference_point+1800)
  report.update(forecast_only=False,
   all38_parent_full_fov_probabilities_independently_verified=True,all_probability_errors_le_3e_6=True,
   all_coordinate_errors_le_3e_12=True,all_binary_disagreements_zero=True,
   disk_atomic_capture_and_reload_verified=True,complete_pipeline_cost_components_measured=True,
   all19_development_series_represented_in_training_cost_measurements=True,
   memory_contract_passed=forecast['GPU_peak_reserved_bytes']<=2_500_000_000 and
    all(v['GPU_peak_reserved_bytes']<=2_500_000_000 for v in r['series']) and r['resources_after']['GPU_free_bytes']>=4_000_000_000,
   six_atomic_capture_estimate_seconds=atomic,training_point_estimate_seconds=train_point,
   admitted_training_wall_seconds=train_wall,planned_FOV_evaluations=168,
   full_family_production_inference_point_estimate_seconds=inference_point,
   complete_family_wall_forecast_seconds=complete_wall,wall_forecast_includes_engineering_allowances=True,
   complete_family_wall_actually_measured=False,actual_terminal_binding=entry(FOV/'ACTUAL_FULL_FOV_TERMINAL_TOOL.json'),
   independent_audit_binding=entry(FOV/'terminal_audit_attempt01/receipt.json'))
  sources += [rp,FOV/'terminal_audit_attempt01/receipt.json',FOV/'ACTUAL_FULL_FOV_TERMINAL_TOOL.json',
   FULL/'ACTUAL_FULL_REAL_PIPELINE_TERMINAL_TOOL.json',FULL/'full_real_terminal_audit_attempt01/receipt.json']
  report['source_bindings']=[entry(p) for p in sources+[Path(__file__),HERE/'V2_PROTOCOL.md']]
  dump(HERE/'FULL_GPU_DEPLOYMENT_QUALIFICATION_V2.json',report)
 else:
  report['source_bindings']=[entry(p) for p in sources+[Path(__file__),HERE/'V2_PROTOCOL.md']]
  out=HERE/'all19_cost_forecast_v2_attempt01';out.mkdir(exist_ok=False);dump(out/'receipt.json',report)
 print(json.dumps({k:v for k,v in report.items() if k not in {'forecast','source_bindings'}}))
 print(json.dumps({k:v for k,v in forecast.items() if k!='per_branch_forecast'}))
 return 0

if __name__=='__main__':raise SystemExit(main())
