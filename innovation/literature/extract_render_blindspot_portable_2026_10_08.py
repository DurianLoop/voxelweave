"""Read existing primary PDFs; new text/render attempt, no PDF authoring."""
import hashlib
import json
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08/site_packages'
sys.path.insert(0, str(RUNTIME))
from pypdf import PdfReader
import pypdfium2 as pdfium
BASE = ROOT/'literature/source_cache/blindspot_dependence_primary_2026-10-08'
OUT = BASE/'portable_extraction_render_attempt01'


def entry(p):
    return dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size,
                sha256=hashlib.sha256(p.read_bytes()).hexdigest())


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(exist_ok=False)
    start = time.perf_counter()
    r = dict(created_utc=datetime.now(timezone.utc).isoformat(), complete=False, errors=[],
        source_bindings=[entry(Path(__file__)),
            entry(ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08/installation_attempt03.json')],
        records=[], extraction_is_not_reading=True, rendering_is_not_visual_review=True,
        MRI_arrays_loaded=0, model_arrays_loaded=0, neural_forwards=0, GPU_forwards=0, training_updates=0)
    try:
        for key, pdf, selected, expected in (
            ('noise2void', BASE/'noise2void.pdf', [5,8], 9),
            ('noise2same', BASE/'noise2same_official_attempt02/noise2same_verified.pdf', [2,5,7], 11)):
            reader = PdfReader(pdf)
            assert len(reader.pages) == expected
            pages = []
            for number, page in enumerate(reader.pages, 1):
                path = OUT/(key+f'_page{number:02d}.txt')
                with path.open('x', encoding='utf-8') as f:
                    f.write(page.extract_text() or '')
                pages.append(dict(physical_page=number, text_read=False, **entry(path)))
            renders = []
            doc = pdfium.PdfDocument(str(pdf))
            assert len(doc) == expected
            for number in selected:
                page = doc[number-1]
                bitmap = page.render(scale=1.6)
                picture = bitmap.to_pil()
                path = OUT/(key+f'_page{number:02d}.png')
                picture.save(path)
                renders.append(dict(physical_page=number, visually_reviewed=False,
                    pixels=list(picture.size), scale=1.6, **entry(path)))
                picture.close()
                bitmap.close()
                page.close()
            doc.close()
            r['records'].append(dict(key=key, PDF=entry(pdf), physical_pages=expected,
                page_texts=pages, rendered_pages=renders))
        r['saved_bytes'] = sum(p.stat().st_size for p in OUT.iterdir() if p.is_file())
        assert r['saved_bytes'] < 5_000_000
        r['complete'] = True
    except Exception as exc:
        r['errors'].append(type(exc).__name__+': '+str(exc))
        r['traceback'] = traceback.format_exc()
    r.update(elapsed_seconds=time.perf_counter()-start, finished_utc=datetime.now(timezone.utc).isoformat())
    with (OUT/'extraction_render_attempt01.json').open('x', encoding='utf-8') as f:
        json.dump(r, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(json.dumps({k:r.get(k) for k in ('complete','errors','saved_bytes','elapsed_seconds')}, ensure_ascii=False), flush=True)
    return int(not r['complete'])


if __name__ == '__main__':
    raise SystemExit(main())
