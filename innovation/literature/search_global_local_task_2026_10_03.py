"""Bounded discovery for task baseline competence; no novelty claims from search absence."""
import json,hashlib,sys,urllib.parse,urllib.request
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'source_cache/global_local_task_search_2026-10-03'
QUERIES=[
'"vestibular schwannoma"[Title/Abstract] AND segmentation[Title/Abstract] AND (coarse[Title/Abstract] OR cascade[Title/Abstract] OR attention[Title/Abstract] OR small[Title/Abstract])',
'(MRI[Title/Abstract] OR "magnetic resonance"[Title/Abstract]) AND segmentation[Title/Abstract] AND (patch[Title/Abstract] OR "sliding window"[Title/Abstract]) AND (normalization[Title/Abstract] OR "global context"[Title/Abstract])',
'(MRI[Title/Abstract] OR "magnetic resonance"[Title/Abstract]) AND ("small lesion"[Title/Abstract] OR "small lesions"[Title/Abstract] OR "small structures"[Title/Abstract]) AND segmentation[Title/Abstract] AND (resolution[Title/Abstract] OR sampling[Title/Abstract] OR "domain randomisation"[Title/Abstract])'
]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);opener=urllib.request.build_opener(urllib.request.ProxyHandler({}));r=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),plan_sha256=sha(ROOT/'2026-10-03_global_local_task_search_plan.md'),responses=[],scope='title/abstract discovery, not fulltext reading or novelty proof')
    for i,term in enumerate(QUERIES,1):
        row=dict(query_index=i,query=term,items=[])
        try:
            url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?'+urllib.parse.urlencode(dict(db='pmc',term='('+term+') AND ("1900/01/01"[Publication Date] : "2026/10/03"[Publication Date])',retmode='json',retmax=6,sort='relevance'));row['url']=url
            with opener.open(url,timeout=25) as response:raw=response.read(4000001);row['http_status']=response.status
            p=OUT/f'query_{i:02d}.response';p.write_bytes(raw);assert len(raw)<=4000000;a=json.loads(raw)['esearchresult'];row.update(raw_file=p.name,raw_sha256=sha(p),hit_count=int(a['count']),ids=a['idlist'])
            if a['idlist']:
                url2='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?'+urllib.parse.urlencode(dict(db='pmc',id=','.join(a['idlist']),retmode='json'));row['summary_url']=url2
                with opener.open(url2,timeout=25) as response:raw2=response.read(4000001)
                p2=OUT/f'summary_{i:02d}.response';p2.write_bytes(raw2);assert len(raw2)<=4000000;b=json.loads(raw2)['result'];row.update(summary_file=p2.name,summary_sha256=sha(p2),items=[dict(pmcid='PMC'+k,title=b[k]['title'],pubdate=b[k]['pubdate'],articleids=b[k].get('articleids',[])) for k in b['uids']])
        except Exception as e:row['error']=type(e).__name__+': '+str(e)
        r['responses'].append(row);(OUT/'attempt_01.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(row,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
