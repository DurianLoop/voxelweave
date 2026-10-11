"""Register actually inspected primary text anchors; acquisition records stay immutable."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'literature/source_cache/sparse_task_joint_fulltexts_2026-10-03'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    path=OUT/'reading_provenance.json';assert not path.exists();source=read(OUT/'attempt_01.json');papers=[]
    for row in source['papers']+[dict(read(OUT/'lge_sr_public_html_attempt_02.json'),key='lge_sr_html')]:
        blocks=read(OUT/row['block_file']);key=row['key']
        ids=list(range(len(blocks))) if key!='lge_sr_html' else [9,11,13,15]+[i for i in range(17,101) if blocks[i]['text'].strip()]
        assert len(ids)=={'joint_scar':39,'soft_spinal':160,'drips':113,'lge_sr_html':81}[key]
        q={k:row[k] for k in ('key','pmcid','raw_file','raw_sha256','block_file','block_sha256','text_file','text_sha256')};q['doi']=row.get('doi',row.get('expected_doi'))
        for prefix in ('raw','block','text'):assert sha(OUT/q[prefix+'_file'])==q[prefix+'_sha256']
        q.update(actual_read_block_ids=ids,actual_read_blocks=[dict(index=i,**blocks[i]) for i in ids],actual_focused_primary_reading_completed=True,author_experiments_independently_reproduced=False,visual_figures_reviewed=False,separate_supplement_read=False,is_preprint=key=='drips',kind='primary research',correction='Two segmentation tasks, not SR plus segmentation' if key=='joint_scar' else None);papers.append(q)
    report=ROOT/'literature/2026-10-03_sparse_task_joint_fulltext_reading.md';search=ROOT/'literature/source_cache/sparse_task_joint_search_2026-10-03/attempt_01.json'
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),new_primary_bodies_read=4,new_primary_pdfs=0,actual_focused_primary_anchors=sum(len(x['actual_read_block_ids']) for x in papers),papers=papers,report=report.relative_to(ROOT).as_posix(),report_sha256=sha(report),search_file=search.relative_to(ROOT).as_posix(),search_sha256=sha(search),source_manifests=[dict(file=x,sha256=sha(OUT/x)) for x in ('attempt_01.json','lge_sr_extra_attempt_01.json','lge_sr_public_html_attempt_02.json')],scientific_confirmation_patients=0,publication_claim_confirmed=False)
    assert r['actual_focused_primary_anchors']==393;path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:r[k] for k in ('new_primary_bodies_read','new_primary_pdfs','actual_focused_primary_anchors')},ensure_ascii=False))
if __name__=='__main__':main()
