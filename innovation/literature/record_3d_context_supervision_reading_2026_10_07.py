"""Read-provenance append after actual 274-block original text reading."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib
import json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/3d_context_supervision_2026-10-07'
r=dict(created_utc=datetime.now(timezone.utc).isoformat(),actual_text_reading_completed=True,
       images_visually_inspected=False,authors_code_read=False,authors_experiments_reproduced=False,
       publication_claim_confirmed=False,scientific_confirmation_patients=0,papers=[])
for name,count in (('3d_unet_sparse_annotation',53),('deepmedic_multiscale',221)):
    path=OUT/(name+'_blocks.json');blocks=json.loads(path.read_text(encoding='utf-8'))
    assert len(blocks)==count and [b['index'] for b in blocks]==list(range(count))
    r['papers'].append(dict(name=name,block_file=path.name,block_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),actual_read_indices=list(range(count))))
note=ROOT/'literature/2026-10-07_3d_context_supervision_fulltext_reading.md'
r['reading_note_file']=note.relative_to(ROOT).as_posix();r['reading_note_sha256']=hashlib.sha256(note.read_bytes()).hexdigest()
with (OUT/'reading_provenance_2026_10_07.json').open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(dict(papers=2,extracted_blocks_read=274,scientific_confirmation_patients=0)))
