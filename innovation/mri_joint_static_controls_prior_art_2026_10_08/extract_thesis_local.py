"""Read a version-identifiable public PDF, binding actual bytes and ETag failure."""
import json,sys,hashlib,time,shutil
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'task_adaptation_compute_prior_art_2026_10_08'))
import query_primary as base
sys.path.insert(0,str(ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08/site_packages'))
from pypdf import PdfReader
def main():
    sys.stdout.reconfigure(encoding='utf-8');base.own_priority();tick=time.perf_counter()
    assert shutil.disk_usage(ROOT).free>8_050_000_000
    source=HERE/'thesis_size_verified_attempt02/cartesian_thesis.pdf'
    assert source.stat().st_size==12377385
    assert hashlib.sha256(source.read_bytes()).hexdigest()=='f318edd5dd559c1282a4f935a443fdbaa519aaaf9f1326d695ef3ca9292ed3bb'
    reader=PdfReader(source);assert len(reader.pages)==189
    identity=reader.pages[0].extract_text() or ''
    assert all(v in identity for v in ('Learning to sample in Cartesian MRI','Thomas Sanchez','2312.04327v1','9981'))
    out=HERE/'thesis_text_attempt01';out.mkdir(exist_ok=False);rows=[]
    for n,page in enumerate(reader.pages,1):
        p=out/f'thesis_page{n:03d}.txt'
        with p.open('x',encoding='utf-8') as f:f.write(page.extract_text() or '')
        rows.append(dict(physical_page=n,text_read=False,**base.entry(p)))
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],physical_pages=189,
        file=base.entry(source),page_texts=rows,source_bindings=[base.entry(Path(__file__)),base.entry(source),
            base.entry(HERE/'THESIS_BODY_IDENTITY_CLARIFICATION.md'),base.entry(HERE/'thesis_identity_attempt01/receipt.json'),
            base.entry(HERE/'thesis_size_verified_attempt02/receipt.json'),base.entry(HERE/'thesis_size_verified_attempt02/headers.txt')],
        local_source_version_identity_passed=True,ETag_sha256_match=False,previous_download_attempt_complete=False,
        original_failed_receipts_not_rewritten=True,extraction_is_not_reading=True,new_primary_papers_read=0,
        medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,training_updates=0,elapsed_seconds=time.perf_counter()-tick)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<30_000_000
    base.new(out/'receipt.json',result)
    print(json.dumps(dict(complete=True,physical_pages=189,source_version_identity_passed=True,ETag_sha256_match=False,
        elapsed_seconds=result['elapsed_seconds'])),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
