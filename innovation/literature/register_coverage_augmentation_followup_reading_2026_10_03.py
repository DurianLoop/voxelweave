"""Register completed cumulative JATS reading, keeping original acquisition unchanged."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'literature/source_cache/coverage_augmentation_fulltexts_2026-10-03'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    path = OUT / 'reading_provenance.json'
    assert not path.exists()
    acquisition = OUT / 'attempt_01.json'
    sources = json.loads(acquisition.read_text(encoding='utf-8'))
    report = ROOT / 'literature/2026-10-03_coverage_augmentation_followup_fulltext_reading.md'
    papers = []
    for source, count, inherited_count in zip(sources['papers'], (98, 107), (49, 54)):
        for prefix in ('raw', 'block', 'text'):
            assert sha(OUT / source[prefix + '_file']) == source[prefix + '_sha256']
        blocks = json.loads((OUT / source['block_file']).read_text(encoding='utf-8'))
        assert len(blocks) == count and source['fulltext_acquired']
        papers.append(dict(**source, actual_primary_body_text_reading_completed=True,
            cumulative_actual_read_block_ids=list(range(count)),
            inherited_read_block_ids=list(range(inherited_count)),
            continuation_completed_block_ids=list(range(inherited_count, count)),
            inherited_reading_source='User-provided continuation summary; actual block ranges stated there.',
            actual_read_blocks=[dict(index=i, **block) for i, block in enumerate(blocks)],
            visual_figures_reviewed=False, separate_supplement_read=False,
            author_experiments_independently_reproduced=False))
    result = dict(created_utc=datetime.now(timezone.utc).isoformat(), script_sha256=sha(__file__),
        acquisition_sha256=sha(acquisition), report=report.relative_to(ROOT).as_posix(),
        report_sha256=sha(report), papers=papers, cumulative_new_primary_bodies_read=2,
        cumulative_body_text_blocks=205, inherited_body_text_blocks=103,
        remaining_body_text_blocks_completed_this_continuation=102, primary_pdfs_read=0,
        scientific_confirmation_patients=0, publication_claim_confirmed=False)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(cumulative_primary_bodies_read=2, cumulative_blocks=205, remaining_completed=102)))


if __name__ == '__main__':
    main()
