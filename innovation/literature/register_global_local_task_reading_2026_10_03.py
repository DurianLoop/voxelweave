"""Register two completed primary body readings and a separately counted old-paper reread."""
import hashlib
import json
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/global_local_task_fulltexts_2026-10-03'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    path=OUT/'reading_provenance.json'
    assert not path.exists()
    acquisition=read(OUT/'attempt_01.json')
    papers=[]
    for source in acquisition['papers']:
        blocks=read(OUT/source['block_file'])
        assert len(blocks)=={'vs_cascade':50,'olfactory':122}[source['key']]
        record={k:source[k] for k in ('key','pmcid','title','expected_doi','url',
            'raw_file','raw_sha256','block_file','block_sha256','text_file','text_sha256')}
        for prefix in ('raw','block','text'):
            assert sha(OUT/record[prefix+'_file'])==record[prefix+'_sha256']
        record.update(actual_read_block_ids=list(range(len(blocks))),
            actual_read_blocks=[dict(index=i,**b) for i,b in enumerate(blocks)],
            actual_primary_body_text_reading_completed=True,author_experiments_independently_reproduced=False,
            visual_figures_reviewed=False,separate_supplement_read=False,new_primary_body=True)
        papers.append(record)
    old=ROOT/'literature/source_cache/cobrai_crossmoda_public_2026-10-02/kujawa_jats_attempt_01_paragraphs.json'
    oldblocks=read(old)
    ids=list(range(39,51))+list(range(64,70))+[74]
    report=ROOT/'literature/2026-10-03_global_local_task_fulltext_reading.md'
    record=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),
        new_primary_bodies_read=2,new_primary_pdfs=0,actual_new_body_text_blocks=172,
        note='Blocks include titles, table texts and captions; not independent observations.',
        papers=papers,acquisition_sha256=sha(OUT/'attempt_01.json'),
        report=report.relative_to(ROOT).as_posix(),report_sha256=sha(report),
        rereading=dict(doi='10.3389/fncom.2024.1365727',new_primary_body=False,
            source_file=old.relative_to(ROOT).as_posix(),source_sha256=sha(old),
            actual_read_block_ids=ids,actual_read_blocks=[dict(index=i,**oldblocks[i]) for i in ids]),
        scientific_confirmation_patients=0,publication_claim_confirmed=False)
    assert sum(len(x['actual_read_block_ids']) for x in papers)==172 and len(ids)==19
    path.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(new_primary_bodies_read=2,new_body_text_blocks=172,old_reread_blocks=19)))


if __name__=='__main__':
    main()
