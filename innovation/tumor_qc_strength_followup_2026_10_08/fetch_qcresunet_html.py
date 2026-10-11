"""Pinned author-preprint HTML after DOI/title/author matching, not publisher version-of-record."""
import json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
import retrieve_stronger_adaptation_primary as client
def main():
    sys.stdout.reconfigure(encoding='utf-8');client.resource_guard();identity=HERE/'identity_attempt01/receipt.json'
    r=json.loads(identity.read_text(encoding='utf-8'));assert r['complete'] and not r['errors']
    cr=next(x for x in r['records'] if x['key']=='qcresunet_exact_doi')['identity']
    ar=next(x for x in r['records'] if x['key']=='qcresunet_arxiv_title')['entries'];assert len(ar)==1
    assert ar[0]['id']=='http://arxiv.org/abs/2412.07156v2'
    assert ar[0]['title'].lower()==cr['title'][0].lower()
    assert ar[0]['authors']==[a['given']+' '+a['family'] for a in cr['author']]
    out=HERE/'primary_sources_attempt01';out.mkdir(exist_ok=False);client.OUT=out
    result=client.fetch('qcresunet_arxiv_v2','https://arxiv.org/html/2412.07156v2','.html')
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    receipt=dict(complete=result['complete'],errors=result['errors'],records=[result],arxiv_title_and_all_authors_matched=True,
        pinned_arxiv_id='2412.07156v2',version_of_record_equivalence_not_asserted=True,actual_primary_maintexts_read=0,
        medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,CUDA_initialized=False,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=client.sha(p)) for p in [Path(__file__),identity,HERE/'QCRESUNET_PRIMARY_SELECTION.md',Path(client.__file__)]])
    client.dump(out/'receipt.json',receipt);print(json.dumps(receipt),flush=True);return int(not receipt['complete'])
if __name__=='__main__':raise SystemExit(main())
