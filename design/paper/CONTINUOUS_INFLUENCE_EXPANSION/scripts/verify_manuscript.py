from adapters import *
import re,collections
CV=P/'revised_manuscript';OLD=P/'original_snapshot/manuscript'
def reachable(base,stem):
    seen=set();labels=[]
    def walk(p):
        assert p not in seen,('Duplicate input',p);seen.add(p)
        t=p.read_text(encoding='utf-8');labels.extend(re.findall(r'\\label\{([^}]+)\}',t))
        for s in re.findall(r'\\input\{([^}]+)\}',t):walk(base/(s if Path(s).suffix else s+'.tex'))
    walk(base/(stem+'.tex'));return seen,labels
def main():
    old=set();new=set();labels={}
    for stem in ['main','supplement']:
        a,_=reachable(OLD,stem);b,ls=reachable(CV,stem);old|=a;new|=b
        assert not [k for k,v in collections.Counter(ls).items() if v>1]
        labels[stem]=len(ls)
    assert {p.name for p in old}<={p.name for p in new}
    nrows=0
    for f in old:
        if f.name=='architecture_coverage_table.tex':continue
        rows=[x.strip() for x in f.read_text(encoding='utf-8').splitlines() if '&' in x and re.search(r'\d',x) and r'\\' in x]
        current=(CV/f.name).read_text(encoding='utf-8')
        assert all(row in current for row in rows),f.name;nrows+=len(rows)
    build=read(P/'build_logs/build_audit.json');assert all(r['success'] and not r['issues'] for r in build)
    mainbuild=next(r for r in build if r['document']=='main');assert mainbuild['body_pages']<=8,mainbuild
    for stem in ['main','supplement']:
        txt=(P/f'build_logs/{stem}_text.txt').read_text(encoding='utf-8')
        assert not re.search(r'\bnan\b|\?\?',txt,re.I)
    t=(CV/'main.tex').read_text(encoding='utf-8')
    assert 'ACVTT' in t and 'fails the frozen numerical gate' in t and 'negative fixed-count association' in t
    d=__import__('pandas').read_csv(P/'CONTINUOUS_INFLUENCE_BIG_TABLE.csv')
    big=(CV/'continuous_influence_big_table.tex').read_text(encoding='utf-8')
    from publish import LABEL,ci,state
    for m in LABEL:
        row=next(x for x in big.splitlines() if x.startswith(LABEL[m]+' &'))
        for ds in ['fastmri','ixi']:
            r=d[(d.model==m)&(d.dataset==ds)].iloc[0]
            assert ci(r,'beyond_count') in row and ci(r,'fixed_count') in row and state(r) in row
    out=dict(status='PASS',old_reachable_tex_files=len(old),new_reachable_tex_files=len(new),retained_historical_numerical_rows=nrows,unique_labels=labels,body_pages=mainbuild['body_pages'],pdf_sha256={s:sha(CV/(s+'.pdf')) for s in ['main','supplement']})
    write(P/'outputs/manuscript_verification.json',out);print(out,flush=True)
if __name__=='__main__':main()
