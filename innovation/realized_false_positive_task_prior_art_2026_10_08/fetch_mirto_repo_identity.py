"""Inspect only the repository explicitly named by the paper; never execute author code."""
import sys,json,ssl,time,hashlib,base64,traceback
from pathlib import Path
from datetime import datetime,timezone
from urllib.request import build_opener,HTTPSHandler,ProxyHandler,Request
from urllib.parse import quote
from urllib.error import HTTPError
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'author_identity_attempt01'
sys.path.insert(0,str(ROOT/'seranet_identity_prior_art_2026_10_08'))
import query_seranet_stdlib_v3 as client

def get(key,url):
    tick=time.perf_counter();row=dict(key=key,requested_url=url,complete=False,errors=[])
    try:
        opener=build_opener(ProxyHandler({}),HTTPSHandler(context=ssl.create_default_context()),client.LimitedRedirect())
        with opener.open(Request(url,headers={'User-Agent':'MRI-innovation-literature-audit/1.0'}),timeout=30) as response:
            row.update(HTTP_status=response.status,effective_url=response.geturl())
            client.base.new(OUT/f'{key}_headers.json',dict(status=response.status,headers=dict(response.headers)))
            chunks=[];total=0
            while True:
                b=response.read(65536)
                if not b:break
                total+=len(b);assert total<=3_000_000 and time.perf_counter()-tick<=35;chunks.append(b)
            body=b''.join(chunks)
        p=OUT/f'{key}.json'
        with p.open('xb') as f:f.write(body)
        row.update(complete=True,response_binding=client.base.entry(p),data=json.loads(body))
    except HTTPError as e:
        row['HTTP_status']=e.code;row['errors'].append(str(e));p=OUT/f'{key}_error.bin'
        body=e.read(3_000_001);assert len(body)<=3_000_000
        with p.open('xb') as f:f.write(body)
        row['error_binding']=client.base.entry(p)
    except Exception as e:row['errors'].append(repr(e));row['traceback']=traceback.format_exc()
    row['elapsed_seconds']=time.perf_counter()-tick
    return row

def main():
    sys.stdout.reconfigure(encoding='utf-8');client.resource_guard();OUT.mkdir(exist_ok=False);rows=[]
    row=get('repo','https://api.github.com/repos/soumickmj/MIRTO');rows.append(row)
    if row['complete']:
        md=row['data'];assert md['full_name']=='soumickmj/MIRTO'
        tree=get('tree',md['url']+'/git/trees/'+quote(md['default_branch'],safe='')+'?recursive=1');rows.append(tree)
        if tree['complete']:
            assert not tree['data'].get('truncated',False)
            rr=[e for e in tree['data']['tree'] if e['type']=='blob' and e['path'].lower()=='readme.md'];assert len(rr)==1
            blob=get('readme_blob',rr[0]['url']);rows.append(blob)
            if blob['complete']:
                b=blob['data'];assert b['encoding']=='base64' and b['sha']==rr[0]['sha'];body=base64.b64decode(b['content'])
                assert hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest()==b['sha']
                p=OUT/'README.md.source.txt'
                with p.open('xb') as f:f.write(body)
                blob['decoded_binding']=client.base.entry(p)
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=all(r['complete'] for r in rows),errors=[e for r in rows for e in r['errors']],
        records=rows,source_bindings=[client.base.entry(p) for p in (Path(__file__),HERE/'AUTHOR_SOURCE_PLAN.md',HERE/'primary_attempt01/receipt.json')],
        resource_snapshot=client.resource_guard(),author_code_executed=False,medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0)
    client.base.new(OUT/'receipt.json',result)
    for r in rows:
        display={k:r.get(k) for k in ('key','complete','HTTP_status','errors')}
        if r['key']=='repo' and r['complete']:display['metadata']={k:r['data'].get(k) for k in ('full_name','html_url','description','default_branch','created_at','pushed_at','license')}
        if r['key']=='tree' and r['complete']:display.update(tree_sha=r['data']['sha'],tree=r['data']['tree'])
        if r['key']=='readme_blob' and r['complete']:display['decoded_binding']=r['decoded_binding']
        print(json.dumps(display,ensure_ascii=False),flush=True)
    return int(not result['complete'])
if __name__=='__main__':raise SystemExit(main())
