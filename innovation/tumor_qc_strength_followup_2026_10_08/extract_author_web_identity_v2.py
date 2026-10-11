"""Local-only parsing repair for already-downloaded public HTML, no retry and no source execution."""
import hashlib,json,re,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'augmentation_primary_followup_2026_10_08'))
from extract_bigaug_stdlib import Parser
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard();src=HERE/'author_web_attempt01/repository_page.html'
    x=Parser();x.feed(src.read_text(encoding='utf-8'));data=[n for n in x.root.walk() if n.tag=='script' and n.attrs.get('type')=='application/json' and n.attrs.get('data-target')=='react-app.embeddedData']
    assert len(data)==1;payload=json.loads(data[0].text())['payload'];repo=payload['codeViewLayoutRoute']['repo'];code=payload['codeViewRepoRoute'];ref=code['refInfo']
    assert repo['name']=='QCResUNet' and repo['ownerLogin']=='sotiraslab' and repo['public'] and not repo['private']
    assert ref['name']==repo['defaultBranch']=='main' and re.fullmatch('[0-9a-f]{40}',ref['currentOid'])
    assert payload['codeViewLayoutRoute']['refInfo']['currentOid']==ref['currentOid']
    pinned=dict(repository='sotiraslab/QCResUNet',default_branch=ref['name'],commit_sha=ref['currentOid'],
        root_items=code['tree']['items'],source='Public root HTML embedded JSON; current branch may not equal paper release')
    r=dict(complete=True,errors=[],local_only=True,additional_HTTP_GETs=0,pinned=pinned,author_code_files_read=0,
        author_code_executed=False,medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,CUDA_initialized=False,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in [Path(__file__),src,
            HERE/'AUTHOR_WEB_ATTEMPT01_FAILURE.json',HERE/'AUTHOR_WEB_ALTERNATIVE_PROTOCOL.md']])
    with (HERE/'author_web_attempt01/receipt_v2.json').open('x',encoding='utf-8') as f:json.dump(r,f,indent=2);f.write('\n')
    print(json.dumps(r),flush=True)
if __name__=='__main__':main()
