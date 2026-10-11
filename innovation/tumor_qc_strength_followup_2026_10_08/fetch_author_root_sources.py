"""Four selected source files at verified commit, .source.txt only; never imports authors' code."""
import json,sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
import retrieve_stronger_adaptation_primary as client
def main():
    sys.stdout.reconfigure(encoding='utf-8');client.resource_guard();identity=HERE/'author_web_attempt01/receipt_v2.json';r=json.loads(identity.read_text(encoding='utf-8'))
    assert r['complete'] and r['local_only'];commit=r['pinned']['commit_sha']
    selected=['README.md','utils.py','dataloading.py','main.py'];assert all(any(i['path']==p and i['contentType']=='file' for i in r['pinned']['root_items']) for p in selected)
    out=HERE/'author_root_sources_attempt01';out.mkdir(exist_ok=False);client.OUT=out
    jobs=[(p.replace('.','_'),'https://raw.githubusercontent.com/sotiraslab/QCResUNet/'+commit+'/'+p,'.source.txt') for p in selected]
    with ThreadPoolExecutor(max_workers=2) as pool:records=list(pool.map(lambda x:client.fetch(*x),jobs))
    for p,record in zip(selected,records):
        record['author_repository_path']=p;record['pinned_commit']=commit
        if record['complete']:assert record['bytes']<=300_000
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    receipt=dict(complete=all(r['complete'] for r in records),errors=[e for r in records for e in r['errors']],records=records,
        files_fetched=len(selected),files_actually_read=0,author_code_executed=False,automatic_retries=False,weights_downloaded=False,
        medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,CUDA_initialized=False,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=client.sha(p)) for p in [Path(__file__),identity,HERE/'AUTHOR_STATIC_AUDIT_PROTOCOL.md',Path(client.__file__)]])
    client.dump(out/'receipt.json',receipt);print(json.dumps(receipt),flush=True);return int(not receipt['complete'])
if __name__=='__main__':raise SystemExit(main())
