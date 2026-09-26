"""Protect Plan 13 and inventory available sources before new outcome evaluation."""
from pathlib import Path
import os,json,hashlib,shutil,datetime,collections
import numpy as np
import pandas as pd
import nibabel as nib
P14=Path(__file__).resolve().parents[1]; PAPER=P14.parent; ROOT=PAPER.parents[1]
OUT=P14/'outputs'; OUT.mkdir(exist_ok=True)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
if not (P14/'original_manifest.json').exists():
    files=[PAPER/'README.md',PAPER/'CVPR/README.md',PAPER/'TMI/README.md']
    for d in ['CVPR/CVPR_ARCH_GENERALIZED/PAPER','TMI/TMI_ARCH_GENERALIZED']:
        files += [p for p in (PAPER/d).rglob('*') if p.is_file()]
    records=[]
    for p in files:
        rel=p.relative_to(PAPER); dst=P14/'original_snapshot'/rel
        dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,dst)
        records.append({'path':rel.as_posix(),'sha256':sha(p),'bytes':p.stat().st_size})
    (P14/'original_manifest.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':records},indent=2))

inventory=[]; manifests=[]
for top in ['dataset','baseline','design','pre','processing','external','docx','tests']:
    counts=collections.Counter(); sizes=collections.Counter()
    for directory,dirs,files in os.walk(ROOT/top):
        dirs[:]=[d for d in dirs if d not in {'.git','__pycache__','node_modules','original_snapshot','.pytest_cache'}]
        for f in files:
            p=Path(directory)/f
            ext='.nii.gz' if f.endswith('.nii.gz') else p.suffix.lower()
            counts[ext]+=1; sizes[ext]+=p.stat().st_size
            if ('manifest' in f.lower() or 'registry' in f.lower()) and ext in ['.json','.csv']:
                manifests.append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size})
    inventory += [{'root':top,'extension':e,'files':n,'bytes':sizes[e]} for e,n in counts.items()]
pd.DataFrame(inventory).to_csv(OUT/'workspace_inventory.csv',index=False)
pd.DataFrame(manifests).to_csv(OUT/'manifest_registry_inventory.csv',index=False)

rows=[]
mr=ROOT/'dataset/NingXiaData/Data/MRNet-v1.0/MRNet-v1.0'
for view in ['axial','coronal','sagittal']:
    for p in sorted((mr/'valid'/view).glob('*.npy')):
        v=np.load(p,mmap_mode='r'); rows.append({'dataset':'mrnet','case':p.stem,'view':view,'path':p.relative_to(ROOT).as_posix(),'shape':str(v.shape),'dtype':str(v.dtype),'sha256':sha(p)})
top=ROOT/'dataset/TopCaw2024'
for p in sorted((top/'imagesTr').glob('*mr*nii.gz')):
    im=nib.load(p); label=top/'cow_seg_labelsTr'/p.name.replace('_0000.nii.gz','.nii.gz')
    rows.append({'dataset':'topcow_mr','case':p.name.split('_')[2],'path':p.relative_to(ROOT).as_posix(),'shape':str(im.shape),'dtype':str(im.get_data_dtype()),'spacing':str(im.header.get_zooms()),'sha256':sha(p),'label_exists':label.exists(),'label_path':label.relative_to(ROOT).as_posix()})
pd.DataFrame(rows).to_csv(OUT/'external_data_qualification.csv',index=False)

# Recompute the split overlap rather than importing conclusions from another project.
sp=ROOT/'dataset/fastMRI_brain_T2/processed/splits/nifti_seed3407'
sets={s:set((sp/f'{s}_cases.txt').read_text().split()) for s in ['train','val','test']}
patients={s:{c.split('_')[0] for c in cs} for s,cs in sets.items()}
split={'series_counts':{s:len(v) for s,v in sets.items()},'patient_counts':{s:len(v) for s,v in patients.items()},'overlaps':{a+'_'+b:sorted(patients[a]&patients[b]) for a,b in [('train','val'),('train','test'),('val','test')]},'source_files':[{'path':(sp/f'{s}_cases.txt').relative_to(ROOT).as_posix(),'sha256':sha(sp/f'{s}_cases.txt')} for s in sets]}
(OUT/'fastmri_split_audit.json').write_text(json.dumps(split,indent=2))
print(json.dumps({'inventory_files':sum(r['files'] for r in inventory),'manifests':len(manifests),'external_series':len(rows),'external_by_dataset':dict(collections.Counter(r['dataset'] for r in rows)),'split':split},indent=2))
