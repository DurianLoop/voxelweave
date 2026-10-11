"""Reproduce failed artificial step0, expose all54 worst update coordinates and Adam formula."""
import os
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='1'
import sys,time,json,gc,traceback
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'adaptive_acquisition_primary_followup_2026_10_09'))
from resource_guard_v1 import guard,entry,bind,read,dump
sys.path.insert(0,str(ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09'))
from qualify_full_fov_gpu_cpu import torch,np,CheckpointedTaskUNet3D,state_hash,array_sha
from mc_rc_3d_baseline_2026_10_07 import loss
from gin_reference_adapter_v1 import draw_parameters,gin,mean_target_kl
from gin_cpu_differentiable_reference_v2 import FunctionalCPUReference,independent_total_loss
def main():
 started=time.perf_counter();torch.set_num_threads(1);assert torch.get_num_interop_threads()==1
 out=HERE/'synthetic_adam_attribution_attempt01';out.mkdir(exist_ok=False)
 r=dict(complete=False,errors=[],CPU_optimizer_updates=0,MRI_arrays_loaded=0,GT_arrays_loaded=0,
  GPU_calls=0,CUDA_initialized=False,coordinates=[],medical_effect_scored=False,full19_qualification_passed=False,
  original_parameter_gate_passed=False,publication_claim_confirmed=False,goal_status='active')
 def save():(out/'receipt.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 def check():
  v=guard(started);assert not torch.cuda.is_initialized();assert torch.get_num_threads()==torch.get_num_interop_threads()==1;return v
 save()
 try:
  r['resources_before']=check();prior=read(HERE/'gin_cpu_reference_verification_attempt02/receipt.json')
  assert not prior['complete'] and prior['CPU_optimizer_updates']==2 and len(prior['steps'])==1
  r['source_bindings']=[entry(p) for p in (Path(__file__),HERE/'GIN_SYNTHETIC_ADAM_ATTRIBUTION_PROTOCOL_V1.md',HERE/'gin_cpu_reference_verification_attempt02/receipt.json',HERE/'verify_gin_cpu_reference_v2.py',HERE/'gin_cpu_differentiable_reference_v2.py',HERE/'gin_reference_adapter_v1.py',ROOT/'adaptive_acquisition_primary_followup_2026_10_09/resource_guard_v1.py')]
  torch.manual_seed(20261009);production=CheckpointedTaskUNet3D();initial={n:v.detach().clone() for n,v in production.state_dict().items()};reference=FunctionalCPUReference(initial)
  assert state_hash(initial)==prior['initial_state_sha256']==state_hash(reference.state_dict());r['initial_state_sha256']=state_hash(initial)
  shape=(2,1,16,16,16);x=torch.randn(shape,generator=torch.Generator().manual_seed(49))
  views=[gin(x,draw_parameters(shape,480000+i))[0] for i in range(3)]
  target=(torch.randn(shape,generator=torch.Generator().manual_seed(501))>.8).float()
  input_hashes=[array_sha(v.numpy()) for v in views];target_hash=array_sha(target.numpy());r['input_hashes']=input_hashes;r['synthetic_target_sha256']=target_hash
  snapshots=[]
  for index,model in enumerate((production,reference)):
   check();opt=torch.optim.AdamW(model.parameters(),lr=1e-4,weight_decay=1e-4,betas=(.9,.999),eps=1e-8,foreach=False,fused=False)
   opt.zero_grad(set_to_none=True);outputs=[model(v) for v in views]
   value=(loss(outputs[0],target)+.1*mean_target_kl(torch.cat((torch.zeros_like(torch.stack([v[0] for v in outputs])),torch.stack([v[0] for v in outputs])),2))) if index==0 else independent_total_loss(outputs,target)
   value.backward();check();grads={n:p.grad.detach().clone() for n,p in model.named_parameters()}
   probs=[torch.stack([v[d].detach().sigmoid() for v in outputs]) for d in range(3)]
   opt.step();r['CPU_optimizer_updates']+=1
   params={n:p.detach().clone() for n,p in model.named_parameters()}
   moments={n:{k:v.detach().clone() for k,v in opt.state[p].items()} for n,p in model.named_parameters()}
   snapshots.append(dict(loss=float(value.detach()),gradients=grads,probabilities=probs,params=params,moments=moments))
   save();del outputs,value,opt;gc.collect();check()
  a,b=snapshots;records=[];pred_max=0.;old={v['name']:v for v in prior['steps'][0]['all54_parameters']}
  for n in initial:
   diff=(a['params'][n]-b['params'][n]).abs();flat=int(diff.argmax());coord=np.unravel_index(flat,tuple(diff.shape))
   ge=float((a['gradients'][n]-b['gradients'][n]).abs().max());pe=float(diff.max())
   fields=[dict(field=k,max_error=float((v-b['moments'][n][k]).abs().max())) for k,v in a['moments'][n].items()]
   assert ge==old[n]['gradient_error'] and pe==old[n]['parameter_error'] and fields==old[n]['optimizer_fields']
   branches=[]
   for label,s in zip(('production_FP32_norm','reference_FP64_norm'),(a,b)):
    p0=initial[n].numpy().astype(np.float64);g=s['gradients'][n].numpy().astype(np.float64)
    predicted=p0*(1-1e-4*1e-4)-1e-4*g/(np.abs(g)+1e-8)
    ee=float(np.max(np.abs(s['params'][n].numpy().astype(np.float64)-predicted)));pred_max=max(pred_max,ee);assert ee<=3e-6
    branches.append(dict(label=label,gradient=float(s['gradients'][n][coord]),initial=float(initial[n][coord]),
     updated=float(s['params'][n][coord]),predicted_updated_double=float(predicted[coord]),
     exp_avg=float(s['moments'][n]['exp_avg'][coord]),exp_avg_sq=float(s['moments'][n]['exp_avg_sq'][coord]),
     step=float(s['moments'][n]['step']),all_parameter_predicted_max_error=ee,
     gradient_sha256=array_sha(s['gradients'][n].numpy()),parameter_sha256=array_sha(s['params'][n].numpy())))
   records.append(dict(name=n,gradient_error=ge,parameter_error=pe,optimizer_fields=fields))
   r['coordinates'].append(dict(name=n,shape=list(diff.shape),coordinate=[int(v) for v in coord],flat=flat,parameter_error=pe,
    coordinate_gradient_difference=abs(branches[0]['gradient']-branches[1]['gradient']),
    gradient_signs=[int(np.sign(v['gradient'])) for v in branches],branches=branches))
  maxima=dict(loss=abs(a['loss']-b['loss']),probability=max(float((v-w).abs().max()) for v,w in zip(a['probabilities'],b['probabilities'])),gradient=max(v['gradient_error'] for v in records),parameter=max(v['parameter_error'] for v in records),optimizer_state=max(f['max_error'] for v in records for f in v['optimizer_fields']))
  assert maxima==prior['steps'][0]['max_errors'] and maxima['parameter']>3e-6
  assert input_hashes==[array_sha(v.numpy()) for v in views] and target_hash==array_sha(target.numpy())
  for source in r['source_bindings']:bind(source)
  r.update(complete=True,all54_parameter_gradient_and162_state_error_rows_reproduced_exactly=True,max_errors=maxima,
   all54_first_step_AdamW_math_checked=True,independent_double_AdamW_max_prediction_error=pred_max,
   worst_coordinate=max(r['coordinates'],key=lambda v:v['parameter_error']),
   CPU_whole_model_forwards=6,CPU_whole_model_backwards=2,step1_executed=False,resources_after=check())
 except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
 r['elapsed_seconds']=time.perf_counter()-started;save()
 print(json.dumps({k:r.get(k) for k in ('complete','errors','CPU_optimizer_updates','max_errors','independent_double_AdamW_max_prediction_error','worst_coordinate','elapsed_seconds')}),flush=True)
 return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
