"""Extract JATS main text with exact source binding; no medical/model access."""
import json,sys,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
import retrieve_stronger_adaptation_primary as client
def content(e):return ' '.join(''.join(e.itertext()).split())
def tag(e):return e.tag.rsplit('}',1)[-1]
def main():
    sys.stdout.reconfigure(encoding='utf-8');client.resource_guard()
    src=HERE/'jungo_primary_attempt01/fulltext.xml'
    assert client.sha(src)=='7c71cfa634f58afa53c79c3787de61091a818406482766ee400cc45e73fda6aa'
    root=ET.parse(src).getroot();blocks=[]
    def walk(e,scope):
        t=tag(e)
        if t=='sec':scope=scope+[e.get('id')]
        if t in {'title','p','fig','table-wrap','disp-formula'}:
            txt=content(e)
            if txt:blocks.append(dict(index=len(blocks),kind=t,id=e.get('id'),scope=scope,text=txt))
            return
        for c in e:walk(c,scope)
    for a in root.findall('./front/article-meta/abstract'):walk(a,['abstract'])
    body=root.find('./body');assert body is not None;walk(body,['body'])
    tables=[dict(id=e.get('id'),text=content(e),rows=[[content(c) for c in row if tag(c) in {'td','th'}] for row in e.iter() if tag(row)=='tr']) for e in body.iter() if tag(e)=='table-wrap']
    out=HERE/'jungo_extraction_attempt01';out.mkdir(exist_ok=False)
    client.dump(out/'blocks.json',blocks);client.dump(out/'tables.json',tables)
    client.dump(out/'receipt.json',dict(complete=True,errors=[],blocks=len(blocks),tables=len(tables),primary_reading_completed=False,
        references_extracted=False,figure_pixels_reviewed=False,medical_arrays_loaded=0,neural_forwards=0,CUDA_initialized=False,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=client.sha(p)) for p in [Path(__file__),src,HERE/'jungo_primary_attempt01/receipt.json']]))
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    print(json.dumps(dict(blocks=len(blocks),tables=len(tables),catalog=[dict(index=b['index'],kind=b['kind'],scope=b['scope'],preview=b['text'][:95]) for b in blocks]),ensure_ascii=False),flush=True)
if __name__=='__main__':main()
