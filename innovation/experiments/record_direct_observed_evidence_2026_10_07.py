"""Record actual observed tool exits and source reading scope, without closing live training."""
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def new(p,v):
    with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def main():
    records=[('first_download_and_failed_extraction','1882ca',1,None,'literature/source_cache/direct_observed_primary_2026-10-07/download_attempt01.json'),
             ('recovered_Poppler_extraction','644ac8',0,None,'literature/source_cache/direct_observed_primary_2026-10-07/extraction_attempt02.json'),
             ('all19_observed_and_synthetic_qualification','82fbfe',0,3696,'experiments/mc_rc_3d_direct_observed_qualification_2026_10_07/attempt01.json'),
             ('independent_coordinates_and_functional_updates','ed3e4d',0,32519,'experiments/mc_rc_3d_direct_observed_independent_2026_10_07/attempt01.json'),
             ('two_primary_source_renders','f7940c',0,None,'literature/source_cache/direct_observed_primary_2026-10-07/render_attempt01.json'),
             ('Jaritz_title_identity','e37fa9',0,None,'literature/source_cache/sparse_dense_counterpoint_2026-10-07/identity_attempt01.json'),
             ('Jaritz_original_acquisition_extraction','6e2582',0,18639,'literature/source_cache/sparse_dense_counterpoint_2026-10-07/acquisition_attempt01.json'),
             ('Jaritz_source_renders','199006',0,None,'literature/source_cache/sparse_dense_counterpoint_2026-10-07/render_attempt01.json')]
    exits={k:dict(chunk=c,observed_tool_exit=e,session=s,result=entry(ROOT/p)) for k,c,e,s,p in records}
    q=read(ROOT/records[2][4]);v=read(ROOT/records[3][4]);assert q['complete'] and v['complete'] and not q['errors'] and not v['errors']
    assert v['source_sha256']==sha(ROOT/records[2][4]) and len(q['series'])==len(v['series'])==19 and all(q['gate'].values())
    new(ROOT/'SESSION_OBSERVED_EXITS_DIRECT_OBSERVED_2026-10-07.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        script_sha256=sha(__file__),observed_exits=exits,full_training_observed_tool_exit=None,own_live_training_session=99542,
        formal_final_budget_completed=False,publication_claim_confirmed=False,goal_status='active'))
    source=ROOT/'literature/source_cache/direct_observed_primary_2026-10-07'
    ext=read(source/'extraction_attempt02.json');papers=[]
    scopes=[('sparsity_invariant',list(range(1,9)),'1708.06500v2'),('confidence_propagation',list(range(1,14)),'1811.01791v2')]
    for key,pages,version in scopes:
        record=next(r for r in ext['records'] if r['key']==key)
        papers.append(dict(key=key,version=version,pdf=entry(source/(key+'.pdf')),physical_pages=record['physical_pages'],
                           complete_pages_actually_read=pages,text_page_files=[r for r in record['texts'] if r['page'] in pages],
                           complete_text_page_exception=[7] if key=='confidence_propagation' else [],
                           exception_explanation='Page7 diagram-heavy text was truncated; complete rendered page actually read.' if key=='confidence_propagation' else None))
    counter=ROOT/'literature/source_cache/sparse_dense_counterpoint_2026-10-07';j=read(counter/'acquisition_attempt01.json')
    papers.append(dict(key='jaritz_sparse_dense',version='1808.00769v2',pdf=entry(counter/'jaritz_sparse_dense.pdf'),
                       physical_pages=j['physical_pages'],complete_pages_actually_read=list(range(1,9)),
                       text_page_files=[r for r in j['texts'] if r['page']<=8],complete_text_page_exception=[]))
    views=read(source/'render_attempt01.json')
    views.extend(dict(key='jaritz_sparse_dense',**r) for r in read(counter/'render_attempt01.json'))
    for row in views:
        assert sha(ROOT/row['file'])==row['sha256'];row.update(actual_view_image_executed=True,
            actual_complete_rendered_page_read=True,visual_review_performed=True,
            tool='functions.exec -> tools.view_image; images forwarded with image() in current continuation')
    provenance=dict(created_utc=datetime.now(timezone.utc).isoformat(),papers=papers,new_primary_papers_method_results_read=3,
        successful_primary_PDF_pages=39,selected_complete_pages_actually_read=29,selected_complete_text_pages_actually_read=28,
        actual_source_visual_reviews=views,actual_source_visual_pages_reviewed=6,author_experiments_reproduced=False,
        source_text_read_tool_chunks=['1bb96f','f8446f','a93836','574e66','312c71','bf2e97','d15793','ee287c','8c05dd','92b14c','874dbb','bb4e8d','bd62ef'],
        truncated_acquisition_outputs_not_treated_as_complete_text=True,paper_findings_not_MRI_task_evidence=True)
    new(source/'reading_provenance.json',provenance)
    rootpaths=[Path('D:/MRI/.gitignore'),Path('D:/MRI/environment.yml')]
    progress=dict(created_utc=datetime.now(timezone.utc).isoformat(),own_live_runs=[99542],last_actual_tool_poll_chunk='42bef7',
        last_actual_tool_poll_exit=None,native_last_committed_update_observed=5940,invocation02_new_updates_observed=5841,
        cumulative_train_wall_seconds_observed=12618.774595899973,
        PCHIP_previous_actual_history_snapshot=99,PCHIP_snapshot_is_not_current_live_tool_progress=True,
        full_training_observed_tool_exit=None,formal_final_budget_completed=False,final_models_evaluated=False,
        MRI_task_effects_scored_by_this_stage=False,new_stage_MRI_training_updates=0,new_stage_synthetic_updates=8,new_stage_GPU_forwards=0,
        GPU_last_actual_query=dict(tool_chunk='2e61be',timestamp_local='2026/10/07 19:16:35.293',free_MiB=1394,total_MiB=24455,util_percent=90),
        root_files_observed=[dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size,modified_by_this_stage=False) for p in rootpaths],
        current_3D_lesion_confirmation_patients=0,whole_project_confirmation_zero_not_claimed=True,
        other_processes_modified=False,publication_claim_confirmed=False,goal_status='active')
    new(ROOT/'SESSION_EXECUTION_PROGRESS_DIRECT_OBSERVED_2026-10-07.json',progress)
    ledger=dict(created_utc=datetime.now(timezone.utc).isoformat(),observed_exits=exits,
        qualification=dict(complete=True,series=19,elapsed_seconds=q['elapsed_seconds'],synthetic_updates=6,
                           parameters=q['model_checks'],augmentation=q['augmentation_checks']),
        independent_replay=dict(complete=True,series=19,elapsed_seconds=v['elapsed_seconds'],synthetic_updates=2,
            coordinate_samples_per_channel=sum(s['checks'][0]['samples'] for s in v['series']),
            max_numerator_abs_error=max(c['max_abs_error'] for s in v['series'] for c in s['checks'] if c['channel']=='numerator'),
            max_availability_abs_error=max(c['max_abs_error'] for s in v['series'] for c in s['checks'] if c['channel']=='availability'),
            coordinate_tolerance=dict(atol=3e-5,rtol=3e-5),functional_replay=v['synthetic_replay']),
        reading_scope=provenance,publication_claim_confirmed=False,goal_status='active',own_live_runs=[99542])
    new(ROOT/'SESSION_EXECUTION_LEDGER_DIRECT_OBSERVED_2026-10-07.json',ledger)
    print(json.dumps(dict(complete=True,observed_exits=len(exits),primary_papers=3,selected_complete_pages=29,actual_visual_pages=6,
                         qualified_development_series=19,synthetic_updates=8,own_live_runs=[99542])));return 0
if __name__=='__main__':raise SystemExit(main())
