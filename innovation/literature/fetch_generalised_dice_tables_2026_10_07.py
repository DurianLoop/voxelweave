"""Preserve source SVG tables and extract available text without claiming visual review."""
import hashlib,json,sys,urllib.request,xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime,timezone
OUT=Path(__file__).resolve().parent/'source_cache/dice_followup_fulltexts_2026-10-07'
FILES=['ComparisonSampleRate_Tot150617.svg','2DResults_DSC.svg','3DResults_DSC.svg']
def main():
    sys.stdout.reconfigure(encoding='utf-8');opener=urllib.request.build_opener(urllib.request.ProxyHandler({}));rows=[]
    for name in FILES:
        url='https://arxiv.org/html/1707.03237v3/'+name;row=dict(file=name,url=url,complete=False,actual_reading_completed=False,visual_review_completed=False)
        try:
            with opener.open(url,timeout=18) as response:raw=response.read(5_000_001);row['http_status']=response.status
            assert len(raw)<=5_000_000
            with (OUT/name).open('xb') as f:f.write(raw)
            root=ET.fromstring(raw);tokens=[' '.join(''.join(e.itertext()).split()) for e in root.iter() if e.tag.split('}')[-1]=='text']
            row.update(complete=True,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),text_nodes=tokens)
        except Exception as e:row['error']=type(e).__name__+': '+str(e)
        rows.append(row);print(json.dumps(row),flush=True)
    report=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),tables=rows)
    with (OUT/'table_svg_acquisition_attempt01.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
    return int(any(not r['complete'] for r in rows))
if __name__=='__main__':raise SystemExit(main())
