"""Bind actual complete returned reading buffers to saved primary and author sources."""
import sys,json,gzip,hashlib,time
from pathlib import Path
import search_primary_candidates as h
HERE=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def entry(p):return dict(path=p.relative_to(h.ROOT).as_posix(),sha256=h.sha(p),bytes=p.stat().st_size)
def main():
 sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();h.guard();compressed=HERE/'ACTUAL_TOOL_OBSERVATIONS_TURN36_PART01.json.gz'
 with gzip.open(compressed,'rt',encoding='utf-8') as f:obs=json.load(f)['observations']
 src=HERE/'hallucination_primary_attempt01';blocks=read(src/'blocks.json');assert len(blocks)==178;coverage=set();flows=[]
 for key,start,stop in [('turn36_hallucination_front',0,45),('turn36_hallucination_definitions',45,97),('turn36_hallucination_experiments',97,117),('turn36_hallucination_results_conclusion',117,140),('turn36_hallucination_supplement',140,178)]:
  tool=obs[key];assert tool['exit_code']==0 and 'session_id' not in tool and 'Warning: truncated output' not in tool['output'] and 'tokens truncated' not in tool['output']
  view=json.loads(tool['output']);assert view==dict(start=start,stop_exclusive=stop,total=178,blocks=blocks[start:stop]);coverage.update(range(start,stop));flows.append(dict(key=key,chunk_id=tool['chunk_id'],start=start,stop_exclusive=stop,exact_complete_inner_buffer_verified=True))
 assert coverage==set(range(178))
 supplemental=[]
 for key,start,stop in [('turn36_hallucination_middle_recovery',36,65),('turn36_hallucination_definitions_visible',65,97),('turn36_hallucination_dip_visible',157,163)]:
  tool=obs[key];assert tool['exit_code']==0 and 'Warning: truncated output' not in tool['output']
  if key.endswith('_visible'):
   expected='\n'.join('['+str(v['index'])+'] '+v['text'] for v in blocks[start:stop])+'\n';assert tool['output'].replace('\r\n','\n')==expected
  else:assert json.loads(tool['output'])==dict(start=start,stop_exclusive=stop,total=178,blocks=blocks[start:stop])
  supplemental.append(dict(key=key,chunk_id=tool['chunk_id'],start=start,stop_exclusive=stop,exact_visible_recovery_verified=True))
 tables=read(src/'tables.json');assert len(tables)==41;data=[v for v in tables if v['id']=='S5.T1.3'];assert len(data)==1
 assert data[0]['rows']==[['Data distribution','U-Net','PLS-TV','DIP'],['IND','0.84','0.71','0.73'],['OOD','0.75','0.73','0.76']]
 author=HERE/'hallucination_author_files_attempt01';receipt=read(author/'receipt.json');assert receipt['complete'] and not receipt['errors']
 authorflows=[]
 for row,key in zip(receipt['records'],['turn36_author_readme','turn36_author_raw','turn36_author_specific']):
  p=h.ROOT/row['source']['path'];raw=p.read_bytes();assert h.sha(p)==row['source']['sha256'] and len(raw)==row['source']['bytes']
  assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob_sha1']
  lines=p.read_text(encoding='utf-8').splitlines();tool=obs[key];expected='\n'.join(str(i+1)+': '+s for i,s in enumerate(lines))+'\n'
  assert tool['exit_code']==0 and 'Warning: truncated output' not in tool['output'] and tool['output'].replace('\r\n','\n')==expected and len(lines)==row['lines']
  authorflows.append(dict(key=key,chunk_id=tool['chunk_id'],author_path=row['author_path'],lines=len(lines),source_binding=row['source'],git_blob_sha1=row['git_blob_sha1'],exact_all_lines_read_verified=True))
 assert sum(v['lines'] for v in authorflows)==336 and receipt['commit']=='d640d6b8b134572c06cb883b73fbd9694f808c87'
 result=dict(complete=True,errors=[],new_distinct_primary_maintexts_actually_read=1,scientific_and_inline_supplement_blocks=178,maintext_and_inline_supplement_text_coverage_complete=True,bibliography_references_individually_read=False,primary_reading_flows=flows,display_recovery_flows=supplemental,outer_display_truncation_disclosed_and_recovered=True,formula_and_algorithm_table_nodes=40,result_data_tables=1,result_table_all_cells_read=True,author_files_actually_read=3,author_file_lines=336,author_sources=authorflows,author_commit=receipt['commit'],author_implementation_executed=False,figure_pixels_read=False,PDF_read=False,Tanno_fulltext_read=False,maintext_source=entry(src/'maintext.html'),source_bindings=[entry(p) for p in [Path(__file__),HERE/'PROTOCOL.md',HERE/'AUTHOR_HALLUCINATION_PROTOCOL.md',src/'receipt.json',src/'blocks.json',src/'tables.json',compressed,author/'receipt.json']],elapsed_seconds=time.perf_counter()-started,publication_claim_confirmed=False,goal_status='active')
 h.dump(HERE/'READING_PROVENANCE.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ['primary_reading_flows','display_recovery_flows','author_sources','source_bindings']},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
