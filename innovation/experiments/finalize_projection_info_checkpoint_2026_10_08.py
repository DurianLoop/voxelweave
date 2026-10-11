"""Record actual archive exit and latest confirmed-live handle, without future exits."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def read(p):return json.loads(p.read_text(encoding='utf-8'))


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))


def new(p,d):
    with p.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    manifest=ROOT/'literature/projection_info_stage_manifest_2026-10-08.json'
    proof=ROOT/'SESSION_ARCHIVE_VERIFICATION_PROJECTION_INFO_2026-10-08.json'
    m,p=read(manifest),read(proof)
    assert m['complete'] and p['complete'] and not m['errors'] and not p['errors'] and sha(manifest)==p['manifest_sha256']
    assert len(m['stage_files'])==109 and len(m['evidence_files'])==3319 and m['stage_bytes']==12441574
    assert p['newly_bound_files']==118 and p['new_evidence_bytes']==13261512
    assert p['previous3201_evidence_hashes_unchanged'] and p['all_final_evidence_hashes_verified'] and p['local_links_verified']
    observed=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        archive=dict(actual_observed_tool_chunk='4bb920',actual_observed_tool_exit=0,stage_files=109,cumulative_frozen_files=3319,
            stage_bytes=12441574,newly_bound_files=118,new_evidence_bytes=13261512),
        metadata_record=dict(actual_observed_tool_chunk='854d3b',actual_observed_tool_exit=0),
        training=dict(actual_observed_tool_chunk='f37d2f',session_id=99542,returned_same_live_session=True,
            native_updates=14652,invocation02_new_updates=14553,cumulative_wall_seconds=33042.42491349997,
            full_training_observed_tool_exit=None,training_restarted=False,training_migrated=False),
        latest_GPU=dict(actual_observed_tool_chunk='83979d',actual_observed_tool_exit=0,timestamp='2026/10/08 00:59:50.188',
            free_MiB=1394,total_MiB=24455,utilization_percent=94,new_GPU8GB_margin_met=False),
        automatic_approval_review_rejections_received=0,goal_status='active',publication_claim_confirmed=False)
    obsfile=ROOT/'SESSION_FINAL_TOOL_OBSERVATIONS_PROJECTION_INFO_2026-10-08.json';new(obsfile,observed)
    receipt=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[entry(x) for x in (Path(__file__),manifest,proof,obsfile,
            ROOT/'SESSION_POST_ARCHIVE_PROJECTION_INFO_UPDATE_2026-10-08.md',ROOT/'SESSION_PREPARED_FINAL_REPLY_PROJECTION_INFO_2026-10-08.md')],
        archive_actual_tool_exit=0,archive_actual_tool_chunk='4bb920',new_stage_files_frozen=109,
        cumulative_frozen_evidence_files=3319,stage_bytes=12441574,new_evidence_bytes=13261512,
        previous3201_evidence_hashes_unchanged=True,production_actual_tool_exit=0,independent_actual_tool_exit=0,
        unique_development_patients=11,unique_development_series=19,checked_axis_maps=22,
        new_medical_arrays_loaded=0,new_model_arrays_loaded=0,new_neural_forwards=0,new_GPU_forwards=0,new_training_updates=0,
        new_primary_papers_read=2,text_pages_read=41,visual_pages_reviewed=6,
        exact_real_linear_rank_independently_certified=True,synthetic_same_statistics_direct_input_witness_verified=True,
        PCHIP_total_information_superiority_claimed=False,float32_inverse_or_condition_number_certified=False,
        live_training=observed['training'],latest_GPU=observed['latest_GPU'],formal_final_budget_completed=False,
        original56FOV_evaluated=False,all6_final_capability_gates_completed=False,
        current_final_model_cache_equivalence_qualified=False,actual_MRI_risk_certificates_issued=0,
        actual_MRI_task_benefit_measured=False,clinical_benefit_measured=False,real_latency_measured=False,
        confirmation_patients_opened=False,validation_data_read=False,locked_IXI_opened=False,
        old_MIRA_MSValid84_confirmation_preserved=True,publication_claim_confirmed=False,goal_status='active',
        current_goal_turn_classification='progress',this_receipt_is_post_manifest_appendix=True)
    dest=ROOT/'SESSION_CHECKPOINT_RECEIPT_PROJECTION_INFO_2026-10-08.json';new(dest,receipt)
    print(json.dumps(dict(complete=True,receipt=entry(dest),archive_actual_tool_exit=0,stage_files=109,
        cumulative_frozen_files=3319,native_updates=14652,full_training_exit=None,goal_status='active',publication_claim_confirmed=False)),flush=True)
    return 0


if __name__=='__main__':raise SystemExit(main())
