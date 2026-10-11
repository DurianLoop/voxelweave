"""Recover paired UTF-16 math glyphs without changing original byte/code-unit data."""
import json,sys,time,traceback
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'tadt_text_attempt04'
sys.path.insert(0,str(ROOT/'task_adaptation_compute_prior_art_2026_10_08'))
import query_primary as base
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard

def main():
    sys.stdout.reconfigure(encoding='utf-8');tick=time.perf_counter();resource_guard();OUT.mkdir(exist_ok=False)
    source=HERE/'tadt_size_verified_attempt03/tadt.pdf'
    expected='d5aab3d1dba2a68aee7981641f0ab450c0241f3ba7066166c7b70ec006373cd8'
    assert base.entry(source)['sha256']==expected
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],source_bindings=[base.entry(p) for p in
        (Path(__file__),source,HERE/'TADT_BODY_AND_TEXT_CLARIFICATION.md',HERE/'tadt_size_verified_attempt03/receipt.json')],
        page_texts=[],new_primary_papers_read=0,medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,network_requests=0)
    try:
        sys.path.insert(0,str(ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08/site_packages'))
        from pypdf import PdfReader
        reader=PdfReader(source);assert len(reader.pages)==16
        for n,page in enumerate(reader.pages,1):
            resource_guard();raw=page.extract_text() or '';archive=OUT/f'tadt_page{n:03d}_raw.json'
            with archive.open('x',encoding='ascii') as f:json.dump(dict(raw_text=raw),f,ensure_ascii=True)
            code_units=raw.encode('utf-16-le',errors='surrogatepass');clean=code_units.decode('utf-16-le',errors='strict')
            assert clean.encode('utf-16-le')==code_units
            p=OUT/f'tadt_page{n:03d}.txt'
            with p.open('x',encoding='utf-8') as f:f.write(clean)
            r['page_texts'].append(dict(physical_page=n,text_read=False,raw_extract=base.entry(archive),
                surrogate_code_units=sum(0xD800<=ord(c)<=0xDFFF for c in raw),code_units_exactly_preserved=True,**base.entry(p)))
        first=(OUT/'tadt_page001.txt').read_text(encoding='utf-8');flat=' '.join(first.split())
        assert 'Task-Aware Dynamic Transformer for Efficient Arbitrary-Scale Image Super-Resolution' in flat
        assert 'arXiv:2408.08736v2' in first and all(name in flat for name in ('Tianyi Xu','Yijie Zhou','Jun Xu'))
        r.update(complete=True,local_title_authors_version_identity_passed=True,physical_pages=16,ETag_match_not_claimed=True)
    except Exception as e:r['errors'].append(f'{type(e).__name__}: {e}');r['traceback']=traceback.format_exc()
    r.update(resources_after=resource_guard(),elapsed_seconds=time.perf_counter()-tick)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<30_000_000
    base.new(OUT/'receipt.json',r)
    print(json.dumps(dict(complete=r['complete'],errors=r['errors'],pages_extracted=len(r['page_texts']),
        surrogate_code_units_preserved=sum(v['surrogate_code_units'] for v in r['page_texts']))),flush=True)
    return 0 if r['complete'] else 1
if __name__=='__main__':raise SystemExit(main())
