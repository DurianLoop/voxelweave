"""Bind actual relevant dStripe/STRESS body blocks and search evidence."""
import hashlib,json,html,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'source_cache/phase_direct_neighbour_fulltexts_2026-10-03'
ANCHORS={'dstripe':[11,13,14,15,16,26,27,28,29,31,33,34,38,40,41,42,44,45,46,47,48,51,52,55,58,60,61,63,64,65,68,73,76,79,81,83,84,86,87,89,90,92,94,100,102,103,104,105,106,114,116,120,123,127,129,132,133,135,139,140,142,143,144,145,147,148,149,151,152,153],'stress':[8,11,14,16,18,20,22,24,25,26,28,29,30,31,33,38,39]}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def main():
 sys.stdout.reconfigure(encoding='utf-8');fetch=read(OUT/'attempt_01.json');papers=[]
 for p in fetch['papers']:
  assert p['fulltext_acquired'];bs=read(OUT/p['block_file']);ids=ANCHORS[p['key']];assert len(ids)==len(set(ids));papers.append(dict(key=p['key'],doi=p['expected_doi'],pmcid=p['pmcid'],raw=p['raw_file'],raw_sha256=p['raw_sha256'],block=p['block_file'],block_sha256=p['block_sha256'],text=p['text_file'],text_sha256=p['text_sha256'],anchors=[dict(index=i,**bs[i]) for i in ids],actual_relevant_body_reading_completed=True,author_experiments_independently_reproduced=False,visual_figures_reviewed=False,supplementary_material_read=False))
 search=ROOT/'source_cache/acquired_synthesized_phase_search_2026-10-03/attempt_01.json';rows=[x for r in read(search)['responses'] for x in r.get('items',[])];report=ROOT/'2026-10-03_phase_direct_neighbour_fulltext_reading.md';proof=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),fetch_manifest_sha256=sha(OUT/'attempt_01.json'),search_manifest=search.relative_to(ROOT).as_posix(),search_manifest_sha256=sha(search),report=report.relative_to(ROOT.parent).as_posix(),report_sha256=sha(report),new_primary_bodies_read=2,new_pdfs=0,actual_focused_primary_anchors=sum(len(x['anchors']) for x in papers),returned_title_rows=len(rows),unique_normalized_titles=len(set(' '.join(html.unescape(x['title']).casefold().split()) for x in rows)),papers=papers,preprint_and_journal_versions_not_counted_as_independent_studies=True,publication_claim_confirmed=False)
 (OUT/'reading_provenance.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in proof.items() if k!='papers'},ensure_ascii=False))
if __name__=='__main__':main()
