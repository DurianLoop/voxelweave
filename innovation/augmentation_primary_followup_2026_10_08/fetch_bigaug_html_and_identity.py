"""Alternate primary HTML and exact DOI identity; no repeated old endpoints or automatic retries."""
import sys,json,time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'sources_attempt01'
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
import retrieve_stronger_adaptation_primary as client

def main():
    sys.stdout.reconfigure(encoding='utf-8');client.resource_guard();OUT.mkdir(exist_ok=False);client.OUT=OUT
    jobs=[('bigaug_pmc_html','https://pmc.ncbi.nlm.nih.gov/articles/PMC7393676/','.html'),
        ('bigaug_exact_doi','https://api.crossref.org/works/10.1109%2FTMI.2020.2973595','.json')]
    with ThreadPoolExecutor(max_workers=2) as pool:records=list(pool.map(lambda x:client.fetch(*x),jobs))
    for r in records:
        if r['complete'] and r['key']=='bigaug_exact_doi':
            q=json.loads((ROOT/r['file']).read_text())['message']
            r['identity']={k:q.get(k) for k in ['title','DOI','author','published','URL']}
            r['identity_matches']=q['DOI'].lower()=='10.1109/tmi.2020.2973595'
    receipt=dict(complete=all(r['complete'] for r in records),errors=[e for r in records for e in r['errors']],records=records,
        primary_text_read=False,automatic_retries=False,medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,
        neural_forwards=0,author_code_executed=False,source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=client.sha(p))
            for p in [Path(__file__),HERE/'PROTOCOL.md',Path(client.__file__)]])
    client.dump(OUT/'receipt.json',receipt);print(json.dumps(receipt),flush=True);return int(not receipt['complete'])
if __name__=='__main__':raise SystemExit(main())
