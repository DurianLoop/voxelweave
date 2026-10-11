"""Read-only eight-page SSC extraction/render using existing local readers, no installation."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import sys,time,json,traceback
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,entry,bind,dump,resource_guard
RUNTIME=ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08';sys.path.insert(0,str(RUNTIME/'site_packages'))
from pypdf import PdfReader
import pypdfium2 as pdfium
started=time.perf_counter();out=HERE/'ssc_extraction_render_attempt01';out.mkdir(exist_ok=False)
r=dict(complete=False,errors=[],pages=[],primary_pages_actually_read=False,figure_pixels_actually_read=False,
 medical_arrays_loaded=0,author_code_executed=False,dependencies_installed=False)
def guard():
 res=resource_guard();size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
 fov=ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09';fs=sum(p.stat().st_size for p in fov.rglob('*') if p.is_file())
 assert size<7_000_000 and fs<20_000_000 and time.perf_counter()-started<180
 assert res['workspace_free_bytes']-22_800_000-(7_000_000-size)-(20_000_000-fs)>=8_000_000_000
 return res
try:
 r['resources_before']=guard();fp=HERE/'ssc_primary_pdf_attempt01/receipt.json';meta=read(fp);assert meta['complete'] and not meta['errors']
 source=bind(meta['pdf']);reader=PdfReader(source);doc=pdfium.PdfDocument(str(source));assert len(reader.pages)==len(doc)==8
 assert 'Towards Realtime Multimodal Fusion' in reader.metadata.title
 r['source_bindings']=[entry(p) for p in [Path(__file__),HERE/'SSC_PRIMARY_PDF_PROTOCOL.md',fp,source,RUNTIME/'installation_attempt03.json']]
 for index in range(8):
  guard();page=doc[index];textpage=page.get_textpage();text=textpage.get_text_range();assert not any(0xD800<=ord(c)<=0xDFFF for c in text)
  p=out/f'page_{index+1:02d}.txt';p.write_text(text,encoding='utf-8')
  bitmap=page.render(scale=1.5);picture=bitmap.to_pil();im=out/f'page_{index+1:02d}.png';picture.save(im)
  r['pages'].append(dict(physical_page=index+1,text=entry(p),render=entry(im),pixels=list(picture.size),text_actually_read=False,render_actually_inspected=False))
  picture.close();bitmap.close();textpage.close();page.close()
 doc.close();first=(out/'page_01.txt').read_text(encoding='utf-8');flat=' '.join(first.split())
 assert 'Towards Realtime Multimodal Fusion' in flat and all(v in flat for v in ['Mattias Paul Heinrich','Mark Jenkinson','Brady','Schnabel','187–194'])
 r.update(complete=True,verified_pages=8,publisher_page_range='187-194',local_title_authors_identity_passed=True,
  DOI_identity_from_metadata_and_request_not_printed_page=True,PDF_metadata=dict(reader.metadata),resources_after=guard())
except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
r['elapsed_seconds']=time.perf_counter()-started;dump(out/'receipt.json',r)
print(json.dumps({k:r.get(k) for k in ['complete','errors','verified_pages','publisher_page_range','elapsed_seconds']},ensure_ascii=False),flush=True)
raise SystemExit(int(not r['complete']))
