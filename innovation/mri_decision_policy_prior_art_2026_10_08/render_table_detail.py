"""Enlarge the numerical supplementary table for primary-source checking."""
import sys,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'task_adaptation_compute_prior_art_2026_10_08'))
import query_primary as base
sys.path.insert(0,str(ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08/site_packages'))
import pypdfium2 as pdfium
base.own_priority();out=HERE/'visual_detail_attempt01';out.mkdir(exist_ok=False)
source=HERE/'primary_attempt01/diagnostic.pdf';doc=pdfium.PdfDocument(str(source));page=doc[10]
bitmap=page.render(scale=2.6);im=bitmap.to_pil();crop=im.crop((200,370,1400,940))
path=out/'diagnostic_table2_detail.png';crop.save(path)
base.new(out/'receipt.json',dict(complete=True,errors=[],physical_page=11,scale=2.6,
    crop_pixels=[200,370,1400,940],source_bindings=[base.entry(Path(__file__)),base.entry(source)],
    output_bindings=[base.entry(path)],visual_reviewed=False,original_PDF_reexported=False))
crop.close();im.close();bitmap.close();page.close();doc.close()
print(json.dumps(dict(complete=True,physical_page=11)),flush=True)
