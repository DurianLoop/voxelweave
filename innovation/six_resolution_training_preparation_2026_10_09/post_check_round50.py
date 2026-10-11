"""Independent completed index/proof and new file verification; no live/MRI/model arrays."""
import sys,time,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'adaptive_acquisition_primary_followup_2026_10_09'))
from resource_guard_v1 import guard,read,entry,bind,dump
started=time.perf_counter();before=guard(started)
proof=read(HERE/'APPEND_ROUND50_PROOF.json');assert proof['complete'] and not proof['errors']
ip=bind(proof['append_index']);v=read(ip);assert v['complete'] and not v['errors'] and v['previous7639_hashes_verified']
assert v['cumulative_frozen_evidence_files']==7639+v['newly_bound_files']==proof['cumulative_frozen_evidence_files']
assert len(v['new_evidence_files'])==len({b['path'] for b in v['new_evidence_files']})==v['newly_bound_files']
for b in v['prior_chain']:bind(b)
live=ROOT/'full_certified_schedule_2026_10_09/full_real_pipeline_attempt01'
for b in v['new_evidence_files']:assert not bind(b).is_relative_to(live)
for k in ('FP64_norm_full_synthetic_parameter_gate_passed','synthetic_verifier_step1_executed','GIN_complete19series_qualification_passed','full38_GPU_qualification_passed','full35904_qualification_passed','formal_medical_training_launched','six_arm_training_ready','publication_claim_confirmed','confirmation_patients_opened','lockedIXI_opened','other_PIDs_enumerated','other_PIDs_modified','original_training_modified'):assert not v[k],k
assert v['total_round50_synthetic_CPU_optimizer_updates']==4 and v['additional_round50_GPU_optimizer_updates']==v['additional_round50_medical_optimizer_updates']==0
assert v['new_distinct_primary_text_papers_read']==3 and v['figure_pixels_actually_inspected']==v['bibliography_items_read']==0
assert v['unchanged_six_arm_total_budget_bytes']==104156359 and v['unchanged_prep_FOV_accepted_adaptive_other_caps_bytes']==[7000000,20000000,6000000,2000000,22800000]
result=dict(complete=True,errors=[],append_index=entry(ip),archive_proof=entry(HERE/'APPEND_ROUND50_PROOF.json'),
 all_new_frozen_files_rehashed=True,prior_chain_manifest_hashes_verified=True,prior7639_file_check_attested_by_archive=True,
 newly_bound_files=v['newly_bound_files'],cumulative_frozen_evidence_files=v['cumulative_frozen_evidence_files'],
 live_full35904_excluded=True,actual_failure_and_medical_scope_flags_preserved=True,unchanged_gates_and_budget_flags_preserved=True,
 resources_before=before,resources_after=guard(started),elapsed_seconds=time.perf_counter()-started,
 publication_claim_confirmed=False,goal_status='active')
out=HERE/'post_archive_check_round50_attempt01';out.mkdir(exist_ok=False);dump(out/'receipt.json',result)
print(json.dumps(result),flush=True)
