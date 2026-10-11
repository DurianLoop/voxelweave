"""Bind direct observations, precise reading scope and zero-new-medical-array evidence."""
import hashlib
import json
import sys
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
    operations=[
        ('projection_production','experiments/observed_projection_information_2026_10_08/attempt01.json','f505cc'),
        ('projection_independent','experiments/observed_projection_information_2026_10_08/independent_modular_rational_attempt01.json','078eec'),
        ('primary_acquisition','literature/source_cache/selfsupervised_selection_primary_2026-10-08/acquisition_attempt01.json','1c612b'),
        ('primary_render','literature/source_cache/selfsupervised_selection_primary_2026-10-08/render_attempt01.json','f65930')]
    exits=[dict(key=key,**entry(ROOT/path),actual_observed_tool_chunk=chunk,actual_observed_tool_exit=0,observation_source='direct_live_tool_result') for key,path,chunk in operations]
    prod,verify,acquired,rendered=(read(ROOT/path) for key,path,chunk in operations)
    assert all(d['complete'] and not d['errors'] for d in (prod,verify,rendered))
    assert prod['summary']['series_with_nonzero_nullity']==12 and prod['summary']['observed_z_full_column_rank_series']==19
    assert verify['checked_series']==19 and verify['checked_unique_axis_maps']==22 and len(verify['axis_certificates'])==22
    for d in (prod,verify):
        for b in d['source_bindings']:assert sha(ROOT/b['path'])==b['sha256']
        assert all(d[key]==0 for key in ('medical_arrays_loaded','model_arrays_loaded','neural_forwards','GPU_forwards','training_updates'))
        assert not d['validation_data_read'] and not d['confirmation_patients_opened'] and not d['publication_claim_confirmed']
    assert acquired['new_primary_papers_read']==0 and len(acquired['records'])==2
    scopes=[]
    for paper in acquired['records']:
        assert paper['complete'] and not paper['errors'] and not paper['new_paper_read']
        pages=list(range(1,9)) if paper['key']=='noise2self' else [1,2,*range(4,29),36,40,45,46,54,55]
        texts=[p for p in paper['page_texts'] if p['physical_page'] in pages]
        images=[p for p in rendered['records'] if p['key']==paper['key']]
        assert len(texts)==len(pages) and all(not p['visually_reviewed'] for p in images)
        for b in [paper['PDF'],*texts,*images]:assert sha(ROOT/b['path'])==b['sha256']
        scopes.append(dict(key=paper['key'],PDF=paper['PDF'],acquired_physical_pages=paper['physical_pages'],
            physical_pages_text_read=pages,page_texts=texts,actual_visual_image_files=images,
            visual_reviewed_pages=[p['physical_page'] for p in images],
            unread_physical_pages=[p for p in range(1,paper['physical_pages']+1) if p not in pages],
            observation_source='actual_direct_text_reads_and_tools.view_image',
            text_read_tools=['85f5d8','c9c2cc','ee7620','887c02','c608c4','64f561']))
    assert sum(len(s['physical_pages_text_read']) for s in scopes)==41 and sum(len(s['actual_visual_image_files']) for s in scopes)==6
    provenance=ROOT/'literature/selfsupervised_selection_reading_provenance_2026-10-08.json'
    new(provenance,dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[entry(ROOT/path) for key,path,chunk in operations[2:]],scopes=scopes,
        new_primary_papers_read=2,acquired_physical_pages=77,text_pages_read=41,physical_pages_visual_reviewed=6,
        acquisition_and_render_receipts_not_rewritten=True,author_training_reproduced=False,
        all_supplementary_or_reference_pages_read=False,
        initial_batched_text_output_truncated=True,omitted_Noise2Self4_5_and_SSDU4_reread_completely=True,
        actual_visual_tool='functions.exec -> six tools.view_image with returned image blocks'))
    roots=[]
    for path,digest in [('D:/MRI/.gitignore','7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524'),('D:/MRI/environment.yml','dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257')]:
        assert sha(Path(path))==digest;roots.append(dict(path=path,sha256=digest,previous_sha256=digest,unchanged=True))
    observations=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],actual_exits=exits,
        production_seconds=prod['elapsed_seconds'],independent_seconds=verify['elapsed_seconds'],
        training_polls=[dict(tool_chunk='070c4f',session_id=99542,returned_same_live_session=True,new_output_lines=0,full_training_observed_tool_exit=None),
            dict(tool_chunk='59b89c',session_id=99542,returned_same_live_session=True,native_updates=14355,invocation02_new_updates=14256,cumulative_wall_seconds=32333.936733299983,full_training_observed_tool_exit=None),
            dict(tool_chunk='a4b5fb',session_id=99542,returned_same_live_session=True,native_updates=14553,invocation02_new_updates=14454,cumulative_wall_seconds=32806.313639499946,full_training_observed_tool_exit=None)],
        latest_GPU=dict(actual_observed_tool_chunk='d57e34',actual_observed_tool_exit=0,timestamp='2026/10/08 00:56:05.347',free_MiB=1394,total_MiB=24455,utilization_percent=93,new_GPU8GB_margin_met=False),
        acquisition_live_launch=dict(tool_chunk='f75069',session_id=17392,terminal_chunk='1c612b',terminal_exit=0),
        protocol_v1_not_executed=True,protocol_v2_pre_execution_source_contract_correction=True,
        new_scientific_execution_failures=0,automatic_approval_review_rejections_received=0,
        training_restarted=False,training_migrated=False,user_terminal_processes_controlled=False,
        other_processes_enumerated=False,new_agents_delegated=False)
    obsfile=ROOT/'SESSION_TOOL_OBSERVATIONS_PROJECTION_INFO_2026-10-08.json';new(obsfile,observations)
    ledger=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[entry(Path(__file__)),entry(obsfile),entry(provenance)]+[entry(ROOT/path) for key,path,chunk in operations],
        actual_exits=exits,unique_development_patients=11,unique_development_series=19,checked_axis_maps=22,
        exact_rank_independently_certified=True,series_with_inplane_nullity=12,series_observed_z_full_column_rank=19,
        synthetic_same_direct_input_and_statistics_witness_verified=True,
        medical_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,training_updates=0,
        array_counts_exclude_original_live_training_and_file_hash_byte_IO=True,
        native_PCHIP_total_information_superiority_claimed=False,float32_inverse_or_condition_number_certified=False,
        actual_MRI_task_benefit_measured=False,clinical_benefit_measured=False,real_latency_measured=False,
        new_primary_papers_read=2,text_pages_read=41,visual_pages_reviewed=6,root_files_observed=roots,
        original_training_session=99542,latest_training_poll=observations['training_polls'][-1],
        full_training_observed_tool_exit=None,latest_GPU=observations['latest_GPU'],
        formal_final_budget_completed=False,original56FOV_evaluated=False,all6_final_capability_gates_completed=False,
        confirmation_patients_opened=False,validation_data_read=False,locked_IXI_opened=False,
        old_MIRA_MSValid84_confirmation_preserved=True,publication_claim_confirmed=False,
        goal_status='active',current_goal_turn_classification='progress')
    new(ROOT/'SESSION_EXECUTION_LEDGER_PROJECTION_INFO_2026-10-08.json',ledger)
    print(json.dumps(dict(complete=True,checked_series=19,checked_axis_maps=22,new_medical_arrays=0,
        new_primary_papers_read=2,text_pages_read=41,visual_pages_reviewed=6,root_hashes_unchanged=True,
        latest_native_updates=14553,full_training_exit=None,goal_status='active',publication_claim_confirmed=False)),flush=True)
    return 0


if __name__=='__main__':raise SystemExit(main())
