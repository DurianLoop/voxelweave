"""Primary HTML tree/text extraction using standard library; no dependency changes or visual review."""
import json,sys,hashlib
from pathlib import Path
from html.parser import HTMLParser
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;SRC=HERE/'sources_attempt01'
VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
class Node:
    def __init__(self,tag,attrs=None,parent=None):self.tag=tag;self.attrs=dict(attrs or []);self.parent=parent;self.children=[]
    def text(self):return ' '.join(c if isinstance(c,str) else c.text() for c in self.children if isinstance(c,str) or c.tag not in ['script','style'])
    def walk(self):
        yield self
        for c in self.children:
            if isinstance(c,Node):yield from c.walk()
class Parser(HTMLParser):
    def __init__(self):super().__init__(convert_charrefs=True);self.root=Node('document');self.stack=[self.root]
    def handle_starttag(self,tag,attrs):
        n=Node(tag,attrs,self.stack[-1]);self.stack[-1].children.append(n)
        if tag not in VOID:self.stack.append(n)
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag not in VOID:self.stack.pop()
    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,0,-1):
            if self.stack[i].tag==tag:self.stack=self.stack[:i];break
    def handle_data(self,data):self.stack[-1].children.append(data)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');p=SRC/'bigaug_pmc_html.html';parser=Parser();parser.feed(p.read_text(encoding='utf-8'))
    nodes=list(parser.root.walk());metas={n.attrs.get('name'):n.attrs.get('content') for n in nodes if n.tag=='meta'}
    expected='Generalizing Deep Learning for Medical Image Segmentation to Unseen Domains via Deep Stacked Transformation'
    assert metas.get('citation_doi','').lower()=='10.1109/tmi.2020.2973595',metas
    assert metas.get('citation_title','').lower()==expected.lower(),metas.get('citation_title')
    articles=[n for n in nodes if n.tag=='article'];assert len(articles)==1,len(articles)
    blocks=[];selected={'h1','h2','h3','h4','p','figure','table','li'}
    for n in articles[0].walk():
        if n.tag not in selected:continue
        ancestor=n.parent;duplicate=False;section=[]
        while ancestor and ancestor is not articles[0]:
            if ancestor.tag in selected:duplicate=True
            if ancestor.tag=='section':section.append(ancestor.attrs.get('id'))
            ancestor=ancestor.parent
        if duplicate:continue
        text=' '.join(n.text().split())
        if text:blocks.append(dict(kind=n.tag,id=n.attrs.get('id'),section_ids=section,text=text))
    assert len(blocks)>30 and any('augmentation' in b['text'].lower() for b in blocks)
    out=HERE/'extraction_attempt01';out.mkdir(exist_ok=False)
    for name,data in [('blocks.json',blocks),('receipt.json',dict(complete=True,errors=[],identity_verified=True,citation_title=expected,
        DOI='10.1109/TMI.2020.2973595',extracted_blocks=len(blocks),actual_reading_completed=False,figure_pixels_reviewed=False,
        source_bindings=[dict(path=x.relative_to(ROOT).as_posix(),sha256=sha(x)) for x in [Path(__file__),p]]))]:
        with (out/name).open('x',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(dict(complete=True,blocks=len(blocks),catalog=[dict(index=i,kind=b['kind'],section_ids=b['section_ids'],preview=b['text'][:140]) for i,b in enumerate(blocks)]),ensure_ascii=False),flush=True)
if __name__=='__main__':main()
