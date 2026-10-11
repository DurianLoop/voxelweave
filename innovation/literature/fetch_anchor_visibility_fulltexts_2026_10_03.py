"""Bounded public JATS retrieval; separate retrieval from actual reading."""
import hashlib
import json
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'source_cache/anchor_visibility_fulltexts_2026-10-03'
PAPERS = [('ms_perceptual_2024','PMC11534588','10.3389/fnins.2024.1473132'), ('axafa_dwi_2023','PMC10963060','10.1093/europace/euad323')]
def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def text_content(elem):
    return ' '.join(''.join(elem.itertext()).split())
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(exist_ok=False)
    rows = []
    for key, pmcid, doi in PAPERS:
        path = OUT / (key + '_attempt_01.xml')
        row = dict(key=key, pmcid=pmcid, expected_doi=doi, started_utc=datetime.now(timezone.utc).isoformat(), fulltext_acquired=False, actual_reading_completed=False)
        url = 'https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=' + pmcid
        # Use the same public EFetch route previously authenticated in this project.
        url = 'https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=' + pmcid if False else 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?' + urllib.parse.urlencode(dict(db='pmc',id=pmcid[3:],rettype='full',retmode='xml'))
        row['url'] = url
        try:
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            with opener.open(urllib.request.Request(url, headers={'User-Agent':'MRI-literature-audit/1.0'}),timeout=30) as response:
                raw = response.read(12000001)
                row.update(http_status=response.status, final_url=response.url)
            path.write_bytes(raw)
            if len(raw)>12000000:
                raise ValueError('Fixed 12MB response cap exceeded')
            root = ET.fromstring(raw)
            article = root if root.tag=='article' else root.find('.//article')
            if article is None or article.find('body') is None:
                raise ValueError('No authenticated article/body')
            dois = [text_content(e) for e in article.findall('.//article-id') if e.attrib.get('pub-id-type')=='doi']
            if doi.lower() not in [x.lower() for x in dois]:
                raise ValueError('Expected DOI absent')
            body = article.find('body')
            paras = [dict(index=i, tag=e.tag, text=text_content(e)) for i,e in enumerate(body.iter()) if e.tag in ('title','p','table-wrap','fig','disp-formula')]
            floats = article.find('floats-group')
            if floats is not None:
                paras += [dict(index=len(paras)+i, tag=e.tag, text=text_content(e)) for i,e in enumerate(floats) if e.tag in ('table-wrap','fig')]
            out_text = OUT / (key + '_maintext.txt')
            out_text.write_text('\n\n'.join('[%04d %s] %s' %(i,p['tag'],p['text']) for i,p in enumerate(paras)) + '\n',encoding='utf-8')
            permissions = article.find('.//permissions')
            title = article.find('.//article-title')
            row.update(fulltext_acquired=True, title=text_content(title), dois=dois, permissions=text_content(permissions) if permissions is not None else None, paragraphs=len(paras), text_file=out_text.name, text_sha256=sha(out_text), text_extraction_warning='Flattened formula/table/figure text; visual figures and supplementary files not inspected')
        except Exception as exc:
            row['error'] = type(exc).__name__ + ': ' + str(exc)
        if path.exists():
            row.update(raw_file=path.name, raw_sha256=sha(path), bytes=path.stat().st_size)
        row['finished_utc'] = datetime.now(timezone.utc).isoformat()
        rows.append(row)
        print(json.dumps({k:row.get(k) for k in ('key','title','fulltext_acquired','paragraphs','error')}),flush=True)
    (OUT / 'attempt_01.json').write_text(json.dumps(dict(created_utc=datetime.now(timezone.utc).isoformat(), script_sha256=sha(__file__), plan_sha256=sha(ROOT/'2026-10-03_anchor_visibility_fulltext_selection.md'), papers=rows),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':
    main()
