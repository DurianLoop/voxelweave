"""Native-resolution external MRA experiment with acquired-only score support."""
from pathlib import Path
import os,json,hashlib,time
os.environ.setdefault('OPENBLAS_NUM_THREADS','2')
os.environ.setdefault('OMP_NUM_THREADS','2')
import numpy as np
import pandas as pd
import nibabel as nib
P14=Path(__file__).resolve().parents[1]; ROOT=P14.parents[2]; OUT=P14/'outputs'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def weights(z,grid):
    out=[]
    for a in grid:
        v=1.
        for b in grid:
            if a!=b: v*=float(z-b)/(a-b)
        out.append(v)
    return np.asarray(out,dtype=np.float32)
def interpolate(v,z,stride,phase,method):
    left=phase+((z-phase)//stride)*stride
    grid=[left,left+stride] if method=='linear' else [left-stride,left,left+stride,left+2*stride]
    if min(grid)<0 or max(grid)>=v.shape[2]: raise ValueError('Unbracketed query')
    w=weights(z,grid); p=np.zeros(v.shape[:2],dtype=np.float32)
    for a,b in zip(w,grid): p+=a*v[:,:,b]
    return p
def fg(v): return abs(v)>.01*max(float(abs(v).max()),1e-6)
def mean(v,mask): return float(np.mean(v[mask],dtype=np.float64)) if mask.any() else np.nan
def pair_stats(a,b,y,mask):
    ea=(a-y)[mask].astype(np.float64); eb=(b-y)[mask].astype(np.float64)
    total=.5*np.mean(ea*ea+eb*eb); diff=ea-eb
    observable=.25*np.mean(diff*diff)
    return {'error':.5*(np.mean(abs(ea))+np.mean(abs(eb))),'disagreement':float(np.mean(abs(diff))),
            'observable':float(observable/total) if total>0 else np.nan,'total_energy':float(total)}
def features(v):
    anchors=v[:,:,::4]; cv=[]; adj=[]
    for j in range(anchors.shape[2]-1):
        a,b=anchors[:,:,j],anchors[:,:,j+1]; adj.append(mean(abs(a-b),fg(a)|fg(b)))
    for j in range(1,anchors.shape[2]-1):
        y=anchors[:,:,j]; cv.append(mean(abs(.5*(anchors[:,:,j-1]+anchors[:,:,j+1])-y),fg(y)))
    vals=anchors[np.isfinite(anchors)&(abs(anchors)>0)]
    scale=max(float(np.diff(np.percentile(vals,[1,99]))[0]),1e-6)
    return {'anchor_cv':float(np.median(cv)),'adjacent_mae':float(np.median(adj)),'acquired_range':scale}

def main():
    qualification=pd.read_csv(OUT/'external_data_qualification.csv',dtype={'case':str})
    q=qualification[qualification.dataset.eq('topcow_mr')]; assert len(q)==125 and q.label_exists.astype(bool).all()
    per=P14/'case_records'; per.mkdir(exist_ok=True)
    started=time.perf_counter(); geometry=[]; source_hashes=[]
    for i,r in enumerate(q.itertuples(),1):
        dest=per/(r.case+'.csv'); bdest=per/(r.case+'_benefit.csv'); meta=per/(r.case+'.json')
        if dest.exists() and bdest.exists() and meta.exists():
            info=json.loads(meta.read_text()); geometry.append(info['geometry']); source_hashes.extend(info['inputs']); continue
        p=ROOT/r.path; lp=ROOT/r.label_path
        im=nib.load(p); lm=nib.load(lp)
        assert im.shape==lm.shape and np.allclose(im.affine,lm.affine,rtol=0,atol=1e-5)
        v=im.get_fdata(dtype=np.float32); lab=np.asarray(lm.dataobj)
        assert np.isfinite(v).all() and np.isfinite(lab).all()
        assert set(np.unique(lab)).issubset({0,1,2,3,4,5,6,7,8,9,10,11,12,15})
        f=features(v); depth=v.shape[2]; zs=[]
        for z in range(1,depth,2):
            if all(phase+((z-phase)//4)*4-4>=0 and phase+((z-phase)//4)*4+8<depth for phase in [0,2]): zs.append(z)
        assert zs and set(z%4 for z in zs)=={1,3}
        rows=[]; benefits=[]
        for z in zs:
            y=v[:,:,z]; left=(z//4)*4
            masks={'acquired':fg(v[:,:,left])|fg(v[:,:,left+4]),'full':np.ones(y.shape,dtype=bool),'gt':fg(y)}
            vessel=lab[:,:,z]>0
            l0=interpolate(v,z,4,0,'linear'); c0=interpolate(v,z,4,0,'cubic')
            lshift=interpolate(v,z,4,2,'linear'); cshift=interpolate(v,z,4,2,'cubic')
            pairings={'LC_shared':(l0,c0),'LC_disjoint':(l0,cshift),'CL_disjoint':(c0,lshift)}
            for mask_name,mask in masks.items():
                if not mask.any(): raise RuntimeError(f'{r.case}/{z} empty {mask_name} support')
                fixed={'linear_error':mean(abs(l0-y),mask),'cubic_error':mean(abs(c0-y),mask)}
                for tag,(a,b) in pairings.items():
                    model,condition=tag.split('_')
                    rows.append({'case':r.case,'z':z,'residue':z%4,'pair':model,'condition':condition,'mask':mask_name,
                                 'mask_pixels':int(mask.sum()),'vessel_pixels':int(vessel.sum()),**fixed,**pair_stats(a,b,y,mask),
                                 'linear_vessel_error':mean(abs(l0-y),vessel),'cubic_vessel_error':mean(abs(c0-y),vessel)})
                    if tag=='LC_shared': rows.append({**rows[-1],'pair':'CL'})
            for method,p4 in [('linear',l0),('cubic',c0)]:
                p2=interpolate(v,z,2,0,method)
                mask=masks['acquired']
                benefits.append({'case':r.case,'z':z,'residue':z%4,'model':method,'mae_x4':mean(abs(p4-y),mask),'mae_x2':mean(abs(p2-y),mask),
                                 'vessel_mae_x4':mean(abs(p4-y),vessel),'vessel_mae_x2':mean(abs(p2-y),vessel),
                                 'vessel_pixels':int(vessel.sum()),**f})
        pd.DataFrame(rows).to_csv(dest,index=False); pd.DataFrame(benefits).to_csv(bdest,index=False)
        geo={'case':r.case,'shape':list(v.shape),'spacing':list(map(float,im.header.get_zooms())),
             'affine_max_difference':float(abs(im.affine-lm.affine).max()),'eligible_planes':len(zs),'vessel_planes':int(sum((lab[:,:,z]>0).any() for z in zs)),
             'label_values':np.unique(lab).tolist(),**f}
        inputs=[{'path':str(x.relative_to(ROOT)),'sha256':sha(x)} for x in [p,lp]]
        info={'geometry':geo,'inputs':inputs,'protocol_sha256':sha(P14/'PROTOCOL.md'),'script_sha256':sha(Path(__file__))}
        meta.write_text(json.dumps(info,indent=2)); geometry.append(geo); source_hashes.extend(inputs)
        print(f'TopCoW {i}/125 case={r.case} planes={len(zs)} vessel_planes={geo["vessel_planes"]} elapsed={time.perf_counter()-started:.1f}s',flush=True)
    pd.concat([pd.read_csv(per/(str(c)+'.csv'),dtype={'case':str}) for c in q.case],ignore_index=True).to_csv(OUT/'topcow_per_plane.csv',index=False)
    pd.concat([pd.read_csv(per/(str(c)+'_benefit.csv'),dtype={'case':str}) for c in q.case],ignore_index=True).to_csv(OUT/'topcow_benefit_per_plane.csv',index=False)
    pd.DataFrame(geometry).to_csv(OUT/'topcow_geometry.csv',index=False)
    (OUT/'topcow_run_manifest.json').write_text(json.dumps({'status':'COMPLETE','cases':len(q),'source':'external public challenge training images; no estimator fitting',
        'protocol_sha256':sha(P14/'PROTOCOL.md'),'script_sha256':sha(Path(__file__)),'inputs':source_hashes,'elapsed_this_invocation_seconds':time.perf_counter()-started},indent=2))
    print('TOPCOW COMPLETE',flush=True)

if __name__=='__main__': main()
