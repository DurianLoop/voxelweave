"""Packed and sequential three-view graphs with attached consensus and original checkpointed task model."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
os.environ['CUDA_VISIBLE_DEVICES']='-1'
import sys,time,json,traceback,gc
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,entry,bind,dump,resource_guard
sys.path.insert(0,str(ROOT/'experiments'));sys.path.insert(0,str(ROOT/'gpu_graph_cost_smoke_2026_10_09'))
from checkpointed_model import CheckpointedTaskUNet3D
from mc_rc_3d_baseline_2026_10_07 import torch,loss
from gin_reference_adapter_v1 import draw_parameters,gin,mean_target_kl
torch.set_num_threads(1);assert torch.get_num_interop_threads()==1

source_v1_path=HERE/'qualify_three_view_graph_synthetic_v1.py'
def main():
 started=time.perf_counter();out=HERE/'three_view_synthetic_attempt02';out.mkdir(exist_ok=False)
 r=dict(complete=False,errors=[],steps=[],MRI_arrays_loaded=0,GT_arrays_loaded=0,parent_model_arrays_loaded=0,
  synthetic_models_initialized=0,synthetic_optimizer_updates=0,new_medical_training_updates=0,
  CUDA_initialized=False,medical_effect_scored=False,clinical_lambda_chosen=False,
  complete19series_GPU_three_view_qualified=False,confirmation_patients_opened=False,lockedIXI_opened=False,
  original_training_modified=False,other_PIDs_enumerated=False,other_PIDs_modified=False,publication_claim_confirmed=False,goal_status='active')
 def guard():
  v=resource_guard();size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
  fov=ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09';fs=sum(p.stat().st_size for p in fov.rglob('*') if p.is_file())
  assert size<7_000_000 and fs<20_000_000 and v['workspace_free_bytes']-22_800_000-(7_000_000-size)-(20_000_000-fs)>=8_000_000_000
  assert time.perf_counter()-started<180 and not torch.cuda.is_initialized() and torch.get_num_threads()==torch.get_num_interop_threads()==1
  return v
 try:
  r['resources_before']=guard();torch.manual_seed(20261009)
  models=[CheckpointedTaskUNet3D(),CheckpointedTaskUNet3D()];models[1].load_state_dict(models[0].state_dict());r['synthetic_models_initialized']=2
  for model in models:model.train()
  optimizers=[torch.optim.AdamW(m.parameters(),lr=1e-4,weight_decay=1e-4,betas=(.9,.999),eps=1e-8,foreach=False,fused=False) for m in models]
  sources=[Path(__file__),source_v1_path,HERE/'THREE_VIEW_GRAPH_PREPARATION_PROTOCOL.md',HERE/'gin_reference_adapter_v1.py',
   ROOT/'gpu_graph_cost_smoke_2026_10_09/checkpointed_model.py',ROOT/'experiments/mc_rc_3d_baseline_2026_10_07.py',
   HERE/'gin_operator_preparation_attempt01/receipt.json']
  r['source_bindings']=[entry(p) for p in sources];assert read(sources[-1])['complete']
  axes=torch.stack(torch.meshgrid(*(torch.arange(16) for _ in range(3)),indexing='ij'))
  target=((axes-7.5).square().sum(dim=0)<25).float()[None,None].repeat(2,1,1,1,1)
  for step in range(2):
   guard();x=torch.randn((2,1,16,16,16),generator=torch.Generator().manual_seed(100+step))
   views=[gin(x,draw_parameters(tuple(x.shape),300+step*3+i))[0] for i in range(3)];target_before=target.clone();costs=[];outputs=[];losses=[];gradients=[]
   for branch,(model,opt) in enumerate(zip(models,optimizers)):
    tick=time.perf_counter();opt.zero_grad(set_to_none=True)
    if branch==0:
     alloutputs=model(torch.cat(views,dim=0));supervised=tuple(o[:2] for o in alloutputs)
     final=alloutputs[0].reshape(3,2,1,16,16,16)
     comparable=[o.reshape(3,2,*o.shape[1:]).detach().sigmoid() for o in alloutputs]
    else:
     separate=[model(view) for view in views];supervised=separate[0];final=torch.stack([value[0] for value in separate],dim=0)
     comparable=[torch.stack([value[depth] for value in separate],dim=0).detach().sigmoid() for depth in range(3)]
    distribution=torch.cat((torch.zeros_like(final),final),dim=2)
    total=loss(supervised,target)+.1*mean_target_kl(distribution);total.backward()
    assert torch.isfinite(total);grad={n:None if p.grad is None else p.grad.detach().clone() for n,p in model.named_parameters()}
    assert all(v is None or torch.isfinite(v).all() for v in grad.values())
    gradients.append(grad);outputs.append(comparable);losses.append(float(total.detach()));costs.append(time.perf_counter()-tick)
   assert gradients[0].keys()==gradients[1].keys();checks=[]
   for name,a in gradients[0].items():
    b=gradients[1][name];assert (a is None)==(b is None)
    error=0. if a is None else float((a-b).abs().max())
    checks.append(dict(name=name,gradient_max_error=error,none_gradient=a is None))
   prob_error=max(float((a-b).abs().max()) for a,b in zip(outputs[0],outputs[1]));loss_error=abs(losses[0]-losses[1]);grad_error=max(v['gradient_max_error'] for v in checks)
   record=dict(step=step+1,all3_head_probabilities_max_error=prob_error,losses=losses,loss_max_error=loss_error,
    full_parameter_gradient_max_error=grad_error,parameter_gradient_checks=checks,
    forward_loss_backward_seconds=costs,synthetic_patch=[16,16,16],three_view_target_attached=True)
   r['steps'].append(record);assert prob_error<=3e-6 and loss_error<=3e-6 and grad_error<=3e-6
   for opt in optimizers:opt.step();r['synthetic_optimizer_updates']+=1
   pairs=zip(models[0].named_parameters(),models[1].named_parameters());parameters=[]
   for (name,a),(other,b) in pairs:
    assert name==other;parameters.append(dict(name=name,parameter_max_error=float((a.detach()-b.detach()).abs().max())))
   parameter_error=max(v['parameter_max_error'] for v in parameters);record.update(parameter_checks=parameters,post_AdamW_parameter_max_error=parameter_error)
   moment_checks=[]
   for (name,a),(other,b) in zip(models[0].named_parameters(),models[1].named_parameters()):
    assert name==other
    ast=optimizers[0].state.get(a,{});bst=optimizers[1].state.get(b,{})
    assert ast.keys()==bst.keys()
    for key,av in ast.items():
     bv=bst[key];assert av.shape==bv.shape and av.dtype==bv.dtype
     error=float((av-bv).abs().max())
     if key=='step':assert torch.equal(av,bv)
     moment_checks.append(dict(name=name,optimizer_field=key,max_error=error))
   moment_error=max([v['max_error'] for v in moment_checks] or [0.])
   record.update(optimizer_state_checks=moment_checks,full_optimizer_state_max_error=moment_error,
                 optimizer_state_fields_compared=len(moment_checks))
   assert parameter_error<=3e-6 and moment_error<=3e-6 and torch.equal(target,target_before)
   del gradients,outputs;gc.collect();guard()
  for b in r['source_bindings']:bind(b)
  r.update(complete=True,all2_synthetic_steps_full_graph_and_parameter_gates_passed=True,resources_after=guard())
 except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
 r['elapsed_seconds']=time.perf_counter()-started;dump(out/'receipt.json',r)
 print(json.dumps(dict(complete=r['complete'],errors=r['errors'],synthetic_optimizer_updates=r['synthetic_optimizer_updates'],
  steps=[{k:v.get(k) for k in ['step','all3_head_probabilities_max_error','loss_max_error','full_parameter_gradient_max_error','post_AdamW_parameter_max_error','full_optimizer_state_max_error','optimizer_state_fields_compared']} for v in r['steps']],elapsed_seconds=r['elapsed_seconds']),ensure_ascii=False),flush=True)
 return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
