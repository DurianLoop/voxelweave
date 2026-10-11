"""Public repo identity and default-branch commit metadata only; no source execution or git mutations."""
import json,sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
import retrieve_stronger_adaptation_primary as client
def main():
    sys.stdout.reconfigure(encoding='utf-8');client.resource_guard();out=HERE/'author_identity_attempt01';out.mkdir(exist_ok=False);client.OUT=out
    jobs=[('repository','https://api.github.com/repos/sotiraslab/QCResUNet','.json'),
        ('default_branch_commit','https://api.github.com/repos/sotiraslab/QCResUNet/commits?per_page=1','.json')]
    with ThreadPoolExecutor(max_workers=2) as pool:records=list(pool.map(lambda x:client.fetch(*x),jobs))
    pinned=None
    if all(r['complete'] for r in records):
        repo=json.loads((ROOT/records[0]['file']).read_text(encoding='utf-8'));commits=json.loads((ROOT/records[1]['file']).read_text(encoding='utf-8'))
        assert repo['full_name'].lower()=='sotiraslab/qcresunet' and not repo['private'] and len(commits)==1
        pinned=dict(repository=repo['full_name'],default_branch=repo['default_branch'],commit_sha=commits[0]['sha'],
            tree_sha=commits[0]['commit']['tree']['sha'],commit_date=commits[0]['commit']['committer']['date'],commit_url=commits[0]['html_url'])
    r=dict(complete=all(r['complete'] for r in records),errors=[e for r in records for e in r['errors']],records=records,pinned=pinned,
        author_source_files_read=0,author_code_executed=False,version_of_record_code_equivalence_not_asserted=True,
        medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,CUDA_initialized=False,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=client.sha(p)) for p in [Path(__file__),HERE/'AUTHOR_STATIC_AUDIT_PROTOCOL.md',Path(client.__file__)]])
    client.dump(out/'receipt.json',r);print(json.dumps(r),flush=True);return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
