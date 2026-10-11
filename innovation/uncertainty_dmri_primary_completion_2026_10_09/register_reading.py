"""Bind exact retrieved text to whole-block tool observations; never infer reading from acquisition."""
import json,re,sys
from pathlib import Path
from fetch_arxiv_maintext import entry,dump,guard
HERE=Path(__file__).resolve().parent
def main():
 sys.stdout.reconfigure(encoding='utf-8');guard();obs=HERE/'ACTUAL_TOOL_OBSERVATIONS_PART02.json';objects=json.loads(obs.read_text(encoding='utf-8'))
 p=HERE/'arxiv_html_attempt01/blocks.json';blocks=json.loads(p.read_text(encoding='utf-8'));assert len(blocks)==139
 chunks=[];texts=[];truncated=[]
 for i in range(9):
  v=objects['dmri_maintext_read_'+str(i)];assert v['status']=='fulfilled' and v['value']['exit_code']==0 and 'session_id' not in v['value']
  r=v['value'];chunks.append(r['chunk_id']);texts.append(r['output'])
  if 'Warning: truncated output' in r['output']:truncated.append(r['chunk_id'])
 coverage={v['index']:[chunks[i] for i,t in enumerate(texts) if v['text'] in t and ('BLOCK '+str(v['index'])+' ') in t] for v in blocks}
 assert set(coverage)==set(range(139)) and all(coverage.values())
 m=json.loads((HERE/'arxiv_html_attempt01/receipt.json').read_text(encoding='utf-8'));assert m['complete'] and m['fulltexts_actually_read']==0 and m['all_nine_author_surnames_and_order_match']
 tables=json.loads((HERE/'arxiv_html_attempt01/tables.json').read_text(encoding='utf-8'));data=[v for v in tables if v['id'].startswith('S4.T')];equations=[v for v in tables if not v['id'].startswith('S4.T')]
 assert len(data)==3 and len(equations)==14
 constant=json.loads((HERE/'constant_variance_attempt02/receipt.json').read_text(encoding='utf-8'));term=objects['dmri_constant_v2_actual']
 assert constant['complete'] and term['exit_code']==0 and 'session_id' not in term and term['chunk_id']=='fe41d8'
 r=dict(complete=True,errors=[],new_distinct_primary_maintexts_actually_read=1,version='1907.13418v1',manuscript_title=m['manuscript_title'],journal_title=m['journal_title'],journal_DOI=m['journal_DOI'],same_nine_author_surnames_and_order=True,publisher_final_read=False,all139_extracted_blocks_wholly_available_in_retained_tool_returns=True,blocks_actually_read=139,block_coverage=coverage,reading_tool_chunks=chunks,inner_truncation_chunks_preserved=truncated,inner_truncated_8to14_recovered_by='4c1ddc',outer_display_truncated_62to63_recovered_by='1f89e7',data_tables_read=3,training_design_tables=1,result_tables=2,equation_layout_tables=14,figure_pixels_read=False,reference_list_wholly_read=False,external_supplement_read=False,author_code_read=False,author_code_executed=False,conference2017_manuscript_only_indexed=True,version_specific_literal_equation_sanity_actual_exit=0,version_specific_literal_equation_sanity_chunk='fe41d8',source_bindings=[entry(v) for v in [Path(__file__),obs,p,HERE/'arxiv_html_attempt01/maintext.html',HERE/'arxiv_html_attempt01/tables.json',HERE/'arxiv_html_attempt01/receipt.json',HERE/'PRIMARY_FINDINGS_AND_TRIALS.md',HERE/'constant_variance_attempt02/receipt.json']],publication_claim_confirmed=False,goal_status='active')
 dump(HERE/'READING_PROVENANCE.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ['block_coverage','source_bindings']},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
