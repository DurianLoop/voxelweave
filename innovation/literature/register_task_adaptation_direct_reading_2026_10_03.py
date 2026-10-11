"""Record selected blocks actually read, alternate public representation and failures."""
import hashlib,json,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'literature/source_cache/task_adaptation_direct_fulltexts_2026-10-03'
ANCHORS={
 'tumorsynth_html':list(range(43,58))+[59,61,63,65,67,69,70,71,73,74,75,77,78,80,81,84,86,88,89,91,93,95,96,97,99,101,102,103,104,105,106,107,109,111,113,115,116,117,118,119,122],
 'multiplanar_fibroid':[12,13,15,16,17,21]+list(range(25,29))+[31]+list(range(34,43))+[46]+list(range(49,59))+[61,65,66,67,68,70,73,74,75,76,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94],
 'plaque_highresolution':[5,8,9,11,13,14,17,19,21,22,23,24,25,28,29,31,32,33,35,37,39,41,44,47,49,51,52,55,56,59,62,65,66,67,68,69,70,71,73]
}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');acquired=read(OUT/'attempt_01.json');html=read(OUT/'tumorsynth_html_extraction_attempt_03.json');papers=[]
    for key,ids in ANCHORS.items():
        if key=='tumorsynth_html':m=html;doi='10.1148/rycan.250222';pmcid='PMC13036690';raw='tumorsynth_public_html_attempt_02.response'
        else:m=next(x for x in acquired['papers'] if x['key']==key);doi=m['expected_doi'];pmcid=m['pmcid'];raw=m['raw_file']
        assert m['fulltext_acquired'];blocks=read(OUT/m['block_file']);assert len(ids)==len(set(ids)) and max(ids)<len(blocks)
        papers.append(dict(key=key,doi=doi,pmcid=pmcid,raw_file=raw,raw_sha256=sha(OUT/raw),block_file=m['block_file'],block_sha256=sha(OUT/m['block_file']),text_file=m['text_file'],text_sha256=sha(OUT/m['text_file']),actual_read_block_ids=ids,actual_read_blocks=[dict(index=i,**blocks[i]) for i in ids],actual_focused_primary_reading_completed=True,visual_figures_reviewed=False,author_experiments_independently_reproduced=False,separate_supplement_read=False))
    report=ROOT/'literature/2026-10-03_task_adaptation_direct_fulltext_reading.md'
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),new_primary_bodies_read=3,new_primary_pdfs=0,actual_focused_primary_anchors=sum(len(x['actual_read_block_ids']) for x in papers),papers=papers,report=report.relative_to(ROOT).as_posix(),report_sha256=sha(report),
           source_manifests=[dict(file=x,sha256=sha(OUT/x)) for x in ('attempt_01.json','tumorsynth_public_html_attempt_02.json','tumorsynth_html_extraction_attempt_03.json','fibroid_table_aggregate_audit_attempt_01.json')],
           search_file='literature/source_cache/task_adaptation_direct_search_2026-10-03/attempt_01.json',search_sha256=sha(ROOT/'literature/source_cache/task_adaptation_direct_search_2026-10-03/attempt_01.json'),discovery_title_rows_including_duplicates=27,scientific_confirmation_patients=0,publication_claim_confirmed=False)
    p=OUT/'reading_provenance.json';assert not p.exists();p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in r.items() if k not in ('papers','source_manifests')},ensure_ascii=False))
if __name__=='__main__':main()
