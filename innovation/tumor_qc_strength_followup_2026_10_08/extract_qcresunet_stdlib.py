"""Pinned arXiv HTML text and exact tabular cells, not a visual review or author implementation."""
import hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'augmentation_primary_followup_2026_10_08'))
from extract_bigaug_stdlib import Parser,Node
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):
    with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard();src=HERE/'primary_sources_attempt01/qcresunet_arxiv_v2.html'
    assert sha(src)=='8cc2f419bbc8e87e84769dd9e875b28d144556e3a3733263ef28ad901bdd0508'
    parser=Parser();parser.feed(src.read_text(encoding='utf-8'));nodes=list(parser.root.walk())
    titles=[' '.join(n.text().split()) for n in nodes if n.tag=='h1'];title='QCResUNet: Joint Subject-level and Voxel-level Segmentation Quality Prediction'
    assert any(t.lower()==title.lower() for t in titles),titles
    articles=[n for n in nodes if n.tag=='article'];assert len(articles)==1
    article=articles[0];selected={'h1','h2','h3','h4','h5','p','figure','table','li'};blocks=[]
    for n in article.walk():
        if n.tag not in selected:continue
        parent=n.parent;duplicate=False;sections=[]
        while parent and parent is not article:
            if parent.tag in selected:duplicate=True
            if parent.tag=='section':sections.append(parent.attrs.get('id'))
            parent=parent.parent
        if duplicate:continue
        content=' '.join(n.text().split())
        if content:blocks.append(dict(kind=n.tag,id=n.attrs.get('id'),section_ids=sections,text=content))
    tables=[]
    for n in article.walk():
        if n.tag!='table':continue
        cells=[]
        for tr in n.walk():
            if tr.tag!='tr':continue
            row=[dict(tag=c.tag,text=' '.join(c.text().split()),rowspan=c.attrs.get('rowspan','1'),colspan=c.attrs.get('colspan','1')) for c in tr.children if isinstance(c,Node) and c.tag in ['td','th']]
            if row:cells.append(row)
        tables.append(dict(id=n.attrs.get('id'),class_name=n.attrs.get('class'),rows=cells))
    maths=[dict(id=n.attrs.get('id'),alttext=n.attrs.get('alttext'),text=' '.join(n.text().split())) for n in nodes if n.tag=='math']
    assert len(blocks)>50 and any('ground truth' in b['text'].lower() for b in blocks)
    out=HERE/'extraction_attempt01';out.mkdir(exist_ok=False)
    dump(out/'blocks.json',blocks);dump(out/'tables.json',tables);dump(out/'maths.json',maths)
    receipt=dict(complete=True,errors=[],identity_verified=True,pinned_arxiv_id='2412.07156v2',citation_title=title,
        blocks=len(blocks),tables=len(tables),math_elements=len(maths),figure_pixels_reviewed=False,author_code_executed=False,
        actual_primary_reading_completed=False,version_of_record_equivalence_not_asserted=True,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in [Path(__file__),ROOT/'augmentation_primary_followup_2026_10_08/extract_bigaug_stdlib.py',src]])
    dump(out/'receipt.json',receipt);assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    print(json.dumps(dict(complete=True,blocks=len(blocks),catalog=[dict(index=i,kind=b['kind'],id=b['id'],sections=b['section_ids'],preview=b['text'][:130]) for i,b in enumerate(blocks)]),ensure_ascii=False),flush=True)
if __name__=='__main__':main()
