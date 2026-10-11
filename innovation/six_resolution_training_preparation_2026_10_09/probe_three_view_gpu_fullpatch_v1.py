"""Full-sized synthetic three-view task graph: packed vs sequential under unchanged GPU cap."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
os.environ['CUDA_VISIBLE_DEVICES']='0'
import sys,time,json,gc,traceback,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09'))
from qualify_full_fov_gpu_cpu import torch,original_cuda_initializer,read,entry,bind,dump,resource_guard,state_hash,array_sha,CheckpointedTaskUNet3D
from mc_rc_3d_baseline_2026_10_07 import loss
from gin_reference_adapter_v1 import draw_parameters,gin,mean_target_kl

def main():
 os.environ['CUDA_VISIBLE_DEVICES']='0';torch.set_num_threads(1);assert torch.get_num_interop_threads()==1
 started=time.perf_counter();out=HERE/'three_view_gpu_fullpatch_attempt01';out.mkdir(exist_ok=False)
 r=dict(complete=False,errors=[],branches=[],comparisons=[],MRI_arrays_loaded=0,GT_arrays_loaded=0,parent_model_arrays_loaded=0,
  synthetic_GPU_optimizer_updates=0,synthetic_GPU_whole_model_forward_calls=0,new_medical_training_updates=0,
  complete19series_GPU_three_view_qualified=False,clinical_lambda_chosen=False,medical_effect_scored=False,
  confirmation_patients_opened=False,lockedIXI_opened=False,original_training_modified=False,
  other_PIDs_enumerated=False,other_PIDs_modified=False,publication_claim_confirmed=False,goal_status='active')
 def save():
  temp=out/'receipt.json.tmp';temp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');temp.replace(out/'receipt.json')
 def guard(cuda=True):
  v=resource_guard();size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
  fov=ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09';fs=sum(p.stat().st_size for p in fov.rglob('*') if p.is_file())
  assert size<7_000_000 and fs<20_000_000 and v['workspace_free_bytes']-22_800_000-(7_000_000-size)-(20_000_000-fs)>=8_000_000_000
  assert time.perf_counter()-started<360 and torch.get_num_threads()==torch.get_num_interop_threads()==1
  if cuda:
   free,total=torch.cuda.mem_get_info();peak=torch.cuda.max_memory_reserved();assert free>=4_000_000_000 and peak<=2_500_000_000
   v.update(GPU_free_bytes=free,GPU_peak_reserved_bytes=peak)
  return v
 save()
 try:
  r['resources_before']=guard(False)
  cpuq=HERE/'three_view_synthetic_attempt02/receipt.json';assert read(cpuq)['all2_synthetic_steps_full_graph_and_parameter_gates_passed']
  r['source_bindings']=[entry(p) for p in [Path(__file__),HERE/'THREE_VIEW_GPU_FULLPATCH_PROTOCOL.md',cpuq,HERE/'gin_reference_adapter_v1.py',
   ROOT/'gpu_graph_cost_smoke_2026_10_09/checkpointed_model.py',ROOT/'experiments/mc_rc_3d_baseline_2026_10_07.py']]
  torch.manual_seed(20261009);base=CheckpointedTaskUNet3D();initial={n:v.detach().clone() for n,v in base.state_dict().items()};del base
  initial_sha=state_hash(initial);r['common_initial_state_sha256']=initial_sha
  shape=(2,1,64,128,128);x=torch.randn(shape,generator=torch.Generator().manual_seed(991))
  tick=time.perf_counter();views=[gin(x,draw_parameters(shape,801+i))[0] for i in range(3)]
  r['GIN_CPU_preparation_seconds']=time.perf_counter()-tick;r['shared_view_sha256']=[array_sha(v.numpy()) for v in views]
  axes=torch.meshgrid(torch.arange(64),torch.arange(128),torch.arange(128),indexing='ij')
  target=(((axes[0]-31.5)/16).square()+((axes[1]-63.5)/24).square()+((axes[2]-63.5)/24).square()<1).float()[None,None].repeat(2,1,1,1,1)
  target_hash=array_sha(target.numpy());del axes,x
  query=subprocess.run(['nvidia-smi','--query-gpu=index,memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True,timeout=20)
  gpu=[list(map(int,v.split(','))) for v in query.stdout.strip().splitlines()];assert len(gpu)==1 and gpu[0][0]==0 and gpu[0][1]>=8192
  r['GPU_aggregate_before']=gpu;os.environ['CUDA_VISIBLE_DEVICES']='0';torch.cuda._lazy_init=original_cuda_initializer;assert torch.cuda.is_available()
  free,total=torch.cuda.mem_get_info();torch.cuda.set_per_process_memory_fraction(min(.1,2_400_000_000/total))
  torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False;torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True
  def branch(mode):
   q=dict(mode=mode,complete=False,errors=[],actual_forward_calls=0,optimizer_update_applied=False);payload=None
   try:
    guard();torch.cuda.reset_peak_memory_stats();model=CheckpointedTaskUNet3D();model.load_state_dict(initial);model.to('cuda:0');model.train()
    opt=torch.optim.AdamW(model.parameters(),lr=1e-4,weight_decay=1e-4,betas=(.9,.999),eps=1e-8,foreach=False,fused=False)
    tick=time.perf_counter();gv=[v.to('cuda:0') for v in views];gt=target.to('cuda:0');torch.cuda.synchronize();q['transfer_seconds']=time.perf_counter()-tick
    opt.zero_grad(set_to_none=True);tick=time.perf_counter()
    if mode=='packed6':
     outputs=model(torch.cat(gv,dim=0));q['actual_forward_calls']+=1
     supervised=tuple(o[:2] for o in outputs);final=outputs[0].reshape(3,2,1,64,128,128)
     comparison=[o.reshape(3,2,*o.shape[1:]) for o in outputs]
    else:
     separate=[]
     for view in gv:separate.append(model(view));q['actual_forward_calls']+=1
     supervised=separate[0];final=torch.stack([v[0] for v in separate],dim=0)
     comparison=[torch.stack([v[depth] for v in separate],dim=0) for depth in range(3)]
    total_loss=loss(supervised,gt)+.1*mean_target_kl(torch.cat((torch.zeros_like(final),final),dim=2));total_loss.backward();torch.cuda.synchronize()
    q.update(loss=float(total_loss.detach()),forward_loss_backward_seconds=time.perf_counter()-tick)
    assert torch.isfinite(total_loss);guard()
    tick=time.perf_counter();gradient={n:None if p.grad is None else p.grad.detach().cpu().clone() for n,p in model.named_parameters()}
    probability=[o.detach().sigmoid().cpu().clone() for o in comparison];q['gradient_probability_capture_seconds']=time.perf_counter()-tick
    assert all(v is None or torch.isfinite(v).all() for v in gradient.values())
    tick=time.perf_counter();opt.step();torch.cuda.synchronize();q.update(AdamW_seconds=time.perf_counter()-tick,optimizer_update_applied=True);guard()
    tick=time.perf_counter();parameter={n:p.detach().cpu().clone() for n,p in model.named_parameters()}
    moments={n:{k:v.detach().cpu().clone() for k,v in opt.state[p].items()} for n,p in model.named_parameters() if p in opt.state}
    q.update(parameter_moment_capture_seconds=time.perf_counter()-tick,complete=True,resources_after=guard())
    payload=dict(gradient=gradient,probability=probability,parameter=parameter,moments=moments)
   except Exception as e:
    q['errors'].append(type(e).__name__+': '+str(e));q['traceback']=traceback.format_exc()
    q['GPU_peak_reserved_bytes_on_failure']=torch.cuda.max_memory_reserved()
   return q,payload
  payloads=[]
  for mode in ('packed6','sequential2'):
   q,payload=branch(mode);r['branches'].append(q);payloads.append(payload)
   r['synthetic_GPU_optimizer_updates']+=int(q['optimizer_update_applied']);r['synthetic_GPU_whole_model_forward_calls']+=q['actual_forward_calls']
   gc.collect();torch.cuda.empty_cache();guard();save();print(json.dumps(q),flush=True)
  if all(v is not None for v in payloads):
   a,b=payloads;assert a['gradient'].keys()==b['gradient'].keys() and a['parameter'].keys()==b['parameter'].keys()
   checks=[]
   for name,av in a['gradient'].items():
    bv=b['gradient'][name];assert (av is None)==(bv is None)
    ge=0. if av is None else float((av-bv).abs().max());pe=float((a['parameter'][name]-b['parameter'][name]).abs().max())
    ast=a['moments'].get(name,{});bst=b['moments'].get(name,{});assert ast.keys()==bst.keys()
    me=max([float((v-bst[k]).abs().max()) for k,v in ast.items()] or [0.]);checks.append(dict(name=name,gradient_error=ge,parameter_error=pe,moment_error=me))
   probability_error=max(float((v-w).abs().max()) for v,w in zip(a['probability'],b['probability']))
   loss_error=abs(r['branches'][0]['loss']-r['branches'][1]['loss']);g=max(v['gradient_error'] for v in checks);p=max(v['parameter_error'] for v in checks);m=max(v['moment_error'] for v in checks)
   r.update(comparisons=checks,max_probability_error=probability_error,max_loss_error=loss_error,max_gradient_error=g,max_parameter_error=p,max_moment_error=m,
    strict_complete_graph_comparison_passed=max(probability_error,loss_error,g,p,m)<=3e-6)
  else:r['strict_complete_graph_comparison_passed']=False
  assert state_hash(initial)==initial_sha and array_sha(target.numpy())==target_hash and [array_sha(v.numpy()) for v in views]==r['shared_view_sha256']
  for b in r['source_bindings']:bind(b)
  r.update(complete=True,all_planned_branches_attempted=True,sequential_fullpatch_graph_completed=r['branches'][1]['complete'],resources_after=guard())
 except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
 r['elapsed_seconds']=time.perf_counter()-started;save()
 print(json.dumps({k:r.get(k) for k in ['complete','errors','sequential_fullpatch_graph_completed','strict_complete_graph_comparison_passed','max_probability_error','max_gradient_error','max_parameter_error','max_moment_error','elapsed_seconds']}),flush=True)
 return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
