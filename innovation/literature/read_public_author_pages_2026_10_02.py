"""Ordinary public repository pages after API quota rejection; no code execution."""
from __future__ import annotations
import hashlib
import json
import re
import sys
from pathlib import Path
from html.parser import HTMLParser
from fetch_author_repo_and_mslesseg_2026_10_02 import fetch, ROOT

OUT=ROOT / 'source_cache/author_repo_and_mslesseg_2026-10-02'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    attempt=len(list(OUT.glob('public_page_attempt_*.json')))+1
    rows=[]
    pins={}
    for key,repo in [('kuestner','midas-tum/recon_uncertainty'),('mslesseg','alessiarondinella/MSLesSeg-2024')]:
        row=fetch(key+'_repo_page','https://github.com/'+repo,attempt)
        rows.append(row)
        if row.get('error'):
            continue
        html=(OUT / row['raw_file']).read_text(encoding='utf-8')
        commits=sorted(set(re.findall(r'"currentOid"\s*:\s*"([0-9a-f]{40})"',html)))
        row['current_oids_in_public_html']=commits
        if len(commits)!=1:
            row['pin_error']='Public page does not expose exactly one currentOid'
            continue
        commit=commits[0]
        pins[repo]=commit
        paths=sorted(set(re.findall(r'"path"\s*:\s*"([^"\n]+)"',html)))
        row['visible_paths']=paths
        readme=fetch(key+'_pinned_readme','https://raw.githubusercontent.com/'+repo+'/'+commit+'/README.md',attempt)
        readme.update(repo=repo,commit=commit)
        rows.append(readme)
    result={'attempt':attempt,'script_sha256':sha(__file__),'helper_sha256':sha(ROOT / 'fetch_author_repo_and_mslesseg_2026_10_02.py'),
            'public_html_pins':pins,'scope':'ordinary anonymous repository/file reads, not GitHub API retries',
            'github_api_403_not_retried':True,'sources':rows,'code_executed':False}
    (OUT / f'public_page_attempt_{attempt:02d}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for r in rows:
        print(json.dumps(r,ensure_ascii=False))
        if r['key'].endswith('pinned_readme') and not r.get('error'):
            print((OUT / r['raw_file']).read_text(encoding='utf-8'))
    p=ROOT / 'source_cache/author_material_and_ms_sources_2026-10-02/ensure_abs_attempt_01.response'
    class Strip(HTMLParser):
        def __init__(self): super().__init__(); self.parts=[]; self.ignore=0; self.links=[]
        def handle_starttag(self,tag,attrs):
            if tag in ('script','style'): self.ignore+=1
            if tag=='a':
                self.links.extend(v for k,v in attrs if k=='href')
        def handle_endtag(self,tag):
            if tag in ('script','style') and self.ignore: self.ignore-=1
        def handle_data(self,data):
            if not self.ignore and data.strip(): self.parts.append(data.strip())
    parser=Strip(); parser.feed(p.read_text(encoding='utf-8'))
    txt='\n'.join(parser.parts)
    parsed={'source_sha256':sha(p),'links_to_pdf_or_html':[x for x in parser.links if '2010.10631' in x and any(t in x for t in ['/pdf/','/html/','/abs/'])],
            'text':txt}
    (OUT / 'ensure_abs_parsed_2026-10-02.json').write_text(json.dumps(parsed,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'ensure_exact_links':parsed['links_to_pdf_or_html']},ensure_ascii=False))
    for term in ['Submission history','[v1]','[v2]','[v3]','[v4]']:
        i=txt.find(term)
        if i>=0: print(txt[max(0,i-100):i+700])

if __name__=='__main__':
    main()
