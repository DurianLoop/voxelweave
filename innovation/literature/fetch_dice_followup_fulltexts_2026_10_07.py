"""Fetch two exact public arXiv versions and preserve separate acquisition/extraction states."""
import hashlib,json,sys,urllib.request
from pathlib import Path
from datetime import datetime,timezone
from extract_dice_region_bias_html_2026_10_07 import Blocks
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/dice_followup_fulltexts_2026-10-07'
PAPERS=[('generalised_dice','1707.03237v3','Generalised Dice'),('dice_semimetric','2303.16296v4','Dice Semimetric')]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}));rows=[]
    for name,arxiv,title in PAPERS:
        row=dict(name=name,arxiv=arxiv,url='https://arxiv.org/html/'+arxiv,complete=False,actual_reading_completed=False)
        try:
            with opener.open(row['url'],timeout=20) as response:
                raw=response.read(8_000_001);row.update(http_status=response.status,content_type=response.headers.get('Content-Type'))
            src=OUT/(name+'_html_attempt01.response');src.write_bytes(raw)
            row.update(source_file=src.name,source_sha256=sha(src),bytes=len(raw))
            assert len(raw)<=8_000_000 and b'<article' in raw and title.encode() in raw
            parser=Blocks();parser.feed(raw.decode('utf-8'));assert len(parser.blocks)>20
            bp=OUT/(name+'_blocks.json');tp=OUT/(name+'_maintext.txt')
            bp.write_text(json.dumps(parser.blocks,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            tp.write_text('\n\n'.join('[%04d %s] %s'%(b['index'],b['tag'],b['text']) for b in parser.blocks)+'\n',encoding='utf-8')
            row.update(complete=True,blocks=len(parser.blocks),block_file=bp.name,block_sha256=sha(bp),text_file=tp.name,text_sha256=sha(tp))
        except Exception as e:row['error']=type(e).__name__+': '+str(e)
        rows.append(row);report=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(Path(__file__)),
            extractor_sha256=sha(ROOT/'literature/extract_dice_region_bias_html_2026_10_07.py'),papers=rows)
        (OUT/'retrieval_and_extraction_attempt01.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(row),flush=True)
    return int(any(not r['complete'] for r in rows))
if __name__=='__main__':raise SystemExit(main())
