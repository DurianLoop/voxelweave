"""Single exact DOI identity request; conditional single public fullTextXML request."""
import json,sys
from pathlib import Path
from urllib.parse import urlencode
import xml.etree.ElementTree as ET
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
import retrieve_stronger_adaptation_primary as client
DOI='10.3389/fnins.2020.00282'
TITLE='Analyzing the Quality and Challenges of Uncertainty Estimations for Brain Tumor Segmentation'
def guard():
    client.resource_guard()
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
def main():
    sys.stdout.reconfigure(encoding='utf-8');guard()
    out=HERE/'jungo_primary_attempt01';out.mkdir(exist_ok=False);client.OUT=out
    records=[];errors=[];identity=None
    query='DOI:"'+DOI+'"'
    r=client.fetch('exact_doi','https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urlencode(dict(query=query,format='json',pageSize=3,resultType='core')),'.json');records.append(r)
    if r['complete']:
        q=json.loads((ROOT/r['file']).read_text(encoding='utf-8'))
        found=[x for x in q.get('resultList',{}).get('result',[]) if (x.get('doi') or '').lower()==DOI]
        assert len(found)==1
        identity=found[0];assert identity['title'].rstrip('.').casefold()==TITLE.casefold()
        pmcid=identity.get('pmcid');assert pmcid and pmcid.startswith('PMC')
        f=client.fetch('fulltext','https://www.ebi.ac.uk/europepmc/webservices/rest/'+pmcid+'/fullTextXML','.xml');records.append(f)
        if f['complete']:
            xml=ET.parse(ROOT/f['file']).getroot()
            assert any(''.join(x.itertext()).strip().lower()==DOI for x in xml.findall('.//article-id'))
            assert any(''.join(x.itertext()).strip().rstrip('.').casefold()==TITLE.casefold() for x in xml.findall('.//article-title'))
    errors=[e for x in records for e in x['errors']]
    complete=len(records)==2 and all(x['complete'] for x in records)
    receipt=dict(complete=complete,errors=errors,records=records,identity=identity,actual_primary_maintexts_read=0,
        publication_claim_confirmed=False,author_code_executed=False,medical_arrays_loaded=0,neural_forwards=0,CUDA_initialized=False,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=client.sha(p)) for p in [Path(__file__),HERE/'UNCERTAINTY_PRIMARY_FOLLOWUP_PROTOCOL.md',Path(client.__file__)]])
    client.dump(out/'receipt.json',receipt);guard()
    print(json.dumps(dict(complete=complete,errors=errors,records=records,identity={k:identity.get(k) for k in ['title','doi','pmcid','id','pubYear','firstPublicationDate','authorString']} if identity else None)),flush=True)
    return int(not complete)
if __name__=='__main__':raise SystemExit(main())
