"""Bind actual tool exits, reading scope, source hashes and current-stage counts."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def new(p,r):
    with p.open('x',encoding='utf-8') as s:json.dump(r,s,ensure_ascii=False,indent=2);s.write('\n')
def main():
    sys.stdout.reconfigure(encoding='utf-8');observations=ROOT/'SESSION_TOOL_OBSERVATIONS_REAL_SUPPORT_2026-10-07.json';obs=read(observations)
    bindings=[]
    for key,v in obs['observed_exits'].items():
        assert v.get('exit',v.get('exit_code'))==0
        p=ROOT/v['result'];r=read(p)
        if 'records' in r:assert all(x['complete'] and not x['errors'] for x in r['records'])
        else:assert r['complete'] and not r['errors']
        bindings.append(dict(key=key,**entry(p),actual_observed_tool_chunk=v.get('chunk',v.get('chunk_id')),actual_observed_tool_exit=0))
    scopes=[dict(key='sact',cache='spatial_compute_primary_2026-10-07',main_pages=list(range(1,9)),references_pages_read=[9,10],visual_pages=[5,7],
        text_read_tool_chunks=['7176f7','bf86b5','04c21f','fe9085','18b177'],render_keys=['sact_method','sact_cost']),
        dict(key='dynconv',cache='spatial_compute_primary_2026-10-07',main_pages=list(range(1,9)),references_pages_read=[9,10],visual_pages=[4,8],
        text_read_tool_chunks=['cb4fd2','324c1f','68ce05','ecf3f9','6aeb27'],render_keys=['dynconv_method','dynconv_cost']),
        dict(key='sbnet',cache='spatial_compute_sbnet_2026-10-07',main_pages=list(range(1,9)),references_pages_read=[],visual_pages=[4,6,8],
        text_read_tool_chunks=['c3b007','1bb852','226a78'],render_keys=['sbnet_method','sbnet_single_cost','sbnet_full_cost'])]
    for scope in scopes:
        directory=ROOT/'literature/source_cache'/scope['cache'];acq=read(directory/'acquisition_attempt01.json')
        row=next(r for r in acq['records'] if r['key']==scope['key']);assert row['physical_pages']==10 and row['complete']
        assert sha(ROOT/row['pdf_file'])==row['pdf_sha256'];scope['PDF']=entry(ROOT/row['pdf_file']);scope['page_texts']=row['page_texts']
        for text in row['page_texts']:assert sha(ROOT/text['path'])==text['sha256'] and text['extraction_exit']==0
        scope['actual_visual_image_files']=[entry(directory/(key+'.png')) for key in scope['render_keys']]
        assert all(next(x for x in obs['render_actual_tool_results'] if x['label']==key)['exit_code']==0 for key in scope['render_keys'])
    reading=ROOT/'literature/spatial_compute_reading_provenance_2026-10-07.json'
    new(reading,dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],source_bindings=[entry(observations)],
        scopes=scopes,new_primary_papers_read=3,physical_PDF_pages_acquired=30,main_physical_pages_text_read=24,physical_pages_visual_reviewed=7,
        supplementary_materials_read=False,author_experiments_reproduced=False,all_figure_pages_visually_read=False,systematic_review=False,
        previous_truncated_reads_corrected=True,render_warnings_retained_in_tool_observations=True))
    prod=read(ROOT/obs['observed_exits']['real_support_production']['result']);ind=read(ROOT/obs['observed_exits']['real_support_independent']['result'])
    assert prod['development_patients']==11 and prod['development_series']==ind['checked_series']==19 and prod['total_tiles']==1139
    assert ind['checked_supports']==38 and ind['checked_single_plane_actions']==806
    assert prod['developer_label_arrays_loaded']==ind['developer_label_arrays_loaded']==19 and prod['new_MRI_pixel_arrays_loaded']==0
    assert not prod['cuda_initialized'] and not prod['confirmation_patients_opened'] and not ind['confirmation_patients_opened']
    previous=read(ROOT/'SESSION_EXECUTION_PROGRESS_PATIENT_BASELINE_2026-10-07.json');root_files=[]
    for old in previous['root_files_observed']:
        p=Path(old['path']);root_files.append(dict(path=str(p),sha256=sha(p),previous_sha256=old['sha256'],unchanged_since_previous_record=sha(p)==old['sha256']))
    ledger=ROOT/'SESSION_EXECUTION_LEDGER_REAL_SUPPORT_2026-10-07.json'
    new(ledger,dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],script_sha256=sha(__file__),
        source_bindings=[entry(observations),entry(reading)]+[dict(path=x['path'],sha256=x['sha256']) for x in bindings],actual_exits=bindings,
        new_primary_papers_read=3,main_text_pages_read=24,visual_pages_reviewed=7,developer_label_reads=38,unique_development_patients=11,
        unique_development_series=19,checked_joint_supports=38,checked_single_plane_actions=806,
        new_MRI_pixel_arrays_loaded=0,new_model_forwards=0,new_GPU_forwards=0,new_training_updates=0,
        running_original_training_excluded_from_annotation_experiment_update_count=True,
        root_files_observed=root_files,other_processes_modified=False,validation_arrays_loaded=0,confirmation_patients_opened=False,
        publication_claim_confirmed=False,actual_MRI_risk_certificates_issued=0,old_MIRA_MSValid84_confirmation_preserved=True,
        own_live_runs=[99542],full_training_observed_tool_exit=None,formal_final_budget_completed=False,
        current_goal_turn_classification='progress',previous_goal_turn_classification='progress',goal_status='active'))
    print(json.dumps(dict(complete=True,new_primary_papers_read=3,developer_label_reads=38,checked_series=19,checked_supports=38,checked_single_plane_actions=806,
        root_files_unchanged=all(x['unchanged_since_previous_record'] for x in root_files),publication_claim_confirmed=False)));return 0
if __name__=='__main__':raise SystemExit(main())
