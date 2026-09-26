from adapters import *
import shutil,re,zipfile,datetime
CV=P/'revised_manuscript';CANON=P.parent/'CVPR/CVPR_ARCH_GENERALIZED/PAPER'
def closure():
    files=set()
    def add(f):
        f=f.resolve();assert f.is_relative_to(CV.resolve()) and f.exists(),f
        if f in files:return
        files.add(f)
        if f.suffix!='.tex':return
        t=f.read_text(encoding='utf-8')
        for x in re.findall(r'\\input\{([^}]+)\}',t):add(CV/(x if Path(x).suffix else x+'.tex'))
        for x in re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}',t):
            candidates=[b/x for b in [CV,CV/'figures']]
            if not Path(x).suffix:candidates=[p.with_suffix(s) for p in candidates for s in ['.pdf','.png','.jpg']]
            f=next((p for p in candidates if p.exists()),None);assert f,x;add(f)
    for s in ['main.tex','supplement.tex','main.pdf','supplement.pdf','references.bib','ieeenat_fullname.bst','cvpr.sty']:add(CV/s)
    return sorted(files)
def main():
    for f in ['source_protection','final_science_verification','manuscript_verification']:assert read(P/f'outputs/{f}.json')['status']=='PASS'
    visual=read(P/'outputs/visual_review.json');assert visual['status']=='PASS'
    for s,h in visual['pdf_sha256'].items():assert sha(CV/(s+'.pdf'))==h
    required=['FINAL_REPORT_ZH.md','CONTINUOUS_INFLUENCE_BIG_TABLE.csv','CONTINUOUS_INFLUENCE_BIG_TABLE.md','ALL_SECONDARY_SIGNS.csv','UPDATED_CLAIM_EVIDENCE_MATRIX.md','UPDATED_MIRA_REPORT_CARD.csv','VISUAL_REVIEW.md']
    assert all((P/f).exists() for f in required)
    for f in (P/'original_snapshot/manuscript').rglob('*'):
        if f.is_file():assert sha(CANON/f.relative_to(P/'original_snapshot/manuscript'))==sha(f),f
    files=closure();records=[]
    for f in files:
        dest=CANON/f.relative_to(CV);oldhash=sha(dest) if dest.exists() else None;newhash=sha(f)
        if oldhash==newhash:continue
        dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dest);assert sha(dest)==newhash
        records.append(dict(path=dest.relative_to(ROOT).as_posix(),before_sha256=oldhash,after_sha256=newhash))
    write(P/'outputs/installed_files.json',records)
    zpath=P/'CVPR_CONTINUOUS_INFLUENCE_REVIEW_PACKAGE.zip'
    with zipfile.ZipFile(zpath,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for f in files:z.write(f,'PAPER/'+f.relative_to(CV).as_posix())
        for f in ['CONTINUOUS_INFLUENCE_BIG_TABLE.csv','ALL_SECONDARY_SIGNS.csv','UPDATED_MIRA_REPORT_CARD.csv']:z.write(P/f,'TABLES/'+f)
        z.writestr('README.txt','Local review package; not an external submission. Includes compiled main/supplement, reachable LaTeX and figures, aggregated influence tables. Excludes patient arrays and private checkpoint/input manifests. Historical nulls and numerical failures are retained. Authors must resolve authentic ethics, data-release permissions and submission metadata.\n')
    with zipfile.ZipFile(zpath) as z:
        assert z.testzip() is None
        for s in ['main','supplement']:assert z.read('PAPER/'+s+'.pdf')==(CANON/(s+'.pdf')).read_bytes()
    final_status=dict(status='COMPLETE',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),canonical_updated=True,new_table_complete=True,latex_rebuilt=True,visual_review_complete=True,installed_files=len(records),main_pdf_sha256=sha(CANON/'main.pdf'),supplement_pdf_sha256=sha(CANON/'supplement.pdf'))
    rows=[]
    for f in sorted(P.rglob('*')):
        if not f.is_file() or 'original_snapshot' in f.parts or 'page_renders' in f.parts or f.name in ['DELIVERY_MANIFEST.json','DELIVERY_STATUS.json']:continue
        rows.append(dict(path=f.relative_to(P).as_posix(),bytes=f.stat().st_size,sha256=sha(f)))
    write(P/'DELIVERY_STATUS.json',final_status)
    f=P/'DELIVERY_STATUS.json';rows.append(dict(path=f.name,bytes=f.stat().st_size,sha256=sha(f)))
    write(P/'DELIVERY_MANIFEST.json',dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=rows,zip_sha256=sha(zpath)))
    print('DELIVERED',len(records),'files; manifest',len(rows),'entries',flush=True)
if __name__=='__main__':main()
