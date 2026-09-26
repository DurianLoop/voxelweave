"""Read-only train diagnostic; no network updates and no validation selection."""
import argparse, json, math, time
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, Subset
from pastnet_v2.common import PACKAGE, sha256, write_json
from pastnet_v2.run import load_model, code_hashes, seed_all
from pastnet_v2.data import IntervalDataset, device_batch
from pastnet_v2.losses import objective, reverse_batch

ROOT=Path(__file__).resolve().parent
CONTROL=PACKAGE/'runs/full_control_seed3407_vram20'


def bands(x):
    h,w=x.shape[-2:]
    fy=torch.fft.fftfreq(h,device=x.device)[:,None]
    fx=torch.fft.fftfreq(w,device=x.device)[None,:]
    radius=(fy.square()+fx.square()).sqrt()
    spectrum=torch.fft.fft2(x.float(),norm='ortho')
    return [torch.fft.ifft2(spectrum*m,norm='ortho').real for m in
            (radius<.10,(radius>=.10)&(radius<.28),radius>=.28)]


def terms(pred,target,coarse,base,reverse):
    e=pred-target;flat=e.flatten(0,1)
    kernel=e.new_tensor([[0,1,0],[1,-4,1],[0,1,0]]).view(1,1,3,3)
    interval=F.pad(e[:,:,0],(0,0,0,0,1,1));sq=flat.square().flatten(1)
    return dict(charb=(e.square()+1e-6).sqrt().mean(),mse=.35*e.square().mean(),
        grad=.04*((flat[:,:,1:]-flat[:,:,:-1]).abs().mean()+(flat[:,:,:,1:]-flat[:,:,:,:-1]).abs().mean()),
        lap=.003*F.conv2d(flat,kernel,padding=1).abs().mean(),
        z=.01*(interval[:,:-2]-2*interval[:,1:-1]+interval[:,2:]).abs().mean(),
        symmetry=.002*F.l1_loss(pred,reverse),residual=.0008*(pred-coarse).abs().mean(),
        base_guard=.005*(pred-base).abs().mean(),
        tail=.2*sq.topk(math.ceil(sq.shape[1]*.1),dim=1,sorted=False).values.mean())


class FixedOutputs:
    def __init__(self,pred,base,reverse):self.pred,self.base,self.reverse=pred,base,reverse
    def forward_components(self,batch):return dict(prediction=self.pred,base_prediction=self.base)
    def __call__(self,batch):return self.reverse.flip(1)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--smoke',action='store_true');args=parser.parse_args()
    out=ROOT/'results'/('smoke' if args.smoke else 'v1')
    if (out/'summary.json').exists():raise FileExistsError(out)
    out.mkdir(parents=True,exist_ok=True);seed_all(3407);torch.set_num_threads(4)
    manifest=json.loads((CONTROL/'manifest.json').read_text(encoding='utf-8'))
    completion=json.loads((CONTROL/'completion.json').read_text(encoding='utf-8'))
    assert manifest['code_hashes']==code_hashes()
    assert sha256(CONTROL/'best.pth')==completion['best_sha256']
    assert sha256(manifest['data_manifest'])==manifest['data_sha256']
    ds=IntervalDataset(manifest['data_manifest'],'train')
    indices=[i for i,(_,z) in enumerate(ds.items) if z%4==0]
    if args.smoke:indices=indices[:2]
    write_json(out/'manifest.json',dict(checkpoint_sha256=completion['best_sha256'],
        data_sha256=manifest['data_sha256'],source_hashes=code_hashes(),script_sha256=sha256(__file__),
        protocol_sha256=sha256(ROOT/'PROTOCOL_ZH.md'),split='train',intervals=len(indices),
        validation_used=False,test_used=False,weights_updated=False,smoke=args.smoke))
    model=load_model('control',CONTROL/'best.pth').cuda().eval()
    for p in model.parameters():p.requires_grad_(False)
    captures={k:[] for k in ('decoder','detail','dual')}
    def hook(key):
        def save(module,inputs,output):captures[key].append(output)
        return save
    handles=[model.base.single.decoder.register_forward_hook(hook('decoder')),
        model.base.single.detail_refiner.register_forward_hook(hook('detail')),
        model.aggressive_refiner.register_forward_hook(hook('dual'))]
    rows=[];checks=dict(parseval=True,objective_value=True,objective_output_gradient=True,decoded_reconstruction=True)
    started=time.perf_counter();torch.cuda.reset_peak_memory_stats()
    try:
        for n,batch in enumerate(DataLoader(Subset(ds,indices),batch_size=1,shuffle=False)):
            b=device_batch(batch,torch.device('cuda'))
            for values in captures.values():values.clear()
            with torch.no_grad(),torch.autocast('cuda'):
                output=model.forward_components(b)
                assert len(captures['decoder'])==len(captures['detail'])==2 and len(captures['dual'])==1
                raw=captures['decoder'][-1];detail=captures['detail'][-1]
                main_res=raw[:,0:1].tanh().float().reshape_as(output['prediction'])
                detail_res=detail.tanh().float().reshape_as(output['prediction'])
                dual=captures['dual'][0][0].tanh().float()
                conf=output['confidence'].float();joint=output['joint_confidence'].float()
                reverse=model(reverse_batch(b)).float().flip(1)
            p=output['prediction'].float().detach().clone().requires_grad_()
            base=output['base_prediction'].float();coarse=b['cond'][:,:,4:5];target=b['target'].float()
            reconstructed=coarse+conf*(main_res+.35*detail_res)+.18*joint*dual
            torch.testing.assert_close(reconstructed,p,atol=.002,rtol=.003) # AMP arithmetic order
            loss_terms=terms(p,target,coarse,base,reverse)
            grads={k:torch.autograd.grad(v,p,retain_graph=True)[0] for k,v in loss_terms.items()}
            total=sum(grads.values());msegrad=grads['mse'];error=(p-target).detach();sq=error.square()
            if n==0:
                reference,_=objective(FixedOutputs(p,base,reverse),b,80,80)
                torch.testing.assert_close(sum(loss_terms.values()),reference)
                expected=torch.autograd.grad(reference,p)[0]
                torch.testing.assert_close(total,expected,atol=1e-10,rtol=1e-5)
                write_json(out/'contracts.json',checks)
            eb=bands(error);gb=bands(total)
            torch.testing.assert_close(sum(eb),error,atol=1e-6,rtol=1e-4)
            torch.testing.assert_close(sum(x.square().mean() for x in eb),sq.mean(),atol=1e-8,rtol=1e-5)
            radius=conf*1.35+.18*joint
            floor=(target-coarse).abs().sub(radius).clamp_min(0).square()
            absolute_floor=(target-coarse).abs().sub(1.53).clamp_min(0).square()
            saturated=(main_res.abs()>=.95)|(detail_res.abs()>=.95)|(dual.abs()>=.95)
            for j in range(3):
                row=dict(patient_id=batch['patient_id'][0],case_id=batch['case_id'][0],z=int(batch['z'][0])+j+1,
                    phase=(j+1)/4,mse=float(sq[0,j].mean()),confidence=float(conf[0,j].mean()),
                    joint_confidence=float(joint[0,j].mean()),fixed_conf_oracle_mse=float(floor[0,j].mean()),
                    maximum_conf_oracle_mse=float(absolute_floor[0,j].mean()),
                    saturation_fraction=float(saturated[0,j].float().mean()),
                    saturation_mse=float((sq*saturated)[0,j].mean()))
                for name,x in [('main',main_res),('detail',detail_res),('dual',dual)]:
                    row[name+'_saturation_fraction']=float((x[0,j].abs()>=.95).float().mean())
                for k,label in enumerate(('low','mid','high')):
                    row['error_energy_'+label]=float(eb[k][0,j].square().mean())
                    row['total_gradient_energy_'+label]=float(gb[k][0,j].square().mean())
                    gm=bands(msegrad)[k][0,j]
                    row['total_gradient_cosine_mse_'+label]=float(F.cosine_similarity(gb[k][0,j].flatten(),gm.flatten(),dim=0,eps=1e-20))
                for name,g in dict(grads,total=total).items():
                    v=g[0,j].flatten();m=msegrad[0,j].flatten()
                    row['gradient_rms_'+name]=float(v.square().mean().sqrt())
                    row['gradient_cosine_mse_'+name]=float(F.cosine_similarity(v,m,dim=0,eps=1e-20))
                rows.append(row)
            if (n+1)%25==0:print(f'Decoder audit {n+1}/{len(indices)}',flush=True)
        frame=pd.DataFrame(rows);frame.to_csv(out/'per_slice.csv',index=False)
        metrics=[c for c in frame if c not in ('patient_id','case_id','z','phase')]
        percase=frame.groupby(['patient_id','case_id'])[metrics].mean()
        perpatient=percase.groupby('patient_id').mean();perpatient.to_csv(out/'per_patient.csv')
        average=perpatient.mean();mse=float(average['mse'])
        fixed_ratio=float(average['fixed_conf_oracle_mse']/mse)
        sat_ratio=float(average['saturation_mse']/mse)
        result=dict(intervals=len(indices),patients=len(perpatient),series=len(percase),
            means={k:float(v) for k,v in average.items()},
            error_energy_fraction={k:float(average['error_energy_'+k]/mse) for k in ('low','mid','high')},
            total_gradient_energy_fraction={k:float(average['total_gradient_energy_'+k]/sum(average['total_gradient_energy_'+s] for s in ('low','mid','high'))) for k in ('low','mid','high')},
            fixed_conf_oracle_mse_fraction=fixed_ratio,saturation_error_fraction=sat_ratio,
            saturation_does_not_justify_full=bool(fixed_ratio<.01 and sat_ratio<.10),
            elapsed_seconds=time.perf_counter()-started,peak_allocated_gib=torch.cuda.max_memory_allocated()/2**30,
            contracts=checks,validation_used=False,test_used=False,weights_updated=False,full_authorized=False,smoke=args.smoke)
        write_json(out/'summary.json',result);print(json.dumps(result,indent=2),flush=True)
    finally:
        for handle in handles:handle.remove()


if __name__=='__main__':main()
