"""Six bounded public GETs based on actually indexed identities and repository searches."""
import sys,json,ssl,time,traceback,re
from pathlib import Path
from datetime import datetime,timezone
from urllib.request import build_opener,ProxyHandler,HTTPSHandler,Request
from urllib.error import HTTPError
from urllib.parse import urlencode,quote,urljoin
from html.parser import HTMLParser
from concurrent.futures import ThreadPoolExecutor
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'index_attempt01'
sys.path.insert(0,str(ROOT/'seranet_identity_prior_art_2026_10_08'))
import query_seranet_stdlib_v3 as previous
base=previous.base

class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.metadata=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=='a' and d.get('href'):self.links.append(d['href'])
        if tag in ('link','meta'):self.metadata.append(d)

def inverted_abstract(data):
    index=data.get('abstract_inverted_index')
    if not index:return None
    words={pos:word for word,positions in index.items() for pos in positions}
    return ' '.join(words[i] for i in sorted(words))

def fetch(job):
    key,url,kind=job;tick=time.perf_counter()
    row=dict(key=key,requested_url=url,complete=False,errors=[])
    try:
        context=ssl.create_default_context()
        opener=build_opener(ProxyHandler({}),HTTPSHandler(context=context),previous.LimitedRedirect())
        req=Request(url,headers={'User-Agent':'MRI-innovation-literature-audit/1.0'})
        with opener.open(req,timeout=30) as response:
            row.update(HTTP_status=response.status,effective_url=response.geturl())
            base.new(OUT/(key+'_headers.json'),dict(status=response.status,headers=dict(response.headers)))
            blocks,total=[],0
            while True:
                b=response.read(65536)
                if not b:break
                total+=len(b);assert total<=3_000_000 and time.perf_counter()-tick<=35
                blocks.append(b)
            body=b''.join(blocks)
        p=OUT/(key+('.html' if kind=='landing' else '.json'))
        with p.open('xb') as f:f.write(body)
        row['response_binding']=base.entry(p)
        if kind=='repo':
            data=json.loads(body);row['total_count']=data['total_count']
            row['entries']=[{k:e.get(k) for k in ('full_name','html_url','url','description','default_branch','contents_url','license','owner')} for e in data['items']]
        elif kind=='openalex':
            data=json.loads(body)
            row['metadata']={k:data.get(k) for k in ('id','doi','title','publication_year','open_access','best_oa_location','locations')}
            row['metadata']['authors']=[e['author']['display_name'] for e in data.get('authorships',[])]
            row['metadata']['abstract']=inverted_abstract(data)
        elif kind=='s2':row['metadata']=json.loads(body)
        else:
            text=body.decode('utf-8',errors='replace');parser=Links();parser.feed(text)
            title=re.search(r'<title[^>]*>(.*?)</title>',text,flags=re.S|re.I)
            row.update(page_title=title.group(1) if title else None,
                metadata=parser.metadata,
                public_links=list(dict.fromkeys(urljoin(row['effective_url'],h) for h in parser.links)))
        row['complete']=True
    except HTTPError as e:
        row.update(HTTP_status=e.code,effective_url=e.geturl())
        body=e.read(3_000_001);assert len(body)<=3_000_000
        p=OUT/(key+'_error.bin')
        with p.open('xb') as f:f.write(body)
        row['error_response']=base.entry(p);row['errors'].append(type(e).__name__+': '+str(e))
    except Exception as e:
        row['errors'].append(type(e).__name__+': '+str(e));row['traceback']=traceback.format_exc()
    row['elapsed_seconds']=time.perf_counter()-tick
    return row

def main():
    sys.stdout.reconfigure(encoding='utf-8');base.own_priority();previous.resource_guard()
    assert not OUT.exists();OUT.mkdir();tick=time.perf_counter()
    source=ROOT/'seranet_identity_prior_art_2026_10_08/location_attempt01/receipt.json'
    q=json.loads(source.read_text(encoding='utf-8'))
    locations=next(r for r in q['records'] if r['key']=='acar_openalex')['metadata']['locations']
    itu=next(e['landing_page_url'] for e in locations if e['id'].endswith('11527/67552'))
    bilkent=next(e['landing_page_url'] for e in locations if e['id'].endswith('11693/111374'))
    assert itu=='https://hdl.handle.net/11527/67552' and bilkent=='http://hdl.handle.net/11693/111374'
    doi='10.1016/j.imavis.2024.105200'
    jobs=[('seranet_repos','https://api.github.com/search/repositories?'+urlencode({'q':'SERANet','per_page':5}),'repo'),
          ('teacher_forcing_repos','https://api.github.com/search/repositories?'+urlencode({'q':'"iterative teacher forcing" MRI','per_page':5}),'repo'),
          ('xu_openalex','https://api.openalex.org/works/https://doi.org/'+quote(doi,safe='/'),'openalex'),
          ('xu_s2','https://api.semanticscholar.org/graph/v1/paper/DOI:'+quote(doi,safe='/')+'?'+urlencode({'fields':'title,authors,year,externalIds,openAccessPdf,url,abstract'}),'s2'),
          ('acar_itu',itu,'landing'),('acar_bilkent','https'+bilkent[4:],'landing')]
    with ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(fetch,jobs))
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=all(r['complete'] for r in rows),
        errors=[e for r in rows for e in r['errors']],records=rows,
        source_bindings=[base.entry(p) for p in (Path(__file__),HERE/'PROTOCOL.md',source)],
        bilkent_handle_original_http=True,bilkent_handle_same_host_path_https_upgrade=True,
        public_GET_only=True,authentication_used=False,TLS_verification_disabled=False,automatic_retries=False,
        resource_snapshot=previous.resource_guard(),elapsed_seconds=time.perf_counter()-tick,
        new_primary_papers_read=0,medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0)
    base.new(OUT/'receipt.json',result)
    for r in rows:
        display={k:r[k] for k in ('key','complete','HTTP_status','effective_url','total_count','page_title','errors') if k in r}
        if 'entries' in r:display['entries']=[{k:e[k] for k in ('full_name','html_url','description')} for e in r['entries']]
        if r['key'].startswith('xu_'):display['metadata']=r.get('metadata')
        if r['key'].startswith('acar_'):display['public_links']=r.get('public_links');display['metadata']=r.get('metadata')
        print(json.dumps(display,ensure_ascii=False),flush=True)
    return int(not result['complete'])
if __name__=='__main__':raise SystemExit(main())
