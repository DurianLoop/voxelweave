"""Independently rehash newly archived files and check positive/negative evidence boundaries."""
import sys,time,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'adaptive_acquisition_primary_followup_2026_10_09'))
from resource_guard_v1 import guard,read,entry,bind,dump
start=time.perf_counter();before=guard(start);proof=read(HERE/'APPEND_ROUND51_PROOF.json');assert proof['complete'] and not proof['errors'];ip=bind(proof['append_index']);v=read(ip)
assert v['complete'] and not v['errors'] and v['previous7728_hashes_verified'] and v['cumulative_frozen_evidence_files']==7728+v['newly_bound_files']==proof['cumulative_frozen_evidence_files']
assert len(v['new_evidence_files'])==len({b['path'] for b in v['new_evidence_files']})==v['newly_bound_files']
for b in v['prior_chain']:bind(b)
live=ROOT/'full_certified_schedule_2026_10_09/full_real_pipeline_attempt01'
for b in v['new_evidence_files']:assert not bind(b).is_relative_to(live)
for key in ('stable_reduction_parameter_gate_passed','stable_reduction_step1_executed','high_precision_original_fullpatch_cost_passed','original_FP32_production_qualified','GIN_complete19series_qualification_passed','full38_GPU_qualification_passed','full35904_qualification_passed','formal_medical_training_launched','six_arm_training_ready','publication_claim_confirmed','confirmation_patients_opened','lockedIXI_opened','other_PIDs_enumerated','other_PIDs_modified','original_training_modified','total_round51_actual_optimizer_count_claimed_exact'):assert not v[key],key
assert v['separate_high_precision_two_synthetic_CPU_steps_passed'] and v['separate_high_precision_two_synthetic_GPU_CPU_steps_passed'] and v['strict_deterministic_disjoint_pool_six_CPU_checks_passed']
assert v['known_recorded_round51_CPU_optimizer_updates']==10 and v['known_recorded_round51_GPU_optimizer_updates']==2 and v['GPU_v1_exact_runtime_optimizer_count_not_recoverable']
assert v['fullpatch_OOM_forward_started']==1 and v['fullpatch_OOM_forward_completed']==v['fullpatch_OOM_optimizer_updates']==0
assert v['recovered_original_foundation_chunks']==2 and v['recovered_complete_original_paper_chunk_sets']==0 and v['omitted_Swin_algorithm_lines_actually_read']==22
assert v['unchanged_six_arm_total_budget_bytes']==104156359 and v['unchanged_prep_FOV_accepted_adaptive_other_caps_bytes']==[7000000,20000000,6000000,2000000,22800000]
out=HERE/'post_archive_check_round51_attempt01';out.mkdir(exist_ok=False)
r=dict(complete=True,errors=[],append_index=entry(ip),archive_proof=entry(HERE/'APPEND_ROUND51_PROOF.json'),all_new_frozen_files_rehashed=True,prior_chain_manifest_hashes_verified=True,prior7728_file_check_attested_by_archive=True,newly_bound_files=v['newly_bound_files'],cumulative_frozen_evidence_files=v['cumulative_frozen_evidence_files'],live_full35904_excluded=True,source_reading_recovery_scope_preserved=True,synthetic_GPU_pass_and_original_fullpatch_failure_scopes_preserved=True,unchanged_gates_and_budget_flags_preserved=True,publication_claim_confirmed=False,goal_status='active',resources_before=before,resources_after=guard(start),elapsed_seconds=time.perf_counter()-start)
dump(out/'receipt.json',r);print(json.dumps(r),flush=True)
