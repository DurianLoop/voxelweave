"""Official title search after two preserved identity failures; no guessed ID reuse."""
import hashlib,json,re,sys,urllib.parse
from datetime import datetime,timezone
from pathlib import Path
from fetch_pareto_testing_primary_2026_10_07 import get,TITLE
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/pareto_testing_official_search_2026-10-07'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],script_sha256=sha(__file__),
        reason='PMLR206 title absent; prior guessed arXiv was another paper',reading_performed=False)
    try:
        url='https://arxiv.org/search/?'+urllib.parse.urlencode(dict(query='Pareto Testing',searchtype='title',abstracts='show',order='-announced_date_first',size=50))
        data,meta=get(url,2_000_000);p=OUT/'title_search.html';p.write_bytes(data)
        r.update(url=url,response=meta,file=p.relative_to(ROOT).as_posix(),sha256=sha(p))
        text=data.decode('utf-8');blocks=re.split(r'<li\s+class="arxiv-result',text)[1:];matches=[]
        for b in blocks:
            titles=re.findall(r'<p[^>]*class="title[^>]*>(.*?)</p>',b,re.S)
            clean=[' '.join(re.sub('<[^>]*>',' ',t).split()) for t in titles]
            if any(t.casefold()==TITLE.casefold() for t in clean):
                ids=re.findall(r'https://arxiv.org/abs/(\d{4}\.\d{4,5}(?:v\d+)?)',b)
                matches.append(dict(titles=clean,official_abs_urls=sorted({'https://arxiv.org/abs/'+x for x in ids})))
        r['matches']=matches;assert len(matches)==1 and len(matches[0]['official_abs_urls'])==1,matches
        r['complete']=True
    except Exception as e:r['errors'].append(f'{type(e).__name__}: {e}')
    with (OUT/'search_attempt03.json').open('x',encoding='utf-8') as s:json.dump(r,s,ensure_ascii=False,indent=2);s.write('\n')
    print(json.dumps(r,ensure_ascii=False));return 0 if r['complete'] else 1
if __name__=='__main__':raise SystemExit(main())
