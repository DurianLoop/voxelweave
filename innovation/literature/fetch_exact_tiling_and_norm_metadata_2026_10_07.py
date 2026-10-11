"""Adaptive primary search follows noisy hits; obtain one selected primary PDF."""
import hashlib,json,shutil,subprocess,sys,urllib.parse,urllib.request
from pathlib import Path
from datetime import datetime,timezone
OUT=Path(__file__).resolve().parent/'source_cache/tile_context_followup_2026-10-07'
QUERIES=[('instance_patch','TITLE_ABS:"instance normalization" AND (TITLE_ABS:patch OR TITLE_ABS:tile)'),
         ('patch_inconsistency','TITLE_ABS:segmentation AND (TITLE_ABS:inconsistency OR TITLE_ABS:seam) AND TITLE_ABS:patch'),
         ('kernel_instance','TITLE_ABS:"kernelized instance normalization"')]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),
           search_reason='Initial normalization query returned mostly unrelated recent papers; narrow mechanism and tiling.',
           actual_reading_completed=False,queries=[],papers=[])
    def save():(OUT/'acquisition_attempt01.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for key,query in QUERIES:
        url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode(
            dict(query=query,format='json',resultType='core',pageSize=12))
        row=dict(key=key,query=query,url=url,complete=False)
        try:
            with opener.open(url,timeout=18) as resp:raw=resp.read(5_000_001)
            path=OUT/(key+'.response');path.write_bytes(raw);assert len(raw)<=5_000_000
            data=json.loads(raw);items=data['resultList']['result']
            row.update(complete=True,hit_count=data['hitCount'],raw_file=path.name,raw_sha256=sha(path),items=[
                {k:x.get(k) for k in ('title','authorString','doi','pmcid','pubYear','fullTextUrlList','abstractText')} for x in items])
        except Exception as e:row['error']=type(e).__name__+': '+str(e)
        r['queries'].append(row);save()
        print(json.dumps(dict(key=key,hit_count=row.get('hit_count'),error=row.get('error'),
              items=[{k:x.get(k) for k in ('title','doi','pmcid','pubYear')} for x in row.get('items',[])]),ensure_ascii=False),flush=True)
    row=dict(key='exact_tile',title='Exact Tile-Based Segmentation Inference for Images Larger than GPU Memory',
             doi='10.6028/jres.126.009',url='https://nvlpubs.nist.gov/nistpubs/jres/126/jres.126.009.pdf',
             actual_reading_completed=False,fulltext_acquired=False)
    try:
        with opener.open(row['url'],timeout=30) as resp:raw=resp.read(15_000_001);row.update(http_status=resp.status,final_url=resp.url)
        assert len(raw)<=15_000_000 and raw.startswith(b'%PDF');pdf=OUT/'exact_tile.pdf';pdf.write_bytes(raw)
        txt=OUT/'exact_tile_layout.txt';command=[shutil.which('pdftotext'),'-layout','-enc','UTF-8',str(pdf),str(txt)]
        run=subprocess.run(command,capture_output=True,timeout=40);assert run.returncode==0,run.stderr
        pages=txt.read_text(encoding='utf-8').split('\f')
        if not pages[-1].strip():pages.pop()
        pagefile=OUT/'exact_tile_pages.json';pagefile.write_text(json.dumps([dict(page=i+1,text=t) for i,t in enumerate(pages)],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        row.update(fulltext_acquired=True,pdf_file=pdf.name,pdf_sha256=sha(pdf),text_file=txt.name,text_sha256=sha(txt),
                   pages=len(pages),pages_file=pagefile.name,pages_sha256=sha(pagefile),extraction_command=command)
    except Exception as e:row['error']=type(e).__name__+': '+str(e)
    r['papers'].append(row);save();print(json.dumps(row,ensure_ascii=False),flush=True)
    return int(not row['fulltext_acquired'])
if __name__=='__main__':raise SystemExit(main())
