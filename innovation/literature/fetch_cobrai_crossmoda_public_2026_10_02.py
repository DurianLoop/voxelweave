"""Bounded public fulltext and metadata reads, with no patient data download."""
from __future__ import annotations
import hashlib
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'source_cache/cobrai_crossmoda_public_2026-10-02'
PLAN=ROOT/'2026-10-02_cobrai_crossmoda_public_followup_plan.md'
TITLE='Deep learning for automatic segmentation of vestibular schwannoma: a retrospective study from multi-center routine MRI'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def fetch(target, attempt):
    key,kind,url=target
    row={'key':key,'kind':kind,'url':url,'started_utc':datetime.now(timezone.utc).isoformat()}
    p=OUT/f'{key}_attempt_{attempt:02d}.response'
    try:
        try:
            opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
            with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRI-public-source-audit/1.0'}),timeout=30) as response:
                raw=response.read(8_000_001)
                row.update(http_status=response.status,final_url=response.url,content_type=response.headers.get('Content-Type'))
        except urllib.error.HTTPError as exc:
            raw=exc.read(8_000_001);p.write_bytes(raw);row.update(http_status=exc.code,final_url=exc.url);raise
        p.write_bytes(raw)
        if len(raw)>8_000_000:raise ValueError('Response exceeds declared cap')
        if kind=='epmc':
            data=json.loads(raw)
            row.update(reported_total=data['hitCount'],items=[{'title':r.get('title'),'doi':r.get('doi'),'pmcid':r.get('pmcid'),'pmid':r.get('id'),'year':r.get('pubYear'),'abstract':r.get('abstractText')} for r in data['resultList']['result']])
        elif kind=='zenodo':
            data=json.loads(raw)
            row.update(record_id=data.get('id'),metadata=data.get('metadata'),access=data.get('access'),files=[{k:f.get(k) for k in ('key','size','checksum','links')} for f in data.get('files',[])])
        elif kind=='synapse':row['entity']=json.loads(raw)
        elif kind=='html':
            html=raw.decode('utf-8',errors='replace')
            row['links']=sorted(set(urllib.parse.urljoin(row['final_url'],u) for u in re.findall(r'href=[\"\x27]([^\"\x27]+)',html)))
    except Exception as exc:row['error']=f'{type(exc).__name__}: {exc}'
    if p.exists():row.update(raw_file=p.name,raw_sha256=sha(p),bytes=p.stat().st_size)
    row['finished_utc']=datetime.now(timezone.utc).isoformat()
    return row

def extract(row, doi, attempt):
    row['article_body_obtained']=False
    if row.get('error'):return
    try:
        root=ET.parse(OUT/row['raw_file']).getroot()
        a=root if root.tag=='article' else root.find('.//article')
        if a is None or a.find('body') is None:raise ValueError('No JATS article body')
        front=a.find('front')
        ids=[(x.text or '').strip().lower() for x in front.findall('.//article-id') if x.get('pub-id-type')=='doi']
        if doi.lower() not in ids:raise ValueError('Exact DOI differs')
        title=' '.join(front.find('.//article-title').itertext())
        chunks=[{'section':'TITLE','kind':'title','text':title}]
        abstract=front.find('.//abstract')
        if abstract is not None:chunks.append({'section':'ABSTRACT','kind':'abstract','text':' '.join(' '.join(abstract.itertext()).split())})
        def walk(el,context):
            if el.tag=='sec' and el.find('title') is not None:context=context+[' '.join(el.find('title').itertext())]
            if el.tag in ('p','table-wrap','fig','disp-formula','supplementary-material'):
                txt=' '.join(' '.join(el.itertext()).split())
                if txt:chunks.append({'section':' / '.join(context),'kind':el.tag,'text':txt,'id':el.get('id')})
                return
            for child in el:walk(child,context)
        for name in ('body','floats-group'):
            e=a.find(name)
            if e is not None:walk(e,[name.upper()])
        back=a.find('back')
        if back is not None:
            for e in back.findall('sec'):walk(e,['BACK'])
        stem=f'{row["key"]}_attempt_{attempt:02d}'
        jf=OUT/(stem+'_paragraphs.json');tf=OUT/(stem+'_maintext.txt')
        jf.write_text(json.dumps(chunks,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        tf.write_text('\n\n'.join(f'[{i:03d} {p["section"]} {p["kind"]}] {p["text"]}' for i,p in enumerate(chunks))+'\n',encoding='utf-8')
        row.update(article_body_obtained=True,title=title,doi=doi,paragraphs=len(chunks),body_characters=sum(len(x['text']) for x in chunks),paragraph_file=jf.name,paragraph_sha256=sha(jf),maintext_file=tf.name,maintext_sha256=sha(tf),public_links=sorted(set(x.get('{http://www.w3.org/1999/xlink}href') for x in a.iter('ext-link') if x.get('{http://www.w3.org/1999/xlink}href'))))
    except Exception as exc:row['parse_error']=f'{type(exc).__name__}: {exc}'

def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(parents=True,exist_ok=True)
    attempt=len(list(OUT.glob('attempt_*.json')))+1
    targets=[('cobrai_jats','jats','https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=12183417&retmode=xml'),
             ('kujawa_exact','epmc','https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':'TITLE:"'+TITLE+'"','format':'json','resultType':'core','pageSize':5})),
             ('crossmoda2022_dataset','html','https://crossmoda2022.grand-challenge.org/dataset/'),
             ('crossmoda2022_zenodo','zenodo','https://zenodo.org/api/records/6504722'),
             ('crossmoda2023_synapse','synapse','https://repo-prod.prod.sagebase.org/repo/v1/entity/syn51236108')]
    with ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(lambda t:fetch(t,attempt),targets))
    extract(rows[0],'10.1002/nbm.70079',attempt)
    candidates=[r for r in rows[1].get('items',[]) if r['title'] and r['title'].rstrip('.').lower()==TITLE.lower() and r['year']=='2024' and r['doi'] and r['pmcid']]
    if len(candidates)==1:
        c=candidates[0]
        r=fetch(('kujawa_jats','jats','https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id='+c['pmcid'].removeprefix('PMC')+'&retmode=xml'),attempt)
        extract(r,c['doi'],attempt);rows.append(r)
    result={'attempt':attempt,'script_sha256':sha(__file__),'plan_sha256':sha(PLAN),'scope':'public text/metadata only; no MRI pixels or labels','responses':rows}
    (OUT/f'attempt_{attempt:02d}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for r in rows:print(json.dumps({k:r.get(k) for k in ('key','http_status','reported_total','article_body_obtained','doi','paragraphs','error','parse_error')},ensure_ascii=False))
    for c in candidates:print(json.dumps(c,ensure_ascii=False))

if __name__=='__main__':main()
