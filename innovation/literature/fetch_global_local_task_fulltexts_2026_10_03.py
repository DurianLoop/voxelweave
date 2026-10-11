"""Acquire two selected primary JATS bodies; retain front-only failures."""
import json,hashlib,sys,urllib.parse,urllib.request,xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'source_cache/global_local_task_fulltexts_2026-10-03'
PAPERS=[('vs_cascade','PMC11903922','10.1002/lary.31979'),('olfactory','PMC8473894','10.1016/j.neuroimage.2021.118464')]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def txt(e):return ' '.join(''.join(e.itertext()).split())
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);opener=urllib.request.build_opener(urllib.request.ProxyHandler({}));records=[]
    for key,pmcid,doi in PAPERS:
        rawfile=OUT/(key+'_attempt_01.xml');r=dict(key=key,pmcid=pmcid,expected_doi=doi,fulltext_acquired=False,actual_reading_completed=False);r['url']='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?'+urllib.parse.urlencode(dict(db='pmc',id=pmcid[3:],rettype='full',retmode='xml'))
        try:
            with opener.open(r['url'],timeout=30) as response:raw=response.read(12000001);r['http_status']=response.status
            rawfile.write_bytes(raw);assert len(raw)<=12000000;tree=ET.fromstring(raw);article=tree if tree.tag=='article' else tree.find('.//article');assert article is not None and article.find('body') is not None;dois=[txt(e).lower() for e in article.findall('.//article-id') if e.get('pub-id-type')=='doi'];assert doi.lower() in dois
            blocks=[dict(tag=e.tag,text=txt(e)) for e in article.find('body').iter() if e.tag in ('title','p','table-wrap','fig','disp-formula')];floats=article.find('floats-group')
            if floats is not None:blocks.extend(dict(tag=e.tag,text=txt(e)) for e in floats if e.tag in ('fig','table-wrap'))
            bp=OUT/(key+'_blocks.json');bp.write_text(json.dumps(blocks,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');tp=OUT/(key+'_maintext.txt');tp.write_text('\n\n'.join('[%04d %s] %s'%(i,b['tag'],b['text']) for i,b in enumerate(blocks))+'\n',encoding='utf-8');r.update(fulltext_acquired=True,title=txt(article.find('.//article-title')),dois=dois,blocks=len(blocks),block_file=bp.name,block_sha256=sha(bp),text_file=tp.name,text_sha256=sha(tp))
        except Exception as e:r['error']=type(e).__name__+': '+str(e)
        if rawfile.exists():r.update(raw_file=rawfile.name,raw_sha256=sha(rawfile),bytes=rawfile.stat().st_size)
        records.append(r);manifest=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),selection_sha256=sha(ROOT/'2026-10-03_global_local_task_selection.md'),papers=records);(OUT/'attempt_01.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
