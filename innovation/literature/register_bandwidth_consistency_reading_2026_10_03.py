"""Bind only the actual focused body blocks read in this continuation."""
import hashlib,json,html,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'source_cache/bandwidth_consistency_fulltexts_2026-10-03'
ANCHORS={
 'lazy_resampling':[4,5,24,28,29,34,35,37,38,40,41,42,74,89,91,92,93,94,95,101,102,103,109,110,111,114,116,121,122,123,124,125,127,128,130,131,132,138,141,142,144,145,146,147,150,151,152,153,155],
 'epilepsy_morphometry':[27,28,31,33,38,39,42,43,44,48,51,58,59,60,62,63,66,69,71,73,77,79,84,88,89,91,94,95,98,99,100,107,108,110,111,114,115,116,117,119,120,122,124,126,128],
 'vocal_tract':[4,5,6,10,11,13,14,15,16,17,20,21,28,30,33,35,36,37,38,39,43,44,46,47,49,50,51,52,53,54,55,56,60,61,62,63,64,66,67,81],
}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def main():
 sys.stdout.reconfigure(encoding='utf-8');f=read(OUT/'attempt_01.json');papers=[]
 for row in f['papers']:
  assert row['fulltext_acquired'];bs=read(OUT/row['block_file']);ids=ANCHORS[row['key']];assert len(ids)==len(set(ids));papers.append(dict(key=row['key'],doi=row['expected_doi'],pmcid=row['pmcid'],title=row['title'],raw=row['raw_file'],raw_sha256=row['raw_sha256'],block=row['block_file'],block_sha256=row['block_sha256'],text=row['text_file'],text_sha256=row['text_sha256'],anchors=[dict(index=i,**bs[i]) for i in ids],actual_relevant_body_reading_completed=True,author_experiments_independently_reproduced=False,visual_figures_reviewed=False,supplementary_material_read=False))
 search=ROOT/'source_cache/bandwidth_consistency_search_2026-10-03/attempt_01.json';rows=[x for r in read(search)['responses'] for x in r.get('items',[])];report=ROOT/'2026-10-03_bandwidth_consistency_fulltext_reading.md';p=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),fetch_manifest_sha256=sha(OUT/'attempt_01.json'),search_manifest=search.relative_to(ROOT).as_posix(),search_manifest_sha256=sha(search),report=report.relative_to(ROOT.parent).as_posix(),report_sha256=sha(report),new_primary_bodies_read=3,new_pdfs=0,actual_focused_primary_anchors=sum(len(x['anchors']) for x in papers),returned_title_rows=len(rows),unique_normalized_titles=len(set(' '.join(html.unescape(x['title']).casefold().split()) for x in rows)),papers=papers,new_method_confirmation_patients=0,publication_claim_confirmed=False)
 (OUT/'reading_provenance.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in p.items() if k!='papers'},ensure_ascii=False))
if __name__=='__main__':main()
