"""Exact DOI and title-only arXiv index acquisition; bounded public GET, no publication-result claims."""
import json,sys,xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlencode
from concurrent.futures import ThreadPoolExecutor
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
import retrieve_stronger_adaptation_primary as client

def main():
    sys.stdout.reconfigure(encoding='utf-8');client.resource_guard();out=HERE/'identity_attempt01';out.mkdir(exist_ok=False);client.OUT=out
    jobs=[('qcresunet_exact_doi','https://api.crossref.org/works/10.1016%2Fj.media.2025.103718','.json'),
        ('qcresunet_arxiv_title','https://export.arxiv.org/api/query?'+urlencode({'search_query':'ti:QCResUNet','start':0,'max_results':3}),'.xml')]
    with ThreadPoolExecutor(max_workers=2) as pool:records=list(pool.map(lambda x:client.fetch(*x),jobs))
    for r in records:
        if not r['complete']:continue
        content=(ROOT/r['file']).read_text(encoding='utf-8')
        if r['key']=='qcresunet_exact_doi':
            q=json.loads(content)['message'];assert q['DOI'].lower()=='10.1016/j.media.2025.103718'
            r['identity']={k:q.get(k) for k in ['title','DOI','author','published','URL','link','relation','license']}
        else:
            ns={'a':'http://www.w3.org/2005/Atom','o':'http://a9.com/-/spec/opensearch/1.1/'};tree=ET.fromstring(content)
            r['total_results']=tree.findtext('o:totalResults',namespaces=ns)
            r['entries']=[dict(id=e.findtext('a:id',namespaces=ns),title=' '.join(e.findtext('a:title',default='',namespaces=ns).split()),
                published=e.findtext('a:published',namespaces=ns),updated=e.findtext('a:updated',namespaces=ns),
                authors=[a.findtext('a:name',namespaces=ns) for a in e.findall('a:author',ns)],
                abstract=' '.join(e.findtext('a:summary',default='',namespaces=ns).split()),links=[x.attrib for x in e.findall('a:link',ns)])
                for e in tree.findall('a:entry',ns)]
    size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file());assert size<5_000_000
    receipt=dict(complete=all(r['complete'] for r in records),errors=[e for r in records for e in r['errors']],records=records,
        actual_primary_maintexts_read=0,automatic_retries=False,medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,
        neural_forwards=0,CUDA_initialized=False,source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=client.sha(p)) for p in
            [Path(__file__),HERE/'QCRESUNET_PRIMARY_SELECTION.md',HERE/'index_attempt01/receipt.json',Path(client.__file__)]])
    client.dump(out/'receipt.json',receipt);print(json.dumps(receipt,ensure_ascii=False),flush=True);return int(not receipt['complete'])
if __name__=='__main__':raise SystemExit(main())
