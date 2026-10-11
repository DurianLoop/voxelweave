"""Additional direct SR primary paper after joint-scar title proved to mean two tasks."""
import hashlib,json,sys,urllib.request,urllib.parse,xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'source_cache/sparse_task_joint_fulltexts_2026-10-03'
sys.stdout.reconfigure(encoding='utf-8')
def txt(e):return ' '.join(''.join(e.itertext()).split())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?'+urllib.parse.urlencode(dict(db='pmc',id='10206514',rettype='full',retmode='xml'))
r=dict(created_utc=datetime.now(timezone.utc).isoformat(),key='lge_sr',pmcid='PMC10206514',doi='10.1117/1.JMI.10.5.051808',url=url,script_sha256=sha(Path(__file__)),fulltext_acquired=False,actual_reading_completed=False,selection_reason='Joint-scar paper concerns two segmenters, not SR; this direct LGE SR paper is an adaptive follow-up from query2')
raw=OUT/'lge_sr_attempt_01.xml';assert not raw.exists()
try:
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(url,timeout=30) as response:payload=response.read(12000001);r['http_status']=response.status
    raw.write_bytes(payload);assert len(payload)<=12000000;tree=ET.fromstring(payload);article=tree if tree.tag=='article' else tree.find('.//article');assert article is not None and article.find('body') is not None
    dois=[txt(e).lower() for e in article.findall('.//article-id') if e.get('pub-id-type')=='doi'];assert r['doi'].lower() in dois
    blocks=[dict(tag=e.tag,text=txt(e)) for e in article.find('body').iter() if e.tag in ('title','p','table-wrap','fig','disp-formula')]
    floating=article.find('floats-group')
    if floating is not None:blocks += [dict(tag=e.tag,text=txt(e)) for e in floating if e.tag in ('fig','table-wrap')]
    bp=OUT/'lge_sr_blocks.json';bp.write_text(json.dumps(blocks,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    tp=OUT/'lge_sr_maintext.txt';tp.write_text('\n\n'.join('[%04d %s] %s'%(i,x['tag'],x['text']) for i,x in enumerate(blocks))+'\n',encoding='utf-8')
    r.update(fulltext_acquired=True,title=txt(article.find('.//article-title')),blocks=len(blocks),block_file=bp.name,block_sha256=sha(bp),text_file=tp.name,text_sha256=sha(tp))
except Exception as exc:r['error']=type(exc).__name__+': '+str(exc)
if raw.exists():r.update(raw_file=raw.name,raw_sha256=sha(raw),bytes=raw.stat().st_size)
(OUT/'lge_sr_extra_attempt_01.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,ensure_ascii=False))
