"""Independent checks of saved statistics and NumPy full-FFT readout."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader,Subset
from pastnet_v2.common import sha256,write_json
from pastnet_v2.run import code_hashes,load_model,seed_all
from pastnet_v2.data import IntervalDataset,device_batch

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results/v1'


def main():
    seed_all(3407);torch.backends.cuda.matmul.allow_tf32=False
    m=json.loads((OUT/'manifest.json').read_text(encoding='utf-8'))
    assert m['script_sha256']==sha256(ROOT/'run.py')
    assert m['protocol_sha256']==sha256(ROOT/'PROTOCOL_ZH.md')
    assert m['original_source_hashes']==code_hashes()
    split_path=ROOT.parent/'pastnet_residual_audit/results/train_residual_v1/patient_split.json'
    assert sha256(split_path)==m['split_sha256']
    split=json.loads(split_path.read_text())
    assert m['fit']==sorted(split['fit']) and m['check']==sorted(split['check'])
    coefficients=dict(np.load(OUT/'coefficients.npz'));stats=np.load(OUT/'sufficient_statistics.npz')
    checks={};max_coeff_error=0.
    # Solve the standardized system using least-squares, independently of solve().
    for name in ('shared','low','mid','high'):
        names=('low','mid','high') if name=='shared' else (name,)
        xx=sum(stats['xx_'+k] for k in names);xy=sum(stats['xy_'+k] for k in names)
        intercept=name in ('shared','low');active=np.arange(65) if intercept else np.arange(1,65)
        var=np.maximum(np.diag(xx)-(xx[0]**2 if intercept else 0),1e-8);var[0]=0
        system=xx+.001*np.diag(var)
        ref=np.linalg.lstsq(system[np.ix_(active,active)],xy[active],rcond=None)[0]
        err=float(np.max(np.abs(ref-coefficients[name][active])));max_coeff_error=max(err,max_coeff_error)
        assert err<1e-7,(name,err)
        if not intercept:assert coefficients[name][0]==0
    frame=pd.read_csv(OUT/'per_slice.csv',dtype={'patient_id':str,'case_id':str})
    assert len(frame)==340*3*3 and not frame.duplicated(['case_id','z','arm']).any()
    saved=frame.set_index(['case_id','z','arm'])
    control=ROOT.parent/'pastnet_v2/runs/full_control_seed3407_vram20'
    source=json.loads((control/'manifest.json').read_text())
    assert sha256(control/'best.pth')==m['checkpoint_sha256']
    assert sha256(source['data_manifest'])==m['data_sha256']
    ds=IntervalDataset(source['data_manifest'],'train')
    chosen=(sorted(split['fit'])[0],sorted(split['check'])[0],'113452254821')
    indices=[next(i for i,(case,z) in enumerate(ds.items) if z==0 and ds.records[case]['patient_id']==p) for p in chosen]
    model=load_model('control',control/'best.pth').cuda().eval();features=[]
    def capture(module,inputs):features.append(inputs[0])
    handle=model.base.single.decoder.register_forward_pre_hook(capture)
    max_mse_error=0.;max_mae_error=0.
    try:
        for batch in DataLoader(Subset(ds,indices),batch_size=1):
            features.clear();b=device_batch(batch,torch.device('cuda'))
            with torch.no_grad(),torch.autocast('cuda'):p=model(b).float()[0,:,0].cpu().numpy()
            assert len(features)==2
            x=features[-1].float().cpu().numpy().astype(np.float64)
            target=batch['target'][0,:,0].numpy().astype(np.float64)
            h,w=x.shape[-2:];fy=np.fft.fftfreq(h)[:,None];fx=np.fft.fftfreq(w)[None,:]
            r=np.sqrt(fy**2+fx**2);masks=(r<.10,(r>=.10)&(r<.28),r>=.28)
            def affine(c):return np.einsum('qchw,c->qhw',x,c[1:],optimize=True)+c[0]
            corrections={'baseline':np.zeros_like(p),'shared':affine(coefficients['shared']),
                'frequency':sum(np.fft.ifft2(np.fft.fft2(affine(coefficients[k]),norm='ortho')*mask,norm='ortho').real
                                for k,mask in zip(('low','mid','high'),masks))}
            for arm,correction in corrections.items():
                err=p.astype(np.float64)+correction.clip(-.05,.05)-target
                for j in range(3):
                    row=saved.loc[(batch['case_id'][0],j+1,arm)]
                    de=abs(float(np.mean(err[j]**2))-row.mse);ae=abs(float(np.mean(np.abs(err[j])))-row.mae)
                    max_mse_error=max(max_mse_error,de);max_mae_error=max(max_mae_error,ae)
                    assert de<1e-8 and ae<1e-7,(batch['case_id'][0],arm,j,de,ae)
    finally:handle.remove()
    # All baseline slices must match the independent earlier prediction cache.
    cache=ROOT.parent/'pastnet_residual_audit/results/train_residual_v1'
    idx=pd.read_csv(cache/'cache_index.csv',dtype={'patient_id':str,'case_id':str});baseline_error=0.
    for row in idx.itertuples():
        with np.load(row.path) as d:
            for j in range(3):
                err=d['pred'][j].astype(np.float64)-d['target'][j].astype(np.float64)
                baseline_error=max(baseline_error,abs(float(np.mean(err**2))-saved.loc[(row.case_id,row.z+j+1,'baseline'),'mse']))
    assert baseline_error<1e-8
    checks.update(source_protocol_checkpoint_and_split_hashes=True,patient_disjoint=True,complete_1020_slices=True,
        independent_lstsq_max_coefficient_difference=max_coeff_error,
        numpy_full_fft_verified_patients=list(chosen),numpy_mse_max_difference=max_mse_error,
        numpy_mae_max_difference=max_mae_error,all_baseline_cached_mse_max_difference=baseline_error,
        verification_script_sha256=sha256(__file__))
    write_json(OUT/'independent_verification.json',checks);print(json.dumps(checks,indent=2))


if __name__=='__main__':main()
