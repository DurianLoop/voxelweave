"""Fullpatch comparison to a complete attached graph, with mathematically exact two-pass upstream derivatives."""
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
 started=time.perf_counter();out=HERE/'three_view_offload_vjp_attempt01';out.mkdir(exist_ok=False)
 r=dict(complete=False,errors=[],branches=[],parameter_comparisons=[],MRI_arrays_loaded=0,GT_arrays_loaded=0,parent_model_arrays_loaded=0,
  synthetic_GPU_optimizer_updates=0,complete19series_GPU_three_view_qualified=False,medical_effect_scored=False,
  confirmation_patients_opened=False,lockedIXI_opened=False,original_training_modified=False,other_PIDs_enumerated=False,
  other_PIDs_modified=False,publication_claim_confirmed=False,goal_status='active')
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
  r['resources_before']=guard(False);oldp=HERE/'three_view_gpu_fullpatch_attempt01/receipt.json';old=read(oldp)
  assert old['complete'] and not old['sequential_fullpatch_graph_completed'] and all(not q['complete'] for q in old['branches'])
  r['source_bindings']=[entry(p) for p in [Path(__file__),HERE/'THREE_VIEW_OFFLOAD_AND_VJP_PROTOCOL.md',oldp,HERE/'gin_reference_adapter_v1.py',
   ROOT/'gpu_graph_cost_smoke_2026_10_09/checkpointed_model.py',ROOT/'experiments/mc_rc_3d_baseline_2026_10_07.py']]
  torch.manual_seed(20261009);base=CheckpointedTaskUNet3D();initial={n:v.detach().clone() for n,v in base.state_dict().items()};del base
  initial_sha=state_hash(initial);assert initial_sha==old['common_initial_state_sha256'];r['common_initial_state_sha256']=initial_sha
  shape=(2,1,64,128,128);x=torch.randn(shape,generator=torch.Generator().manual_seed(991));views=[gin(x,draw_parameters(shape,801+i))[0] for i in range(3)]
  view_hashes=[array_sha(v.numpy()) for v in views];assert view_hashes==old['shared_view_sha256'];r['shared_view_sha256']=view_hashes
  axes=torch.meshgrid(torch.arange(64),torch.arange(128),torch.arange(128),indexing='ij')
  target=(((axes[0]-31.5)/16).square()+((axes[1]-63.5)/24).square()+((axes[2]-63.5)/24).square()<1).float()[None,None].repeat(2,1,1,1,1)
  target_hash=array_sha(target.numpy());del axes,x
  query=subprocess.run(['nvidia-smi','--query-gpu=index,memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True,timeout=20)
  gpu=[list(map(int,v.split(','))) for v in query.stdout.strip().splitlines()];assert len(gpu)==1 and gpu[0][0]==0 and gpu[0][1]>=8192
  r['GPU_aggregate_before']=gpu;os.environ['CUDA_VISIBLE_DEVICES']='0';torch.cuda._lazy_init=original_cuda_initializer;assert torch.cuda.is_available()
  free,total=torch.cuda.mem_get_info();torch.cuda.set_per_process_memory_fraction(min(.1,2_400_000_000/total))
  torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False;torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True
  def branch(mode):
   q=dict(mode=mode,complete=False,errors=[],actual_whole_model_forward_calls=0,optimizer_update_applied=False);payload=None
   try:
    guard();torch.cuda.reset_peak_memory_stats();model=CheckpointedTaskUNet3D();model.load_state_dict(initial);model.to('cuda:0');model.train()
    opt=torch.optim.AdamW(model.parameters(),lr=1e-4,weight_decay=1e-4,betas=(.9,.999),eps=1e-8,foreach=False,fused=False)
    gv=[v.to('cuda:0') for v in views];gt=target.to('cuda:0');torch.cuda.synchronize();opt.zero_grad(set_to_none=True)
    tick=time.perf_counter()
    if mode=='sequential_save_on_cpu':
     with torch.autograd.graph.save_on_cpu(pin_memory=False):
      separate=[]
      for view in gv:separate.append(model(view));q['actual_whole_model_forward_calls']+=1;guard()
      final=torch.stack([v[0] for v in separate],dim=0)
      total_loss=loss(separate[0],gt)+.1*mean_target_kl(torch.cat((torch.zeros_like(final),final),dim=2))
      total_loss.backward()
     torch.cuda.synchronize();q['graph_forward_loss_backward_seconds']=time.perf_counter()-tick
     comparable=[torch.stack([v[depth].detach().sigmoid().cpu() for v in separate],dim=0) for depth in range(3)]
     true_loss=float(total_loss.detach())
    else:
     cached=[];cached_all=[]
     with torch.no_grad():
      for view in gv:
       value=model(view);q['actual_whole_model_forward_calls']+=1
       cached.append(value[0].cpu().clone());cached_all.append([v.sigmoid().cpu().clone() for v in value]);del value;guard()
     torch.cuda.synchronize();q['first_no_grad_pass_and_capture_seconds']=time.perf_counter()-tick
     assert state_hash(model.state_dict())==initial_sha
     tick=time.perf_counter();leaf=torch.stack(cached,dim=0).to('cuda:0').requires_grad_(True)
     attached_term=.1*mean_target_kl(torch.cat((torch.zeros_like(leaf),leaf),dim=2))
     weighted_kl_value=attached_term.detach().cpu();upstream=torch.autograd.grad(attached_term,leaf)[0].detach().cpu()
     del leaf,attached_term;torch.cuda.synchronize();q['attached_upstream_gradient_and_capture_seconds']=time.perf_counter()-tick;guard()
     tick=time.perf_counter();supervised_value=None;replay_checks=[]
     for index in (2,1,0):
      value=model(gv[index]);q['actual_whole_model_forward_calls']+=1
      replay=torch.equal(value[0].detach().cpu(),cached[index]);assert replay
      replay_checks.append(dict(view=index,final_logits_first_second_pass_bitwise_equal=replay))
      gradient=upstream[index].to('cuda:0')
      if index==0:
       supervised=loss(value,gt);supervised_value=supervised.detach().cpu()
       torch.autograd.backward((supervised,value[0]),grad_tensors=(None,gradient));del supervised
      else:value[0].backward(gradient)
      del value,gradient;guard()
     torch.cuda.synchronize();q.update(replay_checks=replay_checks,second_pass_and_backward_seconds=time.perf_counter()-tick,
      attached_consensus_gradient_includes_mean_dependence=True)
     comparable=[torch.stack([v[depth] for v in cached_all],dim=0) for depth in range(3)]
     true_loss=float(supervised_value+weighted_kl_value)
    assert __import__('math').isfinite(true_loss);guard()
    tick=time.perf_counter();grad={n:None if p.grad is None else p.grad.detach().cpu().clone() for n,p in model.named_parameters()}
    assert all(v is None or torch.isfinite(v).all() for v in grad.values());q['gradient_capture_seconds']=time.perf_counter()-tick
    tick=time.perf_counter();opt.step();torch.cuda.synchronize();q.update(optimizer_update_applied=True,AdamW_seconds=time.perf_counter()-tick);guard()
    tick=time.perf_counter();params={n:p.detach().cpu().clone() for n,p in model.named_parameters()}
    moments={n:{k:v.detach().cpu().clone() for k,v in opt.state[p].items()} for n,p in model.named_parameters() if p in opt.state}
    q.update(complete=True,true_loss=true_loss,parameter_moment_capture_seconds=time.perf_counter()-tick,resources_after=guard())
    payload=dict(gradient=grad,parameters=params,moments=moments,probability=comparable)
   except Exception as e:q['errors'].append(type(e).__name__+': '+str(e));q['traceback']=traceback.format_exc()
   return q,payload
  payloads=[]
  for mode in ('sequential_save_on_cpu','two_pass_attached_vjp'):
   q,payload=branch(mode);r['branches'].append(q);payloads.append(payload);r['synthetic_GPU_optimizer_updates']+=int(q['optimizer_update_applied'])
   gc.collect();torch.cuda.empty_cache();guard();save();print(json.dumps(q),flush=True)
  assert all(q['complete'] and not q['errors'] for q in r['branches']) and all(v is not None for v in payloads)
  a,b=payloads;assert a['gradient'].keys()==b['gradient'].keys()
  for name,av in a['gradient'].items():
   bv=b['gradient'][name];assert (av is None)==(bv is None)
   ge=0. if av is None else float((av-bv).abs().max());pe=float((a['parameters'][name]-b['parameters'][name]).abs().max())
   ast=a['moments'].get(name,{});bst=b['moments'].get(name,{});assert ast.keys()==bst.keys()
   fields=[]
   for key,val in ast.items():
    if key=='step':assert torch.equal(val,bst[key])
    fields.append(dict(field=key,max_error=float((val-bst[key]).abs().max())))
   r['parameter_comparisons'].append(dict(name=name,gradient_error=ge,parameter_error=pe,optimizer_fields=fields))
  prob_error=max(float((v-w).abs().max()) for v,w in zip(a['probability'],b['probability']))
  loss_error=abs(r['branches'][0]['true_loss']-r['branches'][1]['true_loss'])
  grad_error=max(v['gradient_error'] for v in r['parameter_comparisons']);param_error=max(v['parameter_error'] for v in r['parameter_comparisons'])
  moments_error=max(c['max_error'] for v in r['parameter_comparisons'] for c in v['optimizer_fields'])
  r.update(max_probability_error=prob_error,max_loss_error=loss_error,max_gradient_error=grad_error,max_parameter_error=param_error,max_optimizer_state_error=moments_error,
   all_strict_numeric_gates_passed=max(prob_error,loss_error,grad_error,param_error,moments_error)<=3e-6)
  assert r['all_strict_numeric_gates_passed']
  assert state_hash(initial)==initial_sha and array_sha(target.numpy())==target_hash and [array_sha(v.numpy()) for v in views]==view_hashes
  for binding in r['source_bindings']:bind(binding)
  r.update(complete=True,status='completed',resources_after=guard())
 except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc();r['status']='failed'
 r['elapsed_seconds']=time.perf_counter()-started;save()
 print(json.dumps({k:r.get(k) for k in ['complete','status','errors','all_strict_numeric_gates_passed','max_probability_error','max_loss_error','max_gradient_error','max_parameter_error','max_optimizer_state_error','elapsed_seconds']}),flush=True)
 return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
