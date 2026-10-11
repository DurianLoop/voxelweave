"""Bounded public DOI metadata and lawful open PMC acquisition only."""
import hashlib,json,sys,time,urllib.parse,urllib.request
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/recent_thickslice_primary_availability_2026-10-07'
DOIS=['10.1016/j.jneumeth.2026.110834','10.1109/tmi.2026.3662706','10.1016/j.compmedimag.2026.102786']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);started=time.perf_counter();records=[]
    for i,doi in enumerate(DOIS,1):
        assert time.perf_counter()-started<=120
        url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode(dict(query='DOI:"'+doi+'"',format='json',resultType='core',pageSize=3))
        r=dict(doi=doi,url=url,fulltext_acquired=False,metadata_reading_not_new_paper=True)
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'MRI-research-public-literature/1.0'})
            with urllib.request.urlopen(req,timeout=20) as f:
                body=f.read(2000001);assert len(body)<=2000000;r['status']=f.status
            p=OUT/('doi'+str(i)+'_metadata.response');p.write_bytes(body);r.update(metadata_file=p.relative_to(ROOT).as_posix(),metadata_sha256=sha(p))
            d=json.loads(body);matches=[v for v in d.get('resultList',{}).get('result',[]) if v.get('doi','').lower()==doi.lower()]
            r['exact_matches']=matches
            public=[v for v in matches if v.get('isOpenAccess')=='Y' and v.get('pmcid')]
            if public:
                pmcid=public[0]['pmcid'];link='https://www.ebi.ac.uk/europepmc/webservices/rest/'+pmcid+'/fullTextXML'
                with urllib.request.urlopen(urllib.request.Request(link,headers={'User-Agent':'MRI-research-public-literature/1.0'}),timeout=20) as f:
                    raw=f.read(2000001);assert len(raw)<=2000000
                target=OUT/('doi'+str(i)+'_public_fulltext.xml');target.write_bytes(raw)
                r.update(fulltext_acquired=True,fulltext_url=link,fulltext_file=target.relative_to(ROOT).as_posix(),fulltext_sha256=sha(target),actual_primary_reading_completed=False)
            else:r['reason']='No exact DOI record with both openAccess=Y and PMC identifier'
        except Exception as e:r['error']=type(e).__name__+': '+str(e)
        records.append(r)
        print(json.dumps({k:r.get(k) for k in ('doi','fulltext_acquired','reason','error')},ensure_ascii=False),flush=True)
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,script_sha256=sha(__file__),records=records,
        elapsed_seconds=time.perf_counter()-started,new_primary_papers_read=0,new_abstracts_read=0,authors_contacted=False,access_controls_bypassed=False)
    assert sum(p.stat().st_size for p in OUT.iterdir())<10000000
    with (OUT/'attempt01.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    return 0
if __name__=='__main__':raise SystemExit(main())
