"""Magnify an ambiguous table read from the original PDF, not OCR."""
import sys,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'seranet_identity_prior_art_2026_10_08'))
import query_seranet_stdlib_v3 as client
sys.path.insert(0,str(ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08/site_packages'))
import pypdfium2 as pdfium
client.base.own_priority();client.resource_guard()
doc=pdfium.PdfDocument(str(HERE/'primary_attempt01/mirto.pdf'));page=doc[14]
bm=page.render(scale=3);im=bm.to_pil();width,height=im.size
crop=im.crop((int(width*.10),int(height*.23),int(width*.92),int(height*.36)))
out=HERE/'visual_attempt01/mirto_page015_table4_detail.png';assert not out.exists();crop.save(out)
client.base.new(HERE/'visual_attempt01/table4_detail_receipt.json',dict(complete=True,errors=[],
    source_bindings=[client.base.entry(Path(__file__)),client.base.entry(HERE/'primary_attempt01/mirto.pdf')],
    image=client.base.entry(out),physical_page=15,visual_read=False,resource_snapshot=client.resource_guard()))
im.close();bm.close();page.close();doc.close();print(str(out))
