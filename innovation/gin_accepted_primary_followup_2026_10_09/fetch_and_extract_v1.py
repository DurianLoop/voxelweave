"""Public accepted GIN manuscript: frozen raw PDF, extracted text and compact page renders."""
import os
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='1'
import sys,json,time,ssl,urllib.request,traceback
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import entry,bind,read,dump,resource_guard
RUNTIME=ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08';sys.path.insert(0,str(RUNTIME/'site_packages'))
from pypdf import PdfReader
import pypdfium2 as pdfium
LIMIT=6_000_000;started=time.perf_counter();out=HERE/'accepted_pdf_attempt01';out.mkdir(exist_ok=False)
r=dict(complete=False,errors=[],pages=[],source_version='institution_repository_accepted_version',
       publisher_typeset_final_claimed=False,primary_maintext_actually_read=False,figure_pixels_actually_read=False,
       new_distinct_primary_papers_read=0,medical_data_uploaded=False,dependencies_installed=False,
       author_source_executed=False,access_denial_not_bypassed=True)
def guard():
    v=resource_guard();size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
    prep=ROOT/'six_resolution_training_preparation_2026_10_09';ps=sum(p.stat().st_size for p in prep.rglob('*') if p.is_file())
    fov=ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09';fs=sum(p.stat().st_size for p in fov.rglob('*') if p.is_file())
    assert size<LIMIT and ps<7_000_000 and fs<20_000_000
    assert v['workspace_free_bytes']-22_800_000-(7_000_000-ps)-(20_000_000-fs)-(LIMIT-size)>=8_000_000_000
    assert time.perf_counter()-started<180
    v.update(paper_total_limit_bytes=LIMIT,paper_current_bytes=size,prep_current_bytes=ps,FOV_current_bytes=fs,
             all_original_stage_limits_retained=True,only_remaining_stage_allowances_subtracted=True)
    return v
try:
    r['resources_before']=guard();lp=ROOT/'six_resolution_training_preparation_2026_10_09/gin_imperial_landing_attempt02/receipt.json';landing=read(lp)
    assert landing['complete'] and landing['doi_present'] and landing['title_present']
    text=bind(landing['visible_text']).read_text('utf-8');assert 'Accepted version' in text
    url=next(v['content'] for v in landing['citation_metadata'] if v['name']=='citation_pdf_url')
    assert url=='https://spiral.imperial.ac.uk/bitstreams/9f1f03f2-fac1-4402-8045-9f9455fdac2d/download'
    r['requested_url']=url
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ssl.create_default_context()))
    with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRIResearchLiterature/1.0'}),timeout=25) as response:
        r.update(http_status=response.status,effective_url=response.url,content_type=response.headers.get('Content-Type'))
        raw=response.read(5_000_001);assert len(raw)<=5_000_000 and raw.startswith(b'%PDF')
    source=out/'accepted.pdf';source.write_bytes(raw);r['pdf']=entry(source);del raw;guard()
    reader=PdfReader(source);doc=pdfium.PdfDocument(str(source));assert len(reader.pages)==len(doc) and 10<=len(doc)<=16
    r['pdf_metadata']=dict(reader.metadata or {})
    r['source_bindings']=[entry(p) for p in (Path(__file__),HERE/'PROTOCOL.md',lp,RUNTIME/'installation_attempt03.json')]
    for index in range(len(doc)):
        guard();page=doc[index];tp=page.get_textpage();text=tp.get_text_range()
        assert not any(0xD800<=ord(c)<=0xDFFF for c in text)
        p=out/f'page_{index+1:02d}.txt';p.write_text(text,encoding='utf-8')
        bitmap=page.render(scale=1.0);image=bitmap.to_pil();compact=image.convert('RGB').quantize(colors=128)
        im=out/f'page_{index+1:02d}.png';compact.save(im,optimize=True)
        r['pages'].append(dict(physical_page=index+1,text=entry(p),render=entry(im),pixels=list(image.size),
                              text_actually_read=False,render_actually_inspected=False,render_scale=1.0,palette_colors=128))
        compact.close();image.close();bitmap.close();tp.close();page.close();guard()
    doc.close();first=' '.join((out/'page_01.txt').read_text('utf-8').split())
    assert 'Causality' in first and 'Single' in first and 'Generalization' in first
    assert all(n in first for n in ('Ouyang','Chen','Li','Qin','Bai','Rueckert'))
    r.update(complete=True,verified_pages=len(reader.pages),title_authors_identity_verified=True,
             DOI_identity_verified_from_repository_metadata=True,resources_after=guard())
except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
r['elapsed_seconds']=time.perf_counter()-started;dump(out/'receipt.json',r)
print(json.dumps({k:r.get(k) for k in ('complete','errors','verified_pages','pdf','source_version','elapsed_seconds')}),flush=True)
raise SystemExit(int(not r['complete']))
