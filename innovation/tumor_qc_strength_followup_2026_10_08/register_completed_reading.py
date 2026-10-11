"""Register actually read primary ranges using saved tool observations; never rewrite acquisition receipts."""
import sys,json,time
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,dump,resource_guard
def actual(v):
    if isinstance(v,dict):
        if 'chunk_id' in v and ('exit_code' in v or 'session_id' in v):yield v
        for x in v.values():yield from actual(x)
    elif isinstance(v,list):
        for x in v:yield from actual(x)
def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resource_guard()
    observations=read(HERE/'ACTUAL_TOOL_OBSERVATIONS_PART01.json')
    lookup={x['key']:x for x in observations['entries']};assert all(x['found'] for x in lookup.values())
    def result(key):
        rows=list(actual(lookup[key]['value']));assert len(rows)==1,key
        r=rows[0];assert r.get('exit_code')==0,key
        return dict(store_key=key,chunk_id=r['chunk_id'],exit_code=0,tool_output_truncated='Warning: truncated output' in r.get('output',''))
    qr=[result(k) for k in ['turn20_qcresunet_read_0_17','turn20_qcresunet_read_18_30','turn20_qcresunet_read_31_53','turn20_qcresunet_read_54_74','turn20_qcresunet_read_75_95','turn20_qcresunet_read_96_108','turn20_qcresunet_appendix_read172_199']]
    jr=[result(k) for k in ['turn20_jungo_read_0_37','turn20_jungo_read_38_70','turn20_jungo_read_71_97','turn20_jungo_read_98_115_and_table']]
    assert not any(x['tool_output_truncated'] for x in qr+jr)
    author=[result('turn20_author_read_'+k) for k in ['README_md','utils_py','dataloading_py','main_py']]
    assert not any(x['tool_output_truncated'] for x in author)
    for p in [HERE/'static_semantics_attempt01/receipt.json',HERE/'uncertainty_definition_attempt01/receipt.json']:
        q=read(p);assert q['complete'] and not q['errors'] and not q['CUDA_initialized'] and q['medical_arrays_loaded']==0
    assert sha(HERE/'primary_sources_attempt01/qcresunet_arxiv_v2.html')=='8cc2f419bbc8e87e84769dd9e875b28d144556e3a3733263ef28ad901bdd0508'
    assert sha(HERE/'jungo_primary_attempt01/fulltext.xml')=='7c71cfa634f58afa53c79c3787de61091a818406482766ee400cc45e73fda6aa'
    assert sha(ROOT.parent/'.gitignore')=='7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524'
    assert sha(ROOT.parent/'environment.yml')=='dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257'
    sources=[Path(__file__),HERE/'ACTUAL_TOOL_OBSERVATIONS_PART01.json',HERE/'PRIMARY_READING_AND_PROJECT_DECISIONS.md',
        HERE/'STRONG_QC_AND_ACTION_PREPARATION.md',HERE/'TASK_NETWORK_UNCERTAINTY_INTERFACE_PREPARATION.md',
        HERE/'identity_attempt01/receipt.json',HERE/'primary_sources_attempt01/receipt.json',HERE/'extraction_attempt01/receipt.json',
        HERE/'extraction_attempt01/blocks.json',HERE/'extraction_attempt01/tables.json',HERE/'extraction_attempt01/maths.json',
        HERE/'jungo_primary_attempt01/receipt.json',HERE/'jungo_primary_attempt01/fulltext.xml',HERE/'jungo_extraction_attempt01/blocks.json',
        HERE/'jungo_extraction_attempt01/tables.json',HERE/'jungo_extraction_attempt01/receipt.json',
        HERE/'author_root_sources_attempt01/receipt.json',HERE/'author_web_attempt01/receipt_v2.json',
        HERE/'static_semantics_attempt01/receipt.json',HERE/'uncertainty_definition_attempt01/receipt.json',
        ROOT/'experiments/mc_rc_3d_baseline_2026_10_07.py',ROOT/'experiments/mc_rc_3d_baseline_v2_2026_10_07.py',
        ROOT/'experiments/mc_rc_3d_19series_common_init_2026_10_07.py',ROOT/'spatial_adaptation_matched_2026_10_08/run_matched_adaptation.py',
        ROOT.parent/'.gitignore',ROOT.parent/'environment.yml']
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],new_distinct_primary_maintexts_completed=2,
        papers=[dict(title='QCResUNet: Joint subject-level and voxel-level segmentation quality prediction',doi='10.1016/j.media.2025.103718',
            actual_read_version='arXiv2412.07156v2 author preprint',journal_equivalence_asserted=False,
            primary_maintext_ranges_inclusive=[[0,107]],same_HTML_appendix_ranges_inclusive=[[172,199]],references_complete=False,actual_reads=qr),
            dict(title='Analyzing the Quality and Challenges of Uncertainty Estimations for Brain Tumor Segmentation',doi='10.3389/fnins.2020.00282',
            actual_read_version='public journal fullTextXML PMC7156850',scientific_maintext_ranges_inclusive=[[0,97]],
            other_extracted_body_ranges_inclusive=[[98,115]],external_supplements_read=False,references_complete=False,actual_reads=jr)],
        index_entries_screened=16,index_entries_not_counted_as_fulltexts=True,systematic_review_claimed=False,
        author_repository='sotiraslab/QCResUNet',author_commit='e9ddc2418c72cc1c20b69bd3074b7f96b8b5f408',
        author_code_files_completely_read=4,author_code_actual_reads=author,author_code_executed=False,whole_repository_reviewed=False,
        nonmedical_CPU_explorations=[result('turn20_static_semantics_actual'),result('turn20_uncertainty_definition_actual')],
        Jungo_fetch_full_tool_payload_saved=False,Jungo_fetch_displayed_metadata_and_source_receipt_saved=True,
        current_task_model_import_chain_read=True,current_selected_TaskUNet3D_and_ConvBlock_contain_no_dropout=True,
        new_patient_medical_results=0,confirmation_patients_opened=0,figure_pixels_reviewed=False,
        author_error_maps_or_uncertainty_heads_not_claimed_as_innovation=True,
        goal_status='active',publication_claim_confirmed=False,root_environment_and_gitignore_hashes_unchanged=True,
        source_bindings=[entry(p) for p in sources],elapsed_seconds=time.perf_counter()-started)
    dump(HERE/'READING_PROVENANCE.json',r)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    print(json.dumps(dict(complete=True,new_primary_maintexts=2,author_code_files_read=4,nonmedical_CPU_explorations=2,
        new_patient_results=0,goal_status='active',elapsed_seconds=r['elapsed_seconds'])),flush=True)
if __name__=='__main__':main()
