"""Independent NumPy windows, finite differences, locality and FP32 failure disclosure."""
import json,sys,traceback
from datetime import datetime,timezone
from mc_rc_3d_baseline_v2_2026_10_07 import ROOT,sha,resource_guard,torch,np
from mc_rc_3d_local_kernel_normalization_2026_10_07 import local_kernel_conv3d
OUT=ROOT/'experiments/mc_rc_3d_local_kernel_normalization_2026_10_07'
def explicit(x,w,b,eps=1e-5):
    padded=np.pad(x,((0,0),(0,0),(1,1),(1,1),(1,1)))
    out=np.empty((x.shape[0],w.shape[0],*x.shape[2:]),dtype=np.float64)
    for n in range(x.shape[0]):
        for z in range(x.shape[2]):
            for r in range(x.shape[3]):
                for c in range(x.shape[4]):
                    box=padded[n,:,z:z+3,r:r+3,c:c+3].astype(np.float64)
                    normalized=(box-box.mean())/np.sqrt(box.var()+eps)
                    out[n,:,z,r,c]=np.einsum('izrc,oizrc->o',normalized,w.astype(np.float64))+b
    return out
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);path=OUT/'attempt01.json'
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],script_sha256=sha(__file__),
        source_file='experiments/mc_rc_3d_local_kernel_normalization_2026_10_07.py',
        source_sha256=sha(ROOT/'experiments/mc_rc_3d_local_kernel_normalization_2026_10_07.py'),
        protocol_sha256=sha(ROOT/'MC_RC_3D_LOCAL_NORMALIZATION_PREPARATION_2026-10-07.md'),
        cases=[],actual_mri_task_forwards=0,actual_training_updates=0,actual_gpu_updates=0,
        mri_or_label_values_loaded=0,confirmation_patients_opened=False,publication_claim_confirmed=False,
        known_operator_not_novel=True,full_architecture_or_training_recipe_implemented=False,dropout_probability=0)
    def save():path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    save()
    try:
        resource_guard();rng=np.random.default_rng(20261007)
        w=rng.normal(scale=.1,size=(4,3,3,3,3));b=rng.normal(scale=.1,size=4)
        examples=[('random',rng.normal(size=(2,3,7,8,9))),('constant_two',np.full((1,3,7,8,9),2.)),
                  ('zero',np.zeros((1,3,7,8,9))),('offset_1000',rng.normal(size=(1,3,7,8,9))+1000)]
        for dtype in (np.float64,np.float32):
            for key,data in examples:
                x=np.asarray(data,dtype=dtype);weights=np.asarray(w,dtype=dtype);bias=np.asarray(b,dtype=dtype)
                reference=explicit(x,weights,bias)
                with torch.inference_mode():out=local_kernel_conv3d(torch.from_numpy(x),torch.from_numpy(weights),torch.from_numpy(bias)).numpy()
                error=float(np.max(np.abs(out-reference))); tolerance=3e-6 if dtype==np.float32 else 1e-7
                result=dict(case=key,dtype=np.dtype(dtype).name,max_output_absolute_error=error,
                    strict_tolerance=tolerance,strict_gate_passed=error<=tolerance,all_outputs_finite=bool(np.isfinite(out).all()))
                r['cases'].append(result);save()
        assert all(row['all_outputs_finite'] for row in r['cases'])
        assert all(row['strict_gate_passed'] for row in r['cases'] if row['dtype']=='float64')
        # One output derivative through local moments and convolution, independently differenced.
        x=torch.from_numpy(examples[0][1][:1].copy()).requires_grad_();weights=torch.from_numpy(w.copy()).requires_grad_()
        bias=torch.from_numpy(b.copy());out=local_kernel_conv3d(x,weights,bias);scalar=out[0,1,3,3,3];scalar.backward()
        h=1e-5;xi=(0,2,3,3,3);wi=(1,1,1,1,1);derivatives=[]
        for name,index,values,gradient in [('input',xi,x.detach().numpy(),float(x.grad[xi])),
                                          ('weight',wi,weights.detach().numpy(),float(weights.grad[wi]))]:
            plus=values.copy();minus=values.copy();plus[index]+=h;minus[index]-=h
            if name=='input':numerical=(explicit(plus,w,b)[0,1,3,3,3]-explicit(minus,w,b)[0,1,3,3,3])/(2*h)
            else:numerical=(explicit(x.detach().numpy(),plus,b)[0,1,3,3,3]-explicit(x.detach().numpy(),minus,b)[0,1,3,3,3])/(2*h)
            error=abs(gradient-numerical);assert error<=1e-7
            derivatives.append(dict(variable=name,index=list(index),autograd=gradient,finite_difference=float(numerical),absolute_error=float(error)))
        r['derivative_verification']=derivatives
        # Interior equivalence uses exactly the same local pixels and no input statistics outside the window.
        image=rng.normal(size=(1,3,12,12,12));crop=image[:,:,2:10,2:10,2:10].copy();changed=image.copy();changed[0,2,11,11,11]+=20
        with torch.inference_mode():
            full=local_kernel_conv3d(torch.from_numpy(image),torch.from_numpy(w),bias).numpy()
            small=local_kernel_conv3d(torch.from_numpy(crop),torch.from_numpy(w),bias).numpy()
            perturbed=local_kernel_conv3d(torch.from_numpy(changed),torch.from_numpy(w),bias).numpy()
        crop_error=float(np.max(np.abs(full[:,:,3:9,3:9,3:9]-small[:,:,1:7,1:7,1:7])))
        remote=float(np.max(np.abs(full[:,:,3:9,3:9,3:9]-perturbed[:,:,3:9,3:9,3:9])))
        assert crop_error<=1e-12 and remote==0
        r['locality_verification']=dict(interior_full_vs_crop_max_error=crop_error,far_perturbation_interior_max_error=remote)
        r['fp32_qualification_passed']=all(row['strict_gate_passed'] for row in r['cases'] if row['dtype']=='float32')
        r['fp32_failed_cases']=[row['case'] for row in r['cases'] if row['dtype']=='float32' and not row['strict_gate_passed']]
        r['float64_qualification_passed']=True;r['cuda_initialized']=torch.cuda.is_initialized();assert not r['cuda_initialized']
        r['complete']=True;r['resources_after']=resource_guard()
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();save();assert path.stat().st_size<1_000_000
    print(json.dumps({k:r.get(k) for k in ('complete','errors','cases','fp32_qualification_passed','fp32_failed_cases','locality_verification','cuda_initialized')}),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
