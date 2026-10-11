"""Bind actual observed tool exits and source reading, while preserving live-training status."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def new(p,v):
    with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def binding(p):return dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),bytes=p.stat().st_size)

def main():
    sys.stdout.reconfigure(encoding='utf-8');stamp=datetime.now(timezone.utc).isoformat()
    paths={
        'primary_acquisition':ROOT/'literature/source_cache/incremental_inference_primary_2026-10-07/acquisition_attempt01.json',
        'alternate_acquisition':ROOT/'literature/source_cache/deepcache_cvpr_alternate_2026-10-07/acquisition_attempt02.json',
        'MRI_cache_qualification':ROOT/'experiments/mc_rc_3d_local_edit_cache_2026_10_07/attempt01.json',
        'metadata_cost_preparation':ROOT/'experiments/mc_rc_3d_local_edit_cache_2026_10_07/development_metadata_cost_attempt01.json',
        'source_page_render':ROOT/'literature/source_cache/incremental_inference_key_page_renders_2026-10-07/render_attempt01.json'}
    observations={
        'primary_acquisition':dict(session_id=24951,terminal_chunk='428f24',observed_tool_exit=1),
        'alternate_acquisition':dict(session_id=76982,terminal_chunk='ebaceb',observed_tool_exit=0),
        'MRI_cache_qualification':dict(session_id=72885,terminal_chunk='a23c43',observed_tool_exit=0),
        'metadata_cost_preparation':dict(session_id=30385,terminal_chunk='223f0f',observed_tool_exit=0),
        'source_page_render':dict(session_id=None,terminal_chunk='c0a71f',observed_tool_exit=0)}
    for name,p in paths.items():observations[name].update(result=binding(p))
    q=read(paths['MRI_cache_qualification']);assert q['complete'] and q['qualification_passed'] and not q['errors']
    assert all(q['gates'].values()) and q['cached_vs_full']['voxels']==1966080
    assert q['label_arrays_loaded']==q['training_updates']==q['GPU_updates']==0 and not q['cuda_initialized']
    m=read(paths['metadata_cost_preparation']);assert m['complete'] and not m['errors'] and m['total_tiles']==1139
    assert m['real_MRI_arrays_loaded']==m['GT_arrays_loaded']==m['actual_model_forwards']==0
    acquisitions=read(paths['primary_acquisition'])['records']+read(paths['alternate_acquisition'])['records']
    papers=[]
    for key,fullpages,partial in (
        ('deltacnn',list(range(1,9)),[]),
        ('sige',list(range(1,12))+[15,16],[dict(physical_page=12,scope='limitation paragraphs and Figure13 caption; reference list not counted'),
                                          dict(physical_page=13,scope='reference22 search only'),
                                          dict(physical_page=14,scope='references, not additional primary papers')]),
        ('deepcache_cvpr',list(range(1,9)),[])):
        a=next(a for a in acquisitions if a['key']==key);assert a['complete']
        pdf=ROOT/a['pdf_file'];assert sha(pdf)==a['pdf_sha256'];page_index={p['physical_page']:p for p in a['page_texts']}
        actual=[]
        for page in fullpages:
            record=page_index[page];p=ROOT/record['text_file'];assert sha(p)==record['text_sha256']
            actual.append(dict(physical_page=page,**binding(p)))
        papers.append(dict(key=key,pdf=binding(pdf),physical_pages=a['physical_pages'],
            complete_page_texts_read=actual,partial_or_reference_reading=partial,
            entire_PDF_all_pages_read=False,author_code_or_experiments_reproduced=False))
    render=read(paths['source_page_render']);assert render['complete']
    visuals=[]
    for item in render['records']:
        p=ROOT/item['image_file'];assert sha(p)==item['image_sha256']
        visuals.append(dict(key=item['key'],physical_page=item['physical_page'],image=binding(p),
            actual_view_image_executed=True,view_image_tool_cell='all3 source images, original detail',
            checked_content={'deltacnn':'Eq3-6 nonlinear update and truncation buffers / Fig3',
                             'sige':'normalization-reuse assumption at right-column bottom / convolution linearity',
                             'deepcache':'Fig3 high-level branch cache / non-uniform1:N Eq7'}[item['key']]))
    provenance=dict(created_utc=stamp,complete=True,script_sha256=sha(__file__),new_primary_papers_method_results_read=3,
        new_abstracts_read=0,downloaded_original_PDF_physical_pages=42,complete_text_pages_read=29,
        source_visual_pages_reviewed=3,papers=papers,source_visual_review=visuals,
        note='Full selected page text reading; SIGE4-5 and15-16 re-read after truncation. No all-PDF reading or systematic-review completeness claim.',
        arxiv_deepcache_over_budget_failure_preserved=True,confirmation_patients_opened=False,publication_claim_confirmed=False)
    new(ROOT/'literature/source_cache/incremental_inference_key_page_renders_2026-10-07/reading_provenance.json',provenance)
    ledger=dict(created_utc=stamp,complete=True,script_sha256=sha(__file__),observed_exits=observations,
        actual_new_training_updates_from_this_stage=0,actual_new_GPU_updates=0,
        actual_MRI_task_network_forwards_in_structure_qualification=28,actual_MRI_tiles_in_structure_qualification=56,
        actual_MRI_task_effect_metrics_scored=False,actual_GT_arrays_loaded=0,
        scientific_confirmation_patients=0,publication_claim_confirmed=False,goal_status='active',
        own_live_runs=[99542],full_training_observed_tool_exit=None,final_execution_closed=False)
    new(ROOT/'SESSION_EXECUTION_LEDGER_INCREMENTAL_INFERENCE_2026-10-07.json',ledger)
    print(json.dumps(dict(complete=True,new_primary_papers_read=3,complete_text_pages_read=29,
        source_visual_pages_reviewed=3,MRI_cache_qualification_observed_exit=0,metadata_cost_observed_exit=0,
        own_live_runs=[99542],full_training_exit=None)),flush=True)
    return 0

if __name__=='__main__':raise SystemExit(main())
