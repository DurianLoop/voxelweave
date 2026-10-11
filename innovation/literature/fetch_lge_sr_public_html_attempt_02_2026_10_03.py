"""Retrieve public PMC HTML after efetch supplied only front matter; retain both attempts."""
import hashlib,json,sys,urllib.request
from pathlib import Path
from datetime import datetime,timezone
from html.parser import HTMLParser
OUT=Path(__file__).resolve().parent/'source_cache/sparse_task_joint_fulltexts_2026-10-03'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
class Blocks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True);self.article=0;self.capture=None;self.blocks=[];self.skip=0
    def handle_starttag(self,t,attrs):
        if t=='article':self.article+=1
        if not self.article:return
        if t in ('script','style'):self.skip+=1
        if self.capture is None and t in ('h1','h2','h3','h4','p','table'):
            self.capture=dict(tag=t,text=[],depth=1)
        elif self.capture is not None and t==self.capture['tag']:self.capture['depth']+=1
        if self.capture is not None and t in ('td','th','tr','br'):self.capture['text'].append(' ')
    def handle_endtag(self,t):
        if not self.article:return
        if t in ('script','style'):self.skip=max(0,self.skip-1)
        if self.capture is not None and t==self.capture['tag']:
            self.capture['depth']-=1
            if not self.capture['depth']:
                b=self.capture;self.blocks.append(dict(tag=b['tag'],text=' '.join(''.join(b['text']).split())));self.capture=None
        if t=='article':self.article-=1
    def handle_data(self,s):
        if self.article and self.capture is not None and not self.skip:self.capture['text'].append(s)
def main():
    sys.stdout.reconfigure(encoding='utf-8');raw=OUT/'lge_sr_public_html_attempt_02.response';path=OUT/'lge_sr_public_html_attempt_02.json'
    assert not raw.exists() and not path.exists()
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),url='https://pmc.ncbi.nlm.nih.gov/articles/PMC10206514/',doi='10.1117/1.JMI.10.5.051808',pmcid='PMC10206514',script_sha256=sha(__file__),preceding_attempt='lge_sr_extra_attempt_01.json',preceding_attempt_sha256=sha(OUT/'lge_sr_extra_attempt_01.json'),failure_diagnosis='Correct DOI and article identity; efetch XML contains front matter but no body',fulltext_acquired=False,actual_reading_completed=False)
    try:
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(r['url'],timeout=30) as response:payload=response.read(12000001);r['http_status']=response.status;r['final_url']=response.url
        raw.write_bytes(payload);assert len(payload)<=12000000
        html=payload.decode('utf-8');assert r['doi'] in html
        p=Blocks();p.feed(html);blocks=p.blocks
        text='\n\n'.join('[%04d %s] %s'%(i,b['tag'],b['text']) for i,b in enumerate(blocks))
        assert len(text)>15000 and 'Discussion' in text and 'super-resolution' in text.lower()
        for name,value in [('lge_sr_html_blocks.json',json.dumps(blocks,ensure_ascii=False,indent=2)),('lge_sr_html_maintext.txt',text)]:
            dest=OUT/name;assert not dest.exists();dest.write_text(value+'\n',encoding='utf-8')
        r.update(fulltext_acquired=True,blocks=len(blocks),block_file='lge_sr_html_blocks.json',text_file='lge_sr_html_maintext.txt',block_sha256=sha(OUT/'lge_sr_html_blocks.json'),text_sha256=sha(OUT/'lge_sr_html_maintext.txt'))
    except Exception as e:r['error']=type(e).__name__+': '+str(e)
    if raw.exists():r.update(raw_file=raw.name,raw_sha256=sha(raw),bytes=raw.stat().st_size)
    path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,ensure_ascii=False))
if __name__=='__main__':main()
