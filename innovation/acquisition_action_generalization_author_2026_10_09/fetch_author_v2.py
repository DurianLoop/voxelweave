"""Small Git ref replaces oversized commit patches; phrase constrained paper screen."""
import sys,ssl,time,json,gzip,urllib.request,urllib.parse,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import resource_guard,read,entry,dump
QUERIES=['TITLE_ABS:"test-time adaptation" AND (MRI OR "magnetic resonance") AND (lesion OR tumor OR tumour) AND OPEN_ACCESS:Y',
    '(TITLE_ABS:"task-driven" OR TITLE_ABS:"task-aware" OR TITLE_ABS:"selective reconstruction") AND (MRI OR "magnetic resonance") AND OPEN_ACCESS:Y',
    'TITLE_ABS:"acquisition parameters" AND (generalization OR generalisation OR uncertainty) AND OPEN_ACCESS:Y']

def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter()
    def guard():
        r=resource_guard();assert time.perf_counter()-started<300 and r['workspace_free_bytes']-11_800_000>=8_000_000_000
        assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<2_000_000;return r
    before=guard();previous=HERE/'public_sources_attempt01';old=read(previous/'receipt.json');out=HERE/'public_sources_attempt02';out.mkdir(exist_ok=False)
    phys=old['repositories'][0];assert phys['complete'];commit=phys['commit_sha']
    files=['README.md','Phys_Seg/network_architecture.py','Phys_Seg/utils.py','Phys_Seg/data_loading.py','Phys_Seg/predict_case.py']
    dump(out/'frozen_config.json',dict(Phys_Seg_commit=commit,Phys_Seg_paths=files,queries=QUERIES,previous=entry(previous/'receipt.json'),
        source_bindings=[entry(Path(__file__)),entry(HERE/'PUBLIC_SOURCE_V2_PROTOCOL.md')]))
    context=ssl.create_default_context();assert context.check_hostname and context.verify_mode==ssl.CERT_REQUIRED
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=context))
    records=[]
    def fetch(url,name,limit):
        guard()
        with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRIResearchLiterature/1.0'}),timeout=25) as response:
            data=response.read(limit+1);assert len(data)<=limit;info=dict(requested_url=url,effective_url=response.url,http_status=response.status)
        p=out/(name+'.gz')
        with p.open('xb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as z:z.write(data)
        info.update(source=entry(p),uncompressed_bytes=len(data),uncompressed_sha256=hashlib.sha256(data).hexdigest());return data,info
    for i,path in enumerate(files):
        row=dict(scope='phys_author_code',repo_path=path,complete=False,code_actually_read=False)
        try:
            data,info=fetch('https://raw.githubusercontent.com/pedrob37/Phys_Seg/'+commit+'/'+path,'phys'+str(i)+'.txt',40_000)
            tree=next(x for x in phys['text_paths'] if x['path']==path);assert len(data)==tree['size']
            assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==tree['sha']
            row.update(complete=True,commit_sha=commit,git_blob_sha_verified=True,**info)
        except Exception as exc:row['error']=dict(type=type(exc).__name__,message=str(exc))
        records.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
    row=dict(scope='amdu_pinned_tree',complete=False)
    try:
        meta=json.loads(gzip.decompress((previous/'repo1_metadata.json.gz').read_bytes()));repo=meta['full_name']
        data,ri=fetch('https://api.github.com/repos/'+repo+'/git/ref/heads/'+urllib.parse.quote(meta['default_branch'],safe=''),'amdu_ref.json',30_000)
        ref=json.loads(data);fixed=ref['object']['sha']
        data,ti=fetch('https://api.github.com/repos/'+repo+'/git/trees/'+fixed+'?recursive=1','amdu_tree.json',2_000_000)
        tree=json.loads(data);assert not tree.get('truncated')
        paths=[x for x in tree['tree'] if x['type']=='blob' and ('unlearn' in x['path'].casefold() or 'domain' in x['path'].casefold() or x['path'] in ['README.md'])]
        row.update(complete=True,commit_sha=fixed,reference=ri,tree_source=ti,related_paths=paths)
    except Exception as exc:row['error']=dict(type=type(exc).__name__,message=str(exc))
    records.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
    for i,query in enumerate(QUERIES):
        row=dict(scope='phrase_index',query=query,complete=False)
        try:
            data,info=fetch('https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode(dict(query=query,format='json',pageSize=8,resultType='core')),'query'+str(i)+'.json',400_000)
            v=json.loads(data);row.update(complete=True,hitCount=v['hitCount'],items=[{k:r.get(k) for k in ['doi','pmcid','title','firstPublicationDate','abstractText']} for r in v['resultList']['result']],**info)
        except Exception as exc:row['error']=dict(type=type(exc).__name__,message=str(exc))
        records.append(row);print(json.dumps({k:v for k,v in row.items() if k!='items'},ensure_ascii=False),flush=True)
        for hit in row.get('items',[]):print(json.dumps({k:v for k,v in hit.items() if k!='abstractText'},ensure_ascii=False),flush=True)
    result=dict(complete=all(x['complete'] for x in records),records=records,resources_before=before,resources_after=guard(),elapsed_seconds=time.perf_counter()-started,
        patient_arrays_loaded=0,patient_information_uploaded=False,code_executed=False,new_maintexts_actually_read=0,publication_claim_confirmed=False,goal_status='active')
    dump(out/'receipt.json',result);return int(not result['complete'])
if __name__=='__main__':raise SystemExit(main())
