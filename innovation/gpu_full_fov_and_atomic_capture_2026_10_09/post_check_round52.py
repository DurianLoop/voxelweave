"""Independent append hash verification and completion/partial scope checks."""
import sys,json,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'adaptive_acquisition_primary_followup_2026_10_09'));from resource_guard_v1 import guard,read,entry,bind,dump
start=time.perf_counter();before=guard(start);p=read(HERE/'APPEND_ROUND52_PROOF.json');assert p['complete'] and not p['errors'];ip=bind(p['append_index']);v=read(ip);assert v['complete'] and not v['errors']
assert v['previous7857_hashes_verified'] and v['cumulative_frozen_evidence_files']==7857+v['newly_bound_files']==p['cumulative_frozen_evidence_files']
assert len(v['new_evidence_files'])==len({b['path'] for b in v['new_evidence_files']})==v['newly_bound_files']
for b in v['prior_chain']:bind(b)
live=HERE/'compact19_real_qualification_attempt01';foundreal=[]
for b in v['new_evidence_files']:
 target=bind(b);assert not target.is_relative_to(live)
 if target.is_relative_to(ROOT/'full_certified_schedule_2026_10_09/full_real_pipeline_attempt01'):foundreal.append(b)
assert foundreal and v['now_terminal_full35904_outputs_included'] and v['old_full35904_actual_terminal_and_independent_audit_completed']
assert v['live_compact19_outputs_excluded'] and v['live_compact19_session']==44838 and v['original_fullpatch_two_synthetic_GPU_CPU_steps_passed']
assert v['synthetic_CPU_optimizer_updates_completed_and_recorded']==15 and v['synthetic_GPU_optimizer_updates_completed_and_recorded']==12
for key in ('whole_author_pipeline_noninterference_proven','author_code_executed','original_FP32_production_qualified','complete19series_new_numeric_branch_qualified','full38_GPU_qualification_passed','formal_medical_training_launched','six_arm_training_ready','publication_claim_confirmed','confirmation_patients_opened','lockedIXI_opened','other_PIDs_enumerated','other_PIDs_modified','original_training_modified'):assert not v[key],key
assert v['unchanged_six_arm_total_budget_bytes']==104156359 and v['unchanged_prep_FOV_accepted_adaptive_other_caps_bytes']==[7000000,20000000,6000000,2000000,22800000]
out=HERE/'post_archive_check_round52_attempt01';out.mkdir(exist_ok=False)
r=dict(complete=True,errors=[],append_index=entry(ip),archive_proof=entry(HERE/'APPEND_ROUND52_PROOF.json'),all_new_frozen_files_rehashed=True,prior_chain_manifest_hashes_verified=True,prior7857_file_check_attested_by_archive=True,newly_bound_files=v['newly_bound_files'],cumulative_frozen_evidence_files=v['cumulative_frozen_evidence_files'],completed_full35904_sources_included_and_live_compact19_excluded=True,synthetic_success_and_medical_scope_preserved=True,all_original_gates_and_budget_flags_preserved=True,publication_claim_confirmed=False,goal_status='active',resources_before=before,resources_after=guard(start),elapsed_seconds=time.perf_counter()-start)
dump(out/'receipt.json',r);print(json.dumps(r),flush=True)
