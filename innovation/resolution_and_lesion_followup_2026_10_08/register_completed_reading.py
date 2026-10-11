"""Register observed complete reading, numerical qualifications and geometry-only scope."""
import sys,json,time
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,dump,resource_guard
def unwrap(value):return value['value'] if isinstance(value,dict) and 'status' in value else value
def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resource_guard()
    docs=[HERE/'ACTUAL_TOOL_OBSERVATIONS_PART01.json',HERE/'ACTUAL_TOOL_OBSERVATIONS_PART02.json']
    entries={x['key']:x for p in docs for x in read(p)['entries']};assert all(x['found'] for x in entries.values())
    def result(key,expected_exit=0):
        r=unwrap(entries[key]['value']);assert r.get('exit_code')==expected_exit,key
        return dict(store_key=key,chunk_id=r['chunk_id'],exit_code=expected_exit,tool_output_truncated='Warning: truncated output' in r.get('output',''))
    gou=[result(k) for k in ['turn22_gouhfi_read_0_44','turn22_gouhfi_read_45_98','turn22_gouhfi_read_99_126_untruncated','turn22_gouhfi_read_127_174_untruncated']]
    cla=[result(k) for k in ['turn22_claustrum_read_0_17_untruncated','turn22_claustrum_read_18_29_verified','turn22_claustrum_read_30_45_untruncated','turn22_claustrum_read_46_67','turn22_claustrum_read_68_87']]
    tables=result('turn22_compact_all_table_cells_and_inline_appendices');assert not any(x['tool_output_truncated'] for x in gou+cla+[tables])
    failed=result('turn22_primaries_start',1);fallback=result('turn22_fallback_start')
    syn=result('turn22_support_start');geom=result('turn22_geometry_audit_actual');fig=result('turn22_figure_actual')
    s=read(HERE/'support_synthetic_attempt01/receipt.json');g=read(HERE/'development_geometry_attempt01/receipt.json')
    assert s['complete'] and not s['errors'] and s['all16_synthetic_cases_passed'] and len(s['records'])==16 and not s['CUDA_initialized']
    assert g['complete'] and not g['errors'] and g['patch_support_plans']==76 and g['same_geometry_input_pairs']==38
    assert g['conservative_source_bbox_fits_count']==0 and g['direct_corner_outside_real_FOV_witness_count']==60
    assert all(v[k]==0 for v in [s,g] for k in ['medical_arrays_loaded','GT_arrays_loaded','model_arrays_loaded','neural_forwards','training_updates'])
    for v in [s,g]:
        for b in v['source_bindings']:bind(b)
    r0={'.gitignore':'7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524','environment.yml':'dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257'}
    assert all(sha(ROOT.parent/k)==v for k,v in r0.items())
    live=unwrap(entries['turn22_training_poll3']['value']);assert live['session_id']==29823 and live.get('exit_code') is None
    sources=[Path(__file__),*docs,HERE/'PROTOCOL.md',HERE/'PRIMARY_SELECTION.md',HERE/'FALLBACK_SELECTION.md',HERE/'PRIMARY_READING_AND_INNOVATION_DECISIONS.md',
        HERE/'NEXT_TRIAL_PREPARATION.md',HERE/'README.md',HERE/'extraction_attempt01/receipt.json',HERE/'primary_attempt01/HTTP_RECEIPT.json',
        HERE/'primary_attempt01/gouhfi.xml',HERE/'extraction_attempt01/gouhfi_blocks.json',HERE/'extraction_attempt01/gouhfi_tables.json',
        HERE/'fallback_attempt01/claustrum.xml',HERE/'fallback_attempt01/receipt.json',HERE/'fallback_attempt01/claustrum_blocks.json',
        HERE/'fallback_attempt01/claustrum_tables.json',HERE/'fallback_attempt01/claustrum_inline_appendices.json',
        HERE/'support_synthetic_attempt01/receipt.json',HERE/'development_geometry_attempt01/receipt.json',HERE/'FIGURE_PROVENANCE.json',HERE/'support_results.png',
        HERE/'roundtrip_support.py',HERE/'SUPPORT_EXPLORATION_PROTOCOL.md',HERE/'DEVELOPMENT_GEOMETRY_ONLY_PROTOCOL.md',HERE/'index_attempt01/receipt.json']
    result_doc=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],new_distinct_primary_maintexts_completed=2,
        papers=[dict(doi='10.1162/imag.a.960',pmcid='PMC12556684',scientific_maintext_blocks_inclusive=[0,145],other_body_blocks_inclusive=[146,174],
            inline_Appendix_A1_A2_and_A3_caption_read=True,tables_all_extracted_cells_read=7,actual_untruncated_reads=gou,primary_maintext_read=True,
            figure_pixels_reviewed=False,author_code_read=False,references_complete=False),
            dict(doi='10.1002/hbm.70303',pmcid='PMC12368599',scientific_maintext_blocks_inclusive=[0,85],support_metadata_blocks_inclusive=[86,87],
            inline_back_Appendix_A_B_read=True,tables_all_extracted_cells_read=3,actual_untruncated_reads=cla,primary_maintext_read=True,
            external_supporting_PDF_read=False,figure_pixels_reviewed=False,author_code_read=False,references_complete=False)],
        table_and_inline_appendix_actual_read=tables,selected_failed_acquisition=failed,substitute_actual_acquisition=fallback,
        unavailable_primaries_not_counted=[dict(doi='10.1016/j.neuroimage.2022.118933',HTTP_status=500),dict(doi='10.1007/978-3-032-16365-3_41',HTTP_status=500)],
        screened_index_records_including_duplicates=15,query_hit_counts=[3,42,7],systematic_review_claimed=False,
        synthetic_actual_exit=syn,development_geometry_actual_exit=geom,figure_actual_exit=fig,
        synthetic_cases=16,independent_intensity_oracle_points_per_case=32,independent_full_voxel_intensity_oracle=False,
        constant_and_linear_checked_all_target_voxels=True,patch_support_plans=76,same_geometry_input_pairs=38,
        direct_corner_outside_FOV_witnesses=60,conservative_support_boxes_fitting_full_FOV=0,
        new_medical_arrays_loaded=0,new_GT_arrays_loaded=0,new_model_arrays_loaded=0,new_neural_forwards=0,new_training_updates=0,
        new_patient_medical_effects=0,new_validation_evaluation_executed=False,confirmation_patients_opened=0,lockedIXI_opened=False,
        original_training_session=29823,actual_live_training_observation=live,actual_current_training_exit_observed=False,
        GPU_authorized=True,GPU_latest_totals_actual=unwrap(entries['turn22_gpu_totals_latest']['value']),
        root_environment_and_gitignore_unchanged=True,root_file_bindings=[dict(path='../'+k,sha256=v,bytes=(ROOT.parent/k).stat().st_size) for k,v in r0.items()],
        source_bindings=[entry(p) for p in sources],author_implementation_executed=False,publication_claim_confirmed=False,goal_status='active',
        stage_saved_bytes_before_registration=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file()),elapsed_seconds=time.perf_counter()-started)
    dump(HERE/'READING_PROVENANCE.json',result_doc)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    print(json.dumps(dict(complete=True,new_primary_maintexts=2,synthetic_cases=16,development_geometry_plans=76,new_patient_medical_effects=0,
        original_training_still_live=True,stage_saved_bytes_before_registration=result_doc['stage_saved_bytes_before_registration'])),flush=True)
if __name__=='__main__':main()
