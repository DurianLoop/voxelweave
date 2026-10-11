"""Three bounded public GETs; metadata and official supplementary, all under innovation."""
import hashlib
import json
import subprocess
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'literature/source_cache/downstream_feature_cost_primary_2026-10-08'
RUNTIME = ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08/site_packages'


def entry(p):
    return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,
                sha256=hashlib.sha256(p.read_bytes()).hexdigest())


def fetch(job):
    key,url,suffix,limit = job
    path = OUT/(key+suffix)
    row = dict(key=key,requested_url=url,complete=False,errors=[],new_paper_read=False)
    started = time.perf_counter()
    try:
        proc = subprocess.run(['curl.exe','--noproxy','*','--fail','--silent','--show-error',
            '--location','--max-redirs','3','--proto','=https','--proto-redir','=https',
            '--max-time','30','--max-filesize',str(limit),'--dump-header',str(OUT/(key+'_headers.txt')),
            '--output',str(path),'--write-out','%{http_code}\n%{url_effective}',url],capture_output=True,timeout=35)
        (OUT/(key+'_curl_stderr.txt')).write_bytes(proc.stderr)
        row['response_status_stdout'] = proc.stdout.decode('utf-8',errors='replace')
        row['actual_curl_subprocess_exit'] = proc.returncode
        row['TLS_certificate_verification_disabled'] = False
        assert proc.returncode == 0,proc.stderr.decode('utf-8',errors='replace')
        assert path.stat().st_size <= limit
        row['file'] = entry(path)
        if suffix=='.json':
            data = json.loads(path.read_text(encoding='utf-8'))
            if key=='prakash_crossref':
                row['items'] = [dict(title=v.get('title'),author=v.get('author'),DOI=v.get('DOI'),
                    URL=v.get('URL'),link=v.get('link'),published=v.get('published'),
                    resource=v.get('resource'),relation=v.get('relation')) for v in data['message']['items']]
            else:
                row['hitCount'] = data.get('hitCount')
                row['results'] = data.get('resultList',{}).get('result',[])
        row['complete'] = True
    except Exception as exc:
        row['errors'].append(type(exc).__name__+': '+str(exc))
        row['traceback'] = traceback.format_exc()
    row['elapsed_seconds'] = time.perf_counter()-started
    return row


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(exist_ok=False)
    title = 'Leveraging self-supervised denoising for image segmentation'
    jobs = [
        ('prakash_crossref','https://api.crossref.org/works?'+urlencode({'query.title':title,'rows':3}),'.json',3_000_000),
        ('prakash_europepmc','https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urlencode({'query':'TITLE:"'+title+'"','format':'json','pageSize':3,'resultType':'core'}),'.json',3_000_000),
        ('noise2same_supplement','https://proceedings.neurips.cc/paper_files/paper/2020/file/ea6b2efbdd4255a9f1b3bbc6399b58f4-Supplemental.pdf','.pdf',10_000_000)]
    with ThreadPoolExecutor(max_workers=3) as pool:
        rows = list(pool.map(fetch,jobs))
    r = dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=all(v['complete'] for v in rows),
        errors=[],records=rows,source_bindings=[entry(Path(__file__)),
            entry(ROOT/'DEPLOYMENT_FEATURE_COST_AND_DOWNSTREAM_PROTOCOL_2026-10-08.md'),
            entry(ROOT/'literature/source_cache/blindspot_dependence_primary_2026-10-08/noise2same_official_identity_attempt01.json')],
        public_GET_only=True,TLS_certificate_verification_disabled=False,new_primary_papers_read=0,
        medical_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,training_updates=0)
    for v in rows:
        if v['key']=='noise2same_supplement' and v['complete']:
            try:
                sys.path.insert(0,str(RUNTIME))
                from pypdf import PdfReader
                reader = PdfReader(ROOT/v['file']['path'])
                v['physical_pages'] = len(reader.pages)
                texts = []
                for number,page in enumerate(reader.pages,1):
                    path = OUT/f'noise2same_supplement_page{number:02d}.txt'
                    with path.open('x',encoding='utf-8') as f:
                        f.write(page.extract_text() or '')
                    texts.append(dict(physical_page=number,text_read=False,**entry(path)))
                v['page_texts'] = texts
            except Exception as exc:
                r['errors'].append(type(exc).__name__+': '+str(exc))
                r['complete'] = False
    r['saved_bytes'] = sum(p.stat().st_size for p in OUT.iterdir() if p.is_file())
    assert r['saved_bytes'] < 20_000_000
    with (OUT/'acquisition_attempt01.json').open('x',encoding='utf-8') as f:
        json.dump(r,f,ensure_ascii=False,indent=2)
        f.write('\n')
    print(json.dumps(dict(complete=r['complete'],errors=r['errors'],saved_bytes=r['saved_bytes'],
        records=[{k:v.get(k) for k in ('key','complete','errors','items','hitCount','results','physical_pages')} for v in rows]),ensure_ascii=False),flush=True)
    return int(not r['complete'])


if __name__=='__main__':
    raise SystemExit(main())
