"""Extract the existing MoEDiff PDF and render selected pages, without reading claims."""
import hashlib
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / 'primary_attempt01'
PDF = ROOT / 'literature/2025_MoEDiff-SR_Mixture_of_Experts-Guided_Diffusion_Model_for_Region-Adaptive_MRI_SR.pdf'
sys.path.insert(0, str(ROOT / 'seranet_identity_prior_art_2026_10_08'))
import query_seranet_stdlib_v3 as client
import pypdfium2 as pdfium


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    client.base.own_priority()
    client.resource_guard()
    OUT.mkdir(exist_ok=False)
    document = pdfium.PdfDocument(str(PDF))
    pages = len(document)
    bindings = []
    rendered = []
    for index in range(pages):
        client.resource_guard()
        page = document[index]
        textpage = page.get_textpage()
        text = textpage.get_text_range()
        path = OUT / ('page_' + str(index+1).zfill(3) + '.txt')
        with path.open('x', encoding='utf-8', newline='\n') as stream:
            stream.write(text)
        bindings.append(client.base.entry(path))
        textpage.close()
        if index+1 in [1, 4, 6, 7, 8, 9]:
            bitmap = page.render(scale=1.35)
            image = bitmap.to_pil()
            dest = OUT / ('page_' + str(index+1).zfill(3) + '.png')
            image.save(dest, optimize=True)
            rendered.append(dict(page=index+1, **client.base.entry(dest)))
            image.close()
            bitmap.close()
        page.close()
        assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file()) < 6_000_000
    document.close()
    receipt = dict(created_utc=datetime.now(timezone.utc).isoformat(), complete=True, errors=[],
        local_existing_pdf=client.base.entry(PDF), PDF_pages=pages, text_files=bindings,
        rendered_pages=rendered, actual_text_read_pages=[], actual_visual_read_pages=[],
        new_independent_papers=0, author_code_executed=False, medical_arrays_loaded=0,
        neural_forwards=0, GPU_forwards=0,
        source_bindings=[client.base.entry(p) for p in [Path(__file__), HERE/'PROTOCOL.md',
            ROOT/'literature/2026-09-30_diffusion_prior_art.md',
            ROOT/'literature/2026-10-08_relative_utility_collision_recheck.md']],
        resource_snapshot=client.resource_guard())
    client.base.new(OUT/'receipt.json', receipt)
    print(json.dumps(receipt, ensure_ascii=False), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
