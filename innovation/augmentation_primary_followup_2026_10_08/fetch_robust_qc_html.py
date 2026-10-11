"""Acquire exactly the primary PMC article chosen from successful exact-DOI indexing."""
import sys,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
import retrieve_stronger_adaptation_primary as client

def main():
    sys.stdout.reconfigure(encoding='utf-8');client.resource_guard()
    index=HERE/'robust_qc_index_attempt01/receipt.json';r=json.loads(index.read_text(encoding='utf-8'))
    assert r['complete'] and not r['errors']
    for b in r['source_bindings']:assert client.sha(ROOT/b['path'])==b['sha256']
    e=next(x for x in r['records'] if x['key']=='robust_qc_epmc')['entries'];assert len(e)==1
    assert e[0]['doi'].lower()=='10.1073/pnas.2216399120' and e[0]['pmcid']=='PMC9992854'
    out=HERE/'robust_qc_sources_attempt01';out.mkdir(exist_ok=False);client.OUT=out
    record=client.fetch('robust_qc_pmc_html','https://pmc.ncbi.nlm.nih.gov/articles/PMC9992854/','.html')
    receipt=dict(complete=record['complete'],errors=record['errors'],records=[record],primary_text_papers_read=0,
        automatic_retries=False,author_code_executed=False,medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,
        neural_forwards=0,CUDA_initialized=False,resources=client.resource_guard(),source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=client.sha(p))
            for p in [Path(__file__),index,HERE/'ROBUST_QC_FOLLOWUP_PROTOCOL.md',Path(client.__file__)]])
    client.dump(out/'receipt.json',receipt);print(json.dumps(receipt),flush=True);return int(not receipt['complete'])
if __name__=='__main__':raise SystemExit(main())
