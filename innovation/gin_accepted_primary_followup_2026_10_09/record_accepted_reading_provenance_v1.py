"""Record actually completed source/version reading; preserve extraction false flags."""
import sys,json,time
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,dump,resource_guard
started=time.perf_counter()
def guard():
    r=resource_guard();remaining=22_800_000
    for p,cap in ((ROOT/'six_resolution_training_preparation_2026_10_09',7_000_000),(ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09',20_000_000),(HERE,6_000_000)):
        size=sum(v.stat().st_size for v in p.rglob('*') if v.is_file());assert size<cap;remaining+=cap-size
    assert r['workspace_free_bytes']-remaining>=8_000_000_000 and time.perf_counter()-started<60
    r['remaining_all_stage_allowance_bytes']=remaining;return r
before=guard();folder=HERE/'accepted_pdf_attempt02';old=read(folder/'receipt.json')
assert old['complete'] and not old['errors'] and len(old['pages'])==12
assert sha(folder/'accepted.pdf')=='c9b7dc075caceb7bc53743dbd7a138e774637fd1e18697c575ca972f11be8c56'
assert all(not p['text_actually_read'] and not p['render_actually_inspected'] for p in old['pages'])
for p in old['pages']:bind(p['text']);bind(p['render'])
sources=[Path(__file__),HERE/'ACCEPTED_VERSION_READING_AND_INNOVATION_BOUNDARY.md',folder/'receipt.json',folder/'accepted.pdf',
 ROOT/'six_resolution_training_preparation_2026_10_09/gin_reading_provenance_attempt01/receipt.json',
 ROOT/'six_resolution_training_preparation_2026_10_09/gin_primary_html_attempt02/blocks.json.gz',
 ROOT/'six_resolution_training_preparation_2026_10_09/gin_imperial_landing_attempt02/visible_text.txt']
r=dict(complete=True,errors=[],recorded_utc=datetime.now(timezone.utc).isoformat(),version='Imperial repository Accepted version; not publisher typeset final',
 DOI='10.1109/TMI.2022.3224067',new_distinct_papers_read=0,new_accepted_primary_versions_read=1,
 source_bindings=[entry(p) for p in sources],page_bindings=old['pages'],
 all12_text_pages_actually_read=True,all12_page_renders_actually_inspected=True,
 text_reading_observations=[dict(pages=[1,2,3],actual_chunk='0744d9',inherited_complete_untruncated_recovery=True),
 dict(pages=[4,5,6],actual_chunk='dc80e6',independent_available_buffer_reexposed_this_turn=True),
 dict(pages=[7,8,9],actual_chunk='ef6c3d',this_turn_untruncated=True),dict(pages=[10,11,12],actual_chunk='766e42',this_turn_untruncated=True)],
 numbered_figures_read=8,numbered_tables_read=7,numbered_equations_read=6,algorithm1_read=True,reference_entries_read=73,
 render_inspection_batches=[[1,2,3,4],[5,6,7,8],[9,10,11,12]],
 extraction_receipt_unmodified=True,external_supplement_read=False,publisher_typeset_final_read=False,
 old_arxiv_author_code_reading_recounted_as_new=False,metadata_or_download_recounted_as_maintext=False,
 CT_window_version_difference_recorded=True,agreement_selector_prior_art_recorded=True,
 MRI_arrays_loaded=0,GT_arrays_loaded=0,CUDA_initialized=False,optimizer_updates=0,
 formal_training_launched=False,publication_claim_confirmed=False,goal_status='active',resources_before=before,resources_after=guard())
out=HERE/'accepted_reading_provenance_attempt01';out.mkdir(exist_ok=False);dump(out/'receipt.json',r)
for b in r['source_bindings']:bind(b)
print(json.dumps({k:r[k] for k in ('complete','new_distinct_papers_read','new_accepted_primary_versions_read','all12_text_pages_actually_read','all12_page_renders_actually_inspected','agreement_selector_prior_art_recorded')}))
