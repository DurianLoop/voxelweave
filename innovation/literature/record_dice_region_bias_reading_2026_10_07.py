"""Register only the text and metadata actually read, leaving retrieval logs immutable."""
import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/dice_region_bias_fulltext_2026-10-07'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
data=json.loads((OUT/'blocks.json').read_text(encoding='utf-8'));assert len(data)==216
paths=[OUT/'html_v4_attempt01.response',OUT/'blocks.json',OUT/'maintext.txt',
       ROOT/'literature/2026-10-07_dice_region_bias_fulltext_reading.md',
       ROOT/'literature/source_cache/small_target_loss_routes_2026-10-07/author_readme_attempt01.response',
       ROOT/'literature/source_cache/small_target_loss_routes_2026-10-07/arxiv_title_attempt01.response']
row=dict(created_utc=datetime.now(timezone.utc).isoformat(),actual_reading_completed=True,
         arxiv='2104.08717v4',doi='10.1016/j.media.2023.103015',blocks_read=list(range(216)),
         sections_read=['abstract','introduction','related work','formulation','experiments','tables','conclusion','references','appendices A-F'],
         equations_available_as_latex=True,original_figure_pixels_reviewed=False,author_training_reproduced=False,
         full_author_code_audited=False,author_readme_and_arxiv_metadata_read=True,
         sources=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in paths],
         script_sha256=sha(Path(__file__)),scientific_confirmation_patients=0)
with (OUT/'reading_provenance_2026_10_07.json').open('x',encoding='utf-8') as f:json.dump(row,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(dict(actual_reading_completed=True,blocks_read=216)))
