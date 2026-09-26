"""Install only verified CVPR revision files; preserve the frozen originals."""
from common import *
import shutil
def main():
    guard();assert read(OUT/'protection_before_install.json')['failures']==0
    for f in ['array_checks_all.csv','new_array_reproduction_checks.csv','reproduction_initial_checks.csv','final_headline_checks.csv']:assert (pd.read_csv(OUT/f).status=='PASS').all(),f
    replay=read(OUT/'reproduction_run.json');assert len(replay)==6 and all(x['returncode']==0 for x in replay)
    builds=read(P/'build_logs/build_audit.json');assert all(x['success'] and not x['issues'] for x in builds)
    assert next(x for x in builds if x['document']=='cvpr')['pages']==8
    src=P/'revised_manuscript';dst=PAPER/'CVPR/CVPR_ARCH_GENERALIZED/PAPER'
    original={r['path']:r['sha256'] for r in read(P/'original_manifest.json')}
    names=['main.tex','supplement.tex','references.bib','p17_control_table.tex']+[x.name for x in src.glob('final_*.tex')]+[x.name for x in src.glob('final_*.pdf')]
    for stem in ['main','supplement']:
        names += [stem+ext for ext in ['.pdf','.aux','.out','.log','.bbl','.blg'] if (src/(stem+ext)).exists()]
    changes=[]
    for name in sorted(set(names)):
        target=dst/name;key=target.relative_to(ROOT).as_posix();before=sha(target) if target.exists() else None
        if key in original:assert before==original[key],f'Original changed since freeze: {target}'
        elif target.exists():assert before==sha(src/name),f'Unrecognized existing file: {target}'
        shutil.copy2(src/name,target);changes.append({'path':key,'before_sha256':before,'after_sha256':sha(target),'snapshot':str((P/'original_snapshot'/key).relative_to(P)) if key in original else None})
    write(OUT/'installed_files.json',changes);print('Installed verified CVPR files',len(changes),'TMI untouched',flush=True)
if __name__=='__main__':main()
