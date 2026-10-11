"""Local recovery of missing optional metadata; no new network request."""
import sys,json
from pathlib import Path
from fetch_and_extract_primaries import ITEMS,norm,DOM,Node
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,dump,resource_guard
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard()
    receiptpath=HERE/'primary_attempt01/HTTP_RECEIPT.json';http=read(receiptpath);assert http['complete'] and not http['errors']
    original=ROOT/'synthsr_psacnn_followup_2026_10_09/index_attempt01/receipt.json';q=read(original)
    entries={v['doi']:v for r in q['records'] for v in r['entries'] if v['doi']}
    irec=next(r for r in http['records'] if r['key']=='jointsr_index');ipath=ROOT/irec['file'];assert sha(ipath)==irec['sha256']
    for v in read(ipath)['resultList']['result']:entries[v['doi']]=v
    ext=HERE/'extraction_attempt02';ext.mkdir(exist_ok=False);catalog=[]
    for key,doi,pmc in ITEMS:
        rec=next(r for r in http['records'] if r['key']==key);url='https://pmc.ncbi.nlm.nih.gov/articles/'+pmc+'/'
        assert rec['complete'] and rec['HTTP_status']==200 and rec['effective_url']==rec['requested_url']==url
        src=ROOT/rec['file'];assert sha(src)==rec['sha256'] and src.stat().st_size==rec['bytes']
        dom=DOM();dom.feed(src.read_text(encoding='utf-8'));nodes=list(dom.root.nodes())
        meta={n.attrs.get('name'):n.attrs.get('content') for n in nodes if n.tag=='meta' and n.attrs.get('name')}
        assert meta['citation_doi'].casefold()==doi and meta['citation_fulltext_html_url']==url
        assert [n.attrs['href'] for n in nodes if n.tag=='link' and n.attrs.get('rel')=='canonical']==[url]
        title=meta['citation_title'];assert norm(title)==norm(entries[doi]['title'])
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
        dump(ext/(key+'_blocks.json'),blocks);dump(ext/(key+'_tables.json'),tables)
        catalog.append(dict(key=key,doi=doi,pmcid=pmc,title=title,meta=meta,blocks=len(blocks),characters=sum(len(v['text']) for v in blocks),tables=len(tables),source_binding=entry(src),
            maintexts_actually_read=0,headings=[dict(index=v['index'],text=v['text'][:150]) for v in blocks if v['kind']=='title']))
    result=dict(complete=True,errors=[],records=catalog,maintexts_read=0,new_network_GETs=0,
        missing_optional_meta_not_fabricated=True,canonical_DOI_title_effective_URL_all_match=True,original_failed_extraction_retained=True,
        medical_arrays_loaded=0,neural_forwards=0,publication_claim_confirmed=False,goal_status='active',
        source_bindings=[entry(p) for p in [Path(__file__),HERE/'fetch_and_extract_primaries.py',HERE/'LOCAL_EXTRACTION_RECOVERY_PROTOCOL.md',receiptpath,original,ipath,
            ROOT/'full_support_oracle_and_vinn_followup_2026_10_08/parse_vinn_html.py',HERE/'ACTUAL_ORIGINAL_EXTRACTION_FAILED_TOOL.json']])
    dump(ext/'receipt.json',result);assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<3_000_000
    print(json.dumps(result,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
