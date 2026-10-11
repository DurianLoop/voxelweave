"""Freeze exact inherited-and-completed reading scope, never alter transport receipts."""
import sys,json,gzip,xml.etree.ElementTree as ET,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,entry,bind,dump,resource_guard
resource_guard();out=HERE/'gin_reading_provenance_attempt01';out.mkdir(exist_ok=False)
hp=HERE/'gin_primary_html_attempt02/receipt.json';html=read(hp);assert html['complete']
for b in html['primary_sources']+html['source_bindings']:bind(b)
blocks=json.loads(gzip.decompress((HERE/'gin_primary_html_attempt02/blocks.json.gz').read_bytes()))
assert len(blocks)==105 and blocks[104]['text']=='References'
ranges=[]
for lo,hi,tool in [(0,30,'324bde'),(30,49,'95f321'),(49,74,'321082'),(74,87,'14ecf6'),(87,104,'9411b1')]:
 p=HERE/f'gin_reading_ranges_attempt01/range_{lo:03}_{hi:03}.json';v=read(p)
 assert v['range_start']==lo and v['range_end_exclusive']==hi and v['blocks_printed']==hi-lo
 ranges.append(dict(start=lo,end_exclusive=hi,actual_tool_chunk_id=tool,scope_record=entry(p),
  inspected_in_inherited_turn=True,inherited_output_reported_untruncated=True))
cp=HERE/'gin_selected_author_code_attempt01/receipt.json';code=read(cp);assert code['complete']
records=[]
for v in code['records']:
 p=bind(v['saved']);data=p.read_bytes();lines=len(data.decode().splitlines())
 assert lines==v['lines'] and hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==v['git_blob_sha1_verified']
 records.append(dict(path_in_repository=v['path_in_repository'],saved=entry(p),unique_read_lines=lines,
  complete_static_source_read=True,author_source_executed=False))
assert sum(v['unique_read_lines'] for v in records)==1489
api=HERE/'gin_author_locator_attempt01/arxiv.gz';root=ET.fromstring(gzip.decompress(api.read_bytes()))
comments=[e.text for e in root.iter() if e.tag.rsplit('}',1)[-1]=='comment'];assert len(comments)==1
assert 'early' in comments[0].lower() and 'revised' in comments[0].lower()
r=dict(complete=True,errors=[],reading_kind='inherited_visible_primary_reading_with_actual_missing_code_ranges_completed',
 version='2111.12525v5',new_distinct_primary_maintexts_read=1,unique_maintext_blocks_actually_read=104,
 maintext_ranges=ranges,algorithm1_actually_read=True,algorithm1_actual_tool_chunk_id='b6d2a9',
 unique_experimental_tables_actually_read=4,HTML_table_element_count_not_paper_table_count=13,
 math_node_count_not_unique_equations_read=207,arxiv_comment_exact=comments[0],
 early_version_not_peer_reviewed_final=True,final_journal_maintext_read=False,figure_pixels_read=False,
 external_supplement_read=False,reference_list_read=False,
 fixed_author_commit=code['commit_sha'],source_reading=records,unique_author_source_lines_actually_read=1489,
 adv_bias_missing187_lines_read_current_tool_chunk_id='fa3b4c',
 prior_six_complete_source_reading_chunks=['05a56a','80d0cd','e077d3','019837'],
 prior_adv_bias180_line_chunk='d8697a',author_code_executed=False,old_primary_papers_recounted=False,
 source_bindings=[entry(p) for p in [Path(__file__),HERE/'GIN_READING_AND_PROJECT_DECISION.md',hp,cp,api,HERE/'read_gin_auxiliary.py']])
dump(out/'receipt.json',r);print(json.dumps({k:r[k] for k in ['complete','version','new_distinct_primary_maintexts_read','unique_maintext_blocks_actually_read','unique_experimental_tables_actually_read','unique_author_source_lines_actually_read','arxiv_comment_exact']},ensure_ascii=False))
