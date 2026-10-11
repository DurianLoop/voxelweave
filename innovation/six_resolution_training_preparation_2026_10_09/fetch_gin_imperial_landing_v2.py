"""Public Imperial landing, bounded gzip artifact; retain v1 download-size failure."""
import sys,ssl,time,gzip,json,urllib.request
from pathlib import Path
from html.parser import HTMLParser
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import entry,dump,resource_guard
started=time.perf_counter();out=HERE/'gin_imperial_landing_attempt02';out.mkdir(exist_ok=False)
class PublicText(HTMLParser):
    def __init__(self):super().__init__();self.skip=0;self.text=[];self.links=[];self.meta=[]
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style'):self.skip+=1
        v=dict(attrs)
        if tag=='a' and v.get('href'):self.links.append(v['href'])
        if tag=='meta' and any('citation' in str(v.get(k,'')) for k in ('name','property')):self.meta.append(v)
    def handle_endtag(self,tag):
        if tag in ('script','style') and self.skip:self.skip-=1
    def handle_data(self,data):
        if not self.skip and data.strip():self.text.append(data.strip())
r=dict(complete=False,errors=[],final_maintext_read=False,new_primary_maintexts_read=0,medical_data_uploaded=False,
       previous150000_byte_limit_failure_retained=True,source_bindings=[entry(Path(__file__)),entry(HERE/'gin_repository_landing_attempt01/receipt.json')])
try:
    v=resource_guard();assert v['workspace_free_bytes']-44_000_000>=8_000_000_000
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ssl.create_default_context()))
    url='https://spiral.imperial.ac.uk/handle/10044/1/101099';r['requested_url']=url
    with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRIResearchLiterature/1.0'}),timeout=25) as response:
        r.update(http_status=response.status,effective_url=response.url)
        data=response.read(1_000_001);r['response_body_bytes_read']=len(data);assert len(data)<=1_000_000
    compressed=gzip.compress(data,mtime=0);assert len(compressed)<150_000
    p=out/'landing.html.gz';p.write_bytes(compressed);r['saved_html']=entry(p)
    parser=PublicText();parser.feed(data.decode('utf-8',errors='replace'));text='\n'.join(parser.text)
    p=out/'visible_text.txt';p.write_text(text,encoding='utf-8');r['visible_text']=entry(p)
    r.update(complete=True,citation_metadata=parser.meta,doi_present='10.1109/tmi.2022.3224067' in text.lower(),
             title_present='causality-inspired' in text.lower(),candidate_file_links=[v for v in parser.links if any(w in v.lower() for w in
                            ('.pdf','bitstream','download','fulltext','file/','document'))])
except Exception as e:r['errors'].append(dict(type=type(e).__name__,message=str(e)))
r['elapsed_seconds']=time.perf_counter()-started;dump(out/'receipt.json',r)
print(json.dumps(r,ensure_ascii=False),flush=True)
