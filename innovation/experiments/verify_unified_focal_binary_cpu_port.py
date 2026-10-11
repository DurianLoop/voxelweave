"""Meaningful numerical value/gradient checks using a separate per-class NumPy oracle."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for name in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[name]='1'
import ast,json,hashlib,sys,traceback
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
import torch
from vs_seg_task_cpu_support import resource_gate
from unified_focal_binary_cpu_port import asymmetric_unified
ROOT=Path(__file__).resolve().parents[1]
torch.set_num_threads(1);torch.set_num_interop_threads(1)
def deny_cuda(*args,**kwargs):raise RuntimeError('GPU initialization prohibited')
torch.cuda._lazy_init=deny_cuda
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def reference(logits,target):
    p=1/(1+np.exp(-logits));classes=[]
    for n in range(len(p)):
        errors=[]
        for foreground in (False,True):
            pred=np.clip(p[n,0] if foreground else 1-p[n,0],1e-7,1-1e-7)
            gt=target[n,0] if foreground else 1-target[n,0]
            a=float(np.sum(gt*pred));b=float(np.sum(gt*(1-pred)));c=float(np.sum((1-gt)*pred))
            ti=(a+1e-7)/(a+.6*b+.4*c+1e-7)
            errors.append((1-ti)**.5 if foreground else 1-ti)
        classes.extend(errors)
    pixels=[]
    for n in range(len(p)):
        for index in np.ndindex(p.shape[2:]):
            prob=float(np.clip(p[(n,0)+index],1e-7,1-1e-7));gt=float(target[(n,0)+index])
            pixels.append(-.4*prob**.5*(1-gt)*np.log(1-prob)-.6*gt*np.log(prob))
    return .5*float(np.mean(classes))+.5*float(np.mean(pixels))
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_gate();out=ROOT/'experiments/unified_focal_binary_cpu_port';out.mkdir(exist_ok=False);path=out/'attempt_01.json'
    author=ROOT/'literature/source_cache/unified_focal_author_code_2026-10-03/loss_functions.py'
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],script_sha256=sha(__file__),
        port_sha256=sha(ROOT/'experiments/unified_focal_binary_cpu_port.py'),author_source_sha256=sha(author),
        protocol_sha256=sha(ROOT/'UNIFIED_FOCAL_BINARY_CPU_PORT_PLAN_2026-10-03.md'),cases=[],gradient_checks=[],
        MRI_pixels_loaded=False,network_forward_calls=0,training_updates=0,scientific_confirmation_patients=0,
        author_package_executed=False,publication_claim_confirmed=False)
    try:
        try:ast.parse(author.read_text(encoding='utf-8'));r['original_author_source_parses']=True
        except SyntaxError as error:r['original_author_source_parses']=False;r['original_source_syntax_error']=dict(line=error.lineno,message=error.msg)
        assert not r['original_author_source_parses']
        rng=np.random.default_rng(20261007);logits=rng.normal(size=(2,1,5,7));target=(rng.random(logits.shape)>.8).astype(float)
        configurations=[('binary',logits,target),('soft',logits,rng.uniform(size=logits.shape)),
                        ('empty',logits,np.zeros_like(target)),('full',logits,np.ones_like(target)),
                        ('extreme',np.where(target>0,35.,-35.),target)]
        for name,x,y in configurations:
            prediction=torch.tensor(x,dtype=torch.float64,requires_grad=True);loss=asymmetric_unified(prediction,torch.tensor(y));loss.backward()
            value=reference(x,y);assert abs(float(loss.detach())-value)<1e-12 and torch.isfinite(prediction.grad).all()
            r['cases'].append(dict(name=name,torch_loss=float(loss.detach()),numpy_loss=value,all_gradients_finite=True))
        x=torch.tensor(logits,dtype=torch.float64,requires_grad=True);loss=asymmetric_unified(x,torch.tensor(target));loss.backward();gradient=x.grad.numpy()
        for flat in rng.choice(logits.size,24,replace=False):
            plus,minus=logits.copy(),logits.copy();plus.flat[flat]+=1e-6;minus.flat[flat]-=1e-6
            finite=(reference(plus,target)-reference(minus,target))/2e-6;actual=float(gradient.flat[flat]);assert abs(actual-finite)<3e-8
            r['gradient_checks'].append(dict(flat_index=int(flat),autograd=actual,numpy_central_difference=finite,absolute_difference=abs(actual-finite)))
        r['gpu_initialized']=torch.cuda.is_initialized();assert not r['gpu_initialized'];r['complete']=True
    except Exception as error:r['errors'].append(type(error).__name__+': '+str(error));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:r.get(k) for k in ('complete','errors','original_author_source_parses','network_forward_calls','gpu_initialized')}));return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
