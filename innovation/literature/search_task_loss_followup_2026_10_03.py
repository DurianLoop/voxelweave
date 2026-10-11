"""Small-structure loss prior art discovery, without changing live training."""
import json,hashlib,sys,urllib.request,urllib.parse
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'source_cache/task_loss_followup_search_2026-10-03'
QUERIES=['"unified focal loss"[Title]',
         '("small lesions"[Title/Abstract] OR "small structures"[Title/Abstract]) AND segmentation[Title/Abstract] AND (loss[Title/Abstract] OR imbalance[Title/Abstract])']
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),
           plan_sha256=sha(ROOT/'2026-10-03_task_loss_followup_search_plan.md'),
           responses=[],scope='discovery only, no fulltext reading or novelty proof')
    for i,query in enumerate(QUERIES,1):
        row=dict(query=query,items=[])
        try:
            url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?'+urllib.parse.urlencode(
                dict(db='pmc',term='('+query+') AND ("1900/01/01"[Publication Date] : "2026/10/03"[Publication Date])',retmode='json',retmax=6,sort='relevance'))
            row['url']=url
            with opener.open(url,timeout=25) as response:raw=response.read(4000001);row['http_status']=response.status
            assert len(raw)<=4000000
            p=OUT/('query_%02d.response'%i);p.write_bytes(raw)
            found=json.loads(raw)['esearchresult'];row.update(raw_file=p.name,raw_sha256=sha(p),hit_count=int(found['count']))
            if found['idlist']:
                summary='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?'+urllib.parse.urlencode(
                    dict(db='pmc',id=','.join(found['idlist']),retmode='json'))
                row['summary_url']=summary
                with opener.open(summary,timeout=25) as response:raw=response.read(4000001)
                assert len(raw)<=4000000
                p=OUT/('summary_%02d.response'%i);p.write_bytes(raw)
                result=json.loads(raw)['result'];row.update(summary_file=p.name,summary_sha256=sha(p),
                    items=[dict(pmcid='PMC'+u,title=result[u]['title'],pubdate=result[u]['pubdate'],articleids=result[u].get('articleids',[])) for u in result['uids']])
        except Exception as error:row['error']=type(error).__name__+': '+str(error)
        r['responses'].append(row)
        (OUT/'attempt_01.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(row,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
