"""One original open JATS clinical SR/task paper; keep text and table rows auditable."""
import hashlib,json,sys,urllib.request,xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/hcc_sr_task_primary_2026-10-07'
DOI='10.3748/wjg.v31.i34.111541';URL='https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12421388/fullTextXML'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def text(e):return ' '.join(' '.join(e.itertext()).split())
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),url=URL,doi_expected=DOI,
        fulltext_acquired=False,actual_reading_completed=False,original_figure_pixels_visually_read=False,
        selection_reason='Original clinical SR-to-task evaluation with an accessible primary body; no outcome-based selection.',actual_training_updates=0,actual_gpu_updates=0)
    try:
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(URL,timeout=25) as response:raw=response.read(5_000_001);r['http_status']=response.status
        path=OUT/'hcc_sr_task_fulltext.xml';path.write_bytes(raw);assert len(raw)<=5_000_000
        root=ET.fromstring(raw);body=root.find('body');assert body is not None
        dois=[e.text for e in root.iter('article-id') if e.get('pub-id-type')=='doi'];assert DOI in dois
        blocks=[]
        for element in root.iter():
            if element.tag not in ('article-title','abstract','title','p','table','ref'):continue
            if element.tag=='table':
                value='\n'.join(' | '.join(text(c) for c in row if c.tag in ('th','td')) for row in element.iter('tr'))
            else:value=text(element)
            if value:blocks.append(dict(block=len(blocks),tag=element.tag,text=value))
        blockfile=OUT/'hcc_sr_task_blocks.json';blockfile.write_text(json.dumps(blocks,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        figures=[dict(id=e.get('id'),text=text(e),graphics=[g.attrib for g in e.iter('graphic')]) for e in root.iter('fig')]
        (OUT/'hcc_sr_task_figures.json').write_text(json.dumps(figures,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        r.update(fulltext_acquired=True,title=root.findtext('.//article-title'),xml_file=path.name,xml_sha256=sha(path),
            blocks_file=blockfile.name,blocks_sha256=sha(blockfile),blocks=len(blocks),matched_doi=DOI,
            pub_dates=[dict(type=e.get('pub-type'),text=text(e)) for e in root.iter('pub-date')])
    except Exception as e:r['error']=type(e).__name__+': '+str(e)
    with (OUT/'acquisition_attempt01.json').open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(r,ensure_ascii=False),flush=True);return int(not r['fulltext_acquired'])
if __name__=='__main__':raise SystemExit(main())
