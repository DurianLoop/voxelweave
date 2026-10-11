"""Normal public GitHub web/raw reads after an API rate limit; never run author code."""
import sys,json,ssl,time,traceback
from pathlib import Path
from datetime import datetime,timezone
from urllib.request import build_opener,HTTPSHandler,ProxyHandler,Request
from urllib.error import HTTPError
from html.parser import HTMLParser
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'author_web_attempt01'
sys.path.insert(0,str(ROOT/'seranet_identity_prior_art_2026_10_08'))
import query_seranet_stdlib_v3 as client
class Parser(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.data=[]
    def handle_starttag(self,tag,attrs):
        if tag=='a':
            for k,v in attrs:
                if k=='href' and v:self.links.append(v)
    def handle_data(self,data):self.data.append(data)
def get(key,url,suffix):
    row=dict(key=key,requested_url=url,complete=False,errors=[]);tick=time.perf_counter()
    try:
        opener=build_opener(ProxyHandler({}),HTTPSHandler(context=ssl.create_default_context()),client.LimitedRedirect())
        with opener.open(Request(url,headers={'User-Agent':'MRI-innovation-literature-audit/1.0'}),timeout=30) as response:
            row.update(HTTP_status=response.status,effective_url=response.geturl())
            client.base.new(OUT/f'{key}_headers.json',dict(status=response.status,headers=dict(response.headers)))
            chunks=[];total=0
            while True:
                block=response.read(65536)
                if not block:break
                total+=len(block);assert total<=3_000_000 and time.perf_counter()-tick<=35;chunks.append(block)
            body=b''.join(chunks)
        p=OUT/f'{key}.{suffix}'
        with p.open('xb') as f:f.write(body)
        row.update(complete=True,response_binding=client.base.entry(p))
    except HTTPError as e:
        row.update(HTTP_status=e.code);row['errors'].append(str(e));body=e.read(3_000_001);assert len(body)<=3_000_000
        p=OUT/f'{key}_error.bin'
        with p.open('xb') as f:f.write(body)
        row['error_binding']=client.base.entry(p)
    except Exception as e:row['errors'].append(repr(e));row['traceback']=traceback.format_exc()
    row['elapsed_seconds']=time.perf_counter()-tick;return row
def main():
    sys.stdout.reconfigure(encoding='utf-8');client.base.own_priority();client.resource_guard();OUT.mkdir(exist_ok=False)
    web=get('repository_web','https://github.com/soumickmj/MIRTO','html');rows=[web];links=[]
    if web['complete']:
        parser=Parser();parser.feed((ROOT/web['response_binding']['path']).read_text(encoding='utf-8'))
        links=sorted(set(x for x in parser.links if '/soumickmj/MIRTO/blob/' in x or '/soumickmj/MIRTO/tree/' in x))
        client.base.new(OUT/'listed_links.json',dict(links=links,complete_repository_tree_verified=False))
        if any(x.endswith('/README.md') for x in links):
            rows.append(get('README','https://raw.githubusercontent.com/soumickmj/MIRTO/master/README.md','source.txt'))
    q=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=all(r['complete'] for r in rows),
        errors=[e for r in rows for e in r['errors']],records=rows,listed_file_links=links,
        source_bindings=[client.base.entry(p) for p in [Path(__file__),HERE/'VISUAL_AND_FALLBACK_PLAN.md',HERE/'author_identity_attempt01/receipt.json']],
        complete_repository_tree_verified=False,author_source_files_read=0,author_code_executed=False,
        medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,resource_snapshot=client.resource_guard())
    client.base.new(OUT/'receipt.json',q)
    print(json.dumps(dict(complete=q['complete'],records=rows,listed_file_links=links),ensure_ascii=False),flush=True)
    return int(not q['complete'])
if __name__=='__main__':raise SystemExit(main())
