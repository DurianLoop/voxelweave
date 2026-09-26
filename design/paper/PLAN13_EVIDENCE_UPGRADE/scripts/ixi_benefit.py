"""Recover all 115 IXI same-architecture I3Net pairs on identical odd planes."""
from pathlib import Path
import hashlib, json, sys
import numpy as np
import pandas as pd
import nibabel as nib
from scipy.stats import rankdata

P13=Path(__file__).resolve().parents[1]; ROOT=P13.parents[2]; OUT=P13/'outputs'
R2=ROOT/'baseline/ixi_i3net/runs/full_test115_x2_fast'
R4=ROOT/'baseline/ixi_i3net/runs/full_test115_stable'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def corr(x,y):
    x=rankdata(x,axis=-1); y=rankdata(y,axis=-1)
    x=x-x.mean(-1,keepdims=True); y=y-y.mean(-1,keepdims=True)
    return (x*y).sum(-1)/np.sqrt((x*x).sum(-1)*(y*y).sum(-1))
def partial(x,y,z):
    a,b,c=corr(x,y),corr(x,z),corr(y,z)
    return (a-b*c)/np.sqrt((1-b*b)*(1-c*c))
def interval(x): return np.nanquantile(x,[.025,.975]).tolist()
def features(anchors):
    cv=[]; adj=[]
    for j in range(anchors.shape[2]-1):
        a=anchors[:,:,j].astype(float); b=anchors[:,:,j+1].astype(float)
        mask=(abs(a)>.01*max(abs(a).max(),1e-6))|(abs(b)>.01*max(abs(b).max(),1e-6))
        assert mask.any(); adj.append(abs(a-b)[mask].mean())
    for j in range(1,anchors.shape[2]-1):
        t=anchors[:,:,j]; p=.5*(anchors[:,:,j-1]+anchors[:,:,j+1])
        mask=abs(t)>.01*max(abs(t).max(),1e-6)
        assert mask.any(); cv.append(float(abs(p-t)[mask].mean()))
    v=anchors[np.isfinite(anchors)&(abs(anchors)>0)]
    scale=max(float(np.diff(np.percentile(v,[1,99]))[0]),1e-6)
    return {'anchor_cv':float(np.median(cv)),'adjacent_mae':float(np.median(adj)),
        'anchor_cv_acquired_normalized':float(np.median(cv))/scale,
        'adjacent_mae_acquired_normalized':float(np.median(adj))/scale,'acquired_range':scale}

test=ROOT/'dataset/IXI/splits/seed3407/test_cases.txt'
cases=test.read_text(encoding='utf-8').split()
assert len(cases)==115 and len(set(cases))==115
meta=pd.read_csv(ROOT/'dataset/IXI/metadata/ixi_cases.csv').set_index('case_id')
records=[]; planes=[]; files=[]; geometry=[]
for i,c in enumerate(cases,1):
    src=Path(meta.loc[c,'T2_path']); p2=R2/'model_outputs'/('diff_'+src.name); p4=R4/'model_outputs'/('diff_'+src.name)
    imgs=[nib.load(p) for p in [src,p2,p4]]
    assert all(np.allclose(im.affine,imgs[0].affine,rtol=0,atol=1e-6) for im in imgs)
    assert all(im.shape[:2]==imgs[0].shape[:2] for im in imgs)
    arrays=[im.get_fdata(dtype=np.float32) for im in imgs]; y,a,b=arrays
    assert all(np.isfinite(v).all() for v in arrays)
    depth=min(v.shape[2] for v in arrays)
    zs=list(range(1,depth-1,2)); assert zs
    f=features(y[:,:,::4])
    for z in zs:
        t=y[:,:,z]; mask=abs(t)>.01*max(abs(t).max(),1e-6); assert mask.any()
        es=[float(abs(v[:,:,z].astype(float)-t)[mask].mean()) for v in [a,b]]
        l2=.5*(y[:,:,z-1]+y[:,:,z+1])
        left=(z//4)*4; right=left+4; assert right<y.shape[2]
        l4=y[:,:,left]*(1-(z-left)/4)+y[:,:,right]*((z-left)/4)
        planes.append({'case':c,'z':z,'mask_pixels':int(mask.sum()),'mae_x2':es[0],'mae_x4':es[1],
             'linear_mae_x2':float(abs(l2-t)[mask].mean()),'linear_mae_x4':float(abs(l4-t)[mask].mean())})
    g=pd.DataFrame(planes[-len(zs):])
    rec={'case':c,'patient_cluster':c,'model':'i3net','planes':len(zs),**f,
        **{k:float(g[k].mean()) for k in ['mae_x2','mae_x4','linear_mae_x2','linear_mae_x4']}}
    rec['benefit']=rec['mae_x4']-rec['mae_x2']; records.append(rec)
    geometry.append({'case':c,'depth_raw':y.shape[2],'depth_x2':a.shape[2],'depth_x4':b.shape[2],
        'common_generated_planes':len(zs),'max_affine_difference':max(float(abs(im.affine-imgs[0].affine).max()) for im in imgs)})
    for p in [src,p2,p4]: files.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size})
    if i%10==0: print('IXI recovery',i,'/115',flush=True)
g=pd.DataFrame(records); g.to_csv(OUT/'ixi_i3net_benefit_per_case.csv',index=False)
pd.DataFrame(planes).to_csv(OUT/'ixi_i3net_benefit_per_plane.csv',index=False)
pd.DataFrame(geometry).to_csv(OUT/'ixi_i3net_geometry.csv',index=False)
idx=np.random.default_rng(20260908).integers(0,115,(10000,115)); rows=[]; budgets=[]
for score in ['anchor_cv','adjacent_mae','anchor_cv_acquired_normalized','adjacent_mae_acquired_normalized']:
    x=g[score].to_numpy(); y=g.benefit.to_numpy(); z=g.mae_x4.to_numpy()
    raw=corr(x[idx],y[idx]); adj=partial(x[idx],y[idx],z[idx])
    rows.append({'score':score,'rho':float(corr(x,y)),'ci_low':interval(raw)[0],'ci_high':interval(raw)[1],
        'partial_rho_given_x4':float(partial(x,y,z)),'partial_ci_low':interval(adj)[0],'partial_ci_high':interval(adj)[1],
        'valid_partial_bootstrap':int(np.isfinite(adj).sum())})
    for budget in [.1,.2,.3,.5]:
        k=int(np.ceil(115*budget)); order=np.argsort(x,kind='stable')[::-1][:k]
        selected=float(y[order].mean()); random=float(y.mean()); oracle=float(np.sort(y)[-k:].mean())
        bs=np.take_along_axis(y[idx],np.argsort(x[idx],axis=1,kind='stable')[:,::-1][:,:k],axis=1).mean(1)-y[idx].mean(1)
        budgets.append({'score':score,'budget':budget,'selected_benefit':selected,'random_expected':random,
            'gain_above_random':selected-random,'ci_low':interval(bs)[0],'ci_high':interval(bs)[1],
            'oracle_normalized_gain':(selected-random)/(oracle-random)})
pd.DataFrame(rows).to_csv(OUT/'ixi_i3net_benefit_correlations.csv',index=False)
pd.DataFrame(budgets).to_csv(OUT/'ixi_i3net_benefit_budgets.csv',index=False)
checkpoints=[]
for r in [R2,R4]:
    p=r/'checkpoints/i3net_epoch_best.pth'; checkpoints.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p)})
manifest={'status':'COMPLETE EXPLORATORY RECOVERED-OUTPUT EXPERIMENT','cases':len(g),'planes':len(planes),
    'same_architecture_not_same_weights':True,'bootstrap':10000,'seed':20260908,'checkpoints':checkpoints,
    'test_list_sha256':sha(test),'protocol_sha256':sha(P13/'PROTOCOL.md'),'inputs':files,
    'means':g[['mae_x2','mae_x4','benefit','linear_mae_x2','linear_mae_x4']].mean().to_dict(),
    'positive_benefit_cases':int((g.benefit>0).sum()),'correlations':rows}
(OUT/'ixi_i3net_run_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(pd.DataFrame(rows).to_string(index=False)); print('IXI COMPLETE',flush=True)
