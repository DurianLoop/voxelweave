"""Identity checked public primary HTML extraction; reading is separately registered."""
import sys,json,unicodedata,time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlencode
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
import retrieve_stronger_adaptation_primary as client
sys.path.insert(0,str(ROOT/'full_support_oracle_and_vinn_followup_2026_10_08'))
from parse_vinn_html import DOM,Node
ITEMS=[('psacnn','10.1016/j.neuroimage.2019.05.033','PMC6688920'),('jointsr','10.1016/j.neuroimage.2021.118206','PMC8354427')]
def norm(s):return ' '.join(unicodedata.normalize('NFKC',s).translate(str.maketrans({'‐':'-','‑':'-','–':'-','—':'-'})).split()).rstrip('.').casefold()
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource=client.resource_guard();assert resource['workspace_free_bytes']>=8_008_000_000
    out=HERE/'primary_attempt01';out.mkdir(exist_ok=False);client.OUT=out
    jobs=[('jointsr_index','https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urlencode(dict(query='DOI:10.1016/j.neuroimage.2021.118206',format='json',pageSize=2,resultType='core')),'.json')]
    jobs.extend((key,'https://pmc.ncbi.nlm.nih.gov/articles/'+pmc+'/', '.html') for key,doi,pmc in ITEMS)
    with ThreadPoolExecutor(max_workers=3) as pool:records=list(pool.map(lambda a:client.fetch(*a),jobs))
    client.dump(out/'HTTP_RECEIPT.json',dict(complete=all(r['complete'] for r in records),records=records,errors=[e for r in records for e in r['errors']],maintexts_read=0))
    oldindex=ROOT/'synthsr_psacnn_followup_2026_10_09/index_attempt01/receipt.json';old=json.loads(oldindex.read_text(encoding='utf-8'))
    identities={e['doi']:e for r in old['records'] for e in r['entries'] if e['doi']}
    if records[0]['complete']:
        for e in json.loads((ROOT/records[0]['file']).read_text(encoding='utf-8'))['resultList']['result']:identities[e['doi']]=e
    ext=HERE/'extraction_attempt01';ext.mkdir(exist_ok=False);catalog=[];errors=[]
    for (key,doi,pmc),http in zip(ITEMS,records[1:]):
        if not http['complete']:errors.extend(http['errors']);continue
        src=ROOT/http['file'];parser=DOM();parser.feed(src.read_text(encoding='utf-8'));nodes=list(parser.root.nodes())
        meta={n.attrs.get('name'):n.attrs.get('content') for n in nodes if n.tag=='meta' and n.attrs.get('name')}
        assert meta['citation_doi'].casefold()==doi and meta['citation_pmcid']==pmc
        title=meta['citation_title'];assert norm(title)==norm(identities[doi]['title'])
        articles=[n for n in nodes if n.tag=='article'];assert len(articles)==1
        blocks=[]
        def walk(n,scope):
            if not isinstance(n,Node):return
            if n.tag in {'section','aside'}:scope=scope+[n.attrs.get('id')]
            if n.tag in {'h1','h2','h3','h4','h5','h6','p','figure','table'}:
                v=n.text()
                if v:blocks.append(dict(index=len(blocks),kind='title' if n.tag.startswith('h') else n.tag,id=n.attrs.get('id'),scope=scope,text=v))
                return
            for c in n.children:walk(c,scope)
        walk(articles[0],['article'])
        tables=[dict(id=n.attrs.get('id'),rows=[[c.text() for c in row.children if isinstance(c,Node) and c.tag in {'th','td'}] for row in n.nodes() if row.tag=='tr']) for n in articles[0].nodes() if n.tag=='table']
        client.dump(ext/(key+'_blocks.json'),blocks);client.dump(ext/(key+'_tables.json'),tables)
        catalog.append(dict(key=key,doi=doi,pmcid=pmc,title=title,meta=meta,blocks=len(blocks),characters=sum(len(v['text']) for v in blocks),tables=len(tables),
            source_binding=dict(path=http['file'],sha256=http['sha256'],bytes=http['bytes']),maintexts_actually_read=0,
            headings=[dict(index=v['index'],text=v['text'][:150]) for v in blocks if v['kind']=='title']))
    result=dict(complete=len(catalog)==2,errors=errors,records=catalog,maintexts_read=0,medical_arrays_loaded=0,neural_forwards=0,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=client.sha(p),bytes=p.stat().st_size) for p in [Path(__file__),HERE/'PROTOCOL.md',oldindex,Path(client.__file__),ROOT/'full_support_oracle_and_vinn_followup_2026_10_08/parse_vinn_html.py']])
    client.dump(ext/'receipt.json',result);assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<3_000_000
    print(json.dumps(result,ensure_ascii=False),flush=True);return int(not result['complete'])
if __name__=='__main__':raise SystemExit(main())
