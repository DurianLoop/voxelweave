"""Retrieve three fixed identity-matched public JATS texts, preserving extraction provenance."""
import json,re,ssl,sys,time,unicodedata,urllib.request,xml.etree.ElementTree as ET
from pathlib import Path
from inventory_frozen_text_storage import ROOT,HERE,entry,dump,guard
ITEMS=[('acquisition','10.1016/j.media.2023.103058','PMC7617170'),
       ('unlearning','10.3389/fmed.2026.1875760','PMC13474016'),
       ('bezier','10.3390/jcm15145508','PMC13413108')]
def tag(e):return e.tag.rsplit('}',1)[-1]
def textval(e):return ' '.join(''.join(e.itertext()).split())
def norm(s):return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().casefold())

def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();before=guard(started)
    indexpath=HERE/'public_index_attempt02/receipt.json'
    index=json.loads(indexpath.read_text(encoding='utf-8'));assert index['complete']
    hits={hit['doi']:hit for row in index['queries'] for hit in row['items'] if hit['doi']}
    out=HERE/'primary_xml_attempt01';out.mkdir(exist_ok=False)
    dump(out/'frozen_selection.json',dict(items=ITEMS,index=entry(indexpath),source_bindings=[entry(Path(__file__)),entry(HERE/'PRIMARY_SELECTION.md')]))
    context=ssl.create_default_context();assert context.check_hostname and context.verify_mode==ssl.CERT_REQUIRED
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=context))
    results=[];total=0
    for key,doi,pmcid in ITEMS:
        guard(started);row=dict(key=key,doi=doi,pmcid=pmcid,complete=False,maintext_actually_read=False)
        url='https://www.ebi.ac.uk/europepmc/webservices/rest/'+pmcid+'/fullTextXML';row['requested_url']=url
        try:
            with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRIResearchLiterature/1.0'}),timeout=25) as resp:
                data=resp.read(300_001);assert len(data)<=300_000
                row.update(http_status=resp.status,effective_url=resp.url)
            total+=len(data);assert total<=800_000
            root=ET.fromstring(data);meta=root.find('./front/article-meta');assert meta is not None
            ids={e.get('pub-id-type'):textval(e) for e in meta.findall('./article-id')}
            assert ids['doi'].casefold()==doi and any(v.removeprefix('PMC')==pmcid.removeprefix('PMC') for k,v in ids.items() if 'pmc' in str(k))
            title=textval(meta.find('./title-group/article-title'));assert norm(title)==norm(hits[doi]['title'])
            blocks=[]
            def walk(e,scope):
                if e is None:return
                kind=tag(e)
                if kind=='sec':scope=scope+[e.get('id') or textval(e.find('./title'))]
                if kind in {'title','p','fig','table-wrap','disp-formula'}:
                    value=textval(e)
                    if value:blocks.append(dict(index=len(blocks),kind=kind,id=e.get('id'),scope=scope,text=value))
                    return
                for child in e:walk(child,scope)
            for e in meta.findall('./abstract'):walk(e,['abstract'])
            walk(root.find('./body'),['body'])
            tables=[dict(id=e.get('id'),text=textval(e),rows=[[textval(c) for c in tr if tag(c) in {'th','td'}] for tr in e.iter() if tag(tr)=='tr']) for e in root.iter() if tag(e)=='table-wrap']
            formulas=[dict(id=e.get('id'),text=textval(e),xml=ET.tostring(e,encoding='unicode')) for e in root.iter() if tag(e)=='disp-formula']
            supplements=[dict(attributes=e.attrib,text=textval(e)) for e in root.iter() if tag(e)=='supplementary-material']
            serialized=[json.dumps(value,ensure_ascii=False,indent=2)+'\n' for value in [blocks,tables,formulas,supplements]]
            current=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
            assert current+len(data)+sum(len(v.encode('utf-8')) for v in serialized)+250_000<2_000_000
            path=out/(key+'.xml')
            with path.open('xb') as f:f.write(data)
            extraction=[]
            for name,value in zip(['blocks','tables','formulas','supplement_links'],[blocks,tables,formulas,supplements]):
                p=out/(key+'_'+name+'.json');dump(p,value);extraction.append(entry(p))
            row.update(complete=True,identity_verified=True,title=title,article_attributes=root.attrib,article_ids=ids,
                blocks=len(blocks),tables=len(tables),display_formulas=len(formulas),maintext_characters=sum(len(v['text']) for v in blocks),
                source=entry(path),extraction_sources=extraction,
                headings=[dict(index=b['index'],text=b['text']) for b in blocks if b['kind']=='title'],figure_pixels_read=False,
                external_supplement_or_author_code_read=False)
        except Exception as exc:row['error']=dict(type=type(exc).__name__,message=str(exc))
        results.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
    result=dict(complete=all(row['complete'] for row in results),records=results,resources_before=before,
        resources_after=guard(started),elapsed_seconds=time.perf_counter()-started,new_distinct_maintexts_actually_read=0,
        patient_information_uploaded=False,patient_arrays_loaded=0,publication_claim_confirmed=False,goal_status='active')
    dump(out/'receipt.json',result);return int(not result['complete'])

if __name__=='__main__':raise SystemExit(main())
