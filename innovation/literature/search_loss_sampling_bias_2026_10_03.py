"""Bounded official PMC title/abstract search; no full-reading claims."""
import json,hashlib,sys,urllib.parse,urllib.request,traceback
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'source_cache/loss_sampling_bias_search_2026-10-03'
QUERIES=[
    '(segmentation[Title/Abstract]) AND ("Dice loss"[Title/Abstract]) AND (gradient[Title/Abstract] OR bias[Title/Abstract] OR volume[Title/Abstract])',
    '(loss[Title]) AND (segmentation[Title/Abstract]) AND (imbalanced[Title/Abstract] OR imbalance[Title/Abstract])',
    '(segmentation[Title/Abstract]) AND (sampling[Title/Abstract]) AND (bias[Title/Abstract] OR foreground[Title/Abstract])']
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),
        plan_sha256=sha(ROOT/'2026-10-03_loss_sampling_bias_search_plan.md'),queries=[],complete=False,errors=[],
        primary_bodies_read=0,actual_reading_completed=False)
    def fetch(params,name):
        url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'+params.pop('endpoint')+'?'+urllib.parse.urlencode(params)
        with opener.open(url,timeout=25) as response:
            raw=response.read(8000001);assert len(raw)<=8000000;status=response.status
        path=OUT/name;path.write_bytes(raw)
        return json.loads(raw),dict(url=url,http_status=status,file=name,sha256=sha(path),bytes=len(raw))
    try:
        for i,query in enumerate(QUERIES):
            s,request=fetch(dict(endpoint='esearch.fcgi',db='pmc',term=query+' AND ("1900/01/01"[Publication Date] : "2026/10/03"[Publication Date])',retmax=6,retmode='json',sort='relevance'),f'query_{i+1}_search.response')
            ids=s['esearchresult']['idlist'];row=dict(query=query,total_hits=int(s['esearchresult']['count']),ids=ids,search_request=request,titles=[])
            if ids:
                v,summary=fetch(dict(endpoint='esummary.fcgi',db='pmc',id=','.join(ids),retmode='json'),f'query_{i+1}_summary.response')
                row['summary_request']=summary
                for uid in ids:
                    e=v['result'][uid];row['titles'].append(dict(pmcid='PMC'+uid,title=e.get('title'),pubdate=e.get('pubdate'),articleids=e.get('articleids',[])))
            r['queries'].append(row);(OUT/'attempt_01.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            print(json.dumps(row,ensure_ascii=False),flush=True)
        r['complete']=True
    except Exception as error:r['errors'].append(type(error).__name__+': '+str(error));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();(OUT/'attempt_01.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
