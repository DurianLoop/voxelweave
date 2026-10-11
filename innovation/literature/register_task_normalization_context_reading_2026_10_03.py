"""Bind focused blocks actually read, scope limitations and retrieval failures."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'source_cache/task_normalization_context_fulltexts_2026-10-03'
ANCHORS={
 'multisite_normalization':list(range(25)),
 'segmentation_harmonization':list(range(2,12))+[14,15,16,18,19,20,22,23,24,25,26,28,30,32,34,36,38,39,41,42,44,45,47,48,51,53,54,56,57,59,60,62,64]+list(range(66,82))+list(range(83,90))+list(range(100,105)),
 'feta2024':[2,3,4,5,6,9,10,11,12,13,14,15,18,20,21,26,28,30,32,34,35,36,37,38,39,40,42,44,45,46,47,48,49,50,51,52,54,55,57,58,67,69,71,72,74,76,78,81,82,85,86,90,91,92,96,97,98,100,102,104,105,107,110,111,112,114,115,116,118,120,122,123,126,127,129,130,135,136,138,140,142,143,145,146,147,148,151,153,154,155,157,158,159,160,161,163,164,165]
}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 sys.stdout.reconfigure(encoding='utf-8');fetch=read(OUT/'attempt_01.json');papers=[]
 for p in fetch['papers']:
  assert p['fulltext_acquired'];blocks=read(OUT/p['block_file']);ids=ANCHORS[p['key']];assert len(ids)==len(set(ids))
  papers.append(dict(key=p['key'],doi=p['expected_doi'],pmcid=p['pmcid'],raw=p['raw_file'],raw_sha256=p['raw_sha256'],block=p['block_file'],block_sha256=p['block_sha256'],text=p['text_file'],text_sha256=p['text_sha256'],anchors=[dict(index=i,**blocks[i]) for i in ids],actual_relevant_body_reading_completed=True,author_experiments_independently_reproduced=False,visual_figures_reviewed=False,supplementary_material_read=False))
 report=ROOT/'2026-10-03_task_normalization_context_fulltext_reading.md'
 searches=[ROOT/'source_cache/task_normalization_context_search_2026-10-03/attempt_01.json',ROOT/'source_cache/task_normalization_context_search_2026-10-03/network_fallback_attempt_01.json',ROOT/'source_cache/task_normalization_context_ncbi_2026-10-03/attempt_01.json']
 proof=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),fetch_manifest_sha256=sha(OUT/'attempt_01.json'),report=report.relative_to(ROOT.parent).as_posix(),report_sha256=sha(report),new_primary_bodies_read=3,new_pdfs=0,actual_focused_primary_anchors=sum(len(p['anchors']) for p in papers),papers=papers,searches=[dict(path=x.relative_to(ROOT.parent).as_posix(),sha256=sha(x)) for x in searches],title_rows_from_narrow_ncbi_search=26,failed_europe_pmc_queries=4,publication_claim_confirmed=False)
 path=OUT/'reading_provenance.json';assert not path.exists();path.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in proof.items() if k not in ('papers','searches')},ensure_ascii=False))
if __name__=='__main__':main()
