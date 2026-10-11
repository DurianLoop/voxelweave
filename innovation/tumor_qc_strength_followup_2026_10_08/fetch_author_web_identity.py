"""One ordinary public repo page after API rate limit; only a verified embedded commit is accepted."""
import json,re,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
import retrieve_stronger_adaptation_primary as client
sys.path.insert(0,str(ROOT/'augmentation_primary_followup_2026_10_08'))
from extract_bigaug_stdlib import Parser
def main():
    sys.stdout.reconfigure(encoding='utf-8');client.resource_guard();out=HERE/'author_web_attempt01';out.mkdir(exist_ok=False);client.OUT=out
    record=client.fetch('repository_page','https://github.com/sotiraslab/QCResUNet','.html');pinned=None
    if record['complete']:
        p=ROOT/record['file'];parser=Parser();parser.feed(p.read_text(encoding='utf-8'))
        data=[n for n in parser.root.walk() if n.tag=='script' and n.attrs.get('type')=='application/json' and n.attrs.get('data-target')=='react-app.embeddedData']
        assert len(data)==1,len(data);page=json.loads(data[0].text());payload=page['payload'];repo=payload['repo']
        assert repo['name']=='QCResUNet' and repo['ownerLogin']=='sotiraslab'
        code=payload['codeViewRepoRoute'];ref=code['refInfo'];assert re.fullmatch('[0-9a-f]{40}',ref['currentOid'])
        pinned=dict(repository='sotiraslab/QCResUNet',default_branch=ref['name'],commit_sha=ref['currentOid'],
            root_items=code['tree']['items'],source='Public root HTML embedded JSON, not API commit history')
        client.dump(out/'embedded_page.json',page)
    receipt=dict(complete=record['complete'] and pinned is not None,errors=record['errors'],records=[record],pinned=pinned,
        API_rate_limit_retried=False,author_source_files_read=0,author_code_executed=False,medical_arrays_loaded=0,
        GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,CUDA_initialized=False,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=client.sha(p)) for p in [Path(__file__),HERE/'AUTHOR_WEB_ALTERNATIVE_PROTOCOL.md',HERE/'author_identity_attempt01/receipt.json',Path(client.__file__)]])
    client.dump(out/'receipt.json',receipt);assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    print(json.dumps(receipt),flush=True);return int(not receipt['complete'])
if __name__=='__main__':raise SystemExit(main())
