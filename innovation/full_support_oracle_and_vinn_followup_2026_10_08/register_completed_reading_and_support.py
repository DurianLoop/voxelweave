"""Register actual complete reading streams and CPU qualifications; no clinical claim."""
import sys,json,time
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,dump,resource_guard
def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resource_guard()
    observation_files=sorted(HERE.glob('ACTUAL_TOOL_OBSERVATIONS_PART*.json'))
    observations={}
    for p in observation_files:
        for x in read(p)['entries']:
            assert x['available'];v=x['actual_tool_result']
            observations[x['store_key']]=dict(actual=v['value'] if v.get('status')=='fulfilled' else v,file=p)
    def actual(key,chunk,exit_code=None,live=False):
        x=observations[key];a=x['actual'];assert a['chunk_id']==chunk
        if exit_code is not None:assert a['exit_code']==exit_code and 'session_id' not in a
        if live:assert a['session_id']==29823 and 'exit_code' not in a
        return dict(store_key=key,actual_chunk_id=chunk,actual_exit_code=a.get('exit_code'),actual_session_id=a.get('session_id'),observation_file=entry(x['file']))
    vinn=[('turn24_vinn_front_complete','1d3b7e',0,24),('turn24_smallread_1','221d8f',24,41),
        ('turn24_methods_1','58e8e0',41,77),('turn24_setup_1','75a355',77,105),('turn24_core_1','a3d82f',105,134),
        ('turn24_padding_and_discussion_1','a883ec',134,161),('turn24_vinn_appendix_header_0','209ccb',161,180),
        ('turn24_vinn_tables_source_0','0a2115',180,202),('turn24_vinn_result_tables1','60c0d0',202,221),
        ('turn24_vinn_final_and_lesion_first_0','410e6e',221,249)]
    lesion=[('turn24_vinn_final_and_lesion_first_1','0e33d3',0,32),('turn24_lesion_methods_and_results_0','629fa2',32,59),
        ('turn24_lesion_results_complete','086e31',59,80)]
    papers=[]
    for key,spans,end,doi,pmc,n in [('vinn',vinn,249,'10.1016/j.neuroimage.2022.118933','PMC9801435',16),
            ('lesion_ensemble',lesion,80,'10.1007/978-3-032-16365-3_41','PMC13148016',3)]:
        coverage=[];readings=[]
        for obs,chunk,lo,hi in spans:
            a=observations[obs]['actual'];assert a['exit_code']==0 and 'Warning: truncated' not in a['output']
            assert 'UnicodeEncodeError' not in a['output']
            coverage.extend(range(lo,hi));readings.append(dict(block_start_inclusive=lo,block_stop_exclusive=hi,**actual(obs,chunk,0)))
        assert coverage==list(range(end))
        if key=='vinn':src=HERE/'author_sources_attempt01/vinn_pmc_html.html';blocks=HERE/'vinn_html_extraction_attempt01/blocks.json';tables=HERE/'vinn_html_extraction_attempt01/tables.json';receipt=HERE/'vinn_html_extraction_attempt01/receipt.json';expected='c3013ac688177b8276e394ad00fe8124deffdb8a78ebbf3c242da41f8bdbbd8b'
        else:src=HERE/'lesion_html_attempt01/source.html';blocks=HERE/'lesion_html_attempt01/blocks.json';tables=HERE/'lesion_html_attempt01/tables.json';receipt=HERE/'lesion_html_attempt01/receipt.json';expected='26784007d15eee45963d1f0a3a4fa4f785ecfaa08ee1f6ea38024e66e0000b1d'
        assert sha(src)==expected;q=read(receipt);assert q['complete'] and not q['errors'] and q['meta']['citation_doi']==doi
        assert len(read(tables))==n+(5 if key=='vinn' else 0)
        papers.append(dict(key=key,doi=doi,pmcid=pmc,title=q.get('title',q['meta']['citation_title']),
            primary_version='PMC author manuscript identified in original HTML header',maintext_textually_completed=True,
            complete_read_block_range=[0,end],references_and_external_cited_papers_not_read=True,
            data_tables_read=n,equation_layout_tables_read=5 if key=='vinn' else 0,
            original_source=entry(src),extracted_blocks=entry(blocks),extracted_tables=entry(tables),extraction_receipt=entry(receipt),
            actual_untruncated_reading_streams=readings,figure_captions_read=True,figure_pixels_reviewed=False,
            external_supplement_read=False,final_edited_PDF_checked=False,author_code_read_or_executed=False))
    full=read(HERE/'full_support_attempt02/receipt.json');label=read(HERE/'development_label_support_attempt01/receipt.json');norm=read(HERE/'normalization_support_attempt01/receipt.json')
    assert all(v['complete'] and not v['errors'] for v in [full,label,norm])
    assert full['distinct_target_voxels_verified']==label['distinct_geometry_target_voxels']==39845888
    assert label['all38_unpadded_domain_fields_independently_verified'] and label['all76_previous_support_mask_hashes_matched']
    assert label['all38_mother_batch_labels_matched'] and label['GT_arrays_loaded']==19
    assert label['aggregates']['crop_only_cache']['foreground']['incomplete_support_voxels']==51803
    assert label['aggregates']['unpadded_resampled_image_domain']['foreground']['incomplete_support_voxels']==0
    assert norm['conv_eroded_max_difference']==0 and norm['instance_norm_eroded_max_difference']>.01
    root=read(ROOT/'resolution_and_lesion_followup_2026_10_08/READING_PROVENANCE.json')['root_file_bindings']
    for b in root:bind(b)
    source_files=[p for p in HERE.rglob('*') if p.is_file() and p.suffix in {'.py','.md','.json','.html'}]
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],new_distinct_primary_maintexts_completed=2,papers=papers,
        systematic_review_claimed=False,author_implementation_executed=False,
        first_full_support_coordinate_attempt=actual('turn23_full_support_start','7011eb',1),
        full_support_V2_actual_terminal=actual('turn23_full_support_v2_poll1','f75c96',0),
        development_label_support_actual_terminal=actual('turn24_label_support_poll2','aeef07',0),
        normalization_probe_actual_terminal=actual('turn24_normalization_probe_actual','820d92',0),
        geometry_target_voxels=39845888,previous_support_fields=76,new_unpadded_domain_fields=38,
        distinct_development_patients=11,development_series=19,GT_arrays_loaded=19,new_medical_MRI_arrays_loaded=0,
        new_checkpoint_arrays_loaded=0,new_patient_neural_forwards=0,new_training_updates=0,new_patient_medical_effects=0,
        new_validation_evaluation_executed=False,confirmation_patients_opened=False,lockedIXI_opened=False,
        actual_current_training_exit_observed=False,latest_live_training_observation=actual('turn24_training_poll3','187bef',live=True),
        current_training_frozen_device='cpu',GPU_authorized=True,
        GPU_totals_actual=actual('turn24_gpu_totals','60c616',0),GPU_free_MiB=1394,original_new_GPU_start_reserve_MiB=8192,
        semantic_correction_previous_fullFOV_means_padded_cache=True,unpadded_resampled_domain_is_not_observed_slice_certificate=True,
        support_mask_does_not_certify_task_output_independence=True,root_file_bindings=root,root_environment_and_gitignore_unchanged=True,
        dependencies_installed=False,agents_delegated=False,publication_claim_confirmed=False,goal_status='active',
        source_bindings=[entry(p) for p in sorted(source_files)],elapsed_seconds=time.perf_counter()-started)
    dump(HERE/'READING_PROVENANCE.json',r)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    print(json.dumps({k:r[k] for k in ['complete','new_distinct_primary_maintexts_completed','GT_arrays_loaded','new_patient_medical_effects','actual_current_training_exit_observed','current_training_frozen_device','publication_claim_confirmed','goal_status']}),flush=True)
if __name__=='__main__':main()
