"""Bounded public JATS retrieval; acquisition is not actual reading."""
import hashlib, json, sys, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'source_cache/resampling_order_fulltexts_2026-10-03'
PAPERS = [
    ('vinna', 'PMC11576933', '10.1162/imag_a_00180'),
    ('mri_preprocessing', 'PMC13178426', '10.21037/qims-2025-aw-2151'),
    ('stability_atlas', 'PMC13514157', '10.3390/jimaging12080392'),
]

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def content(e):
    return ' '.join(''.join(e.itertext()).split())

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(exist_ok=False)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    rows = []
    for key, pmcid, doi in PAPERS:
        path = OUT / (key + '_attempt_01.xml')
        row = dict(key=key, pmcid=pmcid, expected_doi=doi,
                   started_utc=datetime.now(timezone.utc).isoformat(),
                   fulltext_acquired=False, actual_reading_completed=False)
        row['url'] = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?' + urllib.parse.urlencode(dict(db='pmc', id=pmcid[3:], rettype='full', retmode='xml'))
        try:
            with opener.open(urllib.request.Request(row['url'], headers={'User-Agent':'MRI-literature-audit/1.0'}), timeout=30) as response:
                raw = response.read(12000001)
                row.update(http_status=response.status, final_url=response.url)
            path.write_bytes(raw)
            if len(raw)>12000000:
                raise ValueError('Fixed 12MB response cap exceeded')
            root = ET.fromstring(raw)
            article = root if root.tag=='article' else root.find('.//article')
            if article is None or article.find('body') is None:
                raise ValueError('Article/body absent')
            dois = [content(e) for e in article.findall('.//article-id') if e.attrib.get('pub-id-type')=='doi']
            if doi.lower() not in [x.lower() for x in dois]:
                raise ValueError('Expected DOI absent')
            blocks = [dict(tag=e.tag, text=content(e)) for e in article.find('body').iter() if e.tag in ('title','p','table-wrap','fig','disp-formula')]
            floats = article.find('floats-group')
            if floats is not None:
                blocks.extend(dict(tag=e.tag,text=content(e)) for e in floats if e.tag in ('table-wrap','fig'))
            p = OUT / (key + '_blocks.json')
            p.write_text(json.dumps(blocks,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            t = OUT / (key + '_maintext.txt')
            t.write_text('\n\n'.join('[%04d %s] %s'%(i,b['tag'],b['text']) for i,b in enumerate(blocks))+'\n',encoding='utf-8')
            permissions = article.find('.//permissions')
            row.update(fulltext_acquired=True, title=content(article.find('.//article-title')),
                       dois=dois, permissions=content(permissions) if permissions is not None else None,
                       blocks=len(blocks), block_file=p.name, block_sha256=sha(p), text_file=t.name, text_sha256=sha(t),
                       warning='Flattened JATS formula/table/caption; visual figures and supplementary material not inspected')
        except Exception as exc:
            row['error'] = type(exc).__name__+': '+str(exc)
        if path.exists():
            row.update(raw_file=path.name, raw_sha256=sha(path), bytes=path.stat().st_size)
        row['finished_utc'] = datetime.now(timezone.utc).isoformat()
        rows.append(row)
        (OUT/'attempt_01.json').write_text(json.dumps(dict(script_sha256=sha(__file__),plan_sha256=sha(ROOT/'2026-10-03_resampling_order_fulltext_selection.md'),papers=rows),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:row.get(k) for k in ('key','title','fulltext_acquired','blocks','error')},ensure_ascii=False),flush=True)

if __name__=='__main__':
    main()
