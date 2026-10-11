"""Record exact primary-reading scope and tool observations without medical IO."""
import json,sys,time,hashlib,subprocess,shutil
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;PROJECT=ROOT.parent
sys.path.insert(0,str(ROOT/'task_adaptation_compute_prior_art_2026_10_08'))
import query_primary as base

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
    sys.stdout.reconfigure(encoding='utf-8');base.own_priority();tick=time.perf_counter()
    idx=read(HERE/'index_attempt01/receipt.json');prim=read(HERE/'primary_attempt01/receipt.json')
    visual=read(HERE/'visual_attempt01/receipt.json');detail=read(HERE/'visual_detail_attempt01/receipt.json')
    audit=read(HERE/'table_audit_attempt01/receipt.json')
    for d in (idx,prim,visual,detail,audit):assert d['complete'] and not d.get('errors',[])
    assert len(idx['records'])==3 and all(len(r['entries'])==8 for r in idx['records'])
    identifiers=[e['id'].rsplit('/',1)[-1] for r in idx['records'] for e in r['entries']]
    assert len(identifiers)==len(set(identifiers))==24
    reports=[];all_bindings=[]
    selections=[('l2sr','2212.02190v3',list(range(1,22))+[27,28,29],[7,9,14,16,18,29],[22,23,24,25,26,30,31]),
        ('diagnostic','2406.16754v1',list(range(1,9))+[11],[4,5,6,7,11],[9,10])]
    for key,ident,pages,seen,unread in selections:
        rows=[r for r in prim['records'] if r['key']==key];assert len(rows)==1
        r=rows[0];assert r['indexed_record']['id'].endswith('/'+ident)
        text_by_page={v['physical_page']:v for v in r['page_texts']}
        for n in pages:
            b=text_by_page[n];p=ROOT/b['path'];assert base.entry(p)['sha256']==b['sha256']
            assert p.stat().st_size>0
        images=[v for v in visual['records'] if v['paper']==key]
        assert sorted(v['physical_page'] for v in images)==sorted(seen)
        for v in images:
            b=v['image'];assert base.entry(ROOT/b['path'])['sha256']==b['sha256']
        reports.append(dict(key=key,arxiv_id=ident,title=r['indexed_record']['title'],authors=r['indexed_record']['authors'],
            original_PDF=r['file'],physical_pages=r['physical_pages'],full_text_pages_read=pages,
            full_text_page_count=len(pages),visual_pages_reviewed=seen,visual_page_count=len(seen),
            pages_not_read_in_full=unread,full_text_page_bindings=[text_by_page[n] for n in pages],
            visual_page_bindings=images,code_repository_or_published_implementation_read=False,
            experimental_results_independently_reproduced=False,theorem_proofs_fully_reviewed=False,
            reading_attestation='Assistant read complete page text outputs and explicitly viewed listed source renderings.'))
    total=sum(r['full_text_page_count'] for r in reports);assert total==33
    visualcount=sum(r['visual_page_count'] for r in reports);assert visualcount==11
    provenance=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],records=reports,
        source_bindings=[base.entry(HERE/p) for p in ('PRIMARY_READING.md','INDEX_SCREEN.md','INDEX_ORDER_CLARIFICATION.md',
            'primary_attempt01/receipt.json','visual_attempt01/receipt.json','visual_detail_attempt01/receipt.json')],
        additional_review_of_same_physical_page=[dict(paper='diagnostic',physical_page=11,
            enlarged_table_image=detail['output_bindings'][0],numerical_transcription_visually_checked=True,
            does_not_increment_visual_page_count=True)],
        provider_default_order=True,abstracts_fully_screened=24,new_primary_papers_read=2,
        new_full_text_pages_read=total,visual_pages_reviewed=visualcount,
        extraction_and_render_receipt_false_flags_are_generation_snapshots=True,
        existing_receipts_not_rewritten_after_reading=True,full_systematic_novelty_search_completed=False,
        raw_patient_predictions_not_obtained=True,medical_or_model_arrays_loaded=0,neural_forwards=0,GPU_forwards=0)
    base.new(HERE/'READING_PROVENANCE.json',provenance)
    expected={('AUC','Policy Reconstruction'):(1,17,0),('AUC','Undersampled'):(9,7,2),
        ('RECALL','Policy Reconstruction'):(1,17,0),('RECALL','Undersampled'):(8,6,4),
        ('SPECIFICITY','Policy Reconstruction'):(17,1,0),('SPECIFICITY','Undersampled'):(11,5,2)}
    for c in audit['comparisons']:
        assert (c['positive'],c['negative'],c['ties'])==expected[(c['metric'],c['control'])]
        assert len(c['conditions'])==18 and c['independent_patient_count'] is None
    assert audit['reported_slice_sum_agrees'] and audit['split_slice_sum']==39125
    sources=[HERE/p for p in ('index_attempt01/receipt.json','primary_attempt01/receipt.json','visual_attempt01/receipt.json',
        'visual_detail_attempt01/receipt.json','table_audit_attempt01/receipt.json','READING_PROVENANCE.json')]
    for source in sources:
        data=read(source)
        for b in data.get('source_bindings',[])+data.get('output_bindings',[]):
            p=ROOT/b['path'];actual=base.entry(p);assert actual['sha256']==b['sha256']
            if 'bytes' in b:assert actual['bytes']==b['bytes']
            all_bindings.append(dict(document=source.relative_to(ROOT).as_posix(),**b))
    roots=[]
    for name,expected_sha in [('.gitignore','7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524'),
        ('environment.yml','dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257')]:
        p=PROJECT/name;actual=hashlib.sha256(p.read_bytes()).hexdigest();assert actual==expected_sha
        roots.append(dict(path=str(p),sha256=actual,previous_sha256=expected_sha))
    gpu=subprocess.run(['nvidia-smi','--query-gpu=timestamp,name,memory.total,memory.free,utilization.gpu','--format=csv,noheader'],
        capture_output=True,text=True,timeout=15);assert gpu.returncode==0
    csv=gpu.stdout.strip();lines=csv.splitlines();assert len(lines)==1
    freeMiB=int(lines[0].split(',')[3].strip().split()[0]);freebytes=freeMiB*1048576
    livepath=ROOT/'experiments/mc_rc_3d_19series_common_init_cpu_2026_10_07/invocation02.json'
    livebytes=livepath.read_bytes();live=json.loads(livebytes)
    obs=dict(observed_utc=datetime.now(timezone.utc).isoformat(),training_session_id=99542,
        original_training_terminal_exit=None,training_status=live.get('status'),training_complete=live.get('complete'),
        training_errors=live.get('errors'),arms=[{k:a.get(k) for k in ('kind','updates_completed','complete')} for a in live.get('arms',[])],
        invocation02_new_updates=live.get('new_cpu_backbone_updates'),new_updates_not_raw_arm_count=True,
        live_metadata_sha256_observation_not_frozen=hashlib.sha256(livebytes).hexdigest(),
        mutable_training_file_not_added_to_archive=True,gpu_csv=csv,gpu_query_exit=0,gpu_free_bytes=freebytes,
        gpu_authorization_retained=True,new_GPU_job_started=False,new_GPU_startup_reserve_bytes=8_000_000_000,
        GPU_reserve_met_at_this_observation=freebytes>=8_000_000_000,
        workspace_free_bytes=shutil.disk_usage(ROOT).free,disk_reserve_bytes=8_000_000_000,
        root_files_observed=roots,original_terminal_training_modified=False,other_processes_enumerated=False,
        other_processes_modified=False)
    base.new(HERE/'TRAINING_RESOURCE_OBSERVATION.json',obs)
    ledger=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[base.entry(Path(__file__))]+[base.entry(p) for p in sources]+[base.entry(HERE/p) for p in
            ('PROTOCOL.md','RESULT.md','TABLE_AUDIT_IMPLICATIONS.md','POLICY_STABILITY_PREPARATION.md',
            'USER_PROVIDED_HANDOFF.md','VISIBLE_DIALOGUE.md','NEXT_STAGE_HANDOFF.md','DELIVERY.md','TRAINING_RESOURCE_OBSERVATION.json')]+
            [base.entry(ROOT/p) for p in ('paired_task_label_adapter_2026_10_08/RESULT.md',
                'paired_task_label_adapter_2026_10_08/POSTFIT_EXECUTION_BRIDGE.md',
                'task_utility_patient_exposure_2026_10_08/RESULT.md',
                'three_arm_resource_bridge_2026_10_08/RESULT.md',
                'three_arm_resource_bridge_2026_10_08/run_three_arm_real_resource.py')],
        source_bindings_verified=all_bindings,all_source_bindings_verified=True,source_originals_not_overwritten=True,
        actual_exits=[dict(chunk='c41744',exit_code=0,job='public_index_query',inherited_observed_exit_not_rerun=True),
            dict(chunk='8406d1',exit_code=0,job='fetch_two_public_primary_PDFs'),
            dict(chunk='e9f891',exit_code=0,job='render_11_primary_pages'),
            dict(chunk='37b390',exit_code=0,job='enlarge_same_supplemental_page_table'),
            dict(chunk='bb50d8',exit_code=0,job='CPU_reported_table_arithmetic_audit')],
        original_live_polls=[dict(chunk='fc84ca',session_id=99542,returned_session_id=99542,terminal_exit=None,
            raw_pchip_updates=1485,loss=1.1118382215499878,invocation02_new_updates=21285,cumulative_wall_seconds=48972.934279399924),
            dict(chunk='9c410e',session_id=99542,returned_session_id=99542,terminal_exit=None,
            raw_pchip_updates=1584,loss=1.1966423988342285,invocation02_new_updates=21384,cumulative_wall_seconds=49199.29063099995)],
        index_titles_screened=24,index_abstracts_screened=24,index_unique_versioned_papers=24,
        new_primary_papers_read=2,new_full_text_pages_read=33,visual_pages_reviewed=11,
        supplemental_table_same_page_detail_reviews=1,reported_summary_comparisons=6,reported_summary_condition_rows=108,
        reported_condition_rows_not_patient_records=True,CPU_arithmetic_only=True,
        medical_arrays_loaded=0,model_checkpoint_arrays_loaded_from_disk=0,MRI_neural_forwards=0,GPU_forwards=0,
        neural_forwards=0,real_medical_resource_updates=0,real_medical_formal_training_updates=0,head_fits=0,
        new_final_action_labels_generated=0,full_action_cost_measured=False,actual_new_MRI_task_benefit_measured=False,
        original56FOV_evaluation_launched=False,formal_three_arm_training_implemented_and_qualified=False,
        confirmation_patients_opened=False,lockedIXI_opened=False,original_terminal_training_modified=False,
        new_agents_delegated=0,automatic_approval_review_rejections_received=0,root_files_observed=roots,
        publication_claim_confirmed=False,goal_status='active',previous_goal_turn_classification='progress',
        current_goal_turn_classification='progress',current_progress='Read two directly relevant MRI policy papers and audited reported endpoint tradeoffs and policy inference costs; narrowed remaining empirical claim and prepared checkpoint-stability controls.',
        completion_audit=dict(original_two_arm_final_not_complete=True,original_task_capability_not_yet_evaluated=True,
            strong_matched_three_arm_task_effects_not_measured=True,full_action_cost_unknown=True,
            novel_MRI_effect_not_confirmed=True,eight_unseen_patient_confirmation_not_opened=True),
        ancillary_read_failures=['Broad Get-ChildItem search entered inaccessible retained temp paths; bounded rg used thereafter.',
            'Initial rg tools exclusion did not match absolute paths; corrected glob omitted tools.',
            'Read request for paired_task_label_adapter/PRIMARY_READING.md had no file; actual literature is in task_adaptation_compute_prior_art.'],
        original_live_process_terminal_exit_not_inferred_from_metadata=True,elapsed_seconds=time.perf_counter()-tick)
    base.new(HERE/'EXECUTION_LEDGER.json',ledger)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<30_000_000
    print(json.dumps(dict(complete=True,new_primary_papers_read=2,full_text_pages_read=33,visual_pages=11,
        medical_arrays_loaded=0,neural_forwards=0,gpu_free_bytes=freebytes,workspace_free_bytes=obs['workspace_free_bytes'],
        root_hashes_unchanged=True,publication_claim_confirmed=False,goal_status='active'),ensure_ascii=False),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
