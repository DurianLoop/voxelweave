"""Alternate ordinary public article representation; preserve XML exclusion as failure."""
import hashlib,json,sys,urllib.request
from datetime import datetime,timezone
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'experiments'))
from vs_seg_task_cpu_support import resource_gate
resource_gate()
OUT=ROOT/'literature/source_cache/task_adaptation_direct_fulltexts_2026-10-03'
path=OUT/'tumorsynth_public_html_attempt_02.response';assert not path.exists()
url='https://pmc.ncbi.nlm.nih.gov/articles/PMC13036690/'
record=dict(created_utc=datetime.now(timezone.utc).isoformat(),url=url,representation='Ordinary public HTML article page',fulltext_acquired=False,actual_reading_completed=False,
            preceding_xml_failure='Publisher does not allow full text XML download via PMC EFetch; front only response retained',script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
try:
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(url,timeout=30) as resp:
        raw=resp.read(12000001);record.update(http_status=resp.status,final_url=resp.geturl(),bytes=len(raw))
    path.write_bytes(raw);record.update(raw_file=path.name,raw_sha256=hashlib.sha256(raw).hexdigest());assert len(raw)<=12000000
    from bs4 import BeautifulSoup
    soup=BeautifulSoup(raw,'html.parser');article=soup.find('article');assert article is not None
    blocks=[dict(tag=x.name,text=' '.join(x.get_text(' ',strip=True).split())) for x in article.find_all(['h1','h2','h3','p','table'])]
    text='\n\n'.join('[%04d %s] %s'%(i,x['tag'],x['text']) for i,x in enumerate(blocks))
    assert 'TumorSynth' in text and ('Materials and Methods' in text or 'Methods' in text) and '10.1148/rycan.250222' in raw.decode('utf-8',errors='replace')
    assert len(text)>15000 and 'Results' in text and 'Discussion' in text
    p=OUT/'tumorsynth_html_blocks.json';p.write_text(json.dumps(blocks,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    t=OUT/'tumorsynth_html_maintext.txt';t.write_text(text+'\n',encoding='utf-8')
    record.update(fulltext_acquired=True,blocks=len(blocks),block_file=p.name,block_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),text_file=t.name,text_sha256=hashlib.sha256(t.read_bytes()).hexdigest())
except Exception as exc:record['error']=type(exc).__name__+': '+str(exc)
(OUT/'tumorsynth_public_html_attempt_02.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))
