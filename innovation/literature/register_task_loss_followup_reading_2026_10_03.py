"""Record actually completed 162-block loss primary body reading."""
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/task_loss_followup_fulltext_2026-10-03'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def main():
    path=OUT/'reading_provenance.json';assert not path.exists()
    source=read(OUT/'attempt_01.json')['papers'][0]
    blocks=read(OUT/source['block_file']);assert len(blocks)==162
    report=ROOT/'literature/2026-10-03_task_loss_followup_fulltext_reading.md'
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),
        new_primary_bodies_read=1,new_primary_pdfs=0,actual_new_body_text_blocks=162,
        acquisition_sha256=sha(OUT/'attempt_01.json'),report=report.relative_to(ROOT).as_posix(),
        report_sha256=sha(report),paper=source,actual_read_block_ids=list(range(162)),
        actual_read_blocks=[dict(index=i,**b) for i,b in enumerate(blocks)],
        actual_primary_body_text_reading_completed=True,visual_figures_reviewed=False,
        separate_supplement_read=False,author_experiments_independently_reproduced=False,
        scientific_confirmation_patients=0,publication_claim_confirmed=False)
    for prefix in ('raw','block','text'):assert sha(OUT/source[prefix+'_file'])==source[prefix+'_sha256']
    path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(new_primary_bodies_read=1,new_body_text_blocks=162)))
if __name__=='__main__':main()
