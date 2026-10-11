"""Register exact contiguous primary blocks and complete pinned author source lines."""
import sys,json,gzip,time,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,dump,resource_guard
PRIMARY=[(0,40,'turn35_imputation_front'),(40,80,'turn35_imputation_methods'),(80,113,'turn35_imputation_results'),(113,158,'turn35_imputation_discussion_appendix')]
AUTHOR={'00_README.md':[(0,44,'turn35_author_readme')],'01_citations.bib':[(0,19,'turn35_author_citations')],
    '02_recon.m':[(0,200,'turn35_author_recon_front'),(200,400,'turn35_author_recon_middle'),(400,575,'turn35_author_recon_end')],
    '03_sigmarecon.m':[(0,206,'turn35_author_sigma')],'04_sampleSigmaRecon.m':[(0,70,'turn35_author_sample')]}
def actual(v):
    assert v['status']=='fulfilled';r=v['value'];assert r['exit_code']==0 and 'session_id' not in r and 'Warning: truncated output' not in r['output'];return r
def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resource_guard()
    opath=HERE/'ACTUAL_TOOL_OBSERVATIONS_TURN35_PART01.json.gz'
    with gzip.open(opath,'rt',encoding='utf-8') as f:obs=json.load(f)['observations']
    ext=HERE/'extraction_attempt02/receipt.json';q=read(ext);assert q['complete'] and not q['errors'] and q['blocks']==158
    blocks=read(HERE/'extraction_attempt02/blocks.json');streams=[];end=0
    for start,stop,key in PRIMARY:
        assert start==end;r=actual(obs[key]);expected='\n\n'.join(str(v['index'])+' ['+v['kind']+'] '+v['text'] for v in blocks[start:stop])+'\n'
        assert r['output'].replace('\r\n','\n')==expected,key
        streams.append(dict(start_inclusive=start,stop_exclusive=stop,actual_chunk=r['chunk_id'],actual_exit=0,observation_file=entry(opath)));end=stop
    assert end==len(blocks)==158
    tables=read(HERE/'extraction_attempt02/tables.json');assert len(tables)==25 and all(v['id']=='FD'+str(i) and len(v['rows'])==1 for i,v in enumerate(tables,1))
    assert q['doi']=='10.1109/TMI.2018.2866692' and q['pmcid']=='PMC6393212'
    source=next(v for v in q['source_bindings'] if v['path'].endswith('imputation.html'));assert source['sha256']=='e3c8cddab50b7dc735eebc793ac2fd877b832ff77f9dae4d1d606c1f2725799e';bind(source)
    sel=read(HERE/'PRIMARY_SELECTION_ATTEMPT02.json');assert sel['doi']==q['doi'] and sel['pmcid']==q['pmcid'];bind(sel['source_binding'])
    recovered=obs['turn35_ref_recovered_fetch'];assert recovered['exit_code']==0 and 'session_id' not in recovered and recovered['chunk_id']=='132b9f'
    filespath=HERE/'author_files_attempt01/receipt.json';files=read(filespath);assert files['complete'] and not files['errors'] and len(files['records'])==5
    author=[]
    for item in files['records']:
        p=bind(item['source_binding']);data=p.read_bytes();blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();assert blob==item['git_blob_sha1']
        assert item['pinned_commit']=='92bba2322944b1f84a3dcf7d494fd1b5502e7777';lines=p.read_text(encoding='utf-8').splitlines();end=0;reads=[]
        for start,stop,key in AUTHOR[p.name]:
            assert start==end;r=actual(obs[key]);expected='\n'.join(str(i+1)+' '+lines[i] for i in range(start,stop))+'\n'
            assert r['output'].replace('\r\n','\n')==expected,key
            reads.append(dict(line_start_inclusive=start+1,line_stop_inclusive=stop,actual_chunk=r['chunk_id'],actual_exit=0,observation_file=entry(opath)));end=stop
        assert end==len(lines)==item['line_count']
        author.append(dict(author_path=item['author_path'],pinned_commit=item['pinned_commit'],source_binding=item['source_binding'],git_blob_sha1=blob,
            whole_file_text_read=True,line_count=len(lines),actual_untruncated_read_streams=reads,executed=False))
    assert sum(v['line_count'] for v in author)==914
    refs=[dict(path='../'+name,bytes=(ROOT.parent/name).stat().st_size,sha256=sha(ROOT.parent/name)) for name in ['.gitignore','environment.yml']]
    assert refs[0]['sha256']=='7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524'
    assert refs[1]['sha256']=='dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257'
    result=dict(complete=True,errors=[],new_distinct_primary_maintexts_actually_read=1,title=q['title'],doi=q['doi'],pmcid=q['pmcid'],
        public_version='PMC author manuscript, online2018-08-22; author repository cites final issue2019, final PDF not independently inspected',
        maintext_and_inline_AppendixA_textually_completed=True,complete_read_blocks=[0,158],science_maintext_stop_exclusive=128,inline_AppendixA_blocks=[131,145],
        all25_HTML_formula_layout_tables_text_read=True,result_data_tables=0,formula_MathML_layout_not_numerically_replicated=True,
        figure_captions_text_read=True,figure_pixels_reviewed=False,external_supplements_read=False,final_PDF_read=False,cited_references_papers_not_read=True,
        actual_untruncated_primary_streams=streams,primary_source_binding=source,author_sources=author,
        author_repository_files_actually_read=5,author_source_and_document_lines=914,code_computational_files_actually_read=3,author_code_executed=False,
        pinned_commit_not_asserted_original_paper_release=True,root_license_not_found=True,repository_license_metadata=None,
        medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,training_updates=0,new_patient_medical_effects=0,
        confirmation_patients_opened=False,lockedIXI_opened=False,dependencies_installed=False,agents_delegated=False,other_PID_enumerated_or_modified=False,
        publication_claim_confirmed=False,goal_status='active',root_file_bindings=refs,elapsed_seconds=time.perf_counter()-started,resources=resource_guard(),
        source_bindings=[entry(p) for p in [Path(__file__),opath,ext,HERE/'extraction_attempt02/blocks.json',HERE/'extraction_attempt02/tables.json',
            filespath,HERE/'author_tree_attempt01/receipt.json',HERE/'PRIMARY_AND_AUTHOR_EVIDENCE.md',HERE/'NEXT_TRIAL_PREPARATION.md',
            HERE/'PROTOCOL.md',HERE/'AUTHOR_IMPLEMENTATION_PROTOCOL.md',HERE/'NETWORK_RECOVERY_PROTOCOL.md',HERE/'LOCAL_REFERENCE_BINDING_RECOVERY.md',
            HERE/'DIRECT_HTTPS_BUILD_RECEIPT.json',HERE/'REFERENCE_BINDING_BUILD_RECEIPT.json',HERE/'PRIMARY_SELECTION_ATTEMPT02.json']])
    dump(HERE/'READING_PROVENANCE.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ['source_bindings','author_sources','root_file_bindings','actual_untruncated_primary_streams']},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
