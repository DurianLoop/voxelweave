"""One new public HTML attempt; preserve failed earlier BioC attempt."""
import sys,time,ssl,json
from pathlib import Path
from urllib.request import Request,build_opener,ProxyHandler,HTTPSHandler
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import entry,dump,resource_guard
from fetch_author_text_alternatives import Redirect
from parse_vinn_html import DOM,Node
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard();started=time.perf_counter()
    out=HERE/'lesion_html_attempt01';out.mkdir(exist_ok=False)
    r=dict(complete=False,errors=[],requested_url='https://pmc.ncbi.nlm.nih.gov/articles/PMC13148016/',
        actual_primary_maintexts_completed=0,images_reviewed=False,author_code_executed=False,medical_arrays_loaded=0,GT_arrays_loaded=0,CUDA_initialized=False)
    sources=[Path(__file__),HERE/'LESION_ENSEMBLE_HTML_PROTOCOL.md',HERE/'parse_vinn_html.py',HERE/'fetch_author_text_alternatives.py']
    try:
        ctx=ssl.create_default_context();assert ctx.check_hostname and ctx.verify_mode==ssl.CERT_REQUIRED
        op=build_opener(ProxyHandler({}),HTTPSHandler(context=ctx),Redirect())
        with op.open(Request(r['requested_url'],headers={'User-Agent':'MRI-primary-research/1.0'}),timeout=30) as response:
            r.update(HTTP_status=response.status,effective_url=response.geturl())
            content=response.read(500001);assert len(content)<=500000
            dump(out/'headers.json',dict(status=response.status,headers=dict(response.headers)))
        src=out/'source.html'
        with src.open('xb') as f:f.write(content)
        sources.append(src);r['source_binding']=entry(src)
        parser=DOM();parser.feed(content.decode('utf-8'));nodes=list(parser.root.nodes())
        meta={n.attrs.get('name'):n.attrs.get('content') for n in nodes if n.tag=='meta' and n.attrs.get('name')}
        r['meta']=meta;assert meta['citation_doi']=='10.1007/978-3-032-16365-3_41'
        assert 'Lesion-Wise Model Ensemble' in meta['citation_title']
        articles=[n for n in nodes if n.tag=='article'];assert len(articles)==1
        blocks=[]
        def walk(n,scope):
            if not isinstance(n,Node):return
            if n.tag in {'section','aside'}:scope=scope+[n.attrs.get('id')]
            if n.tag in {'h1','h2','h3','h4','h5','h6','p','figure','table'}:
                v=n.text()
                if v:blocks.append(dict(index=len(blocks),kind='title' if n.tag.startswith('h') else n.tag,id=n.attrs.get('id'),scope=scope,text=v))
                return
            for child in n.children:walk(child,scope)
        walk(articles[0],['article']);tables=[]
        for n in articles[0].nodes():
            if n.tag=='table':tables.append(dict(id=n.attrs.get('id'),rows=[[c.text() for c in row.children if isinstance(c,Node) and c.tag in {'th','td'}] for row in n.nodes() if row.tag=='tr']))
        dump(out/'blocks.json',blocks);dump(out/'tables.json',tables)
        r.update(complete=True,blocks=len(blocks),tables=len(tables),headings=[dict(index=b['index'],scope=b['scope'],text=b['text']) for b in blocks if b['kind']=='title'])
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e))
    r.update(elapsed_seconds=time.perf_counter()-started,source_bindings=[entry(p) for p in sources]);dump(out/'receipt.json',r)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    print(json.dumps(r,ensure_ascii=False),flush=True);return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
