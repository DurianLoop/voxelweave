"""Retrieve the direct TIN citation discovered in KIN, with exact arXiv version."""
import hashlib,json,shutil,subprocess,sys,urllib.parse,urllib.request,xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime,timezone
OUT=Path(__file__).resolve().parent/'source_cache/thumbnail_instance_normalization_2026-10-07'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),actual_reading_completed=False,
           selection_reason='KIN primary PDF page 15 reference 8 directly cites fixed-thumbnail feature statistics.',
           fulltext_acquired=False,requests=[])
    def save():(OUT/'acquisition_attempt01.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    save()
    try:
        query='all:"thumbnail" AND all:"normalization"'
        url='https://export.arxiv.org/api/query?'+urllib.parse.urlencode(dict(search_query=query,start=0,max_results=5))
        with opener.open(url,timeout=22) as resp:raw=resp.read(5_000_001)
        path=OUT/'arxiv_query.response';path.write_bytes(raw);assert len(raw)<=5_000_000
        ns={'a':'http://www.w3.org/2005/Atom'}
        entries=[dict(title=e.findtext('a:title',namespaces=ns),id=e.findtext('a:id',namespaces=ns),
            summary=e.findtext('a:summary',namespaces=ns),links=[x.attrib for x in e.findall('a:link',ns)])
            for e in ET.fromstring(raw).findall('a:entry',ns)]
        r.update(search_url=url,search_file=path.name,search_sha256=sha(path),entries=entries);save()
        candidates=[e for e in entries if 'thumbnail instance normalization' in ' '.join(e['title'].lower().split())]
        assert len(candidates)==1,'Exact citation title not uniquely located'
        candidate=candidates[0];r['selected_metadata']=candidate
        pdf_url=next(x['href'] for x in candidate['links'] if x.get('title')=='pdf')
        if pdf_url.startswith('http:'):pdf_url='https:'+pdf_url[5:]
        with opener.open(pdf_url,timeout=25) as resp:raw=resp.read(15_000_001);r['pdf_final_url']=resp.url
        assert len(raw)<=15_000_000 and raw.startswith(b'%PDF');pdf=OUT/'thumbnail_instance_norm.pdf';pdf.write_bytes(raw)
        txt=OUT/'thumbnail_instance_norm_layout.txt';command=[shutil.which('pdftotext'),'-layout','-enc','UTF-8',str(pdf),str(txt)]
        result=subprocess.run(command,capture_output=True,timeout=35);assert result.returncode==0,result.stderr
        pages=txt.read_text(encoding='utf-8').split('\f')
        if not pages[-1].strip():pages.pop()
        pagefile=OUT/'thumbnail_instance_norm_pages.json';pagefile.write_text(json.dumps([dict(page=i+1,text=t) for i,t in enumerate(pages)],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        r.update(fulltext_acquired=True,pdf_url=pdf_url,pdf_file=pdf.name,pdf_sha256=sha(pdf),pages=len(pages),
                 text_file=txt.name,text_sha256=sha(txt),pages_file=pagefile.name,pages_sha256=sha(pagefile),extraction_command=command)
    except Exception as e:r['error']=type(e).__name__+': '+str(e)
    save();print(json.dumps({k:r.get(k) for k in ('fulltext_acquired','selected_metadata','pages','pdf_url','error')},ensure_ascii=False),flush=True)
    return int(not r['fulltext_acquired'])
if __name__=='__main__':raise SystemExit(main())
