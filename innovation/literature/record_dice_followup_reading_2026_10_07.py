import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/dice_followup_fulltexts_2026-10-07'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
record=dict(created_utc=datetime.now(timezone.utc).isoformat(),papers=[],script_sha256=sha(Path(__file__)),
            report_sha256=sha(ROOT/'literature/2026-10-07_generalised_and_soft_dice_fulltext_reading.md'))
for key,n,version in [('generalised_dice',66,'1707.03237v3'),('dice_semimetric',182,'2303.16296v4')]:
    blocks=json.loads((OUT/(key+'_blocks.json')).read_text(encoding='utf-8'));assert len(blocks)==n
    record['papers'].append(dict(name=key,arxiv=version,actual_reading_completed=True,blocks_read=list(range(n)),
        original_figure_pixels_reviewed=False,full_author_code_audited=False,author_training_reproduced=False,
        numerical_table_text_read=key=='dice_semimetric',
        table_limitation='three SVG numerical tables acquired but not visually read' if key=='generalised_dice' else None,
        source_sha256=sha(OUT/(key+'_html_attempt01.response')),block_sha256=sha(OUT/(key+'_blocks.json')),
        text_sha256=sha(OUT/(key+'_maintext.txt'))))
with (OUT/'reading_provenance_2026_10_07.json').open('x',encoding='utf-8') as f:json.dump(record,f,indent=2);f.write('\n')
print(json.dumps(dict(papers_read=2,available_text_blocks_read=248,numerical_table_limitation_preserved=True)))
