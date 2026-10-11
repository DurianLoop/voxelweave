"""Necessary fixed synthetic output/loss/all-gradient equivalence before altered GPU graph."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import sys,time,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,entry,dump,resource_guard
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_3d_baseline_2026_10_07 import TaskUNet3D,loss,torch,np,array_sha
from checkpointed_model import CheckpointedTaskUNet3D
started=time.perf_counter();torch.set_num_threads(1);before=resource_guard();assert not torch.cuda.is_initialized()
out=HERE/'checkpointed_cpu_qualification_attempt01';out.mkdir(exist_ok=False)
torch.manual_seed(20261009);a=TaskUNet3D();b=CheckpointedTaskUNet3D();b.load_state_dict(a.state_dict());a.train();b.train()
rng=np.random.default_rng(20261009);x=torch.from_numpy(rng.standard_normal((2,1,16,24,32),dtype=np.float32))
y=torch.zeros_like(x);y[0,0,4:10,7:16,10:19]=1;y[1,0,2:6,3:8,7:13]=1
aa=a(x);bb=b(x);va=loss(aa,y);vb=loss(bb,y);va.backward();vb.backward()
outputs=[dict(index=i,shape=list(u.shape),exact_equal=torch.equal(u,v),maximum_error=float((u-v).abs().max())) for i,(u,v) in enumerate(zip(aa,bb))]
grads=[dict(name=n,exact_equal=torch.equal(p.grad,q.grad),maximum_error=float((p.grad-q.grad).abs().max())) for (n,p),(m,q) in zip(a.named_parameters(),b.named_parameters()) if n==m]
assert len(grads)==len(list(a.parameters())) and all(r['exact_equal'] for r in outputs+grads) and torch.equal(va,vb)
assert all(torch.isfinite(p.grad).all() for p in b.parameters()) and not torch.cuda.is_initialized()
result=dict(complete=True,errors=[],all_outputs_loss_and_parameter_gradients_bitwise_equal=True,outputs=outputs,gradients=grads,
    loss=float(va.detach()),input_sha256=array_sha(x.numpy()),label_sha256=array_sha(y.numpy()),CPU_threads=torch.get_num_threads(),CUDA_initialized=False,
    MRI_arrays_loaded=0,GT_arrays_loaded=0,model_checkpoints_loaded=0,training_updates=0,source_bindings=[entry(p) for p in [Path(__file__),HERE/'checkpointed_model.py',HERE/'CHECKPOINTED_GRAPH_PROTOCOL.md',ROOT/'experiments/mc_rc_3d_baseline_2026_10_07.py']],
    resources_before=before,resources_after=resource_guard(),elapsed_seconds=time.perf_counter()-started,publication_claim_confirmed=False,goal_status='active')
assert result['elapsed_seconds']<120;dump(out/'receipt.json',result);print(json.dumps({k:result[k] for k in ['complete','all_outputs_loss_and_parameter_gradients_bitwise_equal','elapsed_seconds','CUDA_initialized']}))
