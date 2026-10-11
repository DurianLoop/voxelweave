"""Freeze completed text and visual reading separately from original download receipts."""
import sys,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,entry,bind,dump,resource_guard
resource_guard();out=HERE/'ssc_reading_provenance_attempt01';out.mkdir(exist_ok=False)
fp=HERE/'ssc_primary_pdf_attempt01/receipt.json';ep=HERE/'ssc_extraction_render_attempt01/receipt.json'
f=read(fp);e=read(ep);assert f['complete'] and not f['errors'] and e['complete'] and not e['errors']
assert len(e['pages'])==e['verified_pages']==8 and f['pdf']['sha256']=='058e96f9d877abeea15a1caeb57a04a0f8ea2189bf71d6b565886cd3eee8367d'
bind(f['pdf']);pages=[]
for n,v in enumerate(e['pages'],1):
    assert n==v['physical_page'];bind(v['text']);bind(v['render'])
    pages.append(dict(physical_page=n,publisher_page=186+n,text=v['text'],render=v['render'],
                      text_actually_read=True,render_actually_inspected=True,render_detail='original',
                      text_actual_tool_chunk_id='5cb1d9' if n<=4 else 'b8c52c',
                      actual_visual_batch_key='round48_ssc_visual_1_4' if n<=4 else 'round48_ssc_visual_5_8'))
r=dict(complete=True,errors=[],title=f['title'],doi=f['doi'],authorString=f['authorString'],
       new_distinct_primary_maintexts_read=1,publisher_maintext_and_reference_pages_read=8,
       primary_pdf=f['pdf'],pages=pages,all_text_read_outputs_untruncated=True,
       numbered_figures_actually_read=4,numbered_equations_actually_read=3,independent_experimental_tables_in_paper=0,
       reference_list_actually_read=True,author_source_code_read=False,author_source_code_executed=False,
       registration_framework_reimplemented=False,external_supplement_read=False,
       maintext_reading_receipt_separate_from_transport=True,transport_and_extraction_receipts_unchanged=True,
       source_bindings=[entry(p) for p in (Path(__file__),fp,ep,HERE/'SSC_PAPER_AND_CONTROL_PREPARATION.md')],
       publication_claim_confirmed=False,goal_status='active')
dump(out/'receipt.json',r)
print(json.dumps({k:r[k] for k in ('complete','new_distinct_primary_maintexts_read','publisher_maintext_and_reference_pages_read',
                                 'numbered_figures_actually_read','numbered_equations_actually_read','author_source_code_executed')}))
