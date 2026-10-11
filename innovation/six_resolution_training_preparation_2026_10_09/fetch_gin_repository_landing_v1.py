"""Inspect public institution landing pages; do not use publisher staging PDF links."""
import sys,json,gzip,ssl,time,urllib.request
from pathlib import Path
from html.parser import HTMLParser
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import entry,dump,resource_guard
out=HERE/'gin_repository_landing_attempt01';out.mkdir(exist_ok=False);started=time.perf_counter()
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ssl.create_default_context()))
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.text=[]
    def handle_starttag(self,tag,attrs):
        v=dict(attrs)
        if tag=='a' and v.get('href'):self.links.append(v['href'])
    def handle_data(self,data):
        if data.strip():self.text.append(data.strip())
r=dict(complete=False,errors=[],records=[],final_maintext_read=False,new_primary_maintexts_read=0,
       publisher_staging_url_not_requested=True,access_denial_not_bypassed=True,
       medical_data_uploaded=False,source_bindings=[entry(Path(__file__)),entry(HERE/'gin_final_source_locator_attempt01/receipt.json')])
for label,url in [('TUM','https://mediatum.ub.tum.de/1718725'),('Imperial','https://spiral.imperial.ac.uk/handle/10044/1/101099')]:
    row=dict(label=label,url=url,complete=False)
    try:
        resource_guard();assert time.perf_counter()-started<90
        with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRIResearchLiterature/1.0'}),timeout=25) as response:
            raw=response.read(150001);assert len(raw)<=150000
            row.update(http_status=response.status,effective_url=response.url)
        p=out/(label+'.html.gz');p.write_bytes(gzip.compress(raw,mtime=0));row['saved']=entry(p)
        parser=Links();parser.feed(raw.decode('utf-8',errors='replace'))
        filtered=[v for v in parser.links if any(w in v.lower() for w in ('.pdf','bitstream','download','fulltext','file/','document'))]
        text='\n'.join(parser.text);tp=out/(label+'.text.txt');tp.write_text(text,encoding='utf-8')
        row.update(complete=True,filtered_links=filtered,visible_text=entry(tp),doi_present='10.1109/tmi.2022.3224067' in text.lower(),
                   title_present='causality-inspired' in text.lower())
    except Exception as e:row['error']=dict(type=type(e).__name__,message=str(e))
    r['records'].append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
r['complete']=all(v['complete'] for v in r['records']);r['elapsed_seconds']=time.perf_counter()-started
dump(out/'receipt.json',r)
