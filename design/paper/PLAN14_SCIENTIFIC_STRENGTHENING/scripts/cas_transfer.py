"""Locked TopCoW bright-anchor rule transferred once to all CAS2023 images."""
from pathlib import Path
import json,hashlib,time
import numpy as np
import pandas as pd
import nibabel as nib
from topcow_experiment import interpolate,fg,mean
from bright_anchor_experiment import bright_mask
from stat_utils import corr,ci,naurc
P14=Path(__file__).resolve().parents[1]; ROOT=P14.parents[2]; OUT=P14/'outputs'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    files=sorted((ROOT/'dataset/CAS2023/data').glob('*.nii.gz')); assert len(files)==100
    per=P14/'cas_records';per.mkdir(exist_ok=True);protocol_hash=sha(P14/'PROTOCOL.md')
    provenance=[];start=time.perf_counter();oldhash={r['sha256'] for r in json.loads((OUT/'topcow_run_manifest.json').read_text())['inputs']}
    for i,path in enumerate(files,1):
        case=path.name.split('.')[0];lp=ROOT/'dataset/CAS2023/mask'/path.name;assert lp.exists()
        hashes=[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in [path,lp]];assert not any(x['sha256'] in oldhash for x in hashes)
        provenance.extend(hashes);dest=per/(case+'.csv')
        if dest.exists():continue
        im=nib.load(path);li=nib.load(lp);assert im.shape==li.shape and np.allclose(im.affine,li.affine,rtol=0,atol=1e-5)
        v=im.get_fdata(dtype=np.float32);lab=np.asarray(li.dataobj);assert np.isfinite(v).all() and np.isfinite(lab).all()
        assert set(np.unique(lab)).issubset({0,1}); assert (lab>0).any()
        acq={z:fg(v[:,:,z]) for z in range(0,v.shape[2],4)};bright={z:bright_mask(v[:,:,z]) for z in acq}
        zs=[z for z in range(1,v.shape[2],2) if all(phase+((z-phase)//4)*4-4>=0 and phase+((z-phase)//4)*4+8<v.shape[2] for phase in [0,2])]
        assert zs and set(z%4 for z in zs)=={1,3};rows=[]
        for z in zs:
            left=(z//4)*4;mask=acq[left]|acq[left+4];bm=bright[left]|bright[left+4];vessel=lab[:,:,z]>0;y=v[:,:,z]
            l0=interpolate(v,z,4,0,'linear');c0=interpolate(v,z,4,0,'cubic');l2=interpolate(v,z,4,2,'linear');c2=interpolate(v,z,4,2,'cubic')
            errors={'LC':(mean(abs(l0-y),mask),mean(abs(l0-y),vessel)),'CL':(mean(abs(c0-y),mask),mean(abs(c0-y),vessel))}
            for tag,a,b in [('LC_shared',l0,c0),('LC_disjoint',l0,c2),('CL_shared',c0,l0),('CL_disjoint',c0,l2)]:
                pair,condition=tag.split('_');diff=abs(a-b)
                rows.append({'case':case,'z':z,'residue':z%4,'pair':pair,'condition':condition,'baseline_disagreement':mean(diff,mask),'bright_disagreement':mean(diff,bm),
                             'error':errors[pair][0],'vessel_error':errors[pair][1],'mask_pixels':int(mask.sum()),'bright_pixels':int(bm.sum()),'vessel_pixels':int(vessel.sum()),'vessel_pixels_covered':int((bm&vessel).sum())})
        pd.DataFrame(rows).to_csv(dest,index=False)
        (per/(case+'.json')).write_text(json.dumps({'case':case,'shape':im.shape,'affine':im.affine.tolist(),'spacing_from_header':list(map(float,im.header.get_zooms())),
            'identity_affine':bool(np.allclose(im.affine,np.eye(4))),'protocol_sha256':protocol_hash,'inputs':hashes},indent=2))
        print(f'CAS transfer {i}/100 {case} elapsed={time.perf_counter()-start:.1f}s',flush=True)
    p=pd.concat([pd.read_csv(per/(x.name.split('.')[0]+'.csv'),dtype={'case':str}) for x in files],ignore_index=True)
    p.to_csv(OUT/'cas_transfer_per_plane.csv',index=False)
    g=p.groupby(['case','pair','condition','residue'])[['baseline_disagreement','bright_disagreement','error','vessel_error']].mean().groupby(['case','pair','condition']).mean().reset_index()
    assert g[['baseline_disagreement','bright_disagreement','error','vessel_error']].notna().all().all()
    g.to_csv(OUT/'cas_transfer_per_case.csv',index=False);cases=sorted(g.case.unique());idx=np.random.default_rng(20260909).integers(0,100,(10000,100));rows=[]
    for context in ['shared','disjoint']:
        points=[];replicates=[];ids=[]
        for pair in ['LC','CL']:
            a=g[g.pair.eq(pair)&g.condition.eq(context)].set_index('case').loc[cases];x=a.bright_disagreement.to_numpy();baseline=a.baseline_disagreement.to_numpy()
            for endpoint in ['error','vessel_error']:
                y=a[endpoint].to_numpy();raw=corr(x[idx],y[idx]);d=raw-corr(baseline[idx],y[idx]);risk=naurc(y[idx],x[idx])-naurc(y[idx],baseline[idx])
                row={'pair':pair,'condition':context,'endpoint':endpoint,'baseline_rho':float(corr(baseline,y)),'bright_rho':float(corr(x,y)),'bright_ci_low':ci(raw)[0],'bright_ci_high':ci(raw)[1],
                     'delta_rho':float(corr(x,y)-corr(baseline,y)),'delta_ci_low':ci(d)[0],'delta_ci_high':ci(d)[1],'baseline_naurc':float(naurc(y,baseline)),'bright_naurc':float(naurc(y,x)),
                     'delta_naurc':float(naurc(y,x)-naurc(y,baseline)),'risk_delta_ci_low':ci(risk)[0],'risk_delta_ci_high':ci(risk)[1]};rows.append(row)
                if endpoint=='vessel_error':points.append(row['delta_rho']);replicates.append(d);ids.append(len(rows)-1)
        points=np.array(points);replicates=np.stack(replicates,axis=1);sd=replicates.std(0,ddof=1);critical=np.quantile(np.max(abs((replicates-points)/sd),axis=1),.95)
        for j,k in enumerate(ids):rows[k].update(simultaneous_low=float(points[j]-critical*sd[j]),simultaneous_high=float(points[j]+critical*sd[j]))
    pd.DataFrame(rows).to_csv(OUT/'cas_transfer_rankings.csv',index=False)
    (OUT/'cas_transfer_manifest.json').write_text(json.dumps({'status':'COMPLETE FIXED-RULE EXTERNAL TRANSFER','cases':100,'planes':len(p)//4,'bootstrap':10000,'seed':20260909,'threshold_percentile':95,
        'threshold_searched':False,'protocol_sha256':protocol_hash,'script_sha256':sha(Path(__file__)),'bright_rule_script_sha256':sha(P14/'scripts/bright_anchor_experiment.py'),
        'inputs':provenance,'identical_file_hashes_with_topcow':0,'geometry_note':'Array-grid interpolation; unknown header provenance does not certify millimetre spacing.'},indent=2))
    print(pd.DataFrame(rows).to_string(index=False));print('CAS COMPLETE',flush=True)
if __name__=='__main__':main()
