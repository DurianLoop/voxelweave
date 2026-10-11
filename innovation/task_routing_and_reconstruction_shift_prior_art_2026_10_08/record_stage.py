"""Execution and resource scope after actual primary reading; no medical IO."""
import sys,json,time,hashlib
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'task_adaptation_compute_prior_art_2026_10_08'))
import query_primary as base
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');at=time.perf_counter();resources=resource_guard()
    reading=json.loads((HERE/'READING_PROVENANCE.json').read_text(encoding='utf-8'));audit=json.loads((HERE/'table_audit_attempt01/receipt.json').read_text(encoding='utf-8'))
    obs=json.loads((HERE/'ACTUAL_OBSERVATIONS.json').read_text(encoding='utf-8'))
    for q in (reading,audit):
        assert q['complete'] and not q['errors']
        for b in q['source_bindings']:assert sha(ROOT/b['path'])==b['sha256']
    assert reading['new_full_text_pages_read']==34 and reading['visual_pages_reviewed']==15
    assert obs['actual_live_poll']['value']['session_id']==99542 and 'exit_code' not in obs['actual_live_poll']['value']
    assert obs['actual_goal']['value']['goal']['status']=='active'
    root=[]
    for name,expected in (('.gitignore','7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524'),
                           ('environment.yml','dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257')):
        p=ROOT.parent/name;assert sha(p)==expected;root.append(dict(path=str(p),sha256=expected,previous_sha256=expected))
    sources=[Path(__file__)]+[HERE/name for name in ('READING_PROVENANCE.json','table_audit_attempt01/receipt.json','USER_GOAL_REQUEST.md',
       'VISIBLE_DIALOGUE.md','NEXT_STAGE_HANDOFF.md','ACTUAL_OBSERVATIONS.json','PRIMARY_READING.md','RESULT.md','TASK_DISTRIBUTION_AND_FOV_CONTROL_PREPARATION.md')]
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],source_bindings=[base.entry(p) for p in sources],
      actual_exits=[dict(chunk=c,exit_code=x,job=job) for c,x,job in [('47bafb',1,'bounded_download_schannel_failure'),('927c4f',1,'new_download_attempt_medical_success_TADT_size_failure'),
        ('587000',1,'TADT_complete_download_and_pypdf_encoding_failure'),('ce125f',1,'strict_UTF16_local_extract_failure'),
        ('bf92f7',0,'local_PDFium_extract'),('573451',0,'render15_source_pages'),('358e08',0,'CPU_reported_table_audit'),('5d653e',0,'bind_actual_reading')]],
      known_executed_failures_preserved=True,automatic_approval_review_rejections_received=0,public_GET_only=True,TLS_verification_disabled=False,
      new_primary_papers_read=2,new_full_text_pages_read=34,main_text_pages_read=20,selected_appendix_text_pages_read=7,
      ancillary_reference_and_visual_caption_text_pages_read=7,visual_pages_reviewed=15,network_index_requests=0,new_abstracts_screened=0,
      compute_summary_comparisons=3,PSNR_LIIF_summary_comparisons=8,fixed_intensity_summary_comparisons=5,penalty_summary_tradeoffs=3,
      medical_median_summary_differences=3,medical_patient_count_tables_checked=2,reported_summaries_not_independent_patients=True,
      medical_arrays_loaded=0,model_checkpoint_arrays_loaded_from_disk=0,neural_forwards=0,MRI_neural_forwards=0,GPU_forwards=0,
      real_medical_resource_updates=0,real_medical_formal_training_updates=0,head_fits=0,new_final_action_labels_generated=0,
      full_action_cost_measured=False,actual_new_MRI_task_benefit_measured=False,original56FOV_evaluation_launched=False,
      formal_three_arm_long_MRI_training_implemented_and_qualified=False,confirmation_patients_opened=False,lockedIXI_opened=False,
      original_terminal_training_modified=False,new_agents_delegated=0,root_files_observed=root,publication_claim_confirmed=False,goal_status='active',
      previous_goal_turn_classification='progress',current_goal_turn_classification='progress',
      current_progress='Read TADT/medical-shift primary sources, audited backbone/routing cost denominators and literal patient totals, prepared matched task adaptation/exposure/full-FOV controls.',
      completion_audit=dict(original_two_arm_final_complete=False,original56FOV_six_gates_strict_complete=False,
          strong_matched_three_arm_sufficient_adaptation_complete=False,real_action_lesion_benefit_confirmed=False,full_cost_confirmed=False,
          strongest_static_and_matched_extra_training_effect_confirmed=False,eight_unseen_confirmation_complete=False,publishable_claim_achieved=False),
      resources_before=resources,resources_after=resource_guard(),elapsed_seconds=time.perf_counter()-at)
    base.new(HERE/'EXECUTION_LEDGER.json',r)
    print(json.dumps(dict(complete=True,new_papers_read=2,full_text_pages=34,visual_pages=15,MRI_updates=0,goal_status='active')),flush=True);return 0
if __name__=='__main__':raise SystemExit(main())
