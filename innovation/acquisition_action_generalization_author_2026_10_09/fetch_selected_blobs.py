"""Read-only, Git-blob-verified fixed AMDU training sources and decoded author printout."""
import sys,ssl,time,json,gzip,urllib.request,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import resource_guard,entry,read,dump
PREFIX='nnunetv2/training/nnUNetTrainer/variants/unlearning/'
FILES=[PREFIX+'nnUNetTrainer_UnlearnBase.py',PREFIX+'models.py',PREFIX+'Unlearn/nnUNetTrainer_Unlearn.py',
    PREFIX+'Unlearn/nnUNetTrainer_UnlearnPeriodicPerBatch.py',PREFIX+'Unlearn/nnUNetTrainer_UnlearnPeriodicPerBatchKLDivConfusionLoss.py',
    'nnunetv2/training/dataloading/data_loader_unlearn.py']

def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();before=resource_guard()
    assert before['workspace_free_bytes']-11_800_000>=8_000_000_000
    source=HERE/'public_sources_attempt02/receipt.json';v=read(source);assert v['complete']
    row=next(x for x in v['records'] if x['scope']=='amdu_pinned_tree');commit=row['commit_sha']
    tree=json.loads(gzip.decompress((ROOT/row['tree_source']['source']['path']).read_bytes()));paths={x['path']:x for x in tree['tree'] if x['type']=='blob'}
    assert all(p in paths for p in FILES);out=HERE/'amdu_blobs_attempt01';out.mkdir(exist_ok=False)
    dump(out/'frozen_config.json',dict(commit_sha=commit,files=[paths[p] for p in FILES],source_bindings=[entry(Path(__file__)),entry(source),entry(HERE/'PUBLIC_SOURCE_V2_PROTOCOL.md')]))
    context=ssl.create_default_context();opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=context));records=[]
    for i,path in enumerate(FILES):
        row=dict(repo_path=path,complete=False,code_actually_read=False)
        try:
            assert time.perf_counter()-started<300;resource_guard()
            url='https://raw.githubusercontent.com/Pubec/nnunetv2-unlearning/'+commit+'/'+path
            with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRIResearchLiterature/1.0'}),timeout=25) as response:
                data=response.read(80_001);assert len(data)<=80_000;row.update(requested_url=url,effective_url=response.url,http_status=response.status)
            assert len(data)==paths[path]['size'] and hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==paths[path]['sha']
            p=out/f'file{i}.txt.gz'
            with p.open('xb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as gz:gz.write(data)
            row.update(complete=True,git_blob_SHA_verified=True,source=entry(p),uncompressed_bytes=len(data),uncompressed_sha256=hashlib.sha256(data).hexdigest())
        except Exception as exc:row['error']=dict(type=type(exc).__name__,message=str(exc))
        records.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
    result=dict(complete=all(x['complete'] for x in records),records=records,commit_sha=commit,resources_before=before,resources_after=resource_guard(),
        elapsed_seconds=time.perf_counter()-started,code_executed=False,new_maintexts_actually_read=0,publication_claim_confirmed=False,goal_status='active')
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<2_000_000
    dump(out/'receipt.json',result);return int(not result['complete'])
if __name__=='__main__':raise SystemExit(main())
