"""Register only contiguous untruncated actual read streams; no medical confirmation claim."""
import sys,json,gzip,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,entry,bind,dump,resource_guard,sha
RANGES={'synthsr':[(0,26,'turn32_synthsr_front'),(26,55,'turn32_synthsr_results'),(55,79,'turn32_synthsr_methods1'),(79,112,'turn32_synthsr_methods2_end')],
    'vsrad':[(0,23,'turn32_vsrad_front'),(23,43,'turn32_vsrad_results'),(43,71,'turn32_vsrad_end')]}
def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resource_guard()
    observation=HERE/'ACTUAL_TOOL_OBSERVATIONS_TURN32_PART01.json.gz'
    with gzip.open(observation,'rt',encoding='utf-8') as f:obs=json.load(f)['observations']
    extraction=HERE/'xml_extraction_attempt01/receipt.json';q=read(extraction);assert q['complete'] and not q['errors']
    audit=read(HERE/'table_audit_attempt01/receipt.json');assert audit['complete'] and not audit['errors']
    actual=obs['turn32_original_table_audit'];assert actual['exit_code']==0 and 'session_id' not in actual and actual['chunk_id']=='44f97f'
    papers=[]
    for article in q['records']:
        key=article['key'];path=HERE/('xml_extraction_attempt01/'+key+'_blocks.json');blocks=read(path)
        expected=0;streams=[]
        for start,stop,storage_key in RANGES[key]:
            assert start==expected;v=obs[storage_key];assert v['status']=='fulfilled';r=v['value']
            assert r['exit_code']==0 and 'session_id' not in r and 'Warning: truncated output' not in r['output']
            text='\n\n'.join(str(x['index'])+' ['+x['kind']+'] '+x['text'] for x in blocks[start:stop])
            assert r['output'].replace('\r\n','\n')==text+'\n'
            streams.append(dict(block_start_inclusive=start,block_stop_exclusive=stop,store_key=storage_key,
                actual_chunk_id=r['chunk_id'],actual_exit_code=0,observation_file=entry(observation)))
            expected=stop
        assert expected==len(blocks)==article['blocks']
        bind(article['source_binding'])
        papers.append(dict(key=key,doi=article['doi'],pmcid=article['pmcid'],title=article['title'],
            public_version='public journal JATS XML; final PDF not checked',maintext_textually_completed=True,
            complete_read_block_range=[0,len(blocks)],science_maintext_stop_exclusive=92 if key=='synthsr' else 52,
            all_embedded_tables_read=article['tables'],formula_and_figure_captions_read=True,figure_pixels_reviewed=False,
            external_supplements_read=False,references_cited_papers_not_read=True,author_code_read_or_executed=False,
            source_binding=article['source_binding'],extracted_blocks=entry(path),
            extracted_tables=entry(HERE/('xml_extraction_attempt01/'+key+'_tables.json')),actual_untruncated_reading_streams=streams))
    root_bindings=[dict(path='../'+name,bytes=(ROOT.parent/name).stat().st_size,sha256=sha(ROOT.parent/name)) for name in ['.gitignore','environment.yml']]
    assert root_bindings[0]['sha256']=='7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524'
    assert root_bindings[1]['sha256']=='dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257'
    result=dict(complete=True,errors=[],new_distinct_primary_maintexts_actually_read=2,papers=papers,
        independent_table_XML_and_cell_arithmetic_audit_actual_chunk='44f97f',total_original_tables_read=5,
        extraction_not_substituted_for_reading=True,PSACNN_only_index_not_maintext=True,Katayama2026_previously_read_not_counted=True,
        medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,training_updates=0,
        new_patient_medical_effects=0,confirmation_patients_opened=False,lockedIXI_opened=False,
        CPU_training_session=29823,new_full_intensity_replay_session=90446,
        repaired271_terminal_session=47298,repaired271_actual_terminal_chunk='2ce605',repaired271_independent_audit_chunk='b422fd',
        original_CPU_training_not_moved=True,GPU_authorized=True,GPU_free_MiB_at_actual_snapshot=1394,new_GPU_start_reserve_MiB=8192,
        root_file_bindings=root_bindings,dependencies_installed=False,agents_delegated=False,other_processes_enumerated_or_modified=False,
        publication_claim_confirmed=False,goal_status='active',resources=resource_guard(),elapsed_seconds=time.perf_counter()-started,
        source_bindings=[entry(p) for p in [Path(__file__),observation,extraction,HERE/'table_audit_attempt01/receipt.json',
            HERE/'PROTOCOL.md',HERE/'PRIMARY_SELECTION.md',HERE/'PRIMARY_READING_AND_PROJECT_DECISIONS.md',HERE/'NEXT_TRIAL_PREPARATION.md']])
    dump(HERE/'READING_PROVENANCE.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ['source_bindings','papers','root_file_bindings']},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
