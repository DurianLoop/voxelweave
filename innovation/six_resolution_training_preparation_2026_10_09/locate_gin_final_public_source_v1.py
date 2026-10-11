"""DOI-exact public journal-version locator; no access circumvention or medical upload."""
import sys,time,json,gzip,ssl,urllib.request,urllib.parse
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import entry,dump,resource_guard
started=time.perf_counter();out=HERE/'gin_final_source_locator_attempt01';out.mkdir(exist_ok=False)
DOI='10.1109/TMI.2022.3224067'
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ssl.create_default_context()))
def guard():
    r=resource_guard();size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
    fov=ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09';fs=sum(p.stat().st_size for p in fov.rglob('*') if p.is_file())
    assert size<7_000_000 and fs<20_000_000
    assert r['workspace_free_bytes']-22_800_000-(7_000_000-size)-(20_000_000-fs)>=8_000_000_000
    assert time.perf_counter()-started<120;return r
r=dict(complete=False,errors=[],records=[],public_candidate_sources=[],final_primary_maintext_read=False,
       new_distinct_primary_maintexts_read=0,medical_data_uploaded=False,access_denial_not_bypassed=True,
       author_source_executed=False,doi=DOI,source_bindings=[entry(Path(__file__))],resources_before=guard())
queries=[('crossref','https://api.crossref.org/works/'+urllib.parse.quote(DOI,safe='')),
         ('openalex','https://api.openalex.org/works/https://doi.org/'+DOI+'?select=id,doi,title,primary_location,locations,open_access')]
for name,url in queries:
    row=dict(provider=name,requested_url=url,complete=False)
    try:
        guard()
        with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRIResearchLiterature/1.0','Accept':'application/json'}),timeout=25) as response:
            raw=response.read(250001);assert len(raw)<=250000
            row.update(http_status=response.status,effective_url=response.url)
        data=json.loads(raw);p=out/(name+'.json.gz');p.write_bytes(gzip.compress(raw,mtime=0));row['saved']=entry(p)
        value=data['message'] if name=='crossref' else data
        reported=value['DOI'] if name=='crossref' else value['doi'].removeprefix('https://doi.org/')
        assert reported.casefold()==DOI.casefold();row.update(complete=True,title=value['title'])
        if name=='crossref':
            row['publisher_links']=value.get('link',[])
            r['public_candidate_sources'].extend(dict(provider=name,URL=v.get('URL'),content_type=v.get('content-type'),version_verified=False) for v in value.get('link',[]))
        else:
            row['open_access']=value.get('open_access');row['locations']=value.get('locations',[])
            r['public_candidate_sources'].extend(dict(provider=name,pdf_url=v.get('pdf_url'),landing_page_url=v.get('landing_page_url'),
                                                  reported_version=v.get('version'),is_oa=v.get('is_oa'),version_verified=False)
                                                 for v in value.get('locations',[]) if v.get('pdf_url') or v.get('is_oa'))
    except Exception as e:row['error']=dict(type=type(e).__name__,message=str(e))
    r['records'].append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
r['complete']=all(v['complete'] for v in r['records']);r['elapsed_seconds']=time.perf_counter()-started;r['resources_after']=guard()
dump(out/'receipt.json',r)
print(json.dumps(dict(complete=r['complete'],candidates=r['public_candidate_sources'],final_maintext_read=False),ensure_ascii=False),flush=True)
