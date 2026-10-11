"""Inspect local PDF identity after transport succeeds but ETag SHA disagrees."""
import json,sys,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'task_adaptation_compute_prior_art_2026_10_08'))
import query_primary as base
sys.path.insert(0,str(ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08/site_packages'))
from pypdf import PdfReader
base.own_priority();out=HERE/'thesis_identity_attempt01';out.mkdir(exist_ok=False)
source=HERE/'thesis_size_verified_attempt02/cartesian_thesis.pdf'
data=source.read_bytes();assert data.startswith(b'%PDF-') and len(data)==12377385
reader=PdfReader(source);rows=[]
for n in range(min(8,len(reader.pages))):
    text=reader.pages[n].extract_text() or '';p=out/f'identity_page{n+1:03d}.txt'
    with p.open('x',encoding='utf-8') as f:f.write(text)
    rows.append(dict(physical_page=n+1,text_read=False,**base.entry(p)))
result=dict(complete=True,errors=[],inspection_only=True,physical_pages=len(reader.pages),
    metadata={str(k):str(v) for k,v in (reader.metadata or {}).items()},page_texts=rows,
    source_bindings=[base.entry(Path(__file__)),base.entry(source),base.entry(HERE/'thesis_size_verified_attempt02/receipt.json')],
    actual_body_sha256=hashlib.sha256(data).hexdigest(),ETag_sha256_match=False,
    reading_source_qualified=False,medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0)
base.new(out/'receipt.json',result)
print(json.dumps(dict(complete=True,physical_pages=result['physical_pages'],metadata=result['metadata'],
    actual_body_sha256=result['actual_body_sha256']),ensure_ascii=False),flush=True)
for n in range(2):print((out/f'identity_page{n+1:03d}.txt').read_text(encoding='utf-8'),flush=True)
