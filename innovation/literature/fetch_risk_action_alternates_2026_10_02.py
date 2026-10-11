"""Public EFetch alternates, with DOI-certified JATS extraction."""
from __future__ import annotations
import json
import sys
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from fetch_risk_action_bodies_2026_10_02 import fetch, sha, ROOT

OUT=ROOT / 'source_cache/risk_action_bodies_2026-10-02'
SELECT={
 'gsure_parameter_2012':('PMC3411925','10.1109/TIP.2012.2195015'),
 'ensure_2021':('PMC8323317','10.1109/ICASSP39728.2021.9414513'),
 'rep2rep_2026':('PMC13093144','10.1002/mrm.70155'),
}

def get(item,attempt):
    key,(pmcid,doi)=item
    row=fetch(key+'_efetch','https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id='+pmcid[3:]+'&retmode=xml',attempt)
    row.update(pmcid=pmcid,doi=doi,article_body_obtained=False)
    if row.get('error'):
        return row
    try:
        root=ET.parse(OUT / row['raw_file']).getroot()
        article=root if root.tag=='article' else root.find('.//article')
        if article is None or article.find('body') is None:
            raise ValueError('Response has no primary JATS article body')
        front=article.find('front')
        ids=[x.text for x in front.findall('.//article-id') if x.get('pub-id-type')=='doi']
        if doi.lower() not in [(x or '').lower() for x in ids]:
            raise ValueError('Exact DOI is not in article front')
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
        title=' '.join(front.find('.//article-title').itertext())
        abstract=front.find('.//abstract')
        chunks=[{'section':'TITLE','kind':'title','text':title},
                {'section':'ABSTRACT','kind':'abstract','text':' '.join(abstract.itertext()) if abstract is not None else ''}]
        walk(article.find('body'),['BODY'])
        floats=article.find('floats-group')
        if floats is not None:
            walk(floats,['FLOATS'])
        jf=OUT / f'{key}_efetch_attempt_{attempt:02d}_paragraphs.json'
        tf=OUT / f'{key}_efetch_attempt_{attempt:02d}_maintext.txt'
        jf.write_text(json.dumps(chunks,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        tf.write_text('\n\n'.join(f'[{i:03d} {p["section"]} {p["kind"]}] {p["text"]}' for i,p in enumerate(chunks))+'\n',encoding='utf-8')
        row.update(article_body_obtained=True,title=title,paragraphs=len(chunks),body_characters=sum(len(p['text']) for p in chunks[2:]),
                   paragraph_file=jf.name,paragraph_sha256=sha(jf),maintext_file=tf.name,maintext_sha256=sha(tf),
                   authors=[' '.join(x.itertext()) for x in front.findall('.//contrib') if x.get('contrib-type')=='author'],
                   publication_dates=[' '.join(x.itertext()) for x in front.findall('.//pub-date')],
                   license_text=[' '.join(x.itertext()) for x in front.findall('.//license')])
    except Exception as exc:
        row['parse_error']=f'{type(exc).__name__}: {exc}'
    return row

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True,exist_ok=True)
    attempt=len(list(OUT.glob('alternate_attempt_*.json')))+1
    with ThreadPoolExecutor(max_workers=3) as pool:
        rows=list(pool.map(lambda item:get(item,attempt), SELECT.items()))
    result={'attempt':attempt,'script_sha256':sha(__file__),'helper_sha256':sha(ROOT / 'fetch_risk_action_bodies_2026_10_02.py'),
            'selection_sha256':sha(ROOT / '2026-10-02_risk_action_body_selection.md'),'sources':rows}
    (OUT / f'alternate_attempt_{attempt:02d}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for r in rows:
        print(json.dumps(r,ensure_ascii=False))

if __name__=='__main__':
    main()
