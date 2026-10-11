"""Register actually inspected primary-body anchors, not a reading automation."""
import hashlib,html,json,re,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'source_cache/resampling_order_fulltexts_2026-10-03'
ANCHORS={
 'vinna':[4,6,9,10,21,26,32,33,34,37,39,44,46,59,63,70,72,74,84,88,91,95,97,101,102,103,128,129,136,137,138,141,143],
 'mri_preprocessing':[12,13,16,18,19,21,23,25,29,32,34,43,47,50,52,56,60,62,63,64,65,66,67,68,69,70,71,72,74],
 'stability_atlas':[1,3,4,8,10,12,14,15,16,18,19,21,26,27,29,31,32,34,35,36,39,41,43,44,48,50],
}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def main():
 sys.stdout.reconfigure(encoding='utf-8');report=ROOT/'2026-10-03_resampling_order_fulltext_reading.md';source=read(OUT/'attempt_01.json');papers=[]
 for record in source['papers']:
  if not record['fulltext_acquired']: raise ValueError('Expected primary body absent')
  blocks=read(OUT/record['block_file']);anchors=[dict(index=i,tag=blocks[i]['tag'],text=blocks[i]['text']) for i in ANCHORS[record['key']]]
  papers.append(dict(key=record['key'],doi=record['expected_doi'],title=record['title'],raw_file=record['raw_file'],raw_sha256=record['raw_sha256'],block_file=record['block_file'],block_sha256=record['block_sha256'],text_file=record['text_file'],text_sha256=record['text_sha256'],actual_relevant_body_reading_completed=True,scope='Focused methods, comparisons, results, source/sample roles and limitations; not every visual figure/supplement',anchors=anchors,training_or_phantom_results_independently_reproduced=False,visual_figures_reviewed=False,supplementary_material_read=False))
 searches=[ROOT/'source_cache/resampling_order_search_2026-10-03/attempt_01.json',ROOT/'source_cache/pchip_order_prior_art_2026-10-03/attempt_01.json'];items=[]
 for search in searches:
  for response in read(search)['responses']:
   items.extend(dict(query=response['key'],search_file=search.relative_to(ROOT).as_posix(),**item) for item in response.get('items',[]))
 def norm(title): return re.sub(r'\s+',' ',html.unescape(title).strip().rstrip('.')).lower()
 unique={norm(i['title']) for i in items}
 result=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),report=report.relative_to(ROOT.parent).as_posix(),report_sha256=sha(report),fetch_manifest_sha256=sha(OUT/'attempt_01.json'),new_primary_bodies_read=3,new_pdfs=0,returned_title_rows=len(items),unique_normalized_titles=len(unique),title_rows=items,search_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in searches],papers=papers,actual_focused_primary_anchors=sum(len(v) for v in ANCHORS.values()),unobtained_fourth_body=dict(path='source_cache/t2_tumor_processing_fulltext_2026-10-03/attempt_01.json',sha256=sha(ROOT/'source_cache/t2_tumor_processing_fulltext_2026-10-03/attempt_01.json'),counted_as_fulltext=False),publication_claim_confirmed=False)
 p=OUT/'reading_provenance.json'
 with p.open('x',encoding='utf-8') as stream: json.dump(result,stream,ensure_ascii=False,indent=2)
 print(json.dumps({k:result[k] for k in ('new_primary_bodies_read','new_pdfs','returned_title_rows','unique_normalized_titles','actual_focused_primary_anchors')}),flush=True)
if __name__=='__main__': main()
