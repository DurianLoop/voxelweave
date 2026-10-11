"""Enumerate all ended batch identities and compare actual GPU hashes/cost paired records."""
import sys,json,gzip,itertools,collections,math,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,dump,resource_guard
started=time.perf_counter();resource_guard()
tp=HERE/'ACTUAL_SELECTIVE_RESAMPLING_TERMINAL_TOOL.json';t=read(tp)
assert t['exit_code']==0 and 'session_id' not in t and t['observed_unified_exec_session']==67821
rp=HERE/'selective_resampling_attempt01/receipt.json';r=read(rp);assert r['complete'] and not r['errors']
assert r['MRI_arrays_loaded']==38 and r['GT_arrays_loaded']==r['model_arrays_loaded']==r['training_updates']==0 and not r['CUDA_initialized']
for k in ['validation_pixels_loaded','confirmation_patients_opened','lockedIXI_opened','original_training_modified','full35904_qualified','publication_claim_confirmed']:assert not r[k]
for b in r['source_bindings']:bind(b)
cfg=read(HERE/'coverage_attempt01/frozen_config.json');cp=read(HERE/'coverage_attempt01/receipt.json')
with gzip.open(bind(cp['journal']),'rt',encoding='utf-8') as f:actual={(v['case'],v['kind'],v['mode'],v['optimizer_step']):v for v in map(json.loads,f)}
expected=set(itertools.product(range(19),cfg['kinds'],cfg['modes'],[1,2]));seen=set();byarm=collections.Counter()
oldj=ROOT/'real_context_and_author_code_followup_2026_10_08/full_schedule_attempt01/geometry.journal.jsonl.gz'
with gzip.open(oldj,'rt',encoding='utf-8') as f:exposure=collections.Counter(v['uid'] for v in map(json.loads,f) if v['patch']==0)
for v in r['batches']:
 key=(v['case'],v['kind'],v['mode'],v['optimizer_step']);assert key in expected and key not in seen;seen.add(key)
 assert v['scheduled_step']==actual[key]['scheduled_step'] and v['actual_GPU_input_sha256_reproduced']
 assert math.isfinite(v['production_candidate_seconds']) and v['production_candidate_seconds']>=0
assert seen==expected and len(r['batches'])==228 and r['all456_selected_patch_fields_completed']
for ci,kind,mode in itertools.product(range(19),cfg['kinds'],cfg['modes']):
 samples=[v['production_candidate_seconds'] for v in r['batches'] if (v['case'],v['kind'],v['mode'])==(ci,kind,mode)]
 assert len(samples)==2;byarm[kind+'_'+mode]+=max(samples)*exposure[cfg['cases'][ci]['uid']]
raw=r['raw_comparisons'];identities={(v['case'],v['kind'],v['mode'],v['patch']) for v in raw}
assert len(raw)==len(identities)==12 and identities==set(itertools.product([2],cfg['kinds'],cfg['modes'],[0,1]))
for v in raw:assert v['raw_bitwise_equal'] and v['support_bitwise_equal'] and v['original_full_grid_seconds']>=0 and v['selected_seconds']>=0
original=sum(v['original_full_grid_seconds'] for v in raw);new=sum(v['selected_seconds'] for v in raw)
result=dict(complete=True,errors=[],all228_unique_GPU_input_hash_comparison_identities_verified=True,
 all456_selected_patch_fields_receipts_verified=True,all12_raw_support_paired_comparisons_verified=True,
 actual_arrays_not_reexecuted_in_this_audit=True,paired_selected_failed_series_original_seconds=original,
 paired_selected_failed_series_new_seconds=new,paired_selected_failed_series_speed_ratio=original/new,
 full_six_arm_candidate_only_cost_point_estimate_seconds=dict(byarm),all35904_schedule_requalified=False,
 forecast_is_runtime_upper_bound=False,fullFOV_qualified=False,medical_effect_confirmed=False,
 publication_claim_confirmed=False,goal_status='active',source_bindings=[entry(p) for p in [Path(__file__),tp,rp,
 HERE/'coverage_attempt01/frozen_config.json',bind(cp['journal']),oldj]],resources=resource_guard(),elapsed_seconds=time.perf_counter()-started)
out=HERE/'selective_terminal_audit_attempt01';out.mkdir(exist_ok=False);dump(out/'receipt.json',result);print(json.dumps(result))
