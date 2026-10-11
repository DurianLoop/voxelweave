"""New immutable provenance and live observations; no edits to any earlier evidence."""
import hashlib,json,sys
from pathlib import Path
from fractions import Fraction
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/'literature/source_cache/action_interaction_primary_2026-10-07'
RUN=ROOT/'experiments/mc_rc_3d_action_composition_2026_10_07'
LIVE=ROOT/'experiments/mc_rc_3d_19series_common_init_cpu_2026_10_07'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def binding(p):return dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),bytes=p.stat().st_size)
def new(p,r):assert not p.exists();p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    sys.stdout.reconfigure(encoding='utf-8');stamp=datetime.now(timezone.utc).isoformat()
    selections={'compressive_mri_verified':[1,*range(3,11)],'adaptive_submodularity':[1,*range(3,12),29,30,41],'scalable_mri_verified':[1,2,3,4,6,7,8]}
    versions={'compressive_mri_verified':'arXiv1805.01266v1 2018-05-03','adaptive_submodularity':'arXiv1003.3967v5 2017-12-06','scalable_mri_verified':'arXiv1902.00386v5 2020-03-16'}
    page_counts={'compressive_mri_verified':13,'adaptive_submodularity':60,'scalable_mri_verified':13}
    reviews=read(CACHE/'render_attempt01.json');assert len(reviews)==3
    for row in reviews:
        assert sha(ROOT/row['file'])==row['sha256'];row['actual_view_image_executed']=True
        row['visual_review']='Readable complete page; algorithm/definitions/table costs inspected in actual tool image'
    selected=[dict(key=key,verified_version=versions[key],PDF=binding(CACHE/(key+'.pdf')),physical_pages=page_counts[key],complete_text_pages_actually_read=[dict(page=i,**binding(CACHE/(key+f'_page{i:02d}.txt'))) for i in pages]) for key,pages in selections.items()]
    assert sum(len(r['complete_text_pages_actually_read']) for r in selected)==29
    provenance=dict(created_utc=stamp,new_primary_papers_method_and_main_results_read=3,successful_primary_PDF_pages=86,
        selected_complete_text_pages_actually_read=29,whole_PDFs_all_proofs_read=False,author_code_executed=False,author_experiments_reproduced=False,
        records=selected,actual_source_visual_reviews=reviews,excluded_wrong_identifier=dict(id='1710.09336',actual_title='Properly Ergodic Structures',counted_as_MRI_paper=False,complete_text_reading_claimed=False),
        failed_initial_extraction_preserved=True,root_environment_unchanged=True)
    new(CACHE/'reading_provenance.json',provenance)
    # Direct arithmetic on printed times and process counts, not raw author logs.
    tables=[('KTF152',6*24*60+23*60,152,3*60+25,38,170),('KTF256',7*24*60+8*60,256,5*60+20,64,173),('IST152',3*24*60+11*60,152,1*60+37,38,184),('ALOHA152',25*24*60+1*60,152,18*60+13,38,133)]
    ratios=[dict(row=name,printed_G_minutes=g,printed_G_processes=gp,printed_SG2_minutes=s,printed_SG2_processes=sp,printed_speedup=v,
        ratio_from_printed_formula_exact=str(Fraction(g*gp,s*sp)),ratio_from_printed_formula=float(Fraction(g*gp,s*sp)),
        reason_for_difference_not_inferred=True,author_raw_logs_reproduced=False) for name,g,gp,s,sp,v in tables]
    new(CACHE/'printed_cost_table_arithmetic_audit.json',dict(source=binding(CACHE/'scalable_mri_verified.pdf'),physical_page=8,formula='t_G*nproc_G/(t_SG2*nproc_SG2)',rows=ratios,extrapolated_times_present=True,no_local_speed_claim=True))
    probe=read(RUN/'attempt01.json');verify=read(RUN/'independent_tile_and_metric_control_attempt01.json')
    assert probe['complete'] and probe['qualification_passed'] and not probe['errors'] and verify['complete'] and not verify['errors']
    assert verify['source_sha256']==sha(RUN/'attempt01.json')
    exits={
        'first_acquisition':dict(chunk='372107',observed_tool_exit=1,result=binding(CACHE/'acquisition_attempt01.json')),
        'existing_Poppler_extraction':dict(session=84221,chunk='98eee8',observed_tool_exit=0,result=binding(CACHE/'extraction_attempt02.json')),
        'title_resolution':dict(chunk='0b0540',observed_tool_exit=0,result=binding(CACHE/'identity_attempt03.json')),
        'verified_MRI_primary':dict(chunk='06c869',observed_tool_exit=0,result=binding(CACHE/'verified_acquisition_attempt04.json')),
        'verified_scalable_primary':dict(chunk='48e11a',observed_tool_exit=0,result=binding(CACHE/'verified_acquisition_attempt05.json')),
        'real_MRI_8subset_probe':dict(session=41215,chunk='10321c',observed_tool_exit=0,result=binding(RUN/'attempt01.json')),
        'independent_tile_and_exact_metric_control':dict(chunk='c17d71',observed_tool_exit=0,result=binding(RUN/'independent_tile_and_metric_control_attempt01.json')),
        'source_page_render':dict(chunk='a7acd7',observed_tool_exit=0,result=binding(CACHE/'render_attempt01.json'))}
    new(ROOT/'SESSION_EXECUTION_LEDGER_ACTION_COMPOSITION_2026-10-07.json',dict(created_utc=stamp,script_sha256=sha(__file__),observed_exits=exits,
        successful_new_primary_readings=3,observed_MRI_probe_forward_calls=116,observed_MRI_probe_tiles=232,
        new_experiment_training_updates=0,new_GPU_forwards=0,new_MRI_task_benefit_scores=0,new_confirmation_patients=0,
        continuing_prior_training_not_included_in_new_experiment_zero=True,failures_retained=True,own_live_runs=[99542],full_training_observed_tool_exit=None,goal_status='active'))
    live=read(LIVE/'invocation02.json');histories={}
    for key in ('native_reference','raw_pchip'):
        lines=(LIVE/(key+'_history.jsonl')).read_text(encoding='utf-8').splitlines()
        records=[]
        for line in lines:
            try:records.append(json.loads(line))
            except json.JSONDecodeError:break
        assert records;histories[key]=dict(last_update_observed=records[-1]['update'],complete_history_records_observed=len(records),live_not_frozen=True)
    previous=read(ROOT/'SESSION_EXECUTION_PROGRESS_INCREMENTAL_INFERENCE_2026-10-07.json');roots=[]
    for old in previous['root_files_observed']:
        p=Path(old['path']);assert sha(p)==old['sha256'];roots.append(dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size,modified_by_this_stage=False))
    progress=dict(created_utc=stamp,own_live_runs=[99542],last_tool_poll_chunk='955369',last_tool_poll_observed_exit=None,
        last_tool_poll_native_committed_updates=4455,last_tool_poll_cumulative_wall_seconds=9148.547332599992,
        rolling_invocation_status=live['status'],rolling_invocation_complete=live['complete'],rolling_invocation_errors=live['errors'],
        rolling_invocation_new_cpu_backbone_updates=live['new_cpu_backbone_updates'],rolling_arms=[{k:a.get(k) for k in ('kind','updates_completed','complete')} for a in live['arms']],
        rolling_histories=histories,full_training_observed_tool_exit=None,formal_final_budget_completed=False,final_execution_closed=False,
        current_3D_lesion_confirmation_patients=0,whole_project_external_confirmation_zero_not_claimed=True,
        GPU_last_actual_query=dict(tool_chunk='a69785',timestamp_local='2026/10/07 18:22:45.923',free_MiB=1394,total_MiB=24455,util_percent=86),
        root_files_observed=roots,publication_claim_confirmed=False,goal_status='active')
    assert live['status']=='training' and not live['complete'] and not live['errors']
    new(ROOT/'SESSION_EXECUTION_PROGRESS_ACTION_COMPOSITION_2026-10-07.json',progress)
    print(json.dumps(dict(complete=True,new_primary_readings=3,selected_complete_pages=29,current_history_snapshots=histories,table_ratios=ratios,old_root_files_unchanged=True),ensure_ascii=False))
    return 0
if __name__=='__main__':raise SystemExit(main())
