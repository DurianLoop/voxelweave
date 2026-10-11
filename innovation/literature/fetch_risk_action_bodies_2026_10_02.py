"""Fetch two selected primary JATS bodies and an ENSURE availability index."""
from __future__ import annotations
import hashlib
import json
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parent
OUT=ROOT / 'source_cache/risk_action_bodies_2026-10-02'
SELECT={
    'gsure_parameter_2012': ('PMC3411925', '10.1109/TIP.2012.2195015'),
    'rep2rep_2026': ('PMC13093144', '10.1002/mrm.70155'),
}

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def fetch(key,url,attempt):
    path=OUT / f'{key}_attempt_{attempt:02d}.response'
    row={'key':key,'url':url,'started_utc':datetime.now(timezone.utc).isoformat()}
    try:
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
        try:
            with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRI-literature-audit/1.0'}),timeout=30) as response:
                raw=response.read(8_000_001)
                row.update(http_status=response.status, final_url=response.url, content_type=response.headers.get('Content-Type'))
        except urllib.error.HTTPError as exc:
            raw=exc.read(8_000_001)
            row.update(http_status=exc.code,final_url=exc.url)
            path.write_bytes(raw)
            raise
        path.write_bytes(raw)
        if len(raw)>8_000_000:
            raise ValueError('Response exceeds 8 MB cap')
    except Exception as exc:
        row['error']=f'{type(exc).__name__}: {exc}'
    if path.exists():
        row.update(raw_file=path.name, raw_sha256=sha(path),bytes=path.stat().st_size)
    row['finished_utc']=datetime.now(timezone.utc).isoformat()
    return row

def extract(key,pmcid,doi,attempt):
    row=fetch(key,'https://www.ebi.ac.uk/europepmc/webservices/rest/'+pmcid+'/fullTextXML',attempt)
    row.update(pmcid=pmcid,doi=doi,article_body_obtained=False)
    if row.get('error'):
        return row
    try:
        root=ET.parse(OUT / row['raw_file']).getroot()
        body=root.find('body')
        if root.tag!='article' or body is None or not body.findall('.//p'):
            raise ValueError('No verified JATS primary article body')
        ids=[x.text for x in root.findall('.//article-id') if x.get('pub-id-type')=='doi']
        if doi.lower() not in [(x or '').lower() for x in ids]:
            raise ValueError('Article DOI differs from exact selection')
        chunks=[]
        def walk(el,context):
            if el.tag=='sec':
                title=el.find('title')
                if title is not None:
                    context=context+[' '.join(title.itertext())]
            if el.tag in ('p','table-wrap','fig','disp-formula'):
                txt=' '.join(' '.join(el.itertext()).split())
                if txt:
                    chunks.append({'section':' / '.join(context),'kind':el.tag,'text':txt})
                return
            for child in el:
                walk(child,context)
        walk(body,['BODY'])
        floats=root.find('floats-group')
        if floats is not None:
            walk(floats,['FLOATS'])
        front=root.find('front')
        front_text=' '.join(front.itertext()) if front is not None else ''
        title=root.findtext('.//article-title')
        abstract=root.find('.//abstract')
        pre=[{'section':'TITLE','kind':'title','text':title or ''},
             {'section':'ABSTRACT','kind':'abstract','text':' '.join(abstract.itertext()) if abstract is not None else ''}]
        paragraphs=pre+chunks
        jf=OUT / f'{key}_attempt_{attempt:02d}_paragraphs.json'
        tf=OUT / f'{key}_attempt_{attempt:02d}_maintext.txt'
        jf.write_text(json.dumps(paragraphs,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        tf.write_text('\n\n'.join(f'[{i:03d} {p["section"]} {p["kind"]}] {p["text"]}' for i,p in enumerate(paragraphs))+'\n',encoding='utf-8')
        row.update(article_body_obtained=True,title=title,paragraphs=len(paragraphs),
                   paragraph_file=jf.name,paragraph_sha256=sha(jf),maintext_file=tf.name,maintext_sha256=sha(tf),
                   body_characters=sum(len(p['text']) for p in chunks),
                   license_text=' '.join(x.text or '' for x in root.findall('.//license-p')),
                   front_contains_doi=doi.lower() in front_text.lower())
    except Exception as exc:
        row['parse_error']=f'{type(exc).__name__}: {exc}'
    return row

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True,exist_ok=True)
    attempt=len(list(OUT.glob('attempt_*.json')))+1
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures=[pool.submit(extract,key,*pair,attempt) for key,pair in SELECT.items()]
        futures.append(pool.submit(fetch,'ensure_openalex','https://api.openalex.org/works/https://doi.org/10.1109/ICASSP39728.2021.9414513',attempt))
        rows=[f.result() for f in futures]
    result={'attempt':attempt,'script_sha256':sha(__file__),'selected_exact_papers':SELECT,
            'metadata_only_ensure':True,'sources':rows}
    (OUT / f'attempt_{attempt:02d}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for row in rows:
        print(json.dumps(row,ensure_ascii=False))
    last=rows[-1]
    if not last.get('error'):
        d=json.loads((OUT / last['raw_file']).read_text(encoding='utf-8'))
        print(json.dumps({'ensure_title':d.get('title'),'locations':d.get('locations'),'abstract':d.get('abstract_inverted_index')},ensure_ascii=False))

if __name__=='__main__':
    main()
