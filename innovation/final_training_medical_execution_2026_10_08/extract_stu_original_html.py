"""Article-contained primary HTML blocks, including complete tables; no external packages."""
import json,sys
from html.parser import HTMLParser
from retrieve_stronger_adaptation_primary import HERE,ROOT,OUT,sha,dump,resource_guard
from pathlib import Path
class Blocks(HTMLParser):
    def __init__(self):super().__init__(convert_charrefs=True);self.article=False;self.capture=None;self.depth=0;self.parts=[];self.blocks=[];self.skip=0
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='article':self.article=True
        if not self.article:return
        if tag in ['script','style']:self.skip+=1;return
        if self.skip:return
        if self.capture:
            if tag not in ['img','br','hr','wbr','meta','link','input']:self.depth+=1
            if tag in ['td','th','tr','br']:self.parts.append(' ')
        elif tag in ['h1','h2','h3','h4','h5','h6','p','table','figure','li']:
            self.capture=tag;self.depth=1;self.parts=[]
    def handle_endtag(self,tag):
        if not self.article:return
        if self.skip:
            if tag in ['script','style']:self.skip-=1
            return
        if self.capture:
            self.depth-=1
            if self.depth==0:
                text=' '.join(''.join(self.parts).split())
                if text:self.blocks.append(dict(kind=self.capture,text=text))
                self.capture=None;self.parts=[]
        if tag=='article':self.article=False
    def handle_data(self,data):
        if self.article and self.capture and not self.skip:self.parts.append(data)
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard()
    p=OUT/'stu_original_arxiv_html.html';q=Blocks();q.feed(p.read_text(encoding='utf-8'))
    assert q.blocks and 'STU-Net' in q.blocks[0]['text'] and 'Scalable' in q.blocks[0]['text']
    assert any(x['kind']=='table' for x in q.blocks)
    target=OUT/'stu_original_arxiv_blocks.json';dump(target,q.blocks)
    dump(OUT/'stu_original_extraction_receipt.json',dict(complete=True,errors=[],blocks=len(q.blocks),
        source_file=p.relative_to(ROOT).as_posix(),source_sha256=sha(p),extracted_file=target.relative_to(ROOT).as_posix(),
        extracted_sha256=sha(target),parser_sha256=sha(Path(__file__)),actual_reading_completed=False,
        images_visually_read=False,author_code_executed=False,resource_snapshot=resource_guard()))
    print(json.dumps([dict(i=i,kind=x['kind'],prefix=x['text'][:90]) for i,x in enumerate(q.blocks)],ensure_ascii=False))
if __name__=='__main__':main()
