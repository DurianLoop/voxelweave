"""Explicit substitute for inaccessible primaries, preserve original failure."""
import sys,json,xml.etree.ElementTree as ET
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
import retrieve_stronger_adaptation_primary as client
from fetch_and_extract_primaries import text,tag,norm
def main():
    sys.stdout.reconfigure(encoding='utf-8');client.resource_guard()
    out=HERE/'fallback_attempt01';out.mkdir(exist_ok=False);client.OUT=out
    r=client.fetch('claustrum','https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12368599/fullTextXML','.xml')
    client.dump(out/'HTTP_RECEIPT.json',r)
    if not r['complete']:print(json.dumps(r),flush=True);return 1
    root=ET.parse(ROOT/r['file']).getroot();meta=root.find('./front/article-meta');ids={e.get('pub-id-type'):text(e) for e in meta.findall('./article-id')}
    assert ids['doi'].casefold()=='10.1002/hbm.70303' and 'PMC12368599' in ids.values(),ids
    title=text(meta.find('./title-group/article-title'));q=json.loads((HERE/'index_attempt01/receipt.json').read_text(encoding='utf-8'))
    indexed=next(e for a in q['records'] for e in a['entries'] if e['doi']=='10.1002/hbm.70303');assert norm(title)==norm(indexed['title'])
    blocks=[]
    def walk(e,scope):
        t=tag(e)
        if t=='sec':scope=scope+[e.get('id')]
        if t in {'title','p','fig','table-wrap','disp-formula'}:
            v=text(e)
            if v:blocks.append(dict(index=len(blocks),kind=t,id=e.get('id'),scope=scope,text=v))
            return
        for c in e:walk(c,scope)
    for a in meta.findall('./abstract'):walk(a,['abstract'])
    body=root.find('./body');assert body is not None;walk(body,['body'])
    tables=[dict(id=e.get('id'),text=text(e),rows=[[text(c) for c in row if tag(c) in {'th','td'}] for row in e.iter() if tag(row)=='tr']) for e in body.iter() if tag(e)=='table-wrap']
    client.dump(out/'claustrum_blocks.json',blocks);client.dump(out/'claustrum_tables.json',tables)
    receipt=dict(complete=True,errors=[],doi=ids['doi'],pmcid='PMC12368599',title=title,blocks=len(blocks),tables=len(tables),actual_primary_maintexts_completed=0,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=client.sha(p)) for p in [Path(__file__),HERE/'FALLBACK_SELECTION.md',HERE/'index_attempt01/receipt.json',ROOT/r['file']]],
        headings=[dict(index=b['index'],kind=b['kind'],scope=b['scope'],text=b['text'][:110]) for b in blocks if b['kind'] in {'title','table-wrap','disp-formula'}])
    client.dump(out/'receipt.json',receipt);print(json.dumps(receipt,ensure_ascii=False),flush=True);return 0
if __name__=='__main__':raise SystemExit(main())
