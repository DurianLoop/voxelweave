"""Parse already saved public HTML with stdlib; no request, install or prior record edit."""
import hashlib,json,sys,re
from html.parser import HTMLParser
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent/'source_cache/task_adaptation_direct_fulltexts_2026-10-03'
sys.stdout.reconfigure(encoding='utf-8')
class ArticleBlocks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True);self.inarticle=False;self.article_depth=0;self.tags=[];self.capture=None;self.blocks=[];self.skip=0
    def handle_starttag(self,tag,attrs):
        if tag=='article':self.inarticle=True;self.article_depth+=1
        if not self.inarticle:return
        if tag in ('script','style'):self.skip+=1
        if self.capture is None and tag in ('h1','h2','h3','p','table'):
            self.capture=dict(tag=tag,text=[],depth=1)
        elif self.capture is not None and tag==self.capture['tag']:self.capture['depth']+=1
        if self.capture is not None and tag in ('td','th','tr','br'):self.capture['text'].append(' ')
    def handle_endtag(self,tag):
        if not self.inarticle:return
        if tag in ('script','style'):self.skip=max(0,self.skip-1)
        if self.capture is not None and tag==self.capture['tag']:
            self.capture['depth']-=1
            if self.capture['depth']==0:
                x=self.capture;self.blocks.append(dict(tag=x['tag'],text=' '.join(''.join(x['text']).split())));self.capture=None
        if tag=='article':self.article_depth-=1;self.inarticle=self.article_depth>0
    def handle_data(self,data):
        if self.inarticle and self.capture is not None and not self.skip:self.capture['text'].append(data)

raw=ROOT/'tumorsynth_public_html_attempt_02.response';meta=ROOT/'tumorsynth_public_html_attempt_02.json'
record=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            source_file=raw.name,source_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),preceding_attempt_file=meta.name,
            preceding_attempt_sha256=hashlib.sha256(meta.read_bytes()).hexdigest(),fulltext_acquired=False,actual_reading_completed=False,network_requests=0)
try:
    p=ArticleBlocks();p.feed(raw.read_text(encoding='utf-8'));blocks=p.blocks
    joined='\n\n'.join('[%04d %s] %s'%(i,x['tag'],x['text']) for i,x in enumerate(blocks))
    assert len(joined)>15000 and 'TumorSynth' in joined and 'Materials and Methods' in joined and 'Discussion' in joined
    assert '10.1148/rycan.250222' in raw.read_text(encoding='utf-8')
    for name,value in [('tumorsynth_html_blocks.json',json.dumps(blocks,ensure_ascii=False,indent=2)),('tumorsynth_html_maintext.txt',joined)]:
        dest=ROOT/name;assert not dest.exists();dest.write_text(value+'\n',encoding='utf-8')
    record.update(fulltext_acquired=True,blocks=len(blocks),block_file='tumorsynth_html_blocks.json',text_file='tumorsynth_html_maintext.txt')
    record.update(block_sha256=hashlib.sha256((ROOT/record['block_file']).read_bytes()).hexdigest(),text_sha256=hashlib.sha256((ROOT/record['text_file']).read_bytes()).hexdigest())
except Exception as exc:record['error']=type(exc).__name__+': '+str(exc)
path=ROOT/'tumorsynth_html_extraction_attempt_03.json';assert not path.exists();path.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))
