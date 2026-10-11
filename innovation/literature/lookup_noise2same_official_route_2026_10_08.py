"""Use the official NeurIPS index after a 429; retain failed route rather than retry it."""
import hashlib
import json
import re
import sys
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urljoin
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/blindspot_dependence_primary_2026-10-08'


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.items=[]
        self.href=None
        self.fragments=[]
    def handle_starttag(self,tag,attrs):
        if tag=='a':
            self.href=dict(attrs).get('href')
            self.fragments=[]
    def handle_data(self,data):
        if self.href is not None:
            self.fragments.append(data)
    def handle_endtag(self,tag):
        if tag=='a' and self.href is not None:
            self.items.append(dict(href=self.href,text=' '.join(self.fragments).strip()))
            self.href=None


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    records=[]
    def get(url,name):
        with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRI-public-literature/1.0'}),timeout=30) as response:
            data=response.read(3_000_001)
            assert len(data)<=3_000_000
            row=dict(requested_url=url,final_url=response.geturl(),http_status=response.status,
                     path=(OUT/name).relative_to(ROOT).as_posix(),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
        with (OUT/name).open('xb') as f:
            f.write(data)
        records.append(row)
        return data.decode('utf-8'),row['final_url']
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],records=records,
                prior_OpenAlex_429_actual_tool_exit=1,prior_OpenAlex_429_tool_chunk='4cd0eb',
                wrong_2010_12062_PDF_retained_and_excluded=True,new_primary_papers_read=0)
    try:
        index,base=get('https://proceedings.neurips.cc/paper/2020','neurips2020_index_identity_attempt01.html')
        parser=Links()
        parser.feed(index)
        matches=[x for x in parser.items if 'Noise2Same' in x['text']]
        assert len(matches)==1,matches
        url=urljoin(base,matches[0]['href'])
        abstract,abstractbase=get(url,'noise2same_official_abstract_identity_attempt01.html')
        parser2=Links()
        parser2.feed(abstract)
        pdfs=[urljoin(abstractbase,x['href']) for x in parser2.items if x['href'].lower().endswith('.pdf')]
        result.update(complete=True,matched_title=matches[0]['text'],official_abstract_url=abstractbase,
                      actual_public_PDF_links=pdfs)
    except Exception as exc:
        result['errors'].append(type(exc).__name__+': '+str(exc))
    with (OUT/'noise2same_official_identity_attempt01.json').open('x',encoding='utf-8') as f:
        json.dump(result,f,ensure_ascii=False,indent=2)
        f.write('\n')
    print(json.dumps(result,ensure_ascii=False),flush=True)
    return int(not result['complete'])


if __name__=='__main__':
    raise SystemExit(main())
