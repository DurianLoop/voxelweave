from pathlib import Path
import shutil,json,hashlib
P=Path(__file__).resolve().parents[1];PAPER=P.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if not (P/'original_manifest.json').exists():
    files=[PAPER/'README.md',PAPER/'CVPR/README.md',PAPER/'TMI/README.md']
    for folder in ['CVPR/CVPR_ARCH_GENERALIZED/PAPER','TMI/TMI_ARCH_GENERALIZED']:
        files += [p for p in (PAPER/folder).rglob('*') if p.is_file()]
    rows=[]
    for p in files:
        rel=p.relative_to(PAPER);dst=P/'original_snapshot'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
        rows.append({'path':rel.as_posix(),'sha256':sha(p)})
    (P/'original_manifest.json').write_text(json.dumps({'files':rows},indent=2))
print('Protected current manuscripts and assets.')
