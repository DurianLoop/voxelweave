"""Frozen control residual readouts, patient-disjoint probe fit/check, train only."""
import hashlib,json,argparse
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader,Subset
from pastnet_v2.common import PACKAGE,sha256,write_json
from pastnet_v2.run import load_model,seed_all,code_hashes
from pastnet_v2.data import IntervalDataset,device_batch

ROOT=Path(__file__).resolve().parent
CONTROL=PACKAGE/'runs/full_control_seed3407_vram20'
ARMS={'self':5,'local':13,'extended':17}


def feature_maps(pred,anchors,valid,q):
    """Numpy [32,32,17]. target cannot enter this function."""
    p=torch.from_numpy(pred).float()[None,None]
    smooth=F.avg_pool2d(F.pad(p,(1,1,1,1),mode='reflect'),3,stride=1)[0,0].numpy()
    gy,gx=np.gradient(pred);grad=np.sqrt(gx*gx+gy*gy)
    prev,left,right,nxt=anchors[1:5]
    dp=(left-prev)*valid[1];dn=(nxt-right)*valid[4]
    one=np.ones_like(pred);coarse=(1-q)*left+q*right
    channels=[one,pred,pred**2,smooth-pred,grad,coarse-pred,right-left,dp,dn,
              dn-dp,np.abs(right-left),one*valid[1],one*valid[4],
              (anchors[0]-prev)*valid[0],(anchors[5]-nxt)*valid[5],one*valid[0],one*valid[5]]
    return np.stack(channels,-1).astype(np.float64)


def extract(out):
    m=json.loads((CONTROL/'manifest.json').read_text(encoding='utf-8'))
    c=json.loads((CONTROL/'completion.json').read_text(encoding='utf-8'))
    assert m['code_hashes']==code_hashes() and c['best_sha256']==sha256(CONTROL/'best.pth')
    signature=dict(checkpoint_sha256=c['best_sha256'],data_sha256=sha256(m['data_manifest']),
        script_sha256=sha256(__file__),protocol_sha256=sha256(ROOT/'PROTOCOL_ZH.md'),split='train',grid='z%4=0',
        original_source_hashes=code_hashes())
    cache=out/'cache';cache.mkdir(parents=True,exist_ok=True)
    if (out/'manifest.json').exists():
        assert json.loads((out/'manifest.json').read_text(encoding='utf-8'))==signature,'Cache provenance differs'
    else:write_json(out/'manifest.json',signature)
    ds=IntervalDataset(m['data_manifest'],'train',anchors=6)
    indices=[i for i,(_,z) in enumerate(ds.items) if z%4==0]
    model=load_model('control',CONTROL/'best.pth').cuda().eval()
    records=[]
    for n,(index,batch) in enumerate(zip(indices,DataLoader(Subset(ds,indices),batch_size=1,shuffle=False))):
        case=batch['case_id'][0];patient=batch['patient_id'][0];z=int(batch['z'][0])
        path=cache/f'{case}_{z:03d}.npz'
        if not path.exists():
            data=device_batch(batch,torch.device('cuda'))
            b4=dict(data,anchors=data['anchors'][:,1:5],valid=data['valid'][:,1:5],anchor_z=data['anchor_z'][:,1:5])
            with torch.inference_mode(),torch.autocast('cuda'):
                pred=model(b4).float()[0,:,0]
            target=batch['target'][0,:,0]
            low=F.avg_pool2d(pred[:,None],8)[:,0].cpu().numpy()
            tlow=F.avg_pool2d(target[:,None],8)[:,0].numpy()
            alow=F.avg_pool2d(batch['anchors'][0],8)[:,0].numpy()
            np.savez_compressed(path,pred=pred.cpu().numpy(),target=target.numpy(),low=low,tlow=tlow,
                                anchors=alow,valid=batch['valid'][0].numpy())
        records.append(dict(patient_id=patient,case_id=case,z=z,path=str(path)))
        if (n+1)%25==0:print(f'Frozen train extraction {n+1}/{len(indices)}',flush=True)
    del model;torch.cuda.empty_cache()
    pd.DataFrame(records).to_csv(out/'cache_index.csv',index=False)
    return records


def fit_and_check(out,records):
    patients=sorted({r['patient_id'] for r in records},key=lambda p:hashlib.sha256(('residual-audit-v1:'+p).encode()).hexdigest())
    fit=set(patients[::2]);check=set(patients[1::2]);assert not fit&check
    counts=pd.DataFrame(records).groupby('patient_id').size().to_dict()
    sums={(arm,j):[np.zeros((dim,dim)),np.zeros(dim),0.] for arm,dim in ARMS.items() for j in range(3)}
    for r in records:
        if r['patient_id'] not in fit:continue
        with np.load(r['path']) as d:
            for j in range(3):
                allx=feature_maps(d['low'][j],d['anchors'],d['valid'],(j+1)/4).reshape(-1,17)
                y=(d['tlow'][j]-d['low'][j]).ravel().astype(np.float64)
                weight=1/(counts[r['patient_id']]*len(y))
                for arm,dim in ARMS.items():
                    x=allx[:,:dim];s=sums[(arm,j)]
                    s[0]+=weight*(x.T@x);s[1]+=weight*(x.T@y);s[2]+=weight*len(y)
    coefficients={}
    for key,(xx,xy,n) in sums.items():
        xx/=n;xy/=n
        # Equivalent to centered standardized ridge with an unpenalized intercept.
        variance=np.maximum(np.diag(xx)-xx[0]**2,1e-8);variance[0]=0
        coefficients[key]=np.linalg.solve(xx+.001*np.diag(variance),xy)
    np.savez(out/'coefficients.npz',**{f'{a}_{j}':v for (a,j),v in coefficients.items()})
    write_json(out/'patient_split.json',dict(fit=sorted(fit),check=sorted(check)))
    rows=[]
    for r in records:
        with np.load(r['path']) as d:
            for j in range(3):
                x=feature_maps(d['low'][j],d['anchors'],d['valid'],(j+1)/4)
                pred=d['pred'][j];target=d['target'][j]
                for arm in ('baseline',*ARMS):
                    correction=np.zeros_like(pred)
                    if arm!='baseline':
                        low=x[:,:,:ARMS[arm]]@coefficients[(arm,j)]
                        correction=F.interpolate(torch.tensor(low,dtype=torch.float32)[None,None],size=pred.shape,mode='bilinear',align_corners=False)[0,0].numpy().clip(-.05,.05)
                    error=pred+correction-target;mse=float(np.mean(error.astype(np.float64)**2))
                    rows.append(dict(patient_id=r['patient_id'],case_id=r['case_id'],z=r['z']+j+1,phase=(j+1)/4,
                        group='fit' if r['patient_id'] in fit else 'check',arm=arm,
                        psnr=float(-10*np.log10(max(mse,1e-12))),mse=mse,mae=float(np.abs(error).mean()),
                        correction_rms=float(np.sqrt(np.mean(correction**2)))))
    df=pd.DataFrame(rows);df.to_csv(out/'per_slice.csv',index=False)
    case=df.groupby(['group','arm','patient_id','case_id'])[['psnr','mse','mae','correction_rms']].mean().reset_index()
    p=case.groupby(['group','arm','patient_id'])[['psnr','mse','mae','correction_rms']].mean().reset_index()
    p.to_csv(out/'per_patient.csv',index=False)
    checkframe=p[p.group=='check'];frames={arm:checkframe[checkframe.arm==arm].set_index('patient_id').sort_index() for arm in ('baseline',*ARMS)}
    base=frames['baseline'];hard=base.psnr.nsmallest(int(np.ceil(len(base)*.25))).index
    rng=np.random.default_rng(73019);draw=rng.integers(len(base),size=(10000,len(base)))
    result=dict(fit_patients=len(fit),check_patients=len(check),selection='TRAIN internal exploratory screen, not validation model promotion',arms={})
    for arm,parent in zip(ARMS,('baseline','self','local')):
        a=frames[arm];b=frames[parent];delta=(a.psnr-b.psnr).to_numpy();boot=delta[draw].mean(1)
        total=float((a.psnr-base.psnr).mean());increment=float(delta.mean())
        ci=np.quantile(boot,[.025,.975]).tolist();corrected=np.quantile(boot,[.05/6,1-.05/6]).tolist()
        mae=float((a.mae-base.mae).mean());worst=float((a.psnr-base.psnr).loc[hard].mean());wins=int((delta>0).sum())
        eligible=total>=.05 and increment>=.03 and corrected[0]>0 and wins>=np.ceil(.6*len(base)) and mae<=0 and worst>=0
        result['arms'][arm]=dict(parent=parent,psnr=float(a.psnr.mean()),total_delta=total,increment=increment,
            incremental_ci95=ci,incremental_ci98333=corrected,incremental_wins=wins,mae_delta_vs_baseline=mae,
            worst_quartile_total_delta=worst,eligible_for_validation=bool(eligible))
    result['baseline_psnr']=float(base.psnr.mean())
    result['selected_for_validation']=next((a for a in ARMS if result['arms'][a]['eligible_for_validation']),None)
    write_json(out/'summary.json',result);print(json.dumps(result,indent=2),flush=True)


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'results/train_residual_v1');a=p.parse_args()
    if (a.out/'summary.json').exists():raise FileExistsError('Completed result already exists')
    seed_all(3407);records=extract(a.out);fit_and_check(a.out,records)


if __name__=='__main__':main()
