"""Read one DOI-bound public primary; manuscript extraction alone is not reading."""
import sys,json,time,re,urllib.request,urllib.parse,ssl
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,dump,resource_guard
sys.path.insert(0,str(ROOT/'full_support_oracle_and_vinn_followup_2026_10_08'))
from parse_vinn_html import DOM,Node
DOI='10.1109/TMI.2018.2866692';PMC='PMC6393212';URL='https://pmc.ncbi.nlm.nih.gov/articles/'+PMC+'/'
def norm(v):return re.sub(r'[^a-z0-9]','',v.lower())
def guard():
    r=resource_guard();assert r['workspace_free_bytes']-3_000_000-2_000_000-2_000_000>=8_000_000_000
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<2_000_000
    return r
def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();guard()
    refsrc=ROOT/'pulse_sequence_and_forward_model_2026_10_09/primary_attempt02/jointsr.html'
    dom=DOM();dom.feed(refsrc.read_text(encoding='utf-8'));refs=[n for n in dom.root.nodes() if n.attrs.get('id')=='bib0030'];assert len(refs)==1
    links=[n.attrs.get('href') for n in refs[0].nodes() if n.tag=='a']
    assert 'https://doi.org/'+DOI in links and '/articles/'+PMC+'/' in links
    assert 'Medical image imputation from image collections' in refs[0].text()
    dump(HERE/'PRIMARY_SELECTION_ATTEMPT02.json',dict(complete=True,errors=[],doi=DOI,pmcid=PMC,original_citation_text=refs[0].text(),original_links=links,
        source_binding=entry(refsrc),citation_not_counted_as_reading=True,publication_claim_confirmed=False,goal_status='active'))
    out=HERE/'primary_attempt02';out.mkdir(exist_ok=False);records=[]
    items=[('imputation',URL,'html'),('index','https://www.ebi.ac.uk/europepmc/webservices/rest/search?query='+urllib.parse.quote('DOI:'+DOI)+'&format=json','json')]
    for key,url,suffix in items:
        guard();record=dict(key=key,requested_url=url,complete=False,started_utc=datetime.now(timezone.utc).isoformat())
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'MRI-literature-review/1.0','Accept':'text/html,application/json'})
            ctx=ssl.create_default_context();assert ctx.check_hostname and ctx.verify_mode==ssl.CERT_REQUIRED
            from retrieve_stronger_adaptation_primary import Redirect
            op=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ctx),Redirect())
            with op.open(req,timeout=30) as response:
                data=response.read(2_000_001);assert len(data)<=2_000_000
                assert response.status==200;record.update(HTTP_status=response.status,effective_url=response.geturl())
                headers=dict(response.headers.items())
            p=out/(key+'.'+suffix)
            with p.open('xb') as f:f.write(data)
            dump(out/(key+'_headers.json'),headers)
            record.update(complete=True,file=entry(p))
        except Exception as error:record['error']=repr(error)
        records.append(record)
        dump(out/('HTTP_'+key+'_RECEIPT.json'),record)
    dump(out/'HTTP_RECEIPT.json',dict(complete=all(v['complete'] for v in records),errors=[v.get('error') for v in records if not v['complete']],records=records))
    assert all(v['complete'] for v in records)
    htmlsrc=out/'imputation.html';dom=DOM();dom.feed(htmlsrc.read_text(encoding='utf-8'));nodes=list(dom.root.nodes())
    meta={n.attrs.get('name'):n.attrs.get('content') for n in nodes if n.tag=='meta' and n.attrs.get('name')}
    assert meta['citation_doi'].casefold()==DOI.casefold() and meta['citation_fulltext_html_url']==URL
    assert [n.attrs['href'] for n in nodes if n.tag=='link' and n.attrs.get('rel')=='canonical']==[URL]
    index=read(out/'index.json');indexed=[v for v in index['resultList']['result'] if v.get('doi','').casefold()==DOI.casefold() and v.get('pmcid')==PMC]
    assert len(indexed)==1 and norm(meta['citation_title'])==norm(indexed[0]['title'])
    bodies=[n for n in nodes if n.tag=='article'];assert len(bodies)==1;blocks=[]
    def walk(n,scope):
        if not isinstance(n,Node):return
        if n.tag in {'section','aside'}:scope=scope+[n.attrs.get('id')]
        if n.tag in {'h1','h2','h3','h4','h5','h6','p','figure','table'}:
            text=n.text()
            if text:blocks.append(dict(index=len(blocks),kind='title' if n.tag.startswith('h') else n.tag,id=n.attrs.get('id'),scope=scope,text=text))
            return
        for child in n.children:walk(child,scope)
    walk(bodies[0],['article'])
    tables=[dict(id=n.attrs.get('id'),rows=[[c.text() for c in row.children if isinstance(c,Node) and c.tag in {'td','th'}] for row in n.nodes() if row.tag=='tr']) for n in bodies[0].nodes() if n.tag=='table']
    ext=HERE/'extraction_attempt02';ext.mkdir(exist_ok=False);dump(ext/'blocks.json',blocks);dump(ext/'tables.json',tables)
    result=dict(complete=True,errors=[],doi=DOI,pmcid=PMC,title=meta['citation_title'],meta=meta,indexed=indexed[0],blocks=len(blocks),
        characters=sum(len(v['text']) for v in blocks),total_HTML_table_nodes=len(tables),maintexts_actually_read=0,
        external_supplements_read=False,figure_pixels_reviewed=False,author_code_executed=False,
        original_ref_identity_verified=True,medical_arrays_loaded=0,neural_forwards=0,publication_claim_confirmed=False,goal_status='active',
        headings=[dict(index=v['index'],text=v['text'][:180]) for v in blocks if v['kind']=='title'],
        elapsed_seconds=time.perf_counter()-started,resources=guard(),source_bindings=[entry(p) for p in [Path(__file__),HERE/'PROTOCOL.md',HERE/'NETWORK_RECOVERY_PROTOCOL.md',HERE/'fetch_and_extract_primary.py',HERE/'build_direct_https_attempt02.py',HERE/'PRIMARY_SELECTION_ATTEMPT02.json',
            out/'HTTP_RECEIPT.json',htmlsrc,out/'index.json',ROOT/'full_support_oracle_and_vinn_followup_2026_10_08/parse_vinn_html.py']])
    dump(ext/'receipt.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ['meta','indexed','source_bindings']},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
