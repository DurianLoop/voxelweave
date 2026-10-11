"""Bounded PMC augmentation index search, excluding full-reading claims."""
import json,hashlib,sys,urllib.parse,urllib.request,traceback
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'source_cache/coverage_augmentation_search_2026-10-03'
QUERIES=[
    '(augmentation[Title]) AND (segmentation[Title/Abstract]) AND (MRI[Title/Abstract] OR magnetic[Title/Abstract])',
    '(augmentation[Title/Abstract]) AND (segmentation[Title/Abstract]) AND (brain[Title/Abstract]) AND (small[Title/Abstract] OR limited[Title/Abstract])']
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],script_sha256=sha(__file__),queries=[],primary_bodies_read=0)
    def fetch(params,name):
        url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'+params.pop('endpoint')+'?'+urllib.parse.urlencode(params)
        with opener.open(url,timeout=25) as response:raw=response.read(8000001);status=response.status
        assert len(raw)<=8000000;p=OUT/name;p.write_bytes(raw)
        return json.loads(raw),dict(url=url,http_status=status,file=name,sha256=sha(p),bytes=len(raw))
    try:
        for i,query in enumerate(QUERIES):
            s,request=fetch(dict(endpoint='esearch.fcgi',db='pmc',term=query+' AND ("1900/01/01"[Publication Date] : "2026/10/03"[Publication Date])',retmax=6,retmode='json',sort='relevance'),f'query_{i+1}_search.response')
            ids=s['esearchresult']['idlist'];row=dict(query=query,total_hits=int(s['esearchresult']['count']),ids=ids,search_request=request,titles=[])
            if ids:
                data,summary=fetch(dict(endpoint='esummary.fcgi',db='pmc',id=','.join(ids),retmode='json'),f'query_{i+1}_summary.response');row['summary_request']=summary
                for uid in ids:
                    item=data['result'][uid];row['titles'].append(dict(pmcid='PMC'+uid,title=item.get('title'),pubdate=item.get('pubdate'),articleids=item.get('articleids',[])))
            r['queries'].append(row);(OUT/'attempt_01.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(row,ensure_ascii=False),flush=True)
        r['complete']=True
    except Exception as error:r['errors'].append(type(error).__name__+': '+str(error));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();(OUT/'attempt_01.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
