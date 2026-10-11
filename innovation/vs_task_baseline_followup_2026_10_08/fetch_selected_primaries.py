"""Retrieve only two identity-pinned public JATS primaries; no paper-reading claim."""
import sys,json,xml.etree.ElementTree as ET
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
import retrieve_stronger_adaptation_primary as client
ITEMS=[('clinical_vs','10.1093/jamiaopen/ooaf163','PMC12772638'),('label_preserving','10.1002/nbm.70266','PMC12983123')]
def main():
    sys.stdout.reconfigure(encoding='utf-8');client.resource_guard()
    index=HERE/'index_attempt01/receipt.json';q=json.loads(index.read_text(encoding='utf-8'));assert q['complete']
    entries={x['doi']:x for r in q['records'] for x in r['entries'] if x['doi']}
    out=HERE/'primary_attempt01';out.mkdir(exist_ok=False);client.OUT=out
    for key,doi,pmcid in ITEMS:assert entries[doi]['pmcid']==pmcid
    with ThreadPoolExecutor(max_workers=2) as pool:records=list(pool.map(lambda a:client.fetch(a[0],'https://www.ebi.ac.uk/europepmc/webservices/rest/'+a[2]+'/fullTextXML','.xml'),ITEMS))
    for a,r in zip(ITEMS,records):
        if r['complete']:
            xml=ET.parse(ROOT/r['file']).getroot();assert any(''.join(x.itertext()).strip().lower()==a[1] for x in xml.findall('.//article-id'))
            title=' '.join(''.join(xml.find('.//article-title').itertext()).split())
            assert title.rstrip('.').casefold()==' '.join(entries[a[1]]['title'].split()).rstrip('.').casefold()
            r['identity']=dict(title=title,doi=a[1],pmcid=a[2]);r['article_identity_verified']=True
    receipt=dict(complete=all(r['complete'] for r in records),errors=[e for r in records for e in r['errors']],records=records,
        actual_primary_maintexts_completed=0,medical_arrays_loaded=0,model_arrays_loaded=0,GT_arrays_loaded=0,neural_forwards=0,CUDA_initialized=False,
        publication_claim_confirmed=False,goal_status='active',source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=client.sha(p)) for p in [Path(__file__),HERE/'PRIMARY_SELECTION.md',index,Path(client.__file__)]])
    client.dump(out/'receipt.json',receipt);assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    print(json.dumps(receipt),flush=True);return int(not receipt['complete'])
if __name__=='__main__':raise SystemExit(main())
