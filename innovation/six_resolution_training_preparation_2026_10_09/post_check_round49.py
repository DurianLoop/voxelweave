"""Independently verify the index/proof and newly frozen files; no images/models opened."""
import sys,time,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,entry,bind,dump,resource_guard
started=time.perf_counter();proof=read(HERE/'APPEND_ROUND49_PROOF.json');assert proof['complete'] and not proof['errors']
p=bind(proof['append_index']);v=read(p);assert v['complete'] and not v['errors'] and v['previous7538_hashes_verified']
assert v['cumulative_frozen_evidence_files']==7538+v['newly_bound_files']==proof['cumulative_frozen_evidence_files']
assert len(v['new_evidence_files'])==v['newly_bound_files'] and len({b['path'] for b in v['new_evidence_files']})==v['newly_bound_files']
for b in v['prior_chain']:bind(b)
live=ROOT/'full_certified_schedule_2026_10_09/full_real_pipeline_attempt01'
for b in v['new_evidence_files']:assert not bind(b).is_relative_to(live)
assert not v['GIN_complete19series_qualification_passed'] and not v['full35904_qualification_passed'] and not v['six_arm_training_ready'] and not v['publication_claim_confirmed']
assert not v['finite_difference_fixed_gate_passed'] and v['largest_predeclared_h_failure_retained']
caps=((HERE,7_000_000),(ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09',20_000_000),(ROOT/'gin_accepted_primary_followup_2026_10_09',6_000_000));remaining=22_800_000
for d,cap in caps:
    size=sum(q.stat().st_size for q in d.rglob('*') if q.is_file());assert size<cap;remaining+=cap-size
r=resource_guard();assert r['workspace_free_bytes']-remaining>=8_000_000_000
result=dict(complete=True,errors=[],append_index=entry(p),archive_proof=entry(HERE/'APPEND_ROUND49_PROOF.json'),
 all_new_frozen_files_rehashed=True,prior_chain_manifest_hashes_verified=True,prior7538_file_check_attested_by_archive=True,
 newly_bound_files=v['newly_bound_files'],cumulative_frozen_evidence_files=v['cumulative_frozen_evidence_files'],
 live_full35904_excluded=True,largest_h_finite_difference_failure_preserved=True,pending_training_and_claim_flags_preserved=True,
 resources=r,remaining_all_stage_allowance_bytes=remaining,elapsed_seconds=time.perf_counter()-started)
out=HERE/'post_archive_check_round49_attempt01';out.mkdir(exist_ok=False);dump(out/'receipt.json',result)
print(json.dumps(result),flush=True)
