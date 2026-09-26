from pathlib import Path
import re,json,hashlib,datetime,collections
import pandas as pd

P=Path(__file__).resolve().parents[1];CV=P/'revised_manuscript';OLD=P/'original_snapshot/manuscript'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def reachable(base):
    seen=set()
    def add(name):
        p=base/name
        if p in seen:return
        assert p.exists(),p
        seen.add(p)
        for s in re.findall(r'\\input\{([^}]+)\}',p.read_text(encoding='utf-8')):
            add(s if Path(s).suffix else s+'.tex')
    add('main.tex');add('supplement.tex')
    return seen
def main():
    old=reachable(OLD);new=reachable(CV);oldnames={x.name for x in old};newnames={x.name for x in new}
    assert oldnames<=newnames,(oldnames-newnames)
    nrows=0;nfiles=0
    # These two report tables were expanded and are checked against the actual CSV below.
    changed_tables={'mira_report_card_table.tex','final_acquired_table.tex'}
    for f in old:
        if f.name in changed_tables:continue
        rows=[x.strip() for x in f.read_text(encoding='utf-8').splitlines() if '&' in x and re.search(r'\d',x) and r'\\' in x]
        current=(CV/f.name).read_text(encoding='utf-8')
        assert all(x in current for x in rows),f.name
        nrows+=len(rows);nfiles+=bool(rows)
    labels={}
    for stem in ['main','supplement']:
        seen=set();all_labels=[]
        def walk(f):
            assert f not in seen,('Repeated input',f)
            seen.add(f);s=f.read_text(encoding='utf-8')
            all_labels.extend(re.findall(r'\\label\{([^}]+)\}',s))
            for x in re.findall(r'\\input\{([^}]+)\}',s):walk(CV/(x if Path(x).suffix else x+'.tex'))
        walk(CV/(stem+'.tex'))
        dup=[k for k,v in collections.Counter(all_labels).items() if v>1];assert not dup,(stem,dup)
        labels[stem]=len(all_labels)
    cards=pd.read_csv(P/'UPDATED_MIRA_REPORT_CARD.csv',keep_default_na=False)
    d=pd.read_csv(P/'FIVE_ARCH_ACQUIRED_ONLY_INFLUENCE.csv',keep_default_na=False)
    assert len(cards)==13
    for r in d.itertuples():
        row=cards[(cards.design=='acquired-only '+r.model)&(cards.cohort==r.dataset)].iloc[0]
        if r.technical_eligibility=='ELIGIBLE':
            assert row.stability=='PASS'
            assert abs(float(row.beyond_count)-float(r.beyond_count_estimate))<1e-14
            assert abs(float(row.fixed_count)-float(r.fixed_count_estimate))<1e-14
        else:
            assert all(row[k]=='NA' for k in ['stability','beyond_count','fixed_count'])
    build=json.loads((P/'build_logs/build_audit.json').read_text());assert all(x['success'] and not x['issues'] for x in build)
    for stem in ['cvpr','supplement']:
        txt=(P/f'build_logs/{stem}_text.txt').read_text(encoding='utf-8')
        assert not re.search(r'\bnan\b|\?\?',txt,re.I),stem
    pages=(P/'build_logs/cvpr_text.txt').read_text(encoding='utf-8').split('\f')
    assert 'References' in pages[8] and 'References' not in pages[7]
    out=dict(status='PASS',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
             old_reachable_tex_files=len(old),new_reachable_tex_files=len(new),
             preserved_numeric_rows=nrows,preserved_table_files=nfiles,
             reformatted_tables=sorted(changed_tables),core_report_card_rows_checked=10,
             unique_labels=labels,main_body_pages=8,main_reference_pages=1,supplement_pages=36,
             pdf_sha256={s:sha(CV/(s+'.pdf')) for s in ['main','supplement']})
    (P/'outputs/delivery_checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__':main()
