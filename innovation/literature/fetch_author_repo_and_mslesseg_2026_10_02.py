"""Pin a DOI-matched author repository and fetch one official dataset body."""
from __future__ import annotations
import hashlib
import json
import sys
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parent
OUT=ROOT / 'source_cache/author_repo_and_mslesseg_2026-10-02'

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
                row.update(http_status=response.status,final_url=response.url,content_type=response.headers.get('Content-Type'))
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
        row.update(raw_file=path.name,raw_sha256=sha(path),bytes=path.stat().st_size)
    row['finished_utc']=datetime.now(timezone.utc).isoformat()
    return row

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True,exist_ok=True)
    attempt=len(list(OUT.glob('attempt_*.json')))+1
    targets=[('repo_ref','https://api.github.com/repos/midas-tum/recon_uncertainty/git/ref/heads/main'),
             ('mslesseg_jats','https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=12126551&retmode=xml')]
    with ThreadPoolExecutor(max_workers=2) as pool:
        rows=list(pool.map(lambda t:fetch(*t,attempt),targets))
    ref=rows[0]
    pinned=None
    if not ref.get('error'):
        pinned=json.loads((OUT / ref['raw_file']).read_text(encoding='utf-8'))['object']['sha']
        with ThreadPoolExecutor(max_workers=2) as pool:
            targets=[('repo_readme','https://raw.githubusercontent.com/midas-tum/recon_uncertainty/'+pinned+'/README.md'),
                     ('repo_tree','https://api.github.com/repos/midas-tum/recon_uncertainty/git/trees/'+pinned+'?recursive=1')]
            rows.extend(pool.map(lambda t:fetch(*t,attempt),targets))
    body=rows[1]
    body['article_body_obtained']=False
    if not body.get('error'):
        try:
            root=ET.parse(OUT / body['raw_file']).getroot()
            article=root if root.tag=='article' else root.find('.//article')
            if article is None or article.find('body') is None:
                raise ValueError('No primary JATS article body')
            front=article.find('front')
            ids=[(x.text or '').lower() for x in front.findall('.//article-id') if x.get('pub-id-type')=='doi']
            if '10.1038/s41597-025-05250-y' not in ids:
                raise ValueError('Dataset article DOI differs')
            title=' '.join(front.find('.//article-title').itertext())
            abstract=front.find('.//abstract')
            chunks=[{'section':'TITLE','kind':'title','text':title},
                    {'section':'ABSTRACT','kind':'abstract','text':' '.join(abstract.itertext()) if abstract is not None else ''}]
            def walk(el,context):
                if el.tag=='sec':
                    t=el.find('title')
                    if t is not None:
                        context=context+[' '.join(t.itertext())]
                if el.tag in ('p','table-wrap','fig','disp-formula'):
                    txt=' '.join(' '.join(el.itertext()).split())
                    if txt:
                        chunks.append({'section':' / '.join(context),'kind':el.tag,'text':txt})
                    return
                for child in el:
                    walk(child,context)
            walk(article.find('body'),['BODY'])
            back=article.find('back')
            if back is not None:
                for sec in back.findall('sec'):
                    walk(sec,['BACK'])
            floats=article.find('floats-group')
            if floats is not None:
                walk(floats,['FLOATS'])
            jf=OUT / f'mslesseg_attempt_{attempt:02d}_paragraphs.json'
            tf=OUT / f'mslesseg_attempt_{attempt:02d}_maintext.txt'
            jf.write_text(json.dumps(chunks,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            tf.write_text('\n\n'.join(f'[{i:03d} {p["section"]} {p["kind"]}] {p["text"]}' for i,p in enumerate(chunks))+'\n',encoding='utf-8')
            body.update(article_body_obtained=True,doi='10.1038/s41597-025-05250-y',title=title,paragraphs=len(chunks),
                        paragraph_file=jf.name,paragraph_sha256=sha(jf),maintext_file=tf.name,maintext_sha256=sha(tf),
                        body_characters=sum(len(p['text']) for p in chunks),
                        public_links=sorted(set(x.get('{http://www.w3.org/1999/xlink}href') for x in article.iter('ext-link') if x.get('{http://www.w3.org/1999/xlink}href'))))
        except Exception as exc:
            body['parse_error']=f'{type(exc).__name__}: {exc}'
    result={'attempt':attempt,'script_sha256':sha(__file__),'repo':'midas-tum/recon_uncertainty','commit':pinned,
            'code_executed':False,'patient_images_downloaded':False,'sources':rows}
    (OUT / f'attempt_{attempt:02d}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for r in rows:
        print(json.dumps(r,ensure_ascii=False))
    for r in rows:
        if r['key']=='repo_readme' and not r.get('error'):
            print((OUT / r['raw_file']).read_text(encoding='utf-8'))
        if r['key']=='repo_tree' and not r.get('error'):
            d=json.loads((OUT / r['raw_file']).read_text(encoding='utf-8'))
            print(json.dumps({'truncated':d.get('truncated'),'paths':[x['path'] for x in d.get('tree',[]) if x['type']=='blob']},ensure_ascii=False))

if __name__=='__main__':
    main()
