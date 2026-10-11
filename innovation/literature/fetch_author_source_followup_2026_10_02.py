"""Pinned public code, official Figshare metadata, and linked ENSURE long text."""
from __future__ import annotations
import hashlib
import json
import sys
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from html.parser import HTMLParser
from fetch_author_repo_and_mslesseg_2026_10_02 import fetch, ROOT

OUT=ROOT / 'source_cache/author_repo_and_mslesseg_2026-10-02'
K='ce0e6ede3682a6901bfdd6ddc85b44ef28e72f3a'
M='8daf9a5a59fae6740d7ef83db982f2434f3ce470'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

class ArticleText(HTMLParser):
    def __init__(self):
        super().__init__(); self.in_article=False; self.parts=[]; self.ignore=0
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='article': self.in_article=True
        if not self.in_article: return
        if tag in ('script','style'): self.ignore+=1
        if tag in ('p','h1','h2','h3','h4','li','tr','figure','div','section'):
            self.parts.append('\n')
        if tag=='math' and attrs.get('alttext'):
            self.parts.append(' [LATEX '+attrs['alttext']+'] ')
    def handle_endtag(self,tag):
        if tag=='article': self.in_article=False
        if tag in ('script','style') and self.ignore: self.ignore-=1
    def handle_data(self,data):
        if self.in_article and not self.ignore and data.strip():
            self.parts.append(data.strip()+' ')

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    attempt=len(list(OUT.glob('followup_attempt_*.json')))+1
    q=urllib.parse.urlencode({'query':'DOI:10.1109/TMI.2022.3224359','format':'json','resultType':'core','pageSize':5})
    targets=[
      ('kuestner_train','https://raw.githubusercontent.com/midas-tum/recon_uncertainty/'+K+'/experiments/train_ensemble.py'),
      ('kuestner_config_tree','https://github.com/midas-tum/recon_uncertainty/tree/'+K+'/config'),
      ('kuestner_dataset_tree','https://github.com/midas-tum/recon_uncertainty/tree/'+K+'/ensemble/dataset'),
      ('mslesseg_registration','https://raw.githubusercontent.com/alessiarondinella/MSLesSeg-2024/'+M+'/registration.py'),
      ('mslesseg_figshare','https://api.figshare.com/v2/articles/27919209'),
      ('ensure_long_html','https://arxiv.org/html/2010.10631v4'),
      ('ensure_tmi_epmc','https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+q),
    ]
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows=list(pool.map(lambda item:fetch(*item,attempt),targets))
    for r in rows:
        if r.get('error'): continue
        path=OUT / r['raw_file']
        if r['key']=='ensure_long_html':
            try:
                parser=ArticleText(); parser.feed(path.read_text(encoding='utf-8'))
                lines=[' '.join(s.split()) for s in ''.join(parser.parts).split('\n') if s.strip()]
                if len(lines)<30 or not any('ENSURE' in s for s in lines):
                    raise ValueError('No certified ENSURE long article text')
                text=OUT / f'ensure_long_attempt_{attempt:02d}_maintext.txt'
                text.write_text('\n\n'.join(f'[{i:03d}] '+s for i,s in enumerate(lines))+'\n',encoding='utf-8')
                r.update(article_text_obtained=True,text_file=text.name,text_sha256=sha(text),lines=len(lines),text_characters=sum(len(s) for s in lines),
                         scope='arXiv v4 long-paper HTML; not conference version')
            except Exception as exc:
                r.update(article_text_obtained=False,parse_error=f'{type(exc).__name__}: {exc}')
        if r['key']=='mslesseg_figshare':
            d=json.loads(path.read_text(encoding='utf-8'))
            r.update(article_id=d.get('id'),version=d.get('version'),doi=d.get('doi'),license=d.get('license'),
                     files=[{k:f.get(k) for k in ('id','name','size','download_url','computed_md5','supplied_md5')} for f in d.get('files',[])],
                     description=d.get('description'),title=d.get('title'))
        if r['key']=='ensure_tmi_epmc':
            d=json.loads(path.read_text(encoding='utf-8'))
            r.update(reported_total=d['hitCount'],items=d['resultList']['result'])
    result={'attempt':attempt,'script_sha256':sha(__file__),'helper_sha256':sha(ROOT / 'fetch_author_repo_and_mslesseg_2026_10_02.py'),
            'adaptive_plan_sha256':sha(ROOT / '2026-10-02_author_source_adaptive_followup.md'),'sources':rows,
            'public_repo_commits':{'kuestner':K,'mslesseg':M},'patient_images_downloaded':False,'foreign_code_executed':False}
    (OUT / f'followup_attempt_{attempt:02d}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for r in rows:
        print(json.dumps({k:r.get(k) for k in ('key','http_status','error','article_text_obtained','text_file','text_characters','article_id','version','doi','license','files','reported_total')},ensure_ascii=False))
        if r['key']=='ensure_tmi_epmc':
            for i in r.get('items',[]):
                print(json.dumps({k:i.get(k) for k in ('title','doi','pmcid','pubYear','authorString')},ensure_ascii=False))

if __name__=='__main__':
    main()
