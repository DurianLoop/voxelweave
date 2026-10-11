"""Register185 actually displayed primary body/caption/table blocks, original bytes unchanged."""
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/no_augmentation_task_fulltexts_2026-10-03'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    path=OUT/'reading_provenance.json';assert not path.exists()
    acquisition=OUT/'attempt_01.json';sources=json.loads(acquisition.read_text(encoding='utf-8'))
    report=ROOT/'literature/2026-10-03_no_augmentation_task_fulltext_reading.md';papers=[]
    for source,count in zip(sources['papers'],(91,94)):
        assert source['fulltext_acquired'] and source['blocks']==count
        for prefix in ('raw','block','text'):assert sha(OUT/source[prefix+'_file'])==source[prefix+'_sha256']
        blocks=json.loads((OUT/source['block_file']).read_text(encoding='utf-8'));assert len(blocks)==count
        papers.append(dict(**source,actual_primary_body_text_reading_completed=True,
            actual_read_block_ids=list(range(count)),actual_read_blocks=[dict(index=i,**b) for i,b in enumerate(blocks)],
            visual_figures_reviewed=False,separate_supplement_read=False,author_source_code_read=False,
            author_experiments_independently_reproduced=False))
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),
        acquisition_sha256=sha(acquisition),report=report.relative_to(ROOT).as_posix(),report_sha256=sha(report),
        new_primary_bodies_read=2,actual_body_text_blocks=185,primary_pdfs_read=0,papers=papers,
        original_acquisition_reading_flag_preserved=True,scientific_confirmation_patients=0,publication_claim_confirmed=False)
    path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(new_primary_bodies_read=2,actual_body_text_blocks=185)))


if __name__=='__main__':main()
