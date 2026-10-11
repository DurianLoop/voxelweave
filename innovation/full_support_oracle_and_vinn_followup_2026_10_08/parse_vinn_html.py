"""Standard-library DOM extraction of public PMC author text; extraction is not reading."""
import sys,re,json
from pathlib import Path
from html.parser import HTMLParser
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,entry,dump,resource_guard
VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
class Node:
    def __init__(self,tag,attrs=None):self.tag=tag;self.attrs=dict(attrs or []);self.children=[]
    def nodes(self):
        yield self
        for child in self.children:
            if isinstance(child,Node):yield from child.nodes()
    def text(self):
        if self.tag in {'script','style','noscript'}:return ''
        parts=[]
        for child in self.children:
            if isinstance(child,str):parts.append(child)
            else:parts.append(child.text())
        if self.tag=='img':parts.append(self.attrs.get('alt',''))
        return ' '.join(' '.join(parts).split())
class DOM(HTMLParser):
    def __init__(self):super().__init__(convert_charrefs=True);self.root=Node('root');self.stack=[self.root]
    def handle_starttag(self,tag,attrs):
        node=Node(tag,attrs);self.stack[-1].children.append(node)
        if tag not in VOID:self.stack.append(node)
    def handle_startendtag(self,tag,attrs):self.handle_starttag(tag,attrs);self.handle_endtag(tag)
    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,0,-1):
            if self.stack[i].tag==tag:self.stack=self.stack[:i];return
    def handle_data(self,data):self.stack[-1].children.append(data)
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard()
    receipt=read(HERE/'author_sources_attempt01/receipt.json');http=next(x for x in receipt['records'] if x['key']=='vinn_pmc_html')
    assert http['complete'] and http['HTTP_status']==200 and http['effective_url']=='https://pmc.ncbi.nlm.nih.gov/articles/PMC9801435/'
    src=ROOT/http['source_binding']['path'];parser=DOM();parser.feed(src.read_text(encoding='utf-8'));nodes=list(parser.root.nodes())
    meta={n.attrs.get('name'):n.attrs.get('content') for n in nodes if n.tag=='meta' and n.attrs.get('name')}
    assert meta['citation_doi']=='10.1016/j.neuroimage.2022.118933',meta
    title=meta['citation_title'];assert 'FastSurferVINN' in title and 'resolution' in title
    articles=[n for n in nodes if n.tag=='article'];assert len(articles)==1,len(articles)
    body=articles[0];blocks=[]
    def walk(n,scope):
        if not isinstance(n,Node):return
        if n.tag in {'section','aside'}:scope=scope+[n.attrs.get('id')]
        if n.tag in {'h1','h2','h3','h4','h5','h6','p','figure','table'}:
            v=n.text()
            if v:blocks.append(dict(index=len(blocks),kind='title' if n.tag.startswith('h') else n.tag,id=n.attrs.get('id'),scope=scope,text=v))
            return
        for child in n.children:walk(child,scope)
    walk(body,['article'])
    tables=[]
    for n in body.nodes():
        if n.tag=='table':tables.append(dict(id=n.attrs.get('id'),rows=[[c.text() for c in row.children if isinstance(c,Node) and c.tag in {'th','td'}] for row in n.nodes() if row.tag=='tr']))
    out=HERE/'vinn_html_extraction_attempt01';out.mkdir(exist_ok=False);dump(out/'blocks.json',blocks);dump(out/'tables.json',tables)
    r=dict(complete=True,errors=[],doi=meta['citation_doi'],pmcid='PMC9801435',title=title,meta=meta,blocks=len(blocks),tables=len(tables),
        primary_text_kind='public PMC HTML; author/journal version to be determined from header',actual_primary_maintexts_completed=0,
        external_supplements_read=False,figure_pixels_reviewed=False,author_code_executed=False,source_bindings=[entry(p) for p in [Path(__file__),src,HERE/'author_sources_attempt01/receipt.json']],
        headings=[dict(index=b['index'],scope=b['scope'],text=b['text'][:120]) for b in blocks if b['kind']=='title'])
    dump(out/'receipt.json',r);print(json.dumps(r,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
