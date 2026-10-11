"""Bind already-observed reading ranges without upgrading unread figures/formulas or unavailable code."""
import sys,json,gzip
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,entry,bind,dump,resource_guard
resource_guard();tools=read(HERE/'ACTUAL_READING_TOOL_SCOPE.json')['tools']
assert len(tools)==14 and all(t['exit_code']==0 and not t['was_output_truncated'] for t in tools)
fetch=read(HERE/'primary_xml_attempt01/receipt.json');papers=[];sources=[Path(__file__),HERE/'ACTUAL_READING_TOOL_SCOPE.json',HERE/'primary_xml_attempt01/receipt.json']
for p in fetch['records']:
    key=p['key'];n=p['blocks'];ranges=sorted((HERE/'reading_ranges_attempt01').glob(key+'_*.json'))
    cursor=0
    for path in ranges:
        v=read(path);assert v['complete'] and v['start']==cursor and v['total_blocks']==n
        assert v['emitted_indices']==list(range(v['start'],v['next_index']))
        cursor=v['next_index'];sources.append(path)
        for b in v['source_bindings']:bind(b)
    assert cursor==n
    for b in p['source_bindings']:sources.append(bind(b))
    papers.append(dict(key=key,title=p['title'],doi=p['doi'],pmcid=p['pmcid'],
        complete_extracted_text_range_actually_read=True,blocks_actually_read=n,tables_text_actually_read=p['tables'],
        display_formulas_available=p['display_formulas'],all_display_formulas_individually_interpreted=False,
        image_based_formula_symbols_missing=(key=='routing'),figure_pixels_read=False,external_supplement_read=False,
        ranges=[entry(path) for path in ranges]))
code=read(HERE/'routing_author_code_attempt01/receipt.json');members=code['saved_text']
assert len(members)==21 and sum(m['lines'] for m in members)==631
for m in members:sources.append(bind(m['source']))
sources.append(HERE/'routing_author_code_attempt01/receipt.json')
record=dict(complete=True,errors=[],new_distinct_primary_maintexts_actually_read=2,blocks_actually_read=330,tables_text_actually_read=22,
    already_completed_reading_inherited_not_repeated_as_new_work=True,papers=papers,
    author_text_files_actually_read=21,author_text_lines_actually_read=631,author_code_executed=False,
    author_code_reproduces_published_experiments_certified=False,active_author_repository_status='public_URL_HTTP404_not_obtained',
    indexed_abstracts_or_bibliographic_searches_counted_as_maintexts=False,figure_pixels_read=False,
    source_bindings=[entry(p) for p in sorted(set(sources))],publication_claim_confirmed=False,goal_status='active')
dump(HERE/'READING_PROVENANCE.json',record)
print(json.dumps({k:v for k,v in record.items() if k not in ['papers','source_bindings']}))
