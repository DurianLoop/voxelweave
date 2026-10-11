"""Public original full-text XML and PDF routes, preserving all failed requests."""
import hashlib,json,shutil,subprocess,sys,urllib.parse,urllib.request,xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime,timezone
OUT=Path(__file__).resolve().parent/'source_cache/tile_context_alternates_2026-10-07'
PAPERS=[('exact_tile','PMC10914126'),('patch_mr_norm','PMC3892712')]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),papers=[],metadata=[],actual_reading_completed=False)
    def save():(OUT/'acquisition_attempt01.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for key,pmcid in PAPERS:
        paper=dict(key=key,pmcid=pmcid,requests=[],fulltext_acquired=False,actual_reading_completed=False)
        r['papers'].append(paper)
        for kind,url in [('xml',f'https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML'),
                         ('pdf',f'https://europepmc.org/articles/{pmcid}?pdf=render'),
                         ('oa',f'https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id={pmcid}')]:
            req=dict(kind=kind,url=url,complete=False)
            try:
                with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRI-literature-audit/1.0'}),timeout=22) as resp:
                    raw=resp.read(15_000_001);req.update(http_status=resp.status,final_url=resp.url,content_type=resp.headers.get('Content-Type'))
                assert len(raw)<=15_000_000
                path=OUT/(key+'_'+kind+'.response');path.write_bytes(raw)
                req.update(complete=True,raw_file=path.name,raw_sha256=sha(path),bytes=len(raw))
                if kind=='xml':
                    xml=ET.fromstring(raw);body=xml.find('body');assert body is not None
                    blocks=[]
                    for element in xml.iter():
                        if element.tag in ('article-title','abstract','title','p','table','ref'):
                            text=' '.join(' '.join(element.itertext()).split())
                            if text:blocks.append(dict(block=len(blocks),tag=element.tag,text=text))
                    blockfile=OUT/(key+'_blocks.json');blockfile.write_text(json.dumps(blocks,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
                    paper.update(fulltext_acquired=True,xml_file=path.name,xml_sha256=sha(path),blocks_file=blockfile.name,
                                 blocks_sha256=sha(blockfile),blocks=len(blocks))
                    figs=[dict(id=e.get('id'),text=' '.join(e.itertext()),hrefs=[g.attrib for g in e.iter('graphic')]) for e in xml.iter('fig')]
                    (OUT/(key+'_figures.json')).write_text(json.dumps(figs,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
                if kind=='pdf':
                    assert raw.startswith(b'%PDF'),'Route returned non-PDF bytes'
                    pdf=OUT/(key+'.pdf');pdf.write_bytes(raw);txt=OUT/(key+'_layout.txt')
                    run=subprocess.run([shutil.which('pdftotext'),'-layout','-enc','UTF-8',str(pdf),str(txt)],capture_output=True,timeout=35)
                    assert run.returncode==0,run.stderr
                    pages=txt.read_text(encoding='utf-8').split('\f')
                    if not pages[-1].strip():pages.pop()
                    pagefile=OUT/(key+'_pages.json');pagefile.write_text(json.dumps([dict(page=i+1,text=t) for i,t in enumerate(pages)],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
                    paper.update(pdf_acquired=True,pdf_file=pdf.name,pdf_sha256=sha(pdf),pages=len(pages),pages_file=pagefile.name,pages_sha256=sha(pagefile))
                if kind=='oa':req['links']=[e.attrib for e in ET.fromstring(raw).iter('link')]
            except Exception as e:req['error']=type(e).__name__+': '+str(e);req['complete']=False
            paper['requests'].append(req);save()
        print(json.dumps({k:paper.get(k) for k in ('key','fulltext_acquired','blocks','pdf_acquired','pages')},ensure_ascii=False),flush=True)
    for key,url in [('crossref_kernel', 'https://api.crossref.org/works?'+urllib.parse.urlencode(dict(query='kernelized instance normalization whole slide image',rows=6))),
                    ('arxiv_kernel', 'https://export.arxiv.org/api/query?'+urllib.parse.urlencode(dict(search_query='all:"kernelized" AND all:"normalization"',start=0,max_results=6)))]:
        row=dict(key=key,url=url,complete=False)
        try:
            with opener.open(url,timeout=22) as resp:raw=resp.read(5_000_001)
            path=OUT/(key+'.response');path.write_bytes(raw);assert len(raw)<=5_000_000
            row.update(complete=True,raw_file=path.name,raw_sha256=sha(path))
            if key.startswith('crossref'):
                data=json.loads(raw);row['items']=[{k:i.get(k) for k in ('title','DOI','link','URL','published')} for i in data['message']['items']]
            else:
                namespace={'a':'http://www.w3.org/2005/Atom'}
                row['items']=[dict(title=e.findtext('a:title',namespaces=namespace),id=e.findtext('a:id',namespaces=namespace),
                    summary=e.findtext('a:summary',namespaces=namespace),links=[x.attrib for x in e.findall('a:link',namespace)])
                    for e in ET.fromstring(raw).findall('a:entry',namespace)]
        except Exception as e:row['error']=type(e).__name__+': '+str(e)
        r['metadata'].append(row);save();print(json.dumps(row,ensure_ascii=False),flush=True)
    return int(not all(p['fulltext_acquired'] for p in r['papers']))
if __name__=='__main__':raise SystemExit(main())
