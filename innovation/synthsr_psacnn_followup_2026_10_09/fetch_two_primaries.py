"""Fetch and identity-check two public JATS fulltexts; extraction is not reading."""
import sys,json,xml.etree.ElementTree as ET,unicodedata
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
import retrieve_stronger_adaptation_primary as client
ITEMS=[('synthsr','10.1126/sciadv.add3607','PMC9891693'),('vsrad','10.3389/fneur.2025.1645891','PMC12571571')]
def textval(e):return ' '.join(''.join(e.itertext()).split())
def tag(e):return e.tag.rsplit('}',1)[-1]
def norm(s):return ' '.join(unicodedata.normalize('NFKC',s).translate(str.maketrans({'‐':'-','‑':'-','–':'-','—':'-'})).split()).rstrip('.').casefold()
def main():
    sys.stdout.reconfigure(encoding='utf-8');client.resource_guard()
    index=HERE/'index_attempt01/receipt.json';q=json.loads(index.read_text(encoding='utf-8'));assert q['complete']
    entries={e['doi']:e for r in q['records'] for e in r['entries'] if e['doi']}
    out=HERE/'xml_attempt01';out.mkdir(exist_ok=False);client.OUT=out
    with ThreadPoolExecutor(max_workers=2) as pool:records=list(pool.map(lambda a:client.fetch(a[0],'https://www.ebi.ac.uk/europepmc/webservices/rest/'+a[2]+'/fullTextXML','.xml'),ITEMS))
    client.dump(out/'HTTP_RECEIPT.json',dict(complete=all(r['complete'] for r in records),errors=[e for r in records for e in r['errors']],records=records,maintexts_read=0))
    ext=HERE/'xml_extraction_attempt01';ext.mkdir(exist_ok=False);catalog=[];errors=[]
    for (key,doi,pmcid),r in zip(ITEMS,records):
        if not r['complete']:errors.extend(r['errors']);continue
        root=ET.parse(ROOT/r['file']).getroot();meta=root.find('./front/article-meta')
        ids={e.get('pub-id-type'):textval(e) for e in meta.findall('./article-id')};assert ids['doi'].lower()==doi and pmcid in ids.values(),ids
        title=textval(meta.find('./title-group/article-title'));assert norm(title)==norm(entries[doi]['title'])
        blocks=[]
        def walk(e,scope):
            t=tag(e)
            if t=='sec':scope=scope+[e.get('id')]
            if t in {'title','p','fig','table-wrap','disp-formula'}:
                v=textval(e)
                if v:blocks.append(dict(index=len(blocks),kind=t,id=e.get('id'),scope=scope,text=v))
                return
            for child in e:walk(child,scope)
        for e in meta.findall('./abstract'):walk(e,['abstract'])
        walk(root.find('./body'),['body'])
        tables=[dict(id=e.get('id'),text=textval(e),rows=[[textval(c) for c in row if tag(c) in {'th','td'}] for row in e.iter() if tag(row)=='tr']) for e in root.iter() if tag(e)=='table-wrap']
        supplement=[dict(tag=tag(e),attributes=e.attrib,text=textval(e)) for e in root.iter() if tag(e)=='supplementary-material']
        client.dump(ext/(key+'_blocks.json'),blocks);client.dump(ext/(key+'_tables.json'),tables);client.dump(ext/(key+'_supplement_links.json'),supplement)
        catalog.append(dict(key=key,doi=doi,pmcid=pmcid,title=title,blocks=len(blocks),characters=sum(len(v['text']) for v in blocks),tables=len(tables),
            source_binding=dict(path=r['file'],bytes=r['bytes'],sha256=r['sha256']),maintexts_actually_read=0,
            headings=[dict(index=b['index'],kind=b['kind'],text=b['text'][:140]) for b in blocks if b['kind']=='title']))
    result=dict(complete=len(catalog)==2,errors=errors,records=catalog,maintexts_actually_read=0,medical_arrays_loaded=0,neural_forwards=0,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=client.sha(p),bytes=p.stat().st_size) for p in [Path(__file__),HERE/'PRIMARY_SELECTION.md',index,Path(client.__file__)]])
    client.dump(ext/'receipt.json',result)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<4_000_000
    print(json.dumps(result,ensure_ascii=False),flush=True);return int(not result['complete'])
if __name__=='__main__':raise SystemExit(main())
