"""Verify contiguous actual read streams byte-normalized against every maintext block."""
import sys,json,gzip,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,dump,resource_guard
RANGES={'psacnn':[(0,32,'turn33_psacnn_front'),(32,71,'turn33_psacnn_methods1'),(71,99,'turn33_psacnn_methods2'),
    (99,142,'turn33_psacnn_results1'),(142,177,'turn33_psacnn_results2'),(177,191,'turn33_psacnn_end')],
    'jointsr':[(0,42,'turn33_jointsr_front'),(42,79,'turn33_jointsr_methods1'),(79,112,'turn33_jointsr_methods2'),
    (112,135,'turn33_jointsr_results1'),(135,164,'turn33_jointsr_results_discussion'),(164,184,'turn33_jointsr_end')]}
def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resource_guard()
    observation=HERE/'ACTUAL_TOOL_OBSERVATIONS_TURN33.json.gz'
    with gzip.open(observation,'rt',encoding='utf-8') as f:obs=json.load(f)['observations']
    ext=HERE/'extraction_attempt02/receipt.json';q=read(ext);assert q['complete'] and not q['errors']
    audit=read(HERE/'table_audit_attempt01/receipt.json');assert audit['complete'] and not audit['errors'] and audit['all39_direct_HTML_tables_exact_cell_match']
    with gzip.open(HERE/'ACTUAL_TOOL_OBSERVATIONS_TURN34_PART01.json.gz','rt',encoding='utf-8') as f:current=json.load(f)['observations']
    actual=current['turn34_table_audit'];assert actual['exit_code']==0 and 'session_id' not in actual and actual['chunk_id']=='066bf8'
    actual_probe=current['turn34_after_probe_0']['value'];assert actual_probe['exit_code']==0 and 'session_id' not in actual_probe and actual_probe['chunk_id']=='c2b9cb'
    papers=[]
    for article in q['records']:
        key=article['key'];path=HERE/('extraction_attempt02/'+key+'_blocks.json');blocks=read(path);expected=0;streams=[]
        for start,stop,k in RANGES[key]:
            assert start==expected;v=obs[k];assert v['status']=='fulfilled';r=v['value']
            assert r['exit_code']==0 and 'session_id' not in r and 'Warning: truncated output' not in r['output']
            text='\n\n'.join(str(x['index'])+' ['+x['kind']+'] '+x['text'] for x in blocks[start:stop])
            assert r['output'].replace('\r\n','\n')==text+'\n',k
            streams.append(dict(block_start_inclusive=start,block_stop_exclusive=stop,store_key=k,actual_chunk_id=r['chunk_id'],
                actual_exit_code=0,observation_file=entry(observation)));expected=stop
        assert expected==len(blocks)==article['blocks'];bind(article['source_binding'])
        tablecounts=audit['tables'][key]
        papers.append(dict(key=key,doi=article['doi'],pmcid=article['pmcid'],title=article['title'],
            public_version='PMC accepted manuscript; page-end unedited-manuscript notice, final PDF not checked' if key=='psacnn' else 'PMC journal HTML, final PDF not checked',
            maintext_textually_completed=True,complete_read_block_range=[0,len(blocks)],science_maintext_stop_exclusive=186 if key=='psacnn' else 163,
            all_embedded_HTML_table_nodes_read=article['tables'],table_counts=tablecounts,
            formulas_and_figure_captions_text_read=True,MathML_layout_not_faithfully_reproduced_from_flat_text=True,figure_pixels_reviewed=False,
            external_supplements_read=False,references_cited_papers_not_read=True,author_code_read_or_executed=False,
            source_binding=article['source_binding'],extracted_blocks=entry(path),extracted_tables=entry(HERE/('extraction_attempt02/'+key+'_tables.json')),
            actual_untruncated_reading_streams=streams))
    terminal=read(HERE/'ACTUAL_MEASUREMENT_TERMINAL_TOOL.json');assert terminal==actual_probe
    m=read(HERE/'measurement_contract_attempt01/receipt.json');assert m['complete'] and not m['errors'] and m['all1080_piecewise_cases_completed'] and m['all384_sphere_groups_completed']
    for b in m['source_bindings']:bind(b)
    cases=read(HERE/'measurement_contract_attempt01/cases.json');assert len(cases['piecewise_cases'])==1080 and len(cases['sphere_groups'])==384
    tuples={(r[0],r[1],r[2],r[3]) for r in cases['piecewise_cases']};assert len(tuples)==1080
    assert sum(v['box_residual_positive'] for v in m['summary_by_thickness'])==810
    assert sum(v['projected_outside_0_1_cases'] for v in m['summary_by_thickness'])==809
    roots=[dict(path='../'+name,bytes=(ROOT.parent/name).stat().st_size,sha256=sha(ROOT.parent/name)) for name in ['.gitignore','environment.yml']]
    assert roots[0]['sha256']=='7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524'
    assert roots[1]['sha256']=='dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257'
    result=dict(complete=True,errors=[],new_distinct_primary_maintexts_actually_read=2,papers=papers,
        all39_HTML_nodes_independently_audited=True,formula_table_nodes=31,nonformula_tables=8,result_tables=7,hyperparameter_tables=1,
        original_table_audit_actual_chunk='066bf8',nonmedical_measurement_probe_actual_chunk='c2b9cb',
        piecewise_cases=1080,sphere_groups=384,thick_layer_point_preservation_with_positive_box_residual=810,
        measurement_projection_range_violations=809,medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,
        training_updates=0,new_patient_medical_effects=0,confirmation_patients_opened=False,lockedIXI_opened=False,
        original_CPU_training_not_moved=True,GPU_authorized=True,new_GPU_start_reserve_MiB=8192,
        dependencies_installed=False,agents_delegated=False,other_processes_enumerated_or_modified=False,
        publication_claim_confirmed=False,goal_status='active',root_file_bindings=roots,resources=resource_guard(),elapsed_seconds=time.perf_counter()-started,
        source_bindings=[entry(p) for p in [Path(__file__),observation,HERE/'ACTUAL_TOOL_OBSERVATIONS_TURN34_PART01.json.gz',ext,HERE/'table_audit_attempt01/receipt.json',
            HERE/'ACTUAL_MEASUREMENT_TERMINAL_TOOL.json',HERE/'measurement_contract_attempt01/receipt.json',HERE/'measurement_contract_attempt01/cases.json',
            HERE/'run_measurement_contract_handle_recovery.py',HERE/'MEASUREMENT_LOCAL_RECOVERY.md',HERE/'ACTUAL_MEASUREMENT_PREFLIGHT_FAILED_TOOL.json',
            HERE/'PROTOCOL.md',HERE/'PRIMARY_READING_AND_PROJECT_DECISIONS.md',HERE/'NEXT_TRIAL_PREPARATION.md']])
    dump(HERE/'READING_PROVENANCE.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ['papers','source_bindings','root_file_bindings']},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
