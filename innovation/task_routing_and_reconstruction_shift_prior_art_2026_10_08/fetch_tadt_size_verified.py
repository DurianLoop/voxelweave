"""Only TADT, using verified Content-Length and fresh immutable output directory."""
import hashlib,json,re,subprocess,sys,time,traceback,shutil
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent;OUT=HERE/'tadt_size_verified_attempt03'
sys.path.insert(0,str(ROOT/'task_adaptation_compute_prior_art_2026_10_08'))
import query_primary as base
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard

def main():
    sys.stdout.reconfigure(encoding='utf-8');tick=time.perf_counter();resources=resource_guard()
    assert shutil.disk_usage(ROOT).free>8_050_000_000
    headers=HERE/'primary_attempt02/tadt_headers.txt'; ht=headers.read_text(encoding='utf-8')
    assert re.search(r'(?im)^Content-Length: 10036939\s*$',ht)
    index=ROOT/'mri_decision_policy_prior_art_2026_10_08/index_attempt01/receipt.json'
    row=next(e for g in json.loads(index.read_text(encoding='utf-8'))['records'] for e in g['entries'] if e['id'].endswith('/2408.08736v2'))
    assert row['title']=='Task-Aware Dynamic Transformer for Efficient Arbitrary-Scale Image Super-Resolution'
    OUT.mkdir(exist_ok=False);p=OUT/'tadt.pdf'
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],indexed_record=row,
           requested_url='https://arxiv.org/pdf/2408.08736v2',file_size_limit_bytes=10_050_000,expected_body_bytes=10_036_939,
           source_bindings=[base.entry(v) for v in (Path(__file__),HERE/'PROTOCOL.md',HERE/'TADT_SIZE_VERIFIED_AMENDMENT.md',headers,index)],
           resources_before=resources,new_primary_papers_read=0,medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,training_updates=0)
    try:
        c=subprocess.run(['curl.exe','--noproxy','*','--fail','--silent','--show-error','--location','--max-redirs','3',
            '--proto','=https','--proto-redir','=https','--max-time','30','--max-filesize','10050000','--dump-header',str(OUT/'headers.txt'),
            '--output',str(p),'--write-out','%{http_code}\n%{url_effective}',r['requested_url']],capture_output=True,timeout=35)
        (OUT/'stderr.txt').write_bytes(c.stderr);r.update(curl_exit=c.returncode,status_and_effective_url=c.stdout.decode('utf-8',errors='replace'))
        assert c.returncode==0 and p.stat().st_size==r['expected_body_bytes'] and p.read_bytes().startswith(b'%PDF-')
        r['file']=base.entry(p)
        et=re.search(r'(?im)^etag:\s*"sha256:([0-9a-f]{64})"', (OUT/'headers.txt').read_text(encoding='utf-8'))
        r.update(ETag_SHA256=et.group(1) if et else None,ETag_matches_actual_body=bool(et and et.group(1)==r['file']['sha256']))
        sys.path.insert(0,str(ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08/site_packages'))
        from pypdf import PdfReader
        reader=PdfReader(p);r['physical_pages']=len(reader.pages);r['page_texts']=[]
        for n,page in enumerate(reader.pages,1):
            text=page.extract_text() or '';dest=OUT/f'tadt_page{n:03d}.txt'
            with dest.open('x',encoding='utf-8') as f:f.write(text)
            r['page_texts'].append(dict(physical_page=n,text_read=False,**base.entry(dest)))
        first=(OUT/'tadt_page001.txt').read_text(encoding='utf-8')
        r['first_page_text_for_identity_review']=first[:4000]
        r.update(complete=True,status='body_length_and_PDF_parse_passed',local_title_authors_version_review_pending=True)
    except Exception as e:r['errors'].append(f'{type(e).__name__}: {e}');r['traceback']=traceback.format_exc()
    r.update(resources_after=resource_guard(),elapsed_seconds=time.perf_counter()-tick)
    assert sum(v.stat().st_size for v in HERE.rglob('*') if v.is_file())<30_000_000
    base.new(OUT/'receipt.json',r)
    print(json.dumps({k:r.get(k) for k in ('complete','errors','physical_pages','file','ETag_matches_actual_body','elapsed_seconds')}),flush=True)
    return 0 if r['complete'] else 1
if __name__=='__main__':raise SystemExit(main())
