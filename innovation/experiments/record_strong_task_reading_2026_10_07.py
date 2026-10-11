"""Append-only reading provenance; never revises historical retrieval reading flags."""
from pathlib import Path
import json
import hashlib
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/strong_task_baseline_2026-10-07'
record=dict(created_utc=datetime.now(timezone.utc).isoformat(),actual_text_reading_completed=True,
            source_images_visually_inspected=False,authors_experiments_reproduced=False,
            publication_claim_confirmed=False,scientific_confirmation_patients=0,
            commentary='All extracted original article text, main and appendix table text, captions and references read. No independent supplemental files or author code read.',papers=[])
for name,last in (('nnunet_original',80),('nnunet_revisited',75)):
    p=OUT/(name+'_blocks.json');blocks=json.loads(p.read_text(encoding='utf-8'))
    assert len(blocks)==last+1 and [b['index'] for b in blocks]==list(range(last+1))
    record['papers'].append(dict(name=name,block_file=p.name,block_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),actual_read_indices=list(range(last+1))))
note=ROOT/'literature/2026-10-07_strong_task_baseline_fulltext_reading.md'
record['reading_note_file']=note.relative_to(ROOT).as_posix();record['reading_note_sha256']=hashlib.sha256(note.read_bytes()).hexdigest()
with (OUT/'reading_provenance_2026_10_07.json').open('x',encoding='utf-8') as f:json.dump(record,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(dict(papers=2,extracted_blocks_read=157,confirmation_patients=0)))
