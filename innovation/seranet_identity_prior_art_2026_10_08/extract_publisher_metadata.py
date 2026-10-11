"""Extract public title/authors/abstract and linked PDF identities; do not claim full text."""
import sys,json,re
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin
from datetime import datetime,timezone
import query_seranet_stdlib_v3 as prior
HERE=Path(__file__).resolve().parent;OUT=HERE/'publisher_metadata_attempt01';base=prior.base
class Parser(HTMLParser):
    def __init__(self):super().__init__(convert_charrefs=True);self.meta={};self.links=[];self.stack=[];self.abstract=[];self.titles=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='meta' and (a.get('name','').startswith('citation_') or a.get('property') in ['og:title','og:description']):
            key=a.get('name',a.get('property'));self.meta.setdefault(key,[]).append(a.get('content',''))
        if tag=='a' and 'href' in a and ('pdf' in a['href'].casefold() or 'content' in a['href'].casefold()):
            self.links.append(dict(href=a['href'],label=a.get('aria-label','')))
        if tag not in ['meta','br','hr','input','img','link','source','wbr','area','base','embed','param','track']:
            self.stack.append((tag,a.get('id','')))
    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0]==tag:self.stack=self.stack[:i];break
    def handle_data(self,data):
        if any(t in ['script','style'] for t,k in self.stack):return
        if any(k in ['Abs1','Abs1-content'] for t,k in self.stack):self.abstract.append(data)
        if any(t=='title' for t,k in self.stack):self.titles.append(data)
def main():
    sys.stdout.reconfigure(encoding='utf-8');prior.resource_guard();p=OUT/'chapter.html';parser=Parser();parser.feed(p.read_text(encoding='utf-8'))
    abstract=' '.join(' '.join(parser.abstract).split());assert abstract and 'MRI' in abstract
    q=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],metadata=parser.meta,
        page_title=' '.join(parser.titles),abstract=abstract,
        actual_public_PDF_or_content_links=[dict(**r,absolute_url=urljoin('https://link.springer.com/chapter/10.1007/978-3-031-17247-2_6',r['href'])) for r in parser.links],
        source_bindings=[base.entry(x) for x in (Path(__file__),p,OUT/'receipt.json')],
        downloaded_HTML_is_not_full_paper_read=True,new_primary_papers_read=0,medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0)
    base.new(OUT/'extracted_metadata.json',q)
    print(json.dumps(q,ensure_ascii=False),flush=True);return 0
if __name__=='__main__':raise SystemExit(main())
