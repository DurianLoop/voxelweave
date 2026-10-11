"""Bind inspected original blocks, actual returned chunks, appendix and omitted algorithm."""
import re,json,gzip,time
from pathlib import Path
from resource_guard_v1 import HERE,ROOT,guard,entry,bind,read,dump
started=time.perf_counter();before=guard(started)
prep=ROOT/'six_resolution_training_preparation_2026_10_09'
files=[prep/'ACTUAL_AVAILABLE_TOOL_RETURNS_ROUND50_PART1.json',HERE/'ACTUAL_AVAILABLE_TOOL_RETURNS_ROUND50_PART2.json']
buffers={}
for p in files:buffers.update(read(p)['available'])
specs={
 'active_fewshot':[(0,35,'round50_read_fewshot_0_35','c08feb'),(35,59,'round50_read_fewshot_35_59','96b523')],
 'openmasc':[(0,45,'round50_read_openmasc_0_45','4903d0'),(45,84,'round50_read_openmasc_45_84','3400a1'),(84,120,'round50_read_openmasc_84_120','a6078f')],
 'greedy':[(0,38,'round50_read_greedy_0_38','488d6f'),(38,74,'round50_read_greedy_38_74','d8940c'),(74,108,'round50_read_greedy_74_108','3e501d'),(108,143,'round50_read_greedy_108_143','725110'),(143,178,'round50_read_greedy_143_178','6a7181')]}
records=[]
for name,ranges in specs.items():
 p=HERE/'primary_html_attempt01'/name/'blocks.json.gz';blocks=json.loads(gzip.decompress(p.read_bytes()));cursor=0;rows=[]
 for lo,hi,key,chunk in ranges:
  assert lo==cursor;cursor=hi;v=buffers[key];v=v.get('value',v);assert v['exit_code']==0 and 'session_id' not in v and v['chunk_id']==chunk
  exposed=[int(x) for x in re.findall(r'\['+name+r':(\d+):',v['output'])];assert exposed==list(range(lo,hi))
  for block in blocks[lo:hi]:assert block['text'] in v['output']
  rp=HERE/'range_display_attempt01'/f'{name}_{lo:03d}_{hi:03d}.json';q=read(rp);bind(q['source']);assert not q['text_actually_read']
  rows.append(dict(start=lo,end_exclusive=hi,actual_chunk_id=chunk,actual_exit=0,tool_buffer_key=key,exposure_receipt=entry(rp),actual_text_read=True))
 assert cursor==len(blocks)
 records.append(dict(name=name,blocks=len(blocks),source=entry(p),ranges=rows,maintext_and_available_appendix_text_actually_read=True,
  all_table_and_formula_text_in_blocks_read=True,figure_captions_actually_read=True,figure_pixels_actually_inspected=False,
  bibliography_items_actually_read=False,author_code_actually_read=False,external_supplement_read=False,
  note='Maintext/available appendix text means extracted blocks plus explicitly exposed omitted algorithm; does not certify all raw HTML constructs/figure pixels/bibliography'))
alg=buffers['round50_read_greedy_algorithm'];assert alg['exit_code']==0 and 'session_id' not in alg and alg['chunk_id']=='0c53ec'
ar=read(HERE/'algorithm_exposure_attempt01/receipt.json');assert len(ar['lines'])==37
for row in ar['lines']:assert row['id']+' '+row['text'] in alg['output']
fetch=read(HERE/'primary_html_attempt01/receipt.json');assert fetch['complete'] and not fetch['errors']
for row in fetch['records']:
 for b in row['source_files']:bind(b)
out=HERE/'reading_provenance_attempt01';out.mkdir(exist_ok=False)
r=dict(complete=True,errors=[],new_distinct_primary_text_papers_read=3,records=records,
 fixed_versions=['2010.16262v2','2609.32343v1','2607.22371v1'],
 OpenMASC_is_followup_of_previously_read_MASC_not_independent_replication=True,
 greedy_omitted_Algorithm1_lines_actually_read=37,greedy_algorithm_actual_chunk_id='0c53ec',
 graph_pixels_read_count=0,bibliography_items_read_count=0,PDFs_read_count=0,author_code_executed=False,
 source_bindings=[entry(Path(__file__)),entry(HERE/'resource_guard_v1.py'),entry(HERE/'primary_html_attempt01/receipt.json'),entry(HERE/'algorithm_exposure_attempt01/receipt.json')]+[entry(p) for p in files],
 previous_duplicate_MASC_fairness_TADT_not_recounted=True,confirmation_patients_opened=False,lockedIXI_opened=False,
 publication_claim_confirmed=False,goal_status='active',resources_before=before,resources_after=guard(started),elapsed_seconds=time.perf_counter()-started)
dump(out/'receipt.json',r);print(json.dumps({k:r[k] for k in ('complete','new_distinct_primary_text_papers_read','fixed_versions','greedy_omitted_Algorithm1_lines_actually_read','graph_pixels_read_count','bibliography_items_read_count')}))
