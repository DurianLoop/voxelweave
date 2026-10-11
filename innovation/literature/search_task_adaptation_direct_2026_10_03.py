"""Four bounded PMC discovery queries; not a fulltext or novelty claim."""
import hashlib,json,sys,urllib.parse,urllib.request
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'source_cache/task_adaptation_direct_search_2026-10-03'
QUERIES=[
'(MRI[Title/Abstract] OR "magnetic resonance"[Title/Abstract]) AND ("super-resolution"[Title/Abstract] OR reconstruction[Title/Abstract]) AND segmentation[Title/Abstract] AND (retraining[Title/Abstract] OR adaptation[Title/Abstract] OR "training data"[Title/Abstract])',
'"super-resolution"[Title/Abstract] AND segmentation[Title/Abstract] AND ("domain shift"[Title/Abstract] OR "domain adaptation"[Title/Abstract] OR "training distribution"[Title/Abstract])',
'(MRI[Title/Abstract] OR "magnetic resonance"[Title/Abstract]) AND reconstruction[Title/Abstract] AND ("downstream task"[Title/Abstract] OR "task-based"[Title/Abstract]) AND (training[Title/Abstract] OR adaptation[Title/Abstract])',
'(MRI[Title/Abstract] OR "magnetic resonance"[Title/Abstract]) AND segmentation[Title/Abstract] AND resolution[Title/Abstract] AND (generalizability[Title/Abstract] OR robustness[Title/Abstract])'
]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);opener=urllib.request.build_opener(urllib.request.ProxyHandler({}));r=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),plan_sha256=sha(ROOT/'2026-10-03_task_adaptation_direct_search_plan.md'),responses=[],scope='Title/abstract discovery only, not new fulltexts or novelty proof')
    for i,term in enumerate(QUERIES,1):
        row=dict(query=term,query_index=i)
        try:
            row['url']='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?'+urllib.parse.urlencode(dict(db='pmc',term='('+term+') AND ("1900/01/01"[Publication Date] : "2026/10/03"[Publication Date])',retmode='json',retmax=12,sort='relevance'))
            with opener.open(row['url'],timeout=25) as response:raw=response.read(4000001);row['http_status']=response.status
            p=OUT/f'query_{i:02d}.response';p.write_bytes(raw);assert len(raw)<=4000000;z=json.loads(raw)['esearchresult'];row.update(raw_file=p.name,raw_sha256=sha(p),hit_count=int(z['count']),ids=z['idlist'])
            if z['idlist']:
                row['summary_url']='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?'+urllib.parse.urlencode(dict(db='pmc',id=','.join(z['idlist']),retmode='json'))
                with opener.open(row['summary_url'],timeout=25) as response:raw2=response.read(4000001)
                p2=OUT/f'summary_{i:02d}.response';p2.write_bytes(raw2);assert len(raw2)<=4000000;s=json.loads(raw2)['result'];row.update(summary_file=p2.name,summary_sha256=sha(p2),items=[dict(pmcid='PMC'+k,title=s[k]['title'],pubdate=s[k]['pubdate'],articleids=s[k].get('articleids',[])) for k in s['uids']])
        except Exception as exc:row['error']=type(exc).__name__+': '+str(exc)
        r['responses'].append(row);(OUT/'attempt_01.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:row.get(k) for k in ('query_index','hit_count','items','error')},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
