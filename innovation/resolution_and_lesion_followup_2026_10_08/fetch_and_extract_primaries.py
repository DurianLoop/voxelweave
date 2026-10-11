"""Identity-check and extract three selected public JATS articles; no reading claim."""
import sys,json,unicodedata,xml.etree.ElementTree as ET
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
import retrieve_stronger_adaptation_primary as client
ITEMS=[('gouhfi','10.1162/imag.a.960','PMC12556684'),('vinn','10.1016/j.neuroimage.2022.118933','PMC9801435'),('lesion_ensemble','10.1007/978-3-032-16365-3_41','PMC13148016')]
def text(e):return ' '.join(''.join(e.itertext()).split())
def tag(e):return e.tag.rsplit('}',1)[-1]
def norm(s):return ' '.join(unicodedata.normalize('NFKC',s).translate(str.maketrans({'‐':'-','‑':'-','–':'-','—':'-'})).split()).rstrip('.').casefold()
def main():
    sys.stdout.reconfigure(encoding='utf-8');client.resource_guard()
    index=HERE/'index_attempt01/receipt.json';q=json.loads(index.read_text(encoding='utf-8'));assert q['complete']
    entries={x['doi']:x for r in q['records'] for x in r['entries'] if x['doi']}
    out=HERE/'primary_attempt01';out.mkdir(exist_ok=False);client.OUT=out
    with ThreadPoolExecutor(max_workers=3) as pool:records=list(pool.map(lambda a:client.fetch(a[0],'https://www.ebi.ac.uk/europepmc/webservices/rest/'+a[2]+'/fullTextXML','.xml'),ITEMS))
    client.dump(out/'HTTP_RECEIPT.json',dict(records=records,complete=all(r['complete'] for r in records),actual_primary_maintexts_completed=0))
    ext=HERE/'extraction_attempt01';ext.mkdir(exist_ok=False);catalog=[];errors=[]
    for (key,doi,pmcid),r in zip(ITEMS,records):
        if not r['complete']:errors.extend(r['errors']);continue
        root=ET.parse(ROOT/r['file']).getroot();meta=root.find('./front/article-meta');ids={e.get('pub-id-type'):text(e) for e in meta.findall('./article-id')}
        assert ids['doi'].casefold()==doi and pmcid in ids.values(),ids
        title=text(meta.find('./title-group/article-title'));assert norm(title)==norm(entries[doi]['title']),(title,entries[doi]['title'])
        blocks=[]
        def walk(e,scope):
            t=tag(e)
            if t=='sec':scope=scope+[e.get('id')]
            if t in {'title','p','fig','table-wrap','disp-formula'}:
                content=text(e)
                if content:blocks.append(dict(index=len(blocks),kind=t,id=e.get('id'),scope=scope,text=content))
                return
            for c in e:walk(c,scope)
        for a in meta.findall('./abstract'):walk(a,['abstract'])
        body=root.find('./body');assert body is not None;walk(body,['body'])
        tables=[dict(id=e.get('id'),text=text(e),rows=[[text(c) for c in row if tag(c) in {'th','td'}] for row in e.iter() if tag(row)=='tr']) for e in body.iter() if tag(e)=='table-wrap']
        client.dump(ext/(key+'_blocks.json'),blocks);client.dump(ext/(key+'_tables.json'),tables)
        supplements=[dict(tag=tag(e),attributes=e.attrib,text=text(e)) for e in root.iter() if tag(e) in {'supplementary-material','ext-link'} and ('supp' in str(e.attrib).lower() or tag(e)=='supplementary-material')]
        client.dump(ext/(key+'_supplement_links.json'),supplements)
        catalog.append(dict(key=key,doi=doi,pmcid=pmcid,title=title,blocks=len(blocks),tables=len(tables),source_binding=dict(path=r['file'],sha256=r['sha256'],bytes=r['bytes']),
            headings=[dict(index=b['index'],kind=b['kind'],scope=b['scope'],text=b['text'][:110]) for b in blocks if b['kind'] in {'title','table-wrap','disp-formula'}]))
    receipt=dict(complete=len(catalog)==3,errors=errors,records=catalog,actual_primary_maintexts_completed=0,medical_arrays_loaded=0,neural_forwards=0,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=client.sha(p)) for p in [Path(__file__),HERE/'PRIMARY_SELECTION.md',index,Path(client.__file__)]])
    client.dump(ext/'receipt.json',receipt)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    print(json.dumps(receipt,ensure_ascii=False),flush=True);return int(not receipt['complete'])
if __name__=='__main__':raise SystemExit(main())
