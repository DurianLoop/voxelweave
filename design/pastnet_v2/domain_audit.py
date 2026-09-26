"""Fixed train/validation domain characterization; no external model selection."""
from __future__ import annotations
import argparse
from pathlib import Path
import json

import nibabel as nib
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter
from skimage.transform import resize

from .common import PACKAGE,write_csv,write_json
from .prepare import records_for,geometry


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path,default=PACKAGE/'results/domain_audit')
    a=p.parse_args()
    if a.out.exists():
        raise FileExistsError(a.out)
    fm=json.loads((PACKAGE/'manifests/fastmri/fold_00.json').read_text())['records']
    groups=dict(fastmri=[r for r in fm if r['split'] in ('train','val')],
                ixi=[r for r in records_for('ixi') if r['split'] in ('train','val')],
                ningxia=[r for r in records_for('ningxia',0) if r['split'] in ('train','val')])
    rows=[]
    for dataset,records in groups.items():
        for i,rec in enumerate(records):
            image=nib.load(rec['path']); geo=rec.get('geometry') or geometry(rec)
            spacing=np.array(geo['spacing']); shape=np.array(image.shape)
            # Header statistics cover all train/validation series. Pixel stats use
            # fixed first 12 series per domain, recorded explicitly, no test access.
            row=dict(dataset=dataset,case_id=rec['case_id'],patient_id=rec['patient_id'],split=rec['split'],
                depth=int(shape[2]),sparse_anchors=int((shape[2]+3)//4),
                sx=spacing[0],sy=spacing[1],sz=spacing[2],gap_x4=spacing[2]*4,
                fov_x=shape[0]*spacing[0],fov_y=shape[1]*spacing[1],
                spacing_known=geo['spacing_known'],orientation_known=geo['orientation_known'],
                axes=json.dumps(geo['axes']),source=geo['source'],
                intensity_sampled=i<12,raw_p01='',raw_p99='',adjacent_change='',
                sparse_change='',highpass_mad_proxy='')
            if i<12:
                raw=image.get_fdata(dtype=np.float32)
                observed=raw[:,:,::4]
                v=(raw-float(observed.min()))/max(float(observed.max()-observed.min()),1e-8)
                v=resize(v,(128,128,v.shape[2]),preserve_range=True,anti_aliasing=True)
                hp=v-gaussian_filter(v,sigma=(1,1,0))
                row.update(raw_p01=float(np.quantile(raw,.01)),raw_p99=float(np.quantile(raw,.99)),
                    adjacent_change=float(np.abs(np.diff(v,axis=2)).mean()),
                    sparse_change=float(np.abs(np.diff(v[:,:,::4],axis=2)).mean()),
                    highpass_mad_proxy=float(np.median(np.abs(hp-np.median(hp)))/.67449))
            rows.append(row)
        print(f'domain audit {dataset}: {len(records)} headers, {min(len(records),12)} fixed pixel samples',flush=True)
    write_csv(a.out/'per_series.csv',rows)
    df=pd.DataFrame(rows)
    known=df[df.spacing_known==1]
    summary=known.groupby('dataset')[['sx','sy','sz','gap_x4','fov_x','fov_y','depth','sparse_anchors']].agg(['min','median','max'])
    summary.to_csv(a.out/'geometry_summary.csv')
    write_json(a.out/'manifest.json',dict(no_test_access=True,ningxia_reference_fold=0,
        intensity_sampling='first 12 train/validation series in fixed manifest order per domain',
        noise_proxy_is_not_noise_estimate=True,spacing_unknown_excluded_from_summary=True))
    print(summary.to_string(),flush=True)


if __name__=='__main__':
    main()
