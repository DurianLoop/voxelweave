"""Preserve inherited reading honestly; verify recoverable chunks and new algorithm."""
import gzip,json,re,time
from pathlib import Path
from resource_guard_v1 import HERE,ROOT,guard,entry,bind,read,dump
start=time.perf_counter();before=guard(start);prep=ROOT/'six_resolution_training_preparation_2026_10_09'
bufferpaths=[HERE/f'ACTUAL_AVAILABLE_TOOL_RETURNS_ROUND51_RECOVERY_PART{i}.json' for i in (1,2,3)]
buffers={}
for p in bufferpaths:buffers.update(read(p)['available'])
records=[];specs=[('swin_pretraining',HERE/'foundation_primary_html_attempt01/swin_pretraining',131,[(0,33,'a7d051'),(33,69,'4b9de1'),(69,94,'c01359'),(94,131,'43eaa4')]),('brainsegfounder',HERE/'brainsegfounder_identity_html_attempt02',109,[(0,36,'a41961'),(36,71,'655ab4'),(71,109,'abbaee')])]
for name,folder,count,ranges in specs:
 p=folder/'blocks.json.gz';blocks=json.loads(gzip.decompress(p.read_bytes()));assert len(blocks)==count;coverage=[]
 for lo,hi,chunk in ranges:
  exposed=HERE/'foundation_range_exposure_attempt01'/f'{name}_{lo:03d}_{hi:03d}.json';v=read(exposed);bind(v['source']);assert not v['text_actually_read']
  matching=[(key,val) for key,val in buffers.items() if isinstance(val,dict) and val.get('chunk_id')==chunk]
  recovered=bool(matching)
  if recovered:
   key,q=matching[0];assert q['exit_code']==0 and 'session_id' not in q and 'truncated output' not in q['output']
   assert all(x['text'] in q['output'] for x in blocks[lo:hi])
  coverage.append(dict(start=lo,end_exclusive=hi,original_chunk_id_reported_by_received_summary=chunk,exposure_receipt=entry(exposed),reading_reported_in_received_summary=True,actual_tool_object_recovered_and_text_verified=recovered,actual_buffer_key=matching[0][0] if recovered else None))
 records.append(dict(name=name,version='2111.14791v2' if name=='swin_pretraining' else '2406.10395v3',source=entry(p),extracted_blocks=count,ranges=coverage,complete_extracted_text_read_reported_by_received_summary=True,all_original_tool_objects_recovered=all(v['actual_tool_object_recovered_and_text_verified'] for v in coverage),figure_pixels_actually_inspected=False,bibliography_items_actually_read=False))
alg=read(HERE/'swin_algorithm_exposure_attempt01/receipt.json');q=buffers['round51_read_swin_algorithm'];assert q['exit_code']==0 and 'session_id' not in q and q['chunk_id']=='169d4f' and len(alg['lines'])==22
for v in alg['lines']:assert v['id']+' '+v['text'] in q['output']
bind(alg['source'])
greedy=read(HERE/'greedy_selected_sources_attempt01/receipt.json');utils=read(HERE/'greedy_policy_utils_fetch_attempt01/receipt.json');assert greedy['complete'] and utils['complete']
for row in greedy['records']:bind(row['saved'])
bind(utils['saved'])
out=HERE/'foundation_reading_scope_attempt01';out.mkdir(exist_ok=False)
r=dict(complete=True,errors=[],records=records,inherited_round51_new_distinct_primary_text_papers_reported_read=2,
 recovered_complete_original_paper_chunk_sets=0,recovered_original_foundation_reading_chunks=2,
 original_unrecoverable_foundation_tool_objects_not_reconstructed=True,Swin_omitted_algorithm_lines_actually_read_and_verified=22,
 Swin_algorithm_actual_chunk_id='169d4f',Greedy_author_commit='d4e4164c5e7d13e57391f8a932ffd81958995dcd',
 Greedy_commit_is_authenticated_publication_time_version=False,Greedy_inherited_policy_utils_read_lines=[1,253],
 Greedy_inherited_train_policy_read_lines=[29,109],Greedy_inherited_data_loading_read_lines=[101,162],
 Greedy_author_code_executed=False,Greedy_all_original_author_reading_buffers_recovered=False,
 current_greedy_MI_notebook_cells1_and2_static_recheck_actual_chunk='3b33a2',current_greedy_key_source_static_recheck_actual_chunk='db6937',
 author_training_or_curves_reproduced=False,downloaded_weights=False,PDFs_read=0,figure_pixels_read=0,bibliography_items_read=0,
 source_bindings=[entry(Path(__file__)),entry(prep/'RECEIVED_USER_SUMMARY_ROUND51.md'),entry(HERE/'swin_algorithm_exposure_attempt01/receipt.json'),entry(HERE/'greedy_selected_sources_attempt01/receipt.json'),entry(HERE/'greedy_policy_utils_fetch_attempt01/receipt.json')]+[entry(p) for p in bufferpaths],
 publication_claim_confirmed=False,goal_status='active',resources_before=before,resources_after=guard(start),elapsed_seconds=time.perf_counter()-start)
dump(out/'receipt.json',r);print(json.dumps({k:r[k] for k in ('complete','inherited_round51_new_distinct_primary_text_papers_reported_read','recovered_complete_original_paper_chunk_sets','recovered_original_foundation_reading_chunks','Swin_omitted_algorithm_lines_actually_read_and_verified')}))
