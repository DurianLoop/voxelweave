"""Local-only punctuation reconciliation and bounded JATS extraction; preserve failed fetch."""
import sys,json,xml.etree.ElementTree as ET
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
import retrieve_stronger_adaptation_primary as client
ITEMS=[('clinical_vs','10.1093/jamiaopen/ooaf163','PMC12772638','54fa48e991a4db6a84a9e514658815dfd3f80ee9a9211a22aacf5b7a8de0cf88'),
    ('label_preserving','10.1002/nbm.70266','PMC12983123','10cd90b719c5ad6f82e4d86775bfd5b84123d4e5d94f350fe391fb86bc485ad3')]
def text(e):return ' '.join(''.join(e.itertext()).split())
def tag(e):return e.tag.rsplit('}',1)[-1]
def norm(s):return ' '.join(s.replace('\u2010','-').split()).rstrip('.').casefold()
def main():
    sys.stdout.reconfigure(encoding='utf-8');client.resource_guard()
    index=HERE/'index_attempt01/receipt.json';q=json.loads(index.read_text(encoding='utf-8'));assert q['complete']
    entries={x['doi']:x for r in q['records'] for x in r['entries'] if x['doi']}
    out=HERE/'extraction_attempt01';out.mkdir(exist_ok=False);records=[]
    for key,doi,pmcid,expected in ITEMS:
        src=HERE/('primary_attempt01/'+key+'.xml');assert client.sha(src)==expected
        root=ET.parse(src).getroot();identity={e.get('pub-id-type'):text(e) for e in root.findall('./front/article-meta/article-id')}
        assert identity['doi'].lower()==doi and identity['pmcid']==pmcid
        title=text(root.find('./front/article-meta/title-group/article-title'));assert norm(title)==norm(entries[doi]['title'])
        blocks=[]
        def walk(e,scope):
            t=tag(e)
            if t=='sec':scope=scope+[e.get('id')]
            if t in {'title','p','fig','table-wrap','disp-formula'}:
                content=text(e)
                if content:blocks.append(dict(index=len(blocks),kind=t,id=e.get('id'),scope=scope,text=content))
                return
            for c in e:walk(c,scope)
        for a in root.findall('./front/article-meta/abstract'):walk(a,['abstract'])
        body=root.find('./body');assert body is not None;walk(body,['body'])
        tables=[dict(id=e.get('id'),text=text(e),rows=[[text(c) for c in row if tag(c) in {'th','td'}] for row in e.iter() if tag(row)=='tr']) for e in body.iter() if tag(e)=='table-wrap']
        client.dump(out/(key+'_blocks.json'),blocks);client.dump(out/(key+'_tables.json'),tables)
        records.append(dict(key=key,doi=doi,pmcid=pmcid,original_XML_title=title,index_title=entries[doi]['title'],
            title_identity_verified_after_explicit_punctuation_normalization=True,blocks=len(blocks),tables=len(tables),
            catalog=[dict(index=b['index'],kind=b['kind'],scope=b['scope'],preview=b['text'][:100]) for b in blocks if b['kind'] in {'title','table-wrap','disp-formula'}],
            source_binding=dict(path=src.relative_to(ROOT).as_posix(),sha256=expected,bytes=src.stat().st_size)))
    receipt=dict(complete=True,errors=[],local_only=True,additional_HTTP_GETs=0,original_fetch_tool_session=12809,original_fetch_tool_exit=1,
        original_fetch_error_preserved=True,original_inner_HTTP_returns_recovered=False,records=records,actual_primary_maintexts_completed=0,
        external_supplements_read=False,figure_pixels_reviewed=False,author_code_executed=False,medical_arrays_loaded=0,
        GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,CUDA_initialized=False,publication_claim_confirmed=False,goal_status='active',
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=client.sha(p)) for p in [Path(__file__),index,HERE/'LOCAL_TITLE_RECONCILIATION_PROTOCOL.md',HERE/'fetch_selected_primaries.py']])
    client.dump(out/'receipt.json',receipt);assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    print(json.dumps(dict(complete=True,local_only=True,records=records),ensure_ascii=False),flush=True)
if __name__=='__main__':main()
