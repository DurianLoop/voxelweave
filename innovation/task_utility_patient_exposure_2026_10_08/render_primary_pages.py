"""Read-only PDF rendering with existing portable runtime; no PDF re-export."""
import json,sys,time,ctypes
from datetime import datetime,timezone
from pathlib import Path
from query_acquisition_prior_art import entry
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    k=ctypes.WinDLL('kernel32',use_last_error=True);k.GetCurrentProcess.restype=ctypes.c_void_p
    k.SetPriorityClass.argtypes=(ctypes.c_void_p,ctypes.c_uint32);assert k.SetPriorityClass(k.GetCurrentProcess(),0x00004000)
    sys.path.insert(0,str(ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08/site_packages'))
    import pypdfium2 as pdfium
    out=HERE/'visual_attempt01';out.mkdir(exist_ok=False);tick=time.perf_counter();rows=[]
    for name,pages in [('dynamicdps',[4,7,8]),('tackle',[7,11,15])]:
        source=HERE/'primary_attempt01'/(name+'.pdf');doc=pdfium.PdfDocument(str(source))
        for n in pages:
            page=doc[n-1];bitmap=page.render(scale=1.25);im=bitmap.to_pil();path=out/(name+'_page'+str(n).zfill(2)+'.png')
            assert not path.exists();im.save(path)
            rows.append(dict(paper=name,physical_page=n,image=entry(path),PDF_source=entry(source),visual_reviewed=False))
            im.close();bitmap.close();page.close()
        doc.close()
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,records=rows,
        source_bindings=[entry(Path(__file__)),entry(HERE/'PROTOCOL.md')],elapsed_seconds=time.perf_counter()-tick,
        medical_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,training_updates=0,
        read_only_original_PDF=True)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<30_000_000
    with (out/'receipt.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(dict(complete=True,rendered_pages=len(rows),elapsed_seconds=result['elapsed_seconds']),ensure_ascii=False),flush=True)
    return 0

if __name__=='__main__':raise SystemExit(main())
