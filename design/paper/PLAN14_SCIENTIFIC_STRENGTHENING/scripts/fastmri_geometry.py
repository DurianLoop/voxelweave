"""Read DICOM geometry for the papers' historical test-24; write only Plan 14."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
import pandas as pd
import nibabel as nib
P14=Path(__file__).resolve().parents[1]; ROOT=P14.parents[2]; OUT=P14/'outputs'
sys.path[:0]=[str(ROOT/'design'),str(ROOT)]
from pastnet_v2.prepare import recover_fastmri
source=ROOT/'dataset/fastMRI_brain_T2/processed/splits/nifti_seed3407/test_cases.txt'
cases=source.read_text().split(); records=[]
for c in cases:
    path=ROOT/'dataset/fastMRI_brain_T2/processed/nifti'/(c+'.nii.gz')
    r={'case_id':c,'path':str(path),'dataset':'fastmri'}
    try:
        g=recover_fastmri(r)
        old=nib.load(path).affine[:3,:3]; axes=old/np.linalg.norm(old,axis=0)
        delta=float(np.max(np.abs(axes-np.array(g['axes']))))
        records.append({'case':c,'status':'PASS','max_orientation_entry_difference':delta,**g})
    except Exception as exc: records.append({'case':c,'status':'FAIL','reason':type(exc).__name__+': '+str(exc)})
    print(c,records[-1]['status'],flush=True)
(OUT/'fastmri_test24_geometry.json').write_text(json.dumps({'status':'COMPLETE','test_list_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_function_sha256':hashlib.sha256((ROOT/'design/pastnet_v2/prepare.py').read_bytes()).hexdigest(),'records':records},indent=2))
pd.DataFrame([{'case':r['case'],'status':r['status'],'actual_z_spacing':r.get('spacing',[np.nan]*3)[2],'nonuniformity':r.get('nonuniformity',np.nan),'orientation_delta':r.get('max_orientation_entry_difference',np.nan),'reason':r.get('reason','')} for r in records]).to_csv(OUT/'fastmri_test24_geometry.csv',index=False)
print('Geometry passed',sum(r['status']=='PASS' for r in records),'/',len(records))
