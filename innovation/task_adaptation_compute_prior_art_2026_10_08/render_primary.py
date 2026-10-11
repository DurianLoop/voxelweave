"""Render formula, experiment and denominator pages; preserve original PDFs."""
import sys,time,json
from pathlib import Path
from datetime import datetime,timezone
from query_primary import HERE,ROOT,entry,new,own_priority

def main():
    sys.stdout.reconfigure(encoding='utf-8');own_priority();tick=time.perf_counter()
    sys.path.insert(0,str(ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08/site_packages'))
    import pypdfium2 as pdfium
    out=HERE/'visual_attempt01';out.mkdir(exist_ok=False);rows=[]
    for name,pages in [('task_adapted',[17,20,22,24,26]),('tuning_free',[4,5,6,7])]:
        source=HERE/'primary_attempt01'/(name+'.pdf');doc=pdfium.PdfDocument(str(source))
        for n in pages:
            page=doc[n-1];bitmap=page.render(scale=1.15);im=bitmap.to_pil();path=out/(name+'_page'+str(n).zfill(2)+'.png')
            assert not path.exists();im.save(path)
            rows.append(dict(paper=name,physical_page=n,image=entry(path),PDF_source=entry(source),visual_reviewed=False))
            im.close();bitmap.close();page.close()
        doc.close()
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<30_000_000
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,records=rows,
        source_bindings=[entry(Path(__file__)),entry(HERE/'query_primary.py'),entry(HERE/'PROTOCOL.md')],
        elapsed_seconds=time.perf_counter()-tick,medical_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,training_updates=0,
        original_PDF_reexported=False)
    new(out/'receipt.json',result);print(json.dumps(dict(complete=True,rendered_pages=len(rows),elapsed_seconds=result['elapsed_seconds'])),flush=True)
    return 0

if __name__=='__main__':raise SystemExit(main())
