"""Record actual primary reading plus synthetic and development entry qualifications."""
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
    records=read(HERE/'ACTUAL_TOOL_OBSERVATIONS_PART01.json');lookup={x['key']:x for x in records['entries']};assert all(x['found'] for x in lookup.values())
    def result(key,expected_exit=0):
        rows=list(actual(lookup[key]['value']));assert len(rows)==1,key
        r=rows[0];assert r.get('exit_code')==expected_exit,key
        return dict(store_key=key,chunk_id=r['chunk_id'],exit_code=expected_exit,tool_output_truncated='Warning: truncated output' in r.get('output',''))
    clinical=[result(k) for k in ['turn21_clinical_vs_read_0_42','turn21_clinical_vs_read_43_88_and_table','turn21_clinical_vs_read_89_126_and_supp_metadata']]
    label=[result(k) for k in ['turn21_label_preserving_read_0_33','turn21_label_preserving_read_34_89_and_tables']]
    assert not any(x['tool_output_truncated'] for x in clinical+label)
    extraction=read(HERE/'extraction_attempt01/receipt.json');assert extraction['complete'] and extraction['local_only'] and extraction['additional_HTTP_GETs']==0
    code_runs=[result('turn21_roundtrip_qualification_actual'),result('turn21_clinical_and_texture_actual_0'),result('turn21_clinical_and_texture_actual_1')]
    devrun=result('turn21_real_roundtrip_entry_poll1');dev=read(HERE/'real_development_entry_attempt01/receipt.json')
    assert dev['complete'] and not dev['errors'] and len(dev['series'])==19 and dev['MR_input_arrays_loaded']==38 and dev['GT_arrays_loaded']==19
    assert dev['all38_real_batches_verified'] and dev['all38_original_GT_kept_exactly'] and dev['training_updates']==dev['neural_forwards']==dev['model_arrays_loaded']==0
    assert not dev['CUDA_initialized'] and not dev['validation_pixels_loaded'] and not dev['confirmation_patients_opened']
    for rel in ['roundtrip_synthetic_attempt01/receipt.json','roundtrip_texture_attempt01/receipt.json','clinical_time_audit_attempt01/receipt.json']:
        q=read(HERE/rel);assert q['complete'] and not q['errors'] and q['medical_arrays_loaded']==q['neural_forwards']==0 and not q['CUDA_initialized']
    roots={'.gitignore':'7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524','environment.yml':'dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257'}
    assert all(sha(ROOT.parent/k)==v for k,v in roots.items())
    sources=[Path(__file__),HERE/'ACTUAL_TOOL_OBSERVATIONS_PART01.json',HERE/'PRIMARY_READING_AND_PROJECT_DECISIONS.md',
        HERE/'MATCHED_ROUNDTRIP_NEXT_TRIAL_PREPARATION.md',HERE/'extraction_attempt01/receipt.json',HERE/'extraction_attempt01/clinical_vs_blocks.json',
        HERE/'extraction_attempt01/clinical_vs_tables.json',HERE/'extraction_attempt01/label_preserving_blocks.json',HERE/'extraction_attempt01/label_preserving_tables.json',
        HERE/'primary_attempt01/clinical_vs.xml',HERE/'primary_attempt01/label_preserving.xml',HERE/'index_attempt01/receipt.json',
        HERE/'roundtrip_synthetic_attempt01/receipt.json',HERE/'roundtrip_texture_attempt01/receipt.json',HERE/'clinical_time_audit_attempt01/receipt.json',
        HERE/'real_development_entry_attempt01/receipt.json',HERE/'label_preserving_roundtrip.py']
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],new_distinct_primary_maintexts_completed=2,
        papers=[dict(doi='10.1093/jamiaopen/ooaf163',pmcid='PMC12772638',version='public journal fullTextXML',
            scientific_maintext_ranges_inclusive=[[0,88]],other_extracted_body_ranges_inclusive=[[89,126]],primary_maintext_read=True,
            external_Appendix_A_B_read=False,figure_pixels_reviewed=False,references_complete=False,actual_reads=clinical),
            dict(doi='10.1002/nbm.70266',pmcid='PMC12983123',version='public journal fullTextXML',
            scientific_maintext_ranges_inclusive=[[0,62]],other_extracted_body_ranges_inclusive=[[63,89]],primary_maintext_read=True,
            external_docx_supplement_read=False,figure_pixels_reviewed=False,references_complete=False,actual_reads=label)],
        screened_index_records_including_duplicates=16,query_total_hits=[43,20],screening_not_systematic_review=True,
        previous_vs_cascade_crossMoDA_MC_RC_not_counted_as_new=True,failed_acquisition_terminal_preserved=result('turn21_selected_vs_primaries_terminal',1),
        local_title_reconciliation_and_extraction=result('turn21_reconciled_xml_extraction_actual'),additional_HTTP_GETs_for_reconciliation=0,
        original_inner_acquisition_returns_recovered=False,author_code_executed=False,
        synthetic_and_table_script_exits=code_runs,synthetic_and_table_exploration_topics=2,synthetic_and_table_script_executions=3,
        qualified_development_entry_exit=devrun,development_patients=11,development_series=19,qualified_real_input_batches=38,
        development_MR_arrays_loaded=38,development_GT_arrays_loaded=19,task_model_arrays_loaded=0,neural_forwards=0,new_training_updates=0,
        new_patient_medical_effects=0,new_validation_evaluation_executed=False,confirmation_patients_opened=0,
        root_environment_and_gitignore_unchanged=True,goal_status='active',publication_claim_confirmed=False,
        root_file_bindings=[dict(path='../'+k,sha256=v,bytes=(ROOT.parent/k).stat().st_size) for k,v in roots.items()],
        source_bindings=[entry(p) for p in sources],elapsed_seconds=time.perf_counter()-started)
    dump(HERE/'READING_PROVENANCE.json',r);assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    print(json.dumps(dict(complete=True,new_primary_maintexts=2,synthetic_and_table_script_executions=3,qualified_real_input_batches=38,
        new_training_updates=0,new_patient_medical_effects=0,publication_claim_confirmed=False,elapsed_seconds=r['elapsed_seconds'])),flush=True)
if __name__=='__main__':main()
