from pathlib import Path
import hashlib, json, shutil, datetime

PAPER = Path(__file__).resolve().parents[2]
OUT = PAPER / 'PLAN13_EVIDENCE_UPGRADE'
sources = [PAPER/'README.md', PAPER/'CVPR/README.md', PAPER/'TMI/README.md']
for root in [PAPER/'CVPR/CVPR_ARCH_GENERALIZED/PAPER', PAPER/'TMI/TMI_ARCH_GENERALIZED']:
    sources.extend(p for p in root.rglob('*') if p.is_file())
records=[]
for src in sources:
    rel=src.relative_to(PAPER)
    dst=OUT/'original_snapshot'/rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        raise RuntimeError(f'Snapshot already exists: {dst}')
    shutil.copy2(src,dst)
    records.append({'path':rel.as_posix(),'bytes':src.stat().st_size,'sha256':hashlib.sha256(src.read_bytes()).hexdigest()})
(OUT/'original_manifest.json').write_text(json.dumps({'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':records},indent=2),encoding='utf-8')
print(f'Protected {len(records)} original files')
