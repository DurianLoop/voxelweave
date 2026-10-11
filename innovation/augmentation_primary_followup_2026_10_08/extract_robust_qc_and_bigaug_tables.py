"""Lossless primary HTML identity, structured table cells and indexed text; no article image review."""
import hashlib,json,sys
from pathlib import Path
from fractions import Fraction
from extract_bigaug_stdlib import Parser,Node
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):
    with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def load_tree(p):
    parser=Parser();parser.feed(p.read_text(encoding='utf-8'));return list(parser.root.walk())
def tables(article):
    result=[]
    for n in article.walk():
        if n.tag!='table':continue
        ancestor=n.parent;sections=[]
        while ancestor:
            if ancestor.tag=='section':sections.append(ancestor.attrs.get('id'))
            ancestor=ancestor.parent
        rows=[]
        for tr in n.walk():
            if tr.tag!='tr':continue
            cells=[dict(tag=c.tag,text=' '.join(c.text().split()),rowspan=c.attrs.get('rowspan','1'),colspan=c.attrs.get('colspan','1'))
                for c in tr.children if isinstance(c,Node) and c.tag in ['th','td']]
            if cells:rows.append(cells)
        result.append(dict(sections=sections,rows=rows))
    return result
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard();out=HERE/'robust_qc_extraction_attempt01';out.mkdir(exist_ok=False)
    p=HERE/'robust_qc_sources_attempt01/robust_qc_pmc_html.html';nodes=load_tree(p)
    meta={n.attrs.get('name'):n.attrs.get('content') for n in nodes if n.tag=='meta'}
    title='Robust machine learning segmentation for large-scale analysis of heterogeneous clinical brain MRI datasets'
    assert meta.get('citation_title','').rstrip('.').lower()==title.lower()
    assert meta.get('citation_doi','').lower()=='10.1073/pnas.2216399120'
    articles=[n for n in nodes if n.tag=='article'];assert len(articles)==1;article=articles[0]
    selected={'h1','h2','h3','h4','p','figure','table','li'};blocks=[]
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
    assert len(blocks)>30 and any('quality control' in b['text'].lower() for b in blocks)
    dump(out/'blocks.json',blocks);dump(out/'tables.json',tables(article))
    big=HERE/'sources_attempt01/bigaug_pmc_html.html';bnodes=load_tree(big);ba=next(n for n in bnodes if n.tag=='article');bt=tables(ba)
    dump(out/'bigaug_tables.json',bt)
    t2=next(t for t in bt if 'T2' in t['sections']);arithmetic=[]
    for row in t2['rows']:
        texts=[c['text'] for c in row]
        if len(texts)!=13 or texts[0] in ['Task','Dataset','Supervised']:continue
        try:v=[Fraction(s) for s in texts[1:]]
        except ValueError:continue
        unseen=[v[i] for i in [1,2,3,5,6,8,9]]
        task_equal=((v[1]+v[2]+v[3])/3+(v[5]+v[6])/2+(v[8]+v[9])/2)/3
        arithmetic.append(dict(row=texts[0],exact_primary_cells=texts,source_unseen_average=float(v[-1]),
            equal_domain_average=float(sum(unseen)/7),equal_task_average=float(task_equal),
            source_minus_equal_task_average=float(v[-1]-task_equal),
            equal_task_discrepancy_gt_020=abs(v[-1]-task_equal)>Fraction(1,5)))
    assert arithmetic and any(a['row']=='Perturb' for a in arithmetic)
    dump(out/'bigaug_table_arithmetic.json',dict(complete=True,errors=[],rows=arithmetic,
        interpretation='Arithmetic from displayed primary HTML cells only. Weighting is not asserted; primary reported values retained. >0.20 percentage-point differences warrant caution, not silent correction.',
        neural_forwards=0,medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0))
    dump(out/'receipt.json',dict(complete=True,errors=[],citation_title=title,DOI='10.1073/pnas.2216399120',identity_verified=True,
        extracted_blocks=len(blocks),primary_reading_completed=False,figure_pixels_reviewed=False,independent_supplement_read=False,
        resources=resource_guard(),source_bindings=[dict(path=x.relative_to(ROOT).as_posix(),sha256=sha(x)) for x in
            [Path(__file__),HERE/'extract_bigaug_stdlib.py',p,big,out/'blocks.json',out/'tables.json',out/'bigaug_tables.json',out/'bigaug_table_arithmetic.json']]))
    print(json.dumps(dict(complete=True,blocks=len(blocks),tableII_arithmetic=arithmetic,
        catalog=[dict(index=i,kind=b['kind'],section_ids=b['section_ids'],preview=b['text'][:160]) for i,b in enumerate(blocks)]),ensure_ascii=False),flush=True)
if __name__=='__main__':main()
