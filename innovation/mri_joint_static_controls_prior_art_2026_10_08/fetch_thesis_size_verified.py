"""One public-PDF retry with verified size/hash in a new, immutable attempt."""
import sys,json,re,time,shutil,hashlib,subprocess,traceback
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'task_adaptation_compute_prior_art_2026_10_08'))
import query_primary as base
def main():
    sys.stdout.reconfigure(encoding='utf-8');base.own_priority();assert shutil.disk_usage(ROOT).free>8_050_000_000
    prior=HERE/'primary_attempt01/receipt.json';headers=HERE/'primary_attempt01/cartesian_thesis_headers.txt'
    failure=json.loads(prior.read_text(encoding='utf-8'));row=next(r for r in failure['records'] if r['key']=='cartesian_thesis')
    assert row['curl_exit']==63 and not row['complete']
    h=headers.read_text(encoding='utf-8');size=int(re.search(r'Content-Length: (\d+)',h,re.I)[1])
    expected=re.search(r'etag: "sha256:([a-f0-9]{64})"',h,re.I)[1]
    assert size==12_377_385 and size<12_500_000
    out=HERE/'thesis_size_verified_attempt02';out.mkdir(exist_ok=False);tick=time.perf_counter()
    p=out/'cartesian_thesis.pdf';url=row['requested_url']
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],requested_url=url,
        indexed_record=row['indexed_record'],expected_bytes=size,expected_sha256=expected,
        source_bindings=[base.entry(Path(__file__)),base.entry(HERE/'PROTOCOL.md'),base.entry(prior),base.entry(headers),
            base.entry(HERE/'THESIS_SIZE_VERIFIED_AMENDMENT.md'),base.entry(HERE/'static_index_attempt01/receipt.json')],
        public_GET_only=True,TLS_verification_disabled=False,medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,
        training_updates=0,new_primary_papers_read=0,extraction_is_not_reading=True,goal_status='active')
    try:
        proc=subprocess.run(['curl.exe','--noproxy','*','--fail','--silent','--show-error','--location',
            '--max-redirs','3','--proto','=https','--proto-redir','=https','--max-time','30','--max-filesize','12500000',
            '--dump-header',str(out/'headers.txt'),'--output',str(p),'--write-out','%{http_code}\n%{url_effective}',url],
            capture_output=True,timeout=35)
        (out/'stderr.txt').write_bytes(proc.stderr)
        result.update(curl_exit=proc.returncode,status_and_effective_url=proc.stdout.decode('utf-8',errors='replace'))
        assert proc.returncode==0,proc.stderr.decode('utf-8',errors='replace')
        assert p.stat().st_size==size and hashlib.sha256(p.read_bytes()).hexdigest()==expected
        assert p.read_bytes().startswith(b'%PDF-');result['file']=base.entry(p)
        sys.path.insert(0,str(ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08/site_packages'))
        from pypdf import PdfReader
        reader=PdfReader(p);result['physical_pages']=len(reader.pages);result['page_texts']=[]
        for n,page in enumerate(reader.pages,1):
            path=out/f'thesis_page{n:03d}.txt'
            with path.open('x',encoding='utf-8') as f:f.write(page.extract_text() or '')
            result['page_texts'].append(dict(physical_page=n,text_read=False,**base.entry(path)))
        result['complete']=True
    except Exception as e:
        result['errors'].append(type(e).__name__+': '+str(e));result['traceback']=traceback.format_exc()
    result['elapsed_seconds']=time.perf_counter()-tick
    result['workspace_free_bytes_after']=shutil.disk_usage(ROOT).free
    assert result['workspace_free_bytes_after']>=8_000_000_000
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<30_000_000
    base.new(out/'receipt.json',result)
    print(json.dumps({k:result.get(k) for k in ('complete','physical_pages','file','errors','elapsed_seconds','workspace_free_bytes_after')},
        ensure_ascii=False),flush=True)
    return int(not result['complete'])
if __name__=='__main__':raise SystemExit(main())
