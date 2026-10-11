"""Standard-library arXiv text extraction with explicit inline LaTeX preservation."""
import hashlib,json,sys
from html.parser import HTMLParser
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/dice_region_bias_fulltext_2026-10-07'
class Blocks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack=[];self.blocks=[];self.active=None;self.in_article=False;self.math_depth=0
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='article':self.in_article=True
        if self.in_article and self.active is None and (tag in ('h1','h2','h3','h4','p','table','figure','li') or
                tag=='div' and 'ltx_equation' in attrs.get('class','').split()):
            self.active=dict(depth=len(self.stack),tag=tag,id=attrs.get('id'),parts=[])
        if self.active is not None and tag=='math':
            if self.math_depth==0:self.active['parts'].append(' [LaTeX: '+attrs.get('alttext','')+'] ')
            self.math_depth+=1
        if tag not in ('area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'):
            self.stack.append(tag)
    def handle_endtag(self,tag):
        if tag=='math':self.math_depth=max(0,self.math_depth-1)
        if tag in self.stack:
            pos=len(self.stack)-1-self.stack[::-1].index(tag)
            if self.active is not None and self.active['depth']==pos:
                row=self.active;value=' '.join(''.join(row['parts']).split())
                if value:self.blocks.append(dict(index=len(self.blocks),tag=row['tag'],id=row['id'],text=value))
                self.active=None
            del self.stack[pos:]
        if tag=='article':self.in_article=False
    def handle_data(self,data):
        if self.active is not None and self.math_depth==0:self.active['parts'].append(data)

def main():
    sys.stdout.reconfigure(encoding='utf-8');src=OUT/'html_v4_attempt01.response'
    parser=Blocks();parser.feed(src.read_text(encoding='utf-8'));assert len(parser.blocks)>100
    path=OUT/'blocks.json';txt=OUT/'maintext.txt';assert not path.exists() and not txt.exists()
    path.write_text(json.dumps(parser.blocks,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    txt.write_text('\n\n'.join('[%04d %s] %s'%(b['index'],b['tag'],b['text']) for b in parser.blocks)+'\n',encoding='utf-8')
    row=dict(created_utc=datetime.now(timezone.utc).isoformat(),actual_reading_completed=False,blocks=len(parser.blocks),
             characters=sum(len(b['text']) for b in parser.blocks),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),
             script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             block_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),text_sha256=hashlib.sha256(txt.read_bytes()).hexdigest(),
             extraction='HTMLParser; table/figure grouped; math alttext preserved; no figure pixel review')
    (OUT/'extraction_attempt01.json').write_text(json.dumps(row,indent=2)+'\n',encoding='utf-8');print(json.dumps(row))
if __name__=='__main__':main()
